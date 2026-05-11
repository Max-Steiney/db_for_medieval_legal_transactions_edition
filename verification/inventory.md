# Aggregat-Inventar

Vollständiger Katalog aller Kennzahlen, die das Frontend anzeigt, mit Herkunft (JSON-Datei + Feld) und erwarteter Aggregations-Regel aus TEI + Register-XML.

## Notation

- **JSON-Pfad:** `datei.json#feld.unterfeld` — Punkt-Separator für Pfade in das JSON.
- **TEI-Regel:** XPath-artige Beschreibung der TEI-Extraktion, Zähloperation, Filter.
- **Status:** `covered` = im Test-Set implementiert, `planned` = vorgesehen, `skipped` = bewusst ausgelassen (mit Begründung).

## Ebene 1 — Breite (Gesamtanzahlen)

### Quellen / Dokumente

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| docs.total | `timeline.json#total` | Anzahl aller parsebaren TEI-Dateien unter `sources/QGW/**` und `sources/Stadtbuecher/**` | planned |
| docs.by_collection | `timeline.json#collections.*.count` | Anzahl TEI-Dateien je Unterordner von `sources/` | planned |
| docs.by_decade | `timeline.json#decades` | Counter über Dekaden, abgeleitet aus `//tei:date/@when` oder `@from`/`@to` | planned |
| docs.date_range | `timeline.json#collections.*.min_date` / `max_date` | min/max über `@when` (oder Intervall-Mittelwert bei `@from`/`@to`) pro Quellenkorpus | planned |

### Personen

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| persons.total_individual | `persons_search.json` Arraylänge | Anzahl Einträge in `indices/personList.xml` (`//tei:person`) | planned |
| persons.total_mentions | — (aktuell nicht im JSON) | Anzahl `//tei:rs[@type='person']` über alle TEI-Dateien | planned |
| persons.by_sex | abgeleitet aus `persons_search.json[*].sex` | Counter über `//tei:person/@sex` im Register | planned |
| persons.dc | `persons_search.json[*].dc` | Anzahl unterschiedlicher `file_key` mit mindestens einer Nennung der Person | planned |

### Organisationen

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| orgs.total_individual | `organisations_search.json` Arraylänge | Anzahl `//tei:org` in `indices/orgList.xml` | planned |
| orgs.total_mentions | — | Anzahl `//tei:rs[@type='org']` über alle TEI-Dateien | planned |
| orgs.dc | `organisations_search.json[*].dc` | wie persons.dc, für Organisationen | planned |

### Orte

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| places.total_individual | `places_search.json` Arraylänge | Anzahl `//tei:place` in `indices/placeList.xml` | planned |
| places.total_mentions | — | Anzahl `//tei:rs[@type='place']` plus ggf. `//tei:placeName` in Metadaten | planned |
| places.dc | `places_search.json[*].dc` | wie persons.dc, für Orte | planned |

### Events / Rechtsgeschäfte

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| events.total | abgeleitet aus `roles.json#coverage.total_events` | Anzahl `//tei:rs[@type='event']` über alle TEI-Dateien | planned |
| events.by_decade | `transactions.json#tx_timeline.*.*` (Summe) | Events gruppiert nach Dekade des enthaltenden Dokuments | planned |

### Qualität

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| quality.by_severity | `quality.json#observations.bySeverity.*` | Counter über Validierungsfindings (aktuell nicht aus TEI ableitbar ohne Re-Implementation der Validierung) | skipped (Validierungslogik liegt in Pipeline) |

## Ebene 2 — Tiefe (Kreuztabellen)

### Rollen

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| roles.by_role | abgeleitet | Counter über `@role` von `//tei:rs[@type='fn']` | planned |
| roles.by_role_sex | `roles.json#observations.role_by_sex` | Personen pro Rolle × Geschlecht: `//tei:rs[@type='fn'][@role=$r]//tei:rs[@type='person']/@ref` ∩ `personList[@sex=$s]` | planned |
| roles.by_role_sex_decade | `roles.json#observations.role_by_sex_by_decade` | wie oben, zusätzlich nach Dekade des Dokuments gruppiert | planned |

