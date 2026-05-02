"""Tests for M3: Entity Quality + Scholarly Functions.

Tests cover:
- Entity quality worst-score computation (_entity_quality_worst)
- Quality field (qw) in register search data
- Factoid view HTML structure (toggle button, container)
- Citation helper HTML structure (toggle button, popover, doc-meta JSON)
- Quality filter dropdown on register pages
"""

import json

import pytest

from frontend.build import (
    _entity_quality_worst,
    _person_search_data,
    _org_search_data,
    _place_search_data,
)


# --- Entity quality worst score ---


class TestEntityQualityWorst:
    """Test _entity_quality_worst aggregation."""

    def test_no_documents_returns_minus_one(self):
        assert _entity_quality_worst("pe__none", {}) == -1

    def test_single_ok_document(self):
        reverse = {"pe__x": [{"quality_score": 0}]}
        assert _entity_quality_worst("pe__x", reverse) == 0

    def test_single_warning_document(self):
        reverse = {"pe__x": [{"quality_score": 2}]}
        assert _entity_quality_worst("pe__x", reverse) == 2

    def test_mixed_scores_returns_worst(self):
        reverse = {"pe__x": [
            {"quality_score": 0},
            {"quality_score": 1},
            {"quality_score": 2},
        ]}
        assert _entity_quality_worst("pe__x", reverse) == 2

    def test_all_notices_returns_notice(self):
        reverse = {"pe__x": [
            {"quality_score": 1},
            {"quality_score": 1},
        ]}
        assert _entity_quality_worst("pe__x", reverse) == 1

    def test_missing_quality_score_defaults_to_zero(self):
        reverse = {"pe__x": [{"url": "x.html"}]}
        assert _entity_quality_worst("pe__x", reverse) == 0


# --- Quality field in register search data ---


class TestRegisterSearchDataQuality:
    """Test that qw field is present in all register search data."""

    def test_person_search_data_has_qw(self):
        persons = {"pe__test": {
            "forename": "Hans", "surname": "Test", "addName": "",
            "death": "", "display": "Hans Test", "sex": "m",
        }}
        reverse = {"pe__test": [
            {"url": "x.html", "idno": "1", "quality_score": 2},
        ]}
        data = _person_search_data(persons, reverse)
        assert data[0]["qw"] == 2

    def test_person_no_docs_qw_minus_one(self):
        persons = {"pe__test": {
            "forename": "Hans", "surname": "Test", "addName": "",
            "death": "", "display": "Hans Test", "sex": "m",
        }}
        data = _person_search_data(persons, {})
        assert data[0]["qw"] == -1

    def test_org_search_data_has_qw(self):
        orgs = {"org__test": {"name": "Test Org", "type": "Kloster"}}
        reverse = {"org__test": [
            {"url": "x.html", "idno": "1", "quality_score": 1},
        ]}
        data = _org_search_data(orgs, reverse)
        assert data[0]["qw"] == 1

    def test_place_search_data_has_qw(self):
        places = {"pl__test": {
            "name": "Wien", "type": "settlement", "lat": "", "lng": "",
        }}
        reverse = {"pl__test": [
            {"url": "x.html", "idno": "1", "quality_score": 0},
        ]}
        data = _place_search_data(places, reverse)
        assert data[0]["qw"] == 0


# --- Template structure tests ---


class TestDocumentTemplateM3:
    """Test that document.html contains M3 elements."""

    @pytest.fixture(scope="class")
    def template_html(self):
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "document.html"
        return template_path.read_text(encoding="utf-8")

    def test_factoid_toggle_button(self, template_html):
        assert 'id="factoid-toggle"' in template_html

    def test_factoid_view_container(self, template_html):
        assert 'id="factoid-view"' in template_html

    def test_cite_toggle_button(self, template_html):
        assert 'id="cite-toggle"' in template_html

    def test_cite_popover_container(self, template_html):
        assert 'id="cite-popover"' in template_html

    def test_doc_meta_json_script(self, template_html):
        assert 'id="doc-meta"' in template_html
        assert 'type="application/json"' in template_html


class TestRegisterTemplateM3:
    """Test that register_list.html contains M3 elements."""

    @pytest.fixture(scope="class")
    def template_html(self):
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "register_list.html"
        return template_path.read_text(encoding="utf-8")

    def test_quality_filter_dropdown_removed(self, template_html):
        # Reader-facing Quality-UI im Register entfernt (analog Quellseite):
        # Pipeline-Validation-Findings sind editor-internes Pruefmittel,
        # kein Leser-relevantes Qualitaetssignal.
        assert 'id="filter-quality"' not in template_html

    def test_quality_column_removed(self, template_html):
        assert 'data-sort="qw"' not in template_html

    def test_quality_filter_options_removed(self, template_html):
        assert "Fehlerfrei" not in template_html
        assert "Warnungen" not in template_html


# --- JS structure tests ---


class TestDocumentJsM3:
    """Test that document.js contains M3 init functions."""

    @pytest.fixture(scope="class")
    def js_source(self):
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "static" / "js" / "document.js"
        return js_path.read_text(encoding="utf-8")

    def test_factoid_view_function(self, js_source):
        assert "initFactoidView" in js_source

    def test_citation_helper_function(self, js_source):
        assert "initCitationHelper" in js_source


class TestRegisterJsM3:
    """Test that register.js wires the quality filter."""

    @pytest.fixture(scope="class")
    def js_source(self):
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "static" / "js" / "register.js"
        return js_path.read_text(encoding="utf-8")

    def test_quality_filter_not_in_register(self, js_source):
        assert "filter-quality" not in js_source


# --- CSS structure tests ---


class TestRegisterCssM3:
    """Test that register.css carries the quality indicator styles."""

    @pytest.fixture(scope="class")
    def css_source(self):
        from pathlib import Path
        css_path = Path(__file__).parent.parent / "static" / "css" / "register.css"
        return css_path.read_text(encoding="utf-8")

    def test_quality_indicator_styles(self, css_source):
        assert ".quality-ok" in css_source
        assert ".quality-notice" in css_source
        assert ".quality-warning" in css_source


class TestDocumentCssM3:
    """Test that document.css carries factoid + citation styles."""

    @pytest.fixture(scope="class")
    def css_source(self):
        from pathlib import Path
        css_path = Path(__file__).parent.parent / "static" / "css" / "document.css"
        return css_path.read_text(encoding="utf-8")

    def test_factoid_table_styles(self, css_source):
        assert ".factoid-table" in css_source

    def test_cite_popover_styles(self, css_source):
        assert ".cite-popover" in css_source
