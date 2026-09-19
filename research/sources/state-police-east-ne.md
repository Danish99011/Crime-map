# State Police & Home-Department Data — East India and the North East

_Agent: state-police-east-ne · Researched: 2026-09-19 · Entries: 0 verified / 44 total_

**Scope:** Bihar, Jharkhand, West Bengal, Odisha, Sikkim, Assam, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, Meghalaya.

---

## READ THIS FIRST — verification integrity notice

**Zero entries in this dossier are `VERIFIED_LIVE` or `VERIFIED_LANDING`, and that is not a research
failure — it is an environment constraint that must be recorded loudly so the master catalogue is not
misread.**

This research sandbox's egress policy **blocks the entire `.gov.in` namespace**, plus `archive.org`.
Confirmed blocked by direct `WebFetch` attempt on 2026-09-19:

| Host | Result |
|---|---|
| `police.odisha.gov.in` | `EGRESS_BLOCKED` |
| `kolkatapolice.gov.in` | `EGRESS_BLOCKED` |
| `police.assam.gov.in` | `EGRESS_BLOCKED` |
| `ncrb.gov.in` | `EGRESS_BLOCKED` |
| `data.gov.in` | `EGRESS_BLOCKED` |
| `archive.org` / `web.archive.org` | `EGRESS_BLOCKED` (so the Wayback fallback is also unavailable) |
| `en.wikipedia.org` | **reachable** — used for structural facts only |

Per `/root/.ccr/README.md`, a proxy egress denial must be reported rather than routed around. It was
not retried or circumvented.

**Consequence for how you read every entry below:**

- `verification: CITED` throughout for government sources. The evidence base is **search-engine index
  metadata**: the index returned the *exact URL together with its page title*. That is materially
  stronger than hearsay — it proves the URL was crawlable and names what the page calls itself — but it
  is **not a fetch**. Page contents, year coverage, table structure, row counts and file sizes are
  **inferred or unknown** unless an entry says otherwise.
- The `access` field records the **true expected access mode for the eventual pipeline** (open-download,
  scrape, login, captcha, rti-only), *not* this sandbox's inability to reach it. Marking forty entries
  `blocked` would have destroyed the field's meaning. The sandbox block is instead recorded as the first
  `caveats` entry on every affected source, prefixed `UNFETCHED:`.
- **Hard Rule 1 was obeyed: no URL here was invented.** Every URL was returned by a search index with a
  title attached. Where a URL pattern is *extrapolated* rather than observed (Mizoram district SP hosts,
  Meghalaya district chart codes, WB district roster hosts), the entry says so in capitals.

**Phase 2 must re-verify from an Indian or unrestricted network before any of this is trusted.** The
single highest-value next action for this domain is not more searching — it is ~30 HTTP GETs.

---

## Executive summary

- **10 of 12 states have a named, published crime-data artefact. Only ~6 look usable for a map.**
  Usable: Odisha, Bihar, Sikkim, Meghalaya, Mizoram, Tripura. Marginal: Assam, Nagaland, Jharkhand.
  Thin: Arunachal, Manipur. **West Bengal publishes nothing** and is the region's biggest hole.
- **The brief's expectations are inverted by the findings.** The region's best published crime data is
  not in the big states — it is in **Sikkim (monthly, 2023→2025)** and **Meghalaya (district-wise,
  2010–2023)**. Meanwhile **West Bengal**, with 516 police stations and 91 more under Kolkata Police,
  has no state crime publication at all, and the expected "Kolkata Police at a glance" annual crime
  review **could not be substantiated by two separate searches** — treat that premise as lapsed.
- **Finest granularity in the region is FIR-level, daily, at named police stations** — the
  **SCRB Bihar public FIR repository** (`scrb.bihar.gov.in/View_FIR.aspx`), which uploads all FIRs under
  Supreme Court / High Court direction. **Sikkim's Daily FIR** page is the same shape at 1/100th the
  volume and 1/10th the scraping effort.
- **Best single seed for a police.uk-shaped product: the Bhubaneswar–Cuttack Police Commissionerate.**
  It is the only host in all 12 states that combines **per-police-station pages** + a **`/maps/` section**
  + a **named annual crime-statistics series** on one site. Build the regional prototype there.
- **There is no API anywhere in this domain.** CCTNS's 11 searches and 44 reports are for police and
  agencies (CBI, IB, ED, NIA) only. The only documented machine interface touching this region is the
  generic **data.gov.in resource API**, which serves exactly three relevant resources.
- **ICCC / Smart City command centres are a dead end for public data** — explicitly checked because the
  brief asked. They are operational consoles showing live CCTV and sensor feeds to city staff. No public
  crime dashboard exists for Bhubaneswar, Ranchi, Guwahati, Kolkata or Patna. **The useful residue is
  `smartcities.data.gov.in`**, the open-data portal the SPVs publish to — which is where *Crimes in
  Ranchi* and *Bhubaneswar: Police Station Details* actually come from. Chase the data portal, not the
  command centre.
- **The AFSPA overlap is a correctness problem, not a footnote.** In Manipur, Nagaland, Assam and parts
  of Arunachal, a large share of violent incidents routes to **MHA and SATP as insurgency data**, never
  entering the police crime series. A map built on police data alone renders these states implausibly
  peaceful. Carry the conflict layer separately or caveat loudly — never merge the two.
- **NE states do report to NCRB, but low NE crime rates must never be rendered as "safe."** Nagaland's
  Women Helpline 181 logged **200,000+ calls since 2016 against ~3,400 formal cases** — roughly a
  **1.7% conversion rate**. Manipur's 2023 NCRB figures show **3,399 cases in a conflict category against
  1 in 2022**, a discontinuity that breaks any trend line. This is the single most important lawyering
  point in the dossier.
- **Two domain corrections for the master catalogue.** (1) The brief's `biharpolice.bihar.gov.in` **does
  not appear in any index** — the live hosts are **`police.bihar.gov.in`** (portal) and
  **`scrb.bihar.gov.in`** (statistics + FIRs). (2) NE sites move constantly: legacy hosts
  `nagapol.gov.in`, `sikkimpolice.nic.in`, `odishapolice.gov.in`, `assampolice.gov.in` and
  `arunpol.nic.in` are all still serving alongside their replacements. Record both; prefer the new.
- **Finest spatial granularity achievable in this domain: `police-station`** — but only in Bihar (FIRs),
  Sikkim (daily FIRs), Bhubaneswar–Cuttack (per-station pages) and possibly Meghalaya (crime search).
  Everywhere else the honest ceiling is **`district`, annual**.

