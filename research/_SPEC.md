# Research Contract — India Crime Map, Phase 1 (Source Discovery)

**Read this fully before doing anything.** Every research agent writes to the same schema so
the 16 dossiers can be merged into one machine-readable master catalogue.

## Mission

We are building an India-wide public crime-information portal, in the spirit of **police.uk**
(street-level crime maps, counts by area, drill-down to category and outcome) but adapted to
what Indian data actually permits. Phase 1 is **source discovery only**: find every dataset,
document, portal, API, dashboard, report and record series that could feed such a map — and
for anything that exists but is not openly published, document *exactly how to obtain it*.

The product intent matters, because it decides what counts as a useful source:
a resident wants to know "is this neighbourhood safe to rent in / walk through at night?"
So we care most about sources with **fine spatial granularity** and **regular refresh**.
But we also catalogue coarse annual national data, because it is the backbone and the
benchmark everything else is validated against.

## Hard rules

1. **Never invent a URL.** A plausible-looking URL you did not fetch is worse than no URL.
   Every entry carries a `verification` field and you must be honest about it.
2. **Verify what you can.** Use WebSearch to find, then WebFetch to confirm the page exists and
   says what you think it says. Record the date you checked and what you actually saw
   (page title, table names, file sizes, row counts, years covered).
3. **If something is blocked** (captcha, login, TLS error, 403, geo-fence, JS-only dashboard),
   do not silently drop it. Record it with `access: blocked` and describe the blocker precisely,
   plus your best advice on how a human in India (or a scraper with a session) would get it.
4. **Write down the things you suspect exist but could not confirm** in the `Seed Leads` section.
   Name the likely publisher, the likely document title, and the concrete next step to find it
   (a specific RTI, a specific portal path, a specific person/office to contact). This is
   explicitly wanted output, not a failure.
5. **Record caveats as first-class content.** A source that undercounts, re-bases, changes
   definitions mid-series, or aggregates away the interesting variation is still catalogued —
   with the caveat attached. Caveats are the difference between a map that informs and a map
   that defames a neighbourhood.
6. **Do not scrape at volume.** Phase 1 is reconnaissance. Fetch pages to verify, not to harvest.
   Note rate limits, robots.txt and terms of use for Phase 2.

## Your two output files

### 1. `research/sources/<your-slug>.md` — the human-readable dossier

Structure:

```markdown
# <Domain Title>
_Agent: <slug> · Researched: <YYYY-MM-DD> · Entries: <n> verified / <n> total_

## Executive summary
5-12 bullets. What exists, what is genuinely usable for a map, what the single biggest
blocker in this domain is, and the finest spatial granularity achievable here.

## Source entries
### <n>. <Source name>
(one subsection per source, containing the fields listed in the Field Dictionary below,
written as prose + a fenced key/value block — whatever is readable, but every field present)

## Granularity reality check
A short table: what geographic level is actually available, for what time period, how fast
it updates. Be blunt about the gap between what we want and what exists.

## Blockers and how to get past them
## Seed Leads (unconfirmed but probably real)
## Phase 2 recommendations
Ranked, concrete: what to ingest first and why.
```

### 2. `research/sources/<your-slug>.jsonl` — one JSON object per line, per source

No wrapping array, no trailing commas, one source per line. Fields:

