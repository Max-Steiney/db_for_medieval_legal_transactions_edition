# CLAUDE.md — Frontend Repo

## Was ist das hier?

Dieses Repo ist die **Publikations-Schicht** der Datenbank „Stadt und Gemeinschaft Wien, Datenbank zu mittelalterlichen Wiener Rechtsgeschäften". Hier liegen Build-Code, Templates, statische Assets und das gerenderte HTML, das GitHub Pages ausliefert.

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
  /register/              Personen- und Organisationsregister
                            persons.html | orgs.html              Listen-Seiten
                            persons/<id>.html | orgs/<id>.html    Detail-Profile pro Entität
                            persons.json | organisations.json     Reverse-Index Entität --> Quellen
                            (Ortsregister entfernt: Orts-Stammdaten noch nicht
                             konsolidiert; rs type="place" bleibt als Span mit
                             Tooltip im Quellen-Volltext, aber ohne Sprungziel)
  /analysis/              Analyse-Bereich (nur interner Build docs-intern/, oeffentlich ausgeblendet)
                            auswertungen.html  quantitative Verteilungen (Donut, Bar, Tabelle), Drill-down + Cross-Nav
                            index.html         Abfragen (Template-Familien)
  /exploration/           visuell-interaktive Erkundung (nur interner Build docs-intern/, oeffentlich ausgeblendet)
                            zeitstrom.html         gestapelter Timeline-Bar-Chart mit Brush-to-Drill-down,
                                                   Stack-Kategorie isolierbar
                            personennetzwerk.html  Ego-Layout um eine Person, Klick verlagert Zentrum
                            (Sankey - geplant; keine Karten - Orts-Aussagen liegen
                             ausserhalb des Forschungsfokus)
  korb.html               Datenkorb (clientseitig, localStorage); CSV-Export, Cross-Tab-Sync
  /project/               About, Annotationsrichtlinien, Glossar
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
python -m frontend build                          # baut docs/ aus aktuellem Pipeline-Output (Stufe 1, oeffentlich)
python -m frontend build --single FILE            # einzelne Quelle
python -m frontend build --stage N                # Stufenmodell, N in 1..4 (siehe frontend/stages.py)
python -m frontend build --audience oeffentlich|intern    # Sichtbarkeits-Achse, Default oeffentlich
python -m frontend build --include-mentioned      # Alias fuer --stage 2, schreibt nach docs-with-mentioned/
python scripts/build_all_stages.py                # Pipeline+Frontend fuer alle Stufen am Stueck
python scripts/build_all_stages.py --only 1 3     # nur ausgewaehlte Stufen
python -m pytest frontend/tests/                  # Frontend-Tests (kompakt: -q --tb=no --no-header)
python -m verification.run                        # Stufe 1: TEI -> JSON-Aggregate
python -m verification.run --html                 # Stufe 2: Pipeline-CSV -> gerendertes HTML
python -m verification.run --tei-html             # Stufe 3: TEI direkt -> gerendertes HTML
python -m verification.run --all                  # alle drei Stufen
python -m verification.run --inventory            # TEI-Element-Inventar pro Subkorpus
python -m verification.run --research-questions    # Stufe 4: Forschungsfragen gegen Pipeline-Sollwert
```

`--stage N` setzt `FRONTEND_STAGE=N` und davon abgeleitete Env-Vars. Stufen schreiben in eigene Output-Verzeichnisse (`docs/`, `docs-with-mentioned/`, `docs-full/`, `docs-max/`). Vor einem Vergleichsbuild muss die Pipeline einmal mit dem Mentioned-Filter laufen (`PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform`); mit dem Helper-Skript automatisch. Konzept und vollständige Stufentabelle in [`knowledge/specification.md`](knowledge/specification.md) unter „Stufenmodell fuer Korpus-Auswahl und Annotationsebenen".

`--audience oeffentlich|intern` (Default `oeffentlich`) ist die zweite, orthogonale Achse. Öffentlich schreibt unverändert in das Stufen-Verzeichnis, intern hängt `-intern` an (Stufe 1 plus intern landet in `docs-intern/`). Die interne Variante behält editorisch relevante Sektionen, technische IDs und Aggregat-Achsen, die der öffentliche Build filtert. Daneben existiert ein Client-Schalter: `?dev=1` an einer beliebigen Quellen-Detailseite setzt `.dev-mode` auf `<html>` und macht `.dev-only`-Elemente sichtbar mit gelbem Rahmen. Konzept und Begründung in [`knowledge/specification.md`](knowledge/specification.md) unter „Öffentliche versus interne Sicht in zwei Schichten".

Test-Strategie und Abgrenzung der vier Säulen (pytest, Verifikation, JS-Tests, Sichtprüfung): [`knowledge/architecture.md`](knowledge/architecture.md) Abschnitt _Test-Strategie_.

**TEI-Quellen, Register, Pipeline-Code** gehören ins Schwester-Repo. Nach Änderungen dort:

```
cd ../db_for_medieval_legal_transactions
python -m pipeline transform     # CSVs neu erzeugen
cd -
python -m frontend build         # gegen frische CSVs neu bauen
```

`docs/` ist Build-Output. Nicht direkt editieren — durch Rebuild erzeugen. Ausnahme: Meta-Dateien wie `CLAUDE.md`, `README.md`, `knowledge/`.

## Begriffe und Leitentscheidungen

Begriffsdefinitionen leben in [`frontend/content/project/glossar.md`](frontend/content/project/glossar.md) (Quellenkorpus, Quelle, Event, Rechtsgeschäft, Gesamtnennung, Individuelle Person, Menschen-Event, Rolle, Regest, Faksimile, Volltext, Erschließungsform). Dieselbe Markdown-Quelle wird zur Glossar-Seite gerendert und speist UI-Tooltips über das `tip_glossary`-Macro.

Anforderungs-Spezifikation der Anwendung mit allen Leitentscheidungen lebt in [`knowledge/specification.md`](knowledge/specification.md). Kanonische Begriffshierarchie: Quellenkorpus → Quelle → Event → Gesamtnennung. Kontrolliertes Rollenvokabular (Code-Werte): `issuer`, `recipient`, `witness`, `other`. `witness` deckt die TEI-Formulierung „sealer or witness" ab; ein nicht gesetzter Wert ist der leere String, nicht `none`.

Freigabestand laut SSoT `frontend/config.RELEASED_PERIOD`: Kernzeitraum 1177 bis 1412, ergänzt durch QGW II/2 bis 1457 und Satzbuch CD bis 1460, Lücke 1418 bis 1447 als „noch nicht ausgewertet". Der öffentliche Build zeigt nur den engeren `PUBLIC_CORPORA`-Ausschnitt (aktuell nur QGW II/1 bis 1414; Stadtbücher Bd. 1 laut Frontend-Meeting 17.06.2026 vorerst zurückgestellt, siehe Kommentar in `frontend/config.py`); die übrigen freigegebenen Korpora erscheinen nur im internen Build. Single-Source-of-Truth: `frontend/config.RELEASED_PERIOD` (Zeitraum) und `pipeline/config.RELEASED_CORPORA` im Schwester-Repo (Korpora-Set). Hardcoded Zahlen in Templates gelten als Fehler.

Datenstand (Footer) ist das Datum des letzten Pipeline-Repo-Commits, nicht das Build-Datum. Ermittelt in `frontend/build._pipeline_repo_data_date()`.

Gestaltungsprinzip: maximaler Informations-Output. Nachvollziehbarkeit vor reduzierter Ästhetik. Details in [`knowledge/ui-design.md`](knowledge/ui-design.md).

## Agent-Regeln

- **Sprache:** Deutsch bei inhaltlichen Änderungen; Englisch im Pipeline-Code.
- **Keine Pushes:** lokale Commits; Pushen nur auf expliziten Auftrag.
- **Keine Emojis** in irgendeiner Ausgabe.
- **Minimale Lösungen:** pragmatisch vor ausgebaut. Copy-Paste-Snippets statt neuer UI-Seiten, wenn möglich.
- **Keine Annahmen:** Wenn Kontext fehlt, recherchieren oder rückfragen — nicht raten.
- **Vor Änderungen:** prüfen, ob Frontend (hier) oder Datengrundlage (Schwester-Repo) betroffen ist. `docs/` nicht direkt editieren.
- **Keine UI-Inkonsistenzen:** Derselbe Begriff hat im gesamten UI dasselbe Label. Labels für gleiche Daten-Felder werden über Org-Profil, Personen-Profil, Sidebar, Tooltips synchron gehalten. Detail in [`knowledge/ui-design.md`](knowledge/ui-design.md) unter „Begriffs- und Label-Konsistenz".
- **Sichtbarkeits-Konvention:** Elemente, die nur in der internen Sicht erscheinen sollen, werden mit der CSS-Klasse `.dev-only` markiert, nicht mit eigenen Render-Branches. Default-Sicht blendet sie aus, `?dev=1` an der URL macht sie mit gelbem Rahmen sichtbar. Strukturelle Entfernung aus dem Build (statt nur Verbergen) geht über den Audience-Track (`--audience oeffentlich|intern`), nicht über `.dev-only`. Konzeptuelle Trennung in [`knowledge/specification.md`](knowledge/specification.md) unter „Öffentliche versus interne Sicht in zwei Schichten".
- **Keine technischen IDs im öffentlichen UI:** Personen-, Org- und Event-IDs (`pe__...`, `org__...`, `ev__...`) erscheinen in der öffentlichen Sicht nicht im sichtbaren Text. Sie leben weiter im URL-Slug und in `href`/`data-ref`-Attributen für Zitierbarkeit und Verlinkung. Im internen Build und mit `?dev=1` sichtbar. Beschluss: Stakeholder-Protokoll 18.05.2026 A.3.2.
- **Macros mit `with context` importieren**, wenn sie `root_path` oder andere Template-Variablen aus dem Kontext nutzen. `tip_glossary` ist das prominente Beispiel; ohne `with context` produziert es absolute `/project/...`-Links, die auf GitHub Pages mit Subpfad ins Leere zeigen. Macros, die `root_path` als expliziten Parameter nehmen (`doc_nav`, `funding_table`, `occ_table`), sind nicht betroffen.
- **Test-Pair pro UI-Änderung:** Jede UI- oder Daten-Änderung bekommt im selben Commit einen Regression-Test in `frontend/tests/`. Pattern und Begründung in [`knowledge/test-strategy.md`](knowledge/test-strategy.md). Wenn kein Test sinnvoll ist (rein visuelle Politur), in der Commit-Message vermerken.
- **Subagents auf Windows:** Worktrees brauchen `git config --global core.longpaths true`. Sonst scheitern Subagents am 260-Zeichen-Limit, weil die langen Org-Profil-Dateinamen (`org__wien-st_stephan-kapelle_...`) plus `.claude/worktrees/agent-<id>/`-Pfade die Grenze sprengen.

## Stakeholder-Protokolle

Aktive Stakeholder-Entscheidungen, deren Bezug man pro Task kennen muss.

- **18.05.2026 (Lutter, Handl, Siegl, Steinböck):** Prio 1 Analyse und Exploration aus öffentlicher Sicht ausblenden, ausschließlich freigegebene Korpora (QGW bis 1414, StB Bd. 1), gendergerechte Sprache, Konsistenz Korpus vs. Frontend, Suchlogik. Prio 2 relationale Verknüpfungen, Tabellen-Erklärungen, visuelle Lesbarkeit der Annotationen, problematische Analysekategorien. Pflicht-Bezug: jede Frontend-Task prüft, ob sie Punkt aus diesem Protokoll betrifft.

## Vor-Start-Checkliste

| Aufgabe | Lies zuerst |
|---|---|
| Titel/Nav/Footer ändern | `frontend/templates/base.html` |
| Startseite-Inhalt ändern | `frontend/templates/startseite.html` |
| Quellen-Übersicht (Filter, Chips, Tabelle) | `frontend/templates/index.html`, `frontend/static/js/index.js` |
| Annotations-Block auf Quellen-Detailseite (Tabs, Sub-Tabellen, Section-Header) | `frontend/static/js/document.js`, `frontend/static/css/document.css`; UI-Konvention in [`knowledge/ui-design.md`](knowledge/ui-design.md) unter „Annotations-Block" und „Tabellen-Schicht" |
| Sichtbarkeit öffentlich oder intern ändern | `frontend/audiences.py` (Audience-Achse, Build-zeit) für strukturelle Entfernung; CSS-Klasse `.dev-only` plus `?dev=1`-Schalter (Client-Schicht) für Verbergen im selben Build. Konzept in [`knowledge/specification.md`](knowledge/specification.md) unter „Öffentliche versus interne Sicht in zwei Schichten" |
| Auswertungen-/Zeitstrom-/neue Visualisierungs-Sub-Seite | `frontend/static/js/viz-core.js` zuerst (geteilte Helfer: Range-Slider, Active-Filter-Strip, URL-Sync, Drill-Overlay, JSON-Loader, Domain-Konstanten); page-spezifischer Renderer ruft die Bindings in `DOMContentLoaded` |
| Datenkorb-Anbindung (jede neue Quellen-Liste) | `DataBasket.buttonHTML({id, label, url, date, coll, regest})` ins Zeilen-Markup; Click-Handling über globale Event-Delegation in `frontend/static/js/basket.js` |
| Provenienz- oder Glossar-Tooltip einsetzen | `frontend/templates/macros.html` (`tip_glossary` Glossar, `tip_help` UI-Hilfe, `tip_data_trigger`/`tip_data_body` Provenienz-Popover) |
| Faksimile-Viewer (Zoom, Pan, Rotation) | `frontend/static/js/facsimile.js` plus `doc-facs-panel` in `frontend/templates/document.html`; Lib vendoret unter `frontend/static/vendor/openseadragon/`. UI-Detail in [`knowledge/ui-design.md`](knowledge/ui-design.md) unter „Quellen-Detailseite mit Text-Bild-Synopse" |
| Pro-Quelle-Daten (Personen/Events/Datum) | `frontend/aggregator/docs.py::aggregate_docs` schreibt `docs/data/docs_aggregate.json` |
| Erschließungsform | aus `events_in_sources.csv:event_in` aggregiert (abstract / seal / entry / nota); keine Heuristik im Frontend |
| Annotationsrichtlinien (lokale Kopie) | `frontend/content/project/edition-guidelines.md`; kanonische Quelle im Schwester-Repo (`../db_for_medieval_legal_transactions/edition_guidelines.md`), Kopie bei Bedarf synchronisieren |
| About / Glossar / Annotationsrichtlinien | `frontend/content/project/` |
| Impressum | `frontend/content/impressum.md` |
| TEI-Quellen | `../db_for_medieval_legal_transactions/sources/` |
| Register | `../db_for_medieval_legal_transactions/indices/` |
| Pipeline / CSV-Format | `../db_for_medieval_legal_transactions/knowledge/architecture.md` |
| Verifikations-Test-Set | [`verification/README.md`](verification/README.md) (drei Coverage-Stufen, Run-Kommandos, Statuswerte) und [`verification/findings.md`](verification/findings.md) (aktive Befunde) |
| Test-Strategie und Pattern „Code plus Test im selben Commit" | [`knowledge/test-strategy.md`](knowledge/test-strategy.md) |
| Konzeptionelle Wissensbasis | [`knowledge/`](knowledge/) — Einstieg über `knowledge/index.md` |
