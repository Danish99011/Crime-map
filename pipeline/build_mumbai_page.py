"""Render the Mumbai station map as one self-contained HTML page.

No basemap tiles, for three reasons that all point the same way: the artifact
sandbox blocks external images, a published map of India carries an obligation
to depict national boundaries as Survey of India does, and a street basemap
under these marks would imply a precision the data does not have. Drawing only
Mumbai's own station points avoids depicting a boundary at all.

Marks are circles at police stations, never pins at incidents, because an FIR
records the office that registered it and nothing finer. Maharashtra publishes
no jurisdiction polygons, so there is no honest area to fill either.

Run:  python3 -m pipeline.build_mumbai_page
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = SITE / "mumbai.json"
OUT = SITE / "mumbai.html"

# The drawing is sized to the city, not the other way round. Mumbai is a long
# narrow peninsula, so a square-ish canvas leaves half the card empty; the
# width is derived from the data's own aspect ratio after projecting.
HEIGHT = 840.0
PAD = 34.0
MIN_WIDTH, MAX_WIDTH = 300.0, 760.0

# The three crime heads the map may colour at once. A map is an all-pairs
# form -- any mark can land beside any other -- and at four categorical hues
# the validated palette stops clearing the colour-vision separation floors.
# So the map carries three hues plus a neutral "other", and the full
# breakdown lives in the panel where marks sit in a fixed order.
MAP_HEADS = ("theft", "cheating", "burglary")


def project(stations: list[dict]) -> tuple[list[dict], float, float]:
    """Equirectangular with a cos(lat) correction -- exact enough for one city.

    Returns the placed stations and the canvas sized to fit them, so the
    drawing keeps true proportions without padding the card with empty space.
    """
    lats = [s["lat"] for s in stations]
    lons = [s["lon"] for s in stations]
    mid = math.radians(sum(lats) / len(lats))
    xs = [lon * math.cos(mid) for lon in lons]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(lats), max(lats)
    span_x, span_y = (x1 - x0) or 1e-6, (y1 - y0) or 1e-6

    scale = (HEIGHT - 2 * PAD) / span_y
    width = min(max(span_x * scale + 2 * PAD, MIN_WIDTH), MAX_WIDTH)
    if span_x * scale + 2 * PAD > width:          # very wide city: refit
        scale = (width - 2 * PAD) / span_x
    off_x = (width - span_x * scale) / 2
    off_y = (HEIGHT - span_y * scale) / 2

    out = []
    for station, x in zip(stations, xs):
        out.append(dict(
            station,
            x=round((x - x0) * scale + off_x, 1),
            y=round((y1 - station["lat"]) * scale + off_y, 1),
        ))
    return out, width, HEIGHT


def build() -> str:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    placed, width, height = project(payload["stations"])
    payload["stations"] = placed
    payload["map_heads"] = list(MAP_HEADS)
    payload["viewport"] = {"width": width, "height": height}
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return TEMPLATE.replace("__PAYLOAD__", blob)


TEMPLATE = r"""<title>Mumbai FIR Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root{
  color-scheme:light;
  --paper:#f6f7f8; --surface:#ffffff; --sunk:#eef0f2;
  --ink:#14181d; --muted:#5a6672; --line:#dde1e5;
  --accent:#2a78d6; --warn:#b4540f; --warn-soft:#b4540f14;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s0:#8c95a0;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --paper:#101317; --surface:#1a1e24; --sunk:#151920;
  --ink:#e9ecef; --muted:#9aa4af; --line:#2a3039;
  --accent:#5c9ef0; --warn:#e0904c; --warn-soft:#e0904c1f;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s0:#7d8792;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --paper:#101317; --surface:#1a1e24; --sunk:#151920;
  --ink:#e9ecef; --muted:#9aa4af; --line:#2a3039;
  --accent:#5c9ef0; --warn:#e0904c; --warn-soft:#e0904c1f;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s0:#7d8792;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
h1,h2,h3{font-family:var(--serif);font-weight:600;margin:0;text-wrap:balance}
.wrap{max-width:1280px;margin:0 auto;padding-inline:16px;padding-block:22px 44px}

header{border-bottom:1px solid var(--line);padding-bottom:16px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 7px}
h1{font-size:clamp(25px,3.4vw,35px);line-height:1.12}
.sub{color:var(--muted);margin:8px 0 0;max-width:64ch}

.banner{display:flex;gap:12px;align-items:flex-start;margin:18px 0 22px;padding:14px 16px;
  border:1px solid var(--line);border-left:3px solid var(--warn);
  background:var(--warn-soft);border-radius:4px}
.banner strong{display:block;font-family:var(--serif);font-size:15.5px}
.banner p{margin:5px 0 0;color:var(--muted);max-width:74ch}
.banner-mark{font-family:var(--mono);color:var(--warn);font-size:17px;line-height:1.3}

.layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(310px,1fr);gap:20px;align-items:start}
@media (max-width:920px){.layout{grid-template-columns:1fr}}

