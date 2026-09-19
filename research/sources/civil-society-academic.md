# Civil Society, Academic & Survey Sources on Indian Crime and Safety
_Agent: civil-society-academic · Researched: 2026-09-19 · Entries: 9 verified / 35 total_
_(9 = 8 `VERIFIED_LIVE` + 1 `VERIFIED_LANDING`; 10 `CITED`, 16 `UNVERIFIED`)_

> **Session constraint, stated up front.** This session's egress proxy blocked almost every
> primary domain in scope — `rchiips.org`, `dhsprogram.com`, `acleddata.com`, `devdatalab.org`,
> `praja.org`, `data.unodc.org`, `dataverse.harvard.edu`, `zenodo.org`, `arxiv.org`,
> `data.opencity.in` — and the session-wide **WebSearch budget was exhausted (200/200) by other
> agents after my second query**. Only `en.wikipedia.org`, `github.com`, `api.github.com` and
> `raw.githubusercontent.com` were reachable.
>
> I therefore verified what I could **through published data artefacts rather than publisher
> websites**: third-party mirrors, replication repos, and provenance documentation on GitHub.
> This turned out to be unusually productive — it settled the single most important question in
> my scope (see below) with harder evidence than a factsheet landing page would have given.
> Every entry's `verification` field is honest about which route was used. Nothing here is a
> URL I did not see in fetched content.

## Executive summary

- **The headline finding overturns the brief's premise.** NFHS-5 **district** fact sheets carry
  **104 indicators and contain no violence indicator at all**. I verified this directly: the
  full distinct-indicator list of `NFHS-5-Districts.csv` (pratapvardhan's parse of the IIPS
  factsheets, CC-BY-4.0, DOI `10.7910/DVN/42WNZF`) runs 1–104 and ends at
  "104. Men age 15 years and above who consume alcohol". No indicator contains the string
  "violence", "empowerment", "bank", "mobile" or "decisions". Spousal violence, violence in
  pregnancy and sexual violence are indicators **125, 126, 127 of the 131-indicator STATE
  factsheet only**. Domestic violence sits in NFHS's *state module* (the long questionnaire
  administered to a subsample), so IIPS does not publish it below state/UT level.
- **District-level violence prevalence is still obtainable — but by computing it, not
  downloading it.** NFHS-4 and NFHS-5 are designed to be district-representative and the DHS
  Individual Recode microdata carries district identifiers plus the domestic-violence module
  and its own DV weight (`d005`). Producing ~700 district IPV estimates is a real, tractable
  Phase-2 job: register with DHS, pull the India IR file, tabulate by district with `d005`.
  The cost is precision — the DV subsample is roughly one eligible woman per selected
  household, so district cells are small and confidence intervals will be wide. **This is the
  single highest-value derived dataset available to this project and nobody has to OCR
  anything to get it.**
- **India has never run a recurring national crime victimisation survey.** I could not find one,
  and the absence is itself a finding worth publishing on the map. The nearest thing is the
  IDFC Institute **SATARC** multi-city victimisation survey (Mumbai, Delhi, Chennai, Bengaluru),
  a one-off. Every other "crime rate" for India is a *registration* rate.
- **ACLED does cover India with point geocodes.** Wikipedia (fetched) states India coverage
  **2016–present**, weekly releases, via Data Export Tool / Curated Data Files / API. Six
  independent GitHub repos show the record schema containing
  `admin1, admin2, admin3, location, latitude, longitude, geo_precision, fatalities, source`
  and the endpoint `https://api.acleddata.com/acled/read`. `geo_precision` 1 = coordinates are
  the named town/village. This is a genuine **point-level layer** — but it is *political
  violence and protest*, not ordinary crime, and must be labelled as such.
- **The best fine-grained non-government asset is judicial, not criminological.** Development
  Data Lab's judicial dataset covers **81.2 million district-court cases, 2010–2018**, from
  e-Courts, with state, district, court, case type, filing/decision dates, petitioner and
  defendant gender, and the acts and sections charged. That is a district-court-level,
  section-level, dated series — far finer than NCRB, and it measures *cases that entered court*,
  a third distinct quantity.
- **India Justice Report is state-level only, and it measures capacity, not crime.** Verified
  from the report's own site source code: 4 pillars (police 30, prisons 29, judiciary 28, legal
  aid 15 = 102 indicators), built from Data on Police Organisations, Prison Statistics India,
  NJDG and NALSA returns. Useful as a *confidence modifier* on the map, never as a crime layer.
- **SPIR is perception and self-report, at state/region level.** Verified editions: 2019
  (*Police Adequacy and Working Conditions*, 11,834 police surveyed across 20+ states),
  2020–21 (*Policing in Conflict-Affected Regions*, 11 states, police + public), 2023.
  Partners: Common Cause + Lokniti-CSDS (+ Tata Trusts, Lal Family Foundation).
- **Finest spatial granularity achievable in this domain:**
  `point` (ACLED, political violence only) → `district`/`district-court` (DDL judicial,
  NFHS microdata-derived prevalence) → `state` (all survey violence prevalence, SPIR, IJR).
  **Nothing in this domain reaches ward or police-station level.** The ward-level civic data
  Praja publishes is civic-complaint data, not crime; its policing reports are city/police-
  district level.
- **The biggest blocker is not access, it is that surveys stop at the state line.** Every
  well-measured *experienced-crime* number in India is a state number. Every fine-grained
  number is a *registration* number. Bridging that gap is the core statistical problem of this
  product, and NFHS microdata is the only lever that touches both sides.
- **Three quantities, never to be blended.** See the dedicated section below. A map that plots
  NCRB FIR counts next to NFHS prevalence next to SPIR trust scores without saying which is
  which will actively mislead.

## The three-quantity rule (read before designing any layer)

| Quantity | What it is | Sources in this dossier | Typical India value |
|---|---|---|---|
| **Reported crime** | An FIR existed. A function of *both* offending and willingness/ability to report. | NCRB (other agent), DDL judicial (post-charge), Praja policing reports | The only thing with fine geography |
| **Experienced crime (prevalence)** | A person says it happened to them. Independent of the police. | NFHS (state, microdata→district), SATARC, IHDS | 3–30× reported, depending on offence |
| **Perception of safety** | A person says they feel unsafe / distrusts police. Not an incidence measure at all. | SPIR, ASICS, Lok-Oxford | Correlates weakly with either of the above |

**Recommended layer assignment:**

- **Base choropleth (what happened):** reported crime, district level, from NCRB — but rendered
  with an explicit *reporting-propensity* caveat, never as "crime rate".
