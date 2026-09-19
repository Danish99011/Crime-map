# State Police & Home Department Data — North India
_Agent: state-police-north · Researched: 2026-09-19 · Entries: 0 verified / 31 total_

**Scope:** Jammu & Kashmir, Ladakh, Himachal Pradesh, Punjab, Chandigarh, Haryana, Delhi (NCT),
Rajasthan, Uttar Pradesh, Uttarakhand.

> ## ⚠️ READ THIS FIRST — verification ceiling of this dossier
>
> **Zero entries in this dossier are `VERIFIED_LIVE` or `VERIFIED_LANDING`.** The research
> session's egress proxy enforces a tight domain allowlist. Every `.gov.in`, `.nic.in`,
> `.jk.gov.in` and `.uk.gov.in` host returned `EGRESS_BLOCKED`, as did every non-government
> fallback that could have substituted (`web.archive.org`, `arcgis.com`, `justicehub.in`,
> `data.opencity.in`, `ppsaanjh.in`, `complainthub.org`, `play.google.com`, `thehindu.com`,
> `humanrightsinitiative.org`, `crime-in-india.github.io`). Only `wikipedia.org` and
> `github.com` resolved. Per `/root/.ccr/README.md`, a proxy policy denial must be reported,
> not routed around — so I did **not** use the `translate.goog` mirrors that appeared in
> search results, although those are a legitimate option for a human operator.
>
> **Consequence:** the best honest grade available here is `CITED` — the URL and its page
> title were returned by a live search index on 2026-09-19, and the title corroborates the
> claim, but I did not open the page. Treat every URL below as *strongly indicated, unopened*.
> **A Phase-2 operator's first job is a link-check sweep of the JSONL before any ingestion
> work.** Expect ~10-20% rot: several of these portals have demonstrably moved already
> (Rajasthan's live reports sit under an `/old/` path; Chandigarh runs two parallel citizen
> portals on different stacks).

## Executive summary

- **8 of 10 states/UTs have *some* published crime data; 2 (Ladakh, J&K) have none I could
  find at any level** beyond what NCRB aggregates centrally. Those two get explicit
  `access: rti-only` entries with their RTI routes, as required.
- **The finest granularity in the region is FIR-record level, and it comes from citizen
  service portals, not from statistics publications.** Chandigarh's *View Published FIR*
  endpoint is the standout: it advertises search by **police station + FIR number + date
  range**, which is police-station-level incident data wearing a citizen-service hat.
  Himachal, Rajasthan, Punjab, Uttarakhand, UP and J&K all run comparable CCTNS-derived
  FIR-view features, with varying gates.
- **The statistics publications are all coarser than the portals.** Where a state publishes
  a report, it lands at `district` or `police-district` granularity, annually or monthly,
  as PDF. Nothing in this region publishes a machine-readable station-level count series.
  This is the central structural gap for the map.
- **Three genuinely useful statistics series exist in this region:**
  Himachal's SCRB **Crime Review** (annual, downloadable PDFs off the citizen portal),
  Rajasthan's **Monthly Crime Report** (monthly — the best cadence in the region),
  and UP's **Crime in UP** (annual, district-wise, SCRB).
  Haryana's SCRB statistical wing claims monthly crime statistics. Delhi has a dedicated
  `/statistics` page plus a press archive.
- **Rajasthan is the region's quiet standout for a different reason:** its Home Department
  portal appears to mint a **per-district crime statistics page** on a predictable path
  (`home.rajasthan.gov.in/content/homeportal/en/<district>police/crimestatistics.html` —
  observed for Dholpur and Baran). If that pattern holds across all 57 police districts it
  is the single most ingestible district-level series in North India.
- **Police-station rosters — our geospatial backbone — exist but are HTML/PDF telephone
  directories, never geodata.** Delhi (`/telephonedirectory`), Himachal
  (`viewpolicestation.htm`, `openTeleDir.htm`) and Ladakh (`formation.html`) each expose one.
  **No source in this region ships lat/lon.** BPR&D has a project report literally titled
  *Geo-Coding of Police Stations* — proof the coordinates exist inside government and are
  not published. Geocoding is on us.
- **No open API was found anywhere in the region.** No state police site in scope advertises
  one. The realistic API surface is undocumented JSON behind the CCTNS citizen portals
  (ASP.NET `.aspx`/`.htm` endpoints) and behind Smart City ICCC dashboards — all of which
  need a browser session to discover, which this session could not open.
- **Dashboards: nothing public and crime-specific.** Smart City ICCCs exist for Jaipur and
  Lucknow and are CCTNS-linked, but the public `iccc.smartcities.gov.in` pages are
  programme-monitoring pages about ICCCs, not live crime feeds. Operational ICCC dashboards
  are internal. Do not plan around them.
- **Biggest blocker for the product (not for this session):** the FIR portals are built for
  *single-record retrieval by a person who already knows the FIR number*, and are wrapped in
  captcha/OTP/login plus terms of use. They contain station-level data but are architecturally
  hostile to systematic collection. Turning them into a map is a legal question before it is
  an engineering one.
- **A trap worth recording:** searching "Punjab Police crime statistics" surfaces
  `punjabpolice.gov.pk/crimestatistics` — **Pakistan's** Punjab Police, which (unlike India's)
  publishes a clean crime statistics section. Do not let this into the pipeline. India's is
  `punjabpolice.gov.in`.

## Source entries

