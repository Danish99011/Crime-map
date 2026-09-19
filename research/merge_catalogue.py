#!/usr/bin/env python3
"""Merge per-domain source dossiers into one validated catalogue.

Each research agent writes research/sources/<domain>.jsonl, one JSON object per
line, following the schema in research/_SPEC.md. This script validates those
objects, reports what is wrong with them, and emits:

    research/catalogue.json   every valid entry, sorted by priority
    research/catalogue.csv    flat view for spreadsheets
    research/CATALOGUE.md     the human-facing index

Run:  python3 research/merge_catalogue.py [--strict]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"

REQUIRED = [
    "id", "name", "publisher", "domain", "tier", "urls", "geo_coverage",
    "geo_granularity", "unit_of_record", "cadence", "formats", "access",
    "machine_readable", "license", "ingest_difficulty", "priority",
    "verification", "checked_on",
]

# Ordered coarse -> fine. Agents found two levels the first draft of this enum
# missed: `subdistrict` (the tehsil/taluk, India's real intermediate unit) and
# `village` (LGD village codes, and the areas notified under the SC/ST Act).
GRANULARITY = [
    "national", "state", "district", "city", "subdistrict", "police-district",
    "police-station", "ward", "village", "beat", "grid", "point", "address",
]
# A lower index means less useful for a street-level map.
GRANULARITY_RANK = {g: i for i, g in enumerate(GRANULARITY)}

VERIFICATION = ["VERIFIED_LIVE", "VERIFIED_LANDING", "CITED", "UNVERIFIED"]
ACCESS = [
    "open-download", "api-key", "scrape", "captcha", "login", "rti-only",
    "paid", "on-request", "blocked",
]
CADENCE = [
    "annual", "quarterly", "monthly", "weekly", "daily", "realtime",
    "irregular", "one-off",
]

LOCATION_SEMANTICS = [
    "offence-location", "victim-residence", "offender-residence",
    "reporting-office", "service-point", "interdiction-point", "court-venue",
    "jurisdiction-aggregate", "unknown",
    # Boundary files, statutes, tooling and methodology references carry no
    # crime geography of their own.
    "n/a",
]


def validate(entry: dict, origin: str) -> list[str]:
    """Return a list of human-readable problems with one entry."""
    problems = []
    for field in REQUIRED:
        if field == "urls":
            continue  # shape is checked below; an empty object is legitimate
        if field not in entry or entry[field] in (None, "", []):
            problems.append(f"missing required field {field!r}")

    def check_enum(field, allowed):
        value = entry.get(field)
        if value and value not in allowed:
            problems.append(f"{field}={value!r} not in {allowed}")

    check_enum("geo_granularity", GRANULARITY)
    check_enum("verification", VERIFICATION)
    check_enum("access", ACCESS)
    check_enum("cadence", CADENCE)
    check_enum("location_semantics", LOCATION_SEMANTICS)

    for field, lo, hi in (
        ("tier", 1, 5),
        ("machine_readable", 0, 5),
        ("ingest_difficulty", 1, 5),
        ("priority", 1, 5),
    ):
        value = entry.get(field)
        if isinstance(value, int) and not lo <= value <= hi:
            problems.append(f"{field}={value} outside {lo}-{hi}")
        elif value is not None and not isinstance(value, int):
            problems.append(f"{field} must be an int, got {type(value).__name__}")

    if not isinstance(entry.get("urls"), dict):
        problems.append("urls must be an object")

    # An entry we cannot simply download needs to say how to get at it.
    # Self-service API registration is the one exception: the instruction is
    # "sign up on the portal", which carries no information worth storing.
    if entry.get("access") not in ("open-download", "api-key", None) and not entry.get("how_to_obtain"):
        problems.append(f"access={entry.get('access')!r} requires how_to_obtain")

    # An unverified claim without evidence is just a rumour; make it visible.
    if entry.get("verification") in ("VERIFIED_LIVE", "VERIFIED_LANDING") and not entry.get("evidence"):
        problems.append("claims verification but carries no evidence")

    return [f"{origin}: {p}" for p in problems]


def load() -> tuple[list[dict], list[str]]:
    entries, problems = [], []
    seen_ids: dict[str, str] = {}

    for path in sorted(SOURCES.glob("*.jsonl")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            origin = f"{path.name}:{lineno}"
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append(f"{origin}: unparseable JSON — {exc}")
                continue
            if not isinstance(entry, dict):
                problems.append(f"{origin}: expected an object, got {type(entry).__name__}")
                continue

            entry.setdefault("domain", path.stem)
            problems.extend(validate(entry, origin))

            entry_id = entry.get("id")
            if entry_id:
                if entry_id in seen_ids:
                    problems.append(f"{origin}: duplicate id {entry_id!r}, first seen at {seen_ids[entry_id]}")
                else:
                    seen_ids[entry_id] = origin
            entries.append(entry)

    return entries, problems


def sort_key(entry: dict):
    """Best first: high priority, fine granularity, easy to ingest, verified."""
    return (
        -(entry.get("priority") or 0),
        -GRANULARITY_RANK.get(entry.get("geo_granularity", ""), -1),
        entry.get("ingest_difficulty") or 9,
        VERIFICATION.index(entry["verification"]) if entry.get("verification") in VERIFICATION else 9,
        entry.get("name", ""),
    )


def first_url(entry: dict) -> str:
    urls = entry.get("urls")
    if not isinstance(urls, dict):
        return ""
    for key in ("data", "api", "landing", "docs"):
        if urls.get(key):
            return urls[key]
    return next((v for v in urls.values() if v), "")


def write_outputs(entries: list[dict]) -> None:
    entries.sort(key=sort_key)
    (ROOT / "catalogue.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    columns = [
        "id", "name", "publisher", "domain", "tier", "geo_coverage",
        "geo_granularity", "unit_of_record", "time_start", "time_latest",
        "cadence", "lag", "taxonomy", "access", "machine_readable", "license",
        "ingest_difficulty", "priority", "verification", "checked_on", "url",
    ]
    with (ROOT / "catalogue.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for entry in entries:
            row = dict(entry, url=first_url(entry))
            row["formats"] = ",".join(entry.get("formats") or [])
            writer.writerow(row)

    by_domain = defaultdict(list)
    for entry in entries:
        by_domain[entry.get("domain", "?")].append(entry)

    lines = [
        "# Master Source Catalogue",
        "",
        "Generated by `research/merge_catalogue.py` — do not edit by hand.",
        "Edit the per-domain `.jsonl` files in `research/sources/` and re-run the script.",
        "",
        f"**{len(entries)} sources** across **{len(by_domain)} domains**.",
        "",
        "## Coverage",
        "",
        "| dimension | breakdown |",
        "|---|---|",
    ]
    for label, key in (
        ("Granularity", "geo_granularity"),
        ("Access", "access"),
        ("Verification", "verification"),
        ("Cadence", "cadence"),
        ("Tier", "tier"),
    ):
        counts = Counter(str(e.get(key)) for e in entries)
        summary = " · ".join(f"{k} ({v})" for k, v in counts.most_common())
        lines.append(f"| {label} | {summary} |")

    lines += ["", "## Highest priority sources", "",
              "| pri | source | granularity | cadence | access | verified | link |",
              "|---|---|---|---|---|---|---|"]
    for entry in entries[:40]:
        url = first_url(entry)
        link = f"[link]({url})" if url else "—"
        lines.append(
            f"| {entry.get('priority')} | {entry.get('name')} | {entry.get('geo_granularity')} "
            f"| {entry.get('cadence')} | {entry.get('access')} | {entry.get('verification')} | {link} |"
        )

    lines += ["", "## By domain", ""]
    for domain in sorted(by_domain):
        group = by_domain[domain]
        finest = max(
            (e.get("geo_granularity") for e in group if e.get("geo_granularity") in GRANULARITY_RANK),
            key=lambda g: GRANULARITY_RANK[g],
            default="—",
        )
        lines.append(f"### [{domain}](sources/{domain}.md) — {len(group)} sources, finest: `{finest}`")
        lines.append("")
        for entry in sorted(group, key=sort_key):
            url = first_url(entry)
            name = f"[{entry.get('name')}]({url})" if url else entry.get("name", "?")
            lines.append(
                f"- **P{entry.get('priority')}** {name} — `{entry.get('geo_granularity')}`, "
                f"{entry.get('cadence')}, {entry.get('access')} ({entry.get('verification')})"
            )
        lines.append("")

    (ROOT / "CATALOGUE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="exit non-zero if any entry has problems")
    args = parser.parse_args()

    entries, problems = load()
    if not entries:
        print("No entries found in research/sources/*.jsonl", file=sys.stderr)
        return 1

    write_outputs(entries)

    print(f"Merged {len(entries)} entries into catalogue.json / catalogue.csv / CATALOGUE.md")

    missing_semantics = [e for e in entries if not e.get("location_semantics")]
    if missing_semantics:
        by_domain = Counter(e.get("domain", "?") for e in missing_semantics)
        print(f"\n{len(missing_semantics)} entries still need location_semantics backfilled:")
        for domain, count in by_domain.most_common():
            print(f"  {count:4d}  {domain}")
    if problems:
        print(f"\n{len(problems)} schema problems:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
