"""Where FIR records come from.

Two adapters, and an important asymmetry between them.

`CsvFirSource` works today and is fully tested. It reads a FIR extract that
somebody has already obtained — an RTI response, a portal export, a manual
download — and is the route by which real Bihar data will most likely first
enter this pipeline.

`BiharScrbSource` targets `scrb.bihar.gov.in/View_FIR.aspx`, Bihar's public
all-FIR repository, uploaded under Supreme Court and High Court direction. **It
has never been run against the live site.** The host is unreachable from the
environment this was written in, so its form controls and result-table shape are
unknown. What is implemented here is the part that is knowable without seeing
the page: the ASP.NET WebForms session dance, which works by echoing back
whatever hidden state the form gives you rather than by knowing its field names
in advance. `probe()` reports what the live form actually contains so an
operator in India can fill in the rest in one sitting.

Nothing here guesses a field name. A scraper that quietly posts invented
parameters and gets an empty table back is worse than one that refuses to run.

**Before running this against any portal, read `docs/INGESTION.md`.** Two things
are settled there and not negotiable in code: we do not defeat CAPTCHAs, and we
do not ingest a source whose terms of use forbid it.
"""

from __future__ import annotations

import csv
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from .fir import FirRecord, audit_columns


class FirSource(Protocol):
    """Anything that can yield FIR records."""

    name: str

    def fetch(self) -> Iterator[FirRecord]:
        ...


# --------------------------------------------------------------------------
# CSV / export files
# --------------------------------------------------------------------------

@dataclass
class CsvFirSource:
    """Read FIRs from a delimited export.

    `mapping` names which of the file's columns carry which of our fields.
    Everything else is dropped, and `audit()` reports which dropped columns
    looked like personal data so the operator can confirm before ingesting.
    """

    path: Path
    mapping: dict[str, str]
    name: str = "csv"
    state: str = "BIHAR"
    encoding: str = "utf-8-sig"

    def columns(self) -> list[str]:
        with self.path.open(encoding=self.encoding, newline="") as handle:
            return next(csv.reader(handle), [])

    def audit(self) -> dict:
        columns = self.columns()
        mapped = {v for v in self.mapping.values() if v}
        missing = sorted(mapped - set(columns))
        return {
            "columns": len(columns),
            "mapped": sorted(mapped),
            "missing_from_file": missing,
            "personal_data_columns_present": audit_columns(columns),
        }

    def fetch(self) -> Iterator[FirRecord]:
        report = self.audit()
        if report["missing_from_file"]:
            raise ValueError(
                f"{self.path.name}: mapping names columns that are not in the file: "
                f"{report['missing_from_file']}. Columns present: {self.columns()}")
        with self.path.open(encoding=self.encoding, newline="") as handle:
            for row in csv.DictReader(handle):
                yield FirRecord.from_row(row, self.mapping, source=self.name, state=self.state)


# --------------------------------------------------------------------------
# ASP.NET WebForms portals
# --------------------------------------------------------------------------