### 1. Delhi Police — Crime Statistics page
```
id: state-police-north-delhi-police-statistics
publisher: Delhi Police (MHA)
tier: 2 | geo_granularity: police-district | cadence: annual | access: scrape
urls.landing: https://delhipolice.gov.in/statistics
verification: CITED | checked_on: 2026-09-19
```
Search index returned this URL under the exact page title **"Crime Statistics"** on the
official Delhi Police domain. Delhi Police is organised into **15 police districts and 178
territorial police stations** (Wikipedia, fetched 2026-09-19), so district-level breakdowns
here are `police-district`, not revenue-district. Delhi Police's annual crime figures are
released each January at a press conference — press reporting on 2026-01-21 carried
2023/2024/2025 comparatives (murder 506→504→491; rape 2,141→2,076→1,901; snatching
7,886→6,493→5,406), confirming the series is current and three-year-comparative. Whether
`/statistics` hosts machine-readable tables or only PDFs is **unknown — page not opened**.

### 2. Delhi Police — Press Archive
```
id: state-police-north-delhi-police-press-archive
tier: 2 | geo_granularity: police-district | cadence: irregular | access: scrape
urls.landing: https://delhipolice.gov.in/pressarchive
verification: CITED | checked_on: 2026-09-19
```
Press notes are how Delhi Police actually releases crime summaries between annual reviews.
Narrative documents, not tables — value is as a *nowcast* layer and for incident detail the
statistics page aggregates away.

### 3. Delhi Police — Telephone Directory (police station roster)
```
id: state-police-north-delhi-police-telephone-directory
tier: 2 | geo_granularity: police-station | unit_of_record: boundary-polygon→n/a | access: scrape
urls.landing: https://delhipolice.gov.in/telephonedirectory
verification: CITED | checked_on: 2026-09-19
```
**Geospatial backbone candidate for Delhi.** Expect HTML tables of station name, address,
phone, by district. **No lat/lon.** District Magistrate sites carry parallel per-district
police directories (`dmnortheast.delhi.gov.in/police-directory-north-east/`,
`dmsouthwest.delhi.gov.in/police-directory/`) — useful for cross-validation.

### 4. Praja Foundation — *State of Policing and Law & Order in Delhi* (White Paper)
```
id: state-police-north-delhi-praja-white-paper
publisher: Praja Foundation | tier: 4 | geo_granularity: police-district
cadence: annual | access: open-download | verification: CITED
urls.data: https://praja.org/praja_docs/praja_downloads/Report%20on%20State%20of%20Policing%20and%20Law%20and%20Order%20in%20Delhi,%202022_Final.pdf
```
**The most ingestible Delhi source, and it is an NGO's.** Praja RTIs Delhi Police and
republishes district-wise tables as clean PDFs. The 2022 edition covers **2012–2021**; the
2018 edition covers FY2014-15→FY2017-18; a 2021 edition is mirrored on Justice Hub; the
2015 edition sits on CHRI's site. **Why this matters: Praja has already done the RTI work
that hard rule 4 asks us to plan.** Its methodology section is a free map of which Delhi
Police tables are RTI-obtainable. Caveat: NGO re-keying introduces transcription risk;
validate against NCRB.

### 5. Rajasthan Police — Monthly Crime Report
```
id: state-police-north-rajasthan-monthly-crime-report
tier: 2 | geo_granularity: police-district | cadence: monthly | access: scrape
urls.data: https://police.rajasthan.gov.in/old/MonthlyReport.aspx
verification: CITED | checked_on: 2026-09-19
```
**Best cadence in the region.** Indexed under the title "Monthly Crime Report" / "मासिक अपराध
रिपोर्ट". Described as covering the monthly crime scenario with statistics per **Police
District**; Rajasthan registers crime in **18 categories** (its own taxonomy, not NCRB heads —
a mapping table will be needed). Rajasthan has **57 police districts, 261 circles, 1,014
police stations, 1,283 outposts** (Wikipedia, fetched 2026-09-19). **Fragility warning:** the
live URL sits under `/old/`, meaning the current site already superseded this stack. Capture
the archive before it disappears, and find where it moved.

### 6. Rajasthan Home Department — per-district Crime Statistics pages
```
id: state-police-north-rajasthan-district-crime-statistics
tier: 2 | geo_granularity: district | cadence: irregular | access: scrape
urls.data: https://home.rajasthan.gov.in/content/homeportal/en/dholpurpolice/crimestatistics.html
verification: CITED | checked_on: 2026-09-19
```
**Highest-value structural find in this dossier.** Two distinct districts were observed at the
same path shape — Dholpur and Baran — implying a **templated per-district page across the
Home Department portal**: `…/en/<district>police/crimestatistics.html`. If it generalises to
all 57 police districts, this is a single scraper yielding statewide district-level crime
tables in HTML (not PDF). **Verify the pattern against 3-4 more districts before building.**

### 7. Rajasthan Police — FIR search / RajCop Citizen
```
id: state-police-north-rajasthan-fir-search
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
cadence: daily | access: captcha | verification: CITED
urls.landing: https://police.rajasthan.gov.in/old/Investigation_Home.aspx
```
Rajasthan's FIR search is repeatedly described as unusually accessible — search **and
download** FIRs, with statutory exclusions (sexual-offence victim identity cases are
withheld). Available via web and the **RajCop Citizen** Android app
(`com.datainfosys.rajasthanpolice.publicapp`). `fir-record` granularity. Legally sensitive;
see Blockers.

