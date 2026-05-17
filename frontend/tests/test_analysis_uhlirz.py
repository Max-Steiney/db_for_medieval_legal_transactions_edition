"""Test fuer die Uhlirz-Achse in der Konstellations-Abfrage-UI.

Setzt auf dem Aggregator-Test test_role_constellation_uhlirz.py auf:
wenn role_constellation.json die u-Liste pro Person traegt, muss die
UI das filterbar machen. Erwartet wird, dass in der Personen-Bedingungs-
Tabelle pro Zeile zusaetzlich zu Rolle, Geschlecht und Beruf-Substring
ein Uhlirz-Filter angeboten wird.

Konkrete Erwartungen ans gebaute analysis/index.html:
- Spalten-Header "Uhlirz-Berufsklasse" in qb-persons-table.
- Pro Beispiel-Chip-Definition im JS bleibt die Welt unveraendert
  (die u-Filter sind optional, alte Chips funktionieren weiter).
- data-uhlirz-vocab am qb-persons-table mit JSON-Array der Kategorien.
"""

from pathlib import Path

import pytest

DOC_HTML = (
    Path(__file__).parent.parent.parent / "docs" / "analysis" / "index.html"
)


def _read():
    if not DOC_HTML.exists():
        pytest.skip("docs/analysis/index.html fehlt; bitte build laufen lassen")
    return DOC_HTML.read_text(encoding="utf-8")


def test_analysis_has_uhlirz_column_header():
    """Die Personen-Bedingungs-Tabelle hat einen Uhlirz-Spaltenkopf."""
    html = _read()
    assert "Uhlirz" in html, (
        "Spaltenkopf 'Uhlirz...' fehlt in analysis/index.html. "
        "Pruefen: frontend/templates/analysis.html, qb-persons-table thead."
    )


def test_analysis_has_uhlirz_vocab_data_attribute():
    """Das Vokabular liegt am qb-persons-table als data-uhlirz-vocab.

    Analog zu data-occupation-vocab. Resolver-JS liest es einmal und
    fuettert die Dropdown-Optionen.
    """
    html = _read()
    assert "data-uhlirz-vocab" in html, (
        "data-uhlirz-vocab fehlt am qb-persons-table. "
        "Pruefen: frontend/templates/analysis.html und "
        "frontend/build/_pages.py::_build_analysis (uhlirz-Vocab muss "
        "ans Template gereicht werden)."
    )
    # Mindestens eine Roemische-Ziffer-Kategorie muss im JSON-Array
    # vorkommen, damit das Dropdown nicht leer ist.
    assert "Geistliche Berufe" in html or "Verwaltung" in html, (
        "Uhlirz-Vokabular wirkt leer im HTML. Pruefen: "
        "role_constellation.json vocab.uhlirz und Template-Renderpath."
    )