- **Correction / confidence layer:** NFHS-derived district IPV prevalence next to NCRB
  crime-against-women registration for the same district. Where prevalence is high and
  registration is low, the map should say *"under-registered"*, not *"safe"*. This is the single
  most defensible analytical move available to this project.
- **Point layer:** ACLED events, in their own toggle, labelled "political violence and protest",
  never merged into the crime choropleth.
- **Institutional-capacity overlay:** IJR pillar scores, state level, shown as context for how
  seriously to take the registration numbers.
- **Never a base layer:** perception data. Offer it as a separate, clearly-labelled tab.

---

## Source entries

### 1. NFHS-5 District Fact Sheets (2019–21)

The most-cited candidate for district-level victimisation data in this project — and it does
not contain any. 104 indicators per district, covering population, fertility, maternal and
child health, nutrition, anaemia, blood pressure, blood sugar, cancer screening, HIV knowledge,
tobacco and alcohol. Indicator 19 is menstrual hygiene; indicators 101–104 are tobacco and
alcohol use; there is no gender-based-violence section. The official pages
(`rchiips.org/nfhs/districtfactsheet_NFHS-5.shtml`, and the data.gov.in resource
"NFHS-5 India Districts Factsheet Data (Provisional)", an `.xls`) were egress-blocked from this
session; both URLs were recovered from fetched third-party provenance files. Full round covers
~707 districts; the widely-mirrored Phase-1 release covers 341 districts across 21 states/UTs.

```
id: civil-society-academic-nfhs5-district-factsheets
publisher: IIPS / Ministry of Health & Family Welfare
tier: 1 | geo_granularity: district | unit_of_record: aggregate-count
time: 2019-21 | cadence: irregular (~5-yearly) | lag: 1-3 years
formats: [PDF, XLS, CSV] | access: open-download | machine_readable: 3
verification: CITED — official URL blocked; indicator list verified via two independent mirrors
```
**Caveat that matters most:** *no violence indicators at district level.* Do not plan a map
layer on this. Use it for denominators and socio-economic context instead.

### 2. NFHS-5 State/UT Fact Sheets — Gender Based Violence block

**VERIFIED_LIVE.** Fetched `nfhs_violence_reference.csv`
(`Divya-Asnani/Haven-Cart-Innovate4Impact-Hackathon`) and read actual values. Columns:
`Indicators, sub indicators, NFHS-5 (2019-20), STATE/UT`. Section "Gender Based Violence
(age 18-49 years)" carries exactly three sub-indicators per state/UT:

1. Ever-married women age 18-49 years who have ever experienced spousal violence (%)
2. Ever-married women age 18-49 years who have experienced physical violence during any pregnancy (%)
3. Young women age 18-29 years who experienced sexual violence by age 18 (%)

Observed values include Bihar 40.6 / 1.9 / 7.1, Andhra Pradesh 28.8 / 3.5 / 3.8,
Assam 26.6 / 2.2 / 7.4, Gujarat 10.0 / 2.2 / –, Goa 6.0 / 0.9 / 1.6, A&N Islands 23.2 / (0.0) / 1.4.
Parenthesised values denote unweighted-case warnings, as in the source factsheets.
In the 131-indicator state factsheet these are indicators **125, 126, 127** (verified
independently from `kri6228/AnemiaFusionNet`, which prints the numbered indicator list).
National figure, confirmed from a fetched PIB ministerial reply: **29.3% in NFHS-5, down from
31.2% in NFHS-4.**

```
id: civil-society-academic-nfhs5-state-gbv | tier: 1 | geo_granularity: state
unit_of_record: aggregate-count | time: 2019-21 | cadence: irregular | taxonomy: n/a
formats: [PDF, CSV] | access: open-download | machine_readable: 3 | verification: VERIFIED_LIVE
priority: 4 | ingest_difficulty: 1
```
**This is the best-measured experienced-violence number in India.** It is also only 36 rows.

### 3. NFHS / DHS microdata — the district-IPV route  ← **highest-value lead in this dossier**

NFHS is India's DHS. The Individual Recode (IR) file carries the full domestic-violence module
(the `d1xx` variable block), its own DV sampling weight `d005`, and **district identifiers** —
NFHS-4 and NFHS-5 were both designed to be district-representative. That means the district
spousal- and sexual-violence estimates that IIPS declines to publish **can be computed**.
Access is free but gated: register on `dhsprogram.com`, state a research purpose, get per-survey
file approval. `dhsprogram.com` was egress-blocked from this session, so this entry is CITED.

**Concrete Phase-2 recipe:** request the India IR file for NFHS-5 (and NFHS-4 for a trend) →
tabulate `d105*`/`d106`/`d107` style violence variables by district code, weighting by `d005/1e6`
→ publish estimate **plus n and CI per district** → suppress or grey out districts below a cell
size you pick in advance. Expect wide intervals: the DV module goes to roughly one eligible
woman per selected household within the state-module subsample.

```
id: civil-society-academic-nfhs-dhs-microdata | tier: 1 | geo_granularity: district
unit_of_record: survey-respondent | time_start: 1992-93 | time_latest: 2019-21
access: login | machine_readable: 4 | formats: [Stata, SPSS, SAS, CSV]
license: DHS ToU (registration, no redistribution of microdata) | ingest_difficulty: 3 | priority: 5
verification: CITED
```
**Licence caution for the lawyer:** DHS terms permit publishing *derived aggregates*; they do
not permit redistributing the microdata. Publish the district table, not the file.

### 4. NFHS-4 (2015–16) fact sheets

State factsheet indicator **103** is "Ever-married women who have ever experienced spousal
violence (%)" and **104** is violence during pregnancy — **VERIFIED_LIVE** by fetching
`HindustanTimesLabs/women-empowerment-index/data/103.csv`, which carries urban/rural/total
and a rank for all 36 states/UTs (Sikkim 2.6 lowest, rising through Karnataka 20.5,
Maharashtra 21.4). Whether the NFHS-4 *district* factsheet also carried these two indicators I
could **not** resolve: one mirror's schema dump suggests an NFHS-4 district table with a
"Women's Empowerment and Gender Based Violence (age 15-49 years)" block at column indices
104–106, but that same repo's own integration script states it only ever uses NFHS-4 at
**state** level and warns "True district-to-district trend comparison is therefore not
possible." **Treat as unresolved; resolve it in Phase 2 by opening one NFHS-4 district PDF
(URL pattern confirmed in a fetched file: `rchiips.org/nfhs/pdf/NFHS4/<CODE>_FactSheet.pdf`).**

