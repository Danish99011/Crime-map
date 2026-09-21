"""Render the Mumbai locality page: a pincode in, one glance out.

What a person gets for a pincode: the police stations whose own published
address sits in that pincode, their office telephone numbers, what kinds of
FIRs those stations register, and the nearest stations to run to. All of it
from two official sources -- Maharashtra Police's published FIRs and Brihan
Mumbai Police's own station directory -- joined on the station.

Three things this page will not do, and says so on its face:

* **Locate a crime.** An FIR is counted at the station that registered it.
  The finest honest unit is the station, so the map is stations, sized by
  FIRs, never pins at addresses.
* **Guess where a pincode is.** A pincode is placed only from a station's own
  published address. One that no station lists has no location here, and the
  page says that rather than centring on a third-party centroid that, for
  Mumbai, puts 82 of 89 pincodes on the same point.
* **Vouch for a phone number.** They are the commissionerate's, as published,
  with its own warning that they may have changed. The emergency numbers are
  from the same site's emergency-contacts page.

Inputs (all produced by other modules; nothing is fetched here):
  site/mumbai.json                    FIR aggregates per station-month
  data/spine/mumbai_stations.json     the station directory (no officer names)
  data/spine/mumbai_station_join.json FIR station name -> directory ps_id
  data/spine/mumbai_pincodes.json     pincode -> [ps_id]

Run:  python3 -m pipeline.build_locality_page
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SPINE = ROOT / "data" / "spine"
FIR_JSON = SITE / "mumbai.json"
STATIONS_JSON = SPINE / "mumbai_stations.json"
JOIN_JSON = SPINE / "mumbai_station_join.json"
PINCODES_JSON = SPINE / "mumbai_pincodes.json"
OUT = SITE / "locality.html"

HEIGHT = 820.0
PAD = 30.0
MIN_WIDTH, MAX_WIDTH = 300.0, 760.0

# Three hues on the map, validated for colour-vision separation as an
# all-pairs set (see pipeline/build_mumbai_page.py); the rest is neutral.
MAP_HEADS = ("theft", "cheating", "burglary")

# Official emergency numbers, read from mumbaipolice.gov.in/impcontacts on
# 2026-09-21. Devanagari numerals on the page; transliterated here.
EMERGENCY = (
    ("Police emergency", "100"),
    ("All emergencies", "112"),
    ("Mumbai Police infoline", "1090"),
    ("Women's helpline", "103"),
)


def _load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _project(points: list[dict]) -> tuple[list[dict], float, float]:
    """Equirectangular with a cos(lat) correction; canvas fitted to the city."""
    lats = [p["lat"] for p in points]
    lons = [p["lon"] for p in points]
    mid = math.radians(sum(lats) / len(lats))
    xs = [lon * math.cos(mid) for lon in lons]
    x0, x1, y0, y1 = min(xs), max(xs), min(lats), max(lats)
    span_x, span_y = (x1 - x0) or 1e-6, (y1 - y0) or 1e-6
    scale = (HEIGHT - 2 * PAD) / span_y
    width = min(max(span_x * scale + 2 * PAD, MIN_WIDTH), MAX_WIDTH)
    if span_x * scale + 2 * PAD > width:
        scale = (width - 2 * PAD) / span_x
    off_x = (width - span_x * scale) / 2
    off_y = (HEIGHT - span_y * scale) / 2
    for p, x in zip(points, xs):
        p["x"] = round((x - x0) * scale + off_x, 1)
        p["y"] = round((y1 - p["lat"]) * scale + off_y, 1)
    # metres per SVG unit, so the page can draw a scale bar and size a zoom.
    km_per_unit = (111.32 * span_y) / (span_y * scale) if span_y else 0
    return points, width, HEIGHT, km_per_unit


def build() -> str:
    fir = _load(FIR_JSON, {})
    directory = _load(STATIONS_JSON, [])
    join = _load(JOIN_JSON, {})
    pincodes = _load(PINCODES_JSON, {})

    by_ps = {int(d["ps_id"]): d for d in directory if d.get("ps_id") is not None}
    join_rows = join.get("rows", join) if isinstance(join, dict) else join
    fir_to_ps = {}
    for row in (join_rows if isinstance(join_rows, list) else []):
        if row.get("directory_ps_id") is not None and row.get("method") != "none":
            fir_to_ps[row["fir_name"]] = int(row["directory_ps_id"])

    # One record per FIR station (the unit the crime counts live on), carrying
    # its directory entry where the join found one. Coordinates prefer the
    # commissionerate's own embed over the MHA master, because it is the
    # office describing where it is.
    stations = []
    for s in fir.get("stations", []) + fir.get("unplaced", []):
        ps_id = fir_to_ps.get(s["name"])
        d = by_ps.get(ps_id) if ps_id is not None else None
        lat = (d or {}).get("lat") or s.get("lat")
        lon = (d or {}).get("lon") or s.get("lon")
        stations.append({
            "name": s["name"],
            "total": s["total"],
            "months": s["months"],
            "lat": lat, "lon": lon,
            "located_by": "directory" if (d and d.get("lat")) else ("mha" if s.get("lat") else None),
            "ps_id": ps_id,
            "name_en": (d or {}).get("name_en"),
            "name_mr": (d or {}).get("name_mr"),
            "phones": (d or {}).get("phones") or [],
            "email": (d or {}).get("email"),
            "address": (d or {}).get("address"),
            "pincode": (d or {}).get("pincode"),
            "beats": [b.get("name") for b in (d or {}).get("beat_chowkies") or [] if b.get("name")],
            "localities": [loc for b in (d or {}).get("beat_chowkies") or []
                           for loc in (b.get("localities") or [])],
            "railway": (d or {}).get("nearest_railway"),
            "source_url": (d or {}).get("source_url"),
        })

    placed = [s for s in stations if s["lat"] is not None and s["lon"] is not None]
    unplaced = [s for s in stations if s not in placed]
    placed, width, height, km_per_unit = _project(placed)

    # Directory stations with no FIR record at all (e.g. the five cyber
    # stations, or a station the harvest has not reached yet) still belong on
    # the map as places to run to, with phones -- just with no crime count.
    fir_ps_ids = {s["ps_id"] for s in stations if s["ps_id"] is not None}
    extra = []
    for ps_id, d in by_ps.items():
        if ps_id in fir_ps_ids or not d.get("lat") or not d.get("lon"):
            continue
        extra.append({
            "name": d.get("name_en") or d.get("name_mr") or f"ps {ps_id}",
            "total": 0, "months": {}, "lat": d["lat"], "lon": d["lon"],
            "located_by": "directory", "ps_id": ps_id, "name_en": d.get("name_en"), "name_mr": d.get("name_mr"),
            "phones": d.get("phones") or [], "email": d.get("email"),
            "address": d.get("address"), "pincode": d.get("pincode"),
            "beats": [b.get("name") for b in d.get("beat_chowkies") or [] if b.get("name")],
            "localities": [loc for b in d.get("beat_chowkies") or [] for loc in (b.get("localities") or [])],
            "railway": d.get("nearest_railway"), "source_url": d.get("source_url"),
            "no_fir_record": True,
        })
    if extra:
        # Project them on the same canvas by re-projecting everything together.
        placed, width, height, km_per_unit = _project(placed + extra)

    payload = {
        "city": fir.get("city", "Mumbai"),
        "unit": fir.get("unit", "BRIHAN MUMBAI CITY"),
        "sources": {
            "fir": fir.get("source", {}),
            "directory": {
                "name": "Brihan Mumbai Police — station directory",
                "url": "https://mumbaipolice.gov.in/",
                "caveat": "Telephone numbers are as published by Mumbai Police and, in "
                          "the site's own words, may have changed before being updated.",
            },
        },
        "records": fir.get("records", 0),
        "months": fir.get("months", []),
        "months_complete": fir.get("months_complete", []),
        "months_partial": fir.get("months_partial", {}),
        "heads": fir.get("heads", []),
        "map_heads": list(MAP_HEADS),
        "stations": placed,
        "unplaced": unplaced,
        "pincodes": {k: [int(v) for v in vs] for k, vs in pincodes.items()
                     if isinstance(vs, list)} if isinstance(pincodes, dict) else {},
        "emergency": EMERGENCY,
        "viewport": {"width": width, "height": height, "km_per_unit": km_per_unit},
        "caveats": fir.get("caveats", []),
        "directory_stations": len(by_ps),
        "stations_with_phone": sum(1 for s in placed if s["phones"]),
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return TEMPLATE.replace("__PAYLOAD__", blob)


TEMPLATE = r"""<title>Mumbai Locality Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root{
  color-scheme:light;
  --paper:#f6f7f8; --surface:#ffffff; --sunk:#eef0f2;
  --ink:#14181d; --muted:#5a6672; --line:#dde1e5;
  --accent:#2a78d6; --warn:#b4540f; --warn-soft:#b4540f14; --ok:#1a7f4b;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s0:#8c95a0;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --paper:#101317; --surface:#1a1e24; --sunk:#151920;
  --ink:#e9ecef; --muted:#9aa4af; --line:#2a3039;
  --accent:#5c9ef0; --warn:#e0904c; --warn-soft:#e0904c1f; --ok:#4cc18a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s0:#7d8792;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --paper:#101317; --surface:#1a1e24; --sunk:#151920;
  --ink:#e9ecef; --muted:#9aa4af; --line:#2a3039;
  --accent:#5c9ef0; --warn:#e0904c; --warn-soft:#e0904c1f; --ok:#4cc18a;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s0:#7d8792;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
h1,h2,h3{font-family:var(--serif);font-weight:600;margin:0;text-wrap:balance}
a{color:var(--accent)}
.wrap{max-width:1280px;margin:0 auto;padding-inline:16px;padding-block:20px 44px}

header{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px 24px;align-items:end;
  border-bottom:1px solid var(--line);padding-bottom:16px}
@media (max-width:760px){header{grid-template-columns:1fr}}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 7px}
h1{font-size:clamp(24px,3.2vw,33px);line-height:1.12}
.sub{color:var(--muted);margin:8px 0 0;max-width:60ch}

