"""Build-Package: orchestriert Register laden, TEI parsen, HTML/JSON schreiben.

Submodule:
- _helpers.py    Datums-/Pfad-/Jinja-Helfer, Label-Aufloesung, Sort-Keys
- _metadata.py   TEI-Header extrahieren, body rendern, Datei schreiben
- _kpi.py        Korpus-weite KPIs aus TEI via XPath, Korpus-Matrix
- _pages.py      Seiten-Builder (Startseite, Quellen, Register, Exploration,
                 Analyse, statische Markdown-Seiten)

Public API: re-exportiert hier fuer Backwards-Compat mit `from frontend.build
import ...` (build_single, build_all, _init_jinja, Pfad-Konstanten u.v.m.,
ueber die existierende Tests verfuegen).
"""

import shutil
import sys
import time

from pipeline.utils.xml_loader import collect_source_files

# Pfad-Konstanten und Helpers re-exportieren — viele Tests greifen
# direkt auf `frontend.build.DOCS_DIR`, `frontend.build.TEMPLATES_DIR` etc. zu.
from frontend.config import (
    DOCS_DIR, TEMPLATES_DIR, STATIC_DIR, CONTENT_DIR, KNOWLEDGE_DIR,
    DATA_DIR, FACSIMILE_BASE_URLS,
    EDITION_GUIDELINES_PATH,
    RELEASED_PERIOD, RELEASED_CORPORA, is_released_corpus,
    released_period_label, unprocessed_gaps_label, max_year_with_extensions,
)

from frontend.build._helpers import (
    _GERMAN_MONTHS,
    COLLECTION_LABELS,
    _format_german_date,
    _pipeline_repo_data_date,
    _create_markdown_processor,
    _collection_label,
    _xpath_text,
    _extract_regest,
    _extract_entity_refs,
    _init_jinja,
    _normalize_facsimile_url,
    _output_path,
    _relative_to_root,
    _is_done_file,
    _is_released_file,
    _tei_output_path,
    _load_registers,
    _sort_key_for_nav,
    _compute_prev_next,
    _format_table_date,
    _load_docs_aggregate_lookup,
    _copy_static,
    _copy_tei_sources,
)

from frontend.build._metadata import (
    _extract_metadata,
    _parse_file,
    _write_file,
)

from frontend.build._kpi import (
    _TEI_NS,
    _XP_TOP_EVENTS,
    _XP_PERSONS_EXCL_MENTIONED,
    _XP_PERSONS_ALL,
    _scan_released_tei,
    _compute_corpus_breakdown,
    _compute_release_kpis,
    _compute_matrix_columns,
    _released_person_keys,
    _persons_with_org_released,
)

from frontend.build._pages import (
    _build_index,
    _build_startseite,
    _person_search_data,
    _org_search_data,
    _place_search_data,
    _build_register_list_pages,
    _build_register_json,
    _build_person_profiles,
    _build_exploration,
    _build_guidelines,
    _build_about,
    _build_glossary,
    _build_impressum,
    _write_categories,
    _write_query_vocabulary,
    _build_analysis,
)

# Pipeline-Hilfen, die einige Tests via `frontend.build.<name>` ziehen
from pipeline.config import SOURCES_DIR, NS_MAP, REPO_ROOT  # noqa: F401


def build_single(filepath_str):
    """Build a single document."""
    filepath = REPO_ROOT / filepath_str
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    registers = _load_registers()

    env = _init_jinja()
    result = _parse_file(filepath, registers)
    if result:
        meta, body_html, output, _entity_refs = result
        _write_file(meta, body_html, output, env)
        print(f"Done. Output: {output}")
    _copy_static()
    _copy_tei_sources()


