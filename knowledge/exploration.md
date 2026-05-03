# Exploration

Wissensdokument zum Explorationsbereich der Edition. Die Exploration ist der visuell-interaktive Zweig der Oberfläche und bedient Nutzerinnen ohne vorab spezifizierte Frage. Sie steht als zweiter gleichberechtigter Zweig neben der [[analyse]] und arbeitet mit Information-Visualisation, nicht mit vorgegebenen Auswertungsachsen.

Die konzeptionelle Trennung ist in [[decisions#Exploration und Analyse als getrennte Bereiche]] festgehalten. Erste implementierte Sub-Seite ist der **Zeitstrom** unter `/exploration/zeitstrom.html`; weitere visuelle Zugänge (Personen-Netzwerk, Karten, Sankey) sind konzipiert. Die quantitativen Verteilungen (frühere „Auswertungen") gehören inhaltlich zur [[analyse]] und wurden dorthin verschoben. Siehe [[decisions#Auswertungen gehört in den Analyse-Bereich]].

## Zielsetzung

Die Exploration erlaubt Nutzerinnen, sich der Datenstruktur visuell anzunähern, ohne zu wissen, welche Frage sie an sie stellen werden. Sie macht qualitative Strukturen des Korpus sichtbar, die in einer Verteilungstabelle nicht erkennbar wären — etwa die Topologie eines Personennetzwerks, die geografische Streuung von Rechtsgeschäften oder die zeitliche Verdichtung von Korrespondenzen. Der typische Einstieg ist visuell, nicht quantitativ.

## Abgrenzung zur Analyse

Während die [[analyse]] vorgegebene Achsen bedient (Zeitraum, Geschlecht, Rolle, Transaktionstyp) und Verteilungen entlang dieser Achsen zeigt, lässt die Exploration die Nutzerin frei navigieren. Sie tauscht strukturierte Lesbarkeit gegen offene Sichtbarkeit. Beide Bereiche teilen sich dieselben Aggregate (`epic_*.json`) und dieselben Filter-Bausteine, unterscheiden sich aber radikal im Interaktionsmodus: Analyse arbeitet mit Filtern und liest aus Tabellen ab, Exploration arbeitet mit Hovern, Zoomen, Selektieren auf einer interaktiven Visualisierung.

## Sub-Seiten

Jede Sub-Seite ist eine eigenständige Visualisierung mit eigener Mechanik.

### Zeitstrom (vorhanden)

Gestapelter Bar-Chart der Quellendichte pro Jahrzehnt. Die Stapel-Achse ist umschaltbar zwischen Quellenkorpus, Erschließungsform, Geschlecht der Beteiligten und Transaktionstyp; der Zeitraum-Slider in der Sidebar limitiert die sichtbaren Jahrzehnte; ein Brush per Maus-Drag über mehrere Spalten öffnet die Liste der enthaltenen Quellen direkt darunter.

Datenquellen: `data/search.json` (für die ersten drei Stapel-Achsen), `data/epic_c.json::observations.tx_timeline` (für die Transaktionstyp-Stapelung). Die Drill-down-Liste verlinkt direkt in die Quellen-Detailseiten.

Pattern, das die Sub-Seite trägt: Überblick → Brush → Quellen. Sie ergänzt die [[analyse#Auswertungen|Auswertungen]] um eine zeitlich-visuelle Erkundung — wer dort liest, dass Stiftungen ab den 1340ern zunehmen, kann hier sehen, in welchen Jahrzehnten die belegende Quellendichte trägt.

### Personen-Netzwerk (geplant)

Force-Layout über das Co-Occurrence-Netzwerk der Personen, gefiltert nach Beziehungstyp (Verwandtschaft, Beruf, Vertretung, Freundschaft). Die zugrundeliegende **Co-Occurrence-Definition** ist enger als reines Auftreten in derselben Quelle: zwei Personen ko-okkurrieren, wenn sie im selben `<rs type="event">` annotiert sind, also Beteiligte desselben Rechtsgeschäfts. Damit zählen Zeugenreihen und Urteilslisten nicht als eine einzelne Beziehung. Die Frequenz zwischen zwei Personen ist die Anzahl der gemeinsamen Events.

Die Visualisierung ist auf eine händische Auswahl-Strategie angewiesen, weil die meisten Co-Occurrence-Kanten Gewicht 1 haben — ein Strukturartefakt der Urkundenform, kein analytisch belastbares Beziehungsmaß. Eine Force-Layout-Darstellung über das Gesamtkorpus würde als unleserliches „Knäuel" erscheinen. Sinnvolle Filter-Strategien: Beschränkung auf eine Personenauswahl mit gemeinsamem Bestand, Beschränkung auf Beziehungstyp, Beschränkung auf Mindestkantengewicht.

### Karten-Visualisierung (geplant)

Geografische Verteilung der dokumentierten Orte mit Drill-down auf die zugehörigen Quellen. Voraussetzung ist die Freigabe des Ortsregisters mit Georeferenzierung. Aktuell ist nur ein Bruchteil der Orts-Einträge mit Koordinaten versehen; die Karte muss diesen Coverage-Stand sichtbar machen. Geplant ist Clustering nach Dichte, Zeitraum-Filter mit animierter Slider-Bewegung, Klick auf einen Marker führt zur Quellenliste.

### Sankey-Diagramm der Transaktionen (geplant)

Fluss-Visualisierung von Personen oder Organisationstypen zu Transaktionstypen zu Empfängern. Geeignet, um typische Transaktions-Muster („geistliche Empfänger erhalten überwiegend Stiftungen") visuell sichtbar zu machen, ohne sie als Hypothese vorab zu formulieren.

## Visualisierungs-Prinzipien

Vier Prinzipien tragen alle künftigen Sub-Seiten gleichermaßen.

**Transparenz.** Jede Visualisierung deklariert ihre Datengrundlage, ihre Coverage-Quote und ihre Unsicherheiten. Fehlende oder unsichere Werte erscheinen als eigene Kategorie, nicht als stillschweigende Auslassung.

**Rückverfolgbarkeit.** Jeder visualisierte Datenpunkt erlaubt Drill-down auf die zugrundeliegenden Quellen. Direkte Referenzen (`rs/@ref`) und indirekte Referenzen (`@corresp`) führen beide in die Detailansicht; der Referenz-Typ wird ausgewiesen.

**Wiederverwendbarkeit.** Aggregierte und Register-Daten sind mit Metadaten exportierbar. Quellen und Register-Einträge tragen stabile Referenzen für Zitation.

**Eine Sub-Seite, eine Visualisierung.** Jede Sub-Seite ist eine zusammenhängende interaktive Visualisierung, die einen klaren Zugang zur Datenstruktur eröffnet. Mehrere Visualisierungen auf einer Seite verwässern den Fokus.

## Filterlogik und Anfangszustand

Eine Filteränderung wirkt auf die gesamte Visualisierung. Anklickbare Elemente (Knoten, Karten-Marker, Sankey-Bänder) tragen einen Hover-Zustand und einen Cursor-Wechsel; ein Klick führt entweder in eine Detailansicht oder in das Drill-down-Overlay (siehe [[architecture#Provenienz-Indizes]]).

Der Anfangszustand ist konsequent neutral: voller Zeitraum, keine Filter, kein vorausgewähltes Element. Eine Vorauswahl würde redaktionell wirken — einer einzelnen Person, einem einzelnen Ort eine Sonderstellung geben, die in den Daten so nicht angelegt ist.

Die Übergänge zur [[analyse]] sind möglich, wo die Daten sie tragen. Aus dem Personen-Netzwerk kann man eine Person in die Auswertungen übernehmen; aus den Orten lassen sich die Transaktionen vor Ort öffnen. Cross-Navigations-Punkte erscheinen nur, wenn die Daten sie stützen.

## Zusammenspiel mit übergreifenden Komponenten

- **[[ui-design#Zählebenen-Umschalter]]** wird auch hier wirken, sobald Visualisierungen Personenzählungen anzeigen. Personenzählung wechselt zwischen [[glossar#Gesamtnennung|Gesamtnennungen]] und [[glossar#Individuelle Person|Individuellen Personen]] konsistent.
- **[[ui-design#Bestandsfilter]]** ist universell und gilt auch hier. Die Aggregate in den `epic_*`-Dateien müssen zur Unterschlüsselung nach Quellenkorpus vorbereitet sein, damit clientseitige Filterung auf Teilbestände funktioniert.
- **[[ui-design#Provenienz-Tip und Glossar-Tip]]** macht die Herkunft jeder visualisierten Größe an Ort und Stelle einsehbar.

## Siehe auch

- [[analyse]] der quantitative Zweig: Auswertungen plus Template-Abfragen
- [[decisions#Exploration und Analyse als getrennte Bereiche]] Begründung der Trennung
- [[decisions#Auswertungen gehört in den Analyse-Bereich]] warum die früheren „Exploration"-Sub-Seiten zur Analyse gewandert sind
- [[ui-design]] gemeinsame Komponenten
- [[data]] die Datenbasis, die beide Zweige bedienen
