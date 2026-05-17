# JSON-Schema der Edition

Dokumentation der JSON-Dateien unter `docs/data/` und `docs/register/`. Sie sind das maschinenlesbare Format der Edition: das Frontend liest sie direkt, externe Auswertungen können sie ohne Build-Pipeline weiterverwenden.

Pro Datei beschreibt dieses Dokument den Zweck, den Producer im Build (welche Funktion sie schreibt), die Konsumenten im UI, die Top-Level-Felder und ein Beispiel. Die normativen `meta.structure`-Blöcke in den Dateien selbst sind für Aggregat-Dateien zusätzlich kanonisch.

Stand: aktueller Build. Versionierung pro Datei über `meta.schema_version` bzw. `meta.version`.

## Konventionen

**ID-Präfixe.** Entitäten werden global eindeutig referenziert: `pe__` für Personen (z. B. `pe__alexander_iii_QGW_II_I_0a`), `org__` für Organisationen, `pl__` für Orte, `f__` für Quellen-Files (z. B. `f__QGW_0a`).

**Datums-Felder.** ISO-Datum `YYYY-MM-DD` (oder `YYYY-MM`/`YYYY` bei Unschärfe). Range-Daten in `date_iso_start` und `date_iso_end`. Lesbare Form in `date_display` (z. B. `1327 IX 29`) und/oder `dn` (deutsch, z. B. `29.09.1327`). Dekade als 4-stellige Jahreszahl ohne Einer-Stelle (1320, 1330, …).

**Filter-Geltungsbereich.** Alle JSON-Outputs sind auf `pipeline.config.RELEASED_CORPORA` gefiltert. Nicht-freigegebene Korpora erscheinen weder als Datensätze noch als Statistik-Dimension.

**Kompakt-Felder in Massendaten.** `search.json`, `persons_search.json` und die `register/*.json` verwenden 1–3-Buchstaben-Keys für Bandbreiten-Reduktion. Die Mappings sind unten dokumentiert.

**Aggregat-Konvention (`roles.json` / `relations.json` / `transactions.json`).** Vier Top-Level-Blöcke sind Standard: `meta`, `observations` (Kreuztabellen als verschachtelte Objekte), `drill_down` (Listen von `file_key`-Verweisen pro Aggregat-Zelle), `coverage` (Datenqualitäts-Indikatoren). Siehe [knowledge/architecture.md](../../knowledge/architecture.md) und [knowledge/specification.md](../../knowledge/specification.md) für Begründung.

---

## `search.json`

**Zweck.** Such-Index der Quellen-Übersicht. Trägt alle Filter- und Sortier-Felder für die Tabelle unter `documents.html`.

**Producer.** `frontend/build.py::_build_index` (Z. ~870), Join aus `all_metadata` und `docs_aggregate.json`.
**Consumer.** `frontend/static/js/index.js`.

**Form.** Top-Level Array. Pro Quelle ein Record mit kompakten Feldnamen.

| Feld | Bedeutung |
|---|---|
| `id` | Lesbare Quellen-Nummer (z. B. `0a`, `1015`) |
| `t` | Regest-Text (Original) |
| `tf` | Regest-Text, normalisiert für die Volltextsuche (Diakritika neutralisiert) |
| `c` | Korpus-Kürzel (`QGW`, `Stadtbuecher`) |
| `cp` | Korpus-Pfad (`QGW/Vienna_1177-1414_ready`) |
| `cl` | Lesbares Korpus-Label (`QGW II/1 (1177–1414)`) |
| `sc` | Sub-Collection (Pfadteil 2) |
| `d` | Datum als Anzeigeform (`1177 V 10`) |
| `di` | Datum als ISO (`1177-05-10`) |
| `dn` | Datum deutsch (`10.05.1177`) |
| `p` | Ort der Beurkundung |
| `u` | URL der Detailseite, relativ zu `docs/` |
| `f` | `1` wenn Faksimile vorhanden, sonst `0` |
| `fu` | Faksimile-URL (erste Seite) |
| `pc` | Personen-Count (XPath-basiert, Mentions inklusive) |
| `pcd` | Personen distinct (quellenbereinigt) |
| `pcdf` / `pcdm` / `pcdu` | Distinct nach Geschlecht |
| `ec` | Event-Count (Top-Level-rs-Events) |
| `ecR` / `ecS` / `ecE` / `ecN` | Events nach Subtyp: abstract (Regest), seal, entry, nota |

