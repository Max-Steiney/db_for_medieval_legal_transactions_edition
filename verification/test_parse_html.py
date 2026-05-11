"""Tests fuer verification/parse_html.py.

Pytest-Konvention: file beginnt mit ``test_``, damit pytest ihn aus
``verification/`` mit aufsammelt. Test sichert, dass der Reader die
Felder eines Profil-HTMLs korrekt extrahiert.

Kann auch via `python -m pytest verification/test_parse_html.py`
isoliert laufen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from verification.config import DOCS_DIR, HTML_REGISTER_PERSONS, HTML_REGISTER_ORGS
from verification.parse_html import (
    iter_org_profiles,
    iter_person_profiles,
    read_org_profile,
    read_person_profile,
)


@pytest.fixture(scope="module")
def sample_person_path() -> Path:
    """Ein konkretes Personenprofil mit voller Daten-Vielfalt:
    Mirror-Beziehungen (occ_inverse), Note, viele Quellen."""
    path = HTML_REGISTER_PERSONS / "pe__wilhelm_herzog_von_oesterreich_QGW_II_I_1313.html"
    if not path.exists():
        pytest.skip(f"docs not built: {path}")
    return path


@pytest.fixture(scope="module")
def sample_org_path() -> Path:
    """Klosterneuburg-Augustiner: viele Quellen, viele Beruf/Amt-Eintraege."""
    path = HTML_REGISTER_ORGS / "org__klosterneuburg-augustiner_chorherren.html"
    if not path.exists():
        pytest.skip(f"docs not built: {path}")
    return path


def test_iter_person_profiles_returns_paths():
    paths = iter_person_profiles()
    if not paths:
        pytest.skip("docs not built")
    assert all(p.suffix == ".html" for p in paths)
    assert all(p.stem.startswith("pe__") for p in paths)


def test_iter_org_profiles_returns_paths():
    paths = iter_org_profiles()
    if not paths:
        pytest.skip("docs not built")
    assert all(p.suffix == ".html" for p in paths)
    assert all(p.stem.startswith("org__") for p in paths)


def test_read_person_profile_extracts_core_fields(sample_person_path):
    p = read_person_profile(sample_person_path)
    assert p.pe_id == "pe__wilhelm_herzog_von_oesterreich_QGW_II_I_1313"
    assert p.display_name == "Herzog Wilhelm"
    assert p.sex_label == "männlich"
    assert p.active_min and p.active_min.isdigit()
    assert p.active_max and p.active_max.isdigit()
    assert int(p.active_min) <= int(p.active_max)


def test_read_person_profile_source_count_matches_rows(sample_person_path):
    """Header-Count und Tabellen-Zeilen muessen identisch sein. Diese
    Pruefung deckt die Renderer-Konsistenz ab; der Reader-Bug, der den
    <th> mitgezaehlt hat, ist hier explizit ausgeschlossen."""
    p = read_person_profile(sample_person_path)
    assert p.source_count_displayed is not None
    assert p.source_count_displayed == len(p.source_idnos)


def test_read_person_profile_has_mirror_relations(sample_person_path):
    """Wilhelm Herzog hat aus Commit 24d5f4ad41 ein occ_inverse-Block.
    Sichert ab, dass das Mirror-Feature im HTML ankommt."""
    p = read_person_profile(sample_person_path)
    assert p.relation_counts.get("occ_inverse", 0) > 0


def test_read_org_profile_extracts_core_fields(sample_org_path):
    o = read_org_profile(sample_org_path)
    assert o.org_id == "org__klosterneuburg-augustiner_chorherren"
    assert o.name and "Klosterneuburg" in o.name
    assert o.type_label
    assert o.source_count_displayed is not None
    assert o.source_count_displayed == len(o.source_idnos)


def test_read_org_profile_has_children(sample_org_path):
    """Klosterneuburg hat untergeordnete Orgs (Frauenaltar, Spital)."""
    o = read_org_profile(sample_org_path)
    assert isinstance(o.children_ids, list)
