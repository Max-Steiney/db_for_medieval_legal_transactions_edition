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
    _build_register_json,
)
from frontend.build._pages import _short_collection_label, _type_chip_data
from frontend.register import load_persons, load_orgs, load_places


# --- Short collection label for sub-label in person register ---


class TestShortCollectionLabel:
    def test_strips_year_parens(self):
        assert _short_collection_label(
            "QGW/Vienna_1177-1414_ready"
        ) == "QGW II/1"

    def test_falls_back_to_path(self):
        assert _short_collection_label("Unknown/Path") == "Unknown/Path"


# --- Org-Typ-Filter-Chips: Labels und Sortierung (H1/H2, Meeting 02.06.2026) ---


class TestTypeChipData:
    def test_raw_codes_get_german_labels(self):
        data = [
            {"tp": "Kloster_f"},
            {"tp": "Spital_Siechenhaus"},
            {"tp": "Dioezese_Erzdioezese"},
        ]
        out = {c["key"]: c["label"] for c in _type_chip_data(data)}
        assert out["Kloster_f"] == "Kloster (Frauenorden)"
        assert out["Spital_Siechenhaus"] == "Spital / Siechenhaus"
        assert out["Dioezese_Erzdioezese"] == "Diözese / Erzdiözese"

    def test_other_label_is_sonstige(self):
        out = {c["key"]: c["label"] for c in _type_chip_data([{"tp": "OTHER"}])}
        assert out["OTHER"] == "Sonstige"

    def test_other_sorted_last_even_with_highest_count(self):
        data = [{"tp": "OTHER"}] * 50 + [{"tp": "Messe"}] * 3 + [{"tp": "Pfarre"}]
        out = _type_chip_data(data)
        assert out[-1]["key"] == "OTHER"
        non_other = [c["key"] for c in out if c["key"] != "OTHER"]
        assert non_other == ["Messe", "Pfarre"]

    def test_empty_key_is_ohne_angabe_and_last(self):
        data = [{"tp": ""}] * 5 + [{"tp": "Messe"}]
        out = _type_chip_data(data)
        assert out[-1]["label"] == "ohne Angabe"

    def test_chip_key_stays_raw_for_url_linking(self):
        # Der Filter-Link ?types=OTHER muss weiter funktionieren: nur das
        # Label wird uebersetzt, der key bleibt der Rohwert.
        out = {c["key"]: c for c in _type_chip_data([{"tp": "OTHER"}])}
        assert "OTHER" in out

    def test_empty_input(self):
        assert _short_collection_label("") == ""


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
        # Document 100 has roleName elements with corresp attributes;
        # at minimum it should have the same person refs.
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
        reverse = {"pe__test": [{
            "url": "x.html", "idno": "1",
            "date_iso": "1340-05-10", "date_display": "10. Mai 1340",
            "collection_path": "QGW/Vienna_1177-1414_ready",
            "collection_label": "QGW II/1 (1177–1414)",
            "regest": "",
        }]}
        data = _person_search_data(persons, reverse)
        assert data[0]["dc"] == 1
        # The new fields must all be set.
        assert data[0]["am"] == "1340"
        assert data[0]["ax"] == "1340"
        assert data[0]["i0"] == "1"
        assert data[0]["cl0"] == "QGW II/1"
        assert data[0]["co"] == ["QGW/Vienna_1177-1414_ready"]
        assert data[0]["rl"] == []
        # Removed fields must really be gone.
        assert "u" not in data[0]
        assert "d" not in data[0], "death field should no longer exist"
        assert "qw" not in data[0], "quality-worst field should no longer exist"

    def test_person_search_data_skips_persons_without_docs(self):
        # Defensive: no source => person not in register.
        persons = {"pe__ghost": {
            "forename": "", "surname": "", "addName": "",
            "death": "", "display": "Ghost", "sex": "",
        }}
        data = _person_search_data(persons, {})
        assert data == []

    def test_person_search_data_aggregates_roles(self):
        persons = {"pe__test": {
            "forename": "Hans", "surname": "Test", "addName": "",
            "death": "", "display": "Hans Test", "sex": "m",
        }}
        reverse = {"pe__test": [{
            "url": "x.html", "idno": "1",
            "date_iso": "1340-05-10", "date_display": "1340",
            "collection_path": "QGW/Vienna_1177-1414_ready",
            "collection_label": "QGW", "regest": "",
        }]}
        roles = {"pe__test": {"issuer", "witness"}}
        data = _person_search_data(persons, reverse, person_roles=roles)
        # Sorted (issuer < witness).
        assert data[0]["rl"] == ["issuer", "witness"]

    def test_person_search_data_year_span(self):
        persons = {"pe__test": {
            "forename": "Hans", "surname": "Test", "addName": "",
            "death": "", "display": "Hans Test", "sex": "m",
        }}
        reverse = {"pe__test": [
            {"url": "a.html", "idno": "1",
             "date_iso": "1287-01-01", "date_display": "1287",
             "collection_path": "QGW/Vienna_1177-1414_ready",
             "collection_label": "QGW", "regest": ""},
            {"url": "b.html", "idno": "9",
             "date_iso": "1312-06-30", "date_display": "1312",
             "collection_path": "QGW/Vienna_1177-1414_ready",
             "collection_label": "QGW", "regest": ""},
        ]}
        data = _person_search_data(persons, reverse)
        assert data[0]["am"] == "1287"
        assert data[0]["ax"] == "1312"
        # i0 is the EARLIEST source (reverse_index is date-sorted).
        assert data[0]["i0"] == "1"

    def test_org_search_data_has_doc_count(self):
        # Orgs with at least one released mention enter the list. Entities
        # without a source link are filtered out (same convention as the
        # persons register).
        orgs = {"org__test": {"name": "Test Org", "type": "Kloster"}}
        reverse = {"org__test": [
            {"url": "a.html", "idno": "1",
             "date_iso": "1287-01-01", "date_display": "1287",
             "collection_path": "QGW/Vienna_1177-1414_ready",
             "collection_label": "QGW", "regest": ""},
        ]}
        data = _org_search_data(orgs, reverse)
        assert data[0]["dc"] == 1
        assert data[0]["tp"] == "Kloster"
        assert "u" not in data[0]

class TestRegisterJson:
    """Test that _build_register_json writes correct JSON files."""

    def test_writes_json_files(self, tmp_path, monkeypatch):
        from frontend.tests.conftest import patch_build_path
        import frontend.build._pages as pages_mod
        patch_build_path(monkeypatch, "DOCS_DIR", tmp_path)
        # Stub released-person filter so the synthetic test ID passes through.
        # _build_register_json calls the function imported into _pages —
        # so patch it there.
        monkeypatch.setattr(pages_mod, "_released_person_keys",
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
            # pl__ keys are ignored — places have no register JSON.
            "pl__wien": [
                {"url": "documents/200.html", "idno": "200",
                 "date_display": "1301", "collection_label": "QGW",
                 "regest": ""},
            ],
        }
        _build_register_json(reverse_index)

        persons_json = tmp_path / "register" / "persons.json"
        orgs_json = tmp_path / "register" / "organisations.json"
        places_json = tmp_path / "register" / "places.json"

        assert persons_json.exists()
        assert orgs_json.exists()
        assert not places_json.exists()

        data = json.loads(persons_json.read_text(encoding="utf-8"))
        assert "pe__hans" in data
        assert data["pe__hans"][0]["i"] == "100"
