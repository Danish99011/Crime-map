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

Special and local laws are read by the act's name, never by a bare number. A
handful of them feed a head (`SLL_SECTIONS`): the Motor Vehicles Act into
rash driving, the NDPS Act into narcotics, the Maharashtra Police and
Prohibition Acts into public order. A section under any other named act
matches nothing, because its number means something else under the penal
codes: Prohibition Act 85 is public drunkenness, BNS 85 is cruelty by a husband.

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
    # The three heads below rank beneath every offence against a person or
    # property, so a theft FIR that also cites rash driving is counted as
    # theft, as NCRB would count it. Their special-law sections (Motor
    # Vehicles Act, NDPS Act, Maharashtra Police and Prohibition Acts) are in
    # SLL_SECTIONS below, gated on the act's name.
    CrimeHead("narcotics", "Narcotic drugs (NDPS)", "other", severity=5),
    CrimeHead("rash-driving", "Rash or negligent driving and endangerment", "other",
              ipc=("279", "283", "287", "336", "337", "338"),
              bns=("125", "281", "285", "287"), resolution_loss=True, severity=5),
    CrimeHead("public-order", "Public order and prohibitory orders", "public-order",
              ipc=("188",), bns=("223",), severity=6),
    CrimeHead("other", "Other offences", "other", severity=5),
)

# Sections of special and local laws that feed a head, by the act code that
# `detect_sll_act` returns. They live beside the heads rather than on them
# because they are not comparable across states the way IPC/BNS sections are:
# the Motor Vehicles Act and the NDPS Act are central, but the Maharashtra
# Police Act and the Maharashtra Prohibition Act are state statutes, and
# another state's equivalents are different acts with different numbering.
#
# Only the sections named here count. Every other section under these acts,
# and every section under an act not named here, stays in "other": being found
# in suspicious circumstances at night (Police Act 122) is a stop, not an
# offence against public order, and a helmet fine (MV Act 194D) is not rash
# driving.
SLL_SECTIONS: dict[str, dict[str, tuple[str, ...]]] = {
    # Dangerous driving (184) and driving under the influence (185).
    "rash-driving": {"MVA": ("184", "185")},
    # Section 8 is the prohibition every NDPS FIR cites; 15-30 are the
    # offences and penalties of Chapter IV.
    "narcotics": {"NDPS": ("8", "8A", "15", "16", "17", "18", "19", "20", "21",
                           "22", "23", "24", "25", "25A", "26", "27", "27A",
                           "27B", "28", "29", "30")},
    # Police Act 37 is the power to issue a prohibitory order and 135 the
    # penalty for breaking one; Prohibition Act 65 is illicit manufacture,
    # possession or sale of liquor.
    "public-order": {"MPA": ("37", "135"), "PROH": ("65",)},
}

BY_KEY = {head.key: head for head in CRIME_HEADS}
WITHHELD_KEYS = tuple(h.key for h in CRIME_HEADS if h.withheld)

# A section is digits optionally followed by a suffix letter attached directly
# (304A, 376D, 498A). The suffix must NOT be separated by a space, or the act
# name gets swallowed: "302 IPC" would parse as section "302IP".
_SECTION_RE = re.compile(r"\b(\d{1,3}[A-Z]{0,2})\b")

# Act names as police portals actually write them. Maharashtra's CCTNS portal
# writes them in Marathi; Bihar's writes English. Both are matched here because
# the same stock CCTNS software is deployed across states with the labels
# localised, so a parser that only reads English silently mis-reads half of
# India. Getting this wrong is not cosmetic: IPC 303 is murder by a life-convict
# and BNS 303 is theft, so a missed act name turns thefts into homicides.
_ACT_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    ("BNS", re.compile(r"भारतीय\s*न्याय\s*संहिता|बी\s*एन\s*एस|बीएनएस|"
                       r"\bBNS\b|BHARATIYA\s+NYAYA", re.I)),
    ("IPC", re.compile(r"भारतीय\s*दंड\s*संहिता|भा\.?द\.?वि|आई\s*पी\s*सी|"
                       r"\bIPC\b|INDIAN\s+PENAL", re.I)),
)

