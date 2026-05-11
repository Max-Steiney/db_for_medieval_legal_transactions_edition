"""Tests fuer verification/compare_tei_html.py.

Smoke-Tests fuer die TEI-direkt-zu-HTML-Coverage. Pruefen, dass die
Mapping-Logik und die Symmetrie-Pruefungen die richtigen CheckResult-
Tupel erzeugen.
"""

from __future__ import annotations

import pytest

from verification import compare_tei_html


@pytest.fixture(scope="module")
def stage3_results():
    """Ein einziger Lauf, von allen Tests geteilt — der Scan ist nicht billig."""
    return compare_tei_html.run_tei_html_checks()


def _by_name(results, name):
    for r in results:
        if r.name == name:
            return r
    raise AssertionError(f"check {name} fehlt im Ergebnis")


def test_pair_coverage_documents_paired(stage3_results):
    """Pair-Coverage soll mehr TEI als HTML zaehlen (siehe filenames.csv-Filterung)
    und ein info-Result fuer die Statistik liefern."""
    r = _by_name(stage3_results, "teihtml.pair_coverage.documents_paired")
    assert r.status == "info"
    assert isinstance(r.tei, int)
    assert isinstance(r.json, int)
    assert r.tei >= r.json  # HTML ist Teilmenge der TEI-Sammlung


def test_pair_coverage_orphans_known_gap(stage3_results):
    """Orphans (TEI ohne HTML) sind erwartete Pipeline-Filterung — known_gap,
    nicht mismatch."""
    r = _by_name(stage3_results, "teihtml.pair_coverage.tei_without_html")
    assert r.status in ("match", "known_gap")


def test_person_refs_symmetry(stage3_results):
    """Persons-Refs sollen in beide Richtungen 1:1 abgebildet werden.
    Aktueller Stand: alle gepaarten Quellen sind symmetrisch."""
    r_missing = _by_name(stage3_results, "teihtml.person_refs.missing_in_html")
    r_extra = _by_name(stage3_results, "teihtml.person_refs.extra_in_html")
    assert r_missing.status == "match", r_missing.note
    assert r_extra.status == "match", r_extra.note


def test_org_refs_symmetry(stage3_results):
    """Org-Refs sollen in beide Richtungen 1:1 abgebildet werden."""
    r_missing = _by_name(stage3_results, "teihtml.org_refs.missing_in_html")
    r_extra = _by_name(stage3_results, "teihtml.org_refs.extra_in_html")
    assert r_missing.status == "match", r_missing.note
    assert r_extra.status == "match", r_extra.note


def test_place_refs_symmetry(stage3_results):
    """Place-Refs: auch fuer Place-Spans muss `data-ref` symmetrisch sein
    (das Ortsregister ist entfernt, aber die Annotationen leben weiter
    im Quellen-Volltext)."""
    r_missing = _by_name(stage3_results, "teihtml.place_refs.missing_in_html")
    r_extra = _by_name(stage3_results, "teihtml.place_refs.extra_in_html")
    assert r_missing.status == "match", r_missing.note
    assert r_extra.status == "match", r_extra.note


def test_html_path_mapping_round_trip():
    """Wenige Smoke-Faelle: TEI-Pfad QGW/.../done/100.xml -> docs/.../100.html."""
    import sys
    sys.path.insert(0, "../db_for_medieval_legal_transactions")
    from verification import parse_tei

    docs = parse_tei.scan_sources()
    by_key = {d.file_key: d for d in docs}

    rec = by_key.get("QGW_Vienna_1177-1414_ready_100")
    assert rec is not None, "Referenz-TEI 100.xml nicht gefunden"

    html_path = compare_tei_html._html_path_for_tei(rec)
    assert html_path is not None
    assert html_path.name == "100.html"
    assert html_path.parent.name == "Vienna_1177-1414_ready"
