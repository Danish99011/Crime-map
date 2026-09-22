#!/usr/bin/env python3
"""Collect Mumbai's published FIRs, month by month, resumably.

    python3 scripts/harvest_mumbai.py --from 2021-01 --to 2026-09
    python3 scripts/harvest_mumbai.py --resume          # continue where it stopped
    touch data/raw/live/mumbai/_stop                    # exit cleanly at the next chunk

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
A month is walked in date chunks, a week each by default, because the grid
only accepts a page near the one on screen: a whole month was one walk of
some 170 pages, and the portal dropped two in a row at pages 116 and 54. A
chunk is complete only when one walk of its pages served every record the
portal declared for that range, and the month only when every chunk is and
the chunks' counts add up to the portal's own figure for the whole month
(the date filter is inclusive at both ends; the weekly counts for June 2026
summed to its 8,640 exactly). Short of that the month is written but left
incomplete, with the shortfall recorded. A restart keeps the rows an earlier
walk left on disk and walks again only the chunks that were not whole.
Under-collection must never be silently frozen into the data as a quiet
month -- that is the same error as rendering an absence as zero, arrived at
from a different direction.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from mahapolice_client import MahapoliceClient, PortalError   # noqa: E402
from pipeline.mahapolice import (                             # noqa: E402
    SchemaChanged, parse_grid, portal_message, total_records,
)

OUT = ROOT / "data" / "raw" / "live" / "mumbai"
CHECKPOINT = OUT / "_checkpoint.json"
DEBUG = OUT / "_debug"          # pages the walk could not read, for diagnosis
STOP = OUT / "_stop"            # touch it and the run exits at the next chunk boundary


class StopRequested(Exception):
    """The `_stop` file exists: finish the current chunk, checkpoint, exit."""

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


def _held(path: Path) -> set[tuple[str, str]]:
    """Keys of the rows an earlier run left in this month's file.

    A run killed mid-write can leave a torn last line; it is dropped and the
    file rewritten without it, so the aggregator never meets half a record.
    """
    if not path.exists():
        return set()
    keys, good = set(), []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        keys.add((row["police_station"], row["fir_no_with_year"]))
        good.append(line)
    path.write_text("".join(l + "\n" for l in good), encoding="utf-8")
    return keys


CHUNK_DAYS = 7


def chunks(year: int, month: int, days: int = CHUNK_DAYS) -> list[tuple[str, str, str]]:
    """Cut a month into inclusive date ranges of `days`, as (from, to, label).

    The portal's date filter includes both ends, and a tail shorter than
    half a chunk is folded into the chunk before it rather than walked alone.
    """
    last = calendar.monthrange(year, month)[1]
    out, start = [], 1
    while start <= last:
        end = min(start + days - 1, last)
        if last - end <= days // 2:
            end = last
        out.append((f"{start:02d}/{month:02d}/{year}", f"{end:02d}/{month:02d}/{year}",
                    f"{start:02d}-{end:02d}"))
        start = end + 1
    return out


def _open(client: MahapoliceClient, unit_id: str, date_from: str, date_to: str):
    """A clean form, the range searched, and (page, declared, message).

    A total the portal states as exactly one page while handing back a full
    page is not believed at first sight: the whole-month query for June 2026
    once said 50 for a month whose weeks then walked 8,640. Taken at its
    word, such a figure would mark a range complete after one page, which
    is the silent under-collection this whole script exists to refuse. The
    page is kept for diagnosis and the range is asked for once more; the
    larger of the two answers is used.
    """
    client.reset(unit_id)
    page = client.search(unit_id, date_from, date_to, page_size=PAGE_SIZE)
    declared = total_records(page)
    try:
        rows = parse_grid(page)
    except SchemaChanged:
        # Not a search result at all. Keep it: on 2026-09-22 the portal
        # answered every whole-month query this way for 25 minutes.
        DEBUG.mkdir(parents=True, exist_ok=True)
        (DEBUG / f"{date_from[6:]}-{date_from[3:5]}-{date_from[:2]}_nogrid.html"
         ).write_text(str(page), encoding="utf-8")
        raise
    if declared is not None and declared <= PAGE_SIZE and len(rows) == PAGE_SIZE:
        print(f"      portal says {declared} records with a full page; asking again "
              f"(page kept under {DEBUG.name}/)", flush=True)
        DEBUG.mkdir(parents=True, exist_ok=True)
        (DEBUG / f"{date_from[6:]}-{date_from[3:5]}-{date_from[:2]}_total{declared}.html"
         ).write_text(str(page), encoding="utf-8")
        client.reset(unit_id)
        again = client.search(unit_id, date_from, date_to, page_size=PAGE_SIZE)
        if (total_records(again) or 0) > declared:
            page, declared = again, total_records(again)
    return page, declared, portal_message(page)


def _walk(client: MahapoliceClient, unit_id: str, date_from: str, date_to: str,
          keep) -> dict:
    """Walk every page of one date range, handing new rows to `keep`.

    Returns the range's own accounting: what the portal declared, how many
    rows this walk served on pages that advanced, and whether the two meet.
    """
    # Start from a clean form, not from what the last walk left behind. Re-
    # posting only the unit selection was not enough: see MahapoliceClient
    # .reset, which documents the three-month failure cycle that cost
    # roughly half of a 23-month run.
    page, declared, message = _open(client, unit_id, date_from, date_to)

    seen: set[tuple[str, str]] = set()   # rows this walk has served
    accounted = 0                        # rows that count towards `declared`
    duplicates = 0

    def take(batch) -> int:
        """Record one page. Returns how many of its rows were new to this walk."""
        nonlocal accounted, duplicates
        fresh = [r for r in batch if _key(r) not in seen]
        duplicates += len(batch) - len(fresh)
        if fresh:
            # The grid moved on. A repeated row on a page that advanced is the
            # portal serving one FIR twice (an FIR number is unique to a
            # station and a year), and it counts towards the declared total.
            # A page with nothing new is the grid handing back the same page,
            # and counts for nothing: the rows behind it were never served.
            accounted += len(batch)
        seen.update(_key(r) for r in fresh)
        keep(fresh)
        return len(fresh)

    take(parse_grid(page))
    if declared:
        pages = (declared + PAGE_SIZE - 1) // PAGE_SIZE
        for number in range(2, pages + 1):
            try:
                page = client.goto_grid_page(number, unit_id, date_from,
                                             date_to, PAGE_SIZE)
                batch = parse_grid(page)
            except (PortalError, SchemaChanged) as exc:
                print(f"      page {number}/{pages}: {type(exc).__name__}: "
                      f"{str(exc)[:70]}", flush=True)
                break
            if not batch:
                # An empty grid before the last page is not "no records":
                # the portal declared more. Say so, keep the page for
                # diagnosis, and leave the chunk incomplete.
                note = portal_message(page) or "no message"
                print(f"      page {number}/{pages}: empty grid ({note[:60]}); "
                      f"page kept under {DEBUG.name}/", flush=True)
                DEBUG.mkdir(parents=True, exist_ok=True)
                (DEBUG / f"{date_from[6:]}-{date_from[3:5]}-{date_from[:2]}"
                 f"_p{number}.html").write_text(str(page), encoding="utf-8")
                break
            if not take(batch):
                # The grid handed back a page we already hold. Stopping is
                # right: continuing would spin, and the fixture in tests/
                # exists because another scraper did exactly that 50 times.
                print(f"      page {number}/{pages}: repeated rows, stopping", flush=True)
                break
            if number % 20 == 0:
                print(f"      page {number}/{pages}", flush=True)

    record = {
        "declared": declared,
        "accounted": accounted,
        "duplicates_dropped": duplicates,
        "complete": declared is not None and accounted >= declared,
    }
    if message:
        record["portal_message"] = message[:120]
    return record


def _key(row) -> tuple[str, str]:
    return (row["police_station"], row["fir_no_with_year"])


def harvest_month(client: MahapoliceClient, unit_id: str, year: int, month: int,
                  state: dict, chunk_days: int = CHUNK_DAYS, redo: bool = False) -> dict:
    key = f"{year:04d}-{month:02d}"
    last_day = calendar.monthrange(year, month)[1]

    # Rows are written as they arrive, and appended to whatever an earlier,
    # interrupted run of this month already holds. Opening the file for
    # writing here once replaced 8,000 held rows of a month with the 50 a
    # fresh walk had reached, and the published page showed the month nearly
    # empty until the walk caught up.
    path = OUT / f"{key}.jsonl"
    OUT.mkdir(parents=True, exist_ok=True)
    held = _held(path)
    handle = path.open("a", encoding="utf-8")

    def keep(rows):
        for row in rows:
            if _key(row) not in held:
                held.add(_key(row))
                handle.write(json.dumps({k: row.get(k, "") for k in KEEP},
                                        ensure_ascii=False) + "\n")
        handle.flush()

    # The portal's own figure for the whole month is the reference every
    # chunk walk is checked against. It costs one query.
    _, declared, message = _open(client, unit_id, f"01/{month:02d}/{year}",
                                 f"{last_day:02d}/{month:02d}/{year}")

    # A month is walked a chunk at a time, each chunk a short walk with its
    # own completeness. The grid only accepts a page near the one on screen,
    # so a whole month was one walk of ~170 pages, and when the portal
    # dropped it at page 116 the restart began again at page 1. A dropped
    # chunk now costs a week, and a restart skips the chunks already whole.
    prior = {} if redo else ((state["months"].get(key) or {}).get("chunks") or {})
    plan = chunks(year, month, chunk_days)
    labels = [label for _, _, label in plan]
    records: dict[str, dict] = {}
    try:
        for date_from, date_to, label in plan:
            if prior.get(label, {}).get("complete"):
                records[label] = prior[label]
                continue
            if STOP.exists():
                # A clean stop between chunks: nothing walked is lost, and
                # the run can be restarted with new code at no cost.
                STOP.unlink()
                raise StopRequested(f"{key} {label}")
            print(f"    {label} ...", flush=True)
            try:
                records[label] = _walk(client, unit_id, date_from, date_to, keep)
            except (PortalError, SchemaChanged) as exc:
                # The walk never started, or the session is gone. The next
                # chunk's reset rebuilds it; this one is walked next pass.
                print(f"      {type(exc).__name__}: {str(exc)[:90]}", flush=True)
                records[label] = {"complete": False,
                                  "error": f"{type(exc).__name__}: {str(exc)[:200]}"}
            got = records[label]
            print(f"      {got.get('accounted', 0)} of {got.get('declared')}  "
                  f"{'ok' if got.get('complete') else 'INCOMPLETE'}", flush=True)
            _save_month(state, key, held, declared, message, records, chunk_days, labels)
    finally:
        handle.close()
    return _save_month(state, key, held, declared, message, records, chunk_days, labels)


def _save_month(state, key, held, declared, message, records, chunk_days, labels) -> dict:
    """Write the month's record from its chunk records, and checkpoint it.

    The month is whole only when every chunk is whole and the chunks' own
    declared counts reach the portal's figure for the whole month. Fewer
    means something fell between the chunks, and the chunk records are
    dropped so that the next pass walks the month again in full. More is
    allowed: the month is queried first, and FIRs are entered into the
    portal with their original date days after registration (August 2026
    grew from 8,054 to 8,079 in a day), so the chunks can see records the
    whole-month query did not.
    """
    # Until every chunk has been walked the month is simply unfinished, and
    # what has been walked is kept: the first pass dropped three whole
    # weeks of July from the checkpoint by judging the month after each.
    walked_all = set(labels) <= set(records)
    all_complete = walked_all and all(c.get("complete") for c in records.values())
    counts = [c.get("declared") for c in records.values()]
    chunk_sum = sum(counts) if counts and all(c is not None for c in counts) else None
    accounted = sum(c.get("accounted", 0) for c in records.values())
    complete = all_complete and declared is not None and chunk_sum >= declared
    record = {
        "collected": len(held),
        "declared": declared,
        "duplicates_dropped": sum(c.get("duplicates_dropped", 0) for c in records.values()),
        "complete": complete,
        "chunk_days": chunk_days,
        "chunks": records,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    if message:
        record["portal_message"] = message[:120]
    if declared is not None and accounted < declared:
        record["shortfall"] = declared - accounted
    if all_complete and not complete and declared is not None:
        record["chunk_sum_mismatch"] = {"chunks": chunk_sum, "month": declared}
        record["chunks"] = {}
    if complete and chunk_sum != declared:
        record["chunks_found"] = chunk_sum
        print(f"    weeks found {chunk_sum}, the month query said {declared}", flush=True)
    state["months"][key] = record
    save_checkpoint(state)
    return record


# How long to wait before asking the portal for a failed month again. The
# first pass through a degraded portal marked 25 months failed in 25 minutes,
# one query each, and moved on; the portal was answering normally again half
# an hour later. Waiting is what a person at the form would do.
BACKOFF = (60, 120, 300, 600, 900)


def harvest_month_patiently(client, unit_id, year, month, state, chunk_days, redo,
                            rebuild, sleep=time.sleep, backoff=BACKOFF):
    """harvest_month, retried with growing pauses when the portal fails it.

    `rebuild()` returns a fresh client, since a failed search usually means
    the session is gone. Returns (record or None, client); None means the
    month failed every attempt and was recorded as such.
    """
    for attempt, pause in enumerate((*backoff, None)):
        try:
            return harvest_month(client, unit_id, year, month, state,
                                 chunk_days=chunk_days, redo=redo), client
        except (PortalError, SchemaChanged) as exc:
            key = f"{year:04d}-{month:02d}"
            # Keep whatever chunk progress the month had already checkpointed.
            state["months"][key] = {
                **(state["months"].get(key) or {}),
                "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                "complete": False,
                "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            }
            save_checkpoint(state)
            if pause is None:
                print(f"  FAILED after {attempt} retries: {type(exc).__name__}: "
                      f"{str(exc)[:90]}", flush=True)
                return None, rebuild()
            print(f"  {type(exc).__name__}: {str(exc)[:70]}; waiting {pause}s "
                  f"before asking again", flush=True)
            sleep(pause)
            client = rebuild()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    today = dt.date.today()
    parser.add_argument("--from", dest="start", default="2021-01")
    parser.add_argument("--to", dest="end", default=f"{today:%Y-%m}")
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--redo", action="store_true",
                        help="re-fetch months already marked complete")
    parser.add_argument("--chunk-days", type=int, default=CHUNK_DAYS,
                        help="walk each month in date ranges this long")
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

        def rebuild():
            fresh = MahapoliceClient(delay=args.delay)
            fresh.open_form()
            fresh.select_unit(unit[0])
            return fresh

        try:
            record, client = harvest_month_patiently(
                client, unit[0], year, month, state, args.chunk_days, args.redo, rebuild)
        except StopRequested as where:
            print(f"  stop requested at {where}; checkpoint written, exiting", flush=True)
            return 0
        except PortalError as exc:
            print(f"  cannot re-establish a session: {exc}")
            return 1
        if record is None:
            continue
        flag = "ok" if record["complete"] else f"INCOMPLETE {record}"
        print(f"  {record['collected']} rows of {record['declared']}  {flag}  "
              f"[{client.requests_made} requests, {client.retries} retries]",
              flush=True)

    complete = sum(1 for v in state["months"].values() if v.get("complete"))
    total = sum(v.get("collected", 0) for v in state["months"].values())
    print(f"\n{complete} months complete, {total} records on disk")
    print(f"requests made this run: {client.requests_made}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
