"""Einstiegspunkt für das Verifikations-Set.

Usage:
  python -m verification.run               -- TEI -> JSON-Aggregat-Vergleich
  python -m verification.run --html        -- Pipeline-CSV -> gerendertes HTML
  python -m verification.run --tei-html    -- TEI direkt -> gerendertes HTML
  python -m verification.run --all         -- alle drei Pfade

Liefert Exit-Code 0 bei Match, bekannten Lücken oder Info-Status; Exit-
Code 1 nur bei echten Mismatches.
"""

from __future__ import annotations

import argparse
import sys
import time

from verification import (
    compare,
    compare_html,
    compare_tei_html,
    parse_indices,
    parse_tei,
    provenance,
    report,
)


def run_tei_checks():
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

    print("[verify] TEI -> JSON pruefen ...")
    results = compare.run_checks(docs, persons, orgs, places)

    print("[verify] Provenienz-Konsistenz pruefen ...")
    results.extend(provenance.run_provenance_checks())
    return results


def run_html_checks():
    print("[verify] CSV -> HTML pruefen ...")
    t0 = time.time()
    results = compare_html.run_html_checks()
    print(f"[verify]   {len(results)} Pruefungen in {time.time() - t0:.1f}s")
    return results


def run_tei_html_checks():
    print("[verify] TEI direkt -> HTML pruefen ...")
    t0 = time.time()
    results = compare_tei_html.run_tei_html_checks()
    print(f"[verify]   {len(results)} Pruefungen in {time.time() - t0:.1f}s")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(prog="verification.run")
    parser.add_argument("--html", action="store_true",
                        help="nur die HTML-Coverage (Pipeline-CSV -> Profil-HTML) pruefen")
    parser.add_argument("--tei-html", action="store_true",
                        help="nur die TEI-direkt-zu-HTML-Coverage pruefen")
    parser.add_argument("--all", action="store_true",
                        help="alle drei Pfade pruefen: TEI->JSON, CSV->HTML, TEI->HTML")
    args = parser.parse_args()

    results = []
    if args.all:
        results = run_tei_checks()
        results.extend(run_html_checks())
        results.extend(run_tei_html_checks())
        suffix = "all"
    elif args.html:
        results = run_html_checks()
        suffix = "html"
    elif args.tei_html:
        results = run_tei_html_checks()
        suffix = "tei-html"
    else:
        results = run_tei_checks()
        suffix = None

    match = sum(1 for r in results if r.status == "match")
    mismatch = sum(1 for r in results if r.status == "mismatch")
    known_gap = sum(1 for r in results if r.status == "known_gap")
    info = sum(1 for r in results if r.status == "info")

    md_path, json_path = report.today_paths(suffix=suffix)
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
