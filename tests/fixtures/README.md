# Test fixtures

## Provenance, in one line

**These are saved pages and rows from live Indian police portals, here so a parser can be written and
reviewed without touching a government server. The CCTNS rows are third-party scrapes under no
stated licence and are not ours to republish; the Mumbai Police station pages were fetched by this
project and had every officer's identity removed before being committed. Each section says which.**

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

---

## `mumbaipolice-station-ps{62,9,18}.html`

Three pages from **Mumbai Police's own station directory**, the commissionerate's site rather than the
state CCTNS portal: `https://mumbaipolice.gov.in/policestation?ps=<id>` for Nagpada (62), Bandra (9)
and Chunabhatti (18). They are here so the station-page parser and the directory join
(`pipeline/mumbai_join.py`) can be written and reviewed without touching the host.

### Chain of custody

| | |
|---|---|
| Original publisher | Mumbai Police, a `.gov.in` host |
| Fetched by | this project, `scripts/crawl_mumbaipolice_stations.py`, one request at a time, 3 s apart |
| Fetched | 2026-09-21, into `data/raw/mumbaipolice/stations/ps_<id>.html` (gitignored) |
| Copied here | 2026-09-21, **with officer identity and the page's live CSRF token removed** (below); otherwise byte-for-byte |
| Terms of use | Reviewed: `docs/TERMS-REVIEW.md`. No robots.txt; the site's disclaimer warns that telephone numbers may have changed since publication, and the map must say so too. |

### What was removed, and why

The pages name the station's Senior Police Inspector, the Divisional ACP, the Zonal DCP and the
Regional Additional CP, each linked to a profile page. Those are people, and `docs/INGESTION.md`
rule 3 is that identifiers are dropped at the boundary. Fixtures are committed, so the boundary is
here. In each copy:

| Element on the page | Replaced with |
|---|---|
| Sr. PI's name on the "From the desk of Sr. PI" plate | `[officer name removed]` |
| Sr. PI's mobile number on that plate's post line | `[officer mobile removed]` |
| Sr. PI's photograph (`images/Police_incharge/<n>.png`) | `src="[officer photo removed]"` |
| The page's live Laravel CSRF `_token` (a per-session random value; not this project's credential, and not replayable without the session cookie, which was never captured) | `value="[csrf token removed]"` — caught by the security guard after the first push and scrubbed in the follow-up commit |
| Divisional ACP, DCP Zone and Regional Addl. CP name cells, including the `title` attribute and the `?name=` profile link | `<span class="txt-val" title="[officer name removed]">[officer name removed]</span>` |

Nothing else was changed. The office data stays: station telephone numbers, office email
(obfuscated by the site as `[dot]`/`[at]`), division, zone and region labels, the ACP / DCP / Addl. CP
**office** contact numbers, area, population, beat marshals, beat chowkies, hospitals, nearest railway
station, bus depot, the "Locate Us" address with its pincode, and the map embed the coordinates and
English name come from.

The removal was done by anchored regexes that fail if a page does not carry exactly the expected
number of each element, and `tests/test_mumbai_join.py::TestFixturesCarryNoOfficerIdentity` asserts
the markers are present and no `?name=` link or officer image survives. It does so structurally: a
test that listed what was removed would carry the very thing it exists to keep out. Any refresh of
these fixtures must go through the same scrub before being committed.

The parser is checked from the other side too: `tests/test_mumbaipolice_stations.py::TestNoPersonalData`
reads the officers' names off the **unscrubbed** raw page at test time (`data/raw/...`, gitignored,
so it skips where that file is absent) and asserts that no word of them, and not the number beside
the Sr. PI's name, appears anywhere in the parsed record. `pipeline/mumbaipolice.py` also raises
`PersonalDataLeak` at the end of every parse if a name from the page is found in the record.

### Three things to know before parsing them

1. **Devanagari digits.** Telephone numbers, area and the address pincode are written in Devanagari
   numerals on some pages (`२२२३०९२२९३`, `४०० ००८`) and ASCII on others (`400 050.`). Both occur
   across these three pages, deliberately.
2. **Empty is not zero.** Chunabhatti's "DCP office contact no." cell is blank. That is a null with a
   reason (the site did not publish one), never `""` or `0`.
3. **The coordinates are the office, not the jurisdiction.** The map embed's `!3d`/`!2d` is where the
   station building is. Maharashtra publishes no jurisdiction boundaries; nothing here changes that.

### Handling rules

- Parser and join fixtures only. Do not merge into `data/`, do not publish, do not ship in a built
  site.
- Do not re-fetch from the site to extend them; the crawl script owns that host, one request at a
  time.
