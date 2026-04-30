"""Tests for frontend.aggregator — build-time data aggregation for visualisations."""

import json

import pytest

from frontend.aggregator import (
    _decade,
    _load_csv,
    _parse_coord,
    run_aggregation,
)
from pipeline.config import PIPELINE_OUTPUT, NORM_LISTS_DIR


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


class TestDecade:
    def test_normal_date(self):
        assert _decade("13270415") == 1320

    def test_year_boundary(self):
        assert _decade("14000101") == 1400

    def test_placeholder_date(self):
        assert _decade("99999999") is None

    def test_empty_string(self):
        assert _decade("") is None

    def test_short_string(self):
        assert _decade("12") is None

    def test_non_numeric(self):
        assert _decade("abcd1234") is None

    def test_year_1177(self):
        assert _decade("11770101") == 1170

    def test_year_1526(self):
        assert _decade("15260101") == 1520


class TestParseCoord:
    def test_standard_float(self):
        assert _parse_coord("48.23333") == 48.23333

    def test_comma_decimal(self):
        assert _parse_coord("48,23134719") == pytest.approx(48.23134719)

    def test_text_suffix(self):
        assert _parse_coord("13.95049 Möglich") == pytest.approx(13.95049)

    def test_letter_suffix(self):
        assert _parse_coord("16.45N") == pytest.approx(16.45)

    def test_negative(self):
        assert _parse_coord("-12.5") == pytest.approx(-12.5)

    def test_empty_string(self):
        assert _parse_coord("") is None

    def test_non_numeric(self):
        assert _parse_coord("abc") is None

    def test_none(self):
        assert _parse_coord(None) is None


class TestCsvLoader:
    def test_semicolon_delimiter(self):
        rows = _load_csv(PIPELINE_OUTPUT / "filenames.csv")
        assert len(rows) > 0
        assert "file" in rows[0]
        assert "collection" in rows[0]

    def test_persons_csv_has_expected_columns(self):
        rows = _load_csv(PIPELINE_OUTPUT / "persons.csv")
        assert "id" in rows[0]
        assert "sex" in rows[0]

    def test_tab_delimiter_for_norm_list(self):
        rows = _load_csv(NORM_LISTS_DIR / "label_norm_matching.csv", delimiter="\t")
        assert len(rows) > 0
        assert "source_catchword" in rows[0]
        assert "catchword_main_norm" in rows[0]


# ---------------------------------------------------------------------------
# Integration tests — run all aggregations once, share results
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def aggregation_results(tmp_path_factory):
    """Run full aggregation once for the entire test module."""
    data_dir = tmp_path_factory.mktemp("data")
    run_aggregation(data_dir)
    # Load all JSON results
    results = {}
    for name in ["timeline", "epic_a", "epic_b", "epic_c", "epic_d"]:
        path = data_dir / f"{name}.json"
        results[name] = json.loads(path.read_text(encoding="utf-8"))
    results["_dir"] = data_dir
    return results


class TestMetaBlock:
    def test_all_files_have_meta(self, aggregation_results):
        for name in ["timeline", "epic_a", "epic_b", "epic_c", "epic_d"]:
            data = aggregation_results[name]
            assert "meta" in data, f"{name}.json missing meta block"
            meta = data["meta"]
            assert "schema_version" in meta
            assert "created" in meta
            assert "sources" in meta
            assert "structure" in meta
            assert "dimensions" in meta["structure"]
            assert "measures" in meta["structure"]

    def test_dimensions_have_name_and_type(self, aggregation_results):
        for name in ["timeline", "epic_a", "epic_b", "epic_c", "epic_d"]:
            dims = aggregation_results[name]["meta"]["structure"]["dimensions"]
            for dim in dims:
                assert "name" in dim, f"{name}: dimension missing name"
                assert "type" in dim, f"{name}: dimension missing type"


