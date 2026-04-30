"""Unit tests for build helper functions in frontend.build."""

import pytest
from pathlib import Path

from pipeline.config import SOURCES_DIR
from frontend.build import (
    _output_path,
    _collection_label,
    _sort_key_for_nav,
    _compute_prev_next,
    _extract_regest,
    _relative_to_root,
    _is_done_file,
    _normalize_facsimile_url,
)
from frontend.config import DOCS_DIR
from pipeline.utils.xml_loader import load_xml


class TestOutputPath:
    def test_strips_done(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        result = _output_path(filepath)
        assert "done" not in result.parts

    def test_changes_extension(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        result = _output_path(filepath)
        assert result.suffix == ".html"

    def test_documents_subdir(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        result = _output_path(filepath)
        assert "documents" in result.parts


class TestCollectionLabel:
    def test_known_qgw(self):
        assert "QGW II/1" in _collection_label("QGW", "Vienna_1177-1414_ready")

    def test_known_stb(self):
        result = _collection_label("Stadtbuecher", "Band_1_1395-1400_ready")
        assert "Stadtbücher" in result

    def test_unknown_fallback(self):
        result = _collection_label("Unknown", "SubDir")
        assert result == "Unknown/SubDir"


class TestSortKeyForNav:
    def test_numeric_order(self):
        assert _sort_key_for_nav("100") < _sort_key_for_nav("200")

    def test_numeric_before_string(self):
        assert _sort_key_for_nav("100") < _sort_key_for_nav("abc")

    def test_string_key(self):
        key = _sort_key_for_nav("abc")
        assert key == (1, 0, "abc")


class TestComputePrevNext:
    def test_three_docs(self):
        metas = [
            {"filename": "1", "collection_path": "A/B", "url": "A/B/1.html", "idno": "1"},
            {"filename": "2", "collection_path": "A/B", "url": "A/B/2.html", "idno": "2"},
            {"filename": "3", "collection_path": "A/B", "url": "A/B/3.html", "idno": "3"},
        ]
        _compute_prev_next(metas)
        assert metas[0]["prev_url"] == ""
        assert metas[0]["next_id"] == "2"
        assert metas[1]["prev_id"] == "1"
        assert metas[1]["next_id"] == "3"
        assert metas[2]["prev_id"] == "2"
        assert metas[2]["next_url"] == ""


class TestExtractRegest:
    def test_truncation(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        if not filepath.exists():
            pytest.skip("Test file not available")
        tree = load_xml(filepath)
        result = _extract_regest(tree.getroot(), max_len=50)
        assert len(result) <= 55  # max_len + word boundary + ellipsis

    def test_returns_nonempty(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        if not filepath.exists():
            pytest.skip("Test file not available")
        tree = load_xml(filepath)
        result = _extract_regest(tree.getroot())
        assert len(result) > 0


class TestRelativeToRoot:
    def test_nested_depth(self):
        output = DOCS_DIR / "documents" / "QGW" / "Vienna_1177-1414_ready" / "100.html"
        result = _relative_to_root(output)
        assert result.count("..") >= 3


class TestIsDoneFile:
    def test_done_file_true(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1177-1414_ready" / "done" / "100.xml"
        assert _is_done_file(filepath) is True

    def test_non_done_file_false(self):
        filepath = SOURCES_DIR / "QGW" / "Vienna_1524" / "abstracts" / "2585.xml"
        if not filepath.exists():
            pytest.skip("Test file not available")
        assert _is_done_file(filepath) is False


class TestNormalizeFacsimileUrl:
    """Unit tests for facsimile URL normalization."""

    def test_absolute_http_unchanged(self):
        url = "http://images.monasterium.net/pics/AT-WStLA/HA-U/img.jpg"
        assert _normalize_facsimile_url(url, "QGW") == url

    def test_absolute_https_unchanged(self):
        url = "https://files.transkribus.eu/Get?id=ABC&fileType=view"
        assert _normalize_facsimile_url(url, "Gewerbuch_D") == url

    def test_satzbuch_relative_resolved(self):
        filename = "WSTLA_Grundbuch_Stadt_Wien_B1_34_SatzbuchCD_0026.jpg"
        result = _normalize_facsimile_url(filename, "Satzbuch_CD")
        assert result == f"https://id.acdh.oeaw.ac.at/grundbuecher-facs/{filename}"

    def test_gewerbuch_relative_dropped(self):
        filename = "WSTLA_Grundbuch_Stadt_Wien_B1_Grundbuch_7_Gew%C3%A4hrbuch_D_1020.jpg"
        assert _normalize_facsimile_url(filename, "Gewerbuch_D") is None

    def test_empty_string_dropped(self):
        assert _normalize_facsimile_url("", "Gewerbuch_D") is None

    def test_empty_string_any_collection(self):
        assert _normalize_facsimile_url("", "QGW") is None

    def test_unknown_collection_relative_dropped(self):
        assert _normalize_facsimile_url("some_file.jpg", "UnknownCollection") is None

    def test_absolute_url_any_collection(self):
        url = "https://example.com/image.jpg"
        assert _normalize_facsimile_url(url, "UnknownCollection") == url
