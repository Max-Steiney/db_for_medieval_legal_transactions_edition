"""Orchestrator: load registers, iterate files, write HTML."""

import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
import markdown as markdown_lib

from pipeline.config import SOURCES_DIR, NS_MAP, REPO_ROOT


_GERMAN_MONTHS = [
    "Januar", "Februar", "M\u00e4rz", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _format_german_date(dt):
    """Format a date as '17. April 2026'."""
    return f"{dt.day}. {_GERMAN_MONTHS[dt.month - 1]} {dt.year}"


def _pipeline_repo_data_date():
    """Return the date of the last git commit in the pipeline repo as a german-formatted string.

    Falls back to today's date if git is unavailable or the repo has no commits.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        iso = result.stdout.strip()
        if iso:
            dt = datetime.fromisoformat(iso).date()
            return _format_german_date(dt)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return _format_german_date(date.today())


def _create_markdown_processor():
    """Create Markdown processor with standard project config."""
    return markdown_lib.Markdown(extensions=[
        "tables",
        "fenced_code",
        "codehilite",
        "toc",
        "attr_list",
    ], extension_configs={
        "toc": {
            "toc_depth": "2-3",
            "permalink": True,
        },
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
    })
from pipeline.utils.xml_loader import load_xml, collect_source_files
from pipeline.utils.text_utils import normalize_space, elem_text, strip_hash
from pipeline.utils.date_parser import create_date

from frontend.config import (
    DOCS_DIR, TEMPLATES_DIR, STATIC_DIR, CONTENT_DIR, KNOWLEDGE_DIR,
    DATA_DIR, FACSIMILE_BASE_URLS, VALIDATION_REPORT_PATH,
    EDITION_GUIDELINES_PATH,
    RELEASED_PERIOD, RELEASED_CORPORA, is_released_corpus,
    released_period_label, unprocessed_gaps_label, max_year_with_extensions,
)
from frontend.register import load_persons, load_orgs, load_places
from frontend.renderer import render_document

# Two-layer UI: scholarly labels for technical path fragments
COLLECTION_LABELS = {
    "QGW/Vienna_1177-1414_ready": "QGW II/1 (1177–1414)",
    "QGW/Vienna_1415-1417": "QGW II/2 (1415–1417)",
    "QGW/Vienna_1448-57_ready": "QGW II/2 (1448–1457)",
    "QGW/Vienna_1458-66": "QGW II/3 (1458–1466)",
    "QGW/Vienna_1493-1500": "QGW II/4 (1493–1500)",
    "QGW/Vienna_1524": "QGW II/5 (1524)",
    "Stadtbuecher/Band_1_1395-1400_ready": "Stadtbücher Bd. 1 (1395–1400)",
    "Gewerbuch_D/GB_D_1448-60_ready": "Gewerbuch D (1448–1460)",
    "Satzbuch_CD/SB_CD_1448-60_ready": "Satzbuch CD (1448–1460)",
    "Copeybuch_Zeibig/Buergeraufgebot_1454_05_29_ready": "Copeybuch (Zeibig): Bürgeraufgebot (1454)",
    "Copeybuch_Zeibig/Geldeintreiber_Feuerordnung_1454-05-22_ready": "Copeybuch (Zeibig): Feuerordnung (1454)",
    "Copeybuch_Zeibig/Versammlung_1454-03-30_ready": "Copeybuch (Zeibig): Versammlung (1454)",
    "GenanntenListe_Weinzettel/Gen_Weinz_1459-61_ready": "Genannten-Liste Weinzettel (1459–1461)",
    "Genanntenliste_Stubenviertel/GenStub_1461-66": "Genanntentafel Stubenviertel (1461–1466)",
    "Widmerliste/widmer_1448_ready": "Widmerliste (1448)",
}


def _collection_label(collection, subcollection):
    """Return scholarly label for a collection path, with path as fallback."""
    key = f"{collection}/{subcollection}"
    return COLLECTION_LABELS.get(key, key)


def _xpath_text(root, xpath_expr, default=""):
    """Extract text from first XPath match, or return default."""
    elems = root.xpath(xpath_expr, namespaces=NS_MAP)
    return normalize_space(elem_text(elems[0])) if elems else default


def _extract_regest(root, max_len=200):
    """Extract abstract/entry text as regest preview."""
    for div_type in ("abstract", "entry"):
        divs = root.xpath(
            f".//tei:text//tei:div[@type='{div_type}']", namespaces=NS_MAP
        )
        if divs:
            raw = normalize_space("".join(divs[0].itertext()))
            if raw and not raw.lower().startswith("tei version"):
                if len(raw) > max_len:
                    return raw[:max_len].rsplit(" ", 1)[0] + "…"
                return raw
    return ""


def _extract_entity_refs(root):
    """Extract all entity IDs referenced in the document text.

    Scans <rs type="person|org|place" ref="..."> and <roleName corresp="...">.
    Returns a de-duplicated set of bare entity IDs (without '#' prefix).
    """
    refs = set()
    for rs in root.xpath(
        ".//tei:text//tei:rs[@type='person' or @type='org' or @type='place']",
        namespaces=NS_MAP,
    ):
        ref = strip_hash(rs.get("ref", ""))
        if ref and ref != "NULL":
            refs.add(ref)
    for rn in root.xpath(
        ".//tei:text//tei:roleName[@corresp]",
        namespaces=NS_MAP,
    ):
        corresp = strip_hash(rn.get("corresp", ""))
        if corresp:
            refs.add(corresp)
    return refs


def _init_jinja():
    """Create Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,  # We handle escaping in the renderer
    )
    env.globals["build_date"] = _format_german_date(date.today())
    env.globals["data_date"] = _pipeline_repo_data_date()
    # Cache buster for static assets (CSS/JS): per-build timestamp
    # avoids stale browser caches when source files change without a
    # filename hash. Used in templates as {{ root_path }}/static/...?v={{ asset_v }}.
    env.globals["asset_v"] = datetime.now().strftime("%Y%m%d%H%M%S")
    rp = dict(RELEASED_PERIOD)
    rp["max_year_with_extensions"] = max_year_with_extensions()
    env.globals["released_period"] = rp
    env.globals["released_period_label"] = released_period_label()
    env.globals["unprocessed_gaps_label"] = unprocessed_gaps_label()
    return env


