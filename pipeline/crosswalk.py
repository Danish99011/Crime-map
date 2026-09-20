"""Build the station crosswalk the crime feed joins through, with honest tiers.

The crime feed identifies a station by **name and district**. The map unit is a
**thana polygon**. This module builds the correspondence between them and,
crucially, grades each row by how much evidence supports it.

**There is no ground truth here, and pretending otherwise would be the most
dangerous thing this pipeline could do.** We have two independent and separately
unreliable witnesses:

  * *Geometry* — does the station's point fall inside this polygon? Unreliable
    because roughly 3% of the MHA coordinates are plainly wrong (a Begusarai
    station landing in Nalanda, 80km away), and because large rural "Mufassil"
    thanas swallow points belonging to smaller neighbours.
  * *Name* — does the station name match this polygon's name within the same
    district? Unreliable because Indian station names are transliterated
    inconsistently, and because SADAR, NAGAR and MUFASSIL recur across districts.

Where both witnesses agree, the row is `confirmed`. Where only one speaks, the
row is usable but marked. Where they actively disagree, the row goes to a review
queue and **not** to the map: on a crime map a confident wrong join does not
look like a bug, it looks like a dangerous neighbourhood.

Run:  python3 -m pipeline.crosswalk
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from .resolver import ThanaResolver

SPINE = Path(__file__).resolve().parent.parent / "data" / "spine"

# Evidence tiers, best first. The map renders CONFIRMED and NAME_ONLY;
# everything else is held back.
CONFIRMED = "confirmed"          # name and geometry agree
NAME_ONLY = "name-only"          # no usable point, but an unambiguous name match
GEOMETRY_ONLY = "geometry-only"  # point lands here, name does not corroborate
CONFLICT = "conflict"            # name says one thana, geometry says another
UNRESOLVED = "unresolved"        # neither witness commits

MAPPABLE = {CONFIRMED, NAME_ONLY}


def build_crosswalk() -> tuple[list[dict], dict]:
    resolver = ThanaResolver.from_spine()
    thanas = {
        f["properties"]["thana_id"]: f["properties"]
        for f in json.loads((SPINE / "bihar_thana.geojson").read_text(encoding="utf-8"))["features"]
    }
    with (SPINE / "bihar_stations.csv").open(encoding="utf-8") as handle:
        stations = [s for s in csv.DictReader(handle) if s["kind"] == "territorial"]

    rows = []
    for station in stations:
        by_geometry = station["thana_id"] or None
        result = resolver.resolve(station["name"], station["district"])
        by_name = result.thana_id

        if by_name and by_geometry:
            tier = CONFIRMED if by_name == by_geometry else CONFLICT
            thana_id = by_name if tier == CONFIRMED else None
        elif by_name:
            tier, thana_id = NAME_ONLY, by_name
        elif by_geometry:
            tier, thana_id = GEOMETRY_ONLY, by_geometry
        else:
            tier, thana_id = UNRESOLVED, None

        rows.append({
            "station_name": station["name"],
            "district": station["district"],
            "ps_cd_mha": station["ps_cd_mha"],
            "thana_id": thana_id or "",
            "thana_name": thanas[thana_id]["name"] if thana_id else "",
            "tier": tier,
            "mappable": tier in MAPPABLE,
            "by_name": by_name or "",
            "by_geometry": by_geometry or "",
            "name_method": result.method,
            "name_confidence": result.confidence,
        })

    tiers = Counter(r["tier"] for r in rows)
    covered = {r["thana_id"] for r in rows if r["mappable"] and r["thana_id"]}
    diagnostics = {
        "territorial_stations": len(rows),
        "tiers": dict(tiers),
        "mappable_stations": sum(1 for r in rows if r["mappable"]),
        "thana_polygons": len(thanas),
        "thanas_reached_by_a_mappable_station": len(covered),
        "thanas_with_no_mappable_station": len(thanas) - len(covered),
        "concordance_where_both_witnesses_spoke": (
            round(tiers[CONFIRMED] / max(tiers[CONFIRMED] + tiers[CONFLICT], 1), 4)
        ),
    }
    return rows, diagnostics


def main() -> int:
    rows, diagnostics = build_crosswalk()
    SPINE.mkdir(parents=True, exist_ok=True)

    columns = list(rows[0])
    with (SPINE / "station_crosswalk.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    review = [r for r in rows if r["tier"] in (CONFLICT, GEOMETRY_ONLY, UNRESOLVED)]
    with (SPINE / "review_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(review)

    (SPINE / "crosswalk_report.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8")

    print(f"station_crosswalk.csv  {len(rows)} rows")
    print(f"review_queue.csv       {len(review)} rows needing a human\n")
    for key, value in diagnostics.items():
        print(f"{key:44s} {value}")

    print("\nWhat this means for the map:")
    mappable = diagnostics["mappable_stations"]
    print(f"  {mappable} of {diagnostics['territorial_stations']} territorial stations can be "
          f"placed ({mappable / diagnostics['territorial_stations']:.1%})")
    print(f"  {diagnostics['thanas_with_no_mappable_station']} of "
          f"{diagnostics['thana_polygons']} thana polygons have no station we can attach crime to")
    print("  Those polygons must render as 'no data', never as zero crime.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
