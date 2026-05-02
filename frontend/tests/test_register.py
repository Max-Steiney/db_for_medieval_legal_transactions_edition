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
        assert result == "Konrad Goldstein († 23.06.1350) [pe__konrad_goldstein]"

    def test_person_tooltip_no_death(self):
        data = {"display": "Hans", "death": "",
                "forename": "Hans", "surname": "", "addName": "", "sex": "m"}
        result = build_tooltip_person(data, "pe__hans")
        assert result == "Hans [pe__hans]"

    def test_org_tooltip_with_type(self):
        data = {"name": "Herzogtum Österreich", "type": "Herzogtum"}
        result = build_tooltip_org(data, "org__oesterreich")
        assert result == "Herzogtum Österreich (Herzogtum) [org__oesterreich]"

    def test_org_tooltip_no_type(self):
        data = {"name": "Testorg", "type": ""}
        result = build_tooltip_org(data, "org__test")
        assert result == "Testorg [org__test]"

    def test_place_tooltip_full(self):
        data = {"name": "Wien", "type": "settlement", "lat": "48.2", "lng": "16.37"}
        result = build_tooltip_place(data, "pl__wien")
        assert result == "Wien (settlement) [48.2, 16.37] [pl__wien]"

    def test_place_tooltip_no_coords(self):
        data = {"name": "Unbekannt", "type": "settlement", "lat": "", "lng": ""}
        result = build_tooltip_place(data, "pl__x")
        assert result == "Unbekannt (settlement) [pl__x]"


class TestRegisterLoading:
    """Integration tests that load actual register files."""

    def test_load_persons_returns_dict(self):
        persons = load_persons()
        assert isinstance(persons, dict)
        assert len(persons) > 1000  # 16,088 expected

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
        assert len(orgs) > 100  # 1,078 expected

    def test_known_org_exists(self):
        orgs = load_orgs()
        assert "org__oesterreich-herzogtum" in orgs

    def test_load_places_returns_dict(self):
        places = load_places()
        assert isinstance(places, dict)
        assert len(places) > 500  # 2,537 expected

    def test_place_has_coordinates(self):
        places = load_places()
        assert "pl__seefeld_tirol" in places
        assert places["pl__seefeld_tirol"]["lat"] != ""
        assert places["pl__seefeld_tirol"]["lng"] != ""
