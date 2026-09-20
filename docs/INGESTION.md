# Ingestion rules

These are settled. They are referenced from `pipeline/sources.py`, which refuses
to run until they have been acknowledged, and they are not to be coded around.

## 1. We do not defeat CAPTCHAs

If a portal puts a CAPTCHA in front of its data, that is the end of the
automated route. `BiharScrbSource.probe()` detects one and stops.

This costs us real data — Rajasthan's FIR search is captcha-gated and would
otherwise be one of the better feeds in India. That is the intended trade. The
alternative route is RTI, and the drafts are written: see
`research/sources/rti-playbook.md`.

## 2. We do not ingest a source whose terms forbid it

Before a new source is switched on, someone reads that portal's terms of use and
robots.txt and records what they found. `terms_reviewed` is a flag a human sets
after doing that, not a default.

A public-interest purpose is not a defence against a term that prohibits
automated access. If the terms forbid it, the route is RTI or a data-sharing
request, not a faster scraper.

## 3. Identifiers are dropped at the boundary, not later

Bihar's FIR listing publishes the names and addresses of complainants and
accused. `FirRecord` has no field that can hold a name, an address, a phone
number or an age, and `from_row` copies only the columns named in an explicit
mapping.

Run `CsvFirSource.audit()` before ingesting any new file. It reports which of the
source's columns look like personal data. Finding names there is expected — the
listing genuinely publishes them. Carrying them downstream is what would be
wrong.

## 4. We are polite to public-sector servers

One request at a time per host, with a delay between them. These are frail
systems serving a public that needs them. A scraper that degrades a police
portal for ordinary citizens has done more harm than the map does good.

Phase 1 is reconnaissance: fetch to verify, not to harvest.

## 5. Absence is reported, never rendered as zero

Two categories are missing from every public Indian FIR feed, by law rather than
by accident:

- **Sexual offences and POCSO** — excluded under a Supreme Court direction of
  7 September 2016.
- **National security, law and order, and communal FIRs** — additionally
  withheld by Bihar's repository.

These are declared in `pipeline/taxonomy.py` with the reason attached, and the
map renders them as *withheld*. A blank where a rape statistic should be is a
statement about the law, not about the neighbourhood.

---

## Finishing the Bihar adapter

`BiharScrbSource` targets `scrb.bihar.gov.in/View_FIR.aspx`. Its form controls
are unknown because the host is unreachable from the environment the adapter was
written in, so it refuses to run rather than posting invented parameters and
reporting an empty result as "no crime".

From a network that can reach the host:

```python
from pipeline.sources import BiharScrbSource
print(BiharScrbSource().probe())
```

`probe()` is read-only. It reports the page's hidden ASP.NET state keys, its
visible controls, its dropdowns and whether a CAPTCHA is present. Then:

1. If `captcha_detected` is true, stop and go the RTI route.
2. Otherwise map the real control names into `BiharScrbSource.controls`.
3. Save one result page into `tests/fixtures/` and write the row parser against
   it, test first. Do not write the parser against a page you have not saved:
   the fixture is what makes the parser reviewable by someone who cannot reach
   the site either.
4. Set `terms_reviewed=True` only after rule 2 above has actually been done.

Until then, `CsvFirSource` is the working route. It takes any FIR extract — an
RTI response, a portal export, a manual download — with a column mapping.

## A note on what this pipeline can and cannot tell you

It maps **FIRs registered by a police station**. It does not map where crimes
happened, and it cannot. A station that registers complaints readily will look
worse than one that turns people away, and that error runs one way.

Every aggregate carries this as a structured caveat rather than a footnote, and
the map states it above the fold. If a future change makes that caveat easier to
drop, that change is wrong.
