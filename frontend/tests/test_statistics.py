"""Tests for statistics dashboard: metadata extraction and page generation."""

import json
import re
import pytest

from pipeline.config import SOURCES_DIR, NS_MAP
from pipeline.utils.xml_loader import load_xml

from frontend.build import _extract_metadata
from frontend.config import DOCS_DIR


# --- Metadata extraction: statistics fields ---


class TestStatisticsExtraction:
    """Test that _extract_metadata returns the statistics fields."""

    @pytest.fixture(scope="class")
    def meta_doc_100(self):
        """Extract metadata from document 100."""
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        tree = load_xml(filepath)
        return _extract_metadata(tree, filepath)

    def test_event_count_present(self, meta_doc_100):
        assert "event_count" in meta_doc_100
        assert isinstance(meta_doc_100["event_count"], int)

    def test_fn_count_present(self, meta_doc_100):
        assert "fn_count" in meta_doc_100
        assert isinstance(meta_doc_100["fn_count"], int)

    def test_rolename_count_present(self, meta_doc_100):
        assert "rolename_count" in meta_doc_100
        assert isinstance(meta_doc_100["rolename_count"], int)

    def test_triggerstring_count_present(self, meta_doc_100):
        assert "triggerstring_count" in meta_doc_100
        assert isinstance(meta_doc_100["triggerstring_count"], int)

    def test_fn_role_counts_present(self, meta_doc_100):
        assert "fn_role_counts" in meta_doc_100
        assert isinstance(meta_doc_100["fn_role_counts"], dict)

    def test_fn_role_person_ids_present(self, meta_doc_100):
        """fn_role_person_ids maps roles to person ID lists."""
        assert "fn_role_person_ids" in meta_doc_100
        assert isinstance(meta_doc_100["fn_role_person_ids"], dict)
        all_ids = [pid for pids in meta_doc_100["fn_role_person_ids"].values() for pid in pids]
        assert len(all_ids) > 0
        assert all(pid.startswith("pe__") for pid in all_ids)

    def test_person_count_still_present(self, meta_doc_100):
        """Regression: existing person_count field must still be present."""
        assert "person_count" in meta_doc_100
        assert meta_doc_100["person_count"] > 0

    def test_event_count_positive(self, meta_doc_100):
        assert meta_doc_100["event_count"] > 0

    def test_fn_count_positive(self, meta_doc_100):
        assert meta_doc_100["fn_count"] > 0


# --- Statistics page generation (integration) ---


_JSON_RE = re.compile(
    r'<script id="stats-data" type="application/json">(.*?)</script>',
    re.DOTALL,
)


@pytest.fixture(scope="module")
def stats_json():
    """Extract and parse the embedded stats JSON from the built statistics page."""
    html = (DOCS_DIR / "project" / "statistics.html").read_text(encoding="utf-8")
    m = _JSON_RE.search(html)
    assert m, "JSON script tag not found in project/statistics.html"
    return json.loads(m.group(1))


class TestStatisticsPageGeneration:
    """Integration tests for the generated statistics page."""

    def test_stats_page_exists(self):
        assert (DOCS_DIR / "project" / "statistics.html").exists()

    def test_stats_json_embedded(self):
        html = (DOCS_DIR / "project" / "statistics.html").read_text(encoding="utf-8")
        assert '<script id="stats-data" type="application/json">' in html

    def test_stats_json_parseable(self, stats_json):
        expected_keys = {
            "summary", "timeline", "centuries", "collections",
            "fnRoles", "fnRolesSex", "annotationBreakdown", "personDistribution",
            "coverage", "topWomen", "topMen", "topOrgs", "perCollectionTop",
        }
        assert expected_keys.issubset(set(stats_json.keys()))

    def test_summary_fields(self, stats_json):
        summary = stats_json["summary"]
        assert summary["totalDocs"] > 0
        assert summary["totalPersons"] > 0
        assert summary["facsCount"] > 0
        assert 0 < summary["facsPct"] <= 100
        assert summary["avgAnnotations"] > 0

    def test_collections_have_decades(self, stats_json):
        for coll in stats_json["collections"]:
            assert "decades" in coll, f"Missing decades in {coll['label']}"
            assert isinstance(coll["decades"], dict)

    def test_summary_gender_counts(self, stats_json):
        summary = stats_json["summary"]
        assert "totalWomen" in summary
        assert "totalMen" in summary
        assert summary["totalWomen"] > 0
        assert summary["totalMen"] > 0
        assert summary["totalWomen"] + summary["totalMen"] <= summary["totalPersons"]

    def test_top_women_and_men(self, stats_json):
        assert len(stats_json["topWomen"]) > 0
        assert len(stats_json["topMen"]) > 0
        assert len(stats_json["topWomen"]) <= 10
        assert len(stats_json["topMen"]) <= 10
        for item in stats_json["topWomen"] + stats_json["topMen"]:
            assert "id" in item
            assert "name" in item
            assert "count" in item

    def test_fn_roles_sex_present(self, stats_json):
        fn_sex = stats_json["fnRolesSex"]
        assert "issuer" in fn_sex
        assert "m" in fn_sex["issuer"] or "f" in fn_sex["issuer"]

    def test_per_collection_top_gender_split(self, stats_json):
        for cp, top in stats_json["perCollectionTop"].items():
            assert "women" in top, f"Missing 'women' in perCollectionTop[{cp}]"
            assert "men" in top, f"Missing 'men' in perCollectionTop[{cp}]"
            assert "orgs" in top, f"Missing 'orgs' in perCollectionTop[{cp}]"
