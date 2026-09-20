"""Tests for the Maharashtra published-FIR grid parser.

Written against `tests/fixtures/mahapolice-publishedfirs-brihanmumbai-2026-08-01.html`,
a trimmed but otherwise untouched capture of the live portal. The point of
testing against a saved page is that the parser stays reviewable by someone who
cannot reach a `.gov.in` host — which, until this session, was everyone here.

The failure this file exists to prevent is the dangerous one named in
docs/MANUAL-FETCH.md: a parser that returns an empty list when the portal
changes shape, because **an empty table looks exactly like an absence of
crime**. So the parser is required to raise on an unrecognised schema rather
than return nothing.
"""

from pathlib import Path

import pytest

from pipeline.fir import FirRecord, audit_columns
from pipeline.mahapolice import (
    MAPPING,
    SchemaChanged,
    parse_grid,
    total_records,
)

FIXTURE = (Path(__file__).parent / "fixtures"
           / "mahapolice-publishedfirs-brihanmumbai-2026-08-01.html")


@pytest.fixture(scope="module")
def page() -> str:
    return FIXTURE.read_text(encoding="utf-8")


class TestParseGrid:
    def test_reads_every_data_row(self, page):
        rows = parse_grid(page)
        assert len(rows) == 12

    def test_first_row_matches_the_portal_exactly(self, page):
        row = parse_grid(page)[0]
        assert row["state"] == "MAHARASHTRA"
        assert row["district"] == "BRIHAN MUMBAI CITY"
        assert row["police_station"] == "AGRIPADA"
        assert row["year"] == "2026"
        assert row["fir_number"] == "381"
        assert row["registration_date"] == "01/08/2026 21:15:00"
        assert row["fir_no_with_year"] == "0381/2026"
        assert "137(2)" in row["sections"]

    def test_sections_keep_their_devanagari_act_names(self, page):
        # The act name is the only thing that disambiguates a reused section
        # number, so losing it to an encoding slip would silently mis-classify.
        rows = parse_grid(page)
        assert any("भारतीय न्याय संहिता" in r["sections"] for r in rows)

    def test_no_row_carries_a_personal_column(self, page):
        # Maharashtra's published grid has no complainant or accused column.
        # This asserts that property of the source, so that a portal which
        # starts publishing one fails the suite instead of leaking quietly.
        for row in parse_grid(page):
            assert audit_columns(row) == []

    def test_an_unrecognised_schema_raises_rather_than_returning_nothing(self):
        # The whole point. Returning [] here would be read downstream as
        # "no crime was registered", which is the worst failure this can have.
        with pytest.raises(SchemaChanged):
            parse_grid("<table id='ContentPlaceHolder1_gdvDeadBody'>"
                       "<tr><th>Something</th><th>Else</th></tr>"
                       "<tr><td>a</td><td>b</td></tr></table>")

    def test_a_page_with_no_grid_at_all_raises(self):
        with pytest.raises(SchemaChanged):
            parse_grid("<html><body>Error Has Occurred</body></html>")


class TestTotalRecords:
    def test_reads_the_portals_own_count(self, page):
        # The portal states how many records matched. Comparing it against the
        # number actually parsed is how paging bugs get caught: the fixture is
        # 12 rows out of a stated 310.
        assert total_records(page) == 310

    def test_absent_count_is_none_not_zero(self):
        # None means "not stated"; 0 would mean "no crime". Never conflate.
        assert total_records("<html></html>") is None


class TestIntoFirRecord:
    def test_a_parsed_row_becomes_a_record_with_no_identifiers(self, page):
        row = parse_grid(page)[0]
        record = FirRecord.from_row(row, MAPPING, source="mahapolice",
                                    state="MAHARASHTRA")
        assert record.district == "BRIHAN MUMBAI CITY"
        assert record.police_station == "AGRIPADA"
        assert record.fir_number == "381"
        assert record.fir_year == 2026
        assert record.registered_on is not None
        assert record.registered_on.year == 2026
        assert record.registered_on.month == 8
        assert record.registered_on.day == 1
        assert audit_columns(record.dropped_columns) == []

    def test_registration_date_is_read_day_first(self, page):
        # 01/08/2026 is 1 August. Month-first would file it in January.
        record = FirRecord.from_row(parse_grid(page)[0], MAPPING,
                                    source="mahapolice", state="MAHARASHTRA")
        assert record.registered_on.month == 8

    def test_every_fixture_row_classifies_or_is_reported(self, page):
        records = [FirRecord.from_row(r, MAPPING, source="mahapolice",
                                      state="MAHARASHTRA")
                   for r in parse_grid(page)]
        assert len(records) == 12
        # Not asserting 100% classification — unclassified is a reported
        # outcome, not a failure. Asserting it is *measured*.
        assert all(isinstance(r.classified, bool) for r in records)


PAGER_FIXTURE = (Path(__file__).parent / "fixtures"
                 / "mahapolice-publishedfirs-brihanmumbai-2026-08-with-pager.html")
EMPTY_FIXTURE = (Path(__file__).parent / "fixtures"
                 / "mahapolice-publishedfirs-no-records.html")


@pytest.fixture(scope="module")
def pager_page() -> str:
    return PAGER_FIXTURE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def empty_page() -> str:
    return EMPTY_FIXTURE.read_text(encoding="utf-8")


class TestPagerRowIsNotAnFir:
    """The GridView pager lives inside the results table as a <tr>.

    It holds a nested table of page links, so a parser that counts cells reads
    it as one more FIR -- with district "3" and police station "4". This was a
    live bug: a 50-row page parsed as 51 records, inflating every month's
    count by one per page and inventing stations that do not exist.
    """

    def test_the_pager_row_is_excluded(self, pager_page):
        rows = parse_grid(pager_page)
        assert len(rows) == 3

    def test_no_row_has_a_digit_for_a_district(self, pager_page):
        # What the bug looked like from downstream.
        for row in parse_grid(pager_page):
            assert not row["district"].isdigit()
            assert row["district"] == "BRIHAN MUMBAI CITY"

    def test_every_row_is_a_real_station(self, pager_page):
        for row in parse_grid(pager_page):
            assert row["police_station"].strip()
            assert not row["police_station"].isdigit()


class TestNoRecordsIsNotAFailure:
    """A portal that says "No Records Found" has answered the question.

    That is a verified zero and may be recorded. A page we do not recognise is
    a failed fetch and must raise. docs/INGESTION.md rule 5 is about not
    rendering an absence as zero; this is the other half of the same rule --
    not rendering a stated zero as an absence, and never the reverse.
    """

    def test_an_explicit_no_records_page_parses_as_empty(self, empty_page):
        assert parse_grid(empty_page) == []

    def test_and_reports_zero_rather_than_unknown(self, empty_page):
        assert total_records(empty_page) == 0

    def test_the_portal_states_its_own_limits(self, empty_page):
        # 2017 floor and 90-day window, quoted from the live response. The
        # harvester must respect both or it silently collects nothing.
        from pipeline.mahapolice import portal_message
        message = portal_message(empty_page)
        assert message is not None
        assert "1/01/2017" in message
        assert "90 days" in message
