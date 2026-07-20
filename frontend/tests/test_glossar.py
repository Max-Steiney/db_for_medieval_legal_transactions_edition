"""Tests for the production glossary page (glossary.html).

technik.md und tutorial.md sind archiviert/passiv (Stand 2026-07-17) und
werden nicht mehr gerendert: die technische TEI-Auszeichnung ist in den
Annotationsrichtlinien dokumentiert, die drei Zaehlbegriffe sind ins Glossar
ueberfuehrt. Die frueheren Technik-/Tutorial-Tests entfallen entsprechend.
"""

from pathlib import Path

import pytest

from frontend.build import _build_glossary, _init_jinja


@pytest.fixture(scope="module")
def built_demo(docs_dir):
    env = _init_jinja()
    _build_glossary(env)
    base = docs_dir / "project"
    pages = {"glossar": base / "glossary.html"}
    contents = {}
    for name, path in pages.items():
        assert path.exists(), f"project/{path.name} was not generated"
        contents[name] = path.read_text(encoding="utf-8")
    return contents


# --- Task 1: build plumbing / smoke ---

def test_glossar_built(built_demo):
    assert set(built_demo) == {"glossar"}


def test_pages_have_native_chrome(built_demo):
    for name, content in built_demo.items():
        assert content.startswith("<!DOCTYPE html>"), name
        # base.html chrome marker: the project work name appears in header/footer
        assert "Stadt und Gemeinschaft Wien" in content, name


# --- Task 2: Glossar page ---

def test_glossar_has_core_terms(built_demo):
    c = built_demo["glossar"]
    for term in ("Quelle", "Quellenkorpus", "Event", "Entit", "Rolle",
                 "Annotation", "Regest", "Rechtsgesch"):
        assert term in c, term


def test_glossar_has_zaehlbegriffe(built_demo):
    # Gesamtnennung + Individuelle Person aus der (archivierten) Technik-Seite
    # ins Glossar ueberfuehrt (2026-07-17). Menschen-Event vorerst NICHT
    # aufgenommen (kein UI-Element, das ihn surfaced); wird nachgezogen, wenn
    # der Ein-/Ausschluss-Filter im UI existiert.
    c = built_demo["glossar"]
    for term in ("Gesamtnennung", "Individuelle Person"):
        assert term in c, term
    assert "Menschen-Event" not in c


def test_glossar_normierung_entry(built_demo):
    # Normierung-Eintrag: Anker ist Ziel des surname_added-Popovers auf den
    # Personen-Profilen (person.html -> glossary.html#normierung). Inhalt am
    # 20.07.2026 neu gefasst (weibliche Namensform statt <add>-Verweis);
    # rohe, unescapte TEI-Tags duerfen nie im Output landen (Browser wuerde
    # sie verschlucken).
    c = built_demo["glossar"]
    assert 'id="normierung"' in c
    assert "weiblichen Form" in c
    assert "einem <add>" not in c


def test_glossar_event_is_named_entity(built_demo):
    # Kommentar #6: Ereignis auch als Entitaet benennen
    c = built_demo["glossar"].lower()
    assert "ereignis" in c and "entit" in c


def test_glossar_attribut_without_verwandtschaft(built_demo):
    # Kommentar #7: Verwandtschaft NICHT als Attribut-Beispiel
    c = built_demo["glossar"]
    block = c.split("Attribut", 1)[-1].split("</section>")[0] if "Attribut" in c else ""
    assert "Verwandtschaft" not in block[:600]


def test_glossar_tooltip_preview_removed(built_demo):
    # Tooltip-Vorschau-Block entfernt (Stakeholder 2026-07-08)
    c = built_demo["glossar"]
    assert "demo-tip-demo" not in c
    assert "tip-popover" not in c


def test_glossar_links_to_guidelines_not_technik(built_demo):
    # technik.html ist archiviert/passiv (2026-07-17); der Verweis geht jetzt
    # auf die Annotationsrichtlinien.
    c = built_demo["glossar"]
    assert "edition-guidelines.html" in c
    assert "technik.html" not in c
    assert "tutorial.html" not in c


def test_glossar_witness_and_sealer_separated(built_demo):
    # Kommentar #13/#14: Zeug:in und Siegler:in getrennt, nicht "zusammengefuehrt"
    c = built_demo["glossar"]
    assert "zusammenzuführen" not in c and "zusammenführen" not in c


