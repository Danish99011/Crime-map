"""Build the station crosswalk the crime feed joins through, with honest tiers.

The crime feed identifies a station by **name and district**. The map unit is a
**thana polygon**. This module builds the correspondence between them and grades
each row by how much evidence supports it.

**There is no ground truth here.** We have two witnesses, and both lie in
characteristic ways:

  * *Geometry* — does the station's point fall inside this polygon? About 3% of
    the MHA coordinates are plainly wrong (a Begusarai station landing in
    Nalanda, 80km away), and large rural "Mufassil" thanas and town outposts
    swallow points belonging to their neighbours.
  * *Name* — does the station name match a polygon in the same district? Indian
    station names are transliterated inconsistently (DEVKUND / DEOKUND,
    DHORAIYA / DHURAIYA), and SADAR, NAGAR and MUFASSIL recur across districts.

Three rules combine them, each stated so it can be argued with:

1. **Where they agree, accept.** (`confirmed`)
2. **Where they disagree and the name is a strong match, the name wins.**
   (`name-over-geometry`) Geometry is the demonstrably unreliable witness, and
   where a same-named polygon exists in the right district, that is the station:
   Balia's point sitting inside Mufassil says the coordinate is wrong, not that
   Balia is Mufassil.
3. **Where the name is too weak to accept alone but geometry agrees with it,
   accept.** (`corroborated`) Two weak signals pointing the same way are one
   strong signal; this is what catches the transliteration variants.

Everything else goes to `review_queue.csv` with a proposal and its evidence, and
is **not** mapped. A confident wrong join does not look like a bug on a crime
map; it looks like a dangerous neighbourhood.

Run:  python3 -m pipeline.crosswalk
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from .geography import canonical_district, normalise_name
from .resolver import ACCEPT, ThanaResolver

SPINE = Path(__file__).resolve().parent.parent / "data" / "spine"

# A name this similar, when geometry independently agrees, is accepted even
# though it falls below the resolver's standalone threshold.
CORROBORATE_MIN = 0.70
# A name match this strong overrides a disagreeing point.
NAME_WINS_MIN = 0.90

CONFIRMED = "confirmed"                    # name and geometry agree
NAME_OVER_GEOMETRY = "name-over-geometry"  # they disagree; the name is strong
CORROBORATED = "corroborated"              # weak name, but geometry agrees
NAME_ONLY = "name-only"                    # name resolves; no usable point
NEEDS_REVIEW = "needs-review"              # not enough evidence to commit

MAPPABLE = {CONFIRMED, NAME_OVER_GEOMETRY, CORROBORATED, NAME_ONLY}


def similarity(left: str | None, right: str | None) -> float:
    a, b = normalise_name(left), normalise_name(right)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def grade(station: dict, thanas: dict, resolver: ThanaResolver) -> dict:
    """Decide where one station maps, and say on what evidence."""
    by_geometry = station["thana_id"] or None
    result = resolver.resolve(station["name"], station["district"])
    by_name = result.thana_id

    geometry_name = thanas[by_geometry]["name"] if by_geometry else None
    geometry_similarity = similarity(station["name"], geometry_name)

    if by_name and by_geometry and by_name == by_geometry:
        tier, thana_id, rule = CONFIRMED, by_name, "name and geometry agree"
    elif by_name and by_geometry and result.confidence >= NAME_WINS_MIN:
        tier, thana_id = NAME_OVER_GEOMETRY, by_name
        rule = (f"name matched {thanas[by_name]['name']!r} at {result.confidence}; "
                f"point fell in {geometry_name!r}, which is the unreliable witness")
    elif by_name and not by_geometry:
        tier, thana_id, rule = NAME_ONLY, by_name, "no usable point; unambiguous name match"
    elif by_geometry and geometry_similarity >= CORROBORATE_MIN:
        tier, thana_id = CORROBORATED, by_geometry
        rule = (f"name {station['name']!r} ~ {geometry_name!r} at "
                f"{geometry_similarity:.2f}, below the {ACCEPT} threshold but the "
                f"point falls inside it")
    else:
        tier, thana_id = NEEDS_REVIEW, None
        rule = ("name too weak to accept and geometry does not corroborate it"
                if by_geometry else "neither name nor geometry places this station")

    return {
        "station_name": station["name"],
        "district": station["district"],
        "ps_cd_mha": station["ps_cd_mha"],
        "thana_id": thana_id or "",
        "thana_name": thanas[thana_id]["name"] if thana_id else "",
        "tier": tier,
        "mappable": tier in MAPPABLE,
        "rule": rule,
        "by_name": by_name or "",
        "by_name_confidence": result.confidence,
        "by_geometry": by_geometry or "",
        "by_geometry_name": geometry_name or "",
        "by_geometry_similarity": round(geometry_similarity, 3),
        "proposal": (by_geometry or by_name or "") if tier == NEEDS_REVIEW else "",
    }


def build_crosswalk() -> tuple[list[dict], dict]:
    # Grade from first principles plus human overrides only. Reading back the
    # rule-made aliases this module writes would make its own grades depend on
    # how many times it had been run.
    resolver = ThanaResolver.from_spine(human_aliases_only=True)
    thanas = {
        f["properties"]["thana_id"]: f["properties"]
        for f in json.loads((SPINE / "bihar_thana.geojson").read_text(encoding="utf-8"))["features"]
    }
    with (SPINE / "bihar_stations.csv").open(encoding="utf-8") as handle:
        stations = [s for s in csv.DictReader(handle) if s["kind"] == "territorial"]

    rows = [grade(station, thanas, resolver) for station in stations]

    tiers = Counter(r["tier"] for r in rows)
    reached = {r["thana_id"] for r in rows if r["mappable"] and r["thana_id"]}

    # Reachability is a property of the polygons, not of the station list: a
    # thana with no MHA point is still resolvable if the feed names it.
    unreachable = [
        thana_id for thana_id, thana in thanas.items()
        if resolver.resolve(thana["name"], thana["district"]).thana_id != thana_id
    ]

    diagnostics = {
        "territorial_stations": len(rows),
        "tiers": dict(tiers),
        "mappable_stations": sum(1 for r in rows if r["mappable"]),
        "needs_review": tiers[NEEDS_REVIEW],
        "thana_polygons": len(thanas),
        "thanas_reached_by_a_station": len(reached),
        "thanas_not_reached_by_a_station": len(thanas) - len(reached),
        "thanas_unresolvable_by_name": len(unreachable),
        "unresolvable_examples": [thanas[t]["name"] for t in unreachable[:5]],
        "concordance_where_both_witnesses_spoke": round(
            tiers[CONFIRMED] / max(tiers[CONFIRMED] + tiers[NAME_OVER_GEOMETRY], 1), 4),
    }
    return rows, diagnostics


def write_aliases(rows: list[dict]) -> int:
    """Record every accepted mapping the plain name match would not have made.

    These are the rules doing work beyond the resolver's own threshold, written
    out so that each one can be inspected, argued with and overridden by hand.
    """
    interesting = [r for r in rows if r["tier"] in (NAME_OVER_GEOMETRY, CORROBORATED)]
    path = SPINE / "station_aliases.csv"

    existing: list[dict] = []
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            existing = [r for r in csv.DictReader(handle)
                        if (r.get("confirmed_by") or "").strip()
                        and not (r.get("confirmed_by") or "").startswith("rule:")]

    columns = ["district", "station_name", "thana_id", "confirmed_by", "note"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        # Hand-confirmed rows come first and are never overwritten by a rule.
        writer.writerows(existing)
        human = {(canonical_district(r["district"]), normalise_name(r["station_name"]))
                 for r in existing}
        for row in interesting:
            key = (canonical_district(row["district"]), normalise_name(row["station_name"]))
            if key in human:
                continue
            writer.writerow({
                "district": row["district"],
                "station_name": row["station_name"],
                "thana_id": row["thana_id"],
                "confirmed_by": f"rule:{row['tier']}",
                "note": row["rule"],
            })
    return len(interesting)


def main() -> int:
    rows, diagnostics = build_crosswalk()
    SPINE.mkdir(parents=True, exist_ok=True)

    columns = list(rows[0])
    with (SPINE / "station_crosswalk.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    review = [r for r in rows if r["tier"] == NEEDS_REVIEW]
    with (SPINE / "review_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(review)

    aliases = write_aliases(rows)
    (SPINE / "crosswalk_report.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8")

    print(f"station_crosswalk.csv  {len(rows)} rows")
    print(f"station_aliases.csv    {aliases} rule-accepted mappings")
    print(f"review_queue.csv       {len(review)} rows still needing a human\n")
    for key, value in diagnostics.items():
        print(f"{key:40s} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
