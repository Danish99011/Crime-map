"""Tests for the directory <-> FIR <-> MHA join and the pincode lookups.

The directory records are hand-built in the shared station schema from the
three pages already on disk, so the expected answers are obvious by
inspection. The MHA points are the real coordinates for the handful of
stations these tests touch, keyed the way `load_station_points()` keys them,
rather than the gitignored geojson.

The failure this file guards against is a quiet mis-join: one station's phone
number printed beside another station's crime. So a near miss must be tagged
`fuzzy`, a far miss must be `none`, and neither may ever come back as `exact`.
"""

from pathlib import Path

import pytest

from pipeline.mumbai import normalise
from pipeline.mumbai_join import (
    FUZZY_THRESHOLD,
    join_directory,
    nearest_stations,
    pincode_index,
)

FIXTURES = Path(__file__).parent / "fixtures"


def record(ps_id, name_mr, name_en, lat, lon, pincode, **extra):
    """A station record with only the fields the join reads filled in."""
    base = {"ps_id": ps_id, "name_mr": name_mr, "name_en": name_en,
            "lat": lat, "lon": lon, "pincode": pincode,
            "phones": None, "address": None}
    base.update(extra)
    return base


NAGPADA = record(62, "नागपाडा", "Nagpada", 18.9670135, 72.8292369, "400008",
                 phones=["022-2309-2293", "022-2307-8109"])
BANDRA = record(9, "वांद्रे", "Bandra", 19.05742791697285, 72.83161238576191,
                "400050")
CHUNABHATTI = record(18, "चुनाभट्टी", "Chunabhatti", 19.0564178, 72.8728353,
                     "400022")
KNOWN = [NAGPADA, BANDRA, CHUNABHATTI]

# The FIR portal's spellings, exactly as they appear in data/raw/live/mumbai.
FIR_NAMES = ["NAGPADA", "BANDRA", "CHUNABHATTI POLICE STATION"]


def mha(*names_and_points):
    """MHA points keyed by normalised name, as load_station_points() does."""
    return {normalise(name): {"name": name, "lat": lat, "lon": lon, "ps_cd": None}
            for name, lat, lon in names_and_points}


MHA = mha(("NAGPADA", 18.96718, 72.82826),
          ("BANDRA", 19.0559, 72.8357),
          ("CHUNABHATTI POLICE STATION", 19.05169, 72.8693),
          ("DR. DADASAHEB BHADKAMKAR MARG", 18.95505, 72.81718),
          ("BORIWALI", 19.22934, 72.8559),
          ("KHAR", 19.07254, 72.83777))


def by_fir_name(rows):
    return {row["fir_name"]: row for row in rows}


class TestExactJoin:
    def test_the_three_known_stations_join_by_name(self):
        rows = by_fir_name(join_directory(KNOWN, FIR_NAMES, MHA))
        assert rows["NAGPADA"]["directory_ps_id"] == 62
        assert rows["BANDRA"]["directory_ps_id"] == 9
        assert rows["CHUNABHATTI POLICE STATION"]["directory_ps_id"] == 18
        assert {row["method"] for row in rows.values()} == {"exact"}

    def test_the_mha_side_is_joined_the_way_mumbai_py_joins_it(self):
        rows = by_fir_name(join_directory(KNOWN, FIR_NAMES, MHA))
        assert rows["NAGPADA"]["mha_ps"] == "NAGPADA"
        assert rows["CHUNABHATTI POLICE STATION"]["mha_ps"] == "CHUNABHATTI POLICE STATION"

    def test_directory_and_mha_agree_on_where_each_office_is(self):
        # Two independent ideas of the same office should sit within a few
        # hundred metres. A distance in kilometres would mean a mis-join.
        for row in join_directory(KNOWN, FIR_NAMES, MHA):
            assert row["distance_km_between_directory_and_mha"] < 1.0

    def test_output_carries_every_promised_field(self):
        row = join_directory(KNOWN, ["NAGPADA"], MHA)[0]
        assert set(row) >= {"fir_name", "directory_ps_id", "directory_name_en",
                            "mha_ps", "method",
                            "distance_km_between_directory_and_mha"}
        assert row["directory_name_en"] == "Nagpada"
        assert row["similarity"] is None


