# RTI Acquisition Playbook
_Agent: rti-playbook (written directly by the orchestrating session) · Researched: 2026-09-19 · Entries: 0 verified / 14 total_

> **Provenance warning, stated up front and not to be lost.**
> Two subagent attempts at this dossier terminated on an API content filter, and by the
> time it was written the session's web-search budget was exhausted and the sandbox's
> egress policy was returning 403 for every `.gov.in` host including `rtionline.gov.in`
> and `cic.gov.in`. **This dossier is therefore written from model knowledge and has not
> been verified against a single primary source.** Every entry is `UNVERIFIED`.
>
> Treat it as a competent first draft to be checked, not as authority. Statutory section
> numbers, fee amounts, portal addresses and especially the post-2023 amendment position
> must each be confirmed against the bare Act and the current portals before anyone files
> anything or spends money. Nothing here is legal advice.

## Why this matters more than any other dossier

Every other dossier converges on the same wall. NCRB stops at the district, annually,
12–24 months late. `data.gov.in` has zero crime resources carrying a police-station
column. No state publishes police-station jurisdiction boundaries. Yet the data exists:
CCTNS holds FIR-level records across roughly 15,000–16,000 police stations in real time,
and every state police headquarters runs internal monthly crime reviews at station level
because that is how policing is actually supervised.

The gap between "exists" and "published" is exactly what the Right to Information Act,
2005 was written to close. For this project, RTI is not a fallback. It is the primary
acquisition channel for the resolution that makes the product worth building.

## 1. Mechanics

| item | position (unverified) |
|---|---|
| Statute | Right to Information Act, 2005 |
| Who may file | **Citizens of India only** (s.3). Not companies, not foreign nationals. |
| Application fee | ₹10, waived for BPL applicants |
| Copying charges | ~₹2 per A4 page; actual cost for electronic media |
| Response deadline | 30 days from receipt (s.7(1)); 48 hours where life or liberty is concerned |
| Deemed refusal | Silence past the deadline is treated as refusal and is appealable |
| First appeal | To the First Appellate Authority within the same public authority, within 30 days |
| Second appeal | To the Central or State Information Commission, within 90 days |
| Central online portal | `rtionline.gov.in` — central ministries and their subordinate bodies |
| State filing | Some states run their own portals; many are postal-only, requiring a court-fee stamp or Indian Postal Order |

**The citizenship point is a structural constraint on the project, not a footnote.** If the
portal is eventually run by a company or by someone based abroad, the company cannot file.
A named Indian citizen must sign every application, and at the scale contemplated here that
means recruiting a small group of citizen filers, or partnering with an existing Indian
civil-society organisation that already files at volume.

## 2. Which police bodies are reachable

Section 24 excludes the intelligence and security organisations listed in the Second
Schedule — central bodies such as the Intelligence Bureau, R&AW, the Directorate of
Revenue Intelligence, the Narcotics Control Bureau, the central armed police forces and
similar. Section 24(4) lets state governments notify their own equivalents.

Two things follow, and both need verifying state by state:

1. **State police forces as a whole are generally not exempt.** The exemptions are aimed at
   intelligence and security agencies, not at the district police who register FIRs. A State
   DGP office, a State Crime Records Bureau and a district Superintendent of Police are
   ordinarily public authorities answerable under the Act.
2. **Some states have notified their intelligence wings or special branches.** Where a state
   has done so, route the request to the SCRB or DGP office rather than to any unit with
   "intelligence" or "special branch" in its name, and confirm the state's own s.24(4)
   notification before filing.

Even for a notified body, the proviso to s.24(1) preserves access to information relating
to allegations of corruption and human rights violations, subject to the Commission's
approval and a longer timeline. That route is narrow and slow, and is not the basis for a
data pipeline.

## 3. Section 4(1)(b): ask them to comply, not to indulge you

Section 4 requires every public authority to publish seventeen categories of information on
its own initiative, and s.4(2) states the intent plainly: authorities should provide so much
information suo motu that the public has minimum resort to the Act.

Several of our targets sit squarely inside that duty — the particulars of the organisation's
functions, the norms it sets for discharging them, and the categories of documents it holds.
A state's monthly crime review is a document the organisation holds and uses to run itself.

Frame the first ask as a request for compliance with an existing statutory obligation, not as
a novel demand. It changes the tone of the reply and strengthens the appeal if refused.

## 4. The three refusals you will actually meet

**s.8(1)(h) — "would impede the process of investigation".**
The standard refusal for anything touching crime. The answer is that aggregate counts of
registered cases, by station and month and crime head, identify no investigation and impede
none; the position is routinely conceded once the request is visibly statistical rather than
case-specific. Never ask for anything about a pending case. Ask for counts.

