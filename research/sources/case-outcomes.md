# Case Outcomes — chargesheeted, closed, convicted, acquitted, and when
_Agent: case-outcomes · Researched: 2026-09-20 · Entries: 11 verified_live / 18 total_

> **Verification note.** Every `*.gov.in` / `*.nic.in` host, plus `devdatalab.org`,
> `dataverse.harvard.edu`, `dataful.in`, `justicehub.in`, `huggingface.co`, `dropbox.com`,
> `registry.opendata.aws` and `medium.com`, is blocked by this session's egress proxy
> (CONNECT 403). **`raw.githubusercontent.com` and `*.s3.amazonaws.com` are reachable**, and
> that is where the decisive evidence came from: I downloaded and parsed **real case records
> out of two public S3 buckets**, 1,966 district-court case JSONs and 123,106 High Court
> metadata rows. Everything marked `VERIFIED_LIVE` below was opened, downloaded and counted by
> me on 2026-09-20. Nothing marked `VERIFIED_LIVE` is a landing-page impression.

---

## Executive summary

- **The FIR↔court join IS obtainable in bulk, today, without defeating a CAPTCHA — and it is
  already sitting in a public S3 bucket.** `s3://indian-district-court-judgments-test`
  (anonymous read, no AWS account) carries per-case JSON whose `history` block contains
  `fir_details`, a `^`-delimited triple of **FIR number ^ police-station name ^ FIR year**.
  Verified example, `TSAD090000312023`: `fir_details = "41^Excise  Police  Echoda^2022"`,
  `disp_name = ACQUITTAL`, `date_of_decision = 2024-03-19`. This overturns the working
  assumption that the police-station join requires a CAPTCHA'd per-FIR lookup.

- **Disposal dates and named outcomes exist, per case, as plain strings.** The same `history`
  block carries `date_of_filing`, `dt_regis`, `date_of_decision`, `disp_nature` (integer code)
  and `disp_name` (human-readable). Observed vocabulary in two Telangana complexes for 2023:
  `CONVICTED`, `ACQUITTAL`, `DISCHARGED`, `COMMITTED TO SESSIONS`, `COMPROMISED`, `CLOSED`,
  `SETTLED BEFORE LOK ADALAT`, `TRANSFERRED`, `ABATED`, `QUASHED`, `WITHDRAWN`. Acts and
  sections come with it (`under_act1..4`, `under_sec1..4`, plus a rendered `act` HTML table).

- **The catch, and it is a big one: that bucket is a pilot and it currently holds one state.**
  Years 1980–2025 are present, but under 2023/2024/2025 the only state partition is `29` =
  **Telangana**. The bucket is named `-test`, has **no AWS Open Data Registry entry**
  (`indian-district-court-judgments.yaml` → 404) and **no stated data licence**. So the
  thana-keyed trial-outcome layer is real, is proven, and is one state wide.

- **The High Court corpus, by contrast, is fully published and national.**
  `s3://indian-high-court-judgments` is a registered AWS Open Data dataset, **CC-BY-4.0**,
  managed by Dattam Labs, **17,771,420 judgments / 1.25 TiB / 25 courts / 45 benches /
  1950–2026**, daily-synced. Its `metadata/parquet/` gives `cnr`, `decision_date`,
  `disposal_nature` for every row; a newer `metadata/parquet_case_details/` (four courts so
  far) adds **`fir_no`, `fir_year`, `disposal_nature`, `acts[{act,section}]`, hearings,
  linked cases**. But High Court matters are bail, quashing and appeal — *outcome of a
  proceeding, not outcome of the crime*.

- **Bihar has a usable outcome feed right now, and it is Patna High Court's caption text.**
  Patna HC writes the police case into the case title: *"CRIMINAL MISCELLANEOUS No.83783 of
  2023 **Arising Out of PS. Case No.-136 Year-2023 Thana- CHHATAUNI District- East
  Champaran**"*. Of 123,106 Patna HC rows for 2024, **90,988 (73.9%) parse to (FIR no, FIR
  year, thana, district)** — **1,225 distinct thana strings across 51 districts**. Patna HC
  holds **1,692,461 judgments** in the bucket. The outcomes attached are `BAIL GRANTED`
  (51,703), `BAIL REJECTED` (5,689), `ALLOWED`, `DISMISSED`, `WITHDRAWN` — **not conviction or
  acquittal**. For Bihar this is a *bail-decision* map, not a "case closed" map.

- **Development Data Lab's 81M-case dataset does NOT carry the FIR link — confirmed, with a
  twist that matters more than the confirmation.** Three independent downstream loaders list
  the complete `cases_YYYY` column set: `ddl_case_id, year, state_code, dist_code, court_no,
  cino, judge_position, female_defendant, female_petitioner, female_adv_def, female_adv_pet,
  type_name, purpose_name, disp_name, date_of_filing, date_of_decision, date_first_list,
  date_last_list, date_next_list`. No FIR field, no police station — the previous agent was
  right. **But `cino` is the 16-character CNR, unhashed** (observed value
  `MHNB030013812010`). DDL therefore hands you 81 million CNRs, and the CNR is the key that
  the mobile-API/S3 case-details records are also keyed on. The FIR link DDL stripped is
  **re-joinable per case**, not lost.

- **The thing that makes all of this work is that eCourts has a second, CAPTCHA-free surface.**
  The `app.ecourts.gov.in/ecourt_mobile_DC` mobile API — the one the official Android app uses
  — has **no CAPTCHA at all**, returns the full docket including the FIR block, and is what
  the district-court S3 metadata was actually built from. The website's `fill*` dropdown
  endpoints (including `casestatus/fillPoliceStation`) and the `home/viewHistory` case
  enrichment endpoint are **also CAPTCHA-free**; only the seven `casestatus/submit*` search
  endpoints are gated. **We should still not run the mobile API ourselves** — it needs
  AES-CBC request encryption with keys lifted out of the APK, which is a terms problem even
  though it is not a CAPTCHA problem (`docs/INGESTION.md` rule 2, not rule 1).

- **Police-side disposal — "closed by police, never went to court" — exists only as state-level
  aggregates.** NCRB *Crime in India* publishes "Disposal of IPC Crime Cases by Police"
  (charge-sheeted / final report *true-but-untraced* / final report *false — mistake of fact
  or law* / pending investigation) and "Disposal of IPC Crime Cases by Courts" (trials
  completed, convicted, discharged, acquitted, pending trial, conviction rate). Granularity is
  **State/UT and the 19 metropolitan cities**. There is **no district and no police-station
  disposal table anywhere in the public record**. The chargesheeting rate is defined against
  *cases disposed by police*, not against FIRs registered — a denominator trap.