### 8. Himachal Pradesh SCRB — Crime Review (annual)
```
id: state-police-north-hp-crime-review
publisher: HP State Crime Records Bureau, CID | tier: 2
geo_granularity: district | cadence: annual | access: open-download | machine_readable: 1
urls.data: https://citizenportal.hppolice.gov.in/citizen/downloadancrfile.htm?id=12&stov=62HR-8K88-11NX-88J0-78GZ-MG8P-0BWF-0FPC
verification: CITED | checked_on: 2026-09-19
```
**The clearest "state publishes a real annual crime statistics volume" finding in the region.**
Indexed under the literal title **"CRIME REVIEW-2017 HIMACHAL PRADESH STATE CRIME RECORDS
BUREAU"**; a second document at `id=1` carries the title "STATE CRIME RECORDS BUREAU CRIMINAL
INVESTIGATION DEPARTMENT HIMACHAL PRADESH". Corroborating figure from the 2017 edition:
**17,804 cognizable cases (13,015 IPC + 4,789 SLL)**. **Ingestion note:** the download
endpoint takes an incrementing `id` **plus an opaque `stov` token**, so URLs are *not*
enumerable by `id` alone — you must scrape the listing page to harvest `(id, stov)` pairs.
Only two `id`s are exposed in the index; the back-catalogue depth is unknown.

### 9. Himachal Pradesh — Police Station search (roster)
```
id: state-police-north-hp-police-station-search
tier: 2 | geo_granularity: police-station | access: scrape | verification: CITED
urls.data: https://www.citizenportal.hppolice.gov.in/citizen/viewpolicestation.htm
```
Indexed as **"Search Himachal Pradesh Police Station"** — a dedicated station-directory
search, un-gated (no `login.htm` in path). Companion telephone directory at
`https://citizenportal.hppolice.gov.in/citizen/openTeleDir.htm`. **Best-structured station
roster found in the region.** Format unknown; **no indication of lat/lon**.

### 10. Himachal Pradesh — Citizen Portal (FIR view/download, services)
```
id: state-police-north-hp-citizen-portal
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
cadence: daily | lag: 24 hours | access: login | verification: CITED
urls.landing: https://citizenportal.hppolice.gov.in/citizen/login.htm
```
**The most explicit freshness commitment found anywhere in this research:** FIRs registered
after **01/01/2016** are stated to be uploaded **within 24 hours**, viewable/downloadable via
web and the HP Police app (`ncrb.nic.in.HPPolice`). Combined with entry 9's station directory,
Himachal is the region's best candidate for a station-level pilot. Also offers e-FIR, lost
article, character certificate, e-challan, and a "Citizen's Tip" form
(`citizentipbeforelogin.htm`).

### 11. Haryana SCRB — Statistical Wing / Crime Record Office
```
id: state-police-north-haryana-scrb-statwing
publisher: State Crime Records Bureau, Haryana | tier: 2
geo_granularity: district | cadence: monthly | access: scrape | verification: CITED
urls.landing: https://scrb.haryanapolice.gov.in/statwing
```
Indexed as **"Statistical Wing (Crime Record Office) - SCRB HARYANA"**. Stated remit includes
**monthly crime statistics**, Crime in India compilation, and accidental deaths & suicides.
SCRB Haryana established 01-04-1987, located Police Complex, Moginand, Panchkula.
Corroborating figure: **2,24,216 FIRs registered in Haryana in 2023** (4th nationally).
Whether the monthly statistics are *published* on this page or merely *compiled* here is
**unresolved** — this is the single most valuable page in the dossier to open first.

### 12. Haryana Police — Citizen Services
```
id: state-police-north-haryana-citizen-services
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
access: login | verification: CITED
urls.landing: https://www.haryanapolice.gov.in/Citizen_services
```
Online FIR registration, lost article/property report, complaint registration, character
certificate. Haryana routes much of this through the unified **SARAL Haryana** platform and
**Harsamay**; a parallel Home Department listing exists at
`https://homeharyana.gov.in/Police%20E-Services`. Fragmentation across three portals is the
Haryana-specific ingestion risk.

### 13. Punjab Police — SAANJH citizen services
```
id: state-police-north-punjab-saanjh
publisher: Punjab Police (Punjab) | tier: 2
geo_granularity: police-station | unit_of_record: fir-record | access: login
verification: CITED | checked_on: 2026-09-19
urls.landing: https://ppsaanjh.in/
urls.docs: https://ppsaanjh.in/help-fir.php
```
Note the portal lives on **`ppsaanjh.in`, a non-`.gov.in` domain** — with a legacy host still
indexed at `http://citizen.ppsaanjh.in:7070/PPSANJH/Forms/public_download_links.jsp`
(**port 7070, plain HTTP — not reachable through a standard HTTPS proxy; flag for Phase 2
networking**). Critically, Punjab's FIR copy is an **application form**, not a search: the
published form (`punjab.gov.in/wp-content/uploads/2020/10/Copy-Of-F.I.R.pdf`) requires the
applicant to already supply FIR No., FIR year, PS, district and accused name. **That is a
retrieval service, not a dataset** — materially weaker than Chandigarh's or Rajasthan's.
Punjab Police e-governance overview: `https://www.punjabpolice.gov.in/eGovernance.aspx`.

