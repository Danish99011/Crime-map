# NCRB — National Crime Records Bureau and everything it publishes or operates
_Agent: ncrb-national · Researched: 2026-09-19 · Entries: 1 verified-live / 30 total (25 CITED, 4 UNVERIFIED)_

> **Read this first — environment constraint, declared up front.**
> `ncrb.gov.in` is **hard-blocked by this session's egress proxy**, for both `WebFetch`
> (`EGRESS_BLOCKED`) and `curl` (`CONNECT tunnel failed, response 403`). So are
> `data.gov.in`, `dataful.in`, `data.opencity.in`, `mha.gov.in`, `pib.gov.in`, `mospi.gov.in`,
> `ndap.niti.gov.in`, `zipnet.delhipolice.gov.in`, `digitalpolice.gov.in`, `arxiv.org`,
> `pmc.ncbi.nlm.nih.gov`, `orfonline.org`, `web.archive.org` and every news domain tested.
> The **only** fetchable domain was `en.wikipedia.org`. The WebSearch budget (200 calls,
> shared across the 16 agents) was exhausted partway through.
>
> **Consequence for honesty:** I opened **zero NCRB PDFs**. Every NCRB URL below is marked
> `CITED`, meaning *a search engine returned this exact URL with a matching title*, which is
> good evidence the path resolves but is **not** evidence of its contents. One entry (NAFIS)
> is `VERIFIED_LIVE` because Wikipedia was fetchable. Four are `UNVERIFIED`. **Exact
> district-table numbers could not be confirmed and I have not invented any.** The specific
> page that would settle it is named in §Blockers, first item.

---

## Executive summary

- **The finest spatial granularity NCRB actually offers is `district` — and only in a
  supplementary table set, not in the main report.** Volumes 1–3 of *Crime in India* are
  **State/UT-level** (`A`-suffixed chapters) and **metropolitan-city-level** (`B`/`D`-suffixed
  chapters). District data ships separately, via the page NCRB calls *"Crime in India Table
  (Additional Table) and Chapter Contents"*. NCRB publishes **nothing** at police-station,
  ward, beat or point level, ever.
- **Latest edition published as of today, 2026-09-19: `Crime in India 2024`, released
  6 May 2026.** There is no 2025 edition. The data backing any map built today is ~21 months
  old at the reference-year midpoint and will stay that way.
