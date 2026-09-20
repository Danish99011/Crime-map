"""Resolve a police station name to a thana jurisdiction.

The crime feed we will ingest identifies a station by **name and district**, not
by any code. Nothing in Indian crime data carries a stable station identifier
across systems. So this resolver is the join the entire map depends on, and its
failure mode is the worst one available to us: a wrong match does not look like
an error, it looks like crime in the wrong neighbourhood.

Two rules follow from that, and both are enforced here rather than left to the
caller's discipline:

1. **District first, always.** A station name is only ever matched against
   thanas in the same district. Bihar has multiple stations called SADAR,
   MUFASSIL and NAGAR; matching those state-wide would scatter their crime
   across the map. A name that cannot be placed in a known district is
   unresolved, not guessed.
2. **Ambiguity is an outcome, not a tie to break.** When two thanas in a
   district score near-identically, the resolver returns `ambiguous` with both
   candidates rather than picking one. Those go to a review queue; they do not
   go on the map.

Accuracy is not asserted here. `pipeline/crosswalk.py` grades every station by
how much independent evidence supports its mapping.

**Aliases close the loop.** Names the resolver cannot place go to
`data/spine/review_queue.csv`. A human who confirms one records it in
`data/spine/station_aliases.csv`, which this resolver consults before any
fuzzy matching. That file is the only place a human judgement is allowed to
override the algorithm, which makes it the only place to look when a mapping is
disputed.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .geography import canonical_district, normalise_name, unit_type

SPINE = Path(__file__).resolve().parent.parent / "data" / "spine"
ALIAS_FILE = SPINE / "station_aliases.csv"

# A match at or above this score is accepted; below it the name is unresolved.
ACCEPT = 0.86
# If the runner-up is within this of the winner, the result is ambiguous.
AMBIGUITY_MARGIN = 0.04


@dataclass(frozen=True)
class Resolution:
    thana_id: str | None
    confidence: float
    method: str
    candidates: tuple[tuple[str, float], ...] = ()

    @property
    def ok(self) -> bool:
        return self.thana_id is not None


class ThanaResolver:
    """Name+district -> thana_id, with explicit uncertainty."""

    def __init__(self, thanas: list[dict], aliases: dict[tuple[str, str], str] | None = None):
        # (district, normalised name) -> thana_id, curated by hand from the
        # review queue. Checked before anything is computed.
        self._aliases = aliases or {}
        self._by_district: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        self._exact: dict[tuple[str, str], list[str]] = defaultdict(list)
        self._unit_type: dict[str, str] = {}
        for thana in thanas:
            self._unit_type[thana["thana_id"]] = unit_type(thana["name"])
            district = canonical_district(thana["district"])
            key = normalise_name(thana["name"])
            self._by_district[district].append((thana["thana_id"], thana["name"], key))
            self._exact[(district, key)].append(thana["thana_id"])
        self.districts = set(self._by_district)

    @classmethod
    def from_spine(cls, path: Path | None = None, alias_path: Path | None = None,
                   human_aliases_only: bool = False) -> "ThanaResolver":
        """Build a resolver from the spine.

        `human_aliases_only` exists for pipeline.crosswalk, which *derives* the
        rule-made aliases. If it resolved through them it would be reading back
        its own previous conclusions, and its grades would depend on how many
        times it had been run. Human entries are input and always apply; rule
        entries are output and are excluded from the run that produces them.
        """
        path = path or (SPINE / "bihar_thana.geojson")
        collection = json.loads(path.read_text(encoding="utf-8"))
        return cls([f["properties"] for f in collection["features"]],
                   aliases=load_aliases(alias_path, human_only=human_aliases_only))

    def resolve(self, name: str, district: str) -> Resolution:
        canonical = canonical_district(district)
        if canonical not in self._by_district:
            return Resolution(None, 0.0, "unknown-district")

        key = normalise_name(name)
        if not key:
            return Resolution(None, 0.0, "empty-name")

        alias = self._aliases.get((canonical, key))
        if alias:
            return Resolution(alias, 1.0, "alias")

        exact = self._exact.get((canonical, key), [])
        if len(exact) == 1:
            return Resolution(exact[0], 1.0, "exact")
        if len(exact) > 1:
            # Two thanas in one district normalise to the same name. Before
            # giving up, try the one distinction the fold threw away: a thana
            # and its outpost can share a name, and the query says which it is.
            wanted = unit_type(name)
            same_type = [t for t in exact if self._unit_type.get(t) == wanted]
            if len(same_type) == 1:
                return Resolution(same_type[0], 1.0, "exact-unit-type")
            # Otherwise picking either would be a coin flip dressed up as a match.
            return Resolution(None, 1.0, "ambiguous-exact",
                              tuple((t, 1.0) for t in exact))

        scored = sorted(
            ((thana_id, SequenceMatcher(None, key, candidate_key).ratio())
             for thana_id, _, candidate_key in self._by_district[canonical]),
            key=lambda pair: pair[1],
            reverse=True,
        )
        if not scored:
            return Resolution(None, 0.0, "empty-district")

        best_id, best_score = scored[0]
        if best_score < ACCEPT:
            return Resolution(None, round(best_score, 3), "below-threshold",
                              tuple((t, round(s, 3)) for t, s in scored[:3]))

        runner_up = scored[1][1] if len(scored) > 1 else 0.0
        if best_score - runner_up < AMBIGUITY_MARGIN:
            return Resolution(None, round(best_score, 3), "ambiguous-fuzzy",
                              tuple((t, round(s, 3)) for t, s in scored[:3]))

        return Resolution(best_id, round(best_score, 3), "fuzzy",
                          tuple((t, round(s, 3)) for t, s in scored[:3]))


def load_aliases(path: Path | None = None,
                 human_only: bool = False) -> dict[tuple[str, str], str]:
    """Load station-name to thana mappings.

    Columns: district, station_name, thana_id, confirmed_by, note.
    Rows without a thana_id are pending review and are ignored. A
    `confirmed_by` of `rule:<tier>` marks a mapping derived by
    pipeline.crosswalk; `human_only` excludes those.
    """
    import csv

    path = path or ALIAS_FILE
    if not path.exists():
        return {}
    aliases = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            thana_id = (row.get("thana_id") or "").strip()
            if not thana_id:
                continue
            if human_only and (row.get("confirmed_by") or "").startswith("rule:"):
                continue
            key = (canonical_district(row.get("district")),
                   normalise_name(row.get("station_name")))
            if key[1]:
                aliases[key] = thana_id
    return aliases
