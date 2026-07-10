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


def test_geschlecht_filter_umbenannt_ohne_none():
    # A4: Filter heisst jetzt "Geschlecht der Beteiligten", die Option
    # "ohne Personen" (value none) ist entfernt, weil sie keine
    # Geschlechts-Aussage ist.
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert "Geschlecht der Beteiligten" in html
    assert "Geschlechter-Mix" not in html
    assert ">ohne Personen<" not in html
    src = INDEX_JS.read_text(encoding="utf-8")
    assert "sex === 'none'" not in src, (
        "Die none-Variante (ohne Personen) ist im Sex-Filter zurueck (A4)."
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


def test_korpus_chips_verbergen_nullwerte():
    # Offene Punkte 09.07.2026: Nullwerte ausgefilterter Kategorien nicht
    # dauerhaft anzeigen. Die Korpus-Chips muessen wie alle anderen
    # Filtergruppen ueber _setChipHidden ausgeblendet werden, sobald ihr
    # Live-Count unter den aktiven Filtern 0 ist (aktiver Chip bleibt).
    src = INDEX_JS.read_text(encoding="utf-8")
    corpus_fn = src.split("function updateCorpusCounts()")[1].split("function ")[0]
    assert "_setChipHidden(chip, n)" in corpus_fn, (
        "updateCorpusCounts() blendet Chips mit Count 0 nicht mehr aus; "
        "tote '(0)'-Chips bleiben dann dauerhaft sichtbar."
    )


def test_quelle_ohne_erschliessungsform_bekommt_platzhalter_pille():
    # Offene Punkte 09.07.2026: 66 Quellen ohne Form zeigten gar kein Symbol,
    # was wie ein Datenfehler wirkt. Die Zeile traegt jetzt eine explizite
    # Platzhalter-Pille (gestrichelter Kreis) mit Erklaer-Tooltip.
    src = INDEX_JS.read_text(encoding="utf-8")
    assert "if (!doc.ecR && !doc.ecS && !doc.ecE && !doc.ecN) {" in src
    assert "'Ohne Erschließungsform'" in src.split("function renderContent")[1].split("function ")[0]
    assert "stroke-dasharray" in src, (
        "Das Platzhalter-Icon (FORM_ICONS.x) fehlt."
    )


def test_preview_meta_nennt_fehlende_erschliessungsform():
    src = INDEX_JS.read_text(encoding="utf-8")
    assert "noch keine (Aufarbeitung offen)" in src, (
        "Der Vorschau-Meta-Streifen verschweigt fehlende Erschliessungsformen wieder."
    )


def test_chip_hidden_regel_existiert():
    # Live-Befund 10.07.2026: der Korpus-Chip blieb trotz chip.hidden=true
    # mit "(0)" stehen, weil '.chip { display: inline-flex }' die
    # UA-Regel '[hidden] { display: none }' ueberstimmt. Gegenregel noetig,
    # analog zu '.form-filter-chip[hidden]'.
    css = (_ROOT / "static" / "css" / "index.css").read_text(encoding="utf-8")
    assert ".chip[hidden]" in css, (
        "Die Gegenregel .chip[hidden] { display: none } fehlt; "
        "0-Treffer-Korpus-Chips bleiben dann sichtbar."
    )
