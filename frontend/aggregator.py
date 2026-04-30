"""Build-time aggregation of pipeline CSVs for visualisation Epics.

Reads pipeline/output/*.csv and normalisation_lists/label_norm_matching.csv,
produces precomputed JSON files in docs/data/ for client-side rendering.

Output schema follows a Data-Cube-inspired convention:
- Each JSON file has a top-level "meta" block (provenance, dimensions, measures)
- Aggregated data uses explicit dimension/measure naming
- Entity references use canonical IDs (pe__*, org__*, pl__*, ev__*)
- Schema is JSON-LD-ready: field names can be mapped to a @context later
"""

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from pipeline.config import PIPELINE_OUTPUT, NORM_LISTS_DIR
from frontend.config import is_released_corpus

# Schema version — increment when output structure changes
SCHEMA_VERSION = "1.0"


def _is_released_row(row: dict) -> bool:
    """True, wenn die CSV-Zeile zu einem freigegebenen Quellenkorpus gehört.

    Pipeline-CSVs listen alle Bestände. Für Frontend-Aggregate zählen nur
    freigegebene. Das beseitigt den Vienna_1448-57_ready-Gap und die
    Zählung nicht-freigegebener QGW-Bände.
    """
    coll = row.get("collection", "")
    sub = row.get("subcollection", "")
    if not coll or not sub:
        return False
    return is_released_corpus(f"{coll}/{sub}")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _load_csv(path: Path, delimiter: str = ";") -> list[dict]:
    """Load a CSV file and return rows as list of dicts."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)


# Module-level CSV cache to avoid redundant I/O across aggregations
_csv_cache: dict[str, list[dict]] = {}


_released_file_keys_cache: set[str] | None = None


def _released_file_keys() -> set[str]:
    """Menge aller file_keys, die zu freigegebenen Quellenkorpora gehören.

    Grundlage ist filenames.csv (inkl. collection/subcollection); hier wird
    direkt gegen die CSV-Datei gelesen, damit _cached_csv nicht rekursiv
    aufgerufen wird.
    """
    global _released_file_keys_cache
    if _released_file_keys_cache is None:
        rows = _load_csv(PIPELINE_OUTPUT / "filenames.csv")
        _released_file_keys_cache = {
            r.get("id", "") for r in rows if _is_released_row(r)
        }
    return _released_file_keys_cache


def _cached_csv(name: str, delimiter: str = ";") -> list[dict]:
    """Load a pipeline CSV once, return cached result on subsequent calls.

    Filtert Zeilen nicht-freigegebener Quellenkorpora raus:
    - CSVs mit `collection` + `subcollection` direkt per Pfad-Prüfung.
    - CSVs mit `file_key` (und ohne collection) über die Menge der
      freigegebenen file_keys aus filenames.csv.
    So sickern Nennungen aus nicht-freigegebenen Bänden weder in Counts noch
    in Drill-Downs ein.
    """
    if name not in _csv_cache:
        rows = _load_csv(PIPELINE_OUTPUT / name, delimiter)
        if rows:
            first = rows[0]
            if "collection" in first and "subcollection" in first:
                rows = [r for r in rows if _is_released_row(r)]
            elif "file_key" in first:
                fks = _released_file_keys()
                rows = [r for r in rows if r.get("file_key", "") in fks]
        _csv_cache[name] = rows
    return _csv_cache[name]


def _load_norm_matching() -> dict[str, str]:
    """Load label_norm_matching.csv -> {source_catchword: catchword_main_norm}.

    Tab-delimited. Only rows with a non-empty catchword_main_norm are included.
    """
    path = NORM_LISTS_DIR / "label_norm_matching.csv"
    result = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            src = row.get("source_catchword", "").strip()
            norm = row.get("catchword_main_norm", "").strip()
            if src and norm:
                result[src] = norm
    return result


def _parse_coord(value: str) -> float | None:
    """Parse a coordinate string, handling comma decimals and text suffixes.

    Examples: '48,23134719' -> 48.23134719, '16.45N' -> 16.45,
    '13.95049 Möglich' -> 13.95049
    """
    if not value:
        return None
    # Replace comma with dot (German locale)
    cleaned = value.replace(",", ".")
    # Strip non-numeric suffixes (keep leading minus, digits, dots)
    match = re.match(r'^(-?[\d.]+)', cleaned)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _decade(date_str: str) -> int | None:
    """Extract decade from an ISO-ish date string (e.g. '13270415' -> 1320).

    Returns None for placeholder dates ('99999999') or unparseable values.
    """
    if not date_str or len(date_str) < 4:
        return None
    year_str = date_str[:4]
    try:
        year = int(year_str)
    except ValueError:
        return None
    if year > 1600 or year < 1000:
        return None
    return (year // 10) * 10


def _meta(description: str, sources: list[str],
          dimensions: list[dict], measures: list[dict]) -> dict:
    """Build a standardised meta block for a dataset JSON.

    Follows Data-Cube-inspired conventions:
    - dimensions: the categorical axes of the data (e.g. decade, sex, role)
    - measures: the numeric values being aggregated (e.g. count, weight)
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "created": date.today().isoformat(),
        "description": description,
        "sources": sources,
        "structure": {
            "dimensions": dimensions,
            "measures": measures,
        },
    }


