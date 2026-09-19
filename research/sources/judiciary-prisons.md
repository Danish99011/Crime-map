# Judiciary, Prosecution & Prisons — the criminal-justice outcomes layer
_Agent: judiciary-prisons · Researched: 2026-09-19 · Entries: 7 verified / 28 total_

> **Verification honesty note.** This session's egress proxy blocked every `*.gov.in`,
> `devdatalab.org`, `indiankanoon.org`, `justicehub.in`, `dataful.in` and `arxiv.org` host
> (403 CONNECT at the gateway; confirmed via `curl $HTTPS_PROXY/__agentproxy/status`).
> Only `github.com`, `raw.githubusercontent.com` and `wikipedia.org` were fetchable, and the
> session-wide WebSearch budget (200 calls) was exhausted mid-research by sibling agents.
> Consequently **no government portal below was opened directly by me.** Where I mark
> `VERIFIED_LIVE` it is because I read *primary artefacts of that portal* — real captured
> eCourts HTML/YAML fixtures, real request/response cassettes, and working client code with
> verbatim endpoint constants — hosted on GitHub. That is stronger evidence than a landing-page
> screenshot for the questions that matter here (does the record carry an FIR number? what are
> the POST parameters?), but it is *not* the same as me loading the page. Everything else is
> `CITED` or `UNVERIFIED`. Re-verify all `.gov.in` URLs from an unblocked network before Phase 2.

---

## Executive summary

- **The FIR-number join is real, and it is the single most important finding in this dossier.**
  eCourts district- and High-Court case records contain a discrete **"FIR Details" table** with
  the fields *State, District, Police Station, FIR Number, Year*. I verified this against a real
  captured case page: CNR `KAHC010337682024` parses to `fir: {state: KARNATAKA, district:
  BENGALURU, police_station: INDIRANAGAR PS, number: '155', year: 2024}`. Court data is therefore
  an **indirect route to police-station-attributed crime records for every state in India**,
  including the ~20 states that publish no crime data of their own.

- **eCourts is not just searchable by FIR — it is *enumerable* by police station.** The v6 portal
  exposes `?p=casestatus/fillPoliceStation`, which returns the full police-station dropdown for a
  given state/district/court-complex/establishment, with values of the form
  `"29-5137032"` (state part + **uniform code**). A one-time crawl of that endpoint across all
  establishments yields a **national police-station master list with stable numeric codes** — a
  crosswalk asset in its own right, independent of any crime data. Then
  `?p=casestatus/submitFirNo` takes `police_st_code`, `uniform_code`, `fir_no`, `firyear`,
  `case_status` and returns the matching case(s). FIR numbers restart at 1 each calendar year per
  station, so `for fir_no in 1..N` is a complete, bounded enumeration strategy.

- **But the court route systematically undercounts crime, in a *directional* way.** Only
  chargesheeted matters reach court. Cases closed by police (final report / "untraced" / mistake
  of fact), compounded, or still under investigation never appear. So a police-station case count
  from eCourts is a **lower bound on FIRs, biased toward whatever police chose to charge** — and
  that bias varies by state, by crime head, and by station. It must never be presented on a map
  as "crime in this neighbourhood".

- **Finest achievable spatial granularity in this domain: `police-station`** — but as a *name and
  code*, not a polygon and not a point. The court's own geography (court establishment → taluka /
  district HQ) is the wrong geography: it is where the case is *heard*, not where the crime
  happened. Police-station jurisdiction boundaries are not published by most states, so this
  domain hands you a label that still needs a gazetteer from elsewhere to put on a map.

- **The best ready-made analytical asset is Development Data Lab's judicial dataset** —
  ~81M district-court cases, 2010–2018 (25M criminal / 65M civil), ~15 GB of Stata `.dta`, hosted
  on Dropbox, **CC BY-NC-SA 4.0**. I verified its exact file layout from a downstream project:
  `cases/cases_2010.dta … cases_2018.dta`, `acts_sections.dta`, and `keys/` containing
  `act_key`, `section_key`, `disp_name_key`, `type_name_key`, `purpose_name_key`,
  `cases_state_key`, `cases_district_key`, `cases_court_key`. **District and court-establishment
  identifiers and act/section codes are present. FIR number and police station are NOT** — DDL
  dropped them in anonymisation. So DDL gives you nine years of district × act × section ×
  outcome for free; only a fresh scrape gives you police stations.

- **NJDG's "open API" is real but is not open to us.** The Department of Justice text is explicit:
  the API is "provided to the Central & State Government … using a departmental ID and access
  key", for "institutional litigants", with public extension only *"proposed"*. Several GitHub
  repos cite endpoints like `njdg.ecourts.gov.in/njdgnew/api/index.php` or `/api/search` with a
  Bearer token — these appear in LLM-generated projects with no evidence of ever having returned
  data, and I treat them as **unverified and probably hallucinated**. What *is* public is the NJDG
  dashboard itself, with state → district → establishment drill-down and a civil/criminal split,
  updated daily.

- **CAPTCHA is the operational blocker, not a legal wall.** eCourts uses self-hosted **Securimage**
  (`/vendor/securimage/securimage_show.php`) plus a per-session `app_token`. It is weak enough that
  one open-source client ships a threshold-based solver and another pipes the image to CapSolver.
  That is exactly why volume scraping is the legally exposed act: defeating a CAPTCHA is
  circumventing an access control, not merely reading a public page.

