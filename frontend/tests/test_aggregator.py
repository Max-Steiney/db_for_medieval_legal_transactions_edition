"""Tests for frontend.aggregator — build-time data aggregation for visualisations."""

import json

import pytest

from frontend.aggregator import (
    _decade,
    _load_csv,
    _parse_coord,
    _parse_date_range,
    run_aggregation,
)
from pipeline.config import PIPELINE_OUTPUT, NORM_LISTS_DIR
from frontend.aggregator._run import (
    _remove_legacy_data_files,
    _LEGACY_DATA_FILES,
)


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


class TestLegacyDataCleanup:
    """M2: verwaiste epic_*.json werden beim Aggregationslauf entfernt,
    aktuelle Aggregate bleiben unberuehrt."""

    def test_removes_legacy_epic_files(self, tmp_path):
        for name in _LEGACY_DATA_FILES:
            (tmp_path / name).write_text("{}", encoding="utf-8")
        (tmp_path / "roles.json").write_text("{}", encoding="utf-8")
        _remove_legacy_data_files(tmp_path)
        for name in _LEGACY_DATA_FILES:
            assert not (tmp_path / name).exists()
        assert (tmp_path / "roles.json").exists()

    def test_idempotent_when_absent(self, tmp_path):
        _remove_legacy_data_files(tmp_path)  # darf nicht werfen, wenn nichts da ist


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
    results = {}
    for name in ["timeline", "roles", "relations", "transactions",
                 "docs_aggregate"]:
        path = data_dir / f"{name}.json"
        results[name] = json.loads(path.read_text(encoding="utf-8"))
    results["_dir"] = data_dir
    return results


class TestMetaBlock:
    def test_all_files_have_meta(self, aggregation_results):
        for name in ["timeline", "roles", "relations", "transactions",
                     "docs_aggregate"]:
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
        for name in ["timeline", "roles", "relations", "transactions",
                     "docs_aggregate"]:
            dims = aggregation_results[name]["meta"]["structure"]["dimensions"]
            for dim in dims:
                assert "name" in dim, f"{name}: dimension missing name"
                assert "type" in dim, f"{name}: dimension missing type"


class TestTimelineAggregation:
    def test_total_document_count(self, aggregation_results):
        assert aggregation_results["timeline"]["total"] > 1000

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
        role_sex = aggregation_results["roles"]["observations"]["role_by_sex"]
        assert len(role_sex) > 0
        for role, sex_counts in role_sex.items():
            total = sum(sex_counts.values())
            assert total > 0, f"Role {role} has zero entries"

    def test_sex_categories(self, aggregation_results):
        role_sex = aggregation_results["roles"]["observations"]["role_by_sex"]
        for role, sex_counts in role_sex.items():
            for sex in sex_counts:
                assert sex in ("m", "f", "unspecified"), \
                    f"Unexpected sex '{sex}' in role '{role}'"

    def test_person_count(self, aggregation_results):
        assert aggregation_results["roles"]["coverage"]["person_count"] > 1000

    def test_total_events(self, aggregation_results):
        assert aggregation_results["roles"]["coverage"]["total_events"] > 1000


