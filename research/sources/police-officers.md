# Police Officers and Station Contact Data — Can We Name the SHO?
_Agent: police-officers · Researched: 2026-09-20 · Entries: 4 verified / 18 total_

> **Scope.** Two questions, both answered here. **(A)** Is per-station officer-in-charge data
> (name, rank, phone, email) obtainable in India, and Bihar in particular? **(B)** Should our map
> display it, and in what form? Part B ends with a recommendation that is meant to be
> implementable as a schema constraint, not a policy sentence.
>
> **THIS IS NOT LEGAL ADVICE.** It extends `legal-ethics.md` and inherits its verification
> discipline and its caveat that statutory citations graded `CITED`/`UNVERIFIED` must be checked
> against primary text before launch.

## Research conditions (read before trusting a citation)

| constraint | effect |
|---|---|
| **All `*.gov.in` / `*.nic.in` hosts blocked** (`EGRESS_BLOCKED`) | Could not open `police.bihar.gov.in`, `scrb.bihar.gov.in`, `homeonline.bih.nic.in`, `delhipolice.gov.in/kyps`, `hyderabadpolice.gov.in/know_your_ps.html`, `jhpolice.gov.in/police-station`, `bprd.nic.in` |
| **`data.police.uk` blocked** | The police.uk answer is verified against a **verbatim mirror of the official API docs** committed to GitHub, plus two independent client libraries. Not against the live site. |
| **All OSM hosts blocked** — `openstreetmap.org`, `wiki`, `taginfo`, `overpass-api.de`, `download.geofabrik.de` all returned connection failure | OSM coverage answered from a fetched third-party harvester's own documented findings, not measured directly |
| **`api.github.com` REST is repo-scoped** in this session; `search/code` **is** available via the GitHub MCP tool; `raw.githubusercontent.com` is open; **GitHub *release assets* return 404/403** | Could read any repo file, could not download release assets (so the Bihar i-Bhugoal jurisdiction polygons could not be attribute-profiled) |
| Indian news, `indiankanoon`, `livelaw`, `scconline`, `casemine`, `lawschoolpolicyreview`, `dpdpa.com`, `play.google.com`, `scribd` — all blocked | Several facts below are graded `CITED` from search-result extracts: the URL is real and the extract is quoted, but the page was not opened |
| Reachable and used: **`en.wikipedia.org`**, **`raw.githubusercontent.com`**, **GitHub code search**, **WebSearch result extracts** | |

**Verified this session by actually fetching and parsing the bytes (`VERIFIED_LIVE`):**
the national police-station point layer and its exact 8-field schema (16,459 stations, Bihar 929);
the **Bihar Home Department's own thana data model**, field by field, from the published source of
its official Android client; the police.uk `/people` response shape from a mirrored copy of the
official docs; and the OSM harvester's self-declared coverage.

---

## Executive summary

- **Yes, the SHO record exists in Bihar, in exactly the shape we would want, and I found its
  schema.** The Bihar Home Department runs **Grih Darshan** (package `bih.nic.in.policesoft`),
  whose open-source Android client is on GitHub. Its `UpdateThanaModel` / `PoliceUser_Details`
  entities carry, per thana: `Thana_Name`, **`SHO_Name`**, **`SHO_Mobile_Num`**,
  **`Email_Address`**, `Landline_Num`, `Thana_Address`, `Latitude`, `Longitude`, `Range_Code`,
  `Police_Dist_Code`, `Sub_Div_Code`, `PSCode`, plus the thana's **gazette notification number and
  date** and its **khata/khesra land parcel numbers**. It talks SOAP to
  `http://homeonline.bih.nic.in/GrihDarshan/grihdarshanwebservice.asmx`.
  **This is the single most valuable find in this dossier** — not because we can call the service
  (we cannot: it is authenticated, encrypted per-field, and on a blocked `.nic.in` host) but
  because it lets an RTI name the exact record, the exact fields, and the exact system, which is
  the difference between a request that gets answered and one that gets a s.7(9) refusal.
- **No, it is not published as a dataset anywhere, and it is not mirrored anywhere reachable.**
  The best national artefact — `INDIA_POLICE_STATIONS.geojson` in `india-geodata`, which I
  downloaded and parsed — has **16,459 stations across 36 states/UTs (Bihar: 929, in 44 police
  districts, Patna 70)** and exactly eight properties: `state, state_cd, district, district_c, ps,
  ps_cd, latitude, longitude`. **No officer name. No phone. No email. Not one.** That is the
  ceiling of what is openly available at national scale.
- **OSM will not fill the gap.** An independent harvester (`AdItYa-1900/cyber-tools`) that actually
  ran the Overpass query documents its own result: *"India has on the order of 17,000 police
  stations. OSM has a few thousand... urban districts are well mapped, rural ones barely... There
  is no single public, machine-readable, complete national police station register."* Its extractor
  does pull `phone`/`contact:phone`, `operator` and `website` where tagged — so OSM can contribute
  a **station** phone, never an **officer**.
- **The typical published shape is a per-district HTML table or a "Know Your Police Station"
  form-lookup, not a file.** Confirmed by name for Delhi (`delhipolice.gov.in/kyps`), Hyderabad
  (`hyderabadpolice.gov.in/know_your_ps.html`), Jharkhand (`jhpolice.gov.in/police-station`,
  titled "Police Station Contacts") and the Passport Seva locator. All blocked here; all
  `CITED`. None is a bulk download; none is versioned; none carries an "as on" date.
- **The demand is already being met, badly, by third parties.** Delhi SHO/DO name-and-phone lists
  circulate on Scribd, `sahodar.in`, `kksaxenaassociate.in` and `legalfree.in`, several
  simultaneously claiming to be the "2026" list. That is the market signal *and* the warning: this
  data goes stale faster than anyone republishing it admits.
