---
title: UI-Design
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
topics: ["[[Information Visualisation]]", "[[Scholar-Centered Design]]"]
related: [requirements, scholar-user-stories, decisions, analyse, exploration]
---

# UI-Design

Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten der Oberfläche. Konzeptionell formuliert; konkrete Klassen, Tokens und Pixelmaße leben im Code unter `frontend/static/css/` und `frontend/templates/`.

## Gestaltungshaltung

Die Oberfläche folgt einer wissenschaftlichen Lese-Gravitation. Serifen-Typografie und ein warmer, pergamentnaher Hintergrund signalisieren ein Forschungswerkzeug, kein Konsumprodukt. Annotationen sind farbig, aber zurückgenommen. Der Entwurf zielt auf Laptop- und Tablet-Arbeitsplätze und respektiert Druckausgabe als gleichberechtigten Lesemodus.

Das **Leitprinzip ist maximaler Informations-Output**: Nutzerinnen arbeiten mit den Daten, sie konsumieren sie nicht. Herkunftsanzeigen, Filterzustände und die aktive Zählebene werden nicht versteckt, um die Oberfläche „sauber" wirken zu lassen — eine Reduktion, die Herkunft verschleiert, wäre fachlich dysfunktional. Dichte Darstellung und hierarchische Gliederung sind beide gefragt, nicht gegeneinander.

Eine zweischichtige Lesart durchzieht das UI: technische Identifikatoren (Datei-Schlüssel, Personen-IDs, TEI-Annotationen) koexistieren mit menschenlesbaren Labels. Beide Schichten sind sichtbar.

