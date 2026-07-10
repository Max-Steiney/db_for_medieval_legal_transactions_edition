"""Offene Punkte 09.07.2026: Hover-Infos anhand des neuen Glossars.

Nach dem Einspielen des Partner-Glossars darf kein tip_glossary-Tooltip mehr
den Platzhalter "Definition in redaktioneller Ueberarbeitung" tragen; die
Texte folgen der jeweiligen Glossar-Definition. Die Content-Seite about.md
bleibt bewusst aussen vor (eigener redaktioneller Platzhalter, kein Tooltip).
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent / "docs"

PLACEHOLDER = "Definition in redaktioneller"


def test_keine_platzhalter_tooltips_in_templates():
    hits = []
    for f in (ROOT / "templates").glob("*.html"):
        if PLACEHOLDER in f.read_text(encoding="utf-8"):
            hits.append(f.name)
    if PLACEHOLDER in (ROOT / "build" / "_kpi.py").read_text(encoding="utf-8"):
        hits.append("_kpi.py")
    assert not hits, (
        f"Platzhalter-Tooltips zurueckgekehrt in: {hits}. "
        "Texte anhand von frontend/content/project/glossar.md fuellen."
    )


@pytest.mark.parametrize("rel_path", [
    "index.html", "documents.html", "register/persons.html",
])
def test_keine_platzhalter_tooltips_im_build(rel_path):
    path = DOCS / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    assert PLACEHOLDER not in path.read_text(encoding="utf-8")
