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
    _, content = built_guidelines
    assert "Editionsrichtlinien" in content


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


def test_has_kontrolliertes_vokabular_section(built_guidelines):
    _, content = built_guidelines
    assert "Kontrolliertes Vokabular" in content


# --- New tests for redesigned layout ---


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
    # "3.530" may appear in the Versionsgeschichte changelog as a historical datum,
    # but must not appear in the Projektkontext or Annotationsmodell sections.
    import re
    # Find all occurrences and ensure they are only within the Versionsgeschichte section
    sections_before_changelog = content.split("Versionsgeschichte")[0]
    assert "3.530" not in sections_before_changelog


def test_statistics_reference(built_guidelines):
    """Guidelines reference the statistics page for dynamic metrics."""
    _, content = built_guidelines
    assert "statistics.html" in content


def test_has_zitierhinweis_section(built_guidelines):
    """Section 8: Zitierhinweis exists with citation block."""
    _, content = built_guidelines
    assert "Zitierhinweis" in content
    assert "Wiener Urkundenbuch" in content


def test_has_lizenz_section(built_guidelines):
    """Section 9: Lizenz exists with CC-BY-4.0 link."""
    _, content = built_guidelines
    assert "CC BY 4.0" in content or "CC-BY-4.0" in content or "creativecommons.org" in content


def test_has_versionsgeschichte_section(built_guidelines):
    """Section 10: Versionsgeschichte exists with changelog entries."""
    _, content = built_guidelines
    assert "Versionsgeschichte" in content
