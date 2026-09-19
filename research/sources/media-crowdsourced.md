# Media, Crowdsourced and Commercial Signal
_Agent: media-crowdsourced · Researched: 2026-09-19 · Entries: 7 verified / 27 total_

> **Tooling caveat, stated up front because it changes how you should read every entry below.**
> This session could reach only `en.wikipedia.org` and `github.com`. Every other domain I needed —
> `safecity.in`, `maps.safecity.in`, `reddotfoundation.org`, `safetipin.com`, `gdeltproject.org`,
> `api.gdeltproject.org`, `mediacloud.org`, `eventregistry.org`, `commoncrawl.org`, `data.gov.in`,
> `play.google.com`, all Indian news domains, all property portals — was refused by this
> environment's egress proxy (`EGRESS_BLOCKED`). The session's WebSearch budget (200/200) was also
> already spent by other agents before my fourth query. `curl` from the sandbox returns nothing.
> So only 7 of 27 entries carry `VERIFIED_*`. I did **not** paper over the gap by asserting
> plausible URLs: where I have no confirmed URL I have omitted the `urls` object entirely and
> said so in `evidence`. Re-verification from an unblocked network is the first Phase 2 task.
>
> What I did instead was mine the two reachable domains hard. GitHub code search turned out to be
> a better instrument than a web search would have been for the question the brief called most
> useful — *what already existed in India and why it died* — because abandoned repos carry
> timestamps, and because a decade of Indian student and hackathon projects have left their
> scrapers, their endpoints and their data-source audits in public. Safecity's undocumented JSON
> API below was recovered that way, from four unrelated repos spanning 2016–2023.

## Executive summary

- **India has no street-level crime map, and the reason is not that nobody tried.** It is that
  every attempt was built on a dataset the builder did not own and could not refresh. The
  canonical corpse is **Code for India's Meri Awaaz / SafeRoute** (173 commits, 4 stars, a README
  whose entire body is `This is my README`) — an Android app, an API server and a website stacked
  on top of a *scraper pointed at Safecity*. When the borrowed source stops, the product stops.
  I found the same pattern in `nyctophiliacme/Route-Planning`, `Sharad117/SafeMaps`,
  `DevanshVarshney/SHEILD`, `Tarun-108/HerWay` and `DNA-Coded/RakshaMarg`. **Nobody died of a
  technical problem. They died of not having a data supply.**
- **Safecity data is obtainable — two ways, and only one of them is legitimate.** Technically,
  `maps.safecity.in/reports/fetch_reports` is an unauthenticated, bbox-filtered, category-filtered,
  paginated JSON endpoint; one scraper iterates 553 pages of it. Legitimately, Red Dot Foundation
  runs a formal data-request process offering aggregated insights, geospatial trends and
  anonymised incident-level data. **Take the second route.** The reports are anonymous survivor
  disclosures under research-only terms; scraping them into a commercial-adjacent public map is
  both a terms breach and a betrayal of the people who wrote them.
- **SafetiPin data is *not* obtainable in bulk, and I can show it rather than assert it.** The one
  public ML project that used SafetiPin data shipped it as `safetipin_165_rows.csv` — 165 rows,
  hand-collected. Their business model is licensing to city governments and multilateral-funded
  projects. What *is* free is their published city audit PDFs.
- **SafetiPin is nonetheless the most valuable thing in this dossier**, because it is the only
  Indian dataset that is genuinely point-level, genuinely about streets, and *structurally
  incapable of defaming anyone*: it scores lighting, openness, visibility, people, security,
  walk path, public transport, gender usage and feeling. Those are properties of public
  infrastructure, not accusations about residents. And because the nine parameters are published,
  **the method is reproducible from OSM + VIIRS night-lights + street imagery if they will not
  license to us.** That is a build-vs-buy decision, not a blocker.
