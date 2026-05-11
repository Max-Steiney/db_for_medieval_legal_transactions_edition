"""Tests for M3: Scholarly Functions.

Tests cover:
- Factoid view HTML structure (toggle button, container)
- Citation helper HTML structure (toggle button, popover, doc-meta JSON)
- Regression guards: quality-related UI is gone
"""

import pytest


# --- Template structure tests ---


class TestDocumentTemplateM3:
    """Test that document.html contains M3 elements."""

    @pytest.fixture(scope="class")
    def template_html(self):
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "document.html"
        return template_path.read_text(encoding="utf-8")

    def test_annotations_view_container(self, template_html):
        # The annotations section is permanent, no toolbar toggle any more.
        assert 'id="factoid-view"' in template_html  # id stays (anchor-link stability)
        assert 'class="annotations-view"' in template_html

    def test_no_factoid_toggle_button(self, template_html):
        # Regression guard: the toolbar toggle is gone; the assertions
        # table is the permanent third area beside edition text and facsimile.
        assert 'id="factoid-toggle"' not in template_html

    def test_cite_toggle_button(self, template_html):
        assert 'id="cite-toggle"' in template_html

    def test_cite_popover_container(self, template_html):
        assert 'id="cite-popover"' in template_html

    def test_doc_meta_json_script(self, template_html):
        assert 'id="doc-meta"' in template_html
        assert 'type="application/json"' in template_html

    def test_quality_toggle_removed(self, template_html):
        assert 'id="quality-toggle"' not in template_html
        assert 'id="quality-panel"' not in template_html


class TestRegisterTemplateM3:
    """Test that register_list.html contains M3 elements."""

    @pytest.fixture(scope="class")
    def template_html(self):
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "register_list.html"
        return template_path.read_text(encoding="utf-8")

    def test_quality_filter_dropdown_removed(self, template_html):
        assert 'id="filter-quality"' not in template_html

    def test_quality_column_removed(self, template_html):
        assert 'data-sort="qw"' not in template_html


# --- JS structure tests ---


class TestDocumentJsM3:
    """Test that document.js contains M3 init functions."""

    @pytest.fixture(scope="class")
    def js_source(self):
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "static" / "js" / "document.js"
        return js_path.read_text(encoding="utf-8")

    def test_assertions_view_function(self, js_source):
        assert "initAssertionsView" in js_source

    def test_citation_helper_function(self, js_source):
        assert "initCitationHelper" in js_source

    def test_quality_panel_function_removed(self, js_source):
        assert "initQualityPanel" not in js_source


class TestRegisterJsM3:
    """Test that register.js does not wire any quality filter."""

    @pytest.fixture(scope="class")
    def js_source(self):
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "static" / "js" / "register.js"
        return js_path.read_text(encoding="utf-8")

    def test_quality_filter_not_in_register(self, js_source):
        assert "filter-quality" not in js_source


# --- CSS structure tests ---


class TestDocumentCssM3:
    """Test that document.css carries assertions + citation styles."""

    @pytest.fixture(scope="class")
    def css_source(self):
        from pathlib import Path
        css_path = Path(__file__).parent.parent / "static" / "css" / "document.css"
        return css_path.read_text(encoding="utf-8")

    def test_annotations_table_styles(self, css_source):
        assert ".annotations-table" in css_source

    def test_cite_popover_styles(self, css_source):
        assert ".cite-popover" in css_source

    def test_quality_styles_removed(self, css_source):
        assert ".toolbar-quality" not in css_source
        assert ".quality-panel" not in css_source
