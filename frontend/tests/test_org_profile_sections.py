"""Regressionsschutz fuer die zwei jung hinzugefuegten Sektionen auf den
Org-Profilseiten: Stiftungsnetzwerk und occ-Netzwerk.

Hintergrund: das Stiftungsnetzwerk-Feature war waehrend einer
Cleanup-Session unbemerkt verloren gegangen (existierte nur auf einem
worktree-agent-Branch, der mit dem Cleanup geloescht wurde). Kein Test
hatte das gemerkt, weil die bisherigen Tests nur Aggregator-Strukturen
und generelle Render-Funktionalitaet prueften, nicht die konkrete
Anwesenheit von Sektionen auf konkreten Profilen.

Diese Tests pruefen gegen das echte gebaute ``docs/``. Wenn der
Build noch nicht gelaufen ist, werden sie geskippt.
"""

from pathlib import Path

import pytest

DOCS_REGISTER = Path(__file__).parent.parent.parent / "docs" / "register" / "orgs"

# Zwei Org-Profile, die exemplarisch fuer die zwei Welten stehen:
# - St. Agnes auf der Himmelpforte: kleines Frauenkloster, Mail-Frage 4
#   (Issuer-Recipient-Konstellation, beantwortet von Stiftungsnetzwerk).
# - St. Stephan: grosse Hauptkirche mit vielen Personen mit
#   Taetigkeitsverbindung, Mail-Frage 3 (occ-Netzwerk plus Verwandte).
AGNES = DOCS_REGISTER / "org__wien-st_agnes_auf_der_himmelpforte.html"
STEPHAN = DOCS_REGISTER / "org__wien-st_stephan.html"


def _read(path: Path) -> str:
    if not path.exists():
        pytest.skip(f"{path} fehlt; bitte `python -m frontend build` ausfuehren")
    return path.read_text(encoding="utf-8")


def test_stiftungsnetzwerk_section_on_agnes():
    """St. Agnes muss die Stiftungsnetzwerk-Sektion mit erwarteten Sub-Tabellen tragen.

    Konkrete Erwartung aus dem Aggregator-Lauf: 13 Stifter-Personen,
    1 Stifter-Organisation, 14 Empfaenger-Personen. Empfaenger-Orgs
    leer, also wird die vierte Sub-Tabelle nicht gerendert (defensives
    Rendering, siehe org.html Sektion org-funding).
    """
    html = _read(AGNES)
    assert 'class="org-funding"' in html, (
        "Stiftungsnetzwerk-Sektion fehlt auf St. Agnes. "
        "Pruefen: frontend/aggregator/org_profiles._build_funding_network, "
        "frontend/templates/org.html (Sektion org-funding)."
    )
    assert "Stiftungsnetzwerk" in html
    # Sub-Tabellen-Headings (aus funding_table-Aufrufen in org.html).
    assert "Stifter (Personen)" in html
    assert "Stifter (Organisationen)" in html
    assert "Empfaenger (Personen)" in html
    # Empfaenger (Organisationen) ist datenseitig leer und wird nicht
    # gerendert.
    assert "Empfaenger (Organisationen)" not in html


def test_occ_section_on_stephan():
    """St. Stephan muss die occ-Netzwerk-Sektion tragen.

    Erwartung aus dem Aggregator-Lauf: ueber 100 Personen mit
    Taetigkeitsverbindung. Genauere Zahlen werden absichtlich nicht
    hartcodiert, weil sie sich mit jedem Pipeline-Lauf aendern koennen.
    Statt einer harten Anzahl wird die Anwesenheit der Sektion plus
    eine plausible Mindest-Zahl an Tabellenzeilen geprueft.
    """
    html = _read(STEPHAN)
    assert 'class="org-occ-network"' in html, (
        "occ-Sektion fehlt auf St. Stephan. "
        "Pruefen: frontend/aggregator/org_profiles._build_occ_network, "
        "frontend/templates/org.html (Sektion org-occ-network), "
        "frontend/templates/macros.html (occ_table)."
    )
    assert "T&auml;tigkeitsverbindung" in html or "Taetigkeitsverbindung" in html
    # Spalten-Header aus dem occ_table-Macro.
    assert "Beruf / T&auml;tigkeit / Amt" in html
    assert "Verwandtschaft" in html
    # Plausible Mindest-Zahl von Personen-Zeilen. St. Stephan hat sehr
    # viele occ-Personen; falls weniger als 50 erscheinen, ist
    # vermutlich die Sub-Org-Hierarchie verloren gegangen oder die
    # Sub-Tabelle ist truncatet.
    rel_other_link_count = html.count('class="rel-other-link rel-other-link--person"')
    assert rel_other_link_count >= 50, (
        f"Nur {rel_other_link_count} Personen-Links in St. Stephan, "
        "erwartet mindestens 50. Pruefen: ist die Sub-Org-Hierarchie im "
        "Aggregator korrekt aggregiert?"
    )


def test_stiftungsnetzwerk_kein_funding_section_wenn_leer():
    """Org-Profile ohne Stiftungs-Daten sollen die Sektion nicht rendern.

    Defensive-rendering-Garantie: org.html hat
    `{% if (funding.total or 0) > 0 %}`. Findet sich ein Profil ohne
    Funding, soll keine leere Sektion herumstehen.

    Stichprobe: irgendein anderes Org-Profil ausser den beiden grossen.
    Wenn keines gefunden wird oder alle Funding haben, wird der Test
    geskippt, weil dann nichts zu pruefen ist.
    """
    if not DOCS_REGISTER.exists():
        pytest.skip("docs/register/orgs/ fehlt")
    # Suche ein kleines Org-Profil ohne org-funding-Klasse.
    for path in sorted(DOCS_REGISTER.glob("org__*.html"))[:50]:
        html = path.read_text(encoding="utf-8")
        if 'class="org-funding"' not in html:
            # Sektion ist nicht da. Sicherstellen, dass auch der Heading
            # nicht da ist (Defensiv-Rendering greift).
            assert "Stiftungsnetzwerk</h2>" not in html, (
                f"{path.name}: Heading 'Stiftungsnetzwerk' ohne "
                "umschliessende Sektion gerendert."
            )
            return
    pytest.skip("Keine Org-Profile ohne org-funding gefunden in Stichprobe")
