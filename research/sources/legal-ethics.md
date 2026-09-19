# Legal & Ethical Risk Register — India Crime Map

_Agent: legal-ethics · Researched: 2026-09-19 · Entries: 4 verified / 29 total_

> **THIS IS NOT LEGAL ADVICE.** It is a sourced risk register assembled by a research agent,
> intended to be handed to a qualified Indian advocate (ideally one with data-protection and
> media-law practice) for sign-off before launch. Statutory section numbers, case citations and
> dates below carry an explicit `verification` grade. Anything marked `CITED` or `UNVERIFIED`
> **must be checked against the primary text** before it is relied on. Several citations are
> from the agent's training corpus and could not be confirmed in this session — they are
> flagged individually and listed together in **Must-verify before launch**.

## Research conditions (read this before trusting a citation)

This session was materially constrained and I am recording it rather than papering over it:

| constraint | effect |
|---|---|
| **All `*.gov.in` / `*.nic.in` hosts blocked** by the organisation's egress proxy (`EGRESS_BLOCKED`) | Could not fetch `data.gov.in/Godl`, `ncrb.gov.in/robots.txt`, `ecourts.gov.in/robots.txt`, `indiacode.nic.in`, `egazette.gov.in`, `uppolice.gov.in` |
| **`indiankanoon.org`, `livelaw.in`, `scconline.com`, `prsindia.org`, `data.police.uk`, `web.archive.org` all blocked** | Could not read primary statute text or judgment text |
| **WebSearch budget exhausted (200/200)** mid-task | Only four search queries landed before the cap |
| Reachable: **`en.wikipedia.org` only** | Wikipedia is thin on Indian statutory detail; four facts were verified there |

**Verified this session (`VERIFIED_LIVE`):** BNS commencement 1 July 2024 and defamation = BNS s.356
(Wikipedia, *Bharatiya Nyaya Sanhita*); GODL-India grant/attribution wording (Wikipedia,
*Template:GODL-India*); NDSAP 2012 is a policy not a statute, and its negative list
(Wikipedia, *National Data Sharing and Accessibility Policy*); Survey of India is the certifying
authority for external boundaries on maps published by **private publishers** (Wikipedia,
*Survey of India*), and the 15 February 2021 geospatial liberalisation.

**Verified from search-result extracts (`CITED`)** — the URL is real and the extract is quoted,
but I could not open the page: GODL gazette notification 13 Feb 2017; Copyright Act s.52(1)(q)
and s.2(k); DPDP Rules 2025 three-phase commencement; BNS s.72 = IPC s.228A; the
right-to-be-forgotten case bundle.

---

## Executive summary

- **Nothing in this project is blocked by copyright.** India has **no sui generis database
  right** (unlike the EU), the Supreme Court rejected pure sweat-of-the-brow in *Eastern Book
  Company v D.B. Modak*, and Copyright Act s.52(1)(q)(iii)–(iv) expressly permits reproducing
  reports of government-appointed bodies and court judgments. The **numbers** in a NCRB volume
  are facts and are free. Do not mirror the PDF; extract the facts.
- **GODL-India is genuinely permissive and allows commercial use and derivative works.** The
  binding obligation is attribution with a DOI/URL/URI. But **GODL does not license personal
  data** — its exemptions clause carves personal data out of the grant, so it gives us no cover
  whatsoever for FIR-level records.
- **The DPDP Act's real gate is 14 May 2027, not today.** As of 2026-09-19 the Data Protection
  Board exists and complaints can be filed (since 14 Nov 2025), but the substantive Rules
  (notice, security, breach, retention, children, SDF) commence **14 May 2027**. We are building
  inside the grace window. Plan to the 2027 standard, not today's.
- **DPDP s.3(c)(ii) probably takes public FIR portals outside the Act — but it is not a licence
  to build person-level records.** The exemption attaches to data *made publicly available under
  a legal obligation*; the moment we link two FIRs to the same name, geocode a complainant's
  address, or retain what the portal later takes down, we are arguably creating new personal
  data the exemption never covered. **Crucially, the DPDP Act contains no journalism exemption**
  (unlike GDPR Art. 85 and unlike the 2018 Srikrishna draft). We cannot claim one.
- **The criminal-law provisions are the hard walls, and they bite on geography, not on names.**
  BNS s.72, POCSO s.23 and JJ Act s.74 prohibit publishing *any particular which may lead to
  identification* — POCSO s.23(2) expressly lists **"neighbourhood"** as such a particular. In a
  village or a 400-household ward, "rape, March 2026, Ward 17" identifies the victim. This is
  the single provision that determines the map's minimum aggregation unit.
- **Truth is not a defence to criminal defamation in India.** Exception 1 to BNS s.356
  (ex-IPC s.499) requires truth **and** that publication be for the public good, and *Subramanian
  Swamy v Union of India* (2016) upheld criminal defamation as constitutional. The realistic harm
  is not losing — it is a private complaint filed in a distant magistracy and three years of
  personal appearances by our directors.
- **A crime heat map in India is a caste and religion map, and no Indian law stops anyone from
  using it that way.** Indian residential segregation by caste and religion is well documented;
  the DPDP Act has **no sensitive-personal-data category at all** (caste, religion and health are
  just "personal data"), there is no fair-housing statute, no disparate-impact doctrine, and
  neither RBI nor IRDAI prohibits geographic discrimination in lending or underwriting. The legal
  risk here is near zero and the ethical risk is the highest in the project. That asymmetry is
  the reason mitigation has to be architectural rather than contractual.
- **FIR counts measure police attention, not crime.** Over-policing of Dalit, Muslim, Adivasi and
  denotified-tribe settlements means a raw FIR density map launders enforcement bias into
  apparent fact. Every caveat in `taxonomy-methodology` about the principal offence rule is
  secondary to this one.
- **Intermediary safe harbour is cheap to secure and easy to forfeit.** IT Act s.79 read with
  *Shreya Singhal* protects **third-party** content only, and only on a court/government order
  ("actual knowledge" was read down). Our own computed aggregates are first-party publishing with
  no safe harbour. Keep user-submitted reports architecturally and visually separate from our
  statistics, and ship a named Grievance Officer with a 24h-acknowledge / 15-day-dispose SLA.
- **The cheapest way to get shut down is the basemap.** Default OpenStreetMap, Mapbox and Google
  "international" tiles render the Jammu & Kashmir Line of Control as disputed. That depiction is
  unlawful in India. Survey of India certifies external boundaries on maps published by private
  publishers. This is a day-one tile-layer decision, not a launch-week one.
- **Finest defensible spatial granularity: police-station jurisdiction or ward, with a minimum
  population denominator and small-count suppression — never a point, never an address.**
  For sexual offences, POCSO and JJ matters: district, or not at all.

---

## Risk register

Likelihood and severity are 1–5 (5 worst). "Blocks v1" means the product cannot ship without the
mitigation in place.

