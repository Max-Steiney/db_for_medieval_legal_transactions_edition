"""Seiten-Builder: Startseite, Quellen-Index, Register, Exploration,
Analyse, statische Markdown-Seiten und kleinere JSON-Outputs.

Konsumiert die KPI- und Helper-Module; ruft Jinja-Templates auf und
schreibt HTML/JSON nach docs/.
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
)
from frontend.build._kpi import (
    _compute_release_kpis, _compute_corpus_breakdown, _compute_matrix_columns,
    _released_person_keys, _persons_with_org_released,
)


# ---------------------------------------------------------------------------
# Quellen-Index (documents.html)
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

        # Quality-Findings: in der Suchliste reicht eine kompakte
        # Kategorien-Aggregation pro Quelle. Wir liefern bis zu fuenf
        # Kategorien als {c, n}-Paare (Kategorie, Anzahl). Dadurch kann
        # der Vorschau-Block in der Tabelle die Befund-Arten zeigen,
        # ohne dass clientseitig validation_report.json nachgeladen
        # werden muss.
        qfindings = m.get("quality_findings") or []
        qcat_counts = {}
        for f in qfindings:
            cat = f.get("category", "")
            if cat:
                qcat_counts[cat] = qcat_counts.get(cat, 0) + 1
        qcat_list = sorted(
            ({"c": k, "n": v} for k, v in qcat_counts.items()),
            key=lambda x: (-x["n"], x["c"]),
        )[:5]

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
            "q": m.get("quality_score", 0),
            "qc": m.get("quality_count", 0),
            "qcat": qcat_list,
        })

    collections = {}
    for m in all_metadata:
        path_key = m.get("collection_path", "")
        if path_key not in collections:
            collections[path_key] = {
                "count": 0,
                "label": m.get("collection_label", path_key),
                "path": path_key,
            }
        collections[path_key]["count"] += 1

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

    quality_ok = sum(1 for m in all_metadata if m.get("quality_score", 0) == 0)
    quality_notice = sum(1 for m in all_metadata if m.get("quality_score", 0) == 1)
    quality_warning = sum(1 for m in all_metadata if m.get("quality_score", 0) == 2)

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
        timeline_data=timeline_data,
        max_count=max_count,
        min_year=min_year,
        max_year=max_year,
        top_places=top_places,
        facs_count=facs_count,
        person_register_count=reg.get("persons", 0),
        org_register_count=reg.get("orgs", 0),
        place_register_count=reg.get("places", 0),
        quality_ok=quality_ok,
        quality_notice=quality_notice,
        quality_warning=quality_warning,
        root_path=".",
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "documents.html").write_text(html, encoding="utf-8")
    print(f"  Documents page: {len(all_metadata)} documents")


# ---------------------------------------------------------------------------
# Startseite (index.html)
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
# Register-Seiten (Personen)
# ---------------------------------------------------------------------------


def _entity_quality_worst(entity_id, reverse_index):
    """Compute worst quality score across documents referencing an entity."""
    docs = reverse_index.get(entity_id, [])
    if not docs:
        return -1
    return max(d.get("quality_score", 0) for d in docs)


def _person_search_data(persons, reverse_index, released_keys=None):
    """Build compact JSON list for the persons register page.

    If ``released_keys`` is provided, only persons that appear in at least
    one released TEI source are emitted.
    """
    data = []
    for xml_id, p in persons.items():
        if released_keys is not None and xml_id not in released_keys:
            continue
        data.append({
            "id": xml_id,
            "n": p["display"],
            "fn": p["forename"],
            "sn": p["surname"],
            "sex": p["sex"],
            "d": p["death"],
            "dc": len(reverse_index.get(xml_id, [])),
            "qw": _entity_quality_worst(xml_id, reverse_index),
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
            "qw": _entity_quality_worst(xml_id, reverse_index),
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
            "qw": _entity_quality_worst(xml_id, reverse_index),
        })
    data.sort(key=lambda x: x["n"].lower())
    return data


def _build_register_list_pages(persons, orgs, places, reverse_index, env):
    """Build the three register list pages.

    Nur das Personenregister ist oeffentlich freigegeben. Organisationen und
    Orte bleiben unfreigegeben — keine Listenseiten.
    """
    template = env.get_template("register_list.html")
    released_person_keys = _released_person_keys()

    configs = [
        ("persons", "Personen", persons, _person_search_data),
    ]

    for reg_type, label, register, data_fn in configs:
        out = DOCS_DIR / "register" / f"{reg_type}.html"
        out.parent.mkdir(parents=True, exist_ok=True)

        if reg_type == "persons":
            search_data = data_fn(register, reverse_index,
                                  released_keys=released_person_keys)
        else:
            search_data = data_fn(register, reverse_index)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"{reg_type}_search.json").write_text(
            json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
        )

        if reg_type == "persons":
            visible_ids = {row["id"] for row in search_data}
            filter_values = sorted({
                register[pid]["sex"] for pid in visible_ids
                if register.get(pid, {}).get("sex")
            })
            filter_label = "Geschlecht"
            filter_map = {"m": "Männlich", "f": "Weiblich", "u": "Unbekannt"}
        elif reg_type == "organisations":
            filter_values = sorted({o["type"] for o in register.values() if o["type"]})
            filter_label = "Typ"
            filter_map = {}
        else:
            filter_values = sorted({p["type"] for p in register.values() if p["type"]})
            filter_label = "Typ"
            filter_map = {}

        html = template.render(
            register_type=reg_type,
            register_label=label,
            total_count=len(search_data),
            filter_values=filter_values,
            filter_label=filter_label,
            filter_map=filter_map,
            root_path="..",
        )

        out.write_text(html, encoding="utf-8")
        print(f"  Register list: register/{reg_type}.html ({len(search_data)} entries)")


def _build_register_json(reverse_index):
    """Write reverse-index data as JSON files for client-side detail views.

    Personen werden auf den Released-Set aus ``_released_person_keys()``
    eingeschraenkt: nur Personen, die mindestens einmal als
    ``<rs type="person">`` in einer freigegebenen Quelle auftreten,
    landen in ``register/persons.json``. Reine ``@corresp``-Hilfsverknuepfungen
    zaehlen nicht als Erwaehnung.
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
# Exploration-Hub und Sub-Seiten
# ---------------------------------------------------------------------------


