# Phase 1 Findings — What Can Actually Be Built

_Consolidated from 17 research dossiers and 469 catalogued sources · 2026-09-19_

> **Read the verification caveat first.** This research ran in a sandbox whose egress policy
> returned 403 for `*.gov.in`, `*.nic.in`, `data.police.uk`, OSM mirrors, `arxiv.org` and
> `web.archive.org`. Agents could search but could not open Indian government pages. Of 469
> catalogued sources, **35 are `VERIFIED_LIVE` and 17 `VERIFIED_LANDING`; 302 are `CITED`
> (URL and title seen in a search index) and 101 `UNVERIFIED`.** The verified minority is
> disproportionately what agents could reach on GitHub — which, as it turned out, is where
> the single most important finding lives. Run `research/verify_sources.py` from an unblocked
> network before acting on any URL here.

---

> **Corrections from the first live-network session, 2026-09-20.** The
> verification caveat above has now been partly discharged, and four things in
> this document are wrong or incomplete as a result. See
> `docs/LIVE-FETCH-2026-09-20.md` for the evidence.
>
> 1. **NCRB and data.gov.in forbid automated access.** Both publish
>    `User-agent: * / Disallow: /`. The "~2,521 NCRB resources on data.gov.in"
>    in §2 are real, and off-limits to a scraper under INGESTION rule 2. This
>    is the binding constraint on the district ceiling, not availability.
> 2. **Delhi is not "e-FIR only".** `cctns.delhipolice.gov.in` searches all
>    FIRs from 01-07-2015. But it refuses a search carrying neither an FIR
>    number nor a person's name, so it is a lookup, not a listing, and yields
>    no station-month series. The practical conclusion is unchanged; the reason
>    is different, and the difference matters if anyone re-tries it.
> 3. **Maharashtra's published series starts 2017-01-01**, and no query may
>    span more than 90 days. The portal states both only in a validation
>    message. There is no route to 2015-2016 by this feed.
> 4. **Mumbai is one commissionerate, BRIHAN MUMBAI CITY**, not the two revenue
>    districts this project assumed. The MHA station master uses the same
>    string, which is what makes the FIR-to-station join possible at all.

## 1. The headline

**A police.uk-equivalent crime map is buildable in India today, for about five states covering
roughly 370 million people, without filing a single RTI.** That is a much better answer than
this project started with, and it rests on two findings that contradict what most of the
research fleet independently concluded.

Four separate agents reported that no police station jurisdiction boundaries exist publicly
anywhere in India. That is wrong, and the correction is the most valuable output of Phase 1:

- **Police station (thana) jurisdiction polygons exist for 7 states** — Andhra Pradesh, Bihar,
  Delhi, Karnataka, Rajasthan, Tamil Nadu and Telangana — harvested from the states' own GIS
  portals (APSAC, Bhugoal Bihar, GSDL Delhi, KGIS Karnataka, Rajdharaa, TNGIS, TRACGIS) and
  mirrored as ~36 files / ~96 MB. `VERIFIED_LANDING`: the release manifest was read, the
  archives were not decompressed.
- **An all-India police station point file exists and was fully verified.** 16,459 point
  features carrying `state_cd`, `district_c`, `ps_cd`, name and coordinates, every field
  non-null, spanning 36 states and 983 districts. This is the station master that another
  agent proposed we obtain by RTI. `VERIFIED_LIVE`: downloaded, 5,269,146 bytes, parsed in full.

Set those against the crime-data side and five states line up on both:

| state | station-level crime data | access | jurisdiction polygons | population (approx) |
|---|---|---|---|---|
| **Bihar** | SCRB public FIR repository, all FIRs, daily | scrape | yes | ~130M |
| **Karnataka** | FIR search across 906 stations, daily | scrape | yes (+ station KML) | ~68M |
| **Tamil Nadu** | eServices FIR, 39 police districts, daily | scrape | yes | ~78M |
| **Telangana** | citizen portal FIR, 709 stations, daily | scrape | yes | ~38M |
| **Andhra Pradesh** | FIR search, all stations, daily | scrape | yes | ~54M |