Siehe [[requirements#Informationsdichte vor reduzierter Ästhetik]] und [[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Navigation

Die Hauptnavigation gliedert sich in fünf Bereiche.

### Quellen

Einstieg zur Volltextsuche und zum Durchsuchen der [[glossar#Quelle|Quellen]]. Der Bereich trägt die Grundoperationen Suchen, Filtern nach Zeitraum und Nachladen der Volltexte einzelner Quellen.

### Register

Dropdown mit Personen und Organisationen. Beide Register sind freigegeben; jede individuelle Entität trägt neben dem Listen-Eintrag eine eigene Detail-Profilseite mit Stammdaten, Beziehungen und Quellen-Tabelle. Orts-Daten leben ausschließlich als Inline-Annotation im Quellen-Volltext, ohne eigenes Register.

### Analyse

Dropdown mit zwei Sub-Seiten unter `/analysis/`:

- **Auswertungen** (`auswertungen.html`) zeigt vorberechnete statistische Verteilungen als Donut, Bar-Chart und Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine lokale Zähleinheit-Umschaltung in der Funktionsrollen-Sektion wechselt zwischen Nennungen und Individuellen Personen. Vier Sektionen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen.
- **Abfragen** (`index.html`) bedient zwei Einstiegsmodi nebeneinander: eine kuratierte Frage-Galerie als oberste Ebene und einen Custom-Builder im aufklappbaren `<details>`. Konzept und Pivot-Begründung in [[analyse#4. Interface-Konzept: Frage-Galerie und Custom-Builder]] und [[decisions#Analyse-Seite mit Frage-Galerie und Custom-Builder]].

Die beiden Sub-Seiten teilen sich Aggregate (`roles.json`/`relations.json`/`transactions.json`), unterscheiden sich aber im Interaktionsmodus: Auswertungen filter-getrieben, Abfragen frage-getrieben.

### Exploration

Dropdown mit zwei Sub-Seiten unter `/exploration/`:

- **Zeitstrom** (`zeitstrom.html`) als gestapelter Bar-Chart der Quellendichte pro Jahrzehnt mit umschaltbarer Stapel-Achse, Brush-zu-Drill-down und isolierbarer Stack-Kategorie.
- **Personennetzwerk** (`personennetzwerk.html`) als Ego-Layout um eine Person mit Klick-Hopping durchs Beziehungsnetz.

Ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert, aber noch nicht umgesetzt. Detailkonzept in [[exploration]].

### Projekt

Dropdown mit Metaebenen des UI. Über das Projekt, Annotationsrichtlinien, Glossar, Impressum.

## Zwei Modi nebeneinander

Analyse bedient Nutzerinnen mit einer bestimmten Frage und liefert Zahlen, Verteilungen, exakte Belege. Exploration bedient Nutzerinnen ohne vorab spezifizierte Frage und liefert visuelle Pattern. Innerhalb der Analyse trennen sich filter-getriebene Auswertungen und frage-getriebene Abfragen. Begründung der Trennung in [[decisions#Exploration und Analyse als getrennte Bereiche]] und [[decisions#Auswertungen gehört in den Analyse-Bereich]].

## Information-Seeking-Muster

Die Oberfläche folgt der Sequenz „Überblick zuerst, dann zoomen und filtern, dann Details auf Anforderung". Dasselbe Muster wiederholt sich auf jeder Listen- oder Aggregat-Seite: oben Filter und Suche, in der Mitte die Liste oder Aggregat-Darstellung, an einzelnen Zellen oder Zeilen ein Drill-down, der die zugrunde liegenden Quellen aufschlüsselt. Die Konsistenz ist nicht Stilfrage, sondern Lernfrage — wer ein Muster auf einer Seite verstanden hat, bedient andere Seiten unmittelbar.

## Kernkomponenten

### Tip-System

Vier Tip-Klassen teilen sich die Popover-Mechanik in `tip.js` (Edge-Detection, Hover, Fokus, Klick, Escape) und unterscheiden sich in Trigger, Anlass und visueller Markierung.

- **Provenienz-Tip** (`tip-popover--data`) sitzt an einem Zahlenwert (gepunktet unterstrichen) und nennt Bestand, Zähloperation, Menschen-Event-Status und aktive Filter.
- **Glossar-Tip** (`tip-popover--glossary`) sitzt neben einem Fachbegriff (`i`-Icon) und öffnet die Begriffsdefinition mit Verweis ins Glossar.
- **Help-Tip** (`tip-popover--help`) klärt UI- oder Funktions-Hilfen, deren Bedeutung über bloßes Beschriften hinaus erklärt werden muss.
- **Hover-Hint** (`data-hint`-Attribut) ist die leichteste Variante: kein Popover-Inhalt nötig, nur ein Hover-Reizfeld für Aktions-Buttons, Statusanzeigen oder Spaltenköpfe.

Siehe [[requirements#Datenrobustheit und Provenienz]] und [[glossar]].

### Zählebenen-Umschalter (Phase 2, nicht umgesetzt)

Konzeptionell: ein globaler Umschalter wechselt zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]] und propagiert die Wahl konsistent durch alle abhängigen Darstellungen, mit Anzeige des aktuellen Modus im Provenienz-Tooltip jeder Zahl.

Status: nicht als globale Komponente umgesetzt. Lokal wirkt eine Zähleinheit-Umschaltung in der Funktionsrollen-Sektion der Auswertungs-Seite. Die universelle Propagierung ist als Phase-2-Aufgabe im [[journal]] vermerkt. Siehe [[requirements#Umschaltbarkeit der Zählebenen]].

### Bestandsfilter (Phase 2, nicht umgesetzt)

Konzeptionell: eine universelle Filterkomponente, die in allen Ansichten Mehrfachauswahl über [[glossar#Quellenkorpus|Quellenkorpora]] erlaubt und bei Navigation erhalten bleibt.

Status: derzeit wirkt der Filter nur auf der Quellen-Übersicht. Eine universelle Propagierung auf Auswertungen, Zeitstrom, Personennetzwerk und Register ist Phase-2-Aufgabe und setzt eine korpusbasierte Unterschlüsselung der Aggregat-JSONs voraus. Siehe [[requirements#Bestandsfilterung als universelle Dimension]].

### Menschen-Events-Toggle (Phase 2, nicht umgesetzt)

Konzeptionell: ein aktiv zu setzender Schalter entscheidet über die Einbeziehung oder den Ausschluss von [[glossar#Menschen-Event|Menschen-Events]] in abhängigen Zählungen, mit Glossar-Verweis am Toggle und Status-Anzeige im Provenienz-Tooltip jeder Zahl.

Status: nicht umgesetzt. Die Default-Variante schließt Personen-Annotationen in verschachtelten Events aus der Nennungszählung aus, siehe [[decisions#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]]. Eine umschaltbare Anzeige für die inklusive Variante ist Phase-2-Aufgabe. Siehe [[requirements#Menschen-Events-Behandlung]].

### Zeitfilter

Ein Zeitregler mit flankierenden Eingabefeldern schränkt die Anzeige auf einen Zeitraum ein. Der Regler respektiert den Freigabezeitraum der Datenbank (siehe [[data#Gegenstand]]).

### Glossar-Integration

Fachbegriffe im UI verweisen auf die Glossar-Seite ([[glossar]]). Beim ersten Auftreten eines Begriffs erscheint optional ein Tooltip mit der Kurzdefinition.

### Drill-down-Overlay

Aggregierte Zahlen sind klickbar und öffnen ein Overlay mit den beitragenden Quellen (Nr., Datum, Quellenkorpus, Kurzregest, Link in die Detailseite). Schließen über Schaltfläche, Backdrop oder Escape. Das Overlay ist über alle Aggregations-Träger konsistent gehalten und greift in die `drill_down`-Indizes der Aggregat-JSONs ([[architecture#Provenienz-Indizes]]).

Aktive Filter werden in den Drill mitgenommen, soweit der Aggregat-Schlüssel sie trägt. Bei sehr großen Ergebnismengen wird die Liste begrenzt und auf engere Eingrenzung hingewiesen. Im Footer stehen Cross-Page-Sprung in die Quellen-Liste und Datenkorb-Knopf pro Zeile.

### Active-Filter-Strip

Über jeder Liste oder Visualisierung mit Filtern liegt eine zentrierte Pillen-Leiste, die jeden aktiven Filter als entfernbaren Chip anzeigt („Geschlecht: ♀ weiblich ×"). Der Klick auf eine Pille löst genau diesen Filter; ein Reset-Button in der Sidebar löst alles auf einmal. Die Pillen sind die Single-Source-of-Truth für den Filter-Stand: alle Stellen, die Filter mutieren, schreiben am Ende durch denselben Render-Pfad, der die Pillen generiert.

Begründung: Forschende verlieren den Überblick, welche Filter aktiv sind, sobald die Sidebar einklappt oder die Filter-Quellen heterogen sind (Sidebar-Chips, Donut-Klicks, Toggles, Slider). Die Pillen-Leiste fasst alles an einer Stelle.

### URL-State-Sync

Auf den Daten-Visualisierungs-Seiten landet der Filter-Stand in den URL-Suchparametern und ist damit bookmark-fähig, teilbar und als Permalink in einer Publikation zitierbar. Mechanik in [[architecture#URL-State als Forschungsstand]].

### Cross-Page-Sprung in die Quellen-Liste

Drill-down-Overlay (Auswertungen) und Brush-Drill (Zeitstrom) bieten einen Footer-Link „→ in Quellen-Liste öffnen", der die übernehmbaren Filter (Zeitraum, Geschlecht) in die Quellen-Listenseite weiterreicht. Die Quellen-Liste kennt das Auswertungs-Vokabular nicht (Rolle, Beziehungstyp, Bezeichnung, Transaktionstyp, Stack-Fokus), diese Filter werden bewusst weggelassen — der Tooltip am Link macht die Lückenführung transparent.

Begründung in [[decisions#Cross-Page-Sprung mit Filter-Übernahme]].

### Datenkorb

Forschende sammeln Quellen, Personen und Organisationen über Sitzungen hinweg in einem clientseitigen Datenkorb. Neben jedem Eintrag in den Listen (Quellen-Tabelle, Personen- und Organisations-Register, Drill-Overlay, Brush-Drill, Personennetzwerk-Detail-Tabelle) und auf jeder Detail- und Profilseite steht ein kleiner „+"-Knopf, der den Eintrag in den Korb legt. Das Nav führt ein Korb-Icon mit Live-Badge (Gesamt-Anzahl gesammelter Einträge), klickbar zur Korb-Seite; ein Hover-Tooltip am Icon liefert die Aufschlüsselung nach Typ (Quellen, Personen, Organisationen) plus die Zahl der abgeleiteten Einträge.

Der Korb unterscheidet zwei Zustände pro Eintrag. **Gesammelt** sind Einträge, die die Forscherin selbst per +-Klick hinzugefügt hat (Knopf zeigt „x", farbig). **Abgeleitet** sind Einträge, die als Konsequenz aus einer gesammelten Quelle automatisch in den Korb gespiegelt wurden — beim Sammeln einer Quelle werden ihre annotierten Personen und Organisationen über den Forward-Index `docs_entities.json` als abgeleitete Einträge in den Korb gelegt (Knopf zeigt „*", gestrichelter Rahmen). Ein +-Klick auf einen abgeleiteten Eintrag stuft ihn zur gesammelten Sammlung hoch, sodass er nach Entfernen der Quelle erhalten bleibt. Entfernen einer Quelle räumt ihre Spur aus den abgeleiteten Einträgen; was nicht hochgestuft wurde und keine zweite Quelle als Bezug hat, fällt mit weg.

Die Korb-Seite (`/korb.html`) zeigt drei Tabellen untereinander: Quellen, Personen, Organisationen. Jede Tabelle hat ihre eigene Spaltenstruktur (Datum, Korpus und Regest für Quellen; Name, Geschlecht, aktive Jahre und „aus Quelle" für Personen; Name, Typ und „aus Quelle" für Organisationen), eine eigene Remove-pro-Zeile-Aktion, eine eigene Clear-Aktion für den ganzen Typ und einen CSV-Export (UTF-8 mit BOM, Excel-kompatibel) mit Wahlmöglichkeit zwischen „nur gesammelte" und „auch abgeleitete". Abgeleitete Zeilen sind kursiv und gedimmt; ihre „aus Quelle"-Spalte verlinkt zurück auf die belegende Quelle, mit Hover-Tooltip über Datum und Regest-Auszug.

Persistenz lebt in `localStorage` mit versioniertem Schlüssel; parallele Browser-Tabs synchronisieren sich automatisch via `storage`-Event. Begründung in [[decisions#Datenkorb als clientseitige Sammlung]].

### Quellen-Detailseite mit Text-Bild-Synopse

Die Detailseite einer Quelle stellt edierten Text und Faksimile nebeneinander, sofern ein Faksimile vorliegt. Die Synopse ist Default, kein Tab — wer Text und Bild gleichzeitig braucht, soll dafür nicht klicken müssen. Quellen ohne Faksimile fallen auf eine zentrierte Lese-Spalte zurück. Eine ausschaltbare Annotations-Schicht macht die TEI-Auszeichnung sichtbar oder unsichtbar.

### Register-Listenseite

Personen- und Organisationsregister teilen sich ein einheitliches Listenseiten-Muster: Alphabet-Leiste, Suche, Filter (Geschlecht/Typ/Quellenanzahl), sortierbare Tabelle. Die Namens-Spalte verlinkt auf die Detail-Profilseite der Entität. Eine Zeile lässt sich zusätzlich aufklappen und zeigt alle belegenden Quellen inline, ohne den Filterkontext zu verlieren. Ein „+"-Knopf pro Zeile legt die Entität in den Datenkorb.

### Entitäts-Profilseite

Jede individuelle Person und Organisation trägt eine Profilseite unter `register/persons/<id>.html` bzw. `register/orgs/<id>.html`. Layout im Muster der Quellen-Detailseite: Toolbar mit Breadcrumb und Meta-Strip, Header mit Name und Notiz, Beziehungs-Block, Quellen-Tabelle mit Rolle und Datenkorb-Knopf. Beziehungs-Auflösung in [[data#Register]]. Ein „+"-Knopf in der Toolbar legt die Entität selbst in den Datenkorb. Eine progressiv eingeblendete Quick-Filter-Funktion erlaubt das Eintippen eines Suchstrings über alle Tabellenzeilen.

## Layout-Grundsätze

Filter- und Statusleisten bleiben persistent sichtbar, auch wenn Inhalte gescrollt werden. Brotkrumennavigation führt zurück zu übergeordneten Ansichten.

## Farbkodierung und Typografie

Die Farbpalette bleibt zurückhaltend, damit die Daten im Vordergrund stehen. Drei Ebenen tragen die visuelle Hierarchie:

- **Akzentblau** markiert Interaktives und Kategorien: Icons, Eyebrow-Labels, Link-Hover, Provenienz-Trigger, aktive Filter.
- **Schwarz** trägt den Inhaltstitel: Seiten-Überschriften, Card-Titel, Regesttexte.
- **Gedämpftes Grau** trägt Beschreibungstexte, Metadaten und Fußnoten.

Die Zuordnung ist kein Dekorationsmuster, sondern eine semantische Kodierung: eine blaue Stelle ist navigierbar oder kategorisiert, eine schwarze Stelle ist Inhalt, eine graue Stelle ist Kontext. Nutzerinnen, die die Oberfläche über die Zeit lesen lernen, verlassen sich darauf.

Annotationen im edierten Quellentext folgen einer eigenen Farblogik: Personen tragen ein gedämpftes Blau, Organisationen ein gedämpftes Lila, Orte ein gedämpftes Grün. Funktionsrollen (Aussteller, Empfänger, Zeuge) liegen als linker Rahmen über Gruppen von Entitäten und folgen einer eigenen, akademisch-warmen Palette. Editorische Eingriffe (Hinzufügungen, Unleserliches) verwenden konventionelle philologische Markierungen (Kursive in eckigen Klammern, Wellenlinie). Ziel ist Sichtbarkeit ohne Konkurrenz zum Lese-Text.

Serifen-Typografie trägt lange Lese-Texte wie Regesten. Sans-Serif trägt UI-Elemente und Zahlen, weil beide schneller erfasst werden müssen. Monospace markiert technische Identifikatoren und Pfade — sie sollen sichtbar als technisch lesbar sein.

## Startseite als Zwei-Säulen-Einstieg

Die Startseite führt die beiden methodischen Zugänge — Analyse und Exploration — als nebeneinanderstehende Säulen vor. Eyebrow-Labels in Sans-Caps markieren die Bereiche, ohne sie durch schwergewichtige Trennlinien gegeneinander abzugrenzen. Die Analyse-Säule hält die beiden Sub-Seiten Auswertungen und Abfragen als verlinkte Cards; die Exploration-Säule hält den Zeitstrom und das Personennetzwerk und führt das geplante Sankey-Diagramm als gedämpften Coming-soon-Eintrag.

Darüber liegen Entry-Cards (Quellen durchsuchen, Personenregister, Organisationsregister, Über das Projekt) mit Akzentfarben-Icons. Sie tragen den pragmatischen Alltag, während die Säulen darunter die beiden methodischen Zugänge verorten.

## Datenstand und Build-Datum

Die Fußzeile unterscheidet zwei Datumsangaben. Der **Datenstand** ist das Datum des letzten Commits im Pipeline-Repo, umgesetzt in lesbarer deutscher Langform. Er verweist auf den Stand der Quellen, nicht auf den Zeitpunkt, zu dem die statischen Seiten gebaut wurden. Das **Build-Datum** erscheint pro Seite im Fußzeilen-Zusatz und markiert den Zeitpunkt der jeweiligen Seitengenerierung. Beide sind in lesbarer Form, nicht als ISO-Zeichenkette. Siehe [[architecture#Datenstand aus dem Pipeline-Repo]].

## Zitierbarkeit einzelner Ansichten

Ansichten mit gesetzten Filtern sind über ihre URL referenzierbar. Der Filterzustand lebt im URL-Fragment oder Query-String. Nutzerinnen, die eine Ansicht an Kolleginnen weitergeben, schicken damit dasselbe, was sie selbst sehen.

Siehe [[requirements#Zitierfähige Datenstände]].

## Druckausgabe

Jede Detailseite hat einen sinnvollen Druck-Zustand. Navigation, Filterleisten und Faksimile-Panel werden ausgeblendet; eine eigene Print-Metadaten-Zeile (Nummer, Datum, Ort, Archiv, Zitiervorschlag) wird sichtbar. Annotationen erscheinen als feine Unterstreichungen ohne Hintergrund, weil farbige Flächen im Druck eher stören als helfen. Ziel ist eine ausdruckbare Quelle, die ohne weitere Bearbeitung in einer wissenschaftlichen Arbeit zitiert werden kann.

## Siehe auch

- [[requirements]] Anforderungen, die das Design umsetzt
- [[scholar-user-stories]] Nutzungsszenarien, die die Komponenten motivieren
- [[glossar]] Begriffe, die im UI erklärt werden
- [[exploration]] Detailkonzept des visuell-explorativen Zweigs
- [[analyse]] Detailkonzept des analytischen Query-Bereichs
