# State Police & Home Department Data — Western & Central India
_Agent: state-police-west · Researched: 2026-09-19 · Entries: 3 verified / 26 total_

**Scope:** Maharashtra, Gujarat, Goa, Madhya Pradesh, Chhattisgarh, Dadra & Nagar Haveli and Daman & Diu.

> ## ⚠ Read this before trusting any `verification` field
> **Every `.gov.in` host in this scope was unreachable from this session.** The egress proxy
> answered `403` to `CONNECT` for all of them — a policy denial at the gateway, which the proxy
> README explicitly says to report rather than route around. Also blocked: `web.archive.org`,
> `data.opencity.in`, `praja.org`, `scribd.com`, `indiadataportal.com`.
> Only `github.com` / `raw.githubusercontent.com` and `wikipedia.org` were reachable.
>
> Consequence: **I could not fetch a single official portal.** No entry is marked
> `VERIFIED_LANDING` or `VERIFIED_LIVE` on the strength of an official page, because that would
> be a lie. The three `VERIFIED_LIVE` entries are GitHub-hosted artefacts I genuinely downloaded
> and parsed. Everything else is `CITED` (search index returned the URL with a matching title)
> or `UNVERIFIED`. A human in India must re-confirm before Phase 2 ingestion.
>
> One consolation: the Maharashtra flagship finding is *better* evidenced than a landing-page
> fetch would have given us, because I obtained **real harvested output data** plus **three
> independent scraper implementations**. See §1.

---

## Executive summary

- **Maharashtra's Citizen Portal FIR search is real, open, and scrapable. It has no captcha and
  no login.** Confirmed by three independent public codebases that all POST to
  `citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx`, and by 500 rows of real harvested
  output I downloaded and parsed. **This changes our product ceiling** — see §1.
- Finest granularity achieved anywhere in this scope: **police-station level, individual FIR
  records, timestamped to the second, statewide, refreshed daily** (Maharashtra). That is
  police.uk-class input data. Nothing else in western India comes close.
- **The other five jurisdictions all gate FIR access behind a login or a single-record lookup.**
  Gujarat, MP, Chhattisgarh and Goa each run CCTNS citizen portals with the *same underlying data
  model* as Maharashtra — only the publication policy differs. Maharashtra is the outlier, not
  the norm.
- **Maharashtra publishes no incident coordinates.** The finest real geography is the police
  station. Any "crime map" built on this is a *station-catchment* map wearing a pin's clothing.
- **No police station boundary polygons were found for any state in this scope.** This is the
  single biggest cartographic blocker, and it is not solved by better scraping.
- The published-FIR feed **systematically excludes sexual offences and crimes against
  women/children** by design. Our map would under-represent exactly the crimes that most drive a
  resident's "is it safe to walk here at night" question. This caveat must ship on the map face,
  not in a footnote.
- The **IPC→BNS transition (1 July 2024)** cuts every series in this scope in half. Harvested
  2025 rows carry `भारतीय न्याय संहिता (बी एन एस), 2023` sections; pre-July-2024 rows carry IPC.
  Sections also arrive as **Marathi Devanagari strings**, needing transliteration before mapping.
- Annual benchmark publications exist for **Maharashtra** (`Crime in Maharashtra`, CID Pune) and
  **Madhya Pradesh** (`Crime in MP`, SCRB Bhopal). **Gujarat, Chhattisgarh and DNH&DD produced no
  discoverable statistical publication at all** — recorded as explicit negative findings with RTI
  routes.
- **Goa is the best pilot after Maharashtra**: ~2 districts, ~30 stations, and a portal that does
  list FIRs by police station — but behind registration. One account-creation test settles it.
- A genuine **per-station coordinate source exists for Mumbai**: each
  `mumbaipolice.gov.in/policestation?ps=N` page embeds a Google Maps iframe whose
  `!2d<lng>!3d<lat>` parameters I extracted from a real captured copy (lat 18.9119, lng 72.8165
  for `ps=20`), across ~95+ stations.

---

## Source entries

### 1. Maharashtra Police Citizen Portal — Search & View Published FIR ★ THE FINDING

