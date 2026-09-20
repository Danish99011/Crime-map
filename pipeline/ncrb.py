"""Ingest NCRB district-level crime counts for Bihar, 2001-2014.

This is the only source of actual Bihar crime numbers we hold. It is the
NCRB "Crime in India" district supplementary tables as republished on
data.gov.in under GODL-India, recovered from community mirrors because
ncrb.gov.in is unreachable from this environment.

Three things about it decide how it may be shown:

**It is district-level, and cannot be pushed down.** A district count cannot be
split across the thanas inside it without inventing the split. So this feeds a
separate district layer; it never colours a thana.

**It stops in 2014.** Nothing after that is mirrored anywhere reachable. That
is twelve years stale, so it does not answer "is this area safe now" and must
never be presented as if it did. It is a historical baseline: useful for
validating the pipeline, for long-run trend context, and as the benchmark any
recent feed gets checked against. The recent-data routes are Bihar's live FIR
repository and the Bihar State Data Lab, both of which need network access this
environment does not have.

**Its column names change between years.** The 2001-2012 and 2013 files use
upper-case headers ("STATE/UT", "MURDER"); the 2014 file uses title case
("States/UTs", "Murder") and renames some heads outright ("Attempt to commit
Murder"). Matching is therefore done on a normalised header, or the most recent
year silently contributes nothing.

**Some columns are subsets of others.** THEFT is AUTO THEFT plus OTHER THEFT;
RAPE is CUSTODIAL plus OTHER; KIDNAPPING & ABDUCTION is the two that follow it.
The arithmetic is exact in the data, so the children are skipped rather than
summed — counting both would double every theft in Bihar.

Run:  python3 -m pipeline.ncrb
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ncrb-ogd-district"
REFERENCE = ROOT / "data" / "reference"
SPINE = ROOT / "data" / "spine"

STATE = "BIHAR"

IPC_FILES = (
    "01_District_wise_crimes_committed_IPC_2001_2012.csv",
    "01_District_wise_crimes_committed_IPC_2013.csv",
    "01_District_wise_crimes_committed_IPC_2014.csv",
)

# NCRB column -> our law-neutral crime_key. Columns that are subsets of another
# column are mapped to None and skipped; see the module docstring.
COLUMN_TO_KEY: dict[str, str | None] = {
    "MURDER": "homicide",
    "CULPABLE HOMICIDE NOT AMOUNTING TO MURDER": "homicide",
    "ATTEMPT TO MURDER": "attempt-murder",
    "RAPE": "sexual-offence",
    "CUSTODIAL RAPE": None,                                   # subset of RAPE
    "OTHER RAPE": None,                                       # subset of RAPE
    "KIDNAPPING & ABDUCTION": "kidnapping",
    "KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS": None,      # subset
    "KIDNAPPING AND ABDUCTION OF OTHERS": None,               # subset
    "DACOITY": "dacoity",
    "PREPARATION AND ASSEMBLY FOR DACOITY": "dacoity",
    "ROBBERY": "robbery",
    "BURGLARY": "burglary",
    "THEFT": "theft",
    "AUTO THEFT": None,                                       # subset of THEFT
    "OTHER THEFT": None,                                      # subset of THEFT
    "RIOTS": "rioting",
    "CRIMINAL BREACH OF TRUST": "cheating",
    "CHEATING": "cheating",
    "COUNTERFIETING": "other",                                # NCRB's own spelling
    "ARSON": "other",
    "HURT/GREVIOUS HURT": "grievous-hurt",
    "DOWRY DEATHS": "dowry-death",
    "ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY": "sexual-offence",
    "INSULT TO MODESTY OF WOMEN": "sexual-offence",
    "CRUELTY BY HUSBAND OR HIS RELATIVES": "domestic-cruelty",
    "IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES": "other",
    "CAUSING DEATH BY NEGLIGENCE": "negligent-death",
    "OTHER IPC CRIMES": "other",
    "TOTAL IPC CRIMES": None,                                 # row total
}


def _norm_header(value: str | None) -> str:
    """Fold a column header so 2014's title case matches the earlier years."""
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


