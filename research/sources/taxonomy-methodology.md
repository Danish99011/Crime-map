# Crime Taxonomy, Legal Transition & Statistical Comparability (Data-Model Dossier)
_Agent: taxonomy-methodology · Researched: 2026-09-19 · Entries: 7 verified / 24 total_

> **This file is the reference every ingestion pipeline in this project is written against.**
> It is not a source hunt. It is the set of rules that decide whether a number we paint on a
> polygon means anything. Sections 1-6 are the findings; section 7 is the schema you implement.

---

## Executive summary

- **There is no statutory IPC→BNS concordance.** The Bharatiya Nyaya Sanhita, 2023 (Act 45 of 2023,
  in force **1 July 2024**) contains no schedule of correspondences — s.358 simply repeals the IPC.
  The nearest thing to an *official* mapping is **NCRB's "Sankalan" compendium of the new criminal
  laws** (MHA/NCRB, released around the 1 July 2024 rollout as an app + PDF, billed as a bridge
  between old and new laws). I could not verify it: `ncrb.gov.in` is blocked by this session's
  egress proxy. **Verifying Sankalan is Phase-2 task #1.** A state-police mirror exists and is
  attested by a search-engine result: UP Police, *"Corresponding Section Table Of Bharatiya Nyaya
  Sanhita 2023 (BNS)"*, under a "Three New Major Acts" directory on `uppolice.gov.in` — also
  egress-blocked here. **§1.3 of this file contains a ~110-row mapping table built by hand.**
- **Never key crime data on a section number.** Key on our own law-neutral `crime_key`, with IPC
  and BNS sections as *attributes*. The IPC→BNS relation is many-to-many: IPC 383-389 all collapse
  into BNS 308; IPC 453-460 all collapse into BNS 331; IPC 364/364A/365/367 all collapse into
  BNS 140. **Post-2024 property-crime data is permanently lower-resolution than pre-2024 data.**
- **BNS invented offences that will look like crime waves.** BNS **304 (snatching)**,
  **111 (organised crime)**, **112 (petty organised crime)**, **113 (terrorist act)**,
  **69 (sex by deceitful means)**, **103(2) (mob lynching)** have no IPC predecessor. Any
  2024→2025 growth chart for these is an artefact of the statute book. Conversely **IPC 377 and 497
  have no BNS successor at all** and **IPC 124A (sedition) has only a differently-worded successor
  (BNS 152)** — those series die at 2024-06-30.
- **The principal offence rule censors the map non-randomly.** NCRB counts one offence per FIR —
  the most severely punishable. Apex heads (murder, rape, dacoity) are complete; **subordinate
  heads (hurt, criminal intimidation, trespass, mischief, wrongful restraint) are systematically
  depleted wherever worse crime co-occurs.** The signal on an "assault" map is therefore *inverted*
  in violent areas. NCRB publishes no undercount estimate; §2 gives the experiment to measure it.
- **Denominators are our sharpest own-goal risk.** There has been no census since 2011. Census 2027
  is live now — house-listing ran **1 Apr 2026 – Sep 2026**, population enumeration
  **9-28 Feb 2027** (snow-bound Himalayan areas Aug-Sep 2026, reference date 1 Oct 2026),
  with caste enumeration for the first time since 1931. **District population tables will not land
  before ~2028.** Using Census 2011 denominators for 2025 rates reddens exactly the fast-growing
  peri-urban districts (Gurugram, Gautam Buddha Nagar, Bengaluru Urban, Thane, Rangareddy, Surat)
  by 40-80% relative to slow-growing ones, for purely demographic reasons.
- **The district set moved 25% since the last census.** 640 districts at Census 2011 →
  **800 as of Dec 2025** (Wikipedia, verified). One district in five on a current map has no 2011
  population of its own and no pre-split NCRB history. Telangana went **10 → 31 → 33** in five
  years; Rajasthan went **33 → 50 (Aug 2023) → 41 (Dec 2024)** — reorganisation that *reversed*.
- **NCRB's "city" rows are a subset of its state rows, and the polygons don't match.** The
  numerator is a **police commissionerate** jurisdiction; the denominator is a **Census 2011 urban
  agglomeration**. Different areas. Summing city + state double-counts; joining commissionerate
  names to revenue districts silently drops units (Pimpri-Chinchwad, Pune City, Pune Rural are
  three police rows for one revenue district).