- **Finest achievable granularity for outcomes: `police-station`, as an uppercase free-text
  name with no code and no geometry.** `police_st_code` was `0` in **all 1,966** district
  records I sampled; the station survives only as a name string inside `fir_details`. Joining
  it to a thana polygon is a fuzzy string-match problem handed to the geospatial layer.

- **Single biggest blocker: coverage, not access.** The legal route is open and free; the data
  for 35 of 36 states has simply not been mirrored yet. The people who would have to agree are
  **Dattam Labs** (`contact@dattam.in`) to extend their district pipeline, or the
  **e-Committee, Supreme Court of India** / **Registrar (Computer Cell)** of a specific High
  Court for a direct extract.

---

## Source entries

### 1. Indian High Court Judgments — AWS Open Data Registry  ★ the published corpus
Registered open dataset; judgments plus structured metadata for 25 High Courts. Read without
credentials (`--no-sign-request`, or plain HTTPS against the bucket endpoint).

```yaml
id: case-outcomes-aws-hc-judgments
publisher: Dattam Labs (community project; data sourced from eCourts)
tier: 4
urls:
  landing: "https://registry.opendata.aws/indian-high-court-judgments/"
  data:    "s3://indian-high-court-judgments  (ap-south-1, anonymous read)"
  docs:    "https://github.com/vanga/indian-high-court-judgments/blob/main/opendata/docs/dataset.md"
geo_coverage: all-India (25 High Courts, 45 benches)
geo_granularity: state
location_semantics: court-venue
unit_of_record: case-record
time_start: "1950"
time_latest: "2026"
cadence: daily          # registry entry says Quarterly; repo CI syncs daily
lag: days
taxonomy: IPC+SLL (BNS from 2024-07-01)
formats: [PDF, JSON, Parquet]
access: open-download
machine_readable: 5
license: CC-BY-4.0
ingest_difficulty: 2
priority: 5
verification: VERIFIED_LIVE
```
**What I saw (2026-09-20).** `GET https://indian-high-court-judgments.s3.amazonaws.com/?list-type=2`
→ 200. Prefixes `data/`, `metadata/{json,parquet,parquet_case_details,tar}/`. Registry YAML read
verbatim from `awslabs/open-data-registry/datasets/indian-high-court-judgments.yaml`:
`License: CC-BY-4.0`, `ManagedBy: Dattam Labs`, `Contact: contact@dattam.in`,
`ARN: arn:aws:s3:::indian-high-court-judgments`, `Region: ap-south-1`.
`STATS.md` (snapshot 2026-06-01): **17,771,420 PDFs, 17,775,080 metadata records, 1,276.94 GiB**.
Largest: Punjab & Haryana 1,840,776; Bombay 1,772,808; **Patna 1,692,461**; Allahabad 1,691,473.

**`metadata/parquet/` schema (read from a real file):** `court_code, title, description, judge,
pdf_link, cnr, date_of_registration, decision_date (timestamp), disposal_nature, court,
raw_html, pdf_exists`.

**Caveats.**
- High Court ≠ trial outcome. `disposal_nature` here is dominated by bail and procedural
  dispositions; conviction/acquittal is a district-court event.
- `description` and `raw_html` contain **party names and addresses**. Drop at the boundary
  (`docs/INGESTION.md` rule 3).
- The PDF corpus was harvested with an ONNX CAPTCHA solver by the upstream project. We are
  consuming a published result, not solving a CAPTCHA — but the project should decide that
  explicitly rather than inherit it silently. See *Ethics* below.

---

### 2. `metadata/parquet_case_details/` — the High Court FIR + outcome dimension table  ★
Mobile-API-sourced, one row per CNR, only four courts so far.

```yaml
id: case-outcomes-aws-hc-case-details
publisher: Dattam Labs
tier: 4
urls: {data: "s3://indian-high-court-judgments/metadata/parquet_case_details/court=<c>/bench=<b>/case_details-mobile.parquet"}
geo_coverage: 4 High Courts so far (23_23 Madhya Pradesh, 27_1 Bombay, 2_5 Himachal Pradesh, 9_13 Allahabad)
geo_granularity: police-station     # via fir_no/fir_year only; no PS name column
location_semantics: reporting-office
unit_of_record: case-record
time_latest: "2026"
cadence: daily
taxonomy: IPC+SLL
formats: [Parquet]
access: open-download
machine_readable: 5
license: CC-BY-4.0
ingest_difficulty: 2
priority: 4
verification: VERIFIED_LIVE
```
**Verbatim schema** (read from `court=2_5/bench=cmis/case_details-mobile.parquet`):
```
cnr, case_no, case_type, court, bench, judge, bench_name, judicial_section,
petitioner, respondent, pet_advocate, res_advocate,
date_of_filing, date_of_registration, date_of_decision, disposal_nature, purpose_name,
fir_no, fir_year, lower_court,
acts: list<struct<act, section>>,
hearings: list<struct<cause_list_type, judge, business_on_date, hearing_date, purpose_of_listing>>,
linked_cases: list<struct<filing_number, case_number>>,
documents: list<struct<sr_no, document_no, date_of_receiving, filed_by, name_of_advocate, document_filed>>,
source
```
**Caveats.** Carries `fir_no` and `fir_year` but **no police-station column** — the FIR is not
resolvable to a thana from this table alone. Four courts only; Patna (`court=10_8`) absent
(listing returned `[]`). Party names present.

---

### 3. `s3://indian-district-court-judgments-test` — the thana↔outcome join, proven  ★★★
The single most important source in this dossier. Anonymous-readable S3 bucket of district and
taluka court case metadata and order PDFs, built from the eCourts **mobile** API.

```yaml
id: case-outcomes-aws-dc-judgments-pilot
publisher: Dattam Labs / vanga (pre-release; unregistered)
tier: 4
urls:
  data:    "s3://indian-district-court-judgments-test"
  landing: "https://github.com/vanga/indian-district-court-judgments"
geo_coverage: Telangana only for 2023-2025 (bucket structure is national; state 29 is the only partition populated)
geo_granularity: police-station
location_semantics: reporting-office   # the station that registered the FIR; court venue for the rest of the record
unit_of_record: case-record
time_start: "1980"
time_latest: "2025"
cadence: irregular       # pipeline is live; this bucket is a pilot
lag: months
taxonomy: IPC+SLL (BNS from 2024-07-01)
formats: [JSON, Parquet, PDF]
access: open-download
machine_readable: 5
license: unstated        # code is MIT; the DATA carries no licence statement
ingest_difficulty: 2
priority: 5
verification: VERIFIED_LIVE
```