# --- Technik / Datenmodell: Seite archiviert/passiv (2026-07-17) ---
# technik.md wird nicht mehr gerendert; die frueheren, an die gebaute
# Technik-Seite gekoppelten Tests (Rollen-Codes, roleName-Typen, XML-Snippet,
# witness-Gruppierung, Rueckverlinkung) entfallen. Der technische Inhalt lebt
# jetzt in den Annotationsrichtlinien; die md-Quelle bleibt als ruhendes Archiv.


# --- Tutorial vorerst aus der Demo genommen (Stakeholder 2026-07-08) ---
# Tutorial-/Fallbeispiel-Tests entfallen, bis das Tutorial mit den Fallstudien
# wieder aufgenommen wird. tutorial.md bleibt als ruhende Quelle erhalten.

# --- Task 5: cross-linking / integration ---

def test_glossar_cross_links_guidelines(built_demo):
    # Das Glossar verlinkt auf die Annotationsrichtlinien (technik archiviert).
    assert "edition-guidelines.html" in built_demo["glossar"]


def test_pages_link_glossar_css(built_demo):
    for name, c in built_demo.items():
        assert "static/css/glossar.css" in c, name


def test_md_sources_have_no_inline_style():
    from pathlib import Path
    base = Path(__file__).resolve().parents[1] / "content" / "project"
    for name in ("glossar", "technik"):
        md = (base / f"{name}.md").read_text(encoding="utf-8")
        assert "<style>" not in md, name


def test_glossar_css_asset_exists():
    from pathlib import Path
    css = Path(__file__).resolve().parents[1] / "static" / "css" / "glossar.css"
    assert css.exists()
    body = css.read_text(encoding="utf-8")
    # Kern-Klassen der drei Seiten muessen abgedeckt sein
    for cls in (".glossar-pagenav", ".demo-tip-demo", ".demo-case", ".demo-editnote",
                ".tech-codes", ".roleName-grid", ".dev-only"):
        assert cls in body, cls


# --- Task 2: slug-konforme Rollen-Ueberschriften ---

def test_glossar_role_headings_are_clean():
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project" / "glossar.md").read_text(encoding="utf-8")
    for line in md.splitlines():
        if line.startswith("### "):
            for alias in ("(issuer)", "(recipient)", "(witness)", "(other)"):
                assert alias not in line, line


def test_glossar_role_code_lines_removed():
    # Demo-eigene "Code-Wert"-Zeilen entfernt (Stakeholder 2026-07-08); die Codes leben auf der Technik-Seite.
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project" / "glossar.md").read_text(encoding="utf-8")
    assert "Code-Wert im Datenmodell" not in md
    for code in ("issuer", "recipient", "witness"):
        assert code not in md, code
    # `other` bleibt nur, weil der .docx-Grundherr-Eintrag ihn nennt ("Sammelrolle other")
    assert "`other`" in md


def test_glossar_role_anchor_not_drifted(built_demo):
    # Der Anker der Aussteller:in-Ueberschrift darf den Code nicht enthalten
    c = built_demo["glossar"]
    assert 'id="ausstellerin-issuer"' not in c
    assert 'id="aussteller-in-issuer"' not in c


def test_glossar_has_reference_lines(built_demo):
    c = built_demo["glossar"]
    assert 'class="entry-refs"' in c
    # Beschriftungen der Referenz-Zeilen
    assert "Weiterführend" in c
    assert "Literatur" in c
    assert "Verwandt" in c


def test_glossar_has_external_links(built_demo):
    c = built_demo["glossar"]
    assert "adfontes.uzh.ch" in c
    assert "geschichtewiki.wien.gv.at" in c


def test_glossar_internal_first_mention_links(built_demo):
    # Der Event-Eintrag selbst verlinkt intern auf #quelle (Selbst-Verlinkung).
    c = built_demo["glossar"]
    # Ausschnitt vom Event-Heading bis zum naechsten <h3>
    start = c.find('id="event"')
    assert start != -1, "Event-Heading fehlt"
    seg = c[start:]
    nxt = seg.find("<h3", 3)
    seg = seg[:nxt] if nxt != -1 else seg
    assert 'href="#quelle"' in seg, "Event-Eintrag verlinkt nicht auf #quelle"