def build_all():
    """Build all documents + index page."""
    t0 = time.time()
    persons, orgs, places = _load_registers()
    registers = (persons, orgs, places)
    register_counts = {
        "persons": len(persons),
        "orgs": len(orgs),
        "places": len(places),
    }

    env = _init_jinja()

    all_files = collect_source_files()
    done_files = [f for f in all_files if _is_done_file(f) and _is_released_file(f)]
    print(f"Found {len(done_files)} documents to render (released corpora only).")

    parsed = []
    t1 = time.time()
    for i, filepath in enumerate(done_files, 1):
        result = _parse_file(filepath, registers)
        if result:
            parsed.append(result)
        if i % 100 == 0 or i == len(done_files):
            elapsed = time.time() - t1
            rate = i / elapsed if elapsed > 0 else 0
            print(f"  Parsed [{i}/{len(done_files)}] {rate:.0f} docs/s")

    all_metadata = [p[0] for p in parsed]
    _compute_prev_next(all_metadata)

    print("Building reverse index...")
    reverse_index = {}
    for meta, _body, _out, entity_refs in parsed:
        doc_entry = {
            "url": meta["url"],
            "idno": meta["idno"],
            "date_display": meta["date_display"],
            "date_iso": meta["date_iso"],
            "collection_label": meta["collection_label"],
            "collection_path": meta.get("collection_path", ""),
            "regest": meta["regest"],
        }
        for eid in entity_refs:
            reverse_index.setdefault(eid, []).append(doc_entry)
    for docs in reverse_index.values():
        docs.sort(key=lambda d: d.get("date_iso", ""))
    print(f"  Reverse index: {len(reverse_index)} entities linked to documents")

    from frontend.aggregator import run_aggregation, build_docs_lookup
    run_aggregation(DATA_DIR, reverse_index)
    build_docs_lookup(DATA_DIR, all_metadata)

    docs_out_dir = DOCS_DIR / "documents"
    if docs_out_dir.exists():
        shutil.rmtree(docs_out_dir)
    t2 = time.time()
    for i, (meta, body_html, output, _refs) in enumerate(parsed, 1):
        _write_file(meta, body_html, output, env)
        if i % 500 == 0 or i == len(parsed):
            print(f"  Written [{i}/{len(parsed)}]")

    print(f"  Render pass: {time.time() - t2:.1f}s")

    _build_index(all_metadata, env, register_counts)

    collections_start = {}
    for m in all_metadata:
        path_key = m.get("collection_path", "")
        if path_key not in collections_start:
            collections_start[path_key] = {
                "count": 0,
                "label": m.get("collection_label", path_key),
                "path": path_key,
            }
        collections_start[path_key]["count"] += 1
    _build_startseite(all_metadata, persons, orgs, places, collections_start, env)

    _build_register_list_pages(persons, orgs, places, reverse_index, env)
    _build_register_json(reverse_index)
    _build_person_profiles(reverse_index, env)

    _build_exploration(all_metadata, persons, env)

    _build_guidelines(env)
    _build_about(env)
    _build_impressum(env)

    _build_glossary(env)
    _write_categories()
    _write_query_vocabulary()
    _build_analysis(env)

    _copy_static()
    _copy_tei_sources()

    (DOCS_DIR / ".nojekyll").touch()

    elapsed = time.time() - t0
    print(f"Build complete: {len(all_metadata)} documents in {elapsed:.1f}s")
    print(f"Output: {DOCS_DIR}")


__all__ = [
    "build_single",
    "build_all",
    # Constants commonly imported by tests
    "DOCS_DIR", "TEMPLATES_DIR", "STATIC_DIR", "CONTENT_DIR", "KNOWLEDGE_DIR",
    "DATA_DIR", "FACSIMILE_BASE_URLS",
    "EDITION_GUIDELINES_PATH",
    "RELEASED_PERIOD", "RELEASED_CORPORA",
    "COLLECTION_LABELS",
    # Helpers
    "_format_german_date", "_pipeline_repo_data_date",
    "_create_markdown_processor", "_collection_label",
    "_xpath_text", "_extract_regest", "_extract_entity_refs",
    "_init_jinja", "_normalize_facsimile_url",
    "_output_path", "_relative_to_root",
    "_is_done_file", "_is_released_file",
    "_tei_output_path", "_load_registers",
    "_sort_key_for_nav", "_compute_prev_next",
    "_format_table_date", "_load_docs_aggregate_lookup",
    "_copy_static", "_copy_tei_sources",
    # Metadata
    "_extract_metadata", "_parse_file", "_write_file",
    # KPI
    "_TEI_NS", "_XP_TOP_EVENTS", "_XP_PERSONS_EXCL_MENTIONED", "_XP_PERSONS_ALL",
    "_scan_released_tei", "_compute_corpus_breakdown", "_compute_release_kpis",
    "_compute_matrix_columns", "_released_person_keys",
    "_persons_with_org_released",
    # Pages
    "_build_index", "_build_startseite",
    "_person_search_data", "_org_search_data", "_place_search_data",
    "_build_register_list_pages", "_build_register_json",
    "_build_person_profiles",
    "_build_exploration",
    "_build_guidelines", "_build_about", "_build_glossary", "_build_impressum",
    "_write_categories", "_write_query_vocabulary", "_build_analysis",
]
