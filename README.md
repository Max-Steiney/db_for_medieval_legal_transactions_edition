# Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Rechtsgeschäften

Digitale Edition zu mittelalterlichen Wiener Rechtsgeschäften, freigegebener Zeitraum 1177–1412 (mit Erweiterung bis 1414 für QGW II/1 und II/2). Zeitraum 1418–1447 ist noch nicht ausgewertet.

Dieses Repository ist die **Publikations-Schicht** der Edition: Build-Code, Templates, statische Assets, gerenderte Seite. Die Auslieferung läuft über GitHub Pages aus `docs/`.

## Zwei-Repository-Setup

Die Edition lebt in zwei Repositories, die nebeneinander geklont werden müssen.

- **Frontend-Repo (dieses Repo)** trägt Build-Code, Jinja2-Templates, Content, Assets, Tests und das gerenderte HTML.
- **Pipeline-Repo `../db_for_medieval_legal_transactions`** trägt TEI-Quellen, Register, Normalisierungslisten, das RelaxNG-Schema, die Python-Pipeline (CSV-Generator) und die redaktionellen Annotationsrichtlinien.

`frontend/__init__.py` legt das Pipeline-Repo automatisch auf `sys.path`, damit `from pipeline.config import …` ohne Install-Step funktioniert.

```
parent/
  db_for_medieval_legal_transactions/         ← Datengrundlage
    sources/        TEI-XML
    indices/        Register (Personen, Organisationen, Orte)
    pipeline/       Python/lxml-Pipeline → pipeline/output/*.csv
  db_for_medieval_legal_transactions_edition/ ← dieses Repo
    frontend/       Build-Code, Templates, Content, Assets, Tests
    docs/           Build-Output (von GitHub Pages serviert)
    knowledge/      konzeptionelle Wissensbasis
    verification/   unabhängiges Verifikations-Test-Set
```

## Build

```
# Voraussetzung: Pipeline-Repo nebenan, CSVs aktuell
cd ../db_for_medieval_legal_transactions
python -m pipeline transform           # CSVs neu erzeugen, falls TEI-Quellen sich geändert haben

cd ../db_for_medieval_legal_transactions_edition
python -m frontend build               # Site neu rendern → docs/
python -m frontend build --single FILE # einzelne Quelle
python -m pytest frontend/tests/       # Frontend-Tests
```

## Technischer Stack

- **Quellen:** TEI-XML (im Pipeline-Repo).
- **Build:** Python mit `lxml` für TEI-Parsing und `Jinja2` für HTML-Rendering.
- **Daten-Aussschicht:** aggregierte JSON-Dateien für clientseitiges Suchen, Filtern und Visualisieren.
- **Frontend:** statische HTMLs, Vanilla-JS-Module, eigenes CSS. Kein Framework, keine Serverlogik.
- **Hosting:** GitHub Pages aus `docs/`.

## UI-Bereiche

Die Edition gliedert sich in vier Top-Level-Bereiche:

- **Quellen** (`/documents.html`) — Listenansicht aller freigegebenen Quellen mit Filter, Suche, sortierbarer Tabelle, Volltext-/Regest-Detail.
- **Register → Personen** (`/register/persons.html` + `/register/persons/<id>.html`) — Personenregister mit Suche, Filter, Profilseite pro individueller Person mit Beziehungen und Quellen-Vorkommen. Organisations- und Ortsregister sind angelegt, aber nicht freigegeben.
- **Analyse** — quantitative Zugänge, zwei Sub-Seiten:
  - `/analysis/auswertungen.html` — vorberechnete Verteilungen (Donut für Funktionsrollen + Beziehungstypen, Bar-Chart für Transaktionstypen, Tabelle mit Mini-Bars für Bezeichnungen). Drill-down ins Quellen-Detail per Klick auf jede Aggregat-Zelle. Filter-Stand in der URL.
  - `/analysis/index.html` — Abfragen-Modus mit vorgefertigten Template-Familien.
- **Exploration** — visuell-interaktive Erkundung der Datenstruktur:
  - `/exploration/zeitstrom.html` — gestapelter Bar-Chart der Quellendichte pro Jahrzehnt; Stack-Achse umschaltbar (Quellenkorpus / Erschließungsform / Geschlecht / Transaktionstyp); Brush-zu-Drill-down; Stack-Kategorie isolierbar. Filter-Stand in der URL.
  - `/exploration/personennetzwerk.html` — Ego-Layout um eine Person; Klick auf Nachbar verlagert Zentrum; Beziehungstyp-Filter (Verwandtschaft / Beruf-Stand / Vertretung / Freundschaft); Personen-Suche.
  - Sankey-Diagramm zu Transaktionsflüssen — geplant.

Quer durch alle Quellen-Listen liegt der **Wissenskorb** (`/korb.html`): clientseitige Sammelmappe in `localStorage`, mit „+"-Knopf neben jedem Quellen-Eintrag, Live-Badge im Nav, CSV-Export auf der Korb-Seite.

## Konzeptionelle Dokumentation

Begriffe, Datenstruktur, Architektur, Anforderungen und Gestaltungsprinzipien leben in [`knowledge/`](knowledge/) als zusammenhängende Dokumentation in deutscher Sprache, mit Wiki-Links zwischen den Dokumenten. Einstieg über [`knowledge/index.md`](knowledge/index.md).

Begriffsdefinitionen (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Regest, Faksimile, Volltext, Erschließungsform): [`knowledge/glossar.md`](knowledge/glossar.md). Leitentscheidungen: [`knowledge/decisions.md`](knowledge/decisions.md). Chronologisches Arbeitstagebuch: [`knowledge/journal.md`](knowledge/journal.md).

## Lokales Preview

```
python -m http.server 8765 --directory docs/
```

Aufruf unter `http://localhost:8765/`.

## Lizenz

Noch zu klären.
