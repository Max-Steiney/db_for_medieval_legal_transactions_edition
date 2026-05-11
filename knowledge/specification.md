---
title: Spezifikation
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.3
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

# Spezifikation

Was das User Interface heute leistet, formuliert aus der Perspektive von
Historiker*innen, die mit dem Quellenkorpus arbeiten. Fünf
zusammengefasste User-Stories tragen das Dokument, eine Sektion am Ende
hält die Querschnitts-Eigenschaften des Werkzeugs fest. Geplante
Erweiterungen stehen im [[journal]], nicht hier.

## Eine Person über ihre Quellen und Rollen verfolgen

* Rolle Prosopografin oder Sozialhistorikerin
* Wunsch eine konkrete Person identifizieren und ihren vollständigen Aktenspiegel sehen
* Zweck den Lebensweg, die Rollenverteilung und die Quellenbasis einer Person nachvollziehen
* Eingelöst durch Personenregister mit Filtern nach Geschlecht, Rolle, Aktivitätszeitraum und Korpus
* Eingelöst durch Personenprofil mit Stammdaten, Belegzeitraum, Wortlaut-Bezeichnungen und externen Authority-Links
* Eingelöst durch sortierbare Quellen-Tabelle auf dem Profil mit Signatur, Datum, Korpus, Bezeichnung und Rolle
* Eingelöst durch zitierfähiger Datenstand im Footer und Citation-Helper auf der Quellen-Detailseite

## Die Beziehungen einer Person erkunden

* Rolle Sozialhistorikerin oder Genealogin
* Wunsch das Beziehungsnetz einer Person sichtbar machen, Verwandtschaft, Beruf, Stand, Vertretung, Freundschaft
* Zweck zentrale Akteure, Familienkonstellationen und soziale Verflechtungen rekonstruieren
* Eingelöst durch Beziehungs-Sektion im Personenprofil, pro Beziehungstyp eine sortierbare Tabelle mit Bezeichnung, Perspektive und Quellen-Beleg
* Eingelöst durch Mirror-Beziehungen, Personen mit Amt oder Titel im Bezug zur gerade angesehenen Person tauchen automatisch auf
* Eingelöst durch Personennetzwerk als Ego-Layout, eine Person im Zentrum, ihre direkten Verbindungen radial, Klick auf einen Nachbarn verlagert das Zentrum
* Eingelöst durch Beziehungstyp-Chips zum Aus- und Einblenden einzelner Beziehungsarten

## Rechtsgeschäfte nach Geschlecht und Rolle vergleichen

* Rolle Genderforscherin oder Wirtschaftshistoriker
* Wunsch sehen, wie sich Funktionsrollen, Transaktionstypen und Beziehungstypen nach Geschlecht verteilen und wie sich diese Verteilungen über die Zeit verschieben
* Zweck strukturelle Asymmetrien zwischen Frauen und Männern im spätmittelalterlichen Wiener Rechtsleben quantifizieren
* Eingelöst durch Auswertungs-Seite mit Donut-Diagrammen für Funktionsrollen und Beziehungstypen, gestapelt nach Geschlecht
* Eingelöst durch Top-Bezeichnungen-Tabelle, normalisierte Berufsbezeichnungen mit Geschlechter-Bar pro Bezeichnung
* Eingelöst durch Zeitstrom als gestapelten Bar-Chart pro Jahrzehnt, Stack-Achse umschaltbar zwischen Korpus, Geschlüsselungsform, Geschlecht und Transaktionstyp
* Eingelöst durch Brush-Auswahl im Zeitstrom, ein Zeitabschnitt lässt sich aufziehen und seine Quellen erscheinen darunter

## Organisationen und ihre Mitglieder analysieren

* Rolle Stadtforscherin oder Institutionengeschichte
* Wunsch eine Organisation öffnen und sehen, welche Personen ihr als Amtsträger, Mitglieder oder durch Berufs-Stand-Beziehung zugeordnet sind
* Zweck Hofstrukturen, Klosterzusammensetzungen oder Zunftbestand rekonstruieren
* Eingelöst durch Organisationsregister mit Filtern nach Typ und Korpus
* Eingelöst durch Organisationsprofil parallel zum Personenprofil, mit Quellen-Tabelle und zugeordneten Personen
* Eingelöst durch Verlinkung der Personen aus der Organisations-Seite in deren Personenprofile und zurück
* Eingelöst durch Personennetzwerk-Darstellung der Berufs-Stand-Beziehungen als Knoten anderer Farbe

