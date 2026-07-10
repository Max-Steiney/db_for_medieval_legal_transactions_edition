"""Lokaler Demo-Build ohne Pipeline-CSVs.

Baut nur die Glossar-Demo-Seiten. `from pipeline.config import ...` loest
ueber die Schwester-Repo-Verdrahtung in frontend/__init__.py auf.

Aufruf:  python scripts/build_glossar_demo.py
"""

import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

from frontend.build import _build_glossar_demo, _init_jinja  # noqa: E402

env = _init_jinja()
_build_glossar_demo(env)

_css_src = _REPO / "frontend" / "static" / "css" / "glossar-demo.css"
_css_dst = _REPO / "docs" / "static" / "css" / "glossar-demo.css"
_css_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(str(_css_src), str(_css_dst))

print("OK: docs/project/glossar-demo/ gebaut")