### 14. Chandigarh Police — View Published FIR ★
```
id: state-police-north-chandigarh-view-published-fir
publisher: Chandigarh Police (UT Administration) | tier: 2
geo_granularity: police-station | unit_of_record: fir-record | cadence: daily
access: scrape | machine_readable: 2 | verification: CITED | checked_on: 2026-09-19
urls.data: https://portal.chandigarhpolice.gov.in/public/CitizenPortal/ViewPublishFIR/ViewPublishFIR
```
**The finest-granularity source in this entire dossier, and the best Phase-2 pilot target.**
Indexed under the exact title **"View Published FIR"**, on a path containing **`/public/`** —
strongly implying no login. Described as accepting **FIR number, police station, and a
registration date range**. Search by *police station + date range* with no FIR number is
precisely the query shape that converts a citizen-service portal into a station-level
incident feed.
Chandigarh is a **single small UT with roughly a dozen police stations**, which makes it the
ideal proving ground: small enough to enumerate ethically and completely, structurally
identical (CCTNS) to the large states. **Two portals coexist** —
`portal.chandigarhpolice.gov.in` (modern MVC stack) and the older
`citizenportal.chandigarhpolice.gov.in/…/ViewPublishFIR.aspx`, whose indexed page title is
literally *"Government of India, Ministry of Home Affairs, National Crime Records Bureau"* —
confirming this is **stock NCRB CCTNS citizen-portal software**. **That is the leverage: solve
the CCTNS FIR-view scraper once, and it plausibly ports to every state running the same
build.** Chandigarh publishes **no crime statistics** — see entry 27.

### 15. UP Police SCRB — *Crime in UP* (annual)
```
id: state-police-north-up-crime-in-up
publisher: State Crime Records Bureau, UP Police | tier: 2
geo_granularity: district | cadence: annual | formats: ["PDF"] | machine_readable: 1
access: open-download | verification: CITED | checked_on: 2026-09-19
urls.data: https://uppolice.gov.in/site/writereaddata/siteContent/201803081336125597CrimeinUP2016.pdf
urls.landing: https://uppolice.gov.in/article/en/state-crime-record-bureau-(scrb)
```
**A concrete, directly-linked PDF artifact** — the strongest single piece of evidence in this
dossier that a state in scope publishes a real annual statistical volume. Filename encodes a
2018-03-08 upload of the **2016** edition, i.e. a **~14-month publication lag**. Described as
district-wise cognizable cases under IPC and special laws across all zones, ranges and
districts. UP's SCRB dates to 1906. Contact: `spscrb@up.nic.in`, `scrbup@nic.in`.
**Unknown and important: whether editions after 2016 were published.** A CAG audit chapter
(*Incidence of Crime and Police Deployment*, Report No.3 of 2017) independently audits these
figures and is a useful accuracy cross-check.

### 16. UP Police — Citizen Services / e-FIR / UPCOP
```
id: state-police-north-up-citizen-services
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
access: login | verification: CITED
urls.landing: https://uppolice.gov.in/article/en/citizen-services?cd=NAA1ADAAMQA%3D
```
e-FIR, FIR status, police verification, character certificate, tenant verification, complaint
registration, traffic challan, district police information. e-FIR hands off to the CCTNS site
after authorisation (SMS/email confirmation) — i.e. **login-gated, not a public search**,
unlike Chandigarh. Mobile app **UPCOP** (`uttarpradesh.citizen.app`). UP is the largest
jurisdiction in scope by population; also `uppolice.gov.in/article/en/crime` and
`/article/en/other-citizen-services`.

### 17. Uttarakhand Police — Citizen Portal & e-FIR
```
id: state-police-north-uttarakhand-citizen-portal
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
access: login | verification: CITED
urls.landing: https://policecitizenportal.uk.gov.in/Citizen/index.aspx
urls.data: https://policecitizenportal.uk.gov.in/efir/Login.aspx
```
Services: **View FIR**, tenant/PG verification, cyber crime complaint, character certificate,
protest/strike request, e-FIR (for unknown-accused / non-serious reports). **View FIR requires
registration + login** — a one-time registration, but a hard gate for automated access. Main
site `https://uttarakhandpolice.uk.gov.in/`. App: `com.svinfotech.oneapp`, which surfaces
nearest-police-station numbers (a possible station roster route).

### 18. J&K Police — eServices Citizen Portal
```
id: state-police-north-jk-police-eservices
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
access: login | verification: CITED
urls.landing: https://jkpoliceeservices.gov.in/
urls.data: https://www.jkpoliceeservices.gov.in/login.aspx
```
Indexed as **"Citizen Portal JK | JK Police eServices, eFIR, Online Complaint and
Verification"**. Services: online complaint, **eFIR**, tenant verification, **missing person
and arrested person information**, FIR status tracking. Login-gated (`login.aspx`). Main site
`https://www.jkpolice.gov.in/`; Crime Branch at `/JK-Police-Crime-Branch`. J&K Police: 83,000
employees, ₹9,925.50 crore budget FY2026-27, formed 1873.

### 19. Kashmir Police (Kashmir Zone) — separate portal
```
id: state-police-north-jk-kashmir-police-portal
tier: 2 | geo_granularity: district | access: scrape | verification: CITED
urls.landing: https://kashmirpolice.jk.gov.in/
```
**Follow this one up.** A *zone-specific* portal distinct from `jkpolice.gov.in`, on the
`.jk.gov.in` domain. Search-result summary asserted it "provides access to crime statistics,
traffic data, reports, and an advanced digital crime-tracking system that delivers
block-by-block data." **"Block-by-block" would be the finest granularity claimed by any
source in this dossier** — but this phrasing came from a search-engine summary, not from
the page, and I could not open it to test. **Treat as an unconfirmed lead, not a finding.**
If it is real it materially changes the J&K picture (currently rated 2).

