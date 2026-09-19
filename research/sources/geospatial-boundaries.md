# Geospatial Boundaries & Geocoding Infrastructure for India
_Agent: geospatial-boundaries · Researched: 2026-09-19 · Entries: 12 verified / 34 total_

## Executive summary

- **Police-station jurisdiction polygons DO exist in India — but only for 7 states/UTs + a marine layer, not nationally.** Verified asset list: **Andhra Pradesh (APSAC), Bihar (i-Bhugoal), Delhi (GSDL), Karnataka (KGIS), Rajasthan (Rajdharaa), Tamil Nadu (TNGIS), Telangana (TRACGIS)**, plus `NCOG_Marine_Police_Boundaries`. Karnataka, Tamil Nadu and Rajasthan additionally publish **separate traffic / railway / GRP jurisdiction layers**, so a single location sits inside 2–3 overlapping police jurisdictions. Everything is `.geojsonl.7z` at `github.com/ramSeraph/indian_admin_boundaries/releases/tag/police`, re-packaged as Parquet/PMTiles by `yashveeeeeeer/india-geodata` under CC0. Those 7 states hold roughly a third of India's population. **The other 29 states/UTs have no published thana polygon.**
- **All-India police-station POINTS do exist and are excellent.** I downloaded and parsed `INDIA_POLICE_STATIONS.geojson` (5.27 MB): **16,459 point features, 100% populated, zero null/zero coordinates, zero points outside the India bbox, 36 states/UTs**. Every feature carries `state_cd`, `district_c`, `ps_cd`, `ps`, `district`, `state`. The GeoServer feature ids are `police_station_mha.N` — **this is a Ministry of Home Affairs station master**, i.e. almost certainly the same `ps_cd` namespace used by CCTNS/ICJS. **`ps_cd` is the single most valuable join key found in this entire domain.**
- The MHA codes are a clean hierarchy — `district_c = state_cd*1000 + d`, `ps_cd = district_c*1000 + p` — and it **holds for 15,616 of 16,459 stations (94.9%)**. The 843 failures are *direct evidence of district reorganisation*: e.g. stations in AP's new (2022) Alluri Sitharama Raju district carry `district_c=2057` but retain `ps_cd=2017xxx` from their pre-split parent. Treat `ps_cd` as an immutable station id and `district_c` as mutable.
- **District reorganisation is the defining data problem.** India had **640 districts at Census 2011** and has **~800 as of December 2025** — a 25% increase. 2011 census geography ≠ 2024 administrative geography ≠ police-district geography (the MHA file has **983 distinct police district codes** against ~800 revenue districts, because commissionerates and railway districts are separate).
- **Denominators are stale and will stay stale until 2027.** The 2021 census never happened. Houselisting for the delayed census runs **1 Apr – 30 Sep 2026** (i.e. *now*), population enumeration **9–28 Feb 2027**, with caste enumeration for the first time since 1931. Until then every per-capita crime rate must use projected 2011 populations, and that projection error is larger than most of the crime variation we will be mapping.
- **Legal constraint on the basemap is explicit and quotable.** Geospatial Guidelines 2021, clause xiii: *"For political Maps of India of any scale including national, state and other boundaries, SoI published maps or SoI digital boundary data are the standard to be used… Others may publish such maps that adhere to these standards."* A raw OSM or Mapbox basemap does **not** depict J&K/Aksai Chin/Arunachal the way SoI does. We must overlay an SoI-derived national/state boundary layer on whatever tiles we use.
- **Google Maps Platform is legally unusable for this product, and I have the verbatim clauses.** §3.2.3(c)(iv) forbids *"use latitude/longitude values from the Places API as an input for point-in-polygon analysis"* — which is precisely what a crime map does. §3.2.3(e) *No Use With Non-Google Maps* forbids using Core Services "with or near a non-Google Map". §3.2.3(a) forbids pre-fetching/storing/rehosting geocodes; §3.2.3(b) forbids caching beyond the Service Specific Terms, which permit only **30 consecutive calendar days** for Address Validation lat/long. Conclusion: geocode with self-hosted Nominatim/Photon over an OSM India extract, or licence Mappls.
- **DIGIPIN is a genuine gift.** India Post's official repo `INDIAPOST-gov/digipin` is **Apache-2.0, self-hostable Node/Express**, exposing `GET /api/digipin/encode?latitude=&longitude=` and `GET /api/digipin/decode?digipin=`. A deterministic 4 m × 4 m grid code, no API key, no rate limit, no ToU. Use it as the internal privacy-safe location primitive.
- **Finest spatial granularity actually achievable: police-station jurisdiction polygon in 7 states; police-station point (16,459, all-India) everywhere; municipal ward in 27–28 cities; village/LGD polygon nationally.** Address-level street crime as on police.uk is not achievable from published Indian data.
- **Single biggest blocker:** the absence of thana polygons for 29 states/UTs. The workaround is Voronoi-on-points-clipped-to-police-district, which is defensible but must never be labelled as an official jurisdiction.
- **The reconstruction route that would actually solve it:** village-to-thana mapping tables. LGD gives every village a stable code and india-geodata/ramSeraph give village polygons; if a state police force's "villages under each PS" list can be obtained (many exist as PDFs on state police sites, and all exist internally for CCTNS), dissolving village polygons by thana yields *exact* jurisdiction boundaries rather than approximations.

## Source entries

### 1. india-geodata (aggregated mirror) — the fastest route to everything
The single most useful artefact found. A CC-BY-4.0 unified repackaging of ~1,800 files across 14 collections: administrative (country→state→district→subdistrict→block→panchayat→village→habitation, ~27 GB), electoral, census (2011 + historical districts), postal/pincode (~700 MB), urban wards (~430 MB), police (~101 MB), Survey of India index maps, plus links to SHRUG. Everything in Parquet + PMTiles + GeoJSONL.7z, EPSG:4326. PMTiles matters: we can serve boundary tiles straight from object storage with no tile server.

```
id: geo-india-geodata
publisher: yashveeeeeeer (community aggregation of government sources)
tier: 4 | geo_coverage: all-India | geo_granularity: village
unit_of_record: boundary-polygon | time_start: 1941 | time_latest: 2026
cadence: irregular | lag: varies | taxonomy: n/a
formats: [Parquet, PMTiles, GeoJSONL, SHP, GeoJSON, TopoJSON, KML, CSV, GeoTIFF]
access: open-download | machine_readable: 5 | license: CC-BY-4.0 (per-dataset metadata.json)
ingest_difficulty: 2 | priority: 5 | verification: VERIFIED_LIVE | checked_on: 2026-09-19
evidence: Read top-level README + 10 sub-dataset READMEs + data/police/metadata.json via
  raw.githubusercontent.com. Downloaded and parsed one full dataset (16,459 features).
urls.landing: https://github.com/yashveeeeeeer/india-geodata
urls.data: https://yashveeeeeeer.github.io/india-geodata  (EGRESS-BLOCKED to me; repo readable)
caveats: [third-party mirror not an authority, per-dataset licences vary and some are CC0
  asserted over material whose upstream licence is unstated, vintages differ by layer,
  large files are GitHub Release assets not repo files]
```

### 2. Police station jurisdiction boundaries (7 states + marine) — THE CENTRAL FINDING
Verified asset inventory from the release page:

| State/region | Asset | Upstream authority |
|---|---|---|
| Andhra Pradesh | `APSAC_Police_station_boundaries.geojsonl.7z` | AP State Applications Centre |
| Bihar | `Bhugoal_BH_Police_Thana_Boundaries.geojsonl.7z` | i-Bhugoal (Bihar) |
| Delhi | `GSDL_DL_Police_Station_Boundaries.geojsonl.7z` | Geospatial Delhi Limited |
| Karnataka | `KGISMAPS_KN_Police_Station_Boundaries.geojsonl.7z` (+ `_Railway_`, `_Traffic_`) | Karnataka GIS |
| Rajasthan | `Rajdharaa_RJ_Police_Thana_Boundary.geojsonl.7z` (+ `_GRP_`) | Rajdharaa |
| Tamil Nadu | `TNGIS_TN_Police_Station_Boundaries.geojsonl.7z` (+ `_Traffic_`) | TN GIS |
| Telangana | `TRACGIS_TG_Police_Station_Boundaries.geojsonl.7z` | Telangana GIS |
| Marine/coastal | `NCOG_Marine_Police_Boundaries.geojsonl.7z` | National Centre for Geo-Informatics |

