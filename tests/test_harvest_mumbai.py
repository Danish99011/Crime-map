"""The harvester must not throw away a month's rows when it is restarted.

The portal's GridView only accepts a page near the one on screen, so an
interrupted month has to be walked again from page 1. That costs time, and
there is no way round it. What it must not cost is data: before this test
existed, the month's file was opened for writing on every start, so a
restart at page 80 of 161 replaced 4,000 rows on disk with the 50 the fresh
walk had reached. The published page then showed a month it had held nearly
complete as almost empty. Rows already held are kept; the walk only adds.

The fake client below serves a month as a fixed list of pages, and the
parsers are replaced by ones that read that shape, so the harvester's own
bookkeeping is what is under test.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import harvest_mumbai as hm  # noqa: E402


def row(station, number):
    return {"state": "MAHARASHTRA", "district": "BRIHAN MUMBAI CITY",
            "police_station": station, "year": "2026", "fir_number": str(number),
            "registration_date": "01/08/2026 10:00:00",
            "fir_no_with_year": f"{number:04d}/2026",
            "sections": "भारतीय न्याय संहिता (बी एन एस), 2023 - 303(2) ;"}


class FakeClient:
    """Serves `pages` in order; `die_after` pages, raises like a lost session."""

    def __init__(self, pages, declared, die_after=None):
        self.pages, self.declared, self.die_after = pages, declared, die_after
        self.requests_made = self.retries = 0

    def reset(self, unit_id):
        pass

    def search(self, unit_id, date_from, date_to, page_size):
        self.requests_made += 1
        return {"rows": self.pages[0], "declared": self.declared}

    def goto_grid_page(self, number, unit_id, date_from, date_to, page_size):
        self.requests_made += 1
        if self.die_after is not None and number > self.die_after:
            raise hm.PortalError("connection reset")
        return {"rows": self.pages[number - 1], "declared": self.declared}


@pytest.fixture
def harvest(monkeypatch, tmp_path):
    out = tmp_path / "mumbai"
    monkeypatch.setattr(hm, "OUT", out)
    monkeypatch.setattr(hm, "CHECKPOINT", out / "_checkpoint.json")
    monkeypatch.setattr(hm, "parse_grid", lambda page: list(page["rows"]))
    monkeypatch.setattr(hm, "total_records", lambda page: page["declared"])
    monkeypatch.setattr(hm, "portal_message", lambda page: None)
    monkeypatch.setattr(hm, "PAGE_SIZE", 2)

    def run(pages, declared, die_after=None, state=None):
        state = state if state is not None else {"months": {}}
        client = FakeClient(pages, declared, die_after)
        record = hm.harvest_month(client, "19378", 2026, 8, state)
        held = [json.loads(l) for l in (out / "2026-08.jsonl").read_text(
            encoding="utf-8").splitlines() if l.strip()]
        return record, held, state

    return run


PAGES = [[row("AGRIPADA", 1), row("AGRIPADA", 2)],
         [row("AGRIPADA", 3), row("BANDRA", 1)],
         [row("BANDRA", 2), row("BANDRA", 3)]]


def test_a_clean_walk_is_complete(harvest):
    record, held, _ = harvest(PAGES, declared=6)
    assert record["complete"] and record["collected"] == 6 and "shortfall" not in record
    assert [r["fir_no_with_year"] for r in held] == [
        "0001/2026", "0002/2026", "0003/2026", "0001/2026", "0002/2026", "0003/2026"]
    assert set(held[0]) == set(hm.KEEP)


def test_an_interrupted_walk_is_incomplete_but_keeps_what_it_got(harvest):
    record, held, _ = harvest(PAGES, declared=6, die_after=2)
    assert not record["complete"] and record["collected"] == 4 and record["shortfall"] == 2
    assert len(held) == 4


def test_a_restart_keeps_the_rows_already_held(harvest):
    # First run dies after page 2 holding 4 rows; second run is interrupted
    # even earlier. The file must still hold 4, not shrink to 2.
    _, _, state = harvest(PAGES, declared=6, die_after=2)
    record, held, _ = harvest(PAGES, declared=6, die_after=1, state=state)
    assert len(held) == 4 and record["collected"] == 4
    assert not record["complete"] and record["shortfall"] == 4


def test_a_restart_that_finishes_completes_without_duplicating_rows(harvest):
    _, _, state = harvest(PAGES, declared=6, die_after=2)
    record, held, _ = harvest(PAGES, declared=6, state=state)
    assert record["complete"] and record["collected"] == 6
    assert len(held) == 6 == len({(r["police_station"], r["fir_no_with_year"]) for r in held})
    assert record["duplicates_dropped"] == 0   # re-served rows are not duplicates


def test_pages_already_held_do_not_stop_the_walk(harvest):
    # After a restart the first pages are all rows already on disk. That is
    # not the grid repeating itself, and the walk must continue past them.
    _, _, state = harvest(PAGES, declared=6, die_after=2)
    record, held, _ = harvest(PAGES, declared=6, state=state)
    assert record["complete"] and len(held) == 6


def test_the_grid_repeating_a_page_stops_the_walk(harvest):
    # Page 3 is page 2 again: the portal is spinning, so stop and record it.
    pages = [PAGES[0], PAGES[1], PAGES[1]]
    record, held, _ = harvest(pages, declared=6)
    assert not record["complete"] and record["collected"] == 4
    assert record["duplicates_dropped"] == 2 and record["shortfall"] == 2
    assert len(held) == 4


def test_a_completed_month_is_not_reopened_for_appending_twice(harvest):
    # --redo on a complete month: rows are re-served, nothing is doubled.
    _, _, state = harvest(PAGES, declared=6)
    record, held, _ = harvest(PAGES, declared=6, state=state)
    assert len(held) == 6 and record["complete"]
