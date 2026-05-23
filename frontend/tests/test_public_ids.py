"""Regression test: pe__, org__, ev__ IDs must not appear in the
visible layer of the public build. Visible layer means text nodes
and the attributes that surface to users (title, aria-label,
data-hint, alt, placeholder). IDs may live in any other attribute
(href, data-ref, data-corresp, id, data-basket-*, ...).

Stakeholder decision: Protokoll 18.05.2026 A.3.2.
"""

import re
from pathlib import Path

import pytest
from lxml import html as lxml_html

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

ID_PATTERN = re.compile(r"(?:pe__|org__|ev__)[\w-]+")
VISIBLE_ATTRS = ("title", "aria-label", "data-hint", "alt", "placeholder")

SAMPLE_FILES = [
    "register/orgs/org__kufstein-burg.html",
    "register/orgs/org__wien-st_stephan.html",
    "register/persons.html",
    "register/orgs.html",
    "documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html",
    "documents/QGW/Vienna_1177-1414_ready/100.html",
    "documents/QGW/Vienna_1177-1414_ready/1022.html",
]


def _visible_ids(html_text: str) -> list[str]:
    tree = lxml_html.fromstring(html_text)
    matches = ID_PATTERN.findall(tree.text_content() or "")
    for attr in VISIBLE_ATTRS:
        for el in tree.xpath(f"//*[@{attr}]"):
            matches.extend(ID_PATTERN.findall(el.get(attr) or ""))
    return matches


@pytest.mark.parametrize("rel_path", SAMPLE_FILES)
def test_no_visible_ids_in_sample(rel_path):
    path = DOCS_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"build artifact not found: {rel_path}")
    matches = _visible_ids(path.read_text(encoding="utf-8"))
    assert not matches, (
        f"Visible technical IDs in {rel_path} (first 5): {matches[:5]}. "
        "IDs are forbidden in text nodes and in title/aria-label/data-hint/alt/placeholder."
    )
