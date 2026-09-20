#!/usr/bin/env python3
"""Fetch live crime data from Indian police portals. RUN THIS FROM INDIA.

The development sandbox cannot reach any `.gov.in` host, so this script exists
to be run somewhere that can — an ordinary laptop on an ordinary connection.
It needs only Python 3.9+ and the standard library.

    python3 scripts/fetch_live.py --probe                 # look, fetch nothing
    python3 scripts/fetch_live.py --city mumbai --months 60

**Start with --probe.** It reports whether each host answers, what the search
form actually contains, and whether a CAPTCHA is present. It writes no data and
submits no form. Read its output before fetching anything.

Three rules are enforced here, not left to the operator:

* **It stops at a CAPTCHA.** If one is present the target is skipped with a
  note. We do not defeat CAPTCHAs; the route for those sources is RTI.
* **It is slow on purpose.** One request at a time per host with a pause
  between them. These are public-sector servers that citizens depend on.
* **It keeps no names.** Published FIR listings carry complainant and accused
  names. Those columns are dropped at write time, before anything touches disk.

Everything lands in data/raw/live/ as dated JSON, which the rest of the
pipeline reads. Commit what you collect, or send it over — either works.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "live"

UA = ("Mozilla/5.0 (compatible; IndiaCrimeMap/0.1; public-interest safety research; "
      "contact via the project repository)")

# Columns that must never reach disk, matched against the header text a portal
# gives its result table. The published listings really do carry these.
PERSONAL = re.compile(r"name|accused|complain|address|mobile|phone|father|age", re.I)

TARGETS = {
    "mumbai": {
        "label": "Maharashtra Police — Published FIRs (covers Mumbai)",
        "url": "https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx",
        "districts": ["MUMBAI CITY", "MUMBAI SUBURBAN", "BRIHAN MUMBAI"],
        "note": "Verified column set: district, police station, year, FIR no, "
                "registration date+time, sections. No disposal field.",
    },
    "bangalore": {
        "label": "Karnataka State Police — FIR search",
        "url": "https://ksp.karnataka.gov.in/page/FIR+Search/en",
        "districts": ["BENGALURU CITY"],
        "note": "Reported daily, station-level. Form controls unconfirmed.",
    },
    "delhi": {
        "label": "Delhi Police — citizen services",
        "url": "https://www.delhipolice.gov.in/",
        "districts": [],
        "note": "No bulk published-FIR listing found. Probe looks for one.",
    },
    "bhilwara": {
        "label": "Rajasthan Police — FIR search",
        "url": "https://police.rajasthan.gov.in/",
        "districts": ["BHILWARA"],
        "note": "Expected to be CAPTCHA-gated. Probe will confirm and stop.",
    },
}

CAPTCHA = re.compile(r"captcha|securimage|recaptcha|hcaptcha", re.I)
HIDDEN = re.compile(r'<input[^>]+type=["\']hidden["\'][^>]*>', re.I)
SELECT = re.compile(r'<select[^>]+name=["\']([^"\']+)["\']', re.I)
INPUT_NAME = re.compile(r'<input[^>]+name=["\']([^"\']+)["\'][^>]*>', re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
ATTR = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"')


def fetch(url: str, data: bytes | None = None, timeout: float = 45.0) -> tuple[int, str]:
    request = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                 "Accept-Language": "en-IN,en;q=0.9", "Accept-Encoding": "gzip"})
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            body = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                try:
                    body = gzip.decompress(body)
                except (OSError, EOFError):
                    pass
            return response.status, body.decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception as exc:                      # DNS, TLS, timeout
        return 0, f"{type(exc).__name__}: {exc}"


def probe_one(key: str, target: dict) -> dict:
    status, body = fetch(target["url"])
    report = {"city": key, "label": target["label"], "url": target["url"],
              "status": status, "note": target["note"]}
    if status != 200:
        report["result"] = "unreachable" if status == 0 else f"HTTP {status}"
        report["detail"] = body[:160]
        return report

    title = TITLE.search(body)
    report["title"] = html.unescape(re.sub(r"\s+", " ", title.group(1)).strip())[:120] if title else ""
    report["captcha"] = bool(CAPTCHA.search(body))
    hidden = {}
    for tag in HIDDEN.findall(body):
        attrs = dict(ATTR.findall(tag))
        if attrs.get("name"):
            hidden[attrs["name"]] = len(attrs.get("value", ""))
    report["hidden_state"] = sorted(hidden)
    report["dropdowns"] = sorted(set(SELECT.findall(body)))
    report["inputs"] = sorted(set(INPUT_NAME.findall(body)))[:25]
    report["result"] = ("CAPTCHA present — skip, use RTI instead"
                        if report["captcha"] else "reachable, no CAPTCHA detected")
    return report


def strip_personal(row: dict) -> dict:
    return {k: v for k, v in row.items() if not PERSONAL.search(k or "")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--probe", action="store_true",
                        help="report what each portal exposes; fetch no data")
    parser.add_argument("--city", choices=sorted(TARGETS),
                        help="which city to fetch")
    parser.add_argument("--months", type=int, default=60,
                        help="how many months back to request (default 60, i.e. 5 years)")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="seconds between requests to the same host")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    if args.probe or not args.city:
        reports = []
        for key, target in TARGETS.items():
            print(f"\n=== {target['label']}")
            print(f"    {target['url']}")
            report = probe_one(key, target)
            reports.append(report)
            print(f"    -> {report['result']}")
            if report.get("title"):
                print(f"       title      : {report['title']}")
            if report.get("hidden_state"):
                print(f"       form state : {', '.join(report['hidden_state'][:6])}")
            if report.get("dropdowns"):
                print(f"       dropdowns  : {', '.join(report['dropdowns'][:8])}")
            time.sleep(args.delay)

        path = OUT / f"probe-{dt.date.today():%Y-%m-%d}.json"
        path.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {path.relative_to(ROOT)}")
        print("\nSend this file back, or commit it. It is the missing piece: with the real")
        print("form controls in hand the fetcher can be finished without guessing.")
        return 0

    print("Fetching is not implemented until a probe has confirmed the form controls.")
    print("Run --probe first and share the result; guessing the parameters would")
    print("produce an empty table that looks like an absence of crime.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
