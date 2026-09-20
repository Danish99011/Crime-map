"""Law-neutral crime categories, and the section numbers that map into them.

**Never key crime data on a section number.** The Indian Penal Code was repealed
on 1 July 2024 and replaced by the Bharatiya Nyaya Sanhita, and the relation
between them is many-to-many: IPC 383-389 all collapse into BNS 308, IPC 453-460
all collapse into BNS 331, IPC 364/364A/365/367 all collapse into BNS 140. A
series keyed on sections therefore breaks in the middle of 2024 and cannot be
repaired. Everything here keys on a stable `crime_key` instead, with IPC and BNS
sections as attributes of it.

Three consequences are recorded on the categories themselves, because a map that
hides them misleads:

* **Post-2024 property crime is permanently lower-resolution.** Where several
  IPC offences collapse into one BNS offence, the category carries
  `resolution_loss=True` and any pre/post-2024 comparison within it is invalid.
* **Some categories are new.** BNS 304 (snatching), 111/112 (organised crime),
  113 (terrorist act) and 103(2) (mob lynching) have no IPC predecessor. A
  2024-to-2025 growth chart for these measures the statute book, not crime.
* **Some categories are withheld from public FIR data entirely.** Sexual
  offences and POCSO are excluded under a Supreme Court direction of 7 September
  2016, and Bihar's repository additionally withholds national-security,
  law-and-order and communal FIRs. These categories exist here precisely so the
  map can say "withheld" rather than render a reassuring blank.

The concordance in `data/reference/ipc_bns_concordance.csv` was assembled by hand
and is largely unverified against the gazette — see its provenance note. It is
used here only to *cross-check* the explicit section lists below and to surface
low-confidence rows, never as the source of truth for a mapping.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

REFERENCE = Path(__file__).resolve().parent.parent / "data" / "reference"
CONCORDANCE_FILE = REFERENCE / "ipc_bns_concordance.csv"


@dataclass(frozen=True)
class CrimeHead:
    key: str
    label: str
    group: str
    ipc: tuple[str, ...] = ()
    bns: tuple[str, ...] = ()
    resolution_loss: bool = False   # several IPC offences collapse into one BNS
    no_ipc_predecessor: bool = False  # BNS invented it; no pre-2024 baseline
    withheld: str | None = None     # why this never appears in public FIR data
    severity: int = 3               # 1 = most serious, used only for display order


# The categories a resident actually asks about, not NCRB's reporting heads.
CRIME_HEADS: tuple[CrimeHead, ...] = (
    CrimeHead("homicide", "Murder and culpable homicide", "violence",
              ipc=("302", "303", "304"), bns=("101", "103", "104", "105"), severity=1),
    CrimeHead("attempt-murder", "Attempt to murder", "violence",
              ipc=("307", "308"), bns=("109", "110"), severity=1),
    CrimeHead("grievous-hurt", "Grievous hurt", "violence",
              ipc=("325", "326", "326A", "326B"), bns=("117", "118"), severity=2),
    CrimeHead("hurt", "Hurt and assault", "violence",
              ipc=("323", "324", "352", "commonly depleted"), bns=("115", "131"), severity=3),
    CrimeHead("kidnapping", "Kidnapping and abduction", "violence",
              ipc=("363", "364", "364A", "365", "366", "367", "369"),
              bns=("137", "139", "140"), resolution_loss=True, severity=2),
    CrimeHead("dowry-death", "Dowry death", "women",
              ipc=("304B",), bns=("80",), severity=1),
    CrimeHead("domestic-cruelty", "Cruelty by husband or relatives", "women",
              ipc=("498A",), bns=("85",), severity=2),
    CrimeHead("sexual-offence", "Rape and sexual offences", "women",
              ipc=("376", "376D", "354"), bns=("64", "70", "74"), severity=1,
              withheld="Excluded from public FIR publication under the Supreme Court "
                       "direction of 7 September 2016. Absence here is not absence in reality."),
    CrimeHead("pocso", "Offences against children (POCSO)", "children",
              ipc=(), bns=(), severity=1,
              withheld="Excluded from public FIR publication to protect the child's identity "
                       "(POCSO s.23). Absence here is not absence in reality."),
    CrimeHead("robbery", "Robbery", "property",
              ipc=("392", "393", "394", "397", "398"), bns=("309",), severity=2),
    CrimeHead("dacoity", "Dacoity", "property",
              ipc=("395", "396", "397"), bns=("310",), severity=1),
    CrimeHead("burglary", "House-breaking and burglary", "property",
              ipc=("454", "457", "380"), bns=("331",), resolution_loss=True, severity=3),
    CrimeHead("theft", "Theft", "property",
              ipc=("379", "380", "381", "382"), bns=("303", "305"), severity=4),
    CrimeHead("snatching", "Snatching", "property",
              ipc=(), bns=("304",), no_ipc_predecessor=True, severity=3),
    CrimeHead("extortion", "Extortion", "property",
              ipc=("384", "385", "386", "387", "388", "389"), bns=("308",),
              resolution_loss=True, severity=3),
    CrimeHead("cheating", "Cheating and fraud", "property",
              ipc=("417", "418", "419", "420"), bns=("316", "318"), severity=4),
    CrimeHead("criminal-intimidation", "Criminal intimidation", "public-order",
              ipc=("506", "509"), bns=("351",), severity=4),
    CrimeHead("rioting", "Rioting and unlawful assembly", "public-order",
              ipc=("147", "148", "149"), bns=("191", "192"), severity=3),
    CrimeHead("negligent-death", "Death by negligence (incl. road)", "other",
              ipc=("304A",), bns=("106",), severity=2),
    CrimeHead("other", "Other offences", "other", severity=5),
)

BY_KEY = {head.key: head for head in CRIME_HEADS}
WITHHELD_KEYS = tuple(h.key for h in CRIME_HEADS if h.withheld)

# A section is digits optionally followed by a suffix letter attached directly
# (304A, 376D, 498A). The suffix must NOT be separated by a space, or the act
# name gets swallowed: "302 IPC" would parse as section "302IP".
_SECTION_RE = re.compile(r"\b(\d{1,3}[A-Z]{0,2})\b")
# Statute names and the noise around them, removed before sections are read.
_ACT_TOKENS = re.compile(
    r"\b(IPC|BNS|BNSS|CRPC|CR\.?P\.?C|IEA|BSA|POCSO|ACT|SEC|SECTION|SECTIONS|"
    r"U/?S|R/?W|READ WITH|OF|THE)\b")


def _index() -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    for head in CRIME_HEADS:
        for section in head.ipc:
            if section[0].isdigit():
                index.setdefault(("IPC", section.upper()), head.key)
        for section in head.bns:
            if section[0].isdigit():
                index.setdefault(("BNS", section.upper()), head.key)
    return index


SECTION_INDEX = _index()


def parse_sections(text: str | None) -> list[str]:
    """Pull section numbers out of a free-text 'Under Section(s)' field.

    FIR listings write these as '379/411 IPC', '103(2) BNS', '323, 504, 506' and
    every other shape. Sub-section parentheses are dropped: BNS 103(2) is mob
    lynching, but the head it belongs to is decided by the parent section.
    """
    if not text:
        return []
    cleaned = re.sub(r"\(\d+\)", " ", text.upper())
    cleaned = _ACT_TOKENS.sub(" ", cleaned)
    # Drop bare years, which appear as "Arms Act, 1959" and are not sections.
    cleaned = re.sub(r"\b(1[89]|20)\d{2}\b", " ", cleaned)
    seen, sections = set(), []
    for match in _SECTION_RE.findall(cleaned):
        if match not in seen:
            seen.add(match)
            sections.append(match)
    return sections


def classify(sections: list[str], act: str | None = None) -> tuple[str, bool]:
    """Map a list of sections to one crime_key, plus whether we were confident.

    Returns the *most serious* matching head, mirroring NCRB's principal offence
    rule so our counts are comparable with theirs. That rule systematically
    depletes subordinate heads — an 'assault' map is inverted in violent areas —
    which is why `aggregate.py` records it alongside every count rather than
    leaving it to a methodology page.
    """
    statute = (act or "").upper()
    books = ("BNS",) if "BNS" in statute else ("IPC",) if "IPC" in statute else ("IPC", "BNS")

    matches = []
    for section in sections:
        for book in books:
            key = SECTION_INDEX.get((book, section))
            if key:
                matches.append(BY_KEY[key])
                break
    if not matches:
        return "other", False
    best = min(matches, key=lambda h: (h.severity, h.key))
    return best.key, True


def load_concordance() -> list[dict]:
    if not CONCORDANCE_FILE.exists():
        return []
    with CONCORDANCE_FILE.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def concordance_warnings() -> list[str]:
    """Surface the concordance rows our categories lean on that are weakest."""
    warnings = []
    for row in load_concordance():
        if row.get("confidence") == "L":
            warnings.append(f"low-confidence IPC {row['ipc']} -> BNS {row['bns']}: {row['offence']}")
        if row.get("relation") == "M":
            warnings.append(f"resolution loss: IPC {row['ipc']} collapses into BNS {row['bns']}")
    return warnings
