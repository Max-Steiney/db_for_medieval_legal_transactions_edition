"""Forschungsfrage-spezifische Aggregatoren.

Zwei Operationalisierungen:

1. ``build_uhlirz_iv_marriages``  -- Personen mit Beruf in Uhlirz-Kategorie IV,
   die in einer Kin-Beziehung mit einem Heirats-Term zu einer anderen Person
   stehen.
2. ``build_uhlirz_vi_ownership``  -- Personen mit Beruf in Uhlirz-Kategorie VI,
   die als Hausbesitzer in ``owner_relations_in_sources.csv`` auftreten.

Beide Funktionen liefern eine kompakte JSON-faehige Struktur ohne in
``docs/data/`` zu schreiben.  Sie sind als Daten-Backend fuer
Visualisierungen gedacht und werden separat in die Build-Pipeline
eingebunden.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from pipeline.config import INDICES_DIR, NORM_LISTS_DIR, TEI_NS, XML_NS

from frontend.aggregator._shared import (
    _cached_csv,
    _parse_coord,
    _released_file_keys,
)


# Heirats-Match-Liste (case-insensitive, ganzes Wort).
# Generische "mann" / "frau" bewusst weggelassen: zu viele False Positives.
MARRIAGE_TERMS: set[str] = {
    "gemahl",
    "gemahlin",
    "gemahles",
    "gemahls",
    "gatte",
    "gattin",
    "hausfrau",
    "hausfrauen",
    "ehemann",
    "ehefrau",
    "ehe",
    "ehe|frau",
}


def _normalise_term(value: str) -> str:
    """Lower-case und Whitespace-Trim fuer Vergleichszwecke."""
    return (value or "").strip().lower()


def _contains_marriage_term(kin: str) -> bool:
    """True, wenn ``kin`` einen Heirats-Term als ganzes Wort enthaelt.

    Pipe-Charaktere und Slashes werden wie Whitespace behandelt, damit
    Mehrfach-Eintraege (z. B. ``Gemahlin | Hausfrau``) sauber tokenisiert
    werden.
    """
    if not kin:
        return False
    normalised = _normalise_term(kin)
    # ``ehe|frau`` als Original-Form behalten: zuerst direkte Substring-Pruefung
    if "ehe|frau" in normalised:
        return True
    # Tokenisierung auf nicht-Buchstaben-Zeichen. ``hausvrowe`` matched so
    # nicht versehentlich, ``Gemahl`` aber schon.
    tokens = re.split(r"[\W_]+", normalised, flags=re.UNICODE)
    for token in tokens:
        if token in MARRIAGE_TERMS:
            return True
    return False


# ---------------------------------------------------------------------------
# Uhlirz-Kategorien aus roleName_norm_matching.csv
# ---------------------------------------------------------------------------


def _load_uhlirz_index() -> dict[str, str]:
    """Mapping ``source_prof_spelling -> Uhlirz-Kategorie`` (case-sensitive).

    TAB-delimited; nur Zeilen mit nicht leerer ``Gewerbe_nach_Uhlirz_GstW``.
    Wenn dieselbe Schreibweise mehrere Kategorien hat (selten), gewinnt der
    erste Treffer.
    """
    path = NORM_LISTS_DIR / "roleName_norm_matching.csv"
    result: dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            spelling = (row.get("roleName_spelling") or "").strip()
            cat = (row.get("Gewerbe_nach_Uhlirz_GstW") or "").strip()
            if spelling and cat and spelling not in result:
                result[spelling] = cat
    return result


def _persons_by_category(category_prefix: str) -> tuple[dict[str, str], str]:
    """Sammelt ``person_key -> source_prof`` fuer Personen mit Beruf in der
    gewuenschten Uhlirz-Kategorie (Match ueber Praefix, z. B. ``"IV "``).

    Rueckgabe: ``(persons, category_label)``.  ``category_label`` ist der
    erste in den Daten gefundene vollstaendige Kategorie-String (z. B.
    ``"IV Bekleidungsindustrie"``); leer, wenn nichts matched.
    """
    uhlirz = _load_uhlirz_index()
    persons: dict[str, str] = {}
    category_label = ""
    rows = _cached_csv("persons_in_sources.csv")
    for row in rows:
        prof = (row.get("source_prof") or "").strip()
        pkey = (row.get("person_key") or "").strip()
        if not prof or not pkey:
            continue
        cat = uhlirz.get(prof)
        if not cat or not cat.startswith(category_prefix):
            continue
        if not category_label:
            category_label = cat
        # Falls dieselbe Person mehrere Eintraege hat, ersten Beruf behalten.
        persons.setdefault(pkey, prof)
    return persons, category_label


# ---------------------------------------------------------------------------
# Personen-Namen-Index (aus persons.csv)
# ---------------------------------------------------------------------------


def _person_name_index() -> dict[str, str]:
    """``person_id -> Anzeigename`` aus ``persons.csv``."""
    out: dict[str, str] = {}
    for row in _cached_csv("persons.csv"):
        pid = (row.get("id") or "").strip()
        if not pid:
            continue
        parts = [
            (row.get("forename_reg") or "").strip(),
            (row.get("surname_reg") or "").strip(),
            (row.get("addname_reg") or "").strip(),
        ]
        name = " ".join(p for p in parts if p)
        out[pid] = name or pid
    return out


# ---------------------------------------------------------------------------
# Forschungsfrage 1: Uhlirz IV + Heirat
# ---------------------------------------------------------------------------


def build_uhlirz_iv_marriages() -> dict:
    """Personen mit Beruf in Uhlirz-Kategorie IV plus Heirats-Beziehung."""
    iv_persons, category_label = _persons_by_category("IV ")
    names = _person_name_index()
    kin_rows = _cached_csv("kin_relations_in_sources.csv")

    # Personen ausserhalb Kategorie IV: trotzdem deren Beruf bereitstellen,
    # falls vorhanden -- damit ``occ_in_iv`` korrekt gesetzt werden kann.
    other_profs: dict[str, str] = {}
    for row in _cached_csv("persons_in_sources.csv"):
        pkey = (row.get("person_key") or "").strip()
        prof = (row.get("source_prof") or "").strip()
        if pkey and prof and pkey not in iv_persons:
            other_profs.setdefault(pkey, prof)

    # Mehrere Erwaehnungen derselben (a, b)-Konstellation bundeln.
    # ``a`` ist die IV-Person (mit Beruf), ``b`` der Ehe-Partner.  Die kin-
    # Beziehung ist in der Quelle meist asymmetrisch (z. B. ``pe_a -> "Hausfrau"
    # -> pe_b`` heisst: pe_a ist die Hausfrau von pe_b).  Wir akzeptieren
    # darum beide Richtungen und drehen die Rollen so, dass ``a`` immer der
    # Beruf-Traeger ist.
    pair_buckets: dict[tuple[str, str], dict] = {}
    for row in kin_rows:
        kin = row.get("kin") or ""
        if not _contains_marriage_term(kin):
            continue
        person_key = (row.get("person_key") or "").strip()
        related_key = (row.get("related_key") or "").strip()
        file_key = (row.get("file_key") or "").strip()
        if not person_key or not related_key:
            continue
        if person_key in iv_persons:
            a_key, b_key = person_key, related_key
        elif related_key in iv_persons:
            a_key, b_key = related_key, person_key
        else:
            continue
        bucket_key = (a_key, b_key)
        bucket = pair_buckets.get(bucket_key)
        if bucket is None:
            bucket = {
                "a": {
                    "id": a_key,
                    "name": names.get(a_key, a_key),
                    "occ": iv_persons[a_key],
                },
                "b": {
                    "id": b_key,
                    "name": names.get(b_key, b_key),
                    "occ_in_iv": b_key in iv_persons,
                },
                "kin_term": kin.strip(),
                "files": [],
            }
            pair_buckets[bucket_key] = bucket
        if file_key and file_key not in bucket["files"]:
            bucket["files"].append(file_key)

    pairs = list(pair_buckets.values())
    pairs.sort(key=lambda p: (p["a"]["name"].lower(), p["b"]["name"].lower()))

    return {
        "meta": {
            "category": category_label or "IV",
            "match_terms": sorted(MARRIAGE_TERMS),
        },
        "pairs": pairs,
        "total": len(pairs),
    }


# ---------------------------------------------------------------------------
# Forschungsfrage 2: Uhlirz VI + Hausbesitz
# ---------------------------------------------------------------------------


def _place_coordinates_from_index() -> dict[str, tuple[float | None, float | None]]:
    """``place_id -> (lat, lon)`` aus ``indices/placeList.xml``.

    Liest ``//tei:place/tei:location/tei:geo`` ("lat lon"). Beide Werte
    koennen ``None`` sein, wenn das Element fehlt oder unparsbar ist.
    """
    path = INDICES_DIR / "placeList.xml"
    coords: dict[str, tuple[float | None, float | None]] = {}
    try:
        tree = ET.parse(path)
    except (ET.ParseError, FileNotFoundError):
        return coords
    ns = {"tei": TEI_NS, "xml": XML_NS}
    xml_id_attr = f"{{{XML_NS}}}id"
    for place in tree.iter(f"{{{TEI_NS}}}place"):
        pid = place.get(xml_id_attr)
        if not pid:
            continue
        geo = place.find("tei:location/tei:geo", ns)
        if geo is None or not (geo.text or "").strip():
            coords[pid] = (None, None)
            continue
        parts = (geo.text or "").split()
        lat = _parse_coord(parts[0]) if parts else None
        lon = _parse_coord(parts[1]) if len(parts) > 1 else None
        coords[pid] = (lat, lon)
    return coords


def _place_name_index() -> dict[str, str]:
    """``place_id -> Anzeigename`` aus ``places.csv``."""
    out: dict[str, str] = {}
    for row in _cached_csv("places.csv"):
        pid = (row.get("id") or "").strip()
        if not pid:
            continue
        name = (
            (row.get("name_reg") or "").strip()
            or (row.get("name_orig") or "").strip()
            or pid
        )
        out[pid] = name
    return out


def build_uhlirz_vi_ownership() -> dict:
    """Personen mit Beruf in Uhlirz-Kategorie VI plus Hausbesitz."""
    vi_persons, category_label = _persons_by_category("VI ")
    names = _person_name_index()
    place_names = _place_name_index()
    coords = _place_coordinates_from_index()
    released = _released_file_keys()

    # owner_relations_in_sources.csv hat ``xml_key`` (nicht ``file_key``) und
    # wird darum nicht durch ``_cached_csv`` released-gefiltert. Manuell filtern.
    rows = _cached_csv("owner_relations_in_sources.csv")

    ownerships_by_pair: dict[tuple[str, str], dict] = {}
    for row in rows:
        xml_key = (row.get("xml_key") or "").strip()
        if released and xml_key not in released:
            continue
        person_id = (row.get("rel_key") or "").strip()
        place_id = (row.get("place_key") or "").strip()
        if not person_id or not place_id:
            continue
        if person_id not in vi_persons:
            continue
        bucket_key = (person_id, place_id)
        bucket = ownerships_by_pair.get(bucket_key)
        if bucket is None:
            lat, lon = coords.get(place_id, (None, None))
            bucket = {
                "person": {
                    "id": person_id,
                    "name": names.get(person_id, person_id),
                    "occ": vi_persons[person_id],
                },
                "place": {
                    "id": place_id,
                    "name": place_names.get(place_id, place_id),
                    "lat": lat,
                    "lon": lon,
                },
                "files": [],
            }
            ownerships_by_pair[bucket_key] = bucket
        if xml_key and xml_key not in bucket["files"]:
            bucket["files"].append(xml_key)

    ownerships = list(ownerships_by_pair.values())
    ownerships.sort(
        key=lambda o: (o["person"]["name"].lower(), o["place"]["name"].lower())
    )
    with_coords = sum(
        1
        for o in ownerships
        if o["place"]["lat"] is not None and o["place"]["lon"] is not None
    )

    return {
        "meta": {"category": category_label or "VI"},
        "ownerships": ownerships,
        "total": len(ownerships),
        "with_coords": with_coords,
    }


# ---------------------------------------------------------------------------
# Smoke-Test
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    iv = build_uhlirz_iv_marriages()
    print(f"Uhlirz IV Heiratspaare: {iv['total']}")
    vi = build_uhlirz_vi_ownership()
    print(f"Uhlirz VI Hausbesitz: {vi['total']} ({vi['with_coords']} mit Koordinaten)")
