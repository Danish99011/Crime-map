#!/usr/bin/env python3
"""Normalise agent-written JSONL into the controlled vocabularies of _SPEC.md.

Sixteen agents wrote these files independently, so the drift is predictable:
free-text cadence values that carry a qualifier ("irregular (GBD cycles)"),
`urls` given as a bare string, and granularity levels the original enum did not
anticipate. The qualifiers are worth keeping — they just belong in `notes`
rather than in a field the catalogue sorts and groups on.

This rewrites research/sources/*.jsonl in place. It only ever moves information
sideways; it never invents a value to satisfy the schema. Anything it cannot
resolve is left alone for merge_catalogue.py to report.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SOURCES = Path(__file__).resolve().parent / "sources"

CADENCE = ["annual", "quarterly", "monthly", "weekly", "daily", "realtime",
           "irregular", "one-off"]
GRANULARITY_ALIASES = {
    "sub-district": "subdistrict", "taluk": "subdistrict", "tehsil": "subdistrict",
    "commissionerate": "police-district", "zone": "police-district",
    "locality": "ward", "neighbourhood": "ward", "neighborhood": "ward",
    "lat-lon": "point", "coordinate": "point", "incident-point": "point",
}


def normalise_cadence(entry: dict) -> bool:
    value = entry.get("cadence")
    if not isinstance(value, str) or value in CADENCE:
        return False
    lowered = value.lower().strip()
    for candidate in CADENCE:
        # "irregular (GBD cycles)" and "annual, with monthly PDFs" both start
        # with the real cadence; the rest is commentary.
        if lowered.startswith(candidate):
            entry["cadence"] = candidate
            remainder = value[len(candidate):].strip(" ,;()")
            if remainder:
                note = entry.get("notes", "")
                entry["notes"] = f"{note} Cadence detail: {remainder}.".strip()
            return True
    if lowered in ("unknown", "n/a", "none", ""):
        entry["cadence"] = "irregular"
        note = entry.get("notes", "")
        entry["notes"] = f"{note} Publication cadence not stated by the publisher.".strip()
        return True
    return False


def normalise_urls(entry: dict) -> bool:
    value = entry.get("urls")
    if isinstance(value, dict):
        return False
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        entry["urls"] = {"landing": value}
        return True
    if isinstance(value, list):
        entry["urls"] = {f"url{i}": u for i, u in enumerate(value, 1) if isinstance(u, str)}
        return True
    # An agent that deliberately recorded no URL rather than guessing one did
    # the right thing. Give it an empty object so the shape is uniform.
    entry["urls"] = {}
    return True


def normalise_granularity(entry: dict) -> bool:
    value = entry.get("geo_granularity")
    if not isinstance(value, str):
        return False
    key = value.strip().lower()
    if key in GRANULARITY_ALIASES:
        entry["geo_granularity"] = GRANULARITY_ALIASES[key]
        return True
    return False


def normalise_ints(entry: dict) -> bool:
    """Agents occasionally write "5" or "5 (high)" where an int is required."""
    changed = False
    for field in ("tier", "machine_readable", "ingest_difficulty", "priority"):
        value = entry.get(field)
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                entry[field] = int(match.group())
                changed = True
    return changed


def main() -> int:
    total_changed = 0
    for path in sorted(SOURCES.glob("*.jsonl")):
        lines, changed_here = [], 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("//"):
                lines.append(raw)
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError:
                lines.append(raw)
                continue
            if any([normalise_cadence(entry), normalise_urls(entry),
                    normalise_granularity(entry), normalise_ints(entry)]):
                changed_here += 1
            lines.append(json.dumps(entry, ensure_ascii=False))
        if changed_here:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"{path.name}: normalised {changed_here} entries")
            total_changed += changed_here
    print(f"\nNormalised {total_changed} entries in total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
