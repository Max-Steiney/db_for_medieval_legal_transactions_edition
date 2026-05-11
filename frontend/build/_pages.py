"""Page builders: landing page, sources index, register, exploration,
analysis, static Markdown pages and smaller JSON outputs.

Consumes the KPI and helper modules; invokes Jinja templates and
writes HTML/JSON to docs/.
"""

import json
import re as _re
import sys
from collections import Counter
from datetime import date, datetime

from frontend.config import (
    DOCS_DIR, CONTENT_DIR, KNOWLEDGE_DIR, DATA_DIR,
    EDITION_GUIDELINES_PATH,
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
# see knowledge/decisions.md). Empty/`none` values are filtered out.
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


def _org_search_data(orgs, reverse_index):
    """Build compact JSON list for the organisations register page."""
    data = []
    for xml_id, o in orgs.items():
        data.append({
            "id": xml_id,
            "n": o["name"],
            "tp": o["type"],
            "dc": len(reverse_index.get(xml_id, [])),
        })
    data.sort(key=lambda x: x["n"].lower())
    return data


def _place_search_data(places, reverse_index):
    """Build compact JSON list for the places register page."""
    data = []
    for xml_id, p in places.items():
        data.append({
            "id": xml_id,
            "n": p["name"],
            "tp": p["type"],
            "lat": p["lat"],
            "lng": p["lng"],
            "dc": len(reverse_index.get(xml_id, [])),
        })
    data.sort(key=lambda x: x["n"].lower())
    return data


def _build_register_list_pages(persons, orgs, places, reverse_index, env):
    """Build the persons register page.

    Only the persons register is publicly released. Organisations and places
    remain unreleased.

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

    buckets = {"persons": {}, "organisations": {}, "places": {}}
    for eid, docs in reverse_index.items():
        if eid.startswith("pe__"):
            if eid not in released_persons:
                continue
            bucket = "persons"
        elif eid.startswith("org__"):
            bucket = "organisations"
        elif eid.startswith("pl__"):
            bucket = "places"
        else:
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


def _build_person_profiles(reverse_index, env):
    """Render one profile page per person in the released corpora.

    Source: ``frontend.aggregator.build_person_profiles`` returns the
    fully aggregated profile per pe__-id (master data, sources, roles,
    relations). Here the list is rendered into individual HTML files.

    Call path: after ``_build_register_json`` from build_all() — both
    live under ``docs/register/`` and share the linking convention
    ``register/persons/<id>.html``.
    """
    from frontend.aggregator import build_person_profiles

    profiles = build_person_profiles(reverse_index)
    if not profiles:
        print("  Person profiles: keine Personen — skip")
        return

    template = env.get_template("person.html")
    out_dir = DOCS_DIR / "register" / "persons"
    out_dir.mkdir(parents=True, exist_ok=True)

    linked_persons = set(profiles.keys())

    for pid, profile in profiles.items():
        html = template.render(
            profile=profile,
            linked_persons=linked_persons,
            root_path="../..",
        )
        (out_dir / f"{pid}.html").write_text(html, encoding="utf-8")

    print(f"  Person profiles: {len(profiles)} Profile in register/persons/")


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
    knowledge/decisions.md "Auswertungen gehoeren in den Analyse-Bereich".
    Previously three separate sub-pages (roles/networks/transactions)
    under /exploration/, then merged into /exploration/auswertungen.html,
    finally moved to /analysis/.
    """
    epic_a_path = DATA_DIR / "epic_a.json"
    epic_b_path = DATA_DIR / "epic_b.json"
    epic_c_path = DATA_DIR / "epic_c.json"
    if not epic_a_path.exists():
        print("  WARN: epic_a.json not found, skipping Auswertungen.",
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
    epic_a_json = epic_a_path.read_text(encoding="utf-8")
    epic_b_json = (epic_b_path.read_text(encoding="utf-8")
                   if epic_b_path.exists() else "{}")
    epic_c_json = (epic_c_path.read_text(encoding="utf-8")
                   if epic_c_path.exists() else "{}")

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
        epic_a_json=epic_a_json,
        epic_b_json=epic_b_json,
        epic_c_json=epic_c_json,
        root_path="..",
    )
    (analysis_dir / "auswertungen.html").write_text(html, encoding="utf-8")
    print("  Auswertungen: analysis/auswertungen.html")


# ---------------------------------------------------------------------------
# Wissenskorb page (client-side collection, persisted in localStorage)
# ---------------------------------------------------------------------------


def _build_korb(env):
    """Build the Wissenskorb page (korb.html). Pure front-shell without
    server-side data — the collection lives client-side in localStorage,
    is managed by wissenskorb.js and rendered on the page via
    korb-page.js."""
    html = env.get_template("korb.html").render(
        build_date=_format_german_date(date.today()),
        root_path=".",
    )
    (DOCS_DIR / "korb.html").write_text(html, encoding="utf-8")
    print("  Wissenskorb: korb.html")


# ---------------------------------------------------------------------------
# Exploration / Zeitstrom (visual-interactive sub-page under /exploration/)
# ---------------------------------------------------------------------------


def _build_exploration_timeline(all_metadata, env):
    """Build the Zeitstrom page (exploration/zeitstrom.html) — stacked
    bar chart of source density per decade with brush-to-drill-down.
    Stack axis selectable (corpus / form of treatment / sex / transaction
    type). Reads search.json client-side for the first three axes,
    epic_c.json for the transaction-type stacking.

    Lives under /exploration/ because it is visual-interactive exploration
    of the data structure (not a distribution display) — see knowledge/
    decisions.md "Exploration und Analyse als getrennte Bereiche".
    """
    epic_c_path = DATA_DIR / "epic_c.json"

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

    epic_c_json = (epic_c_path.read_text(encoding="utf-8")
                   if epic_c_path.exists() else "{}")

    explore_dir = DOCS_DIR / "exploration"
    explore_dir.mkdir(parents=True, exist_ok=True)

    html = env.get_template("exploration_timeline.html").render(
        build_date=_format_german_date(date.today()),
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        epic_c_json=epic_c_json,
        root_path="..",
    )
    (explore_dir / "zeitstrom.html").write_text(html, encoding="utf-8")
    print("  Zeitstrom: exploration/zeitstrom.html")


def _build_exploration_network(env):
    """Build the Personennetzwerk page (exploration/personennetzwerk.html).
    Ego layout around one person, source epic_b.json::persons with the
    extended rels (related_key). Page is data-driven: the embedded JSON
    is the sole data source, no on-demand person loading.
    """
    epic_b_path = DATA_DIR / "epic_b.json"
    epic_b_json = (epic_b_path.read_text(encoding="utf-8")
                   if epic_b_path.exists() else "{}")

    explore_dir = DOCS_DIR / "exploration"
    explore_dir.mkdir(parents=True, exist_ok=True)

    html = env.get_template("exploration_network.html").render(
        build_date=_format_german_date(date.today()),
        epic_b_json=epic_b_json,
        root_path="..",
    )
    (explore_dir / "personennetzwerk.html").write_text(html, encoding="utf-8")
    print("  Personennetzwerk: exploration/personennetzwerk.html")


# ---------------------------------------------------------------------------
# Static Markdown pages (about, glossary, guidelines, impressum)
# ---------------------------------------------------------------------------


def _build_guidelines(env):
    """Build edition guidelines page from Markdown source.

    The guidelines are editorial documentation of the annotation model
    for the source data; they live in the pipeline repository's root
    (`edition_guidelines.md`) rather than in the frontend's content/
    folder, because they describe the data, not the publication.
    """
    md_path = EDITION_GUIDELINES_PATH
    if not md_path.exists():
        print("  WARN: edition_guidelines.md not found, skipping guidelines page.",
              file=sys.stderr)
        return

    md_source = md_path.read_text(encoding="utf-8")

    md = _create_markdown_processor()

    content_html = md.convert(md_source)
    toc_html = md.toc

    template = env.get_template("guidelines.html")
    html = template.render(
        content=content_html,
        toc=toc_html,
        build_date=_format_german_date(date.today()),
        root_path="..",
    )

    out = DOCS_DIR / "project" / "edition-guidelines.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  Guidelines page: project/edition-guidelines.html")


