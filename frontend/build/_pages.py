"""Page builders: landing page, sources index, register, exploration,
analysis, static Markdown pages and smaller JSON outputs.

Consumes the KPI and helper modules; invokes Jinja templates and
writes HTML/JSON to docs/.
"""

import json
import re as _re
import shutil
import sys
from collections import Counter
from datetime import date, datetime

from frontend.config import (
    DOCS_DIR, CONTENT_DIR, KNOWLEDGE_DIR, DATA_DIR,
    EDITION_GUIDELINES_PATH, EDITION_GUIDELINES_CANONICAL,
    RELEASED_PERIOD, max_year_with_extensions,
)

from frontend.build._helpers import (
    _format_german_date, _create_markdown_processor,
    _format_table_date, _load_docs_aggregate_lookup,
    COLLECTION_LABELS,
)
from frontend.build._kpi import (
    _compute_release_kpis, _compute_corpus_breakdown, _compute_matrix_columns,
    _released_person_keys, _persons_with_org_released,
)


# Controlled role vocabulary for the persons register.
# The `persons_in_events.csv` CSV yields four non-empty values:
# issuer/recipient/witness/other (witness covers 'sealer or witness',
# see knowledge/specification.md). Empty/`none` values are filtered out.
PERSON_ROLES = ("issuer", "recipient", "witness", "other")


def _short_collection_label(collection_path: str) -> str:
    """Compact label variant without year parenthesis for sub-labels.

    `QGW/Vienna_1177-1414_ready` -> `QGW II/1`, `Stadtbuecher Bd. 1
    (1395-1400)` -> `Stadtbuecher Bd. 1`. Falls back to the path when
    no mapping is available.
    """
    label = COLLECTION_LABELS.get(collection_path, collection_path)
    # Strip parenthesised year suffix: `Foo (1234-1456)` -> `Foo`
    cut = label.split(" (", 1)[0]
    return cut.strip()


def _load_person_roles(released_keys):
    """Aggregate the set of roles per person from persons_in_events.csv.
    Only roles from PERSON_ROLES are kept; empty/`none` entries are skipped.
    Restricted to the released set.
    """
    try:
        from frontend.aggregator import _cached_csv
        rows = _cached_csv("persons_in_events.csv")
    except Exception:
        return {}
    out: dict[str, set[str]] = {}
    valid = set(PERSON_ROLES)
    for r in rows:
        pk = r.get("person_key", "")
        if pk not in released_keys:
            continue
        role = (r.get("event_role") or "").strip()
        if role in valid:
            out.setdefault(pk, set()).add(role)
    return out


# ---------------------------------------------------------------------------
# Sources index (documents.html)
# ---------------------------------------------------------------------------


def _build_index(all_metadata, env, register_counts=None):
    """Build the index/browse page."""
    all_metadata.sort(key=lambda m: (m.get("date_iso", ""), m.get("collection", "")))

    agg_lookup = _load_docs_aggregate_lookup()
    search_data = []
    for m in all_metadata:
        agg = agg_lookup.get((m.get("collection_path", ""), m.get("idno", "")))
        if agg:
            persons_dist = agg.get("persons", {})
            events_dist = agg.get("events", {})
        else:
            persons_dist = {}
            events_dist = {}

        search_data.append({
            "t": m.get("regest", "") or m.get("title", ""),
            "tf": m.get("regest_full", "") or m.get("regest", ""),
            "d": m.get("date_display", ""),
            "di": m.get("date_iso", ""),
            "dn": _format_table_date(agg) if agg else "",
            "c": m.get("collection", ""),
            "sc": m.get("subcollection", ""),
            "cl": m.get("collection_label", ""),
            "cp": m.get("collection_path", ""),
            "id": m.get("idno", ""),
            "u": m.get("url", ""),
            "p": m.get("place", ""),
            "f": 1 if m.get("has_facsimile") else 0,
            "fu": (m.get("facsimile_urls") or [""])[0],
            "pc": m.get("person_count", 0),
            "pcd": persons_dist.get("distinct", 0),
            "pcdf": persons_dist.get("f", 0),
            "pcdm": persons_dist.get("m", 0),
            "pcdu": persons_dist.get("u", 0),
            "ec": events_dist.get("total", 0),
            "ecR": events_dist.get("abstract", 0),
            "ecS": events_dist.get("seal", 0),
            "ecE": events_dist.get("entry", 0),
            "ecN": events_dist.get("nota", 0),
        })

    collections_dict = {}
    for m in all_metadata:
        path_key = m.get("collection_path", "")
        if path_key not in collections_dict:
            collections_dict[path_key] = {
                "count": 0,
                "label": m.get("collection_label", path_key),
                "path": path_key,
            }
        collections_dict[path_key]["count"] += 1
    # List for the sidebar_corpus_chips macro: {key, label, count}
    collections = [
        {"key": path_key, "label": col["label"], "count": col["count"]}
        for path_key, col in sorted(
            collections_dict.items(),
            key=lambda kv: kv[1]["label"].lower(),
        )
    ]

    # --- Form-of-treatment chips: fixed order R/S/E/N/none ------------------
    # Counts are set client-side (faceted search). Icons are injected via
    # JS from FORM_ICONS (see index.js), not declared in the markup, so that
    # icons live centrally as a single source of truth.
    form_data = [
        {"key": "R",    "label": "Regest",  "title": "Regest-Annotation"},
        {"key": "S",    "label": "Siegel",  "title": "Siegelbeschreibung"},
        {"key": "E",    "label": "Eintrag", "title": "Stadtbuch-Eintrag"},
        {"key": "N",    "label": "Nota",    "title": "Nota / Nachsatz"},
        {"key": "none", "label": "ohne",    "title": "Quelle ohne erkannte Erschließungsform"},
    ]

    decade_counts = Counter()
    all_years = []
    for m in all_metadata:
        year_str = m.get("date_iso", "")[:4]
        if year_str.isdigit():
            year = int(year_str)
            all_years.append(year)
            decade = (year // 10) * 10
            decade_counts[decade] += 1

    min_year = min(all_years) if all_years else RELEASED_PERIOD["min_year"]
    max_year = max(all_years) if all_years else max_year_with_extensions()
    min_year = max(min_year, RELEASED_PERIOD["min_year"])
    max_year = min(max_year, max_year_with_extensions())

    if decade_counts:
        min_decade = min(decade_counts.keys())
        max_decade = max(decade_counts.keys())
        timeline_data = [
            {"decade": d, "count": decade_counts.get(d, 0)}
            for d in range(min_decade, max_decade + 10, 10)
        ]
        max_count = max(decade_counts.values())
    else:
        timeline_data = []
        max_count = 1

    place_counts = Counter()
    for m in all_metadata:
        if m.get("place"):
            place_counts[m["place"]] += 1
    top_places = place_counts.most_common(15)

    facs_count = sum(1 for m in all_metadata if m.get("has_facsimile"))

    reg = register_counts or {}

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "search.json").write_text(
        json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
    )

    template = env.get_template("index.html")
    html = template.render(
        documents=all_metadata,
        total_count=len(all_metadata),
        collections=collections,
        form_data=form_data,
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        top_places=top_places,
        facs_count=facs_count,
        person_register_count=reg.get("persons", 0),
        org_register_count=reg.get("orgs", 0),
        place_register_count=reg.get("places", 0),
        root_path=".",
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "documents.html").write_text(html, encoding="utf-8")
    print(f"  Documents page: {len(all_metadata)} documents")


