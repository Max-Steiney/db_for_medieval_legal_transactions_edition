"""Tests fuer die Open-Beta-Begruessungs-Box der Startseite."""

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def test_beta_note_has_project_mail():
    # Echte Projekt-Adresse (Uni Wien, seit 2026-07-20) statt Platzhalter
    src = (BASE / "templates" / "startseite.html").read_text(encoding="utf-8")
    assert 'href="mailto:stadtgemeinschaftwien.ioeg@univie.ac.at"' in src


def test_no_placeholder_mail_anywhere():
    # Der Launch-Platzhalter (PLATZHALTER-MAIL@example.com) darf nirgends
    # mehr auftauchen, auch nicht in Kommentaren.
    for f in list((BASE / "templates").glob("*.html")) + list((BASE / "build").glob("*.py")):
        assert "PLATZHALTER" not in f.read_text(encoding="utf-8"), f.name