def test_glossar_event_heading_clean_slug(built_demo):
    # '### Event' -> id="event"; kein Slug-Drift durch '/ Ereignis'
    c = built_demo["glossar"]
    assert 'id="event"' in c
    assert 'id="event--ereignis"' not in c


def test_entry_refs_styled_in_css():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "css" / "glossar.css").read_text(encoding="utf-8")
    assert ".entry-refs" in css


def test_tooltip_preview_reset_positioning():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "css" / "glossar.css").read_text(encoding="utf-8")
    # Der Demo-Override muss die absolute-Positionierung der echten tip.css neutralisieren
    block = css.split(".demo-tip-demo .tip-popover", 1)[-1].split("}", 1)[0]
    assert "transform: none" in block
    assert "animation: none" in block
    assert "left: auto" in block


# --- Task 2 (D/E/F): neue Abschnitte ---

def test_glossar_has_sections_def(built_demo):
    c = built_demo["glossar"]
    for term in ("Stadtrat", "Bürgermeister", "Richter", "Bürgerschranne",
                 "Rechtsgeschäft", "Verkauf", "Schenkung", "Stiftung",
                 "Verpfändung", "Darlehen", "Urteil", "Offener Brief",
                 "Wiener Pfennig", "Gulden", "Joch", "Burgrecht"):
        assert term in c, term


def test_glossar_def_references(built_demo):
    c = built_demo["glossar"]
    assert "Czeike" in c
    assert ("Geyer" in c) or ("Ertl" in c)
    assert "geschichtewiki.wien.gv.at/Schranne" in c
    assert "geschichtewiki.wien.gv.at/Kaufkraftrechner" in c


def test_glossar_gender_doppelpunkt():
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project" / "glossar.md").read_text(encoding="utf-8")
    assert "*in" not in md  # kein Gender-Stern aus dem .docx
    assert "Bürger:in" in md


# --- Task 3: inflected/plural internal links ---

def test_beziehung_links_to_entitat(built_demo):
    c = built_demo["glossar"]
    idx = c.find('id="beziehung"')
    assert idx != -1, "Beziehung-Heading fehlt"
    seg = c[idx:idx + 500]
    assert 'href="#entitat"' in seg, "Beziehung verlinkt nicht auf Entität"


# --- Import des finalen .docx: gesperrte Invarianten ---

def test_glossar_quellenkorpus_erfassungsstand(built_demo):
    # Final: QGW/Uhlirz als aktueller Korpus, Erfassungsstand 1177–1414, Monasterium-Link
    c = built_demo["glossar"]
    assert "Erfassungsstand" in c
    assert "1177" in c and "1414" in c
    assert "monasterium.net" in c
    assert "Uhlirz" in c


def test_glossar_hofmeister_removed(built_demo):
    # Final entfernt Hofmeister:in aus Abschnitt D
    assert "Hofmeister" not in built_demo["glossar"]


def test_glossar_section_b_expanded(built_demo):
    # Ausbau-Saetze aus Abschnitt B (Urkunde/Edition/Vidimus) + AdFontes-Sammelglossar
    c = built_demo["glossar"]
    for term in ("Privaturkunden", "Transsumpt", "Textzeugen"):
        assert term in c, term
    assert "adfontes.uzh.ch/glossar" in c


def test_glossar_section_e_expanded(built_demo):
    c = built_demo["glossar"]
    assert "imareal.sbg.ac.at" in c            # Brauneder/Neschwara-Glossar (Intro E)
    assert "Vogtbarkeit" in c                  # Geschaeftsfaehigkeits-Absatz
    assert ("Messstiftung" in c) or ("Altarpfründe" in c)
    # Grundzins und Burgrecht liegen in Abschnitt E (aus F verschoben)
    assert "Grundzins" in c and "Burgrecht" in c


def test_glossar_all_eight_roles(built_demo):
    c = built_demo["glossar"]
    for role in ("Aussteller:in", "Empfänger:in", "Einbringer:in", "Zeug:in",
                 "Siegler:in", "Grundherr:in", "Erblasser:in",
                 "Testamentsvollstrecker:in"):
        assert role in c, role


def test_glossar_section_c_heading(built_demo):
    assert "C. Rollen in Rechtsgeschäften" in built_demo["glossar"]


def test_no_gender_star_in_any_source():
    base = Path(__file__).resolve().parents[1] / "content" / "project"
    for name in ("glossar", "technik"):
        md = (base / f"{name}.md").read_text(encoding="utf-8")
        assert "*in" not in md, name


