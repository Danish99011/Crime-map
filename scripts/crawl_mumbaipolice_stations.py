#!/usr/bin/env python3
"""Fetch every Brihan Mumbai police station page from mumbaipolice.gov.in.

One request at a time, three seconds apart, retried on transient resets. This
is the commissionerate's own directory: each page carries the station's office
telephone numbers, email, division / zone / region, beat chowkies, nearest
railway station, the office address with its pincode, and a map embed with the
station's coordinates. Raw pages land in data/raw/mumbaipolice/stations/ so the
parser can be written and reviewed against saved files, and the site is asked
once rather than every time the parser changes.

Terms: see docs/TERMS-REVIEW.md. No robots.txt; the disclaimer permits linking
without permission, forbids framing, and warns that telephone numbers may have
changed since publication -- which the map must say too.
"""
from __future__ import annotations
import gzip, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "mumbaipolice" / "stations"
ROSTER = OUT.parent / "getpolicestations.json"
UA = ("Mozilla/5.0 (compatible; IndiaCrimeMap/0.1; public-interest safety research; "
      "contact via the project repository)")
BASE = "https://mumbaipolice.gov.in"
DELAY = 3.0

def get(url: str, tries: int = 5) -> tuple[int, bytes]:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                                       "Accept-Language": "en-IN,en;q=0.9"})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return r.status, body
        except urllib.error.HTTPError as e:
            return e.code, b""
        except Exception as e:
            last = e; time.sleep(2.0 * (attempt + 1))
    print(f"  giving up on {url}: {last}", flush=True)
    return 0, b""

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not ROSTER.exists():
        status, body = get(BASE + "/getpolicestations")
        if status != 200:
            print("roster fetch failed", status); return 1
        ROSTER.write_bytes(body); time.sleep(DELAY)
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    ids = [int(e["id"]) for e in roster]
    print(f"{len(ids)} stations in roster", flush=True)
    done = fail = 0
    for i, sid in enumerate(ids, 1):
        target = OUT / f"ps_{sid}.html"
        if target.exists() and target.stat().st_size > 20000:
            continue
        status, body = get(f"{BASE}/policestation?ps={sid}")
        if status == 200 and len(body) > 20000:
            target.write_bytes(body); done += 1
        else:
            fail += 1; print(f"  ps={sid}: HTTP {status} {len(body)}B", flush=True)
        if i % 10 == 0:
            print(f"  {i}/{len(ids)}  saved={done} failed={fail}", flush=True)
        time.sleep(DELAY)
    print(f"finished: saved={done} failed={fail} on disk={len(list(OUT.glob('ps_*.html')))}", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
