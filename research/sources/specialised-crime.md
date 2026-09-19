# Specialised Crime Institutions & Data Pipelines
_Agent: specialised-crime · Researched: 2026-09-19 · Entries: 0 verified / 41 total_

> **Verification warning — read before trusting any URL below.**
> This session's egress proxy blocked **every** `.gov.in`, `.nic.in`, Indian news and Indian
> data-vendor domain, for both WebFetch and `curl` (`CONNECT tunnel failed, response 403`).
> The session's shared WebSearch budget (200/200) was also exhausted after six queries.
> Only `en.wikipedia.org` and `github.com` were fetchable.
> **Therefore no entry is marked `VERIFIED_LIVE` or `VERIFIED_LANDING`.** Every URL recorded
> here was either (a) returned in a WebSearch result index with its page title, or
> (b) taken from a Wikipedia infobox. Both are recorded as `CITED`. Nothing was fetched and
> confirmed. A human with normal network access must re-verify every row before ingestion.
> No URL in this file was constructed by guesswork — where I had no observed URL, the
> `urls` object is omitted and the entry is `UNVERIFIED`.

## Executive summary

- **Specialised institutions hold better geography than they publish.** NCRP, TrackChild, NHRC
  and the SC/ST Protection Cells all capture district and often police-station identifiers in
  their case records, but their *public* output is a state-level PDF or a Parliament answer.
  The gap between held and published granularity is the defining feature of this whole scope.
- **The single biggest analytical hazard is location semantics, and cybercrime is where it
  bites hardest.** Three different bodies publish three different "cybercrime by district"
  numbers that mean opposite things: NCRP complaint counts are ~the **victim's** district of
  residence; I4C "cybercrime hotspot district" analyses are the **offender's** district
  (Jamtara, Nuh/Mewat, Bharatpur/Alwar, Deoghar); NCRB cyber tables are the **police station
  that registered the FIR**, aggregated to state and to 19 metro cities. Plot the wrong one
  and the map brands victim-rich metros as offender havens, or rural Jharkhand as unsafe to
  walk through at night.
- **Best geography in this scope: SC/ST atrocities.** It is the only domain with (i) a
  statutory annual report to Parliament (PoA Act s.21(4)), (ii) dedicated NCRB crime heads
  with district-capable tables, (iii) honest *offence-location* semantics (contact crimes,
  FIR filed where it happened), and (iv) a genuinely **sub-district official geography** —
  the "atrocity-prone areas" that states must identify under s.17(1) / Rule 3(1).
- **Finest geography in principle: custodial deaths.** An NHRC custodial-death intimation
  names an exact police station or jail — a *point*. Volume is low (order 150-175 police-custody
  deaths/yr, ~1,500-2,700 including judicial custody) but precision is perfect and the
  accountability value is high. Published output is still only state-level.
- **Cybercrime is the fastest-growing category and is the most nationally-collected — and it
  is the one most likely to make the map lie.** NCRP complaints rose from 4.52 lakh (2021) to
  19.18 lakh (2024); 6.59 million complaints 2021–Jun 2025. It *is* geolocatable to the
  victim, which is what a resident cares about — but "cybercrime in your area" is a
  category error for a neighbourhood-safety map, since the harm is not spatial.
- **Economic crime has effectively no usable geography.** RBI fraud data is by reporting
  *bank group*; ED/SFIO/SEBI case geography is the accused entity's registered office or the
  ED zonal office. All three collapse onto Mumbai/Delhi. Catalogue for a "white-collar" layer,
  never for a street map.
- **Narcotics data measures enforcement deployment, not drug presence.** NCB seizure tables are
  by *seizure location* — borders, ports, highways, airports — and NCB's own geography is
  ~23 zones, not districts. The only prevalence source is the AIIMS/NDDTC
  *Magnitude of Substance Use in India* survey, designed for state-level estimates.
- **Trafficking has a source/destination trap identical to cybercrime's victim/offender trap.**
  NCRB records the FIR location, which for trafficking is usually the *rescue/destination*
  city. Mapping it marks Delhi and Mumbai as trafficking hotspots and renders the source
  districts (which are the actual problem) invisible.
- **Two portals carry a third, rarely-noticed geography: the service-delivery point.**
  One Stop Centres (Sakhi) and CHILDLINE report at the *centre's* location, so their coverage
  map is a map of where centres exist, not where harm occurs. SHe-Box adds a fourth: the
  **workplace's** location.
- **CHILDLINE's 2021 transfer to MHA control (police personnel replacing social workers on
  1098) is a series break.** Any pre-2021/post-2021 comparison of 1098 call volumes is invalid.
- **Realistic ceiling for this scope: district-level, annual, 12–24 month lag**, with two
  exceptions worth chasing — NCRP (state/district, near-monthly, short lag) and NHRC
  custodial deaths (facility-point, continuous intimation, but state-level publication).

## Source entries

### 1. National Cyber Crime Reporting Portal (NCRP)
The front door for all citizen cybercrime reporting in India, launched 30 Aug 2019. Complaints
are filed online by the citizen, who supplies state/district, and are routed to the police
station with jurisdiction. MHA material states the portal includes "National/State/District-Level
monitoring dashboards" — these are internal law-enforcement dashboards, not public.
**Location semantics: the complainant (victim) selects their own state/district, so aggregates
approximate victim residence.** This is genuinely different from, and better than, FIR geography.

```
id: specialised-crime-ncrp-portal
publisher: Indian Cyber Crime Coordination Centre (I4C), MHA
tier: 2 | geo_granularity: district | unit_of_record: case-record
time_start: 2019-08-30 | time_latest: live | cadence: realtime | lag: n/a
access: login (dashboards are LEA-only; public site is complaint-filing only)
verification: CITED (cybercrime.gov.in given as I4C's official site in Wikipedia infobox;
  not fetched — domain egress-blocked)
```

### 2. Indian Cyber Crime Coordination Centre (I4C)
Attached office of MHA w.e.f. 1 July 2024; scheme approved Oct 2018 (₹415.86 cr), later ₹782 cr.
Seven verticals per Wikipedia: National Cyber Crime **Threat Analytics Unit (TAU)**, NCRP,
National Cyber Crime Training Centre, Cyber Crime Ecosystem Management Unit, National Cyber
Crime Research & Innovation Centre, National Cyber Crime Forensic Laboratory ecosystem, and
the Platform for Joint Cyber Crime Investigation Team. **TAU is the unit that produces the
"cybercrime hotspot district" analyses — these are OFFENDER geography.** I4C has publicly
flagged clusters around Jamtara (JH), Nuh/Mewat (HR), Bharatpur & Alwar (RJ), Deoghar (JH).

