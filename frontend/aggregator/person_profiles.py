"""Person profiles: master data + sources + roles + relations per person.

Aggregates from the pipeline CSVs a profile structure per ``pe__`` ID
for rendering the person profile pages under
``docs/register/persons/<id>.html``.

Input:
- ``reverse_index`` (built in build/__init__.py): per entity ID, the
  list of source metadata entries (url, idno, date_display, ...).
  Provides the profile's source table without re-derivation.

Output: a dict ``{pe__id: profile}`` with fixed structure (see module
README). Writes no file — the HTMLs are rendered directly in the build
step ``_build_person_profiles``.

Relation types per person:
- kin       (kinship)               — person<->person, bidirectional
- friend    (friendship)            — person<->person, bidirectional
- rep       (representation)        — person<->person, bidirectional
- occ       (occupation re: org)    — person->org, unidirectional
- title_ref (title re: org)         — person->org, unidirectional
- owner     (place ownership)       — person<-place, place-side relation
- tenant    (place tenancy)         — person<-place, place-side relation
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv
from ._profile_labels import split_authorities
from ._profile_enrichment import (
    file_key_lookup,
    per_doc_label_persons,
    per_doc_roles_persons,
    enrich_sources,
    ROLE_LABEL_PERSON,
)


_ROLES = ("issuer", "recipient", "witness", "other")


def _load_person_stammdaten():
    """Load persons.csv -> per-id master-data dict.

    Includes the *_orig forms (forename / surname / addname) so the
    profile header can show how the name appears in the source where
    they differ from the regularised form.
    """
    out = {}
    for r in _cached_csv("persons.csv"):
        pid = r.get("id", "")
        if not pid:
            continue
        out[pid] = {
            "forename":      (r.get("forename_reg") or "").strip(),
            "surname":       (r.get("surname_reg") or "").strip(),
            "addName":       (r.get("addname_reg") or "").strip(),
            "forename_orig": (r.get("forename_orig") or "").strip(),
            "surname_orig":  (r.get("surname_orig") or "").strip(),
            "addname_orig":  (r.get("addname_orig") or "").strip(),
            "sex":           (r.get("sex") or "").strip(),
            "note":          (r.get("note") or "").strip(),
            "death_iso":     (r.get("dead_before") or "").strip(),
            "authority":     (r.get("authority") or "").strip(),
            "wiki_pageid":   (r.get("PAGEID_WienWiki") or "").strip(),
            "wiki_label":    (r.get("Name_WienWiki") or "").strip(),
        }
    return out


def _load_org_names():
    """Load organisations.csv -> {org_id: name}."""
    out = {}
    for r in _cached_csv("organisations.csv"):
        oid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or oid).strip()
        if oid:
            # only keep the main name (pre-pipe) for label use
            out[oid] = name.split("|", 1)[0].strip() or oid
    return out


def _load_place_names():
    """Load places.csv -> {pl__id: name}."""
    out = {}
    for r in _cached_csv("places.csv"):
        pid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or pid).strip()
        if pid:
            out[pid] = name.split("|", 1)[0].strip() or pid
    return out


def _format_death_german(death_iso):
    if not death_iso:
        return ""
    parts = death_iso.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        y, m, d = parts
        return f"{int(d):02d}.{int(m):02d}.{int(y):04d}"
    if len(parts) == 1 and parts[0].isdigit():
        return parts[0]
    return death_iso


def _display_name(s):
    """Compact display name from regularised master data."""
    parts = [s.get("forename", ""), s.get("surname", ""), s.get("addName", "")]
    return " ".join(p for p in parts if p) or ""


def _orig_display(s):
    """Compact original-form display name; empty if no _orig form differs.

    Concatenates the *_orig values when at least one of them is set and
    differs from the regularised form. Used by the template to surface
    the source spelling alongside the regularised header.
    """
    fo = s.get("forename_orig", "")
    so = s.get("surname_orig", "")
    ao = s.get("addname_orig", "")
    parts = [p for p in (fo, so, ao) if p]
    if not parts:
        return ""
    reg = _display_name(s)
    candidate = " ".join(parts)
    return candidate if candidate != reg else ""


def _file_to_source_lookup(reverse_index):
    """Map file_key -> source-meta dict (kept for relation rows)."""
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


def _aggregate_roles_per_person():
    """persons_in_events.csv -> {person_key: {issuer:n, recipient:n, ...}}."""
    out = defaultdict(lambda: Counter())
    for r in _cached_csv("persons_in_events.csv"):
        pk = r.get("person_key", "")
        role = (r.get("event_role") or "").strip()
        if pk and role in _ROLES:
            out[pk][role] += 1
    return out


def _aggregate_source_titles():
    """persons_in_sources.csv -> {person_key: [unique source_titles + source_prof]}.

    Combined title/occupation list, sorted by frequency.
    """
    counters = defaultdict(Counter)
    for r in _cached_csv("persons_in_sources.csv"):
        pk = r.get("person_key", "")
        if not pk:
            continue
        for col in ("source_titles", "source_prof"):
            v = (r.get(col) or "").strip()
            if v:
                counters[pk][v] += 1
    return {pk: [t for t, _ in c.most_common()] for pk, c in counters.items()}


def _build_relation_index(file_lookup, person_names, org_names, place_names):
    """Load all relation CSVs and group per person.

    Returns: ``{person_id: {kin, friend, rep, occ, title_ref, owner,
    tenant}}`` with each entry of the shape::

        {"label": str, "other_id": str, "other_name": str,
         "other_kind": "person"|"org"|"place",
         "role": "subject"|"counterpart",
         "file_key": str, "idno": str, "date_display": str, "url": str,
         "regest": str}

    role:
        - "subject":     this person is the bearer of the label
                         (person_key in the CSV, or the implicit
                         owner/tenant of the place row)
        - "counterpart": this person is the counterparty
                         (related_key in a person-person CSV)
    """
    rel = defaultdict(lambda: {k: [] for k in
                               ("kin", "friend", "rep", "occ", "title_ref",
                                "owner", "tenant")})

    # Person <-> Person, bidirectional.
    BIDIR = [
        ("kin_relations_in_sources.csv",    "kin",    "kin"),
        ("friend_relations_in_sources.csv", "friend", "friend"),
        ("rep_relations_in_sources.csv",    "rep",    "rep"),
    ]
    for csv_name, label_col, group in BIDIR:
        for r in _cached_csv(csv_name):
            pk = (r.get("person_key") or "").strip()
            rk = (r.get("related_key") or "").strip()
            label = (r.get(label_col) or "").strip().strip("|").strip()
            fk = (r.get("file_key") or "").strip()
            if not pk or not rk:
                continue
            src = file_lookup.get(fk, {})
            base = {
                "label":      label,
                "file_key":   fk,
                "idno":       src.get("idno", ""),
                "date_display": src.get("date_display", ""),
                "date_iso":   src.get("date_iso", ""),
                "collection_label": src.get("collection_label", ""),
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            sub = dict(base, other_id=rk,
                       other_name=person_names.get(rk, rk),
                       other_kind="person", role="subject")
            rel[pk][group].append(sub)
            cp = dict(base, other_id=pk,
                      other_name=person_names.get(pk, pk),
                      other_kind="person", role="counterpart")
            rel[rk][group].append(cp)

    # Person -> Org, unidirectional. Person owns the relation.
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
            if not pk:
                continue
            src = file_lookup.get(fk, {})
            entry = {
                "label":      label,
                "other_id":   rk,
                "other_name": org_names.get(rk, rk),
                "other_kind": "org",
                "role":       "subject",
                "file_key":   fk,
                "idno":       src.get("idno", ""),
                "date_display": src.get("date_display", ""),
                "date_iso":   src.get("date_iso", ""),
                "collection_label": src.get("collection_label", ""),
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            rel[pk][group].append(entry)

    # Place <- Person, unidirectional. Place owns the CSV, person is the
    # counterparty (``rel_key``). We surface it on the person side too so
    # the profile shows both sides of the same relation.
    PLACE_RELS = [
        ("owner_relations_in_sources.csv",  "owner",  "owner"),
        ("tenant_relations_in_sources.csv", "tenant", "tenant"),
    ]
    for csv_name, label_col, group in PLACE_RELS:
        for r in _cached_csv(csv_name):
            place_id = (r.get("place_key") or "").strip()
            rk = (r.get("rel_key") or "").strip()
            label = (r.get(label_col) or "").strip().strip("|").strip()
            fk = (r.get("xml_key") or r.get("file_key") or "").strip()
            if not place_id or not rk or not rk.startswith("pe__"):
                # Only the person-side relations land here; org-tenant
                # rows are still kept on the place profile.
                continue
            src = file_lookup.get(fk, {})
            entry = {
                "label":      label,
                "other_id":   place_id,
                "other_name": place_names.get(place_id, place_id),
                "other_kind": "place",
                "role":       "subject",
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


def build_person_profiles(reverse_index):
    """Build ``{pe__id: profile}`` for all persons with at least one
    released mention.

    profile structure (additions over the previous shape are noted):
        {
          "id", "display",
          "forename", "surname", "addName",
          "name_orig_display": "Anna Yrrensteig",     # NEW (or "")
          "sex", "note", "death_iso", "death_display",
          "authority_urls": ["https://...", ...],     # NEW (pipe-split)
          "wiki_label", "wiki_pageid",
          "source_titles": [str, ...],
          "sources":      [doc-meta + label + roles],  # ENRICHED
          "source_count": int,
          "active_min", "active_max": "YYYY",
          "roles":      {issuer, recipient, witness, other},
          "role_total": int,
          "role_labels": {key: german label},          # NEW
          "relations":  {kin, friend, rep, occ, title_ref, owner, tenant},
        }
    """
    stamm = _load_person_stammdaten()
    org_names = _load_org_names()
    place_names = _load_place_names()
    file_lookup = _file_to_source_lookup(reverse_index)
    person_roles = _aggregate_roles_per_person()
    source_titles = _aggregate_source_titles()

    person_names = {pid: _display_name(s) or pid for pid, s in stamm.items()}
    relations = _build_relation_index(file_lookup, person_names,
                                      org_names, place_names)

    # Per-doc enrichment for the sources table.
    fk_lookup = file_key_lookup()
    label_map = per_doc_label_persons()
    role_map = per_doc_roles_persons()

    profiles = {}
    for pid, docs in reverse_index.items():
        if not pid.startswith("pe__"):
            continue
        if not docs:
            continue
        s = stamm.get(pid, {})
        years = [d.get("date_iso", "")[:4] for d in docs
                 if d.get("date_iso", "")[:4].isdigit()]
        roles = person_roles.get(pid, Counter())
        roles_dict = {r: roles.get(r, 0) for r in _ROLES}
        rels = relations.get(pid, {k: [] for k in
                                    ("kin", "friend", "rep", "occ",
                                     "title_ref", "owner", "tenant")})

        sources = enrich_sources(docs, pid, fk_lookup, label_map, role_map,
                                 ROLE_LABEL_PERSON)

        profiles[pid] = {
            "id": pid,
            "display": _display_name(s) or pid,
            "forename": s.get("forename", ""),
            "surname":  s.get("surname", ""),
            "addName":  s.get("addName", ""),
            "name_orig_display": _orig_display(s),
            "sex":      s.get("sex", ""),
            "note":     s.get("note", ""),
            "death_iso":     s.get("death_iso", ""),
            "death_display": _format_death_german(s.get("death_iso", "")),
            "authority_urls": split_authorities(s.get("authority", "")),
            "wiki_label":   s.get("wiki_label", ""),
            "wiki_pageid":  s.get("wiki_pageid", ""),
            "source_titles": source_titles.get(pid, []),
            "sources":       sources,
            "source_count":  len(docs),
            "active_min":    min(years) if years else "",
            "active_max":    max(years) if years else "",
            "roles":         roles_dict,
            "role_total":    sum(roles_dict.values()),
            "role_labels":   ROLE_LABEL_PERSON,
            "relations":     rels,
        }

    return profiles
