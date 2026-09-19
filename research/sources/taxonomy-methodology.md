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

---

## 2. The principal offence rule

### 2.1 What it is

NCRB's counting unit is the **FIR (case), not the offence**. Where one FIR discloses several
offences, **only the offence with the most severe maximum punishment is counted**, and it is
counted **once**. The rule is stated in the "Concepts and Definitions" / explanatory note at the
front of every *Crime in India* volume. Its purpose is to prevent a single incident inflating the
total; its cost is that every subordinate offence in that FIR becomes statistically invisible.

Worked examples of what disappears:

| FIR contains | NCRB counts | What vanishes |
|---|---|---|
| Murder (103) + robbery (309) + hurt (115) | Murder | the robbery and the hurt |
| Rape (64) + murder (103) | Murder | **the rape** |
| Kidnapping (137) + rape (64) | Rape | the kidnapping |
| House-breaking (331) + theft (303) | House-breaking | the theft |
| Robbery (309) + grievous hurt (117) | Robbery | the grievous hurt |
| Dowry death (80) + cruelty (85) | Dowry death | the 498A-cruelty |
| Theft (303) + Arms Act s.25 | **Arms Act (SLL)** | **the theft leaves the BNS map entirely** |
| BNS 65 (rape of a child) + POCSO s.6 | counted once (NCRB de-duplicates explicitly) | nothing, but the head it lands in varies |

### 2.2 How much does it undercount?

**NCRB publishes no estimate, and I found no official one.** Anyone who gives you a single
percentage is guessing. What can be said rigorously:

1. **The undercount is bounded below by the number of distinct offence heads per FIR.** Indian FIRs
   routinely stack sections; a typical assault FIR carries 323 + 504 + 506 (now 115 + 352 + 351),
   a typical burglary carries 457 + 380 (now 331 + 305). From ordinary charging practice the mean
   is on the order of **1.7-2.6 distinct offence sections per FIR**, implying the count of
   *offences* is roughly **1.7x-2.6x** the count of *cases*.
2. **It is not spread evenly.** The shortfall sits almost entirely in the subordinate heads.
3. **A published, checkable illustration using NCRB's own printed heads.** Unlawful killing in
   India is split across at least four heads that a lay reader would call "murder":
   murder (302/103), culpable homicide not amounting to murder (304/105), dowry death (304B/80),
   and deaths within rape cases (376A/66) — plus abetment of suicide (306/108). A map that renders
   only the s.302 head **undercounts unlawful violent death by roughly a quarter to a third**,
   before the principal-offence rule is even considered. *(Order-of-magnitude: CII reports on the
   order of 28-29k murders against ~6-7k dowry deaths and ~3-4k culpable homicides. Verify the
   exact figures against CII Table 1A.2 / Chapter 3 before publishing any of them.)*

**Phase-2 experiment — measure it ourselves, it is cheap.** Several states expose FIR-level data
(Kerala Police FIR search, Delhi Police FIR portal, Telangana, Madhya Pradesh CCTNS citizen
portals — see the `state-portals` dossier). From a sample of FIRs, compute:

```
sections_per_fir          = mean(count(distinct section) per FIR)
multi_head_rate           = P(FIR maps to >= 2 distinct crime_key)
censoring_rate(crime_key) = 1 - (FIRs where crime_key is principal) / (FIRs where crime_key appears)
```

`censoring_rate` **per head** is the correction factor the map needs. Publishing it — even as a
rough per-head multiplier with a confidence interval — would be a genuinely novel contribution and
would immunise us against the "your assault map is nonsense" critique.

### 2.3 Exactly how this distorts a category-level map

| Head class | Examples | Effect |
|---|---|---|
| **Apex** (never subordinate) | murder 103, rape 64/65, dacoity 310, terrorist act 113 | **Complete.** These maps are trustworthy, modulo reporting |
| **Middle** (subordinate only to apex) | robbery 309, house-breaking 331, kidnapping 137, acid attack 124 | **Partially censored.** The boundary between adjacent property categories is set by escalation, and escalation rates differ by area |
| **Subordinate** (usually stacked under something worse) | hurt 115, grievous hurt 117, criminal intimidation 351, trespass 329, mischief 324, wrongful restraint 126, insult 352 | **Heavily and non-randomly censored** |

The subordinate-head distortion is **signal inversion, not noise**:

> A district where assaults routinely escalate into robberies and homicides will show **fewer**
> recorded assaults than a district where assaults stay assaults. The "assault" layer therefore
> makes the most violent districts look calm.

Three further consequences an engineer must design around:

- **Category counts are not additive to anything meaningful.** Σ(category counts) = total FIRs,
  **not** total offences. Any "share of crime that is X" figure built from NCRB is wrong.
- **Cross-category ratios are corrupted.** The rape:murder ratio is biased down everywhere,
  because every rape-murder is filed as a murder.
- **IPC/SLL leakage creates holes in specific places.** Where an SLL offence outranks the BNS one
  (NDPS commercial quantity, POCSO s.6, Arms Act s.25, SC/ST PoA), the whole FIR is counted under
  SLL. **A "sexual offence" layer built from BNS 63-71 alone will massively undercount child
  sexual offences, which mostly sit under POCSO.** Our `crime_key` for sexual offences must union
  BNS heads with POCSO heads and de-duplicate.

