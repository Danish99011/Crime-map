# Published-FIR Row Schema (Bihar target, CCTNS deployments observed)
_Agent: bihar-fir-schema · Researched: 2026-09-20 · Entries: 3 verified / 7 total_

## Executive summary

- **`scrb.bihar.gov.in` was never fetched.** The entire `.gov.in` / `.nic.in` namespace is refused by
  this sandbox's egress proxy. Nothing below is a reading of the live Bihar page. The route taken
  instead was GitHub: `api.github.com` code search (via the authenticated MCP tool — the raw REST
  endpoint is proxy-restricted to this repo) plus `raw.githubusercontent.com`, which **is** reachable
  and was used to fetch and read every file cited.
- **A Bihar-specific scraper exists and was read in full**: `Kantvishu/Govt-of-Bihar-Data`. It declares
  the FIR result columns, the ASP.NET control names, the full 50-entry district-code dropdown, and
  reports **92,424 FIR rows across 40 districts, 2016–2026**, scraped 2026-03-28 to 2026-03-30.
  Its `data/` directory is **gitignored — no Bihar rows are committed anywhere on GitHub.**
- **The correct Bihar endpoint is `FIRiew.aspx`, not `View_FIR.aspx`.** Every scraper and the repo's
  own API table name `https://scrb.bihar.gov.in/FIRiew.aspx`. `View_FIR.aspx` is most likely the menu
  page that links to it. `docs/INGESTION.md` and `BiharScrbSource.path` currently target the wrong one.
- **Transferability holds, but only partly.** Maharashtra's `PublishedFIRs.aspx` is stock CCTNS and was
  confirmed by **four independent scrapers** agreeing on a 10-column grid. Bihar's page is **not the
  same page**: it is a differently-built SCRB application with different controls and, decisively,
  **five extra columns Maharashtra does not have** (complainant, address, accused, incident_date, and
  a possible status). Treat Maharashtra as a lower bound on Bihar, not as a template for it.
- **Real rows were obtained — for Maharashtra.** `Atharvayadav11/mahagovscrapper` commits four JSON
  dumps harvested from `citizen.mahapolice.gov.in` on 2025-09-27. Fetched, parsed and saved to
  `tests/fixtures/`. **These contain no personal data** — `pipeline.fir.audit_columns()` returns `[]`
  against their column list, and `parse_date()` already handles their timestamp format.
- **Answer on disposal: no. Nowhere.** Not in Maharashtra's observed rows, not in Bihar's declared
  columns as the repo's README and CLAUDE.md state them. A `status` string appears in the Bihar
  scraper's *positional column list* but is contradicted by the same repo's two prose descriptions,
  and the parser pads short rows with empty strings, so an over-declared column would be invisible.
  **Unresolved — do not build a disposal feature on it.**
- **Answer on location finer than station: no, for offence location.** Maharashtra publishes nothing
  below the police station. Bihar publishes an `address` — but that is the **complainant's residence**,
  not where the offence happened, and `FirRecord` is forbidden from carrying it anyway. The one place
  a genuine place-of-incident appears is the **sibling Missing Persons grid**, which has an
  `Incident Place` column in both states' stock software. The FIR grid does not.
- **The `coordinates` in two fixtures are not portal data.** The harvester geocoded the police-station
  *name* through Nominatim/Google/MapMyIndia. Every FIR at a station shares one point. Treating those
  as incident locations would be exactly the false-precision failure `_SPEC.md` warns about.
- **Bihar carries an occurrence date that Maharashtra lacks.** `incident_date` is declared distinct
  from `fir_date`. If real, that is the single most valuable field difference for a safety map, because
  it separates when the crime happened from when someone got around to reporting it.

---

## 1. Maharashtra — `citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx` — VERIFIED_LIVE

Verified in the strong sense: real harvested rows were fetched from `raw.githubusercontent.com`,
parsed, and the column names below are the keys those rows actually carry.

### The row, as actually observed

