"""Build the Bihar geography spine: the map units a crime layer attaches to.

Two public sources, neither of which was built to be joined to the other:

  * **MHA police station points** — 929 Bihar stations with a national `ps_cd`,
    a district name and coordinates. Tells us which stations exist.
  * **i-Bhugoal thana boundaries** — 896 Bihar police station jurisdiction
    polygons with their own `PS_Code` and district names. Tells us where each
    station's jurisdiction is.

The codes do not correspond: the points carry the MHA/NCRB alphabetical series
(Bihar = 5) and the polygons carry the Census series (Bihar = 10), and the
per-station codes share no scheme at all. There is no published crosswalk. So
the join is spatial — a station point is matched to the polygon that contains
it — with name agreement used only as corroboration, never as the join key.

Three things about Indian police geography make a naive join wrong, and each is
handled explicitly here rather than silently:

1. **Specialist stations overlap territorial ones.** A district's Mahila
   (women's), SC/ST and Prohibition stations sit physically inside some
   territorial thana but have their own, usually district-wide, jurisdiction.
   Point-in-polygon places them inside a thana they do not govern. They are
   classified out of the territorial spine rather than mapped to it.
2. **Railway police overlay everything.** Bihar's four railway police districts
   have jurisdiction over railway land across the state, not a contiguous area.
3. **District names disagree by transliteration and by convention.** The point
   file names several districts after their headquarters town (Motihari,
   Bettiah) where the polygons use the official district name (East Champaran,
   West Champaran). These are resolved through an explicit, auditable alias
   table, never by fuzzy matching — a wrong district silently moves crime from
   one part of the state to another.

Run:  python3 -m pipeline.geography
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from shapely import STRtree
from shapely.geometry import Point, mapping, shape

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SPINE = ROOT / "data" / "spine"

POINTS_FILE = RAW / "INDIA_POLICE_STATIONS.geojson"
THANA_FILE = RAW / "Bhugoal_BH_Police_Thana_Boundaries.geojsonl"

STATE = "BIHAR"

# Provenance travels with the data. A crime map that cannot say where its
# geography came from cannot be audited, and an unauditable crime map is a
# rumour with a projection.
SOURCES = {
    "stations": {
        "name": "MHA police station master (point locations)",
        "url": "https://raw.githubusercontent.com/yashveeeeeeer/india-geodata/"
               "main/data/police/stations/INDIA_POLICE_STATIONS.geojson",
        "attribution": "Ministry of Home Affairs, via the india-geodata mirror",
        "licence": "unstated upstream; mirror asserts CC0-1.0",
    },
    "thanas": {
        "name": "Bihar police thana jurisdiction boundaries",
        "url": "https://github.com/ramSeraph/indian_admin_boundaries/releases/"
               "download/police/Bhugoal_BH_Police_Thana_Boundaries.geojsonl.7z",
        "attribution": "i-Bhugoal (Government of Bihar), via datameet/ramSeraph",
        "licence": "CC0-1.0, attribute datameet and the original government source",
    },
}

# Station-name patterns that mark a unit as something other than a territorial
# thana. Order matters: the first match wins.
STATION_KINDS: list[tuple[str, str]] = [
    ("mahila", r"\bMAHILA\b|\bWOMEN\b"),
    ("sc_st", r"SC\s*/?\s*ST\b|\bSCST\b"),
    ("prohibition", r"PROHIBITION|MADHNISHEDH|MADHNISEDH"),
    ("traffic", r"\bTRAFFIC\b"),
    ("cyber", r"\bCYBER\b"),
    ("railway", r"\bGRP\b|\bRAILWAY\b|\bRLY\b"),
]

# District aliases, point-file spelling -> polygon-file spelling. Explicit and
# reviewable by design; see the module docstring.
DISTRICT_ALIASES = {
    "BETIAH": "WEST CHAMPARAN",        # Bettiah is the HQ of West Champaran
    "MOTHIHARI": "EAST CHAMPARAN",     # Motihari is the HQ of East Champaran
    "BHABHUA": "KAIMUR (BHABUA)",
    "MUJAFFARPUR": "MUZAFFARPUR",
    "PURNEA": "PURNIA",
    "LAKHI SARAI": "LAKHISARAI",
    "NAUGHACHHIA": "NAUGACHHIA",
}

# Railway police districts have no contiguous territory; they are excluded from
# the territorial spine and reported separately.
RAILWAY_DISTRICTS = {"RLY PATNA", "RLY KATIHAR", "RLY JAMALPUR", "RLY MUJAFFARPUR"}

NAME_MATCH_THRESHOLD = 0.82


def normalise_name(value: str | None) -> str:
    """Fold a station or district name to a comparable form.

    Indian place names arrive transliterated inconsistently across systems
    (MEHANDIA / MEHANDIYA, NARPATGANJ / NARPATAGANJ). This strips the noise that
    differs without changing which place is meant. It is used only to *score*
    agreement between two records already joined spatially — never to join them.
    """
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    text = text.upper()
    text = re.sub(r"\b(P\.?S\.?|O\.?P\.?|THANA|POLICE STATION|OUTPOST)\b", " ", text)
    text = re.sub(r"[^A-Z0-9]+", "", text)
    # Collapse the vowel and consonant pairs that transliteration varies on.
    for a, b in (("AA", "A"), ("EE", "I"), ("OO", "U"), ("Y", "I"),
                 ("W", "V"), ("Z", "J"), ("KH", "K"), ("GH", "G"), ("PH", "F")):
        text = text.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", text)


def name_similarity(left: str | None, right: str | None) -> float:
    a, b = normalise_name(left), normalise_name(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def classify_station(name: str | None, district: str | None) -> str:
    """Return the kind of policing unit: territorial, or a named speciality."""
    if (district or "").upper() in RAILWAY_DISTRICTS:
        return "railway"
    haystack = (name or "").upper()
    for kind, pattern in STATION_KINDS:
        if re.search(pattern, haystack):
            return kind
    return "territorial"


def canonical_district(name: str | None) -> str:
    key = re.sub(r"\s+", " ", (name or "").strip().upper())
    return DISTRICT_ALIASES.get(key, key)


@dataclass
class Spine:
    """The built geography, plus everything that went wrong building it."""

    thanas: list[dict] = field(default_factory=list)
    stations: list[dict] = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)


def load_thanas() -> list[dict]:
    features = []
    for line in THANA_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            features.append(json.loads(line))
    return features


def load_stations(state: str = STATE) -> list[dict]:
    collection = json.loads(POINTS_FILE.read_text(encoding="utf-8"))
    return [f for f in collection["features"]
            if (f["properties"].get("state") or "").upper() == state]


def build_spine() -> Spine:
    thana_features = load_thanas()
    station_features = load_stations()

    geometries, repaired = [], 0
    for feature in thana_features:
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            # buffer(0) resolves self-intersections without moving the boundary
            # meaningfully. Counted, because a silent repair is a silent change.
            geometry = geometry.buffer(0)
            repaired += 1
        geometries.append(geometry)

    tree = STRtree(geometries)

    thanas = []
    for index, feature in enumerate(thana_features):
        properties = feature["properties"]
        thanas.append({
            "thana_id": f"BH-{properties['PS_Code']}",
            "ps_code_bhugoal": properties["PS_Code"],
            "name": (properties.get("PS_NAME") or "").strip(),
            "district": canonical_district(properties.get("DIST_NAME")),
            "district_raw": (properties.get("DIST_NAME") or "").strip(),
            "state": STATE,
            "area_sq_deg": properties.get("Shape_Area"),
            "_index": index,
            "stations": [],
        })

    stations, unmatched, ambiguous = [], [], 0
    for feature in station_features:
        properties = feature["properties"]
        kind = classify_station(properties.get("ps"), properties.get("district"))
        point = Point(properties["longitude"], properties["latitude"])

        containing = [i for i in tree.query(point) if geometries[i].covers(point)]
        if len(containing) > 1:
            ambiguous += 1
            # Prefer the candidate whose name agrees; these are nested or
            # overlapping polygons, so containment alone cannot decide.
            containing.sort(
                key=lambda i: name_similarity(properties.get("ps"), thanas[i]["name"]),
                reverse=True,
            )

        record = {
            "station_id": f"BH-PS-{properties['ps_cd']}",
            "ps_cd_mha": properties["ps_cd"],
            "name": (properties.get("ps") or "").strip(),
            "district": canonical_district(properties.get("district")),
            "district_raw": (properties.get("district") or "").strip(),
            "kind": kind,
            "latitude": properties["latitude"],
            "longitude": properties["longitude"],
            "thana_id": None,
            "match_method": "none",
            "name_agreement": 0.0,
        }

        if containing:
            thana = thanas[containing[0]]
            similarity = name_similarity(record["name"], thana["name"])
            record["name_agreement"] = round(similarity, 3)
            if kind == "territorial":
                record["thana_id"] = thana["thana_id"]
                record["match_method"] = (
                    "spatial+name" if similarity >= NAME_MATCH_THRESHOLD else "spatial-only"
                )
                thana["stations"].append(record["station_id"])
            else:
                # A specialist unit sits inside this polygon but does not police
                # it. Record where it physically is, and refuse the mapping.
                record["match_method"] = f"located-in-{thana['thana_id']}-not-mapped"
        else:
            unmatched.append(record["name"])

        stations.append(record)

    territorial = [s for s in stations if s["kind"] == "territorial"]
    mapped = [s for s in territorial if s["thana_id"]]
    corroborated = [s for s in mapped if s["match_method"] == "spatial+name"]
    empty_thanas = [t for t in thanas if not t["stations"]]

    diagnostics = {
        "thana_polygons": len(thanas),
        "thana_polygons_repaired": repaired,
        "station_points": len(stations),
        "stations_by_kind": {
            kind: sum(1 for s in stations if s["kind"] == kind)
            for kind in sorted({s["kind"] for s in stations})
        },
        "territorial_stations": len(territorial),
        "territorial_mapped_to_a_thana": len(mapped),
        "mapped_with_name_agreement": len(corroborated),
        "mapped_on_geometry_alone": len(mapped) - len(corroborated),
        "stations_outside_every_polygon": len(unmatched),
        "stations_outside_examples": unmatched[:10],
        "ambiguous_containment": ambiguous,
        "thanas_with_no_station_point": len(empty_thanas),
        "districts_in_thanas": len({t["district"] for t in thanas}),
        "districts_in_stations": len({s["district"] for s in stations}),
        "district_alias_misses": sorted(
            {s["district"] for s in stations if s["kind"] == "territorial"}
            - {t["district"] for t in thanas}
        ),
    }

    for thana in thanas:
        thana.pop("_index")

    return Spine(thanas=thanas, stations=stations, diagnostics=diagnostics)


def write_outputs(spine: Spine, simplify_tolerance: float = 0.0005) -> None:
    SPINE.mkdir(parents=True, exist_ok=True)
    thana_features = load_thanas()

    def collection(tolerance: float | None) -> dict:
        features = []
        for record, source in zip(spine.thanas, thana_features):
            geometry = shape(source["geometry"])
            if not geometry.is_valid:
                geometry = geometry.buffer(0)
            if tolerance:
                simplified = geometry.simplify(tolerance, preserve_topology=True)
                # Never let simplification empty or break a jurisdiction.
                if not simplified.is_empty and simplified.is_valid:
                    geometry = simplified
            properties = {k: v for k, v in record.items() if k != "stations"}
            properties["station_count"] = len(record["stations"])
            features.append({"type": "Feature", "properties": properties,
                             "geometry": mapping(geometry)})
        return {
            "type": "FeatureCollection",
            "metadata": {"state": STATE, "unit": "police station jurisdiction (thana)",
                         "sources": SOURCES,
                         "simplify_tolerance_degrees": tolerance or 0},
            "features": features,
        }

    full = SPINE / "bihar_thana.geojson"
    web = SPINE / "bihar_thana.simplified.geojson"
    full.write_text(json.dumps(collection(None), ensure_ascii=False), encoding="utf-8")
    web.write_text(json.dumps(collection(simplify_tolerance), ensure_ascii=False), encoding="utf-8")

    with (SPINE / "bihar_stations.csv").open("w", newline="", encoding="utf-8") as handle:
        columns = ["station_id", "ps_cd_mha", "name", "district", "district_raw", "kind",
                   "latitude", "longitude", "thana_id", "match_method", "name_agreement"]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(spine.stations)

    (SPINE / "build_report.json").write_text(
        json.dumps({"sources": SOURCES, "diagnostics": spine.diagnostics}, indent=2),
        encoding="utf-8")

    print(f"wrote {full.name} ({full.stat().st_size / 1e6:.1f} MB)")
    print(f"wrote {web.name} ({web.stat().st_size / 1e6:.1f} MB)")
    print(f"wrote bihar_stations.csv ({len(spine.stations)} rows)")


def main() -> int:
    spine = build_spine()
    write_outputs(spine)
    print("\n--- build diagnostics ---")
    for key, value in spine.diagnostics.items():
        print(f"{key:34s} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