```
id: specialised-crime-i4c | tier: 2 | geo_granularity: district
unit_of_record: narrative-document | cadence: irregular | access: blocked
verification: CITED | landing: https://i4c.mha.gov.in/ncrp.aspx (search-index title
  "Indian Cybercrime Coordination Centre"; WebFetch returned EGRESS_BLOCKED)
CRITICAL: offender-location, not victim-location. Never merge with entry 1 or 3.
```

### 3. OGD resource — "State/UT-wise Details of Statistics on NCRP Related to Cyber Fraud Cases as on 28-02-2025"
The most concretely ingestible cybercrime artifact found. A data.gov.in resource whose exact
title was returned by the search index. data.gov.in normally offers CSV/XLSX/JSON plus a
documented API key (data.gov.in API), and publishes under **GODL-India**.

```
id: specialised-crime-ncrp-ogd-statewise | publisher: I4C/MHA via NIC OGD Platform
tier: 1 | geo_granularity: state | unit_of_record: aggregate-count
time_latest: 2025-02-28 | cadence: irregular | access: open-download | machine_readable: 4
license: GODL-India (OGD default; unconfirmed for this resource)
url: https://www.data.gov.in/resource/stateut-wise-details-statistics-national-cyber-crime-reporting-portal-ncrp-related-cyber
verification: CITED — exact title seen in search index; WebFetch EGRESS_BLOCKED.
NOTE: data.gov.in also exposes state mirrors (up.data.gov.in, karnataka.data.gov.in) that
sometimes carry resources the main portal's search does not surface.
```

### 4. CFCFRMS + Helpline 1930 (Citizen Financial Cyber Fraud Reporting & Management System)
Module inside NCRP connecting 85+ banks/payment intermediaries/wallets, enabling same-day
freezing of defrauded funds. Reported volumes: financial-fraud complaints rose 2.62 lakh (2021)
to 24.02 lakh (2025). **The "amount saved/lien-marked" series is the operationally interesting
one and is reported in Parliament answers, usually state-wise.**

```
id: specialised-crime-cfcfrms-1930 | tier: 2 | geo_granularity: state
unit_of_record: case-record | cadence: realtime | access: login | verification: CITED
Location semantics: victim's bank account / victim's declared district. Offender's mule-account
district is held but never published — that is the map everyone actually wants.
```

### 5. CERT-In incident statistics
Formed 19 Jan 2004 under IT Act s.70B. The 28 Apr 2022 Directions mandate reporting of cyber
incidents **within six hours**. CERT-In publishes annual reports with incidents-handled counts.
**No geography whatsoever** — incidents are attributed to organisations/ASNs, not places.
Catalogue for national-trend context only.

```
id: specialised-crime-cert-in | tier: 2 | geo_granularity: national
unit_of_record: aggregate-count | cadence: annual | access: blocked (this session)
url landing: https://www.cert-in.org.in (Wikipedia infobox) | verification: CITED
priority: 2
```

### 6. Sanchar Saathi / Chakshu (DoT)
Web portal May 2023; mobile app Jan 2025. Chakshu is the fraud-communication reporting module.
Reported: >700,000 lost/stolen handsets recovered by Dec 2025; ~2,000 fraud reports/day via app.
**Geography is the telecom subscriber's LSA (Licensed Service Area), not a district** — LSAs
are mostly state-shaped but Delhi/Mumbai/Kolkata are separate metro LSAs and some LSAs span
states. A real reprojection problem for any map.

```
id: specialised-crime-sancharsaathi-chakshu | publisher: Department of Telecommunications
tier: 2 | geo_granularity: state (LSA, approximately) | cadence: realtime
url landing: https://sancharsaathi.gov.in (Wikipedia infobox) | verification: CITED
```

### 7. MHA Parliament answers on cybercrime
The de facto publication channel for NCRP/I4C numbers. Two concrete PDFs surfaced in the
search index: `LS02122025/452.pdf` (Lok Sabha, 2 Dec 2025) and `LS14032023/2291.pdf`
(14 Mar 2023, missing children). These answers routinely carry **state/UT-wise annexures** and
occasionally district lists. They are the cheapest route to series that are otherwise unpublished.

```
id: specialised-crime-mha-parliament-answers | tier: 3 | geo_granularity: state
unit_of_record: aggregate-count | cadence: irregular | formats: ["PDF"] | machine_readable: 1
urls: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/LS02122025/452.pdf
verification: CITED | ingest_difficulty: 4 (PDF table extraction, no stable schema)
NOTE: path pattern MHA1/Par2017/pdfs/par<YYYY>-pdfs/<HOUSE><DDMMYYYY>/<qno>.pdf is
predictable enough to enumerate in Phase 2 — but confirm before building a crawler.
```

### 8. NCW "Statistical Overview of Complaints"
A live nature-wise complaint statistics page on the NCW application server. This is the closest
thing to a refreshing, category-broken-down complaint feed for crimes against women.

```
id: specialised-crime-ncw-complaint-stats | publisher: National Commission for Women
tier: 3 | geo_granularity: state | unit_of_record: aggregate-count
cadence: monthly (believed) | access: scrape | machine_readable: 2 | formats: ["HTML"]
url: https://ncwapps.nic.in/frmComp_stat_Overview.aspx (search-index title
  "Statistical Overview of Complaints") | verification: CITED
Companion complaint-intake system: https://ncwapps.nic.in/onlinecomplaintsv2/
```

### 9. NCW Annual Report
Statutory body est. 31 Jan 1992 under the National Commission for Women Act, 1990. The
2023–24 English annual report PDF was surfaced by the search index on NCW's CDN.
2025 figures reported in press: 7,698 complaints; Delhi 688, Maharashtra 473, MP 351,
Bihar 342, Haryana 306.

```
id: specialised-crime-ncw-annual-report | tier: 3 | geo_granularity: state
unit_of_record: aggregate-count | cadence: annual | lag: ~12 months | formats: ["PDF"]
url: https://cdn.ncw.gov.in/wp-content/uploads/2025/03/NCWAnnualReport20232024Eng.pdf
verification: CITED (search-index result titled "Ncw") | machine_readable: 1
CAVEAT — severe: NCW complaints are self-selected letters/emails to a Delhi commission.
Delhi's #1 rank reflects proximity and awareness, not incidence. Per-capita normalisation
makes this WORSE, not better. This is an access-to-redress indicator, not a crime indicator.
```

### 10. OGD — NCW state-wise complaints 2018–2023
```
id: specialised-crime-ncw-ogd | tier: 1 | geo_granularity: state | cadence: one-off
time_start: 2018 | time_latest: 2023 | access: open-download | license: GODL-India
url: https://up.data.gov.in/resource/stateut-wise-details-total-number-complaints-received-national-commission-women-ncw-2018
keyword hub: https://www.data.gov.in/keywords/NCW  | verification: CITED
Related resource (same platform): year-wise NCW complaints on workplace sexual harassment,
2020–2023 — https://www.data.gov.in/resource/year-wise-number-complaints-received-national-commission-womenncw-related-investigation
```

