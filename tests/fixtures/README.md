# Test fixtures

## Provenance, in one line

**These are third-party harvested scrapes of a live Indian police portal, taken by someone
unconnected to this project, under no stated licence. They are here so a parser can be written and
reviewed without touching a government server. They are not ours to republish.**

---

## `cctns-published-firs-maharashtra-*.json`

Rows from **Maharashtra Police's CCTNS citizen portal**, "Published FIRs":
`https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx`

### Chain of custody

| | |
|---|---|
| Original publisher | Maharashtra Police (CCTNS citizen portal), a `.gov.in` host |
| Harvested by | `Atharvayadav11/mahagovscrapper` on GitHub — an individual, not this project |
| Harvest date | 2025-09-27 (from the source filenames) |
| Fetched into this repo | 2026-09-20, from `raw.githubusercontent.com`, byte-for-byte unmodified except for renaming |
| Licence | **Unstated.** The source repository has no `LICENSE` and no `README`. Default: all rights reserved. |
| Terms of use of the originating portal | **Not reviewed.** The host is unreachable from this project's network. |

Raw URLs, all under `https://raw.githubusercontent.com/Atharvayadav11/mahagovscrapper/main/`:

| File here | Fetched from | Bytes | Rows | Unique |
|---|---|---|---|---|
| `cctns-published-firs-maharashtra-20rows.json` | `fir-data-2025-09-27T08-44-14-002Z.json` | 9,525 | 20 | 20 |
| `cctns-published-firs-maharashtra-60rows.json` | `fir-data-2025-09-27T08-47-21-029Z.json` | 29,239 | 60 | 60 |
| `cctns-published-firs-maharashtra-500rows-paging-duplicates.json` | `fir-data-2025-09-27T07-41-06-426Z.json` | 209,602 | 500 | **10** |

### What is in a row

```json
{
  "srNo": 6,
  "state": "MAHARASHTRA",
  "district": "PALGHAR",
  "policeStation": "BOISAR",
  "year": 2025,
  "firNumber": "339",
  "registrationDate": "09/08/2025 18:07:00",
  "firNoWithYear": "0339/2025",
  "sections": "भारतीय न्याय संहिता (बी एन एस), 2023 - 303(2) ;",
  "hasDownloadButton": false,
  "coordinates": { "lat": 19.7968929, "lng": 72.7451817 }
}
```

The portal's own English column headers, in order:
`Sr. No. | State | District | Police Station | Year | FIR No. | Registration Date | Sections`,
plus an unlabelled FIR-no-with-year column and a per-row `Download` button for the FIR PDF.

### Why each file is here

- **`20rows`** — smallest honest sample. Two districts, two stations. Use it for fast unit tests.
- **`60rows`** — the richest. Ten distinct acts including BNS 2023, IPC 1860, Motor Vehicles,
  NDPS, SC/ST Atrocities, Juvenile Justice and two state Acts. Multi-act cells, Devanagari act names,
  Devanagari numerals. This is the one to write `pipeline/taxonomy.py` tests against.
- **`500rows-paging-duplicates`** — **deliberately kept because it is broken.** It holds 10 unique FIRs
  repeated 50 times: the harvester's pagination loop re-fetched page 1. It is the regression fixture
  for "does our ingest deduplicate?" Dedup key: `(district, policeStation, firNoWithYear)`.
  It is also the only file **without** the derived `coordinates` key, so it is closest to the raw
  portal columns.

### Three things not to believe

1. **`coordinates` is not portal data.** The harvester geocoded the *police-station name* through
   Nominatim / Google / MapMyIndia. Every FIR at a station gets the same point. The portal publishes
   no geography below the station. Rendering these as incident locations would be a false-precision
   error of exactly the kind `research/_SPEC.md` exists to prevent. `location_semantics` here is
   `reporting-office`, full stop.
2. **`hasDownloadButton` is `false` on all 580 rows**, yet two other independent scrapers locate and
   click a per-row `Download` submit button on the live page. The flag is an artefact of parsing the
   AJAX `updatePanel` fragment, not evidence the PDF is absent.
3. **Row counts are not crime counts.** Two police stations over about six weeks. Nothing here is
   representative of Maharashtra, let alone of India.

### Personal data

**There is none, and that is a property of the source, not of our handling.** The Maharashtra
published-FIR grid carries no complainant, accused, address, age or phone. Verified:

```
>>> from pipeline.fir import audit_columns
>>> audit_columns(['srNo','state','district','policeStation','year','firNumber',
...                'registrationDate','firNoWithYear','sections','hasDownloadButton','coordinates'])
[]
```

This is **not** true of the Bihar repository these fixtures stand in for. Bihar's FIR grid publishes
`complainant`, `address` and `accused`. When a real Bihar extract arrives, `CsvFirSource.audit()` will
flag all three, and that is expected — see `docs/INGESTION.md` rule 3.

### Why Maharashtra fixtures for a Bihar adapter

`scrb.bihar.gov.in` is unreachable from this project's network and no Bihar FIR row is committed
anywhere on GitHub. These Maharashtra rows are the nearest real published-FIR data obtainable. They
are a **lower bound on Bihar's schema, not a template for it** — Bihar's SCRB application is a
separate build with at least five columns Maharashtra lacks.

Read `research/sources/bihar-fir-schema.md` before relying on any of this. Its "What I could NOT
establish" section is the part that matters.

### Handling rules

- Parser fixtures only. Do not merge into `data/`, do not aggregate, do not publish, do not ship in a
  built site.
- Do not re-harvest from the live portal to extend them. `docs/INGESTION.md` rule 4: Phase 1 is
  reconnaissance, and rule 2 is unsatisfied — nobody has read that portal's terms of use.
- If the provenance above cannot be honoured, delete the files rather than quietly keeping them.
