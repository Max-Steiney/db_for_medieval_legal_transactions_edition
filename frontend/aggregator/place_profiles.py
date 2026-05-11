"""Place profiles: master data + sources + topo/owner/tenant relations per place.

Counterpart to ``person_profiles.py`` for ``pl__`` entities. Built from the
same released-only CSV subset.

Relations involving the place:
- topo    (place->place, topographic relation: ‚an dem‘, ‚gegen‘, ...)
- owner   (place owned by person or org)
- tenant  (place tenanted by person or org)
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv


# Event roles used in places_in_events.csv. The transaction-good values
# (transactiongood_I, transactiongood_II) capture the place's *function*
# in a transaction. They are surfaced verbatim in the profile.
_EVENT_ROLES = ("transactiongood_I", "transactiongood_II", "where", "of")


def _load_place_stammdaten():
    """Load places.csv -> {id: master-data fields}."""
    out = {}
    for r in _cached_csv("places.csv"):
        pid = r.get("id", "")
        if not pid:
            continue
        out[pid] = {
            "name":       (r.get("name_reg") or r.get("name_orig") or pid).strip(),
            "name_orig":  (r.get("name_orig") or "").strip(),
            "type":       (r.get("type") or "").strip(),
            "lat":        (r.get("lat") or "").strip(),
            "lng":        (r.get("lng") or "").strip(),
            "rel_place_key": (r.get("rel_place_key") or "").strip(),
            "adresse":    (r.get("Adresse_ak") or "").strip(),
            "geonames":   (r.get("geonames") or "").strip(),
            "parzelle":   (r.get("parzelle_idno") or "").strip(),
            "authority":  (r.get("authority") or "").strip(),
            "sub":        (r.get("sub") or "").strip(),
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


def _load_org_names():
    out = {}
    for r in _cached_csv("organisations.csv"):
        oid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or oid).strip()
        if oid:
            out[oid] = name or oid
    return out


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


def _aggregate_event_roles_per_place():
    """places_in_events.csv -> {place_key: Counter(event_role)}."""
    out = defaultdict(lambda: Counter())
    for r in _cached_csv("places_in_events.csv"):
        pk = r.get("place_key", "")
        role = (r.get("event_role") or "").strip()
        if pk and role:
            out[pk][role] += 1
    return out


def _aggregate_source_labels_per_place():
    """places_in_sources.csv -> {place_key: [unique source_text labels]}."""
    counters = defaultdict(Counter)
    for r in _cached_csv("places_in_sources.csv"):
        pk = r.get("place_key", "")
        if not pk:
            continue
        v = (r.get("source_text") or "").strip()
        if v:
            counters[pk][v] += 1
    out = {}
    for pk, c in counters.items():
        out[pk] = [t for t, _ in c.most_common()]
    return out


def _related_kind(rel_key):
    """Classify a related_key into person/org/place by prefix."""
    if not rel_key:
        return ""
    if rel_key.startswith("pe__"):
        return "person"
    if rel_key.startswith("org__"):
        return "org"
    if rel_key.startswith("pl__"):
        return "place"
    return ""


def _build_place_relations(file_lookup, person_names, org_names, place_names):
    """Load topo/owner/tenant CSVs and group by *place*.

    All three CSVs share the same shape: place_key, <label>, rel_key,
    event_key, xml_key (file_key). rel_key is the counterparty (any kind).
    """
    rel = defaultdict(lambda: {"topo": [], "owner": [], "tenant": []})

    PLACE_RELS = [
        ("topo_relations_in_sources.csv",   "topo",   "topo"),
        ("owner_relations_in_sources.csv",  "owner",  "owner"),
        ("tenant_relations_in_sources.csv", "tenant", "tenant"),
    ]
    name_books = {
        "person": person_names,
        "org":    org_names,
        "place":  place_names,
    }
    for csv_name, label_col, group in PLACE_RELS:
        for r in _cached_csv(csv_name):
            pk = (r.get("place_key") or "").strip()
            rk = (r.get("rel_key") or "").strip()
            label = (r.get(label_col) or "").strip().strip("|").strip()
            fk = (r.get("xml_key") or r.get("file_key") or "").strip()
            if not pk or not rk:
                continue
            kind = _related_kind(rk)
            name = name_books.get(kind, {}).get(rk, rk)
            src = file_lookup.get(fk, {})
            entry = {
                "label":      label,
                "other_id":   rk,
                "other_name": name,
                "other_kind": kind,
                "file_key":   fk,
                "idno":       src.get("idno", ""),
                "date_display": src.get("date_display", ""),
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            rel[pk][group].append(entry)

    return rel


def build_place_profiles(reverse_index):
    """Build ``{pl__id: profile}`` for places with at least one released
    mention.

    profile structure:
        {
          "id", "name", "name_orig", "type",
          "lat", "lng", "adresse", "geonames", "parzelle",
          "authority", "sub", "rel_place_key", "rel_place_name",
          "source_labels": [str, ...],
          "sources":      [doc-meta...],
          "source_count": int,
          "active_min", "active_max": "YYYY",
          "event_roles": {role: count},
          "relations": {topo: [...], owner: [...], tenant: [...]},
        }
    """
    stamm = _load_place_stammdaten()
    person_names = _load_person_names()
    org_names = _load_org_names()
    place_names = {pid: s["name"] for pid, s in stamm.items()}
    file_lookup = _file_to_source_lookup(reverse_index)
    place_roles = _aggregate_event_roles_per_place()
    source_labels = _aggregate_source_labels_per_place()
    relations = _build_place_relations(file_lookup, person_names,
                                       org_names, place_names)

    profiles = {}
    for pid, docs in reverse_index.items():
        if not pid.startswith("pl__"):
            continue
        if not docs:
            continue
        s = stamm.get(pid, {})
        years = [d.get("date_iso", "")[:4] for d in docs
                 if d.get("date_iso", "")[:4].isdigit()]
        roles = dict(place_roles.get(pid, Counter()))
        rels = relations.get(pid, {"topo": [], "owner": [], "tenant": []})

        profiles[pid] = {
            "id": pid,
            "name":       s.get("name", pid),
            "name_orig":  s.get("name_orig", ""),
            "type":       s.get("type", ""),
            "lat":        s.get("lat", ""),
            "lng":        s.get("lng", ""),
            "adresse":    s.get("adresse", ""),
            "geonames":   s.get("geonames", ""),
            "parzelle":   s.get("parzelle", ""),
            "authority":  s.get("authority", ""),
            "sub":        s.get("sub", ""),
            "rel_place_key":  s.get("rel_place_key", ""),
            "rel_place_name": place_names.get(s.get("rel_place_key", ""), ""),
            "source_labels": source_labels.get(pid, []),
            "sources":      docs,
            "source_count": len(docs),
            "active_min":   min(years) if years else "",
            "active_max":   max(years) if years else "",
            "event_roles":  roles,
            "relations":    rels,
        }

    return profiles
