"""City targets: what geography and what crime feed each one actually has.

The project starts with six cities rather than a whole state, because a
consolidated safety map is only worth using where it is dense. They divide
sharply by what data exists, and pretending otherwise would produce a map that
looks uniform while resting on wildly different foundations:

  Delhi      police station jurisdiction polygons, published by Geospatial
             Delhi Limited. The best-mapped city in India for this purpose.
  Bangalore  Karnataka's KGIS publishes station polygons statewide; the
             Bengaluru subset is taken by bounding box because the layer
             carries no city field.
  Bhilwara   Rajasthan's Rajdharaa publishes thana polygons with police
             district, circle and range attached.
  Mumbai     No polygon layer exists for Maharashtra. But Maharashtra runs the
             most open FIR feed in India — every FIR, daily, station-level,
             timestamped — so the crime data is the best available and the
             geography is the weak half. The inverse of everywhere else.
  Gurgaon    Haryana publishes neither polygons nor an open FIR feed.
  Noida      Uttar Pradesh the same.

Station *points* exist for all six, from the all-India MHA station master, so
every city can at least place its stations. Where a polygon layer is missing, a
station point is not a jurisdiction and must not be drawn as one.

Run:  python3 -m pipeline.cities
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from shapely.geometry import box, shape

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CITIES_RAW = RAW / "cities"
SPINE = ROOT / "data" / "spine"

STATIONS_FILE = RAW / "INDIA_POLICE_STATIONS.geojson"


@dataclass(frozen=True)
class City:
    key: str
    name: str
    state: str
    # MHA station-master district labels that make up this city.
    mha_districts: tuple[str, ...]
    # Bounding box (min_lon, min_lat, max_lon, max_lat) for spatial selection.
    bbox: tuple[float, float, float, float]
    boundary_file: str | None = None
    boundary_filter: dict = field(default_factory=dict)
    fir_feed: str = "none"
    notes: str = ""


CITIES: tuple[City, ...] = (
    City("delhi", "Delhi", "DELHI",
         mha_districts=("CENTRAL", "EAST", "NEW DELHI", "NORTH", "NORTH EAST",
                        "NORTH WEST", "SHAHDARA", "SOUTH", "SOUTH EAST",
                        "SOUTH WEST", "WEST", "DWARKA", "ROHINI", "OUTER",
                        "OUTER NORTH", "AIRPORT", "RAILWAYS", "METRO"),
         bbox=(76.83, 28.40, 77.35, 28.89),
         boundary_file="GSDL_DL_Police_Station_Boundaries.geojsonl",
         fir_feed="e-FIR only; no bulk published-FIR listing found",
         notes="Delhi Police publish an annual review; no open station-month series."),
    City("bangalore", "Bengaluru", "KARNATAKA",
         mha_districts=("BANGALORE CITY", "BENGALURU CITY", "BANGALORE",
                        "BENGALURU", "BANGALORE RURAL", "BENGALURU RURAL"),
         bbox=(77.40, 12.78, 77.80, 13.18),
         boundary_file="KGISMAPS_KN_Police_Station_Boundaries.geojsonl",
         fir_feed="Karnataka FIR search, daily, station-level, scrapable",
         notes="OpenCity also publishes Karnataka crime CSVs and a station KML."),
    City("bhilwara", "Bhilwara", "RAJASTHAN",
         mha_districts=("BHILWARA",),
         bbox=(74.20, 25.00, 75.40, 26.00),
         boundary_file="Rajdharaa_RJ_Police_Thana_Boundary.geojsonl",
         boundary_filter={"POLICE_DISTRICT_NAME": "BHILWARA"},
         fir_feed="Rajasthan FIR search exists but is CAPTCHA-gated; out of scope",
         notes="Polygons carry police district, circle and range."),
    City("mumbai", "Mumbai", "MAHARASHTRA",
         mha_districts=("MUMBAI", "MUMBAI CITY", "MUMBAI SUBURBAN",
                        "BRIHAN MUMBAI", "GREATER MUMBAI"),
         bbox=(72.75, 18.87, 73.05, 19.32),
         fir_feed="Maharashtra published FIRs: every FIR, daily, station-level, timestamped",
         notes="Best crime feed in India; no jurisdiction polygons published."),
    City("gurgaon", "Gurugram", "HARYANA",
         mha_districts=("GURGAON", "GURUGRAM"),
         bbox=(76.85, 28.32, 77.20, 28.55),
         fir_feed="none published",
         notes="Neither polygons nor an open FIR feed. RTI is the route."),
    City("noida", "Noida", "UTTAR PRADESH",
         mha_districts=("GAUTAM BUDDHA NAGAR", "GAUTAMBUDH NAGAR", "NOIDA"),
         bbox=(77.28, 28.36, 77.60, 28.65),
         fir_feed="UP e-FIR; no bulk listing found",
         notes="Neither polygons nor an open FIR feed. RTI is the route."),
)

BY_KEY = {c.key: c for c in CITIES}


def load_boundaries(city: City) -> list[dict]:
    """Polygons for one city, or [] where the state publishes none."""
    if not city.boundary_file:
        return []
    path = CITIES_RAW / city.boundary_file
    if not path.exists():
        return []
    features = [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines() if line.strip()]

    if city.boundary_filter:
        wanted = {k: v.upper() for k, v in city.boundary_filter.items()}
        features = [f for f in features
                    if all(str(f["properties"].get(k, "")).upper() == v
                           for k, v in wanted.items())]
        return features

    # No city field on the layer: select by geography instead. Any polygon
    # intersecting the city box counts, so boundary stations are not lost.
    window = box(*city.bbox)
    return [f for f in features if shape(f["geometry"]).intersects(window)]


def load_stations(city: City) -> list[dict]:
    """MHA station points for one city, by district label then by bounding box."""
    collection = json.loads(STATIONS_FILE.read_text(encoding="utf-8"))
    wanted = {d.upper() for d in city.mha_districts}
    by_label, by_box = [], []
    min_lon, min_lat, max_lon, max_lat = city.bbox
    for feature in collection["features"]:
        properties = feature["properties"]
        if (properties.get("district") or "").upper() in wanted:
            by_label.append(feature)
        elif (min_lon <= properties["longitude"] <= max_lon
              and min_lat <= properties["latitude"] <= max_lat):
            by_box.append(feature)
    # District labels are authoritative where they match; the box catches
    # stations whose district is spelled differently.
    return by_label + by_box


def survey() -> list[dict]:
    rows = []
    for city in CITIES:
        boundaries = load_boundaries(city)
        stations = load_stations(city)
        rows.append({
            "key": city.key,
            "city": city.name,
            "state": city.state,
            "polygons": len(boundaries),
            "stations": len(stations),
            "has_boundaries": bool(boundaries),
            "fir_feed": city.fir_feed,
            "notes": city.notes,
        })
    return rows


def main() -> int:
    print(f"{'city':12s} {'state':14s} {'polygons':>9s} {'stations':>9s}  crime feed")
    print("-" * 104)
    for row in survey():
        print(f"{row['city']:12s} {row['state']:14s} {row['polygons']:9d} "
              f"{row['stations']:9d}  {row['fir_feed'][:52]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
