"""Qualitaets-Findings: Index-Lade-Helfer und docs/data/quality.json.

Liest validation_report.json aus dem Pipeline-Output, filtert Findings aus
nicht-freigegebenen Korpora aus und schreibt die korpusweiten Aggregate
nach docs/data/quality.json.
"""

import json
import sys
from collections import Counter
from datetime import date

from frontend.config import (
    DATA_DIR, VALIDATION_REPORT_PATH, is_released_corpus,
)


def _load_quality_index():
    """Load validation_report.json and index findings by source-relative file path.

    Returns a dict mapping normalised file paths (forward slashes, relative to
    sources/) to a list of finding dicts. If the report file does not exist,
    returns an empty dict so the build can proceed without quality data.

    Filtert Findings nicht-freigegebener Quellenkorpora aus: Pfade unter
    sources/{collection}/{subcollection}/... werden gegen RELEASED_CORPORA
    geprueft. Findings ueber Index-Dateien (indices/*.xml) und sonstige
    Pfade ohne Korpus-Praefix bleiben enthalten.
    """
    if not VALIDATION_REPORT_PATH.exists():
        print("  WARN: validation_report.json not found, quality data disabled.",
              file=sys.stderr)
        return {}

    report = json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))
    index = {}
    skipped = 0
    for finding in report.get("findings", []):
        key = finding["file"].replace("\\", "/")
        parts = key.split("/")
        if len(parts) >= 2 and parts[0] not in ("indices",):
            corpus_path = f"{parts[0]}/{parts[1]}"
            if not is_released_corpus(corpus_path):
                skipped += 1
                continue
        index.setdefault(key, []).append({
            "severity": finding["severity"],
            "category": finding["category"],
            "detail": finding["detail"],
        })
    total_kept = sum(len(v) for v in index.values())
    msg = f"  Quality index: {len(index)} files with findings ({total_kept} kept"
    if skipped:
        msg += f", {skipped} aus nicht-freigegebenen Korpora ausgefiltert"
    msg += ")"
    print(msg)
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

    by_category = Counter()
    by_severity = Counter()
    by_collection = {}
    for filepath, findings in quality_index.items():
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