### Beziehungen

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| relations.by_type | `relations.json#overview.by_type` | Counter über `//tei:roleName[@type][@corresp]` mit Typ-Normalisierung | planned |
| relations.by_type_decade | `relations.json#overview.by_decade` | wie oben, zusätzlich nach Dekade | planned |

### Transaktionsverben

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| transactions.by_verb_decade | `transactions.json#tx_timeline` | Text von `//tei:rs[@type='event']/tei:triggerstring[@n='disp']`, normalisiert zu Catchwords (Normalisierung aus Pipeline übernehmen oder mindestens Rohtext vergleichen) | planned |
| transactions.recipients | `transactions.json#recipients` | Organisationen in `<rs type="fn" role="recipient">` innerhalb eines Events | planned |

### Orte mit Dokumentbezug

| Name | JSON-Pfad | TEI-Regel | Status |
|---|---|---|---|
| places.doc_count | `epic_d.json#places[*].doc_count` | Anzahl distinkter `file_key` pro Ort-ID | planned |
| places.decades | `epic_d.json#places[*].decades` | Dekaden-Abdeckung pro Ort-ID | planned |

## Reihenfolge der Implementierung

1. `docs.*` — einfachster Fall, testet Parser-Grundlage und Dekaden-Berechnung.
2. `persons.*`, `orgs.*`, `places.*` auf Register-Ebene (Ebene 1) — testet Register-Loader.
3. `*.dc` — testet Reverse-Index.
4. `events.total`, `roles.by_role` — testet Event- und Rollen-Extraktion.
5. Tiefe: `roles.by_role_sex`, `relations.by_type`, `transactions.by_verb_decade`.
6. Orte-Detaildaten (`epic_d`).

## Bewusst ausgelassen

- **`quality.json`-Aggregate** — die Validierungslogik lebt in der Pipeline. Eine Re-Implementation hier wäre eine Parallel-Validierung, nicht eine Verifikation. Quality wird separat gegen das Pipeline-`validation_report.json` verglichen, falls nötig.
- **`search.json`** — reiner Flachindex für Volltextsuche; Inhalt wird nicht aggregiert, Vergleich unsinnig.
- **`docs_lookup.json`** — Mapping, kein Aggregat.

## Ebene 4 — HTML-Coverage (Pipeline-CSV → gerendertes HTML)

Die obigen Ebenen prüfen, ob die Pipeline-JSONs zum TEI-Stand passen.
Die HTML-Coverage geht eine Stufe weiter und prüft, ob die struktur-
ierten Felder, die der Aggregator aus den Pipeline-CSVs an das
Template übergibt, im gerenderten Output sichtbar werden.

Lauf: `python -m verification.run --html`. Eingaben:
- `pipeline/output/*.csv` (persons.csv, organisations.csv, occ_relations_in_sources.csv)
- `docs/register/persons/*.html`, `docs/register/orgs/*.html`, `docs/documents/**/*.html`

| Name | Quelle (CSV) | HTML-Selector | Status |
|---|---|---|---|
| html.persons.display_name_mismatch | persons.csv: forename_reg, surname_reg, addname_reg | `.person-name` | covered |
| html.persons.sex_label_mismatch | persons.csv: sex | `.ph-meta-strip dt=Geschlecht + dd` | covered |
| html.persons.source_count_vs_rows | docs in reverse_index | `.ph-meta-strip dt=Quellen` vs `.person-source-table tbody td.src-col-idno` | covered |
| html.persons.death_display_vs_csv | persons.csv: dead_before (ISO → DD.MM.YYYY) | `.ph-meta-strip dt=Verstorben vor + dd` | covered |
| html.persons.authority_urls_vs_csv | persons.csv: authority (pipe-split URLs) | `.ph-subline a.ext-link[href*=authority]` | covered |
| html.persons.wiki_url_vs_csv | persons.csv: PAGEID_WienWiki | `.ph-subline a.ext-link[href*=wienwiki]` | covered |
| html.orgs.name_mismatch | organisations.csv: name_reg (pre-pipe) | `.person-name` | covered |
| html.orgs.observance_vs_csv | organisations.csv: observance | `.ph-meta-strip dt=Observanz + dd` | covered |
| html.orgs.parent_org_vs_csv | organisations.csv: org_key (released only) | `.ph-meta-strip dt=Übergeordnet + dd a` | covered |
| html.orgs.authority_urls_vs_csv | organisations.csv: authority | `.ph-subline a.ext-link` | covered |
| html.persons.occ_count_vs_csv | occ_relations_in_sources.csv: person_key | `.rel-block-occ tbody tr` Count | covered |
| html.persons.occ_inverse_count_vs_csv | occ_relations_in_sources.csv: related_key (wenn pe__) | `.rel-block-occ_inverse tbody tr` Count | covered |
| html.documents.orphan_person_refs | docs/register/persons/ Datei-Existenz | `data-ref^=pe__` in `docs/documents/**/*.html` | covered |
| html.documents.orphan_org_refs | docs/register/orgs/ Datei-Existenz | `data-ref^=org__` in `docs/documents/**/*.html` | covered |