# Special and local laws whose sections feed a head (see SLL_SECTIONS). These
# are matched on the act's name and never on a bare number, because the
# numbers collide: Motor Vehicles Act 184 and 185 are dangerous and drunk
# driving, IPC 184 and 185 are obstructing a public sale; Maharashtra
# Prohibition Act 85 is being drunk in public, BNS 85 is cruelty by a husband.
# Before the special laws were gated, every Prohibition s.85 FIR in Mumbai
# was counted as domestic cruelty.
#
# Each pattern is written to reject the look-alike acts that sit next to it
# on the portal's dropdown, listed on the pattern.
_SLL_ACT_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    # Motor Vehicles Act 1988, written 'मोटरवाहन' and 'मोटार वाहन'. 'अधिनियम'
    # (Act) is required so that the Maharashtra Motor Vehicles *Rules* 1989
    # ('मोटार वाहन नियम') and the Motor Vehicles *Tax* Act ('मोटर वाहन (कर)
    # अधिनियम') do not match: a rule number is not an Act section.
    ("MVA", re.compile(r"मोटा?र\s*वाहन\s*अधिनियम|MOTOR\s+VEHICLES?\s+ACT", re.I)),
    # NDPS Act 1985. 'गुंगीकारक' is the word for narcotic in the Marathi
    # title, which the portal writes with joiners inside conjuncts and a typo
    # in 'पदार्थ'. The English form refuses 'IN NARCOTIC DRUGS' so that the
    # Prevention of Illicit Traffic in NDPS Act 1988, a preventive-detention
    # law whose Marathi title ('अंमली औषधीद्रव्य ... विधिनिसीध्द व्यापार
    # प्रतिबंध अधिनियम') shares no word with this pattern, is not read as it.
    ("NDPS", re.compile(r"गुंगीकारक|एन\s*डी\s*पी\s*एस|एनडीपीएस|\bNDPS\b|"
                        r"(?<!IN\s)NARCOTIC\s+DRUGS", re.I)),
    # Maharashtra Police Act 1951, formerly the Bombay Police Act. The
    # Police (Incitement to Disaffection) Act 1922 ('पोलीस (अप्रीतीची भावना
    # चेतावणे) अधिनियम') is a different statute and does not match.
    ("MPA", re.compile(r"(?:महाराष्ट्र|मुंबई)\s*पोल[ीि]स\s*अधिनियम|"
                       r"(?:MAHARASHTRA|BOMBAY)\s+POLICE\s+ACT", re.I)),
    # Maharashtra Prohibition Act 1949, formerly the Bombay Prohibition Act.
    # 'दारूबंदी' is liquor prohibition specifically; the Dowry Prohibition
    # Act is 'हुंडाबंदी'. In English only the Maharashtra/Bombay title is
    # accepted, since other states' prohibition acts number differently.
    ("PROH", re.compile(r"दार[ूु]बंदी|(?:MAHARASHTRA|BOMBAY)\s+PROHIBITION\s+ACT",
                        re.I)),
)

# Zero-width joiners the portal inserts inside Devanagari conjuncts, and not
# consistently: 'महाराष्ट्र' appears with and without one. Stripped before an
# act name is matched, since a regex written against the plain spelling would
# otherwise miss the joined one.
_JOINERS = re.compile("[‌‍]")

# Devanagari digits appear in Marathi act years (१९८८) AND in the section
# numbers themselves: Maharashtra writes pre-BNS FIRs as
# "भारतीय दंड संहिता १८६० - ३८०", where १८६० is the year 1860 and ३८० is
# section 380. An earlier version of this module assumed they were only ever
# years and deleted them, which left 97% of the first live Mumbai month
# unclassified -- every pre-2024 theft and burglary silently became "other".
#
# So they are transliterated rather than dropped, and the existing rule that
# strips bare years does the rest. The digits are contiguous in Unicode, so
# the mapping is arithmetic.
_DEVANAGARI_DIGITS = re.compile(r"[\u0966-\u096F]+")
_DEVANAGARI_TO_ASCII = {0x0966 + n: str(n) for n in range(10)}


def devanagari_digits_to_ascii(text: str) -> str:
    """Rewrite ०-९ as 0-9, leaving everything else untouched."""
    return text.translate(_DEVANAGARI_TO_ASCII)

# A sections cell may carry several acts, separated by newlines or by a
# semicolon that is followed by another act name.
_SEGMENT_SPLIT = re.compile(r"[\r\n]+|;\s*(?=\S*[\u0900-\u097F A-Za-z]{4})")


def detect_act_or_none(text: str | None) -> str | None:
    """'IPC' or 'BNS' if either is named here, else None."""
    text = _JOINERS.sub("", text or "")
    for code, pattern in _ACT_PATTERNS:
        if text and pattern.search(text):
            return code
    return None


def detect_sll_act(text: str | None) -> str | None:
    """The code of a special or local law named here, or None.

    Only the acts in `_SLL_ACT_PATTERNS` are recognised. A penal code is never
    returned from here, and any other act name is None: its sections are read
    under no numbering at all rather than under a guessed one.
    """
    text = _JOINERS.sub("", text or "")
    if not text or detect_act_or_none(text):
        return None
    for code, pattern in _SLL_ACT_PATTERNS:
        if pattern.search(text):
            return code
    return None