```
id: civil-society-academic-nfhs4-factsheets | tier: 1
geo_granularity: state (district status unresolved) | verification: VERIFIED_LIVE (state level)
priority: 3
```

### 5. NFHS-6

Wikipedia (fetched 2026-09-19) lists **NFHS-6 (2023–24)** as the latest round. I could not
confirm publication status, whether factsheets are out, or whether the GBV block moved. Given
NFHS-5's design, assume violence remains state-only unless shown otherwise.

```
id: civil-society-academic-nfhs6 | tier: 1 | verification: UNVERIFIED | priority: 3
how_to_obtain: check rchiips.org/nfhs and mohfw.gov.in; IIPS Mumbai is the fieldwork agency
```

### 6. Status of Policing in India Report (SPIR)

Common Cause + Lokniti-CSDS. Survey instrument, so: *perception and self-report*, never
incidence. Editions confirmed from fetched news-corpus text:

| Edition | Subject | Sample as reported |
|---|---|---|
| 2018 | Performance and perceptions | households + police, ~22 states |
| 2019 | Police Adequacy and Working Conditions | **11,834 police personnel, 20+ states** |
| 2020–21 | Policing in Conflict-Affected Regions | police + public in 11 states (J&K, AP, Telangana, Odisha, Chhattisgarh, Jharkhand, Bihar, Assam, Tripura, Nagaland, Manipur); partners incl. Tata Trusts, Lal Family Foundation |
| 2023 | Citizen trust, perceptions of bias, support for extra-legal violence | not confirmed |

Sample findings from the 2020–21 edition, verbatim from a fetched report of it: 21% of police
personnel and 19% of the public said that "for the greater good of the society, sometimes
killing" a dangerous Naxalite/insurgent is "more effective than giving them a legal trial";
22% of people knew a woman arrested by police or detained by army/paramilitary.
Publisher site `commoncause.in` (recorded as live HTTP 200 in a fetched link-audit file).

```
id: civil-society-academic-spir | tier: 4 | geo_granularity: state
unit_of_record: survey-respondent | cadence: irregular | formats: [PDF]
access: open-download | machine_readable: 1 | verification: CITED | priority: 3
caveats: perception not incidence; regional subsamples; non-comparable across editions
```
**Use:** a "trust in police" contextual tab. **Never** as evidence about crime levels.

### 7. India Justice Report

**VERIFIED_LIVE** — fetched the report site's own source (`frappe/ijr`, the Frappe-built
indiajusticereport.org application) including `ijr/www/_methodology.md`. Editions 2019, 2020,
2022 (2025 edition referenced elsewhere, unconfirmed here). 2022 edition: **102 indicators** —
police 30, prisons 29, judiciary 28, legal aid 15 — across six themes (Infrastructure, Human
Resources, Diversity, Budgets, Workload, Trends), plus a standalone State Human Rights
Commission pillar scored separately and excluded from the ranking.

Underlying official sources, per the methodology page: Data on Police Organisations 2022
(as at 1 Jan 2022); Prison Statistics India 2021 (as at 31 Dec 2021); NJDG / Supreme Court /
Court News / DoJ (2022–23); NALSA (2020–21 to 2022); CAG documents and state budgets (2020–21).
Ranking clusters: I — 18 large/mid states (10M+), II — 7 small states, III — 8 UTs (unranked),
IV — 3 AFSPA states (unranked). Stated limitation, verbatim: "limited by the unavailability and
paucity of data and its inconsistencies".

```
id: civil-society-academic-india-justice-report | tier: 4 | geo_granularity: state
urls: {landing: https://indiajusticereport.org/}
unit_of_record: aggregate-count | time_start: 2019 | cadence: irregular | lag: ~12 months
formats: [PDF, XLSX, dashboard-only] | access: open-download | machine_readable: 2
license: unstated (a third-party catalogue claims non-commercial-with-attribution — unverified)
verification: VERIFIED_LIVE | priority: 3 | ingest_difficulty: 2
```
**This measures justice-system capacity, not crime.** Its real use here is as a denominator of
credibility: a state that ranks badly on police human resources is a state whose registration
counts should be read with more suspicion.

### 8. The missing national crime victimisation survey — a documented absence

I searched for an Indian equivalent of the US NCVS or the England & Wales CSEW and found none.
**India has no established, recurring national crime victimisation survey.** NCRB publishes
registrations; no agency publishes national experienced-crime prevalence for crime in general.
The only national prevalence numbers are NFHS's, and they cover intimate-partner and sexual
violence only.

**This belongs on the map as published methodology**, not just in an internal note. It is the
reason every district colour on the map is a statement about *police records*, not about safety.

```
id: civil-society-academic-no-national-victimisation-survey | tier: 4 | geo_granularity: national
unit_of_record: narrative-document | access: n/a | verification: CITED (absence; searched, not found)
priority: 4 | notes: negative finding, treat as publishable methodology content
```
**Residual risk:** BPR&D has commissioned one-off victimisation studies that are not well
indexed online. Phase 2 should file an RTI with BPR&D (see Seed Leads).

### 9. IDFC Institute SATARC — Safety Trends and Reporting of Crime

The nearest thing India has to a city crime victimisation survey: a household victimisation and
reporting survey run by IDFC Institute across **Mumbai, Delhi, Chennai and Bengaluru**,
designed explicitly to measure the gap between crimes experienced and crimes registered. One-off
(mid/late 2010s). Directly on-point for this project's confidence language, because its whole
purpose was to estimate the under-registration multiplier by offence type.

```
id: civil-society-academic-idfc-satarc | tier: 4 | geo_granularity: city
unit_of_record: survey-respondent | cadence: one-off | formats: [PDF]
access: on-request | verification: UNVERIFIED | priority: 4 | ingest_difficulty: 3
how_to_obtain: IDFC Institute publications archive; if the org has wound down, contact the named
  authors directly or look for the working paper in an institutional repository
```
**Flagged as UNVERIFIED and important.** If the microdata or the offence-wise reporting rates
can be obtained, this is the best available basis for per-category under-reporting multipliers.

### 10. India Human Development Survey (IHDS)

**Partly VERIFIED_LIVE** (Wikipedia fetched). Three waves: 2004–05, 2011–12, and **2022–23**.
Wave 1 covered 41,554 households in 1,503 villages and 971 urban neighbourhoods; later waves
re-interviewed 37,000+ plus refreshers. Run by NCAER with University of Maryland
(Sonalde Desai, Reeve Vanneman); site `ihds.umd.edu`. The Wikipedia topic list — health,
education, employment, economic status, marriage, fertility, **gender relations**, social
capital — does not name crime or policing, but IHDS instruments have historically carried
confidence-in-institutions (including police) and household conflict items. Data is archived at
ICPSR. District identifiers exist but IHDS is **not** district-representative; treat sub-state
estimates as unreliable.

