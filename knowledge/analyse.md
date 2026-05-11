---
title: Analyse
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-02-19
updated: 2026-05-09
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

**Auswertungen** (`/analysis/auswertungen.html`) zeigt vorberechnete Verteilungen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen — jeweils als Donut, Bar-Chart oder Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine Zähleinheit-Umschaltung wechselt zwischen Nennungen und Individuellen Personen. Die Seite ist filter-getrieben: Nutzerinnen ändern Achsen und sehen Verteilungen sich anpassen, ohne eine konkrete Frage formulieren zu müssen. Begründung der Verortung im Analyse-Bereich: [[decisions#Auswertungen gehört in den Analyse-Bereich]].

Jede Aggregat-Zelle ist klickbar und öffnet das [[ui-design#Drill-down-Overlay]] mit den beitragenden Quellen — Donut-Arc und Legend-Item für Funktionsrollen und Beziehungstypen, Bar für Transaktionstypen, Tabellenzeile für Bezeichnungen. Filter werden in den Drill mitgenommen (sex-Suffix im Lookup-Schlüssel, Dekaden-Filter über Datums-Parsing). Im Footer steht der Cross-Page-Sprung in die Quellen-Liste mit übernommenem Zeitraum-und-Geschlecht-Filter ([[ui-design#Cross-Page-Sprung in die Quellen-Liste]]).

Der Filter-Stand wird in die URL serialisiert (`?dec=1300-1380&sex=f&type=kin&q=hausfrau&mode=persons`), siehe [[ui-design#URL-State-Sync]] — damit ist jeder Forschungsstand dieser Seite zitierbar.

**Abfragen** (`/analysis/index.html`) bietet vorgefertigte Fragetypen mit typisierten Slots — der Template-Abfragemodus, dessen Konzept im Folgenden ausführlich beschrieben ist. Nutzerinnen kommen mit einer konkreten Frage und füllen Slots, das Interface beantwortet die Frage als einzelne Zahl plus Drill-down auf die Quellen.

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

Pro Ebene liegt eine eigene JSON vor: Quellen in `search.json` und `docs_lookup.json`, Personen in `persons_search.json`, Organisationen in `orgs_search.json`, vorberechnete Aggregate in `roles.json` (Rollen), `relations.json` (Beziehungen), `transactions.json` (Transaktionen). Detail-Profile pro Entität liegen unter `register/persons/` und `register/orgs/`. Ein Ortsregister gibt es nicht; die Orts-Stammdaten sind noch nicht hinreichend konsolidiert.

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

Das Organisationsregister liegt parallel als `orgs_search.json` vor und nutzt dasselbe Such-Schema wie das Personenregister; zusätzlich trägt jeder Eintrag ein `tp`-Feld für den Typ. Detail-Profile pro Organisation stehen unter `register/orgs/<org__id>.html`. Ein Ortsregister wird derzeit nicht ausgeliefert; Orts-Annotationen im Quellen-Volltext bleiben als Markup sichtbar, tragen aber kein Sprungziel.

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

Der Validierungsreport (`quality.json`) und die Coverage-Blöcke der Aggregat-JSONs machen die Datenqualität sichtbar. Charakteristisch ist eine durchgängig niedrige Normalisierungsrate: nur ein kleiner Teil der dispositiven Verben ist im kontrollierten Vokabular der Transaktionstypen geführt, und nur ein Teil der Personen hat eine explizite Organisationszuordnung. Die Orts-Stammdaten sind im Datenbestand vorhanden, aber nicht hinreichend konsolidiert; aus diesem Grund wird das Ortsregister derzeit nicht ausgeliefert.

Diese Verhältnisse sind keine nebensächliche Meta-Information, sondern konstitutiver Teil dessen, was das Interface ausweisen muss. Eine Zählung *Transaktionen vom Typ Kauf* bedeutet nicht, dass alle anderen Events keine Käufe sind, sondern dass nur ein Bruchteil überhaupt kategorisiert ist.

Nicht alle in der Validierung erscheinenden Korpora sind im UI sichtbar. Die Single-Source-of-Truth für freigegebene Korpora ist `pipeline/config.py::RELEASED_CORPORA` im Schwester-Repo.

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

## 4. Interface-Konzept: Query-Templates mit Slots

### 4.1 Grundstruktur

Ein Template ist ein Satz mit typisierten Lücken. Das generische Template lautet:

> Zeige [Zählmodus] von [Entitätstyp] mit [Eigenschaft] gleich [Wert], gruppiert nach [Dimension].

Der Nutzer füllt die Slots der Reihe nach; jede Auswahl schränkt die möglichen Folgewerte ein. Bei jeder Wahl wird live die resultierende Ergebniszahl angezeigt.

### 4.2 Slot-Typen

**Zählmodus-Slot.** Bestimmt die Zählebene: individuelle Identitäten, Gesamtnennungen, Events, Quellendokumente. Die Unterscheidung ist nicht kosmetisch: *Anzahl Personen mit Rolle Zeuge* (individuell) und *Anzahl Zeugen-Nennungen* (Gesamt) sind verschiedene Zahlen.

**Entitätstyp-Slot.** Geschlossene Liste der im Freigabestand sichtbaren Entitäten: Personen, Organisationen, Orte, Quellen, Events. Welche tatsächlich wählbar sind, hängt am Freigabe-Filter und an der Verfügbarkeit von Aggregationen.

**Eigenschafts-Slot.** Dynamisch abhängig vom Entitätstyp. Für Personen: Geschlecht, Rolle im Event, Beruf, Verwandtschaftsbeziehung, Qualitätsgewicht. Für Organisationen: Typ, Kategorie (geistlich/weltlich). Für Quellen: Korpus, Jahrzehnt, Erschließungsform. Für Events: Transaktionstyp, beteiligter Organisationstyp.

**Wert-Slot.** Tatsächlich vorkommende Werte aus den Daten, mit Count hinter jeder Option.

**Gruppierungs-Slot.** Optional. Bestimmt die Pivot-Dimension: nach Dekade, nach Korpus, nach Organisationstyp, nach Geschlecht. Gibt das Ergebnis nicht als einzelne Zahl, sondern als Tabelle oder Diagramm aus.

**Join-Slot.** Weil Verknüpfungen zwischen Personen und Organisationen über Events laufen, braucht es für Fragen wie *Personen in geistlichen Einrichtungen* einen Slot, der die Verknüpfungsebene explizit macht: *Personen, die an Events mit Organisationen vom Typ [Wert] beteiligt sind, in der Rolle [Wert]*.

### 4.3 Template-Familien (konkrete Startmenge)

Aus den vorhandenen Aggregationen lassen sich unmittelbar fünf Template-Familien ableiten, die ohne zusätzliche Berechnung funktionieren:

**Familie 1: Personenrollen nach Geschlecht.** Basis: `roles.observations.role_by_sex`. Slot-Template: *Anzahl [Nennungen|Personen] in der Rolle [Rolle] mit Geschlecht [Geschlecht]*, optional gruppiert nach Dekade.

**Familie 2: Beteiligung an Organisationstypen.** Basis: `roles.observations.org_type_by_sex` und `org_type_totals`. Slot-Template: *Anzahl [Nennungen|Personen] in Events mit Organisationen vom Typ [Typ] oder Kategorie [geistlich/weltlich], mit Geschlecht [Geschlecht]*, optional gruppiert nach Dekade.

**Familie 3: Rechtsgeschäftstypen.** Basis: `roles.observations.transaction_types` und `transactions.observations.tx_timeline`. Slot-Template: *Anzahl Events vom Typ [Transaktionstyp]*, optional gruppiert nach Dekade oder Empfänger-Organisationstyp.

**Familie 4: Beziehungsstrukturen.** Basis: `relations`. Slot-Template: *Anzahl Beziehungen vom Typ [Verwandtschaft|Beruf|Vertretung|Freundschaft] mit Label [Wert]*, optional gefiltert nach Geschlecht der beteiligten Personen.

**Familie 5: Dokumentenverteilung.** Basis: `timeline.json` und `search.json`. Slot-Template: *Anzahl Quellen im Korpus [Korpus] in der Dekade [Dekade]*.

Die erste konkrete Beispielabfrage aus dem Entwurfsgespräch (*Personen in geistlichen Einrichtungen nach Geschlecht*) realisiert sich als Familie 2 mit Kategorie-Filter *geistlich* und Gruppierung *Geschlecht*. Die resultierenden Zahlen lassen sich direkt aus `roles.observations.org_type_by_sex` ablesen, nach Summierung über die geistlichen Typen gemäß `categories.json`.

### 4.4 Darstellung

Für den ersten Prototyp sind Dropdowns oder Chip-Gruppen pragmatisch. Chips haben den Vorteil, alle Optionen gleichzeitig sichtbar zu machen, was das Datenmodell transparenter erscheinen lässt. Scratch-artige Drag-and-Drop-Blöcke bleiben als spätere Ausbaustufe möglich.

### 4.5 Live-Counts

Neben jeder Slot-Option steht der zugehörige Count, kontextabhängig aktualisiert bei jeder Auswahl. Das verhindert Null-Result-Queries, macht das Datenmodell transparent und gibt Exploration eine haptische Qualität. Quelle der Counts: die jeweils passende Ebene der Aggregat-JSONs.

### 4.6 Globale Filter

Oberhalb der Templates: Korpus (multi-select), Zeitraum (Range innerhalb der freigegebenen Grenzen), Qualitätsgewicht (Schwellenwert für `qw` bei Personen). Diese Filter wirken auf alle Templates parallel.

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

### 6.2 Zu klärende Punkte vor Implementierung

- Welche Zählmodi sind pro Entitätstyp semantisch zulässig? Nennungen gibt es nur für Register-Entitäten, nicht für Quellen.
- Wie gehen wir mit dem Anteil *unspecified* beim Geschlecht um? Im Datenmodell ist *f*/*m* binär, was die historische Realität vereinfacht und als Modellierungsentscheidung ausgewiesen werden sollte.
- Welche Granularität an Auswertungen über Organisationen und Orte ist wissenschaftlich tragbar, angesichts der unterschiedlichen Bearbeitungstiefe der drei Register? Detail-Profile sind freigegeben; Aggregationen über Organisationstypen, Ortstypen und Eigentumsbeziehungen lassen sich darauf aufbauend ergänzen.
- Wie soll mit der Qualität der Normalisierung umgegangen werden? Vorschlag: Default-Schwellenwert `qw >= 0` (Unbekannt ausgeschlossen), mit Toggle zum Einschluss.
- Wie positionieren wir das Interface zwischen *Exploration* (spielerisch, niedrigschwellig) und *Analyse* (nachvollziehbar, zitierfähig)? Beides ist möglich, sollte aber nicht verwechselt werden.

### 6.3 Erweiterungspotenzial

- Volltextsuche auf `search.json` als alternativer Einstieg neben dem Template-Interface.
- Export der Abfragespezifikation als JSON oder CSV zur Weitergabe und Zitation.

Kartenvisualisierung und Netzwerkvisualisierung liegen konzeptionell im Bereich [[exploration]] und werden dort ausgearbeitet.

---

## Zusammenfassung

Der Analysebereich lässt sich auf Basis der vorhandenen JSON-Datenbestände als statisches Frontend ohne Backend umsetzen. Die Aggregat-JSONs liefern bereits vorberechnete Aggregationen mit Drill-Down-Listen auf Dokumentenebene, sodass das zentrale UI-Muster (Zahl anzeigen, Herkunft aufschlüsseln, Quellen einsehen) direkt implementierbar ist. Die Register-Dateien erlauben dynamische Filter in Millisekunden. Die Kategorisierung *geistlich/weltlich* ist als eigene Zuordnungstabelle zu modellieren, da sie im Datenmodell nicht als Eigenschaft vorliegt. Das Interface nutzt Query-Templates mit sechs Slot-Typen (Zählmodus, Entitätstyp, Eigenschaft, Wert, Gruppierung, Join), Live-Counts aus den vorberechneten Aggregationen und Provenienzanzeige auf vier Ebenen inklusive Coverage-Kontext.

Eine konkrete Startmenge von fünf Template-Familien lässt sich ohne zusätzliche Berechnung aus den vorhandenen Aggregationen realisieren: Personenrollen, Organisationsbeteiligungen, Rechtsgeschäftstypen, Beziehungsstrukturen, Dokumentenverteilung.

Mögliche nächste Schritte:

- Die Zuordnungstabelle `categories.json` für Organisationstypen schreiben und im Team abstimmen, weil sie als Modellierungsentscheidung die späteren Zählungen prägt.
- Einen minimalen Prototyp einer Template-Familie (Vorschlag: Familie 2, Organisationsbeteiligungen nach Geschlecht) als Proof of Concept implementieren, um Interaktionsfluss, Live-Counts und Drill-Down an realen Daten zu erproben.