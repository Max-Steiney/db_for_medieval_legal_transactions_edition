"""Epic D: Ortsregister mit Georeferenzierungs-Status — exploration/places.html."""

from collections import Counter, defaultdict
from pathlib import Path

from ._shared import _cached_csv, _meta, _parse_coord, _decade, _write_json


def aggregate_epic_d(docs_data_dir: Path, reverse_index: dict | None = None) -> dict:
    """Aggregate place data with reference and georeferencing status.

    Enhanced for Place Explorer (Option B): adds per-place document counts
    and file_keys for settlements with coordinates (map drill-down).
    """
    places_rows = _cached_csv("places.csv")
    pis_rows = _cached_csv("places_in_sources.csv")
    pie_rows = _cached_csv("places_in_events.csv")
    eis_rows = _cached_csv("events_in_sources.csv")

    # Build place_key -> set(file_key) lookup from places_in_sources
    place_file_keys: dict[str, set] = defaultdict(set)
    for r in pis_rows:
        pk = r.get("place_key", "")
        fk = r.get("file_key", "")
        if pk and fk:
            place_file_keys[pk].add(fk)

    # Build event_key -> decade lookup for temporal dimension
    event_decade: dict[str, int | None] = {}
    for r in eis_rows:
        ek = r.get("event_key", "")
        dec = _decade(r.get("date_not_before", ""))
        if dec is None:
            dec = _decade(r.get("date_not_after", ""))
        event_decade[ek] = dec

    # Build place_key -> set(decade) from places_in_events
    place_decades: dict[str, set] = defaultdict(set)
    for r in pie_rows:
        pk = r.get("place_key", "")
        ek = r.get("event_key", "")
        dec = event_decade.get(ek)
        if pk and dec is not None:
            place_decades[pk].add(dec)

    # Places referenced in sources
    referenced_keys = set(place_file_keys.keys())

    # Also check reverse_index if available
    if reverse_index:
        for eid in reverse_index:
            if eid.startswith("pl__"):
                referenced_keys.add(eid)

    # Type counts for coverage
    type_counts: Counter = Counter()

    places = []
    for r in places_rows:
        pid = r.get("id", "")
        lat = r.get("lat", "").strip()
        lng = r.get("lng", "").strip()
        geonames = r.get("geonames", "").strip()
        ptype = r.get("type", "")

        # Parse coordinates, handling comma decimals and text suffixes
        lat_f = _parse_coord(lat) if lat else None
        lng_f = _parse_coord(lng) if lng else None
        has_coords = lat_f is not None and lng_f is not None
        has_geonames = bool(geonames)

        type_counts[ptype] += 1

        doc_count = len(place_file_keys.get(pid, set()))
        decades = sorted(place_decades.get(pid, set()))
        entry = {
            "id": pid,
            "name": r.get("name_reg", ""),
            "type": ptype,
            "lat": lat_f,
            "lng": lng_f,
            "geonames": geonames if has_geonames else None,
            "referenced": pid in referenced_keys,
            "has_coords": has_coords,
            "has_geonames": has_geonames,
            "doc_count": doc_count,
            "decades": decades,
        }

        # Provenance: include file_keys for every referenced place so that
        # any aggregated number involving places can be traced back to its
        # source documents. Zero-referenced places omit the key to keep
        # unused entries small.
        if doc_count > 0:
            entry["file_keys"] = sorted(place_file_keys[pid])

        places.append(entry)

    referenced_count = sum(1 for p in places if p["referenced"])
    with_coords = sum(1 for p in places if p["has_coords"])
    with_geonames = sum(1 for p in places if p["has_geonames"])
    settlements_with_coords = sum(
        1 for p in places if p["type"] == "settlement" and p["has_coords"]
    )
    total_doc_links = sum(p["doc_count"] for p in places)

    raw_with_latlng = sum(1 for r in places_rows
                          if r.get("lat", "").strip() and r.get("lng", "").strip())

    result = {
        "meta": _meta(
            description="Place register with reference and georeferencing status",
            sources=["places.csv", "places_in_sources.csv"],
            dimensions=[
                {"name": "place", "type": "entity", "id_prefix": "pl__"},
                {"name": "place_type", "type": "categorical",
                 "description": "Register type classification"},
                {"name": "reference_status", "type": "boolean",
                 "description": "Whether place is referenced from source documents"},
                {"name": "georef_status", "type": "categorical",
                 "values": ["coords", "geonames", "both", "none"]},
            ],
            measures=[
                {"name": "count", "type": "integer",
                 "description": "Number of place entries"},
                {"name": "doc_count", "type": "integer",
                 "description": "Number of source documents referencing this place"},
            ],
        ),
        "places": places,
        "coverage": {
            "total": len(places),
            "referenced": referenced_count,
            "unreferenced": len(places) - referenced_count,
            "with_coords": with_coords,
            "with_geonames": with_geonames,
            "settlements_with_coords": settlements_with_coords,
            "total_doc_links": total_doc_links,
            "type_counts": dict(type_counts),
            "coord_parse_failures": raw_with_latlng - with_coords,
        },
    }

    _write_json(result, docs_data_dir / "epic_d.json")
    return result


# ---------------------------------------------------------------------------
# Document lookup for drill-down (V1 shared component)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Per-source aggregate (docs_aggregate.json)
# ---------------------------------------------------------------------------

