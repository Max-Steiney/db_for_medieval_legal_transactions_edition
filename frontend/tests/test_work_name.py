"""Guard gegen den alten Projektnamen in den ausgelieferten JS-Modulen.

Das Projekt hiess frueher "Wiener Urkundenbuch". M3 hat die zitierfaehigen
Ausgaben (Chicago, BibTeX) und Datei-Header auf den aktuellen Werknamen
"Stadt und Gemeinschaft Wien" gezogen. Diese Tests halten das fest, damit der
alte Name nicht ueber einen kopierten Header zurueckkehrt.
"""

from pathlib import Path

JS_DIR = Path(__file__).resolve().parents[1] / "static" / "js"


def test_no_old_work_name_in_js():
    offenders = [
        p.name for p in sorted(JS_DIR.glob("*.js"))
        if "Wiener Urkundenbuch" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, (
        f"Alter Projektname 'Wiener Urkundenbuch' noch in: {offenders}. "
        f"Werkname ist 'Stadt und Gemeinschaft Wien'."
    )


def test_citation_uses_current_work_name():
    src = (JS_DIR / "document.js").read_text(encoding="utf-8")
    assert "Stadt und Gemeinschaft Wien" in src, (
        "Zitier-Helfer nennt den aktuellen Werknamen nicht."
    )
    # alter BibTeX-Key-Praefix darf nicht mehr vorkommen
    assert "WUB_" not in src
    # neuer Schluessel-Praefix vorhanden
    assert "SuGW_" in src
