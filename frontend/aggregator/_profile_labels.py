"""Display helpers for entity detail profiles.

Used by ``person_profiles`` and ``org_profiles`` to turn raw CSV values
into the UI shape consumed by the Jinja templates.

Mappings are conservative: only values present in the released CSVs get
a German label, unknown keys fall through unchanged so additions stay
visible instead of being silently bucketed.
"""

# Singular German display form (the label sits on one entity, not a class).
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

def label_org_type(value: str) -> str:
    """German display label for an org type; unknown keys fall through."""
    if not value:
        return ""
    return TYPE_LABEL_ORG.get(value, value.replace("_", " "))


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
    """Split a pipe-joined authority field into clean URLs, order preserved
    so editors control display order."""
    if not value:
        return []
    out = []
    for part in value.split("|"):
        url = part.strip()
        if url:
            out.append(url)
    return out
