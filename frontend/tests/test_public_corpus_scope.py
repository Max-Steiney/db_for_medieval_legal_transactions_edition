"""Invarianten gegen den gebauten oeffentlichen Stand (docs/).

Behauptet das Stakeholder-Prinzip direkt: oeffentlich erscheinen nur die
zwei freigegebenen Sammlungen, keine Entitaet ohne Quelle, keine verwaiste
Profil-Datei, kein Link in eine versteckte Quelle. Diese Tests haetten die
beiden gefundenen Lecks (verwaiste Profile, occ-Netzwerk) gefangen.
Stakeholder decision: Protokoll 18.05.2026 ("QGW bis 1414, StB Bd. 1").

Lesen den oeffentlichen Build-Output; ueberspringen, wenn er fehlt.
"""

import json
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[2] / "docs"

PUBLIC_CORPORA = {
    "QGW/Vienna_1177-1414_ready",
    "Stadtbuecher/Band_1_1395-1400_ready",
}
HIDDEN_SUBDIRS = (
    "QGW/Vienna_1415-1417",
    "QGW/Vienna_1448-57_ready",
    "Satzbuch_CD/SB_CD_1448-60_ready",
)
HIDDEN_DOC_PATHS = (
    "documents/QGW/Vienna_1415-1417",
    "documents/QGW/Vienna_1448-57",
    "documents/Satzbuch_CD",
)
# So tauchen versteckte Sammlungen in den Aggregat-JSONs auf: als
# file_key-Praefix (f__Satzbuch_CD_...) bzw. Collection-Key und als
# Anzeige-Label (corpus_event_counts, per-Event-Feld). Die file_keys der
# QGW-II/2-Quellen kollidieren mit den oeffentlichen QGW-Keys (f__QGW_<n>),
# darum wird QGW II/2 nur ueber das Label erkannt. Diese Marker fehlten und
# liessen das Aggregat-Leck (Befund Gesamtanalyse 2026-05-27) durchrutschen.
HIDDEN_AGGREGATE_MARKERS = (
    "Satzbuch_CD",
    "Satzbuch CD",
    "QGW II/2",
)


def _load(rel):
    p = DOCS / rel
    if not p.exists():
        pytest.skip(f"build artifact not found: {rel}")
    return json.loads(p.read_text(encoding="utf-8"))


def test_no_hidden_corpus_in_any_data_json():
    """Keine Daten-JSON im oeffentlichen Build nennt eine versteckte Sammlung.

    Breiter Klassen-Test ueber das gesamte data/-Verzeichnis statt einzelner
    Dateien: faengt das docs_aggregate.json-Leck und jede kuenftige Aggregat-
    Datei, die den Sicht-Filter vergisst. Wuerde frueher gegriffen haben,
    haette dieser Test den per-Quelle-Aggregat-Leak sofort gemeldet.
    """
    data_dir = DOCS / "data"
    if not data_dir.exists():
        pytest.skip("docs/data/ noch nicht gebaut")
    needles = HIDDEN_SUBDIRS + HIDDEN_DOC_PATHS + HIDDEN_AGGREGATE_MARKERS
    offenders = []
    for p in sorted(data_dir.glob("*.json")):
        txt = p.read_text(encoding="utf-8")
        hits = sum(txt.count(n) for n in needles)
        if hits:
            offenders.append(f"{p.name} ({hits})")
    assert not offenders, (
        f"Daten-JSONs nennen versteckte Sammlungen: {offenders}. "
        f"Wahrscheinlich fehlt ein is_visible_corpus-Filter in der Aggregation."
    )


