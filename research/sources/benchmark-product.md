# Benchmark Products — police.uk and International Crime-Map Analogues
_Agent: benchmark-product · Researched: 2026-09-19 · Entries: 3 verified / 26 total_

> **Environment caveat, stated up front.** This session's egress proxy blocked `data.police.uk`,
> `www.police.uk`, `www.gov.uk`, `www.ons.gov.uk`, `www.saps.gov.za`, `api.usa.gov`,
> `data.cityofchicago.org`, `arxiv.org` and `web.archive.org`. The session's WebSearch budget was
> also exhausted (200/200) before this agent started. Everything below was therefore reconstructed
> from **sources I could fetch**: Wikipedia, `github.com`, and `raw.githubusercontent.com` — i.e.
> working client code, ingestion pipelines, university course材 and a data-journalism post that
> **quote the official documentation verbatim**. Where I quote police.uk's own words, the quote is
> reproduced from a fetched third-party page that cites the official anchor URL; I did not read the
> official page myself. `verification` is `CITED` for almost everything, and that is accurate, not
> lazy. Re-verification against the primary domains is the first task of Phase 2 and is listed in
> **Blockers**.

## Executive summary

- **police.uk is not a map; it is an anonymisation pipeline with a map on top.** The single most
  transferable thing in it is the rule that no crime is ever published at its true location. Every
  crime is **snapped to the nearest entry in a pre-built master list of anonymous map points**, each
  of which sits over a street centre / park / commercial premise and whose catchment contains **at
  least eight postal addresses or none at all**; if the nearest map point is **more than 20 km away
  the coordinates are zeroed out**. The master list was built in 2012 from Ordnance Survey data.
- **Published estimates of the map-point count disagree** (680,000 / ~750,000 / ~760,000 across three
  independent third-party projects). None of them cite the official figure with a page reference.
  Treat "~750,000" as folklore until the official `/about/` page is re-read. The *rule* is solid; the
  *count* is not.
- **The API is small, unauthenticated, and free.** Base `https://data.police.uk/api`, no API key,
  leaky-bucket rate limit of **15 requests/second with a burst of 30**, licensed **Open Government
  Licence v3.0**. The whole thing is roughly 20 endpoints. This is a realistic target for us to copy
  in shape, if not in content.
- **The bulk CSV is the real data product, not the API.** The API does not carry LSOA codes; the
  monthly CSV archive does. Anyone doing area analysis uses
  `https://data.police.uk/data/archive/{YYYY-MM}.zip` → `{force}/{YYYY-MM}-street.csv` with the
  12-column schema `Crime ID, Month, Reported by, Falls within, Longitude, Latitude, Location,
  LSOA code, LSOA name, Crime type, Last outcome category, Context`. **We should ship a bulk file
  from day one for exactly this reason.**
- **The outcomes model is the honesty mechanism.** 14 crime categories × 9 outcome categories, where
  the two largest outcomes are *"Investigation complete; no suspect identified"* and *"Unable to
  prosecute suspect"*. Publishing outcomes alongside counts is what stops a crime map from reading
  as a list of solved crimes. India's structural analogue is the **charge-sheeting rate and
  conviction rate**, which NCRB already publishes.
- **police.uk's known failure modes are precisely our failure modes.** A local-journalism
  investigation found 41 shoplifting offences mapped to a location with no shops nearby; the Home
  Office attributed it to "inconsistent geocoding policies". Snap points create phantom hotspots at
  street centroids, car parks and station forecourts. Separately, a commercial property-research
  skill I fetched describes police.uk as *"best-in-class **address-level** crime data"* — it is not
  address-level, and that misreading by a downstream commercial consumer **is the harm**, arriving
  without anyone lying.
- **Nobody should copy police.uk's geography directly.** LSOA (~1,500 residents) exists because
  England & Wales have a stable, nationally-maintained small-area statistical geography with
  population denominators attached. India's nearest structural equivalents are the **revenue village**
  (rural) and the **census ward / enumeration block** (urban) — and the ward is far too big while the
  enumeration block is not published with boundaries. The unit India *actually* has is the **police
  station jurisdiction**.
- **South Africa, not the UK, is the model India should copy.** SAPS publishes **police-station-level
  counts quarterly** across 17 community-reported serious-crime categories, with **no point data at
  all**, and Stats SA publishes matching **police district boundary polygons**. That is the exact
  shape India can reach: the police station is India's real administrative atom, its jurisdictions
  exist on paper, and per-station per-month per-head FIR counts are a record the police already keep.
- **Mexico's SESNSP is the cadence model.** ~2.56 million rows, 2,486 municipalities, monthly cuts,
  a four-level crime taxonomy (bien jurídico → tipo → subtipo → modalidad), published as one CSV.
  It also demonstrates the failure we should design against: the official portal now hides behind a
  JS anti-bot challenge and non-durable OneDrive links, and the CKAN API has returned 403 since
  2026-08-13, so the only working path is an undocumented mirror host.
- **The survey pairing is non-optional for India.** England & Wales run the **CSEW** (~31,000 adults
  + ~1,500 children 10–15 a year) explicitly because police-recorded crime misses most crime — by
  1998 fewer than half of offences were reported to police. India's analogue is **NFHS** (plus SPIR).
  A reported-crime map without a survey layer will map *reporting behaviour* and call it *crime*.
- **Finest granularity achievable in this domain (for the benchmarks):** `point` (snapped) for
  UK/US city open data; `police-station` for South Africa; `city`/`municipality` for Mexico, Brazil,
  Colombia and most of Europe. **Finest defensible for India v1: `district`, with a
  `police-station` pilot.**