def _normalize_facsimile_url(raw_url, collection):
    """Normalize a single facsimile URL.

    Absolute URLs (http/https) pass through unchanged. Relative filenames
    are resolved against FACSIMILE_BASE_URLS if the collection has a
    configured base URL, otherwise dropped (return None).
    """
    if not raw_url:
        return None
    if raw_url.startswith(("http://", "https://")):
        return raw_url
    base = FACSIMILE_BASE_URLS.get(collection)
    if base:
        return base + raw_url
    return None


def _extract_metadata(tree, filepath):
    """Extract document metadata from TEI header."""
    root = tree.getroot()

    # Date
    iso_date = create_date(tree)

    # Simple XPath extractions
    title = _xpath_text(root, ".//tei:teiHeader//tei:titleStmt/tei:title") or filepath.stem
    date_display = _xpath_text(root, ".//tei:teiHeader//tei:profileDesc/tei:creation/tei:date") or iso_date
    place = _xpath_text(root, ".//tei:teiHeader//tei:profileDesc/tei:creation/tei:placeName")
    repository = _xpath_text(root, ".//tei:teiHeader//tei:repository")
    idno = _xpath_text(root, ".//tei:teiHeader//tei:msIdentifier/tei:idno") or filepath.stem
    source_url = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl[@type='url']")
    orig_date = _xpath_text(root, ".//tei:teiHeader//tei:origDate")

    # Source citation (prefer draft, fallback to any bibl)
    citation = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl[@status='draft']")
    if not citation:
        citation = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl")

    # Collection (derived from path) — needed before facsimile URL resolution
    rel = filepath.relative_to(SOURCES_DIR)
    collection = rel.parts[0] if rel.parts else ""
    subcollection = rel.parts[1] if len(rel.parts) > 1 else ""
    collection_label = _collection_label(collection, subcollection)

    # Facsimile URLs (resolve relative filenames against collection base URLs)
    facsimile_urls = []
    for g in root.xpath(".//tei:facsimile//tei:graphic", namespaces=NS_MAP):
        normalized = _normalize_facsimile_url(g.get("url", ""), collection)
        if normalized:
            facsimile_urls.append(normalized)

    # Regest: extract readable text from abstract/entry
    regest = _extract_regest(root)
    regest_full = _extract_regest(root, max_len=500)

    # Source file path (for provenance)
    source_path = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    # Entity counts (annotation density)
    person_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='person']", namespaces=NS_MAP
    ))
    org_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='org']", namespaces=NS_MAP
    ))

    # Annotation counts for statistics dashboard
    event_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='event']"
        "[not(ancestor::tei:rs[@type='event'])]",
        namespaces=NS_MAP
    ))
    fn_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='fn']", namespaces=NS_MAP
    ))
    rolename_count = len(root.xpath(
        ".//tei:text//tei:roleName", namespaces=NS_MAP
    ))
    triggerstring_count = len(root.xpath(
        ".//tei:text//tei:triggerstring", namespaces=NS_MAP
    ))

    # Function role breakdown (+ person IDs per role for gender stats)
    fn_role_counts = Counter()
    fn_role_person_ids = {}  # role -> [person_id, ...]
    for fn_elem in root.xpath(
        ".//tei:text//tei:rs[@type='fn']", namespaces=NS_MAP
    ):
        role = fn_elem.get("role", "other")
        fn_role_counts[role] += 1
        for pref in fn_elem.xpath(
            ".//tei:rs[@type='person']/@ref", namespaces=NS_MAP
        ):
            pid = strip_hash(pref)
            if pid and pid != "NULL":
                fn_role_person_ids.setdefault(role, []).append(pid)

    # Seal presence
    has_seal = bool(root.xpath(
        ".//tei:text//tei:div[@type='seal']", namespaces=NS_MAP
    ))

    return {
        "title": title,
        "idno": idno,
        "date_iso": iso_date,
        "date_display": date_display,
        "place": place,
        "repository": repository,
        "citation": citation,
        "source_url": source_url,
        "orig_date": orig_date,
        "facsimile_urls": facsimile_urls,
        "has_facsimile": bool(facsimile_urls),
        "collection": collection,
        "subcollection": subcollection,
        "collection_label": collection_label,
        "collection_path": f"{collection}/{subcollection}",
        "regest": regest,
        "regest_full": regest_full,
        "source_path": source_path,
        "filename": filepath.stem,
        "person_count": person_count,
        "org_count": org_count,
        "event_count": event_count,
        "fn_count": fn_count,
        "rolename_count": rolename_count,
        "triggerstring_count": triggerstring_count,
        "fn_role_counts": dict(fn_role_counts),
        "fn_role_person_ids": fn_role_person_ids,
        "has_seal": has_seal,
    }


def _output_path(filepath):
    """Compute output HTML path, dropping 'done/' from the path."""
    rel = filepath.relative_to(SOURCES_DIR)
    # Drop 'done' directory from path
    parts = [p for p in rel.parts if p != "done"]
    # Change extension
    out = DOCS_DIR / "documents" / Path(*parts).with_suffix(".html")
    return out


def _relative_to_root(output_path):
    """Compute relative path from output file back to docs root."""
    depth = len(output_path.relative_to(DOCS_DIR).parts) - 1
    if depth <= 0:
        return "."
    return "/".join([".."] * depth)


def _is_done_file(filepath):
    """Check if file is in a 'done' directory."""
    return "done" in filepath.relative_to(SOURCES_DIR).parts


