"""Tests for the Mumbai Police station-directory parser.

Written against three saved pages in `tests/fixtures/`, copied from the
crawler's output with every officer's name replaced by a marker. The values
asserted here were read off the raw HTML by eye before the parser existed, so
a passing suite means the parser agrees with a human, not with itself.

Two failures this file exists to prevent:

* **A person's name reaching an output.** Each station page names four
  officers. The parser must not read those cells at all, and the test that
  matters most below checks the *original* page's names -- collected at test
  time, never written down here -- against the parsed record's JSON.
* **A missing value rendered as a value.** A 500 page, or a page whose map
  embed is absent, must come back as nulls with reasons. Never an empty
  string, never a zero, never a guessed coordinate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline.mumbaipolice import (
    FIELDS,
    extract_pincode,
    normalise_phone,
    parse_station,
)

FIXTURES = Path(__file__).parent / "fixtures"
RAW = Path(__file__).resolve().parent.parent / "data" / "raw" / "mumbaipolice" / "stations"

# ps_id -> (fixture file, roster name). The roster name is what
# getpolicestations.json gives for that id; the parser takes it as an argument
# rather than reading it off the page.
STATIONS = {
    62: ("mumbaipolice-station-ps62.html", "नागपाडा"),
    9: ("mumbaipolice-station-ps9.html", "वांद्रे"),
    18: ("mumbaipolice-station-ps18.html", "चुनाभट्टी"),
}

# The record shape every module downstream agrees on. Asserted as a whole so
# that a field added to the parser (a hospital list, an officer, a tourist
# spot) fails here rather than quietly widening what gets persisted.
SCHEMA_KEYS = (
    "ps_id", "name_mr", "name_en", "lat", "lon", "phones", "email",
    "division_mr", "zone_mr", "region_mr",
    "acp_office_phone", "dcp_office_phone", "addl_cp_office_phone",
    "area_sqkm", "population_note", "beat_marshals", "beat_chowkies",
    "nearest_railway", "bus_depot", "address", "pincode",
    "source_url", "fetched_from_file",
)
# Provenance and bookkeeping the parser adds beside the schema fields.
EXTRA_KEYS = ("embed_place", "coords_source", "page_recognised", "missing", "notes")


def load(ps_id: int) -> dict:
    filename, name_mr = STATIONS[ps_id]
    page = (FIXTURES / filename).read_text(encoding="utf-8")
    return parse_station(page, ps_id, name_mr)


def dump(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False)


def missing_fields(record: dict) -> set[str]:
    return {m["field"] for m in record["missing"]}


@pytest.fixture(scope="module")
def nagpada() -> dict:
    return load(62)


@pytest.fixture(scope="module")
def bandra() -> dict:
    return load(9)


@pytest.fixture(scope="module")
def chunabhatti() -> dict:
    return load(18)


class TestNagpada:
    """ps=62. The fullest of the three pages: every schema field is present."""

    def test_identity_and_provenance(self, nagpada):
        assert nagpada["ps_id"] == 62
        assert nagpada["name_mr"] == "नागपाडा"
        assert nagpada["source_url"] == "https://mumbaipolice.gov.in/policestation?ps=62"
        assert nagpada["fetched_from_file"] == "data/raw/mumbaipolice/stations/ps_62.html"

    def test_english_name_comes_from_the_map_embed(self, nagpada):
        # "!2sNagpada+Police+Station" with the suffix stripped.
        assert nagpada["name_en"] == "Nagpada"
        assert nagpada["embed_place"] == "Nagpada Police Station"

    def test_coordinates_read_from_the_embed(self, nagpada):
        # !3d is latitude, !2d is longitude. Getting these the wrong way round
        # puts the station in the Arabian Sea, so both are pinned exactly.
        assert nagpada["lat"] == 18.9670135
        assert nagpada["lon"] == 72.8292369
        assert nagpada["coords_source"] == "maps_embed"

    def test_office_phones_are_transliterated_and_normalised(self, nagpada):
        # The page writes २२२३०९२२९३ and २२२३०७८१०९: ten Devanagari digits
        # with the 22 area code but no leading zero.
        assert nagpada["phones"] == ["022-2309-2293", "022-2307-8109"]

    def test_email_is_deobfuscated(self, nagpada):
        assert nagpada["email"] == "ps.nagpada.mum@mahapolice.gov.in"

    def test_structure_labels_but_not_the_people_beside_them(self, nagpada):
        assert nagpada["division_mr"] == "ताडदेव विभाग"
        assert nagpada["zone_mr"] == "पो उप आ मध्य परिमंडळ-१"
        assert nagpada["region_mr"] == "मध्य प्रादेशिक विभाग"

    def test_senior_office_phones(self, nagpada):
        assert nagpada["acp_office_phone"] == "022-2353-2142"
        assert nagpada["dcp_office_phone"] == "022-2370-0608"
        assert nagpada["addl_cp_office_phone"] == "022-2375-0909"

    def test_area_population_and_marshals(self, nagpada):
        assert nagpada["area_sqkm"] == 2.0
        assert nagpada["population_note"] == "5 Lakhs"
        assert nagpada["beat_marshals"] == 4

    def test_four_beat_chowkies_with_no_locality_lists(self, nagpada):
        chowkies = nagpada["beat_chowkies"]
        # Names stay in the site's script, Devanagari digits included: only
        # the fields that carry a figure are transliterated.
        assert [c["name"] for c in chowkies] == [
            "सुख्लाजी स्ट्रीट पोलीस चौकी",
            "क्लेअर रोड पोलीस चौकी",
            "५ लेन कामाठीपुरा पोलीस चौकी",
            "मुंबई सेन्ट्रल पोलीस चौकी",
        ]
        assert all(c["localities"] == [] for c in chowkies)
        assert all(c["phones"] == [] for c in chowkies)

    def test_transport(self, nagpada):
        assert nagpada["nearest_railway"] == "मुंबई सेंट्रल रेल्वे स्टेशन, डॉ नायर रोड नागपाडा मुंबई"
        assert nagpada["bus_depot"] == (
            "मुंबई सेंट्रल बस विभाग, ताडदेव बस डेपो, मुंबई सेंट्रल एसटी बस विभाग")

    def test_address_and_pincode(self, nagpada):
        # The site writes the pincode as ४०० ००८: Devanagari, with a space.
        assert nagpada["address"] == "सोफिया झुबेर रोड, नागपाडा, मुंबई 400 008"
        assert nagpada["pincode"] == "400008"

    def test_nothing_is_missing_on_the_full_page(self, nagpada):
        assert nagpada["page_recognised"] is True
        assert nagpada["missing"] == []


class TestBandra:
    """ps=9. English address, a two-number DCP office, an empty second phone."""

    def test_name_and_coordinates(self, bandra):
        assert bandra["name_en"] == "Bandra"
        assert bandra["lat"] == 19.05742791697285
        assert bandra["lon"] == 72.83161238576191

    def test_an_empty_anchor_is_not_a_phone(self, bandra):
        # The cell holds one number and an empty <a href="" title=""> </a>.
        assert bandra["phones"] == ["022-2642-3122"]

    def test_email(self, bandra):
        assert bandra["email"] == "ps.bandra.mum@mahapolice.gov.in"

    def test_english_address_with_a_spaced_pincode_and_full_stop(self, bandra):
        assert bandra["address"] == "Hill Road, Bandra (West), Mumbai 400 050."
        assert bandra["pincode"] == "400050"

    def test_two_dcp_office_numbers_are_both_kept(self, bandra):
        assert bandra["acp_office_phone"] == "022-2640-0917"
        assert bandra["dcp_office_phone"] == "022-2642-2042, 022-2645-3700"
        assert bandra["addl_cp_office_phone"] == "022-2640-2122"

    def test_devanagari_population_figure(self, bandra):
        assert bandra["population_note"] == "10 Lakhs"
        assert bandra["area_sqkm"] == 5.0
        assert bandra["beat_marshals"] == 4

    def test_labels(self, bandra):
        assert bandra["division_mr"] == "वांद्रे विभाग"
        assert bandra["zone_mr"] == "पो उप आ पश्चिम परिमंडळ-२"
        assert bandra["region_mr"] == "पश्चिम प्रादेशिक विभाग"

    def test_four_chowkies(self, bandra):
        assert len(bandra["beat_chowkies"]) == 4
        assert bandra["beat_chowkies"][3]["name"] == "चिंबई पोलीस चौकी"

    def test_transport(self, bandra):
        assert bandra["nearest_railway"] == "वांद्रे रेल्वे स्टेशन, वांद्रे (प) मुंबई"
        assert bandra["bus_depot"] == "वांद्रे रिक्लेमेशन बस डेपो, वांद्रे बस डेपो"

    def test_hospitals_and_tourist_places_are_not_carried(self, bandra):
        # The page lists two hospitals and two tourist places. They are not in
        # the schema and must not leak in under any key.
        text = dump(bandra)
        assert "भाभा हॉस्पिटल" not in text
        assert "लिलावती" not in text
        assert "बांद्रा किल्ला" not in text


class TestChunabhatti:
    """ps=18. Chowkies carry locality lists; the DCP and bus-depot cells are empty."""

    def test_name_and_coordinates(self, chunabhatti):
        assert chunabhatti["name_en"] == "Chunabhatti"
        assert chunabhatti["lat"] == 19.0564178
        assert chunabhatti["lon"] == 72.8728353

    def test_eleven_digit_and_eight_digit_numbers_normalise_alike(self, chunabhatti):
        # ०२२२४०५००८४ carries the 022 prefix; २४०५००८६ does not.
        assert chunabhatti["phones"] == ["022-2405-0084", "022-2405-0086"]

    def test_email(self, chunabhatti):
        assert chunabhatti["email"] == "ps.chunabhatti.mum@mahapolice.gov.in"

    def test_an_empty_dcp_cell_is_null_with_a_reason(self, chunabhatti):
        assert chunabhatti["dcp_office_phone"] is None
        assert "dcp_office_phone" in missing_fields(chunabhatti)
        assert chunabhatti["acp_office_phone"] == "022-2522-4409"
        assert chunabhatti["addl_cp_office_phone"] == "022-2523-0893"

    def test_absent_bus_depot_section_is_null_with_a_reason(self, chunabhatti):
        assert chunabhatti["bus_depot"] is None
        assert "bus_depot" in missing_fields(chunabhatti)
        assert chunabhatti["nearest_railway"] == "चुनाभट्टी रेल्वे स्टेशन"

    def test_three_chowkies_split_into_name_and_localities(self, chunabhatti):
        chowkies = chunabhatti["beat_chowkies"]
        assert len(chowkies) == 3
        assert chowkies[0]["name"] == "कुरेशीनगर कसाईवाडा बीट चौकी"
        assert chowkies[0]["localities"][0] == "बडी मस्जिद"
        assert chowkies[0]["localities"][-1] == "गॅलेक्सी अपार्टमेंट"
        assert len(chowkies[0]["localities"]) == 9
        # "अंबिका बीट चौकी -नागोबा चौक": no space after the dash on the page.
        assert chowkies[1]["name"] == "अंबिका बीट चौकी"
        assert chowkies[1]["localities"][0] == "नागोबा चौक"
        assert len(chowkies[1]["localities"]) == 19
        assert chowkies[2]["name"] == "सिंधी सोसायटी बीट चौकी"
        assert len(chowkies[2]["localities"]) == 12

    def test_decimal_area_and_labels(self, chunabhatti):
        assert chunabhatti["area_sqkm"] == 4.5
        assert chunabhatti["population_note"] == "3 Lakhs"
        assert chunabhatti["beat_marshals"] == 3
        assert chunabhatti["division_mr"] == "नेहरू नगर विभाग"
        assert chunabhatti["zone_mr"] == "पो उप आ पूर्व परिमंडळ-२"
        assert chunabhatti["region_mr"] == "पूर्व प्रादेशिक विभाग"

    def test_address_digits_are_transliterated_and_pincode_read(self, chunabhatti):
        assert chunabhatti["address"] == (
            "डी / 01 इमारत, देवरत्न नगर, स्वदेशी मिल रोड, शीव, चुनाभट्टी, मुंबई 400 022.")
        assert chunabhatti["pincode"] == "400022"

    def test_only_the_two_empty_cells_are_missing(self, chunabhatti):
        assert missing_fields(chunabhatti) == {"dcp_office_phone", "bus_depot"}


# ps_id -> roster name for the three pages whose own "Telephone Nos" cell
# repeats the number printed beside the Sr. PI's name. Raw pages only; the
# audit of 2026-09-21 found that number in the built directory for exactly
# these, so the raw-page check below runs on them whenever the crawl is on
# disk.
PLATE_NUMBER_REPEATED = {15: "भायखळा", 26: "देवनार", 36: "जोगेश्वरी"}

# Tokens that are titles rather than names. Dropped before the word-level
# check so an honorific alone cannot produce a false hit.
HONORIFICS = {"डॉ", "डॉ.", "श्री", "श्री.", "श्रीमती", "dr", "dr."}


def officer_words(page: str) -> set[str]:
    """Words of every officer named on a raw page.

    Read from the name plate under "From the desk of Sr. PI" and from the
    `?name=` links on the three senior-officer cells. Computed at test time
    from a file that is not committed, so no name is written into this suite.
    """
    names = re.findall(r'class="ips-name-plate"[^>]*>(.*?)</span>', page, re.S)
    names += re.findall(r'\?name=([^"]+)"', page)
    words = set()
    for name in names:
        for word in re.split(r"\s+", name.strip()):
            word = word.strip(",.").strip()
            if len(word) >= 3 and word.lower() not in HONORIFICS:
                words.add(word)
    return words


def officer_mobile(page: str) -> str | None:
    """The number printed beside the Sr. PI's name, in Devanagari, if any."""
    found = re.search(r'class="post-locate".*?Police Station,\s*([०-९\d]{8,})', page, re.S)
    return found.group(1) if found else None


