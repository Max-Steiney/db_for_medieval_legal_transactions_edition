"""Zentrales Mapping fuer Funktionsrollen-Labels.

Single-source-of-truth fuer die deutschen Anzeigewerte des TEI-Vokabulars
``issuer | recipient | witness | other``. Vier Konsumenten lesen daraus:

* ``frontend/renderer.py`` (Quellen-Detail-Annotations-Tabelle)
* ``frontend/aggregator/_profile_enrichment.py`` (Personen- und
  Org-Profile)
* Jinja-Templates ``person.html`` und ``org.html`` (per Context)
* ``frontend/static/js/document.js`` (per ``<script id="role-labels">`` in
  ``base.html``, vom Build als JSON eingebettet; Inline-Fallback im JS)

Witness fasst Zeugen und Siegler zusammen (TEI-Edition-Guidelines
"sealer or witness"). Das Label macht beide Funktionen sichtbar.
"""

ROLE_LABELS = {
    "issuer":    "Aussteller:in",
    "recipient": "Empfänger:in",
    "witness":   "Zeug:in / Siegler:in",
    "other":     "Sonstige",
}

# Plural-Variante fuer Kategorie-, Filter- und Aggregat-Kontexte (Register-
# Sidebar-Chips, Aktiv-Filter, Abfrage-Dropdowns, Rollen-Verteilung), wo ein
# Label eine Gruppe meint, nicht eine Einzelperson. Per-Person-Stellen
# (Annotationstabelle, Profil, Tabellen-Pille) nutzen den Singular oben.
ROLE_LABELS_PLURAL = {
    "issuer":    "Aussteller:innen",
    "recipient": "Empfänger:innen",
    "witness":   "Zeug:innen / Siegler:innen",
    "other":     "Sonstige",
}
