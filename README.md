# Stadt und Gemeinschaft Wien — Datenbank zu mittelalterlichen Rechtsgeschäften

Datenbank zu mittelalterlichen Wiener Rechtsgeschäften, freigegebener Zeitraum 1177–1412 (mit Erweiterung bis 1414 für QGW II/1 und II/2). Zeitraum 1418–1447 ist noch nicht ausgewertet.

Dieses Repository ist die **Publikations-Schicht** der Datenbank: Build-Code, Templates, statische Assets, gerenderte Seite. Die Auslieferung läuft über GitHub Pages aus `docs/`.

## Korpora: freigegeben versus öffentlich

Zwei bewusst getrennte Ebenen.

**Freigegeben** sind die Subkorpora, die die Pipeline als CSV exportiert, das Tupel `RELEASED_CORPORA` in `../db_for_medieval_legal_transactions/pipeline/config.py`. Sie stehen dem Build zur Verfügung. Die mit (öffentlich) markierten sind zusätzlich für die Veröffentlichung freigegeben:

- `QGW/Vienna_1177-1414_ready` — Wiener Urkunden 1177–1414. **(öffentlich)**
- `QGW/Vienna_1415-1417` — Anschluss-Subkorpus 1415–1417.
- `QGW/Vienna_1448-57_ready` — Auswahl 1448–1457 mit konsequenter Orts- und Mentioned-Annotation.
- `Stadtbuecher/Band_1_1395-1400_ready` — Stadtbücher, Band 1, 1395–1400. **(öffentlich)**
- `Satzbuch_CD/SB_CD_1448-60_ready` — Satzbuch CD, 1448–1460, mit konsequenter Orts- und Mentioned-Annotation.

**Öffentlich** ist die strikte Teilmenge, die der Stakeholder für die Publikation freigegeben hat, das Tupel `PUBLIC_CORPORA` in [`frontend/config.py`](frontend/config.py). Welche Subkorpora ein Build tatsächlich rendert, entscheidet die Sicht (siehe „Sichtbarkeit öffentlich versus intern"): der öffentliche Build rendert nur `PUBLIC_CORPORA`, der interne Build alle `RELEASED_CORPORA`. Quelle der Beschränkung: Stakeholder-Protokoll 18.05.2026 („QGW bis 1414, StB Bd. 1"). Die Funktion `visible_corpora()` in `frontend/config.py` ist die Single Source of Truth, an der jeder Build seine Sammlungs-Menge zieht. Subkorpora außerhalb von `RELEASED_CORPORA` liegen in `sources/` für die editorische Arbeit, werden aber weder exportiert noch gerendert.

Durchgängige Regel, die das absichert: eine Person oder Organisation, die in keiner in der jeweiligen Sicht sichtbaren Quelle vorkommt, bekommt keine Profilseite, keinen Listen- oder Sucheintrag und zählt nicht in den Gesamtzahlen. Regressionstests dazu in `frontend/tests/test_visible_corpora.py` und `frontend/tests/test_public_corpus_scope.py`.

Override für interne Analysen: `PIPELINE_INCLUDE_UNRELEASED=1 python -m pipeline transform` zieht alle Subkorpora in den CSV-Export. Nicht für den publizierten Build verwenden.

Aufnahme eines weiteren Subkorpus: Quelle unter `sources/<Collection>/<Subcollection>_ready/` ablegen, `RELEASED_CORPORA` ergänzen, `python -m pipeline transform`, `python -m frontend build`. Soll der Korpus auch öffentlich erscheinen, zusätzlich in `PUBLIC_CORPORA` aufnehmen. Liegt er außerhalb von 1177–1414, zusätzlich `RELEASED_PERIOD` in [`frontend/config.py`](frontend/config.py) anpassen.

## Stufenmodell

Build und Pipeline kennen vier benannte Stufen, die Korpus-Auswahl und Annotationsebenen als zitierbares Profil bündeln. Aktiviert über `--stage N`; ohne Flag gilt Stufe 1 (Publikation).

