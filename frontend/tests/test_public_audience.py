"""Regression test: Analyse and Exploration sections must be marked
as .dev-only in the public build. CSS hides them by default; ?dev=1
makes them visible. Stakeholder decision: Protokoll 18.05.2026
Teil A Punkt 1.
"""

from pathlib import Path

import pytest
from lxml import html as lxml_html

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


def _parse(rel_path: str):
    path = DOCS_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    return lxml_html.fromstring(path.read_text(encoding="utf-8"))


def test_nav_analyse_dropdown_is_dev_only():
    tree = _parse("index.html")
    dropdowns = tree.xpath("//div[contains(@class, 'nav-dropdown')]")
    analyse = [
        d for d in dropdowns
        if (d.xpath("string(.//button)") or "").strip().startswith("Analyse")
    ]
    assert analyse, "Analyse-Dropdown not found in nav"
    for d in analyse:
        assert "dev-only" in (d.get("class") or ""), (
            "Analyse-Dropdown must carry the dev-only class"
        )


def test_nav_exploration_dropdown_is_dev_only():
    tree = _parse("index.html")
    dropdowns = tree.xpath("//div[contains(@class, 'nav-dropdown')]")
    exploration = [
        d for d in dropdowns
        if (d.xpath("string(.//button)") or "").strip().startswith("Exploration")
    ]
    assert exploration, "Exploration-Dropdown not found in nav"
    for d in exploration:
        assert "dev-only" in (d.get("class") or ""), (
            "Exploration-Dropdown must carry the dev-only class"
        )


def test_startseite_twoways_section_is_dev_only():
    tree = _parse("index.html")
    sections = tree.xpath("//section[contains(@class, 'start-twoways')]")
    assert sections, "start-twoways section not found"
    for s in sections:
        assert "dev-only" in (s.get("class") or ""), (
            "start-twoways section (Analyse/Exploration hub) must carry dev-only"
        )


def test_register_dropdown_is_not_dev_only():
    tree = _parse("index.html")
    dropdowns = tree.xpath("//div[contains(@class, 'nav-dropdown')]")
    register = [
        d for d in dropdowns
        if (d.xpath("string(.//button)") or "").strip().startswith("Register")
    ]
    assert register, "Register-Dropdown not found in nav"
    for d in register:
        assert "dev-only" not in (d.get("class") or ""), (
            "Register-Dropdown must remain visible in the public view"
        )
