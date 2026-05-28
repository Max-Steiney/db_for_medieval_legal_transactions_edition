"""Zentrales Mapping fuer Funktionsrollen-Labels.

Single-source-of-truth fuer die deutschen Anzeigewerte des TEI-Vokabulars
``issuer | recipient | witness | other``. Vier Konsumenten lesen daraus:

* ``frontend/renderer.py`` (Quellen-Detail-Annotations-Tabelle)
* ``frontend/aggregator/_profile_enrichment.py`` (Personen- und
  Org-Profile)
* Jinja-Templates ``person.html`` und ``org.html`` (per Context)
* ``frontend/static/js/document.js`` (per ``data/role_labels.json``,
  vom Build geschrieben)

Witness fasst Zeugen und Siegler zusammen (TEI-Edition-Guidelines
"sealer or witness"). Das Label macht beide Funktionen sichtbar.
"""

ROLE_LABELS = {
    "issuer":    "Aussteller*in",
    "recipient": "Empfänger*in",
    "witness":   "Zeug*in / Siegler*in",
    "other":     "Sonstige",
}
