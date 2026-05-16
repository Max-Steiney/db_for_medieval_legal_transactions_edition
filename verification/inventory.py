"""TEI-Inventar pro Subkorpus.

Scannt das `sources/`-Verzeichnis des Pipeline-Repos (oder eines beliebigen
alternativen Repos via VERIFY_SOURCES_DIR) und zaehlt pro Subkorpus jedes
verwendete Element mit allen vorkommenden Attributen und distinct
Attribut-Werten. Der Report dient als Coverage-Grundlage: was hier
inventarisiert ist, sollte spaeter auch im Frontend ankommen.

Aufruf:
    python -m verification.run --inventory

Mit alternativem Repo:
    VERIFY_SOURCES_DIR=/c/Users/Chrisi/.../sources python -m verification.run --inventory

Output:
    verification/reports/inventory-YYYY-MM-DD.json
    verification/reports/inventory-YYYY-MM-DD.md
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lxml import etree

from verification.config import REPORTS_DIR, TEI_NS, TEI_SOURCES_DIR


_ATTR_VALUE_CAP = 50
_ATTR_VALUE_DISPLAY = 12


def _sources_dir() -> Path:
    """Active sources directory. Honours VERIFY_SOURCES_DIR for ad-hoc
    runs against an alternative repo clone."""
    override = os.environ.get("VERIFY_SOURCES_DIR", "").strip()
    if override:
        return Path(override).resolve()
    return TEI_SOURCES_DIR


def _strip_ns(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _iter_subcorpora(sources_dir: Path):
    """Yield (collection, subcollection, done_dir) for every Subdir that
    holds an XML-bearing `done/` (or its own .xml files)."""
    if not sources_dir.exists():
        return
    for collection in sorted(sources_dir.iterdir()):
        if not collection.is_dir() or collection.name in {"schema"}:
            continue
        for sub in sorted(collection.iterdir()):
            if not sub.is_dir():
                continue
            done = sub / "done"
            if done.exists() and any(done.rglob("*.xml")):
                yield collection.name, sub.name, done
            elif any(sub.rglob("*.xml")):
                yield collection.name, sub.name, sub


def _scan_corpus(done_dir: Path) -> dict:
    """Walk all .xml files under done_dir and build the inventory."""
    files = sorted(done_dir.rglob("*.xml"))
    n_files = 0
    element_counts: Counter[str] = Counter()
    element_files: defaultdict[str, set[str]] = defaultdict(set)
    attr_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    attr_values: defaultdict[tuple[str, str], Counter[str]] = defaultdict(Counter)

    for f in files:
        try:
            tree = etree.parse(str(f))
        except etree.XMLSyntaxError:
            continue
        n_files += 1
        root = tree.getroot()
        for el in root.iter():
            if not isinstance(el.tag, str):
                continue
            name = _strip_ns(el.tag)
            element_counts[name] += 1
            element_files[name].add(f.name)
            for attr, value in el.attrib.items():
                attr_name = _strip_ns(attr)
                attr_counts[name][attr_name] += 1
                val_counter = attr_values[(name, attr_name)]
                if len(val_counter) < _ATTR_VALUE_CAP or value in val_counter:
                    val_counter[value] += 1

    elements = []
    for name in sorted(element_counts):
        attrs = []
        for attr_name, attr_count in sorted(attr_counts[name].items()):
            values = attr_values[(name, attr_name)]
            top = values.most_common(_ATTR_VALUE_DISPLAY)
            attrs.append({
                "name": attr_name,
                "count": attr_count,
                "distinct_values": len(values),
                "top_values": [
                    {"value": v, "count": c} for v, c in top
                ],
                "truncated": len(values) >= _ATTR_VALUE_CAP,
            })
        elements.append({
            "name": name,
            "count": element_counts[name],
            "in_files": len(element_files[name]),
            "attributes": attrs,
        })

    return {
        "files": n_files,
        "elements": elements,
    }


def _flag_summary(corpus_inv: dict) -> dict:
    """Frontend-relevant headline numbers, derived from the inventory."""
    by_name = {e["name"]: e for e in corpus_inv["elements"]}

    def el(name):
        return by_name.get(name, {"count": 0, "in_files": 0, "attributes": []})

    def attr_value_count(name, attr, target_value):
        e = by_name.get(name)
        if not e:
            return 0
        for a in e["attributes"]:
            if a["name"] != attr:
                continue
            for v in a["top_values"]:
                if v["value"] == target_value:
                    return v["count"]
        return 0

    def attr_total(name, attr):
        e = by_name.get(name)
        if not e:
            return 0
        for a in e["attributes"]:
            if a["name"] == attr:
                return a["count"]
        return 0

    rs = el("rs")
    rs_total = rs["count"]
    rs_type_event = attr_value_count("rs", "type", "event")
    rs_type_person = attr_value_count("rs", "type", "person")
    rs_type_org = attr_value_count("rs", "type", "org")
    rs_type_place = attr_value_count("rs", "type", "place")
    rs_ref_total = attr_total("rs", "ref")

    return {
        "rs_total": rs_total,
        "rs_type_event": rs_type_event,
        "rs_type_person": rs_type_person,
        "rs_type_org": rs_type_org,
        "rs_type_place": rs_type_place,
        "rs_with_ref": rs_ref_total,
        "ref_ratio": (rs_ref_total / rs_total) if rs_total else 0.0,
        "fn_count": el("fn")["count"],
        "rel_count": el("rel")["count"],
        "persName_count": el("persName")["count"],
        "orgName_count": el("orgName")["count"],
        "placeName_count": el("placeName")["count"],
        "date_count": el("date")["count"],
        "triggerstring_count": el("triggerstring")["count"],
        "occupation_count": el("occupation")["count"],
    }


def build_inventory() -> dict:
    src = _sources_dir()
    corpora = []
    for collection, sub, done in _iter_subcorpora(src):
        inv = _scan_corpus(done)
        summary = _flag_summary(inv)
        corpora.append({
            "path": f"{collection}/{sub}",
            "done_dir": str(done.relative_to(src)),
            "files": inv["files"],
            "headline": summary,
            "elements": inv["elements"],
        })
    return {
        "sources_dir": str(src),
        "generated": date.today().isoformat(),
        "corpora": corpora,
    }


def _format_value(v):
    if isinstance(v, float):
        return f"{v*100:.1f}%"
    return str(v)


def _write_markdown(report: dict, path: Path) -> None:
    lines = []
    lines.append("# TEI-Inventar pro Subkorpus")
    lines.append("")
    lines.append(f"Quelle: `{report['sources_dir']}`")
    lines.append(f"Stand: {report['generated']}")
    lines.append("")
    lines.append("## Querschnitt")
    lines.append("")
    lines.append(
        "| Korpus | Dateien | rs gesamt | rs/event | rs/person | rs/org | rs/place | rs mit ref | ref-Quote |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for c in report["corpora"]:
        h = c["headline"]
        lines.append(
            f"| `{c['path']}` | {c['files']} | {h['rs_total']} | "
            f"{h['rs_type_event']} | {h['rs_type_person']} | "
            f"{h['rs_type_org']} | {h['rs_type_place']} | "
            f"{h['rs_with_ref']} | {_format_value(h['ref_ratio'])} |"
        )
    lines.append("")
    lines.append("Weitere Schluesselelemente pro Korpus:")
    lines.append("")
    lines.append(
        "| Korpus | persName | orgName | placeName | fn | rel | date | occupation | triggerstring |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for c in report["corpora"]:
        h = c["headline"]
        lines.append(
            f"| `{c['path']}` | {h['persName_count']} | {h['orgName_count']} | "
            f"{h['placeName_count']} | {h['fn_count']} | {h['rel_count']} | "
            f"{h['date_count']} | {h['occupation_count']} | "
            f"{h['triggerstring_count']} |"
        )
    lines.append("")

    for c in report["corpora"]:
        lines.append(f"## {c['path']}")
        lines.append("")
        lines.append(f"Dateien: {c['files']}, Element-Typen: {len(c['elements'])}")
        lines.append("")
        lines.append("| Element | Count | Dateien | Attribute (Top-Werte) |")
        lines.append("|---|---:|---:|---|")
        for el in c["elements"]:
            attr_strs = []
            for a in el["attributes"]:
                top = ", ".join(
                    f"{v['value']}={v['count']}"
                    for v in a["top_values"][:6]
                )
                more = "+..." if a["truncated"] else ""
                attr_strs.append(f"@{a['name']} ({a['distinct_values']}{more}: {top})")
            attrs_md = "; ".join(attr_strs) if attr_strs else "-"
            lines.append(
                f"| `{el['name']}` | {el['count']} | {el['in_files']} | {attrs_md} |"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_inventory():
    report = build_inventory()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = report["generated"]
    json_path = REPORTS_DIR / f"inventory-{stamp}.json"
    md_path = REPORTS_DIR / f"inventory-{stamp}.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_markdown(report, md_path)
    print(f"[verify] Inventar: {md_path}")
    print(f"[verify]            {json_path}")
    print(
        f"[verify] {len(report['corpora'])} Subkorpora, "
        f"Quelle: {report['sources_dir']}"
    )
    return report