- **The biggest blocker in this domain is not access, it is the temptation to over-deliver.** Every
  product here that publishes finer than it can justify (SpotCrime address scores, CrimeGrade
  block-level ML gap-filling, Citizen's scanner feed) has a documented harm attached to it.

## Source entries

### 1. data.police.uk API

The public JSON API behind police.uk. Unauthenticated, free, OGL v3.0. Base URL
`https://data.police.uk/api`. Documentation at `https://data.police.uk/docs/`, call limits at
`https://data.police.uk/docs/api-call-limits/`.

**Rate limiting** (quoted from the `ukpolice` R package vignette, which paraphrases the docs):
> "The API uses a 'leaky bucket' rate limiter, which allows for 15 requests per second with a burst
> of 30. This allows for 15 requests each second, but up to 30 in a single second at one go. The API
> does not require authentication."

**Endpoints observed in fetched, working client code** (`Mta-adham/IngestEngine/src/clients/police_uk.py`):

```
GET /forces                                      list of forces
GET /forces/{force_id}                           force detail
GET /{force_id}/neighbourhoods                   neighbourhoods in a force
GET /{force_id}/{neighbourhood_id}               neighbourhood detail
GET /{force_id}/{neighbourhood_id}/boundary      neighbourhood boundary (lat/lng vertex list)
GET /locate-neighbourhood?q={lat},{lng}          which neighbourhood team covers a point
GET /crime-categories?date=YYYY-MM                valid categories for that month
GET /crimes-street/{category}?lat=&lng=&date=     street-level crimes, 1-mile radius of a point
GET /crimes-street/{category}?poly=lat,lng:lat,lng:...&date=   same, custom polygon
GET /crimes-at-location?lat=&lng=&date=           crimes snapped to one specific map point
GET /crimes-no-location?force=&category=&date=    crimes the force could not locate
GET /outcomes-at-location?lat=&lng=&date=         street-level outcomes
GET /stops-street?lat=&lng=&date=                 stop & search by area
GET /stops-force?force=&date=                     stop & search by force
GET /crime-last-updated                           date of most recent data load
GET /crimes-street-dates                          which months are available, per force
```

**Additional endpoints named as tools in a published MCP client** (`dwain-barnes/police-uk-api-mcp-server`,
21 tools) but whose exact paths I did **not** see in fetched code — treat the paths as inferred:
senior officers (`/forces/{id}/people`), neighbourhood team / events / priorities
(`/{force}/{nh}/people|events|priorities`), outcomes for a single crime
(`/outcomes-for-crime/{persistent_id}`), stops at location (`/stops-at-location`), stops with no
location (`/stops-no-location`).

**Example calls** (reproduced verbatim from `jdorfman/awesome-json-datasets`, as mirrored in
`trackawesomelist/trackawesomelist` and `bgoonz/awesome-4-new-developers`):

```
https://data.police.uk/api/crimes-at-location?date=2015-02&lat=52.629729&lng=-1.131592
https://data.police.uk/api/crimes-street-dates
https://data.police.uk/api/leicestershire/neighbourhoods
https://data.police.uk/api/forces
```

and, from `hrbrmstr/jwatr` (note: **POST** works as well as GET):

```r
POST(url = "https://data.police.uk/api/crimes-street/all-crime",
     query = list(lat = "52.629729", lng = "-1.131592", date = "2017-01"))
```

and a real polygon call captured in a fixtures manifest (`kyky2347/pulse-london`), dated 2026-09-11:

```
https://data.police.uk/api/crimes-street/all-crime?poly=51.356760,-0.390377:51.426760,-0.390377:51.426760,-0.510377:51.356760,-0.510377&date=2026-07
```

**Crime object response fields:** `id`, `persistent_id`, `category`, `month`, `context`,
`location_type`, `location_subtype`, `location{latitude, longitude, street{id, name}}`,
`outcome_status{category, date}`.

**Critical limitation:** the JSON API does **not** return LSOA identifiers. The bulk CSV does. Any
area aggregation must go through the CSV route.

```
id: police-uk-api
tier: 2   geo_granularity: point (snapped)   unit_of_record: incident-point
cadence: monthly   lag: ~1-2 months   license: OGL-v3.0   access: open-download
machine_readable: 5   ingest_difficulty: 1   priority: 5 (as design benchmark)
verification: CITED   checked_on: 2026-09-19
```

### 2. police.uk bulk CSV downloads / monthly archive

The custom-download page is `https://data.police.uk/data/`; the full monthly archives follow the
pattern `https://data.police.uk/data/archive/{YYYY-MM}.zip` (URL pattern reproduced from a working
fetch script, `SocialCatalystLab/ape-papers/apep_0472/v1/code/01_fetch_data.R`). Each zip contains
per-force directories with `{force}/{YYYY-MM}-street.csv`, plus `-outcomes.csv` and
`-stop-and-search.csv`.

**Street CSV schema — 12 columns, confirmed identically across five independent repositories:**

| # | column | notes |
|---|---|---|
| 1 | `Crime ID` | 64-char hash; the API's `persistent_id`. **Blank for anti-social behaviour rows.** |
| 2 | `Month` | `YYYY-MM`. There is no day, and no time of day, anywhere in the public data. |
| 3 | `Reported by` | force that took the report |
| 4 | `Falls within` | force in whose area it occurred — differs from `Reported by` for cross-border and BTP |
| 5 | `Longitude` | **snapped** WGS84; blank if zeroed out |
| 6 | `Latitude` | **snapped** WGS84 |
| 7 | `Location` | human string, always of the form `On or near <street>` — never a house number |
| 8 | `LSOA code` | e.g. `E01031464` |
| 9 | `LSOA name` | e.g. `Arun 007F` |
| 10 | `Crime type` | one of the 14 categories |
| 11 | `Last outcome category` | one of the 9 outcome categories |
| 12 | `Context` | free text; almost always empty |

Sample row (from `AlistairLR112/EnglandCrimeAssociations`):
`2012-08 | Metropolitan Police... | Metropolitan Police... | -0.508053 | 50.809718 | On or near Claigm... | E01031464 | Arun 007F | Violent crime | Under investigation | null`

Note the `Location` field's construction — `"On or near <street>"` — is itself a deliberate honesty
device. The string can never be read as an address.

**Retention:** an ingestion project active in 2026 (`djshaf/NightRunner`) reports that
"data.police.uk maintains only a rolling ~3-year window. The earliest currently available data is
June 2023," and dynamically resolves available months per run rather than assuming a start date.
If true this is a significant change from the original Dec-2010 series and a **major product lesson**:
*if you don't archive it yourself, the publisher will delete your history.*

```
id: police-uk-bulk-csv
tier: 2   geo_granularity: point (snapped) + LSOA   unit_of_record: incident-point
time_start: 2010-12 (historically); ~2023-06 in the live rolling window as of 2026
cadence: monthly   license: OGL-v3.0   access: open-download   machine_readable: 4
ingest_difficulty: 1   priority: 5   verification: CITED   checked_on: 2026-09-19
```

### 3. police.uk location-anonymisation methodology  ← **the important one**

Official anchor: `https://data.police.uk/about/#location-anonymisation`.

Reproduced verbatim from a data-journalism post by Glyn Mottershead
(`egrommet/egrommet.github.io`, `post/data-police-location-issues/index.html`) which quotes the
official page and links that anchor:

> **"The latitude and longitude locations of Crime and ASB incidents published on this site always
> represent the approximate location of a crime — not the exact place that it happened."**
>
> *How are crime locations anonymised?*
> We maintain a master list of anonymous map points. Each map point is specifically chosen so that it:
> - Appears over the centre point of a street, above a public place such as a Park or Airport, or
>   above a commercial premise like a Shopping Centre or Nightclub.
> - Has a catchment area which contains at least eight postal addresses or no postal addresses at all.
>
> When crime data is uploaded by police forces, the exact location of each crime is compared against
> this master list to find the nearest map point. The co-ordinates of the actual crime are then
> replaced with the co-ordinates of the map point. *If the nearest map point is more than 20km away*,
> the co-ordinates are zeroed out. **No other filtering or rules are applied.**

The post further records that the master list was **created in 2012 using Ordnance Survey data**.

An independent restatement, from a university GIS course (`jo-wilkin/GEOG0030` and
`jtvandijk/GEOG0030_20232024`):

> "This displacement occurs to preserve anonymity of the individuals involved. The process by how
> this displacement occurs is standardised. There is a list of anonymous map points to which the
> exact location of each crime is compared against this master list to find the nearest map point.
> The co-ordinates of the actual crime are then replaced with the co-ordinates of the map point.
> **Each map point is specifically chosen to avoid associating that point with an exact household.**
> ... the police also convert the data from their recorded BNG eastings and northings into WGS84
> latitude and longitude."

**The rule, in one sentence, for our spec:**
> *Every crime is moved to the nearest point on a fixed, pre-published list of anonymous map points,
> each of which sits on a street centre or public/commercial feature and covers a catchment of at
> least eight postal addresses (or none at all); if no map point lies within 20 km the coordinates
> are deleted entirely.*

**Five design properties worth copying, independent of the eight-address number:**
1. **The point list is fixed and pre-computed, not derived per-release.** Snapping is deterministic
   and reproducible; it does not leak information through jitter that varies between releases.
2. **It is not random displacement.** Gaussian jitter/geomasking can be statistically inverted given
   enough incidents; snapping to a shared point cannot — multiple crimes collapse onto one identical
   coordinate and become mutually indistinguishable. This is k-anonymity by construction.
3. **Points are deliberately placed on features that are not homes.** Street centres, parks,
   airports, shopping centres, nightclubs. The rule "never a house" is enforced by *where the points
   are*, not by a post-hoc check.
4. **The k threshold (8 addresses) is published.** Users can reason about the privacy guarantee.
5. **The fallback is deletion, not approximation.** Beyond 20 km, the answer is "no location",
   which is why `crimes-no-location` exists as a first-class endpoint. **Having an explicit
   "we do not know where this was" bucket is a feature.**

**What it costs:** snapping concentrates incidents onto street centroids, so a point with 41 offences
is an artefact of the grid, not a hotspot (see entry 6). Any consumer computing "crimes within 100 m
of this address" is computing noise.

**Spatial resolution, empirically measured** (`djshaf/NightRunner`, Camden, one 6-month pull):
1,384 distinct snap points across ~21.8 km² — "roughly one point every ~125 m as an upper bound".
No official average spacing figure is published.

**ASB handling:** ASB is one of the 14 categories, is snapped by the same process, and carries **no
Crime ID and no outcome** (the CSV `Crime ID` column is blank for ASB rows and ASB has no entry in
the outcomes model). I saw the category in every category list and saw ASB discussed as snapped
alongside crime in the official quote ("Crime **and ASB** incidents"), but I did **not** find a
fetched source stating the blank-Crime-ID rule explicitly. **Flagged in Seed Leads for confirmation.**

```
id: police-uk-anonymisation-method
tier: 2   geo_granularity: point   unit_of_record: narrative-document
formats: ["HTML"]   license: OGL-v3.0   access: open-download   machine_readable: 1
ingest_difficulty: 1   priority: 5   verification: CITED   checked_on: 2026-09-19
```

### 4. police.uk crime categories and outcomes model

**14 crime categories** (list reproduced from `Janusz99bis/bigdata-crimes-airbnb-project`, and
corroborated by the GEOG0030 coursebook's "Coding of Crimes into 14 Categories"):

`anti-social-behaviour`, `bicycle-theft`, `burglary`, `criminal-damage-arson`, `drugs`,
`other-theft`, `possession-of-weapons`, `public-order`, `robbery`, `shoplifting`,
`theft-from-the-person`, `vehicle-crime`, `violence-and-sexual-offences`, `other-crime`.

(The slugs above are the conventional API slugs; the display names I verified are: Anti-social
behaviour, Bicycle theft, Burglary, Criminal damage and arson, Drugs, Other theft, Possession of
weapons, Public order, Robbery, Shoplifting, Theft from the person, Vehicle crime, Violence and
sexual offences, Other crime. Historic months also carry `Violent crime` — an older label seen in
2012 rows — so **the category list is month-dependent**, which is why `/crime-categories` takes a
`date` parameter. That is a design detail India will need too, for the IPC→BNS transition.)

**9 outcome categories:**
Offender given a caution · Under investigation · Investigation complete; no suspect identified ·
Unable to prosecute suspect · Awaiting court outcome · Further investigation is not in the public
interest · Local resolution · Action to be taken by another organisation · Further action is not in
the public interest. (Plus, in the data as it is actually served: `Status update unavailable` and
`Court result unavailable`.)

**Empirical shape of the outcomes distribution**, 2012–2016, England & Wales
(`BBC-Data-Unit/unsolved-crime`):

| Outcome | Total 2012–2016 |
|---|---|
| Investigation complete; no suspect identified | 9,424,687 |
| Under investigation | 2,427,381 |
| Unable to prosecute suspect | 1,649,291 |
| Court result unavailable | 715,163 |
| Offender given a caution | 611,237 |
| Local resolution | 482,307 |

**Read that table again.** The modal outcome of a recorded crime in England & Wales is *nothing
happened and nobody was identified* — and police.uk shows that to the public, per crime, on the map.
This is the single most credibility-building feature of the product, and it is the one that is
cheapest for us to replicate in India because NCRB already publishes charge-sheeting and conviction
rates by crime head.

A criminology teaching repo (`Adam-Ansar/west-midlands-crime-analysis`) notes the flip side:
> "Outcomes such as 'Unable to prosecute suspect' or 'Investigation complete; no suspect identified'
> are technically different but similarly indicate unresolved cases, making detailed outcome
> analysis challenging."

```
id: police-uk-categories-outcomes
tier: 2   geo_granularity: n/a   unit_of_record: aggregate-count
taxonomy: custom (14 Home Office categories)   license: OGL-v3.0   access: open-download
machine_readable: 5   ingest_difficulty: 1   priority: 5   verification: CITED   checked_on: 2026-09-19
```

### 5. police.uk neighbourhood boundaries and stop-and-search

**Boundaries:** `GET /{force}/{neighbourhood}/boundary` returns the polygon vertices for a
neighbourhood policing team area, and `GET /locate-neighbourhood?q={lat},{lng}` reverse-locates a
point to a team. This is how police.uk answers "who polices here", separately from "what happened
here". **It is a distinct product surface from the crime map and it is the one India can build
best** — every Indian police station has a jurisdiction, a phone number, and an SHO.

**Stop and search:** `/stops-street`, `/stops-force`, `/stops-at-location`, `/stops-no-location`.
Fields include type, object of search, outcome, datetime, and self-defined + officer-defined
ethnicity, age range and gender.

The ethnicity fields are the reason this dataset exists — they are what makes disproportionality
measurable. But note the deliberate choice made by one downstream consumer (`djshaf/NightRunner`),
which is a good rule for us to adopt in a *consumer safety* context:
> Retained: type, object of search, outcome, datetime. Deliberately excluded: gender, age range and
> ethnicity — "sensitive personal data with no legitimate role in a safety score."

**The distinction matters enormously for India.** Demographic breakdowns of police action belong in an
**accountability** product, where they are the point. They must never appear in a **neighbourhood
safety** product, where they become a caste/religion risk score for a locality.

```
id: police-uk-neighbourhoods-stops
tier: 2   geo_granularity: neighbourhood-polygon / point   unit_of_record: boundary-polygon, incident-point
cadence: monthly   license: OGL-v3.0   access: open-download   machine_readable: 5
ingest_difficulty: 1   priority: 4   verification: CITED   checked_on: 2026-09-19
```

### 6. Known criticisms of police.uk

**(a) Phantom hotspots from snapping.** Journalist Conor Gogarty investigated discrepancies in
mapped crime locations and found **41 shoplifting incidents mapped to a location with no nearby
shops**. Police confirmed the markers are "snap points" that pull reports from nearby areas rather
than exact crime locations; a Home Office spokesperson attributed inaccuracies to **"inconsistent
geocoding policies"**. (Via `egrommet/egrommet.github.io`.) Two failures compound here: the snap
grid itself, *and* forces geocoding inconsistently before snapping.

**(b) False precision, downstream.** A commercial property-research tool I fetched
(`soreavis/property-deep-dive`) describes the UK as *"Best-in-Class **Parcel-Level** Data"* with
*"**address-level** crime data"*. That is flatly wrong — police.uk is street-segment level by design.
**This is what the harm actually looks like in the wild:** not a lie by the publisher, but a
confident misreading by a commercial consumer that then sells "crime at this address" to a renter.
A working product spec I fetched (`Demonstrandum/floot`) states the counter-rule explicitly:
> "Resolution is *street segment, not address*. **Never present one snap point as 'crime at this
> address'.**"

**(c) Small-number noise.** The same spec: street-level crime counts "are often below 20 incidents
annually — raw rates are noise without statistical regularisation," and applies a 400 m buffer plus
**empirical-Bayes shrinkage toward the borough mean**. It also reports results as a **London
percentile rather than an absolute rate**.

**(d) Denominator errors.** The same spec separates footfall-driven acquisitive crime (theft from the
person, shoplifting, bicycle theft — normalise by **workday** population) from residential-relevant
crime (burglary, criminal damage, ASB, violence — normalise by **resident** population; burglary by
**household count**). Without this, "busy commercial area" and "dangerous area" become the same
colour. **Old Street looks like a crime hotspot purely because of pedestrian volume.**

**(e) Jurisdictional contamination.** British Transport Police records must be excluded from
neighbourhood analysis, or "every flat near a station looks terrible for reasons that have nothing
to do with the street-level safety" of that flat. India's analogue: Railway Police (GRP), and
specialised units whose FIRs are registered at a station that is not where the crime happened.

**(f) Category coarseness.** 14 buckets means "Violence and sexual offences" merges a pub fight and
a rape; "Other theft" absorbs a large residual. Outcome categories similarly merge distinguishable
legal states into indistinguishable "unresolved" (see entry 4).

**(g) Geography mismatch.** From the Manchester crime-mapping textbook (`maczokni/crime_mapping`):
LSOAs "may not bear much resemblance to what residents might think of as their neighbourhood."

**(h) The underlying number is reported crime.** The textbook is explicit that the data represents
"crime reported to the police". See entry 8.

*Not found in this session (blocked domains): the peer-reviewed literature on crime-map effects on
house prices, and the 2011-era UK privacy/ICO debate over crime-map granularity. Both are real and
both are listed in Seed Leads.*

```
id: police-uk-criticisms
tier: 4   geo_granularity: n/a   unit_of_record: narrative-document
formats: ["HTML","MD"]   access: open-download   machine_readable: 1
ingest_difficulty: 1   priority: 5   verification: CITED   checked_on: 2026-09-19
```

### 7. LSOA — the geography unit, and India's nearest equivalent

police.uk tags every crime with an LSOA code (`E01…`) and name (`Arun 007F`). LSOAs are the ONS
small-area statistical geography for England & Wales, designed to hold roughly **1,500 residents**
(brief's figure; ONS design constraints are a minimum of 1,000 residents / 400 households, with
~34,700 LSOAs in England & Wales at 2011 and ~35,700 at 2021 — **I could not verify these numbers,
ons.gov.uk was blocked; treat as UNVERIFIED**). Boundaries are published as shapefiles under OGL and
mid-year population estimates are published per LSOA, which is what makes rates computable.

**The three properties that make LSOA work, and which India must reproduce or abandon:**
1. Stable codes with a published change history between census rounds.
2. A **population denominator published at the same geography and refreshed annually**.
3. Open boundary polygons.

**India's candidates:**

| Unit | Approx. count (2011 Census) | Typical population | Boundaries public? | Denominator public? | Verdict |
|---|---|---|---|---|---|
| State/UT | 28 + 8 | tens of millions | yes | yes | too coarse, but the reliable floor |
| District | 640 | ~1.9 m mean | yes | yes | **v1 unit.** Reorganised frequently — needs a crosswalk |
| Sub-district / tehsil | 5,924 | ~200 k | partly | yes | useful tier 2 |
| Town | 7,935 | varies | partly | yes | urban framing unit |
| Village (revenue) | >600,000 | ~1,000–2,000 | patchy | yes | **closest LSOA analogue by population**, but rural only and boundaries are the hard part |
| Municipal ward | tens of thousands | 10 k–100 k | patchy | partly | too big, and reorganised at every delimitation |
| Census Enumeration Block | not published | ~100–200 households | **no** | **no** | correct size, but does not exist as a public geography |
| **Police station jurisdiction** | ~17,000 (BPR&D figure — **verify**) | varies wildly | **mostly no** | **no** | **the unit the data is actually recorded in** |

*Census counts above are verified from the Census of India article; 2011 is the latest completed
census — the 2021 census was postponed and enumeration is now scheduled from 1 October 2026
(Himalayan states) and 1 March 2027 (rest). **Our population denominators will be 16 years old at
v1 launch and this must be stated on the map.***

**The conclusion that should drive the whole product:** India has no unit that is simultaneously
(a) the size of an LSOA, (b) publicly boundaried, and (c) attached to a fresh population
denominator. The **police station** satisfies none of (a)–(c) cleanly but is the only unit the crime
data is natively recorded in. Therefore our geography roadmap is: **district now → police station
when we win the boundaries → never point.**

```
id: benchmark-lsoa-geography
tier: 1   geo_granularity: LSOA   unit_of_record: boundary-polygon
license: OGL-v3.0   access: open-download   machine_readable: 4
ingest_difficulty: 2   priority: 4   verification: UNVERIFIED (ons.gov.uk blocked)   checked_on: 2026-09-19
```

### 8. Crime Survey for England and Wales (CSEW) — the under-reporting counterpart

Run by **Verian (formerly Kantar Public) for the ONS**; data curated by the UK Data Service.
Established 1982 as the British Crime Survey; every four years initially, **continuous interviewing
from April 2001**. Sample: **~31,000 people aged 16+ per year, plus ~1,500 children aged 10–15**.
Reported by financial year with headline measures updated **quarterly** on a rolling 12-month basis.

**Why it exists, in one number:** by 1998 the police received reports for **fewer than half of all
offences that occurred**.

**Coverage gaps (the caveats we inherit):** excludes non-household populations (~1.7% of England &
Wales — care homes, prisons, homeless); excludes homicide and victimless crimes such as drug
possession; struggles with rare high-harm crimes due to sample size; historically undercounted
repeat victimisation such as domestic violence through capping.

**Why this matters more in India than in the UK.** The UK pairs a near-complete police-recorded
series with a survey that corrects it at the margin. India will pair a *demonstrably incomplete*
police-recorded series with a survey. **The survey layer is therefore not a refinement for us — it
is the thing that stops the map being wrong.** An Indian district with low recorded crime against
women may have low crime or may have a police station that refuses to register FIRs, and only survey
prevalence can tell those two apart. The Indian analogue is **NFHS** (which carries spousal-violence
and help-seeking modules at district level) plus **SPIR**; both belong to other agents' domains, and
this agent's recommendation is that the map **must not ship without one of them wired in**.

```
id: ons-csew
tier: 1   geo_coverage: England & Wales   geo_granularity: national/regional
unit_of_record: survey-respondent   time_start: 1982   cadence: quarterly (rolling 12m)
license: OGL-v3.0   access: open-download (tables) / login (microdata via UK Data Service)
machine_readable: 4   ingest_difficulty: 2   priority: 5   verification: CITED   checked_on: 2026-09-19
```

### 9. FBI Crime Data Explorer / NIBRS

NIBRS is "an incident-based reporting system used by law enforcement agencies in the United States
for collecting and reporting data on crimes." Agencies submit every incident and arrest for
**Group A offences (52 offences in 23 crime categories)**, plus arrest data for **10 Group B
offences**. Approved for general use at a national UCR conference in **March 1988**; became the sole
FBI collection standard on 1 January 2021.

**What NIBRS does that police.uk does not:**
- **No Hierarchy Rule.** Summary UCR reported only the most serious offence in a multi-offence
  incident; NIBRS records **all** offences. *This is precisely the NCRB principal-offence-rule
  problem, and NIBRS is the proof that abolishing it is possible and what it costs.*
- Three offence classes: Crimes Against Persons, Property, **and Society** (drugs etc.).
- Seven linked segments per incident: offence (incl. **location type**, weapons, completion status),
  victim (age, sex, race, ethnicity, relationship to offender, injury), offender (age, sex, race),
  property (loss type, value, description, recovery), arrestee, plus zero-reporting.

**The transition cost, in numbers** — and this is the warning for India:
- 1 Jan 2022: 11,794 agencies, **69% population coverage**
- Q2 2023: 13,363 agencies — the FBI stated it was **"unable to make confident statements about
  national crime trends"** because of incomplete data
- Q4 2023: 15,199 agencies, **82% coverage**

A richer taxonomy adopted mid-series **broke the national trend line for roughly three years**.
India is doing the same thing right now with the IPC→BNS transition (in force 1 July 2024). We
should expect and design for a 2–4 year period in which *no honest year-on-year comparison spans the
break*, and we should mark it on every chart rather than quietly interpolating.

**Granularity:** CDE serves agency-level and state-level aggregates. It does **not** publish
incident coordinates — US point-level data comes from cities, not the FBI.

```
id: fbi-cde-nibrs
tier: 1   geo_coverage: USA   geo_granularity: agency/state   unit_of_record: case-record (incident)
cadence: annual + quarterly   lag: ~6-12 months   taxonomy: NIBRS Group A/B
formats: ["CSV","JSON","dashboard-only"]   access: api-key (api.data.gov key)   machine_readable: 5
ingest_difficulty: 2   priority: 3   verification: CITED   checked_on: 2026-09-19
```

### 10. US city open data — Chicago, NYC, Seattle, SF, Detroit, Denver

The US practice that distinguishes it from the UK: **cities publish incident-level records with
coordinates and block-level addresses, on Socrata/ArcGIS, refreshed daily, with no snap-point
anonymisation layer.** Instead they truncate the address to the block (e.g. "0XX N STATE ST") and
round coordinates.

Verified dataset identifiers (from multiple independent ingestion pipelines):

| City | Dataset | Endpoint | Cadence |
|---|---|---|---|
| Chicago | Crimes 2001–Present | `https://data.cityofchicago.org/resource/ijzp-q8t2.json` (docs: `dev.socrata.com/foundry/data.cityofchicago.org/ijzp-q8t2`) | daily, with publication lag |
| NYC | NYPD Complaint Data Historic | `https://data.cityofnewyork.us/resource/qgea-i56i.json` | ~annual |
| NYC | NYPD Complaint Data Current (YTD) | `5uac-w243` | ~quarterly |
| NYC | NYPD Arrests | `8h9b-rp9u` (historic) / `uip8-fykc` (YTD) | as above |
| Seattle | SPD Crime Data | `https://data.seattle.gov/d/tazs-3rd5` | daily |
| San Francisco | Police incident reports | `wg3w-h783` | daily |
| Detroit | RMS Crime Incidents | `https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/RMS_Crime_Incidents/FeatureServer/0` | daily |
| Denver | Crime Offenses | `https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/ODC_CRIME_OFFENSES_P/FeatureServer/324` | weekdays |

Bulk CSV via `https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv` and
`https://data.cityofnewyork.us/api/views/qgea-i56i/rows.csv?accessType=DOWNLOAD`.

**The controversy.** Block-level publication plus daily cadence means a determined observer can
often identify the household — particularly for burglary on a short residential block, and
catastrophically for domestic violence and sexual offences, where many US cities consequently
suppress or generalise those categories inconsistently between agencies. The US has no national
anonymisation standard; each city invents one. **The UK's single national snap-point list is
strictly better governance, and it is the model to imitate even though we will never publish points.**

**A second lesson:** NYC's split into "Historic" and "Year To Date" datasets with different lags,
and the resulting need to query and merge both, is a pattern we will face with Indian state portals.
Design the ingestion layer to treat "the same series arriving from two endpoints with two lags" as
normal.

```
id: us-city-open-data-crime
tier: 2   geo_coverage: individual US cities   geo_granularity: point / block-address
unit_of_record: incident-point   cadence: daily   lag: 1-14 days
formats: ["JSON","CSV","GeoJSON"]   access: open-download   machine_readable: 5
license: varies (mostly public-domain / city ToU)   ingest_difficulty: 1   priority: 3
verification: CITED   checked_on: 2026-09-19
```

### 11. Crime Open Database (CODE) — mpjashby

An academic harmonisation layer over multiple US cities' open crime data, by Matthew Ashby (UCL):
"a service that makes it convenient to use crime data from multiple US cities in research on crime."
Data and documentation are hosted on OSF (`https://osf.io/zyaqn/`). Licence: free to use with
acknowledgement. The repository code (`code/02_load_crime_data.R`) shows per-city download +
recoding into a common offence scheme (e.g. `'ARSON' ~ '200 Arson'`).

**Why it matters to us more than any single city portal:** it is the proof-of-concept for exactly the
hard problem India presents — *many publishers, incompatible taxonomies, one comparable output*. If
we build an Indian equivalent, CODE is the design precedent for: a published crosswalk table, a
versioned harmonised category scheme, and honest per-city coverage notes. **This is our IPC/BNS →
common-category mapping problem, already solved once for a different country.**

```
id: crime-open-database
tier: 4   geo_coverage: multiple US cities   geo_granularity: point
unit_of_record: incident-point   formats: ["CSV"]   access: open-download   machine_readable: 4
license: attribution-required   ingest_difficulty: 2   priority: 3   verification: VERIFIED_LANDING
checked_on: 2026-09-19
```

### 12–15. US commercial crime-map products (SpotCrime, LexisNexis Community Crime Map, CrimeMapping.com, CityProtect, Citizen)

From a fetched 2026 competitive audit (`GojoCookz/Cyclopalypse/docs/competitive-audit-2026.md`) and
the Citizen Wikipedia article:

| Product | Data source | Granularity | Model | Note for us |
|---|---|---|---|---|
| **SpotCrime** (`spotcrime.com`, `spotcrime.io`) | 22k+ cities via direct LE feeds (CAD/blotters/open portals/FOIA) + verified news; 500M+ records | **address-level**; 9 normalised categories, sourced links | Free consumer (ads) + API tiers (Developer $199/mo, Pro $599/mo, Enterprise) | 2026: "expanded API with **address safety scores**/trends". This is the line we must not cross. |
| **LexisNexis Community Crime Map** (`communitycrimemap.com`, + RAIDS) | Direct agency RMS/CAD feeds, hundreds of agencies, "cleaned/geocoded/**redacted**" | block | Free public, B2G for agencies | Suffered a **2024 breach affecting 364k+**, disclosed 2025. Holding agency data centrally is a liability. |
| **CrimeMapping.com** (CentralSquare) | Automated daily RMS imports, **opt-in agencies only** | **"block-level privacy"** | B2G SaaS | *Opt-in* means coverage maps are participation maps. A blank area means "no contract", not "no crime". |
| **CityProtect** (Motorola) | Voluntary opt-in CAD/RMS, incl. **calls for service** | point/block | B2G SaaS | Retention 180 days–1 year. Publishing *calls for service* rather than verified offences is a distinct and much noisier product. |
| **Citizen** | Unencrypted public-safety radio + AI transcription + human analysts + user video; ~300–400 incidents surfaced daily from NYC's ~10,000 calls | incident, seconds-to-minutes | Freemium $5.99–$19.99/mo | Launched as **"Vigilante"** in 2016, pulled from the App Store within 48 hours for encouraging mob justice. In the 2021 Palisades Fire it posted a photo of an **innocent man** as the suspected arsonist with a **$30,000 bounty**; he was questioned and exonerated. |
| **CrimeGrade.org** | FBI UCR/NIBRS + local + **ML gap-filling (180+ variables)** | **block-level A–F grades** | Free + B2B licensing to insurers/real estate | Grades a block by *model output* where no data exists. This is fabrication with a confidence interval. |
| **NeighborhoodScout** (CoreLogic), **AreaVibes**, **Niche**, **Verisk CAP Index** | FBI-derived indexes, surveys | neighbourhood → **address-specific 0–2000 score** (Verisk) | real-estate lead-gen / insurance underwriting | AreaVibes lags 1+ years; Niche is 37.5% resident survey. The property-value/insurance pipeline is where a crime map stops being information and becomes a price. |

**The composite lesson from the commercial tier:** every one of these products monetises by making
the number *finer and more confident* than the underlying data supports, because an address-level
score is sellable to proptech and insurance and a district-level count is not. The commercial
gradient runs directly against the honesty gradient. **A public-interest Indian crime map must decide
in advance that it is not in this market, and should say so on the page.**

```
ids: spotcrime · lexisnexis-community-crime-map · crimemapping-com · cityprotect · citizen-app · crimegrade-org
tier: 5   geo_granularity: address / block   unit_of_record: incident-point
access: open-download (consumer) / paid (API)   license: ToU-restricts-reuse   machine_readable: 2
ingest_difficulty: 4   priority: 1 (as anti-pattern reference: 5)   verification: CITED   checked_on: 2026-09-19
```

### 16. SAPS quarterly crime statistics — South Africa  ← **the model India should copy**

Landing: `https://www.saps.gov.za/services/crimestats.php` (older releases:
`https://www.saps.gov.za/services/older_crimestats.php`). Published **quarterly**, as Excel
workbooks, at **police station (precinct) level**, for **17 community-reported serious crime
categories** plus detected crimes (drug-related, driving under the influence, illegal firearms),
culpable homicide, public violence and other offences. No point data whatsoever.

**Matching boundaries:** Stats SA publishes Police District polygons —
`https://www.statssa.gov.za/wp-content/uploads/2025/08/PoliceDistrict.zip`. Population denominators
per precinct from Census 2022 via the StatsSA SuperWeb API.

**What a working reconstruction looks like** (`afrith/crime-stats`, licensed **ODC PDDL v1.0**,
public domain):
- `crime-stats.csv` — monthly counts by station × category × year × month, **January 2020 to
  September 2025**, extracted from the quarterly PDFs/workbooks
- `police_stations.csv` — station name, Census 2022 population, area in km², and codes linking to
  local municipality, district municipality and province
- `police_stations.gpkg` — precinct boundary geometry with the same fields

**The three hard problems it had to solve, all of which India will have:**
1. **The raw data is in hidden worksheets.** The author wrote a separate tool (`afrith/unhide-xlsx`)
   to unhide the sheets containing the machine-readable numbers. *The publisher ships a
   presentation artefact and buries the dataset inside it.* Exactly the NCRB PDF problem.
2. **Station renaming and reorganisation.** Nine Eastern Cape stations renamed (Cradock→Nxuba,
   Grahamstown→Makhanda), fourteen name spellings standardised, two new stations (Phaudi, Majola)
   reallocated to parent districts. *This is the district-reorganisation problem at station scale,
   and it is unavoidable — a crosswalk table is a first-class deliverable, not a cleanup step.*
3. **Boundary topology.** Precinct polygons required PostGIS `ST_CoverageClean` to resolve
   slivers/overlaps.

**Why this is India's model rather than police.uk's:**

| | UK (police.uk) | South Africa (SAPS) | India (achievable) |
|---|---|---|---|
| Finest published unit | snapped point | **police station** | **police station**, where won |
| Prerequisite | national address register + 750k-point snap list + per-force monthly upload mandate | a spreadsheet per quarter per station | a spreadsheet per quarter per station |
| Boundaries | ONS, open | Stats SA, open | **missing — the binding constraint** |
| Denominator | LSOA mid-year estimates, annual | Census 2022 per precinct | Census **2011**, per district |
| Anonymisation needed | elaborate | **none — aggregation is the anonymisation** | **none** |
| Privacy risk | managed | structurally near-zero | structurally near-zero |

The decisive point: **SAPS needs no anonymisation methodology at all, because it never publishes a
location.** Aggregation to a jurisdiction with thousands of residents *is* the privacy mechanism.
India can have the SAPS product within one RTI cycle per state. India cannot have the police.uk
product at all, because the snap-point list presupposes a national address-point register that India
does not have in open form.

**Consumption pattern:** SAPS data is heavily re-used by civil society and the press — GBV
dashboards, academic theses joining precinct polygons to census blocks, open-source geospatial
pipelines producing GeoParquet/PMTiles (`ChelseaH93/sa-gbv-data`), and Kaggle mirrors
(`slwessels/crime-statistics-for-south-africa`, province × station × crime type). **The
station-level release created an ecosystem.** That is the strongest argument for making
police-station data the Indian product's north star.

```
id: saps-quarterly-station-crime-stats
tier: 2   geo_coverage: South Africa   geo_granularity: police-station
unit_of_record: aggregate-count   time_start: 1994-ish (station series), 2020-01 in the clean reconstruction
time_latest: 2025-09   cadence: quarterly   lag: ~2-4 months   taxonomy: custom (17 SAPS categories)
formats: ["XLSX","PDF","CSV","GPKG","SHP"]   access: open-download   machine_readable: 2 (raw) / 5 (afrith)
license: unstated (SAPS) / ODC-PDDL-1.0 (afrith)   ingest_difficulty: 3   priority: 5
verification: CITED   checked_on: 2026-09-19
```

### 17. SESNSP incidencia delictiva municipal — Mexico

Landing: `https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva`.
Monthly municipal crime incidence based on **carpetas de investigación** (opened investigation
files), 2015–present, covering **2,486 municipalities**.

**Structure:** one row per year × municipality × crime taxonomy, **wide format with 12 monthly
columns**. Latest verified file `IDM_NM_dic25.csv`: **361 MB, 2,562,994 rows × 21 columns,
Latin-1 encoding**. Four-level taxonomy: **bien jurídico afectado (7) → tipo de delito (40) →
subtipo (55) → modalidad (59)**.

**Access reality, verified 2026-08-13 by an active ingestion project
(`jballesterosc/observatorio-delictivo-mx`):**

| Method | URL | Status |
|---|---|---|
| Official page | `gob.mx/sesnsp/…datos-abiertos…` | JS anti-bot challenge; now links to OneDrive with **non-durable tokens** |
| CKAN API | `https://www.datos.gob.mx/api/3/action/package_show?id=incidencia_delictiva` | **403 Forbidden since 2026-08-13** (worked 2026-07-09) |
| **Direct mirror (working)** | `https://repodatos.atdt.gob.mx/api_update/sesnsp/incidencia_delictiva/IDM_NM_{mmm}{yy}.csv` | **200** — the only reliable path |

Also: `datos.gob.mx` serves an **incomplete TLS certificate chain**, requiring bundled Let's Encrypt
intermediates.

**Quirks that read as a checklist for our own ingestion design:**
1. **Growing taxonomy grid** — rows/year rise from 189,238 (2015–16) to 243,628 (2024–25) as
   municipalities and categories are added. Never assume a constant Cartesian grid.
2. **Retroactive revision** — each monthly cut can alter figures across the **entire 2015–present
   history**. Therefore: snapshot every vintage, never overwrite
   (`data/raw/…/vintage=YYYY-MM-DD/`), and show users which vintage they are looking at.
3. **Dual-date filenames** — `dic25_corte_jun26.csv` encodes *data cutoff* (Dec 2025) and
   *publication edition* (Jun 2026). **These are two different dates and both must be modelled.**
   Our "data is N months old" badge needs the cutoff, not the edition.
4. Encoding alternates between Latin-1 and UTF-8 between vintages.
5. **Cifra negra** — the data is *delito denunciado y registrado*, not crime that occurred. Mexico
   runs ENVIPE as the survey counterpart, exactly as England & Wales runs CSEW.

**Cadence:** intended monthly (~20th for the prior month); in practice automation lags by months.

```
id: mexico-sesnsp-municipal
tier: 2   geo_coverage: Mexico   geo_granularity: city (municipio)   unit_of_record: aggregate-count
time_start: 2015-01   time_latest: 2026 cuts   cadence: monthly   lag: ~1-3 months (official) / months (mirror)
taxonomy: custom 4-level   formats: ["CSV","XLSX","ZIP"]   access: scrape (official page is JS-challenged)
machine_readable: 4   license: unstated/open-government   ingest_difficulty: 3   priority: 4
verification: CITED   checked_on: 2026-09-19
```

### 18. Fogo Cruzado — Brazil (crowdsourced + verified shooting data, geocoded)

A civil-society dataset of **gun-violence occurrences with coordinates**, covering Rio de Janeiro,
Greater Recife and (later) other metros, built from crowdsourced reports plus verification.

**Public API v2, verified in three independent production pipelines** (including the Rio city
government's own data platform, `prefeitura-rio/pipelines_rj_civitas`):

```
POST https://api-service.fogocruzado.org.br/api/v2/auth/login      → bearer token
GET  https://api-service.fogocruzado.org.br/api/v2/states
GET  https://api-service.fogocruzado.org.br/api/v2/occurrences?page={n}   (Authorization: Bearer …)
```

Requires registration for credentials; paginated; returns per-occurrence records with municipality
and geocode, aggregable by município.

**Why it matters to India:** it is the clearest working proof that a **non-state actor can build a
geocoded incident dataset that the state itself then consumes** (the Rio prefecture ingests it into
BigQuery). It is also the clearest demonstration of the risk: a crowdsourced incident feed has
**no denominator, no completeness guarantee, and a reporting bias toward areas with engaged
reporters** — so it can only honestly be presented as "reports we received", never as "shootings
that happened". If we ever accept community reports in India (Safecity-style), that framing must be
hard-coded into the UI, not left to a disclaimer.

```
id: fogo-cruzado
tier: 4   geo_coverage: Rio de Janeiro, Recife, + expanding Brazilian metros
geo_granularity: point   unit_of_record: incident-point   cadence: realtime/daily
formats: ["JSON"]   access: api-key (free registration)   machine_readable: 5
license: unknown (registration ToU)   ingest_difficulty: 2   priority: 3
verification: CITED   checked_on: 2026-09-19
```

### 19. SSP-SP / Brazilian state secretariats

São Paulo's Secretaria de Segurança Pública publishes both aggregate monthly statistics
(`https://www.ssp.sp.gov.br/estatistica/consultas`) and, since ~2016, **detailed boletim de
ocorrência (BO)-level records** for the capital through its transparency portal
(`http://www.ssp.sp.gov.br/transparenciassp/`). The R package `brcrimR` exists precisely because
"muitas Secretarias de Segurança disponibilizam as informações filtradas por mês ou localidade" —
each state publishes separately, filtered by month or locality, behind a paginated form, so the
package's whole purpose is "iterar por essas páginas".

**This is the closest structural analogue to India that exists**: a federal country where public
security is a state subject, every state publishes differently, some publish at incident level and
most publish monthly aggregates behind a search form, and the only way to get a national picture is
per-state scraping plus harmonisation. **Whatever Brazil had to build, we will have to build.**

```
id: brazil-ssp-sp
tier: 2   geo_coverage: São Paulo state (+ pattern for all BR states)   geo_granularity: city / police-district
unit_of_record: fir-record (BO) for capital; aggregate-count otherwise   cadence: monthly
formats: ["HTML","CSV","XLSX"]   access: scrape   machine_readable: 2   license: unstated
ingest_difficulty: 4   priority: 3   verification: CITED   checked_on: 2026-09-19
```

### 20. Colombia — Policía Nacional estadística delictiva

`https://www.policia.gov.co/estadistica-delictiva` plus the national open-data portal
`https://www.datos.gov.co` (Socrata), with population denominators from DANE
(`https://www.dane.gov.co`). Granularity is **departamento → municipio**; at least one public map
product (`miguelF21/Mapa-de-Criminalidad-en-Colombia`) renders department → municipality drill-down
with per-crime breakdowns from these sources. Some city datasets (Bogotá) carry UPZ/localidad
granularity.

```
id: colombia-policia-estadistica-delictiva
tier: 2   geo_coverage: Colombia   geo_granularity: city (municipio)   unit_of_record: aggregate-count
cadence: monthly   formats: ["XLSX","CSV","JSON"]   access: open-download   machine_readable: 3
license: unstated   ingest_difficulty: 3   priority: 2   verification: CITED   checked_on: 2026-09-19
```

### 21–24. European national crime data (Netherlands, Denmark, Estonia, + Sweden/Germany/Finland)

From a fetched multi-country source catalogue (`soreavis/property-deep-dive`). **URLs are the
publishers' landing pages, not verified dataset endpoints.**

| Country | Statistical office | Police portal | Granularity |
|---|---|---|---|
| **Netherlands** | CBS StatLine (`https://www.cbs.nl/`) | `https://politie.nl/` — *maandcijfers per gemeente* | **per gemeente + buurt (neighbourhood) level for major cities** |
| **Denmark** | DST Kriminalitet (`https://www.dst.dk/da/Statistik/emner/sociale-forhold/kriminalitet`) | `https://politi.dk/` | **per kommune + sogn (parish)** |
| **Estonia** | Statistikaamet (`https://stat.ee/en/find-statistics/statistics-theme/well-being/security`) | PPA (`https://www.politsei.ee/en`); Ministry of Justice `https://www.just.ee/` annual crime overview | per maakond (county) + Tallinn district level |
| Sweden | Brå (`https://www.bra.se/statistik.html`) | `https://polisen.se/` monthly local reports | per kommun + neighbourhood in major cities |
| Germany | BKA PKS | Länder LKA reports; Berlin Sicherheitsatlas, München Sicherheitsbericht | per Bundesland + city |
| Finland | Tilastokeskus (`https://stat.fi/til/rpk/index.html`) | `https://poliisi.fi/` | per kunta, quarterly |

**The European pattern, and it is the important finding:** the mainstream European model is **not**
a point map. It is **municipality-level counts, published monthly or quarterly by the statistical
office, with a neighbourhood tier only in the largest cities**. The Netherlands' *buurt* and
Denmark's *sogn* are the fine tier, and they exist because those countries maintain small-area
statistical geographies with population registers — the same precondition as LSOA.

**police.uk is the outlier in Europe, not the norm.** A reasonable Indian product that stops at
district-and-sometimes-finer is not a compromised version of the European standard; it *is* the
European standard, delivered at India's data maturity.

Also noted for comparison: **Singapore** (SPF Annual Crime Brief; national + 7 land divisions +
**Neighbourhood Police Centre catchments**, with interactive hot-spot maps and very low
under-reporting) — the NPC catchment is structurally the same idea as the police-station tier.

```
ids: netherlands-cbs-politie · denmark-dst-politi · estonia-stat-ppa
tier: 1   geo_granularity: city (gemeente/kommune) + ward (buurt/sogn) in cities
unit_of_record: aggregate-count   cadence: monthly/quarterly   formats: ["CSV","JSON","HTML"]
access: open-download   machine_readable: 4   license: unknown/open-government
ingest_difficulty: 3   priority: 2   verification: CITED   checked_on: 2026-09-19
```

## Granularity reality check

What the benchmarks actually achieve, and the honest gap to India:

| Country / product | Finest published unit | Unit of record | Cadence | Lag | Anonymisation | Denominator |
|---|---|---|---|---|---|---|
| UK police.uk | snapped point (≥8 addresses) + LSOA | incident | monthly | 1–2 mo | **snap-to-master-list + 20 km zeroing** | LSOA mid-year estimates |
| US cities | point / block address | incident | **daily** | 1–14 d | block truncation, per-city, inconsistent | ACS tract |
| US FBI CDE/NIBRS | agency / state | incident | annual + quarterly | 6–12 mo | aggregation | census |
| **South Africa SAPS** | **police station** | aggregate count | **quarterly** | 2–4 mo | **aggregation only** | **Census 2022 per precinct** |
| Mexico SESNSP | municipality | aggregate count | monthly | 1–3 mo | aggregation only | INEGI |
| Brazil SSP-SP | BO-level (capital) / city | mixed | monthly | 1–2 mo | partial | IBGE |
| Colombia | municipality | aggregate count | monthly | ~1 mo | aggregation only | DANE |
| NL / DK / SE | gemeente/kommune + buurt/sogn | aggregate count | monthly/quarterly | 1–3 mo | aggregation only | population register |
| **India — available now** | **district** | **aggregate count** | **annual** | **12–24 mo** | aggregation only | **Census 2011** |
| **India — winnable** | **police station** | aggregate count | monthly/quarterly | 1–6 mo | aggregation only | **none exists at that unit** |
| **India — a few cities** | city / commissionerate | aggregate count | monthly | 1–3 mo | aggregation only | Census 2011 city totals |
| **India — never** | ~~point~~ | ~~incident~~ | — | — | — | — |

**The blunt version.** We want what police.uk has and we will not get it. We want monthly and we have
annual. We want 2026 population and we have 2011. The single gap that matters most is not the crime
data at all — **it is that India has no published population denominator at police-station level**,
so even after we win station-level counts by RTI we can publish *counts* but not *rates*, and counts
without rates are how you defame a dense neighbourhood. Closing that gap (areal interpolation from
census villages/wards onto station polygons) is a named Phase 2 workstream.

## Synthesis — what India's version can be

### A. Tiered product model

**Tier 1 — National / State / District. Ships in v1. Source: NCRB.**
Choropleth by district, rate per 100,000, category filter, 5-year trend. Annual cadence, 12–24 month
lag. Every number carries the principal-offence-rule caveat and the IPC→BNS discontinuity marker.
This tier is boring, defensible, and nationally complete — which is exactly why it is v1.

**Tier 2 — City / commissionerate. Ships where it exists.**
A handful of state police and city commissionerates publish monthly or annual counts. Present as a
city page, not a map layer, until the boundary set is complete. Ward-level exists for almost nowhere
and must not be faked by splitting city totals across wards by population.

**Tier 3 — Police station. The prize. Won, not found.**
This is the SAPS tier. Obtained by (a) RTI to each state DGP/SP office for per-station per-month
per-head FIR counts, (b) scraping state FIR-search portals where they exist, (c) ICJS/CCTNS
aggregate extracts where a state will share them. Publish **counts + rank within district**, and a
**rate only where a defensible denominator has been constructed and its method published**.
*Requires the police-station boundary layer to exist first — coordinate with `geospatial-boundaries`.*

**Tier 4 — Point / address. Never.**
Not "not yet". Never, for FIR-derived data. Three independent reasons, any one sufficient:
1. **No infrastructure.** There is no open Indian address-point register, so there is no way to build
   a snap-point list with a provable k≥8 guarantee. Publishing an unsnapped FIR location publishes
   the complainant's location.
2. **The source data is already over-exposed.** Several Indian FIR portals publish FIR PDFs
   containing complainant and accused names and addresses. Geocoding and mapping those would
   aggregate a diffuse existing exposure into a searchable one — a qualitatively new harm.
3. **Legal.** Identity disclosure for victims of sexual offences is criminal (BNS s.72, formerly IPC
   s.228A; POCSO s.23), and DPDP 2023 obligations attach to the processing. *Detail belongs to
   `legal-ethics`; the product rule is: point maps are out of scope for v1 through vN.*

**Additional hard exclusions, at every tier:**
- No caste, religion or community breakdown of crime by locality. Ever. This is the single fastest
  route from "public information" to "communal targeting", and it is also a redlining vector.
- No composite "safety score" for a locality, and no score at all for an address.
- No accused names, no complainant names, no FIR numbers rendered as links to identifying documents.
- No calls-for-service or ERSS-112 call volumes presented as crime — those measure *calling*, not
  crime, and India's 112 usage varies by an order of magnitude between states.
- No rendering of a cell whose count is below threshold (see D1).

### B. Proposed API and data schema

Borrow police.uk's field names where they fit, because a proven vocabulary is free, and change the
names where the meaning differs — **especially the unit of record**.

The fundamental schema difference, and it should be impossible to miss: **police.uk's record is a
crime; ours is an area-month-category count.** Encode that in the type names so that no downstream
consumer can accidentally treat our rows as incidents.

```
Base: https://api.<our-domain>/v1
Auth: none for read. Rate limit: leaky bucket, 15 req/s, burst 30  (copied from police.uk)
Licence: CC-BY-4.0 on our derived data; upstream terms (GODL-India etc.) declared per record
```

```
GET /v1/crime-categories?date=YYYY-MM       our harmonised categories valid for that period
GET /v1/taxonomies                           IPC / BNS / NCRB-head crosswalks, versioned
GET /v1/areas?level=state|district|city|police-station
GET /v1/areas/{area_code}                    area detail incl. denominator + its vintage
GET /v1/areas/{area_code}/boundary           GeoJSON polygon
GET /v1/locate-area?q={lat},{lng}&level=…    reverse lookup   (police.uk /locate-neighbourhood)
GET /v1/crime-counts?area={code}&date=YYYY-MM[&category=]       THE core endpoint
GET /v1/crime-counts-dates                   availability per area per level  (police.uk /crimes-street-dates)
GET /v1/last-updated                         (police.uk /crime-last-updated)
GET /v1/outcomes?area={code}&date=YYYY       charge-sheeting / conviction  (police.uk outcomes)
GET /v1/survey-prevalence?area={code}        NFHS-derived reporting gap, where available
GET /v1/sources/{source_id}                  provenance record
```

**Core record — `crime-count`:**

```jsonc
{
  "area_code":        "IN-MH-PUNE",        // stable; never reused after reorganisation
  "area_name":        "Pune",
  "area_level":       "district",          // national|state|district|city|police-station
  "falls_within":     "IN-MH",             // police.uk's "Falls within" — the reporting authority
  "reported_by":      "Maharashtra Police",// police.uk's "Reported by"
  "month":            "2023-07",           // null when the source is annual
  "year":             2023,
  "period_type":      "annual",            // annual|quarterly|monthly — never inferred
  "category":         "theft",             // our harmonised category
  "category_source":  "NCRB-head:Theft (IPC 379-382)",
  "taxonomy":         "IPC",               // IPC|BNS|IPC+SLL|NCRB-heads
  "count":            1423,
  "count_suppressed": false,               // true ⇒ count is null, below threshold
  "rate_per_100k":    98.4,                // null unless denominator_confidence >= "medium"
  "denominator":      1446000,
  "denominator_source": "Census 2011, projected",
  "denominator_year": 2011,                // SHOWN IN THE UI. Always.
  "last_outcome":     { "chargesheeting_rate": 0.41, "conviction_rate": 0.19, "year": 2023 },
  "source_id":        "ncrb-crime-in-india-2023",
  "source_tier":      1,
  "source_url":       "https://…",
  "data_cutoff":      "2023-12-31",        // SESNSP lesson: cutoff ≠ edition
  "published_on":     "2025-02-11",
  "vintage":          "2025-02-11",        // which release of the series this row came from
  "confidence":       "medium",            // high|medium|low — see D8
  "caveats":          ["principal-offence-rule", "denominator-2011", "bns-transition-break"]
}
```

**Deliberate design choices:**
- `count_suppressed` is a field, not an absence. A suppressed cell is *data*, and hiding the fact of
  suppression is itself a lie.
- `rate_per_100k` is **null by default** and only populated when the denominator clears a confidence
  bar. It is easier to refuse to divide than to explain a bad division.
- `vintage` + `data_cutoff` + `published_on` are three separate dates because Mexico proved they are.
- `caveats[]` is machine-readable and rendered in the UI, not buried in a methodology page.
- Ship a **bulk download** (one CSV per year per level, plus GeoJSON boundaries) from launch day.
  police.uk's API lacking LSOA codes pushed every serious user to the CSV; don't repeat that split.
- Version the taxonomy crosswalk and serve it over the API, CODE-style. The IPC→BNS mapping is the
  single most contested artefact we will produce and it must be publicly auditable.

### C. The honesty layer — concrete UI rules

These are the acceptance criteria, not aspirations. **A build that violates any of these does not ship.**

1. **Minimum-count suppression.** At district level and finer, any cell with count `< 5` renders as
   `<5`, never as a number and never as a map colour. At police-station level the threshold is
   `< 10`. Suppression is shown as a distinct hatched fill with the legend entry "too few to
   publish", not as "0" and not as grey-for-missing.
2. **No rate without a denominator.** Never render a rate where the denominator population is
   `< 5,000` or where `denominator_confidence` is low. Show the count and say why there is no rate.
3. **Never colour a choropleth by raw count.** Count maps are population maps. Rate per 100,000 only,
   with the denominator year printed in the legend: *"per 100,000 — Census 2011 population"*.
4. **Age badge on every number.** `Jan 2024 data · 21 months old`, computed from `data_cutoff`, not
   from `published_on`. Amber past 18 months, red past 36.
5. **Provenance chip on every number.** `NCRB` / `State portal` / `RTI response` / `Scraped`, each
   linking to the `/v1/sources/{id}` record and the original file.
6. **"Reported crime ≠ crime" is permanent furniture,** not a dismissible modal. It sits in the map
   legend. Where an NFHS-derived reporting-gap figure exists for that crime type, state it
   numerically in place of the generic sentence — *"NFHS: X% of women who experienced physical
   violence sought help from police"* beats any amount of prose.
7. **Mark the BNS break.** Any series crossing 1 July 2024 renders a vertical discontinuity rule and
   refuses to draw a connecting line or a percentage change across it. Year-on-year deltas spanning
   the break are not computed, not greyed out — **not computed**.
8. **A visible three-state confidence chip** (High / Medium / Low), derived from
   `source_tier × granularity × recency × denominator quality`, rendered next to the number, never
   in a hover tooltip. Hover is not disclosure.
9. **Search snaps to area.** No address search, no lat/lng input that returns a "your location"
   score. Typing an address returns the district (or station) that contains it, with the area's
   figures and an explicit "this is a <district> figure, not a figure about this address."
10. **A "how this map can mislead you" page**, linked from every view, written in the first person
    and listing our own failure modes: reporting propensity varies by police station and that varies
    by how well the station treats complainants; a district with more women reporting may look worse
    and be better; low counts can mean low crime or a refusal to register FIRs; 2011 denominators
    understate growing cities and overstate shrinking ones.
11. **Rank, don't score.** Where comparison is wanted, use a percentile within state ("higher than
    68% of Maharashtra districts") rather than a grade or an absolute risk number. Percentiles carry
    their own uncertainty more gracefully than an A–F grade, and cannot be lifted into an insurance
    premium as cleanly.
12. **Publish the suppression and harmonisation rules as part of the product,** not in a PDF. If a
    user cannot audit why a cell is blank, the blank looks like concealment.

### D. Recommended v1 scope

**Build this:**
1. **All-India district choropleth from NCRB**, ~2018 → latest published year, rate per 100,000,
   filterable by a harmonised category set of roughly 10–14 heads (police.uk's 14 is a good target
   count — enough to be useful, few enough to be defensible), with district-reorganisation crosswalk.
2. **A district page** per district: counts, rates, 5-year trend with the BNS break marked,
   charge-sheeting and conviction rate as the outcomes layer, source provenance, and the full
   caveat list rendered inline.
3. **The honesty layer in full** (all 12 rules above). This is not a v2 polish item; it is the
   product's reason to exist and it is cheap to build early and expensive to retrofit.
4. **One police-station pilot in one state** that already publishes or will release station-level
   counts — end-to-end: ingestion, station boundary layer, suppression, a published denominator
   method, and a page. One state proving the pipeline is worth more than 36 states of district data
   we already have. It also produces the RTI template for the other 35.
5. **The NFHS reporting-gap layer** for crimes against women, at district level, displayed as a
   paired figure wherever a women's-safety category is shown.
6. **Public bulk download + open API + published taxonomy crosswalk** from launch.

**Explicitly not in v1:** point maps; any address-level anything; a composite safety score; ward
layers; real-time or community incident reporting; caste/religion cuts; a mobile app; anything
requiring 36 successful RTI campaigns before it renders.

**The one design decision that determines whether this product helps or harms:**
**the unit of record.** Everything follows from choosing `aggregate-count over a named area with a
published denominator and a suppression threshold` instead of `incident-point`. Choose the
aggregate and the privacy problem, the legal problem, the defamation problem, the small-number
problem and the false-precision problem all shrink to manageable size, and the honest product is
also the cheap product. Choose the point and you must first build a national address register, a
750,000-point snap list, a k-anonymity proof and a legal defence — and, as police.uk's own
experience shows, you will *still* ship phantom hotspots, and a commercial consumer will *still*
relabel your street segments as addresses and sell them to a landlord.

## Blockers and how to get past them

| Blocker | Detail | How to get past it |
|---|---|---|
| **Egress proxy blocked every primary source** | `data.police.uk`, `www.police.uk`, `www.gov.uk`, `www.ons.gov.uk`, `www.saps.gov.za`, `api.usa.gov`, `data.cityofchicago.org`, `arxiv.org`, `web.archive.org` all returned `EGRESS_BLOCKED`; `curl` got `CONNECT tunnel failed, response 403` | Re-run this agent's verification pass from an unrestricted network, or from India. The list of URLs to confirm is in Seed Leads. **Nothing in this dossier should be quoted publicly until that pass is done.** |
| **WebSearch budget exhausted** | 200/200 used before this agent started; no discovery search was possible | Raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, or give the benchmark agent its own session |
| **GitHub MCP repo-scoped** | `get_file_contents` refused all repos except `danish99011/crime-map`; only `search_code` was org-wide | Worked around via `raw.githubusercontent.com` through WebFetch — keep that path for Phase 2 |
| **Official map-point count unconfirmed** | Three third-party figures: 680,000 / ~750,000 / ~760,000 | Read `https://data.police.uk/about/#location-anonymisation` directly and quote it with a date |
| **LSOA numbers unverified** | ONS blocked | Confirm min/mean population, household thresholds, and LSOA counts for 2011 and 2021 |
| **No India police-station denominator** | Counts without rates defame dense areas | Phase 2 workstream: areal interpolation of census village/ward population onto police-station polygons; publish the method |
| **SAPS raw data in hidden Excel sheets** | Presentation artefact with the dataset buried inside | `afrith/unhide-xlsx` is the existing solution; expect the same for NCRB-style publications |

## Seed Leads (unconfirmed but probably real)

1. **`https://data.police.uk/about/` — the authoritative methodology page.** Contains the location-
   anonymisation section (anchor `#location-anonymisation`), the ASB handling rules, the data-source
   list and the licence statement. *Next step: fetch it and quote the map-point count verbatim.*
2. **The police.uk master map-point list itself.** If the ~750,000-point list has ever been
   published (or is obtainable under FOI from the Home Office), it is the single most valuable
   artefact in this whole domain — a worked example of a national k-anonymous snap grid.
   *Next step: FOI request to the Home Office for the map-point dataset and its generation
   specification.*
3. **The ASB blank-Crime-ID rule.** Widely believed, not confirmed in any source I fetched.
   *Next step: download one `{YYYY-MM}-street.csv` and check whether ASB rows have a Crime ID and an
   outcome.*
4. **`https://data.police.uk/docs/api-call-limits/`** — cited by two client libraries; confirm the
   exact leaky-bucket parameters and whether a 429 body carries retry information.
5. **Home Office / ONS methodology on crime-map anonymisation, ~2011.** There was a public debate
   about granularity, ICO involvement, and an explicit decision on the 8-address threshold.
   *Next step: search gov.uk for the Home Office crime-mapping guidance and the ICO's contribution.*
6. **Peer-reviewed work on crime maps and property values.** Certain to exist (UK and US housing
   economics). *Next step: Google Scholar for "crime maps" + "house prices" + police.uk.*
7. **The Conor Gogarty / Bristol Live investigation** into snap-point errors (41 shoplifting offences
   at a shopless location). *Next step: locate the original article for citable detail and the Home
   Office quote in context.*
8. **SAPS crime-stats release schedule and the underlying station-level definition document** —
   what counts as a "community-reported serious crime", and how stations are defined and renamed.
   *Next step: SAPS crimestats.php + the quarterly release PDF's methodology annex.*
9. **Stats SA Police District boundary metadata** — vintage, accuracy, licence.
   `https://www.statssa.gov.za/wp-content/uploads/2025/08/PoliceDistrict.zip` (cited, unverified).
10. **Mexico ENVIPE** (the victimisation survey paired with SESNSP) — the CSEW analogue for Latin
    America, and probably a better methodological template for India than CSEW because it operates in
    a high-`cifra negra` environment. *Next step: INEGI ENVIPE landing page.*
11. **Instituto Sou da Paz** (Brazil) — named in the brief; not reached this session. Likely
    publishes homicide and firearm analyses that pair with SSP-SP administrative data.
12. **Netherlands `buurt`-level crime data as an actual downloadable table** — CBS StatLine has an
    OData API; if buurt-level crime counts are genuinely published, the Netherlands is the best
    European example of a *fine* tier done through aggregation rather than points.
13. **`BSteffaniak/crime-map`** — another crime-map project on GitHub with a `source-discovery` skill
    that references CrimeMapping.com. Worth reading as a peer's source catalogue.
14. **BPR&D "Data on Police Organisations"** — for the authoritative count of police stations in
    India (I used ~17,000 as an unverified figure). Belongs to `mha-parliament` but the number is a
    dependency for our station-tier sizing.

## Phase 2 recommendations

Ranked, with the reason:

1. **Re-verify every police.uk URL and quote in this dossier from an unblocked network.** Half a day.
   Everything downstream — our anonymisation policy, our API design, our category count — rests on
   text I read at one remove. *Highest value per hour of anything in this document.*
2. **Adopt the aggregate-count unit of record formally, in writing, before any UI work.** Make it a
   documented architectural decision with the reasoning from §D. This is the decision that is
   expensive to reverse and easy to erode under feature pressure.
3. **Ingest SAPS as a reference implementation.** Not for the data — for the pipeline. Quarterly
   station-level workbooks → station polygons → census denominators → suppressed, rate-normalised
   tiles is *exactly* the Indian pipeline, and `afrith/crime-stats` (ODC-PDDL, public domain) plus
   `ChelseaH93/sa-gbv-data` give us working code to study. Build ours against SAPS data first, then
   swap the source. **You get to debug the hard part with data that already exists.**
4. **Build the taxonomy crosswalk service early** (IPC → BNS → our harmonised categories), versioned
   and served over the API, CODE-style. It is the most contested artefact we will publish and the
   one most likely to be attacked; make it auditable from day one.
5. **Write the honesty layer as acceptance tests, not as design notes.** Suppression threshold,
   no-rate-without-denominator, no-count-choropleth, BNS-break refusal — each is a unit test that
   fails the build. Rules that live in Figma get negotiated away; rules that live in CI do not.
6. **Start the police-station RTI campaign for one state now**, in parallel with v1 district work,
   because the RTI clock (30 days + first appeal + second appeal) is the long pole. Coordinate with
   `rti-playbook`; the SAPS release format is the concrete "please provide it like this" attachment.
7. **Commission the police-station denominator method** with `geospatial-boundaries`: areal
   interpolation from census villages/wards onto station polygons, with published uncertainty. Until
   this exists, the station tier can publish counts and ranks but no rates.
8. **Mirror everything we ingest, immutably, by vintage.** police.uk appears to have dropped to a
   ~3-year rolling window and SESNSP retroactively revises its entire history. Assume every Indian
   publisher will do both. `vintage=YYYY-MM-DD` snapshots from the first ingest.
9. **Pair with NFHS before launch, not after.** The reporting-gap layer is what separates this from
   a map of policing activity. Coordinate with `civil-society-academic`.
10. **Write the anti-pattern memo** from §12–15 (SpotCrime address scores, CrimeGrade ML gap-filled
    block grades, Citizen's bounty incident, LexisNexis's 364k-record breach) and circulate it
    internally. Every one of these organisations had reasonable people who arrived there one
    feature at a time.