class TestAliasJoin:
    # The portal writes "D.B.MARG"; the MHA master writes the road's full
    # name; the directory's map embed could plausibly write either. Both
    # must join, and both must say so.
    DB_MARG_FULL = record(22, "डॉ. डी. बी. मार्ग", "Dr. Dadasaheb Bhadkamkar Marg",
                          18.955, 72.817, "400007")
    DB_MARG_SHORT = record(22, "डॉ. डी. बी. मार्ग", "D.B. Marg",
                           18.955, 72.817, "400007")

    def test_the_portals_abbreviation_reaches_the_full_name(self):
        row = join_directory([self.DB_MARG_FULL], ["D.B.MARG"], MHA)[0]
        assert row["directory_ps_id"] == 22
        assert row["method"] == "alias"
        assert row["mha_ps"] == "DR. DADASAHEB BHADKAMKAR MARG"

    def test_the_directorys_own_abbreviation_is_reached_too(self):
        row = join_directory([self.DB_MARG_SHORT], ["D.B.MARG"], MHA)[0]
        assert row["directory_ps_id"] == 22
        assert row["method"] == "alias"

    def test_an_alias_is_never_reported_as_exact(self):
        for rec in (self.DB_MARG_FULL, self.DB_MARG_SHORT):
            assert join_directory([rec], ["D.B.MARG"], MHA)[0]["method"] != "exact"


class TestFuzzyJoin:
    BORIVALI = record(14, "बोरीवली", "Borivali", 19.229, 72.856, "400092")
    KHERWADI = record(43, "खेरवाडी", "Kherwadi", 19.066, 72.850, "400051")

    def test_a_near_miss_is_offered_but_tagged_fuzzy(self):
        # W/V is the commonest Marathi transliteration split, and the portal
        # and the directory sit either side of it.
        row = join_directory([self.BORIVALI], ["BORIWALI"], MHA)[0]
        assert row["directory_ps_id"] == 14
        assert row["method"] == "fuzzy"
        assert row["similarity"] >= FUZZY_THRESHOLD
        assert row["mha_ps"] == "BORIWALI"

    def test_a_far_miss_is_none_not_a_guess(self):
        # KHAR and KHERWADI are neighbouring stations that share a prefix.
        # Joining them would put Kherwadi's phones next to Khar's crime.
        row = join_directory([self.KHERWADI], ["KHAR"], MHA)[0]
        assert row["method"] == "none"
        assert row["directory_ps_id"] is None
        assert row["mha_ps"] == "KHAR"

    def test_a_tie_between_two_records_is_not_resolved_by_luck(self):
        # Two records the same distance from the name, in different directions.
        twins = [record(1, "अ", "Boriwali N", 19.0, 72.0, None),
                 record(2, "ब", "Boriwali S", 19.0, 72.0, None)]
        row = join_directory(twins, ["BORIWALI"], MHA)[0]
        assert row["method"] == "none"


class TestNothingIsJoinedWithoutEvidence:
    def test_a_station_the_records_do_not_cover_is_none_everywhere(self):
        # Vanrai is in the FIR feed but in neither the three records nor the
        # MHA master, so every identifier must be null, not 0 or "".
        row = join_directory(KNOWN, ["VANRAI POLICE STATION"], MHA)[0]
        assert row["method"] == "none"
        assert row["directory_ps_id"] is None
        assert row["directory_name_en"] is None
        assert row["mha_ps"] is None
        assert row["distance_km_between_directory_and_mha"] is None

    def test_a_record_without_an_english_name_cannot_be_joined(self):
        # The parser leaves name_en null when the embed is absent. That is a
        # gap to report, not a reason to index under the Marathi name.
        nameless = record(62, "नागपाडा", None, 18.967, 72.829, "400008")
        row = join_directory([nameless], ["NAGPADA"], MHA)[0]
        assert row["method"] == "none"

    def test_distance_is_null_when_the_directory_has_no_coordinates(self):
        unplaced = record(62, "नागपाडा", "Nagpada", None, None, "400008")
        row = join_directory([unplaced], ["NAGPADA"], MHA)[0]
        assert row["directory_ps_id"] == 62
        assert row["distance_km_between_directory_and_mha"] is None

    def test_every_fir_name_gets_exactly_one_row(self):
        names = FIR_NAMES + ["VANRAI POLICE STATION", "D.B.MARG"]
        rows = join_directory(KNOWN, names, MHA)
        assert [row["fir_name"] for row in rows] == names