```
id: geo-police-station-jurisdictions
publisher: State GIS agencies (APSAC, i-Bhugoal, GSDL, KGIS, Rajdharaa, TNGIS, TRACGIS, NCOG)
tier: 2 | geo_coverage: AP, BR, DL, KA, RJ, TN, TG + Indian marine zones
geo_granularity: police-station | unit_of_record: boundary-polygon
time_start: unknown | time_latest: 2024 (metadata.json last_updated 2024-08-15)
cadence: irregular | lag: unknown | taxonomy: n/a
formats: [GeoJSONL, Parquet, PMTiles, SHP] | access: open-download
machine_readable: 5 | license: CC0-1.0 as asserted by mirror; upstream state portal ToU unstated
ingest_difficulty: 2 | priority: 5 | verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: Release page github.com/ramSeraph/indian_admin_boundaries/releases/tag/police lists the
  13 assets above with per-state attribution; india-geodata data/police/README.md independently
  tabulates the same 8 sources and states "Polygon boundaries for 8 states/regions, ~36 files,
  ~96 MB". Archives not decompressed (feature counts unverified).
urls.data: https://github.com/ramSeraph/indian_admin_boundaries/releases/tag/police
urls.landing: https://github.com/yashveeeeeeer/india-geodata/tree/main/data/police
caveats: [only 7 of 36 states/UTs, vintage differs per state and is undocumented, traffic/railway/GRP
  jurisdictions OVERLAP territorial ones so a naive point-in-polygon returns multiple hits,
  CC0 assertion is the mirror's not the states', no published crosswalk from these polygons to
  MHA ps_cd so names must be fuzzy-matched, boundaries change on thana bifurcation with no changelog]
how_to_obtain: gh release download police --repo ramSeraph/indian_admin_boundaries
```

### 3. MHA all-India police station points (16,459) — the join key
The highest-value single file in this dossier. Parsed in full.

```
id: geo-mha-police-station-points
publisher: Ministry of Home Affairs (served via NIC/Bhuvan-class GeoServer; mirrored on GitHub)
tier: 2 | geo_coverage: all-India (36 states/UTs) | geo_granularity: police-station
unit_of_record: point | time_start: unknown | time_latest: 2024-ish | cadence: irregular
formats: [GeoJSON] | access: open-download | machine_readable: 5 | license: unstated (mirror CC0)
ingest_difficulty: 1 | priority: 5 | verification: VERIFIED_LIVE | checked_on: 2026-09-19
evidence: Downloaded 5,269,146 bytes. 16,459 Point features. Schema
  [state, state_cd, district, district_c, ps, ps_cd, latitude, longitude], all 100% non-null.
  36 distinct state_cd, 983 distinct district_c, 964 distinct district names, 16,459 unique ps_cd,
  14,647 distinct station names. bbox lat 7.01653–34.84755, lon 68.53847–97.006616. 0 zero-coords,
  0 out-of-bbox. Feature ids are "police_station_mha.N". Largest: TN 2427, UP 1713, MP 1110,
  MH 1086, KA 1046, AP 1031, BR 929, TG 821. Code hierarchy holds for 15,616/16,459.
urls.data: https://raw.githubusercontent.com/yashveeeeeeer/india-geodata/main/data/police/stations/INDIA_POLICE_STATIONS.geojson
caveats: [state_cd is the MHA/NCRB alphabetical series (1=A&N, 2=AP, 29=TN, 37=TG) and is NOT the
  Census 2011 state code (AP=28, TN=33) — a crosswalk is mandatory; code 9 and 36 are absent;
  843 stations carry a ps_cd whose embedded district code contradicts their current district_c,
  i.e. stale post-reorganisation codes; 14,647 names for 16,459 stations means names are NOT unique
  even within a state so never join on name alone; Assam 324 and West Bengal 452 look low vs
  published force strength, so coverage is probably incomplete for some states; no timestamp field;
  coordinates are station buildings, not jurisdiction centroids]
```

### 4. Police station points — alternative/corroborating sources
`SOI_PoliceStations.geojsonl.7z` (Survey of India, via indiamaps.gov.in), `LivingAtlas_PoliceStations.geojsonl.7z` (Esri LivingAtlas India), `MP_Police_Stations.geojsonl.7z` (Madhya Pradesh Police, mppolice.gov.in). Release notes state CC0-1.0 with attribution requested to DataMeet and the originating government source. Use these to cross-validate MHA coordinates and to fill states where MHA looks thin.

```
id: geo-soi-livingatlas-police-points | publisher: Survey of India / Esri India / MP Police
tier: 2 | geo_coverage: all-India (SOI, LivingAtlas) + Madhya Pradesh | geo_granularity: point
unit_of_record: point | formats: [GeoJSONL, PMTiles] | access: open-download | machine_readable: 5
license: CC0-1.0 (as stated in release notes) | ingest_difficulty: 2 | priority: 3
verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: Release github.com/ramSeraph/indian_facilities/releases/tag/police-stations lists the three
  assets with per-source attribution and vector-tile endpoints. Archives not opened.
caveats: [no ps_cd on SOI/LivingAtlas layers so they cannot be joined to crime data directly,
  Esri LivingAtlas redistribution terms may differ from the CC0 assertion, unknown vintage]
```

### 5. LGD — Local Government Directory (the master geography spine)
The canonical registry of state/district/subdistrict/block/panchayat/village codes, MoPR. **Direct access was EGRESS-BLOCKED to me.** However, LGD-derived polygon layers are verified to exist downstream: `LGD_Districts.{parquet,pmtiles,geojsonl.7z}` and `LGD_Villages.{...}` in india-geodata, and `ramSeraph/opendata/lgd/` contains the scraping toolchain with a published mirror.

```
id: geo-lgd | publisher: Ministry of Panchayati Raj | tier: 1
geo_coverage: all-India | geo_granularity: village | unit_of_record: boundary-polygon
time_start: 2010s | time_latest: current (continuously updated) | cadence: irregular (near-continuous)
formats: [HTML, CSV, Parquet, PMTiles, GeoJSONL] | access: scrape | machine_readable: 3
license: unstated (GoI portal, likely GODL-India) | ingest_difficulty: 3 | priority: 5
verification: CITED | checked_on: 2026-09-19
evidence: Could not fetch lgdirectory.gov.in (egress policy). Existence and structure confirmed
  from two independent verified sources: india-geodata data/administrative/{districts,villages}/README.md
  name LGD_Districts and LGD_Villages release assets attributed to "Local Government Directory,
  Ministry of Panchayati Raj"; ramSeraph/opendata README documents "lgd/ - Code for pulling data from
  Local Government Directory (https://lgdirectory.gov.in)" with a data mirror.
urls.landing: https://lgdirectory.gov.in  (unverified by me)
urls.data: https://github.com/ramSeraph/opendata/tree/master/lgd
how_to_obtain: LGD exposes report/export pages rather than a documented REST API. Use the
  ramSeraph/opendata/lgd scraper, or its published mirror, rather than writing a new scraper.
caveats: [LGD codes change when units are created/merged and LGD does not version history well —
  keep your own validity intervals; LGD is a CODE REGISTRY, the geometry attached to it downstream
  comes from SOI/Bhuvan and the code-to-geometry join quality is unverified; LGD village names
  differ in transliteration from Census 2011 names]
```

### 6. Census of India 2011 boundaries + Town/Village Directory
`Census_Villages`, `Districts_2011`, `SubDistricts_2011`, and `PC11_TV_DIR.csv.7z` (Town & Village Directory) — release tag `census/2011`, ~20 files, ~1 GB. DataMeet additionally holds census-2001 and census-2011 district shapefiles in-repo.

