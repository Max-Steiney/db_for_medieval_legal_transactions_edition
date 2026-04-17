# UI-Design

Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten der Oberfläche.

## Leitprinzip: Maximaler Informations-Output

<!-- Die Oberfläche priorisiert Nachvollziehbarkeit vor reduzierter Ästhetik. Bewusste Absage an konsumnutzer-orientierte Design-Konventionen. Fachnutzerinnen erwarten Dichte, nicht Reduktion. Siehe [[requirements#Informationsdichte vor reduzierter Ästhetik]]. -->

## Navigation

<!-- Fünf Hauptbereiche, jeder mit klar umrissener Funktion. -->

### Dokumente

<!-- Einstieg zur Volltextsuche und zum Durchsuchen der [[glossar#Quelle]]. -->

### Register

<!-- Drei Unterbereiche: Personen, Organisationen, Orte. Konsolidierte Identitäten mit Verweisen in die Quellen. -->

### Exploration

<!-- Visuell-explorativer Zugang nach dem Information Seeking Mantra: Überblick, Filter, Details on demand. Bedient ergebnisoffene Fragestellungen. -->

### Analyse

<!-- Klassischer Abfragemodus für wiederkehrende Kombinationen aus Bestand × Rolle × Geschlecht × Nennungsart. Bedient gezielte Forschungsfragen. Ergänzt Exploration, ersetzt sie nicht. -->

### Projekt

<!-- Metaebene: Über das Projekt, Statistik, Qualität, Editionsrichtlinien, Glossar, Impressum. -->

## Zwei Modi nebeneinander

<!-- Exploration und Analyse sind zwei gleichrangige Zugangsformen. Warum beide: unterschiedliche Forschungssituationen erfordern unterschiedliche UI-Interaktionsmuster. -->

## Kernkomponenten

### Provenienz-Tooltip

<!-- An jedem dargestellten Datenpunkt: welcher Bestand, welche Zähloperation, [[glossar#Menschen-Event]]-Status, aktive Filter. Siehe [[requirements#Datenrobustheit und Provenienz]]. -->

### Zählebenen-Umschalter

<!-- Global zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]] umschaltbar. Auswahl propagiert konsistent. -->

### Bestandsfilter

<!-- Universelle Filterkomponente, in allen Ansichten präsent. Mehrfachauswahl möglich. -->

### Menschen-Events-Toggle

<!-- Aktive Entscheidung über Einbeziehung oder Ausschluss von [[glossar#Menschen-Event]]. Status sichtbar. -->

### Zeitfilter

<!-- Zeitregler und Eingabefelder für Zeitraumeinschränkung. -->

### Glossar-Integration

<!-- Fachbegriffe im UI verlinken auf die Glossar-Seite (Quelle: [[glossar]]). Tooltips bei erstem Auftreten eines Begriffs. -->

## Layout-Grundsätze

<!-- Informationsdichte vor Weißraum. Persistente Filterleiste. Brotkrumennavigation. Responsives Verhalten für Laptop- und Tablet-Arbeitsplätze; kein Mobil-First. -->

## Farbkodierung und Typografie

<!-- Zurückhaltende Farbpalette, damit Daten im Vordergrund bleiben. Serifen-Typografie für lange Lese-Texte (Regesten), Sans-Serif für UI-Elemente und Zahlen. -->

## Zitierbarkeit einzelner Ansichten

<!-- Ansichten mit gesetzten Filtern sind über URL referenzierbar. Filterzustand lebt im URL-Fragment oder Query-String. Siehe [[requirements#Zitierfähige Datenstände]]. -->

## Siehe auch

- [[requirements]] — Anforderungen, die das Design umsetzt
- [[scholar-user-stories]] — Nutzungsszenarien, die die Komponenten motivieren
- [[glossar]] — Begriffe, die im UI erklärt werden
