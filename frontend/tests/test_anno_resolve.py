"""B3: die Annotationstabelle loest Pronomen/Bezugswoerter zur Person aus
dem Register auf ("identifiziert als <Name>"); die technische ID erscheint
nur im internen Build oder mit ?dev=1. Source-Guards gegen document.js/CSS."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
DOC_JS = _ROOT / "static" / "js" / "document.js"
DOC_CSS = _ROOT / "static" / "css" / "document.css"


def test_resolved_name_captured_and_rendered():
    src = DOC_JS.read_text(encoding="utf-8")
    assert "resolved: (entity.getAttribute('data-hint')" in src
    assert "resolved: (el.getAttribute('data-hint')" in src
    assert "identifiziert als " in src, (
        "Die Annotationstabelle zeigt den aufgeloesten Registernamen nicht (B3)."
    )


def test_id_only_internal_or_dev():
    src = DOC_JS.read_text(encoding="utf-8")
    assert "data-audience') === 'intern'" in src, (
        "Die ID-Anzeige ist nicht an den internen Build gekoppelt (B3)."
    )
    assert "showIds && f.ref" in src, (
        "Die ID wird nicht nur unter showIds gerendert (B3)."
    )


def test_resolve_css_present():
    css = DOC_CSS.read_text(encoding="utf-8")
    assert ".anno-resolved" in css and ".anno-ref" in css
