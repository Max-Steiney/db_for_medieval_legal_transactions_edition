"""TEI-Coverage Stufe 3: TEI-Quelldatei direkt vs. gerendertes Quellen-HTML.

Ueberspringt die CSV-Pipeline-Zwischenstufe und prueft End-to-End:
Jede Personen- und Organisations-Annotation `<rs type="..." ref="...">` in der
TEI muss als `data-ref="..."` im gerenderten Quellen-HTML auftauchen, und
umgekehrt. Damit werden zwei Klassen von Fehlern aufgedeckt, die Stufe 1
(TEI -> JSON) und Stufe 2 (CSV -> HTML) jeweils einzeln nicht sehen koennen:

- TEI-Annotation, die vom Aggregator entfernt wurde, aber im HTML fehlt
  (Pipeline-Drop ohne Aggregat-Effekt).
- HTML-`data-ref`, das durch das Template injiziert wird, ohne dass die TEI-
  Quelle ihn enthaelt (Renderer-Halluzination).

Mapping: TEI-`file_key` `Korpus_Subkorpus_Stem` <-> HTML-Pfad
`docs/documents/Korpus/Subkorpus/Stem.html`. Beides liest die jeweils
authoritative Quelle ohne Umweg.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from verification import compare, parse_html, parse_tei
from verification.config import HTML_DOCUMENTS


CheckResult = compare.CheckResult


@dataclass
class DocPair:
    """Ein gepaarter Eintrag: TEI-Record + zugehoeriges HTML."""

    tei: parse_tei.DocRecord
    html: parse_html.DocumentHtml


def _html_path_for_tei(rec: parse_tei.DocRecord) -> Optional[Path]:
    """`sources/QGW/Vienna_1177-1414_ready/done/100.xml`
    -> `docs/documents/QGW/Vienna_1177-1414_ready/100.html`. None falls die
    HTML-Datei fehlt (Quelle wurde nicht gerendert)."""
    if not rec.collection or not rec.subcollection:
        return None
    candidate = HTML_DOCUMENTS / rec.collection / rec.subcollection / f"{rec.path.stem}.html"
    if candidate.exists():
        return candidate
    return None


def _build_pairs(docs: List[parse_tei.DocRecord]) -> Tuple[List[DocPair], List[parse_tei.DocRecord]]:
    """Paart TEI-Records mit ihren HTML-Aequivalenten. Records ohne HTML
    werden separat zurueckgegeben (typischerweise nicht-released Bandseiten
    oder Stadtbuecher-Eintraege, die `filenames.csv` ausschliesst).

    Bei Lese-Fehlern (parse_html.read_document liefert read_failed=True)
    wird das Dokument auch als "orphan" gewertet — Lesefehler werden
    separat in Stufe 2 (_check_reader_health) reported, sodass sie hier
    nicht stillschweigend in Symmetrie-Mismatches verschwinden."""
    paired: List[DocPair] = []
    orphans: List[parse_tei.DocRecord] = []
    for rec in docs:
        path = _html_path_for_tei(rec)
        if path is None:
            orphans.append(rec)
            continue
        html_doc = parse_html.read_document(path)
        if html_doc.read_failed:
            orphans.append(rec)
            continue
        paired.append(DocPair(tei=rec, html=html_doc))
    return paired, orphans


def _sample(items: List[str], n: int = 3) -> str:
    return ", ".join(items[:n]) + (f" (+{len(items) - n} weitere)" if len(items) > n else "")


def _format_diff(file_key: str, missing: Set[str], extra: Set[str]) -> str:
    parts = []
    if missing:
        parts.append(f"TEI->HTML fehlt: {_sample(sorted(missing))}")
    if extra:
        parts.append(f"HTML->TEI extra: {_sample(sorted(extra))}")
    return f"{file_key}: " + "; ".join(parts)


def check_person_refs(pairs: List[DocPair]) -> List[CheckResult]:
    """Jede Personen-Annotation in TEI muss im HTML auftauchen, und umgekehrt."""
    missing_in_html: Dict[str, Set[str]] = {}
    extra_in_html: Dict[str, Set[str]] = {}
    for pair in pairs:
        tei_refs: Set[str] = set(pair.tei.person_refs)
        html_refs: Set[str] = set(pair.html.person_refs)
        miss = tei_refs - html_refs
        extra = html_refs - tei_refs
        if miss:
            missing_in_html[pair.tei.file_key] = miss
        if extra:
            extra_in_html[pair.tei.file_key] = extra

    results: List[CheckResult] = []
    if missing_in_html:
        examples = [
            _format_diff(k, v, set()) for k, v in list(missing_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.person_refs.missing_in_html",
            tei=sum(len(v) for v in missing_in_html.values()),
            json=0,
            status="mismatch",
            note=(
                f"{len(missing_in_html)} Quellen haben TEI-Annotationen ohne HTML-data-ref. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.person_refs.missing_in_html",
            tei=0, json=0, status="match",
        ))

    if extra_in_html:
        examples = [
            _format_diff(k, set(), v) for k, v in list(extra_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.person_refs.extra_in_html",
            tei=0,
            json=sum(len(v) for v in extra_in_html.values()),
            status="mismatch",
            note=(
                f"{len(extra_in_html)} Quellen haben HTML-data-ref ohne TEI-Annotation. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.person_refs.extra_in_html",
            tei=0, json=0, status="match",
        ))
    return results


def check_org_refs(pairs: List[DocPair]) -> List[CheckResult]:
    """Analog zu check_person_refs fuer Organisations-Refs."""
    missing_in_html: Dict[str, Set[str]] = {}
    extra_in_html: Dict[str, Set[str]] = {}
    for pair in pairs:
        tei_refs: Set[str] = set(pair.tei.org_refs)
        html_refs: Set[str] = set(pair.html.org_refs)
        miss = tei_refs - html_refs
        extra = html_refs - tei_refs
        if miss:
            missing_in_html[pair.tei.file_key] = miss
        if extra:
            extra_in_html[pair.tei.file_key] = extra

    results: List[CheckResult] = []
    if missing_in_html:
        examples = [
            _format_diff(k, v, set()) for k, v in list(missing_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.org_refs.missing_in_html",
            tei=sum(len(v) for v in missing_in_html.values()),
            json=0,
            status="mismatch",
            note=(
                f"{len(missing_in_html)} Quellen haben TEI-Org-Annotationen ohne HTML-data-ref. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.org_refs.missing_in_html",
            tei=0, json=0, status="match",
        ))

    if extra_in_html:
        examples = [
            _format_diff(k, set(), v) for k, v in list(extra_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.org_refs.extra_in_html",
            tei=0,
            json=sum(len(v) for v in extra_in_html.values()),
            status="mismatch",
            note=(
                f"{len(extra_in_html)} Quellen haben HTML-Org-data-ref ohne TEI-Annotation. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.org_refs.extra_in_html",
            tei=0, json=0, status="match",
        ))
    return results


def check_event_refs(pairs: List[DocPair]) -> List[CheckResult]:
    """Event-Refs in TEI (<rs type="event">) vs. HTML (data-ref="ev__...").
    Events binden Rechtsgeschaeft, Versiegelung, Eintrag, Notiz — Drift hier
    waere ein Renderer- oder Pipeline-Fehler in der Event-Aufloesung.

    TEI-Konvention <rs type="event" ref="NULL"> markiert ein Event ohne
    Identifier; das Frontend rendert solche Faelle bewusst ohne data-ref.
    Diese werden hier herausgefiltert."""
    missing_in_html: Dict[str, Set[str]] = {}
    extra_in_html: Dict[str, Set[str]] = {}
    for pair in pairs:
        tei_refs: Set[str] = {r for r in pair.tei.events if r != "NULL"}
        html_refs: Set[str] = set(pair.html.event_refs)
        miss = tei_refs - html_refs
        extra = html_refs - tei_refs
        if miss:
            missing_in_html[pair.tei.file_key] = miss
        if extra:
            extra_in_html[pair.tei.file_key] = extra

    results: List[CheckResult] = []
    if missing_in_html:
        examples = [
            _format_diff(k, v, set()) for k, v in list(missing_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.event_refs.missing_in_html",
            tei=sum(len(v) for v in missing_in_html.values()),
            json=0,
            status="mismatch",
            note=(
                f"{len(missing_in_html)} Quellen haben TEI-Event-Annotationen ohne HTML-data-ref. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.event_refs.missing_in_html",
            tei=0, json=0, status="match",
        ))

    if extra_in_html:
        examples = [
            _format_diff(k, set(), v) for k, v in list(extra_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.event_refs.extra_in_html",
            tei=0,
            json=sum(len(v) for v in extra_in_html.values()),
            status="mismatch",
            note=(
                f"{len(extra_in_html)} Quellen haben HTML-Event-data-ref ohne TEI-Annotation. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.event_refs.extra_in_html",
            tei=0, json=0, status="match",
        ))
    return results


def check_place_refs(pairs: List[DocPair]) -> List[CheckResult]:
    """Place-Refs werden im HTML als Span+Tooltip gerendert, sind aber genauso
    `data-ref`-annotiert. Die Symmetrie sollte trotzdem gelten."""
    missing_in_html: Dict[str, Set[str]] = {}
    extra_in_html: Dict[str, Set[str]] = {}
    for pair in pairs:
        tei_refs: Set[str] = set(pair.tei.place_refs)
        html_refs: Set[str] = set(pair.html.place_refs)
        miss = tei_refs - html_refs
        extra = html_refs - tei_refs
        if miss:
            missing_in_html[pair.tei.file_key] = miss
        if extra:
            extra_in_html[pair.tei.file_key] = extra

    results: List[CheckResult] = []
    if missing_in_html:
        examples = [
            _format_diff(k, v, set()) for k, v in list(missing_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.place_refs.missing_in_html",
            tei=sum(len(v) for v in missing_in_html.values()),
            json=0,
            status="mismatch",
            note=(
                f"{len(missing_in_html)} Quellen haben TEI-Place-Annotationen ohne HTML-data-ref. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.place_refs.missing_in_html",
            tei=0, json=0, status="match",
        ))

    if extra_in_html:
        examples = [
            _format_diff(k, set(), v) for k, v in list(extra_in_html.items())[:3]
        ]
        results.append(CheckResult(
            name="teihtml.place_refs.extra_in_html",
            tei=0,
            json=sum(len(v) for v in extra_in_html.values()),
            status="mismatch",
            note=(
                f"{len(extra_in_html)} Quellen haben HTML-Place-data-ref ohne TEI-Annotation. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.place_refs.extra_in_html",
            tei=0, json=0, status="match",
        ))
    return results


def _pairs_set(pairs: List[Tuple[str, Optional[str]]]) -> Set[Tuple[str, Optional[str]]]:
    """(ref, role)-Paare als Set, mit None statt leerer Rolle."""
    return {(ref, role or None) for ref, role in pairs}


def check_person_roles(pairs: List[DocPair]) -> List[CheckResult]:
    """Pro Quelle: jede (person_ref, role)-Zuordnung der TEI muss im HTML
    als verschachtelte data-role-Klammer vorhanden sein.

    Findet Rollen-Drift, die die reine Ref-Symmetrie (check_person_refs) nicht
    sieht: wenn HTML einen pe__-Ref rendert, aber die umgebende data-role-
    Klammer falsch ist oder fehlt, ist das hier ein mismatch.
    """
    missing_pairs: Dict[str, Set[Tuple[str, Optional[str]]]] = {}
    extra_pairs: Dict[str, Set[Tuple[str, Optional[str]]]] = {}
    for pair in pairs:
        tei_set = _pairs_set(pair.tei.person_roles)
        html_set = _pairs_set(pair.html.person_roles)
        miss = tei_set - html_set
        extra = html_set - tei_set
        if miss:
            missing_pairs[pair.tei.file_key] = miss
        if extra:
            extra_pairs[pair.tei.file_key] = extra

    return _build_role_results(
        missing_pairs, extra_pairs,
        "teihtml.person_roles.missing_in_html",
        "teihtml.person_roles.extra_in_html",
        entity="Person",
    )


def check_org_roles(pairs: List[DocPair]) -> List[CheckResult]:
    """Analog zu check_person_roles fuer Organisations-Rollen."""
    missing_pairs: Dict[str, Set[Tuple[str, Optional[str]]]] = {}
    extra_pairs: Dict[str, Set[Tuple[str, Optional[str]]]] = {}
    for pair in pairs:
        tei_set = _pairs_set(pair.tei.org_roles)
        html_set = _pairs_set(pair.html.org_roles)
        miss = tei_set - html_set
        extra = html_set - tei_set
        if miss:
            missing_pairs[pair.tei.file_key] = miss
        if extra:
            extra_pairs[pair.tei.file_key] = extra

    return _build_role_results(
        missing_pairs, extra_pairs,
        "teihtml.org_roles.missing_in_html",
        "teihtml.org_roles.extra_in_html",
        entity="Org",
    )


def _build_role_results(
    missing_pairs: Dict[str, Set[Tuple[str, Optional[str]]]],
    extra_pairs: Dict[str, Set[Tuple[str, Optional[str]]]],
    miss_name: str,
    extra_name: str,
    entity: str,
) -> List[CheckResult]:
    """Gemeinsamer Result-Bau fuer person/org-Rollen."""
    results: List[CheckResult] = []
    if missing_pairs:
        examples = []
        for k, pairs in list(missing_pairs.items())[:3]:
            sample = ", ".join(f"{ref}|{role}" for ref, role in sorted(pairs)[:3])
            examples.append(f"{k}: TEI->HTML fehlt: {sample}")
        results.append(CheckResult(
            name=miss_name,
            tei=sum(len(v) for v in missing_pairs.values()),
            json=0,
            status="mismatch",
            note=(
                f"{len(missing_pairs)} Quellen haben TEI-{entity}-Rollen ohne HTML-Pendant. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name=miss_name, tei=0, json=0, status="match",
        ))

    if extra_pairs:
        examples = []
        for k, pairs in list(extra_pairs.items())[:3]:
            sample = ", ".join(f"{ref}|{role}" for ref, role in sorted(pairs)[:3])
            examples.append(f"{k}: HTML->TEI extra: {sample}")
        results.append(CheckResult(
            name=extra_name,
            tei=0,
            json=sum(len(v) for v in extra_pairs.values()),
            status="mismatch",
            note=(
                f"{len(extra_pairs)} Quellen haben HTML-{entity}-Rollen ohne TEI-Pendant. "
                f"Beispiele: {' | '.join(examples)}"
            ),
        ))
    else:
        results.append(CheckResult(
            name=extra_name, tei=0, json=0, status="match",
        ))
    return results


def _normalize_date(s: str) -> str:
    """Whitespace-Normalisierung; aeussere Klammern strippen. Stadtbuecher-
    Konvention setzt das Datum oft in eckige/runde Klammern, das Frontend
    rendert es ohne — beides ist legitim, deshalb beim Vergleich nicht
    zaehlen."""
    s = " ".join(s.split())
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
    return s


def _dates_equivalent(tei: str, html: str) -> bool:
    """Vergleich nach Normalisierung. Plus: Stadtbuecher-Konvention
    'Eintragsdatum (Originaldatum)' — das Frontend rendert das innere
    Datum, das aeussere ist nur das Buchhaltungsdatum. Wenn HTML das
    eingeklammerte Innen-Datum ist, gilt das als Match."""
    if tei == html:
        return True
    # 'X (Y)' Pattern: das Frontend uebernimmt nur Y
    if "(" in tei and tei.endswith(")"):
        idx = tei.rfind("(")
        inner = tei[idx + 1:-1].strip()
        if inner == html:
            return True
    return False


def check_date_display(pairs: List[DocPair]) -> List[CheckResult]:
    """TEI-Datums-Text (Inhalt des <date>-Knotens) vs. HTML-Datums-Anzeige
    aus dem <title>-Tag. Beide stammen aus derselben TEI-Quelle, sollten
    also identisch sein. Wenn nicht, hat eine Build-Stufe das Datum
    umgeformt — verdaechtig genug fuer einen Mismatch.

    Normalisierung: Whitespace + aeussere Klammern, denn die Stadtbuecher-
    Konvention setzt das Datum oft in Klammern und das Frontend rendert
    es ohne. Das ist keine Drift, sondern eine konsistente Konvention.
    """
    mismatches: List[Dict[str, Any]] = []
    missing_html: List[str] = []
    for pair in pairs:
        tei_date = _normalize_date(pair.tei.date_display or "")
        html_date = _normalize_date(pair.html.date_display or "")
        if not tei_date:
            continue
        if not html_date:
            missing_html.append(pair.tei.file_key)
            continue
        if not _dates_equivalent(tei_date, html_date):
            mismatches.append({
                "id": pair.tei.file_key,
                "tei": tei_date,
                "html": html_date,
            })

    results: List[CheckResult] = []
    if mismatches:
        sample = "; ".join(
            f"{m['id']}: TEI='{m['tei']}' HTML='{m['html']}'" for m in mismatches[:3]
        )
        results.append(CheckResult(
            name="teihtml.date_display_vs_tei",
            tei=0,
            json=len(mismatches),
            status="mismatch",
            note=f"Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="teihtml.date_display_vs_tei",
            tei=0, json=0, status="match",
        ))

    if missing_html:
        results.append(CheckResult(
            name="teihtml.date_display_html_missing",
            tei=0,
            json=len(missing_html),
            status="mismatch",
            note=(
                "Quellen mit TEI-Datum, aber leerem HTML-date_display: "
                + _sample(missing_html)
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.date_display_html_missing",
            tei=0, json=0, status="match",
        ))
    return results


def check_pair_coverage(
    pairs: List[DocPair], orphans: List[parse_tei.DocRecord]
) -> List[CheckResult]:
    """Gegenpaarung: wieviele TEI-Dokumente haben kein HTML-Pendant?

    Erwartet: alle freigegebenen TEI-Quellen werden auch gerendert. Wenn nicht,
    ist das ein known_gap mit Liste der ausgelassenen Stems — das deckt die
    Pipeline-Filterung (z. B. `filenames.csv`-Exklusion in Stadtbuecher) auf.
    """
    results: List[CheckResult] = []
    results.append(CheckResult(
        name="teihtml.pair_coverage.documents_paired",
        tei=len(pairs) + len(orphans),
        json=len(pairs),
        status="info",
        note=f"{len(orphans)} TEI-Quellen ohne HTML-Pendant",
    ))
    if orphans:
        keys = [o.file_key for o in orphans]
        results.append(CheckResult(
            name="teihtml.pair_coverage.tei_without_html",
            tei=len(orphans),
            json=0,
            status="known_gap",
            note=(
                "Pipeline-Filterung filenames.csv status='in progress' "
                "(noch nicht freigegeben). "
                + _sample(sorted(keys))
            ),
        ))
    else:
        results.append(CheckResult(
            name="teihtml.pair_coverage.tei_without_html",
            tei=0, json=0, status="match",
        ))
    return results


def run_tei_html_checks() -> List[CheckResult]:
    """Alle Stufe-3-Pruefungen in einem Lauf."""
    docs = parse_tei.scan_sources()
    pairs, orphans = _build_pairs(docs)
    results: List[CheckResult] = []
    results.extend(check_pair_coverage(pairs, orphans))
    results.extend(check_person_refs(pairs))
    results.extend(check_org_refs(pairs))
    results.extend(check_place_refs(pairs))
    results.extend(check_event_refs(pairs))
    results.extend(check_person_roles(pairs))
    results.extend(check_org_roles(pairs))
    results.extend(check_date_display(pairs))
    return results
