"""Vergleich Test-Aggregate vs. JSON-Aggregate.

Ruft die einzelnen Aggregations-Funktionen aus `aggregate.py`, liest die
Pendants aus `parse_json.py` und erzeugt eine Liste von Vergleichs-
Ergebnissen. Ein Ergebnis besteht aus Name, erwartetem Wert (TEI),
beobachtetem Wert (JSON), Status und optionaler Notiz.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from tests import aggregate, parse_indices, parse_json, parse_tei


@dataclass
class CheckResult:
    name: str
    tei: Any
    json: Any
    status: str  # "match" | "mismatch" | "info"
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tei": _jsonable(self.tei),
            "json": _jsonable(self.json),
            "status": self.status,
            "note": self.note,
        }


def _jsonable(value: Any) -> Any:
    """Dicts mit int-Keys sind in JSON nicht erlaubt — als Strings speichern."""
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _check_equal(name: str, tei_value: Any, json_value: Any, note: Optional[str] = None) -> CheckResult:
    status = "match" if tei_value == json_value else "mismatch"
    return CheckResult(name=name, tei=tei_value, json=json_value, status=status, note=note)


def run_checks(
    docs: List[parse_tei.DocRecord],
    persons: Dict[str, parse_indices.PersonRecord],
    orgs: Dict[str, parse_indices.OrgRecord],
    places: Dict[str, parse_indices.PlaceRecord],
) -> List[CheckResult]:
    results: List[CheckResult] = []

    # --- Dokumente / Timeline ---------------------------------------------
    results.append(
        _check_equal(
            "docs.total",
            aggregate.docs_total(docs),
            parse_json.timeline_total(),
            note="TEI zählt nur Dokumente mit TEI-Datei in sources/; Timeline-JSON stützt sich auf filenames.csv und enthält auch Einträge ohne TEI (z. B. Vienna_1448-57_ready).",
        )
    )
    results.append(
        _check_equal(
            "docs.by_collection",
            aggregate.docs_by_collection(docs),
            parse_json.timeline_by_collection(),
        )
    )

    tei_range = aggregate.docs_date_range(docs)
    json_range = parse_json.timeline_date_range()
    for collection in sorted(set(tei_range.keys()) | set(json_range.keys())):
        results.append(
            _check_equal(
                f"docs.date_range.{collection}",
                tei_range.get(collection),
                json_range.get(collection),
            )
        )

    # --- Register ----------------------------------------------------------
    results.append(
        _check_equal(
            "persons.total_individual",
            aggregate.persons_total(persons),
            parse_json.persons_search_count(),
            note="Individuelle Personen im Register personList.xml vs. Länge persons_search.json.",
        )
    )
    results.append(
        _check_equal(
            "persons.by_sex",
            aggregate.persons_by_sex(persons),
            parse_json.persons_search_by_sex(),
        )
    )
    results.append(
        _check_equal(
            "orgs.total_individual",
            aggregate.orgs_total(orgs),
            parse_json.organisations_search_count(),
        )
    )
    results.append(
        _check_equal(
            "places.total_individual",
            aggregate.places_total(places),
            parse_json.places_search_count(),
        )
    )

    # --- Events + Rollen ---------------------------------------------------
    results.append(
        CheckResult(
            name="events.total",
            tei=aggregate.events_total(docs),
            json=parse_json.epic_a_total_events(),
            status="info",
            note="epic_a.coverage.total_events zählt Event-Nennungen (nicht dedupliziert); TEI-Zählung dedupliziert pro Dokument nach Event-Ref. Kein direkter Match zu erwarten.",
        )
    )

    tei_roles = aggregate.roles_by_role(docs)
    results.append(
        CheckResult(
            name="roles.by_role",
            tei=tei_roles,
            json=None,
            status="info",
            note="Rollen-Counter aus TEI; kein direktes Pendant in JSON (nur role_by_sex).",
        )
    )

    tei_role_sex = aggregate.roles_by_role_sex(docs, persons)
    json_role_sex = parse_json.epic_a_role_by_sex()
    # Role-Keys normalisieren: JSON '' entspricht TEI 'none'.
    # Pseudo-Rollen aus TEI-Annotationsfehlern (transactiongood_*) als 'info' markieren.
    normalized_json = {}
    for role, sexd in json_role_sex.items():
        key = "none" if role == "" else role
        normalized_json[key] = sexd

    all_roles = sorted(set(tei_role_sex.keys()) | set(normalized_json.keys()))
    for role in all_roles:
        tei_val = tei_role_sex.get(role)
        json_val = normalized_json.get(role)
        name = f"roles.by_role_sex.{role}"
        if role.startswith("transactiongood"):
            results.append(
                CheckResult(
                    name=name,
                    tei=tei_val,
                    json=json_val,
                    status="info",
                    note="Pseudo-Rolle aus TEI-Annotationsfehlern; kein echter Rollen-Wert.",
                )
            )
        else:
            results.append(_check_equal(name, tei_val, json_val))

    # --- Beziehungen -------------------------------------------------------
    results.append(
        _check_equal(
            "relations.by_type",
            aggregate.relations_by_type(docs),
            parse_json.epic_b_type_totals(),
            note="TEI zählt alle <roleName type=X corresp=Y> Einträge; epic_b aggregiert nach Typ über Geschlechter-Summe.",
        )
    )

    # --- Transaktionsverben (Rohtext) --------------------------------------
    tei_disp = aggregate.disp_triggers(docs)
    results.append(
        CheckResult(
            name="transactions.disp_top",
            tei=dict(sorted(tei_disp.items(), key=lambda kv: -kv[1])[:20]),
            json=None,
            status="info",
            note="Top-20 Roh-Trigger für disp; Vergleich mit normalisierten Transaktionstypen in epic_c noch offen.",
        )
    )

    return results