- **GDELT is the wrong shape and I recommend against building on it.** Its CAMEO ontology is a
  political-conflict scheme "focused on inter-state behavior" — there are no codes for theft,
  burglary, robbery, chain-snatching or cheating, i.e. for the volume crime a renter actually
  asks about. Its geocoding resolves to gazetteer place names, so a Bengaluru murder lands on
  "Bengaluru", not on the locality the article named. Its own documented failure modes include
  media-composition drift and regional attention bias. Use the **DOC 2.0 article API** instead if
  we use GDELT at all, and run our own Indian offence classifier over it.
- **News gets us locality names and same-day freshness — for the wrong crimes.** Indian crime
  reporting covers murder, rape, robbery, communal violence and large fraud, and essentially
  ignores the theft, burglary, snatching and cheating that dominate FIR volume. A news layer is
  therefore a *severity-biased* sample: it over-represents the rare and terrible and
  near-zero-represents the common. That is precisely inverted from what a resident needs.
- **English-only is not a smaller pipeline, it is a different one.** ABC circulation (Jul–Dec 2022)
  puts Dainik Bhaskar at 3.57m against Times of India's 1.87m; across the top 20 titles the six
  Hindi papers total ~9.7m versus ~3.7m for the four English ones — before Telugu, Tamil, Marathi,
  Bengali, Malayalam and Kannada are counted at all. English-only over-covers metros and
  under-covers the small-town and rural India where most people and most crime are.
- **Our closest commercial competitors have no crime data at all.** 99acres publishes
  resident-written locality reviews rated on connectivity, lifestyle, **safety** and environment.
  Housing.com, MagicBricks and NoBroker publish comparable opinion ratings. None publishes a
  crime-derived score, because none has crime data. The bar is a star rating from an unknown
  number of self-selected, sometimes broker-affiliated reviewers. That is both an easy bar to
  clear and a mistake we must not copy.
- **Finest granularity genuinely achievable in this domain:** `point` for SafetiPin-style
  environmental audits and for Safecity pins; `ward`/locality-name for a news-derived feed after
  deduplication; nothing finer than `city` for anything automated and unsupervised.
- **The biggest blocker is not access, it is legitimacy.** Every fine-grained source here is
  either unverified, unrepresentative, or someone else's to give. Phase 2's job is partnership
  and method, not scraping.

## Source entries

Full machine-readable records are in `media-crowdsourced.jsonl` (27 lines). The narrative below
covers what the fields cannot carry. Entry ids are given for cross-reference.

### 1. Safecity — crowdsourced harassment map (`media-crowdsourced-safecity`)

Red Dot Foundation, Mumbai. Launched December 2012 by ElsaMarie D'Silva, Surya Velamuri, Aditya
Kapoor and Saloni Malhotra after the 2012 Delhi gang rape. India plus Kenya, Cameroon, Nepal and
Malaysia; Indian density is in Delhi, Mumbai, Pune, Patna and Ahmedabad.

The endpoints, recovered from source code rather than documentation:

```
http://maps.safecity.in/reports                      # public report list
http://maps.safecity.in/reports/fetch_reports        # JSON; params sw, ne (lng,lat bbox), z, c[n], page
http://maps.safecity.in/reports/view/<id>            # single report (id 11679 existed in 2019)
http://maps.safecity.in/api?task=<task>              # base used by an unofficial Android client
https://maps.safecity.in/main                        # the map itself
```

**Volume is the finding that matters.** Reported counts are ~6,000 (2015), ~10,000 (2018),
~25,000 (2021) per Wikipedia, "22,000+" on Red Dot's own site, and "100k+" in one third-party
repo — the disagreement is itself a caveat. Take 25,000 over 13 years across five countries:
roughly **five reports a day, globally**. For comparison, police.uk publishes on the order of five
to six million street-level crimes a year for England and Wales. Safecity's entire lifetime corpus
is a rounding error against a single month of the product we are imitating. It is a qualitative
layer and a potential partner. **It is not a denominator and it cannot carry a map.**

