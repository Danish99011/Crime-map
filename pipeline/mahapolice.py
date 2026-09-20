"""Maharashtra Police published-FIR grid: the parser and the form it comes from.

Maharashtra runs the most open crime feed in India. Every FIR its stations
register appears on a public page within a day, with the station, the
registration timestamp to the second, and the acts and sections cited. There is
no login and no CAPTCHA. `docs/PHASE1-FINDINGS.md` calls it the richest single
feed found, and that is still true.

What it does **not** publish is where anything happened. A row names the police
station that registered the FIR, not a location. The finest honest unit is the
thana jurisdiction, and Maharashtra publishes no jurisdiction polygons at all,
so for Mumbai even that is approximate. Nothing here may be drawn as a pin.

Two things in this module exist to prevent one specific failure. The portal is
an ASP.NET form, and a form posted with wrong parameters answers with an empty
grid rather than an error. **An empty grid is indistinguishable from an absence
of crime**, and would be rendered as a safe neighbourhood. So:

* `parse_grid` raises `SchemaChanged` when it does not recognise the table. It
  never returns `[]` as a way of saying "I did not understand this page".
* `total_records` reads the portal's own count of matching records, so a caller
  can compare what it was promised against what it actually parsed and notice a
  paging bug instead of silently under-reporting a neighbourhood.

Personal data: there is none in this grid, and that is a property of the source
rather than of our handling. The ten published columns carry no complainant, no
accused, no address, no age and no phone. `parse_grid` still returns only the
columns named in `COLUMNS`, so a portal that starts publishing an identifier
column drops it here, at the boundary, rather than somewhere downstream.
"""

from __future__ import annotations

import html
import re

# The grid's own element id. Stable across the pages captured so far, and the
# only table on the results page that carries an id.
GRID_ID = "ContentPlaceHolder1_gdvDeadBody"

# The portal's English headers, in the order it renders them. Two of them
# differ only by a full stop -- "FIR No." is the serial within the year and
# "FIR No" is that serial with the year appended -- so columns are read by
# position against this list and never by header text alone.
EXPECTED_HEADERS = (
    "sr. no.", "state", "district", "police station", "year", "fir no.",
    "registration date", "fir no", "sections", "download",
)

# Position in the row -> our field name. "Download" is a per-row submit button
# for the FIR PDF and carries no text; it is deliberately not mapped.
COLUMNS = {
    0: "sr_no",
    1: "state",
    2: "district",
    3: "police_station",
    4: "year",
    5: "fir_number",
    6: "registration_date",
    7: "fir_no_with_year",
    8: "sections",
}

# How those columns feed `FirRecord.from_row`. Registration date is the only
# date Maharashtra publishes -- there is no occurrence date and no disposal
# field -- so every Maharashtra record is counted on a registration basis.
MAPPING = {
    "district": "district",
    "police_station": "police_station",
    "fir_number": "fir_number",
    "fir_year": "year",
    "registered_on": "registration_date",
    "sections": "sections",
}

# The portal renders the count and its label as two separate spans, so the
# count is read from the labelled span first and only then from running text.
# A data row is recognised by the GridView's own per-row span ids
# (`..._gdvDeadBody_<label>_<rowindex>`). Recognising rows by cell count
# instead lets the pager row -- a <tr class="gridPager"> wrapping a nested
# table of page links -- through as a 51st FIR whose district is "3".
DATA_ROW = re.compile(r'id="%s_[A-Za-z]+\d*_\d+"' % re.escape(GRID_ID), re.I)

# The portal's own way of saying it holds nothing for this query. Distinct
# from a page we failed to understand, and treated differently: see
# `parse_grid`.
NO_RECORDS = re.compile(r'id="%s_lblNoRowsFound"' % re.escape(GRID_ID), re.I)

# Validation text the portal returns with an out-of-range query. It states the
# two limits that bound any harvest: the published series starts 2017-01-01,
# and no single query may span more than 90 days.
PORTAL_MESSAGE = re.compile(
    r'id="ContentPlaceHolder1_lblMsg"[^>]*>(.*?)</span>', re.S | re.I)

TOTAL_LABEL = re.compile(
    r'id="ContentPlaceHolder1_lbltotalrecord"[^>]*>\s*([\d,]+)\s*<', re.I)
TOTAL_TEXT = re.compile(r"([\d,]+)\s+total\s+records\s+found", re.I)
TAG = re.compile(r"<[^>]+>")
CELL = re.compile(r"<t([dh])[^>]*>(.*?)</t\1>", re.S | re.I)


