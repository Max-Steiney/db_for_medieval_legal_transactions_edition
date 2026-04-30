"""Frontend builder for the medieval Viennese legal transactions edition.

This package consumes the data infrastructure provided by the sibling
repository `db_for_medieval_legal_transactions` (TEI sources + Python
pipeline that produces CSV exports). Both repositories must be cloned
side-by-side; the bootstrap below puts the sibling on `sys.path` so
`from pipeline.config import ...` resolves transparently — no install
step, no submodule.

Repository layout convention:
    parent/
      db_for_medieval_legal_transactions/         ← sources, indices, pipeline
      db_for_medieval_legal_transactions_edition/ ← this repo (frontend + Pages output)
"""

import sys
from pathlib import Path

_PIPELINE_REPO = (
    Path(__file__).resolve().parent.parent.parent
    / "db_for_medieval_legal_transactions"
)
if not _PIPELINE_REPO.is_dir():
    raise RuntimeError(
        f"Sibling pipeline repository not found at {_PIPELINE_REPO}. "
        "Clone db_for_medieval_legal_transactions next to this repository."
    )
if str(_PIPELINE_REPO) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_REPO))