| field | type | notes |
|---|---|---|
| `id` | string | kebab-case unique slug, prefix with your agent slug e.g. `ncrb-crime-in-india` |
| `name` | string | official name of the dataset/report/portal |
| `publisher` | string | the body that owns it |
| `domain` | string | your agent slug |
| `tier` | int 1-5 | 1=official national statistics, 2=official operational/police, 3=official-adjacent (courts, ministries, regulators), 4=academic/NGO/civil society, 5=media/crowdsourced/commercial |
| `urls` | object | `{"landing":..., "data":..., "api":..., "docs":...}` — omit keys you have no URL for |
| `geo_coverage` | string | e.g. "all-India", "Telangana", "Mumbai city police jurisdiction" |
| `geo_granularity` | string | one of: `national`,`state`,`district`,`city`,`police-district`,`police-station`,`ward`,`beat`,`grid`,`point`,`address` |
| `location_semantics` | string | **what the geography in this source actually means** — see below |
| `unit_of_record` | string | `aggregate-count`, `fir-record`, `incident-point`, `case-record`, `victim-record`, `survey-respondent`, `boundary-polygon`, `narrative-document` |
| `time_start` | string | earliest year/date available, or `unknown` |
| `time_latest` | string | most recent period available as of your check |
| `cadence` | string | `annual`,`quarterly`,`monthly`,`weekly`,`daily`,`realtime`,`irregular`,`one-off` |
| `lag` | string | typical publication delay, e.g. "12-18 months" |
| `taxonomy` | string | crime classification used: `IPC`,`BNS`,`IPC+SLL`,`NCRB-heads`,`custom`,`n/a` |
| `formats` | array | `["PDF","XLSX","CSV","JSON","HTML","SHP","GeoJSON","dashboard-only"]` |
| `access` | string | `open-download`,`api-key`,`scrape`,`captcha`,`login`,`rti-only`,`paid`,`on-request`,`blocked` |
| `machine_readable` | int 0-5 | 0=scanned image PDF, 5=documented JSON API |
| `license` | string | e.g. `GODL-India`, `CC-BY-4.0`, `unstated`, `ToU-restricts-reuse`, `unknown` |
| `caveats` | array of strings | undercounting, definition breaks, principal-offence-rule, district reorg, etc. |
| `ingest_difficulty` | int 1-5 | 1=trivial download, 5=needs RTI campaign or OCR of scanned scans |
| `priority` | int 1-5 | 5=must have for v1 of the map, 1=nice to have someday |
| `verification` | string | `VERIFIED_LIVE` (you fetched it and saw the data), `VERIFIED_LANDING` (page loads, data not opened), `CITED` (credible reference elsewhere, URL unconfirmed), `UNVERIFIED` (you believe it exists) |
| `checked_on` | string | YYYY-MM-DD |
| `evidence` | string | what you actually saw — page title, table names, years, row/file counts. 1-3 sentences. |
| `how_to_obtain` | string | required when access is not `open-download`. Concrete steps. |
| `notes` | string | anything else that matters |

## `location_semantics` — the field that stops us shipping a wrong map

One word, "location", hides at least seven different things in Indian crime data, and
blending them produces a map that is confidently false. The cyber-fraud portal counts the
**victim's** district. The national cyber centre's hotspot list counts the **offender's**
district. NCRB counts the **police station that registered the FIR**. Trafficking data often
records the **rescue** city rather than the source village; narcotics data records the
**interdiction point**, which is a highway checkpoint, not where the drugs are sold.

Every entry must declare which it is:

| value | meaning |
|---|---|
| `offence-location` | where the act happened — the only semantics a safety map really wants |
| `victim-residence` | where the victim lives or was registered |
| `offender-residence` | where the accused lives or was traced to |
| `reporting-office` | the police station, commission or portal that recorded it |
| `service-point` | where a helpline, shelter, hospital or One Stop Centre delivered a service |
| `interdiction-point` | where a seizure, raid or arrest occurred |
| `court-venue` | where the case is being heard |
| `jurisdiction-aggregate` | aggregated to an administrative area with semantics unstated by the publisher |
| `unknown` | you could not determine it — say so rather than guessing |
| `n/a` | the entry is not crime data: a boundary file, statute, tool or methodology reference |

If a source mixes several, record the dominant one and explain the rest in `caveats`.

## Field Dictionary notes

- **`geo_granularity` is the field that decides the product.** Be precise and be honest.
  "District-level annual counts" and "police-station-level monthly counts" are different
  products. If a source claims fine granularity but only ships a PDF of state totals, the
  granularity is `state`.
- **`priority`** should reflect: granularity x freshness x coverage x ease. A monthly
  police-station-level feed for one city beats an annual national PDF for our purposes,
  even though the PDF is more "official".
- **`caveats`** — always check for and note: the NCRB *principal offence rule*, changes in
  crime-head definitions, the IPC-to-BNS transition (BNS/BNSS/BSA in force 1 July 2024),
  district boundary reorganisation, population denominators used for rates, and whether
  counts are *reported crime* (FIRs) vs *convictions* vs *survey prevalence*.

## Style

Dense, specific, sourced. No filler, no "it is important to note", no restating the brief.
A sentence that does not carry a fact, a URL, a number or an instruction should be deleted.
Prefer a table to a paragraph. Write for an engineer who has to build the ingestion pipeline
and a lawyer who has to sign off on publishing it.
