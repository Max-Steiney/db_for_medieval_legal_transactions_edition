"""TEI-Metadaten extrahieren und Document-HTML schreiben.

Pro-Quelle-Pipeline: TEI-XML laden, Header-Felder extrahieren, Body
rendern, Reverse-Index-Refs sammeln, Templates rendern, Datei schreiben.
"""

import sys
from collections import Counter

from pipeline.config import SOURCES_DIR, NS_MAP, REPO_ROOT
from pipeline.utils.xml_loader import load_xml
from pipeline.utils.text_utils import normalize_space, strip_hash
from pipeline.utils.date_parser import create_date

from frontend.config import DOCS_DIR
from frontend.renderer import render_document

from frontend.build._helpers import (
    _xpath_text, _collection_label, _normalize_facsimile_url,
    _extract_regest, _extract_entity_refs,
    _output_path, _relative_to_root, _tei_output_path,
)
from frontend.build._quality import _quality_score


def _extract_metadata(tree, filepath):
    """Extract document metadata from TEI header."""
    root = tree.getroot()

    iso_date = create_date(tree)

    title = _xpath_text(root, ".//tei:teiHeader//tei:titleStmt/tei:title") or filepath.stem
    date_display = _xpath_text(root, ".//tei:teiHeader//tei:profileDesc/tei:creation/tei:date") or iso_date
    place = _xpath_text(root, ".//tei:teiHeader//tei:profileDesc/tei:creation/tei:placeName")
    repository = _xpath_text(root, ".//tei:teiHeader//tei:repository")
    idno = _xpath_text(root, ".//tei:teiHeader//tei:msIdentifier/tei:idno") or filepath.stem
    source_url = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl[@type='url']")
    orig_date = _xpath_text(root, ".//tei:teiHeader//tei:origDate")

    citation = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl[@status='draft']")
    if not citation:
        citation = _xpath_text(root, ".//tei:teiHeader//tei:sourceDesc/tei:bibl")

    rel = filepath.relative_to(SOURCES_DIR)
    collection = rel.parts[0] if rel.parts else ""
    subcollection = rel.parts[1] if len(rel.parts) > 1 else ""
    collection_label = _collection_label(collection, subcollection)

    facsimile_urls = []
    for g in root.xpath(".//tei:facsimile//tei:graphic", namespaces=NS_MAP):
        normalized = _normalize_facsimile_url(g.get("url", ""), collection)
        if normalized:
            facsimile_urls.append(normalized)

    regest = _extract_regest(root)
    regest_full = _extract_regest(root, max_len=500)

    source_path = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

    person_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='person']", namespaces=NS_MAP
    ))
    org_count = len(root.xpath(
        ".//tei:text//tei:rs[@type='org']", namespaces=NS_MAP
    ))

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

    fn_role_counts = Counter()
    fn_role_person_ids = {}
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

    if quality_index:
        rel_key = str(filepath.relative_to(SOURCES_DIR)).replace("\\", "/")
        findings = quality_index.get(rel_key, [])
    else:
        findings = []
    meta["quality_score"] = _quality_score(findings)
    meta["quality_findings"] = findings
    meta["quality_count"] = len(findings)

    bodies = root.xpath(".//tei:text/tei:body", namespaces=NS_MAP)
    if not bodies:
        bodies = root.xpath(".//tei:body", namespaces=NS_MAP)
    if not bodies:
        print(f"  WARN: No <body> in {filepath}", file=sys.stderr)
        return None

    output = _output_path(filepath)
    root_path = _relative_to_root(output)
    body_html = render_document(bodies[0], registers, root_path)

    entity_refs = _extract_entity_refs(root)

    meta["url"] = str(output.relative_to(DOCS_DIR)).replace("\\", "/")
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
