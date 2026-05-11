"""Epic C: transaction types, verb forms, recipients — for the transaction
section in analysis/auswertungen.html."""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import _cached_csv, _load_norm_matching, _meta, _decade, _write_json


def aggregate_epic_c(docs_data_dir: Path) -> dict:
    """Aggregate transaction types and institutional recipients."""
    eis_rows = _cached_csv("events_in_sources.csv")
    oie_rows = _cached_csv("orgs_in_events.csv")
    orgs_rows = _cached_csv("organisations.csv")
    pie_rows = _cached_csv("persons_in_events.csv")
    norm_map = _load_norm_matching()

    org_info = {r["id"]: {"name": r.get("name_reg", ""), "type": r.get("type", "")}
                for r in orgs_rows}

    # Transaction types x decade
    tx_decade: dict[str, Counter] = defaultdict(Counter)
    tx_decade_fkeys: dict[str, dict[int, list]] = defaultdict(lambda: defaultdict(list))
    triggerstrings: dict[str, dict] = {}

    for r in eis_rows:
        cw = r.get("catchwords", "").strip()
        date_str = r.get("date_not_before", "")
        file_key = r.get("file_key", "")
        dec = _decade(date_str)

        if cw:
            norm = norm_map.get(cw, "_not_normalised")
            if dec is not None:
                tx_decade[norm][dec] += 1
                tx_decade_fkeys[norm][dec].append(file_key)

            if cw not in triggerstrings:
                triggerstrings[cw] = {"freq": 0, "norm": norm_map.get(cw, ""),
                                      "files": set()}
            triggerstrings[cw]["freq"] += 1
            triggerstrings[cw]["files"].add(file_key)

    # Serialise transaction type timeline
    all_decades_tx = set()
    for counts in tx_decade.values():
        all_decades_tx.update(counts.keys())

    tx_timeline = {}
    for tx_type, decade_counts in tx_decade.items():
        tx_timeline[tx_type] = {str(d): decade_counts.get(d, 0)
                                for d in sorted(all_decades_tx)}

    # Recipient organisations
    recipient_events: dict[str, list] = defaultdict(list)
    for r in oie_rows:
        role = r.get("event_role", "")
        if role == "recipient":
            ok = r.get("org_key", "")
            ek = r.get("event_key", "")
            fk = r.get("file_key", "")
            recipient_events[ok].append({"event_key": ek, "file_key": fk})

    # Recipient type breakdown
    recipients = []
    for ok, events in recipient_events.items():
        info = org_info.get(ok, {"name": ok, "type": ""})
        otype = info["type"] or "unknown"
        recipients.append({
            "id": ok,
            "name": info["name"],
            "type": otype,
            "count": len(events),
        })

    # Per organisation: contributing persons
    event_persons: dict[str, list] = defaultdict(list)
    for r in pie_rows:
        ek = r.get("event_key", "")
        pk = r.get("person_key", "")
        role = r.get("event_role", "")
        fk = r.get("file_key", "")
        event_persons[ek].append({"person_key": pk, "role": role, "file_key": fk})

    org_supporters: dict[str, list] = {}
    for ok, events in recipient_events.items():
        supporters = []
        for ev in events:
            for p in event_persons.get(ev["event_key"], []):
                supporters.append({
                    "person_key": p["person_key"],
                    "role": p["role"],
                    "file_key": p["file_key"],
                })
        org_supporters[ok] = supporters

    # Compact triggerstrings for JSON (include file_keys for drill-down)
    trigger_list = []
    for form, info in sorted(triggerstrings.items(), key=lambda x: -x[1]["freq"]):
        trigger_list.append({
            "form": form,
            "freq": info["freq"],
            "norm": info["norm"],
            "doc_count": len(info["files"]),
            "file_keys": sorted(info["files"]),
        })

    # Drill-down: file_keys per transaction type x decade
    drill_down_tx = {}
    for tx_type, decade_fkeys in tx_decade_fkeys.items():
        drill_down_tx[tx_type] = {str(d): fkeys
                                  for d, fkeys in decade_fkeys.items()}

    # Recipient type totals
    type_totals: Counter = Counter()
    for r in recipients:
        type_totals[r["type"]] += r["count"]

    normalised_event_count = sum(
        1 for r in eis_rows if norm_map.get(r.get("catchwords", "").strip())
    )

    # ── E4: Org type × transaction type cross-tabulation ──
    # Build event_key → normalised transaction type lookup
    event_tx_type: dict[str, str] = {}
    for r in eis_rows:
        ek = r.get("event_key", "")
        cw = r.get("catchwords", "").strip()
        if ek and cw:
            norm = norm_map.get(cw)
            if norm:
                event_tx_type[ek] = norm

    # Cross-tab: org_type × tx_type, only for recipient events
    org_tx_matrix: dict[str, Counter] = defaultdict(Counter)
    org_tx_fkeys: dict[str, set] = defaultdict(set)
    org_tx_total = 0
    org_tx_matched = 0
    for ok, events in recipient_events.items():
        info = org_info.get(ok, {"name": ok, "type": ""})
        otype = info["type"] or "unknown"
        for ev in events:
            org_tx_total += 1
            tx = event_tx_type.get(ev["event_key"])
            if tx:
                org_tx_matched += 1
                org_tx_matrix[otype][tx] += 1
                fk = ev.get("file_key", "")
                if fk:
                    org_tx_fkeys[f"{otype}__{tx}"].add(fk)

    # Serialise: [{org_type, tx_type, count}] for heatmap
    org_tx_cells = []
    for otype, tx_counts in sorted(org_tx_matrix.items()):
        for tx, cnt in tx_counts.most_common():
            org_tx_cells.append({"org_type": otype, "tx_type": tx, "count": cnt})
    org_tx_cells.sort(key=lambda c: -c["count"])

    org_tx_data = {
        "cells": org_tx_cells,
        "drill_down": {k: sorted(v) for k, v in org_tx_fkeys.items()},
        "coverage": {
            "total_recipient_events": org_tx_total,
            "matched_with_tx_type": org_tx_matched,
            "match_rate": round(org_tx_matched / org_tx_total * 100, 1) if org_tx_total else 0,
        },
    }

    result = {
        "meta": _meta(
            description="Transaction types (dispositive verbs) and institutional "
                        "recipients over time",
            sources=["events_in_sources.csv", "orgs_in_events.csv",
                     "organisations.csv", "persons_in_events.csv",
                     "label_norm_matching.csv"],
            dimensions=[
                {"name": "transaction_type", "type": "categorical",
                 "description": "Normalised dispositive verb category "
                                "(~15% coverage)"},
                {"name": "decade", "type": "temporal",
                 "values": "1170-1520 (step 10)"},
                {"name": "org_type", "type": "categorical",
                 "description": "Organisation register type (24 values)"},
                {"name": "verb_form", "type": "categorical",
                 "description": "Raw triggerstring as annotated in source"},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of events/transactions"},
                {"name": "freq", "type": "integer",
                 "description": "Occurrence frequency of verb form"},
            ],
        ),
        "observations": {
            "tx_timeline": tx_timeline,
            "recipient_type_totals": dict(type_totals),
        },
        "triggerstrings": trigger_list,
        "recipients": sorted(recipients, key=lambda r: -r["count"]),
        "org_supporters": org_supporters,
        "org_tx": org_tx_data,
        "drill_down": {
            "tx_type_decade": drill_down_tx,
        },
        "coverage": {
            "total_events": len(eis_rows),
            "normalised_events": normalised_event_count,
            "unique_verb_forms": len(trigger_list),
            "recipient_orgs": len(recipients),
        },
    }

    _write_json(result, docs_data_dir / "epic_c.json")
    return result