### 11. SHe-Box (Sexual Harassment electronic Box)
Portal of the Ministry of Women & Child Development for complaints under the Sexual Harassment
of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013. Complaints route to the
employer's **Internal Committee** or, for small/unorganised workplaces, to the **Local Committee
constituted by the District Officer** in each district (and optionally at block level).

```
id: specialised-crime-shebox | tier: 3 | geo_granularity: district (District Officer /
  Local Committee is a genuine district-level statutory unit) | unit_of_record: case-record
access: login | verification: UNVERIFIED (portal domain not confirmed this session)
LOCATION SEMANTICS — unique in this scope: the geography is the WORKPLACE, not the victim's
home and not a police station. A district with many offices will dominate regardless of
residential safety. Do not merge with any residence-based layer.
```

### 12. One Stop Centres (Sakhi) / Mission Shakti MIS
OSCs are district-sited facilities providing integrated support to women affected by violence,
under the MWCD Mission Shakti umbrella (Sambal/Samarthya sub-schemes). Case counts are reported
per centre, so the district identifier is exact.

```
id: specialised-crime-osc-sakhi | tier: 3 | geo_granularity: district
unit_of_record: case-record | cadence: monthly (MIS, internal) | access: rti-only
verification: UNVERIFIED | priority: 3
LOCATION SEMANTICS: service-delivery point. Coverage = where OSCs exist. A district with no
functioning OSC shows zero cases and would render as "safe". This is the most dangerous
false-negative pattern in the whole scope.
how_to_obtain: RTI to MWCD (Mission Shakti division) for OSC-wise monthly case registers;
state Women & Child Development departments hold the same MIS and often answer faster.
```

### 13. Women Helpline 181
Universalised women's helpline; calls are answered at state-run call centres and referred to
police/OSC. Unit is a call, geography is the caller's state (call-centre catchment).

```
id: specialised-crime-whl-181 | tier: 3 | geo_granularity: state | unit_of_record: case-record
cadence: monthly (internal) | access: rti-only | verification: UNVERIFIED | priority: 2
```

### 14. NCPCR complaint systems — e-Baalnidan, POCSO e-Box, Baalswaraj, SAHARA
NCPCR constituted 5 Mar 2007 under s.3 of the Commissions for Protection of Child Rights Act,
2005. Portals confirmed via Wikipedia: **e-Baalnidan** (all child-rights complaints other than
POCSO), **POCSO e-Box** (child sexual abuse), **SAHARA** (children of CAPF personnel),
a J&K/Ladakh portal, and **Baalswaraj** (real-time tracking of children in need of care and
protection, with modules for COVID-affected children, street-children rescue, and POCSO case
tracking). Baalswaraj is a **child-record-level tracking system** — the highest-value asset here.

```
id: specialised-crime-ncpcr-portals | tier: 3 | geo_granularity: district
unit_of_record: case-record | access: login | verification: CITED (ncpcr.gov.in from
  Wikipedia infobox; portal names from the same article) | priority: 3
No public statistical output found. State Commissions (SCPCRs) mirror this at state level.
```

### 15. TrackChild / Khoya-Paya (missing & found children)
National database of missing and recovered children, used by police across state boundaries.
2024 figures reported: 147,175 children tracked, 67.1% recovery, ~36,000 still missing;
West Bengal 22,742 cases, Madhya Pradesh 19,131. **Reported non-reporting states: Delhi, Punjab,
Nagaland, Jharkhand, Tamil Nadu, West Bengal, J&K, Andhra Pradesh** — a coverage hole that
must be rendered as "no data", never as zero.

```
id: specialised-crime-trackchild | publisher: MWCD / NIC | tier: 2
geo_granularity: police-station (held) / state (published) | unit_of_record: victim-record
cadence: realtime (portal) / irregular (publication) | access: login
urls landing: https://trackthemissingchild.gov.in ; india.gov.in service page
  https://www.india.gov.in/category/benefits-social-development/subcategory/women-children/details/portal-for-missing-and-tracked-children
OGD slice: https://karnataka.data.gov.in/resource/year-wise-cases-missing-children-reported-track-child-portal-including-maharashtra-during
verification: CITED | priority: 4
UNIQUE VALUE: TrackChild holds TWO geographies per child — the police station of the
missing-report and the place of recovery. That is an origin-destination pair, i.e. the only
trafficking-corridor dataset in Indian public administration. Chase this one.
CAVEAT: recovery rates are contaminated by data-entry discipline (Kerala 95.0%, Uttarakhand
96.4% vs seven states reporting zero) — this measures bureaucratic diligence as much as outcomes.
```

### 16. CHILDLINE 1098
Founded 1996 (Jeroo Billimoria); ~1 million calls/month; 50 lakh calls answered and 3.95 lakh
children assisted Apr 2020–Mar 2021; present in 602+ districts, 144+ railway stations,
11 bus terminals; contact centres in Mumbai, Delhi, Kolkata, Bengaluru, Chennai.
**In 2021 CHILDLINE was brought under the administrative control of MHA and police personnel
replaced social workers on the line — a hard series break.**

```
id: specialised-crime-childline-1098 | tier: 4 (NGO-origin) -> 2 (post-2021 MHA)
geo_granularity: district | unit_of_record: case-record | time_start: 1996
cadence: monthly (internal) | access: on-request | verification: CITED
url landing: https://www.childlineindia.org/ (Wikipedia infobox)
caveats: ["2021 transfer to MHA control changes who answers and what gets logged — do not
  compare across 2021", "call volume tracks awareness campaigns, not incidence",
  "geography is the contact centre's catchment, not the child's location"]
```

### 17. POCSO case data & Fast Track Special Courts
POCSO cases appear as a dedicated NCRB crime head and in Department of Justice FTSC monitoring.
**Location semantics are good** — POCSO is a contact offence, so the FIR police station is
normally the offence location. Best-semantics child dataset.

```
id: specialised-crime-pocso-cases | tier: 3 | geo_granularity: district
unit_of_record: case-record | taxonomy: IPC+SLL (POCSO Act) | cadence: annual
verification: UNVERIFIED (no FTSC portal URL confirmed this session) | priority: 3
how_to_obtain: Department of Justice FTSC monthly progress reports (state/district-wise court
counts and disposals); NJDG for court-level pendency; RTI to DoJ if not public.
```

