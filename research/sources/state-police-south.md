# South India state police & home-department crime data
_Agent: state-police-south · Researched: 2026-09-19 · Entries: 0 fetched-live / 38 total (38 `CITED`, 0 `VERIFIED_LIVE` — see **Verification caveat** below)_

**Scope:** Andhra Pradesh, Telangana, Karnataka, Tamil Nadu, Kerala, Puducherry, Andaman & Nicobar, Lakshadweep.

> ### Verification caveat — read before trusting any `verification` field
> Every `*.gov.in` host and `data.opencity.in` is **blocked by this sandbox's outbound egress proxy**
> (`CONNECT tunnel failed, response 403` on curl; `EGRESS_BLOCKED` from WebFetch). `web.archive.org`,
> `groups.google.com`, `github.io` and all news domains are blocked too. I could therefore fetch **zero**
> primary sources, and no entry is marked `VERIFIED_LIVE`. What I *could* do, and did:
> 1. **Live web search** (200 queries, budget exhausted) — returns indexed page **titles** and summaries,
>    which is strong evidence a URL exists and weak evidence about its contents.
> 2. **`raw.githubusercontent.com` (reachable)** — I fetched two independent third-party source audits in
>    full: `joesaby/kerala-gov-mission-control/docs/data/safety.md` (self-dated **2026-05-18**) and
>    `Aparup321/crime_detection/docs/research/indian-city-crime-datasets.md` (sources verified **2026-09-10**,
>    21 primary sources). Several entries below rest on these and say so explicitly.
> 3. **GitHub code search** — used as a URL/endpoint discovery engine; the Telangana DKAN API surface and
>    the Tamil Nadu Wicket URL forms were recovered verbatim from third-party code this way.
>
> **Phase 2 must re-verify every entry from an unblocked network, ideally an Indian IP.** Treat this
> dossier as a high-confidence map of *what to check*, not as confirmation of what is downloadable today.

## Executive summary

- **Kerala is the only jurisdiction in India found here that publishes crime statistics at
  police-station level.** `ps.keralapolice.gov.in/<station>-ps/crime-statistics` — 14 distinct live
  station pages confirmed by title across 8 districts, out of 564 stations statewide. Nothing else in
  the region comes within one administrative level of this.
- **Finest granularity overall = police-station, via three FIR endpoints:** Kerala THUNA
  (`/citizen-fir-download`, by district+station+year, back to Nov 2016), Karnataka KSP
  (`/firsearch/en`, by district+station+FIR-no+year) and AP (`FIRComplainant.jsp`, by
  district+station+date+FIR-no). Only Kerala's supports listing without already knowing the FIR number.
- **Telangana's reputation is wrong.** `data.telangana.gov.in` is a genuinely good DKAN v2 portal with
  a documented JSON API and ~637–658 datasets, and **no crime dataset**. The single police holding,
  `/dataset/police-stations`, is reported to be a per-district *count* of stations — not a roster, no
  coordinates. Telangana's real crime publication is the DGP's Annual Report (commissionerate-level,
  released ~29 December each year, i.e. near-zero lag) and it is a press release, not a download.
- **Cheapest high-value ingest is Karnataka via OpenCity:** four years (2022–2025) of KSP
  district/commissionerate IPC-BNS and SLL tables as CSV behind a keyless CKAN 3 API, plus monthly
  Crime Review PDFs. Start here on day one of Phase 2.
- **The geometry problem is nearly solved in exactly one state.** Karnataka has published
  police-station **point** coordinates (KML, Karnataka + Bengaluru Urban, base list 2012). Everywhere
  else, station location must be geocoded from free-text addresses or reverse-engineered from a
  mobile app. No jurisdiction anywhere in the region publishes police-station **jurisdiction polygons**.
- **No incident-level geocoded crime data exists anywhere in India.** This was independently
  established on 2026-09-10 across 21 primary sources (data.gov.in, ncrb.gov.in, mospi.gov.in,
  BCP/KSP, TN CCTNS reviews, Mumbai Police) and nothing found here contradicts it. A police.uk-style
  *street-level point map is not buildable from Indian open data.* The honest product is
  station-area choropleth with an explicit "station-area aggregation, not incident locations" label.
- **The single biggest data-integrity blocker is the Supreme Court sensitive-category carve-out**
  (judgment of 07.09.2016): FIRs for sexual offences, POCSO, insurgency and terrorism are never
  uploaded to any state police site. Every public FIR corpus in India is therefore missing precisely
  the crime categories a resident asking "is this safe to walk through at night?" most wants.
- **Three UTs publish nothing at all.** Puducherry, Andaman & Nicobar and Lakshadweep are
  `access: rti-only`, recorded as explicit negative findings. Each is small enough (21 and 16
  stations respectively for A&N and Lakshadweep) that one well-drafted RTI could return a complete
  station-level series.