Two more states have excellent crime data but no polygons, so they map as station points with
approximated catchments rather than filled areas:

| state | station-level crime data | polygons | note |
|---|---|---|---|
| **Maharashtra** | published FIRs statewide, daily, timestamped to the second, no login or captcha | no | the richest single feed found |
| **Kerala** | per-station crime statistics pages + FIR search back to 2016 | no | already publishes aggregates, so the RTI ask is trivial |

Rajasthan has polygons and a public FIR search, but behind a captcha — which we treat as a
closed door, not an obstacle to engineer around.

## 2. The granularity ladder

What exists at each level, nationally:

| level | what exists | cadence | lag | verdict |
|---|---|---|---|---|
| National / state | NCRB *Crime in India*; ~2,521 NCRB resources on data.gov.in | annual | 12–24 months | solid, boring, necessary |
| District | NCRB supplementary tables only — **not** in Volumes 1–3; 2016 and 2017 have none at all. On data.gov.in the district crime series **stops in 2014-15** | annual | 12–24 months | the national ceiling |
| City | NCRB metro chapters (population 1M+); ~593 city resources | annual | 12–24 months | usable |
| Police station | **no national source**; zero of 198,428 data.gov.in resources carry a police-station crime column | — | — | only via state portals |
| Point / incident | **none for crime, anywhere in India** | — | — | does not exist |

The single most important line in this table is the last one. India publishes no geocoded
crime incidents. Any product promising a street-level crime pin is either using a state FIR
feed geocoded to the *station*, or it is making data up — and, per §6, some published apps are
doing exactly the latter.

## 3. What does not exist (so we stop looking)

- **Geocoded crime incidents.** Not at national level, not in any state. FIR records carry a
  police station, not a location.
- **NCRB microdata.** No unit-level release, no researcher access process.
- **A national citizen FIR search.** CCTNS is police-only; the Digital Police Portal does not
  expose one.
- **Police station polygons for 29 of 36 states/UTs.**
- **An official IPC→BNS concordance.** BNS s.358 simply repeals the IPC; there is no statutory
  mapping schedule. Every dataset spanning 1 July 2024 therefore carries two incompatible
  section-numbering systems with no authoritative crosswalk between them. The only mapping we
  hold is a hand-built ~110-row table in `research/sources/taxonomy-methodology.md` §1.3, of
  which two rows are web-verified. Building and maintaining that concordance is an unavoidable,
  un-delegatable cost of ingesting any post-2024 Indian crime data.
- **A national crime victimisation survey.** India has never run one. This is why reported
  crime is all we have, and why §5 matters so much.
- **NFHS district-level violence data.** Corrected during this research: district fact sheets
  carry 104 indicators, none measuring violence. The violence indicators are 125–127 of the
  *state* fact sheet, because the module runs on a subsample. District prevalence is
  *computable* from DHS Individual Recode microdata with the `d005` weight — a real analytical
  project, not a download, and the highest-value one in the catalogue.

## 4. The one genuinely point-level public dataset is not crime

**MoRTH/NHAI road accident black spots**: 13,795 identified 500-metre highway segments with
state, highway number, chainage and landmark, published as office-memorandum annexures.
Geocoding chainage against the national highway GIS alignment is tractable, and a GitHub search
returned zero repositories working with it — nobody has liberated this.

For an Indian resident, road danger is a larger daily risk than violent crime and is far better
located. This should be a first-class layer, not an afterthought.

## 5. Three ways this map could lie

Each of these was found independently by a different agent. Together they are the design brief
for the honesty layer, and they are not footnote material — they belong on the map's face.

**(a) The map of reported crime is partly a map of police responsiveness.**
A well-policed neighbourhood where people trust the station and FIRs get registered will show
*more* crime than a neighbourhood where registration is refused. The error is signed, not
random, so it does not average out. The north-east is the extreme case: a Nagaland helpline
logged over 200,000 calls since 2016 against roughly 3,400 registered cases. **Colouring
Nagaland green because its reported rate is low would invert the truth**, and would be this
project's worst failure mode.