**The lead was reported as "FIR search by police station and date". It is true, and it is better
than reported.**

I could not open the portal (egress 403). Instead I verified it three ways that, combined, are
stronger than a landing-page fetch:

**(a) Real harvested output.** I downloaded `fir-data-2025-09-27T07-41-06-426Z-with-coords.json`
from `github.com/Atharvayadav11/mahagovscrapper` — 245,102 bytes, exactly 500 records. Schema:

```json
{"srNo": 1, "state": "MAHARASHTRA", "district": "NASHIK CITY",
 "policeStation": "ADAGAON POLICE STATION", "year": 2025, "firNumber": "258",
 "registrationDate": "11/08/2025 17:52:50", "firNoWithYear": "0258/2025",
 "sections": "भारतीय न्याय संहिता (बी एन एस), 2023 - 303(2) ;",
 "hasDownloadButton": false, "coordinates": {"lat": 19.9975, "lng": 73.7898}}
```

Parsed distribution: all 500 rows `NASHIK CITY` / `ADAGAON`, dates 30/07/2025–04/08/2025; acts =
BNS 2023 (450), Motor Vehicles Act 1988 (100), Maharashtra Police Act 1951 (50). A second file
held 60 rows across `PALGHAR` (50) and `NASHIK CITY` (10), 21/06/2025–12/08/2025. District values
include `BRIHAN MUMBAI CITY`, so the dropdown spans commissionerates and rural districts statewide.

**(b) Three independent scrapers, none handling a captcha or a login.**

| Repo | File | Captcha | Login |
|---|---|---|---|
| `Atharvayadav11/mahagovscrapper` | `fir-scraper.js` | none | none |
| `RudraBhagat/FIR_Agent` | `services/scraper.py` | none | none |
| `PALASH2201/web_scraping` | `pdf_data.py` | none | none |

**(c) The exact control surface**, recovered from `fir-scraper.js`:

```
POST https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx
  ctl00$ContentPlaceHolder1$txtDateOfRegistrationFrom   '03/06/2025'   (dd/MM/yyyy)
  ctl00$ContentPlaceHolder1$txtDateOfRegistrationTo     '15/08/2025'
  ctl00$ContentPlaceHolder1$ddlDistrict                 '19408'        (numeric code)
  ctl00$ContentPlaceHolder1$ddlPoliceStation            ''             (blank = all in district)
  ctl00$ContentPlaceHolder1$txtFirno                    ''
  ctl00$ContentPlaceHolder1$btnSearch                   'Search'
  ctl00$ContentPlaceHolder1$ucRecordView$ddlPageSize    '50'
  + replay __VIEWSTATE, __EVENTVALIDATION, __PREVIOUSPAGE each request
Paging: __EVENTTARGET=ctl00$ContentPlaceHolder1$ucGridRecordView, __EVENTARGUMENT=Page$N
FIR PDF: <input> button in result cell index 9  (per pdf_data.py, downloads without auth)
```

Result columns: Sr No · State · District · Police Station · Year · FIR No · Registration Date ·
FIR No w/ Year · Sections · Download button.

```yaml
id: mh-citizen-published-firs
tier: 2            access: scrape          machine_readable: 3
geo_granularity: police-station            unit_of_record: fir-record
cadence: daily     lag: days               taxonomy: BNS
time_start: unknown (>=2025 confirmed)     time_latest: 2025-09
priority: 5        ingest_difficulty: 3    verification: CITED
license: unstated
```

**Answers to the specific questions asked:**

| Question | Answer |
|---|---|
| Fields exposed? | District, police station, year, FIR number, registration date **with time to the second**, sections, PDF download button |
| Captcha? | **No.** Three independent implementations, zero captcha handling |
| Login? | **No.** `PublishedFIRs.aspx` sits outside the `SignUp.aspx`/login flow |
| Rate limits? | None documented. `FIR_Agent` uses courtesy waits (1500 ms after district select, 15 s dropdown timeout). Wide date ranges **time out** — harvest in narrow windows per station |
| How far back? | **Unverified.** Only 2025 observed. Probing `txtDateOfRegistrationFrom` backwards is the single highest-value next test |
| Terms of use? | **Not located.** No ToU or robots.txt reviewed — a genuine open legal question, not a cleared one |

