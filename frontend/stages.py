"""Stufenmodell fuer Korpus-Auswahl und Annotationsebenen.

Jede Stufe ist eine benannte Kombination aus vier Achsen, die das
Build-Verhalten festlegt. Eine im Frontend angezeigte Zahl wird damit
interpretierbar als Aussage unter einer bestimmten Stufe.

Achsen:
- corpora_scope:   "released" (nur die Standard-Freigegebenen, gleich der
                    pipeline.config.RELEASED_CORPORA), "all_ready" (alle
                    Subkorpora mit _ready-Suffix), "all_tei" (alle Subkorpora
                    mit TEI-Dateien).
- include_mentioned: bool. Schaltet verschachtelte rs-Events ein/aus.
- place_visibility:  "inline" (nur Markup ohne Sprungziel), "register"
                    (eigene Listen- und Profilseiten), "register_plus_map"
                    (zusaetzlich Karte).
- display_filter:    "fixed" (Build-Time-Filter), "toggleable" (UI-Filter
                    fuer Freigabe-Status).

Ein Stufen-Wechsel wirkt ueber die Umgebungsvariable FRONTEND_STAGE auf
frontend.config.DOCS_DIR und pipeline.config.include_mentioned_events().
Stufen 1 und 2 sind heute funktional aktiv; Stufen 3 und 4 bauen, liefern
aber noch denselben Daten-Output wie 1 bzw. 2, weil die zugehoerigen
Subkorpora und Features (Ortsregister, Karte) noch nicht aktiv sind.
"""

from __future__ import annotations

import os


STAGES = {
    1: {
        "id": 1,
        "name": "publication",
        "label": "Publikation",
        "corpora_scope": "released",
        "include_mentioned": False,
        "place_visibility": "inline",
        "display_filter": "fixed",
        "output_dir": "docs",
        "description": (
            "Der publizierte Stand. Konservativ, methodisch tragfaehig, "
            "wird ueber GitHub Pages ausgeliefert."
        ),
    },
    2: {
        "id": 2,
        "name": "comparison",
        "label": "Vergleich",
        "corpora_scope": "released",
        "include_mentioned": True,
        "place_visibility": "inline",
        "display_filter": "fixed",
        "output_dir": "docs-with-mentioned",
        "description": (
            "Editorisches Vergleichswerkzeug. Wie Stufe 1, aber mit "
            "verschachtelten rs-Events als vollwertigen Events."
        ),
    },
    3: {
        "id": 3,
        "name": "full-ready",
        "label": "Voller _ready-Bestand",
        "corpora_scope": "all_ready",
        "include_mentioned": False,
        "place_visibility": "register",
        "display_filter": "toggleable",
        "output_dir": "docs-full",
        "description": (
            "Alle Subkorpora mit _ready-Suffix. Ortsregister sichtbar, "
            "Freigabe-Filter umschaltbar."
        ),
    },
    4: {
        "id": 4,
        "name": "maximum",
        "label": "Maximalversion",
        "corpora_scope": "all_tei",
        "include_mentioned": True,
        "place_visibility": "register_plus_map",
        "display_filter": "toggleable",
        "output_dir": "docs-max",
        "description": (
            "Alle Subkorpora mit TEI-Annotation. Schema-Stresstest, "
            "nicht zur Publikation."
        ),
    },
}


DEFAULT_STAGE_ID = 1


def active_stage_id() -> int:
    """Aktive Stufen-ID aus der Umgebungsvariable FRONTEND_STAGE.

    Faellt auf den Default zurueck, wenn die Variable fehlt oder
    keinen gueltigen Wert traegt.
    """
    raw = os.environ.get("FRONTEND_STAGE", "").strip()
    if not raw:
        return DEFAULT_STAGE_ID
    try:
        sid = int(raw)
    except ValueError:
        return DEFAULT_STAGE_ID
    if sid not in STAGES:
        return DEFAULT_STAGE_ID
    return sid


def active_stage() -> dict:
    """Aktives Stufen-Dict. Nie None: faellt auf Stufe 1 zurueck."""
    return STAGES[active_stage_id()]


def set_stage_env(stage_id: int) -> None:
    """Aktiviert die Stufe fuer den aktuellen Prozess.

    Setzt FRONTEND_STAGE und die abgeleiteten Schalter (heute nur
    PIPELINE_INCLUDE_MENTIONED_EVENTS). Muss VOR dem Import von
    frontend.config gerufen werden, weil DOCS_DIR beim Import berechnet
    wird.
    """
    if stage_id not in STAGES:
        raise ValueError(
            f"Unbekannte Stufe {stage_id}. Verfuegbar: {sorted(STAGES)}"
        )
    stage = STAGES[stage_id]
    os.environ["FRONTEND_STAGE"] = str(stage_id)
    if stage["include_mentioned"]:
        os.environ["PIPELINE_INCLUDE_MENTIONED_EVENTS"] = "1"
    else:
        # Aktiv loeschen, falls vom Parent-Prozess gesetzt: Stufen-Wahl
        # ist explizit, sonst koennte ein verbleibendes Env-Var aus einem
        # vorhergehenden Lauf den Stage-Output verfaelschen.
        os.environ.pop("PIPELINE_INCLUDE_MENTIONED_EVENTS", None)


def output_dir_name(stage_id: int | None = None) -> str:
    """Output-Verzeichnisname fuer eine Stufe (relativ zum Repo-Root)."""
    sid = stage_id if stage_id is not None else active_stage_id()
    return STAGES[sid]["output_dir"]