**Product rules that follow:**
1. Publish at **L2 group** level by default; expose L3 heads only for apex offences.
2. Carry `principal_offence_rule = true` on every NCRB-derived fact, and make the UI
   **refuse to render a crime-mix pie chart** from rows where it is true.
3. Never compare the *level* of a subordinate head across districts without the censoring
   correction from §2.2.

---

## 3. Denominators

### 3.1 The state of the count

| Item | Status as of **2026-09-19** |
|---|---|
| **Census 2011** | The last completed census. Reference date 00:00 hrs, **1 March 2011**. Total population **1,210,854,977** (verified). 640 districts. **The only real district-level population count we have, and it is 15.5 years old.** |
| **Census 2021** | **Never held.** Postponed in 2020 for COVID-19, then deferred repeatedly for six years. There is no 2021 count and there never will be. |
| **Census 2027** | **In progress now.** House-listing / HLO phase **1 April 2026 – September 2026** (running as this is written). Population enumeration **9-28 February 2027**, reference date 1 March 2027. Snow-bound Himalayan areas enumerated **August-September 2026**, reference date **1 October 2026**. **Caste enumeration included for the first time since 1931.** (Verified via Wikipedia *Census of India*, 2026-09-19.) |
| **When we get usable numbers** | Provisional totals realistically **mid-to-late 2027**; Primary Census Abstract with district-level figures **2028**; ward/village-level tables **2028-2029**. **Plan for no new official district population before 2028.** |

### 3.2 Official projections

**"Population Projections for India and States 2011-2036"**, *Report of the Technical Group on
Population Projections*, National Commission on Population, **Ministry of Health & Family Welfare,
July 2020**. This is the authoritative official projection and the one NCRB uses.

- Projects **to 2036**, by **state/UT**, by sex, by five-year age group, with a **rural/urban split**.
- **It does not go below state level. There are no official district projections in India.**
- Reference points (Wikipedia *Demographics of India*, 2026-09-19, mixing TG and UN WPP 2024
  figures — **verify each against the TG report before use**): 2011 census 1,210,854,977;
  ~1.414bn (2021); ~1.438bn (2023, UN); ~1.451bn (2024, UN); ~1.461bn (2025/26).

### 3.3 What NCRB itself uses (and the trap inside it)

| NCRB geography | Denominator NCRB uses | Consequence |
|---|---|---|
| India, State/UT | **Projected mid-year population** from the TG report | Reasonable. Level roughly right |
| **District** | **Census 2011 district population** | Rates are inflated by ~19-21% nationally *and unevenly across districts* |
| **Metropolitan city** | **Census 2011 city / urban-agglomeration population** | Same problem, worse — cities grew fastest |
| Crime against children | Projected **child** population | |

