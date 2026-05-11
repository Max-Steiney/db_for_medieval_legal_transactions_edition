"""Project status dashboard — compact console output for development context.

Usage: python -m frontend status [--json] [--test]
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from pipeline.config import REPO_ROOT

DOCS_DIR = REPO_ROOT / "docs"
DATA_DIR = DOCS_DIR / "data"

# Frontend milestones — hardcoded after Phase I substantially completed.
# Update by hand when a milestone moves between completed and pending.
# Each entry: id, label, done (1=complete, 0=pending), blocked (count of blockers).
_MILESTONES = [
    ("M3", "Scholarly functions",         1, 0),
    ("V0", "Data aggregation",            1, 0),
    ("V1", "Shared UI components",        1, 0),
    ("V2", "Epic A: Role Explorer",       1, 0),  # partial — A.3 deferred
    ("V3", "Epic C: Transaction Explorer", 1, 0), # T5 deferred (Q2)
    ("V4", "Epic B: Network Explorer",    1, 0),
    ("V5", "Epic D: Place Explorer",      1, 0),
    ("M5", "Performance + accessibility", 1, 0),
    ("M6", "E2E tests + documentation",   0, 0),
]

MILESTONE_IDS = [m[0] for m in _MILESTONES]
MILESTONE_LABELS = {m[0]: m[1] for m in _MILESTONES}
_MILESTONE_STATUS = {m[0]: {"done": m[2], "total": 1, "blocked": m[3]} for m in _MILESTONES}

OPEN_QUESTIONS = [
    ("Q1", "@cert interpretation", "V4-T1"),
    ("Q2", "Kirche/Kapelle grouping", "V3-T5"),
    ("Q3", "geistlich/weltlich mapping", "V2-T5/T6/T7"),
    ("Q4", "Place annotation scope", "V5"),
    ("Q5", "Verb normalisation (15%)", "V3"),
]


def _parse_milestones() -> dict:
    """Return the hardcoded milestone status table."""
    return dict(_MILESTONE_STATUS)


def _data_files() -> list:
    """List JSON files in docs/data/ with sizes."""
    if not DATA_DIR.exists():
        return []

    files = []
    for p in sorted(DATA_DIR.glob("*.json")):
        size = p.stat().st_size
        files.append({"name": p.name, "bytes": size})
    return files


def _format_size(b: int) -> str:
    """Format byte count as human-readable string."""
    if b < 1024:
        return f"{b}B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f}K"
    else:
        return f"{b / (1024 * 1024):.1f}M"


def _html_pages() -> list:
    """Check which top-level HTML pages exist (post-URL-refactor paths)."""
    expected = [
        "index.html",
        "documents.html",
        "impressum.html",
        "register/persons.html",
        "register/organisations.html",
        "register/places.html",
        "analysis/auswertungen.html",
        "exploration/zeitstrom.html",
        "exploration/personennetzwerk.html",
        "korb.html",
        "project/edition-guidelines.html",
        "project/about.html",
        "project/glossary.html",
    ]
    result = []
    for name in expected:
        path = DOCS_DIR / name
        result.append({"name": name, "exists": path.exists()})
    return result


def _git_log(n: int = 5) -> list:
    """Get last N git commits."""
    try:
        out = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            timeout=5,
        )
        if out.returncode == 0:
            return [line.strip() for line in out.stdout.strip().splitlines() if line.strip()]
    except Exception:
        pass
    return []


def _run_tests() -> dict | None:
    """Run pytest and return summary."""
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "frontend/tests/", "-q", "--tb=no"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            timeout=120,
        )
        for line in reversed(out.stdout.splitlines()):
            m = re.search(r'(\d+) passed', line)
            f = re.search(r'(\d+) failed', line)
            if m:
                return {
                    "passed": int(m.group(1)),
                    "failed": int(f.group(1)) if f else 0,
                    "returncode": out.returncode,
                }
    except Exception:
        pass
    return None


def collect_status(run_tests: bool = False) -> dict:
    """Collect all status data into a dict."""
    milestones = _parse_milestones()

    ms_list = []
    for ms_id in MILESTONE_IDS:
        ms = milestones.get(ms_id, {"done": 0, "total": 0, "blocked": 0})

        if ms["total"] > 0 and ms["done"] == ms["total"]:
            symbol = "done"
        elif ms["done"] > 0:
            symbol = "wip"
        else:
            symbol = "pending"

        ms_list.append({
            "id": ms_id,
            "label": MILESTONE_LABELS.get(ms_id, ms_id),
            "done": ms["done"],
            "total": ms["total"],
            "blocked": ms["blocked"],
            "status": symbol,
        })

    tests = _run_tests() if run_tests else None

    return {
        "date": date.today().isoformat(),
        "milestones": ms_list,
        "data_files": _data_files(),
        "html_pages": _html_pages(),
        "open_questions": [
            {"id": q[0], "topic": q[1], "blocks": q[2]}
            for q in OPEN_QUESTIONS
        ],
        "git_log": _git_log(),
        "tests": tests,
    }


def _out(text: str = "") -> None:
    """Print with UTF-8 fallback for Windows consoles."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def print_status(status: dict) -> None:
    """Print formatted status dashboard to console."""
    bar = "=" * 60
    thin = "-" * 60

    _out(f"\nPROJECT STATUS -- {status['date']}")
    _out(bar)

    pages = status["html_pages"]
    existing = [p["name"].replace(".html", "") for p in pages if p["exists"]]
    missing = [p["name"].replace(".html", "") for p in pages if not p["exists"]]
    _out(f"  Pages:  {len(existing)} built" +
         (f"  ({', '.join(missing)} missing)" if missing else ""))

    df = status["data_files"]
    if df:
        parts = []
        for d in df:
            name = d["name"].replace(".json", "")
            parts.append(f"{name} {_format_size(d['bytes'])}")
        _out(f"  Data:   {' | '.join(parts)}")
    else:
        _out("  Data:   (no JSON files in docs/data/)")

    if status.get("tests"):
        t = status["tests"]
        symbol = "OK" if t["failed"] == 0 else "FAIL"
        _out(f"  Tests:  {symbol} {t['passed']} passed, {t['failed']} failed")
    else:
        _out("  Tests:  (run with --test)")

    _out(f"\nMILESTONES")
    _out(thin)

    symbols = {"done": "+", "wip": "~", "pending": "."}

    # Two-column layout
    ms = status["milestones"]
    half = (len(ms) + 1) // 2
    col1 = ms[:half]
    col2 = ms[half:]

    for i in range(max(len(col1), len(col2))):
        parts = []
        for col in [col1, col2]:
            if i < len(col):
                m = col[i]
                sym = symbols[m["status"]]
                progress = ""
                if m["total"] > 0:
                    progress = f" [{m['done']}/{m['total']}"
                    if m["blocked"] > 0:
                        progress += f", {m['blocked']}blk"
                    progress += "]"
                entry = f"  {sym} {m['id']:<3} {m['label']:<24}{progress}"
                parts.append(f"{entry:<42}")
            else:
                parts.append(" " * 42)
        _out("".join(parts))

    blocking = [q for q in status["open_questions"]]
    if blocking:
        _out(f"\nBLOCKED BY OPEN QUESTIONS")
        _out(thin)
        for q in blocking:
            _out(f"  {q['id']} -> {q['blocks']:<14} {q['topic']}")

    commits = status.get("git_log", [])
    if commits:
        _out(f"\nLAST {len(commits)} COMMITS")
        _out(thin)
        for c in commits:
            if len(c) > 72:
                c = c[:69] + "..."
            _out(f"  {c}")

    _out()


def run(args: list[str] | None = None) -> None:
    """Entry point for the status command."""
    args = args or []
    as_json = "--json" in args
    run_tests = "--test" in args

    status = collect_status(run_tests=run_tests)

    if as_json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_status(status)
