"""Audience-Modell fuer oeffentliche vs. private Builds.

Steuert, welche Funktionen und Felder im Build sichtbar sind. Orthogonal
zur Stufenwahl in frontend.stages: Stage waehlt den Korpus-Umfang und
das Mentioned-Toggle, Audience waehlt die UI-Sichtbarkeit von noch nicht
publikationsreifen Sektionen und technischen IDs.

Werte (Begriffsbildung analog zu GitHub-Repos):
- public:  Veroeffentlichungs-Stand fuer GitHub Pages. Versteckt die
           Sektionen Analyse und Exploration und blendet technische IDs
           (pe__..., org__..., Event-IDs) im Frontend aus.
- private: Vollstand fuer Projektpartner und interne Pruefung. Enthaelt
           alle experimentellen Sektionen und IDs.

Ein Audience-Wechsel wirkt ueber die Umgebungsvariable FRONTEND_AUDIENCE
auf frontend.config.DOCS_DIR (Suffix -private fuer private Builds) und
ueber den Jinja-Globals-Eintrag 'audience' auf alle Templates.

Hintergrund: Protokoll der internen Besprechung vom 18. Mai 2026.
"""

from __future__ import annotations

import os


AUDIENCES = {
    "public": {
        "id": "public",
        "label": "Oeffentlich",
        "show_analysis_section": False,
        "show_exploration_section": False,
        "show_entity_ids": False,
        "show_event_ids": False,
        "description": (
            "Veroeffentlichungs-Stand fuer GitHub Pages. Versteckt "
            "experimentelle Sektionen (Analyse, Exploration) und "
            "technische IDs (pe__..., org__..., Event-IDs)."
        ),
    },
    "private": {
        "id": "private",
        "label": "Privat",
        "show_analysis_section": True,
        "show_exploration_section": True,
        "show_entity_ids": True,
        "show_event_ids": True,
        "description": (
            "Vollstand fuer Projektpartner und interne Pruefung. Enthaelt "
            "alle experimentellen Sektionen und IDs."
        ),
    },
}


DEFAULT_AUDIENCE_ID = "public"


def active_audience_id() -> str:
    """Aktive Audience-ID aus FRONTEND_AUDIENCE.

    Faellt auf 'public' zurueck, wenn die Variable fehlt oder einen
    ungueltigen Wert traegt.
    """
    raw = os.environ.get("FRONTEND_AUDIENCE", "").strip().lower()
    if not raw:
        return DEFAULT_AUDIENCE_ID
    if raw not in AUDIENCES:
        return DEFAULT_AUDIENCE_ID
    return raw


def active_audience() -> dict:
    """Aktives Audience-Dict. Nie None: faellt auf 'public' zurueck."""
    return AUDIENCES[active_audience_id()]


def set_audience_env(audience_id: str) -> None:
    """Aktiviert die Audience fuer den aktuellen Prozess.

    Muss VOR dem Import von frontend.config gerufen werden, weil
    DOCS_DIR beim Import berechnet wird.
    """
    if audience_id not in AUDIENCES:
        raise ValueError(
            f"Unbekannte Audience {audience_id!r}. "
            f"Verfuegbar: {sorted(AUDIENCES)}"
        )
    os.environ["FRONTEND_AUDIENCE"] = audience_id


def output_dir_suffix(audience_id: str | None = None) -> str:
    """Suffix fuer das Output-Verzeichnis.

    Leerer String fuer public (damit der Default-Build weiterhin nach
    docs/ schreibt), '-private' fuer private Builds. Wird in
    frontend.config an den Stage-Output-Dir-Namen angehaengt, so dass
    Stage 1 + private nach docs-private/ schreibt und Stage 2 +
    private nach docs-with-mentioned-private/.
    """
    aid = audience_id if audience_id is not None else active_audience_id()
    if aid == DEFAULT_AUDIENCE_ID:
        return ""
    return f"-{aid}"