.controls{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:flex-end;margin-bottom:14px}
.field{display:flex;flex-direction:column;gap:4px;min-width:0}
.field label{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted)}
.field select,.field input{font:inherit;color:var(--ink);background:var(--surface);
  border:1px solid var(--line);border-radius:4px;padding:7px 9px;min-width:160px;max-width:100%}

.card{background:var(--surface);border:1px solid var(--line);border-radius:6px}
.mapcard{padding:10px;position:relative}
svg.map{display:block;width:100%;height:auto}
svg.map circle.st{cursor:pointer;stroke:var(--surface);stroke-width:2;
  transition:opacity .12s}
svg.map circle.st:hover{opacity:.78}
svg.map circle.st.sel{stroke:var(--ink);stroke-width:2.5}
@media (prefers-reduced-motion:reduce){svg.map circle.st{transition:none}}
.scalebar{font-family:var(--mono);font-size:10.5px;fill:var(--muted)}

.legend{display:flex;flex-wrap:wrap;gap:7px 16px;margin-top:10px;padding-top:10px;
  border-top:1px solid var(--line);font-size:12px;color:var(--muted);align-items:center}
.key{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block;flex:none}
.sizekey{display:inline-flex;align-items:center;gap:6px;margin-left:auto}
.sizekey svg{display:block}

.tip{position:absolute;pointer-events:none;z-index:5;background:var(--surface);
  border:1px solid var(--line);border-radius:5px;padding:7px 9px;font-size:12.5px;
  box-shadow:0 4px 14px #0000001f;max-width:230px}
.tip b{font-family:var(--serif);font-size:13.5px;display:block}
.tip span{color:var(--muted);font-family:var(--mono);font-size:11.5px}

.psec{padding:14px 16px;border-bottom:1px solid var(--line)}
.psec:last-child{border-bottom:0}
.psec h2{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted)}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(84px,1fr));gap:12px;margin-top:11px}
.stat .num{font-family:var(--mono);font-size:21px;font-variant-numeric:tabular-nums;line-height:1.1}
.stat .lbl{font-size:11.5px;color:var(--muted);margin-top:2px}

table.brk{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
table.brk th{text-align:left;font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);font-weight:500;padding:0 0 6px}
table.brk th.n,table.brk td.n{text-align:right;font-variant-numeric:tabular-nums;
  font-family:var(--mono)}
table.brk td{padding:5px 0;border-top:1px solid var(--line);vertical-align:middle}
table.brk td.c{width:16px;padding-right:7px}
.bar{height:6px;border-radius:3px;background:var(--s0);display:block;min-width:2px}
.withheld td{color:var(--muted)}
.withheld .tagw{font-family:var(--mono);font-size:10px;border:1px solid currentColor;
  border-radius:99px;padding:0 6px;color:var(--warn)}

ul.stlist{list-style:none;margin:10px 0 0;padding:0;max-height:300px;overflow-y:auto}
ul.stlist li+li{border-top:1px solid var(--line)}
ul.stlist button{width:100%;text-align:left;background:none;border:0;padding:7px 2px;
  font:inherit;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;
  align-items:center;gap:10px}
