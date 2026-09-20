"""Generate the self-contained map page.

No basemap tiles. Two reasons, and both are deliberate rather than a shortcut.
The artifact sandbox blocks external images outright, so tiles would silently
fail; and a published map of India carries a legal obligation to depict national
boundaries as Survey of India does. Drawing only Bihar's internal thana
jurisdictions avoids depicting a national boundary at all.

Polygons are projected and simplified here rather than in the browser, so the
page ships paths instead of coordinate arrays and stays small enough to inline.

Run:  python3 -m pipeline.build_page
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

WIDTH = 1000.0
PAGE_SIMPLIFY = 0.0025   # degrees; drawing tolerance, not an analytical one
PRECISION = 1


def project(features: list[dict]) -> tuple[list[dict], dict]:
    """Equirectangular projection scaled for Bihar's latitude.

    Bihar spans roughly 24-27.5N, so longitudes are compressed by cos(mean lat).
    At this extent that is visually indistinguishable from a conic projection
    and costs nothing to compute.
    """
    bounds = [180.0, 90.0, -180.0, -90.0]
    geometries = []
    for feature in features:
        geometry = shape(feature["geometry"]).simplify(PAGE_SIMPLIFY, preserve_topology=True)
        if geometry.is_empty:
            geometry = shape(feature["geometry"])
        geometries.append(geometry)
        x0, y0, x1, y1 = geometry.bounds
        bounds = [min(bounds[0], x0), min(bounds[1], y0),
                  max(bounds[2], x1), max(bounds[3], y1)]

    min_lon, min_lat, max_lon, max_lat = bounds
    mean_lat = math.radians((min_lat + max_lat) / 2)
    span_x = (max_lon - min_lon) * math.cos(mean_lat)
    scale = WIDTH / span_x
    height = (max_lat - min_lat) * scale

    def to_xy(lon: float, lat: float) -> tuple[float, float]:
        x = (lon - min_lon) * math.cos(mean_lat) * scale
        y = (max_lat - lat) * scale
        return round(x, PRECISION), round(y, PRECISION)

    def ring_path(coords) -> str:
        points = [to_xy(lon, lat) for lon, lat, *_ in coords]
        deduped = [points[0]]
        for point in points[1:]:
            if point != deduped[-1]:
                deduped.append(point)
        if len(deduped) < 3:
            return ""
        head = f"M{deduped[0][0]} {deduped[0][1]}"
        rest = "".join(f"L{x} {y}" for x, y in deduped[1:])
        return head + rest + "Z"

    out = []
    for feature, geometry in zip(features, geometries):
        polygons = (geometry.geoms if geometry.geom_type == "MultiPolygon" else [geometry])
        path = "".join(
            ring_path(list(polygon.exterior.coords)) for polygon in polygons
            if polygon.exterior
        )
        if not path:
            continue
        properties = feature["properties"]
        out.append({
            "i": properties["id"],
            "n": properties["name"] or "(unnamed)",
            "d": properties["district"],
            "a": 1 if properties["corroborated"] else 0,
            "e": properties.get("evidence") or "",
            "s": properties.get("station") or "",
            # Stations located inside this thana, and the nearest ones to its
            # centre. Compacted to [name, kind, km] triples to keep the page
            # small enough to inline.
            "in": [[x["name"], x["kind"], x["km"]] for x in properties.get("stations_inside", [])],
            "nr": [[x["name"], x["kind"], x["km"]] for x in properties.get("stations_nearest", [])],
            "p": path,
        })
    return out, {"width": round(WIDTH), "height": round(height)}


def build() -> dict:
    collection = json.loads((SITE / "thanas.geojson").read_text(encoding="utf-8"))
    meta = json.loads((SITE / "meta.json").read_text(encoding="utf-8"))
    shapes, viewport = project(collection["features"])

    payload = {
        "viewport": viewport,
        "thanas": shapes,
        "meta": {
            "state": meta["state"],
            "unit": meta["unit"],
            "thanas": meta["thanas"],
            "resolvable": meta["thanas_resolvable"],
            "corroborated": meta["thanas_corroborated"],
            "uncorroborated": meta["thanas_uncorroborated"],
            "caveats": meta["caveats"],
            "categories": [c for c in meta["categories"] if c["key"] != "other"],
            "coverage": meta["coverage"],
            "sources": meta["sources"],
            "availability": meta["availability"],
        },
    }
    out = SITE / "map_data.json"
    out.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"site/map_data.json  {out.stat().st_size / 1e6:.2f} MB  "
          f"{len(shapes)} thanas  viewport {viewport}")
    return payload


def render() -> None:
    """Inline the data into the template, as a standalone page and a fragment.

    Two outputs because they are wrapped differently: `index.html` is a complete
    document for serving from the repo, while `artifact.html` omits the doctype
    and head, which the Artifact publisher supplies itself.
    """
    template = (SITE / "_template.html").read_text(encoding="utf-8")
    data = (SITE / "map_data.json").read_text(encoding="utf-8")
    fragment = template.replace("__DATA__", data)
    (SITE / "artifact.html").write_text(fragment, encoding="utf-8")
    (SITE / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        "</head>\n<body>\n" + fragment + "\n</body>\n</html>\n", encoding="utf-8")
    for name in ("index.html", "artifact.html"):
        print(f"site/{name}  {(SITE / name).stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    build()
    render()
