"""Einstiegspunkt für das Test-Set.

Usage: `python -m tests.run` aus dem Edition-Repo-Root. Liefert
Exit-Code 0 wenn alle Checks den Status 'match' haben, sonst 1.
"""

from __future__ import annotations

import sys
import time

from tests import compare, parse_indices, parse_tei, report


def main() -> int:
    print("[tests] TEI-Quellen einlesen ...")
    t0 = time.time()
    docs = parse_tei.scan_sources()
    print(f"[tests]   {len(docs)} Dokumente in {time.time() - t0:.1f}s")

    print("[tests] Register einlesen ...")
    t0 = time.time()
    persons = parse_indices.load_persons()
    orgs = parse_indices.load_orgs()
    places = parse_indices.load_places()
    print(
        f"[tests]   {len(persons)} Personen, {len(orgs)} Organisationen, "
        f"{len(places)} Orte in {time.time() - t0:.1f}s"
    )

    print("[tests] Vergleichen ...")
    results = compare.run_checks(docs, persons, orgs, places)

    match = sum(1 for r in results if r.status == "match")
    mismatch = sum(1 for r in results if r.status == "mismatch")
    info = sum(1 for r in results if r.status == "info")

    md_path, json_path = report.today_paths()
    report.write_markdown(results, md_path)
    report.write_json(results, json_path)
    print(f"[tests] Report: {md_path}")
    print(f"[tests]         {json_path}")
    print(f"[tests] {match} match, {mismatch} mismatch, {info} info")

    return 0 if mismatch == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
