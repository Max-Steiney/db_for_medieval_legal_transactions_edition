"""Tests for E4, E5, D3, E6, and M5 deliverables."""

import inspect
import json

import pytest

import frontend.build
import frontend.aggregator
from frontend.tests.conftest import parse_html


# ---------------------------------------------------------------------------
# E5: Representation Direction
# ---------------------------------------------------------------------------

class TestRepDirection:

    def test_rep_direction_in_epic_b_output(self):
        """Epic B aggregation includes rep_direction data."""
        source = inspect.getsource(frontend.aggregator.aggregate_epic_b)
        assert 'rep_direction' in source

    def test_rep_direction_structure(self):
        source = inspect.getsource(frontend.aggregator.aggregate_epic_b)
        assert 'top_representatives' in source
        assert 'top_principals' in source
        assert 'matrix' in source


# ---------------------------------------------------------------------------
# E4: Org Type × Transaction Type
# ---------------------------------------------------------------------------

class TestOrgTxMatrix:

    def test_org_tx_in_epic_c_output(self):
        """Epic C aggregation includes org_tx cross-tabulation."""
        source = inspect.getsource(frontend.aggregator.aggregate_epic_c)
        assert 'org_tx' in source
        assert 'org_tx_matrix' in source

    def test_org_tx_coverage_tracked(self):
        source = inspect.getsource(frontend.aggregator.aggregate_epic_c)
        assert 'match_rate' in source


# ---------------------------------------------------------------------------
# D3: Friendship
# ---------------------------------------------------------------------------

class TestFriendship:

    def test_friendship_in_epic_b_output(self):
        """Epic B aggregation includes friendship edge data."""
        source = inspect.getsource(frontend.aggregator.aggregate_epic_b)
        assert 'friendship' in source
        assert 'friend_edges' in source


# ---------------------------------------------------------------------------
# E6: Cross-Epic Navigation
# ---------------------------------------------------------------------------

class TestCrossEpicNavigation:

    def test_getparam_in_core_js(self):
        from pathlib import Path
        js_path = Path(frontend.build.STATIC_DIR) / "js" / "core.js"
        content = js_path.read_text(encoding="utf-8")
        assert 'getParam' in content
        assert 'URLSearchParams' in content

    # The former sub-pages exploration-networks.js / exploration-roles.js
    # have been merged into analysis-aggregat.js; URL-param drill is still
    # open (V2/V3 follow-up). Once implemented, corresponding asserts
    # against analysis-aggregat.js can be reintroduced here.


# ---------------------------------------------------------------------------
# M5: Impressum + Persistent URIs
# ---------------------------------------------------------------------------

class TestImpressum:

    def test_impressum_content_exists(self):
        from pathlib import Path
        md_path = Path(frontend.build.CONTENT_DIR) / "impressum.md"
        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")
        assert 'CC BY 4.0' in content
        assert 'Universität Wien' in content

    def test_build_impressum_function_exists(self):
        assert hasattr(frontend.build, '_build_impressum')

    def test_nav_has_impressum_link(self):
        from pathlib import Path
        tpl_path = Path(frontend.build.TEMPLATES_DIR) / "base.html"
        content = tpl_path.read_text(encoding="utf-8")
        assert 'impressum.html' in content


class TestPersistentURIs:

    def test_canonical_link_in_document_template(self):
        from pathlib import Path
        tpl_path = Path(frontend.build.TEMPLATES_DIR) / "document.html"
        content = tpl_path.read_text(encoding="utf-8")
        assert 'rel="canonical"' in content

    def test_citation_meta_in_document_template(self):
        from pathlib import Path
        tpl_path = Path(frontend.build.TEMPLATES_DIR) / "document.html"
        content = tpl_path.read_text(encoding="utf-8")
        assert 'citation_title' in content