class TestNoPersonalData:
    """The load-bearing tests. docs/INGESTION.md rule 3, applied to a directory."""

    @pytest.mark.parametrize("ps_id", sorted(STATIONS))
    def test_the_fixture_markers_never_reach_the_record(self, ps_id):
        # Fixtures carry "[officer name removed]" where a name was. If the
        # parser read any of those cells the marker would be in the record.
        text = dump(load(ps_id))
        assert "[officer name removed]" not in text
        assert "[officer mobile removed]" not in text
        assert "?name=" not in text
        assert "Sr. PI" not in text

    @pytest.mark.parametrize("ps_id", sorted(STATIONS))
    def test_no_word_of_any_officers_name_appears_in_the_record(self, ps_id):
        raw = RAW / f"ps_{ps_id}.html"
        if not raw.exists():
            pytest.skip("raw page not on this machine; data/raw is not committed")
        page = raw.read_text(encoding="utf-8")
        words = officer_words(page)
        assert len(words) >= 4, "expected at least four officers on a raw page"
        record = parse_station(page, ps_id, STATIONS[ps_id][1])
        text = dump(record)
        leaked = sorted(w for w in words if w in text)
        assert leaked == [], f"{len(leaked)} officer-name word(s) leaked into the record"

    @pytest.mark.parametrize("ps_id", sorted(STATIONS) + sorted(PLATE_NUMBER_REPEATED))
    def test_the_number_beside_the_sr_pis_name_is_not_kept(self, ps_id):
        raw = RAW / f"ps_{ps_id}.html"
        if not raw.exists():
            pytest.skip("raw page not on this machine; data/raw is not committed")
        page = raw.read_text(encoding="utf-8")
        mobile = officer_mobile(page)
        assert mobile, "expected a number on the Sr. PI name plate"
        from pipeline.taxonomy import devanagari_digits_to_ascii
        name_mr = {**{k: v[1] for k, v in STATIONS.items()}, **PLATE_NUMBER_REPEATED}[ps_id]
        text = dump(parse_station(page, ps_id, name_mr))
        assert mobile not in text
        assert devanagari_digits_to_ascii(mobile) not in text

    @pytest.mark.parametrize("ps_id", sorted(STATIONS))
    def test_record_carries_exactly_the_agreed_fields(self, ps_id):
        record = load(ps_id)
        assert tuple(record) == SCHEMA_KEYS + EXTRA_KEYS
        assert tuple(FIELDS) == SCHEMA_KEYS + EXTRA_KEYS


