"""Lokaler Demo-Build ohne Pipeline-CSVs.

Legt den _MS_Test-Pipeline-Fork (read-only) auf sys.path, damit
`from pipeline.config import ...` aufloest, und baut nur die drei
Glossar-Demo-Seiten. frontend/__init__.py bleibt unveraendert.

Aufruf:  python3 scripts/build_glossar_demo.py
"""

import shutil  # noqa: E402  (oben zu den Imports ziehen)
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MS_TEST = _REPO.parent / "db_for_medieval_legal_transactions_MS_Test"
if not (_MS_TEST / "pipeline").is_dir():
    raise SystemExit(f"pipeline-Fork nicht gefunden unter {_MS_TEST}")
sys.path.insert(0, str(_MS_TEST))
sys.path.insert(0, str(_REPO))

from frontend.build import _build_glossar_demo, _init_jinja  # noqa: E402

env = _init_jinja()
_build_glossar_demo(env)

_css_src = _REPO / "frontend" / "static" / "css" / "glossar-demo.css"
_css_dst = _REPO / "docs" / "static" / "css" / "glossar-demo.css"
_css_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(str(_css_src), str(_css_dst))

print("OK: docs/project/glossar-demo/ gebaut")
