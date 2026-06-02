"""Globaler "Gesamten Datenkorb leeren"-Button auf der Korb-Seite.
Source-Guards gegen Markup und Verdrahtung."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
KORB_HTML = _ROOT / "templates" / "korb.html"
PAGE_JS = _ROOT / "static" / "js" / "basket-page.js"


def test_clear_all_button_in_header():
    html = KORB_HTML.read_text(encoding="utf-8")
    assert 'id="basket-clear-all"' in html, "Globaler Leeren-Button fehlt."
    assert 'data-action="clear-all"' in html


def test_clear_all_wired_and_clears_everything():
    src = PAGE_JS.read_text(encoding="utf-8")
    assert "basket-clear-all" in src, "Button ist nicht verdrahtet."
    # Leert ohne Typ-Argument, also den gesamten Korb.
    assert "DataBasket.clear();" in src, (
        "clear-all ruft nicht DataBasket.clear() ohne Typ auf."
    )
    assert "confirm(" in src, "Sicherheitsabfrage fehlt vor dem Leeren."


def test_clear_all_hidden_when_empty():
    src = PAGE_JS.read_text(encoding="utf-8")
    assert "clearAll.hidden = (DataBasket.count() === 0)" in src, (
        "Der Button wird im leeren Zustand nicht ausgeblendet."
    )


def test_explore_btn_hidden_attribute_wins():
    # .explore-btn setzt display:inline-flex und schlaegt damit die UA-Regel
    # [hidden]{display:none}. Ohne expliziten Reset bleibt ein explore-btn
    # mit hidden-Attribut sichtbar (Leeren-Button im leeren Korb).
    css = (_ROOT / "static" / "css" / "exploration.css").read_text(encoding="utf-8")
    assert ".explore-btn[hidden] { display: none; }" in css, (
        "Der [hidden]-Reset fuer .explore-btn fehlt; der Leeren-Button "
        "bleibt im leeren Korb sichtbar."
    )
