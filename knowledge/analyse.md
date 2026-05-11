---
title: Analyse
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-02-19
updated: 2026-05-11
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Information Visualisation]]", "[[Quantitative Analysis]]"]
related: [exploration, requirements, ui-design, decisions, glossar]
---

# Analyse

Wissensdokument zum Analysebereich der Datenbank. Der Analysebereich versammelt alle quantitativen Zugänge zur Datenbasis. Er besteht aus zwei Sub-Seiten unter `/analysis/` und steht als gleichberechtigter Zweig neben der [[exploration]]; das Interaktionsmuster ist strukturiert (vorgegebene Achsen, exakte Zahlen, Provenienz), die Exploration arbeitet visuell-interaktiv. Die Trennung ist in [[decisions#Exploration und Analyse als getrennte Bereiche]] begründet.

## Zwei Sub-Seiten

**Auswertungen** (`/analysis/auswertungen.html`) zeigt vorberechnete Verteilungen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen — jeweils als Donut, Bar-Chart oder Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine Zähleinheit-Umschaltung in der Funktionsrollen-Sektion wechselt lokal zwischen Nennungen und Individuellen Personen. Die Seite ist filter-getrieben: Nutzerinnen ändern Achsen und sehen Verteilungen sich anpassen, ohne eine konkrete Frage formulieren zu müssen. Begründung der Verortung im Analyse-Bereich: [[decisions#Auswertungen gehört in den Analyse-Bereich]].

Jede Aggregat-Zelle ist klickbar und öffnet das [[ui-design#Drill-down-Overlay]] mit den beitragenden Quellen — Donut-Arc und Legend-Item für Funktionsrollen und Beziehungstypen, Bar für Transaktionstypen, Tabellenzeile für Bezeichnungen. Filter werden in den Drill mitgenommen (sex-Suffix im Lookup-Schlüssel, Dekaden-Filter über Datums-Parsing). Im Footer steht der Cross-Page-Sprung in die Quellen-Liste mit übernommenem Zeitraum-und-Geschlecht-Filter ([[ui-design#Cross-Page-Sprung in die Quellen-Liste]]).

Der Filter-Stand wird in die URL serialisiert (`?dec=1300-1380&sex=f&type=kin&q=hausfrau&mode=persons`), siehe [[ui-design#URL-State-Sync]] — damit ist jeder Forschungsstand dieser Seite zitierbar.

**Abfragen** (`/analysis/index.html`) bedient zwei Einstiegsmodi nebeneinander: eine kuratierte Galerie konkreter Forschungsfragen als oberste Ebene, ein freier Custom-Builder darunter im aufklappbaren `<details>`. Die Frage ist first-class concept und autonom. Nutzerinnen kommen mit ihrer Frage und finden sie in der Galerie oder bauen sie über Slots im Builder zusammen; das Result-Panel beantwortet die Frage als Visualisierung plus Drill-down auf die Quellen. Architektur und Pivot-Begründung in [[decisions#Analyse-Seite mit Frage-Galerie und Custom-Builder]].

Beide Sub-Seiten teilen sich dieselben Aggregate (`roles.json`, `relations.json`, `transactions.json`) und dieselben Filter-Bausteine in der Sidebar. Eine Filteränderung auf der einen Seite überträgt sich aktuell nicht automatisch auf die andere; das ist eine offene Designfrage.

Deployment als statisches Frontend auf GitHub Pages, auf Basis der vorhandenen JSON-Datengrundlage.

## 1. Zielsetzung

Der Analysebereich soll Nutzerinnen erlauben, konkrete inhaltliche Fragen an den Datenbestand zu stellen, ohne SQL, SPARQL oder vergleichbare Query-Sprachen lernen zu müssen. Statt beliebiger Abfragen werden vorgefertigte Fragetypen angeboten, die über typisierte Slots angepasst werden. Das konzeptionelle Vorbild ist die komponierbare Logik von Scratch, übersetzt in ein domänenspezifisches Vokabular für Urkundenforschung.

Typische Beispielfragen, die das Interface beantworten soll:

- Wie viele geistliche Einrichtungen sind im Datenbestand belegt?
- Wie verteilen sich die Beteiligten an Rechtsgeschäften nach Geschlecht?
- Welche Rechtsgeschäftstypen treten in welchem Zeitraum auf?
- In welchen Rollen treten Frauen in Stadtbüchern auf?

## 2. Datenbestand als Ausgangspunkt

Der Datenbestand liegt in Form vorkonfektionierter JSON-Dateien vor, die bereits stark auf Analyse- und Visualisierungszwecke hin normalisiert sind. Die Ebenen und Dimensionen des Modells (vgl. `data.md`) finden sich darin konkret wieder.

### 2.1 Datenbestand

Pro Ebene liegt eine eigene JSON vor: Quellen in `search.json` und `docs_lookup.json`, Personen in `persons_search.json`, Organisationen in `orgs_search.json`, vorberechnete Aggregate in `roles.json` (Rollen), `relations.json` (Beziehungen), `transactions.json` (Transaktionen). Detail-Profile pro Entität liegen unter `register/persons/` und `register/orgs/`.

Zeitraum: freigegeben 1177 bis 1412 (Ausnahmen bis 1414 für QGW II/1 und II/2), mit nicht ausgewertetem Bereich 1418 bis 1447. Die Dokumentdichte ist stark ungleichverteilt, wenige Dutzend Dokumente in den ersten zwei Jahrhunderten, ein Dichte-Schwerpunkt im späten 14. Jahrhundert (insbesondere Stadtbücher). Konkrete Zahlen leben in den `coverage`-Blöcken der Aggregate und im Footer der Datenbank.

### 2.2 Register-Dateien

Das öffentlich freigegebene Personenregister liegt als flaches Array mit kompakten Feldnamen in `persons_search.json` vor. Beispiel:

```json
{
  "id": "pe__abraham_QGW_II_I_1599",
  "n":  "Abraham der Jud",
  "fn": "Abraham",
  "sn": "",
  "sex": "m",
  "d": "",
  "dc": 1,
  "qw": 1
}
```

Felder: `id` eindeutige Kennung, `n` Namensform, `fn`/`sn` Vor- und Familienname, `sex` Geschlecht, `d` Datierung, `dc` Anzahl der Quellen mit Nennung (*document count*), `qw` Qualitäts- bzw. Normalisierungsgewicht (`-1` unbekannt, `0` niedrig, `1` und `2` höhere Konfidenz).

Das Organisationsregister liegt parallel als `orgs_search.json` vor und nutzt dasselbe Such-Schema wie das Personenregister; zusätzlich trägt jeder Eintrag ein `tp`-Feld für den Typ. Detail-Profile pro Organisation stehen unter `register/orgs/<org__id>.html`. Orts-Annotationen im Quellen-Volltext bleiben als Inline-Markup sichtbar, tragen aber kein Sprungziel und kein eigenes Register.

### 2.3 Vorkompilierte Aggregationen: die Aggregat-JSONs

Die `roles.json`/`relations.json`/`transactions.json` enthalten bereits vorberechnete Kreuztabellen mit Drill-Down-Listen auf Dokumentenebene. Sie entsprechen exakt dem in früheren Iterationen theoretisch angenommenen Konzept der *vorberechneten Aggregationen*.

- `roles.json` Rollen × Geschlecht × Dekade × Organisationstyp (Event-Partizipationen)
- `relations.json` Beziehungen (Verwandtschaft, Beruf, Vertretung, Freundschaft), 12.178 insgesamt
- `transactions.json` Transaktionstypen × Dekade × Organisationstyp

Die Struktur jeder Datei ist dreigeteilt:

```
meta          Schema, Dimensionen, Maße, Quellen
observations  Kreuztabellen als verschachtelte Objekte
drill_down    Listen von Dokument-IDs pro Zelle
coverage      Gesamtsummen und Datenqualitäts-Indikatoren
```

Das ermöglicht ein einheitliches UI-Muster: aggregierte Zahl anzeigen, bei Klick direkt die Liste der Quelldokumente aufschlüsseln, über `docs_lookup.json` zu Metadaten jedes Dokuments auflösen.

### 2.4 Organisationstypen als Klassifikationsbasis

Das Feld `tp` im Organisationsregister enthält eine geschlossene Typologie. Die Kategorie *geistlich vs. weltlich* liegt im Datenmodell nicht als eigene Eigenschaft vor, sondern muss über eine Zuordnungstabelle erzeugt werden. Geistliche Typen sind etwa Messe, Pfarre, Kirche_Kapelle, Altar, Dioezese_Erzdioezese, Kloster_m, Kloster_f, Zeche_Bruderschaft, Spital_Siechenhaus, Orden, Kirche, Kapelle. Weltliche Typen sind Stadt, Gemeinde, Stadtviertel, Herzogtum, Burg, Koenigreich, Reich, Markgrafschaft. Universität und OTHER bleiben kontextabhängig.

Diese Zuordnung ist eine inhaltliche Modellierungsentscheidung, die im Interface dokumentiert werden muss. Zeche_Bruderschaft und Spital_Siechenhaus sind Grenzfälle und sollten als solche ausweisbar sein.

### 2.5 Datenqualität und Freigabestand

Der Validierungsreport (`quality.json`) und die Coverage-Blöcke der Aggregat-JSONs machen die Datenqualität sichtbar. Charakteristisch ist eine durchgängig niedrige Normalisierungsrate: nur ein kleiner Teil der dispositiven Verben ist im kontrollierten Vokabular der Transaktionstypen geführt, und nur ein Teil der Personen hat eine explizite Organisationszuordnung.

Diese Verhältnisse sind keine nebensächliche Meta-Information, sondern konstitutiver Teil dessen, was das Interface ausweisen muss. Eine Zählung *Transaktionen vom Typ Kauf* bedeutet nicht, dass alle anderen Events keine Käufe sind, sondern dass nur ein Bruchteil überhaupt kategorisiert ist.

Nicht alle in der Validierung erscheinenden Korpora sind im UI sichtbar. Die Single-Source-of-Truth für die freigegebenen Korpora ist `RELEASED_CORPORA` im Schwester-Repo (`pipeline/config.py`); der freigegebene Zeitraum lebt als `RELEASED_PERIOD` im Frontend-Repo (`frontend/config.py`). Hardcoded Werte in Templates gelten als Fehler.

### 2.6 Volumen und Performance

Die größeren JSON-Dateien (`search.json`, `persons_search.json`, `relations.json`, `transactions.json`, `docs_lookup.json`) liegen jeweils im einstelligen MB-Bereich. GitHub Pages liefert sie gzip-komprimiert aus. Progressives Laden (Register beim Start, Aggregat-JSONs on-demand beim Öffnen der zugehörigen Template-Familie) hält den initialen Transfer klein.

## 3. Technische Architektur

### 3.1 Verzicht auf SPARQL im Browser

Comunica oder Oxigraph WASM funktionieren grundsätzlich, bringen aber deutlichen Overhead (Bundle mehrere MB, Cold Start, kleine Entwicklerbasis). Da die Aggregationen im Datenbestand bereits vorberechnet vorliegen, ist die Ausdrucksstärke einer SPARQL-Engine nicht nötig und methodisch nicht gerechtfertigt.

### 3.2 Zweischichtige Laufzeitarchitektur

**Aggregations-Schicht (read-only, vorkompiliert).** Für Fragen, die sich auf die vorberechneten Kreuztabellen der Aggregat-JSONs abbilden lassen, werden die Zählungen direkt aus der passenden Datei gelesen. Antwortzeit: Einzelabfrage, O(1)-Lookup in verschachtelten Objekten.

**Filter-Schicht (dynamisch, auf Register-Arrays).** Für Fragen, die die vorberechneten Dimensionen kombinieren oder feinere Filter setzen, werden die Register-Arrays zur Laufzeit gefiltert. Bei der Korpusgröße und einfachen Prädikaten liegt das im Millisekundenbereich.

**Drill-Down-Schicht.** Jede Aggregation ist über `drill_down[key]` mit einer Liste von Dokument-IDs verknüpft, die über `docs_lookup.json` in Metadaten aufgelöst werden. Das erlaubt das Klick-zu-Quellen-Muster ohne zusätzliche Datenladung.

### 3.3 Indizierung beim Start

Beim ersten Öffnen des Analysebereichs werden folgende Indizes im Speicher aufgebaut:

```
personsById         Map<id, Person>
personsBySex        Map<"m"|"f", Person[]>
personsByQw         Map<number, Person[]>
orgsById            Map<id, Organisation>
orgsByType          Map<typeName, Organisation[]>
orgsByCategory      Map<"geistlich"|"weltlich"|"sonstige", Organisation[]>
placesById          Map<id, Place>
docsById            Map<id, Document>
docsByCorpus        Map<corpusName, Document[]>
docsByDecade        Map<decade, Document[]>
```

Diese Indizes stehen allen Query-Templates zur Verfügung und sind nach Build einmal initialisiert.

### 3.4 Kategorien-Mapping als separates Artefakt

Die Zuordnung `tp → category` (geistlich/weltlich/sonstige) liegt nicht in den Daten, sondern muss explizit modelliert werden. Sie gehört als eigene Konfigurationsdatei `categories.json` ins Repository, versioniert und dokumentiert. Im Interface muss die verwendete Zuordnung aufrufbar und zitierbar sein.

### 3.5 Freigabe-Filter

Nicht alle Korpora in der Validierung sind im UI sichtbar. Eine Konfiguration `release.json` entscheidet, welche Korpora und welche Register-Dimensionen angezeigt werden. Die Filterung erfolgt beim Build (um die ausgelieferten JSON-Dateien klein zu halten) und zusätzlich zur Laufzeit als Sicherheitsnetz.

### 3.6 Build-Pipeline

GitHub Action beim Deploy:

1. Eingangsdaten (JSON-LD oder TEI-abgeleitet) werden normalisiert.
2. Register werden mit kompakten Feldnamen geschrieben.
3. Aggregat-JSONs werden neu gerechnet, inklusive `drill_down` und `coverage`.
4. `categories.json` und `release.json` werden angewendet.
5. Dateien werden gzipkomprimiert ausgeliefert.

## 4. Interface-Konzept: Frage-Galerie und Custom-Builder

### 4.1 Grundstruktur

Die Abfragen-Sub-Seite hat zwei Einstiegsmodi nebeneinander. Die kuratierte **Frage-Galerie** liegt oben und zeigt konkrete Forschungsfragen als Karten mit Frage-Text, Antwort als Mini-Visualisierung und einer Hand voll Kontext-Zahlen. Der **Custom-Builder** liegt darunter im aufklappbaren `<details>` und erlaubt das freie Zusammenstellen einer Abfrage über Subject, Filter-Set und Gruppierung. Das Result-Panel ist die zentrale Antwort-Bühne; sowohl Galerie als auch Builder schreiben dorthin.

Die Pivot-Begründung gegen den früheren Slot-Workbench-Ansatz mit Familien-Tab-Bar als oberster UI-Ebene ist in [[decisions#Analyse-Seite mit Frage-Galerie und Custom-Builder]] festgehalten.

### 4.2 Frage als first-class concept

Eine Frage ist eine autonome Datenstruktur:

```
{
  id,                  eindeutiger Schlüssel (Permalink-Anker #q=<id>)
  group,               Gruppierung in der Galerie
  text,                Frage-Text im UI
  dataFiles,           welche Aggregat-JSONs sie konsumiert
  viz,                 welche Visualisierungs-Klasse die Antwort trägt
  answer,              Antwort als Mini-Viz für die Galerie-Karte
  resolveViz,          Resolver für das volle SVG-Rendering im Result-Panel
  resolveComparison,   optional, baut den Vergleichsstand auf
  resolveDrillDown,    optional, baut den Drill-down auf
  coverage             Coverage-Indikator für epistemische Transparenz
}
```

Die Frage ist nicht an eine Familie gebunden. Familien bleiben für den Custom-Builder relevant, sind aber im Galerie-Modus keine Ordnungsebene.

### 4.3 Drei Mini-Viz-Stufen

Galerie-Karten zeigen die Antwort in einer von drei subtilen Stufen, abhängig von der Frage-Form: 6 px gestapelte Bars für Verteilungs-Aufschlüsselungen, 28 px Sparklines für Zeitverläufe, Top-3-Mini-Bars oder 2 × 2 Heatmaps für Vergleiche. Im Result-Panel werden dieselben Daten als vollwertige SVG-Visualisierung wiederholt — beide Stufen teilen sich die Renderer-Logik.

### 4.4 Custom-Builder

Im aufklappbaren `<details>` baut die Nutzerin eine eigene Abfrage aus drei Slots: Subject (Person, Organisation, Event, Quelle), Filter-Set (eine oder mehrere typisierte Filter wie Geschlecht, Rolle, Quellenkorpus, Dekade) und Gruppierung (Dekade, Korpus, Geschlecht, Organisationstyp). Die Slots greifen auf dieselben Aggregat-JSONs zu wie die Galerie-Resolver. Familien 2 bis 5 sind als Galerie-Resolver implementiert, aber im Builder noch nicht durchgängig als Slot-Kombinationen ausgebaut.

### 4.5 Capability-Manifest

Die Brücke zwischen einer (Subject, Filter-Set)-Kombination und den benötigten JSON-Dateien plus Resolver-Funktion lebt in einem deklarativen Capability-Manifest (`analysis-capabilities.js`). Eine neue Frage oder eine neue Slot-Kombination wird durch einen Eintrag im Manifest verfügbar gemacht, ohne dass der Driver oder der Composer angefasst werden müssen.

### 4.6 Permalinks

Permalinks sind doppelt: `#q=<id>` adressiert eine Galerie-Frage, `#f=<fid>&...` adressiert einen Custom-Builder-Stand mit allen Slot-Werten. Beide sind bidirektional serialisiert; ein Custom-Permalink öffnet das `<details>` beim Page-Load automatisch. Ein Permalink-Copy-Knopf liefert die aktuelle URL über die Clipboard-API.

### 4.7 Coverage-Konsolidierung

Eine zentrale COVERAGE-Map konsolidiert die früher vier nahezu identischen Coverage-Funktionen pro Familie. Ein generischer `topN(source, n, opts)`-Helfer ersetzt drei vorher dupizierte `topX`-Helfer. Label-Maps für Rollen, Organisationstypen und Transaktionstypen liegen zentral, nicht pro Frage.

## 5. Provenienz und epistemische Transparenz

### 5.1 Vier Ebenen

**Datensatz-Ebene.** Herkunft der Quellenkorpus: Datenbank, Projekt, beteiligte Institutionen. Zentral verlinkbar.

**Korpus- und Erschließungsform-Ebene.** Jede Aggregation ist nach Korpus und Erschließungsform aufschlüsselbar. Stadtbücher (ausgeschriebener Volltext) und QGW (Regesten plus Faksimile) stützen unterschiedliche Arten von Aussagen.

**Entitäts-Ebene.** Jede Person, Organisation, Ort oder Quelle trägt über die `id` eine eindeutige Identität und ist über `docs_lookup.json` mit den Originalquellen verknüpft (Monasterium-URL, Quellenstelle).

**Query-Ebene.** Unter jedem Ergebnis steht ein kompakter Auszug: verwendete Felder, Zählmodus, zugrunde gelegte Zuordnungstabellen (etwa `categories.json`), herangezogene Korpora.

### 5.2 Ausweisung der Datenqualität

Zahlen aus `quality.json` und aus den `coverage`-Blöcken der Aggregat-JSONs werden neben relevanten Counts als Kontext angezeigt. Eine Zählung von Transaktionstypen weist beispielsweise aus, auf wie vielen normalisierten Events sie beruht und wie viele Events bislang nicht ins kontrollierte Vokabular überführt sind. Eine Zuordnung Person zu Organisation weist die Coverage-Quote der explizit angebundenen Personen aus.

Der Interface-Ton bleibt beschreibend, nicht apologetisch. Die Verhältnisse sind Eigenschaft der Datenbank, nicht Makel des Interfaces.

### 5.3 Drill-Down-Mechanik

Jede Aggregation ist interaktiv. Klick auf eine Aggregat-Zelle (etwa *Zeugen-Nennungen männlich*) öffnet die Liste der Quelldokumente aus `drill_down.role_sex.witness.m`, aufgelöst über `docs_lookup.json` zu einer Liste mit Datum, Kurzregest und Link zur Quelle. Dieser Pfad macht die aggregierte Zahl auf Einzelbelegebene nachprüfbar.

Theoretischer Bezug: Die Offenlegung dieser Übersetzungskette von der Urkunde über Katalogisierung, Annotation, Aggregation und Freigabe bis zur angezeigten Zahl entspricht der Sichtbarmachung von Latours *circulating reference*. Das Interface dokumentiert seine eigene epistemische Infrastruktur.

### 5.4 UI-Komponenten

- Info-Icon neben jeder Aggregation mit Popover (Query-Definition, Zählmodus, herangezogene Felder, Korpora, Coverage-Zahlen, verwendete Zuordnungstabellen).
- Quellenliste bei Drill-Down: Chips mit Kürzel, Datum, Erschließungsform-Markierung, verlinkt.
- Erschließungsform-Breakdown unter jedem Count (Aufteilung Regest- und Volltext-Anteil).
- Export als JSON oder CSV: Query-Spezifikation, Ergebniszahlen, beteiligte Dokument-IDs, Zeitstempel, Versionskennung der Daten.

## 6. Sonderfälle und offene Punkte

### 6.1 Sonderfälle aus dem Datenmodell

`data.md` verweist auf Menschen-Events, deren UI-Behandlung in separaten Dokumenten festgelegt ist. Das Template-System muss konfigurierbar bleiben, damit solche Sonderfälle als eigene Template-Familien ergänzt werden können.

### 6.2 Zu klärende Punkte vor weiterem Ausbau

- Welche Zählmodi sind pro Entitätstyp semantisch zulässig? Nennungen gibt es nur für Register-Entitäten, nicht für Quellen.
- Wie gehen wir mit dem Anteil *unspecified* beim Geschlecht um? Im Datenmodell ist *f*/*m* binär, was die historische Realität vereinfacht und als Modellierungsentscheidung ausgewiesen werden sollte.
- Welche Granularität an Aggregationen über Organisationen ist wissenschaftlich tragbar, angesichts der unterschiedlichen Bearbeitungstiefe von Personen- und Organisationsregister? Detail-Profile sind freigegeben; Aggregationen über Organisationstypen und Eigentumsbeziehungen lassen sich darauf aufbauend ergänzen.
- Wie soll mit der Qualität der Normalisierung umgegangen werden? Vorschlag: Default-Schwellenwert `qw >= 0` (Unbekannt ausgeschlossen), mit Toggle zum Einschluss.

### 6.3 Erweiterungspotenzial

- Volltextsuche auf `search.json` als alternativer Einstieg neben dem Template-Interface.
- Export der Abfragespezifikation als JSON oder CSV zur Weitergabe und Zitation.

Kartenvisualisierung und Netzwerkvisualisierung liegen konzeptionell im Bereich [[exploration]] und werden dort ausgearbeitet.

---

## Zusammenfassung

Der Analysebereich liegt als statisches Frontend ohne Backend vor. Die Aggregat-JSONs liefern vorberechnete Aggregationen mit Drill-down-Listen auf Dokumentenebene, sodass das zentrale UI-Muster (Antwort anzeigen, Herkunft aufschlüsseln, Quellen einsehen) durchgängig trägt. Die Register-Dateien erlauben dynamische Filter in Millisekunden. Die Auswertungen-Sub-Seite bedient filter-getriebene Verteilungen mit Drill-down, die Abfragen-Sub-Seite bedient eine kuratierte Frage-Galerie und einen freien Custom-Builder mit Permalinks und Capability-Manifest. Die Provenienz lebt vierfach: pro Korpus und Erschließungsform, pro Entität, pro Query (Coverage-Kontext) und über das Verifikations-Test-Set.

Mögliche nächste Schritte:

- Die Familien 2 bis 5 als Custom-Builder-Slots ausbauen; aktuell sind sie als Galerie-Resolver implementiert, aber nur Familie 1 ist auch als Slot vollständig.
- Die Zuordnungstabelle `categories.json` für Organisationstypen geistlich/weltlich schreiben und im Team abstimmen, weil sie als Modellierungsentscheidung die späteren Zählungen prägt.
- Korpus-Filter im Builder einführen, sobald die Aggregate eine korpusbasierte Unterschlüsselung tragen.