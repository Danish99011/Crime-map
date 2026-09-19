# Union Government Crime-Relevant Data outside NCRB — MHA, BPR&D, Parliament
_Agent: mha-parliament · Researched: 2026-09-19 · Entries: 1 verified / 28 total_

> **Verification honesty statement.** This session's egress proxy blocks every `*.gov.in`,
> `*.nic.in` and most Indian domains (`mha.gov.in`, `bprd.nic.in`, `sansad.in`, `rsdoc.nic.in`,
> `112.gov.in`, `data.gov.in`, `cdnbbsr.s3waas.gov.in`, `prsindia.org`, `factly.in`,
> `huggingface.co`, `web.archive.org` — all returned `EGRESS_BLOCKED`). Only `github.com`,
> `raw.githubusercontent.com` and `en.wikipedia.org` were reachable. Consequently **one entry is
> `VERIFIED_LIVE`** (the open-source Parliament mirrors, whose READMEs and scraper source I read
> in full) and the rest are `CITED` — meaning the exact URL was returned verbatim by a search
> engine with a matching page title, but I did not open the page. Four entries are `UNVERIFIED`
> and carry **no URL at all**, because I refuse to write a URL I never saw. Everything below is
> re-verifiable in under an hour from an unblocked network; that is the single cheapest next action.

## Executive summary

- **The finest granularity in this whole domain is `district`, and it is reached almost entirely
  through Parliament answers**, not through any published dataset. MPs routinely extract
  State/UT-wise and district-wise tables that no ministry publishes anywhere else. This is the
  central finding.
- **Two genuine district-level layers exist.** (1) MHA's **LWE-affected district classification**
  and its district-wise incident/death series — but MHA declared in 2026 that *no district* remains
  LWE-affected, so this is now a historical layer (incidents fell 2,213 in 2010 → 33 by 21 Jul 2026).
  (2) **Parliament answer annexures**, which are a corpus, not a dataset.
- **MHA hosts its own Parliament answer PDFs in a crawlable static tree** at
  `mha.gov.in/MHA1/Par2017/…`, with per-sitting HTML index pages and per-question PDFs under
  `pdfs/par<YYYY>-pdfs/<HOUSE><DDMMYYYY>/<QNO>.pdf`. This sidesteps the sansad.in API entirely and
  hands you the MHA-only subset pre-filtered. Most people mining Indian PQs do not know it exists.
- **Digital Sansad has a real, working, undocumented JSON API.** `GET
  https://sansad.in/api_ls/question/qetFilteredQuestionsAns` with `loksabhaNo`, `sessionNumber`,
  `pageNo`, `pageSize`, `locale`, `ministryCode` and — critically — **`keyWord`**. I reconstructed
  the full request contract and response schema from six independent open-source clients. The
  Rajya Sabha equivalent, `rsdoc.nic.in/Question/Search_Questions?whereclause=<SQL>`, returns full
  question text and is genuinely searchable. Mining plan in its own section below.
- **`data.gov.in` already publishes Parliament answer annexures as CSV** — catalogs
  `answers-data-rajya-sabha-questions-session-<N>` for sessions 234 → 265+, maintained by MHA's own
  Parliament Section. This is the only place those annexure tables exist as machine-readable rows
  instead of table-images inside PDFs. **Ingest this before building any PDF table extractor.**
- **ERSS / Dial 112 is the highest-value and least-obtainable source in the domain.** It runs
  GIS-based Computer Aided Dispatch over ten intake channels — i.e. geocoded incident points in
  near-realtime. Nothing point-level is published; public output is state/national annual call
  totals via PQ answers and one `data.gov.in` resource (2020-21 to 2022-23, derived from Rajya Sabha
  Session 262). Records sit with **state** ERCs, not MHA.
- **BPR&D's Data on Police Organisations is the denominator, not a layer.** As on 01.01.2024
  (released 1 Jul 2025): **18,284 sanctioned police stations — 9,127 rural, 5,492 urban, 3,665
  special-purpose**. The special-purpose stations (railway/women/cyber/traffic) have no territorial
  jurisdiction and must be excluded from any geographic denominator. DoPO gives station **counts by
  state**, not a station **roster with locations** — the brief's hope for a mappable station roster
  is not satisfied by DoPO (see Seed Leads).
- **Safe City (8 cities, Nirbhaya Fund) is the best lever for sub-city geography.** Its own scheme
  text names "Identification of Crime Hot-spots in the city" and CCTV saturation of those hotspots.
  Each of the eight cities therefore produced a geocoded hotspot layer and a camera inventory.
  None is public. One successful RTI here changes the product.
- **Biggest blocker in this domain:** everything of value is inside a PDF annexure to a Parliament
  answer, and the answers are not searchable by their contents on any official system. `keyWord` on
  the LS API matches subject/metadata only; there is no server-side full-text search over answers.