- **The judiciary has no open-data policy.** This is the structural blocker for the whole domain
  (Vidhi's *Open Courts in the Digital Age* makes the case). Bulk access is negotiated per High
  Court, not granted by statute. DDL's release is the precedent that it can be done.

- **Prisons are jail-level but annual and aggregate.** NCRB *Prison Statistics India* 2023 covers
  1,332 prisons (152 Central, 436 District, 549 Sub, 101 Open, 47 Special, 35 Women, 10 Borstal,
  2 other), national occupancy 120.8%. Jails are geocodable *points* with known types, which makes
  a decent map layer — but PSI publishes by state × jail-type, not per named jail, in most tables.
  e-Prisons NPIP is the live counterpart. NCRB is another agent's beat; here it is flagged only for
  its jail geography.

- **Prosecution and legal-aid data are thin and state-fragmented.** Conviction rates exist
  (Maharashtra's Directorate of Prosecution publishes one; NCRB publishes them nationally) but
  rarely below state level and rarely as data. NALSA publishes Lok Adalat, legal-aid, victim-
  compensation and undertrial-prisoner statistics — as PDFs, state-level, irregular.

- **Single biggest blocker:** there is no bulk export. Everything police-station-level in this
  domain is behind a per-record CAPTCHA'd form, which converts a data problem into a
  ~10^7-request crawling-and-legal problem. The way past it is to ask, not to scrape: the
  e-Committee / High Court Registrar (Computer Cell) route, with DDL as the precedent.

---

## Source entries

### 1. eCourts Services — District & Taluka Courts (CIS v6 portal)

The public face of the national district-court Case Information System (CIS National Core 3.2).
Cascading dropdowns: State → District → Court Complex → Court Establishment. Case Status can be
searched by CNR, Case Number, Filing Number, Party Name, Advocate Name, **FIR Number**, Act and
Case Type. Every search is CAPTCHA-gated and carries a per-session `app_token`.

```yaml
id: ecourts-district-services
publisher: eCommittee, Supreme Court of India / NIC / Department of Justice
tier: 3
urls: {landing: "https://services.ecourts.gov.in/ecourtindia_v6/",
       data: "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"}
geo_coverage: all-India (district & taluka courts, ~18,735 courts incl. High Courts on NJDG)
geo_granularity: police-station   # via the FIR Details block; court establishment otherwise
unit_of_record: case-record
time_start: ~2010 (CIS rollout; varies by establishment)
time_latest: current (daily)
cadence: realtime
taxonomy: IPC+SLL (BNS from 2024-07-01)
formats: [HTML, PDF]
access: captcha
machine_readable: 2
license: unstated
ingest_difficulty: 4
priority: 5
verification: VERIFIED_LIVE
```

**Verbatim endpoint map** (from a working client, `neveonai-sys/mamlaAI`, base
`https://services.ecourts.gov.in/ecourtindia_v6`):

| Purpose | `?p=` endpoint |
|---|---|
| CNR lookup | `cnr_status/searchByCNR` |
| Case history | `home/viewHistory` |
| PDF fetch | `home/display_pdf` |
| District list | `casestatus/fillDistrict` |
| Court complex list | `casestatus/fillcomplex` |
| Establishment list | `casestatus/fillCourtEstablishment` |
| **Police station list** | **`casestatus/fillPoliceStation`** |
| **FIR search** | **`casestatus/submitFirNo`** |
| Party-name search | `casestatus/submitPartyName` |
| Filing-no search | `casestatus/submitFillingNo` |
| Advocate search | `casestatus/submitAdvName` |
| Case-type list | `casestatus/fillCaseType` |
| Cause list | `cause_list/fillCauseList`, `cause_list/submitCauseList` |
| Orders/judgments | `courtorder/submitCaseNo`, `courtorder/submitOrderDate`, `courtorder/submitCourtNo` |

CAPTCHA image: `https://services.ecourts.gov.in/ecourtindia_v6/vendor/securimage/securimage_show.php`
(Securimage; cache-buster `?cb=<ts>` must not clobber an existing query string or the PHP session
namespace desyncs).

**Caveats.** CIS deployment date varies by establishment, so early years are incomplete and the
incompleteness is geographically patterned. The FIR block is a CIS field that some establishments
leave blank. Post-2024-07-01 filings carry BNS sections; earlier ones IPC — the map needs an
IPC↔BNS crosswalk or it will split one crime type into two series.

---

### 2. eCourts FIR-number case search — **the police↔court join**

`POST …/?p=casestatus/submitFirNo` with parameters, verbatim from working client code:

```
state_code, dist_code, court_complex_code, est_code,
police_st_code, uniform_code, fir_no, firyear,
case_status, fir_captcha_code, ajax_req, app_token
```

`police_station_code` from the dropdown (e.g. `"29-5137032"`) splits on the first `-` into
`police_st_code="29"` and `uniform_code="5137032"`. `case_status` ∈ {Pending, Disposed, Both}.
The High Court equivalent is a plain GET page:
`https://hcservices.ecourts.gov.in/ecourtindiaHC/cases/fir1.php?state_cd=11&dist_cd=1&court_code=1&stateNm=Odisha/`.

Returned case detail pages carry a `FIR Details` table which parses to
`{State, District, Police Station, FIR Number, Year}`, plus `Under Act(s)` and `Under Section(s)`
(e.g. `Under Act(s): IPC`, `Under Section(s): 188`).

```yaml
id: ecourts-fir-search
tier: 3
geo_granularity: police-station
unit_of_record: case-record
access: captcha
machine_readable: 2
license: unstated
ingest_difficulty: 5
priority: 5
verification: VERIFIED_LIVE
caveats:
  - "Chargesheeted cases only — FIRs closed by police, still under investigation, or compounded never appear."
  - "FIR→court lag: months to years; recent months are structurally empty."
  - "FIR Details is an optional CIS field; blank/zero in some establishments."
  - "Police-station string in the FIR block may not equal the fillPoliceStation dropdown label."
  - "Enumerating FIR 1..N per station per year is ~10^7 CAPTCHA'd requests nationally."
```

---

### 3. eCourts police-station master list (`fillPoliceStation`)

`POST …/?p=casestatus/fillPoliceStation` with `state_code, dist_code, court_complex_code, est_code,
ajax_req, app_token` returns HTML `<option>` elements whose `value` is the composite police-station
code. **Crawled once across all establishments this produces a national police-station registry
with stable codes — a crosswalk asset worth building even if no case data is ever scraped.** The
`uniform_code` shape strongly suggests the CCTNS/NCRB uniform police-station code, which would make
it joinable to CCTNS-derived sources; *this is a hypothesis I could not verify and it should be
tested against a known CCTNS code list before being relied on.*

```yaml
id: ecourts-police-station-master
tier: 3
geo_granularity: police-station
unit_of_record: boundary-polygon   # actually a code registry, no geometry
access: scrape
machine_readable: 2
ingest_difficulty: 3
priority: 5
verification: VERIFIED_LIVE
notes: "No geometry, no lat/lon. Names are uppercase free-text with 'PS'/'P.S.' variants. Deduplicate across establishments — one station appears under every establishment whose jurisdiction it falls in."
```

---

### 4. CNR number — the national case identifier and its geocoding value

16-character alphanumeric, structured **State (2) + District (2) + Court Establishment (2) +
Filing serial (6) + Year (4)**. Verified against a real record: `KAHC010337682024` = Karnataka
High Court, establishment 01, serial 033768, 2024. It is constant for the life of the case and
survives transfer.

**Is it geocodable?** Partially, and to the wrong thing. It resolves to a *court establishment*,
which sits in a taluka or district HQ — the venue, not the crime scene. It is useful as (a) a
primary key, (b) a state/district roll-up key, (c) a way to detect which establishment handles a
given area. It is **not** a substitute for the FIR block's police station.

```yaml
id: ecourts-cnr-scheme
tier: 3
geo_granularity: district
unit_of_record: case-record
access: open-download   # the scheme itself; lookups are captcha'd
machine_readable: 3
priority: 4
verification: VERIFIED_LIVE
```

---

### 5. eCourts High Court Services (`hcservices.ecourts.gov.in`)

CIS National Core 1.0. Same search surface as district courts including FIR search
(`/ecourtindiaHC/cases/fir1.php`). Endpoint constants verified from `openjustice-in/ecourts`:
`BASE_URL = "https://hcservices.ecourts.gov.in/ecourtindiaHC"` with
`/cases/s_orderdate_qry.php`, `/cases/s_show_business.php`, `/cases/display_pdf.php`,
`/cases/s_casetype_qry.php`, `/cases/s_actwise_qry.php`, `/cases/o_civil_case_history.php`,
`/cases/case_no_qry.php`, `/cases/highcourt_causelist_qry.php`. Responses are `^^`/`^#`-delimited
strings, not JSON. `"INVALID CAPTCHA"` in the first field signals a retry.

```yaml
id: ecourts-high-court-services
tier: 3
geo_granularity: district           # HC bench jurisdiction; FIR block still gives PS
unit_of_record: case-record
access: captcha
machine_readable: 2
ingest_difficulty: 4
priority: 3
verification: VERIFIED_LIVE
notes: "High Court matters are appeals/quashings/bail — useful for OUTCOME, near-useless for incidence."
```

---

### 6. NJDG — District & Subordinate Courts dashboard

Daily-refreshed pendency and disposal, drill-down by **age of case, State and District**, with a
civil/criminal split. DoJ text (captured verbatim in a GitHub-hosted scrape of doj.gov.in):
"database of orders, judgments and case details of 18,735 District & Subordinate Courts and High
Courts", "over 26.35 crore cases and more than 27.06 crore orders/judgments". "Reasons for delay"
were added as a field.

```yaml
id: njdg-district-subordinate
urls: {landing: "https://njdg.ecourts.gov.in/njdgnew/index.php"}
tier: 3
geo_granularity: district           # establishment-level views exist in the UI
unit_of_record: aggregate-count
time_start: "2015-09-19"
cadence: daily
lag: near-zero
taxonomy: custom                    # civil/criminal + case-type, not NCRB heads
formats: [dashboard-only, PDF]
access: scrape
machine_readable: 2
priority: 3
verification: CITED
caveats:
  - "Stock-and-flow, not crime counts. Pendency ≠ incidence."
  - "Criminal/civil split only; no crime-head detail."
  - "Snapshot semantics — no published historical time series; must be snapshotted daily to build one."
```

### 7. NJDG — High Courts · 8. NJDG — Supreme Court

`https://njdg.ecourts.gov.in/hcnjdgnew/` and `https://njdg.ecourts.gov.in/scnjdg/` (SC onboarded
2023-09-14). Same caveats, coarser geography (bench / national).

### 9. NJDG Open API — **restricted, not public**

> "In consonance with the National Data Sharing and Accessibility Policy (NDSAP) … Open
> Application Programming Interface (API) has been provided to the Central & State Government to
> allow easy access to the NJDG data using a departmental ID and access key. This will allow the
> institutional litigants to access the NJDG data for their evaluation and monitoring purposes.
> It is proposed to expand the facility to non-institutional litigants as well in future."
> — Department of Justice, "The National Judicial Data Grid (NJDG)"

```yaml
id: njdg-open-api
tier: 3
access: on-request
machine_readable: 4
priority: 2
verification: CITED
how_to_obtain: "Write to Department of Justice, Ministry of Law & Justice (eCourts Mission Mode Project) requesting a departmental ID and access key, stating the institutional user. A private crime-map is not an 'institutional litigant' and will likely be refused; a partnership with a state Home Department, a Legal Services Authority or a university may qualify. Fall back to daily dashboard snapshots."
notes: "GitHub repos citing 'https://njdg.ecourts.gov.in/njdgnew/api/index.php' or '/njdgnew/api/search' with a Bearer token are LLM-generated projects with no evidence of a live response. Treat as hallucinated until a 200 is observed."
```

---

### 10. Judgments & Orders portal (`judgments.ecourts.gov.in`)

Free-text search over High Court (and Supreme Court) judgments and final orders, with structured
filters: Bench, Case Type, Case Number, Year, Petitioner/Respondent, Judge, **Act, Section**,
Decision-date range. The Act+Section filter is what makes it useful here: it lets you count
disposals by offence without parsing free text.

```yaml
id: ecourts-judgments-portal
urls: {landing: "https://judgments.ecourts.gov.in/"}
tier: 3
geo_granularity: state              # High Court bench
unit_of_record: narrative-document
cadence: daily
formats: [HTML, PDF]
access: captcha
machine_readable: 2
priority: 2
verification: CITED
```

### 11. Supreme Court of India — judgments & case status (`sci.gov.in`)

`https://www.sci.gov.in/` with judgment search by case number (`/judgements-case-no/`). National
granularity; relevant only for doctrine and for validating outcome definitions.
`tier: 3 · geo_granularity: national · priority: 1 · verification: CITED`

---

### 12. Indian Kanoon (`indiankanoon.org`) — judgment corpus

The largest free Indian judgment search engine, covering SC, HCs, tribunals and some district
courts. Full-text with section/act linking.

### 13. Indian Kanoon API (`api.indiankanoon.org`) — the legal route

Documentation at `https://api.indiankanoon.org/documentation/`, terms at `…/terms/`. Four endpoint
families (search, document, document fragments, …); JSON or XML by `Accept` header; auth either by
a shared API token generated on the site or by public/private key with per-request signing.
**Charged per search/document call.** Terms require a **"Powered by IKanoon"** attribution wherever
results are rendered to end users.

```yaml
id: indiankanoon-api
tier: 5
urls: {api: "https://api.indiankanoon.org/", docs: "https://api.indiankanoon.org/documentation/"}
geo_granularity: state
unit_of_record: narrative-document
access: paid
machine_readable: 5
license: ToU-restricts-reuse
ingest_difficulty: 2
priority: 2
verification: CITED
notes: "Scraping indiankanoon.org HTML is a separate act not covered by these API terms and is against the spirit of a paid API that exists precisely to serve this need. Budget for the API; do not scrape the site."
caveats:
  - "Judgment text ≠ structured crime data. No FIR field, no reliable police station, no geocode."
  - "Coverage skews to reported/appellate matters — the opposite of the volume crime we care about."
```

---

### 14. Development Data Lab — Indian Judicial Data (**verified to exist; the key asset**)

~81 million district-court cases, 2010–2018, from ~7,000+ district and subordinate courts staffed
by 80,000+ judges. The DDL team's own paper (*In-group bias in the Indian judiciary: Evidence from
5 million criminal cases*) states the complete unfiltered release contains **77 million case
records**, of which their criminal analysis sample is 5 million; DDL's own portal copy says 81M
(25M criminal / 65M civil). Anonymised. Hosted on **Dropbox**, linked from the portal page.

**File layout — verified from a downstream project's README:**

```
ddl_data/
  cases/  cases_2010.dta … cases_2018.dta
  acts_sections.dta
  keys/   act_key.dta  section_key.dta  disp_name_key.dta
          type_name_key.dta  purpose_name_key.dta
          cases_state_key.dta  cases_district_key.dta  cases_court_key.dta
```

Variables per the DDL description: filing / registration / hearing / decision dates, petitioner and
respondent names, position of the presiding judge, **the acts and sections under which the case was
filed**, and the final decision / disposition. ~15 GB.

```yaml
id: ddl-judicial-data
publisher: Development Data Lab
tier: 4
urls: {landing: "https://www.devdatalab.org/judicial-data",
       data: "https://www.dropbox.com/sh/hkcde3z2l1h9mq1/AADRe-BuBQ92ozAJiG7YERdCa?dl=0"}
geo_coverage: all-India district & subordinate courts
geo_granularity: district           # plus court establishment via cases_court_key
unit_of_record: case-record
time_start: "2010"
time_latest: "2018"
cadence: one-off
lag: "7+ years and growing"
taxonomy: IPC+SLL                   # act_key / section_key, pre-BNS
formats: [CSV, XLSX]                # actually Stata .dta; convertible
access: open-download
machine_readable: 4
license: CC-BY-NC-SA-4.0
ingest_difficulty: 2
priority: 5
verification: CITED                 # file layout & variables VERIFIED_LIVE from downstream code; portal not fetched
caveats:
  - "NO FIR number and NO police station — stripped in anonymisation. District is the floor."
  - "Series stops in 2018. Useless for 'is this street safe tonight'; essential as a nine-year baseline."
  - "Non-commercial licence. A commercial crime map needs a separate licence from DDL."
  - "Scraped from eCourts, so it inherits every CIS coverage gap and the chargesheet filter."
  - "Pre-BNS section codes only."
  - "District IDs need mapping to current districts — India has created many districts since 2018."
how_to_obtain: "Download from the Dropbox link on devdatalab.org/judicial-data. For de-anonymised or extended access, apply to DDL as a researcher."
```

### 15. DDL replication package — *In-group Bias in the Indian Judiciary*

The 5M-criminal-case analysis build, with `cases_clean_20XX` annual Stata files, `judges_clean`
(judge demographics), `poi_master` (People of India), ACLED India 2005–2023, and **district-level
matching keys**. Archived at **Harvard Dataverse DOI `10.7910/DVN/GHLGSW`** and on Google Drive.
Needs ~30 GB RAM, Stata 16+. `make_justice.do` is the master build.

```yaml
id: ddl-paper-justice-replication
tier: 4
urls: {landing: "https://github.com/devdatalab/paper-justice",
       data: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GHLGSW"}
geo_granularity: district
unit_of_record: case-record
time_start: "2010"
time_latest: "2018"
access: open-download
machine_readable: 4
priority: 3
verification: VERIFIED_LIVE
notes: "Dataverse DOI is the stable archival copy — prefer it over Dropbox for reproducibility. Also ships an open-source name→gender/religion classifier (97% out-of-sample), which is a reusable tool and a serious ethical hazard if applied to a public map. Do not."
```

### 16. DAKSH — Deciphering Judicial Data / DAKSH database

DAKSH systematically cleans and standardises eCourts case and hearing data into its own database,
explicitly to fix "lot of inconsistencies in data". The cleaning methodology is as valuable as the
data: it is the published record of where eCourts data is inconsistent.
`https://www.dakshindia.org/deciphering-judicial-data-daksha-database/`
`tier: 4 · geo_granularity: district · access: on-request · priority: 3 · verification: CITED`

### 17. Justice Hub (`justicehub.in`) — curated eCourts-derived datasets

An open data portal of eCourts-derived research datasets. Confirmed holdings:

| Dataset | Content |
|---|---|
| Unpacking Judicial Data to Track POCSO Implementation (Assam, Delhi, Haryana) | 19,783 district-court cases, all details from eCourts |
| Analysis of CALPRA 1986 | 10,800 cases, 1 Jan 2015 – Mar 2023, across Assam, Bihar, Jharkhand, Maharashtra, Tamil Nadu, UP |
| Contract Enforcement Litigation (NIPFP) | 5 acts, court complexes in ~2 cities per state |

```yaml
id: justicehub-datasets
tier: 4
urls: {landing: "https://justicehub.in/dataset"}
geo_granularity: district
unit_of_record: case-record
access: open-download
machine_readable: 3
priority: 3
verification: CITED
notes: "The POCSO and CALPRA sets are the best available worked examples of act-specific eCourts extraction at scale, with methodology. Read them before writing a scraper."
```

### 18. `openjustice-in/ecourts` — the reference scraping toolkit

GPL-3.0-or-later Python library "primarily meant for journalists and data researchers who need
bulk access". Covers High Court services; district coverage is the stated goal. Implements Act-Type
search, cause lists, orders by date; Case-Number and **FIR-Number search (police station, FIR
number, year, status)** are listed as in development. Ships `ecourts get-case-type` /
`get-act-type` because *"different courts use distinct numbering systems for case types and acts"*.

**Explicitly single-threaded, no parallelism, "do not hammer the site"**, retry with
`time.sleep(1)` and backoff on 5xx, 15 attempts default. Its own README: *"if you run this code,
you are responsible for the legal implications of the same."*

Entity model confirms the extractable schema — `Case`: `case_type, registration_number, cnr_number,
filing_number, registration_date, first_hearing_date, decision_date, case_status,
nature_of_disposal, coram, bench, state, district, judicial, petitioners[], respondents[],
orders[], case_number, hearings[], category, sub_category, objections[], not_before_me,
filing_date, fir, token`. `FIR`: `state, district, police_station, number, year`.

```yaml
id: openjustice-ecourts-toolkit
tier: 4
urls: {landing: "https://github.com/openjustice-in/ecourts", docs: "https://pypi.org/project/ecourts/"}
license: GPL-3.0-or-later
access: open-download
machine_readable: 5
priority: 4
verification: VERIFIED_LIVE
notes: "Adopt its rate-limiting ethic wholesale. Note the GPL: linking it into our pipeline has licence consequences for anything we distribute."
```

---

### 19. NCRB — Prison Statistics India (PSI)  ⚑ *NCRB covered in depth by another agent*

Flagged here **only for jail geography**. PSI 2023: 1,332 prisons — 549 Sub Jails, 436 District
Jails, 152 Central Jails, 101 Open Jails, 47 Special Jails, 35 Women Jails, 10 Borstal Schools,
2 other. Capacity 439,119; population 530,333 (down from 573,220 in 2022); occupancy 120.8%
(131.4% in 2022, 130.2% in 2021). Highest occupancy: District Jails 136.6%. Undertrials concentrate
in district jails (50.5%) and central jails (37.6%); convicts in central jails (65.5%).
PSI 2022 PDF observed at
`https://www.ncrb.gov.in/uploads/nationalcrimerecordsbureau/custom/psiyearwise2022/1701613297PSI2022ason01122023.pdf`.

```yaml
id: ncrb-prison-statistics-india
tier: 1
geo_granularity: state              # jail-TYPE within state; not per named jail in most tables
unit_of_record: aggregate-count
time_start: "1995"
time_latest: "2023"
cadence: annual
lag: "18-22 months"
formats: [PDF, XLSX]
access: open-download
machine_readable: 1
license: GODL-India
priority: 2
verification: CITED
caveats:
  - "State × jail-type, not per-jail. Individual jail names appear only in a few annexures."
  - "Undertrial vs convict is the split that matters and it is only state-level."
  - "Jail location is where a person is HELD, not where the offence occurred — never map prison counts as neighbourhood crime."
```
Mirror worth knowing: Dataful (`dataful.in`) republishes PSI as tidy year×state×jail-type series
(e.g. datasets 19003, 19004) — paid/freemium, `tier: 5`, saves substantial PDF-parsing effort.

### 20. e-Prisons / National Prison Information Portal (NPIP)

NIC's prison suite: **ePrisons MIS** (internal, per-prison day-to-day), **NPIP** (citizen-facing
statistics for jails across the country), and **Kara Bazaar**. Modules include Prisoner Information
Management, Visitors, Hospital, **Police Monitoring**, **Courts Management**, Roaster, Kiosk.
Cloud/SaaS from NIC Cloud, free to adopt.