SERVER_ERROR = ("<!DOCTYPE html><html><head><title>Server Error</title></head>"
                "<body><h1>Server Error</h1><p>Something went wrong.</p></body></html>")


class TestUnrecognisedPages:
    """A page we do not understand yields nulls with reasons, never values."""

    def test_a_server_error_page_is_all_nulls_with_reasons(self):
        record = parse_station(SERVER_ERROR, 62, "नागपाडा")
        assert record["page_recognised"] is False
        assert record["ps_id"] == 62
        assert record["name_mr"] == "नागपाडा"
        for field in SCHEMA_KEYS:
            if field in ("ps_id", "name_mr", "source_url", "fetched_from_file"):
                continue
            assert record[field] is None, f"{field} should be null on an error page"
        assert "page" in missing_fields(record)
        for entry in record["missing"]:
            assert entry["reason"].strip(), f"missing[{entry['field']}] needs a reason"

    def test_nothing_on_an_error_page_is_an_empty_string_or_zero(self):
        record = parse_station(SERVER_ERROR, 62, "नागपाडा")
        for field in ("phones", "beat_chowkies", "email", "pincode", "lat", "lon",
                      "area_sqkm", "beat_marshals"):
            assert record[field] not in ("", 0, 0.0, [])

    def test_a_page_with_no_map_embed_has_null_coordinates(self, nagpada):
        page = (FIXTURES / STATIONS[62][0]).read_text(encoding="utf-8")
        stripped = re.sub(r"<iframe[^>]*>.*?</iframe>", "", page, flags=re.S)
        record = parse_station(stripped, 62, "नागपाडा")
        assert record["lat"] is None and record["lon"] is None
        assert record["name_en"] is None
        assert record["coords_source"] is None
        assert {"lat", "lon", "name_en"} <= missing_fields(record)
        # Everything else still reads. The embed is one field, not the page.
        assert record["phones"] == nagpada["phones"]
        assert record["pincode"] == nagpada["pincode"]

    def test_the_roster_name_is_not_invented_when_absent(self):
        page = (FIXTURES / STATIONS[62][0]).read_text(encoding="utf-8")
        record = parse_station(page, 62, None)
        assert record["name_mr"] is None
        assert "name_mr" in missing_fields(record)


