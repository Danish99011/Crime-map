"""Join Mumbai's three station lists, and answer "which station, from here".

Mumbai has three lists of police stations that were never meant to line up:

* The **FIR feed** (`data/raw/live/mumbai/*.jsonl`) names the registering
  station in the CCTNS portal's spelling -- "NAGPADA", "D.B.MARG",
  "CHUNABHATTI POLICE STATION" -- 96 distinct names so far.
* The **MHA station master** (`INDIA_POLICE_STATIONS.geojson`) has one point per
  station in the Ministry's spelling, 90 for Brihan Mumbai. `pipeline/mumbai.py`
  joins the FIR names to these and places the counts on them.
* The **commissionerate's own directory** (`mumbaipolice.gov.in/policestation`)
  has 99 pages with what a resident in trouble actually needs: office telephone
  numbers, email, beat chowkies and the office address with its pincode. Its
  names are Marathi in the roster and English only inside a map embed.

This module joins the directory to the other two and builds the two lookups
behind the map's "search a pincode, see your stations" panel. It takes
directory records in the shared station schema (the parser's output) and never
reads the station pages itself.

What a join here may and may not do
-----------------------------------
* Spelling is reduced with the **same** `normalise()` and `ALIASES` as
  `pipeline/mumbai.py`, so the name that places an FIR on the map is the name
  that finds its directory page. Two normalisers would drift, and a station
  would then show crime with no phone number, or the reverse.
* A page whose embed never names the station (the label is "Urban hotel", a
  street address, or there is no label) has no English name to join on. For
  those, and only those, `ROSTER_NAMES_EN` says by hand what the roster's
  Marathi name is in the portal's spelling. Each entry was checked against the
  page's address and the MHA point; the check is written beside it.
* A near miss (difflib ratio at or above `FUZZY_THRESHOLD` after normalising)
  is offered but tagged `fuzzy`, so a reviewer sees it before it ships. It is
  never promoted to `exact`, because a wrong join here prints one station's
  phone number beside another station's crime. Two near misses are refused
  outright: a page a rule has already given to another FIR name ("WADALA TT"
  is 0.86 like "Wadala", and Wadala's page belongs to "WADALA"), and a name
  that differs in a compass word ("CYBER ... EAST REGION" is 0.93 like
  "... WEST REGION", and they are two stations).
* Nothing is guessed for a name no rule reaches. `method` is `none`, the
  identifiers are null, and the list of such rows is the work list for the
  alias table, not a failure to hide.

Pincodes
--------
A station's address carries exactly one pincode -- the office's own. Its
jurisdiction spans several, and a pincode routinely spans several stations
(research/sources/geospatial-boundaries.md, entry 18). So `pincode_index`
answers "which station offices sit *in* this pincode" and nothing more. A
pincode absent from it is not a pincode without police; it is one this index
cannot resolve by address, and the result says so instead of returning an
empty list that a map would render as nothing nearby.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from .mumbai import ALIASES, LIVE, normalise
from .stations import haversine_km

# Below this a near miss is noise; at or above it, it earns a reviewer's glance.
# 0.85 lets a W/V split like BORIWALI ~ BORIVALI through (0.875) and keeps
# KHAR away from KHERWADI (0.5). Set against the names in hand, not derived
# from anything. The near misses seen so far were confirmed and moved into
# ALIASES, so a fuzzy row today is a spelling nobody has looked at yet.
FUZZY_THRESHOLD = 0.85

# A near miss that differs in one of these is a different station, however
# close the rest of the spelling. Matched on the normalised key, where a
# false hit inside a longer word could only make the step more cautious.
COMPASS = re.compile(r"EAST|WEST|NORTH|SOUTH|CENTRAL")

# ALIASES is keyed by a station's exact spelling ("D.B.MARG"). The
# directory's map embed may write the same abbreviation with spaces ("D.B.
# Marg"), so the table is also consulted on letters alone, both ways.
_ALIAS_BY_LETTERS = {re.sub(r"[^A-Z0-9]", "", k): v for k, v in ALIASES.items()}

# Roster (Marathi) name -> the portal's spelling, for the pages whose map
# embed does not name the station and so have no `name_en`. Each was read by
# hand; the note gives the distance from the office on the page's map to the
# MHA point of the same name, or what stood in for that when one side had no
# coordinates. Whitespace-collapsed, because the roster doubles some spaces.
ROSTER_NAMES_EN = {
    "देवनार": "DEONAR",              # 0.91 km; the label is "Urban hotel"
    "गोरेगाव": "GOREGAON",           # 1.32 km; the label is "in"
    "खेरवाडी": "KHERWADI",           # 0.27 km; the iframe is a bare lat,lon
    "नवघर": "NAVGHAR",               # 0.74 km; the label is the street address
    "पार्कसाईट": "PARK SITE",         # no map on the page; the address says
                                     # Parksite police station, LBS Marg
    "ताडदेव": "TARDEO",              # 0.73 km; the label is the street address
    "विलेपार्ले": "VILE PARLE",       # 0.95 km; the label is just "Police Station"
    "यलो गेट": "YELLOWGATE",         # 0.06 km; the label is "Yellow Gate"
    # The five regional cyber stations are housed in a territorial station's
    # building, so the parser refuses the host's name from the embed. The
    # region word in the roster name is the whole of what tells them apart.
    "दक्षिण प्रादेशिक विभाग सायबर": "CYBER POLICE STATION SOUTH REGION",    # 0.23 km; at D B Marg PS
    "मध्य प्रादेशिक विभाग सायबर": "CYBER POLICE STATION CENTRAL REGION",    # 0.01 km; 5th floor, Worli PS
    "पुर्व प्रादेशिक विभाग सायबर": "CYBER POLICE STATION EAST REGION",      # 0.03 km; Shivaji Nagar PS compound
    "पश्चिम प्रादेशिक विभाग सायबर": "CYBER POLICE STATION WEST REGION",    # no map; address is Bandra (W)
                                                                          # 400050, where the MHA point is
    "उत्तर प्रादेशिक विभाग सायबर": "CYBER POLICE STATION NORTH REGION",    # no map; address is Samta Nagar
                                                                          # PS compound, 0.07 km from the MHA point
}

PINCODE_NOTE = (
    "A station is indexed under the pincode of its own office address only. "
    "Station jurisdictions span several pincodes and a pincode spans several "
    "stations, and Maharashtra publishes no jurisdiction boundaries, so a "
    "pincode absent here is unresolved, not unpoliced. Until a pincode "
    "boundary source is adopted, resolve such a search by nearest_stations() "
    "from the pincode's centroid and say that it is a straight-line estimate.")


def _letters(name: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", (name or "").upper())


def _directory_index(records: list[dict]) -> dict[str, tuple[dict, bool]]:
    """Normalised English name -> (record, reached through an alias)."""
    index: dict[str, tuple[dict, bool]] = {}
    for record in records:
        name = record.get("name_en")
        if name:
            # `normalise()` applies ALIASES itself, so whether this key came
            # through one is decided here, before the insert, or the row would
            # read `exact` for a spelling a person had to vouch for.
            via_alias = (name.upper().strip() in ALIASES
                         or _letters(name) in _ALIAS_BY_LETTERS)
            index.setdefault(normalise(name), (record, via_alias))
            expanded = _ALIAS_BY_LETTERS.get(_letters(name))
            if expanded:
                index.setdefault(normalise(expanded), (record, True))
        # A record with no English name has nothing the FIR feed will look up,
        # unless a person has said what its roster name is in the portal's
        # spelling. Otherwise it is left out here and shows up as `none` rows
        # downstream, not indexed under a Marathi name nothing will search.
        spelling = ROSTER_NAMES_EN.get(" ".join((record.get("name_mr") or "").split()))
        if spelling:
            index.setdefault(normalise(spelling), (record, True))
    return index


def _nearest_spelling(key: str, index: dict[str, tuple[dict, bool]],
                      taken: set[int]) -> tuple[dict | None, float | None]:
    """The one record whose name is close enough to `key`, or nothing.

    A record in `taken` already has its FIR name by rule and is not offered
    again: the near miss is then a second station sharing a prefix, not a
    second spelling. A candidate whose compass words differ from the key's is
    a different station by the same reasoning. Two different records tied at
    the top is an ambiguity, and an ambiguity resolved by dict order would be
    a guess, so it returns nothing.
    """
    compass = set(COMPASS.findall(key))
    scored = sorted(
        ((SequenceMatcher(None, key, candidate).ratio(), candidate, record)
         for candidate, (record, _) in index.items()
         if record["ps_id"] not in taken
         and set(COMPASS.findall(candidate)) == compass),
        key=lambda item: -item[0])
    if not scored or scored[0][0] < FUZZY_THRESHOLD:
        return None, None
    best_ratio, _, best = scored[0]
    for ratio, _, record in scored[1:]:
        if ratio < best_ratio:
            break
        if record is not best:
            return None, None
    return best, round(best_ratio, 3)


def join_directory(records: list[dict], fir_station_names: list[str],
                   mha_points: dict[str, dict]) -> list[dict]:
    """One row per FIR station name, saying which directory page it is.

    `mha_points` is `pipeline.mumbai.load_station_points()`: MHA points keyed
    by normalised name. The MHA side is joined exactly as `mumbai.py` does it,
    with no fuzzy step, so `mha_ps` here is null for precisely the stations
    that module reports as unplaced.

    `distance_km_between_directory_and_mha` is a check, not a fact about the
    city: the directory's embed and the MHA point are two people's idea of
    where the same office is, and a large distance means one of the joins
    landed on the wrong station.
    """
    index = _directory_index(records)
    # Rules first, for every name, so that the near-miss pass knows which
    # pages are already spoken for before it offers any.
    by_rule: dict[str, tuple[dict, str]] = {}
    for fir_name in fir_station_names:
        hit = index.get(normalise(fir_name))
        if hit:
            record, via_alias = hit
            by_rule[fir_name] = (record, "alias" if via_alias
                                 or fir_name.upper().strip() in ALIASES else "exact")
    taken = {record["ps_id"] for record, _ in by_rule.values()}

    rows = []
    for fir_name in fir_station_names:
        key = normalise(fir_name)
        point = mha_points.get(key)
        similarity = None
        if fir_name in by_rule:
            record, method = by_rule[fir_name]
        else:
            record, similarity = _nearest_spelling(key, index, taken)
            method = "fuzzy" if record else "none"

        distance = None
        if (record and point and record.get("lat") is not None
                and record.get("lon") is not None):
            distance = round(haversine_km(record["lon"], record["lat"],
                                          point["lon"], point["lat"]), 2)
        rows.append({
            "fir_name": fir_name,
            "directory_ps_id": record["ps_id"] if record else None,
            "directory_name_en": record.get("name_en") if record else None,
            "mha_ps": point["name"] if point else None,
            "method": method,
            "similarity": similarity,
            "distance_km_between_directory_and_mha": distance,
        })
    return rows


def pincode_index(records: list[dict],
                  known_pincodes: list[str] | None = None) -> dict:
    """Station offices grouped by the pincode in their own address.

    `known_pincodes` is the full list of pincodes the search box should
    accept, once a pincode source exists. Given it, `uncovered` names the ones
    no station address carries. Without it, `uncovered` is null with the
    reason, because "no pincode is uncovered" is not something this function
    can know from station addresses alone.
    """
    by_pincode: dict[str, list[int]] = defaultdict(list)
    without: list[int] = []
    for record in records:
        pincode = record.get("pincode")
        if pincode:
            by_pincode[pincode].append(record["ps_id"])
        else:
            without.append(record["ps_id"])

    if known_pincodes is None:
        uncovered, reason = None, ("no pincode list to compare against; the "
                                   "catalogue has no adopted pincode source yet")
    else:
        uncovered, reason = sorted(set(known_pincodes) - set(by_pincode)), None

    return {
        "by_pincode": {pin: sorted(ids) for pin, ids in sorted(by_pincode.items())},
        "without_pincode": sorted(without),
        "uncovered": uncovered,
        "uncovered_reason": reason,
        "note": PINCODE_NOTE,
    }


def nearest_stations(lat: float, lon: float, records: list[dict],
                     k: int = 3) -> list[dict]:
    """The k station offices closest to a point, nearest first.

    Straight-line distance on a sphere. Nobody crosses Mumbai in a straight
    line, so the panel shows this as "about", never as a journey. A record
    without coordinates cannot be ranked and is left out; it is the parser's
    job to say why the coordinates are missing, and the join's `none` rows to
    make the gap visible.
    """
    ranked = sorted(
        ((haversine_km(lon, lat, record["lon"], record["lat"]), record)
         for record in records
         if record.get("lat") is not None and record.get("lon") is not None),
        key=lambda pair: pair[0])
    return [{
        "ps_id": record["ps_id"],
        "name_en": record.get("name_en"),
        "name_mr": record.get("name_mr"),
        "lat": record["lat"],
        "lon": record["lon"],
        "distance_km": round(distance, 2),
        "phones": record.get("phones"),
        "address": record.get("address"),
    } for distance, record in ranked[:k]]


def load_fir_station_names(live: Path = LIVE) -> list[str]:
    """Every distinct registering-station name in the harvested FIRs."""
    names: set[str] = set()
    for path in sorted(live.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                names.add(json.loads(line)["police_station"].strip())
    return sorted(names)
