"""Regression test: Im Org-Profil darf 'Personen mit Beruf / Amt'
nicht parallel zu 'Personen mit Taetigkeitsverbindung' rendern.
Die occ-Relationen wandern komplett in den aggregierten Block,
sonst entstand eine sichtbare Block-Dopplung im Single-Person-Fall
(siehe Screenshot Burg Kufstein im Stakeholder-Review).
"""

from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

SAMPLES = [
    "register/orgs/org__kufstein-burg.html",
    "register/orgs/org__wien-st_stephan.html",
]


@pytest.mark.parametrize("rel_path", SAMPLES)
def test_no_occ_relations_block(rel_path):
    path = DOCS_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    text = path.read_text(encoding="utf-8")
    assert "Personen mit Beruf / Amt" not in text, (
        f"Block 'Personen mit Beruf / Amt' darf nicht mehr rendern in "
        f"{rel_path} (aggregiert jetzt in 'Personen mit "
        f"Taetigkeitsverbindung'-Block)."
    )


@pytest.mark.parametrize("rel_path", SAMPLES)
def test_taetigkeitsverbindung_block_remains(rel_path):
    path = DOCS_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    text = path.read_text(encoding="utf-8")
    assert "Personen mit T\xe4tigkeitsverbindung" in text or \
        "Personen mit T&auml;tigkeitsverbindung" in text, (
        f"Aggregations-Block 'Personen mit Taetigkeitsverbindung' "
        f"muss in {rel_path} weiter rendern."
    )
