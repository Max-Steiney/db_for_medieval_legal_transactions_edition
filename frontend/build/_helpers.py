"""Shared build helpers.

Low-level: date and Markdown helpers, path mapping, Jinja init,
label resolution, XPath snippets, sort key for nav, static asset copy.
Imported by all other build modules.
"""

import json
import shutil
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
import markdown as markdown_lib

from pipeline.config import SOURCES_DIR, NS_MAP, REPO_ROOT
from pipeline.utils.xml_loader import collect_source_files
from pipeline.utils.text_utils import normalize_space, elem_text, strip_hash

from frontend.config import (
    DOCS_DIR, TEMPLATES_DIR, STATIC_DIR,
    DATA_DIR, FACSIMILE_BASE_URLS,
    RELEASED_PERIOD, is_released_corpus,
    released_period_label, unprocessed_gaps_label, max_year_with_extensions,
)
from frontend.audiences import active_audience
from frontend.register import load_persons, load_orgs, load_places


_GERMAN_MONTHS = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]


def _format_german_date(dt):
    """Format a date as '17. April 2026'."""
    return f"{dt.day}. {_GERMAN_MONTHS[dt.month - 1]} {dt.year}"


def _pipeline_repo_data_date():
    """Return the date of the last git commit in the pipeline repo as a German-formatted string.

    Falls back to today's date if git is unavailable or the repo has no commits.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        iso = result.stdout.strip()
        if iso:
            dt = datetime.fromisoformat(iso).date()
            return _format_german_date(dt)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return _format_german_date(date.today())


def _create_markdown_processor():
    """Create Markdown processor with standard project config."""
    return markdown_lib.Markdown(extensions=[
        "tables",
        "fenced_code",
        "codehilite",
        "toc",
        "attr_list",
    ], extension_configs={
        "toc": {
            "toc_depth": "2-3",
            "permalink": True,
        },
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
    })


# Two-layer UI: scholarly labels for technical path fragments
COLLECTION_LABELS = {
    "QGW/Vienna_1177-1414_ready": "QGW II/1 (1177–1414)",
    "QGW/Vienna_1415-1417": "QGW II/2 (1415–1417)",
    "QGW/Vienna_1448-57_ready": "QGW II/2 (1448–1457)",
    "QGW/Vienna_1458-66": "QGW II/3 (1458–1466)",
    "QGW/Vienna_1493-1500": "QGW II/4 (1493–1500)",
    "QGW/Vienna_1524": "QGW II/5 (1524)",
    "Stadtbuecher/Band_1_1395-1400_ready": "Stadtbücher Bd. 1 (1395–1400)",
    "Gewerbuch_D/GB_D_1448-60_ready": "Gewerbuch D (1448–1460)",
    "Satzbuch_CD/SB_CD_1448-60_ready": "Satzbuch CD (1448–1460)",
    "Copeybuch_Zeibig/Buergeraufgebot_1454_05_29_ready": "Copeybuch (Zeibig): Bürgeraufgebot (1454)",
    "Copeybuch_Zeibig/Geldeintreiber_Feuerordnung_1454-05-22_ready": "Copeybuch (Zeibig): Feuerordnung (1454)",
    "Copeybuch_Zeibig/Versammlung_1454-03-30_ready": "Copeybuch (Zeibig): Versammlung (1454)",
    "GenanntenListe_Weinzettel/Gen_Weinz_1459-61_ready": "Genannten-Liste Weinzettel (1459–1461)",
    "Genanntenliste_Stubenviertel/GenStub_1461-66": "Genanntentafel Stubenviertel (1461–1466)",
    "Widmerliste/widmer_1448_ready": "Widmerliste (1448)",
}


def _collection_label(collection, subcollection):
    """Return scholarly label for a collection path, with path as fallback."""
    key = f"{collection}/{subcollection}"
    return COLLECTION_LABELS.get(key, key)


def _xpath_text(root, xpath_expr, default=""):
    """Extract text from first XPath match, or return default."""
    elems = root.xpath(xpath_expr, namespaces=NS_MAP)
    return normalize_space(elem_text(elems[0])) if elems else default


def _extract_regest(root, max_len=200):
    """Extract abstract/entry text as regest preview."""
    for div_type in ("abstract", "entry"):
        divs = root.xpath(
            f".//tei:text//tei:div[@type='{div_type}']", namespaces=NS_MAP
        )
        if divs:
            raw = normalize_space("".join(divs[0].itertext()))
            if raw and not raw.lower().startswith("tei version"):
                if len(raw) > max_len:
                    return raw[:max_len].rsplit(" ", 1)[0] + "…"
                return raw
    return ""


def _extract_entity_refs(root):
    """Extract all entity IDs referenced in the document text.

    Scans <rs type="person|org|place" ref="..."> and <roleName corresp="...">.
    Returns a de-duplicated set of bare entity IDs (without '#' prefix).
    """
    refs = set()
    for rs in root.xpath(
        ".//tei:text//tei:rs[@type='person' or @type='org' or @type='place']",
        namespaces=NS_MAP,
    ):
        ref = strip_hash(rs.get("ref", ""))
        if ref and ref != "NULL":
            refs.add(ref)
    for rn in root.xpath(
        ".//tei:text//tei:roleName[@corresp]",
        namespaces=NS_MAP,
    ):
        corresp = strip_hash(rn.get("corresp", ""))
        if corresp:
            refs.add(corresp)
    return refs


def _format_de_int(value):
    """Format an integer with German thousand separators ('.' as group sep).

    Used as the ``de_int`` Jinja filter so templates can write ``{{ n | de_int }}``
    instead of repeating ``"{:,}".format(n).replace(",", ".")``.
    """
    try:
        return "{:,}".format(int(value)).replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def _init_jinja():
    """Create Jinja2 environment."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    env.globals["build_date"] = _format_german_date(date.today())
    env.globals["data_date"] = _pipeline_repo_data_date()
    env.globals["asset_v"] = datetime.now().strftime("%Y%m%d%H%M%S")
    rp = dict(RELEASED_PERIOD)
    rp["max_year_with_extensions"] = max_year_with_extensions()
    env.globals["released_period"] = rp
    env.globals["released_period_label"] = released_period_label()
    env.globals["unprocessed_gaps_label"] = unprocessed_gaps_label()
    audience = active_audience()
    env.globals["audience"] = audience
    env.globals["audience_id"] = audience["id"]
    env.filters["de_int"] = _format_de_int
    return env