**s.7(9) — form of access and "we would have to create a new record".**
The most important one to draft around. Authorities argue they need not compile information
that does not already exist in the requested shape. The counter is that CCTNS already holds
these records electronically and produces exactly these reports for internal supervision, so
what is sought is a copy of an existing output, not the creation of a new one. Say so in the
application, in those words. The better your evidence that the report already exists as a
routine internal artefact, the weaker the objection.

**s.8(1)(j) — personal information.**
Irrelevant if you ask for counts rather than case details, and you should draft so that it
cannot arise: state explicitly that no names, addresses, FIR numbers or any
person-identifying field are sought.

> **A material recent change that must be checked before relying on any older guidance.**
> The Digital Personal Data Protection Act, 2023 amended s.8(1)(j) of the RTI Act, and the
> amendment is understood to have removed the public-interest override and the
> "information available to Parliament" test, leaving a broader personal-information
> exemption. If that is the position in force, RTI has become materially weaker for anything
> touching personal data — which is precisely why our asks must be framed as aggregates,
> where the exemption has no purchase. **Verify the commencement status and the exact
> amended text before building any strategy on it.**

## 5. Five draft applications

These are drafted to pre-empt the objections above. Fill the bracketed fields. Keep each to a
single page; long applications invite s.7(9).

---

### (a) Police-station-wise monthly FIR counts — the core ask

> To: The Public Information Officer, Office of the Director General of Police, [State]
> / State Crime Records Bureau, [State]
>
> Subject: Request under the Right to Information Act, 2005 for station-wise monthly counts
> of First Information Reports registered
>
> Sir/Madam,
>
> I request the following information:
>
> For each police station in [State], the **number of First Information Reports registered
> per calendar month**, from [Month Year] to [Month Year], disaggregated by major crime head
> as classified in the Crime and Criminal Tracking Network and Systems (CCTNS).
>
> The information sought is **statistical and aggregate only**. I am **not** seeking the name,
> address, or any identifying particular of any complainant, accused, victim or witness; nor
> any FIR number; nor any information relating to any specific case or investigation.
> Accordingly no exemption under s.8(1)(j) arises, and as the request identifies no case or
> investigation, no exemption under s.8(1)(h) arises either.
>
> These figures are already held in electronic form in CCTNS and are, to my understanding,
> generated as routine monthly crime review reports for internal supervisory purposes. What is
> sought is therefore a **copy of information already held**, and not the creation of a new
> record. I respectfully submit that s.7(9) is not attracted.
>
> I request the information **in electronic form as a CSV or Excel file sent to the email
> address below**, which is the least burdensome form for your office and involves no
> photocopying. I am willing to pay any charges lawfully payable.
>
> Application fee of ₹10 is enclosed / has been paid online vide [reference].
>
> [Name] · [Full postal address] · [Email] · Citizen of India

---

### (b) The police station master list — the single most valuable ask

> I request, for [State]:
>
> 1. A complete list of all police stations, with: official station name, station code as used
>    in CCTNS, the district and police range/zone/commissionerate it falls under, and full
>    postal address.
> 2. The **geographic coordinates (latitude and longitude)** of each police station building.
> 3. The **jurisdiction of each police station**, in whatever form it is held — whether as a
>    textual description of boundaries, a list of villages, wards, revenue circles or census
>    codes falling within it, or a map or shapefile.
>
> This is administrative reference information about the organisation's structure. It contains
> no personal information and relates to no investigation. Publication of such particulars is
> in any event contemplated by s.4(1)(b) of the Act.
>
> Electronic form (CSV/Excel, and any map as a shapefile, KML or PDF) by email is requested.

*Why this one matters most: without it, station-level counts cannot be placed on a map at all.
Item 3 is the request that, if answered anywhere in India, unlocks the police.uk-style product.*

---

### (c) The state's own crime review, machine-readable

> I request a copy of the **annual crime review / annual crime statistics compilation** prepared
> by [State Crime Records Bureau / DGP Office] for the years [X] to [Y], **in the electronic
> spreadsheet form in which the underlying tables were prepared** (Excel or CSV), rather than as
> a scanned or printed document.
>
> Where the document is published, I request the direct link. Where only a PDF exists, I request
> the source spreadsheet from which it was typeset, which I understand to be held by the office.

---

### (d) Road accident records with coordinates

> To: The Public Information Officer, [State Transport Department / State Police (Traffic)]
>
> I request, in respect of road accidents recorded in the Integrated Road Accident Database
> (iRAD) / e-Detailed Accident Report (eDAR) system for [State] between [dates], the following
> **non-personal fields only**, as one row per accident:
>
> date; time; latitude; longitude; road name or highway number and chainage; accident severity
> (fatal / grievous / minor / property damage only); number of persons killed; number injured;
> vehicle types involved; the police station in whose jurisdiction it was recorded.
>
> I am expressly **not** seeking the name, address, licence number, registration number, or any
> other identifying particular of any person or vehicle involved. Please **redact or omit** any
> such field rather than refusing the request as a whole; s.10 of the Act requires partial
> disclosure where a record contains both exempt and non-exempt information.

