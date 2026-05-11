"""Shared helpers, CSV cache and RELEASED_CORPORA filter.

Consumed by the entire aggregator package. Contains:
- _load_csv / _cached_csv: CSV reader with module-level cache
- _is_released_row / _released_file_keys: RELEASED_CORPORA filter
- _load_norm_matching: normalisation tables
- _parse_coord / _decade: value parsers
- _meta / _write_json: output helpers
- SCHEMA_VERSION: global versioning constant
"""

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from pipeline.config import PIPELINE_OUTPUT, NORM_LISTS_DIR
from frontend.config import is_released_corpus

# Schema version — increment when output structure changes
SCHEMA_VERSION = "1.0"


def _is_released_row(row: dict) -> bool:
    """True if the CSV row belongs to a released source corpus.

    Pipeline CSVs list all holdings. For frontend aggregates only released
    ones count. This removes the Vienna_1448-57_ready gap and the counting
    of non-released QGW volumes.
    """
    coll = row.get("collection", "")
    sub = row.get("subcollection", "")
    if not coll or not sub:
        return False
    return is_released_corpus(f"{coll}/{sub}")


def _load_csv(path: Path, delimiter: str = ";") -> list[dict]:
    """Load a CSV file and return rows as list of dicts."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)


# Module-level CSV cache to avoid redundant I/O across aggregations
_csv_cache: dict[str, list[dict]] = {}


_released_file_keys_cache: set[str] | None = None


def _released_file_keys() -> set[str]:
    """Set of all file_keys belonging to released source corpora.

    Backed by filenames.csv (incl. collection/subcollection); reads the
    CSV file directly here so _cached_csv is not invoked recursively.
    """
    global _released_file_keys_cache
    if _released_file_keys_cache is None:
        rows = _load_csv(PIPELINE_OUTPUT / "filenames.csv")
        _released_file_keys_cache = {
            r.get("id", "") for r in rows if _is_released_row(r)
        }
    return _released_file_keys_cache


def _cached_csv(name: str, delimiter: str = ";") -> list[dict]:
    """Load a pipeline CSV once, return cached result on subsequent calls.

    Filters out rows from non-released source corpora:
    - CSVs with `collection` + `subcollection` via direct path check.
    - CSVs with `file_key` (and no collection) via the set of released
      file_keys from filenames.csv.
    This way mentions from non-released volumes leak neither into counts
    nor into drill-downs.
    """
    if name not in _csv_cache:
        rows = _load_csv(PIPELINE_OUTPUT / name, delimiter)
        if rows:
            first = rows[0]
            if "collection" in first and "subcollection" in first:
                rows = [r for r in rows if _is_released_row(r)]
            elif "file_key" in first:
                fks = _released_file_keys()
                rows = [r for r in rows if r.get("file_key", "") in fks]
        _csv_cache[name] = rows
    return _csv_cache[name]


def _load_norm_matching() -> dict[str, str]:
    """Load label_norm_matching.csv -> {source_catchword: catchword_main_norm}.

    Tab-delimited. Only rows with a non-empty catchword_main_norm are included.
    """
    path = NORM_LISTS_DIR / "label_norm_matching.csv"
    result = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            src = row.get("source_catchword", "").strip()
            norm = row.get("catchword_main_norm", "").strip()
            if src and norm:
                result[src] = norm
    return result


def _parse_coord(value: str) -> float | None:
    """Parse a coordinate string, handling comma decimals and text suffixes.

    Examples: '48,23134719' -> 48.23134719, '16.45N' -> 16.45,
    '13.95049 Möglich' -> 13.95049
    """
    if not value:
        return None
    # Replace comma with dot (German locale)
    cleaned = value.replace(",", ".")
    # Strip non-numeric suffixes (keep leading minus, digits, dots)
    match = re.match(r'^(-?[\d.]+)', cleaned)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _decade(date_str: str) -> int | None:
    """Extract decade from an ISO-ish date string (e.g. '13270415' -> 1320).

    Returns None for placeholder dates ('99999999') or unparseable values.
    """
    if not date_str or len(date_str) < 4:
        return None
    year_str = date_str[:4]
    try:
        year = int(year_str)
    except ValueError:
        return None
    if year > 1600 or year < 1000:
        return None
    return (year // 10) * 10


def _meta(description: str, sources: list[str],
          dimensions: list[dict], measures: list[dict]) -> dict:
    """Build a standardised meta block for a dataset JSON.

    Follows Data-Cube-inspired conventions:
    - dimensions: the categorical axes of the data (e.g. decade, sex, role)
    - measures: the numeric values being aggregated (e.g. count, weight)
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "created": date.today().isoformat(),
        "description": description,
        "sources": sources,
        "structure": {
            "dimensions": dimensions,
            "measures": measures,
        },
    }


def _write_json(data: dict | list, path: Path) -> None:
    """Write JSON to file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