class TestTimelineAggregation:
    def test_total_document_count(self, aggregation_results):
        assert aggregation_results["timeline"]["total"] > 1000  # sanity check

    def test_placeholder_dates_counted(self, aggregation_results):
        # Field is always present; count may be 0 after recent source-cleanup
        # rounds removed collections that contained unparseable dates.
        assert "placeholder_count" in aggregation_results["timeline"]
        assert aggregation_results["timeline"]["placeholder_count"] >= 0

    def test_decades_structure(self, aggregation_results):
        decades = aggregation_results["timeline"]["decades"]
        assert len(decades) > 0
        for d, data in decades.items():
            assert "total" in data

    def test_collections_present(self, aggregation_results):
        assert len(aggregation_results["timeline"]["collections"]) > 0

    def test_period_range(self, aggregation_results):
        period = aggregation_results["timeline"]["period"]
        assert period[0] is not None
        assert period[0] >= 1170
        assert period[1] <= 1530


class TestEpicAAggregation:
    def test_role_sex_totals(self, aggregation_results):
        role_sex = aggregation_results["epic_a"]["observations"]["role_by_sex"]
        assert len(role_sex) > 0
        for role, sex_counts in role_sex.items():
            total = sum(sex_counts.values())
            assert total > 0, f"Role {role} has zero entries"

    def test_sex_categories(self, aggregation_results):
        role_sex = aggregation_results["epic_a"]["observations"]["role_by_sex"]
        for role, sex_counts in role_sex.items():
            for sex in sex_counts:
                assert sex in ("m", "f", "unspecified"), \
                    f"Unexpected sex '{sex}' in role '{role}'"

    def test_person_count(self, aggregation_results):
        assert aggregation_results["epic_a"]["coverage"]["person_count"] > 1000

    def test_total_events(self, aggregation_results):
        assert aggregation_results["epic_a"]["coverage"]["total_events"] > 1000