- **Two dead ends worth recording so they are not chased again:** Bengaluru's crowdsourced *Public Eye*
  app is retired (BTP no longer monitors it, ASTraM replaced it, and ASTraM's dashboard is internal);
  and the Hyderabad ICCC — 100,000+ cameras, the Dial-100/112 node, the richest incident data in the
  country — has no public dashboard or feed of any kind.
- **Licence risk is real and unevenly distributed.** OpenCity mirrors carry "Other (Public Domain)"
  but the *upstream* KSP/BCP terms are unverified; the BCP contact dataset is explicitly
  **"No License Provided"** (use geometry and station names, never republish the phone numbers); state
  police HTML pages are uniformly `unstated`. Only the NIC OGD portals (`tn.data.gov.in`,
  `kerala.data.gov.in`) and `data.telangana.gov.in` carry a clean **GODL-India** grant.

### State-by-state accessibility rating (1–5, for *our* map)

| Jurisdiction | Rating | Justification |
|---|---|---|
| **Kerala** | **5** | Only police-station-level published crime tables in India; monthly refresh; open FIR search by station back to 2016-11; district mirrors. Loses nothing but the sensitive-category carve-out and the absence of an API. |
| **Karnataka** | **4** | District + commissionerate, **monthly**, already CSV-ified behind a keyless CKAN API, four years deep — plus the region's only published station point geometry. Ceiling is district: no station-level counts. |
| **Tamil Nadu** | **3** | Data exists (SCRB annual, CCTNS district reviews, 2019–2023 CSVs) but head coverage is shallow, lag is 12+ months, the citizen portal is a session-bound Wicket app, and the state OGD portal carries no crime dataset. |
| **Telangana** | **3** | Fastest annual release in India and a station-addressable signed-FIR service — but the celebrated open data portal has no crime data, and the ICCC publishes nothing. Access is police-gated, not open. |
| **Andhra Pradesh** | **3** | Live crime-statistics and FIR endpoints on a stateless, scrape-friendly JSP stack; but content/period unverified and two district-boundary breaks (2014, 2022) to reconcile. |
| **Puducherry** | **1** | No published crime statistics. RTI or the DES Statistical Abstract. Four non-contiguous regions make UT totals near-meaningless spatially. |
| **Andaman & Nicobar** | **1** | SCRB collects from all 21 stations, publishes none of it. Only public numbers are MHA Annual Report UT totals. Tiny population → severe small-number volatility. |
| **Lakshadweep** | **1** | CCTNS since 2015-12-23, nothing published. ~70,000 people, 16 stations, single-digit counts — must be suppressed, not mapped. |

## Source entries

---

## Kerala — rating 5/5

Kerala is the best-documented police jurisdiction in India for our purposes, and the gap
between it and everyone else is not close. Three things stack: (a) every police station has its own
web page with a `crime statistics` tab — genuine **police-station-level** publication, which nowhere
else in the region offers; (b) THUNA publishes downloadable FIRs searchable by *police district +
police station + year* back to **November 2016**; (c) the state site carries **monthly** crime tables
that are refreshed within weeks, not the 12–18 month NCRB lag. 564 stations across 20 police
districts. The catch is the Supreme Court sensitive-category carve-out — sexual offences, POCSO,
terrorism FIRs are never uploaded — which removes exactly the categories a safety map is asked about.

### 1. Kerala Police per-police-station 'crime statistics' pages (ps.keralapolice.gov.in)
Search index returned 14 distinct live station pages with the exact title pattern 'crime statistics - <Station> PS' across at least 8 districts: Cantonment, Thampanoor, Mannanthala (Tvm), Payyoli (Kozhikode Rural), Pothukal (Malappuram), Mulavukadu (Ernakulam), Thalasseri + Mattannur (Kannur), Sasthamcotta (Kollam), Varandarapilly + Viyyur + Anthikad + Chavakkad (Thrissur), Marangattupilly (Kottayam). Page furniture also advertises FIR download, jurisdiction and service-rating features per station.

**How to obtain:** Harvest the station index from ps.keralapolice.gov.in (or the district sites' 'police stations' menus), then GET /<slug>-ps/crime-statistics for each. Phase 2: ~564 GETs, throttle to <=1 req/s, check robots.txt first.

```
id: state-police-south-kerala-ps-crime-statistics
name: Kerala Police per-police-station 'crime statistics' pages (ps.keralapolice.gov.in)
publisher: Kerala Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ps.keralapolice.gov.in/thampanoor-ps", "data": "https://ps.keralapolice.gov.in/cantonment-ps/crime-statistics"}
geo_coverage: Kerala, individual police stations (564 stations statewide as of 2021: 484 law & order + 80 specialised)
geo_granularity: police-station
unit_of_record: aggregate-count
time_start: unknown
time_latest: unknown (pages live at check)
cadence: irregular
lag: unknown
taxonomy: IPC+SLL
formats: ["HTML"]
access: scrape
machine_readable: 2
license: unstated
caveats: ["period covered and whether every station keeps the page current is UNVERIFIED - some may be stale or empty", "station slugs are irregular and contain typos (viyoor-ps for Viyyur PS, maranagttupilly-ps for Marangattupilly PS) so the slug list MUST be harvested, never generated", "no coordinates on the page; join to station geometry is a separate problem"]
ingest_difficulty: 3
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned 14 distinct live station pages with the exact title pattern 'crime statistics - <Station> PS' across at least 8 districts: Cantonment, Thampanoor, Mannanthala (Tvm), Payyoli (Kozhikode Rural), Pothukal (Malappuram), Mulavukadu (Ernakulam), Thalasseri + Mattannur (Kannur), Sasthamcotta (Kollam), Varandarapilly + Viyyur + Anthikad + Chavakkad (Thrissur), Marangattupilly (Kottayam). Page furniture also advertises FIR download, jurisdiction and service-rating features per station.
how_to_obtain: Harvest the station index from ps.keralapolice.gov.in (or the district sites' 'police stations' menus), then GET /<slug>-ps/crime-statistics for each. Phase 2: ~564 GETs, throttle to <=1 req/s, check robots.txt first.
notes: THIS IS THE FINEST PUBLISHED SPATIAL GRANULARITY FOUND IN THE WHOLE REGION and the closest analogue to police.uk area counts. Ingest first.
```

### 2. THUNA citizen portal — published FIR search & download (Kerala Police)
Search index returned the page 'How to download FIR? - THUNA - Kerala Police' at /citizen-fir-download with the summary: search and download published FIRs by year of registration, police district and police station name; FIRs from November 2016 onwards available. Sibling live paths seen: /arrest-search, /documentVerifier, /inform-us; legacy portal at oldthuna.keralapolice.gov.in/citizen/login.htm.

**How to obtain:** Form POST with (year, police district, police station) tuples; iterate the 20x~30 station cross-product per year. Expect a captcha or rate limit - confirm from an Indian IP with a browser session first. Do NOT bulk-harvest in Phase 1.

```
id: state-police-south-kerala-thuna-fir-download
name: THUNA citizen portal — published FIR search & download (Kerala Police)
publisher: Kerala Police
domain: state-police-south
tier: 2
urls: {"landing": "https://thuna.keralapolice.gov.in/", "data": "https://thuna.keralapolice.gov.in/citizen-fir-download"}
geo_coverage: Kerala, all police districts and stations
geo_granularity: police-station
unit_of_record: fir-record
time_start: 2016-11
time_latest: current (rolling)
cadence: daily
lag: days (SC directive requires upload within 24h/72h of registration)
taxonomy: IPC+SLL (BNS from 2024-07-01)
formats: ["PDF", "HTML"]
access: scrape
machine_readable: 1
license: unstated; public-record publication mandated by Supreme Court
caveats: ["SENSITIVE-CATEGORY EXCLUSION: per the SC judgment of 07.09.2016, FIRs for sexual offences, POCSO, insurgency and terrorism are NOT uploaded - i.e. precisely the categories a neighbourhood-safety map most needs are systematically missing", "FIR PDFs are document scans/native PDFs in Malayalam and English; OCR/NLP needed for offence extraction", "address in the FIR is free text; no lat-lon; geocoding is a separate, error-prone step", "FIRs may be withdrawn/expunged, so a harvested corpus drifts from the live index"]
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the page 'How to download FIR? - THUNA - Kerala Police' at /citizen-fir-download with the summary: search and download published FIRs by year of registration, police district and police station name; FIRs from November 2016 onwards available. Sibling live paths seen: /arrest-search, /documentVerifier, /inform-us; legacy portal at oldthuna.keralapolice.gov.in/citizen/login.htm.
how_to_obtain: Form POST with (year, police district, police station) tuples; iterate the 20x~30 station cross-product per year. Expect a captcha or rate limit - confirm from an Indian IP with a browser session first. Do NOT bulk-harvest in Phase 1.
notes: Combined with the per-station crime tables this is the only route in South India to anything resembling record-level, station-attributed crime data.
```

### 3. Kerala Police — Crime Statistics tables (Total Cases, IPC Cases, Crime against Women, POCSO, Cyber, Missing, Road Accidents, COTPA, SC/ST)
Could not fetch (see Blockers: all .gov.in egress-blocked from this sandbox). Corroborated by an independent source audit I did fetch live on 2026-09-19 (raw.githubusercontent.com/joesaby/kerala-gov-mission-control/main/docs/data/safety.md, itself dated 'Last verified: 2026-05-18') which records both URLs as 'Year/month tables of total cases, IPC cases, and category breakdowns - updated monthly', format 'HTML tables + PDF detail', 'API auth: None', 'AMBER - scrape-required (well-formed HTML tables)'. Search index independently returns page titles 'Total Crime Cases', 'Crime against women', 'The statistics of case registered in 2025 under POCSO Act'.

**How to obtain:** Plain HTTP GET + HTML table parse, no auth. Category paths observed: /crime/total-cases, /crime/pocso, /crime/road-accidents, /crime-statistics/ipc-cases, /crime-statistics/crime-against-woman. Re-check for a geo-fence from non-IN egress.

```
id: state-police-south-kerala-police-crime-tables
name: Kerala Police — Crime Statistics tables (Total Cases, IPC Cases, Crime against Women, POCSO, Cyber, Missing, Road Accidents, COTPA, SC/ST)
publisher: Kerala Police / State Crime Records Bureau
domain: state-police-south
tier: 2
urls: {"landing": "https://keralapolice.gov.in/crime-statistics/crime-against-woman", "data": "https://keralapolice.gov.in/crime/total-cases", "docs": "https://keralapolice.gov.in/crime-statistics/ipc-cases"}
geo_coverage: Kerala (state totals + 20 police districts)
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: 2026 (partial year; category index stamped 'last updated August 06, 2026')
cadence: monthly
lag: 1-2 months
taxonomy: IPC+SLL
formats: ["HTML", "PDF"]
access: scrape
machine_readable: 2
license: unstated
caveats: ["reported crime (FIR registrations), not convictions", "IPC->BNS break from 1 July 2024; heads renamed mid-series", "20 police districts != 14 revenue districts; 6 city commissionerates carved out of rural districts", "no stated principal-offence rule, so totals will not reconcile cleanly with NCRB", "HTML tables have no stable row IDs; re-scraping is the only diff mechanism"]
ingest_difficulty: 2
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Could not fetch (see Blockers: all .gov.in egress-blocked from this sandbox). Corroborated by an independent source audit I did fetch live on 2026-09-19 (raw.githubusercontent.com/joesaby/kerala-gov-mission-control/main/docs/data/safety.md, itself dated 'Last verified: 2026-05-18') which records both URLs as 'Year/month tables of total cases, IPC cases, and category breakdowns - updated monthly', format 'HTML tables + PDF detail', 'API auth: None', 'AMBER - scrape-required (well-formed HTML tables)'. Search index independently returns page titles 'Total Crime Cases', 'Crime against women', 'The statistics of case registered in 2025 under POCSO Act'.
how_to_obtain: Plain HTTP GET + HTML table parse, no auth. Category paths observed: /crime/total-cases, /crime/pocso, /crime/road-accidents, /crime-statistics/ipc-cases, /crime-statistics/crime-against-woman. Re-check for a geo-fence from non-IN egress.
notes: Same audit explicitly warns that Kerala CCTNS is an INTERNAL system with no public feed - any claim of a 'Kerala CCTNS feed' is false. These HTML pages are the only sub-annual Kerala-specific crime source.
```

### 4. Kerala Police district/city commissionerate crime-statistics mirrors
Search index returned titled pages on four distinct district subdomains: kannur., kochicity., kollamcity., wayanad. (paths /crime/total-cases, /crime/pocso, /crime-statistics/crime-against-woman). A third-party crawl seed list (github navchandar/civic-media-scout base_urls.txt, read via code-search excerpt) additionally lists ernakulamrural., kasaragod. and coastal. subdomains.

**How to obtain:** Enumerate <district>.keralapolice.gov.in from the parent site's district menu, then GET the same /crime/* paths.

```
id: state-police-south-kerala-district-police-crime-pages
name: Kerala Police district/city commissionerate crime-statistics mirrors
publisher: Kerala Police (district units)
domain: state-police-south
tier: 2
urls: {"landing": "https://kannur.keralapolice.gov.in/public-information/crime-statistics/crime-against-women", "data": "https://kollamcity.keralapolice.gov.in/crime/total-cases"}
geo_coverage: Each of 20 Kerala police districts / 6 city commissionerates
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: 2026
cadence: monthly
lag: 1-2 months
taxonomy: IPC+SLL
formats: ["HTML"]
access: scrape
machine_readable: 2
license: unstated
caveats: ["path scheme is inconsistent between the new site (/crime/...) and older district sites (/public-information/crime-statistics/...)", "district subdomain list must be harvested; not all 20 confirmed"]
ingest_difficulty: 2
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned titled pages on four distinct district subdomains: kannur., kochicity., kollamcity., wayanad. (paths /crime/total-cases, /crime/pocso, /crime-statistics/crime-against-woman). A third-party crawl seed list (github navchandar/civic-media-scout base_urls.txt, read via code-search excerpt) additionally lists ernakulamrural., kasaragod. and coastal. subdomains.
how_to_obtain: Enumerate <district>.keralapolice.gov.in from the parent site's district menu, then GET the same /crime/* paths.
notes: This is how district granularity is obtained; the state page alone gives state totals.
```

### 5. Kerala Police station directory & jurisdiction pages (ps.keralapolice.gov.in)
Search-index summaries of the per-station sites describe sections for 'jurisdiction information', FIR download and service rating alongside crime statistics. Station counts from the Kerala Police Wikipedia article, fetched live 2026-09-19.

**How to obtain:** Crawl the station index; parse address + jurisdiction text; geocode addresses separately (Nominatim/Bhuvan) and hand-QA.

```
id: state-police-south-kerala-ps-directory
name: Kerala Police station directory & jurisdiction pages (ps.keralapolice.gov.in)
publisher: Kerala Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ps.keralapolice.gov.in/thampanoor-ps"}
geo_coverage: Kerala, 564 police stations (2021: 484 law & order, 14 women, 13 railway, 18 coastal, 19 cybercrime, 1 crime branch, 1 ATS)
geo_granularity: police-station
unit_of_record: narrative-document
time_start: n/a
time_latest: current
cadence: irregular
lag: n/a
taxonomy: n/a
formats: ["HTML"]
access: scrape
machine_readable: 2
license: unstated
caveats: ["jurisdiction is described in prose (village/ward lists), not as a polygon - deriving boundaries is a manual gazetteer job", "phone numbers present: treat as contact PII under Indian norms, do not republish in bulk"]
ingest_difficulty: 3
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Search-index summaries of the per-station sites describe sections for 'jurisdiction information', FIR download and service rating alongside crime statistics. Station counts from the Kerala Police Wikipedia article, fetched live 2026-09-19.
how_to_obtain: Crawl the station index; parse address + jurisdiction text; geocode addresses separately (Nominatim/Bhuvan) and hand-QA.
notes: Needed to give the per-station crime counts a location.
```

### 6. THUNA — Arrest Search (Kerala Police)
Search index returned the titled page 'Arrest Search - THUNA - Kerala Police' at www.thuna.keralapolice.gov.in/arrest-search. Contents and query fields not inspected.

**How to obtain:** Same session/form approach as the FIR download.

```
id: state-police-south-kerala-thuna-arrest-search
name: THUNA — Arrest Search (Kerala Police)
publisher: Kerala Police
domain: state-police-south
tier: 2
urls: {"landing": "https://www.thuna.keralapolice.gov.in/arrest-search"}
geo_coverage: Kerala
geo_granularity: police-station
unit_of_record: case-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: IPC+SLL
formats: ["HTML"]
access: scrape
machine_readable: 1
license: unstated
caveats: ["arrests are not crimes; using arrest counts as a crime proxy over-weights enforcement intensity, not victimisation", "contains personal data (names of arrested persons) - do NOT republish; aggregate only"]
ingest_difficulty: 3
priority: 3
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled page 'Arrest Search - THUNA - Kerala Police' at www.thuna.keralapolice.gov.in/arrest-search. Contents and query fields not inspected.
how_to_obtain: Same session/form approach as the FIR download.
notes: Legal review required before any derived publication - this is PII.
```

### 7. Kerala Police legacy daily 'arrested persons' district PDFs
Exact URL pattern captured verbatim from a 2014-era Indian GIS project's working notes (github navbharti/navbharti, file naveen.txt), read through GitHub code-search excerpts on 2026-09-19: 'Trivandrum City (http://www.keralapolice.gov.in/newsite/pdfs/arrested_persons_2014/august/4/arrested_persons_tvmcity.pdf)' plus ten sibling district URLs; the author notes he generated shapefiles from them.

**How to obtain:** Try old.keralapolice.gov.in first; otherwise Internet Archive (web.archive.org) CDX query for newsite/pdfs/arrested_persons_* to reconstruct a daily 2014-2016 district series. Archive fetches were themselves blocked from this sandbox.

```
id: state-police-south-kerala-legacy-arrested-persons-pdfs
name: Kerala Police legacy daily 'arrested persons' district PDFs
publisher: Kerala Police (legacy newsite)
domain: state-police-south
tier: 2
urls: {"landing": "https://old.keralapolice.gov.in/public-information/crime-statistics/crime-against-women", "data": "http://www.keralapolice.gov.in/newsite/pdfs/arrested_persons_2014/august/4/arrested_persons_tvmcity.pdf"}
geo_coverage: Kerala, per police district (tvmcity, tvmrl, klmcity, idk, ekmcity, ekmrl ... district codes)
geo_granularity: police-district
unit_of_record: case-record
time_start: ~2014
time_latest: unknown (path scheme predates the current site)
cadence: daily
lag: 1 day
taxonomy: IPC+SLL
formats: ["PDF"]
access: blocked
machine_readable: 1
license: unstated
caveats: ["URL scheme belongs to the retired 'newsite'; almost certainly 404 today", "district code vocabulary (tvmcity/tvmrl/ekmcity/ekmrl) merges city and rural units that a map must keep separate"]
ingest_difficulty: 5
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Exact URL pattern captured verbatim from a 2014-era Indian GIS project's working notes (github navbharti/navbharti, file naveen.txt), read through GitHub code-search excerpts on 2026-09-19: 'Trivandrum City (http://www.keralapolice.gov.in/newsite/pdfs/arrested_persons_2014/august/4/arrested_persons_tvmcity.pdf)' plus ten sibling district URLs; the author notes he generated shapefiles from them.
how_to_obtain: Try old.keralapolice.gov.in first; otherwise Internet Archive (web.archive.org) CDX query for newsite/pdfs/arrested_persons_* to reconstruct a daily 2014-2016 district series. Archive fetches were themselves blocked from this sandbox.
notes: Only value is historical backfill; not a live feed.
```

---

## Karnataka — rating 4/5

Karnataka is the easiest to *ingest* even though its granularity stops at district/commissionerate.
KSP publishes an annual `Crime in Karnataka` and a **Monthly Crime Review** with district and
commissionerate tables; OpenCity has already converted four years of it to CSV behind a CKAN API with
no key. Critically, Karnataka is also the only state in the region with a published **police-station
point geometry** (KML, Karnataka + Bengaluru Urban) — which is what makes a map possible at all.
Bengaluru City Police publish an annual FIR-based city report. Nothing goes below district except the
FIR search, which requires you to already know the FIR number. Note two domain traps: BCP is
`bcp.karnataka.gov.in` (not bcp.gov.in) and KSP runs a *second* domain `ksp.gov.in` alongside
`ksp.karnataka.gov.in`.

### 8. OpenCity — Karnataka Crime Data 2022 / 2023 / 2024 / 2025 (KSP-sourced CSV mirror)
Search index returned the titled CKAN pages for karnataka-crime-data-2022/2023/2024/2025 and the resource 'District and Commissionerate-wise Crimes (IPC/BNS and SLL) in Karnataka in 2025'; a domain-filtered search shows '217 datasets found for "ksp.karnataka.gov.in"' on OpenCity. Corroborated by the Aparup321 research note (verified 2026-09-10), item S13.

**How to obtain:** CKAN API: GET /api/3/action/package_search?q=crime&fq=organization:... then /api/3/action/datastore_search for tabular resources. No key required.

```
id: state-police-south-opencity-karnataka-crime
name: OpenCity — Karnataka Crime Data 2022 / 2023 / 2024 / 2025 (KSP-sourced CSV mirror)
publisher: OpenCity / Civic Insights Foundation (mirroring Karnataka State Police)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/dataset/karnataka-crime-data-2025", "data": "https://data.opencity.in/dataset/karnataka-crime-data-2025/resource/90ef5e20-0e55-41d9-8a63-aceff7205d61", "api": "https://data.opencity.in/api/3/action/package_show?id=karnataka-crime-data-2025"}
geo_coverage: Karnataka - all districts and commissionerates incl. Bengaluru City
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: 2022
time_latest: 2025 (December review carries the annual roll-up)
cadence: annual, with monthly review PDFs attached
lag: 1-2 months behind KSP
taxonomy: IPC+SLL / BNS+SLL (IPC/BNS heads, SLL heads, women/children/SC-ST heads)
formats: ["CSV", "PDF", "JSON", "XML"]
access: open-download
machine_readable: 4
license: 'Other (Public Domain)' on the mirror; upstream KSP terms UNVERIFIED
caveats: ["a mirror, not the source of record - always cite KSP and re-check the upstream PDF before publishing a number", "mirror lag and occasional transcription error; no checksum published", "commissionerate rows overlap district rows"]
ingest_difficulty: 1
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled CKAN pages for karnataka-crime-data-2022/2023/2024/2025 and the resource 'District and Commissionerate-wise Crimes (IPC/BNS and SLL) in Karnataka in 2025'; a domain-filtered search shows '217 datasets found for "ksp.karnataka.gov.in"' on OpenCity. Corroborated by the Aparup321 research note (verified 2026-09-10), item S13.
how_to_obtain: CKAN API: GET /api/3/action/package_search?q=crime&fq=organization:... then /api/3/action/datastore_search for tabular resources. No key required.
notes: CHEAPEST HIGH-VALUE INGEST IN THE REGION: CSV, CKAN API, four years, district granularity, no auth. Start here for Karnataka.
```

### 9. Monthly Crime Review (Karnataka State Police)
Search index returned the titled page 'Monthly Crime Review - Karnataka State Police'. Independently corroborated by a third-party research note I fetched live on 2026-09-19 (raw.githubusercontent.com/Aparup321/crime_detection/main/docs/research/indian-city-crime-datasets.md, verified 2026-09-10), row C: 'Karnataka Crime Data 2024 / 2025 (KSP reviews) ... monthly "Crime Review" PDFs ... Aggregated (district/commissionerate x head; monthly review tables) ... Month (in review PDFs)'.

**How to obtain:** Download the month PDFs from the page; parse with camelot; reconcile December against the annual 'Crime in Karnataka' edition.

```
id: state-police-south-ksp-monthly-crime-review
name: Monthly Crime Review (Karnataka State Police)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ksp.karnataka.gov.in/new-page/Monthly%20Crime%20Review/en"}
geo_coverage: Karnataka, district + commissionerate
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: December 2025 (the December review carries the annual roll-up)
cadence: monthly
lag: ~1 month
taxonomy: IPC+SLL / BNS+SLL
formats: ["PDF"]
access: open-download
machine_readable: 1
license: unstated
caveats: ["PDF only - table extraction (tabula/camelot) required, layout changes between months", "month tables are cumulative in some editions and discrete in others; verify before differencing"]
ingest_difficulty: 3
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled page 'Monthly Crime Review - Karnataka State Police'. Independently corroborated by a third-party research note I fetched live on 2026-09-19 (raw.githubusercontent.com/Aparup321/crime_detection/main/docs/research/indian-city-crime-datasets.md, verified 2026-09-10), row C: 'Karnataka Crime Data 2024 / 2025 (KSP reviews) ... monthly "Crime Review" PDFs ... Aggregated (district/commissionerate x head; monthly review tables) ... Month (in review PDFs)'.
how_to_obtain: Download the month PDFs from the page; parse with camelot; reconcile December against the annual 'Crime in Karnataka' edition.
notes: Best monthly x district feed for Karnataka. Mirrored as CSV on OpenCity for recent years - check the mirror first.
```

### 10. Police Station Locations in Karnataka and Bengaluru Urban (KML)
Search index returned the titled resource page 'Police Station Locations in Karnataka and Bengaluru Urban - Karnataka Police Station Locations Map'. The Aparup321 note (verified 2026-09-10) lists it under the BCP organisation as the project's 'area-level geometry source', format KML, and flags the licence problem on the companion contact dataset.

**How to obtain:** Download the KML resource; ogr2ogr -f GeoJSON. Validate station count against KSP's 906 and BCP's 116+53+8+9.

```
id: state-police-south-opencity-police-station-locations-karnataka
name: Police Station Locations in Karnataka and Bengaluru Urban (KML)
publisher: OpenCity (Bengaluru City Police / Karnataka sources)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/dataset/police-station-locations", "data": "https://data.opencity.in/dataset/police-station-locations/resource/9f99ef79-3231-4c9a-8a9d-c8940198489a"}
geo_coverage: Karnataka + Bengaluru Urban
geo_granularity: point
unit_of_record: incident-point
time_start: 2012 (stations list)
time_latest: 2025 (contacts refresh)
cadence: one-off
lag: n/a
taxonomy: n/a
formats: ["KML", "CSV", "GeoJSON"]
access: open-download
machine_readable: 4
license: unclear - sibling BCP contact dataset is 'No License Provided'
caveats: ["base list is from 2012: stations created since (Electronics City division, new CEN stations) will be missing", "station points, not jurisdiction polygons - a choropleth built on Voronoi/Thiessen cells from these points is an approximation and must be labelled as one", "coordinate datum/precision unverified"]
ingest_difficulty: 2
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled resource page 'Police Station Locations in Karnataka and Bengaluru Urban - Karnataka Police Station Locations Map'. The Aparup321 note (verified 2026-09-10) lists it under the BCP organisation as the project's 'area-level geometry source', format KML, and flags the licence problem on the companion contact dataset.
how_to_obtain: Download the KML resource; ogr2ogr -f GeoJSON. Validate station count against KSP's 906 and BCP's 116+53+8+9.
notes: This is the geometry that makes a Karnataka map possible at all. Pair with KSP kspmap to fill post-2012 gaps.
```

### 11. Search First Information Report — Karnataka (KSP FIR search)
Search index returned the titled KSP page 'Search First Information Report karnataka' at /firsearch/en and the matching National Government Services Portal entry; KSP summary text states the search criteria are 'District, FIR Number, Police Station, and Year'.

**How to obtain:** Serial-number walk per (district, station, year) with backoff, or RTI to SCRB Bengaluru for a station-month FIR count extract (much cheaper and lower-risk than enumeration).

```
id: state-police-south-ksp-fir-search
name: Search First Information Report — Karnataka (KSP FIR search)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ksp.karnataka.gov.in/firsearch/en", "docs": "https://services.india.gov.in/service/detail/state-police-search-first-information-report-karnataka"}
geo_coverage: Karnataka, all 906 police stations
geo_granularity: police-station
unit_of_record: fir-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: IPC+SLL / BNS+SLL
formats: ["PDF", "HTML"]
access: scrape
machine_readable: 1
license: unstated
caveats: ["search requires District + Police Station + FIR Number + Year: there is no 'list all FIRs for station X in month Y' mode, so enumeration means guessing FIR serial numbers", "sensitive-category FIRs withheld per the 2016 SC judgment", "PDF FIRs in Kannada/English; no coordinates"]
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled KSP page 'Search First Information Report karnataka' at /firsearch/en and the matching National Government Services Portal entry; KSP summary text states the search criteria are 'District, FIR Number, Police Station, and Year'.
how_to_obtain: Serial-number walk per (district, station, year) with backoff, or RTI to SCRB Bengaluru for a station-month FIR count extract (much cheaper and lower-risk than enumeration).
notes: Enumeration is legally and ethically loaded. Prefer the aggregate Monthly Crime Review unless record-level is essential.
```

### 12. District Police Stations map (KSP kspmap)
Search index returned the titled page 'Distric Police Stations - Karnataka State Police' at /kspmap/en (the typo is KSP's). Station/office counts from the Karnataka State Police Wikipedia article fetched live 2026-09-19. The KSP mobile app is separately described as giving each station's 'contact number and location, with navigation link ... via Google maps', which implies stored coordinates somewhere in the same stack.

**How to obtain:** Open /kspmap/en with devtools, capture XHRs (look for /kspmap/... .json or a Leaflet/Google Maps marker payload). If it is server-rendered, fall back to the OpenCity KML (see opencity-bcp-station-locations) and the KSP app's API.

```
id: state-police-south-ksp-police-station-map
name: District Police Stations map (KSP kspmap)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ksp.karnataka.gov.in/kspmap/en"}
geo_coverage: Karnataka, 906 police stations, 230 circle offices, 91 SDPOs, 31 DPOs
geo_granularity: police-station
unit_of_record: incident-point
time_start: n/a
time_latest: current
cadence: irregular
lag: n/a
taxonomy: n/a
formats: ["HTML", "dashboard-only"]
access: scrape
machine_readable: 3
license: unstated
caveats: ["whether the map exposes coordinates in a JSON/GeoJSON XHR is UNVERIFIED - it may be a static image map", "unit_of_record here is a station point, not a crime point"]
ingest_difficulty: 3
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled page 'Distric Police Stations - Karnataka State Police' at /kspmap/en (the typo is KSP's). Station/office counts from the Karnataka State Police Wikipedia article fetched live 2026-09-19. The KSP mobile app is separately described as giving each station's 'contact number and location, with navigation link ... via Google maps', which implies stored coordinates somewhere in the same stack.
how_to_obtain: Open /kspmap/en with devtools, capture XHRs (look for /kspmap/... .json or a Leaflet/Google Maps marker payload). If it is server-rendered, fall back to the OpenCity KML (see opencity-bcp-station-locations) and the KSP app's API.
notes: Highest-value unconfirmed API lead in Karnataka. Check the KSP Android app (com.capulustech.ksppqrs) traffic too.
```

### 13. Crime in Karnataka — year-wise crime statistics (KSP)
Search index returned the titled KSP pages 'Crime in Karnataka' (/new-page/Crime%20in%20Karnataka/en) and 'Crimes' (/page/Crime/Crimes/en); KSP's own summary text describes 'Year Wise Crime Statistics and Monthly Crime Statistics'. A third-party scraper repo (INDIRESH-P-L/KSP-Sentinel) carries a pdf_cache/ with one file per Karnataka unit (bengaluru city, mysuru, mysuru city, mangaluru, kalaburagi, davanagere, yadgir, ramanagara, vijayanagara, chamarajanagar, uttara kannada, chikkaballapur), evidencing per-district PDF downloads from this site.

**How to obtain:** Direct PDF download; KSP static assets sit under https://ksp.karnataka.gov.in/storage/pdf-files/... (pattern confirmed by an indexed KSP PDF URL).

```
id: state-police-south-ksp-crime-in-karnataka
name: Crime in Karnataka — year-wise crime statistics (KSP)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ksp.karnataka.gov.in/new-page/Crime%20in%20Karnataka/en", "docs": "https://ksp.karnataka.gov.in/page/Crime/Crimes/en"}
geo_coverage: Karnataka (32 police districts + 6 commissionerates)
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: 2025 (annual)
cadence: annual
lag: 1-3 months
taxonomy: IPC+SLL (BNS from 2024-07-01)
formats: ["PDF"]
access: open-download
machine_readable: 1
license: unstated
caveats: ["PDF tables; commissionerate rows overlap the district rows they were carved from - double counting risk", "IPC->BNS renumbering mid-2024 breaks the head-level series"]
ingest_difficulty: 3
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled KSP pages 'Crime in Karnataka' (/new-page/Crime%20in%20Karnataka/en) and 'Crimes' (/page/Crime/Crimes/en); KSP's own summary text describes 'Year Wise Crime Statistics and Monthly Crime Statistics'. A third-party scraper repo (INDIRESH-P-L/KSP-Sentinel) carries a pdf_cache/ with one file per Karnataka unit (bengaluru city, mysuru, mysuru city, mangaluru, kalaburagi, davanagere, yadgir, ramanagara, vijayanagara, chamarajanagar, uttara kannada, chikkaballapur), evidencing per-district PDF downloads from this site.
how_to_obtain: Direct PDF download; KSP static assets sit under https://ksp.karnataka.gov.in/storage/pdf-files/... (pattern confirmed by an indexed KSP PDF URL).
notes: Prefer the OpenCity CSV mirror for ingestion; use this for authority and for any year the mirror lacks.
```

### 14. Crime in Bengaluru — Bengaluru City Police annual crime report (FIR-based)
Third-party research note fetched live 2026-09-19 (Aparup321/crime_detection docs/research/indian-city-crime-datasets.md, sources verified 2026-09-10), item S10: 'press-release PDF + 5 CSVs (total/children/cyber/accidental-suicide/women, 2021-2023 splits); source https://bcp.karnataka.gov.in; author Vaidyanathan R; created 2024-01-04, updated 2025-11-25; licence Other (Public Domain). Aggregate only - no incident rows, no coordinates.'

**How to obtain:** CSV download from the OpenCity mirror; cross-check against the BCP site for the latest year.

```
id: state-police-south-bcp-crime-in-bengaluru
name: Crime in Bengaluru — Bengaluru City Police annual crime report (FIR-based)
publisher: Bengaluru City Police
domain: state-police-south
tier: 2
urls: {"landing": "https://bcp.karnataka.gov.in/en", "data": "https://data.opencity.in/dataset/bengaluru-crime-data-2023"}
geo_coverage: Bengaluru City Police commissionerate (11 L&O divisions, 116 L&O stations, 53 traffic, 8 women, 9 CEN, 1 CCB)
geo_granularity: city
unit_of_record: aggregate-count
time_start: 2021
time_latest: 2023 (mirror updated 2025-11-25); later editions likely on bcp.karnataka.gov.in
cadence: annual
lag: ~1 week after year end (press release in early January)
taxonomy: custom (BCP crime heads: total, children, cyber, accidental/suicide, women)
formats: ["PDF", "CSV"]
access: open-download
machine_readable: 3
license: 'Other (Public Domain)' on the OpenCity mirror; original BCP terms UNVERIFIED
caveats: ["CITY TOTAL ONLY - no division or station breakdown, so it cannot drive a neighbourhood map on its own", "press-release framing: heads change between years", "BCP domain is bcp.karnataka.gov.in, NOT bcp.gov.in"]
ingest_difficulty: 1
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Third-party research note fetched live 2026-09-19 (Aparup321/crime_detection docs/research/indian-city-crime-datasets.md, sources verified 2026-09-10), item S10: 'press-release PDF + 5 CSVs (total/children/cyber/accidental-suicide/women, 2021-2023 splits); source https://bcp.karnataka.gov.in; author Vaidyanathan R; created 2024-01-04, updated 2025-11-25; licence Other (Public Domain). Aggregate only - no incident rows, no coordinates.'
how_to_obtain: CSV download from the OpenCity mirror; cross-check against the BCP site for the latest year.
notes: Use as the city-level benchmark that station-level estimates must sum to.
```

### 15. Bengaluru City Police — Contact Info (station list + contacts)
Aparup321 research note (verified 2026-09-10), item S12, verbatim: 'station contact CSVs (2012 stations list; 2025 contacts PDF); licence "No License Provided" - use geometry/names only, not phone numbers.'

**How to obtain:** CSV download from the CKAN page.

```
id: state-police-south-opencity-bcp-contact-info
name: Bengaluru City Police — Contact Info (station list + contacts)
publisher: OpenCity (mirroring Bengaluru City Police)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/dataset/bengaluru-city-police-contact-info"}
geo_coverage: Bengaluru city
geo_granularity: police-station
unit_of_record: narrative-document
time_start: 2012
time_latest: 2025
cadence: irregular
lag: n/a
taxonomy: n/a
formats: ["CSV", "PDF"]
access: open-download
machine_readable: 3
license: No License Provided
caveats: ["EXPLICIT LICENCE PROBLEM: 'No License Provided' on the mirror - use station names and geometry, do NOT republish phone numbers", "2012 station list vs 2025 contacts PDF: two different vintages in one dataset"]
ingest_difficulty: 2
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Aparup321 research note (verified 2026-09-10), item S12, verbatim: 'station contact CSVs (2012 stations list; 2025 contacts PDF); licence "No License Provided" - use geometry/names only, not phone numbers.'
how_to_obtain: CSV download from the CKAN page.
notes: Use only as a station-name crosswalk for joining KSP tables to KML points.
```

### 16. Police Seva — KSP Citizen Centric Portal (e-FIR, complaints)
Search index returned 'Citizen Centric Portal - Karnataka State Police - KSP' at policeseva.ksp.gov.in and its Login.aspx. Note the separate second-level domain ksp.gov.in (www.ksp.gov.in also hosts a 'Crime Statistics of Karnataka' page) alongside the primary ksp.karnataka.gov.in.

**How to obtain:** No bulk route. Nothing to ingest without an institutional MoU.

```
id: state-police-south-ksp-policeseva-citizen-portal
name: Police Seva — KSP Citizen Centric Portal (e-FIR, complaints)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://policeseva.ksp.gov.in/", "data": "https://policeseva.ksp.gov.in/Login.aspx"}
geo_coverage: Karnataka
geo_granularity: police-station
unit_of_record: case-record
time_start: unknown
time_latest: current
cadence: realtime
lag: n/a
taxonomy: IPC+SLL / BNS+SLL
formats: ["HTML"]
access: login
machine_readable: 1
license: ToU-restricts-reuse
caveats: ["registration/login required; per-user view of one's own complaints only - it is a transaction portal, not a data source", "e-FIR is limited to non-serious categories (vehicle theft, lost property); serious crime still needs an in-person complaint, so any e-FIR-derived series is a biased slice"]
ingest_difficulty: 5
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned 'Citizen Centric Portal - Karnataka State Police - KSP' at policeseva.ksp.gov.in and its Login.aspx. Note the separate second-level domain ksp.gov.in (www.ksp.gov.in also hosts a 'Crime Statistics of Karnataka' page) alongside the primary ksp.karnataka.gov.in.
how_to_obtain: No bulk route. Nothing to ingest without an institutional MoU.
notes: Catalogued so it is not rediscovered as a false lead. Also note the second KSP domain www.ksp.gov.in/Page.aspx?page=Crime+Statistics+of+Karnataka.
```

### 17. Criminal Intelligence Gazette (KSP)
Search index returned the titled KSP page 'Criminal Intelligence Gazette'. Contents not inspected.

**How to obtain:** Direct PDF download from the page.

```
id: state-police-south-ksp-criminal-intelligence-gazette
name: Criminal Intelligence Gazette (KSP)
publisher: Karnataka State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://ksp.karnataka.gov.in/new-page/Criminal%20Intelligence%20Gazette/en"}
geo_coverage: Karnataka
geo_granularity: police-district
unit_of_record: narrative-document
time_start: unknown
time_latest: unknown
cadence: irregular
lag: unknown
taxonomy: IPC+SLL
formats: ["PDF"]
access: open-download
machine_readable: 0
license: unstated
caveats: ["contains wanted-person / suspect material: PII, not publishable", "content and periodicity unverified"]
ingest_difficulty: 4
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled KSP page 'Criminal Intelligence Gazette'. Contents not inspected.
how_to_obtain: Direct PDF download from the page.
notes: Possible source of modus-operandi / offence-location narrative text for enrichment only; high PII risk.
```

### 18. BTP ASTraM — Bengaluru Traffic Police traffic/incident platform (and retired Public Eye)
Play Store listings for BTP ASTraM and Public Eye returned by search; Deccan Herald reporting ('traffic police phase out publiceye app') states BTP will rely exclusively on ASTraM. ASTraM described as an AI/big-data platform with dashboard analytics; no public endpoint documented.

**How to obtain:** Mobile-app API reverse engineering (mitmproxy on an Android emulator) is the only discovery route; treat as Phase 3 and check terms first.

```
id: state-police-south-btp-astram
name: BTP ASTraM — Bengaluru Traffic Police traffic/incident platform (and retired Public Eye)
publisher: Bengaluru Traffic Police
domain: state-police-south
tier: 2
urls: {"landing": "https://play.google.com/store/apps/details?id=com.BTPASTraM"}
geo_coverage: Bengaluru city
geo_granularity: point
unit_of_record: incident-point
time_start: ~2023
time_latest: current
cadence: realtime
lag: minutes
taxonomy: custom (traffic violations, incidents)
formats: ["dashboard-only"]
access: blocked
machine_readable: 0
license: unknown
caveats: ["traffic violations are not crime; mixing them into a safety index would mislead", "Public Eye (com.ichangemycity.publiceye) is RETIRED - BTP no longer monitors it; do not build on it", "the ASTraM 'dashboard analytics' (congestion length, vehicle count/type, safety and road conditions) is internal, not public"]
ingest_difficulty: 5
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Play Store listings for BTP ASTraM and Public Eye returned by search; Deccan Herald reporting ('traffic police phase out publiceye app') states BTP will rely exclusively on ASTraM. ASTraM described as an AI/big-data platform with dashboard analytics; no public endpoint documented.
how_to_obtain: Mobile-app API reverse engineering (mitmproxy on an Android emulator) is the only discovery route; treat as Phase 3 and check terms first.
notes: Catalogued mainly as a warning: the widely-cited Public Eye crowdsourced feed is dead.
```

---

## Tamil Nadu — rating 3/5

Tamil Nadu has the largest force in the region (1,302 law-and-order stations across 39 police
districts and 9 commissionerates) and the thinnest published statistics. The SCRB annual volume
exists — a 2020 edition PDF is mirrored publicly — and OpenCity carries district/city CSVs for
2019–2023 sourced from CCTNS reviews, but the head coverage is shallow (total complaints, murder,
crimes against women, theft/robbery/burglary, suicides, road accidents) rather than the full IPC head
list Karnataka gives you. The citizen portal is a stateful Apache Wicket app whose `wicket/page?N`
URLs are session-scoped, so it defeats naive crawlers. `tn.data.gov.in` exists but surfaced **no**
police or crime dataset in any search run here.

### 19. OpenCity — Tamil Nadu Crime Data (2019-2021 series, 2022, 2023)
Search index returned titled CKAN pages for tamil-nadu-crime-data, -2022 and -2023 plus named resources: 'Tamil Nadu District and Citywise Total Theft and Robbery Cases Data', 'Tamil Nadu District and Citywise Road Accident Deaths in 2019 to 2021', 'District-wise Cases and Deaths by Road and Other Accidents'. Aparup321 note (verified 2026-09-10), item S15: 'TN 2023 (district-wise CSVs, source eservices.tnpolice.gov.in CCTNS reviews)'.

**How to obtain:** CKAN API or direct CSV download; no key.

```
id: state-police-south-opencity-tn-crime
name: OpenCity — Tamil Nadu Crime Data (2019-2021 series, 2022, 2023)
publisher: OpenCity (mirroring Tamil Nadu Police / SCRB CCTNS reviews)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/dataset/tamil-nadu-crime-data-2023", "data": "https://data.opencity.in/dataset/tamil-nadu-crime-data", "api": "https://data.opencity.in/api/3/action/package_show?id=tamil-nadu-crime-data-2023"}
geo_coverage: Tamil Nadu districts and cities
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: 2019
time_latest: 2023 (mirror last updated 2026-01-16)
cadence: annual
lag: 12+ months
taxonomy: IPC+SLL
formats: ["CSV", "PDF", "JSON"]
access: open-download
machine_readable: 4
license: 'Other (Public Domain)' on the mirror
caveats: ["thin head coverage compared with Karnataka: confirmed tables are total complaints registered, murder/homicide, crimes against women, theft/robbery/burglary, suicides by sex, road-accident deaths and causes - not the full IPC head list", "'total complaints registered - written, oral and through different bodies' is a complaint count, NOT an FIR count; do not mix the two series", "mirror, not source of record"]
ingest_difficulty: 1
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned titled CKAN pages for tamil-nadu-crime-data, -2022 and -2023 plus named resources: 'Tamil Nadu District and Citywise Total Theft and Robbery Cases Data', 'Tamil Nadu District and Citywise Road Accident Deaths in 2019 to 2021', 'District-wise Cases and Deaths by Road and Other Accidents'. Aparup321 note (verified 2026-09-10), item S15: 'TN 2023 (district-wise CSVs, source eservices.tnpolice.gov.in CCTNS reviews)'.
how_to_obtain: CKAN API or direct CSV download; no key.
notes: Best machine-readable TN crime source found. District granularity only.
```

### 20. Tamil Nadu Police eServices Citizen Portal (CCTNS) — View FIR / FIR status / arrested persons / UIDB
Wicket URL forms captured verbatim from four independent GitHub repos via code search on 2026-09-19: /CCTNSNICSDC/wicket/page?23, ?37, /CCTNSNICSDC/Index?22, /CCTNSNICSDC/ComplaintRegistrationPage?0, /CCTNSNICSDC/RedirectToNationalCyberCrimeReportingPortal(NCRP). Service list (View FIR, FIR Status, CSR Status, Vehicle Status, Lost Document Report, Road Accident documents, Online Complaints, Un-Identified Dead Body Search, Details of Arrested Persons) from NIC district-portal service pages returned by search.

**How to obtain:** Drive with a real browser session (Playwright), maintaining Wicket page-version state; do not construct wicket/page? URLs by hand. Alternatively RTI to TN SCRB, Chennai for station-month counts.

```
id: state-police-south-tn-eservices-citizen-portal
name: Tamil Nadu Police eServices Citizen Portal (CCTNS) — View FIR / FIR status / arrested persons / UIDB
publisher: Tamil Nadu Police, State Crime Records Bureau
domain: state-police-south
tier: 2
urls: {"landing": "https://eservices.tnpolice.gov.in/", "data": "https://eservices.tnpolice.gov.in/CCTNSNICSDC/", "docs": "https://www.india.gov.in/services/details/view-fir-details-tamil-nadu-police"}
geo_coverage: Tamil Nadu - 39 police districts (incl. 2 railway) + 9 commissionerates; 1,302 L&O + 202 all-women + 243 traffic + 47 railway stations
geo_granularity: police-station
unit_of_record: fir-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: IPC+SLL / BNS+SLL
formats: ["HTML", "PDF"]
access: scrape
machine_readable: 1
license: unstated
caveats: ["APACHE WICKET STATEFUL UI: page URLs are of the form /CCTNSNICSDC/wicket/page?23 and are session-scoped - the numeric page id is NOT a stable deep link, so a naive crawler breaks immediately", "sensitive-category FIRs withheld (2016 SC judgment)", "the tnpolice.gov.in/CCTNSNICSDC/ path is also advertised; two hostnames front the same app"]
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Wicket URL forms captured verbatim from four independent GitHub repos via code search on 2026-09-19: /CCTNSNICSDC/wicket/page?23, ?37, /CCTNSNICSDC/Index?22, /CCTNSNICSDC/ComplaintRegistrationPage?0, /CCTNSNICSDC/RedirectToNationalCyberCrimeReportingPortal(NCRP). Service list (View FIR, FIR Status, CSR Status, Vehicle Status, Lost Document Report, Road Accident documents, Online Complaints, Un-Identified Dead Body Search, Details of Arrested Persons) from NIC district-portal service pages returned by search.
how_to_obtain: Drive with a real browser session (Playwright), maintaining Wicket page-version state; do not construct wicket/page? URLs by hand. Alternatively RTI to TN SCRB, Chennai for station-month counts.
notes: TN SCRB publishes its aggregate 'crime review' out of this same CCTNS instance - see opencity-tn-crime, whose CSVs cite eservices.tnpolice.gov.in as source.
```

### 21. Crime Statistics, Tamil Nadu — State Crime Records Bureau annual report
A direct PDF URL was returned by search with the title 'Statistics Tamil Nadu STATE CRIME RECORDS BUREAU CHENNAI, TAMIL NADU' and filename tn_cr_statistics_2020.pdf, hosted on the OpenCity mirror - proof the annual SCRB statistics volume exists and is publicly redistributable.

**How to obtain:** Download from the OpenCity mirror; for later years request from SCRB Chennai or look under tnpolice.gov.in publications.

```
id: state-police-south-tn-scrb-crime-statistics
name: Crime Statistics, Tamil Nadu — State Crime Records Bureau annual report
publisher: State Crime Records Bureau, Chennai, Tamil Nadu Police
domain: state-police-south
tier: 2
urls: {"landing": "https://www.tnpolice.gov.in/", "data": "https://data.opencity.in/dataset/c894271b-0cbf-4a17-b4fe-96685e125f09/resource/8a8bade6-ce22-4a62-ab77-02a57b287b3d/download/tn_cr_statistics_2020.pdf"}
geo_coverage: Tamil Nadu, district and city-wise
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown (2020 edition confirmed)
time_latest: 2023 (district CSVs on the mirror)
cadence: annual
lag: 6-12 months
taxonomy: IPC+SLL
formats: ["PDF", "CSV"]
access: open-download
machine_readable: 1
license: unstated
caveats: ["SCRB feeds NCRB, so TN SCRB and NCRB numbers for the same year can differ where NCRB applied the principal-offence rule", "city rows (Chennai, Coimbatore, Madurai...) overlap the districts they sit in"]
ingest_difficulty: 3
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: A direct PDF URL was returned by search with the title 'Statistics Tamil Nadu STATE CRIME RECORDS BUREAU CHENNAI, TAMIL NADU' and filename tn_cr_statistics_2020.pdf, hosted on the OpenCity mirror - proof the annual SCRB statistics volume exists and is publicly redistributable.
how_to_obtain: Download from the OpenCity mirror; for later years request from SCRB Chennai or look under tnpolice.gov.in publications.
notes: Locate the native tnpolice.gov.in URL in Phase 2 - the mirror is the only copy confirmed here.
```

### 22. OpenCity — Greater Chennai Police organisation datasets (road accidents, city crime)
Search index returned the organisation page 'Greater Chennai Police (GCP) - Organizations - CKAN' with 7 datasets, and named resources covering total road accidents and deaths 2019-2021 by vehicle type and cause (hit-and-run, poor roads).

**How to obtain:** CKAN API.

```
id: state-police-south-opencity-greater-chennai-police
name: OpenCity — Greater Chennai Police organisation datasets (road accidents, city crime)
publisher: OpenCity (mirroring Greater Chennai Police)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/organization/greater-chennai-police", "data": "https://data.opencity.in/dataset?organization=greater-chennai-police"}
geo_coverage: Chennai (Greater Chennai Police, 132 stations, 4 sub-divisions)
geo_granularity: city
unit_of_record: aggregate-count
time_start: 2019
time_latest: 2023
cadence: annual
lag: 12+ months
taxonomy: custom
formats: ["CSV", "PDF"]
access: open-download
machine_readable: 4
license: 'Other (Public Domain)' on the mirror
caveats: ["7 datasets only, and mostly road-accident rather than crime tables", "city aggregate: no zone or station breakdown"]
ingest_difficulty: 1
priority: 3
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the organisation page 'Greater Chennai Police (GCP) - Organizations - CKAN' with 7 datasets, and named resources covering total road accidents and deaths 2019-2021 by vehicle type and cause (hit-and-run, poor roads).
how_to_obtain: CKAN API.
notes: Useful for a road-safety layer; weak for crime.
```

### 23. Open Government Data Portal of Tamil Nadu (tn.data.gov.in)
Search index returned tn.data.gov.in and its /about page ('portal for supporting Open Data initiative of Government of Tamil Nadu ... Departments/Organizations of Government of Tamil Nadu to publish datasets'), and the portal is registered at re3data.org (r3d100012682) and dateno.io. No crime/police catalogue entry appeared in crime-targeted searches.

**How to obtain:** Register at data.gov.in for an API key, then /resource/<id>?api-key=...&format=json.

```
id: state-police-south-tn-open-government-data-portal
name: Open Government Data Portal of Tamil Nadu (tn.data.gov.in)
publisher: Tamil Nadu Information Technology Dept / TNeGA, on the NIC OGD platform
domain: state-police-south
tier: 1
urls: {"landing": "https://tn.data.gov.in/", "docs": "https://tn.data.gov.in/about"}
geo_coverage: Tamil Nadu
geo_granularity: state
unit_of_record: aggregate-count
time_start: 2021
time_latest: unknown
cadence: irregular
lag: unknown
taxonomy: n/a
formats: ["CSV", "XLSX", "JSON"]
access: api-key
machine_readable: 4
license: GODL-India
caveats: ["NEGATIVE FINDING: no police or crime dataset surfaced on tn.data.gov.in in any search performed; TN crime data reaches the public through tnpolice.gov.in and the OpenCity mirror instead", "NIC OGD instances require a free API key for the data API"]
ingest_difficulty: 2
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned tn.data.gov.in and its /about page ('portal for supporting Open Data initiative of Government of Tamil Nadu ... Departments/Organizations of Government of Tamil Nadu to publish datasets'), and the portal is registered at re3data.org (r3d100012682) and dateno.io. No crime/police catalogue entry appeared in crime-targeted searches.
how_to_obtain: Register at data.gov.in for an API key, then /resource/<id>?api-key=...&format=json.
notes: Re-check with an in-country browser for a 'Home / Police' department facet before writing TN off as portal-less.
```

---

## Telangana — rating 3/5 (reputation exceeds reality)

**This is the most important correction in this dossier.** Telangana's reputation as India's most
open state for crime data does not survive contact with the portal. `data.telangana.gov.in` is a real,
well-built DKAN v2 instance with a documented JSON API and ~637–658 datasets — and, as far as every
search run here could establish, **not one crime dataset**. The only police holding is
`/dataset/police-stations`, reported to be nothing more than a count of stations per district: no
names, no addresses, no coordinates. What Telangana *does* have is (a) the fastest annual crime
publication in India — the DGP's Annual Report lands within days of year end, broken down by
commissionerate — and (b) an FIR download service issuing digitally signed PDFs. Both are
police-owned, neither is open data. The ICCC, which holds the richest incident data in the country,
publishes nothing. Downgrade Telangana from "most open" to "fast but closed".

### 24. Telangana Police Annual Report (DGP's annual crime review)
Multiple independent outlets report the 2024 edition: released by DGP Jitender Reddy on 29 December 2024; total cases 1,69,477 in 2024 vs 1,38,312 in 2023 (+22.5%); cybercrime 25,184 vs 17,571 (+43.33%) with commissionerate splits Cyberabad 25,112 / Hyderabad 20,299 / Rachakonda 14,815; Rs 180 crore refunded to cyber victims; 14,984 SIMs, 9,811 IMEIs and 1,825 URLs blocked. Technology stack reviewed in the report: CCTNS, TG-COP, Hawkeye. Telangana described as the first state to issue digitally signed FIR copies under the new criminal laws.

**How to obtain:** Ask the DGP's PRO / Telangana SCRB for the PDF, or RTI to the SCRB. Failing that, reconstruct commissionerate tables from the press coverage (citing the report, not the outlet).

```
id: state-police-south-telangana-police-annual-report
name: Telangana Police Annual Report (DGP's annual crime review)
publisher: Telangana State Police, DGP office
domain: state-police-south
tier: 2
urls: {"landing": "https://www.tspolice.gov.in/"}
geo_coverage: Telangana - statewide, broken down by commissionerate (Hyderabad, Cyberabad, Rachakonda, Warangal, Malkajgiri, Ramagundam, Nizamabad) and district
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: 2024 edition, released 29 December 2024
cadence: annual
lag: ~0 months (released in the last days of the reporting year)
taxonomy: IPC+SLL / BNS+SLL
formats: ["PDF"]
access: on-request
machine_readable: 1
license: unstated
caveats: ["FASTEST ANNUAL RELEASE IN INDIA (published within days of year-end) but therefore PROVISIONAL - late FIR registrations are not reflected; numbers will not match NCRB's later figures", "circulated as a press release; a stable public download URL was NOT confirmed", "criticised in reporting for selective coverage (e.g. silence on specific incidents)"]
ingest_difficulty: 4
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Multiple independent outlets report the 2024 edition: released by DGP Jitender Reddy on 29 December 2024; total cases 1,69,477 in 2024 vs 1,38,312 in 2023 (+22.5%); cybercrime 25,184 vs 17,571 (+43.33%) with commissionerate splits Cyberabad 25,112 / Hyderabad 20,299 / Rachakonda 14,815; Rs 180 crore refunded to cyber victims; 14,984 SIMs, 9,811 IMEIs and 1,825 URLs blocked. Technology stack reviewed in the report: CCTNS, TG-COP, Hawkeye. Telangana described as the first state to issue digitally signed FIR copies under the new criminal laws.
how_to_obtain: Ask the DGP's PRO / Telangana SCRB for the PDF, or RTI to the SCRB. Failing that, reconstruct commissionerate tables from the press coverage (citing the report, not the outlet).
notes: Commissionerate-level, annual, near-zero lag. This is Telangana's real crime publication - not the open data portal.
```

### 25. Telangana Police citizen portal / CCTNS-TSP — FIR search and download
Search index returned 'Telangana State Police - Official Website' at www.tspolice.gov.in and the JSP entry point /jsp/homePage?method=getHomePageElements; also the HRMS instance tspolice.cgg.gov.in and the cyber bureau at tgcsb.tspolice.gov.in. Reporting confirms FIRs are downloadable from the Telangana Police website via the CCTNS-TSP portal and that Telangana was first to issue digitally signed FIR copies. A cybersecurity outlet reports the site was restored after an incident with security upgraded.

**How to obtain:** Browser session against the citizen portal; select district + station + FIR no/date. Expect a captcha. Confirm robots.txt and the WAF posture before any automation.

```
id: state-police-south-tspolice-citizen-fir
name: Telangana Police citizen portal / CCTNS-TSP — FIR search and download
publisher: Telangana State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://www.tspolice.gov.in/", "data": "https://www.tspolice.gov.in/jsp/homePage?method=getHomePageElements"}
geo_coverage: Telangana, 709 police stations across 33 districts and 7 commissionerates
geo_granularity: police-station
unit_of_record: fir-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: BNS+SLL (IPC before 2024-07-01)
formats: ["PDF", "HTML"]
access: scrape
machine_readable: 1
license: unstated
caveats: ["Telangana issues DIGITALLY SIGNED FIR PDFs - good for provenance, but the signature layer can defeat naive text extraction", "site was defaced/taken down and restored with 'security upgraded' in a recent incident, so expect WAF/bot protection", "sensitive-category FIRs withheld", "TS->TG rebranding means both tspolice.gov.in and telanganapolice branding appear; tspolice.gov.in is still the live host"]
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned 'Telangana State Police - Official Website' at www.tspolice.gov.in and the JSP entry point /jsp/homePage?method=getHomePageElements; also the HRMS instance tspolice.cgg.gov.in and the cyber bureau at tgcsb.tspolice.gov.in. Reporting confirms FIRs are downloadable from the Telangana Police website via the CCTNS-TSP portal and that Telangana was first to issue digitally signed FIR copies. A cybersecurity outlet reports the site was restored after an incident with security upgraded.
how_to_obtain: Browser session against the citizen portal; select district + station + FIR no/date. Expect a captcha. Confirm robots.txt and the WAF posture before any automation.
notes: Sibling city portals: hyderabadpolice.cgg.gov.in (Hyderabad City) and cyberabadpolice.gov.in (Cyberabad).
```

### 26. Telangana Open Data Portal (data.telangana.gov.in) — DKAN v2 API
API surface captured verbatim from six independent GitHub repos via code search on 2026-09-19: base https://data.telangana.gov.in/api/1/ with /search?fulltext=<q>, /metastore/schemas/dataset/items/<uuid>[?show-reference-ids=true], /metastore/schemas/dataset/items/<uuid>/docs (OpenAPI), /datastore/query/<distribution-uuid>?count=true&results=true&schema=true&keys=true&format=csv, /datastore/sql?query=<sql>&show_db_columns=true, plus a legacy /api/action/datastore/search.json?resource_id=&limit=. One repo (SundareshPrasanna/neer-vazhvu docs/cities/hyderabad/data-sources.md) states flatly: 'DKAN, not CKAN. API base /api/1; GET /api/1/search?fulltext=<q> works. The OpenCity CKAN recipe does not transfer.' Portal itself was egress-blocked from this sandbox.

**How to obtain:** GET https://data.telangana.gov.in/api/1/search?fulltext=crime (and =police, =FIR, =law) to settle definitively whether any crime dataset exists. No key needed.

```
id: state-police-south-telangana-open-data-portal
name: Telangana Open Data Portal (data.telangana.gov.in) — DKAN v2 API
publisher: Government of Telangana (Open Data Policy)
domain: state-police-south
tier: 1
urls: {"landing": "https://data.telangana.gov.in/", "api": "https://data.telangana.gov.in/api/1/search?fulltext=police", "docs": "https://data.telangana.gov.in/api/1/metastore/schemas/dataset/items/{dataset_uuid}/docs"}
geo_coverage: Telangana
geo_granularity: district
unit_of_record: aggregate-count
time_start: 2015
time_latest: current
cadence: irregular
lag: varies by department
taxonomy: n/a
formats: ["CSV", "JSON", "XLSX"]
access: open-download
machine_readable: 5
license: GODL-India
caveats: ["MAJOR NEGATIVE FINDING: despite Telangana's reputation as India's most open state, the ONLY police dataset surfaced is 'Police Stations', and a DataMeet discussion describes it as aggregate counts of police stations by district - 'limited granular value'. No crime/FIR/offence dataset was found on the portal.", "it is DKAN, NOT CKAN - the /api/3/action/... CKAN recipe does not work here", "~637-658 datasets in total, dominated by power, weather, transport, land records and industry"]
ingest_difficulty: 1
priority: 3
verification: CITED
checked_on: 2026-09-19
evidence: API surface captured verbatim from six independent GitHub repos via code search on 2026-09-19: base https://data.telangana.gov.in/api/1/ with /search?fulltext=<q>, /metastore/schemas/dataset/items/<uuid>[?show-reference-ids=true], /metastore/schemas/dataset/items/<uuid>/docs (OpenAPI), /datastore/query/<distribution-uuid>?count=true&results=true&schema=true&keys=true&format=csv, /datastore/sql?query=<sql>&show_db_columns=true, plus a legacy /api/action/datastore/search.json?resource_id=&limit=. One repo (SundareshPrasanna/neer-vazhvu docs/cities/hyderabad/data-sources.md) states flatly: 'DKAN, not CKAN. API base /api/1; GET /api/1/search?fulltext=<q> works. The OpenCity CKAN recipe does not transfer.' Portal itself was egress-blocked from this sandbox.
how_to_obtain: GET https://data.telangana.gov.in/api/1/search?fulltext=crime (and =police, =FIR, =law) to settle definitively whether any crime dataset exists. No key needed.
notes: FIRST ACTION IN PHASE 2 FOR TELANGANA: run that one API call. It is cheap and it resolves the single biggest open question in the brief.
```

### 27. Police Stations — Telangana Open Data Portal dataset
Dataset page title 'Telangana Open Data Portal' at /dataset/police-stations returned by two independent domain-filtered searches. A DataMeet mailing-list thread on the Telangana DKAN portal is summarised as noting the Police Stations dataset 'has been criticised as providing only aggregate numbers of police stations by district, which has limited granular value'. Page not fetchable from this sandbox; the aggregate-only claim is second-hand and should be re-verified.

**How to obtain:** GET the dataset's /api distribution and read the schema: https://data.telangana.gov.in/api/1/metastore/schemas/dataset/items/<uuid>

```
id: state-police-south-telangana-police-stations-dataset
name: Police Stations — Telangana Open Data Portal dataset
publisher: Government of Telangana / Home Department
domain: state-police-south
tier: 1
urls: {"landing": "https://data.telangana.gov.in/dataset/police-stations"}
geo_coverage: Telangana, 33 districts (709 police stations statewide)
geo_granularity: district
unit_of_record: aggregate-count
time_start: unknown
time_latest: unknown
cadence: irregular
lag: unknown
taxonomy: n/a
formats: ["CSV", "JSON"]
access: open-download
machine_readable: 5
license: GODL-India
caveats: ["NOT A ROSTER: reported to contain only the NUMBER of police stations per district, with no station names, addresses, phones or coordinates - it cannot be used to place stations on a map", "this is the dataset most often cited as evidence that 'Telangana publishes police data'; the citation oversells it"]
ingest_difficulty: 1
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Dataset page title 'Telangana Open Data Portal' at /dataset/police-stations returned by two independent domain-filtered searches. A DataMeet mailing-list thread on the Telangana DKAN portal is summarised as noting the Police Stations dataset 'has been criticised as providing only aggregate numbers of police stations by district, which has limited granular value'. Page not fetchable from this sandbox; the aggregate-only claim is second-hand and should be re-verified.
how_to_obtain: GET the dataset's /api distribution and read the schema: https://data.telangana.gov.in/api/1/metastore/schemas/dataset/items/<uuid>
notes: Station count (709) from the Telangana Police Wikipedia article, fetched live 2026-09-19.
```

### 28. Hyderabad City Police eTools — View / Print FIR
Search index returned the National Portal of India service entry 'Login for View / Print FIR with the Hyderabad City Police, Telangana' and the live host 'Hyderabad City Police, Telangana State - Official eTools Site - By Centre for Good Governance' at hyderabadpolice.cgg.gov.in. Zone/station counts from the Hyderabad City Police Wikipedia article fetched live 2026-09-19.

**How to obtain:** Registered citizen login required. For bulk, RTI to the Commissioner of Police, Hyderabad for station-wise monthly FIR counts.

```
id: state-police-south-hyderabad-city-police-fir
name: Hyderabad City Police eTools — View / Print FIR
publisher: Hyderabad City Police (built by Centre for Good Governance)
domain: state-police-south
tier: 2
urls: {"landing": "https://hyderabadpolice.cgg.gov.in/", "docs": "https://www.india.gov.in/services/details/login-for-view-print-fir-with-the-hyderabad-city-police-telangana"}
geo_coverage: Hyderabad city police commissionerate - 6 zones, 105 police stations
geo_granularity: police-station
unit_of_record: fir-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: BNS+SLL
formats: ["PDF", "HTML"]
access: login
machine_readable: 1
license: unstated
caveats: ["the national services catalogue lists this explicitly as 'Login for View / Print FIR' - a login wall, unlike Kerala's open FIR search", "separate stack (cgg.gov.in) from the state portal: two different scrapers needed"]
ingest_difficulty: 5
priority: 3
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the National Portal of India service entry 'Login for View / Print FIR with the Hyderabad City Police, Telangana' and the live host 'Hyderabad City Police, Telangana State - Official eTools Site - By Centre for Good Governance' at hyderabadpolice.cgg.gov.in. Zone/station counts from the Hyderabad City Police Wikipedia article fetched live 2026-09-19.
how_to_obtain: Registered citizen login required. For bulk, RTI to the Commissioner of Police, Hyderabad for station-wise monthly FIR counts.
notes: Also hyderabadpolice.gov.in (public site) and a 'Lost Report' mobile app.
```

### 29. Telangana Cyber Security Bureau (TGCSB)
Search index returned the live host 'tgcsb - Telangana Police' at tgcsb.tspolice.gov.in. Newsonair reporting confirms TGCSB operations (165 arrests in six months as of Nov 2024).

**How to obtain:** Direct fetch of the bureau's statistics/press pages.

```
id: state-police-south-tgcsb
name: Telangana Cyber Security Bureau (TGCSB)
publisher: Telangana State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://tgcsb.tspolice.gov.in/"}
geo_coverage: Telangana
geo_granularity: state
unit_of_record: aggregate-count
time_start: 2024
time_latest: current
cadence: irregular
lag: unknown
taxonomy: custom (cyber offence categories)
formats: ["HTML", "PDF"]
access: open-download
machine_readable: 2
license: unstated
caveats: ["cybercrime has no meaningful physical location - the victim's address is not where the offence happened, so cyber counts must be kept OUT of any neighbourhood-safety layer", "TGCSB is new (2024); series is short"]
ingest_difficulty: 3
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the live host 'tgcsb - Telangana Police' at tgcsb.tspolice.gov.in. Newsonair reporting confirms TGCSB operations (165 arrests in six months as of Nov 2024).
how_to_obtain: Direct fetch of the bureau's statistics/press pages.
notes: Relevant for a separate cyber-fraud layer, not the street map.
```

### 30. Telangana Integrated Command and Control Centre (TGICCC), Hyderabad
Wikipedia article on the TGICCC fetched live 2026-09-19: inaugurated 4 Aug 2022, >Rs 600 crore, 6.42 lakh sq ft across five towers, integrates 'over a lakh CCTV cameras state-wide', main node for Dial 100/112, uses 'advanced data analytics and artificial intelligence modules'. The article contains NO mention of any public dashboard or data portal, and none surfaced in search.

**How to obtain:** RTI under the RTI Act 2005 to the PIO, Telangana State Police HQ / TGICCC, asking for Dial-112 call volumes aggregated by police station and month for the last 36 months, with the CCTV-derived data expressly excluded to avoid a s.8 exemption refusal. Expect partial refusal on security grounds.

```
id: state-police-south-tgiccc
name: Telangana Integrated Command and Control Centre (TGICCC), Hyderabad
publisher: Telangana State Police
domain: state-police-south
tier: 2
urls: {"landing": "https://www.tspolice.gov.in/"}
geo_coverage: Telangana (Hyderabad-centred), 100,000+ CCTV cameras
geo_granularity: point
unit_of_record: incident-point
time_start: 2022-08-04
time_latest: current
cadence: realtime
lag: none
taxonomy: custom
formats: ["dashboard-only"]
access: rti-only
machine_readable: 0
license: unknown
caveats: ["NO PUBLIC-FACING DASHBOARD OR DATA PORTAL EXISTS - this is an internal policing facility", "Dial 100/112 call data held here would be the single richest incident-point source in India and is entirely unpublished", "surveillance-derived data raises privacy issues that would need explicit legal sign-off even if released"]
ingest_difficulty: 5
priority: 1
verification: CITED
checked_on: 2026-09-19
evidence: Wikipedia article on the TGICCC fetched live 2026-09-19: inaugurated 4 Aug 2022, >Rs 600 crore, 6.42 lakh sq ft across five towers, integrates 'over a lakh CCTV cameras state-wide', main node for Dial 100/112, uses 'advanced data analytics and artificial intelligence modules'. The article contains NO mention of any public dashboard or data portal, and none surfaced in search.
how_to_obtain: RTI under the RTI Act 2005 to the PIO, Telangana State Police HQ / TGICCC, asking for Dial-112 call volumes aggregated by police station and month for the last 36 months, with the CCTV-derived data expressly excluded to avoid a s.8 exemption refusal. Expect partial refusal on security grounds.
notes: Documented as a negative finding so the ICCC is not chased again as an open source.
```

---

## Andhra Pradesh — rating 3/5

AP's redeeming feature is architectural: its police site is an old-style stateless JSP app, so
`homePage.do?method=crimeStatistics` and `homePage.do?method=getCrimeInAP` are plain GET-able URLs
rather than session-bound widgets. That makes AP unusually cheap to check and probably cheap to
scrape. FIR search by district + station + date + FIR number is live. Against that: the period,
cadence and granularity of the crime-statistics pages are entirely unverified, and AP carries two
structural breaks a map must handle — the 2014 bifurcation (pre-2014 "AP" includes Telangana) and
the 2022 reorganisation from 13 to 26 districts.

### 31. Andhra Pradesh Police — FIR search / view / download by district, station and date
Search index returned the live JSP 'Welcome to AP police.' at www.appolice.gov.in/jsp/FIRComplainant.jsp and the citizen portal root citizen.appolice.gov.in; multiple how-to guides describe the flow as select district -> select police station -> enter FIR registration date -> enter FIR number and year -> view/download FIR copy.

**How to obtain:** Form POST per (district, station, date). For bulk, RTI to the AP SCRB / DGP office, Mangalagiri for station-wise monthly FIR counts.

```
id: state-police-south-ap-fir-search
name: Andhra Pradesh Police — FIR search / view / download by district, station and date
publisher: Andhra Pradesh Police
domain: state-police-south
tier: 2
urls: {"landing": "https://citizen.appolice.gov.in/", "data": "https://www.appolice.gov.in/jsp/FIRComplainant.jsp"}
geo_coverage: Andhra Pradesh, all police stations
geo_granularity: police-station
unit_of_record: fir-record
time_start: unknown
time_latest: current
cadence: daily
lag: days
taxonomy: BNS+SLL (IPC before 2024-07-01)
formats: ["PDF", "HTML"]
access: scrape
machine_readable: 1
license: unstated
caveats: ["search requires FIR number and year in addition to district/station/date - no bulk listing mode confirmed", "sensitive-category FIRs withheld", "FIR PDFs in Telugu and English"]
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the live JSP 'Welcome to AP police.' at www.appolice.gov.in/jsp/FIRComplainant.jsp and the citizen portal root citizen.appolice.gov.in; multiple how-to guides describe the flow as select district -> select police station -> enter FIR registration date -> enter FIR number and year -> view/download FIR copy.
how_to_obtain: Form POST per (district, station, date). For bulk, RTI to the AP SCRB / DGP office, Mangalagiri for station-wise monthly FIR counts.
notes: Together with Kerala THUNA and Karnataka firsearch this is one of three station-addressable FIR endpoints in the region.
```

### 32. Crime Statistics / Crime in AP — Andhra Pradesh Police
Search index returned three distinct live endpoints with police-branded titles: 'Crime Statistics - Andhra Pradesh Police' at citizen.appolice.gov.in/jsp/homePage.do?method=crimeStatistics, 'Andhra Pradesh Police' at www.appolice.gov.in/jsp/homePage.do?method=crimeStatistics, and appolice.gov.in/jsp/homePage.do?method=getCrimeInAP. Pages not fetchable from this sandbox.

**How to obtain:** Direct GET on the JSP endpoints; they are classic stateless query-string servlets, which makes them unusually scrape-friendly.

```
id: state-police-south-ap-crime-statistics
name: Crime Statistics / Crime in AP — Andhra Pradesh Police
publisher: Andhra Pradesh Police
domain: state-police-south
tier: 2
urls: {"landing": "https://citizen.appolice.gov.in/jsp/homePage.do?method=crimeStatistics", "data": "https://appolice.gov.in/jsp/homePage.do?method=getCrimeInAP"}
geo_coverage: Andhra Pradesh (districts + Visakhapatnam and Vijayawada city commissionerates)
geo_granularity: police-district
unit_of_record: aggregate-count
time_start: unknown
time_latest: unknown
cadence: irregular
lag: unknown
taxonomy: IPC+SLL / BNS+SLL
formats: ["HTML", "PDF"]
access: open-download
machine_readable: 2
license: unstated
caveats: ["period covered and update cadence are UNVERIFIED - two distinct endpoints (crimeStatistics and getCrimeInAP) may serve different vintages", "AP's 2022 district reorganisation (13 -> 26 districts) breaks any pre/post district join; police districts did not move in lockstep with revenue districts", "2014 bifurcation: pre-2014 'Andhra Pradesh' series include Telangana"]
ingest_difficulty: 3
priority: 4
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned three distinct live endpoints with police-branded titles: 'Crime Statistics - Andhra Pradesh Police' at citizen.appolice.gov.in/jsp/homePage.do?method=crimeStatistics, 'Andhra Pradesh Police' at www.appolice.gov.in/jsp/homePage.do?method=crimeStatistics, and appolice.gov.in/jsp/homePage.do?method=getCrimeInAP. Pages not fetchable from this sandbox.
how_to_obtain: Direct GET on the JSP endpoints; they are classic stateless query-string servlets, which makes them unusually scrape-friendly.
notes: HIGHEST-VALUE QUICK CHECK FOR AP - stateless JSP URLs mean one fetch settles granularity and period.
```

### 33. Crime Investigation Department, Andhra Pradesh — statistics
Search index returned the titled page 'Crime Investigation Department - Andhra Pradesh' at cid.appolice.gov.in/cid/statistics. Contents not inspected.

**How to obtain:** Direct GET.

```
id: state-police-south-ap-cid-statistics
name: Crime Investigation Department, Andhra Pradesh — statistics
publisher: AP CID
domain: state-police-south
tier: 2
urls: {"landing": "https://cid.appolice.gov.in/cid/statistics"}
geo_coverage: Andhra Pradesh
geo_granularity: state
unit_of_record: aggregate-count
time_start: unknown
time_latest: unknown
cadence: irregular
lag: unknown
taxonomy: IPC+SLL
formats: ["HTML", "PDF"]
access: open-download
machine_readable: 2
license: unstated
caveats: ["CID handles only referred/specialised cases (economic offences, major crime) - counts are a small, non-representative slice of total crime and must never be read as state totals"]
ingest_difficulty: 2
priority: 3
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the titled page 'Crime Investigation Department - Andhra Pradesh' at cid.appolice.gov.in/cid/statistics. Contents not inspected.
how_to_obtain: Direct GET.
notes: Useful for an economic-offence layer only.
```

### 34. Disha SOS / Suraksha (AP Police Seva) citizen safety apps
Play Store (gov.appolice.citizenapp, 'Suraksha') and App Store (id1555415773, 'AP Police Seva' / 'Suraksha Citizen Services') listings returned by search; press reporting on the Police Seva launch describes 87 services connecting all police stations, and reports Disha SOS at 11 lakh downloads with 568 complaints and 117 FIRs registered.

**How to obtain:** The only legitimate route to any of this is an RTI or an MoU with the AP Police for the nearby-police-station geodatabase (not the SOS records).

```
id: state-police-south-ap-disha-suraksha
name: Disha SOS / Suraksha (AP Police Seva) citizen safety apps
publisher: Andhra Pradesh Police
domain: state-police-south
tier: 2
urls: {"landing": "https://play.google.com/store/apps/details?id=gov.appolice.citizenapp", "docs": "https://apps.apple.com/us/app/suraksha-citizen-services/id1555415773"}
geo_coverage: Andhra Pradesh
geo_granularity: point
unit_of_record: incident-point
time_start: 2019 (Disha) / 2021 (Police Seva)
time_latest: current
cadence: realtime
lag: none
taxonomy: custom
formats: ["dashboard-only"]
access: blocked
machine_readable: 0
license: unknown
caveats: ["SOS alert locations are victim-reported distress points, not verified offences - publishing them on a map would be both inaccurate and a serious privacy breach", "no public aggregate of SOS volumes found", "app ships a 'nearby police stations' feature, implying an internal station geodatabase that is not published"]
ingest_difficulty: 5
priority: 1
verification: CITED
checked_on: 2026-09-19
evidence: Play Store (gov.appolice.citizenapp, 'Suraksha') and App Store (id1555415773, 'AP Police Seva' / 'Suraksha Citizen Services') listings returned by search; press reporting on the Police Seva launch describes 87 services connecting all police stations, and reports Disha SOS at 11 lakh downloads with 568 complaints and 117 FIRs registered.
how_to_obtain: The only legitimate route to any of this is an RTI or an MoU with the AP Police for the nearby-police-station geodatabase (not the SOS records).
notes: Worth one RTI asking only for the station master list with coordinates that powers 'nearby police stations'.
```

---

## Puducherry, Andaman & Nicobar, Lakshadweep — rating 1/5 each

All three are **`access: rti-only`**. None publishes a crime statistic. Each police site is a
services site (FIR registration, verification requests, stolen-vehicle lookups) with no data layer.
A&N's SCRB states its job is to collect crime data from all 21 police stations and maintain records —
and publishes none of it; the only public A&N numbers sit inside the MHA Annual Report. Lakshadweep's
CCTNS page documents that FIRs have run through Central CAS 4.5 since 23 December 2015 and exposes
nothing. All three are small enough that a *single* RTI per UT could return the complete
station-level series — 21 stations in A&N, 16 in Lakshadweep. For Puducherry the better route is the
Directorate of Economics and Statistics Statistical Abstract, which carries a crime chapter compiled
from police returns.

### 35. Puducherry Police — official site (no published crime statistics)
Search index returned the live site police.py.gov.in and the legacy police.puducherry.gov.in, plus the Directorate of Economics and Statistics annual report page (statistics.py.gov.in/annual-report) and Indiastat's derived crime-and-law tables for Puducherry - but NO police-published crime statistics page. Wikipedia (fetched live 2026-09-19) confirms jurisdiction over Puducherry, Yanam, Karaikal and Mahe and cites no crime-data URL.

**How to obtain:** RTI under the RTI Act 2005 to the PIO, Office of the Director General of Police, Puducherry: request station-wise counts of FIRs registered per month for the last 36 months, broken down by major head (body/property/women/children), in machine-readable form. Also check the DES Puducherry annual report and Statistical Abstract, which routinely carries a crime chapter compiled from police returns.

```
id: state-police-south-puducherry-police
name: Puducherry Police — official site (no published crime statistics)
publisher: Puducherry Police, UT of Puducherry
domain: state-police-south
tier: 2
urls: {"landing": "https://police.py.gov.in/", "docs": "https://statistics.py.gov.in/annual-report"}
geo_coverage: UT of Puducherry - 4 non-contiguous regions: Puducherry, Karaikal, Yanam, Mahe
geo_granularity: state
unit_of_record: aggregate-count
time_start: n/a
time_latest: n/a
cadence: irregular
lag: n/a
taxonomy: n/a
formats: ["HTML"]
access: rti-only
machine_readable: 0
license: n/a
caveats: ["NEGATIVE FINDING: no crime statistics publication, dashboard or downloadable crime table was found for Puducherry Police - the site carries services (FIR registration, complaint tracking, tenant/employee verification, missing persons, stolen vehicles), not data", "the UT's four regions are geographically separated and embedded in TN and AP, so any state-level number is nearly meaningless for a map", "the legacy host police.puducherry.gov.in also resolves - two domains for one force"]
ingest_difficulty: 5
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the live site police.py.gov.in and the legacy police.puducherry.gov.in, plus the Directorate of Economics and Statistics annual report page (statistics.py.gov.in/annual-report) and Indiastat's derived crime-and-law tables for Puducherry - but NO police-published crime statistics page. Wikipedia (fetched live 2026-09-19) confirms jurisdiction over Puducherry, Yanam, Karaikal and Mahe and cites no crime-data URL.
how_to_obtain: RTI under the RTI Act 2005 to the PIO, Office of the Director General of Police, Puducherry: request station-wise counts of FIRs registered per month for the last 36 months, broken down by major head (body/property/women/children), in machine-readable form. Also check the DES Puducherry annual report and Statistical Abstract, which routinely carries a crime chapter compiled from police returns.
notes: Best realistic route is the Directorate of Economics and Statistics Statistical Abstract, not the police site.
```

### 36. Andaman & Nicobar Police — official site and SCRB (no published crime statistics)
Search index returned both live hosts and the CID/support-units pages; the SCRB objective sentence quoted above came back in the same search summary. The A&N Police Wikipedia article (fetched live 2026-09-19) gives 3 police districts, 21+3 stations, 24 outposts, 12 Jarawa Protection Posts, 4,130 personnel, and sources its crime-rate table to the MHA Annual Report 2021-22 (www.mha.gov.in/sites/default/files/AnnualReport202122_24112022[1]) - i.e. the UT's own force publishes no table.

**How to obtain:** RTI to the PIO, Office of the DGP, Andaman & Nicobar Police, Port Blair: station-wise monthly FIR counts by major head for the last 36 months. A&N is a UT administered by MHA, so a parallel RTI to MHA is a viable fallback.

```
id: state-police-south-andaman-nicobar-police
name: Andaman & Nicobar Police — official site and SCRB (no published crime statistics)
publisher: Andaman and Nicobar Islands Police
domain: state-police-south
tier: 2
urls: {"landing": "https://police.andamannicobar.gov.in/index.php/en/", "docs": "https://police.andaman.gov.in/index.php/en/support-units/criminal-investigation-department.html"}
geo_coverage: A&N Islands - 3 police districts (South Andaman, North & Middle Andaman, Nicobar), 21 territorial + 3 special police stations, 24 outposts
geo_granularity: state
unit_of_record: aggregate-count
time_start: n/a
time_latest: 2021-22 (only via the MHA Annual Report)
cadence: annual
lag: 12-24 months
taxonomy: IPC+SLL
formats: ["PDF", "HTML"]
access: rti-only
machine_readable: 0
license: n/a
caveats: ["NEGATIVE FINDING: the A&N SCRB's stated job is 'to collect crime data from all Police Stations of A&N Islands and to maintain records' - but nothing station-wise or district-wise is published; the only public numbers are UT totals inside the MHA Annual Report and NCRB", "two live domains (police.andamannicobar.gov.in and the older police.andaman.gov.in) serve overlapping content", "tiny population (~4 lakh) means small-number volatility - any rate per 100k will swing wildly year to year and must be suppressed or smoothed"]
ingest_difficulty: 5
priority: 2
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned both live hosts and the CID/support-units pages; the SCRB objective sentence quoted above came back in the same search summary. The A&N Police Wikipedia article (fetched live 2026-09-19) gives 3 police districts, 21+3 stations, 24 outposts, 12 Jarawa Protection Posts, 4,130 personnel, and sources its crime-rate table to the MHA Annual Report 2021-22 (www.mha.gov.in/sites/default/files/AnnualReport202122_24112022[1]) - i.e. the UT's own force publishes no table.
how_to_obtain: RTI to the PIO, Office of the DGP, Andaman & Nicobar Police, Port Blair: station-wise monthly FIR counts by major head for the last 36 months. A&N is a UT administered by MHA, so a parallel RTI to MHA is a viable fallback.
notes: 21 stations across three districts is a small enough universe that one RTI could yield a complete station-level dataset.
```

### 37. Lakshadweep Police / CCTNS page (no published crime statistics)
Search index returned the live host lakshadweeppolice.gov.in, its /cctns page ('FIR registrations in all Police Stations are processed through Central CAS (4.5) system from 23rd December 2015 onwards'), and the UT department pages at lakshadweep.gov.in. No statistics page appeared. Indiastat carries derived Lakshadweep crime-and-law tables, which are NCRB-derived, not police-published.

**How to obtain:** RTI to the PIO, Lakshadweep Police, Kavaratti for station-wise annual FIR counts since 2016. With 16 stations the whole dataset fits on one page.

```
id: state-police-south-lakshadweep-police-cctns
name: Lakshadweep Police / CCTNS page (no published crime statistics)
publisher: Lakshadweep Police, UT of Lakshadweep
domain: state-police-south
tier: 2
urls: {"landing": "https://lakshadweeppolice.gov.in/", "data": "https://lakshadweeppolice.gov.in/cctns", "docs": "https://lakshadweep.gov.in/departments/police/"}
geo_coverage: UT of Lakshadweep - 9 police stations + 7 coastal police stations, HQ Kavaratti; population ~70,000 across 32 sq km
geo_granularity: state
unit_of_record: aggregate-count
time_start: 2015-12-23 (CCTNS/CAS 4.5 go-live)
time_latest: n/a (nothing published)
cadence: irregular
lag: n/a
taxonomy: IPC+SLL
formats: ["HTML"]
access: rti-only
machine_readable: 0
license: n/a
caveats: ["NEGATIVE FINDING: no crime statistics are published; the CCTNS page documents that FIRs are processed through Central CAS 4.5 from 23 December 2015 but exposes no data", "lowest crime rate in India with heinous crime rare - at this population, counts will be single digits and MUST be suppressed rather than mapped", "an island UT with no contiguous geography; a 'neighbourhood safety' map is close to meaningless here"]
ingest_difficulty: 5
priority: 1
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned the live host lakshadweeppolice.gov.in, its /cctns page ('FIR registrations in all Police Stations are processed through Central CAS (4.5) system from 23rd December 2015 onwards'), and the UT department pages at lakshadweep.gov.in. No statistics page appeared. Indiastat carries derived Lakshadweep crime-and-law tables, which are NCRB-derived, not police-published.
how_to_obtain: RTI to the PIO, Lakshadweep Police, Kavaratti for station-wise annual FIR counts since 2016. With 16 stations the whole dataset fits on one page.
notes: Catalogue for completeness; NCRB UT totals are the practical source.
```

---

## Cross-cutting aggregator

One third-party portal does more work for this project than any state government: OpenCity
(Civic Insights Foundation) runs a CKAN 3 instance that has already mirrored 217 datasets from
`ksp.karnataka.gov.in`, 637 from `data.telangana.gov.in` and 565 from `tracgis.telangana.gov.in`,
plus NCRB, Bengaluru City Police and Greater Chennai Police collections. No API key. It is a mirror,
not a source of record — every published figure must still be traced to the `.gov.in` original — but
it is the correct first hop.

### 38. OpenCity Urban Data Portal (CKAN) — aggregator of South-Indian police releases
Search index returned organisation pages 'Bengaluru City Police (BCP) 6 Datasets' and 'Greater Chennai Police (GCP)', a tag listing /dataset?tags=Crime, and domain-provenance listings showing 217 datasets sourced from ksp.karnataka.gov.in, 637 from data.telangana.gov.in and 565 from tracgis.telangana.gov.in. Also holds the NCRB mirror /dataset/crime-in-india-2023 and a direct TN SCRB PDF at /dataset/c894271b-.../download/tn_cr_statistics_2020.pdf.

**How to obtain:** Standard CKAN 3 API, no key. package_search, package_show, datastore_search.

```
id: state-police-south-opencity-ckan-portal
name: OpenCity Urban Data Portal (CKAN) — aggregator of South-Indian police releases
publisher: Civic Insights Foundation (OpenCity)
domain: state-police-south
tier: 4
urls: {"landing": "https://data.opencity.in/", "data": "https://data.opencity.in/dataset?tags=Crime", "api": "https://data.opencity.in/api/3/action/package_search?q=crime"}
geo_coverage: Bengaluru, Chennai, Karnataka, Tamil Nadu, Telangana, plus national NCRB mirrors
geo_granularity: district
unit_of_record: aggregate-count
time_start: 2019
time_latest: 2025
cadence: irregular
lag: weeks to months behind the source
taxonomy: NCRB-heads / IPC+SLL
formats: ["CSV", "PDF", "JSON", "XML"]
access: open-download
machine_readable: 4
license: mostly 'Other (Public Domain)'; some resources 'No License Provided'
caveats: ["third-party mirror: never the source of record for a published figure", "per-resource licences vary inside a single dataset"]
ingest_difficulty: 1
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: Search index returned organisation pages 'Bengaluru City Police (BCP) 6 Datasets' and 'Greater Chennai Police (GCP)', a tag listing /dataset?tags=Crime, and domain-provenance listings showing 217 datasets sourced from ksp.karnataka.gov.in, 637 from data.telangana.gov.in and 565 from tracgis.telangana.gov.in. Also holds the NCRB mirror /dataset/crime-in-india-2023 and a direct TN SCRB PDF at /dataset/c894271b-.../download/tn_cr_statistics_2020.pdf.
how_to_obtain: Standard CKAN 3 API, no key. package_search, package_show, datastore_search.
notes: Single best machine-readable entry point for the whole region. Phase 2: mirror the CKAN catalogue, then chase upstream .gov.in sources for anything with a licence gap.
```

## Granularity reality check

What we want for a police.uk-style product is incident points with timestamps, refreshed monthly.
What actually exists:

| Level | Where it genuinely exists | Period | Refresh | Honest assessment |
|---|---|---|---|---|
| `point` (incident) | **Nowhere.** No Indian police force publishes geocoded incident rows. | — | — | Independently established across 21 primary sources on 2026-09-10. The core product concept must be re-scoped. |
| `point` (police station) | Karnataka only — OpenCity KML, Karnataka + Bengaluru Urban | base list 2012, contacts 2025 | one-off | The region's only ready-made geometry. Stations created since 2012 (e.g. Electronics City division) are missing. |
| `police-station` (counts) | **Kerala only** — `ps.keralapolice.gov.in/<slug>-ps/crime-statistics`, 564 stations | unverified per station | irregular | The single best thing in this dossier. Period coverage per station is the one big unknown. |
| `police-station` (FIR records) | Kerala THUNA (2016-11→), Karnataka firsearch, AP FIRComplainant, TN eServices, TS CCTNS-TSP | 2016→ (Kerala); others unknown | daily | Record-level but retrieval-gated: only Kerala lists by station+year without a FIR number. Sensitive categories excluded everywhere. |
| `police-district` / commissionerate | Karnataka (monthly), Kerala (monthly), TN (annual), Telangana (annual), AP (unverified) | 2019→ typical | monthly (KA, KL) / annual (TN, TG, AP) | **This is the realistic v1 resolution for four of five states.** Watch the district/commissionerate double-count. |
| `city` | Bengaluru (BCP annual, 2021→), Chennai (GCP, road accidents) | 2021→ | annual | City totals only; no division or zone split. Useful as a benchmark the station estimates must sum to. |
| `state` / UT | All eight, via NCRB and MHA Annual Report | 1953→ | annual, 12–18 month lag | The backbone and the validation benchmark. Useless for the product question. |

**The gap, stated bluntly:** a resident asks about a street; the best data in the best state answers
at the level of a police station covering tens of thousands of people, and the best data in six of the
eight jurisdictions answers at the level of a district covering millions. Any map we ship must
foreground that, or it will defame neighbourhoods it cannot actually resolve.

## Blockers and how to get past them

1. **This sandbox's egress allowlist** — all `.gov.in`, `data.opencity.in`, archive.org and news
   domains return 403 at the proxy. *Fix:* re-run verification from an unrestricted network; prefer an
   Indian IP, since several state police sites are known to geo-fence or aggressively WAF foreign traffic.
   Every finding below carries the evidence I actually saw so this is re-checkable rather than re-doable.
2. **Supreme Court sensitive-category exclusion (07.09.2016)** — sexual offences, POCSO, insurgency and
   terrorism FIRs are never published. *No technical fix exists.* Mitigation: (a) never present a public
   FIR corpus as total crime; (b) backfill these categories from NCRB district tables, which do include
   them, and label the join; (c) state the exclusion in the UI next to every category filter.
3. **No jurisdiction polygons anywhere** — we have station points (Karnataka) and prose jurisdiction
   descriptions (Kerala), never boundaries. *Fix:* Voronoi/Thiessen tessellation clipped to district
   polygons from DataMeet `maps` (CC BY 4.0), explicitly labelled as an approximation; or a manual
   gazetteer build from Kerala's per-station jurisdiction text.
4. **Session-bound and captcha-gated portals** — TN eServices is Apache Wicket with session-scoped
   `wicket/page?N` URLs; KSP firsearch and AP FIR search need the FIR number; Hyderabad City Police is
   behind a login. *Fix:* Playwright with a maintained session for TN; for the rest, prefer RTI for
   station-month aggregate counts over record enumeration — it is cheaper, more complete and far less
   legally exposed.
5. **PDF-only monthly series (Karnataka, Telangana, TN SCRB)** — layouts shift between editions.
   *Fix:* camelot/tabula with per-edition templates and a reconciliation test against the annual
   roll-up; prefer the OpenCity CSV mirror where it exists and fall back to PDF only for missing periods.
6. **Definitional breaks that will silently corrupt a time series** — IPC→BNS from 1 July 2024 (head
   renumbering across every state); AP's 2022 reorganisation from 13 to 26 districts; the 2014
   AP/Telangana bifurcation; NCRB's principal-offence rule (one FIR counts once, under its most serious
   head) which state SCRB totals do *not* apply, so state and NCRB figures for the same year legitimately
   differ. *Fix:* a versioned crime-head crosswalk and a district crosswalk as first-class, reviewed
   artefacts — not a preprocessing afterthought.
7. **Licence ambiguity** — state police HTML pages are `unstated`; the OpenCity BCP contact dataset is
   `No License Provided`. *Fix:* publish only from GODL-India/CC-BY sources and from aggregate counts
   scraped under a documented fair-dealing position; never redistribute the BCP phone numbers; seek a
   written reuse permission from KSP and Kerala Police SCRB before launch.

## Seed Leads (unconfirmed but probably real)

1. **A crime or FIR dataset on `data.telangana.gov.in` that no search surfaced.** *Next step:* one API
   call, no key — `GET https://data.telangana.gov.in/api/1/search?fulltext=crime` (repeat for `police`,
   `FIR`, `law and order`, `SCRB`). This resolves the brief's biggest open question in a single request.
2. **A JSON/GeoJSON endpoint behind `ksp.karnataka.gov.in/kspmap/en`.** The KSP Android app
   (`com.capulustech.ksppqrs`) gives each station's location and a Google Maps navigation link, so
   coordinates exist server-side. *Next step:* open `/kspmap/en` with devtools and capture XHRs; if
   server-rendered, mitmproxy the app on an emulator.
3. **A KSP dashboard at `ksp.karnataka.gov.in/bsbmd/`.** A third-party scraper's cached pages reference
   `/bsbmd/plugins/{bootstrap,node-waves,animate-css,morrisjs}` — Morris.js is a charting library, so
   this path is an analytics dashboard, not a content page. *Next step:* fetch `/bsbmd/` directly and
   enumerate its data endpoints.
4. **The native `tnpolice.gov.in` URL for the SCRB annual "Crime Statistics, Tamil Nadu".** The 2020
   edition is only confirmed via an OpenCity-hosted copy (`tn_cr_statistics_2020.pdf`). *Next step:*
   walk `tnpolice.gov.in` publications/SCRB pages for the 2021–2024 editions; if absent, RTI the SCRB,
   Chennai for the PDF series.
5. **A stable public download URL for the Telangana Police Annual Report.** Confirmed to exist and be
   released each ~29 December, but only ever seen quoted in press coverage. *Next step:* ask the DGP's
   PRO, Telangana Police HQ; failing that RTI the Telangana SCRB for the last five editions.
6. **`kerala.data.gov.in`** — a Kerala NIC OGD instance exists but was reported "undergoing maintenance"
   in search results and yielded no crime dataset. *Next step:* re-check its department facet for
   Home/Police once it is back up.
7. **Kerala Police daily arrest PDFs, 2014–2016** — concrete legacy URL pattern recovered
   (`/newsite/pdfs/arrested_persons_2014/august/4/arrested_persons_tvmcity.pdf`). *Next step:* Internet
   Archive CDX query on `keralapolice.gov.in/newsite/pdfs/arrested_persons_*` to reconstruct a daily
   district series for historical backfill.
8. **Station master lists with coordinates behind the "nearby police station" features** of the AP
   Suraksha app, the KSP app and the TG-COP app. *Next step:* one RTI per state asking *only* for the
   police-station master table (name, station code, address, lat/lon, jurisdiction) — a low-sensitivity
   request that is hard to refuse under s.4 proactive-disclosure duties, and it solves the geometry
   problem for four states at once.
9. **Puducherry Directorate of Economics and Statistics Statistical Abstract / Annual Report crime
   chapter** (`statistics.py.gov.in/annual-report`). *Next step:* download the latest edition and check
   for a police-returns crime table — likelier to exist than anything on the police site.
10. **`tracgis.telangana.gov.in`** — OpenCity indexes 565 datasets from this Telangana GIS host. Its
    police/administrative layers are unexamined here. *Next step:* enumerate its layer catalogue for a
    police-station or police-jurisdiction layer.

## Phase 2 recommendations

Ranked by (granularity × freshness × coverage) ÷ effort.

1. **Kerala per-station crime statistics** (`state-police-south-kerala-ps-crime-statistics`). The only
   station-level counts in India. First harvest the station slug index (slugs are irregular and contain
   typos — `viyoor-ps`, `maranagttupilly-ps` — so they must never be generated), then ~564 throttled GETs.
   Check robots.txt first. Outcome: a station-level baseline that nothing else in the region can match.
2. **Karnataka via OpenCity CKAN** (`state-police-south-opencity-karnataka-crime` +
   `-opencity-police-station-locations-karnataka`). Keyless API, CSV, 2022–2025, district +
   commissionerate, *and* the matching station point geometry in the same portal. This is the fastest
   path to a working end-to-end map slice and should run in parallel with (1).
3. **Kerala monthly state + district crime tables** (`-kerala-police-crime-tables`,
   `-kerala-district-police-crime-pages`). Well-formed HTML, no auth, monthly cadence — the freshest
   crime series available anywhere in the region and the validation benchmark for (1).
4. **One API call to settle Telangana** (`-telangana-open-data-portal`, seed lead 1). Costs a minute;
   either unlocks a state or lets us stop treating Telangana as a priority.
5. **KSP Monthly Crime Review PDFs** (`-ksp-monthly-crime-review`) for any month the OpenCity mirror
   lacks, plus the December edition as the annual reconciliation check.
6. **Tamil Nadu district CSVs via OpenCity** (`-opencity-tn-crime`) — low effort, shallow reward, but it
   is the only machine-readable TN crime source found.
7. **The three RTI campaigns**, drafted together and filed in one batch: Puducherry, A&N and Lakshadweep
   station-wise monthly FIR counts (small universes, plausibly complete answers), plus the
   station-master-with-coordinates request (seed lead 8) to AP, Telangana, TN and Kerala. File early —
   RTI turnaround is 30 days statutory and realistically longer.
8. **AP crime-statistics endpoint probe** (`-ap-crime-statistics`). Two stateless GETs decide whether AP
   is a tier-1 or tier-3 state for us.
9. **Defer entirely:** TGICCC, Disha/Suraksha, BTP ASTraM, Public Eye, KSP policeseva, Criminal
   Intelligence Gazette. All are either internal, retired, login-walled or PII-laden.

### Build note for the engineer

Model the spine as `(jurisdiction_id, period, crime_head, count, source_id, source_verification)` where
`jurisdiction_id` resolves against a **versioned** police-geography table carrying `police-station →
police-district → commissionerate → state` and validity dates, so the 2022 AP reorganisation and the
2014 bifurcation are data, not exceptions. Keep the crime-head crosswalk (IPC ↔ BNS ↔ NCRB heads ↔
each state's local head names) as a reviewed artefact with its own version number. Never store a count
without its `source_id`, and never render a map tile that cannot name the geographic level it is drawn at.