- **Do not confuse MHA's incident counts with NCRB's FIR counts.** MHA/IB security reporting
  (communal, LWE, J&K, North-East) uses an undefined "incident" unit and diverges materially from
  NCRB at state level. Publishing both without labelling the difference would be a defamation risk.

## Source entries

### 1. MHA Annual Report
The backbone narrative document. Editions confirmed from 2004-05 (`AnnualReport_04_05.pdf`, which
reports 640 communal incidents / 129 deaths / 2,022 injured for 2004) through 2024-25
(`AREnglish_24032026.pdf`). Carries MHA's own communal, LWE, J&K and North-East incident series —
the only place they sit together. State-level; not a map layer by itself.

```
id: mha-parliament-mha-annual-report        tier: 3    priority: 3
publisher: Ministry of Home Affairs
landing: https://www.mha.gov.in/en/documents/annual-reports
data:    https://www.mha.gov.in/sites/default/files/AREnglish_24032026.pdf   (2024-25)
         https://www.mha.gov.in/sites/default/files/AnnualReport_27122024.pdf (2023-24)
         https://www.mha.gov.in/sites/default/files/AnnualReport202122_24112022[1].pdf
         https://www.mha.gov.in/sites/default/files/AnnualReport_04_05.pdf
geo: all-India / state     unit: aggregate-count     2004-05 → 2024-25, annual, lag 9-15mo
taxonomy: custom   formats: PDF   access: open-download   machine_readable: 1   licence: GODL-India
ingest_difficulty: 3   verification: CITED   checked_on: 2026-09-19
caveats: narrative not statistical; no XLSX companion; MHA≠NCRB on communal counts;
         "incident" never defined; table numbering shifts between editions — key on captions.
```

### 2. MHA Left Wing Extremism Division — district classification and violence data
**The only genuinely district-level MHA series, and it has just been retired.** Post-31-March-2026
security review: *no district in the country falls under the LWE-affected category*. Historical arc:
~200 districts (2005) → 2 core districts → 0; last "most affected" trio was Bijapur, Sukma and
Narayanpur (all Chhattisgarh). Incidents 2,213 (2010) → 33 (to 21 Jul 2026); deaths 1,005 → 11.

```
id: mha-parliament-lwe-division              tier: 3    priority: 4
landing: https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division
geo: ~10 states (Red Corridor) / DISTRICT   unit: aggregate-count   2005 → 2026-07-21, irregular
formats: PDF, HTML   access: open-download   machine_readable: 1   licence: GODL-India
ingest_difficulty: 3   verification: CITED   checked_on: 2026-09-19
caveats: series effectively terminated 2026; category membership is a FUNDING decision (SRA
         eligibility), not an incidence measure; IB-sourced not FIR-sourced; district boundaries
         changed repeatedly 2005-2026 (Chhattisgarh, Jharkhand, Telangana) — needs a crosswalk;
         per-district annual counts live in PQ answers, not on the division page.
how_to_obtain: crawl the division page for scheme docs/press notes; authoritative per-district
         tables come from MHA PQ answers. RTI the LWE Division for year-wise district-wise
         incident/death 2005-2026 if the PQ trawl leaves gaps.
```

### 3. Safe City Projects (Nirbhaya Fund Phase I, 8 cities)
Delhi, Mumbai, Chennai, Kolkata, Hyderabad, Ahmedabad, Lucknow, Bengaluru. Launched 2018, tenure
extended to 2024. 60:40 Centre:State. Sanction figures conflict across sources (MHA approvals
Rs 3,080.16 crore vs project cost Rs 2,919.55 crore). **Published material is scheme text, not crime
data** — but the scheme mandates crime-hotspot identification and CCTV saturation, so a geocoded
hotspot layer and a camera inventory exist in each city.

```
id: mha-parliament-women-safety-safe-city     tier: 3   priority: 3
landing: https://www.mha.gov.in/en/divisionofmha/women-safety-division/safe-city-projects
docs:    https://www.mha.gov.in/en/commoncontent/safe-city-projects
data:    https://www.mha.gov.in/sites/default/files/pressreleasesafecityprojectinLucknow_01112018.pdf
         https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=188078&reg=48&lang=2
geo: 8 cities / CITY   unit: narrative-document   2018 → 2024   irregular
access: open-download   machine_readable: 1   ingest_difficulty: 4   verification: CITED
how_to_obtain: RTI each Safe City PMU / state police Safe City Project Director for (a) hotspot
         locations with coordinates used for camera siting, (b) ICCC camera inventory with lat/long.
         Expect s.8(1)(g)/(h) refusal; appeal on the ground that cameras are visible in public space.
```

### 4. Nirbhaya Fund
Rs 1,000 crore corpus announced 2013, administered by DEA, spent across MHA/MWCD/MoRTH/Railways/MeitY.
Chronic underutilisation — of Rs 587 crore allocated to Sambal in 2021-22, ~Rs 183 crore (31%) used.
Money, not crime: use only to date when a city got CCTV/ERSS.

