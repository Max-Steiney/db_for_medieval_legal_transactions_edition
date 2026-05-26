"""Organisation profiles: master data + sources + roles + relations.

Counterpart to ``person_profiles.py`` for ``org__`` entities. Adds the
hierarchical parent/child relation derived from ``organisations.csv``'s
``org_key`` column (404 children grouped under 137 parents in the
released set).
"""

from collections import Counter, defaultdict

from frontend.config import is_visible_corpus
from ._shared import _cached_csv
from ._profile_labels import (
    split_pipe_names, split_authorities, label_org_type,
)
from ._profile_enrichment import (
    file_key_lookup,
    file_meta_by_key,
    per_doc_label_orgs,
    per_doc_roles_orgs,
    enrich_sources,
    ROLE_LABEL_ORG,
)


_ROLES = ("issuer", "recipient", "witness", "other")


def _load_org_stammdaten():
    """Load organisations.csv -> {id: master-data}."""
    out = {}
    for r in _cached_csv("organisations.csv"):
        oid = r.get("id", "")
        if not oid:
            continue
        out[oid] = {
            "name_raw":   (r.get("name_reg") or r.get("name_orig") or oid).strip(),
            "name_orig":  (r.get("name_orig") or "").strip(),
            "type":       (r.get("type") or "").strip(),
            "observance": (r.get("observance") or "").strip(),
            "authority":  (r.get("authority") or "").strip(),
            "sub":        (r.get("sub") or "").strip(),
            "place_key":  (r.get("place_key") or "").strip(),
            "org_key":    (r.get("org_key") or "").strip(),
        }
    return out


def _load_person_names():
    out = {}
    for r in _cached_csv("persons.csv"):
        pid = r.get("id", "")
        if not pid:
            continue
        parts = [(r.get("forename_reg") or "").strip(),
                 (r.get("surname_reg") or "").strip(),
                 (r.get("addname_reg") or "").strip()]
        out[pid] = " ".join(p for p in parts if p) or pid
    return out


def _load_place_names():
    out = {}
    for r in _cached_csv("places.csv"):
        pid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or pid).strip()
        if pid:
            out[pid] = name.split("|", 1)[0].strip() or pid
    return out


def _org_display_name(stamm_row):
    """Pre-pipe main name. Falls back to the raw value when no pipe is set."""
    main, _ = split_pipe_names(stamm_row.get("name_raw", ""))
    return main or stamm_row.get("name_raw", "")


def _file_to_source_lookup(reverse_index):
    by_cp_idno = {}
    for docs in reverse_index.values():
        for d in docs:
            cp = d.get("collection_path", "")
            idno = d.get("idno", "")
            if cp and idno:
                by_cp_idno[(cp, idno)] = d

    out = {}
    for r in _cached_csv("filenames.csv"):
        fk = r.get("id", "")
        fname = r.get("file", "")
        coll = r.get("collection", "")
        sub = r.get("subcollection", "")
        if not fk or not fname or not coll or not sub:
            continue
        idno = fname[:-4] if fname.endswith(".xml") else fname
        cp = f"{coll}/{sub}"
        d = by_cp_idno.get((cp, idno))
        if not d:
            continue
        out[fk] = {
            "url":              d.get("url", ""),
            "idno":             idno,
            "date_display":     d.get("date_display", ""),
            "date_iso":         d.get("date_iso", ""),
            "collection_label": d.get("collection_label", ""),
            "collection_path":  cp,
            "regest":           d.get("regest", ""),
        }
    return out


def _aggregate_event_roles_per_org():
    out = defaultdict(lambda: Counter())
    for r in _cached_csv("orgs_in_events.csv"):
        ok = r.get("org_key", "")
        role = (r.get("event_role") or "").strip()
        if ok and role in _ROLES:
            out[ok][role] += 1
    return out