| Stufe | Subkorpora | Mentioned-Events | Output |
|---|---|---|---|
| 1 Publikation | alle freigegebenen `_ready` | aus | `docs/` |
| 2 Vergleich | wie Stufe 1 | ein | `docs-with-mentioned/` |
| 3 Voller `_ready`-Bestand | heute deckungsgleich mit Stufe 1 | aus | `docs-full/` |
| 4 Maximalversion | alle mit TEI | ein | `docs-max/` |

Detaillierte Begründung und Achsen in [`knowledge/specification.md`](knowledge/specification.md) unter „Stufenmodell für Korpus-Auswahl und Annotationsebenen".

```
# Stufe 1 (Default, publizierter Stand)
python -m frontend build

# Stufe 2 (Vergleich mit Mentioned-Events)
cd ../db_for_medieval_legal_transactions
PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform
cd ../db_for_medieval_legal_transactions_edition
python -m frontend build --stage 2

# Stufen 3 und 4 analog
cd ../db_for_medieval_legal_transactions
FRONTEND_STAGE=3 python -m pipeline transform
cd ../db_for_medieval_legal_transactions_edition
python -m frontend build --stage 3
```

Helper zum Bauen aller Stufen am Stück: [`scripts/build_all_stages.py`](scripts/build_all_stages.py).

```
python scripts/build_all_stages.py            # alle vier Stufen
python scripts/build_all_stages.py --only 1 3 # nur ausgewaehlte Stufen
```

## Sichtbarkeit öffentlich versus intern

Neben dem Stufenmodell trägt der Build eine zweite, orthogonale Achse, die unterscheidet, *für wen* der Output gedacht ist. Sie wird auf zwei Schichten gelöst.

Build-zeit über die Audience-Achse. CLI-Flag `--audience oeffentlich|intern`, Default `oeffentlich`. Die interne Variante hängt `-intern` an das Stage-Output-Verzeichnis (Stufe 1 plus intern landet in `docs-intern/`) und behält editorisch relevante Sektionen, technische IDs und Aggregat-Achsen, die im öffentlichen Build gefiltert werden. Die Achse ist orthogonal zum Stufenmodell, beide kombinieren sich frei.

