#!/usr/bin/env python3
"""Build the Mumbai station spine: the directory, its join to the FIR feed, and the pincode index.

    python3 scripts/build_mumbai_stations.py

Reads the station pages the crawler saved under data/raw/mumbaipolice/ and
writes three files under data/spine/, the inputs `pipeline/build_locality_page.py`
draws the "search a pincode, see your stations" panel from:

  mumbai_stations.json       one record per station, in the parser's schema
  mumbai_station_join.json   one row per FIR station name saying which directory
                             page it is, with counts by method and the work list
                             of what did not join
  mumbai_pincodes.json       pincode -> ps_ids of the offices addressed in it

Nothing is fetched. The pages, the FIR feed and the MHA station master are all
read from disk, so this can be re-run as often as the parser changes without
the commissionerate's server hearing about it.

Why one script rather than the parser's own main
------------------------------------------------
`python3 -m pipeline.mumbaipolice` writes the records alone. The join needs the
FIR feed's station names and the MHA points beside them, the pincode index
needs the records, and all three files have to come from a single parse so
that a ps_id means the same page in each. Writing them together is what makes
that true.

What is checked before anything is written
------------------------------------------
* **No officer's name, and not the number beside it.** Every station page
  names four people and prints a mobile number beside the Sr. PI's name.
  `parse_station` refuses to return a record that carries either; this script
  repeats the check against the three finished files, whole name (or whole
  number) against whole file, because the files are what ships. It is
  deliberately not a word-by-word check: on six of the 99 pages a single word
  of an officer's name is also part of a street, a garden or a housing society
  in that station's own address or beat list, and a word-level check would
  refuse to write true office data. The tests do the word-level check per
  record on the fixtures; here the rule is the parser's.
* **A near miss that lands on a page already taken.** A `fuzzy` row whose
  directory page an `exact` row also claims is almost certainly the wrong
  station -- the page already has its own FIR name -- and shipping it would
  print that station's phones beside another station's crime. Such rows are
  written as the join module tagged them, listed under
  `fuzzy_colliding_with_exact` in the summary, and printed, because the fix
  belongs in the alias table, not in a second opinion here.

The coverage report it prints counts records that carry a value; the rest are
null with a reason in each record's `missing`, never blank.
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote_plus

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]

from pipeline.mumbai import load_station_points                          # noqa: E402
from pipeline.mumbai_join import (                                       # noqa: E402
    join_directory,
    load_fir_station_names,
    pincode_index,
)
from pipeline.mumbaipolice import (                                      # noqa: E402
    NAME_PLATE,
    OUT as STATIONS_JSON,
    PROFILE_LINK,
    STATIONS_DIR,
    TAG,
    parse_all,
    plate_number,
)

SPINE = STATIONS_JSON.parent
JOIN_JSON = SPINE / "mumbai_station_join.json"
PINCODES_JSON = SPINE / "mumbai_pincodes.json"

# Fields a map needs before a station is useful on it, in the order the
# coverage report prints them. `address` is included because `pincode` is
# read from it, so the two counts explain each other.
COVERAGE_FIELDS = ("name_en", "lat", "lon", "phones", "email", "address",
                   "pincode", "beat_chowkies")

# The directory's embed and the MHA master are two people's idea of where the
# same office is. Within this they agree; beyond it one of them, or the join,
# is wrong, and a reviewer needs to look before the map draws either.
DISAGREE_KM = 1.5

# Everything in the pincode file's top level is a pincode except this key,
# which holds what the index says about itself: the offices with no pincode
# in their address, and why "uncovered" cannot yet be computed. A dict under
# an underscore so a reader iterating pincodes skips it, and so no pincode
# can ever be spelled the same way.
META_KEY = "_meta"

JOIN_NOTE = (
    "One row per distinct registering-station name in the FIR feed. `exact` "
    "and `alias` rows are joined by rule; `fuzzy` rows are near misses offered "
    "for review and must not be trusted until an alias confirms them; `none` "
    "rows have no directory page and no guess. The summary's lists are the work "
    "list for pipeline/mumbai.py's ALIASES table.")


class OfficerNameInOutput(RuntimeError):
    """A name from a station page is in a file about to be written."""


def officer_names(page: str) -> list[str]:
    """What a page calls its officers: the Sr. PI's name plate, the three
    profile links, and the number printed beside the Sr. PI's name. Read only
    to check that the outputs do not contain them."""
    names = [html.unescape(TAG.sub(" ", m)) for m in NAME_PLATE.findall(page)]
    names += [html.unescape(unquote_plus(m)) for m in PROFILE_LINK.findall(page)]
    cleaned = (re.sub(r"\s+", " ", n).strip(" ,") for n in names)
    number = plate_number(page)
    return [n for n in cleaned if len(n) >= 3] + ([number] if number else [])


def check_no_officer_name(outputs: dict[Path, str]) -> int:
    """Raise if any officer named on any saved page is in any output.

    Returns how many names were checked, so the caller can say the check
    ran against something rather than against an empty list.
    """
    checked = 0
    for path in sorted(STATIONS_DIR.glob("ps_*.html")):
        for name in officer_names(path.read_text(encoding="utf-8")):
            checked += 1
            for out, text in outputs.items():
                if name in text:
                    raise OfficerNameInOutput(
                        f"an officer named on {path.name} is in "
                        f"{out.relative_to(ROOT)}; nothing written")
    return checked


def coverage(records: list[dict]) -> dict[str, int]:
    """How many records carry each field. A null, and only a null, is absent."""
    return {field: sum(1 for r in records if r.get(field) is not None)
            for field in COVERAGE_FIELDS}


def summarise(rows: list[dict], records: list[dict], points: dict) -> dict:
    """The counts and the work lists that travel with the join table."""
    claimed_by_rule = {r["directory_ps_id"] for r in rows if r["method"] in ("exact", "alias")}
    joined = {r["directory_ps_id"] for r in rows if r["directory_ps_id"] is not None}
    fuzzy = [r for r in rows if r["method"] == "fuzzy"]
    return {
        "fir_stations": len(rows),
        "directory_stations": len(records),
        "mha_points": len(points),
        "by_method": {m: sum(1 for r in rows if r["method"] == m)
                      for m in ("exact", "alias", "fuzzy", "none")},
        "fir_without_directory": [r["fir_name"] for r in rows if r["method"] == "none"],
        "fuzzy": [{"fir_name": r["fir_name"], "directory_ps_id": r["directory_ps_id"],
                   "directory_name_en": r["directory_name_en"],
                   "similarity": r["similarity"]} for r in fuzzy],
        "fuzzy_colliding_with_exact": [
            r["fir_name"] for r in fuzzy if r["directory_ps_id"] in claimed_by_rule],
        "directory_without_fir": [
            {"ps_id": r["ps_id"], "name_mr": r["name_mr"], "name_en": r["name_en"],
             "embed_place": r["embed_place"]}
            for r in records if r["ps_id"] not in joined],
        "fir_without_mha": [r["fir_name"] for r in rows if r["mha_ps"] is None],
        "coords_disagree_over_km": DISAGREE_KM,
        "coords_disagree": [
            {"fir_name": r["fir_name"], "directory_ps_id": r["directory_ps_id"],
             "mha_ps": r["mha_ps"],
             "distance_km": r["distance_km_between_directory_and_mha"]}
            for r in rows
            if (r["distance_km_between_directory_and_mha"] or 0) > DISAGREE_KM],
    }


def pincode_file(records: list[dict]) -> dict:
    """The flat pincode -> ps_ids map the page builder reads, plus `_meta`."""
    index = pincode_index(records)
    out: dict = dict(index.pop("by_pincode"))
    out[META_KEY] = index
    return out


def report(records: list[dict], summary: dict, pincodes: dict) -> None:
    unrecognised = [r["ps_id"] for r in records if not r["page_recognised"]]
    print(f"{len(records)} station pages parsed"
          + (f", {len(unrecognised)} not recognised as station pages: "
             f"ps={unrecognised}" if unrecognised else ""))
    print(f"coverage (records carrying a value, of {len(records)}):")
    for field, count in coverage(records).items():
        print(f"  {field:15s} {count:3d}")

    by = summary["by_method"]
    print(f"join: {summary['fir_stations']} FIR station names -> "
          f"{by['exact']} exact, {by['alias']} alias, {by['fuzzy']} fuzzy, "
          f"{by['none']} none")
    for row in summary["fuzzy"]:
        flag = "  <- page already claimed by an exact row" \
            if row["fir_name"] in summary["fuzzy_colliding_with_exact"] else ""
        print(f"  fuzzy  {row['fir_name']!r} -> ps={row['directory_ps_id']} "
              f"{row['directory_name_en']!r} ({row['similarity']}){flag}")
    for name in summary["fir_without_directory"]:
        print(f"  none   {name!r}")
    print(f"{len(summary['directory_without_fir'])} directory pages with no FIR name:")
    for entry in summary["directory_without_fir"]:
        print(f"  ps={entry['ps_id']:<4d} {entry['name_mr']!r}  name_en={entry['name_en']!r}"
              f"  embed={entry['embed_place']!r}")
    print(f"{len(summary['fir_without_mha'])} FIR names with no MHA point: "
          f"{summary['fir_without_mha']}")
    print(f"{len(summary['coords_disagree'])} stations where the directory and MHA "
          f"disagree by more than {DISAGREE_KM} km:")
    for entry in summary["coords_disagree"]:
        print(f"  {entry['fir_name']:22s} ps={entry['directory_ps_id']:<4d} "
              f"{entry['distance_km']:6.2f} km")

    without = pincodes[META_KEY]["without_pincode"]
    print(f"{len(pincodes) - 1} pincodes indexed; {len(without)} offices without one: "
          f"ps={without}")


def main() -> int:
    records = parse_all()
    if not records:
        print(f"no station pages under {STATIONS_DIR.relative_to(ROOT)}; "
              f"run scripts/crawl_mumbaipolice_stations.py first")
        return 1
    points = load_station_points()
    rows = join_directory(records, load_fir_station_names(), points)
    summary = summarise(rows, records, points)
    pincodes = pincode_file(records)

    outputs = {
        STATIONS_JSON: records,
        JOIN_JSON: {"note": JOIN_NOTE, "summary": summary, "rows": rows},
        PINCODES_JSON: pincodes,
    }
    texts = {path: json.dumps(payload, ensure_ascii=False, indent=1)
             for path, payload in outputs.items()}
    checked = check_no_officer_name(texts)

    SPINE.mkdir(parents=True, exist_ok=True)
    for path, text in texts.items():
        path.write_text(text + "\n", encoding="utf-8")

    report(records, summary, pincodes)
    print(f"{checked} officer names checked against the outputs; none present")
    for path in texts:
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