def _build_funding_network(file_lookup, person_names, org_display_names):
    """Pro Org: Stiftungsnetzwerk aus Issuer-Recipient-Beziehungen.

    Forschungsfrage 4 aus der Mail vom 16. Mai 2026: wer steht in einem
    Issuer-Recipient-Verhaeltnis zur betrachteten Organisation. Logik:
    fuer jede Org X sammle Events, in denen X als Issuer oder Recipient
    auftritt; ermittle die jeweiligen Gegenparts (Personen plus Orgs) in
    der komplementaeren Rolle.

    Returns: {org_id: {"issued_by_persons": [...], "issued_by_orgs": [...],
                       "received_by_persons": [...], "received_by_orgs": [...]}}
    Jeder Eintrag traegt die Belege als file_key-Liste plus Datum, sodass
    das Template Quellen verlinken kann.
    """
    # Schritt 1: Pro Org die Events bestimmen
    org_events_issuer = defaultdict(set)
    org_events_recipient = defaultdict(set)
    for r in _cached_csv("orgs_in_events.csv"):
        ok = r.get("org_key", "")
        role = (r.get("event_role") or "").strip()
        ek = r.get("event_key", "")
        if not ok or not ek:
            continue
        if role == "issuer":
            org_events_issuer[ok].add(ek)
        elif role == "recipient":
            org_events_recipient[ok].add(ek)

    # Schritt 2: pro Event die Gegenparts indexieren
    persons_by_event_role = defaultdict(lambda: defaultdict(list))
    for r in _cached_csv("persons_in_events.csv"):
        ek = r.get("event_key", "")
        role = (r.get("event_role") or "").strip()
        pk = r.get("person_key", "")
        fk = r.get("file_key", "")
        if ek and role and pk:
            persons_by_event_role[ek][role].append((pk, fk))

    orgs_by_event_role = defaultdict(lambda: defaultdict(list))
    for r in _cached_csv("orgs_in_events.csv"):
        ek = r.get("event_key", "")
        role = (r.get("event_role") or "").strip()
        ok = r.get("org_key", "")
        fk = r.get("file_key", "")
        if ek and role and ok:
            orgs_by_event_role[ek][role].append((ok, fk))

    # Schritt 3: Pro Org Gegenpart-Liste bauen, eindeutig pro Entity mit Beleg-Quellen
    out = {}
    for oid in set(org_events_issuer) | set(org_events_recipient):
        # X ist Issuer, Gegenpart ist Recipient
        rec_pers = defaultdict(list)
        rec_orgs = defaultdict(list)
        for ek in org_events_issuer.get(oid, set()):
            for pk, fk in persons_by_event_role[ek].get("recipient", []):
                rec_pers[pk].append(fk)
            for ok2, fk in orgs_by_event_role[ek].get("recipient", []):
                if ok2 != oid:
                    rec_orgs[ok2].append(fk)
        # X ist Recipient, Gegenpart ist Issuer
        iss_pers = defaultdict(list)
        iss_orgs = defaultdict(list)
        for ek in org_events_recipient.get(oid, set()):
            for pk, fk in persons_by_event_role[ek].get("issuer", []):
                iss_pers[pk].append(fk)
            for ok2, fk in orgs_by_event_role[ek].get("issuer", []):
                if ok2 != oid:
                    iss_orgs[ok2].append(fk)

        def entries(d, name_lookup, kind):
            rows = []
            for entity_id, fks in d.items():
                files = []
                for fk in fks:
                    src = file_lookup.get(fk, {})
                    if not src:
                        continue
                    files.append({
                        "file_key": fk,
                        "idno": src.get("idno", ""),
                        "date_display": src.get("date_display", ""),
                        "date_iso": src.get("date_iso", ""),
                        "url": src.get("url", ""),
                        "regest": src.get("regest", ""),
                        "collection_label": src.get("collection_label", ""),
                    })
                files.sort(key=lambda x: x.get("date_iso") or "")
                rows.append({
                    "entity_id": entity_id,
                    "entity_kind": kind,
                    "name": name_lookup.get(entity_id, entity_id),
                    "files": files,
                    "file_count": len(files),
                })
            rows.sort(key=lambda r: (-r["file_count"], r["name"].lower()))
            return rows

        funding = {
            "received_by_persons": entries(iss_pers, person_names, "person"),
            "received_by_orgs":    entries(iss_orgs, org_display_names, "org"),
            "issued_by_persons":   entries(rec_pers, person_names, "person"),
            "issued_by_orgs":      entries(rec_orgs, org_display_names, "org"),
        }
        # Nur aufnehmen wenn mindestens eine Liste nicht leer ist
        if any(v for v in funding.values()):
            funding["total"] = sum(len(v) for v in funding.values())
            out[oid] = funding
    return out


