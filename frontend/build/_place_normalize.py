"""Kanonisierung von Freitext-Ortsnamen aus TEI-Quellen.

Die TEI-Quellen tragen den Datums-Ort als Freitext in
``profileDesc/creation/placeName``, mit Schreibvarianten wie
"Wiener-Neustadt" gegen "Wiener Neustadt" oder "Sankt Pölten" gegen
"St. Pölten". Ohne Kanonisierung erscheinen diese Varianten im
Place-Filter als getrennte Buckets.

Strategie ohne TEI-Eingriff:

1. ``normalize_place_key`` baut einen Vergleichs-Schluessel aus dem
   Freitext (Bindestrich zu Leerzeichen, Whitespace kollabiert,
   Casefold).
2. ``build_canonical_index`` liest ``places.csv`` aus dem
   Schwester-Repo plus ``content/place_aliases.json`` und baut eine
   Map ``normalisierter_schluessel -> Anzeigename``.
3. ``canonical_place_name`` schlaegt den normalisierten Schluessel in
   der Map nach. Treffer liefern den kanonischen Namen; Fehlschlag
   liefert den Freitext unveraendert zurueck.

Die Lookup-Map wird einmal pro Build aufgebaut. Mehrdeutigkeiten
(zwei Place-Eintraege mit normalisiert gleichem Schluessel) sind
hier nicht aufloesbar; ein Build-Test in ``frontend/tests`` prueft
diese Eindeutigkeit und blockiert den Build im Konfliktfall.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_place_key(text: str) -> str:
    """Vergleichs-Schluessel fuer einen Ortsnamen.

    Bindestrich, Slash und Punkt werden zu Leerzeichen. Mehrfache
    Whitespaces fallen auf ein einzelnes Leerzeichen zusammen.
    Casefold macht den Schluessel case-insensitiv.
    """
    if not text:
        return ""
    cleaned = re.sub(r"[\-\./]", " ", text)
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned.casefold()


def _load_places_csv(places_csv_path: Path) -> list[dict]:
    """``places.csv`` als Zeilen-Liste lesen; leere Datei toleriert."""
    if not places_csv_path.exists():
        return []
    with places_csv_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        return list(reader)


def _load_aliases(aliases_path: Path) -> dict[str, str]:
    """JSON-Map ``Alias-Schreibung -> kanonischer Name``."""
    if not aliases_path.exists():
        return {}
    return json.loads(aliases_path.read_text(encoding="utf-8"))


def build_canonical_index(
    places_csv_path: Path,
    aliases_path: Path,
) -> dict[str, str]:
    """Lookup-Map ``normalisierter Schluessel -> Anzeigename`` bauen.

    Reihenfolge der Quellen: ``places.csv`` zuerst, dann Aliase. Aliase
    koennen also Auflosungen aus ``places.csv`` ueberschreiben (z.B.
    wenn eine historische Schreibung explizit auf einen anderen
    Anzeigenamen zeigen soll).

    Mehrdeutigkeiten innerhalb ``places.csv`` (zwei Eintraege mit
    normalisiert gleichem Schluessel) werden hier still uebernommen;
    Schutz dagegen ist Aufgabe des Build-Tests, der die Eindeutigkeit
    der Map prueft.
    """
    index: dict[str, str] = {}

    for row in _load_places_csv(places_csv_path):
        # Nur settlement-Typen sind relevant fuer den Datums-Ort einer
        # Urkunde. immo/street/river sind Liegenschaften/Strassen/Fluesse
        # und gehoeren nicht in den Place-Filter.
        if (row.get("type") or "").strip() != "settlement":
            continue
        name = (row.get("name_reg") or row.get("id") or "").strip()
        if not name:
            continue
        key = normalize_place_key(name)
        if key and key not in index:
            index[key] = name

    for raw, canonical in _load_aliases(aliases_path).items():
        if raw.startswith("_"):
            continue  # Schema- oder Doku-Keys ueberspringen
        key = normalize_place_key(raw)
        if key:
            index[key] = canonical

    return index


def canonical_place_name(text: str, index: dict[str, str]) -> str:
    """Den Freitext gegen die Lookup-Map auflosen.

    Treffer liefert den kanonischen Anzeigenamen aus der Map.
    Kein Treffer liefert den Freitext unveraendert zurueck, damit
    unbekannte Orte weiterhin im Filter sichtbar bleiben.
    """
    if not text:
        return text
    key = normalize_place_key(text)
    return index.get(key, text)


def detect_collisions(places_csv_path: Path) -> list[tuple[str, list[str]]]:
    """Schluessel mit mehrfacher Auflosung in ``places.csv`` finden.

    Rueckgabe: Liste von ``(normalisierter_schluessel, [Name1, Name2, ...])``
    fuer alle Konflikte. Leer, wenn die Map eindeutig ist.

    Dedup auf den Anzeigenamen vor dem Konflikt-Test: identische
    name_reg-Werte unter unterschiedlichen Place-IDs (z.B. zwei
    Eintraege fuer denselben Bezirk) sind kein Auflosungs-Konflikt,
    weil der Lookup denselben Display-Namen liefern wuerde.
    """
    buckets: dict[str, set[str]] = {}
    for row in _load_places_csv(places_csv_path):
        if (row.get("type") or "").strip() != "settlement":
            continue
        name = (row.get("name_reg") or row.get("id") or "").strip()
        if not name:
            continue
        key = normalize_place_key(name)
        if not key:
            continue
        buckets.setdefault(key, set()).add(name)
    return [(k, sorted(names)) for k, names in buckets.items() if len(names) > 1]
