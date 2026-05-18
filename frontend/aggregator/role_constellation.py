"""Per-event participant lists for analysis/index.html (Rollen-Konstellation).
Each event carries its participants with role, sex, titles, occupations;
the client-side resolver in analysis-resolver.js matches N-Personen queries
against this JSON. See docs/data/role_constellation.json for the shape.
"""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import (
    _cached_csv,
    _load_norm_matching,
    _load_uhlirz_matching,
    _meta,
    _write_json,
)


# --- Helpers --------------------------------------------------------------

def _person_display_name(row: dict) -> str:
    """Forename + surname (or addname) + genname; multi-values take the first.

    Fallback-Kette fuer den Beinamen: surname_reg ist Hauptfeld (~11.6k
    Personen); fehlt der, traegt addname_reg den Beinamen (~3.4k Personen,
    z. B. "von Purgstall auf der Schuett"); zuletzt addname_orig (~600).
    """
    def first(s: str) -> str:
        return (s or "").split("|")[0].strip()

    fn = first(row.get("forename_reg", ""))
    sn = (first(row.get("surname_reg", ""))
          or first(row.get("addname_reg", ""))
          or first(row.get("addname_orig", "")))
    gen = first(row.get("genname", ""))
    return " ".join(p for p in (fn, sn, gen) if p) or row.get("id", "")


def _split_pipes(value: str) -> list[str]:
    """`|a|b|` -> ['a', 'b']. Empty fragments dropped."""
    if not value:
        return []
    return [p.strip() for p in value.strip("|").split("|") if p.strip()]


def _corpus_short(file_key: str, file_corpus: dict[str, str]) -> str:
    """`QGW II/1 (1177-1414)` -> `QGW II/1`."""
    label = file_corpus.get(file_key, "")
    return label.split(" (", 1)[0].strip() if label else ""


def _normalise_transaction(catchwords: str, norm_map: dict[str, str]) -> str:
    """First catchword, normalised via norm_map if available."""
    parts = _split_pipes(catchwords)
    if not parts:
        return ""
    return norm_map.get(parts[0], parts[0])


# --- Main aggregator ------------------------------------------------------

VALID_ROLES = ("issuer", "recipient", "witness", "other")