ul.stlist button:hover{color:var(--accent)}
ul.stlist .n{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--muted);font-size:12.5px}
ul.stlist .nm{display:flex;align-items:center;gap:7px;min-width:0}
ul.stlist .nm span.t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

ol.cav{list-style:none;margin:10px 0 0;padding:0;counter-reset:c}
ol.cav li{padding:9px 0 9px 25px;border-bottom:1px solid var(--line);position:relative;counter-increment:c}
ol.cav li:last-child{border-bottom:0}
ol.cav li::before{content:counter(c);position:absolute;left:0;top:10px;font-family:var(--mono);
  font-size:11px;color:var(--muted)}
ol.cav b{display:block;font-family:var(--serif);font-size:14px}
ol.cav span{color:var(--muted);display:block;margin-top:2px}

.covrow{display:flex;justify-content:space-between;gap:10px;padding:6px 0;
  border-bottom:1px solid var(--line);font-size:13px;align-items:center}
.covrow:last-child{border-bottom:0}
.covrow .m{font-family:var(--mono)}
.pill{font-family:var(--mono);font-size:10.5px;border-radius:99px;padding:1px 8px;
  border:1px solid currentColor;white-space:nowrap}
.pill.full{color:var(--s3)} .pill.part{color:var(--warn)}

footer{margin-top:26px;padding-top:14px;border-top:1px solid var(--line);
  color:var(--muted);font-size:12px;max-width:80ch}
footer a{color:var(--accent)}
footer code{font-family:var(--mono);font-size:11.5px}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
</style>

<div class="wrap">
  <header>
    <p class="eyebrow">Mumbai &middot; Brihan Mumbai City police commissionerate</p>
    <h1>Where Mumbai&rsquo;s FIRs get registered</h1>
    <p class="sub">Every First Information Report published by Maharashtra Police for the
      Brihan Mumbai City commissionerate, counted at the police station that registered it.
      Maharashtra runs the most open crime feed in India &mdash; and publishes no station
      boundaries at all, which is why this is a map of stations and not of areas.</p>
  </header>

  <div class="banner">
    <span class="banner-mark" aria-hidden="true">&#9888;</span>
    <div>
      <strong>A mark is a police station, not a crime scene.</strong>
      <p>An FIR records the station that registered it, never where the offence happened.
        Nothing here should be read as &ldquo;crime at this spot&rdquo;, and a station with a
        high count may simply be one that registers complaints readily. Read
        <em>What is wrong with this data</em> before drawing any conclusion from it.</p>
    </div>
  </div>

  <div class="controls">
    <div class="field">
      <label for="f-month">Month</label>
      <select id="f-month"></select>
    </div>
    <div class="field">
      <label for="f-head">Crime type</label>
      <select id="f-head"></select>
    </div>
    <div class="field">
      <label for="f-q">Find a station</label>
      <input id="f-q" type="search" placeholder="Andheri, Colaba&hellip;" autocomplete="off" spellcheck="false">
    </div>
  </div>

  <div class="layout">
    <div class="card mapcard">
      <svg class="map" id="map" role="img" aria-labelledby="map-t">
        <title id="map-t">Police stations of Brihan Mumbai City, sized by the number of FIRs registered</title>
        <g id="marks"></g>
        <g id="scale"></g>
      </svg>
      <div class="legend" id="legend"></div>
    </div>

    <aside class="card">
      <section class="psec">
        <h2>In view</h2>
        <div class="stats">
          <div class="stat"><div class="num" id="s-fir">&mdash;</div><div class="lbl">FIRs</div></div>
          <div class="stat"><div class="num" id="s-st">&mdash;</div><div class="lbl">stations</div></div>
          <div class="stat"><div class="num" id="s-mo">&mdash;</div><div class="lbl">months held</div></div>
        </div>
      </section>

      <section class="psec" id="detail">
        <h2 id="d-title">Breakdown</h2>
        <p class="sub" id="d-hint" style="font-size:13px;margin-top:8px">
          Select a station on the map or in the list for its own breakdown.</p>
        <table class="brk" id="d-table" hidden>
          <thead><tr><th colspan="2">Offence head</th><th class="n">FIRs</th></tr></thead>
          <tbody id="d-body"></tbody>
        </table>
      </section>

      <section class="psec">
        <h2>Stations</h2>
        <ul class="stlist" id="stations"></ul>
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
var D = JSON.parse(document.getElementById("payload").textContent);
var SV = ["--s1","--s2","--s3"], NEUTRAL = "var(--s0)";
var headLabel = {}, headWithheld = {};
D.heads.forEach(function(h){ headLabel[h.key]=h.label; headWithheld[h.key]=h.withheld; });
var mapColor = {};
D.map_heads.forEach(function(k,i){ mapColor[k] = "var("+SV[i]+")"; });

