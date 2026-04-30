"""Tests for M0: Quality Data Pipeline.

Tests the quality index loading, score computation, quality JSON generation,
and integration of quality fields into document metadata.
"""

import json

import pytest

from frontend.build import (
    _load_quality_index,
    _quality_score,
    _build_quality_json,
    _parse_file,
)
from frontend.config import VALIDATION_REPORT_PATH


# --- _quality_score ---

class TestQualityScore:
    def test_no_findings_returns_ok(self):
        assert _quality_score([]) == 0

    def test_none_treated_as_empty(self):
        assert _quality_score(None) == 0

    def test_single_info_returns_notice(self):
        findings = [{"severity": "info", "category": "x", "detail": "y"}]
        assert _quality_score(findings) == 1

    def test_multiple_info_returns_notice(self):
        findings = [
            {"severity": "info", "category": "a", "detail": "b"},
            {"severity": "info", "category": "c", "detail": "d"},
        ]
        assert _quality_score(findings) == 1

    def test_warning_returns_warning(self):
        findings = [{"severity": "warning", "category": "x", "detail": "y"}]
        assert _quality_score(findings) == 2

    def test_error_returns_warning(self):
        findings = [{"severity": "error", "category": "x", "detail": "y"}]
        assert _quality_score(findings) == 2

    def test_mixed_severities_returns_worst(self):
        findings = [
            {"severity": "info", "category": "a", "detail": "b"},
            {"severity": "warning", "category": "c", "detail": "d"},
        ]
        assert _quality_score(findings) == 2


# --- _load_quality_index ---

class TestLoadQualityIndex:

    @pytest.fixture(scope="class")
    def quality_index(self):
        """Load the quality index once for the whole test class."""
        if not VALIDATION_REPORT_PATH.exists():
            pytest.skip("validation_report.json not found")
        return _load_quality_index()

    def test_returns_non_empty_dict(self, quality_index):
        assert isinstance(quality_index, dict)
        assert len(quality_index) > 0

    def test_paths_use_forward_slashes(self, quality_index):
        for key in quality_index:
            assert "\\" not in key, f"Backslash in key: {key}"

    def test_findings_have_required_fields(self, quality_index):
        for findings in list(quality_index.values())[:5]:
            for f in findings:
                assert "severity" in f
                assert "category" in f
                assert "detail" in f

    def test_finding_count_is_positive(self, quality_index):
        """The report should have a plausible number of findings."""
        total = sum(len(findings) for findings in quality_index.values())
        assert total > 500, f"Expected >500 findings, got {total}"


# --- _build_quality_json ---

class TestBuildQualityJson:
    def test_writes_quality_json(self, tmp_path, monkeypatch):
        import frontend.build
        monkeypatch.setattr(frontend.build, "DATA_DIR", tmp_path)

        quality_index = {
            "QGW/Vienna_1177-1414_ready/done/100.xml": [
                {"severity": "warning", "category": "ref_null", "detail": "test"},
            ],
            "QGW/Vienna_1177-1414_ready/done/101.xml": [
                {"severity": "info", "category": "instant", "detail": "test2"},
                {"severity": "info", "category": "instant", "detail": "test3"},
            ],
        }
        _build_quality_json(quality_index)

        out = tmp_path / "quality.json"
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "meta" in data
        assert data["meta"]["schema_version"] == "1.0"
        assert data["coverage"]["totalFiles"] == 2
        assert data["coverage"]["totalFindings"] == 3
        assert data["observations"]["bySeverity"]["warning"] == 1
        assert data["observations"]["bySeverity"]["info"] == 2
        assert data["observations"]["byCategory"]["ref_null"] == 1
        assert data["observations"]["byCategory"]["instant"] == 2

    def test_by_collection_grouping(self, tmp_path, monkeypatch):
        import frontend.build
        monkeypatch.setattr(frontend.build, "DATA_DIR", tmp_path)

        quality_index = {
            "QGW/Vienna_1177-1414_ready/done/100.xml": [
                {"severity": "warning", "category": "ref_null", "detail": "x"},
            ],
            "Gewerbuch_D/GB_D_1448-60_ready/done/file.xml": [
                {"severity": "info", "category": "instant", "detail": "y"},
            ],
        }
        _build_quality_json(quality_index)

        data = json.loads((tmp_path / "quality.json").read_text(encoding="utf-8"))
        assert "QGW/Vienna_1177-1414_ready" in data["observations"]["byCollection"]
        assert "Gewerbuch_D/GB_D_1448-60_ready" in data["observations"]["byCollection"]

    def test_empty_index_writes_zeros(self, tmp_path, monkeypatch):
        import frontend.build
        monkeypatch.setattr(frontend.build, "DATA_DIR", tmp_path)

        _build_quality_json({})

        data = json.loads((tmp_path / "quality.json").read_text(encoding="utf-8"))
        assert data["coverage"]["totalFiles"] == 0
        assert data["coverage"]["totalFindings"] == 0
        assert data["observations"]["bySeverity"] == {}
        assert data["observations"]["byCategory"] == {}
        assert data["observations"]["byCollection"] == {}


# --- Integration: quality fields in document metadata ---

class TestQualityInMetadata:
    def test_parse_file_adds_quality_fields(self):
        """_parse_file injects quality_score/count/findings into metadata."""
        from frontend.register import load_persons, load_orgs, load_places
        from pipeline.config import REPO_ROOT

        filepath = REPO_ROOT / "sources/QGW/Vienna_1177-1414_ready/done/100.xml"
        registers = (load_persons(), load_orgs(), load_places())

        # With a synthetic quality index
        quality_index = {
            "QGW/Vienna_1177-1414_ready/done/100.xml": [
                {"severity": "warning", "category": "ref_null", "detail": "test"},
            ],
        }
        result = _parse_file(filepath, registers, quality_index)
        assert result is not None
        meta = result[0]
        assert meta["quality_score"] == 2
        assert meta["quality_count"] == 1
        assert len(meta["quality_findings"]) == 1

    def test_parse_file_without_findings_scores_zero(self):
        """Documents without findings get score 0."""
        from frontend.register import load_persons, load_orgs, load_places
        from pipeline.config import REPO_ROOT

        filepath = REPO_ROOT / "sources/QGW/Vienna_1177-1414_ready/done/100.xml"
        registers = (load_persons(), load_orgs(), load_places())

        result = _parse_file(filepath, registers, {})
        assert result is not None
        meta = result[0]
        assert meta["quality_score"] == 0
        assert meta["quality_count"] == 0
        assert meta["quality_findings"] == []

    def test_parse_file_without_quality_index(self):
        """Passing None as quality_index defaults to score 0."""
        from frontend.register import load_persons, load_orgs, load_places
        from pipeline.config import REPO_ROOT

        filepath = REPO_ROOT / "sources/QGW/Vienna_1177-1414_ready/done/100.xml"
        registers = (load_persons(), load_orgs(), load_places())

        result = _parse_file(filepath, registers, None)
        assert result is not None
        meta = result[0]
        assert meta["quality_score"] == 0
        assert meta["quality_count"] == 0
