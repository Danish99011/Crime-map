# Terms of use and robots.txt, per source

`docs/INGESTION.md` rule 2: a source is not switched on until someone has read
that portal's terms of use and robots.txt and written down what they found.
`terms_reviewed` is a flag a human sets after doing that, not a default.

This file is that record. Everything below was read from the live sites on
**2026-09-20**, which is the first session in this project's history able to
reach a `.gov.in` host at all. Re-read before relying on it: terms change, and
a stale review is worth about as much as no review.

A public-interest purpose is not a defence against a term that prohibits
automated access. Where a term prohibits it, the route is RTI.

---

## citizen.mahapolice.gov.in — Maharashtra Police CCTNS citizen portal

**Verdict: automated access is not prohibited, and reproduction is expressly
permitted with attribution. Ingestion may proceed.**

### robots.txt

| Host | Result |
|---|---|
| `citizen.mahapolice.gov.in/robots.txt` | **404** — no robots.txt exists, so nothing is disallowed |
| `mahapolice.gov.in/robots.txt` | 200 — `User-agent: *`, `Disallow:` (i.e. allow all), then `Disallow: /css/ /fonts/ /images/ /js/` |

The parent site's file disallows only static asset directories. No content path
is excluded, and `Disallow:` with an empty value explicitly permits everything.

### Terms, from `/Citizen/MH/Disclaimers.aspx`

Read in full. Four sections: Disclaimer, Hyperlink Policy, Privacy Policy,
Copyright Policy. The load-bearing passages, quoted:

> **Disclaimer.** "unauthorized attempts to defeat or circumvent security
> features, to use the system for other than intended purposes, to deny service
> to authorized users, to access, obtain, alter, damage, or destroy information,
> or otherwise to interfere with the system or its operation is prohibited."

> **Copyright Policy.** "Material featured on this portal should not be
> reproduced in a derogatory manner or in a misleading context. Where the
> material is being published or issued to others, the source must be
> prominently acknowledged."

### How this project reads that

| Term | What we do |
|---|---|
| No defeating or circumventing security features | There are none to circumvent. No login, no CAPTCHA, no rate-limit token. We post the site's own public search form with the site's own rendered values. |
| No use for other than intended purposes | The intended purpose of a page titled "Published FIRs" with a public date-and-unit search is that the public reads published FIRs. That is exactly and only what we do. |
| No denying service to authorized users | The binding constraint. One request at a time per host, three-second pause, no concurrency, no retry storm — `MIN_DELAY` in `scripts/mahapolice_client.py` is a floor, not a default. |
| No altering, damaging or destroying information | Read-only throughout. The fetcher issues no write of any kind. |
| Not reproduced in a derogatory manner or misleading context | This is a standing design obligation, not a one-off check. `docs/INGESTION.md` rule 5 and the station-not-scene caveat exist to satisfy it. Rendering FIR counts as a map of danger, or an absence of data as safety, would put us in breach of the licence as well as being wrong. |
| Source must be prominently acknowledged | Maharashtra Police must be named on the face of any view built from this feed, not in a footnote. |

**No clause prohibits automated access, bulk retrieval, or reuse.** There is no
separate terms-of-service page, no API agreement and no rate-limit policy.

### Personal data

None to drop. The published grid's ten columns are `Sr. No. | State | District
| Police Station | Year | FIR No. | Registration Date | FIR No | Sections |
Download`. There is no complainant, accused, address, age or phone column.
`pipeline/mahapolice.py` still returns only the columns named in `COLUMNS`, so a
portal that starts publishing an identifier drops it at the boundary.

### Limits the portal states about itself

Quoted from its own validation message, and not documented anywhere a caller
would otherwise find them:

> "From Date should be greater than 1/01/2017 and date difference between From
> and To Date should be less than 90 days."

So the published series begins **2017-01-01** — there is no route to 2015 or
2016 here — and **no single query may span more than 90 days**. A query
breaching either returns "No Records Found", which is why
`pipeline/mahapolice.py` distinguishes a stated zero from a failed fetch.

---

## ncrb.gov.in and data.gov.in

Reachable (HTTP 307 and 302 respectively). NCRB publications are Government of
India works released for public use; data.gov.in resources carry the
**Government Open Data License – India (GODL)**, which permits reuse with
attribution. Not yet harvested in this session, so not yet reviewed in the
detail Maharashtra was.

## ksp.karnataka.gov.in and delhipolice.gov.in

Not reviewed, because not reachable — see `docs/LIVE-FETCH-2026-09-20.md`.
Reviewing terms for a site we cannot open would be inventing a record.

## police.rajasthan.gov.in

**Out of scope by rule 1, independent of its terms.** The FIR search is
CAPTCHA-gated. That is a closed door, not an obstacle to engineer around, and
Bhilwara's route is RTI — see `research/sources/rti-playbook.md`.