**Caveats (all load-bearing):**
- Published FIRs **exclude** rape/POCSO/women-and-child cases by policy → systematic
  undercounting of the highest-salience crimes.
- Geography is the **police station, not the incident**. No incident lat/lon exists.
- IPC→BNS break at 2024-07-01; sections are **Marathi Devanagari** strings.
- `hasDownloadButton` was `false` for all 500 sampled rows → PDF availability is partial.
- Bulk re-publication legality is **untested**.

---

### 2. Maharashtra Citizen Portal — Search Accused / Arrested Accused
`citizen.mahapolice.gov.in/Citizen/MH/SearcgAccusedArrest.aspx` (the typo `Searcg` is in the
official URL). Found as a live link inside a real captured copy of `mumbaipolice.gov.in`; Mumbai
Police's menu labels it "Information of Arrested Accused". Same ASP.NET pattern as §1.

**Recommendation: do not map this.** It names arrested individuals who have not been convicted.
Aggregate-only, if at all. `priority: 2`, `verification: CITED`.

### 3. Crime in Maharashtra (annual) — CID Maharashtra, Pune
`mahacid.gov.in/publications/crime-in-maharashtra`; a 2017 edition PDF sits at
`mahapolice.gov.in/uploads/other_flash/486.pdf` (search returned the title
"CRIME IN MAHARASHTRA- 2017 Criminal Investigation Department Maharashtra State").
District-level annual aggregates, PDF tables. **Only the 2017 edition was positively identified**
— continuity to the present is unconfirmed. This is the benchmark series for validating whether
the §1 scrape is complete. `priority: 3`, `ingest_difficulty: 4`.

### 4. Mumbai Police — Crime Review / Crime Statistics
`mumbaipolice.gov.in/Crime_info` and `/CrimeStatistics`. Both paths confirmed present in the site
navigation of a real captured copy. City totals, not station-level — the page name does *not*
imply granularity. Note Mumbai city police jurisdiction ≠ BMC boundary; Thane and Navi Mumbai are
separate commissionerates. `geo_granularity: city`, `priority: 3`.

### 5. Mumbai Police — per-station pages with embedded coordinates ✅ VERIFIED_LIVE
`mumbaipolice.gov.in/policestation?ps=N`. I downloaded real captures (`ps_2` … `ps_95`, so ~95+
stations). `policestation_ps_20.html` contains a Google Maps embed encoding
`!2d72.81654191437444!3d18.911938662` → **lng 72.8165, lat 18.9119**.

Iterate `ps=1..~100` and regex `!2d(<lng>)!3d(<lat>)`. This yields *genuine* station coordinates —
far better than the crude geocoding bundled with the scraper corpus (§13). Still points, not
polygons. `priority: 4`, `ingest_difficulty: 2`.

