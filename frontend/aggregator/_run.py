"""Orchestrator: runs all aggregations and writes JSONs to docs/data/."""

from pathlib import Path

from . import _shared
from .timeline import aggregate_timeline
from .roles import aggregate_roles
from .relations import aggregate_relations
from .transactions import aggregate_transactions
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

    roles = aggregate_roles(docs_data_dir)
    print(f"  Roles: {roles['coverage']['person_count']} persons, "
          f"{roles['coverage']['total_events']} events")

    relations = aggregate_relations(docs_data_dir)
    print(f"  Relations: {relations['coverage']['persons_with_relations']} persons, "
          f"{relations['coverage']['total_relations']} relations, "
          f"{relations['coverage']['unique_labels']} labels")

    transactions = aggregate_transactions(docs_data_dir)
    print(f"  Transactions: {transactions['coverage']['unique_verb_forms']} verb forms, "
          f"{transactions['coverage']['recipient_orgs']} recipients")

    docs_agg = aggregate_docs(docs_data_dir)
    print(f"  Docs aggregate: {docs_agg['total']} sources, "
          f"{docs_agg['with_persons']} with at least one register-linked person")

    return {
        "timeline": {"total": timeline["total"]},
        "roles": {"persons": roles["coverage"]["person_count"]},
        "relations": relations["coverage"],
        "transactions": {"verb_forms": transactions["coverage"]["unique_verb_forms"]},
        "docs_aggregate": docs_agg,
    }