- **India publishes no national polygon layer for police jurisdictions at any level.** Not
  commissionerates, not police districts, not police stations. The finest *authoritative* polygon
  in the country is the Census 2011 village/town. This is the hard ceiling on our spatial product,
  and it is the single biggest gap between us and police.uk.
- **A map of reported crime is partly a map of police responsiveness, not of crime.** Kerala
  reports roughly the highest IPC crime rate in India while being by every independent measure
  among its safest states. NFHS-derived work indicates **>90% of sexual assaults never reach the
  police**; NCRB's own 2006 report put unreported rape at **71%**. BNSS s.173(3) re-introduced a
  discretionary 14-day preliminary inquiry for 3-7 year offences — a partial statutory rollback of
  *Lalita Kumari* that may **depress** registered crime from 1 July 2024 onward.
- **Finest granularity actually achievable at national scale: district-annual.** Everything finer
  is single-state, single-city, or does not exist. Design the product for district-annual and treat
  sub-district data as a per-city bonus layer, not the backbone.

---

## 1. The crime taxonomy

### 1.1 IPC (Act 45 of 1860) — the chapters that matter to a resident

The IPC had 23 chapters and 511 sections. Four chapters carry ~95% of what a crime map shows.

| IPC chapter | Title | Sections | Why it matters |
|---|---|---|---|
| VIII | Offences against the public tranquillity | 141-160 | rioting, unlawful assembly, affray |
| XIV | Offences affecting public health, safety, convenience, decency and morals | 268-294A | rash driving (279), obscenity, nuisance |
| XVI | **Offences affecting the human body** | 299-377 | homicide, hurt, assault, kidnapping, rape |
| XVII | **Offences against property** | 378-462 | theft, extortion, robbery, dacoity, cheating, trespass, house-breaking |
| XX-A | Cruelty by husband or relatives | 498A | the largest single "crime against women" head |
| XXII | Criminal intimidation, insult and annoyance | 503-510 | 506, 509 |
| XXIII | Attempts | 511 | attempt-to-rape and other attempts |

Resident-relevant sections, in the order a product manager would ask for them:

| Concept | IPC sections |
|---|---|
| Murder | 300 (def), **302** (punishment), 303 (by life-convict) |
| Culpable homicide not amounting to murder | 299 (def), **304** |
| Death by negligence (incl. road) | **304A** |
| Dowry death | **304B** |
| Attempt to murder / attempt to commit culpable homicide | **307** / 308 |
| Abetment of suicide | 305, 306 |
| Hurt | 319 (def), 321, **323** (punishment), 324 (dangerous weapon) |
| Grievous hurt | 320 (def), 322, **325** (punishment), 326 (dangerous weapon), 326A/B (acid) |
| Assault / criminal force | 349-358; **354** (outraging modesty), 354A (harassment), 354B (disrobing), 354C (voyeurism), 354D (stalking) |
| Kidnapping & abduction | 359-361 (def), 362 (abduction), **363** (punishment), 363A (begging), 364, 364A (ransom), 365, **366** (to compel marriage), 366A, 366B, 367, 368, **369** |
| Trafficking | 370, 370A |
| Rape | 375 (def), **376** (punishment), 376A, 376AB, 376B, 376C, **376D** (gang rape), 376DA, 376DB, 376E |
| Unnatural offences | 377 |
| Theft | 378 (def), **379** (punishment), 380 (dwelling house), 381 (servant), 382 |
| Extortion | 383 (def), **384** (punishment), 385-389 |
| Robbery | 390 (def), **392** (punishment), 393, 394, 397, 398 |
| Dacoity | 391 (def), **395** (punishment), 396 (with murder), 397-402 |
| Criminal breach of trust | 405-409 |
| Cheating | 415 (def), 417, 418, 419 (personation), **420** |
| Mischief / arson | 425-440 |
| Criminal trespass & house-breaking (our "burglary") | 441-442 (def), 443-444 (lurking house-trespass), **445-446** (house-breaking), 447-448 (punishments), 449-452, **453-460** (punishments incl. **457** house-breaking by night to commit an imprisonable offence) |
| Cruelty by husband/relatives | **498A** |
| Rioting / unlawful assembly | 141 (def), 143, 146 (def), **147** (punishment), 148, 149 |
| Promoting enmity | 153A, 153B |
| Criminal intimidation | 503 (def), **506**; 509 (insulting modesty) |