.emg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12.5px;color:var(--muted);
  padding:8px 12px;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
.emg b{font-family:var(--mono);color:var(--ink);font-size:15px;letter-spacing:.02em}
.emg span{display:inline-flex;align-items:baseline;gap:6px}

.search{margin:18px 0 14px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:end}
@media (max-width:560px){.search{grid-template-columns:1fr}}
.search label{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);display:block;margin-bottom:5px}
.search input{width:100%;font:inherit;font-size:17px;color:var(--ink);background:var(--surface);
  border:1px solid var(--line);border-radius:6px;padding:11px 13px}
.search .btns{display:flex;gap:8px}
.btn{font:inherit;font-size:13.5px;padding:10px 14px;border-radius:6px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);cursor:pointer}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn:hover{filter:brightness(.97)}
.hint{font-size:12.5px;color:var(--muted);margin:6px 0 0}
.hint.bad{color:var(--warn)}

.banner{display:flex;gap:12px;align-items:flex-start;margin:0 0 16px;padding:12px 14px;
  border:1px solid var(--line);border-left:3px solid var(--warn);background:var(--warn-soft);border-radius:4px}
.banner strong{display:block;font-family:var(--serif);font-size:15px}
.banner p{margin:4px 0 0;color:var(--muted);max-width:76ch}
.banner-mark{font-family:var(--mono);color:var(--warn);font-size:17px;line-height:1.3}