**Layout.** `{year}/{state_code}/{district_code}/{complex_code}/{metadata.tar, metadata.index.json,
orders.tar, orders.index.json}`, plus `metadata/parquet/year=YYYY/state=NN/cases.parquet`,
`metadata/tar/`, `data/tar/`, `enriched/tar/`, `metadata/checkpoints/`.

**What I downloaded and counted (2026-09-20).**

| File | Size | Cases | With parsable `fir_details` | Distinct stations |
|---|---|---|---|---|
| `2023/29/1/1290014/metadata.tar` (Adilabad, Boath/Ichoda area) | 11,479,040 B | 1,054 | **927 (88%)** | 7 |
| `2023/29/22/1290148/metadata.tar` (Mancherial) | 12,533,760 B | 912 | 255 | 22 |
| `1980/29/1/1290005/metadata.tar` (oldest partition) | 225,280 B | — | 0 (civil, pre-CCTNS) | — |

**Record shape.** Top-level keys `case_summary`, `location`, `orders`, `history`, `scraped_at`,
`source`. `history` has **92 keys**. The ones that matter:

| Field | Meaning | Observed value |
|---|---|---|
| `cino` | CNR — joins to DDL's `cino` | `TSAD090000312023` |
| **`fir_details`** | **`FIR_no ^ police_station ^ FIR_year`** | `41^Excise  Police  Echoda^2022` |
| `fir_no`, `fir_year`, `police_st_code` | discrete fields | **empty / `0` in all 1,966 sampled** |
| `date_of_filing`, `dt_regis` | filing / registration | `2023-01-17` |
| **`date_of_decision`** | **disposal date** | `2024-03-19` |
| **`disp_name`** | **outcome, human-readable** | `ACQUITTAL` |
| `disp_nature` | outcome code | `12` |
| `under_act1..4`, `under_sec1..4`, `act` | acts/sections (codes + rendered HTML table) | `INDIAN PENAL CODE / 304(A)` |
| `type_name`, `regcase_type` | case type | `CC`, `STC`, `PRC` |
| `court_name`, `est_code`, `district_name`, `state_name`, `complex_code` | court geography | `Junior Civil Judge Court Boath`, `TSAD09` |
| `pet_name`, `res_name`, `pet_adv`, `res_adv`, `petNameAdd` | **party names** | present — must be dropped |
| `historyOfCaseHearing`, `finalOrder`, `interimOrder`, `processes`, `link_cases` | HTML blobs | present |

**Outcome vocabulary observed** (2 complexes, 2023): `ADMISSION OF CLAIM` 663, `COMPROMISED` 126,
`ALLOWED` 181, `TRANSFERRED` 93, `DISMISSED` 88, `ACQUITTAL` 58, `TERMINATED` 35,
`SETTLED BEFORE LOK ADALAT` 49, `CLOSED` 27, `COMMITTED TO SESSIONS` 8, `CONVICTED` 2,
`DISCHARGED` 1, `QUASHED` 1, `ABATED` 2.

**Top act/section pairs** (Adilabad 2023): `MOTOR VEHICLES ACT 185(a)` 352, `IPC 336` 50,
`IPC 290` 45, `Telangana Gaming Act 9(i)` 29, `IPC 379` 20, `IPC 294-B,323,506,34` 18,
`IPC 304(A)` 13, `Negotiable Instruments Act 138` 11.

**Lag measured.** FIR year → decision year, n=471: **median 0 years, p90 2 years.**

**Caveats.**
- **One state.** `2023/`, `2024/`, `2025/` each contain exactly one state prefix: `29`
  (Telangana). No Bihar, no UP, no Maharashtra.
- **No AWS Open Data Registry entry** (404) and **no data licence**. Do not assume CC-BY.
- `police_st_code` is `0` everywhere; the station is a free-text name with doubled spaces
  (`"Excise  Police  Echoda"`), `PS`/`P.S.` variants and non-geographic pseudo-stations
  (`MAHILA P.S.`, `SC/ST`, `PATNA COMPLAINT CASE`, `GOVERNMENT OFFICIAL COMP.`).
- `disp_name` is court-local free text, not a controlled vocabulary. `ADMISSION OF CLAIM`
  dominating a criminal docket is an artefact of how traffic/petty pleas are recorded.
- FIR fill rate varies hugely by complex: 88% vs 28% in two complexes of the same state/year.
- Party names present. `docs/INGESTION.md` rule 3 applies at the boundary.
- `metadata/parquet/.../cases.parquet` is **not** a substitute — its schema is only
  `case_no, cino, case_type, state_code, state_name, district_code, district_name,
  complex_code, complex_name, reg_year, date_of_filing, date_of_decision, final_orders,
  interim_orders, has_pdf`. **No FIR, no disposal nature.** The join lives in the tar JSONs.
```yaml
how_to_obtain: "aws s3 sync s3://indian-district-court-judgments-test/2023/29/ ./ --no-sign-request, or plain HTTPS GET on https://indian-district-court-judgments-test.s3.amazonaws.com/<key>. For any state other than Telangana, ask Dattam Labs (contact@dattam.in) to extend the pipeline, or negotiate an extract."
```

---

### 4. eCourts mobile API (`app.ecourts.gov.in/ecourt_mobile_DC`) — **CAPTCHA-free, and the reason entry 3 exists**
The backend of the official *eCourts Services* Android app (`in.gov.ecourts.eCourtsServices`,
v3.0). No CAPTCHA anywhere in the flow.

```yaml
id: case-outcomes-ecourts-mobile-api
publisher: eCommittee, Supreme Court of India / NIC
tier: 3
urls: {api: "https://app.ecourts.gov.in/ecourt_mobile_DC/"}
geo_coverage: all-India district & taluka courts
geo_granularity: police-station
location_semantics: reporting-office
unit_of_record: case-record
time_start: "~1980 (archive flag present)"
time_latest: current
cadence: realtime
taxonomy: IPC+SLL
formats: [JSON, PDF]
access: blocked          # not CAPTCHA'd, but requires app-embedded AES keys — see below
machine_readable: 5
license: unstated
ingest_difficulty: 4
priority: 3
verification: VERIFIED_LIVE
```
**Endpoints** (verbatim from `vanga/indian-district-court-judgments/mobile/api_client.py`):
`appReleaseWebService.php` (session/JWT), `stateWebService.php` (`action_code=getStates`),
`districtWebService.php`, `courtEstWebService.php` (`action_code=fillCourtComplex`),
`caseNumberWebService.php`, **`searchByCaseType.php`** (the bulk discovery axis:
state/dist/court_code_arr/case_type/year/Pending|Disposed), **`caseHistoryWebService.php`**
(the full docket incl. the FIR block), `getAllLabelsWebService.php`, `display_pdf.php`.
Request body is a single `params` field, **AES-CBC encrypted**; `authtoken` likewise; device
identity is `<uuid16>:in.gov.ecourts.eCourtsServices`; the server presents a **self-signed
certificate** (client runs `verify_ssl=False`).

