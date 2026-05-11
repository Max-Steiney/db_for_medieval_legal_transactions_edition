"""Organisation profiles: master data + sources + roles + relations per org.

Counterpart to ``person_profiles.py`` for ``org__`` entities. Built from the
same released-only CSV subset.

Input:
- ``reverse_index`` (built in build/__init__.py): per entity ID, the
  released source list (url, idno, date_display, ...).

Output: a dict ``{org__id: profile}`` for orgs with at least one released
mention. The HTMLs are rendered directly in the build step
``_build_org_profiles``.

Relations involving the org:
- occ        (person->org, occupation)     — inverse of person profile
- title_ref  (person->org, title)          — inverse of person profile
- events     (org as recipient/issuer/...) from orgs_in_events.csv
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv


# Event roles for orgs mirror the person side. orgs_in_events.csv yields
# the same `event_role` vocabulary.
_ROLES = ("issuer", "recipient", "witness", "other")


def _load_org_stammdaten():
    """Load organisations.csv -> {id: master-data fields}."""
    out = {}
    for r in _cached_csv("organisations.csv"):
        oid = r.get("id", "")
        if not oid:
            continue
        out[oid] = {
            "name":       (r.get("name_reg") or r.get("name_orig") or oid).strip(),
            "name_orig":  (r.get("name_orig") or "").strip(),
            "type":       (r.get("type") or "").strip(),
            "observance": (r.get("observance") or "").strip(),
            "authority":  (r.get("authority") or "").strip(),
            "sub":        (r.get("sub") or "").strip(),
            "place_key":  (r.get("place_key") or "").strip(),
        }
    return out


def _load_person_names():
    """Load persons.csv -> {pe__id: display name}."""
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
    """Load places.csv -> {pl__id: display name}."""
    out = {}
    for r in _cached_csv("places.csv"):
        pid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or pid).strip()
        if pid:
            out[pid] = name or pid
    return out


def _file_to_source_lookup(reverse_index):
    """file_key -> source-meta dict via filenames.csv + reverse_index.

    Same bridge as person_profiles._file_to_source_lookup.
    """
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
    """orgs_in_events.csv -> {org_key: {issuer:n, recipient:n, ...}}."""
    out = defaultdict(lambda: Counter())
    for r in _cached_csv("orgs_in_events.csv"):
        ok = r.get("org_key", "")
        role = (r.get("event_role") or "").strip()
        if ok and role in _ROLES:
            out[ok][role] += 1
    return out


def _aggregate_source_labels_per_org():
    """orgs_in_sources.csv -> {org_key: [unique source_text labels]}.

    The pipeline records the form of the org mention in
    ``source_text`` (e.g. an inline form like ‚Bürgerschaft zu Wien‘),
    grouped by frequency.
    """
    counters = defaultdict(Counter)
    for r in _cached_csv("orgs_in_sources.csv"):
        ok = r.get("org_key", "")
        if not ok:
            continue
        v = (r.get("source_text") or "").strip()
        if v:
            counters[ok][v] += 1
    out = {}
    for ok, c in counters.items():
        out[ok] = [t for t, _ in c.most_common()]
    return out


def _build_person_to_org_relations(file_lookup, person_names):
    """Load occ/title_ref CSVs and group by *org*.

    Each entry per org:
        {"label": str, "person_id": str, "person_name": str,
         "file_key", "idno", "date_display", "url", "regest"}
    """
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
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            rel[rk][group].append(entry)

    return rel


def build_org_profiles(reverse_index):
    """Build ``{org__id: profile}`` for orgs with at least one released
    mention.

    profile structure:
        {
          "id", "name", "name_orig", "type", "observance",
          "authority", "sub", "place_key", "place_name",
          "source_labels": [str, ...],
          "sources":      [doc-meta...],
          "source_count": int,
          "active_min", "active_max": "YYYY",
          "roles": {issuer, recipient, witness, other},
          "role_total": int,
          "relations": {occ: [...], title_ref: [...]},
        }
    """
    stamm = _load_org_stammdaten()
    person_names = _load_person_names()
    place_names = _load_place_names()
    file_lookup = _file_to_source_lookup(reverse_index)
    org_roles = _aggregate_event_roles_per_org()
    source_labels = _aggregate_source_labels_per_org()
    relations = _build_person_to_org_relations(file_lookup, person_names)

    profiles = {}
    for oid, docs in reverse_index.items():
        if not oid.startswith("org__"):
            continue
        if not docs:
            continue
        s = stamm.get(oid, {})
        years = [d.get("date_iso", "")[:4] for d in docs
                 if d.get("date_iso", "")[:4].isdigit()]
        roles = org_roles.get(oid, Counter())
        roles_dict = {r: roles.get(r, 0) for r in _ROLES}
        rels = relations.get(oid, {"occ": [], "title_ref": []})

        profiles[oid] = {
            "id": oid,
            "name":       s.get("name", oid),
            "name_orig":  s.get("name_orig", ""),
            "type":       s.get("type", ""),
            "observance": s.get("observance", ""),
            "authority":  s.get("authority", ""),
            "sub":        s.get("sub", ""),
            "place_key":  s.get("place_key", ""),
            "place_name": place_names.get(s.get("place_key", ""), ""),
            "source_labels": source_labels.get(oid, []),
            "sources":      docs,
            "source_count": len(docs),
            "active_min":   min(years) if years else "",
            "active_max":   max(years) if years else "",
            "roles":        roles_dict,
            "role_total":   sum(roles_dict.values()),
            "relations":    rels,
        }

    return profiles
