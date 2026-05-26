"""Regression test: der Public-Build (docs/) darf weder Analyse- noch
Exploration-Seiten enthalten und die Nav-Bar einer beliebigen
Public-Seite darf keine Links auf /analysis/ oder /exploration/ tragen.

Stakeholder-Anforderung 18.05.2026: klare Trennung zwischen oeffentlich
sichtbaren Bereichen und intern zugaenglichen experimentellen Funktionen.
Der Schalter sitzt in frontend.audiences (show_analysis_section,
show_exploration_section) und wird in frontend/build/__init__.py und in
templates/base.html abgefragt.
"""

from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

FORBIDDEN_DIRS = ("analysis", "exploration")
SAMPLE_NAV_PAGES = [
    "index.html",
    "documents.html",
    "register/persons.html",
    "register/orgs.html",
    "impressum.html",
]


def test_public_build_has_no_analysis_dir():
    if not DOCS_ROOT.exists():
        pytest.skip("docs/ noch nicht gebaut")
    assert not (DOCS_ROOT / "analysis").exists(), (
        "docs/analysis/ existiert im Public-Build. "
        "Der Schalter audience.show_analysis_section wird ignoriert."
    )


def test_public_build_has_no_exploration_dir():
    if not DOCS_ROOT.exists():
        pytest.skip("docs/ noch nicht gebaut")
    assert not (DOCS_ROOT / "exploration").exists(), (
        "docs/exploration/ existiert im Public-Build. "
        "Der Schalter audience.show_exploration_section wird ignoriert."
    )


@pytest.mark.parametrize("rel_path", SAMPLE_NAV_PAGES)
def test_public_nav_has_no_analysis_or_exploration_links(rel_path):
    page = DOCS_ROOT / rel_path
    if not page.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    text = page.read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_DIRS:
        assert f"/{forbidden}/" not in text, (
            f"{rel_path} verweist im Public-Build auf /{forbidden}/. "
            "Nav-Eintrag muss audience-conditional sein."
        )


def test_public_register_dropdown_stays_visible():
    """Gegenprobe: Register-Dropdown darf nicht versehentlich miteliminiert
    werden. Wenn der Audience-Refactor die Bedingungen schief verdrahtet,
    faellt hier auf, dass Register aus der Nav verschwindet.
    """
    page = DOCS_ROOT / "index.html"
    if not page.exists():
        pytest.skip("docs/index.html noch nicht gebaut")
    text = page.read_text(encoding="utf-8")
    assert "/register/persons.html" in text, "Personen-Register-Link fehlt"
    assert "/register/orgs.html" in text, "Org-Register-Link fehlt"
