"""Brihan Mumbai Police's station directory: one saved page in, one record out.

`mumbaipolice.gov.in/policestation?ps=<id>` is the commissionerate's own page
for each of its 99 stations, and it carries what a person in trouble needs
and the FIR feed does not: office telephone numbers, an office email, the
beat chowkies, the nearest railway station, the office address with its
pincode, and a map embed that places the office.
`scripts/crawl_mumbaipolice_stations.py` saves those pages, one request at a
time; this module reads the saved files and makes no request of its own.

Every page also names four people -- the Senior PI, with a mobile number
beside the name, and the Divisional ACP, Zonal DCP and Regional Addl. CP,
each linked to a profile. None of that is read. The cells are keyed by the
site's own template keys (`static.ACP_Div`, ...), the ones that name a person
are listed in `NEVER_READ` so the omission is visible rather than accidental,
and `parse_station` ends by checking the finished record against the names
on the page and raising if one got through. The project persists no names of
people, the site's own disclaimer says they change, and a directory of who to
call does not need them.

The number beside the Sr. PI's name is treated the same way as the name. On
three pages the station's own "Telephone Nos" cell repeats it, and there it
would be easy to read as an office line; it is still the number printed
beside a named person, and the fixtures scrub it as officer identity, so the
record must not carry it either. `_scrub_plate_number` removes it from every
telephone field after parsing and says so in `notes` without repeating the
digits. A station whose only listed number was that one has `phones` null,
with the reason, rather than a number that identifies its inspector.

Two rules from docs/INGESTION.md shape the record:

* **Absence is never zero.** A cell the page does not carry, or carries
  empty, is null with a reason in `missing`. `phones` is a list only when at
  least one number was read; a blank cell is null, not `[]`, because a map
  would draw `[]` as "no phone" when the truth is "not published".
* **Nothing is fabricated.** "Mumbai - 62" is not expanded to 400062. A map
  label that does not say "Police Station" does not become the station's
  English name. Coordinates outside Greater Mumbai are refused, not drawn.

Telephone numbers. Mumbai landlines are eight digits under the 022 code, and
the site writes them three ways -- eight digits, 22 plus eight, 022 plus
eight -- mostly in Devanagari. All three normalise to `022-XXXX-XXXX`.
Anything else is not rewritten: a ten-digit mobile that a station lists as
its own is kept as written with a note, and fewer than six digits (several
pages type a chowky's serial number into its phone cell) is not a telephone
number and is dropped with a note. The site warns that its numbers may have
changed since publication, and the map must say so too.

Email. The site spells its addresses out as "ps[dot]x[dot]mum[at]..." to
foil harvesters, and the record carries the plain address. One page spells
"[at]" twice, which is not an address and is null with the cell quoted;
one lists two addresses with a slash between them, and both are kept, joined
with a comma the way a two-number DCP office is.

Run:  python3 -m pipeline.mumbaipolice
"""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote_plus

from .taxonomy import devanagari_digits_to_ascii

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "mumbaipolice"
STATIONS_DIR = RAW / "stations"
ROSTER = RAW / "getpolicestations.json"
OUT = ROOT / "data" / "spine" / "mumbai_stations.json"

SOURCE_URL = "https://mumbaipolice.gov.in/policestation?ps={ps_id}"
RAW_FILE = "data/raw/mumbaipolice/stations/ps_{ps_id}.html"

# The record, in the order every module downstream agrees on. A record
# carries these keys and no others; the last five are provenance and
# bookkeeping rather than data from the page.
FIELDS = (
    "ps_id", "name_mr", "name_en", "lat", "lon", "phones", "email",
    "division_mr", "zone_mr", "region_mr",
    "acp_office_phone", "dcp_office_phone", "addl_cp_office_phone",
    "area_sqkm", "population_note", "beat_marshals", "beat_chowkies",
    "nearest_railway", "bus_depot", "address", "pincode",
    "source_url", "fetched_from_file",
    "embed_place", "coords_source", "page_recognised", "missing", "notes",
)