**Sample.**

```json
{"id":"0a","t":"Papst Alexander III. ...","cp":"QGW/Vienna_1177-1414_ready",
 "cl":"QGW II/1 (1177–1414)","d":"1177 V 10","di":"1177-05-10",
 "p":"Venedig","u":"documents/QGW/Vienna_1177-1414_ready/0a.html",
 "f":0,"q":1,"qc":1,"pcd":1,"pcdm":1,"ec":1,"ecR":1}
```

---

## `docs_aggregate.json`

**Zweck.** Pro-Quelle-Aggregat: zentrale Datenschicht zwischen Pipeline-CSVs und Frontend-Views. Trägt Datum (ISO-normalisiert mit Range-Behandlung), Personen-Counts mit Geschlechter-Aufschlüsselung, Event-Counts mit Aufschlüsselung nach `rs/@type='event'`-Subtyp.

**Producer.** `frontend/aggregator.py::aggregate_docs`. Join aus `filenames.csv`, `persons.csv`, `persons_in_sources.csv`, `events_in_sources.csv`.
**Consumer.** `frontend/build.py::_build_index` zum Bauen von `search.json`.

**Form.** `{meta, docs}` mit `docs` als Array von Records.

| Feld | Bedeutung |
|---|---|
| `file_key` | Pipeline-File-Schlüssel (`f__…`) |
| `idno` | Lesbare Quellen-Nummer |
| `collection_path` | `{collection}/{subcollection}` |
| `date_iso_start` / `date_iso_end` | ISO-Range |
| `date_year` | Jahresanteil als Integer |
| `persons.distinct` / `f` / `m` / `u` | Quellenbereinigte Distinct-Counts |
| `events.total` / `abstract` / `seal` / `entry` / `nota` / `other` | Event-Counts pro Subtyp |