| # | Grid column (English header) | Key in harvested JSON | Real value |
|---|---|---|---|
| 0 | `Sr. No.` | `srNo` | `6` |
| 1 | `State` | `state` | `MAHARASHTRA` |
| 2 | `District` | `district` | `PALGHAR` |
| 3 | `Police Station` | `policeStation` | `BOISAR` |
| 4 | `Year` | `year` | `2025` |
| 5 | `FIR No.` | `firNumber` | `339` |
| 6 | `Registration Date` | `registrationDate` | `09/08/2025 18:07:00` |
| 7 | (FIR no. with year) | `firNoWithYear` | `0339/2025` |
| 8 | `Sections` | `sections` | `भारतीय न्याय संहिता (बी एन एस), 2023 - 303(2) ;` |
| 9 | (download control) | `hasDownloadButton` | `input[type="submit"][value="Download"]` → FIR PDF |

Columns 0–8 header text is quoted verbatim from `shivam-sharma0/extract-fir-data`, whose committed
`maharashtra_police_fir_data.csv` writes exactly
`Sr. No.,State,District,Police Station,Year,FIR No.,Registration Date,Sections`.
**That CSV is header-only — 78 bytes, zero data rows.** It corroborates the labels and nothing else.

### The five questions, answered for Maharashtra

| Question | Answer |
|---|---|
| Case status / disposal / closure? | **NO.** Ten columns, none of them a status. An FIR here is a registration event with no outcome attached, ever. |
| Act and section? | **YES**, fused into one free-text cell. Act name in Marathi/Devanagari, then ` - `, then comma-separated section numbers, then ` ; `. Multiple acts are separated by `;` and frequently by a literal newline. |
| Date **and** time? | **YES.** `dd/MM/yyyy HH:mm:ss`, e.g. `11/08/2025 17:52:50`. This is the *registration* timestamp — the moment the FIR was keyed in, not when the offence occurred. `pipeline.fir.parse_date` already handles it (returns `2025-08-11`). |
| Crime head? | **NO.** There is no NCRB head, no category, no description. Any crime head must be derived from the `sections` string — which means `pipeline/taxonomy.py` must parse **Devanagari act names**, not just IPC/BNS numbers. |
| Location beyond police station? | **NO.** State → District → Police Station, and that is the floor. |

### Act vocabulary actually seen (60-row fixture)

```
53  भारतीय न्याय संहिता (बी एन एस), 2023          BNS 2023
 6  मोटरवाहन अधिनियम, १९८८                        Motor Vehicles Act 1988
 3  महाराष्ट्र दारूबंदी अधिनियम,१९४९               Maharashtra Prohibition Act 1949
 2  अन्न सुरक्षा आणि मानके अधिनियम २००६            Food Safety and Standards Act 2006
 2  मुस्लिम महिला (विवाहाच्या अधिकाराचे...) २०१९   Muslim Women (Protection of Rights on Marriage) Act 2019
 1  भारतीय दंड संहिता १८६०                        IPC 1860  (pre-BNS residue, still appearing in 2025)
 1  महाराष्ट्र पोलीस अधिनियम, १९५१                 Maharashtra Police Act 1951
 1  अल्पवयीन न्याय (मुलांची काळजी व संरक्षण) २०१५  Juvenile Justice Act 2015
 1  अनुसूचीत जाती आणि अनुसूचीत जमाती ... १९८९      SC/ST (Prevention of Atrocities) Act 1989
 1  गुंगीकारक औषधीदव्‍य ... अधिनियम, १९८५          NDPS Act 1985
```

Two facts a parser must survive: **IPC and BNS coexist in the same feed in 2025**, and the Devanagari
digits (`१९८८`, `२००६`) are not ASCII. Note also the numeral inconsistency — `2023` and `२०१५` in the
same vocabulary. Section numbers themselves are ASCII throughout.

Three multi-act values, verbatim:

```
मोटरवाहन अधिनियम, १९८८  - 184 ; \n\nभारतीय न्याय संहिता (बी एन एस), 2023 - 125(a),125(b),281,324(4) ;
भारतीय न्याय संहिता (बी एन एस), 2023 - 3(5),324(4),329(1),352 ;
महाराष्ट्र पोलीस अधिनियम, १९५१ - 122C ;
```

### Form controls — Maharashtra

```
POST https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx
__VIEWSTATE / __EVENTVALIDATION / __PREVIOUSPAGE   replayed from a prior GET
__VIEWSTATEGENERATOR                               6F2EA376  (observed, hardcoded by one scraper)
ctl00$ContentPlaceHolder1$txtDateOfRegistrationFrom   dd/MM/yyyy
ctl00$ContentPlaceHolder1$txtDateOfRegistrationTo     dd/MM/yyyy
ctl00$ContentPlaceHolder1$ddlDistrict                 numeric code, e.g. 19408
ctl00$ContentPlaceHolder1$ddlPoliceStation            AJAX-repopulated by ddlDistrict postback
ctl00$ContentPlaceHolder1$txtFirno                    optional
ctl00$ContentPlaceHolder1$btnSearch                   'Search'
ctl00$ContentPlaceHolder1$ucRecordView$ddlPageSize    page size
ctl00$ContentPlaceHolder1$ucGridRecordView$txtPageNumber
paging: __EVENTTARGET=ctl00$ContentPlaceHolder1$ucGridRecordView, __EVENTARGUMENT=Page$N
results grid element id: ContentPlaceHolder1_gdvDeadBody   (sic)
legacy grid id seen in a 2023 scraper: grvPublishedFIRs
```

Two operational notes recorded by the scrapers and worth carrying forward:
- **The district postback wipes both date fields.** Three separate authors independently re-write the
  dates *after* selecting the district. One left a comment: `🔥 FORCE dates AGAIN (THIS IS THE CRITICAL PART)`.
- **The results grid is literally named `gdvDeadBody`.** Stock CCTNS software copy-pasted from the
  dead-bodies page. That is the clearest single piece of evidence that these pages are one codebase
  deployed per state, and it is why the Maharashtra layout is worth anything to a Bihar adapter.

No CAPTCHA is described by any of the four scrapers. `docs/INGESTION.md` rule 1 is therefore not
triggered for Maharashtra — but rule 2 is untouched: **nobody has read that portal's terms of use.**

---

## 2. Bihar — `scrb.bihar.gov.in/FIRiew.aspx` — CITED

Verified only in the weak sense: the **scraper source was fetched and read in full**; **no Bihar row
was ever seen**, by me or by anything I could fetch.

Source: `Kantvishu/Govt-of-Bihar-Data` — `scrape_scrb.py`, `README.md`, `CLAUDE.md`.
Raw URLs under `https://raw.githubusercontent.com/Kantvishu/Govt-of-Bihar-Data/main/`.

### Declared FIR columns

From `scrape_scrb.py`, `PAGES["fir"]["columns"]`, verbatim:

```python
["sno", "fir_no", "fir_date", "complainant", "address",
 "accused", "police_station", "sections", "district",
 "incident_date", "status"]
```

The same repo's `README.md` and `CLAUDE.md` both describe the columns in prose and **both omit
`status`**:

> **FIR**: FIR No, FIR Date, Complainant, Address, Accused, Police Station, IPC Sections, District
> Columns: fir_no, fir_date, complainant, address, accused, police_station, sections, district, incident_date

### The five questions, answered for Bihar