---

## Per-state verdict and accessibility rating

Rated 1–5 on **data accessibility for our map** (granularity × freshness × coverage × ease).

| State | Rating | Justification |
|---|---|---|
| **Odisha** | **5** | The only complete stack in the region: state open-data subdomain with a Crime group, district-wise IPC/SLL on data.gov.in, a commissionerate site with per-police-station pages + maps + annual crime statistics, a "Know Your Police Station" lookup, an OGD police-station roster resource, FIR copy download and a citizen mobile app. Nothing else comes close. |
| **Bihar** | **4** | Uniquely holds **both** a district-wise annual series (*Crime in Bihar*, 2018–2020 confirmed) **and** a public all-FIR repository at police-station granularity refreshed daily. Docked one point: PDFs are unstructured, the FIR endpoint is an ASPX form, and the repository censors national-security / law-and-order / communal FIRs by design. |
| **Sikkim** | **4** | **Monthly Crime Review PDFs Jan 2023 → May 2025 plus a Daily FIR page** — the freshest regular crime series in all 12 states, beating every large state on cadence. Docked for: tiny population (single incidents swing rates), hash-based PDF filenames that force listing-page scraping, and unconfirmed district split. |
| **Meghalaya** | **4** | **14 years of district-wise data (2010–2023)** — the longest confirmed district series in the NE — plus per-district crime-chart PDFs, a Crime Search form, daily crime incidents and a published `/sitemap`. Docked because chart PDFs may be images (machine_readable could be 0) and only one district code is confirmed. |
| **Mizoram** | **3** | Three independent routes: Mizoram Police crime-statistics page (data into Dec 2024), Home Department `crsmizo` district crime figures in **HTML** (easier than anyone else's PDFs), and district SP pages. Docked hard because the police page splices **arrests** and **cases** across three incompatible windows — concatenating them would be an outright error. |
| **Assam** | **3** | Largest NE state, genuinely active web presence, a dedicated **Crime Data** page, FIR download, e-FIR and Seva Setu. But **two searches failed to surface a single year, table or file from inside the Crime Data page** — so its value is entirely unproven. Also runs four coexisting hosts, and the 2022 district reorganisation breaks series. |
| **Tripura** | **3** | A real **District wise Crime Data** page, and press-briefed 2025 totals (3,698 cases vs 4,033 in 2024) give us a rare **reconciliation target**. Docked for dual live domains, 4→8 district break in 2012, and political framing of the headline numbers. |
| **Nagaland** | **3** | **District-wise FIR reports for 8 districts** is the promising part. But the only crime-statistics page with visible years covers **2013–2015** — potentially decade-old data. AFSPA routing and a ~1.7% helpline-to-case conversion rate make the police series structurally incomplete. Resolves to 4 if `/fir-2/` is live and current. |
| **Jharkhand** | **3** | Carried almost entirely by one external asset: **Crimes in Ranchi** on data.gov.in, **updated 2025-02-17**, GODL-licensed and machine-readable — the freshest such resource in the region. The state's own `/crime-statement` page exists by title with **contents completely unknown**; one fetch moves Jharkhand to 2 or 4. |
| **West Bengal** | **2** | **Explicit negative finding.** The largest state in scope publishes **no standalone crime-statistics volume**. Its SCRB's described role is to prepare CII/ADSI returns *for NCRB* — data flows upward, never out. The anticipated Kolkata Police annual crime review was not substantiated. What exists is structural only: district `/PoliceStations` rosters and a station list. Effectively **NCRB-only**, capping WB at district/annual with 12–18 month lag. |
| **Arunachal** | **2** | A `crime_records.html` page exists by title with **entirely unknown contents**. Static legacy `.nic.in` site partly served over plain HTTP, citizen portal on a *different* namespace with at least one `comingsoon.htm` stub. 25+ districts mostly created post-2014, so any history is boundary-broken. AFSPA in Tirap/Changlang/Longding. |
| **Manipur** | **2** | No crime-statistics page found on the police site at all. The only figures route is the **Legislative Assembly's tabled administrative report** (`assembly.mn.gov.in`), and even that may carry only establishment and budget. Citizen portal is a `JSP Page` / `comingsoon.htm` stub. Sustained ethnic conflict since May 2023 means any 2023+ series is conflict-distorted, not ordinary crime. |

**Mean rating: 3.0.** Median 3. Only one state (Odisha) is ready to build on without preliminary RTI or
reconnaissance fetching.

---

## Source entries

Full field-complete records for all 44 sources are in
`research/sources/state-police-east-ne.jsonl`. This section gives the reading order and the load-bearing
detail; it does not duplicate every field.

### BIHAR

#### 1. Crime in Bihar (annual SCRB publication) — `state-police-east-ne-bihar-scrb-crime-in-bihar`

```
publisher   State Crime Records Bureau, Bihar Police, Sardar Patel Bhawan, Patna
landing     https://scrb.bihar.gov.in/
data        https://scrb.bihar.gov.in/images/Crime%20in%20Bihar.pdf   (2018)
            https://scrb.bihar.gov.in/images/CIB%2019.pdf             (2019)
            https://scrb.bihar.gov.in/images/cib_20.pdf               (2020)
granularity district · aggregate-count · annual · IPC+SLL · PDF
access      open-download   machine_readable 1   ingest_difficulty 4   priority 4
verification CITED
```

Three distinct year-files are indexed with titles confirming the series. The index snippet states data is
collected via **34 proforma from 48 districts/units** for the calendar year.

Caveats that matter: the "48 districts/units" figure **mixes revenue districts with railway and special
units**, so it is not a clean 38-district join. SCRB's own note says the data is **"not for legal use"**
and certified figures must be sought from districts/units. Only 2018–2020 surfaced — the series may be
discontinued or later years may sit at unindexed paths. Guess forward by incrementing `cib_NN.pdf`.

#### 2. SCRB Bihar public FIR repository — `state-police-east-ne-bihar-scrb-public-fir-repository` ★

```
landing     https://scrb.bihar.gov.in/View_FIR.aspx
data        https://scrb.bihar.gov.in/FIRiew.aspx
granularity police-station · fir-record · daily · IPC+SLL
access      scrape   machine_readable 2   ingest_difficulty 4   priority 5
```

**The finest-grained published record series found anywhere in the 12 states.** Individual FIRs
attributable to a named police station, refreshed daily, published under Supreme Court and High Court
direction.

Three things make it dangerous as well as valuable:

1. **Systematic exclusions by design.** FIRs debarred by court order, FIRs touching national security,
   and FIRs that "may adversely affect Law & Order and communal situations" are **not uploaded**. That
   censors exactly the categories a safety map most wants, in a non-random way.
2. **An FIR is a report, not a finding.** No outcome, no conviction; withdrawn and false cases are not
   retracted from the page.
3. **Named-accused privacy exposure.** Volume-scraping a state FIR repository and republishing it has
   obvious defamation and privacy consequences for people who have not been convicted.

Mechanically: ASPX postback form, so ViewState/EventValidation must be replayed; results almost certainly
require district + police station + date range, so there is **no single bulk endpoint**. FIR text is
Hindi/Devanagari and frequently a scanned image, needing OCR plus address parsing before geocoding.

#### 3. Bihar Police portal — `state-police-east-ne-bihar-police-portal`

`https://police.bihar.gov.in/` — online FIR, missing persons, ERSS-112. **Domain correction: the brief's
`biharpolice.bihar.gov.in` appears in no index.** 12 ranges of 2–5 districts each. Patna Police has no
separately indexed statistics publication.

### JHARKHAND

#### 4. Jharkhand Police Crime Statement — `state-police-east-ne-jharkhand-crime-statement`

`https://www.jhpolice.gov.in/crime-statement`. **The highest-value unknown in this dossier.** The path
name is the *only* evidence of content — no table names, years or file sizes were observable. A single
fetch resolves whether Jharkhand rates a 2 or a 4. RTI fallback: PIO, SCRB Jharkhand, PHQ, Dhurwa,
Ranchi 834004.

#### 7. Crimes in Ranchi (Smart Cities Mission / OGD) — `state-police-east-ne-ranchi-smartcity-crimes-ogd` ★

`https://www.data.gov.in/catalog/crimes-ranchi` — released under NDSAP by MoHUA Smart Cities Mission,
**updated 2025-02-17**, GODL-India, CSV/XLSX/JSON. **The freshest machine-readable crime resource found
for the whole region** and the highest ingest-value-per-effort item here. Caveat: Smart Cities datasets
are notoriously uneven — many are a single year of city totals despite an inviting title — and they are
usually supplied by the SPV, not the police, so definitions may not match SCRB or NCRB heads.

Also: #5 citizen portal (`citizen.jhpolice.gov.in`, 9 services, login), #6 JOFS e-FIR
(`jofs.jhpolice.gov.in` — hostname appeared only inside a snippet, one degree weaker than everything
else here).

### WEST BENGAL

#### 11. WB state crime statistics — **NEGATIVE FINDING** — `state-police-east-ne-wb-scrb-crime-statistics-rti`

**State this plainly in the master catalogue: West Bengal, the largest state in scope, appears to publish
no standalone crime-statistics volume.** Two targeted searches over `wbpolice.gov.in` surfaced only
organisation/functions PDFs (`Abou2019350001.pdf`, `Abou2021350002.pdf`), a gazette (`Poli2019040039.pdf`)
and `Publ2022290006.pdf` — no crime-statistics title, no "Crime in West Bengal" analogue to Bihar's.

WB SCRB's described role is to prepare **CII and ADSI returns *for* NCRB** — the data exists internally
and is transmitted upward but is not separately disclosed. Consequence: **for WB, NCRB *Crime in India*
is effectively the only published source**, capping granularity at district and cadence at annual with a
12–18 month lag.

This cannot be ruled out absolutely — the sandbox could not fetch `wbpolice.gov.in`, and a Publications
menu may exist that the index did not surface. Marked `UNVERIFIED` rather than `CITED` for that reason.

#### 10. Kolkata Police — `state-police-east-ne-kolkata-police`

```
landing  https://kolkatapolice.gov.in/          (EGRESS_BLOCKED on direct fetch 2026-09-19)
         https://kolkatapolice.gov.in/new-crime-trends/
         https://crskp.kolkatapolice.org/       (Criminal Record System — .org host, likely authenticated)
         https://www.kolkatapolice.gov.in/images/docs/rti.pdf
         http://www.kolkatapolice.gov.in/localpolice.asp   (legacy — likely the station roster)
```

**The brief expected "Kolkata Police at a glance"-style annual crime reviews. Two separate searches
failed to surface any such publication. Treat the historical-publication premise as unconfirmed and
probably lapsed.**

⚠️ **Do not mistake "New Crime Trends" for crime data.** It is an advisory/awareness page about emerging
fraud types, not a statistical series. Site is a mix of legacy ASP and modern WordPress; legacy pages may
be unmaintained. 91 police stations across 10 divisions (North, North Suburban, Central, Eastern
Suburban, South, Port, South East, South Suburban, East, Bhangar).

#### 9. WB district `/PoliceStations` rosters — `state-police-east-ne-wb-district-police-station-rosters`

`https://birbhumpolice.wb.gov.in/PoliceStations` and `https://barrackporepolice.wb.gov.in/PoliceStations`
confirmed. **The `/PoliceStations` path is confirmed on two hosts only and is EXTRAPOLATED to the other
~26.** Host naming is not uniform (`birbhumpolice` vs `barrackporepolice`) so the host list must be
*discovered* from `wbpolice.gov.in`'s district links, not generated. This is the only route to a roster
for WB's 516 stations, and it is the base layer any WB map needs even when the counts come from NCRB.

### ODISHA — the strongest state in scope

#### 15. Bhubaneswar–Cuttack Police Commissionerate — `state-police-east-ne-bbsr-cuttack-commissionerate-crime-statistics` ★★★ BEST SEED LEAD

```
crime stats   https://bhubaneswarcuttackpolice.gov.in/crime-statistics/
annual 2022   https://bhubaneswarcuttackpolice.gov.in/crimecounter/annual-crime-statistics-2022/
stations      https://bhubaneswarcuttackpolice.gov.in/know-your-police-station/
              https://bhubaneswarcuttackpolice.gov.in/policestations/<slug>/   (cantonment, infocity,
              cyber-crime-and-economic-offence, and a numeric /policestations/764/)
maps          https://bhubaneswarcuttackpolice.gov.in/maps/
legacy        https://bhubaneswarcuttackpolice.gov.in/crimestatistics.php
granularity   police-station · aggregate-count · annual · access open-download · priority 5
```

**The only source in the 12 states that combines per-police-station pages, a maps section and a named
annual crime-statistics series on one host** — i.e. the closest existing analogue to police.uk geometry
anywhere in this region. Build the regional prototype here.

Risks: `/maps/` might be a static image rather than a web map, which would halve the value. Only the 2022
volume surfaced by title; other years are implied by the URL pattern but unconfirmed. Two generations of
the same section are live (`/crime-statistics/` and `/crimestatistics.php`). Station count is disputed in
sources: **43 vs 60**. Covers ~14 lakh population, so it cannot anchor a statewide map.

#### 16 & 17. Odisha open data — `...odisha-open-data-crime`, `...bhubaneswar-police-station-details-ogd`

- `https://odisha.data.gov.in/dataset-group-name/Crime%20rate` — **Odisha is the only state in scope
  confirmed to run its own open-data subdomain with a crime group.**
- `https://www.data.gov.in/catalog/district-wise-crime-cases-ipc-and-sll-reported-odisha` — district-wise
  IPC/SLL, GODL-India.
- `https://www.data.gov.in/resource/bhubaneswar-police-station-details` — **if this carries lat-lon it is
  the only ready-made geocoded police-station roster in the 12 states.** A 10-minute test with a large
  payoff; check it first. (Mirrored at `kerala.data.gov.in` — state OGD subdomains cross-serve the
  national catalogue; not a separate source.)

Caveat on both: OGD crime catalogues are frequently **derived from NCRB** rather than from SCRB directly,
so they may repackage *Crime in India* with the principal-offence-rule distortion intact. Also a
30-revenue-district vs 32-police-district mismatch will bite on joins.

#### 13. Know Your Police Station — `state-police-east-ne-odisha-know-your-police-station`

`https://police.odisha.gov.in/en/sun/knowyourstation`. **Phase 2 should open devtools on this page before
anything else in Odisha.** A locality→station lookup almost always has a JSON backend; if so, that is the
closest thing to an API found in this entire region.

Also: #12 portal (612 stations / 32 police districts / 7 ranges; legacy `odishapolice.gov.in` Drupal
`/main/?q=node/N` still live), #14 FIR copy (`citizenportal-op.gov.in/citizen/FIR_Copy.aspx`,
`services-op.odisha.gov.in/Citizen/AboutFIRCopy.aspx` — fetch *AboutFIRCopy* first, it documents required
inputs and settles whether enumeration is possible). **The `Sahayata` Android app**
(`odishapolice.citizen.odishacitizenapp`) offers FIR copy download and service tracking — **decompiling
its API calls is a legitimate Phase 2 route to an undocumented JSON endpoint.**