class TestPincodeIndex:
    def test_each_station_sits_under_its_own_address_pincode(self):
        index = pincode_index(KNOWN)
        assert index["by_pincode"] == {"400008": [62], "400050": [9], "400022": [18]}

    def test_two_offices_in_one_pincode_are_both_listed(self):
        twin = record(99, "क", "Twin", 18.967, 72.829, "400008")
        assert pincode_index(KNOWN + [twin])["by_pincode"]["400008"] == [62, 99]

    def test_a_station_without_a_pincode_is_listed_not_dropped(self):
        missing = record(87, "वनराई", "Vanrai", 19.16, 72.86, None)
        index = pincode_index(KNOWN + [missing])
        assert index["without_pincode"] == [87]
        assert 87 not in sum(index["by_pincode"].values(), [])

    def test_uncovered_pincodes_are_unknown_until_a_pincode_source_exists(self):
        # Without a list of Mumbai's pincodes, "none are uncovered" cannot be
        # known. Null with a reason, never an empty list.
        index = pincode_index(KNOWN)
        assert index["uncovered"] is None
        assert index["uncovered_reason"]

    def test_uncovered_is_computed_once_a_pincode_list_is_supplied(self):
        index = pincode_index(KNOWN, known_pincodes=["400008", "400001", "400050"])
        assert index["uncovered"] == ["400001"]
        assert index["uncovered_reason"] is None

    def test_the_result_says_what_the_index_means(self):
        assert "not unpoliced" in pincode_index(KNOWN)["note"]


class TestNearestStations:
    def test_bandra_to_nagpada_is_about_ten_kilometres(self):
        nearest = nearest_stations(BANDRA["lat"], BANDRA["lon"], [NAGPADA], k=1)
        assert 9.5 < nearest[0]["distance_km"] < 10.5

    def test_ranked_nearest_first_and_cut_at_k(self):
        # From Mumbai Central: Nagpada is next door, Bandra is about ten
        # kilometres north and Chunabhatti a little further, to the north-east.
        nearest = nearest_stations(18.969, 72.820, KNOWN, k=2)
        assert [s["ps_id"] for s in nearest] == [62, 9]
        assert nearest[0]["distance_km"] < nearest[1]["distance_km"]

    def test_the_panel_gets_what_a_person_in_trouble_needs(self):
        nearest = nearest_stations(18.969, 72.820, KNOWN, k=1)[0]
        assert nearest["name_en"] == "Nagpada"
        assert nearest["name_mr"] == "नागपाडा"
        assert nearest["phones"] == ["022-2309-2293", "022-2307-8109"]

    def test_a_station_without_coordinates_is_not_ranked(self):
        unplaced = record(87, "वनराई", "Vanrai", None, None, None)
        nearest = nearest_stations(18.969, 72.820, KNOWN + [unplaced], k=10)
        assert [s["ps_id"] for s in nearest] == [62, 9, 18]


class TestFixturesCarryNoOfficerIdentity:
    """The station pages name officers. The fixture copies must not.

    These assert the removal structurally -- by the markers the scrub left
    and the elements it took out -- because a test that spelled out what was
    removed would carry the very thing it exists to keep out.
    """

    @pytest.fixture(params=[62, 9, 18], ids=["nagpada", "bandra", "chunabhatti"])
    def page(self, request):
        return (FIXTURES / f"mumbaipolice-station-ps{request.param}.html"
                ).read_text(encoding="utf-8")

    def test_the_four_name_bearing_elements_are_marked_removed(self, page):
        # Sr. PI name plate, Divisional ACP, DCP Zone, Regional Addl. CP.
        assert page.count("[officer name removed]") >= 4
        assert "[officer mobile removed]" in page
        assert "[officer photo removed]" in page

    def test_no_link_to_an_officer_profile_survives(self, page):
        assert "?name=" not in page
        assert "images/Police_incharge/" not in page

    def test_the_office_data_the_parser_needs_is_still_there(self, page):
        # The fixtures exist so the parser can be written and reviewed offline;
        # scrubbing must not have taken the office fields with the names.
        for marker in ("Telephone Nos", "Email ID", "Division:", "Beat Chowki",
                       "Locate Us", "!2s", "+Police+Station", "!3d"):
            assert marker in page