**Snatching has no IPC section.** Before 1 July 2024 it was booked as theft (379) or robbery (392)
depending on whether force was used and on local practice, *except* in states that added their own
amendments — Delhi (IPC 356/379A/379B as amended), Punjab and Haryana (379A/379B), Maharashtra.
**Any pre-2024 "snatching" series is state-law-dependent and is not nationally comparable.**

### 1.2 BNS / BNSS / BSA — the 2024 break

| Act | Number | Replaces | In force | Size |
|---|---|---|---|---|
| **Bharatiya Nyaya Sanhita, 2023** | Act 45 of 2023 | Indian Penal Code, 1860 | **1 July 2024** | 358 sections, 20 chapters |
| **Bharatiya Nagarik Suraksha Sanhita, 2023** | Act 46 of 2023 | Code of Criminal Procedure, 1973 | **1 July 2024** | 531 sections, 39 chapters, 2 schedules |
| **Bharatiya Sakshya Adhiniyam, 2023** | Act 47 of 2023 | Indian Evidence Act, 1872 | **1 July 2024** | 170 sections |

BNS chapter structure (reconstructed — the Wikipedia rendering of the arrangement of sections is
offset by one chapter and **must be checked against the gazette before shipping**):

| Ch | Title | Sections |
|---|---|---|
| I | Preliminary | 1-3 |
| II | Of Punishments | 4-13 |
| III | General Exceptions (incl. right of private defence) | 14-44 |
| IV | Of Abetment, Criminal Conspiracy and Attempt | 45-62 |
| **V** | **Of Offences Against Woman and Child** | **63-99** |
| **VI** | **Of Offences Affecting the Human Body** | **100-146** |
| VII | Of Offences Against the State | 147-158 |
| VIII | Of Offences Relating to Army, Navy and Air Force | 159-168 |
| IX | Of Offences Relating to Elections | 169-177 |
| X | Of Offences Relating to Coin, Currency-Notes, Bank-Notes and Government Stamps | 178-188 |
| **XI** | **Of Offences Against Public Tranquillity** | **189-197** |
| XII | Of Offences By or Relating to Public Servants | 198-205 |
| XIII | Of Contempts of Lawful Authority of Public Servants | 206-226 |
| XIV | Of False Evidence and Offences Against Public Justice | 227-269 |
| XV | Of Offences Affecting Public Health, Safety, Convenience, Decency and Morals | 270-297 |
| XVI | Of Offences Relating to Religion | 298-302 |
| **XVII** | **Of Offences Against Property** | **303-334** |
| XVIII | Of Offences Relating to Documents and to Property Marks | 335-350 |
| XIX | Of Criminal Intimidation, Insult, Annoyance, Defamation, etc. | 351-357 |
| XX | Repeal and Savings | 358 |

**The single most important structural change for us:** the IPC scattered offences against women
across chapters XVI, XVII and XX-A. **BNS pulls them all into one chapter (V, ss.63-99).** So rape,
outraging modesty, stalking, dowry death (80), kidnapping-to-marry (87), 498A-cruelty (85) and
insulting modesty (79) are now contiguous. A "crimes against women" filter is a *section-range*
filter post-2024 and a *scattered-list* filter pre-2024.

**Savings clause: the IPC does not stop appearing in 2025 or 2026 data.** BNSS s.531 preserves the
old law for offences committed before 1 July 2024. FIRs under IPC sections continue to be
registered and investigated for years. **CII 2024 and CII 2025 are genuinely mixed-statute
datasets. Plan for both numbering systems in every year from 2024 onward, indefinitely.**

**Not-yet-notified provision:** BNS **106(2)** (hit-and-run causing death, 10 years) was held in
abeyance after the January 2024 transporters' strike and was not brought into force with the rest
of the Sanhita on 1 July 2024. Confirm its current status before ingesting any 106 data.

### 1.3 IPC → BNS concordance table

**Provenance and warning.** This table was assembled by hand from legal knowledge of both statutes.
Only two rows are independently web-verified in this session (BNS 63 ← IPC 375 rape definition, and
BNS 147 ← IPC 121 waging war; both from Wikipedia). The Ministry of Home Affairs, India Code,
Legislative Department, NCRB and UP Police sites are **all blocked by this session's egress proxy**,
so I could not confirm against a gazette. **Confidence column: H = high (would bet the product on
it), M = medium (structure certain, sub-section number may differ), L = low (verify before use).**
**Do not ship this table without checking it against NCRB Sankalan or the gazette.**

