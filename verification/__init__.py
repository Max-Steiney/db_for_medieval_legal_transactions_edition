"""Verifikations-Test-Set fuer die Edition.

Liest TEI-Quellen und Register-XMLs aus dem Schwester-Repo
`db_for_medieval_legal_transactions` direkt ein, rechnet Aggregate
nachvollziehbar nach und vergleicht sie mit den JSON-Outputs im eigenen
`docs/data/`. Die Trennung schuetzt davor, dass Pipeline-Fehler durch
ihre eigene Aggregations-Logik validiert werden.

Der sys.path-Bootstrap unten erlaubt `from pipeline.config import ...`
fuer den RELEASED_CORPORA-Filter, identisch zum Pattern in
`frontend/__init__.py`.
"""

import sys
from pathlib import Path

_PIPELINE_REPO = (
    Path(__file__).resolve().parent.parent.parent
    / "db_for_medieval_legal_transactions"
)
if _PIPELINE_REPO.is_dir() and str(_PIPELINE_REPO) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_REPO))
