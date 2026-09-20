# Bihar Police Geography — Supplementary Sources
_Agent: bihar-geography-extra · Researched: 2026-09-20 · Entries: 7 verified / 11 total_

Commissioned to resolve the residual `needs-review` rows in `data/spine/review_queue.csv`
(118 at briefing, **99** as of this check — `pipeline/crosswalk.py` was being improved
concurrently). The brief's hypothesis was that these are outposts (O.P.) sitting inside a
parent thana, or stations created after the boundaries were drawn.

## Executive summary

* **The decisive fact was already in `data/raw/`, not on the internet.** i-Bhugoal's
  `PS_Code` and the MHA point file's `ps_cd` are **the same national code space**.
  734 of 929 Bihar MHA stations have an exact-code twin among the 896 polygons, and on
  those 734 the name similarity is **median 1.000, mean 0.923**. `geography.py` already
  mints `thana_id = f"BH-{PS_Code}"`, so the join key is literally `BH-{ps_cd}`.
* Against the live 99-row queue, the code join **resolves 25 rows (25%)**, and they are
  precisely the class name-and-geometry cannot reach: transliteration
  (THAKRAHAN/THAKRAHA, CHANDAULI/CHANDAUTI, NAWA KOTHI/NAOKOTHI, MAJORGANJ/MEJARGANJ,
  MURKAHI/MORKHI, AMJHAUR/AMJHOR, GAOROL/GORAUL) and outright **translation**
  (AUDHYOGIK/INDUSTRIAL AREA, KHAGARIA/TOWN THANA, ASHOK PAPER MILLS/APM).
* **The code is a third witness, not an oracle.** It contradicts 6 of the 684 currently
  accepted mappings (0.9%) — see *The six collisions*. Treat it as evidence, not override.
* **The 89 outpost polygons are already in the 896.** i-Bhugoal carries `... OP` /
  `... O.P` polygons as first-class jurisdictions (BALIA O.P, TURKI OP, HALAI OP,
  MARIA OP). Outposts are **siblings, not children** — there is no nesting to resolve.
  The MHA point file names **zero** stations "OP", which is exactly why the names miss.
* **No outpost-to-parent-thana mapping exists in any reachable source.** Searched the
  whole ramSeraph catalogue, the LGD mirrors and ESRI/SOI. It does not exist openly.
* **There is no newer or alternative Bihar thana boundary set.** The authoritative layer
  catalogue (`indianopenmaps/worker/src/routes/listing.json`, 574 layers) lists exactly
  **one** Bihar police layer: `Bhugoal_BH_Police_Thana_Boundaries`. No outpost layer, no
  second vintage, no police-district layer. Bihar has 1 layer where Karnataka has 3.
* **Two new India-wide police-station point sets found and downloaded** (`SOI` 12,141 pts;
  `LivingAtlas` 14,984 pts). Both are disappointing for this problem: SOI has **no name
  field at all**, and LivingAtlas's 872 Bihar points carry free-text names with only 22
  marked chowki/outpost and an ESRI-internal `code` unrelated to `ps_cd`. Neither yields
  a parent mapping; LivingAtlas is a usable weak third geolocator.
* **Overpass and every OSM source are egress-blocked** — `overpass-api.de`,
  `overpass.kumi.systems`, `overpass.osm.ch`, `overpass.private.coffee`,
  `download.geofabrik.de`, `planet.openstreetmap.org` all fail CONNECT with proxy 403.
  Hunt item 3 could not be attempted at all.
* **LGD has no Bihar police-station entity.** LGD models "Police Station" as a
  *subdistrict type* only for Odisha (state 21), where the P.S. *is* the revenue unit.
  Bihar (state 10) subdistricts are Blocks/Circles. A village→thana rebuild from LGD is
  therefore impossible in principle, not merely blocked.
* Residual after the code join: **74 rows**. 19 carry codes numerically above every
  i-Bhugoal code in their district block (genuinely newer stations); 55 sit in gaps.
  They cluster in West Champaran (12) and East Champaran (12) — districts where MHA has
  11 and 10 more stations than i-Bhugoal has polygons.

