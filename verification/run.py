"""Einstiegspunkt für das Verifikations-Set.

Usage: `python -m verification.run` aus dem Edition-Repo-Root. Liefert
Exit-Code 0 bei Match, bekannten Lücken oder Info-Status; Exit-Code 1
nur bei echten Mismatches.
"""

from __future__ import annotations

import sys
import time

from verification import compare, parse_indices, parse_tei, report


def main() -> int:
    print("[verify] TEI-Quellen einlesen ...")
    t0 = time.time()
    docs = parse_tei.scan_sources()
    print(f"[verify]   {len(docs)} Dokumente in {time.time() - t0:.1f}s")

    print("[verify] Register einlesen ...")
    t0 = time.time()
    persons = parse_indices.load_persons()
    orgs = parse_indices.load_orgs()
    places = parse_indices.load_places()
    print(
        f"[verify]   {len(persons)} Personen, {len(orgs)} Organisationen, "
        f"{len(places)} Orte in {time.time() - t0:.1f}s"
    )

    print("[verify] Vergleichen ...")
    results = compare.run_checks(docs, persons, orgs, places)

    match = sum(1 for r in results if r.status == "match")
    mismatch = sum(1 for r in results if r.status == "mismatch")
    known_gap = sum(1 for r in results if r.status == "known_gap")
    info = sum(1 for r in results if r.status == "info")

    md_path, json_path = report.today_paths()
    report.write_markdown(results, md_path)
    report.write_json(results, json_path)
    print(f"[verify] Report: {md_path}")
    print(f"[verify]         {json_path}")
    print(
        f"[verify] {match} match, {mismatch} mismatch, "
        f"{known_gap} known_gap, {info} info"
    )

    return 0 if mismatch == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