```
id: geo-census-2011-boundaries | publisher: Registrar General & Census Commissioner of India
tier: 1 | geo_coverage: all-India | geo_granularity: village | unit_of_record: boundary-polygon
time_start: 2011 | time_latest: 2011 | cadence: one-off | lag: n/a
formats: [Parquet, PMTiles, GeoJSONL, CSV, SHP] | access: open-download | machine_readable: 5
license: CC0 asserted by mirror; censusindia.gov.in ToU unverified | ingest_difficulty: 2
priority: 5 | verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: india-geodata data/census/census-2011/README.md tabulates the 8 datasets, release tag and
  ~1 GB total; data/administrative/districts/README.md confirms in-repo census-2001 and census-2011
  DataMeet shapefiles. censusindia.gov.in itself was EGRESS-BLOCKED.
caveats: [640 districts — 160 fewer than today; PC11 codes are a different namespace from LGD codes
  AND from MHA state_cd; 2011 population is a 15-year-old denominator; J&K geometry predates the
  2019 reorganisation into J&K and Ladakh UTs]
```

### 7. Census 2027 (the next denominator)
2021 census never conducted (COVID). Houselisting **1 Apr – 30 Sep 2026** (Himalayan regions Aug–Sep 2026); population enumeration **9–28 Feb 2027**; first caste enumeration since 1931; digital collection with self-enumeration; will be the basis for delimitation and women's reservation.

```
id: geo-census-2027 | publisher: RGI/ORGI, MHA | tier: 1 | geo_coverage: all-India
geo_granularity: village | unit_of_record: aggregate-count | time_start: 2026 | time_latest: 2027
cadence: one-off | lag: expect 12-24 months post-enumeration for microdata/boundaries
formats: [PDF, XLSX, CSV] | access: open-download (when published) | machine_readable: 2
license: unknown | ingest_difficulty: 3 | priority: 4 | verification: CITED | checked_on: 2026-09-19
evidence: en.wikipedia.org/wiki/Census_of_India gives the phase dates and confirms 2021 was postponed.
caveats: [until 2027-28 every rate we publish uses projected 2011 populations; the boundary freeze
  date matters enormously — new districts created after the freeze will not appear in census outputs;
  a NEW set of 2027 census codes will arrive and break every 2011-keyed join]
```

### 8. Historical district boundaries + district-change ledger (the reorg solver)
Release tag `census/historical`: `India-State-Districts-{1941,1951,1961,1971,1981,1991,2001}` (21 release files) plus **four in-repo CSVs**: `District_Timeseries_1951-2024.csv`, `District_splits_and_carveouts_1951_to_2024.csv`, `New_districts_created_1951_to_2024.csv`, `District_name_changes_1951_to_2021.csv`. Sourced from India State Stories (FLAME University), census records and gazette notifications. **This is the closest thing to an authoritative district crosswalk that exists publicly.**

```
id: geo-historical-districts | publisher: FLAME University (India State Stories) / Census of India
tier: 4 | geo_coverage: all-India | geo_granularity: district | unit_of_record: boundary-polygon
time_start: 1941 | time_latest: 2024 | cadence: irregular | formats: [Parquet, PMTiles, GeoJSONL, CSV]
access: open-download | machine_readable: 5 | license: CC0 | ingest_difficulty: 2 | priority: 5
verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: data/census/historical/README.md lists the 4 CSVs by exact filename, the 7 decadal polygon
  years, "21 release files + 4 in-repo CSV files", and cites indiastatestory.in/datadownloads.
urls.landing: https://www.indiastatestory.in/datadownloads (cited, unverified by me)
caveats: [polygons stop at 2001 — the 2001→2026 period, which is when most splits happened, is
  covered only by the CSV ledger not by geometry; CSV ends 2024 and districts have been created since;
  no LGD or PC11 codes guaranteed on the CSVs — verify before relying on an automated join]
```

### 9. SHRUG — Socioeconomic High-resolution Rural-Urban Geographic Platform
Development Data Lab (Asher/Novosad). 500,000+ villages, 8,000+ towns, 1991–present, unified by the **`shrid`** — a village/town unit with *consistent boundaries since 1991*, built by aggregating units that split or merged. Modules: Population Census 1991/2001/2011, Economic Census, SECC 2012, nightlights 1992–2021, elections, PMGSY, bank branches, **open polygons (2011)**. Available at village, town, subdistrict, district and constituency level.

```
id: geo-shrug | publisher: Development Data Lab | tier: 4 | geo_coverage: all-India
geo_granularity: village | unit_of_record: boundary-polygon | time_start: 1991 | time_latest: 2021
cadence: irregular | formats: [CSV, Stata, SHP, Parquet, PMTiles] | access: open-download (registration)
machine_readable: 4 | license: CC-BY-NC-SA-4.0 | ingest_difficulty: 2 | priority: 4
verification: CITED | checked_on: 2026-09-19
evidence: devdatalab.org was EGRESS-BLOCKED. Content, shrid definition, module list, licence and
  citation confirmed from india-geodata data/external/shrug/README.md, and shrug-village-pc11 /
  shrug-subdistrict-pc11 / shrug-district-pc11 appear as release assets under tag census/2011.
urls.data: https://www.devdatalab.org/shrug_download/  urls.docs: https://docs.devdatalab.org/
caveats: [**CC-BY-NC-SA 4.0 — NON-COMMERCIAL ONLY.** If the crime portal is ever monetised or is
  deemed commercial, SHRUG cannot be used without written permission from DDL. ShareAlike may also
  infect derived layers. Get a licensing decision BEFORE building shrid into the spine.
  Also: shrid is a research unit, not an administrative one, so it is not a display geography.]
```

### 10. Survey of India — the legal authority on boundaries
SoI is statutorily responsible for "scrutiny and certification of external boundaries of India and Coastline on maps published by other agencies" and for the naming/spelling of geographical features. Historically topographic maps were sale-restricted to Indian citizens with export prohibited; liberalised from **15 February 2021**. `indiamaps.gov.in` is its public map portal; `onlinemaps.surveyofindia.gov.in` is the download portal (ramSeraph/opendata has a puller for it). india-geodata carries SoI index grids (1:1M, 1:250K, 1:50K), outline maps and `SOI_Districts`/`SOI_Villages`/`SOI_VILLAGE_POINT` layers.

```
id: geo-survey-of-india | publisher: Survey of India, Dept of Science & Technology | tier: 1
geo_coverage: all-India | geo_granularity: village | unit_of_record: boundary-polygon
time_start: unknown | time_latest: current | cadence: irregular
formats: [SHP, PDF, Parquet, PMTiles, GeoJSONL] | access: open-download | machine_readable: 4
license: CC-BY-4.0 (index maps via DataMeet); SoI open data terms otherwise | ingest_difficulty: 3
priority: 5 | verification: CITED | checked_on: 2026-09-19
evidence: surveyofindia.gov.in EGRESS-BLOCKED. Role/authority and the 2021 liberalisation date from
  en.wikipedia.org/wiki/Survey_of_India. Layer inventory from india-geodata
  data/survey-of-india/README.md and data/administrative/{districts,villages}/README.md.
  indiamaps.gov.in named as the SOI police-station source in ramSeraph/indian_facilities release notes.
caveats: [**SoI boundaries are the only legally safe depiction of J&K/Ladakh/Arunachal for a map
  published in India** — see entry 12; SoI village polygons and LGD village codes are separate
  datasets whose join is not guaranteed 1:1]
```

### 11. Geospatial Guidelines 2021 — what is now releasable, and the boundary mandate
The February 2021 guidelines removed prior-approval requirements for Indian entities collecting/ storing/ publishing geospatial data, with threshold and foreign-entity conditions. **Clause xiii, quoted verbatim from a verified source:**

> "For political Maps of India of any scale including national, state and other boundaries, SoI published maps or SoI digital boundary data are the standard to be used, which shall be made easily downloadable for free and their digital display and printing shall be permissible. Others may publish such maps that adhere to these standards."

