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


def tag_text(value: str) -> str:
    """Anzeigeform eines Rollen-/Berufs-Werts aus den Beziehungs-CSVs.

    Die Pipeline verkettet die Textknoten EINES roleName-Tags mit ``|``
    (XSLT-Erbe: ``normalize-space(string-join(.//text(), '|'))``). Ein
    Strich markiert dort also eine Elementgrenze innerhalb des Tags
    (``Bürger|meister``, ``mein genedig |herren| herczog``), kein
    zweites Tag. Fuer Anzeige und Nachschlagen wird er zu einem
    Leerzeichen, Leerraum wird zusammengezogen.
    """
    return re.sub(r"\s+", " ", (value or "").replace("|", " ")).strip()


def norm_key(value: str) -> str:
    """Vergleichsschluessel fuer die roleName-Normliste: ``tag_text`` in
    Kleinschreibung. Wird auf BEIDE Seiten angewandt (Listenschluessel
    und CSV-Wert), damit Striche, Leerraum und Gross/Klein nie
    entscheiden. Entspricht ``_norm_key`` in ``pipeline/integrity.py``.
    """
    return tag_text(value).lower()


def split_multi(cell: str) -> list[str]:
    """Zerlegt eine Mehrfach-Zelle aus ``persons_in_sources.csv``
    (``source_prof``, ``source_titles``) in ihre Tags.

    Dort trennt ``|`` MEHRERE Tags derselben Art einer Person
    (``Hantfestschreiber|Pikcher`` = zwei prof-Tags). Jeder Teil wird
    einzeln nachgeschlagen. Leere Teile entfallen.
    """
    return [p.strip() for p in (cell or "").split("|") if p.strip()]


def _load_rolename_norm(role_type: str | None = None) -> dict:
    """Load roleName_norm_matching.csv -> inhaltliche Normalform je Tag.

    Schluessel ist seit 30.10.2026 das Paar aus roleName-Typ (Spalte
    ``type``: occ, prof, kin, title, rep, title_ref, tenant) und
    ``norm_key(roleName_spelling)``. Dieselbe Schreibung kann je Typ
    eine andere Klasse tragen ("wirt" als kin = Ehegatt_in, als prof =
    Gastwirt_in; "bruder" als kin = Geschwister, als title =
    Ordensbruder_Schwester), ein Lookup nur ueber die Schreibung waere
    deshalb mehrdeutig.

    - ``role_type`` gesetzt: ``{norm_key(spelling): klasse}`` nur fuer
      Zeilen dieses Typs (so rufen die Aggregatoren auf).
    - ``role_type`` None: ``{(type, norm_key(spelling)): klasse}``.

    Klasse = ``roleName_contentual_norm``, ersatzweise
    ``roleName_spelling_norm``; der Aufrufer faellt auf die Rohschreibung
    zurueck. Erste Zeile je Schluessel gewinnt. Zeilen ohne Typ werden
    uebersprungen. Tab-delimited, utf-8-sig.
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    result: dict = {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rtype = (row.get("type") or "").strip()
            src = norm_key(row.get("roleName_spelling") or "")
            if not src or not rtype:
                continue
            if role_type is not None and rtype != role_type:
                continue
            norm = ((row.get("roleName_contentual_norm") or "").strip()
                    or (row.get("roleName_spelling_norm") or "").strip())
            if not norm:
                continue
            key = src if role_type is not None else (rtype, src)
            result.setdefault(key, norm)
    return result


def _load_uhlirz_matching(role_type: str = "prof") -> dict[str, list[str]]:
    """Load roleName_norm_matching.csv -> {norm_key(spelling): [uhlirz_categories]}.

    Die Uhlirz-Klassifikation (Spalte ``Gewerbe_nach_Uhlirz_GstW``) ist
    seit 30.10.2026 ausschliesslich eine Eigenschaft von Berufen, also
    von Zeilen mit ``type`` = prof. Werte an occ- oder rep-Zeilen in der
    Liste sind Altbestand und werden hier ignoriert (``role_type``
    steuert das; Default prof). Schluessel ist ``norm_key`` der
    Originalschreibung, wie sie in ``persons_in_sources.csv`` Spalte
    ``source_prof`` steht (dort ``|``-getrennt je Tag, siehe
    ``split_multi``).

    Wert ist eine Liste, weil eine Schreibung prinzipiell mehrere
    Kategorien tragen kann. Eintraege ohne Kategorie werden
    uebersprungen, mehrere Zeilen derselben Schreibung werden vereinigt.
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    result: dict[str, set[str]] = {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if (row.get("type") or "").strip() != role_type:
                continue
            src = norm_key(row.get("roleName_spelling") or "")
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