### 20. Ladakh Police — Citizen Portal & formations
```
id: state-police-north-ladakh-police-citizen-portal
tier: 2 | geo_granularity: police-station | unit_of_record: fir-record
access: login | verification: CITED
urls.landing: https://citizenportalpolice.ladakh.gov.in/
urls.data: https://police.ladakh.gov.in/pages/formation.html
```
Services: complaint, **FIR Copy**, character certificate, employee & tenant verification,
event performance, vehicle enquiry, missing person, missing child
(`police.ladakh.gov.in/pages/tenant.html`). **`formation.html` is the station-roster
candidate** — Ladakh is tiny (2 districts: Leh, Kargil), so a complete roster is trivially
small. Control rooms published: PHQ 01982-260887, Leh 01982-258880, Kargil 01985-232275.
UT-level index: `https://ladakh.gov.in/online-citizen-services/`.

### 21. MHA Digital Police Portal — State Police Citizen Portals index ★ SEED
```
id: state-police-north-mha-digital-police-portal
publisher: Ministry of Home Affairs / NCRB | tier: 1
geo_coverage: all-India | access: scrape | verification: CITED
urls.landing: https://digitalpolice.gov.in/DigitalPolice/portal
urls.docs: https://digitalpolice.gov.in/DigitalPolice/AboutUs
```
**The highest-leverage single URL in this dossier.** MHA's master index of **every state's
CCTNS citizen portal**, behind a state-selection interface. Launched 21-08-2017. The brief
warned "many have moved" — **this page is the authoritative answer to that problem for all 36
states/UTs at once, and it is maintained by the body that mandates the portals.** Open this
before hand-checking any individual state. Related: `digitalpolicecitizenservices.gov.in`.

### 22. data.gov.in — Crime Review catalogues (2024, 2025, 2026)
```
id: state-police-north-datagovin-crime-review
publisher: NIC / OGD Platform India | tier: 1 | geo_coverage: all-India
cadence: annual | access: open-download | license: GODL-India | verification: CITED
urls.data: https://www.data.gov.in/catalog/crime-review-year-2024
```
Three consecutive catalogues indexed: `crime-review-year-2024`,
**`crime-reveiw-year-2025`** (note the **typo "reveiw" is in the real slug** — do not
"correct" it in a scraper) and `crime-review-year-2026`. A **2026** catalogue existing as of
2026-09-19 implies **within-year, likely monthly, release** — far better than NCRB's annual
cadence. Publisher/coverage per catalogue is unconfirmed; GODL-India is the platform default,
not verified per-resource. Also: `data.gov.in/sector/police`,
`data.gov.in/keywords/Police%20Station`, and the NCRB-released
`district-wise-crimes-under-various-sections-indian-penal-code-ipc-crimes`.

### 23. AIKosh (IndiaAI) — Crime Review datasets
```
id: state-police-north-aikosh-crime-review
publisher: IndiaAI / MeitY | tier: 3 | access: open-download | verification: CITED
urls.data: https://aikosh.indiaai.gov.in/home/datasets/details/crime_review_for_the_year_2025.html
```
The same Crime Review series **re-published on MeitY's AI dataset platform** (2024 and 2025
editions indexed). Worth checking independently: AI-corpus platforms often host **cleaner,
more machine-readable derivatives** (CSV/JSON) of what OGD ships as PDF. Potentially the
highest `machine_readable` score available for this series.

### 24. BPR&D — *Geo-Coding of Police Stations in India* (project report)
```
id: state-police-north-bprd-geocoding-police-stations
publisher: Bureau of Police Research & Development, MHA | tier: 3
geo_granularity: police-station | unit_of_record: narrative-document
access: open-download | verification: CITED
urls.data: https://bprd.nic.in/uploads/pdf/Geo-Coding%20of%20Police%20Stations.pdf
```
**Documentary proof that police-station coordinates and jurisdiction boundaries exist inside
Indian government, and are not published.** The report describes converting station locations
to lat/lon and **mapping their jurisdiction boundaries** using Google/Bing/ArcGIS/Here APIs,
for crime mapping and forecasting. **Jurisdiction polygons are the missing piece our entire
product depends on** — station points alone cannot produce choropleths. This report names the
office to RTI and likely documents methodology and coverage. **Read this before designing the
geo layer.** Companion: `bprd.nic.in/uploads/pdf/Mobile%20CCTNS.pdf`, which states Mobile
CCTNS captures **exact date, time, lat/lon, crime type, IO name and crime-scene photos** —
i.e. point-level geodata is being captured operationally today.

### 25. ArcGIS Online — "India Police Station Locations"
```
id: state-police-north-arcgis-india-police-stations
publisher: unknown ArcGIS Online contributor | tier: 5
geo_granularity: point | formats: ["GeoJSON","dashboard-only"] | access: blocked
verification: CITED | license: unknown
urls.landing: https://www.arcgis.com/home/item.html?id=35371bda12c74ae39b19e5c45c91cc19
```
A hosted feature layer of **police station locations across India, stated as "per NCRB
reports."** If real and reasonably complete, this is the **fastest path to a national station
point-layer**, and ArcGIS feature layers expose a **queryable REST/GeoJSON endpoint** — the
closest thing to an API found in this research. **But: unknown third-party contributor,
unknown licence, unknown vintage, unknown completeness, and derived-not-authoritative.**
Treat as a bootstrap/cross-check layer, never as ground truth. `arcgis.com` was egress-blocked
so none of this could be confirmed. Counter-evidence from the same search: multiple sources
state no comprehensive geocoded Indian police-station dataset is publicly available and
researchers geocode their own.