# The site's template keys, which label every cell as `<p title=" static.X">`.
# Cells are found by key rather than by the English label beside them: the
# labels are translations that can be re-worded, the keys are what the
# template renders from.
KEY = {
    "phones": "Tel_no",
    "email": "Email_id",
    "division_mr": "Div",
    "zone_mr": "zone",
    "region_mr": "region",
    "acp_office_phone": "ACP_Tel_no",
    "dcp_office_phone": "DCP_Tel_no",
    "addl_cp_office_phone": "Regional_Addl_CP_contactno",
    "population_note": "Population",
    "area_sqkm": "area",
    "beat_marshals": "beat_mar",
    "nearest_railway": "ps_rs",
    "bus_depot": "ps_bdepo",
}

# Cells that name a person. `_officer_names` reads them only to check that
# the finished record does not contain them, and discards what it read. The
# Sr. PI's name plate is not a keyed cell; `NAME_PLATE` below finds it for
# the same check.
NEVER_READ = ("ACP_Div", "DCP_Zone", "Regional_Addl_CP")

# Greater Mumbai, generously. A page whose map falls outside this is pointing
# at the wrong place, and a wrong pin is worse than no pin.
LAT_RANGE = (18.85, 19.35)
LON_RANGE = (72.70, 73.05)

TAG = re.compile(r"<[^>]+>")
PARAGRAPH = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
VALUE_SPAN = re.compile(r'<span\s+class="txt-val"[^>]*>(.*?)</span>', re.S | re.I)
STATIC_KEY = re.compile(r"static\.(\w+)")
CHOWKY_KEY = re.compile(r"^Beat_chowki_(\d+)$")
NAME_PLATE = re.compile(r'class="ips-name-plate"[^>]*>(.*?)</span>', re.S)
PROFILE_LINK = re.compile(r'\?name=([^"&]+)')
PLATE_NUMBER = re.compile(r'class="post-locate".*?Police Station,\s*([०-९\d]{8,})', re.S)

# `str.isdigit` is true of every script's digits, and only Devanagari is
# transliterated, so the shape test names 0-9 outright: eight Arabic-Indic
# digits must not come back as "022-٢٣٥٣-٢١٤٢".
ASCII_DIGITS = re.compile(r"[0-9]+")
# One address after de-obfuscation: a local part, one "@", a dotted domain.
# The site's own typo "x[at]mahapolice[at]gov[dot]in" has two "@" and fails.
EMAIL = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+$")

IFRAME = re.compile(r'<iframe\b[^>]*\bsrc="([^"]*)"', re.I)
# In an embed (`/maps/embed?pb=`) !3d is latitude and !2d longitude. In a
# place URL (`/maps/place/...`) !3d is latitude and !4d longitude. Two pages
# use a place URL and one has a bare "lat,lon" as the iframe src.
PB_LAT = re.compile(r"!3d(-?\d+(?:\.\d+)?)")
PB_LON = re.compile(r"!2d(-?\d+(?:\.\d+)?)")
PLACE_LON = re.compile(r"!4d(-?\d+(?:\.\d+)?)")
PB_LABEL = re.compile(r"!2s([^!]*)")
PLACE_LABEL = re.compile(r"/maps/place/([^/@?]+)")
BARE_LATLON = re.compile(r"^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$")
# "Police Thane" is the Marathi word for the same thing, and one label uses it.
POLICE_STATION = re.compile(r"\s*police\s+(?:station|thane|thana)\s*", re.I)
STATION_ROAD = re.compile(r"\s*police\s+(?:station|thane|thana)\s+(?:rd|road)\b\.?", re.I)

ADDRESS = re.compile(r'<div\s+class="map-info"[^>]*>.*?<p>(.*?)</p>', re.S | re.I)
# Mumbai pincodes are 400xxx, written "400 008", "400008" or "-400018". A
# year appended to an address ("स्थापना वर्ष 2017") is four digits and never
# matches; a plot number is three.
PINCODE = re.compile(r"(?<!\d)(4\d{2})\s?(\d{3})(?!\d)")
# "मुंबई - 62": the postal-district suffix Mumbaikars write for 400062. Named
# in the reason so a reviewer can resolve it; never expanded here.
PIN_SUFFIX = re.compile(r"(?:मुंबई|Mumbai)\s*-?\s*(\d{2})\s*\.?\s*$", re.I)
# "मुंबई 400 15": a pincode typed with a digit missing. Which digit is not
# knowable from the page -- the hospitals listed beside that address are in
# three different postal districts -- so the fragment is named, not completed.
PIN_TRUNCATED = re.compile(r"(?<!\d)(4\d{2}\s?\d{1,2})(?!\d)\s*\.?\s*$")


