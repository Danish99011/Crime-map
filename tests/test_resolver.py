"""Tests for the name->thana join the crime feed depends on.

These use a small hand-built spine rather than the real one so the expected
answers are obvious by inspection.
"""

import pytest

from pipeline.resolver import ThanaResolver


def thana(thana_id, name, district):
    return {"thana_id": thana_id, "name": name, "district": district}


@pytest.fixture
def resolver():
    return ThanaResolver([
        thana("T-1", "ARARIA", "ARARIA"),
        thana("T-2", "BATHNAHA", "ARARIA"),
        thana("T-3", "NARPATAGANJ", "ARARIA"),
        thana("T-4", "SADAR", "PATNA"),
        thana("T-5", "MUFASSIL", "PATNA"),
        thana("T-6", "SADAR", "GAYA"),
    ])


class TestResolve:
    def test_exact_match_within_district(self, resolver):
        result = resolver.resolve("ARARIA", "ARARIA")
        assert (result.thana_id, result.method, result.confidence) == ("T-1", "exact", 1.0)

    def test_transliteration_variant_still_exact(self, resolver):
        assert resolver.resolve("NARPATGANJ", "ARARIA").thana_id == "T-3"

    def test_district_scopes_the_match(self, resolver):
        # SADAR exists in both PATNA and GAYA. Each must stay in its own
        # district; matching state-wide would scatter crime across the map.
        assert resolver.resolve("SADAR", "PATNA").thana_id == "T-4"
        assert resolver.resolve("SADAR", "GAYA").thana_id == "T-6"

    def test_unknown_district_is_refused_not_guessed(self, resolver):
        result = resolver.resolve("ARARIA", "NOWHERE")
        assert result.thana_id is None
        assert result.method == "unknown-district"

    def test_unknown_name_is_refused(self, resolver):
        result = resolver.resolve("COMPLETELYUNRELATED", "PATNA")
        assert result.thana_id is None
        assert result.method == "below-threshold"
        assert result.candidates, "a refusal should still show what it considered"

    def test_empty_name_never_matches(self, resolver):
        assert resolver.resolve("", "PATNA").thana_id is None
        assert resolver.resolve("   ", "PATNA").method == "empty-name"


class TestAmbiguity:
    def test_duplicate_names_in_one_district_are_ambiguous(self):
        # Two thanas normalising to the same name inside one district cannot be
        # told apart. Picking one would be a coin flip presented as a fact.
        resolver = ThanaResolver([
            thana("T-1", "MEHANDIA", "ARWAL"),
            thana("T-2", "MEHANDIYA", "ARWAL"),
        ])
        result = resolver.resolve("MEHANDIA", "ARWAL")
        assert result.thana_id is None
        assert result.method == "ambiguous-exact"
        assert {c[0] for c in result.candidates} == {"T-1", "T-2"}

    def test_near_tie_is_ambiguous_rather_than_a_coin_flip(self):
        resolver = ThanaResolver([
            thana("T-1", "RAMPUR EAST", "PATNA"),
            thana("T-2", "RAMPUR WEST", "PATNA"),
        ])
        result = resolver.resolve("RAMPUR", "PATNA")
        assert result.thana_id is None
        assert result.method in ("ambiguous-fuzzy", "below-threshold")


class TestLayering:
    """Spelling variation is handled by the matcher, not by name folding.

    `normalise_name` deliberately does not fold an inserted schwa
    (NARPATGANJ / NARPATAGANJ) because doing so would require dropping vowels,
    which would collide genuinely different neighbouring thanas. The fuzzy
    matcher absorbs it instead, and this test pins that end-to-end behaviour so
    a future tightening of the threshold cannot silently break it.
    """

    def test_inserted_schwa_resolves_via_fuzzy(self, resolver):
        result = resolver.resolve("NARPATGANJ", "ARARIA")
        assert result.thana_id == "T-3"
        assert result.method == "fuzzy"
        assert result.confidence >= 0.9

    def test_district_convention_resolves_via_the_alias_table(self):
        # PURNEA/PURNIA and MOTHIHARI/EAST CHAMPARAN are conventions, not
        # spellings, so they are resolved before the resolver ever sees them.
        from pipeline.geography import canonical_district

        assert canonical_district("PURNEA") == canonical_district("PURNIA")
        assert canonical_district("MOTHIHARI") == "EAST CHAMPARAN"


class TestAliases:
    def test_alias_overrides_the_algorithm(self):
        resolver = ThanaResolver(
            [thana("T-1", "ARARIA", "ARARIA"), thana("T-2", "BATHNAHA", "ARARIA")],
            aliases={("ARARIA", "JOGBANI"): "T-2"},
        )
        result = resolver.resolve("JOGBANI", "ARARIA")
        assert (result.thana_id, result.method) == ("T-2", "alias")

    def test_alias_respects_district_scope(self):
        resolver = ThanaResolver(
            [thana("T-1", "ARARIA", "ARARIA")],
            aliases={("ARARIA", "JOGBANI"): "T-1"},
        )
        # The same station name in a different district must not pick up the alias.
        assert resolver.resolve("JOGBANI", "PATNA").method == "unknown-district"