def _is_released_file(filepath):
    """True, wenn die Datei zu einem freigegebenen Quellenkorpus gehört.

    Filtert QGW II/3, II/4, Vienna_1448-57_ready und alle Nebenkorpora
    (Gewerbuch, Satzbuch, Copeybuch, Genanntenlisten, Widmerliste) aus dem
    Public-Build. Freigabe-Regel in config.RELEASED_CORPORA.
    """
    rel = filepath.relative_to(SOURCES_DIR)
    if len(rel.parts) < 2:
        return False
    return is_released_corpus(f"{rel.parts[0]}/{rel.parts[1]}")


def _load_registers():
    """Load person/org/place registers with timing."""
    print("Loading registers...")
    t0 = time.time()
    persons = load_persons()
    orgs = load_orgs()
    places = load_places()
    print(f"  Loaded {len(persons)} persons, {len(orgs)} orgs, {len(places)} places "
          f"in {time.time() - t0:.1f}s")
    return persons, orgs, places


def _load_quality_index():
    """Load validation_report.json and index findings by source-relative file path.

    Returns a dict mapping normalised file paths (forward slashes, relative to
    sources/) to a list of finding dicts.  If the report file does not exist,
    returns an empty dict so the build can proceed without quality data.
    """
    if not VALIDATION_REPORT_PATH.exists():
        print("  WARN: validation_report.json not found, quality data disabled.",
              file=sys.stderr)
        return {}

    report = json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))
    index = {}  # normalised path -> [findings]
    for finding in report.get("findings", []):
        # Normalise Windows backslashes to forward slashes
        key = finding["file"].replace("\\", "/")
        index.setdefault(key, []).append({
            "severity": finding["severity"],
            "category": finding["category"],
            "detail": finding["detail"],
        })
    print(f"  Quality index: {len(index)} files with findings "
          f"({report.get('summary', {}).get('total_findings', 0)} total)")
    return index


def _quality_score(findings):
    """Compute quality score from a list of findings.

    Returns: 0 = ok (no findings), 1 = notice (info only), 2 = warning.
    """
    if not findings:
        return 0
    severities = {f["severity"] for f in findings}
    if "warning" in severities or "error" in severities:
        return 2
    return 1