| Question | Answer |
|---|---|
| Case status / disposal / closure? | **UNRESOLVED, lean no.** `status` is the 11th entry in a positional list, contradicted by the repo's own two prose descriptions. `parse_table_rows` pads rows shorter than the column list with `''`, so an over-declared column produces a silently empty field rather than an error — exactly the failure mode that would leave a phantom name in the list. Independently, a web search of Hindi how-to guides describing the page named *Police Station, FIR No, FIR Date, Accused, Complainant Name, Incident Date* and **no status**. Treat as absent until a row is seen. |
| Act and section? | **SECTION YES, ACT PROBABLY NOT.** One column, `sections`; the README glosses it "IPC Sections". Whether the act is named in the cell, as Maharashtra does, is unknown. Bihar's own portal censorship note implies SLL cases are present, so an IPC-only reading would be wrong. |
| Date **and** time? | **TWO DATES, TIME UNKNOWN.** `fir_date` (registration) **and** `incident_date` (occurrence) — a genuinely better shape than Maharashtra's single timestamp. Whether either carries a time is unobserved. |
| Crime head? | **NO.** Same as Maharashtra: derive from `sections` or not at all. |
| Location beyond police station? | **Technically yes, semantically no.** `address` exists, but it is the **complainant's address** — `victim-residence`, not `offence-location`. It is also precisely what `docs/INGESTION.md` rule 3 forbids carrying, and `FORBIDDEN_COLUMN` in `pipeline/fir.py` already matches both `address` and `complainant`. Map it to nothing. |

**Bihar publishes personal data that Maharashtra does not.** Three of Bihar's eleven columns —
`complainant`, `address`, `accused` — are identifiers. `audit_columns()` will flag all three. This
confirms the premise of `docs/INGESTION.md` rule 3 from an independent source.

### Form controls — Bihar

```
GET  https://scrb.bihar.gov.in/FIRiew.aspx          -> harvest __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION
POST https://scrb.bihar.gov.in/FIRiew.aspx
  __EVENTTARGET / __EVENTARGUMENT / __LASTFOCUS      empty
  ctl00$ContentPlaceHolder1$ddlDistrict              numeric code (see below)
  ctl00$ContentPlaceHolder1$ddlPoliceStation         '' — leaving it empty returns the whole district
  ctl00$ContentPlaceHolder1$optionsRadios            'radioPetioner'  (search-by mode)
  ctl00$ContentPlaceHolder1$txtfDate                 date from
  ctl00$ContentPlaceHolder1$txttDate                 date to
  ctl00$ContentPlaceHolder1$btnSearch                'Search'
results: a single <tbody> of <tr>/<td>. NO PAGING CONTROL — the whole district comes back at once.
```

`optionsRadios` is a radio group; `radioPetioner` is the only value observed. A web search of guide
pages describes the same page as offering search by **Complainant's Name / FIR Number / Accused's
Name**, which is consistent with three radio values. The other two are unknown.

**Session cookies are required. No login. No CAPTCHA** — per the repo's explicit note
("Session cookies required but no login/captcha needed"). If that holds, `docs/INGESTION.md` rule 1
does not stop a Bihar adapter. It should still be re-checked by `probe()`, because that claim is
six months old and is somebody else's.

### District dropdown — 50 options, read verbatim from the scraper

38 revenue districts plus 12 special units. Reproduced because it is the single most reusable artefact
here and it is not guessable:

```
 1 Arariya      2 Arwal       3 Aurangabad   4 Banka        5 Begusarai
 6 Bhabhua      7 Bhagalpur   8 Bhojpur      9 Buxar       10 Darbhanga
11 East_Champaran            12 Gaya        13 Gopalganj   14 Jamui
15 Jehanabad   16 Katihar    17 Khagaria    18 Kishanganj  19 Lakhisarai
20 Madhepura   21 Madhubani  22 Munger      23 Muzaffarpur 24 Nalanda
25 Nawada      26 Patna      27 Purnia      28 Rohtas      29 Saharsa
30 Samastipur  31 Saran      32 Sheikhpura  33 Sheohar     34 Sitamarhi
35 Siwan       36 Supaul     37 Vaishali    38 West_Champaran
39 Bagaha      41 Naugachhia
--- special units, excluded from DISTRICT_IDS by default ---
42 ATS         44 SVU        45 Rail_Muzaffarpur          46 Rail_Jamalpur
48 Rail_Patna  49 Rail_Katihar             50 VIB         51 Economic_Offence_Unit
52 CID_Patna
```

