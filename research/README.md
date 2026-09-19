# India Crime Map — Phase 1: Source Discovery

Goal: a public portal that tells an ordinary person in India what crime looks like where they
live, walk, rent or buy — the way [police.uk](https://www.police.uk/) does for England & Wales.

Phase 1 answers one question before a line of product code is written:
**what data actually exists, at what geographic resolution, how often does it refresh, and
what is it legal and ethical to publish?**

**Status: Phase 1 complete.** 540 sources catalogued across 17 domains, schema-clean.
Findings and recommendations: [`../docs/PHASE1-FINDINGS.md`](../docs/PHASE1-FINDINGS.md).

## Layout

| path | what it is |
|---|---|
| `_SPEC.md` | the research contract every dossier follows |
| `sources/<domain>.md` | human-readable dossier per research domain |
| `sources/<domain>.jsonl` | machine-readable source entries, one JSON per line |
| `CATALOGUE.md` / `catalogue.json` / `catalogue.csv` | generated master catalogue |
| `_raw/` | scratch, gitignored |

## Tooling

```bash
python3 research/merge_catalogue.py            # rebuild the catalogue, report schema problems
python3 research/merge_catalogue.py --strict   # non-zero exit if any entry is malformed
python3 research/normalize_sources.py          # fold vocabulary drift back into the enums
python3 research/verify_sources.py --patch     # link-check every URL (run from an unblocked network)
```

Edit the per-domain `.jsonl` files, never the generated catalogue.

## The verification gap you must close first

This research ran in a sandbox whose egress policy returned 403 for `*.gov.in`, `*.nic.in`,
`data.police.uk`, OSM mirrors and `web.archive.org`. Agents could search but could not open
Indian government pages. So of 540 sources, **43 are `VERIFIED_LIVE` and 18
`VERIFIED_LANDING`; 357 are `CITED`** (URL and title seen in a search index) **and 122
`UNVERIFIED`**.

That is a target list, not a source list. `verify_sources.py` exists to close the gap: it is
stdlib-only, rate-limits itself to one request per host, and records each page's `<title>`
alongside its status code — because a portal that redirects unknown paths to its homepage
answers `200` for URLs that no longer exist, and the title is what catches that.

## Research domains

| slug | scope |
|---|---|
| `ncrb-national` | NCRB: Crime in India, ADSI, Prison Statistics, CCTNS/ICJS, NDSO, ZIPNET |
| `mha-parliament` | MHA, BPR&D, Parliament Q&A, Nirbhaya/Safe City, ERSS-112 |
| `state-police-north` | J&K, Ladakh, HP, Punjab, Chandigarh, Haryana, Delhi, Rajasthan, UP, Uttarakhand |
| `state-police-south` | AP, Telangana, Karnataka, TN, Kerala, Puducherry, A&N, Lakshadweep |
| `state-police-west` | Maharashtra, Gujarat, Goa, MP, Chhattisgarh, DNH&DD |
| `state-police-east-ne` | Bihar, Jharkhand, WB, Odisha, Sikkim + all 7 NE states |
| `judiciary-prisons` | eCourts, NJDG, HC/SC, prosecution & conviction, prisons, legal aid |
| `geospatial-boundaries` | police-station jurisdictions, district/ward/village boundaries, geocoding |
| `open-data-portals` | data.gov.in, NDAP, state portals, smart-city ICCC dashboards |
| `road-safety-emergency` | MoRTH, iRAD/eDAR, 112/ERSS, fire, disaster |
| `specialised-crime` | cyber (I4C/NCRP), women, children, SC/ST, trafficking, narcotics, economic |
| `civil-society-academic` | SPIR, India Justice Report, Praja, NFHS, DDL/SHRUG, Dataful, academic panels |
| `media-crowdsourced` | news corpora, Safecity, SafetiPin, community reporting |
| `taxonomy-methodology` | IPC→BNS mapping, NCRB heads, principal offence rule, district reorg, denominators |
| `legal-ethics` | GODL-India, DPDP Act 2023, ToU, defamation, victim-identity law, redlining risk |
| `rti-playbook` | how to force out what is not published: RTI mechanics, templates, appeals |
| `benchmark-product` | police.uk & international analogues, data specs, what India's version can be |
