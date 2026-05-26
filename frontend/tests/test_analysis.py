"""Tests for the analysis page build (categories validation, page render)."""

import json
from pathlib import Path

import pytest

import frontend.build
from frontend.build import _write_categories, _build_analysis, _init_jinja
from frontend.config import CONTENT_DIR, DATA_DIR


# ---- Source-of-truth (frontend/content/categories.json) ----------------------

def _load_source_categories():
    src = CONTENT_DIR / "categories.json"
    assert src.exists(), "frontend/content/categories.json missing"
    return json.loads(src.read_text(encoding="utf-8"))


def test_categories_source_has_required_schema():
    data = _load_source_categories()
    assert "meta" in data
    assert "categories" in data
    cats = data["categories"]
    assert set(cats.keys()) == {"geistlich", "weltlich", "sonstige"}
    assert all(isinstance(v, list) for v in cats.values())


def test_categories_are_disjoint():
    cats = _load_source_categories()["categories"]
    seen = []
    for tlist in cats.values():
        seen.extend(tlist)
    assert len(seen) == len(set(seen)), "an org_type appears in more than one category"


def test_categories_cover_roles_org_types():
    """Jeder im Pipeline-Output vorkommende org_type ist klassifiziert.

    Asymmetrische Pruefung: categories.json darf Typen vorrasten, die in
    der aktuellen Stufe noch nicht aktiv sind (z. B. Koenigreich erst in
    Stage 4). Pflicht ist nur, dass kein im Pipeline-Output erscheinender
    Typ unklassifiziert bleibt.
    """
    roles_path = DATA_DIR / "roles.json"
    if not roles_path.exists():
        pytest.skip("docs/data/roles.json not built yet")

    roles = json.loads(roles_path.read_text(encoding="utf-8"))
    real_types = set(roles.get("observations", {}).get("org_type_totals", {}).keys())
    cats = _load_source_categories()["categories"]
    mapped = {t for ts in cats.values() for t in ts}

    missing = real_types - mapped
    assert not missing, f"unclassified org_types: {sorted(missing)}"


# ---- Build-time output (docs/data/categories.json) ---------------------------

@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    """Redirect DATA_DIR and DOCS_DIR to a temp location for build tests."""
    from frontend.tests.conftest import patch_build_path
    docs = tmp_path / "docs"
    data = docs / "data"
    data.mkdir(parents=True)
    patch_build_path(monkeypatch, "DOCS_DIR", docs)
    patch_build_path(monkeypatch, "DATA_DIR", data)
    return data


def test_write_categories_creates_output(isolated_data_dir):
    _write_categories()
    out = isolated_data_dir / "categories.json"
    assert out.exists()
    written = json.loads(out.read_text(encoding="utf-8"))
    assert "categories" in written
    assert "created" in written.get("meta", {}), "build must inject meta.created"


def test_write_categories_validates_against_roles_when_present(isolated_data_dir, capsys):
    """If roles lives in DATA_DIR, the writer validates and warns on drift."""
    fake_epic = {"observations": {"org_type_totals": {"Stadt": 1, "Kloster_m": 2, "NEW_TYPE_X": 1}}}
    (isolated_data_dir / "roles.json").write_text(
        json.dumps(fake_epic), encoding="utf-8"
    )
    _write_categories()
    captured = capsys.readouterr()
    assert "NEW_TYPE_X" in captured.err


# ---- Page render -------------------------------------------------------------

def test_build_analysis_renders(docs_dir):
    env = _init_jinja()
    _build_analysis(env)
    out = docs_dir / "analysis" / "index.html"
    assert out.exists(), "analysis/index.html was not generated"
    content = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Abfragen" in content


def test_build_analysis_renders_constellation(docs_dir):
    """Constellation query containers plus resolver script are in the HTML."""
    env = _init_jinja()
    _build_analysis(env)
    content = (docs_dir / "analysis" / "index.html").read_text(encoding="utf-8")
    assert 'id="qb-persons-table"' in content
    assert 'id="qb-persons-tbody"' in content
    assert 'id="hits-table"' in content
    assert 'id="hits-tbody"' in content
    assert 'id="active-filters"' in content
    assert "analysis-resolver.js" in content
    assert "role-constellation-data" in content
    # Old galerie/composer artefacts are gone.
    assert 'id="composer"' not in content
    assert "analysis-capabilities.js" not in content
    assert "analysis-composer.js" not in content
    assert "analysis-gallery" not in content
    assert "analysis-questions.js" not in content
    assert "analysis-families.js" not in content
    assert "analysis-satzbuilder.js" not in content