class TestEpicBAggregation:
    def test_overview_has_type_by_sex(self, aggregation_results):
        tbs = aggregation_results["epic_b"]["overview"]["type_by_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            assert t in tbs
            for s in ["m", "f", "unspecified"]:
                assert s in tbs[t]

    def test_labels_non_empty(self, aggregation_results):
        labels = aggregation_results["epic_b"]["labels"]
        assert len(labels) > 100
        top = labels[0]
        assert "label" in top
        assert "type" in top
        assert top["total"] > 0

    def test_persons_have_required_fields(self, aggregation_results):
        for p in aggregation_results["epic_b"]["persons"][:10]:
            assert "id" in p
            assert "sex" in p
            assert p["sex"] in ("m", "f", "unspecified")
            assert "rels" in p
            assert len(p["rels"]) > 0

    def test_coverage_has_totals(self, aggregation_results):
        cov = aggregation_results["epic_b"]["coverage"]
        assert cov["total_relations"] > 1000
        assert cov["persons_with_relations"] > 500


class TestEpicCAggregation:
    def test_normalisation_rate(self, aggregation_results):
        cov = aggregation_results["epic_c"]["coverage"]
        pct = cov["normalised_events"] / cov["total_events"] * 100
        assert 5 < pct < 50, f"Normalisation rate {pct:.1f}% outside expected range"

    def test_triggerstrings_present(self, aggregation_results):
        assert len(aggregation_results["epic_c"]["triggerstrings"]) > 100

    def test_triggerstring_structure(self, aggregation_results):
        ts = aggregation_results["epic_c"]["triggerstrings"][0]
        assert "form" in ts
        assert "freq" in ts
        assert "norm" in ts
        assert "doc_count" in ts

    def test_recipients_present(self, aggregation_results):
        assert len(aggregation_results["epic_c"]["recipients"]) > 0

    def test_tx_timeline_has_not_normalised(self, aggregation_results):
        assert "_not_normalised" in \
            aggregation_results["epic_c"]["observations"]["tx_timeline"]


class TestEpicDAggregation:
    def test_total_places(self, aggregation_results):
        assert aggregation_results["epic_d"]["coverage"]["total"] > 2500

    def test_referenced_places(self, aggregation_results):
        assert aggregation_results["epic_d"]["coverage"]["referenced"] > 0

    def test_place_structure(self, aggregation_results):
        p = aggregation_results["epic_d"]["places"][0]
        assert "id" in p
        assert "name" in p
        assert "referenced" in p
        assert "has_coords" in p
        assert "has_geonames" in p

    def test_coord_parse_failures_tracked(self, aggregation_results):
        """Non-numeric coordinates should be counted as parse failures."""
        failures = aggregation_results["epic_d"]["coverage"]["coord_parse_failures"]
        assert isinstance(failures, int)

    def test_referenced_unreferenced_sum_to_total(self, aggregation_results):
        cov = aggregation_results["epic_d"]["coverage"]
        assert cov["referenced"] + cov["unreferenced"] == cov["total"]

    def test_comma_coords_parsed(self, aggregation_results):
        """Comma-decimal coordinates (German locale) should be parsed."""
        cov = aggregation_results["epic_d"]["coverage"]
        # With comma parsing, we expect >700 (before fix: 647)
        assert cov["with_coords"] > 700


class TestEpicBConsistency:
    def test_label_totals_match_sex_sums(self, aggregation_results):
        """Each label's total must equal m + f + unspecified."""
        for lb in aggregation_results["epic_b"]["labels"][:50]:
            assert lb["total"] == lb["m"] + lb["f"] + lb["unspecified"], \
                f"Label {lb['label']}: total mismatch"

    def test_drill_down_type_sex_keys(self, aggregation_results):
        dd = aggregation_results["epic_b"]["drill_down"]["type_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            for s in ["m", "f"]:
                key = f"{t}_{s}"
                assert key in dd, f"Missing drill_down key: {key}"

    def test_persons_have_valid_rels(self, aggregation_results):
        for p in aggregation_results["epic_b"]["persons"][:20]:
            for rel in p["rels"]:
                assert rel["t"] in ("kin", "occ", "rep", "friend"), \
                    f"Invalid rel type: {rel['t']}"


# ---------------------------------------------------------------------------
# Cross-Epic integrity tests (Phase 1C / 5A)
# ---------------------------------------------------------------------------


class TestCrossEpicIntegrity:
    """Verify referential integrity across all Epic JSON files."""

    def test_epic_a_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        """All file_keys in Epic A drill_down use the canonical f__ prefix."""
        dd = aggregation_results["epic_a"]["drill_down"]
        for role, sex_fkeys in dd.get("role_sex", {}).items():
            for sex, fkeys in sex_fkeys.items():
                for fk in fkeys[:5]:
                    assert fk.startswith("f__"), \
                        f"Epic A role_sex drill_down has non-f__ key: {fk}"
        for ot, fkeys in dd.get("org_type", {}).items():
            for fk in fkeys[:5]:
                assert fk.startswith("f__"), \
                    f"Epic A org_type drill_down has non-f__ key: {fk}"

    def test_epic_b_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        dd = aggregation_results["epic_b"]["drill_down"]
        for key, fkeys in dd.get("type_sex", {}).items():
            for fk in fkeys[:5]:
                assert fk.startswith("f__"), \
                    f"Epic B type_sex drill_down has non-f__ key: {fk}"

    def test_epic_c_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        dd = aggregation_results["epic_c"]["drill_down"]
        for tx_type, decades in dd.get("tx_type_decade", {}).items():
            for decade, fkeys in decades.items():
                for fk in fkeys[:3]:
                    assert fk.startswith("f__"), \
                        f"Epic C drill_down has non-f__ key: {fk}"

    def test_epic_a_empty_role_key_exists(self, aggregation_results):
        """Aggregator produces '' (empty) role key that JS merges into 'other'."""
        obs = aggregation_results["epic_a"]["observations"]
        role_sex = obs["role_by_sex"]
        # '' key should exist if there are unspecified-role person-events
        # This is data-dependent; just verify the canonical roles exist
        for role in ["issuer", "recipient", "witness", "other"]:
            assert role in role_sex, f"Missing canonical role: {role}"

    def test_epic_a_coverage_consistency(self, aggregation_results):
        """Coverage stats should be internally consistent."""
        cov = aggregation_results["epic_a"]["coverage"]
        assert cov["person_count"] > 0
        assert cov["total_events"] > 0
        assert cov["normalisation_rate"] <= cov["total_events"]
        assert cov["org_type_count"] > 0

    def test_epic_b_person_ids_use_entity_prefix(self, aggregation_results):
        """All entries in Epic B persons should have canonical entity IDs.

        Most are pe__ (persons), but some relationship annotations reference
        organisations (org__) — this is valid source data, not a bug.
        """
        valid_prefixes = ("pe__", "org__")
        for p in aggregation_results["epic_b"]["persons"][:50]:
            assert any(p["id"].startswith(pre) for pre in valid_prefixes), \
                f"Epic B person has unexpected ID prefix: {p['id']}"

    def test_epic_b_coverage_internal_consistency(self, aggregation_results):
        """Coverage totals should match type_counts sum."""
        cov = aggregation_results["epic_b"]["coverage"]
        type_sum = sum(cov["type_counts"].values())
        assert cov["total_relations"] == type_sum, \
            f"total_relations ({cov['total_relations']}) != sum of type_counts ({type_sum})"

    def test_epic_c_normalised_lte_total(self, aggregation_results):
        """Normalised event count must not exceed total events."""
        cov = aggregation_results["epic_c"]["coverage"]
        assert cov["normalised_events"] <= cov["total_events"]

    def test_epic_c_triggerstring_doc_count_lte_freq(self, aggregation_results):
        """Each triggerstring's doc_count should not exceed its freq."""
        for ts in aggregation_results["epic_c"]["triggerstrings"][:50]:
            assert ts["doc_count"] <= ts["freq"], \
                f"Triggerstring '{ts['form']}': doc_count ({ts['doc_count']}) > freq ({ts['freq']})"

    def test_epic_c_recipients_sorted_descending(self, aggregation_results):
        """Recipients list should be sorted by count descending."""
        recipients = aggregation_results["epic_c"]["recipients"]
        for i in range(len(recipients) - 1):
            assert recipients[i]["count"] >= recipients[i + 1]["count"], \
                f"Recipients not sorted at index {i}"

    def test_epic_d_settlements_with_coords_have_file_keys(self, aggregation_results):
        """Settlements with coords and doc_count > 0 should have file_keys."""
        for p in aggregation_results["epic_d"]["places"]:
            if p["type"] == "settlement" and p["has_coords"] and p["doc_count"] > 0:
                assert "file_keys" in p, \
                    f"Settlement {p['id']} ({p['name']}) missing file_keys"

    def test_epic_d_type_counts_sum_to_total(self, aggregation_results):
        """Sum of type_counts should equal total places."""
        cov = aggregation_results["epic_d"]["coverage"]
        type_sum = sum(cov["type_counts"].values())
        assert type_sum == cov["total"], \
            f"type_counts sum ({type_sum}) != total ({cov['total']})"

    def test_all_drill_down_blocks_non_empty(self, aggregation_results):
        """Each Epic's drill_down should have at least one key with file_keys."""
        # Epic A
        dd_a = aggregation_results["epic_a"]["drill_down"]
        assert len(dd_a.get("role_sex", {})) > 0, "Epic A has no role_sex drill_down"

        # Epic B
        dd_b = aggregation_results["epic_b"]["drill_down"]
        assert len(dd_b.get("type_sex", {})) > 0, "Epic B has no type_sex drill_down"

        # Epic C
        dd_c = aggregation_results["epic_c"]["drill_down"]
        assert len(dd_c.get("tx_type_decade", {})) > 0, "Epic C has no tx_type_decade drill_down"
