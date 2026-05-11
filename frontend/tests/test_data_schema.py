"""Schema tests for docs/data/ and docs/register/.

Verifies the structures documented in docs/data/SCHEMA.md against the real
build output. Assumes that `python -m frontend build` has run at least
once (in CI: smoke build before pytest).

Tests that the aggregator itself can verify (timeline, epic_*,
docs_aggregate, docs_lookup) live in test_aggregator.py with their own
fixture. This file covers what is not covered by run_aggregation alone:
search.json, persons_search.json, register/*.json, categories.json,
query_vocabulary.json.

If docs/data/ is missing, all tests are skipped.
"""

import json
from pathlib import Path

import pytest

DOCS_DATA = Path(__file__).parent.parent.parent / "docs" / "data"
DOCS_REGISTER = Path(__file__).parent.parent.parent / "docs" / "register"


def _load(path: Path):
    if not path.exists():
        pytest.skip(f"{path} missing - run python -m frontend build first")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# search.json — search index of the source overview
# ---------------------------------------------------------------------------

class TestSearchJson:
    """search.json: top-level array, compact field names per source."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "search.json")

    def test_is_array(self, data):
        assert isinstance(data, list)
        assert len(data) > 1000

    def test_record_has_required_fields(self, data):
        # From SCHEMA.md: all documented fields must be in the first record.
        required = {"id", "t", "tf", "c", "cp", "cl", "sc",
                    "d", "di", "dn", "p", "u",
                    "f",
                    "pc", "pcd", "pcdf", "pcdm", "pcdu",
                    "ec", "ecR", "ecS", "ecE", "ecN"}
        sample = data[0]
        missing = required - set(sample.keys())
        assert not missing, f"search.json record missing fields: {missing}"

    def test_quality_fields_removed(self, data):
        # Quality fields were completely removed — regression guard.
        forbidden = {"q", "qc", "qcat"}
        sample = data[0]
        leaked = forbidden & set(sample.keys())
        assert not leaked, f"quality fields still present in search.json: {leaked}"

    def test_fac_flag_boolean(self, data):
        for d in data[:100]:
            assert d["f"] in (0, 1)

    def test_url_relative(self, data):
        # u is relative to docs/, does not start with /
        for d in data[:100]:
            assert not d["u"].startswith("/"), f"absolute URL: {d['u']}"
            assert d["u"].endswith(".html")


# ---------------------------------------------------------------------------
# persons_search.json — person register search index
# ---------------------------------------------------------------------------

class TestPersonsSearchJson:
    """persons_search.json: array of persons, compact fields."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load(DOCS_DATA / "persons_search.json")

    def test_is_array(self, data):
        assert isinstance(data, list)
        assert len(data) > 1000

    def test_record_has_required_fields(self, data):
        # Fields after rework: id, n/fn/sn (search index), sex, dc (>=1 by
        # construction), am/ax (activity period), co (corpus list),
        # i0/cl0 (anchor for sub-label), rl (roles). d/qw are dropped.
        required = {"id", "n", "fn", "sn", "sex",
                    "dc", "am", "ax", "co", "i0", "cl0", "rl"}
        sample = data[0]
        missing = required - set(sample.keys())
        assert not missing, f"persons_search.json record missing: {missing}"

    def test_id_prefix(self, data):
        for p in data[:50]:
            assert p["id"].startswith("pe__"), f"id without pe__: {p['id']}"

    def test_sex_values(self, data):
        # sex is m/f or empty (per SCHEMA)
        for p in data[:100]:
            assert p["sex"] in ("m", "f", ""), f"unexpected sex {p['sex']!r}"

    def test_dc_at_least_one(self, data):
        # By construction: only persons with at least one released source
        # mention enter the register.
        for p in data[:200]:
            assert p["dc"] >= 1, f"dc < 1 in released register: {p['id']}"

    def test_roles_in_vocabulary(self, data):
        # Role vocabulary controlled to four values.
        valid = {"issuer", "recipient", "witness", "other"}
        for p in data[:200]:
            for r in p.get("rl", []):
                assert r in valid, f"unexpected role {r!r} in {p['id']}"


# ---------------------------------------------------------------------------
# register/{persons,organisations,places}.json — reverse index
# ---------------------------------------------------------------------------

class TestRegisterReverseJson:
    """register/*.json: entity_id -> [doc-record], compact fields."""

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
# categories.json — editorial org-type mappings
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
# query_vocabulary.json — analysis composer vocabulary
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
# docs_lookup.json — file_key -> metadata lookup
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
# Cross-file consistency: SCHEMA.md mentions versioning fields
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
