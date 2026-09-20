"""Tests for FIR parsing, with emphasis on the two silent-corruption risks:
personal data leaking through, and dates landing in the wrong month.
"""

from datetime import date

import pytest

from pipeline.fir import FirRecord, audit_columns, parse_date
from pipeline.taxonomy import classify, parse_sections

MAPPING = {
    "district": "District",
    "police_station": "PoliceStation",
    "fir_number": "FIRNo",
    "registered_on": "RegDate",
    "act": "Act",
    "sections": "Sections",
}


class TestParseDate:
    @pytest.mark.parametrize("text,expected", [
        ("11/08/2025", date(2025, 8, 11)),
        ("11-08-2025", date(2025, 8, 11)),
        ("2025-08-11", date(2025, 8, 11)),
        ("11/08/2025 17:52:50", date(2025, 8, 11)),
    ])
    def test_formats(self, text, expected):
        assert parse_date(text) == expected

    def test_day_first_is_assumed(self):
        # 03/04/2025 is 3 April in Indian convention. Reading it month-first
        # would move a third of the year's records into the wrong month.
        assert parse_date("03/04/2025") == date(2025, 4, 3)

    def test_unparseable_returns_none_rather_than_guessing(self):
        assert parse_date("not a date") is None
        assert parse_date("") is None
        assert parse_date(None) is None


class TestPersonalData:
    def test_identifier_columns_are_dropped_not_carried(self):
        row = {
            "District": "PATNA", "PoliceStation": "KOTWALI", "FIRNo": "123",
            "RegDate": "11/08/2025", "Act": "BNS", "Sections": "303",
            "ComplainantName": "A Person", "AccusedName": "B Person",
            "Address": "somewhere", "MobileNo": "9999999999",
        }
        record = FirRecord.from_row(row, MAPPING, source="test")
        assert record.crime_key == "theft"
        # The record has nowhere to put these, and says what it discarded.
        assert set(record.dropped_columns) == {
            "AccusedName", "Address", "ComplainantName", "MobileNo"}
        assert "Person" not in repr(record)
        assert not any("9999999999" in str(v) for v in vars(record).values())

    def test_audit_flags_personal_columns_for_the_operator(self):
        flagged = audit_columns(
            ["District", "FIRNo", "ComplainantName", "father_name", "Age", "Sections"])
        assert flagged == ["Age", "ComplainantName", "father_name"]

    def test_audit_is_quiet_on_a_clean_feed(self):
        assert audit_columns(["District", "PoliceStation", "FIRNo", "Sections"]) == []


class TestClassification:
    @pytest.mark.parametrize("text,act,expected", [
        ("302 IPC", "IPC", "homicide"),
        ("u/s 302 IPC", "IPC", "homicide"),
        ("304A IPC", "IPC", "negligent-death"),
        ("498A IPC", "IPC", "domestic-cruelty"),
        ("379/411 IPC", "IPC", "theft"),
        ("395/397 IPC", "IPC", "dacoity"),
        ("323, 504, 506", "IPC", "hurt"),
    ])
    def test_sections_map_to_heads(self, text, act, expected):
        assert classify(parse_sections(text), act)[0] == expected

    def test_the_act_disambiguates_a_reused_number(self):
        # IPC 303 is murder by a life-convict; BNS 303 is theft. Getting this
        # wrong would turn thefts into homicides on the map.
        assert classify(["303"], "IPC")[0] == "homicide"
        assert classify(["303"], "BNS")[0] == "theft"

    def test_act_name_is_not_read_as_a_section(self):
        assert parse_sections("302 IPC") == ["302"]
        assert parse_sections("103(2) BNS") == ["103"]

    def test_year_in_an_act_title_is_not_a_section(self):
        assert parse_sections("Arms Act, 1959 s.25") == ["25"]

    def test_unknown_sections_fall_through_honestly(self):
        key, confident = classify(["25"], None)
        assert (key, confident) == ("other", False)

    def test_principal_offence_rule_picks_the_most_serious(self):
        # Mirrors NCRB: one offence per FIR, the most serious. Recorded so the
        # depletion of subordinate heads is a known property, not a surprise.
        assert classify(parse_sections("302/323/379"), "IPC")[0] == "homicide"


class TestDevanagariSectionNumbers:
    """Marathi FIRs write the section number itself in Devanagari digits.

    This was found the hard way: the first live Mumbai month fetched from
    citizen.mahapolice.gov.in came back 97% unclassified. The cause was an
    assumption recorded in taxonomy.py that Devanagari digits "appear in
    Marathi act years and are never section numbers" -- true of the 2025 BNS
    fixtures the rule was written against, false of everything before the BNS
    changeover, where the portal writes:

        भारतीय दंड संहिता १८६० - ३८० ;      (IPC 1860 s.380, theft)

    An unclassified FIR is not a harmless gap. It lands in "other", so a map
    built from pre-2024 records would show almost no burglary anywhere in
    Mumbai -- an absence presented as a fact about the city rather than about
    our parser.
    """

    def test_devanagari_section_number_is_read(self):
        assert parse_sections("भारतीय दंड संहिता १८६० - ३८० ;") == ["380"]

    def test_and_classifies_the_same_as_latin_digits(self):
        devanagari = classify(parse_sections("भारतीय दंड संहिता १८६० - ३८० ;"), "IPC")
        latin = classify(parse_sections("भारतीय दंड संहिता १८६० - 380 ;"), "IPC")
        assert devanagari == latin
        assert devanagari[1] is True

    def test_the_act_year_is_still_not_read_as_a_section(self):
        # १८६० is 1860, the year the IPC was enacted, and must not become a
        # section. This is what the original strip-the-digits rule got right.
        assert "1860" not in parse_sections("भारतीय दंड संहिता १८६० - ३८० ;")

    def test_mixed_devanagari_and_latin_in_one_cell(self):
        text = "शस्त्र अधिनियम, १९५९ - २५,३ ; भारतीय दंड संहिता १८६० - 380 ;"
        sections = parse_sections(text)
        assert "25" in sections and "3" in sections and "380" in sections
        assert "1959" not in sections and "1860" not in sections

    @pytest.mark.parametrize("text,expected", [
        ("भारतीय दंड संहिता १८६० - ३०२ ;", "302"),   # murder
        ("भारतीय दंड संहिता १८६० - ३७९ ;", "379"),   # theft
        ("भारतीय दंड संहिता १८६० - ४२० ;", "420"),   # cheating
    ])
    def test_common_ipc_sections_in_devanagari(self, text, expected):
        assert expected in parse_sections(text)
