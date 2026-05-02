"""Pro-Quelle-Aggregat (docs_aggregate.json) und docs_lookup.json."""

import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

from ._shared import _cached_csv, _meta, _write_json


def _parse_date_range(date_str: str) -> tuple[str | None, str | None, int | None]:
    """Parse the ``date`` field from filenames.csv.

    Pipeline conventions:
      ``1177-05-10``                -> ("1177-05-10", "1177-05-10", 1177)
      ``1208-01-01 | 1208-12-31``   -> ("1208-01-01", "1208-12-31", 1208)
      empty / unparseable           -> (None, None, None)
    """
    if not date_str:
        return None, None, None
    parts = [p.strip() for p in date_str.split("|") if p.strip()]
    if not parts:
        return None, None, None
    start = parts[0]
    end = parts[-1] if len(parts) > 1 else parts[0]
    year = None
    if len(start) >= 4:
        try:
            year = int(start[:4])
        except ValueError:
            year = None
    return start, end, year


def aggregate_docs(docs_data_dir: Path) -> dict:
    """Per-source aggregate: counts, dates, event-form distribution.

    Konsolidiert pro Quelle (file_key) Personen- und Event-Counts mit
    Geschlechter- und Form-Aufschluesselung. Liest ausschliesslich
    Pipeline-CSVs (kein TEI-Parsing). Persons distinct sind alle
    person_keys, die in persons_in_sources mit dem file_key auftauchen
    (kind_of_linking ref ODER corresp; Berthold's Gemahlin teilt
    Berthold's pe__-Key, Berthold wird einmal gezaehlt).

    Output: docs/data/docs_aggregate.json
    """
    fnames = _cached_csv("filenames.csv")
    persons = _cached_csv("persons.csv")
    pis = _cached_csv("persons_in_sources.csv")
    eis = _cached_csv("events_in_sources.csv")

    # Sex lookup: person_key -> 'f' | 'm' | '' (empty = not annotated)
    sex_by_person: dict[str, str] = {
        p.get("id", ""): (p.get("sex", "") or "").strip().lower()
        for p in persons
    }

    # Distinct persons per source (any kind_of_linking)
    persons_per_file: dict[str, set[str]] = defaultdict(set)
    for r in pis:
        fk = r.get("file_key", "")
        pk = r.get("person_key", "")
        if fk and pk:
            persons_per_file[fk].add(pk)

    # Events per source: distinct event_keys, broken down by event_in
    EVENT_BUCKETS = ("abstract", "seal", "entry", "nota", "other")
    events_per_file: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {b: set() for b in ("_all",) + EVENT_BUCKETS}
    )
    for r in eis:
        fk = r.get("file_key", "")
        ek = r.get("event_key", "")
        ein = (r.get("event_in", "") or "").strip().lower()
        if not fk or not ek:
            continue
        bucket = ein if ein in EVENT_BUCKETS[:-1] else "other"
        events_per_file[fk]["_all"].add(ek)
        events_per_file[fk][bucket].add(ek)

    # Build records (released sources only — _cached_csv pre-filters by
    # collection; here also filter status='done' to match build.py which
    # only processes TEI files under .../done/ subdirectories).
    records = []
    for f in fnames:
        fk = f.get("id", "")
        if not fk:
            continue
        if (f.get("status", "") or "").strip() != "done":
            continue

        date_raw = (f.get("date", "") or "").strip()
        date_iso_start, date_iso_end, date_year = _parse_date_range(date_raw)

        pks = persons_per_file.get(fk, set())
        pcd = len(pks)
        pcdf = sum(1 for pk in pks if sex_by_person.get(pk) == "f")
        pcdm = sum(1 for pk in pks if sex_by_person.get(pk) == "m")
        pcdu = pcd - pcdf - pcdm

        eb = events_per_file.get(fk)
        if eb is None:
            event_dist = {b: 0 for b in ("total",) + EVENT_BUCKETS}
        else:
            event_dist = {
                "total": len(eb["_all"]),
                **{b: len(eb[b]) for b in EVENT_BUCKETS},
            }

        # filenames.csv URL-encodet Sonderzeichen im Dateinamen (z.B.
        # `1542 a.xml` -> `1542%20a.xml`). Das build.py-Metadata-Pendant
        # ist NICHT encoded, also dekodieren, damit der (collection_path,
        # idno)-Lookup stimmt.
        idno = unquote(f.get("file", "").replace(".xml", ""))
        records.append({
            "file_key": fk,
            "idno": idno,
            "collection_path": (
                f"{f.get('collection', '')}/{f.get('subcollection', '')}"
            ),
            "date_iso_start": date_iso_start,
            "date_iso_end": date_iso_end,
            "date_year": date_year,
            "persons": {
                "distinct": pcd,
                "f": pcdf,
                "m": pcdm,
                "u": pcdu,
            },
            "events": event_dist,
        })

    records.sort(key=lambda r: r["file_key"])

    output = {
        "meta": _meta(
            description=(
                "Per-source aggregate: distinct persons (with sex "
                "breakdown), distinct events (with TEI div-type "
                "breakdown: abstract / seal / entry / nota), "
                "and normalised dates from filenames.csv."
            ),
            sources=[
                "filenames.csv",
                "persons.csv",
                "persons_in_sources.csv",
                "events_in_sources.csv",
            ],
            dimensions=[
                {"name": "file_key", "type": "entity", "id_prefix": "f__"},
            ],
            measures=[
                {"name": "persons.distinct", "type": "count",
                 "description": "Distinct register-linked persons"},
                {"name": "persons.f", "type": "count",
                 "description": "Distinct female"},
                {"name": "persons.m", "type": "count",
                 "description": "Distinct male"},
                {"name": "persons.u", "type": "count",
                 "description": "Distinct without sex annotation"},
                {"name": "events.total", "type": "count",
                 "description": "Distinct events"},
                {"name": "events.abstract", "type": "count",
                 "description": "Events with event_in=abstract"},
                {"name": "events.seal", "type": "count",
                 "description": "Events with event_in=seal"},
                {"name": "events.entry", "type": "count",
                 "description": "Events with event_in=entry"},
                {"name": "events.nota", "type": "count",
                 "description": "Events with event_in=nota"},
            ],
        ),
        "docs": records,
    }

    _write_json(output, docs_data_dir / "docs_aggregate.json")
    return {
        "total": len(records),
        "with_persons": sum(1 for r in records if r["persons"]["distinct"] > 0),
    }