```
id: geo-geospatial-guidelines-2021 | publisher: Dept of Science & Technology, GoI | tier: 3
geo_coverage: all-India | geo_granularity: national | unit_of_record: narrative-document
time_start: 2021-02-15 | time_latest: 2021 | cadence: one-off | formats: [PDF] | access: open-download
machine_readable: 1 | license: GoI | ingest_difficulty: 1 | priority: 5
verification: CITED | checked_on: 2026-09-19
evidence: dst.gov.in EGRESS-BLOCKED. Clause xiii reproduced verbatim in the README of
  github.com/ramSeraph/indian_admin_boundaries, which I fetched and read, with the PDF URL cited.
urls.docs: https://dst.gov.in/sites/default/files/Final%20Approved%20Guidelines%20on%20Geospatial%20Data_0.pdf
caveats: [I read the clause quoted in a third-party README, not the gazette PDF — have counsel verify
  against the original before launch; the guidelines also impose accuracy thresholds and
  foreign-entity restrictions that I could NOT verify and that a lawyer must read directly]
```

### 12. National Geospatial Policy 2022
Successor policy framing India's geospatial knowledge stack; DIGIPIN explicitly claims compliance with it. PDF hosted on surveyofindia.gov.in.
```
id: geo-national-geospatial-policy-2022 | publisher: Dept of Science & Technology / Survey of India
tier: 3 | geo_coverage: all-India | geo_granularity: national | unit_of_record: narrative-document
time_start: 2022 | time_latest: 2022 | cadence: one-off | formats: [PDF] | access: open-download
machine_readable: 1 | license: GoI | ingest_difficulty: 1 | priority: 3 | verification: CITED
checked_on: 2026-09-19
evidence: URL cited in india-geodata top-level README legal notice; INDIAPOST-gov/digipin README
  states DIGIPIN "Complies with the National Geospatial Policy 2022". PDF not opened (host blocked).
urls.docs: https://www.surveyofindia.gov.in/webroot/UserFiles/files/National%20Geospatial%20Policy.pdf
```

### 13. Bhuvan / NRSC / ISRO
Bhuvan is the national geoportal. `bhuvan_districts`, `bhuvan_villages` and **`Bhuvan_JK_Villages`** (Jammu & Kashmir village boundaries specifically) are verified as release assets in india-geodata. NRSC is also a DIGIPIN co-developer. Bhuvan historically exposes WMS/WFS and a registration-gated download portal.
```
id: geo-bhuvan | publisher: NRSC/ISRO | tier: 1 | geo_coverage: all-India | geo_granularity: village
unit_of_record: boundary-polygon | time_start: unknown | time_latest: current | cadence: irregular
formats: [SHP, Parquet, PMTiles, GeoJSONL, WMS] | access: login (portal) / open-download (mirror)
machine_readable: 4 | license: unstated | ingest_difficulty: 3 | priority: 3
verification: CITED | checked_on: 2026-09-19
evidence: bhuvan.nrsc.gov.in EGRESS-BLOCKED. Layers confirmed by name in india-geodata
  data/administrative/{districts,villages}/README.md attributed to "Bhuvan (ISRO)".
urls.landing: https://bhuvan.nrsc.gov.in
how_to_obtain: Bhuvan download requires free account registration; WMS/WFS endpoints are open.
caveats: [Bhuvan J&K village layer exists separately from the main village layer — a sign the
  national layer excludes J&K; registration-gated bulk download]
```

### 14. Bharatmaps / State GIS Portals (NIC) — where the thana polygons come FROM
NIC's multi-layer GIS platform with NICMAPS base at 1:50,000 from SoI/ISRO/FSI/RGI, ~23 layers. `stategisportal.nic.in/stategisportal/Home/State/{code}` gives per-state portals. **This is the upstream that the 7 states' police jurisdiction layers were harvested from**, and therefore the place to look for the missing 29 states.
```
id: geo-bharatmaps-stategisportal | publisher: National Informatics Centre | tier: 2
geo_coverage: all-India (per-state portals) | geo_granularity: police-station
unit_of_record: boundary-polygon | time_start: unknown | time_latest: current | cadence: irregular
formats: [dashboard-only, WMS] | access: blocked | machine_readable: 2 | license: unstated
ingest_difficulty: 4 | priority: 4 | verification: CITED | checked_on: 2026-09-19
evidence: bharatmaps.gov.in and stategisportal.nic.in both EGRESS-BLOCKED to me. Platform description
  from an NIC Informatics PDF surfaced in search; india-geodata data/police/metadata.json names
  "State GIS Portals" with url https://bharatmaps.gov.in/ and authority "Various State Police
  Departments" as the source of the jurisdiction polygons.
how_to_obtain: Open each state portal, find the police/thana layer, read its WMS/WFS GetCapabilities,
  and pull via WFS GetFeature (outputFormat=application/json). ramSeraph's toolchain already does
  this for 7 states — extend it. Requires an unblocked network path, ideally from India.
caveats: [JS-heavy viewers, layers often view-only with no export button, per-state ToU unstated]
```

### 15. DataMeet maps (`datameet/maps`)
Community shapefiles: `Country`, `States`, `Districts`, `divisions`, `assembly-constituencies`, `parliamentary-constituencies`, `Survey-of-India-Index-Maps`, `eci`, `docs`, `website`. **CC BY 4.0, MIT on code, 475 stars, 412 forks — but last updated 11 May 2022.**
```
id: geo-datameet-maps | publisher: DataMeet India community | tier: 4 | geo_coverage: all-India
geo_granularity: district | unit_of_record: boundary-polygon | time_start: 2001 | time_latest: 2022
cadence: irregular | formats: [SHP, GeoJSON, KML] | access: open-download | machine_readable: 4
license: CC-BY-4.0 | ingest_difficulty: 1 | priority: 3 | verification: VERIFIED_LANDING
checked_on: 2026-09-19
evidence: Fetched github.com/datameet/maps and /tree/master. Folder list as above. README states
  "Unless explicitly stated, all datasets in this repository is shared under CC BY 4.0". No pincode
  folder at top level.
caveats: [**STALE — last commit May 2022**, so districts are ~4 years out of date and miss dozens of
  new districts; still the most-cited Indian boundary dataset so expect other sources to be keyed to it]
```

### 16. DataMeet Municipal Spatial Data — city ward boundaries
**27 city folders**: Ahmedabad, Bangalore, Bhopal, Bhubaneswar, Bodh Gaya, Chandigarh, Chennai, Coimbatore, Delhi, Faridabad, Hyderabad, Jaipur, Kanpur, Katihar, Kishangarh, Kochi, Kolkata, Lucknow, Mira-Bhayandar, MMR, Mumbai, NMMC, PCMC, Pune, Purnia, Vadodara, Vijayawada. Typical layers per city: ward boundaries, municipal boundary, zones/circles, facilities. Last updated 28 Feb 2024. india-geodata mirrors this as "28 cities".
```
id: geo-datameet-municipal-wards | publisher: DataMeet India community | tier: 4
geo_coverage: 27-28 Indian cities | geo_granularity: ward | unit_of_record: boundary-polygon
time_start: unknown | time_latest: 2024-02-28 | cadence: irregular
formats: [GeoJSON, KML, SHP] | access: open-download | machine_readable: 4 | license: CC-BY-4.0
ingest_difficulty: 2 | priority: 5 | verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: Fetched github.com/datameet/Municipal_Spatial_Data (city list above, 150 stars, 186 forks,
  55 commits) and india-geodata data/urban/municipal-boundaries/README.md which tabulates 28 cities
  and the per-city layer types. README.md itself 404s on both main and master branches.
caveats: [ward boundaries are REDRAWN at each municipal delimitation (typically every election cycle)
  and these files carry no vintage field — a 2018 Bengaluru ward map is wrong for 2026 BBMP/GBA;
  coverage varies wildly by city; MMR/NMMC/PCMC are separate bodies not sub-areas of Mumbai]
```

