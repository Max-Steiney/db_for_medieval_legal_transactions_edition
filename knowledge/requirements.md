# Anforderungen

Funktionale und nicht-funktionale Anforderungen an das User Interface. Pro Anforderung: *Was / Warum / Wie*.

## Datenrobustheit und Provenienz

### Was

<!-- Jede dargestellte Zahl muss in ihrer Herkunft transparent, in ihrer Berechnung dokumentiert und durch Fachnutzerinnen eigenständig reproduzierbar sein. -->

### Warum

<!-- Wissenschaftliche Verwendbarkeit hängt an Reproduzierbarkeit. Intransparente Zahlen sind fachlich unbrauchbar, auch wenn sie korrekt sind. -->

### Wie

<!-- Provenienz-Tooltip an jedem Datenpunkt: welcher Bestand, welche Zähloperation, welche Filter aktiv, [[glossar#Menschen-Event]] inkludiert oder nicht. Siehe [[ui-design#Provenienz-Tooltip]]. -->

## Umschaltbarkeit der Zählebenen

### Was

<!-- UI zeigt jederzeit entweder [[glossar#Gesamtnennung]] oder [[glossar#Individuelle Person]] (bzw. Organisation/Ort). Umschaltung an Ort und Stelle. Prozentsätze auf beiden Ebenen verfügbar. -->

### Warum

<!-- Rechnerisches Mittel (Nennungen/Personen) täuscht Gleichverteilung vor. Tatsächlich werden die meisten Personen einmal, wenige sehr häufig genannt. Die Verteilung ist forschungsrelevant. -->

### Wie

<!-- Globaler Umschalter; aktuelle Wahl wird in Anzeigen, Diagrammen und Tabellen konsistent propagiert. -->

## Bestandsfilterung als universelle Dimension

### Was

<!-- Aussagen lassen sich jederzeit auf Gesamtbestand oder Teilbestände (einzelne [[glossar#Quellenkorpus]]) einschränken. In allen Ansichten verfügbar, nicht nur auf einer einzelnen Seite. -->

### Warum

<!-- Forschungsfragen beziehen sich regelmäßig auf Teilbestände. Ein Filter, der nur an einer Stelle verfügbar ist, bricht den Arbeitsfluss. -->

### Wie

<!-- Bestandsfilter als persistente Komponente im UI-Rahmen; Auswahl propagiert durch alle abhängigen Darstellungen. -->

## Menschen-Events-Behandlung

### Was

<!-- [[glossar#Menschen-Event]] werden nicht stillschweigend ein- oder ausgeschlossen. Nutzerin entscheidet aktiv. Einmal getroffene Entscheidung propagiert konsistent. -->

### Warum

<!-- Asymmetrische Behandlung (z. B. Einschluss bei Gesamtnennungen, Ausschluss bei individuellen Personen) kippt Relationen und macht statistische Aussagen ungültig. Der Begriff ist nicht selbsterklärend. -->

### Wie

<!-- Toggle mit Glossar-Verweis. Aktueller Zustand im Provenienz-Tooltip sichtbar. -->

## Zitierfähige Datenstände

### Was

<!-- Bestimmte Datenstände bleiben dauerhaft referenzierbar, unabhängig vom aktuellen Stand der Datenbank. -->

### Warum

<!-- Publikationen verweisen auf einen Stichtag, nicht auf einen bewegten Stand. Ohne eingefrorene Stände keine wissenschaftliche Zitierbarkeit. -->

### Wie

<!-- Persistente Identifier oder stabile URLs zu versionierten Datenständen. Datenstand in der Fußzeile sichtbar. -->

## Informationsdichte vor reduzierter Ästhetik

### Was

<!-- Leitprinzip [[ui-design#Maximaler Informations-Output]]: Nachvollziehbarkeit der Datenherkunft hat Vorrang vor reduzierter Darstellung. -->

### Warum

<!-- Das Interface bedient Fachnutzerinnen, keine Konsumnutzerinnen. Reduktion, die Provenienz verschleiert, wäre dysfunktional. -->

### Wie

<!-- Tooltips, Filtermarkierungen, Zählebenen-Anzeige immer sichtbar. Information wird nicht versteckt, um UI „sauber" zu halten. -->

## Zwei Zugangsmodi

### Was

<!-- Explorativer Modus (Überblick, Filter, Details) und klassischer Abfragemodus (vordefinierte Kombinationen) nebeneinander. -->

### Warum

<!-- Unterschiedliche Forschungssituationen: ergebnisoffenes Erkunden vs. gezielte wiederkehrende Frage. -->

### Wie

<!-- Zwei Navigationsbereiche: Exploration und Analyse. Siehe [[ui-design#Navigation]]. -->

## Siehe auch

- [[ui-design]] — wie die Anforderungen gestalterisch umgesetzt sind
- [[scholar-user-stories]] — Forschungsszenarien, aus denen die Anforderungen entstehen
- [[glossar]] — verwendete Begriffe