```
id: civil-society-academic-ihds | tier: 4 | geo_granularity: state (district IDs present, not representative)
unit_of_record: survey-respondent | time: 2004-05 / 2011-12 / 2022-23 | cadence: irregular
formats: [Stata, SPSS, CSV] | access: login (ICPSR registration) | machine_readable: 4
verification: CITED | priority: 2
```

### 11. NSSO rounds touching safety — largely a dead end

No NSS round is a crime victimisation survey. Safety-adjacent content (household amenities,
lighting, transport, women's mobility) appears incidentally across rounds but is not an
incidence measure and is not published below state × sector. Recorded so the next researcher
does not repeat the search.

```
id: civil-society-academic-nsso-safety | tier: 1 | geo_granularity: state
verification: UNVERIFIED (negative) | priority: 1
```

### 12. Lok Foundation–Oxford Surveys (administered by CMIE)

Nationally representative attitude surveys carried on CMIE's field network; rounds have covered
gender attitudes, trust in institutions and public-space safety perceptions. Perception only.
Published as summary articles rather than as an open microdata series.

```
id: civil-society-academic-lok-foundation-oxford | tier: 4 | geo_granularity: state
unit_of_record: survey-respondent | access: on-request | verification: UNVERIFIED | priority: 1
```

### 13. CMIE Consumer Pyramids Household Survey

~175k households, high-frequency (four-monthly waves), genuinely fine geography (CMIE's own
"homogeneous regions", below state). **But it carries no crime or victimisation module** —
it is income, consumption, employment and sentiment. Commercial subscription. Catalogued here
only to close the loop: it is not a crime source, and its cost cannot be justified for this
project on the basis of sentiment variables.

```
id: civil-society-academic-cmie-cphs | tier: 5 | geo_granularity: district
unit_of_record: survey-respondent | cadence: quarterly | access: paid
verification: UNVERIFIED | priority: 1
```

### 14. Praja Foundation — city policing and civic reports

Praja publishes annual city reports built substantially from **RTI returns**, covering Mumbai,
Delhi, Bengaluru and other cities, including reports on the state of policing and law and order
alongside its better-known civic-issue and councillor-performance reports. `praja.org` was
egress-blocked from this session and I could find no mirrored Praja data artefact on the
reachable surfaces, so **I could not confirm the granularity claim in the brief.**

**My assessment, stated as an assessment:** Praja's *civic* data (complaints, councillor
attendance) is ward-level because municipal wards are the unit those RTIs return. Police data
obtained by RTI is returned by **police station or police district**, because that is how police
record-keeping is organised — it does not map to municipal wards. So the likely reality is
police-station-level for the policing reports, ward-level only for non-crime civic indicators.
**Do not assume ward-level crime until a Praja policing report is actually opened.**

```
id: civil-society-academic-praja-foundation | tier: 4
geo_coverage: Mumbai, Delhi, Bengaluru (+ others) | geo_granularity: police-station (assessed; unconfirmed)
unit_of_record: aggregate-count | cadence: annual | formats: [PDF]
access: blocked (this session) / open-download (expected) | machine_readable: 1
verification: UNVERIFIED | priority: 4 | ingest_difficulty: 4
how_to_obtain: open praja.org from an unblocked network; the reports are free PDFs. If a report
  cites RTI replies, request the underlying RTI response set from Praja directly — they have
  historically shared methodology appendices.
```
**Highest-priority unverified entry in this dossier.** If the policing reports really are
station-level and annual, they are the finest-grained non-government crime data in India and
should jump to priority 5.

### 15. Janaagraha — Annual Survey of India's City-Systems (ASICS)

Scores Indian cities on urban governance quality (laws, planning, capacity, transparency,
citizen participation). City-level, irregular. **Not a crime or safety measure** — no
victimisation, no incidence. Useful only as city-level institutional context.

```
id: civil-society-academic-janaagraha-asics | tier: 4 | geo_granularity: city
unit_of_record: aggregate-count | cadence: irregular | formats: [PDF]
verification: UNVERIFIED | priority: 1
```

### 16. Open City / Bengaluru Open Data (opencity.in)

An open civic data repository hosting Indian government datasets in cleaned, downloadable form —
including NFHS state factsheets, which is how I first encountered it (a dataset resource URL of
the form `data.opencity.in/dataset/<uuid>/resource/<uuid>/download/<name>.pdf` appeared in
search results). Bengaluru-centric but hosts national datasets. **Often better-cleaned than the
government original**, which is precisely the category the brief asked me to look for. Domain
was egress-blocked here.

```
id: civil-society-academic-opencity-bengaluru | tier: 4 | geo_coverage: Bengaluru + all-India holdings
geo_granularity: city | unit_of_record: aggregate-count | formats: [CSV, PDF, XLSX]
access: open-download | machine_readable: 3 | verification: CITED | priority: 3
notes: CKAN-style dataset/resource URL structure implies a usable CKAN API for Phase 2 harvesting
```

### 17. Development Data Lab — SHRUG

**VERIFIED_LANDING** (repo metadata fetched): `devdatalab/shrug-public`, "Issue tracking for the
Socioeconomic High-resolution Rural-Urban Geographic Platform for India (SHRUG)", 35 stars, last
pushed 2026-08-17 — an actively maintained project. Download page
`https://www.devdatalab.org/shrug_download/` (URL recovered from a fetched resource list).
SHRUG is the standard open platform for India at **town/village (shrid) level**, with keys that
bridge Census, Economic Census, NSS, elections and nightlights across years.

**SHRUG is not a crime dataset.** Its value to this project is as the **spatial spine**: it
solves district and sub-district boundary reconciliation across decades of reorganisation, which
is otherwise one of the hardest problems in building an India crime map.

```
id: civil-society-academic-ddl-shrug | tier: 4 | geo_coverage: all-India
geo_granularity: village/town (shrid) | unit_of_record: aggregate-count + boundary-polygon
time_start: 1990 | cadence: irregular | formats: [CSV, SHP, Stata]
access: open-download (email registration) | machine_readable: 4 | license: open, attribution
verification: VERIFIED_LANDING | priority: 4 | ingest_difficulty: 2
```

### 18. Development Data Lab — Judicial Data (e-Courts, 81.2M cases)

