"""Provenienz-Konsistenz-Checks über alle Aggregat- und Register-JSONs.

Ergänzt compare.py um eine orthogonale Prüfrichtung: statt TEI-Werte gegen
JSON-Werte zu legen, wird hier nur **innerhalb** der JSON-Ausgaben geprüft.

Für jede aggregierte Zahl soll das zugehörige Drill-Down existieren, und
jeder dort referenzierte `file_key` soll im `docs_lookup.json` auflösbar
sein. Fehlende oder unbekannte file_keys sind entweder ein Pipeline-Fehler
oder der bekannte Vienna_1448-57_ready-Gap (siehe known_gap-Logik in
compare.py). Eine Zahl ohne gültige Provenienz ist im Frontend nicht
zitierbar.

Für die drei Register-JSONs (`register/persons.json` etc.) werden die
Dokumenten-URLs gegen das `docs_lookup.json` geprüft, analog.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List, Set, Tuple

from verification.compare import CheckResult
from verification.config import DATA_DIR, EDITION_ROOT, PIPELINE_ROOT


def _load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _known_file_keys() -> Set[str]:
    """Alle gültigen file_keys aus docs_lookup.json."""
    lookup = _load(DATA_DIR / "docs_lookup.json")
    return set(lookup.keys())


def _no_tei_file_keys() -> Set[str]:
    """file_keys aus filenames.csv, für die keine TEI-Datei existiert.

    Aktuell ist das der Bestand Vienna_1448-57_ready (530 Dokumente).
    Solange diese Dokumente im Build per CSV geführt werden, ohne dass
    TEI in `sources/` liegt, landen ihre file_keys in Drill-Downs, aber
    nicht in `docs_lookup.json`. Das ist **kein** Pipeline-Fehler im
    engeren Sinn, sondern derselbe bekannte Gap wie `docs.total`.
    """
    fk_csv = PIPELINE_ROOT / "pipeline" / "output" / "filenames.csv"
    if not fk_csv.exists():
        return set()
    tei_dir = PIPELINE_ROOT / "sources"
    no_tei: Set[str] = set()
    with fk_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            fid = row.get("id", "")
            if not fid:
                continue
            collection = row.get("collection", "")
            sub = row.get("subcollection", "")
            filename = row.get("file", "")
            if not (collection and filename):
                continue
            candidates = [
                tei_dir / collection / sub / "done" / filename,
                tei_dir / collection / sub / filename,
            ]
            if not any(p.exists() for p in candidates):
                no_tei.add(fid)
    return no_tei


def _known_doc_urls() -> Set[str]:
    """Alle bekannten Dokument-URLs aus docs_lookup.json.

    Register-JSONs referenzieren Dokumente per URL (Feld `u`), nicht per
    file_key. Diese URLs stehen im docs_lookup-Wert-Objekt unter `u`.
    """
    lookup = _load(DATA_DIR / "docs_lookup.json")
    return {v["u"] for v in lookup.values() if isinstance(v, dict) and "u" in v}


def _iter_file_keys_from_dict(node, path: str) -> Iterable[tuple[str, str]]:
    """Alle file_keys aus geschachteltem Drill-Down-Dict extrahieren.

    Liefert Tupel (pfad, file_key). Unterstützt beide Formen:
    - dict → recurse
    - list/str → als file_key betrachten, wenn Präfix f__ oder Aussehen passt
    """
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _iter_file_keys_from_dict(v, f"{path}.{k}")
    elif isinstance(node, list):
        for fk in node:
            if isinstance(fk, str):
                yield path, fk


def _check_file_keys(
    name: str,
    fkeys: Iterable[Tuple[str, str]],
    known: Set[str],
    no_tei: Set[str],
) -> List[CheckResult]:
    """Erzeuge CheckResults, die unbekannte file_keys in zwei Kategorien trennen.

    - `known_gap`: file_keys sind in `filenames.csv` vorgesehen, aber ohne TEI
      (Vienna_1448-57_ready). Dieselbe Wurzel wie `docs.total`.
    - `mismatch`: file_keys, die weder in `docs_lookup.json` noch im
      bekannten Gap liegen. Echter Pipeline-Inkonsistenz-Hinweis.

    Liefert ein bis zwei Ergebnisse, ohne zusätzlichen Rauschen bei 0.
    """
    unknown: List[str] = []
    total = 0
    for _path, fk in fkeys:
        total += 1
        if fk not in known:
            unknown.append(fk)
    if not unknown:
        return [
            CheckResult(
                name=name,
                tei=f"{total} file_keys geprüft",
                json="alle in docs_lookup",
                status="match",
                note=None,
            )
        ]

    gap_hits = [fk for fk in unknown if fk in no_tei]
    real_misses = [fk for fk in unknown if fk not in no_tei]

    results: List[CheckResult] = []
    if gap_hits:
        results.append(CheckResult(
            name=f"{name}.known_gap",
            tei=f"{total} file_keys geprüft",
            json=f"{len(gap_hits)} Einträge aus Vienna_1448-57_ready",
            status="known_gap",
            note=(
                "file_keys aus filenames.csv ohne TEI-Quelle. Dieselbe Wurzel "
                "wie docs.total: Pipeline zählt zusätzlich Dokumente ohne TEI."
            ),
        ))
    if real_misses:
        results.append(CheckResult(
            name=name,
            tei=f"{total} file_keys geprüft",
            json=f"{len(real_misses)} unbekannt, Beispiele: {sorted(set(real_misses))[:5]}",
            status="mismatch",
            note=(
                "file_key in Drill-Down, aber weder in docs_lookup.json noch im "
                "bekannten Vienna_1448-57_ready-Gap. Pipeline-Inkonsistenz."
            ),
        ))
    if not gap_hits and not real_misses:
        results.append(CheckResult(
            name=name,
            tei=f"{total} file_keys geprüft",
            json="alle in docs_lookup",
            status="match",
            note=None,
        ))
    return results


def run_provenance_checks() -> List[CheckResult]:
    """Konsistenz-Checks über alle JSONs mit Provenienz-Informationen."""
    results: List[CheckResult] = []
    known_fks = _known_file_keys()
    no_tei_fks = _no_tei_file_keys()
    known_urls = _known_doc_urls()

    # --- roles.drill_down.role_sex ---------------------------------------
    roles = _load(DATA_DIR / "roles.json")
    fkeys_a = list(_iter_file_keys_from_dict(
        roles.get("drill_down", {}).get("role_sex", {}), "role_sex"
    ))
    results.extend(_check_file_keys("provenance.roles.role_sex", fkeys_a, known_fks, no_tei_fks))

    # --- relations.drill_down -------------------------------------------------
    relations = _load(DATA_DIR / "relations.json")
    fkeys_b = list(_iter_file_keys_from_dict(
        relations.get("drill_down", {}), "drill_down"
    ))
    results.extend(_check_file_keys("provenance.relations.drill_down", fkeys_b, known_fks, no_tei_fks))

    # relations.persons: list of entities with rels[].f -> file_key
    persons_b = relations.get("persons", [])
    person_rel_fks: List[Tuple[str, str]] = []
    for entry in persons_b:
        for rel in entry.get("rels", []):
            fk = rel.get("f")
            if fk:
                person_rel_fks.append(("persons.rels", fk))
    results.extend(
        _check_file_keys("provenance.relations.persons.rels", person_rel_fks, known_fks, no_tei_fks)
    )

    # --- transactions.drill_down.tx_type_decade ---------------------------------
    transactions = _load(DATA_DIR / "transactions.json")
    fkeys_c = list(_iter_file_keys_from_dict(
        transactions.get("drill_down", {}), "drill_down"
    ))
    results.extend(_check_file_keys("provenance.transactions.drill_down", fkeys_c, known_fks, no_tei_fks))

    # --- epic_d.places[*].file_keys ---------------------------------------
    # epic_d.json wird nicht mehr gebaut (Orte-Exploration entfernt). Falls
    # die Datei aus einem alten Build noch da liegt, pruefen wir; sonst
    # ueberspringen.
    epic_d_path = DATA_DIR / "epic_d.json"
    if epic_d_path.exists():
        epic_d = _load(epic_d_path)
        fkeys_d: List[Tuple[str, str]] = []
        referenced_without_fks = 0
        for p in epic_d.get("places", []):
            if not p.get("referenced"):
                continue
            fks = p.get("file_keys")
            if not fks:
                referenced_without_fks += 1
                continue
            for fk in fks:
                fkeys_d.append((f"places.{p.get('id')}", fk))
        results.extend(_check_file_keys("provenance.epic_d.places", fkeys_d, known_fks, no_tei_fks))

        if referenced_without_fks:
            results.append(CheckResult(
                name="provenance.epic_d.coverage",
                tei=None,
                json=f"{referenced_without_fks} referenced places ohne file_keys",
                status="mismatch",
                note="Referenzierte Orte ohne Provenienz-Verweis.",
            ))
        else:
            results.append(CheckResult(
                name="provenance.epic_d.coverage",
                tei="alle referenced Places",
                json="haben file_keys",
                status="match",
                note=None,
            ))

    # --- register/persons|organisations|places.json ------------------------
    register_dir = EDITION_ROOT / "docs" / "register"
    for kind in ("persons", "organisations", "places"):
        path = register_dir / f"{kind}.json"
        if not path.exists():
            continue
        data = _load(path)
        urls: List[tuple[str, str]] = []
        for _entity_id, docs in data.items():
            if not isinstance(docs, list):
                continue
            for doc in docs:
                u = doc.get("u") if isinstance(doc, dict) else None
                if u:
                    urls.append((kind, u))
        unknown = [u for _p, u in urls if u not in known_urls]
        if unknown:
            results.append(CheckResult(
                name=f"provenance.register.{kind}",
                tei=f"{len(urls)} Doc-URLs gepr\u00fcft",
                json=f"{len(unknown)} unbekannt, Beispiele: {sorted(set(unknown))[:3]}",
                status="mismatch",
                note="Register verweist auf Dokument-URL, die nicht in docs_lookup.json auflösbar ist.",
            ))
        else:
            results.append(CheckResult(
                name=f"provenance.register.{kind}",
                tei=f"{len(urls)} Doc-URLs gepr\u00fcft",
                json="alle in docs_lookup",
                status="match",
                note=None,
            ))

    return results
