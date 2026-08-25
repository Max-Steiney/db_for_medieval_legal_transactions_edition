"""Bulk-Add auf den Profilseiten: ein Knopf im Kopf der Sektion "Quellen mit
Nennung" uebernimmt alle dort gelisteten Quellen auf einmal in den Datenkorb.

Geprueft werden das gemeinsame Macro (Render-Test gegen die echte
Template-Datei) sowie die Verdrahtung in Templates, basket.js, basket-mount.js
und CSS (Source-Guards)."""

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = _ROOT / "templates"
BASKET_JS = _ROOT / "static" / "js" / "basket.js"
MOUNT_JS = _ROOT / "static" / "js" / "basket-mount.js"
MACROS_HTML = TEMPLATES / "macros.html"
PERSON_HTML = TEMPLATES / "person.html"
ORG_HTML = TEMPLATES / "org.html"
COMPONENTS_CSS = _ROOT / "static" / "css" / "components.css"
PERSON_CSS = _ROOT / "static" / "css" / "person.css"

# Eine Quelle in der Form, wie profile.sources sie liefert.
SOURCE = {
    "idno": "QGW II/1 123",
    "url": "documents/qgw_123.html",
    "date_iso": "1380-05-01",
    "date_display": "1. Mai 1380",
    "collection_label": "QGW II/1",
    "regest": "Ulrich verkauft <ein> Haus & Hof.",
}


