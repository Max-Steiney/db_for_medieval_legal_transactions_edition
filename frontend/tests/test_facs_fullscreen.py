"""B1: Vollbild-Button im Faksimile-Viewer, links von Zoom +/-.
Source-Guards gegen Markup, Verdrahtung und CSS."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
DOC_HTML = _ROOT / "templates" / "document.html"
FACS_JS = _ROOT / "static" / "js" / "facsimile.js"
DOC_CSS = _ROOT / "static" / "css" / "document.css"


def test_fullscreen_button_before_zoom():
    html = DOC_HTML.read_text(encoding="utf-8")
    fs = html.find("facs-fullscreen")
    zin = html.find("facs-zoom-in")
    assert fs != -1, "Vollbild-Button fehlt im Markup (B1)."
    assert fs < zin, "Vollbild-Button steht nicht links von Zoom + (B1)."


def test_fullscreen_wired_to_native_api():
    src = FACS_JS.read_text(encoding="utf-8")
    assert "requestFullscreen" in src and "exitFullscreen" in src, (
        "Vollbild-Button ist nicht an die Fullscreen-API verdrahtet (B1)."
    )


def test_fullscreen_css_rule_present():
    css = DOC_CSS.read_text(encoding="utf-8")
    assert ".facs-viewer:fullscreen" in css, (
        "CSS-Regel fuer den Vollbild-Zustand fehlt (B1)."
    )