def _write_json(data: dict | list, path: Path) -> None:
    """Write JSON to file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Timeline aggregation (V0-T2)
# ---------------------------------------------------------------------------

def aggregate_timeline(docs_data_dir: Path) -> dict:
    """Aggregate filenames.csv into timeline data by collection and decade."""
    rows = _cached_csv("filenames.csv")

    collections: dict[str, dict] = {}
    decades: dict[int, Counter] = defaultdict(Counter)
    placeholder_count = 0
    all_years = []

    for row in rows:
        coll = row.get("collection", "unknown")
        date_str = row.get("date", "")

        if coll not in collections:
            collections[coll] = {"count": 0, "dates": []}
        collections[coll]["count"] += 1

        dec = _decade(date_str)
        if dec is None:
            placeholder_count += 1
        else:
            decades[dec]["total"] += 1
            decades[dec][coll] += 1
            year = int(date_str[:4])
            all_years.append(year)
            collections[coll]["dates"].append(date_str)

    # Summarise collections
    coll_summary = {}
    for name, info in collections.items():
        dates = sorted(info["dates"])
        coll_summary[name] = {
            "count": info["count"],
            "min_date": dates[0] if dates else None,
            "max_date": dates[-1] if dates else None,
        }

    # Build decade list (fill gaps)
    if all_years:
        min_decade = (min(all_years) // 10) * 10
        max_decade = (max(all_years) // 10) * 10
    else:
        min_decade, max_decade = 1170, 1520

    decades_out = {}
    for d in range(min_decade, max_decade + 10, 10):
        entry = {"total": decades[d]["total"]}
        for coll_name in collections:
            entry[coll_name] = decades[d].get(coll_name, 0)
        decades_out[str(d)] = entry

    result = {
        "meta": _meta(
            description="Document counts by decade and source collection",
            sources=["filenames.csv"],
            dimensions=[
                {"name": "decade", "type": "temporal", "values": "1170-1520 (step 10)"},
                {"name": "collection", "type": "categorical",
                 "values": sorted(collections.keys())},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of source documents"},
            ],
        ),
        "total": len(rows),
        "period": [min(all_years) if all_years else None,
                   max(all_years) if all_years else None],
        "placeholder_count": placeholder_count,
        "collections": coll_summary,
        "decades": decades_out,
    }

    _write_json(result, docs_data_dir / "timeline.json")
    return result


# ---------------------------------------------------------------------------
# Epic A aggregation (V0-T3): roles x sex x institutions
# ---------------------------------------------------------------------------

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

    for r in pie_rows:
        pk = r.get("person_key", "")
        role = r.get("event_role", "other")
        ek = r.get("event_key", "")
        sex = person_sex.get(pk, "")
        if sex not in ("m", "f"):
            sex = "unspecified"

        role_sex[role][sex] += 1

        ei = event_info.get(ek, {})
        fk = ei.get("file_key", "")
        dec = _decade(ei.get("date", ""))
        if dec is not None:
            role_sex_decade[role][dec][sex] += 1

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

def aggregate_epic_b(docs_data_dir: Path) -> dict:
    """Build relationship-focused aggregation for the Beziehungsexplorer.

    Aggregates annotated relationships (kin, occ, rep, friend) by type,
    sex, decade, and label.  Produces compact JSON for grouped bar chart,
    label browser heatmap, and drill-down to persons and documents.
    """
    persons_rows = _cached_csv("persons.csv")
    events_rows = _cached_csv("events_in_sources.csv")

    # Person lookup: sex + display name
    person_sex: dict[str, str] = {}
    person_names: dict[str, str] = {}
    for r in persons_rows:
        pk = r["id"]
        sex = r.get("sex", "")
        person_sex[pk] = sex if sex in ("m", "f") else "unspecified"
        parts = [r.get("forename_reg", ""), r.get("surname_reg", "")]
        person_names[pk] = " ".join(p for p in parts if p).strip() or pk

    # Event → decade lookup (from date_not_after)
    event_decade: dict[str, int | None] = {}
    for r in events_rows:
        ek = r.get("event_key", "")
        if ek:
            dna = r.get("date_not_after", "").strip()
            event_decade[ek] = _decade(dna)

    # ── Label normalisation map ──
    # Maps lowercased spelling variants to a canonical key so that
    # e.g. "hausfrau", "hausfraw", "hausfraun", "hausfrawn", "hawsfraw"
    # are counted together.  The display label is chosen from the
    # highest-frequency raw variant during aggregation.
    _LABEL_NORM: dict[str, str] = {}
    _norm_groups = [
        # kin – wife / spouse
        ("hausfrau", [
            "hausfraw", "hausfraun", "hausfrawn", "hawsfraw", "hawsfrawn",
            "hausvrowe", "hausfrawen", "hawsfrawen", "hawsfrau",
            "hausvrown", "hausfrowe", "hausfrown", "hawsfrowe",
        ]),
        # kin – widow
        ("witib", [
            "witiben", "wittib", "wittibe", "witwe", "wittiben",
            "witibn", "wittibn",
        ]),
        # kin – son
        ("sun", ["sohn", "sohne", "sohnes", "sohns", "söhne"]),
        # kin – daughter
        ("tochter", ["tochtter", "töchter", "tochterr"]),
        # kin – children
        ("kinder", ["kindern", "kinden", "chinder", "chinden", "kind"]),
        # kin – brother
        ("bruder", [
            "pruder", "prudern", "bruders", "brüdern", "brüder",
            "prueder", "prüder",
        ]),
        # kin – brothers (collective)
        ("gepruder", ["gebruder", "gebrüder", "geprüder"]),
        # kin – sister
        ("swester", ["swestern", "schwester", "schwestern"]),
        # kin – siblings
        ("geswistreid", [
            "geswistreiden", "geswistreyd",
        ]),
        # kin – mother
        ("muter", ["mutter", "mueter", "müter"]),
        # kin – cousin / uncle
        ("vetter", ["vettern", "vetters"]),
        ("swager", ["schwager", "schwagers"]),
        ("oheim", ["oheims"]),
        ("muhme", ["muemen", "mumen", "mümen"]),
        # kin – son-in-law
        ("aidem", ["eidam"]),
        # kin – marriage qualifier
        ("elichen", ["eleichen"]),
        # occ – citizen
        ("burger", [
            "purger", "bürger", "bürgers", "burgern",
            "mitburger", "mitbürger", "mitpurger", "mitbürgern",
            "wiener bürger", "wiener bürgers",
            "purger ze wienn", "purger ze wienne",
        ]),
        # occ – mayor
        ("purgermaister", [
            "burgermaister", "bürgermeisters", "bürgermeister",
            "purgermeister",
        ]),
        # occ – chaplain
        ("kaplan", ["caplan", "chaplan", "capplan", "chapplan", "chapellan"]),
        # occ – pastor
        ("pharrer", ["pfarrer"]),
        # occ – council
        ("rats", ["rates", "rat", "rats der stat",
                  "rates der stat ze wienne"]),
        # occ – mintmaster
        ("münzmaister", ["münssmaister", "munssmaister"]),
        # occ – abbot
        ("abt", ["abbt"]),
        # occ – officer
        ("amptman", ["ambtman"]),
        # occ – mountain master
        ("bergmeisters", ["pergmaister"]),
        # occ – canon
        ("korherr", ["chorherr"]),
        # rep – on behalf of
        ("anstat", ["an stat", "anstatt", "anstat und zuhanden"]),
        # rep – executor
        ("geschefftleuten", ["geschefftleut"]),
        # rep – for
        ("zu handen", ["zu hannden"]),
        # rep – Geschäftsvollstrecker
        ("geschäftsvollstrecker", ["geschäftsherr", "geschäftsherren"]),
    ]
    for canonical, variants in _norm_groups:
        for v in variants:
            _LABEL_NORM[v] = canonical

    def _norm_label(raw_lower: str) -> str:
        """Return the canonical label key for aggregation."""
        return _LABEL_NORM.get(raw_lower, raw_lower)

    # ── Collect all annotated relationships ──
    REL_FILES = [
        ("kin_relations_in_sources.csv", "kin"),
        ("occ_relations_in_sources.csv", "occ"),
        ("rep_relations_in_sources.csv", "rep"),
        ("friend_relations_in_sources.csv", "friend"),
    ]
    SEX_KEYS = ["m", "f", "unspecified"]
    REL_TYPES = ["kin", "occ", "rep", "friend"]

    # Accumulators
    type_by_sex: dict[str, Counter] = {t: Counter() for t in REL_TYPES}
    type_by_sex_by_decade: dict[str, dict[int, Counter]] = {
        t: defaultdict(Counter) for t in REL_TYPES
    }
    # Label aggregation: (label_norm, type) -> {m, f, unspecified, persons, decades}
    label_agg: dict[tuple, dict] = defaultdict(
        lambda: {"m": 0, "f": 0, "unspecified": 0,
                 "persons": set(), "decades": set(), "raw_label": "",
                 "variant_counts": Counter()}
    )
    # Per-person relationship list (for detail panel)
    person_rels: dict[str, list] = defaultdict(list)
    # Drill-down file_keys per type×sex
    dd_type_sex: dict[str, set] = defaultdict(set)
    # Drill-down file_keys per label×sex (top labels only, built later)
    label_sex_fkeys: dict[tuple, set] = defaultdict(set)

    for rel_file, rel_name in REL_FILES:
        rel_rows = _cached_csv(rel_file)
        for r in rel_rows:
            pk = r.get("person_key", "")
            fk = r.get("file_key", "")
            ek = r.get("event_key", "")
            label = r.get(rel_name, "").strip()
            if not pk:
                continue

            sex = person_sex.get(pk, "unspecified")
            dec = event_decade.get(ek)

            # Overview aggregation
            type_by_sex[rel_name][sex] += 1
            if dec is not None:
                type_by_sex_by_decade[rel_name][dec][sex] += 1

            # Drill-down: type × sex
            if fk:
                dd_type_sex[f"{rel_name}_{sex}"].add(fk)

            # Label aggregation
            label_lower = label.lower().strip().strip("|").strip()
            label_norm = _norm_label(label_lower)
            if label_lower:
                key = (label_norm, rel_name)
                la = label_agg[key]
                la[sex] += 1
                la["persons"].add(pk)
                if dec is not None:
                    la["decades"].add(dec)
                # Track variant frequencies to pick best display label
                raw = label.strip().strip("|").strip()
                if raw:
                    la["variant_counts"][raw] += 1
                # Collect file_keys for label drill-down
                if fk:
                    label_sex_fkeys[(label_norm, rel_name, sex)].add(fk)

            # Per-person relationship entry (use normalised label for matching)
            person_rels[pk].append({
                "t": rel_name,
                "l": label.strip().strip("|").strip(),
                "ln": _norm_label(label_lower) if label_lower else "",
                "f": fk,
            })

    # ── Build overview ──
    overview_tbs = {}
    for t in REL_TYPES:
        overview_tbs[t] = {s: type_by_sex[t][s] for s in SEX_KEYS}

    overview_tbsd = {}
    for t in REL_TYPES:
        decade_dict = {}
        for dec, counts in sorted(type_by_sex_by_decade[t].items()):
            decade_dict[str(dec)] = {s: counts[s] for s in SEX_KEYS}
        overview_tbsd[t] = decade_dict

    # ── Build labels array (sorted by total frequency desc) ──
    labels_list = []
    for (label_norm_key, rel_type), agg in label_agg.items():
        total = agg["m"] + agg["f"] + agg["unspecified"]
        decades = sorted(agg["decades"]) if agg["decades"] else []
        # Pick the most frequent raw variant as the display label
        vc = agg["variant_counts"]
        display_label = vc.most_common(1)[0][0] if vc else label_norm_key
        # Collect all variant spellings (for transparency)
        variants = [v for v, _ in vc.most_common() if v.lower() != display_label.lower()]
        entry: dict = {
            "label": display_label,
            "type": rel_type,
            "m": agg["m"],
            "f": agg["f"],
            "unspecified": agg["unspecified"],
            "total": total,
            "persons": len(agg["persons"]),
            "decade_range": [decades[0], decades[-1]] if decades else [],
        }
        if variants:
            entry["variants"] = variants[:5]  # cap at 5 for JSON size
        entry["_norm_key"] = label_norm_key  # internal, stripped before output
        labels_list.append(entry)
    labels_list.sort(key=lambda x: x["total"], reverse=True)

    # ── Build persons array (only those with ≥1 annotated relationship) ──
    persons_out = []
    for pk in sorted(person_rels.keys()):
        persons_out.append({
            "id": pk,
            "name": person_names.get(pk, pk),
            "sex": person_sex.get(pk, "unspecified"),
            "rels": person_rels[pk],
        })

    # ── Build drill-down blocks ──
    dd_ts = {k: sorted(v) for k, v in dd_type_sex.items()}

    # Label drill-down: only for top 100 labels by frequency
    top_label_keys = set()
    for entry in labels_list[:100]:
        top_label_keys.add((entry["_norm_key"], entry["type"]))

    dd_ls = {}
    for (lbl_lower, rel_type, sex), fkeys in label_sex_fkeys.items():
        if (lbl_lower, rel_type) in top_label_keys:
            dd_key = f"{lbl_lower}__{sex}"
            dd_ls[dd_key] = sorted(fkeys)

    # ── E5: Representation direction (who represents whom, by sex) ──
    rep_rows = _cached_csv("rep_relations_in_sources.csv")
    rep_direction: dict[str, int] = Counter()  # "{rep_sex}>{principal_sex}" -> count
    rep_direction_fkeys: dict[str, set] = defaultdict(set)
    rep_top_reps: Counter = Counter()    # person_key -> count (as representative)
    rep_top_principals: Counter = Counter()  # person_key -> count (as principal)
    for r in rep_rows:
        rep_pk = r.get("person_key", "")
        principal_pk = r.get("related_key", "")
        fk = r.get("file_key", "")
        if not rep_pk or not principal_pk:
            continue
        rep_sex = person_sex.get(rep_pk, "unspecified")
        principal_sex = person_sex.get(principal_pk, "unspecified")
        direction_key = f"{rep_sex}>{principal_sex}"
        rep_direction[direction_key] += 1
        if fk:
            rep_direction_fkeys[direction_key].add(fk)
        rep_top_reps[rep_pk] += 1
        rep_top_principals[principal_pk] += 1

    rep_direction_data = {
        "matrix": dict(rep_direction),
        "drill_down": {k: sorted(v) for k, v in rep_direction_fkeys.items()},
        "top_representatives": [
            {"id": pk, "name": person_names.get(pk, pk),
             "sex": person_sex.get(pk, "unspecified"), "count": cnt}
            for pk, cnt in rep_top_reps.most_common(10) if pk in person_names
        ],
        "top_principals": [
            {"id": pk, "name": person_names.get(pk, pk),
             "sex": person_sex.get(pk, "unspecified"), "count": cnt}
            for pk, cnt in rep_top_principals.most_common(10) if pk in person_names
        ],
        "total": len(rep_rows),
    }

    # ── D3: Friendship edges (small network, fully enumerable) ──
    friend_rows = _cached_csv("friend_relations_in_sources.csv")
    friend_edges: list[dict] = []
    friend_node_degree: Counter = Counter()
    for r in friend_rows:
        pk1 = r.get("person_key", "")
        pk2 = r.get("related_key", "")
        fk = r.get("file_key", "")
        if not pk1 or not pk2:
            continue
        friend_edges.append({
            "source": pk1,
            "source_name": person_names.get(pk1, pk1),
            "source_sex": person_sex.get(pk1, "unspecified"),
            "target": pk2,
            "target_name": person_names.get(pk2, pk2),
            "target_sex": person_sex.get(pk2, "unspecified"),
            "file_key": fk,
        })
        friend_node_degree[pk1] += 1
        friend_node_degree[pk2] += 1

    friendship_data = {
        "edges": friend_edges,
        "total_edges": len(friend_edges),
        "unique_persons": len(friend_node_degree),
    }

    # ── Coverage stats ──
    total_rels = sum(
        sum(c.values()) for c in type_by_sex.values()
    )
    type_counts = {t: sum(type_by_sex[t].values()) for t in REL_TYPES}

    coverage = {
        "total_relations": total_rels,
        "persons_with_relations": len(person_rels),
        "unique_labels": len(label_agg),
        "type_counts": type_counts,
        # Backward-compatible keys for build.py template injection
        "node_count": len(person_rels),
        "total_annotated_relations": total_rels,
    }

    result = {
        "meta": _meta(
            description="Annotated relationships in medieval Viennese legal "
                        "transactions — aggregated by type, sex, decade, and label",
            sources=["persons.csv", "events_in_sources.csv",
                     "kin_relations_in_sources.csv",
                     "occ_relations_in_sources.csv",
                     "rep_relations_in_sources.csv",
                     "friend_relations_in_sources.csv"],
            dimensions=[
                {"name": "relationship_type", "type": "categorical",
                 "values": REL_TYPES},
                {"name": "sex", "type": "categorical",
                 "values": SEX_KEYS},
                {"name": "decade", "type": "temporal",
                 "description": "Decade derived from date_not_after"},
                {"name": "label", "type": "categorical",
                 "description": "Annotated relationship label (e.g. hausfrau, burger)"},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of annotated relationship instances"},
            ],
        ),
        "overview": {
            "type_by_sex": overview_tbs,
            "type_by_sex_by_decade": overview_tbsd,
        },
        "labels": [{k: v for k, v in e.items() if k != "_norm_key"}
                   for e in labels_list],
        "persons": persons_out,
        "drill_down": {
            "type_sex": dd_ts,
            "label_sex": dd_ls,
        },
        "rep_direction": rep_direction_data,
        "friendship": friendship_data,
        "coverage": coverage,
    }

    _write_json(result, docs_data_dir / "epic_b.json")
    return result


# ---------------------------------------------------------------------------
# Epic C aggregation (V0-T5): transaction repertoire x recipients
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Epic D aggregation (V0-T6): places with status
# ---------------------------------------------------------------------------

def aggregate_epic_d(docs_data_dir: Path, reverse_index: dict | None = None) -> dict:
    """Aggregate place data with reference and georeferencing status.

    Enhanced for Place Explorer (Option B): adds per-place document counts
    and file_keys for settlements with coordinates (map drill-down).
    """
    places_rows = _cached_csv("places.csv")
    pis_rows = _cached_csv("places_in_sources.csv")
    pie_rows = _cached_csv("places_in_events.csv")
    eis_rows = _cached_csv("events_in_sources.csv")

    # Build place_key -> set(file_key) lookup from places_in_sources
    place_file_keys: dict[str, set] = defaultdict(set)
    for r in pis_rows:
        pk = r.get("place_key", "")
        fk = r.get("file_key", "")
        if pk and fk:
            place_file_keys[pk].add(fk)

    # Build event_key -> decade lookup for temporal dimension
    event_decade: dict[str, int | None] = {}
    for r in eis_rows:
        ek = r.get("event_key", "")
        dec = _decade(r.get("date_not_before", ""))
        if dec is None:
            dec = _decade(r.get("date_not_after", ""))
        event_decade[ek] = dec

    # Build place_key -> set(decade) from places_in_events
    place_decades: dict[str, set] = defaultdict(set)
    for r in pie_rows:
        pk = r.get("place_key", "")
        ek = r.get("event_key", "")
        dec = event_decade.get(ek)
        if pk and dec is not None:
            place_decades[pk].add(dec)

    # Places referenced in sources
    referenced_keys = set(place_file_keys.keys())

    # Also check reverse_index if available
    if reverse_index:
        for eid in reverse_index:
            if eid.startswith("pl__"):
                referenced_keys.add(eid)

    # Type counts for coverage
    type_counts: Counter = Counter()

    places = []
    for r in places_rows:
        pid = r.get("id", "")
        lat = r.get("lat", "").strip()
        lng = r.get("lng", "").strip()
        geonames = r.get("geonames", "").strip()
        ptype = r.get("type", "")

        # Parse coordinates, handling comma decimals and text suffixes
        lat_f = _parse_coord(lat) if lat else None
        lng_f = _parse_coord(lng) if lng else None
        has_coords = lat_f is not None and lng_f is not None
        has_geonames = bool(geonames)

        type_counts[ptype] += 1

        doc_count = len(place_file_keys.get(pid, set()))
        decades = sorted(place_decades.get(pid, set()))
        entry = {
            "id": pid,
            "name": r.get("name_reg", ""),
            "type": ptype,
            "lat": lat_f,
            "lng": lng_f,
            "geonames": geonames if has_geonames else None,
            "referenced": pid in referenced_keys,
            "has_coords": has_coords,
            "has_geonames": has_geonames,
            "doc_count": doc_count,
            "decades": decades,
        }

        # Provenance: include file_keys for every referenced place so that
        # any aggregated number involving places can be traced back to its
        # source documents. Zero-referenced places omit the key to keep
        # unused entries small.
        if doc_count > 0:
            entry["file_keys"] = sorted(place_file_keys[pid])

        places.append(entry)

    referenced_count = sum(1 for p in places if p["referenced"])
    with_coords = sum(1 for p in places if p["has_coords"])
    with_geonames = sum(1 for p in places if p["has_geonames"])
    settlements_with_coords = sum(
        1 for p in places if p["type"] == "settlement" and p["has_coords"]
    )
    total_doc_links = sum(p["doc_count"] for p in places)

    raw_with_latlng = sum(1 for r in places_rows
                          if r.get("lat", "").strip() and r.get("lng", "").strip())

    result = {
        "meta": _meta(
            description="Place register with reference and georeferencing status",
            sources=["places.csv", "places_in_sources.csv"],
            dimensions=[
                {"name": "place", "type": "entity", "id_prefix": "pl__"},
                {"name": "place_type", "type": "categorical",
                 "description": "Register type classification"},
                {"name": "reference_status", "type": "boolean",
                 "description": "Whether place is referenced from source documents"},
                {"name": "georef_status", "type": "categorical",
                 "values": ["coords", "geonames", "both", "none"]},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of place entries"},
                {"name": "doc_count", "type": "integer",
                 "description": "Number of source documents referencing this place"},
            ],
        ),
        "places": places,
        "coverage": {
            "total": len(places),
            "referenced": referenced_count,
            "unreferenced": len(places) - referenced_count,
            "with_coords": with_coords,
            "with_geonames": with_geonames,
            "settlements_with_coords": settlements_with_coords,
            "total_doc_links": total_doc_links,
            "type_counts": dict(type_counts),
            "coord_parse_failures": raw_with_latlng - with_coords,
        },
    }

    _write_json(result, docs_data_dir / "epic_d.json")
    return result


# ---------------------------------------------------------------------------
# Document lookup for drill-down (V1 shared component)
# ---------------------------------------------------------------------------

def build_docs_lookup(docs_data_dir: Path, all_metadata: list[dict]) -> None:
    """Build a file_key -> document metadata JSON for exploration drill-down.

    Maps pipeline file_keys (from filenames.csv) to public URLs and metadata,
    enabling the JS drill-down overlay to display document details.
    """
    fnames = _cached_csv("filenames.csv")

    # Build (collection, subcollection, filename_stem) -> file_key
    fkey_map: dict[tuple, str] = {}
    for r in fnames:
        fk = r.get("id", "")
        coll = r.get("collection", "")
        subcoll = r.get("subcollection", "")
        fname = r.get("file", "").replace(".xml", "")
        if fk:
            fkey_map[(coll, subcoll, fname)] = fk

    lookup = {}
    for meta in all_metadata:
        key = (meta.get("collection", ""),
               meta.get("subcollection", ""),
               meta.get("filename", ""))
        fk = fkey_map.get(key)
        if fk:
            lookup[fk] = {
                "u": meta.get("url", ""),
                "i": meta.get("idno", ""),
                "d": meta.get("date_display", ""),
                "c": meta.get("collection_label", ""),
                "r": (meta.get("regest", "") or "")[:150],
            }

    _write_json(lookup, docs_data_dir / "docs_lookup.json")
    print(f"  Docs lookup: {len(lookup)} documents mapped")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_aggregation(docs_data_dir: Path, reverse_index: dict | None = None) -> dict:
    """Run all aggregations and write JSON files to docs/data/.

    Called from frontend/build.py after register loading.
    Returns a summary dict with stats from each aggregation.
    """
    print("Running data aggregation for visualisations...")
    docs_data_dir.mkdir(parents=True, exist_ok=True)

    # Clear CSV cache for fresh run
    _csv_cache.clear()

    timeline = aggregate_timeline(docs_data_dir)
    print(f"  Timeline: {timeline['total']} documents, "
          f"{timeline['placeholder_count']} placeholders")

    epic_a = aggregate_epic_a(docs_data_dir)
    print(f"  Epic A: {epic_a['coverage']['person_count']} persons, "
          f"{epic_a['coverage']['total_events']} events")

    epic_b = aggregate_epic_b(docs_data_dir)
    print(f"  Epic B: {epic_b['coverage']['persons_with_relations']} persons, "
          f"{epic_b['coverage']['total_relations']} relations, "
          f"{epic_b['coverage']['unique_labels']} labels")

    epic_c = aggregate_epic_c(docs_data_dir)
    print(f"  Epic C: {epic_c['coverage']['unique_verb_forms']} verb forms, "
          f"{epic_c['coverage']['recipient_orgs']} recipients")

    epic_d = aggregate_epic_d(docs_data_dir, reverse_index)
    print(f"  Epic D: {epic_d['coverage']['total']} places, "
          f"{epic_d['coverage']['referenced']} referenced")

    return {
        "timeline": {"total": timeline["total"]},
        "epic_a": {"persons": epic_a["coverage"]["person_count"]},
        "epic_b": epic_b["coverage"],
        "epic_c": {"verb_forms": epic_c["coverage"]["unique_verb_forms"]},
        "epic_d": epic_d["coverage"],
    }
