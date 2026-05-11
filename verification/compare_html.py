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
        if p.source_count_displayed is None:
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


def run_html_checks() -> List[CheckResult]:
    """Alle HTML-Coverage-Pruefungen in einem Lauf."""
    results: List[CheckResult] = []
    results.extend(check_person_profiles())
    results.extend(check_org_profiles())
    results.extend(check_person_relation_counts())
    results.extend(check_document_refs())
    return results