Relation codes: `=` exact; `⊂` BNS narrower; `⊃` BNS wider; `M` many IPC → one BNS (resolution
lost); `S` one IPC → several BNS; `NEW` no IPC predecessor; `GONE` no BNS successor.

#### Homicide and hurt (BNS Ch. VI)

| IPC | Offence | BNS | Rel | Conf | Note |
|---|---|---|---|---|---|
| 299 | Culpable homicide (def) | 100 | = | H | |
| 300 | Murder (def) | 101 | = | H | |
| **302** | **Punishment for murder** | **103(1)** | S | H | 103(2) is **NEW**: murder by a group of 5+ on grounds of race, caste, community, sex, place of birth, language, personal belief (mob lynching) |
| 303 | Murder by life-convict | 104 | = | M | |
| **304** | **Culpable homicide not amounting to murder** | **105** | = | H | |
| **304A** | **Causing death by negligence** | **106(1)** | ⊂ | H | 106(2) hit-and-run **NEW, kept in abeyance** |
| **304B** | **Dowry death** | **80** | = | H | moved to Ch. V |
| 305 / 306 | Abetment of suicide (child/unsound mind; general) | 107 / 108 | = | H | |
| **307** | **Attempt to murder** | **109** | = | H | |
| 308 | Attempt to commit culpable homicide | 110 | = | H | |
| 309 | Attempt to commit suicide | — | GONE | H | only BNS 226 (attempt to suicide to compel a public servant) survives |
| — | **Organised crime** | **111** | NEW | H | previously only state MCOCA-type acts / UAPA |
| — | **Petty organised crime** | **112** | NEW | H | gang theft, pickpocketing, snatching rings, card skimming |
| — | **Terrorist act** | **113** | NEW | H | parallel to UAPA; choice of statute is the SHO's |
| 310 / 311 | Thug | 114 | = | M | |
| 321 / **323** | **Voluntarily causing hurt (def / punishment)** | 115(1) / **115(2)** | = | H | |
| 320 | Grievous hurt (def) | 116 | = | H | |
| 322 / **325** | **Voluntarily causing grievous hurt (def / punishment)** | 117(1) / **117(2)** | S | H | 117(3)/(4) **NEW**: grievous hurt by group of 5+ on identity grounds |
| 324 / 326 | Hurt / grievous hurt by dangerous weapons | 118(1) / 118(2) | M | H | two sections merged into one |
| 326A / 326B | Acid attack / attempt | 124(1) / 124(2) | = | H | |
| 327 / 329 | Hurt or grievous hurt to extort property | 119 | M | M | |
| 330 / 331 | Hurt or grievous hurt to extort confession | 120 | M | M | |
| 332 / 333 | Hurt or grievous hurt to deter public servant | 121 | M | M | |
| 334 / 335 | Hurt or grievous hurt on provocation | 122 | M | M | |
| 328 | Administering stupefying drug | 123 | = | M | |
| 336 / 337 / 338 | Acts endangering life or personal safety | 125 | M | M | three sections merged |
| 339 / 341 | Wrongful restraint | 126(1) / 126(2) | = | M | |
| 340 / 342-348 | Wrongful confinement | 127 | M | M | seven sections merged |
| 349 / 350 / 351 | Force / criminal force / assault (defs) | 128 / 129 / 130 | = | M | |
| 352 | Punishment for assault or criminal force | 131 | = | M | |
| 353 | Assault to deter public servant | 132 | = | M | |
| 354* (see Ch. V) | | | | | *moved out of Ch. VI into Ch. V* |
| 355 / 356 / 357 / 358 | Assault to dishonour / in theft attempt / in confinement attempt / on provocation | 133 / 134 / 135 / 136 | = | M | |

#### Kidnapping, abduction, trafficking (BNS Ch. VI, partly Ch. V)

| IPC | Offence | BNS | Rel | Conf | Note |
|---|---|---|---|---|---|
| 359-361 | Kidnapping (defs) | 137(1) | M | H | |
| **363** | **Punishment for kidnapping** | **137(2)** | = | H | |
| 362 | Abduction | 138 | = | H | |
| 363A | Kidnapping/maiming a child for begging | 139 | = | M | |
| **364 / 364A / 365 / 367** | **Kidnap to murder / for ransom / to secretly confine / for grievous hurt or slavery** | **140** (sub-ss.) | M | M | **four distinct IPC heads collapse into one BNS section — permanent resolution loss** |
| **366** | **Kidnapping/abducting a woman to compel marriage** | **87** | = | H | moved to Ch. V |
| 366A | Procuration of a minor girl | 96 | ⊃ | M | now gender-neutral ("child") |
| 366B | Importation of a girl from a foreign country | 141 | ⊃ | M | now "girl or boy" |
| 368 | Wrongfully concealing a kidnapped person | 142 | = | M | |
| **369** | **Kidnapping a child under 10 to steal from its person** | **97** | = | M | moved to Ch. V |
| 370 / 370A | Trafficking / exploitation of a trafficked person | 143 / 144 | = | H | |
| 371 / 374 | Habitual dealing in slaves / unlawful compulsory labour | 145 / 146 | = | M | |