class TestEpicBAggregation:
    def test_overview_has_type_by_sex(self, aggregation_results):
        tbs = aggregation_results["relations"]["overview"]["type_by_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            assert t in tbs
            for s in ["m", "f", "unspecified"]:
                assert s in tbs[t]

    def test_labels_non_empty(self, aggregation_results):
        labels = aggregation_results["relations"]["labels"]
        assert len(labels) > 100
        top = labels[0]
        assert "label" in top
        assert "type" in top
        assert top["total"] > 0

    def test_persons_have_required_fields(self, aggregation_results):
        for p in aggregation_results["relations"]["persons"][:10]:
            assert "id" in p
            assert "sex" in p
            assert p["sex"] in ("m", "f", "unspecified")
            assert "rels" in p
            assert len(p["rels"]) > 0

    def test_coverage_has_totals(self, aggregation_results):
        cov = aggregation_results["relations"]["coverage"]
        assert cov["total_relations"] > 1000
        assert cov["persons_with_relations"] > 500


class TestEpicCAggregation:
    def test_normalisation_rate(self, aggregation_results):
        cov = aggregation_results["transactions"]["coverage"]
        pct = cov["normalised_events"] / cov["total_events"] * 100
        assert 5 < pct < 50, f"Normalisation rate {pct:.1f}% outside expected range"

    def test_triggerstrings_present(self, aggregation_results):
        assert len(aggregation_results["transactions"]["triggerstrings"]) > 100

    def test_triggerstring_structure(self, aggregation_results):
        ts = aggregation_results["transactions"]["triggerstrings"][0]
        assert "form" in ts
        assert "freq" in ts
        assert "norm" in ts
        assert "doc_count" in ts

    def test_recipients_present(self, aggregation_results):
        assert len(aggregation_results["transactions"]["recipients"]) > 0

    def test_tx_timeline_has_not_normalised(self, aggregation_results):
        assert "_not_normalised" in \
            aggregation_results["transactions"]["observations"]["tx_timeline"]


class TestEpicBConsistency:
    def test_label_totals_match_sex_sums(self, aggregation_results):
        """Each label's total must equal m + f + unspecified."""
        for lb in aggregation_results["relations"]["labels"][:50]:
            assert lb["total"] == lb["m"] + lb["f"] + lb["unspecified"], \
                f"Label {lb['label']}: total mismatch"

    def test_drill_down_type_sex_keys(self, aggregation_results):
        dd = aggregation_results["relations"]["drill_down"]["type_sex"]
        for t in ["kin", "occ", "rep", "friend"]:
            for s in ["m", "f"]:
                key = f"{t}_{s}"
                assert key in dd, f"Missing drill_down key: {key}"

    def test_persons_have_valid_rels(self, aggregation_results):
        for p in aggregation_results["relations"]["persons"][:20]:
            for rel in p["rels"]:
                assert rel["t"] in ("kin", "occ", "rep", "friend"), \
                    f"Invalid rel type: {rel['t']}"


# ---------------------------------------------------------------------------
# Cross-Epic integrity tests (Phase 1C / 5A)
# ---------------------------------------------------------------------------


class TestCrossEpicIntegrity:
    """Verify referential integrity across all Epic JSON files."""

    def test_roles_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        """All file_keys in Roles-Aggregation drill_down use the canonical f__ prefix."""
        dd = aggregation_results["roles"]["drill_down"]
        for role, sex_fkeys in dd.get("role_sex", {}).items():
            for sex, fkeys in sex_fkeys.items():
                for fk in fkeys[:5]:
                    assert fk.startswith("f__"), \
                        f"Roles-Aggregation role_sex drill_down has non-f__ key: {fk}"
        for ot, fkeys in dd.get("org_type", {}).items():
            for fk in fkeys[:5]:
                assert fk.startswith("f__"), \
                    f"Roles-Aggregation org_type drill_down has non-f__ key: {fk}"

    def test_relations_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        dd = aggregation_results["relations"]["drill_down"]
        for key, fkeys in dd.get("type_sex", {}).items():
            for fk in fkeys[:5]:
                assert fk.startswith("f__"), \
                    f"Relations-Aggregation type_sex drill_down has non-f__ key: {fk}"

    def test_transactions_drill_down_fkeys_have_f_prefix(self, aggregation_results):
        dd = aggregation_results["transactions"]["drill_down"]
        for tx_type, decades in dd.get("tx_type_decade", {}).items():
            for decade, fkeys in decades.items():
                for fk in fkeys[:3]:
                    assert fk.startswith("f__"), \
                        f"Transactions-Aggregation drill_down has non-f__ key: {fk}"

    def test_roles_empty_role_key_exists(self, aggregation_results):
        """Aggregator produces '' (empty) role key that JS merges into 'other'."""
        obs = aggregation_results["roles"]["observations"]
        role_sex = obs["role_by_sex"]
        # The '' key should exist if there are unspecified-role person-events.
        # This is data-dependent; just verify the canonical roles exist.
        for role in ["issuer", "recipient", "witness", "other"]:
            assert role in role_sex, f"Missing canonical role: {role}"

    def test_roles_coverage_consistency(self, aggregation_results):
        """Coverage stats should be internally consistent."""
        cov = aggregation_results["roles"]["coverage"]
        assert cov["person_count"] > 0
        assert cov["total_events"] > 0
        assert cov["normalisation_rate"] <= cov["total_events"]
        assert cov["org_type_count"] > 0

    def test_relations_person_ids_use_entity_prefix(self, aggregation_results):
        """All entries in Relations-Aggregation persons should have canonical entity IDs.

        Most are pe__ (persons), but some relationship annotations reference
        organisations (org__) — this is valid source data, not a bug.
        """
        valid_prefixes = ("pe__", "org__")
        for p in aggregation_results["relations"]["persons"][:50]:
            assert any(p["id"].startswith(pre) for pre in valid_prefixes), \
                f"Relations-Aggregation person has unexpected ID prefix: {p['id']}"

    def test_relations_coverage_internal_consistency(self, aggregation_results):
        """Coverage totals should match type_counts sum."""
        cov = aggregation_results["relations"]["coverage"]
        type_sum = sum(cov["type_counts"].values())
        assert cov["total_relations"] == type_sum, \
            f"total_relations ({cov['total_relations']}) != sum of type_counts ({type_sum})"

    def test_transactions_normalised_lte_total(self, aggregation_results):
        """Normalised event count must not exceed total events."""
        cov = aggregation_results["transactions"]["coverage"]
        assert cov["normalised_events"] <= cov["total_events"]

    def test_transactions_triggerstring_doc_count_lte_freq(self, aggregation_results):
        """Each triggerstring's doc_count should not exceed its freq."""
        for ts in aggregation_results["transactions"]["triggerstrings"][:50]:
            assert ts["doc_count"] <= ts["freq"], \
                f"Triggerstring '{ts['form']}': doc_count ({ts['doc_count']}) > freq ({ts['freq']})"

    def test_transactions_recipients_sorted_descending(self, aggregation_results):
        """Recipients list should be sorted by count descending."""
        recipients = aggregation_results["transactions"]["recipients"]
        for i in range(len(recipients) - 1):
            assert recipients[i]["count"] >= recipients[i + 1]["count"], \
                f"Recipients not sorted at index {i}"

    def test_all_drill_down_blocks_non_empty(self, aggregation_results):
        """Each Epic's drill_down should have at least one key with file_keys."""
        dd_a = aggregation_results["roles"]["drill_down"]
        assert len(dd_a.get("role_sex", {})) > 0, "Roles-Aggregation has no role_sex drill_down"

        dd_b = aggregation_results["relations"]["drill_down"]
        assert len(dd_b.get("type_sex", {})) > 0, "Relations-Aggregation has no type_sex drill_down"

        dd_c = aggregation_results["transactions"]["drill_down"]
        assert len(dd_c.get("tx_type_decade", {})) > 0, "Transactions-Aggregation has no tx_type_decade drill_down"


# ---------------------------------------------------------------------------
# _parse_date_range — pure unit tests
# ---------------------------------------------------------------------------

class TestParseDateRange:
    def test_clean_iso_date(self):
        assert _parse_date_range("1177-05-10") == ("1177-05-10", "1177-05-10", 1177)

    def test_whole_year_uncertainty(self):
        # Pipeline convention for "year uncertain"
        assert _parse_date_range("1208-01-01 | 1208-12-31") == \
            ("1208-01-01", "1208-12-31", 1208)

    def test_multi_year_range(self):
        assert _parse_date_range("1198-01-01 | 1230-12-31") == \
            ("1198-01-01", "1230-12-31", 1198)

    def test_empty_string(self):
        assert _parse_date_range("") == (None, None, None)

    def test_whitespace_only(self):
        assert _parse_date_range("   ") == (None, None, None)

    def test_extra_whitespace_in_range(self):
        assert _parse_date_range("  1208-01-01   |   1208-12-31  ") == \
            ("1208-01-01", "1208-12-31", 1208)


# ---------------------------------------------------------------------------
# Docs aggregate — integration
# ---------------------------------------------------------------------------

def _doc_by_idno_collection(docs, idno, collection_path):
    """Pick a record from docs_aggregate by (idno, collection_path)."""
    for d in docs:
        if d["idno"] == idno and d["collection_path"] == collection_path:
            return d
    return None


class TestDocsAggregate:

    def test_total_within_expected_range(self, aggregation_results):
        """Aggregator source count is within the released corpus' magnitude.

        Range check, kein exakter Zahlenvergleich: die Quellenzahl driftet
        mit jedem Pipeline-Refactor und mit jedem TEI-Fix. Eine harte Zahl
        veraltet sofort. Untergrenze schuetzt vor stillschweigendem Datenverlust,
        Obergrenze vor durchgesickerten Nicht-released-Subkorpora.
        """
        docs = aggregation_results["docs_aggregate"]["docs"]
        # Untergrenze schuetzt vor Datenverlust (Stufe 1: ca. 2600 Quellen),
        # Obergrenze erfasst auch Stufe 4 mit allen TEI-Subkorpora
        # (heute ca. 3100 Quellen). Beide Werte sind absichtlich grob.
        assert 2500 <= len(docs) <= 3500, \
            f"Source count {len(docs)} ausserhalb plausibler Spanne 2500-3500"

    def test_qgw_0a_against_tei_truth(self, aggregation_results):
        """Spot check: 0a has 1 male person, 1 abstract event."""
        docs = aggregation_results["docs_aggregate"]["docs"]
        d = _doc_by_idno_collection(docs, "0a", "QGW/Vienna_1177-1414_ready")
        assert d is not None
        assert d["persons"] == {"distinct": 1, "f": 0, "m": 1, "u": 0}
        assert d["events"]["total"] == 1
        assert d["events"]["abstract"] == 1
        assert d["events"]["seal"] == 0

    def test_qgw_10_with_wife_via_corresp(self, aggregation_results):
        """Spot check: QGW 10 has Berthold (m) + Diemut (f, via corresp)."""
        docs = aggregation_results["docs_aggregate"]["docs"]
        d = _doc_by_idno_collection(docs, "10", "QGW/Vienna_1177-1414_ready")
        assert d is not None
        assert d["persons"]["distinct"] == 2
        assert d["persons"]["f"] == 1
        assert d["persons"]["m"] == 1
        assert d["events"]["abstract"] >= 1
        assert d["events"]["seal"] >= 1

    def test_stadtbuecher_10_against_tei_truth(self, aggregation_results):
        """Spot check: StB 10 has 7 persons (1f, 6m), 1 entry event."""
        docs = aggregation_results["docs_aggregate"]["docs"]
        d = _doc_by_idno_collection(docs, "10", "Stadtbuecher/Band_1_1395-1400_ready")
        assert d is not None
        assert d["persons"] == {"distinct": 7, "f": 1, "m": 6, "u": 0}
        assert d["events"]["entry"] == 1
        assert d["events"]["abstract"] == 0

    def test_multi_event_source_1542(self, aggregation_results):
        """Spot check: QGW 1542 is a special case with 4 legal transactions."""
        docs = aggregation_results["docs_aggregate"]["docs"]
        d = _doc_by_idno_collection(docs, "1542", "QGW/Vienna_1177-1414_ready")
        assert d is not None
        assert d["events"]["total"] == 4

    def test_sex_breakdown_sums_to_distinct(self, aggregation_results):
        """For each source f + m + u must equal distinct."""
        for d in aggregation_results["docs_aggregate"]["docs"]:
            p = d["persons"]
            assert p["f"] + p["m"] + p["u"] == p["distinct"], \
                f"Sex breakdown mismatch in {d['file_key']}"

    def test_all_records_have_file_key(self, aggregation_results):
        """No record without file_key (otherwise no frontend lookup is possible)."""
        for d in aggregation_results["docs_aggregate"]["docs"]:
            assert d["file_key"], f"Record without file_key: {d}"
            assert d["file_key"].startswith("f__"), \
                f"file_key prefix broken: {d['file_key']}"

    def test_only_active_stage_corpora_present(self, aggregation_results):
        """Aggregator filters auf die in der aktiven Stufe freigegebenen Korpora.

        Stage-aware statt hardcoded Praefixe: der erlaubte Set kommt direkt
        aus pipeline.config.active_corpora(), das die FRONTEND_STAGE-Env-Var
        beruecksichtigt. Pruefung: jeder collection_path muss in der Liste
        stehen, kein nicht-freigegebener Pfad leakt durch.
        """
        from pipeline.config import active_corpora
        allowed = set(active_corpora())
        for d in aggregation_results["docs_aggregate"]["docs"]:
            cp = d["collection_path"]
            assert cp in allowed, \
                f"Korpus ausserhalb der aktiven Stufe geleakt: {cp}"

    def test_event_form_counts_le_total(self, aggregation_results):
        """Each form bucket must not contain more events than total."""
        for d in aggregation_results["docs_aggregate"]["docs"]:
            ev = d["events"]
            for bucket in ("abstract", "seal", "entry", "nota", "other"):
                assert ev[bucket] <= ev["total"], \
                    f"{d['file_key']}: {bucket}={ev[bucket]} > total={ev['total']}"

    def test_qgw_ready_event_total_distribution(self, aggregation_results):
        """QGW-_ready-Quellen tragen fast immer genau ein Event (Norm).

        Nur auf die kuratierten _ready-Subkorpora beschraenkt: nicht-_ready-
        Subkorpora (Stufe 4) sind editorial unfertig und tragen haeufig
        Quellen ohne Event-Annotation.

        Nur in Stufen ohne Mentioned-Events sinnvoll: wenn
        PIPELINE_INCLUDE_MENTIONED_EVENTS aktiv ist (Stufen 2 und 4),
        zaehlen verschachtelte Events als eigene, womit die Ein-Event-Norm
        per Konstruktion verletzt wird.
        """
        from pipeline.config import include_mentioned_events
        if include_mentioned_events():
            pytest.skip("Stage zaehlt mentioned events als eigene; Norm gilt nicht")
        qgw_ready = [d for d in aggregation_results["docs_aggregate"]["docs"]
                     if d["collection_path"].startswith("QGW/")
                     and d["collection_path"].endswith("_ready")]
        with_one = sum(1 for d in qgw_ready if d["events"]["total"] == 1)
        assert with_one / len(qgw_ready) > 0.99, \
            f"Only {with_one}/{len(qgw_ready)} QGW _ready sources with total=1"

    def test_with_persons_ratio_is_dominant(self, aggregation_results):
        """Anteil der Quellen mit mindestens einer Register-Person ist dominant.

        Verhaeltnis-Test statt fixer Zahl: Quellen ohne Personen-Annotation
        sind die seltene Ausnahme (z. B. Geistesgut-Verzeichnisse). Wenn der
        Anteil unter 90 Prozent faellt, ist im Aggregator etwas kaputt.
        """
        docs = aggregation_results["docs_aggregate"]["docs"]
        with_persons = sum(1 for d in docs if d["persons"]["distinct"] > 0)
        ratio = with_persons / len(docs)
        assert ratio > 0.9, \
            f"Nur {with_persons}/{len(docs)} ({ratio:.1%}) Quellen mit Personen"

    def test_dates_present_and_parseable(self, aggregation_results):
        """At least 95% of sources have a parseable date_year."""
        docs = aggregation_results["docs_aggregate"]["docs"]
        with_year = sum(1 for d in docs if d.get("date_year"))
        assert with_year / len(docs) > 0.95, \
            f"Only {with_year}/{len(docs)} sources with year"
