---
title: Wissensbasis
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.2
created: 2026-02-19
updated: 2026-05-16
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
related: [glossar, data, architecture, specification, ui-design, analyse, exploration, user-stories, test-strategy, journal]
---

# Wissensbasis

Konzeptionelle Dokumentation der Datenbank „Stadt und Gemeinschaft Wien, Datenbank zu mittelalterlichen Wiener Rechtsgeschäften". Zeitlos formuliert, in deutscher Sprache, mit Wiki-Links zwischen den Dokumenten. Build-Anleitungen und Code-Details leben in `CLAUDE.md` und `README.md`, chronologische Notizen im [[journal]].

## Lesepfad

Die kanonischen Definitionen der Fachbegriffe (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Erschließungsform) liegen außerhalb dieses Ordners im Frontend-Content unter `frontend/content/project/glossar.md` und werden zur Glossar-Seite gerendert.

- [[data]] — Gegenstand der Datenbank: Quellenkorpora, Erschließungsformen, Datenebenen, Annotationsebenen, Aggregat-Schicht.
- [[architecture]] — Datenfluss von TEI bis statisches HTML, Aggregator, Verifikations-Test-Set, Provenienz-Indizes.
- [[specification]] — Anforderungs-Spezifikation der Anwendung: Korpus und Freigabe, Begriffe und Zählebenen, UI-Bereiche und User-Stories, Querschnitts-Anforderungen, Build und Wissensbasis. Bündelt auch die Leitentscheidungen mit Begründung und Konsequenz.
- [[ui-design]] — Gestaltungsprinzipien, Navigation, Kernkomponenten, Farben, Druck.
- [[analyse]] — quantitativer Zweig unter `/analysis/`: Auswertungen und Abfragen.
- [[exploration]] — visuell-interaktiver Zweig unter `/exploration/`: Zeitstrom und Personennetzwerk.
- [[user-stories]] — Forschungsszenarien aus Historiker*innen-Perspektive: Anwendungs-Stories, konkrete Forschungsfragen aus der editorischen Praxis, granulare Operationen, wissenschaftliche Absicherung.
- [[test-strategy]] — vier Säulen der Qualitätssicherung (Pytest, Verifikation, JS-Tests, Sichtprüfung), Pattern „Code plus Test im selben Commit", Datenfeld-Coverage als nächster Ausbauschritt.
- [[journal]] — einziges chronologisches Dokument der Wissensbasis.

## Beziehungen zu anderen Dokumentationsorten

`CLAUDE.md` im Repo-Root trägt Agent-Regeln, Build-Kommandos und die Vor-Start-Checkliste. `README.md` führt den Repo-Setup für externe Leserinnen. Die redaktionellen Annotationsrichtlinien zur TEI-Auszeichnung leben im Schwester-Repo unter `edition_guidelines.md`. `status.md` in diesem Ordner ist der lebende Projekt-Tracker (Anforderungs-Stand und Meeting-Notizen) und bewusst nicht zeitlos wie die übrigen Dokumente hier.
