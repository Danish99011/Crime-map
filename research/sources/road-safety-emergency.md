# Road Safety, Traffic & Emergency-Response Data
_Agent: road-safety-emergency · Researched: 2026-09-19 · Entries: 1 verified-live / 37 total_

> **Verification health warning, read this first.** This session ran behind an egress
> allowlist that blocked **every `*.gov.in`, `*.nic.in` and most Indian civil-society host**
> I attempted (`morth.gov.in`, `morth.nic.in`, `nhai.gov.in`, `irad.parivahan.gov.in`,
> `btp.gov.in`, `traffic.delhipolice.gov.in`, `112.gov.in`, `data.gov.in`,
> `data.opencity.in`, `tripc.iitd.ac.in`, `pib.gov.in`, `cdac.in`, `dataforindia.com`,
> `ncbi.nlm.nih.gov`, `indiairf.com`). The search *index* was reachable and returned these
> URLs with their page titles; direct fetch was refused at the proxy. Per `_SPEC.md` rule 1
> I have therefore recorded almost everything as `CITED` (URL returned by a search engine
> with a matching title) or `UNVERIFIED` (I believe it exists, no URL seen), **not** as
> verified. The session's WebSearch budget was also exhausted mid-run (200/200), which cut
> off ~8 planned queries (NDMA/Bhuvan hazard layers, WHO GSRRS, VAHAN dashboard, state fire
> services, Mumbai Traffic Police, Tamil Nadu RADMS, 108/EMRI, Rajmargyatra).
> **Phase 1b action: re-run this dossier's URL list from an unrestricted network.** Every
> URL below is a real string returned by a search engine, not a guess, except where the
> entry says `urls` is a bare domain root.

## Executive summary

- **Road-traffic danger is the best-geolocated physical-risk domain in India, and it is not
  close.** India records ~4.9 lakh crashes and ~1.77 lakh road deaths a year (MoRTH, RAI
  2024 — 4,87,707 crashes / 1,77,175 deaths / 4,71,441 injured). For a resident asking "is
  this area safe?", the annual probability of being killed or maimed on the road near home
  dwarfs the probability of being a victim of the violent crime the NCRB counts.
- **There is exactly one genuinely point-level, publicly-published physical-danger dataset
  in India that I found: the MoRTH/NHAI "black spot" lists.** A black spot is a defined
  **500 m stretch of National Highway** with ≥5 fatal/grievous crashes or ≥10 fatalities in
  3 calendar years. **13,795 black spots** have been identified nationally (2016–2022
  vintage); short-term rectification on 9,525, long-term/permanent on ~4,777–5,036. The
  published annexures carry **state, NH number, chainage (km), and a free-text location
  description**; some state lists carry lat/long. This is map-ready after geocoding against
  the NH alignment. **Ingest this first.**
- **iRAD/eDAR is the prize and it is closed.** The Integrated Road Accident Database
  (iRAD), now extended as e-DAR (e-Detailed Accident Report), is a MoRTH + World Bank +
  IIT-Madras (RBG Labs) + NIC/NICSI national crash database in which **police capture the
  crash location by GPS on a mobile app at the scene**, joined to Health, Transport and
  road-owning-agency records. All **36 states/UTs joined by November 2022**. Dashboards
  exist but are explicitly described as "accessible to higher authorities of stakeholder
  departments and MoRTH". No public API, no public download, no research-access route was
  found. **This is the single highest-value RTI target in the entire Crime-map project** —
  see "Blockers" for the exact wording that survives the post-DPDP Section 8(1)(j).
- **MoRTH is now using e-DAR to re-derive black spots in near-real time.** Ministry
  guidelines of **February 2024** direct advance action on accident spots *reported on the
  e-DAR platform*, and MoRTH has signalled the first "real-time mapping" of black spots for
  2023–24. If those refreshed lists are published, we get a point-level layer that updates
  far faster than anything in the crime domain.
- **City traffic police are the sleeper source.** Bengaluru Traffic Police publishes
  **police-station-wise** fatal/non-fatal accident counts (2015–2024 series) as HTML tables
  on `btp.gov.in`. Delhi Traffic Police publishes an annual **Delhi Road Crash Report**
  (2021, 2022, 2023 editions confirmed) with junction/stretch-level blackspot analysis.
  Police-station granularity is exactly the join key the crime layer will use.
- **IIT Delhi's TRIPC has already geocoded Delhi's fatal crashes** (2019–2021) from MACT
  cell records plus Delhi Traffic Police FIR lists, digitised and cleaned at the Transport
  Department, and published **per-district heatmaps of fatal crash locations** for all 11
  Delhi districts. The maps are raster-in-PDF; **the underlying geocoded point file exists**
  and is obtainable by academic request rather than RTI. Cheapest route to real point data.
- **ERSS/Dial-112 is the closest thing India has to a live incident feed** — ten intake
  channels (voice, SMS, SOS, email, web, chatbot, media crawler, IoT, WhatsApp, external
  signals) into a state Public Safety Answering Point, with caller location. It is
  **state-held, state-by-state**, which makes it 36 separate RTI conversations rather than
  one — but also makes a single cooperative state a viable pilot.
- **MoRTH and NCRB disagree on road deaths every year and both are undercounts.** For 2023:
  MoRTH ~1.73–1.77 lakh, NCRB ADSI 1.73 lakh deaths / 4,64,029 crashes, with a third NCRB
  figure of 1.81 lakh in circulation. Both are police-sourced; they diverge because MoRTH
  collects via State *transport* departments (now iRAD) while NCRB compiles from *FIRs*
  through the crime-statistics chain. WHO/GBD put India's true toll materially higher.
  **Never put a MoRTH number and an NCRB number on the same axis without a footnote.**
- **Railway trespass death is a genuinely point-level urban killer that nobody maps.**
  Mumbai suburban alone: ~2,000+ deaths/year; 848 trespass deaths in a recent year (516
  Central Railway, 332 Western Railway; Kalyan worst at 44). RPF/GRP/railway officials have
  **already identified 139 specific locations** with the most trespassing. That is a
  ready-made point layer for the single deadliest commute in the country.
- **Finest spatial granularity actually achievable in this domain today:** `point`
  (NH black spots, via chainage → geocode) and `police-station` (Bengaluru, Delhi).
  Realistically achievable within 12 months with one successful RTI or one academic
  agreement: `point` for one metro (Delhi via TRIPC, or any state via iRAD).
- **Single biggest blocker:** the country's only national point-level crash database
  (iRAD/eDAR) is closed to the public, and the **DPDP Act 2023 amendment to RTI §8(1)(j)**
  removed the public-interest override for "personal information", giving every CPIO a
  clean refusal unless the request is framed as strictly non-personal.

---

## Source entries

### 1. MoRTH "Road Accidents in India" (annual report)
The statistical backbone of the domain. Compiled by the Transport Research Wing, MoRTH,
from state transport department returns (increasingly from iRAD). Latest edition is
**RAI 2024**, released around June 2026 (4,87,707 crashes; 1,77,175 deaths; 4,71,441
injured; +1.5% crashes and +2.5% deaths over 2023; over-speeding implicated in ~70%).
RAI 2023 PDF sits at a stable `morth.gov.in/backend/documents/uploaded/` path.

```yaml
id: road-safety-emergency-morth-road-accidents-india
publisher: Ministry of Road Transport & Highways (Transport Research Wing)
tier: 1
urls:
  data: https://morth.gov.in/backend/documents/uploaded/Road-Accident-in-India-2023-Publications.pdf
geo_granularity: state (+ a 50-million-plus-cities table, + NH/SH/other-road split)
unit_of_record: aggregate-count
time_start: 1970 (continuous series; modern format from ~2005)
time_latest: calendar year 2024
cadence: annual
lag: 16-18 months
formats: [PDF]   # some years also XLSX annexures
access: open-download
machine_readable: 1   # text PDF, tables need extraction
ingest_difficulty: 3
priority: 4
verification: CITED
```
**Caveats:** police-reported only; systematic undercount vs WHO/GBD; "road accidents" ≠
NCRB ADSI figure; city table covers only million-plus cities and uses *municipal/police
commissionerate* boundaries that do not match NCRB's city definitions; definition of
"grievous injury" changed with the 2016 reporting-format revision.