### 26. Chandigarh — NO published crime statistics (negative finding)
```
id: state-police-north-chandigarh-crime-stats-rti
tier: 2 | geo_granularity: district | access: rti-only | verification: UNVERIFIED
```
**Explicit negative finding.** Targeted searching for Chandigarh crime statistics surfaced the
FIR portal and general pages but **no statistics page, no annual report, no crime review**.
Chandigarh's crime data appears to reach the public only via NCRB (as a UT row) and via the
FIR portal record-by-record. **RTI route:** PIO, Office of the DGP/SSP Chandigarh, Police
Headquarters, Sector 9, Chandigarh — request monthly station-wise cognizable-crime returns,
which CCTNS generates automatically. ₹10 fee; 30-day statutory reply; first appeal to the
departmental FAA, second appeal to the **Central** Information Commission (Chandigarh is a UT
under MHA, so **CIC, not a state SIC** — a common and costly mistake).

### 27. Punjab — NO published crime statistics (negative finding)
```
id: state-police-north-punjab-crime-stats-rti
tier: 2 | geo_granularity: district | access: rti-only | verification: UNVERIFIED
```
**Explicit negative finding.** No Punjab Police crime statistics page, annual report or crime
review was found. Punjab crime figures reach the public through **parliamentary answers and
press statements** (e.g. cybercrime 378 in 2020 → 697 in 2022, stated by a minister in
Parliament) rather than a published series. SAANJH is a service portal, not a statistics
portal. **RTI route:** PIO, Office of the DGP Punjab, Punjab Police Headquarters, Sector 9,
Chandigarh; appeals to the **Punjab State Information Commission**. Ask specifically for the
**SCRB monthly crime statement, district-wise** — the artefact exists internally because
Punjab must file it to NCRB.

### 28. Uttarakhand — NO published crime statistics (negative finding)
```
id: state-police-north-uttarakhand-crime-stats-rti
tier: 2 | geo_granularity: district | access: rti-only | verification: UNVERIFIED
```
**Explicit negative finding.** Searching Uttarakhand Police crime statistics returned only the
citizen portal and commercial aggregators (Indiastat). No state-published crime report was
located. **RTI route:** PIO, Police Headquarters, Uttarakhand Police, Dehradun; appeals to the
**Uttarakhand Information Commission**. Uttarakhand runs CCTNS (the citizen portal proves it),
so district- and station-wise monthly returns are machine-generated and should be supplied as
CSV if the request explicitly asks for "the data in the electronic form in which it is held"
under **s.7(9) RTI Act**.

### 29. Jammu & Kashmir — NO published crime statistics (negative finding)
```
id: state-police-north-jk-crime-stats-rti
tier: 2 | geo_granularity: district | access: rti-only | verification: UNVERIFIED
```
**Explicit negative finding**, with a caveat: entry 19 (`kashmirpolice.jk.gov.in`) *may*
publish statistics — unconfirmed. Otherwise J&K crime data surfaces only via NCRB and press
(e.g. crimes against women 3,405 in 2020 → 3,937 in 2021; a reported 15.62% one-year rise).
**RTI route is the region's most complicated:** post-reorganisation J&K is a UT with a
legislature; **the J&K RTI Act 2009 was repealed and the central RTI Act 2005 now applies**,
with appeals to the **Central Information Commission**. Expect **s.8(1)(a) (sovereignty and
security) exemptions** to be invoked far more readily here than elsewhere in scope — J&K
policing data is genuinely security-sensitive and partial refusal should be the planning
assumption, not the exception.

### 30. Ladakh — NO published crime statistics (negative finding)
```
id: state-police-north-ladakh-crime-stats-rti
tier: 2 | geo_granularity: district | access: rti-only | verification: UNVERIFIED
```
**Explicit negative finding — the emptiest jurisdiction in scope.** Ladakh Police was
constituted only after the 2019 reorganisation; no statistics publication of any kind was
found. **Mitigating factor: it is also the smallest and simplest** — 2 districts, a handful of
police stations, very low absolute crime volume. A single well-drafted RTI could plausibly
obtain the **complete** station-wise crime record for the UT. **RTI route:** PIO, Police
Headquarters UT Ladakh, Leh (`ladakh.gov.in/department/police-headquarters-ut-ladakh/`);
central RTI Act 2005 applies, appeals to the **CIC**. **Caveat for the map: tiny denominators.
Per-capita crime rates in Ladakh will be statistically meaningless and will produce absurd
choropleth extremes. Suppress or band them.**

### 31. Smart City ICCC programme pages (Jaipur, Lucknow)
```
id: state-police-north-iccc-smartcities
publisher: MoHUA / Smart Cities Mission | tier: 3
geo_granularity: city | access: blocked | machine_readable: 0 | verification: CITED
urls.landing: https://iccc.smartcities.gov.in/icc/city-details/c210316aa28429797908af0d5b50cad7
```
**Recorded mainly to close the question off.** ICCCs in Jaipur and Lucknow are real and are
**linked to CCTNS**, and Jaipur's ICOC does crime and vehicle-count analytics with geo-spatial
display. **But the public pages are programme-monitoring pages about ICCC deployment, not
crime dashboards** — the operational dashboards are internal to police/city administration and
not publicly addressable. **Do not build a Phase-2 dependency on ICCC.** The realistic route
is a data-sharing MoU with a city administration, not scraping. Also
`iccc.niua.org`.

## Granularity reality check