def build_docs_lookup(docs_data_dir: Path, all_metadata: list[dict]) -> None:
    """Build a file_key -> document metadata JSON for exploration drill-down.

    Maps pipeline file_keys (from filenames.csv) to public URLs and metadata,
    enabling the JS drill-down overlay to display document details.
    """
    fnames = _cached_csv("filenames.csv")

    # Build (collection, subcollection, filename_stem) -> file_key
    fkey_map: dict[tuple, str] = {}
    for r in fnames:
        fk = r.get("id", "")
        coll = r.get("collection", "")
        subcoll = r.get("subcollection", "")
        fname = r.get("file", "").replace(".xml", "")
        if fk:
            fkey_map[(coll, subcoll, fname)] = fk

    lookup = {}
    for meta in all_metadata:
        key = (meta.get("collection", ""),
               meta.get("subcollection", ""),
               meta.get("filename", ""))
        fk = fkey_map.get(key)
        if fk:
            lookup[fk] = {
                "u": meta.get("url", ""),
                "i": meta.get("idno", ""),
                "d": meta.get("date_display", ""),
                "c": meta.get("collection_label", ""),
                "r": (meta.get("regest", "") or "")[:150],
            }

    _write_json(lookup, docs_data_dir / "docs_lookup.json")
    print(f"  Docs lookup: {len(lookup)} documents mapped")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