class PersonalDataLeak(RuntimeError):
    """A name from the page reached the record. A parser bug, never data."""


def _text(fragment: str) -> str:
    """Visible text of an HTML fragment, whitespace collapsed.

    Marathi text is kept in the site's own script, digits included: a zone
    label or a chowky name is an identifier, and "परिमंडळ-२" must match the
    site's spelling wherever it is used as one. Only the fields that carry a
    figure -- phones, address, area, population, marshals -- transliterate.
    """
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", fragment))).strip()


def _cells(page: str) -> dict[str, str]:
    """Template key -> the `<p>` block it labels, first occurrence wins.

    Only the part of the block before the value span is searched for keys,
    because a value's own title can carry one too ("5 static.Lakhs").
    """
    cells: dict[str, str] = {}
    for block in PARAGRAPH.findall(page):
        head = block.split('class="txt-val"', 1)[0]
        for key in STATIC_KEY.findall(head):
            cells.setdefault(key, block)
    return cells


def _value(block: str) -> str:
    """Text of the value span(s) in a cell. Empty string if there is none."""
    return " ".join(t for t in (_text(v) for v in VALUE_SPAN.findall(block)) if t)


def normalise_phone(raw: str | None) -> tuple[str | None, str | None]:
    """(number, note) for one telephone number as the site wrote it.

    A recognised Mumbai landline comes back as 022-XXXX-XXXX with no note. An
    unrecognised shape with six or more digits comes back as written, with a
    note saying why it was left alone. Fewer than six digits is not a
    telephone number: the number is None and the note says what was there.
    """
    text = devanagari_digits_to_ascii(raw or "").strip()
    compact = re.sub(r"[\s\-()]", "", text)
    if not compact:
        return None, "empty"
    if not ASCII_DIGITS.fullmatch(compact):
        return text, f"'{text}' kept verbatim: not all 0-9 digits"
    if len(compact) < 6:
        return None, f"'{text}' is not a telephone number: {len(compact)} digit(s)"
    if len(compact) == 8:
        local = compact
    elif len(compact) == 10 and compact.startswith("22"):
        local = compact[2:]
    elif len(compact) == 11 and compact.startswith("022"):
        local = compact[3:]
    else:
        return compact, (f"'{compact}' kept verbatim: {len(compact)} digits, "
                         f"not a Mumbai landline shape")
    return f"022-{local[:4]}-{local[4:]}", None


def _phones(value: str, where: str, notes: list[str]) -> list[str]:
    """Every number in a comma-separated cell, normalised, listed once."""
    numbers: list[str] = []
    for part in value.split(","):
        if not part.strip():
            continue
        number, note = normalise_phone(part)
        if note:
            notes.append(f"{where}: {note}")
        if number and number not in numbers:
            numbers.append(number)
    return numbers


def _emails(value: str, notes: list[str]) -> list[str]:
    """Every address in an email cell, de-obfuscated, listed once.

    Addresses are separated by a slash, semicolon or comma; whitespace inside
    one is the site's spacing around "[dot]" and is dropped. A part that is
    not an address after de-obfuscation is left out with a note, so the
    field never carries a string that only looks like an address.
    """
    addresses: list[str] = []
    for part in re.split(r"[/;,]", value.lower()):
        email = re.sub(r"\s+", "", part)
        if not email:
            continue
        for pattern, plain in (("[dot]", "."), ("(dot)", "."), ("[at]", "@"), ("(at)", "@")):
            email = email.replace(pattern, plain)
        if not EMAIL.match(email):
            notes.append(f"email: '{part.strip()}' is not an address; not kept")
        elif email not in addresses:
            addresses.append(email)
    return addresses


