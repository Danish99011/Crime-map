"""Tests for disclosure control.

The records here are constructed in code, never written to a data file, and
describe no real incident. They exist to prove the suppression and no-data rules
hold, which is the part of this pipeline most likely to be quietly relaxed later.
"""

from datetime import date

import pytest

from pipeline.aggregate import (
    MIN_DISPLAY_COUNT,
    NO_DATA,
    PUBLISHED,
    SUPPRESSED,
    aggregate,
    thana_status,
)
from pipeline.fir import FirRecord
from pipeline.resolver import ThanaResolver


def record(station="ARARIA", district="ARARIA", month="2025-08", crime_key="theft"):
    return FirRecord(
        source="test", state="BIHAR", district=district, police_station=station,
        fir_number="1", fir_year=2025,
        registered_on=date(int(month[:4]), int(month[5:]), 11),
        act="BNS", sections=("303",), crime_key=crime_key, classified=True,
    )


@pytest.fixture
def resolver():
    return ThanaResolver([
        {"thana_id": "T-1", "name": "ARARIA", "district": "ARARIA"},
        {"thana_id": "T-2", "name": "BATHNAHA", "district": "ARARIA"},
        {"thana_id": "T-3", "name": "FORKLIFT", "district": "PATNA"},
    ])


ALL_THANAS = ["T-1", "T-2", "T-3"]


class TestSuppression:
    def test_counts_below_the_threshold_are_suppressed(self, resolver):
        result = aggregate([record()] * (MIN_DISPLAY_COUNT - 1), resolver, ALL_THANAS)
        cell = result.cells[0]
        assert cell.status == SUPPRESSED
        assert cell.display_count is None, "a suppressed cell must not leak its count"

    def test_counts_at_the_threshold_are_published(self, resolver):
        result = aggregate([record()] * MIN_DISPLAY_COUNT, resolver, ALL_THANAS)
        cell = result.cells[0]
        assert cell.status == PUBLISHED
        assert cell.display_count == MIN_DISPLAY_COUNT

    def test_suppression_is_per_category_not_per_thana(self, resolver):
        # A thana with plenty of thefts must not thereby reveal its two assaults.
        records = [record(crime_key="theft")] * 10 + [record(crime_key="hurt")] * 2
        result = aggregate(records, resolver, ALL_THANAS)
        by_key = {c.crime_key: c for c in result.cells}
        assert by_key["theft"].status == PUBLISHED
        assert by_key["hurt"].status == SUPPRESSED


class TestNoDataIsNotZero:
    def test_a_thana_with_no_records_reports_no_data(self, resolver):
        result = aggregate([record()] * 5, resolver, ALL_THANAS)
        assert thana_status("T-1", result) == PUBLISHED
        # T-2 and T-3 saw nothing. Rendering them as zero would invent safety.
        assert thana_status("T-2", result) == NO_DATA
        assert thana_status("T-3", result) == NO_DATA

    def test_empty_input_leaves_every_thana_as_no_data(self, resolver):
        result = aggregate([], resolver, ALL_THANAS)
        assert result.coverage["thanas_no_data"] == len(ALL_THANAS)
        assert all(thana_status(t, result) == NO_DATA for t in ALL_THANAS)

    def test_a_thana_with_only_suppressed_cells_is_not_published(self, resolver):
        result = aggregate([record()] * (MIN_DISPLAY_COUNT - 1), resolver, ALL_THANAS)
        assert thana_status("T-1", result) == SUPPRESSED


class TestUnmapped:
    def test_unresolvable_stations_are_counted_not_silently_dropped(self, resolver):
        records = [record()] * 3 + [record(station="NOWHERE AT ALL", district="ARARIA")]
        result = aggregate(records, resolver, ALL_THANAS)
        assert result.coverage["records_unmapped"] == 1
        assert sum(result.coverage["unmapped_reasons"].values()) == 1
        assert result.unmapped[0]["police_station"] == "NOWHERE AT ALL"

    def test_records_without_a_date_are_reported(self, resolver):
        undated = FirRecord(
            source="test", state="BIHAR", district="ARARIA", police_station="ARARIA",
            fir_number="1", fir_year=None, registered_on=None, act="BNS",
            sections=("303",), crime_key="theft", classified=True)
        result = aggregate([undated], resolver, ALL_THANAS)
        assert result.coverage["unmapped_reasons"]["no-date"] == 1
        assert result.cells == []


class TestCaveats:
    def test_the_critical_caveats_always_travel_with_the_data(self, resolver):
        result = aggregate([record()] * 5, resolver, ALL_THANAS)
        ids = {c["id"] for c in result.caveats}
        # These three are the ones that stop the map being read as a crime map.
        assert {"reporting-office", "withheld-categories", "principal-offence"} <= ids
        critical = {c["id"] for c in result.caveats if c["severity"] == "critical"}
        assert "reporting-office" in critical

    def test_withheld_categories_are_declared_even_with_no_data(self, resolver):
        result = aggregate([], resolver, ALL_THANAS)
        assert "sexual-offence" in result.coverage["withheld_categories"]
        assert "pocso" in result.coverage["withheld_categories"]