### SIKKIM — the region's surprise

#### 18. Monthly Crime Review — `state-police-east-ne-sikkim-monthly-crime-review` ★★

```
listing  https://police.sikkim.gov.in/visitor/monthlycrimereview
sample   https://police.sikkim.gov.in/mcreviewdoc/mcreviewdoc-3h6o8ZOQQyaOasdxpaznWyA4jvsyPAJsvOcIxTzg.pdf
cadence  MONTHLY · Jan 2023 → May 2025 confirmed · lag 1-2 months · priority 5
```

Six PDFs indexed with titles `1 MONTHLY CRIME REVIEW FOR THE MONTH OF <MONTH>-<YEAR>`: JANUARY-2023,
MAY-2023, JUNE-2023, JANUARY-2024, MARCH-2024, MAY-2025. Content includes total crime split IPC /
Non-IPC plus sections on new-age and cyber crime.

**Monthly cadence is the headline — the freshest regular crime series in all 12 states, beating every
large state here.** Sikkim, population ~0.7m, is the accidental star of this region.

Three hard constraints: **filenames are random 40-char hashes with no date in the path, so you cannot
construct URLs** — the listing page is the only index and must be scraped for every link. District split
is **inferred, not confirmed** (may be state-total only). Small-numbers problem is acute: a single
incident swings a rate, so **suppression thresholds are essential before mapping**. Pre- and post-BNS
volumes sit in one series with no flagged break at 1 July 2024. Indexed months are sparse, so continuity
is unproven.

