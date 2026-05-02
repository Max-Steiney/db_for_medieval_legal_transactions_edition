"""Tests for M1 deliverables: Annotation Toggle, TEI Download."""

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
        "filename": "100",
    }
    base.update(overrides)
    return base


@pytest.fixture(scope="module")
def jinja_env():
    """Create a Jinja2 environment for template rendering."""
    return frontend.build._init_jinja()


# ---------------------------------------------------------------------------
# Annotation Toggle
# ---------------------------------------------------------------------------

class TestAnnotationToggle:
    """Annotation-Layer-Toggle ist die Detail-Legende selbst — kein
    eigener Toolbar-Button und kein Dropdown-Popover mehr. Die Legende
    haelt vier `.legend-toggle`-Buttons mit `data-layer` und
    `aria-pressed`. JS in document.js togglet damit die `.doc-body`-
    Klassen `hide-{entities,functions,attributes,triggers}`.
    """

    def test_legend_toggles_present(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        toggles = finder.find_by_attr("data-layer")
        assert len(toggles) == 4

    def test_legend_toggle_layers_are_correct(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        finder = parse_html(html)
        toggles = finder.find_by_attr("data-layer")
        layers = {attrs["data-layer"] for _, attrs in toggles}
        assert layers == {"entities", "functions", "attributes", "triggers"}

    def test_no_toolbar_anno_button(self, jinja_env):
        html = _build_doc_html(_sample_meta(), "<p>Text</p>", jinja_env)
        # Regression-Guard: das alte Dropdown ist weg.
        assert 'id="anno-toggle"' not in html
        assert 'id="anno-toggle-popover"' not in html
        assert 'id="anno-toggle-all"' not in html


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
