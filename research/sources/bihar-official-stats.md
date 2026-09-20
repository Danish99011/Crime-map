# Bihar Official Crime Statistics & Government Reports (via GitHub, blocked-network route)
_Agent: bihar-official-stats · Researched: 2026-09-20 · Entries: 6 verified-live / 12 total (4 VERIFIED_LIVE data, 2 VERIFIED_LIVE manifest, 4 CITED, 2 UNVERIFIED)_

> **Environment declared up front.** Every `.gov.in` / `.nic.in` host is blocked by this session's
> egress proxy, confirmed by the proxy's own log: `kind: connect_rejected`,
> `detail: "gateway answered 403 to CONNECT (policy denial or upstream failure)"` for
> `scrb.bihar.gov.in:443`, `police.bihar.gov.in:443`, `statedata.bihar.gov.in:443`, `ncrb.gov.in:443`,
> `www.data.gov.in:443`. Also blocked: `web.archive.org`, `zenodo.org`, `dataverse.harvard.edu`,
> `osf.io`, `devdatalab.org`. **I did not route around any of these.** Reachable: `github.com`,
> `raw.githubusercontent.com`, and GitHub code search. `api.github.com` repo endpoints are
> per-repo gated in this session (403 "not enabled for this session") — code search + raw still work.
>
> **Consequence:** every number below was read out of a file I actually downloaded from GitHub.
> No `.gov.in` URL in this dossier was fetched by me; those are marked `CITED` and carry a
> third-party scrape date instead of my own.

---

## Executive summary

- **District-level Bihar crime counts are now IN HAND and validated.** 2001–2014, 44 Bihar police
  districts, 30 IPC crime heads (93 finer heads in 2014), downloaded to
  `data/raw/ncrb-ogd-district/`. This is the NCRB *Crime in India* district supplementary table
  set as republished on data.gov.in under GODL-India, recovered from GitHub mirrors.
- **Provenance is as strong as this kind of find ever gets: four independent repositories carry a
  byte-identical file.** `01_District_wise_crimes_committed_IPC_2001_2012.csv` has
  sha256 `590bd77d0c827d68c4370f8ff94b126951ecbf1bd61d5e7dbb6db9fdfb9a6388` in
  `PaletiKrishnasai/Analytics_of_crimes_in_India` and `aadhityasw/Minority-Report` (both downloaded
  and hashed by me), and the identical oid appears in `DMR-001/crime`'s Git-LFS pointer and
  `Prathamesh0-0/KSP-CrimeIntel`. One of those repos names the originating publisher and licence
  verbatim: *"National Crime Records Bureau (NCRB), Govt of India has published this dataset on their
  website and also has shared on Open Govt Data Platform India portal under Govt. Open Data
  License - India."*
- **It passes an arithmetic authenticity test that synthetic data does not.** For all 14
  independent year-panels checked, the sum of the 44 Bihar district rows equals the file's own
  `TOTAL` row **exactly, delta 0** — 2001 (88,432), 2002 (94,040) … 2012 (146,614), 2013 (167,455),
  plus 12 years of the women's table. Fabricated "India crime" CSVs do not reconcile like this.
- **The join to our thana spine is solved and 100% complete.** `data/spine/bihar_stations.csv`
  carries 44 police districts; NCRB carries the same 44. I built
  `data/reference/bihar_ncrb_district_crosswalk.csv` and validated it: **zero unmapped NCRB labels,
  zero uncovered spine districts, in both directions, across 2001–2014.**
- **The crosswalk is not identity — six labels genuinely differ, and two are traps.** NCRB names
  two districts by HQ town where our spine uses the revenue name: **`BETTIAH` = WEST CHAMPARAN** and
  **`MOTIHARI` = EAST CHAMPARAN**. `BHABHUA` = KAIMUR (BHABUA). Spelling drifts: `PURNEA`→PURNIA,
  `NAWADAH`→NAWADA, `NAUGACHIA`→NAUGACHHIA. A naive string join silently drops the two Champaran
  districts — ~8% of Bihar's population — and they would render as holes on the map.