var state = { month:"__ALL__", head:"__ALL__", sel:null, q:"" };
var all = D.stations.concat(D.unplaced);

function countOf(st, month, head){
  var t=0;
  for (var m in st.months){
    if (month!=="__ALL__" && m!==month) continue;
    var c=st.months[m];
    if (head==="__ALL__"){ for(var k in c) t+=c[k]; }
    else if (c[head]) t+=c[head];
  }
  return t;
}
function breakdown(st, month){
  var out={};
  for (var m in st.months){
    if (month!=="__ALL__" && m!==month) continue;
    var c=st.months[m];
    for (var k in c) out[k]=(out[k]||0)+c[k];
  }
  return out;
}
function dominant(st, month){
  var b=breakdown(st,month), best=null, bv=0;
  D.map_heads.forEach(function(k){ if((b[k]||0)>bv){bv=b[k]||0;best=k;} });
  return best;
}

var svg=document.getElementById("map");
svg.setAttribute("viewBox","0 0 "+D.viewport.width+" "+D.viewport.height);
var marks=document.getElementById("marks");
var tip=null;

function radius(n, max){
  if (!n) return 3;
  return 4 + 17*Math.sqrt(n/ (max||1));   // area-proportional
}

function draw(){
  var counts = D.stations.map(function(s){ return countOf(s,state.month,state.head); });
  var max = Math.max.apply(null, counts.concat([1]));
  marks.textContent="";
  D.stations.forEach(function(s,i){
    var n=counts[i];
    var c=document.createElementNS("http://www.w3.org/2000/svg","circle");
    c.setAttribute("class","st"+(state.sel===s.name?" sel":""));
    c.setAttribute("cx",s.x); c.setAttribute("cy",s.y);
    c.setAttribute("r",radius(n,max));
    var col;
    if (state.head!=="__ALL__") col = mapColor[state.head] || NEUTRAL;
    else { var d=dominant(s,state.month); col = d?mapColor[d]:NEUTRAL; }
    c.setAttribute("fill", col);
    c.setAttribute("fill-opacity", n? "0.82":"0.22");
    c.setAttribute("tabindex","0");
    c.setAttribute("role","button");
    c.setAttribute("aria-label", s.name+", "+n+" FIRs");
    c.addEventListener("click",function(){ select(s.name); });
    c.addEventListener("keydown",function(e){ if(e.key==="Enter"||e.key===" "){e.preventDefault();select(s.name);} });
    c.addEventListener("mouseenter",function(e){ showTip(e,s,n); });
    c.addEventListener("mousemove",function(e){ moveTip(e); });
    c.addEventListener("mouseleave",hideTip);
    c.addEventListener("focus",function(e){ showTip(e,s,n); });
    c.addEventListener("blur",hideTip);
    marks.appendChild(c);
  });
  document.getElementById("s-fir").textContent =
    all.reduce(function(a,s){return a+countOf(s,state.month,state.head);},0).toLocaleString("en-IN");
  document.getElementById("s-st").textContent = all.filter(function(s){
    return countOf(s,state.month,state.head)>0; }).length;
  document.getElementById("s-mo").textContent = D.months.length;
  drawList(); drawLegend(max);
}

