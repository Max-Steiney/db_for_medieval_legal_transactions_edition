"""Extract TEI metadata and write per-document HTML.

Per-source pipeline: load TEI-XML, extract header fields, render body,
collect reverse-index refs, render templates, write file.
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


def _build_citation(root):
    """Compose a clean citation string from the TEI sourceDesc/bibl.

    Two corpus shapes:
    - QGW: a single text-only ``<bibl status='draft'>`` whose body looks like
      ``"Quellen zur Geschichte der Stadt Wien, Bd. II/1, Nr. 1033 As
      published in HAUrk by Wiener Stadt- und Landesarchiv"``. The
      ``As published in …``-tail is a Monasterium auto-injected note
      that breaks the reading flow and gets stripped.
    - Stadtbuecher: a structured ``<bibl>`` with nested ``<title>`` (main
      + sub), ``<author>``, ``<pubPlace>``, ``<publisher>`` children.
      We compose ``Authors, MainTitle. SubTitle. Place: Publisher.``
    """
    bibl = root.xpath(
        ".//tei:teiHeader//tei:sourceDesc/tei:bibl[@status='draft']",
        namespaces=NS_MAP,
    )
    if not bibl:
        bibl = root.xpath(
            ".//tei:teiHeader//tei:sourceDesc/tei:bibl[not(@type='url')]",
            namespaces=NS_MAP,
        )
    if not bibl:
        return ""
    b = bibl[0]

    titles_main = [normalize_space(t.text or "") for t in
                   b.xpath(".//tei:title[@type='main']", namespaces=NS_MAP)]
    titles_sub = [normalize_space(t.text or "") for t in
                  b.xpath(".//tei:title[@type='sub']", namespaces=NS_MAP)]
    authors = [normalize_space(a.text or "") for a in
               b.xpath("./tei:author", namespaces=NS_MAP)]
    pub_places = [normalize_space(p.text or "") for p in
                  b.xpath("./tei:pubPlace", namespaces=NS_MAP)]
    publishers = [normalize_space(p.text or "") for p in
                  b.xpath("./tei:publisher", namespaces=NS_MAP)]

    if titles_main or authors or publishers:
        parts = []
        if authors:
            parts.append(" / ".join(a for a in authors if a))
        if titles_main:
            main = " / ".join(t for t in titles_main if t)
            if titles_sub:
                main = main + ". " + " / ".join(t for t in titles_sub if t)
            parts.append(main)
        if pub_places or publishers:
            place = "/".join(p for p in pub_places if p)
            pub = " ".join(p for p in publishers if p)
            tail = ": ".join(s for s in (place, pub) if s)
            if tail:
                parts.append(tail)
        composed = ". ".join(p for p in parts if p)
        return composed.rstrip(".") + "." if composed else ""

    text = normalize_space("".join(b.itertext()))
    text = _re.sub(r"\s+As published in [^.]*$", "", text, flags=_re.IGNORECASE).strip()
    return text


import re as _re


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

    citation = _build_citation(root)

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

    # Provenance-Anzeige "X Pers., Y Org." meint individuelle
    # Entitaeten (Glossar: "Individuelle Person") und nicht die Summe
    # aller Nennungen ("Gesamtnennung"). Refs deduplizieren, damit der
    # Wert mit der Annotations-Summary-Zeile in der UI uebereinstimmt.
    # Eintraege ohne ref (orphan spans) zaehlen je einmal pro Vorkommen.
    person_refs = root.xpath(
        ".//tei:text//tei:rs[@type='person']/@ref", namespaces=NS_MAP
    )
    person_orphans = root.xpath(
        ".//tei:text//tei:rs[@type='person'][not(@ref)]", namespaces=NS_MAP
    )
    person_count = (
        len({strip_hash(r) for r in person_refs if r and strip_hash(r) != "NULL"})
        + len(person_orphans)
    )
    org_refs = root.xpath(
        ".//tei:text//tei:rs[@type='org']/@ref", namespaces=NS_MAP
    )
    org_orphans = root.xpath(
        ".//tei:text//tei:rs[@type='org'][not(@ref)]", namespaces=NS_MAP
    )
    org_count = (
        len({strip_hash(r) for r in org_refs if r and strip_hash(r) != "NULL"})
        + len(org_orphans)
    )

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


def _parse_file(filepath, registers):
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