def _build_occ_network(file_meta, person_names):
    """Pro Org: Personen, die ueber occ (Taetigkeit) angebunden sind.

    Forschungsfrage 3 aus der Mail vom 16. Mai 2026: Personen mit occ-
    Verbindung zur betrachteten Org, plus Hinweis auf Verwandte (kin_count
    als 1-Hop-Mass). Logik:

      1. Pro Org alle Personen mit occ-Eintrag sammeln, occ-Begriffe und
         Beleg-Files deduplizieren.
      2. Pro Person kin-Eintraege im Quellenkorpus zaehlen (1-Hop).
      3. Liefere {"occ_persons": [...], "total": n}; nur Orgs mit
         occ_persons aufnehmen.
    """
    # Schritt 1: pro Org Personen mit occ-Begriffen und Belegen sammeln
    org_to_persons = defaultdict(lambda: defaultdict(lambda: {
        "occ_terms": set(),
        "files": set(),
    }))
    for r in _cached_csv("occ_relations_in_sources.csv"):
        pk = (r.get("person_key") or "").strip()
        rk = (r.get("related_key") or "").strip()
        occ = (r.get("occ") or "").strip().strip("|").strip()
        fk = (r.get("file_key") or "").strip()
        if not pk or not rk:
            continue
        bucket = org_to_persons[rk][pk]
        if occ:
            bucket["occ_terms"].add(occ)
        if fk:
            bucket["files"].add(fk)

    # Schritt 2: kin_count pro Person (1-Hop)
    kin_counts = Counter()
    for r in _cached_csv("kin_relations_in_sources.csv"):
        pk = (r.get("person_key") or "").strip()
        if pk:
            kin_counts[pk] += 1

    # Schritt 3: Ausgabe pro Org bauen
    out = {}
    for oid, persons in org_to_persons.items():
        rows = []
        for pk, info in persons.items():
            files = []
            for fk in info["files"]:
                src = file_meta.get(fk, {})
                if not src:
                    continue
                files.append({
                    "file_key": fk,
                    "idno": src.get("idno", ""),
                    "date_display": src.get("date_display", ""),
                    "date_iso": src.get("date_iso", ""),
                    "url": src.get("url", ""),
                    "regest": src.get("regest", ""),
                    "collection_label": src.get("collection_label", ""),
                })
            files.sort(key=lambda x: x.get("date_iso") or "")
            rows.append({
                "entity_id": pk,
                "name": person_names.get(pk, pk),
                "occ_terms": sorted(info["occ_terms"]),
                "files": files,
                "kin_count": kin_counts.get(pk, 0),
            })
        if not rows:
            continue
        rows.sort(key=lambda r: (-r["kin_count"], r["name"].lower()))
        out[oid] = {
            "occ_persons": rows,
            "total": len(rows),
        }
    return out


def _aggregate_source_labels_per_org():
    counters = defaultdict(Counter)
    for r in _cached_csv("orgs_in_sources.csv"):
        ok = r.get("org_key", "")
        if not ok:
            continue
        v = (r.get("source_text") or "").strip()
        if v:
            counters[ok][v] += 1
    return {ok: [t for t, _ in c.most_common()] for ok, c in counters.items()}