- **Bihar's NCRB unit list is police districts, not revenue districts.** 44 = 40 territorial + 4
  railway (`JAMALPUR RLY.`, `KATIHAR RLY.`, `MUZAFFARPUR RLY.`, `PATNA RLY.`). The 40 territorial
  are Bihar's 38 revenue districts **plus Bagaha** (carved from West Champaran) **plus Naugachia**
  (carved from Bhagalpur). Railway GRP units have **no polygon** in our thana spine and must never be
  mapped to territory — their "district" is a railway line, not an area.
- **2014 is a hard schema break.** 2001–2013 files are 33 columns / 30 IPC heads; the 2014 file is
  **93 columns**, renames railway units `RLY.`→`Railway`, and adds two pseudo-districts that are not
  geography at all: **`Anti Terrorist Squad` and `Economic Offences Unit`**. Both must be dropped
  before any spatial join or they become phantom places.
- **Case disposal at district level for Bihar: NOT FOUND, and I can now say why.** The two files
  whose names promise it — `04_01/04_02_Person_arrested_and_their_disposal_by_police_and_court_*` —
  are **state × crime-head**, not district: column 2 is `CRIME HEAD`, not `DISTRICT`. Same for
  `07_01_Persons_arrested_by_sex_and_age_group_*` and `17_Crime_by_place_of_occurrence_*`
  (state × year). Downloaded anyway as state-level benchmark; **do not let the filename fool a
  later ingest.**
- **A new, better Bihar source surfaced that the east-ne dossier did not have: the Bihar State Data
  Lab.** `Kantvishu/Govt-of-Bihar-Data` commits a 288 KB manifest of **1,109 XLSX files across 40
  sectors** of `statedata.bihar.gov.in`, with exact download URLs, scraped 2026-03-27. Sector 24
  *Police & Crime* holds 35 files including **"Districtwise Number of Reported Cases" for 2013,
  2014, 2015, 2016, 2018, 2021, 2022**, "Districtwise Number of Woman Reported Cases", "Number of
  SC_ST reported cases", "Number of True Cases of Serious Crimes", and **"Number Of Police Station
  In Bihar" (2015, 2016, 2018)**. Sector 1 adds **"Status of Trial of Criminal Cases" 2012–2021**.
  **This is XLSX, not PDF, and it covers 2015–2022 — exactly the years NCRB's district CSVs stop
  short of.** I extracted the 157 crime/justice URLs to `data/raw/bihar-statedata/`.
- **Two corrections to `state-police-east-ne.md`.** (1) That dossier says
  `biharpolice.bihar.gov.in` "appears in no index"; the real legacy host is
  **`biharpolice.bih.nic.in`**, which served monthly Crime Monitoring Abstracts at
  `/menuhome/CMA-{YYYY}.htm`, 2010–2021. (2) That dossier says the SCRB FIR repository has "no
  single bulk endpoint"; the committed scraper shows **there is a per-district bulk endpoint** —
  leave the police-station dropdown empty and one POST returns the whole district, **no login and
  no captcha**, session cookie only.
- **Biggest gap: 2015 onward at district level, from an official source I can actually reach.**
  NCRB's district CSVs stop at 2014. NCRB withheld district data entirely for 2016 and 2017.
  Everything that would close the gap — SCRB *Crime in Bihar* PDFs, the State Data Lab XLSX, the
  live FIR repository — sits behind the `.gov.in` block. **Nothing on GitHub mirrors Bihar district
  crime counts for 2015+.** I searched for it specifically and it is not there.

---

## Source entries

### 1. NCRB district-wise IPC crime, Bihar 2001–2014 (OGD/data.gov.in republication) ★★ INGEST FIRST

The backbone find. NCRB *Crime in India* district supplementary tables, released by NCRB on the
Open Government Data platform under GODL-India, recovered from GitHub mirrors because
`data.gov.in` is blocked.