def _build_quality_json(quality_index):
    """Write corpus-wide quality aggregation to docs/data/quality.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Per-category breakdown
    by_category = Counter()
    by_severity = Counter()
    by_collection = {}  # collection_prefix -> Counter(severity)
    for filepath, findings in quality_index.items():
        # Extract collection from path (first two segments)
        parts = filepath.split("/")
        collection_key = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
        for f in findings:
            by_category[f["category"]] += 1
            by_severity[f["severity"]] += 1
            by_collection.setdefault(collection_key, Counter())[f["severity"]] += 1

    total_findings = sum(by_severity.values())

    quality_data = {
        "meta": {
            "schema_version": "1.0",
            "created": date.today().isoformat(),
            "description": "Corpus-wide validation findings from pipeline validation",
            "sources": ["validation_report.json"],
            "structure": {
                "dimensions": [
                    {"name": "category", "type": "categorical",
                     "values": sorted(by_category.keys())},
                    {"name": "severity", "type": "ordinal",
                     "values": ["info", "warning", "error"]},
                    {"name": "collection", "type": "categorical"},
                ],
                "measures": [
                    {"name": "count", "type": "integer",
                     "description": "Number of findings"},
                ],
            },
        },
        "observations": {
            "bySeverity": dict(by_severity),
            "byCategory": dict(by_category),
            "byCollection": {k: dict(v) for k, v in sorted(by_collection.items())},
        },
        "coverage": {
            "totalFiles": len(quality_index),
            "totalFindings": total_findings,
        },
    }

    out = DATA_DIR / "quality.json"
    out.write_text(json.dumps(quality_data, ensure_ascii=False), encoding="utf-8")
    print(f"  Quality JSON: quality.json ({total_findings} findings)")


def build_single(filepath_str):
    """Build a single document."""
    filepath = REPO_ROOT / filepath_str
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    registers = _load_registers()
    quality_index = _load_quality_index()

    env = _init_jinja()
    result = _parse_file(filepath, registers, quality_index)
    if result:
        meta, body_html, output, _entity_refs = result
        _write_file(meta, body_html, output, env)
        print(f"Done. Output: {output}")
    _copy_static()
    _copy_tei_sources()


def build_all():
    """Build all documents + index page."""
    t0 = time.time()
    persons, orgs, places = _load_registers()
    registers = (persons, orgs, places)
    register_counts = {
        "persons": len(persons),
        "orgs": len(orgs),
        "places": len(places),
    }

    quality_index = _load_quality_index()

    env = _init_jinja()

    # Collect source files (nur freigegebene Quellenkorpora)
    all_files = collect_source_files()
    done_files = [f for f in all_files if _is_done_file(f) and _is_released_file(f)]
    print(f"Found {len(done_files)} documents to render (released corpora only).")

    # Pass 1: Parse all documents, collect metadata + body HTML
    parsed = []
    t1 = time.time()
    for i, filepath in enumerate(done_files, 1):
        result = _parse_file(filepath, registers, quality_index)
        if result:
            parsed.append(result)
        if i % 100 == 0 or i == len(done_files):
            elapsed = time.time() - t1
            rate = i / elapsed if elapsed > 0 else 0
            print(f"  Parsed [{i}/{len(done_files)}] {rate:.0f} docs/s")

    # Compute prev/next links (needs all metadata before rendering)
    all_metadata = [p[0] for p in parsed]
    _compute_prev_next(all_metadata)

    # Build reverse index: entity_id -> [doc metadata]
    print("Building reverse index...")
    reverse_index = {}
    for meta, _body, _out, entity_refs in parsed:
        doc_entry = {
            "url": meta["url"],
            "idno": meta["idno"],
            "date_display": meta["date_display"],
            "date_iso": meta["date_iso"],
            "collection_label": meta["collection_label"],
            "collection_path": meta.get("collection_path", ""),
            "regest": meta["regest"],
            "quality_score": meta.get("quality_score", 0),
        }
        for eid in entity_refs:
            reverse_index.setdefault(eid, []).append(doc_entry)
    # Sort each entity's documents by date
    for docs in reverse_index.values():
        docs.sort(key=lambda d: d.get("date_iso", ""))
    print(f"  Reverse index: {len(reverse_index)} entities linked to documents")

    # Quality data aggregation
    _build_quality_json(quality_index)

    # Data aggregation for visualisation Epics
    from frontend.aggregator import run_aggregation, build_docs_lookup
    run_aggregation(DATA_DIR, reverse_index)
    build_docs_lookup(DATA_DIR, all_metadata)

    # Pass 2: Render templates and write HTML files.
    # Vorher docs/documents/ leeren, damit Altbestände aus nicht-freigegebenen
    # Korpora nicht als stale Dateien zurückbleiben.
    docs_out_dir = DOCS_DIR / "documents"
    if docs_out_dir.exists():
        shutil.rmtree(docs_out_dir)
    t2 = time.time()
    for i, (meta, body_html, output, _refs) in enumerate(parsed, 1):
        _write_file(meta, body_html, output, env)
        if i % 500 == 0 or i == len(parsed):
            print(f"  Written [{i}/{len(parsed)}]")

    print(f"  Render pass: {time.time() - t2:.1f}s")

    # Build document list page (formerly index.html, now documents.html)
    _build_index(all_metadata, env, register_counts)

    # Build Startseite (portal landing page -> index.html)
    collections_start = {}
    for m in all_metadata:
        path_key = m.get("collection_path", "")
        if path_key not in collections_start:
            collections_start[path_key] = {
                "count": 0,
                "label": m.get("collection_label", path_key),
                "path": path_key,
            }
        collections_start[path_key]["count"] += 1
    _build_startseite(all_metadata, persons, orgs, places, collections_start, env)

    # Build register pages
    _build_register_list_pages(persons, orgs, places, reverse_index, env)
    _build_register_json(reverse_index)
    # Statistics dashboard removed: KPIs now live on the Datengrundlage page.

    # Build exploration page (V1 shared + V2 Epic A)
    _build_exploration(all_metadata, persons, env)

    # Build guidelines page
    _build_guidelines(env)

    # Build about page + impressum
    _build_about(env)
    _build_impressum(env)

    # Build glossary + analysis page (with categories source-of-truth)
    _build_glossary(env)
    _write_categories()
    _write_query_vocabulary()
    _build_analysis(env)

    # Datengrundlage-Inhalte sind in die Provenance-Tooltips integriert,
    # daher keine eigene Seite mehr.

    # Copy static assets + TEI sources
    _copy_static()
    _copy_tei_sources()

    # Write .nojekyll
    (DOCS_DIR / ".nojekyll").touch()

    elapsed = time.time() - t0
    print(f"Build complete: {len(all_metadata)} documents in {elapsed:.1f}s")
    print(f"Output: {DOCS_DIR}")


def _sort_key_for_nav(filename):
    """Sort key for sequential navigation: numeric if possible, else string."""
    try:
        return (0, int(filename), "")
    except (ValueError, TypeError):
        return (1, 0, str(filename))


def _compute_prev_next(all_metadata):
    """Compute previous/next document links within each collection."""
    # Group by collection_path
    by_collection = {}
    for meta in all_metadata:
        cp = meta.get("collection_path", "")
        by_collection.setdefault(cp, []).append(meta)

    for cp, metas in by_collection.items():
        metas.sort(key=lambda m: _sort_key_for_nav(m.get("filename", "")))
        for i, meta in enumerate(metas):
            if i > 0:
                meta["prev_url"] = metas[i - 1].get("url", "")
                meta["prev_id"] = metas[i - 1].get("idno", "")
            else:
                meta["prev_url"] = ""
                meta["prev_id"] = ""
            if i < len(metas) - 1:
                meta["next_url"] = metas[i + 1].get("url", "")
                meta["next_id"] = metas[i + 1].get("idno", "")
            else:
                meta["next_url"] = ""
                meta["next_id"] = ""


def _parse_file(filepath, registers, quality_index=None):
    """Parse a TEI-XML source: extract metadata + render body HTML.

    Returns (meta, body_html, output_path, entity_refs) or None on failure.
    """
    try:
        tree = load_xml(filepath)
    except Exception as e:
        print(f"  WARN: Could not parse {filepath}: {e}", file=sys.stderr)
        return None

    root = tree.getroot()
    meta = _extract_metadata(tree, filepath)

    # Quality data: look up findings for this file
    if quality_index:
        # Key: path relative to sources/, forward slashes
        rel_key = str(filepath.relative_to(SOURCES_DIR)).replace("\\", "/")
        findings = quality_index.get(rel_key, [])
    else:
        findings = []
    meta["quality_score"] = _quality_score(findings)
    meta["quality_findings"] = findings
    meta["quality_count"] = len(findings)

    # Find body
    bodies = root.xpath(".//tei:text/tei:body", namespaces=NS_MAP)
    if not bodies:
        bodies = root.xpath(".//tei:body", namespaces=NS_MAP)
    if not bodies:
        print(f"  WARN: No <body> in {filepath}", file=sys.stderr)
        return None

    output = _output_path(filepath)
    root_path = _relative_to_root(output)
    body_html = render_document(bodies[0], registers, root_path)

    # Collect entity references for reverse index
    entity_refs = _extract_entity_refs(root)

    meta["url"] = str(output.relative_to(DOCS_DIR)).replace("\\", "/")

    # TEI download URL (derived from _tei_output_path for consistency)
    meta["tei_url"] = str(_tei_output_path(filepath).relative_to(DOCS_DIR)).replace("\\", "/")

    return meta, body_html, output, entity_refs


def _write_file(meta, body_html, output, env):
    """Render template and write HTML file."""
    root_path = _relative_to_root(output)

    template = env.get_template("document.html")
    html = template.render(
        meta=meta,
        body=body_html,
        root_path=root_path,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def _format_table_date(rec):
    """Format docs_aggregate date fields for the documents-table display.

    Pipeline-Konvention: ISO-Datum ``YYYY-MM-DD``, Unsicherheit als
    ``YYYY-01-01 | YYYY-12-31`` (Jahr unscharf) oder
    ``YYYYa-01-01 | YYYYb-12-31`` (Jahresbereich).

    Anzeige:
      - ``DD.MM.YYYY`` bei sauberem Einzeldatum
      - ``MM.YYYY``     bei Jahr+Monat
      - ``YYYY``        bei Vollwertig-Jahres-Unscharfe (1.1.-31.12. desselben Jahres)
      - ``YYYY-YYYY``   bei Mehrjahres-Range (1.1.YYYYa - 31.12.YYYYb)
      - ``YYYY``        Fallback aus ``date_year``
      - ``''``          wenn keine Datumsinformation vorliegt
    """
    start = rec.get("date_iso_start", "") or ""
    end = rec.get("date_iso_end", "") or ""
    year = rec.get("date_year", "")
    if not start:
        return ""
    is_full_year_range = (
        start != end
        and start.endswith("-01-01")
        and end.endswith("-12-31")
    )
    if is_full_year_range:
        ys, ye = start[:4], end[:4]
        return ys if ys == ye else f"{ys}–{ye}"  # en-dash
    # Full ISO YYYY-MM-DD
    if len(start) >= 10 and start[4] == "-" and start[7] == "-":
        try:
            y, mo, d = start[:10].split("-")
            return f"{d}.{mo}.{y}"
        except ValueError:
            pass
    # Year-month YYYY-MM
    if len(start) >= 7 and start[4] == "-":
        try:
            y, mo = start[:7].split("-")
            return f"{mo}.{y}"
        except ValueError:
            pass
    return str(year) if year else start


def _load_docs_aggregate_lookup():
    """Build (collection_path, idno) -> aggregate-record lookup.

    Reads docs/data/docs_aggregate.json (written earlier by aggregator.py
    during run_aggregation). Falls back to {} if the file is missing,
    which keeps the build resilient during partial runs.
    """
    path = DATA_DIR / "docs_aggregate.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        (rec.get("collection_path", ""), rec.get("idno", "")): rec
        for rec in payload.get("docs", [])
    }


def _build_index(all_metadata, env, register_counts=None):
    """Build the index/browse page."""
    # Sort by date, then collection
    all_metadata.sort(key=lambda m: (m.get("date_iso", ""), m.get("collection", "")))

    # Prepare JSON for client-side search.
    # Joined with docs_aggregate.json for normalised dates, distinct-person
    # counts (with sex breakdown), and event-form distribution.
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
            "q": m.get("quality_score", 0),
            "qc": m.get("quality_count", 0),
        })

    # Collection statistics
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

    # Timeline: decade buckets + year range for slider
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
    # Clamp an Freigabe-Zeitraum, falls einzelne Regesten über den Rand
    # hinausgehen (sollte nach RELEASED_CORPORA-Filter nicht mehr passieren).
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

    # Place frequency: top places for filter dropdown
    place_counts = Counter()
    for m in all_metadata:
        if m.get("place"):
            place_counts[m["place"]] += 1
    top_places = place_counts.most_common(15)

    # Facsimile count
    facs_count = sum(1 for m in all_metadata if m.get("has_facsimile"))

    # Quality count breakdown
    quality_ok = sum(1 for m in all_metadata if m.get("quality_score", 0) == 0)
    quality_notice = sum(1 for m in all_metadata if m.get("quality_score", 0) == 1)
    quality_warning = sum(1 for m in all_metadata if m.get("quality_score", 0) == 2)

    # Register counts (passed from build_all)
    reg = register_counts or {}

    # Write search data to external JSON file (reduces page size from ~5.6 MB to <200 KB)
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
    # Sex breakdown still derived from the register; only counts persons that
    # are actually present in released sources.
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


def _entity_quality_worst(entity_id, reverse_index):
    """Compute worst quality score across documents referencing an entity."""
    docs = reverse_index.get(entity_id, [])
    if not docs:
        return -1  # no documents → not applicable
    return max(d.get("quality_score", 0) for d in docs)


def _person_search_data(persons, reverse_index, released_keys=None):
    """Build compact JSON list for the persons register page.

    If ``released_keys`` is provided, only persons that appear in at least
    one released TEI source are emitted. The full register has ~16k
    entries; the released subset is ~8.4k. Stakeholder requirement: the
    public register must mirror the released corpus, not the editorial
    workspace.
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

    Nur das Personenregister ist öffentlich freigegeben (siehe
    decisions.md#Personenregister-Freigabe). Organisationen und Orte
    bekommen eine Platzhalter-Seite, bis der redaktionelle Abgleich
    abgeschlossen ist. Das Personenregister wird auf die in den
    freigegebenen Quellen tatsächlich annotierten Personen gefiltert.
    """
    template = env.get_template("register_list.html")
    released_person_keys = _released_person_keys()

    # Nur das Personenregister wird gebaut. Organisationen und Orte sind
    # nicht aus der Navigation erreichbar; ihre Placeholder-Seiten werden
    # nicht mehr erzeugt.
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

        # Write search data to external JSON file (reduces page size)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"{reg_type}_search.json").write_text(
            json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
        )

        # Collect unique types/sexes for filter dropdowns. Filter pool is
        # limited to entities actually present on the page.
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
    eingeschr&auml;nkt: nur Personen, die mindestens einmal als
    ``<rs type="person">`` in einer freigegebenen Quelle auftreten,
    landen in ``register/persons.json``. Reine ``@corresp``-Hilfsverkn&uuml;pfungen
    z&auml;hlen nicht als Erw&auml;hnung — entsprechend der Konvention im
    Glossar (siehe knowledge/glossar.md#Gesamtnennung).
    """
    out_dir = DOCS_DIR / "register"
    out_dir.mkdir(parents=True, exist_ok=True)

    released_persons = _released_person_keys()

    # Split by ID prefix — keys match register page filenames
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
        # Compact keys to save bandwidth
        buckets[bucket][eid] = [
            {"u": d["url"], "i": d["idno"], "d": d["date_display"],
             "c": d["collection_label"], "r": d["regest"]}
            for d in docs
        ]

    for name, data in buckets.items():
        out = out_dir / f"{name}.json"
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"  Register JSON: {name}.json ({len(data)} entities)")


