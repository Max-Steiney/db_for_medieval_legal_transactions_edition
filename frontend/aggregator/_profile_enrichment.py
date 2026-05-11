"""Per-doc enrichment for entity detail profiles.

Each profile carries a chronologically sorted ``sources`` list (built by
``build/__init__.py`` from ``reverse_index``). The detail-page tables
need two more columns:

* ``label`` — how the entity is named in *this particular* source
* ``role``  — what event-role the entity plays in *this particular* source

Both come from per-source CSVs that key by ``(entity_key, file_key)``,
so we build that map here once per build and re-use it for all three
entity types.

The (collection_path, idno) -> file_key bridge mirrors the reverse one
already present in each profile aggregator.
"""

from collections import Counter, defaultdict

from ._shared import _cached_csv


# Role label maps. Persons / orgs share the same event-role vocabulary
# (issuer / recipient / witness / other). Places use a different set of
# event-roles (where / of / transactiongood_I / transactiongood_II).
ROLE_LABEL_PERSON = {
    "issuer":    "Aussteller*in",
    "recipient": "Empfänger*in",
    "witness":   "Zeuge / Siegler*in",
    "other":     "Sonstige",
}

ROLE_LABEL_ORG = ROLE_LABEL_PERSON

ROLE_LABEL_PLACE = {
    "where":             "Handlungsort",
    "of":                "Bezugsort",
    "transactiongood_I": "Transaktionsgut",
    "transactiongood_II": "Transaktionsgut (II)",
}


def file_key_lookup() -> dict[tuple[str, str], str]:
    """(collection_path, idno) -> file_key.

    Inverse of the lookup each profile aggregator builds internally.
    Used to bridge from ``reverse_index`` doc-entries to the file_key
    that the per-source / per-event CSVs key on.
    """
    out = {}
    for r in _cached_csv("filenames.csv"):
        fk = r.get("id", "")
        fname = r.get("file", "")
        coll = r.get("collection", "")
        sub = r.get("subcollection", "")
        if not fk or not fname or not coll or not sub:
            continue
        idno = fname[:-4] if fname.endswith(".xml") else fname
        out[(f"{coll}/{sub}", idno)] = fk
    return out


def _per_doc_label(csv_name: str, key_col: str,
                   label_cols: tuple[str, ...]) -> dict[tuple[str, str], str]:
    """(entity_key, file_key) -> most-frequent label in that source.

    A single source can mention an entity several times with different
    labels (e.g. ``Ritter|hern``). We keep the most frequent one and let
    the source-label chips upstairs carry the full breadth.
    """
    counters: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in _cached_csv(csv_name):
        ek = (r.get(key_col) or "").strip()
        fk = (r.get("file_key") or "").strip()
        if not ek or not fk:
            continue
        for col in label_cols:
            v = (r.get(col) or "").strip()
            if v:
                counters[(ek, fk)][v] += 1
    return {k: c.most_common(1)[0][0] for k, c in counters.items() if c}


def per_doc_label_persons() -> dict[tuple[str, str], str]:
    """Top-1 label per (person_key, file_key)."""
    return _per_doc_label("persons_in_sources.csv", "person_key",
                          ("source_titles", "source_prof"))


def per_doc_label_orgs() -> dict[tuple[str, str], str]:
    """Top-1 label per (org_key, file_key)."""
    return _per_doc_label("orgs_in_sources.csv", "org_key", ("source_text",))


def per_doc_label_places() -> dict[tuple[str, str], str]:
    """Top-1 label per (place_key, file_key)."""
    return _per_doc_label("places_in_sources.csv", "place_key", ("source_text",))


def _per_doc_roles(csv_name: str, key_col: str) -> dict[tuple[str, str], list[str]]:
    """(entity_key, file_key) -> ordered list of distinct event_roles.

    An entity can appear in several events within one source (typical
    QGW shape: one abstract event + one seal event), each with its own
    role. The order is by first occurrence, deduplicated.
    """
    out: dict[tuple[str, str], list[str]] = defaultdict(list)
    seen: dict[tuple[str, str], set] = defaultdict(set)
    for r in _cached_csv(csv_name):
        ek = (r.get(key_col) or "").strip()
        fk = (r.get("file_key") or "").strip()
        role = (r.get("event_role") or "").strip()
        if not ek or not fk or not role:
            continue
        key = (ek, fk)
        if role in seen[key]:
            continue
        seen[key].add(role)
        out[key].append(role)
    return dict(out)


def per_doc_roles_persons() -> dict[tuple[str, str], list[str]]:
    return _per_doc_roles("persons_in_events.csv", "person_key")


def per_doc_roles_orgs() -> dict[tuple[str, str], list[str]]:
    return _per_doc_roles("orgs_in_events.csv", "org_key")


def per_doc_roles_places() -> dict[tuple[str, str], list[str]]:
    return _per_doc_roles("places_in_events.csv", "place_key")


def enrich_sources(sources: list[dict], entity_key: str,
                   fk_lookup: dict[tuple[str, str], str],
                   label_map: dict[tuple[str, str], str],
                   role_map: dict[tuple[str, str], list[str]],
                   role_labels: dict[str, str]) -> list[dict]:
    """Return a new list with ``label`` and ``roles`` added per source.

    ``roles`` is a list of dicts ``[{"key": "issuer", "label":
    "Aussteller*in"}]`` so the template can style each chip independently.
    The original entries from ``reverse_index`` are preserved verbatim.
    """
    out = []
    for d in sources:
        cp = d.get("collection_path", "")
        idno = d.get("idno", "")
        fk = fk_lookup.get((cp, idno), "")
        enriched = dict(d)
        enriched["label"] = label_map.get((entity_key, fk), "") if fk else ""
        role_keys = role_map.get((entity_key, fk), []) if fk else []
        enriched["roles"] = [
            {"key": rk, "label": role_labels.get(rk, rk)} for rk in role_keys
        ]
        out.append(enriched)
    return out
