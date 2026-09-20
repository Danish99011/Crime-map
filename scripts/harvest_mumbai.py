#!/usr/bin/env python3
"""Collect Mumbai's published FIRs, month by month, resumably.

    python3 scripts/harvest_mumbai.py --from 2021-01 --to 2026-09
    python3 scripts/harvest_mumbai.py --resume          # continue where it stopped

Writes one JSON Lines file per month under `data/raw/live/mumbai/`, plus a
checkpoint so an interrupted run continues rather than restarting. Stopping it
is safe at any point: a month is only marked complete once its own row count
matches the count the portal declared.

Why month by month, newest first
--------------------------------
The portal caps a query at 90 days and a page at 50 rows, and its GridView
only accepts a page near the one currently rendered, so pages must be walked
in order. A recent Mumbai month is around 8,000 FIRs, or 160 sequential pages;
an older one is nearer 1,700. At a polite three seconds a request that is
roughly eleven minutes for a recent month, and the whole 2017-2026 series is a
job of hours, not minutes. That is the cost of being a good citizen of someone
else's server, and it is not negotiable downward.

Newest first because a safety map is most wrong when it is stale, so partial
coverage should be recent coverage.

What is counted as done
-----------------------
A month is complete only when the rows collected equal `total records found`
on the portal's own page. Short of that the month is written but left
incomplete, with the shortfall recorded. Under-collection must never be
silently frozen into the data as a quiet month -- that is the same error as
rendering an absence as zero, arrived at from a different direction.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from mahapolice_client import MahapoliceClient, PortalError   # noqa: E402
from pipeline.mahapolice import (                             # noqa: E402
    SchemaChanged, parse_grid, portal_message, total_records,
)

OUT = ROOT / "data" / "raw" / "live" / "mumbai"
CHECKPOINT = OUT / "_checkpoint.json"

UNIT_NAME = "BRIHAN MUMBAI CITY"
PAGE_SIZE = 50

# The portal serves nothing before this date and says so only in a validation
# message. Asking for earlier silently returns "No Records Found".
SERIES_STARTS = dt.date(2017, 1, 1)

# Columns we keep. The published grid carries no identifier column, but the
# whitelist is what makes that a guarantee rather than an observation.
KEEP = ("state", "district", "police_station", "year", "fir_number",
        "registration_date", "fir_no_with_year", "sections")


def months(start: str, end: str):
    year, month = (int(x) for x in start.split("-"))
    last_year, last_month = (int(x) for x in end.split("-"))
    out = []
    while (year, month) <= (last_year, last_month):
        out.append((year, month))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return out


def load_checkpoint() -> dict:
    if CHECKPOINT.exists():
        return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    return {"months": {}}


def save_checkpoint(state: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(state, indent=1, sort_keys=True),
                          encoding="utf-8")


def harvest_month(client: MahapoliceClient, unit_id: str, year: int, month: int,
                  state: dict) -> dict:
    key = f"{year:04d}-{month:02d}"
    last_day = calendar.monthrange(year, month)[1]
    date_from = f"01/{month:02d}/{year}"
    date_to = f"{last_day}/{month:02d}/{year}"

    page = client.search(unit_id, date_from, date_to, page_size=PAGE_SIZE)
    declared = total_records(page)
    message = portal_message(page)

    rows = parse_grid(page)
    seen = {(r["police_station"], r["fir_no_with_year"]) for r in rows}
    collected = list(rows)

    if declared:
        pages = (declared + PAGE_SIZE - 1) // PAGE_SIZE
        for number in range(2, pages + 1):
            try:
                page = client.goto_grid_page(number, unit_id, date_from,
                                             date_to, PAGE_SIZE)
                batch = parse_grid(page)
            except (PortalError, SchemaChanged) as exc:
                print(f"    page {number}: {type(exc).__name__}: "
                      f"{str(exc)[:70]}", flush=True)
                break
            if not batch:
                break
            fresh = [r for r in batch
                     if (r["police_station"], r["fir_no_with_year"]) not in seen]
            if not fresh:
                # The grid handed back a page we already hold. Stopping is
                # right: continuing would spin, and the fixture in tests/
                # exists because another scraper did exactly that 50 times.
                print(f"    page {number}: repeated rows, stopping", flush=True)
                break
            seen.update((r["police_station"], r["fir_no_with_year"]) for r in fresh)
            collected.extend(fresh)
            if number % 20 == 0:
                print(f"    page {number}/{pages}  {len(collected)} rows",
                      flush=True)

    path = OUT / f"{key}.jsonl"
    OUT.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in collected:
            handle.write(json.dumps({k: row.get(k, "") for k in KEEP},
                                    ensure_ascii=False) + "\n")

    complete = declared is not None and len(collected) == declared
    record = {
        "collected": len(collected),
        "declared": declared,
        "complete": complete,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    if message:
        record["portal_message"] = message[:120]
    if declared is not None and len(collected) != declared:
        record["shortfall"] = declared - len(collected)
    state["months"][key] = record
    save_checkpoint(state)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    today = dt.date.today()
    parser.add_argument("--from", dest="start", default="2021-01")
    parser.add_argument("--to", dest="end", default=f"{today:%Y-%m}")
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--redo", action="store_true",
                        help="re-fetch months already marked complete")
    args = parser.parse_args()

    state = load_checkpoint()
    wanted = months(args.start, args.end)
    wanted = [(y, m) for y, m in wanted
              if dt.date(y, m, 1) >= SERIES_STARTS.replace(day=1)]
    wanted.sort(reverse=True)            # newest first

    client = MahapoliceClient(delay=args.delay)
    units = client.open_form()
    unit = next((u for u in units if u[1] == UNIT_NAME), None)
    if unit is None:
        print(f"{UNIT_NAME!r} is not in the portal's unit list. Found: "
              f"{[t for _, t in units][:6]}...")
        return 2
    client.select_unit(unit[0])
    print(f"unit {unit[1]} ({unit[0]}); {len(wanted)} months to consider\n")

    for year, month in wanted:
        key = f"{year:04d}-{month:02d}"
        done = state["months"].get(key)
        if done and done.get("complete") and not args.redo:
            continue
        print(f"{key} ...", flush=True)
        try:
            record = harvest_month(client, unit[0], year, month, state)
        except (PortalError, SchemaChanged) as exc:
            print(f"  FAILED {type(exc).__name__}: {str(exc)[:110]}", flush=True)
            state["months"][key] = {
                "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                "complete": False,
                "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            }
            save_checkpoint(state)
            # A failed month usually means the session died. Rebuild it.
            try:
                client = MahapoliceClient(delay=args.delay)
                client.open_form()
                client.select_unit(unit[0])
            except PortalError as rebuild:
                print(f"  cannot re-establish a session: {rebuild}")
                return 1
            continue
        flag = "ok" if record["complete"] else f"INCOMPLETE {record}"
        print(f"  {record['collected']} rows of {record['declared']}  {flag}",
              flush=True)

    complete = sum(1 for v in state["months"].values() if v.get("complete"))
    total = sum(v.get("collected", 0) for v in state["months"].values())
    print(f"\n{complete} months complete, {total} records on disk")
    print(f"requests made this run: {client.requests_made}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