- **Churn is the decisive technical fact, and it is brutal.** *Prakash Singh v Union of India*
  (2006) Directive 3 prescribes a **minimum two-year tenure** for the SHO in charge of a police
  station. Reality: on **15 September 2026 — five days before this dossier — 20 SHOs were
  transferred in Patna district alone**, against a Patna establishment of ~70–75 stations. That is
  **roughly 27% of a district's station commanders replaced by one order on one day.** Bihar issued
  at least five separate police transfer orders between May and September 2026. Plan for
  **30–60% of the 929 Bihar SHO postings turning over per year**; an annually-refreshed name column
  is ~40% wrong before it is replaced. The station's *name, code and coordinates* change roughly
  once a decade. **Those two fields do not belong in the same table.**
- **police.uk names officers — but never next to a crime count, and the contact that works is the
  team's, not the person's.** `GET /{force}/{neighbourhood}/people` returns `name`, `rank`, `bio`
  and `contact_details`; in the official worked example the `contact_details` of **both** named
  sergeants are **`{}` — empty**. The usable contact lives one level up, on the *neighbourhood*:
  `"telephone": "101"`, `"email": "centralleicester.npa@leicestershire.pnn.police.uk"` — a **team
  mailbox and the national non-emergency number**. And the crime endpoints
  (`/crimes-street`, `/crimes-at-location`, `/outcomes-at-location`) contain **no officer field of
  any kind**. police.uk answers "who polices here" and "what happened here" through two separate
  surfaces that are never joined. That is the design we should copy.
- **DPDP is probably not our binding constraint here; staleness and defamation are.** RTI
  s.4(1)(b)(ix) obliges every public authority to publish **"a directory of its officers and
  employees"** suo motu. A police force is therefore *under an obligation under law to make that
  personal data publicly available*, which squarely engages **DPDP s.3(c)(ii)(B)** and takes the
  data outside the Act at source. Whether the exemption *travels to a downstream re-publisher* is
  still the open question flagged as Blocker 3 in `legal-ethics.md` — but for officer names the
  argument is far stronger than it is for FIR data. The real exposure is BNS s.356: publishing
  "SHO Ramesh Kumar" beside "Thana X: 412 FIRs" is an imputation about a named living person, and
  Exception 1 requires truth **and** public good — and the *imputation* (that he is responsible for
  the number) is not true, because the number is not a measure of him.
- **The safety argument for Bihar is weaker than it looks, and the corruption argument is stronger
  than expected — and they point the same way.** Bihar was declared **Naxal-free in February 2026**
  after the last armed Maoist surrendered in Munger, with zero Naxalite incidents reported in 2025;
  the 7 remaining LWE districts nationally are in Chhattisgarh, Jharkhand and Odisha, none in
  Bihar. So the insurgency-safety case is largely spent *for Bihar*. What replaces it is organised
  crime: sand-mafia henchmen attacked police and administrative officials **50+ times in eleven
  months**, and on **13 September 2026** a liquor-mafia attack in Samastipur injured a
  *thanadhyaksh* and several officers. Meanwhile an RTI by activist Shiv Prakash Rai found
  **50+ Bihar SHOs suspended, transferred or charged in three years for colluding with the sand and
  liquor mafias.** Both facts argue against *our* map naming anyone: the officers who deserve
  naming were surfaced by a disciplinary record and an RTI — not by a crime count — and the
  officers at risk are at risk from exactly the people a searchable, mapped, phone-number-bearing
  directory would serve best.
- **The user's actual question is "who do I contact about this area", and the station answers it
  completely.** A resident who wants to report, follow up or complain needs: which thana has
  jurisdiction, where it is, its landline, its official email, the ERSS-112 route, the online-FIR
  link, and who to escalate to (SDPO/SP office). None of that requires a human being's name.
  Every one of those fields is stable across transfers. **The name adds nothing the user needs and
  imports every risk in this document.**
- **Finest defensible officer granularity: the post, never the person.** Render
  *"Officer in charge (Thanadhyaksh) — [Station] PS"* as a **role** with the **role's** official
  contact. Where a state publishes the current incumbent on its own site, **deep-link to that page
  rather than copying the name** — the link is never stale, never ours to defame with, and never
  ours to take down.

---

## PART A — Is the data obtainable?

### A.1 What Indian state police actually publish

There is no national police-station directory carrying officer particulars. There are four
observed shapes, in descending order of usefulness to us:

| shape | example | machine-readable | carries SHO name? | carries phone? |
|---|---|---|---|---|
| **"Know Your Police Station" form lookup** — type a locality, get the covering station | `delhipolice.gov.in/kyps`; `hyderabadpolice.gov.in/know_your_ps.html`; Passport Seva `LocatePoliceStation` | 0–1 (JS/form-gated, one record per query) | **usually yes** | usually yes |
| **Per-district HTML contact table** | `jhpolice.gov.in/police-station` ("Police Station Contacts") | 2 (scrapeable table, no API) | **often yes** | yes |
| **PDF district directory / police manual annexure** | Puducherry police manual Ch. XXXII "Police Station and the Station House Officer" | 0–1 | sometimes | sometimes |
| **Internal geotagging app backing a SOAP service** | **Bihar Grih Darshan** (below) | 5 internally, 0 publicly | **yes, by design** | **yes — SHO mobile *and* email** |

The consistent properties: no "as on" date, no version history, no bulk export, no stable
identifier for the officer, and no commitment to update on transfer. A state that publishes an
SHO name is publishing a *snapshot with no timestamp* — which is precisely the artefact that is
dangerous to mirror.

