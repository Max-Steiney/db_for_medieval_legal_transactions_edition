"""Konsistenz-Test fuer den Spalten-Header in Profil-Quellen-Tabellen.

Personen- und Org-Profil-Quellen-Tabellen heissen 'Funktionsrolle',
nicht 'Rolle'. Begruendung: edition-guidelines-kanonischer Begriff,
disambiguiert gegen Verwandtschafts-, Berufs- und Trigger-Rollen.

Analyse-Templates (analysis.html, analysis_aggregat.html) sind hier
absichtlich nicht erfasst; sie nutzen 'Rolle' im Kontext einer
Sektion, deren Header bereits 'Funktionsrollen' nennt.
"""

import re
from pathlib import Path


TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent / "templates"
)


class TestProfileRoleHeader:
    """person.html und org.html tragen 'Funktionsrolle' als Header."""

    def test_person_template_funktionsrolle(self):
        text = (TEMPLATES_DIR / "person.html").read_text(encoding="utf-8")
        assert 'data-sort="role">Funktionsrolle</th>' in text

    def test_org_template_funktionsrolle(self):
        text = (TEMPLATES_DIR / "org.html").read_text(encoding="utf-8")
        assert 'data-sort="role">Funktionsrolle</th>' in text

    def test_kein_nacktes_rolle_in_profil_quellen_spalte(self):
        """Schutz gegen Re-Drift: kein '>Rolle<' im data-sort=role-Header
        der Profil-Templates."""
        for name in ("person.html", "org.html"):
            text = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
            assert not re.search(
                r'data-sort="role">\s*Rolle\s*</th>', text
            ), f"{name} traegt wieder 'Rolle' im Funktionsrollen-Spalten-Header"