### 17. National ward/ULB layers (SBM, World Bank AMRUT, Esri LivingAtlas)
Release tag `urban/boundaries`: `SBM_Wards`, `SBM_Areas`, `SBM_ULBs`, `LivingAtlas_Wards`, `WB_AMRUT_Wards`, `WB_AMRUT_ULBs`, `Shillong_Wards`. Broader than the 27-city DataMeet set — this is the route to national ward coverage.
```
id: geo-national-ward-layers | publisher: Swachh Bharat Mission / World Bank AMRUT / Esri India
tier: 3 | geo_coverage: all-India (urban) | geo_granularity: ward | unit_of_record: boundary-polygon
time_start: unknown | time_latest: unknown | cadence: irregular
formats: [Parquet, PMTiles, GeoJSONL] | access: open-download | machine_readable: 5 | license: CC0
ingest_difficulty: 2 | priority: 4 | verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: india-geodata data/urban/wards/README.md lists the 7 datasets, release tag urban/boundaries
  and the source attributions. Assets not downloaded.
caveats: [SBM/AMRUT ward geometry is programme-administrative and may not match the municipal
  corporation's legal ward map; Esri LivingAtlas redistribution terms uncertain vs the CC0 claim]
```

### 18. Pincode boundaries
Release tag `postal/boundaries`: `PincodeBoundaries` (DataMeet community), `Datagov_Pincode_Boundaries` (data.gov.in), `GSDL_Pincodes` (Delhi). ~700 MB total. Plus in-repo `pincodes-datameet/` split shapefile archives, and `datameet/INDIA_PINCODES` (last updated 2 Nov 2018). **Pincodes are what Indian users actually know and type.**
```
id: geo-pincode-boundaries | publisher: DataMeet / data.gov.in / Geospatial Delhi Limited
tier: 4 | geo_coverage: all-India | geo_granularity: ward (approx; pincode) | unit_of_record: boundary-polygon
time_start: unknown | time_latest: unknown | cadence: irregular
formats: [SHP, Parquet, PMTiles, GeoJSONL] | access: open-download | machine_readable: 4
license: CC0 (release) / DataMeet project licence (in-repo) | ingest_difficulty: 2 | priority: 4
verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: india-geodata data/postal/README.md tabulates the three release datasets and the in-repo
  DataMeet archives. datameet/INDIA_PINCODES seen in org listing (33 forks, updated 2018-11-02).
caveats: [**pincodes are postal DELIVERY ROUTES, not areas** — the polygons are reconstructions,
  they overlap, have holes, and some pincodes are a single building (PO Box style); India Post
  changes them without notice; NO official pincode polygon exists, only the point directory;
  a pincode routinely spans multiple thanas and multiple wards, so pincode→thana is many-to-many]
```

### 19. India Post PIN code directory / DIGIPIN
See entry 20 for DIGIPIN. The pincode *directory* (pincode→post office→district, as points) is published by India Post and mirrored on data.gov.in; both hosts were EGRESS-BLOCKED to me.
```
id: geo-indiapost-pincode-directory | publisher: Department of Posts | tier: 1
geo_coverage: all-India | geo_granularity: point | unit_of_record: point | time_latest: current
cadence: irregular | formats: [CSV, XLSX] | access: open-download | machine_readable: 4
license: GODL-India (likely) | ingest_difficulty: 2 | priority: 3 | verification: UNVERIFIED
checked_on: 2026-09-19
evidence: indiapost.gov.in and data.gov.in both EGRESS-BLOCKED; no direct confirmation obtained.
caveats: [listed as UNVERIFIED — do not cite a URL for this until someone fetches it]
```

### 20. DIGIPIN — India Post digital addressing (open source, self-hostable)
Official GoI repo. 10-character alphanumeric code for a ~4 m × 4 m grid cell, a pure function of lat/long. Developed with IIT Hyderabad and NRSC/ISRO. Node.js + Express, **Apache-2.0**, Swagger UI at `/api-docs`, server on `:5000`.
- `GET /api/digipin/encode?latitude=13.11179621&longitude=80.20264269`
- `GET /api/digipin/decode?digipin=4P3JK852C9`
```
id: geo-digipin | publisher: Department of Posts, Ministry of Communications | tier: 1
geo_coverage: all-India | geo_granularity: grid | unit_of_record: point | time_start: 2025
time_latest: 2026 | cadence: n/a (deterministic function) | formats: [JSON] | access: open-download
machine_readable: 5 | license: Apache-2.0 | ingest_difficulty: 1 | priority: 4
verification: VERIFIED_LIVE | checked_on: 2026-09-19
evidence: Read README.md of github.com/INDIAPOST-gov/digipin (official INDIAPOST-gov org, 103 stars)
  including the Apache-2.0 badge, the two endpoint signatures verbatim, localhost:5000 and /api-docs,
  and the statement that it was built with IIT Hyderabad and NRSC/ISRO and complies with the
  National Geospatial Policy 2022. Community fork CEPT-VZG/digipin has 414 stars.
urls.landing: https://github.com/INDIAPOST-gov/digipin
caveats: [DIGIPIN is a GEOCODE, not a geocodER — it converts coordinates to a code, it does NOT
  resolve a street address to coordinates, so it does not replace Nominatim; adoption is early so
  few source records will carry one; 4 m precision is far finer than any crime data we will publish,
  so aggregate up before display]
```

### 21. OpenStreetMap India — `amenity=police` and admin relations
OSM carries `amenity=police` POIs and `boundary=administrative` relations with `admin_level` 2/4/5/6/7/8 for India. Overpass API is the query route; Geofabrik publishes a daily India `.osm.pbf` extract. **All OSM hosts were EGRESS-BLOCKED to me, so coverage quality is UNVERIFIED.** OSM is ODbL — share-alike, which is a genuine consideration for derived boundary products.
```
id: geo-osm-india | publisher: OpenStreetMap Foundation / OSM India community | tier: 5
geo_coverage: all-India | geo_granularity: point | unit_of_record: point
time_start: 2004 | time_latest: current | cadence: realtime | formats: [JSON, GeoJSON, SHP, PBF]
access: open-download | machine_readable: 5 | license: ODbL-1.0 | ingest_difficulty: 2 | priority: 3
verification: UNVERIFIED | checked_on: 2026-09-19
evidence: Could not reach openstreetmap.org, wiki.openstreetmap.org, taginfo, overpass-api.de or
  download.geofabrik.de — all EGRESS-BLOCKED. No coverage figure obtained. Do not quote a count.
how_to_obtain: Overpass QL to count Indian police POIs:
  [out:json][timeout:180];area["ISO3166-1"="IN"][admin_level=2]->.in;
  nwr["amenity"="police"](area.in);out count;
  Then drop the "out count;" for the features. For bulk work use the Geofabrik india-latest.osm.pbf
  rather than Overpass (Overpass has strict fair-use limits; do not harvest at volume).
caveats: [**ODbL share-alike**: publishing a boundary layer derived from OSM may oblige us to release
  it under ODbL — keep OSM-derived geometry in a separate, clearly-licensed layer from CC0/CC-BY data;
  OSM admin boundaries for India are incomplete below admin_level 6 and district edits are contested;
  OSM's depiction of J&K/Arunachal does NOT match Survey of India — see entry 12]
```

### 22. Nominatim (self-hosted) — recommended geocoder
```
id: geo-nominatim | publisher: OSM Foundation | tier: 5 | geo_coverage: all-India
geo_granularity: address | unit_of_record: point | cadence: realtime | formats: [JSON]
access: open-download (self-host) | machine_readable: 5 | license: ODbL-1.0 (data), GPL (software)
ingest_difficulty: 3 | priority: 5 | verification: UNVERIFIED | checked_on: 2026-09-19
evidence: nominatim.openstreetmap.org EGRESS-BLOCKED; recommendation is on architectural grounds,
  not a live check.
how_to_obtain: Self-host from the Geofabrik India extract. The public instance's usage policy caps
  at ~1 req/s and forbids bulk geocoding — do not build on it.
caveats: [Indian address quality in OSM is poor outside metros — expect low hit rates on rural
  addresses; no official house-number coverage; ODbL applies to results]
```

### 23. Photon (self-hosted, OSM-based, typo-tolerant)
```
id: geo-photon | publisher: Komoot | tier: 5 | geo_coverage: all-India | geo_granularity: address
unit_of_record: point | formats: [JSON] | access: open-download (self-host) | machine_readable: 5
license: Apache-2.0 (software), ODbL (data) | ingest_difficulty: 3 | priority: 3
verification: UNVERIFIED | checked_on: 2026-09-19
evidence: photon.komoot.io EGRESS-BLOCKED. Listed for completeness as the autocomplete-friendly
  companion to Nominatim.
caveats: [same ODbL and Indian-address-quality caveats as Nominatim; public instance is not for
  production use]
```

