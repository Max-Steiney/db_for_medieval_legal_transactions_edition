"""Wiki-Link-Validator fuer die Knowledge-Base.

Prueft alle Obsidian-Wiki-Links der Form ``[[target#anchor|alias]]`` in
``knowledge/*.md`` und ``frontend/content/project/*.md``:

* ``target`` muss als Markdown-Datei in einem der beiden Ordner existieren
  (Glossar liegt unter ``frontend/content/project/glossar.md``).
* Wenn ein ``#anchor`` mitgegeben ist, muss er als Heading in der Zieldatei
  vorkommen. Heading-Vergleich ist case-sensitiv und wortgenau, weil
  Obsidian und unsere Templates so verlinken.

Topic-Tag-Links wie ``[[Information Visualisation]]`` werden uebersprungen,
weil sie reine Obsidian-Topic-Cluster sind und keine konkreten Files
adressieren. Heuristik: Topic-Tags sind nicht im Kebab-Case-Schema, das
unsere Knowledge-Files tragen.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
PROJECT_CONTENT_DIR = REPO_ROOT / "frontend" / "content" / "project"

# Matches [[target]], [[target#anchor]], [[target|alias]], [[target#anchor|alias]].
WIKI_LINK_RE = re.compile(r"\[\[([^|\]]+?)(?:#([^|\]]+?))?(?:\|[^\]]+?)?\]\]")

# Knowledge-Dateinamen sind in Kebab-Case. Topic-Tags wie
# [[Information Visualisation]] tragen Leerzeichen oder Camelcase und
# werden hier herausgefiltert.
KEBAB_TARGET_RE = re.compile(r"^[a-z][a-z0-9_-]*$")

# Markdown-Heading (ATX): ein bis sechs # plus Text bis Zeilenende.
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def _collect_source_files() -> list[Path]:
    files: list[Path] = []
    if KNOWLEDGE_DIR.exists():
        files.extend(sorted(KNOWLEDGE_DIR.glob("*.md")))
    if PROJECT_CONTENT_DIR.exists():
        files.extend(sorted(PROJECT_CONTENT_DIR.glob("*.md")))
    return files


def _resolve_target(target: str) -> Path | None:
    """Resolve a Wiki-Link target to an existing Markdown file.

    Sucht erst in knowledge/, dann in frontend/content/project/. Gibt None
    zurueck, wenn keine Datei matcht (= toter Link).
    """
    candidates = [
        KNOWLEDGE_DIR / f"{target}.md",
        PROJECT_CONTENT_DIR / f"{target}.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _file_headings(path: Path) -> set[str]:
    """Sammle alle Heading-Texte aus einer Markdown-Datei."""
    headings: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEADING_RE.match(line)
        if m:
            headings.add(m.group(1).strip())
    return headings


def _extract_links(path: Path) -> list[tuple[int, str, str | None]]:
    """Liefere (Zeilennummer, target, anchor-or-None) fuer jeden Wiki-Link."""
    out: list[tuple[int, str, str | None]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in WIKI_LINK_RE.finditer(line):
            target = m.group(1).strip()
            anchor = m.group(2).strip() if m.group(2) else None
            out.append((lineno, target, anchor))
    return out


@pytest.mark.parametrize("source_file", _collect_source_files(),
                         ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_knowledge_wiki_links_resolve(source_file: Path) -> None:
    """Pro Knowledge-Datei: alle Wiki-Links zeigen auf existierende Ziele."""
    broken: list[str] = []
    for lineno, target, anchor in _extract_links(source_file):
        if not KEBAB_TARGET_RE.match(target):
            # Topic-Tag wie [[Information Visualisation]], kein File-Link.
            continue
        resolved = _resolve_target(target)
        if resolved is None:
            broken.append(f"L{lineno}: [[{target}{('#' + anchor) if anchor else ''}]] -> target file not found")
            continue
        if anchor is not None:
            headings = _file_headings(resolved)
            if anchor not in headings:
                broken.append(
                    f"L{lineno}: [[{target}#{anchor}]] -> heading not found in {resolved.name}"
                )
    assert not broken, (
        f"\nKaputte Wiki-Links in {source_file.relative_to(REPO_ROOT)}:\n  "
        + "\n  ".join(broken)
    )
