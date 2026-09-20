# India Crime Map

A public crime-information portal for India, in the spirit of
[police.uk](https://www.police.uk/) — so that an ordinary person can find out what
crime looks like where they live, walk, rent or buy.

**Current state: Mumbai carries live FIRs. Bihar has the geography and no feed.**

The two halves of the problem sit in different cities. Bihar publishes thana
jurisdiction polygons and its FIR repository is unreachable from here. Mumbai is
the exact inverse: Maharashtra publishes every FIR it registers, daily and
station-level, and no boundaries at all. So Mumbai is drawn as stations, never
as areas, because no honest area has been published.

## What exists

```
research/     Phase 1: 540 catalogued sources across 17 domains
docs/         PHASE1-FINDINGS.md (what is buildable) · INGESTION.md (the rules)
              TERMS-REVIEW.md (what each portal permits, read from the live sites)
              LIVE-FETCH-2026-09-20.md (what the first unblocked session found)
pipeline/     The Bihar pipeline, plus mahapolice.py / mumbai.py for Mumbai
scripts/      harvest_mumbai.py -- the resumable live fetch
site/         The map pages (generated)
tests/        124 tests
```

## Run it

```bash
pip install -r requirements.txt

python3 -m pipeline.download     # fetch the two public source datasets
python3 -m pipeline.geography    # join stations to thana polygons -> data/spine/
python3 -m pipeline.crosswalk    # grade each mapping by evidence -> review queue
python3 -m pipeline.build_site   # aggregate + assemble site data
python3 -m pipeline.build_page   # render site/index.html

python3 -m pytest tests/ -q
```

### Mumbai, from the live portal

```bash
python3 scripts/fetch_live.py --probe          # look, fetch nothing
python3 scripts/harvest_mumbai.py --from 2021-01 --to 2026-09   # resumable
python3 -m pipeline.mumbai                     # aggregate to station-month
python3 -m pipeline.build_mumbai_page          # render site/mumbai.html
```

The harvest is slow on purpose and slower still by the portal's own speed: it
serves a 50-row page in 20-26 seconds and pages must be walked in order, so a
recent month is about an hour and the full 2017-2026 series is a multi-day
background job. It resumes, and it marks a month complete only when its row
count matches the count the portal declares. Do not raise the concurrency --
these are public-sector servers that citizens depend on.

Then serve `site/` and open it. Everything under `data/` and the generated pages
are reproducible from those commands and are not committed.

## What the pilot established

Bihar was chosen because it is the only Indian state with **both** a public
all-FIR repository at police-station granularity **and** published police station
jurisdiction boundaries. Building it end to end surfaced the problems that a
national version will hit everywhere:

**The geography exists, and nobody built it to be joined.** 929 MHA station
points and 896 i-Bhugoal thana polygons carry incompatible code schemes with no
published crosswalk. The join is spatial, corroborated by name — and neither
witness is trustworthy on its own. About 3% of station coordinates are plainly
wrong (a Begusarai station lands in Nalanda, 80km away), and large rural
"Mufassil" thanas swallow points belonging to smaller neighbours. So every
mapping is graded by evidence, and the 240 rows where the two witnesses disagree
go to a review queue rather than to the map.

**All 896 thanas are reachable; 689 are corroborated.** An earlier version of
this README reported "328 blind spots". That figure was wrong — it counted
thanas with no MHA station point, but the crime feed names stations and the
resolver matches those names against polygons directly, so a missing point is a
missing *second witness*, not a missing route. Every polygon now resolves from
its own name. 689 are additionally confirmed by an independent station record;
the other 207 rest on one source.

**The law changed underneath the data.** The IPC was repealed on 1 July 2024 and
the BNS that replaced it has no statutory concordance. The relation is
many-to-many: IPC 383–389 all collapse into BNS 308. Post-2024 property crime is
therefore permanently lower-resolution than pre-2024, and nothing here keys on a
section number.

**Two categories are absent by law.** A Supreme Court direction of 7 September
2016 excludes sexual offences and POCSO from public FIR publication, and Bihar
additionally withholds national-security, law-and-order and communal FIRs. The
map says *withheld* where those would appear.

## What this map does not say

It maps **FIRs registered by a police station** — not where crimes happened, and
not how safe anywhere is. A station where people trust the police and complaints
get registered will look worse than one that turns people away. That error runs
in one direction and does not average out.

That caveat is carried in the data structures, not in a footnote, and it is
stated above the fold on the map itself. See `docs/INGESTION.md` rule 5.

## Next

1. **Keep the Mumbai harvest running.** `scripts/harvest_mumbai.py` resumes; the
   full 2017-2026 series is tens of hours of polite fetching.
2. **Get the NCRB district tables by hand.** `ncrb.gov.in` and `data.gov.in` both
   publish `Disallow: /`, so the automated route is closed under
   `docs/INGESTION.md` rule 2 — not by preference but by the term. A person
   downloading them, or the data.gov.in API with a registered key, are the routes
   left. This is what closes the 2015-2024 district gap.
3. Work the remaining 118-row review queue. 85 of those are stations whose point
   lands in an unrelated polygon — almost certainly outposts or stations created
   after the boundaries were drawn — and need either local knowledge or a newer
   boundary source.
4. Verify the IPC→BNS concordance against NCRB's Sankalan compendium before any
   post-2024 data is published.
5. Bengaluru, when `ksp.karnataka.gov.in` is reachable — or via the OpenCity
   Karnataka CSVs, which are already machine-readable and licensed.