**Statutory backdrop.** The SHO is not a rank but a **post** — the holder is an Inspector or
Sub-Inspector; several states call it Officer-in-Charge (OC), and West Bengal uses
Inspector-in-Charge (IC) in urban areas. The criminal procedure code (CrPC s.2(o), carried into
BNSS 2023) defines **"officer in charge of a police station"** as a statutory office with named
powers — which is exactly why the "public official acting in an official capacity" argument in
Part B is strong. `CITED`: the BNSS section number could not be confirmed against primary text;
`indiacode.nic.in` is blocked.

### A.2 Bihar in particular — the Grih Darshan find

`patnaapp/GrihDarshan_WithDatabase` (branch `master`) is the published source of the Bihar Home
Department's **Grih Darshan** app, Play Store id **`bih.nic.in.policesoft`**, described by the
publisher as *"GIS mapping of major utilities and offices under the home department"*. It is a
**thana census and geotagging tool used by the station itself**, not a citizen-facing directory.
Every field below was read directly from fetched source.

Service (from `web_services/WebServiceHelper.java`, verbatim):

```java
public static final String SERVICENAMESPACE = "http://homeonline.bih.nic.in/";
public static final String SERVICEURL1 = "http://homeonline.bih.nic.in/GrihDarshan/grihdarshanwebservice.asmx";
// commented-out alternates, also present in source:
//   https://www.fts.bih.nic.in/PoliceSoftwebservice.asmx      (namespace https://fts.bih.nic.in/)
//   http://10.133.20.196:8088/GrihDarshanWebservice.asmx      (internal)

public static final String RANGE_LIST            = "GetRangeList";
public static final String RANGE_LIST_Master     = "GetMst_RangeList";
public static final String Police_District_List  = "GetPoliceDistrictList";
public static final String SUB_DIVISION_List     = "GetSub_DivisionList";
public static final String GETMOBILE_OTP         = "Register_Thana_Signup";
public static final String PS_Registration       = "UpdateThana";
public static final String OUTPOST_Registration  = "Insert_Outpost";
public static final String INSERT_CONTACTS       = "Insert_Contact";
public static final String Authenticate          = "Authenticate";
public static final String Contact_Details       = "GetContactList_New";
public static final String Major_Util_Details    = "GetMajorUtilitiesList";
public static final String Office_List_Details   = "GetOfficesList";
```

Per-thana record (`entity/UpdateThanaModel.java`, and mirrored in `entity/PoliceUser_Details.java`):

```
Range_Code · PSCode · Police_Dist_Code · Sub_Div_Code · Thana_Name
SHO_Name · SHO_Mobile_Num · Email_Address · Landline_Num · Thana_Address
Thana_Notification_Avail · Notification_Num · Notification_Date
Land_Avail · Khata_Num · Kheshra_Num
Latitude · Longitude · Photo1 (Photo2) · App_Ver · Device_Type · Imei_Num
```

Outposts get the same treatment with `OutPost_Inch_Name` (outpost in-charge) alongside `SHOMobile`
and `SHOEmail` (`entity/OutPostEntry.java`). A parallel `Insert_Imp_Contacts` table geotags
`Officer_Name`, `email`, `Officer_Contact`, `Photo`, `Lat`, `Long` for post offices, hospitals,
schools and bus stands within the thana.

**What this is worth to us:**

1. It **proves the record exists**, in a named electronic system, with the exact fields. That
   defeats the standard s.7(9) "we would have to create a new record" refusal before it is made.
2. `Notification_Num` + `Notification_Date` are the **gazette notification constituting the thana**.
   That is the legal instrument that defines its jurisdiction — a far better RTI ask than "please
   send a shapefile", and it is a document the office indisputably holds.
3. `Khata_Num`/`Kheshra_Num` mean the Home Department geotagged the station building to a **cadastral
   parcel** — so precise coordinates for all 929 Bihar thanas exist inside government.
4. It is **not a source we can ingest.** `Authenticate` issues a token; every SOAP property is
   individually encrypted (`_encrptor.Encrypt(...)` with a per-call `RandomNo`) and gated by an
   OTP-verified SHO signup. Calling it would be an IT Act s.43(b)/s.66 problem under R6 of the
   risk register even if `.nic.in` were reachable. **Do not attempt it. Cite it in an RTI.**

Also on file for Bihar, from `state-police-east-ne.md`: the **SCRB public FIR repository**
(`scrb.bihar.gov.in/View_FIR.aspx`) publishes FIRs at police-station granularity daily — meaning
Bihar already publishes the *station* as the unit of account. It does not publish the SHO.

### A.3 Is any of it mirrored or harvestable?

**Checked, and the answer is no.** Every route was tested this session.

