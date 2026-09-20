"""Attach police stations to thanas: which sit inside, which are nearest.

Answers the question a resident actually asks — "which police station covers
this area, and what else is near me" — from the one thing we genuinely have at
station level: 929 Bihar station points with coordinates.

Two lists per thana, and the distinction matters:

* **Inside** — station points that fall within the polygon. This includes the
  territorial thana itself plus any specialist units physically located there:
  a district's Mahila (women's), SC/ST, Prohibition or Traffic station, and
  railway police posts. Those specialists have their own, usually district-wide,
  jurisdiction, so they are listed with their kind rather than silently counted
  as though they policed this area.
* **Nearest** — the closest station points *outside* the polygon, so a resident
  near an edge sees the station across the boundary. Stations already listed as
  inside are excluded rather than repeated.

Distances are straight-line, computed on a sphere. Nobody travels in a straight
line in Bihar, so these are shown as "about", never as a journey.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from shapely.geometry import Point, shape
from shapely import STRtree

SPINE = Path(__file__).resolve().parent.parent / "data" / "spine"

EARTH_RADIUS_KM = 6371.0
NEAREST_COUNT = 4


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def load_stations() -> list[dict]:
    with (SPINE / "bihar_stations.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["latitude"] = float(row["latitude"])
        row["longitude"] = float(row["longitude"])
    return rows


def attach(features: list[dict]) -> dict[str, dict]:
    """Return thana_id -> {inside: [...], nearest: [...], counts}."""
    stations = load_stations()
    points = [Point(s["longitude"], s["latitude"]) for s in stations]
    tree = STRtree(points)

    result: dict[str, dict] = {}
    for feature in features:
        thana_id = feature["properties"]["thana_id"]
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        centroid = geometry.centroid

        inside = []
        for index in tree.query(geometry):
            if geometry.covers(points[index]):
                station = stations[index]
                inside.append({
                    "name": station["name"],
                    "kind": station["kind"],
                    "km": round(haversine_km(centroid.x, centroid.y,
                                             station["longitude"], station["latitude"]), 1),
                })
        inside.sort(key=lambda s: s["km"])

        inside_keys = {(s["name"], s["km"]) for s in inside}
        nearest = sorted(
            (entry for entry in (
                {"name": s["name"], "kind": s["kind"], "district": s["district"],
                 "km": round(haversine_km(centroid.x, centroid.y,
                                          s["longitude"], s["latitude"]), 1)}
                for s in stations)
             if (entry["name"], entry["km"]) not in inside_keys),
            key=lambda s: s["km"],
        )[:NEAREST_COUNT]

        result[thana_id] = {
            "inside": inside,
            "nearest": nearest,
            "count_inside": len(inside),
            "count_territorial_inside": sum(1 for s in inside if s["kind"] == "territorial"),
            "specialist_kinds": sorted({s["kind"] for s in inside if s["kind"] != "territorial"}),
        }
    return result