```
id: mha-parliament-nirbhaya-fund   tier: 3   priority: 2   geo: state   verification: CITED
landing: https://www.mha.gov.in/en/commoncontent/nirbhayaerss-section
docs:    https://en.wikipedia.org/wiki/Nirbhaya_Fund   (fetched; confirms corpus, DEA, Sambal figure)
```

### 5. ERSS / Dial 112 — **the flagship target**
State-centric system on a common MHA platform. Ten intake channels (voice, SMS, SOS, email, web
request, chatbot, media crawler, IoT signals, WhatsApp, external signals). GIS-based Computer Aided
Dispatch with dynamic map updating and continuous contact with dispatched vehicles. Each State/UT
runs a dedicated Emergency Response Centre and its own instance (e.g. `rj.erss.in`).

```
id: mha-parliament-erss-112                  tier: 2    priority: 5
landing: https://112.gov.in/        (also /about /features /faq)
docs:    https://www.mha.gov.in/en/commoncontent/emergency-response-support-system-erss
data:    https://www.data.gov.in/resource/year-wise-details-number-calls-received-emergency-number-112-2020-21-2022-23
geo: all States/UTs / POINT (internal) — STATE (published)   unit: incident-point
2019 → live   cadence: realtime internally; published aggregates lag 6-24 months
formats: dashboard-only, PDF, CSV   access: BLOCKED   machine_readable: 1   licence: unstated
ingest_difficulty: 5   verification: CITED   checked_on: 2026-09-19
caveats: a 112 call is DISTRESS, not crime — large medical/fire/RTA/prank/test share; volume tracks
         awareness and channel mergers, not incidence (Haryana Apr-2025 6,06,039 calls vs Apr-2024
         5.35 lakh; 2.31 crore calls and 46.6 lakh dispatches since inception); no single national
         record store — 36 state instances with different schemas and retention.
how_to_obtain: public aggregates from the data.gov.in resource (itself derived from Rajya Sabha
         Session 262 answers) and MHA PQ annexures. For finer data, RTI a SINGLE state's ERSS/ERC
         nodal officer for monthly 112 call counts by call-category and by POLICE-STATION
         JURISDICTION — not caller identity, not coordinates. Framing it as jurisdiction-level
         counts defeats the privacy objection. Start with Rajasthan, Kerala or Telangana. Do not
         ask MHA: MHA does not hold the records.
```

### 6. MHA Cyber & Information Security Division / I4C
I4C became an attached office of MHA on 1 July 2024. Runs NCRP (`cybercrime.gov.in`), helpline 1930
and the **Samanvaya** MIS/repository with interstate crime-criminal linkage analytics. Headline
numbers released as PIB soundbites: Rs 7,130 crore saved across 23.02 lakh complaints, 16,840
arrests, 1,05,129 investigation-assistance requests.

```
id: mha-parliament-cis-i4c    tier: 2   priority: 2   geo: state   verification: CITED
landing: https://www.mha.gov.in/en/division_of_mha/cyber-and-information-security-cis-division/Details-about-Indian-Cybercrime-Coordination-Centre-I4C-Scheme
docs:    https://www.pib.gov.in/PressReleasePage.aspx?PRID=2205201&reg=3&lang=1
caveats: NCRP complaints ≠ FIRs (low, state-varying conversion); cybercrime has no
         offence-location property — mapping to victim district is analytically weak, label it.
companion entry: mha-parliament-ncrp-cybercrime-portal
```

### 7. MHA Parliament Questions archive (`MHA1/Par2017`) — **underrated**
MHA mirrors its own answer PDFs in a static, crawlable tree with per-sitting HTML index pages
(English and Hindi variants).

```
id: mha-parliament-mha-pq-portal              tier: 3    priority: 5
landing: https://www.mha.gov.in/MHA1/Par2017/PArQueAnsPage-new.html
index:   https://www.mha.gov.in/MHA1/Par2017/Rs-02082023-hindi.html
data:    https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/LS18032025/2946.pdf
         https://www.mha.gov.in/MHA1/Par2017/pdfs/par2023-pdfs/RS05042023/3734.pdf
         .../MHA1/Par2017/pdfs/par2018-pdfs/ls-11122018/156.pdf
docs:    https://services.india.gov.in/service/detail/answers-to-parliament-question-mha
geo: all-India, annexures often State/UT- and DISTRICT-wise   unit: narrative-document
2017 → 2025 confirmed   lag: days after the sitting   access: scrape   machine_readable: 2
ingest_difficulty: 3   verification: CITED   checked_on: 2026-09-19
caveats: URL scheme is NOT stable — 2018 uses lowercase-hyphen `ls-11122018/`, 2023/2025 use
         uppercase `RS05042023/` and `LS18032025/`. DO NOT GUESS; crawl the sitting index.
         Hindi duplicates. Annexure tables often image-only. Many answers say "data not
         maintained centrally" — a large share of hits are duds.
```

