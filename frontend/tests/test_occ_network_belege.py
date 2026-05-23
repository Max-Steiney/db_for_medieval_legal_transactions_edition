"""Regression test: Belege-Spalte im 'Personen mit Taetigkeits-
verbindung'-Block muss die tatsaechliche Anzahl der Belege zeigen,
nicht 0. Bug-Quelle: _build_occ_network nutzte (collection_path, idno)
-> file_key-Lookup mit file_key als query, was strukturell nicht
hitten konnte.
"""

import re
from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


def test_kufstein_phleger_has_one_beleg():
    path = DOCS_ROOT / "register/orgs/org__kufstein-burg.html"
    if not path.exists():
        pytest.skip("build artifact not found")
    text = path.read_text(encoding="utf-8")
    m = re.search(
        r'data-sort-value="phleger".*?'
        r'<td class="rel-col-count" data-sort-value="(\d+)"',
        text,
        re.DOTALL,
    )
    assert m is not None, (
        "phleger-Zeile im occ-Netzwerk von Kufstein nicht gefunden"
    )
    count = int(m.group(1))
    assert count >= 1, (
        f"Belege-Zaehler fuer Rudolf von Rosenheim (phleger zu "
        f"Kufstein) ist {count}, sollte mindestens 1 sein "
        f"(Quelle 223a belegt ihn)."
    )
