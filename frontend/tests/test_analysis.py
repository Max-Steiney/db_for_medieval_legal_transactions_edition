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


def test_categories_consistent_with_epic_a():
    """Every org_type produced by the pipeline must be classified.

    Schlaegt fehl, wenn die Pipeline neue Typen einfuehrt, ohne dass
    `frontend/content/categories.json` mitgepflegt wurde — bzw. wenn die
    JSON-Klassifikation Typen nennt, die nicht (mehr) in den Aggregaten
    vorkommen.
    """
    epic_a_path = DATA_DIR / "epic_a.json"
    if not epic_a_path.exists():
        pytest.skip("docs/data/epic_a.json not built yet")

    epic_a = json.loads(epic_a_path.read_text(encoding="utf-8"))
    real_types = set(epic_a.get("observations", {}).get("org_type_totals", {}).keys())
    cats = _load_source_categories()["categories"]
    mapped = {t for ts in cats.values() for t in ts}

    missing = real_types - mapped
    extra = mapped - real_types
    assert not missing, f"unclassified org_types: {sorted(missing)}"
    assert not extra, f"classified types not present in epic_a: {sorted(extra)}"


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


def test_write_categories_validates_against_epic_a_when_present(isolated_data_dir, capsys):
    """Wenn epic_a in DATA_DIR liegt, validiert der Writer und warnt bei Drift."""
    fake_epic = {"observations": {"org_type_totals": {"Stadt": 1, "Kloster_m": 2, "NEW_TYPE_X": 1}}}
    (isolated_data_dir / "epic_a.json").write_text(
        json.dumps(fake_epic), encoding="utf-8"
    )
    _write_categories()
    captured = capsys.readouterr()
    assert "NEW_TYPE_X" in captured.err  # missing type → warning


# ---- Page render -------------------------------------------------------------

def test_build_analysis_renders(docs_dir):
    env = _init_jinja()
    _build_analysis(env)
    out = docs_dir / "analysis" / "index.html"
    assert out.exists(), "analysis/index.html was not generated"
    content = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Analyse" in content


def test_build_analysis_renders_composer(docs_dir):
    """Composer- und Result-Container sowie die Composer-Skripte sind im HTML."""
    env = _init_jinja()
    _build_analysis(env)
    content = (docs_dir / "analysis" / "index.html").read_text(encoding="utf-8")
    assert 'id="composer"' in content
    assert 'id="result"' in content
    assert 'id="analysis-drilldown"' in content
    assert "analysis-capabilities.js" in content
    assert "analysis-composer.js" in content
    assert "analysis.js" in content
    # Header-Stats sind weg, kein Satz-Builder mehr
    assert "Institutionsbezug" not in content  # KPI lebt im Composer-Result
    assert "analysis-satzbuilder.js" not in content
    # Galerie und Familien-Builder sind weg
    assert "analysis-gallery" not in content
    assert "analysis-questions.js" not in content
    assert "analysis-families.js" not in content
