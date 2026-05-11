"""Aggregationen aus TEI + Register — unabhängig von der Build-Pipeline.

Jede Funktion liefert ein einfaches Python-Dict oder int/tuple. compare.py
legt diese Ergebnisse gegen die JSON-Aggregate aus dem Build.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

from verification.parse_indices import OrgRecord, PersonRecord, PlaceRecord
from verification.parse_tei import DocRecord


def docs_total(docs: List[DocRecord]) -> int:
    return len(docs)


def docs_by_collection(docs: List[DocRecord]) -> Dict[str, int]:
    c: Counter = Counter()
    for d in docs:
        c[d.collection] += 1
    return dict(c)


def docs_by_decade(docs: List[DocRecord]) -> Dict[int, int]:
    """Dokumente pro Dekade. Dokumente mit ungültigem Datum werden gezählt unter None."""
    c: Counter = Counter()
    for d in docs:
        c[d.decade] += 1
    return {k: v for k, v in c.items() if k is not None}


def docs_date_range(docs: List[DocRecord]) -> Dict[str, Dict[str, Optional[str]]]:
    """Min/max Datum pro Quellenkorpus, ignoriert offensichtlich fehlerhafte Daten."""
    out: Dict[str, Dict[str, Optional[str]]] = {}
    for d in docs:
        if not d.date_iso or d.date_iso.startswith("9999"):
            continue
        if d.collection not in out:
            out[d.collection] = {"min_date": d.date_iso, "max_date": d.date_iso}
        else:
            if d.date_iso < out[d.collection]["min_date"]:
                out[d.collection]["min_date"] = d.date_iso
            if d.date_iso > out[d.collection]["max_date"]:
                out[d.collection]["max_date"] = d.date_iso
    return out


def persons_total(persons: Dict[str, PersonRecord]) -> int:
    return len(persons)


def persons_by_sex(persons: Dict[str, PersonRecord]) -> Dict[str, int]:
    c: Counter = Counter()
    for p in persons.values():
        c[p.sex or "unknown"] += 1
    return dict(c)


def orgs_total(orgs: Dict[str, OrgRecord]) -> int:
    return len(orgs)


def places_total(places: Dict[str, PlaceRecord]) -> int:
    return len(places)


def person_mentions_total(docs: List[DocRecord]) -> int:
    """Summe aller Personen-Nennungen über alle Dokumente (nicht pro Doc dedupliziert)."""
    return sum(len(d.person_roles) for d in docs)


def person_mentions_unique_per_doc(docs: List[DocRecord]) -> int:
    """Summe der pro Dokument dedupliziterten Personen-Nennungen."""
    return sum(len(d.person_refs) for d in docs)


def events_total(docs: List[DocRecord]) -> int:
    """Pro Dokument werden Events nach ref dedupliziert (ein Event kann mehrfach erscheinen)."""
    return sum(len(d.events) for d in docs)


def roles_by_role(docs: List[DocRecord]) -> Dict[str, int]:
    """Zählt (person_ref, role)-Paare. Nennungen ohne Rolle unter 'none'."""
    c: Counter = Counter()
    for d in docs:
        for _ref, role in d.person_roles:
            c[role or "none"] += 1
    return dict(c)


def roles_by_role_sex(
    docs: List[DocRecord], persons: Dict[str, PersonRecord]
) -> Dict[str, Dict[str, int]]:
    """Rolle × Geschlecht. Geschlecht aus Register, Nennungen ohne Rolle unter 'none'."""
    out: Dict[str, Counter] = {}
    for d in docs:
        for ref, role in d.person_roles:
            rec = persons.get(ref)
            sex = (rec.sex if rec else None) or "unknown"
            role_key = role or "none"
            out.setdefault(role_key, Counter())[sex] += 1
    return {role: dict(c) for role, c in out.items()}


def relations_by_type(docs: List[DocRecord]) -> Dict[str, int]:
    c: Counter = Counter()
    for d in docs:
        for rtype, _src, _tgt in d.relations:
            c[rtype] += 1
    return dict(c)


def disp_triggers(docs: List[DocRecord]) -> Dict[str, int]:
    """Zählt Roh-Text der disp-Trigger ohne Normalisierung. Für transactions-Vergleich."""
    c: Counter = Counter()
    for d in docs:
        for text in d.disp_triggers:
            c[text] += 1
    return dict(c)