def _build_about(env):
    """Build about page from Markdown source."""
    md_path = CONTENT_DIR / "about.md"
    if not md_path.exists():
        print("  WARN: about.md not found, skipping about page.",
              file=sys.stderr)
        return

    md_source = md_path.read_text(encoding="utf-8")

    md = _create_markdown_processor()

    content_html = md.convert(md_source)
    toc_html = md.toc

    template = env.get_template("about.html")
    html = template.render(
        content=content_html,
        toc=toc_html,
        build_date=_format_german_date(date.today()),
        root_path="..",
    )

    out = DOCS_DIR / "project" / "about.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  About page: project/about.html")


def _build_glossary(env):
    """Build glossary page from knowledge/glossar.md.

    Wiki links of the form [[#term]] become page-internal anchor links;
    [[document]] and [[document#anchor]] are kept as plain text
    (target pages live outside the edition).

    Source is preferably the edition repo (sibling path), otherwise
    KNOWLEDGE_DIR in the pipeline repo.
    """
    from pipeline.config import REPO_ROOT
    candidates = [
        REPO_ROOT.parent / "db_for_medieval_legal_transactions_edition" / "knowledge" / "glossar.md",
        KNOWLEDGE_DIR / "glossar.md",
    ]
    md_path = next((p for p in candidates if p.exists()), None)
    if md_path is None:
        print("  WARN: glossar.md nicht gefunden (weder Edition-Repo noch Pipeline), skip glossary.",
              file=sys.stderr)
        return

    md_source = md_path.read_text(encoding="utf-8")

    def _slug(text):
        s = text.strip().lower()
        s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
        out = []
        for ch in s:
            if ch.isalnum():
                out.append(ch)
            elif ch in (" ", "-", "_"):
                out.append("-")
        return "".join(out).strip("-")

    def _replace_wiki_link(match):
        target = match.group(1)
        if target.startswith("#"):
            label = target[1:]
            return f"[{label}](#{_slug(label)})"
        if "#" in target:
            doc, _sep, anchor = target.partition("#")
            return anchor or doc
        return target

    md_source = _re.sub(r"\[\[([^\]]+)\]\]", _replace_wiki_link, md_source)

    md = _create_markdown_processor()
    content_html = md.convert(md_source)
    toc_html = md.toc

    template = env.get_template("glossary.html")
    html = template.render(
        content=content_html,
        toc=toc_html,
        build_date=_format_german_date(date.today()),
        root_path="..",
    )
    out = DOCS_DIR / "project" / "glossary.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  Glossary page: project/glossary.html")