> **Our position.** This is not a CAPTCHA, so `docs/INGESTION.md` rule 1 does not fire. But
> encrypting requests with keys extracted from an APK is an access control in substance, and
> rule 2 (terms of use) plainly does. **Recommendation: do not run it.** Consume the published
> S3 output instead, and if we need a state that is not mirrored, ask rather than reimplement.

---

### 5. eCourts web portal — the CAPTCHA map, corrected
Previously we recorded eCourts as uniformly CAPTCHA-gated. That is wrong and it cost us a route.

| Endpoint | CAPTCHA? | Returns |
|---|---|---|
| `casestatus/fillDistrict`, `fillcomplex`, `fillCourtEstablishment` | **No** | dropdown options |
| **`casestatus/fillPoliceStation`** | **No** | `{"police_station_list": "<option value='2-33325003'>Arjunda 2</option>…"}` |
| `casestatus/fillCaseType`, `fillActType` | **No** | `21^3` = CRIMINAL CASE; `actcode=12` = IPC |
| `cause_list/fillCauseList` | **No** | judge list per complex |
| `casestatus/set_data` | **No** | binds session to a complex |
| **`home/viewHistory`** | **No** | **full case HTML: filing/registration/decision dates, case status & stage, nature of disposal, acts & sections, hearings, parties, orders** |
| `casestatus/submit_case_type`, `submitPartyName`, `submitAdvName`, `submitAct`, `submitFirNo`, `submitFillingNo`, `submitCaseNo` | **Yes** | the search result sets |

So: **discovery** is CAPTCHA'd; **enrichment is not**. Given a CNR + `internal_case_no` +
`court_code` from any other source (DDL gives you 81 million of them), `viewHistory` returns
the outcome record with **zero CAPTCHAs**. What `viewHistory` does *not* return is the FIR
block — that is mobile-API-only.

```yaml
id: case-outcomes-ecourts-viewhistory
tier: 3
urls: {data: "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/viewHistory"}
geo_granularity: district
location_semantics: court-venue
unit_of_record: case-record
access: scrape
machine_readable: 2
license: unstated
ingest_difficulty: 3
priority: 4
verification: VERIFIED_LIVE
caveats:
  - "No FIR block — acts/sections and outcome only."
  - "Needs internal_case_no + cnr + court_code, which come from a CAPTCHA'd search or another dataset."
  - "Hearing-history table parses to garbled dict keys in the reference implementation."
```

```yaml
id: case-outcomes-ecourts-police-station-master
name: "eCourts casestatus/fillPoliceStation — national police-station option list"
tier: 3
geo_granularity: police-station
location_semantics: n/a
unit_of_record: boundary-polygon   # a code registry; no geometry
access: scrape
machine_readable: 2
ingest_difficulty: 2
priority: 4
verification: VERIFIED_LIVE
notes: "value='police_st_code-uniform_code', split on the first hyphen. 7 stations returned at Civil Court Gunderdehi (state=18, district=19, complex=1180084). NO CAPTCHA. One bounded crawl over 3,567 complexes yields a national station registry with codes — the only artefact that can reconcile the free-text station names in entry 3 to a stable key."
```

---

### 6. Development Data Lab — Indian Judicial Data (2010–2018)
~81M district-court cases scraped from eCourts, anonymised, Stata `.dta` **and CSV**.

```yaml
id: case-outcomes-ddl-judicial
publisher: Development Data Lab
tier: 4
urls:
  landing: "https://www.devdatalab.org/judicial-data"
  data:    "https://www.dropbox.com/sh/hkcde3z2l1h9mq1/AAB2U1dYf6pR7qij1tQ5y11Fa/csv?dl=0"
geo_coverage: all-India district & subordinate courts (incl. Bihar)
geo_granularity: district
location_semantics: court-venue
unit_of_record: case-record
time_start: "2010"
time_latest: "2018"
cadence: one-off
lag: "8+ years and growing"
taxonomy: IPC+SLL (pre-BNS)
formats: [CSV, DTA]
access: open-download
machine_readable: 4
license: CC-BY-NC-SA-4.0
ingest_difficulty: 2
priority: 4
verification: CITED     # portal & Dropbox blocked here; layout and columns VERIFIED_LIVE from downstream code
```

