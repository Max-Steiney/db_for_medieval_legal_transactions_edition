# CLAUDE.md — Frontend Repo

## Was ist das hier?

Dieses Repo ist die **Publikations-Schicht** der digitalen Edition „Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Wiener Rechtsgeschäften". Hier liegen Build-Code, Templates, statische Assets und das gerenderte HTML, das GitHub Pages ausliefert.

Die **Datengrundlage** (TEI-Quellen, Register, Normalisierungslisten, CSV-Pipeline) liegt im Schwester-Repo `../db_for_medieval_legal_transactions`. Beide Repos müssen nebeneinander geklont sein. `frontend/__init__.py` legt das Pipeline-Repo automatisch auf `sys.path`, damit `from pipeline.config import …` ohne Install-Step funktioniert.

Konzeptionelle Substanz, Gestaltungsprinzipien und Leitentscheidungen leben in `knowledge/`. Wer das Projekt versteht, fängt dort an.

## Struktur

```
frontend/                 Build-Code (Python/Jinja2), Templates, Content (Markdown), Assets, Tests
docs/                     Build-Output, von GitHub Pages serviert
  /                       Portal-Einstiegsseiten (index, documents, impressum)
  /documents/             Regesten als HTMLs, aus TEI gerendert
  /tei/                   TEI-XML-Downloads der freigegebenen Quellen
  /data/                  JSON-Indexe (search, register, epics, timeline, quality, docs_aggregate)
  /register/              Personenregister (HTML + JSON; Org/Ort vorbereitet, nicht freigegeben)
  /exploration/           visuell-explorative Zugänge (Rollen, Beziehungen, Transaktionen, Orte)
  /analysis/              klassischer Abfragemodus
  /project/               About, Statistik, Qualität, Editionsrichtlinien, Glossar
  /static/                CSS, JS, Fonts
knowledge/                konzeptionelle Wissensbasis (Obsidian-Markdown, Wiki-Links)
verification/             unabhängiges Verifikations-Test-Set (Python, lxml)

../db_for_medieval_legal_transactions/   Schwester-Repo (Datengrundlage)
  sources/                TEI-Quellen
  indices/                Register
  pipeline/               CSV-Generator
  pipeline/output/        Pipeline-CSVs (vom Frontend gelesen)
```

## Arbeitsregel

**Frontend-Änderungen** (Templates, Build-Code, Content, Assets) gehören hierher:

```
python -m frontend build                # baut docs/ aus aktuellem Pipeline-Output
python -m frontend build --single FILE  # einzelne Quelle
python -m pytest frontend/tests/        # Frontend-Tests (kompakt: -q --tb=no --no-header)
```

**TEI-Quellen, Register, Pipeline-Code** gehören ins Schwester-Repo. Nach Änderungen dort:

```
cd ../db_for_medieval_legal_transactions
python -m pipeline transform     # CSVs neu erzeugen
cd -
python -m frontend build         # gegen frische CSVs neu bauen
```

`docs/` ist Build-Output. Nicht direkt editieren — durch Rebuild erzeugen. Ausnahme: Meta-Dateien wie `CLAUDE.md`, `README.md`, `knowledge/`.

## Begriffe und Leitentscheidungen

Begriffsdefinitionen leben in [`knowledge/glossar.md`](knowledge/glossar.md) (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Regest, Faksimile, Volltext, Erschließungsform).

Leitentscheidungen (Begründung pro Entscheidung) leben in [`knowledge/decisions.md`](knowledge/decisions.md). Kanonische Begriffshierarchie: Quellenkorpus → Quelle → Event → Gesamtnennung. Kontrolliertes Rollenvokabular: `issuer`, `recipient`, `sealer or witness`, `other`, `none`.

Freigabestand: 1177–1412 (mit Erweiterung bis 1414 für QGW II/1 und II/2), Lücke 1418–1447 als „noch nicht ausgewertet". Single-Source-of-Truth: `frontend/config.RELEASED_PERIOD` (Zeitraum) und `pipeline/config.RELEASED_CORPORA` im Schwester-Repo (Korpora-Set). Hardcoded Zahlen in Templates gelten als Fehler.

Datenstand (Footer) ist das Datum des letzten Pipeline-Repo-Commits, nicht das Build-Datum. Ermittelt in `frontend/build._pipeline_repo_data_date()`.

Gestaltungsprinzip: maximaler Informations-Output. Nachvollziehbarkeit vor reduzierter Ästhetik. Details in [`knowledge/ui-design.md`](knowledge/ui-design.md).

## Agent-Regeln

- **Sprache:** Deutsch bei inhaltlichen Änderungen; Englisch im Pipeline-Code.
- **Keine Pushes:** lokale Commits; Pushen nur auf expliziten Auftrag.
- **Keine Emojis** in irgendeiner Ausgabe.
- **Minimale Lösungen:** pragmatisch vor ausgebaut. Copy-Paste-Snippets statt neuer UI-Seiten, wenn möglich.
- **Keine Annahmen:** Wenn Kontext fehlt, recherchieren oder rückfragen — nicht raten.
- **Vor Änderungen:** prüfen, ob Frontend (hier) oder Datengrundlage (Schwester-Repo) betroffen ist. `docs/` nicht direkt editieren.

## Vor-Start-Checkliste

| Aufgabe | Lies zuerst |
|---|---|
| Titel/Nav/Footer ändern | `frontend/templates/base.html` |
| Startseite-Inhalt ändern | `frontend/templates/startseite.html` |
| Quellen-Übersicht (Filter, Chips, Tabelle) | `frontend/templates/index.html`, `frontend/static/js/index.js` |
| Provenienz- oder Glossar-Tooltip einsetzen | `frontend/templates/macros.html` (`prov_stat`, `prov_popover`, `prov_ratio_stat`, `glossary_tip`) |
| Pro-Quelle-Daten (Personen/Events/Datum) | `frontend/aggregator.py::aggregate_docs` schreibt `docs/data/docs_aggregate.json` |
| Erschließungsform | aus `events_in_sources.csv:event_in` aggregiert (abstract / seal / entry / nota); keine Heuristik im Frontend |
| Editionsrichtlinien | `../db_for_medieval_legal_transactions/edition_guidelines.md` |
| About / Impressum / Glossar | `frontend/content/` |
| TEI-Quellen | `../db_for_medieval_legal_transactions/sources/` |
| Register | `../db_for_medieval_legal_transactions/indices/` |
| Pipeline / CSV-Format | `../db_for_medieval_legal_transactions/knowledge/architecture.md` |
| Verifikations-Test-Set | `verification/`, siehe [`knowledge/architecture.md`](knowledge/architecture.md) |
| Konzeptionelle Wissensbasis | [`knowledge/`](knowledge/) — Einstieg über `knowledge/index.md` |
