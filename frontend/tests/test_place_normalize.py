"""Tests fuer Ortsnamen-Normalisierung im Build."""

import json
from pathlib import Path

import pytest

from frontend.build._place_normalize import (
    normalize_place_key,
    build_canonical_index,
    canonical_place_name,
    detect_collisions,
)


class TestNormalizeKey:
    """normalize_place_key liefert einen vergleichbaren Schluessel."""

    def test_bindestrich_zu_leerzeichen(self):
        assert normalize_place_key("Wiener-Neustadt") == "wiener neustadt"
        assert normalize_place_key("Wiener Neustadt") == "wiener neustadt"

    def test_case_insensitiv(self):
        assert normalize_place_key("WIEN") == "wien"
        assert normalize_place_key("Wien") == "wien"

    def test_punkt_zu_leerzeichen(self):
        assert normalize_place_key("St. Pölten") == "st pölten"
        assert normalize_place_key("St.Pölten") == "st pölten"

    def test_mehrfache_whitespaces_kollabieren(self):
        assert normalize_place_key("Wiener   Neustadt") == "wiener neustadt"

    def test_leer_und_none(self):
        assert normalize_place_key("") == ""
        assert normalize_place_key(None) == ""


class TestCanonicalIndex:
    """build_canonical_index baut Map aus places.csv plus aliases."""

    def test_places_csv_baut_index(self, tmp_path):
        csv_path = tmp_path / "places.csv"
        csv_path.write_text(
            "id;name_reg;source;name_orig;type\n"
            "pl__wiener_neustadt;Wiener Neustadt;;;settlement\n"
            "pl__st_poelten;St. Pölten;;;settlement\n",
            encoding="utf-8",
        )
        index = build_canonical_index(csv_path, tmp_path / "nope.json")
        assert index["wiener neustadt"] == "Wiener Neustadt"
        assert index["st pölten"] == "St. Pölten"

    def test_aliases_ergaenzen(self, tmp_path):
        csv_path = tmp_path / "places.csv"
        csv_path.write_text(
            "id;name_reg;source;name_orig;type\n"
            "pl__pressburg;Pressburg;;;settlement\n",
            encoding="utf-8",
        )
        aliases_path = tmp_path / "aliases.json"
        aliases_path.write_text(
            json.dumps({"Posonium": "Pressburg"}),
            encoding="utf-8",
        )
        index = build_canonical_index(csv_path, aliases_path)
        assert index["posonium"] == "Pressburg"
        assert index["pressburg"] == "Pressburg"

    def test_underscore_keys_uebersprungen(self, tmp_path):
        """Schema- oder Doku-Keys mit _-Prefix tauchen nicht im Index auf."""
        csv_path = tmp_path / "places.csv"
        csv_path.write_text("id;name_reg;source;name_orig;type\n", encoding="utf-8")
        aliases_path = tmp_path / "aliases.json"
        aliases_path.write_text(
            json.dumps({"_description": "Doku", "Posonium": "Pressburg"}),
            encoding="utf-8",
        )
        index = build_canonical_index(csv_path, aliases_path)
        assert "doku" not in index.values()
        assert index.get("posonium") == "Pressburg"

    def test_immo_typ_uebersprungen(self, tmp_path):
        """Liegenschaften (immo) gehoeren nicht in den Datums-Ort-Filter."""
        csv_path = tmp_path / "places.csv"
        csv_path.write_text(
            "id;name_reg;source;name_orig;type\n"
            "pl__wien;Wien;;;settlement\n"
            "pl__wien-immo_haus_X;Johann von Eslarn Haus;;;immo\n",
            encoding="utf-8",
        )
        index = build_canonical_index(csv_path, tmp_path / "nope.json")
        assert "wien" in index
        assert "johann von eslarn haus" not in index


class TestCanonicalPlaceName:
    """canonical_place_name aufloesen oder Freitext zurueck."""

    def test_bindestrich_variante_aufgeloest(self):
        index = {"wiener neustadt": "Wiener Neustadt"}
        assert canonical_place_name("Wiener-Neustadt", index) == "Wiener Neustadt"
        assert canonical_place_name("Wiener Neustadt", index) == "Wiener Neustadt"

    def test_unbekannt_unveraendert(self):
        index = {"wiener neustadt": "Wiener Neustadt"}
        assert canonical_place_name("Hintertupfing", index) == "Hintertupfing"

    def test_leer_unveraendert(self):
        index = {"wiener neustadt": "Wiener Neustadt"}
        assert canonical_place_name("", index) == ""


class TestRealPlacesCsv:
    """Gegen das echte places.csv aus dem Schwester-Repo pruefen."""

    @pytest.fixture
    def real_places_csv(self):
        from pipeline.config import PIPELINE_OUTPUT
        path = PIPELINE_OUTPUT / "places.csv"
        if not path.exists():
            pytest.skip("places.csv nicht verfuegbar")
        return path

    def test_keine_kollisionen(self, real_places_csv):
        """Eindeutigkeit-Schutz: kein normalisierter Schluessel zeigt
        auf mehr als einen Anzeigenamen in places.csv. Faellt der Test,
        muss ein Eintrag umbenannt oder eine Disambiguierungs-Spalte
        ergaenzt werden."""
        collisions = detect_collisions(real_places_csv)
        assert collisions == [], (
            f"Mehrfache Aufloesungen fuer dieselbe normalisierte Form: "
            f"{collisions[:5]}"
        )

    def test_wiener_neustadt_kanonisiert(self, real_places_csv):
        """Der Live-Bug aus dem Audit darf nicht mehr auftreten."""
        index = build_canonical_index(
            real_places_csv,
            Path(__file__).parent.parent / "content" / "place_aliases.json",
        )
        assert canonical_place_name("Wiener-Neustadt", index) == "Wiener Neustadt"
        assert canonical_place_name("Wiener Neustadt", index) == "Wiener Neustadt"