Note `40`, `43` and `47` are absent from the mapping, and that Bagaha (39) and Naugachhia (41) are
police districts rather than revenue districts — the same revenue/police mixing that
`state-police-east-ne.md` flags for *Crime in Bihar*'s "48 districts/units". A district join will not
be clean.

### Server behaviour, as reported by the one person who has actually run this

Recorded verbatim from `CLAUDE.md` because it changes how the adapter must be built:

- **"Date filter broken on FIR page — returns all data regardless of date params."** If true, there is
  no incremental fetch: every run pulls the district's entire history. That makes polite, rate-limited
  daily refresh essentially impossible and pushes Bihar toward one-off bulk snapshots.
- **OutOfMemoryException** on large districts — the server renders every result at once. Workaround is
  date-range chunking, which is in tension with the broken date filter above.
- **Photo-rendering crash** (`Cannot access a closed Stream`, invalid S3 virtual path) — affects the
  arrest/dead-bodies pages, which embed photos; 11 of 40 arrest districts and 10 of 40 dead-body
  districts failed outright.
- **DNS instability** — "server frequently goes offline after heavy querying."

Claimed volumes: **FIR 92,424 rows / 40 districts / 0 errors / 2016–2026**, with 12 districts holding
only 2023+ data. Arrest 277,557 rows / 28 of 40 districts. Dead bodies 51 rows. Missing persons partial.

### Sibling pages on the same Bihar host

| Page | Columns as declared |
|---|---|
| `FIRiew.aspx` | as above |
| `ArrestDetail.aspx` | sno, entry_date, fir_no, fir_date, arrested_person, father_husband_name, age, gender, arrested_ps, **po_name**, **po_designation**, trial_section, photo |
| `deadbodies.aspx` | sno, entry_date, dd_no, dd_date, person_name, height, face, complexion, age, marks, built, dress, found_date, police_station, district, notes, photo |
| `MissingPersons.aspx` | sno, entry_date, fir_no, fir_date, missing_person, father_name, address, police_station, missing_place, missing_date, age, marks, district, photo |

`ArrestDetail.aspx` carries **arresting-officer name and designation**; the repo reports 35,719
uniquely identifiable officers and 4,977 with traceable transfers. That is a real re-identification
surface on a public portal. It is out of scope for this map and should stay out of it —
`FirRecord` cannot hold it and should not gain the ability.

`MissingPersons.aspx` has `missing_place` — a place finer than the station. The FIR page does not.

---

## 3. Harvested Maharashtra dumps — `Atharvayadav11/mahagovscrapper` — VERIFIED_LIVE

Four JSON files, all fetched and parsed on 2026-09-20.

| Raw URL (all under `https://raw.githubusercontent.com/Atharvayadav11/mahagovscrapper/main/`) | Bytes | Rows | Unique | Districts |
|---|---|---|---|---|
| `fir-data-2025-09-27T07-41-06-426Z.json` | 209,602 | 500 | **10** | NASHIK CITY |
| `fir-data-2025-09-27T07-41-06-426Z-with-coords.json` | 245,102 | 500 | **10** | NASHIK CITY |
| `fir-data-2025-09-27T08-44-14-002Z.json` | 9,525 | 20 | 20 | NASHIK CITY, PALGHAR |
| `fir-data-2025-09-27T08-47-21-029Z.json` | 29,239 | 60 | 60 | NASHIK CITY, PALGHAR |

**The 500-row files contain 10 unique FIRs repeated 50 times.** Every row is `srNo` 1–10 from
`ADAGAON POLICE STATION`. The paging loop re-fetched page 1 fifty times — the repo contains a
`check-duplicates.js`, so the author knew. Anyone quoting "500 Maharashtra FIRs" from this repo is
quoting a bug. Deduplicate on `(district, policeStation, firNoWithYear)`.

