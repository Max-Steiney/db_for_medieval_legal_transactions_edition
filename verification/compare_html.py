"""HTML-Coverage: Pipeline-CSV vs. gerenderte Profil-Seite.

Prueft, ob die strukturierten Daten, die der Aggregator aus den Pipeline-
CSVs an das Frontend uebergibt, im gerenderten HTML auch sichtbar
erscheinen. Eingangs-Stufe ist also die Aggregator-Eingabe (CSV-Werte
plus Register-XML), Ausgangs-Stufe das HTML.

Architektonisches Ziel: jeder Inhalt, den das Frontend zeigt, wird auch
durch die TEI gedeckt. Wenn das HTML einen Namen rendert, der im
Register nicht steht, ist das ein Bug (Mismatch). Wenn das Register
einen Belegt-Zeitraum hat, der im HTML fehlt, ist das ein Bug
(Mismatch). Wenn beide gleich sind, ist das ein Match.

Die andere Richtung (Register-Werte, die explizit NICHT im HTML erscheinen
sollen) ist in ``contract.py`` als "filter" deklariert und wird hier
geehrt.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from verification import compare, parse_html
from verification.config import PIPELINE_ROOT


CheckResult = compare.CheckResult


def _check_reader_health() -> List[CheckResult]:
    """Prueft, ob alle Profil- und Quellen-HTMLs parsebar sind.

    Beim Build laufen Pipeline und Renderer parallel. Ein Single-File-Crash
    (Datei wird gerade geschrieben, ist leer oder hat ein abgeschnittenes
    Markup) wuerde frueher den ganzen Lauf killen. Jetzt liefert
    parse_html.read_*-Funktionen ein leeres Datenobjekt mit
    read_failed=True; dieser Check sammelt die betroffenen IDs in einem
    eigenen mismatch-Result, damit Lese-Probleme nicht von echten Daten-
    mismatches verschluckt werden.
    """
    failed_persons: List[str] = []
    failed_orgs: List[str] = []
    failed_docs: List[str] = []

    for path in parse_html.iter_person_profiles():
        p = parse_html.read_person_profile(path)
        if p.read_failed:
            failed_persons.append(p.pe_id)

    for path in parse_html.iter_org_profiles():
        o = parse_html.read_org_profile(path)
        if o.read_failed:
            failed_orgs.append(o.org_id)

    for path in parse_html.iter_documents():
        d = parse_html.read_document(path)
        if d.read_failed:
            # Relativer Pfad fuer den Report
            try:
                rel = path.relative_to(path.parents[3])
            except (ValueError, IndexError):
                rel = path.name
            failed_docs.append(str(rel))

    results: List[CheckResult] = []

    def _emit(name: str, ids: List[str]) -> None:
        if ids:
            sample = ", ".join(ids[:5])
            if len(ids) > 5:
                sample += f" (+{len(ids) - 5} weitere)"
            results.append(CheckResult(
                name=name, tei=0, json=len(ids), status="mismatch",
                note=(
                    "HTML-Dateien nicht parsebar (leer, abgeschnitten, oder "
                    f"Schreibkollision): {sample}"
                ),
            ))
        else:
            results.append(CheckResult(name=name, tei=0, json=0, status="match"))

    _emit("html.reader_health.persons", failed_persons)
    _emit("html.reader_health.orgs", failed_orgs)
    _emit("html.reader_health.documents", failed_docs)
    return results


def _load_persons_csv() -> Dict[str, Dict[str, str]]:
    """persons.csv aus pipeline/output in einen Lookup pe__id -> Row."""
    out: Dict[str, Dict[str, str]] = {}
    path = PIPELINE_ROOT / "pipeline" / "output" / "persons.csv"
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            pid = (r.get("id") or "").strip()
            if pid:
                out[pid] = r
    return out


def _load_orgs_csv() -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    path = PIPELINE_ROOT / "pipeline" / "output" / "organisations.csv"
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            oid = (r.get("id") or "").strip()
            if oid:
                out[oid] = r
    return out


def _expected_display_name(row: Dict[str, str]) -> str:
    """Wie der Aggregator den Display-Namen zusammensetzt (siehe
    aggregator/person_profiles.py::_display_name)."""
    parts = [
        (row.get("forename_reg") or "").strip(),
        (row.get("surname_reg") or "").strip(),
        (row.get("addname_reg") or "").strip(),
    ]
    return " ".join(p for p in parts if p) or row.get("id", "")


def check_person_profiles(
    sample_size: Optional[int] = None,
) -> List[CheckResult]:
    """Prueft jedes gerenderte Personenprofil-HTML gegen persons.csv.

    Felder, die heute gegengeprueft werden:
    - Display-Name (forename + surname + addName aus den _reg-Spalten)
    - sex-Label (m -> "männlich", f -> "weiblich", sonst Standardtext)

    Felder, die spaeter (M6c) ergaenzt werden:
    - Belegt-Zeitraum (aus reverse_index, schwer ohne Build-Run)
    - death_display, authority_urls, source_titles
    """
    results: List[CheckResult] = []
    persons_csv = _load_persons_csv()
    if not persons_csv:
        results.append(CheckResult(
            name="html.persons.csv_loaded",
            tei="present",
            json="missing",
            status="known_gap",
            note="persons.csv aus Pipeline-Output nicht gefunden",
        ))
        return results

    sex_label_map = {"m": "männlich", "f": "weiblich"}
    default_sex_label = "Geschlecht unbestimmt"

    paths = parse_html.iter_person_profiles()
    if sample_size:
        paths = paths[:sample_size]

    name_mismatches: List[Dict[str, Any]] = []
    sex_mismatches: List[Dict[str, Any]] = []
    missing_in_csv: List[str] = []

    for path in paths:
        p = parse_html.read_person_profile(path)
        if p.read_failed:
            continue
        row = persons_csv.get(p.pe_id)
        if row is None:
            missing_in_csv.append(p.pe_id)
            continue

        expected = _expected_display_name(row)
        if p.display_name and expected and p.display_name != expected:
            name_mismatches.append({
                "id": p.pe_id,
                "html": p.display_name,
                "csv": expected,
            })

        expected_sex = sex_label_map.get(
            (row.get("sex") or "").strip(), default_sex_label
        )
        if p.sex_label and p.sex_label != expected_sex:
            sex_mismatches.append({
                "id": p.pe_id,
                "html": p.sex_label,
                "csv_sex": row.get("sex") or "",
                "csv_label": expected_sex,
            })

    results.append(CheckResult(
        name="html.persons.profiles_checked",
        tei=len(paths),
        json=len(paths) - len(missing_in_csv),
        status="info",
        note=f"{len(missing_in_csv)} Profile ohne CSV-Match",
    ))

    if missing_in_csv:
        results.append(CheckResult(
            name="html.persons.profile_without_csv_row",
            tei=0,
            json=len(missing_in_csv),
            status="mismatch",
            note=(
                "Profile fuer IDs, die nicht in persons.csv stehen: "
                + ", ".join(missing_in_csv[:5])
                + (f" (+{len(missing_in_csv) - 5} weitere)" if len(missing_in_csv) > 5 else "")
            ),
        ))

    if name_mismatches:
        sample = "; ".join(
            f"{m['id']}: HTML='{m['html']}' vs CSV='{m['csv']}'"
            for m in name_mismatches[:3]
        )
        results.append(CheckResult(
            name="html.persons.display_name_mismatch",
            tei=0,
            json=len(name_mismatches),
            status="mismatch",
            note=f"Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="html.persons.display_name_mismatch",
            tei=0,
            json=0,
            status="match",
        ))

    if sex_mismatches:
        sample = "; ".join(
            f"{m['id']}: HTML='{m['html']}' vs CSV-sex='{m['csv_sex']}'"
            for m in sex_mismatches[:3]
        )
        results.append(CheckResult(
            name="html.persons.sex_label_mismatch",
            tei=0,
            json=len(sex_mismatches),
            status="mismatch",
            note=f"Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="html.persons.sex_label_mismatch",
            tei=0,
            json=0,
            status="match",
        ))

    # Source-Count-Konsistenz: Header sagt "Quellen: N", Tabelle hat N
    # Zeilen. Diese Probe hat in der Stichprobe Wilhelm bereits 62 vs.
    # 63 gezeigt - ein echter Drift.
    count_mismatches: List[Dict[str, Any]] = []
    for path in paths:
        p = parse_html.read_person_profile(path)
        if p.read_failed or p.source_count_displayed is None:
            continue
        if p.source_count_displayed != len(p.source_idnos):
            count_mismatches.append({
                "id": p.pe_id,
                "header": p.source_count_displayed,
                "rows": len(p.source_idnos),
            })

    if count_mismatches:
        sample = "; ".join(
            f"{m['id']}: header={m['header']} rows={m['rows']}"
            for m in count_mismatches[:3]
        )
        results.append(CheckResult(
            name="html.persons.source_count_vs_rows",
            tei=0,
            json=len(count_mismatches),
            status="mismatch",
            note=f"Header-Count weicht von Tabellen-Zeilen ab. Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="html.persons.source_count_vs_rows",
            tei=0,
            json=0,
            status="match",
        ))

    return results


def check_org_profiles(sample_size: Optional[int] = None) -> List[CheckResult]:
    """Analog zu check_person_profiles, fuer Organisations-Profile."""
    results: List[CheckResult] = []
    orgs_csv = _load_orgs_csv()
    if not orgs_csv:
        results.append(CheckResult(
            name="html.orgs.csv_loaded",
            tei="present",
            json="missing",
            status="known_gap",
            note="organisations.csv aus Pipeline-Output nicht gefunden",
        ))
        return results

    paths = parse_html.iter_org_profiles()
    if sample_size:
        paths = paths[:sample_size]

    name_mismatches: List[Dict[str, Any]] = []
    count_mismatches: List[Dict[str, Any]] = []
    missing_in_csv: List[str] = []

    for path in paths:
        o = parse_html.read_org_profile(path)
        if o.read_failed:
            continue
        row = orgs_csv.get(o.org_id)
        if row is None:
            missing_in_csv.append(o.org_id)
            continue

        # Name: split_pipe_names liefert Haupt-Name links vom "|"; hier
        # vergleichen wir nur den Pre-Pipe-Teil von name_reg.
        raw = (row.get("name_reg") or row.get("name_orig") or o.org_id).strip()
        expected = raw.split("|", 1)[0].strip() or o.org_id
        if o.name and expected and o.name != expected:
            name_mismatches.append({
                "id": o.org_id,
                "html": o.name,
                "csv": expected,
            })

        if o.source_count_displayed is not None:
            if o.source_count_displayed != len(o.source_idnos):
                count_mismatches.append({
                    "id": o.org_id,
                    "header": o.source_count_displayed,
                    "rows": len(o.source_idnos),
                })

    results.append(CheckResult(
        name="html.orgs.profiles_checked",
        tei=len(paths),
        json=len(paths) - len(missing_in_csv),
        status="info",
        note=f"{len(missing_in_csv)} Profile ohne CSV-Match",
    ))

    if missing_in_csv:
        results.append(CheckResult(
            name="html.orgs.profile_without_csv_row",
            tei=0,
            json=len(missing_in_csv),
            status="mismatch",
            note=", ".join(missing_in_csv[:5]),
        ))

    if name_mismatches:
        sample = "; ".join(
            f"{m['id']}: HTML='{m['html']}' vs CSV='{m['csv']}'"
            for m in name_mismatches[:3]
        )
        results.append(CheckResult(
            name="html.orgs.name_mismatch",
            tei=0,
            json=len(name_mismatches),
            status="mismatch",
            note=f"Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="html.orgs.name_mismatch",
            tei=0,
            json=0,
            status="match",
        ))

    if count_mismatches:
        sample = "; ".join(
            f"{m['id']}: header={m['header']} rows={m['rows']}"
            for m in count_mismatches[:3]
        )
        results.append(CheckResult(
            name="html.orgs.source_count_vs_rows",
            tei=0,
            json=len(count_mismatches),
            status="mismatch",
            note=f"Header-Count weicht von Tabellen-Zeilen ab. Beispiele: {sample}",
        ))
    else:
        results.append(CheckResult(
            name="html.orgs.source_count_vs_rows",
            tei=0,
            json=0,
            status="match",
        ))

    return results


def _load_relations_csv(name: str, key_col: str) -> Dict[str, int]:
    """Aggregiert ein relations-CSV nach key_col -> count. Wird genutzt
    fuer die Pruefung "Anzahl Eintraege im HTML stimmt mit der Anzahl
    in der CSV ueberein", z.B. wieviele occ_inverse-Eintraege Wilhelm
    haben sollte."""
    counts: Dict[str, int] = {}
    path = PIPELINE_ROOT / "pipeline" / "output" / name
    if not path.exists():
        return counts
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            key = (r.get(key_col) or "").strip()
            if key:
                counts[key] = counts.get(key, 0) + 1
    return counts


def _expected_death_display(death_iso: str) -> str:
    """Spiegelt aggregator/person_profiles.py::_format_death_german."""
    if not death_iso:
        return ""
    parts = death_iso.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        y, m, d = parts
        return f"{int(d):02d}.{int(m):02d}.{int(y):04d}"
    if len(parts) == 1 and parts[0].isdigit():
        return parts[0]
    return death_iso


def _expected_authority_urls(authority: str) -> List[str]:
    """Spiegelt aggregator/_profile_labels.py::split_authorities."""
    return [u.strip() for u in (authority or "").split("|") if u.strip()]


def check_person_extended_fields(
    sample_size: Optional[int] = None,
) -> List[CheckResult]:
    """Erweiterte Feld-Coverage: death_display, authority_urls, wiki_url.
    Pruefungen sind conditional (nur dort, wo CSV das Feld setzt)."""
    results: List[CheckResult] = []
    persons_csv = _load_persons_csv()
    if not persons_csv:
        return results

    paths = parse_html.iter_person_profiles()
    if sample_size:
        paths = paths[:sample_size]

    death_mismatches: List[Dict[str, Any]] = []
    auth_mismatches: List[Dict[str, Any]] = []
    wiki_mismatches: List[Dict[str, Any]] = []

    for path in paths:
        p = parse_html.read_person_profile(path)
        if p.read_failed:
            continue
        row = persons_csv.get(p.pe_id)
        if row is None:
            continue

        # death_display
        expected = _expected_death_display((row.get("dead_before") or "").strip())
        if expected and p.death_display != expected:
            death_mismatches.append({
                "id": p.pe_id, "html": p.death_display, "csv": expected,
            })

        # authority_urls
        expected_auth = _expected_authority_urls(row.get("authority") or "")
        if expected_auth and set(p.authority_urls) != set(expected_auth):
            auth_mismatches.append({
                "id": p.pe_id,
                "html_count": len(p.authority_urls),
                "csv_count": len(expected_auth),
            })

        # wiki_url
        page_id = (row.get("PAGEID_WienWiki") or "").strip()
        wiki_label = (row.get("Name_WienWiki") or "").strip()
        if page_id and wiki_label:
            if not p.wiki_url or page_id not in p.wiki_url:
                wiki_mismatches.append({
                    "id": p.pe_id,
                    "html": p.wiki_url or "(none)",
                    "expected_pageid": page_id,
                })

    def _add(name: str, ms: List[Dict[str, Any]]) -> None:
        if ms:
            sample = "; ".join(str(m) for m in ms[:3])
            results.append(CheckResult(
                name=name, tei=0, json=len(ms),
                status="mismatch", note=f"Beispiele: {sample}",
            ))
        else:
            results.append(CheckResult(
                name=name, tei=0, json=0, status="match",
            ))

    _add("html.persons.death_display_vs_csv", death_mismatches)
    _add("html.persons.authority_urls_vs_csv", auth_mismatches)
    _add("html.persons.wiki_url_vs_csv", wiki_mismatches)
    return results


def check_org_extended_fields(
    sample_size: Optional[int] = None,
) -> List[CheckResult]:
    """Erweiterte Org-Feld-Coverage: type_label, observance, place_name,
    parent_org_id."""
    results: List[CheckResult] = []
    orgs_csv = _load_orgs_csv()
    if not orgs_csv:
        return results

    paths = parse_html.iter_org_profiles()
    if sample_size:
        paths = paths[:sample_size]

    observance_mismatches: List[Dict[str, Any]] = []
    parent_mismatches: List[Dict[str, Any]] = []
    auth_mismatches: List[Dict[str, Any]] = []

    for path in paths:
        o = parse_html.read_org_profile(path)
        if o.read_failed:
            continue
        row = orgs_csv.get(o.org_id)
        if row is None:
            continue

        expected_observance = (row.get("observance") or "").strip()
        if expected_observance and o.observance != expected_observance:
            observance_mismatches.append({
                "id": o.org_id, "html": o.observance, "csv": expected_observance,
            })

        expected_parent = (row.get("org_key") or "").strip()
        if expected_parent and o.parent_org_id != expected_parent:
            # Wenn parent existiert aber nicht released ist, wird im HTML
            # ein Klartext gerendert (kein Link); o.parent_org_id ist dann
            # None. Das ist erwartet, nicht Bug. Nur als mismatch loggen,
            # wenn HTML einen anderen Link hat.
            if o.parent_org_id is not None:
                parent_mismatches.append({
                    "id": o.org_id,
                    "html": o.parent_org_id,
                    "csv": expected_parent,
                })

        expected_auth = _expected_authority_urls(row.get("authority") or "")
        if expected_auth and set(o.authority_urls) != set(expected_auth):
            auth_mismatches.append({
                "id": o.org_id,
                "html_count": len(o.authority_urls),
                "csv_count": len(expected_auth),
            })

    def _add(name: str, ms: List[Dict[str, Any]]) -> None:
        if ms:
            sample = "; ".join(str(m) for m in ms[:3])
            results.append(CheckResult(
                name=name, tei=0, json=len(ms),
                status="mismatch", note=f"Beispiele: {sample}",
            ))
        else:
            results.append(CheckResult(
                name=name, tei=0, json=0, status="match",
            ))

    _add("html.orgs.observance_vs_csv", observance_mismatches)
    _add("html.orgs.parent_org_vs_csv", parent_mismatches)
    _add("html.orgs.authority_urls_vs_csv", auth_mismatches)
    return results


def check_person_relation_counts(sample_size: Optional[int] = None) -> List[CheckResult]:
    """Vergleicht pro Person die Anzahl der Beziehungs-Tabellen-Zeilen
    im HTML mit der erwarteten Anzahl aus der jeweiligen
    relations-CSV.

    occ_inverse / title_ref_inverse sind die Mirror-Zaehler aus Commit
    24d5f4ad41: Person X ist related_key in occ-Relationen wo person_key
    eine andere Person ist."""
    results: List[CheckResult] = []

    # Counts der occ-relations gruppiert nach person_key (Vorwaertsrelation)
    occ_forward = _load_relations_csv(
        "occ_relations_in_sources.csv", "person_key"
    )
    # Mirror: occ_inverse zaehlt Eintraege, wo related_key == pe__X UND
    # person_key auch pe__... ist (Person->Person).
    occ_mirror: Dict[str, int] = {}
    path = PIPELINE_ROOT / "pipeline" / "output" / "occ_relations_in_sources.csv"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                pk = (r.get("person_key") or "").strip()
                rk = (r.get("related_key") or "").strip()
                if pk.startswith("pe__") and rk.startswith("pe__"):
                    occ_mirror[rk] = occ_mirror.get(rk, 0) + 1

    paths = parse_html.iter_person_profiles()
    if sample_size:
        paths = paths[:sample_size]

    occ_mismatches: List[Dict[str, Any]] = []
    occ_inverse_mismatches: List[Dict[str, Any]] = []

    for path in paths:
        p = parse_html.read_person_profile(path)
        if p.read_failed:
            continue
        html_occ = p.relation_counts.get("occ", 0)
        expected_occ = occ_forward.get(p.pe_id, 0)
        if html_occ != expected_occ:
            occ_mismatches.append({
                "id": p.pe_id, "html": html_occ, "csv": expected_occ,
            })

        html_inverse = p.relation_counts.get("occ_inverse", 0)
        expected_inverse = occ_mirror.get(p.pe_id, 0)
        if html_inverse != expected_inverse:
            occ_inverse_mismatches.append({
                "id": p.pe_id,
                "html": html_inverse,
                "csv": expected_inverse,
            })

    def _add_mismatch_result(name: str, ms: List[Dict[str, Any]]) -> None:
        if ms:
            sample = "; ".join(
                f"{m['id']}: HTML={m['html']} CSV={m['csv']}" for m in ms[:3]
            )
            results.append(CheckResult(
                name=name,
                tei=sum(m["csv"] for m in ms),
                json=sum(m["html"] for m in ms),
                status="mismatch",
                note=f"Beispiele: {sample}",
            ))
        else:
            results.append(CheckResult(
                name=name, tei=0, json=0, status="match",
            ))

    _add_mismatch_result("html.persons.occ_count_vs_csv", occ_mismatches)
    _add_mismatch_result("html.persons.occ_inverse_count_vs_csv", occ_inverse_mismatches)

    return results


def check_document_refs(sample_size: Optional[int] = None) -> List[CheckResult]:
    """Sicherstellt, dass jeder data-ref in einer Quellen-HTML-Datei auf
    eine real existierende Entitaet zeigt (Profil-HTML vorhanden) oder
    bekannt unrendered ist.

    Findet Renderer-Bugs wie 'Person X wird im Quellen-Body annotiert,
    hat aber kein Profil' (was bei einem korrekten reverse_index-Gate
    nicht passieren darf)."""
    results: List[CheckResult] = []
    paths = parse_html.iter_documents()
    if sample_size:
        paths = paths[:sample_size]

    persons_dir_ids = {p.stem for p in parse_html.iter_person_profiles()}
    orgs_dir_ids = {p.stem for p in parse_html.iter_org_profiles()}

    orphan_persons: Dict[str, int] = {}
    orphan_orgs: Dict[str, int] = {}
    docs_with_orphans: int = 0

    for path in paths:
        d = parse_html.read_document(path)
        if d.read_failed:
            continue
        local_orphan = False
        for ref in d.person_refs:
            if ref not in persons_dir_ids:
                orphan_persons[ref] = orphan_persons.get(ref, 0) + 1
                local_orphan = True
        for ref in d.org_refs:
            if ref not in orgs_dir_ids:
                orphan_orgs[ref] = orphan_orgs.get(ref, 0) + 1
                local_orphan = True
        if local_orphan:
            docs_with_orphans += 1

    results.append(CheckResult(
        name="html.documents.scanned",
        tei=len(paths),
        json=docs_with_orphans,
        status="info",
        note=f"{docs_with_orphans} Quellen mit mindestens einer Orphan-Annotation",
    ))

    if orphan_persons:
        sample = ", ".join(list(orphan_persons.keys())[:5])
        results.append(CheckResult(
            name="html.documents.orphan_person_refs",
            tei=0,
            json=sum(orphan_persons.values()),
            status="mismatch",
            note=(
                f"{len(orphan_persons)} eindeutige IDs ohne Profil-Datei. "
                f"Beispiele: {sample}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="html.documents.orphan_person_refs",
            tei=0, json=0, status="match",
        ))

    if orphan_orgs:
        sample = ", ".join(list(orphan_orgs.keys())[:5])
        results.append(CheckResult(
            name="html.documents.orphan_org_refs",
            tei=0,
            json=sum(orphan_orgs.values()),
            status="mismatch",
            note=(
                f"{len(orphan_orgs)} eindeutige IDs ohne Profil-Datei. "
                f"Beispiele: {sample}"
            ),
        ))
    else:
        results.append(CheckResult(
            name="html.documents.orphan_org_refs",
            tei=0, json=0, status="match",
        ))

    return results


def check_profile_source_consistency(
    sample_size: Optional[int] = None,
) -> List[CheckResult]:
    """Quervergleich: Wenn Profil A behauptet "ich erscheine in Quelle X",
    muss Quelle X auch `data-ref="A"` enthalten. Und umgekehrt: wenn Quelle X
    eine Person A annotiert, muss Profil A die Quelle X in seiner Tabelle
    listen.

    Findet zwei Klassen von Asymmetrien:
    - Profil-Eintrag ohne Annotation in der Quelle (reverse_index zeigt eine
      Quelle, die im Quellen-HTML keinen `data-ref` hat).
    - Annotation in der Quelle ohne Profil-Eintrag (Quelle annotiert eine
      Person, aber das Profil hat die Quelle nicht in der Tabelle).
    """
    results: List[CheckResult] = []

    # Profile-Sicht: pe_id -> Set(source file_keys)
    person_profile_sources: Dict[str, set] = {}
    person_paths = parse_html.iter_person_profiles()
    if sample_size:
        person_paths = person_paths[:sample_size]
    for path in person_paths:
        p = parse_html.read_person_profile(path)
        if p.read_failed:
            continue
        person_profile_sources[p.pe_id] = set(p.source_file_keys)

    org_profile_sources: Dict[str, set] = {}
    org_paths = parse_html.iter_org_profiles()
    if sample_size:
        org_paths = org_paths[:sample_size]
    for path in org_paths:
        o = parse_html.read_org_profile(path)
        if o.read_failed:
            continue
        org_profile_sources[o.org_id] = set(o.source_file_keys)

    # Quellen-Sicht: file_key -> Set(pe_id / org_id)
    doc_persons: Dict[str, set] = {}
    doc_orgs: Dict[str, set] = {}
    doc_paths = parse_html.iter_documents()
    if sample_size:
        doc_paths = doc_paths[:sample_size]
    for path in doc_paths:
        d = parse_html.read_document(path)
        if d.read_failed:
            continue
        # file_key analog zu parse_tei: <corpus>_<sub>_<stem>
        parts = path.parts
        try:
            idx = parts.index("documents")
            corpus = parts[idx + 1]
            sub = parts[idx + 2]
        except (ValueError, IndexError):
            continue
        file_key = f"{corpus}_{sub}_{path.stem}"
        # Person/Org "erscheint in der Quelle" = direkte Nennung (data-ref)
        # ODER indirekter Bezug (data-corresp ueber roleName). Das Profil
        # nimmt beide ueber das reverse_index auf, also muss der Cross-
        # Check das auch zusammenfassen.
        doc_persons[file_key] = set(d.person_refs) | set(d.person_corresps)
        doc_orgs[file_key] = set(d.org_refs) | set(d.org_corresps)

    # Asymmetrie 1: Profil zeigt Quelle, aber Quelle hat keinen data-ref auf Profil.
    person_profile_only: List[str] = []
    for pe_id, source_keys in person_profile_sources.items():
        for src_key in source_keys:
            if pe_id not in doc_persons.get(src_key, set()):
                person_profile_only.append(f"{pe_id} @ {src_key}")
                if len(person_profile_only) >= 50:
                    break
        if len(person_profile_only) >= 50:
            break

    # Asymmetrie 2: Quelle annotiert Person, aber Profil listet die Quelle nicht.
    doc_only_persons: List[str] = []
    for src_key, refs in doc_persons.items():
        for ref in refs:
            if ref not in person_profile_sources:
                continue  # in orphan-check abgedeckt
            if src_key not in person_profile_sources[ref]:
                doc_only_persons.append(f"{ref} @ {src_key}")
                if len(doc_only_persons) >= 50:
                    break
        if len(doc_only_persons) >= 50:
            break

    # Selbiges fuer Orgs.
    org_profile_only: List[str] = []
    for org_id, source_keys in org_profile_sources.items():
        for src_key in source_keys:
            if org_id not in doc_orgs.get(src_key, set()):
                org_profile_only.append(f"{org_id} @ {src_key}")
                if len(org_profile_only) >= 50:
                    break
        if len(org_profile_only) >= 50:
            break

    doc_only_orgs: List[str] = []
    for src_key, refs in doc_orgs.items():
        for ref in refs:
            if ref not in org_profile_sources:
                continue
            if src_key not in org_profile_sources[ref]:
                doc_only_orgs.append(f"{ref} @ {src_key}")
                if len(doc_only_orgs) >= 50:
                    break
        if len(doc_only_orgs) >= 50:
            break

    def _result(name: str, items: List[str], note_prefix: str) -> None:
        if items:
            results.append(CheckResult(
                name=name, tei=0, json=len(items),
                status="mismatch",
                note=f"{note_prefix}: {', '.join(items[:5])}"
                     + (f" (+{len(items) - 5} weitere, max 50 gesammelt)" if len(items) > 5 else ""),
            ))
        else:
            results.append(CheckResult(
                name=name, tei=0, json=0, status="match",
            ))

    _result(
        "html.cross.person_profile_source_missing_annotation",
        person_profile_only,
        "Profile listen Quellen, in denen kein data-ref auf die Person steht",
    )
    _result(
        "html.cross.person_doc_annotation_missing_in_profile",
        doc_only_persons,
        "Quellen annotieren Personen, deren Profil die Quelle nicht listet",
    )
    _result(
        "html.cross.org_profile_source_missing_annotation",
        org_profile_only,
        "Profile listen Quellen, in denen kein data-ref auf die Org steht",
    )
    _result(
        "html.cross.org_doc_annotation_missing_in_profile",
        doc_only_orgs,
        "Quellen annotieren Orgs, deren Profil die Quelle nicht listet",
    )
    return results


def run_html_checks() -> List[CheckResult]:
    """Alle HTML-Coverage-Pruefungen in einem Lauf."""
    results: List[CheckResult] = []
    results.extend(_check_reader_health())
    results.extend(check_person_profiles())
    results.extend(check_person_extended_fields())
    results.extend(check_org_profiles())
    results.extend(check_org_extended_fields())
    results.extend(check_person_relation_counts())
    results.extend(check_document_refs())
    results.extend(check_profile_source_consistency())
    return results
