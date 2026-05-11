"""Aggregator package: build-time aggregation of pipeline CSVs to docs/data/.

The aggregator runs once per build (called from frontend/build.py) and
produces the JSON files that the client-side visualisations read.

Submodule layout:
- _shared.py — CSV cache, RELEASED_CORPORA filter, common helpers
- timeline.py — aggregate_timeline (timeline.json)
- roles.py — aggregate_roles (roles.json: function roles)
- relations.py — aggregate_relations (relations.json: person relationships)
- transactions.py — aggregate_transactions (transactions.json: legal transactions)
- docs.py — aggregate_docs (docs_aggregate.json) + build_docs_lookup
- _run.py — run_aggregation orchestrator

Public API re-exported here for `from frontend.aggregator import ...`
callers (build.py + tests).
"""

from ._shared import (
    SCHEMA_VERSION,
    _cached_csv,
    _decade,
    _is_released_row,
    _load_csv,
    _load_norm_matching,
    _meta,
    _parse_coord,
    _released_file_keys,
    _write_json,
)
from .timeline import aggregate_timeline
from .roles import aggregate_roles
from .relations import aggregate_relations
from .transactions import aggregate_transactions
from .docs import _parse_date_range, aggregate_docs, build_docs_lookup
from .person_profiles import build_person_profiles
from .org_profiles import build_org_profiles
from .place_profiles import build_place_profiles
from ._run import run_aggregation

__all__ = [
    "SCHEMA_VERSION",
    "_cached_csv",
    "_decade",
    "_is_released_row",
    "_load_csv",
    "_load_norm_matching",
    "_meta",
    "_parse_coord",
    "_parse_date_range",
    "_released_file_keys",
    "_write_json",
    "aggregate_docs",
    "aggregate_relations",
    "aggregate_roles",
    "aggregate_timeline",
    "aggregate_transactions",
    "build_docs_lookup",
    "build_person_profiles",
    "build_org_profiles",
    "build_place_profiles",
    "run_aggregation",
]
