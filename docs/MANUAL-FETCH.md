# What I need you to run

I cannot reach any `.gov.in` host from this environment, and that is an
organisation egress policy rather than something I can configure around. Two
ways past it, and the second is faster.

---

## Option A — one command, five minutes

On any machine in India with Python 3.9+ (a laptop is fine — no install, no
dependencies):

```bash
git clone https://github.com/Danish99011/Crime-map
cd Crime-map
git checkout claude/kind-ride-8yivdu
python3 scripts/fetch_live.py --probe
```

It visits four police portals, reads nothing but the search page, writes
`data/raw/live/probe-YYYY-MM-DD.json` and stops. It submits no form, downloads
no records and stops immediately at any CAPTCHA.

**Send me that one file** — paste it here or commit and push it.

### Why that file is the whole unlock

Every portal is an ASP.NET form. To request records you must post back the
form's own hidden state along with the right control names — `ddlDistrict`,
`ddlPoliceStation`, the date fields, the submit button. I know the *shape* from
third-party scrapers, but not the live names, and a scraper that posts guessed
parameters gets an empty table back. **An empty table looks exactly like an
absence of crime**, which is the single most dangerous failure this project
has. So I will not guess them.

With the probe output I can finish the fetcher properly and you run it once
more to pull five years of records.

---

## Option B — a fresh environment, and I do the rest

Create a Claude Code environment whose network policy allows these hosts, and
everything below happens without you:

```
*.gov.in
*.nic.in
web.archive.org
overpass-api.de
```

Docs: <https://code.claude.com/docs/en/claude-code-on-the-web>. The network
policy is chosen when the environment is created, so it needs a new one rather
than a change to this one. Start a session there against this repo and branch
and say "run the live fetch". I would then:

1. Probe and finish the fetchers (the part Option A needs you for).
2. Pull five years of Mumbai and Bengaluru station-level FIRs.
3. Re-verify the 858 catalogue URLs — 460 of them sit on blocked domains and
   are currently marked `CITED`, meaning found in a search index but never
   opened.
4. Fetch NCRB district tables for 2015-2024, which close the gap between the
   2001-2014 data in hand and your five-year requirement.

---

## If you would rather fetch by hand

In priority order. Each is a browser download, no scripting.

| # | What | Where | Why it matters |
|---|---|---|---|
| 1 | **Mumbai published FIRs** | `citizen.mahapolice.gov.in` → Published FIRs → district `MUMBAI CITY` / `MUMBAI SUBURBAN`, one month at a time | The best crime feed in India. Every FIR, daily, station-level, timestamped to the second. This alone makes Mumbai a real product. |
| 2 | **Bengaluru crime CSVs** | `data.opencity.in` → search "karnataka crime" | Already machine-readable, already licensed. District and commissionerate level, monthly review PDFs alongside. |
| 3 | **Delhi station list** | `delhipolice.gov.in` → police station directory | We have Delhi's 180 jurisdiction polygons but want the official station roster to check them against. |
| 4 | **NCRB Crime in India 2019-2024** | `ncrb.gov.in` → Crime in India → the district supplementary tables, not Volumes 1-3 | Closes the 2015-2024 gap. Note the district tables are a separate download from the main volumes — the volumes are state-level only. |

Save anything you get under `data/raw/` and tell me the filenames. Formats do
not matter — XLS, PDF, CSV, a saved HTML page all work.

---

## What I will not ask you to do

**Defeat a CAPTCHA.** Rajasthan's FIR search is CAPTCHA-gated, which puts
Bhilwara's crime data out of reach by this route. That is a decision, not an
obstacle; the route there is RTI, and the drafts are in
`research/sources/rti-playbook.md`.

**Collect names.** These listings publish complainant and accused names. The
fetcher drops those columns before anything reaches disk, and `FirRecord` has
no field that can hold them.
