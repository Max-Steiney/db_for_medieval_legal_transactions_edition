"""Orchestrator: laeuft alle Aggregationen und schreibt JSONs nach docs/data/."""

from pathlib import Path

from . import _shared
from .timeline import aggregate_timeline
from .epic_a import aggregate_epic_a
from .epic_b import aggregate_epic_b
from .epic_c import aggregate_epic_c
from .docs import aggregate_docs


def run_aggregation(docs_data_dir: Path, reverse_index: dict | None = None) -> dict:
    """Run all aggregations and write JSON files to docs/data/.

    Called from frontend/build.py after register loading.
    Returns a summary dict with stats from each aggregation.
    """
    print("Running data aggregation for visualisations...")
    docs_data_dir.mkdir(parents=True, exist_ok=True)

    # Reset shared caches for a fresh run (relevant in tests where
    # run_aggregation is called multiple times in different tmp_paths).
    _shared._csv_cache.clear()
    _shared._released_file_keys_cache = None

    timeline = aggregate_timeline(docs_data_dir)
    print(f"  Timeline: {timeline['total']} documents, "
          f"{timeline['placeholder_count']} placeholders")

    epic_a = aggregate_epic_a(docs_data_dir)
    print(f"  Epic A: {epic_a['coverage']['person_count']} persons, "
          f"{epic_a['coverage']['total_events']} events")

    epic_b = aggregate_epic_b(docs_data_dir)
    print(f"  Epic B: {epic_b['coverage']['persons_with_relations']} persons, "
          f"{epic_b['coverage']['total_relations']} relations, "
          f"{epic_b['coverage']['unique_labels']} labels")

    epic_c = aggregate_epic_c(docs_data_dir)
    print(f"  Epic C: {epic_c['coverage']['unique_verb_forms']} verb forms, "
          f"{epic_c['coverage']['recipient_orgs']} recipients")

    docs_agg = aggregate_docs(docs_data_dir)
    print(f"  Docs aggregate: {docs_agg['total']} sources, "
          f"{docs_agg['with_persons']} with at least one register-linked person")

    return {
        "timeline": {"total": timeline["total"]},
        "epic_a": {"persons": epic_a["coverage"]["person_count"]},
        "epic_b": epic_b["coverage"],
        "epic_c": {"verb_forms": epic_c["coverage"]["unique_verb_forms"]},
        "docs_aggregate": docs_agg,
    }
