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


def test_occ_terms_normalised_basel():
    """occ-Schreibweisen werden auf die inhaltliche Normalform gezogen.

    Peter von Aspelt ist mit org__basel-dioezese in zwei Quellen verbunden:
    Quelle 27 als Wortlaut "pischolf", Quelle 28 als "Bischof". Die occ-Spalte
    darf nur die Normalform "Bischof" zeigen, nicht "Bischof, pischolf"
    (Meeting 2026-06-17); die Belege bleiben unveraendert zwei.
    """
    path = DOCS_ROOT / "register/orgs/org__basel-dioezese.html"
    if not path.exists():
        pytest.skip("build artifact not found")
    text = path.read_text(encoding="utf-8")
    m = re.search(
        r'data-sort-value="Peter von Aspelt".*?'
        r'<td class="rel-col-occ" data-sort-value="([^"]*)"',
        text,
        re.DOTALL,
    )
    assert m is not None, (
        "Peter-von-Aspelt-Zeile im occ-Netzwerk von Basel nicht gefunden"
    )
    occ = m.group(1)
    assert "pischolf" not in occ, (
        f'occ-Spalte zeigt noch die Rohschreibung: "{occ}" '
        f'(erwartet normalisiert auf "Bischof").'
    )
    assert "Bischof" in occ, (
        f'occ-Spalte zeigt nicht die Normalform "Bischof": "{occ}"'
    )