**The strongest fine-grained non-government record series in this dossier.** Verified from the
Data Is Plural newsletter archive (fetched, edition 2021-02-24), quoting verbatim:

> "The Development Data Lab has gathered data on **81.2 million court cases** in India's lower
> judiciary **between 2010 and 2018**, drawn from the country's e-Courts platform. It's 'the
> largest open-access dataset on judicial proceedings in the world'… The public dataset contains
> each case's **state, district, court, case type, filing and decision dates, defendant and
> petitioner genders, legal codes**, and more. It 'has been fully anonymized to prevent the
> identification of individual judges or litigants,' but researchers can apply for more
> extensive access."

URLs recovered from fetched content: `https://www.devdatalab.org/judicial-data`,
`http://www.devdatalab.org/judicial-bias-data`,
`https://devdatalab.medium.com/big-data-for-justice-f53e0e14c9c9`,
source platform `https://districts.ecourts.gov.in/`.

```
id: civil-society-academic-ddl-judicial-data | tier: 4 | geo_coverage: all-India lower judiciary
geo_granularity: district (court-level within district) | unit_of_record: case-record
time_start: 2010 | time_latest: 2018 | cadence: one-off | taxonomy: IPC + acts/sections
formats: [CSV, Stata] | access: open-download (extended access on-request) | machine_readable: 4
license: open for research, attribution | verification: CITED | priority: 5 | ingest_difficulty: 3
caveats: measures cases reaching court, not incidents; ends 2018 so entirely pre-BNS; e-Courts
  coverage and data quality vary sharply by state; section coding is inconsistent and needs
  normalisation; anonymised — no addresses, no sub-district geography
```
**Recommended as a first ingest** alongside NCRB. It gives a district × IPC-section × year
series that is independent of NCRB's principal-offence rule — which makes it a genuine
cross-check on NCRB's category mix, not just more of the same.

### 19. Justice Hub (CivicDataLab) — judicial datasets

**VERIFIED_LIVE** — fetched `apoorv74/ecourts-india-resources/datasets.md` and read the full
catalogue. Hosted at `justicehub.in`:

| Dataset | Content |
|---|---|
| Unpacking Judicial Data: POCSO Act in Assam, Delhi & Haryana | case details for **19,783 cases** in district courts of those three states, from eCourts |
| Analysis of Child and Adolescent Labour (Prohibition & Regulation) Act 1986 | **10,800 cases**, Jan 2015–Mar 2023, six states (Assam, Bihar, Jharkhand, Maharashtra, Tamil Nadu, UP) |
| Contract Enforcement Litigation (with NIPFP) | five acts, court complexes in ~2 cities per state across 29 states |

The POCSO archive is directly relevant: child sexual offence cases, district-court level, with
case-level detail — a category where registration data is especially weak.

```
id: civil-society-academic-justicehub | tier: 4 | geo_granularity: district
unit_of_record: case-record | time_start: 2015 | time_latest: 2023 | taxonomy: custom (act-specific)
formats: [CSV] | access: open-download | machine_readable: 4 | verification: VERIFIED_LIVE
priority: 3 | ingest_difficulty: 2 | notes: catalogue verified; individual dataset pages not opened
```

### 20. DAKSH — judicial database

Cleans and standardises e-Courts case and hearing data, explicitly addressing the
inconsistencies that make raw e-Courts data hard to use. High Courts database at
`https://database.dakshindia.org/`; methodology at
`https://www.dakshindia.org/deciphering-judicial-data-daksha-database/`. Both URLs recovered
from fetched content.

```
id: civil-society-academic-daksh | tier: 4 | geo_granularity: district (+ High Court)
unit_of_record: case-record | cadence: irregular | formats: [dashboard-only, CSV]
access: scrape | machine_readable: 3 | verification: CITED | priority: 2
```
**Use as a cleaning reference** for the DDL judicial data rather than as a separate ingest.

### 21. pratapvardhan/NFHS-5 — the mirror that settled the question

**VERIFIED_LIVE**, and the evidentiary backbone of this dossier's headline finding.
Machine-readable CSV parse of the IIPS NFHS-5 PDF factsheets, published under **CC BY 4.0** with
a Harvard Dataverse DOI, **`10.7910/DVN/42WNZF`**. Default branch `master`.

- `NFHS-5-States.csv` — 131 indicators × 36 states/UTs
- `NFHS-5-Districts.csv` — **104 indicators × 341 districts across 21 states/UTs (Phase 1)**;
  long format, columns `State, State-Code, District, Indicator, NFHS-5, NFHS-4, NFHS-5-note, NFHS-4-note`
  — i.e. it ships the NFHS-4 value beside each NFHS-5 value, a built-in five-year trend.
- `district-level/NFHS-5-<CC>-<State>.csv` — per-state splits. I fetched the Kerala file
  (1,040 rows, 14 districts): **zero rows mention violence.**

A separate fetched repo (`vybhav72954/trilytics_team_vector`) documents the same structure at
full coverage: "698 districts x 104 numbered indicators, +NFHS-4 trend". 341 × 104 = 35,464,
which exactly matches the row count another repo reports for the Phase-1 district file — the
arithmetic is internally consistent across three independent sources.

Author's own warning, verbatim: *"Quality checks have been minimally done. Please recheck with
source before doing any analysis."*

```
id: civil-society-academic-pratapvardhan-nfhs5 | tier: 4 | geo_granularity: district
urls: {data: https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv,
       landing: https://github.com/pratapvardhan/NFHS-5, docs: https://doi.org/10.7910/DVN/42WNZF}
unit_of_record: aggregate-count | time: 2019-21 | cadence: one-off | formats: [CSV]
access: open-download | machine_readable: 5 | license: CC-BY-4.0
verification: VERIFIED_LIVE | priority: 3 | ingest_difficulty: 1
caveats: Phase-1 only (341 of ~707 districts); author disclaims QC; no violence indicators
```

### 22. NFHS district parse with Census 2011 codes

A fetched provenance file cites
`https://raw.githubusercontent.com/SaiSiddhardhaKalla/NFHS/main/India.csv` as a third-party
parse of the IIPS district factsheets **with `ST_CEN_CD` and `DT_CEN_CD` Census 2011 codes
attached**. The Census district code is the join key to essentially every India district
shapefile, so a parse that ships it saves a painful fuzzy-name-matching step. The same file
claims "35,465 rows, 640 districts × ~104 indicators", which is arithmetically impossible
(640 × 104 = 66,560) and matches the 341-district Phase-1 count instead — **the description is
unreliable; the file may not be.** I did not fetch it.