.layout{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,1fr);gap:18px;align-items:start}
@media (max-width:920px){.layout{grid-template-columns:1fr} .layout aside{order:-1}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:6px}
.mapcard{padding:10px;position:relative}
svg.map{display:block;width:100%;height:auto}
svg.map circle.st{cursor:pointer;stroke:var(--surface);stroke-width:2;transition:opacity .15s,r .25s}
svg.map circle.st:hover{opacity:.8}
svg.map circle.st.dim{opacity:.18}
svg.map circle.st.hit{stroke:var(--ink);stroke-width:2.5}
svg.map circle.st.sel{stroke:var(--accent);stroke-width:3.5}
svg.map .lbl{font-family:var(--sans);font-size:11px;fill:var(--ink);paint-order:stroke;stroke:var(--surface);stroke-width:3px;pointer-events:none}
svg.map .scale line{stroke:var(--muted);stroke-width:1.5}
svg.map .scale text{font-family:var(--mono);font-size:10.5px;fill:var(--muted)}
@media (prefers-reduced-motion:reduce){svg.map circle.st{transition:none}}
.maptools{position:absolute;right:16px;top:16px;display:flex;gap:6px}
.maptools .btn{padding:6px 10px;font-size:12.5px}
.legend{display:flex;flex-wrap:wrap;gap:7px 16px;margin-top:10px;padding-top:10px;
  border-top:1px solid var(--line);font-size:12px;color:var(--muted);align-items:center}
.key{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block;flex:none}
.tip{position:absolute;pointer-events:none;z-index:5;background:var(--surface);border:1px solid var(--line);
  border-radius:5px;padding:7px 9px;font-size:12.5px;box-shadow:0 4px 14px #0000001f;max-width:240px}
.tip b{font-family:var(--serif);font-size:13.5px;display:block}
.tip span{color:var(--muted);font-family:var(--mono);font-size:11.5px}

.psec{padding:14px 16px;border-bottom:1px solid var(--line)}
.psec:last-child{border-bottom:0}
.psec h2{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted)}
.glance-title{font-family:var(--serif);font-size:20px;margin-top:6px}
.glance-sub{color:var(--muted);font-size:13px;margin:2px 0 0}

ul.stations{list-style:none;margin:10px 0 0;padding:0}
ul.stations li{padding:10px 0;border-top:1px solid var(--line)}
ul.stations li:first-child{border-top:0;padding-top:4px}
.st-head{display:flex;justify-content:space-between;gap:10px;align-items:baseline}
.st-name{font-family:var(--serif);font-size:15.5px;font-weight:600}
.st-name button{font:inherit;background:none;border:0;padding:0;color:var(--ink);cursor:pointer;text-align:left}
.st-name button:hover{color:var(--accent)}
.st-dist{font-family:var(--mono);font-size:11.5px;color:var(--muted);white-space:nowrap}
.st-phones{display:flex;flex-wrap:wrap;gap:6px 10px;margin-top:5px}
.st-phones a{font-family:var(--mono);font-size:14px;text-decoration:none;color:var(--ink);
  border:1px solid var(--line);border-radius:5px;padding:3px 8px;background:var(--sunk)}