### 18. Annual Report u/s 21(4), SC/ST (Prevention of Atrocities) Act, 1989 — **the flagship of this scope**
Statutory report laid before both Houses. Rule 18 requires states to send annual reports to the
Union by 31 March. Content is built on NCRB SC/ST crime heads plus state returns.
Concrete artifacts surfaced in the search index: a landing page listing PoA annual reports, the
2017 report PDF, and an older `arpoa13.pdf`. PIB reports 53,372 cases registered under the Act
in 2023. Pendency: 147,545 (92.97%) SC cases pending in 2019, rising to 254,475 (96.1%) in 2021;
ST 26,025 (90.72%) in 2019. Conviction rates historically very low (2.31% of disposed cases in
2002; PM stated <30% in 2009; ~2% for rape cases). Exclusive Special Courts: 194 across 11
states in 2019, down to 176 by 2021.

```
id: specialised-crime-poa-annual-report | publisher: Department of Social Justice &
  Empowerment, Ministry of Social Justice & Empowerment | tier: 1
geo_granularity: district (capable; state guaranteed) | unit_of_record: aggregate-count
time_start: ~1990 | time_latest: 2023 (cases) | cadence: annual | lag: 18-30 months
taxonomy: IPC+SLL (PoA Act + PCR Act heads) | formats: ["PDF"] | machine_readable: 1
access: open-download | license: GODL-India (assumed) | ingest_difficulty: 4
priority: 5 | verification: CITED
urls: landing https://socialjustice.gov.in/whats-new/77881
      data   https://socialjustice.gov.in/writereaddata/UploadFile/Annual%20Report-PoA-2017636988121973975658.pdf
      data   https://socialjustice.gov.in/writereaddata/UploadFile/arpoa13.pdf
LOCATION SEMANTICS: offence location. PoA offences are contact/place-bound, the FIR is filed
where it happened, and the Act's own machinery (Protection Cells, Special Courts) is
district-organised. This is the most honest fine geography in the whole scope.
CAVEAT — denominator: rates MUST use SC/ST population as denominator, not total population.
Using total population understates atrocity rates in low-SC-share districts and is the classic
error in press coverage of this series.
```

### 19. "Atrocity-prone areas" notified under s.17(1) PoA Act / Rule 3(1)
The Act authorises identification of atrocity-prone areas so that preventive measures
(including firearms-licence restrictions and enhanced monitoring) can be applied.
**These notifications are made by state governments at village / police-station / block level.**

```
id: specialised-crime-atrocity-prone-areas | tier: 2 | geo_granularity: police-station
unit_of_record: boundary-polygon (or named-place list) | cadence: irregular
access: rti-only | verification: UNVERIFIED | priority: 4 | ingest_difficulty: 5
how_to_obtain: RTI to each state's Social Welfare / SC-ST Welfare Department and to the state
SC/ST Protection Cell (state police HQ), asking for "the list of areas identified as
atrocity-prone under Section 17(1) of the SC/ST (PoA) Act, 1989 read with Rule 3(1) of the
1995 Rules, with the notification numbers and dates". Several states publish these as district
collector notifications in the state gazette.
*** THIS IS THE BEST SEED LEAD IN THE ENTIRE DOSSIER — it is the only sub-district,
officially-designated crime geography I found anywhere in this scope. ***
```

### 20. NCDHR / NDMJ analysis — "Five Years of Caste-Based Atrocity"
Civil-society reanalysis of NCRB SC/ST data, Feb 2026. Useful as an independent cross-check and
for the definitional critique of the official series.
```
id: specialised-crime-ncdhr-atrocity | publisher: National Campaign on Dalit Human Rights
tier: 4 | geo_granularity: state | cadence: one-off | formats: ["PDF"] | access: open-download
url: https://www.ncdhr.org.in/wp-content/uploads/2026/02/Five-Years-of-Caste-Based-Atrocity-Feb-9-2026-for-web.pdf
verification: CITED | priority: 2
```

### 21. Evaluation Study on Functioning of SC/ST Protection Cells
Ministry evaluation summary report. Documents how the district-level Protection Cell machinery
actually works (or does not), which is exactly what determines whether district PoA counts are
comparable across states.
```
id: specialised-crime-scst-protection-cells-eval | tier: 3 | geo_granularity: state
formats: ["PDF"] | cadence: one-off | access: open-download | verification: CITED
url: https://socialjustice.gov.in/public/ckeditor/upload/Summary%20Report-Evaluation%20of%20SCST%20Protection%20Cells_1648793671.pdf
priority: 2 | notes: read this before trusting cross-state comparison of PoA registration rates.
```

### 22. Anti-Human Trafficking Units (AHTUs)
MHA-funded district-level police units. AHTU-wise rescue/case data is collected centrally but
not published. Each AHTU maps to a district, so the latent granularity is district.
```
id: specialised-crime-ahtu | publisher: MHA Anti-Trafficking Cell (CS Division)
tier: 2 | geo_granularity: district | unit_of_record: case-record | access: rti-only
verification: UNVERIFIED | priority: 3 | ingest_difficulty: 5
how_to_obtain: RTI to MHA Anti-Trafficking Cell for AHTU-wise annual returns; parallel RTIs to
state CIDs which run the AHTUs. Parliament answers occasionally table AHTU counts by state.
```

### 23. NCRB Human Trafficking chapter
Dedicated chapter in Crime in India with victims disaggregated by age/sex and by purpose of
trafficking, plus rescued/repatriated counts. State and metro-city level.
```
id: specialised-crime-ncrb-trafficking | tier: 1 | geo_granularity: state
unit_of_record: victim-record (aggregated) | cadence: annual | lag: 12-18 months
taxonomy: NCRB-heads | verification: UNVERIFIED | priority: 3
*** LOCATION TRAP: the FIR is registered where the victim is RESCUED — i.e. the destination.
Mapping this marks Delhi/Mumbai/Bengaluru as trafficking hotspots and makes the source
districts, which are the actual policy problem, invisible. If we render trafficking at all, it
must be rendered as an origin-destination flow, never as a choropleth. ***
```

### 24. UNODC South Asia / Global Report on Trafficking in Persons — India chapter
Country-level narrative and comparative statistics; useful for definitional alignment with
international standards, not for geography.
```
id: specialised-crime-unodc-india | publisher: UN Office on Drugs and Crime | tier: 4
geo_granularity: national | cadence: irregular | access: open-download
verification: UNVERIFIED (unodc.org EGRESS_BLOCKED this session) | priority: 1
```

