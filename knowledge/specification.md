---
title: Spezifikation
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.5
created: 2026-02-19
updated: 2026-05-16
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
Historiker*innen, die mit dem Quellenkorpus arbeiten. Sieben
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

## Personenkonstellationen über kombinierte Bedingungen abfragen

* Rolle Prosopografin, Sozialhistorikerin oder Rechtshistoriker
* Wunsch alle Rechtsgeschäfte finden, in denen eine spezifische Konstellation aus mehreren Personen mit jeweils eigenen Rollen und Merkmalen gleichzeitig auftritt, etwa männliche Aussteller in einer bestimmten Berufsgruppe zusammen mit weiblichen Empfängerinnen einer anderen
* Zweck typische Akteurskonstellationen identifizieren, Hypothesen über soziale Verflechtungen prüfen, einen kuratierten Quellen-Ausschnitt für die Detailauswertung erzeugen
* Eingelöst durch Abfrage-Sub-Seite mit beliebig vielen nummerierten Personen-Bedingungen, je mit Rolle (Aussteller, Empfänger, Zeuge oder Siegler, sonstige) und optional Geschlecht und Beruf/Tätigkeit/Amt
* Eingelöst durch Beruf-Bedingung als Freitext mit Operator „enthält" auf der Originalschreibung des Quellenwortes, mit smarten Vorschlägen aus den häufigsten Originalvarianten samt Belegzahl
* Eingelöst durch globale Filter Zeitraum, Quellenkorpus und Verknüpfungs-Modus, der wählt, ob alle Bedingungen im selben Rechtsgeschäft oder in derselben Quelle erfüllt sein müssen
* Eingelöst durch live aktualisierte Treffer-Tabelle mit Datum, Quelle, Korpus, einer Pille je Personenblock und Rechtsgeschäfts-Typ; leerer Anfangszustand, solange keine Bedingung gesetzt ist
* Eingelöst durch zitierfähigem Permalink, der die gesamte Abfrage in der URL serialisiert
* Eingelöst durch CSV-Export der angezeigten Tabelle für die Weiterverarbeitung in externen Werkzeugen
* Eingelöst durch Datenkorb-Anbindung pro Zeile, damit Treffer in das übergreifende Forschungskorbsystem fließen

## Forschungsfragen aus der editorischen Praxis beantworten

* Rolle Stadt- oder Sozialhistorikerin mit konkretem Erkenntnisinteresse
* Wunsch eine prosopografische oder netzwerkbezogene Frage stellen und die Antwort als Zahlen plus Quellenliste bekommen, ohne SQL oder externe Tools
* Zweck typische Forschungsfragen wie „Welche Personen einer Berufsgruppe sind untereinander verheiratet", „Welche Personen sind durch Tätigkeit an eine Institution gebunden plus deren Verwandte", „Wer steht in einem Stifter-Empfänger-Verhältnis zu einer bestimmten Organisation" direkt im UI durchspielen
* Eingelöst durch Galerie konkreter Forschungsfragen unter `/analysis/index.html` mit Frage-Text, Antwort als Visualisierung und Provenienz
* Eingelöst durch Sektionen auf dem Organisationsprofil, die das Stiftungsnetzwerk und die Tätigkeitsverbindungen aus dem heutigen Aggregat ableiten
* Eingelöst durch Uhlirz-Berufsklassifikation aus `normalisation_lists/roleName_norm_matching.csv` (Spalte `Gewerbe_nach_Uhlirz_GstW`) als Filter- und Gruppierungs-Achse
* Eingelöst durch Heirats-Begriffs-Match auf den freien Verwandtschafts-Bezeichnungen in `kin_relations_in_sources.csv`

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

Eigenschaften, die für alle sieben User-Stories gleichermaßen
gelten und nicht einer einzelnen zugeordnet werden können.

### Zitierbares Build-Profil

Jede aggregierte Zahl im Frontend ist Aussage unter einer bestimmten Stufe. Vier benannte Stufen bündeln Korpus-Auswahl und Annotationsebenen als zitierbares Profil: Publikation (Stufe 1), Vergleich mit mentioned events (Stufe 2), voller `_ready`-Bestand (Stufe 3), Maximalversion (Stufe 4). Konzept in [[decisions#Stufenmodell für Korpus-Auswahl und Annotationsebenen]], CLI-Mechanik in `frontend/stages.py`.

### Datenpfad-Ehrlichkeit

Filterbedingungen und Achsenwerte im UI werden nur angeboten, wenn sie in den Daten tatsächlich existieren und das TEI-Annotationsmodell sie trennscharf führt. Ein Filter „Titel ist Herr" wird beispielsweise auf der Abfragen-Sub-Seite nicht angeboten, weil die TEI-Edition Honorifics und Berufe in einer einzigen Annotation zusammenführt. Eine derartige Bedingung müsste zuerst im Schwester-Repo als eigene Spalte angelegt werden. Bedingungen mit nur einer Schreibweise im Datenbestand (Originalform) werden explizit als solche gekennzeichnet, damit Forscherinnen das Trefferbild korrekt einordnen.

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
* [[scholar-user-stories]] ausführliche Forschungsszenarien hinter den sieben Stories
* [[glossar]] verwendete Begriffe
* [[journal]] chronologische Notizen zu Umsetzung und geplanten Erweiterungen