| route | result |
|---|---|
| **`india-geodata` → `data/police/stations/INDIA_POLICE_STATIONS.geojson`** | **Downloaded and parsed: 5,269,146 bytes, 16,459 features, 36 states/UTs.** Property keys across *all* features: `state, state_cd, district, district_c, ps, ps_cd, latitude, longitude`. **No officer field exists.** Feature ids are `police_station_mha.N` (MHA-derived, via `datta07/INDIAN-SHAPEFILES`). Bihar = **929 stations in 44 police districts**; Patna = 70; zero missing coordinates. |
| **`ramSeraph/indian_admin_boundaries` release `police` / `india-geodata` `police/jurisdictions`** | **Could not profile.** Release-asset downloads and `releases.atom` return 404/403 in this sandbox. Metadata fetched: 8 layers (TN, KA, AP, TG, **Bihar via i-Bhugoal**, RJ, Delhi, NCOG marine), temporal 2024, CC0, last updated 2024-08-15, release-only (`repo_files: false`). Whether the Bihar polygon carries any officer attribute is **UNVERIFIED** — on the evidence of every other state GIS layer, almost certainly not; these are jurisdiction geometries with PS name/code. |
| **OpenStreetMap `amenity=police`** | All OSM hosts unreachable. But `AdItYa-1900/cyber-tools/scripts/gen_police_stations.py` — a real harvester, fetched and read — extracts `phone`/`contact:phone`, `operator`, `website`, `addr:*` and documents its own coverage: *"India has on the order of 17,000 police stations. OSM has a few thousand... It is a finding aid, not an authoritative register."* It also notes OSM tags `addr:district` on **~3%** of these nodes, so it assigns district by point-in-polygon against Census-2011 boundaries instead. **OSM gives station phone/operator at low and urban-biased coverage; it never gives an officer.** ODbL share-alike applies. |
| **GitHub code search for harvested SHO directories** | Ten query formulations across CSV/JSON/code. **Zero hits** for any Indian SHO-name-and-phone dataset. The only `SHO_Name` field in public code anywhere is the Bihar app above and a handful of student CCTNS-clone projects with invented seed data. |
| **`data.gov.in` mirrors** | No crime or police resource carrying an officer column surfaced. Consistent with `open-data-portals.md`. |
| **Third-party republications** | Delhi SHO/DO lists on Scribd, `sahodar.in`, `kksaxenaassociate.in`, `legalfree.in`. Blocked here; `CITED`. Unlicensed, unsourced, undated, mutually inconsistent. **Not ingestible and not a model.** |

### A.4 Churn — the number that decides this

**De jure:** *Prakash Singh & Ors v Union of India* (2006), Directive 3 — officers on operational
field duty including *"Station House Officer in-charge of a Police Station shall have a prescribed
minimum tenure of two years unless it is found necessary to remove them prematurely following
disciplinary proceedings."*

**De facto, Bihar, this year:**

