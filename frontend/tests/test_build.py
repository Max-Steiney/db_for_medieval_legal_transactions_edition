"""Integration test: build a single file and verify HTML structure.

Uses monkeypatched DOCS_DIR to write into tmp_path, avoiding side effects
on the real docs/ working tree.
"""

import pytest
from pathlib import Path

from frontend.build import build_single
from frontend.tests.conftest import TagFinder


@pytest.fixture(scope="module")
def built_doc(docs_dir):
    """Build doc 100 into the shared temp docs directory."""
    build_single("sources/QGW/Vienna_1177-1414_ready/done/100.xml")

    output = docs_dir / "documents" / "QGW" / "Vienna_1177-1414_ready" / "100.html"
    assert output.exists(), f"Expected output file not found: {output}"
    content = output.read_text(encoding="utf-8")
    return output, content, docs_dir


def test_html_has_doctype(built_doc):
    _, content, _ = built_doc
    assert content.startswith("<!DOCTYPE html>")


def test_html_has_date(built_doc):
    _, content, _ = built_doc
    assert "1327" in content


def test_html_has_idno(built_doc):
    _, content, _ = built_doc
    finder = TagFinder()
    finder.feed(content)
    assert "100" in content


def test_html_has_annotation_spans(built_doc):
    _, content, _ = built_doc
    finder = TagFinder()
    finder.feed(content)
    assert finder.find_by_class("anno-person"), "No person annotations found"
    assert finder.find_by_class("anno-fn-issuer") or finder.find_by_class("anno-fn"), (
        "No function annotations found"
    )


def test_html_has_person_tooltip(built_doc):
    _, content, _ = built_doc
    assert "pe__konrad_chrannest" in content


def test_html_has_css_link(built_doc):
    _, content, _ = built_doc
    assert "base.css" in content
    assert "tokens.css" in content


def test_html_has_js_link(built_doc):
    _, content, _ = built_doc
    assert "core.js" in content


def test_static_files_copied(built_doc):
    """Static assets should be copied into the temp docs directory."""
    _, _, tmp_docs = built_doc
    assert (tmp_docs / "static" / "css" / "base.css").exists()
    assert (tmp_docs / "static" / "js" / "core.js").exists()


def test_done_not_in_path(built_doc):
    """The 'done' directory should be stripped from output paths."""
    output, _, _ = built_doc
    assert "done" not in str(output)


def test_canonical_is_absolute(built_doc):
    """Audit-Fix 20.07.2026: der canonical-Link war relativ und zeigte,
    gegen die Seiten-URL aufgeloest, auf einen nicht existierenden
    Doppelpfad. Er muss die absolute oeffentliche URL tragen."""
    from frontend.config import SITE_BASE_URL
    _, content, _ = built_doc
    expected = (f'<link rel="canonical" '
                f'href="{SITE_BASE_URL}/documents/QGW/'
                f'Vienna_1177-1414_ready/100.html">')
    assert expected in content
    assert '<link rel="canonical" href="documents/' not in content