## Source entries

### 1. i-Bhugoal `PS_Code` ↔ MHA `ps_cd` code concordance (derived finding)

Not a new download — a property of the two files already in `data/raw/`. Established by
parsing both in full.

```
id               bihar-geo-extra-bhugoal-ps-code-concordance
verification     VERIFIED_LIVE
bhugoal_codes    896      mha_bihar_codes  929
exact_intersect  734      (79.0% of MHA Bihar stations)
name_similarity  mean 0.923 / median 1.000 on the 734
agreement        678 of 684 currently-accepted crosswalk rows (99.1%)
join_key         thana_id == f"BH-{station.ps_cd_mha}"
```

**The six collisions** (code join disagrees with an accepted mapping):

| ps_cd | MHA name | currently accepted | code join says |
|---|---|---|---|
| 5793002 | KRISHNABRAHM | KARISHNA BARHAM | NAYABHOJPUR OP |
| 5130023 | Sahayak Thana | SHAYAK | SALMARI |
| 5118004 | Maranga | MARANGA | BALIA O.P |
| 5133001 | CHAKMAHESHI | CHAK MAHESI | MOHANPUR |
| 5133033 | Bangra | BANGRA | HALAI OP |
| 5123004 | NAGAR | NAGRA | SARAN NAGAR THANA |

Four of the six are cases where a same-named polygon exists *and* the coded polygon is an
outpost — i.e. the two agencies assigned the same number to different units, most likely
where an O.P. was upgraded or a thana split. **Where the name match is exact and the code
points elsewhere, keep the name.** The code should never silently overturn a `confirmed`.

### 2. SOI Police Stations (Survey of India) — DOWNLOADED

```
id               bihar-geo-extra-soi-police-stations
publisher        Survey of India, via ramSeraph/indian_facilities
url              https://github.com/ramSeraph/indian_facilities/releases/download/police-stations/SOI_PoliceStations.geojsonl.7z
local            data/raw/SOI_PoliceStations.geojsonl(.7z)   440,566 B → 5,979,974 B
features         12,141 India-wide · 608 in Bihar
fields           state, district, subdivision, lgd_state_code, lgd_district_code,
                 lgd_sub_dist_code, soi_code, unique_id, addl_info, remarks, svy_date
verification     VERIFIED_LIVE  (fetched, extracted, parsed)
licence          CC0-1.0 per repo LICENSE; attribute Datameet + Survey of India
```

**Has no station-name field of any kind.** `addl_info` is non-empty on 359 of 12,141 and
`remarks` on 674; neither is a name. Useless for resolving the 85. Its one virtue is
`lgd_sub_dist_code` on every point, which makes it a clean **subdistrict sanity layer**:
a Bihar police point whose LGD subdistrict disagrees with its assigned thana's subdistrict
is a coordinate to distrust. Survey of India vintage 2022-09-27 (file mtime).

### 3. ESRI LivingAtlas Police Stations — DOWNLOADED

```
id               bihar-geo-extra-livingatlas-police-stations
publisher        ESRI India LivingAtlas, via ramSeraph/indian_facilities
url              https://github.com/ramSeraph/indian_facilities/releases/download/police-stations/LivingAtlas_PoliceStations.geojsonl.7z
local            data/raw/LivingAtlas_PoliceStations.geojsonl(.7z)  359,091 B → 4,687,540 B
features         14,984 India-wide · 872 in Bihar across 38 districts
fields           policestationname, code, villgae [sic], subdistrict, district, state
verification     VERIFIED_LIVE  (fetched, extracted, parsed)
licence          CC0-1.0 asserted by mirror; ESRI LivingAtlas upstream terms UNCLEAR
```

Bihar name shapes: 692 contain "Station", 158 "other", **22** chowki/outpost. Names are
free text and inconsistent — `'Police Station'` with no place name at all, `'Bivha House
Police Camp'`, `'Police Station Baddi Op'`, `'Medni Chowki Ps'`. `code` is populated on
460/872 as `PS#####`, an **ESRI-internal id with no relation to `ps_cd`**. Carries
`villgae` (village) and `subdistrict`, which is the one genuinely new signal: it can place
a station in a village, and a village sits in exactly one thana.