def _normalize_facsimile_url(raw_url, collection):
    """Normalize a single facsimile URL.

    Absolute URLs (http/https) pass through unchanged. Relative filenames
    are resolved against FACSIMILE_BASE_URLS if the collection has a
    configured base URL, otherwise dropped (return None).
    """
    if not raw_url:
        return None
    if raw_url.startswith(("http://", "https://")):
        return raw_url
    base = FACSIMILE_BASE_URLS.get(collection)
    if base:
        return base + raw_url
    return None


def _output_path(filepath):
    """Compute output HTML path, dropping 'done/' from the path."""
    rel = filepath.relative_to(SOURCES_DIR)
    parts = [p for p in rel.parts if p != "done"]
    out = DOCS_DIR / "documents" / Path(*parts).with_suffix(".html")
    return out


def _relative_to_root(output_path):
    """Compute relative path from output file back to docs root."""
    depth = len(output_path.relative_to(DOCS_DIR).parts) - 1
    if depth <= 0:
        return "."
    return "/".join([".."] * depth)


def _is_done_file(filepath):
    """Check if file is in a 'done' directory."""
    return "done" in filepath.relative_to(SOURCES_DIR).parts


def _is_released_file(filepath):
    """True if the file belongs to a released source corpus."""
    rel = filepath.relative_to(SOURCES_DIR)
    if len(rel.parts) < 2:
        return False
    return is_released_corpus(f"{rel.parts[0]}/{rel.parts[1]}")