### 25. NCB Annual Report
NCB established 17 Mar 1986 under the NDPS Act, 1985 / PITNDPS Act, 1988. 2024: narcotics worth
₹25,330 crore seized, +55% on 2023; methamphetamine 34→80 quintals; cocaine 292→1,426 kg;
mephedrone 688→3,391 kg. NCB's operating geography is **zones**, not districts — Mumbai, Indore,
Kolkata, Delhi, Chennai, Lucknow, Jodhpur, Chandigarh, Jammu, Ahmedabad, Bengaluru, Guwahati,
Patna, plus Agartala, Raipur, Visakhapatnam, Gorakhpur, Jalpaiguri, Itanagar, Bhopal, Cochin,
Jaipur, Srinagar, Amritsar, Dehradun, Mandi.
```
id: specialised-crime-ncb-annual-report | tier: 2 | geo_granularity: state (via zone)
unit_of_record: aggregate-count | cadence: annual | formats: ["PDF"] | machine_readable: 1
url: https://narcoticsindia.nic.in/Publication/ncb-annual-report-2024.pdf
landing: https://narcoticsindia.nic.in/  | verification: CITED | priority: 3
WARNING: a second URL (…/Upload/UploadFiles/AnnualReport2024.pdf) appeared only in a search
engine's prose summary, not in its result index. Treat it as unconfirmed; do not hard-code.
```

### 26. NCB state-wise DLEA seizure tables
"State-wise seizure of drugs all over India by all DLEAs" — a per-year PDF. The closest thing
to a state seizure panel.
```
id: specialised-crime-ncb-seizure-statewise | tier: 2 | geo_granularity: state
unit_of_record: aggregate-count | time_latest: 2024 | cadence: annual | formats: ["PDF"]
url: https://narcoticsindia.nic.in/ImportantSeizure/seizure2024.pdf
verification: CITED (exact index title observed) | priority: 3
*** LOCATION SEMANTICS: seizure location = INTERDICTION EFFORT, not drug prevalence.
This series tracks border districts, ports, airports and national highways. Punjab's numbers
are about the Pakistan border; Gujarat's are about the coast. Rendering seizures as "drug
crime in your neighbourhood" is straightforwardly false. ***
```

### 27. "Magnitude of Substance Use in India" — AIIMS / NDDTC national survey
The only *prevalence* (as opposed to enforcement) source for narcotics. Commissioned by MoSJE,
executed by the National Drug Dependence Treatment Centre, AIIMS New Delhi. Household survey +
respondent-driven sampling of dependent users. Sample designed for **state-level** estimates.
```
id: specialised-crime-nddtc-substance-use | tier: 1 | geo_granularity: state
unit_of_record: survey-respondent | time_latest: 2019 | cadence: one-off | formats: ["PDF"]
access: open-download | verification: UNVERIFIED (no URL confirmed this session) | priority: 3
caveats: ["survey prevalence, NOT crime — different universe from every other entry here",
  "district estimates are not statistically supportable from this sample design",
  "one-off 2019; a repeat has been discussed but not confirmed"]
how_to_obtain: MoSJE publications page; NDDTC/AIIMS site. Search exact title
"Magnitude of Substance Use in India 2019".
```

### 28. RBI bank fraud statistics
RBI's Annual Report carries a frauds section; the *Report on Trend and Progress of Banking in
India* carries more; the Database on Indian Economy (DBIE) is the structured outlet.
```
id: specialised-crime-rbi-fraud | publisher: Reserve Bank of India | tier: 3
geo_granularity: national | unit_of_record: aggregate-count | cadence: annual
url landing: https://www.rbi.org.in (Wikipedia infobox) | verification: CITED | priority: 2
*** NO USABLE GEOGRAPHY: frauds are tabulated by BANK GROUP (PSB / private / foreign) and by
fraud category, not by place. The branch where a fraud occurred is held in RBI's CRILC/CFR but
never published. Do not attempt to map. ***
caveats: ["date-of-reporting vs date-of-occurrence: RBI's headline counts are by year of
  REPORTING, and frauds are often reported years after occurrence — the series is not a
  time series of events", "amount involved is not amount lost"]
```

### 29. Enforcement Directorate (ED)
Est. 1 May 1956. Enforces FEMA 1999, PMLA 2002, FEOA 2018. 5 regional offices (Mumbai, Chennai,
Chandigarh, Kolkata, Delhi), 16 zonal offices, 14 sub-zonal offices. As of 31 Jan 2023:
5,906 ECIRs registered, 513 persons arrested; through Jul 2023, 31 PMLA trials completed with
29 convictions (93.54%).
```
id: specialised-crime-ed-cases | tier: 3 | geo_granularity: state (via zonal office)
unit_of_record: case-record | cadence: annual/irregular | access: blocked
url landing: https://enforcementdirectorate.gov.in (Wikipedia infobox) | verification: CITED
priority: 1 | notes: geography is the ZONAL OFFICE that registered the ECIR — an
administrative artefact of ED's own org chart, not a crime location.
```

### 30. Serious Fraud Investigation Office (SFIO)
GoI resolution 2 Jul 2003; statutory status under s.211, Companies Act 2013. Investigates
corporate fraud on referral (Registrar of Companies, special resolution, public interest,
government request).
```
id: specialised-crime-sfio | tier: 3 | geo_granularity: national
unit_of_record: case-record | cadence: annual | url landing: https://sfio.gov.in
verification: CITED (Wikipedia) | priority: 1
notes: case geography would be the accused company's registered office — a corporate-filing
address, frequently a nominee/CA office. Useless for spatial crime mapping.
```

### 31. SEBI enforcement / adjudication orders
Statutory 30 Jan 1992 under SEBI Act 1992. HQ Mumbai (BKC); regional offices Northern (Delhi),
Eastern (Kolkata), Southern (Chennai), Western (Ahmedabad); 16 of 17 local offices closed
Jun 2023. SEBI publishes every order as a dated PDF plus an annual report.
```
id: specialised-crime-sebi-orders | tier: 3 | geo_granularity: national
unit_of_record: narrative-document | cadence: daily (orders) | formats: ["PDF","HTML"]
url landing: https://sebi.gov.in (Wikipedia infobox) | access: open-download
verification: CITED | machine_readable: 2 | priority: 1
notes: high-volume, well-structured order corpus — attractive for NLP, worthless for geography.
The June 2023 closure of 16 local offices further centralises any location signal onto Mumbai.
```