### 2. SafetiPin — safety audits (`media-crowdsourced-safetipin-audit-data`, `-city-reports`)

Founded 2013 by Kalpana Viswanath and Ashish Basu. Three apps: My SafetiPin (crowdsourced),
SafetiPin Nite (car-mounted night-time camera audits along road networks), SafetiPin Site
(professional audits). Nine parameters: lighting, openness, visibility, people, security guards,
walk path, public transport, gender usage, feeling. 20+ cities; Delhi NCR since 2013, plus Mumbai,
Bengaluru, Kolkata, and internationally Bogotá (230 km of bike paths, 2016), Nairobi, Hanoi.
Documented government use: Delhi (streetlight installation, patrolling), Bogotá (lighting, CCTV
siting).

Two confirmed-by-citation public PDFs, from another project's source-audit file:

```
https://safetipin.com/wp-content/uploads/2021/04/social-vulnerability-audit-report-in-kolkata-safetipin-2021.pdf
https://safetipin.com/wp-content/uploads/2021/04/james-long-sarani-a-pilot-design-report-safetipin-2021.pdf
```

Note the methodological bias that follows from *how* SafetiPin Nite collects: a camera on a car
covers drivable roads. Lanes, footpaths and informal settlements are systematically
under-audited — and those are exactly the places where lighting is worst.

### 3. Government citizen apps (entries 5–9)

**Himmat** (Delhi Police, launched 1 January 2015 by Rajnath Singh) is the instructive one: a
Parliamentary panel found it ineffective in 2018 due to "low registrations and other problems".
**Disha** (AP), **112/ERSS**, **Citizen COP** and **Raksha** round out the set. The pattern across
all five is identical and worth stating plainly: **the Indian state has built at least half a
dozen citizen safety apps and published operational data from none of them.** There is no
dashboard, no open dataset, no aggregate release at any geography for any of them.

They are still worth one RTI batch, because one statistic would be genuinely novel and is
answerable at an aggregate level that no authority can refuse on privacy grounds: **how many SOS
alerts convert into a registered FIR.** Ask for counts by district and by month, never for points.

### 4. Meri Awaaz / Code for India (`media-crowdsourced-meriawaaz-code-for-india`)

See the executive summary. Four stars, seven forks, 173 commits, a placeholder README, and a
`pythonapiserver/saferoute/scraper/scraper.py` pointed at safecity.in. This is the single most
useful artefact I found, because it is an autopsy rather than an opinion.

### 5. News-as-data (entries 13–19)

GDELT Event DB, GDELT DOC 2.0 API, Media Cloud, Event Registry, Common Crawl, Indian
English-language outlet archives, and the vernacular press. The per-source caveats are in the
JSONL. Three cross-cutting points:

- **Deduplication is the whole game.** One Indian incident appears across 5–15 outlets plus
  syndicated wire copy. Count clusters, never articles. Event Registry sells clustering; evaluate
  it as a dedup service rather than as a source.
- **Allegation, not offence.** Indian crime reporting is overwhelmingly at the FIR stage. A large
  fraction of FIRs are later closed, reclassified or found false, and outlets almost never publish
  the correction. Every news-derived record needs a status field and must default to "reported".
- **Copyright discipline.** Headline + URL + date + extracted locality, with attribution and a
  link. Never store or re-serve article body text. Use Google News sitemaps as the discovery
  surface — most Indian outlets publish them, and they are the cleanest legal route.

### 6. Commercial / real-estate (entries 22–24)

99acres' four-parameter locality rating (connectivity, lifestyle, **safety**, environment) is the
competitor surface. `soodoku/vaastu_tax` is a research scrape of 99acres, MagicBricks and
Housing.com with a Dataverse deposit containing `housingcom_listings.parquet` (columns include
`rating_overall` "Overall locality rating", `rating_connectivity`) plus raw HTML tarballs — the
only bulk route I found to Indian portal locality ratings without scraping them ourselves.