```
id: civil-society-academic-nfhs-census-coded-parse | tier: 4 | geo_granularity: district
formats: [CSV] | access: open-download | machine_readable: 5 | license: unknown
verification: CITED | priority: 2 | notes: verify row count and coverage before use; the value is
  the Census 2011 code crosswalk, not the indicators
```

### 23. Hindustan Times Labs — Women's Empowerment Index (NFHS-4)

**VERIFIED_LIVE** — fetched both the README and `data/103.csv`. A media data team's index built
from the eight NFHS-4 "Women's Empowerment and Gender-Based Violence" indicators, state level,
36 states/UTs, with urban/rural/total splits and ranks, methodology following an NIPFP
governance-rating paper. Comparable NFHS-3 (2005–06) data for four indicators across 28
states/UTs. No licence stated in the README.

Its real value here is as **a worked, citable example of exactly the normalisation choice this
project will have to make** — including the decision to invert negative indicators so higher
always means better, which is the same trap a crime map falls into when it colours "more
reported crime" as "worse".

```
id: civil-society-academic-htlabs-wei | tier: 5 | geo_granularity: state
unit_of_record: aggregate-count | time: 2015-16 | cadence: one-off | formats: [CSV]
access: open-download | machine_readable: 5 | license: unstated
verification: VERIFIED_LIVE | priority: 2
```

### 24. Academic replication data — district NCRB crime panels

A body of published economics papers digitised NCRB **district**-level tables and released
replication files, which would save substantial OCR effort. The canonical example is the
literature on women in local government and crime reporting against women (Iyer, Mani, Mishra &
Topalova, *AEJ: Applied*, 2012), which built a district-level panel of NCRB crimes against women
and — importantly for us — argued that increases in recorded crime there reflected **increased
reporting**, not increased offending. Related strands: crime and rainfall/temperature shocks,
dowry deaths, and elections and violence.

I could not fetch any repository (Harvard Dataverse, ICPSR, Zenodo, AEA data archive and arXiv
were all egress-blocked) so **no replication URL is asserted here.**

```
id: civil-society-academic-replication-district-panels | tier: 4 | geo_granularity: district
unit_of_record: aggregate-count | time_start: ~1970s | time_latest: varies (mostly pre-2015)
taxonomy: NCRB-heads | formats: [Stata, CSV] | access: open-download | machine_readable: 4
verification: UNVERIFIED | priority: 4 | ingest_difficulty: 2
how_to_obtain: search the AEA Data and Code Repository, Harvard Dataverse and ICPSR for the paper
  titles; most AEJ papers since ~2010 have mandatory public replication packages
caveats: district boundaries as of the paper's vintage, not current; author-specific cleaning
  choices; often a single crime head only
```
**Strong recommendation:** chase these before commissioning any OCR of NCRB district tables.
The digitisation has probably already been done and paid for by someone else.

### 25. ACLED — Armed Conflict Location & Event Data (India)

**India is covered from 2016 to present**, weekly releases (Wikipedia, fetched 2026-09-19:
South and Southeast Asia "from 2010 to the present, with the exception of India (2016–present)";
"collects data in real time and releases updates on a weekly basis"; available via "the
website's Data Export Tool, the website's Curated Data Files, or directly from the ACLED API").

Record schema, corroborated across six independent fetched repositories:
`event_id_cnty, event_date, year, time_precision, disorder_type, event_type, sub_event_type,
actor1, assoc_actor_1, inter1, actor2, assoc_actor_2, inter2, interaction, civilian_targeting,
region, country, admin1, admin2, admin3, location, latitude, longitude, geo_precision, source,
source_scale, notes, fatalities, timestamp, iso3`.
API endpoint `https://api.acleddata.com/acled/read`, key/Bearer-token authenticated, supports
`country=India`, `event_date` range filters and a `fields=` projection. `acleddata.com` itself
was egress-blocked, so this is CITED rather than VERIFIED.

```
id: civil-society-academic-acled-india | tier: 4 | geo_coverage: India (all states)
geo_granularity: point | unit_of_record: incident-point | time_start: 2016 | time_latest: current
cadence: weekly | lag: ~1 week | taxonomy: custom (ACLED event/sub-event types)
formats: [CSV, JSON] | access: api-key | machine_readable: 5
license: ToU-restricts-reuse (free for non-commercial/academic with registration and attribution;
  commercial and redistribution terms are separate — get sign-off before publishing derived points)
verification: CITED | priority: 4 | ingest_difficulty: 2
caveats: POLITICAL violence and protest only, NOT ordinary crime — riots, mob violence, communal
  incidents, attacks on civilians, protests; media-sourced, so coverage tracks press attention and
  is denser in English-media-covered areas; geo_precision 1/2/3 must be respected (2 and 3 are
  approximate, sometimes only an admin centroid) — never plot precision-3 events as exact points
```
**The only true point-level layer available in this domain.** Ship it as its own toggle with an
explicit "political violence and protest" label and a `geo_precision` filter, or it will be
misread as a crime feed.

### 26. UNODC crime and criminal justice statistics

UNODC compiles member-state submissions (intentional homicide, and via its UN-CTS survey a wider
set of offences and criminal-justice indicators) at `data.unodc.org` / `dataunodc.un.org`.
India's submissions derive from NCRB, so **UNODC is not an independent measurement of India** —
it is NCRB, reformatted onto an international taxonomy. Its value is cross-national benchmarking
and a stable long series, not correction. Domain egress-blocked here.

```
id: civil-society-academic-unodc | tier: 3 | geo_granularity: national
unit_of_record: aggregate-count | cadence: annual | lag: 1-2 years | taxonomy: ICCS
formats: [XLSX, CSV] | access: open-download | machine_readable: 4 | verification: CITED | priority: 2
caveats: derived from NCRB, so inherits its undercount and principal-offence rule; ICCS mapping
  from NCRB heads is lossy
```

### 27. WHO Global Health Estimates — homicide mortality

WHO's mortality estimates for interpersonal violence deaths are built from vital registration and
verbal-autopsy modelling, **not from police records** — which makes them a genuinely independent
cross-check on NCRB murder counts. National level for India (subnational only through modelling).
Historically WHO/GBD homicide estimates for India have diverged materially from NCRB's, and that
divergence is exactly the kind of thing that belongs in the map's methodology page.

```
id: civil-society-academic-who-ghe-homicide | tier: 3 | geo_granularity: national
unit_of_record: aggregate-count | cadence: irregular | formats: [XLSX, CSV] | access: open-download
machine_readable: 4 | verification: UNVERIFIED | priority: 3
notes: independent of police records — the single most useful national-level sanity check available
```

### 28. Global Burden of Disease — interpersonal violence, India state level

IHME's GBD, and specifically the **India State-Level Disease Burden Initiative** (ICMR / PHFI /
IHME), produces **state-level** cause-of-death estimates for India including interpersonal
violence and self-harm. Downloadable from the GHDx results tool. State level, modelled,
annual back-series. Like WHO GHE it is mortality-based and police-independent.