### 32. NHRC custodial death statistics — **best spatial precision in this scope**
NHRC constituted 12 Oct 1993 under the Protection of Human Rights Act, 1993. It oversees
25 State Human Rights Commissions. Reported figures: >11,650 custodial deaths (police +
judicial) 2016–2022; 2,739 custodial deaths in 2024 of which 155 in police custody; annual
police-custody deaths 140–176 across 2021–2026; ~90% of custodial-death complaints concern
judicial custody. Apr 2018–Mar 2023: 687 deaths registered, Gujarat 81, Maharashtra 80, MP 50,
Bihar 47. 2025–26: Bihar 19, Rajasthan 18 police-custody deaths. Only one instance of
disciplinary action reported over five years.
```
id: specialised-crime-nhrc-custodial | tier: 3 | geo_granularity: point (the custodial
  facility) held / state published | unit_of_record: case-record
time_start: 1993 | cadence: realtime (intimation) / annual (report) | access: blocked
url landing: https://nhrc.nic.in/ (Wikipedia infobox);
  press-release path observed in index: https://nhrc.nic.in/media/press-release/70-37
verification: CITED | priority: 4 | ingest_difficulty: 4
*** LOCATION SEMANTICS — the cleanest in this dossier. A custodial death intimation names the
exact police station or jail. That is a true point, with no ambiguity about victim vs offender
vs reporting office: all three coincide. For a police-accountability layer this is ideal.
The constraint is that NHRC publishes only state totals; the facility identifier sits in the
case file. ***
NOTE: the widely-cited "24-hour intimation" requirement comes from NHRC's own directions to
Chief Secretaries/DGPs (1993 onwards), not from the PHRA text — verify the exact instrument
before citing it in the product.
caveats: ["police custody vs judicial custody are routinely conflated in press coverage — the
  ~10x difference between 155 and 2,739 for 2024 is exactly this", "NHRC counts INTIMATIONS
  received, so a state with better compliance looks worse", "NHRC has no jurisdiction over the
  armed forces in the same way, and J&K historically had a separate regime"]
```

### 33. State Human Rights Commissions (25)
Per-state mirrors of NHRC with their own annual reports and complaint statistics; formation
dates 1994–2019 (most recent: Telangana, 2019). Coverage is uneven and several are dormant.
```
id: specialised-crime-shrc | tier: 3 | geo_granularity: district (complaint origin)
cadence: annual | access: scrape | verification: CITED (count and dates from Wikipedia)
priority: 2 | notes: 25 separate sites, 25 separate formats. Phase 3 work, not Phase 2.
```

### 34. Police Complaints Authorities (state and district)
Established following the Supreme Court's directions in *Prakash Singh v Union of India* (2006);
exist as State PCAs with District PCAs beneath them. Publication is sporadic to nonexistent.
```
id: specialised-crime-pca | tier: 3 | geo_granularity: district | unit_of_record: case-record
cadence: irregular | access: rti-only | verification: CITED (two-tier structure confirmed via
  Wikipedia; no data product found) | priority: 2
how_to_obtain: RTI to each State PCA for year-wise complaints received/disposed by district and
by nature of allegation. CHRI (Commonwealth Human Rights Initiative) tracks PCA compliance and
is the best civil-society aggregator to approach first.
```

### 35. MHA communal incident statistics
Published almost exclusively through Parliament answers rather than a standing report series.
PRS Legislative Research has compiled a 2005–2017 table of incidents / deaths / injured by year.
2005–2009: ~130 deaths/year, 24 of 35 states/UTs reporting incidents; Maharashtra 700 incidents
(highest); MP highest fatality rate per 100,000; India-wide 0.01 deaths per 100,000.
2012: 93 deaths (48 Muslims, 44 Hindus, 1 police official). 2013: 107 killed (66 Muslims,
41 Hindus).
```
id: specialised-crime-mha-communal | tier: 3 | geo_granularity: state | cadence: irregular
unit_of_record: aggregate-count | access: blocked | verification: CITED
priority: 2
caveats: ["no standing publication — availability depends on which MP asked a question that
  year", "'communal incident' has no stable statutory definition; classification is a state
  police judgement call and is politically contested", "counts of incidents and counts of
  deaths move independently and are often conflated"]
```

### 36. Varshney–Wilkinson Hindu–Muslim riots dataset (and successors)
Event-level dataset of Hindu–Muslim riots compiled by Ashutosh Varshney and Steven Wilkinson
from *Times of India* reports, underpinning Varshney's *Ethnic Conflict and Civic Life: Hindus
and Muslims in India*. Widely understood to cover 1950–1995 at town/city level and to be
archived with a US social-science data archive.
```
id: specialised-crime-varshney-wilkinson | publisher: Varshney & Wilkinson (academic)
tier: 4 | geo_granularity: city | unit_of_record: incident-point | time_start: 1950
time_latest: 1995 | cadence: one-off | access: on-request
verification: UNVERIFIED — the Wikipedia biography of Varshney confirms the book and his work
  on ethnic conflict but does NOT name the dataset, its years, or an archive. The dedicated
  book article returned HTTP 404. A GitHub repository search for the dataset returned 0 results.
  NO URL RECORDED because none was observed.
priority: 2 | ingest_difficulty: 3
how_to_obtain: search ICPSR (Inter-university Consortium for Political and Social Research) for
"Varshney-Wilkinson Dataset on Hindu-Muslim Violence in India"; failing that, contact the Brown
University Center for Contemporary South Asia directly. For post-1995 successors, evaluate
ACLED's India event data (geocoded, event-level, high cadence) — named here as a lead only,
with no URL, since it could not be checked in this session.
caveats: ["press-report-derived: coverage tracks Times of India editions and city bureaus, so
  small-town riots are systematically under-recorded", "ends 1995 — three decades stale for a
  live map; usable as historical context only"]
```

### 37. ZIPNET (Zonal Integrated Police Network)
Delhi-Police-hosted inter-state police information sharing network for missing persons,
unidentified bodies, stolen vehicles and arrested persons, covering the NCR states and several
others. Publishes **individual missing-person records** with the reporting police station.
```
id: specialised-crime-zipnet | tier: 2 | geo_granularity: police-station
unit_of_record: victim-record | cadence: realtime | access: scrape
url landing: https://zipnet.delhipolice.gov.in (domain observed only in my own connectivity
  probe, NOT in a search index — treat as unconfirmed)
verification: UNVERIFIED | priority: 4 | ingest_difficulty: 3
WHY IT MATTERS: one of the very few Indian sources that publishes record-level data carrying a
police-station identifier. If it is live and scrapeable it is a rare police-station-granularity
feed. Verify first; check robots.txt and ToU before any harvesting.
```

### 38. NCRB missing-persons tables
Crime in India's missing persons chapter: persons reported missing / traced, by sex and
child/adult, at state and metro-city level. 1,21,351 children missing as of 2021 per NCRB.
```
id: specialised-crime-ncrb-missing | tier: 1 | geo_granularity: state | cadence: annual
lag: 12-18 months | verification: CITED (2021 figure via Wikipedia) | priority: 3
Third-party structured mirrors observed in the search index:
  https://dataful.in/datasets/18468/ ("NCRB: Year, State, and Gender Wise Number Of Children…")
  https://www.indiastat.com/table/southern-region/crime-and-law/state-wise-number-missing-children-as-per-track-ch/1445283
caveats: ["'missing' is a stock/flow muddle — reported-in-year vs still-untraced-at-year-end
  are different numbers and are constantly conflated in reporting"]
```