*(High confidence, but the exact wording is in the CII explanatory note, which I could not fetch —
`ncrb.gov.in` is blocked here. Confirm before quoting NCRB's methodology in the product.)*

### 3.4 The error from a 2011 denominator in 2025

**The uniform part is harmless; the differential part is the problem.**

- **Uniform:** India grew from 1.211bn (2011) to ~1.44-1.46bn (2026) — **+19% to +21%**. Using
  2011 everywhere inflates every rate by about a fifth. Rank order is preserved, so a *map* is not
  destroyed by this. It is a labelling error, not a ranking error.
- **Differential:** district growth over 2011→2026 ranges from roughly **+10-15%** (much of Kerala,
  Tamil Nadu, rural West Bengal, Himachal) to **+60-100%** (Gurugram, Gautam Buddha Nagar,
  Bengaluru Urban, Rangareddy, Medchal-Malkajgiri, Thane, Surat, Ghaziabad, Pune). The 2001→2011
  decadal rates already showed this: Gurgaon ~+74%, Rangareddy ~+48%, Bengaluru Urban ~+47%,
  Surat ~+42%, Gautam Buddha Nagar ~+51%, against a national ~+17.7%. *(Standard Census 2011 PCA
  figures; verify against the PCA before publishing any specific number.)*

> **Net effect: a crime-rate map built on Census 2011 denominators overstates the rate in
> fast-growing peri-urban districts by roughly 40-80% relative to slow-growing ones.**
> Gurugram, Noida, Bengaluru, Thane, Pune, Surat, Rangareddy and Medchal will be painted red for
> a reason that has nothing to do with crime. This is a defamation-grade error, and it is the kind
> of error a journalist can reproduce in ten minutes.

### 3.5 Recommendation

**Do not use Census 2011 raw, and do not use NCRB's published rates.** Compute our own, versioned:

1. **Base**: Census 2011 district populations, on a **frozen 2011 district geometry** (see §4).
2. **State trend**: apply the **TG (NCP/MoHFW 2020) state-level projected growth** for the target
   year, separately for rural and urban using each district's 2011 urban share.
3. **Within-state differential**: apply each district's own **2001→2011 decadal growth rate,
   shrunk toward the state mean** (shrinkage λ ≈ 0.5-0.7 — extreme growth mean-reverts; an
   unshrunk extrapolation of Gurgaon's 74% would be absurd by 2026). Rescale so district sums
   reproduce the TG state total exactly.
4. **Cross-check annually against ECI electoral rolls.** The Election Commission publishes elector
   counts per Assembly Constituency (and per district) and revises them every year. **This is the
   only annually-refreshed, official, sub-state population signal India has.** Electors ≈ adults
   18+; the elector-to-population ratio is stable enough within a state to flag districts where our
   projection is badly wrong. Secondary proxies: PMJAY/Ayushman enrolment, Aadhaar saturation,
   NFHS-5 sampling frames, SECC 2011.
5. **Carry provenance and uncertainty on every rate**: `denominator_version`,
   `denominator_method`, `denominator_ci_low/high`. **Never render a rate without its band.**
6. **Default the UI to counts, not rates.** Offer "per 100,000" as an explicit toggle, and show
   the denominator and its vintage in the tooltip. Suppress rates where the count is below a
   minimum (e.g. <20 cases) — small numbers over uncertain denominators produce vivid, false reds.
7. **Re-base and re-version the whole panel when Census 2027 district tables land (~2028).**
   Keep the old version queryable so published figures remain reproducible.

**One line:** *Build a versioned district-year population panel — Census 2011 district base ×
state-level TG projection growth, differentiated within-state by shrunk 2001-2011 district growth,
cross-checked annually against ECI elector counts — and attach `denominator_method` plus an
uncertainty band to every rate; re-base on Census 2027 (~2028).*

---

## 4. Geographic comparability over time

### 4.1 How many districts

| Year | Districts | Source / confidence |
|---|---|---|
| 1991 Census | **466** | Standard Census of India figure — model knowledge, **verify against Census Administrative Atlas** |
| 2001 Census | **593** | Standard Census of India figure — model knowledge, **verify** |
| **2011 Census** | **640** | Standard Census of India figure — model knowledge, **verify against Census 2011 PCA/Administrative Atlas**. This is the reference geometry we should freeze to |
| ~2021 | ~736-748 | LGD-derived; approximate, **verify against lgdirectory.gov.in** |
| **Dec 2025** | **800** | **VERIFIED** — Wikipedia *List of districts in India* / *Districts of India*, "as of 9 December 2025", incl. Mahe and Yanam (census districts) and a temporary Maha Kumbh Mela district, excl. Itanagar Capital Complex |

> **640 → 800 is +160 districts (+25%) since the last census.**
> **One district in five on a current map has no 2011 population of its own and no pre-split NCRB
> history.**

### 4.2 The worst cases

| Case | What happened | Damage |
|---|---|---|
| **Telangana** | **10** districts at formation **2 June 2014** → **31** on **11 October 2016** (21 created in one day) → **33** on **17 February 2019** (Mulugu, Narayanpet). **VERIFIED** | 3.3x in under 5 years. Nothing before Oct 2016 joins to anything after it without a village-level crosswalk |
| **Andhra Pradesh** | **13 → 26** districts on **4 April 2022** — a single-day doubling (current Wikipedia list shows 28; **verify**) | An entire state's district panel is discontinuous at one date |
| **Rajasthan** | **33** (2011) → **50** (August 2023, 19 new districts + 3 divisions) → **41** (**28 December 2024**, 17 of the 19 new districts **scrapped**). Wikipedia's current list shows 41, consistent with the reversal | **Reorganisation that reversed.** Breaks the universal engineering assumption that districts only split. Two schema changes in 16 months |
| **Assam** | 27 (2011) → many created 2015-16 (Charaideo, Hojai, W. Karbi Anglong, Biswanath, S. Salmara-Mankachar, Majuli) → **four districts MERGED BACK on 1 January 2023** (Biswanath→Sonitpur, Hojai→Nagaon, Bajali→Barpeta, Tamulpur→Baksa) → 35 now | Another reverse reorganisation; merges are harder to crosswalk than splits |
| **Arunachal Pradesh** | 16 (2011) → **27** now, via a near-continuous stream of splits 2014-2018 (Namsai, Kra Daadi, Siang, Kamle, Lepa Rada, Pakke-Kessang, Shi-Yomi, Lower Siang) | Small base populations, so every split produces wildly volatile rates |
| **Jammu & Kashmir** | **J&K Reorganisation Act, 2019** — assent **9 August 2019**, effective **31 October 2019**. State of J&K (22 districts) → **UT of J&K (20 districts)** + **UT of Ladakh (Leh, Kargil; now 7)**. **VERIFIED** | A **state-level** break, not just district. India's state/UT list changed: 29 states + 7 UTs → 28 + 9 (31 Oct 2019) → **28 + 8** after Dadra & Nagar Haveli and Daman & Diu merged on **26 January 2020**. Any all-India state panel must handle both |
| **Madhya Pradesh** | 50 (2011) → **55** (Niwari 2018; Maihar, Pandhurna, Mauganj 2023-24) | |
| **Uttar Pradesh** | **Revenue districts are stable at 75** since ~2012. **The churn is in police geography** — Lucknow & Gautam Buddha Nagar commissionerates (Jan 2020), Kanpur & Varanasi (Mar 2021), Agra, Ghaziabad, Prayagraj (late 2022) | **For crime data this is a bigger break than any revenue-district change**, because NCRB's reporting units are police units (§5) |
| **West Bengal** | 19 (2011) → 23 by 2017 (Alipurduar 2014; Kalimpong, Jhargram, Paschim/Purba Bardhaman 2017); 7 more announced 2022, partially implemented; Wikipedia's current list shows **27** (**verify**) | |
| **Renames (silent killers)** | Gurgaon→**Gurugram** (2016), Allahabad→**Prayagraj** (2018), Faizabad→**Ayodhya** (2018), Aurangabad→**Chhatrapati Sambhajinagar** & Osmanabad→**Dharashiv** (2023), Hoshangabad→**Narmadapuram** (2021), Bangalore→Bengaluru, Mysore→Mysuru, Belgaum→Belagavi, Gulbarga→Kalaburagi, Bellary→Ballari, Bijapur→Vijayapura, Tumkur→Tumakuru, Shimoga→Shivamogga | A name-join silently produces a phantom "new" district and a phantom "vanished" district on the same map |

### 4.3 What this does to a time series

1. **A split produces a fake crime drop.** The parent district's counts fall by the share that went
   to the child. On a trend line this looks like a policing success. It is arithmetic.
2. **Numerator and denominator split differently.** Crime is reported by *police* jurisdiction;
   population is counted by *revenue* boundary. When a district splits, the two do not split on the
   same line or on the same date. A newly-created district's crime *rate* can be arbitrary.
3. **NCRB district tables are keyed on name strings**, and the names change (§4.2). A naive join
   loses rows silently.
4. **NCRB district tables are police districts, not revenue districts** — so the key is neither
   the Census district nor the LGD district (§5).
5. **Merges are worse than splits.** A split can be apportioned. A merge destroys the
   distinction permanently going forward (Assam 2023, Rajasthan 2024).

### 4.4 Recommended strategy

**Freeze to Census 2011 for anything with a time axis; use LGD for anything about "now".**

- **Two canonical geographies, both stored, never mixed:**
  - `geo_vintage = 'c2011'` — the **640 Census 2011 districts**. The only geography with a real
    population count, a published boundary family (Census Administrative Atlas / DataMeet
    maps / SHRUG) and complete NCRB coverage since 2001. **Every chart with a time axis uses this.**
  - `geo_vintage = 'lgd'` (snapshotted, e.g. `lgd2026-04`) — the current administrative set, keyed
    on the **LGD (Local Government Directory) district code**. LGD is the only government-wide
    district identifier with codes, effective dates and a change history, and it is what MoSPI/NIC
    systems use. **Every "what is happening in my district now" view uses this.**
- **Store both codes on every geo row**, plus a `name_aliases[]` history with effective dates.
  **Never join on a name. Ever.** A name join is the single most common way an Indian data pipeline
  silently loses a district.
- **Build a weighted many-to-many crosswalk**:
  `geo_xwalk(from_geo_key, from_vintage, to_geo_key, to_vintage, share, basis, source, confidence)`.
  Derive `share` from **2011 sub-district/village-level population**, because new districts are
  constituted from **whole tehsils and whole villages** by state gazette notification — so the
  split is exactly resolvable at that level, and only at that level.
- **Backbone: SHRUG** (Development Data Lab). It publishes village/town-level keys linking the
  1991, 2001 and 2011 censuses plus a district-level crosswalk, which is exactly the hard part
  already done. Extend it *forward* past 2011 using the state gazette notifications that list each
  new district's constituent tehsils. *(SHRUG's site is egress-blocked here; verify the current
  distribution and licence in Phase 2.)*
- **Publish two series, labelled, never blended:**
  - **(A) "Current districts"** — best resolution for today, no history before the district existed.
  - **(B) "2011-frozen districts"** — child-district counts re-aggregated up to the 2011 parent.
    **Any line chart, any "vs last year", any trend colour uses (B).**
- **Flag every district-year cell** with `geo_stability ∈ {stable, split_after, merged_after,
  renamed, reconstituted, jurisdiction_recut}` and **break the trend line visually** where it is
  not `stable`. A dotted segment with a hover note costs one afternoon and prevents the single most
  common misreading.

---

## 5. Urban vs rural, and commissionerate geography

### 5.1 What NCRB actually reports

NCRB reports cities **separately from, and in addition to, districts** — but the city rows are a
**subset** of the state rows, not an increment.

- The city panel definition **changed at CII 2014**: from **"mega cities", population 1 million+
  per Census 2011 (53 cities)** to **"metropolitan cities", population 2 million+ per Census 2011
  (19 cities)**. *(The brief says 1M+; the current threshold is 2M+. Verify the exact list and
  threshold against the CII volume — `ncrb.gov.in` is blocked here.)* The 19 are approximately:
  Ahmedabad, Bengaluru, Chennai, Coimbatore, Delhi, Ghaziabad, Hyderabad, Indore, Jaipur, Kanpur,
  Kochi, Kolkata, Kozhikode, Lucknow, Mumbai, Nagpur, Patna, Pune, Surat.
- **The threshold is frozen on Census 2011.** Cities that crossed 2 million after 2011 are still
  absent from the city panel 15 years later.

### 5.2 The double-counting risk

| Risk | Mechanism |
|---|---|
| **City + state double-count** | Metropolitan-city tables **re-report** crimes already counted in the state and district tables. `state_total + city_total` counts the city twice |
| **City + district double-count** | The district tables already contain rows like "Mumbai (City)", "Mumbai Suburban", "Bengaluru City" — these *are* the commissionerates. The metropolitan table repeats them |
| **Railways** | GRP (Government Railway Police) crime is reported in **separate railway tables** and is **not** in the district counts. Ignore it → a hole along railway land in every city. Add it to the district → double-count where the state also reports it |

**Rule:** treat `geo_level` as a partition, not a hierarchy to be summed. Store city rows with
`geo_level='commissionerate'` and a `contained_in` pointer, and make the aggregation layer refuse
to sum across levels.

### 5.3 The polygon mismatch (the part nobody notices)

For a metropolitan city, **NCRB's numerator and denominator come from different polygons**:

- **Numerator** = crimes recorded by the **police commissionerate**, whose jurisdiction is
  defined by a **state gazette notification** listing police stations.
- **Denominator** = the **Census 2011 city / urban agglomeration** population.

These are not the same area anywhere. Delhi Police covers the whole NCT; the Delhi UA is a
different polygon again. Bengaluru City Police covers materially less than Bengaluru Urban
district. Every published NCRB metropolitan crime *rate* therefore has a definitional error before
any of the problems in §3 are applied.

### 5.4 The gap risk (the one that will silently corrupt our pipeline)

Where a commissionerate is carved out of a revenue district, the residual becomes a separate
"rural" police unit. **One revenue district becomes two or three NCRB rows:**

> Pune district → **"Pune City"** (commissionerate) + **"Pimpri-Chinchwad"** (commissionerate,
> created August 2018) + **"Pune Rural"** (SP).

If the pipeline joins NCRB police-district rows to LGD revenue districts **by name**,
"Pimpri-Chinchwad" matches no revenue district, is dropped, and **Pune's counts silently lose their
most populous urban chunk.** The same pattern applies to Nagpur, Nashik, Thane/Mira-Bhayandar,
Ahmedabad, Surat, Lucknow, Kanpur, Bhopal, Indore, Jaipur, Ludhiana, Hyderabad/Cyberabad/
Rachakonda, Bengaluru City/Bengaluru Rural, Chennai, Kolkata/Bidhannagar/Barrackpore/Howrah.

**New commissionerates also create mid-series breaks**, splitting one district's counts into two
rows from one year to the next: UP (Lucknow, Gautam Buddha Nagar — Jan 2020; Kanpur, Varanasi —
Mar 2021; Agra, Ghaziabad, Prayagraj — late 2022), MP (Bhopal, Indore — Dec 2021), and many others.
**Wikipedia's *Law enforcement in India* (verified 2026-09-19) states 68 cities and suburban areas
currently operate under the commissionerate system.**

### 5.5 The hard ceiling

> **India publishes no national polygon layer for police jurisdictions at any level** —
> not commissionerates, not police districts, not police stations. The jurisdiction exists only as
> a gazette notification listing police-station names. To draw a commissionerate we would have to
> digitise every police-station jurisdiction and union them, and police-station jurisdictions are
> themselves undigitised nearly everywhere.

The finest **authoritative** polygon in India is the **Census 2011 village / town**. Police-station
polygons exist as one-off state GIS efforts in a handful of places (Telangana, Delhi, Kerala).

**This is the gap between us and police.uk and it is not closable in Phase 1.** police.uk can do
street-level because UK forces publish snapped, anonymised point data under a defined
anonymisation standard. India has no equivalent. **Do not render a dot where we have a district
count.** Fabricated precision is the fastest route to both a correction and a lawsuit.

---

## 6. Reported vs actual

### 6.1 Under-reporting: what is actually evidenced

| Crime category | Evidence | Figure |
|---|---|---|
| **Sexual violence (general)** | Independent analyses of NFHS data, as summarised in Wikipedia *Rape in India* (**verified** 2026-09-19) | **>90% of sexual assaults go unreported** |
| **Rape** | **NCRB's own 2006 report** (cited in the same article) | **71% of rapes went unreported** |
| **Sexual assault** | Livemint, 25 October 2015, *"99% cases of sexual assaults go unreported, govt data shows"* — an NFHS/NCRB comparison | **~99%** (media-derived; treat as an upper bound) |
| **Spousal violence** | NFHS-4/NFHS-5: ~29-30% of ever-married women 18-49 report spousal physical/sexual violence; only ~14% of those ever sought help and **only ~1.5% sought help from the police** | **>98% never reaches the police.** *(Model knowledge — verify against the NFHS-5 national report, Ch. 15.)* |
| **Marital rape** | **Legally unreportable.** Sexual intercourse by a man with his own wife aged 18+ is excepted from BNS 63 | A structural zero, not a behavioural one |
| **Global benchmark** | UN Women, cited in the same article | ~11% of rape/sexual assault ever reported |

For property crime the driver is different and just as strong: **the insurance/utility of an FIR**.
Vehicle theft is reported at a high rate because an FIR is required for an insurance claim and for
the RTO. Mobile-phone theft, pickpocketing and snatching are reported at a low rate because the
recovery expectation is near zero and the transaction cost of the police station is high. **So the
reported-crime mix is shaped by the paperwork value of an FIR, not by the incidence of crime.**

### 6.2 Burking — police refusal to register

"Burking" is the Indian term of art for suppressing crime registration to keep figures down.

- **Legal duty**: CrPC s.154 (now **BNSS s.173**) — registration of an FIR is mandatory where the
  information discloses a cognizable offence.
- **Lalita Kumari v. Government of Uttar Pradesh, (2014) 2 SCC 1** (Constitution Bench,
  12 November 2013) held registration **mandatory**, with preliminary inquiry permitted only in
  specified categories (matrimonial/family, commercial, medical negligence, corruption, abnormal
  delay) and capped at 7 days.
- **IPC 166A(c)** (Criminal Law (Amendment) Act 2013) → **BNS 199** criminalises a public servant's
  failure to record information about specified sexual offences. Recorded convictions under it are
  negligible.
- **BNSS s.173(3) reintroduced a discretionary preliminary inquiry (up to 14 days) for cognizable
  offences punishable with 3-7 years** — a partial statutory rollback of *Lalita Kumari*.
  **This is live and it matters for us: a fall in registered crime in 2024-25 may be a statutory
  artefact rather than a real improvement.** Flag it on every 2024+ series.
- Institutional acknowledgement: the **Padmanabhaiah Committee on Police Reforms (2000)** and the
  **Second Administrative Reforms Commission, 5th Report, "Public Order" (2007)** both identify
  non-registration as systemic. The **Status of Policing in India Report** series
  (Common Cause / Lokniti-CSDS, 2018, 2019, 2023, 2025) surveys citizens and police on exactly
  this. *(All egress-blocked here; verify in Phase 2.)*

**Observable statistical signatures of burking** — each is a usable detector:

| Signature | Example |
|---|---|
| A state with one of the **highest recorded IPC crime rates** that is by every independent measure among the safest | **Kerala.** Kerala's rank is a registration artefact, and it is the clearest single proof of the whole problem |
| A **step change** in recorded crime after a change of DGP/government or a "free registration" directive | Delhi's recorded rapes rose roughly 2.5x between 2012 and 2013 after the December 2012 gang rape and the directives that followed. The crime did not rise 2.5x; the registration did |
| **High murder rate + low total IPC rate** | The signature of low registration of non-lethal crime — murder is hard to suppress, everything else is not |

**The anchor trick, and I recommend we build it:** murder is the **least-burkable** series (there is
a body, and BNSS/CrPC requires an inquest). So define, per district-year:

```
registration_propensity = (total recorded IPC/BNS cases) / (recorded murders)
```

benchmarked against the national relationship (and, better, against ADSI's unnatural-death and
road-fatality counts, which are collected through a different channel). A district far **below**
the expected ratio is **under-registering**, not safe. This is cheap, computable from data we
already plan to ingest, and it is the correction that makes the product honest.

### 6.3 Say it plainly

> **A map of reported crime is partly a map of police responsiveness, not of crime.**
> A district can be dark on our map because it is safe, or because its police do not write FIRs,
> or because its residents have concluded that reporting is pointless. Our data cannot, on its own,
> tell those three apart. **A low number is not a green light.**

### 6.4 How to communicate this without destroying the product

The failure mode to avoid is the disclaimer that nobody reads sitting next to a red polygon that
everybody believes. Eight concrete measures:

1. **Never publish a bare "safest / most dangerous" ranking.** Rankings are what generates the
   wrong headline and the defamation exposure. If we must rank, rank **within a state** and
   **within a comparable-district peer group** (similar urbanisation and population).
2. **Name the metric honestly in the UI.** The layer is **"Recorded crime"**, not "Crime". Every
   tooltip reads *"cases recorded by police"*, with a one-screen methodology link.
3. **Ship a data-confidence layer alongside the crime layer**, per district:
   (a) `registration_propensity` vs national expectation (§6.2);
   (b) **police strength per lakh** (BPR&D, *Data on Police Organisations*, annual, state-level);
   (c) **chargesheeting rate** and **conviction rate** (NCRB disposal tables);
   (d) share of FIRs registered electronically / share of Zero FIRs.
   **Districts with low propensity get a visible "likely under-recorded" chip.**
   **This is the single most important UX decision in the product**: it turns a low number from a
   green light into a warning.
4. **Show uncertainty, not points.** Ranges for every rate, and **grey out any cell below a
   minimum count** (e.g. <20 cases) so small-number volatility cannot paint a village red.
5. **Pair with victimisation data where it exists.** NFHS gives district-level estimates for
   spousal violence — for that one category we can show reported-vs-experienced side by side and
   **label the difference as "the reporting gap"**. Doing this for even one category teaches users
   to read the rest of the map correctly.
6. **Give people outcomes, like police.uk does.** India's analogue of "what happened to this crime"
   is the chargesheeting rate and the conviction rate (NCRB by crime head and state; NJDG/eCourts
   at case level). *"Of 100 burglaries recorded here, 43 were chargesheeted and 8 ended in
   conviction"* is more actionable, more interesting and far less defamatory than a heat colour.
7. **Never render finer than the data supports.** District-annual data gets a district polygon.
   No dots, no heat blobs, no street-level anything unless a specific force publishes point data.
8. **Answer the resident's actual question differently.** "Is this neighbourhood safe to walk
   through at night?" is not answerable from FIR counts. What *is* answerable and genuinely useful:
   nearest police station and its response infrastructure, street-lighting coverage, reported
   category mix, outcome rates, and how this district compares to its peer group. **Reframing the
   question is better product design and better ethics than pretending the counts answer it.**

---

## 7. Recommended canonical schema

Law-neutral, statute-agnostic, geography-versioned. Two fact tables and five dimensions.
**The design rule behind all of it: never key on a section number, never key on a name, never
aggregate across a level or a table boundary without an explicit flag saying it is safe.**

### 7.1 `crime_count_fact` — the workhorse (NCRB, state dashboards, RTI returns)

```sql
CREATE TABLE crime_count_fact (
  fact_id                TEXT PRIMARY KEY,
  source_id              TEXT NOT NULL,      -- FK -> source (the research .jsonl id)
  source_table_ref       TEXT,               -- 'CII-2022 Table 3A.1' ; aggregation boundary
  source_row_hash        TEXT,               -- reproducibility

  geo_key                TEXT NOT NULL,      -- FK -> geo_unit
  geo_level              geo_level_enum NOT NULL,
  geo_vintage            TEXT NOT NULL,      -- 'c2011' | 'lgd2026-04' | 'src-native'

  period_start           DATE NOT NULL,
  period_end             DATE NOT NULL,
  period_type            period_enum NOT NULL,

  crime_key              TEXT NOT NULL,      -- FK -> crime_head : OUR taxonomy, law-neutral
  statute_family         statute_enum NOT NULL,
  statute_sections       TEXT[],             -- as printed: ['302'] or ['103(1)']
  statute_jurisdiction   TEXT,               -- 'central' | 'state:TS' | 'n/a'

  measure                measure_enum NOT NULL,
  counting_unit          unit_enum NOT NULL,
  principal_offence_rule BOOLEAN NOT NULL,   -- TRUE for everything from NCRB
  rollup_safe            BOOLEAN NOT NULL,   -- may this row be summed with siblings?

  value                  NUMERIC NOT NULL,
  value_is_estimated     BOOLEAN DEFAULT FALSE,
  suppressed             BOOLEAN DEFAULT FALSE,

  denominator_population NUMERIC,
  denominator_version    TEXT,               -- FK -> denominator_version
  rate_per_100k          NUMERIC,
  rate_ci_low            NUMERIC,
  rate_ci_high           NUMERIC,

  geo_stability          stability_enum NOT NULL,
  series_break_flags     TEXT[],             -- ['bns_transition','cla_2013','commissionerate_2020']
  comparable_over_time   BOOLEAN NOT NULL,
  comparable_across_geo  BOOLEAN NOT NULL,
  confidence             SMALLINT,           -- 1-5

  ingested_at            TIMESTAMPTZ NOT NULL,
  UNIQUE (source_id, geo_key, geo_vintage, period_start, period_end,
          crime_key, measure, statute_family)
);
```

### 7.2 `crime_event` — incident level (Kerala/Delhi/Telangana FIR feeds, court records)

```sql
CREATE TABLE crime_event (
  event_id             TEXT PRIMARY KEY,
  source_id            TEXT NOT NULL,
  source_record_id     TEXT,                -- FIR number as published
  fir_number           TEXT,
  fir_date             DATE,
  is_zero_fir          BOOLEAN,             -- BNSS s.173 : filed outside jurisdiction

  police_station_key   TEXT,
  district_key         TEXT,
  geo_vintage          TEXT NOT NULL,

  occurrence_start_ts  TIMESTAMPTZ,
  occurrence_end_ts    TIMESTAMPTZ,         -- FIRs often give a window, not an instant
  report_ts            TIMESTAMPTZ,
  report_delay_days    INTEGER,             -- occurrence -> report ; a quality signal

  location_text        TEXT,
  geom                 GEOMETRY(POINT,4326),
  geocode_method       geocode_enum,        -- exact|street|ward_centroid|ps_centroid|district_centroid|none
  geocode_confidence   SMALLINT,
  publish_geom_precision precision_enum,    -- point|500m|1km|ps|district|withheld

  statute_family       statute_enum,
  statute_sections     TEXT[],              -- ALL sections on the FIR, not just the principal one
  crime_keys           TEXT[],              -- all mapped heads
  principal_crime_key  TEXT,                -- what NCRB would have counted -> lets us MEASURE the rule

  victim_count         INTEGER,
  accused_count        INTEGER,
  outcome              outcome_enum,        -- under_investigation|chargesheeted|closed_untraced|
                                            -- closed_false|closed_mistake_of_fact|convicted|acquitted|compounded
  outcome_date         DATE,
  is_redacted          BOOLEAN DEFAULT TRUE -- victim-identifying detail stripped before storage
);
```

`statute_sections` holding **all** sections while `principal_crime_key` holds the NCRB-equivalent
choice is what lets us compute the censoring rates in §2.2. **Do not discard non-principal
sections at ingest.**

### 7.3 Dimensions

```sql
crime_head (
  crime_key            TEXT PK,             -- 'property.burglary.house_breaking_night'
  l1_family            TEXT,                -- violence_against_person | sexual_offence |
                                            -- property_crime | public_order | economic_fraud |
                                            -- cyber | traffic_negligence | offence_against_state |
                                            -- special_local_law | other
  l2_group             TEXT,                -- homicide | attempted_homicide | assault | kidnapping |
                                            -- rape | other_sexual_offence | domestic_cruelty |
                                            -- theft | burglary | robbery_dacoity | snatching |
                                            -- vehicle_theft | cheating | extortion | rioting |
                                            -- arson | drugs | arms | prohibition | gambling | ...
  l3_head              TEXT,
  ipc_sections         TEXT[],
  bns_sections         TEXT[],
  sll_acts             TEXT[],
  is_apex_head         BOOLEAN,             -- never subordinate under the principal offence rule
  comparable_pre_2024  BOOLEAN,             -- FALSE for BNS 304/111/112/113/69/103(2)
  comparable_across_states BOOLEAN,         -- FALSE for every state-SLL head. Map layer OBEYS this
  min_publishable_count SMALLINT DEFAULT 20,
  public_label         TEXT,                -- plain-English, non-stigmatising
  public_definition    TEXT
);

ncrb_head_alias ( year INT, raw_label TEXT, source_table_ref TEXT, crime_key TEXT,
                  PRIMARY KEY (year, raw_label, source_table_ref) );
  -- an unmapped raw_label MUST FAIL THE BUILD, never be silently dropped

statute_xwalk ( from_statute TEXT, from_section TEXT, to_statute TEXT, to_section TEXT,
                relation TEXT,   -- exact|narrowed|widened|split|merged|new|repealed
                comparable BOOLEAN, source TEXT, confidence SMALLINT );
  -- this is §1.3 of this document, as data

geo_unit ( geo_key TEXT PK, geo_vintage TEXT, level geo_level_enum, name TEXT,
           name_aliases TEXT[], lgd_code TEXT, census2011_code TEXT, ncrb_label TEXT,
           state_key TEXT, parent_key TEXT, contained_in TEXT,
           valid_from DATE, valid_to DATE,
           boundary_source TEXT, geom GEOMETRY(MULTIPOLYGON,4326),
           geom_is_authoritative BOOLEAN );   -- FALSE for every police jurisdiction we approximate

geo_xwalk ( from_geo_key TEXT, from_vintage TEXT, to_geo_key TEXT, to_vintage TEXT,
            share NUMERIC,      -- apportionment weight, sums to 1 per (from_geo_key, to_vintage)
            basis TEXT,         -- population2011|area|village_list|gazette|manual
            source TEXT, confidence SMALLINT );

denominator_version ( denominator_version TEXT PK, method TEXT, base_census TEXT,
                      projection_source TEXT, shrinkage_lambda NUMERIC,
                      validated_against TEXT, created_at TIMESTAMPTZ, superseded_by TEXT );

population_panel ( geo_key TEXT, geo_vintage TEXT, year INT, denominator_version TEXT,
                   population NUMERIC, population_low NUMERIC, population_high NUMERIC,
                   urban_share NUMERIC, method_note TEXT,
                   PRIMARY KEY (geo_key, geo_vintage, year, denominator_version) );

source ( source_id TEXT PK, ... )  -- the research .jsonl catalogue, loaded verbatim
```

### 7.4 Controlled vocabularies

| Enum | Values |
|---|---|
| `geo_level` | `national`, `state`, `district`, `police_district`, `commissionerate`, `city`, `subdivision`, `circle`, `police_station`, `ward`, `beat`, `grid`, `point` |
| `period_type` | `year`, `quarter`, `month`, `week`, `day` |
| `statute_family` | `IPC`, `BNS`, `SLL-central`, `SLL-state`, `POCSO`, `NDPS`, `mixed`, `n/a` |
| `measure` | `cases_registered`, `cases_chargesheeted`, `cases_convicted`, `cases_pending_investigation`, `cases_closed_false`, `victims`, `persons_arrested`, `persons_convicted`, `rate_per_100k` |
| `counting_unit` | `fir`, `offence`, `victim`, `accused`, `case` |
| `geo_stability` | `stable`, `split_after`, `merged_after`, `renamed`, `reconstituted`, `jurisdiction_recut` |
| `geocode_method` | `exact`, `street`, `ward_centroid`, `ps_centroid`, `district_centroid`, `none` |
| `publish_geom_precision` | `point`, `500m`, `1km`, `ps`, `district`, `withheld` |
| `outcome` | `under_investigation`, `chargesheeted`, `closed_untraced`, `closed_false`, `closed_mistake_of_fact`, `convicted`, `acquitted`, `compounded` |
| `series_break_flags` | `pocso_2012`, `cla_2013`, `ncrb_city_panel_2014`, `cii_format_2016`, `attempt_rape_head_2017`, `jk_reorg_2019`, `dnhdd_merger_2020`, `bns_transition_2024`, `bnss_prelim_inquiry_2024`, `district_split`, `district_merge`, `commissionerate_created`, `rename` |

### 7.5 Six invariants the pipeline must enforce as assertions, not documentation

1. **No name joins.** Every join is on `lgd_code`, `census2011_code` or `geo_key`.
2. **No cross-`source_table_ref` aggregation** unless `rollup_safe = TRUE` on every row.
3. **No section-number joins.** Section → `crime_key` goes through `statute_xwalk`; an unmapped
   section fails the build.
4. **No unmapped NCRB label passes ingest.** `ncrb_head_alias` misses are build failures.
5. **No rate without a `denominator_version`**, and none rendered without its band.
6. **No time-axis chart on `geo_vintage != 'c2011'`**, and no choropleth for a `crime_key` with
   `comparable_across_states = FALSE`.
