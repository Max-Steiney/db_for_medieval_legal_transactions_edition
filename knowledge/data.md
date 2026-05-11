---
title: Datenbasis
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-02-19
updated: 2026-05-09
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[TEI]]", "[[Prosopography]]", "[[Data Modelling]]"]
knowledge-sources:
  standards:
    TEI P5: https://tei-c.org/release/doc/tei-p5-doc/en/html/
related: [architecture, requirements, decisions, glossar]
---

# Datenbasis

Was die Datenbank als Gegenstand dokumentiert und wie die Daten strukturiert sind. Fachbegriffe werden verwendet, nicht definiert. Definitionen in [[glossar]].

## Gegenstand

Die Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte in schriftlicher Überlieferung. Der Fokus liegt auf Urkunden und urkundlich verfassten Einträgen in Stadtbüchern, die rechtliche Transaktionen dokumentieren.

Der freigegebene Zeitraum beginnt 1177 und endet 1412, mit einer Ausnahme bis 1414 für die Quellenkorpora QGW II/1 und QGW II/2. Außerhalb dieses Rahmens liegende Zeitabschnitte werden nicht angezeigt.

## Quellenkorpora

Die Daten sind in Quellenkorpora organisiert, die sich in Zeitraum, Provenienz und Erschließungsform unterscheiden.

Das QGW-Corpus bündelt die „Quellen zur Geschichte Wiens" in mehreren Bänden. Die Stadtbücher bilden eine eigenständige Quellengruppe mit abweichender Überlieferungsform. Weitere Korpora wie Gewerbücher und Grundbücher werden im Build-Prozess vorgehalten, sind aber zum aktuellen Zeitpunkt nicht freigegeben.

Aktuell freigegeben und im UI sichtbar sind zwei Subkorpora: `QGW/Vienna_1177-1414_ready` (Wiener Urkunden 1177–1414) und `Stadtbuecher/Band_1_1395-1400_ready` (Stadtbücher, Band 1, 1395–1400). Die Single Source of Truth ist das Tupel `RELEASED_CORPORA` im Pipeline-Repo (`pipeline/config.py`); es steuert sowohl die CSV-Erzeugung als auch die Sichtbarkeit im Frontend-Build. Subkorpora außerhalb dieses Tupels liegen für die editorische Arbeit in `sources/`, werden aber weder exportiert noch gerendert. Für interne Analysen existiert der Override `PIPELINE_INCLUDE_UNRELEASED=1`, der alle Subkorpora einbezieht; im publizierten Build wird er nicht verwendet.

Welche Korpora im UI tatsächlich sichtbar sind, entscheidet sich am Freigabestand, nicht an der technischen Verfügbarkeit.

## Nicht oder nur teilweise ausgewertet

Der Zeitraum 1418 bis 1447 ist im UI als „noch nicht ausgewertet" gekennzeichnet. Die Überlieferung existiert, die redaktionelle Auswertung steht aus.

Personen und Organisationen sind als freigegebene Register-Dimensionen angelegt. Jede Entität mit mindestens einer Nennung in einer freigegebenen Quelle erhält eine Listen- und eine Detail-Seite. Das Ortsregister bleibt vorerst zurückgehalten, weil die Stammdaten zu Orten noch nicht hinreichend konsolidiert sind; Orts-Annotationen im Quellen-Volltext bleiben als Markup sichtbar, tragen aber kein Sprungziel.

## Erschließungsformen

Die Quellenkorpora unterscheiden sich in der Form ihrer Erschließung. Die Unterscheidung ist an der Oberfläche sichtbar zu machen, weil sie bestimmt, welche Art von Aussage eine Quelle stützt.

Monasterium-Quellen liegen als digitalisierte Faksimiles mit zugeordneten Regesten vor. Ein Regest ist eine redaktionelle Zusammenfassung; der zugrunde liegende Text ist nicht vollständig ediert, aber im Digitalisat einsehbar.

Die Stadtbücher sind als ausgeschriebener Volltext erschlossen. Textgenaue Belege sind hier möglich, weil die Datenbank die Wortlaute wiedergibt.

Grundbücher und verwandte Bestände befinden sich auf unterschiedlichen Stufen der Erschließung. Der Status wird pro Bestand ausgewiesen.

## Hierarchie der Daten