```yaml
id: eprisons-npip
publisher: National Informatics Centre / MHA
tier: 3
urls: {landing: "https://eprisons.nic.in/npip/public/DashBoard",
       data: "https://eprisons.nic.in/NPIPDashboard/"}
geo_granularity: point              # individual jail
unit_of_record: aggregate-count
cadence: realtime
formats: [dashboard-only]
access: scrape
machine_readable: 2
priority: 2
verification: CITED
notes: "The 'Courts Management' module means e-Prisons already holds a prisoner↔case link internally — the missing end of the FIR→court→custody chain. Not public. Worth an RTI."
caveats: ["Dashboard-only; no export observed.", "Not all states are on e-Prisons; some run their own PMS."]
```

### 21. e-Prisons MIS (internal) — `access: rti-only`
Per-prisoner operational records. Not public and should not be. Aggregates obtainable by RTI to the
state Prisons Department / DG (Prisons). `tier: 3 · priority: 1 · verification: UNVERIFIED`

### 22. State Prison / Correctional Services Departments
Each state runs a Prisons Department site with jail directories, annual administration reports and
sometimes daily strength. Quality is wildly uneven. Concrete next step: enumerate the 36 state/UT
departments, record per-state whether a jail directory with addresses exists (that is your jail
gazetteer). `tier: 2 · geo_granularity: point · access: scrape · priority: 2 · verification: UNVERIFIED`