Konzeptionelle Beschreibung: [knowledge/data.md#Aggregat-Schicht](../../knowledge/data.md).

---

## `docs_lookup.json`

**Zweck.** `file_key → Metadaten`-Lookup für Drill-down-Overlays in den Exploration-Sub-Seiten. Erlaubt Klick auf eine Aggregat-Zelle → Quellen-Liste auflösen.

**Producer.** `frontend/aggregator.py::build_docs_lookup`.
**Consumer.** `frontend/static/js/drill-down.js`.

**Form.** Top-Level-Objekt, Schlüssel sind `file_key`s.

| Feld | Bedeutung |
|---|---|
| `u` | URL der Detailseite |
| `i` | `idno` (Quellen-Nummer) |
| `d` | Datum als `date_display` |
| `c` | Lesbares Korpus-Label |
| `r` | Regest, auf 150 Zeichen gekürzt |

---

## `roles.json` — Rollen × Geschlecht × Dekade × Organisationstyp

**Zweck.** Datenbasis der Sub-Seite [Rollen](../exploration/roles.html). Kreuztabellen über Personen-Event-Beteiligungen.

**Producer.** `frontend/aggregator/roles.py::aggregate_roles`.
**Consumer.** `frontend/static/js/exploration-roles.js`.

**Top-Level-Blöcke.**

| Block | Inhalt |
|---|---|
| `meta` | Schema-Version, Datenquellen, Dimensionen/Maße |
| `observations.role_by_sex` | `{role: {sex: count}}` |
| `observations.role_by_sex_by_decade` | `{role: {sex: {decade: count}}}` |
| `observations.transaction_types` | `{transaction_type: count}` |
| `observations.org_type_by_sex` | `{org_type: {sex: count}}` |
| `observations.org_type_totals` | `{org_type: count}` |
| `observations.org_type_by_decade_by_sex` | `{org_type: {decade: {sex: count}}}` |
| `drill_down` | Pro Kreuztabellen-Zelle eine sortierte `file_key`-Liste |
| `coverage` | Gesamtsummen, Normalisierungsraten |

**Dimensionen.** `role` (`issuer`, `recipient`, `witness`, `other`, `''` unspecified), `sex` (`m`, `f`, `unspecified`), `decade` (`1170`–`1410`, Schritt 10), `transaction_type` (kontrolliertes Vokabular).

---

## `relations.json` — Beziehungen

**Zweck.** Datenbasis der Sub-Seite [Beziehungen](../exploration/networks.html). Annotierte Verbindungen zwischen Personen, klassifiziert nach Typ.

**Producer.** `frontend/aggregator/relations.py::aggregate_relations`.
**Consumer.** `frontend/static/js/exploration-networks.js`.

**Top-Level-Blöcke.**

| Block | Inhalt |
|---|---|
| `meta` | Standard |
| `overview.type_by_sex` | `{type: {sex: count}}` |
| `overview.type_by_sex_by_decade` | `{type: {sex: {decade: count}}}` |
| `labels` | Liste annotierter Beziehungslabels mit Typ-Klassifikation und Frequenz |
| `persons` | Personen mit Beziehungs-Summary (für Personen-Detail) |
| `rep_direction` | Vertretungs-Richtungs-Matrix (Vertreter × Vertretene × Geschlecht) |
| `friendship` | Freundschafts-Edges separat |
| `drill_down` | `file_key`-Listen pro Aggregat-Zelle |
| `coverage` | Gesamtsummen |

**Dimensionen.** `relationship_type` (`kin`, `occ`, `rep`, `friend`), `sex`, `decade`, `label`.

---

## `transactions.json` — Transaktionen

**Zweck.** Datenbasis der Sub-Seite [Transaktionen](../exploration/transactions.html). Repertoire der Rechtsgeschäfte über die Zeit.

**Producer.** `frontend/aggregator/transactions.py::aggregate_transactions`.
**Consumer.** `frontend/static/js/exploration-transactions.js`.

**Top-Level-Blöcke.**

| Block | Inhalt |
|---|---|
| `observations.tx_timeline` | `{transaction_type: {decade: count}}` |
| `observations.recipient_type_totals` | `{org_type: count}` |
| `triggerstrings` | Verbform-Tabelle (raw → normalisiert, Frequenz) |
| `recipients` | Empfänger-Aggregate |
| `org_supporters` | Pro Organisation: Liste der unterstützenden Personen |
| `org_tx` | Org-Typ × Transaktionstyp Heatmap |
| `drill_down` | `file_key`-Listen pro Zelle |
| `coverage` | Normalisierungsrate, Gesamtevents |

**Dimensionen.** `transaction_type`, `decade`, `org_type`, `verb_form`.

---

## `persons_search.json`

**Zweck.** Such-Index für das Personenregister.

**Producer.** `frontend/build.py::_person_search_data` (gefiltert auf `_released_person_keys()`).
**Consumer.** `frontend/static/js/register.js`.

**Form.** Top-Level Array.

| Feld | Bedeutung |
|---|---|
| `id` | Personen-ID (`pe__…`) |
| `n` | Anzeigename |
| `fn` | Vorname |
| `sn` | Familienname |
| `sex` | `m`, `f` oder leer |
| `d` | Sterbedatum oder leer |
| `dc` | Document Count (Anzahl Quellen mit Nennung) |

---

## `register/persons.json`, `organisations.json`, `places.json`

**Zweck.** Reverse-Index für die Inline-Detail-Erweiterung im Register: Klick auf einen Eintrag → Liste aller Quellen, in denen er vorkommt.

**Producer.** `frontend/build.py::_build_register_json`. Personen sind auf `_released_person_keys()` gefiltert; Organisationen und Orte über den `reverse_index` implizit (nur Entitäten, die in freigegebenen Quellen referenziert sind).
**Consumer.** `frontend/static/js/register.js` (Lazy-Load bei erstem Klick).

**Form.** Top-Level-Objekt, Schlüssel sind Entity-IDs.

| Feld pro Quellen-Eintrag | Bedeutung |
|---|---|
| `u` | URL der Detailseite |
| `i` | `idno` |
| `d` | Datum (`date_display`) |
| `c` | Korpus-Label |
| `r` | Regest |

---

## `timeline.json`

**Zweck.** Histogramm-Daten für den Zeit-Range-Slider auf Quellen-Übersicht und Exploration-Sub-Seiten.

**Producer.** `frontend/aggregator.py::aggregate_timeline`.
**Consumer.** `frontend/templates/index.html` (Server-Side-Rendering der Bars), JS-Histogramm-Update.

**Top-Level-Blöcke.**

| Feld | Bedeutung |
|---|---|
| `total` | Gesamtzahl Quellen |
| `period` | `[min_year, max_year]` |
| `placeholder_count` | Quellen mit nicht-parsbarem Datum |
| `collections` | Pro Korpus die Anzahl Quellen |
| `decades` | `{decade: count}` |

---

## `categories.json`

**Zweck.** Editorielle Zuordnungstabelle Organisationstyp → Kategorie (`geistlich`, `weltlich`, `sonstige`). Wird nicht aus den TEI-Daten abgeleitet, sondern als Modellierungsentscheidung gepflegt.

**Producer.** `frontend/content/categories.json` (Quelle), `frontend/build.py::_write_categories` kopiert nach `docs/data/`.
**Consumer.** Analyse-Seite, Exploration-Filter.

**Top-Level-Blöcke.**

| Feld | Bedeutung |
|---|---|
| `meta.version` / `decided` / `note` | Versions- und Entscheidungs-Metadaten |
| `categories` | `{category: [org_type, …]}` |
| `borderline` | Liste fachlich uneindeutiger Typen (z. B. `Zeche_Bruderschaft`) |
| `labels` | Anzeige-Labels |

---

## `query_vocabulary.json`

**Zweck.** Vokabular für die Analyse-Seite (Composer-Dashboard): Subjekte, Filter, Werte, Constraints.

**Producer.** `frontend/content/query_vocabulary.json` (Quelle), `frontend/build.py::_write_query_vocabulary` kopiert.
**Consumer.** `frontend/static/js/analysis-composer.js`.

**Top-Level-Blöcke.**

| Feld | Bedeutung |
|---|---|
| `subjects` | `{subject: {label, filters}}` (`persons`, `sources`, `events`, …) |
| `filters` | `{filter: {label, value_kind, values, …}}` |
| `coverage` | Pro Subjekt ein Coverage-Hinweistext |
| `constraints.max_active_filters` | Hartes Limit (3) |

Schema-Drift gegen die `roles.json` / `relations.json` / `transactions.json`-Werte wird im Test `frontend/tests/test_query_vocabulary.py` geprüft.

---

## Schema-Versionierung

`meta.schema_version` (Aggregat-Dateien) bzw. `meta.version` (Editorielle) inkrementiert, sobald sich die Top-Level-Struktur ändert. Konsumenten sollten beim Laden den Wert prüfen und bei Inkompatibilität explizit fehlschlagen statt stillschweigend Felder zu erraten.

Aktueller Stand: alle Aggregat-Dateien `schema_version: "1.0"`.

## Build und Konsistenz

Die JSON-Outputs werden durch `python -m frontend build` aus `pipeline/output/*.csv` (Schwester-Repo) und den `frontend/content/*.json` (editorielle Mappings) erzeugt. Reproduzierbarkeit: gleicher Input → identischer Output, abgesehen von Build-Datums-Stempeln in `meta.created`.

Verifikation gegen die TEI-Quellen läuft über das unabhängige Test-Set unter `verification/` (siehe [knowledge/architecture.md#Verifikations-Test-Set](../../knowledge/architecture.md)).