def _build_impressum(env):
    """Build impressum page from Markdown source."""
    md_path = CONTENT_DIR / "impressum.md"
    if not md_path.exists():
        print("  WARN: impressum.md not found, skipping.", file=sys.stderr)
        return

    md_source = md_path.read_text(encoding="utf-8")
    md = _create_markdown_processor()
    content_html = md.convert(md_source)
    toc_html = md.toc

    template = env.get_template("about.html")  # Reuse about.html template
    html = template.render(
        content=content_html,
        toc=toc_html,
        build_date=_format_german_date(date.today()),
        root_path=".",
        page_title="Impressum",
        page_subtitle="Lizenz, Verantwortliche, Datenquellen, Zitierweise",
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "impressum.html").write_text(html, encoding="utf-8")
    print("  Impressum page: impressum.html")


# ---------------------------------------------------------------------------
# Analysis page + vocabulary and categories JSON
# ---------------------------------------------------------------------------


def _write_categories():
    """Copy categories.json from content/ to docs/data/, with build metadata.

    The source file lives in `frontend/content/categories.json` and is the
    versioned editorial mapping `org_type -> category` (geistlich/weltlich/
    sonstige). It is validated against the org-type list in epic_a.json so
    that the pipeline cannot silently introduce types that the editorial
    classification does not yet cover.
    """
    src = CONTENT_DIR / "categories.json"
    if not src.exists():
        print("  WARN: categories.json not found, skipping.", file=sys.stderr)
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    data.setdefault("meta", {})["created"] = date.today().isoformat()

    epic_a_path = DATA_DIR / "epic_a.json"
    if epic_a_path.exists():
        try:
            epic_a = json.loads(epic_a_path.read_text(encoding="utf-8"))
            real_types = set(epic_a.get("observations", {}).get("org_type_totals", {}).keys())
            mapped_types = {t for ts in data.get("categories", {}).values() for t in ts}
            missing = real_types - mapped_types
            extra = mapped_types - real_types
            if missing:
                print(f"  WARN: org types in epic_a not classified: {sorted(missing)}", file=sys.stderr)
            if extra:
                print(f"  WARN: classified types not in epic_a: {sorted(extra)}", file=sys.stderr)
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
    """Build analysis page (Composer UI).

    Minimal build: only template render with an asset-version string for
    cache-busting of the composer scripts. No header KPIs any more — KPIs
    now live in the composer itself (live from epic_*.json).
    """
    assets_version = datetime.now().strftime("%Y%m%d%H%M%S")

    template = env.get_template("analysis.html")
    html = template.render(
        build_date=_format_german_date(date.today()),
        root_path="..",
        assets_version=assets_version,
    )
    out = DOCS_DIR / "analysis" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  Analysis page: analysis/index.html")