class _FormParser(HTMLParser):
    """Collect every form control on an ASP.NET page.

    WebForms pages carry their state in hidden inputs (__VIEWSTATE and friends)
    which must be echoed back verbatim on each post. Reading them from the page
    rather than hardcoding them is what makes this work without having seen it.
    """

    def __init__(self) -> None:
        super().__init__()
        self.hidden: dict[str, str] = {}
        self.controls: list[dict[str, str]] = []
        self.selects: list[str] = []
        self._select_name: str | None = None
        self.options: dict[str, list[tuple[str, str]]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {k: (v or "") for k, v in attrs}
        if tag == "input":
            name = attributes.get("name")
            if not name:
                return
            if attributes.get("type", "").lower() == "hidden":
                self.hidden[name] = attributes.get("value", "")
            else:
                self.controls.append({
                    "name": name,
                    "type": attributes.get("type", "text"),
                    "id": attributes.get("id", ""),
                    "value": attributes.get("value", ""),
                })
        elif tag == "select":
            name = attributes.get("name")
            if name:
                self.selects.append(name)
                self._select_name = name
                self.options[name] = []
        elif tag == "option" and self._select_name:
            self.options[self._select_name].append(
                (attributes.get("value", ""), ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "select":
            self._select_name = None


@dataclass
class BiharScrbSource:
    """Adapter for Bihar's public FIR repository. NEVER RUN AGAINST LIVE.

    Status: the endpoint is documented in `research/sources/state-police-east-ne.md`
    as CITED — its URL and purpose were confirmed from a search index, but the
    page itself was never opened, so every field name below is unknown rather
    than wrong.

    To finish this adapter, from a network that can reach the host:

        source = BiharScrbSource()
        print(source.probe())

    `probe()` prints the form's hidden state keys, its visible controls and its
    dropdowns. Fill `controls` with the real names for district, police station
    and the date range, fill `row_selector` with how a result row is laid out,
    and the rest of this class already works.

    **Three constraints are settled and must not be coded around.**

    1. Bihar's repository withholds sexual offences and POCSO (Supreme Court
       direction, 7 September 2016) and additionally withholds national
       security, law-and-order and communal FIRs. Those categories must render
       as "withheld", never as zero.
    2. The listing carries complainant and accused names. `FirRecord` cannot
       hold them; do not add a field that can.
    3. If the form presents a CAPTCHA, this adapter stops. That is a decision,
       not a limitation to work around.
    """

    base_url: str = "https://scrb.bihar.gov.in"
    # Corrected from View_FIR.aspx after a third-party scraper was found naming
    # this path. Still CITED, not verified: the host is unreachable from here.
    path: str = "/FIRiew.aspx"
    delay_seconds: float = 2.0
    user_agent: str = "IndiaCrimeMap/0.1 (public-interest research; contact in repo)"
    name: str = "bihar-scrb"

    # Form controls named by a third-party scraper of this portal. CITED, not
    # verified — probe() must confirm them against the live form before use.
    controls: dict[str, str] = field(default_factory=lambda: {
        "district": "ddlDistrict",
        "police_station": "ddlPoliceStation",
        "date_from": "txtfDate",
        "date_to": "txttDate",
        "submit": "btnSearch",
    })

    # Set deliberately by an operator who has read the site's terms of use.
    terms_reviewed: bool = False

    @property
    def url(self) -> str:
        return urllib.parse.urljoin(self.base_url, self.path)

    def _get(self, url: str, data: bytes | None = None) -> str:
        request = urllib.request.Request(
            url, data=data,
            headers={"User-Agent": self.user_agent,
                     "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
        time.sleep(self.delay_seconds)
        return body.decode("utf-8", "replace")

    def probe(self) -> dict:
        """Report what the live form actually contains. Read-only."""
        html = self._get(self.url)
        parser = _FormParser()
        parser.feed(html)
        captcha = bool(re.search(r"captcha|securimage", html, re.I))
        return {
            "url": self.url,
            "hidden_state_keys": sorted(parser.hidden),
            "controls": parser.controls,
            "dropdowns": {name: len(options) for name, options in parser.options.items()},
            "captcha_detected": captcha,
            "next_step": (
                "A CAPTCHA is present. This adapter stops here by design; pursue the "
                "data by RTI instead — see research/sources/rti-playbook.md."
                if captcha else
                "Map these control names into BiharScrbSource.controls, then implement "
                "row parsing against a saved copy of a result page."),
        }

    def fetch(self) -> Iterator[FirRecord]:
        if not self.terms_reviewed:
            raise RuntimeError(
                "Refusing to fetch: set terms_reviewed=True only after reading this "
                "portal's terms of use and confirming that automated access is permitted. "
                "See docs/INGESTION.md.")
        if not self.controls:
            raise NotImplementedError(
                "BiharScrbSource is not finished: its form controls are unknown because "
                "the host was unreachable when it was written. Run probe() from a network "
                "that can reach scrb.bihar.gov.in and fill in `controls`. Until then use "
                "CsvFirSource with an export or an RTI response.")
        raise NotImplementedError(
            "Result-row parsing must be written against a real result page. Save one, "
            "add it to tests/fixtures/, and implement parsing test-first.")


# Column names a third-party scraper reports for Bihar's published-FIR table.
# CITED, not verified. Bihar uniquely publishes incident_date — when the offence
# happened — and also publishes complainant and accused names, which is why
# FirRecord cannot hold them.
BIHAR_COLUMNS = {
    "district": "district",
    "police_station": "police_station",
    "fir_number": "fir_no",
    "registered_on": "fir_date",
    "occurred_on": "incident_date",
    "sections": "sections",
}

# Maharashtra's CCTNS portal, verified against harvested rows in tests/fixtures.
MAHARASHTRA_COLUMNS = {
    "district": "district",
    "police_station": "policeStation",
    "fir_number": "firNumber",
    "fir_year": "year",
    "registered_on": "registrationDate",
    "sections": "sections",
}


def load_records(sources: Iterable[FirSource]) -> list[FirRecord]:
    records: list[FirRecord] = []
    for source in sources:
        records.extend(source.fetch())
    return records
