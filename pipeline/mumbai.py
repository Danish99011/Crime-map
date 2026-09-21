"""Aggregate Mumbai's published FIRs to station-month and place them on a map.

Mumbai is the inverse of everywhere else in this project. Maharashtra runs the
most open crime feed in India -- every FIR, daily, station-level, timestamped
to the second -- and publishes no police station jurisdiction polygons at all.
So the crime data is the best available and the geography is the weak half.

That asymmetry decides how this renders. Every other city in `cities.py` can
draw a thana as a filled area; Mumbai cannot, because no such area has been
published. What exists is a point per station from the MHA station master, and
**a station point is not a jurisdiction**. It is the address of the office that
registered the FIR. Drawing a catchment around it, or a pin at it, would invent
a geography the state has not published -- the precise failure
`docs/PHASE1-FINDINGS.md` section 6 catches other apps committing.

Three things this module refuses to do
--------------------------------------
* **Place an FIR anywhere but at its registering station.** No jitter, no
  interpolation, no nearest-road snapping.
* **Drop a station because we lack its coordinates.** Four Mumbai stations
  appear in the FIR feed but not in the MHA master. Their FIRs are counted and
  reported as unplaced rather than quietly discarded, because discarding them
  would shrink the city's total to match our own gaps.
* **Show a month as quiet when it was merely unfetched.** Coverage is carried
  per month, and a month nobody has fetched is absent, not zero.

Run:  python3 -m pipeline.mumbai
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .cities import BY_KEY
from .fir import FirRecord
from .mahapolice import MAPPING
from .taxonomy import BY_KEY as HEAD_BY_KEY, CRIME_HEADS

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "data" / "raw" / "live" / "mumbai"
STATIONS_FILE = ROOT / "data" / "raw" / "INDIA_POLICE_STATIONS.geojson"
SITE = ROOT / "site"
OUT = SITE / "mumbai.json"

# The unit the FIR portal publishes under, which the MHA station master happens
# to spell identically. That coincidence is what makes the join possible.
UNIT = "BRIHAN MUMBAI CITY"

# Spellings of one station that `normalise()` cannot reduce to each other.
# Every entry was checked by hand; anything not here stays unmatched rather
# than being guessed at.
ALIASES = {
    # The portal's abbreviations, which the MHA master writes in full. Each is
    # a road named after a person, which is why the two spellings look
    # unrelated. Verified against the MHA list.
    "D.B.MARG": "DR. DADASAHEB BHADKAMKAR MARG",
    "LT MARG": "LOKMANY TILAK MARG",
    "V.P.ROAD": "VALLABHBHAI PATEL ROAD",
    # The commissionerate directory's English spellings (the label on each
    # station page's map embed), written as the portal writes them. Verified
    # by reading the page: its address names the same place, and the office
    # on its map sits within 1.4 km of the MHA point of the same name, except
    # where the note says the MHA point is the one that is off.
    "AAREY ROAD": "AREY SUB PS",           # no MHA point; the one Aarey, in Aarey Colony, Goregaon (E)
    "BKC": "BANDRA-KURLA COMPLEX",         # 1.06 km
    "BORIVALI": "BORIWALI",                # 0.02 km; the W/V transliteration split
    "CHARKOP": "CHARCOP",                  # 0.00 km
    "KANDIVALI": "KANDIVALI (WEST)",       # 1.35 km; the address says Kandivali (West).
                                           # Kandivali (East) is Samta Nagar, its own page.
    "KASTURBA ROAD": "KASTURBA SUB PS",    # 0.04 km
    "MATA RAMABAI AMBEDKAR MARG": "M R A MARG",  # no MHA point; the roster's एम.आर.ए.मार्ग
    "MHB": "MHB COLONY",                   # 0.01 km
    "MULUND": "MULUND (WEST)",             # 0.80 km; the address says Mulund (West).
                                           # Mulund (East) is Navghar, its own page.
    "RAFI AHMED KIDWAI MARG": "R.A KIDWAI MARG",  # 1.15 km
    "SAHAR AIRPORT": "SAHAR",              # MHA point is 4.45 km off, at Jogeshwari PS;
                                           # the address is Sahar Airport Road, Andheri (E)
    "SEWREE / DARUKHANA": "SEWRI",         # MHA point is 2.18 km off; the address is
                                           # Reay Road, Darukhana, Sewri 400010
    "VINOBA BHAVE": "VINOBA BHAVE NAGAR",  # 0.14 km
    "WADALA TRUCK TERMINAL": "WADALA TT",  # 0.27 km. Not Wadala: that office is 2.7 km away
}


def normalise(name: str) -> str:
    """Reduce a station name to something joinable across two spellings."""
    text = (name or "").upper().strip()
    text = ALIASES.get(text, text)
    text = re.sub(r"\bPOLICE STATION\b|\bSUB PS\b|\bPS\b", " ", text)
    return re.sub(r"[^A-Z0-9]", "", text)


def load_station_points() -> dict[str, dict]:
    """Mumbai city station points, keyed by normalised name."""
    collection = json.loads(STATIONS_FILE.read_text(encoding="utf-8"))
    points = {}
    for feature in collection["features"]:
        properties = feature["properties"]
        if properties.get("district") != UNIT:
            continue
        points[normalise(properties["ps"])] = {
            "name": properties["ps"].replace("?", "").strip(),
            "lat": properties["latitude"],
            "lon": properties["longitude"],
            "ps_cd": properties["ps_cd"],
        }
    return points


def load_records() -> tuple[list[FirRecord], dict]:
    """Every harvested FIR, with the coverage the harvester recorded."""
    records: list[FirRecord] = []
    for path in sorted(LIVE.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(FirRecord.from_row(
                    json.loads(line), MAPPING, source="mahapolice",
                    state="MAHARASHTRA"))
    checkpoint = LIVE / "_checkpoint.json"
    coverage = (json.loads(checkpoint.read_text(encoding="utf-8"))
                if checkpoint.exists() else {"months": {}})
    return records, coverage


def build() -> dict:
    records, coverage = load_records()
    points = load_station_points()

    # station -> month -> crime_key -> count
    counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    station_display: dict[str, str] = {}
    for record in records:
        if not record.month:
            continue
        key = normalise(record.police_station)
        station_display.setdefault(key, record.police_station.strip())
        counts[key][record.month][record.crime_key] += 1

    months = sorted({m for s in counts.values() for m in s})

    stations, unplaced = [], []
    for key, by_month in sorted(counts.items()):
        point = points.get(key)
        entry = {
            "name": station_display[key],
            "total": sum(sum(c.values()) for c in by_month.values()),
            "months": {m: dict(c) for m, c in sorted(by_month.items())},
        }
        if point:
            entry.update(lat=point["lat"], lon=point["lon"],
                         official_name=point["name"], ps_cd=point["ps_cd"])
            stations.append(entry)
        else:
            unplaced.append(entry)

    # Only months the harvester verified against the portal's own count may be
    # treated as fully covered. The rest are shown as partial, with the
    # shortfall named, because a half-fetched month drawn at full strength is
    # a quiet neighbourhood we invented.
    complete = sorted(m for m, v in coverage["months"].items() if v.get("complete"))
    # Anything present in the data but not verified complete is partial --
    # including a month still being fetched, and including the stray records
    # a neighbouring month's query returns at a date boundary. Treating an
    # unverified month as whole is how a half-fetched city starts looking calm.
    partial = {m: coverage["months"].get(m, {"collected": None, "declared": None})
               for m in months if m not in set(complete)}

    return {
        "city": BY_KEY["mumbai"].name,
        "unit": UNIT,
        "source": {
            "name": "Maharashtra Police — Published FIRs (CCTNS citizen portal)",
            "url": "https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx",
            "acknowledgement": "Contains information published by Maharashtra Police.",
            "terms": "Reproduction permitted with the source prominently acknowledged.",
            "series_starts": "2017-01-01",
        },
        "records": len(records),
        "months": months,
        "months_complete": complete,
        "months_partial": {m: {"collected": v.get("collected"),
                               "declared": v.get("declared"),
                               "in_data": sum(
                                   sum(c.get(m, {}).values())
                                   for c in [s["months"] for s in stations + unplaced])}
                           for m, v in sorted(partial.items())},
        "stations": sorted(stations, key=lambda s: -s["total"]),
        "unplaced": sorted(unplaced, key=lambda s: -s["total"]),
        "heads": [{"key": h.key, "label": h.label, "group": h.group,
                   "severity": h.severity,
                   "withheld": h.withheld} for h in CRIME_HEADS],
        "caveats": caveats(len(records), unplaced, complete, partial),
    }


def caveats(total: int, unplaced: list, complete: list, partial: dict) -> list[dict]:
    """The qualifications that travel with every number on this map."""
    items = [
        {"kind": "geography",
         "text": "An FIR records the police station that registered it, not "
                 "where the offence happened. Maharashtra publishes no station "
                 "jurisdiction boundaries, so each mark is the station's own "
                 "address. It is not a crime scene and not a catchment area."},
        {"kind": "reporting",
         "text": "This maps reported crime. A station people trust, and where "
                 "FIRs get registered readily, will show more crime than one "
                 "that turns complainants away. The error runs one way, so it "
                 "does not average out: a low count can mean a safe area or an "
                 "unresponsive station, and this map cannot tell you which."},
        {"kind": "withheld",
         "text": "Sexual offences and POCSO cases are excluded from every "
                 "public Indian FIR feed under a Supreme Court direction of "
                 "7 September 2016. They are shown as withheld, never as zero. "
                 "A blank there is a statement about the law, not about the "
                 "neighbourhood."},
        {"kind": "law-change",
         "text": "FIRs registered before 1 July 2024 cite the Indian Penal "
                 "Code; later ones cite the Bharatiya Nyaya Sanhita. There is "
                 "no official concordance between the two, so counts either "
                 "side of that date are not strictly comparable."},
    ]
    if unplaced:
        names = ", ".join(s["name"] for s in unplaced)
        count = sum(s["total"] for s in unplaced)
        items.append({
            "kind": "unplaced",
            "text": f"{len(unplaced)} stations carrying {count:,} FIRs are in "
                    f"the FIR feed but not in the MHA station master, so they "
                    f"have no coordinates and are listed rather than drawn: "
                    f"{names}. Their FIRs are counted in the totals."})
    if partial:
        items.append({
            "kind": "coverage",
            "text": f"{len(complete)} months are fetched in full and verified "
                    f"against the portal's own record count. "
                    f"{len(partial)} are partial. A partial month is under-"
                    f"counted, not quiet."})
    return items


def main() -> int:
    payload = build()
    SITE.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    placed = len(payload["stations"])
    print(f"{payload['records']:,} FIRs")
    print(f"{placed} stations placed, {len(payload['unplaced'])} unplaced")
    print(f"months: {', '.join(payload['months']) or 'none'}")
    print(f"complete: {len(payload['months_complete'])}  "
          f"partial: {len(payload['months_partial'])}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
