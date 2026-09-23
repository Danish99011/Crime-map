"""The harvester walks a month in date chunks and must not lose what it holds.

Two things drove the design under test here, both seen on the live portal on
2026-09-22:

* **A mid-walk failure cost the whole month.** The grid only accepts a page
  near the one on screen, so a month of 170 pages is a single 3-hour walk,
  and the portal dropped two months in a row at pages 116 and 54. Each
  restart walked from page 1 again. A month is now fetched in date chunks
  (a week by default), each its own short walk with its own completeness,
  so a failure costs a week and a restart skips the weeks already whole.
  The portal's date filter is inclusive at both ends and the weekly counts
  summed exactly to the month's own count (2,075 + 2,296 + 2,214 + 2,055 =
  8,640 for June 2026), which is checked again for every month fetched:
  the chunks must add up to the portal's whole-month figure or the month
  stays incomplete.
* **A restart threw away the rows on disk.** The month's file was opened
  for writing on every start, so one restart replaced 8,000 held rows with
  50. Rows are now appended; a torn last line from a mid-write kill is
  dropped.

The fake client serves rows by the date range asked for, paged the way the
portal pages, and the parsers are replaced by ones that read that shape, so
the harvester's own bookkeeping is what is under test.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import harvest_mumbai as hm  # noqa: E402

BNS_THEFT = "भारतीय न्याय संहिता (बी एन एस), 2023 - 303(2) ;"


def row(station, number, day):
    return {"state": "MAHARASHTRA", "district": "BRIHAN MUMBAI CITY",
            "police_station": station, "year": "2026", "fir_number": str(number),
            "registration_date": f"{day:02d}/08/2026 10:00:00",
            "fir_no_with_year": f"{number:04d}/2026", "sections": BNS_THEFT}


def _day(text):
    return int(text.split("/")[0])


class FakeClient:
    """Serves `rows` filtered to the range asked for, `page_size` at a time.

    `fail` maps (date_from, page) to how many times that page should raise
    before it works; `repeat` names a range whose page 2 is page 1 again;
    `declared_override` lets the whole-month figure disagree with the rows.
    """

    def __init__(self, rows, page_size=1, fail=None, repeat=None, declared_override=None):
        self.rows, self.page_size = rows, page_size
        self.fail, self.repeat = dict(fail or {}), repeat
        self.declared_override = declared_override or {}
        self.requests_made = self.retries = 0
        self.searched = []

    def _in(self, date_from, date_to):
        lo, hi = _day(date_from), _day(date_to)
        return [r for r in self.rows if lo <= _day(r["registration_date"]) <= hi]

    def _page(self, date_from, date_to, number):
        rows = self._in(date_from, date_to)
        if self.repeat == date_from and number == 2:
            number = 1
        start = (number - 1) * self.page_size
        return {"rows": rows[start:start + self.page_size],
                "declared": self.declared_override.get(date_from, len(rows))}

    def reset(self, unit_id):
        self.requests_made += 3

    def search(self, unit_id, date_from, date_to, page_size):
        self.requests_made += 1
        self.searched.append((date_from, date_to))
        return self._page(date_from, date_to, 1)

    def goto_grid_page(self, number, unit_id, date_from, date_to, page_size):
        self.requests_made += 1
        left = self.fail.get((date_from, number), 0)
        if left:
            self.fail[(date_from, number)] = left - 1
            raise hm.PortalError("connection reset")
        return self._page(date_from, date_to, number)


@pytest.fixture
def harvest(monkeypatch, tmp_path):
    out = tmp_path / "mumbai"
    monkeypatch.setattr(hm, "OUT", out)
    monkeypatch.setattr(hm, "CHECKPOINT", out / "_checkpoint.json")
    monkeypatch.setattr(hm, "DEBUG", out / "_debug")      # never the real data dir
    monkeypatch.setattr(hm, "STOP", out / "_stop")
    def parse_grid(page):
        if page["rows"] is None:
            raise hm.SchemaChanged("no table with id 'gdvDeadBody' on this page")
        return list(page["rows"])
    monkeypatch.setattr(hm, "parse_grid", parse_grid)
    monkeypatch.setattr(hm, "total_records", lambda page: page["declared"])
    monkeypatch.setattr(hm, "portal_message", lambda page: None)
    monkeypatch.setattr(hm, "PAGE_SIZE", 1)

    def run(client, state=None, redo=False, backoff=()):
        state = state if state is not None else {"months": {}}
        record = hm.harvest_month(client, "19378", 2026, 8, state, redo=redo,
                                  sleep=run.slept.append, backoff=backoff)
        text = (out / "2026-08.jsonl").read_text(encoding="utf-8")
        held = [json.loads(l) for l in text.splitlines() if l.strip()]
        return record, held, state

    run.out = out
    run.slept = []
    return run


# Two rows in each week of August 2026: chunks 01-07, 08-14, 15-21, 22-31.
ROWS = [row("AGRIPADA", 1, 1), row("AGRIPADA", 2, 2),
        row("AGRIPADA", 3, 9), row("BANDRA", 1, 10),
        row("BANDRA", 2, 16), row("BANDRA", 3, 17),
        row("COLABA", 1, 23), row("COLABA", 2, 30)]

W1, W2, W3, W4 = "01/08/2026", "08/08/2026", "15/08/2026", "22/08/2026"


def test_a_month_is_cut_into_inclusive_chunks_that_cover_every_day():
    assert hm.chunks(2026, 8) == [(W1, "07/08/2026", "01-07"), (W2, "14/08/2026", "08-14"),
                                  (W3, "21/08/2026", "15-21"), (W4, "31/08/2026", "22-31")]
    assert hm.chunks(2026, 2)[-1] == ("22/02/2026", "28/02/2026", "22-28")
    # A tail of half a chunk or less folds into the chunk before it.
    assert hm.chunks(2026, 6, days=7)[-1] == ("22/06/2026", "30/06/2026", "22-30")
    assert hm.chunks(2026, 6, days=10) == [("01/06/2026", "10/06/2026", "01-10"),
                                           ("11/06/2026", "20/06/2026", "11-20"),
                                           ("21/06/2026", "30/06/2026", "21-30")]
    for year, month in ((2024, 2), (2026, 1), (2026, 4)):
        got = hm.chunks(year, month)
        assert got[0][0].startswith("01/") and _day(got[-1][1]) == hm.calendar.monthrange(year, month)[1]
        for (_, end, _), (start, _, _) in zip(got, got[1:]):
            assert _day(start) == _day(end) + 1


def test_a_clean_walk_is_complete(harvest):
    client = FakeClient(ROWS)
    record, held, _ = harvest(client)
    assert record["complete"] and record["collected"] == 8 and record["declared"] == 8
    assert "shortfall" not in record
    assert [c["complete"] for c in record["chunks"].values()] == [True] * 4
    assert list(record["chunks"]) == ["01-07", "08-14", "15-21", "22-31"]
    assert [r["fir_no_with_year"] for r in held] == [
        "0001/2026", "0002/2026", "0003/2026", "0001/2026",
        "0002/2026", "0003/2026", "0001/2026", "0002/2026"]
    assert set(held[0]) == set(hm.KEEP)
    # The whole month was asked for once (the reference figure), then each week.
    assert client.searched == [(W1, "31/08/2026"), (W1, "07/08/2026"), (W2, "14/08/2026"),
                               (W3, "21/08/2026"), (W4, "31/08/2026")]


def test_a_failure_costs_the_chunk_not_the_month(harvest):
    client = FakeClient(ROWS, fail={(W2, 2): 1})
    record, held, _ = harvest(client)
    assert not record["complete"] and record["shortfall"] == 1
    assert record["collected"] == 7 and len(held) == 7
    assert [c["complete"] for c in record["chunks"].values()] == [True, False, True, True]
    assert record["chunks"]["08-14"]["accounted"] == 1


def test_a_restart_walks_only_the_chunks_that_were_not_whole(harvest):
    _, _, state = harvest(FakeClient(ROWS, fail={(W2, 2): 1}))
    client = FakeClient(ROWS)
    record, held, _ = harvest(client, state=state)
    assert record["complete"] and record["collected"] == 8 and len(held) == 8
    assert client.searched == [(W1, "31/08/2026"), (W2, "14/08/2026")]
    assert len(held) == len({(r["police_station"], r["fir_no_with_year"]) for r in held})
    assert record["duplicates_dropped"] == 0


def test_a_restart_keeps_the_rows_already_held(harvest):
    # First run gets 7 rows; the second dies on the very chunk it has to
    # redo, before adding anything. The file must still hold 7, not shrink.
    _, _, state = harvest(FakeClient(ROWS, fail={(W2, 2): 1}))
    record, held, _ = harvest(FakeClient(ROWS, fail={(W2, 2): 1}), state=state)
    assert len(held) == 7 and record["collected"] == 7 and not record["complete"]


def test_redo_walks_every_chunk_again_without_doubling_rows(harvest):
    _, _, state = harvest(FakeClient(ROWS))
    client = FakeClient(ROWS)
    record, held, _ = harvest(client, state=state, redo=True)
    assert record["complete"] and len(held) == 8 and len(client.searched) == 5


def test_the_grid_repeating_a_page_stops_that_chunk(harvest):
    # Page 2 of the third week is page 1 again: the portal is spinning.
    record, held, _ = harvest(FakeClient(ROWS, repeat=W3))
    chunk = record["chunks"]["15-21"]
    assert not chunk["complete"] and chunk["duplicates_dropped"] == 1 and chunk["accounted"] == 1
    assert not record["complete"] and record["shortfall"] == 1 and len(held) == 7


def test_chunks_that_do_not_add_up_to_the_month_leave_it_incomplete(harvest):
    # The portal's whole-month figure says 9 but the weeks only found 8.
    client = FakeClient(ROWS, declared_override={W1: 9})
    # W1 is also the first week's date_from; give the week its true count.
    client.declared_override = {}
    real_page = client._page

    def page(date_from, date_to, number):
        out = real_page(date_from, date_to, number)
        if (date_from, date_to) == (W1, "31/08/2026"):
            out["declared"] = 9
        return out
    client._page = page
    record, held, _ = harvest(client)
    assert not record["complete"] and record["declared"] == 9 and record["shortfall"] == 1
    assert record["chunk_sum_mismatch"] == {"chunks": 8, "month": 9}
    # Nothing is carried forward: the next pass walks the month again.
    assert record["chunks"] == {}
    assert len(held) == 8


def test_chunks_that_find_more_than_the_month_figure_still_complete(harvest):
    # FIRs are entered days late with their original date, so the weeks,
    # queried after the month, can see one the month figure did not.
    client = FakeClient(ROWS)
    real_page = client._page

    def page(date_from, date_to, number):
        out = real_page(date_from, date_to, number)
        if (date_from, date_to) == (W1, "31/08/2026"):
            out["declared"] = 7
        return out
    client._page = page
    record, held, _ = harvest(client)
    assert record["complete"] and record["declared"] == 7 and len(held) == 8
    assert "chunk_sum_mismatch" not in record and "shortfall" not in record


def test_an_empty_grid_before_the_last_page_leaves_the_chunk_incomplete(harvest, monkeypatch):
    # The portal declared two rows for the week but page 2 comes back with
    # no grid. That is not "no records"; the page is kept for diagnosis.
    monkeypatch.setattr(hm, "DEBUG", harvest.out / "_debug")
    client = FakeClient(ROWS)
    real_page = client._page

    def page(date_from, date_to, number):
        out = real_page(date_from, date_to, number)
        if date_from == W3 and number == 2:
            out["rows"] = []
        return out
    client._page = page
    record, held, _ = harvest(client)
    chunk = record["chunks"]["15-21"]
    assert not chunk["complete"] and chunk["accounted"] == 1 and len(held) == 7
    assert (harvest.out / "_debug" / "2026-08-15_p2.html").exists()


def test_weeks_already_whole_survive_a_kill_before_the_month_is_walked(harvest):
    # The run dies (not a portal error: the container went) after the first
    # week. The checkpoint written after that week must still carry it,
    # so the restart skips it. The first pass threw it away by judging
    # the month's sum after every chunk.
    class Gone(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            if date_from == W2:
                raise RuntimeError("container reclaimed")
            return super().search(unit_id, date_from, date_to, page_size)
    state = {"months": {}}
    with pytest.raises(RuntimeError):
        hm.harvest_month(Gone(ROWS), "19378", 2026, 8, state)
    saved = state["months"]["2026-08"]
    assert saved["chunks"]["01-07"]["complete"] and not saved["complete"]
    assert "chunk_sum_mismatch" not in saved
    client = FakeClient(ROWS)
    record, held, _ = harvest(client, state=state)
    assert record["complete"] and len(held) == 8
    assert (W1, "07/08/2026") not in client.searched


def test_the_stop_file_ends_the_run_between_chunks_without_loss(harvest, monkeypatch):
    stop = harvest.out / "_stop"
    monkeypatch.setattr(hm, "STOP", stop)

    class Touching(FakeClient):
        def goto_grid_page(self, number, unit_id, date_from, date_to, page_size):
            if date_from == W2 and number == 2:
                stop.parent.mkdir(parents=True, exist_ok=True)
                stop.touch()
            return super().goto_grid_page(number, unit_id, date_from, date_to, page_size)
    state = {"months": {}}
    with pytest.raises(hm.StopRequested):
        hm.harvest_month(Touching(ROWS), "19378", 2026, 8, state)
    saved = state["months"]["2026-08"]
    assert [c["complete"] for c in saved["chunks"].values()] == [True, True]
    assert not stop.exists()          # consumed, so the next run is not stopped too
    client = FakeClient(ROWS)
    record, held, _ = harvest(client, state=state)
    assert record["complete"] and len(held) == 8
    assert client.searched == [(W1, "31/08/2026"), (W3, "21/08/2026"), (W4, "31/08/2026")]


def test_a_total_of_one_full_page_is_asked_for_again(harvest, monkeypatch):
    # The portal said 50 for June 2026 once, for a month of 8,640. Here it
    # says 1 (one full page of one row) for the second week's first query
    # and the truth on the second; the first page is kept for diagnosis.
    monkeypatch.setattr(hm, "DEBUG", harvest.out / "_debug")
    client = FakeClient(ROWS)
    real_page, asked = client._page, {"n": 0}

    def page(date_from, date_to, number):
        out = real_page(date_from, date_to, number)
        if date_from == W2 and number == 1:
            asked["n"] += 1
            if asked["n"] == 1:
                out["declared"] = 1
        return out
    client._page = page
    record, held, _ = harvest(client)
    assert record["complete"] and len(held) == 8
    assert record["chunks"]["08-14"]["declared"] == 2
    assert asked["n"] == 2
    assert (harvest.out / "_debug" / "2026-08-08_total1.html").exists()


def test_a_wrong_month_figure_is_recorded_beside_what_the_weeks_found(harvest):
    client = FakeClient(ROWS)
    real_page = client._page

    def page(date_from, date_to, number):
        out = real_page(date_from, date_to, number)
        if (date_from, date_to) == (W1, "31/08/2026"):
            out["declared"] = 1        # one full page: asked again, same answer
        return out
    client._page = page
    record, held, _ = harvest(client)
    assert record["complete"] and record["declared"] == 1 and record["chunks_found"] == 8
    assert client.searched.count((W1, "31/08/2026")) == 2


def test_a_failed_month_is_asked_for_again_after_a_pause(harvest):
    # The portal answers the first two whole-month queries with its error
    # page. The month must be waited for, not skipped: the third attempt
    # walks it whole.
    class Degraded(FakeClient):
        failures = 2

        def search(self, unit_id, date_from, date_to, page_size):
            if Degraded.failures and (date_from, date_to) == (W1, "31/08/2026"):
                Degraded.failures -= 1
                raise hm.PortalError("search returned the portal's error page")
            return super().search(unit_id, date_from, date_to, page_size)
    state, waited, built = {"months": {}}, [], []

    def rebuild():
        built.append(1)
        return Degraded(ROWS)
    record, client = hm.harvest_month_patiently(
        Degraded(ROWS), "19378", 2026, 8, state, 7, False, rebuild,
        sleep=waited.append, backoff=(1, 2, 4))
    assert record["complete"] and waited == [1, 2] and len(built) == 2
    assert "error" not in state["months"]["2026-08"]


def test_a_month_that_fails_every_attempt_is_recorded_and_left(harvest):
    class Dead(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            raise hm.PortalError("portal error page")
    state, waited = {"months": {"2026-08": {"collected": 40, "declared": 90}}}, []
    record, client = hm.harvest_month_patiently(
        Dead(ROWS), "19378", 2026, 8, state, 7, False, lambda: Dead(ROWS),
        sleep=waited.append, backoff=(1, 2))
    assert record is None and waited == [1, 2]
    saved = state["months"]["2026-08"]
    assert saved["complete"] is False and saved["error"].startswith("PortalError")
    assert saved["collected"] == 40 and saved["declared"] == 90   # earlier progress kept


def test_a_month_query_without_a_grid_is_kept_and_the_weeks_walked_anyway(harvest):
    # The portal answered the whole-month query without a grid for 30
    # months in a row on 2026-09-22 while answering every weekly query.
    # The month is judged by its weeks; their sum becomes its figure.
    class NoMonthGrid(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            if (date_from, date_to) == (W1, "31/08/2026"):
                return {"rows": None, "declared": None}
            return super().search(unit_id, date_from, date_to, page_size)
    record, held, _ = harvest(NoMonthGrid(ROWS))
    assert record["complete"] and len(held) == 8
    assert record["declared"] == 8 and record["month_query"] == "no grid"
    assert "chunk_sum_mismatch" not in record
    assert (harvest.out / "_debug" / "2026-08-01_nogrid.html").exists()


def test_a_month_query_without_a_grid_carries_the_last_figure_while_incomplete(harvest):
    class NoMonthGrid(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            if (date_from, date_to) == (W1, "31/08/2026"):
                return {"rows": None, "declared": None}
            return super().search(unit_id, date_from, date_to, page_size)
    state = {"months": {"2026-08": {"collected": 3, "declared": 9}}}
    record, held, _ = harvest(NoMonthGrid(ROWS, fail={(W3, 2): 1}), state=state)
    assert not record["complete"] and record["declared"] == 9
    assert record["month_query"].startswith("no grid; figure carried")
    assert record["shortfall"] == 2


def test_a_week_query_without_a_grid_is_waited_for_and_asked_again(harvest):
    # The portal refuses the second week twice, then answers. The week is
    # waited for and walked whole; the month completes.
    class Flaky(FakeClient):
        refusals = 2

        def search(self, unit_id, date_from, date_to, page_size):
            if date_from == W2 and Flaky.refusals:
                Flaky.refusals -= 1
                return {"rows": None, "declared": None}
            return super().search(unit_id, date_from, date_to, page_size)
    record, held, _ = harvest(Flaky(ROWS), backoff=(1, 2, 4))
    assert record["complete"] and len(held) == 8 and harvest.slept == [1, 2]
    assert (harvest.out / "_debug" / "2026-08-08_nogrid.html").exists()


def test_a_week_that_fails_every_wait_is_recorded_and_left_for_the_next_pass(harvest):
    class NoWeekGrid(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            if date_from == W2:
                return {"rows": None, "declared": None}
            return super().search(unit_id, date_from, date_to, page_size)
    record, held, _ = harvest(NoWeekGrid(ROWS), backoff=(1, 2))
    assert not record["complete"] and "error" in record["chunks"]["08-14"]
    assert harvest.slept == [1, 2] and len(held) == 6
    assert [c.get("complete") for c in record["chunks"].values()] == [True, False, True, True]


def test_a_torn_last_line_is_dropped_before_appending(harvest):
    harvest.out.mkdir(parents=True)
    path = harvest.out / "2026-08.jsonl"
    path.write_text(json.dumps(row("AGRIPADA", 1, 1), ensure_ascii=False) + "\n"
                    + '{"state": "MAHARASHTRA", "district": "BRI', encoding="utf-8")
    record, held, _ = harvest(FakeClient(ROWS))
    assert record["complete"] and len(held) == 8
    assert all(json.loads(l) for l in path.read_text(encoding="utf-8").splitlines())


def test_an_error_before_any_page_is_recorded_on_the_chunk(harvest):
    class Dead(FakeClient):
        def search(self, unit_id, date_from, date_to, page_size):
            if date_from == W4:
                raise hm.PortalError("portal error page")
            return super().search(unit_id, date_from, date_to, page_size)
    record, held, _ = harvest(Dead(ROWS))
    assert not record["complete"] and len(held) == 6
    assert record["chunks"]["22-31"]["complete"] is False
    assert "error" in record["chunks"]["22-31"]
    assert record["shortfall"] == 2
