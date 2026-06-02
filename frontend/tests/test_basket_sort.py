"""Korb-Tabellen sortierbar und im index-table-Stil der Register.
Source-Guards gegen Markup und Sortier-Verdrahtung."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
KORB_HTML = _ROOT / "templates" / "korb.html"
PAGE_JS = _ROOT / "static" / "js" / "basket-page.js"


def test_tables_use_index_table_style():
    html = KORB_HTML.read_text(encoding="utf-8")
    # Alle drei Sektions-Tabellen tragen den Register-Tabellenstil.
    assert html.count('class="index-table basket-table"') == 3, (
        "Nicht alle Korb-Tabellen nutzen index-table (Konsistenz mit Registern)."
    )
    assert "aggregat-table basket-table" not in html, (
        "Eine Korb-Tabelle haengt noch am alten aggregat-table-Stil."
    )


def test_sortable_columns_declared():
    html = KORB_HTML.read_text(encoding="utf-8")
    for key in ('data-sort="idno"', 'data-sort="date"', 'data-sort="coll"',
                'data-sort="name"', 'data-sort="sex"', 'data-sort="active"',
                'data-sort="type"'):
        assert key in html, f"Sortier-Spalte fehlt: {key}"


def test_sex_column_compact_like_register():
    # Geschlecht im Korb als Kurzform m/w wie im Personen-Register,
    # nicht ausgeschrieben (Label-Konsistenz).
    src = PAGE_JS.read_text(encoding="utf-8")
    assert "it.sex === 'm' ? 'm' : it.sex === 'f' ? 'w'" in src, (
        "Korb-Geschlechtsspalte ist nicht die Kurzform m/w wie das Register."
    )
    assert "männlich" not in src and "weiblich" not in src, (
        "Korb schreibt das Geschlecht wieder aus."
    )


def test_sort_wired_in_page_js():
    src = PAGE_JS.read_text(encoding="utf-8")
    assert "sortState" in src and "thead th[data-sort]" in src, (
        "Die Spalten-Sortierung ist nicht an die Header gebunden."
    )
    assert "EdCore.compareValues" in src, (
        "Sortierung nutzt nicht den geteilten Vergleichs-Helfer."
    )
    assert "sorted-asc" in src and "sorted-desc" in src, (
        "Sort-Indikator-Klassen werden nicht gesetzt."
    )


def test_derived_org_type_uses_normalised_label():
    # Abgeleitete Organisationen im Korb zeigen das normalisierte Label
    # (tpl aus demselben label_org_type-Code), nicht den Rohcode (Kloster_m).
    basket = (_ROOT / "static" / "js" / "basket.js").read_text(encoding="utf-8")
    assert "o.tpl || o.tp" in basket, (
        "Abgeleitete Org nimmt wieder den Rohcode statt des tpl-Labels."
    )
    docs_py = (_ROOT / "aggregator" / "docs.py").read_text(encoding="utf-8")
    assert '"tpl": row.get("tpl"' in docs_py, (
        "docs_entities.json reicht das normalisierte tpl-Label nicht durch."
    )
