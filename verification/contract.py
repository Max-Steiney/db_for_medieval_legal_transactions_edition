"""Vertrag fuer die TEI-zu-HTML-Coverage.

Definiert pro Entity-Typ, welche Felder der Aggregator-Input
(persons.csv, organisations.csv, persons_in_sources.csv, ...) im
gerenderten HTML zu finden sein muessen, welche optional sind und
welche bewusst nicht im HTML erscheinen.

Das ist die Stelle, an der bekannte Lücken (known_gap) deklariert
werden, damit der Coverage-Lauf zwischen "Renderer-Bug" und
"absichtlich nicht angezeigt" unterscheiden kann.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set


@dataclass(frozen=True)
class FieldContract:
    """Spec fuer ein einzelnes Datenfeld der Coverage-Pruefung.

    - ``required``: HTML muss diesen Wert zeigen, wenn die CSV ihn hat.
    - ``conditional``: HTML zeigt nur unter bestimmten Bedingungen
      (Doku in ``condition`` als kurzem Text).
    - ``filter``: CSV-Wert wird bewusst nicht ins HTML uebernommen
      (z. B. interne IDs, Editor-Kommentare).
    """

    name: str
    required: bool = True
    condition: Optional[str] = None
    filter_reason: Optional[str] = None

    @property
    def is_filter(self) -> bool:
        return self.filter_reason is not None


# ---------------------------------------------------------------------------
# Person-Felder aus persons.csv
# ---------------------------------------------------------------------------

PERSON_FIELD_CONTRACTS = {
    # Aus _reg-Spalten gebaut. Erscheint als <h1>.
    "display_name": FieldContract(
        name="display_name", required=True
    ),
    # In ph-meta-strip als sex_label ("männlich"/"weiblich"/"Geschlecht
    # unbestimmt").
    "sex_label": FieldContract(name="sex_label", required=True),
    # death_iso -> death_display. Conditional: nur wenn dead_before im
    # CSV gesetzt ist, taucht "Verstorben vor" im Header auf.
    "death_display": FieldContract(
        name="death_display",
        required=False,
        condition="nur wenn persons.csv:dead_before gesetzt",
    ),
    # authority-Spalte ist pipe-gesplittete URL-Liste. Wenn vorhanden,
    # erscheinen als Authority-Links in ph-subline.
    "authority_urls": FieldContract(
        name="authority_urls",
        required=False,
        condition="nur wenn persons.csv:authority gesetzt",
    ),
    # PAGEID_WienWiki + Name_WienWiki -> Wien-Wiki-Link in ph-subline.
    "wiki_url": FieldContract(
        name="wiki_url",
        required=False,
        condition="nur wenn PAGEID_WienWiki gesetzt",
    ),
    # forename_orig / surname_orig / addname_orig: kombiniert nur dann
    # angezeigt, wenn != _reg-Form. ph-subline > "Im Quellen-Wortlaut".
    "name_orig": FieldContract(
        name="name_orig",
        required=False,
        condition="nur wenn _orig-Form von _reg-Form abweicht",
    ),
    # note: persons.csv:note. Erscheint als <p class=person-note>.
    "note": FieldContract(
        name="note",
        required=False,
        condition="nur wenn persons.csv:note gesetzt",
    ),
    # Filter: bewusst nicht im HTML
    "internal_id_columns": FieldContract(
        name="internal_id_columns",
        required=False,
        filter_reason="xml_id-Varianten sind Pipeline-intern",
    ),
}


# ---------------------------------------------------------------------------
# Org-Felder aus organisations.csv
# ---------------------------------------------------------------------------

ORG_FIELD_CONTRACTS = {
    "name": FieldContract(name="name", required=True),
    "type_label": FieldContract(
        name="type_label",
        required=False,
        condition="nur wenn type-Spalte gesetzt",
    ),
    "observance": FieldContract(
        name="observance",
        required=False,
        condition="nur wenn observance-Spalte gesetzt",
    ),
    "place_name": FieldContract(
        name="place_name",
        required=False,
        condition="nur wenn place_key gesetzt UND der Ort im Register vorhanden",
    ),
    "parent_org_id": FieldContract(
        name="parent_org_id",
        required=False,
        condition="nur wenn org_key gesetzt",
    ),
    "authority_urls": FieldContract(
        name="authority_urls",
        required=False,
        condition="nur wenn organisations.csv:authority gesetzt",
    ),
}


# ---------------------------------------------------------------------------
# Bekannte known_gap-Marker fuer Felder, die in der CSV stehen, aber im
# HTML systematisch nicht angezeigt werden (z. B. weil das jeweilige
# Register fehlt oder das Feld experimentell ist).
# ---------------------------------------------------------------------------

KNOWN_GAPS: Set[str] = {
    # Place-Profile gibt es nicht; place_name auf Org-Profilen ist
    # Klartext (nicht verlinkt).
    "org.place_name.is_plain_text",
    # title_ref_inverse: derzeit leer im CSV, aber strukturell vorbereitet.
    "person.title_ref_inverse.empty_by_data",
}