def extract_pincode(address: str | None,
                    map_label: str | None = None) -> tuple[str | None, str | None]:
    """(pincode, reason). One of the two is always None.

    Only the office's own published address is read. `map_label` is the
    Google label under the page's map, and a pincode there is Google's for
    whatever the site's editor searched -- on ps=66 the road, not the office.
    It is quoted in the reason for a reviewer and never adopted.
    """
    if not address:
        return None, "no address to read a pincode from"
    text = devanagari_digits_to_ascii(address)
    found = PINCODE.search(text)
    if found:
        return found.group(1) + found.group(2), None
    suffix = PIN_SUFFIX.search(text)
    if suffix:
        return None, (f"address ends with the two-digit Mumbai postal suffix "
                      f"'{suffix.group(1)}', not a full pincode; not expanded")
    truncated = PIN_TRUNCATED.search(text)
    if truncated:
        return None, (f"address ends with '{truncated.group(1)}', a pincode "
                      f"with a digit missing; which digit is not knowable, "
                      f"so it is not completed")
    reason = "no six-digit pincode in the address"
    in_label = PINCODE.search(map_label or "")
    if in_label:
        reason += (f"; the map label carries {in_label.group(1)}{in_label.group(2)}, "
                   f"which is Google's pincode for what the map was searched "
                   f"by, not the office's published address; not adopted")
    return None, reason


def _map(page: str) -> tuple[float | None, float | None, str | None, str | None, str | None]:
    """(lat, lon, label, source, reason) from the iframe under "Locate Us"."""
    start = page.find("static.Locate_us")
    found = IFRAME.search(page, start if start >= 0 else 0)
    if not found:
        return None, None, None, None, "no map iframe on the page"
    src = html.unescape(found.group(1))
    label = None
    if "/maps/embed?" in src:
        source = "maps_embed"
        lat, lon = PB_LAT.search(src), PB_LON.search(src)
        labelled = PB_LABEL.search(src)
        label = labelled.group(1) if labelled else None
    elif "/maps/place/" in src:
        source = "maps_place_url"
        lat, lon = PB_LAT.search(src), PLACE_LON.search(src)
        labelled = PLACE_LABEL.search(src)
        label = labelled.group(1) if labelled else None
    elif BARE_LATLON.match(src):
        source = "iframe_bare_latlon"
        bare = BARE_LATLON.match(src)
        lat, lon = bare, bare
    else:
        return None, None, None, None, (
            f"map iframe src is not a shape this parser knows: {src[:80]}")
    if label is not None:
        label = re.sub(r"\s+", " ", unquote_plus(label)).strip() or None
    if not lat or not lon:
        return None, None, label, None, f"{source} iframe carries no coordinates"
    lat_v = float(lat.group(1))
    lon_v = float(lon.group(2) if source == "iframe_bare_latlon" else lon.group(1))
    if not (LAT_RANGE[0] <= lat_v <= LAT_RANGE[1] and LON_RANGE[0] <= lon_v <= LON_RANGE[1]):
        return None, None, label, None, (
            f"coordinates ({lat_v}, {lon_v}) fall outside Greater Mumbai; "
            f"the page's map points somewhere else")
    return lat_v, lon_v, label, source, None


def _english_name(label: str | None) -> tuple[str | None, str | None]:
    """The station's English name from a map label, or why there is none.

    Only a label that says "Police Station" (or "Police Thane") is trusted:
    the label is whatever the site's editor searched for when placing the
    map, and on two pages that was "Urban hotel" and "in". The cost is that
    "Ram Mandir" and "Yellow Gate", which are real station names written
    without the suffix, come back null too; `embed_place` keeps the label so
    a reviewer can confirm them by hand rather than a rule guessing.
    """
    if not label:
        return None, "no map label to take an English name from"
    if not POLICE_STATION.search(label):
        return None, f"map label does not name a police station: '{label}'"
    # Two labels are a full address ("Nehru Nagar Police Station, Nehru Nagar
    # Rd, Kurla, ..."). The name is the comma-separated part that says
    # "Police Station", not the road and pincode after it.
    segment = next(s for s in label.split(",") if POLICE_STATION.search(s))
    # "Nehru Nagar Police Station Rd" is Google naming the road after the
    # station; the station is what comes before. A road the station is merely
    # named after ("Kasturba Road Police Station") is left whole.
    segment = STATION_ROAD.sub(" ", segment)
    name = re.sub(r"\s+", " ", POLICE_STATION.sub(" ", segment)).strip(" -()")
    if not name:
        return None, "map label is just 'Police Station'"
    return name, None


