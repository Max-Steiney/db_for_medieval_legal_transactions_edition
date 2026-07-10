"""Offene Punkte 09.07.2026: keine ID-Suche in der oeffentlichen Sicht.

Das Register-Suchfeld darf in der oeffentlichen Sicht technische IDs
(pe__/org__) weder als Vorschlag bewerben (Platzhalter, Hilfe-Tooltip)
noch im Such-Haystack matchen. Im internen Build bleibt beides erhalten.
Der Hash-Deep-Link (#pe__id) laeuft ueber state.hashId statt ueber das
Suchfeld, damit die rohe ID nicht im UI auftaucht.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTER_JS = ROOT / "frontend" / "static" / "js" / "register.js"
TEMPLATE = ROOT / "frontend" / "templates" / "register_list.html"
DOCS = ROOT / "docs"


def test_js_haystack_gates_id_on_audience():
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "idSearchable ? (e.id || '') : ''" in src, (
        "Die technische ID steht wieder bedingungslos im Such-Haystack."
    )
    assert "data-audience" in src, (
        "Die Audience-Weiche fuer die ID-Suche fehlt."
    )


def test_js_deep_link_does_not_use_search_box():
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "searchControl.set(targetId)" not in src, (
        "Der Hash-Deep-Link schreibt die rohe ID wieder ins Suchfeld."
    )
    assert "state.hashId = targetId" in src, (
        "Der Hash-Deep-Link laeuft nicht mehr ueber state.hashId; "
        "die Zeile landet sonst nicht sicher im virtualisierten tbody."
    )


def test_template_placeholder_is_audience_conditional():
    src = TEMPLATE.read_text(encoding="utf-8")
    assert "'Name, ID, Jahr ...' if audience.show_entity_ids else 'Name, Jahr ...'" in src
    assert src.count("{% if audience.show_entity_ids %}<li><strong>ID</strong>") == 2


@pytest.mark.parametrize("rel_path", ["register/persons.html", "register/orgs.html"])
def test_public_build_has_no_id_search_hint(rel_path):
    path = DOCS / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    html = path.read_text(encoding="utf-8")
    assert "Name, ID, Jahr" not in html, (
        "Der oeffentliche Build bewirbt die ID-Suche wieder im Platzhalter."
    )
    assert "Name, Jahr ..." in html
    assert "<strong>ID</strong> der konsolidierten" not in html, (
        "Der Hilfe-Tooltip listet die ID im oeffentlichen Build wieder als Suchfeld."
    )