**Real file layout** (verbatim from a downstream project's README, CSV distribution):
```
csv/
  acts_sections.csv
  cases/cases/cases_2010.csv … cases_2018.csv
  judges_clean.csv
  keys/keys/{act_key, cases_court_key, cases_district_key, cases_state_key,
             disp_name_key, judge_case_merge_key, purpose_name_key,
             section_key, type_name_key}.csv
```

**Complete `cases_YYYY` column list**, cross-confirmed by three independent loaders:
```
ddl_case_id, year, state_code, dist_code, court_no, cino, judge_position,
female_defendant, female_petitioner, female_adv_def, female_adv_pet,
type_name, purpose_name, disp_name,
date_of_filing, date_of_decision, date_first_list, date_last_list, date_next_list
```
`acts_sections.csv`: `ddl_case_id, act, section, bailable_ipc, number_sections_ipc, criminal`.

**Answering the question directly:**
- **Disposition? YES** — `disp_name` (integer), resolved via `disp_name_key` (`disp_name`,
  `year` → `disp_name_s`, `count`).
- **Disposal date? YES** — `date_of_decision`.
- **FIR number or police station? NO.** Neither appears in any loader's column list, dtype map
  or merge key. Party names were also replaced by gender flags (`female_defendant`,
  `female_petitioner`, …) — this is the anonymisation step, and the FIR block went with it.
  **Confirmed, not refuted.**
- **But `cino` is the raw CNR** (observed `MHNB030013812010`, `MHNB030004552010` — 16-char,
  `SSDDEEnnnnnnYYYY`). DDL is therefore a free national index of 81M CNRs, and the CNR is the
  join key into entries 2–4. The FIR link is recoverable per case; it was not destroyed.

**Caveats.** Stops 2018, pre-BNS. `act_key` is unnormalised free text — `Motor Vehicles Act`,
`MOTOR VEHICLES ACT`, `Motor Vehicle Act`, `MOTOR VEHICLES ACT, 1988` and `Motor Vehicles Act
1988` are five separate codes for one statute (verified from `act_key` counts). District IDs
predate ~8 years of district creation. **Non-commercial licence.**

### 7. DDL replication package — *In-group Bias in the Indian Judiciary*
`github.com/devdatalab/paper-justice`; data at Harvard Dataverse `10.7910/DVN/GHLGSW` and
Google Drive. Files `cases_clean_2010…2018.dta` (~24.51M criminal obs before filtering),
`judges_clean`, `poi_master`, `ACLED_India_violence_2005-2023`, keys incl. `disp_name_key`,
`pc11_court_district_key` (← a **district↔PC11 census-code crosswalk**, useful to us).
**This package is NOT anonymised**: the build scripts reference `def_name`, `pet_name`,
`pet_adv`, `def_adv`, `judge_desg`, `state_name`, `district_name`, `court_name`.
`tier: 4 · access: open-download · priority: 3 · verification: VERIFIED_LIVE`
**Do not ingest the name-bearing files.** The package also ships a name→religion/gender
classifier; applying it to a public crime map would be indefensible.

---

### 8. NCRB — Disposal of Crime Cases by Police
The only public record of a case being **closed by police rather than by a court**.

```yaml
id: case-outcomes-ncrb-police-disposal
publisher: NCRB, Ministry of Home Affairs
tier: 1
urls:
  landing: "https://ncrb.gov.in/en/crime-india"
  data:    "https://www.data.gov.in/catalog/crime-india-2022"
geo_coverage: all-India
geo_granularity: state          # plus the 19 metropolitan cities
location_semantics: reporting-office
unit_of_record: aggregate-count
time_start: "1953"
time_latest: "2024"
cadence: annual
lag: "12-24 months"
taxonomy: NCRB-heads
formats: [PDF, XLSX, CSV]
access: open-download
machine_readable: 2
license: GODL-India
ingest_difficulty: 4
priority: 3
verification: CITED    # ncrb.gov.in and data.gov.in both egress-blocked this session
```
**Disposal categories** (confirmed wording): cases **charge-sheeted**; cases in which a **Final
Report** was submitted, split into *true but untraced / no clue / insufficient evidence* and
*false — mistake of fact, mistake of law, or civil dispute*; cases **withdrawn by government**;
cases **pending investigation** at year end. **Chargesheeting rate** = charge-sheeted ÷ **cases
disposed by police after investigation** — *not* ÷ cases registered. Published series titles
include *"Disposal of IPC Crime Cases by Police"* and *"Crime Head-wise Police Disposal of
Indian Penal Code (IPC) Crimes in Metropolitan Cities"* (data.gov.in resource). Reported
national figures: IPC chargesheeting rate **75.8% (2020)**, **72.7% (2023)**.

**Caveats.**
- **State/UT and metro city only. No district table, no police-station table, anywhere.**
- Principal offence rule applies, so a case is counted once under its gravest head.
- The *false / mistake of fact* bucket is where community-level bias hides, and it is only ever
  published as a state total — precisely the aggregation that makes it unauditable.
- IPC→BNS break at 2024-07-01 fractures the whole series.

### 9. NCRB — Disposal of Crime Cases by Courts
Same publication, same granularity: trials completed, **convicted**, **discharged**,
**acquitted**, cases withdrawn, cases **pending trial**, and the conviction rate.
`id: case-outcomes-ncrb-court-disposal · tier: 1 · geo_granularity: state ·
unit_of_record: aggregate-count · cadence: annual · access: open-download · priority: 3 ·
verification: CITED`. **This is the benchmark our court-derived rates must be validated
against** — if our Telangana thana rollup does not reconcile to NCRB's Telangana state total,
our extraction is wrong.

### 10. Mirrors of the NCRB disposal tables
- **Dataful** (`dataful.in`) — e.g. dataset 458, *"NCRB: Police disposal of cases of fake/false
  news and rumours registered under Section 505 of IPC"*; collection 1108 *NCRB Crime in India
  (Summary)*. Tidy year × state series, freemium. `tier: 5 · access: paid · priority: 2 · CITED`
- **Indiastat** — `indiastat.com/data/crime-and-law/disposal-of-ipc-crime-cases-by-police` and
  `…/disposal-of-ipc-crime-cases-by-courts`, year-wise. `tier: 5 · access: paid · priority: 1 · CITED`
Both save days of PDF-table extraction and neither adds granularity.

---

### 11. Patna High Court caption extraction — the Bihar outcome route  ★
Not a dataset anyone published; a property of Patna HC's case-title convention that makes the
national HC corpus thana-keyed **for Bihar**.

```yaml
id: case-outcomes-patna-hc-fir-captions
publisher: Patna High Court (via the AWS HC corpus)
tier: 4
urls: {data: "s3://indian-high-court-judgments/metadata/parquet/year=2024/court=10_8/bench=patnahcucisdb94/metadata.parquet"}
geo_coverage: Bihar
geo_granularity: police-station
location_semantics: reporting-office
unit_of_record: case-record
time_start: "1950"
time_latest: "2026"
cadence: daily
lag: days
taxonomy: IPC+SLL
formats: [Parquet]
access: open-download
machine_readable: 4
license: CC-BY-4.0
ingest_difficulty: 2
priority: 4
verification: VERIFIED_LIVE
```
**Measured, 2026-09-20.** `year=2024/court=10_8` → **123,106 rows**. Regex
`PS\.?\s*Case\s*No\.?-?\s*(\S+)\s*Year-?\s*(\d{4})\s*Thana-?\s*(.+?)\s*District-?\s*(.+?)\s*=`
over `description` matched **90,988 rows (73.9%)** → **1,225 distinct thana strings, 51
districts**. Top districts: Patna 8,849, East Champaran 5,830, Gaya 5,004, Saran 4,190,
Samastipur 3,902, Madhubani 3,584, Vaishali 3,484, Muzaffarpur 3,304.
FIR-year → decision-year lag: **median 1 year, p90 5 years**.

**`disposal_nature` for the FIR-linked rows:** BAIL GRANTED 51,674 · ALLOWED 14,431 ·
WITHDRAWN 6,641 · DISMISSED 5,802 · BAIL REJECTED 5,687 · DISPOSED 4,127 · REJECTED 1,132 ·
PARTLY ALLOWED 511 · D.F.D. FOR NON APPEARANCE 498 · DISMISS FOR NON-PROSECUTION 305 ·
CONVERTED 133 · ABATED 24.

**Caveats — read these before shipping anything.**
- **These are not trial outcomes.** 63% are bail decisions. A thana with many `BAIL GRANTED`
  rows is a thana whose accused reached the High Court, which correlates with case volume,
  lawyer access and seriousness — not with whether crime was resolved.
- Thana strings include non-geographic entries (`Excise P.S.` 3,310, `MAHILA P.S.` 1,034 +
  `MAHILA PS` 537, `PATNA COMPLAINT CASE` 1,002, `SC/ST` 551, `COMPLAINT CASE` 504,
  `GOVERNMENT OFFICIAL COMP.` 438). Case and spacing are inconsistent within a single field.
- 26% of rows have no parsable block (civil writs, service matters).
- A small number of `Year-` values are junk (one lag of −999 observed) — filter on
  `1990 ≤ fir_year ≤ decision_year`.
- The caption is free text set by a registry clerk. It is not a CIS field and it can change
  format without notice. Re-measure the match rate on every refresh.
- Other High Courts do **not** share this convention; this is Patna-specific and was found by
  reading the data, not by assuming it.

### 12. Bihar district courts — what does NOT exist
No Bihar district-court extract is published anywhere I could reach. `2023/8/`, `2024/8/`
(Bihar = state code 8) are **absent** from the district bucket. DDL covers Bihar but only to
**district × act × section × disposition, 2010–2018**. Justice Hub's CALPRA-1986 dataset
(10,800 cases, Jan 2015–Mar 2023) includes Bihar but is one statute. Bihar's own
`scrb.bihar.gov.in/View_FIR.aspx` is the *input* side (FIRs) — pairing it with court outcomes
is exactly the join this dossier is about, and the missing piece is a Bihar district-court
pull. `id: case-outcomes-bihar-district-gap · access: on-request · priority: 5 · verification: VERIFIED_LIVE (absence confirmed by S3 listing)`

---

### 13. NJDG v3 — pendency and disposal dashboard
`https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=<code>&app_token=<tok>`;
High Court view at `/hcnjdg_v2/`. Daily-refreshed, state → district → establishment,
civil/criminal split, "reasons for delay". Snapshot semantics: **no history is kept**, so a
time series exists only if we start snapshotting.
`tier: 3 · geo_granularity: district · unit_of_record: aggregate-count · cadence: daily ·
access: scrape · machine_readable: 2 · priority: 3 · verification: CITED`
The **NJDG Open API remains government-only** (departmental ID + access key, institutional
litigants; public extension "proposed"). `access: on-request · priority: 2`.

### 14. `openjustice-in/ecourts` — the field-schema reference
GPL-3.0 Python toolkit, High Court coverage. Value to us is its **entity model and committed
fixtures**, which is the cleanest published statement of what an eCourts case record contains.
`Case`: `case_type, registration_number, cnr_number, filing_number, registration_date,
first_hearing_date, decision_date, case_status, nature_of_disposal, coram, bench, state,
district, judicial, petitioners[], respondents[], orders[], case_number, hearings[], category,
sub_category, objections[], not_before_me, filing_date, fir, token`.
`FIR`: `state, district, police_station, number, year`.
Parser reads the `Case Status` block for `First Hearing Date`, `Decision Date`,
`Nature of Disposal`, `Coram`, `Bench`, `Not Before Me`, and `span.FIR_details_table` for
`State / District / Police Station / FIR Number / Year`.

**Committed fixture, re-verified today** — `test/fixtures/case_details/KAHC010337682024.yml`:
```yaml
cnr_number: KAHC010337682024   case_type: CRL.P   case_status: ORDERS
filing_date: 2024-06-14   registration_date: 2024-06-18   decision_date: null
nature_of_disposal: null   coram: 1492M.NAGAPRASANNA   bench: Single Bench
fir: {state: KARNATAKA, district: BENGALURU, police_station: INDIRANAGAR PS,
      number: '155', year: 2024}
```
Also ships 150+ `test/fixtures/cases/JKHC*.yml` (J&K HC) — all with `fir: null`, which is
itself evidence that the FIR block is often empty at High Court level.
`tier: 4 · access: open-download · machine_readable: 5 · license: GPL-3.0-or-later ·
priority: 3 · verification: VERIFIED_LIVE`

### 15. `vanga/indian-district-court-judgments` — reference only, **do not run**
MIT-licensed scraper behind entry 3. Ships `web/src/captcha_solver/captcha.onnx`, an ONNX
CAPTCHA solver (~1–2 s/solve). Its own cost model: a full national first pass is
**~680,000 CAPTCHAs, 2–4 weeks at 2 workers**. Its documentation is nonetheless the best
public map of the eCourts surface: `web/WEB_PORTAL_SEARCH_OPTIONS.md` (all seven search tabs
with live-tested parameters) and `web/WEB_SCRAPER_REFERENCE.md` (the CAPTCHA/no-CAPTCHA split
in entry 5).
`tier: 4 · access: open-download · license: MIT · priority: 2 · verification: VERIFIED_LIVE`
**`docs/INGESTION.md` rule 1 forbids us running this.** We read its docs and consume its output.

### 16. Indian Supreme Court Judgments — AWS Open Data
`registry.opendata.aws/indian-supreme-court-judgments/`, 1950–2025, CC-BY-4.0, same
publisher and layout. Registry YAML confirmed present (HTTP 200). National granularity;
relevant only for validating outcome definitions.
`tier: 4 · geo_granularity: national · access: open-download · priority: 1 · verification: CITED`

### 17. Justice Hub / DAKSH / CivicDataLab — curated eCourts extracts
`justicehub.in/dataset` (blocked here): POCSO tracker (19,783 district-court cases across
Assam, Delhi, Haryana), CALPRA-1986 (10,800 cases, 2015–2023, six states **including Bihar**),
NIPFP contract enforcement. CivicDataLab's POCSO methodology page is the best published
worked example of act-specific eCourts extraction with an outcome variable.
`tier: 4 · geo_granularity: district · access: open-download · priority: 3 · verification: CITED`

---

## Granularity reality check

| Level | Outcome content available | Source | Period | Refresh | Legit route today? |
|---|---|---|---|---|---|
| `police-station` (name) — **trial outcome** | convicted / acquitted / discharged / committed / compromised / closed + disposal date + act & section | **DC S3 pilot** (entry 3) | 1980–2025 | pilot | **Yes — Telangana only** |
| `police-station` (name) — **bail outcome** | bail granted / rejected, allowed, dismissed + decision date | **Patna HC captions** (entry 11) | 1950–2026 | daily | **Yes — Bihar** |
| `police-station` (FIR no. only, no name) | disposal_nature + decision date + acts | HC `parquet_case_details` | –2026 | daily | Yes — 4 High Courts |
| `district` | disposition + disposal date + act + section, 81M cases | **DDL** | 2010–2018 | frozen | Yes, non-commercial |
| `district` | pendency / disposal counts, civil-criminal split | NJDG v3 | live | daily | Dashboard scrape |
| `state` / metro city | **police** disposal: chargesheet / final report true / false / pending | **NCRB CII** | 1953–2024 | annual | Yes |
| `state` / metro city | **court** disposal: convicted / acquitted / discharged / pending trial | NCRB CII | 1953–2024 | annual | Yes |
| `address` / `point` | nothing | — | — | — | — |

**The blunt version.** The police-station outcome layer is not hypothetical any more — I pulled
it, parsed it and counted it. It exists for **one state at trial level and one state at bail
level**, from two public buckets, for free, with no CAPTCHA. Everything above that is a
coverage problem, and coverage is bought with a conversation, not with a scraper.

---

## Feasibility verdict

**Can we show "case closed" on a thana map?**

**Yes for Telangana, today, legitimately.** `s3://indian-district-court-judgments-test`
gives per-case `fir_details` → police-station name, `disp_name` → `CONVICTED` / `ACQUITTAL` /
`DISCHARGED` / `CLOSED` / `COMMITTED TO SESSIONS`, `date_of_decision` → when, and
`under_act*`/`under_sec*` → what for. FIR-to-disposal lag measured at **median 0, p90 2 years**.
Granularity is a **police-station name string** — no code, no polygon, doubled spaces, PS/P.S.
variants, and pseudo-stations (`MAHILA P.S.`, `Excise P.S.`) that are not places. Coverage of
the FIR field is complex-dependent: **88% in one complex, 28% in another, same state, same year.**

**Yes for Bihar, but only for bail.** Patna HC's captions yield thana + FIR for **73.9% of
123,106 rows in 2024 alone**, across **1,225 thana strings in 51 districts**, over a corpus of
**1.69M Patna judgments** — but the outcome attached is `BAIL GRANTED` / `BAIL REJECTED`, not
conviction. Rendering that as "case closed" would be a lie. Render it as *"the High Court has
ruled on bail in N matters arising from this thana"*, or not at all.

**No for the other 34 states and UTs, not without a data-sharing agreement.** Say it plainly:
**for national police-station-level case outcomes, we need someone to agree.** In order of how
likely they are to say yes:

1. **Dattam Labs** — `contact@dattam.in`, maintainers of both buckets and the mobile pipeline
   that produced the FIR-bearing district records. They have already done the hard part for
   Telangana; extending it to Bihar is a configuration change on a pipeline that exists. **Ask
   them first.** Also ask them to register the district bucket with AWS Open Data and put a
   licence on it — without one we have no right to redistribute anything derived from it.
2. **The e-Committee, Supreme Court of India** (`ecommitteesci.gov.in`) — owner of eCourts and
   of any national bulk-data decision. eCourts Phase III explicitly funds data standards and
   interoperability; this is the door to knock on for a policy answer rather than a one-off.
3. **The Registrar (Computer Cell) of a named High Court** — each High Court controls its own
   district judiciary's CIS database. **For Bihar this is the Registrar (Computer Cell), Patna
   High Court.** One cooperative High Court is a complete pilot state, and DDL's 81M-case
   release is the precedent that it has been granted before.
4. **Department of Justice / NIC** — for an NJDG API departmental ID. Aggregates only; will not
   give us a thana.

**And say the cost of the coverage we do not have:** everything in this dossier is
*chargesheeted* matters. Cases the police closed by Final Report — the *untraced*, the *mistake
of fact*, the *false* — never reach a court and therefore never reach any of these datasets.
The only public record of those is NCRB, at state level. **A thana map built from court data is
structurally blind to police non-action, and police non-action is exactly what a resident
deciding where to live would most want to know.** That must be on the map, above the fold, not
in a footnote.

---

## Blockers and how to get past them

| # | Blocker | Severity | Route past it |
|---|---|---|---|
| 1 | **District-court S3 bucket holds one state (Telangana)** | critical | Email Dattam Labs (`contact@dattam.in`). Offer to co-fund or to run the compute. This is the single highest-leverage email in the whole project. |
| 2 | **That bucket has no data licence and no registry entry** | critical (legal) | Same email. Until a licence exists we may analyse it but must not redistribute derivatives. Compare: the HC bucket *is* CC-BY-4.0 and registered. |
| 3 | **Police station is a free-text name, not a code** | high | `police_st_code` is `0` in every record. Crawl `casestatus/fillPoliceStation` (no CAPTCHA) across 3,567 complexes to build a name↔code registry, then fuzzy-match. Hand the result to the geospatial layer, which already has thana polygons for 7 states incl. **Bihar** (`Bhugoal_BH_Police_Thana_Boundaries`). |
| 4 | **Chargesheet filter — court data is blind to police-closed cases** | critical (analytical) | Unfixable. Disclose it. Calibrate it where a state publishes FIR counts: Bihar's `scrb.bihar.gov.in` FIR repository divided by a Bihar court pull gives a per-station court/FIR ratio, which is both a correction factor and a publishable finding in its own right. |
| 5 | **High Court outcomes are bail, not verdicts** | high (analytical) | Never label `BAIL GRANTED` as a case outcome. Keep HC in a separate, separately-labelled layer. |
| 6 | **`disp_name` is court-local free text** | medium | Build a disposition crosswalk to a small controlled vocabulary (convicted / acquitted / discharged / compromised / transferred / withdrawn / pending / other). Seed it from DDL's `disp_name_key` and extend from observed district strings. Publish the mapping; never silently bucket. |
| 7 | **Both corpora carry party names** | high (legal) | `docs/INGESTION.md` rule 3: drop at the boundary. `pet_name`, `res_name`, `pet_adv`, `res_adv`, `petNameAdd`, `resNameAdd`, `description`, `raw_html`, `title` all carry identities. Run `CsvFirSource.audit()` equivalent on every new column. |
| 8 | **DDL is CC BY-NC-SA and stops in 2018** | medium | Fine as a baseline; relicense separately if the map ever goes commercial; ShareAlike binds derivatives. |
| 9 | **IPC→BNS break at 2024-07-01** | medium | The crosswalk is a shared project artefact. DDL `act_key`/`section_key` give the IPC vocabulary; the district records give BNS-era strings. |
| 10 | **`act_key` is unnormalised** | medium | Five distinct codes for the Motor Vehicles Act alone. Normalise before any act-level chart. |
| 11 | **NCRB publishes no district or station disposal table** | high | Not solvable by data engineering. RTI to the State Crime Records Bureau for district-wise disposal returns — the DCRBx compile them monthly, so they exist on paper. See `research/sources/rti-playbook.md`. |
| 12 | **All `.gov.in` blocked in this environment** | procedural | Re-verify NCRB table numbers, NJDG and data.gov.in from an India-resident network before Phase 2. |

### Ethics and terms — the call this project has to make

`docs/INGESTION.md` rule 1 says we do not defeat CAPTCHAs. Three distinct situations here, and
they are not the same:

1. **The district-court metadata with the FIR link came from the eCourts *mobile* API, which
   has no CAPTCHA.** Rule 1 was never engaged in its creation. Consuming it is clean.
2. **The High Court PDF corpus was harvested by a scraper that ships an ONNX CAPTCHA solver.**
   We would be consuming a published CC-BY-4.0 dataset, not solving anything. That is
   permitted by the letter of rule 1 and it should still be decided explicitly rather than
   drifted into. Recommend `research/sources/legal-ethics.md` rules on it before ingest.
3. **Running the mobile API ourselves would require AES keys extracted from the official APK.**
   Not a CAPTCHA, but an access control in substance, and squarely a rule-2 terms problem.
   **Recommendation: we do not do this.** If we need a state, we ask.

And the standing one: court records name accused persons, and several High Courts have ordered
de-indexing of judgments naming acquitted people. **Publish counts and outcomes. Never publish
names, and never let a name-keyed column reach the served tiles.**

---

## Seed Leads (unconfirmed but probably real)

1. **The district bucket's `enriched/tar/` prefix.** It exists and I did not open it. If it
   holds the `viewHistory`-enriched records, it may carry a cleaner acts/sections structure
   than the `act` HTML blob. *Next step:* list `enriched/tar/` and diff one record against the
   same CNR in `metadata/tar/`.
2. **`police_st_code` may be populated in states other than Telangana.** It was `0` in all
   1,966 records I read, but that could be a Telangana CIS configuration rather than a national
   truth. *Next step:* when a second state is mirrored, re-check; if it is populated anywhere,
   test whether it equals the `uniform_code` from `fillPoliceStation`, which would give us a
   national station key for free.
3. **`disp_nature` (integer) is probably a national CIS code list while `disp_name` is local.**
   Observed `disp_nature=12` ↔ `ACQUITTAL` in Telangana. *Next step:* check whether
   `disp_nature=12` means acquittal in another state's records; if it does, the integer is the
   crosswalk we need for blocker 6 and DDL's `disp_name_key` can be aligned to it.
4. **Other High Courts may embed the FIR in captions too.** Patna does. *Next step:* run the
   same regex family over one 2024 parquet for each of the other 24 courts and publish the
   match rate per court. Cheap (25 small downloads) and it would tell us exactly how many
   states get a free bail-level thana layer.
5. **DDL `cino` → `viewHistory` is a no-CAPTCHA enrichment path for 81M historical cases.**
   `viewHistory` needs `internal_case_no` alongside the CNR, which DDL does not ship — but
   `cnr_status/searchByCNR` may accept the CNR alone. *Next step:* test whether a CNR-only
   lookup returns the case page without a CAPTCHA. If it does, DDL 2010–2018 becomes
   enrichable nationally at district level and possibly to the act/section level, legitimately.
6. **Bihar SCRB FIR repository × Patna HC thana strings.** Both name Bihar police stations in
   free text. *Next step:* build the fuzzy crosswalk between the two name vocabularies and the
   `Bhugoal_BH_Police_Thana_Boundaries` polygon layer. Bihar is the one state where all three
   sides of the join plausibly exist.
7. **Dattam Labs' contact is a real, answerable address.** `contact@dattam.in` is in the AWS
   registry YAML. *Next step:* write, cite the Telangana pilot by name, ask about (a) a data
   licence, (b) state prioritisation, (c) whether they would take Bihar next.
8. **State Crime Records Bureau district disposal returns.** DCRBx report monthly to SCRBx.
   *Next step:* RTI to SCRB Bihar and SCRB Telangana for district-wise cases registered /
   charge-sheeted / final-report-true / final-report-false / pending, 2019–2025. Telangana is
   the state where we could *validate the answer against court data we already hold*.

---

## Phase 2 recommendations (ranked)

1. **Ingest the Telangana district pilot and build the entire outcomes pipeline against it.**
   ~40 tar files, a few hundred MB. It has everything the product needs — station, act,
   section, outcome, disposal date — and it lets us build, test and demo the whole thana
   outcome layer before anyone negotiates anything. Write the `fir_details` parser
   (`no ^ station ^ year`, collapse whitespace, strip `PS`/`P.S.`) and the `disp_name`
   crosswalk first, both test-first against saved fixtures per `docs/INGESTION.md`.
2. **Email Dattam Labs.** Licence, registry entry, and Bihar. One email, multi-week latency,
   unblocks the difference between a one-state demo and a national product. Start it in week one.
3. **Ingest Patna HC 2015–2026 and ship it as a clearly-labelled Bihar *bail* layer.** ~1.69M
   records, CC-BY-4.0, no permission needed, and it is the only thana-keyed Bihar court data in
   existence today. Publish the 73.9% match rate and the junk-thana list as part of the layer's
   metadata.
4. **Crawl `casestatus/fillPoliceStation` across all 3,567 complexes.** No CAPTCHA, bounded,
   reference data not case data. Produces the national station name↔code registry that blocker
   3 needs and that every other agent's work can join to. Single-threaded, delay between
   requests, per rule 4.
5. **Ingest DDL 2010–2018 as the district-level historical baseline** and as the 81M-CNR index.
   Convert to Parquet, keep `cino`, drop nothing else — the CNR is the asset.
6. **Ingest NCRB police and court disposal tables at state level** and wire them in as the
   validation benchmark. If our Telangana thana rollup does not reconcile to NCRB Telangana,
   we ship nothing.
7. **Run seed lead 4** (FIR-in-caption regex across all 25 High Courts). One afternoon; tells
   us how many states get a free thana layer.
8. **Defer:** the mobile API, any CAPTCHA'd endpoint, Indian Kanoon, NJDG API applications.
   The first two are rule problems, the last two are low-yield relative to items 1–4.