def page_with(iframe_src: str | None = None, address: str = "x",
              plate: str | None = None, **cells: str) -> str:
    """A minimal station page: the given cells, an address, optionally a map.

    `plate` adds the "From the desk of Sr. PI" name plate with that number
    on its post line, the way the site prints it after the station's name.
    """
    parts = ['<p title=" static.Tel_no"><span>Telephone Nos :</span> '
             '<span class="txt-val"><a href="२३५३२१४२">२३५३२१४२</a></span></p>']
    if plate is not None:
        parts.append('<span class="ips-name-plate" title="#">[officer name removed],</span> '
                     '<span class="post-locate" title=" static.Sr.PI, x Police Station"> '
                     f'Sr. PI, x Police Station,{plate}</span>')
    for key, value in cells.items():
        parts.append(f'<p title=" static.{key}"><span>{key} :</span> '
                     f'<span class="txt-val" title="{value}">{value}</span></p>')
    parts.append('<h4 title=" static.Locate_us">Locate Us</h4>')
    if iframe_src is not None:
        parts.append(f'<iframe src="{iframe_src}" frameborder="0"></iframe>')
    parts.append(f'<div class="map-info" id="lightgallery"><img src="x"><p> {address}</p></div>')
    return "<html><body>" + "\n".join(parts) + "</body></html>"