### 23. Model Prison Manual 2016 / Model Prisons and Correctional Services Act 2023 (MHA)
Normative, not statistical. Defines the categories (jail types, undertrial classes, reporting
formats) that PSI and e-Prisons use — needed to read those correctly.
`tier: 3 · unit_of_record: narrative-document · priority: 1 · verification: UNVERIFIED`

---

### 24. State Directorates of Prosecution — conviction rates

Post-CrPC s.25A each state has a Directorate of Prosecution separated from the police. Maharashtra's
publishes a conviction-rate page (`https://dop.maharashtra.gov.in/conviction-rate`); the Home
Department page is `https://home.maharashtra.gov.in/en/organization/directorate-of-public-prosecution/`.
Reported figures: Maharashtra 9% (2013) → 53% (2025, per CM); Tamil Nadu ~62–67.8%; Kerala 17.7%
(historic). These are political numbers quoted without method — treat as unusable until the
underlying series is obtained.

```yaml
id: state-directorates-of-prosecution
tier: 2
geo_granularity: state              # district-wise exists internally
unit_of_record: aggregate-count
cadence: irregular
formats: [HTML, PDF]
access: scrape
machine_readable: 1
priority: 2
verification: CITED
how_to_obtain: "RTI to each state Directorate of Prosecution for district-wise cases instituted / decided / convicted / acquitted by year and by major head. Districts DO hold this — District Government Pleader offices report it monthly."
caveats:
  - "Denominator is never stated: conviction rate over cases decided, over cases tried, or over FIRs? These differ by a factor of several."
  - "Politically reported figures (CM statements) are not a data series."
```

