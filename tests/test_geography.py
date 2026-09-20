"""Tests for the pieces of the spine where a silent error moves crime on a map."""

import pytest

from pipeline.geography import (
    canonical_district,
    classify_station,
    name_similarity,
    normalise_name,
)


class TestNormaliseName:
    # normalise_name folds *noise* only. Genuine spelling variation is the
    # fuzzy matcher's job and naming convention is the alias table's job; see
    # test_resolver.py::TestLayering. Making this function absorb all three
    # would collide real neighbours, which the next test guards against.
    @pytest.mark.parametrize("left,right", [
        ("MEHANDIA", "MEHANDIYA"),        # Y/I are the same sound here
        ("LAKHI SARAI", "LAKHISARAI"),    # spacing
        ("Araria", "ARARIA  "),           # case and padding
        ("BAKHRI PS", "Bakhri"),          # station suffix
        ("MOHANPUR O.P", "Mohanpur"),     # outpost suffix
        ("BAZAAR SAMITI", "BAZAR SAMITI"),  # doubled vowel
    ])
    def test_noise_folds_away(self, left, right):
        assert normalise_name(left) == normalise_name(right)

    def test_distinct_places_stay_distinct(self):
        # Folding must not be so aggressive that real neighbours collide.
        assert normalise_name("BARAUNI") != normalise_name("BARAHIYA")
        assert normalise_name("PATNA") != normalise_name("PURNIA")

    def test_empty_input_is_empty_not_an_error(self):
        assert normalise_name(None) == ""
        assert normalise_name("   ") == ""


class TestNameSimilarity:
    def test_identical_after_folding_scores_one(self):
        assert name_similarity("MEHANDIA", "MEHANDIYA") == 1.0

    def test_empty_never_matches(self):
        # An empty name must not silently match the first thana in a district.
        assert name_similarity("", "ARARIA") == 0.0
        assert name_similarity(None, None) == 0.0


class TestClassifyStation:
    @pytest.mark.parametrize("name,expected", [
        ("MAHILA", "mahila"),
        ("Patna Mahila PS", "mahila"),
        ("SC/ST", "sc_st"),
        ("SC / ST PS", "sc_st"),
        ("Araria Prohibition", "prohibition"),
        ("Bodhgaya Traffic", "traffic"),
        ("ARARIA", "territorial"),
        ("BATHNAHA", "territorial"),
    ])
    def test_specialist_units_are_not_territorial(self, name, expected):
        assert classify_station(name, "PATNA") == expected

    def test_railway_districts_override_the_name(self):
        # Railway police have no contiguous territory whatever the station is
        # called, so the district decides.
        assert classify_station("JAMALPUR", "RLY JAMALPUR") == "railway"
        assert classify_station("PATNA", "RLY PATNA") == "railway"


class TestCanonicalDistrict:
    @pytest.mark.parametrize("given,expected", [
        ("MOTHIHARI", "EAST CHAMPARAN"),   # HQ town vs official district name
        ("BETIAH", "WEST CHAMPARAN"),
        ("MUJAFFARPUR", "MUZAFFARPUR"),
        ("PURNEA", "PURNIA"),
        ("  patna  ", "PATNA"),
    ])
    def test_aliases_and_casing(self, given, expected):
        assert canonical_district(given) == expected

    def test_unknown_district_passes_through_uppercased(self):
        # Never invent a district; an unrecognised one stays itself so the
        # resolver can refuse it rather than guessing.
        assert canonical_district("Nowhere") == "NOWHERE"
