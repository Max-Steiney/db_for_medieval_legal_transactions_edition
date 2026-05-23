"""Configuration for the frontend builder.

After the cross-repo split (2026-04-30), the frontend lives in this
publication repository while sources, registers, and the pipeline live
in the sibling repo `db_for_medieval_legal_transactions`. Path
constants below distinguish carefully between the two roots.
"""

from pathlib import Path

from pipeline.config import REPO_ROOT as PIPELINE_REPO_ROOT
from frontend.stages import active_stage

# This frontend's own repo root (the publication / Pages-served repo).
EDITION_DIR = Path(__file__).resolve().parent
FRONTEND_REPO_ROOT = EDITION_DIR.parent

# Build output stays in this repo so GitHub Pages can serve from `/docs`.
# Welches Unterverzeichnis genau, bestimmt die aktive Stufe (siehe
# frontend/stages.py): Stufe 1 schreibt nach docs/, Stufe 2 nach
# docs-with-mentioned/, Stufe 3 nach docs-full/, Stufe 4 nach docs-max/.
# Der Default ist Stufe 1; ohne CLI-Flag bleibt der publizierte Build
# unangetastet.
_ACTIVE_STAGE = active_stage()
DOCS_DIR = FRONTEND_REPO_ROOT / _ACTIVE_STAGE["output_dir"]
DATA_DIR = DOCS_DIR / "data"

# Templates, static assets, and content travel with the build code.
TEMPLATES_DIR = EDITION_DIR / "templates"
STATIC_DIR = EDITION_DIR / "static"
CONTENT_DIR = EDITION_DIR / "content"

# Sources, registers and knowledge base live in the sibling pipeline
# repository.
SOURCES_REPO_ROOT = PIPELINE_REPO_ROOT
KNOWLEDGE_DIR = PIPELINE_REPO_ROOT / "knowledge"

# Annotation guidelines are kept as a local copy under content/project/
# so the build is self-contained. The canonical source lives in the
# pipeline repo; the build syncs the local copy from it when the
# canonical document is newer (see frontend.build._pages._build_guidelines).
EDITION_GUIDELINES_PATH = CONTENT_DIR / "project" / "edition-guidelines.md"
EDITION_GUIDELINES_CANONICAL = PIPELINE_REPO_ROOT / "edition_guidelines.md"

# Backwards-compatibility alias. Some callers still import REPO_ROOT
# from this module; they expect the docs/output root.
REPO_ROOT = FRONTEND_REPO_ROOT

# Facsimile base URLs for collections that use relative filenames.
# Key: top-level directory name under sources/
# Value: Base URL to prepend to relative filenames
FACSIMILE_BASE_URLS = {
    "Satzbuch_CD": "https://id.acdh.oeaw.ac.at/grundbuecher-facs/",
}

# Editorial settings defining the release state of the edition.
# Single source of truth — propagated to templates during the build.
RELEASED_PERIOD = {
    "min_year": 1177,
    "max_year": 1412,
    "extensions": [
        {"corpora": "QGW II/2", "until": 1457},
        {"corpora": "Satzbuch CD", "until": 1460},
    ],
    "unprocessed_gaps": [
        {"from": 1418, "to": 1447},
    ],
}

# Released-corpora scope is owned by the pipeline (it's a data concept,
# not an edition concept). Re-exported here so existing edition imports
# keep working.
from pipeline.config import RELEASED_CORPORA, is_released_corpus  # noqa: E402,F401


def released_period_label():
    """Build the human-readable label for the released period.

    Liste der Extensions wird als "ergaenzt durch X bis Y und Z bis W"
    formatiert. Eine einzelne Extension behaelt die kuerzere Form bei.
    """
    rp = RELEASED_PERIOD
    label = f"{rp['min_year']}\u2013{rp['max_year']}"
    exts = rp.get("extensions") or []
    if not exts:
        return label
    if len(exts) == 1:
        e = exts[0]
        return label + f" (mit Erg\u00e4nzungen bis {e['until']} f\u00fcr {e['corpora']})"
    parts = [f"{e['corpora']} bis {e['until']}" for e in exts]
    if len(parts) == 2:
        ext_text = " und ".join(parts)
    else:
        ext_text = ", ".join(parts[:-1]) + " und " + parts[-1]
    return label + f" (erg\u00e4nzt durch {ext_text})"


def max_year_with_extensions():
    """Highest year including all extensions (e.g. 1414 for QGW II/1+II/2)."""
    rp = RELEASED_PERIOD
    candidates = [rp["max_year"]] + [e["until"] for e in rp.get("extensions", [])]
    return max(candidates)


def unprocessed_gaps_label():
    """Build a sentence listing unprocessed periods."""
    gaps = RELEASED_PERIOD["unprocessed_gaps"]
    if not gaps:
        return ""
    parts = [f"{g['from']}\u2013{g['to']}" for g in gaps]
    return ", ".join(parts) + ": noch nicht ausgewertet."