### 39. Wildlife Crime Control Bureau (WCCB)
Statutory provisions in force 6 Jun 2007 under the Wild Life (Protection) Amendment Act, 2006;
operational 2008. HQ Trikoot-1, Bhikaji Cama Place, New Delhi. Involved in the Wildlife
Enforcement Monitoring System with UNU and Columbia's Earth Institute.
```
id: specialised-crime-wccb | tier: 2 | geo_granularity: state | unit_of_record: case-record
cadence: irregular | url landing: https://wccb.gov.in (Wikipedia infobox)
verification: CITED | priority: 1
notes: geography is the seizure/enforcement location, same interdiction-effort bias as NCB.
Irrelevant to neighbourhood safety; relevant only to a separate environmental-crime layer.
```

### 40. FSSAI food-sample surveillance and enforcement statistics
Est. 5 Sep 2008 under the Food Safety and Standards Act, 2006. Lab network: 22 referral labs,
72 State/UT labs, 112 notified NABL-accredited private labs. FSSAI reports samples analysed,
found non-conforming, and prosecutions launched, state-wise, in its annual report.
```
id: specialised-crime-fssai-surveillance | tier: 3 | geo_granularity: state
unit_of_record: aggregate-count | cadence: annual | url landing: https://www.fssai.gov.in
verification: CITED (Wikipedia infobox) | priority: 1
notes: sample-collection geography = where food safety officers were deployed. Same
enforcement-effort bias. A cited survey found 73% of 12,308 respondents had little or no
confidence in FSSAI/state regulators — relevant to how any adulteration layer is framed.
```

### 41. CCTNS / ICJS — the structural answer to "why does India not have police.uk"
NCRB-implemented; integrates **more than 14,000 police stations** (target ~15,000 stations plus
5,000 supervisory offices) on a Core Application Software built by Wipro, holding FIR
registration, investigation records and charge sheets. ICJS links CCTNS to e-Courts, e-Prisons,
Forensics and Prosecution. NAFIS (linked) held 1.06 crore fingerprint records as of 31 Oct 2024.
The citizen portal offers individual lookups (FIR copy, tenant/servant verification), not
statistics.

```
id: specialised-crime-cctns-icjs | tier: 2 | geo_granularity: police-station
unit_of_record: fir-record | cadence: realtime | access: login | verification: CITED
url landing: https://ncrb.gov.in | priority: 3 | ingest_difficulty: 5
*** The FIR records in CCTNS ARE police-station-identified. The only reason India has no
street-level crime map is policy, not technology. Any serious version of this product
eventually has to argue for a CCTNS aggregate-release policy. ***
CAVEAT — legal: FIR-level data names accused persons who have not been convicted. Bulk
publication carries acute DPDP Act and defamation exposure. Aggregate-only, k-anonymised,
with a suppression threshold, or not at all.
how_to_obtain: state-level engagement is far more tractable than NCRB — several state police
forces already publish CCTNS-derived dashboards under their own branding. Start there.
```

## Granularity reality check

| Domain | Finest PUBLISHED geography | Finest HELD geography | Location semantics | Cadence | Lag |
|---|---|---|---|---|---|
| Cybercrime — NCRP complaints | state (OGD resource) | district | **victim's declared district** | near-monthly | weeks–months |
| Cybercrime — I4C TAU hotspots | district (ad hoc) | police-station | **offender's district** | irregular | n/a |
| Cybercrime — NCRB cyber head | state + 19 metro cities | police-station | **station that took the FIR** | annual | 12–18 mo |
| CERT-In incidents | national | none spatial | organisation / ASN | annual | 6–12 mo |
| Sanchar Saathi / Chakshu | state (via telecom LSA) | subscriber | **subscriber's LSA** | realtime | n/a |
| Crimes vs women — NCW | state | district | **complainant's residence** | monthly | ~1 mo |
| SHe-Box | district (Local Cttee) | employer | **workplace location** | n/a public | n/a |
| One Stop Centres | district | centre | **service-delivery point** | monthly (internal) | n/a |
| Children — TrackChild | state | **police-station × 2 (missing-from AND found-at)** | victim origin + recovery | realtime | n/a public |
| CHILDLINE 1098 | district | call | **contact-centre catchment** | monthly (internal) | n/a |
| POCSO | district | police-station | **offence location** (clean) | annual | 12–18 mo |
| **SC/ST atrocities (PoA s.21(4))** | **district** | **police-station + notified atrocity-prone areas (sub-district)** | **offence location** (clean) | annual | 18–30 mo |
| Human trafficking | state | police-station | **rescue/destination** (trap) | annual | 12–18 mo |
| Narcotics — NCB seizures | state (via 23+ zones) | seizure point | **interdiction location** (trap) | annual | 6–12 mo |
| Narcotics — NDDTC survey | state | survey PSU | **respondent residence** (prevalence) | one-off 2019 | — |
| Economic — RBI | national (by bank group) | branch | **reporting bank** (unusable) | annual | 12 mo |
| Economic — ED/SFIO/SEBI | national | zonal office / registered office | **administrative artefact** | annual | 12 mo |
| **Custodial deaths — NHRC** | state | **exact police station or jail (point)** | **facility — victim, offender and reporter coincide** | continuous | 12–24 mo |
| Communal incidents | state | district | offence location | irregular (Q&A) | varies |
| Varshney–Wilkinson riots | city | town | offence location | one-off, ends 1995 | 30 yr |
| Missing persons — ZIPNET | **police-station (record-level)** | police-station | **station of report** | realtime | n/a |
| Wildlife / food adulteration | state | seizure/sample point | **enforcement location** | annual | 12 mo |

**The blunt gap.** The product wants street-level, near-real-time, victim-located incidents.
This scope realistically delivers **district-level, annual, 12–30-month-lagged aggregates**, with
exactly two exceptions worth building for: NCRP (state now, district obtainable, near-monthly)
and NHRC custodial deaths (facility-point, but you must open case files to get it).

## Blockers and how to get past them