.st-phones a:hover{border-color:var(--accent);color:var(--accent)}
.st-addr{font-size:12.5px;color:var(--muted);margin-top:4px}
.st-meta{font-size:12px;color:var(--muted);margin-top:3px}
.st-none{font-size:12.5px;color:var(--warn);margin-top:4px}

table.brk{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}
table.brk td{padding:5px 0;border-top:1px solid var(--line);vertical-align:middle}
table.brk tr:first-child td{border-top:0}
table.brk td.c{width:16px;padding-right:7px}
table.brk td.n{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono);white-space:nowrap}
.bar{height:6px;border-radius:3px;display:block;min-width:2px;margin-top:3px;opacity:.5}
.withheld td{color:var(--muted)}
.tagw{font-family:var(--mono);font-size:10px;border:1px solid currentColor;border-radius:99px;padding:0 6px;color:var(--warn)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(84px,1fr));gap:10px;margin-top:10px}
.stat .num{font-family:var(--mono);font-size:20px;font-variant-numeric:tabular-nums;line-height:1.1}
.stat .lbl{font-size:11.5px;color:var(--muted);margin-top:2px}

.covrow{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid var(--line);font-size:12.5px}
.covrow:last-child{border-bottom:0}
.covrow .m{font-family:var(--mono)}
.pill{font-family:var(--mono);font-size:10.5px;border-radius:99px;padding:1px 8px;border:1px solid currentColor;white-space:nowrap}
.pill.full{color:var(--ok)} .pill.part{color:var(--warn)}
details.more summary{cursor:pointer;font-size:12.5px;color:var(--muted);margin-top:8px}

ol.cav{list-style:none;margin:10px 0 0;padding:0;counter-reset:c}
ol.cav li{padding:8px 0 8px 24px;border-bottom:1px solid var(--line);position:relative;counter-increment:c}
ol.cav li:last-child{border-bottom:0}
ol.cav li::before{content:counter(c);position:absolute;left:0;top:9px;font-family:var(--mono);font-size:11px;color:var(--muted)}
ol.cav b{display:block;font-family:var(--serif);font-size:14px}
ol.cav span{color:var(--muted);display:block;margin-top:2px}
footer{margin-top:24px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;max-width:84ch}
footer code{font-family:var(--mono);font-size:11.5px}
</style>

<div class="wrap">
  <header>
    <div>
      <p class="eyebrow">Mumbai &middot; Brihan Mumbai City police commissionerate</p>
      <h1>Your locality, from the record</h1>
      <p class="sub">Type your pincode or your area. You get the police stations that sit in it, their
        office numbers, and what kinds of FIRs those stations register &mdash; from Maharashtra
        Police&rsquo;s published FIRs and Mumbai Police&rsquo;s own station directory, joined on the station.</p>
    </div>
    <div class="emg" id="emg" role="note" aria-label="Emergency numbers"></div>
  </header>

  <div class="search">
    <div>
      <label for="q">Pincode or locality</label>
      <input id="q" type="search" inputmode="text" placeholder="400050, Bandra, Kamathipura&hellip;" autocomplete="off" spellcheck="false" list="q-list">
      <datalist id="q-list"></datalist>
      <p class="hint" id="hint">Search a 6-digit pincode, a station, or a beat-chowky locality named by Mumbai Police.</p>
    </div>
    <div class="btns">
      <button class="btn primary" type="button" id="go">Show my locality</button>
      <button class="btn" type="button" id="reset">Whole city</button>
    </div>
  </div>

  <div class="banner">
    <span class="banner-mark" aria-hidden="true">&#9888;</span>
    <div>
      <strong>A mark is a police station, not a crime scene.</strong>
      <p>An FIR is counted at the station that registered it, never where anything happened. A high count
        can mean a busy area or a station that registers complaints readily; a low one can mean a quiet area
        or a station that turns people away. This page cannot tell you which, and does not try.</p>
    </div>
  </div>

  <div class="layout">
    <div class="card mapcard">
      <div class="maptools"><button class="btn" type="button" id="zoomout" hidden>Zoom out</button></div>
      <svg class="map" id="map" role="img" aria-labelledby="map-t">
        <title id="map-t">Police stations of Brihan Mumbai City, sized by FIRs registered; highlighted stations match the search</title>
        <g id="marks"></g><g id="labels"></g><g class="scale" id="scale"></g>
      </svg>
      <div class="legend" id="legend"></div>
    </div>

    <aside class="card">
      <section class="psec">
        <h2>At a glance</h2>
        <div class="glance-title" id="g-title">All of Mumbai</div>
        <p class="glance-sub" id="g-sub"></p>
        <div class="stats">
          <div class="stat"><div class="num" id="s-fir">&mdash;</div><div class="lbl">FIRs held</div></div>
          <div class="stat"><div class="num" id="s-st">&mdash;</div><div class="lbl">stations</div></div>
          <div class="stat"><div class="num" id="s-ph">&mdash;</div><div class="lbl">with phone</div></div>
        </div>
      </section>
      <section class="psec">
        <h2 id="st-h">Police stations here</h2>
        <ul class="stations" id="stations"></ul>
      </section>
      <section class="psec">
        <h2>What gets registered here</h2>
        <p class="glance-sub" id="brk-sub"></p>
        <table class="brk" id="brk"><tbody id="brk-body"></tbody></table>
      </section>
      <section class="psec">
        <h2>Months held</h2>
        <div id="coverage"></div>
      </section>
      <section class="psec">
        <h2>What is wrong with this data</h2>
        <ol class="cav" id="cav"></ol>
      </section>
    </aside>
  </div>
  <footer id="prov"></footer>
