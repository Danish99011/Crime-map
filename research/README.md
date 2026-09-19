# India Crime Map — Phase 1: Source Discovery

Goal: a public portal that tells an ordinary person in India what crime looks like where they
live, walk, rent or buy — the way [police.uk](https://www.police.uk/) does for England & Wales.

Phase 1 answers one question before a line of product code is written:
**what data actually exists, at what geographic resolution, how often does it refresh, and
what is it legal and ethical to publish?**

## Layout

| path | what it is |
|---|---|
| `_SPEC.md` | the research contract every dossier follows |
| `sources/<domain>.md` | human-readable dossier per research domain |
| `sources/<domain>.jsonl` | machine-readable source entries, one JSON per line |
| `_raw/` | scratch, gitignored |

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
