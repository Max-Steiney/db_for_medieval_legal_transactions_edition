"""KPIs of the released corpus, sourced directly from TEI via XPath.

Single source of truth for the header figures on the start page, exploration
and analysis pages. The pipeline CSVs are not consulted here — only the
TEI sources under sources/<corpus>/done/.
"""

import csv as _csv

from markupsafe import Markup

from frontend.config import RELEASED_CORPORA, visible_corpora
from frontend.build._helpers import COLLECTION_LABELS


_TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# XPath specs — single source of truth for all release-KPIs. These are the
# same expressions documented in the public Provenance-Tooltips on the
# homepage. Counted directly against the released TEI files; CSV outputs
# from the pipeline are only used for non-KPI auxiliary data.
_XP_TOP_EVENTS = (
    "//tei:body//tei:rs[@type='event']"
    "[not(ancestor::tei:rs[@type='event'])]"
)
# With the mentioned-events override every annotated rs-event counts.
_XP_ALL_EVENTS = "//tei:body//tei:rs[@type='event']"
_XP_PERSONS_EXCL_MENTIONED = (
    "//tei:body//tei:*[@type='person']"
    "[not(ancestor::tei:rs[@type='event']"
    "     [ancestor::tei:rs[@type='event']])]"
)
_XP_PERSONS_ALL = "//tei:body//tei:*[@type='person']"


def _active_event_xpath():
    """Active event selector for KPIs. Switches to _XP_ALL_EVENTS when the
    PIPELINE_INCLUDE_MENTIONED_EVENTS override is set."""
    from pipeline.config import include_mentioned_events
    return _XP_ALL_EVENTS if include_mentioned_events() else _XP_TOP_EVENTS


def _active_person_mention_xpath():
    """Active person-mention selector for KPIs. With the override active,
    person annotations inside nested events count as mentions too."""
    from pipeline.config import include_mentioned_events
    return _XP_PERSONS_ALL if include_mentioned_events() else _XP_PERSONS_EXCL_MENTIONED