function showTip(e,s,n){
  hideTip();
  tip=document.createElement("div"); tip.className="tip";
  var b=breakdown(s,state.month), parts=[];
  D.map_heads.forEach(function(k){ if(b[k]) parts.push(headLabel[k]+" "+b[k]); });
  tip.innerHTML="<b>"+esc(s.name)+"</b><span>"+n.toLocaleString("en-IN")+" FIRs"+
    (parts.length?" &middot; "+esc(parts.join(", ")):"")+"</span>";
  document.querySelector(".mapcard").appendChild(tip);
  moveTip(e);
}
function moveTip(e){
  if(!tip) return;
  var box=document.querySelector(".mapcard").getBoundingClientRect();
  var x=(e.clientX||box.left+box.width/2)-box.left+12;
  var y=(e.clientY||box.top+box.height/2)-box.top+12;
  x=Math.min(x, box.width-tip.offsetWidth-8);
  tip.style.left=Math.max(6,x)+"px"; tip.style.top=Math.max(6,y)+"px";
}
function hideTip(){ if(tip&&tip.parentNode) tip.parentNode.removeChild(tip); tip=null; }

function drawLegend(max){
  var el=document.getElementById("legend"), h=[];
  if (state.head!=="__ALL__"){
    h.push('<span class="key"><i class="dot" style="background:'+
      (mapColor[state.head]||NEUTRAL)+'"></i>'+esc(headLabel[state.head]||state.head)+'</span>');
  } else {
    D.map_heads.forEach(function(k){
      h.push('<span class="key"><i class="dot" style="background:'+mapColor[k]+
        '"></i>most often '+esc(headLabel[k])+'</span>');
    });
    h.push('<span class="key"><i class="dot" style="background:'+NEUTRAL+
      '"></i>other or none of those three</span>');
  }
  h.push('<span class="sizekey"><svg width="46" height="18" aria-hidden="true">'+
    '<circle cx="7" cy="12" r="4" fill="var(--s0)" fill-opacity=".55"></circle>'+
    '<circle cx="28" cy="10" r="8" fill="var(--s0)" fill-opacity=".55"></circle>'+
    '</svg>area &#8733; FIRs (max '+max.toLocaleString("en-IN")+')</span>');
  el.innerHTML=h.join("");
}

function drawList(){
  var q=state.q.toLowerCase();
  var rows=all.map(function(s){ return {s:s,n:countOf(s,state.month,state.head)}; })
    .filter(function(r){ return !q || r.s.name.toLowerCase().indexOf(q)>=0; })
    .sort(function(a,b){ return b.n-a.n || a.s.name.localeCompare(b.s.name); });
  document.getElementById("stations").innerHTML = rows.map(function(r){
    var d = state.head!=="__ALL__" ? state.head : dominant(r.s,state.month);
    var col = d?mapColor[d]:NEUTRAL;
    var un = r.s.lat===undefined ? ' <span class="n" title="no coordinates published">no location</span>' : '';
    return '<li><button type="button" data-n="'+esc(r.s.name)+'">'+
      '<span class="nm"><i class="dot" style="background:'+col+'"></i>'+
      '<span class="t">'+esc(r.s.name)+'</span>'+un+'</span>'+
      '<span class="n">'+r.n.toLocaleString("en-IN")+'</span></button></li>';
  }).join("") || '<li><button type="button" disabled>No station matches that.</button></li>';
  Array.prototype.forEach.call(document.querySelectorAll("#stations button[data-n]"),function(b){
    b.addEventListener("click",function(){ select(b.getAttribute("data-n")); });
  });
}

function select(name){
  state.sel = (state.sel===name)?null:name;
  draw(); drawDetail();
  var c=document.querySelector("circle.sel"); if(c) c.focus({preventScroll:true});
}

