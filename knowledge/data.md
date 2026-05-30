---
title: Datenbasis
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.3
created: 2026-02-19
updated: 2026-05-23
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[TEI]]", "[[Prosopography]]", "[[Data Modelling]]"]
knowledge-sources:
  standards:
    TEI P5: https://tei-c.org/release/doc/tei-p5-doc/en/html/
related: [architecture, specification, glossar]
---

# Datenbasis

Was die Datenbank als Gegenstand dokumentiert und wie die Daten strukturiert sind. Fachbegriffe werden verwendet, nicht definiert. Definitionen in [[glossar]].

## Gegenstand

Die Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte in schriftlicher Überlieferung. Der Fokus liegt auf Urkunden und urkundlich verfassten Einträgen in Stadtbüchern, die rechtliche Transaktionen dokumentieren.

Der freigegebene Zeitraum ist in `RELEASED_PERIOD` (`frontend/config.py`) festgelegt; Zeitabschnitte außerhalb werden nicht angezeigt. Eine ausgewiesene Lücke innerhalb des Rahmens trägt das Label „noch nicht ausgewertet".

## Quellenkorpora

Die Daten sind in Quellenkorpora organisiert, die sich in Zeitraum, Provenienz und Erschließungsform unterscheiden.

Das QGW-Corpus bündelt die „Quellen zur Geschichte Wiens" in mehreren Bänden. Die Stadtbücher bilden eine eigenständige Quellengruppe mit abweichender Überlieferungsform. Weitere Korpora wie Gewerbücher und Grundbücher werden im Build-Prozess vorgehalten, sind aber nicht freigegeben.

Single Source of Truth für die freigegebenen Subkorpora ist `RELEASED_CORPORA` im Pipeline-Repo (`pipeline/config.py`). Es steuert sowohl die CSV-Erzeugung als auch die Sichtbarkeit im Frontend-Build. Nicht freigegebene Subkorpora bleiben für die editorische Arbeit in `sources/`, werden aber weder exportiert noch gerendert. Für interne Analysen existiert der Override `PIPELINE_INCLUDE_UNRELEASED=1`; im publizierten Build wird er nicht verwendet.

## Stufenmodell für Korpus-Auswahl

