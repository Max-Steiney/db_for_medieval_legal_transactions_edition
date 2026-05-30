---
title: UI-Design
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.3
created: 2026-02-19
updated: 2026-05-23
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Information Visualisation]]", "[[Scholar-Centered Design]]"]
related: [specification, user-stories, analyse, exploration]
---

# UI-Design

Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten der Oberfläche. Konzeptionell formuliert; konkrete Klassen, Tokens und Pixelmaße leben im Code unter `frontend/static/css/` und `frontend/templates/`.

## Gestaltungshaltung

Die Oberfläche folgt einer wissenschaftlichen Lese-Gravitation. Serifen-Typografie und ein warmer, pergamentnaher Hintergrund signalisieren ein Forschungswerkzeug, kein Konsumprodukt. Annotationen sind farbig, aber zurückgenommen. Der Entwurf zielt auf Laptop- und Tablet-Arbeitsplätze und respektiert Druckausgabe als gleichberechtigten Lesemodus.

Das **Leitprinzip ist maximaler Informations-Output**: Nutzerinnen arbeiten mit den Daten, sie konsumieren sie nicht. Herkunftsanzeigen, Filterzustände und die aktive Zählebene werden nicht versteckt, um die Oberfläche „sauber" wirken zu lassen — eine Reduktion, die Herkunft verschleiert, wäre fachlich dysfunktional. Dichte Darstellung und hierarchische Gliederung sind beide gefragt, nicht gegeneinander.

Eine zweischichtige Lesart durchzieht das UI: technische Identifikatoren (Datei-Schlüssel, TEI-Annotationen, Korpus-Pfade) koexistieren mit menschenlesbaren Labels. Die öffentliche Sicht zeigt die menschenlesbare Schicht; die technischen Personen-, Org- und Event-IDs (`pe__...`, `org__...`, `ev__...`) leben weiter im URL-Slug und in HTML-Attributen für Zitierbarkeit und Verlinkung, aber nicht im sichtbaren Text. Die interne Sicht (`?dev=1` oder interner Audience-Build) blendet sie ein. Beschluss: Stakeholder-Protokoll 18.05.2026 A.3.2.