`hasDownloadButton` is `false` on all 580 rows, although two other scrapers locate and click a
per-row `Download` submit button on the live page. The flag is a parser artefact of scraping the
AJAX `updatePanel` fragment, not evidence that the PDF is missing.

No `LICENSE` file, no `README.md`. **Licence unstated — default all-rights-reserved.**

---

## 4. The stock-software claim, tested

| State | Citizen portal FIR endpoint | Stack | Same page as Maharashtra? |
|---|---|---|---|
| Maharashtra | `citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx` | ASP.NET WebForms | reference |
| Uttarakhand | `policecitizenportal.uk.gov.in/Citi/firSearch.aspx` | ASP.NET | likely — `.aspx`, same shape |
| Assam | `assampolice.assam.gov.in/citizen/FIRDownload.aspx` | ASP.NET | likely |
| Odisha | `citizenportal-op.gov.in/citizen/FIR_Copy.aspx` | ASP.NET | likely |
| MP | `citizen.mppolice.gov.in/CitizenLogin.aspx?CtznService=13` | ASP.NET, **login-gated** | unknown |
| Haryana | `haryanapolice.gov.in/ViewFIR/FIRStatusSearch?From=...` | ASP.NET MVC | **different** — and note the name *FIRStatusSearch* |
| Chhattisgarh | `search.cgpolice.gov.in/CCTNS_Citizen_Portal/Citizen_Login.jsp` | **Java/JSP**, login | **different stack** |
| Andhra Pradesh | `citizen.appolice.gov.in/jsp/citizenLogin.do?...viewfirlink` | Java/Struts, login | different stack |
| Telangana | `tspolice.gov.in/jsp/citizenLogin?method=viewLoginForm` | Java/JSP, login | different stack |
| Jharkhand | `citizen.jhpolice.gov.in/citizen/login.htm` | Java, login | different stack |
| Himachal / Arunachal | `citizenportal.{hppolice,arunpol}.gov.in/citizen/login.htm` | Java, login | different stack |
| Tamil Nadu | `eservices.tnpolice.gov.in/CCTNSNICSDC/CitizenFIRView?0` | Java | different stack |
| Karnataka | `ksp.karnataka.gov.in/firsearch/en` | modern web app | different |
| Goa | `citizen.goapolice.gov.in/web/guest/firdocsearch` | Liferay portal | different |
| Delhi | `delhipolice.gov.in/viewfir` | — | different |
| Bihar | `police.bihar.gov.in/` (portal); FIRs at `scrb.bihar.gov.in/FIRiew.aspx` | ASP.NET WebForms | **separate SCRB app, not the citizen portal** |

Roster source: `Mehul-Rathva/osint-toolkit-central-main` → `src/pages/StateFirPortals.tsx`, fetched
2026-09-20. 27 states listed. These are **URLs transcribed from a third-party OSINT toolkit; none was
opened** — they are leads, not verified endpoints.

**Verdict on the brief's key hypothesis.** It is half right. "CCTNS citizen portal" is a *programme*,
not one binary: roughly a third of states run the ASP.NET WebForms variant Maharashtra runs, and the
rest run Java/JSP builds behind a login. Bihar is in neither camp — SCRB Bihar is its own ASP.NET
application on a different host from the state's citizen portal. So the Maharashtra layout tells us
what a published-FIR grid *minimally* contains, and the confirmation that **no ASP.NET deployment
anywhere carries a disposal field** is real and useful. It does not give us Bihar's column names.

---

## Granularity reality check

| | Maharashtra (observed) | Bihar (declared) |
|---|---|---|
| Finest geography | police station | police station (+ complainant address, unusable) |
| Offence location | **not published** | **not published** |
| Time resolution | date **and** second | date; time unknown |
| Occurrence vs registration | registration only | **both** (`incident_date`, `fir_date`) |
| Outcome / disposal | **absent** | absent-or-phantom |
| Crime classification | act + section string only | section string only |
| Cadence | daily | daily, but date filter reportedly broken |
| Personal data in row | **none** | complainant, address, accused |