def _chowkies(cells: dict[str, str], notes: list[str]) -> list[dict] | None:
    """Beat chowkies in the site's numbering, with gaps tolerated.

    "NAME - loc1, loc2" splits into a name and its localities. A number on
    the end of a name is a phone typed into the wrong cell and moves to
    `phones`; a numbered `Tel_no_chowki_N` cell is read alongside.
    """
    numbered = sorted((int(m.group(1)), key) for key in cells
                      for m in [CHOWKY_KEY.match(key)] if m)
    out = []
    for n, key in numbered:
        raw = _value(cells[key])
        phones: list[str] = []
        # Searched on a transliterated copy; the mapping is one character to
        # one, so the match's offsets apply to the original text.
        trailing = re.search(r"\s+(\d{6,})\s*$", devanagari_digits_to_ascii(raw))
        if trailing:
            raw = raw[:trailing.start()]
            phones += _phones(trailing.group(1), f"chowky {n} name", notes)
        split = re.match(r"^(.*?)\s+-\s*(.+)$", raw)
        if split:
            name = split.group(1).strip()
            localities = [l.strip() for l in split.group(2).split(",") if l.strip()]
        else:
            name, localities = raw.strip(), []
        if not name:
            continue
        tel = cells.get(f"Tel_no_chowki_{n}")
        if tel:
            for number in _phones(_value(tel), f"chowky {n} phone", notes):
                if number not in phones:
                    phones.append(number)
        out.append({"name": name, "localities": localities, "phones": phones})
    return out or None


def _officer_names(page: str, cells: dict[str, str]) -> list[str]:
    """What the page calls its officers. Read for the leak check only."""
    names = [_text(m) for m in NAME_PLATE.findall(page)]
    names += [_text(unquote_plus(m)) for m in PROFILE_LINK.findall(page)]
    names += [_value(cells[key]) for key in NEVER_READ if key in cells]
    return [n.strip(" ,") for n in names if len(n.strip(" ,")) >= 3]