class TestMapShapes:
    """The site uses three iframe shapes. Each is read, and labelled as such."""

    def test_maps_place_url_gives_coordinates_from_3d_and_4d(self):
        # ps=11 and the two cyber stations use a /maps/place/ URL rather than
        # an embed. There !3d is latitude and !4d longitude, unlike the embed.
        src = ("https://www.google.com/maps/place/Bangur+Nagar+Police+Station/"
               "@19.1765173,72.8298122,17z/data=!4m10!1m2!2m1!1sX!3m6!1s0x0:0x0"
               "!8m2!3d19.1765172!4d72.8345761!16s%2Fg%2F11scpd8nm3?entry=ttu")
        record = parse_station(page_with(src), 11, "बांगुर नगर लिंक रोड")
        assert record["lat"] == 19.1765172
        assert record["lon"] == 72.8345761
        assert record["coords_source"] == "maps_place_url"
        assert record["name_en"] == "Bangur Nagar"

    def test_bare_lat_lon_iframe_is_read_and_labelled(self):
        # ps=43 has <iframe src="19.0659476,72.8476667">, nothing else.
        record = parse_station(page_with("19.0659476,72.8476667"), 43, "खेरवाडी")
        assert record["lat"] == 19.0659476
        assert record["lon"] == 72.8476667
        assert record["coords_source"] == "iframe_bare_latlon"
        assert record["name_en"] is None
        assert "name_en" in missing_fields(record)

    def test_a_label_that_is_not_a_police_station_gives_no_english_name(self):
        # ps=26's embed is labelled "Urban hotel". The coordinates are kept,
        # the label is kept for review, and no station name is derived.
        src = ("https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1!2d72.9168787"
               "!3d19.0589512!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2sUrban+hotel!5e0")
        record = parse_station(page_with(src), 26, "देवनार")
        assert record["lat"] == 19.0589512
        assert record["name_en"] is None
        assert record["embed_place"] == "Urban hotel"
        assert "name_en" in missing_fields(record)

    def test_label_prefix_and_parenthesis_variants(self):
        # "Police+Station+-+Aarey+Road" (ps=2) and "Police+Station+(Bhoiwada)" (ps=13).
        base = ("https://www.google.com/maps/embed?pb=!2d72.86!3d19.16!2s{}!5e0")
        aarey = parse_station(page_with(base.format("Police+Station+-+Aarey+Road")), 2, "आरे")
        assert aarey["name_en"] == "Aarey Road"
        bhoiwada = parse_station(page_with(base.format("Police+Station+(Bhoiwada)")), 13, "भोईवाडा")
        assert bhoiwada["name_en"] == "Bhoiwada"

    def test_a_full_address_label_yields_only_the_station_part(self):
        # ps=64's embed is labelled with a whole address whose first part is
        # the road Google named after the station: "Nehru Nagar Police
        # Station Rd". The name is the station, not the road or the pincode.
        src = ("https://www.google.com/maps/embed?pb=!2d72.88!3d19.07"
               "!2sNehru+Nagar+Police+Station+Rd%2C+Nehru+Nagar%2C+Kurla%2C+Mumbai"
               "%2C+Maharashtra+400024!5e0")
        record = parse_station(page_with(src), 64, "नेहरू नगर")
        assert record["name_en"] == "Nehru Nagar"

    def test_a_station_named_after_a_road_keeps_the_road(self):
        src = "https://www.google.com/maps/embed?pb=!2d72.858!3d19.228!2sKasturba+Road+Police+Station!5e0"
        assert parse_station(page_with(src), 41, "कस्तुरबा मार्ग")["name_en"] == "Kasturba Road"

    def test_the_marathi_word_for_station_is_accepted(self):
        # ps=71: "Rafi Ahmed Kidwai Marg Police Thane".
        src = "https://www.google.com/maps/embed?pb=!2d72.86!3d19.02!2sRafi+Ahmed+Kidwai+Marg+Police+Thane!5e0"
        record = parse_station(page_with(src), 71, "आर.ए.के. मार्ग")
        assert record["name_en"] == "Rafi Ahmed Kidwai Marg"

    def test_a_real_name_without_the_suffix_is_still_not_trusted(self):
        # ps=95 is labelled "Yellow Gate", which is its name, but the rule
        # cannot tell that from "Urban hotel". Null, label kept for review.
        src = "https://www.google.com/maps/embed?pb=!2d72.84!3d18.95!2sYellow+Gate!5e0"
        record = parse_station(page_with(src), 95, "यलो गेट")
        assert record["name_en"] is None
        assert record["embed_place"] == "Yellow Gate"

    def test_a_cyber_station_does_not_take_its_host_buildings_name(self):
        # ps=96, "दक्षिण प्रादेशिक विभाग सायबर" (South Region Cyber), sits in
        # D B Marg police station and its map says so. That is the host's
        # name, not this station's, and carrying it would join the cyber
        # station's phones to D B Marg's crime.
        src = "https://www.google.com/maps/embed?pb=!2d72.817!3d18.96!2sD+B+Marg+Police+Station!5e0"
        record = parse_station(page_with(src), 96, "दक्षिण  प्रादेशिक विभाग  सायबर")
        assert record["name_en"] is None
        assert record["embed_place"] == "D B Marg Police Station"
        reason = next(m["reason"] for m in record["missing"] if m["field"] == "name_en")
        assert "host" in reason
        # The territorial station in the same building keeps its name.
        assert parse_station(page_with(src), 22, "डॉ. डी. बी. मार्ग")["name_en"] == "D B Marg"

    def test_a_cyber_station_whose_label_says_cyber_keeps_it(self):
        src = ("https://www.google.com/maps/embed?pb=!2d72.858!3d19.064"
               "!2sCyber+Police+Station%2C+Cyber+Crime%2C+CID%2C+Mumbai!5e0")
        assert parse_station(page_with(src), 21, "सायबर")["name_en"] == "Cyber"

    def test_coordinates_outside_greater_mumbai_are_refused(self):
        src = "https://www.google.com/maps/embed?pb=!2d77.2090!3d28.6139!2sNagpada+Police+Station!5e0"
        record = parse_station(page_with(src), 62, "नागपाडा")
        assert record["lat"] is None and record["lon"] is None
        assert "lat" in missing_fields(record)
        reason = next(m["reason"] for m in record["missing"] if m["field"] == "lat")
        assert "28.6139" in reason

    def test_an_unrecognised_iframe_is_null_with_the_src_in_the_reason(self):
        record = parse_station(page_with("https://example.org/not-a-map"), 62, "नागपाडा")
        assert record["lat"] is None
        reason = next(m["reason"] for m in record["missing"] if m["field"] == "lat")
        assert "example.org" in reason