#### Sexual offences and offences against women (BNS Ch. V)

| IPC | Offence | BNS | Rel | Conf | Note |
|---|---|---|---|---|---|
| 375 | **Rape (definition)** | **63** | ⊃ | **H (verified)** | marital-rape exception age raised 15 → 18 |
| **376(1)/(2)** | **Punishment for rape** | **64(1)/(2)** | = | **H (verified)** | |
| 376(3) / 376AB | Rape of a woman under 16 / under 12 | 65(1) / 65(2) | = | H | |
| 376A | Rape causing death or persistent vegetative state | 66 | = | H | |
| 376B | Intercourse by husband during separation | 67 | = | H | |
| 376C | Intercourse by a person in authority | 68 | = | H | |
| — | **Sexual intercourse by employing deceitful means / false promise of marriage** | **69** | NEW | H | **no IPC predecessor**; previously prosecuted (contestedly) as 376 or 417 |
| **376D / 376DA / 376DB** | **Gang rape (incl. under 16 / under 12)** | **70(1) / 70(2)** | M | H | |
| 376E | Repeat offenders | 71 | = | H | |
| 228A | Disclosure of victim identity | 72 | = | M | |
| **354** | **Assault or criminal force to outrage a woman's modesty** | **74** | = | H | |
| 354A | Sexual harassment | 75 | = | H | |
| 354B | Assault with intent to disrobe | 76 | = | H | |
| 354C | Voyeurism | 77 | = | H | |
| 354D | Stalking | 78 | = | H | |
| 509 | Word/gesture insulting a woman's modesty | 79 | = | H | |
| 312-318 | Miscarriage, child abandonment, concealment of birth | 88-94 | M | M | |
| — | Hiring/employing a child to commit an offence | 95 | NEW | M | |
| 372 / 373 | Selling / buying a child for prostitution | 98 / 99 | = | M | |
| 493-496 | Deceitful cohabitation, bigamy, sham marriage | 81-83 | = | M | |
| 498 | Enticing a married woman | 84 | = | M | |
| **498A** | **Cruelty by husband or his relatives** | **85** (+ 86 def) | = | H | largest single crime-against-women head |
| 377 | Unnatural offences | — | **GONE** | H | **no BNS successor.** Non-consensual sex against men and transgender persons, and bestiality, have no provision |
| 497 | Adultery | — | GONE | H | already void (*Joseph Shine*, 2018) |

#### Property (BNS Ch. XVII)