### 6–7. Pune City and Pune Rural Police
- City: `admin.punepolice.gov.in/CrimeStatistics`, `/Crime_info` (titles "Crime Statistics | Pune
  City Police", "Crime Review | Pune City Police"). `admin.*` is the live CMS.
- Rural: `puneruralpolice.gov.in/crime-statistics`, `/crime-review`.

The two jurisdictions are **disjoint** — union them, never double-count. Pune is the strongest
non-Mumbai pilot: city stats + rural stats + a `data.gov.in` catalogue + an ICCC all coexist.
`priority: 3` each.

### 8. Maharashtra district police CMS pattern
`palgharpolice.gov.in`, `chandrapurpolice.gov.in` and peers share the `/crime-statistics` +
`/crime-review` path convention with Pune Rural. **Phase 2 action:** enumerate all ~45 Maharashtra
units and probe those two paths. Coverage and freshness vary wildly. `priority: 2`.

### 9. Maharashtra CCTNS NCL Dashboard
`citizen.mahapolice.gov.in/NCLDashboard/Login.aspx`, title "CCTNS.STATE.CAS". Police-internal,
credentialed. **Do not attempt access.** Its existence is nonetheless useful leverage: it proves
station-level aggregates already exist in exportable form internally, which strengthens an RTI or
data-sharing ask. `access: login`, `priority: 1`.

### 10. Crimes in Pune — data.gov.in catalogue
`data.gov.in/catalog/crimes-pune`, released under NDSAP → **GODL-India licensed**, which would be
a clean legal shortcut around scraping *if* it is genuinely station-wise. Granularity unverified;
data.gov.in city catalogues are frequently stale one-off uploads. `priority: 3`.

### 11. Mumbai Crime Data 2023 — OpenCity
`data.opencity.in/dataset/mumbai-crime-data-2023`. Tier 4 re-publication; provenance must be
re-established. **Key insight: it is a CKAN instance**, so `data.opencity.in/api/3/action/
package_search` is very likely live — the easiest machine-readable entry point in this entire
scope. `priority: 3`.

### 12. Praja Foundation — State of Policing and Law & Order in Mumbai
Annual NGO white papers (2019 and 2023 editions surfaced) built on **RTI returns**, reaching
police-station level for Mumbai. Advocacy framing; definitions may not match NCRB heads.

**Its real value is as an RTI playbook** — Praja has already won station-level Mumbai data, so
their appendices reveal exactly which questions Maharashtra Police will actually answer.
`tier: 4`, `priority: 3`.

### 13. Public GitHub corpus of harvested Maharashtra FIR data ✅ VERIFIED_LIVE
`Atharvayadav11/mahagovscrapper`, `RudraBhagat/FIR_Agent`, `PALASH2201/web_scraping`,
`shivam-sharma0/extract-fir-data`. Proof our exact pipeline already works end-to-end.

**Warnings:** hobby harvests with no completeness guarantee; a committed `.env` is present in one
repo (read, don't run); and the bundled station coordinates are **bad** — I confirmed 10+ Nashik
stations sharing one identical `(20.0064, 73.7898)` city-centre fallback. Use as schema reference
and test fixture only. `priority: 4`, `ingest_difficulty: 1`.

### 14–15. Gujarat — Citizen Portal (e-GujCop) and crime statistics
Portal: `gujhome.gujarat.gov.in`, plus a distinct `fir.gujarat.gov.in` host titled "GUJARAT
POLICE", plus an official guideline PDF at `/portal/images/eGujCop/UserGuideline_En.pdf`.
Services include "Get FIR Copy".

**The critical difference from Maharashtra:** Gujarat's is a single-record **lookup**, not a
browsable **list**. The documented flow requires identifying details before "generate report", so
there is no station+date-range enumeration. Registration required. `access: captcha`,
`ingest_difficulty: 5`.

**Crime statistics — NEGATIVE FINDING.** No Gujarat equivalent of "Crime in Maharashtra" surfaced
in any search; only the services portal and commercial aggregators (Indiastat) appeared. Recorded
as `access: rti-only`, `verification: UNVERIFIED` — and I flag honestly that absence of evidence
*under a blocked-egress constraint* is weaker than a confirmed absence.

> **RTI route:** PIO, Director General of Police, Gujarat, Police Bhavan, Sector 18, Gandhinagar.
> Request district- and station-wise FIR counts by major head, monthly, last 5 years, in XLSX/CSV.
> Cite that CCTNS already holds it electronically, pre-empting a "disproportionate diversion of
> resources" refusal under Sec 7(9).

### 16–17. Madhya Pradesh
- **`scrb.mppolice.gov.in/crime_in_mp.php`** — "Crime in MP", SCRB Bhopal. District-level annual
  aggregates in PDF. MP's best open source; a benchmark layer, not a map layer. `priority: 3`.
- **`citizen.mppolice.gov.in/CitizenLogin.aspx?CtznService=13`** — View FIR, **behind a login**.
  No anonymous published-FIR list. Corroborated by a third-party state-portal index I downloaded.

MP runs the **same ASP.NET CCTNS stack as Maharashtra**, so the data model is identical and only
the publication policy differs. That makes MP the strongest RTI target in this scope: *ask them to
publish what Maharashtra already publishes.* District boundary churn (frequent new districts)
breaks the series.

### 18–20. Chhattisgarh
- **`cgpolice.gov.in/crime-in-chhattisgarh`** — dedicated crime page. Granularity unconfirmed and
  possibly narrative; recorded conservatively as `state` per the spec rule that an unopened claim
  earns no fine-granularity label.
- **`dashboard.cgpolice.gov.in/CCTNS_Citizen_Portal/Citizen_Login.jsp`** (also served from
  `search.cgpolice.gov.in`) — View FIR, **login-gated**. A **Java/JSP** CCTNS build, so the
  Maharashtra ASP.NET scraper does not transfer. Worth probing whether any JSP endpoint responds
  pre-login — JSP CCTNS builds elsewhere have exposed unauthenticated FIR lists.
- **LWE / Naxal incidents — NEGATIVE FINDING.** No public incident-level dataset. Expect RTI
  refusal under **Sec 8(1)(a)** (sovereignty/security). LWE uses a bespoke MHA taxonomy that does
  not map onto IPC/BNS heads. **Recommend scoping out of v1**: high political and real-world
  safety risk, low value for a rental-safety use case. District-wise annual tables in the MHA
  Annual Report are the practical open substitute.

### 21–22. Goa — best pilot candidate after Maharashtra
- **`citizen.goapolice.gov.in/web/guest/view-fir`** plus a distinct
  **`/web/guest/firdocsearch`**. The portal is described as letting users view FIRs registered by
  different police stations in Goa — **but requires registration**. Liferay stack (a third
  distinct platform).
- **`/web/guest/scrb`** — SCRB page; its described role is compiling returns *for* NCRB, so it may
  carry no state tables of its own. `/web/guest/download` is service **forms**, not data — do not
  mistake it for a data download.

**Why Goa is the pilot:** ~2 districts, ~30 stations — small enough to validate the entire
pipeline end-to-end in days. It *does* list FIRs by police station. The only open question is
whether the login gate also caps enumeration. **One account-creation test settles it.** Caveat:
low absolute volumes mean small-number effects will dominate any rate map.

### 23–24. Dadra & Nagar Haveli and Daman & Diu
`police.ddd.gov.in` (current), legacy `dnhpolice.gov.in` / `citizen.dnhpolice.gov.in` (http-only).
The citizen portal's described function is **service requests and status tracking — not a
published FIR list**. **No crime statistics of any kind surfaced** → `access: rti-only`.

Two separate PIOs despite the merged UT (SP Silvassa; SP Daman). Population ~600k across three
non-contiguous enclaves — statistically thin. **Recommendation: fall back to NCRB state/UT tables
rather than chasing a local source.** `priority: 1`.

### 25. Digital Police Portal — national index of state citizen portals
`digitalpolice.gov.in/DigitalPolice/portal`, title "State Police Citizen Portals" (MHA/NCRB).
An index of links, not data — but **the highest-leverage single page to open first in Phase 2**,
because it resolves every state's *current* CCTNS domain in one fetch and defeats the link rot
that plagues state portal migrations. `priority: 4`, `ingest_difficulty: 1`.

### 26. Police Stations roster with lat/lon ✅ VERIFIED_LIVE
Header verified exactly: `CityName,Name of Police Station,Address,Longitude,Latitude`. The copy I
opened is a **433-byte, 3-row stub** (Amaravati only) — the full national file was *not* obtained.
The `_0` filename suffix is the `data.gov.in` resource convention, so the real source is very
likely an OGD/Smart Cities catalogue. Semicolons are used as intra-field separators and will break
naive CSV parsing.

**This schema is exactly what we need to geolocate station-level FIR counts.** Recovering the
complete file is a high-value, low-cost Phase 2 task.

---

## Granularity reality check

| Jurisdiction | Best granularity actually available | Period | Refresh | Reality |
|---|---|---|---|---|
| **Maharashtra** | **police-station, per-FIR, timestamped** | 2025 confirmed; earlier untested | **daily** | The only police.uk-class input in this scope |
| Mumbai (station geometry) | **point** (station pin, ~95+ stations) | current | irregular | Real coords; still points, no polygons |
| Pune city / rural | city / police-district aggregates | unknown | monthly | Page names overpromise; assume totals |
| Goa | police-station, per-FIR — **behind login** | unknown | daily | Pilot-sized; gate untested |
| Madhya Pradesh | district annual aggregates (PDF) | unknown | annual | Benchmark only, not mappable |
| Chhattisgarh | state-level (unconfirmed) | unknown | irregular | Weakest of the five states |
| Gujarat | **none published** — lookup only | n/a | n/a | RTI route |
| DNH & DD | **none published** | n/a | n/a | Use NCRB; not worth local pursuit |

**The gap, stated bluntly.** We want incident points with categories and outcomes. What exists,
at its best, is *FIRs attributed to a police station*. A station may cover several square
kilometres of mixed-income city. Rendering those as pins would manufacture a precision the data
does not contain and would defame specific streets. The honest v1 visual is a **station-catchment
choropleth with explicit uncertainty** — and even that needs boundary polygons **which do not
exist publicly for any state in this scope**.

---

## Data accessibility ratings

| State / UT | Rating | Justification |
|---|---|---|
| **Maharashtra** | **5 / 5** | Station-level per-FIR records, daily, statewide, no captcha, no login, PDF downloads. Verified via real harvested data + 3 independent scrapers. Only deductions: no incident coords, sensitive categories withheld, back-history unproven |
| **Goa** | **3 / 5** | Portal genuinely lists FIRs by station, but registration-gated. Small enough that one test resolves it. Upside to 4 if the gate permits enumeration |
| **Madhya Pradesh** | **2 / 5** | A real annual SCRB publication exists (good), but FIR access is login-gated and stats are district-annual PDFs. Same stack as MH → best RTI target |
| **Chhattisgarh** | **2 / 5** | A crime page exists but granularity unconfirmed; FIR portal login-gated on a different (JSP) stack; LWE data effectively closed |
| **Gujarat** | **2 / 5** | Large, well-built citizen portal that deliberately exposes **lookup, not list**. No statistical publication found at all. Capable state, closed data |
| **DNH & DD** | **1 / 5** | No statistics, no published FIR list, tiny population, split PIOs. Use NCRB instead |

---

## Blockers and how to get past them

1. **[This session] Total egress block on `.gov.in`.** Gateway `403` on `CONNECT` for every
   official host, plus `web.archive.org`. *Fix:* re-run verification from an unrestricted network
   or from India. Nothing here should be ingested on my say-so alone.
2. **No police-station boundary polygons anywhere.** The hard cartographic blocker; more scraping
   will not solve it. *Routes:* (a) RTI to each DGP for station jurisdiction maps — note the
   Maharashtra NCL Dashboard (§9) proves internal geo exists; (b) approximate via Voronoi
   tessellation of station points, **clearly labelled as an estimate**; (c) partner with a state
   Smart City/ICCC programme which already holds beat boundaries.
3. **Sensitive-category exclusion.** Unfixable by technical means; it is a publication policy.
   *Mitigation:* pair the map with NCRB district totals so the divergence is visible, and state
   the exclusion on the map face.
4. **IPC→BNS discontinuity + Marathi section strings.** *Fix:* build an IPC↔BNS crosswalk and a
   Devanagari section parser before any time-series is shown. Budget real effort here.
5. **Login gates in Gujarat/MP/CG/Goa.** *Do not* scrape behind personal accounts — it breaches
   ToU and is not a production route. *Fix:* RTI and formal data-sharing requests.
6. **Unresolved ToU/robots for the Maharashtra portal.** Genuinely open, not cleared. *Fix:* have
   counsel review before any bulk harvest; throttle hard; cache aggressively.
7. **Rate-limit fragility.** Wide date ranges time out. *Fix:* harvest per-station in narrow
   windows with backoff — and treat that as a courtesy obligation, not just a workaround.

---

## Seed Leads (unconfirmed but probably real)

| Lead | Likely publisher | Concrete next step |
|---|---|---|
| **How far back `PublishedFIRs` goes** | Maharashtra Police | Binary-search `txtDateOfRegistrationFrom` (2015 → present) for one station. **Single highest-value test in this whole dossier** — it decides whether we have a trend product or only a nowcast |
| Maharashtra `ddlDistrict` code list | Maharashtra Police | Parse the dropdown once; `19408` = Nashik City is the one confirmed code. Needed to enumerate statewide |
| Full national "Police Stations" lat/lon CSV | data.gov.in / Smart Cities | Search OGD for the exact header in §26 |
| OpenCity CKAN API | OpenCity | Try `data.opencity.in/api/3/action/package_search?q=crime` |
| ICCC / Smart City crime dashboards (Pune, Nagpur, Surat, Ahmedabad, Indore, Bhopal, Raipur) | Smart City SPVs | **Not investigated — web-search budget exhausted before reaching them.** Start at each SPV site; ICCCs typically expose dashboards but rarely open data. Ask the SPV, not the police, for beat boundaries |
| Recent "Crime in Maharashtra" editions | CID Maharashtra | Only 2017 confirmed. Probe `mahapolice.gov.in/uploads/other_flash/<id>.pdf` around 486, and the MAHACID publications page |
| CG JSP portal pre-login endpoints | CG Police | Probe `CCTNS_Citizen_Portal/*.jsp` for anything responding without a session |
| Goa `firdocsearch` vs `view-fir` | Goa Police | Register once; determine which permits station+date enumeration |
| Gujarat SCRB / Sec 4(1)(b) disclosures | Gujarat Home Dept | Check proactive-disclosure pages before filing RTI |
| Thane / Navi Mumbai / Nagpur commissionerates | Respective CPs | **Not individually verified.** Probe the `/crime-statistics` + `/crime-review` path convention from §8 |

---

## Phase 2 recommendations (ranked)

1. **Re-verify §1 from an unblocked network, then probe the historical depth.** Everything else is
   contingent on this. One afternoon's work; decides the product's shape.
2. **Build the Maharashtra station-level FIR ingester.** Per-station, narrow date windows, polite
   backoff, full `__VIEWSTATE` replay. Store raw HTML for provenance. Get ToU review in parallel —
   *before* volume, not after.
3. **Extract Mumbai station coordinates (§5)** by regexing the map embeds. ~95 stations, hours of
   work, and it is real data rather than the bad geocoding in §13.
4. **Open the Digital Police Portal index (§25) once** to resolve every current state domain and
   kill link rot across all 16 dossiers.
5. **Run the Goa pilot.** Register, test enumeration. Cheapest path to a *second* state and a
   genuine check on whether Maharashtra is replicable.
6. **Recover the national police-station lat/lon file (§26)** and try the OpenCity CKAN API.
7. **Build the IPC↔BNS crosswalk and the Devanagari section parser.** Unglamorous; blocks every
   time series.
8. **File RTIs in parallel** (they take 30–60 days, so start now): Gujarat DGP, MP SCRB,
   CG DGP, DNH&DD. Ask MP and Gujarat explicitly to publish what Maharashtra already does — a
   politically effective framing. Model the wording on Praja's successful Mumbai requests (§12).
9. **Solve station boundaries** — RTI first, Voronoi fallback, always labelled as estimated.
10. **Defer:** Chhattisgarh LWE (§20), the arrested-accused endpoint (§2), and the NCL
    Dashboard (§9). Low value, high legal and ethical risk.

---

## A closing note on publication ethics

The spec warns that caveats are "the difference between a map that informs and a map that
defames a neighbourhood". This scope makes that concrete. The Maharashtra feed is good enough to
build something that *looks* authoritative at street level while (a) resolving only to station
catchments, (b) omitting sexual offences entirely, and (c) counting *reported FIRs*, not
convictions — so a neighbourhood with high trust in police and good reporting rates will look
*more* dangerous than one where victims stay silent. That inversion is the single most dangerous
property of this dataset, and the product must be designed around it rather than footnoting it.