class TestNormalisePhone:
    """Mumbai landlines are 8 digits under the 022 code, written three ways."""

    def test_ten_devanagari_digits_with_area_code(self):
        assert normalise_phone("२२२३०९२२९३") == ("022-2309-2293", None)

    def test_eight_digits_gain_the_area_code(self):
        assert normalise_phone("२३५३२१४२") == ("022-2353-2142", None)
        assert normalise_phone("23532142") == ("022-2353-2142", None)

    def test_eleven_digits_with_leading_zero(self):
        assert normalise_phone("०२२२४०५००८४") == ("022-2405-0084", None)

    def test_spaces_and_dashes_are_stripped_first(self):
        assert normalise_phone("022 2309 2293") == ("022-2309-2293", None)
        assert normalise_phone("2309-2293") == ("022-2309-2293", None)

    def test_a_ten_digit_mobile_is_kept_verbatim_with_a_note(self):
        # Some stations list a ten-digit mobile as a station number. Not a
        # landline shape, so it is not rewritten, and the note says why. The
        # number here is made up: a real one from a page would be the very
        # thing this suite exists to keep out.
        value, note = normalise_phone("८८८८८७७७७७")
        assert value == "8888877777"
        assert note and "verbatim" in note

    def test_too_few_digits_is_not_a_number(self):
        # Several pages put a chowky's serial (1, 2, 3...) in its phone cell,
        # and one DCP cell reads "2". These are not telephone numbers.
        value, note = normalise_phone("2")
        assert value is None
        assert note
        assert normalise_phone("")[0] is None
        assert normalise_phone("   ")[0] is None

    def test_a_ten_digit_number_not_starting_22_is_not_given_the_area_code(self):
        value, _ = normalise_phone("9876501234")
        assert value == "9876501234"

    def test_digits_from_another_script_are_not_reformatted(self):
        # `str.isdigit` is true of Arabic-Indic and superscript digits too,
        # and only Devanagari is transliterated. Eight such digits must stay
        # as written with a note, not come back as a half-ASCII landline.
        value, note = normalise_phone("\u0662\u0663\u0665\u0663\u0662\u0661\u0664\u0662")
        assert value == "\u0662\u0663\u0665\u0663\u0662\u0661\u0664\u0662"
        assert note and "verbatim" in note


class TestExtractPincode:
    """Pincodes appear as ४०० ००८, 400 050., मुंबई-४०००१८. and bare 400091."""

    @pytest.mark.parametrize("address, expected", [
        ("सोफिया झुबेर रोड, नागपाडा, मुंबई 400 008", "400008"),
        ("Hill Road, Bandra (West), Mumbai 400 050.", "400050"),
        ("5 वा मजला, वरळी पोलीस ठाणे, डॉ. ए.बी.रोड, मुंबई-400018.", "400018"),
        ("विलेपार्ले (पूर्व), मुंबई -400 099", "400099"),
        ("गोराई गाव, मुंबई, महाराष्ट्र 400091", "400091"),
    ])
    def test_reads_each_shape(self, address, expected):
        assert extract_pincode(address) == (expected, None)

    def test_a_year_after_the_pincode_is_not_mistaken_for_it(self):
        # ps=30 appends "स्थापना वर्ष 2017" to its address.
        address = "ग्रांट रोड (पश्चिम,) मुंबई 400 007. गावदेवी पोलीस स्टेशन स्थापना वर्ष 2017"
        assert extract_pincode(address) == ("400007", None)

    def test_plot_numbers_are_not_a_pincode(self):
        address = "प्लॉट क्रमांक 150, 152, 153, 155, आरडीपी.01, चारकोप, मुंबई 400 067"
        assert extract_pincode(address) == ("400067", None)

    def test_a_two_digit_mumbai_suffix_is_not_expanded(self):
        # "मुंबई - 62" means 400062 to a Mumbaikar, but it is not written on
        # the page, so it is not written in the record. The reason names it.
        pincode, reason = extract_pincode("बॅक रोड, गोरेगाव, (पश्चिम) मुंबई - 62")
        assert pincode is None
        assert reason and "62" in reason

    def test_a_pincode_with_a_digit_missing_is_named_not_completed(self):
        # ps=71 ends "मुंबई 400 15". 400015 and 400031 are both one digit
        # away, and the page lists hospitals in each, so no completion is
        # honest. The fragment is quoted so a reviewer can see what was there.
        pincode, reason = extract_pincode(
            "इमारत 01, 'ए' विंग, पहिला मजला, रफी अहमद किडवाई मार्ग, मुंबई 400 15")
        assert pincode is None
        assert reason and "400 15" in reason and "not completed" in reason

    def test_a_pincode_only_in_the_map_label_is_quoted_not_adopted(self):
        # ps=66's address has no pincode; its map label is Google's entry for
        # "Oshiwara Police Station Rd ... 400047", a road, not the office.
        pincode, reason = extract_pincode(
            "न्यू लिंक रोड, म्हाडा कार्यालयाचे समोर, ओशिवरा, जोगेश्वरी (पूर्व), मुंबई",
            map_label="Oshiwara Police Station Rd, Mumbai, Maharashtra 400047")
        assert pincode is None
        assert reason and "400047" in reason and "not adopted" in reason

    def test_a_label_pincode_is_never_adopted_by_the_parser(self):
        src = ("https://www.google.com/maps/embed?pb=!2d72.83!3d19.14"
               "!2sOshiwara+Police+Station+Rd%2C+Mumbai%2C+Maharashtra+400047!5e0")
        record = parse_station(page_with(src, address="न्यू लिंक रोड, मुंबई"), 66, "ओशिवरा")
        assert record["pincode"] is None
        assert record["lat"] == 19.14
        reasons = [m["reason"] for m in record["missing"] if m["field"] == "pincode"]
        assert reasons and "400047" in reasons[0]

    def test_no_pincode_at_all(self):
        pincode, reason = extract_pincode("न्यू लिंक रोड, अंधेरी (पश्चिम), मुंबई")
        assert pincode is None
        assert reason == "no six-digit pincode in the address"

    def test_none_in_none_out(self):
        assert extract_pincode(None) == (None, "no address to read a pincode from")


