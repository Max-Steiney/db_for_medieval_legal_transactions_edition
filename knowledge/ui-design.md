# UI-Design

Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten der Oberfläche.

## Leitprinzip Maximaler Informations-Output

Die Oberfläche priorisiert Nachvollziehbarkeit vor reduzierter Darstellung. Nutzerinnen des Interfaces arbeiten mit den Daten, sie konsumieren sie nicht. Für diese Arbeit ist Information nicht störend, sondern notwendig.

Konkret folgt daraus, dass Herkunftsanzeigen, Filterzustände und die aktive Zählebene nicht versteckt werden, um die Oberfläche „sauber" wirken zu lassen. Eine Reduktion, die Herkunft verschleiert, wäre fachlich dysfunktional.

Nicht gemeint ist Unübersichtlichkeit. Dichte Darstellung und hierarchische Gliederung widersprechen sich nicht. Der Entwurf sucht beides.

Siehe [[requirements#Informationsdichte vor reduzierter Ästhetik]], [[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Navigation

Die Hauptnavigation gliedert sich in fünf Bereiche.

Der Bereich Dokumente ist der Einstieg zur Volltextsuche und zum Durchsuchen der [[glossar#Quelle|Quellen]]. Er trägt die Grundoperationen Suchen, Filtern nach Zeitraum und Nachladen der Volltexte einzelner Quellen.

Der Bereich Register fasst Personen, Organisationen und Orte zusammen. Konsolidierte Identitäten aus den drei Registern werden hier gelistet, jeweils mit Rückverweisen in die zugehörigen Quellen.

Der Bereich Exploration bietet visuell-explorative Zugänge zu den Daten. Er bedient ergebnisoffene Fragestellungen nach dem Muster Überblick, Filter, Details auf Anforderung.

Der Bereich Analyse hält einen klassischen Abfragemodus bereit. Er bedient gezielte, wiederkehrende Kombinationen aus Bestand, Rolle, Geschlecht und Nennungsart. Exploration und Analyse stehen nebeneinander, nicht anstelle voneinander.

Der Bereich Projekt bündelt Metaebenen des UI: Über das Projekt, Statistik, Qualität, Editionsrichtlinien, Glossar und Impressum.

## Zwei Modi nebeneinander

Exploration und Analyse bedienen unterschiedliche Forschungssituationen. Die Exploration ist für Nutzerinnen ohne vorab spezifizierte Frage, die Analyse für Nutzerinnen mit einer bestimmten Abfragekombination, die sie regelmäßig braucht.

Eine Zusammenlegung wäre unsauber, weil die jeweiligen Interaktionsmuster gegeneinander arbeiten. Exploration verlangt offene Einstiegspunkte und schrittweise Eingrenzung. Analyse verlangt direkten Zugriff auf eine definierte Abfrage.

## Kernkomponenten

### Provenienz-Tooltip

Jeder dargestellte Zahlenwert trägt eine Herkunftsanzeige. Sie nennt den zugrunde liegenden Bestand, die angewandte Zähloperation, den [[glossar#Menschen-Event]]-Status und die aktiven Filter.

Die Anzeige ist über ein einheitliches Interaktionsmuster abrufbar (Mouseover oder Fokus). Damit wird der Unterschied zwischen oberflächlicher Ansicht und verwendbarer Zahl aufhebbar.

Siehe [[requirements#Datenrobustheit und Provenienz]].

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

Die Farbpalette bleibt zurückhaltend, damit die Daten im Vordergrund stehen. Serifen-Typografie trägt lange Lese-Texte wie Regesten. Sans-Serif trägt UI-Elemente und Zahlen, weil beide schneller erfasst werden müssen.

## Zitierbarkeit einzelner Ansichten

Ansichten mit gesetzten Filtern sind über ihre URL referenzierbar. Der Filterzustand lebt im URL-Fragment oder Query-String. Nutzerinnen, die eine Ansicht an Kolleginnen weitergeben, schicken damit dasselbe, was sie selbst sehen.

Siehe [[requirements#Zitierfähige Datenstände]].

## Siehe auch

- [[requirements]] Anforderungen, die das Design umsetzt
- [[scholar-user-stories]] Nutzungsszenarien, die die Komponenten motivieren
- [[glossar]] Begriffe, die im UI erklärt werden