def detect_act(text: str | None) -> str:
    """Return 'IPC', 'BNS' or 'SLL' for an act name in English or Devanagari.

    Anything named that is not the penal code is a special or local law. Those
    counts are not comparable across states, since state legislatures differ on
    prohibition, gambling and cow protection, so they are labelled rather than
    folded in.
    """
    return detect_act_or_none(text) or ("SLL" if text else "SLL")


def parse_section_field(text: str | None) -> list[tuple[str, str, list[str]]]:
    """Split a portal's 'sections' cell into (act_code, act_name, sections).

    Real example from Maharashtra, one FIR, two acts:

        मोटरवाहन अधिनियम, १९८८  - 184 ;
        भारतीय न्याय संहिता (बी एन एस), 2023 - 125(a),125(b),281,324(4) ;

    Each act must be read with its own sections, because the same number means
    different offences under different acts.
    """
    if not text:
        return []
    out = []
    for segment in _SEGMENT_SPLIT.split(text):
        segment = segment.strip(" ;\t")
        if not segment:
            continue
        # Sections follow the last dash; everything before it names the act.
        # A segment with no dash is bare section numbers — some feeds carry the
        # act in its own column instead.
        head, dash, tail = segment.rpartition("-")
        if not dash:
            head, tail = "", segment
        act_name = _DEVANAGARI_DIGITS.sub(" ", head).strip(" ,")
        sections = parse_sections(tail)
        if not sections:
            continue
        if act_name:
            act_code = detect_act(act_name)
        else:
            # No act name before a dash, but the act may still be written
            # inline ("302 IPC"). Only accept a real match; otherwise leave it
            # unknown so the caller's act column can decide.
            act_code = detect_act_or_none(segment) or ""
        out.append((act_code, act_name, sections))
    return out


def classify_field(text: str | None,
                   act_hint: str | None = None) -> tuple[str, bool, list[str]]:
    """Classify a whole sections cell, honouring each act separately.

    Returns (crime_key, confident, act_codes). Applies the principal offence
    rule across every act in the FIR, matching NCRB practice.

    `act_hint` names the act for feeds that carry it in its own column rather
    than inline. It is only used for segments that name no act themselves, so an
    inline act always wins — which matters, because a row's act column may say
    "BNS" while one of its segments cites the Motor Vehicles Act.
    """
    segments = parse_section_field(text)
    if not segments:
        return "other", False, []
    hint = detect_act(act_hint) if act_hint else ""
    best_key, confident = "other", False
    best_severity = 99
    acts = set()
    for act_code, act_name, sections in segments:
        resolved = act_code or hint
        acts.add(resolved or "UNKNOWN")
        # The act's *name* decides which numbering the sections are read
        # under, so it goes to classify() whole: the code "SLL" alone cannot
        # say whether 184 is the Motor Vehicles Act or something else. The
        # code is only the label the record carries.
        key, ok = classify(sections, act_name or act_code or act_hint or None)
        if ok and BY_KEY[key].severity < best_severity:
            best_key, best_severity, confident = key, BY_KEY[key].severity, True
    return best_key, confident, sorted(acts)
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
    for key, acts in SLL_SECTIONS.items():
        if key not in BY_KEY:
            raise KeyError(f"SLL_SECTIONS names a head that does not exist: {key!r}")
        for act, sections in acts.items():
            for section in sections:
                index.setdefault((act, section.upper()), key)
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
    # Devanagari section numbers first, so everything below sees one numeral
    # system. Act years written in Devanagari become ordinary years here and
    # are removed by the year rule a few lines down, exactly as Latin ones are.
    text = devanagari_digits_to_ascii(text)
    # Sub-section markers: 303(2), 125(a), 118(1). The parent section decides
    # the head, so the marker is dropped rather than read as another number.
    cleaned = re.sub(r"\((?:\d+|[a-zA-Z])\)", " ", text.upper())
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

    `act` is a code ('IPC', 'BNS') or the act's name as a portal wrote it, in
    English or Devanagari. A named act is read under its own numbering only:
    a penal code by its book, a recognised special law by its code, and any
    other act not at all, because its numbers mean something else there. Only
    when no act is named are both penal codes tried.
    """
    code = detect_act_or_none(act)
    if code:
        books: tuple[str, ...] = (code,)
    elif act:
        sll = detect_sll_act(act)
        books = (sll,) if sll else ()
    else:
        books = ("IPC", "BNS")

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
