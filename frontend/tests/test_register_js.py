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