</div>

<script id="payload" type="application/json">__PAYLOAD__</script>
<script>
(function(){
"use strict";
var D=JSON.parse(document.getElementById("payload").textContent);
var NEUTRAL="var(--s0)", SV=["--s1","--s2","--s3"], mapColor={};
D.map_heads.forEach(function(k,i){ mapColor[k]="var("+SV[i]+")"; });
var headLabel={}; D.heads.forEach(function(h){ headLabel[h.key]=h.label; });
var all=D.stations, byName={}; all.forEach(function(s){ byName[s.name]=s; });
var W=D.viewport.width, H=D.viewport.height, KM=D.viewport.km_per_unit||0.05;
var state={ hits:null, sel:null, label:"", sub:"", zoom:1 };
// Units that are real police stations but not places a resident runs to:
// the five cyber-crime cells and the two marine units. They stay searchable
// and keep their counts; they are just not offered as "the nearest station".
var NOT_TERRITORIAL=/CYBER|SAGRI|MARINE|सायबर|सागरी/i;

function esc(s){ return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];}); }
function total(s){ var t=0; for(var m in s.months){ var c=s.months[m]; for(var k in c) t+=c[k]; } return t; }
function breakdown(list){ var b={}; list.forEach(function(s){ for(var m in s.months){ var c=s.months[m]; for(var k in c) b[k]=(b[k]||0)+c[k]; } }); return b; }
function dominant(s){ var b=breakdown([s]),best=null,bv=0; D.map_heads.forEach(function(k){ if((b[k]||0)>bv){bv=b[k];best=k;} }); return best; }
function km(a,b){ var R=6371,dl=(b.lat-a.lat)*Math.PI/180,dn=(b.lon-a.lon)*Math.PI/180,
  x=Math.sin(dl/2)*Math.sin(dl/2)+Math.cos(a.lat*Math.PI/180)*Math.cos(b.lat*Math.PI/180)*Math.sin(dn/2)*Math.sin(dn/2);
  return 2*R*Math.atan2(Math.sqrt(x),Math.sqrt(1-x)); }
function norm(s){ return String(s||"").toLowerCase().replace(/police station|sub ps|\bps\b|पोलीस ठाणे|पोलीस चौकी|बीट चौकी/g,"").replace(/[^a-z0-9ऀ-ॿ]/g,""); }

// --- map ------------------------------------------------------------------
var svg=document.getElementById("map"); svg.setAttribute("viewBox","0 0 "+W+" "+H);
var marks=document.getElementById("marks"), labels=document.getElementById("labels"), tip=null;
var maxTotal=Math.max.apply(null,all.map(total).concat([1]));
// Radii are screen pixels: divided by the zoom so a mark drawn at 20px stays
// 20px after the viewBox tightens, instead of ballooning with the map.
function radius(n){ return (n? 4+16*Math.sqrt(n/maxTotal) : 3.5)/state.zoom; }