### 8. Digital Sansad Lok Sabha Questions API
```
id: mha-parliament-sansad-ls-questions-api    tier: 3    priority: 5
landing: https://sansad.in/ls/questions/questions-and-answers
api:     https://sansad.in/api_ls/question/qetFilteredQuestionsAns      (GET)
         https://sansad.in/api_ls/question/qetAllQuestions
         https://sansad.in/api_ls/question/member/qetFilteredQuestionsAns
         https://sansad.in/api_ls/business/AllLoksabhaAndSessionDates
         https://sansad.in/api_ls/member/{mpsno}?locale=en
         https://sansad.in/api_ls/debate/debate-search
         https://sansad.in/api_ls/debate/text-of-debate
         https://sansad.in/api_ls/committee/lsRSAllReports
params:  loksabhaNo, sessionNumber, pageNo, pageSize, locale=en, ministryCode, keyWord
headers: User-Agent: <project>/1.0 ; Referer: https://sansad.in/ls/questions/questions-and-answers
response: single-element array → data[0].listOfQuestions[] and data[0].totalRecordSize
record:  quesNo, subjects, lokNo, member[], ministry, type(STARRED|UNSTARRED), date,
         questionText, answerText, answerTextHindi, questionsFilePath, questionsFilePathHindi,
         sessionNo, supplementaryQuestionResDtoList[], supplementaryType
formats: JSON, PDF   access: scrape   machine_readable: 3   licence: unstated
ingest_difficulty: 3   verification: CITED   checked_on: 2026-09-19
caveats: undocumented, reverse-engineered from the Next.js bundle; endpoint is misspelled ("qet");
         some routes are REFERER-CHECKED and return an HTML error page instead of JSON;
         questionText/answerText frequently null — the PDF at questionsFilePath is authoritative;
         question numbers RESTART each Lok Sabha term, so (lokNo, sessionNo, quesNo) is the key;
         keyWord matches subject/metadata only — NO server-side full-text search over answers.
```

### 9. Rajya Sabha Questions — `rsdoc.nic.in` + `cms.rajyasabha.nic.in`
```
id: mha-parliament-sansad-rs-questions        tier: 3    priority: 4
landing: https://sansad.in/rs/questions/questions-and-answers
api:     https://rsdoc.nic.in/Question/Search_Questions?whereclause=<url-encoded SQL predicate>
         e.g.  (qtitle LIKE '%crime%' OR qn_text LIKE '%crime%')
         e.g.  ses_no>=265 and ses_no<=271 and mp_code='<code>'
data:    https://cms.rajyasabha.nic.in/UploadedFiles/Questions/QuestionsList/259/English_202326_EngUQ060223.pdf
         https://cms.rajyasabha.nic.in/UploadedFiles/Questions/QuestionsStatistical/228/20201128_228.pdf
         https://cdnbbsr.s3waas.gov.in/s35d6646aad9bcc0be55b2c82f69750387/uploads/2025/01/202501081712938686.pdf
                                                     (266th session, Winter 2024 replies volume)
access: scrape   machine_readable: 3   ingest_difficulty: 4   verification: CITED
caveats: whereclause takes a RAW SQL FRAGMENT — query it read-only, never probe it; expect it to be
         patched or withdrawn without notice. Full question text IS returned (qtitle, qn_text) but
         ANSWER TEXT IS NULL FOR EVERY RECORD — answers are PDF-only (exact inverse of the LS API's
         weakness). One row per question-member pairing → de-duplicate on (ses_no, question no).
```

### 10. `data.gov.in` — Answers Data of Rajya Sabha Questions (per session)
**The only place Parliament answer annexures already exist as CSV.** Maintained by MHA's Parliament
Section under NDSAP. Catalogs confirmed for sessions 234, 239, 250, 254, 256, 258, 259, 263, 265.

```
id: mha-parliament-ogd-rs-answers-data        tier: 1    priority: 4
landing: https://www.data.gov.in/catalog/answers-data-rajya-sabha-questions-session-265
         https://www.data.gov.in/catalog/answers-data-rajya-sabha-questions-session-263   (…-234, -239, -250, -254, -256, -258, -259)
geo: all-India, resources often State/UT-wise   formats: CSV, JSON, HTML
access: api-key (free data.gov.in registration)   machine_readable: 4   licence: GODL-India
ingest_difficulty: 2   verification: CITED
caveats: PATCHY — only annexures a ministry chose to upload appear; it is a convenience layer, not
         a mirror. One catalog per session (~8/yr) and no cross-session search. Column headers are
         inconsistent between ministries and sessions.
```