Their **locality polygons** are worth more to us than their ratings: they encode how Indian users
actually name the areas they search for, which our geocoder has to match.

### 7. Traps (entries 26–27)

**Routify** blends district-level NCRB annual counts with street-level OSM attributes and emits a
0–100 route safety score. That is an unjustifiable resolution upgrade and precisely the error we
must not make. Read it before designing our scoring.

**The ~40k-row "Crime Dataset India 2020–2024" circulating on Kaggle** is, I believe, synthetic —
no Indian authority publishes per-incident FIR records with city, date and crime description
nationally, so a 40,000-row national incident file cannot have official provenance. **I could not
reach Kaggle to confirm this**, so treat it as a strong prior requiring verification, not as
established fact. It is already embedded in dozens of public GitHub dashboards presented as real
Indian crime data. Verify it first thing in Phase 2 and, if confirmed, blacklist its fingerprint.

## Granularity reality check

| Layer | Geographic level actually available | Period | Refresh | Honest verdict |
|---|---|---|---|---|
| SafetiPin audits | `point` (road segments, 9 params) | 2013→campaign-dependent | one-off per campaign | **The only true street-level Indian data. Not crime. Licensed, not open.** |
| SafetiPin city PDFs | `ward` (aggregated, maps as images) | 2021 for the two confirmed | one-off | Free. Underlying points not in the PDF. |
| Safecity pins | `point` | 2012→live | minutes–days | Point-level but ~5 reports/day globally. Volume, not geography, is the limit. |
| News (English) | `ward`/locality *name*, needs geocoding | ~2000→live | hours | Locality names yes; addresses almost never. Severity-biased. |
| News (vernacular) | `ward`, often finer | varies→live | hours | Best sub-district coverage in India. Needs OCR + IndicTrans2. Not started. |
| GDELT events | `city` (gazetteer place name) | 1979→live | daily/15-min | No street. No volume-crime codes. Wrong ontology. |
| 112 / Himmat / Disha | `point` internally | 2015/2018→live | realtime | **Published at no geography whatsoever.** RTI for district aggregates only. |
| Property portal ratings | `ward` (proprietary polygons) | unknown→live | irregular | Opinion, no methodology, no sample size. |
| Reddit / WhatsApp / RWA | `city` / `address` | →live | minutes | Unusable (Reddit) or off-limits (WhatsApp). |

**The gap, stated bluntly:** we want police-station-or-finer, monthly, all-India, all offence
types. This domain can supply point-level *environmental* data for a handful of cities under
licence, locality-named *allegations* for severe crimes at same-day freshness, and nothing else.
No combination of the sources in this dossier produces a defensible neighbourhood crime rate.
They produce context around one. Build accordingly.

## Critical analysis

### 1. Value — what this layer can and cannot honestly deliver

**Can:** same-day freshness; locality-level naming; point-level *environmental* safety (lighting,
openness, walkability) which is what actually drives whether a street feels safe at 10pm; a
qualitative layer of lived experience that no official statistic carries; and a national
early-warning tripwire for large violent incidents.

**Cannot:** counts, rates, trends, or comparisons between areas. Not for any crime type.

The crime types where a news/crowdsourced layer has real recall are homicide, rape and sexual
assault, robbery and chain-snatching, communal and mob violence, road-rage assault, and large
fraud. The crime types a renter asks about — house burglary while away, two-wheeler theft, phone
snatching, package theft, harassment on the walk from the metro — are either unreported to police,
unreported by press, or both. **The severity bias means the layer is most confident exactly where
it matters least for a tenancy decision, and silent where it matters most.**

The single highest-value realistic deliverable from this domain is therefore *not* a crime layer
at all. It is a **SafetiPin-style night-walkability layer**, either licensed or reconstructed from
OSM + VIIRS + street imagery, presented as what it is: an infrastructure score, not a crime score.
It answers "is this street lit and overlooked?" — a large part of the real question — without
making a single claim about any person.