#### 19. Daily FIR — `state-police-east-ne-sikkim-daily-fir` ★★

`https://police.sikkim.gov.in/visitor/fir`. **Act on this early.** Daily-FIR pages commonly show only a
rolling 7–30 day window with no back catalogue. If that is the case here, the series must be harvested
*forward* from the day you start — **every day of delay is data permanently lost**. Together with Bihar's
`View_FIR.aspx` this is one of only two FIR-level daily series in the region, and by far the easier of
the two to ingest.

Legacy host `sikkimpolice.nic.in` still indexed; control-room contact `pcr@sikkimpolice.nic.in` is still
on the old domain.

### ASSAM

#### 21. Assam Police Crime Data — `state-police-east-ne-assam-crime-data`

`https://police.assam.gov.in/information-services/crime-data`. **A dedicated Crime Data page provably
exists, but two searches failed to surface any year, table name or file from inside it.** Granularity and
cadence are inferred, not observed — **the largest single unknown for Assam**. Assam is the largest NE
state and the only one with a genuinely active police web presence, so resolving this page's contents
changes the regional picture more than any other single fetch.

⚠️ **Four coexisting hosts** — do not assume one canonical domain: `police.assam.gov.in` (informational),
`assampolice.assam.gov.in` (citizen portal), `polcitizen.assam.gov.in` (citizen portal), legacy
`assampolice.gov.in/districts/index.php`. Also: the **2022 district reorganisation** merged several
districts, so any multi-year series has a boundary break around 2022–23. Check whether state figures
include Guwahati's separate city arrangement.

#### 22. FIR Download — `state-police-east-ne-assam-fir-download`

`https://assampolice.assam.gov.in/citizen/FIRDownload.aspx`. **Useful fingerprint:** the indexed page
*title* is "Government of India, Ministry of Home Affairs, National Crime Records Bureau" — i.e. this is
**boilerplate NCRB CCTNS software**, not an Assam-specific build. Searching other states for that same
title is a cheap way to locate their CCTNS FIR endpoints. Contact `citizensupport@assampolice.assam.gov.in`
/ (0361)-2460303.

Also #23: e-FIR and Seva Setu confirmed real (the brief's lead checks out) but they are **intake**
channels, not disclosure channels, and e-FIR is typically restricted to vehicle/mobile/property theft —
not a representative crime sample even if data leaked.

### MEGHALAYA — the best-documented NE police site

#### 34. Statistics (district-wise 2010–2023) — `state-police-east-ne-meghalaya-statistics` ★★

`https://megpolice.gov.in/statistics` + per-district charts at
`https://megpolice.gov.in/crime/Crime_Chart_WJH.pdf`.

**14 years of district-wise data is the longest confirmed district-level series found in the NE** — not
the result the brief anticipated.