- **Publication lag is 12–24 months and erratic**: CII 2021 ≈ 14 months; CII 2022 → uploaded
  2023-12-03 (the unix timestamp `1701607577` is embedded in NCRB's own filename) ≈ 12 months;
  CII 2023 → 29–30 Sept 2025 ≈ **21 months**; CII 2024 → 6 May 2026 ≈ 16 months. A "recent
  crime" product cannot be built on this series. It is a **benchmark**, not a feed.
- **The principal offence rule silently deletes crimes from the map.** Only the most serious
  offence in a multi-offence FIR is counted. A murder-plus-rape-plus-robbery FIR is one murder
  and zero of the other two. Every non-apex category on a map is therefore *systematically*
  undercounted, and the undercount is **worse in violent neighbourhoods** — precisely where a
  map is most consequential.
- **The IPC→BNS break at 2024-07-01 makes 2024 an unusable pivot year and 2025 a new series.**
  2024 is *half IPC, half BNS*. NCRB's own attribution for the headline −6% national decline
  (58.85 lakh cases in 2024 vs 62.41 lakh in 2023) is the statute change, not less crime:
  "simple hurt" became **non-cognisable** and so left police registration entirely, and the
  Hurt head fell **30.58%** (6.36 lakh → 4.41 lakh) for definitional reasons alone.
- **District identity is not stable.** 2011 Census: 640 districts. ~693 in 2021 → ~785 by
  Feb 2024 → **800 as of Dec 2025**. Andhra Pradesh 13→26 (2022, now 28); Telangana 10→33
  (2016); Rajasthan 33→**50** (2023) then cut back to **41**; Delhi 11→13 (effective
  2026-01-01). And NCRB's keys are *police* districts, not revenue districts, so they do not
  even track the reorganisations cleanly.
- **Commissionerate cities are reported separately from districts, and this is the biggest
  single mapping hazard.** The metro chapters cover **19 urban agglomerations**; supplementary
  tables reach **34** and a "Miscellaneous Mega Cities" set **53** — against **77 police
  commissionerates** nationally. For Delhi, NCRB's denominator is the *entire National Capital
  Region* including Faridabad, Ghaziabad, Gurgaon and Noida, which mechanically deflates
  Delhi's crime rate. City rows and district rows are different polygons that may overlap.
- **NCRB does not release unit-level data. At all. There is no microdata programme**, no
  application form, no data enclave — unlike MoSPI/NSSO. It additionally withheld
  **district-wise data entirely for reference years 2016 and 2017**, with no stated reason,
  and published nothing machine-readable for those two years. Those are two holes in the
  district panel that no amount of OCR will fill.
- **CCTNS is the dataset this product actually wants, and it is closed.** ~15,000 police
  stations and ~5,000 supervisory offices, FIR-level, near-real-time, nationally interlinked
  since 2013. The national database behind the Digital Police Portal offers 11 searches and
  44 reports — **to police, CBI, IB, ED and NIA only**. There is **no national citizen FIR
  search**. Nationwide citizen FIR *filing* is a routing layer over state portals.
- **The cleanest NCRB district data lives on data.gov.in, not on ncrb.gov.in** — two OGD
  catalogs, *District-wise crimes under various sections of IPC* and *District-wise crimes
  committed against Women*, in CSV/XLSX/JSON under GODL-India with an API key. Both are
  believed **stale** (terminal year unconfirmed, likely early 2010s). Confirming their
  terminal year is the cheapest high-value action available.
- **Biggest blocker:** granularity floor. NCRB stops at district, annually, 12–24 months late,
  with unstable district keys and a counting rule that suppresses the secondary offence.
  A police.uk-style product **cannot be built from NCRB**. NCRB is the calibration layer;
  the map itself has to come from state CCTNS portals and state police disclosures.

---

## Source entries

### 1. Crime in India (annual series, 1953–2024)
The backbone. Aggregation of returns from 36 States/UTs plus CAPFs and CPOs. Three volumes
since the 2017 format revamp. Chapter numbering encodes geography by letter suffix:

| chapter | subject | geography |
|---|---|---|
| 1A | Summary | States/UTs |
| 2A / 2B | Murder | States/UTs / Metropolitan Cities |
| 2C / 2D | Kidnapping & Abduction | States/UTs / Metropolitan Cities |
| 3A / 3B | Crime Against Women | States/UTs / Metropolitan Cities |
| 4A | Crime Against Children | States/UTs |
| 5 | Juveniles in Conflict with Law | States/UTs |

Volume II carries crime against senior citizens, SCs/STs, economic offences, cybercrime,
anti-national offences and environment-related offences. Volume III carries railway crime,
crimes by/against foreigners, custodial crimes, and property stolen & recovered.

```yaml
id: ncrb-crime-in-india-series
publisher: NCRB, Ministry of Home Affairs
tier: 1
urls:
  landing: https://ncrb.gov.in/en/crime-india
  docs:    https://ncrb.gov.in/crime-in-india-table-addtional-table-and-chapter-contents
geo_coverage: all-India (36 States/UTs + CAPF/CPO)
geo_granularity: district          # via supplementary tables only
unit_of_record: aggregate-count
time_start: 1953
time_latest: 2024 (published 2026-05-06)
cadence: annual
lag: 12-24 months
taxonomy: IPC+SLL to 2023; IPC(Jan-Jun)+BNS(Jul-Dec) 2024; BNS+SLL from 2025
formats: [PDF, XLSX]
access: open-download
machine_readable: 2
license: unstated (GODL-India applies to the data.gov.in mirror)
ingest_difficulty: 4
priority: 5
verification: CITED
checked_on: 2026-09-19
evidence: >
  ncrb.gov.in blocked here (WebFetch EGRESS_BLOCKED; curl CONNECT 403). Search engine
  returned indexed NCRB PDF URLs with matching titles for CII 2019 Vol 3, CII 2022 Book 1,
  CII 2023 Part I and CII 2024 Volume II. Wikipedia "Crime in India" (fetched) confirms the
  2023 edition cites Vol 1, Vol 2 and Vol 3.
```
**Caveats:** principal offence rule; reported-crime-only; IPC→BNS break; unstable district
lists; 2011-Census-projected rate denominators; **no district data for 2016 and 2017**.

### 2. Crime in India 2024 — the latest edition, explicitly
`https://www.ncrb.gov.in/uploads/files/2CrimeinIndia2024-VolumeII.pdf` (indexed).
Released **6 May 2026**. 58.85 lakh cases, −6% YoY; cybercrime +17%; crime against women
−1.5%; children +5.9%; senior citizens +16.9%. **First edition on BNS/BNSS/BSA heads and
therefore not comparable at crime-head level with anything before it.** `priority: 5`,
`verification: CITED`.

### 3. Crime in India 2023 — the last clean IPC year
`https://www.ncrb.gov.in/uploads/files/1CrimeinIndia2023PartI.pdf` (indexed, title
"NCRB Crime in India Report 2023"). Released 29–30 Sept 2025 after a **~21-month** wait.
62.41 lakh cases (+7.2%), rate **448.3 per lakh** (from 422.2 in 2022). **Use 2023 as the
terminal base year of any IPC-era time series.** `priority: 5`, `CITED`.

### 4. Crime in India 2022
`https://www.ncrb.gov.in/uploads/nationalcrimerecordsbureau/custom/1701607577CrimeinIndia2022Book1.pdf`.
The embedded epoch `1701607577` = **2023-12-03 12:46 UTC**, dating the release precisely.
An academic source cites *"NCRB 2022, Chapter 3, Table 3A.1, p.211"* as the crimes-against-women
State/UT table — the only concrete NCRB table number I could source in this session, and it is
a **state-level** table. Mirrored at `ruralindiaonline.org` (Vol I and II). `priority: 4`, `CITED`.

> **Filename forensics, useful for Phase 2:** the older path pattern
> `/uploads/nationalcrimerecordsbureau/custom/<unix-epoch>_<Name>.pdf` lets you date any NCRB
> upload to the second (`1653730682` = 2022-05-28, a re-upload of `CII2019-Volume-3.pdf`).
> The newer pattern is `/uploads/files/<n><Name>.pdf` with a leading volume digit. Both are
> guessable enough to enumerate a full archive from an unblocked host.

### 5. Crime in India — Additional Tables and Chapter Contents *(the district tables)*
`https://ncrb.gov.in/crime-in-india-table-addtional-table-and-chapter-contents`
— note NCRB's own typo, **"addtional"**, which is in the live URL. This page surfaced in
response to a query for the exact NCRB table title *"Crime Head-wise & District-wise Cases
Registered"*. **This is where district data lives**, outside the numbered chapters.

**I could not open it, so I cannot give you the district table numbers.** What I will not do
is guess them. `priority: 5`, `ingest_difficulty: 4`, `CITED`.
**This is the single highest-value verification step in this dossier.**

### 6. Crime in India — Metropolitan Cities chapters and Mega Cities tables
19 urban agglomerations in the main chapters; 34 in additional tables; 53 in "Miscellaneous
Mega Cities"; **77 police commissionerates exist nationally**. Delhi's denominator is the
whole NCR. City units are commissionerate jurisdictions, not municipal boundaries, and do
**not** nest inside revenue districts. `priority: 5`, `CITED`. See §Critical analysis #4.

### 7. Crime in India historical editions (1953 → ~2013)
Scanned image PDFs, shifting table layouts, repeated crime-head redefinitions (notably the
rape definition widened by the Criminal Law (Amendment) Act 2013, breaking that series at
2013). `machine_readable: 0`, `ingest_difficulty: 5`, `priority: 2`, `UNVERIFIED`.

### 8. Accidental Deaths & Suicides in India (ADSI)
Landing `https://www.ncrb.gov.in/accidental-deaths-suicides-in-india-adsi.html` (indexed,
title "Accidental Deaths & Suicides in India (ADSI) Reports"); alt path
`https://ncrb.gov.in/accidental-deaths-suicides-india-adsi`; 2023 file
`https://www.ncrb.gov.in/uploads/files/1ADSIPublication-2023.pdf`.
**ADSI 2024 released ~6–7 May 2026 alongside CII 2024; 1,70,746 suicides in 2024.**
Tables cover accidental deaths by force of nature, traffic (cases, injured, dead, mode of
transport, month and time of occurrence), and suicides by cause, profession, marital status,
economic status and means adopted.

**Granularity honesty:** the brief suggested district-level tables. The evidence I have says
the sub-national cuts are **city-wise** on the same ~53-metro frame as *Crime in India*, with
district coverage thinner than the framing implies and needing table-by-table checking.
`geo_granularity: city`, `priority: 3`, `CITED`. Road-death figures overlap and **disagree**
with MoRTH's *Road Accidents in India*.

### 9. Prison Statistics India (PSI)
**PSI 2024 released ~8 May 2026.** 1,333 jails; sanctioned capacity 4.53 lakh; actual
population 5.11 lakh; occupancy **112.7%** (down from 120.8% in 2023); 95.8% male, 4.14%
female, 122 transgender; **73% undertrial**; Delhi highest occupancy at **194.6%**, then
Meghalaya 163.5%, J&K 148.3%, MP 147.1%.

Jail-level tables exist, but **inmates are attributed to the committing state, not to where
the offence happened** — so PSI cannot locate crime. `geo_granularity: state`, `priority: 2`,
`CITED`. Tabulated on Dataful as collections 1411 / 1415 / 1417 and dataset 19004.

### 10. Finger Print in India (annual)
NCRB absorbed the CBI Central Finger Print Bureau at its founding on 11 March 1986. An annual
fingerprint report is the Bureau's standard output but **no URL surfaced**. Operational
throughput only; no crime counts; no spatial value. `priority: 1`, `UNVERIFIED`.

### 11. CCTNS — Crime and Criminal Tracking Network and Systems
Cabinet approval 2009, ₹2,000 crore; pilot 4 Jan 2013; Core Application Software by Wipro;
**~15,000 police stations and ~5,000 supervisory offices across 28 states and 8 UTs**; a
central citizen portal linking to state citizen portals.

**Nothing is published in aggregate.** This is the richest crime dataset in India —
FIR-level, police-station-keyed, near-real-time — and none of it is open.
`access: blocked`, `machine_readable: 0`, `priority: 4` (because the *route* to it matters).

**How a human in India gets useful data out of it:**
1. **Scrape each state's own CCTNS citizen portal.** This is where police-station-level FIR
   listings actually exist. Different agent's scope, but flag it: state portals are downstream
   of CCTNS and share its schema, so one parser generalises.
2. **RTI each State Crime Records Bureau** for *monthly police-station-wise FIR counts by
   crime head*. Ask for **counts, never records** — counts survive the s.8(1)(h)
   investigation exemption.
3. MoU with NCRB/MHA for research access. No documented process exists.

### 12. Digital Police Portal — `digitalpolice.gov.in`
Launched **21 Aug 2017**. About page `https://digitalpolice.gov.in/DigitalPolice/AboutUs`;
CCTNS brief `https://digitalpolice.gov.in/writereaddata/brief180917.pdf`; citizen endpoint
`https://www.digitalpolicecitizenservices.gov.in/centercitizen/login.htm` (indexed as
":::CCTNS:::", a **login page**). Launch covered by PIB release 171422.

Services: online FIR/complaint registration, passport police verification, case-status
tracking, victim compensation fund, legal services — all routed to the relevant state system,
availability varying by state. The **national** criminal database behind it exposes 11
searches and 44 reports **to state police, CBI, IB, ED and NIA only**.

> **Direct answer to the brief's question: national citizen FIR *search* does NOT exist.**
> Nationwide FIR *filing* is a routing layer, not a national record. `access: login`,
> `priority: 3`, `CITED`.

### 13. ICJS — Inter-operable Criminal Justice System (and ICJS 2.0)
NCRB is nodal agency, NIC is technology partner. Integrates **five pillars**: Police (CCTNS),
Courts (eCourts), Prisons (ePrisons), Forensic Labs (eForensics), Prosecution (eProsecution).
Hosted on MeghRaj. ICJS 2.0 adds an **enterprise data lake** and refreshes all four
non-police applications. Data flow governed by a *Data Sharing Matrix* approved by the Supreme
Court e-Committee — which does not include the public.

Refs: `https://www.mha.gov.in/en/commoncontent/inter-operable-criminal-justice-system-icjs`,
`https://www.mha.gov.in/en/commoncontent/icjsncrb-administration`, PIB factsheet
`https://static.pib.gov.in/WriteReadData/specificdocs/documents/2022/jun/doc202262367401.pdf`,
IIPA evaluation `https://iipa.org.in/upload/project_report/pr36_1.pdf`.

**The hook:** ICJS's stated intent is that *"national level crime analytics [will] be
published at an increased frequency."* That sentence is the basis for an RTI asking for the
analytics products already generated under ICJS 2.0. `access: blocked`, `priority: 2`, `CITED`.

### 14. Cri-MAC — Crime Multi Agency Centre
Implemented **12 March 2020**. Police-to-police alerting for heinous crime and inter-state
coordination, across all States/UTs. Nothing public. No published alert volumes.
`priority: 1`, `CITED`. Source: MHA Women Safety Division CCTNS page.

### 15. NDSO — National Database on Sexual Offenders
Launched **20 Sept 2018** alongside the CCPWC portal. **4.5 lakh+ entries at launch.**
NCRB-maintained, **law-enforcement access only**. Contains *arrested/charged* persons as well
as convicted. India deliberately did not build a US-style public registry.
`priority: 1`, `CITED`. **Do not build any product feature on this.**

### 16. Talash — missing persons / unidentified dead body matching
Named on the MHA CCTNS page as an NCRB service for "matching of missing persons and dead
bodies". No standalone URL surfaced. Internal matching, not a public search. Functionally
overlaps ZIPNET and state missing-persons portals. `priority: 1`, `CITED`.

### 17. Vahan Samanvay — stolen / recovered vehicle matching
Named on the MHA CCTNS page as "online matching for Stolen/Recovered vehicles". **Lookup by
registration number only** — no bulk or area query, so it cannot yield vehicle-theft density.
No working URL surfaced. **Explicitly do not scrape**: per-record lookup services are exactly
what rate limits and legal notices exist for. `priority: 1`, `CITED`.

### 18. NAFIS — National Automated Fingerprint Identification System
**The one `VERIFIED_LIVE` entry** (Wikipedia was fetchable). Launched **17 Aug 2022**;
assigns a **10-digit National Fingerprint Number (NFN)** to every arrested person; **1.06
crore criminal fingerprint records as of 31 Oct 2024**; connected to state fingerprint systems
across all states and UTs.

The NFN is the person-level join key across CCTNS/ICJS — which is precisely why unit-level
NCRB release will never happen without de-identification. `priority: 1`.

### 19. ZIPNET — Zonal Integrated Police Network
**The brief's `zipnet.in` appears superseded.** The live service is
`https://zipnet.delhipolice.gov.in/`, with indexed sections:
`/victims/missingpersons/`, `/victims/unidentifieddeadbodies`, `/victims/unidentifiedpersons/`,
`/vehiclesmobiles/missingmobiles/`. Delhi Police recently relaunched an upgraded site.

**Not an NCRB system** — a Delhi-Police-run consortium of **8 jurisdictions**: Delhi, Haryana,
UP, Rajasthan, Punjab, Chandigarh, Uttarakhand, Himachal Pradesh. Created **2004**.
As of 23 July 2025: **7,880+** people reported missing in Delhi since 1 Jan still untraced;
**1,486** bodies unidentified in the same window.

`access: scrape`, `geo_granularity: police-district`, `cadence: daily`, `priority: 2`, `CITED`.
**Use derived counts by police district only. Never republish the individual records** —
these are named, photographed missing persons and unidentified bodies.

### 20. Khoya-Paya / TrackChild → Mission Vatsalya
**Status change worth flagging:** `trackthemissingchild.gov.in` services have been **migrated
to `https://missionvatsalya.wcd.gov.in`**, and the Khoya-Paya missing/sighted-children
application is integrated into it. Owned by MWCD, not NCRB. Citizen-reported sightings are
police-unverified, so counts mix records with crowd reports. `priority: 1`, `CITED`.
NCRB's own Crime Against Children chapter covers this ground more consistently.

### 21. NCRB unit-level / FIR-level microdata
**Answer to the brief: no. NCRB does not release unit-level data, and there is no process.**
No microdata policy page, no application form, no data enclave — in contrast to MoSPI/NSSO,
which runs one. The FIR is the basic unit of the annual reports; only aggregates are published.
And NCRB withheld **district-wise data entirely for 2016 and 2017**, with no stated reason and
no machine-readable release for those years.
`access: blocked`, `priority: 3`, `CITED` (source: ThePrint's NCRB data analysis).

### 22. RTI route to unpublished NCRB tabulations
`rtionline.gov.in` → Ministry of Home Affairs / NCRB. Expect a **s.6(3) transfer to the
state**, because NCRB holds what states send it rather than the underlying records — so
**file the state RTI in parallel from day one**. `s.8(1)(h)` is the standard refusal for
anything record-level; request counts only. Responses arrive as scanned PDFs of printed tables.
Postal address for the CPIO: NCRB, NH-8, Mahipalpur, New Delhi 110037.
A statistics contact `stat@ncrb.gov.in` surfaced in a search synthesis — **unconfirmed**.
`access: rti-only`, `priority: 3`, `UNVERIFIED`.

### 23. NCRB datasets on data.gov.in (OGD) — **the good mirror**
- `https://www.data.gov.in/catalog/district-wise-crimes-under-various-sections-indian-penal-code-ipc-crimes`
- `https://www.data.gov.in/catalog/district-wise-crimes-committed-against-women`
- `https://www.data.gov.in/catalogs/?ministry=National+Crime+Records+Bureau+%28NCRB%29`

CSV / XLSX / JSON, **GODL-India**, free API key. Heads covered: murder, rape, kidnapping &
abduction, dacoity, robbery, theft, riots; and for women — rape, K&A, dowry death, assault
with intent to outrage modesty, insult to modesty, cruelty by husband or relatives,
importation of girls.

**This is the cleanest machine-readable district series NCRB has ever shipped, and it appears
frozen.** District names are **raw strings with no stable code** and will not join to LGD or
Census codes without a crosswalk. `machine_readable: 4`, `ingest_difficulty: 2`,
**`priority: 5`**, `CITED`. Another agent covers portals; flagged here because this is the
NCRB series with the cleanest mirror.

### 24. NDAP (NITI Aayog) — `https://ndap.niti.gov.in/`
Listed on the strength of its mandate; **no NCRB dataset URL surfaced and the domain is
blocked here**. NDAP's selling point is a **standardised district key across datasets** —
exactly the crosswalk this project needs. If NDAP has already harmonised NCRB districts, it
removes the largest single piece of ingestion work. `priority: 4`, **`UNVERIFIED`** — verify early.

### 25. Dataful (Factly) — `https://dataful.in/`
Indexed items: collection **1108** "NCRB Crime in India (Summary)"; datasets **21867**
"Year and State wise Number of IPC/BNS Crimes" (to 2024), **21547** "Crimes against Women:
Year and State wise", **22522** "Year, State and City wise Number of IPC Crimes";
prison collections **1411 / 1415 / 1417** and dataset **19004**.

**Observed collections are year-and-STATE-wise. Dataful appears to have digitised the state
tables, not the district ones** — so it does not solve our problem. Commercial, mostly paid;
redistribution inside a public map is a licensing question. Tier 5. `priority: 3`, `CITED`.

### 26. OpenCity CKAN — `https://data.opencity.in/`
Dataset pages for *Crime in India* 2022 / 2023 / 2024 and *ADSI 2024*; a facet search reports
**"26 datasets found for ncrb.gov.in"** filtered to PDF. Mostly mirrors of NCRB PDFs.

**Valuable workaround:** `https://data.opencity.in/api/3/action/package_search?q=ncrb` gives a
complete manifest with sizes and checksums — the cheapest way to enumerate what exists if
`ncrb.gov.in` is slow, rate-limited or geo-fenced for your ingestion host. `priority: 3`, `CITED`.

### 27. MoSPI Statistical Year Book, Ch. 37 "Crime Statistics"
`https://www.mospi.gov.in/sites/default/files/Statistical_year_book_india_chapters/Crime.pdf`.
Pure re-publication of NCRB headline tables, state level. **Use it as an independent
transcription to validate your OCR**, not as a data source. `priority: 1`, `CITED`.

### 28. Parliament answers (Lok Sabha / Rajya Sabha) — **underrated**
`https://sansad.in/getFile/annex/266/AU1119_bGpZrf.pdf` (snippet opens *"(a): The National
Crime Records Bureau (NCRB) compiles…"*); MHA mirror pattern
`https://www.mha.gov.in/MHA1/Par2017/pdfs/par<year>-pdfs/LS<DDMMYYYY>/<qno>.pdf`
(a 24 March 2026 answer, `LS24032026/5252.pdf`, was indexed).

**Often fresher than the published report** — MPs are given years NCRB has not yet released —
and occasionally contains cuts NCRB never publishes at all. Coverage is unsystematic (whatever
someone asked), formats inconsistent. **The most reliable way to get post-2024 figures before
*Crime in India 2025* appears.** `priority: 3`, `CITED`.

### 29. "How She Figures" — NCRB data and metadata 1953–2022
`https://hrf.net.in/wp-content/uploads/VAWG-howshefigures-ncrb-and-meta-data-1953-2022.pdf`
A civil-society **70-year metadata reconstruction** for crimes against women and girls.
Tier 4, unverified contents — but if it is what its title says, **it is the crime-head
definition crosswalk this pipeline needs and nobody else appears to have built one**.
`priority: 4`, `CITED`. **Fetch this first among the third-party documents.**

### 30. Third-party NCRB district layers on ArcGIS Online
`https://www.arcgis.com/home/item.html?id=15807229ed3342939bfabd8c9606f25e`
("NCRB: District Wise Crime Against Women"), plus "NCRB: Violent Crimes (Incidence & Crime
Rate)" and an IPC/SLL layer. Public ArcGIS items expose a FeatureServer queryable as GeoJSON
without a key. **Provenance, vintage and boundary vintage are all unknown** — an unlabelled
boundary set will silently misattribute crime to the wrong district.
**Use to steal their crosswalk, not their numbers.** Tier 5, `priority: 2`, `CITED`.

---

## Critical analysis

### 1. The principal offence rule — what it does to a map

NCRB counts **one offence per FIR: the most serious one**. An FIR recording a murder, a rape
and a robbery in the same house becomes **one murder**. The rape and the robbery do not appear
anywhere in *Crime in India*. Critics call this *"definitional burking of crime."* The EU
counting rules do the opposite — count every offence in an incident, and count repeated
offences of the same type more than once.

**Three consequences a crime map must handle:**

1. **Every non-apex category is undercounted, and the bias is not uniform.** Rape, robbery,
   assault, theft and criminal intimidation lose exactly those instances that co-occurred with
   something worse. So the undercount is **concentrated in areas with more serious violent
   crime** — the map will show those areas as *safer* on property and sexual-offence layers
   than they are. That is a defamation risk in reverse: it flatters the wrong places.
2. **Category ratios are not interpretable.** "Rape per 100 thefts" is not a real quantity in
   NCRB data; it is an artefact of which offence topped each FIR.
3. **Total "crimes" ≈ total FIRs, not total offences.** State the denominator on every tile.
   The honest label is *"cognisable cases registered"*, never *"crimes committed"*.

**Mitigation:** do not attempt to correct it. Surface it. Any per-category chloropleth needs
a fixed footnote, and the product should prefer **total cognisable cases** for the headline
layer — the one figure the rule does not distort.

### 2. IPC → BNS, in force 2024-07-01

BNS came into effect **1 July 2024**: 20 chapters, 358 sections; **20 new offences added, 19
IPC provisions dropped**; sedition removed and replaced by an offence against sovereignty,
unity and integrity; organised crime and terrorism brought into the general penal code;
gang-rape adult threshold raised from 16 to 18; imprisonment increased for 33 offences, fines
for 83, mandatory minimums introduced for 23.

**What this does to NCRB's crime-head continuity:**

| period | statute basis | usable? |
|---|---|---|
| …–2023 | IPC throughout | Yes — the clean IPC series, ends with CII 2023 |
| **2024** | **IPC 1 Jan–30 Jun, BNS 1 Jul–31 Dec** | **No. A split year. Do not use as a pivot.** |
| 2025– | BNS throughout | Yes, as the start of a **new** series |

The damage is concrete, not theoretical. Hurt/grievous-hurt sections were **merged**, and
**"simple hurt" was reclassified as non-cognisable** — so it no longer enters police
registration data at all. The Hurt head fell **30.58%** (6.36 lakh → 4.41 lakh) in 2024. That
one reclassification is a large share of the **6% "national decline"** the 2024 report reports,
and NCRB itself attributes the dip to the statute change.

**Engineering consequence:** build **two taxonomies and an explicit, lossy crosswalk between
them**, and render any chart crossing 2024-07-01 with a visible series break. Never
interpolate. A map that shows assault "falling 30%" in mid-2024 is reporting a parliamentary
drafting decision as a change in public safety.

### 3. District reorganisation — quantified

| point in time | districts | note |
|---|---|---|
| Census 2011 | 640 | the boundary set every population denominator is projected from |
| 2021 | ~693 | |
| Feb 2024 | ~785 | |
| **Dec 2025** | **800** | Wikipedia, *List of districts in India*, as of 2025-12-09 |

Churn by state, with dates: **Telangana 10 → 33 (2016)**. **Andhra Pradesh 13 → 26 by
executive order (2022), now 28** (Polavaram and Markapuram added). **Rajasthan 33 → 50 (2023),
then cut back to 41** — a reorganisation that was *partially reversed*, which is worse than one
that merely happened. **Delhi 11 → 13, effective 2026-01-01.**

**Quantified problem for a district panel 2011→2025:** roughly **160 net new districts (+25%)**
against the Census 2011 frame, from a mix of splits, mergers, renames and reversals — while
the **population denominators are still projections off the 2011 640-district frame**. NCRB
publishes **no district code** and **no year-to-year concordance**; its rows are *name strings*
for **police** districts, which do not track revenue reorganisations on the same schedule.

**What this means in practice:** any district time series is a **panel with an unstable index**.
A newly-split district shows an apparent crime "collapse" in year *t* purely because its
successor units carry the other half. Rates are worse: a 2023-created Rajasthan district has no
2011 population, so either NCRB imputes silently or the rate is nonsense.

**Mitigation:** build a **Census-2011-frame crosswalk** and aggregate every year up to stable
2011 parent districts for anything involving trend or rate. Show current districts only for
single-year snapshots, and only with counts, never rates. Check NDAP first (#24) — it may have
done this already.

### 4. Commissionerate cities vs rural districts — the mapping hazard

**Yes, NCRB reports commissionerate cities separately, and it is a serious problem.**

- The metropolitan chapters (2B, 2D, 3B …) cover **19 urban agglomerations**.
- Supplementary tables extend to **34 metropolitan cities**.
- A **"Miscellaneous Mega Cities"** set reaches **53**.
- There are **77 police commissionerates** in India. **Most have no separate NCRB row.**
- For Delhi, NCRB's denominator is the **entire National Capital Region**, including
  Faridabad, Ghaziabad, Gurgaon and Noida — cities in *three other states*. Delhi's published
  crime rate is therefore divided by a population several times its own jurisdiction's.

**Four failure modes for the map:**

1. **Non-nesting.** Mumbai City Police, Bengaluru City Police and Delhi Police jurisdictions
   are not revenue districts and do not tile the state. A district chloropleth that renders
   both city and district rows will **double-count or leave holes**, depending on which way
   the state's returns were compiled.
2. **Wrong denominator.** Using a city's *urban agglomeration* population against its
   *commissionerate* case count understates rates, dramatically so for Delhi.
3. **Silent heterogeneity.** Two districts rendered in the same colour may be a
   commissionerate city and a rural district with completely different reporting propensity,
   police density and FIR registration culture.
4. **Ambiguous overlap.** Whether a commissionerate city's cases are *also* inside the parent
   district row, or carved out of it, is **state-dependent** and undocumented.

**Mitigation:** treat city and district as **two separate map layers with two separate
geometries**, resolve the overlap question **per state** before rendering, and never sum them.

---

## Granularity reality check

| level | available from NCRB? | period | refresh | notes |
|---|---|---|---|---|
| `national` | Yes | 1953–2024 | annual, 12–24 mo lag | headline totals and rates |
| `state` | Yes — the main product | 1953–2024 | annual, 12–24 mo lag | `A`-suffixed chapters; also on Dataful as CSV |
| `city` | Yes, but only 19 / 34 / 53 cities | ~2014–2024 | annual | commissionerate jurisdictions; NCR denominator for Delhi |
| **`district`** | **Yes — supplementary tables only. THE FLOOR.** | ~2001–2024, **2016 and 2017 missing** | annual, 12–24 mo lag | unstable keys, no district code, police≠revenue districts |
| `police-district` | Implicitly (NCRB's district rows *are* police districts) | as above | annual | no published mapping to revenue districts |
| `police-station` | **No. Never.** | — | — | exists in CCTNS; not published |
| `ward` / `beat` / `grid` / `point` / `address` | **No.** | — | — | not collected in any published NCRB product |

**The gap, stated plainly:** the product wants *"is this neighbourhood safe to walk through at
night?"* NCRB's answer arrives **once a year, 12–24 months late, for an administrative unit
averaging roughly 1.6 million people**, with only the most serious offence of each FIR counted,
on a district key that changes annually. **NCRB cannot make this product. It can only
calibrate it.**

---

## Blockers and how to get past them

1. **`ncrb.gov.in` is unreachable from this environment** (WebFetch `EGRESS_BLOCKED`,
   curl `CONNECT 403`). Every NCRB fact here is from search-engine indexing or Wikipedia.
   → **First action for a human or an unblocked crawler:** open
   `https://ncrb.gov.in/crime-in-india-table-addtional-table-and-chapter-contents` and
   **enumerate the district tables and their exact numbering, per year, per format**. That
   one page closes the largest gap in this dossier.
2. **WebSearch budget exhausted** (200/200 shared across agents) mid-investigation. Three
   planned queries were lost: the exact contents of the additional-tables page; the
   PDF-vs-XLS availability matrix per year; the "Crime in India Snapshots" compendium.
3. **No unit-level data, ever.** Route: RTI for **counts** to State Crime Records Bureaux
   (not NCRB — it will transfer under s.6(3)). Phrase as
   *"crime-head-wise number of cases registered, for each police station in <district>, for
   calendar years 2022–2025, in machine-readable format."*
4. **2016 and 2017 have no district data and nothing machine-readable.** Not recoverable from
   NCRB. Partial reconstruction possible from State Crime Records Bureau annual reports and
   from Parliament answers for those years.
5. **PDF-only for recent years.** Table extraction from multi-hundred-page NCRB PDFs is the
   main ingestion cost. Mitigate by preferring the **data.gov.in district CSVs** (#23) wherever
   their years cover, and by pulling PDFs from **OpenCity CKAN** (#26) if ncrb.gov.in
   rate-limits your host.
6. **No robots.txt or ToU could be checked for any NCRB property.** Before Phase 2 scraping,
   fetch `ncrb.gov.in/robots.txt`, `digitalpolice.gov.in/robots.txt` and
   `zipnet.delhipolice.gov.in/robots.txt`, and read the GoI website ToU. Do not assume.
7. **Licensing is unstated on NCRB's own PDFs.** Only the **data.gov.in** mirror carries an
   explicit licence (**GODL-India**). For a public-facing map, **prefer the GODL-licensed
   mirror for anything you republish**, and cite the PDF as provenance. Get this in front of a
   lawyer before launch.

---

## Seed Leads (unconfirmed but probably real)

| lead | likely publisher / title | concrete next step |
|---|---|---|
| **NCRB additional-tables index contents** | NCRB, "Crime in India Table (Additional Table) and Chapter Contents" | Open `https://ncrb.gov.in/crime-in-india-table-addtional-table-and-chapter-contents` and list every file, year and format. **Do this first.** |
| **Per-year XLS/CSV availability** | NCRB | Same page. Recent years are believed to ship some tables as XLS/XLSX alongside PDF; **unverified**. Older years are scanned images. |
| **"Crime in India — Snapshots"** | NCRB summary booklet / "at a glance" | Search the Publications menu on ncrb.gov.in. Cited in a Wikipedia reference for 1953–2006 crime rates, suggesting a historical compendium format. |
| **NCRB microdata / research access** | NCRB Statistics Division | Email the statistics contact (`stat@ncrb.gov.in`, **unconfirmed**) asking directly whether any de-identified unit-level or district-level extract can be supplied to a research institution, and under what agreement. |
| **NCRB Annual Report / Citizen's Charter** | NCRB | Would document the publication calendar and the data-supply cycle from states — i.e. *why* the lag is 12–24 months. Check the About/RTI section of ncrb.gov.in. |
| **State-to-NCRB return formats** | NCRB "Crime in India" proforma / schedule sent to State Crime Records Bureaux | RTI for the blank proforma. **This is the schema of Indian crime statistics** and would tell you exactly which fields states report and which NCRB drops before publication. High value, low cost. |
| **NDAP harmonised NCRB tables** | NITI Aayog NDAP | Register, search "NCRB", and check specifically whether NDAP applied its standardised district key. Could eliminate the whole crosswalk problem. |
| **ICJS 2.0 crime analytics products** | NCRB / MHA | RTI citing ICJS's own stated objective of publishing "national level crime analytics… at an increased frequency", asking what has been produced and whether it will be released. |
| **Finger Print in India** | NCRB Central Finger Print Bureau, annual | Publications menu on ncrb.gov.in; RTI if absent. Low value, listed for completeness. |
| **`zipnet.in`** | original ZIPNET domain | Confirm whether it still resolves or redirects to `zipnet.delhipolice.gov.in`. Evidence points to the Delhi Police subdomain being the live service. |

---

## Phase 2 recommendations (ranked)

1. **Open the additional-tables page and enumerate the district tables.** Everything else in
   the NCRB domain is downstream of knowing exactly what district data exists, for which
   years, in which format. One page. Highest return per minute in this entire dossier.
2. **Ingest the two data.gov.in district catalogs first** (#23). GODL-India licensed,
   CSV/XLSX/JSON, API key, district-level. Confirm their terminal year on day one — if they
   really do stop in the early 2010s, that fact reshapes the roadmap and should be known
   before anyone writes a PDF parser.
3. **Build the district crosswalk to the Census-2011 frame before ingesting anything else.**
   640 → 800 districts, with splits, merges, renames and at least one partial reversal
   (Rajasthan). Check NDAP (#24) and the ArcGIS layers (#30) first — someone may have done it.
   Without this, every trend line and every rate on the map is wrong.
4. **Ingest Crime in India 2023 (all volumes) as the IPC-era base**, then 2024 as the start of
   the BNS era, with a hard, visible series break at 2024-07-01. Do not build a 2023→2024
   comparison feature.
5. **Resolve the commissionerate-vs-district overlap per state** before the first chloropleth
   renders. Two layers, two geometries, never summed.
6. **Start the State Crime Records Bureau RTI campaign now**, in parallel with everything
   above. It is the only route to police-station granularity, it is slow (30 days statutory,
   realistically longer, plus appeals), and it is the long pole for any product that resembles
   police.uk. Ask for counts, never records. Budget for 36 jurisdictions.
7. **Fetch the "How She Figures" metadata compendium** (#29) and use it to seed the crime-head
   definition crosswalk. A 70-year metadata reconstruction already done by someone else is
   worth more than a month of your own archaeology.
8. **Set up a Parliament-answer watcher** on sansad.in for "NCRB", "CCTNS", "crime against
   women". Between annual reports this is the only fresh official crime data in India, and it
   sometimes carries cuts NCRB never publishes.
9. **Do not design around CCTNS, ICJS, NDSO, Cri-MAC, Talash, Vahan Samanvay or NAFIS.** They
   are closed. Catalogue them, watch ICJS 2.0 for a public analytics release, and put the
   engineering effort into **state CCTNS citizen portals**, which are the only place
   police-station-level Indian crime data is actually visible.
