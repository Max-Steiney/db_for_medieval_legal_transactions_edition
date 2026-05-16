"""Forschungsfragen-Verifikation (Stufe 4).

Die ersten drei Stufen pruefen TEI->JSON, CSV->HTML und TEI->HTML.
Diese vierte Stufe rechnet vier konkrete Forschungsfragen direkt aus
TEI/Indices/Pipeline-CSV neu und veroeffentlicht die Referenzzahlen.
Der Vergleich gegen das Frontend-Output kommt in einer spaeteren
Iteration; vorerst dient der Report als unabhaengiger Sollwert.

Aufruf:
    python -m verification.run --research-questions

Output:
    verification/reports/research_questions-YYYY-MM-DD.json
    verification/reports/research_questions-YYYY-MM-DD.md
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from lxml import etree

from pipeline.config import INDICES_DIR, NORM_LISTS_DIR, PIPELINE_OUTPUT
from verification.config import REPORTS_DIR, TEI_NS

_NS = {"tei": TEI_NS}


# --------------------------------------------------------------------- #
# CSV-Loader                                                            #
# --------------------------------------------------------------------- #

def _read_csv(path: Path, delimiter: str = ";") -> list[dict]:
    """Liest eine CSV als Liste von dicts. Robust gegen BOM."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return [row for row in reader]


# --------------------------------------------------------------------- #
# Frage 1: Uhlirz IV (Erzeugung und Vertrieb von Leuchtstoffen)         #
# --------------------------------------------------------------------- #

_UHLIRZ_IV_CATEGORY = "IV Erzeugung und Vertrieb von Leuchtstoffen Fetten und Oelen"

_MARRIAGE_TERMS = (
    "gemahl",      # Gemahl, gemahls, Gemahlin
    "gatte",       # Gatte, ehegatte
    "gattin",
    "hausfrau",    # Hausfrau, hausfraun
    "hawsfraw",    # mhd. Schreibvarianten Hausfrau
    "hausvrow",    # housvrowe, hausvrowe
    "ehemann",
    "ehefrau",
    "ehe",         # generischer Fallback (vom Aufgabentext explizit verlangt)
    "ehe|frau",
)