def parse_station(page: str, ps_id: int, name_mr: str | None,
                  fetched_from_file: str | None = None) -> dict:
    """One station record from one saved page. Never raises for a missing field.

    `ps_id` and `name_mr` come from the site's roster
    (`data/raw/mumbaipolice/getpolicestations.json`), not from the page.
    Raises `PersonalDataLeak` only if an officer's name is found in the
    finished record, which would be a bug here rather than a fact about the
    page.
    """
    missing: list[dict] = []
    notes: list[str] = []
    record: dict = {field: None for field in FIELDS}
    record.update(ps_id=ps_id, name_mr=name_mr or None,
                  source_url=SOURCE_URL.format(ps_id=ps_id),
                  fetched_from_file=fetched_from_file or RAW_FILE.format(ps_id=ps_id))

    def gap(field: str, reason: str) -> None:
        missing.append({"field": field, "reason": reason})

    if not name_mr:
        gap("name_mr", "the roster gave no Marathi name for this id")

    cells = _cells(page)
    recognised = KEY["phones"] in cells
    record["page_recognised"] = recognised
    if not recognised:
        gap("page", "not a station page: no 'Telephone Nos' cell (an error "
                    "page, or the site changed)")

    def cell(field: str) -> str | None:
        """The cell's text, or None with the gap recorded."""
        block = cells.get(KEY[field])
        if block is None:
            gap(field, f"no '{KEY[field]}' cell on the page")
            return None
        value = _value(block)
        if not value:
            gap(field, f"'{KEY[field]}' cell is empty")
            return None
        return value

    value = cell("phones")
    if value is not None:
        numbers = _phones(value, "phones", notes)
        if numbers:
            record["phones"] = numbers
        else:
            gap("phones", f"'{KEY['phones']}' cell holds no telephone number: '{value}'")

    value = cell("email")
    if value is not None:
        addresses = _emails(value, notes)
        if addresses:
            # Joined for the same reason the DCP office's numbers are: the
            # schema says a string, and one page publishes two addresses.
            record["email"] = ", ".join(addresses)
        else:
            gap("email", f"'{KEY['email']}' cell is not an address: '{value}'")

    for field in ("division_mr", "zone_mr", "region_mr", "nearest_railway", "bus_depot"):
        value = cell(field)
        if value is not None:
            record[field] = value

    for field in ("acp_office_phone", "dcp_office_phone", "addl_cp_office_phone"):
        value = cell(field)
        if value is not None:
            numbers = _phones(value, field, notes)
            if numbers:
                # More than one number is common for a DCP office. Joined so
                # the field stays a string, as the schema says.
                record[field] = ", ".join(numbers)
            else:
                gap(field, f"'{KEY[field]}' cell holds no telephone number: '{value}'")

    value = cell("area_sqkm")
    if value is not None:
        value = devanagari_digits_to_ascii(value)
        figure = re.search(r"\d+(?:\s*\.\s*\d+)?", value)
        if figure:
            record["area_sqkm"] = float(re.sub(r"\s", "", figure.group(0)))
        else:
            gap("area_sqkm", f"'{KEY['area_sqkm']}' cell has no figure: '{value}'")

    value = cell("population_note")
    if value is not None:
        value = devanagari_digits_to_ascii(value)
        if re.search(r"\d", value):
            # A note, never a number: pages say "5 Lakhs" and also "7000
            # Lakhs" and "182000 Lakhs", which is a raw count mislabelled.
            record["population_note"] = value
        else:
            gap("population_note", f"'{KEY['population_note']}' cell has no figure: '{value}'")

    value = cell("beat_marshals")
    if value is not None:
        value = devanagari_digits_to_ascii(value)
        if value.isdigit():
            record["beat_marshals"] = int(value)
        else:
            gap("beat_marshals", f"'{KEY['beat_marshals']}' cell is not a count: '{value}'")

    chowkies = _chowkies(cells, notes)
    if chowkies:
        record["beat_chowkies"] = chowkies
    else:
        gap("beat_chowkies", "no 'Beat_chowki_N' cells on the page")

    found = ADDRESS.search(page)
    # The one Marathi field that is transliterated: its pincode has to be
    # searchable, and the site writes it as ४०० ००८ on most pages.
    address = devanagari_digits_to_ascii(_text(found.group(1))) if found else ""
    if address:
        record["address"] = address
    else:
        gap("address", "no 'Locate Us' address block on the page")

    lat, lon, label, source, reason = _map(page)
    record.update(lat=lat, lon=lon, coords_source=source, embed_place=label)
    if reason:
        gap("lat", reason)
        gap("lon", reason)
    # After the map so that a pincode the label carries and the address does
    # not can be named in the reason; see `extract_pincode`.
    pincode, reason = extract_pincode(address or None, label)
    if pincode:
        record["pincode"] = pincode
    else:
        gap("pincode", reason)
    name_en, reason = _english_name(label)
    if name_en and "सायबर" in (name_mr or "") and "cyber" not in name_en.lower():
        # The five regional cyber stations are housed in a territorial
        # station's building, and their map is that building's: "D B Marg
        # Police Station" for the South Region cyber station. Carrying the
        # host's name would join the cyber station's phones to the host's
        # crime, so the label is kept for review and the name is not derived.
        reason = (f"the roster says this is a cyber station but the map label "
                  f"names its host building: '{label}'")
        name_en = None
    if name_en:
        record["name_en"] = name_en
    else:
        gap("name_en", reason)

    record["missing"] = missing
    record["notes"] = notes
    _scrub_plate_number(record, page, gap)
    _check_no_leak(record, page, cells)
    return record


