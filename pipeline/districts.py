"""Build Bihar district polygons by dissolving the thana layer.

We have no district boundary file, but we have 896 thana polygons each tagged
with its police district, so the districts are recoverable by union. That keeps
one geometry lineage for the whole product: if a thana boundary is wrong, the
district containing it is wrong in exactly the same way, rather than the two
layers disagreeing for reasons nobody can trace.

These are **police** districts, which is what NCRB's district tables count by.
They are not always the revenue districts of the same name — Bagaha and
Naugachhia are police districts carved out of West Champaran and Bhagalpur.

Run:  python3 -m pipeline.districts
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
SPINE = ROOT / "data" / "spine"

SIMPLIFY_DEGREES = 0.002


def build() -> dict:
    collection = json.loads((SPINE / "bihar_thana.geojson").read_text(encoding="utf-8"))

    by_district: dict[str, list] = defaultdict(list)
    for feature in collection["features"]:
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        by_district[feature["properties"]["district"]].append(geometry)

    features = []
    for district, geometries in sorted(by_district.items()):
        merged = unary_union(geometries)
        simplified = merged.simplify(SIMPLIFY_DEGREES, preserve_topology=True)
        if not simplified.is_empty and simplified.is_valid:
            merged = simplified
        features.append({
            "type": "Feature",
            "properties": {"district": district, "thanas": len(geometries)},
            "geometry": mapping(merged),
        })

    out = {"type": "FeatureCollection",
           "metadata": {"unit": "police district",
                        "derived_from": "union of bihar_thana.geojson by district",
                        "note": "Police districts, which is what NCRB counts by. "
                                "Bagaha and Naugachhia are police districts without a "
                                "revenue district of the same name."},
           "features": features}
    (SPINE / "bihar_district.geojson").write_text(
        json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"bihar_district.geojson  {len(features)} districts "
          f"from {len(collection['features'])} thanas")
    return out


if __name__ == "__main__":
    build()