function drawDetail(){
  var t=document.getElementById("d-table"), hint=document.getElementById("d-hint"),
      title=document.getElementById("d-title");
  if(!state.sel){ t.hidden=true; hint.hidden=false; title.textContent="Breakdown"; return; }
  var st=all.filter(function(s){return s.name===state.sel;})[0];
  if(!st){ t.hidden=true; hint.hidden=false; return; }
  title.textContent=st.name;
  var b=breakdown(st,state.month);
  var rows=D.heads.filter(function(h){ return b[h.key] || h.withheld; });
  var max=Math.max.apply(null,D.heads.map(function(h){return b[h.key]||0;}).concat([1]));
  document.getElementById("d-body").innerHTML = rows.map(function(h){
    if (h.withheld){
      return '<tr class="withheld"><td class="c"></td><td>'+esc(h.label)+
        ' <span class="tagw">withheld</span></td><td class="n">&mdash;</td></tr>';
    }
    var n=b[h.key]||0;
    var col = mapColor[h.key] || NEUTRAL;
    return '<tr><td class="c"><i class="dot" style="background:'+col+'"></i></td>'+
      '<td>'+esc(h.label)+'<span class="bar" style="width:'+
      Math.round(100*n/max)+'%;background:'+col+';opacity:.5"></span></td>'+
      '<td class="n">'+n.toLocaleString("en-IN")+'</td></tr>';
  }).join("");
  t.hidden=false; hint.hidden=true;
}

function esc(s){ return String(s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }

// --- controls -------------------------------------------------------------
var mo=document.getElementById("f-month");
mo.innerHTML='<option value="__ALL__">All months held</option>'+
  D.months.map(function(m){
    var full=D.months_complete.indexOf(m)>=0;
    return '<option value="'+m+'">'+m+(full?" (complete)":" (partial)")+'</option>';
  }).join("");
mo.addEventListener("change",function(){ state.month=mo.value; draw(); drawDetail(); });

var hd=document.getElementById("f-head");
hd.innerHTML='<option value="__ALL__">All offence heads</option>'+
  D.map_heads.map(function(k){ return '<option value="'+k+'">'+esc(headLabel[k])+'</option>'; }).join("");
hd.addEventListener("change",function(){ state.head=hd.value; draw(); drawDetail(); });

var q=document.getElementById("f-q");
q.addEventListener("input",function(){ state.q=q.value.trim(); drawList(); });

// --- coverage & caveats ---------------------------------------------------
document.getElementById("coverage").innerHTML = D.months.map(function(m){
  var full=D.months_complete.indexOf(m)>=0;
  var p=D.months_partial[m];
  var note;
  if (full) note="verified against the portal&rsquo;s own count";
  else if (p && p.declared) note="got "+p.in_data+" of "+p.declared;
  else if (p && p.in_data < 25) note="stray records from an adjacent month&rsquo;s query";
  else note="fetched but not yet verified";
  return '<div class="covrow"><span class="m">'+m+'</span>'+
    '<span class="n" style="color:var(--muted);font-size:12px">'+note+'</span>'+
    '<span class="pill '+(full?"full":"part")+'">'+(full?"complete":"partial")+'</span></div>';
}).join("");

document.getElementById("cav").innerHTML = D.caveats.map(function(c){
  var titles={geography:"A station is not a scene",reporting:"This maps reporting, not crime",
    withheld:"Whole categories are missing by law",
    "law-change":"Two incompatible statute books",
    unplaced:"Some stations cannot be drawn",coverage:"Partial months are undercounts"};
  return '<li><b>'+esc(titles[c.kind]||c.kind)+'</b><span>'+esc(c.text)+'</span></li>';
}).join("");

document.getElementById("prov").innerHTML =
  "Source: <a href=\""+D.source.url+"\" target=\"_blank\" rel=\"noopener\">"+esc(D.source.name)+
  "</a>. "+esc(D.source.acknowledgement)+" Reproduced under the portal&rsquo;s copyright policy, which "+
  "permits reproduction where the source is prominently acknowledged. The published series begins "+
  esc(D.source.series_starts)+". "+
  D.records.toLocaleString("en-IN")+" FIRs held across "+D.months.length+" month(s); "+
  D.stations.length+" stations placed and "+D.unplaced.length+" listed without coordinates. "+
  "Station points come from the MHA all-India police station master, which publishes no telephone numbers, "+
  "so none are shown rather than invented. Built by <code>pipeline/build_mumbai_page.py</code>.";

draw(); drawDetail();
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
