"""Tests for the analysis page (analysis/auswertungen.html) and the
associated JSON aggregates roles/b/c."""

import json
import pytest

from frontend.config import DOCS_DIR, DATA_DIR


class TestEpicADrillDown:
    """Verify roles.json includes drill_down data after aggregation."""

    @pytest.fixture(scope="class")
    def roles(self):
        path = DATA_DIR / "roles.json"
        if not path.exists():
            pytest.skip("roles.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_drill_down_key_present(self, roles):
        assert "drill_down" in roles

    def test_drill_down_has_role_sex(self, roles):
        dd = roles["drill_down"]
        assert "role_sex" in dd

    def test_drill_down_issuer_has_m_and_f(self, roles):
        dd = roles["drill_down"]["role_sex"]
        assert "issuer" in dd
        assert "m" in dd["issuer"]
        assert "f" in dd["issuer"]

    def test_drill_down_file_keys_are_lists(self, roles):
        dd = roles["drill_down"]["role_sex"]
        for role, sex_map in dd.items():
            for sex, fkeys in sex_map.items():
                assert isinstance(fkeys, list), f"{role}/{sex} should be a list"

    def test_drill_down_file_keys_start_with_f(self, roles):
        """All file_keys should start with 'f__'."""
        dd = roles["drill_down"]["role_sex"]
        for role, sex_map in dd.items():
            for sex, fkeys in sex_map.items():
                for fk in fkeys[:5]:
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
        # Detail table (expandable).
        assert 'id="roles-table"' in html
        # Toggle mentions / persons.
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
        # Corpus filter was intentionally removed (roles/b/c are collection-
        # aggregated; a corpus filter could not be implemented client-side).
        assert 'id="filter-corpora"' not in html
        assert 'id="filter-sex"' in html
        assert 'id="filter-reset"' in html

    def test_loads_aggregation_data_via_json_blocks(self, html):
        assert 'id="aggregat-data-roles"' in html
        assert 'id="aggregat-data-relations"' in html
        assert 'id="aggregat-data-transactions"' in html

    def test_active_filter_strip_present(self, html):
        assert 'id="active-filters"' in html

    def test_time_aware_hints_present_in_relations_and_labels(self, html):
        """Beziehungen und Bezeichnungen kennen keine Jahrzehnt-Buckets.

        Der Hint sitzt als hidden-Element im Markup; JS toggelt ihn, wenn
        ein Zeitraum-Filter aktiv wird. Tests verifizieren das Markup, das
        Toggle-Verhalten lebt in der JS-Schicht (analysis-aggregat.js).
        """
        assert html.count('aggregat-quadrant-time-hint') == 2, \
            'Zeitfilter-Hint soll genau in den 2 nicht zeit-bucketed Quadranten stehen'
        # Beide Hinweise stehen als hidden im Markup, JS toggelt visibility.
        assert 'class="aggregat-quadrant-time-hint" hidden' in html


class TestEpicBData:
    """Verify relations.json has correct structure for Relationship Explorer."""

    @pytest.fixture(scope="class")
    def relations(self):
        path = DATA_DIR / "relations.json"
        if not path.exists():
            pytest.skip("relations.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_overview(self, relations):
        assert "overview" in relations
        tbs = relations["overview"]["type_by_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            assert t in tbs
            for s in ["m", "f", "unspecified"]:
                assert s in tbs[t]

    def test_has_labels(self, relations):
        labels = relations["labels"]
        assert len(labels) > 100
        top = labels[0]
        assert "label" in top
        assert "type" in top
        assert "m" in top
        assert "f" in top
        assert "total" in top

    def test_has_persons(self, relations):
        persons = relations["persons"]
        assert len(persons) > 3000
        p = persons[0]
        assert "id" in p
        assert "name" in p
        assert "sex" in p
        assert "rels" in p

    def test_coverage(self, relations):
        cov = relations["coverage"]
        assert cov["total_relations"] > 10000
        assert cov["persons_with_relations"] > 3000

    def test_json_size(self):
        path = DATA_DIR / "relations.json"
        if not path.exists():
            pytest.skip("relations.json not found")
        size_mb = path.stat().st_size / (1024 * 1024)
        assert size_mb < 5, f"relations.json is {size_mb:.1f} MB, expected < 5 MB"

    def test_has_drill_down(self, relations):
        dd = relations["drill_down"]
        assert "type_sex" in dd
        assert "label_sex" in dd


class TestEpicCData:
    """Verify transactions.json has correct structure for Transaction Explorer."""

    @pytest.fixture(scope="class")
    def transactions(self):
        path = DATA_DIR / "transactions.json"
        if not path.exists():
            pytest.skip("transactions.json not found (run full build first)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_observations(self, transactions):
        assert "observations" in transactions

    def test_has_tx_timeline(self, transactions):
        assert "tx_timeline" in transactions["observations"]

    def test_tx_timeline_has_not_normalised(self, transactions):
        tl = transactions["observations"]["tx_timeline"]
        assert "_not_normalised" in tl

    def test_tx_timeline_not_normalised_has_significant_count(self, transactions):
        """The 'not normalised' category should have substantial counts."""
        tl = transactions["observations"]["tx_timeline"]
        not_norm_total = sum(tl["_not_normalised"].values())
        assert not_norm_total > 500, (
            f"_not_normalised ({not_norm_total}) should be > 500"
        )

    def test_has_recipient_type_totals(self, transactions):
        assert "recipient_type_totals" in transactions["observations"]

    def test_recipient_type_totals_not_empty(self, transactions):
        assert len(transactions["observations"]["recipient_type_totals"]) > 5

    def test_has_triggerstrings(self, transactions):
        assert "triggerstrings" in transactions
        assert len(transactions["triggerstrings"]) > 100

    def test_triggerstrings_have_required_fields(self, transactions):
        for ts in transactions["triggerstrings"][:10]:
            assert "form" in ts
            assert "freq" in ts
            assert "norm" in ts or ts["norm"] == ""
            assert "doc_count" in ts
            assert "file_keys" in ts

    def test_triggerstrings_file_keys_match_doc_count(self, transactions):
        """file_keys list length should equal doc_count."""
        for ts in transactions["triggerstrings"][:20]:
            assert len(ts["file_keys"]) == ts["doc_count"], (
                f"'{ts['form']}': file_keys={len(ts['file_keys'])} "
                f"!= doc_count={ts['doc_count']}"
            )

    def test_triggerstrings_sorted_by_freq_desc(self, transactions):
        freqs = [ts["freq"] for ts in transactions["triggerstrings"]]
        assert freqs == sorted(freqs, reverse=True)

    def test_has_recipients(self, transactions):
        assert "recipients" in transactions
        assert len(transactions["recipients"]) > 10

    def test_recipients_have_required_fields(self, transactions):
        for r in transactions["recipients"][:10]:
            assert "id" in r
            assert "name" in r
            assert "type" in r
            assert "count" in r

    def test_recipients_sorted_by_count_desc(self, transactions):
        counts = [r["count"] for r in transactions["recipients"]]
        assert counts == sorted(counts, reverse=True)

    def test_has_org_supporters(self, transactions):
        assert "org_supporters" in transactions
        assert len(transactions["org_supporters"]) > 10

    def test_org_supporters_have_file_keys(self, transactions):
        sample_key = list(transactions["org_supporters"].keys())[0]
        supporters = transactions["org_supporters"][sample_key]
        assert len(supporters) > 0
        assert "file_key" in supporters[0]
        assert "person_key" in supporters[0]
        assert "role" in supporters[0]

    def test_has_drill_down(self, transactions):
        assert "drill_down" in transactions
        assert "tx_type_decade" in transactions["drill_down"]

    def test_drill_down_file_keys_are_lists(self, transactions):
        dd = transactions["drill_down"]["tx_type_decade"]
        for tx_type in list(dd.keys())[:3]:
            for decade, fkeys in dd[tx_type].items():
                assert isinstance(fkeys, list), (
                    f"{tx_type}/{decade} should be a list"
                )

    def test_coverage_stats(self, transactions):
        cov = transactions["coverage"]
        # Threshold reflects the released-corpora top-level event scope
        # (RELEASED_CORPORA in pipeline.config; iter_top_level_events).
        assert cov["total_events"] > 4000
        assert cov["normalised_events"] > 0
        assert cov["normalised_events"] < cov["total_events"]
        assert cov["unique_verb_forms"] > 100
        assert cov["recipient_orgs"] > 10


class TestEpicARolePersons:
    """Verify roles.json includes the new individual-count aggregate."""

    @pytest.fixture(scope="class")
    def roles(self):
        path = DATA_DIR / "roles.json"
        if not path.exists():
            pytest.skip("roles.json not found")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_has_role_persons_by_sex(self, roles):
        obs = roles["observations"]
        assert "role_persons_by_sex" in obs
        assert "issuer" in obs["role_persons_by_sex"]
        assert "m" in obs["role_persons_by_sex"]["issuer"]

    def test_has_role_persons_by_decade(self, roles):
        obs = roles["observations"]
        assert "role_persons_by_decade" in obs
        issuer_dec = obs["role_persons_by_decade"].get("issuer", {})
        assert len(issuer_dec) > 0
        for decade, sex_keys in issuer_dec.items():
            for sex, keys in sex_keys.items():
                assert isinstance(keys, list)

    def test_individuals_smaller_than_mentions(self, roles):
        """Distinct persons must be <= mentions (sanity check)."""
        mentions = roles["observations"]["role_by_sex"]
        persons = roles["observations"]["role_persons_by_sex"]
        for role in mentions:
            for sex in ("m", "f"):
                if sex in mentions[role] and sex in persons.get(role, {}):
                    assert persons[role][sex] <= mentions[role][sex], \
                        f"persons > mentions for {role}/{sex}"
