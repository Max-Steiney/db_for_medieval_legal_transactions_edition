# CLAUDE.md — Frontend Repo

## Was ist das hier?

Dieses Repo ist die **Publikations-Schicht** der Digital Edition. Hier liegen:

- `frontend/` — Build-Code (Python/Jinja2), Templates, Content (Markdown), statische Assets, Tests
- `docs/` — gerenderte Seite, von GitHub Pages serviert
- `knowledge/` — konzeptionelle Frontend-Wissensbasis (Obsidian-Markdown)
- `verification/` — unabhängiges Verifikations-Test-Set
- `vault/` — Legacy-Promptotyping-Dokumentation

Die **Datengrundlage** (TEI-Quellen, Register, Normalisierungslisten, Pipeline) liegt im Schwester-Repo `../db_for_medieval_legal_transactions`. Beide Repos müssen nebeneinander geklont sein; `frontend/__init__.py` legt das Pipeline-Repo automatisch auf `sys.path`, damit `from pipeline.config import …` funktioniert (kein Install-Step, kein Submodule).

## Arbeitsregel

**Frontend-Änderungen** (Templates, Build-Code, Content, statische Assets) gehören hierher. Build:

```
python -m frontend build                # baut docs/ aus aktuellem Pipeline-Output
python -m frontend build --single FILE  # einzelne Quelle
python -m pytest frontend/tests/        # Frontend-Tests
```

**TEI-Quellen, Register, Pipeline-Code** gehören ins Schwester-Repo. Wenn du dort etwas änderst:

```
cd ../db_for_medieval_legal_transactions
python -m pipeline transform     # CSVs neu erzeugen
cd -
python -m frontend build         # Frontend gegen frische CSVs neu bauen
```

Anmerkungen zu Nicht-Build-Inhalten dieses Repos:
- `knowledge/` — konzeptionelle Frontend-Wissensbasis. Obsidian-kompatible Markdowns mit `[[Wiki-Links]]`. Zeitlos formuliert, keine Meetings / Personen / Quantitäten. Ausnahmen: [[journal]] ist chronologisch und enthält Entscheidungspfade; [[analyse]] ist eine Analyse-Blaupause mit konkreten quantitativen Eckdaten zum Zeitpunkt ihrer Erstellung. Siehe `knowledge/decisions.md` für Leitentscheidungen.
- `verification/` — unabhängiges Verifikations-Test-Set.
- `vault/` — Legacy-Promptotyping-Dokumentation.
- `CLAUDE.md`, `README` u. ä. Meta-Dateien.

## Struktur

```
frontend/                 Build-Code: Python (build.py, aggregator.py, renderer.py, register.py),
                          Templates (Jinja2), Content (Markdown), statische Assets, Tests
docs/                     gerenderte Seite (von GitHub Pages serviert)
  /                       Portal-Einstiegsseiten + flache HTMLs (index, documents, persons, ...)
  /documents/             Regesten als HTMLs, aus TEI gerendert
  /tei/                   TEI-XML-Downloads der freigegebenen Quellen
  /data/                  JSON-Indexe (search, register, epics, timeline, quality)
  /register/              Personen-, Organisations-, Ortsregister (HTML + JSON)
  /exploration/           visuell-explorative Zugänge (Rollen, Beziehungen, Transaktionen, Orte)
  /analysis/              klassischer Abfragemodus (in Vorbereitung, siehe knowledge/analyse.md)
  /project/               About, Statistik, Qualität, Editionsrichtlinien, Glossar, Impressum
  /static/                CSS, JS, Fonts
knowledge/                konzeptionelle Frontend-Wissensbasis (Obsidian-Markdown)
verification/             Unabhängiges Verifikations-Test-Set (Python, lxml)
vault/                    Legacy-Promptotyping-Dokumentation

../db_for_medieval_legal_transactions/   Schwester-Repo (Datengrundlage)
  sources/                TEI-Quellen (read by frontend via filesystem)
  indices/                Register
  pipeline/               CSV-Generator (read via from pipeline.config import …)
  pipeline/output/        CSVs (read by frontend)
```