def _released_person_keys():
    """Return the set of distinct person_keys that appear anywhere in the
    released TEI sources. This matches the headline "Individuelle Personen"
    figure: a person enters the public register as soon as she is annotated
    in any released file, regardless of whether the only attestation sits
    inside a mentioned (nested) rs-event."""
    from lxml import etree
    from pipeline.config import SOURCES_DIR

    keys = set()
    for path_key in RELEASED_CORPORA:
        coll, sub = path_key.split("/", 1)
        done = SOURCES_DIR / coll / sub / "done"
        if not done.exists():
            continue
        for tei_file in done.rglob("*.xml"):
            try:
                tree = etree.parse(str(tei_file))
            except etree.XMLSyntaxError:
                continue
            for el in tree.xpath(_XP_PERSONS_ALL, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if ref.startswith("pe__"):
                    keys.add(ref)
    return keys


_TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# XPath specs — single source of truth for all release-KPIs. These are the
# same expressions documented in the public Provenance-Tooltips on the
# homepage. Counted directly against the released TEI files; CSV outputs
# from the pipeline are only used for non-KPI auxiliary data.
_XP_TOP_EVENTS = (
    "//tei:body//tei:rs[@type='event']"
    "[not(ancestor::tei:rs[@type='event'])]"
)
# Persons that are not inside a nested (mentioned) rs-event:
_XP_PERSONS_EXCL_MENTIONED = (
    "//tei:body//tei:*[@type='person']"
    "[not(ancestor::tei:rs[@type='event']"
    "     [ancestor::tei:rs[@type='event']])]"
)
_XP_PERSONS_ALL = "//tei:body//tei:*[@type='person']"


def _scan_released_tei():
    """Walk all released TEI sources and collect KPIs directly via XPath.

    Single source of truth for the release-level numbers shown on the
    homepage. The pipeline CSVs are not used here. Two passes per file:

    - ``_XP_PERSONS_ALL`` drives the distinct-person count and
      "Quellen mit Personen" — a person counts as soon as she is annotated
      anywhere in a released file, including inside a nested rs-event.
    - ``_XP_PERSONS_EXCL_MENTIONED`` drives the mention count — a mention
      only counts if the annotation is not inside a nested rs-event.

    Asymmetry is intentional and documented in
    ``knowledge/decisions.md`` ("Asymmetrische Zählung: individuelle
    Personen vs. Nennungen").

    Returns a tuple (totals, per_corpus) where totals is a flat dict and
    per_corpus is a list of dicts with the same shape per corpus, ordered
    as in RELEASED_CORPORA.
    """
    from lxml import etree
    from pipeline.config import SOURCES_DIR

    def _new_bucket():
        return {
            "sources": 0,
            "files_with_persons": set(),
            "person_mentions": 0,
            "distinct_persons": set(),
            "distinct_events": set(),
        }

    totals = _new_bucket()
    per_corpus = {c: _new_bucket() for c in RELEASED_CORPORA}

    for path_key in RELEASED_CORPORA:
        coll, sub = path_key.split("/", 1)
        done = SOURCES_DIR / coll / sub / "done"
        if not done.exists():
            continue
        for tei_file in sorted(done.rglob("*.xml")):
            try:
                tree = etree.parse(str(tei_file))
            except etree.XMLSyntaxError:
                continue
            cb = per_corpus[path_key]
            cb["sources"] += 1
            totals["sources"] += 1

            for ev in tree.xpath(_XP_TOP_EVENTS, namespaces=_TEI_NS):
                ref = (ev.get("ref") or "").strip().lstrip("#")
                if ref:
                    cb["distinct_events"].add(ref)
                    totals["distinct_events"].add(ref)

            # Person-Nennungen: ohne mentioned (XPath-Filter
            # schließt Personen in nested rs-events aus).
            for el in tree.xpath(_XP_PERSONS_EXCL_MENTIONED, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if not ref.startswith("pe__"):
                    continue
                cb["person_mentions"] += 1
                totals["person_mentions"] += 1

            # Alle Person-Annotationen: bestimmt "Quellen mit Personen"
            # und die distinct individual person count (eine Person ist im
            # öffentlichen Register, sobald sie irgendwo in einer
            # freigegebenen Quelle als @type='person' annotiert ist).
            file_has_person = False
            for el in tree.xpath(_XP_PERSONS_ALL, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if not ref.startswith("pe__"):
                    continue
                file_has_person = True
                cb["distinct_persons"].add(ref)
                totals["distinct_persons"].add(ref)
            if file_has_person:
                cb["files_with_persons"].add(tei_file.name)
                totals["files_with_persons"].add(str(tei_file))

    def _flatten(b):
        return {
            "sources": b["sources"],
            "sources_with_persons": len(b["files_with_persons"]),
            "person_mentions": b["person_mentions"],
            "distinct_persons": len(b["distinct_persons"]),
            "distinct_events": len(b["distinct_events"]),
        }

    flat_totals = _flatten(totals)
    flat_per_corpus = [
        {"path": c, "label": COLLECTION_LABELS.get(c, c), **_flatten(per_corpus[c])}
        for c in RELEASED_CORPORA
    ]
    return flat_totals, flat_per_corpus


def _compute_matrix_columns(total_docs, total_mentions, total_events):
    """Liefert die Spalten-Configs der Korpus-Matrix als Datenstruktur.

    Drei Datenspalten — Quellen, Nennungen, Events. Jede Spalte traegt
    sowohl die Glossar-Definition (fuer den i-Icon-Tooltip am Header)
    als auch den Provenienz-XPath (fuer den Tooltip an der Gesamt-Zahl).
    Das Template iteriert ueber diese Liste, statt jeden Block einzeln
    auszuschreiben.

    XPath-HTML wird mit ``Markup`` markiert, damit Jinja2 die
    Syntax-Highlighting-Spans nicht escaped.
    """
    return [
        {
            "id": "sources",
            "label": "Quellen",
            "glossary_id": "gloss-quelle",
            "glossary_term": "Quelle",
            "glossary_anchor": "quelle",
            "glossary_def": Markup(
                "Eine einzelne Urkunde oder ein Regest als Datensatz-Einheit. "
                "Tr&auml;ger eines oder mehrerer Events."
            ),
            "total": total_docs,
            "row_key": "sources",
            "prov_id": "prov-total-sources",
            "prov_title": "Quellen — Provenienz",
            "prov_xpath": Markup(
                '<span class="xp-axis">//</span>'
                '<span class="xp-elem">tei:TEI</span>'
            ),
            "prov_note": Markup(
                "aus <code>sources/&lt;korpus&gt;/done/</code>, "
                "eingeschr&auml;nkt auf freigegebene Korpora."
            ),
        },
        {
            "id": "mentions",
            "label": "Nennungen",
            "glossary_id": "gloss-nennung",
            "glossary_term": "Gesamtnennung",
            "glossary_anchor": "gesamtnennung",
            "glossary_def": Markup(
                "Eine Beziehung zwischen einer Person und einer Quelle, in "
                "der sie genannt wird. Quellenbereinigt: Mehrfacherw&auml;hnungen "
                "in derselben Quelle z&auml;hlen einmal."
            ),
            "total": total_mentions,
            "row_key": "mentions",
            "prov_id": "prov-total-mentions",
            "prov_title": "Nennungen — Provenienz",
            "prov_xpath": Markup(
                '<span class="xp-axis">//</span><span class="xp-elem">tei:body</span>'
                '<span class="xp-axis">//</span><span class="xp-elem">tei:*</span>'
                '<span class="xp-pred">[</span><span class="xp-attr">@type</span>='
                '<span class="xp-string">\'person\'</span><span class="xp-pred">]</span>\n'
                '<span class="xp-pred">  [not(</span>'
                '<span class="xp-axis">ancestor::</span><span class="xp-elem">tei:rs</span>'
                '<span class="xp-pred">[</span><span class="xp-attr">@type</span>='
                '<span class="xp-string">\'event\'</span><span class="xp-pred">]</span>\n'
                '<span class="xp-pred">       [</span>'
                '<span class="xp-axis">ancestor::</span><span class="xp-elem">tei:rs</span>'
                '<span class="xp-pred">[</span><span class="xp-attr">@type</span>='
                '<span class="xp-string">\'event\'</span><span class="xp-pred">]])]</span>'
            ),
            "prov_note": Markup(
                "<code>@corresp</code> und Personen in verschachtelten Events "
                "ausgeschlossen."
            ),
        },
        {
            "id": "events",
            "label": "Events",
            "glossary_id": "gloss-event",
            "glossary_term": "Event",
            "glossary_anchor": "event",
            "glossary_def": Markup(
                "Ein konkreter Vorgang im Quellentext: Rechtsgesch&auml;ft "
                "(Kauf, Schenkung &hellip;), Siegelvermerk, Kanzleieintrag "
                "oder Notiz."
            ),
            "total": total_events,
            "row_key": "events",
            "prov_id": "prov-total-events",
            "prov_title": "Events — Provenienz",
            "prov_xpath": Markup(
                '<span class="xp-axis">//</span><span class="xp-elem">tei:body</span>'
                '<span class="xp-axis">//</span><span class="xp-elem">tei:rs</span>'
                '<span class="xp-pred">[</span><span class="xp-attr">@type</span>='
                '<span class="xp-string">\'event\'</span><span class="xp-pred">]</span>\n'
                '<span class="xp-pred">  [not(</span>'
                '<span class="xp-axis">ancestor::</span><span class="xp-elem">tei:rs</span>'
                '<span class="xp-pred">[</span><span class="xp-attr">@type</span>='
                '<span class="xp-string">\'event\'</span><span class="xp-pred">])]</span>'
            ),
            "prov_note": Markup(
                "distinct &uuml;ber <code>@ref</code>; verschachtelte rs-Events "
                "ausgeschlossen."
            ),
        },
    ]


def _compute_corpus_breakdown():
    """Backward-compatible wrapper around _scan_released_tei for the start
    page Korpus-Matrix. Personen in mentioned Events sind ausgeschlossen
    (legacy-konsistent).
    """
    _, per_corpus = _scan_released_tei()
    return [
        {
            "path": c["path"],
            "label": c["label"],
            "sources": c["sources"],
            "mentions": c["person_mentions"],
            "events": c["distinct_events"],
        }
        for c in per_corpus
    ]


def _compute_release_kpis():
    """Compute the canonical released-data KPIs directly from TEI via XPath.

    Wraps :func:`_scan_released_tei`. The default values match the legacy
    frontend output:

    - ``sources_total``, ``sources_with_persons`` — file-level counts.
    - ``distinct_persons`` — distinct ``pe__``-keys across all
      person-annotations (including those inside mentioned rs-events).
    - ``person_mentions`` — mention count *outside* mentioned rs-events.
    - ``distinct_events`` — distinct top-level ``<rs type='event'>``.
    - ``register_total`` — size of the full person register
      (``indices/personList.xml``), shown for context.
    """
    import csv as _csv
    from pipeline.config import PIPELINE_OUTPUT

    totals, _ = _scan_released_tei()

    register_total = 0
    pe_path = PIPELINE_OUTPUT / "persons.csv"
    with pe_path.open(encoding="utf-8") as fh:
        register_total = sum(1 for _ in _csv.DictReader(fh, delimiter=";"))

    return {
        "sources_total": totals["sources"],
        "sources_with_persons": totals["sources_with_persons"],
        "distinct_persons": totals["distinct_persons"],
        "person_mentions": totals["person_mentions"],
        "distinct_events": totals["distinct_events"],
        "register_total": register_total,
    }


def _build_exploration(all_metadata, persons, env):
    """Build exploration hub + 4 subpages (roles, networks, transactions, places).

    Header-KPIs (Personen, Events, Geschlechter, Personen mit
    Institutionsbezug) sind auf den freigegebenen Korpus eingeschr&auml;nkt
    und stammen aus ``_compute_release_kpis()`` + ``_released_person_keys()``
    — gleiche XPath-Quelle wie Startseite und Analyse-Header.
    Normalisierungsrate kommt weiterhin aus ``epic_a.json``, weil sie
    eine Aggregator-Statistik &uuml;ber annotierte Verben ist und keine
    Personen-Z&auml;hlung.
    """
    # Load pre-computed epic_a.json
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

    # Aggregator-Coverage: nur die Normalisierungsrate aus epic_a verwenden
    # (Personen-/Event-Counts haben wir bereits released-only oben).
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

    # 1) Hub page
    hub_html = env.get_template("exploration.html").render(**shared_vars)
    (explore_dir / "index.html").write_text(hub_html, encoding="utf-8")
    print("  Exploration hub: exploration/index.html")

    # 2) Rollenexplorer (Epic A, fully functional)
    #    epic_a.json is already written to DATA_DIR by the aggregator — JS fetches it
    roles_html = env.get_template("exploration_roles.html").render(**shared_vars)
    (explore_dir / "roles.html").write_text(roles_html, encoding="utf-8")
    print("  Exploration subpage: exploration/roles.html")

    # 3) Transaktionsexplorer (Epic C)
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

    # 4) Netzwerkexplorer (Epic B)
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

    # 5) Ortsexplorer (Epic D)
    epic_d_path = DATA_DIR / "epic_d.json"
    if epic_d_path.exists():
        epic_d = json.loads(epic_d_path.read_text(encoding="utf-8"))
        cov_d = epic_d.get("coverage", {})
        places_vars = dict(
            epic_d_json=True,
            total_places=cov_d.get("total", 0),
            settlements_with_coords=cov_d.get("settlements_with_coords", 0),
            referenced_places=cov_d.get("referenced", 0),
            total_doc_links=cov_d.get("total_doc_links", 0),
        )
        places_html = env.get_template("exploration_places.html").render(
            **{**shared_vars, **places_vars})
    else:
        places_html = env.get_template("exploration_places.html").render(**shared_vars)
    (explore_dir / "places.html").write_text(places_html, encoding="utf-8")
    print("  Exploration subpage: exploration/places.html")


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
    (Zielseiten liegen außerhalb der Edition).

    Quelle ist bevorzugt das Edition-Repo (Sibling-Pfad), sonst KNOWLEDGE_DIR
    im Pipeline-Repo. Das ist derselbe Knowledge-Vault, nur je nach Setup
    unter anderem Pfad.
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

    import re as _re
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

    # Validate against epic_a if present (released-corpora org types).
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
            pass  # Validation is best-effort; do not block build.

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "categories.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  Categories: data/categories.json")


def _write_query_vocabulary():
    """Copy query_vocabulary.json from content/ to docs/data/.

    Vocabulary fuer den Satz-Builder der Analyse-Seite. Liefert Subjekte,
    Filter, Werte-Listen mit Verb-Phrasen, Gruppierungen und Aggregationen.
    Wird vom Satz-Builder im Browser geladen.
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


def _persons_with_org_released(released_persons):
    """Z&auml;hle distinct Personen aus dem Released-Set, die in mindestens
    einem Event mit einer Organisations-Verkn&uuml;pfung beteiligt sind.

    Liest persons_in_events.csv x orgs_in_events.csv und schneidet auf
    ``released_persons``. Idempotent gegen&uuml;ber Erst-Build (gibt 0
    zur&uuml;ck, wenn die Aggregator-CSVs nicht vorhanden sind).
    """
    try:
        from frontend.aggregator import _cached_csv
        pie_rows = _cached_csv("persons_in_events.csv")
        oie_rows = _cached_csv("orgs_in_events.csv")
    except Exception:
        return 0
    events_with_org = {r.get("event_key", "") for r in oie_rows
                       if r.get("event_key")}
    out = set()
    for r in pie_rows:
        pk = r.get("person_key", "")
        ek = r.get("event_key", "")
        if pk in released_persons and ek in events_with_org:
            out.add(pk)
    return len(out)


def _build_analysis(env):
    """Build analysis page (Composer-UI).

    Minimaler Build: nur Template-Render mit Asset-Versions-String fuer
    Cache-Busting der Composer-Skripte. Keine Header-KPIs mehr — KPIs
    leben jetzt im Composer selbst (live aus ``epic_*.json``).
    """
    from datetime import datetime
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
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "impressum.html").write_text(html, encoding="utf-8")
    print("  Impressum page: impressum.html")


def _copy_static():
    """Copy static assets to docs/static/."""
    target = DOCS_DIR / "static"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(str(STATIC_DIR), str(target))


def _tei_output_path(filepath):
    """Compute output path for TEI-XML source copy.

    Maps sources/{collection}/{sub}/done/{file}.xml
    to docs/tei/{collection}/{sub}/{file}.xml (strips 'done').
    """
    rel = filepath.relative_to(SOURCES_DIR)
    parts = [p for p in rel.parts if p != "done"]
    return DOCS_DIR / "tei" / Path(*parts)


def _copy_tei_sources():
    """Copy all 'done' TEI-XML sources to docs/tei/ for static download.

    Removes stale copies from previous builds before copying.
    """
    tei_dir = DOCS_DIR / "tei"
    if tei_dir.exists():
        shutil.rmtree(tei_dir)

    all_files = collect_source_files()
    done_files = [f for f in all_files if _is_done_file(f) and _is_released_file(f)]

    copied = 0
    for filepath in done_files:
        dest = _tei_output_path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(filepath), str(dest))
        copied += 1

    print(f"  TEI sources: {copied} files copied to docs/tei/")