*The s.10 severability point is the operative sentence. It converts "this file has personal data
in it" from a refusal into a redaction exercise.*

---

### (e) Emergency call volumes

> I request, in respect of the Emergency Response Support System (Dial 112) in [State], for the
> period [dates]: the **number of calls received per month**, broken down by emergency category
> as classified in the system, and by the finest geographic unit in which the system records
> them (district, police station, or ERSS zone — please state which).
>
> I also request a statement of **what geographic information the system captures** for each
> call (whether caller location coordinates, cell tower location, or the responding unit's
> jurisdiction), and the **median and 90th-percentile response times** by district.
>
> No caller identity, phone number or call content is sought.

*Ask (e) does double duty: even a refusal usually reveals what the system holds, which tells us
whether a future ask is worth making.*

---

## 6. Running this at scale

**Sequencing beats volume.** Do not file 36 state applications on day one. File (b), the station
master list, in three or four contrasting states first — one that already publishes a lot, one
that publishes nothing, one small UT. The replies calibrate the wording before it is spent
across the country.

**Cost is not the constraint.** At ₹10 per application, a 36-state campaign across all five
drafts is roughly ₹1,800 in fees plus copying charges and postage. The binding constraints are
the citizen-filer requirement, the calendar (30 days, plus 30 for first appeal, plus a Commission
backlog that can run to months or years for a second appeal), and the patience to work refusals.

**Budget for appeals as the normal path, not the exception.** A first-round refusal is
information: it tells you which objection that state reaches for, and the first appeal can be
drafted to answer it directly.

**Avoid the vexatious-applicant trap.** Many narrow applications to one office in quick
succession invites hostility and sometimes a s.7(9) refusal on cumulative burden. One
well-drafted application per office per cycle, clearly part of a stated public-interest project,
reads very differently from a scattergun.

**Precedent to study:** Praja Foundation has run a sustained, multi-year municipal RTI programme
in Mumbai and other cities and publishes the results as structured civic reports. Their method —
repeat the same standardised questions annually to the same offices, and publish — is the closest
existing model for what this project needs. Their output is also itself a source; the
civil-society dossier flags it as possibly India's finest non-government crime data.

## 7. Alternatives worth running in parallel

- **Assembly and parliamentary questions.** An MLA or MP can extract district-level tables that
  RTI officers resist, and answers are tabled publicly with annexures. The MHA dossier found that
  Rajya Sabha answers are already published as CSV on `data.gov.in` — a route with no fee, no
  30-day wait and no appeal.
- **A research MoU with one state police force.** Cheaper than fighting 36 refusals. Offer
  something back: a dashboard for their own supervision, in exchange for the aggregate feed.
- **Journalist partnership.** Newsrooms file RTIs routinely and have escalation paths.
- **Recommended first state: Kerala.** It already publishes per-police-station crime statistics
  pages, which means the data is already in a publishable form and already deemed publishable by
  the force — so the ask is for a machine-readable copy of something they have conceded, not for
  a new disclosure. Runner-up: Odisha, whose Bhubaneswar–Cuttack commissionerate already combines
  per-station pages with maps.

## Granularity reality check

| what we want | RTI can plausibly deliver | confidence |
|---|---|---|
| Station-month counts by crime head | Yes — existing CCTNS output | moderate |
| Station list with coordinates | Yes — administrative reference data | high |
| Station jurisdiction boundaries | Maybe, in text or village-list form; a shapefile is unlikely | low |
| Incident-level records with coordinates | No. Do not ask; it invites refusal and is not publishable anyway | — |
| Accident records with coordinates | Yes, with personal fields redacted under s.10 | moderate |

## Seed Leads

- **Which states have notified bodies under s.24(4)** — no consolidated list is known to exist.
  Compiling one is itself an RTI to each state's General Administration Department, and would be
  a publishable public good.
- **CIC decisions on crime statistics.** The Commission publishes its decisions and they are
  searchable. A systematic review would give citable precedent for each standard refusal. This
  was in scope for this dossier and could not be done without network access — it is the single
  highest-value verification task here.
- **The NCRB state-return proforma.** Flagged by the NCRB dossier: the blank form states send
  their returns on is the actual schema of Indian crime statistics, and shows which fields states
  report that NCRB then drops before publication. A short, targeted, high-yield ask.

## Phase 2 recommendations

1. Verify everything in this dossier against the bare Act and the live portals. It is unverified.
2. Compile the per-state filing table (portal, fee, payment method, postal address) — it could not
   be built without network access and is the operational prerequisite for everything else.
3. Identify the citizen filer(s). Nothing can be filed until this is settled.
4. File draft (b) in Kerala, Odisha, Maharashtra and one UT. Compare the replies.
5. Search CIC decisions for crime-statistics precedent before the first appeal is needed, not after.