### 25. NALSA — statistics

`https://nalsa.gov.in/statistics/` is described as carrying Lok Adalat reports, mediation
settlements, legal-services beneficiaries, awareness camps, para-legal volunteers, legal services
clinics, **victim compensation schemes**, training programmes and **undertrial prisoners**.
National Lok Adalat reports at `https://nalsa.gov.in/national-lok-adalat-report/`. Scale: the 3rd
National Lok Adalat of 2026 settled >2.10 crore cases worth ₹13,589.28 crore.

```yaml
id: nalsa-statistics
tier: 3
geo_granularity: state              # SLSA; DLSA-level exists in some reports
unit_of_record: aggregate-count
cadence: quarterly                  # Lok Adalats are quarterly national events
formats: [PDF]
access: open-download
machine_readable: 1
priority: 2
verification: CITED
caveats:
  - "Lok Adalat 'disposals' are overwhelmingly cheque-bounce, motor-accident claims and utility matters — NOT violent crime. Do not read as crime resolution."
  - "PDF tables, state-level, inconsistent format between events."
```

### 26. NALSA victim compensation (and the SLSA application system)

`https://nalsa.gov.in/victim-compensation/`; state schemes implemented by SLSAs/DLSAs under CrPC
s.357A (now BNSS s.396), plus the NALSA *Compensation Scheme for Women Victims/Survivors of Sexual
Assault/other Crimes, 2018*. An application system was observed at
`https://scourtapp.nic.in/lsams/nologin/victimcompensation.action` (LSAMS). State scheme pages
exist (e.g. `https://madhyapradesh.nalsa.gov.in/victim-compensation/`).