Caveats: the per-district files are **charts**, and a chart PDF may be an image with no extractable
table — potentially `machine_readable: 0`, not 1. **Test one PDF for extractable text before budgeting
ingest time for the rest.** Only the `WJH` (West Jaintia Hills) code is confirmed; other district codes
(EKH, WKH, SKH, RB, EJH, WGH, EGH, SGH, NGH, SWGH, SWKH) are **extrapolated**. Separately, the site's
older "annual reports" are 2009-10/2010-11/2011-12, a long-dead series — and some indexed "annual
reports" are **CHILDLINE India** reports, not police reports. Do not conflate.

#### 35. Crime Search + daily Crime Incident — `state-police-east-ne-meghalaya-crime-search`

`https://megpolice.gov.in/crimes-search`, with a published **`/sitemap`** (unusually helpful — use it as
the crawl entry point). A public crime-search form usually accepts GET parameters, which would make it
**the nearest thing to a query API in the NE**. Worth testing early. `unit_of_record` is recorded as
`incident-point` optimistically — "Daily Crime Incident" could equally be a narrative bulletin with no
structured location.

### TRIPURA

#### 37. District wise Crime Data — `state-police-east-ne-tripura-district-crime-data`

`https://police.tripura.gov.in/district_crime_data`. Real and titled as district-split.

**Rare and valuable: we have a reconciliation target.** Press reporting quotes Tripura Police annual data
released in early 2026 — **2025: 3,698 total cases vs 2024: 4,033**; crimes against women 665 vs 724;
rape 169 vs 180; property offences 293 vs 349; NDPS up 11.06%; road accidents 527 vs 578. **Whatever we
scrape for Tripura 2024/2025 must reconcile to those totals.** Almost nothing else in this region offers
a cross-check.

Caveats: **dual live domains** (`police.tripura.gov.in` and `tripurapolice.gov.in`) — determine which is
canonical first. Districts went 4→8 in 2012. Headline figures reach the public via CM/DGP statements
first, and the political framing ("lowest crime rate in 20 years") is a reason for caution about
completeness, not confidence.

### MIZORAM

#### 32. Home Department consolidated district crime figures — `state-police-east-ne-mizoram-crsmizo-district-crime` ★

`http://crsmizo.mizoram.gov.in/administrative/index.php?page=administrative_crime_district&title=Crime+Figure+-+Home+Department`

**District-level and HTML rather than PDF — better for us than Mizoram Police's own page. Ingest this in
preference.** The real key is `page=administrative_crime_district`; the `title=` parameter is cosmetic.
Served over plain HTTP. Home Department figures and Mizoram Police figures **may not reconcile** — check
before combining. Districts went 8→11 in 2019 (Khawzawl, Saitual, Hnahthial), breaking series.
Companion: `http://mizoramdata.mizoram.gov.in/` (DES, year-wise and district-wise crime + CAW).

#### 31. Mizoram Police Crime Statistics — `state-police-east-ne-mizoram-police-crime-statistics`

`https://police.mizoram.gov.in/crime-statistics/` and `/page/crime-statistics` (two generations live).

⚠️ **The series is discontinuous by construction.** Three unrelated blocks: arrest analysis
**Sep 2023–Dec 2024**, comparative crime figures **2020–2022**, comparative IPC figures **2009–2019**.
Different units (**arrests vs cases**), different windows, different taxonomies. **Do not concatenate
them.** And mapping *arrests* as *crime* would actively mislead — arrests measure policing activity, not
incidence.

#### 33. District SP pages — `state-police-east-ne-mizoram-district-sp-crime-statistics`

`https://splunglei.mizoram.gov.in/page/crime-statistics` is the **only confirmed host**; the
`sp<district>.mizoram.gov.in` pattern across 11 districts is **extrapolated from a single observation**.
Cheap to test (resolve candidate hostnames, GET `/page/crime-statistics` on each) and potentially
delivers district coverage for the whole state in one pass. Good Phase 2 experiment.

### NAGALAND

#### 27. District-wise FIR reports — `state-police-east-ne-nagaland-district-fir-reports`

`https://police.nagaland.gov.in/fir-2/` — FIR reports enumerated for **Dimapur, Kiphire, Kohima,
Longleng, Mokokchung, Mon, Peren, Wokha** (8 of 16+ districts, so coverage is partial or the index is).
**If these are genuine per-district FIR listings, Nagaland jumps from 2 to 4.** Worth an early fetch.

#### 26. Crime Windows — `state-police-east-ne-nagaland-crime-windows`

`https://police.nagaland.gov.in/crime-windows/`, breakdown by crime head under IPC and under Local and
Special Laws — a **category axis with no evidence of a district axis**, hence `geo_granularity: state`.

⚠️ **Staleness warning:** the only crime-statistics page with years visible in its URL covers
**2013–2015**. If Crime Windows is not separately maintained, Nagaland's published crime data is a decade
old. Legacy `http://nagapol.gov.in/` still serving alongside `https://police.nagaland.gov.in/`.
SCRB contact: `scrb-ngl@nic.in`, PHQ, P.R. Hill, Kohima 797001.

### MANIPUR

#### 29. Legislative Assembly administrative report — `state-police-east-ne-manipur-police-administrative-report` ★

`https://assembly.mn.gov.in/user/pages/files/administrative-reports/Police%20and%20Others.pdf`
— "THE 2025 - 2026 POLICE DEPARTMENT GOVERNMENT OF MANIPUR".

**This entry establishes a pattern worth applying region-wide:** where a police department publishes
nothing, the **state Legislative Assembly's tabled administrative reports and assembly question answers**
are often the only public crime figures — and they are *already public*, cost nothing, and are faster
than RTI. The `/administrative-reports/` directory is worth listing for other years and departments.

Risk: administrative reports often carry only establishment, budget and staffing, with **no crime tables
at all**. Bundled file ("Police and Others") mixes departments.

#### 28 & 30. Police portal and citizen portal

`manipurpolice.gov.in` has **no crime-statistics page** that searching could find. It does have per-district
and **per-police-station pages** (Lamphel PS, Kasom Khullen PS), so **a Manipur station roster is buildable
even though crime counts are not published** — but the WordPress site uses unrewritten query-string URLs
(`?page_id=`, `?p=`, `?cat=`, `?attachment_id=`), which are fragile and unenumerable without crawling.
The citizen portal (`mnpcitizenportal.mn.gov.in`) surfaced only as a **`JSP Page` / `comingsoon.htm`
stub** — a default title plus a placeholder path indicates an unconfigured CCTNS deployment.

