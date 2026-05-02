"""Schema-Tests fuer docs/data/ und docs/register/.

Prueft die in docs/data/SCHEMA.md dokumentierten Strukturen gegen den
realen Build-Output. Setzt voraus, dass `python -m frontend build`
mindestens einmal gelaufen ist (im CI: Smoke-Build vor pytest).

Tests, die der Aggregator selbst pruefen kann (timeline, epic_*,
docs_aggregate, docs_lookup), liegen in test_aggregator.py mit eigener
Fixture. Diese Datei deckt das ab, was nicht durch run_aggregation
allein abgedeckt wird: search.json, persons_search.json,
register/*.json, categories.json, query_vocabulary.json.

Wenn docs/data/ fehlt, werden alle Tests geskippt.
"""

import json
from pathlib import Path

import pytest

DOCS_DATA = Path(__file__).parent.parent.parent / "docs" / "data"
DOCS_REGISTER = Path(__file__).parent.parent.parent / "docs" / "register"


def _load(path: Path):
    if not path.exists():
        pytest.skip(f"{path} fehlt - python -m frontend build vorher ausfuehren")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# search.json — Such-Index der Quellen-Uebersicht
# ---------------------------------------------------------------------------

class TestSearchJson:
    """search.json: Top-Level Array, kompakte Field-Names pro Quelle."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "search.json")

    def test_is_array(self, data):
        assert isinstance(data, list)
        assert len(data) > 1000

    def test_record_has_required_fields(self, data):
        # Aus SCHEMA.md: alle dokumentierten Felder muessen im 1. Record sein
        required = {"id", "t", "tf", "c", "cp", "cl", "sc",
                    "d", "di", "dn", "p", "u",
                    "f",
                    "pc", "pcd", "pcdf", "pcdm", "pcdu",
                    "ec", "ecR", "ecS", "ecE", "ecN"}
        sample = data[0]
        missing = required - set(sample.keys())
        assert not missing, f"search.json record missing fields: {missing}"

    def test_quality_fields_removed(self, data):
        # Quality-Felder wurden komplett entfernt — Regression-Guard.
        forbidden = {"q", "qc", "qcat"}
        sample = data[0]
        leaked = forbidden & set(sample.keys())
        assert not leaked, f"quality fields still present in search.json: {leaked}"

    def test_fac_flag_boolean(self, data):
        # f ist 0 oder 1
        for d in data[:100]:
            assert d["f"] in (0, 1)

    def test_url_relative(self, data):
        # u ist relativ zu docs/, beginnt nicht mit /
        for d in data[:100]:
            assert not d["u"].startswith("/"), f"absolute URL: {d['u']}"
            assert d["u"].endswith(".html")


# ---------------------------------------------------------------------------
# persons_search.json — Personenregister-Suchindex
# ---------------------------------------------------------------------------

class TestPersonsSearchJson:
    """persons_search.json: Array von Personen, kompakte Felder."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "persons_search.json")

    def test_is_array(self, data):
        assert isinstance(data, list)
        assert len(data) > 1000

    def test_record_has_required_fields(self, data):
        # Felder nach Rework: id, n/fn/sn (Suchindex), sex, dc (>=1 per
        # Konstruktion), am/ax (Aktivitaetszeitraum), co (Korpus-Liste),
        # i0/cl0 (Anker fuer Sub-Label), rl (Rollen). d/qw entfallen.
        required = {"id", "n", "fn", "sn", "sex",
                    "dc", "am", "ax", "co", "i0", "cl0", "rl"}
        sample = data[0]
        missing = required - set(sample.keys())
        assert not missing, f"persons_search.json record missing: {missing}"

    def test_id_prefix(self, data):
        for p in data[:50]:
            assert p["id"].startswith("pe__"), f"id without pe__: {p['id']}"

    def test_sex_values(self, data):
        # sex ist m/f oder leer (laut SCHEMA)
        for p in data[:100]:
            assert p["sex"] in ("m", "f", ""), f"unexpected sex {p['sex']!r}"

    def test_dc_at_least_one(self, data):
        # Per Konstruktion: nur Personen mit mindestens einer freigegebenen
        # Quellennennung kommen ins Register.
        for p in data[:200]:
            assert p["dc"] >= 1, f"dc < 1 in released register: {p['id']}"

    def test_roles_in_vocabulary(self, data):
        # Rollen-Vokabular kontrolliert auf vier Werte
        valid = {"issuer", "recipient", "witness", "other"}
        for p in data[:200]:
            for r in p.get("rl", []):
                assert r in valid, f"unexpected role {r!r} in {p['id']}"


# ---------------------------------------------------------------------------
# register/{persons,organisations,places}.json — Reverse-Index
# ---------------------------------------------------------------------------