### 11. Open-source Parliament Q&A mirrors and pipelines — **the one VERIFIED entry**
```
id: mha-parliament-oss-pq-mirrors             tier: 4    priority: 4   verification: VERIFIED_LIVE
https://github.com/indiavotes/proceedings-data          4 corpora (debates-ls/rs, questions-ls/rs)
                                                        newest-first JSON shards: reports-<house>-NN.json,
                                                        texts-NN.json, manifests, audit.json;
                                                        "LS questions alone is ~243K records";
                                                        RS backfill walks ~72 sessions;
                                                        4 Cloudflare Pages deployments
https://github.com/NakliTechie/sansadsaar-proceedings-data
                                                        ~57,000 LS speech-level debate records,
                                                        ~280,000 LS per-question records; sources
                                                        sansad.in api_ls/* and api_rs/*; 1,348 commits;
                                                        served at sansadsaar-proceedings.naklitechie.com
https://github.com/herrrickshaw/lok-rajya-sabha-qa      34,720 LS question records; 24,661 RS records
                                                        (sessions 265-271); documents that LS lacks
                                                        question text and RS lacks answer text
https://github.com/livelifelively/pipeline.loksabha-qna TWO-STAGE EXTRACTOR — Stage 1 Marker (text) +
                                                        Camelot (table DETECTION) locally, free;
                                                        Stage 2 Gemini vision ONLY on documents where
                                                        Stage 1 detected tables. Output markdown +
                                                        question.progress.json state file.
also: https://github.com/NakliTechie/parliamentwatch-data , https://github.com/pranaykotas/parliamentwatch ,
      https://github.com/CMHLP/archive (RS scraper) , https://www.opensanctions.org/datasets/in_sansad/
caveats: third-party, no SLA, licences unstated. They mirror METADATA and PDFs, NOT extracted
         statistics. Record counts differ between mirrors for the same corpus (34,720 vs ~243K vs
         ~280K) because the UNIT differs (per-question vs per-question-member vs per-shard) —
         reconcile before trusting any count.
```

### 12. BPR&D — Data on Police Organisations (DoPO)
```
id: mha-parliament-bprd-dopo                  tier: 1    priority: 4
landing: https://bprd.nic.in/page/dopo
data:    https://bprd.nic.in/page/data_on_police_organization_dopo
docs:    https://bprd.nic.in/page/table_b  /page/table_c  /page/table_d
         https://bprd.nic.in/page/documents_by_statesuts
geo: all States/UTs + CPOs + CAPFs / STATE   unit: aggregate-count
1986 → as on 01.01.2024 (released 1 Jul 2025 at Bharat Mandapam, with DIPTI as on 31.03.2024)
annual, lag 12-18 months   formats: PDF   access: open-download   machine_readable: 1
licence: GODL-India   ingest_difficulty: 3   verification: CITED   checked_on: 2026-09-19
key numbers: 18,284 SANCTIONED police stations as on 01.01.2024 —
             9,127 rural + 5,492 urban + 3,665 special-purpose
caveats: SANCTIONED ≠ actual — routinely conflated in secondary reporting. Special-purpose stations
         (railway, women, cyber, SC/ST, traffic) have NO TERRITORIAL JURISDICTION and must be
         excluded from any geographic denominator. PDF-only, print-laid-out tables with merged
         headers — every edition needs its own parser. As-on-1-January snapshot but states report
         at different times; missing cells are common and unflagged. "Police station" vs "outpost"
         vs "police post" is defined differently by each state — cross-state density is not
         comparable without care. GIVES STATION COUNTS BY STATE, NOT A STATION ROSTER WITH
         LOCATIONS; whether any edition breaks stations down by district could not be verified.
```

### 13-14. BPR&D — DIPTI and state documents
`DIPTI` (Directory of Indian Police Training Institutions, as on 31.03.2023) at
`https://bprd.nic.in/uploads/pdf/1716350798_80f5684dfb1ba3181fd5.pdf` — the one BPR&D publication
shipping named facilities with postal addresses, i.e. geocodable. Priority 1.
`https://bprd.nic.in/page/documents_by_statesuts` — contents unverified; worth one recon pass.
(`/page/documents_by_bprd`, `/page/completed_circulated_to_states`, `/find` also exist.)

### 15. MHA Police Modernisation Division allocations
Context only, priority 1. **No division landing URL was confirmed, so none is recorded.** Only
`https://www.mha.gov.in/sites/default/files/2023-01/bprd_0[1].pdf` was observed. MPF/CCTNS release
tables come out as PQ annexures nearly every session — mine those. Useful as a covariate: MPF/CCTNS
release dates explain when a state's reporting quality changes.

### 16-17. CBI
`https://cbi.gov.in/view-fir` — an actual FIR register, `fir-record` unit, but a few thousand cases a
year, biased by construction (corruption, bank fraud, court-referred), located at the CBI *branch*
city not the offence, and coverage determined by which states have withdrawn general consent.
Priority 1. Companion: `https://www.data.gov.in/resource/year-wise-detail-corruption-case-registered-central-bureau-investigation-cbi-2017-2021`
(national totals, series ends 2021).

