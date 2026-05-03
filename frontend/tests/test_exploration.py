"""Tests fuer die Auswertungs-Seite (analysis/auswertungen.html) und die
zugehoerigen JSON-Aggregate epic_a/b/c."""

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


class TestAuswertungenPage:
    """Verify the consolidated Auswertungen page (4-quadrant aggregate view)."""

    @pytest.fixture(scope="class")
    def html(self):
        path = DOCS_DIR / "analysis" / "auswertungen.html"
        if not path.exists():
            pytest.skip("analysis/auswertungen.html not found")
        return path.read_text(encoding="utf-8")

    def test_uses_index_layout(self, html):
        assert 'index-layout' in html
        assert 'index-sidebar' in html
        assert 'index-main' in html

    def test_has_aggregat_grid(self, html):
        assert 'aggregat-grid' in html

    def test_has_four_sections(self, html):
        for q in ('q-roles', 'q-relations', 'q-tx', 'q-labels'):
            assert f'id="{q}"' in html, f'Missing section id={q}'

    def test_roles_section_has_donut_and_legend(self, html):
        assert 'id="roles-donut"' in html
        assert 'id="roles-legend"' in html
        # Detail-Tabelle (aufklappbar)
        assert 'id="roles-table"' in html
        # Toggle Nennungen / Personen
        assert 'data-roles-mode="mentions"' in html
        assert 'data-roles-mode="persons"' in html

    def test_relations_section_has_donut_and_legend(self, html):
        assert 'id="relations-donut"' in html
        assert 'id="relations-legend"' in html

    def test_tx_section_has_bars_container(self, html):
        assert 'id="tx-bars"' in html

    def test_labels_section_has_scrollable_table(self, html):
        assert 'aggregat-table--labels-wrap' in html
        assert 'id="labels-table"' in html

    def test_sidebar_has_required_filter_blocks(self, html):
        # Korpus-Filter wurde bewusst entfernt (epic_a/b/c sind kollektions-
        # aggregiert; Korpus-Filter waere clientseitig nicht umsetzbar).
        assert 'id="filter-corpora"' not in html
        assert 'id="filter-sex"' in html
        assert 'id="filter-reset"' in html

    def test_loads_epic_data_via_json_blocks(self, html):
        assert 'id="aggregat-data-epic-a"' in html
        assert 'id="aggregat-data-epic-b"' in html
        assert 'id="aggregat-data-epic-c"' in html

    def test_active_filter_strip_present(self, html):
        assert 'id="active-filters"' in html


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


class TestEpicARolePersons:
    """Verify epic_a.json includes the new individual-count aggregate."""

    @pytest.fixture(scope="class")
    def epic_a(self):
        path = DATA_DIR / "epic_a.json"
        if not path.exists():
            pytest.skip("epic_a.json not found")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_role_persons_by_sex(self, epic_a):
        obs = epic_a["observations"]
        assert "role_persons_by_sex" in obs
        assert "issuer" in obs["role_persons_by_sex"]
        assert "m" in obs["role_persons_by_sex"]["issuer"]

    def test_has_role_persons_by_decade(self, epic_a):
        obs = epic_a["observations"]
        assert "role_persons_by_decade" in obs
        issuer_dec = obs["role_persons_by_decade"].get("issuer", {})
        assert len(issuer_dec) > 0
        for decade, sex_keys in issuer_dec.items():
            for sex, keys in sex_keys.items():
                assert isinstance(keys, list)

    def test_individuals_smaller_than_mentions(self, epic_a):
        """Distinct persons must be <= mentions (sanity check)."""
        mentions = epic_a["observations"]["role_by_sex"]
        persons = epic_a["observations"]["role_persons_by_sex"]
        for role in mentions:
            for sex in ("m", "f"):
                if sex in mentions[role] and sex in persons.get(role, {}):
                    assert persons[role][sex] <= mentions[role][sex], \
                        f"persons > mentions for {role}/{sex}"
