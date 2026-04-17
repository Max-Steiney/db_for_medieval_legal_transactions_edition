"""Report-Generator: Markdown und JSON aus Vergleichsergebnissen."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable, List

from tests.compare import CheckResult
from tests.config import REPORTS_DIR


def _format_value(value) -> str:
    """Kompakte Darstellung für Markdown-Tabellen."""
    if value is None:
        return "—"
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = ", ".join(f"{k}={v}" for k, v in list(value.items())[:6])
        if len(value) > 6:
            items += f", … ({len(value)} total)"
        return f"{{{items}}}"
    if isinstance(value, (list, tuple)):
        if not value:
            return "[]"
        return f"[{', '.join(str(v) for v in value[:6])}{'…' if len(value) > 6 else ''}]"
    return str(value)


def _status_emoji(status: str) -> str:
    return {"match": "OK", "mismatch": "FAIL", "info": "INFO"}.get(status, status)


def write_markdown(results: List[CheckResult], dest: Path) -> None:
    match = sum(1 for r in results if r.status == "match")
    mismatch = sum(1 for r in results if r.status == "mismatch")
    info = sum(1 for r in results if r.status == "info")

    lines: List[str] = []
    lines.append(f"# Verifikations-Report {date.today().isoformat()}")
    lines.append("")
    lines.append("## Zusammenfassung")
    lines.append("")
    lines.append(f"- Checks gesamt: {len(results)}")
    lines.append(f"- Match: {match}")
    lines.append(f"- Mismatch: {mismatch}")
    lines.append(f"- Info / Nicht direkt vergleichbar: {info}")
    lines.append("")

    if mismatch:
        lines.append("## Mismatches")
        lines.append("")
        for r in results:
            if r.status != "mismatch":
                continue
            lines.append(f"### {r.name}")
            lines.append("")
            lines.append(f"- TEI: `{_format_value(r.tei)}`")
            lines.append(f"- JSON: `{_format_value(r.json)}`")
            if r.note:
                lines.append(f"- Notiz: {r.note}")
            lines.append("")

    lines.append("## Matches")
    lines.append("")
    lines.append("| Status | Name | Wert |")
    lines.append("|---|---|---|")
    for r in results:
        if r.status != "match":
            continue
        lines.append(f"| {_status_emoji(r.status)} | {r.name} | `{_format_value(r.tei)}` |")
    lines.append("")

    if info:
        lines.append("## Info / Kontext-Aggregate ohne direkten Vergleich")
        lines.append("")
        for r in results:
            if r.status != "info":
                continue
            lines.append(f"### {r.name}")
            lines.append("")
            lines.append(f"- TEI: `{_format_value(r.tei)}`")
            lines.append(f"- JSON: `{_format_value(r.json)}`")
            if r.note:
                lines.append(f"- Notiz: {r.note}")
            lines.append("")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines), encoding="utf-8")


def write_json(results: List[CheckResult], dest: Path) -> None:
    payload = {
        "date": date.today().isoformat(),
        "summary": {
            "total": len(results),
            "match": sum(1 for r in results if r.status == "match"),
            "mismatch": sum(1 for r in results if r.status == "mismatch"),
            "info": sum(1 for r in results if r.status == "info"),
        },
        "results": [r.to_dict() for r in results],
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def today_paths() -> tuple[Path, Path]:
    stamp = date.today().isoformat()
    return REPORTS_DIR / f"{stamp}.md", REPORTS_DIR / f"{stamp}.json"
