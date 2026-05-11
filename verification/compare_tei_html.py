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
    oder Stadtbuecher-Eintraege, die `filenames.csv` ausschliesst)."""
    paired: List[DocPair] = []
    orphans: List[parse_tei.DocRecord] = []
    for rec in docs:
        path = _html_path_for_tei(rec)
        if path is None:
            orphans.append(rec)
            continue
        html_doc = parse_html.read_document(path)
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
    return results
