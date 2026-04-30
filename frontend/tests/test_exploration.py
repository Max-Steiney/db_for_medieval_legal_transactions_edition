"""Tests for exploration pages: hub, roles subpage, placeholder subpages, data files."""

import json
import pytest

from frontend.config import DOCS_DIR, DATA_DIR


class TestEpicADrillDown:
    """Verify epic_a.json includes drill_down data after aggregation."""

    @pytest.fixture(scope="class")
    def epic_a(self):
        path = DATA_DIR / "epic_a.json"
        if not path.exists():
            pytest.skip("epic_a.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_drill_down_key_present(self, epic_a):
        assert "drill_down" in epic_a

    def test_drill_down_has_role_sex(self, epic_a):
        dd = epic_a["drill_down"]
        assert "role_sex" in dd

    def test_drill_down_issuer_has_m_and_f(self, epic_a):
        dd = epic_a["drill_down"]["role_sex"]
        assert "issuer" in dd
        assert "m" in dd["issuer"]
        assert "f" in dd["issuer"]

    def test_drill_down_file_keys_are_lists(self, epic_a):
        dd = epic_a["drill_down"]["role_sex"]
        for role, sex_map in dd.items():
            for sex, fkeys in sex_map.items():
                assert isinstance(fkeys, list), f"{role}/{sex} should be a list"

    def test_drill_down_file_keys_start_with_f(self, epic_a):
        """All file_keys should start with 'f__'."""
        dd = epic_a["drill_down"]["role_sex"]
        for role, sex_map in dd.items():
            for sex, fkeys in sex_map.items():
                for fk in fkeys[:5]:  # spot-check first 5
                    assert fk.startswith("f__"), f"Bad file_key: {fk}"


class TestDocsLookup:
    """Verify docs_lookup.json structure."""

    @pytest.fixture(scope="class")
    def lookup(self):
        path = DATA_DIR / "docs_lookup.json"
        if not path.exists():
            pytest.skip("docs_lookup.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_lookup_not_empty(self, lookup):
        assert len(lookup) > 100

    def test_lookup_keys_start_with_f(self, lookup):
        sample = list(lookup.keys())[:10]
        for fk in sample:
            assert fk.startswith("f__"), f"Bad key: {fk}"

    def test_lookup_entries_have_required_fields(self, lookup):
        sample = list(lookup.values())[:10]
        for entry in sample:
            assert "u" in entry, "Missing url"
            assert "i" in entry, "Missing idno"
            assert "d" in entry, "Missing date"
            assert "c" in entry, "Missing collection"

    def test_lookup_urls_point_to_html(self, lookup):
        sample = list(lookup.values())[:10]
        for entry in sample:
            assert entry["u"].endswith(".html"), f"Bad url: {entry['u']}"


class TestExplorationHub:
    """Verify exploration.html hub page is generated with expected structure."""

    @pytest.fixture(scope="class")
    def html(self):
        path = DOCS_DIR / "exploration.html"
        if not path.exists():
            pytest.skip("exploration.html not found (run full build first)")
        return path.read_text(encoding="utf-8")

    def test_page_has_exploration_id(self, html):
        assert 'id="exploration-page"' in html

    def test_page_has_hub_grid(self, html):
        assert 'explore-hub-grid' in html

    def test_page_links_to_roles(self, html):
        assert 'exploration_roles.html' in html

    def test_page_links_to_networks(self, html):
        assert 'exploration_networks.html' in html

    def test_page_links_to_transactions(self, html):
        assert 'exploration_transactions.html' in html

    def test_page_links_to_places(self, html):
        assert 'exploration_places.html' in html

    def test_page_has_transparency_bar(self, html):
        assert 'id="explore-transparency"' in html


class TestExplorationRoles:
    """Verify exploration_roles.html subpage with Epic A content."""

    @pytest.fixture(scope="class")
    def html(self):
        path = DOCS_DIR / "exploration_roles.html"
        if not path.exists():
            pytest.skip("exploration_roles.html not found (run full build first)")
        return path.read_text(encoding="utf-8")

    def test_page_has_exploration_id(self, html):
        assert 'id="exploration-page"' in html

    def test_page_no_longer_embeds_epic_a_data(self, html):
        """Epic A data is now loaded from external JSON, not embedded."""
        assert 'id="explore-epic-a-data"' not in html

    def test_page_has_no_subnav(self, html):
        """Subnav removed — top nav dropdown is sufficient."""
        assert 'explore-subnav' not in html

    def test_page_has_filter_header(self, html):
        assert 'id="explore-filters"' in html

    def test_page_has_role_chart_container(self, html):
        assert 'id="explore-role-chart"' in html

    def test_page_has_drilldown_overlay(self, html):
        assert 'id="explore-drilldown"' in html

    def test_page_has_institution_chart(self, html):
        assert 'id="explore-inst-chart"' in html

    def test_page_has_unified_header(self, html):
        assert 'explore-header-unified' in html


class TestExplorationPlaceholderPages:
    """Verify placeholder subpages (networks) exist."""

    @pytest.mark.parametrize("filename,expected_title", [
        ("exploration_networks.html", "Beziehungen"),
        ("exploration_transactions.html", "Transaktionen"),
        ("exploration_places.html", "Orte"),
    ])
    def test_placeholder_page_exists_and_has_title(self, filename, expected_title):
        path = DOCS_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not found (run full build first)")
        html = path.read_text(encoding="utf-8")
        assert expected_title in html

    @pytest.mark.parametrize("filename", [
        "exploration_networks.html",
        "exploration_transactions.html",
        "exploration_places.html",
    ])
    def test_placeholder_page_has_no_subnav(self, filename):
        """Subnav removed — top nav dropdown is sufficient."""
        path = DOCS_DIR / filename
        if not path.exists():
            pytest.skip(f"{filename} not found (run full build first)")
        html = path.read_text(encoding="utf-8")
        assert 'explore-subnav' not in html

    def test_networks_page_has_relationship_panels(self):
        path = DOCS_DIR / "exploration_networks.html"
        if not path.exists():
            pytest.skip("exploration_networks.html not found (run full build first)")
        html = path.read_text(encoding="utf-8")
        assert 'explore-rel-chart' in html
        assert 'explore-panel-labels' in html
        assert 'explore-panel-detail' in html


class TestEpicBData:
    """Verify epic_b.json has correct structure for Relationship Explorer."""

    @pytest.fixture(scope="class")
    def epic_b(self):
        path = DATA_DIR / "epic_b.json"
        if not path.exists():
            pytest.skip("epic_b.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_overview(self, epic_b):
        assert "overview" in epic_b
        tbs = epic_b["overview"]["type_by_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            assert t in tbs
            for s in ["m", "f", "unspecified"]:
                assert s in tbs[t]

    def test_has_labels(self, epic_b):
        labels = epic_b["labels"]
        assert len(labels) > 100
        top = labels[0]
        assert "label" in top
        assert "type" in top
        assert "m" in top
        assert "f" in top
        assert "total" in top

    def test_has_persons(self, epic_b):
        persons = epic_b["persons"]
        assert len(persons) > 3000
        p = persons[0]
        assert "id" in p
        assert "name" in p
        assert "sex" in p
        assert "rels" in p

    def test_coverage(self, epic_b):
        cov = epic_b["coverage"]
        assert cov["total_relations"] > 10000
        assert cov["persons_with_relations"] > 3000

    def test_json_size(self):
        path = DATA_DIR / "epic_b.json"
        if not path.exists():
            pytest.skip("epic_b.json not found")
        size_mb = path.stat().st_size / (1024 * 1024)
        assert size_mb < 5, f"epic_b.json is {size_mb:.1f} MB, expected < 5 MB"

    def test_has_drill_down(self, epic_b):
        dd = epic_b["drill_down"]
        assert "type_sex" in dd
        assert "label_sex" in dd


class TestEpicDData:
    """Verify epic_d.json has correct structure for Place Explorer."""

    @pytest.fixture(scope="class")
    def epic_d(self):
        path = DATA_DIR / "epic_d.json"
        if not path.exists():
            pytest.skip("epic_d.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_places(self, epic_d):
        assert "places" in epic_d
        assert len(epic_d["places"]) > 2000

    def test_places_have_required_fields(self, epic_d):
        for p in epic_d["places"][:20]:
            assert "id" in p
            assert "name" in p
            assert "type" in p
            assert "referenced" in p
            assert "has_coords" in p
            assert "doc_count" in p
            assert "decades" in p
            assert isinstance(p["decades"], list)

    def test_settlements_with_coords_have_file_keys(self, epic_d):
        settlements = [p for p in epic_d["places"]
                       if p["type"] == "settlement" and p["has_coords"]
                       and p["doc_count"] > 0]
        assert len(settlements) > 0
        for p in settlements[:10]:
            assert "file_keys" in p
            assert len(p["file_keys"]) == p["doc_count"]

    def test_non_settlement_entries_may_have_file_keys(self, epic_d):
        """All referenced places (incl. immo) carry file_keys for cross-Epic linking.

        Updated 2026-04 (commit b4cba658de): aggregator now emits file_keys for
        every referenced place, not only settlements with coords. This enables
        bidirectional navigation from any place entry into source documents.
        """
        immos = [p for p in epic_d["places"] if p["type"] == "immo"]
        # We don't enforce presence/absence — just that the schema is consistent
        # (file_keys, where present, is a list aligned with doc_count).
        for p in immos[:20]:
            if "file_keys" in p:
                assert isinstance(p["file_keys"], list)
                assert len(p["file_keys"]) == p["doc_count"]

    def test_coverage_has_type_counts(self, epic_d):
        cov = epic_d["coverage"]
        assert "type_counts" in cov
        assert "settlement" in cov["type_counts"]
        assert "immo" in cov["type_counts"]

    def test_coverage_has_settlement_stats(self, epic_d):
        cov = epic_d["coverage"]
        assert "settlements_with_coords" in cov
        assert cov["settlements_with_coords"] > 100

    def test_coverage_has_doc_links(self, epic_d):
        cov = epic_d["coverage"]
        assert "total_doc_links" in cov
        assert cov["total_doc_links"] > 0

    def test_place_types_are_canonical(self, epic_d):
        types = set(p["type"] for p in epic_d["places"])
        assert types <= {"settlement", "immo", "street", "river", ""}


class TestExplorationPlaces:
    """Verify exploration_places.html is functional (not placeholder)."""

    @pytest.fixture(scope="class")
    def html(self):
        path = DOCS_DIR / "exploration_places.html"
        if not path.exists():
            pytest.skip("exploration_places.html not found")
        return path.read_text(encoding="utf-8")

    def test_page_has_exploration_id(self, html):
        assert 'id="exploration-page"' in html

    def test_page_has_map_panel(self, html):
        assert 'id="explore-panel-map"' in html

    def test_page_has_places_panel(self, html):
        assert 'id="explore-panel-places"' in html

    def test_page_has_map_container(self, html):
        assert 'id="explore-map"' in html

    def test_page_has_place_search(self, html):
        assert 'id="explore-place-search"' in html

    def test_page_has_drilldown_overlay(self, html):
        assert 'id="explore-drilldown"' in html

    def test_page_has_unified_header(self, html):
        assert 'explore-header-unified' in html

    def test_page_has_time_slider(self, html):
        assert 'id="explore-range-min"' in html

    def test_page_is_not_placeholder(self, html):
        assert 'In Entwicklung' not in html

    def test_page_loads_leaflet(self, html):
        assert 'leaflet' in html.lower()

    def test_page_has_title(self, html):
        assert 'Orte' in html


class TestEpicCData:
    """Verify epic_c.json has correct structure for Transaction Explorer."""

    @pytest.fixture(scope="class")
    def epic_c(self):
        path = DATA_DIR / "epic_c.json"
        if not path.exists():
            pytest.skip("epic_c.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_observations(self, epic_c):
        assert "observations" in epic_c

    def test_has_tx_timeline(self, epic_c):
        assert "tx_timeline" in epic_c["observations"]

    def test_tx_timeline_has_not_normalised(self, epic_c):
        tl = epic_c["observations"]["tx_timeline"]
        assert "_not_normalised" in tl

    def test_tx_timeline_not_normalised_has_significant_count(self, epic_c):
        """The 'not normalised' category should have substantial counts."""
        tl = epic_c["observations"]["tx_timeline"]
        not_norm_total = sum(tl["_not_normalised"].values())
        assert not_norm_total > 500, (
            f"_not_normalised ({not_norm_total}) should be > 500"
        )

    def test_has_recipient_type_totals(self, epic_c):
        assert "recipient_type_totals" in epic_c["observations"]

    def test_recipient_type_totals_not_empty(self, epic_c):
        assert len(epic_c["observations"]["recipient_type_totals"]) > 5

    def test_has_triggerstrings(self, epic_c):
        assert "triggerstrings" in epic_c
        assert len(epic_c["triggerstrings"]) > 100

    def test_triggerstrings_have_required_fields(self, epic_c):
        for ts in epic_c["triggerstrings"][:10]:
            assert "form" in ts
            assert "freq" in ts
            assert "norm" in ts or ts["norm"] == ""
            assert "doc_count" in ts
            assert "file_keys" in ts

    def test_triggerstrings_file_keys_match_doc_count(self, epic_c):
        """file_keys list length should equal doc_count."""
        for ts in epic_c["triggerstrings"][:20]:
            assert len(ts["file_keys"]) == ts["doc_count"], (
                f"'{ts['form']}': file_keys={len(ts['file_keys'])} "
                f"!= doc_count={ts['doc_count']}"
            )

    def test_triggerstrings_sorted_by_freq_desc(self, epic_c):
        freqs = [ts["freq"] for ts in epic_c["triggerstrings"]]
        assert freqs == sorted(freqs, reverse=True)

    def test_has_recipients(self, epic_c):
        assert "recipients" in epic_c
        assert len(epic_c["recipients"]) > 10

    def test_recipients_have_required_fields(self, epic_c):
        for r in epic_c["recipients"][:10]:
            assert "id" in r
            assert "name" in r
            assert "type" in r
            assert "count" in r

    def test_recipients_sorted_by_count_desc(self, epic_c):
        counts = [r["count"] for r in epic_c["recipients"]]
        assert counts == sorted(counts, reverse=True)

    def test_has_org_supporters(self, epic_c):
        assert "org_supporters" in epic_c
        assert len(epic_c["org_supporters"]) > 10

    def test_org_supporters_have_file_keys(self, epic_c):
        sample_key = list(epic_c["org_supporters"].keys())[0]
        supporters = epic_c["org_supporters"][sample_key]
        assert len(supporters) > 0
        assert "file_key" in supporters[0]
        assert "person_key" in supporters[0]
        assert "role" in supporters[0]

    def test_has_drill_down(self, epic_c):
        assert "drill_down" in epic_c
        assert "tx_type_decade" in epic_c["drill_down"]

    def test_drill_down_file_keys_are_lists(self, epic_c):
        dd = epic_c["drill_down"]["tx_type_decade"]
        for tx_type in list(dd.keys())[:3]:
            for decade, fkeys in dd[tx_type].items():
                assert isinstance(fkeys, list), (
                    f"{tx_type}/{decade} should be a list"
                )

    def test_coverage_stats(self, epic_c):
        cov = epic_c["coverage"]
        # Threshold reflects the released-corpora top-level event scope
        # (RELEASED_CORPORA in pipeline.config; iter_top_level_events).
        assert cov["total_events"] > 4000
        assert cov["normalised_events"] > 0
        assert cov["normalised_events"] < cov["total_events"]
        assert cov["unique_verb_forms"] > 100
        assert cov["recipient_orgs"] > 10


class TestExplorationTransactions:
    """Verify exploration_transactions.html is functional (not placeholder)."""

    @pytest.fixture(scope="class")
    def html(self):
        path = DOCS_DIR / "exploration_transactions.html"
        if not path.exists():
            pytest.skip("exploration_transactions.html not found")
        return path.read_text(encoding="utf-8")

    def test_page_has_exploration_id(self, html):
        assert 'id="exploration-page"' in html

    def test_page_no_longer_embeds_epic_c_data(self, html):
        """Epic C data is now loaded from external JSON, not embedded."""
        assert 'id="explore-epic-c-data"' not in html

    def test_page_has_no_subnav(self, html):
        """Subnav removed — top nav dropdown is sufficient."""
        assert 'explore-subnav' not in html

    def test_page_has_filter_header(self, html):
        assert 'id="explore-filters"' in html

    def test_page_has_timeline_panel(self, html):
        assert 'id="explore-panel-timeline"' in html

    def test_page_has_verb_panel(self, html):
        assert 'id="explore-panel-verbs"' in html

    def test_page_has_recipients_panel(self, html):
        assert 'id="explore-panel-recipients"' in html

    def test_page_has_drilldown_overlay(self, html):
        assert 'id="explore-drilldown"' in html

    def test_page_has_inst_detail_overlay(self, html):
        assert 'id="explore-inst-detail"' in html

    def test_page_has_unified_header(self, html):
        assert 'explore-header-unified' in html

    def test_page_has_verb_search(self, html):
        assert 'id="explore-verb-search"' in html

    def test_page_is_not_placeholder(self, html):
        assert 'In Entwicklung' not in html

    def test_page_has_title(self, html):
        assert 'Transaktionen' in html
