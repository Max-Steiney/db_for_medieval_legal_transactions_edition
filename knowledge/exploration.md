# Exploration

Wissensdokument zum Explorationsbereich der Edition. Die Exploration ist der visuell-explorative Zweig der Oberfläche und bedient Nutzerinnen ohne vorab spezifizierte Frage. Sie steht als zweiter gleichberechtigter Zweig neben der [[analyse]] und arbeitet mit offenen Einstiegspunkten, Überblicksdarstellungen und schrittweiser Eingrenzung, nicht mit vordefinierten Abfragekombinationen.

Die konzeptionelle Entscheidung für die Trennung von Exploration und Analyse liegt in [[decisions#Exploration und Analyse als getrennte Bereiche]]. Die beiden Modi widersprechen sich nicht, sondern decken unterschiedliche Forschungssituationen ab und nutzen teilweise dieselben Aggregate auf unterschiedliche Weise.

## Zielsetzung

Die Exploration erlaubt Nutzerinnen, sich einem Teilbestand anzunähern, ohne zu wissen, welche Frage sie an ihn stellen werden. Sie macht Strukturen des Korpus sichtbar, die nicht Gegenstand gezielter Abfragen sind, und bietet einen niedrigschwelligen Einstiegspunkt für die qualitative Lektüre. Typische Bewegungen sind:

- Ein Blick auf die Verteilung einer Dimension (etwa Rollen, Geschlechter, Transaktionstypen) über das gesamte Korpus.
- Eine Filterung dieser Verteilung auf einen Teilbestand, einen Zeitraum oder eine Entitätsklasse.
- Ein Drill-down auf die Quellen, die eine bestimmte Aggregat-Zelle tragen.

Das Muster ist dasselbe für alle vier Sub-Seiten: aggregierte Übersicht, interaktive Filter, Drill-down auf Einzelbelegebene. Die [[ui-design#Provenienz-Tip und Glossar-Tip]]-Komponente macht die Herkunft jeder gezeigten Zahl an Ort und Stelle einsehbar.

## Visualisierungs-Prinzipien

Vier Prinzipien tragen alle Sub-Seiten gleichermaßen.

**Transparenz.** Jede Visualisierung deklariert ihre Datengrundlage, ihre Coverage-Quote und ihre Unsicherheiten. Fehlende oder unsichere Werte erscheinen als eigene Kategorie, nicht als stillschweigende Auslassung.

**Rückverfolgbarkeit.** Jeder aggregierte Datenpunkt erlaubt Drill-down auf die zugrundeliegenden Quellen. Direkte Referenzen (`rs/@ref`) und indirekte Referenzen (`@corresp`) führen beide in die Detailansicht; der Referenz-Typ wird ausgewiesen.

**Wiederverwendbarkeit.** Aggregierte und Register-Daten sind mit Metadaten exportierbar. Quellen und Register-Einträge tragen stabile Referenzen für Zitation.

**Eine Sub-Seite, eine Visualisierung.** Jede Sub-Seite ist eine zusammenhängende interaktive Visualisierung aus mehreren Panels, die einen gemeinsamen Filterkontext teilen. Eine Filteränderung in einem Panel wirkt auf alle Panels derselben Sub-Seite.

## Zwei Normalisierungs-Systeme

Zwei unabhängige Normalisierungs-Systeme prägen die Sub-Seiten Rollen und Transaktionen.

Die **Transaktionstyp-Normalisierung** wirkt auf das dispositive Verb des Rechtsgeschäfts (verkaufen, schenken, verleihen). Sie betrifft die Transaktions-Sub-Seite und den Transaktionstyp-Filter überall sonst. Die Coverage-Quote ist niedrig: ein erheblicher Teil der Verben ist noch nicht in das kontrollierte Vokabular überführt.

Die **Funktions-Normalisierung** wirkt auf die Rolle, in der eine Person an einem Event beteiligt ist (Aussteller, Empfänger, Zeuge). Sie operiert auf einer eigenen Liste von Triggerstrings. Die Coverage-Quote unterscheidet sich von der Transaktionstyp-Normalisierung — beide Systeme dürfen nicht zu einer Kennzahl zusammengezogen werden, weil sie analytisch verschiedene Fragen beantworten. Jede Coverage-Angabe nennt das System, auf das sie sich bezieht.

## Die vier Sub-Seiten

Die Exploration gliedert sich in vier thematische Sub-Seiten, die jeweils eine zentrale Dimension der Datenbasis tragen. Die Zuordnung ist nicht disjunkt: eine Person hat Rollen, steht in Beziehungen, trägt zu Transaktionen bei und ist mit Orten verknüpft. Die Sub-Seiten unterscheiden sich darin, welche Dimension sie zum primären Zugang machen.

### Rollen

Einstieg über die Funktion, in der Personen in Rechtsgeschäften auftreten. Das kontrollierte Rollenvokabular (siehe [[glossar#Rolle]]) liefert die Primärachse. Gesicherte Achsen sind Geschlecht und Zeitraum; sekundär steht die institutionelle Zugehörigkeit (Organisationstyp).

Datenquelle: `epic_a.json` mit den Kreuztabellen `role_by_sex`, `org_type_by_sex`, `transaction_types` sowie dem zugehörigen `drill_down`-Abschnitt auf `file_key`-Ebene.

Typische Fragen: „In welchen Rollen treten Frauen in Stadtbüchern auf?", „Wie verteilt sich die Rolle *sealer or witness* nach Jahrzehnt?", „Welche Organisationstypen stellen welche Rollenanteile?".

### Beziehungen

Einstieg über annotierte Verbindungen zwischen Personen: Verwandtschaft, Beruf, Vertretung, Freundschaft. Die Sub-Seite macht Netzwerkstrukturen und Geschlechter-Asymmetrien in diesen Beziehungstypen sichtbar.

Datenquelle: `epic_b.json` mit den Kantenlisten und ihrer Klassifikation. Die Zählung auf Personenebene bleibt quellenbereinigt (siehe [[decisions#Quellenbereinigte Zählung]]).

Die zugrundeliegende **Co-Occurrence-Definition** ist enger als reines Auftreten in derselben Quelle: zwei Personen ko-okkurrieren, wenn sie im selben `<rs type="event">` annotiert sind, also Beteiligte desselben Rechtsgeschäfts. Damit zählen Zeugenreihen und Urteilslisten nicht als eine einzelne Beziehung. Die Frequenz zwischen zwei Personen ist die Anzahl der gemeinsamen Events.

Statt eines kraftgerichteten Netzwerks zeigt die Sub-Seite eine Beziehungs-Heatmap mit gruppierten Balken (Beziehungstyp × Geschlecht) und einer paginierten Label-Heatmap (Beziehungslabel × Typkategorie). Begründung: Die meisten Co-Occurrence-Kanten haben Gewicht 1 — ein Strukturartefakt der Urkundenform, kein analytisch belastbares Beziehungsmaß. Eine Force-Layout-Darstellung würde bei Korpus-Größenordnung als unleserliches „Knäuel" erscheinen. Die Heatmap konzentriert sich auf das, was die TEI-Annotation explizit aussagt: die sechs annotierten Beziehungstypen.

Typische Fragen: „Wie oft treten Ehepaare gemeinsam als Aussteller auf?", „Wie verteilen sich berufliche Beziehungen im Zeitverlauf?", „Welche Freundschaftsbeziehungen überspannen Bestandsgrenzen?".

### Transaktionen

Einstieg über das Repertoire der Rechtsgeschäfte: Transaktionstypen, dispositive Verbformen, Empfänger-Organisationstypen. Die Sub-Seite macht sichtbar, welche Handlungsformen das Korpus dokumentiert und wie sie sich über die Zeit verändern.

Datenquelle: `epic_c.json` mit `tx_timeline`, der Verbform-Normalisierungstabelle und Empfänger-Aggregaten. Eine Coverage-Angabe weist den Normalisierungsgrad aus.

Typische Fragen: „Wann setzt die Schenkungspraxis an geistliche Empfänger ein?", „Welche Verbformen werden noch nicht in das kontrollierte Vokabular normalisiert?", „Wie verschiebt sich das Typenprofil zwischen Regest- und Volltext-Beständen?".

### Orte

Einstieg über das Einzugsgebiet der Rechtsgeschäfte. Neben einer Siedlungskarte steht ein vollständiges Ortsregister mit Referenzierungs- und Georeferenzierungsstatus.

Datenquelle: `epic_d.json` mit `places` und deren `file_keys`. Nicht alle Orte sind georeferenziert; die Sub-Seite weist beide Zahlen (referenziert und georeferenziert) separat aus.

Typische Fragen: „Welche Siedlungen außerhalb Wiens erscheinen besonders häufig?", „Welche Orte tauchen nur in den Stadtbüchern auf?", „Wo liegen die georeferenzierten Lücken?".

## Gemeinsames Muster: Überblick → Filter → Drill-down

Jede Sub-Seite hält drei Ebenen:

1. **Überblick** — aggregierte Zahlen als Kacheln, Balken, Karten oder Listen. Die Aggregate stammen aus den vorkompilierten `epic_*.json` und sind ohne weitere Berechnung abrufbar.
2. **Filter** — global angewandt auf die Überblicksdarstellung. Minimalausstattung: Zeitraum, Quellenkorpus. Sub-Seiten-spezifisch kommen hinzu: Geschlecht (Rollen, Beziehungen), Organisationstyp (Rollen, Transaktionen), Beziehungstyp (Beziehungen), Ort-Klasse (Orte).
3. **Drill-down** — Klick auf eine Aggregat-Zelle öffnet ein Overlay mit den beitragenden Quellen. Die `file_key`-Listen kommen aus dem `drill_down`-Abschnitt des jeweiligen `epic_*.json`, aufgelöst über `data/docs_lookup.json`.

Die Drill-down-Komponente ist eine gemeinsame UI-Infrastruktur (siehe [[architecture#Provenienz-Indizes]]).

## Filterlogik und Anfangszustand

Eine Filteränderung in einer Sub-Seite wirkt auf alle Panels derselben Sub-Seite gleichzeitig. Anklickbare Elemente (Balken, Heatmap-Zelle, Karten-Marker) tragen einen Hover-Zustand und einen Cursor-Wechsel; ein Klick führt entweder in eine Detailansicht oder in das Drill-down-Overlay.

Der Anfangszustand ist konsequent neutral: voller Zeitraum, keine Filter, kein vorausgewähltes Element. Eine Vorauswahl würde redaktionell wirken — einer einzelnen Person, einem einzelnen Ort eine Sonderstellung geben, die in den Daten so nicht angelegt ist.

Die Übergänge zwischen den Sub-Seiten sind möglich, wo die Daten sie tragen. Aus den Rollen kann man eine Person ins Beziehungsnetzwerk übernehmen; aus den Transaktionen kann ein Empfänger-Ort auf der Karte erscheinen; aus den Orten lassen sich die Transaktionen vor Ort öffnen. Cross-Navigations-Punkte erscheinen nur, wenn die Daten sie stützen.

## Zusammenspiel mit übergreifenden Komponenten

- **[[ui-design#Zählebenen-Umschalter]]** greift in allen vier Sub-Seiten. Personenzählung wechselt zwischen [[glossar#Gesamtnennung|Gesamtnennungen]] und [[glossar#Individuelle Person|Individuellen Personen]] konsistent.
- **[[ui-design#Menschen-Events-Toggle]]** wirkt primär auf Rollen und Beziehungen, indirekt auf Transaktionen. Der Status ist im Provenienz-Tooltip jeder Zahl sichtbar.
- **[[ui-design#Bestandsfilter]]** ist universell und gilt auch hier. Die Aggregate in den `epic_*`-Dateien müssen zur Unterschlüsselung nach Quellenkorpus vorbereitet sein, damit clientseitige Filterung auf Teilbestände funktioniert.

## Abgrenzung zur Analyse

Die Exploration endet, wo eine Nutzerin eine konkrete, in der Datenbank typische Frage stellt. Ab diesem Punkt setzt die [[analyse]] an: dort werden Abfragekombinationen als Template direkt aufgerufen, Ergebnisse erscheinen als einzelne Zahl mit Provenienz und Drill-down. Die Exploration bleibt als Einstiegspunkt erhalten, auch wenn eine Fragestellung schließlich in einer Analyse-Abfrage mündet.

## Siehe auch

- [[analyse]] der zweite Zweig: gezielte Abfragen mit Template-Familien
- [[requirements]] Anforderungen, die beide Zweige erfüllen müssen
- [[ui-design]] gemeinsame Komponenten
- [[data]] die Datenbasis, die beide Zweige bedienen
