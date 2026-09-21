"""Tests for the special-law gate in the taxonomy and the three heads it feeds.

Written against section strings copied verbatim from the Mumbai FIRs on disk
(`data/raw/live/mumbai/*.jsonl`), joiners and typos included, because that is
what the portal writes: the NDPS Act's Marathi title carries two zero-width
joiners and misspells 'पदार्थ', and a pattern written against a tidier spelling
would not match a single one of the 4,000 FIRs cited under it.

Two failures this file exists to prevent:

* A bare number read under the wrong act. Motor Vehicles Act 184 is dangerous
  driving; BNS 184 is not. Maharashtra Prohibition Act 85 is being drunk in
  public; BNS 85 is cruelty by a husband -- and until the gate existed, every
  public-drunkenness FIR in Mumbai (about a thousand on disk) was counted as
  domestic cruelty.
* A road-traffic or public-order head outranking an offence against a person
  or property. NCRB's principal-offence rule counts a theft that also cites
  rash driving as a theft, and so must we, or the property heads deplete.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

from pipeline.fir import FirRecord
from pipeline.mahapolice import MAPPING, parse_grid
from pipeline.taxonomy import (
    BY_KEY,
    CRIME_HEADS,
    classify,
    classify_field,
    detect_act,
    detect_sll_act,
    parse_sections,
)

FIXTURES = Path(__file__).parent / "fixtures"

# The CCTNS JSON fixtures carry the portal's columns in camelCase.
JSON_MAPPING = {
    "district": "district",
    "police_station": "policeStation",
    "fir_number": "firNumber",
    "fir_year": "year",
    "registered_on": "registrationDate",
    "sections": "sections",
}

# Act titles exactly as the portal writes them, joiners included. A string
# built as f"{NDPS} - 27,8(c) ;" is byte-for-byte the on-disk cell.
BNS = "भारतीय न्याय संहिता (बी एन एस), 2023"
IPC = "भारतीय दंड संहिता १८६०"
MVA = "मोटरवाहन अधिनियम, १९८८"
NDPS = ("गुंगीकारक औषधीदव्‍य आणि मनोव्‍यापारावर परिणाम करणारे "
        "प्रदार्थ अधिनियम, १९८५")
MPA = "महाराष्ट्र पोलीस अधिनियम, १९५१"
PROH = "महाराष्ट्र दारूबंदी अधिनियम,१९४९"
ARMS = "शस्‍त्र अधिनियम, १९५९"


def key_of(text: str) -> str:
    return classify_field(text)[0]


class TestRashDriving:
    @pytest.mark.parametrize("sections", [
        "285",                    # danger or obstruction in a public way
        "125,281",                # endangering life + rash driving
        "287",                    # negligent conduct with machinery
        "281",
        "125(a),125(b),281",
    ])
    def test_bns_sections(self, sections):
        assert classify_field(f"{BNS} - {sections} ;") == ("rash-driving", True, ["BNS"])

    @pytest.mark.parametrize("text", [
        f"{IPC} - २७९,३३८ ;",
        f"{IPC} - २७९,३३६ ;",
        f"{IPC} - २७९,३३७,३३८ ; {MVA} - 134(A),134(B) ;",
    ])
    def test_ipc_predecessors_in_devanagari_digits(self, text):
        assert key_of(text) == "rash-driving"

    @pytest.mark.parametrize("text", [
        f"{MVA} - 185 ;",                       # drunk driving, no BNS cited
        f"{MVA} - 184,185 ;",
        f"{MVA} - 181,185,३(१) ;",
        f"{MVA} - 184 ; {BNS} - 125,281 ;",
    ])
    def test_motor_vehicles_act_gate(self, text):
        assert classify_field(text)[:2] == ("rash-driving", True)

    def test_a_bare_184_under_a_penal_code_is_not_rash_driving(self):
        # IPC 184 and 185 are obstructing a public sale. Only the Motor
        # Vehicles Act's 184 and 185 are dangerous and drunk driving.
        assert classify(["184"], "BNS") == ("other", False)
        assert classify(["184"], "IPC") == ("other", False)
        assert classify(["185"], "BNS") == ("other", False)
        assert classify_field(f"{BNS} - 184 ;")[:2] == ("other", False)

    def test_a_motor_vehicles_number_is_not_read_under_the_bns(self):
        # The reverse collision: the Motor Vehicles Act has no offence at
        # 281, and the number must not leak into BNS 281 (rash driving).
        assert classify(["281"], MVA) == ("other", False)
        assert classify(["125"], MVA) == ("other", False)

    def test_the_rules_and_the_tax_act_do_not_pass_the_gate(self):
        # Both sit next to the Act on the portal's dropdown and both are
        # picked by mistake. A rule number is not an Act section.
        assert detect_sll_act("महाराष्ट्र मोटार वाहन नियम, 1989") is None
        assert detect_sll_act("महाराष्ट्र मोटर वाहन (कर) अधिनियम , १९५८") is None
        assert classify(["184"], "महाराष्ट्र मोटार वाहन नियम, 1989") == ("other", False)
        # But the Act's own title with the portal's other spelling does.
        assert detect_sll_act("मोटार वाहन अधिनियम, १९५४") == "MVA"
        assert detect_sll_act("Motor Vehicles Act, 1988") == "MVA"

    @pytest.mark.parametrize("sections", ["177", "134(A),134(B)", "194D", "181", "119"])
    def test_other_motor_vehicles_offences_stay_out(self, sections):
        # A general-penalty citation or a helmet fine is not rash driving.
        assert classify(parse_sections(sections), MVA) == ("other", False)


class TestNarcotics:
    @pytest.mark.parametrize("sections", ["27,8(c)", "20(b),8(c)", "22,8(c)", "29,२२(क),8(c)"])
    def test_ndps_act_gate(self, sections):
        assert classify_field(f"{NDPS} - {sections} ;") == ("narcotics", True, ["SLL"])

    def test_the_title_matches_with_its_joiners_and_without(self):
        assert detect_sll_act(NDPS) == "NDPS"
        assert detect_sll_act(NDPS.replace("‍", "")) == "NDPS"
        assert detect_sll_act("NDPS Act, 1985") == "NDPS"
        assert detect_sll_act("Narcotic Drugs and Psychotropic Substances Act, 1985") == "NDPS"

    def test_the_illicit_traffic_act_is_not_the_ndps_act(self):
        # PITNDPS 1988 is preventive detention, not a drug offence. Its
        # Marathi title is what 'अंमली पदार्थ' would have matched.
        pitndps = ("अंमली औषधीद्रव्‍य व मनःप्रभावी पदार्थ विधिनिसीध्‍द "
                   "व्‍यापार प्रतिबंध अधिनियम, १९८८")
        assert detect_sll_act(pitndps) is None
        assert classify_field(f"{pitndps} - 8 ;")[:2] == ("other", False)
        assert detect_sll_act("Prevention of Illicit Traffic in Narcotic Drugs "
                              "and Psychotropic Substances Act, 1988") is None

    def test_with_a_police_act_section_outside_the_head(self):
        assert key_of(f"{NDPS} - 27,8(c) ; {MPA} - 142 ;") == "narcotics"

    def test_ndps_numbers_are_not_read_under_a_penal_code(self):
        assert classify(["20"], NDPS) == ("narcotics", True)
        assert classify(["20"], "BNS") == ("other", False)
        assert classify(["27"], "IPC") == ("other", False)


class TestPublicOrder:
    @pytest.mark.parametrize("text", [
        f"{BNS} - 223 ;",
        f"{BNS} - 223,3(5) ;",
        f"{IPC} - १८८ ;",
    ])
    def test_disobeying_an_order_under_either_code(self, text):
        assert classify_field(text)[:2] == ("public-order", True)

    @pytest.mark.parametrize("text", [
        f"{MPA} - 135,37(1)(a) ;",
        f"{ARMS} - 25,4 ; {MPA} - 135,37(1)(a) ;",
    ])
    def test_police_act_gate(self, text):
        assert classify_field(text)[:2] == ("public-order", True)

    def test_prohibition_act_gate(self):
        assert classify_field(f"{PROH} - 65(e) ;") == ("public-order", True, ["SLL"])
        # The statute's older title, still on the dropdown.
        assert detect_sll_act("मुंबई दारूबंदी अधिनियम ,१९९८") == "PROH"
        assert detect_sll_act("Maharashtra Prohibition Act, 1949") == "PROH"

    @pytest.mark.parametrize("sections", ["142", "122", "१२२(ख)", "122E", "131", "110,117"])
    def test_police_act_sections_outside_the_head_stay_out(self, sections):
        # 122 is being found in suspicious circumstances at night: a stop,
        # not an offence against public order. 142 is breach of an
        # externment order. Neither is claimed by the head.
        assert classify_field(f"{MPA} - {sections} ;")[:2] == ("other", False)

    def test_look_alike_acts_are_not_the_police_or_prohibition_act(self):
        disaffection = "पोलीस (अप्रीतीची भावना चेतावणे) अधिनियम, १९२२"
        assert detect_sll_act(disaffection) is None
        assert classify_field(f"{disaffection} - 3 ;")[:2] == ("other", False)
        # Dowry Prohibition is 'हुंडाबंदी'; liquor prohibition is 'दारूबंदी'.
        assert detect_sll_act("हुंडाबंदी अधिनियम, १९६१") is None
        assert classify(["65"], "हुंडाबंदी अधिनियम, १९६१") == ("other", False)
        assert detect_sll_act("Dowry Prohibition Act, 1961") is None


class TestNumberCollisionsAcrossActs:
    """The bug the gate fixes: a special-law number read as a BNS section."""

    @pytest.mark.parametrize("sections", ["85", "85 (1)", "85(1)(a)"])
    def test_public_drunkenness_is_not_domestic_cruelty(self, sections):
        key, confident, acts = classify_field(f"{PROH} - {sections} ;")
        assert key != "domestic-cruelty"
        assert (key, confident, acts) == ("other", False, ["SLL"])

    def test_police_act_131_is_not_hurt(self):
        assert key_of(f"{MPA} - 131 ; {BNS} - 223 ;") == "public-order"

    def test_police_act_110_is_not_attempt_to_murder(self):
        assert classify_field(f"{MPA} - 110,117 ; {PROH} - 85 (1) ;")[:2] == ("other", False)

    def test_motor_vehicles_117_119_is_not_grievous_hurt(self):
        assert key_of(f"{MVA} - 117,119 ; {BNS} - 125,223,285 ;") == "rash-driving"

    def test_an_unrecognised_act_matches_nothing(self):
        # A named act we do not know is read under no numbering at all.
        # Only a section with no act named is tried against both codes.
        assert classify(["303"], ARMS) == ("other", False)
        assert classify(["303"], "SLL") == ("other", False)
        assert classify(["303"], "BNS") == ("theft", True)
        # With no act named at all, the section is tried under the IPC and
        # then the BNS, as before: 379 is theft in the IPC.
        assert classify(["379"], None) == ("theft", True)
        assert classify(["303"], None)[1] is True

    def test_joiners_inside_an_act_title_do_not_hide_it(self):
        assert detect_sll_act("महाराष्‍ट्र पोलीस अधिनियम, १९५१") == "MPA"
        assert detect_act("भारतीय न्‍याय संहिता") == "BNS"

    def test_the_captured_live_page(self):
        # Twelve real FIRs from 1 August 2026. Before the gate, the three
        # Prohibition s.85(1) rows on this page were domestic cruelty.
        page = (FIXTURES / "mahapolice-publishedfirs-brihanmumbai-2026-08-01.html").read_text(
            encoding="utf-8")
        records = [FirRecord.from_row(r, MAPPING, source="mahapolice", state="MAHARASHTRA")
                   for r in parse_grid(page)]
        counts = Counter(r.crime_key for r in records)
        assert counts == {"kidnapping": 1, "rash-driving": 8, "other": 3}
        assert all("दारूबंदी" in r.act or "SLL" in r.acts for r in records
                   if r.crime_key == "other")


class TestPrincipalOffenceOrdering:
    def test_theft_with_rash_driving_counts_as_theft(self):
        # Endangering life (125) alongside theft (303(2)).
        assert key_of(f"{BNS} - 125,303(2) ;") == "theft"
        # A real cell that also cites intimidation (351(2)): whichever of the
        # two person/property heads wins, the traffic head does not.
        assert key_of(f"{BNS} - 125,303(2),351(2),352 ;") in ("theft", "criminal-intimidation")
        # And with the Motor Vehicles Act cited too, in the portal's shape.
        assert key_of(f"{MVA} - 184 ; {BNS} - 125,281,303(2) ;") == "theft"

    def test_rash_driving_yields_to_homicide(self):
        assert key_of(f"{IPC} - २७९,304 ;") == "homicide"

    def test_rash_driving_outranks_public_order(self):
        # Disobeying an order is usually the add-on on a traffic FIR.
        assert key_of(f"{MVA} - 119 ; {BNS} - 223,281 ;") == "rash-driving"
        assert key_of(f"{IPC} - १८८,२८३ ;") == "rash-driving"

    def test_narcotics_outranks_public_order(self):
        assert key_of(f"{NDPS} - 27,8(c) ; {MPA} - 135 ;") == "narcotics"

    def test_new_heads_rank_below_every_person_and_property_head(self):
        person_or_property = max(
            h.severity for h in CRIME_HEADS
            if h.group in ("violence", "women", "children", "property"))
        for key in ("rash-driving", "narcotics", "public-order"):
            assert BY_KEY[key].severity > person_or_property, key
        assert CRIME_HEADS[-1].key == "other"

    def test_the_withheld_heads_are_untouched(self):
        assert BY_KEY["sexual-offence"].withheld
        assert BY_KEY["sexual-offence"].ipc == ("376", "376D", "354")
        assert BY_KEY["sexual-offence"].bns == ("64", "70", "74")
        assert BY_KEY["pocso"].withheld
        assert BY_KEY["pocso"].ipc == () and BY_KEY["pocso"].bns == ()


class TestExistingHeadsUnchanged:
    @pytest.mark.parametrize("text,expected", [
        (f"{BNS} - 303(2) ;", "theft"),
        (f"{BNS} - 318(4) ;", "cheating"),
        (f"{BNS} - 305(a),331(3),331(4) ;", "burglary"),
        (f"{IPC} - ३७९ ;", "theft"),
        (f"{IPC} - ३४,४१९,४२० ;", "cheating"),
        (f"{IPC} - ३८० ;", "burglary"),
    ])
    def test_the_map_heads_on_their_commonest_cells(self, text, expected):
        assert classify_field(text)[:2] == (expected, True)

    @pytest.mark.parametrize("fixture,expected", [
        ("cctns-published-firs-maharashtra-20rows.json",
         {"theft": 8, "cheating": 0, "burglary": 1}),
        ("cctns-published-firs-maharashtra-60rows.json",
         {"theft": 9, "cheating": 4, "burglary": 2}),
        ("cctns-published-firs-maharashtra-500rows-paging-duplicates.json",
         {"theft": 250, "cheating": 0, "burglary": 50}),
    ])
    def test_map_head_counts_on_the_fixtures_are_what_they_were(self, fixture, expected):
        # Pinned from the taxonomy before the special-law gate existed.
        rows = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
        counts = Counter(
            FirRecord.from_row(r, JSON_MAPPING, source="t", state="MAHARASHTRA").crime_key
            for r in rows)
        assert {k: counts[k] for k in expected} == expected

    def test_records_still_label_a_special_law_as_sll(self):
        # The map filters special laws out by this label; folding four acts
        # into heads must not change what the record says it cites.
        row = {"district": "BRIHAN MUMBAI CITY", "police_station": "AGRIPADA",
               "year": "2026", "fir_number": "1", "registration_date": "01/08/2026 21:15:00",
               "sections": f"{MVA} - 185 ; {BNS} - 125,281 ;"}
        record = FirRecord.from_row(row, MAPPING, source="mahapolice", state="MAHARASHTRA")
        assert record.crime_key == "rash-driving"
        assert record.acts == ("BNS", "SLL")

    @pytest.mark.parametrize("act,sections,expected", [
        ("BNS", "281", "rash-driving"),
        ("Motor Vehicles Act, 1988", "184", "rash-driving"),
        ("NDPS Act", "20", "narcotics"),
        ("Arms Act", "25", "other"),
        ("IPC", "184", "other"),
    ])
    def test_a_feed_that_names_the_act_in_its_own_column(self, act, sections, expected):
        # Bihar's shape: act and sections in separate columns.
        row = {"District": "PATNA", "PoliceStation": "KOTWALI", "FIRNo": "1",
               "RegDate": "11/08/2025", "Act": act, "Sections": sections}
        mapping = {"district": "District", "police_station": "PoliceStation",
                   "fir_number": "FIRNo", "registered_on": "RegDate",
                   "act": "Act", "sections": "Sections"}
        assert FirRecord.from_row(row, mapping, source="test").crime_key == expected
