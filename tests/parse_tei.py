"""TEI-Parser für das Test-Set.

Liest einzelne TEI-Dokumente aus `sources/QGW/**` und
`sources/Stadtbuecher/**` und extrahiert die Informationen, die für
Aggregation und Vergleich mit den Frontend-JSONs gebraucht werden.

Scope: Struktur, die im Corpus tatsächlich verwendet wird (getestet an
QGW/Vienna_1177-1414_ready und Stadtbuecher/Band_1_1395-1400_ready).
Andere Korpora ohne TEI-Quelle im Pipeline-Repo werden nicht abgedeckt
(siehe tests/README.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

from lxml import etree

from tests.config import COLLECTIONS_WITH_TEI, NS, TEI_SOURCES_DIR

TEI_NS = NS["tei"]
TEI_PREFIX = f"{{{TEI_NS}}}"


@dataclass
class DocRecord:
    file_key: str
    path: Path
    collection: str
    subcollection: str
    idno: Optional[str] = None
    date_iso: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    decade: Optional[int] = None
    events: Set[str] = field(default_factory=set)
    person_refs: Set[str] = field(default_factory=set)
    org_refs: Set[str] = field(default_factory=set)
    place_refs: Set[str] = field(default_factory=set)
    # (person_ref, role) pairs. Role kommt vom nächstgelegenen <rs type='fn'>-Vorfahr.
    person_roles: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    org_roles: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    # (relation_type, source_ref, target_ref) tuples via <roleName @type @corresp>
    relations: List[Tuple[str, Optional[str], str]] = field(default_factory=list)
    # Normierte "disp"-Trigger-Texte pro Event (unverändert, nur lowercase, trimmed)
    disp_triggers: List[str] = field(default_factory=list)


def _strip_hash(ref: Optional[str]) -> Optional[str]:
    if not ref:
        return None
    return ref.lstrip("#").strip() or None


def _parse_when(when: str) -> Optional[str]:
    """Normalisiert TEI-@when zu ISO YYYY-MM-DD (so weit möglich)."""
    if not when:
        return None
    w = when.strip()
    if not w:
        return None
    # YYYYMMDD kompakt
    if len(w) == 8 and w.isdigit():
        return f"{w[0:4]}-{w[4:6]}-{w[6:8]}"
    # YYYY-MM-DD bereits kanonisch
    if len(w) == 10 and w[4] == "-" and w[7] == "-":
        return w
    # YYYY-MM
    if len(w) == 7 and w[4] == "-":
        return w + "-01"
    # YYYY nur
    if len(w) == 4 and w.isdigit():
        return f"{w}-01-01"
    return None


def _decade_of(date_iso: Optional[str]) -> Optional[int]:
    if not date_iso or len(date_iso) < 4:
        return None
    try:
        year = int(date_iso[:4])
    except ValueError:
        return None
    return (year // 10) * 10


def _find_innermost_role(node) -> Optional[str]:
    """Traverse ancestors and return the @role of the nearest <rs type='fn'>.

    Innermost gewinnt: wenn ein `<rs type="fn" role="other">` innerhalb eines
    `<rs type="fn" role="issuer">` liegt, haben Kinder des inneren Blocks
    Rolle `other`.
    """
    current = node.getparent()
    while current is not None:
        if current.tag == f"{TEI_PREFIX}rs" and current.get("type") == "fn":
            role = current.get("role")
            if role:
                return role.strip()
        current = current.getparent()
    return None


def _collection_and_sub(path: Path) -> Tuple[str, str]:
    """('QGW', 'Vienna_1177-1414_ready') aus .../sources/QGW/Vienna_1177-1414_ready/done/100.xml."""
    try:
        rel = path.relative_to(TEI_SOURCES_DIR)
    except ValueError:
        return "", ""
    parts = rel.parts
    collection = parts[0] if parts else ""
    subcollection = parts[1] if len(parts) > 1 else ""
    return collection, subcollection


def _file_key(path: Path) -> str:
    """Stabiler Schlüssel analog zur Pipeline.

    Beispiel-Pfad: .../sources/QGW/Vienna_1177-1414_ready/done/100.xml
    File-Key:      QGW_Vienna_1177-1414_ready_100
    """
    collection, subcollection = _collection_and_sub(path)
    stem = path.stem
    return f"{collection}_{subcollection}_{stem}" if subcollection else f"{collection}_{stem}"


def parse_document(path: Path) -> Optional[DocRecord]:
    """Parst eine einzelne TEI-Datei. Gibt None bei Parse-Fehlern zurück."""
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError:
        return None
    root = tree.getroot()

    collection, subcollection = _collection_and_sub(path)
    rec = DocRecord(
        file_key=_file_key(path),
        path=path,
        collection=collection,
        subcollection=subcollection,
    )

    # Metadaten
    idno = root.find(".//tei:msIdentifier/tei:idno", NS)
    if idno is not None and idno.text:
        rec.idno = idno.text.strip()

    # Datum aus profileDesc/creation/date
    date_node = root.find(".//tei:profileDesc/tei:creation/tei:date", NS)
    if date_node is not None:
        when = date_node.get("when")
        if when:
            rec.date_iso = _parse_when(when)
        else:
            frm = date_node.get("from")
            to = date_node.get("to")
            rec.date_from = _parse_when(frm) if frm else None
            rec.date_to = _parse_when(to) if to else None
            if rec.date_from:
                rec.date_iso = rec.date_from
    rec.decade = _decade_of(rec.date_iso)

    # Entity-Nennungen und Rollen-Zuordnung
    for rs in root.iter(f"{TEI_PREFIX}rs"):
        rtype = rs.get("type")
        if rtype not in ("person", "org", "place", "event"):
            continue
        ref = _strip_hash(rs.get("ref"))
        if not ref:
            continue
        if rtype == "event":
            rec.events.add(ref)
            # disp-Trigger pro Event einsammeln
            for trig in rs.iter(f"{TEI_PREFIX}triggerstring"):
                if trig.get("n") == "disp":
                    text = (trig.text or "").strip().lower()
                    if text:
                        rec.disp_triggers.append(text)
        elif rtype == "person":
            rec.person_refs.add(ref)
            rec.person_roles.append((ref, _find_innermost_role(rs)))
        elif rtype == "org":
            rec.org_refs.add(ref)
            rec.org_roles.append((ref, _find_innermost_role(rs)))
        elif rtype == "place":
            rec.place_refs.add(ref)

    # Beziehungen via <roleName @type @corresp>
    for rn in root.iter(f"{TEI_PREFIX}roleName"):
        rtype = rn.get("type")
        corresp = _strip_hash(rn.get("corresp"))
        if not rtype or not corresp:
            continue
        # Beziehungs-Quelle: nächstgelegener <rs type="person"> Vorfahr
        ancestor = rn.getparent()
        source_ref = None
        while ancestor is not None:
            if ancestor.tag == f"{TEI_PREFIX}rs" and ancestor.get("type") == "person":
                source_ref = _strip_hash(ancestor.get("ref"))
                break
            ancestor = ancestor.getparent()
        rec.relations.append((rtype.strip(), source_ref, corresp))

    return rec


def iter_sources(collections: Iterable[str] = COLLECTIONS_WITH_TEI) -> Iterable[Path]:
    """Yield alle TEI-Dateien unterhalb der angegebenen Quellenkorpora.

    Überspringt Schema-Ordner (`sources/**/schema/**`) und den Root-Schema-Ordner.
    """
    for collection in collections:
        base = TEI_SOURCES_DIR / collection
        if not base.exists():
            continue
        for path in base.rglob("*.xml"):
            # Schemas überspringen
            if any(part.lower() == "schema" for part in path.parts):
                continue
            yield path


def scan_sources(collections: Iterable[str] = COLLECTIONS_WITH_TEI) -> List[DocRecord]:
    """Lädt und parst alle TEI-Dateien der angegebenen Quellenkorpora."""
    docs: List[DocRecord] = []
    for path in iter_sources(collections):
        rec = parse_document(path)
        if rec is not None:
            docs.append(rec)
    return docs