```
id: civil-society-academic-gbd-interpersonal-violence | tier: 4 | geo_granularity: state
unit_of_record: aggregate-count | time_start: 1990 | cadence: irregular | formats: [CSV]
access: open-download | machine_readable: 4 | license: IHME free-use with attribution
verification: UNVERIFIED | priority: 3
caveats: MODELLED estimates with uncertainty intervals, not counts — always carry the UI; a
  modelled state estimate must never be rendered with the same visual weight as an observed count
```

### 29. World Bank — intentional homicide rate (WDI)

`SH.STA.HOMI.P5` in the World Development Indicators, sourced from UNODC and therefore, for
India, from NCRB. National, annual, trivially accessible via the WDI API. Catalogued for
completeness and benchmarking; adds no independent information about India.

```
id: civil-society-academic-worldbank-wdi-homicide | tier: 3 | geo_granularity: national
cadence: annual | formats: [CSV, JSON] | access: open-download | machine_readable: 5
license: CC-BY-4.0 | verification: UNVERIFIED | priority: 1
```

### 30. Institute for Economics & Peace — Global Peace Index

Composite national index blending conflict, militarisation and "societal safety and security"
indicators; India scored nationally. Composite of composites, several inputs themselves derived
from NCRB. **Not usable as a crime measure**; catalogued to explain why it should not be used.

```
id: civil-society-academic-iep-gpi | tier: 4 | geo_granularity: national | cadence: annual
formats: [PDF, XLSX] | access: open-download | verification: UNVERIFIED | priority: 1
```

### 31. IndiaSpend

Data journalism outlet that has built and maintained original incident databases from media
reports — most notably a hate-crime / cow-related-violence tracker. Incident-level with dates and
locations, which is rare and valuable, but **media-derived**: it counts *reported-in-press*
events, a fourth and even narrower quantity than police-reported crime, with severe and
non-random selection. The Wikipedia article 404'd; the site was not reachable from this session.

```
id: civil-society-academic-indiaspend | tier: 5 | geo_granularity: district
unit_of_record: incident-point | cadence: irregular | formats: [HTML, CSV] | access: scrape
machine_readable: 2 | license: unknown | verification: UNVERIFIED | priority: 2
caveats: media-report-derived; English-press bias; trackers have in the past been paused or taken
  down — archive anything you rely on; verify current status and licence before republishing
```

### 32. Factly / Dataful

Factly runs a large Indian open-data repository (Dataful, formerly Factly DataSets) that
republishes government datasets — including NCRB series — in cleaned, machine-readable,
API-accessible form. If it carries NCRB's district tables as CSV, it removes a large chunk of
this project's hardest ingestion work. **Unverified; both domains unreachable here.** This is my
best single "cheap win" lead.

```
id: civil-society-academic-factly-dataful | tier: 5 | geo_granularity: district (claimed)
unit_of_record: aggregate-count | formats: [CSV, JSON, API] | access: api-key (freemium, some paid)
machine_readable: 5 | license: unknown (likely ToU-restricted for redistribution)
verification: UNVERIFIED | priority: 4 | ingest_difficulty: 1
how_to_obtain: open dataful.in, search NCRB / Crime in India, check whether district tables are
  present and at what tier; confirm redistribution rights before building a public map on it
```

### 33. Article-14, Scroll.in, The Hindu data team

Investigative and data-journalism outlets that have published original analyses of Indian
criminal justice — Article-14 in particular on undertrials, sedition/UAPA prosecutions and
police accountability, often with case-level databases assembled by hand. Typically published as
narrative with an accompanying table rather than as a maintained dataset.

```
id: civil-society-academic-data-journalism-outlets | tier: 5 | geo_granularity: district
unit_of_record: case-record | cadence: irregular | formats: [HTML, PDF] | access: scrape
machine_readable: 1 | license: ToU-restricts-reuse | verification: UNVERIFIED | priority: 2
notes: treat as leads to underlying official records, not as sources in their own right
```

### 34. Police Data Accessibility Project / Vera Police Data Transparency Index

**VERIFIED_LIVE** (Data Is Plural archive, edition 2024-01-24, fetched). US-only, so out of
geographic scope — catalogued as **methodological precedent**: PDAP maintains a meta-dataset of
1,700+ police record sources recording, per source, "where to find them online, what time period
they cover, how often they're updated"; Vera's index scores 90+ agencies across 10 categories of
data transparency. That is close to exactly the schema this project's Phase 1 is building, and
Vera's transparency scoring is a ready-made model for the per-state credibility rating this map
will need.

```
id: civil-society-academic-pdap-vera-precedent | tier: 4 | geo_coverage: USA (precedent only)
geo_granularity: n/a | unit_of_record: narrative-document | formats: [CSV, HTML]
access: open-download | verification: VERIFIED_LIVE | priority: 2
```

### 35. Community dataset catalogues (use with care)

`connu/awesome-datasets` carries a `topics/crime-and-policing/in/` section listing NCRB Crime in
India, NCRB Prison Statistics, India Justice Report and the data.gov.in public-safety sector
page, with per-entry licence and format metadata. **VERIFIED_LIVE** that the file exists and says
this. But its quantitative metadata is not credible — it asserts figures like "~2 GB per edition"
and "~500 MB" for a PDF report, and reads as machine-generated. Similarly `apoorv74/ecourts-india-resources`
(reliable, hand-curated) versus various LLM-written "research" repos I encountered (not reliable).

```
id: civil-society-academic-community-catalogues | tier: 5 | unit_of_record: narrative-document
access: open-download | verification: VERIFIED_LIVE (existence) | priority: 1
notes: harvest the URLs, discard the metadata; re-derive every field yourself
```

---

## Granularity reality check