function draw(){
  marks.textContent=""; labels.textContent="";
  var hitSet=state.hits? new Set(state.hits.map(function(s){return s.name;})) : null;
  all.forEach(function(s){
    var n=total(s), c=document.createElementNS("http://www.w3.org/2000/svg","circle");
    var cls="st"; if(hitSet){ cls+= hitSet.has(s.name)?" hit":" dim"; } if(state.sel===s.name) cls+=" sel";
    c.setAttribute("class",cls); c.setAttribute("cx",s.x); c.setAttribute("cy",s.y); c.setAttribute("r",radius(n));
    c.setAttribute("vector-effect","non-scaling-stroke");
    var d=dominant(s); c.setAttribute("fill", d?mapColor[d]:NEUTRAL); c.setAttribute("fill-opacity", n?"0.82":"0.35");
    c.setAttribute("tabindex","0"); c.setAttribute("role","button");
    c.setAttribute("aria-label", s.name+", "+n+" FIRs"+(s.phones.length?", phone "+s.phones[0]:""));
    c.addEventListener("click",function(){ select(s.name); });
    c.addEventListener("keydown",function(e){ if(e.key==="Enter"||e.key===" "){e.preventDefault();select(s.name);} });
    c.addEventListener("mouseenter",function(e){ showTip(e,s,n); }); c.addEventListener("mousemove",moveTip);
    c.addEventListener("mouseleave",hideTip); c.addEventListener("focus",function(e){ showTip(e,s,n); }); c.addEventListener("blur",hideTip);
    marks.appendChild(c);
    if(hitSet && hitSet.has(s.name)){
      var t=document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("class","lbl"); t.setAttribute("x",s.x+radius(n)+4/state.zoom); t.setAttribute("y",s.y+4/state.zoom);
      t.setAttribute("font-size",(11/state.zoom)+"px"); t.setAttribute("stroke-width",(3/state.zoom)+"px"); t.textContent=s.name_en||s.name;
      labels.appendChild(t);
    }
  });
  drawScale(); drawLegend();
}
function drawScale(){
  var g=document.getElementById("scale"); g.textContent="";
  var vb=svg.getAttribute("viewBox").split(" ").map(Number), x0=vb[0],y0=vb[1],w=vb[2],h=vb[3];
  var kmTarget = w*KM>8? 2 : (w*KM>3? 1 : 0.5), len=kmTarget/KM;
  var x=x0+w-len-14, y=y0+h-14;
  var l=document.createElementNS("http://www.w3.org/2000/svg","line"); l.setAttribute("x1",x);l.setAttribute("x2",x+len);l.setAttribute("y1",y);l.setAttribute("y2",y); g.appendChild(l);
  var t=document.createElementNS("http://www.w3.org/2000/svg","text"); t.setAttribute("x",x);t.setAttribute("y",y-5/state.zoom); t.setAttribute("font-size",(10.5/state.zoom)+"px"); t.textContent=kmTarget+" km"; g.appendChild(t);
  l.setAttribute("vector-effect","non-scaling-stroke");
}
function zoomTo(list){
  var zo=document.getElementById("zoomout");
  if(!list||!list.length){ svg.setAttribute("viewBox","0 0 "+W+" "+H); zo.hidden=true; state.zoom=1; draw(); return; }
  var xs=list.map(function(s){return s.x;}), ys=list.map(function(s){return s.y;});
  var minSpan=3/KM; // never tighter than ~3 km across, so neighbours stay in view
  var cx=(Math.min.apply(null,xs)+Math.max.apply(null,xs))/2, cy=(Math.min.apply(null,ys)+Math.max.apply(null,ys))/2;
  var w=Math.max(Math.max.apply(null,xs)-Math.min.apply(null,xs)+80, minSpan), h=Math.max(Math.max.apply(null,ys)-Math.min.apply(null,ys)+80, minSpan*H/W);
  if(w/h > W/H) h=w*H/W; else w=h*W/H;
  svg.setAttribute("viewBox",(cx-w/2)+" "+(cy-h/2)+" "+w+" "+h); zo.hidden=false; state.zoom=W/w; draw();
}
function showTip(e,s,n){ hideTip(); tip=document.createElement("div"); tip.className="tip";
  tip.innerHTML="<b>"+esc(s.name_en||s.name)+"</b><span>"+n.toLocaleString("en-IN")+" FIRs"+(s.phones.length?" &middot; "+esc(s.phones[0]):"")+(s.pincode?" &middot; "+esc(s.pincode):"")+"</span>";
  document.querySelector(".mapcard").appendChild(tip); moveTip(e); }
function moveTip(e){ if(!tip) return; var box=document.querySelector(".mapcard").getBoundingClientRect();
  var x=(e.clientX||box.left)-box.left+12, y=(e.clientY||box.top)-box.top+12; x=Math.min(x,box.width-tip.offsetWidth-8);
  tip.style.left=Math.max(6,x)+"px"; tip.style.top=Math.max(6,y)+"px"; }
function hideTip(){ if(tip&&tip.parentNode) tip.parentNode.removeChild(tip); tip=null; }
function drawLegend(){ var h=[]; D.map_heads.forEach(function(k){ h.push('<span class="key"><i class="dot" style="background:'+mapColor[k]+'"></i>mostly '+esc(headLabel[k])+'</span>'); });
  h.push('<span class="key"><i class="dot" style="background:'+NEUTRAL+'"></i>other, or no FIRs held</span>');
  h.push('<span class="key">area &#8733; FIRs registered</span>'); document.getElementById("legend").innerHTML=h.join(""); }