| IPC | Offence | BNS | Rel | Conf | Note |
|---|---|---|---|---|---|
| 378 / **379** | **Theft (def / punishment)** | 303(1) / **303(2)** | = | H | community service now available for a first theft under ₹5,000 on return of property |
| — | **Snatching** | **304** | NEW | H | **no IPC predecessor.** Pre-2024 series is state-law-dependent (Delhi/Punjab/Haryana amendments) |
| 380 | Theft in a dwelling house | 305 | ⊃ | H | widened to means of transport and places of worship — **"theft in dwelling" and "theft from vehicle" are no longer separable post-2024** |
| 381 / 382 | Theft by clerk or servant / after preparation for hurt | 306 / 307 | = | M | |
| **383-389** (incl. **384**) | **Extortion (all seven sections)** | **308** | M | H | **seven IPC heads collapse into one BNS section** |
| 390 / **392** | **Robbery (def / punishment)** | 309(1) / **309(4)** | = | M | sub-section number is the uncertain part |
| 393 / 394 | Attempt at robbery / hurt caused in robbery | 309(5) / 309(6) | M | M | |
| 391 / **395** | **Dacoity (def / punishment)** | 310(1) / **310(2)** | = | H | |
| 396 | Dacoity with murder | 310(3) | = | M | |
| 397 / 398 | Robbery or dacoity with attempt to kill / armed with deadly weapon | 311 / 312 | = | M | |
| 399 / 402 | Preparation for / assembling for dacoity | 310(4)/(5) | M | L | |
| 400 / 401 | Belonging to a gang of dacoits / thieves | 313 | M | L | |
| 403 / 404 | Dishonest misappropriation | 314 / 315 | = | M | |
| 405-409 | Criminal breach of trust (incl. by servant, banker, public servant) | 316(1)-(5) | M | H | |
| 410-414 | Stolen property (receiving, retaining, assisting concealment) | 317 | M | H | |
| 415 / 417 / 418 / **420** | **Cheating (def / punishment / with knowledge / inducing delivery of property)** | 318(1) / 318(2) / 318(3) / **318(4)** | = | H | **420 → 318(4)** is the single most-used mapping in Indian fraud data |
| 416 / 419 | Cheating by personation | 319(1) / 319(2) | = | H | |
| 421-424 | Fraudulent removal/concealment of property | 320-323 | M | M | |
| 425-440 | Mischief (all forms incl. arson, animal maiming, inundation) | 324-328 | M | M | |
| 441 / 442 | Criminal trespass / house-trespass (defs) | 329(1) / 329(2) | = | H | |
| **447 / 448** | **Punishment for criminal trespass / house-trespass** | **329(3) / 329(4)** | = | H | |
| 443 / 444 | Lurking house-trespass / by night (defs) | 330(1) / 330(2) | = | H | |
| **445 / 446** | **House-breaking / house-breaking by night (defs)** | **330(3) / 330(4)** | = | H | |
| **453-460** (incl. **457**) | **Punishments for lurking house-trespass & house-breaking** | **331(1)-(8)** | M | M | **eight IPC punishment heads collapse into one BNS section.** 457 ≈ 331(4). Our "burglary" category loses its internal structure post-2024 |
| 449 / 450 / 451 | House-trespass to commit an offence punishable with death / life / imprisonment | 332(a)/(b)/(c) | = | M | |
| 452 | House-trespass after preparation for hurt | 333 | = | M | |
| 461 / 462 | Dishonestly breaking open a receptacle | 334 | M | M | |

#### Public order, state, intimidation, documents, misc.

| IPC | Offence | BNS | Rel | Conf | Note |
|---|---|---|---|---|---|
| 141 / 143 | Unlawful assembly (def / punishment) | 189(1) / 189(2) | = | H | |
| 144 / 145 | Joining armed / after dispersal order | 189(3)-(6) | M | M | |
| 149 | Common-object liability of every member | 190 | = | H | |
| 146 / **147** / 148 | **Rioting (def / punishment / armed)** | 191(1) / **191(2)** / 191(3) | = | H | |
| 152 | Assaulting a public servant suppressing a riot | 195 | = | M | |
| 153 | Wantonly provoking a riot | 192 | = | M | |
| 154-156 | Liability of landowner/occupier | 193 | M | L | |
| 159 / 160 | Affray | 194 | M | M | |
| **153A** | **Promoting enmity between groups** | **196** | = | H | |
| 153B | Imputations prejudicial to national integration | 197 | = | M | |
| 121 | Waging war against the Government of India | **147** | = | **H (corroborated)** | |
| 121A / 122 / 123 | Conspiracy / collecting arms / concealing design | 148 / 149 / 150 | = | M | |
| **124A** | **Sedition** | **— (152 is a new offence)** | GONE | H | BNS 152 "act endangering sovereignty, unity and integrity of India" is **not** a renumbering. **Any sedition time series ends 2024-06-30** |
| 166A(c) | Public servant failing to record information (sexual offences) | 199 | = | M | the anti-burking provision |
| 188 | Disobedience to a public servant's order | 223 | = | M | |
| 269 / 270 | Negligent / malignant act spreading infection | 271 / 272 | = | M | |
| **279** | **Rash driving on a public way** | **281** | = | H | |
| 292 / 293 / 294 / 294A | Obscene material / sale to a child / obscene acts / lottery office | 294 / 295 / 296 / 297 | = | M | |
| 295 / **295A** / 296 / 297 / 298 | Religious offences | 298 / **299** / 300 / 301 / 302 | = | H | |
| 463 / 465 | Forgery (def / punishment) | 336(1) / 336(2) | = | H | |
| 466 / 467 / 468 / 469 | Forgery of court record / valuable security / for cheating / to harm reputation | 337 / 338 / 336(3) / 336(4) | S | M | |
| 470 / 471 | Forged document / using it as genuine | 340(1) / 340(2) | = | M | |
| 477A | Falsification of accounts | 344 | = | M | |
| 489A-489E | Counterfeiting currency notes | 178-181 | M | M | |
| 503 / **506** / 507 | **Criminal intimidation (def / punishment / anonymous)** | 351(1) / **351(2)-(3)** | M | H | |
| 504 / 505 | Insult to provoke breach of peace / public-mischief statements | 352 / 353 | = | H | |
| 499-502 | Defamation | 356 | M | H | community service added |
| 508 / 510 | Divine-displeasure inducement / drunken misconduct | 354 / 355 | = | M | |
| 120A / 120B | Criminal conspiracy | 61 | = | H | |
| **511** | **Attempt to commit an offence** | **62** | = | H | |
| 171A-171I | Election offences | 169-177 | = | M | |

