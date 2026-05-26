"""Stakeholder-Protokoll A.5.2: Personennetzwerk

Tests sichern die A.5.2-Antworten:
- Quellen direkt verlinkt (Source-Chips statt Beleg-Count)
- Beziehungsbegriffe ueberpruefbar (raw + normalisierte Form)
- Shift+Pfeiltaste extendiert den Brush im Zeitstrom ueber mehrere Spalten
"""

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