Siehe [[specification#Maximaler Informations-Output als Gestaltungsleitlinie]] und [[architecture#Audience-Schicht für öffentliche und interne Sicht]].

## Begriffs- und Label-Konsistenz

Ein Feld oder Begriff trägt im gesamten UI dieselbe Bezeichnung. Liegt dieselbe Datenlogik in mehreren Ansichten (z. B. min und max der Quellen-Jahre einer Entität auf Org-Profil, Personen-Profil und Sidebar-Filter), muss das Label überall identisch sein, einschließlich Tooltip-Titeln und Hilfe-Texten. Inkonsistenzen sind Bug, nicht Designfreiheit. Wer ein Label an einer Stelle ändert, prüft alle anderen Stellen mit.

Begründung: Wechselnde Bezeichnungen für dieselbe Sache zwingen Forschende, jedes Mal neu zu prüfen, ob dasselbe gemeint ist. Das bricht die Lese-Gravitation und führt zu Fehl-Interpretationen.

Konkrete Beispiele aus der Pflege: „Datum der Quelle" (bei einer Quelle) bzw. „Datum der Quellen" (bei mehreren) für die Min-/Max-Spanne der ISO-Jahre einer Entität, identisch in Org-Profil, Personen-Profil, Personen-Datenkorb-Tabelle und Sidebar-Filter beider Register. „Empfänger*in", „Aussteller*in", „Zeug*in / Siegler*in", „Sonstige" als kontrolliertes Rollenvokabular in Profil-Header, Annotations-Tabelle, Drill-Down-Pills und Filter-Chips.

## Section-Header in Tabellen mit Quellenzitat

Eine Tabellen-Gruppen-Überschrift, die ein Quellenzitat trägt (z. B. die Dispositiv-Vorschau pro Rechtsgeschäft in der Annotations-Tabelle), folgt einer zweischichtigen Anordnung. Oben rechts ein schmaler Header-Streifen mit Meta-Information (Counter, gegebenenfalls ein Statusmarker). Darunter eine eigene zentrierte Zeile mit dem Quellenzitat, in deutschen Anführungszeichen „..." über `<q class="annotations-group-source">`, kursiv, gedämpft grau, klar abgesetzt von der kräftigen Inline-Trigger-Farbe im Volltext.

Begründung: das Zitat ist Quellentext und keine UI-Aussage. Wenn es mit dem Counter in einer Zeile mitläuft, vermischt sich beides optisch. Die Zentrierung und Anführungszeichen markieren es eindeutig als Zitat; die gedämpfte Farbe verhindert die Verwechslung mit den kräftigeren Inline-Annotationen im Volltext darüber.

Fallback bei fehlendem Quellentext (häufig im Stadtbuch-Korpus): die Quote-Zeile wird gar nicht erst gerendert. Der Counter bleibt. Kein Text-Fallback wie „kein Quellen-Verb erfasst", weil das eine editorische Aussage über die Datenlage wäre, die der Stakeholder nicht treffen will, solange keine bewusste Entscheidung getroffen wurde.

## Datenkorb-Erklär-Pattern

Die Korb-Seite trägt einen mehrteiligen Erklär-Block direkt unter dem Titel: Persistenz (lokal im Browser, kein Login, kein Server-Sync, geht beim Cache-Leeren verloren), Bedeutung der Status-Marker „gesammelt" und „abgeleitet" inkl. Beförderungs-Mechanik per „*"-Knopf, und das Export-Verhalten der Knöpfe. Visuell als linksbündige Erklär-Box mit Borderstreifen, nicht als Fließtext.

Die Export-Knöpfe sind in den Sektionen Personen und Organisationen paarweise beschriftet: „Nur gesammelte exportieren" gegen „Mit abgeleiteten exportieren". Im Quellen-Block reicht ein einzelner Knopf „Quellen exportieren", weil Quellen nicht abgeleitet werden können. Der Korb-Button in der Topbar trägt einen Tooltip, der die aktuelle Aufschlüsselung dynamisch zeigt (`breakdownText()`), plus statischen Fallback-Hint für den Initial-Render.

Begründung: Stakeholder-Anliegen aus Protokoll 18.05.2026 A.1.2 („Datenkorb als gute Idee, aber Erklärung und Testung notwendig") und das wiederkehrende Missverständnis, dass der Topbar-Counter alle Einträge (gesammelt plus abgeleitet) über alle drei Sektionen summiert, nicht nur die direkt gesammelten.

## Navigation

Die Hauptnavigation gliedert sich in fünf Bereiche.

### Quellen

Einstieg zur Volltextsuche und zum Durchsuchen der [[glossar#Quelle|Quellen]]. Der Bereich trägt die Grundoperationen Suchen, Filtern nach Zeitraum und Nachladen der Volltexte einzelner Quellen.

### Register

Dropdown mit Personen und Organisationen. Beide Register sind freigegeben; jede individuelle Entität trägt neben dem Listen-Eintrag eine eigene Detail-Profilseite mit Stammdaten, Beziehungen und Quellen-Tabelle. Orts-Daten leben ausschließlich als Inline-Annotation im Quellen-Volltext, ohne eigenes Register.

### Analyse

Dropdown mit zwei Sub-Seiten unter `/analysis/`:

- **Auswertungen** (`auswertungen.html`) zeigt vorberechnete statistische Verteilungen als Donut, Bar-Chart und Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine lokale Zähleinheit-Umschaltung in der Funktionsrollen-Sektion wechselt zwischen Nennungen und Individuellen Personen. Vier Sektionen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen.
- **Abfragen** (`index.html`) ist eine strukturierte Konstellations-Abfrage über Rollen-Konstellationen. Forscherinnen legen N nummerierte Personen-Bedingungen an, je mit Rolle und optional Geschlecht und Beruf-Substring, und sehen alle Rechtsgeschäfte, in denen diese Konstellation gemeinsam erfüllt ist. Globale Filter: Zeitraum, Korpus, Verknüpfungs-Modus „im selben Rechtsgeschäft" gegen „in derselben Quelle". Konzept und Begründung in [[analyse#Konstellations-Abfrage]] und [[specification#Abfragen-Sub-Seite als Konstellations-Abfrage]].

Die beiden Sub-Seiten teilen sich Aggregate (`roles.json`/`relations.json`/`transactions.json` plus `role_constellation.json`), unterscheiden sich aber im Interaktionsmodus: Auswertungen filter-getrieben, Abfragen konstellations-getrieben.

### Exploration

Dropdown mit zwei Sub-Seiten unter `/exploration/`:

- **Zeitstrom** (`zeitstrom.html`) als gestapelter Bar-Chart der Quellendichte pro Jahrzehnt mit umschaltbarer Stapel-Achse, Brush-zu-Drill-down und isolierbarer Stack-Kategorie.
- **Personennetzwerk** (`personennetzwerk.html`) als Ego-Layout um eine Person mit Klick-Hopping durchs Beziehungsnetz.

Ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert, aber noch nicht umgesetzt. Detailkonzept in [[exploration]].

### Projekt

Dropdown mit Metaebenen des UI. Über das Projekt, Annotationsrichtlinien, Glossar, Impressum.

## Zwei Modi nebeneinander

Analyse bedient Nutzerinnen mit einer bestimmten Frage und liefert Zahlen, Verteilungen, exakte Belege. Exploration bedient Nutzerinnen ohne vorab spezifizierte Frage und liefert visuelle Pattern. Innerhalb der Analyse trennen sich filter-getriebene Auswertungen und frage-getriebene Abfragen. Begründung der Trennung in [[specification#Exploration und Analyse als getrennte Bereiche]] und [[specification#Auswertungen gehört in den Analyse-Bereich]].

## Information-Seeking-Muster

Die Oberfläche folgt der Sequenz „Überblick zuerst, dann zoomen und filtern, dann Details auf Anforderung". Dasselbe Muster wiederholt sich auf jeder Listen- oder Aggregat-Seite: oben Filter und Suche, in der Mitte die Liste oder Aggregat-Darstellung, an einzelnen Zellen oder Zeilen ein Drill-down, der die zugrunde liegenden Quellen aufschlüsselt. Die Konsistenz ist nicht Stilfrage, sondern Lernfrage — wer ein Muster auf einer Seite verstanden hat, bedient andere Seiten unmittelbar.

## Kernkomponenten

### Tip-System

Vier Tip-Klassen teilen sich die Popover-Mechanik in `tip.js` (Edge-Detection, Hover, Fokus, Klick, Escape) und unterscheiden sich in Trigger, Anlass und visueller Markierung.

- **Provenienz-Tip** (`tip-popover--data`) sitzt an einem Zahlenwert (gepunktet unterstrichen) und nennt Bestand und Zähloperation.
- **Glossar-Tip** (`tip-popover--glossary`) sitzt neben einem Fachbegriff (`i`-Icon) und öffnet die Begriffsdefinition mit Verweis ins Glossar.
- **Help-Tip** (`tip-popover--help`) klärt UI- oder Funktions-Hilfen, deren Bedeutung über bloßes Beschriften hinaus erklärt werden muss.
- **Hover-Hint** (`data-hint`-Attribut) ist die leichteste Variante: kein Popover-Inhalt nötig, nur ein Hover-Reizfeld für Aktions-Buttons, Statusanzeigen oder Spaltenköpfe.

Siehe [[specification#Datenrobustheit und Provenienz]] und [[glossar]].

### Bestandsfilter

Auf den drei Listen-Seiten (Quellen, Personenregister, Organisationsregister) steht in der Filter-Seitenleiste eine Gruppe Chips mit den verfügbaren [[glossar#Quellenkorpus|Quellenkorpora]] und der jeweiligen Treffer-Anzahl. Mehrfachauswahl ist möglich.

Auf den Visualisierungs-Seiten (Auswertungen, Zeitstrom, Personennetzwerk) wird der Filter bewusst nicht angeboten: die dort gezeigten Aggregate werden über alle Korpora gemeinsam berechnet, ein Korpus-Filter hätte keine Wirkung. Wer einen Teilbestand braucht, geht über die Quellenliste und nutzt den Cross-Page-Sprung zurück in die Visualisierung.

Auf der Auswertungs-Seite trägt die Funktionsrollen-Sektion eine lokale Umschaltung zwischen Gesamtnennungen und Individuellen Personen. Die Unterscheidung ist nur in dieser einen Sektion fachlich tragend und wird daher nicht global propagiert.

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

### Tabellen-Schicht

Tabellen erscheinen projektweit nach denselben Konventionen, getragen durch geteilte Cell-Renderer und CSS-Klassen ([[architecture#Geteilte Tabellen-Schicht]]). Vier wiederkehrende Cell-Formen.

**Type-Marker** als kleiner farbiger Punkt vor der Nennform, in der Annotations-Token-Farbe der jeweiligen Kategorie (Person blau, Organisation lila, Ort grün). Trägt die Typ-Information ohne eigene Spalte zu kosten. Hover-Tooltip nennt den Typ aus.

**Funktionsrollen-Pille** als gefüllter Pillen-Chip in Akzentblau für kontrolliertes Vokabular (Aussteller*in, Empfänger*in, Zeug*in / Siegler*in, Sonstige). Die Füllung signalisiert „klassifizierter Wert", visuell hervorgehoben gegenüber dem darum stehenden Klartext.

**Attribut-Tag** als umrandeter Pillen-Chip ohne Füllung, ein Tag pro Einzelwert für quellennahe Beischriften aus `roleName`-Annotationen (`frawen`, `witib`, `statrichter`, `chaplan`). Type-Information liegt im Hover-Tooltip. Die Umrandung statt Füllung signalisiert „Quellenwortlaut, keine Klassifikation".

**Geschlechts-Label** ausgeschrieben als „weiblich"/„männlich"/„ohne Angabe" für Tabellen-Zellen, Glyph-Variante `♀ weiblich`/`♂ männlich` für Visualisierungs-Achsen. Konsequenter Fallback-Wert „ohne Angabe" projektweit, nicht abweichend pro Page.

Sortier-Pfeile sind global gesetzt (`components.css`, Klasse `.sortable-table`), `white-space: nowrap` auf den Spaltenköpfen verhindert, dass der Pfeil unter das Label rutscht. Eine gruppen-aware Sortierung respektiert Section-Header (Annotations-Tabelle mit Event-Gruppen).

### Dev-Mode-Schalter

Ein URL-Parameter `?dev=1` an einer beliebigen Seite setzt `.dev-mode` auf das `<html>`-Element. CSS-Selektor `.dev-mode .dev-only` macht Elemente mit der Klasse `.dev-only` sichtbar, ergänzt um einen gelben gestrichelten Rahmen und ein „Entwicklung"-Label am rechten oberen Rand. Default-Sicht ohne URL-Parameter blendet sie aus.

Die Mechanik ist projektweit anwendbar und parallel zur build-zeit-Audience-Achse. Audience entscheidet, *ob* etwas im Build enthalten ist, Dev-Mode entscheidet, *ob* enthaltene Elemente sichtbar geschaltet werden. Erstes Anwendungsbeispiel ist die Dispositivformeln-Sub-Tabelle in der Annotationsansicht. Begründung in [[specification#Öffentliche versus interne Sicht in zwei Schichten]], Architektur-Detail in [[architecture#Dev-Mode-Schalter als komplementäre Client-Schicht]].

### Pillen-System und Tabellen-Toolbar auf der Abfragen-Seite

Die Abfragen-Sub-Seite (`/analysis/index.html`) verwendet eine eigene Klassenfamilie `.qb-pill` für alle interaktiven Form-Elemente im Abfrage-Bereich (Modus-Toggle, Korpus-Checkboxen, Add-Person, Add-Organisation, Reset). Die Klasse ist absichtlich getrennt von der globalen `.form-filter-chip`-Klasse, die in der Sidebar der Listen-Seiten lebt: dort sind viele eng gepackte Chips für eine Mehrfachauswahl typisch, hier sind wenige prominente Filter-Pillen mit großzügiger Schrift und Padding gemeint. Eine spätere Konsolidierung wäre möglich, würde aber Padding- und Größen-Tokens parametrisieren müssen; bis dahin bleiben die zwei Familien parallel.

Die Trefferliste der Konstellations-Abfrage führt eine Toolbar-Zeile direkt im Tabellen-Container über den Spaltenköpfen, mit derselben `--color-bg-warm`-Hintergrundfarbe wie die Spaltenköpfe. Visueller Effekt: KPI („X Rechtsgeschäfte in Y Quellen") und CSV-Download wirken als zusätzliche Header-Zeile, nicht als schwebender Block über der Tabelle. Die KPI hebt die führende Zahl in der Akzent-Farbe hervor, damit die dynamische Abfrage-Antwort visuell von den darum stehenden Begleitworten getrennt ist.

### Bedingungs-Bereiche und Treffer-Pillen pro Entitätstyp

Personen und Organisationen sind zwei eigenständige Bedingungs-Bereiche unter der gemeinsamen Sektion „Bedingungen". Jeder Sub-Bereich trägt einen Sub-Header mit dem Bereichsnamen links (mit farbigem Border-Akzent: blau für Personen über `--anno-person`, lila für Organisationen über `--anno-org`) und dem Hinzufügen-Knopf rechts in derselben Zeile. Die zugehörige Tabelle wird erst sichtbar, sobald mindestens eine Bedingungszeile angelegt ist. Diese Trennung wurde gewählt, weil Personen- und Org-Bedingungen verschiedene Slots haben (Personen: Rolle, Geschlecht, Beruf, Uhlirz; Orgs: Rolle, Name, Typ); eine gemeinsame Tabelle wäre entweder mit leeren Zellen durchlöchert oder müsste die Slot-Konfiguration pro Zeile umschalten, was die Sub-Header-Lösung sauber vermeidet.

In der Treffer-Tabelle korrespondieren die Bedingungs-Bereiche mit zwei Pillen-Familien: `.person-pill` (blau, verlinkt aufs Personen-Profil) und `.org-pill` (lila, verlinkt aufs Organisations-Profil). Pillen-Nummern sind farbig in der jeweiligen Akzentfarbe und nummerieren pro Entitätstyp eigenständig (Person 1, Person 2; Org 1, Org 2), in der Reihenfolge der Bedingungszeilen. So bleibt der visuelle Bezug zwischen Treffer und gesetzter Bedingung lesbar, auch wenn Personen- und Org-Bedingungen gemischt aktiv sind.

Die Beteiligten-Spalte zeigt nicht nur die Bedingungs-Treffer, sondern alle Hauptakteure des Rechtsgeschäfts (Aussteller und die ersten vier Empfänger pro Entitätstyp), damit die Transaktions-Konstellation auf einen Blick lesbar ist. Bedingungs-Treffer sind durch ihre Nummern-Pille hervorgehoben. Weitere Empfänger jenseits der Schwelle und alle Zeugen/Siegler/sonstigen Beteiligungen sind hinter einem „+N weitere"-Schalter pro Trefferzeile ausklappbar, der die Tabelle bei Stiftungen und Testamenten mit 20+ Empfängern ruhig hält. Frühere Varianten (alle Beteiligten immer sichtbar oder umgekehrt nur die Bedingungs-Treffer) wurden verworfen: erstere überschüttet die Tabelle mit Erbschafts-Wänden, letztere versteckt die Transaktionspartner, was die Spalte „Beteiligte" zur Selbstreferenz macht.

### Custom-Autocomplete für Vokabular-Felder

Die Vokabular-Felder der Konstellations-Abfrage (Beruf/Tätigkeit/Amt bei Personen, Name bei Organisationen) verwenden ein eigenes Popover-Panel statt der nativen HTML-`<datalist>`. Das native Element lässt sich nicht stylen und wird auf Windows-Chrome dunkel mit weißem Text gerendert, was visuell aus der Seite herausfällt und für Nutzerinnen wie ein Bruch wirkt. Das eigene Popover hängt im `body`, wird per JS positioniert (damit Tabellen-Overflow es nicht beschneidet), und zeigt pro Eintrag links den Wert und rechts dezent `N Vorkommen im Korpus`. Tastatur-Navigation mit Pfeil hoch/runter, Enter zum Übernehmen, Esc zum Schließen. Die Zahl ist eine Vokabular-Häufigkeit (so oft kommt der Eintrag in den Daten vor), nicht die Live-Trefferzahl unter den aktiven Bedingungen; die explizite Beschriftung „N Vorkommen im Korpus" trennt das von der KPI in der Trefferzeile, die sich mit jeder Bedingungs-Änderung neu berechnet. Falls dasselbe Muster anderswo gebraucht wird, sollte der Helper in einen geteilten Baustein (z. B. `viz-core.js`) wandern; aktuell lebt er nur im Konstellations-Resolver.

### Datums-Formatierung in Trefferlisten

Die Trefferliste der Konstellations-Abfrage zeigt Datümer lesbar als `8. Apr 1342` (Tag, Drei-Buchstaben-Monat, Jahr) statt im ISO-Format. ISO ist intern weiter Sortier-Grundlage, weil es lexikographisch korrekt sortiert, aber visuell ist es eine Maschinen-Notation, die in der Tabelle stört. Nur-Jahr-Daten bleiben als Jahr stehen, leere Daten (Stadtbuch-Einträge ohne Einzeldatierung) erscheinen als `—`. Spalten-Sortierung über Header-Klick ist auf der Konstellations-Tabelle aktiviert (Datum, Quelle, Korpus, Rechtsgeschäft); CSV-Export folgt der gewählten Sortierung.

### URL-State-Sync

Auf den Daten-Visualisierungs-Seiten landet der Filter-Stand in den URL-Suchparametern und ist damit bookmark-fähig, teilbar und als Permalink in einer Publikation zitierbar. Mechanik in [[architecture#URL-State als Forschungsstand]].

### Cross-Page-Sprung in die Quellen-Liste

Drill-down-Overlay (Auswertungen) und Brush-Drill (Zeitstrom) bieten einen Footer-Link „→ in Quellen-Liste öffnen", der die übernehmbaren Filter (Zeitraum, Geschlecht) in die Quellen-Listenseite weiterreicht. Die Quellen-Liste kennt das Auswertungs-Vokabular nicht (Rolle, Beziehungstyp, Bezeichnung, Transaktionstyp, Stack-Fokus), diese Filter werden bewusst weggelassen — der Tooltip am Link macht die Lückenführung transparent.

Begründung in [[specification#Cross-Page-Sprung mit Filter-Übernahme]].

### Datenkorb

Forschende sammeln Quellen, Personen und Organisationen über Sitzungen hinweg in einem clientseitigen Datenkorb. Neben jedem Eintrag in den Listen (Quellen-Tabelle, Personen- und Organisations-Register, Drill-Overlay, Brush-Drill, Personennetzwerk-Detail-Tabelle) und auf jeder Detail- und Profilseite steht ein kleiner „+"-Knopf, der den Eintrag in den Korb legt. Das Nav führt ein Korb-Icon mit Live-Badge (Gesamt-Anzahl gesammelter Einträge), klickbar zur Korb-Seite; ein Hover-Tooltip am Icon liefert die Aufschlüsselung nach Typ (Quellen, Personen, Organisationen) plus die Zahl der abgeleiteten Einträge.

Der Korb unterscheidet zwei Zustände pro Eintrag. **Gesammelt** sind Einträge, die die Forscherin selbst per +-Klick hinzugefügt hat (Knopf zeigt „x", farbig). **Abgeleitet** sind Einträge, die als Konsequenz aus einer gesammelten Quelle automatisch in den Korb gespiegelt wurden — beim Sammeln einer Quelle werden ihre annotierten Personen und Organisationen über den Forward-Index `docs_entities.json` als abgeleitete Einträge in den Korb gelegt (Knopf zeigt „*", gestrichelter Rahmen). Ein +-Klick auf einen abgeleiteten Eintrag stuft ihn zur gesammelten Sammlung hoch, sodass er nach Entfernen der Quelle erhalten bleibt. Entfernen einer Quelle räumt ihre Spur aus den abgeleiteten Einträgen; was nicht hochgestuft wurde und keine zweite Quelle als Bezug hat, fällt mit weg.

Die Korb-Seite (`/korb.html`) zeigt drei Tabellen untereinander: Quellen, Personen, Organisationen. Jede Tabelle hat ihre eigene Spaltenstruktur (Datum, Korpus und Regest für Quellen; Name, Geschlecht, aktive Jahre und „aus Quelle" für Personen; Name, Typ und „aus Quelle" für Organisationen), eine eigene Remove-pro-Zeile-Aktion, eine eigene Clear-Aktion für den ganzen Typ und einen CSV-Export (UTF-8 mit BOM, Excel-kompatibel) mit Wahlmöglichkeit zwischen „nur gesammelte" und „auch abgeleitete". Abgeleitete Zeilen sind kursiv und gedimmt; ihre „aus Quelle"-Spalte verlinkt zurück auf die belegende Quelle, mit Hover-Tooltip über Datum und Regest-Auszug.

Persistenz lebt in `localStorage` mit versioniertem Schlüssel; parallele Browser-Tabs synchronisieren sich automatisch via `storage`-Event. Begründung in [[specification#Datenkorb als clientseitige Sammlung]].

### Quellen-Detailseite mit Text-Bild-Synopse

Die Detailseite einer Quelle stellt edierten Text und Faksimile nebeneinander, sofern ein Faksimile vorliegt. Die Synopse ist Default, kein Tab — wer Text und Bild gleichzeitig braucht, soll dafür nicht klicken müssen. Quellen ohne Faksimile fallen auf eine zentrierte Lese-Spalte zurück. Eine ausschaltbare Annotations-Schicht macht die TEI-Auszeichnung sichtbar oder unsichtbar.

Das Faksimile-Panel ist ein Deep-Zoom-Viewer auf Basis von OpenSeadragon. Das Panel hat eine feste Höhe (`100vh − Header`) und scrollt nicht intern; Lesen größerer Ausschnitte erfolgt über den Viewer selbst. Bedienung: Mausrad und Toolbar-Knöpfe für Zoom, Drag und Pinch für Pan, ein Rotate-Knopf für 90°-Schritte, ein 1:1-Reset setzt Zoom und Rotation auf den Ausgangszustand. Bei mehrseitigen Quellen schalten Pfeil-Knöpfe zwischen den Seiten um; die Rotation wird beim Seitenwechsel zurückgesetzt, damit eine neu geladene Seite nicht verkippt startet. Pan ist durch OpenSeadragon-Constraints geklemmt, das Bild bleibt im Sichtbereich.

### Annotations-Block

Unter Quellentext und Faksimile-Panel steht der Annotations-Block als dritter Lese-Bereich. Er trägt die aus dem TEI extrahierten Annotationen in einer Sub-Tabellen-Struktur, konsolidiert über einen Tab-Toggle.

Block-Header. Reine Überschrift „Annotationen" als Titel, kein Untertitel und keine Counter-Pille. Die Zahlen leben in den Tab-Pillen darunter (z. B. „Entitäten 19"). Bei genau einer sichtbaren Sub-Tabelle bleibt der Tab-Strip ausgeblendet, weil ein Either-Or-Schalter ohne Alternative überflüssig wäre.

Tab-Strip. Zentriert über dem Body, drei Tab-Pillen für Entitäten, Dispositivformeln und Editorische Ergänzungen. Aktive Pille gefüllt in Akzentblau, inaktive Pille umrandet. Pro Pille ein Count als kleine Sub-Pille. Die Dispositivformeln-Tab trägt die Klasse `.dev-only` und ist in der öffentlichen Sicht versteckt, in der privaten Sicht (`?dev=1`) sichtbar mit gelbem Rahmen.

Entitäten-Tabelle. Vier Spalten: Genannt als, Funktionsrolle, Attribute, Geschlecht. Sortierung gruppen-aware innerhalb der Event-Sections. Type-Marker vor der Nennform als farbiger Punkt ([[#Tabellen-Schicht]]), Funktionsrolle als gefüllte Pille, Attribute als umrandete Tags pro Wert, Geschlecht ausgeschrieben.

Section-Header pro Rechtsgeschäft. Innerhalb der Entitäten-Tabelle gruppiert ein Section-Header die Beteiligten pro Event. Inhalt ist eine kursive Disp-Vorschau (erste und letzte Dispositivformel des Events mit `…` dazwischen, in Trigger-Farbe) und rechtsbündig „N Genannte". Die rohe `ev__`-ID ist nicht sichtbar, der Disp-Wortlaut übernimmt die Mini-Titel-Funktion. Nested Events sind eingeklappt und ihre Entitäten wandern in die Eltern-Gruppe.

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

Siehe [[specification#Zitierfähiger Datenstand]].

## Druckausgabe

Jede Detailseite hat einen sinnvollen Druck-Zustand. Navigation, Filterleisten und Faksimile-Panel werden ausgeblendet; eine eigene Print-Metadaten-Zeile (Nummer, Datum, Ort, Archiv, Zitiervorschlag) wird sichtbar. Annotationen erscheinen als feine Unterstreichungen ohne Hintergrund, weil farbige Flächen im Druck eher stören als helfen. Ziel ist eine ausdruckbare Quelle, die ohne weitere Bearbeitung in einer wissenschaftlichen Arbeit zitiert werden kann.

## Siehe auch

- [[specification]] User-Stories, die das Design umsetzt
- [[user-stories]] Nutzungsszenarien, die die Komponenten motivieren
- [[glossar]] Begriffe, die im UI erklärt werden
- [[exploration]] Detailkonzept des visuell-explorativen Zweigs
- [[analyse]] Detailkonzept des analytischen Query-Bereichs
