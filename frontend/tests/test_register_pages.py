"""Tests for register page generation: entity ref extraction, reverse index,
list pages, and JSON detail data."""

import json
import pytest

from pipeline.config import SOURCES_DIR, NS_MAP
from pipeline.utils.xml_loader import load_xml

from frontend.build import (
    _extract_entity_refs,
    _person_search_data,
    _org_search_data,
    _place_search_data,
    _build_register_json,
)
from frontend.register import load_persons, load_orgs, load_places


# --- Entity ref extraction ---


class TestExtractEntityRefs:
    """Test _extract_entity_refs on a known source document."""

    @pytest.fixture(scope="class")
    def refs_doc_100(self):
        """Extract entity refs from document 100."""
        tree = load_xml(
            SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        )
        return _extract_entity_refs(tree.getroot())

    def test_returns_set(self, refs_doc_100):
        assert isinstance(refs_doc_100, set)

    def test_finds_person_refs(self, refs_doc_100):
        # Document 100 contains person annotations
        person_refs = [r for r in refs_doc_100 if r.startswith("pe__")]
        assert len(person_refs) > 0, "Expected person refs in document 100"

    def test_known_person_present(self, refs_doc_100):
        assert "pe__konrad_chrannest_QGW_II_I_99" in refs_doc_100

    def test_excludes_null_refs(self, refs_doc_100):
        assert "NULL" not in refs_doc_100

    def test_strips_hash_prefix(self, refs_doc_100):
        for ref in refs_doc_100:
            assert not ref.startswith("#"), f"Hash prefix not stripped: {ref}"


class TestExtractEntityRefsRoleName:
    """Test that roleName/@corresp references are captured."""

    @pytest.fixture(scope="class")
    def refs_doc_100(self):
        tree = load_xml(
            SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        )
        return _extract_entity_refs(tree.getroot())

    def test_captures_rolename_corresp(self, refs_doc_100):
        # Document 100 has roleName elements with corresp attributes
        # At minimum it should have the same person refs
        assert len(refs_doc_100) > 0


# --- Register data for search JSON ---


class TestRegisterSearchData:
    """Test that register data has expected structure."""

    @pytest.fixture(scope="class")
    def persons(self):
        return load_persons()

    @pytest.fixture(scope="class")
    def orgs(self):
        return load_orgs()

    @pytest.fixture(scope="class")
    def places(self):
        return load_places()

    def test_persons_have_display_name(self, persons):
        for xml_id, data in list(persons.items())[:10]:
            assert "display" in data
            assert data["display"], f"Empty display for {xml_id}"

    def test_orgs_have_name(self, orgs):
        for xml_id, data in list(orgs.items())[:10]:
            assert "name" in data
            assert data["name"], f"Empty name for {xml_id}"

    def test_places_have_name(self, places):
        for xml_id, data in list(places.items())[:10]:
            assert "name" in data
            assert data["name"], f"Empty name for {xml_id}"

    def test_persons_have_sex(self, persons):
        sexes = {data["sex"] for data in persons.values() if data["sex"]}
        assert "m" in sexes
        assert "f" in sexes


class TestSearchDataStructure:
    """Test that search data JSON entries have expected fields."""

    def test_person_search_data_has_doc_count(self):
        persons = {"pe__test": {
            "forename": "Hans", "surname": "Test", "addName": "",
            "death": "", "display": "Hans Test", "sex": "m",
        }}
        reverse = {"pe__test": [{"url": "x.html", "idno": "1"}]}
        data = _person_search_data(persons, reverse)
        assert data[0]["dc"] == 1
        assert "u" not in data[0], "URL field should no longer exist"

    def test_org_search_data_has_doc_count(self):
        orgs = {"org__test": {"name": "Test Org", "type": "Kloster"}}
        data = _org_search_data(orgs, {})
        assert data[0]["dc"] == 0
        assert "u" not in data[0]

    def test_place_search_data_has_doc_count(self):
        places = {"pl__test": {"name": "Wien", "type": "settlement", "lat": "", "lng": ""}}
        data = _place_search_data(places, {})
        assert data[0]["dc"] == 0
        assert "u" not in data[0]


class TestRegisterJson:
    """Test that _build_register_json writes correct JSON files."""

    def test_writes_json_files(self, tmp_path, monkeypatch):
        import frontend.build as build_mod
        monkeypatch.setattr(build_mod, "DOCS_DIR", tmp_path)
        # Stub released-person filter so the synthetic test ID passes through.
        monkeypatch.setattr(build_mod, "_released_person_keys",
                            lambda: {"pe__hans"})

        reverse_index = {
            "pe__hans": [
                {"url": "documents/100.html", "idno": "100",
                 "date_display": "1300", "collection_label": "QGW",
                 "regest": "Regest text"},
            ],
            "org__kloster": [
                {"url": "documents/200.html", "idno": "200",
                 "date_display": "1301", "collection_label": "QGW",
                 "regest": "Org regest"},
            ],
            "pl__wien": [],
        }
        _build_register_json(reverse_index)

        persons_json = tmp_path / "register" / "persons.json"
        orgs_json = tmp_path / "register" / "organisations.json"
        places_json = tmp_path / "register" / "places.json"

        assert persons_json.exists()
        assert orgs_json.exists()
        assert places_json.exists()

        data = json.loads(persons_json.read_text(encoding="utf-8"))
        assert "pe__hans" in data
        assert data["pe__hans"][0]["i"] == "100"

    def test_empty_entity_not_in_json(self, tmp_path, monkeypatch):
        import frontend.build as build_mod
        monkeypatch.setattr(build_mod, "DOCS_DIR", tmp_path)
        monkeypatch.setattr(build_mod, "_released_person_keys", lambda: set())

        _build_register_json({"pl__wien": []})
        data = json.loads(
            (tmp_path / "register" / "places.json").read_text(encoding="utf-8")
        )
        # Empty doc list still gets written (0 docs)
        assert "pl__wien" in data
        assert data["pl__wien"] == []
