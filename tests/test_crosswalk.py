"""Tests for the rules that decide where a station maps.

Each rule exists because one of the two witnesses lies in a characteristic way.
These pin the rules to the evidence that justified them, so that changing a
threshold has to be a deliberate act with a failing test attached.
"""

import csv

import pytest

from pipeline.crosswalk import (
    CONFIRMED,
    CORROBORATED,
    NAME_ONLY,
    NAME_OVER_GEOMETRY,
    NEEDS_REVIEW,
    grade,
    write_aliases,
)
from pipeline.geography import normalise_name
from pipeline.resolver import ThanaResolver

THANAS = {
    "T-1": {"thana_id": "T-1", "name": "BALIA", "district": "BEGUSARAI"},
    "T-2": {"thana_id": "T-2", "name": "MUFASSIL", "district": "BEGUSARAI"},
    "T-3": {"thana_id": "T-3", "name": "DEOKUND", "district": "AURANGABAD"},
    "T-4": {"thana_id": "T-4", "name": "MADANPUR", "district": "AURANGABAD"},
}


@pytest.fixture
def resolver():
    return ThanaResolver(list(THANAS.values()))


def station(name, district, thana_id=""):
    return {"name": name, "district": district, "thana_id": thana_id, "ps_cd_mha": "1"}


class TestRules:
    def test_agreement_is_confirmed(self, resolver):
        row = grade(station("BALIA", "BEGUSARAI", "T-1"), THANAS, resolver)
        assert row["tier"] == CONFIRMED
        assert row["thana_id"] == "T-1"

    def test_strong_name_beats_a_disagreeing_point(self, resolver):
        # The real case: Balia's station point falls inside Mufassil's polygon.
        # The coordinate is wrong; Balia is not Mufassil.
        row = grade(station("BALIA", "BEGUSARAI", "T-2"), THANAS, resolver)
        assert row["tier"] == NAME_OVER_GEOMETRY
        assert row["thana_id"] == "T-1"
        assert "unreliable witness" in row["rule"]

    def test_weak_name_plus_agreeing_geometry_is_accepted(self, resolver):
        # DEVKUND/DEOKUND is a transliteration variant that scores below the
        # resolver's standalone threshold. The point falling inside it is the
        # second signal that makes it safe to accept.
        row = grade(station("DEVKUND", "AURANGABAD", "T-3"), THANAS, resolver)
        assert row["tier"] == CORROBORATED
        assert row["thana_id"] == "T-3"

    def test_weak_name_and_unrelated_geometry_goes_to_review(self, resolver):
        # "Azan" landing inside Madanpur tells us where the building is, not
        # that Azan's jurisdiction is Madanpur's.
        row = grade(station("Azan", "AURANGABAD", "T-4"), THANAS, resolver)
        assert row["tier"] == NEEDS_REVIEW
        assert row["thana_id"] == ""
        assert row["proposal"] == "T-4", "review rows still carry a proposal to judge"

    def test_name_alone_is_accepted_when_there_is_no_point(self, resolver):
        row = grade(station("BALIA", "BEGUSARAI", ""), THANAS, resolver)
        assert row["tier"] == NAME_ONLY
        assert row["thana_id"] == "T-1"

    def test_nothing_at_all_goes_to_review(self, resolver):
        row = grade(station("UNRELATED PLACE", "BEGUSARAI", ""), THANAS, resolver)
        assert row["tier"] == NEEDS_REVIEW
        assert row["thana_id"] == ""


class TestAliasFile:
    def test_a_hand_confirmed_alias_survives_a_rebuild(self, tmp_path, monkeypatch):
        """The alias file is rewritten on every run. A human judgement recorded
        there must never be silently replaced by a rule's opinion."""
        from pipeline import crosswalk

        monkeypatch.setattr(crosswalk, "SPINE", tmp_path)
        path = tmp_path / "station_aliases.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["district", "station_name", "thana_id",
                                    "confirmed_by", "note"])
            writer.writeheader()
            writer.writerow({"district": "BEGUSARAI", "station_name": "BALIA",
                             "thana_id": "T-99", "confirmed_by": "a.person",
                             "note": "checked against the gazette"})

        write_aliases([{
            "district": "BEGUSARAI", "station_name": "BALIA", "thana_id": "T-1",
            "tier": NAME_OVER_GEOMETRY, "rule": "a rule would say T-1",
        }])

        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        human = [r for r in rows if r["confirmed_by"] == "a.person"]
        assert len(human) == 1
        assert human[0]["thana_id"] == "T-99", "the human's answer must win"
        assert not [r for r in rows if r["confirmed_by"].startswith("rule:")], \
            "a rule must not re-add a station a human has already ruled on"

    def test_rule_accepted_rows_are_labelled_with_their_rule(self, tmp_path, monkeypatch):
        from pipeline import crosswalk

        monkeypatch.setattr(crosswalk, "SPINE", tmp_path)
        write_aliases([{
            "district": "AURANGABAD", "station_name": "DEVKUND", "thana_id": "T-3",
            "tier": CORROBORATED, "rule": "below threshold but the point falls inside",
        }])
        rows = list(csv.DictReader((tmp_path / "station_aliases.csv").open(encoding="utf-8")))
        assert rows[0]["confirmed_by"] == f"rule:{CORROBORATED}"
        assert rows[0]["note"]


class TestIdempotence:
    """The crosswalk writes aliases that the resolver reads. If it also graded
    through them it would be reading back its own conclusions, and the tiers
    would shift every run — which they did, oscillating 546/53 against 599/0.
    """

    def test_rule_aliases_are_excluded_from_a_human_only_load(self, tmp_path):
        from pipeline.resolver import load_aliases

        path = tmp_path / "aliases.csv"
        path.write_text(
            "district,station_name,thana_id,confirmed_by,note\n"
            "PATNA,DEVKUND,T-1,rule:corroborated,derived\n"
            "PATNA,BAKHRI,T-2,a.person,checked by hand\n"
            "PATNA,JAMHAUR,,a.person,pending — no thana_id yet\n",
            encoding="utf-8")

        everything = load_aliases(path)
        human = load_aliases(path, human_only=True)

        # Keys are normalised names, not raw ones.
        assert len(everything) == 2, "rows without a thana_id are pending, not aliases"
        assert len(human) == 1
        assert human == {("PATNA", normalise_name("BAKHRI")): "T-2"}
        assert ("PATNA", normalise_name("DEVKUND")) not in human, \
            "a derived alias must not feed the run that derives it"
