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
import markdown as markdown_lib

from pipeline.config import SOURCES_DIR, NS_MAP, REPO_ROOT


_GERMAN_MONTHS = [
    "Januar", "Februar", "M\u00e4rz", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _format_german_date(dt):
    """Format a date as '17. April 2026'."""
    return f"{dt.day}. {_GERMAN_MONTHS[dt.month - 1]} {dt.year}"


def _transmission_form(collection_path):
    """Map a collection path to a human-readable transmission/edition form.

    QGW-based corpora: Regest plus Faksimile (summarised catalogue entries linked
    to digitised images). Stadtbuecher: edierter Volltext (full edited text).
    Unknown paths fall back to 'Regest'.
    """
    cp = (collection_path or "").lower()
    if cp.startswith("stadtbuecher"):
        return "Volltext"
    if cp.startswith("qgw"):
        return "Regest + Faksimile"
    return "Regest"


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
    # Build statistics dashboard
    _build_statistics(all_metadata, persons, orgs, places, reverse_index, env)

    # Build exploration page (V1 shared + V2 Epic A)
    _build_exploration(all_metadata, persons, env)

    # Build guidelines page
    _build_guidelines(env)

    # Build about page + impressum
    _build_about(env)
    _build_impressum(env)

    # Build glossary + analysis placeholder page
    _build_glossary(env)
    _build_analysis(env)

    # Build quality dashboard (M2)
    _build_quality_dashboard(all_metadata, quality_index, env)

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


def _build_index(all_metadata, env, register_counts=None):
    """Build the index/browse page."""
    # Sort by date, then collection
    all_metadata.sort(key=lambda m: (m.get("date_iso", ""), m.get("collection", "")))

    # Prepare JSON for client-side search
    search_data = []
    for m in all_metadata:
        search_data.append({
            "t": m.get("regest", "") or m.get("title", ""),
            "tf": m.get("regest_full", "") or m.get("regest", ""),
            "d": m.get("date_display", ""),
            "di": m.get("date_iso", ""),
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
                "form": _transmission_form(path_key),
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
    total_docs = len(all_metadata)
    total_persons = len(persons)
    total_orgs = len(orgs)
    total_places = len(places)
    sex_m = sum(1 for p in persons.values() if p.get("sex") == "m")
    sex_f = sum(1 for p in persons.values() if p.get("sex") == "f")

    template = env.get_template("startseite.html")
    html = template.render(
        total_docs=total_docs,
        total_persons=total_persons,
        total_orgs=total_orgs,
        total_places=total_places,
        sex_m=sex_m,
        sex_f=sex_f,
        collection_count=len(collections),
        collections=collections,
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


def _person_search_data(persons, reverse_index):
    """Build compact JSON list for the persons register page."""
    data = []
    for xml_id, p in persons.items():
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
    abgeschlossen ist.
    """
    template = env.get_template("register_list.html")
    placeholder_tpl = env.get_template("register_placeholder.html")

    RELEASED = {"persons"}  # bei Freigabe um "organisations", "places" ergänzen

    configs = [
        ("persons", "Personen", persons, _person_search_data),
        ("organisations", "Organisationen", orgs, _org_search_data),
        ("places", "Orte", places, _place_search_data),
    ]

    for reg_type, label, register, data_fn in configs:
        out = DOCS_DIR / "register" / f"{reg_type}.html"
        out.parent.mkdir(parents=True, exist_ok=True)

        if reg_type not in RELEASED:
            html = placeholder_tpl.render(
                register_label=label,
                build_date=_format_german_date(date.today()),
                root_path="..",
            )
            out.write_text(html, encoding="utf-8")
            print(f"  Register placeholder: register/{reg_type}.html (nicht freigegeben)")
            continue

        search_data = data_fn(register, reverse_index)

        # Write search data to external JSON file (reduces page size)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"{reg_type}_search.json").write_text(
            json.dumps(search_data, ensure_ascii=False), encoding="utf-8"
        )

        # Collect unique types/sexes for filter dropdowns
        if reg_type == "persons":
            filter_values = sorted({p["sex"] for p in register.values() if p["sex"]})
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
            total_count=len(register),
            filter_values=filter_values,
            filter_label=filter_label,
            filter_map=filter_map,
            root_path="..",
        )

        out.write_text(html, encoding="utf-8")
        print(f"  Register list: register/{reg_type}.html ({len(register)} entries)")


def _build_register_json(reverse_index):
    """Write reverse-index data as JSON files for client-side detail views."""
    out_dir = DOCS_DIR / "register"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Split by ID prefix — keys match register page filenames
    buckets = {"persons": {}, "organisations": {}, "places": {}}
    for eid, docs in reverse_index.items():
        if eid.startswith("pe__"):
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


def _build_statistics(all_metadata, persons, orgs, places, reverse_index, env):
    """Build the statistics dashboard page with embedded JSON for client-side charts."""

    total_docs = len(all_metadata)

    # --- Date range + timeline ---
    decade_counts = Counter()
    century_counts = Counter()
    collection_decade_counts = {}   # {collection_path: Counter(decade -> count)}
    collection_fn_roles = {}        # {collection_path: Counter(role -> count)}
    collection_fn_roles_sex = {}    # {collection_path: {role: Counter(sex -> count)}}
    all_years = []

    for m in all_metadata:
        cp = m.get("collection_path", "")
        year_str = m.get("date_iso", "")[:4]
        if year_str.isdigit():
            year = int(year_str)
            all_years.append(year)
            decade = (year // 10) * 10
            decade_counts[decade] += 1
            century = (year // 100) * 100
            century_counts[century] += 1
            collection_decade_counts.setdefault(cp, Counter())[decade] += 1

        # Per-collection function role totals
        for role, count in m.get("fn_role_counts", {}).items():
            collection_fn_roles.setdefault(cp, Counter())[role] += count

        # Per-collection function role + gender (person-level)
        for role, pids in m.get("fn_role_person_ids", {}).items():
            canonical = role if role in ("issuer", "recipient", "witness") else "other"
            role_sex = collection_fn_roles_sex.setdefault(cp, {})
            for pid in pids:
                sex = persons.get(pid, {}).get("sex", "u")
                role_sex.setdefault(canonical, Counter())[sex] += 1

    min_year = min(all_years) if all_years else 1177
    max_year = max(all_years) if all_years else 1524

    # Fill gaps in decade timeline
    if decade_counts:
        min_decade = min(decade_counts.keys())
        max_decade = max(decade_counts.keys())
        timeline_data = [
            {"decade": d, "count": decade_counts.get(d, 0)}
            for d in range(min_decade, max_decade + 10, 10)
        ]
    else:
        timeline_data = []

    century_data = [{"century": c, "count": n} for c, n in sorted(century_counts.items())]

    # --- Facsimile count ---
    facs_count = sum(1 for m in all_metadata if m.get("has_facsimile"))
    facs_pct = round(facs_count / total_docs * 100, 1) if total_docs else 0

    # --- Annotation depth ---
    total_annotations = 0
    fn_role_totals = Counter()
    annotation_breakdown = Counter()
    person_histogram = Counter()  # fine-grained: person_count -> num_docs

    for m in all_metadata:
        pc = m.get("person_count", 0)
        oc = m.get("org_count", 0)
        ec = m.get("event_count", 0)
        fc = m.get("fn_count", 0)
        rc = m.get("rolename_count", 0)
        tc = m.get("triggerstring_count", 0)
        total_annotations += pc + oc + ec + fc + rc + tc

        annotation_breakdown["persons"] += pc
        annotation_breakdown["orgs"] += oc
        annotation_breakdown["events"] += ec
        annotation_breakdown["functions"] += fc
        annotation_breakdown["rolenames"] += rc
        annotation_breakdown["triggerstrings"] += tc

        # Fine-grained person count histogram (cap display at 30+)
        person_histogram[min(pc, 30)] += 1

        # Function role breakdown
        for role, count in m.get("fn_role_counts", {}).items():
            fn_role_totals[role] += count

    avg_annotations = round(total_annotations / total_docs, 1) if total_docs else 0

    # --- Gender breakdown per function role (corpus-wide) ---
    fn_role_sex = {}  # {role: Counter(sex -> count)}
    for m in all_metadata:
        for role, pids in m.get("fn_role_person_ids", {}).items():
            canonical = role if role in ("issuer", "recipient", "witness") else "other"
            for pid in pids:
                sex = persons.get(pid, {}).get("sex", "u")
                fn_role_sex.setdefault(canonical, Counter())[sex] += 1

    person_histogram_data = [
        {"bucket": i, "count": person_histogram.get(i, 0)}
        for i in range(31)
    ]

    # --- Entity coverage ---
    person_linked = sum(1 for pid in persons if pid in reverse_index)
    org_linked = sum(1 for oid in orgs if oid in reverse_index)
    place_linked = sum(1 for plid in places if plid in reverse_index)

    def _pct(linked, total):
        return round(linked / total * 100, 1) if total else 0

    coverage = {
        "persons": {"linked": person_linked, "total": len(persons),
                     "pct": _pct(person_linked, len(persons))},
        "orgs": {"linked": org_linked, "total": len(orgs),
                  "pct": _pct(org_linked, len(orgs))},
        "places": {"linked": place_linked, "total": len(places),
                    "pct": _pct(place_linked, len(places))},
    }

    # --- Top-10 most referenced ---
    def _top_entities(source, register, name_fn, filter_fn=None, n=10):
        """Rank entities by reference count, return top N."""
        items = (
            (eid, cnt if isinstance(cnt, int) else len(cnt))
            for eid, cnt in source.items()
            if eid in register and (filter_fn is None or filter_fn(register[eid]))
        )
        ranked = sorted(items, key=lambda x: x[1], reverse=True)[:n]
        return [{"id": eid, "name": name_fn(register[eid]), "count": cnt}
                for eid, cnt in ranked]

    _person_name = lambda p: p["display"]
    _org_name = lambda o: o["name"]
    _is_female = lambda p: p["sex"] == "f"
    _is_male = lambda p: p["sex"] == "m"

    # Corpus-wide: source is reverse_index (eid -> list of docs)
    ri_counts = {eid: len(docs) for eid, docs in reverse_index.items()}
    top_women = _top_entities(ri_counts, persons, _person_name, _is_female)
    top_men = _top_entities(ri_counts, persons, _person_name, _is_male)
    top_orgs = _top_entities(ri_counts, orgs, _org_name)

    # --- Per-collection top-10 (for cross-filtering) ---
    collection_entity_counts = {}  # {cp: Counter(eid -> count)}
    for eid, docs in reverse_index.items():
        for doc_entry in docs:
            cp = doc_entry.get("collection_path", "")
            collection_entity_counts.setdefault(cp, Counter())[eid] += 1

    per_collection_top = {}
    for cp, entity_counter in collection_entity_counts.items():
        per_collection_top[cp] = {
            "women": _top_entities(entity_counter, persons, _person_name, _is_female),
            "men": _top_entities(entity_counter, persons, _person_name, _is_male),
            "orgs": _top_entities(entity_counter, orgs, _org_name),
        }

    # --- Collection comparison ---
    collection_stats = {}
    for m in all_metadata:
        cp = m.get("collection_path", "")
        if cp not in collection_stats:
            collection_stats[cp] = {
                "label": m.get("collection_label", cp),
                "docs": 0, "years": [], "person_sum": 0, "facs": 0,
            }
        cs = collection_stats[cp]
        cs["docs"] += 1
        year_str = m.get("date_iso", "")[:4]
        if year_str.isdigit():
            cs["years"].append(int(year_str))
        cs["person_sum"] += m.get("person_count", 0)
        if m.get("has_facsimile"):
            cs["facs"] += 1

    collections_json = []
    for cp, cs in sorted(collection_stats.items()):
        date_range = ""
        if cs["years"]:
            date_range = f"{min(cs['years'])}–{max(cs['years'])}"
        avg_persons = round(cs["person_sum"] / cs["docs"], 1) if cs["docs"] else 0
        coll_facs_pct = round(cs["facs"] / cs["docs"] * 100) if cs["docs"] else 0
        collections_json.append({
            "path": cp,
            "label": cs["label"],
            "docs": cs["docs"],
            "dateRange": date_range,
            "avgPersons": avg_persons,
            "facsPct": coll_facs_pct,
            "facsCount": cs["facs"],
            "pctOfTotal": round(cs["docs"] / total_docs * 100, 1) if total_docs else 0,
            "decades": dict(collection_decade_counts.get(cp, {})),
            "fnRoles": dict(collection_fn_roles.get(cp, {})),
            "fnRolesSex": {role: dict(counts)
                           for role, counts in collection_fn_roles_sex.get(cp, {}).items()},
        })

    # --- Top persons by event participation (across all roles) ---
    person_event_counts = Counter()  # person_id -> total mentions
    person_role_breakdown = {}       # person_id -> {role: count}
    for m in all_metadata:
        for role, pids in m.get("fn_role_person_ids", {}).items():
            canonical = role if role in ("issuer", "recipient", "witness") else "other"
            for pid in pids:
                person_event_counts[pid] += 1
                person_role_breakdown.setdefault(pid, Counter())[canonical] += 1

    top_persons = []
    for pid, total in person_event_counts.most_common(20):
        if pid not in persons:
            continue
        p = persons[pid]
        roles = dict(person_role_breakdown.get(pid, {}))
        top_persons.append({
            "id": pid,
            "name": p["display"],
            "sex": p.get("sex", "u"),
            "total": total,
            "roles": roles,
        })
        if len(top_persons) >= 20:
            break

    # --- Build comprehensive JSON for client-side charts ---
    stats_json = {
        "summary": {
            "totalDocs": total_docs,
            "totalPersons": len(persons),
            "totalOrgs": len(orgs),
            "totalPlaces": len(places),
            "dateRange": f"ca.\u00a0{min_year}\u2013{max_year}",
            "facsCount": facs_count,
            "facsPct": facs_pct,
            "totalAnnotations": total_annotations,
            "avgAnnotations": avg_annotations,
            "totalWomen": sum(1 for p in persons.values() if p["sex"] == "f"),
            "totalMen": sum(1 for p in persons.values() if p["sex"] == "m"),
        },
        "timeline": timeline_data,
        "centuries": century_data,
        "collections": collections_json,
        "fnRoles": dict(fn_role_totals),
        "fnRolesSex": {role: dict(counts) for role, counts in fn_role_sex.items()},
        "annotationBreakdown": dict(annotation_breakdown),
        "personDistribution": person_histogram_data,
        "coverage": coverage,
        "topWomen": top_women,
        "topMen": top_men,
        "topOrgs": top_orgs,
        "topPersons": top_persons,
        "perCollectionTop": per_collection_top,
    }

    # --- Render ---
    template = env.get_template("statistics.html")
    html = template.render(
        build_date=_format_german_date(date.today()),
        stats_data_json=json.dumps(stats_json, ensure_ascii=False),
        # Server-side variables for no-JS fallback header
        total_docs=total_docs,
        total_persons=len(persons),
        total_women=sum(1 for p in persons.values() if p["sex"] == "f"),
        total_men=sum(1 for p in persons.values() if p["sex"] == "m"),
        total_orgs=len(orgs),
        total_places=len(places),
        date_range=f"ca.\u00a0{min_year}\u2013{max_year}",
        facs_count=facs_count,
        facs_pct=facs_pct,
        total_annotations=total_annotations,
        avg_annotations=avg_annotations,
        root_path="..",
    )

    out = DOCS_DIR / "project" / "statistics.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("  Statistics page: project/statistics.html")


def _build_quality_dashboard(all_metadata, quality_index, env):
    """Build the quality dashboard page (M2)."""
    total_files = len(all_metadata)
    files_with_findings = sum(1 for m in all_metadata if m.get("quality_count", 0) > 0)
    files_ok = sum(1 for m in all_metadata if m.get("quality_score", 0) == 0)
    files_notice = sum(1 for m in all_metadata if m.get("quality_score", 0) == 1)
    files_warning = sum(1 for m in all_metadata if m.get("quality_score", 0) == 2)

    # Per-category breakdown
    by_category = Counter()
    by_severity = Counter()
    by_collection = {}
    for m in all_metadata:
        for f in m.get("quality_findings", []):
            by_category[f["category"]] += 1
            by_severity[f["severity"]] += 1
        cp = m.get("collection_path", "")
        cl = m.get("collection_label", cp)
        if cp not in by_collection:
            by_collection[cp] = {
                "label": cl, "total": 0, "ok": 0, "notice": 0, "warning": 0,
            }
        by_collection[cp]["total"] += 1
        score = m.get("quality_score", 0)
        if score == 0:
            by_collection[cp]["ok"] += 1
        elif score == 1:
            by_collection[cp]["notice"] += 1
        else:
            by_collection[cp]["warning"] += 1

    total_findings = sum(by_severity.values())

    # Per-file data for export
    file_quality = []
    for m in all_metadata:
        file_quality.append({
            "file": m.get("source_path", ""),
            "idno": m.get("idno", ""),
            "collection": m.get("collection_label", ""),
            "score": m.get("quality_score", 0),
            "count": m.get("quality_count", 0),
            "categories": ";".join(sorted({f["category"]
                                           for f in m.get("quality_findings", [])})),
        })

    quality_json = {
        "summary": {
            "totalFiles": total_files,
            "filesWithFindings": files_with_findings,
            "filesOk": files_ok,
            "filesNotice": files_notice,
            "filesWarning": files_warning,
            "totalFindings": total_findings,
        },
        "bySeverity": dict(by_severity),
        "byCategory": [
            {"category": cat, "count": cnt}
            for cat, cnt in by_category.most_common()
        ],
        "byCollection": [
            {"path": cp, **data}
            for cp, data in sorted(by_collection.items())
        ],
        "files": file_quality,
    }

    template = env.get_template("quality.html")
    html = template.render(
        build_date=_format_german_date(date.today()),
        quality_data_json=json.dumps(quality_json, ensure_ascii=False),
        total_files=total_files,
        files_ok=files_ok,
        files_notice=files_notice,
        files_warning=files_warning,
        total_findings=total_findings,
        root_path="..",
    )

    out = DOCS_DIR / "project" / "quality.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  Quality dashboard: project/quality.html ({total_findings} findings)")


def _build_exploration(all_metadata, persons, env):
    """Build exploration hub + 4 subpages (roles, networks, transactions, places)."""
    # Load pre-computed epic_a.json
    epic_a_path = DATA_DIR / "epic_a.json"
    if not epic_a_path.exists():
        print("  WARN: epic_a.json not found, skipping exploration pages.",
              file=sys.stderr)
        return

    total_docs = len(all_metadata)
    total_persons = len(persons)
    sex_m = sum(1 for p in persons.values() if p.get("sex") == "m")
    sex_f = sum(1 for p in persons.values() if p.get("sex") == "f")
    sex_u = total_persons - sex_m - sex_f

    # Parse epic_a for event count and normalisation rate (JS fetches it directly)
    epic_a = json.loads(epic_a_path.read_text(encoding="utf-8"))
    total_events = epic_a.get("coverage", {}).get("total_events", 0)
    norm_rate = epic_a.get("coverage", {}).get("normalisation_rate", 0)
    norm_rate_pct = round(norm_rate / total_events * 100, 1) if total_events else 0
    persons_with_org = epic_a.get("coverage", {}).get("persons_with_org", 0)
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
    """Build edition guidelines page from Markdown source."""
    md_path = CONTENT_DIR / "edition_guidelines.md"
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


def _build_analysis(env):
    """Build analysis placeholder page (classical query mode, content TBD)."""
    template = env.get_template("analysis.html")
    html = template.render(
        build_date=_format_german_date(date.today()),
        root_path="..",
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