**(b) The most-wanted categories are systematically missing.**
A Supreme Court direction of 7 September 2016 means sexual offences, POCSO and terrorism FIRs
are withheld from public FIR publication by every state. So the finest-grained data we have
omits precisely the crimes a woman checking a neighbourhood most wants to see. The map must say
so where those categories would appear, rather than rendering a reassuring blank.

**(c) One word, "location", means at least seven different things.**
The national cyber-fraud portal counts the victim's district. The cyber coordination centre's
hotspot list counts the offender's district. NCRB counts the police station that registered the
FIR. Trafficking data records the rescue city, not the source village. Narcotics data records
the interdiction point — a highway checkpoint, not where drugs are sold. Court data records the
court venue, a taluka seat. Blend these and the map is confidently false. Every source in the
catalogue now carries a mandatory `location_semantics` field for this reason, and **almost all
police-published counts are `reporting-office`, not `offence-location`.** Across 540 sources the
backfill came out at: reporting-office 181, n/a 150, offence-location 50, victim-residence 24,
court-venue 21, interdiction-point 9, jurisdiction-aggregate 6, unknown 6, service-point 5,
offender-residence 3.

Three concrete cases where getting this wrong would produce a specifically defamatory map:

1. **The cyber-fraud reporting portal records the victim's district; the cyber coordination
   centre's hotspot list records the offender's district.** Same word, opposite ends of the same
   offence. Plotting them on one layer would brand Jamtara and Bengaluru identically.
2. **Human trafficking FIRs are registered where the victim is rescued.** A choropleth of them
   marks Delhi and Mumbai as *source* areas when they are destinations.
3. **Narcotics seizure tables record border, highway and port checkpoints.** That is a map of
   enforcement effort, not of drug prevalence.

## 6. Contamination already in the wild

Two widely-circulated Kaggle "Indian crime" datasets are hazards, not sources. One ships a file
explicitly named as synthetic. The other cites no government origin and carries no coordinates,
yet is consumed as geocoded incident data. **Both are already embedded in public crime-map
applications.** Since no Indian authority publishes national per-incident FIR records, any
dataset claiming to be one is fabricated by construction. Verify and blacklist before anything
touches our pipeline.

## 7. Legal gates before anything ships

Not legal advice; a list of what an Indian lawyer must clear. Detail in
`research/sources/legal-ethics.md`.

1. **Publishing FIR-derived data.** Published FIR listings carry names of complainants and
   accused. Aggregate to station-month and drop identifiers at ingestion, as a standing rule.
2. **Victim identity is a criminal matter.** IPC 228A (BNS equivalent) and POCSO s.23 make
   disclosure of a victim's identity an offence. A news report plus a precise map pin can
   jointly identify someone even when neither does alone.
3. **Criminal defamation.** Indian defamation is criminal as well as civil, and truth alone is
   not a complete defence — it must be truth *and* public good. "This locality has high crime"
   is exposed in a way it would not be in the UK or US.
4. **Communal and caste segregation.** Indian localities are frequently segregated by caste and
   religion. A crime heat map can function as a communal map. This is the most serious ethical
   risk in the project and it constrains design from day one: minimum aggregation thresholds,
   rates not raw counts, suppression of small numbers, no point pins in residential areas.
5. **Terms of use and the DPDP Act 2023**, including its amendment to RTI s.8(1)(j), which
   appears to have removed the public-interest override. Verify commencement before relying on it.
6. **Map boundary compliance.** Maps published in India must depict national boundaries per
   Survey of India.

**Standing engineering rule adopted from this:** we do not defeat CAPTCHAs, and we do not scrape
what a portal's terms forbid. Rajasthan's captcha-gated FIR search is therefore out of scope even
though it would be useful.

## 7b. The design discipline to inherit from police.uk

The benchmark dossier's sharpest observation: **police.uk is not a map, it is an anonymisation
pipeline with a map on top.** No crime is ever published at its true location. Every crime is
snapped to the nearest entry in a pre-built master list of anonymous map points, each sitting
over a street centre, park or commercial premise, and each of whose catchment contains **at
least eight postal addresses — or none at all**. If the nearest map point is more than 20 km
away, the coordinates are zeroed out entirely.

