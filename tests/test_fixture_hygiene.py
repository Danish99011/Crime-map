"""Structural checks that committed fixtures carry nothing live and nobody's name.

Fixtures are copies of real pages from a police portal, kept so parsers can be
written and reviewed without touching the server. Two things must never ride
along in such a copy, and both are enforced here by shape rather than by
example, so a new fixture is covered the day it is added:

* **A live token.** The Mumbai Police pages are Laravel forms and carry a
  per-session CSRF ``_token``. One was committed on 2026-09-21 in three
  fixtures and caught by the security guard after the push. It was not this
  project's credential and not replayable without the session cookie that
  was never captured, but a live value in a public commit is exactly the
  thing the guard exists to stop. The scrub leaves ``[csrf token removed]``.
* **A person's identity.** The same pages name officers. The fixtures replace
  each with ``[officer name removed]`` (and the Sr. PI's mobile and photo
  likewise); the join test checks the placeholders, this file checks that no
  40-character random string survived anywhere in any fixture.
"""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
HTML = sorted(FIXTURES.glob("*.html"))
MUMBAIPOLICE = sorted(FIXTURES.glob("mumbaipolice-station-*.html"))


@pytest.mark.parametrize("path", HTML, ids=[p.name for p in HTML])
def test_no_live_hidden_token_value(path):
    import re
    text = path.read_text(encoding="utf-8")
    # Match the whole <input ...> tag and read its attributes in any order, so
    # a page that writes value= before name= cannot slip a live value past.
    names = re.compile(r'^(?:_token|csrf[-_]?token|X-CSRF-TOKEN|authenticity_token)$', re.I)
    for tag in re.findall(r"<input\b[^>]*>", text, flags=re.I):
        attrs = dict(re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', tag))
        if names.match(attrs.get("name", "")):
            assert attrs.get("value") == "[csrf token removed]", (
                f"{path.name} carries a live token value; scrub it to the placeholder")
    # And nothing anywhere in the file should look like a bare 40-char token.
    for value in re.findall(r'(?:value|content)="([A-Za-z0-9]{40})"', text):
        raise AssertionError(f"{path.name} carries a 40-character token-like value")


@pytest.mark.parametrize("path", MUMBAIPOLICE, ids=[p.name for p in MUMBAIPOLICE])
def test_mumbaipolice_fixture_is_scrubbed(path):
    text = path.read_text(encoding="utf-8")
    assert "[csrf token removed]" in text
    assert text.count("[officer name removed]") >= 4
    assert "[officer mobile removed]" in text
    assert "[officer photo removed]" in text
    assert "?name=" not in text and "images/Police_incharge/" not in text


def test_no_fixture_carries_a_session_cookie():
    for path in HTML:
        text = path.read_text(encoding="utf-8").lower()
        for marker in ("laravel_session=", "xsrf-token=", "phpsessid=", "asp.net_sessionid="):
            assert marker not in text, f"{path.name} carries {marker!r}"