Die Daten sind in vier Ebenen organisiert. [[glossar#Quellenkorpus]] ist die oberste Gruppierung, darunter einzelne [[glossar#Quelle|Quellen]], darunter einzelne [[glossar#Event|Events]], darunter einzelne Nennungen.

Jede Ebene hat ihre eigene Zählung. Wer nach Urkunden zählt, bleibt auf Quellenebene. Wer nach Rechtsgeschäften zählt, steigt auf Event-Ebene ab. Wer nach Personen zählt, wählt zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]].

Auf der Nennungsebene gilt: Mehrfacherwähnungen einer Entität innerhalb einer Quelle werden bei der Aggregation zu einer Nennung zusammengefasst. Die Zählebene [[glossar#Gesamtnennung]] ist damit quellenbereinigt. Die Entscheidung und ihr Hintergrund stehen in [[decisions#Quellenbereinigte Zählung]], die technische Umsetzung in [[architecture#Quellenbereinigte Aggregation als Invariante]].

## Register

Die Datenbank publiziert zwei Register: Personen und Organisationen. Jeder Eintrag ist eine konsolidierte Identität mit eindeutiger ID und verknüpft die Vorkommen in den Quellen.

Die Register sind nicht redundant zu den Quellen, sondern deren Bezugspunkt. Ohne Register gäbe es nur Namensketten ohne Zuordnung zu individuellen Entitäten. Orts-Daten werden weiterhin in den TEI-Quellen ausgezeichnet und in der Pipeline geführt, aber nicht als eigenes öffentliches Register ausgespielt.

## Annotationsebenen

Die TEI-Auszeichnung arbeitet auf vier Ebenen.

Events bilden die oberste Auszeichnungsebene. Sie halten ein konkretes Rechtsgeschäft als strukturierte Einheit zusammen.

Funktionen und Rollen spezifizieren, in welcher Eigenschaft eine Person oder Organisation an einem Event beteiligt ist. Das kontrollierte Vokabular ist in [[glossar#Rolle]] festgelegt.

Entitäten referenzieren die Register-Einträge für Personen, Organisationen und Orte.

Attribute halten zusätzliche Merkmale fest, etwa Verwandtschaftsbeziehungen, Berufe oder topographische Zuordnungen.

## Sonderfall Menschen-Events

Im Datenbestand vorkommend. Definition in [[glossar#Menschen-Event]], UI-Behandlung in [[requirements#Menschen-Events-Behandlung]].

## Aggregat-Schicht

Zwischen den Pipeline-CSVs und den Frontend-Views liegt eine konsolidierte Aggregat-Schicht, die pro Quelle ein vollständiges Record führt: Datum (ISO-normalisiert mit Range-Behandlung), Personen-Counts mit Geschlechter-Aufschlüsselung, Event-Counts mit Aufschlüsselung nach `<rs type="event">`-Subtyp (abstract, seal, entry, nota) und den Korpus-Pfad.

Die Aufschlüsselung nach Event-Subtyp macht die TEI-Heterogenität sichtbar: eine QGW-Quelle hat typischerweise einen Regest-Event und einen Siegel-Event, eine Stadtbücher-Quelle einen Entry-Event. Personen-Counts sind quellenbereinigt im Sinne von [[architecture#Quellenbereinigte Aggregation als Invariante]] — indirekte Erwähnungen über `kind_of_linking=corresp` teilen den `person_key` mit der genannten Person und werden nicht doppelt gezählt.

Neben den thematischen Aggregaten (Funktionsrollen × Geschlecht × Dekade in `roles`, Beziehungstypen und Bezeichnungen in `relations`, Transaktionstypen × Dekade in `transactions`) führt jede dieser JSON-Strukturen einen `drill_down`-Schnitt: pro Aggregat-Zelle eine Liste der beitragenden `file_key`-Verweise. Eine Quelle kann in mehreren Zellen erscheinen, der Schnitt führt sie pro Zelle nur einmal. Aufgelöst werden die `file_keys` über `data/docs_lookup.json`, das pro Schlüssel die Stammdaten Datum, Korpus-Label, Kurzregest und Quellen-URL hält. Damit ist jede aggregierte Zahl im Frontend bis zur einzelnen Quelldokument-Seite rückführbar — die Provenienz-Garantie aus [[requirements#Datenrobustheit und Provenienz]] hängt an dieser doppelten Schicht (Aggregat + Lookup).

Technische Umsetzung in [[architecture#Datenschichten und Aggregator]].

## Siehe auch

- [[glossar]] Definitionen der verwendeten Begriffe
- [[architecture]] wie die Daten technisch verarbeitet werden
- [[requirements]] welche Anforderungen sich aus der Datenstruktur ableiten
