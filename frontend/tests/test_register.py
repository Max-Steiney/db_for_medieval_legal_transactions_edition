"""Unit tests for register loading and tooltip generation."""

import pytest

from frontend.register import (
    load_persons,
    load_orgs,
    load_places,
    build_tooltip_person,
    build_tooltip_org,
    build_tooltip_place,
)


class TestTooltipBuilders:
    """Test tooltip string formatting (no I/O needed)."""

    def test_person_tooltip_full(self):
        data = {"display": "Konrad Goldstein", "death": "1350-06-23",
                "forename": "Konrad", "surname": "Goldstein", "addName": "", "sex": "m"}
        result = build_tooltip_person(data, "pe__konrad_goldstein")
        # Sterbedatum seit Meeting 2026-06-17 nicht mehr im Tooltip/Hint:
        # notAfter-Terminus, als exaktes Datum missverstaendlich.
        assert result == "Konrad Goldstein"
        assert "†" not in result

    def test_person_tooltip_no_death(self):
        data = {"display": "Hans", "death": "",
                "forename": "Hans", "surname": "", "addName": "", "sex": "m"}
        result = build_tooltip_person(data, "pe__hans")
        assert result == "Hans"

    def test_org_tooltip_with_type(self):
        data = {"name": "Herzogtum Österreich", "type": "Herzogtum"}
        result = build_tooltip_org(data, "org__oesterreich")
        assert result == "Herzogtum Österreich (Herzogtum)"

    def test_org_tooltip_no_type(self):
        data = {"name": "Testorg", "type": ""}
        result = build_tooltip_org(data, "org__test")
        assert result == "Testorg"

    def test_place_tooltip_full(self):
        data = {"name": "Wien", "type": "settlement", "lat": "48.2", "lng": "16.37"}
        result = build_tooltip_place(data, "pl__wien")
        assert result == "Wien (settlement) [48.2, 16.37]"

    def test_place_tooltip_no_coords(self):
        data = {"name": "Unbekannt", "type": "settlement", "lat": "", "lng": ""}
        result = build_tooltip_place(data, "pl__x")
        assert result == "Unbekannt (settlement)"


class TestRegisterLoading:
    """Integration tests that load actual register files."""

    def test_load_persons_returns_dict(self):
        persons = load_persons()
        assert isinstance(persons, dict)
        assert len(persons) > 1000

    def test_person_has_required_keys(self):
        persons = load_persons()
        sample = next(iter(persons.values()))
        for key in ("forename", "surname", "addName", "death", "display", "sex"):
            assert key in sample

    def test_known_person_exists(self):
        persons = load_persons()
        assert "pe__konrad_goldstein" in persons
        assert persons["pe__konrad_goldstein"]["forename"] == "Konrad"

    def test_load_orgs_returns_dict(self):
        orgs = load_orgs()
        assert isinstance(orgs, dict)
        assert len(orgs) > 100

    def test_known_org_exists(self):
        orgs = load_orgs()
        assert "org__oesterreich-herzogtum" in orgs

    def test_load_places_returns_dict(self):
        places = load_places()
        assert isinstance(places, dict)
        assert len(places) > 500

    def test_place_has_coordinates(self):
        places = load_places()
        assert "pl__seefeld_tirol" in places
        assert places["pl__seefeld_tirol"]["lat"] != ""
        assert places["pl__seefeld_tirol"]["lng"] != ""


class TestAddnameDedupRegisterliste:
    """load_persons() nutzt dieselbe Dedup-SSoT wie die Profilseiten.

    Befund 20.07.2026: Personen, deren addName den surname woertlich
    doppelt, erschienen in Register-Liste, Suche und Tooltips doppelt
    benannt ("Heinrich Holm Holm"), auf der Profilseite aber korrekt —
    weil load_persons() nie an _dedup_addname angeschlossen war.
    """

    def test_holm_erscheint_nur_einmal(self):
        persons = load_persons()
        p = persons["pe__heinrich_holm_QGW_II_I_634"]
        assert p["display"] == "Heinrich Holm"
        assert p["addName"] == ""

    def test_distinkter_addname_bleibt(self):
        persons = load_persons()
        p = persons["pe__thomas_gorser_SB_CD_00787_a"]
        assert p["addName"] == "zu Schönberg"
        assert p["display"] == "Thomas Gorser zu Schönberg"

    def test_keine_surname_dopplung_im_gesamten_register(self):
        persons = load_persons()
        dopplungen = [
            xml_id for xml_id, p in persons.items()
            if p["addName"] and p["surname"]
            and p["addName"].casefold().strip() == p["surname"].casefold().strip()
        ]
        assert dopplungen == []

    def test_tooltip_erbt_dedupliziertes_display(self):
        persons = load_persons()
        p = persons["pe__heinrich_holm_QGW_II_I_634"]
        assert build_tooltip_person(p, "pe__heinrich_holm_QGW_II_I_634") == "Heinrich Holm"
