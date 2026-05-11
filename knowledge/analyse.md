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

Der Analysebereich versammelt die quantitativen Zugänge zur Datenbasis. Er steht als gleichberechtigter Zweig neben der [[exploration]]: das Interaktionsmuster ist strukturiert (vorgegebene Achsen, exakte Zahlen, Provenienz), die Exploration arbeitet visuell-interaktiv. Begründung der Trennung in [[decisions#Exploration und Analyse als getrennte Bereiche]].

## Zwei Sub-Seiten

**Auswertungen** (`/analysis/auswertungen.html`) zeigt vorberechnete Verteilungen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen — jeweils als Donut, Bar-Chart oder Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine Zähleinheit-Umschaltung in der Funktionsrollen-Sektion wechselt lokal zwischen Nennungen und Individuellen Personen. Die Seite ist filter-getrieben — Nutzerinnen ändern Achsen und sehen Verteilungen sich anpassen. Begründung der Verortung in [[decisions#Auswertungen gehört in den Analyse-Bereich]].

Jede Aggregat-Zelle ist klickbar und öffnet das [[ui-design#Drill-down-Overlay]] mit den beitragenden Quellen — Donut-Arc und Legend-Item für Funktionsrollen und Beziehungstypen, Bar für Transaktionstypen, Tabellenzeile für Bezeichnungen. Im Footer steht der Cross-Page-Sprung in die Quellen-Liste mit übernommenem Zeitraum-und-Geschlecht-Filter ([[ui-design#Cross-Page-Sprung in die Quellen-Liste]]). Der Filter-Stand wird in die URL serialisiert, damit jeder Forschungsstand zitierbar ist ([[ui-design#URL-State-Sync]]).

**Abfragen** (`/analysis/index.html`) bedient zwei Einstiegsmodi nebeneinander: eine kuratierte Galerie konkreter Forschungsfragen als oberste Ebene, ein freier Custom-Builder darunter im aufklappbaren `<details>`. Architektur und Pivot-Begründung in [[decisions#Analyse-Seite mit Frage-Galerie und Custom-Builder]].

Beide Sub-Seiten teilen sich dieselben Aggregate (`roles.json`, `relations.json`, `transactions.json`) und dieselben Filter-Bausteine in der Sidebar. Eine Filteränderung auf der einen Seite überträgt sich nicht automatisch auf die andere; das ist eine offene Designfrage.

## Zielsetzung

Der Analysebereich soll Nutzerinnen erlauben, konkrete inhaltliche Fragen an den Datenbestand zu stellen, ohne SQL, SPARQL oder vergleichbare Query-Sprachen lernen zu müssen. Statt beliebiger Abfragen werden vorgefertigte Fragetypen angeboten, die über typisierte Slots angepasst werden. Das konzeptionelle Vorbild ist die komponierbare Logik von Scratch, übersetzt in ein domänenspezifisches Vokabular für Urkundenforschung.

Typische Beispielfragen:

- Wie viele geistliche Einrichtungen sind im Datenbestand belegt?
- Wie verteilen sich die Beteiligten an Rechtsgeschäften nach Geschlecht?
- Welche Rechtsgeschäftstypen treten in welchem Zeitraum auf?
- In welchen Rollen treten Frauen in Stadtbüchern auf?

## Datenbestand

Pro Ebene liegt eine eigene JSON vor: Quellen in `search.json` und `docs_lookup.json`, Personen in `persons_search.json`, Organisationen in `orgs_search.json`, vorberechnete Aggregate in `roles.json`, `relations.json` und `transactions.json`. Detail-Profile pro Entität liegen unter `register/persons/` und `register/orgs/`.

Die Aggregat-JSONs enthalten vorberechnete Kreuztabellen mit Drill-Down-Listen auf Dokumentenebene und sind dreigeteilt: `meta` (Schema, Dimensionen, Quellen), `observations` (Kreuztabellen), `drill_down` (Listen von Dokument-IDs pro Zelle) und `coverage` (Gesamtsummen und Datenqualitäts-Indikatoren). Das ermöglicht das einheitliche UI-Muster *aggregierte Zahl anzeigen, bei Klick Quelldokumente auflisten, über `docs_lookup.json` zu Metadaten auflösen*.

Das Personenregister liegt als flaches Array mit kompakten Feldnamen vor (Kennung, Namensform, Vor- und Familienname, Geschlecht, Datierung, Quellen-Count, Qualitätsgewicht). Das Organisationsregister nutzt dasselbe Schema mit zusätzlichem Typ-Feld. Orts-Annotationen im Quellen-Volltext bleiben als Inline-Markup sichtbar, tragen aber kein Sprungziel und kein eigenes Register.

### Organisationstypen als Klassifikationsbasis

Das `tp`-Feld des Organisationsregisters führt eine geschlossene Typologie. Die Kategorie geistlich/weltlich liegt nicht als eigene Eigenschaft vor und muss über eine versionierte Zuordnungstabelle erzeugt werden. Im Interface ist die verwendete Zuordnung aufrufbar und zitierbar. Grenzfälle (Zeche/Bruderschaft, Spital/Siechenhaus) sind als solche ausweisbar.

### Datenqualität und Freigabestand

Der Validierungsreport (`quality.json`) und die `coverage`-Blöcke der Aggregat-JSONs machen die Datenqualität sichtbar. Charakteristisch ist eine durchgängig niedrige Normalisierungsrate. Diese Verhältnisse sind keine nebensächliche Meta-Information: eine Zählung *Transaktionen vom Typ Kauf* bedeutet nicht, dass alle anderen Events keine Käufe sind, sondern dass nur ein Bruchteil überhaupt kategorisiert ist.

Single Source of Truth für die freigegebenen Korpora ist `RELEASED_CORPORA` im Schwester-Repo (`pipeline/config.py`); der Zeitraum lebt als `RELEASED_PERIOD` im Frontend-Repo (`frontend/config.py`). Hardcoded Werte in Templates sind ein Fehler.

## Technische Architektur

Zwei Laufzeit-Schichten tragen die Analyse-Seiten. Die **Aggregations-Schicht** liest vorberechnete Kreuztabellen aus den Aggregat-JSONs. Die **Filter-Schicht** kombiniert oder verfeinert dynamisch, indem sie die Register-Arrays zur Laufzeit filtert. Die **Drill-Down-Schicht** verknüpft jede Aggregat-Zelle mit einer Liste von Dokument-IDs, aufgelöst über `docs_lookup.json` — Klick-zu-Quellen ohne zusätzliches Nachladen.

Eine SPARQL-Engine im Browser (Comunica, Oxigraph WASM) wäre möglich, ist aber methodisch nicht gerechtfertigt: die Aggregationen liegen vorberechnet vor, der Engine-Overhead wäre Selbstzweck.

## Frage-Galerie und Custom-Builder

Die Abfragen-Sub-Seite hat zwei Einstiegsmodi nebeneinander. Die kuratierte **Frage-Galerie** liegt oben und zeigt konkrete Forschungsfragen als Karten mit Frage-Text, Antwort als Mini-Visualisierung und Kontext-Zahlen. Der **Custom-Builder** liegt darunter im aufklappbaren `<details>` und erlaubt das freie Zusammenstellen einer Abfrage über Subject, Filter-Set und Gruppierung. Das Result-Panel ist die zentrale Antwort-Bühne; sowohl Galerie als auch Builder schreiben dorthin.

### Frage als first-class concept

Eine Frage ist eine autonome Datenstruktur mit Frage-Text, benötigten Datenquellen, Visualisierungs-Klasse, einer Mini-Viz für die Galerie-Karte, einem Resolver für das volle SVG-Rendering und einem Coverage-Indikator für epistemische Transparenz. Die Frage ist nicht an eine Familie gebunden; Familien bleiben für den Custom-Builder relevant.

### Mini-Viz-Stufen

Galerie-Karten zeigen die Antwort in subtilen Mini-Visualisierungen, abhängig von der Frage-Form: gestapelte Bars für Verteilungen, Sparklines für Zeitverläufe, Top-N-Mini-Bars oder kleine Heatmaps für Vergleiche. Im Result-Panel werden dieselben Daten als vollwertige SVG-Visualisierung wiederholt — beide Stufen teilen sich die Renderer-Logik.

### Custom-Builder

Im aufklappbaren `<details>` baut die Nutzerin eine eigene Abfrage aus drei Slots: Subject (Person, Organisation, Event, Quelle), Filter-Set (typisierte Filter wie Geschlecht, Rolle, Quellenkorpus, Dekade) und Gruppierung (Dekade, Korpus, Geschlecht, Organisationstyp). Einige Resolver sind als Galerie-Antwort fertig, aber noch nicht als Slot-Kombination im Builder ausgebaut.

### Capability-Manifest

Die Brücke zwischen einer (Subject, Filter-Set)-Kombination und den benötigten JSON-Dateien plus Resolver-Funktion lebt in einem deklarativen Capability-Manifest (`analysis-capabilities.js`). Eine neue Frage oder Slot-Kombination wird durch einen Eintrag im Manifest verfügbar, ohne dass der Driver oder der Composer angefasst werden müssen.

### Permalinks

Permalinks sind doppelt: `#q=<id>` adressiert eine Galerie-Frage, `#f=<fid>&...` adressiert einen Custom-Builder-Stand mit allen Slot-Werten. Beide sind bidirektional serialisiert; ein Custom-Permalink öffnet das `<details>` beim Page-Load automatisch.

## Provenienz und epistemische Transparenz

Die Provenienz lebt auf vier Ebenen:

- **Datensatz-Ebene.** Herkunft des Quellenkorpus: Datenbank, Projekt, Institutionen.
- **Korpus- und Erschließungsform-Ebene.** Jede Aggregation ist nach Korpus und Erschließungsform aufschlüsselbar. Volltext und Regest plus Faksimile stützen unterschiedliche Arten von Aussagen.
- **Entitäts-Ebene.** Jede Person, Organisation oder Quelle trägt eine eindeutige `id` und ist über `docs_lookup.json` mit den Originalquellen verknüpft.
- **Query-Ebene.** Unter jedem Ergebnis steht der verwendete Zählmodus, die herangezogenen Felder und Korpora sowie die zugrunde gelegten Zuordnungstabellen.

Drill-down-Mechanik und Provenienz-Indizierung in [[architecture#Provenienz-Indizes]], UI-Ausprägung in [[ui-design#Provenienz-Tip und Glossar-Tip]] und [[ui-design#Drill-down-Overlay]]. Die Coverage-Blöcke machen Datenqualität sichtbar, ohne apologetisch zu werden — die Verhältnisse sind Eigenschaft der Datenbank, nicht Makel des Interfaces. Theoretischer Bezug: die Offenlegung der Übersetzungskette von der Urkunde bis zur angezeigten Zahl entspricht der Sichtbarmachung von Latours *circulating reference*.

## Offene Punkte

- Welche Zählmodi sind pro Entitätstyp semantisch zulässig? Nennungen gibt es nur für Register-Entitäten, nicht für Quellen.
- Wie gehen wir mit dem Anteil *unspecified* beim Geschlecht um? Das binäre `f`/`m`-Modell ist eine Vereinfachung der historischen Realität und sollte als Modellierungsentscheidung ausgewiesen werden.
- Welche Granularität an Aggregationen über Organisationen ist wissenschaftlich tragbar? Detail-Profile sind freigegeben; Aggregationen über Organisationstypen und Eigentumsbeziehungen lassen sich darauf aufbauend ergänzen.
- Volltextsuche auf `search.json` als alternativer Einstieg neben dem Frage-Interface.
- Export der Abfragespezifikation als JSON oder CSV zur Weitergabe und Zitation.

Menschen-Events sind ein Sonderfall des Datenmodells (Definition in [[glossar#Menschen-Event]]). Personen-Annotationen in verschachtelten Events werden nicht doppelt gezählt, siehe [[decisions#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]]. Kartenvisualisierungen und Netzwerk-Visualisierungen liegen konzeptionell im Bereich [[exploration]].