def _build_exploration(all_metadata, persons, env):
    """Build exploration hub + 3 subpages (roles, networks, transactions).

    Header-KPIs (Personen, Events, Geschlechter, Personen mit
    Institutionsbezug) sind auf den freigegebenen Korpus eingeschraenkt
    und stammen aus _compute_release_kpis() + _released_person_keys().
    """
    epic_a_path = DATA_DIR / "epic_a.json"
    if not epic_a_path.exists():
        print("  WARN: epic_a.json not found, skipping exploration pages.",
              file=sys.stderr)
        return

    kpis = _compute_release_kpis()
    released_persons = _released_person_keys()

    total_docs = len(all_metadata)
    total_persons = kpis["distinct_persons"]
    total_events = kpis["distinct_events"]
    sex_m = sum(1 for pid, p in persons.items()
                if pid in released_persons and p.get("sex") == "m")
    sex_f = sum(1 for pid, p in persons.items()
                if pid in released_persons and p.get("sex") == "f")
    sex_u = total_persons - sex_m - sex_f

    epic_a = json.loads(epic_a_path.read_text(encoding="utf-8"))
    epic_a_total_events = epic_a.get("coverage", {}).get("total_events", 0)
    norm_rate = epic_a.get("coverage", {}).get("normalisation_rate", 0)
    norm_rate_pct = (round(norm_rate / epic_a_total_events * 100, 1)
                     if epic_a_total_events else 0)
    persons_with_org = _persons_with_org_released(released_persons)
    org_type_count = epic_a.get("coverage", {}).get("org_type_count", 0)

    shared_vars = dict(
        build_date=_format_german_date(date.today()),
        total_docs=total_docs,
        total_persons=total_persons,
        total_events=total_events,
        sex_m=sex_m,
        sex_f=sex_f,
        sex_u=sex_u,
        norm_rate_pct=norm_rate_pct,
        persons_with_org=persons_with_org,
        org_type_count=org_type_count,
        root_path="..",
    )

    explore_dir = DOCS_DIR / "exploration"
    explore_dir.mkdir(parents=True, exist_ok=True)

    hub_html = env.get_template("exploration.html").render(**shared_vars)
    (explore_dir / "index.html").write_text(hub_html, encoding="utf-8")
    print("  Exploration hub: exploration/index.html")

    roles_html = env.get_template("exploration_roles.html").render(**shared_vars)
    (explore_dir / "roles.html").write_text(roles_html, encoding="utf-8")
    print("  Exploration subpage: exploration/roles.html")

    epic_c_path = DATA_DIR / "epic_c.json"
    if epic_c_path.exists():
        epic_c_json = epic_c_path.read_text(encoding="utf-8")
        epic_c = json.loads(epic_c_json)
        cov = epic_c.get("coverage", {})
        total_ev_c = cov.get("total_events", 0)
        norm_ev_c = cov.get("normalised_events", 0)
        norm_pct_c = round(norm_ev_c / total_ev_c * 100, 1) if total_ev_c else 0
        tx_vars = dict(
            epic_c_json=epic_c_json,
            total_events_c=total_ev_c,
            normalised_events=norm_ev_c,
            unique_verb_forms=cov.get("unique_verb_forms", 0),
            recipient_orgs=cov.get("recipient_orgs", 0),
            norm_rate_pct=norm_pct_c,
        )
        tx_html = env.get_template("exploration_transactions.html").render(
            **{**shared_vars, **tx_vars})
        (explore_dir / "transactions.html").write_text(tx_html, encoding="utf-8")
        print("  Exploration subpage: exploration/transactions.html")
    else:
        html = env.get_template("exploration_transactions.html").render(**shared_vars)
        (explore_dir / "transactions.html").write_text(html, encoding="utf-8")
        print("  Exploration subpage: exploration/transactions.html (placeholder)")

    epic_b_path = DATA_DIR / "epic_b.json"
    if epic_b_path.exists():
        epic_b = json.loads(epic_b_path.read_text(encoding="utf-8"))
        cov_b = epic_b.get("coverage", {})
        net_vars = dict(
            epic_b_json=True,
            node_count=cov_b.get("node_count", 0),
            total_annotated_relations=cov_b.get("total_annotated_relations", 0),
        )
        net_html = env.get_template("exploration_networks.html").render(
            **{**shared_vars, **net_vars})
    else:
        net_html = env.get_template("exploration_networks.html").render(**shared_vars)
    (explore_dir / "networks.html").write_text(net_html, encoding="utf-8")
    print("  Exploration subpage: exploration/networks.html")


# ---------------------------------------------------------------------------
# Statische Markdown-Seiten (about, glossary, guidelines, impressum)
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

    Wiki-Links der Form [[#Begriff]] werden zu seiten-internen Anker-Links,
    [[Dokument]] und [[Dokument#Anker]] werden als Klartext belassen
    (Zielseiten liegen ausserhalb der Edition).

    Quelle ist bevorzugt das Edition-Repo (Sibling-Pfad), sonst KNOWLEDGE_DIR
    im Pipeline-Repo.
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
# Analyse-Seite + Vokabular- und Kategorien-JSON
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

    Vocabulary fuer den Satz-Builder der Analyse-Seite. Liefert Subjekte,
    Filter, Werte-Listen mit Verb-Phrasen, Gruppierungen und Aggregationen.
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
    """Build analysis page (Composer-UI).

    Minimaler Build: nur Template-Render mit Asset-Versions-String fuer
    Cache-Busting der Composer-Skripte. Keine Header-KPIs mehr — KPIs
    leben jetzt im Composer selbst (live aus epic_*.json).
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
