# Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Rechtsgeschäften

Digitale Edition zu mittelalterlichen Wiener Rechtsgeschäften, freigegebener Zeitraum 1177–1412 (QGW II/1 und II/2 bis 1414).

Dieses Repository ist die **Publikations-Schicht** der Edition: Build-Code, Templates, statische Assets, gerenderte Seite. Die GitHub-Pages-Bereitstellung läuft aus diesem Repo.

## Zwei-Repository-Setup

- **Frontend-Repo (dieses Repo):** `frontend/` (Build-Code, Jinja2-Templates, Content-Markdown, statische Assets, Tests), `docs/` (Build-Output für GitHub Pages), `knowledge/` (konzeptionelle Frontend-Wissensbasis), `verification/` (unabhängiges Verifikations-Test-Set).
- **Pipeline-Repo:** `../db_for_medieval_legal_transactions` — TEI-Quellen, Register, Normalisierungslisten, RelaxNG-Schema, Python-Pipeline (CSV-Generator), redaktionelle Annotationsrichtlinien.

Beide Repos müssen nebeneinander geklont sein. `frontend/__init__.py` legt das Pipeline-Repo automatisch auf `sys.path`, damit `from pipeline.config import …` ohne Install-Step funktioniert.

```
parent/
  db_for_medieval_legal_transactions/         ← Datengrundlage
    sources/        TEI-XML
    indices/        Register (Personen, Organisationen, Orte)
    pipeline/       Python/lxml-Pipeline → pipeline/output/*.csv
  db_for_medieval_legal_transactions_edition/ ← dieses Repo
    frontend/
      templates/    Jinja2
      content/      Markdown (About, Impressum, Editionsrichtlinien)
      static/       CSS, JS, Fonts
      config.py     redaktionelle Festlegungen
      build.py      Build-Orchestrierung
    docs/           Build-Output (von GitHub Pages serviert)
```

## Build

```
# Voraussetzung: Pipeline-Repo nebenan, CSVs aktuell
cd ../db_for_medieval_legal_transactions
python -m pipeline transform           # CSVs neu erzeugen (wenn TEI-Quellen sich geändert haben)

cd ../db_for_medieval_legal_transactions_edition
python -m frontend build               # Site neu rendern → docs/
python -m frontend build --single FILE # einzelne Quelle
python -m pytest frontend/tests/       # Frontend-Tests
```

## Technischer Stack

- **Quellen:** TEI-XML (Urkunden, Regesten, Register) — im Pipeline-Repo.
- **Build:** Python mit `lxml` für TEI-Parsing und `Jinja2` für HTML-Rendering.
- **Daten:** aggregierte JSON-Dateien für clientseitiges Suchen, Filtern und Visualisieren.
- **Frontend:** statische HTMLs, Vanilla-JS-Module, eigenes CSS. Kein Framework, keine Serverlogik.
- **Hosting:** GitHub Pages aus `docs/`.

## Struktur

```
frontend/                 Build-Code, Templates, Content, Assets, Tests
docs/                     Build-Output (GitHub-Pages-Source)
  /                       Einstiegsseiten: index, documents, impressum
  /documents/             Regesten (aus TEI gerenderte Einzelseiten)
  /tei/                   TEI-XML-Downloads der freigegebenen Quellen
  /register/              Personen-, Organisations-, Ortsregister (HTML + JSON)
  /exploration/           visuell-explorative Zugänge
  /analysis/              klassischer Abfragemodus (in Vorbereitung)
  /project/               About, Statistik, Qualität, Editionsrichtlinien, Glossar
  /data/                  JSON-Indexe (Suche, Timeline, Register, Qualität)
  /static/                CSS, JS, Fonts
knowledge/                konzeptionelle Wissensbasis (Obsidian-Markdown)
verification/             unabhängiges Verifikations-Test-Set (Python, lxml)
vault/                    Legacy-Promptotyping-Dokumentation
```

## Begriffshierarchie

- **Quellenkorpus** — oberste Gruppe, etwa `QGW` oder `Stadtbücher`.
- **Quelle** — einzelne Urkunde oder Regest.
- **Event / Rechtsgeschäft** — in einer Quelle verzeichnete Transaktion.
- **Gesamtnennung** — Person×Quelle-Beziehung, quellenbereinigt gezählt: Mehrfacherwähnungen derselben Person in derselben Quelle zählen einmal.
- **Individuelle Person / Organisation / Ort** — konsolidierter Registereintrag.

Definitionen und Abgrenzungen: [knowledge/glossar.md](knowledge/glossar.md).

## Freigabestatus

- Freigegebener Zeitraum: **1177–1412**, Erweiterung **bis 1414 für QGW II/1 und II/2**.
- Bestand **1418–1447** ist noch nicht ausgewertet.
- Organisations- und Ortsregister sind vorbereitet, inhaltlich aber noch nicht freigegeben.

Redaktionelle Festlegungen: `frontend/config.py` (Zeitraum, Anzeige) und `../db_for_medieval_legal_transactions/pipeline/config.py::RELEASED_CORPORA` (Korpora-Set).

## Lokales Preview

```
python -m http.server 8765 --directory docs/
```

Aufruf unter `http://localhost:8765/`.

## Lizenz

Noch zu klären.