def test_technik_case2_sealer_has_witness_code():
    # Konsistenz: alle drei Faelle geben fuer die Siegler-Funktion den Code witness an.
    # Pruefung an der .md-Quelle (das gerenderte HTML enthaelt ein TOC mit gleichen Titeln).
    md = (Path(__file__).resolve().parents[1] / "content" / "project" / "technik.md").read_text(encoding="utf-8")
    seg = md.split("Benedicta de Arnstain", 1)[-1].split("Fallbeispiel 3", 1)[0]
    assert "Siegler" in seg and "witness" in seg
    # kein isoliertes "(sealer)" ohne witness in irgendeinem Fall
    assert "(sealer)" not in md


def test_glossar_section_f_mirrors_docx_structure(built_demo):
    # Abschnitt F folgt der .docx-Gliederung (Kategorien + Legende + Erlaeuterungen),
    # nicht der frueheren Pro-Begriff-Paraphrase (Stakeholder-Entscheidung 2026-07-07).
    c = built_demo["glossar"]
    for header in ("Recheneinheiten vs. Umlaufsmünze",
                   "Weitere Silbermünzen",
                   "Goldmünzen als"):
        assert header in c, header
    # woertliche Abkuerzungs-Legende
    for token in ("denarius", "libra", "solidus", "240 denarii"):
        assert token in c, token
    # Inhalte vollstaendig erhalten
    assert "Schinderlingszeit" in c and "Quadratklafter" in c and "Zentner" in c


def test_glossar_has_literaturverzeichnis(built_demo):
    # Abschnitt G: konsolidiertes Literaturverzeichnis (neu in der .docx-Fassung 2026-07-08)
    c = built_demo["glossar"]
    assert "G. Literaturverzeichnis" in c
    for cite in ("Uhlirz", "Brauneder", "Jaritz", "Neschwara", "Czeike",
                 "Geyer", "Ertl", "Perger"):
        assert cite in c, cite
    # beide QGW-Baende erfasst
    assert "1239" in c and "1411" in c
    assert "1412" in c and "1457" in c


def test_glossar_event_drops_gerichtsverfahren(built_demo):
    # Final 2026-07-08: Event-Beispiele ohne Gerichtsverfahren
    c = built_demo["glossar"]
    start = c.find('id="event"')
    seg = c[start:c.find("<h3", start + 3)]
    assert "Gerichtsverfahren" not in seg


# --- Struktur 2026-07-17: Technik + Tutorial archiviert/passiv ---

def test_no_tutorial_references_in_glossar():
    # Keine Tutorial-Links/-Mentions in der aktiven Glossar-Quelle
    base = Path(__file__).resolve().parents[1] / "content" / "project"
    md = (base / "glossar.md").read_text(encoding="utf-8")
    assert "tutorial.html" not in md
    assert "Tutorial" not in md


def test_glossar_intro_links_guidelines(built_demo):
    # Intro verlinkt jetzt auf die Annotationsrichtlinien (technik archiviert).
    c = built_demo["glossar"]
    assert "edition-guidelines.html" in c
    assert "Annotationsrichtlinien" in c
    assert "technisches Glossar" not in c


# --- Produktiv-Integration 2026-07-10 ---

def test_glossar_in_project_nav(built_demo):
    # Glossar ist im Projekt-Dropdown verlinkt; Technik (in Arbeit) bewusst nicht
    c = built_demo["glossar"]
    assert 'href="../project/glossary.html"' in c
    assert '/project/technik.html"' not in c.split('nav-links')[1].split('</nav>')[0]


def test_ui_glossary_slugs_have_anchors(built_demo):
    # Jeder slug=... aus Templates/_kpi muss als Anker existieren
    import re
    base = Path(__file__).resolve().parents[1]
    referenced = set()
    for f in list((base / "templates").glob("*.html")) + [base / "build" / "_kpi.py"]:
        referenced.update(re.findall(r"slug='([a-z0-9-]+)'", f.read_text(encoding="utf-8")))
        referenced.update(re.findall(r'"glossary_slug": "([a-z0-9-]+)"', f.read_text(encoding="utf-8")))
    anchors = set(re.findall(r'id="([a-z0-9-]+)"', built_demo["glossar"]))
    missing = referenced - anchors
    assert not missing, f"UI verlinkt Glossar-Anker, die nicht existieren: {sorted(missing)}"
