"""The canonical FIR record, built so it cannot carry a person's identity.

Bihar's repository publishes FIRs that contain the names and addresses of
complainants and accused. Phase 1 set a standing rule: aggregate to
station-month and drop identifiers at ingestion. This module enforces that rule
in the type system rather than in a code review comment.

`FirRecord` has no field for a name, an address, a phone number or an age. It is
built through `from_row`, which copies only the fields named in an explicit
mapping and reports everything it discarded. A field that is not on the list
cannot reach the database by accident, and the count of dropped columns is
surfaced so that a source quietly gaining a new identifier column is visible
rather than silent.

What we keep is what a map needs: where it was registered, when, and under what
sections. That is enough to colour a thana and nothing like enough to identify
a person.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable, Iterator

from .taxonomy import classify, parse_sections

# Columns that must never be carried, whatever a source calls them. Matched
# case-insensitively against the column name. This is a backstop: the real
# protection is that from_row copies only what it is told to.
FORBIDDEN_COLUMN = re.compile(
    r"name|father|husband|address|mobile|phone|aadhaar|age|caste|gender|"
    r"complainant|accused|victim|informant|witness|email",
    re.I,
)

DATE_FORMATS = (
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%y",
)


def parse_date(value: str | None) -> date | None:
    """Parse the date formats Indian police portals actually emit.

    Day-first is assumed throughout, which is the Indian convention. An
    ambiguous value like 03/04/2025 is therefore 3 April, not 4 March; a source
    that uses month-first must be converted before it reaches here, or a third
    of the year silently lands in the wrong month.
    """
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


@dataclass(frozen=True)
class FirRecord:
    """One registered FIR, stripped to what a map may lawfully show."""

    source: str
    state: str
    district: str
    police_station: str
    fir_number: str
    fir_year: int | None
    registered_on: date | None
    act: str
    sections: tuple[str, ...]
    crime_key: str
    classified: bool
    dropped_columns: tuple[str, ...] = field(default=(), repr=False)

    @property
    def month(self) -> str | None:
        return self.registered_on.strftime("%Y-%m") if self.registered_on else None

    @classmethod
    def from_row(cls, row: dict, mapping: dict[str, str], source: str,
                 state: str = "BIHAR") -> "FirRecord":
        """Build a record from a source row using an explicit column mapping.

        `mapping` maps our field names to the source's column names. Anything
        not named there is discarded and reported, so a source that starts
        emitting a new personal-data column shows up in `dropped_columns`
        instead of slipping through.
        """
        def get(name: str) -> str:
            column = mapping.get(name)
            return (str(row.get(column, "")).strip() if column else "")

        kept = {c for c in mapping.values() if c}
        dropped = tuple(sorted(c for c in row if c not in kept))

        act = get("act")
        sections = tuple(parse_sections(get("sections")))
        crime_key, classified = classify(list(sections), act)
        registered = parse_date(get("registered_on"))

        year_text = get("fir_year")
        fir_year = int(year_text) if year_text.isdigit() else (
            registered.year if registered else None)

        return cls(
            source=source,
            state=state,
            district=get("district").upper(),
            police_station=get("police_station"),
            fir_number=get("fir_number"),
            fir_year=fir_year,
            registered_on=registered,
            act=act,
            sections=sections,
            crime_key=crime_key,
            classified=classified,
            dropped_columns=dropped,
        )


def audit_columns(columns: Iterable[str]) -> list[str]:
    """Return source columns that look like personal data.

    Called before ingestion so the operator sees what a feed contains and can
    confirm the mapping excludes it. Finding names here is expected, not alarming
    — the FIR listing genuinely publishes them. Carrying them downstream is what
    would be wrong.
    """
    return sorted(c for c in columns if FORBIDDEN_COLUMN.search(c or ""))


def summarise(records: Iterator[FirRecord] | list[FirRecord]) -> dict:
    records = list(records)
    unclassified = [r for r in records if not r.classified]
    undated = [r for r in records if r.registered_on is None]
    return {
        "records": len(records),
        "unclassified": len(unclassified),
        "unclassified_share": round(len(unclassified) / len(records), 4) if records else 0.0,
        "undated": len(undated),
        "districts": len({r.district for r in records}),
        "stations": len({(r.district, r.police_station) for r in records}),
        "months": sorted({r.month for r in records if r.month}),
    }
