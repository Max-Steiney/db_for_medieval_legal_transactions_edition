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

Relation types (5):
- kin       (kinship)               — person<->person, bidirectional
- friend    (friendship)            — person<->person, bidirectional
- rep       (representation)        — person<->person, bidirectional
- occ       (occupation re: org)    — person->org, unidirectional
- title_ref (title re: org)         — person->org, unidirectional
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv


# English role values from persons_in_events.csv. In sync with
# PERSON_ROLES in build/_pages.py — we repeat the list here deliberately
# to avoid introducing a build-order dependency.
_ROLES = ("issuer", "recipient", "witness", "other")


def _load_person_stammdaten():
    """Load persons.csv -> {id: {forename, surname, addName, sex, note,
    death_iso, wiki_pageid}}."""
    out = {}
    for r in _cached_csv("persons.csv"):
        pid = r.get("id", "")
        if not pid:
            continue
        out[pid] = {
            "forename": (r.get("forename_reg") or "").strip(),
            "surname":  (r.get("surname_reg") or "").strip(),
            "addName":  (r.get("addname_reg") or "").strip(),
            "sex":      (r.get("sex") or "").strip(),
            "note":     (r.get("note") or "").strip(),
            "death_iso": (r.get("dead_before") or "").strip(),
            "wiki_pageid": (r.get("PAGEID_WienWiki") or "").strip(),
            "wiki_label":  (r.get("Name_WienWiki") or "").strip(),
        }
    return out


def _load_org_names():
    """Load organisations.csv -> {org_id: name}."""
    out = {}
    for r in _cached_csv("organisations.csv"):
        oid = r.get("id", "")
        name = (r.get("name_reg") or r.get("name_orig") or oid).strip()
        if oid:
            out[oid] = name or oid
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
    """Compact display name from master data."""
    parts = [s.get("forename", ""), s.get("surname", ""), s.get("addName", "")]
    return " ".join(p for p in parts if p) or ""


def _file_to_source_lookup(reverse_index):
    """Map file_key -> source-meta dict for relation-row resolution.

    Pipeline CSVs reference sources via ``file_key`` (e.g.
    ``f__QGW_10``). reverse_index is idno-based (``10``, in
    ``QGW/Vienna_1177-1414_ready``). We bridge via filenames.csv
    (file_key -> file + collection path) and then match against
    reverse_index by (collection_path, idno).
    """
    # 1) Index reverse_index docs by (collection_path, idno) ----------
    by_cp_idno = {}
    for docs in reverse_index.values():
        for d in docs:
            cp = d.get("collection_path", "")
            idno = d.get("idno", "")
            if cp and idno:
                by_cp_idno[(cp, idno)] = d

    # 2) Walk filenames.csv (released-only via _cached_csv) -----------
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

    Returns the title/occupation labels as they appear in the source,
    sorted by frequency. Occupation and title are merged because the UI
    distinction adds little value — both serve to identify the person.
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
    out = {}
    for pk, c in counters.items():
        out[pk] = [t for t, _ in c.most_common()]
    return out


def _build_relation_index(file_lookup, person_names, org_names):
    """Load the 5 relation CSVs and group per person.

    Returns: {person_id: {"kin":[...], "friend":[...], "rep":[...],
                          "occ":[...], "title_ref":[...]}}

    Each entry per person:
        {"label": str, "other_id": str, "other_name": str, "other_kind":
         "person"|"org", "other_sex": str, "role": "subject"|"counterpart",
         "file_key": str, "idno": str, "date_display": str, "url": str,
         "regest": str}

    role:
        - "subject":     this person is person_key (= bearer of the label)
        - "counterpart": this person is related_key (counterparty)
    """
    rel = defaultdict(lambda: {k: [] for k in
                               ("kin", "friend", "rep", "occ", "title_ref")})

    # person<->person relations: bidirectional
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
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            # subject view (person_key)
            sub = dict(base)
            sub["other_id"]   = rk
            sub["other_name"] = person_names.get(rk, rk)
            sub["other_kind"] = "person"
            sub["role"]       = "subject"
            rel[pk][group].append(sub)
            # counterpart view (related_key)
            cp = dict(base)
            cp["other_id"]   = pk
            cp["other_name"] = person_names.get(pk, pk)
            cp["other_kind"] = "person"
            cp["role"]       = "counterpart"
            rel[rk][group].append(cp)

    # person->org relations: unidirectional (org has no profile yet)
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
                "url":        src.get("url", ""),
                "regest":     src.get("regest", ""),
            }
            rel[pk][group].append(entry)

    return rel


def build_person_profiles(reverse_index):
    """Build dict ``{pe__id: profile}`` for all persons with at least
    one source in the released set.

    A person appears in the profile set iff they are annotated as
    ``rs type="person"`` in a released source — the reverse_index
    already delivers this correctly.

    profile structure:
        {
          "id": pe__id,
          "display": "Forename Surname AddName" or pe__id,
          "forename", "surname", "addName",
          "sex": "m"|"f"|"",
          "note": str,
          "death_iso": str,           # raw ISO (or year)
          "death_display": str,       # DD.MM.YYYY or year
          "wiki_label", "wiki_pageid",
          "source_titles": [str, ...],
          "sources":     [doc-meta...],
          "source_count": int,
          "active_min", "active_max": "YYYY",
          "roles": {issuer, recipient, witness, other},
          "role_total": int,
          "relations": {kin, friend, rep, occ, title_ref}
        }
    """
    stamm = _load_person_stammdaten()
    org_names = _load_org_names()
    file_lookup = _file_to_source_lookup(reverse_index)
    person_roles = _aggregate_roles_per_person()
    source_titles = _aggregate_source_titles()

    # person_names for relation resolution — display from master data,
    # fallback to ID. Also used for persons not in the released set
    # (a relation to a non-released person stays visible with the name,
    # but the link is defensively checked in the template).
    person_names = {pid: _display_name(s) or pid for pid, s in stamm.items()}

    relations = _build_relation_index(file_lookup, person_names, org_names)

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
                                    ("kin", "friend", "rep", "occ", "title_ref")})

        profiles[pid] = {
            "id": pid,
            "display": _display_name(s) or pid,
            "forename": s.get("forename", ""),
            "surname":  s.get("surname", ""),
            "addName":  s.get("addName", ""),
            "sex":      s.get("sex", ""),
            "note":     s.get("note", ""),
            "death_iso":     s.get("death_iso", ""),
            "death_display": _format_death_german(s.get("death_iso", "")),
            "wiki_label":   s.get("wiki_label", ""),
            "wiki_pageid":  s.get("wiki_pageid", ""),
            "source_titles": source_titles.get(pid, []),
            "sources":      docs,
            "source_count": len(docs),
            "active_min":   min(years) if years else "",
            "active_max":   max(years) if years else "",
            "roles":        roles_dict,
            "role_total":   sum(roles_dict.values()),
            "relations":    rels,
        }

    return profiles