def _render_macro(sources):
    """Rendert sources_bulk_mount isoliert, mit der Env-Konfiguration des
    Builds (autoescape=False, siehe frontend/build/_helpers._init_jinja)."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    tmpl = env.from_string(
        "{% from 'macros.html' import sources_bulk_mount %}"
        "{{ sources_bulk_mount(sources) }}"
    )
    return tmpl.render(sources=sources)


def _payload_from(html):
    m = re.search(
        r'<script type="application/json" class="basket-bulk-data">(.*?)</script>',
        html, re.S,
    )
    assert m, f"Kein Payload-Block im Macro-Output: {html!r}"
    return json.loads(m.group(1))


def test_macro_renders_mount_and_payload():
    html = _render_macro([SOURCE])
    assert 'class="basket-bulk-mount"' in html, (
        "Der Platzhalter fuer den Bulk-Knopf fehlt."
    )
    assert 'class="basket-bulk-data"' in html, (
        "Der JSON-Payload-Block fehlt."
    )


def test_macro_payload_fields_match_basket_field_form():
    payload = _payload_from(_render_macro([SOURCE]))
    assert payload == [{
        "id": "QGW II/1 123",
        "label": "QGW II/1 123",
        "url": "documents/qgw_123.html",
        "date": "1380-05-01",
        "coll": "QGW II/1",
        "regest": "Ulrich verkauft <ein> Haus & Hof.",
    }], "Die Payload-Feldform weicht vom Einzel-Mount (document.html) ab."


def test_macro_payload_falls_back_to_display_date():
    src = dict(SOURCE, date_iso="")
    assert _payload_from(_render_macro([src]))[0]["date"] == "1. Mai 1380"
    src = dict(SOURCE, date_iso="", date_display="")
    assert _payload_from(_render_macro([src]))[0]["date"] == ""


def test_macro_payload_escapes_markup():
    """|tojson escapet '<', der Block kann das Script-Tag nicht sprengen."""
    html = _render_macro([dict(SOURCE, regest="</script><script>x()</script>")])
    assert "</script><script>x()" not in html
    assert "\\u003c" in html


def test_macro_renders_nothing_without_sources():
    assert _render_macro([]).strip() == "", (
        "Ohne Quellen darf kein Bulk-Knopf und kein Payload entstehen."
    )


def test_both_profile_templates_use_the_macro():
    for path in (PERSON_HTML, ORG_HTML):
        html = path.read_text(encoding="utf-8")
        assert "sources_bulk_mount" in html.split("{% block content %}")[0], (
            f"{path.name} importiert das Macro nicht."
        )
        assert "sources_bulk_mount(profile.sources)" in html, (
            f"{path.name} ruft den Bulk-Mount nicht mit profile.sources auf."
        )
        # Der Knopf gehoert in die Kopfzeile der Quellen-Sektion.
        head = html.split('<section class="person-sources"')[1].split("</h2>")[0]
        assert "sources_bulk_mount" in head, (
            f"{path.name}: Bulk-Mount sitzt nicht im section-head der Quellen."
        )


def test_basket_js_exposes_add_many():
    src = BASKET_JS.read_text(encoding="utf-8")
    assert "function addMany(items)" in src, "addMany fehlt in basket.js."
    assert re.search(r"return\s*\{\s*add,\s*addMany,", src), (
        "addMany ist nicht im oeffentlichen Rueckgabe-Objekt."
    )
    assert "function attachDerivedMany(" in src, (
        "Der gebuendelte Ableitungs-Durchgang fehlt."
    )


def test_basket_js_has_commonjs_export_guard():
    src = BASKET_JS.read_text(encoding="utf-8")
    assert "module.exports = { DataBasket }" in src, (
        "Ohne CommonJS-Guard laesst sich basket.js nicht unter Vitest laden."
    )


def test_mount_js_hydrates_bulk_mount():
    src = MOUNT_JS.read_text(encoding="utf-8")
    assert "'.basket-bulk-mount'" in src, (
        "basket-mount.js hydriert den Bulk-Platzhalter nicht."
    )
    assert "DataBasket.addMany(" in src, (
        "Der Bulk-Klick geht nicht ueber DataBasket.addMany."
    )
    assert "DataBasket.list('source')" in src, (
        "Der Knopf-Zustand wird nicht aus dem Korb-Inhalt berechnet."
    )
    # Ein isGathered pro gelisteter Quelle liest und parst den kompletten
    # Korb je Eintrag (O(Quellen x Korbgroesse)). Der Zustand kommt aus
    # genau einem Read pro Repaint, siehe tests/js/basket-mount.test.js.
    assert "DataBasket.isGathered(" not in src, (
        "Bulk-Zustand wieder ueber isGathered je Quelle berechnet."
    )
    assert "'basket-change'" in src and "'storage'" in src, (
        "Der Knopf reagiert nicht auf Korb-Aenderungen (auch aus anderen Tabs)."
    )


def test_bulk_button_avoids_the_global_click_delegation():
    """basket.js delegiert Klicks auf .basket-btn. Traegt der Bulk-Knopf
    diese Klasse, wuerde er als Einzel-Knopf behandelt."""
    src = MOUNT_JS.read_text(encoding="utf-8")
    assert "basket-bulk-btn" in src
    for cls in re.findall(r"className\s*=\s*'([^']*)'", src):
        assert "basket-btn" not in cls.split(), (
            f"Bulk-Knopf traegt die delegierte Klasse basket-btn: {cls!r}"
        )


def test_bulk_button_labels_are_german_and_count_aware():
    src = MOUNT_JS.read_text(encoding="utf-8")
    assert "'Alle ' + n + ' Quellen'" in src, (
        "Das Label nennt die Zahl der Quellen nicht."
    )
    # Sichtbare Labels tragen echte Umlaute; die ASCII-Schreibweise gilt nur
    # fuer Code-Kommentare und Symbolnamen.
    assert "Einträge mit übernommen." in src, (
        "Der Hovertext des Bulk-Knopfs nutzt keine echten Umlaute."
    )
    assert "uebernommen" not in src and "Eintraege mit" not in src, (
        "ASCII-Transliteration im sichtbaren Hovertext."
    )
    assert "' im Datenkorb'" in src and "' in den Datenkorb'" in src, (
        "Normal- und Fertig-Zustand tragen nicht die vereinbarten Labels."
    )


def test_basket_button_labels_use_real_umlauts():
    """Begriffs- und Label-Konsistenz im Datenkorb: sichtbare Labels und
    Hovertexte tragen echte Umlaute, die ASCII-Schreibweise bleibt
    Code-Kommentaren und Symbolnamen vorbehalten."""
    src = BASKET_JS.read_text(encoding="utf-8")
    for good, bad in (
        ("In den Datenkorb übernehmen", "uebernehmen"),
        ("Klick übernimmt den Eintrag", "uebernimmt"),
        ("als eigenständig gesammelt", "eigenstaendig"),
        ("Zum Datenkorb hinzufügen", "hinzufuegen"),
    ):
        assert good in src, f"Label fehlt oder ist transliteriert: {good!r}"
        assert bad not in src, f"ASCII-Transliteration im sichtbaren Label: {bad!r}"


def test_bulk_css_present():
    css = COMPONENTS_CSS.read_text(encoding="utf-8")
    assert ".basket-bulk-btn {" in css, "Stil fuer den Bulk-Knopf fehlt."
    assert ".basket-bulk-btn.is-in" in css, "Fertig-Zustand ist nicht gestylt."
    layout = PERSON_CSS.read_text(encoding="utf-8")
    assert ".person-sources .section-head .basket-bulk-btn" in layout, (
        "Rechtsbuendige Platzierung im section-head fehlt."
    )
    assert re.search(
        r"\.person-sources \.section-head \.basket-bulk-btn \{[^}]*margin-left: auto",
        layout, re.S,
    ), "Der Knopf wird nicht ans Zeilenende geschoben."