def _tei_output_path(filepath):
    """Compute output path for TEI-XML source copy.

    Maps sources/{collection}/{sub}/done/{file}.xml
    to docs/tei/{collection}/{sub}/{file}.xml (strips 'done').
    """
    rel = filepath.relative_to(SOURCES_DIR)
    parts = [p for p in rel.parts if p != "done"]
    return DOCS_DIR / "tei" / Path(*parts)


def _load_registers():
    """Load person/org/place registers with timing."""
    print("Loading registers...")
    t0 = time.time()
    persons = load_persons()
    orgs = load_orgs()
    places = load_places()
    print(f"  Loaded {len(persons)} persons, {len(orgs)} orgs, {len(places)} places "
          f"in {time.time() - t0:.1f}s")
    return persons, orgs, places


def _sort_key_for_nav(filename):
    """Sort key for sequential navigation: numeric if possible, else string."""
    try:
        return (0, int(filename), "")
    except (ValueError, TypeError):
        return (1, 0, str(filename))


def _compute_prev_next(all_metadata):
    """Compute previous/next document links within each collection."""
    by_collection = {}
    for meta in all_metadata:
        cp = meta.get("collection_path", "")
        by_collection.setdefault(cp, []).append(meta)

    for cp, metas in by_collection.items():
        metas.sort(key=lambda m: _sort_key_for_nav(m.get("filename", "")))
        for i, meta in enumerate(metas):
            if i > 0:
                meta["prev_url"] = metas[i - 1].get("url", "")
                meta["prev_id"] = metas[i - 1].get("idno", "")
            else:
                meta["prev_url"] = ""
                meta["prev_id"] = ""
            if i < len(metas) - 1:
                meta["next_url"] = metas[i + 1].get("url", "")
                meta["next_id"] = metas[i + 1].get("idno", "")
            else:
                meta["next_url"] = ""
                meta["next_id"] = ""


def _format_table_date(rec):
    """Format docs_aggregate date fields for the documents-table display.

    Pipeline convention: ISO date YYYY-MM-DD, uncertainty expressed as
    YYYY-01-01 | YYYY-12-31 (fuzzy year) or
    YYYYa-01-01 | YYYYb-12-31 (year range).
    """
    start = rec.get("date_iso_start", "") or ""
    end = rec.get("date_iso_end", "") or ""
    year = rec.get("date_year", "")
    if not start:
        return ""
    is_full_year_range = (
        start != end
        and start.endswith("-01-01")
        and end.endswith("-12-31")
    )
    if is_full_year_range:
        ys, ye = start[:4], end[:4]
        return ys if ys == ye else f"{ys}–{ye}"
    if len(start) >= 10 and start[4] == "-" and start[7] == "-":
        try:
            y, mo, d = start[:10].split("-")
            return f"{d}.{mo}.{y}"
        except ValueError:
            pass
    if len(start) >= 7 and start[4] == "-":
        try:
            y, mo = start[:7].split("-")
            return f"{mo}.{y}"
        except ValueError:
            pass
    return str(year) if year else start


def _load_docs_aggregate_lookup():
    """Build (collection_path, idno) -> aggregate-record lookup.

    Reads docs/data/docs_aggregate.json (written by aggregator during
    run_aggregation). Falls back to {} if the file is missing.
    """
    path = DATA_DIR / "docs_aggregate.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        (rec.get("collection_path", ""), rec.get("idno", "")): rec
        for rec in payload.get("docs", [])
    }


def _copy_static():
    """Copy static assets to docs/static/."""
    target = DOCS_DIR / "static"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(str(STATIC_DIR), str(target))


def _copy_tei_sources():
    """Copy all 'done' TEI-XML sources to docs/tei/ for static download.

    Removes stale copies from previous builds before copying.
    """
    tei_dir = DOCS_DIR / "tei"
    if tei_dir.exists():
        shutil.rmtree(tei_dir)

    all_files = collect_source_files()
    done_files = [f for f in all_files if _is_done_file(f) and _is_released_file(f)]

    copied = 0
    for filepath in done_files:
        dest = _tei_output_path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(filepath), str(dest))
        copied += 1

    print(f"  TEI sources: {copied} files copied to {DOCS_DIR.name}/tei/")