Die Audience steuert auch den Korpus-Umfang. Der öffentliche Build rendert nur `PUBLIC_CORPORA`, der interne alle `RELEASED_CORPORA` (siehe „Korpora: freigegeben versus öffentlich"). Wer eine andere Auswahl bauen will, etwa nur ein einzelnes Subkorpus zur internen Prüfung, gibt sie ausdrücklich an: `--corpora <Pfad,Pfad,…>` hat Vorrang vor der Sicht-Vorgabe.

```
python -m frontend build                            # oeffentlich, Stufe 1 → docs/ (2 öffentliche Korpora)
python -m frontend build --audience intern          # interne Sicht → docs-intern/ (alle freigegebenen)
python -m frontend build --stage 2 --audience intern    # Stufe 2 plus interne Sicht
python -m frontend build --audience intern --corpora QGW/Vienna_1448-57_ready   # gezielte Auswahl
```

Client-zeit über einen Dev-Mode-Schalter. URL-Parameter `?dev=1` an einer beliebigen Quellen-Detailseite setzt `.dev-mode` auf das HTML-Wurzel-Element und macht alle Elemente mit der Klasse `.dev-only` sichtbar, ergänzt um einen gelben gestrichelten Rahmen und ein „Entwicklung"-Label. Default-Sicht blendet sie aus. Erstes Anwendungsbeispiel ist die Dispositivformeln-Sub-Tabelle in der Annotationsansicht.

Die zwei Schichten lösen verschiedene Dinge. Audience entscheidet build-zeit, *ob* etwas im Output enthalten ist. Dev-Mode entscheidet client-zeit, *ob* enthaltene Elemente sichtbar geschaltet werden. Begründung in [`knowledge/specification.md`](knowledge/specification.md) unter „Öffentliche versus interne Sicht in zwei Schichten", Architektur-Detail in [`knowledge/architecture.md`](knowledge/architecture.md).

## Zwei-Repository-Setup

Die Datenbank lebt in zwei Repositories, die nebeneinander geklont werden müssen.

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
python -m frontend build                                    # Site neu rendern → docs/
python -m frontend build --single FILE                      # einzelne Quelle
python -m frontend build --stage N                          # Stufe 1..4 (siehe oben)
python -m frontend build --audience oeffentlich|intern      # öffentlich oder intern (siehe oben)
python -m frontend build --corpora PFAD,PFAD                 # ausdrueckliche Korpus-Auswahl (Vorrang vor Audience)
python -m pytest frontend/tests/                            # Frontend-Tests
```

## Technischer Stack

- **Quellen:** TEI-XML (im Pipeline-Repo).
- **Build:** Python mit `lxml` für TEI-Parsing und `Jinja2` für HTML-Rendering.
- **Daten-Aussschicht:** aggregierte JSON-Dateien für clientseitiges Suchen, Filtern und Visualisieren.
- **Frontend:** statische HTMLs, Vanilla-JS-Module, eigenes CSS. Kein Framework, keine Serverlogik.
- **Hosting:** GitHub Pages aus `docs/`.

## UI-Bereiche

Die Datenbank gliedert sich in vier Top-Level-Bereiche:

- **Quellen** (`/documents.html`) — Listenansicht aller freigegebenen Quellen mit Filter, Suche, sortierbarer Tabelle, Volltext-/Regest-Detail.
- **Register → Personen** (`/register/persons.html` + `/register/persons/<id>.html`) — Personenregister mit Suche, Filter, Profilseite pro individueller Person mit Beziehungen und Quellen-Vorkommen. Das Organisationsregister (`/register/orgs.html` plus Profilseiten) ist ebenfalls freigegeben. Ein Ortsregister gibt es nicht: Orts-Stammdaten sind nicht konsolidiert, Orte erscheinen nur als Inline-Markup im Volltext ohne Sprungziel.
- **Analyse** — quantitative Zugänge, zwei Sub-Seiten:
  - `/analysis/auswertungen.html` — vorberechnete Verteilungen (Donut für Funktionsrollen + Beziehungstypen, Bar-Chart für Transaktionstypen, Tabelle mit Mini-Bars für Bezeichnungen). Drill-down ins Quellen-Detail per Klick auf jede Aggregat-Zelle. Filter-Stand in der URL.
  - `/analysis/index.html` — Abfragen-Modus mit vorgefertigten Template-Familien.
- **Exploration** — visuell-interaktive Erkundung der Datenstruktur:
  - `/exploration/zeitstrom.html` — gestapelter Bar-Chart der Quellendichte pro Jahrzehnt; Stack-Achse umschaltbar (Quellenkorpus / Erschließungsform / Geschlecht / Transaktionstyp); Brush-zu-Drill-down; Stack-Kategorie isolierbar. Filter-Stand in der URL.
  - `/exploration/personennetzwerk.html` — Ego-Layout um eine Person; Klick auf Nachbar verlagert Zentrum; Beziehungstyp-Filter (Verwandtschaft / Beruf-Stand / Vertretung / Freundschaft); Personen-Suche.
  - Sankey-Diagramm zu Transaktionsflüssen — geplant.

Quer durch alle Quellen-Listen liegt der **Datenkorb** (`/korb.html`): clientseitige Sammelmappe in `localStorage`, mit „+"-Knopf neben jedem Quellen-Eintrag, Live-Badge im Nav, CSV-Export auf der Korb-Seite.

## Konzeptionelle Dokumentation

Begriffe, Datenstruktur, Architektur, Anforderungen und Gestaltungsprinzipien leben in [`knowledge/`](knowledge/) als zusammenhängende Dokumentation in deutscher Sprache, mit Wiki-Links zwischen den Dokumenten. Einstieg über [`knowledge/index.md`](knowledge/index.md).

Begriffsdefinitionen (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Regest, Faksimile, Volltext, Erschließungsform): [`frontend/content/project/glossar.md`](frontend/content/project/glossar.md). Anforderungs-Spezifikation mit allen Leitentscheidungen: [`knowledge/specification.md`](knowledge/specification.md). Chronologisches Arbeitstagebuch: [`knowledge/journal.md`](knowledge/journal.md).

## Lokales Preview

```
python -m http.server 8765 --directory docs/
```

Aufruf unter `http://localhost:8765/`.

## Lizenz

Noch zu klären.
