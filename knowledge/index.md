---
title: Wissensbasis
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
related: [glossar, data, architecture, requirements, decisions, ui-design, analyse, exploration, scholar-user-stories, journal]
---

# Wissensbasis

Konzeptionelle Dokumentation der Edition „Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Wiener Rechtsgeschäften". Zeitlos formuliert, in deutscher Sprache, mit Wiki-Links zwischen den Dokumenten. Build-Anleitungen, Quellcode-Details und Projektmanagement-Stand gehören nicht hierher — sie leben im Code, in `CLAUDE.md` und in [[journal]].

Wer das Projekt zum ersten Mal liest, folgt der unten skizzierten Reihenfolge. Wer ein konkretes Konzept sucht, geht direkt in das passende Dokument.

## Lesepfad

[[glossar]] zuerst — die Begriffe der Edition (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Erschließungsform, Regest, Faksimile, Volltext) sind Voraussetzung für alles Weitere. Definitionen sind hier kanonisch; andere Dokumente verlinken sie.

[[data]] beschreibt, was die Edition als Gegenstand dokumentiert: Quellenkorpora, Erschließungsformen (Regest plus Faksimile, Volltext), die vier Datenebenen (Korpus, Quelle, Event, Nennung), die Annotationsebenen, die Aggregat-Schicht zwischen Pipeline und Frontend.

[[architecture]] erklärt, wie der Datenfluss technisch verläuft: TEI-Quellen, Python-Pipeline, Aggregator, Jinja2-Templates, statische HTML-Ausgabe, das unabhängige Verifikations-Test-Set, die Provenienz-Indizes und die Quellenbereinigung als Invariante.

[[requirements]] formuliert funktionale und nicht-funktionale Anforderungen an das UI: Datenrobustheit und Provenienz, Umschaltbarkeit der Zählebenen, universelle Bestandsfilterung, Menschen-Events-Behandlung, zitierfähige Datenstände, Informationsdichte vor reduzierter Ästhetik.

[[decisions]] hält die Leitentscheidungen mit Begründung fest. Hier steht, warum „Quellenkorpus" statt „Sammlung", warum „Gesamtnennung" und nicht „Nennung", warum die quellenbereinigte Zählung, warum KPIs direkt aus TEI gerechnet werden, warum Edition- und Pipeline-Repo getrennt liegen.

[[ui-design]] übersetzt die Anforderungen in Gestaltungsprinzipien, Navigationsstruktur und Kernkomponenten: Provenienz-Tip, Glossar-Tip, Zählebenen-Umschalter, Bestandsfilter, Menschen-Events-Toggle, Drill-down-Overlay, Text-Bild-Synopse, Register-Listenseiten, Druckausgabe, Farb- und Typografielogik.

[[analyse]] und [[exploration]] vertiefen die beiden methodischen Zugänge der Edition. Analyse versammelt unter `/analysis/` die Auswertungen-Sub-Seite (Donut, Bar-Chart, Verteilungstabellen mit Drill-down ins Quellen-Detail) und die Abfragen-Sub-Seite (Template-Familien). Exploration trägt unter `/exploration/` den Zeitstrom (gestapelter Bar-Chart mit Brush-zu-Drill-down) und das Personennetzwerk (Ego-Layout um eine Person, Klick-Hopping durchs Beziehungsnetz); ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert. Beide Bereiche lesen dieselben Aggregate, aber unter unterschiedlichem Interaktionsmuster. Die Trennung folgt [[decisions#Exploration und Analyse als getrennte Bereiche]].

Quer durch alle Listen und Drill-downs liegt der Wissenskorb (siehe [[ui-design#Wissenskorb]]) als sammelnde Schicht: jede Quelle bekommt einen „+"-Knopf, das Nav führt ein Korb-Icon mit Live-Badge, eine eigene Korb-Seite (`/korb.html`) erlaubt Remove, Clear und CSV-Export. Persistenz lebt clientseitig in `localStorage`.

[[scholar-user-stories]] nimmt die Forscherinnen-Perspektive ein und beschreibt typische Nutzungsszenarien — vom Bestandsvergleich über die Provenienzprüfung bis zur publikationsreifen Zitation. Jede Story leitet eine Anforderung und eine Komponente ab.

[[journal]] ist das einzige chronologische Dokument der Wissensbasis. Hier landen Entscheidungspfade, verworfene Alternativen und offene Fragen mit Datum. Die übrigen Dokumente bleiben zeitlos.

## Beziehungen zu anderen Dokumentationsorten

`CLAUDE.md` im Repo-Root trägt Agent-Regeln, Build-Kommandos und die Vor-Start-Checkliste — alles, was operativ für die Mitarbeit am Code wichtig ist. `README.md` führt den Repo-Setup für externe Leserinnen und verlinkt in diese Wissensbasis. Die redaktionellen Annotationsrichtlinien zur TEI-Auszeichnung leben im Schwester-Repo unter `edition_guidelines.md`.
