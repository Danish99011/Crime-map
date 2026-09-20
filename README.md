# India Crime Map

A public crime-information portal for India, in the spirit of
[police.uk](https://www.police.uk/) — so that an ordinary person can find out what
crime looks like where they live, walk, rent or buy.

**Current state: Bihar pilot, geography complete, crime feed not yet connected.**

## What exists

```
research/     Phase 1: 540 catalogued sources across 17 domains
docs/         PHASE1-FINDINGS.md (what is buildable) · INGESTION.md (the rules)
pipeline/     The Bihar pipeline, end to end
site/         The map page (generated)
tests/        68 tests
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

**568 of 896 thanas can currently take a crime feed.** The other 328 have no
station we can confidently resolve a FIR to. They render as *no data*, never as
zero crime — the distinction the whole design turns on.

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

1. Run `research/verify_sources.py` from an unblocked network — 86% of the
   Phase 1 catalogue is `CITED` rather than verified because every `.gov.in` host
   was blocked during research.
2. Work the 240-row review queue into `data/spine/station_aliases.csv`; that is
   the path from 568 attachable thanas to roughly 850.
3. Finish the Bihar FIR adapter — `docs/INGESTION.md` has the procedure.
4. Verify the IPC→BNS concordance against NCRB's Sankalan compendium before any
   post-2024 data is published.