### 18-20. NIA · NATGRID · Bureau of Immigration — **UNVERIFIED, no URLs recorded**
- **NIA** — only secondary reporting seen (210 accused across 80 cases in 2024; a planned
  NIA-NATGRID-IB national database of bomb blasts, terror funding, FICN, narcotics, hawala, arms).
  Case pages, if they exist, name a police station and district — district-or-finer but N is
  negligible. s.24 RTI exemption applies.
- **NATGRID** — closed intelligence-fusion platform linking 21+ databases for 10+ agencies. Nothing
  public, s.24 exempt. **Recorded as a negative result so nobody re-investigates it.**
- **Bureau of Immigration** — no data page surfaced. Its crime-relevant content (LOCs, deportations,
  trafficking interceptions, Foreigners-Act offences) is port-of-entry, not neighbourhood, and
  Foreigners-Act counts are already in NCRB SLL heads.

### 21. National Commission for Women — Statistical Overview of Complaints
```
id: mha-parliament-ncw-complaint-statistics   tier: 3    priority: 2
data:    https://ncwapps.nic.in/frmComp_stat_Overview.aspx
landing: https://www.ncw.gov.in/
docs:    https://cdn.ncw.gov.in/wp-content/uploads/2025/03/NCWAnnualReport20232024Eng.pdf
api:     https://www.data.gov.in/resource/year-wise-number-complaints-received-national-commission-womenncw-related-investigation
geo: State/UT   2000 → 2026 (dashboard exposes the CURRENT year — its one advantage over NCRB)
filters: year (2000-2026) × report type (Nature Wise | State Wise | Nature Vs State) × state
caveats: complaints, NOT crimes, NOT FIRs. 7,698 complaints in all of 2025; 12,648 in 2024 — of
         which UP 6,492, Delhi 1,119, Maharashtra 764. That distribution reflects NCW's reach and
         UP's population, NOT relative danger. NCW's "nature" taxonomy does not map onto IPC/BNS.
         Complaint state = complainant's state, which for online complaints ≠ incident location.
how_to_obtain: ASP.NET WebForms — state carried in __VIEWSTATE. Needs a session and one POST per
         (year, report_type): 26 × 3 ≈ 78 requests. Do it once, politely.
hand-off: give to a women's-safety agent if one exists.
```

### 22. NHRC complaints and custodial deaths
Custodial-death cases registered at NHRC: 176 (2021-22), 163 (2022-23), 157 (2023-24), 140 (2024-25),
**170 in the first 74 days of 2026** (Bihar 19, Rajasthan 18, UP 15). One disciplinary action
reported over five years (Tamil Nadu). Annual Report 2022-23 at
`https://nhrc.nic.in/assets/uploads/annual_reports/1755187649_22c03590defde4e97944.pdf` (uploaded 2025 —
an 18-30 month lag). **The current numbers reach the public exclusively through Parliament answers** —
a direct illustration of the PQ-mining thesis. FY vs CY basis differs between AR and PQ. `hrcnet.nic.in`
was not confirmed as a public statistics source. Priority 2; hand off if another agent covers HR bodies.

### 23. PIB press releases
```
id: mha-parliament-pib-releases   tier: 3   priority: 3   geo: state   cadence: daily, lag same-day
https://www.pib.gov.in/PressReleasePage.aspx?PRID=2088945&reg=48&lang=2   MHA Year End Review 2024
https://www.pib.gov.in/PressReleasePage.aspx?PRID=2205201&reg=3&lang=1    Cyber security & fraud combat
https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=188078&reg=48&lang=2   Safe City Project (legacy scheme)
caveats: the ministry's framing of its own numbers — denominators, date ranges and definitions
         routinely omitted. Most statistics releases are VERBATIM REPRODUCTIONS of a Parliament
         answer, so PIB is derivative of the PQ corpus — but faster to search. TWO URL schemes
         (PressReleasePage.aspx?PRID= and legacy newsite/PrintRelease.aspx?relid=) — crawl both.
         reg/lang params change content; verify per release. Year-End Reviews are the densest
         annual artefact per ministry.
use: high-recall / low-precision discovery index. NEVER cite PIB alone in the product.
```

### 24-28. Flags, mirrors and parked items
- **NCB (narcotics)** — flagged only per brief; dedicated agent owns it. No URL verified here.
- **Commercial mirrors** — `https://dataful.in/datasets/18054/` (NHRC custodial deaths),
  `https://www.indiastat.com/data/crime-and-law/complaints-registered-by-national-human-rights-commission-nhrc`.
  Paid, ToU restricts redistribution — **fatal for a public map**. But they do exactly what we
  propose: harvest PQ annexures into tidy CSVs. **Strategic use: scrape their dataset TITLES (not
  their data) to build our own extraction target list.**
- **`https://services.india.gov.in/service/detail/answers-to-parliament-question-mha`** — signpost
  page; a stable entry point if MHA reorganises its URLs.
