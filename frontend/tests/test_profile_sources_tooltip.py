"""Konsistenz-Test fuer den Provenienz-Tooltip an der Quellen-Zahl.

Der Zaehler 'Quellen mit Nennung' auf Personen- und Org-Profilen ist
ein tip_data-Trigger: Hover/Klick auf die Zahl erklaert, wie sie
zustande kommt (namentliche Annotation ODER indirekte Referenz ueber
eine Amtsbezeichnung via roleName-corresp; Mehrfachnennungen pro
Quelle dedupliziert). Der Popover-Body verlinkt auf den Glossar-
Eintrag 'Gesamtnennung', der dieselbe Zaehlregel definiert.

Die Registerlisten-Spalte 'Quellen' zaehlt identisch; ihr Tooltip
traegt dieselbe Erklaerung (Label-Konsistenz-Regel, siehe
knowledge/ui-design.md 'Begriffs- und Label-Konsistenz').
"""

from pathlib import Path


TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent / "templates"
)


def _read(name):
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


class TestProfileSourcesTooltip:
    """person.html und org.html: Zahl als tip_data-Trigger mit Popover."""

    def test_person_count_is_tip_data_trigger(self):
        text = _read("person.html")
        assert "tip_data_trigger('prov-profile-sources')" in text
        assert "tip_data_body('prov-profile-sources'" in text

    def test_org_count_is_tip_data_trigger(self):
        text = _read("org.html")
        assert "tip_data_trigger('prov-profile-sources')" in text
        assert "tip_data_body('prov-profile-sources'" in text

    def test_trigger_wraps_count_badge(self):
        """Die section-head-count-Pille liegt im Trigger, nicht daneben."""
        for name in ("person.html", "org.html"):
            text = _read(name)
            assert ("tip_data_trigger('prov-profile-sources') %}"
                    '<span class="section-head-count">') in text, name

    def test_popover_links_glossar_gesamtnennung(self):
        for name in ("person.html", "org.html"):
            text = _read(name)
            assert "glossary.html#gesamtnennung" in text, name

    def test_popover_explains_rolename_corresp(self):
        """Die indirekte Schiene (roleName-corresp/Amtsbezeichnung) wird
        genannt; sie unterscheidet die Zahl von reiner Namensnennung."""
        for name in ("person.html", "org.html"):
            text = _read(name)
            assert "Amts" in text and "Mehrfachnennungen" in text, name

    def test_org_popover_mentions_suborg_rule(self):
        assert "Unterorganisation" in _read("org.html")

    def test_templates_import_tip_data_macros(self):
        """Import mit 'with context', sonst zeigt der Glossar-Link auf
        GitHub Pages mit Subpfad ins Leere (root_path fehlt)."""
        for name in ("person.html", "org.html"):
            text = _read(name)
            import_line = next(
                line for line in text.splitlines()
                if "from \"macros.html\" import" in line
            )
            assert "tip_data_trigger" in import_line, name
            assert "tip_data_body" in import_line, name
            assert "with context" in import_line, name


class TestRegisterListTooltipAligned:
    """Registerlisten-Tooltip 'Quellen' erklaert dieselbe Zaehlregel."""

    def test_mentions_indirect_reference(self):
        text = _read("register_list.html")
        assert "Amts" in text and "Mehrfachnennungen" in text

    def test_links_glossar_gesamtnennung(self):
        text = _read("register_list.html")
        assert "slug='gesamtnennung'" in text
