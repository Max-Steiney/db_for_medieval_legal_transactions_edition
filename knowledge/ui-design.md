# UI-Design

Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten der Oberfläche.

## Leitprinzip Maximaler Informations-Output

Die Oberfläche priorisiert Nachvollziehbarkeit vor reduzierter Darstellung. Nutzerinnen des Interfaces arbeiten mit den Daten, sie konsumieren sie nicht. Für diese Arbeit ist Information nicht störend, sondern notwendig.

Konkret folgt daraus, dass Herkunftsanzeigen, Filterzustände und die aktive Zählebene nicht versteckt werden, um die Oberfläche „sauber" wirken zu lassen. Eine Reduktion, die Herkunft verschleiert, wäre fachlich dysfunktional.

Nicht gemeint ist Unübersichtlichkeit. Dichte Darstellung und hierarchische Gliederung widersprechen sich nicht. Der Entwurf sucht beides.

Siehe [[requirements#Informationsdichte vor reduzierter Ästhetik]], [[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Navigation

Die Hauptnavigation gliedert sich in fünf Bereiche.

### Dokumente

Einstieg zur Volltextsuche und zum Durchsuchen der [[glossar#Quelle|Quellen]]. Der Bereich trägt die Grundoperationen Suchen, Filtern nach Zeitraum und Nachladen der Volltexte einzelner Quellen.

### Register

Fasst Personen, Organisationen und Orte zusammen. Konsolidierte Identitäten aus den drei Registern werden hier gelistet, jeweils mit Rückverweisen in die zugehörigen Quellen.

### Exploration

Bietet visuell-explorative Zugänge zu den Daten. Der Bereich bedient ergebnisoffene Fragestellungen nach dem Muster Überblick, Filter, Details auf Anforderung.

### Analyse

Hält einen klassischen Abfragemodus bereit. Der Bereich bedient gezielte, wiederkehrende Kombinationen aus Bestand, [[glossar#Rolle]], Geschlecht und Nennungsart. Exploration und Analyse stehen nebeneinander, nicht anstelle voneinander.

### Projekt

Bündelt Metaebenen des UI. Über das Projekt, Statistik, Qualität, Editionsrichtlinien, Glossar und Impressum.

## Zwei Modi nebeneinander

Exploration und Analyse bedienen unterschiedliche Forschungssituationen. Die Exploration ist für Nutzerinnen ohne vorab spezifizierte Frage, die Analyse für Nutzerinnen mit einer bestimmten Abfragekombination, die sie regelmäßig braucht.

Eine Zusammenlegung wäre unsauber, weil die jeweiligen Interaktionsmuster gegeneinander arbeiten. Exploration verlangt offene Einstiegspunkte und schrittweise Eingrenzung. Analyse verlangt direkten Zugriff auf eine definierte Abfrage.

## Kernkomponenten

### Provenienz-Tip und Glossar-Tip

Zwei verwandte, aber funktional getrennte Tooltip-Komponenten teilen sich die Popover-Mechanik, unterscheiden sich aber im Trigger und im Inhalt.

Der **Provenienz-Tip** sitzt an einem dargestellten Zahlenwert (Trigger ist die Zahl, gepunktet unterstrichen) und nennt den zugrunde liegenden Bestand, die angewandte Zähloperation, den [[glossar#Menschen-Event]]-Status und die aktiven Filter. Er macht den Unterschied zwischen oberflächlicher Ansicht und verwendbarer Zahl aufhebbar.

Der **Glossar-Tip** sitzt neben einem Fachbegriff (Trigger ist ein kompaktes `i`-Icon) und öffnet die Begriffsdefinition mit einem Verweis ins Glossar. Er bedient die Erstbegegnung mit einem projektspezifischen Begriff am Ort des Auftretens.

Beide Komponenten sind über dasselbe Interaktionsmuster abrufbar (Hover, Fokus, Klick). Siehe [[requirements#Datenrobustheit und Provenienz]] und [[glossar]].

### Zählebenen-Umschalter

Ein globaler Umschalter wechselt zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]]. Die Wahl propagiert konsistent durch alle abhängigen Darstellungen.

Der aktuelle Zustand ist in jeder Zahl-Darstellung über das Provenienz-Tooltip einsehbar.

Siehe [[requirements#Umschaltbarkeit der Zählebenen]].

### Bestandsfilter

Eine universelle Filterkomponente ist in allen Ansichten präsent. Sie erlaubt Mehrfachauswahl über [[glossar#Quellenkorpus|Quellenkorpora]] und bleibt bei Navigation erhalten.

Siehe [[requirements#Bestandsfilterung als universelle Dimension]].

### Menschen-Events-Toggle

Ein aktiv zu setzender Schalter entscheidet über die Einbeziehung oder den Ausschluss von [[glossar#Menschen-Event|Menschen-Events]]. Der Status ist im Provenienz-Tooltip jeder abhängigen Zahl sichtbar.

Neben dem Toggle steht ein Verweis auf die Glossar-Definition, damit Nutzerinnen die Bedeutung an Ort und Stelle nachschlagen können.

Siehe [[requirements#Menschen-Events-Behandlung]].

### Zeitfilter

Ein Zeitregler mit flankierenden Eingabefeldern schränkt die Anzeige auf einen Zeitraum ein. Der Regler respektiert den Freigabezeitraum der Edition (siehe [[data#Gegenstand]]).

### Glossar-Integration

Fachbegriffe im UI verweisen auf die Glossar-Seite ([[glossar]]). Beim ersten Auftreten eines Begriffs erscheint optional ein Tooltip mit der Kurzdefinition.

## Layout-Grundsätze

Informationsdichte steht vor Weißraum. Filter- und Statusleisten bleiben persistent sichtbar, auch wenn Inhalte gescrollt werden. Brotkrumennavigation führt Nutzerinnen zurück zu übergeordneten Ansichten.

Das Responsive-Verhalten zielt auf Laptop- und Tablet-Arbeitsplätze. Ein Mobile-First-Ansatz wäre hier dysfunktional, weil Recherche an kleinen Bildschirmen die Dichte der Darstellung nicht trägt.

## Farbkodierung und Typografie

Die Farbpalette bleibt zurückhaltend, damit die Daten im Vordergrund stehen. Drei Ebenen tragen die visuelle Hierarchie:

- **Akzentblau** markiert Interaktives und Kategorien: Icons, Eyebrow-Labels, Link-Hover, Provenienz-Trigger, aktive Filter.
- **Schwarz** trägt den Inhaltstitel: Seiten-Überschriften, Card-Titel, Regesttexte.
- **Gedämpftes Grau** trägt Beschreibungstexte, Metadaten und Fußnoten.

Die Zuordnung ist kein Dekorationsmuster, sondern eine semantische Kodierung: eine blaue Stelle ist navigierbar oder kategorisiert, eine schwarze Stelle ist Inhalt, eine graue Stelle ist Kontext. Nutzerinnen, die die Oberfläche über die Zeit lesen lernen, verlassen sich darauf.

Serifen-Typografie trägt lange Lese-Texte wie Regesten. Sans-Serif trägt UI-Elemente und Zahlen, weil beide schneller erfasst werden müssen.

## Startseite als Zwei-Säulen-Einstieg

Die Startseite führt die beiden gleichberechtigten Zugänge der Navigation — Exploration und Analyse — als nebeneinanderstehende Säulen vor. Eyebrow-Labels in Sans-Caps markieren die Bereiche, ohne sie durch schwergewichtige Trennlinien gegeneinander abzugrenzen. Die Exploration-Säule hält ein 2×2-Raster visueller Zugänge (Rollen, Beziehungen, Transaktionen, Orte). Die Analyse-Säule zeigt den Einstieg zu den Template-Familien, die in [[analyse]] konzeptionell ausgearbeitet sind.

Darüber liegen drei Entry-Cards (Quellen durchsuchen, Personenregister, Über das Projekt) mit Akzentfarben-Icons. Sie tragen den pragmatischen Alltag, während die Säulen darunter die beiden methodischen Zugänge verorten.

## Datenstand und Build-Datum

Die Fußzeile unterscheidet zwei Datumsangaben. Der **Datenstand** ist das Datum des letzten Commits im Pipeline-Repo, umgesetzt in lesbarer deutscher Langform. Er verweist auf den Stand der Quellen, nicht auf den Zeitpunkt, zu dem die statischen Seiten gebaut wurden. Das **Build-Datum** erscheint pro Seite im Fußzeilen-Zusatz und markiert den Zeitpunkt der jeweiligen Seitengenerierung. Beide sind in lesbarer Form, nicht als ISO-Zeichenkette. Siehe [[architecture#Datenstand aus dem Pipeline-Repo]].

## Zitierbarkeit einzelner Ansichten

Ansichten mit gesetzten Filtern sind über ihre URL referenzierbar. Der Filterzustand lebt im URL-Fragment oder Query-String. Nutzerinnen, die eine Ansicht an Kolleginnen weitergeben, schicken damit dasselbe, was sie selbst sehen.

Siehe [[requirements#Zitierfähige Datenstände]].

## Siehe auch

- [[requirements]] Anforderungen, die das Design umsetzt
- [[scholar-user-stories]] Nutzungsszenarien, die die Komponenten motivieren
- [[glossar]] Begriffe, die im UI erklärt werden
- [[exploration]] Detailkonzept des visuell-explorativen Zweigs
- [[analyse]] Detailkonzept des analytischen Query-Bereichs
