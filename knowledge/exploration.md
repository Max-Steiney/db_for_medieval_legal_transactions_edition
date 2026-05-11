---
title: Exploration
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
topics: ["[[Information Visualisation]]", "[[Exploratory Search]]"]
related: [analyse, requirements, ui-design, decisions, glossar]
---

# Exploration

Wissensdokument zum Explorationsbereich der Datenbank. Die Exploration ist der visuell-interaktive Zweig der Oberfläche und bedient Nutzerinnen ohne vorab spezifizierte Frage. Sie steht als zweiter gleichberechtigter Zweig neben der [[analyse]] und arbeitet mit Information-Visualisation, nicht mit vorgegebenen Auswertungsachsen.

Die konzeptionelle Trennung ist in [[decisions#Exploration und Analyse als getrennte Bereiche]] festgehalten. Implementierte Sub-Seiten sind der **Zeitstrom** unter `/exploration/zeitstrom.html` und das **Personennetzwerk** unter `/exploration/personennetzwerk.html`; ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert, aber noch nicht umgesetzt. Geographische Karten sind bewusst nicht vorgesehen, weil Orts-Aussagen außerhalb des Forschungsfokus der Datenbank liegen. Die quantitativen Verteilungen (frühere „Auswertungen") gehören inhaltlich zur [[analyse]] und wurden dorthin verschoben. Siehe [[decisions#Auswertungen gehört in den Analyse-Bereich]].

## Zielsetzung

Die Exploration erlaubt Nutzerinnen, sich der Datenstruktur visuell anzunähern, ohne zu wissen, welche Frage sie an sie stellen werden. Sie macht qualitative Strukturen des Korpus sichtbar, die in einer Verteilungstabelle nicht erkennbar wären — etwa die Topologie eines Personennetzwerks, die geografische Streuung von Rechtsgeschäften oder die zeitliche Verdichtung von Korrespondenzen. Der typische Einstieg ist visuell, nicht quantitativ.

## Abgrenzung zur Analyse

Während die [[analyse]] vorgegebene Achsen bedient (Zeitraum, Geschlecht, Rolle, Transaktionstyp) und Verteilungen entlang dieser Achsen zeigt, lässt die Exploration die Nutzerin frei navigieren. Sie tauscht strukturierte Lesbarkeit gegen offene Sichtbarkeit. Beide Bereiche teilen sich dieselben Aggregate (`roles.json`/`relations.json`/`transactions.json`) und dieselben Filter-Bausteine, unterscheiden sich aber radikal im Interaktionsmodus: Analyse arbeitet mit Filtern und liest aus Tabellen ab, Exploration arbeitet mit Hovern, Zoomen, Selektieren auf einer interaktiven Visualisierung.

## Sub-Seiten

Jede Sub-Seite ist eine eigenständige Visualisierung mit eigener Mechanik.

### Zeitstrom (vorhanden)

Gestapelter Bar-Chart der Quellendichte pro Jahrzehnt. Die Stapel-Achse ist umschaltbar zwischen Quellenkorpus, Erschließungsform, Geschlecht der Beteiligten und Transaktionstyp; der Zeitraum-Slider in der Sidebar limitiert die sichtbaren Jahrzehnte; ein Brush per Maus-Drag über mehrere Spalten öffnet die Liste der enthaltenen Quellen direkt darunter.

Ein Klick auf ein Legend-Item fokussiert eine Stapel-Kategorie: die anderen Segmente werden in den Bars gedimmt, und der Brush-Drill filtert auf die fokussierte Kategorie. Damit wird ein unscharfer Brush („alle Quellen in 1390er") zu einer scharfen Auswahl („nur Schuldbrief/Pfand-Geschäfte in 1390er") — ohne dass die zeitliche Achse verloren geht. Stack-Switch hebt den Fokus automatisch auf, weil die Kategorien wechseln; Toggle auf dem gleichen Item hebt ihn manuell auf.

Datenquellen: `data/search.json` (für die ersten drei Stapel-Achsen), `data/transactions.json::observations.tx_timeline` (für die Transaktionstyp-Stapelung). Bei aktivem Tx-Fokus läuft der Drill über `transactions.drill_down.tx_type_decade` und löst die `file_keys` über `data/docs_lookup.json` auf. Die Drill-down-Liste verlinkt direkt in die Quellen-Detailseiten und bietet pro Zeile einen „+"-Knopf für den [[ui-design#Datenkorb]]; im Header steht der Cross-Page-Sprung in die Quellen-Liste mit übernommenem Zeitraum.

Der Filter-Stand wird in die URL serialisiert (`?dec=1300-1410&stack=tx&brush=1340-1370&focus=Kauf`), siehe [[ui-design#URL-State-Sync]].

Pattern, das die Sub-Seite trägt: Überblick → Brush → Quellen. Sie ergänzt die [[analyse#Zwei Sub-Seiten|Auswertungen]] um eine zeitlich-visuelle Erkundung — wer dort liest, dass Stiftungen ab den 1340ern zunehmen, kann hier sehen, in welchen Jahrzehnten die belegende Quellendichte trägt.

### Personennetzwerk (vorhanden)

Ego-Layout um eine Person: Mittelpunkt ist eine ausgewählte Person, ihre direkten annotierten Beziehungen (Verwandtschaft, Beruf / Stand, Vertretung, Freundschaft) liegen radial drumherum. Klick auf einen Nachbar verlagert den Mittelpunkt, so wandert man durchs Netz. Sidebar-Filter: Personen-Suche (Autocomplete) und Beziehungstyp-Chips (multi-select, mindestens einer aktiv).

Bewusst gegen Force-Layout: die meisten Co-Occurrence-Kanten haben Gewicht 1 — ein Strukturartefakt der Urkundenform, kein analytisch belastbares Beziehungsmaß. Ein Force-Layout über das Gesamt-Beziehungsnetz würde als unleserliches „Knäuel" erscheinen, in dem nichts erkennbar ist. Das Ego-Layout schneidet stattdessen pro Schritt einen lesbaren lokalen Ausschnitt — analog zum klassischen Genealogie-Stammbaum, nur mit Klick-Hopping als Navigation. Globale Topologie lässt sich daraus durch sequenzielles Erkunden rekonstruieren.

Datenquelle: `relations.json::persons`, jede Person trägt eine `rels`-Liste mit `{type, label, label_norm, source_file_key, related_key}`. Beruflich-institutionelle Beziehungen (`occ`) zeigen Person → Organisation; sie werden als Knoten anderer Farbe (Sand) dargestellt. Innerhalb des Netzwerks tragen sie das Klick-Hopping nicht — Verwandtschaft, Vertretung und Freundschaft sind person-zu-person und navigierbar. Die Organisations-Profile existieren inzwischen separat im Register und sind aus der Detail-Tabelle unter dem Graphen verlinkt.

Detail-Tabelle unter dem Graphen listet alle Verbindungen der Mittelpunkt-Person mit Beziehungstyp, Bezeichnung, Beleg-Anzahl und „+"-Knopf für den [[ui-design#Datenkorb]] (Sammlung verlinkter Personen oder Organisationen).

URL-State: `?p=pe__id&types=kin,occ` macht jeden Personen-Mittelpunkt zitierbar.

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

- **[[ui-design#Zählebenen-Umschalter]]** ist derzeit nicht als globale Komponente implementiert; sobald er kommt, soll er konsistent zwischen [[glossar#Gesamtnennung|Gesamtnennungen]] und [[glossar#Individuelle Person|Individuellen Personen]] umschalten. Phase-2-Aufgabe.
- **[[ui-design#Bestandsfilter]]** wirkt derzeit nur auf der Quellen-Übersicht; die universelle Propagierung auf Zeitstrom und Personennetzwerk ist Phase-2-Aufgabe und setzt eine korpusbasierte Unterschlüsselung der Aggregat-JSONs voraus.
- **[[ui-design#Provenienz-Tip und Glossar-Tip]]** macht die Herkunft jeder visualisierten Größe an Ort und Stelle einsehbar und ist auf beiden vorhandenen Sub-Seiten aktiv.

## Siehe auch

- [[analyse]] der quantitative Zweig: Auswertungen plus Template-Abfragen
- [[decisions#Exploration und Analyse als getrennte Bereiche]] Begründung der Trennung
- [[decisions#Auswertungen gehört in den Analyse-Bereich]] warum die früheren „Exploration"-Sub-Seiten zur Analyse gewandert sind
- [[ui-design]] gemeinsame Komponenten
- [[data]] die Datenbasis, die beide Zweige bedienen