def _build_person_to_org_relations(file_lookup, person_names):
    """Load occ/title_ref CSVs and group by *org*."""
    rel = defaultdict(lambda: {"occ": [], "title_ref": []})

    PERSON_TO_ORG = [
        ("occ_relations_in_sources.csv",       "occ",       "occ"),
        ("title-ref_relations_in_sources.csv", "title_ref", "title_ref"),
    ]
    for csv_name, label_col, group in PERSON_TO_ORG:
        for r in _cached_csv(csv_name):
            pk = (r.get("person_key") or "").strip()
            rk = (r.get("related_key") or "").strip()
            label = (r.get(label_col) or "").strip().strip("|").strip()
            fk = (r.get("file_key") or "").strip()
            if not pk or not rk:
                continue
            src = file_lookup.get(fk, {})
            entry = {
                "label":      label,
                "person_id":   pk,
                "person_name": person_names.get(pk, pk),
                "file_key":   fk,
                "idno":       src.get("idno", ""),
                "date_display": src.get("date_display", ""),
                "date_iso":   src.get("date_iso", ""),
                "collection_label": src.get("collection_label", ""),
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            rel[rk][group].append(entry)

    return rel


def _build_children_index(stamm, released_org_ids):
    """{parent_org_id: [{id, name, released}]} sorted by display name.

    The full hierarchy from ``organisations.csv`` is materialised so a
    profile can list its sub-orgs even when none of them ended up in
    the released set. The ``released`` flag drives whether the template
    renders a link or plain text.
    """
    children = defaultdict(list)
    for oid, s in stamm.items():
        parent = s.get("org_key", "")
        if not parent:
            continue
        children[parent].append({
            "id": oid,
            "name": _org_display_name(s),
            "released": oid in released_org_ids,
        })
    for parent in children:
        children[parent].sort(key=lambda c: (c["name"] or "").lower())
    return children


def build_org_profiles(reverse_index):
    """Build ``{org__id: profile}`` for orgs with at least one released
    mention.

    profile structure additions:
        - "name", "name_aliases"  (NEW; pipe-split from name_reg)
        - "type_label"            (NEW; German display label)
        - "authority_urls"        (NEW; pipe-split list of URLs)
        - "parent_org_id" / "parent_org_name" / "parent_org_released"
        - "children": [{id, name, released}]
        - "role_labels", "role_total"
        - "sources" entries enriched with "label" and "roles"
    """
    stamm = _load_org_stammdaten()
    person_names = _load_person_names()
    place_names = _load_place_names()
    file_lookup = _file_to_source_lookup(reverse_index)
    org_roles = _aggregate_event_roles_per_org()
    source_labels = _aggregate_source_labels_per_org()
    relations = _build_person_to_org_relations(file_lookup, person_names)
    org_display_names = {oid: _org_display_name(s) for oid, s in stamm.items()}
    funding_network = _build_funding_network(file_lookup, person_names,
                                              org_display_names)
    visible_file_meta = {fk: m for fk, m in file_meta_by_key().items()
                         if is_visible_corpus(m.get("collection_path", ""))}
    occ_network = _build_occ_network(visible_file_meta, person_names)

    released_org_ids = {oid for oid, docs in reverse_index.items()
                        if oid.startswith("org__") and docs}
    children_index = _build_children_index(stamm, released_org_ids)

    fk_lookup = file_key_lookup()
    label_map = per_doc_label_orgs()
    role_map = per_doc_roles_orgs()

    profiles = {}
    for oid, docs in reverse_index.items():
        if not oid.startswith("org__"):
            continue
        if not docs:
            continue
        s = stamm.get(oid, {})
        name_main, name_aliases = split_pipe_names(s.get("name_raw", ""))
        years = [d.get("date_iso", "")[:4] for d in docs
                 if d.get("date_iso", "")[:4].isdigit()
                 and is_visible_corpus(d.get("collection_path", ""))]
        roles = org_roles.get(oid, Counter())
        roles_dict = {r: roles.get(r, 0) for r in _ROLES}
        rels = relations.get(oid, {"occ": [], "title_ref": []})

        parent_id = s.get("org_key", "")
        parent_name = ""
        parent_released = False
        if parent_id:
            parent_stamm = stamm.get(parent_id, {})
            parent_name = (_org_display_name(parent_stamm)
                           if parent_stamm else parent_id)
            parent_released = parent_id in released_org_ids

        sources = enrich_sources(docs, oid, fk_lookup, label_map, role_map,
                                 ROLE_LABEL_ORG)

        profiles[oid] = {
            "id": oid,
            "name":         name_main or s.get("name_raw", oid),
            "name_aliases": name_aliases,
            "name_orig":    s.get("name_orig", ""),
            "type":         s.get("type", ""),
            "type_label":   label_org_type(s.get("type", "")),
            "observance":   s.get("observance", ""),
            "authority_urls": split_authorities(s.get("authority", "")),
            "sub":          s.get("sub", ""),
            "place_key":    s.get("place_key", ""),
            "place_name":   place_names.get(s.get("place_key", ""), ""),
            "parent_org_id":       parent_id,
            "parent_org_name":     parent_name,
            "parent_org_released": parent_released,
            "children":     children_index.get(oid, []),
            "source_labels": source_labels.get(oid, []),
            "sources":       sources,
            "source_count":  len(docs),
            "active_min":    min(years) if years else "",
            "active_max":    max(years) if years else "",
            "roles":         roles_dict,
            "role_total":    sum(roles_dict.values()),
            "role_labels":   ROLE_LABEL_ORG,
            "relations":     rels,
            "funding":       funding_network.get(oid, {}),
            "occ_network":   occ_network.get(oid, {}),
        }

    return profiles
