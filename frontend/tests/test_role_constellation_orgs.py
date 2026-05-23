"""Test fuer die Organisations-Achse in role_constellation.json.

Diese Session hat das Konstellations-Aggregat um Organisationen
erweitert (events[].og[]-Block plus vocab.organisation und
vocab.org_type), damit die Abfrage Personen- und Org-Bedingungen
parallel filtern kann (Mail-Frage 4: Issuer-Recipient mit St. Agnes
auf der Himmelpforte).

Schluessel-Quellen:
- organisations.csv (id, name_reg, type)
- orgs_in_events.csv (event_key, org_key, event_role)

Erwartete Datenstruktur in events[].og[] (analog zu events[].p[]):
- g: org_key (entity-id)
- n: Anzeigename (name_reg)
- r: event_role (issuer|recipient|witness|other)
- tp: Org-Typ (Kloster_m, Pfarre, ...; ggf. leer)

Vokabular:
- vocab.organisation: Liste der haeufigsten Orgs als
  [{value, count}, ...] (gespeist aus name_reg und Vorkommen).
- vocab.org_type: Liste der vorhandenen Org-Typen.
"""

import json
from pathlib import Path

import pytest

DATA_PATH = (
    Path(__file__).parent.parent.parent / "docs" / "data" / "role_constellation.json"
)

VALID_ROLES = {"issuer", "recipient", "witness", "other"}


def _load():
    if not DATA_PATH.exists():
        pytest.skip("docs/data/role_constellation.json fehlt; bitte build laufen lassen")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def test_role_constellation_vocab_has_organisation():
    """vocab.organisation traegt die haeufigsten Org-Namen als {value, count}."""
    data = _load()
    vocab = data.get("vocab", {})
    assert "organisation" in vocab, (
        "vocab.organisation fehlt. Erwartet: Liste der haeufigsten "
        "Org-Namen aus organisations.csv (name_reg), zusammen mit ihrer "
        "Vorkommens-Zahl im Korpus."
    )
    items = vocab["organisation"]
    assert isinstance(items, list) and items, "vocab.organisation ist leer"
    for it in items[:5]:
        assert isinstance(it, dict) and "value" in it and "count" in it, (
            f"Vokabel-Eintrag muss {{value, count}} sein, gefunden: {it!r}"
        )
        assert isinstance(it["value"], str) and it["value"].strip()
        assert isinstance(it["count"], int) and it["count"] > 0


def test_role_constellation_vocab_has_org_type():
    """vocab.org_type listet die vorhandenen Org-Typen."""
    data = _load()
    vocab = data.get("vocab", {})
    assert "org_type" in vocab, (
        "vocab.org_type fehlt. Erwartet: sortierte Liste der "
        "tatsaechlich vorkommenden Org-Typen (z. B. Kloster_m, Pfarre)."
    )
    types = vocab["org_type"]
    assert isinstance(types, list) and types, "vocab.org_type ist leer"
    for t in types:
        assert isinstance(t, str) and t.strip()


def test_role_constellation_events_carry_og_block():
    """Mindestens ein Event hat einen og[]-Block mit den vier Pflichtfeldern.

    Nicht jedes Event hat Org-Beteiligte; aber die Aggregat-Struktur
    muss ihn vorsehen. Wenn keiner gefunden wird, ist die Erweiterung
    entweder nicht gelaufen oder im Aggregator gedroppt.
    """
    data = _load()
    events = data.get("events", [])
    assert events, "events[] ist leer"
    found_og = False
    for ev in events:
        og = ev.get("og")
        if not og:
            continue
        found_og = True
        for o in og:
            for key in ("g", "n", "r", "tp"):
                assert key in o, (
                    f"og-Eintrag {o!r} in Event {ev.get('e')!r} muss "
                    f"Schluessel {key!r} tragen."
                )
            assert isinstance(o["g"], str) and o["g"].strip()
            assert isinstance(o["n"], str)
            assert o["r"] in VALID_ROLES, (
                f"og.r muss in {VALID_ROLES} sein, gefunden: {o['r']!r}"
            )
            assert isinstance(o["tp"], str)
        # Eine Validierungsrunde reicht; iteriere weiter nur falls noch
        # nichts gefunden wurde, sonst Abbruch.
        break
    assert found_og, (
        "Kein Event mit og[]-Block gefunden. Pruefen: "
        "frontend/aggregator/role_constellation.py liest "
        "orgs_in_events.csv und schreibt events[].og[]."
    )


def test_role_constellation_org_known_target_is_present():
    """Bekannte Ziel-Orgs der Forschungsfragen sind im Aggregat enthalten.

    St. Agnes auf der Himmelpforte (Frage 4) muss in mindestens einem
    Event als Beteiligte auftauchen, sonst kann die Mail-Frage im
    Abfrage-Interface nicht beantwortet werden.
    """
    data = _load()
    target = "org__wien-st_agnes_auf_der_himmelpforte"
    hits = 0
    for ev in data.get("events", []):
        for o in (ev.get("og") or []):
            if o.get("g") == target:
                hits += 1
                break
    assert hits > 0, (
        f"Ziel-Org {target!r} ist in keinem Event verzeichnet. "
        "Pruefen: orgs_in_events.csv enthaelt die Org-ID, und der "
        "Aggregator filtert sie nicht weg."
    )
