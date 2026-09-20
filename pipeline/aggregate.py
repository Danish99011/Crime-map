"""Turn FIR records into what a map may show, and refuse to show the rest.

Three rules are enforced here rather than left to the front end, because a rule
that lives only in the UI is a rule that the next developer removes.

**1. Small counts are suppressed.** A thana-month with one or two FIRs in a
category is suppressed and reported as such. In England this kind of threshold
protects a household from being identified. In India the binding risk is
different and worse: localities are frequently segregated by caste and religion,
so a map that shades a small area on three incidents is publishing a claim about
a community. The threshold is a display rule first and a privacy control second.

**2. "No data" and "no crime" are different colours.** 328 of Bihar's 896 thanas
currently have no station we can attach crime to. Rendering them as zero would
invent safety. Every thana carries an explicit `status`, and only `published`
means a number you may read.

**3. Every figure carries what is wrong with it.** Counts are of FIRs
*registered by a station*, not offences located in its jurisdiction. Sexual
offences and POCSO are absent by law, not by fortune. The principal offence rule
depletes subordinate heads wherever worse crime co-occurs. These travel with the
data as structured caveats so the UI cannot lose them.

Rates are deliberately not computed. There is no thana-level population — the
last census was 2011 and the next lands around 2028 — and dividing by a stale or
invented denominator would redden fast-growing peri-urban thanas for purely
demographic reasons. Counts only, clearly labelled.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date

from .fir import FirRecord
from .resolver import ThanaResolver
from .taxonomy import BY_KEY, CRIME_HEADS, WITHHELD_KEYS

# A thana-month-category with fewer than this many FIRs is not displayed.
MIN_DISPLAY_COUNT = 3

PUBLISHED = "published"
SUPPRESSED = "suppressed"    # below the display threshold
NO_DATA = "no-data"          # no station we can attach crime to
WITHHELD = "withheld"        # excluded from the source by law


@dataclass(frozen=True)
class Cell:
    """One thana, one month, one crime head."""

    thana_id: str
    month: str
    crime_key: str
    count: int
    status: str

    @property
    def display_count(self) -> int | None:
        return self.count if self.status == PUBLISHED else None


@dataclass
class Aggregation:
    cells: list[Cell] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    caveats: list[dict] = field(default_factory=list)
    unmapped: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "cells": [asdict(c) for c in self.cells],
            "coverage": self.coverage,
            "caveats": self.caveats,
            "unmapped_sample": self.unmapped[:50],
        }


def standing_caveats(months: list[str], source_name: str) -> list[dict]:
    """Caveats that are true of this data whatever it contains."""
    latest = max(months) if months else None
    caveats = [
        {
            "id": "reporting-office",
            "severity": "critical",
            "headline": "This maps where crimes were reported, not where they happened",
            "detail": (
                "Counts are FIRs registered by a police station. A station that "
                "registers complaints readily will look worse than one that turns "
                "people away. The error runs one way and does not average out."
            ),
        },
        {
            "id": "withheld-categories",
            "severity": "critical",
            "headline": "Sexual offences and offences against children are missing by law",
            "detail": (
                "A Supreme Court direction of 7 September 2016 excludes sexual "
                "offences and POCSO cases from public FIR publication, and Bihar's "
                "repository additionally withholds national security, law and order "
                "and communal FIRs. Their absence here says nothing about whether "
                "they occurred."
            ),
        },
        {
            "id": "principal-offence",
            "severity": "important",
            "headline": "Only the most serious offence in each FIR is counted",
            "detail": (
                "Following NCRB practice, an FIR for murder that also involved theft "
                "counts once, as murder. Lesser categories are therefore undercounted "
                "wherever more serious crime occurs alongside them."
            ),
        },
        {
            "id": "no-rates",
            "severity": "important",
            "headline": "These are counts, not rates",
            "detail": (
                "There is no population figure for a police station jurisdiction. The "
                "last census was in 2011 and the next is not expected to publish "
                "district tables before about 2028, so a per-capita rate would be "
                "built on a stale denominator. A large thana will show more crime "
                "partly because more people live in it."
            ),
        },
        {
            "id": "suppression",
            "severity": "note",
            "headline": f"Fewer than {MIN_DISPLAY_COUNT} cases is shown as 'too few to display'",
            "detail": (
                "Small counts are withheld because Indian localities are often "
                "segregated by caste and religion, and shading a small area on two or "
                "three incidents makes a claim about a community rather than a place."
            ),
        },
        {
            "id": "provenance",
            "severity": "note",
            "headline": f"Source: {source_name}" + (f", latest data {latest}" if latest else ""),
            "detail": (
                "Police station boundaries are from i-Bhugoal via datameet; station "
                "locations from the MHA station master. Neither was published for this "
                "purpose and both carry known errors — see data/spine/build_report.json."
            ),
        },
    ]
    return caveats


def aggregate(records: list[FirRecord], resolver: ThanaResolver,
              all_thana_ids: list[str], source_name: str = "unknown",
              min_count: int = MIN_DISPLAY_COUNT) -> Aggregation:
    """Aggregate FIRs to thana-month-category cells with disclosure control."""
    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    unmapped: list[dict] = []
    unmapped_reasons: Counter = Counter()

    for record in records:
        if not record.month:
            unmapped_reasons["no-date"] += 1
            continue
        result = resolver.resolve(record.police_station, record.district)
        if not result.ok:
            unmapped_reasons[result.method] += 1
            if len(unmapped) < 200:
                unmapped.append({
                    "police_station": record.police_station,
                    "district": record.district,
                    "reason": result.method,
                    "best_confidence": result.confidence,
                })
            continue
        counts[(result.thana_id, record.month, record.crime_key)] += 1

    cells = [
        Cell(thana_id, month, crime_key, count,
             PUBLISHED if count >= min_count else SUPPRESSED)
        for (thana_id, month, crime_key), count in sorted(counts.items())
    ]

    with_data = {c.thana_id for c in cells}
    months = sorted({c.month for c in cells})
    published = [c for c in cells if c.status == PUBLISHED]

    coverage = {
        "records_in": len(records),
        "records_mapped": sum(c.count for c in cells),
        "records_unmapped": len(records) - sum(c.count for c in cells),
        "unmapped_reasons": dict(unmapped_reasons),
        "thanas_total": len(all_thana_ids),
        "thanas_with_data": len(with_data),
        "thanas_no_data": len(all_thana_ids) - len(with_data),
        "months": months,
        "cells_total": len(cells),
        "cells_published": len(published),
        "cells_suppressed": len(cells) - len(published),
        "withheld_categories": list(WITHHELD_KEYS),
        "min_display_count": min_count,
    }
    return Aggregation(cells=cells, coverage=coverage,
                       caveats=standing_caveats(months, source_name),
                       unmapped=unmapped)


def thana_status(thana_id: str, aggregation: Aggregation) -> str:
    """What a single thana should render as."""
    relevant = [c for c in aggregation.cells if c.thana_id == thana_id]
    if not relevant:
        return NO_DATA
    if any(c.status == PUBLISHED for c in relevant):
        return PUBLISHED
    return SUPPRESSED


def category_catalogue() -> list[dict]:
    """The crime heads, with why each one may be missing or misleading."""
    catalogue = []
    for head in CRIME_HEADS:
        catalogue.append({
            "key": head.key,
            "label": head.label,
            "group": head.group,
            "severity": head.severity,
            "withheld": head.withheld,
            "resolution_loss": head.resolution_loss,
            "no_ipc_predecessor": head.no_ipc_predecessor,
        })
    return catalogue
