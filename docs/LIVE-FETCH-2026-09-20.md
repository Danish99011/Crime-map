# The first session that could reach a .gov.in host

_2026-09-20_

Every earlier session in this project ran behind an egress policy that returned
403 for `*.gov.in` and `*.nic.in`. `docs/MANUAL-FETCH.md` was written to ask a
human to run the fetch instead. The allowlist has since been changed, and this
is the record of what turned out to be true once the hosts could actually be
opened.

Short version: **Maharashtra works and is now being harvested. The two national
portals forbid it. Delhi has a search but not a listing. Karnataka is
unreachable.** Three of those four are conclusions about the sources, not about
the network, so they do not change if someone re-runs this from India.

---

## 1. Reachability, and what "unreachable" was hiding

`scripts/fetch_live.py --probe` reported all four targets unreachable. That was
the probe being too blunt: three different causes were collapsed into one word.

| Host | Result | What it actually was |
|---|---|---|
| `citizen.mahapolice.gov.in` | **200, ~4 of 5 attempts** | Transient relay resets. Retries fix it. |
| `ncrb.gov.in` | 200 | Reachable, but see §3. |
| `data.gov.in` | 200 | Reachable, but see §3. |
| `delhipolice.gov.in` | **200 without `www.`** | `www.delhipolice.gov.in` serves an expired certificate; the apex host does not. |
| `ksp.karnataka.gov.in` | 0 of 5 | Genuinely unreachable; connection reset at the origin. |
| `police.rajasthan.gov.in` | 2 of 5 | Reachable, and irrelevant: CAPTCHA-gated, out of scope by rule 1. |

None of the failures was a policy denial — there was no 403 from the proxy in
any of them. The probe now needs retries before it reports a host down, because
"unreachable" and "answered, then the tunnel dropped" are not the same claim.

The Delhi case is worth keeping in mind generally: a `www.` host and its apex
can have different certificates, and testing only one of them is how a working
source gets written off. TLS verification was never disabled to get past it.

## 2. Maharashtra: what the live form actually contains

`docs/MANUAL-FETCH.md` said the form controls could not be guessed and must be
read off the live page. That was right, and four of them would have been
guessed wrong:

* **The unit dropdown is empty until a session exists.** Requesting
  `PublishedFIRs.aspx` cold returns it with a single "Select" option. Visiting
  `index.aspx` first is what makes the server populate it. A scraper that skips
  the warm-up sees no districts and concludes the portal is broken.
* **Mumbai is one unit, not two.** `pipeline/cities.py` assumed `MUMBAI CITY`
  and `MUMBAI SUBURBAN`. The portal is organised by commissionerate:
  **BRIHAN MUMBAI CITY, unit 19378, 98 police stations**, covering both revenue
  districts. `NAVI MUMBAI` and `RAILWAY MUMBAI` are separate commissionerates.
* **The station dropdown's placeholder changes value between requests** — the
  literal `Select` on the blank form, empty once a unit is chosen. Posting the
  wrong one fails EventValidation and returns a generic error page.
* **Page size is capped at 50.** 100 and 500 are rejected.

And two limits the portal states only in a validation message, nowhere a caller
would look:

> "From Date should be greater than 1/01/2017 and date difference between From
> and To Date should be less than 90 days."

So **the published series begins 2017-01-01** — there is no route to 2015 or
2016 here — and **no query may span more than 90 days**.

### The bug the fixtures caught

The results grid's pager is a `<tr class="gridPager">` wrapping a nested table
of page links. A parser that counts cells reads it as a 51st FIR whose district
is the literal `3` and whose police station is `4`. Every 50-row page parsed as
51 records. `tests/fixtures/mahapolice-publishedfirs-brihanmumbai-2026-08-with-pager.html`
exists to keep that fixed.

The parser now raises `SchemaChanged` rather than returning `[]` for anything it
does not recognise, and returns empty only when the portal explicitly says
"No Records Found". An empty grid and an absence of crime are indistinguishable
downstream, so they must be distinguished here.

### Devanagari section numbers

The first live month came back **97% unclassified**. `pipeline/taxonomy.py`
carried a comment asserting that Devanagari digits "appear in Marathi act years
and are never section numbers". True of the 2025 BNS fixtures it was written
against; false of every pre-BNS record, which the portal writes as

    भारतीय दंड संहिता १८६० - ३८० ;      (IPC 1860 s.380, theft)

where ३८० is the section. Transliterating rather than deleting the digits takes
January 2021 from 97% unclassified to 41%, and the remainder is almost exactly
that month's special and local laws — 701 SLL acts against 711 unclassified —
which have no IPC crime head by design.

## 3. NCRB and data.gov.in forbid automated access

Both national portals publish the same robots.txt:

```
User-agent: *
Disallow: /
```

`ncrb.gov.in` and `data.gov.in` disallow crawling of their entire sites. Under
`docs/INGESTION.md` rule 2 that closes the automated route to the NCRB district
tables, and a public-interest purpose is not a defence against it.

This is a real loss: those tables are what would close the 2015-2024 district
gap. Two routes remain, and both need a person rather than a scraper:

1. **Download them by hand.** robots.txt governs crawlers, not a person
   clicking a link.
2. **Use the data.gov.in API with a registered key**, which is an invited,
   documented channel rather than crawling. That needs the user's own key; this
   session did not create one.

## 4. Delhi has an FIR search, but it is a lookup, not a listing

