"""Assemble the static site: geometry, aggregates and the caveats that qualify them.

The map this feeds has no crime data in it yet, and that is the point. Bihar's
FIR repository is not reachable from the environment this was built in, so the
crime layer is wired up and empty, and every thana correctly renders as "no
data" rather than as zero crime.

What it *can* show is real and worth showing: the 896 actual thana jurisdiction
polygons, and which of them we can attach a crime feed to at all. That coverage
layer is a map of our own readiness, and it makes the central Phase 2 problem
visible at a glance — a third of Bihar's thanas have no station we can confidently
resolve a FIR to.

Run:  python3 -m pipeline.build_site
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from shapely.geometry import mapping, shape

from .aggregate import (
    NO_DATA,
    PUBLISHED,
    SUPPRESSED,
    aggregate,
    category_catalogue,
    thana_status,
)
from .resolver import ThanaResolver
from .stations import attach as attach_stations

ROOT = Path(__file__).resolve().parent.parent
SPINE = ROOT / "data" / "spine"
SITE = ROOT / "site"

# Coarser than the analysis geometry: this is for drawing, not measuring.
WEB_SIMPLIFY_DEGREES = 0.0012


# Tiers whose mapping we accept. See pipeline/crosswalk.py for what each means.
ATTACHABLE_TIERS = {"confirmed", "name-over-geometry", "corroborated", "name-only"}


def load_crosswalk() -> dict[str, dict]:
    """thana_id -> the best evidence we have for attaching crime to it."""
    path = SPINE / "station_crosswalk.csv"
    best: dict[str, dict] = {}
    if not path.exists():
        return best
    rank = {"confirmed": 0, "name-over-geometry": 1, "corroborated": 2, "name-only": 3}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            thana_id = row["thana_id"]
            if not thana_id or row["tier"] not in ATTACHABLE_TIERS:
                continue
            current = best.get(thana_id)
            if current is None or rank.get(row["tier"], 9) < rank.get(current["tier"], 9):
                best[thana_id] = row
    return best


def field_availability() -> list[dict]:
    """What the map is asked to show, against what the data can support.

    Stated as data rather than prose so the page cannot quietly display an
    empty panel as though it were a zero. Each entry says what would have to
    happen for the field to become available — see docs/PHASE1-FINDINGS.md and
    research/sources/rti-playbook.md for the routes.
    """
    return [
        {"field": "Police stations nearby", "status": "available",
         "detail": "929 Bihar station points with coordinates, from the MHA station master."},
        {"field": "Number of stations", "status": "available",
         "detail": "Counted per thana, with specialist units listed separately because "
                   "a Mahila or SC/ST station sits inside a thana without policing it."},
        {"field": "Case types", "status": "available",
         "detail": "20 law-neutral crime heads mapped from IPC and BNS sections. Two are "
                   "withheld from every public Indian FIR feed by law."},
        {"field": "Cases registered", "status": "blocked",
         "detail": "Bihar publishes every FIR at scrb.bihar.gov.in, but the host is "
                   "unreachable from this environment. The pipeline is written and waiting; "
                   "see docs/INGESTION.md."},
        {"field": "Cases closed, and when", "status": "not-published",
         "detail": "FIR listings carry no disposal field. Outcomes live in the court system, "
                   "joined by FIR number, and bulk access there is CAPTCHA-gated. Police-side "
                   "disposal is published only at district level, annually."},
        {"field": "Location of each case", "status": "does-not-exist",
         "detail": "No Indian authority publishes geocoded crime incidents. An FIR records "
                   "the police station that registered it, not where the offence happened. "
                   "The thana jurisdiction is the finest honest unit, and any product showing "
                   "street-level pins for India is inventing them."},
        {"field": "Station house officer", "status": "policy-pending",
         "detail": "Obtainable from state police directories, but postings rotate often and a "
                   "stale name beside crime counts is worse than none. Naming an individual "
                   "next to figures driven by population and reporting propensity invites a "
                   "reading the data cannot support."},
    ]


def build() -> dict:
    SITE.mkdir(parents=True, exist_ok=True)
    collection = json.loads((SPINE / "bihar_thana.geojson").read_text(encoding="utf-8"))
    crosswalk = load_crosswalk()

    resolver = ThanaResolver.from_spine()
    thana_ids = [f["properties"]["thana_id"] for f in collection["features"]]
    nearby = attach_stations(collection["features"])

    # No crime records yet: the feed is unreachable from here. The aggregation
    # still runs, so the empty state is the real pipeline's output, not a mock.
    aggregation = aggregate([], resolver, thana_ids, source_name="not yet ingested")

    # Reachability and corroboration are different questions, and conflating
    # them is what produced the earlier, wrong "328 blind spots" figure. A
    # polygon with no MHA station point is still reachable: the crime feed names
    # stations, and the resolver matches those names against polygons directly.
    # What such a polygon lacks is a second, independent witness that it exists.
    features = []
    for feature in collection["features"]:
        properties = feature["properties"]
        thana_id = properties["thana_id"]
        evidence = crosswalk.get(thana_id)
        geometry = shape(feature["geometry"]).simplify(
            WEB_SIMPLIFY_DEGREES, preserve_topology=True)
        if geometry.is_empty or not geometry.is_valid:
            geometry = shape(feature["geometry"])

        features.append({
            "type": "Feature",
            "properties": {
                "id": thana_id,
                "name": properties["name"],
                "district": properties["district"],
                "crime_status": thana_status(thana_id, aggregation),
                # Can the resolver return this polygon from a station name?
                "resolvable": resolver.resolve(
                    properties["name"], properties["district"]).thana_id == thana_id,
                # Does a second source independently confirm a station here?
                "corroborated": bool(evidence),
                "evidence": evidence["tier"] if evidence else None,
                "station": evidence["station_name"] if evidence else None,
                "stations_inside": nearby[thana_id]["inside"],
                "stations_count": nearby[thana_id]["count_inside"],
                "specialist_kinds": nearby[thana_id]["specialist_kinds"],
                "stations_nearest": nearby[thana_id]["nearest"][:3],
            },
            "geometry": mapping(geometry),
        })

    geo_path = SITE / "thanas.geojson"
    geo_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features},
                   separators=(",", ":")), encoding="utf-8")

    corroborated = sum(1 for f in features if f["properties"]["corroborated"])
    resolvable = sum(1 for f in features if f["properties"]["resolvable"])
    meta = {
        "state": "Bihar",
        "unit": "Police station jurisdiction (thana)",
        "thanas": len(features),
        "thanas_resolvable": resolvable,
        "thanas_corroborated": corroborated,
        "thanas_uncorroborated": len(features) - corroborated,
        "crime_data_status": "none ingested",
        "coverage": aggregation.coverage,
        "caveats": aggregation.caveats,
        "categories": category_catalogue(),
        "sources": collection.get("metadata", {}).get("sources", {}),
        "availability": field_availability(),
    }
    (SITE / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"site/thanas.geojson  {geo_path.stat().st_size / 1e6:.2f} MB  "
          f"{len(features)} thanas")
    print(f"site/meta.json       {resolvable}/{len(features)} resolvable, "
          f"{corroborated} corroborated by a station point")
    return meta


if __name__ == "__main__":
    build()