Bekannte Lücken (siehe `contract.py::KNOWN_GAPS`):
- `org.place_name.is_plain_text` — Place-Profile gibt es nicht; place_name wird als Klartext im Org-Header gerendert.
- `person.title_ref_inverse.empty_by_data` — Mirror-Schlüssel ist strukturell vorbereitet, aber im aktuellen TEI-Stand sind alle `related_key` in title-ref-Relationen org__-Keys.

### Profil-Quelle-Konsistenz (Cross-Check)

| Name | Erwartung | Status |
|---|---|---|
| html.cross.person_profile_source_missing_annotation | Profil listet Quelle X → Quelle X hat `data-ref` ODER `data-corresp` auf Profil | covered |
| html.cross.person_doc_annotation_missing_in_profile | Quelle X annotiert Person A → Profil von A listet Quelle X | covered |
| html.cross.org_profile_source_missing_annotation | analog fuer Organisationen | covered |
| html.cross.org_doc_annotation_missing_in_profile | analog fuer Organisationen | covered |

## Ebene 5 — TEI-Direkt-Coverage (TEI → gerendertes HTML)

Lauf: `python -m verification.run --tei-html`. Eingaben:
- TEI-Quelldateien in `../db_for_medieval_legal_transactions/sources/`
- `docs/documents/**/*.html`

Ueberspringt die CSV-Pipeline-Zwischenstufe und prueft End-to-End, ob jede
`<rs ref="...">`-Annotation als `data-ref="..."` im HTML erscheint und umgekehrt.

| Name | TEI-Quelle | HTML-Selector | Status |
|---|---|---|---|
| teihtml.pair_coverage.documents_paired | TEI-Dateien gesamt vs. gerenderte HTMLs | Datei-Existenz | covered |
| teihtml.pair_coverage.tei_without_html | TEI-Dateien ohne HTML-Pendant | `filenames.csv status='in progress'` als known_gap | covered |
| teihtml.person_refs.{missing,extra}_in_html | `<rs type="person" ref>` | `[data-ref^=pe__]` | covered |
| teihtml.org_refs.{missing,extra}_in_html | `<rs type="org" ref>` | `[data-ref^=org__]` | covered |
| teihtml.place_refs.{missing,extra}_in_html | `<rs type="place" ref>` | `[data-ref^=pl__]` | covered |
| teihtml.event_refs.{missing,extra}_in_html | `<rs type="event" ref>` (ohne NULL) | `[data-ref^=ev__]` | covered |
| teihtml.person_roles.{missing,extra}_in_html | innermost `<rs type="fn" role>` ueber `<rs type="person">` | innermost `data-role` ueber `[data-ref^=pe__]` | covered |
| teihtml.org_roles.{missing,extra}_in_html | analog fuer Org | analog | covered |
| teihtml.date_display_vs_tei | Text-Inhalt `<profileDesc/creation/date>` | letzte `(...)` vor `, Datenbank` im `<title>` | covered |
| teihtml.date_display_html_missing | TEI hat Datum, HTML rendert leer | — | covered |

Normalisierungen im Vergleich:
- Aeussere runde/eckige Klammern werden gestrippt (Stadtbuecher-Konvention).
- `X (Y)`-Pattern: das Frontend rendert nur Y, das gilt als Match.

Bekannte Drift-Ergebnisse (Daten- oder Renderer-Bugs, nicht Coverage-Luecken):
- 3 Stadtbuecher mit Klammer-Anomalien im TEI-Datums-Text.
- 1 Stadtbuch (333) mit kaputtem Zeichen im HTML-Titel.