### 24. Google Maps Platform — LEGALLY UNUSABLE FOR THIS PRODUCT
Verbatim from the Terms of Service, which I fetched and extracted:
- **§3.2.3(a) No Scraping** — "Customer will not export, extract, or otherwise scrape Google Maps Content for use outside the Services. For example, Customer will not: (i) pre-fetch, index, store, reshare, or rehost Google Maps Content outside the services; (ii) bulk download Google Maps tiles, Street View images, **geocodes**, directions…"
- **§3.2.3(b) No Caching** — "Customer will not cache Google Maps Content except as expressly permitted under the Maps Service Specific Terms."
- **§3.2.3(c) No Creating Content From Google Maps Content** — "…Customer will not: … **(iv) use latitude/longitude values from the Places API as an input for point-in-polygon analysis**…"
- **§3.2.3(e) No Use With Non-Google Maps** — "To avoid quality issues and/or brand confusion, Customer will not use the Google Maps Core Services with or near a non-Google Map in a Customer Application. For example, Customer will not (i) display or use Places content on a non-Google Map…"
- Maps Service Specific Terms §1.3.2: Address Validation lat/long may be cached **"30 consecutive calendar days, after which Customer must delete the cached Google Maps Content."**

Our product geocodes an address and performs point-in-polygon into a thana/ward polygon, stores the result, and renders it on a MapLibre/vector basemap. That is squarely prohibited by (a), (c)(iv) and (e).
```
id: geo-google-maps-platform | publisher: Google LLC | tier: 5 | geo_coverage: all-India
geo_granularity: address | unit_of_record: point | cadence: realtime | formats: [JSON]
access: api-key (paid) | machine_readable: 5 | license: ToU-restricts-reuse | ingest_difficulty: 1
priority: 1 | verification: VERIFIED_LIVE | checked_on: 2026-09-19
evidence: Fetched cloud.google.com/maps-platform/terms and .../maps-service-terms (2.4 MB HTML),
  stripped markup and extracted the clauses above verbatim with their section numbers.
urls.docs: https://cloud.google.com/maps-platform/terms/
caveats: [**Do not use. Blocking legal constraint, not a cost constraint.** Using Google only as a
  live-rendered basemap with Google's own tiles would be compliant but forecloses vector styling,
  offline tiles and the SoI boundary overlay we are legally required to apply.]
```

### 25–27. Mapbox, HERE, Mappls/MapmyIndia
All three hosts were EGRESS-BLOCKED; I have no verified terms for any of them. Recorded so they are not silently dropped.
- **Mapbox** — commercial geocoding + vector tiles. Permanent geocoding is a separate, more expensive SKU; standard geocoding forbids permanent storage. Must be checked against our store-and-serve model.
- **HERE** — commercial; generally more permissive on storage than Google but requires contract review.
- **Mappls (CE Info Systems / MapmyIndia)** — Indian-origin, with an ISRO/government relationship, and the one vendor whose boundary depiction is India-compliant by construction. Strongest commercial candidate for Indian address geocoding, which OSM does poorly.
```
ids: geo-mapbox, geo-here, geo-mappls | tier: 5 | geo_granularity: address | unit_of_record: point
access: api-key | license: ToU-restricts-reuse | verification: UNVERIFIED | checked_on: 2026-09-19
evidence: mapbox.com, docs.mapbox.com, here.com, mapmyindia.com and mappls.com all EGRESS-BLOCKED;
  en.wikipedia.org/wiki/Mappls and /wiki/CE_Info_Systems both 404. No terms verified. Flagged for
  Phase 2 legal review, not for reliance.
```

### 28. indianopenmaps — a working tile server for ~498 Indian layers
ramSeraph's Cloudflare Worker serving vector tiles (protobuf) and raster tiles from PMTiles archives and COGs, with mosaic sharding for oversized PMTiles, TileJSON endpoints per source, a STAC API over geoparquet indices, and MapLibre GL viewers with feature inspection and partial download. Ships `iomaps`, a Python CLI that clips the large `.7z` archives to an arbitrary polygon/bbox and exports to other formats — exactly what we need to pull, say, only Bengaluru.
```
id: geo-indianopenmaps | publisher: ramSeraph (community) | tier: 4 | geo_coverage: all-India
geo_granularity: village | unit_of_record: boundary-polygon | time_latest: 2026-06 | cadence: irregular
formats: [PMTiles, GeoTIFF, Parquet, JSON] | access: open-download | machine_readable: 5
license: varies per layer | ingest_difficulty: 2 | priority: 4 | verification: VERIFIED_LANDING
checked_on: 2026-09-19
evidence: Read README of github.com/ramSeraph/indianopenmaps — "Currently serves ~498 tile sources",
  architecture, iomaps tool, and the list of 11 backing data repos. Listed site indianopenmaps.com
  not fetched (only the repo was reachable).
urls.landing: https://indianopenmaps.com/ (cited)
```

### 29. ramSeraph/indian_admin_boundaries — the true upstream
Release tags: `states`, `districts`, `subdistricts`, `blocks`, `panchayats`, `villages`, `habitations`, `urban`, `forests`, `coastal`, `postal`, **`police`**, `constituencies`, `census-2011`, `historical`. This is where india-geodata's boundary content actually comes from — prefer citing this.
```
id: geo-ramseraph-admin-boundaries | publisher: ramSeraph (community harvest of GoI portals)
tier: 4 | geo_coverage: all-India | geo_granularity: village | unit_of_record: boundary-polygon
time_start: 1941 | time_latest: 2026 | cadence: irregular | formats: [GeoJSONL, PMTiles, Parquet]
access: open-download | machine_readable: 5 | license: varies; README reproduces Geospatial
  Guidelines clause xiii as the governing constraint | ingest_difficulty: 2 | priority: 5
verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: Read the repo README (full tag list, clause xiii quote) and the police release page
  (13 assets with per-state attribution).
urls.data: https://github.com/ramSeraph/indian_admin_boundaries/releases
```

### 30. ramSeraph/opendata — LGD and Survey of India scrapers
`lgd/` pulls the Local Government Directory (with a published data mirror at `ramseraph.github.io/opendata/lgd`); `maps/SOI/` pulls `onlinemaps.surveyofindia.gov.in`. Updated April 2026. **This is the practical way to get LGD in bulk without writing a scraper.**
```
id: geo-ramseraph-opendata-lgd | publisher: ramSeraph | tier: 4 | geo_coverage: all-India
geo_granularity: village | unit_of_record: aggregate-count (code registry) | time_latest: 2026-04
cadence: irregular | formats: [CSV, JSON] | access: open-download | machine_readable: 4
license: unstated | ingest_difficulty: 2 | priority: 5 | verification: VERIFIED_LANDING
checked_on: 2026-09-19
evidence: Read github.com/ramSeraph/opendata README naming lgd/, bbnl/, maps/SOI/ and doc/ with their
  data mirror URLs. Mirror itself (github.io) EGRESS-BLOCKED to me.
```

### 31. datta07/INDIAN-SHAPEFILES
National (India, states, districts, PCs, highways, railways), state (district→sub-district→constituency) and metro (ward, sub-division) layers. GeoJSON RFC-7946 + shapefile, EPSG:4326, **MIT licence**. Named as the source of india-geodata's police *points*.
```
id: geo-datta07-indian-shapefiles | publisher: datta07 (community) | tier: 4 | geo_coverage: all-India
geo_granularity: ward | unit_of_record: boundary-polygon | time_start: 2019 | time_latest: unknown
cadence: irregular | formats: [GeoJSON, SHP] | access: open-download | machine_readable: 4
license: MIT | ingest_difficulty: 2 | priority: 2 | verification: VERIFIED_LANDING | checked_on: 2026-09-19
evidence: Fetched github.com/datta07/INDIAN-SHAPEFILES README. Explicitly states data vintage is
  "Primarily 2019 (with ongoing updates)" and warns "Some datasets reflect 2019 administrative
  boundaries. Recent territorial changes may not be reflected in all files." No police layer is
  documented in its README despite india-geodata citing it for police points.
caveats: [2019 vintage; the police-point attribution chain between this repo and india-geodata is
  inconsistent — india-geodata's own file is MHA-derived (feature ids police_station_mha.N),
  so trust the file, not the attribution]
```