Caveat: this is a compiled/crowd-derived layer. Do not let it outvote MHA or i-Bhugoal.

### 4. indianopenmaps layer catalogue — the instrument that closes hunt item 1

```
id               bihar-geo-extra-indianopenmaps-listing
url              https://github.com/ramSeraph/indianopenmaps  (worker/src/routes/listing.json)
verification     VERIFIED_LIVE  (cloned, parsed: 574 layer entries)
```

Every police layer published across all ramSeraph repos:

| state | layers |
|---|---|
| Bihar | `Bhugoal_BH_Police_Thana_Boundaries` **(one, ours)** |
| Karnataka | Police, Railway Police, Traffic Police station boundaries |
| Rajasthan | `Rajdharaa_RJ_Police_Thana_Boundary`, `Rajdharaa_RJ_GRP_Thana_Boundary` |
| Tamil Nadu | Police, Traffic Police station boundaries (TNGIS) |
| Telangana | `TRACGIS_TG_Police_Station_Boundaries` |
| Andhra Pradesh | `APSAC_Police_station_boundaries` |
| Delhi | `GSDL_DL_Police_Station_Boundaries` |
| marine (natl) | `NCOG_Marine_Police_Boundaries` |
| points (natl) | `SOI_PoliceStations`, `LivingAtlas_PoliceStations`, `MP_Police_Stations` |

Bihar source is recorded as `i-Bhugoal - https://gis.bih.nic.in/` (host blocked here).
Probed and **404**: `Bhugoal_BH_Police_District_Boundaries`, `..._OP_Boundaries`,
`..._Outpost_Boundaries`, `..._Range_Boundaries`, and every manifest name
(`listing.csv`, `index.json`, `manifest.json`, …). **There is nothing else for Bihar.**

### 5-8. LGD admin boundaries (ramSeraph/indian_admin_boundaries)

All four confirmed present with exact byte sizes; **not downloaded** (size, and none
resolves the 85).

| id | asset | bytes |
|---|---|---|
| `bihar-geo-extra-lgd-villages` | `villages/LGD_Villages.geojsonl.7z` | 350,561,734 |
| `bihar-geo-extra-lgd-subdistricts` | `subdistricts/LGD_Subdistricts.geojsonl.7z` | 59,849,479 |
| `bihar-geo-extra-lgd-blocks` | `blocks/LGD_Blocks.geojsonl.7z` | 60,893,264 |
| `bihar-geo-extra-lgd-districts` | `districts/LGD_Districts.geojsonl.7z` | 22,195,016 |

`verification: VERIFIED_LANDING` — HTTP 200 and full byte count observed, contents not
opened. Licence CC0-1.0 per repo LICENSE. These answer hunt item 5 (sanity-check geography)
and would pair with LivingAtlas's `villgae` field for a village-mediated join.

### 9. LGD full daily archive (ramSeraph/opendata) — BLOCKED

```
id               bihar-geo-extra-lgd-archive
landing          https://ramseraph.github.io/opendata/lgd/
access           blocked  (github.io egress-blocked; lgdirectory.gov.in blocked)
verification     CITED — repo master branch cloned and read; the data site itself not reachable
```

**Decisive negative:** read `lgd/wikidata/common.py`. LGD gives subdistricts a per-state
type, and `"Police Station"` appears **only under state code 21 (Odisha)**, with the note
*"Tehsils exist, Police station maps are available in the Census Atlas"*. Bihar (10) is
Blocks/Circles. **LGD contains no Bihar village→police-station mapping to mirror.** Hunt
item 4 is closed on the merits.

### 10. planemad/india-local-government-directory — LGD CSV mirror

