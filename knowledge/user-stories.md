---
title: User Stories
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 1.1
created: 2026-02-19
updated: 2026-05-17
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Scholar-Centered Design]]", "[[User Stories]]"]
related: [specification, ui-design, analyse, exploration, glossar]
---

# User Stories

Konzeptionelles Dokument zu den Forschungsszenarien, die das Fachteam an die Datenbank trägt. Beschreibt, was Forscher*innen mit dem Material untersuchen wollen, und ordnet jedes Szenario den Anforderungen, Komponenten und Begriffen zu, die es einlöst.

Vier Schichten:

1. **Anwendungs-Stories** — die großen Forschungsszenarien, die das UI als Ganzes adressiert
2. **Konkrete Forschungsfragen aus der editorischen Praxis** — die prototypischen Fragen, an denen die Anwendung sich misst, als inhaltliche Konkretisierung der Anwendungs-Story zu Forschungsfragen
3. **Granulare Forschungsoperationen** — kleinere Arbeitsschritte, die in den Anwendungs-Stories aufgehen
4. **Wissenschaftliche Absicherung** — Stories, die Provenienz, Reproduzierbarkeit und Zitierbarkeit beim Forschen betreffen

Die Stories sind beschreibend, kein Backlog. Implementierungsstand, datenseitige Limitierungen und offene Befunde leben nicht hier, sondern in [verification/findings.md](../verification/findings.md) und im [[journal]].

---

# 1 Anwendungs-Stories

Sechs große Forschungsszenarien aus Historiker*innen-Perspektive. Pro Story Rolle, Wunsch, Zweck und die Komponenten der Anwendung, die das Szenario einlösen.

## Eine Person über ihre Quellen und Rollen verfolgen