**Context that overrides everything else for Manipur:** sustained ethnic conflict since May 2023,
President's Rule in periods, AFSPA. NCRB recorded **3,399 cases in a conflict category for 2023 against 1
in 2022** — a discontinuity so large the series is simply not continuous. Any 2023+ Manipur data is
conflict-distorted, not ordinary crime.

### ARUNACHAL PRADESH

#### 24. Crime Records — `state-police-east-ne-arunachal-crime-records`

`https://arunpol.nic.in/crime_records.html`. A page exists by title; **its contents are entirely
unknown** — no year, table or file surfaced. Static `.html` on the legacy `.nic.in` namespace, root
served over `http://` in the index — fragile and possibly unmaintained. Domain split: informational site
on `arunpol.nic.in`, citizen portal on `arunpol.gov.in`. 25+ districts mostly created post-2014, so
severe boundary breaks. **AFSPA in Tirap, Changlang, Longding and Assam-border areas** — insurgency
incidents there route to MHA and will be absent or reclassified in police crime records.

Citizen portal (#25) has at least one `comingsoon.htm` placeholder and an `http://` login URL — if that
is not an index artefact it is a real transport-security problem for citizens.

### CROSS-CUTTING

#### 42. NCRB reporting reliability for the NE — `state-police-east-ne-ncrb-ne-reporting-reliability` ★★★

**This answers the brief's NCRB question and is the most important lawyering content in the dossier.**

Sources: ORF *Measuring Crime in India: The Limits of Statistical Compilation*; CJP *Counting Crimes,
Discounting Justice: The NCRB's statistical blind spots*; FACTLY; Morung Express; Assam Tribune; arXiv
2112.07314.

**Do NE states report to NCRB? Yes — the data arrives.** Nagaland's 2021→2023 figures were published by
NCRB and reported on. The problem is not transmission, it is what the numbers mean:

| Gap | Effect on our map |
|---|---|
| NCRB does no independent review and no primary research — it compiles what states send | No error bars, no audit trail |
| **Only cognizable crimes** counted; non-cognizable excluded entirely | Whole categories invisible |
| **Principal offence rule** — only the most serious head per FIR is kept | Systematically deflates lesser heads |
| NE reporting rates are very low: Nagaland helpline **200,000+ calls since 2016 → ~3,400 cases (~1.7%)** | Low NE rates are an artefact of *reporting*, not safety |
| Manipur 2023: **3,399 cases vs 1 in 2022** in a conflict category | Trend lines break entirely |
| Insurgency violence in AFSPA areas routes to **MHA**, not NCRB | Violent states render as peaceful |

**Conclusion: NE crime rates must never be rendered on our map as "safe" without an explicit
reporting-rate caveat.** A choropleth that colours Nagaland green because its per-capita reported rate is
low is not merely imprecise — it is affirmatively wrong and defamatory in the opposite direction.

#### 38 & 39. The AFSPA / insurgency overlap — SATP and MHA

- `https://www.satp.org/datasheet-terrorist-attack/fatalities/india-insurgencynortheast` — state-wise NE
  datasheets for all seven states, maintained, weekly-ish. **`satp.org` is NOT on the egress blocklist,
  so unlike the `.gov.in` sources it should be fetchable in Phase 2.** Media-derived, so coverage tracks
  media attention and undercounts rural incidents; partisan-framing concerns are routinely raised about
  ICM's classifications; terms of use are restrictive about redistribution.
- MHA Annual Report NE figures (via secondary reporting): **2023 — 243 incidents (Manipur 187, Nagaland
  35, Arunachal 13, Assam 8); 2024 to November — 266 (Manipur 203, Nagaland 40, Arunachal 16, Assam 6,
  Meghalaya 1).** ⚠️ **The MHA Annual Report itself has no confirmed URL** — the recorded URLs are the
  CCTNS pages that surfaced. It must be located in Phase 2; do not guess the path.

**Design rule: never merge SATP or MHA conflict counts into the general crime layer.** Keep them as a
separate layer with its own legend, or the map conflates insurgency with burglary.

#### 40. CCTNS / Digital Police Portal — the definitive "no API" finding

`https://digitalpolice.gov.in/DigitalPolice/AboutUs`,
`https://www.digitalpolicecitizenservices.gov.in/centercitizen/login.htm`. Launched 2017-08-21; 34
states/UTs have citizen portals.

**The 11 searches and 44 reports are for police and investigating agencies only (CBI, IB, ED, NIA). There
is no public bulk interface and no public API.** This is the system underlying *every* state citizen
portal in this dossier — which is why Bihar, Odisha, Assam, Arunachal, Jharkhand, Meghalaya, Manipur and
Nagaland portals all behave identically. Understanding it once explains all eight.

#### 41. ICCC / Smart City command centres — **NEGATIVE FINDING, as the brief asked**

**ICCCs are operational consoles for city staff — live CCTV, sensor feeds, alerts on a wall display — not
public data products. No public crime dashboard exists for Bhubaneswar, Ranchi, Guwahati, Kolkata or
Patna.** CCTNS-to-ICCC integration is described at policy level (PIB PRID=1947455) as an intention and a
capability, with no evidence of resulting public disclosure. Even where an ICCC ingests crime records, the
output is a wall display, so there is nothing to scrape. The city-details URL pattern
`iccc.smartcities.gov.in/icc/city-details/<32-hex-id>` is confirmed, but **the ids for Bhubaneswar, Ranchi
and Guwahati were not found**.

**The useful residue is `https://smartcities.data.gov.in/`** — the open-data portal SPVs publish to, and
the actual origin of *Crimes in Ranchi* and *Bhubaneswar: Police Station Details*. **Chase the data
portal, not the command centre.**

#### 43. Indiastat — validation set only

Crime-and-law pages exist for all 12 states, with district-level IPC-crime pages for Jharkhand and
Mizoram. **Derivative** — repackages NCRB and state statistical handbooks, adding back-series convenience,
not new information; every NCRB caveat passes straight through. **Licence explicitly restricts
redistribution — we could validate our pipeline against it but almost certainly cannot republish its
tables. Get legal sign-off before any use.** Useful as a cheap way to discover *which* district series
exist before spending RTI effort.

---

## Granularity reality check

What we want versus what exists. Blunt version.

| Geographic level | Where it actually exists in this region | Period | Refresh | Formats |
|---|---|---|---|---|
| `address` / `point` | **Nowhere.** No source in 12 states geocodes incidents. | — | — | — |
| `beat` / `ward` | **Nowhere.** No beat- or ward-level crime counts found. | — | — | — |
| `police-station` (incidents) | **Bihar** FIR repository; **Sikkim** Daily FIR | unknown → now | daily | ASPX/HTML, scanned PDF |
| `police-station` (counts) | **Bhubaneswar–Cuttack** commissionerate only | ~2022 | annual | HTML/PDF |
| `police-station` (roster/geometry) | Odisha (`knowyourstation`, OGD resource), WB district sites, Manipur, Bhubaneswar | current | irregular | HTML, CSV |
| `district` | Bihar, Odisha, Meghalaya (2010–2023), Mizoram, Tripura, Nagaland(?), Assam(?), Arunachal(?) | 2009 → 2024 | annual | **PDF dominant** |
| `district` (monthly) | **Sikkim only** — and the district split is unconfirmed | 2023-01 → 2025-05 | **monthly** | PDF |
| `city` | Ranchi (OGD, updated 2025-02-17), Bhubaneswar | ~2024 | irregular | CSV/XLSX/JSON |
| `state` | All 12, via NCRB *Crime in India*; Nagaland/Mizoram own pages | long series | annual, 12–18 mo lag | PDF |

**The gap, stated plainly.** The product intent is "is this neighbourhood safe to rent in or walk through
at night?" That requires sub-district, ideally sub-ward, geography and a refresh measured in weeks.

**This region offers that in exactly three places: Bihar's FIRs, Sikkim's daily FIRs, and one
commissionerate covering 14 lakh people in Odisha.** Everywhere else, the honest ceiling is a
**district-level annual count in a PDF** — which can tell a user which *district* has more reported
crime, and nothing whatsoever about a neighbourhood.

Three further degradations apply on top:

1. **Nothing is geocoded.** Even police-station-level data has no coordinates. The one possible exception
   (`bhubaneswar-police-station-details`) is unverified.
2. **Almost nothing is machine-readable.** Of 44 entries, exactly **three** rate ≥4 on
   `machine_readable`, and all three are data.gov.in resources, not police outputs.
3. **Boundary instability is endemic.** Assam 2022 reorg, Mizoram 8→11 in 2019, Tripura 4→8 in 2012,
   Arunachal 25+ districts mostly post-2014, Odisha 30-revenue vs 32-police districts, Bihar's 48
   "districts/units" mixing revenue and railway units. **No multi-year district series in this region
   joins cleanly to a single boundary set.**

---

## Blockers and how to get past them

### 1. Research-environment egress block (blocks verification, not the pipeline)

The `.gov.in` namespace and `archive.org` are blocked by this sandbox's egress policy, so **nothing here
is fetch-verified**. Fix: run ~30 targeted GETs from an Indian or unrestricted network. This is the
single highest-value Phase 2 action and it is cheap. Priority fetch list is in the recommendations below.

### 2. PDF-first publishing (the real, structural blocker)

**The genuine blocker in this domain is that Indian state police publish PDFs, not data.** Of 44 entries,
three are machine-readable and none of those three is a police output. Mitigations, in order of
preference:

- Prefer **HTML sources over PDF** wherever both exist: Mizoram's `crsmizo` HTML tables beat Mizoram
  Police's page; WB district rosters are HTML; commissionerate station pages are HTML.
- **Test extractability before budgeting.** Meghalaya's `Crime_Chart_*.pdf` may be images. One test
  decides whether that state costs 2 days or 2 weeks.
- Budget **OCR + Devanagari/regional-script handling** for Bihar.

### 3. Hash-based and opaque file paths (blocks enumeration)

Sikkim's `mcreviewdoc-<40-char-hash>.pdf` and WB's `/writereaddata/wbp/<prefix><digits>.pdf` cannot be
constructed or enumerated — **there is no directory listing**. You must scrape the listing/HTML pages for
every link, and re-scrape to discover new ones. Design the harvester around link discovery, not URL
generation.

### 4. ASPX postback forms and CAPTCHAs (blocks bulk FIR access)

Bihar `View_FIR.aspx`, Odisha `FIR_Copy.aspx`, Assam `FIRDownload.aspx` are all CCTNS boilerplate.
ViewState/EventValidation must be replayed; most require district + station + date or FIR number.
**If FIR *number* is mandatory, enumeration is impossible** — fetch Odisha's `AboutFIRCopy.aspx` first,
because it documents the required inputs and settles the question for the whole CCTNS family at once.

### 5. Rolling windows (data loss that compounds daily)

Sikkim's Daily FIR and Meghalaya's daily Crime Incident may retain only days or weeks. **Every day
without a harvester is history permanently lost.** Stand these up before the polished work.

### 6. Domain churn (the brief predicted this correctly)

Legacy and current hosts are simultaneously live across the region: `nagapol.gov.in` ↔
`police.nagaland.gov.in`; `sikkimpolice.nic.in` ↔ `police.sikkim.gov.in`; `odishapolice.gov.in` ↔
`police.odisha.gov.in`; `assampolice.gov.in` ↔ `police.assam.gov.in` (+2 citizen hosts);
`tripurapolice.gov.in` ↔ `police.tripura.gov.in`; `arunpol.nic.in` ↔ `arunpol.gov.in`. **No dead link was
confirmed dead** (the sandbox cannot distinguish dead from blocked) — but several are `http://`-only or
legacy CMS generations. Record both hosts per force; monitor for drift; never hardcode one.

### 7. Legal and ethical exposure (the blocker that should slow us down)

Bihar's and Sikkim's FIR feeds name **accused persons who have not been convicted**. Publishing them on a
map is a defamation and privacy problem, not merely a licensing one. Separately, **most sources state no
licence at all** (`unstated`) — absence of a licence is not permission. Indiastat explicitly forbids
redistribution. **Get legal sign-off on the FIR layers before any public release**, and consider
publishing only aggregated counts per station rather than individual records.

---

## Seed Leads (unconfirmed but probably real)

1. **A hidden JSON endpoint behind Odisha's "Know Your Police Station."** Locality→station lookups almost
   always have an AJAX backend. *Next step:* open devtools on
   `police.odisha.gov.in/en/sun/knowyourstation`, watch XHR. This would be the only real API in the region.
2. **The `Sahayata` Android app's API** (`odishapolice.citizen.odishacitizenapp`). *Next step:* pull the
   APK, decompile, extract endpoint URLs and auth scheme. A documented mobile backend is worth more than
   any scrape.
3. **Meghalaya district chart PDFs beyond `WJH`.** *Next step:* fetch `megpolice.gov.in/sitemap` (it
   exists) and enumerate `/crime/Crime_Chart_*.pdf` rather than guessing codes.
4. **Mizoram's per-district SP sites.** *Next step:* resolve `spaizawl`, `spchamphai`, `spkolasib`,
   `spmamit`, `spserchhip`, `spsaiha`, `spkhawzawl`, `spsaitual`, `sphnahthial` `.mizoram.gov.in` and GET
   `/page/crime-statistics`.
5. **Later years of *Crime in Bihar*.** *Next step:* try `scrb.bihar.gov.in/images/cib_21.pdf` through
   `cib_25.pdf`; if 404, ask the SCRB Statistical Cell, Sardar Patel Bhawan, Patna.
6. **Bhubaneswar–Cuttack annual volumes beyond 2022.** *Next step:* try
   `/crimecounter/annual-crime-statistics-2023/`, `-2024/`, `-2025/`.
7. **Legislative-assembly administrative reports for every thin state.** Proven to work for Manipur.
   *Next step:* check `assembly.<state>.gov.in` (and assembly question answers) for **West Bengal,
   Arunachal, Nagaland** before spending any RTI effort — this material is already public and free.
8. **A Kolkata Police station roster at the legacy `localpolice.asp`.** *Next step:* fetch
   `http://www.kolkatapolice.gov.in/localpolice.asp`; likely the 91-station list with division mapping.
9. **An Odisha SCRB "Crime in Odisha" annual volume.** Odisha has an SCRB with a statistical cell but no
   annual volume surfaced — given everything else Odisha publishes, its absence is more likely a search
   gap than a real gap. *Next step:* crawl `police.odisha.gov.in/en/sun/ourbrnchesinner/state-crime-records-bureau-bhubaneswar`
   for a publications link. *(The search budget was exhausted before this could be tested.)*
10. **Assam SCRB district-wise series behind the Crime Data page.** *Next step:* fetch
    `police.assam.gov.in/information-services/crime-data` — the highest-information single fetch in the NE.
11. **The MHA Annual Report PDF.** Path is **unconfirmed**; likely under `mha.gov.in/en/documents/annual-reports`.
    *Next step:* browse, do not guess. English and Hindi editions exist.
12. **`data.gov.in` resource API keys for the three relevant resources.** *Next step:* register for a free
    API key, then resolve resource-ids for `crimes-ranchi`, `district-wise-crime-cases-ipc-and-sll-reported-odisha`
    and `bhubaneswar-police-station-details`.

---

## Phase 2 recommendations

**Ranked. Steps 1–3 are hours of work and decide most of the regional plan.**

**Tier 0 — reconnaissance (do first; ~30 GETs from an unrestricted network)**

1. **Fetch the six "unknown contents" pages.** In order of information gain:
   `police.assam.gov.in/information-services/crime-data` → `jhpolice.gov.in/crime-statement` →
   `police.tripura.gov.in/district_crime_data` → `police.nagaland.gov.in/fir-2/` →
   `megpolice.gov.in/statistics` → `arunpol.nic.in/crime_records.html`.
   These six fetches re-rate five states and cost under an hour.
2. **Test `data.gov.in/resource/bhubaneswar-police-station-details` for lat-lon columns.** Ten minutes; if
   it has coordinates it is the region's only ready-made geocoded roster.
3. **Determine retention windows on Sikkim Daily FIR and Meghalaya Crime Incident.** If rolling, start
   harvesting *the same day* — this is the only item where delay destroys data.

**Tier 1 — build the prototype (highest granularity per unit of effort)**

4. **Bhubaneswar–Cuttack commissionerate.** Crawl `/policestations/` for station slugs, pair with
   `/crime-statistics/` and `/maps/`. **This is the police.uk-shaped prototype.** One city, real
   per-station geometry, real annual counts.
5. **Sikkim end-to-end.** Scrape the Monthly Crime Review listing for all `/mcreviewdoc/` links, parse the
   PDFs, and run the Daily FIR harvester. Smallest state, cleanest pipeline, **monthly cadence** — the
   best place to prove the temporal side of the product. Apply suppression thresholds from day one.
6. **The three data.gov.in resources** (Ranchi crimes, Odisha district IPC/SLL, Bhubaneswar stations) via
   the documented resource API. The only genuinely machine-readable inputs in the region.

**Tier 2 — broaden coverage**

7. **Meghalaya** (`/sitemap` → `/statistics` → district charts → `/crimes-search` GET-parameter probe) —
   14 years of district data and the NE's best-documented site.
8. **Mizoram via `crsmizo` HTML** (not the police PDF page), then test the `sp<district>` hostname pattern.
9. **Bihar *Crime in Bihar* PDFs** — district-wise annual backbone. OCR + Devanagari pipeline. Defer the
   FIR repository until legal sign-off (step 12).
10. **Tripura**, reconciling scraped totals against the published 3,698 / 4,033 figures.
11. **Police-station rosters as a standalone base layer**: Odisha `knowyourstation`, WB district
    `/PoliceStations` hosts, Manipur `?p=` station pages, Kolkata `localpolice.asp`. Geocode separately.
    **This base layer is worth building even where crime counts never arrive** — it gives the map its
    geometry and it is the prerequisite for any later RTI data to be mappable.

**Tier 3 — slow tracks, start the clock early**

12. **Legal review of FIR-level publication** (Bihar, Sikkim) before ingesting at volume. Recommend
    publishing aggregated per-station counts, not individual named records.
13. **Assembly-report sweep** for WB, Arunachal, Nagaland — free, public, faster than RTI.
14. **RTI campaign** for what remains: WB SCRB, Kolkata Police, Manipur, Arunachal, Nagaland. Always
    request data **"in the form in which it is already held"** (the NCRB CII return proforma) to defeat
    a s.7(9) refusal. Budget for s.8(1)(g)/(h) refusals and first appeals, especially in AFSPA states.
15. **Conflict layer** from SATP (fetchable) plus MHA state figures — **rendered separately**, never
    merged into the crime layer.

**Do not spend time on:** ICCC command centres (no public data, confirmed), e-FIR and citizen-portal
*intake* systems (they collect, they do not disclose), and Indiastat as a publishable source (licence
forbids it — validation only).

**Finally, a product decision this research forces.** Six of twelve states cannot support a neighbourhood
safety map at all, and in the NE the reported rates are so depressed by underreporting that a naive
choropleth would be actively misleading. Recommend the region ships as: **(a) a genuine drill-down map for
Bhubaneswar–Cuttack, Sikkim and Bihar; (b) district-level indicative counts elsewhere, visually distinct
from (a); and (c) a mandatory reporting-rate caveat on every NE view.** Rendering Nagaland green because
its reported rate is low would be the single worst failure mode available to this project.