1. **Session-level network blocker (this dossier's biggest limitation).** The egress proxy
   returned `EGRESS_BLOCKED` / `CONNECT tunnel failed, response 403` for every `.gov.in`,
   `.nic.in`, `dataful.in`, `indiastat.com`, `unodc.org`, `prsindia.org`, `cyberpeace.org`,
   `web.archive.org` and Indian news domain, in both WebFetch and `curl`. Only
   `en.wikipedia.org` and `github.com` resolved. The shared WebSearch budget (200/200) was
   exhausted after six queries. **Fix: re-run this agent with those domains allowlisted, or
   have a human in India confirm the 30 URLs recorded above.** Until then, treat every URL as
   a hypothesis.
2. **State-level publication of district-level holdings.** NCRP, TrackChild, NHRC and the SC/ST
   Protection Cells all hold district/station identifiers and publish state totals.
   *Fix:* Parliament questions are the cheapest lever — an MP's starred question reliably
   produces a state/UT annexure and sometimes a district list. Next cheapest: RTI to the
   specific division (named per entry above). Third: state-level RTIs in parallel, which often
   succeed where the central body refuses.
3. **Login/LEA-only dashboards.** NCRP's "National/State/District-Level monitoring dashboards"
   are for police users. *Fix:* do not attempt access. Request the aggregate extract via RTI, or
   partner with a state police department that can publish its own slice (several state police
   already publish dashboards under their own branding).
4. **Scanned/table-in-PDF publication.** The PoA annual report, NCB annual report and NCB
   seizure tables are PDFs with `machine_readable: 1`. *Fix:* budget for `camelot`/`tabula`
   extraction plus manual QA; expect column drift between years and a definition footnote that
   changes silently.
5. **No standing series for communal incidents.** *Fix:* systematically harvest MHA Parliament
   answers; PRS Legislative Research has already compiled 2005–2017 and is the fastest start.
6. **Series breaks that will silently corrupt trends:** CHILDLINE's 2021 move to MHA;
   the IPC→BNS transition (BNS/BNSS/BSA in force 1 July 2024) which re-codes every crime head
   in every entry above that uses `IPC+SLL`; NCW's portal migration; district reorganisation
   (Telangana, Assam, Ladakh, Arunachal, Gujarat, UP have all split districts in the last
   decade). *Fix:* carry a `taxonomy_version` and a `district_vintage` on every ingested row,
   and never join a pre-2024 crime head to a post-2024 one without an explicit crosswalk.

## Seed Leads (unconfirmed but probably real)

| # | Lead | Likely publisher | Concrete next step |
|---|---|---|---|
| 1 | **Notified "atrocity-prone areas" under PoA s.17(1) / Rule 3(1)** — village/block lists | State Social Welfare Depts + state SC/ST Protection Cells | RTI per state, wording in entry 19. Also search each state gazette for "atrocity prone area" notifications. **Highest-value lead in this dossier.** |
| 2 | **TrackChild origin–destination pairs** (missing-from station × recovered-at station) | MWCD / NIC | RTI to MWCD Child Protection Division for anonymised year-wise counts by missing-district × recovery-district. This is the trafficking-corridor dataset. |
| 3 | **I4C "cybercrime hotspot districts" list** with the underlying mule-account district counts | I4C Threat Analytics Unit, MHA | Parliament question, or RTI to I4C. Must be labelled offender-geography wherever used. |
| 4 | **AHTU-wise annual returns** | MHA Anti-Trafficking Cell (CS Division) + state CIDs | RTI to MHA; parallel RTIs to state CID AHTU nodal officers. |
| 5 | **One Stop Centre MIS, centre-wise monthly case register** | MWCD Mission Shakti division | RTI; state WCD departments hold the same MIS and answer faster. |
| 6 | **NHRC custodial-death case register with facility names** | NHRC | RTI for year-wise custodial deaths by district and custodial facility type. NHRC has released facility-level detail in response to specific questions before. |
| 7 | **Varshney–Wilkinson dataset location** | ICPSR / Brown University Center for Contemporary South Asia | Search ICPSR for the exact dataset title; email the Center. |
| 8 | **ACLED India event data** as the post-1995 successor for riot/communal events | ACLED | Verify India coverage, geocoding precision and licence terms. Named without URL — unverified. |
| 9 | **Department of Justice Fast Track Special Court (POCSO) monthly progress reports** | Department of Justice, MoLJ | Check the DoJ site for the FTSC scheme dashboard; RTI if absent. |
| 10 | **CFCFRMS "amount lien-marked / saved" by state** | I4C | Parliament question — this series has been tabled before. |
| 11 | **ZIPNET record-level missing-person listings** | Delhi Police | Confirm the portal is live, read robots.txt and ToU, assess whether records carry police-station identifiers. |
| 12 | **SHe-Box district-wise complaint counts** | MWCD | RTI; the Local Committee structure guarantees a district field exists. |
| 13 | **"Magnitude of Substance Use in India" (AIIMS/NDDTC, 2019) microdata** | MoSJE / NDDTC AIIMS | Request microdata from NDDTC; the published report is state-level but the sample frame is district-based. |

## Phase 2 recommendations

1. **Ingest the PoA Act s.21(4) annual report series first.** Best geography (district, with a
   sub-district statutory layer to chase), honest offence-location semantics, statutory
   guarantee of continued publication, and a well-defined denominator (SC/ST population) that we
   can source from the Census. Two PDF URLs are already in hand. *Effort: medium (PDF tables).*
2. **Ingest the OGD NCRP state-wise cyber-fraud resource** — it is the only entry in this scope
   that is plausibly a real CSV/API behind a GODL-India licence, and cybercrime is the
   fastest-growing category. Ship it with a prominent "this is where the victim lives, not
   where the crime happened" label, or do not ship it. *Effort: low.*
3. **Build the Parliament-answer harvester.** MHA/MoSJE/MWCD answers are the actual publication
   channel for at least six domains here (cybercrime, communal, trafficking, missing children,
   custodial deaths, AHTUs). One crawler unlocks all of them. The MHA path pattern is
   predictable enough to enumerate. *Effort: medium. Payoff: highest breadth-per-unit-effort.*
4. **File the four RTIs in Seed Leads #1, #2, #4 and #6 now**, because RTI turnaround is 30+ days
   and appeals add months. These are the only routes to sub-state geography in this scope.
5. **Verify ZIPNET (#37) early.** If it is live and carries police-station identifiers on
   record-level entries, it is the single finest-grained thing in this dossier and changes what
   the product can promise for the NCR.
6. **Do not build a narcotics layer, an economic-crime layer, or a wildlife layer for v1.**
   Their geography measures enforcement deployment or corporate registration, not risk. Park
   them behind a clearly-labelled "enforcement activity" toggle if they ship at all.
7. **Adopt a mandatory `location_semantics` column across the whole master catalogue**, with the
   enum `victim-residence | offence-location | offender-residence | reporting-office |
   service-delivery-point | workplace | facility | interdiction-point | none`. Nothing in this
   scope can be safely merged without it, and four of the traps documented above
   (cybercrime, trafficking, narcotics, One Stop Centres) become invisible the moment a
   district code from one semantics class is joined to a district code from another.