| # | Risk | L | S | Statute / precedent | Concrete mitigation | Blocks v1 |
|---|---|---|---|---|---|---|
| R1 | Fine-grained geography identifies a rape / child victim by inference | 3 | 5 | BNS s.72, s.73; POCSO s.23(2) (expressly lists "neighbourhood"); JJ Act s.74; *Nipun Saxena v UoI* (2019) 2 SCC 703 | Sexual offences, POCSO and JJ categories rendered **at district level only**, with month suppressed to quarter. No point geometry for any category. No category+date+small-area triple. | **YES** |
| R2 | Basemap shows non-Survey-of-India national boundary (J&K / Aksai Chin / Arunachal) | 4 | 4 | Criminal Law (Amendment) Act 1961 s.2 (3 yrs / fine); DST *Guidelines for Geospatial Data* 15 Feb 2021; Survey of India certification mandate | Never render the national boundary ourselves. Use an India-served tileset (Mapbox/Google India endpoints) or SoI-published boundary layers. Legal review of the tile provider's India compliance before launch. | **YES** |
| R3 | We persist FIR-derived names/addresses without a DPDP lawful basis | 3 | 5 | DPDP Act 2023 ss.3(c)(ii), 4, 8, 17(2)(b); DPDP Rules 2025 (full force 14 May 2027); s.33 + Schedule (up to ₹250 cr) | **Hash-and-drop at ingest.** Names, phone numbers, complainant/accused addresses never reach durable storage. Store only: category, coarse geocode, date, source ID. Retention policy written before first scrape. | **YES** (architecture) |
| R4 | Criminal defamation complaint over "locality X is unsafe" | 3 | 4 | BNS s.356 (ex-IPC 499/500), **Exception 1 requires truth *and* public good**; *Subramanian Swamy v UoI* (2016) 7 SCC 221; BNSS s.222 private complaint | Rates with visible denominators and confidence intervals, never bare counts. Label everything "reported crime (FIRs), not crime". No rankings, no "most dangerous" lists, no "safety score". Named editorial standards page. | No (constrains copy) |
| R5 | The map functions as a communal / caste map | 4 | 5 | No Indian statute on point. Art. 15, Art. 17; SC/ST (PoA) Act 1989 (economic/social boycott provisions); Maharashtra Social Boycott Act 2016 | Minimum population denominator per rendered unit (propose 5,000). Suppress any cell with n < 10. Rate-not-count display. No ward-level counts. No ranking API. Published methodology stating FIR density measures policing. | **YES** |
| R6 | Scraping a police/court portal against its terms → unauthorised access claim | 3 | 4 | IT Act 2000 s.43(b) (downloading/copying data without owner's permission — civil compensation), s.66 (same acts done dishonestly/fraudulently — up to 3 yrs). **No CFAA-equivalent "authorisation" case law in India; exposure is untested.** | Obey robots.txt. Identifiable User-Agent with a contact URL. Hard rate limit (≤1 req/2s/host). Prefer RTI and official bulk feeds over scraping. Seek written permission from each state CID/SCRB. Document all of it. | No (needs counsel sign-off) |
| R7 | User-submitted reports are defamatory / obscene / identify a victim | 3 | 3 | IT Act s.79(2)–(3); *Shreya Singhal v UoI* (2015) 5 SCC 1 (s.79(3)(b) read down to court/govt orders); IT Rules 2021 r.3(1)(b), r.3(1)(d) (36h), r.3(2)(a) (24h ack / 15d dispose; 24h for intimate-image content); r.3A GAC | Named Grievance Officer with Indian address + email, published. Complaint workflow with SLA timers. Keep UGC on a visually and technically separate layer from our statistics, clearly attributed to users. | **YES if UGC ships** |
| R8 | Naming accused persons in pending matters → contempt | 2 | 4 | Contempt of Courts Act 1971 ss.2(c), 3, 4, 12; *Sahara India Real Estate v SEBI* (2012) 10 SCC 603 (postponement orders) | **Never publish the name of an accused, a complainant or a victim.** Category, geography, date, disposal status only. | No (eliminated by R-NN) |
| R9 | Right-to-be-forgotten / delisting demands after acquittal | 3 | 2 | *XXX v India Today Group*, 2024:DHC:5535 (Del HC); *SK v UoI*, 2023 LiveLaw (Del) 488; SC stay dated 24 Jul 2024 of Madras HC order re Indian Kanoon; Patiala House John Doe order, 28 Nov 2025 (Moser Baer) | Holding no names means there is nothing to delist. Publish a takedown route anyway; honour orders within 36h. | No |
| R10 | Downstream use for tenant screening, insurance pricing, lending | 4 | 4 | **No Indian prohibition.** RBI Digital Lending Guidelines and IRDAI underwriting rules contain no anti-redlining provision. DPDP has no Art.22-GDPR profiling right. | No address-level or building-level output, ever. No bulk/commercial API in v1. ToU prohibiting screening/underwriting/credit use (weak but evidentially useful). Rate display with uncertainty. | **YES** (no address-level scores) |
| R11 | GODL attribution failure, or relying on GODL to cover personal data | 2 | 3 | GODL-India (gazette-notified 13 Feb 2017); its exemptions clause excludes personal data and third-party IP from the grant | Per-dataset attribution block rendered with every derived view. Treat GODL as licensing **statistics only**; never cite it as authority for handling FIR personal data. | No |
| R12 | Copyright claim over reproduced NCRB / state police tables | 2 | 2 | Copyright Act 1957 ss.2(k), 17(d), 28 (60-yr Govt work term), **s.52(1)(q)(iii)–(iv)**; *Eastern Book Company v D.B. Modak* (2008) 1 SCC 1 (modicum of creativity); no sui generis DB right in India | Extract facts, not layout. Do not host mirrored PDFs at scale. Cite the source volume, year and table number. | No |
| R13 | Displaying counts rather than rates misstates risk and feeds R4/R5 | 4 | 3 | n/a — methodological | Rate-per-1,000-residents is the only default. Counts available only on explicit drill-down with a denominator shown alongside. | No (design rule) |
| R14 | Enrichment creates person-level records outside the s.3(c)(ii) exemption | 3 | 5 | DPDP Act s.3(c)(ii)(A)–(B) | **Never link records across FIRs at person level.** No entity resolution on names. No cross-source identity graph. Enforce at schema level, not by policy. | **YES** |
| R15 | RTI can no longer be used to obtain personal particulars | 4 | 2 | RTI Act s.8(1)(j) **as amended by DPDP Act s.44(3)** — the "larger public interest" override was deleted | Design all RTI requests (see `rti-playbook`) for aggregates and metadata, never for named individuals. | No |
| R16 | Hosting abroad triggers foreign-entity geospatial restrictions | 2 | 3 | DST Geospatial Guidelines 15 Feb 2021 — foreign-owned/controlled entities restricted on finer-than-1m data and may only serve via API to Indian end-users | Incorporate in India; host map tiles and geospatial processing in India. | No (check with counsel) |

---

## 1. Can we reuse government data?

### 1.1 GODL-India

`VERIFIED_LIVE` (partial, via Wikipedia `Template:GODL-India`) / `CITED` (gazette date).
The canonical page `https://www.data.gov.in/Godl` was **blocked by the egress proxy** this session.

Confirmed wording of the grant:

> "worldwide, royalty-free, non-exclusive license to use, adapt, publish … for all lawful
> commercial and non-commercial purposes."

Confirmed attribution obligation:

> "The user must acknowledge the provider, source, and license of data by explicitly publishing
> the attribution statement, including the DOI, URL, or URI."

Confirmed liability position: providers "are not liable for any errors or omissions".

Search extract (`CITED`, from `jk.data.gov.in/godl` and `smartcities.data.gov.in`) adds: gazette
notified **13 February 2017**; scope is "all shareable non-sensitive data available either in
digital or analog forms but generated using public funds by various agencies of the Government of
India"; the grant expressly covers "adapt, publish (either in original, or in adapted and/or
derivative forms), translate, display, add value, and create derivative works (including products
and services)".

**Product conclusions:**

1. **Commercial use is permitted.** Explicitly. A paid tier or an ad-supported map is within the
   licence.
2. **Derivative works are permitted**, including "products and services". A crime map built on
   GODL data is a licensed derivative.
3. **There is no share-alike.** Our derived layers need not be released under GODL.
4. **Attribution is the one real obligation** and it is per-dataset with a resolvable identifier.
   Build the attribution string into the ingestion record so it renders automatically.
5. **The exemptions clause is the trap.** The licence covers "shareable **non-sensitive**" data.
   `UNVERIFIED`: the canonical exemptions list (which I recall as excluding personal data,
   third-party IP, logos/emblems/insignia, military insignia, identity documents, and data
   exempt under RTI ss.8–9) must be read from the gazette text. **Whatever its exact wording,
   GODL is not authority for processing FIR-level personal data.** Do not let an engineer cite
   "it's GODL" for a dataset containing names.
6. `UNVERIFIED`: a no-endorsement clause (we may not imply official endorsement) and an
   accuracy/non-misleading clause are, to my recollection, in the licence. If so they interact
   directly with R4 and R13 — misrepresenting the data could be a **licence breach as well as**
   a defamation risk. Counsel must read the clause.

### 1.2 Copyright Act 1957 — is a government report reproducible?

`CITED` (Indian Kanoon, `indiankanoon.org/doc/648494/` — blocked this session).

- **s.2(k)** defines "Government work" as a work made or published by or under the direction or
  control of the Government, a legislature, or any court/tribunal/other judicial authority in
  India. Search extract confirms the judicial limb. `UNVERIFIED` for the executive limb.
- **s.17(d)** `UNVERIFIED`: Government is first owner of copyright in a Government work absent
  agreement to the contrary. **India has no US-style "edicts of government" public-domain rule.**
  A NCRB volume *is* copyrighted.
- **s.28** `UNVERIFIED`: term for Government works is 60 years from the start of the calendar year
  following first publication. NCRB volumes back to 1953 are therefore still in term.
- **s.52(1)(q)** — the exception that saves us. Search extract confirms limb (iv):
  reproduction or publication of "any judgment or order of a court, Tribunal or other judicial
  authority, unless the reproduction or publication of such judgment or order is prohibited by the
  court". `UNVERIFIED` for the other limbs, which I recall as: (i) matter published in any
  Official Gazette except an Act of a Legislature; (ii) an Act of a Legislature, subject to being
  published with commentary or other original matter; **(iii) the report of any committee,
  commission, council, board or other like body appointed by the Government, unless reproduction
  or publication of such report is prohibited by the Government.**
  - **Limb (iii) is the one that matters for NCRB.** If NCRB's *Crime in India* counts as the
    report of a like body appointed by Government, reproducing it is not infringement unless
    Government has prohibited it. Counsel must confirm whether a statutory Bureau's annual
    statistical volume falls within "committee, commission, council, board or other like body".

**Facts vs compilations — address this squarely.** Copyright subsists in *original literary
works* (s.13), not in facts. The number of burglaries in Kanpur in 2023 is a fact and nobody owns
it. What can attract thin copyright is the **selection and arrangement** of a compilation.

- *Eastern Book Company v D.B. Modak*, (2008) 1 SCC 1 (`UNVERIFIED` citation — could not fetch)
  is the controlling authority. The Supreme Court **rejected the pure "sweat of the brow"
  standard** and adopted a "modicum of creativity" / "skill and judgment" test: raw copy-edited
  judgments lack originality; editorial additions (headnotes, paragraph numbering reflecting
  editorial judgment) do attract copyright. Earlier sweat-of-the-brow database cases such as
  *Burlington Home Shopping v Rajnish Chibber*, 61 (1995) DLT 6, are doubtful after *Modak*.
- **India has no sui generis database right.** There is no Indian equivalent of the EU Database
  Directive 96/9/EC. A non-creative compilation of facts is not separately protected.

**Practical rule:** extract the numbers, rebuild our own schema and presentation, cite the
volume/year/table. Do not host bulk mirrors of the original PDFs and do not copy distinctive
editorial apparatus. This is a low-severity risk (R12) and should not slow the pipeline.

### 1.3 NDSAP 2012

`VERIFIED_LIVE` (Wikipedia, *National Data Sharing and Accessibility Policy*).

- Cabinet approval **9 February 2012**; notified **17 March 2012**.
- Scope: "All shareable non-sensitive data available either in digital or analog forms but
  generated using public funds by various ministries, departments, subordinate offices,
  organizations, and agencies."
- Negative list (confirmed): personal information; non-shareable/sensitive data; official symbols
  (names, crests, logos); data subject to IP rights; military insignia; identity documents; data
  that would violate **RTI Act s.8**.
- **Legal status: policy, not statute.** Not directly enforceable. Its operative teeth come from
  (a) the GODL, which *was* gazette-notified, and (b) RTI Act s.4(2)'s proactive-disclosure duty,
  which is statutory.
- Practical use: NDSAP + RTI s.4(2) together are the best argument in an RTI first appeal that a
  department *should already have published* a dataset in machine-readable form. See
  `rti-playbook`.

### 1.4 Terms of use and robots.txt — what I could and could not establish

**All four target hosts were blocked by the egress proxy.** I am recording them as `blocked`
rather than guessing, per `_SPEC.md` rule 3. These are Phase 2 must-checks:

| host | what to fetch | why it matters |
|---|---|---|
| `ncrb.gov.in` | `/robots.txt`, Terms & Conditions, Copyright Policy, Hyperlinking Policy | `UNVERIFIED`: NCRB almost certainly carries the standard NIC/GoI website content policy ("Material featured on this website may be reproduced free of charge … subject to the material being reproduced accurately and not being used in a derogatory manner or in a misleading context … the source must be prominently acknowledged"). If so, **the "not in a misleading context" condition is a contractual echo of R4/R13.** Must be read verbatim. |
| `ecourts.gov.in` / `njdg.ecourts.gov.in` | `/robots.txt`, Terms of Use, Disclaimer | `UNVERIFIED`: eCourts disclaimers are widely reported to restrict use to personal/informational purposes and to bar bulk/automated extraction. The existence of a thriving scraper ecosystem (`openjustice-in/ecourts`, Apify actors, Spider Cloud) is **evidence of practice, not of permission**. NJDG has an official API path — prefer it. |
| `data.gov.in` | `/robots.txt`, Terms of Use, GODL page | GODL governs the datasets; the site ToU governs the *site*. These are different documents and may conflict. |
| each state police portal | `/robots.txt`, FIR-search page ToU, CAPTCHA presence | The FIR portals are where personal data lives. See `state-police-*` dossiers. |

**The India-specific legal frame for scraping — this is more dangerous than the US position.**
There is no CFAA and no *hiQ v LinkedIn* in India. Exposure runs through the IT Act:

- **s.43(b)**: liability to pay compensation to a person who, without permission of the owner or
  person in charge of a computer resource, "downloads, copies or extracts any data, computer data
  base or information" from it. Note there is **no damage threshold** and no "dishonesty"
  requirement — s.43 is civil and strict-ish.
- **s.66**: if any act referred to in s.43 is done **dishonestly or fraudulently**, imprisonment
  up to three years, or fine up to ₹5 lakh, or both. `UNVERIFIED` on the fine figure.
- The open question — undecided in India — is whether a **browsewrap terms-of-use prohibition
  negates "permission of the owner"** for s.43(b). If it does, scraping a portal whose ToU bars
  automated access is a statutory civil wrong from the first request. **This is a genuine
  question for counsel and it is the most likely single reason a scraping pipeline gets a legal
  notice.**

Mitigation is behavioural and evidentiary: obey robots.txt even where you disagree with it,
identify yourself in the User-Agent with a contact URL, rate-limit hard, never defeat a CAPTCHA,
and above all **write to the SCRB/CID of each state asking for the data or for written permission
to collect it**. A refusal is useful; silence after a documented request is useful; an unanswered
letter in the file materially changes how a court reads the word "dishonestly".

---

## 2. Personal data

### 2.1 DPDP Act 2023 — current status

`CITED` (multiple corroborating search extracts: AZB & Partners, Shardul Amarchand Mangaldas,
`dpdpa.dcomply.in`, PIB). Primary sources blocked.

**Status as of 2026-09-19 — one line:** the Act is in force in stages, the **DPDP Rules 2025 were
notified 14 November 2025**, the Data Protection Board is constituted and accepting complaints,
**Consent Manager registration (Rule 4) opens 14 November 2026 — under two months away**, and the
**substantive obligations (Rules 3, 5–16, 22, 23: notice, consent, principal rights, security
safeguards, breach reporting, retention/deletion, children's data, cross-border) commence
14 May 2027**, with no expected grace period.

| phase | date | what commences |
|---|---|---|
| 1 | 14 Nov 2025 | Rules 1, 2, 17–21. Board constituted. Definitions and procedure live. Complaints can be filed. |
| 2 | 14 Nov 2026 | Rule 4. Consent Manager registration. Enforcement/penalty machinery operative. |
| 3 | 14 May 2027 | Rules 3, 5–16, 22, 23. Full compliance: notice, consent, rights, security, breach, retention, children, cross-border. |

**Planning conclusion:** design to the May 2027 standard now. Retrofitting consent, retention and
breach machinery into a live crime map is far more expensive than building it in.

### 2.2 Does publicly available personal data fall outside the Act?

**s.3(c)(ii)** `UNVERIFIED` (could not fetch primary text; the following is from the agent's
training corpus and **must be read against the gazette**). The Act is stated not to apply to
personal data that is made or caused to be made publicly available by —
**(A)** the Data Principal to whom such personal data relates; or
**(B)** any other person who is under an obligation under any law for the time being in force in
India to make such personal data publicly available.

**Applied to FIR portals, limb (B) is the live argument, and it is a good one:**

- *Youth Bar Association of India v Union of India*, (2016) 9 SCC 473 (`UNVERIFIED` citation)
  directed that copies of FIRs, **except those of a sensitive nature — sexual offences, offences
  under POCSO, insurgency and terrorism-related matters** — be uploaded on the police or State
  Government website **within 24 hours** of registration (72 hours in remote areas). A direction
  under Art. 32 is law under Art. 141. A State uploading an FIR pursuant to it is plausibly
  "under an obligation under any law … to make such personal data publicly available."
- `UNVERIFIED` and worth chasing: **BNSS 2023 s.37** is reported to require each police station
  and district to designate an officer and to **maintain a public display, including digitally, of
  the names and addresses of arrested persons**. If that is the text, it is an *express statutory
  obligation to publish personal data* and squarely engages s.3(c)(ii)(B). Verify.

**Three reasons not to treat this as a green light:**

1. **The exemption is contested downstream.** It is drafted around data being "made publicly
   available"; Indian commentary is divided on whether a *re-publisher* who aggregates that data
   inherits the exemption or is a fresh Data Fiduciary. No Board decision or judgment exists yet.
   Counsel must give a written view.
2. **Enrichment probably breaks it (R14).** If we geocode a complainant's address, resolve "Ramesh
   Kumar s/o Suresh" across three FIRs, or retain a record after the portal removes it, we have
   produced personal data that was never "made publicly available" by anyone. The exemption
   cannot plausibly extend to an identity graph we constructed. **Prohibit person-level linkage at
   schema level.**
3. **The exemption only switches off the DPDP Act.** It does nothing about BNS s.72, POCSO s.23,
   JJ s.74, contempt, defamation, or the constitutional privacy right in *K.S. Puttaswamy v Union
   of India*, (2017) 10 SCC 1 (`UNVERIFIED` citation), which binds the State and increasingly
   informs private-law privacy claims.

**There is no journalism exemption in the DPDP Act.** GDPR Art. 85 requires member states to
reconcile data protection with journalistic expression; the 2018 Srikrishna draft Bill had a
journalistic-purposes exemption; **the 2023 Act as passed does not.** A public-interest crime map
cannot shelter behind a media carve-out. This is an important, underappreciated, India-specific
fact and it should be stated to counsel explicitly.

The realistic route for a statistics publisher is **s.17(2)(b)** `UNVERIFIED` — the exemption for
processing for research, archiving or statistical purposes **if carried on in accordance with such
standards as may be prescribed**. The prescribing rule (Rule 15 and the Second Schedule, per the
Rules 2025 numbering) commences 14 May 2027. **Ask counsel whether a publicly-facing aggregate
crime map qualifies as "statistical purposes" under s.17(2)(b), and what the prescribed standards
require.** If yes, it is the cleanest basis for the whole product.

### 2.3 What we hold if we scrape FIRs — head-on

If we scrape a state FIR portal we will, at the moment of the HTTP response, be holding: the
complainant's name and often address and phone; the accused's name, parentage and address;
sometimes the victim's name; and the section(s) invoked. That is personal data under s.2(t) and
we would be a Data Fiduciary under s.2(i) unless s.3(c)(ii) applies.

**The mitigation is architectural and it is the design rule I would make non-negotiable:**

> **Personal identifiers never reach durable storage.** Parse in memory, emit only
> `{category, coarse_geocode, date, source_ref, disposal_status}`, discard the rest before the
> write. No raw HTML archive of FIR pages. No "we'll anonymise later" staging table.

This converts R3 and R14 from live compliance exposure into a non-issue, removes the R9
delisting surface entirely, and — because we never hold the names — makes the "are we exempt under
s.3(c)(ii)?" question largely academic. It costs one engineering decision made early and is
essentially impossible to retrofit.

If a person-level store is ever required (it should not be for v1), it needs: a written lawful
basis, a retention schedule, security safeguards to the Rule 6 standard, a breach-notification
runbook to Rule 7, a published Data Protection Officer / contact person under s.8(9), and a
grievance mechanism under s.8(10) and s.13. `UNVERIFIED` section numbers.

### 2.4 Right to be forgotten in India

`CITED` — real URLs, extracts quoted, pages not openable.

Indian law here is **unsettled and moving**, with High Courts more willing than the Supreme Court:

| case | court / date | what happened |
|---|---|---|
| *XXX v India Today Group*, 2024:DHC:5535 | Delhi HC, 2024 | "Fit case to invoke right to be forgotten" — directed removal of posts showing a man's involvement in crime **after his acquittal**. Injunction granted against the media group. |
| *SK v Union of India*, 2023 LiveLaw (Del) 488 | Delhi HC, 2023 | Directed information-publication websites and **legal databases** to remove the accused's name from search results. |
| Madras HC order dated 27 Feb 2024 (re Indian Kanoon) | Madras HC → **stayed by Supreme Court 24 Jul 2024** | HC had directed removal of the petitioner's identity from a 2011 judgment on Indian Kanoon. **The Supreme Court stayed it** — the strongest signal that the doctrine is not settled. |
| Patiala House Court, 28 Nov 2025 (Moser Baer matter) | Delhi district court | John Doe order directing **Indian Kanoon, major media and Google LLC** to remove or de-index URLs naming a man exonerated on merits in 2024. |
| Delhi HC framework decision, 2026 | Delhi HC | Reported to hold right to be forgotten a facet of Art. 21 and to distinguish **de-indexing** from **masking** (replacing identifiers in public digital versions while preserving unredacted official court records). |
| Karnataka HC, Jan 2017 | Karnataka HC | `VERIFIED_LIVE` (Wikipedia): upheld the right to be forgotten where a woman sought removal of search results about criminal proceedings. |
| Delhi HC, Apr 2016 | Delhi HC | `VERIFIED_LIVE` (Wikipedia): banker sought removal of details after a marital dispute; search engines asked to respond. |

Statutorily, **DPDP s.12** `UNVERIFIED` gives a Data Principal a right to erasure of personal data
processed under consent — but if we rely on the s.3(c)(ii) exemption, s.12 does not reach us.
The exposure is therefore judicial, not statutory.

**Design consequence:** the masking/de-indexing remedy exists because publishers hold names. Hold
no names and this entire body of law becomes a courtesy takedown process rather than a litigation
risk. Publish the takedown route anyway and honour court orders within 36 hours (IT Rules
r.3(1)(d)).

---

## 3. Publication restrictions specific to crime

### 3.1 Victim identity — the hard walls

**BNS s.72** (`CITED`; confirmed as the successor to **IPC s.228A** by multiple search extracts
including the UP Police IPC↔BNS comparative table and Wikipedia's *Section 228A* article).

- Prohibits printing or publishing the name or **any matter which may make known the identity** of
  a person against whom an offence under BNS ss.64–71 (rape and related sexual offences) is
  alleged or found to have been committed.
- Penalty: imprisonment of either description **up to two years, and fine**.
- Exceptions (s.72(2)): by or under written order of the officer-in-charge / investigating officer
  in good faith for investigation purposes; by or with the victim's **written** authorisation; or,
  where the victim is dead, a minor or of unsound mind, with the next of kin's written
  authorisation. `VERIFIED_LIVE` (Wikipedia) that the IPC version also excepted High Court and
  Supreme Court judgments.
- `UNVERIFIED`: **BNS s.73** (= IPC s.228A(3)) prohibits printing or publishing any matter in
  relation to court proceedings in such cases **without the prior permission of the court**.
- `UNVERIFIED`: *Nipun Saxena v Union of India*, (2019) 2 SCC 703 — the Supreme Court held victim
  identity must not be disclosed even with next-of-kin authorisation except through the court, and
  extended the s.228A protection to POCSO victims. If correct, it closes the consent route
  entirely for us.

**POCSO s.23** `UNVERIFIED` (Wikipedia's POCSO article does not cover it; primary text blocked).
From the agent's corpus, and **the single most important sentence in this dossier for map design**:

> No reports in any media shall disclose the identity of a child including his name, address,
> photograph, family details, school, **neighbourhood** or any other particular which may lead to
> disclosure of identity of the child.

- The Special Court may permit disclosure if it is in the child's interest.
- Penalty s.23(4): imprisonment of six months to one year, or fine, or both.
- s.23(3): the publisher or owner of the media is **jointly and severally liable** for acts and
  omissions of employees.

**"Neighbourhood" is expressly enumerated as an identifying particular.** A map whose unit of
display *is* a neighbourhood, showing a POCSO offence in a given month, is publishing exactly the
particular the section names. Counsel must confirm the wording, but if it stands, **POCSO
categories cannot be rendered at neighbourhood granularity at all.**

**JJ Act s.74** `UNVERIFIED`. Prohibits any report in any newspaper, magazine, news-sheet,
audio-visual media or other form of communication disclosing the name, address, school or any
other particular which may lead to identification of a **child in conflict with law, a child in
need of care and protection, or a child victim or witness**; and prohibits publishing any picture.
The Board or Committee may permit disclosure in the child's best interest, recording reasons.
Penalty s.74(3): imprisonment up to six months, or fine up to ₹2 lakh, or both.

**Synthesis — R1 mitigation, stated as a rule:**

> For BNS ss.64–71 offences, all POCSO offences, and all JJ Act matters: render at **district
> level only**, aggregate the date to **quarter**, and suppress any cell below the small-count
> threshold. No point geometry for **any** category, anywhere, ever. No API that returns
> category + fine geography + fine date together.

Note that in rural India the problem is worse, not better: a village with 800 people and one
reported rape is an identification even at village level. The population-denominator floor (R5
mitigation) does double duty here.

### 3.2 Contempt and sub judice

`UNVERIFIED` (Contempt of Courts Act 1971 primary text and the Wikipedia page both unavailable —
the Wikipedia URL returned 404).

From the agent's corpus:
- **s.2(c)** — criminal contempt includes publication which "prejudices, or interferes or tends to
  interfere with, the due course of any judicial proceeding".
- **s.3** — innocent publication defence where the proceeding was not pending, or the publisher had
  no reasonable grounds to believe it was.
- **s.4** — a fair and accurate report of a judicial proceeding is not contempt.
- **s.5** — fair criticism of a decided case is not contempt.
- **s.12** — punishment: simple imprisonment up to six months, or fine up to ₹2,000, or both.
- *Sahara India Real Estate Corp v SEBI*, (2012) 10 SCC 603 — courts may pass constitutional
  "postponement orders" restraining publication where there is a real and substantial risk of
  prejudice to a fair trial.

**Our exposure is low by construction.** Aggregated statistics about reported offences in a
district do not prejudice any identifiable proceeding. Exposure appears only if we publish case
narratives tied to named accused in pending matters — which R-NN (never publish names) forbids.
Keep the "outcome"/disposal field abstract (`pending` / `chargesheeted` / `convicted` /
`acquitted` / `closed`) and never attach it to a person.

### 3.3 Publishing the names of the accused

Do not. Three independent reasons converge:

1. **Presumption of innocence.** An FIR is an allegation. Conviction rates for IPC crimes run far
   below registration rates; publishing accusation as if it were fact is the mechanism by which
   the right-to-be-forgotten cases (§2.4) arose in the first place.
2. **Defamation (§4).** A named accused who is acquitted has a strong civil claim and a viable
   criminal complaint. Truth of "an FIR was registered" may be provable, but Exception 1 to
   BNS s.356 also requires *public good*, and a court is unlikely to find public good in naming a
   private individual on a map.
3. **It buys us nothing.** No user of a neighbourhood safety map needs a name. The product value
   is entirely in the aggregate.

---

## 4. Defamation and area stigmatisation

### 4.1 The provisions

`VERIFIED_LIVE` (Wikipedia, *Bharatiya Nyaya Sanhita*): **defamation is BNS Chapter 20, s.356**;
the BNS commenced **1 July 2024**.

`UNVERIFIED` for the detail: s.356(1) carries the IPC s.499 definition and its ten Exceptions;
s.356(2) punishes defamation with simple imprisonment up to two years, or fine, or both, **or
community service** (community service is a BNS innovation); s.356(3) covers printing or engraving
defamatory matter; s.356(4) covers sale of such matter. IPC ss.499/500 map to BNS s.356.

Defamation in India is **both civil (tort, uncodified, English-derived) and criminal**.

### 4.2 The India-specific hazard: truth alone is not a defence

This is the point to internalise, because it inverts the intuition of anyone trained on US or
UK law.

- In **civil** defamation, justification (truth) is a complete defence, following English law.
  `VERIFIED_LIVE` (Wikipedia, *Defamation*) notes one asymmetry: unlike the UK, India has **no
  statutory provision allowing partial justification** — if the defendant proves the truth of only
  some of several charges, there is no Indian equivalent of the English rule preserving the
  defence where the unproved charges do not materially injure reputation. **India is stricter
  than England even on the civil side.**
- In **criminal** defamation, **Exception 1** (`UNVERIFIED` wording, from the agent's corpus)
  reads: it is not defamation to impute anything which is true concerning any person, **if it be
  for the public good that the imputation should be made or published. Whether or not it is for
  the public good is a question of fact.**

So a publisher who is completely, demonstrably right can still be convicted if the court finds
publication was not for the public good. "Public good" is a question of fact decided by a
magistrate, after trial, at whatever forum the complainant chose.

- *Subramanian Swamy v Union of India*, (2016) 7 SCC 221 (`UNVERIFIED` citation — Wikipedia page
  404'd) upheld the constitutionality of IPC ss.499/500, holding reputation is part of the Art. 21
  right to life and criminal defamation a reasonable restriction under Art. 19(2). Criminal
  defamation is therefore alive and will remain so under BNS s.356.

**What this means operationally.** The realistic harm is not a judgment against us. It is that any
aggrieved builder, RWA office-bearer or local politician can file a **private complaint** (BNSS
s.222, ex-CrPC s.199) before a magistrate anywhere they can establish jurisdiction, obtain
summons, and require our directors to appear personally, repeatedly, for years. That is a
harassment cost, and it is available cheaply. Budget for it or design to avoid it.

**Mitigations that actually reduce the "public good" and "imputation" exposure:**

- Publish **rates with visible denominators and confidence intervals**, never bare counts (R13).
- Frame everything as **"reported crime (FIRs registered)"**, never "crime". The distinction is
  both true and protective — it makes the imputation about *police records*, not about residents.
- **No rankings.** Never publish "India's 10 most unsafe localities". A ranking converts a
  statistic into an imputation about a determinate group.
- **No adjectives.** "Unsafe", "dangerous", "avoid" are editorial characterisations. Numbers and
  a neutral colour ramp are not.
- Publish a **methodology page and a corrections policy** and honour them visibly. Evidence of
  good faith goes directly to Exception 9 (good faith for the public good) and to the civil
  qualified-privilege analysis.
- **Right of reply**: give any local body a documented route to submit context that renders
  alongside the data. Cheap, and powerful evidence of public-good intent.

### 4.3 Can an RWA, builder or municipality sue?

`UNVERIFIED` throughout — this needs counsel.

- **Explanation 2 to IPC s.499** (carried into BNS s.356) provides that it may amount to
  defamation to make an imputation concerning **a company or an association or collection of
  persons as such**. So group defamation is recognised in principle.
- Indian courts require the group to be **determinate and identifiable**, and require the claimant
  to show the imputation pointed at them. A **locality** is not a legal person and cannot sue. But:
  - a **Resident Welfare Association** usually *is* a registered body (Societies Registration Act
    1860, or a state Apartment Ownership Act, or a co-operative housing society statute) and is
    therefore a juristic person that can complain;
  - a **builder / developer** is a company and can sue in both civil and criminal defamation over
    an imputation about a named project;
  - a **municipality** is a statutory corporation. Whether an elected governmental body can sue
    for defamation at all is the question answered "no" in England by *Derbyshire County Council v
    Times Newspapers Ltd* [1993] AC 534. Derbyshire is persuasive but **not binding** in India and
    the Indian position is not settled. Assume a municipality can at least try.

**Precedent on maps or ratings harming property values: I found none, and I am recording that as
a finding rather than as an absence of risk.** There appears to be no reported Indian decision on
a crime map, an area safety rating, or a neighbourhood index. The nearest analogues — consumer
review platforms, credit ratings, "project blacklisted" reporting — are different enough that they
would not control. **The consequence is that the exposure is unquantified, not low.** A first case
against us would be a case of first impression, which is the most expensive kind to be in.
This is one of the two items I would most want a litigator's view on.

---

## 5. Discrimination and redlining risk

**This is the most serious ethical risk in the project, and Indian law is thin to the point of
absence. I want to state that plainly rather than pad it.**

### 5.1 What Indian law does *not* do

- **No fair-housing statute.** There is no Indian Fair Housing Act, no equivalent of the US
  Equal Credit Opportunity Act, no general disparate-impact doctrine in private law.
- **Constitutional provisions reach the State, mostly.** Art. 15(1) binds the State; Art. 15(2)
  reaches private denial of access to shops, public restaurants, hotels and places of public
  entertainment, and to wells/tanks/roads — not to tenancy or lending. Art. 17 abolishes
  untouchability.
- **The DPDP Act has no sensitive-personal-data category at all.** `UNVERIFIED` but I am
  confident: unlike the 2018 and 2019 drafts, unlike GDPR Art. 9, and unlike the SPDI Rules 2011,
  the 2023 Act treats caste, religion, health and sexual orientation as ordinary personal data.
  There is also **no Art. 22-GDPR right against automated decision-making** and **no profiling
  provision**. So Indian data-protection law places no brake on inference.
- **No financial-sector prohibition.** RBI's Digital Lending Guidelines (Sept 2022) and Fair
  Practices Code require board-approved credit policies and disclosure, but contain no
  geographic-discrimination prohibition. IRDAI's underwriting regulations do not prohibit
  locality-based pricing. `UNVERIFIED` — but I am not aware of any Indian anti-redlining rule,
  and counsel should confirm the negative.
- **Tenant screening is essentially unregulated.** Refusal to rent on grounds of religion or diet
  is widely documented in Indian metros and is not, in general, actionable.

The only instruments that reach in this direction are criminal and narrow:
- **SC/ST (Prevention of Atrocities) Act 1989** — provisions on denial of customary access and on
  **economic and social boycott** of members of Scheduled Castes/Tribes. `UNVERIFIED`: a map
  demonstrably used to organise boycott of a Dalit basti could conceivably be argued into this
  frame. That is an argument, not an established exposure.
- **Maharashtra Prohibition of People's Protection from Social Boycott Act, 2016** — makes social
  boycott an offence, in Maharashtra only.

**Conclusion: the legal risk of enabling redlining in India is close to zero, and the ethical
risk is close to maximal. Because the law will not stop us, the architecture has to.**

### 5.2 The caste and religion dimension — state it explicitly

Indian urban residential space is segregated by caste and religion to a degree that is
empirically documented (see the `civil-society-academic` dossier for the segregation literature —
Bharathi/Malghan/Rahman on Indian city segregation using census and SHRUG data; Gandhi/Tandel on
Mumbai). Muslim-concentrated localities in Ahmedabad, Mumbai, Delhi and Hyderabad, and Dalit
bastis in most cities, are spatially distinct and locally known as such.

**Therefore: a fine-grained crime choropleth of an Indian city is, to a substantial degree, a map
of where Muslims and Dalits live.** A user does not need to intend communal reasoning for the map
to supply it. The map will be screenshotted, cropped and circulated without our caveats.

Two compounding effects make the raw data worse than it looks:

1. **FIR density measures policing, not crime.** Over-policing of Dalit, Adivasi, Muslim and
   denotified-tribe settlements — plus differential willingness of residents to approach a police
   station, plus refusal to register FIRs in some areas — means FIR counts confound crime with
   police presence and police attitude. A map of FIRs per sq km is substantially a map of police
   attention. **Publishing it as "crime" launders enforcement bias into apparent fact.**
2. **Counts without denominators punish density.** A dense low-income settlement of 20,000 people
   generates more absolute FIRs than a gated colony of 800, at any per-capita rate. A count map
   is a population-density map wearing a crime label.

### 5.3 Mitigations (used elsewhere; adopt as the design standard)

| mitigation | source / precedent | our rule |
|---|---|---|
| **Snap incidents to pre-defined anonymous points, never to an address** | police.uk: incidents are mapped to a catalogue of anonymous map points, each chosen so the area it represents contains a minimum number of postal addresses; a point is never placed on an actual address. `UNVERIFIED` — `data.police.uk` was blocked; **`benchmark-product` must verify the exact method and the address-count threshold.** | We go further: **no point geometry at all in v1.** Polygons only. |
| **Primary suppression of small counts** | Standard statistical disclosure control (UK ONS, US Census, NCHS). Thresholds of n < 5 or n < 10 are conventional. | Suppress any rendered cell with **n < 10**. Show "insufficient data", not zero. |
| **Complementary suppression** | SDC practice: suppressing one cell is useless if it can be back-calculated from row/column totals. | If one cell in an area is suppressed, suppress a second, or do not publish the total. Applies to the category breakdown within an area *and* to the time series. |
| **Rate, not count, with the denominator visible** | Universal statistical practice. | Default view is per-1,000-residents. Counts only on drill-down, always shown next to the population. |
| **Minimum population denominator per rendered unit** | k-anonymity on geography. | No unit with fewer than **5,000 residents** is rendered independently; smaller units are merged with neighbours before display. Prevents a 500-person ward with 3 thefts reading as a hotspot. |
| **No point pins in residential areas** | The brief's own formulation; consistent with police.uk's address-count rule. | Follows automatically from "polygons only". |
| **Display uncertainty, not a single colour** | Small-area estimation practice. | Colour ramp bucketed coarsely; confidence interval shown on hover; areas whose CI spans two buckets rendered as "no significant difference". |
| **Refuse to rank** | Editorial. | No "most dangerous" list, no league table, no per-address "safety score", no ranking endpoint in the API. |
| **Terms of use prohibiting screening, underwriting and credit use** | Weak in India (unenforceable against a scraper) but evidentially valuable. | Publish it, and make bulk access contractual rather than open in v1. |
| **Publish the bias caveat as prominently as the data** | | The methodology note on policing bias renders **on the map**, not on a linked page. |

**Honest limitation:** none of this prevents a determined actor from scraping our polygons and
building a screening product. The suppression rules and the refusal to publish address-level
output raise the cost and remove the precision that makes screening commercially attractive. That
is the achievable goal; "prevention" is not.

---

## 6. Intermediary liability (if we accept user-submitted reports)

`VERIFIED_LIVE` (Wikipedia, *Information Technology Act, 2000* and *Information Technology Rules,
2021*) for: *Shreya Singhal* declined to strike down ss.69A and 79; the Rules supersede the 2011
Intermediary Guidelines; Rule 4(1) requires a **Chief Compliance Officer, a nodal contact person
and a Resident Grievance Officer**; a **36-hour** takedown requirement exists; Rule 4(2)
first-originator/traceability applies to significant intermediaries.

`UNVERIFIED` for the section and rule detail below.

**IT Act s.79 — safe harbour**

- s.79(1): an intermediary is not liable for third-party information, data or communication links
  made available or hosted by it.
- s.79(2): available only if (a) the function is limited to providing access to a communication
  system over which information is transmitted, temporarily stored or hosted; **or** (b) the
  intermediary does not initiate the transmission, select the receiver, and select or modify the
  information; **and** (c) it observes due diligence and such guidelines as the Central Government
  prescribes.
- s.79(3): safe harbour is lost if (a) the intermediary conspired, abetted, aided or induced the
  unlawful act; or (b) on receiving **actual knowledge**, or on being notified by the appropriate
  Government or its agency, it fails to expeditiously remove or disable access.
- ***Shreya Singhal v Union of India*, (2015) 5 SCC 1** read down s.79(3)(b): "actual knowledge"
  means knowledge arising from a **court order** or a notification by the appropriate Government
  or its agency — **not** a private complaint. This is strongly in our favour: a builder's angry
  email does not start a takedown clock.

**The line that matters: s.79 protects third-party content only.** Our computed heat map, our
category assignments and our editorial framing are **first-party publications**. There is no safe
harbour for them. Consequence:

> Keep user-submitted reports on a **separate layer**, visually distinct, explicitly attributed to
> users, never merged into the statistical layer, and never used as an input to our own published
> aggregates. The moment a user report feeds our number, that number is our speech.

**IT Rules 2021 — the v1 compliance checklist** (`UNVERIFIED` rule numbers):

| obligation | rule | deadline |
|---|---|---|
| Publish rules, privacy policy and user agreement | r.3(1)(a) | at launch |
| Inform users of prohibited content categories (defamatory, obscene, invasive of privacy including bodily privacy, harmful to child, etc.) | r.3(1)(b) | at launch |
| Notify users of the rules periodically (annually) | r.3(1)(c) | annual |
| Remove/disable content on a **court order or Appropriate Government notification** | r.3(1)(d) | **36 hours** |
| Retain information of removed records | r.3(1)(g) | 180 days |
| Provide information/assistance to a government agency on lawful order | r.3(1)(j) | **72 hours** |
| **Publish name and contact of a Grievance Officer** | r.3(2)(a) | at launch |
| Acknowledge a grievance | r.3(2)(a) | **24 hours** |
| Dispose of a grievance | r.3(2)(a) | **15 days** |
| Remove content exposing private areas / nudity / sexual act / impersonation incl. morphed images | r.3(2)(b) | **24 hours** |
| Grievance Appellate Committee appeal route (user may appeal our GO's decision) | r.3A (IT Amendment Rules 2022, effective 1 Mar 2023) | GAC decides in 30 days; binding |
| Significant Social Media Intermediary obligations: CCO, nodal contact, RGO, monthly compliance report, traceability | r.4 | only above the threshold — **50 lakh (5 million) registered Indian users** per MeitY notification 25 Feb 2021 |

**We will not be a Significant Social Media Intermediary for v1.** The baseline r.3 obligations
are cheap: a named Grievance Officer resident in India with a published address and email, a
ticketing workflow with 24h/15d SLA timers, and a documented 36-hour court-order takedown path.
**Ship all of it on day one if UGC ships at all** — retrofitting after a notice arrives is how
safe harbour is lost.

---

## 7. Map and boundary compliance

`VERIFIED_LIVE` (Wikipedia, *Survey of India*): Survey of India is responsible for **"scrutiny and
certification of external boundaries of India and Coastline on maps published by the other
agencies including private publishers"**, and for demarcation of India's borders and external
boundaries. The **National Map Policy of 2005** is in force, and on **15 February 2021** the
Government announced mapping-policy changes which "free up a lot of earlier restrictions related
to mapping".

`VERIFIED_LIVE` (Wikipedia, *Geospatial Information Regulation Bill*): the 2016 Bill — which would
have licensed all geospatial acquisition and dissemination — **was never enacted and remains
pending**. On 15 February 2021 the Department of Science & Technology released approved
**Guidelines for acquiring and producing geospatial data and geospatial data services including
maps**, which "would largely replace the restrictions proposed within the Geospatial Information
Regulation Bill of 2016 by deregulating the sector".

`UNVERIFIED` — the operative detail, which counsel must confirm from the DST Guidelines text:

1. **Indian entities need no prior approval, security clearance or licence** to collect, generate,
   prepare, disseminate, store, publish, update or digitise geospatial data and maps within India.
   Good for us.
2. A **Negative List** of attributes reserved to Indian government agencies, defined by accuracy
   thresholds (commonly cited as finer than **1 m horizontal / 3 m vertical** for ground data, with
   separate thresholds for terrestrial mobile mapping, street-view and lidar).
3. **Maps depicting India's boundaries must conform to the boundaries published by Survey of
   India.** This is the operative compliance obligation for us.
4. **Foreign-owned or foreign-controlled entities** face restrictions: they may licence digital
   maps/services of 1 m-or-coarser resolution to Indian end-users through an API and may not
   re-export finer data (R16 — a reason to incorporate and host in India).

`UNVERIFIED` and important — **the "wrong map" offence**. The commonly cited basis is the
**Criminal Law (Amendment) Act, 1961, s.2**: whoever by words, spoken or written, or by signs, or
by **visible representation** or otherwise, questions the territorial integrity or frontiers of
India in a manner which is, or is likely to be, prejudicial to the interests of the safety or
security of India — imprisonment **up to three years**, or fine, or both. (Note: my scope note
said "Criminal Law Amendment 1990"; the Wikipedia page for a 1990 Act returned 404 and I believe
**1961** is correct. Counsel must confirm which Act and section.) Ancillary exposure: blocking
under **IT Act s.69A**, and the practical risk of an FIR registered in any district.

The **National Geospatial Policy 2022** (DST, Dec 2022) is `UNVERIFIED` and is in any event a
policy rather than a statute; it sets national mapping targets and does not create new offences.

**The concrete v1 trap.** Default **OpenStreetMap, Mapbox and Google "international" tiles render
the Jammu & Kashmir Line of Control as a dashed/disputed boundary, and show Aksai Chin outside
India.** That depiction is unlawful in India. Google, Apple and Mapbox serve India-specific
tilesets to requests originating in India. **If we self-host OSM-derived tiles, we inherit the
non-compliant boundary and ship an offence.**

**v1 rules:**
- Never render the national boundary from our own geometry.
- Use an India-served tileset from a provider that warrants India compliance, or serve the
  Survey of India-published boundary layer.
- Get the tile-provider decision reviewed by counsel **before** the first public deploy, not
  before launch week.
- Apply the same care to Arunachal Pradesh and to the Sir Creek/Gujarat coastline.

---

## Granularity reality check (legal ceiling, not data floor)

The other dossiers describe what data *exists*. This table describes the **finest granularity it
is defensible to publish**, which is often coarser.

| category | data may exist at | legally defensible publication unit | date granularity | why |
|---|---|---|---|---|
| Property crime (theft, burglary, vehicle) | police-station / point | **ward or police-station polygon**, pop ≥ 5,000, n ≥ 10 | month | Lowest-risk category. No victim-identity statute engaged. R4/R5 still bind. |
| Violent crime (non-sexual) | police-station / point | **ward or police-station polygon**, pop ≥ 5,000, n ≥ 10 | month | As above; small counts identify more easily. |
| Sexual offences (BNS ss.64–71) | FIR-level | **district** | quarter | BNS s.72/73. Location + date + category identifies. |
| POCSO | FIR-level | **district** | quarter | POCSO s.23(2) enumerates "neighbourhood" as an identifying particular. |
| JJ Act / children in conflict with law | case-level | **district**, or do not publish | quarter/annual | JJ s.74. |
| SC/ST (PoA) Act offences | FIR-level | **district** | quarter | Not a publication offence, but caste-coded by construction (§5.2). Publishing at ward level draws a caste map directly. |
| Road accidents (iRAD/eDAR) | point | **road segment / junction** | month | No personal data if de-identified; the least constrained layer and probably the best v1 demo. |
| Cyber / NCRP | complaint-level | **district or city** | month | Victim location often the complainant's residence; treat as personal. |
| Court outcomes (eCourts/NJDG) | case-level | **district court** | monthly | s.52(1)(q)(iv) permits reproduction; the RTBF case law (§2.4) means do not attach names. |

**The gap between want and reality:** the product question is "is this street safe at night" and
the defensible answer is a ward-level reported-FIR rate for property and non-sexual violent crime,
with confidence intervals, refreshed monthly at best. That is a genuinely useful product. It is
not police.uk, and the gap is created by law and by data quality in roughly equal measure.

---

## Blockers and how to get past them

1. **Primary legal texts were unreachable this session.** All `*.gov.in`/`*.nic.in` hosts,
   Indian Kanoon, LiveLaw, SCC Online and PRS India are blocked by the egress proxy, and the
   WebSearch budget was exhausted. *Get past it:* have a human open India Code
   (`indiacode.nic.in`) and the e-Gazette, or run this dossier's **Must-verify** list past counsel
   who has SCC Online / Manupatra access. Budget half a day.
2. **No verified robots.txt or terms of use for any target portal.** *Get past it:* a one-hour
   manual pass by someone in India capturing, for each of NCRB, eCourts/NJDG, data.gov.in and each
   state police FIR portal: `/robots.txt`, the Terms/Disclaimer page, and a screenshot with date.
   Store in `research/_raw/tou/`. This is a prerequisite for Phase 2 ingestion, not an optional
   extra.
3. **The s.3(c)(ii) question is genuinely open.** No Board decision, no judgment. *Get past it:*
   a written opinion from a data-protection counsel, framed narrowly: "may an aggregator
   re-publish district-level statistics derived from FIRs lawfully published on state police
   portals, without becoming a Data Fiduciary in respect of the underlying personal data?"
4. **No Indian precedent on area-rating defamation.** *Get past it:* accept that this is
   unquantified, and reduce exposure by editorial design (§4.2). Ask a litigator for a view on
   whether a registered RWA has standing to complain about a ward-level statistic.
5. **Basemap boundary compliance.** *Get past it:* written confirmation from the tile provider
   that their India-served tiles conform to Survey of India boundaries, on file before deploy.

---

## Seed Leads (unconfirmed but probably real)

| lead | likely publisher | why it matters | concrete next step |
|---|---|---|---|
| **BNSS 2023 s.37** requiring public (including digital) display of names and addresses of arrested persons | MHA / state police | If real, it is an express statutory obligation to publish personal data and squarely triggers DPDP s.3(c)(ii)(B) | Read BNSS s.37 on India Code; check whether any state has actually implemented a digital display |
| **MeitY / DPB guidance on s.3(c)(ii)** | Data Protection Board of India | Would resolve the central open question | Watch DPB decisions from Nov 2025 onward; check MeitY FAQ pages |
| **DPDP Rule 15 + Second Schedule** — prescribed standards for research/archiving/statistical processing under s.17(2)(b) | MeitY | Likely our cleanest lawful basis | Read the Rules 2025 text; commences 14 May 2027 |
| **NCRB data-sharing policy / MoU template** | NCRB | NCRB shares unit-level data with researchers under MoU; terms unknown | RTI to NCRB: "provide a copy of the data-sharing policy and the standard MoU under which unit-level CCTNS data is shared with researchers, 2020–2026" |
| **State-level FIR publication circulars** implementing *Youth Bar Association* | each state DGP/Home Dept | Establishes the "obligation under law" for limb (B) on a per-state basis | RTI to each state Home Department for the circular implementing the SC's FIR-upload direction |
| **Survey of India map certification procedure and fee** | Survey of India, Dehradun | Needed if we ever render our own boundary | Write to SoI Map Publication office; ask for the OSM (Open Series Map) certification procedure |
| **Press Council of India norms on crime reporting** | Press Council of India | Not binding on us, but a court would treat the norms as the standard of responsible publication | Obtain "Norms of Journalistic Conduct" (latest edition); extract the crime-reporting and victim-identity chapters |
| **Any Indian defamation suit over a review/rating platform** | — | Closest analogue to area-rating exposure | Ask counsel to run a Manupatra/SCC search for defamation suits against review or rating platforms, 2015–2026 |

---

## Must-verify before launch (the list for the advocate)

Ordered by how much the product changes if the answer is different from what is assumed here.

1. **DPDP s.3(c)(ii) text and scope.** Does the exemption travel to a downstream re-publisher?
   Written opinion, narrowly framed.
2. **POCSO s.23(2)** — does the text actually enumerate "neighbourhood"? If yes, confirm that
   district-level rendering of POCSO categories is sufficient.
3. **BNS s.72 and s.73** exact text, and whether *Nipun Saxena* forecloses consent-based
   disclosure.
4. **Which Act and section creates "wrong map" liability** — Criminal Law (Amendment) Act 1961
   s.2, or something else. Confirm the penalty.
5. **DST Geospatial Guidelines 2021** — confirm the Survey-of-India-conformity requirement for
   boundary depiction, the Negative List thresholds, and the foreign-entity restrictions.
6. **Copyright Act s.52(1)(q)(iii)** — does a NCRB annual statistical volume fall within "report
   of any committee, commission, council, board or other like body appointed by the Government"?
7. **IT Act s.43(b)** — does a browsewrap ToU prohibiting automated access negate "permission of
   the owner"? Any Indian authority either way?
8. **BNS s.356 Exception 1** — exact wording, and whether a ward-level crime rate published with
   caveats is likely to be found "for the public good".
9. **Group defamation** — standing of a registered RWA, a developer, and a municipal corporation.
   Is *Derbyshire* followed in India?
10. **DPDP s.17(2)(b)** research/statistical exemption — does a public aggregate crime map qualify,
    and what do the prescribed standards require?
11. **GODL exemptions clause** — confirm personal data is carved out of the grant, and confirm
    whether a no-endorsement / non-misleading clause exists.
12. **IT Rules 2021** grievance timelines (24h / 15d / 36h / 72h) and GAC appeal mechanics, and
    whether our UGC layer makes us an intermediary at all.
13. **BNSS s.37** — does it require public display of arrested persons' particulars?
14. **RTI s.8(1)(j) as amended by DPDP s.44(3)** — confirm the public-interest override is gone,
    and what that leaves available to `rti-playbook`.

---

## Phase 2 recommendations

Ranked by what unblocks the most product.

1. **Adopt the non-negotiable design rule now, before any ingestion code is written:**
   *personal identifiers never reach durable storage; parse in memory, persist only
   `{category, coarse_geocode, date, source_ref, disposal_status}`.* This single decision
   neutralises R3, R9 and R14, and makes the unresolved s.3(c)(ii) question largely moot. It is
   free today and very expensive in six months.
2. **Encode the suppression rules in the serving layer, not the UI.** Minimum population 5,000,
   minimum count 10, complementary suppression, rate-as-default, no point geometry, no ranking
   endpoint. If they live in the API they cannot be lost in a redesign, and the API cannot be
   scraped for what it will not serve.
3. **Settle the basemap.** Choose an India-compliant tile source and get written confirmation of
   Survey of India boundary conformity on file. This is a one-week task that becomes a shutdown
   risk if deferred.
4. **Commission the counsel opinion** on items 1–5 of the must-verify list. Everything else can be
   checked later; those five determine the schema and the map.
5. **Do the ToU/robots.txt capture pass** (Blocker 2) and store dated screenshots in
   `research/_raw/tou/`. Ingestion for any portal whose ToU has not been read should not start.
6. **Write to every state SCRB/CID** asking for a data feed or for written permission to collect.
   Do this before scraping, not after a notice. The correspondence file is the single most
   valuable artefact for R6.
7. **Ship the intermediary compliance kit with v1 if and only if UGC ships:** named Grievance
   Officer, published contact, 24h/15d SLA timers, 36h court-order takedown path, UGC on a
   separate layer.
8. **Write the methodology and caveats page before the map.** It carries the policing-bias caveat,
   the "reported crime not crime" framing, the suppression rules and the corrections policy. It is
   both the ethical core and the best evidence of good faith under BNS s.356 Exceptions 1 and 9.
9. **Hand `benchmark-product` the open question on police.uk's anonymisation method** — the exact
   anonymous-map-point catalogue, the minimum address count per point, and the licence. I could
   not reach `data.police.uk` and that method is the single best precedent for our geography rules.
