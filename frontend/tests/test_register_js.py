"""Guard: der aktive Rollen-Filter-Chip im Register zeigt ein deutsches Label.

Regression zu register.js:622: dort wurde ROLE_LABELS[r].long auf einer
flachen String-Map gelesen, was immer undefined ergab und den Chip auf den
rohen Schluessel (issuer/recipient/witness/other) zuruckfallen liess. Das
verstiess gegen "keine technischen IDs im oeffentlichen UI". Die Wording- und
Gender-Vereinheitlichung der Rollen-Labels ist eine offene Stakeholder-
Entscheidung (siehe doc.md) und nicht Gegenstand dieses Tests.
"""

from pathlib import Path

REGISTER_JS = Path(__file__).resolve().parents[1] / "static" / "js" / "register.js"


def test_role_filter_chip_uses_label_not_raw_key():
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "ROLE_LABELS[r].long" not in src, (
        "Der kaputte .long-Zugriff auf die flache ROLE_LABELS-Map ist zurueck; "
        "der Filter-Chip zeigt dann wieder den rohen Schluessel."
    )
    assert "ROLE_LABELS[r] || r" in src, (
        "Der Rollen-Filter-Chip soll das deutsche Label aus ROLE_LABELS nutzen."
    )


def test_org_type_column_uses_normalised_label():
    # Tabellenspalte und Datenkorb sollen das normalisierte Label (tpl) zeigen,
    # nicht den rohen Code (tp). Guard zur Einheitlichkeit ueber alle Stellen.
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "entry.tpl || entry.tp" in src, (
        "Die Org-Typ-Spalte faellt wieder auf den rohen Code zurueck."
    )


def test_org_type_chips_resort_by_live_count():
    # Unter einem aktiven Filter sollen die Typ-Chips nach der aktuell
    # sichtbaren Zahl umsortiert werden (Sammelposten OTHER/leer ans Ende),
    # damit nicht eine kleinere Zahl ueber einer groesseren steht.
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "typeChips.sort(" in src, (
        "Die Typ-Chips werden nicht mehr dynamisch nach Zahl sortiert; "
        "die feste Build-Reihenfolge ist zurueck (Burg 3 ueber Orden 1)."
    )


def test_zeitraum_balken_setzt_kein_natives_title():
    # A5: doppelter Tooltip am Zeitraum-Histogramm. Der Balken darf kein
    # natives title-Attribut setzen, nur data-hint aktualisieren.
    src = REGISTER_JS.read_text(encoding="utf-8")
    assert "bar.title" not in src, (
        "Histogramm-Balken setzt wieder ein natives title-Attribut: "
        "zweiter Tooltip neben dem hint.js-Popover (A5)."
    )
