# Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Rechtsgeschäften

Digitale Edition zu mittelalterlichen Wiener Rechtsgeschäften, freigegebener Zeitraum 1177–1412 (QGW II/1 und II/2 bis 1414).

Dieses Repository enthält den **Build-Output** der Edition und wird über GitHub Pages als statische Website ausgeliefert. HTML-, JSON- und Asset-Dateien werden nicht direkt hier bearbeitet, sondern aus dem Pipeline-Repository gerendert und synchronisiert.

## Zwei-Repository-Setup

- **Edition-Repository (dieses Repo):** reiner Build-Output für GitHub Pages.
- **Pipeline-Repository:** `../db_for_medieval_legal_transactions` — enthält TEI-Quellen, Registerdaten, Jinja2-Templates, Build-Code, statische Assets und redaktionelle Konfiguration.

Arbeitsfluss:

```
Pipeline-Repo
  sources/        TEI-XML
  indices/        Register (Personen, Organisationen, Orte)
  edition/
    templates/    Jinja2
    content/      Markdown (About, Impressum, Editionsrichtlinien)
    static/       CSS, JS, Fonts
    config.py     redaktionelle Festlegungen
    build.py      Build-Orchestrierung

python -m edition build
  -> schreibt nach docs/

cp -r docs/* -> Edition-Repo
  -> GitHub Pages liefert statisch aus
```

## Technischer Stack

- **Quellen:** TEI-XML (Urkunden, Regesten, Register).
- **Build:** Python mit `lxml` für TEI-Parsing und `Jinja2` für HTML-Rendering.
- **Daten:** aggregierte JSON-Dateien für clientseitiges Suchen, Filtern und Visualisieren.
- **Frontend:** statische HTMLs, Vanilla-JS-Module, eigenes CSS. Kein Framework, keine Serverlogik.
- **Hosting:** GitHub Pages.

## Struktur

```
/                         Einstiegsseiten: index, documents, impressum
/documents/<corpus>/...   Regesten (aus TEI gerenderte Einzelseiten)
/tei/<corpus>/...         TEI-XML-Downloads der freigegebenen Quellen
/register/                Personen-, Organisations-, Ortsregister (HTML + JSON)
/exploration/             visuell-explorative Zugänge: Rollen, Beziehungen, Transaktionen, Orte
/analysis/                klassischer Abfragemodus (in Vorbereitung)
/project/                 About, Statistik, Qualität, Editionsrichtlinien, Glossar
/data/                    JSON-Indexe (Suche, Timeline, Register, Qualität)
/static/                  CSS, JS, Fonts
/knowledge/               konzeptionelle Wissensbasis (Obsidian-Markdown, direkt hier gepflegt)
```

## Begriffshierarchie

- **Quellenkorpus** — oberste Gruppe, etwa `QGW` oder `Stadtbücher`.
- **Quelle** — einzelne Urkunde oder Regest.
- **Event / Rechtsgeschäft** — in einer Quelle verzeichnete Transaktion.
- **Gesamtnennung** — Person×Quelle-Beziehung, quellenbereinigt gezählt: Mehrfacherwähnungen derselben Person in derselben Quelle zählen einmal.
- **Individuelle Person / Organisation / Ort** — konsolidierter Registereintrag.

Definitionen und Abgrenzungen: [knowledge/glossar.md](knowledge/glossar.md).

## Ausnahmen vom Build-Output

Zwei Ordner werden direkt in diesem Repository gepflegt und nicht aus dem Pipeline-Repo erzeugt:

- **`knowledge/`** — konzeptionelle Frontend-Wissensbasis. Obsidian-kompatible Markdowns mit Wiki-Links. Zeitlos formuliert, ohne Meeting-Bezüge, Personennamen oder Quantitäten des Korpus. Enthält Daten-, Anforderungs-, Architektur- und Design-Dokumentation, ein Glossar sowie ein Arbeitstagebuch.
- **`vault/`** — Legacy-Dokumentation aus dem Pipeline-Repo (Promptotyping).

Meta-Dateien (`CLAUDE.md`, `README.md`, `.gitignore`) werden ebenfalls hier gepflegt.

## Freigabestatus

- Freigegebener Zeitraum: **1177–1412**, Erweiterung **bis 1414 für QGW II/1 und II/2**.
- Bestand **1418–1447** ist noch nicht ausgewertet.
- Organisations- und Ortsregister sind vorbereitet, inhaltlich aber noch nicht freigegeben.

Die redaktionellen Festlegungen liegen zentral in `edition/config.py` (Pipeline-Repo).

## Lokales Preview

```
python -m http.server 8765
```

im Repository-Root. Aufruf unter `http://localhost:8765/`.

## Lizenz

Noch zu klären.