### 32. OpenCity / Police Jurisdiction Maps for Major Cities of India
A CKAN dataset titled "Police Jurisdiction Maps for Major Cities of India" exists on OpenCity's data portal, and OpenCity publishes a guide "How to Access Government GIS Data for Indian Cities/States". Both hosts EGRESS-BLOCKED. Worth chasing because it may cover cities outside the 7 states above (Mumbai in particular).
```
id: geo-opencity-police-jurisdiction | publisher: OpenCity / Oorvani Foundation | tier: 4
geo_coverage: major Indian cities | geo_granularity: police-station | unit_of_record: boundary-polygon
access: blocked | machine_readable: 3 | license: unknown | ingest_difficulty: 3 | priority: 4
verification: CITED | checked_on: 2026-09-19
evidence: Dataset title and URL surfaced in search results; data.opencity.in and opencity.in both
  EGRESS-BLOCKED. Search snippet indicates a Mumbai police jurisdiction map with station locations.
urls.landing: https://data.opencity.in/dataset/police-jurisdiction-maps-for-major-cities-of-india
how_to_obtain: Open the CKAN dataset page from an unblocked network; CKAN exposes /api/3/action/
  package_show for machine access.
```

### 33. Geospatial Delhi Limited (GSDL) — Delhi's full stack
GSDL supplies Delhi police station jurisdiction boundaries *and* Delhi pincode boundaries, both already in the release sets above. A DataMeet mailing-list thread "Shape files for Police Jurisdiction Maps of Delhi" points at the GSDL GIS server serving jurisdictional boundary layers as GeoJSON at multiple levels.
```
id: geo-gsdl-delhi | publisher: Geospatial Delhi Limited, GNCTD | tier: 2 | geo_coverage: Delhi NCT
geo_granularity: police-station | unit_of_record: boundary-polygon | formats: [GeoJSON, SHP]
access: open-download (via mirror) | machine_readable: 4 | license: unstated | ingest_difficulty: 2
priority: 4 | verification: CITED | checked_on: 2026-09-19
evidence: GSDL named as source of GSDL_DL_Police_Station_Boundaries and GSDL_Pincodes in two verified
  READMEs/release pages. The datameet Google Group thread was EGRESS-BLOCKED.
urls.landing: https://groups.google.com/g/datameet/c/cNqq9bC_RTk (cited, unverified)
```

### 34. Basemap: MapLibre + PMTiles + SoI boundary overlay (recommended architecture)
Not a "source" so much as the only compliant configuration. Serve our own vector tiles (PMTiles on object storage, MapLibre GL client — the pattern indianopenmaps already proves at ~498 layers), and render the national/state boundary from **SoI digital boundary data** on top, so the published map's depiction of J&K/Ladakh/Aksai Chin/Arunachal matches the official standard required by Geospatial Guidelines clause xiii.
```
id: geo-basemap-maplibre-pmtiles-soi | publisher: n/a (our architecture) | tier: 3
geo_coverage: all-India | geo_granularity: national | unit_of_record: boundary-polygon
formats: [PMTiles, GeoJSON] | access: open-download | machine_readable: 5
license: mixed (OSM ODbL for cartography, SoI for boundaries) | ingest_difficulty: 3 | priority: 5
verification: CITED | checked_on: 2026-09-19
evidence: Architecture inferred from the verified clause xiii text and the verified indianopenmaps
  README. Not a fetched product.
caveats: [if the cartographic basemap is OSM-derived, its own boundary lines must be SUPPRESSED and
  replaced by the SoI layer, not merely overdrawn — an OSM dashed LoC visible under our line is
  still a non-compliant depiction]
```

## Granularity reality check

| Level | What exists | Coverage | Period | Refresh | Usable for the map? |
|---|---|---|---|---|---|
| Address / street | nothing public | — | — | — | **No.** police.uk's core unit is unavailable in India. |
| Grid (H3 / DIGIPIN) | derivable from any point layer; DIGIPIN 4 m official | all-India | n/a | deterministic | **Yes** — best privacy-safe aggregation unit |
| Police station polygon | 7 states + marine + traffic/railway variants | AP, BR, DL, KA, RJ, TN, TG (~1/3 of population) | vintage undocumented, mirror says 2024 | irregular, no changelog | **Yes, in those 7** |
| Police station point | 16,459 with MHA `ps_cd` | all 36 states/UTs | unknown | irregular | **Yes — the join key** |
| Municipal ward | 27–28 cities (DataMeet) + SBM/AMRUT national urban | metros + urban India | 2018–2024, mixed | per delimitation | **Yes — the best "neighbourhood" unit** |
| Pincode polygon | community + data.gov.in reconstructions | all-India | unknown | irregular | Use for **input**, never for display |
| Subdistrict / tehsil | LGD, SOI, Census 2011 | all-India | 2011 + current | irregular | Yes |
| District | LGD (~800), Census 2011 (640), historical 1941–2001 + change ledger to 2024 | all-India | 1941–2026 | continuous | **Yes — the safe national default** |
| State | everywhere | all-India | current | rare | Yes |

**The gap, stated plainly:** we want street-level and we can get police-station-level in 7 states, ward-level in ~28 cities, and district-level everywhere. There is no Indian equivalent of the England & Wales neighbourhood boundary release.

## Critical analysis — recommended geography spine and join strategy

**Spine: a two-layer model — analytic unit = police station (`ps_cd`); display unit = ward in cities, district nationally.**

Reasoning: Indian crime data is *generated* at the thana. FIRs are registered at a police station; CCTNS keys on the station; NCRB aggregates up from it. Choosing anything else as the analytic unit forces a lossy allocation at ingestion, which is where errors become permanent. The MHA point file gives us all 16,459 stations with a code, nationally, today.

But the thana is the wrong *display* unit, for two reasons: we only have true polygons for 7 states, and thana jurisdictions are unfamiliar to residents. So:

1. **Analytic spine — `ps_cd`.** Treat the MHA 7–8 digit code as the immutable primary key for a station. Do **not** derive district from it (843 stations prove the embedded district code goes stale after reorganisation); carry `district_c` as a separate, time-versioned attribute.
2. **Geometry for the spine:**
   - *7 states:* use the published jurisdiction polygon. Match polygon→`ps_cd` by nearest-point + normalised-name agreement, and store the match confidence; names are not unique (14,647 names for 16,459 stations), so never match on name alone.
   - *Everywhere else:* **Voronoi/Thiessen cells over station points, clipped to the police district boundary.** Clipping is what makes this defensible — a cell may be wrong within a district but it is never wrong *across* one, and police districts are the level at which counts are actually published. Label these in the UI as "approximate catchment area", with a distinct fill pattern from real jurisdictions. Never colour them identically to verified polygons.
   - *Refinement where available:* population-weight the Voronoi using village polygons + SHRUG/WorldPop so cells follow settlement rather than empty geometry.
3. **Display units:** district for the national view; **municipal ward** for city views (27–28 cities now, more via SBM/AMRUT); thana polygon only on drill-down and only where real. For point-level data use **H3 res 7–8** (≈5 km² / ≈0.7 km²) rather than exact points — it gives police.uk-like visual texture without implying an address.
4. **Join strategy, in strict preference order:**
   1. Record carries a police station code → direct join on `ps_cd`. *(Aim to make every ingestion path produce this.)*
   2. Record carries state + district + station name → normalise (uppercase, strip "PS"/"P.S."/"Police Station"/"Thana", collapse whitespace, handle transliteration variants) and fuzzy-match **within the state only**, with a manual review queue for scores below threshold.
   3. Record carries an address → self-hosted Nominatim/Photon over the OSM India extract → point-in-polygon into (thana polygon | Voronoi cell), ward, district. **Never Google** (§3.2.3(c)(iv) prohibits exactly this).
   4. Record carries only a pincode → pincode polygon → areal- and population-weighted allocation to wards/districts. Many-to-many; always publish an uncertainty band.
   5. Record carries a DIGIPIN → decode to lat/long, then as (3).
