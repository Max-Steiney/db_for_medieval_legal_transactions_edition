"""Guards fuer die Quellen-Liste, Block 1 aus dem Meeting 02.06.2026.

A1 Ort raus aus der Volltextsuche (eigener Ort-Filter bleibt).
A2 Erschliessungsform-Filter aus der Sidebar entfernt.
A3 Faksimile-Filter aus der Sidebar entfernt.

Quelltext-Guards in der Tradition von test_register_js.py: die geaenderten
Stellen liegen im JS-Haystack und im Jinja-Template, nicht in einer pruefbaren
Python-Funktion.
"""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
INDEX_JS = _ROOT / "static" / "js" / "index.js"
INDEX_HTML = _ROOT / "templates" / "index.html"


def test_volltextsuche_enthaelt_keinen_ort():
    src = INDEX_JS.read_text(encoding="utf-8")
    assert "doc.p, doc.id, doc.cl" not in src, (
        "doc.p ist wieder im _s-Haystack: der Ausstellungsort wird dann "
        "doch ueber die Volltextsuche durchsucht (A1)."
    )
    assert "doc.id, doc.cl" in src


def test_suche_placeholder_nennt_keinen_ort():
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert "Signatur, Datum, Regest" in html
    assert "Signatur, Datum, Ort, Regest" not in html


def test_erschliessungsform_filter_entfernt():
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert "filter-forms" not in html, (
        "Der Erschliessungsform-Filter ist wieder in der Sidebar (A2)."
    )


def test_faksimile_filter_entfernt():
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="filter-facs"' not in html, (
        "Der Faksimile-Filter ist wieder in der Sidebar (A3)."
    )


def test_zeitraum_balken_setzt_kein_natives_title():
    # A5: ein natives title-Attribut am Histogramm-Balken erzeugt neben dem
    # eigenen hint.js-Tooltip einen zweiten Browser-Tooltip. Der Balken darf
    # nur data-hint aktualisieren.
    src = INDEX_JS.read_text(encoding="utf-8")
    assert "bar.title" not in src, (
        "Histogramm-Balken setzt wieder ein natives title-Attribut: "
        "zweiter Tooltip neben dem hint.js-Popover (A5)."
    )