def test_aggregate_jsons_free_of_hidden_corpora():
    """Die fuenf ueber _cached_csv aggregierten JSONs nennen kein verstecktes Korpus.

    Engt den breiten Klassen-Test auf genau die Dateien ein, die das Leck
    getragen haben (Befund Gesamtanalyse 2026-05-27): sie filtern ueber
    _shared._cached_csv und mussten von is_released_corpus auf
    is_visible_corpus umgestellt werden. Der Test verteidigt diese
    Umstellung gezielt, falls der breite Test je verengt wird.
    """
    targets = ("roles.json", "relations.json", "transactions.json",
               "role_constellation.json", "timeline.json")
    markers = HIDDEN_SUBDIRS + HIDDEN_DOC_PATHS + HIDDEN_AGGREGATE_MARKERS
    offenders = []
    for name in targets:
        p = DOCS / "data" / name
        if not p.exists():
            pytest.skip(f"build artifact not found: data/{name}")
        txt = p.read_text(encoding="utf-8")
        hits = {m: txt.count(m) for m in markers if txt.count(m)}
        if hits:
            offenders.append(f"{name}: {hits}")
    assert not offenders, (
        f"Aggregate enthalten versteckte Korpora: {offenders}. "
        f"Ursache: _cached_csv filtert nicht auf is_visible_corpus."
    )


def test_no_hidden_corpus_document_dirs():
    if not DOCS.exists():
        pytest.skip("docs/ noch nicht gebaut")
    for sub in HIDDEN_SUBDIRS:
        assert not (DOCS / "documents" / sub).exists(), (
            f"Versteckte Sammlung {sub} wurde oeffentlich gerendert."
        )


def test_register_entities_all_have_a_source():
    for rel in ("data/persons_search.json", "data/orgs_search.json"):
        data = _load(rel)
        zero = [e["id"] for e in data if e.get("dc", 0) < 1]
        assert not zero, (
            f"{rel}: {len(zero)} Eintraege ohne Quelle, z.B. {zero[:3]}. "
            f"Eine Entitaet ohne Quelle darf in keiner Ansicht erscheinen."
        )


def test_register_search_only_public_corpora():
    for rel in ("data/persons_search.json", "data/orgs_search.json"):
        data = _load(rel)
        bad = [(e["id"], cp) for e in data for cp in e.get("co", [])
               if cp not in PUBLIC_CORPORA]
        assert not bad, (
            f"{rel}: Verweise auf nicht-oeffentliche Sammlungen, z.B. {bad[:3]}."
        )


def test_reverse_index_only_public_corpora():
    for rel in ("register/persons.json", "register/organisations.json"):
        data = _load(rel)
        bad = []
        for eid, sources in data.items():
            for s in sources:
                if any(h in s.get("u", "") for h in HIDDEN_DOC_PATHS):
                    bad.append((eid, s.get("u", "")))
                    break
        assert not bad, (
            f"{rel}: Quellen aus versteckten Sammlungen, z.B. {bad[:3]}."
        )


def test_profiles_have_no_hidden_corpus_links():
    """Kein Personen- oder Org-Profil verlinkt eine versteckte Quelle.

    Faengt das occ-Netzwerk-Leck (gelistete Orgs wie Kuttenberg) und
    verwaiste Alt-Profile (Teuffl-Fall) gleichermassen. Gelistete Personen-
    Profile koennen nicht lecken (ihre Beziehungen filtern auf sichtbare
    Quellen), darum reicht dort der Scan der nicht-gelisteten Dateien; das
    haelt den Test schnell statt ueber 8000 Dateien zu lesen.
    """
    if not (DOCS / "register").exists():
        pytest.skip("register/ noch nicht gebaut")
    offenders = []

    org_dir = DOCS / "register" / "orgs"
    if org_dir.exists():
        for f in org_dir.glob("*.html"):
            if any(h in f.read_text(encoding="utf-8") for h in HIDDEN_DOC_PATHS):
                offenders.append(f"orgs/{f.name}")

    persons = set(_load("register/persons.json"))
    pers_dir = DOCS / "register" / "persons"
    if pers_dir.exists():
        for f in pers_dir.glob("*.html"):
            if f.stem in persons:
                continue
            if any(h in f.read_text(encoding="utf-8") for h in HIDDEN_DOC_PATHS):
                offenders.append(f"persons/{f.name}")

    assert not offenders, (
        f"{len(offenders)} Profile verlinken versteckte Quellen, z.B. "
        f"{offenders[:3]}. Ursache meist verwaiste Alt-Datei oder eine "
        f"Beziehungs-Liste, die nicht auf sichtbare Sammlungen filtert."
    )
