"""Tests for the three-page glossary demo build."""

from pathlib import Path

import pytest

from frontend.build import _build_glossar_demo, _init_jinja


@pytest.fixture(scope="module")
def built_demo(docs_dir):
    env = _init_jinja()
    _build_glossar_demo(env)
    base = docs_dir / "project" / "glossar-demo"
    pages = {p: (base / f"{p}.html") for p in ("glossar", "technik", "tutorial")}
    contents = {}
    for name, path in pages.items():
        assert path.exists(), f"glossar-demo/{name}.html was not generated"
        contents[name] = path.read_text(encoding="utf-8")
    return contents


# --- Task 1: build plumbing / smoke ---

def test_all_three_pages_built(built_demo):
    assert set(built_demo) == {"glossar", "technik", "tutorial"}


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


def test_glossar_event_is_named_entity(built_demo):
    # Kommentar #6: Ereignis auch als Entitaet benennen
    c = built_demo["glossar"].lower()
    assert "ereignis" in c and "entit" in c


def test_glossar_attribut_without_verwandtschaft(built_demo):
    # Kommentar #7: Verwandtschaft NICHT als Attribut-Beispiel
    c = built_demo["glossar"]
    block = c.split("Attribut", 1)[-1].split("</section>")[0] if "Attribut" in c else ""
    assert "Verwandtschaft" not in block[:600]


def test_glossar_has_tooltip_coupling_demo(built_demo):
    c = built_demo["glossar"]
    assert "tip-popover" in c  # Demonstration des echten Tooltip-Looks


def test_glossar_links_to_other_demo_pages(built_demo):
    c = built_demo["glossar"]
    assert "technik.html" in c and "tutorial.html" in c


def test_glossar_witness_and_sealer_separated(built_demo):
    # Kommentar #13/#14: Zeug:in und Siegler:in getrennt, nicht "zusammengefuehrt"
    c = built_demo["glossar"]
    assert "zusammenzuführen" not in c and "zusammenführen" not in c


# --- Task 3: Technik / Datenmodell page ---

def test_technik_has_role_codes(built_demo):
    c = built_demo["technik"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_technik_has_rolename_types(built_demo):
    c = built_demo["technik"]
    for t in ("prof", "title", "dead", "kin", "rep", "occ", "title_ref"):
        assert t in c, t


def test_technik_has_xml_snippet(built_demo):
    c = built_demo["technik"]
    assert "rs type=" in c and "role=" in c


def test_technik_explains_witness_grouping(built_demo):
    # #12/#13: witness fasst siegelnde Zeugen und Aussteller zusammen, Rollen aber getrennt beschrieben
    c = built_demo["technik"].lower()
    assert "witness" in c and "siegel" in c


def test_technik_links_back(built_demo):
    c = built_demo["technik"]
    assert "glossar.html" in c and "tutorial.html" in c


# --- Task 4: Tutorial page (three case examples) ---

CASE_DOCS = ("604", "16", "1869")


def test_tutorial_links_to_three_real_sources(built_demo):
    c = built_demo["tutorial"]
    base = "documents/QGW/Vienna_1177-1414_ready"
    for nr in CASE_DOCS:
        assert f"{base}/{nr}.html" in c, nr


def test_tutorial_case_sources_exist_in_repo():
    # Die drei Fall-Quellen muessen real gebaut vorliegen
    repo = Path(__file__).resolve().parents[2]
    for nr in CASE_DOCS:
        p = repo / "docs" / "documents" / "QGW" / "Vienna_1177-1414_ready" / f"{nr}.html"
        assert p.exists(), p


def test_tutorial_resolves_roles_in_context(built_demo):
    c = built_demo["tutorial"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_tutorial_links_into_glossar_and_technik(built_demo):
    c = built_demo["tutorial"]
    assert "glossar.html" in c and "technik.html" in c


def test_tutorial_case2_not_generically_gendered(built_demo):
    # Kommentar #22: in den Faellen exakte Rollen, kein generisches Gendern.
    # Fall 2 (Nr. 16) hat eine Ausstellerin (Singular feminin) -> "Ausstellerin".
    c = built_demo["tutorial"]
    seg = c.split("16.html", 1)[0][-1200:] + c.split("16.html", 1)[-1][:1200]
    assert "Ausstellerin" in seg


# --- Task 5: cross-linking / integration ---

def test_mutual_cross_links(built_demo):
    # jede Seite verlinkt die beiden anderen
    pairs = {
        "glossar": ("technik.html", "tutorial.html"),
        "technik": ("glossar.html", "tutorial.html"),
        "tutorial": ("glossar.html", "technik.html"),
    }
    for page, targets in pairs.items():
        for t in targets:
            assert t in built_demo[page], f"{page} -> {t}"


def test_glossary_demo_does_not_touch_production(docs_dir):
    # produktive glossary.html wird vom Demo-Build NICHT geschrieben
    assert not (docs_dir / "project" / "glossary.html").exists()


def test_pages_link_demo_css(built_demo):
    for name, c in built_demo.items():
        assert "static/css/glossar-demo.css" in c, name


def test_md_sources_have_no_inline_style():
    from pathlib import Path
    base = Path(__file__).resolve().parents[1] / "content" / "project" / "glossar-demo"
    for name in ("glossar", "technik", "tutorial"):
        md = (base / f"{name}.md").read_text(encoding="utf-8")
        assert "<style>" not in md, name


def test_demo_css_asset_exists():
    from pathlib import Path
    css = Path(__file__).resolve().parents[1] / "static" / "css" / "glossar-demo.css"
    assert css.exists()
    body = css.read_text(encoding="utf-8")
    # Kern-Klassen der drei Seiten muessen abgedeckt sein
    for cls in (".demo-pagenav", ".demo-tip-demo", ".demo-case", ".demo-editnote",
                ".tech-codes", ".roleName-grid", ".dev-only"):
        assert cls in body, cls


# --- Task 2: slug-konforme Rollen-Ueberschriften ---

def test_glossar_role_headings_are_clean():
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project"
          / "glossar-demo" / "glossar.md").read_text(encoding="utf-8")
    for line in md.splitlines():
        if line.startswith("### "):
            for alias in ("(issuer)", "(recipient)", "(witness)", "(other)"):
                assert alias not in line, line


def test_glossar_role_codes_present_in_body(built_demo):
    c = built_demo["glossar"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_glossar_role_anchor_not_drifted(built_demo):
    # Der Anker der Aussteller:in-Ueberschrift darf den Code nicht enthalten
    c = built_demo["glossar"]
    assert 'id="ausstellerin-issuer"' not in c
    assert 'id="aussteller-in-issuer"' not in c