class TestPlateNumber:
    """The number beside the Sr. PI's name is officer identity, wherever it recurs.

    Three pages repeat it in the station's own "Telephone Nos" cell. The
    fixtures scrub it as the officer's mobile, so the record cannot carry it
    either, and a station whose only number was that one is null with a
    reason. The numbers here are made up and appear on no page.
    """

    PLATE = "८८८८८७७७७७"

    def test_repeated_in_the_station_cell_it_is_dropped_and_the_rest_kept(self):
        page = page_with(plate=self.PLATE).replace(
            '<a href="२३५३२१४२">२३५३२१४२</a>',
            f'<a href="२३५३२१४२">२३५३२१४२</a>, <a href="{self.PLATE}">{self.PLATE}</a>')
        record = parse_station(page, 15, "भायखळा")
        assert record["phones"] == ["022-2353-2142"]
        text = dump(record)
        assert "8888877777" not in text and self.PLATE not in text
        assert any("Sr. PI" in n and "not kept" in n for n in record["notes"])

    def test_when_it_is_the_only_number_phones_is_null_with_a_reason(self):
        page = page_with(plate=self.PLATE).replace(
            '<a href="२३५३२१४२">२३५३२१४२</a>', f'<a href="{self.PLATE}">{self.PLATE}</a>')
        record = parse_station(page, 15, "भायखळा")
        assert record["phones"] is None
        assert "phones" in missing_fields(record)
        reason = next(m["reason"] for m in record["missing"] if m["field"] == "phones")
        assert "Sr. PI" in reason and "8888877777" not in reason

    def test_in_a_chowky_or_office_cell_it_is_dropped_too(self):
        page = page_with(plate=self.PLATE, Beat_chowki_1="अ चौकी", Tel_no_chowki_1=self.PLATE,
                         DCP_Tel_no=f"२३७००६०८, {self.PLATE}")
        record = parse_station(page, 15, "भायखळा")
        assert record["beat_chowkies"][0]["phones"] == []
        assert record["dcp_office_phone"] == "022-2370-0608"
        assert "8888877777" not in dump(record)

    def test_a_page_without_a_plate_is_untouched(self):
        record = parse_station(page_with(), 15, "भायखळा")
        assert record["phones"] == ["022-2353-2142"]
        assert not any("Sr. PI" in n for n in record["notes"])


class TestChowkyDetails:
    def test_a_chowky_phone_cell_is_attached_to_its_chowky(self):
        page = page_with(
            Beat_chowki_1="भारत नगर पोलीस चौकी",
            Tel_no_chowki_1="२६५०१२३४",
            Beat_chowki_2="वाल्मिकी नगर पोलीस चौकी",
            Tel_no_chowki_2="2",
        )
        record = parse_station(page, 10, "बी.के.सी.")
        chowkies = record["beat_chowkies"]
        assert chowkies[0]["phones"] == ["022-2650-1234"]
        # "2" is the chowky's serial number typed into its phone cell, not a
        # phone. It is dropped, and the note says so.
        assert chowkies[1]["phones"] == []
        assert any("2" in n and "chowky" in n.lower() for n in record["notes"])

    def test_a_number_written_into_the_chowky_name_is_moved_to_its_phones(self):
        # ps=13: "तकिया मस्जीद 02220847278".
        record = parse_station(page_with(Beat_chowki_1="तकिया मस्जीद 02220847278"), 13, "भोईवाडा")
        assert record["beat_chowkies"][0]["name"] == "तकिया मस्जीद"
        assert record["beat_chowkies"][0]["phones"] == ["022-2084-7278"]

    def test_numbering_gaps_do_not_truncate_the_list(self):
        # ps=58 has chowky cells 3 and 5 and nothing between.
        record = parse_station(page_with(Beat_chowki_3="अ चौकी", Beat_chowki_5="ब चौकी"), 58, "x")
        assert [c["name"] for c in record["beat_chowkies"]] == ["अ चौकी", "ब चौकी"]

    def test_no_chowky_cells_is_null_with_a_reason(self):
        record = parse_station(page_with(), 21, "सायबर")
        assert record["beat_chowkies"] is None
        assert "beat_chowkies" in missing_fields(record)


