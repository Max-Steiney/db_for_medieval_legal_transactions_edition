"""Aggregator package: build-time aggregation of pipeline CSVs to docs/data/.

The aggregator runs once per build (called from frontend/build.py) and
produces the JSON files that the client-side visualisations read.

Submodule layout:
- _shared.py — CSV cache, RELEASED_CORPORA filter, common helpers
- timeline.py — aggregate_timeline (timeline.json)
- epic_a.py — aggregate_epic_a (epic_a.json: roles)
- epic_b.py — aggregate_epic_b (epic_b.json: relationships)
- epic_c.py — aggregate_epic_c (epic_c.json: transactions)
- docs.py — aggregate_docs (docs_aggregate.json) + build_docs_lookup
- _run.py — run_aggregation orchestrator

Public API re-exported here for backwards compatibility with previous
`from frontend.aggregator import ...` callers (build.py + tests).
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
from .epic_a import aggregate_epic_a
from .epic_b import aggregate_epic_b
from .epic_c import aggregate_epic_c
from .docs import _parse_date_range, aggregate_docs, build_docs_lookup
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
    "aggregate_epic_a",
    "aggregate_epic_b",
    "aggregate_epic_c",
    "aggregate_timeline",
    "build_docs_lookup",
    "run_aggregation",
]