```yaml
id: nalsa-victim-compensation
tier: 3
geo_granularity: district           # DLSA awards compensation; district is the natural unit
unit_of_record: victim-record       # published only as aggregate-count
cadence: annual
access: rti-only
machine_readable: 1
priority: 2
verification: CITED
how_to_obtain: "RTI to each State Legal Services Authority for district-wise applications received / awards made / amount disbursed by offence category and year. LSAMS holds this; DLSAs report it upward."
notes: "Compensation awards are the only source in this domain that is keyed to the VICTIM and to the offence category, at district level. That is a genuinely different and underused view of serious crime."
```

### 27. Juvenile Justice — JJBs, CWCs, NCPCR  ⚑ *overlaps a child-protection agent*

Juvenile Justice Boards and Child Welfare Committees operate at district level under the JJ Act
2015; NCPCR (`ncpcr.gov.in`) and state SCPCRs monitor. NCRB *Crime in India* carries "Juveniles in
conflict with law" tables. JJB case data is **not** in the eCourts district-court CIS in most
states, so it is a structural hole in the FIR→court chain for offences by minors.

```yaml
id: juvenile-justice-boards-cwc
tier: 3
geo_granularity: district
unit_of_record: aggregate-count
cadence: annual
access: rti-only
machine_readable: 1
priority: 2
verification: UNVERIFIED
how_to_obtain: "RTI to State Department of Women & Child Development / SCPCR for district-wise JJB institution and disposal counts. Also check Justice Hub's POCSO dataset for the child-victim side."
caveats: ["Child identity protection (JJ Act s.74) legally bars publishing anything identifying — aggregate only, and suppress small cells.", "JJB matters are largely absent from eCourts, so the court route silently drops juvenile offending."]
```