- **15th Finance Commission police/justice grants** — context only, no URL verified, parked.

## Granularity reality check

| Level | What actually exists at that level | Period | Refresh | Reality |
|---|---|---|---|---|
| `point` | ERSS/112 CAD records (geocoded, 10 channels) | 2019→live | realtime | **Not published. Held by 36 state ERCs.** Best case via single-state RTI, and then only as jurisdiction counts. |
| `point` | Safe City CCTV / ICCC camera inventories, crime-hotspot layers | 2018→ | one-off | **Not published.** Exists in 8 city PMUs. RTI target. |
| `ward`/`beat` | — | — | — | **Nothing at Union level. Zero.** |
| `police-station` | DoPO gives station *counts* by state, not a roster | 1986→2024 | annual, 12-18mo lag | A denominator, not a map layer. No national station roster with locations was found. |
| `district` | LWE-affected classification + district incident/death tables | 2005→2026 | irregular | Real, but the series was **terminated in 2026** (0 districts). Historical layer. |
| `district` | Parliament answer annexures (LS + RS) | ~2015→current | per session, days | **The only live district-level channel.** A corpus, not a dataset — requires PDF table extraction. |
| `city` | Safe City project docs (8 cities); CBI branch cases | 2018→ | irregular | Scheme text and a negligible case count. |
| `state` | MHA AR incident series; DoPO; NCW; NHRC; I4C/NCRP; ERSS call totals; OGD PQ CSVs | 2000→2026 | annual/monthly | Plentiful and easy. **This is where the domain actually lives.** |
| `national` | PIB releases, CBI OGD series | →current | daily | Headlines. |

**Blunt version:** for the product intent ("is this neighbourhood safe to walk through at night?"),
this entire domain delivers essentially nothing on its own. Its jobs are (a) supply the
**denominator** (BPR&D police strength and station counts), (b) supply **district-level covariates
and historical layers** (LWE), and (c) act as the **extraction channel** (Parliament answers) through
which district-level numbers that are never otherwise published reach the public.

## Blockers and how to get past them

1. **This session's egress policy blocks every Indian government domain.** 27 of 28 entries could
   not be opened. *Fix:* re-run verification from an unblocked network, or have a human in India
   open the ~15 landing pages listed above. Budget one hour. This is the cheapest next action by a
   wide margin and it converts most of this dossier from `CITED` to `VERIFIED_LIVE`.
2. **The data is inside PDF annexures.** The answer body is usually a text PDF; the statistical
   annexure is often an image or a print-laid-out table. *Fix:* adopt the two-stage design from
   `livelifelively/pipeline.loksabha-qna` — Marker + Camelot locally for **table detection** (free,
   fast), vision-LLM **only** on the detected subset (expensive, accurate). Do **not** run a vision
   model over the whole corpus.
3. **No official full-text search over answers.** LS `keyWord` matches subject/metadata only.
   *Fix:* use the RS `rsdoc.nic.in` `whereclause` (which *does* search `qn_text`) for discovery,
   then pull the matching LS/MHA answer for the structured record. The same MHA answer is usually
   given in both houses.
4. **`sansad.in` API is undocumented and Referer-checked.** Param names differ between clients,
   which means they have changed. *Fix:* pin a client, monitor for schema drift, and keep the
   MHA `MHA1/Par2017` static tree as a redundant path — it is plain HTML/PDF and far more stable.
5. **MHA answer-PDF URL scheme is inconsistent across years.** *Fix:* never construct URLs; crawl
   the per-sitting index pages and follow links.
6. **MHA ≠ NCRB.** Two official numbers for the same phenomenon will be quoted against us. *Fix:*
   store `source_system` on every row and never blend MHA incident counts with NCRB FIR counts in
   one series or one map layer.
7. **ERSS records are state-held, not MHA-held.** An RTI to MHA will be transferred or refused.
   *Fix:* file to the state ERC nodal officer directly, and ask for jurisdiction-level counts by
   call category — not points, not identities.
8. **`ncwapps.nic.in` is `__VIEWSTATE`-bound ASP.NET.** *Fix:* session-aware scraper, ~78 POSTs, once.
9. **Licensing is unstated on `sansad.in`, `rsdoc.nic.in`, NCW and NHRC.** Only `data.gov.in` and
   MHA documents are clearly GODL-India. *Fix:* get counsel to sign off on republishing
   Parliament-answer-derived tables (they are proceedings of Parliament — likely fine, but confirm)
   before the tables reach the front end.

## Seed Leads (unconfirmed but probably real)

1. **A national police-station roster with locations.** DoPO gives counts, not a roster. CCTNS
   covers 17,000+ police stations (per MHA statements quoted in press) and ICJS/the Digital Police
   Portal must hold a station directory with jurisdiction identifiers. *Next step:* ask NCRB/MHA for
   the CCTNS police-station master (station code, name, district, jurisdiction) via RTI — it is
   administrative reference data, not case data, so the s.8 exemptions are weak. **This is the
   single highest-value unconfirmed lead in the domain.** A station roster turns every
   station-level count anyone ever publishes into a map.