---

### 2. MoRTH RAI — million-plus-cities tables (subset of #1, treated separately for ingest)
The only part of the national report that gets below state level. ~50 cities, annual
crashes / deaths / injuries, sometimes split by road-user type. Delhi is consistently top
(e.g. 5,652 crashes in the year covered by RAI 2024 reporting). This is the table that
lets us put a city-level comparator on the map on day one.

```yaml
id: road-safety-emergency-morth-rai-million-plus-cities
publisher: MoRTH (Transport Research Wing)
tier: 1
urls: {data: https://morth.gov.in/backend/documents/uploaded/Road-Accident-in-India-2023-Publications.pdf}
geo_granularity: city
unit_of_record: aggregate-count
cadence: annual
lag: 16-18 months
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 3
priority: 4
verification: CITED
```
**Caveats:** city boundary = police commissionerate, which for Delhi/Bengaluru/Hyderabad is
much larger than the municipal area; denominators (population) are 2011-Census-projected.

---

### 3. MoRTH identified road-accident **black spots** on National Highways
**The point-level layer.** Published as Ministry Office Memoranda with state-wise
annexures. The 2016 OM ("Additional Road Accident Black Spots identified based on 2014
fatalities on National Highways, OM dated 18.1.2016") is a confirmed file path on
`morth.nic.in/sites/default/files/`. Definition: 500 m NH stretch with ≥5 fatal/grievous
crashes **or** ≥10 fatalities over 3 calendar years. National total **13,795** identified.
Annexure columns observed in this family of documents: S.No., State, NH No., **chainage
from (km) / chainage to (km)**, location/landmark description, number of accidents, number
of fatalities, proposed rectification, status.

```yaml
id: road-safety-emergency-morth-black-spots-om
publisher: MoRTH (Road Safety Cell)
tier: 2
urls:
  data: https://morth.nic.in/sites/default/files/Additional_Road_Accident_Black_Spots_identified_based_on_2014_fatalities_on_National_Highways_OM_dated_18_1_2016.pdf
geo_granularity: point   # 500 m NH segment, chainage-referenced
unit_of_record: incident-point   # a hazard location, not a single crash
time_start: 2015 (first consolidated list)
time_latest: 2022 vintage published; 2023-24 e-DAR-derived refresh announced
cadence: irregular
lag: 1-3 years
taxonomy: n/a
formats: [PDF]
access: open-download
machine_readable: 1
license: GODL-India (assumed, unstated on document)
ingest_difficulty: 4   # chainage -> lat/long requires NH alignment geometry
priority: 5
verification: CITED
```
**Caveats:** **National Highways only** — ~2% of the road network, but IIT Delhi attributes
30.3% of crashes and 36% of deaths to it. Excludes state highways, urban arterials and all
city streets, so absence of a black spot means nothing about a neighbourhood. Lists are
cumulative and re-issued, so de-duplicate across vintages. "Rectified" spots stay on the
list — join to the rectification-status file (#4) or you will show a fixed junction as
dangerous.

---

### 4. NHAI black spots page and rectification-status reports
NHAI maintains a dedicated black-spots section with state-wise reports and rectification
status. Parliamentary answers give the running totals: of 13,795 identified, short-term
measures on 9,525 and permanent rectification on 4,777 (a parallel figure of 5,036
long-term-rectified is also in circulation). State detail from Parliament: Punjab 911,
Himachal Pradesh 226, J&K 200, Haryana 144. MoRTH target: 1,000 spots in FY26, all by FY28.

```yaml
id: road-safety-emergency-nhai-black-spots
publisher: National Highways Authority of India
tier: 2
urls: {landing: https://nhai.gov.in/nhai/black-spots}
geo_granularity: point
unit_of_record: incident-point
time_latest: 2024-25 status
cadence: irregular
formats: [PDF, XLSX]
access: open-download
machine_readable: 2
ingest_difficulty: 3
priority: 5
verification: CITED
```
**Caveats:** NHAI covers only NHAI-managed NH; other NH stretches sit with state PWDs and
NHIDCL and may be reported separately or not at all.

---

### 5. MoRTH GIS mapping of National Highways
A MoRTH circular titled "Final GIS Mapping" plus a portal page "GIS mapping of all National
Highways". This is the **geometry we need to turn chainage into coordinates** for entries
#3/#4. Without it the black-spot layer cannot be mapped.

```yaml
id: road-safety-emergency-morth-nh-gis-mapping
publisher: MoRTH
tier: 2
urls:
  docs: https://morth.nic.in/sites/default/files/circulars_document/Final%20GIS%20Mapping.pdf
  landing: http://morth.gov.in/en/gis-mapping-all-national-highways
geo_granularity: point
unit_of_record: boundary-polygon   # linear referencing geometry
cadence: irregular
formats: [PDF, SHP]
access: open-download
machine_readable: 2
ingest_difficulty: 4
priority: 5
verification: CITED
```
**Caveats:** NH numbering was wholesale renumbered in 2010; chainage restarts at state
boundaries on some NHs; older black-spot lists use pre-2010 NH numbers.

---

### 6. MoRTH "Revised Road Accidents Data Recording and Reporting Formats"
The circular that defines what a police officer must record for every crash. **This is the
schema document** — it tells us exactly which fields (including location/GPS) exist inside
iRAD and therefore exactly what to name in an RTI. Indexed at `morth.gov.in/print/9989`.

```yaml
id: road-safety-emergency-morth-accident-reporting-formats
publisher: MoRTH
tier: 2
urls: {docs: https://morth.gov.in/print/9989}
geo_granularity: n/a
unit_of_record: narrative-document
cadence: one-off
formats: [PDF, HTML]
access: open-download
machine_readable: 3
ingest_difficulty: 1
priority: 4
verification: CITED
```

---

### 7. **iRAD / eDAR — Integrated Road Accident Database / e-Detailed Accident Report**
India's national crash database. MoRTH initiative, **World Bank funded**, conceptualised and
designed by **RBG Labs, IIT Madras**, built and run by **NIC/NICSI**. Integrates Police,
Health, Transport and road-owning agencies. Police record the crash **on the spot via a
mobile app**, which is where the GPS fix comes from. e-DAR extends it to auto-generate the
Detailed Accident Report required by Motor Accident Claims Tribunals and insurers. **All 36
states/UTs onboarded by Nov 2022.** Live and demo web apps are linked from
`irad.parivahan.gov.in`; a demo instance is exposed at `gisnic.tn.nic.in/irad/webapp/`.

```yaml
id: road-safety-emergency-irad-edar
publisher: MoRTH / NIC / NICSI (design: RBG Labs, IIT Madras; funding: World Bank)
tier: 2
urls: {landing: https://irad.parivahan.gov.in/}
geo_coverage: all-India (36 states/UTs)
geo_granularity: point
unit_of_record: incident-point
time_start: 2020 (pilot); nationwide 2022
time_latest: current (operational, near-real-time)
cadence: realtime
lag: days
taxonomy: custom (MoRTH accident recording format; not IPC/BNS)
formats: [dashboard-only]
access: login   # effectively blocked to the public
machine_readable: 0   # nothing public
license: unknown
ingest_difficulty: 5
priority: 5
verification: CITED
how_to_obtain: >
  Three parallel routes. (a) RTI to MoRTH CPIO (Road Safety Cell / IT Cell, Transport
  Bhawan, 1 Parliament Street, New Delhi 110001) — see the drafted text in "Blockers".
  (b) RTI to the State Transport Commissioner and State DGP, because iRAD is federated and
  the state is the data owner for its own records; a single cooperative state is far more
  likely to answer than MoRTH. (c) Academic/MoU route via RBG Labs, IIT Madras (the system
  designer) or the World Bank task team — request de-identified research extract.
```
**Caveats:** even if obtained, coverage ramp-up is uneven (2021-22 records are sparse for
late-adopting states); GPS may be captured at the *police station* rather than the scene
where officers back-fill; no public documentation of positional accuracy; records are
FIR-linked and therefore contain personal data, which is the legal hook every refusal will
use.

---

### 8. iRAD/eDAR user manual (public schema documentation)
Two manual PDFs are indexed publicly: `irad.parivahan.gov.in/downloads/iRAD_MANNUAL_april_2024.pdf`
and a v2.0 draft at `gisnic.tn.nic.in/irad/downloads/iRAD_User_Manual_V_2.0_draft.pdf`.
These give field names and screen flow — i.e. the exact vocabulary for an RTI, and the
column list for a Phase-2 schema if we ever get an extract.

```yaml
id: road-safety-emergency-irad-edar-user-manual
publisher: MoRTH / NICSI
tier: 3
urls:
  docs: https://irad.parivahan.gov.in/downloads/iRAD_MANNUAL_april_2024.pdf
  data: https://gisnic.tn.nic.in/irad/downloads/iRAD_User_Manual_V_2.0_draft.pdf
geo_granularity: n/a
unit_of_record: narrative-document
time_latest: April 2024
cadence: irregular
formats: [PDF]
access: open-download
machine_readable: 2
ingest_difficulty: 1
priority: 5
verification: CITED
notes: Read this before drafting the iRAD RTI. Name the fields the manual names.
```

---

### 9. World Bank project documentation for iRAD
iRAD was World Bank funded. World Bank Project Appraisal Documents, Implementation Status
Reports and ICRs routinely publish the data model, results framework, record counts and any
**data-sharing covenants** — material that MoRTH itself will not release. `documents.worldbank.org`
is full-text searchable and open-licensed (CC BY 3.0 IGO).

```yaml
id: road-safety-emergency-worldbank-irad-docs
publisher: World Bank
tier: 3
urls: {landing: https://documents.worldbank.org/}
geo_coverage: all-India
geo_granularity: national
unit_of_record: narrative-document
cadence: irregular
formats: [PDF, HTML]
access: open-download
machine_readable: 3
license: CC-BY-3.0-IGO
ingest_difficulty: 1
priority: 4
verification: UNVERIFIED
notes: >
  URL is the bare portal root, not a confirmed document path. Search terms to use:
  "Integrated Road Accident Database", "iRAD", "India road safety", "Harnessing data for
  road safety". Also check the Bloomberg Philanthropies Initiative for Global Road Safety
  (BIGRS) city reports for Mumbai/Bengaluru, which carry geocoded crash analysis.
```

---

### 10. Delhi Road Crash Report (Delhi Traffic Police, annual)
Confirmed editions: 2021, 2022, 2023. The 2022 edition was released by the Commissioner of
Police and reported 1,461 deaths. Content is crash counts plus **causes, patterns, and
recommendations on road design, regulation and prosecution** — i.e. it names dangerous
junctions and stretches. Stable PDF paths under
`traffic.delhipolice.gov.in/sites/default/files/uploads/<year>/`.

```yaml
id: road-safety-emergency-delhi-traffic-police-crash-report
publisher: Delhi Traffic Police
tier: 2
urls:
  data: https://traffic.delhipolice.gov.in/sites/default/files/uploads/2022/Delhi-Crash-Report-2022.pdf
  landing: https://traffic.delhipolice.gov.in/delhi-crash-report-2023
geo_coverage: NCT of Delhi (Delhi Police jurisdiction)
geo_granularity: police-district   # with named junction/stretch blackspots inside
unit_of_record: aggregate-count
time_start: 2014 (basic series carried in the reports)
time_latest: 2023
cadence: annual
lag: 6-12 months
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 3
priority: 5
verification: CITED
```
**Caveats:** Delhi Police's 15 police districts ≠ the 11 revenue districts used by TRIPC and
the Transport Department. Reconcile before joining.

---

### 11. Delhi Transport Department road-safety publications
The Transport Department publishes **Delhi Road Crash Fatality Reports for 2020, 2021 and
2022** plus a "Road Safety Data to Action" report, and hosts the per-district TRIPC reports.
This is where the *cleaned, digitised* crash dataset behind the maps lives administratively.

```yaml
id: road-safety-emergency-delhi-transport-publications
publisher: Transport Department, GNCTD
tier: 2
urls:
  landing: https://transport.delhi.gov.in/transport/publications
  data: https://transport.delhi.gov.in/sites/default/files/inline-files/east.pdf
geo_coverage: NCT of Delhi
geo_granularity: district
unit_of_record: aggregate-count
time_start: 2020
time_latest: 2022
cadence: annual
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 2
priority: 4
verification: CITED
how_to_obtain: >
  For the underlying geocoded file rather than the PDF: RTI to the CPIO, Transport
  Department, GNCTD, asking for the digitised crash dataset (non-personal fields only)
  compiled from MACT cell records and Delhi Traffic Police FIR lists for 2019-2021 as used
  in the district road safety reports prepared with IIT Delhi.
```

---

### 12. TRIPC (IIT Delhi) district road safety reports — **geocoded Delhi crash points**
Eleven district reports (South, Central, New Delhi, East, …). Method, stated in the reports:
crash records from the **MACT cells of the districts**, supplemented by **FIR lists from
Delhi Traffic Police**, compiled/digitised/cleaned at the Transport Department, covering
**2019–2021**; high-risk locations identified per district; **heatmaps of fatal road crash
locations and deaths by road-user type**; on-site investigation of each high-risk location.

```yaml
id: road-safety-emergency-tripc-delhi-district-reports
publisher: Transportation Research and Injury Prevention Centre, IIT Delhi
tier: 4
urls:
  data: https://tripc.iitd.ac.in/assets/training_material/South%20District%20Concise.pdf
  docs: https://tripc.iitd.ac.in/assets/training_material/Central%20District%20Concise.pdf
geo_coverage: NCT of Delhi, 11 districts
geo_granularity: point   # in the underlying file; raster maps in the published PDF
unit_of_record: incident-point
time_start: 2019
time_latest: 2021
cadence: one-off
formats: [PDF]
access: open-download (PDF) / on-request (point file)
machine_readable: 0   # maps are images
ingest_difficulty: 5   # for the PDF; 2 if the point file is granted
priority: 5
verification: CITED
how_to_obtain: >
  Email TRIPC, IIT Delhi requesting the de-identified geocoded crash point file used for
  the district reports, under a research data-sharing agreement. This is the cheapest
  credible route to real point-level crash data in India and does not require an RTI.
```
**Caveats:** Delhi only; 2019–2021 includes two COVID years with abnormally low exposure —
do not present 2020 rates as typical.

---

### 13. India Status Report on Road Safety (IIT Delhi, annual)
Independent annual synthesis, editions confirmed for 2023 and 2024. Reconciles MoRTH, NCRB
and survey/hospital sources and publishes **state-level fatality rates corrected for
under-reporting**. This is the benchmark to validate any map we build.

```yaml
id: road-safety-emergency-tripc-india-status-report
publisher: IIT Delhi (TRIPC)
tier: 4
urls:
  data: https://tripc.iitd.ac.in/assets/publication/India_Status_Report_on_Road_Safety-20242.pdf
  docs: https://tripc.iitd.ac.in/assets/publication/RSI_2023_web.pdf
geo_granularity: state
unit_of_record: aggregate-count
time_start: 2023
time_latest: 2024
cadence: annual
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 2
priority: 4
verification: CITED
```

---

### 14. Bengaluru Traffic Police — accident statistics (station-wise)
`btp.gov.in/Accidentstats.aspx` and `btp.gov.in/statistics.aspx` carry **station-wise
accident statistics for 2022, 2023 and 2024** plus a fatal/non-fatal series **2015–2024**.
Police-station granularity, published as web tables. Bengaluru ranked 2nd nationally in
road fatalities in 2023 with 921 deaths (~3/day).

```yaml
id: road-safety-emergency-btp-accident-statistics
publisher: Bengaluru Traffic Police
tier: 2
urls:
  data: https://btp.gov.in/Accidentstats.aspx
  landing: https://btp.gov.in/statistics.aspx
geo_coverage: Bengaluru city police / traffic police jurisdiction
geo_granularity: police-station
unit_of_record: aggregate-count
time_start: 2015
time_latest: 2024
cadence: annual (some tables monthly)
lag: 1-3 months
formats: [HTML]
access: scrape
machine_readable: 3
ingest_difficulty: 2
priority: 5
verification: CITED
how_to_obtain: ASP.NET page; scrape politely, check robots.txt, cache one pull per quarter.
```
**Caveats:** traffic police station boundaries ≠ law-and-order police station boundaries in
Bengaluru — there are ~50 traffic stations vs ~110+ law-and-order stations. The crime layer
and this layer will need two different boundary sets.

---

### 15. Bengaluru Traffic Police — Road Safety Report (annual)
A designed annual report (2023 edition confirmed) with blackspot identification using the
MoRTH 500 m definition, mirrored on OpenCity. Complements #14 with narrative and location
naming.

```yaml
id: road-safety-emergency-btp-road-safety-report
publisher: Bengaluru Traffic Police
tier: 2
urls:
  data: https://data.opencity.in/dataset/81336158-a834-4e79-a866-8196ea8b75d3/resource/2261ce08-a0cb-46e1-a1a1-1025ae1f0b72/download/6c425f17-b19b-402f-a638-6b9cae856025.pdf
geo_coverage: Bengaluru Metropolitan Region
geo_granularity: city
unit_of_record: aggregate-count
time_latest: 2023
cadence: annual
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 2
priority: 3
verification: CITED
```

---

### 16. Road Accidents in Karnataka (Karnataka State Police, annual)
State-police annual compilation; OpenCity holds editions for 2020, 2021, 2022 and 2023.
Typically district-wise. The state-level analogue of #14 and a model for what other state
police forces may hold unpublished.

```yaml
id: road-safety-emergency-ksp-road-accidents-karnataka
publisher: Karnataka State Police
tier: 2
urls: {landing: https://data.opencity.in/dataset/road-accidents-in-karnataka}
geo_coverage: Karnataka
geo_granularity: district
unit_of_record: aggregate-count
time_start: 2020
time_latest: 2023
cadence: annual
formats: [PDF]
access: open-download
machine_readable: 1
ingest_difficulty: 2
priority: 3
verification: CITED
```

---

### 17. OpenCity Urban Data Portal (CKAN)
Civil-society CKAN instance that **mirrors and normalises** government PDFs and sheets:
MoRTH RAI 2023, NCRB ADSI 2023, Delhi Road Crashes Data, Bengaluru Road Accidents Data 2024,
Bengaluru Traffic Police collection, Road Accidents in Karnataka. Because it is CKAN it has
a **standard CKAN API** (`/api/3/action/package_search`), which makes it the single easiest
ingestion target in this entire dossier.

```yaml
id: road-safety-emergency-opencity
publisher: OpenCity (Oorvani Foundation / Data{Meet} ecosystem)
tier: 4
urls:
  landing: https://data.opencity.in/
  data: https://data.opencity.in/dataset?organization=bengaluru-traffic-police
  api: https://data.opencity.in/api/3/action/package_search
geo_coverage: all-India, deepest for Bengaluru and Delhi
geo_granularity: city
unit_of_record: aggregate-count
cadence: irregular
formats: [PDF, XLSX, CSV, JSON]
access: open-download
machine_readable: 4
license: unstated (mirrors upstream government licences)
ingest_difficulty: 1
priority: 5
verification: CITED
notes: >
  API path is the CKAN standard and was not fetched in this session — confirm before
  relying on it. Mirrors are convenience copies; cite the upstream government document as
  the source of record for anything we publish.
```

---

### 18. Mumbai Traffic Police accident data
Mumbai Traffic Police publish annual accident statistics and have a public data/RTI page.
Not reached in this session; no URL confirmed. Mumbai is a must-have city for v1.

```yaml
id: road-safety-emergency-mumbai-traffic-police
publisher: Mumbai Traffic Police / Mumbai Police
tier: 2
geo_coverage: Greater Mumbai police jurisdiction
geo_granularity: police-station
unit_of_record: aggregate-count
cadence: annual
formats: [PDF, HTML]
access: on-request
machine_readable: 1
ingest_difficulty: 3
priority: 4
verification: UNVERIFIED
how_to_obtain: >
  Check trafficpolicemumbai.org and the Mumbai Police site for an annual accident
  statement; if absent, RTI to CPIO, Joint CP (Traffic), Mumbai, for zone-wise and
  police-station-wise fatal/non-fatal accident counts by month for the last 5 years.
```

---

### 19. Maharashtra Highway Traffic Police — iRAD/eDAR page
`highwaypolice.maharashtra.gov.in/info-dar-page/` is a state highway-police page dedicated
to iRAD/eDAR. State highway police are the *entry point* for iRAD records on state highways
and are a more approachable RTI respondent than MoRTH.

```yaml
id: road-safety-emergency-maharashtra-highway-police-irad
publisher: Maharashtra Highway Traffic Police
tier: 2
urls: {landing: https://highwaypolice.maharashtra.gov.in/info-dar-page/}
geo_coverage: Maharashtra highways
geo_granularity: point (underlying), state (published)
unit_of_record: incident-point
cadence: realtime (system) / none (publication)
formats: [HTML]
access: login
machine_readable: 0
ingest_difficulty: 5
priority: 3
verification: CITED
how_to_obtain: RTI to CPIO, Highway Traffic Police, Maharashtra — non-personal iRAD fields only.
```

---

### 20. NCRB "Accidental Deaths & Suicides in India" (ADSI)
The crime-statistics-chain counterpart of MoRTH. ADSI 2023: **4,64,029 road accidents,
~1.73 lakh killed, ~4.47 lakh injured** (+17,261 crashes over 2022). ADSI also carries
**fire accident deaths**, drowning, falls, electrocution, poisoning and natural-force
deaths — the broader "accidental death" layer this project should use for non-road hazards.

```yaml
id: road-safety-emergency-ncrb-adsi
publisher: National Crime Records Bureau, MHA
tier: 1
urls:
  landing: https://www.ncrb.gov.in/
  data: https://data.opencity.in/dataset/accidental-deaths-and-suicides-in-india-2023
geo_coverage: all-India
geo_granularity: state (+ 19/53 metropolitan-city tables)
unit_of_record: aggregate-count
time_start: 1967
time_latest: 2023
cadence: annual
lag: 12-20 months
taxonomy: NCRB-heads (not IPC/BNS)
formats: [PDF, XLSX, CSV]
access: open-download
machine_readable: 2
license: GODL-India
ingest_difficulty: 2
priority: 4
verification: CITED
```
**Caveats:** *disagrees with MoRTH on road deaths every single year* — 2023: MoRTH ~1.73–1.77
lakh vs NCRB 1.73 lakh in one table and 1.81 lakh in another. Both are police-sourced; they
diverge because MoRTH collects through **state transport departments** (now iRAD) and NCRB
through **FIR-based crime statistics**. ADSI is not subject to the principal-offence rule
(that applies to *Crime in India*), but the metro-city tables use NCRB's own city
definitions, which differ from MoRTH's. Do not sum the two.

---

### 21. eChallan dashboard (Parivahan)
`echallan.parivahan.gov.in/echallanreport/` is a live reporting dashboard for the national
digital traffic-enforcement system run by NIC for MoRTH. Enforcement intensity is a useful
**proxy for both risk and policing presence** — and, where states use ANPR/ITMS cameras
(Bengaluru's AI-enabled ITMS is named), challans are generated at **fixed, known camera
locations**, which are points.

```yaml
id: road-safety-emergency-echallan-dashboard
publisher: MoRTH / NIC
tier: 2
urls:
  data: https://echallan.parivahan.gov.in/echallanreport/
  landing: https://echallan.parivahan.gov.in/
geo_coverage: all-India (state/RTO-wise)
geo_granularity: state   # district/RTO in some views
unit_of_record: aggregate-count
time_latest: current
cadence: daily
lag: near-real-time
formats: [dashboard-only]
access: scrape
machine_readable: 2
ingest_difficulty: 4
priority: 3
verification: CITED
how_to_obtain: >
  Dashboard is JS-rendered; inspect the XHR endpoints it calls and pull JSON directly.
  A mirror host exists at echallan.parivahan.nic.in. For camera locations, RTI to the city
  traffic police for the ITMS/ANPR camera inventory with coordinates.
```
**Caveats:** challan counts measure *enforcement*, not danger. A neighbourhood with many
challans may simply have a camera. Never render this as a risk layer without that framing.

---

### 22. Parivahan VAHAN / Sarathi (vehicle registrations, driving licences)
Denominator layer. VAHAN gives registered vehicles by RTO and vehicle class; Sarathi gives
driving licences. Essential for converting crash counts into **rates per registered vehicle**
and for two-wheeler exposure, given two-wheelers dominate Indian road deaths (69,240 of
155,622 deaths in NCRB 2021).

```yaml
id: road-safety-emergency-parivahan-vahan-sarathi
publisher: MoRTH / NIC
tier: 1
urls: {landing: https://parivahan.gov.in/}
geo_coverage: all-India
geo_granularity: district   # RTO-level
unit_of_record: aggregate-count
time_start: ~2010 (digitised)
time_latest: current
cadence: daily
formats: [dashboard-only, XLSX]
access: scrape
machine_readable: 2
ingest_difficulty: 3
priority: 3
verification: UNVERIFIED
notes: >
  URL is the bare portal root; the analytics dashboard path was not confirmed in this
  session. RTO jurisdictions are not coterminous with districts in large states — build an
  RTO->district crosswalk before using as a denominator.
```

---

### 23. ERSS / Dial 112 (national)
MHA's "ONE INDIA ONE EMERGENCY NUMBER 112". Deployed as a **state-centric** system: each
state/UT runs an Emergency Response Centre and a Public Safety Answering Point receiving
distress signals over **ten channels** (voice, SMS, SOS, email, web request, chatbot, media
crawler, IoT signals, WhatsApp, external signals). Response-time commitments are published
per state (Haryana: 15–20 minutes). Technology partner: C-DAC.

```yaml
id: road-safety-emergency-erss-112
publisher: Ministry of Home Affairs (states operate)
tier: 2
urls:
  landing: https://112.gov.in/about
  docs: https://www.mha.gov.in/en/commoncontent/emergency-response-support-system-erss
geo_coverage: all-India (36 states/UTs)
geo_granularity: point   # caller location, held internally
unit_of_record: incident-point
time_start: 2019
time_latest: current
cadence: realtime
formats: [dashboard-only]
access: blocked   # no public call data found
machine_readable: 0
ingest_difficulty: 5
priority: 5
verification: CITED
how_to_obtain: >
  State-by-state RTI to the ERSS Nodal Officer / DGP / State Home Department. Ask for
  AGGREGATES ONLY to survive §8(1)(j): monthly count of 112 calls by emergency category
  (police / fire / medical / road accident / women's safety) by police station or ERV
  response zone, and mean/median dispatch and on-scene arrival time by district, for the
  last 36 months. Explicitly disclaim any request for caller identity, number, recording
  or address. Start with a state that already publishes an ERSS dashboard.
```
**Caveats:** calls ≠ incidents (hoax and duplicate call rates in Indian ERCs are high, often
cited above 50% of total inbound); call volume tracks awareness and phone penetration, so a
low-call ward may be under-served rather than safe. This is the most defamation-prone layer
in the project.

---

### 24. State ERSS dashboards
Several states run their own 112 portals with live or periodic statistics — a Kerala KSDMA
ERSS-112 page and an `ld.erss.in` instance were indexed. Where a state publishes call counts
by district, that is obtainable without RTI.

```yaml
id: road-safety-emergency-erss-state-dashboards
publisher: State police / State Home Departments
tier: 2
urls: {landing: https://ld.erss.in/}
geo_coverage: state-specific
geo_granularity: district
unit_of_record: aggregate-count
cadence: daily
formats: [dashboard-only, HTML]
access: scrape
machine_readable: 2
ingest_difficulty: 4
priority: 3
verification: UNVERIFIED
notes: >
  `ld.erss.in` appeared in search results as an ERSS host; its content was not verified and
  it may be a vendor demo. Audit each state 112 site individually in Phase 1b — UP-112,
  Telangana, Kerala, Punjab and Rajasthan are the likeliest to publish numbers.
```

---

### 25. 108 emergency ambulance service (GVK EMRI and state operators)
The largest pre-hospital emergency network in India, operating in ~15+ states, dispatching
GPS-tracked ambulances against GPS-located calls. Its incident log is effectively a
**geolocated injury feed** including road crashes, and it is independent of the police
reporting chain — so it can be used to *estimate police under-reporting*.

```yaml
id: road-safety-emergency-emri-108
publisher: GVK EMRI / state health departments
tier: 3
geo_coverage: ~15+ states
geo_granularity: point
unit_of_record: incident-point
time_start: 2005
time_latest: current
cadence: realtime
formats: [dashboard-only]
access: on-request
machine_readable: 0
ingest_difficulty: 5
priority: 3
verification: UNVERIFIED
how_to_obtain: >
  Two routes: (a) RTI to the State Health Department / National Health Mission which
  contracts the service, for monthly counts of road-traffic-accident (RTA) 108 dispatches
  by block/police station and mean response time; (b) academic collaboration — EMRI has
  published with AIIMS and IIT groups and has an established research-request process.
```
**Caveats:** health-department data is subject to patient-confidentiality objections; ask
for counts by geography and hour, never by case.

---

### 26. Indian Railways / RPF — untoward incidents and trespass deaths
Railways report "untoward incidents" and deaths due to trespassing; a figure of ~30,000
deaths from trespassing and untoward incidents over three years has been stated by Indian
Railways. NCRB separately recorded 17,993 railway accidents in 2021 (+38% on 2020). MyGov
has run a public consultation group specifically on "Deaths due to trespassing".

```yaml
id: road-safety-emergency-railways-untoward-incidents
publisher: Ministry of Railways / Railway Protection Force
tier: 2
urls: {landing: https://www.mygov.in/group-issue/deaths-due-trespassing/}
geo_coverage: all-India (by zonal railway)
geo_granularity: district   # zonal railway / division, not administrative
unit_of_record: aggregate-count
time_latest: 2024
cadence: annual
formats: [PDF, HTML]
access: rti-only   # aggregates appear only in Parliament answers and press
machine_readable: 1
ingest_difficulty: 4
priority: 3
verification: CITED
how_to_obtain: >
  RTI to CPIO, Railway Board (Security Directorate) and to the CPIO of each zonal railway
  (Central and Western Railway for Mumbai), for: deaths and injuries due to trespassing and
  untoward incidents, by station and by kilometre-post, for the last 5 years; plus the list
  of identified trespassing-prone locations and their coordinates.
```
**Caveats:** railway geography is zone/division/section, not district/ward — a crosswalk to
station coordinates (which are openly available in OSM and in the railway station master)
is required to map anything.

---

### 27. Mumbai suburban railway deaths (GRP / Central & Western Railway)
The most concentrated fatality statistic in urban India and the one most relevant to "should
I live along this line?". Confirmed figures from reporting: **848 trespass deaths in a
recent year — 516 Central Railway, 332 Western Railway; Kalyan worst with 44**. Unnatural
deaths *at stations*: 662 (2022), 656 (2023), 781 (2024). Long-run: ~3,700 deaths/year
average 2002–2012; 36,152 deaths and 36,688 injuries over that decade; 17 deaths per weekday
at the 2008 peak; ~7/day now. **RPF, GRP and railway officials have identified 139 specific
locations with the most trespassing incidents.**

```yaml
id: road-safety-emergency-mumbai-suburban-railway-deaths
publisher: Government Railway Police (Maharashtra) / Central & Western Railway
tier: 2
geo_coverage: Mumbai suburban railway network
geo_granularity: point   # station and named trespass location
unit_of_record: aggregate-count   # point-level in the internal 139-location list
time_start: 2002
time_latest: 2024
cadence: annual (monthly internally)
formats: [PDF, HTML]
access: rti-only
machine_readable: 1
ingest_difficulty: 3
priority: 4
verification: CITED
how_to_obtain: >
  RTI to CPIO, Commissioner of Police (Railways) Mumbai / GRP, for station-wise and
  section-wise unnatural deaths and injuries by cause (trespassing, falling from train,
  platform gap, OHE contact) by month for 5 years; and to CPIO, Central Railway and
  Western Railway, for the list of 139 identified trespassing-prone locations with
  kilometre-post references. The 139-location list is the point layer.
```
**Caveats:** GRP and railway administration publish different totals for the same year
because of jurisdiction splits between station premises and track sections.

---

### 28. Commission of Railway Safety — accident inquiry reports
Statutory inquiry body under the Ministry of Civil Aviation. Publishes inquiry reports into
serious train accidents, each naming an exact location and kilometre-post. Low volume, high
precision; relevant to corridor-level risk narrative rather than neighbourhood risk.

```yaml
id: road-safety-emergency-commission-railway-safety
publisher: Commission of Railway Safety, Ministry of Civil Aviation
tier: 3
geo_granularity: point
unit_of_record: narrative-document
cadence: irregular
formats: [PDF]
access: open-download
machine_readable: 0
ingest_difficulty: 4
priority: 1
verification: UNVERIFIED
notes: No URL confirmed this session. Search "Commission of Railway Safety accident inquiry reports".
```

---

### 29. State Fire & Emergency Services statistics
Fire is a "is this building/area safe" hazard that residents care about and that nobody maps.
Two routes: NCRB ADSI's fire-accident-deaths tables (state level, annual, already in #20),
and state fire service annual reports / station-wise call logs, which are typically
**station-level with addresses** and are held by the Directorate of Fire Services in each
state (Delhi Fire Service, Maharashtra Fire Service, Tamil Nadu Fire & Rescue Services).

```yaml
id: road-safety-emergency-state-fire-services
publisher: State Directorates of Fire & Emergency Services; NDRF/DG Fire Services (MHA) at centre
tier: 2
geo_coverage: state-specific
geo_granularity: ward   # fire-station response area; address-level in the call log
unit_of_record: incident-point
cadence: annual (published) / realtime (internal)
formats: [PDF]
access: rti-only
machine_readable: 1
ingest_difficulty: 4
priority: 3
verification: UNVERIFIED
how_to_obtain: >
  RTI to the Director, Fire Services, of the target state: monthly count of fire calls by
  fire station and by call type (building fire, vehicle fire, rescue, false alarm), plus
  fire deaths and injuries, for 5 years; plus the fire-station location list with
  coordinates and declared response areas. Fire-station coverage gaps are themselves a
  publishable safety layer.
```
**Caveats:** fire services also handle non-fire rescue, so raw "calls" over-state fire risk;
NCRB fire-death totals and state fire-service totals routinely disagree.

---

### 30. NRSC Bhuvan / NDEM — flood and hazard geospatial layers
The natural-hazard layer for "is this address safe". ISRO's NRSC runs Bhuvan and the
National Database for Emergency Management, which host flood-inundation mapping, cyclone
tracks and hazard layers, generally as **WMS/WMTS services** — i.e. already GIS, already
polygonal, and directly overlayable.

```yaml
id: road-safety-emergency-bhuvan-ndem
publisher: National Remote Sensing Centre, ISRO
tier: 1
geo_coverage: all-India
geo_granularity: grid
unit_of_record: boundary-polygon
cadence: irregular (event-driven for floods)
formats: [GeoJSON, SHP, HTML]
access: api-key   # Bhuvan requires registration for most downloads
machine_readable: 4
license: unstated / Bhuvan ToU restricts redistribution
ingest_difficulty: 3
priority: 3
verification: UNVERIFIED
notes: >
  No URL confirmed this session (search budget exhausted). Verify bhuvan.nrsc.gov.in,
  bhuvan-app1.nrsc.gov.in/ndem and the Bhuvan WMS endpoints. Check the terms of use
  carefully before republishing — Bhuvan's ToU has historically restricted derivative
  publication, which matters for a public-facing map.
```

---

### 31. GSI Bhukosh — landslide inventory
Geological Survey of India's Bhukosh portal publishes a **national landslide incident
inventory with coordinates** plus landslide susceptibility mapping. Genuinely point-level
hazard data, directly relevant in Himalayan, Western Ghats and Northeast towns.

```yaml
id: road-safety-emergency-gsi-bhukosh-landslide
publisher: Geological Survey of India
tier: 1
geo_coverage: all-India (dense in hill states)
geo_granularity: point
unit_of_record: incident-point
cadence: annual
formats: [SHP, GeoJSON, XLSX]
access: open-download
machine_readable: 4
license: unstated
ingest_difficulty: 2
priority: 3
verification: UNVERIFIED
notes: URL not confirmed this session. Verify bhukosh.gsi.gov.in and the landslide inventory layer.
```

---

### 32. WHO Global Status Report on Road Safety — India chapter
The external validation benchmark. WHO publishes a modelled estimate of India's true road
deaths that is substantially above the police-reported MoRTH figure, plus legislative
scorecards (helmet, seatbelt, speed, drink-driving laws and enforcement scores).

```yaml
id: road-safety-emergency-who-gsrrs
publisher: World Health Organization
tier: 3
urls: {landing: https://www.who.int/}
geo_coverage: India (national)
geo_granularity: national
unit_of_record: aggregate-count
cadence: irregular (roughly triennial)
formats: [PDF, XLSX]
access: open-download
machine_readable: 3
license: CC-BY-NC-SA-3.0-IGO
ingest_difficulty: 1
priority: 2
verification: UNVERIFIED
notes: Bare domain root only — deep path not confirmed. Use to caption "official counts are a floor, not a ceiling".
```

---

### 33. IHME Global Burden of Disease — India road injury estimates
GBD gives modelled road-injury deaths, DALYs and rates **by Indian state**, annually, with
uncertainty intervals, downloadable from the GBD Results Tool. This is the only source that
gives a *state-level, methodologically consistent, under-reporting-corrected* road-death
series — perfect for calibrating a map built on police counts.

```yaml
id: road-safety-emergency-ihme-gbd-india
publisher: Institute for Health Metrics and Evaluation
tier: 4
urls: {landing: https://www.healthdata.org/}
geo_coverage: India, by state
geo_granularity: state
unit_of_record: aggregate-count
time_start: 1990
cadence: irregular (GBD cycles)
formats: [CSV, JSON]
access: open-download
machine_readable: 5
license: IHME free-of-charge non-commercial terms
ingest_difficulty: 2
priority: 3
verification: UNVERIFIED
notes: >
  Bare domain root; the GBD Results Tool path was not confirmed. Licence is NOT open —
  IHME's terms restrict commercial use and require attribution; get this reviewed before
  shipping it in a public product.
```

---

### 34. Parliament Questions (Lok Sabha / Rajya Sabha) on road safety
**The most under-rated obtainable source in this dossier.** MoRTH answers starred and
unstarred questions with **state-wise annexure tables** that are never published anywhere
else: black spots by state (Punjab 911, HP 226, J&K 200, Haryana 144), rectification status,
deaths by NH, iRAD rollout status. Answers are published as PDFs within days and are fully
open. A standing scrape of MoRTH/Railways/MHA answers is a low-cost, high-yield feed.

```yaml
id: road-safety-emergency-parliament-questions
publisher: Lok Sabha Secretariat / Rajya Sabha Secretariat
tier: 3
geo_coverage: all-India
geo_granularity: state   # occasionally district or NH-stretch in annexures
unit_of_record: aggregate-count
time_start: 1999 (digitised)
time_latest: current session
cadence: irregular (per session)
formats: [PDF, HTML]
access: open-download
machine_readable: 2
ingest_difficulty: 3
priority: 4
verification: CITED
notes: >
  URLs not confirmed (sansad.in hosts were not reachable). Evidence is indirect: multiple
  news reports quoting state-wise annexure data given in Rajya Sabha by the Minister.
  Phase 2: build a keyword watch on "black spot", "iRAD", "eDAR", "road accident",
  "trespassing" across both houses.
```

---

### 35. NHAI Rajmargyatra (citizen app for National Highways)
NHAI's citizen app for NH users: real-time highway information and a **geotagged complaint/
incident reporting channel**. If complaint records are obtainable they are point data
covering exactly the corridors the black-spot list covers.

```yaml
id: road-safety-emergency-nhai-rajmargyatra
publisher: NHAI
tier: 2
urls: {landing: https://nhai.gov.in/}
geo_coverage: National Highways
geo_granularity: point
unit_of_record: incident-point
cadence: realtime
formats: [dashboard-only]
access: on-request
machine_readable: 0
ingest_difficulty: 5
priority: 2
verification: UNVERIFIED
how_to_obtain: >
  Inspect the app's API traffic for an open endpoint; failing that, RTI to NHAI for
  counts of geotagged citizen complaints by NH and chainage bucket. Also ask about the
  NHAI 1033 highway helpline call log, which is a separate and larger incident stream.
```

---

### 36. Tamil Nadu RADMS (Road Accident Data Management System)
Tamil Nadu ran a GIS-based state road accident database (RADMS), developed under the World
Bank-assisted TN Road Sector Project, years before iRAD — reportedly with geocoded crash
locations and a web interface for police and highways engineers. If any state has a mature,
requestable, geocoded crash dataset, it is this one.

```yaml
id: road-safety-emergency-tn-radms
publisher: Tamil Nadu Police / TN Highways Department
tier: 2
geo_coverage: Tamil Nadu
geo_granularity: point
unit_of_record: incident-point
time_start: ~2009
cadence: realtime
formats: [dashboard-only]
access: on-request
machine_readable: 0
ingest_difficulty: 5
priority: 3
verification: UNVERIFIED
how_to_obtain: >
  RTI to the Additional DGP (Traffic), Tamil Nadu Police and to the TN Highways Department
  asking whether RADMS is still operational, its current relationship to iRAD, and for a
  non-personal geocoded extract. Also check World Bank TNRSP project documents, which
  should describe the RADMS schema publicly.
```

---

### 37. Community mirrors and derived datasets (GitHub, Kaggle)
A live GitHub search returned ~10 repositories analysing Indian road accident data
(`katreparitosh/Multi-Dimensional-Data-Analytics-of-Road-Accidents-in-India`,
`harnagpal/IndiaAccidentalData2015` — map visualisation, `rinbaruah/Indian-roads-data-analysis`,
`Shruti21Chaturvedi/RoadAccidents-India-2020-`, and others), plus a Kaggle notebook on
Bangalore road accidents. A parallel GitHub search for **India highway "black spot"**
returned **0 repositories** — nobody has liberated the black-spot lists yet. That is our gap
to fill and our contribution back to the commons.

```yaml
id: road-safety-emergency-community-mirrors
publisher: various (GitHub / Kaggle contributors)
tier: 5
urls:
  landing: https://github.com/search?q=india+road+accident+data&type=repositories
  data: https://www.kaggle.com/code/supratimhaldar/bangalore-road-accidents-basic-data-analysis
geo_coverage: all-India, various
geo_granularity: state
unit_of_record: aggregate-count
cadence: one-off
formats: [CSV, JSON]
access: open-download
machine_readable: 4
license: unknown (mostly unstated; upstream provenance usually undocumented)
ingest_difficulty: 1
priority: 2
verification: VERIFIED_LIVE
evidence: >
  Fetched the GitHub repository search on 2026-09-19 and saw ~10 named repositories on
  Indian road accident data. A second search for india + "black spot" + highway + accident
  returned "0 results" / "Your search did not match any repositories."
```
**Caveats:** provenance is almost always undocumented — treat as leads to the upstream
official table, never as a source of record.

---

## Granularity reality check

| Layer | Geographic level actually shipped | Period | Refresh | Point-level possible? |
|---|---|---|---|---|
| MoRTH/NHAI **black spots** | **point** (NH chainage, 500 m segment) + text landmark | 2015–2022 vintage; 2023-24 e-DAR refresh announced | irregular, 1–3 yr | **Yes — already public** |
| GSI Bhukosh landslides | **point** | multi-year | annual | **Yes — already public** |
| iRAD / eDAR | point (GPS at scene) — **not published** | 2020– | realtime | Yes, if RTI/MoU succeeds |
| ERSS-112 calls | point (caller location) — **not published** | 2019– | realtime | Yes, if state RTI succeeds |
| 108 / EMRI dispatches | point — **not published** | 2005– | realtime | Yes, via health dept or academic route |
| TRIPC Delhi crash file | point — published only as **raster maps in PDFs** | 2019–2021 | one-off | Yes, by academic request |
| Mumbai rail trespass "139 locations" | point — **not published** | current | annual | Yes, via zonal railway RTI |
| Bengaluru Traffic Police | **police-station** | 2015–2024 | annual/monthly | No |
| Delhi Road Crash Report | police-district + named junctions in prose | 2014–2023 | annual | Partially (geocode the named junctions) |
| Fire services | fire-station response area | varies | annual | Only via RTI on the call log |
| MoRTH RAI city table | **city** (police commissionerate) | 1970–2024 | annual, 16–18 mo lag | No |
| NCRB ADSI | **state** + 19 metro cities | 1967–2023 | annual, 12–20 mo lag | No |
| Karnataka / state police reports | district | 2020–2023 | annual | No |
| VAHAN / Sarathi (denominators) | RTO ≈ district | ~2010– | daily | No |
| eChallan | state / RTO | current | daily | Only the camera inventory is point |
| WHO / GBD | national / state | 1990– | triennial | No |

**The gap, stated bluntly:** we want ward- or street-level, monthly. In this domain we can
have, today, **point-level but only on National Highways and only as a static hazard list**,
or **police-station-level but only for Bengaluru and Delhi and only annually**. Everything
else is state or city, 12–18 months stale. The one thing that would close the gap —
iRAD/eDAR — exists, is national, is point-level, is near-real-time, and is closed.

## Ranking: which layers actually change a resident's decision

Scored on (a) geographic precision and (b) decision-weight for "should I live/walk here".

| Rank | Layer | Precision | Decision-weight | Why |
|---|---|---|---|---|
| 1 | **iRAD/eDAR crash points** | 5 | 5 | The whole product, if we can get it. Point, national, fresh. |
| 2 | **NH black spots** | 4 | 4 | Public *today*. In India NHs run through dense urban areas (NH-48 Gurugram, NH-44 Delhi/Hyderabad) — a black spot 400 m from a flat is a real, actionable fact. |
| 3 | **City traffic police station-wise counts** | 3 | 5 | Joins to the crime layer's geography; annual but comparable; covers where people actually live. |
| 4 | **ERSS-112 aggregates** | 3 | 4 | Response time is the thing residents most want and never get. "Ambulance/police reaches this ward in N minutes" is a killer feature. |
| 5 | **Mumbai rail trespass locations** | 5 | 4 | Tiny geography, enormous mortality, zero existing maps. |
| 6 | **Fire-station coverage + fire calls** | 3 | 3 | Especially for renters in dense old housing. |
| 7 | **Flood / landslide hazard polygons** | 4 | 4 | Already GIS. For Chennai, Mumbai, Bengaluru, Guwahati, Shimla this outranks crime. |
| 8 | **MoRTH RAI city table** | 2 | 2 | Backbone and headline number, not a decision input. |
| 9 | **ADSI** | 1 | 2 | Cross-check only. |
| 10 | **eChallan** | 2 | 1 | Measures policing, not danger. Easy to misread; ship last or not at all. |

**Direct answer to the brief's question — what can give us POINT data:**
`MoRTH/NHAI black-spot annexures` (public, now), `GSI Bhukosh landslide inventory` (public,
now), and — conditional on access — `iRAD/eDAR`, `ERSS-112`, `108/EMRI`, `TRIPC's Delhi
geocoded file` and `the railways' 139 trespass locations`. Nothing in the NCRB crime domain
will give us a point; **this domain will.**

## Blockers and how to get past them

**B1. iRAD/eDAR is closed — and DPDP has made RTI harder.**
The DPDP Act 2023 amended RTI §8(1)(j) to exempt *personal information* outright, removing
the public-interest override. Any request that touches an FIR-linked record will be refused
on that ground. **Frame the request as strictly non-personal and say so in the application.**

Draft RTI (MoRTH CPIO, Road Safety Cell / IT Cell, Transport Bhawan, 1 Parliament Street,
New Delhi 110001; ₹10 fee; copy to the CPIO, NIC):

1. A copy of the iRAD/eDAR **data dictionary or database schema** for the accident record,
   listing table and field names.
2. A copy of the **data-sharing policy, SOP or MoU** governing access to iRAD/eDAR data by
   researchers, state governments, insurers or third parties, and the **name and designation
   of the officer competent to approve** such access.
3. The **number of accident records** in iRAD/eDAR, **by state and by calendar year**, since
   inception.
4. In electronic form (CSV by email, per §7(9) and §2(j)), for accidents recorded in
   [district] during [years], the following **non-personal** fields only: pseudonymised
   accident ID, date, time, **latitude, longitude**, road name / NH number, chainage,
   accident severity, collision type, categories of road users involved, junction type,
   road-surface condition, weather, lighting.
   *"I am not seeking any personal information. I specifically exclude names, addresses,
   contact details, vehicle registration numbers, driving licence numbers, FIR numbers and
   any other identifier of any individual."*
5. Whether the latitude/longitude in iRAD is **captured by GPS at the accident scene or
   entered manually**, and the positional accuracy recorded.

If refused: First Appeal to the FAA within 30 days, arguing (i) the data sought is
non-personal and therefore outside the amended §8(1)(j); (ii) MoRTH already publishes crash
locations in aggregate (black-spot lists), so location is not confidential; (iii) §8(2)
public interest. Then CIC second appeal. **Run the same request in parallel against 3–4 State
Transport Commissioners / DGPs** — iRAD is federated, states hold their own data, and a
state is far more likely to answer than the Ministry.

**B2. Chainage is not coordinates.** Black-spot lists give NH number + km. We need the NH
alignment geometry (entry #5, or OSM's `ref=NH*` ways as a fallback) plus a linear-reference
routine. Budget real engineering time; validate against the free-text landmark in each row.

**B3. Blocked and JS-only portals.** btp.gov.in, echallan dashboard and VAHAN are ASP.NET or
JS-rendered. Scrape the underlying XHR endpoints, not the HTML. Honour robots.txt; one pull
per quarter is enough for annual data (spec rule 6).

**B4. My own egress allowlist.** Every `.gov.in` host was refused at the proxy. Phase 1b:
re-run the full URL list from an Indian or unrestricted network and promote `CITED` entries
to `VERIFIED_LIVE`. This is a one-afternoon job and should happen before any ingestion.

**B5. Two official road-death numbers.** Pick MoRTH as the series of record (it is the
transport-department chain that feeds iRAD and the black-spot process), show NCRB ADSI as a
comparison line, and caption both with the WHO/GBD modelled estimate. Never subtract them.

**B6. Defamation risk.** A black spot is a property of a *road*, not a *neighbourhood*. An
ERSS call volume is a property of *reporting*, not of *danger*. Design the map so that road
hazards render on road geometry and never as a shaded polygon over residential areas.

## Seed Leads (unconfirmed but probably real)

1. **The 2023–24 e-DAR-derived black-spot refresh.** MoRTH signalled "real-time mapping" of
   black spots using e-DAR and issued guidelines in **February 2024** for advance action on
   accident spots reported on e-DAR. Next step: RTI/portal watch for the OM implementing
   those guidelines and the refreshed annexure. *If this list is published with lat/long
   instead of chainage, it is the single best day-one dataset in the whole project.*
2. **World Bank iRAD project documents** at `documents.worldbank.org` — likely to contain the
   iRAD results framework, record counts and data-sharing covenants that MoRTH won't give.
3. **National Road Safety Board** (statutory, created under §215D of the MV (Amendment) Act
   2019) — a body with an explicit mandate over road-safety data. Next step: find its
   constitution notification, annual report and CPIO; ask it for the crash-data-access policy.
4. **The 139 identified Mumbai trespassing locations** — held jointly by RPF, GRP and CR/WR.
   Next step: RTI to CPIO, Central Railway (Mumbai CSMT) and CPIO, Western Railway
   (Churchgate) for the list with kilometre-posts.
5. **Tamil Nadu RADMS** and its relationship to iRAD (entry #36).
6. **Kerala** — the MVD "Safe Kerala" programme and KSDMA's ERSS-112 page suggest Kerala is
   the most likely state to hand over structured accident and 112 data on request.
7. **Punjab Sadak Suraksha Force (SSF)** — a dedicated highway-patrol force launched 2024
   with GPS-tracked vehicles and response-time targets; likely holds a geolocated incident
   and response-time log with no publication policy yet. Ask early, before the data culture
   hardens.
8. **ITMS/ANPR camera inventories** for Bengaluru, Hyderabad, Delhi, Pune — point locations
   of enforcement cameras, obtainable by RTI, useful both as a covariate and as a map layer.
9. **NHAI 1033 highway helpline call log** — an incident stream nobody has asked for.
10. **Bloomberg Philanthropies Initiative for Global Road Safety** city partnerships
    (Mumbai, Bengaluru) — these programmes typically produce geocoded crash analyses that
    are shared with partners even when the city publishes nothing.
11. **State Road Safety Councils / Lead Agencies** — mandated in every state after the
    Supreme Court's road-safety directions; each produces an annual report with
    district-level crash tables that rarely reach the internet.
12. **NCRB ADSI microdata / unit-level records** — ADSI publishes tables; the unit records
    behind them exist. Worth one RTI to NCRB asking whether district-level tables beyond
    those printed can be supplied.

## Phase 2 recommendations (ranked)

1. **Ingest the MoRTH/NHAI black-spot annexures and geocode them.** Public, point-level,
   nationally consistent, and no one else has done it (GitHub: 0 repositories). Deliverable:
   a GeoJSON of ~13,795 hazard points with NH, chainage, crash/fatality counts and
   rectification status. This is the project's first genuinely differentiated artifact.
2. **Scrape Bengaluru Traffic Police station-wise stats and parse the Delhi Road Crash
   Reports.** Two metros at police-station granularity, matching the crime layer's join key.
   Small, fast, immediately useful.
3. **File the iRAD RTI in week one, at MoRTH and at 4 states in parallel.** The clock
   (30 days + 30-day appeal + CIC backlog) is the long pole in the entire project. File it
   before you finish the schema design, not after.
4. **Email TRIPC, IIT Delhi for the geocoded Delhi crash point file.** Free, no legal
   process, could arrive in a fortnight, and would let us prototype the point-level UI
   before any RTI lands.
5. **Stand up the OpenCity CKAN API as a mirror/backfill source**, with upstream government
   documents as the citation of record.
6. **Build the Parliament-question watcher** for "black spot", "iRAD", "eDAR", "road
   accident", "trespassing". Cheapest continuous feed of state-wise tables in this domain.
7. **Ingest MoRTH RAI (city + state tables) and NCRB ADSI as the calibration backbone**, with
   an explicit reconciliation note rendered in the UI.
8. **Add GSI Bhukosh landslide points and Bhuvan flood layers** for hill and coastal cities —
   check the Bhuvan terms of use with a lawyer before republishing.
9. **State-by-state ERSS-112 aggregate RTIs**, starting with Kerala, Telangana and Punjab.
10. **Defer eChallan.** High effort, high misinterpretation risk, low decision value.
