"""Epic A: Rollen x Geschlecht x Organisationen — fuer die Rollen-Sektion
in analysis/auswertungen.html."""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import _cached_csv, _load_norm_matching, _meta, _decade, _write_json


def aggregate_epic_a(docs_data_dir: Path) -> dict:
    """Aggregate role distribution by sex, time series, and institution links."""
    persons_rows = _cached_csv("persons.csv")
    pie_rows = _cached_csv("persons_in_events.csv")
    eis_rows = _cached_csv("events_in_sources.csv")
    orgs_rows = _cached_csv("organisations.csv")
    oie_rows = _cached_csv("orgs_in_events.csv")
    norm_map = _load_norm_matching()

    # Build lookup dicts
    person_sex = {r["id"]: r.get("sex", "") for r in persons_rows}
    event_info = {}
    for r in eis_rows:
        ek = r.get("event_key", "")
        event_info[ek] = {
            "date": r.get("date_not_before", ""),
            "catchwords": r.get("catchwords", ""),
            "file_key": r.get("file_key", ""),
        }
    org_type = {r["id"]: r.get("type", "") for r in orgs_rows}

    # Build event -> org types lookup
    event_orgs: dict[str, set] = defaultdict(set)
    for r in oie_rows:
        ek = r.get("event_key", "")
        ok = r.get("org_key", "")
        otype = org_type.get(ok, "")
        if otype:
            event_orgs[ek].add(otype)

    # Role x sex totals and time series
    role_sex: dict[str, Counter] = defaultdict(Counter)
    role_sex_decade: dict[str, dict[int, Counter]] = \
        defaultdict(lambda: defaultdict(Counter))
    person_org_types: dict[str, set] = defaultdict(set)

    # Drill-down: file_keys per (role, sex) for document-level traceability
    role_sex_files: dict[str, dict[str, set]] = \
        defaultdict(lambda: defaultdict(set))

    # Distinct persons per role x sex (individual count, not mention count)
    role_sex_persons: dict[str, dict[str, set]] = \
        defaultdict(lambda: defaultdict(set))
    # Distinct persons per role x sex x decade (for time-filtered individual counts)
    role_sex_decade_persons: dict[str, dict[int, dict[str, set]]] = \
        defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

    for r in pie_rows:
        pk = r.get("person_key", "")
        role = r.get("event_role", "other")
        ek = r.get("event_key", "")
        sex = person_sex.get(pk, "")
        if sex not in ("m", "f"):
            sex = "unspecified"

        role_sex[role][sex] += 1
        if pk:
            role_sex_persons[role][sex].add(pk)

        ei = event_info.get(ek, {})
        fk = ei.get("file_key", "")
        dec = _decade(ei.get("date", ""))
        if dec is not None:
            role_sex_decade[role][dec][sex] += 1
            if pk:
                role_sex_decade_persons[role][dec][sex].add(pk)

        # Collect file_keys for drill-down
        if fk:
            role_sex_files[role][sex].add(fk)

        for ot in event_orgs.get(ek, set()):
            person_org_types[pk].add(ot)

    # Org-type frequency: how many events per org type (for Panel 2)
    org_type_events: dict[str, Counter] = defaultdict(Counter)
    org_type_files: dict[str, set] = defaultdict(set)
    for r in oie_rows:
        ek = r.get("event_key", "")
        ok = r.get("org_key", "")
        otype = org_type.get(ok, "")
        if not otype:
            continue
        fk = event_info.get(ek, {}).get("file_key", "")
        dec = _decade(event_info.get(ek, {}).get("date", ""))
        if dec is not None:
            org_type_events[otype][str(dec)] += 1
        if fk:
            org_type_files[otype].add(fk)

    # Org-type totals (all decades)
    org_type_totals = {
        ot: sum(decades.values()) for ot, decades in org_type_events.items()
    }

    # Person -> org types (how many persons have contact with each org type)
    person_org_sex: dict[str, Counter] = defaultdict(Counter)
    for pk, org_types in person_org_types.items():
        sex = person_sex.get(pk, "")
        if sex not in ("m", "f"):
            sex = "unspecified"
        for ot in org_types:
            person_org_sex[ot][sex] += 1

    # Normalisation status for transaction type breakdown
    catchword_stats = Counter()
    normalised_count = 0
    for r in eis_rows:
        cw = r.get("catchwords", "").strip()
        if cw:
            norm = norm_map.get(cw)
            if norm:
                catchword_stats[norm] += 1
                normalised_count += 1
            else:
                catchword_stats["_not_normalised"] += 1

    # Sex distribution summary
    sex_total = Counter()
    for pk, sex_val in person_sex.items():
        if sex_val in ("m", "f"):
            sex_total[sex_val] += 1
        else:
            sex_total["unspecified"] += 1

    # Serialise time series
    role_sex_decade_out = {}
    for role, decade_data in role_sex_decade.items():
        role_sex_decade_out[role] = {
            str(d): dict(c) for d, c in sorted(decade_data.items())
        }

    # Serialise distinct-person aggregates (count, not key list — keys would
    # bloat the JSON; client recomputes time-filtered individuals from
    # role_sex_decade_persons_keys below).
    role_persons_by_sex = {
        role: {sex: len(pks) for sex, pks in sex_pks.items()}
        for role, sex_pks in role_sex_persons.items()
    }

    # Per-decade person key lists for time-filter recomputation. Compact
    # representation: every person_key occurs in each decade-bucket where
    # they hold this role. JS unions the sets across the active decade range.
    role_persons_by_decade_out = {}
    for role, decade_data in role_sex_decade_persons.items():
        role_persons_by_decade_out[role] = {
            str(d): {sex: sorted(pks) for sex, pks in sex_pks.items()}
            for d, sex_pks in sorted(decade_data.items())
        }

    result = {
        "meta": _meta(
            description="Function roles by sex, with temporal and "
                        "institutional dimensions",
            sources=["persons.csv", "persons_in_events.csv",
                     "events_in_sources.csv", "organisations.csv",
                     "orgs_in_events.csv", "label_norm_matching.csv"],
            dimensions=[
                {"name": "role", "type": "categorical",
                 "values": sorted(role_sex.keys()),
                 "description": "Event role from rs/@role; includes "
                                "'' (unspecified) and transactiongood_* "
                                "(6 rows, rare annotation artefacts)"},
                {"name": "sex", "type": "categorical",
                 "values": ["m", "f", "unspecified"]},
                {"name": "decade", "type": "temporal",
                 "values": "1170-1520 (step 10)"},
                {"name": "transaction_type", "type": "categorical",
                 "description": "Normalised dispositive verb category"},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of person-event participations"},
            ],
        ),
        "observations": {
            "role_by_sex": {role: dict(c) for role, c in role_sex.items()},
            "role_by_sex_by_decade": role_sex_decade_out,
            "role_persons_by_sex": role_persons_by_sex,
            "role_persons_by_decade": role_persons_by_decade_out,
            "transaction_types": dict(catchword_stats),
            "org_type_totals": org_type_totals,
            "org_type_by_decade": {
                ot: dict(decades) for ot, decades in org_type_events.items()
            },
            "org_type_by_sex": {
                ot: dict(c) for ot, c in person_org_sex.items()
            },
        },
        "drill_down": {
            "role_sex": {
                role: {sex: sorted(fkeys) for sex, fkeys in sex_fkeys.items()}
                for role, sex_fkeys in role_sex_files.items()
            },
            "org_type": {
                ot: sorted(fkeys) for ot, fkeys in org_type_files.items()
            },
        },
        "coverage": {
            "sex_distribution": dict(sex_total),
            "normalisation_rate": normalised_count,
            "total_events": len(eis_rows),
            "person_count": len(persons_rows),
            "persons_with_org": len(person_org_types),
            "org_type_count": len(org_type_totals),
        },
    }

    _write_json(result, docs_data_dir / "epic_a.json")
    return result


# ---------------------------------------------------------------------------
# Epic B aggregation (V0-T4): co-occurrence network
# ---------------------------------------------------------------------------

