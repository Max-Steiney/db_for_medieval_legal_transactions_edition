"""Stakeholder-Protokoll A.5.2: Personennetzwerk

Tests sichern die A.5.2-Antworten:
- Quellen direkt verlinkt (Source-Chips statt Beleg-Count)
- Beziehungsbegriffe ueberpruefbar (raw + normalisierte Form)
- Shift+Pfeiltaste extendiert den Brush im Zeitstrom ueber mehrere Spalten
- Layout: Filter horizontal oben, Graph und Tabelle nebeneinander
- Akteursnetzwerk: Personen und Organisationen sind gleichwertige
  Mittelpunkte, relations.json liefert orgs[] mit lesbaren Namen.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class TestNetworkSourceChips:
    """exploration-network.js rendert Quellen-Chips statt Belege-Count."""

    def setup_method(self):
        self.js = _read(ROOT / "static" / "js" / "exploration-network.js")

    def test_collects_normalised_label(self):
        assert "labelsNorm" in self.js, "ln-Form muss pro Edge gesammelt werden"
        assert "r.ln" in self.js

    def test_renders_source_chip(self):
        assert "net-source-chip" in self.js, "Source-Chip-Render fehlt"
        assert "net-source-chips" in self.js

    def test_uses_docs_lookup_for_chip_label(self):
        assert "DOCS_LOOKUP[fk]" in self.js or "DOCS_LOOKUP[" in self.js

    def test_lookup_loaded_before_first_render(self):
        assert "loadDocsLookup" in self.js
        assert ".finally(" in self.js, (
            "renderActive muss in finally laufen, damit Chips aufloesen"
        )

    def test_template_column_header_is_quellen(self):
        tpl = _read(ROOT / "templates" / "exploration_network.html")
        assert ">Quellen<" in tpl
        assert ">Belege<" not in tpl


class TestNetworkLabelVerifiability:
    """Bezeichnungs-Spalte zeigt raw plus normalisierte Form, sofern verschieden."""

    def setup_method(self):
        self.js = _read(ROOT / "static" / "js" / "exploration-network.js")

    def test_label_cell_renders_norm(self):
        assert "renderLabelCell" in self.js
        assert "net-label-norm" in self.js


class TestNetworkLayoutV2:
    """Phase 1: Graph und Detail-Tabelle stehen nebeneinander, Filter
    sitzen in einer horizontalen Leiste oberhalb des Layouts."""

    def setup_method(self):
        self.tpl = _read(ROOT / "templates" / "exploration_network.html")

    def test_no_more_index_sidebar(self):
        assert 'index-sidebar' not in self.tpl, (
            "Filter-Sidebar wurde durch horizontale Filter-Leiste ersetzt"
        )

    def test_filterbar_present_above_layout(self):
        assert 'explore-net-filterbar' in self.tpl
        bar_pos = self.tpl.index('explore-net-filterbar')
        layout_pos = self.tpl.index('explore-net-layout')
        assert bar_pos < layout_pos, "Filter-Leiste muss vor dem Grid stehen"

    def test_two_column_layout_wrapper(self):
        assert 'explore-net-layout' in self.tpl

    def test_filterbar_holds_search_and_chips_and_reset(self):
        bar = self.tpl[self.tpl.index('explore-net-filterbar'):
                       self.tpl.index('explore-net-layout')]
        assert 'id="net-person-search"' in bar
        assert 'id="net-type-filter"' in bar
        assert 'id="filter-reset"' in bar

    def test_active_filters_inside_filterbar(self):
        """A.5.2-Wunsch: aktive Filter sollen in derselben Leiste sichtbar
        sein, nicht in einem separaten Strip oberhalb."""
        bar = self.tpl[self.tpl.index('explore-net-filterbar'):
                       self.tpl.index('explore-net-layout')]
        assert 'active_filters()' in bar, (
            "active_filters-Macro muss innerhalb der Filter-Leiste stehen"
        )


class TestAkteursnetzwerk:
    """Phase 2: Organisationen sind klickbare Mittelpunkte, relations.json
    liefert orgs[] mit lesbaren Anzeigenamen aus organisations.csv."""

    def test_relations_json_has_orgs_array(self):
        for name in ("docs", "docs-intern"):
            path = ROOT.parent / name / "data" / "relations.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "orgs" in data, f"{name}/data/relations.json fehlt orgs[]"
            orgs = data["orgs"]
            assert len(orgs) > 0
            for o in orgs[:3]:
                assert o["id"].startswith("org__")
                assert o["name"] and o["name"] != o["id"], (
                    "Anzeigenamen muessen aus organisations.csv kommen, "
                    "nicht aus dem Slug"
                )

    def test_js_uses_actor_index(self):
        js = _read(ROOT / "static" / "js" / "exploration-network.js")
        assert "const ACTORS" in js, "Gemeinsamer Akteurs-Index fehlt"
        assert "RELATIONS.orgs" in js, "orgs[] muss in den Index uebernommen werden"

    def test_js_supports_org_recentering(self):
        js = _read(ROOT / "static" / "js" / "exploration-network.js")
        # Inverse-Edges-Aufbau: Org-Edges werden aus Personen-Edges gespiegelt.
        assert "Inverse Edges" in js or "orgEdges" in js
        assert "data-org" in js
        # recenter akzeptiert Personen- und Org-Keys.
        assert "ACTORS.has(key)" in js

    def test_template_hint_mentions_orgs(self):
        tpl = _read(ROOT / "templates" / "exploration_network.html")
        hint_chunk = tpl[tpl.index('explore-network-hint'):]
        assert "Organisation" in hint_chunk


class TestNetworkTooltipsAndLegend:
    """Phase 3: Edges und Nodes haben data-hint (hint.js-Tooltips, kein
    SVG-title mehr), Beziehungstyp-Filter zeigen farbige Swatches und
    sind zugleich Legende."""

    def setup_method(self):
        self.js = _read(ROOT / "static" / "js" / "exploration-network.js")
        self.tpl = _read(ROOT / "templates" / "exploration_network.html")
        self.css = _read(ROOT / "static" / "css" / "exploration.css")

    def test_edge_uses_data_hint_not_title(self):
        assert 'data-hint=' in self.js
        # Native SVG <title> ist projektweit raus, hint.js styled konsistent.
        assert '<title>' not in self.js, (
            "SVG <title> kollidiert mit hint.js und sieht in jedem Browser anders aus"
        )

    def test_node_hint_includes_kind_label(self):
        assert "data-hint-type=" in self.js
        assert "nodeHintText" in self.js

    def test_filter_chip_has_swatch(self):
        assert 'net-type-swatch' in self.tpl
        # CSS-Selektor pro Beziehungstyp existiert
        for t in ("kin", "occ", "rep", "friend"):
            assert f'[data-net-type="{t}"]' in self.css

    def test_filter_chips_have_hint_explanations(self):
        for t in ("kin", "occ", "rep", "friend"):
            field = self.tpl[self.tpl.index(f'data-net-type="{t}"'):]
            chunk = field[:300]
            assert 'data-hint=' in chunk, (
                f"Filter-Chip {t} braucht data-hint mit Klartext-Erklaerung"
            )


class TestZeitstromShiftArrow:
    """Shift+Pfeiltaste verschiebt Fokus auf die Nachbar-Spalte und erweitert
    den Brush wiederholbar."""

    def setup_method(self):
        self.js = _read(ROOT / "static" / "js" / "exploration-timeline.js")

    def test_shift_arrow_uses_target_decade(self):
        assert "targetDec" in self.js, "Shift+Arrow muss Schritt vom Ziel berechnen"

    def test_shift_arrow_moves_focus(self):
        assert "next.focus()" in self.js or ".focus();" in self.js
        assert "explore-stream-col[data-decade=" in self.js