## Quellen ausschnitthaft sammeln, teilen und exportieren

* Rolle Editionsbearbeiterin oder Forscherin auf einem konkreten Projekt
* Wunsch einen Teilbestand zusammenstellen, ihn als Permalink mit Kolleginnen teilen oder in eine Tabellen- oder Bibliografiesoftware übernehmen
* Zweck eine Arbeitssammlung anlegen, eine Reviewerin auf dieselbe Datensicht führen, oder das Material in einer externen Datenbank weiterverarbeiten
* Eingelöst durch Filter auf der Quellenliste, Korpus, Zeitraum, Ort, Geschlechter-Mix, Erschließungsform, Faksimile
* Eingelöst durch URL-Sync der Filterzustände auf den Visualisierungs-Seiten, eine kopierte URL stellt den Filterkontext wieder her
* Eingelöst durch clientseitiger Datenkorb für Quellen, Personen und Organisationen über Sitzungen hinweg
* Eingelöst durch CSV-Export pro Typklasse aus dem Datenkorb
* Eingelöst durch Cross-Page-Sprung von einer Visualisierung in die Quellenliste mit übernommenem Filterkontext

## Querschnitts-Eigenschaften

Eigenschaften, die für alle fünf User-Stories gleichermaßen
gelten und nicht einer einzelnen zugeordnet werden können.

### Datenrobustheit und Provenienz

Aggregierte Zahlen tragen auf Startseite, Auswertungen und
Korpus-Zählern einen Provenienz-Tooltip, der den zugrunde liegenden
Bestand und die Zähloperation benennt. Die Rückführung auf
die Quelldokumente läuft über die in
[[architecture#Provenienz-Indizes]] beschriebenen Indizes. Das
Tip-System umfasst vier Klassen, Provenienz, Glossar-Definition,
UI-Hilfe und schneller Hover-Hint, siehe [[ui-design#Tip-System]].

### Verifizierbarkeit

Drei Verifikations-Stufen unter `verification/` prüfen die im
Frontend dargestellten Zahlen und Annotationen unabhängig vom
Build-Lauf gegen die TEI-Quellen und Register-XMLs. Befunde, die in der
Edition nicht behoben werden können, sind in
`verification/findings.md` namentlich dokumentiert. Architektur in
[[architecture#Test-Strategie]].

### Barrierefreiheit

Das UI ist mit Tastatur und Screen-Reader bedienbar und erfüllt die
zentralen WCAG-2.1-AA-Kriterien. Sprachauszeichnung, Skip-Link,
sichtbarer Tastatur-Fokus, semantische Landmark-Struktur,
Heading-Hierarchie, ARIA-Live-Regions für dynamische
Trefferzahlen, `aria-sort` auf sortierbaren Tabellenspalten, Focus-Trap
und Return-Focus im Drill-down-Overlay, Hover-Hints auch über
Tastatur-Fokus erreichbar, Kontrast-Tokens auf AA-Niveau,
`prefers-reduced-motion` reduziert Animationen.

### Zitierfähiger Datenstand

Der aktuelle Datenstand ist in der Fußzeile jeder Seite als Datum
des letzten Commits im Pipeline-Repo sichtbar, in lesbarer Langform. Er
ist damit der Stand der Quellen, nicht der Zeitpunkt des Build-Laufs.
Umsetzung in [[architecture#Datenstand aus dem Pipeline-Repo]],
UI-Ausprägung in [[ui-design#Datenstand und Build-Datum]].

### Informationsdichte vor reduzierter Ästhetik

Leitprinzip des Designs. Ausführung in
[[ui-design#Leitprinzip Maximaler Informations-Output]],
Entscheidungshintergrund in
[[decisions#Maximaler Informations-Output als Gestaltungsleitlinie]].

## Siehe auch

* [[ui-design]] wie die User-Stories gestalterisch umgesetzt sind
* [[scholar-user-stories]] ausführliche Forschungsszenarien hinter den fünf Stories
* [[glossar]] verwendete Begriffe
* [[journal]] chronologische Notizen zu Umsetzung und geplanten Erweiterungen
