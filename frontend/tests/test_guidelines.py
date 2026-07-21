"""Tests for the edition guidelines page build."""

import pytest
from pathlib import Path

from frontend.build import _build_guidelines, _init_jinja


@pytest.fixture(scope="module")
def built_guidelines(docs_dir):
    """Build the guidelines page into the shared temp docs directory."""
    env = _init_jinja()
    _build_guidelines(env)

    output = docs_dir / "project" / "edition-guidelines.html"
    assert output.exists(), "project/edition-guidelines.html was not generated"
    content = output.read_text(encoding="utf-8")
    return output, content


def test_has_doctype(built_guidelines):
    _, content = built_guidelines
    assert content.startswith("<!DOCTYPE html>")


def test_has_title(built_guidelines):
    """Seite heisst seit der Ueberarbeitung "Annotationsrichtlinien"."""
    _, content = built_guidelines
    assert "Annotationsrichtlinien" in content
    assert "Editionsrichtlinien" not in content


def test_has_toc_container(built_guidelines):
    _, content = built_guidelines
    assert 'class="guidelines-toc"' in content


def test_has_body_container(built_guidelines):
    _, content = built_guidelines
    assert 'class="guidelines-body"' in content


def test_has_annotationsmodell_section(built_guidelines):
    _, content = built_guidelines
    assert "Annotationsmodell" in content


def test_has_id_konstruktionsregeln_section(built_guidelines):
    _, content = built_guidelines
    assert "ID-Konstruktionsregeln" in content


def test_has_richtlinien_nav_link(built_guidelines):
    _, content = built_guidelines
    assert "edition-guidelines.html" in content
    assert "richtlinien" in content


def test_has_xml_code_examples(built_guidelines):
    _, content = built_guidelines
    assert "rs type=" in content or 'rs type="event"' in content


def test_has_validierung_section(built_guidelines):
    """Abschnitt 6 heisst seit dem Meeting 21.07.2026 "Validierung"
    (vorher "Vokabular und Validierung", davor "Kontrolliertes
    Vokabular")."""
    _, content = built_guidelines
    assert 'id="6-validierung"' in content
    assert "Kontrolliertes Vokabular" not in content


# --- Tests for redesigned layout ---


def test_has_sidebar(built_guidelines):
    """Sidebar wrapper element exists."""
    _, content = built_guidelines
    assert 'id="guidelines-sidebar"' in content


def test_quickref_cards_removed(built_guidelines):
    """Quick-reference cards were removed."""
    _, content = built_guidelines
    assert 'class="guidelines-quickref"' not in content


def test_has_guidelines_layout(built_guidelines):
    """Two-column layout wrapper exists."""
    _, content = built_guidelines
    assert 'id="guidelines-layout"' in content


def test_section5_removed(built_guidelines):
    """Old Section 5 'Funktionsrollen und Relationstypen' was removed."""
    _, content = built_guidelines
    assert "Funktionsrollen und Relationstypen" not in content


def test_section7_removed(built_guidelines):
    """Old Section 7 'Kurationslogik' was removed."""
    _, content = built_guidelines
    assert "Kurationslogik" not in content


def test_no_stale_file_count(built_guidelines):
    """Hardcoded corpus count '3.530' only appears in historical changelog, not in running text."""
    _, content = built_guidelines
    # "3.530" may appear in the Versionsgeschichte changelog as a historical
    # datum, but must not appear in the Projektkontext or Annotationsmodell
    # sections.
    import re
    sections_before_changelog = content.split("Versionsgeschichte")[0]
    assert "3.530" not in sections_before_changelog


def test_no_dead_datengrundlage_reference(built_guidelines):
    """The dead Datengrundlage reference must stay removed.

    A datengrundlage.html page was never built. The canonical guidelines
    source (sister repo, commit fa187242d1, 2026-05-30 "tote
    Datengrundlage-Verweise entfernen") dropped all references to it. This
    guard keeps the dead link from silently reappearing in the rendered page.
    """
    _, content = built_guidelines
    assert "datengrundlage.html" not in content


def test_has_zitierhinweis_section(built_guidelines):
    """Section 8: Zitierhinweis exists with citation block."""
    _, content = built_guidelines
    assert "Zitierhinweis" in content
    assert "Stadt und Gemeinschaft Wien" in content


def test_has_lizenz_section(built_guidelines):
    """Abschnitt 8: einheitliche Lizenz CC BY-NC-SA 4.0 mit CC-Link
    (Meeting-Entscheidung 21.07.2026)."""
    _, content = built_guidelines
    assert "CC BY-NC-SA 4.0" in content
    assert "creativecommons.org" in content


def test_versionsgeschichte_removed(built_guidelines):
    """Versionsgeschichte bewusst entfernt: keine Vogeler-Auflage
    verlangt sie, Versionierung leistet die Git-Historie des
    Daten-Repos (analog test_section5_removed/test_section7_removed)."""
    _, content = built_guidelines
    assert "Versionsgeschichte" not in content
