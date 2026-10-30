"""Nachschlagen in der roleName-Normliste: ein Vergleichsschluessel fuer
Liste und CSV-Werte (Striche, Leerraum, Gross/Klein), Mehrfach-Zellen
der Personentabelle werden je Tag nachgeschlagen.

Hintergrund (Normlisten-Deep-Dive, 12.10.2026): Die Pipeline verkettet
die Textknoten EINES roleName-Tags in den Beziehungs-CSVs mit ``|``
(``mein genedig |herren| herczog``), waehrend ``persons_in_sources``
MEHRERE Tags einer Person mit ``|`` zusammenfasst
(``Hantfestschreiber|Pikcher``). Die Liste soll nur noch den reinen
Tagtext als Schluessel tragen; die Uebersetzung passiert hier.
"""

from pathlib import Path

import pytest

from frontend.aggregator import _shared
from frontend.aggregator._shared import norm_key, split_multi, tag_text


def test_tag_text_pipe_is_element_boundary():
    assert tag_text("mein genedig |herren| herczog") == "mein genedig herren herczog"
    assert tag_text("Bürger|meister") == "Bürger meister"
    assert tag_text("|Diener") == "Diener"
    assert tag_text("  aussern\n   rats der stat zu Wienn ") == "aussern rats der stat zu Wienn"


def test_norm_key_lowercases_and_matches_pipeline_rule():
    assert norm_key("clericus| Olomucensis dyocesis") == "clericus olomucensis dyocesis"
    assert norm_key("Wachsgiesser") == norm_key("wachsgiesser")
    assert norm_key("") == ""


def test_split_multi_separates_tags_of_one_person():
    assert split_multi("Hantfestschreiber|Pikcher") == ["Hantfestschreiber", "Pikcher"]
    assert split_multi("|ledrer|") == ["ledrer"]
    assert split_multi("") == []


@pytest.fixture
def norm_list(tmp_path, monkeypatch):
    # Spaltenfolge der Liste seit Oktober 2026: type ist Spalte A.
    rows = [
        "type\troleName_spelling\troleName_spelling_norm\troleName_contentual_norm\tGewerbe_nach_Uhlirz_GstW\tauthority\tnote\tnote_type\tresp\tKomttar Zu Uhlirz Klassifikation\tBelege",
        "occ\tmein genedig herren herczog\tHerzog\tHerzog_in\t\t\t\t\trs\t\t",
        "occ\tclericus| Olomucensis dyocesis\tKleriker\tKanoniker\t\t\t\t\trs\t\t",
        "prof\tWachsgiesser\tWachsgiesser\tWachsgiesser\tIV Leuchtstoffe\t\t\t\tkg\t\t",
        "prof\tledrer\tLederer\tGerber\tVI Lederindustrie\t\t\t\tkg\t\t",
        # dieselbe Schreibung mit zwei Typen und zwei Klassen
        "kin\twirt\tWirt\tEhegatt_in\t\t\t\t\tkg\t\t",
        "prof\twirt\tWirt\tGastwirt_in\tVIII Gastgewerbe\t\t\t\tkg\t\t",
        "occ\twirt\tWirt\tGastwirt_in\tVIII Gastgewerbe\t\t\t\tkg\t\t",
        # occ-Zeile mit Gewerbe-Altbestand: darf die Uhlirz-Zuordnung nicht speisen
        "occ\tburgermaister\tBuergermeister\tBuergermeister\tXVIII Verwaltung\t\t\t\tkg\t\t",
        # Zeile ohne Typ: wird uebersprungen
        "\tbesehers\tBeseher\tBeseher\t\t\t\t\tkg\t\t",
    ]
    (tmp_path / "roleName_norm_matching.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(_shared, "NORM_LISTS_DIR", Path(tmp_path))
    return tmp_path


def test_rolename_norm_lookup_ignores_pipes_and_case(norm_list):
    norm = _shared._load_rolename_norm("occ")
    # CSV-Wert mit Strich trifft den Listen-Schluessel ohne Strich ...
    assert norm[norm_key("mein genedig |herren| herczog")] == "Herzog_in"
    # ... und ein Listen-Schluessel mit Strich (Altbestand) trifft den Tagtext.
    assert norm[norm_key("clericus Olomucensis dyocesis")] == "Kanoniker"
    # prof-Zeilen sind im occ-Lookup nicht enthalten
    assert norm_key("wachsgiesser") not in norm
    assert _shared._load_rolename_norm("prof")[norm_key("wachsgiesser")] == "Wachsgiesser"


def test_rolename_norm_lookup_is_type_aware(norm_list):
    # "wirt" ist als kin der Ehemann, als prof/occ der Gastwirt
    assert _shared._load_rolename_norm("kin")[norm_key("Wirt")] == "Ehegatt_in"
    assert _shared._load_rolename_norm("prof")[norm_key("Wirt")] == "Gastwirt_in"
    assert _shared._load_rolename_norm("occ")[norm_key("Wirt")] == "Gastwirt_in"
    # ohne Typ: Schluessel ist das Paar (type, key)
    full = _shared._load_rolename_norm()
    assert full[("kin", "wirt")] == "Ehegatt_in"
    assert full[("prof", "wirt")] == "Gastwirt_in"
    assert ("", "besehers") not in full and "besehers" not in {k[1] for k in full}


def test_uhlirz_lookup_per_tag_of_multi_cell(norm_list):
    uhlirz = _shared._load_uhlirz_matching()
    parts = split_multi("Guelher|der ledrer")
    cats = [uhlirz.get(norm_key(p)) for p in parts]
    assert cats == [None, None]  # "der ledrer" ist nicht "ledrer": Liste braucht eigene Zeile
    assert uhlirz[norm_key("Ledrer")] == ["VI Lederindustrie"]


def test_uhlirz_lookup_uses_prof_rows_only(norm_list):
    uhlirz = _shared._load_uhlirz_matching()
    # Gewerbe ist eine Berufseigenschaft: occ-Zeilen mit Altbestand zaehlen nicht
    assert norm_key("burgermaister") not in uhlirz
    assert uhlirz[norm_key("wirt")] == ["VIII Gastgewerbe"]
    # explizit occ angefragt: dann sichtbar (Altbestand), aber kein Default
    assert _shared._load_uhlirz_matching("occ")[norm_key("burgermaister")] == ["XVIII Verwaltung"]