#### Engineering consequences of the shape of this table

1. **The relation is not a function.** Build `statute_xwalk(from_statute, from_section,
   to_statute, to_section, relation, comparable, note)`, not a dictionary.
2. **`relation = M` rows mean permanent loss of resolution.** Property crime is the worst hit:
   extortion (7→1), house-breaking punishments (8→1), kidnapping-for-X (4→1), wrongful
   confinement (7→1). **Our L3 crime heads for property must be defined at the coarser,
   BNS-compatible level, or they will break at 2024-07-01.**
3. **`relation = NEW` rows must be excluded from any pre/post-2024 comparison** and flagged in the
   UI as "new offence category, 2024 onward".
4. **`relation = GONE` rows must terminate their series**, not show as zero. A zero is a lie.
5. Because escalation and merger both exist, **the only robust unit of comparison across the
   2024 boundary is our own L2 `group`** (e.g. `burglary`, `robbery_dacoity`, `sexual_offence`),
   not L3, and never the section.

### 1.4 Special & Local Laws (SLL) — and why they must never be choropleth-mapped

SLL is **~40% of all cognizable crime**. Wikipedia's *Crime in India* article reports for 2023:
62,41,569 cognizable crimes = 37,63,102 IPC + **24,78,467 SLL** (39.7%), overall rate 448.3 per
100,000 (*verify against the NCRB volume — these figures are Wikipedia-sourced*).

SLL splits into two very different things:

| Type | Enacted by | Examples | Cross-state comparable? |
|---|---|---|---|
| **Special laws (central)** | Parliament, uniform text nationwide | NDPS 1985, Arms Act 1959, POCSO 2012, IT Act 2000, SC/ST (PoA) Act 1989, PC Act 1988, Immoral Traffic (Prevention) Act 1956, Dowry Prohibition Act 1961, JJ Act 2015, Motor Vehicles Act 1988, Explosive Substances Act 1908, Railways Act 1989 | **Text yes, enforcement no** |
| **Local laws (state)** | State legislatures, text differs or does not exist | State Excise/Prohibition Acts, Gambling Acts, Cattle Preservation / Cow Slaughter Acts, State Police Acts, Prevention of Begging Acts, Shops & Establishments Acts, Sand-mining rules, Cinematograph Acts | **No. Not even in principle.** |

**Why SLL counts must not be compared across states on a map — the five reasons, in order of severity:**

1. **The offence does not exist in the comparison state.** Bihar's Prohibition and Excise Act, 2016
   criminalises possession and consumption of alcohol; Gujarat has had prohibition since 1960. These
   two states generate *hundreds of thousands* of excise FIRs a year for conduct that is lawful in
   Maharashtra. A national "SLL crime rate" choropleth paints Bihar and Gujarat dark red **because
   they criminalised drinking**, and a reader will read that as "dangerous". This alone is
   disqualifying.
2. **Cattle-preservation / cow-slaughter acts** are stringent and heavily enforced in UP, MP,
   Gujarat, Haryana, Rajasthan and Maharashtra, and absent or minimal in Kerala, West Bengal, Goa
   and most of the North-East. Zero in Kerala is *"not an offence"*, not *"never happens"*.
3. **Gambling and online-gaming** acts are state-adapted versions of the Public Gambling Act, 1867,
   with divergent recent amendments (Tamil Nadu, Karnataka, Telangana). Both the offence and the
   enforcement drive differ.