def _scan_released_tei():
    """Walk all released TEI sources and collect KPIs directly via XPath.

    Single source of truth for the release-level numbers shown on the
    homepage. The pipeline CSVs are not used here. Two passes per file:

    - ``_XP_PERSONS_ALL`` drives the distinct-person count and
      "Quellen mit Personen" — a person counts as soon as she is annotated
      anywhere in a released file, including inside a nested rs-event.
    - ``_XP_PERSONS_EXCL_MENTIONED`` drives the mention count — a mention
      only counts if the annotation is not inside a nested rs-event.

    The asymmetry is intentional and documented in
    ``knowledge/specification.md`` ("Asymmetrische Zaehlung: individuelle
    Personen vs. Nennungen").

    Returns a tuple (totals, per_corpus) where totals is a flat dict and
    per_corpus is a list of dicts with the same shape per corpus, ordered
    as in RELEASED_CORPORA.
    """
    from lxml import etree
    from pipeline.config import SOURCES_DIR

    def _new_bucket():
        return {
            "sources": 0,
            "files_with_persons": set(),
            "person_mentions": 0,
            "distinct_persons": set(),
            "distinct_events": set(),
        }

    corpora = visible_corpora()
    totals = _new_bucket()
    per_corpus = {c: _new_bucket() for c in corpora}
    event_xp = _active_event_xpath()
    person_mention_xp = _active_person_mention_xpath()

    for path_key in corpora:
        coll, sub = path_key.split("/", 1)
        done = SOURCES_DIR / coll / sub / "done"
        if not done.exists():
            continue
        for tei_file in sorted(done.rglob("*.xml")):
            try:
                tree = etree.parse(str(tei_file))
            except etree.XMLSyntaxError:
                continue
            cb = per_corpus[path_key]
            cb["sources"] += 1
            totals["sources"] += 1

            for ev in tree.xpath(event_xp, namespaces=_TEI_NS):
                ref = (ev.get("ref") or "").strip().lstrip("#")
                if ref:
                    cb["distinct_events"].add(ref)
                    totals["distinct_events"].add(ref)

            for el in tree.xpath(person_mention_xp, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if not ref.startswith("pe__"):
                    continue
                cb["person_mentions"] += 1
                totals["person_mentions"] += 1

            file_has_person = False
            for el in tree.xpath(_XP_PERSONS_ALL, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if not ref.startswith("pe__"):
                    continue
                file_has_person = True
                cb["distinct_persons"].add(ref)
                totals["distinct_persons"].add(ref)
            if file_has_person:
                cb["files_with_persons"].add(tei_file.name)
                totals["files_with_persons"].add(str(tei_file))

    def _flatten(b):
        return {
            "sources": b["sources"],
            "sources_with_persons": len(b["files_with_persons"]),
            "person_mentions": b["person_mentions"],
            "distinct_persons": len(b["distinct_persons"]),
            "distinct_events": len(b["distinct_events"]),
        }

    flat_totals = _flatten(totals)
    flat_per_corpus = [
        {"path": c, "label": COLLECTION_LABELS.get(c, c), **_flatten(per_corpus[c])}
        for c in corpora
    ]
    return flat_totals, flat_per_corpus


def _compute_corpus_breakdown():
    """Backward-compatible wrapper around _scan_released_tei for the start
    page corpus matrix. Persons inside mentioned events are excluded
    (legacy-consistent).
    """
    _, per_corpus = _scan_released_tei()
    return [
        {
            "path": c["path"],
            "label": c["label"],
            "sources": c["sources"],
            "mentions": c["person_mentions"],
            "events": c["distinct_events"],
        }
        for c in per_corpus
    ]


def _compute_release_kpis():
    """Compute the canonical released-data KPIs directly from TEI via XPath.

    Wraps :func:`_scan_released_tei`. The default values match the legacy
    frontend output:

    - ``sources_total``, ``sources_with_persons`` — file-level counts.
    - ``distinct_persons`` — distinct ``pe__``-keys across all
      person-annotations (including those inside mentioned rs-events).
    - ``person_mentions`` — mention count *outside* mentioned rs-events.
    - ``distinct_events`` — distinct top-level ``<rs type='event'>``.
    - ``register_total`` — size of the full person register
      (``indices/personList.xml``), shown for context.
    """
    from pipeline.config import PIPELINE_OUTPUT

    totals, _ = _scan_released_tei()

    register_total = 0
    pe_path = PIPELINE_OUTPUT / "persons.csv"
    with pe_path.open(encoding="utf-8") as fh:
        register_total = sum(1 for _ in _csv.DictReader(fh, delimiter=";"))

    return {
        "sources_total": totals["sources"],
        "sources_with_persons": totals["sources_with_persons"],
        "distinct_persons": totals["distinct_persons"],
        "person_mentions": totals["person_mentions"],
        "distinct_events": totals["distinct_events"],
        "register_total": register_total,
    }


def _compute_matrix_columns(total_docs, total_mentions, total_events):
    """Return the column configs of the corpus matrix as a data structure.

    Three data columns: sources, mentions, events. Each column carries
    both the glossary definition (for the i-icon tooltip on the header)
    and the data-provenance text (for the tooltip on the total figure).
    The template iterates over this list instead of writing each block
    out individually.
    """
    return [
        {
            "id": "sources",
            "label": "Quellen",
            "glossary_id": "gloss-quelle",
            "glossary_term": "Quelle",
            "glossary_slug": "quelle",
            "glossary_def": Markup(
                "Definition in redaktioneller &Uuml;berarbeitung."
            ),
            "total": total_docs,
            "row_key": "sources",
            "prov_id": "prov-total-sources",
            "prov_title": "Quellen",
            "prov_description": Markup(
                "Anzahl der freigegebenen Quellen im Editionsstand. "
                "Eine Quelle ist eine einzelne TEI-XML-Datei mit einem "
                "Regest und seinen Annotationen."
            ),
            "prov_source": Markup(
                "Direkt aus den freigegebenen TEI-Quellen, gez&auml;hlt "
                "pro Datei."
            ),
        },
        {
            "id": "mentions",
            "label": "Nennungen",
            "glossary_id": "gloss-nennung",
            "glossary_term": "Gesamtnennung",
            "glossary_slug": None,
            "glossary_def": Markup(
                "Definition in redaktioneller &Uuml;berarbeitung."
            ),
            "total": total_mentions,
            "row_key": "mentions",
            "prov_id": "prov-total-mentions",
            "prov_title": "Nennungen",
            "prov_description": Markup(
                "Wie oft Personen in den Quellen genannt werden. "
                "Eine Person, die in zwei verschiedenen Quellen vorkommt, "
                "z&auml;hlt zweimal."
            ),
            "prov_source": Markup(
                "Aus den Personen-Annotationen in den freigegebenen TEI-"
                "Quellen. Mehrfachnennungen innerhalb derselben Quelle "
                "z&auml;hlen einmal."
            ),
        },
        {
            "id": "events",
            "label": "Events",
            "glossary_id": "gloss-event",
            "glossary_term": "Event",
            "glossary_slug": "event",
            "glossary_def": Markup(
                "Definition in redaktioneller &Uuml;berarbeitung."
            ),
            "total": total_events,
            "row_key": "events",
            "prov_id": "prov-total-events",
            "prov_title": "Events",
            "prov_description": Markup(
                "Anzahl der annotierten Vorg&auml;nge in den Quellen. "
                "Ein Event ist ein konkreter Akt: Rechtsgesch&auml;ft, "
                "Siegelvermerk, Stadtbucheintrag oder Notiz."
            ),
            "prov_source": Markup(
                "Aus den Event-Annotationen in den freigegebenen TEI-Quellen, "
                "verschachtelte Events ausgeschlossen."
            ),
        },
    ]


def _released_person_keys():
    """Return the set of distinct person_keys that appear anywhere in the
    released TEI sources. This matches the headline 'Individuelle Personen'
    figure: a person enters the public register as soon as she is annotated
    in any released file, regardless of whether the only attestation sits
    inside a mentioned (nested) rs-event."""
    from lxml import etree
    from pipeline.config import SOURCES_DIR

    keys = set()
    for path_key in visible_corpora():
        coll, sub = path_key.split("/", 1)
        done = SOURCES_DIR / coll / sub / "done"
        if not done.exists():
            continue
        for tei_file in done.rglob("*.xml"):
            try:
                tree = etree.parse(str(tei_file))
            except etree.XMLSyntaxError:
                continue
            for el in tree.xpath(_XP_PERSONS_ALL, namespaces=_TEI_NS):
                ref = (el.get("ref") or "").strip().lstrip("#")
                if ref.startswith("pe__"):
                    keys.add(ref)
    return keys


def _persons_with_org_released(released_persons):
    """Count distinct persons from the released set involved in at least
    one event with an organisation link.

    Reads persons_in_events.csv x orgs_in_events.csv and intersects with
    ``released_persons``. Idempotent against first build (returns 0 if
    the aggregator CSVs are not present).
    """
    try:
        from frontend.aggregator import _cached_csv
        pie_rows = _cached_csv("persons_in_events.csv")
        oie_rows = _cached_csv("orgs_in_events.csv")
    except Exception:
        return 0
    events_with_org = {r.get("event_key", "") for r in oie_rows
                       if r.get("event_key")}
    out = set()
    for r in pie_rows:
        pk = r.get("person_key", "")
        ek = r.get("event_key", "")
        if pk in released_persons and ek in events_with_org:
            out.add(pk)
    return len(out)