### 28. Vidhi Centre for Legal Policy — *Open Courts in the Digital Age: A Prescription for an Open Data Policy*

The reference document for why bulk judicial data is not available and what a policy would look
like. Observed at `https://vidhilegalpolicy.in/wp-content/uploads/2019/11/OpenCourts_digital16dec.pdf`.
Cite it in any access request. `tier: 4 · unit_of_record: narrative-document · access: open-download ·
priority: 2 · verification: CITED`

---

## Granularity reality check

| Level | What you actually get | Source | Period | Refresh |
|---|---|---|---|---|
| `address` / `point` (crime) | **nothing** | — | — | — |
| `police-station` (label + code) | case count, act/section, dates, outcome — *chargesheeted only* | eCourts FIR block + `fillPoliceStation` | ~2010– | daily |
| `point` (jail) | jail location & type; occupancy at state×type | e-Prisons NPIP; NCRB PSI | 1995– | realtime / annual |
| court establishment (taluka/district HQ) | pendency, disposal, case-type mix | NJDG; DDL `cases_court_key` | 2010– | daily / frozen 2018 |
| `district` | case counts by act & section & outcome | **DDL 2010–2018**; NJDG live | 2010– | one-off / daily |
| `state` | conviction rate, prisons, Lok Adalat, victim compensation | NCRB PSI, DoP, NALSA | 1995– | annual |
| `national` | everything | all | | |

**The blunt version.** We want a street. This domain's floor is a police station — and it hands you
that police station as an uppercase string and a numeric code, with no coordinates and no polygon.
The one level that is free, clean, bulk and instantly usable (DDL) is *district* and stops in 2018.
Everything below district is behind a CAPTCHA, one case at a time. There is no version of this
domain that produces a street-level map on its own; its honest role is the **outcome layer** —
"of the crimes recorded here, this many were charged, this many convicted, and it took this long" —
draped over a geography that must come from somewhere else.

---

## Blockers and how to get past them

| # | Blocker | Severity | Route past it |
|---|---|---|---|
| 1 | **Securimage CAPTCHA + `app_token` on every eCourts query** | critical | Do **not** build a CAPTCHA-defeating crawler as the primary strategy. Use it only at pilot scale (one district, one year) to prove the FIR join and to size the prize, then use that pilot as the evidence in a formal bulk-data request. |
| 2 | **No judicial open-data policy; no bulk export anywhere** | critical | Formal request to the **e-Committee, Supreme Court of India** and, in parallel, to the **Registrar (Computer Cell) of a specific High Court** — High Courts control their own district judiciary's data and one cooperative High Court is a complete pilot state. Cite NDSAP, RTI s.4, the Vidhi report, and DDL's existing release as precedent. |
| 3 | **Chargesheet filter — court data ≠ FIR data** | critical (analytical) | Unfixable; must be disclosed. Calibrate it: for districts where a state police portal *does* publish FIR counts, compute the court/FIR ratio per station per year. That ratio is itself a publishable finding and the correction factor everywhere else. |
| 4 | **No police-station boundaries** | high | Out of scope for this agent — depends on the geospatial agent. Interim: geocode the station name + district to a point, render as a labelled point or a Voronoi/Thiessen surface, and label it as approximate. Never shade a polygon you did not get from a boundary file. |
| 5 | **NJDG API is government-only** | medium | Snapshot the public dashboard daily and build our own time series; it is the only way to get history out of a snapshot-only system. Apply for the key via a Home Department / university partner. |
| 6 | **DDL is CC BY-NC-SA** | medium (legal) | If the map is non-commercial, use it and attribute. If any commercial element appears, licence separately from DDL — they state commercial use requires it. ShareAlike also means derived datasets must be released under the same terms. |
| 7 | **DDL stops at 2018 and is pre-BNS** | medium | Treat DDL as the historical baseline, our own scrape as the current layer, and build an IPC↔BNS section crosswalk as a first-class artefact. |
| 8 | **CIS coverage varies by establishment and year** | medium | Compute per-establishment first-record-date from the data itself and publish a coverage map. Never show a trend across a coverage discontinuity. |
| 9 | **This session's network blocked every `.gov.in`** | procedural | Re-run verification from an unblocked network / an India-resident vantage point. Several of these portals are also known to geo-throttle or rate-limit foreign IPs. |

### Terms-of-use and scraping legality — honest assessment

**eCourts.** I could not fetch the ToU page (egress blocked) and I will not paraphrase a document I
have not read. What I can state from primary artefacts: the data is served without login to any
member of the public; the portal deploys a CAPTCHA and a session token, which is an explicit
technical access control; and NIC has never published a machine-access policy. The legal exposure
is therefore not "reading public data" — it is *circumventing the CAPTCHA*, which in India runs at
IT Act ss.43 and 66 and at any contractual ToU. The most experienced open-source client in this
space (`openjustice-in/ecourts`, GPL-3.0) ships an explicit disclaimer that the operator "is
responsible for the legal implications", and enforces single-threaded, non-parallel access with
backoff — that is the community norm and we should not undercut it. **Recommendation: pilot small,
then ask.** Get the ToU read and a written opinion before any crawl above pilot scale.

**Indian Kanoon.** Clean and unambiguous: there is a documented paid API with published terms at
`api.indiankanoon.org/terms/`, token or public-key auth, per-call charging, and a
**"Powered by IKanoon"** attribution requirement for downstream rendering. Use the API. Scraping
the HTML site when a paid API exists is both legally weaker and ethically worse.

**DDL.** CC BY-NC-SA 4.0. Attribution + non-commercial + share-alike. Commercial use needs a
separate licence from Development Data Lab.

**Publishing risk beyond scraping.** Court records name accused persons. Republishing
name-level criminal case data on a public map is a defamation and privacy exposure of a completely
different order from publishing counts — and the Indian right-to-be-forgotten line of judgments
(several High Courts ordering judgment de-indexing for acquitted persons) cuts directly against it.
**Publish counts and outcomes. Never publish names, and never let a name-keyed record reach the
served tiles.** DDL anonymised for exactly this reason and we should inherit that decision.