class TestOddCells:
    def test_area_with_a_stray_space_in_the_decimal(self):
        # ps=7 writes "४. ११ Sq.Kms."
        assert parse_station(page_with(area="४. ११ Sq.Kms."), 7, "x")["area_sqkm"] == 4.11

    def test_area_with_marathi_units_repeated(self):
        assert parse_station(page_with(area="३.५ चौरस किलोमीटर Sq.Kms."), 26, "x")["area_sqkm"] == 3.5

    def test_area_not_set(self):
        record = parse_station(page_with(area="Not Set Sq.Kms."), 101, "x")
        assert record["area_sqkm"] is None
        assert "area_sqkm" in missing_fields(record)

    def test_population_with_no_figure_is_null(self):
        record = parse_station(page_with(Population="Lakhs"), 21, "x")
        assert record["population_note"] is None
        assert "population_note" in missing_fields(record)

    def test_population_is_a_note_not_a_number(self):
        # ps=4 says "७००० Lakhs", which would be 700 million people. Kept as
        # the page wrote it, transliterated, and never computed on.
        assert parse_station(page_with(Population="७००० Lakhs"), 4, "x")["population_note"] == "7000 Lakhs"

    def test_devanagari_beat_marshal_count(self):
        assert parse_station(page_with(beat_mar="०२"), 2, "x")["beat_marshals"] == 2

    def test_empty_email_cell_is_null(self):
        page = page_with().replace(
            '<h4 title=" static.Locate_us">',
            '<p title=" static.Email_id"><span>Email ID :</span> <span class="txt-val" title=""> <a href="mailto:"></a></span></p>'
            '<h4 title=" static.Locate_us">')
        record = parse_station(page, 21, "x")
        assert record["email"] is None
        assert "email" in missing_fields(record)

    def test_an_email_with_two_at_signs_is_null_with_the_cell_quoted(self):
        # ps=47 writes "ps[dot]midc[dot]mum[at]mahapolice[at]gov[dot]in".
        # Reading it as "ps.midc.mum@mahapolice@gov.in" would publish a
        # string that only looks like an address.
        record = parse_station(
            page_with(Email_id="ps[dot]midc[dot]mum[at]mahapolice[at]gov[dot]in"), 47, "x")
        assert record["email"] is None
        reason = next(m["reason"] for m in record["missing"] if m["field"] == "email")
        assert "[at]mahapolice[at]" in reason

    def test_two_addresses_in_one_cell_are_both_kept(self):
        # ps=104 publishes a gmail address and a mahapolice one with a slash
        # between them. Both are the office's; neither is dropped, and they
        # are not run together into one string.
        record = parse_station(page_with(
            Email_id="cybernorthregion[at]gmail[dot]com / ps[dot]northcyber[dot]mum[at]mahapolice[dot]gov[dot]in"),
            104, "x")
        assert record["email"] == "cybernorthregion@gmail.com, ps.northcyber.mum@mahapolice.gov.in"
        assert "email" not in missing_fields(record)

    def test_an_address_without_at_is_null(self):
        # ps=71 writes "[dot]" where "[at]" belongs.
        record = parse_station(
            page_with(Email_id="ps[dot]rakmarg[dot]mum[dot]mahapolice[dot]gov[dot]in"), 71, "x")
        assert record["email"] is None
        assert "email" in missing_fields(record)

    def test_a_plain_address_and_a_bracketed_one_read_the_same(self):
        plain = parse_station(page_with(Email_id="ps.vakola.mum@mahapolice.gov.in"), 86, "x")
        bracketed = parse_station(
            page_with(Email_id="PS[dot]Vakola[dot]mum[at]mahapolice[dot]gov[dot]in"), 86, "x")
        assert plain["email"] == bracketed["email"] == "ps.vakola.mum@mahapolice.gov.in"

    def test_duplicate_numbers_in_one_cell_are_listed_once(self):
        # ps=43 lists ०२२२६५७०८७७ twice.
        page = page_with().replace(
            '<a href="२३५३२१४२">२३५३२१४२</a>',
            '<a href="०२२२६५७०८७७">०२२२६५७०८७७</a>, <a href="०२२२६५७०८७७">०२२२६५७०८७७</a>')
        assert parse_station(page, 43, "x")["phones"] == ["022-2657-0877"]
