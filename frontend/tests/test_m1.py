"""Tests for M1 deliverables: Quality Strip, Annotation Toggle, TEI Download."""

import json
from pathlib import Path

import pytest
from lxml import etree

import frontend.build
from frontend.renderer import render_document
from frontend.tests.conftest import (
    EMPTY_REGISTERS, TEI, parse_html, tei,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_doc_html(meta, body_html, env):
    """Render the document template with given meta and body."""
    template = env.get_template("document.html")
    root_path = "."
    return template.render(meta=meta, body=body_html, root_path=root_path)


def _sample_meta(**overrides):
    """Create a minimal meta dict for template rendering."""
    base = {
        "idno": "100",
        "date_display": "1200",
        "collection_label": "QGW II/1",
        "collection_path": "QGW/Vienna_1177-1414_ready",
        "place": "Wien",
        "source_path": "sources/QGW/Vienna_1177-1414_ready/done/100.xml",
        "tei_url": "tei/QGW/Vienna_1177-1414_ready/100.xml",
        "url": "documents/QGW/Vienna_1177-1414_ready/100.html",
        "facsimile_urls": [],
        "source_url": None,
        "repository": None,
        "orig_date": None,
        "citation": None,
        "has_facsimile": False,
        "person_count": 3,
        "org_count": 1,
        "event_count": 1,
        "fn_count": 2,
        "rolename_count": 1,
        "triggerstring_count": 0,
        "prev_url": None,
        "prev_id": None,
        "next_url": None,
        "next_id": None,
        "quality_score": 0,
        "quality_findings": [],
        "quality_count": 0,
        "filename": "100",
    }
    base.update(overrides)
    return base


@pytest.fixture(scope="module")
def jinja_env():
    """Create a Jinja2 environment for template rendering."""
    return frontend.build._init_jinja()


# ---------------------------------------------------------------------------
# Quality Strip
# ---------------------------------------------------------------------------

class TestQualityStrip:

    def test_quality_badge_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        badges = finder.find_by_attr("id", "quality-toggle")
        assert len(badges) == 1

    def test_quality_badge_ok_for_clean_doc(self, jinja_env):
        meta = _sample_meta(quality_score=0, quality_count=0)
        html = _build_doc_html(meta, "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        badges = finder.find_by_class("toolbar-quality-ok")
        assert len(badges) == 1

    def test_quality_badge_warning_for_flagged_doc(self, jinja_env):
        findings = [{"severity": "warning", "category": "ref_null", "detail": "ref=NULL"}]
        meta = _sample_meta(quality_score=2, quality_count=1, quality_findings=findings)
        html = _build_doc_html(meta, "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        badges = finder.find_by_class("toolbar-quality-warning")
        assert len(badges) == 1

    def test_quality_panel_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        panels = finder.find_by_attr("id", "quality-panel")
        assert len(panels) == 1

    def test_quality_panel_empty_for_clean_doc(self, jinja_env):
        meta = _sample_meta(quality_score=0, quality_count=0)
        html = _build_doc_html(meta, "<p>Text</p>", jinja_env)
        assert "Keine Auff\u00e4lligkeiten" in html

    def test_quality_panel_shows_findings(self, jinja_env):
        findings = [
            {"severity": "warning", "category": "ref_null", "detail": "ref=NULL in line 5"},
            {"severity": "info", "category": "rs_no_type", "detail": "rs without type"},
        ]
        meta = _sample_meta(quality_score=2, quality_count=2, quality_findings=findings)
        html = _build_doc_html(meta, "<p>Text</p>", jinja_env)
        assert "ref_null" in html
        assert "rs_no_type" in html
        finder = parse_html(html)
        tables = finder.find_by_class("quality-table")
        assert len(tables) == 1

    def test_quality_score_in_doc_meta_json(self, jinja_env):
        meta = _sample_meta(quality_score=1)
        html = _build_doc_html(meta, "<p>Text</p>", jinja_env)
        # Extract JSON from script tag
        import re
        match = re.search(r'id="doc-meta"[^>]*>(.*?)</script>', html, re.DOTALL)
        assert match
        doc_meta = json.loads(match.group(1))
        assert doc_meta["quality_score"] == 1


# ---------------------------------------------------------------------------
# Annotation Toggle
# ---------------------------------------------------------------------------

class TestAnnotationToggle:

    def test_toggle_button_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        btns = finder.find_by_attr("id", "anno-toggle")
        assert len(btns) == 1

    def test_toggle_popover_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        popovers = finder.find_by_attr("id", "anno-toggle-popover")
        assert len(popovers) == 1

    def test_four_layer_checkboxes(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        checkboxes = finder.find_by_attr("data-layer")
        assert len(checkboxes) == 4

    def test_checkbox_layers_are_correct(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        checkboxes = finder.find_by_attr("data-layer")
        layers = {attrs["data-layer"] for _, attrs in checkboxes}
        assert layers == {"entities", "functions", "attributes", "triggers"}

    def test_toggle_all_button_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        btns = finder.find_by_attr("id", "anno-toggle-all")
        assert len(btns) == 1


# ---------------------------------------------------------------------------
# TEI Download
# ---------------------------------------------------------------------------

class TestTeiDownload:

    def test_download_link_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        links = finder.find_by_attr("download")
        assert len(links) >= 1
        # First download link should be the TEI download
        assert links[0][1].get("download") == "100.xml"

    def test_download_href_points_to_tei(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        links = finder.find_by_attr("download")
        assert len(links) >= 1
        href = links[0][1].get("href", "")
        assert "tei/" in href
        assert href.endswith(".xml")


class TestTeiOutputPath:

    def test_strips_done_directory(self):
        from pipeline.config import SOURCES_DIR
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        result = frontend.build._tei_output_path(filepath)
        assert "done" not in result.parts
        assert result.name == "100.xml"
        assert "tei" in result.parts

    def test_preserves_collection_path(self):
        from pipeline.config import SOURCES_DIR
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        result = frontend.build._tei_output_path(filepath)
        rel = str(result).replace("\\", "/")
        assert "QGW/Vienna_1177-1414_ready/100.xml" in rel


# ---------------------------------------------------------------------------
# Top Persons (E7) — Statistics page wurde entfernt; Test wurde mitentfernt.
# Top-Persons-Listen leben jetzt im Personenregister.
# ---------------------------------------------------------------------------