* **Rolle** Prosopografin oder Sozialhistorikerin
* **Wunsch** eine konkrete Person identifizieren und ihren vollständigen Aktenspiegel sehen
* **Zweck** den Lebensweg, die Rollenverteilung und die Quellenbasis einer Person nachvollziehen
* **Eingelöst durch** Personenregister mit Filtern nach Geschlecht, Rolle, Aktivitätszeitraum und Korpus; Personenprofil mit Stammdaten, Belegzeitraum, Wortlaut-Bezeichnungen, externen Authority-Links und sortierbarer Quellen-Tabelle; zitierfähiger Datenstand im Footer
* **Anforderung** [[specification#Personen- und Organisationsprofile als Detailseiten]], [[specification#Zitierfähiger Datenstand]]

## Die Beziehungen einer Person erkunden

* **Rolle** Sozialhistorikerin oder Genealogin
* **Wunsch** das Beziehungsnetz einer Person sichtbar machen, Verwandtschaft, Beruf, Stand, Vertretung, Freundschaft
* **Zweck** zentrale Akteure, Familienkonstellationen und soziale Verflechtungen rekonstruieren
* **Eingelöst durch** Beziehungs-Sektion im Personenprofil pro Beziehungstyp; Mirror-Beziehungen (Personen mit Amt oder Titel im Bezug zur aktuellen Person tauchen automatisch auf); Personennetzwerk als Ego-Layout mit Klick-Hopping; Beziehungstyp-Chips zum Aus- und Einblenden
* **Anforderung** [[specification#Personen- und Organisationsprofile als Detailseiten]]

## Rechtsgeschäfte nach Geschlecht und Rolle vergleichen

* **Rolle** Genderforscherin oder Wirtschaftshistoriker
* **Wunsch** sehen, wie sich Funktionsrollen, Transaktionstypen und Beziehungstypen nach Geschlecht verteilen und wie sich diese Verteilungen über die Zeit verschieben
* **Zweck** strukturelle Asymmetrien zwischen Frauen und Männern im spätmittelalterlichen Wiener Rechtsleben quantifizieren
* **Eingelöst durch** Auswertungs-Seite mit Donut-Diagrammen, gestapelt nach Geschlecht; Top-Bezeichnungen-Tabelle mit Geschlechter-Bar; Zeitstrom als gestapelter Bar-Chart pro Jahrzehnt mit umschaltbarer Stack-Achse und Brush-zu-Drill-down
* **Anforderung** [[specification#Auswertungen gehört in den Analyse-Bereich]], [[specification#Exploration und Analyse als getrennte Bereiche]]

## Organisationen und ihre Mitglieder analysieren

* **Rolle** Stadtforscherin oder Institutionengeschichte
* **Wunsch** eine Organisation öffnen und sehen, welche Personen ihr als Amtsträger, Mitglieder oder durch Berufs-Stand-Beziehung zugeordnet sind
* **Zweck** Hofstrukturen, Klosterzusammensetzungen oder Zunftbestand rekonstruieren
* **Eingelöst durch** Organisationsregister mit Filtern; Organisationsprofil parallel zum Personenprofil mit Quellen-Tabelle und zugeordneten Personen; bidirektionale Verlinkung zwischen Personen- und Organisationsprofilen; Personennetzwerk-Darstellung der Berufs-Stand-Beziehungen
* **Anforderung** [[specification#Personen- und Organisationsprofile als Detailseiten]]

## Personenkonstellationen über kombinierte Bedingungen abfragen

* **Rolle** Prosopografin, Sozialhistorikerin oder Rechtshistoriker
* **Wunsch** alle Rechtsgeschäfte finden, in denen eine spezifische Konstellation aus mehreren Personen mit jeweils eigenen Rollen und Merkmalen gleichzeitig auftritt
* **Zweck** typische Akteurskonstellationen identifizieren, Hypothesen über soziale Verflechtungen prüfen, einen kuratierten Quellen-Ausschnitt für die Detailauswertung erzeugen
* **Eingelöst durch** Abfrage-Sub-Seite mit beliebig vielen nummerierten Personen-Bedingungen; Beruf-Bedingung als Freitext mit smarten Vorschlägen; globale Filter Zeitraum, Quellenkorpus und Verknüpfungs-Modus; live aktualisierte Treffer-Tabelle; zitierfähiger Permalink; CSV-Export; Datenkorb-Anbindung pro Zeile
* **Anforderung** [[specification#Abfragen-Sub-Seite als Konstellations-Abfrage]]

## Quellen, Personen und Organisationen sammeln, teilen und exportieren

* **Rolle** Editionsbearbeiterin oder Forscherin auf einem konkreten Projekt
* **Wunsch** einen Teilbestand aus verschiedenen Achsen zusammenstellen (Bezeichnungs-Suche, Zeitstrom-Brush, Personennetzwerk, Register-Listen, Detail- und Profilseiten), ihn als Permalink mit Kolleginnen teilen oder in eine Tabellen- oder Bibliografiesoftware übernehmen
* **Zweck** eine Arbeitssammlung anlegen, eine Reviewerin auf dieselbe Datensicht führen, oder das Material in einer externen Datenbank weiterverarbeiten
* **Eingelöst durch** Filter auf der Quellenliste mit URL-Sync der Filterzustände; clientseitigen Datenkorb für drei Item-Typen (Quellen, Personen, Organisationen) mit Cross-Tab-Sync; CSV-Export pro Typklasse; Cross-Page-Sprung von einer Visualisierung in die Quellenliste mit übernommenem Filterkontext
* **Pfad** An jedem Eintrag in den Listen und an jeder Detail- und Profilseite steht ein „+"-Knopf, der den Eintrag in den Datenkorb legt. Das Korb-Icon im Nav führt zur Korb-Seite mit drei Sektionen, jeweils eigener Remove-Aktion und eigenem CSV-Export. Wer eine Quelle in den Korb legt, sieht ihre annotierten Personen und Organisationen automatisch als abgeleitete Einträge — ein zweiter „+"-Klick stuft sie zur eigenständigen Sammlung hoch.
* **Anforderung** [[specification#Datenkorb als clientseitige Sammlung]], [[specification#Forschungsstand zitierbar via URL-Parameter]], [[specification#Cross-Page-Sprung mit Filter-Übernahme]]
* **Komponente** [[ui-design#Datenkorb]]

---

# 2 Konkrete Forschungsfragen aus der editorischen Praxis

Vier Fragen, die das Fachteam an die Datenbasis stellt. Sie sind die inhaltliche Konkretisierung der Anwendungs-Story über Forschungsfragen ([[specification#Forschungsfragen als Implementierungs-Achse]]): prototypisch für eine ganze Klasse ähnlicher Fragen und prägen die Galerie unter `/analysis/index.html` sowie die Sektionen der Organisationsprofile. Datenbasis und Komponente pro Frage benannt, damit nachvollziehbar bleibt, woraus die Antwort entsteht.

## Endogamie in einer Berufsgruppe

*Als Forscherin, die Heiratsstrategien innerhalb von Handwerkergruppen untersuche, will ich alle Personen erkennen, die einer bestimmten Uhlirz-Berufskategorie zugeordnet sind und untereinander durch Heirat verbunden sind, damit ich Endogamie-Muster im spätmittelalterlichen Wiener Gewerbe rekonstruieren kann.*

* **Datenbasis** Uhlirz-Spalte `Gewerbe_nach_Uhlirz_GstW` in `roleName_norm_matching.csv`; Verwandtschaft in `kin_relations_in_sources.csv` mit freier deutscher Bezeichnung („Gemahlin", „Hausfrau", „Gatte"); Match-Liste für Heirat
* **Komponente** Galerie-Frage in [[analyse]]
* **Beispiel** Uhlirz IV (Erzeugung und Vertrieb von Leuchtstoffen, Fetten, Ölen) plus Heirats-Beziehung

## Berufsgruppe und Hausbesitz

*Als Forscherin, die die topographische Verteilung eines Gewerbes untersuche, will ich alle Personen einer Berufskategorie auflisten und ihre Hausbesitz-Orte als Tabelle mit Datum und Quelle einsehen, damit ich räumliche Verdichtungen erkenne.*

* **Datenbasis** Uhlirz-Spalte; `owner_relations_in_sources.csv`; `placeList.xml` (Koordinaten teilweise vorhanden)
* **Komponente** Galerie-Frage in [[analyse]] als Tabelle
* **Beispiel** Uhlirz VI (Lederindustrie) plus Hausbesitz; Kartendarstellung deferred, Tabelle zeigt Lat/Lon-Spalte

## Tätigkeitsverbindung zu einer Institution plus Verwandte

*Als Forscherin, die das soziale Umfeld einer geistlichen Institution untersuche, will ich auf dem Organisationsprofil alle Personen sehen, die als Kaplan, Chorherr, Verweser oder in vergleichbarer Funktion an die Institution gebunden sind, mit Link auf das Personenprofil, wo ich ihre Verwandten finde, damit ich die klerikal-soziale Verflechtung rekonstruiere.*

* **Datenbasis** `occ_relations_in_sources.csv` (Person → Org mit Tätigkeitsbegriff); `kin_relations_in_sources.csv`
* **Komponente** Sektion „Personen mit Tätigkeitsverbindung" auf jeder Organisations-Profilseite ([[ui-design#Entitäts-Profilseite]])
* **Beispiel** St. Stephan in Wien plus alle Sub-Orgs (Altäre, Messen, Zechen, Kapellen)

## Stifter-Empfänger-Netzwerk einer Organisation

*Als Klosterforscherin, die das Stifternetzwerk einer Klosterkirche rekonstruiere, will ich auf dem Organisationsprofil alle Personen und Organisationen sehen, die in einem Issuer-Recipient-Verhältnis zu dieser Institution stehen, damit ich nachvollziehe, wer ihr Stiftungen zugewendet hat.*

* **Datenbasis** `persons_in_events.csv` und `orgs_in_events.csv` mit Rolle Issuer/Recipient; Org-Hierarchie in `orgList.xml`
* **Komponente** Sektion „Stiftungsnetzwerk" auf jeder Organisations-Profilseite ([[ui-design#Entitäts-Profilseite]])
* **Beispiel** St. Agnes auf der Himmelpforte (Wien, Augustinerinnen)

---

# 3 Granulare Forschungsoperationen

Kleinere Arbeitsschritte, die in den Anwendungs-Stories aufgehen, aber als eigenständige Operationen benannt sind, weil Forscher*innen sie als Mikropraxis erkennen.

## Verteilung einer Kategorie überblicken

*Als Forscherin, die Häufigkeitsstrukturen in einer Kategorie untersucht, will ich jederzeit zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]] umschalten, damit ich Frequenz und Breite sauber voneinander trennen kann.*

* **Komponente** lokale Zähleinheit-Umschaltung auf der [[analyse#Zwei Sub-Seiten|Auswertungs-Sub-Seite]] (Sektion Funktionsrollen); eine globale Umschaltung ist fachlich nur in dieser Sektion tragend
* **Begriffe** [[glossar#Gesamtnennung]], [[glossar#Individuelle Person]]

## Bestandsvergleich

*Als Forscherin, die einen Teilbestand gegen den Gesamtbestand kontrastiert, will ich die gleiche Kategorie auf beide Bestände anwenden, damit ich Auffälligkeiten des Teilbestands erkenne.*

* **Komponente** [[ui-design#Bestandsfilter]]
* **Begriff** [[glossar#Quellenkorpus]]

## Zeitverlauf einer Kategorie

*Als Forscherin, die Entwicklungen über die Zeit untersucht, will ich eine Kategorie im Zeitraster sehen, damit ich Kontinuitäten und Brüche erkenne.*

* **Komponente** [[ui-design#Zeitfilter]], [[exploration]]

## Vom Aggregat in die Quelle

Zwei Pfade von einer aggregierten Anzeige zur Quellen-Liste, die dieselbe Mechanik tragen, aber unterschiedlich starten.

*Als Forscherin, die wissen will, welche Personen im Korpus die Bezeichnung „wittib" tragen, will ich diese Verteilungs-Kategorie direkt anklicken und in die Liste der belegenden Quellen springen, damit ich nicht in den Pipeline-CSVs nach dem passenden Schlüssel suchen muss.*

Pfad Klick: Auswertungen-Seite → Bezeichnungs-Suche → Klick auf die Tabellenzeile öffnet das [[ui-design#Drill-down-Overlay]] mit den Quellen, die diese Bezeichnung enthalten; jede Zeile linkt in die Quellen-Detailseite. Geschlechter-Filter wird in den Drill mitgenommen.

*Als Forscherin, die in der Auswertungstabelle sieht, dass Schuldbrief-Pfand-Geschäfte im Korpus selten sind, will ich sehen, in welchen Jahrzehnten sie sich häufen, damit ich beurteilen kann, ob es sich um eine echte zeitliche Konzentration oder einen Korpus-Artefakt handelt.*

Pfad Brush: Auswertungen → Transaktionstypen-Sektion → wechseln auf die Zeitstrom-Sub-Seite, Stack-Achse auf „Transaktionstyp" → Stapel zeigen die Verteilung über die Jahrzehnte → Klick auf die Schuldbrief-Pfand-Kategorie in der Legende fokussiert die anderen weg → Brush wählt den interessanten Zeitabschnitt → Drill-Liste zeigt nur die Quellen dieser Kategorie in dem Zeitraum.

* **Komponente** [[ui-design#Drill-down-Overlay]], [[exploration#Zeitstrom (vorhanden)]]

## Menschen-Events kontrolliert behandeln

*Als Forscherin, die exakte Statistiken zu Personen in einem Rechtsgeschäft aufstellt, will ich [[glossar#Menschen-Event|Menschen-Events]] aktiv ein- oder ausschließen, damit referenzierte Personen aus früheren Geschäften meine Zahlen nicht verzerren.*

Default-Stand schliesst mentioned Events aus. Der Vergleichsstand wird über `--stage 2` als separater Build erzeugt, nicht über einen UI-Toggle. Begründung: [[specification#Mentioned-Event-Vergleichsstand als Build-Flag]] und [[specification#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]].

* **Begriff** [[glossar#Menschen-Event]]

## Unbekannten Begriff an Ort und Stelle verstehen

*Als Forscherin, die einem projektspezifischen Begriff wie [[glossar#Menschen-Event]] zum ersten Mal begegnet, will ich seine Bedeutung im UI nachschlagen, ohne den Kontext zu verlassen, damit ich die Konsequenz einer Filteraktion verstehe.*

* **Komponente** [[ui-design#Glossar-Integration]]

---

# 4 Wissenschaftliche Absicherung

Stories, die das Forschen jenseits der inhaltlichen Frage absichern: Provenienz, Reproduzierbarkeit, Zitierbarkeit, Fehlerlokalisierung. Sie sind nicht UI-Features im engeren Sinn, sondern Erwartungen an die wissenschaftliche Verwendbarkeit der Anwendung.

## Provenienz einer Zahl prüfen und Fehlerverdacht lokalisieren

Zwei Lesarten desselben Mechanismus: einmal als Vertrauensaufbau für eine Zahl in der Publikation, einmal als Fehlersuche für eine unplausible Zahl.

*Als Forscherin, die eine Zahl in einer Publikation verwenden will, will ich an Ort und Stelle sehen, welcher Bestand und welche Operation der Zahl zugrunde liegen, damit ich sie gegenüber Reviewerinnen vertreten kann.*

*Als Forscherin, die eine unplausible Zahl sieht, will ich erkennen können, ob der Grund in den Quelldaten, in der Transformation oder in der Darstellung liegt, damit ich den Fehler präzise benennen kann.*

* **Komponente** [[ui-design#Tip-System]] mit Provenienz-Information; [verification/findings.md](../verification/findings.md) mit Befund-Register
* **Anforderung** [[specification#Datenrobustheit und Provenienz]], [[specification#Verifizierbarkeit und Verifikations-Test-Set]]
* **Fundament** [[architecture]]

## Forschungsstand zitieren und peer-reviewen

Zwei Use-Cases derselben Zitierbarkeit: einmal in der kollegialen Diskussion, einmal in der publizierten Arbeit.

*Als Forscherin, die eine Auswertung einer Kollegin prüft, will ich dieselbe Filterkombination aufrufen können wie sie, damit wir auf derselben Datensicht diskutieren.*

*Als Forscherin, die Zahlen in einer Veröffentlichung zitiert, will ich einen eingefrorenen Datenstand zum Stichtag der Einreichung referenzieren, damit meine Aussagen langfristig überprüfbar bleiben.*

* **Komponente** URL-Permalink auf den Daten-Visualisierungs-Seiten; Datenstand im Footer
* **Anforderung** [[specification#Forschungsstand zitierbar via URL-Parameter]], [[specification#Zitierfähiger Datenstand]]

---

## Siehe auch

* [[specification]] Anforderungs-Spezifikation, deren Einlösung die Stories beschreiben
* [[ui-design]] gestalterische Umsetzung der Komponenten
* [[analyse]], [[exploration]] die zwei großen UI-Bereiche
* [[glossar]] verwendete Fachbegriffe
* [[journal]] chronologische Notizen zu Umsetzung und Stand