def plate_number(page: str) -> str | None:
    """The number printed beside the Sr. PI's name, normalised, if any.

    Read for the scrub and the leak check only; never written anywhere.
    """
    plate = PLATE_NUMBER.search(page)
    if not plate:
        return None
    number, _ = normalise_phone(plate.group(1))
    return number


def _scrub_plate_number(record: dict, page: str, gap) -> None:
    """Drop the Sr. PI's name-plate number from every telephone field.

    The digits are not repeated in the note: the note is in the record, and
    the point is that the record does not carry them. `gap` is the parser's
    own `missing` writer, so a field emptied here is null with a reason like
    any other absence.
    """
    number = plate_number(page)
    if not number:
        return
    dropped: list[str] = []

    def keep(numbers: list[str], where: str) -> list[str]:
        if number in numbers:
            dropped.append(where)
        return [n for n in numbers if n != number]

    if record["phones"]:
        kept = keep(record["phones"], "phones")
        record["phones"] = kept or None
        if not kept:
            gap("phones", "the only number the station lists is the one printed "
                          "beside the Sr. PI's name; not kept")
    for field in ("acp_office_phone", "dcp_office_phone", "addl_cp_office_phone"):
        if record[field]:
            kept = keep(record[field].split(", "), field)
            record[field] = ", ".join(kept) or None
            if not kept:
                gap(field, "the only number in the cell is the one printed beside "
                           "the Sr. PI's name; not kept")
    for i, chowky in enumerate(record["beat_chowkies"] or []):
        chowky["phones"] = keep(chowky["phones"], f"chowky {i + 1} phone")
    # The verbatim-kept note written while parsing quotes the digits.
    record["notes"] = [n for n in record["notes"] if number not in n]
    for where in dropped:
        record["notes"].append(
            f"{where}: one number is the one printed beside the Sr. PI's name "
            f"and is not kept")


def _check_no_leak(record: dict, page: str, cells: dict[str, str]) -> None:
    """Raise if an officer's name, or the name-plate number, is in the record."""
    blob = json.dumps(record, ensure_ascii=False)
    for name in _officer_names(page, cells):
        if name in blob:
            raise PersonalDataLeak(
                f"an officer's name from the page is in the record for "
                f"ps={record['ps_id']}. Not writing it anywhere.")
    number = plate_number(page)
    if number and number in blob:
        raise PersonalDataLeak(
            f"the number beside the Sr. PI's name is in the record for "
            f"ps={record['ps_id']}. Not writing it anywhere.")


def load_roster(path: Path = ROSTER) -> dict[int, str]:
    """ps_id -> Marathi name, from the site's own station list."""
    entries = json.loads(path.read_text(encoding="utf-8"))
    return {int(e["id"]): e["name"].strip() for e in entries}


def parse_all(stations_dir: Path = STATIONS_DIR, roster_path: Path = ROSTER) -> list[dict]:
    """Every saved page, parsed, in ps_id order."""
    roster = load_roster(roster_path) if roster_path.exists() else {}
    records = []
    for path in stations_dir.glob("ps_*.html"):
        ps_id = int(path.stem.split("_", 1)[1])
        page = path.read_text(encoding="utf-8")
        records.append(parse_station(page, ps_id, roster.get(ps_id),
                                     str(path.relative_to(ROOT))))
    return sorted(records, key=lambda r: r["ps_id"])


def main() -> int:
    records = parse_all()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")

    recognised = [r for r in records if r["page_recognised"]]
    gaps = Counter(m["field"] for r in records for m in r["missing"])
    print(f"{len(records)} pages on disk, {len(recognised)} recognised as station pages")
    print(f"{sum(1 for r in records if r['lat'] is not None)} with coordinates, "
          f"{sum(1 for r in records if r['pincode'])} with a pincode, "
          f"{sum(1 for r in records if r['phones'])} with an office telephone")
    if gaps:
        print("missing, by field:")
        for field, count in gaps.most_common():
            print(f"  {field:22s} {count}")
    unplaced = [r["ps_id"] for r in records if r["lat"] is None]
    if unplaced:
        print(f"listed, not drawn (no coordinates): ps={unplaced}")
    print(f"{sum(len(r['notes']) for r in records)} notes on kept-verbatim or dropped values")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