## Finale Terminologie-Entscheidungen (Stand 2026-04-17)

**Haupttitel / Branding**
- Haupt: **Stadt und Gemeinschaft Wien**
- Sub: **Datenbank zu mittelalterlichen Wiener Rechtsgeschäften**
- Footer-Zeile: **Stadt und Gemeinschaft Wien — Datenbank**

Die Nav-Brand zeigt nur den Haupttitel. Der Sub-Text lebt ausschließlich als Hero-Description auf der Startseite.

**Navigationsbereiche (drei, nicht zwei)**
- **Dokumente** — Volltextsuche / Browse über Quellen.
- **Register** — Personen, Organisationen, Orte.
- **Exploration** — visuell-explorative Zugänge (Epics A–D: Rollen, Beziehungen, Transaktionen, Orte). Bleibt als Begriff erhalten.
- **Analyse** (neu) — klassischer Abfragemodus: wiederkehrende Kombinationen aus Bestand × Rolle × Geschlecht × Nennungsart. Vorbild: Standardsuche der alten Datenbank. Ersetzt NICHT die Exploration, sondern ergänzt sie als eigener Zweig.
- **Projekt** — About, Statistik, Qualität, Editionsrichtlinien, Glossar, Impressum.

**Begriffshierarchie (aus alter DB etabliert)**
- **Quellenkorpus** statt „Sammlung" (z. B. `QGW`, `Stadtbuecher` als oberste Gruppe)
- **Quellen** (einzelne Urkunden / Regesten)
- **Events** bzw. **Rechtsgeschäfte** (in Quellen verzeichnete Transaktionen)
- **Gesamtnennungen** — alle Erwähnungen einer Person/Organisation/eines Ortes (über mehrere Quellen hinweg)
- **Individuelle Personen/Organisationen/Orte** — konsolidierte Identitäten (Registereintrag)

**Rollen-Vokabular** (TEI-kodiert): `issuer`, `recipient`, `sealer or witness`, `other`, `none`.

**Zeitraum-Anzeige (Freigabestand)**
- **1177–1412**, Ausnahme **1414 für QGW II/1 und II/2**.
- Zentrale Konfiguration: `frontend/config.RELEASED_PERIOD`. Hardcoded Zahlen in Templates gelten als Fehler.
- Warntext „Überlieferungslücke 1418–1447" → **„noch nicht ausgewertet"**.