```
id          bihar-official-stats-ncrb-ogd-district-ipc
publisher   National Crime Records Bureau (MHA), via Open Government Data Platform India
granularity district (police district) · aggregate-count · annual · IPC · CSV
years       2001-2012 (one file), 2013, 2014
access      open-download (from GitHub mirror)   machine_readable 4   ingest_difficulty 2   priority 5
verification VERIFIED_LIVE — downloaded, parsed, row-counted, checksummed, totals-reconciled
local       data/raw/ncrb-ogd-district/01_District_wise_crimes_committed_IPC_{2001_2012,2013,2014}.csv
```

Schema 2001–2013 (33 cols): `STATE/UT, DISTRICT, YEAR,` then 30 IPC heads —
MURDER, ATTEMPT TO MURDER, CULPABLE HOMICIDE NOT AMOUNTING TO MURDER, RAPE, CUSTODIAL RAPE,
OTHER RAPE, KIDNAPPING & ABDUCTION (+2 sub-heads), DACOITY, PREPARATION AND ASSEMBLY FOR DACOITY,
ROBBERY, BURGLARY, THEFT (+AUTO THEFT, OTHER THEFT), RIOTS, CRIMINAL BREACH OF TRUST, CHEATING,
COUNTERFIETING *(sic — NCRB's own misspelling, preserved)*, ARSON, HURT/GREVIOUS HURT *(sic)*,
DOWRY DEATHS, ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY, INSULT TO MODESTY OF WOMEN,
CRUELTY BY HUSBAND OR HIS RELATIVES, IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES,
CAUSING DEATH BY NEGLIGENCE, OTHER IPC CRIMES, TOTAL IPC CRIMES.

Bihar row counts: **540** rows 2001–2012 (45 units × 12 years), **45** in 2013, **47** in 2014.

**Verification actually performed**, not asserted:

| year | Σ 44 district rows | file's own TOTAL row | delta |
|---|---|---|---|
| 2001 | 88,432 | 88,432 | 0 |
| 2005 | 97,850 | 97,850 | 0 |
| 2010 | 127,453 | 127,453 | 0 |
| 2012 | 146,614 | 146,614 | 0 |
| 2013 | 167,455 | 167,455 | 0 |

All 12 years of 2001–2012 reconcile at delta 0; so do all 12 years of the women's table.

### 2. NCRB district-wise crime against women / SC / ST / children, Bihar 2001–2014 ★

Same provenance, same geography, same crosswalk. Downloaded:
`42_..._against_women_{2001_2012,2013,2014}.csv`, `02_01_..._against_SC_{2001_2012,2013,2014}.csv`,
`02_..._against_ST_{2013,2014}.csv`, `03_..._against_children_2013.csv`.
`priority 5` for women (it is the category a safety map is most asked about), `4` for SC/ST/children.

### 3. Bihar State Data Lab — Police & Crime sector (35 XLSX) ★★ HIGHEST-VALUE BLOCKED ITEM

```
id          bihar-official-stats-bihar-statedatalab-police-crime
publisher   Government of Bihar (statedata.bihar.gov.in/dataLab)
granularity district · aggregate-count · annual · XLSX
years       2013-2022
access      blocked (.gov.in egress denial) — URLs exact and third-party-verified
verification CITED (manifest VERIFIED_LIVE; the XLSX files themselves unfetched by me)
local       data/raw/bihar-statedata/bihar_statedatalab_crime_justice_files.csv  (157 URLs)
            data/raw/bihar-statedata/bihar_sectors_all.json                      (all 1,109)
```

Titles confirmed in the manifest, with year: *Districtwise Number of Reported Cases* (2013, 2014,
2015, 2016, 2018, 2021, 2022); *Districtwise Number of Woman Reported Cases* (2013, 2014, 2019,
2020); *Number of SC_ST reported cases* (2013–2016, 2019, 2020); *Number of True Cases of Serious
Crimes* (2013–2016); *Cognizable Crime Figure* (2019–2022); *Comparative Crime Figure* (2015–2022);
*Number Of Police Station In Bihar* (2015, 2016, 2018).

URL pattern: `https://statedata.bihar.gov.in/dataLab/assets/pdf/sectoralData/<filename>.xlsx`
(note: `.xlsx` files served from a directory called `pdf`). Third-party note says files are
**directly downloadable despite the site's captcha modal** — the captcha is a front-end modal only.

*"Number Of Police Station In Bihar"* is the one to grab first after the crime tables — it is the
official thana roster, and our spine currently has 99 stations in `needs-review` and 190 thana
polygons unreached by any station.

### 4. Bihar Civil & Criminal Justice — Status of Trial of Criminal Cases, 2012–2021

Same portal, sector 1, 20 XLSX files (10 years × 2 titles: *Status of Trial of Criminal Cases*,
*No of Cases decided in Sub Courts of Bihar*). **This is the closest thing to disposal data found
for Bihar.** Granularity unknown — the title does not say whether it breaks down by district. URLs
captured in the same manifest CSV. `priority 3`, `verification CITED`.

### 5. SCRB Bihar FIR / Arrest / Dead-Bodies / Missing-Persons repository — mechanics recovered

```
id          bihar-official-stats-scrb-fir-endpoint-mechanics
granularity police-station · fir-record · daily
access      blocked here; scrape elsewhere   verification CITED (third-party scrape 2026-03-28/30)
```

`Kantvishu/Govt-of-Bihar-Data` commits a working scraper (`scrape_scrb.py`, 331 lines) and its
`CLAUDE.md`. What it establishes, upgrading the east-ne dossier:

- Endpoints: `FIRiew.aspx`, `ArrestDetail.aspx`, `deadbodies.aspx`, `MissingPersons.aspx`.
- ASP.NET postback: GET for `__VIEWSTATE` + `__VIEWSTATEGENERATOR` + `__EVENTVALIDATION`, then POST
  `ctl00$ContentPlaceHolder1$ddlDistrict` + date range + `btnSearch`.
- **`ddlPoliceStation` left empty returns the whole district** — a bulk endpoint does exist.
- **No login, no captcha.** Session cookie only.
- Reported yields: 92,424 FIRs (2016–2026), 277,557 arrest records. *Third-party claim — the repo's
  `data/` directory is `.gitignore`d, so none of it is committed and I could not verify the counts.*
- Server bugs to design around: OutOfMemory on large districts (query by date range), photo
  rendering crashes, **the FIR page's date filter is broken and returns all data regardless**, DNS
  instability under load.

**Carries a live SCRB district-code table** (`DISTRICTS` dict, 49 entries) — see entry 6.

**Ethics flag, recorded deliberately.** The arrest feed carries officer name + designation, and
that repo's README states *"Officer surnames allow approximate caste inference (~40% match rate)"*
and that 35,719 officers are individually identifiable. It also names not-yet-convicted arrestees.
This is a re-identification and defamation hazard on both sides of the encounter. Nothing from this
feed should reach the public map without legal sign-off; see `legal-ethics.md`.

### 6. Bihar SCRB police-district code table (49 units) ★ — the code list hunt item

Recovered from `scrape_scrb.py`, described in-file as *"District code -> name mapping from the
website"*. 40 territorial IDs `1–39, 41` and 9 special units `42, 44, 45, 46, 48, 49, 50, 51, 52`
(ATS, SVU, Rail_Muzaffarpur, Rail_Jamalpur, Rail_Patna, Rail_Katihar, VIB, Economic_Offence_Unit,
CID_Patna). Local copy: `data/raw/bihar-statedata/scrape_scrb.py`.

**Decisive for the crosswalk:** SCRB calls them `East_Champaran` / `West_Champaran`, while NCRB
calls the same two units `MOTIHARI` / `BETTIAH`. Seeing both vocabularies side by side is what
proved the two are the same geography rather than missing districts.

### 7. Bihar NCRB → spine district crosswalk (built here) ★★

```
local       data/reference/bihar_ncrb_district_crosswalk.csv
columns     ncrb_ogd_label, spine_district, revenue_district, unit_type, note
verification VERIFIED_LIVE — validated in both directions, zero residual
```

53 rows: 44 mappable police districts + the drop-list (`TOTAL`, `ZZ TOTAL`, `Anti Terrorist Squad`,
`Economic Offences Unit`) + the 2014 `Railway` spelling variants. See §How it joins.

### 8. NCRB state-level disposal & arrest tables (negative finding, downloaded as benchmark)

`04_01`/`04_02` (persons arrested and their disposal by police and court, SLL/IPC, 2012 & 2013),
`07_01` (persons arrested by sex and age group, IPC, 2013 & 2014), `17` (crime by place of
occurrence, 2001–2012, 2013, 2014). **All are state-level**, keyed `STATE/UT × CRIME HEAD` or
`STATE/UT × YEAR`. Bihar appears as 30 crime-head rows (04_02, 2013), 11 (04_01, 2013), 12 year-rows
(17). `geo_granularity: state`. Useful only to benchmark a district panel against the state total.
`priority 2`.

### 9. `devdatalab/paper-justice` — eCourts criminal-case replication (disposal, but gated)

Replication repo for *"In-group bias in the Indian judiciary: Evidence from 5 million criminal
cases"* (Ash, Asher, Bhowmick, Chen, Devi, Goessman, Novosad, Siddiqi 2021). Files
`cases_clean_2010`…`cases_clean_2018` cover close to the universe of Indian lower-judiciary criminal
cases, plus `judges_clean` and `acled_districts` (an ACLED-to-district key). **The data packet is
hosted off-GitHub and the host is blocked; only code is in the repo.** This is the single best
route to district-level *court* disposal for Bihar if the packet can be reached from an unblocked
network. `verification CITED`, `priority 3`, `access on-request`.

### 10. `devdatalab/masala-merge` — fuzzy matcher for Indian place names (tool)

Stata/R/Python fuzzy join with Levenshtein costs tuned for Indian transliteration (e.g. `KS→X`),
`reclink` content matching, and conservative exclusion of ambiguous matches. Directly applicable to
our 99 `needs-review` stations and to any future district vocabulary that is not already in the
crosswalk. `tier 4`, `priority 3`, `verification VERIFIED_LIVE` (README read).

### 11. Bihar Police CMA — monthly Crime Monitoring Abstracts, 2010–2021 (seed lead)

`http://biharpolice.bih.nic.in/menuhome/CMA-{YYYY}.htm`, reachable only through the Wayback Machine.
Third-party reports 1,848 monthly observations, 14 crime categories, **state-level aggregates only**,
2016 missing (archived page truncated), 2021 Jan–Mar only. Both `.nic.in` and `web.archive.org` are
blocked here. `verification CITED`, `priority 2` — monthly cadence is attractive but state-level
granularity is not what the map needs.

### 12. HAZARDS — what NOT to ingest

- **Any "India crime" CSV without a numbered NCRB table prefix.** The `NN_` prefix
  (`01_`, `02_01_`, `42_`) is the OGD resource index and is the provenance. A file called
  `crime.csv` or `india_crime_data.csv` with the same columns is unfalsifiable.
- **The Kaggle synthetic "India crime" datasets** flagged by a previous agent. I did not locate or
  download either; the defence against them is mechanical — **run the district-sum-vs-TOTAL
  reconciliation** in entry 1. Genuine NCRB extracts reconcile at delta 0. Fabricated ones do not.
- **`Xmanish8/KSP_DATATHON`'s `data/processed/*` (≈70 files).** Derived ML outputs —
  `risk_scores.csv`, `crime_forecast.csv`, `anomaly_flagged.csv`, `hotspot_clusters.csv`. Model
  output, not observation. Do not let it near the map. Its `data/raw/` is fine; `data/processed/`
  is not.
- **`Xmanish8`'s copy of `01_..._2001_2012.csv` (sha256 `edab26…`) differs from the four-repo
  consensus hash.** I diffed the Bihar rows and they are identical after CRLF normalisation, so it
  is a line-ending artefact — but prefer the consensus-hash copy, which is what
  `data/raw/ncrb-ogd-district/MANIFEST.csv` records.
- **Repos claiming counts for data they do not commit.** `Kantvishu/Govt-of-Bihar-Data` is valuable
  for its manifest and its scraper, but its headline row counts are unverifiable: `data/` is
  gitignored and the raw URLs 404.

---

## How this joins to our thana / district geography

**District level (works today, end to end).**

`data/raw/ncrb-ogd-district/*.csv` → column `DISTRICT` (or `District` in 2014)
→ `data/reference/bihar_ncrb_district_crosswalk.csv[ncrb_ogd_label]`
→ `spine_district` → `data/spine/bihar_stations.csv[district]`
→ `station_id` / `thana_id` → `data/spine/bihar_thana.geojson`.

Validated: 44 NCRB labels, 44 spine districts, **zero unmapped either way**, 2001–2014.

Mandatory pre-join steps, in order:

1. Filter `STATE/UT == 'BIHAR'` (2001–2013) or `States/UTs == 'Bihar'` (2014).
2. **Drop `TOTAL`, `ZZ TOTAL`, `Anti Terrorist Squad`, `Economic Offences Unit`.** These are not
   places. Keeping `TOTAL` double-counts the entire state; keeping ATS/EOU invents two districts.
3. Uppercase and trim, then map through the crosswalk — **do not string-match**, or BETTIAH and
   MOTIHARI silently vanish.
4. Handle 2014 separately: 93 columns, `Railway` not `RLY.`.
5. Flag the 4 railway units `unit_type = railway-police-district`. **They have no polygon.** Either
   exclude them or show them as a non-spatial footnote; never dissolve them into territory.
6. For products that need Bihar's 38 revenue districts rather than 40 police districts, sum
   `BAGAHA + WEST CHAMPARAN` and `NAUGACHHIA + BHAGALPUR` (the `revenue_district` column does this).

**Thana level: not possible from NCRB, at any year.** NCRB's floor is the district. Bihar's district
crime count must be rendered as a **district choropleth**, never pushed down to the 896 thana
polygons — a district count divided across thanas is an invention. Thana-level Bihar crime exists
only in the SCRB FIR repository (entry 5), which is blocked here and legally encumbered.

**`location_semantics` for everything in entry 1–3: `reporting-office`.** NCRB counts the police
district that registered the FIR, not where the offence occurred. For the four railway units this is
especially sharp — a theft on a train between Patna and Katihar is counted at whichever GRP post
registered it.

---

## Granularity reality check

| level | source | years | cadence | in hand? |
|---|---|---|---|---|
| `district` (44 police districts) | NCRB OGD CSVs, entries 1–2 | **2001–2014** | annual | **YES — downloaded & validated** |
| `district` | Bihar State Data Lab XLSX, entry 3 | 2013–2022 | annual | No — `.gov.in` blocked, URLs captured |
| `district` | SCRB *Crime in Bihar* PDFs | 2018–2020 | annual | No — blocked; also scanned PDF |
| `state` | NCRB disposal/arrest, entry 8 | 2012–2014 | annual | YES — downloaded (benchmark only) |
| `state` | Bihar Police CMA, entry 11 | 2010–2021 | **monthly** | No — `.nic.in` + Wayback blocked |
| `police-station` | SCRB FIR repository, entry 5 | 2016–2026 | daily | No — blocked; ethics hold |
| **2015–2024 district** | **nothing reachable** | — | — | **NO — the gap** |

The honest summary: we have a **clean, joinable, 14-year district panel that ends in 2014**, and
nothing after it. For a product that answers "is this neighbourhood safe to rent in *now*", a panel
ending 2014 is a historical baseline, not an answer.

---

## Blockers and how to get past them

1. **`.gov.in` / `.nic.in` egress denial** (403 on CONNECT). Not circumventable and I did not try.
   Everything in entries 3, 4, 5, 11 needs one run from an unblocked network. The URLs are exact —
   entry 3's 157 URLs are a ready-made download list, roughly one `curl` loop.
2. **`web.archive.org` blocked**, which removes the usual fallback for entry 11 and for older
   *Crime in Bihar* volumes.
3. **`dataverse.harvard.edu`, `zenodo.org`, `osf.io` all blocked**, so the academic-replication
   route (entry 9) is closed from here even though the repos are readable.
4. **`api.github.com` repo endpoints are per-repo gated in this session** (`git/trees` returns 403
   "not enabled for this session"). Workarounds used: GitHub **code search** with `repo:` to
   enumerate files, and `raw.githubusercontent.com` to fetch. Note code search does not index files
   over ~350 KB — the large 2001–2012 panels were invisible to search and had to be probed by
   direct raw URL guess.
5. **Git LFS pointers masquerade as CSVs.** `DMR-001/crime` returns HTTP 200 and a 132-byte
   `version https://git-lfs.github.com/spec/v1` stub. Always check the first 40 bytes.

---

## Seed Leads (unconfirmed but probably real)

1. **`Crime in Bihar` 2021–2024 volumes.** east-ne found 2018/2019/2020 at
   `scrb.bihar.gov.in/images/{Crime%20in%20Bihar,CIB%2019,cib_20}.pdf`. Increment: `cib_21.pdf` …
   `cib_24.pdf`. The State Data Lab manifest shows Police & Crime files existing for 2021 and 2022,
   so the series did continue past 2020 in some form.
2. **Bihar Vidhan Sabha / Vidhan Parishad starred-question answers** carrying district crime tables.
   Not searchable from here (assembly sites are `.nic.in`). Concrete step: `vidhansabha.bih.nic.in`
   question-answer archive, or RTI to the Bihar Legislative Assembly Secretariat.
3. **Bihar Police Annual Administrative Report**, tabled in the Assembly. Standard for state police
   forces; not indexed on GitHub. RTI to PIO, Police Headquarters, Sardar Patel Bhawan, Patna.
4. **Bihar Economic Survey** (Finance Dept, annual) reliably carries a law-and-order chapter with
   district tables, and is usually a clean digital PDF rather than a scan. Likelier to be
   OCR-free than the SCRB volumes.
5. **CCTNS Bihar district dashboards.** Every state runs one internally; a few expose read-only
   views. Worth one probe of `biharpolice.gov.in`/`scrb.bihar.gov.in` for a `dashboard`/`report`
   path from an unblocked network.
6. **The `paper-justice` data packet** (entry 9) — `paulnovosad.com/pdf/india-judicial-bias.pdf`
   names the packet location. That domain was not tested here.

---

## Phase 2 recommendations — ranked "ingest first" for Bihar

1. **`data/raw/ncrb-ogd-district/01_*` + `42_*` → district panel, Bihar, 2001–2014.**
   Already downloaded, already crosswalked, already reconciled. Zero further network needed.
   Ship this as the map's district baseline layer. **Start here today.**
2. **Wire `data/reference/bihar_ncrb_district_crosswalk.csv` into the pipeline as the only
   permitted district-name resolver for Bihar**, with a hard assertion that every input label
   resolves. This is the guard that stops BETTIAH/MOTIHARI silently disappearing in a later refresh.
3. **From an unblocked network, fetch the 35 Police & Crime XLSX** in
   `data/raw/bihar-statedata/bihar_statedatalab_crime_justice_files.csv`. This is the single
   highest-value remaining action: it is machine-readable, district-level, and covers **2015–2022**,
   closing the exact gap NCRB leaves. Fetch *Number Of Police Station In Bihar* in the same pass.
4. **Reconcile State Data Lab against NCRB on the 2013 and 2014 overlap.** Two independent official
   sources for the same two years is a free validation of both. If they disagree, we learn the
   definitional difference before it reaches a map.
5. **`02_01_*` SC / `02_*` ST / `03_*` children** — already downloaded, same crosswalk, adds crime
   categories at no ingest cost.
6. **Status of Trial of Criminal Cases 2012–2021** (entry 4) — determine whether it is district-level.
   If yes, it is our only disposal series for Bihar and jumps to priority 5.
7. **`masala-merge`** against the 99 `needs-review` stations and 190 unreached thana polygons.
8. **Legal review before any FIR-level work** (entry 5). Do not scrape SCRB until
   `legal-ethics.md` sign-off exists; the officer-identification and named-accused exposure are
   real, and the caste-inference finding in that public repo shows the harm is not hypothetical.
9. **Do not ingest** `data/processed/*` from any of the mirror repos. Model output, not data.