---

## Seed Leads (unconfirmed but probably real)

1. **The `uniform_code` is probably the CCTNS/NCRB uniform police-station code.** If true, the
   eCourts police-station dropdown is a ready-made eCourts↔CCTNS↔state-police crosswalk, and it
   is the highest-leverage unverified claim in this dossier. *Next step:* pull one state's
   `fillPoliceStation` output and diff the codes against a known CCTNS police-station list (NCRB
   publishes station counts by district; some state portals expose station codes directly).

2. **High Court Registrar (Computer Cell) bulk-data requests.** Each High Court's Computer Cell
   administers its district judiciary's CIS database. *Next step:* letter to the Registrar
   (Computer Cell), High Court of Karnataka and High Court of Kerala — both have relatively open
   e-governance postures — requesting a de-identified extract of case master + FIR fields for the
   district judiciary, citing DDL's precedent and offering to publish only aggregates.

3. **e-Prisons "Courts Management" module holds the prisoner↔CNR link.** That would close the
   FIR → case → custody chain. *Next step:* RTI to NIC (e-Prisons project) and to two state DG
   (Prisons) asking for the module's data dictionary and whether CNR is stored.

4. **District-wise prosecution returns exist on paper in every state.** District Government
   Pleader / Public Prosecutor offices file monthly returns to the Directorate. *Next step:* RTI
   to the Directorate of Prosecution, Maharashtra and Tamil Nadu (both are relatively responsive),
   for district-wise cases instituted / decided / convicted / acquitted by year, 2015–2025, with
   the definition of the conviction-rate denominator stated.

5. **NALSA's LSAMS (`scourtapp.nic.in/lsams/`) is a national legal-services MIS.** If it holds
   DLSA-level victim-compensation records, that is district-level victim data for serious crime.
   *Next step:* RTI to NALSA for the LSAMS data dictionary and district-wise victim-compensation
   aggregates by offence category.

6. **An eCourts "Open Data"/bulk-download initiative may exist or be imminent.** The e-Committee
   has published data standards work and the DoJ text says public API extension is "proposed".
   *Next step:* check `ecommitteesci.gov.in` publications and the eCourts Phase III project
   documents (Phase III explicitly funds data standards and interoperability) for a data-sharing
   deliverable and its owner.

7. **Per-jail (not per-jail-type) tables in PSI annexures.** PSI's main tables are state×type, but
   some annexures list individual prisons. *Next step:* open PSI 2023 Chapter 1 annexures; if
   per-jail rows exist, that is a complete national jail gazetteer with capacity — a good map layer.

8. **State-level court data portals.** Some High Courts run their own case portals with looser
   controls than the national CIS (Delhi, Punjab & Haryana, Kerala historically). *Next step:*
   enumerate all 25 High Court websites and record which offer non-CAPTCHA'd case search or
   judgment bulk download.

9. **`ecourtsindia.com` / Apify commercial eCourts APIs.** Third-party paid wrappers around the
   scraping problem exist (`ecourtsindia.com/api`, several Apify actors). **These are not official**
   despite naming that implies it. *Next step:* price one against a pilot; buying a few thousand
   records to validate the FIR join may be cheaper and safer than building a solver.

---

## Phase 2 recommendations (ranked)

1. **Ingest DDL judicial data (2010–2018) immediately.** Free, bulk, clean, district × act ×
   section × disposition × dates, nine years, 81M cases. Zero blockers. It is the baseline against
   which every later claim is validated, and it lets us build and test the entire outcomes pipeline
   before touching a CAPTCHA. Prefer the Harvard Dataverse copy (`10.7910/DVN/GHLGSW`) for the
   criminal subset; Dropbox for the full release. Budget ~15 GB and a Stata→parquet conversion.

2. **Crawl the eCourts police-station master (`fillPoliceStation`) across all establishments.**
   This is a modest, bounded, one-time crawl of *reference data, not case data* — far lower risk
   than case scraping, and it produces a national police-station registry with codes that every
   other agent's work can join to. Do this before the geospatial agent finishes, so they have a
   canonical station list to geocode against.

3. **Run a single-district FIR-join pilot.** Pick one district in a state that publishes nothing.
   Enumerate FIR 1..N for 2–3 police stations for 2022–2023 via `submitFirNo`, at human pace,
   single-threaded. Measure: what fraction of FIRs resolve to a case; how often the FIR block is
   populated; whether the PS string matches the dropdown label; what the act/section distribution
   looks like. **This pilot decides whether the court route is a product feature or a footnote.**
   Do not scale it until the legal opinion is in.

4. **Snapshot NJDG daily.** A cron job against the district dashboard, stored as dated rows. Cheap,
   and it is the only way to ever have a judicial time series, because NJDG itself keeps none.

5. **Build the IPC↔BNS section crosswalk** as a shared artefact. Every source in this project
   fractures on 2024-07-01 and this fixes all of them at once. DDL's `section_key.dta` and
   `act_key.dta` give the IPC-side vocabulary for free.

6. **Ingest NCRB PSI jail tables + build the jail gazetteer** from PSI annexures and state prison
   department directories. Prisons are a legitimate, uncontroversial, geocodable map layer with
   zero defamation risk — good early visible output while the hard stuff is negotiated.

7. **Open the access conversation in parallel with all of the above**: letters to two High Court
   Registrars (Computer Cell), an RTI to NALSA for LSAMS, and RTIs to two Directorates of
   Prosecution. These have multi-month turnarounds, so start them in week one.

8. **Defer**: Indian Kanoon API (buy only when a specific text-analysis need appears), Supreme
   Court judgments, Model Prison Manual, Lok Adalat series. Low granularity, low freshness, or low
   relevance to "is this neighbourhood safe".