class TestRegisterReverseJson:
    """register/*.json: entity_id -> [doc-record], kompakte Felder."""

    @pytest.mark.parametrize("name,prefix", [
        ("persons", "pe__"),
        ("organisations", "org__"),
        ("places", "pl__"),
    ])
    def test_top_level_object_with_prefixed_keys(self, name, prefix):
        data = _load(DOCS_REGISTER / f"{name}.json")
        assert isinstance(data, dict)
        # Allow empty dict for stubs, but if non-empty all keys must use prefix
        for k in list(data.keys())[:20]:
            assert k.startswith(prefix), \
                f"{name}.json has non-prefixed key: {k}"

    @pytest.mark.parametrize("name", ["persons", "organisations", "places"])
    def test_doc_records_have_compact_keys(self, name):
        data = _load(DOCS_REGISTER / f"{name}.json")
        if not data:
            pytest.skip(f"{name}.json empty - nothing to validate")
        first_id = next(iter(data))
        records = data[first_id]
        assert isinstance(records, list)
        if not records:
            return
        required = {"u", "i", "d", "c", "r"}
        missing = required - set(records[0].keys())
        assert not missing, f"register/{name}.json record missing: {missing}"


# ---------------------------------------------------------------------------
# categories.json — Editorielle Org-Typ-Mappings
# ---------------------------------------------------------------------------

class TestCategoriesJson:
    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "categories.json")

    def test_top_level_keys(self, data):
        for k in ("meta", "categories", "labels"):
            assert k in data, f"categories.json missing {k}"

    def test_meta_has_version(self, data):
        meta = data["meta"]
        assert "version" in meta or "decided" in meta

    def test_three_categories(self, data):
        cats = data["categories"]
        for k in ("geistlich", "weltlich", "sonstige"):
            assert k in cats, f"categories.json missing category {k}"
            assert isinstance(cats[k], list)


# ---------------------------------------------------------------------------
# query_vocabulary.json — Analyse-Composer-Vokabular
# ---------------------------------------------------------------------------

class TestQueryVocabularyJson:
    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "query_vocabulary.json")

    def test_top_level_keys(self, data):
        for k in ("meta", "subjects", "filters", "constraints"):
            assert k in data, f"query_vocabulary.json missing {k}"

    def test_subjects_have_filters(self, data):
        for sid, subject in data["subjects"].items():
            assert "label" in subject, f"subject {sid} missing label"
            assert "filters" in subject, f"subject {sid} missing filters"
            assert isinstance(subject["filters"], list)

    def test_filter_definitions_match_subject_references(self, data):
        defined = set(data["filters"].keys())
        for sid, subject in data["subjects"].items():
            for f in subject["filters"]:
                assert f in defined, \
                    f"subject {sid} references undefined filter {f}"

    def test_max_active_filters_constraint(self, data):
        assert data["constraints"]["max_active_filters"] >= 1


# ---------------------------------------------------------------------------
# docs_lookup.json — file_key -> Metadaten-Lookup
# ---------------------------------------------------------------------------

class TestDocsLookupJson:
    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "docs_lookup.json")

    def test_keys_are_file_keys(self, data):
        for k in list(data.keys())[:50]:
            assert k.startswith("f__"), f"non-file_key: {k}"

    def test_records_have_required_fields(self, data):
        first = next(iter(data.values()))
        required = {"u", "i", "d", "c", "r"}
        missing = required - set(first.keys())
        assert not missing, f"docs_lookup record missing: {missing}"

    def test_url_relative(self, data):
        for record in list(data.values())[:50]:
            assert not record["u"].startswith("/")
            assert record["u"].endswith(".html")


# ---------------------------------------------------------------------------
# Cross-File-Konsistenz: SCHEMA.md erwaehnt versionierungs-Felder
# ---------------------------------------------------------------------------

class TestSchemaVersioning:
    @pytest.mark.parametrize("filename", [
        "docs_aggregate.json", "epic_a.json", "epic_b.json", "epic_c.json",
        "timeline.json",
    ])
    def test_aggregate_files_have_schema_version(self, filename):
        data = _load(DOCS_DATA / filename)
        assert "meta" in data
        assert "schema_version" in data["meta"], \
            f"{filename} meta missing schema_version"

    @pytest.mark.parametrize("filename", [
        "categories.json", "query_vocabulary.json",
    ])
    def test_editorial_files_have_version(self, filename):
        data = _load(DOCS_DATA / filename)
        assert "meta" in data
        # editorial files use 'version' instead of 'schema_version'
        assert "version" in data["meta"] or "schema_version" in data["meta"], \
            f"{filename} meta missing version field"
