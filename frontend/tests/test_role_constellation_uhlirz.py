"""Test fuer die Uhlirz-Achse in role_constellation.json.

Mail-Frage 1 aus der Korrespondenz vom 16. Mai 2026 fragt nach
Heiratsbeziehungen innerhalb der Uhlirz-Kategorie IV (Erzeugung und
Vertrieb von Leuchtstoffen, Fetten und Oelen). Damit das im Frontend
beantwortbar wird, muss die Konstellations-Abfrage nach Uhlirz-
Kategorie filterbar sein. Das setzt voraus, dass die Aggregat-JSON
fuer jede Person die zugehoerigen Uhlirz-Kategorien mitfuehrt.

Datenbasis: `normalisation_lists/roleName_norm_matching.csv` im
Pipeline-Repo, Spalte `Gewerbe_nach_Uhlirz_GstW`. Schluessel ist die
Originalschreibung des Berufs (`roleName_spelling_norm`), wie sie auch
heute schon in `events[].p[].o[]` von role_constellation.json steht.

Erwartete Datenstruktur in `events[].p[]` (additiv):
- `o`: bestehend, Liste der Original-Berufsstrings.
- `u`: neu, Liste der Uhlirz-Kategorien, in die irgendeiner der
  o-Strings faellt. Kann leer sein, wenn keiner gemappt ist.

Auf Vokabular-Ebene erwartet das Frontend in `vocab.uhlirz` eine
sortierte Liste aller im Korpus tatsaechlich belegten Kategorien.
"""

import json
from pathlib import Path

import pytest

DATA_PATH = (
    Path(__file__).parent.parent.parent / "docs" / "data" / "role_constellation.json"
)


def _load():
    if not DATA_PATH.exists():
        pytest.skip("docs/data/role_constellation.json fehlt; bitte build laufen lassen")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_role_constellation_vocab_has_uhlirz():
    """vocab.uhlirz traegt die Liste der im Korpus belegten Kategorien."""
    data = _load()
    vocab = data.get("vocab", {})
    assert "uhlirz" in vocab, (
        "vocab.uhlirz fehlt. Erwartet: Liste der im Korpus belegten "
        "Uhlirz-Kategorien, gespeist aus normalisation_lists/"
        "roleName_norm_matching.csv Spalte Gewerbe_nach_Uhlirz_GstW."
    )
    uhlirz = vocab["uhlirz"]
    assert isinstance(uhlirz, list)
    assert len(uhlirz) > 0, "vocab.uhlirz ist leer"
    # Alle Eintraege Strings, beginnen mit roemischer Ziffer (I, II, IV, ...).
    for cat in uhlirz:
        assert isinstance(cat, str)
        assert cat[0] in "IVX", f"Uhlirz-Kategorie sieht nicht nach 'I/II/...' aus: {cat!r}"


def test_role_constellation_participants_have_uhlirz_field():
    """Jede Person in events[].p[] hat ein u-Feld (Uhlirz-Kategorien, ggf. leer)."""
    data = _load()
    events = data.get("events", [])
    assert events, "events[] ist leer"
    # Stichprobe: erste 20 Events
    for ev in events[:20]:
        for p in ev.get("p", []):
            assert "u" in p, (
                f"Person {p.get('p')!r} in Event {ev.get('e')!r} hat kein "
                "u-Feld. Aggregator muss role_constellation.events[].p[] "
                "additiv um u-Liste erweitern."
            )
            assert isinstance(p["u"], list)


def test_role_constellation_uhlirz_mapping_active():
    """Mehrere Uhlirz-Kategorien muessen Personen zugeordnet haben.

    Das Mapping greift, wenn mindestens fuenf Kategorien Personen
    tragen. Die genaue Zahl pro Kategorie haengt vom freigegebenen
    Korpus ab und aendert sich mit jedem Pipeline-Lauf; deshalb wird
    nicht pro Kategorie geprueft, sondern die Mapping-Wirksamkeit als
    ganzes.

    Hintergrund: ohne dieses Mapping (case-insensitiv ueber
    roleName_spelling) waere die u-Liste der Personen leer und Mail-
    Frage 1 (Heirat innerhalb Uhlirz IV) im UI nicht erschliessbar.
    """
    data = _load()
    cats_with_persons: dict[str, int] = {}
    for ev in data.get("events", []):
        for p in ev.get("p", []):
            for u in p.get("u", []):
                cats_with_persons[u] = cats_with_persons.get(u, 0) + 1
    assert len(cats_with_persons) >= 5, (
        f"Nur {len(cats_with_persons)} Uhlirz-Kategorien haben Personen, "
        "erwartet mindestens 5. Pruefen: case-insensitiv-Lookup in "
        "frontend/aggregator/role_constellation.py."
    )