4. **Whether the police register it at all.** In several states, excise enforcement sits with a
   separate Excise Department whose cases never become police FIRs and therefore never reach NCRB.
   Motor Vehicles Act offences are processed as challans (not FIRs) almost everywhere, but a few
   states do register them — those states' SLL totals explode for a purely procedural reason.
5. **SLL is police-initiated, not victim-initiated.** Drugs, arms, excise, gambling and
   prohibition cases are found by the police, not reported by a victim. **Their count measures
   police activity and political direction, not risk to a resident.** For the question our product
   answers — *"is this neighbourhood safe to walk through at night?"* — SLL is close to pure noise.

**Rule, enforced in the schema, not in a caveat box:** every crime head carries
`comparable_across_states` and `statute_jurisdiction` (`central` | `state:<state_key>`). The map
layer **refuses** to render a choropleth for a head with `comparable_across_states = false`; it
offers only a within-state view, with the enacting statute named on the legend. Central special
laws (POCSO, NDPS, Arms, SC/ST PoA, IT Act) may be mapped nationally **with an enforcement-intensity
warning**, because uniform text does not imply uniform policing.

### 1.5 NCRB crime heads and how they nest

**NCRB does not publish a stable numeric crime-head code dictionary.** In the report the heads are
identified by a serial number within a table; in the machine-readable extracts they are identified
by **label strings** (`Group_Name`, `Sub_Group_Name`) which drift between editions ("Rape" →
"Rape (Sec 376 IPC)" → "Rape (Sec.376 IPC)"). **The practical primary key is a
(year, raw_label) pair, and it is unstable.**

Nesting, in three levels that behave differently:

| Level | Example | Sums? |
|---|---|---|
| **Sub-head → head** (within one table) | "Murder (Sec 302)" + "Attempt to murder (307)" + … → "Total Offences Affecting the Human Body" | **Yes**, by construction |
| **Head → chapter total** (within one chapter) | Human body + Property + Public tranquillity + … → "Total Cognizable IPC Crimes" | **Yes** |
| **Across chapters** | Ch.1 (IPC) + Ch.3 (Crime against Women) | **NO — massive double-count** |

The cross-cutting chapters are **views over the same FIRs**, not additional crime:

| Cross-cut chapter | What it re-aggregates |
|---|---|
| Crime against Women | BNS/IPC 302/304B/498A/354/354A-D/376/509/366A/366B/363-373 **+** Dowry Prohibition Act, Indecent Representation of Women Act, Immoral Traffic (Prevention) Act, PWDVA |
| Crime against Children | kidnapping, murder, foeticide, POCSO, JJ Act, Child Marriage Act |
| Crime against SC / ST | IPC/BNS heads **+** SC/ST (PoA) Act |
| Crime against Senior Citizens | IPC/BNS heads filtered by victim age |
| Economic Offences | cheating, forgery, criminal breach of trust **+** central acts |
| Cyber Crimes | IT Act **+** IPC/BNS heads committed by electronic means |
| Human Trafficking | 370/370A + ITPA + JJ + Bonded Labour Act |
| Missing Persons, Juveniles in Conflict with Law, Disposal, Police strength | separate frames entirely |

**Ingestion rule:** every fact row carries `source_table_ref` and a `rollup_safe` flag.
Aggregation is permitted only within a single `source_table_ref`. A pipeline that adds
"Crime against Women" to "Total IPC Crimes" is producing a number that exists nowhere.

**Known definitional breaks to encode as `series_break_flags`:**

| Date | Break |
|---|---|
| 14 Nov 2012 | POCSO Act in force — child sexual offences move to an SLL head |
| 3 Feb 2013 | **Criminal Law (Amendment) Act 2013** redefines rape (375) to cover non-penile penetration and creates 354A-D, 326A/B, 370. **Reported rape jumps in 2013 for definitional reasons.** Any sexual-offence series crossing 2013 is broken |
| CII 2014 | NCRB switches from **53 "mega cities" (1M+)** to **19 "metropolitan cities" (2M+ per Census 2011)** — the city panel changes shape |
| CII 2016 | Published Nov 2017 with a reduced and restructured table set; several long-running tables dropped |
| CII 2017 | Published ~Oct 2019 — a ~22-month lag; format changed again |
| ~2017 | "Attempt to commit rape (376/511)" split out as its own head |
| **1 Jul 2024** | **BNS/BNSS/BSA.** CII 2024 contains ~6 months of IPC FIRs and ~6 months of BNS FIRs, plus IPC registrations continuing under BNSS s.531 savings |