`docs/PHASE1-FINDINGS.md` recorded Delhi as "e-FIR only; no bulk published-FIR
listing found". That is half right, and the correction matters because Delhi is
the best-mapped city in India for this purpose.

`delhipolice.gov.in/viewfir.aspx` links to
`cctns.delhipolice.gov.in/citizen/firSearch.htm`, which is a **general** FIR
search covering everything from 01-07-2015 — not just e-FIR. No CAPTCHA, no
robots.txt, 24 districts, years 2015-2026, a date range, and a clean JSON
endpoint for the police stations of a district.

It still cannot produce a station-month series, because of this in its own
client-side validation:

```js
if (firNo == "") { if (searchName1 == "") { fancyAlert(...); return false; } }
```

**A search must carry either an FIR number or a person's name.** A date range
alone is refused. So enumerating a station's FIRs would mean either iterating
FIR numbers — thousands of requests against a lookup form, which is not what
that form is for — or searching by name, which this project will not do.

Delhi therefore stays geography-rich and data-poor. Worth revisiting only if a
bulk route appears; the RTI route in `research/sources/rti-playbook.md` is the
honest one meanwhile.

## 5. Karnataka

`ksp.karnataka.gov.in` and `karnataka.gov.in` both reset the connection on every
attempt, from a network that reaches other `.gov.in` hosts in the same minute.
Nothing about the source was established, so nothing is claimed about it. The
OpenCity Karnataka CSVs remain the better first target there in any case.

## 6. Gurugram and Noida: confirmed from the live sites

Both states' portals answer, and neither publishes a bulk FIR listing.

| Host | Result |
|---|---|
| `www.haryanapolice.gov.in` | 200 (the apex `haryanapolice.gov.in` does not answer) |
| `uppolice.gov.in` | 200 |
| robots.txt on both | 404 — none published, so nothing disallowed |

Both run the same CCTNS citizen-portal template, and on both the landing page
offers the same five citizen links. The one that matters, **"FIR Download",
points at `Citizen_login.aspx` on each.** It is login-gated: a citizen retrieves
*their own* FIR, which is a different product from Maharashtra's published list
of every FIR registered. There is no date-and-station search to drive.

So the earlier conclusion holds, and now on evidence rather than on absence of
evidence: **Gurugram and Noida stay RTI targets.** Neither state publishes
station boundaries either, so even with a feed they would map as points only.

`research/sources/rti-playbook.md` has the drafts.

---

## What it costs to harvest Mumbai

Measured, not estimated. Page size is capped at 50 and the GridView only accepts
a page near the one it currently renders, so pages must be walked in order.

* A recent month is about 8,000 FIRs — roughly 160 sequential pages.
* The portal takes **~20-26 seconds to serve a paging postback**, which is the
  binding constraint and nothing to do with our delay between requests.
* That is roughly **an hour per recent month**, and on the order of **45 hours**
  for 2017-2026.

The first attempt was far worse — about three minutes a page — because the
client backed off escalatingly on connection resets, and this link drops about
one request in five. A reset means the server never finished serving the
request, so retrying promptly adds nothing to its load; the politeness that
matters is the gap between *served* requests. Fixing that took it from ~3 min to
~25 s a page.

So a full five-year Mumbai harvest is a multi-day background job at a
respectful rate, not something a session finishes. `scripts/harvest_mumbai.py`
is built for that: newest month first, rows flushed to disk as they arrive, and
a month marked complete only when its row count matches the count the portal
itself declares.

```bash
python3 scripts/harvest_mumbai.py --from 2021-01 --to 2026-09   # resumes
```

Do not raise the concurrency. These are public-sector servers that citizens
depend on, and degrading one does more harm than the map does good.

---

## 7. Locating a pincode: what was tried on 2026-09-21, and why the answer is "the police's own addresses"

The product wants a person to type their pincode and see their locality. No
Indian authority publishes pincode polygons, so a centre point per pincode was
the fallback sought. Every candidate failed, each for a different reason, and
the reasons matter more than the list:

| Source | Result | Why it is out |
|---|---|---|
| GeoNames IN postal file (via the sanand0/pincode mirror, CC-BY) | reachable | **Measured unusable**: of 89 Mumbai pincodes, 82 share the single point (19.0167, 72.85). Zooming to it would put most of the city on Fort. |
| `download.geonames.org` | policy-blocked | same data anyway |
| Overpass, Nominatim, openstreetmap.org | policy-blocked | OSM `addr:postcode` would have been the best free source |
| Wikidata (P281 postal code, P625 coordinates, CC0) | policy-blocked | |
| Wikipedia API (`/w/api.php`) | 429, and robots.txt `User-agent: *` disallows `/w/` and `/api/` | closed under INGESTION rule 2, independent of the rate limit |
| India Post directory on data.gov.in | robots-disallowed | see §3 |
| ramSeraph `postal` release (pincode boundaries) | release page and API unreadable through the proxy; asset names not guessable | worth one try from an unblocked network |

What works, and is better than all of the above for this purpose: **Brihan
Mumbai Police publish each station's own address with its pincode**, on the
station's page at `mumbaipolice.gov.in/policestation?ps=<id>`, together with
office telephone numbers, email, beat chowkies (some listing the localities
each covers), the nearest railway station, and a map embed carrying the
station's coordinates. That makes "pincode → the stations that sit in it" a
statement from the police rather than an inference from a third party.

The honest limit follows directly: a pincode that no station lists as its
address has no location on this map, and the page says so instead of guessing.