// --- search ----------------------------------------------------------------
function findHits(q){
  q=q.trim(); if(!q) return {hits:null,label:"All of Mumbai",sub:""};
  var pin=q.replace(/\s+/g,"");
  if(/^\d{6}$/.test(pin)){
    var ids=D.pincodes[pin]||[], hits=all.filter(function(s){ return s.ps_id!=null && ids.indexOf(s.ps_id)>=0; });
    if(hits.length) return {hits:hits,label:"Pincode "+pin,sub:hits.length+" police station"+(hits.length>1?"s list":" lists")+" this pincode as its own address."};
    if(/^400\d{3}$/.test(pin)) return {hits:[],label:"Pincode "+pin,sub:"No police station lists this pincode as its address, and Mumbai Police publish no pincode-to-station map. Nothing is drawn rather than guessed: try a neighbouring pincode, your area's name, or the station you know."};
    return {hits:[],label:"Pincode "+pin,sub:"That is not a Mumbai pincode (Mumbai's run 400001-400104)."};
  }
  var n=norm(q), hits=all.filter(function(s){ return norm(s.name).indexOf(n)>=0 || norm(s.name_en).indexOf(n)>=0; });
  if(hits.length) return {hits:hits,label:hits.length===1?(hits[0].name_en||hits[0].name)+" police station":q,sub:hits.length===1?"":hits.length+" stations match."};
  hits=all.filter(function(s){ return s.beats.concat(s.localities).some(function(x){ return norm(x).indexOf(n)>=0; }); });
  if(hits.length) return {hits:hits,label:q,sub:"Named by Mumbai Police as a beat chowky or a locality under "+hits.map(function(s){return s.name_en||s.name;}).join(", ")+"."};
  return {hits:[],label:q,sub:"No pincode, station, or police-named locality matches. Localities come only from what Mumbai Police list under each station's beat chowkies."};
}
function run(){
  var r=findHits(document.getElementById("q").value); state.hits=r.hits; state.label=r.label; state.sub=r.sub; state.sel=null;
  var hint=document.getElementById("hint"); hint.className="hint"+(r.hits&&!r.hits.length?" bad":""); hint.textContent=r.hits&&!r.hits.length? r.sub : "Search a 6-digit pincode, a station, or a beat-chowky locality named by Mumbai Police.";
  zoomTo(r.hits&&r.hits.length?r.hits:null); panel();
}
function select(name){ state.sel=(state.sel===name)?null:name; draw(); panel(); var c=document.querySelector("circle.sel"); if(c) c.focus({preventScroll:true}); }

// --- panel -----------------------------------------------------------------
function stationRow(s, distKm){
  var phones=s.phones.length? '<div class="st-phones">'+s.phones.map(function(p){ return '<a href="tel:'+esc(p.replace(/[^\d+]/g,""))+'">'+esc(p)+'</a>'; }).join("")+'</div>'
                              : '<div class="st-none">No office number in the Mumbai Police directory for this station'+(s.ps_id==null?' (no directory match)':'')+'.</div>';
  var meta=[]; if(s.pincode) meta.push("pincode "+esc(s.pincode)); if(s.railway) meta.push("nearest station: "+esc(s.railway.split(",")[0]));
  if(s.no_fir_record) meta.push("no FIRs held for this station yet"); else meta.push(total(s).toLocaleString("en-IN")+" FIRs held");
  return '<li><div class="st-head"><span class="st-name"><button type="button" data-n="'+esc(s.name)+'">'+esc(s.name_en||s.name)+'</button></span>'+
    (distKm!=null?'<span class="st-dist">'+distKm.toFixed(1)+' km</span>':'')+'</div>'+phones+
    (s.address?'<div class="st-addr">'+esc(s.address)+'</div>':'')+'<div class="st-meta">'+meta.join(" &middot; ")+'</div></li>';
}
function panel(){
  var hits=state.hits, focus = state.sel? [byName[state.sel]] : (hits&&hits.length? hits : all.filter(function(s){return !s.no_fir_record;}));
  document.getElementById("g-title").textContent = state.sel? (byName[state.sel].name_en||state.sel) : state.label||"All of Mumbai";
  document.getElementById("g-sub").textContent = state.sel? (byName[state.sel].address||"") : state.sub;
  var firs=focus.reduce(function(a,s){return a+total(s);},0);
  document.getElementById("s-fir").textContent=firs.toLocaleString("en-IN");
  document.getElementById("s-st").textContent=focus.length;
  document.getElementById("s-ph").textContent=focus.filter(function(s){return s.phones.length;}).length;

  // stations: the matched ones first, then the nearest others by distance from the match's centre
  var list=[], head=document.getElementById("st-h");
  if(hits&&hits.length||state.sel){
    var anchor=state.sel? [byName[state.sel]] : hits;
    var c={lat:anchor.reduce(function(a,s){return a+s.lat;},0)/anchor.length, lon:anchor.reduce(function(a,s){return a+s.lon;},0)/anchor.length};
    var names=new Set(anchor.map(function(s){return s.name;}));
    list=anchor.map(function(s){ return stationRow(s, state.sel?null:0); });
    var near=all.filter(function(s){return !names.has(s.name) && !NOT_TERRITORIAL.test(s.name) && !NOT_TERRITORIAL.test(s.name_mr||"");}).map(function(s){return {s:s,d:km(c,s)};}).sort(function(a,b){return a.d-b.d;}).slice(0,4);
    head.textContent=state.sel?"This station, then the nearest":"Police stations here, then the nearest";
    list=anchor.map(function(s){return stationRow(s,null);}).concat(near.map(function(x){return stationRow(x.s,x.d);}));
  } else {
    head.textContent="Police stations (most FIRs first)";
    list=all.filter(function(s){return !s.no_fir_record;}).slice().sort(function(a,b){return total(b)-total(a);}).slice(0,8).map(function(s){return stationRow(s,null);});
  }
  document.getElementById("stations").innerHTML=list.join("");
  Array.prototype.forEach.call(document.querySelectorAll("#stations button[data-n]"),function(b){ b.addEventListener("click",function(){ select(b.getAttribute("data-n")); }); });

  // breakdown, grouped by offence head, for the stations in focus
  var b=breakdown(focus), rows=D.heads.filter(function(h){return b[h.key]||h.withheld;}), max=Math.max.apply(null,D.heads.map(function(h){return b[h.key]||0;}).concat([1]));
  document.getElementById("brk-sub").textContent = focus.length===1? "FIRs registered at this station, by offence head." : "FIRs registered at these "+focus.length+" stations, by offence head.";
  document.getElementById("brk-body").innerHTML = rows.map(function(h){
    if(h.withheld) return '<tr class="withheld"><td class="c"></td><td>'+esc(h.label)+' <span class="tagw">withheld by law</span></td><td class="n">&mdash;</td></tr>';
    var n=b[h.key]||0, col=mapColor[h.key]||NEUTRAL;
    return '<tr><td class="c"><i class="dot" style="background:'+col+'"></i></td><td>'+esc(h.label)+'<span class="bar" style="width:'+Math.round(100*n/max)+'%;background:'+col+'"></span></td><td class="n">'+n.toLocaleString("en-IN")+'</td></tr>';
  }).join("");
}

