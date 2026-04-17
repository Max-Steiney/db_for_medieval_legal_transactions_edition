# Exploration

Wissensdokument zum Explorationsbereich der Edition. Die Exploration ist der visuell-explorative Zweig der Oberfläche und bedient Nutzerinnen ohne vorab spezifizierte Frage. Sie steht als zweiter gleichberechtigter Zweig neben der [[analyse]] und arbeitet mit offenen Einstiegspunkten, Überblicksdarstellungen und schrittweiser Eingrenzung, nicht mit vordefinierten Abfragekombinationen.

Die konzeptionelle Entscheidung für die Trennung von Exploration und Analyse liegt in [[decisions#Exploration und Analyse als getrennte Bereiche]]. Die beiden Modi widersprechen sich nicht, sondern decken unterschiedliche Forschungssituationen ab und nutzen teilweise dieselben Aggregate auf unterschiedliche Weise.

## Zielsetzung

Die Exploration erlaubt Nutzerinnen, sich einem Teilbestand anzunähern, ohne zu wissen, welche Frage sie an ihn stellen werden. Sie macht Strukturen des Korpus sichtbar, die nicht Gegenstand gezielter Abfragen sind, und bietet einen niedrigschwelligen Einstiegspunkt für die qualitative Lektüre. Typische Bewegungen sind:

- Ein Blick auf die Verteilung einer Dimension (etwa Rollen, Geschlechter, Transaktionstypen) über das gesamte Korpus.
- Eine Filterung dieser Verteilung auf einen Teilbestand, einen Zeitraum oder eine Entitätsklasse.
- Ein Drill-down auf die Quellen, die eine bestimmte Aggregat-Zelle tragen.

Das Muster ist dasselbe für alle vier Sub-Seiten: aggregierte Übersicht, interaktive Filter, Drill-down auf Einzelbelegebene. Die [[ui-design#Provenienz-Tooltip]]-Komponente macht die Herkunft jeder gezeigten Zahl an Ort und Stelle einsehbar.

## Die vier Sub-Seiten

Die Exploration gliedert sich in vier thematische Sub-Seiten, die jeweils eine zentrale Dimension der Datenbasis tragen. Die Zuordnung ist nicht disjunkt: eine Person hat Rollen, steht in Beziehungen, trägt zu Transaktionen bei und ist mit Orten verknüpft. Die Sub-Seiten unterscheiden sich darin, welche Dimension sie zum primären Zugang machen.

### Rollen

Einstieg über die Funktion, in der Personen in Rechtsgeschäften auftreten. Das kontrollierte Rollenvokabular (siehe [[glossar#Rolle]]) liefert die Primärachse. Gesicherte Achsen sind Geschlecht und Zeitraum; sekundär steht die institutionelle Zugehörigkeit (Organisationstyp).

Datenquelle: `epic_a.json` mit den Kreuztabellen `role_by_sex`, `org_type_by_sex`, `transaction_types` sowie dem zugehörigen `drill_down`-Abschnitt auf `file_key`-Ebene.

Typische Fragen: „In welchen Rollen treten Frauen in Stadtbüchern auf?", „Wie verteilt sich die Rolle *sealer or witness* nach Jahrzehnt?", „Welche Organisationstypen stellen welche Rollenanteile?".

### Beziehungen

Einstieg über annotierte Verbindungen zwischen Personen: Verwandtschaft, Beruf, Vertretung, Freundschaft. Die Sub-Seite macht Netzwerkstrukturen und Geschlechter-Asymmetrien in diesen Beziehungstypen sichtbar.

Datenquelle: `epic_b.json` mit den Kantenlisten und ihrer Klassifikation. Die Zählung auf Personenebene bleibt quellenbereinigt (siehe [[decisions#Quellenbereinigte Zählung]]).

Typische Fragen: „Wie oft treten Ehepaare gemeinsam als Aussteller auf?", „Wie verteilen sich berufliche Beziehungen im Zeitverlauf?", „Welche Freundschaftsbeziehungen überspannen Bestandsgrenzen?".

### Transaktionen

Einstieg über das Repertoire der Rechtsgeschäfte: Transaktionstypen, dispositive Verbformen, Empfänger-Organisationstypen. Die Sub-Seite macht sichtbar, welche Handlungsformen das Korpus dokumentiert und wie sie sich über die Zeit verändern.

Datenquelle: `epic_c.json` mit `tx_timeline`, der Verbform-Normalisierungstabelle und Empfänger-Aggregaten. Eine Coverage-Angabe weist den Normalisierungsgrad aus.

Typische Fragen: „Wann setzt die Schenkungspraxis an geistliche Empfänger ein?", „Welche Verbformen werden noch nicht in das kontrollierte Vokabular normalisiert?", „Wie verschiebt sich das Typenprofil zwischen Regest- und Volltext-Beständen?".

### Orte

Einstieg über das Einzugsgebiet der Rechtsgeschäfte. Neben einer Siedlungskarte steht ein vollständiges Ortsregister mit Referenzierungs- und Georeferenzierungsstatus.

Datenquelle: `epic_d.json` mit `places` und deren `file_keys`, sowie `places_search.json` für das tabellarische Register. Nicht alle Orte sind georeferenziert; die Sub-Seite weist beide Zahlen (referenziert und georeferenziert) separat aus.

Typische Fragen: „Welche Siedlungen außerhalb Wiens erscheinen besonders häufig?", „Welche Orte tauchen nur in den Stadtbüchern auf?", „Wo liegen die georeferenzierten Lücken?".

## Gemeinsames Muster: Überblick → Filter → Drill-down

Jede Sub-Seite hält drei Ebenen:

1. **Überblick** — aggregierte Zahlen als Kacheln, Balken, Karten oder Listen. Die Aggregate stammen aus den vorkompilierten `epic_*.json` und sind ohne weitere Berechnung abrufbar.
2. **Filter** — global angewandt auf die Überblicksdarstellung. Minimalausstattung: Zeitraum, Quellenkorpus. Sub-Seiten-spezifisch kommen hinzu: Geschlecht (Rollen, Beziehungen), Organisationstyp (Rollen, Transaktionen), Beziehungstyp (Beziehungen), Ort-Klasse (Orte).
3. **Drill-down** — Klick auf eine Aggregat-Zelle öffnet ein Overlay mit den beitragenden Quellen. Die `file_key`-Listen kommen aus dem `drill_down`-Abschnitt des jeweiligen `epic_*.json`, aufgelöst über `data/docs_lookup.json`.

Die Drill-down-Komponente ist eine gemeinsame UI-Infrastruktur (siehe [[architecture#Provenienz-Indizes]]).

## Zusammenspiel mit Phase-2-Komponenten

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