Über den freigegebenen Bestand hinaus definiert das Frontend vier benannte Stufen (siehe `frontend/stages.py` und [[specification#Stufenmodell für Korpus-Auswahl und Annotationsebenen]]):

- **Stufe 1 Publikation** bedient den freigegebenen Bestand und entspricht der Single Source of Truth in `RELEASED_CORPORA`.
- **Stufe 2 Vergleich** ist Stufe 1 plus mentioned events als volle Events.
- **Stufe 3 voller `_ready`-Bestand** zieht alle Subkorpora mit `_ready`-Suffix ein und ist heute deckungsgleich mit Stufe 1, weil alle `_ready`-Subkorpora freigegeben sind; beide divergieren erst, sobald ein `_ready`-Subkorpus die Freigabe nicht hat.
- **Stufe 4 Maximalversion** zieht alle Subkorpora mit TEI-Annotation ein, auch solche ohne `_ready`-Suffix; sie dient dem Schema-Stresstest, nicht der Publikation.

Stufen 3 und 4 sind heute strukturell vorhanden und baubar, datenseitig aber an die jeweilige Korpus-Erweiterung gebunden. Aussagen unter höheren Stufen sind methodisch breiter, aber editorisch weniger geprüft.

## Nicht oder nur teilweise ausgewertet

Innerhalb des freigegebenen Rahmens trägt die nicht ausgewertete Periode das Label „noch nicht ausgewertet" — die Überlieferung existiert, die redaktionelle Auswertung steht aus. Konkrete Grenzen siehe [[architecture#Datenstand aus dem Pipeline-Repo]] und `RELEASED_PERIOD`.

Personen und Organisationen sind als freigegebene Register-Dimensionen angelegt. Jede individuelle Entität mit mindestens einer Nennung in einer freigegebenen Quelle erhält eine Listen-Seite und eine eigene Detail-Profilseite mit Stammdaten, Beziehungen und Quellen-Tabelle.

## Erschließungsformen

Die Quellenkorpora unterscheiden sich in der Form ihrer Erschließung. Die Unterscheidung ist an der Oberfläche sichtbar zu machen, weil sie bestimmt, welche Art von Aussage eine Quelle stützt.

Monasterium-Quellen liegen als digitalisierte Faksimiles mit zugeordneten Regesten vor. Ein Regest ist eine redaktionelle Zusammenfassung; der zugrunde liegende Text ist nicht vollständig ediert, aber im Digitalisat einsehbar.

Die Stadtbücher sind als ausgeschriebener Volltext erschlossen. Textgenaue Belege sind hier möglich, weil die Datenbank die Wortlaute wiedergibt.

Grundbücher und verwandte Bestände befinden sich auf unterschiedlichen Stufen der Erschließung. Der Status wird pro Bestand ausgewiesen.

## Hierarchie der Daten

Die Daten sind in vier Ebenen organisiert. [[glossar#Quellenkorpus]] ist die oberste Gruppierung, darunter einzelne [[glossar#Quelle|Quellen]], darunter einzelne [[glossar#Event|Events]], darunter einzelne Nennungen.

Jede Ebene hat ihre eigene Zählung. Wer nach Urkunden zählt, bleibt auf Quellenebene. Wer nach Rechtsgeschäften zählt, steigt auf Event-Ebene ab. Wer nach Personen zählt, wählt zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]].

Auf der Nennungsebene gilt: Mehrfacherwähnungen einer Entität innerhalb einer Quelle werden bei der Aggregation zu einer Nennung zusammengefasst. Die Zählebene [[glossar#Gesamtnennung]] ist damit quellenbereinigt. Die Entscheidung und ihr Hintergrund stehen in [[specification#Quellenbereinigte Zählung]], die technische Umsetzung in [[architecture#Quellenbereinigte Aggregation als Invariante]].

In der publizierten Datenbasis ist die Hierarchie Quelle → Event in der Praxis fast überall flach: nahezu alle Quellen mit Events tragen genau ein Event, nur eine Handvoll trägt zwei oder drei. Eine Urkunde dokumentiert in der editorischen Realität meist ein einziges Rechtsgeschäft; Mehrfach-Event-Quellen sind die Ausnahme. UI-Aussagen, die Quellen- und Event-Counts nebeneinander stellen („X Rechtsgeschäfte in Y Quellen"), zeigen daher fast immer dieselbe oder eine sehr nahe beieinander liegende Zahl. Die Begriffshierarchie bleibt trotzdem ein eigener Wert, weil sie die Grundlage für Aussagen über Geltungsbereich („gemeinsam in derselben Quelle" gegen „im selben Rechtsgeschäft") und für die Mehrfach-Event-Ausnahmen ist.

## Register

Die Datenbank publiziert zwei Register: Personen und Organisationen. Jeder Eintrag ist eine konsolidierte Identität mit eindeutiger ID, verknüpft die Vorkommen in den Quellen und trägt eine eigene Detail-Profilseite. Beziehungen zwischen Entitäten (Verwandtschaft, Freundschaft, Vertretung, Beruf, Titelverweis) sind in beiden Profilen sichtbar, wo es semantisch trägt: Verwandtschaft, Freundschaft und Vertretung sind bidirektional aufgelöst (eine CSV-Zeile erscheint im Profil beider Seiten), Beruf und Titelverweis sind einseitig (das Gegenüber ist eine Organisation).

Die Register sind nicht redundant zu den Quellen, sondern deren Bezugspunkt. Ohne Register gäbe es nur Namensketten ohne Zuordnung zu individuellen Entitäten. Orts-Annotationen bleiben als Inline-Markup im Quellen-Volltext sichtbar, tragen aber kein Sprungziel und kein eigenes Register.

## Annotationsebenen

Die TEI-Auszeichnung arbeitet auf vier Ebenen.

Events bilden die oberste Auszeichnungsebene. Sie halten ein konkretes Rechtsgeschäft als strukturierte Einheit zusammen.

Funktionen und Rollen spezifizieren, in welcher Eigenschaft eine Person oder Organisation an einem Event beteiligt ist. Das kontrollierte Vokabular ist in [[glossar#Rolle]] festgelegt.

Entitäten referenzieren die Register-Einträge für Personen, Organisationen und Orte.

Attribute halten zusätzliche Merkmale fest, etwa Verwandtschaftsbeziehungen, Berufe oder topographische Zuordnungen.

Berufe sind im Quellen-Text in der Original-Schreibweise belegt und werden über `normalisation_lists/roleName_norm_matching.csv` normalisiert. Die Spalte `Gewerbe_nach_Uhlirz_GstW` ordnet jedem normalisierten Beruf eine Uhlirz-Kategorie zu (römische Ziffer plus Klartext, von „I Landwirtschaft" bis „XVIII Verwaltung"). Diese Klassifikation ist die Grundlage für berufsgruppen-orientierte Forschungsfragen ([[user-stories#Endogamie in einer Berufsgruppe]]). Verwandtschaftsbezeichnungen liegen in `kin_relations_in_sources.csv` als freier deutscher Begriff vor („Gemahlin", „Hausfrau", „Gatte"); ein typisierter Heirats-Tag existiert nicht, ein String-Match auf eine Heirats-Begriffsliste löst den Anwendungsfall.

### Drei Orte für die Berufs-Angabe

Eine Berufsbezeichnung kann in der Pipeline an drei verschiedenen Stellen auftauchen, und jede Stelle steht für eine andere Annotationspraxis:

- `occ_relations_in_sources.csv` hält Berufe, die im TEI durch ein explizites `<occupation>`-Element annotiert sind, samt Bezug zu Event und Person. Dies ist die strengste Form: die Annotation hat einen eigenen `<rs>`-Wrapper und ist als Berufs-Aussage typisiert.
- `persons_in_sources.csv::source_prof` hält die Berufsangabe, wie sie im Quellentext als Apposition zur Personenerwähnung erscheint („Hannsen, dem wachsgiesser"). Diese Form ist häufiger, weil sie näher an der Quellenformulierung bleibt, und ist nicht als eigenständige Beruf-Annotation modelliert.
- `persons.csv::addname_orig` hält Beinamen in der Personen-Stammdatei. Wenn ein Beruf identitätsbildend ist („Jakob Wachsgießer"), wandert er hierher und nicht zwangsläufig in die quellenbezogenen Spalten.

Diese Mehrfach-Lokalisierung ist editorische Realität, nicht Designfehler — sie spiegelt unterschiedlich tiefe Auszeichnungs-Entscheidungen je Person und Quelle. Schwerpunkt ist erkennbar: `occ_relations` trägt häufig institutionelle Funktion und Status (purger, clericus, official, Bürger), `source_prof` häufig das eigentliche Handwerk in der Quellenformulierung (wachsgiesser, ledrer, chramer, gürtler). Beide Pfade stehen unabhängig und in 326 Person-Quelle-Paaren parallel; nur in 11 davon trägt eine Spalte denselben String wie die andere.

Konsequenz für die Aggregat-Schicht: Jeder Aggregator, der Berufe oder Uhlirz-Kategorien verwendet, muss bewusst entscheiden, welchen der drei Orte er liest. Die zwei UI-getriebenen Konstellations-Aggregatoren (`role_constellation.py`) und die Verifikations-Säule (`verification/research_questions.py` und `frontend/aggregator/research_questions.py`) lesen beide `occ_relations` und `source_prof` und vereinigen sie deduliziert; die Personen- und Organisationsprofile listen die Einträge aus beiden Spalten separat unter Quellenvorkommen, damit die editorische Tiefe pro Person sichtbar bleibt. `addname_orig` aus der Stammdatei fließt heute in keinen der Beruf-Filter ein, sondern bleibt Bestandteil des Anzeigenamens.

## Organisationen im Konstellations-Index

Der Konstellations-Aggregator `role_constellation.py` führt pro Event zwei Listen: `p` (Personen-Teilnehmer aus `persons_in_events.csv`) und `og` (Org-Teilnehmer aus `orgs_in_events.csv`). Beide spiegeln sich in `event_role` (issuer, recipient, witness, other), seltene Sonderwerte aus `orgs_in_events` (`transactiongood_I/II`, 5 Zeilen) werden auf `other` normalisiert, damit der Resolver keine Sonderfälle braucht. Org-Stammdaten (`name_reg`, `type`) kommen aus `organisations.csv`; das dortige Feld `org_key` ist eine Doubletten-Referenz auf einen anderen Eintrag und wird nicht ausgewertet. Vokabular für das UI-Autocomplete: Top-50 Namen nach Häufigkeit (St. Stephan, Bürgerspital, St. Agnes etc.) und alle vorkommenden Typen alphabetisch.

Das Match-Verhalten ist parallel zu Personen: der Org-Name ist Substring-Match auf `name_reg` (case-insensitiv), der Typ ist exakter Match auf das kontrollierte Vokabular. Bei generischen Namensbestandteilen, die als Personenname und Heiligen-Patrozinium gleichermaßen vorkommen (Agnes, Maria, Margarethe), produziert der Namensfilter Beifang aus Stiftungs-Org-Namen wie „Jahrtagsstiftung der Agnes Melberin"; toponymische Beifügungen („Himmelpforte", „Stubentor") sind robuster und im UI-Beispiel daher bevorzugt. Doubletten in den Daten kommen vor: einzelne Orgs sind in `name_reg` zweifach mit Pipe verkettet eingetragen (`Dominikaner (Prediger) Wien | Dominikaner (Prediger) Wien`), das ist Datenpflege im Schwester-Repo, nicht Aggregator-Problem.

## Sonderfall Menschen-Events

Im Datenbestand vorkommend. Definition in [[glossar#Menschen-Event]]. Im UI werden Personen-Annotationen in verschachtelten Events nicht doppelt gezählt, siehe [[specification#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]].

## Aggregat-Schicht

Zwischen den Pipeline-CSVs und den Frontend-Views liegt eine konsolidierte Aggregat-Schicht, die pro Quelle ein vollständiges Record führt: Datum (ISO-normalisiert mit Range-Behandlung), Personen-Counts mit Geschlechter-Aufschlüsselung, Event-Counts mit Aufschlüsselung nach `<rs type="event">`-Subtyp (abstract, seal, entry, nota) und den Korpus-Pfad.

Die Aufschlüsselung nach Event-Subtyp macht die TEI-Heterogenität sichtbar: eine QGW-Quelle hat typischerweise einen Regest-Event und einen Siegel-Event, eine Stadtbücher-Quelle einen Entry-Event. Personen-Counts sind quellenbereinigt im Sinne von [[architecture#Quellenbereinigte Aggregation als Invariante]] — indirekte Erwähnungen über `kind_of_linking=corresp` teilen den `person_key` mit der genannten Person und werden nicht doppelt gezählt.

Neben den thematischen Aggregaten (Funktionsrollen × Geschlecht × Dekade in `roles`, Beziehungstypen und Bezeichnungen in `relations`, Transaktionstypen × Dekade in `transactions`) führt jede dieser JSON-Strukturen einen `drill_down`-Schnitt: pro Aggregat-Zelle eine Liste der beitragenden `file_key`-Verweise. Eine Quelle kann in mehreren Zellen erscheinen, der Schnitt führt sie pro Zelle nur einmal. Aufgelöst werden die `file_keys` über `data/docs_lookup.json`, das pro Schlüssel die Stammdaten Datum, Korpus-Label, Kurzregest und Quellen-URL hält. Damit ist jede aggregierte Zahl im Frontend bis zur einzelnen Quelldokument-Seite rückführbar — die Provenienz-Garantie aus [[specification#Datenrobustheit und Provenienz]] hängt an dieser doppelten Schicht (Aggregat + Lookup).

Eine zweite Aggregat-Familie bedient die Entitäts-Profile. Die Module `person_profiles` und `org_profiles` joinen Stammdaten (Name, Geschlecht, Todesdatum, Notiz, Wien-Wiki-Link bzw. Typ, Observanz, Hierarchie), Quellenvorkommen, Rollen-Aggregation pro Person und die fünf Beziehungs-CSVs (Verwandtschaft, Freundschaft, Vertretung, Beruf, Titelverweis) zu einem Profil pro Entität, das direkt server-seitig zu `register/persons/<id>.html` und `register/orgs/<id>.html` gerendert wird. Eine zusätzliche Forward-Index-JSON `docs_entities.json` ordnet jeder Quelle die Liste ihrer annotierten Personen- und Organisations-IDs zu; der Datenkorb nutzt diesen Index, um beim Sammeln einer Quelle die zugehörigen Entitäten automatisch als abgeleitete Einträge in den Korb zu legen.

Audience-bewusste Filterung. Aggregat-JSONs werden für die öffentliche Audience gefiltert, sodass technische Identifikatoren (`pe__`-, `org__`-, `ev__`-IDs als Schlüssel oder Inline-Felder) nicht in den öffentlichen Build leaken. Die interne Audience trägt sie unverändert für die editorische Verifikation. Die Filterung lebt im Aggregator selbst, nicht im Template, damit die Audience-Trennung auch bei direkter JSON-Konsumption durch externe Werkzeuge greift. Konvention in [[specification#Öffentliche versus interne Sicht in zwei Schichten]], Build-Mechanik in [[architecture#Audience-Schicht für öffentliche und interne Sicht]].

Technische Umsetzung in [[architecture#Datenschichten und Aggregator]].

## Siehe auch

- [[glossar]] Definitionen der verwendeten Begriffe
- [[architecture]] wie die Daten technisch verarbeitet werden
- [[specification]] welche User-Stories die Datenstruktur einlöst
