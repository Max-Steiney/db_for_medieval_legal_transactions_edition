"""Relations aggregation: annotated relations between persons — for the relation and label
sections in analysis/auswertungen.html."""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import _cached_csv, _meta, _decade, _write_json


def aggregate_relations(docs_data_dir: Path) -> dict:
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
        ("anstat", ["an stat", "anstatt", "anstat und zuhanden",
                    "statt", "stat", "an seines herrn statt"]),
        # rep – executor
        ("geschefftleuten", ["geschefftleut"]),
        # rep – for
        ("zu handen", ["zu hannden"]),
        # rep – executor (medieval German "Geschäftsherr/-herren" — many
        # spellings: geschefft- / gescheft- / geschäft-, with or without
        # final -n; all collapse onto one canonical key).
        ("geschäftsvollstrecker", [
            "geschäftsherr", "geschäftsherren", "geschäftsherrn",
            "geschefftherr", "geschefftherren", "geschefftherrn",
            "gescheftherr", "gescheftherren", "gescheftherrn",
        ]),
        # rep / occ – advocate ("vorsprech" without final -en is the older
        # form, both meanings overlap; conflated regardless of type bucket).
        ("vorsprech", ["vorsprechen", "vorsprecher", "vorsprechern"]),
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
    # Label aggregation: (label_norm, type) -> nennungen + unique-person sets.
    # m/f/unspecified count nennungen (one increment per CSV row), persons_*
    # are sets of unique person_keys; the latter are what gets reported in
    # the labels table so the sex breakdown matches the Personen column.
    label_agg: dict[tuple, dict] = defaultdict(
        lambda: {"m": 0, "f": 0, "unspecified": 0,
                 "persons": set(),
                 "persons_m": set(), "persons_f": set(),
                 "persons_unspecified": set(),
                 "decades": set(), "raw_label": "",
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
                la[f"persons_{sex}"].add(pk)
                if dec is not None:
                    la["decades"].add(dec)
                # Track variant frequencies to pick best display label
                raw = label.strip().strip("|").strip()
                if raw:
                    la["variant_counts"][raw] += 1
                # Collect file_keys for label drill-down
                if fk:
                    label_sex_fkeys[(label_norm, rel_name, sex)].add(fk)

            # Per-person relationship entry (use normalised label for matching).
            # related_key (rk) is carried along so the person-network
            # visualisation can build person-to-person edges.
            person_rels[pk].append({
                "t": rel_name,
                "l": label.strip().strip("|").strip(),
                "ln": _norm_label(label_lower) if label_lower else "",
                "f": fk,
                "r": r.get("related_key", "").strip(),
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
            # Unique-person counts per sex. pm + pf + pu == persons.
            # Used by the labels table for an M/W bar that matches the
            # Personen column.
            "pm": len(agg["persons_m"]),
            "pf": len(agg["persons_f"]),
            "pu": len(agg["persons_unspecified"]),
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
        # The normalised key (kept as "norm" in the output) is what the
        # drill_down.label_sex map is keyed by — the display "label" is just
        # the most-frequent raw variant. Frontend uses "norm" for drill-down,
        # "label" for rendering.
        "labels": [{("norm" if k == "_norm_key" else k): v for k, v in e.items()}
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

    _write_json(result, docs_data_dir / "relations.json")
    return result