class SchemaChanged(RuntimeError):
    """The results page did not look like the grid we know how to read.

    Raised instead of returning an empty list. The caller must treat this as a
    fetch failure, never as a quiet zero -- see the module docstring.
    """


def _text(fragment: str) -> str:
    """Visible text of an HTML fragment, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", fragment))).strip()


def _grid(page: str) -> str:
    """The results table, matched with balanced tags because it nests others."""
    opening = re.search(r'<table[^>]*id="%s"[^>]*>' % re.escape(GRID_ID), page, re.I)
    if not opening:
        raise SchemaChanged(
            f"no table with id {GRID_ID!r} on this page. Either the search "
            f"failed, the session expired, or the portal changed. Refusing to "
            f"report this as zero records.")
    start = opening.start()
    depth = 0
    for tag in re.finditer(r"<(/?)table\b[^>]*>", page[start:], re.I):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return page[start:start + tag.end()]
    raise SchemaChanged("results table is not closed; page truncated mid-transfer")


def _rows(grid: str) -> list[str]:
    """Split the grid into rows, honouring nested tables.

    The pager row wraps a whole table of page links, so a non-greedy
    `<tr>.*?</tr>` stops at the nested table's first `</tr>` and returns a
    truncated fragment. Depth counting keeps each row whole.
    """
    out: list[str] = []
    index = 0
    while True:
        opening = re.search(r"<tr[^>]*>", grid[index:], re.I)
        if not opening:
            return out
        start = index + opening.start()
        depth = 0
        closing = None
        for tag in re.finditer(r"<(/?)tr\b[^>]*>", grid[start:], re.I):
            depth += -1 if tag.group(1) else 1
            if depth == 0:
                closing = start + tag.end()
                break
        if closing is None:
            return out
        out.append(grid[start:closing])
        index = closing


def parse_grid(page: str) -> list[dict]:
    """Rows of the published-FIR grid, as the portal published them.

    Returns one dict per FIR carrying only the columns in `COLUMNS`. Raises
    `SchemaChanged` if the table is missing or its headers are not the ones
    this parser was written against.
    """
    grid = _grid(page)
    if NO_RECORDS.search(grid):
        # The portal answered the question and the answer was none. This is a
        # verified zero, not a failure, and is the only path on which this
        # function returns an empty list.
        return []

    rows = _rows(grid)
    if not rows:
        raise SchemaChanged("results table has no rows at all")

    header = [_text(c).lower() for _, c in CELL.findall(rows[0])]
    if tuple(header[:len(EXPECTED_HEADERS)]) != EXPECTED_HEADERS:
        raise SchemaChanged(
            f"unexpected columns.\n  expected: {list(EXPECTED_HEADERS)}\n"
            f"  found   : {header}\n"
            f"The portal has changed its grid. Re-read it and update COLUMNS "
            f"before ingesting anything, because reading the wrong column "
            f"positions would mis-file real crime rather than fail loudly.")

    out: list[dict] = []
    for raw in rows[1:]:
        if not DATA_ROW.search(raw):
            # The pager row and any spacer rows live in this same table. They
            # are skipped on the positive evidence that they carry no GridView
            # cell ids, not on a guess about how many cells they have.
            continue
        cells = [c for kind, c in CELL.findall(raw) if kind.lower() == "d"]
        if len(cells) < len(COLUMNS):
            raise SchemaChanged(
                f"a data row has {len(cells)} cells, fewer than the "
                f"{len(COLUMNS)} columns we read. Refusing to guess which "
                f"column is which.")
        out.append({field: _text(cells[i]) for i, field in COLUMNS.items()})
    return out


def portal_message(page: str) -> str | None:
    """The portal's validation message, if it returned one.

    Worth surfacing because it is where the portal states its own limits --
    "From Date should be greater than 1/01/2017 and date difference between
    From and To Date should be less than 90 days" -- rather than documenting
    them anywhere a caller would find them.
    """
    found = PORTAL_MESSAGE.search(page)
    return _text(found.group(1)) if found else None


def total_records(page: str) -> int | None:
    """How many records the portal says matched, or None if it did not say.

    `None` means "not stated" and must never be turned into 0. Comparing this
    against the number of rows actually collected is the paging check: the
    third fixture in `tests/fixtures/` exists because another scraper got this
    wrong and re-fetched page 1 fifty times.
    """
    found = TOTAL_LABEL.search(page) or TOTAL_TEXT.search(_text(page))
    return int(found.group(1).replace(",", "")) if found else None
