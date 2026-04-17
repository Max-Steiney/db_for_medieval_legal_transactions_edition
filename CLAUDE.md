# CLAUDE.md — Edition Repo (Build Output)

## Was ist das hier?

Dieses Repo ist der **Build-Output** der Digital Edition für GitHub Pages. Es wird per Sync-Commit aus dem Pipeline-Repo aktualisiert.

**Pipeline-Repo (Quelle):** `../db_for_medieval_legal_transactions/`
- Jinja2-Templates: `edition/templates/`
- Content (Markdown): `edition/content/`
- Build-Code: `edition/build.py`
- Statische Assets: `edition/static/`
- Registerdaten: `indices/`
- TEI-Quellen: `sources/`

## Arbeitsregel

**HTML-/JSON-Dateien hier nicht direkt editieren.** Änderungen gehören ins Pipeline-Repo, dann:

```
cd ../db_for_medieval_legal_transactions
python -m edition build
```

Build schreibt nach `docs/`. Von dort wird in dieses Repo gesynct.

Ausnahmen:
- `vault/` — Promptotyping-Dokumentation (Legacy-Build-Output aus dem Pipeline-Repo).
- `knowledge/` — konzeptionelle Frontend-Wissensbasis, wird direkt hier gepflegt. Obsidian-kompatible Markdowns mit `[[Wiki-Links]]`. Zeitlos formuliert, keine Meetings / Personen / Quantitäten. Ausnahmen: [[journal]] ist chronologisch und enthält Entscheidungspfade; [[quer ui]] ist eine Analyse-Blaupause mit konkreten quantitativen Eckdaten zum Zeitpunkt ihrer Erstellung. Siehe `knowledge/decisions.md` für Leitentscheidungen.
- `verification/` — unabhängiges Verifikations-Test-Set, wird direkt hier gepflegt.
- `CLAUDE.md`, `README` u. ä. Meta-Dateien.

## Struktur

```
/                         Portal-Einstiegsseiten + flache HTMLs (index, documents, persons, ...)
/documents/<coll>/<sub>/  Regesten als HTMLs, aus TEI gerendert
/tei/<coll>/<sub>/        TEI-XML-Downloads der freigegebenen Quellen
/data/                    JSON-Indexe (search, register, epics, timeline, quality)
/register/                Personen-, Organisations-, Ortsregister (HTML + JSON)
/exploration/             visuell-explorative Zugänge (Rollen, Beziehungen, Transaktionen, Orte)
/analysis/                klassischer Abfragemodus (in Vorbereitung, siehe knowledge/quer ui.md)
/project/                 About, Statistik, Qualität, Editionsrichtlinien, Glossar, Impressum
/static/                  CSS, JS, Fonts
/vault/                   Legacy-Promptotyping-Dokumentation
/knowledge/               konzeptionelle Frontend-Wissensbasis (Obsidian-Markdown)
/verification/            Unabhängiges Verifikations-Test-Set (Python, lxml)
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
- Zentrale Konfiguration: `edition/config.RELEASED_PERIOD`. Hardcoded Zahlen in Templates gelten als Fehler.
- Warntext „Überlieferungslücke 1418–1447" → **„noch nicht ausgewertet"**.

**Datenstand (Fußzeile)**
- **Datenstand** ist das Datum des letzten Pipeline-Repo-Commits, nicht das Build-Datum. Ermittelt über `git log -1 --format=%cI` in `edition/build._pipeline_repo_data_date`.
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
5. **Analyse-Seite mit Template-Familien** — Blaupause in [[quer ui]]. Konkrete Familienmenge braucht Fachteam.
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
- **Vor Änderungen am Build-Output**: prüfen, ob die Änderung ins Pipeline-Repo gehört. Wenn ja: dort machen, rebuild, syncen.

## Vor-Start-Checkliste

| Aufgabe | Lies zuerst |
|---|---|
| Titel/Nav/Footer ändern | `../db_for_medieval_legal_transactions/edition/templates/base.html` |
| Startseite-Inhalt ändern | `../db_for_medieval_legal_transactions/edition/templates/startseite.html` |
| Editionsrichtlinien | `../db_for_medieval_legal_transactions/edition/content/edition_guidelines.md` |
| About / Impressum / Glossar | `../db_for_medieval_legal_transactions/edition/content/` |
| Quellen-Übersicht (Filter, Chips) | `../db_for_medieval_legal_transactions/edition/templates/index.html` |
| Provenienz-Tooltip einsetzen | `../db_for_medieval_legal_transactions/edition/templates/macros.html` (`prov_stat`, `prov_popover`, `prov_ratio_stat`) |
| Erschließungsform-Mapping | `../db_for_medieval_legal_transactions/edition/build._transmission_form` |
| Freigabestand (Zeitraum, Korpora) | `../db_for_medieval_legal_transactions/edition/config.py` |
| Verifikations-Test-Set | `verification/` (Python, lxml), siehe [[architecture#Verifikations-Test-Set]] |
| Analyse-Blaupause | `knowledge/quer ui.md` |
| Konzeptionelle Wissensbasis | `knowledge/` (data, requirements, architecture, ui-design, scholar-user-stories, glossar, decisions, journal, quer ui) |