def aggregate_role_constellation(docs_data_dir: Path) -> dict:
    """Build docs/data/role_constellation.json and return it for inspection."""
    from frontend.build._helpers import COLLECTION_LABELS

    persons_rows = _cached_csv("persons.csv")
    pie_rows = _cached_csv("persons_in_events.csv")
    eis_rows = _cached_csv("events_in_sources.csv")
    fn_rows = _cached_csv("filenames.csv")
    occ_rows = _cached_csv("occ_relations_in_sources.csv")
    pis_rows = _cached_csv("persons_in_sources.csv")
    title_rows = _cached_csv("title-ref_relations_in_sources.csv")
    norm_map = _load_norm_matching()
    # Uhlirz-Klassifikation der Berufe (Spalte Gewerbe_nach_Uhlirz_GstW in
    # roleName_norm_matching.csv im Pipeline-Repo). Mapping
    # original_spelling -> [uhlirz_categories]. Wird pro Person auf die
    # o-Liste angewandt und ergibt die u-Liste (deduplisiert).
    uhlirz_map = _load_uhlirz_matching()

    person_info = {
        r["id"]: {
            "sex": r.get("sex", ""),
            "name": _person_display_name(r),
            "note": (r.get("note", "") or "").strip(),
        }
        for r in persons_rows if r.get("id")
    }

    file_corpus: dict[str, str] = {}
    for r in fn_rows:
        fk = r.get("id", "")
        coll, sub = r.get("collection", ""), r.get("subcollection", "")
        if fk and coll and sub:
            file_corpus[fk] = COLLECTION_LABELS.get(f"{coll}/{sub}", "")

    event_meta: dict[str, dict] = {}
    for r in eis_rows:
        ek = r.get("event_key", "")
        if not ek or ek in event_meta:
            continue
        event_meta[ek] = {
            "file_key": r.get("file_key", ""),
            "date": (r.get("date_not_before", "") or "").strip(),
            "tx": _normalise_transaction(r.get("catchwords", ""), norm_map),
        }

    event_occs: dict[tuple, list[str]] = defaultdict(list)
    for r in occ_rows:
        ek, pk = r.get("event_key", ""), r.get("person_key", "")
        if ek and pk:
            event_occs[(ek, pk)].extend(_split_pipes(r.get("occ", "")))

    # Zweiter Beruf-Pfad: source_prof aus persons_in_sources.csv. Dort
    # liegt die Apposition im Quellentext (Hannsen, dem wachsgiesser).
    # Editorisch ist das oft das eigentliche Handwerk, waehrend
    # occ_relations eher Funktion und Status traegt (purger, clericus).
    # Beide Spalten zusammen entsprechen dem Forschungsinteresse "wer
    # tritt als Wachsgiesser im Bestand auf", unabhaengig vom
    # Annotationsort. Gemappt wird per file_key (Quelle), weil
    # source_prof ohne event-Bezug vorliegt; alle Events einer Quelle
    # erben die source_prof-Eintraege der dort genannten Person.
    file_person_profs: dict[tuple, list[str]] = defaultdict(list)
    for r in pis_rows:
        fk, pk = r.get("file_key", ""), r.get("person_key", "")
        if fk and pk:
            file_person_profs[(fk, pk)].extend(_split_pipes(r.get("source_prof", "")))

    event_titles: dict[tuple, list[str]] = defaultdict(list)
    for r in title_rows:
        ek, pk = r.get("event_key", ""), r.get("person_key", "")
        tit = (r.get("title_ref", "") or "").strip()
        if ek and pk and tit:
            event_titles[(ek, pk)].append(tit)

    event_to_file = {ek: meta["file_key"] for ek, meta in event_meta.items()}

    event_participants: dict[str, list[dict]] = defaultdict(list)
    for r in pie_rows:
        ek, pk = r.get("event_key", ""), r.get("person_key", "")
        if not (ek and pk):
            continue
        pinfo = person_info.get(pk, {})
        role = r.get("event_role", "") or "other"
        if role not in VALID_ROLES:
            role = "other"
        # Beruf-Liste vereinigt zwei Quellen, case-insensitiv dedupliziert
        # (occ_relations kommt zuerst, dann nur die source_prof-Werte, die
        # noch nicht vertreten sind). Die Trennung der zwei Annotationsorte
        # ist editorisch real (siehe knowledge/data.md), wird hier aber
        # bewusst aufgegeben, weil das Forschungsinteresse "wer tritt als
        # Wachsgiesser auf" beide Wege gleichermaßen meint. Die Detail-
        # Trennung bleibt auf den Personenprofilen erhalten.
        occs = list(event_occs.get((ek, pk), []))
        seen_lower = {o.lower() for o in occs}
        fk = event_to_file.get(ek, "")
        for prof in file_person_profs.get((fk, pk), []):
            key = prof.lower()
            if key in seen_lower:
                continue
            occs.append(prof)
            seen_lower.add(key)
        # Uhlirz-Kategorien aus dem Beruf-Mapping ableiten, deduplisiert
        # und sortiert. Eine Person hat ggf. mehrere Berufe und damit
        # mehrere Kategorien; eine leere Liste ist der Default fuer
        # Personen ohne klassifizierten Beruf.
        uhlirz_set = set()
        for o in occs:
            # case-insensitiv, weil das CSV und die TEI-Annotation
            # gemischte Schreibungen tragen.
            for cat in uhlirz_map.get(o.lower(), []):
                uhlirz_set.add(cat)
        participant = {
            "p": pk,
            "n": pinfo.get("name", ""),
            "r": role,
            "s": pinfo.get("sex", ""),
            "t": event_titles.get((ek, pk), []),
            "o": occs,
            "u": sorted(uhlirz_set),
        }
        if pinfo.get("note"):
            participant["nt"] = pinfo["note"]
        event_participants[ek].append(participant)

    events: list[dict] = []
    occ_counter: Counter = Counter()
    uhlirz_counter: Counter = Counter()
    distinct_persons: set[str] = set()
    distinct_files: set[str] = set()
    decade_counts: Counter = Counter()
    corpus_event_counts: Counter = Counter()
    total_participations = 0

    for ek, meta in event_meta.items():
        participants = event_participants.get(ek, [])
        if not participants:
            continue
        fk = meta["file_key"]
        corpus_short = _corpus_short(fk, file_corpus)
        events.append({
            "e": ek, "f": fk, "c": corpus_short,
            "d": meta["date"], "tx": meta["tx"], "p": participants,
        })
        distinct_files.add(fk)
        corpus_event_counts[corpus_short] += 1
        year_str = (meta["date"] or "")[:4]
        if year_str.isdigit():
            decade_counts[(int(year_str) // 10) * 10] += 1
        for part in participants:
            distinct_persons.add(part["p"])
            total_participations += 1
            for occ in part["o"]:
                occ_counter[occ] += 1
            for cat in part["u"]:
                uhlirz_counter[cat] += 1

    # Histogram across the released period — gap-free decade list so the
    # range-slider histogram has no holes.
    if decade_counts:
        min_dec = min(decade_counts)
        max_dec = max(decade_counts)
        decade_histogram = [
            {"decade": d, "count": decade_counts.get(d, 0)}
            for d in range(min_dec, max_dec + 10, 10)
        ]
    else:
        decade_histogram = []

    # The TEI ``title_ref`` column does NOT hold honorifics (Herr/Frau/Bischof);
    # it carries toponymic prepositions of name forms (``zu``, ``von``,
    # ``gesessen zu``). A UI conditional "Titel = Herr" therefore has no data
    # path. We deliberately do not emit a title vocabulary; the dimension
    # ``title`` is dropped from the schema too.
    out = {
        "meta": _meta(
            description="Per-event participant lists for analysis/index.html.",
            sources=["persons.csv", "persons_in_events.csv", "events_in_sources.csv",
                     "filenames.csv", "occ_relations_in_sources.csv",
                     "persons_in_sources.csv",
                     "normalisation_lists/roleName_norm_matching.csv"],
            dimensions=[
                {"id": "event",      "label": "Event"},
                {"id": "person",     "label": "Person"},
                {"id": "role",       "label": "Funktionsrolle", "values": list(VALID_ROLES)},
                {"id": "sex",        "label": "Geschlecht",     "values": ["m", "f"]},
                {"id": "occupation", "label": "Beruf/Tätigkeit"},
                {"id": "uhlirz",     "label": "Uhlirz-Berufsklasse"},
            ],
            measures=[],
        ),
        "vocab": {
            "occupation": [{"value": v, "count": c} for v, c in occ_counter.most_common(50)],
            "uhlirz": sorted(uhlirz_counter.keys()),
        },
        "coverage": {
            "total_events": len(events),
            "total_sources": len(distinct_files),
            "total_persons": len(distinct_persons),
            "total_participations": total_participations,
            "decade_histogram": decade_histogram,
            "corpus_event_counts": [
                {"key": k, "count": c} for k, c in corpus_event_counts.most_common()
            ],
        },
        "events": events,
    }
    _write_json(out, docs_data_dir / "role_constellation.json")
    return out