# ---------------------------------------------------------------------------
# Landing page (index.html)
# ---------------------------------------------------------------------------


def _build_startseite(all_metadata, persons, orgs, places, collections, env):
    """Build the portal landing page (index.html)."""
    kpis = _compute_release_kpis()
    corpus_rows = _compute_corpus_breakdown()
    total_docs = kpis["sources_total"]
    total_persons = kpis["distinct_persons"]
    total_mentions = kpis["person_mentions"]
    total_events = kpis["distinct_events"]
    register_total = kpis["register_total"]
    matrix_columns = _compute_matrix_columns(total_docs, total_mentions, total_events)
    total_orgs = len(orgs)
    total_places = len(places)
    released_person_keys = _released_person_keys()
    sex_m = sum(1 for pid, p in persons.items()
                if pid in released_person_keys and p.get("sex") == "m")
    sex_f = sum(1 for pid, p in persons.items()
                if pid in released_person_keys and p.get("sex") == "f")

    template = env.get_template("startseite.html")
    html = template.render(
        total_docs=total_docs,
        total_persons=total_persons,
        total_mentions=total_mentions,
        total_events=total_events,
        register_total=register_total,
        total_orgs=total_orgs,
        total_places=total_places,
        sex_m=sex_m,
        sex_f=sex_f,
        collection_count=len(collections),
        collections=collections,
        corpus_rows=corpus_rows,
        matrix_columns=matrix_columns,
        build_date=_format_german_date(date.today()),
        root_path=".",
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print("  Startseite: index.html")


# ---------------------------------------------------------------------------
# Register pages (persons)
# ---------------------------------------------------------------------------


def _person_search_data(persons, reverse_index, released_keys=None,
                        person_roles=None):
    """Build compact JSON list for the persons register page.

    Restricted to the released set (persons appearing as rs-person in at
    least one released source); a person without sources does not show up
    here. Fields per entry:

    - ``id`` xml:id (e.g. ``pe__katharina_QGW_II_I_66``).
    - ``n`` / ``fn`` / ``sn``  display name + components for search.
    - ``sex``  ``m`` | ``f`` | ``""``.
    - ``dc``  number of released sources mentioning the person (>=1 by
      construction).
    - ``am`` / ``ax``  activity range as year strings (e.g. ``"1340"``);
      ``am == ax`` for a single-year occurrence.
    - ``co``  list of collection_path keys in which the person appears.
    - ``i0`` / ``cl0``  idno and short label of the first (chronologically
      earliest) source — anchor for the sub-label below the name.
    - ``rl``  sorted list of event_role values (issuer/recipient/
      witness/other), only roles that actually occur.
    """
    data = []
    person_roles = person_roles or {}
    for xml_id, p in persons.items():
        if released_keys is not None and xml_id not in released_keys:
            continue
        docs = reverse_index.get(xml_id, [])
        if not docs:
            # Defensive: released_keys guarantees dc>=1, but if a register
            # entry exists without any source link we drop it — the UI no
            # longer handles dc==0.
            continue

        years = []
        for d in docs:
            di = (d.get("date_iso") or "")[:4]
            if di.isdigit():
                years.append(di)
        am = min(years) if years else ""
        ax = max(years) if years else ""

        corpora = sorted({d.get("collection_path", "") for d in docs
                          if d.get("collection_path")})

        first = docs[0]
        i0 = first.get("idno", "")
        cl0 = _short_collection_label(first.get("collection_path", ""))

        roles = sorted(person_roles.get(xml_id, set()))

        data.append({
            "id": xml_id,
            "n": p["display"],
            "fn": p["forename"],
            "sn": p["surname"],
            "sex": p["sex"],
            "dc": len(docs),
            "am": am,
            "ax": ax,
            "co": corpora,
            "i0": i0,
            "cl0": cl0,
            "rl": roles,
        })
    data.sort(key=lambda x: x["n"].lower())
    return data


def _entity_doc_aggregates(docs):
    """Common per-entity aggregates for register search-data rows.

    Returns (am, ax, corpora, i0, cl0) computed from the reverse-index
    document list. Reused by orgs and places so the search rows mirror
    the persons row shape and the JS register page can apply the same
    timeline / corpus filters.
    """
    years = []
    for d in docs:
        di = (d.get("date_iso") or "")[:4]
        if di.isdigit():
            years.append(di)
    am = min(years) if years else ""
    ax = max(years) if years else ""
    corpora = sorted({d.get("collection_path", "") for d in docs
                      if d.get("collection_path")})
    first = docs[0] if docs else {}
    i0 = first.get("idno", "")
    cl0 = _short_collection_label(first.get("collection_path", ""))
    return am, ax, corpora, i0, cl0


def _org_search_data(orgs, reverse_index):
    """Compact JSON list for the organisations register page.

    Restricted to orgs with at least one released mention. Fields mirror
    the person row shape so register.js can reuse search / sort / chip
    infrastructure unchanged: ``n``, ``id``, ``tp`` (type), ``dc``,
    ``am`` / ``ax`` (activity range), ``co`` (corpora), ``i0`` / ``cl0``.
    """
    data = []
    for xml_id, o in orgs.items():
        docs = reverse_index.get(xml_id, [])
        if not docs:
            continue
        am, ax, corpora, i0, cl0 = _entity_doc_aggregates(docs)
        data.append({
            "id": xml_id,
            "n":  o["name"],
            "tp": o["type"],
            "dc": len(docs),
            "am": am,
            "ax": ax,
            "co": corpora,
            "i0": i0,
            "cl0": cl0,
        })
    data.sort(key=lambda x: x["n"].lower())
    return data


def _build_register_list_pages(persons, orgs, places, reverse_index, env):
    """Build the persons and organisations register pages.

    Each register reads from its own search-data list (persons_search.json,
    orgs_search.json). Both pages share the same template
    ``register_list.html``; sidebar facets are toggled by
    ``register_type``. Places are no register page — the underlying
    master data is not yet consolidated. ``places`` is kept in the
    signature so callers stay stable; the dict is not consumed here.
    """
    del places  # places register intentionally omitted
    _build_persons_register(persons, reverse_index, env)
    _build_orgs_register(orgs, reverse_index, env)


def _build_persons_register(persons, reverse_index, env):
    """Persons register page + persons_search.json.

    Provides the template with all data required by the sidebar filters (sex,
    role, activity-range histogram, source corpus). Counts are pre-computed
    here so that the table can render without an initial JS aggregation pass.
    """
    template = env.get_template("register_list.html")
    released_person_keys = _released_person_keys()
    person_roles = _load_person_roles(released_person_keys)

    out = DOCS_DIR / "register" / "persons.html"
    out.parent.mkdir(parents=True, exist_ok=True)

    search_data = _person_search_data(
        persons, reverse_index,
        released_keys=released_person_keys,
        person_roles=person_roles,
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "persons_search.json").write_text(
        json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
    )

    # --- Sex chips: m/f/u with counts ---------------------------------------
    sex_counts = Counter()
    for row in search_data:
        sex_counts[row["sex"] or "u"] += 1
    sex_data = [
        {"key": "m", "label": "Männlich",  "count": sex_counts.get("m", 0)},
        {"key": "f", "label": "Weiblich",  "count": sex_counts.get("f", 0)},
        {"key": "u", "label": "Unbekannt", "count": sex_counts.get("u", 0)},
    ]
    sex_data = [s for s in sex_data if s["count"] > 0]

    # --- Role chips ---------------------------------------------------------
    role_counts = Counter()
    for row in search_data:
        for r in row["rl"]:
            role_counts[r] += 1
    ROLE_LABELS = {
        "issuer":    "Aussteller",
        "recipient": "Empfänger",
        "witness":   "Zeuge / Siegler",
        "other":     "Sonstige",
    }
    # Sidebar chips show only label + count — analogous to the
    # form-of-treatment chips on the sources page. Icon differentiation
    # happens in the table pills (see register.js ROLE_ICONS).
    role_data = []
    for key in PERSON_ROLES:
        c = role_counts.get(key, 0)
        if c > 0:
            role_data.append({
                "key":   key,
                "label": ROLE_LABELS[key],
                "count": c,
            })

    # --- Corpus chips -------------------------------------------------------
    corpus_counts = Counter()
    for row in search_data:
        for c in row["co"]:
            corpus_counts[c] += 1
    corpora_data = []
    for path_key, count in sorted(
        corpus_counts.items(),
        key=lambda kv: COLLECTION_LABELS.get(kv[0], kv[0]).lower(),
    ):
        corpora_data.append({
            "key":   path_key,
            "label": COLLECTION_LABELS.get(path_key, path_key),
            "count": count,
        })

    # --- Activity range: histogram per decade -------------------------------
    decade_counts = Counter()
    all_years = []
    for row in search_data:
        am = row["am"]
        ax = row["ax"]
        if not am.isdigit():
            continue
        ymin = int(am)
        ymax = int(ax) if ax.isdigit() else ymin
        all_years.extend([ymin, ymax])
        # A person is counted in every decade their range overlaps — not
        # only am_min — otherwise we lose persons with a long span from
        # later decades. (Same logic as for sources, except each source
        # has a single point-in-time date.)
        d_min = (ymin // 10) * 10
        d_max = (ymax // 10) * 10
        for dec in range(d_min, d_max + 10, 10):
            decade_counts[dec] += 1

    min_year = min(all_years) if all_years else RELEASED_PERIOD["min_year"]
    max_year = max(all_years) if all_years else max_year_with_extensions()
    min_year = max(min_year, RELEASED_PERIOD["min_year"])

    # Gap-free decade list between min_decade and max_decade
    min_decade = (min_year // 10) * 10
    max_decade = (max_year // 10) * 10
    max_count = max(decade_counts.values()) if decade_counts else 1
    timeline_data = [
        {"decade": d, "count": decade_counts.get(d, 0)}
        for d in range(min_decade, max_decade + 10, 10)
    ]

    html = template.render(
        register_type="persons",
        register_label="Personen",
        total_count=len(search_data),
        sex_data=sex_data,
        role_data=role_data,
        corpora_data=corpora_data,
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        root_path="..",
    )

    out.write_text(html, encoding="utf-8")
    print(f"  Register list: register/persons.html ({len(search_data)} entries)")


# ---------------------------------------------------------------------------
# Shared helpers for the orgs and places list pages
# ---------------------------------------------------------------------------


def _type_chip_data(search_data):
    """Build chip data for the ``tp`` (type) facet on orgs/places.

    Aggregates counts per distinct ``tp`` value. Empty values are bucketed
    under the literal key ``""`` and rendered as "ohne Angabe".
    """
    counts = Counter()
    for row in search_data:
        counts[row.get("tp") or ""] += 1
    out = []
    for key, c in counts.most_common():
        if c <= 0:
            continue
        out.append({
            "key":   key,
            "label": key or "ohne Angabe",
            "count": c,
        })
    return out


def _corpus_chip_data(search_data):
    """Build chip data for the corpus facet (same shape as for persons)."""
    corpus_counts = Counter()
    for row in search_data:
        for c in row.get("co", []):
            corpus_counts[c] += 1
    out = []
    for path_key, count in sorted(
        corpus_counts.items(),
        key=lambda kv: COLLECTION_LABELS.get(kv[0], kv[0]).lower(),
    ):
        out.append({
            "key":   path_key,
            "label": COLLECTION_LABELS.get(path_key, path_key),
            "count": count,
        })
    return out


def _timeline_buckets(search_data):
    """Per-decade counts for the activity-range histogram.

    Returns (timeline_data, max_count, min_year, max_year). Mirrors the
    persons-side aggregation so the slider behaves identically on all
    three registers.
    """
    decade_counts = Counter()
    all_years = []
    for row in search_data:
        am = row.get("am", "")
        ax = row.get("ax", "")
        if not am.isdigit():
            continue
        ymin = int(am)
        ymax = int(ax) if ax.isdigit() else ymin
        all_years.extend([ymin, ymax])
        d_min = (ymin // 10) * 10
        d_max = (ymax // 10) * 10
        for dec in range(d_min, d_max + 10, 10):
            decade_counts[dec] += 1
    min_year = min(all_years) if all_years else RELEASED_PERIOD["min_year"]
    max_year = max(all_years) if all_years else max_year_with_extensions()
    min_year = max(min_year, RELEASED_PERIOD["min_year"])
    min_decade = (min_year // 10) * 10
    max_decade = (max_year // 10) * 10
    max_count = max(decade_counts.values()) if decade_counts else 1
    timeline_data = [
        {"decade": d, "count": decade_counts.get(d, 0)}
        for d in range(min_decade, max_decade + 10, 10)
    ]
    return timeline_data, max_count, min_year, max_year


# ---------------------------------------------------------------------------
# Orgs and places list pages
# ---------------------------------------------------------------------------


def _build_orgs_register(orgs, reverse_index, env):
    """Organisations register page + orgs_search.json.

    Sidebar facets: source corpus, activity timeline, type. No sex / no
    role chips (persons-only). Pre-computes the counts so the table can
    render before the JS aggregation kicks in.
    """
    template = env.get_template("register_list.html")
    search_data = _org_search_data(orgs, reverse_index)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "orgs_search.json").write_text(
        json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
    )

    type_data = _type_chip_data(search_data)
    corpora_data = _corpus_chip_data(search_data)
    timeline_data, max_count, min_year, max_year = _timeline_buckets(search_data)

    html = template.render(
        register_type="orgs",
        register_label="Organisationen",
        total_count=len(search_data),
        sex_data=[],
        role_data=[],
        type_data=type_data,
        corpora_data=corpora_data,
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        root_path="..",
    )

    out = DOCS_DIR / "register" / "orgs.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  Register list: register/orgs.html ({len(search_data)} entries)")


def _build_register_json(reverse_index):
    """Write reverse-index data as JSON files for client-side detail views.

    Persons are restricted to the released set from
    ``_released_person_keys()``: only persons appearing at least once as
    ``<rs type="person">`` in a released source end up in
    ``register/persons.json``. Pure ``@corresp`` auxiliary links do not
    count as a mention.
    """
    out_dir = DOCS_DIR / "register"
    out_dir.mkdir(parents=True, exist_ok=True)

    released_persons = _released_person_keys()

    buckets = {"persons": {}, "organisations": {}}
    for eid, docs in reverse_index.items():
        if eid.startswith("pe__"):
            if eid not in released_persons:
                continue
            bucket = "persons"
        elif eid.startswith("org__"):
            bucket = "organisations"
        else:
            # pl__ and anything else: no register JSON; place register
            # has been removed.
            continue
        buckets[bucket][eid] = [
            {"u": d["url"], "i": d["idno"], "d": d["date_display"],
             "c": d["collection_label"], "r": d["regest"]}
            for d in docs
        ]

    for name, data in buckets.items():
        out = out_dir / f"{name}.json"
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"  Register JSON: {name}.json ({len(data)} entities)")


# ---------------------------------------------------------------------------
# Person-Profile (docs/register/persons/<pe__id>.html)
# ---------------------------------------------------------------------------


def _build_person_profiles(reverse_index, env, linked_orgs=None):
    """Render one profile page per person in the released corpora.

    Source: ``frontend.aggregator.build_person_profiles`` returns the
    fully aggregated profile per pe__-id (master data, sources, roles,
    relations). Here the list is rendered into individual HTML files.

    ``linked_orgs`` carries the IDs that have a dedicated detail page so
    the ``occ`` / ``title_ref`` rows can link to the org profile when
    one was built. Places have no detail page; place references in
    owner/tenant rows render as plain text.
    """
    from frontend.aggregator import build_person_profiles

    profiles = build_person_profiles(reverse_index)
    if not profiles:
        print("  Person profiles: keine Personen — skip")
        return set()

    template = env.get_template("person.html")
    out_dir = DOCS_DIR / "register" / "persons"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    linked_persons = set(profiles.keys())
    linked_orgs = linked_orgs or set()

    for pid, profile in profiles.items():
        html = template.render(
            profile=profile,
            linked_persons=linked_persons,
            linked_orgs=linked_orgs,
            root_path="../..",
        )
        (out_dir / f"{pid}.html").write_text(html, encoding="utf-8")

    print(f"  Person profiles: {len(profiles)} Profile in register/persons/")
    return linked_persons


# ---------------------------------------------------------------------------
# Org-Profile (docs/register/orgs/<org__id>.html)
# ---------------------------------------------------------------------------


def _build_org_profiles(reverse_index, env, linked_persons=None):
    """Render one profile page per organisation with a released mention.

    Mirrors ``_build_person_profiles``. The aggregator
    ``build_org_profiles`` returns the per-org dict (master data,
    sources, event roles, person-side relations occ / title_ref).
    Returns the set of org IDs with a profile (used by other builders
    to gate org-links). Places have no detail page; the ``Standort``
    label on the org profile renders as plain text.
    """
    from frontend.aggregator import build_org_profiles

    profiles = build_org_profiles(reverse_index)
    if not profiles:
        print("  Org profiles: keine Organisationen — skip")
        return set()

    template = env.get_template("org.html")
    out_dir = DOCS_DIR / "register" / "orgs"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    linked_orgs = set(profiles.keys())
    linked_persons = linked_persons or set()

    for oid, profile in profiles.items():
        html = template.render(
            profile=profile,
            linked_orgs=linked_orgs,
            linked_persons=linked_persons,
            root_path="../..",
        )
        (out_dir / f"{oid}.html").write_text(html, encoding="utf-8")

    print(f"  Org profiles: {len(profiles)} Profile in register/orgs/")
    return linked_orgs


# ---------------------------------------------------------------------------
# Auswertungen (statistics section under /analysis/)
# ---------------------------------------------------------------------------


def _build_exploration(all_metadata, persons, env):
    """Build the Auswertungen page (analysis/auswertungen.html) — one
    page with four aggregate sections: function roles (donut), relation
    types (donut), transaction types (bar chart) and labels (table with
    mini bars). Sidebar: time range + sex.

    Lives under /analysis/ because it shows quantitative analyses
    (statistical distributions), not visual exploration — see
    knowledge/specification.md "Auswertungen gehoert in den Analyse-Bereich".
    Previously three separate sub-pages (roles/networks/transactions)
    under /exploration/, then merged into /exploration/auswertungen.html,
    finally moved to /analysis/.
    """
    roles_path = DATA_DIR / "roles.json"
    relations_path = DATA_DIR / "relations.json"
    transactions_path = DATA_DIR / "transactions.json"
    if not roles_path.exists():
        print("  WARN: roles.json not found, skipping Auswertungen.",
              file=sys.stderr)
        return

    kpis = _compute_release_kpis()
    released_persons = _released_person_keys()

    total_docs = len(all_metadata)
    total_persons = kpis["distinct_persons"]
    total_events = kpis["distinct_events"]
    total_mentions = kpis["person_mentions"]

    sex_m = sum(1 for pid, p in persons.items()
                if pid in released_persons and p.get("sex") == "m")
    sex_f = sum(1 for pid, p in persons.items()
                if pid in released_persons and p.get("sex") == "f")
    sex_u = total_persons - sex_m - sex_f

    # --- Sidebar data: time-range slider + corpus chips ---------------------
    decade_counts = Counter()
    all_years = []
    for m in all_metadata:
        year_str = (m.get("date_iso") or "")[:4]
        if year_str.isdigit():
            year = int(year_str)
            all_years.append(year)
            decade_counts[(year // 10) * 10] += 1
    if all_years:
        min_year = max(min(all_years), RELEASED_PERIOD["min_year"])
        max_year = min(max(all_years), max_year_with_extensions())
    else:
        min_year = RELEASED_PERIOD["min_year"]
        max_year = max_year_with_extensions()
    if decade_counts:
        min_dec = min(decade_counts.keys())
        max_dec = max(decade_counts.keys())
        timeline_data = [{"decade": d, "count": decade_counts.get(d, 0)}
                         for d in range(min_dec, max_dec + 10, 10)]
        max_count = max(decade_counts.values())
    else:
        timeline_data = []
        max_count = 1

    collections_dict = {}
    for m in all_metadata:
        path_key = m.get("collection_path", "")
        if not path_key:
            continue
        c = collections_dict.setdefault(path_key, {
            "count": 0,
            "label": m.get("collection_label", path_key),
            "path": path_key,
        })
        c["count"] += 1
    collections = [
        {"key": k, "label": col["label"], "count": col["count"]}
        for k, col in sorted(collections_dict.items(),
                             key=lambda kv: kv[1]["label"].lower())
    ]

    sex_data = [
        {"key": "all", "label": "alle", "count": total_persons},
        {"key": "m", "label": "♂ männlich", "count": sex_m},
        {"key": "f", "label": "♀ weiblich", "count": sex_f},
        {"key": "unspecified", "label": "ohne Angabe", "count": sex_u},
    ]

    # --- Corpus label for the as-of-date banner ----------------------------
    released_corpora_label = " · ".join(
        _short_collection_label(p) for p in collections_dict.keys()
    ) if collections_dict else "alle Korpora"

    # --- JSON payloads (raw text, in <script type="application/json">) -----
    roles_json = roles_path.read_text(encoding="utf-8")
    relations_json = (relations_path.read_text(encoding="utf-8")
                   if relations_path.exists() else "{}")
    transactions_json = (transactions_path.read_text(encoding="utf-8")
                   if transactions_path.exists() else "{}")

    analysis_dir = DOCS_DIR / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    html = env.get_template("analysis_aggregat.html").render(
        build_date=_format_german_date(date.today()),
        total_docs=total_docs,
        total_persons=total_persons,
        total_mentions=total_mentions,
        total_events=total_events,
        sex_m=sex_m,
        sex_f=sex_f,
        sex_u=sex_u,
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        collections=collections,
        sex_data=sex_data,
        released_corpora_label=released_corpora_label,
        roles_json=roles_json,
        relations_json=relations_json,
        transactions_json=transactions_json,
        root_path="..",
    )
    (analysis_dir / "auswertungen.html").write_text(html, encoding="utf-8")
    print("  Auswertungen: analysis/auswertungen.html")


# ---------------------------------------------------------------------------
# Knowledge basket page (client-side collection, persisted in localStorage).
# UI label "Datenkorb" stays German; code-side symbols use English ("basket").
# ---------------------------------------------------------------------------


def _build_basket(env):
    """Build the basket page (korb.html). Pure front-shell without any
    server-side data — the collection lives client-side in localStorage,
    is managed by basket.js and rendered on the page via basket-page.js."""
    html = env.get_template("korb.html").render(
        build_date=_format_german_date(date.today()),
        root_path=".",
    )
    (DOCS_DIR / "korb.html").write_text(html, encoding="utf-8")
    print("  Basket: korb.html")


# ---------------------------------------------------------------------------
# Exploration / Zeitstrom (visual-interactive sub-page under /exploration/)
# ---------------------------------------------------------------------------


def _build_exploration_timeline(all_metadata, env):
    """Build the Zeitstrom page (exploration/zeitstrom.html) — stacked
    bar chart of source density per decade with brush-to-drill-down.
    Stack axis selectable (corpus / form of treatment / sex / transaction
    type). Reads search.json client-side for the first three axes,
    transactions.json for the transaction-type stacking.

    Lives under /exploration/ because it is visual-interactive exploration
    of the data structure (not a distribution display) — see knowledge/
    specification.md "Exploration und Analyse als getrennte Bereiche".
    """
    transactions_path = DATA_DIR / "transactions.json"

    # Sidebar data: time-range slider with histogram of sources per decade
    decade_counts = Counter()
    all_years = []
    for m in all_metadata:
        year_str = (m.get("date_iso") or "")[:4]
        if year_str.isdigit():
            year = int(year_str)
            all_years.append(year)
            decade_counts[(year // 10) * 10] += 1
    if all_years:
        min_year = max(min(all_years), RELEASED_PERIOD["min_year"])
        max_year = min(max(all_years), max_year_with_extensions())
    else:
        min_year = RELEASED_PERIOD["min_year"]
        max_year = max_year_with_extensions()
    if decade_counts:
        min_dec = min(decade_counts.keys())
        max_dec = max(decade_counts.keys())
        timeline_data = [{"decade": d, "count": decade_counts.get(d, 0)}
                         for d in range(min_dec, max_dec + 10, 10)]
        max_count = max(decade_counts.values())
    else:
        timeline_data = []
        max_count = 1

    transactions_json = (transactions_path.read_text(encoding="utf-8")
                   if transactions_path.exists() else "{}")

    explore_dir = DOCS_DIR / "exploration"
    explore_dir.mkdir(parents=True, exist_ok=True)

    html = env.get_template("exploration_timeline.html").render(
        build_date=_format_german_date(date.today()),
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        transactions_json=transactions_json,
        root_path="..",
    )
    (explore_dir / "zeitstrom.html").write_text(html, encoding="utf-8")
    print("  Zeitstrom: exploration/zeitstrom.html")


def _build_exploration_network(env):
    """Build the Personennetzwerk page (exploration/personennetzwerk.html).
    Ego layout around one person, source relations.json::persons with the
    extended rels (related_key). Page is data-driven: the embedded JSON
    is the sole data source, no on-demand person loading.
    """
    relations_path = DATA_DIR / "relations.json"
    relations_json = (relations_path.read_text(encoding="utf-8")
                   if relations_path.exists() else "{}")

    explore_dir = DOCS_DIR / "exploration"
    explore_dir.mkdir(parents=True, exist_ok=True)

    html = env.get_template("exploration_network.html").render(
        build_date=_format_german_date(date.today()),
        relations_json=relations_json,
        root_path="..",
    )
    (explore_dir / "personennetzwerk.html").write_text(html, encoding="utf-8")
    print("  Personennetzwerk: exploration/personennetzwerk.html")


# ---------------------------------------------------------------------------
# Static Markdown pages (about, glossary, guidelines, impressum)
# ---------------------------------------------------------------------------


def _sync_guidelines_copy():
    """Synchronise local guidelines copy from the canonical pipeline source.

    Die kanonische Quelle liegt im Schwester-Repo unter
    ``edition_guidelines.md``; die lokale Kopie unter
    ``frontend/content/project/edition-guidelines.md`` ist die Quelle fuer den
    Build. Diese Funktion kopiert die kanonische Quelle in die lokale Datei,
    wenn sie neuer ist (mtime-Vergleich) oder die lokale Kopie fehlt.

    Wenn die kanonische Quelle nicht erreichbar ist (Schwester-Repo nicht
    geklont), bleibt die lokale Kopie unveraendert. Der Build laeuft dann
    gegen den letzten gesyncten Stand.
    """
    canonical = EDITION_GUIDELINES_CANONICAL
    local = EDITION_GUIDELINES_PATH

    if not canonical.exists():
        if not local.exists():
            print("  WARN: edition_guidelines.md weder kanonisch noch lokal "
                  "vorhanden, skip guidelines sync.", file=sys.stderr)
        return

    local.parent.mkdir(parents=True, exist_ok=True)

    needs_copy = (
        not local.exists()
        or canonical.stat().st_mtime > local.stat().st_mtime
    )
    if not needs_copy:
        return

    import shutil
    shutil.copy2(canonical, local)
    print(f"  Guidelines sync: {canonical.name} -> content/project/edition-guidelines.md")


def _build_guidelines(env):
    """Build annotation guidelines page from Markdown source.

    Die kanonische Quelle liegt im Schwester-Repo; die lokale Kopie unter
    ``frontend/content/project/edition-guidelines.md`` wird durch
    ``_sync_guidelines_copy`` aktualisiert.
    """
    _sync_guidelines_copy()

    md_path = EDITION_GUIDELINES_PATH
    if not md_path.exists():
        print("  WARN: edition_guidelines.md not found, skipping guidelines page.",
              file=sys.stderr)
        return

    _render_content_page(
        env,
        md_source=md_path.read_text(encoding="utf-8"),
        page_title="Annotationsrichtlinien",
        page_subtitle="Annotationsmodell, Tagging-Workflow und Konventionen.",
        out_path=DOCS_DIR / "project" / "edition-guidelines.html",
        root_path="..",
    )
    print("  Guidelines page: project/edition-guidelines.html")


def _build_about(env):
    """Build about page from Markdown source."""
    md_path = CONTENT_DIR / "project" / "about.md"
    if not md_path.exists():
        print("  WARN: about.md not found, skipping about page.",
              file=sys.stderr)
        return

    _render_content_page(
        env,
        md_source=md_path.read_text(encoding="utf-8"),
        page_title="Über das Projekt",
        page_subtitle="Prosopographische Datenbank mittelalterlicher Wiener Rechtsgeschäfte.",
        out_path=DOCS_DIR / "project" / "about.html",
        root_path="..",
    )
    print("  About page: project/about.html")


def _slug_anchor(text):
    """Slug a German term to a URL-safe anchor (used by wiki-link rewriter)."""
    s = text.strip().lower()
    s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("-")
    return "".join(out).strip("-")


def _strip_frontmatter(md_source):
    """Entfernt YAML-Frontmatter zwischen --- ... --- (falls vorhanden)."""
    return _re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", md_source, count=1, flags=_re.DOTALL)


def _strip_leading_h1(md_source):
    """Entfernt das erste Markdown-H1, falls es ganz oben steht.

    Das Page-Header-H1 wird vom Template gesetzt; ein zusaetzliches H1 in der
    Quelle ergaebe ein doppeltes H1.
    """
    return _re.sub(r"\A\s*#\s+[^\n]+\r?\n", "", md_source, count=1)


def _rewrite_wiki_links(md_source):
    """Wiki-Links in Markdown umwandeln.

    [[#Term]]              -> [Term](#term-slug)
    [[#Term|Label]]        -> [Label](#term-slug)
    [[doc#anchor]]         -> *anchor*   (Zieldokument liegt ausserhalb)
    [[doc#anchor|Label]]   -> *Label*
    [[doc]]                -> *doc*
    [[doc|Label]]          -> *Label*
    """
    def _replace(match):
        target = match.group(1)
        label_override = None
        if "|" in target:
            target, _sep, label_override = target.partition("|")
        if target.startswith("#"):
            label = label_override or target[1:]
            return f"[{label}](#{_slug_anchor(target[1:])})"
        if "#" in target:
            doc, _sep, anchor = target.partition("#")
            text = label_override or anchor or doc
            return f"*{text}*"
        return f"*{label_override or target}*"

    return _re.sub(r"\[\[([^\]]+)\]\]", _replace, md_source)


def _render_content_page(env, *, md_source, page_title, page_subtitle,
                        out_path, root_path, template_name="about.html"):
    """Render eine Inhaltsseite aus Markdown auf das about.html-Geruest.

    Einheitliche Pipeline fuer Glossar, Impressum und vergleichbare Seiten:
    Frontmatter raus, fuehrendes Markdown-H1 raus, Wiki-Links umschreiben,
    Markdown rendern, Template einsetzen, Datei schreiben.
    """
    md_source = _strip_frontmatter(md_source)
    md_source = _strip_leading_h1(md_source)
    md_source = _rewrite_wiki_links(md_source)

    md = _create_markdown_processor()
    content_html = md.convert(md_source)
    toc_html = md.toc

    template = env.get_template(template_name)
    html = template.render(
        content=content_html,
        toc=toc_html,
        build_date=_format_german_date(date.today()),
        root_path=root_path,
        page_title=page_title,
        page_subtitle=page_subtitle,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def _build_glossary(env):
    """Build glossary page from frontend/content/project/glossar.md."""
    md_path = CONTENT_DIR / "project" / "glossar.md"
    if not md_path.exists():
        print("  WARN: glossar.md nicht gefunden, skip glossary.",
              file=sys.stderr)
        return

    _render_content_page(
        env,
        md_source=md_path.read_text(encoding="utf-8"),
        page_title="Glossar",
        page_subtitle="Kanonische Definitionen aller Fachbegriffe der Datenbank.",
        out_path=DOCS_DIR / "project" / "glossary.html",
        root_path="..",
    )
    print("  Glossary page: project/glossary.html")


def _build_impressum(env):
    """Build impressum page from Markdown source."""
    md_path = CONTENT_DIR / "impressum.md"
    if not md_path.exists():
        print("  WARN: impressum.md not found, skipping.", file=sys.stderr)
        return

    _render_content_page(
        env,
        md_source=md_path.read_text(encoding="utf-8"),
        page_title="Impressum",
        page_subtitle="Lizenz, Verantwortliche, Datenquellen, Zitierweise.",
        out_path=DOCS_DIR / "impressum.html",
        root_path=".",
    )
    print("  Impressum page: impressum.html")


# ---------------------------------------------------------------------------
# Analysis page + vocabulary and categories JSON
# ---------------------------------------------------------------------------


def _write_categories():
    """Copy categories.json from content/ to docs/data/, with build metadata.

    The source file lives in `frontend/content/categories.json` and is the
    versioned editorial mapping `org_type -> category` (geistlich/weltlich/
    sonstige). It is validated against the org-type list in roles.json so
    that the pipeline cannot silently introduce types that the editorial
    classification does not yet cover.
    """
    src = CONTENT_DIR / "categories.json"
    if not src.exists():
        print("  WARN: categories.json not found, skipping.", file=sys.stderr)
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    data.setdefault("meta", {})["created"] = date.today().isoformat()

    roles_path = DATA_DIR / "roles.json"
    if roles_path.exists():
        try:
            roles = json.loads(roles_path.read_text(encoding="utf-8"))
            real_types = set(roles.get("observations", {}).get("org_type_totals", {}).keys())
            mapped_types = {t for ts in data.get("categories", {}).values() for t in ts}
            missing = real_types - mapped_types
            extra = mapped_types - real_types
            if missing:
                print(f"  WARN: org types in roles.json not classified: {sorted(missing)}", file=sys.stderr)
            if extra:
                print(f"  WARN: classified types not in roles.json: {sorted(extra)}", file=sys.stderr)
        except (json.JSONDecodeError, OSError):
            pass

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "categories.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  Categories: data/categories.json")


def _write_query_vocabulary():
    """Copy query_vocabulary.json from content/ to docs/data/.

    Vocabulary for the sentence builder of the analysis page. Provides
    subjects, filters, value lists with verb phrases, groupings and
    aggregations.
    """
    src = CONTENT_DIR / "query_vocabulary.json"
    if not src.exists():
        print("  WARN: query_vocabulary.json not found, skipping.", file=sys.stderr)
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    data.setdefault("meta", {})["created"] = date.today().isoformat()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "query_vocabulary.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  Query vocabulary: data/query_vocabulary.json")


def _build_analysis(env):
    """Build analysis/index.html. Pulls totals + vocab from role_constellation.json.
    Syncs analysis.css so single-page rebuilds don't leave an outdated CSS in docs/.
    """
    assets_version = datetime.now().strftime("%Y%m%d%H%M%S")

    import shutil
    from frontend.config import STATIC_DIR
    src_css = STATIC_DIR / "css" / "analysis.css"
    dst_css = DOCS_DIR / "static" / "css" / "analysis.css"
    if src_css.exists():
        dst_css.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_css, dst_css)

    rc_path = DATA_DIR / "role_constellation.json"
    if rc_path.exists():
        with open(rc_path, encoding="utf-8") as f:
            rc = json.load(f)
        rc_coverage = rc.get("coverage", {})
        rc_vocab = rc.get("vocab", {})
    else:
        print("  WARN: role_constellation.json not found, using zero placeholders.",
              file=sys.stderr)
        rc_coverage, rc_vocab = {}, {}

    # Histogram + corpus counts come from the constellation aggregate, so
    # the slider and the corpus chips reflect the actual data the page
    # queries against — no hardcoded mocks in the template.
    decade_histogram = rc_coverage.get("decade_histogram", [])
    if decade_histogram:
        max_count = max(b["count"] for b in decade_histogram) or 1
        min_year = decade_histogram[0]["decade"]
        # Last decade's range covers up to released max_year (e.g. 1410 -> 1414).
        max_year = max(b["decade"] for b in decade_histogram) + 9
        # Clamp to the released period bounds.
        min_year = max(min_year, RELEASED_PERIOD["min_year"])
        max_year = min(max_year, max_year_with_extensions())
    else:
        max_count = 1
        min_year = RELEASED_PERIOD["min_year"]
        max_year = max_year_with_extensions()

    # Corpus event counts: aggregator emits a short label ("QGW II/1",
    # "Stadtbuecher Bd. 1"); the chips show those literally — the
    # released-period suffix lives in the KPI strip instead.
    collections = [
        {"key": c["key"], "label": c["key"], "count": c["count"]}
        for c in rc_coverage.get("corpus_event_counts", [])
    ]

    template = env.get_template("analysis.html")
    html = template.render(
        build_date=_format_german_date(date.today()),
        root_path="..",
        assets_version=assets_version,
        total_sources=rc_coverage.get("total_sources", 0),
        total_events=rc_coverage.get("total_events", 0),
        total_persons=rc_coverage.get("total_persons", 0),
        occupation_vocab=rc_vocab.get("occupation", []),
        occupation_full_vocab=rc_vocab.get("occupation_full", []),
        uhlirz_vocab=rc_vocab.get("uhlirz", []),
        organisation_full_vocab=rc_vocab.get("organisation_full", []),
        organisation_vocab=rc_vocab.get("organisation", []),
        org_type_vocab=rc_vocab.get("org_type", []),
        timeline_data=decade_histogram,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        collections=collections,
    )
    out = DOCS_DIR / "analysis" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  Analysis page: analysis/index.html")