// --- static ----------------------------------------------------------------
document.getElementById("emg").innerHTML=D.emergency.map(function(e){ return '<span>'+esc(e[0])+' <b><a href="tel:'+esc(e[1])+'" style="color:inherit;text-decoration:none">'+esc(e[1])+'</a></b></span>'; }).join("");
var dl=document.getElementById("q-list"), opts=[];
Object.keys(D.pincodes).sort().forEach(function(p){ opts.push(p); }); all.forEach(function(s){ opts.push(s.name_en||s.name); });
dl.innerHTML=opts.map(function(o){return '<option value="'+esc(o)+'"></option>';}).join("");
document.getElementById("go").addEventListener("click",run);
document.getElementById("q").addEventListener("keydown",function(e){ if(e.key==="Enter"){ e.preventDefault(); run(); } });
document.getElementById("reset").addEventListener("click",function(){ document.getElementById("q").value=""; run(); });
document.getElementById("zoomout").addEventListener("click",function(){ zoomTo(null); });
document.getElementById("coverage").innerHTML=D.months.map(function(m){ var full=D.months_complete.indexOf(m)>=0, p=D.months_partial[m]; var note=full?"verified against the portal&rsquo;s own count":(p&&p.declared?"got "+p.in_data+" of "+p.declared:(p&&p.in_data<25?"stray records from an adjacent query":"fetched, not yet verified"));
  return '<div class="covrow"><span class="m">'+m+'</span><span style="color:var(--muted)">'+note+'</span><span class="pill '+(full?"full":"part")+'">'+(full?"complete":"partial")+'</span></div>'; }).join("");
var titles={geography:"A station is not a scene",reporting:"This maps reporting, not crime",withheld:"Whole categories are missing by law","law-change":"Two incompatible statute books",unplaced:"Some stations cannot be drawn",coverage:"Partial months are undercounts"};
document.getElementById("cav").innerHTML=D.caveats.map(function(c){ return '<li><b>'+esc(titles[c.kind]||c.kind)+'</b><span>'+esc(c.text)+'</span></li>'; }).join("")+
  '<li><b>Phone numbers may have changed</b><span>'+esc(D.sources.directory.caveat)+' In an emergency dial 100 or 112.</span></li>'+
  '<li><b>A pincode is only where a station says it is</b><span>Pincodes come from each station&rsquo;s own published address. No authority publishes pincode boundaries, so a pincode no station lists is not drawn, rather than guessed.</span></li>';
document.getElementById("prov").innerHTML="Sources: <a href=\""+esc(D.sources.fir.url||"#")+"\" target=\"_blank\" rel=\"noopener\">"+esc(D.sources.fir.name||"Maharashtra Police published FIRs")+"</a> (contains information published by Maharashtra Police; reproduced with the source acknowledged, as its copyright policy requires) and <a href=\""+esc(D.sources.directory.url)+"\" target=\"_blank\" rel=\"noopener\">"+esc(D.sources.directory.name)+"</a> (office numbers, addresses, beat chowkies and station coordinates from each station&rsquo;s page; officer names are not carried). "+
  D.records.toLocaleString("en-IN")+" FIRs across "+D.months.length+" months; "+D.stations.length+" stations drawn, "+D.stations_with_phone+" with an office number, "+D.unplaced.length+" listed without a location. Built by <code>pipeline/build_locality_page.py</code>.";
run();
})();
</script>
"""


def main() -> int:
    SITE.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
