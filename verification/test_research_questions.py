"""Tests fuer verification/research_questions.py.

Sichert zwei Eigenschaften der Frontend-vs-Sollwert-Bruecke:

1. Die Klassifikationsfunktion _frontend_vs_sollwert_status liefert
   die erwarteten vier Status (no_frontend, match, known_gap, mismatch).

2. compute_occ_st_stephan() laeuft durch und produziert nie 'mismatch'.
   'known_gap' (Frontend kleiner wegen Korpus-Filter) ist erwartbar,
   'mismatch' (Frontend groesser als Sollwert) waere echter Drift im
   Aggregator und muss als Bug auffallen.
"""

from __future__ import annotations

import pytest

from verification.research_questions import (
    _frontend_vs_sollwert_status,
    compute_occ_st_stephan,
)


class TestFrontendVsSollwertStatus:
    def test_none_returns_no_frontend(self):
        assert _frontend_vs_sollwert_status(None, 5) == "no_frontend"

    def test_equal_returns_match(self):
        assert _frontend_vs_sollwert_status(5, 5) == "match"

    def test_smaller_returns_known_gap(self):
        assert _frontend_vs_sollwert_status(3, 5) == "known_gap"

    def test_larger_returns_mismatch(self):
        assert _frontend_vs_sollwert_status(7, 5) == "mismatch"


class TestOccStStephan:
    @pytest.fixture(scope="class")
    def result(self):
        return compute_occ_st_stephan()

    def test_has_expected_keys(self, result):
        for k in (
            "target_org",
            "occ_records_main_only",
            "occ_records_including_suborgs",
            "distinct_persons",
            "persons_with_kin_relations",
            "kin_records_sum",
            "frontend_section_count",
            "frontend_row_count",
            "frontend_kin_sum",
            "status_persons",
            "status_kin",
            "status_section_vs_rows",
        ):
            assert k in result, f"Key {k!r} fehlt im Resultat"

    def test_persons_status_never_mismatch(self, result):
        assert result["status_persons"] in ("match", "known_gap", "no_frontend"), (
            f"status_persons={result['status_persons']!r}: Frontend zeigt "
            f"mehr Personen als der Pipeline-Sollwert. Aggregator-Drift?"
        )

    def test_kin_status_never_mismatch(self, result):
        assert result["status_kin"] in ("match", "known_gap", "no_frontend"), (
            f"status_kin={result['status_kin']!r}: Frontend zeigt mehr "
            f"kin-Records als der Pipeline-Sollwert."
        )

    def test_section_count_matches_row_count(self, result):
        assert result["status_section_vs_rows"] in ("match", "no_frontend"), (
            "Renderer-Drift: die im section-head angezeigte Zahl weicht "
            "von der Zeilenanzahl in der Tabelle ab."
        )
