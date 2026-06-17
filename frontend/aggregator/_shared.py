"""Shared helpers, CSV cache and corpus visibility filter.

Consumed by the entire aggregator package. Contains:
- _cached_csv: CSV reader with module-level cache, filtered to the corpora
  visible in the current view (audience-coupled, see _is_visible_row)
- _is_visible_row / _is_released_row: visible vs released corpus filters
- _visible_file_keys / _released_file_keys: scoped file_key sets
- _load_norm_matching: normalisation tables
- _parse_coord / _decade: value parsers
- _meta / _write_json: output helpers
- SCHEMA_VERSION: global versioning constant
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from pipeline.config import PIPELINE_OUTPUT, NORM_LISTS_DIR
from frontend.config import is_released_corpus, is_visible_corpus

# Schema version — increment when output structure changes
SCHEMA_VERSION = "1.0"

# Lift csv field-size limit; events_in_sources.csv has long `text` cells.
csv.field_size_limit(10_000_000)


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


def _is_visible_row(row: dict) -> bool:
    """True if the CSV row belongs to a corpus visible in the current view.

    Audience-gekoppelt: 'oeffentlich' laesst nur PUBLIC_CORPORA durch,
    'intern' den vollen freigegebenen Umfang. Dies ist der Filter fuer die
    oeffentlich ausgelieferten Aggregat-JSONs, damit kein nicht-freigegebenes
    Korpus (z.B. Satzbuch CD, QGW II/2) ueber roles/relations/transactions/
    role_constellation/timeline in die oeffentliche Sicht leckt.
    """
    coll = row.get("collection", "")
    sub = row.get("subcollection", "")
    if not coll or not sub:
        return False
    return is_visible_corpus(f"{coll}/{sub}")


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


_visible_file_keys_cache: set[str] | None = None


def _visible_file_keys() -> set[str]:
    """Set of file_keys belonging to corpora visible in the current view.

    Wie _released_file_keys, aber sicht-gekoppelt (siehe _is_visible_row).
    Backed by filenames.csv; reads the CSV directly here so _cached_csv is
    not invoked recursively.
    """
    global _visible_file_keys_cache
    if _visible_file_keys_cache is None:
        rows = _load_csv(PIPELINE_OUTPUT / "filenames.csv")
        _visible_file_keys_cache = {
            r.get("id", "") for r in rows if _is_visible_row(r)
        }
    return _visible_file_keys_cache


def _cached_csv(name: str, delimiter: str = ";") -> list[dict]:
    """Load a pipeline CSV once, return cached result on subsequent calls.

    Filters out rows from corpora not visible in the current view
    (audience-coupled, see _is_visible_row):
    - CSVs with `collection` + `subcollection` via direct path check.
    - CSVs with `file_key` (and no collection) via the set of visible
      file_keys from filenames.csv.
    This way mentions from non-public volumes leak neither into counts
    nor into drill-downs of the public-facing aggregate JSONs.
    """
    if name not in _csv_cache:
        rows = _load_csv(PIPELINE_OUTPUT / name, delimiter)
        if rows:
            first = rows[0]
            if "collection" in first and "subcollection" in first:
                rows = [r for r in rows if _is_visible_row(r)]
            elif "file_key" in first:
                fks = _visible_file_keys()
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


def _load_rolename_norm() -> dict[str, str]:
    """Load roleName_norm_matching.csv -> {spelling_lower: contentual_norm}.

    Bildet die (case-insensitive) Schreibweise einer Rollen-/Amts-/Berufs-
    bezeichnung auf ihre inhaltliche Normalform ab, z. B. "pischolf" ->
    "Bischof". Faellt auf die Schreibungs-Normform und schliesslich (im
    Aufrufer) auf die Rohschreibung zurueck, wenn die inhaltliche Normform
    fehlt. Tab-delimited, utf-8-sig; Lookup case-insensitiv wie bei
    _load_uhlirz_matching, weil die occ-Spalte gemischte Schreibung traegt.
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    result: dict[str, str] = {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            src = (row.get("roleName_spelling") or "").strip().lower()
            if not src:
                continue
            norm = ((row.get("roleName_contentual_norm") or "").strip()
                    or (row.get("roleName_spelling_norm") or "").strip())
            if norm:
                result[src] = norm
    return result


def _load_uhlirz_matching() -> dict[str, list[str]]:
    """Load roleName_norm_matching.csv -> {original_spelling_lower: [uhlirz_categories]}.

    Tab-delimited. Schluessel ist die Originalschreibung des Berufs
    (Spalte ``roleName_spelling``), **in Kleinschreibung**, wie sie auch
    in der TEI-Annotation ``<occupation>`` und damit in den
    ``occ_relations_in_sources.csv`` Spalte ``occ`` vorkommt. Wert ist
    eine Liste, weil eine Schreibvariante prinzipiell mehrere Uhlirz-
    Kategorien tragen kann (selten, aber moeglich nach Daten-Stand
    2026-05).

    Lookup muss case-insensitiv erfolgen, weil das CSV uneinheitlich
    sowohl ``Wachsgiesser`` als auch ``wachsgiesser`` enthalten kann,
    und die ``occ``-Spalte in den Pipeline-CSVs ebenfalls beide
    Schreibungen tragen kann.

    Eintraege ohne Kategorie werden uebersprungen. Mehrere Zeilen mit
    derselben Originalschreibung (case-insensitiv) werden zu einer
    Liste vereinigt (deduplisiert).
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    result: dict[str, set[str]] = {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            src = (row.get("roleName_spelling") or "").strip().lower()
            cat = (row.get("Gewerbe_nach_Uhlirz_GstW") or "").strip()
            if src and cat:
                result.setdefault(src, set()).add(cat)
    return {k: sorted(v) for k, v in result.items()}


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