### 2. The bias trap — crowdsourced reports measure who reports

A crowdsourced count is `incidence × propensity_to_report`, and we only ever observe the product.
Propensity varies with smartphone ownership, English literacy, awareness that the platform exists,
trust that reporting is safe, and — decisively — whether an NGO ran a workshop on that street.
Safecity's Indian density in Delhi, Mumbai, Pune, Patna and Ahmedabad is not a finding about
Indian crime. **It is a map of Red Dot Foundation's programme footprint.**

The failure is worse than noise, because it is *signed*. Affluent, English-speaking,
smartphone-owning, well-policed areas generate more reports and look more dangerous. Areas with
the worst under-reporting — where women do not report because reporting is not safe — render as
clean. **A naive crowdsourced map inverts the truth and then publishes it with a colour ramp.**
This is the same artefact that makes Kerala and Delhi look high-crime in NCRB tables: they are
places where registration actually happens.

**How police.uk avoids this — and the answer is structural, not statistical.** police.uk is not
crowdsourced in any part. Every record is a police-recorded crime entering through a single
national counting standard, geocoded not to the real address but *snapped* to the nearest of a
fixed national set of anonymised map points, and suppressed where counts are too low. Crucially,
the UK publishes the **Crime Survey for England and Wales alongside it**, because recorded crime
is known to be reporting-dependent; and the UK statistics authority has removed the National
Statistics designation from police recorded crime for many offence types for exactly that reason,
directing users to the survey for trends. The lesson is not "police.uk normalises cleverly". It is
**"police.uk never asks the public for the counts, and it ships an independent probability survey
next to the administrative data so users can see the gap."**

What we would have to do, concretely:

1. **Never publish a crowdsourced count as a rate, and never rank areas by one.** No league tables,
   no "most dangerous neighbourhoods", ever.
2. **Show crowdsourced reports as reports.** Label the layer "people have reported N incidents
   here", with "this is not a crime rate" as visible product copy, not a footnote.
3. **Ship a denominator or refuse the comparison.** Where we cannot estimate reporting propensity,
   the correct product decision is to withhold the comparison rather than publish a misleading one.
4. **Calibrate against probability samples.** NFHS-5 carries district-level prevalence for
   spousal and sexual violence; NCRB carries district FIR counts. The ratio of reported to
   estimated is itself the most honest thing we could publish, and nobody in India publishes it.
5. **Publish the footprint.** Show *where reporting activity exists* as an explicit coverage layer,
   so a blank area reads as "no data" rather than "safe".

### 3. The harm trap — an unverified pin is a published accusation

**Legal exposure in India is materially worse than in the UK or US.** Defamation is a *criminal*
offence in India, not merely a tort — historically IPC ss.499–500, carried into the BNS at s.356
(confirm the section with counsel; the BNS/BNSS/BSA came into force 1 July 2024 and section
numbering has moved). Liability can attach to the publisher of a third party's statement.
Intermediary safe harbour under IT Act s.79 requires due diligence under the IT Rules 2021 and is
forfeited on failure to act on a valid complaint — and a curated, editorially-ranked, scored map
is on any honest reading **not a neutral intermediary at all**.

Two India-specific hazards that are easy to miss and severe:

- **Victim identification in sexual-offence cases is itself a criminal offence** (IPC 228A →
  BNS s.72), as is publication in breach of the POCSO Act's identity provisions. A news report
  that names a locality plus a map pin that fixes the street can *jointly* identify a victim even
  though neither does alone. Our aggregation is not merely a courtesy here; it is compliance.
- **Communal inference.** A cluster of pins in a minority-majority locality will be read as a
  claim about that community, and can expose us to action under the BNS provisions on promoting
  enmity and on statements conducing to public mischief — quite apart from the real-world harm.

Note also that a *locality* cannot sue, but identifiable individuals within a report can, and
RWAs, builders and portals with a commercial interest in an area's reputation will find a
plaintiff. The practical risk is less a defamation verdict than a takedown-and-blocking order
plus the cost of defending it.