2. **`ministryCode` for the Ministry of Home Affairs on the sansad LS API.** Confirmed codes seen in
   the wild: 59 = MeitY, 12 = Education, 39 = Finance. MHA's code is unknown. *Next step:* one call
   to `qetFilteredQuestionsAns` with a known MHA question and read back `ministry`, or enumerate
   codes 1-80 once. Trivial from an unblocked network; it cuts the LS crawl by ~95%.
3. **Per-district LWE incident/death tables 2005-2026.** Certainly exist inside MHA as an SRA
   administrative series. *Next step:* RTI to the LWE Division, MHA, North Block, for "year-wise,
   district-wise number of LWE incidents and resultant deaths, 2005 to 2026" — a table they
   demonstrably maintain because they answer it piecemeal in Parliament every session.
4. **Safe City crime-hotspot layers and ICCC camera inventories** for the 8 cities. *Next step:*
   RTI to each state's Safe City Project Director (Delhi Police, Mumbai Police, Greater Chennai
   Police, Kolkata Police, Hyderabad/Cyberabad, Ahmedabad, Lucknow, Bengaluru City Police).
5. **State ERSS monthly call statistics by category and jurisdiction.** Some states publish a public
   dashboard on their own instance (`rj.erss.in` exists; others almost certainly do). *Next step:*
   enumerate `<state>.erss.in` and each state police site for a 112 dashboard before filing any RTI.
6. **`api_rs/*` endpoints.** `NakliTechie/sansadsaar-proceedings-data` states it sources from
   `sansad.in`'s `api_ls/*` **and `api_rs/*`** endpoints, but I could not read the `api_rs` paths.
   *Next step:* read `questions/scrapers/` and `questions/common.py` in that repo — the exact RS
   endpoint paths are in there and this is a 5-minute job.
7. **MHA Annual Report pre-2004.** The index may go back further than 2004-05. *Next step:* open
   `/en/documents/annual-reports` and page to the end.
8. **NCRB / MHA "Crime in India" state-district crosswalk.** District reorganisation
   (Chhattisgarh, Jharkhand, Telangana, Ladakh, and the 2022-23 wave in Rajasthan) breaks every
   district time series. *Next step:* ask whether LGD (Local Government Directory, `lgdirectory.gov.in`)
   publishes historical district code changes — this is a boundary-agent hand-off but nobody has claimed it.

## Phase 2 recommendations (ranked)

1. **Re-verify from an unblocked network (1 hour).** Open the ~15 landing pages, confirm the DoPO
   PDF link and the MHA PQ index, capture the MHA `ministryCode`. Everything below depends on this.
2. **Ingest `data.gov.in` "Answers Data of Rajya Sabha Questions" sessions 234→current.** Free API
   key, CSV/JSON, already parsed. **Highest ratio of usable rows to engineering hours in the entire
   domain.** Do it before writing a single line of PDF-parsing code.
3. **Crawl the MHA `MHA1/Par2017` PQ tree.** Static HTML indexes → per-question PDFs, pre-filtered to
   MHA, ~8 sessions/yr × 2 houses. Politely rate-limited at 1 req/2s this is a few hours of wall
   clock and gives the complete MHA answer corpus with no API fragility.
4. **Build the two-stage annexure extractor** (Marker + Camelot detect → vision-LLM on hits only).
   Validate it against the `data.gov.in` CSVs from step 2 — you have ground truth for free.
5. **Ingest BPR&D DoPO as the denominator.** Parse the 01.01.2024 edition first, then backfill.
   Store sanctioned and actual separately; tag special-purpose stations and exclude them from
   geographic denominators.
6. **Discovery sweep on `rsdoc.nic.in`** with a crime vocabulary in `whereclause` over `qtitle` and
   `qn_text` (crime, FIR, police station, rape, murder, atrocities, cyber, missing, trafficking,
   custodial, conviction, NCRB, district-wise). Output: a ranked list of which answers carry tables.
7. **File the ERSS single-state RTI** (Rajasthan / Kerala / Telangana) for monthly 112 call counts by
   category and police-station jurisdiction. Long lead time — start it in parallel with step 1.
8. **File the CCTNS police-station-master RTI** (seed lead 1). Also long lead; start early.
9. **Build the LWE historical district layer** from MHA AR annexures + PQ answers + a district
   crosswalk. Ship it labelled "historical — MHA declared zero LWE-affected districts in 2026".
10. **Set up a PIB watcher** on `reg=48` (MHA) as a low-cost alerting tripwire for new statistics
    announcements, resolving each to its underlying Parliament answer before use.
11. Park NATGRID, NIA, Bureau of Immigration, NCB and the 15th FC. Recorded, not worth further time.