`location_semantics` for both: **`reporting-office`**. This is the station that registered the FIR.
It is not where the crime happened, and no field in either feed makes it so.

---

## What I could NOT establish

Stated plainly, because guessing any of these would be worse than the gap:

1. **Bihar's actual rendered column headers.** Everything in §2 is one developer's Python variable
   names. I never saw the page. The English or Hindi labels the grid renders are unknown.
2. **Whether Bihar's `status` column exists at all**, and if it does, what values it takes and whether
   it means case disposal, upload status, or something else entirely. The evidence is internally
   contradictory *within a single repository*.
3. **Whether Bihar's `fir_date` / `incident_date` carry a time**, and in what format.
4. **Whether `View_FIR.aspx` and `FIRiew.aspx` are the same page**, two pages, or one redirecting to
   the other. `docs/INGESTION.md` and `BiharScrbSource.path` name the first; every scraper names the second.
5. **Whether Bihar's `sections` cell names the act**, or only bare section numbers.
6. **A committed Bihar FIR row, anywhere.** The one repo that has 92,424 of them gitignores `data/`.
   I searched code, filenames and CSV contents; there is nothing. **This is the biggest gap.**
7. **Bihar's `optionsRadios` values other than `radioPetioner`.**
8. **Maharashtra district codes beyond `19408`.** The dropdown is a postback; nobody committed the map.
9. **Terms of use and robots.txt for either portal** — both hosts unreachable. `terms_reviewed` must
   stay `False`. `docs/INGESTION.md` rule 2 is unsatisfied and this dossier does not satisfy it.
10. **Whether Bihar's repository presents a CAPTCHA today.** One six-month-old third-party claim that
    it does not is not a substitute for `probe()`.

## Phase 2 recommendations

1. **Fix the endpoint before anything else.** Point `BiharScrbSource.path` at `/FIRiew.aspx` and keep
   `/View_FIR.aspx` as a documented alias to check. One minute of work; currently the adapter would
   probe the wrong URL.
2. **Run `probe()` from an Indian network.** The three things it must settle: CAPTCHA present y/n, the
   real rendered headers, and whether an 11th `status` column exists.
3. **Write the parser against the Maharashtra fixtures now.** They are committed, they are real, they
   exercise Devanagari act names, mixed IPC/BNS, multi-act cells, the `dd/MM/yyyy HH:mm:ss` timestamp,
   and a genuine pagination-duplication bug. That is most of the parser's difficulty, available today
   without touching a live site.
4. **Extend `pipeline/taxonomy.py` to Devanagari act names** before any CCTNS ingestion. `parse_sections`
   against `भारतीय न्याय संहिता (बी एन एस), 2023 - 3(5),303(2) ;` is the test to write.
5. **Add Maharashtra as a source in its own right.** It is cleaner than Bihar on the dimension that
   matters most for publishing: it contains no personal data at all.
6. **Do not chase the Java/JSP states.** Ten-plus of them put FIR search behind a login. That is
   `access: login`, and the route is RTI.

## Seed Leads (unconfirmed but probably real)

- **The 92,424-row Bihar FIR CSV exists on one person's disk.** `Kantvishu` scraped it in March 2026
  and gitignored it. A polite issue or email asking for the *header row and one redacted sample row* —
  not the dataset — would close gaps 1, 2, 3 and 5 at once, at zero load on the SCRB server. Highest
  value-per-effort action in this dossier.
- **Bihar's police-station dropdown** is AJAX-populated from `ddlDistrict` and would yield a full
  station roster for all 38 districts — the join key `pipeline/geography.py` needs.
- **`hasDownloadButton` implies a per-row FIR PDF** on both portals. Bihar's FIR text is reported
  elsewhere to be scanned Hindi images. If Maharashtra's PDFs are digital text, they may carry the
  place of occurrence that the grid omits — the only identified route to `offence-location`.
  Rule 4 (politeness) makes bulk PDF fetching a poor idea regardless.