**Concrete design mitigations — these are product requirements, not aspirations:**

1. **Two-track rendering, enforced in code.** Verified records (police/court provenance) may render
   at fine geography. **Unverified records — news and crowdsourced — never render as a point and
   never below a fixed aggregation unit** (ward, or a 1 km grid cell). Make this a hard constraint
   in the rendering layer, not a policy document.
2. **Minimum-count suppression.** Suppress any cell below k (use k ≥ 5), and additionally suppress
   any cell where a single report would change the displayed band. Snap-point geocoding, never raw
   coordinates, for anything person-linked.
3. **No composite locality "safety score" from unverified reports.** Score only the *environment*
   — lighting, openness, walkability — which is a property of public infrastructure and cannot
   defame a resident.
4. **Deduplicate before counting.** Cluster on (date, locality, offence, victim descriptor) and
   count clusters. Undeduplicated news counts inflate by roughly 3–10×.
5. **Provenance and status on every item.** Source outlet, URL, publication date, and an explicit
   `allegation | charged | convicted | closed` field. Default label "reported", never "crime".
6. **Strip identifiers at ingestion** — names, vehicle registrations, house numbers, employer,
   caste and community descriptors — before anything is stored, not before it is displayed.
7. **A standing do-not-map list**: sexual-offence and POCSO matters at any geography finer than
   district; anything naming a minor; anything where the report itself identifies the victim.
8. **Right of reply and notice-and-action.** A published, time-bound takedown process with a named
   contact, a public log of actions taken, and automatic de-publication of any item whose source
   URL 404s or is retracted.
9. **Decay.** Expire unverified reports after a defined window (12–24 months). A single 2019
   incident must not brand a street permanently.
10. **Counsel reviews the rendering rules, not the items.** Get sign-off on the aggregation
    thresholds, the status taxonomy and the takedown process once — then the pipeline is
    defensible at volume.

## Blockers and how to get past them

| Blocker | Nature | Route through |
|---|---|---|
| This session's egress proxy blocked ~15 needed domains; WebSearch budget exhausted at 200/200 | Tooling, not source | Re-run verification from an unblocked network. Affects 20 of 27 entries. **First Phase 2 task.** |
| Safecity terms: research-only, permission required | Legal + ethical | Formal request to Red Dot Foundation. Do not scrape `fetch_reports`. |
| SafetiPin raw data is a licensed commercial asset | Commercial | Partnership; or RTI to a *commissioning city government* for the audit deliverable it holds; or reconstruct the published 9-parameter rubric from OSM + VIIRS + imagery. |
| No Indian police app publishes anything | Institutional | RTI batch for district-level monthly aggregates + alert-to-FIR conversion. Expect partial refusal; budget for first appeals. |
| Vernacular press is e-paper page images | Technical | OCR in Devanagari/Telugu/Tamil/Bengali + IndicTrans2 (AI4Bharat, open, 22 languages). Non-trivial; scope as its own workstream. |
| News copyright and outlet ToS | Legal | Headline + URL + date + locality only. Google News sitemaps for discovery. Licence talks with The Hindu and Indian Express, both of which have licensed archives before. |
| Locality-name geocoding (Gurgaon/Gurugram, and far worse below city level) | Technical | Build an Indian locality gazetteer with alias handling early. Property-portal locality polygons are a good seed for how users actually name places. |

## Seed Leads (unconfirmed but probably real)

1. **Red Dot Foundation data-request process** — `reddotfoundation.org/data` is described in search
   results as offering aggregated insights, geospatial trends and anonymised incident-level data
   under formal review. *Next step:* fetch that page, then a written request to ElsaMarie D'Silva
   stating public-interest use, aggregation thresholds and attribution.
2. **SafetiPin's full published-report set** — the two confirmed PDFs sit under
   `safetipin.com/wp-content/uploads/2021/04/`. *Next step:* crawl that uploads directory and the
   site's reports index for every city audit; these are free and are the cheapest possible read on
   their method before any licensing conversation.