```
id               bihar-geo-extra-planemad-lgd
url              https://raw.githubusercontent.com/planemad/india-local-government-directory/main/municipal-directory.csv
verification     VERIFIED_LIVE  (fetched 1,830,420 B, 22,912 rows, header parsed)
header           S.No, State Name, Localbody Code, Localbody Name, Census 2011 Code,
                 District Code, District Name, Subdistrict Code, Subdistrict Name,
                 Village Code, Village Name
```

Urban-local-body → village mapping. No police column; its own README defers to the
ramSeraph LGD dump. Useful only as a village-code lookup.

### 11. OpenStreetMap Bihar `amenity=police` — BLOCKED, NOT ATTEMPTED

```
id               bihar-geo-extra-osm-overpass
access           blocked
verification     UNVERIFIED
```

Every endpoint fails CONNECT with proxy 403: `overpass-api.de`,
`overpass.kumi.systems`, `overpass.osm.ch`, `overpass.private.coffee`,
`download.geofabrik.de`, `osm-internal.download.geofabrik.de`,
`planet.openstreetmap.org`. **No OSM data was obtained and no claim about OSM content is
made here.** This remains the best untried lead — see Phase 2.

## Granularity reality check

| layer | unit | count (Bihar) | vintage | refresh |
|---|---|---|---|---|
| i-Bhugoal thana polygons | jurisdiction polygon | 896 (89 are O.P.) | one-off snapshot | never re-released |
| MHA station points | point | 929 | one-off | never |
| SOI police points | point, **unnamed** | 608 | 2022-09 | one-off |
| LivingAtlas police points | point + free-text name | 872 | 2025-01 | irregular |
| LGD villages | polygon | national | daily upstream | blocked here |

The gap: we want a current, authoritative thana jurisdiction layer with an outpost→parent
relation. What exists is one undated snapshot in which outposts are siblings and the
relation is simply absent.

## Blockers and how to get past them

1. **All `.gov.in`/`.nic.in` blocked** — `gis.bih.nic.in` (i-Bhugoal itself),
   `lgdirectory.gov.in`, `police.bihar.gov.in`. Not routed around.
2. **`github.io` blocked** — costs us the ramSeraph LGD dump and the india-geodata
   catalogue page. The underlying git repos *are* reachable, which is how item 9 was
   answered anyway.
3. **`api.github.com` and repo HTML blocked (403)** for non-attached repos.
   Reachable GitHub surface is exactly: `raw.githubusercontent.com`,
   `github.com/*/releases/download/*` (redirects to `release-assets.githubusercontent.com`),
   and anonymous `git clone`. Release *assets* therefore cannot be enumerated — only
   probed by name. The way through is `git clone` of the repo that *indexes* the
   releases (`indianopenmaps`), which is how the complete police layer list was obtained.
4. **All OSM egress blocked.**

## Seed Leads (unconfirmed but probably real)

* **Bihar Police SHO/contact directory.** A "SHO UPDATE" PDF listing Bihar police stations
  *with O.P. entries under their parent thana* is indexed on Scribd (search result only,
  not fetched — Scribd needs a session). Patna district pages list e.g. "Samiyagarh O.P.",
  "Neura OP". A district-by-district scrape of the 38 `<district>.nic.in/police-stations/`
  pages would very likely reconstruct the parent mapping. Blocked here (`.nic.in`).
  **This is the single highest-value unblocked-elsewhere lead.**
* **CCTNS/ICJS station master.** The registry MHA's `ps_cd` comes from. It necessarily
  contains a station-type flag (PS vs OP) and a parent. RTI to Bihar Police SCRB for
  "the CCTNS police-station master for Bihar: ps_cd, name, type, parent station, district".
* **Bihar Police Gazette / Home Dept notifications** creating new thanas since the
  i-Bhugoal snapshot — would date the 19 numerically-newer codes and name their parents.
* **Bihar Police Association / district annual reports** often tabulate "Thana: N,
  O.P.: M" per district, which would at least validate the 89 O.P. count.

## Phase 2 recommendations — how to resolve the 99

Ranked by evidence-per-unit-of-work.

**1. Add `ps_cd == PS_Code` as a third witness in `crosswalk.py`. Resolves 25 of 99. Zero new data.**