| date | order | scale |
|---|---|---|
| **15 Sep 2026** | **SHO reshuffle, Patna district** | **20 thanadhyaksh moved in one order** (~27% of Patna's ~70–75 stations, in a day) |
| 6 Sep 2026 | Home Dept, SDPO/DSP/ASP | 37 officers |
| 29 Aug 2026 | Home Dept, Bihar Police Service, Notification No. 10560 | 27 officers |
| 18 Aug 2026 | Home Dept, senior | 9 officers |
| 20 May 2026 | State govt reshuffle | 8 officers |

All `CITED` from search-result extracts; the underlying news pages are blocked.

**Planning estimate.** One 27%-of-a-district order in a single day, in a state that issued at least
five police transfer orders in five months, implies a per-posting hazard well above the two-year
statutory floor. Absent a measured figure (see RTI draft 5(g) below, which is designed to produce
one), **assume 30–60% annual turnover of the 929 Bihar SHO postings, and assume it is lumpy —
concentrated in orders that move a quarter of a district at once, often around elections, law-and-
order incidents and the transfer season.**

**Field half-life, which is the actual argument:**

| field | expected changes per decade | staleness cost if wrong |
|---|---|---|
| `ps_cd` (CCTNS station code) | ~0 | breaks joins — detectable |
| station name, coordinates | ~1 (thana bifurcation / new notification) | small map error — visible |
| station landline / official email | 1–3 | user cannot reach the station — recoverable |
| jurisdiction boundary | 1–2 (new thana carved out) | wrong polygon — serious, but correctable |
| **SHO name** | **~10–20** | **a named private individual is publicly associated with crimes in a place he does not police** |

A 929-row SHO table refreshed **annually** is roughly **40% wrong** by the time it is replaced, and
is wrong in the one way that is not recoverable: the error is an assertion about a named person.
Refreshed **quarterly** it is still ~10–15% wrong. There is no refresh cadence we can realistically
sustain against a SOAP service we cannot call, on a host we cannot reach, for 36 states.
**This is, on its own, sufficient to decide Part B.**

### A.5 Extending the RTI playbook, §5(b)

`rti-playbook.md` §5(b) asks for the station master list: name, CCTNS code, district/range,
address, coordinates, jurisdiction. It is the right ask. Three additions now supported by
evidence, plus two new drafts.

**Additions to 5(b), for Bihar (adapt the system name for other states):**

> 4. For each police station, the **official landline number(s), the official email address, and
>    the designated official mobile number attached to the post of Officer-in-Charge** (as distinct
>    from any personal number of the present incumbent).
> 5. For each police station, the **number and date of the notification by which the police station
>    was constituted**, and a copy of that notification.
> 6. The same particulars for each **Outpost (OP)** subordinate to each police station.
>
> I understand these particulars to be held in electronic form in the **Grih Darshan** application
> maintained by the Home Department (package `bih.nic.in.policesoft`, web service hosted at
> `homeonline.bih.nic.in/GrihDarshan/`), in which each police station has been registered with its
> address, contact particulars, geographic coordinates and constituting notification. What is
> sought is therefore a **copy of information already held in electronic form**, and s.7(9) is not
> attracted. I seek no personal information of any officer; if the record contains any such field,
> I request that it be **redacted and the remainder supplied**, as s.10 requires.

The final sentence is the operative one. It converts the one field that would otherwise sink the
request into a redaction exercise, and it is *also* our editorial position: we do not want the name.

---

#### New draft 5(f) — the post and its contact, without the person

> To: The Public Information Officer, Office of the Director General of Police, [State] /
> State Crime Records Bureau, [State]
>
> Subject: Request under the RTI Act, 2005 for the directory of offices and official contact
> particulars of police stations, published under s.4(1)(b)(ix)
>
> I request, for each police station in [State]:
>
> 1. The **designation** of the officer who holds charge of the police station (Station House
>    Officer / Officer-in-Charge / Inspector-in-Charge, as applicable in this State) and the
>    **rank** ordinarily posted to that charge.
> 2. The **official telephone number(s), official email address and official postal address** of
>    the police station.
> 3. The **name, designation and official contact particulars of the supervisory officer** to whom
>    a complaint against that police station is to be escalated (Sub-Divisional Police Officer /
>    Circle Officer and Superintendent of Police), by office, not by individual.
> 4. The date on which each of the above particulars was last updated.
>
> Section **4(1)(b)(ix)** of the Act requires every public authority to publish suo motu **"a
> directory of its officers and employees"**, and s.4(2) states the legislative intent that
> authorities provide information suo motu so that the public has minimum resort to the Act. This
> request therefore seeks compliance with an existing statutory obligation, in machine-readable
> form.
>
> **I do not seek the name of any individual officer.** I seek the particulars of the **office**.
> Accordingly no exemption under s.8(1)(j) arises. The request identifies no case and no
> investigation, so s.8(1)(h) does not arise.
>
> Electronic form (CSV or Excel) by email is requested.

*Why this is the right shape: it asks for precisely the data we intend to publish, and it asks for
it in a way that removes the exemption the DPDP amendment to s.8(1)(j) strengthened. It should be
filed together with 5(b), not instead of it.*

#### New draft 5(g) — measuring churn without asking for a single name

> I request, for each police station in [State], for the period 1 April 2021 to the date of this
> application:
>
> 1. The **number of officers who held charge** of that police station during the period.
> 2. For each such charge, the **date of taking over charge and the date of relinquishing charge**.
> 3. The **rank** of the officer holding charge on each such date.
>
> **No name, service number or personal particular of any officer is sought** — only the count of
> changes of charge and the dates. Accordingly s.8(1)(j) does not arise. The information is held in
> the station's General Diary / charge-handover register and in the establishment records of the
> district, and is a copy of information already held; s.7(9) is not attracted.
>
> I additionally request a statement of the **policy or standing order governing minimum tenure**
> of an officer in charge of a police station in this State, with reference to Directive 3 of the
> judgment of the Hon'ble Supreme Court in *Prakash Singh v Union of India* (2006).

*This is the highest-value new ask in the playbook. It yields a real churn distribution per
station — which is itself publishable, genuinely in the public interest, and a direct measure of
compliance with a Supreme Court directive — while containing not one personal data point. It also
answers, with evidence rather than estimate, the question A.4 had to approximate. And a station
whose charge changed nine times in four years is a finding about an institution, not an
accusation against a person.*

---

## PART B — Should it be published, and how?

### B.1 The case for naming

1. **The SHO is a statutory public office, not a private individual at work.** "Officer in charge
   of a police station" is a defined term in the criminal procedure code with powers that attach
   to the office — registering FIRs, arrest, investigation. Acts done in that capacity are done in
   public, in the public's name, funded publicly.
2. **The police already publish it, and are obliged to.** RTI **s.4(1)(b)(ix)** requires suo motu
   publication of "a directory of its officers and employees"; s.4(1)(b)(x) requires each officer's
   monthly remuneration. Police manuals require station display boards listing the station's
   officers and superiors. Several forces run public "Know Your Police Station" lookups that return
   the incumbent's name and number. **Nothing we would publish would be a disclosure.**
3. **DPDP 2023 most likely does not bite.** s.3(c)(ii)(B) excludes personal data made publicly
   available by a person "under an obligation under any law... to make such personal data publicly
   available". s.4(1)(b)(ix) is exactly such an obligation. Unlike FIR complainant data — where
   `legal-ethics.md` R3/R14 warn that we *create* new personal data by linking — an SHO directory
   is a flat copy of a mandated publication.
4. **Person-level transparency is what has actually produced accountability in Bihar.** An RTI by
   Shiv Prakash Rai surfaced **50+ SHOs** suspended, transferred or charged in three years for
   collusion with the sand and liquor mafias. That is not an abstraction.
5. **police.uk does name officers.** `GET /{force}/{neighbourhood}/people` returns `name`, `rank`
   and a free-text `bio`; `GET /forces/{id}/people` returns named senior officers. The UK's
   flagship transparency product decided naming was acceptable.

### B.2 The case against, and why it wins

**(a) The adjacency is the harm, and the data cannot support it.** Put "SHO: [name]" in the same
card as "Thana X — 412 FIRs, up 14%" and every reader draws one inference: *this man's area is bad,
therefore this man is bad at his job*. The inference is wrong for reasons this project has already
documented at length. FIR counts move with population, reporting propensity, the presence of a
highway or railway station, commercial footfall, and above all **policing effort** —
`legal-ethics.md` states it flatly: *"FIR counts measure police attention, not crime."* A station
that registers more FIRs may be the one doing its job. The map would systematically praise burking
and punish diligence.

**(b) It would corrupt the statistic we exist to publish — and there is direct precedent.** In
January 2014 the UK Statistics Authority **stripped police recorded crime of its National
Statistics designation**, having found that "the quality and consistency of the underlying data may
not be reliable"; HMIC's 2014 thematic inspection found under-recording of victim reports at a
level it called *"unacceptable"*. That happened in a jurisdiction with far less performance
pressure on individual station commanders than India has. India already has a name for the
pathology — **burking**, the active refusal or discouragement of FIR registration — which persists
despite *Lalita Kumari v Govt of UP* (2013) making registration mandatory on disclosure of a
cognizable offence, and which BNSS s.173(3)'s preliminary-enquiry window arguably widens. **Naming
the SHO beside his station's count hands every SHO in India a personal, reputational, searchable
reason to register fewer FIRs.** We would be degrading our own input data. This is the single
strongest argument in this dossier and it is not a legal one.

**(c) Defamation risk is real and asymmetric.** BNS s.356 (ex-IPC 499/500): truth alone is not a
defence; Exception 1 requires truth **and** public good, and *Subramanian Swamy v UoI* (2016)
upheld criminal defamation. The name is true; the *imputation carried by the adjacency* is not.
Per R4, the realistic harm is not losing — it is a private complaint under BNSS s.222 in a distant
magistracy and years of personal appearances. An individual officer is a legal person who can sue;
a locality (R4) is not. **Adding names converts our lowest-exposure risk into our highest.**

**(d) Officer safety, stated precisely rather than rhetorically.** For Bihar the insurgency framing
is largely obsolete — the state was declared **Naxal-free in February 2026**, zero Naxalite
incidents in 2025, and none of the 7 remaining LWE-classified districts nationally is in Bihar. But
the organised-crime exposure is live and current: sand-mafia attacks on police and administrative
officials **50+ times in eleven months**, and a liquor-mafia attack on **13 September 2026** in
Samastipur that injured a thanadhyaksh and several officers. A national, searchable, mapped,
mobile-number-bearing SHO directory, sorted by which stations are seizing the most, is a
**targeting aid** — and the people best resourced to use it are not residents. This argument does
*not* apply to a station landline on a public counter. It applies to a personal mobile number and a
name joined to enforcement activity.

**(e) Staleness makes it affirmatively false, not merely unhelpful.** See A.4. At 30–60% annual
turnover and no reachable refresh path, a name column is wrong about hundreds of people at any
moment — and each error is a false public statement about a named individual. **A stale SHO name
attached to crime figures is worse than none** — the brief's own formulation, and the evidence
supports it without qualification.

**(f) It does not serve the user's purpose.** "Who do I contact about this area" is answered by the
station. The person answering the phone is a duty officer, not the SHO, at most hours of most days.

### B.3 What police.uk actually does — verified, and more instructive than "it names officers"

Verified against a committed verbatim mirror of the official `data.police.uk` API documentation
(`EduardoTrevino/Fail-TaLMs/api_docs/OpenData/datapoliceuk.txt`, 56 KB), cross-checked against two
independent client libraries (`rkhleics/police-api-client-python` docs; `tjcain/ukpolice` Go
structs). `data.police.uk` itself is blocked in this sandbox.

**It names officers — on a separate surface.**

`GET https://data.police.uk/api/leicestershire/NC04/people` — official example response:

```json
[
  { "bio": "<p>I joined Leicestershire Police in 1997 ...</p>",
    "contact_details": {}, "name": "Andy Cooper", "rank": "Sgt" },
  { "bio": "<p>I am the Safer Neighbourhood Sergeant for the Cultural Quarter ...</p>",
    "contact_details": {}, "name": "Andy Price",  "rank": "Sgt" }
]
```

Documented fields of `contact_details`: `email`, `telephone`, `mobile`, `fax`, `address`, `web`,
`facebook`, `twitter`, `google-plus`, `forum`, `e-messaging`, `blog`, `rss`.
**In the publisher's own worked example, both named officers' `contact_details` are empty.**

`GET https://data.police.uk/api/forces/leicestershire/people` — senior officers — likewise returns
`name`, `rank`, `bio`, and in the official example a `contact_details` of exactly
`{"twitter": "http://www.twitter.com/ACCCLeicsPolice"}`.

**The contact that actually works is the team's, not the person's.** On the *neighbourhood*
resource:

```json
"contact_details": {
  "telephone": "101",
  "email": "centralleicester.npa@leicestershire.pnn.police.uk",
  "twitter": "http://www.twitter.com/centralleicsNPA",
  "facebook": "http://www.facebook.com/leicspolice"
}
```

A **team mailbox** and the **national non-emergency number**. Not a personal line.

**And the crime data contains no officer field at all.** The `/crimes-street/{category}` response
is `category, location_type, location{latitude, street{id,name}, longitude}, context,
outcome_status, persistent_id, id, location_subtype, month`. Same for `/crimes-at-location` and
`/outcomes-at-location`. There is **no key on which an officer could be joined to a crime**, by us
or by anyone.

**The design rule to copy, stated exactly:** police.uk answers *"what happened here"* and *"who
polices here"* through **two endpoints that share a geography and nothing else**. Naming is
confined to the second, where an officer is a **contact point and a face**, never a denominator.
Where person-level data does appear next to enforcement — stop-and-search officer-defined ethnicity
— it exists for **disproportionality analysis**, and `benchmark-product.md` already records the
downstream rule adopted by a consumer safety product: those fields are *"sensitive personal data
with no legitimate role in a safety score"* and were deliberately dropped. Same logic, same answer.

**What police.uk does *not* do:** it does not publish a national officer directory as a dataset; it
does not attach an officer to a crime record; it does not publish officers' personal mobile
numbers; it does not rank officers or areas by officer; and it does not guarantee the team list is
current — which is survivable there because no count hangs off the name.

### B.4 The DPDP position, stated for counsel

| question | position | grade |
|---|---|---|
| Is an SHO's name in an official directory "personal data"? | Yes. DPDP has no public-figure carve-out and **no sensitive-data category at all**. | `CITED` |
| Does s.3(c)(ii)(B) take it outside the Act? | **Probably yes at source.** RTI s.4(1)(b)(ix) is an obligation under law to publish a directory of officers; s.4(1)(b)(x) goes further, to remuneration. The police force is the "other person under an obligation". | `CITED` — s.3(c)(ii) text unverified against primary source |
| Does the exemption travel to us as downstream re-publisher? | **Open.** No Board decision, no judgment (`legal-ethics.md` Blocker 3). The argument is materially stronger here than for FIR data, because we would add nothing: no linkage, no inference, no new personal data. It weakens the moment we join the name to a count, because that **creates a new assertion about the person** that no public authority published. | `UNVERIFIED` |
| Does RTI still get us the name? | **Weaker than it was.** DPDP s.44(3) amended RTI s.8(1)(j), understood to remove the larger-public-interest override. Per R15, design every ask for offices and aggregates. Drafts 5(f) and 5(g) do exactly that. | `CITED` |
| Is there a journalism exemption to fall back on? | **No.** The DPDP Act has none, unlike GDPR Art. 85. Stated to counsel explicitly. | `CITED` |
| What is left once DPDP is cleared? | **BNS s.356** (truth alone insufficient), **staleness**, and the incentive effect in B.2(b). DPDP is not the binding constraint. | — |

---

## RECOMMENDATION

### Display this — the station, as an institution

For every police station we can place, render a **"Who polices this area"** panel, architecturally
separate from the statistics panel:

| field | source | stable? |
|---|---|---|
| Official station name + vernacular name | RTI 5(b) / state site / `INDIA_POLICE_STATIONS.geojson` | yes |
| CCTNS station code (`ps_cd`) | same | yes |
| District (police), sub-division, range | same | yes |
| Coordinates, postal address | same | yes |
| **Station landline(s)** | RTI 5(f) / state site / OSM `phone` | mostly |
| **Official station email** | RTI 5(f) / state site | mostly |
| **ERSS-112** and the state's online-FIR / e-FIR link | state portal | yes |
| **Escalation route by office**: SDPO/Circle Officer, then SP — office contacts, not individuals | RTI 5(f) item 3 | yes |
| **Post title only**: *"Officer in charge (Thanadhyaksh)"* | statutory | permanent |
| **Deep link** to the force's own "Know Your Police Station" page for this station | state site | n/a |
| Jurisdiction polygon where published (Bihar, TN, KA, AP, TG, RJ, Delhi) | `india-geodata` / `ramSeraph` | slow |
| "Contact details as on [date] · source [URL]" | ours | — |

### Do not display this

1. **No SHO name.** Not in the panel, not in a tooltip, not in a CSV export, not in an API
   response, not in the HTML source, not in a "credits" page.
2. **No officer's personal mobile number**, even where a state publishes one. Official landline and
   official email only. If a state's published "SHO mobile" is a personal number, it is not
   republishable by us at national scale next to enforcement data — B.2(d).
3. **No officer photograph, service number, or posting history.**
4. **Nothing person-level anywhere near a count.** Enforce at schema level, extending R14: the
   station-contact table and the crime-statistics table share `ps_cd` and **must not** contain an
   officer column. A migration that adds one should fail CI.
5. **No officer-keyed or station-ranked league table**, no "worst-performing station", no
   percentage-change callout beside any human name. R4 and R13 already forbid the area version;
   this extends it to the person.

### The one thing to build instead

**Publish the churn, not the incumbent.** RTI draft 5(g) yields, per station, the number of changes
of charge and their dates — with no name in it. *"This police station has had 9 officers in charge
since 2021; the Supreme Court's 2006 direction in Prakash Singh prescribes a minimum two-year
tenure"* is a real, defensible, genuinely novel public-interest finding about an **institution**.
It is the accountability story the SHO name only appears to offer, it cannot defame anyone, it
cannot be gamed by suppressing FIRs, it does not go stale, and as far as I can find **nobody in
India publishes it.** That is a better product than a name column, and it is obtainable.

### If counsel later clears naming anyway — the conditions

Only with **all** of: (a) role title plus official contact only, never a personal mobile or photo;
(b) an "as on [date] · source [URL]" stamp on the same line; (c) a refresh SLA of **30 days**, with
the field **auto-hidden** when the stamp ages past it rather than shown stale; (d) **physical
separation on the page** from every crime figure, with no shared card, table row or export column;
(e) an officer-name takedown route honoured within 36 hours, no questions asked; and (f) a
deep-link to the force's own page preferred over a copied value wherever one exists.

### The strongest argument against this recommendation

**Our most-needed user is the one this fails.** The moment an ordinary Indian citizen most needs
this map is when a police station **refuses to register their FIR**. *Lalita Kumari* compliance is
not enforced against institutions; it is enforced person by person, by naming the officer who
refused and escalating above him. The Bihar evidence cuts the same way: 50+ SHOs disciplined for
mafia collusion were surfaced by an **RTI naming individuals**, not by any institutional statistic.
A map that says "contact Thana X" to someone Thana X has already turned away is polite and useless.
Worse, the state itself publishes the name on a board at the station door and on its own website —
so we would be **more secretive about a public official than the police are**, and we would be that
way to protect ourselves, not the user. That is a real cost and it should be named honestly rather
than argued away.

**Why the recommendation still holds.** The fix for a refused FIR is an **escalation route** — the
SDPO and SP offices, the Police Complaints Authority, the online-FIR channel, the magistrate's
power to direct registration — all of which are **offices**, all of which are stable, all of which
we can publish, and all of which are *more* effective than a name that is 40% likely to be wrong by
the time it is read. We should build that escalation panel deliberately and well, and treat it as
the answer to this objection rather than a consolation for it. What we must not do is put a
person's name next to a number that cannot bear the weight of it.

---

## Granularity reality check

| what we want | what exists, reachable | what exists, unreachable | verdict |
|---|---|---|---|
| Station point + code, all-India | **16,459 stations, 8 fields, CC0-ish, one file** — `VERIFIED_LIVE` | — | **have it** |
| Station point + code, Bihar | **929 stations, 44 police districts, full coordinates** — `VERIFIED_LIVE` | BPRD DoPO authoritative count | **have it** (reconcile: Wikipedia says Patna Police has 75 stations, layer has 70) |
| Station jurisdiction polygon | 8 states/regions incl. Bihar, release-gated in this sandbox | 28 states have none published | **partial**, per `geospatial-boundaries.md` |
| Station landline / official email | OSM `phone` at low, urban-biased coverage | state "Police Station Contacts" pages (`.gov.in`, blocked) | **RTI 5(f), or scrape the state page with permission** |
| **SHO name / rank** | **nowhere** | Grih Darshan (auth+encrypted); "Know Your Police Station" lookups | **not obtainable at scale — and we should not want it** |
| **SHO mobile / email** | **nowhere** | Grih Darshan `SHO_Mobile_Num`, `Email_Address` | **not obtainable — and must not be published** |
| Changes of charge per station + dates | nowhere | station General Diary; district establishment records | **RTI 5(g) — the ask worth making** |

## Blockers and how to get past them

1. **Every state police host is blocked here.** The shapes in A.1 are `CITED` from search extracts.
   *Get past it:* one pass from an unblocked machine capturing, per state, the police-station
   directory page, its `robots.txt` and its Terms page, with dated screenshots into
   `research/_raw/tou/` — the same pass `legal-ethics.md` Blocker 2 already requires. Record
   whether each page shows an officer name and whether it carries an "as on" date.
2. **Grih Darshan is authenticated and encrypted.** Not a scraping target — it is an **RTI
   target**. Draft 5(b)+5(f) name it explicitly, which is what defeats s.7(9).
3. **GitHub release assets unreachable in this sandbox**, so the Bihar i-Bhugoal jurisdiction
   polygon's attribute table is unprofiled. *Get past it:*
   `gh release download police --repo ramSeraph/indian_admin_boundaries` from an unblocked machine
   and confirm (expected: no officer attribute).
4. **No measured churn figure exists publicly.** A.4 is an estimate from one district-day.
   *Get past it:* RTI 5(g), filed first in Bihar and one contrasting state.
5. **Two station counts disagree for Patna** (70 in the MHA-derived layer vs 75 per Wikipedia).
   Neither is authoritative. *Get past it:* BPRD *Data on Police Organisations* (state-wise police
   stations as on 01.01.20XX), or RTI 5(b) item 1.

## Seed Leads (unconfirmed but probably real)

- **`fts.bih.nic.in/PoliceSoftwebservice.asmx`** — a second, commented-out Bihar endpoint in the
  same source, under Finance/FTS rather than Home. Suggests an earlier or parallel PoliceSoft
  deployment. *Next step:* name both endpoints in the RTI; ask which system is the system of record.
- **Grih Darshan's `GetContactList_New` / `GetOfficesList` / `GetMajorUtilitiesList`** — the app
  also geotags hospitals, schools, post offices, bus stands, courts, jails and "major crime heads"
  per thana. If any of that is releasable, it is a **denominator and context layer for Bihar at
  police-station granularity**, which is scarcer than the crime data. *Next step:* a separate RTI.
- **State standing orders on SHO minimum tenure** post-*Prakash Singh*. Punjab legislated it
  (Punjab Police Act s.15: assured one year, extendable to three). Whether Bihar has an equivalent
  is unknown. *Next step:* RTI 5(g)'s second limb.
- **CIC decisions on s.4(1)(b)(ix) directory compliance.** If the Commission has ordered forces to
  publish officer directories, that is citable precedent for 5(f) — and also evidence for Part B
  that the data is treated as unambiguously public. *Next step:* the CIC decision review already
  flagged as the highest-value verification task in `rti-playbook.md`.
- **Bihar SCRB FIR repository as an SHO proxy.** `scrb.bihar.gov.in/View_FIR.aspx` publishes FIRs
  daily; an FIR carries the registering officer. **If it does, that is an inadvertent per-station
  officer feed — and a reason to check what we are ingesting before we ingest it.** *Next step:*
  inspect one FIR PDF's fields before Phase 2 ingestion, and confirm the hash-and-drop list covers
  the registering officer's name.

## Phase 2 recommendations

1. **Ingest `INDIA_POLICE_STATIONS.geojson` now.** 16,459 rows, eight clean fields, no personal
   data, national coverage, one HTTP GET. It is the spine of the "who polices here" surface and it
   carries zero risk. Reconcile `ps_cd` against CCTNS codes as they arrive from RTI 5(b).
2. **Write the schema constraint before the feature.** Station-contact table and crime-statistics
   table; shared key `ps_cd`; **no officer column in either**; a CI check that fails on a migration
   introducing one. Cheapest possible enforcement of this dossier's conclusion.
3. **File RTI 5(b)+5(f) together in Bihar**, naming Grih Darshan. Bihar is the right first state:
   it already publishes station-level FIRs, so station-level administrative data is not a novel
   concession, and this dossier hands the applicant the system name and field list.
4. **File RTI 5(g) in Bihar and one contrasting state.** It is cheap, it is unexempted, and it
   produces a publishable finding nobody else has.
5. **Build the escalation panel** (SDPO/CO → SP → Police Complaints Authority → online FIR →
   magistrate's power to direct registration), by office. This is the honest answer to the
   strongest objection against this recommendation, and it should ship with v1, not after it.
6. **Do the ToU/robots capture pass for state police-station directory pages** while doing it for
   FIR portals. If a state permits reuse of its station contact table, that is the cheapest route
   to landlines and emails and it avoids an RTI cycle.
7. **Check the Bihar FIR PDFs for the registering officer's name before volume ingestion**, and add
   it to the hash-and-drop list under R3 if present. This is the one place an officer name could
   enter our pipeline by accident.
