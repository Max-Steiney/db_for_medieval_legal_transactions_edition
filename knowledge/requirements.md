---
title: Anforderungen
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
topics: ["[[Requirements Engineering]]"]
related: [scholar-user-stories, decisions, ui-design, architecture]
---

# Anforderungen

Funktionale und nicht-funktionale Anforderungen an das User Interface. Pro Anforderung ein Abschnitt im Muster Was, Warum, Wie.

## Datenrobustheit und Provenienz

### Was

Jede dargestellte Zahl ist transparent in Herkunft und Berechnung und reproduzierbar für Nutzerinnen, die sie gegen eine andere Quelle prüfen wollen.

### Warum

Wissenschaftliche Verwendbarkeit hängt an Reproduzierbarkeit. Eine Zahl, die korrekt ist, aber nicht nachvollzogen werden kann, ist für Publikationen unbrauchbar, weil sie sich gegen niemanden verteidigen lässt.

### Wie

An jedem Datenpunkt steht eine Herkunftsanzeige zur Verfügung, die den zugrunde liegenden Bestand, die Zähloperation, den [[glossar#Menschen-Event]]-Status und die aktiven Filter sichtbar macht. Siehe [[ui-design#Provenienz-Tip und Glossar-Tip]]. Die Rückführung auf die Quelldokumente einer aggregierten Zahl läuft technisch über [[architecture#Provenienz-Indizes]].

Zusätzlich verifiziert das [[architecture#Verifikations-Test-Set]] unabhängig von der Pipeline, dass jede im Frontend dargestellte Zahl mit den TEI-Quellen und Register-XMLs konsistent ist. Diskrepanzen deuten auf Fehler in Aggregation, Labeling oder Datenlücken hin und werden als solche sichtbar gemacht.

## Umschaltbarkeit der Zählebenen

### Was

Das UI zeigt an jeder Stelle entweder [[glossar#Gesamtnennung]] oder [[glossar#Individuelle Person]] und lässt die Umschaltung ohne Kontextverlust zu. Prozentangaben sind auf beiden Ebenen verfügbar.

### Warum

Das rechnerische Mittel aus Nennungen und Personen täuscht eine Gleichverteilung vor, die nicht besteht. Die tatsächliche Verteilung ist stark asymmetrisch. Die wenigen häufig genannten Personen sind forschungsrelevant, weil ihre Frequenz auf zentrale gesellschaftliche Funktionsträger verweist.

### Wie

Ein globaler Umschalter propagiert die Wahl durch alle abhängigen Darstellungen. Die aktuell gewählte Ebene ist im Provenienz-Tooltip jeder Zahl sichtbar. Siehe [[ui-design#Zählebenen-Umschalter]].

Status: konzeptionell formuliert, im UI noch nicht als globale Komponente umgesetzt. Lokal wirkt eine Zähleinheit-Umschaltung in der Funktionsrollen-Sektion der Auswertungs-Seite. Die universelle Propagierung über alle Visualisierungen ist als Phase-2-Aufgabe im journal vermerkt.

## Bestandsfilterung als universelle Dimension

### Was

Aussagen lassen sich jederzeit auf den Gesamtbestand oder auf einzelne [[glossar#Quellenkorpus|Quellenkorpora]] einschränken. Der Filter ist in allen Ansichten verfügbar, nicht nur auf einer Einstiegsseite.

### Warum

Forschungsfragen beziehen sich regelmäßig auf Teilbestände. Ein Filter, der nur an einer Stelle greift, zwingt Nutzerinnen, den Zustand bei jedem Ansichtswechsel manuell zu rekonstruieren.

### Wie

Der Bestandsfilter ist persistente Komponente im UI-Rahmen. Die Auswahl propagiert durch alle abhängigen Darstellungen und bleibt bei Navigation erhalten. Siehe [[ui-design#Bestandsfilter]].

Status: derzeit wirkt der Filter nur auf der Quellen-Übersicht. Eine universelle Propagierung über Auswertungen, Zeitstrom, Personennetzwerk und Register ist als Phase-2-Aufgabe offen, weil die Aggregate dafür eine zusätzliche Unterschlüsselung nach Quellenkorpus tragen müssten.

## Menschen-Events-Behandlung

### Was

[[glossar#Menschen-Event|Menschen-Events]] werden nicht stillschweigend ein- oder ausgeschlossen. Nutzerinnen treffen die Entscheidung aktiv, und die gewählte Option gilt konsistent für alle abhängigen Abfragen.

### Warum

Eine asymmetrische Behandlung (Einbeziehung in einer Zahl, Ausschluss in einer anderen) verändert Verhältnisse und macht Vergleiche ungültig. Der Begriff ist außerhalb des Projekts nicht etabliert, also braucht die Nutzerin an der Oberfläche eine Erklärung.

### Wie

Ein Toggle mit Glossar-Verweis ist sichtbar platziert. Der aktuelle Zustand steht im Provenienz-Tooltip jeder Zahl. Siehe [[ui-design#Menschen-Events-Toggle]].

Status: nicht implementiert. Die Default-Variante schließt Personen-Annotationen in verschachtelten Events aus der Nennungszählung aus, siehe [[decisions#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]]; eine umschaltbare Anzeige für die inklusive Variante ist Phase-2-Aufgabe.

## Zitierfähige Datenstände

### Was

Sowohl der Datenstand der Quellen als auch der Filter-Stand einer Ansicht bleiben dauerhaft referenzierbar — der eine als Stichtag der zitierten Daten, der andere als zitierter Forschungsstand.

### Warum

Publikationen verweisen auf einen Stichtag, nicht auf einen bewegten Stand. Ohne eingefrorene Datenstände kann eine in einer Zeitschrift gedruckte Zahl später nicht mehr überprüft werden. Und ohne stabile Filter-Permalinks kann eine Reviewerin die Aussage nicht auf derselben Datensicht prüfen, auf der die Autorin sie formuliert hat.

### Wie

Persistente Identifier oder stabile URLs zu versionierten Datenständen werden im UI ausgewiesen. Der aktuelle Datenstand ist in der Fußzeile jeder Seite sichtbar als Datum des letzten Commits im Pipeline-Repo, in lesbarer Langform. Er ist damit der Stand der Quellen, nicht der Zeitpunkt des Build-Laufs. Umsetzung in [[architecture#Datenstand aus dem Pipeline-Repo]], UI-Ausprägung in [[ui-design#Datenstand und Build-Datum]] und [[ui-design#Zitierbarkeit einzelner Ansichten]].

Der Filter-Stand wird auf den Daten-Visualisierungs-Seiten in die URL-Suchparameter serialisiert; eine kopierte URL stellt den vollständigen Filter-Kontext beim Aufruf wieder her. Architektur in [[architecture#URL-State als Forschungsstand]], UI-Ausprägung in [[ui-design#URL-State-Sync]].

## Wiederverwendbarkeit der Auswahl

### Was

Eine Forscherin kann eine über mehrere Ansichten verteilte Auswahl aus Quellen, Personen und Organisationen sammeln, persistieren und in externe Werkzeuge exportieren.

### Warum

Forschungspfade sind nicht linear. Eine Auswahl entsteht häufig durch Querstreifzüge zwischen Drill-down-Overlay, Brush-Auswahl, Quellen-Liste, Profilseiten und Register-Listen. Ohne ein sammelndes Vehikel zerfällt die zwischenstehende Arbeit beim Tab-Wechsel, und der Übergang in eine Bibliografie- oder Tabellen-Software erzwingt manuelles Abschreiben.

### Wie

Ein clientseitiger Datenkorb sammelt Quellen, Personen und Organisationen über Sitzungen hinweg. Eine im Korb liegende Quelle zieht ihre annotierten Personen und Organisationen automatisch als abgeleitete Einträge nach. Umsetzung in [[ui-design#Datenkorb]], Architektur in [[architecture#Datenkorb als clientseitige Persistenz]], Begründung in [[decisions#Datenkorb als clientseitige Sammlung]].

## Informationsdichte vor reduzierter Ästhetik

Leitprinzip des Designs. Ausführung und Begründung in [[ui-design#Leitprinzip Maximaler Informations-Output]]. Entscheidungshintergrund in [[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Siehe auch

- [[ui-design]] wie die Anforderungen gestalterisch umgesetzt sind
- [[scholar-user-stories]] Forschungsszenarien, aus denen die Anforderungen entstehen
- [[glossar]] verwendete Begriffe
