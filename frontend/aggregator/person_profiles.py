"""Person-Profile: Stammdaten + Quellen + Rollen + Beziehungen pro Person.

Aggregiert aus den Pipeline-CSVs eine Profil-Struktur pro ``pe__``-ID
fuer das Rendering der Personen-Profilseiten unter
``docs/register/persons/<id>.html``.

Eingang:
- ``reverse_index`` (gebaut in build/__init__.py): pro Entitaets-ID die
  Liste der Quellen-Metadata-Eintraege (url, idno, date_display, ...).
  Liefert die Quellen-Tabelle des Profils ohne Re-Derivation.

Output: ein dict ``{pe__id: profile}`` mit fester Struktur (s. README im
Modul). Schreibt keine Datei — die HTMLs werden direkt im Build-Schritt
``_build_person_profiles`` gerendert.

Beziehungstypen (5):
- kin       (Verwandtschaft)        — person<->person, beidseitig
- friend    (Freundschaft)          — person<->person, beidseitig
- rep       (Stellvertretung)       — person<->person, beidseitig
- occ       (Beruf/Amt re: Org)     — person->org, einseitig
- title_ref (Titel re: Org)         — person->org, einseitig
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv


# Englische Rollenwerte aus persons_in_events.csv. Synchron mit
# PERSON_ROLES in build/_pages.py — wir wiederholen die Liste hier
# bewusst, um keine Build-Reihenfolgen-Abhaengigkeit einzufuehren.
_ROLES = ("issuer", "recipient", "witness", "other")


def _load_person_stammdaten():
    """Lade persons.csv -> {id: {forename, surname, addName, sex, note,
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
    """Lade organisations.csv -> {org_id: name}."""
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
    """Kompakter Anzeigename aus Stammdaten."""
    parts = [s.get("forename", ""), s.get("surname", ""), s.get("addName", "")]
    return " ".join(p for p in parts if p) or ""


def _file_to_source_lookup(reverse_index):
    """Map file_key -> source-meta dict for relation-row resolution.

    Pipeline-CSVs referenzieren Quellen via ``file_key`` (z. B.
    ``f__QGW_10``). reverse_index ist idno-basiert (``10``, in
    ``QGW/Vienna_1177-1414_ready``). Wir bauen die Bruecke ueber
    filenames.csv (file_key -> Datei + Collection-Pfad) und matchen
    dann gegen reverse_index per (collection_path, idno).
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

    Liefert die in der Quelle stehenden Titel-/Berufsbezeichnungen,
    sortiert nach Haeufigkeit. Beruf und Titel werden zusammengefasst,
    weil die UI-Differenzierung kaum Mehrwert bringt — sie dienen beide
    der Identifikation der Person.
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
    """Lade die 5 Beziehungs-CSVs und gruppiere pro Person.

    Liefert: {person_id: {"kin":[...], "friend":[...], "rep":[...],
                          "occ":[...], "title_ref":[...]}}

    Jeder Eintrag pro Person:
        {"label": str, "other_id": str, "other_name": str, "other_kind":
         "person"|"org", "other_sex": str, "role": "subject"|"counterpart",
         "file_key": str, "idno": str, "date_display": str, "url": str,
         "regest": str}

    role:
        - "subject":     diese Person ist person_key (= Traegerin des Labels)
        - "counterpart": diese Person ist related_key (Gegenpartei)
    """
    rel = defaultdict(lambda: {k: [] for k in
                               ("kin", "friend", "rep", "occ", "title_ref")})

    # person<->person Beziehungen: beidseitig
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
            # Subject-Sicht (person_key)
            sub = dict(base)
            sub["other_id"]   = rk
            sub["other_name"] = person_names.get(rk, rk)
            sub["other_kind"] = "person"
            sub["role"]       = "subject"
            rel[pk][group].append(sub)
            # Counterpart-Sicht (related_key)
            cp = dict(base)
            cp["other_id"]   = pk
            cp["other_name"] = person_names.get(pk, pk)
            cp["other_kind"] = "person"
            cp["role"]       = "counterpart"
            rel[rk][group].append(cp)

    # person->org Beziehungen: einseitig (Org hat noch kein Profil)
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
    """Baue dict ``{pe__id: profile}`` fuer alle Personen mit mind.
    einer Quelle im released set.

    Eine Person erscheint im Profil-Set genau dann, wenn sie als
    ``rs type="person"`` in einer freigegebenen Quelle annotiert ist —
    der reverse_index liefert dies bereits richtig.

    profile-Struktur:
        {
          "id": pe__id,
          "display": "Forename Surname AddName" oder pe__id,
          "forename", "surname", "addName",
          "sex": "m"|"f"|"",
          "note": str,
          "death_iso": str,           # rohes ISO (oder Jahr)
          "death_display": str,       # DD.MM.YYYY oder Jahr
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

    # person_names fuer Beziehungs-Aufloesung — Display aus Stammdaten,
    # Fallback ID. Wird auch fuer Personen genutzt, die nicht released
    # sind (Beziehung zu einer nicht-freigegebenen Person bleibt sichtbar
    # mit Namen, aber der Link wird im Template defensiv geprueft).
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