5. **District reorganisation.** Build a district crosswalk table keyed on LGD district code with `valid_from` / `valid_to`, seeded from `District_Timeseries_1951-2024.csv`, `District_splits_and_carveouts_1951_to_2024.csv` and `New_districts_created_1951_to_2024.csv`. Rules: (a) **display** on current LGD districts; (b) compute **time series** on a fixed stable geography — Census 2011 districts, or SHRUG's consistent units if the non-commercial licence permits — by aggregating children to their 2011 parent; (c) never compare a rate across a split boundary without collapsing both sides to the common ancestor; (d) treat police districts (983 codes) as a *distinct* hierarchy from revenue districts (~800), because commissionerates and railway districts do not nest.
6. **Denominators.** Every per-capita figure until 2028 rests on projections from a 2011 base. Publish absolute counts as the primary number and rates as secondary with an explicit "2011-projected population" footnote. Re-base when 2027 census outputs land — and budget for a full code migration when they do.

## Blockers and how to get past them

| # | Blocker | Way past |
|---|---|---|
| 1 | **No thana polygons for 29 of 36 states/UTs** | Voronoi-clipped-to-police-district as the interim; in parallel pursue the village→thana route (below) and harvest more state GIS portals. |
| 2 | **Research-environment egress policy** blocked nearly every primary host: `lgdirectory.gov.in`, `censusindia.gov.in`, `surveyofindia.gov.in`, `bhuvan.nrsc.gov.in`, `bharatmaps.gov.in`, `stategisportal.nic.in`, `data.gov.in`, `devdatalab.org`, all OSM hosts, `opencity.in`, `mapbox.com`, `mapmyindia.com`, `indiapost.gov.in`, `*.github.io`, `groups.google.com` | Everything marked CITED/UNVERIFIED here needs one pass from an unblocked network. Only `github.com`, `raw.githubusercontent.com`, `en.wikipedia.org` and `cloud.google.com` were reachable. **WebSearch budget was also exhausted session-wide after ~4 queries**, which capped discovery breadth. |
| 3 | Jurisdiction polygons carry no `ps_cd` | Spatial-join polygon centroids to MHA points, require normalised-name agreement, keep a confidence score and a manual queue. |
| 4 | State GIS portals are view-only JS viewers | Read WMS/WFS `GetCapabilities`, pull via `WFS GetFeature&outputFormat=application/json`. ramSeraph's toolchain already does this for 7 states. |
| 5 | Ward boundaries have no vintage and are redrawn each cycle | Version wards with `valid_from`/`valid_to`; scrape each corporation's delimitation notification; never join a 2018 ward map to 2026 incidents. |
| 6 | Google Maps ToS forbids our core operation | Self-host Nominatim/Photon; evaluate Mappls commercially. Settled, not open. |
| 7 | SHRUG is CC-BY-NC-SA | Get a written licensing decision from DDL **before** shrid enters the schema, or keep SHRUG strictly to internal validation. |
| 8 | OSM is ODbL share-alike | Keep OSM-derived geometry in a physically separate layer with its own licence notice; do not merge it into CC0/CC-BY outputs. |
| 9 | Stale denominators until 2027-28 | Counts primary, rates secondary and footnoted. |
| 10 | Overlapping traffic/railway/GRP jurisdictions | Model `jurisdiction_type` as a first-class column; point-in-polygon returns a *set*, not a value. |

## Seed Leads (unconfirmed but probably real)

1. **Village-to-thana mapping tables — the highest-value lead in this dossier.** Every state police force must know which villages fall under each station; CCTNS requires it. Many state police sites publish "list of villages under each police station" as PDFs, and district administrations publish them in gazetteers. Dissolving LGD/Census village polygons by such a table yields **exact** thana boundaries, not approximations. *Next step:* RTI to each State DGP's office (and to NCRB/MHA for the CCTNS station master) requesting "the police-station-wise list of villages/wards comprising each station's jurisdiction, with LGD village codes, in machine-readable form". Start with the 29 states that lack polygons; a single successful state is worth more than any amount of Voronoi work.
2. **MHA/NCRB holds a national police station master.** The `police_station_mha` layer name and the clean `ps_cd` hierarchy prove MHA maintains an authoritative station registry. *Next step:* RTI to MHA (CCTNS division) / NCRB for the station master **with jurisdiction descriptions**, and ask whether a jurisdiction polygon layer exists internally on the ICJS GIS.
3. **The other state GIS portals probably have the layer.** 7 states publish it, which suggests the NIC/Bharatmaps template includes a police layer that most states populate but do not expose. *Next step:* enumerate `stategisportal.nic.in/stategisportal/Home/State/{1..38}`, inspect each WMS `GetCapabilities` for a police/thana layer name.
4. **Maharashtra/Mumbai.** Absent from every polygon source found, despite being the highest-value city for this product. MCGM publishes ward boundaries; Mumbai Police publish jurisdiction maps as images. OpenCity's "Police Jurisdiction Maps for Major Cities of India" may already hold a digitised Mumbai layer. *Next step:* open that CKAN dataset; if empty, georeference the Mumbai Police jurisdiction PDF against MCGM wards.
5. **Uttar Pradesh (1,713 stations) and Madhya Pradesh (1,110).** Both large, both polygon-less. MP Police already publish station *points* (`MP_Police_Stations` via mppolice.gov.in), which suggests some GIS capability worth an RTI.
6. **Census 2027 boundary freeze date.** MHA normally notifies a date after which no new administrative units are recognised for census purposes. Knowing it tells us exactly which district vintage the 2027 outputs will use. *Next step:* find the MHA/RGI gazette notification for the 2026-27 census boundary freeze.
7. **LGD API.** LGD is known to expose report/export endpoints and possibly an ApiSetu-published API (`apisetu.gov.in` was blocked). *Next step:* check ApiSetu's catalogue for an MoPR/LGD API before committing to the scraper route.
8. **`ramSeraph/indian_cadastrals`** (updated Mar 2026) holds state cadastral maps — plot-level geometry. Almost certainly too fine and too patchy for v1, but it is the only route to sub-ward precision in rural India.

## Phase 2 recommendations (ranked)

1. **Ingest `INDIA_POLICE_STATIONS.geojson` and make `ps_cd` the primary key of the entire product.** One 5 MB download, already validated. Build the `state_cd`(MHA) ↔ PC11 ↔ LGD state/district crosswalk immediately — every other agent's crime data will need it.
2. **Pull the 13 police jurisdiction assets** from `ramSeraph/indian_admin_boundaries` tag `police`, decompress, count features per state, and build the polygon→`ps_cd` match with confidence scores. Separate territorial from traffic/railway/GRP into a `jurisdiction_type` column.
3. **Build the district crosswalk** from the four `District_*` CSVs + LGD districts + Census 2011 districts, with validity intervals. Nothing time-series is trustworthy until this exists.
4. **Generate clipped Voronoi catchments** for the 29 polygon-less states and ship them behind an explicit "approximate" label with its own map style.
5. **Ingest ward boundaries** — DataMeet's 27 cities first (metros matter most), then SBM/AMRUT national urban wards. Version them with `valid_from`/`valid_to`.
6. **Stand up self-hosted Nominatim + Photon** on the Geofabrik India extract and benchmark hit rates on real Indian addresses by state. If rural hit rates are unusable, price Mappls.
7. **Stand up the basemap**: PMTiles on object storage + MapLibre, with the SoI boundary layer overlaid and any OSM boundary lines suppressed. Get counsel to sign off against Geospatial Guidelines clause xiii before any public launch.
8. **Vendor `INDIAPOST-gov/digipin`** (Apache-2.0) as an internal library for privacy-safe location encoding.
9. **File the RTIs in Seed Leads 1 and 2 now** — RTI turnaround is 30+ days, so it must start in parallel with engineering, not after it.
10. **Re-verify everything marked CITED/UNVERIFIED** from an unblocked network before any of it reaches the published product.