def _load_uhlirz_spelling_to_category() -> dict[str, str]:
    """Map roleName_spelling (lower) -> Gewerbe_nach_Uhlirz_GstW.

    Quelle: normalisation_lists/roleName_norm_matching.csv (TAB-delim).
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    mapping: dict[str, str] = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            spelling = (row.get("roleName_spelling") or "").strip().lower()
            category = (row.get("Gewerbe_nach_Uhlirz_GstW") or "").strip()
            if spelling and category:
                # erste Sichtung gewinnt (Norm-Liste ist 1:n, Lemma stabil)
                mapping.setdefault(spelling, category)
    return mapping


def _persons_in_category(category: str) -> tuple[set[str], set[str]]:
    """Personen und Quellen mit source_prof in `category`.

    Returns (person_keys, file_keys).
    """
    spelling_to_cat = _load_uhlirz_spelling_to_category()
    persons = _read_csv(PIPELINE_OUTPUT / "persons_in_sources.csv")

    person_keys: set[str] = set()
    file_keys: set[str] = set()
    for row in persons:
        prof = (row.get("source_prof") or "").strip().lower()
        if not prof:
            continue
        if spelling_to_cat.get(prof) == category:
            person_keys.add(row["person_key"])
            file_keys.add(row["file_key"])
    return person_keys, file_keys


def _is_marriage_kin(kin: str) -> bool:
    s = (kin or "").lower()
    return any(term in s for term in _MARRIAGE_TERMS)


def compute_uhlirz_iv_marriages() -> dict:
    """Heirats-Paare in Kategorie IV (Leuchtstoffe, Fette, Oele)."""
    person_keys, _ = _persons_in_category(_UHLIRZ_IV_CATEGORY)

    kin = _read_csv(PIPELINE_OUTPUT / "kin_relations_in_sources.csv")
    pairs: set[tuple[str, str]] = set()
    files: set[str] = set()
    for row in kin:
        if not _is_marriage_kin(row.get("kin", "")):
            continue
        a = row.get("person_key", "")
        b = row.get("related_key", "")
        if not a or not b:
            continue
        if a in person_keys or b in person_keys:
            pairs.add(tuple(sorted((a, b))))
            files.add(row.get("file_key", ""))

    return {
        "question_id": "uhlirz_iv_marriages",
        "category": _UHLIRZ_IV_CATEGORY,
        "persons_in_category": len(person_keys),
        "marriage_pairs_in_category": len(pairs),
        "source_files_involved": len(files),
    }


# --------------------------------------------------------------------- #
# Frage 2: Uhlirz VI (Lederindustrie) + Besitz + Geo-Koordinaten        #
# --------------------------------------------------------------------- #

_UHLIRZ_VI_CATEGORY_PREFIX = "VI Lederindustrie"


def _places_with_geo_from_xml() -> set[str]:
    """xml:ids aller `<tei:place>` mit `<tei:location/tei:geo>`."""
    path = INDICES_DIR / "placeList.xml"
    tree = etree.parse(str(path))
    ids: set[str] = set()
    for el in tree.getroot().xpath(
        "//tei:place[tei:location/tei:geo]", namespaces=_NS
    ):
        xml_id = el.get("{http://www.w3.org/XML/1998/namespace}id")
        if xml_id:
            ids.add(xml_id)
    return ids


def _resolve_category_persons(category_match) -> set[str]:
    """Personen mit source_prof in einer Kategorie (Praefix-Match)."""
    spelling_to_cat = _load_uhlirz_spelling_to_category()
    matching_spellings = {
        sp for sp, cat in spelling_to_cat.items() if category_match(cat)
    }
    persons = _read_csv(PIPELINE_OUTPUT / "persons_in_sources.csv")
    person_keys: set[str] = set()
    for row in persons:
        prof = (row.get("source_prof") or "").strip().lower()
        if prof and prof in matching_spellings:
            person_keys.add(row["person_key"])
    return person_keys


def compute_uhlirz_vi_ownership() -> dict:
    """Besitzverhaeltnisse in Kategorie VI (Lederindustrie)."""

    def _match(cat: str) -> bool:
        return cat.startswith(_UHLIRZ_VI_CATEGORY_PREFIX)

    person_keys = _resolve_category_persons(_match)

    # Besitz-Relationen: owner_relations_in_sources.csv referenziert
    # Personen ueber rel_key (Spalten-Pruefung: id;place_key;cert_place_key;
    # owner;rel_key;cert_topo_relation_key;event_key;xml_key).
    owner = _read_csv(PIPELINE_OUTPUT / "owner_relations_in_sources.csv")
    persons_with_ownership: set[str] = set()
    ownership_places: set[str] = set()
    for row in owner:
        person_key = (row.get("rel_key") or "").strip()
        place_key = (row.get("place_key") or "").strip()
        if person_key in person_keys:
            persons_with_ownership.add(person_key)
            if place_key:
                ownership_places.add(place_key)

    geo_ids = _places_with_geo_from_xml()
    places_with_coordinates = sum(1 for p in ownership_places if p in geo_ids)

    return {
        "question_id": "uhlirz_vi_ownership",
        "category": "VI Lederindustrie",
        "persons_in_category": len(person_keys),
        "persons_with_ownership": len(persons_with_ownership),
        "ownership_places": len(ownership_places),
        "places_with_coordinates": places_with_coordinates,
    }


# --------------------------------------------------------------------- #
# Frage 3: Occupations bei St. Stephan (inkl. Sub-Organisationen)       #
# --------------------------------------------------------------------- #

_ST_STEPHAN_ID = "org__wien-st_stephan"


def _suborgs_of(target_id: str) -> set[str]:
    """xml:ids der Ziel-Organisation und aller verschachtelten <org>."""
    path = INDICES_DIR / "orgList.xml"
    tree = etree.parse(str(path))
    xml_id_attr = "{http://www.w3.org/XML/1998/namespace}id"
    root_org = tree.getroot().xpath(
        f"//tei:org[@xml:id='{target_id}']", namespaces=_NS
    )
    if not root_org:
        return {target_id}
    result: set[str] = set()
    for org in root_org[0].iter(f"{{{TEI_NS}}}org"):
        xid = org.get(xml_id_attr)
        if xid:
            result.add(xid)
    return result


def compute_occ_st_stephan() -> dict:
    """Occupations bei St. Stephan (Haupt-Org + Sub-Orgs)."""
    main_only = {_ST_STEPHAN_ID}
    full = _suborgs_of(_ST_STEPHAN_ID)

    occ = _read_csv(PIPELINE_OUTPUT / "occ_relations_in_sources.csv")
    occ_main = 0
    occ_full = 0
    persons_full: set[str] = set()
    for row in occ:
        related = (row.get("related_key") or "").strip()
        if related in main_only:
            occ_main += 1
        if related in full:
            occ_full += 1
            person_key = (row.get("person_key") or "").strip()
            if person_key:
                persons_full.add(person_key)

    # Personen mit irgendeiner Kin-Relation (als person_key ODER related_key).
    kin = _read_csv(PIPELINE_OUTPUT / "kin_relations_in_sources.csv")
    persons_in_kin: set[str] = set()
    for row in kin:
        for col in ("person_key", "related_key"):
            v = (row.get(col) or "").strip()
            if v:
                persons_in_kin.add(v)
    persons_with_kin = len(persons_full & persons_in_kin)

    return {
        "question_id": "occ_st_stephan",
        "target_org": _ST_STEPHAN_ID,
        "occ_records_main_only": occ_main,
        "occ_records_including_suborgs": occ_full,
        "distinct_persons": len(persons_full),
        "persons_with_kin_relations": persons_with_kin,
    }


# --------------------------------------------------------------------- #
# Frage 4: Stiftungen rund um St. Agnes auf der Himmelpforte            #
# --------------------------------------------------------------------- #

_ST_AGNES_ID = "org__wien-st_agnes_auf_der_himmelpforte"


def compute_funding_st_agnes() -> dict:
    """Events mit St. Agnes auf der Himmelpforte als Aussteller bzw.
    Empfaenger, plus die Gegenpartei in der jeweils anderen Rolle."""
    orgs_in_events = _read_csv(PIPELINE_OUTPUT / "orgs_in_events.csv")
    persons_in_events = _read_csv(PIPELINE_OUTPUT / "persons_in_events.csv")

    issuer_events: set[str] = set()
    recipient_events: set[str] = set()
    for row in orgs_in_events:
        if row.get("org_key") != _ST_AGNES_ID:
            continue
        ev = row.get("event_key") or ""
        role = (row.get("event_role") or "").strip().lower()
        if role == "issuer":
            issuer_events.add(ev)
        elif role == "recipient":
            recipient_events.add(ev)

    issuer_persons_for_recipient: set[str] = set()
    issuer_orgs_for_recipient: set[str] = set()
    recipient_persons_for_issuer: set[str] = set()
    recipient_orgs_for_issuer: set[str] = set()

    # Personen-Gegenparteien
    for row in persons_in_events:
        ev = row.get("event_key") or ""
        role = (row.get("event_role") or "").strip().lower()
        person_key = row.get("person_key") or ""
        if not person_key:
            continue
        if ev in recipient_events and role == "issuer":
            issuer_persons_for_recipient.add(person_key)
        if ev in issuer_events and role == "recipient":
            recipient_persons_for_issuer.add(person_key)

    # Organisations-Gegenparteien (St. Agnes selbst rausnehmen)
    for row in orgs_in_events:
        ev = row.get("event_key") or ""
        role = (row.get("event_role") or "").strip().lower()
        org_key = row.get("org_key") or ""
        if not org_key or org_key == _ST_AGNES_ID:
            continue
        if ev in recipient_events and role == "issuer":
            issuer_orgs_for_recipient.add(org_key)
        if ev in issuer_events and role == "recipient":
            recipient_orgs_for_issuer.add(org_key)

    return {
        "question_id": "funding_st_agnes",
        "target_org": _ST_AGNES_ID,
        "events_as_issuer": len(issuer_events),
        "events_as_recipient": len(recipient_events),
        "issuer_persons_for_recipient_events": len(issuer_persons_for_recipient),
        "issuer_orgs_for_recipient_events": len(issuer_orgs_for_recipient),
        "recipient_persons_for_issuer_events": len(recipient_persons_for_issuer),
        "recipient_orgs_for_issuer_events": len(recipient_orgs_for_issuer),
    }


# --------------------------------------------------------------------- #
# Report-Aufbau                                                         #
# --------------------------------------------------------------------- #

ALL_QUESTIONS = (
    compute_uhlirz_iv_marriages,
    compute_uhlirz_vi_ownership,
    compute_occ_st_stephan,
    compute_funding_st_agnes,
)


def build_report() -> dict:
    results = [fn() for fn in ALL_QUESTIONS]
    return {
        "generated": date.today().isoformat(),
        "pipeline_output": str(PIPELINE_OUTPUT),
        "indices_dir": str(INDICES_DIR),
        "norm_lists_dir": str(NORM_LISTS_DIR),
        "questions": results,
    }


def _format_block(q: dict) -> list[str]:
    lines = [f"### {q['question_id']}", ""]
    for key, value in q.items():
        if key == "question_id":
            continue
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return lines


def _write_markdown(report: dict, path: Path) -> None:
    lines: list[str] = []
    lines.append("# Forschungsfragen-Verifikation")
    lines.append("")
    lines.append(f"Stand: {report['generated']}")
    lines.append("")
    lines.append(f"- Pipeline-Output: `{report['pipeline_output']}`")
    lines.append(f"- Indices: `{report['indices_dir']}`")
    lines.append(f"- Norm-Listen: `{report['norm_lists_dir']}`")
    lines.append("")
    lines.append(
        "Diese Stufe rechnet vier Forschungsfragen direkt aus TEI/Indices/"
        "Pipeline-CSV neu. Vergleich gegen das Frontend-Output folgt in"
        " einer spaeteren Iteration."
    )
    lines.append("")
    lines.append("## Ergebnisse")
    lines.append("")
    for q in report["questions"]:
        lines.extend(_format_block(q))
    path.write_text("\n".join(lines), encoding="utf-8")


def run_research_questions() -> dict:
    report = build_report()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = report["generated"]
    json_path = REPORTS_DIR / f"research_questions-{stamp}.json"
    md_path = REPORTS_DIR / f"research_questions-{stamp}.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_markdown(report, md_path)
    print(f"[verify] Forschungsfragen: {md_path}")
    print(f"[verify]                   {json_path}")
    for q in report["questions"]:
        keys = ", ".join(f"{k}={v}" for k, v in q.items() if k != "question_id")
        print(f"[verify]   {q['question_id']}: {keys}")
    return report
