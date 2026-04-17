# Anforderungen

Funktionale und nicht-funktionale Anforderungen an das User Interface. Pro Anforderung ein Abschnitt im Muster Was, Warum, Wie.

## Datenrobustheit und Provenienz

### Was

Jede dargestellte Zahl ist transparent in Herkunft und Berechnung und reproduzierbar für Nutzerinnen, die sie gegen eine andere Quelle prüfen wollen.

### Warum

Wissenschaftliche Verwendbarkeit hängt an Reproduzierbarkeit. Eine Zahl, die korrekt ist, aber nicht nachvollzogen werden kann, ist für Publikationen unbrauchbar, weil sie sich gegen niemanden verteidigen lässt.

### Wie

An jedem Datenpunkt steht eine Herkunftsanzeige zur Verfügung, die den zugrunde liegenden Bestand, die Zähloperation, den [[glossar#Menschen-Event]]-Status und die aktiven Filter sichtbar macht. Siehe [[ui-design#Provenienz-Tooltip]]. Die Rückführung auf die Quelldokumente einer aggregierten Zahl läuft technisch über [[architecture#Provenienz-Indizes]].

Zusätzlich verifiziert das [[architecture#Verifikations-Test-Set]] unabhängig von der Pipeline, dass jede im Frontend dargestellte Zahl mit den TEI-Quellen und Register-XMLs konsistent ist. Diskrepanzen deuten auf Fehler in Aggregation, Labeling oder Datenlücken hin und werden als solche sichtbar gemacht.

## Umschaltbarkeit der Zählebenen

### Was

Das UI zeigt an jeder Stelle entweder [[glossar#Gesamtnennung]] oder [[glossar#Individuelle Person]] und lässt die Umschaltung ohne Kontextverlust zu. Prozentangaben sind auf beiden Ebenen verfügbar.

### Warum

Das rechnerische Mittel aus Nennungen und Personen täuscht eine Gleichverteilung vor, die nicht besteht. Die tatsächliche Verteilung ist stark asymmetrisch. Die wenigen häufig genannten Personen sind forschungsrelevant, weil ihre Frequenz auf zentrale gesellschaftliche Funktionsträger verweist.

### Wie

Ein globaler Umschalter propagiert die Wahl durch alle abhängigen Darstellungen. Die aktuell gewählte Ebene ist im Provenienz-Tooltip jeder Zahl sichtbar. Siehe [[ui-design#Zählebenen-Umschalter]].

## Bestandsfilterung als universelle Dimension

### Was

Aussagen lassen sich jederzeit auf den Gesamtbestand oder auf einzelne [[glossar#Quellenkorpus|Quellenkorpora]] einschränken. Der Filter ist in allen Ansichten verfügbar, nicht nur auf einer Einstiegsseite.

### Warum

Forschungsfragen beziehen sich regelmäßig auf Teilbestände. Ein Filter, der nur an einer Stelle greift, zwingt Nutzerinnen, den Zustand bei jedem Ansichtswechsel manuell zu rekonstruieren.

### Wie

Der Bestandsfilter ist persistente Komponente im UI-Rahmen. Die Auswahl propagiert durch alle abhängigen Darstellungen und bleibt bei Navigation erhalten. Siehe [[ui-design#Bestandsfilter]].

## Menschen-Events-Behandlung

### Was

[[glossar#Menschen-Event|Menschen-Events]] werden nicht stillschweigend ein- oder ausgeschlossen. Nutzerinnen treffen die Entscheidung aktiv, und die gewählte Option gilt konsistent für alle abhängigen Abfragen.

### Warum

Eine asymmetrische Behandlung (Einbeziehung in einer Zahl, Ausschluss in einer anderen) verändert Verhältnisse und macht Vergleiche ungültig. Der Begriff ist außerhalb des Projekts nicht etabliert, also braucht die Nutzerin an der Oberfläche eine Erklärung.

### Wie

Ein Toggle mit Glossar-Verweis ist sichtbar platziert. Der aktuelle Zustand steht im Provenienz-Tooltip jeder Zahl. Siehe [[ui-design#Menschen-Events-Toggle]].

## Zitierfähige Datenstände

### Was

Bestimmte Datenstände bleiben dauerhaft referenzierbar, unabhängig vom aktuellen Stand der wachsenden Datenbank.

### Warum

Publikationen verweisen auf einen Stichtag, nicht auf einen bewegten Stand. Ohne eingefrorene Datenstände kann eine in einer Zeitschrift gedruckte Zahl später nicht mehr überprüft werden.

### Wie

Persistente Identifier oder stabile URLs zu versionierten Datenständen werden im UI ausgewiesen. Der aktuelle Datenstand ist in der Fußzeile jeder Seite sichtbar. Siehe [[ui-design#Zitierbarkeit einzelner Ansichten]].

## Informationsdichte vor reduzierter Ästhetik

Leitprinzip des Designs. Ausführung und Begründung in [[ui-design#Leitprinzip Maximaler Informations-Output]]. Entscheidungshintergrund in [[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Siehe auch

- [[ui-design]] wie die Anforderungen gestalterisch umgesetzt sind
- [[scholar-user-stories]] Forschungsszenarien, aus denen die Anforderungen entstehen
- [[glossar]] verwendete Begriffe