3. **A city government holding a SafetiPin deliverable** — Delhi, Kolkata, Bhubaneswar, Mumbai,
   Bengaluru are the known candidates. *Next step:* identify the commissioning department for one
   of them and file an RTI for the audit dataset supplied under contract. A dataset held by a
   public authority is a public record even where the vendor's own copy is not. **This is the most
   likely route to point-level Indian street-safety data that exists, and nobody appears to have
   tried it.**
4. **CMAPS (Crime Mapping, Analytics and Predictive System), Delhi Police** — believed to be a
   real Delhi Police/ISRO crime-mapping system, internal and never public. I could **not** confirm
   it this session (no Wikipedia article; search unavailable). *Next step:* search Delhi Police
   annual reports and ISRO/NRSC project listings for the acronym, then RTI to Delhi Police for the
   system's data dictionary and the geography at which it holds records — establishing that
   police-station-or-finer geocoded data *exists* is worth far more than obtaining it.
5. **Telangana / Cyberabad "Hawk Eye" citizen app** — believed real and among the more actively
   used state police apps. Unconfirmed this session. *Next step:* verify, then include in the RTI
   batch.
6. **ERSS/112 state nodal officers** — *Next step:* MHA Police Modernisation Division for the list
   of state ERSS nodal officers, then a single RTI template to all of them.
7. **The Kaggle 40k "Crime Dataset India 2020–2024" provenance** — *Next step:* open the dataset
   card, look for a named source. If none, blacklist the fingerprint. **Do this before anyone on
   the team finds it and assumes it is real.**
8. **`soodoku/vaastu_tax` Dataverse DOI** — the repo's `export_dataverse.py` describes the deposit
   but I did not recover the DOI. *Next step:* read the repo README or email Gaurav Sood.

## Phase 2 recommendations

Ranked by value per unit of effort and risk.

1. **Re-verify this dossier from an unblocked network.** 20 of 27 entries are `CITED`/`UNVERIFIED`
   purely because of this environment. Cheap, and everything else depends on it.
2. **Open a partnership conversation with SafetiPin.** Highest-value data in the domain,
   point-level, defamation-safe, and already trusted by city governments. Pull their public city
   PDFs first so the conversation starts informed. **Do this before building any safety scoring.**
3. **Open a data-request conversation with Red Dot Foundation / Safecity.** Lower data value, high
   credibility value, and they have institutional knowledge about the bias trap that we would
   otherwise have to learn by publishing something harmful.
4. **Prototype the environmental layer ourselves, in one city, from OSM + VIIRS night-lights.**
   Reproduces most of SafetiPin's published rubric, costs nothing, carries no legal risk, is
   refreshable, and gives us a fallback and a negotiating position. **This is the single best
   engineering bet in the dossier.**
5. **Build the news pipeline as headline-metadata only, English, two cities, with dedup and a
   status field — and do not ship it to users in v1.** Run it internally for a quarter and measure
   recall against a known set of incidents before deciding whether it is publishable at all.
6. **File the RTI batch** (Himmat, Disha, ERSS/112, plus the SafetiPin-via-city-government request
   at lead 3). One template, many addressees, aggregate counts only. Low hit rate, high payoff.
7. **Stand up the dataset blacklist and verify the Kaggle 40k file.** Hours of work; prevents the
   worst single failure mode available to this project, which is publishing fiction about real
   neighbourhoods.
8. **Defer:** GDELT Event DB (wrong ontology), Common Crawl (wrong tool), Reddit (unrepresentative),
   Google Places reviews (terms probably fatal). **Refuse permanently:** WhatsApp/Telegram/RWA
   harvesting and MyGate.
9. **Scope the vernacular workstream now even though it lands later.** If v1 ships English-only,
   the product must say so on the map in those words — otherwise it silently asserts that
   small-town India has no crime.
