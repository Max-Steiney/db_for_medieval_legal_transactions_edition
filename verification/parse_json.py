"""Lesen der bestehenden JSON-Aggregate aus `/data/`.

Extrahiert aus jedem Aggregat-JSON die für compare.py relevanten
Kennzahlen in Python-Dicts. Struktur folgt den Feldnamen, die auch
`verification/inventory.md` verwendet.
"""

from __future__ import annotations

import json
from typing import Dict

from verification.config import DATA_DIR


def _load(name: str):
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_optional(name: str):
    """Wie _load, aber gibt None zurueck, wenn die Datei fehlt.

    Notwendig, weil Organisationen und Orte aktuell nicht freigegeben sind
    und entsprechend keine Such-JSONs gebaut werden. Verifikation muss
    sauber durchlaufen, ohne darueber zu stolpern.
    """
    path = DATA_DIR / name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def persons_search_count() -> int:
    return len(_load("persons_search.json"))


def organisations_search_count() -> int:
    data = _load_optional("organisations_search.json")
    return len(data) if data is not None else None


def places_search_count() -> int:
    data = _load_optional("places_search.json")
    return len(data) if data is not None else None


def persons_search_by_sex() -> Dict[str, int]:
    from collections import Counter
    c: Counter = Counter()
    for entry in _load("persons_search.json"):
        c[entry.get("sex") or "unknown"] += 1
    return dict(c)


def timeline() -> dict:
    return _load("timeline.json")


def timeline_by_collection() -> Dict[str, int]:
    t = timeline()
    return {k: v.get("count", 0) for k, v in t.get("collections", {}).items()}


def timeline_total() -> int:
    return int(timeline().get("total", 0))


def timeline_date_range() -> Dict[str, Dict[str, str]]:
    t = timeline()
    return {
        k: {"min_date": v.get("min_date"), "max_date": v.get("max_date")}
        for k, v in t.get("collections", {}).items()
    }


def timeline_by_decade() -> Dict[int, int]:
    t = timeline()
    decades = t.get("decades", {})
    out: Dict[int, int] = {}
    for k, v in decades.items():
        try:
            decade = int(k)
        except (TypeError, ValueError):
            continue
        if isinstance(v, dict):
            out[decade] = int(v.get("total", 0))
        else:
            out[decade] = int(v or 0)
    return out


def roles_role_by_sex() -> Dict[str, Dict[str, int]]:
    data = _load("roles.json")
    obs = data.get("observations", {})
    rbs = obs.get("role_by_sex", {})
    return {role: {sex: int(n) for sex, n in sexd.items()} for role, sexd in rbs.items()}


def roles_total_events() -> int:
    data = _load("roles.json")
    return int(data.get("coverage", {}).get("total_events", 0))


def relations_by_type() -> Dict[str, Dict[str, int]]:
    """Beziehungen pro Typ × Geschlecht aus relations.json#overview.type_by_sex."""
    data = _load("relations.json")
    bt = data.get("overview", {}).get("type_by_sex", {})
    return {t: {sex: int(n) for sex, n in sexd.items()} for t, sexd in bt.items()}


def relations_type_totals() -> Dict[str, int]:
    """Beziehungen pro Typ, summiert über Geschlechter."""
    return {t: sum(sexd.values()) for t, sexd in relations_by_type().items()}