| Level | What actually exists here | Period | Refresh | Honest verdict |
|---|---|---|---|---|
| `point` | ACLED events (lat/long + `geo_precision`) | 2016– | weekly | Real, but political violence only, and precision 2–3 are not true points |
| `police-station` | Praja RTI-based policing reports (assessed, unconfirmed) | ~2010s– | annual | The one plausible route to sub-city crime data in this domain — unverified |
| `district` | DDL judicial (81.2M cases); NFHS microdata-derived prevalence; academic replication panels | 2010–18 / 2015–21 | one-off | The workhorse level. Judicial is observed; prevalence must be computed and comes with wide CIs |
| `city` | SATARC victimisation (4 cities); ASICS governance | mid-2010s | one-off | Thin, dated, but the only city victimisation data India has |
| `state` | NFHS GBV factsheets; SPIR; IJR; GBD interpersonal violence | 1992–2021 | 3–5 yearly | Well measured, uselessly coarse for "is this street safe" |
| `national` | UNODC, WHO GHE, World Bank, GPI | 1990– | annual | Benchmark only |
| **`ward`/`beat`** | **nothing** | — | — | **The brief's target granularity does not exist in this domain.** Praja is the only candidate and its crime data is almost certainly police-station, not ward |

**The gap, stated plainly:** the product wants ward-level current crime. This domain offers
district-level five-year-old prevalence and state-level survey estimates. The honest v1 map
colours districts, not streets, and says so.

## Blockers and how to get past them

1. **Egress blocking (this session).** ~20 in-scope domains returned `EGRESS_BLOCKED` (403/407
   class). Per the proxy README this is organisation policy and must be reported, not routed
   around. **Fix:** re-run this dossier's UNVERIFIED entries from an unblocked network. The
   entries most worth re-running, in order: Praja (14), Dataful (32), SATARC (9), DHS (3).
2. **WebSearch budget exhausted session-wide (200/200) after two queries.** This removed
   discovery entirely. **Fix:** raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, or give
   discovery agents a dedicated budget slice.
3. **NFHS publishes violence at state level only.** Not an access problem — a design decision
   (state module subsample). **Fix:** DHS microdata, entry 3. This is a computation, not a
   request.
4. **DHS microdata is login-gated** with per-survey approval and a no-redistribution term.
   **Fix:** register early (approval takes days, not minutes); plan to publish only aggregates.
5. **Praja's data is locked inside PDF reports** built from RTI replies. **Fix:** ask Praja for
   the underlying RTI response sets and methodology appendix; failing that, file the same RTIs
   with Mumbai/Delhi police directly — Praja's reports document which questions were asked.
6. **Academic replication files are scattered** across Dataverse, ICPSR and journal archives with
   no India-crime index. **Fix:** search by paper title in the AEA Data and Code Repository first
   (mandatory deposits since ~2010), then Dataverse.
7. **Everything ends before BNS.** DDL judicial stops at 2018; NFHS-5 fieldwork ended 2021; the
   IPC→BNS/BNSS/BSA transition took effect 1 July 2024. **No source in this domain spans the
   transition.** Any series crossing mid-2024 needs an explicit definitional break marker.
8. **GitHub as a verification surface has a rate limit.** Unauthenticated `api.github.com` calls
   hit 403 quickly; the authenticated MCP GitHub tools did not. Prefer those, and note that
   `get_file_contents` is restricted to session-configured repos — `raw.githubusercontent.com`
   via WebFetch is the working route for third-party repo files.

## Seed Leads (unconfirmed but probably real)

1. **Praja Foundation, "Report on the State of Policing and Law & Order" (Mumbai; Delhi).**
   Annual, RTI-built. *Next step:* `praja.org` → Reports/Downloads; if the PDF cites RTI replies,
   email Praja for the response set.
2. **BPR&D commissioned victimisation studies.** The Bureau of Police Research & Development has
   funded one-off victimisation and police-perception research that is poorly indexed.
   *Next step:* RTI to BPR&D, New Delhi, asking for a list of all victimisation-survey studies
   commissioned since 2000 with their report titles and whether reports are public.
3. **IDFC Institute SATARC microdata or offence-wise reporting rates** (entry 9). *Next step:*
   IDFC Institute publications archive; failing that, contact the authors — this is the only
   Indian source likely to yield per-category under-reporting multipliers.
4. **NFHS-6 GBV design.** Whether the DV module stays in the state module. *Next step:* IIPS
   Mumbai, or the NFHS-6 interviewer's manual once published — the manual states which
   questionnaire version carries the DV module, which settles the geography question.
5. **India Justice Report 2025 (4th edition).** Referenced outside the site source I read.
   *Next step:* `indiajusticereport.org` → Reports.
6. **SPIR editions after 2023.** *Next step:* `commoncause.in` → Publications.
7. **An NCRB district-table digitisation that already exists.** Given how many published papers
   use district NCRB panels, a consolidated multi-decade district file almost certainly exists in
   someone's replication package. *Next step:* AEA Data and Code Repository, search "crime India
   district".
8. **Dataful's NCRB holdings** (entry 32) — potentially the cheapest large win in the whole
   project if district tables are already CSV there.
9. **`opencity.in` CKAN API.** The dataset/resource URL structure implies CKAN. *Next step:* try
   `data.opencity.in/api/3/action/package_search?q=crime` — if it responds, the whole catalogue
   is harvestable in one pass.

## Phase 2 recommendations (ranked)

1. **Compute district-level IPV prevalence from NFHS-5 (and NFHS-4) DHS microdata.** Entry 3.
   Highest value, fully tractable, no OCR, and it is the only thing in this domain that produces
   a *district-level victimisation* number. Ship it with n and CI per district and suppress small
   cells. This becomes the map's under-registration correction layer.
2. **Ingest the DDL judicial dataset (81.2M cases, 2010–18).** Entry 18. District × section ×
   date, observed not modelled, and independent of NCRB's principal-offence rule — so it
   cross-checks NCRB rather than echoing it.
3. **Resolve Praja.** Entry 14. If the policing reports are police-station-level and annual, they
   are the finest non-government crime data in India and this ranking changes.
4. **Chase academic replication packages before commissioning any OCR.** Entry 24. Potentially
   saves the single largest cost item in the project.
5. **Add ACLED as a separate, clearly-labelled point layer.** Entry 25. Cheap, current, weekly,
   genuinely geocoded — but only if it is visually and textually separated from crime, and
   filtered on `geo_precision`.
6. **Pull SHRUG for the spatial spine.** Entry 17. Not crime data; solves boundary reconciliation,
   which every other ingest depends on.
7. **Take NFHS-5 state GBV (entry 2) and IJR (entry 7) as context layers now** — both are tiny,
   clean, and immediately usable while the harder work proceeds.
8. **Write the methodology page early**, built on the three-quantity table above and on entry 8
   (the absence of a national victimisation survey). On this subject the caveats are not a
   disclaimer appended at the end; they are the product.