The key already exists: `geography.py:216` mints `thana_id = f"BH-{PS_Code}"` and
`geography.py:257` keeps `ps_cd_mha`. So:

```python
by_code = f"BH-{station['ps_cd_mha']}" if f"BH-{station['ps_cd_mha']}" in thanas else None
```

Grade it as a new tier, e.g. `code-join`, and place it in the rule ladder as:

* accept when `by_code` is present **and** `thanas[by_code]["district"] == station district`
  (24 of the 25 satisfy this; the 1 that does not must stay in review);
* promote to a stronger tier when `by_code == by_geometry` (8 of the 25 — double-witnessed);
* **never** let `by_code` overturn a `confirmed` or a ≥0.90 name match — emit a
  `code-conflict` flag instead, which will surface exactly the six collisions above for a
  human. Those six are real information: they are probably O.P.-upgrade events.

This is consistent with the module's existing philosophy — a third independent witness,
graded, arguable, and never a silent override.

**2. Mark the outpost polygons and stop treating them as ordinary thanas. Costs one regex.**

89 of the 896 polygons are `... OP` / `... O.P`. Add `is_outpost` to the thana record in
`geography.py`. Two immediate payoffs: (a) strip the `OP` token before name comparison, so
`TURKI OP`↔`Turki Khararu` and `BALIA O.P`↔`Maranga` stop being scored as 0.5 mismatches;
(b) the map can render an outpost distinctly rather than implying it is a full thana.

**3. Accept the residual 74 as genuinely unresolvable from current data — and say so on the map.**

19 have codes above every i-Bhugoal code in their district (post-snapshot stations); 55 sit
in code gaps; 3 fall outside every polygon. No reachable source can place them. The honest
product move is to keep them unmapped and publish the count, per the module's own
"a confident wrong join looks like a dangerous neighbourhood" principle. Their crime should
roll up to district level, not be attributed to a neighbour's polygon.

**4. Village-mediated join as a tie-breaker for the 74 (LivingAtlas + LGD villages).**

LivingAtlas gives 872 Bihar stations a `villgae` and `subdistrict`. `LGD_Villages` gives
village polygons. A station whose LivingAtlas village polygon lies wholly inside one thana
is weak corroboration for that thana. Cost: 350 MB download plus a fuzzy
LivingAtlas↔MHA name/district match. Do this only after 1-3, and only as a
`needs-review` *proposal*, never an auto-accept — LivingAtlas is crowd-derived.

**5. OSM, when egress permits.** Unattempted, not unpromising: OSM Bihar
`amenity=police` with `name`/`official_name`/`operator` frequently spells outposts as
"X Outpost (Y Thana)". Retry `overpass-api.de`, or take the Geofabrik
`asia/india-latest.osm.pbf` and filter. Would also independently test the ~3% of MHA
coordinates believed wrong.

**6. RTI / district-site scrape for the parent mapping.** The only route to a real
outpost→parent table. See Seed Leads.

## How this plugs into `pipeline/geography.py`

Nothing here changes the spine's inputs. The two downloaded point sets are **additive
witnesses**, not replacements for `INDIA_POLICE_STATIONS.geojson`:

* `data/raw/SOI_PoliceStations.geojsonl` — filter `state == "BIHAR"` (608). Join nothing by
  name (there is none). Use `lgd_sub_dist_code` to flag thana assignments whose subdistrict
  disagrees, i.e. a QA pass over `district_conflicts`.
* `data/raw/LivingAtlas_PoliceStations.geojsonl` — filter `state == "Bihar"` (872). Fuzzy
  match `policestationname` × `district` against `bihar_stations.csv`; where it matches,
  carry `villgae` and the second coordinate. Feed to `crosswalk.py` as a proposal column in
  `review_queue.csv` only.

The change that actually resolves rows is in `crosswalk.py`, not `geography.py`:
recommendation 1 above. `geography.py` already carries both halves of the key
(`ps_code_bhugoal` on thanas, `ps_cd_mha` on stations) — the join was there all along.
