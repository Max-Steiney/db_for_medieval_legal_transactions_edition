"""Tests for the three-page glossary demo build."""

import pytest

from frontend.build import _build_glossar_demo, _init_jinja


@pytest.fixture(scope="module")
def built_demo(docs_dir):
    env = _init_jinja()
    _build_glossar_demo(env)
    base = docs_dir / "project" / "glossar-demo"
    pages = {p: (base / f"{p}.html") for p in ("glossar", "technik", "tutorial")}
    contents = {}
    for name, path in pages.items():
        assert path.exists(), f"glossar-demo/{name}.html was not generated"
        contents[name] = path.read_text(encoding="utf-8")
    return contents


def test_all_three_pages_built(built_demo):
    assert set(built_demo) == {"glossar", "technik", "tutorial"}


def test_pages_have_native_chrome(built_demo):
    for name, content in built_demo.items():
        assert content.startswith("<!DOCTYPE html>"), name
        # base.html chrome marker: the project work name appears in header/footer
        assert "Stadt und Gemeinschaft Wien" in content, name
