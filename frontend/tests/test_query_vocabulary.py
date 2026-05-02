"""Tests fuer das Query-Vokabular des Composers.

Pruefen:
  1. Schema-Konsistenz von ``frontend/content/query_vocabulary.json``.
  2. Drift zwischen Vokabular und tatsaechlichen Daten (sex-Werte,
     korpus-Werte, rel_type-Werte, org_category-Werte).
  3. Build-Output: ``docs/data/query_vocabulary.json`` wird erzeugt.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import frontend.build
from frontend.build import _write_query_vocabulary
from frontend.config import CONTENT_DIR, DATA_DIR


VOCAB_PATH = CONTENT_DIR / "query_vocabulary.json"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def _vocab() -> dict:
    assert VOCAB_PATH.exists(), f"missing: {VOCAB_PATH}"
    return json.loads(VOCAB_PATH.read_text(encoding="utf-8"))


def test_vocab_has_required_top_level_keys():
    v = _vocab()
    for key in ("subjects", "filters", "coverage", "constraints"):
        assert key in v, f"missing top-level key: {key}"


def test_vocab_subjects_have_required_fields():
    v = _vocab()
    for sid, sdef in v["subjects"].items():
        assert "label" in sdef, f"subject {sid}: missing label"
        assert "filters" in sdef, f"subject {sid}: missing filters"
        for fid in sdef["filters"]:
            assert fid in v["filters"], (
                f"subject {sid} references unknown filter '{fid}'"
            )


def test_vocab_filters_have_required_fields():
    v = _vocab()
    for fid, fdef in v["filters"].items():
        assert "label" in fdef, f"filter {fid}: missing label"
        assert (
            "values" in fdef
            or fdef.get("value_kind") in ("range", "from_data")
        ), f"filter {fid}: needs values or value_kind"


def test_vocab_constraints_max_filters_is_positive_int():
    v = _vocab()
    n = v["constraints"]["max_active_filters"]
    assert isinstance(n, int) and n >= 1


def test_vocab_coverage_has_entry_per_subject():
    v = _vocab()
    for sid in v["subjects"]:
        assert sid in v["coverage"], f"missing coverage for subject '{sid}'"


# ---------------------------------------------------------------------------
# Drift gegen Daten
# ---------------------------------------------------------------------------


def _load_data(name: str) -> dict | None:
    p = DATA_DIR / name
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def test_vocab_sex_values_match_epic_a_coverage():
    epic_a = _load_data("epic_a.json")
    if epic_a is None:
        pytest.skip("docs/data/epic_a.json not built yet")
    vocab_sex = {o["value"] for o in _vocab()["filters"]["sex"]["values"]}
    real = set(epic_a["coverage"]["sex_distribution"].keys())
    assert vocab_sex == real - {"unspecified"}, (
        f"sex drift: vocab={vocab_sex}, data={real}"
    )


def test_vocab_role_values_match_epic_a_role_by_sex():
    epic_a = _load_data("epic_a.json")
    if epic_a is None:
        pytest.skip("docs/data/epic_a.json not built yet")
    vocab_roles = {o["value"] for o in _vocab()["filters"]["role"]["values"]}
    real = set(epic_a["observations"]["role_by_sex"].keys()) - {""}
    assert vocab_roles <= real, f"vocab roles not in data: {vocab_roles - real}"


def test_vocab_korpus_values_match_timeline_collections():
    timeline = _load_data("timeline.json")
    if timeline is None:
        pytest.skip("docs/data/timeline.json not built yet")
    vocab_k = {o["value"] for o in _vocab()["filters"]["korpus"]["values"]}
    real = set(timeline["collections"].keys())
    assert vocab_k == real, f"korpus drift: vocab={vocab_k}, data={real}"


def test_vocab_org_category_values_match_categories_json():
    cats_path = CONTENT_DIR / "categories.json"
    if not cats_path.exists():
        pytest.skip("categories.json missing")
    cats = json.loads(cats_path.read_text(encoding="utf-8"))
    vocab_cat = {o["value"] for o in _vocab()["filters"]["org_category"]["values"]}
    real = set(cats["categories"].keys())
    assert vocab_cat == real


def test_vocab_rel_type_values_match_epic_b_type_counts():
    epic_b = _load_data("epic_b.json")
    if epic_b is None:
        pytest.skip("docs/data/epic_b.json not built yet")
    vocab_t = {o["value"] for o in _vocab()["filters"]["rel_type"]["values"]}
    real = set(epic_b["coverage"]["type_counts"].keys())
    assert vocab_t == real, f"rel_type drift: vocab={vocab_t}, data={real}"


# ---------------------------------------------------------------------------
# Build-Output
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    from frontend.tests.conftest import patch_build_path
    docs = tmp_path / "docs"
    data = docs / "data"
    data.mkdir(parents=True)
    patch_build_path(monkeypatch, "DOCS_DIR", docs)
    patch_build_path(monkeypatch, "DATA_DIR", data)
    return data


def test_write_query_vocabulary_creates_output(isolated_data_dir):
    _write_query_vocabulary()
    out = isolated_data_dir / "query_vocabulary.json"
    assert out.exists()
    written = json.loads(out.read_text(encoding="utf-8"))
    assert "subjects" in written
    assert "filters" in written
    assert "created" in written.get("meta", {}), "build must inject meta.created"