# Headers that changed wording between editions, normalised form -> our column.
HEADER_ALIASES = {
    "STATESUTS": "STATE/UT",
    "ATTEMPTTOCOMMITMURDER": "ATTEMPT TO MURDER",
    "KIDNAPPINGABDUCTION": "KIDNAPPING & ABDUCTION",
    "COUNTERFEITING": "COUNTERFIETING",
    "HURTGREVIOUSHURT": "HURT/GREVIOUS HURT",
    "HURTGRIEVOUSHURT": "HURT/GREVIOUS HURT",
    "DOWRYDEATH": "DOWRY DEATHS",
}

_CANONICAL = {_norm_header(c): c for c in COLUMN_TO_KEY}
_CANONICAL.update({_norm_header(k): k for k in ("STATE/UT", "DISTRICT", "YEAR")})


def canonical_row(row: dict) -> dict:
    """Re-key a row onto the 2001-2013 header names."""
    out = {}
    for header, value in row.items():
        normalised = _norm_header(header)
        canonical = HEADER_ALIASES.get(normalised) or _CANONICAL.get(normalised)
        out[canonical or (header or "")] = value
    return out


def load_crosswalk() -> dict[str, str]:
    """NCRB district label -> spine district name. Non-districts map to ''."""
    path = REFERENCE / "bihar_ncrb_district_crosswalk.csv"
    mapping = {}
    with path.open(encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            mapping[row["ncrb_ogd_label"].strip().upper()] = row["spine_district"].strip().upper()
    return mapping


def ingest() -> tuple[list[dict], dict]:
    crosswalk = load_crosswalk()
    counts: dict[tuple[str, int, str], int] = defaultdict(int)
    unmapped: set[str] = set()
    skipped_aggregate = 0
    rows_read = 0

    for name in IPC_FILES:
        path = RAW / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig") as handle:
            for raw in csv.DictReader(handle):
                row = canonical_row(raw)
                if (row.get("STATE/UT") or "").strip().upper() != STATE:
                    continue
                rows_read += 1
                label = (row.get("DISTRICT") or "").strip().upper()
                district = crosswalk.get(label)
                if district is None:
                    unmapped.add(label)
                    continue
                if not district:
                    # TOTAL rows and non-geographies (ATS, EOU): real records,
                    # but not places, so they are dropped deliberately.
                    skipped_aggregate += 1
                    continue
                try:
                    year = int((row.get("YEAR") or "").strip())
                except ValueError:
                    continue
                for column, key in COLUMN_TO_KEY.items():
                    if key is None or column not in row:
                        continue
                    value = (row.get(column) or "").strip()
                    if value.isdigit():
                        counts[(district, year, key)] += int(value)

    cells = [{"district": d, "year": y, "crime_key": k, "count": n}
             for (d, y, k), n in sorted(counts.items())]
    diagnostics = {
        "rows_read": rows_read,
        "aggregate_rows_dropped": skipped_aggregate,
        "unmapped_district_labels": sorted(unmapped),
        "districts": len({c["district"] for c in cells}),
        "years": sorted({c["year"] for c in cells}),
        "cells": len(cells),
        "total_offences": sum(c["count"] for c in cells),
    }
    return cells, diagnostics


def main() -> int:
    cells, diagnostics = ingest()
    SPINE.mkdir(parents=True, exist_ok=True)
    (SPINE / "ncrb_district_counts.json").write_text(
        json.dumps({"state": STATE, "unit": "district", "source":
                    "NCRB Crime in India district tables via data.gov.in (GODL-India)",
                    "diagnostics": diagnostics, "cells": cells},
                   separators=(",", ":")), encoding="utf-8")
    for key, value in diagnostics.items():
        print(f"{key:28s} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
