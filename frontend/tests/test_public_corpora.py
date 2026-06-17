"""Regression test: Datums-Span in Org- and Person-Profilen darf
nur Jahre aus den oeffentlich sichtbaren Public-Korpora ziehen
(seit Frontend-Meeting 2026-06-17 nur QGW/Vienna_1177-1414_ready;
Stadtbuecher Bd. 1 wurde aus PUBLIC_CORPORA genommen).
Stakeholder decision: Protokoll 18.05.2026, angepasst 2026-06-17.
"""

import re
from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"
DATUM_PATTERN = re.compile(
    r"Datum der Quelle.*?<dd>\s*(\d{4})(?:\s*bis\s*(\d{4}))?\s*</dd>",
    re.DOTALL,
)


def _date_span(rel_path: str):
    path = DOCS_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    text = path.read_text(encoding="utf-8")
    m = DATUM_PATTERN.search(text)
    if not m:
        pytest.skip(f"no Datum-Block found in {rel_path}")
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    return start, end


@pytest.mark.parametrize("rel_path,max_allowed", [
    ("register/orgs/org__wien-st_stephan.html", 1414),
    ("register/orgs/org__kufstein-burg.html", 1414),
])
def test_org_datums_span_within_public_corpora(rel_path, max_allowed):
    start, end = _date_span(rel_path)
    assert end <= max_allowed, (
        f"Datums-Span in {rel_path}: {start} bis {end}, "
        f"darf aber maximal bis {max_allowed} (QGW bis 1414, StB Bd. 1)."
    )
    assert start >= 1177, (
        f"Datums-Span in {rel_path}: {start} bis {end}, "
        f"darf aber fruehestens 1177 beginnen."
    )