**Datenstand (Fußzeile)**
- **Datenstand** ist das Datum des letzten Pipeline-Repo-Commits, nicht das Build-Datum. Ermittelt über `git log -1 --format=%cI` in `frontend/build._pipeline_repo_data_date`.
- Lesbare deutsche Langform (z. B. „17. April 2026"), nicht ISO.

**Farblogik**
- Blau (`--anno-person`): Icons, Eyebrow-Labels, Link-Hover, Provenienz-Trigger — alles Interaktive und Kategorisierende.
- Schwarz: Inhaltstitel, Card-Titel, Regesttexte.
- Gedämpftes Grau: Beschreibungstexte, Metadaten, Fußnoten.

## Phasen-Plan zur CS-Feedback-Einarbeitung

**Phase 1 — Sofortmaßnahmen: erledigt.**

Titel/Untertitel/Footer, Zeitraum-Anzeige, Label „individuelle Personen", Terminologie Quellenkorpus, Analyse-Platzhalter, „noch nicht ausgewertet", Erschließungsform-Chips (Regest + Faksimile / Volltext), deaktivierte Organisations-/Orts-Register, Tag-Links zu Register-Einträgen, Glossar-Seite mit Einträgen zu [[glossar#Menschen-Event]] und [[glossar#Gesamtnennung]].

**Phase 2 — Strukturelle Anforderungen**

Quelle: CS-Feedback 2026-04-17 (Meeting). Status pro Punkt:

1. **Provenienz-Tooltip-Komponente** — Komponente steht. Ausgerollt auf Startseite, Exploration-Hub, Personenregister, Datenqualität. Weiterer Ausbau auf Exploration-Sub-Seiten, Transaktionen, Statistik offen.
2. **Umschalter Gesamtnennungen ↔ Individuelle Personen** — Konzept in [[requirements#Umschaltbarkeit der Zählebenen]] und [[ui-design#Zählebenen-Umschalter]]. Implementierungspfad in [[journal]] (Eintrag Terminologie-Konsolidierung).
3. **Menschen-Events-Toggle** — analog, Implementierungspfad in [[journal]].
4. **Bestandsfilter universell** — Korpus-Chips auf Quellen-Übersicht; universelle Ausrollung offen, Implementierungspfad in [[journal]].
5. **Analyse-Seite mit Template-Familien** — Blaupause in [[analyse]]. Konkrete Familienmenge braucht Fachteam.
6. **Persistente Referenzierbarkeit / PID** — beschlossen, technische Ausprägung (w3id, ARK, Handle) braucht Stakeholder-Entscheidung. Siehe [[requirements#Zitierfähige Datenstände]].
7. **Datenstand prominent** — erledigt, lebt im Footer als Pipeline-Commit-Datum in deutscher Langform.
8. **Quellenbereinigung klären** — erledigt. Zählung ist quellenbereinigt, dokumentiert in [[glossar#Gesamtnennung]], [[decisions#Quellenbereinigte Zählung]] und im Provenienz-Tooltip der individuellen Person.

**Gestaltungsprinzip:** *Maximaler Informations-Output*. Nachvollziehbarkeit vor reduzierter Ästhetik. Bewusst anders als konsumnutzer-orientierte Design-Konventionen.

## Agent-Regeln

- **Sprache:** Deutsch bei inhaltlichen Änderungen; Englisch im Pipeline-Code.
- **Keine Pushes:** Nur lokale Commits. Pushen nur auf expliziten Auftrag.
- **Keine Emojis** in irgendeiner Ausgabe.
- **Minimale Lösungen:** pragmatisch vor ausgebaut. Copy-Paste-Snippets statt neuer UI-Seiten, wenn möglich.
- **Keine Annahmen:** Wenn Kontext fehlt, entweder recherchieren oder Rückfrage stellen — nicht raten.
- **Vor Änderungen**: prüfen, ob die Änderung Frontend (Templates / Build-Code / Content) oder Datengrundlage (TEI / Register / Pipeline) betrifft. Frontend hier; Datengrundlage im Schwester-Repo `../db_for_medieval_legal_transactions`. `docs/` ist Build-Output und wird durch `python -m frontend build` neu erzeugt — nicht direkt editieren.

## Vor-Start-Checkliste

| Aufgabe | Lies zuerst |
|---|---|
| Titel/Nav/Footer ändern | `frontend/templates/base.html` |
| Startseite-Inhalt ändern | `frontend/templates/startseite.html` |
| Editionsrichtlinien | `frontend/content/edition_guidelines.md` |
| About / Impressum / Glossar | `frontend/content/` |
| Quellen-Übersicht (Filter, Chips) | `frontend/templates/index.html` |
| Provenienz-Tooltip einsetzen | `frontend/templates/macros.html` (`prov_stat`, `prov_popover`, `prov_ratio_stat`) |
| Erschließungsform-Mapping | `frontend/build._transmission_form` |
| Freigabestand (Zeitraum, Korpora) | `frontend/config.py` (Zeitraum) und `../db_for_medieval_legal_transactions/pipeline/config.py::RELEASED_CORPORA` (Korpora-Set) |
| TEI-Quellen | `../db_for_medieval_legal_transactions/sources/` |
| Register | `../db_for_medieval_legal_transactions/indices/` |
| Pipeline / CSV-Format | `../db_for_medieval_legal_transactions/knowledge/architecture.md` |
| Verifikations-Test-Set | `verification/` (Python, lxml), siehe [[architecture#Verifikations-Test-Set]] |
| Analyse-Blaupause | `knowledge/analyse.md` |
| Konzeptionelle Wissensbasis | `knowledge/` (data, requirements, architecture, ui-design, scholar-user-stories, glossar, decisions, journal, analyse, exploration) |