| Level | Available? | Where | Period | Refresh | Format |
|---|---|---|---|---|---|
| `point` / `address` | **No** (public) | Mobile CCTNS captures lat/lon operationally — never published | — | — | — |
| `beat` / `ward` | **No** | Nothing found in scope | — | — | — |
| `police-station` | **Partially — record-by-record only** | Chandigarh *View Published FIR* (PS + date range); HP FIR view (24h lag, post-2016); Rajasthan FIR search; Punjab/UP/UK/J&K FIR copy (login or FIR-no. required) | 2016– (HP) | daily | HTML per record |
| `police-district` | **Yes** | Rajasthan Monthly Crime Report; Delhi `/statistics` | varies | **monthly** (Raj) / annual (Delhi) | PDF/HTML |
| `district` | **Yes** | UP *Crime in UP*; HP SCRB Crime Review; Haryana SCRB statwing; Rajasthan per-district pages | ~2016– | annual (monthly for Haryana?) | PDF, HTML (Raj) |
| `state` | Yes | NCRB + all of the above | 1953– | annual | PDF |

**The blunt version.** We want station- or beat-level counts, refreshed monthly, as CSV.
What North India actually publishes is **district-level annual PDFs**. The station-level data
undeniably exists — it is inside CCTNS, and the FIR portals prove it by exposing it one record
at a time — but **no state in scope publishes station-level counts in any aggregated,
machine-readable form.** The gap between the product vision and the published reality is
roughly **two levels of geography and one order of magnitude of machine-readability.**

The single most important consequence: **for v1 we cannot honestly render a
neighbourhood-level "is this street safe" map for North India from published data.** We can
render district-level choropleths with monthly refresh for Rajasthan and annual refresh
elsewhere, plus a genuine station-level pilot for Chandigarh (and possibly Himachal). Anything
finer requires either RTI or the FIR portals — and the FIR-portal route is a legal decision,
not an engineering one.

## Blockers and how to get past them

1. **This session's egress allowlist (research blocker, not a product blocker).**
   All `.gov.in`/`.nic.in` blocked; `web.archive.org` and every non-gov fallback blocked.
   **Fix:** re-run this dossier's link-check from an unrestricted environment, or have the
   proxy allowlist extended to `*.gov.in`, `*.nic.in`, `web.archive.org`, `data.gov.in`,
   `arcgis.com`. Until then no entry here can rise above `CITED`.
2. **FIR portals are retrieval interfaces, not datasets.** Most require an FIR number you
   would only have if you were a party to the case; several add captcha/OTP/login.
   **Fix:** prioritise the ones that accept **police station + date range** (Chandigarh
   first). Budget for captcha handling and strict rate limiting.
3. **Legal and ethical exposure — the real blocker.** FIR copies carry **names and addresses of
   accused and complainants**. Republishing them as map points would be defamatory and likely
   unlawful; several states already withhold sexual-offence records by statute. **This must be
   resolved before Phase 2 touches a FIR portal.** The defensible design: **aggregate to counts
   by station and month, discard all personal identifiers at ingestion, never store or serve
   the FIR text.** Also check each portal's terms of use and `robots.txt` — the *Delhi/Praja*
   precedent shows RTI-then-aggregate is the route that has survived public scrutiny.
4. **No jurisdiction polygons.** Station points cannot make a choropleth. BPR&D's geo-coding
   report (entry 24) shows the boundaries exist internally. **Fix:** RTI BPR&D and the state
   SCRBs for station jurisdiction boundaries; fall back to Voronoi tessellation over geocoded
   station points, clipped to district boundaries, and **label it clearly as approximate** —
   a Voronoi cell is not a jurisdiction and must never be presented as one.
5. **Taxonomy drift.** Rajasthan uses **18 custom categories**, not NCRB heads. Compounding
   this, **BNS/BNSS/BSA took effect 01-07-2024**, so any series spanning that date has an
   **IPC→BNS section-code break mid-series**. **Every multi-year series in this region needs a
   documented IPC↔BNS crosswalk**, and 2024 must be treated as a broken year.
6. **District reorganisation.** Rajasthan went to **57 police districts** (recently and
   contentiously restructured); UP and Haryana have also changed district counts.
   Time-series by district name will silently mis-join. **Fix:** maintain a district-alias and
   vintage table keyed to year, from the start.
7. **Ephemeral URLs.** Rajasthan's live monthly report is under `/old/`; Punjab's legacy portal
   is on `:7070` plain HTTP; HP downloads need an opaque `stov` token.
   **Fix:** archive-on-first-fetch — store the PDF/HTML blob, never rely on re-fetching.
8. **Pakistan-Punjab contamination.** `punjabpolice.gov.pk` ranks for Indian Punjab queries.
   **Fix:** hard-block `.pk` at the crawler level.

## Seed Leads (unconfirmed but probably real)

