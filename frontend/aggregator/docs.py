"""Per-source aggregate (docs_aggregate.json) and docs_lookup.json."""

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

    Consolidates per source (file_key) person and event counts with sex
    and form-of-treatment breakdown. Reads only pipeline CSVs (no TEI
    parsing). Distinct persons are all person_keys appearing in
    persons_in_sources with the file_key (kind_of_linking ref OR
    corresp; Berthold's wife shares Berthold's pe__-key, Berthold is
    counted once).

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

        # filenames.csv URL-encodes special characters in the filename
        # (e.g. `1542 a.xml` -> `1542%20a.xml`). The build.py metadata
        # counterpart is NOT encoded, so decode here so the
        # (collection_path, idno) lookup matches.
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


def build_docs_entities(
    docs_data_dir: Path,
    forward_entities: dict[str, dict[str, list[str]]],
) -> None:
    """Build ``docs_entities.json`` (idno -> {p:[...], o:[...]}).

    The forward index maps each source ``idno`` to the lists of person
    and organisation IDs annotated in that source via ``rs/@ref``. To
    keep payload small and avoid extra fetches on the client side, each
    referenced entity is enriched here with its display fields read back
    from the just-written register search JSONs (``persons_search.json``
    and ``orgs_search.json``).

    Output shape::

        {
          "<idno>": {
            "p": [{"id": "pe__...", "n": "Name", "sex": "m",
                    "am": 1340, "ax": 1366}, ...],
            "o": [{"id": "org__...", "n": "Name", "tp": "Pfarre"}, ...]
          }
        }

    Consumed by ``basket.js`` to attach derived person/org entries when
    the user adds a source to the data basket. Missing referenced IDs
    (e.g. entities filtered out of the released search data) are
    skipped silently; the basket simply gets fewer derived entries.
    """
    import json

    persons_search = docs_data_dir / "persons_search.json"
    orgs_search = docs_data_dir / "orgs_search.json"
    pmap: dict[str, dict] = {}
    omap: dict[str, dict] = {}
    if persons_search.exists():
        for row in json.loads(persons_search.read_text(encoding="utf-8")):
            pid = row.get("id", "")
            if pid:
                pmap[pid] = {
                    "id":  pid,
                    "n":   row.get("n", ""),
                    "sex": row.get("sex", ""),
                    "am":  row.get("am", ""),
                    "ax":  row.get("ax", ""),
                }
    if orgs_search.exists():
        for row in json.loads(orgs_search.read_text(encoding="utf-8")):
            oid = row.get("id", "")
            if oid:
                omap[oid] = {
                    "id": oid,
                    "n":  row.get("n", ""),
                    "tp": row.get("tp", ""),
                }

    out: dict[str, dict[str, list[dict]]] = {}
    for idno, refs in forward_entities.items():
        persons_resolved = [pmap[pid] for pid in refs.get("p", []) if pid in pmap]
        orgs_resolved = [omap[oid] for oid in refs.get("o", []) if oid in omap]
        if persons_resolved or orgs_resolved:
            out[idno] = {"p": persons_resolved, "o": orgs_resolved}

    _write_json(out, docs_data_dir / "docs_entities.json")
    print(f"  Docs entities: {len(out)} sources with person/org references")


def build_docs_lookup(docs_data_dir: Path, all_metadata: list[dict]) -> None:
    """Build a file_key -> document metadata JSON for exploration drill-down.

    Maps pipeline file_keys (from filenames.csv) to public URLs and metadata,
    enabling the JS drill-down overlay to display document details.
    """
    fnames = _cached_csv("filenames.csv")

    # Build (collection, subcollection, filename_stem) -> file_key.
    # filenames.csv URL-encodes special characters ('1542 a.xml' ->
    # '1542%20a.xml'); build.py sets meta['filename'] = filepath.stem from
    # the filesystem, i.e. raw form with spaces. For the lookup to hit, we
    # decode here the same way aggregate_docs does for the (collection_path,
    # idno) lookup. Otherwise 13 documents drop out of docs_lookup and
    # drill-down/register URLs cannot be resolved.
    fkey_map: dict[tuple, str] = {}
    for r in fnames:
        fk = r.get("id", "")
        coll = r.get("collection", "")
        subcoll = r.get("subcollection", "")
        fname = unquote(r.get("file", "").replace(".xml", ""))
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
