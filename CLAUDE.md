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
- `knowledge/` — konzeptionelle Frontend-Wissensbasis, wird direkt hier gepflegt. Obsidian-kompatible Markdowns mit `[[Wiki-Links]]`. Zeitlos formuliert, keine Meetings / Personen / Quantitäten. Siehe `knowledge/decisions.md` für Leitentscheidungen.
- `CLAUDE.md`, `README` u. ä. Meta-Dateien.

## Struktur

```
/                         Portal-Einstiegsseiten + flache HTMLs (index, documents, persons, ...)
/documents/<coll>/<sub>/  Regesten (3.541 HTMLs, aus TEI gerendert)
/tei/<coll>/<sub>/        TEI-XML-Downloads der freigegebenen Quellen
/data/                    JSON-Indexe (search, register, epics, timeline, quality)
/register/                reverse-index JSONs für Personen/Organisationen/Orte
/static/                  CSS, JS, Fonts
/vault/                   Promptotyping-Dokumentation (Legacy-Build-Output)
/knowledge/               konzeptionelle Frontend-Wissensbasis (Obsidian-Markdown)
```

## Finale Terminologie-Entscheidungen (Stand 2026-04-17)

**Haupttitel / Branding**
- Haupt: **Stadt und Gemeinschaft Wien**
- Sub: **Database for Medieval Legal Transactions**
- Footer-Zeile: **Stadt und Gemeinschaft Wien — Datenbank**

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
- Nicht anzeigen: 1524, 1520, 1170 (fehlerhaft generiert im aktuellen Frontend).
- Warntext „Überlieferungslücke 1418–1447" → **„noch nicht ausgewertet"**.

## Phasen-Plan zur CS-Feedback-Einarbeitung

**Phase 1 — Sofortmaßnahmen (diese Arbeitssession, vor 23.04.2026)**

Arbeitsdokument: CS-Feedback 17.04.2026, Punkte 1.1–3.4 in Teil 1 bis Teil 3.

1. Titel, Untertitel, Footer, Zeitraum-Anzeigen (1.1, 1.2, 1.8)
2. Label „Gesamtnennungen" statt „Personen" auf Startseite (1.3)
3. Terminologie-Umstellung: Sammlung → Quellenkorpus (2.1)
4. Neuer Nav-Bereich „Analyse" als **Platzhalter-Seite** (wird in Phase 2 inhaltlich gefüllt)
5. Warntext Überlieferungslücke (1.7)
6. Differenzierte Erschließungsformen (Monasterium / Stadtbücher / Grundbücher) (2.3)
7. Orte/Organisationen bis zur Freigabe deaktivieren (2.4)
8. Personen-Tag-Links reparieren (3.2)
9. Legende mit Info-Texten / Mouse-over (3.3)
10. Glossar-Seite (neue Idee des Users, inkl. Eintrag „Menschen-Events" aus Wissensdokument §4.3)

**Phase 2 — Strukturelle Anforderungen (nach 23.04.2026, aus Wissensdokument)**

Quelle: SuGW – Frontend-Datenrobustheit und Provenienz (Meeting 17.04.2026).

1. **Provenienz-Tooltip-Komponente** (§5): an jedem Datenpunkt — welche Bestände, welche Zähloperation, Menschen-Events ja/nein, aktive Filter.
2. **Umschalter Gesamtnennungen ↔ Individuelle Personen** (§4.1), inkl. Prozentsätze auf beiden Ebenen.
3. **Menschen-Events-Toggle** (§4.3): aktiv ein-/ausschließbar, konsistent durch alle abhängigen Darstellungen.
4. **Bestandsfilter universell** (§4.4): in allen Ansichten, nicht nur Dokumente-Seite.
5. **Analyse-Seite mit 10 Grundabfragen** (§5 Abfragemodus, §7 Capacity Building): Rolle × Geschlecht × Bestand × Nennungsart.
6. **Persistente Referenzierbarkeit / PID** (§6): eingefrorene Datenstände per w3id o. ä.
7. **Datenstand prominent** (nach alter DB): „Stand: TT.MM.JJJJ" in Fußzeile / Startseite.
8. **Quellenbereinigung klären** (§4.2): werden Gesamtnennungen quellenbereinigt gezählt oder alle Einzelnennungen? Im Interface dokumentieren.

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
| About / Impressum / Glossar (neu) | `../db_for_medieval_legal_transactions/edition/content/` |
| Dokumente-Seite (Filter) | `../db_for_medieval_legal_transactions/edition/templates/index.html` |
| Pipeline verstehen | `../db_for_medieval_legal_transactions/CLAUDE.md` |
| Session-Journal (Legacy) | `vault/journal.html` |
| Konzeptionelle Wissensbasis | `knowledge/` (data, requirements, architecture, ui-design, scholar-user-stories, glossar, decisions, journal) |
