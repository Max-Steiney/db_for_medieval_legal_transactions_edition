"""Display helpers for entity detail profiles.

Used by ``person_profiles``, ``org_profiles`` and ``place_profiles`` to
turn raw CSV values (typ-Labels, pipe-joined names/authorities) into the
UI-ready shape consumed by the Jinja templates.

The mappings are deliberately conservative — only the values that
actually occur in the released ``organisations.csv`` / ``places.csv``
get a German label. Everything else falls through unchanged so future
type-key additions remain visible (instead of being silently mapped to
the bucket label).
"""

# Org-types from organisations.csv:type. Underscore conventions and
# English/Latin labels get a German display form. Plural avoided since the
# label is used for a single entity (Wiener Buergerspital -> "Spital").
TYPE_LABEL_ORG = {
    "Stadt":                  "Stadt",
    "Markt":                  "Markt",
    "Dorf":                   "Dorf",
    "Herzogtum":              "Herzogtum",
    "Grafschaft":             "Grafschaft",
    "Herrschaft":             "Herrschaft",
    "Burg":                   "Burg",
    "Kloster_m":              "Kloster (Männerorden)",
    "Kloster_f":              "Kloster (Frauenorden)",
    "Kloster":                "Kloster",
    "Kirche_Kapelle":         "Kirche / Kapelle",
    "Pfarre":                 "Pfarre",
    "Dioezese_Erzdioezese":   "Diözese / Erzdiözese",
    "Spital_Siechenhaus":     "Spital / Siechenhaus",
    "Altar":                  "Altar",
    "Messe":                  "Messstiftung",
    "Bruderschaft_Zeche":     "Bruderschaft / Zeche",
    "Universitaet":           "Universität",
    "Burschaft_Kollegium":    "Burse / Kollegium",
    "Zunft":                  "Zunft",
    "Gericht":                "Gericht",
    "Amt":                    "Amt",
    "Familie":                "Familie",
    "Reich":                  "Reich",
    "Koenigreich":            "Königreich",
    "Land":                   "Land",
    "Stift":                  "Stift",
}

# Place-types from places.csv:type. Raw English DB keys map to German
# vocabulary used elsewhere in the UI (Quellenkorpus / Ortsregister).
TYPE_LABEL_PLACE = {
    "settlement": "Siedlung",
    "street":     "Straße",
    "immo":       "Immobilie",
    "region":     "Region",
    "river":      "Fluss",
    "bridge":     "Brücke",
    "gate":       "Tor",
    "tower":      "Turm",
    "land":       "Flur",
    "vineyard":   "Weingarten",
    "field":      "Feld",
    "garden":     "Garten",
    "mill":       "Mühle",
    "house":      "Haus",
    "court":      "Hof",
    "mountain":   "Berg",
    "valley":     "Tal",
    "lake":       "See",
}


def label_org_type(value: str) -> str:
    """Return the German display label for an org type, falling through
    on unknown keys with underscores stripped."""
    if not value:
        return ""
    return TYPE_LABEL_ORG.get(value, value.replace("_", " "))


def label_place_type(value: str) -> str:
    """Return the German display label for a place type, falling through
    on unknown keys lowercased + underscore-stripped."""
    if not value:
        return ""
    return TYPE_LABEL_PLACE.get(value, value.replace("_", " "))


def split_pipe_names(value: str) -> tuple[str, list[str]]:
    """Split a pipe-joined name field into (main, aliases).

    Used for ``name_reg`` values that pack alternative forms like
    ``"Anna Yrrensteigin Haus | Anna, Anna Yrrensteigins Enkelin, Haus"``
    into a single column. The first segment serves as the primary name,
    subsequent segments are shown as aliases. Whitespace-only segments
    are dropped.
    """
    if not value:
        return "", []
    parts = [p.strip() for p in value.split("|")]
    parts = [p for p in parts if p]
    if not parts:
        return "", []
    return parts[0], parts[1:]


def split_authorities(value: str) -> list[str]:
    """Split a pipe-joined authority field into a list of clean URLs.

    Empty segments and whitespace-only entries are dropped. The order is
    preserved so editors can control display order.
    """
    if not value:
        return []
    out = []
    for part in value.split("|"):
        url = part.strip()
        if url:
            out.append(url)
    return out


def geonames_id(url: str) -> str:
    """Extract the numeric GeoNames id from a geonames.org URL.

    Returns the empty string if the URL doesn't follow the
    ``www.geonames.org/<digits>/...`` shape.
    """
    if not url:
        return ""
    import re
    m = re.search(r"geonames\.org/(\d+)", url)
    return m.group(1) if m else ""