| Lead | Likely publisher | Concrete next step |
|---|---|---|
| **MHA master list of all state CCTNS citizen portals** | MHA/NCRB | Open `digitalpolice.gov.in/DigitalPolice/portal`, enumerate the state dropdown. **Do this first — it resolves "which URL is current" for all 10 states at once.** |
| **Rajasthan per-district crime pages generalise to all 57** | Rajasthan Home Dept | Test `home.rajasthan.gov.in/content/homeportal/en/<d>police/crimestatistics.html` for jaipurpolice, jodhpurpolice, alwarpolice, kotapolice. 4 fetches confirms or kills it. |
| **`kashmirpolice.jk.gov.in` "block-by-block" crime data** | J&K Police, Kashmir Zone | Open the site. If the block-level claim is real it is the finest granularity in North India and changes J&K's rating from 2 to 4+. |
| **Haryana SCRB publishes monthly crime statistics** | SCRB Haryana | Open `scrb.haryanapolice.gov.in/statwing` and look for a downloads/publications section. |
| **UP *Crime in UP* editions after 2016** | UP SCRB | Scrape `uppolice.gov.in/site/writereaddata/siteContent/` listing; else RTI SCRB Lucknow (`scrbup@nic.in`) for 2017–2025 editions. |
| **HP Crime Review back-catalogue depth** | HP SCRB, CID | Scrape the citizen-portal downloads listing to harvest all `(id, stov)` pairs — `id=1` and `id=12` are known, implying ≥12 documents. |
| **Delhi Police annual review as a document** | Delhi Police | Open `delhipolice.gov.in/statistics`; cross-check against Praja's PDFs, which cite their sources. |
| **Undocumented JSON behind CCTNS portals** | NCRB CCTNS build | Open Chandigarh's ViewPublishFIR with devtools; the MVC path shape suggests XHR/JSON behind the form. **One finding here ports to every CCTNS state.** |
| **AIKosh hosts CSV/JSON of Crime Review** | IndiaAI / MeitY | Open the AIKosh dataset pages and check the resource formats. |
| **RTI 4(1)(b) pages — not found for any state in scope** | each state police | These exist by statutory mandate but none surfaced in search. Find via site-search for "4(1)(b)" / "suo motu" on each police domain. Haryana has issued explicit 4(1)(b) uploading guidelines, so Haryana is the best first test. |

## Phase 2 recommendations (ranked)

1. **Link-check this entire JSONL from an unrestricted network.** Nothing here is opened.
   Cheap, and it gates everything else. Promote each entry to `VERIFIED_*` or kill it.
2. **Open `digitalpolice.gov.in/DigitalPolice/portal`** and rebuild the canonical portal URL
   list for all 10 jurisdictions from the authoritative source.
3. **Pilot Chandigarh *View Published FIR*.** Smallest jurisdiction, `/public/` path, search by
   PS + date range, stock CCTNS software. **Goal is not data volume — it is to learn the CCTNS
   citizen-portal contract once and port it.** Pair with a written legal position on
   aggregate-only publication *before* any collection begins.
4. **Ingest the three real statistics series:** Rajasthan Monthly Crime Report (best cadence),
   UP *Crime in UP* (largest population), HP SCRB Crime Review (cleanest structure).
   District-level, PDF → tabular extraction.
5. **Test the Rajasthan per-district URL pattern** (4 fetches). If it holds, it is the single
   best district-level HTML series in North India and needs one scraper, not 57.
6. **Build the station roster + geocoding pipeline.** Harvest Delhi `/telephonedirectory`,
   HP `viewpolicestation.htm`, Ladakh `formation.html`; geocode; cross-check against the
   ArcGIS layer. Read the BPR&D geo-coding report first.
7. **File RTIs for the five negative-finding jurisdictions** (Chandigarh, Punjab, Uttarakhand,
   J&K, Ladakh). **Use identical wording** — request SCRB **monthly station-wise cognizable
   crime returns**, explicitly invoking **s.7(9) for electronic form**. Start with **Ladakh**
   (smallest, most likely to yield complete data) to debug the request wording cheaply, then
   fire the rest. Route Chandigarh/J&K/Ladakh appeals to the **CIC**, Punjab/Uttarakhand to
   their **SICs**.
8. **Do not invest in ICCC/Safe City dashboards.** Not publicly addressable; MoU territory.

## State-by-state accessibility rating

| State/UT | Rating | Justification |
|---|---|---|
| **Chandigarh** | **4** | Public `/public/` FIR search by **police station + date range** — finest granularity in scope. Tiny, enumerable, stock CCTNS. Loses a point: **no crime statistics published at all**. |
| **Rajasthan** | **4** | Only **monthly** statistics series in the region; likely templated per-district HTML pages; FIR search with download. Loses a point for the `/old/` path fragility and an 18-category custom taxonomy. |
| **Himachal Pradesh** | **4** | Only state with a **named, downloadable annual statistical volume** (SCRB Crime Review) **plus** a dedicated station-directory search **plus** a 24-hour FIR upload commitment. Loses a point for the opaque `stov` token and unknown catalogue depth. |
| **Delhi (NCT)** | **3** | Dedicated `/statistics` page, press archive, telephone directory, and **the best NGO shadow-dataset in India (Praja)**. Capped at 3: `police-district` granularity (15 districts for 20M people is coarse), annual cadence. |
| **Uttar Pradesh** | **3** | A real, directly-linked district-wise annual PDF (*Crime in UP*), active SCRB, e-FIR/UPCOP. Capped at 3: **~14-month lag**, post-2016 editions unconfirmed, e-FIR is login-gated. |
| **Haryana** | **3** | Dedicated **SCRB statistical wing** claiming monthly crime statistics — genuinely promising. Capped at 3 because publication (vs. internal compilation) is unconfirmed, and services are fragmented across three portals. |
| **Punjab** | **2** | SAANJH is mature but FIR copy is an **application form requiring the FIR number** — retrieval, not data. **No statistics published.** Legacy host on plain-HTTP `:7070`. |
| **Uttarakhand** | **2** | Functional CCTNS citizen portal with View FIR, but **login-gated**, and **no statistics published**. RTI-dependent. |
| **Jammu & Kashmir** | **2** | Mature eServices portal, but **no statistics found**, login-gated, and **s.8(1)(a) security exemptions are a realistic RTI obstacle**. Could rise to 4 if the `kashmirpolice.jk.gov.in` block-level claim is real. |
| **Ladakh** | **1** | **Nothing published.** Portal exists; statistics do not. Offsetting positive: so small that one RTI could yield the complete record — and tiny denominators make rates unmappable anyway. |

**Mean accessibility for the region: 2.8/5.**