That rule is the reason a public crime map can exist in a democracy without becoming a tool for
targeting households. It is worth restating that the published point-count estimates disagree
across three independent third-party projects (680,000 / ~750,000 / ~760,000) and none cite an
official figure — **the rule is solid, the number is folklore** until the official page is
re-read.

**What this means for India, which is the interesting part.** We have no point-level crime data,
so we cannot make the mistake police.uk had to engineer around. Our smallest unit is the police
station jurisdiction — which in urban India contains tens of thousands of people, far above any
disclosure threshold. The anonymisation problem is solved for us by the data's coarseness.

But the *principle* transfers and should be adopted as a hard rule: **never display a count for
a unit below a minimum population and a minimum count threshold.** In India the binding risk is
not identifying a household; it is §7(4) — stigmatising a locality that is segregated by caste
or religion. Same discipline, different threat model.

Two more things worth copying directly:
- **The bulk CSV is the real product, not the API.** police.uk's API does not even carry the
  area codes; the monthly CSV archive does, and that is what every serious analyst uses. We
  should ship a bulk file from day one rather than treating it as an afterthought.
- **The outcomes model.** police.uk shows what *happened* to each crime, not just that it was
  reported. India's equivalent is the eCourts FIR-details join (see `judiciary-prisons`), with
  the standing caveat that only chargesheeted cases reach court.

## 8. Ranked next actions

**Verification first — everything below assumes it.**
0. Run `research/verify_sources.py` from an unblocked network. 469 URLs, rate-limited, produces
   `URL_CHECK.md`. Until this runs, 86% of the catalogue is a target list, not a source list.

**Then, in order of value per unit of effort:**
1. **Decompress the 7-state police polygon release and the 16,459-station point file, and build
   the geography spine.** This is the product's foundation and it is sitting in a GitHub release.
   Expect work: the station codes are the MHA/NCRB alphabetical series, *not* Census 2011 codes,
   so a crosswalk is mandatory; 843 stations carry stale post-reorganisation district codes;
   station names are not unique (14,647 distinct names for 16,459 stations) so never join on name.
2. **Build one state end to end as the pilot.** Recommend **Bihar** — public all-FIR repository,
   daily, scrapable, plus jurisdiction polygons. Karnataka is the strong alternative and has the
   best supporting data (OpenCity crime CSVs, station KML, monthly crime reviews).
3. **Ingest the boring national backbone**: NCRB district tables and the data.gov.in resources.
   Slow and coarse, but it is the benchmark every state feed gets validated against.
4. **Geocode the MoRTH black spots.** Nobody has. It is the only point-level public safety data
   in India and it would differentiate the product immediately.
5. **Mine Parliament Q&A.** Rajya Sabha answers are already published as CSV on data.gov.in.
   District-level tables surface there that exist nowhere else, with no fee and no 30-day wait.
6. **Compute NFHS district violence prevalence** from DHS microdata. This is the honest
   counterweight to reported-crime layers, and the only way to show where crime is *not* reported.
7. **File RTI draft (b)** — the station master with jurisdiction — in Kerala, Odisha and
   Maharashtra. Kerala first: it already publishes per-station statistics, so the ask is for a
   machine-readable copy of something already conceded. Drafts in `research/sources/rti-playbook.md`.

## 9. Verification debt

| status | count | meaning |
|---|---|---|
| `VERIFIED_LIVE` | 35 | data actually fetched and inspected |
| `VERIFIED_LANDING` | 17 | page loaded, data not opened |
| `CITED` | 302 | URL and title from a search index, page never opened |
| `UNVERIFIED` | 101 | believed to exist, no URL confirmed |

The `rti-playbook` dossier is **entirely unverified** — written from model knowledge after two
subagent attempts died on a content filter, with every `.gov.in` host blocked. Its statutory
section numbers, fee amounts and portal addresses must each be checked against the bare Act.

Two things could not be attempted at all and remain open:
- **CIC decisions on crime statistics.** The precedent that would settle how state police
  actually respond to these asks. Highest-value single verification task.
- **A per-state RTI filing table** (portal, fee, payment method, address). The operational
  prerequisite for any filing campaign; it does not exist yet.
