# Current Knowledge

Snapshot zum Wiedereinstieg in die nächste Session. Kompakt, sachlich, auf den aktuellen Stand bezogen. Neuester Block oben.

---

# Session 2026-05-11 (abends) — Accessibility, Knowledge-Refactor, specification.md

## 1. Was diese Session geschafft hat

### Accessibility (Commit `e01c3316d7`)

WCAG-AA-Patches an Tabellen, Modals, Live-Regions, Kontrast. Quer durch das Frontend mehrere kleine fokussierte Fixes, die zusammen den überwiegenden Teil der über alle Seiten verstreuten AA-Mängel beheben. pytest 356 passed, vitest 49 passed, Verifikation Stage 1 unverändert.

- Sortable Tables `aria-sort` an allen Spalten in `document.js`, `profile.js`, `table-infra.js`
- Live-Regions `aria-live="polite"` an `result_count`, `active_filters`, `no_results` in `macros.html`
- Focus-Trap + Initialfokus + Return-Fokus im Drilldown-Overlay in `viz-core.js`
- ESC schließt Hamburger-Menü in `core.js`
- Sichtbar-für-AT-H1 (`sr-only`) auf Quellen-Detailseite in `document.html`
- Per-Seite-Alt-Text bei mehrseitigen Faksimiles in `facsimile.js`
- Canvas-Container im Personennetzwerk mit `role="img"` und `aria-describedby` in `exploration_network.html`
- Kontrast-Token `--anno-fn-other` abgedunkelt von `#7a6b8c` auf `#5e5174` in `tokens.css`

Code-Konvention bestätigt: neue Kommentare im Frontend englisch, sparsam, nur dort wo das Warum aus dem Code nicht hervorgeht.

### Knowledge-Refactor (uncommitted)

`requirements.md` wurde gelöscht und durch `specification.md` ersetzt. Begründung: das Dokument hatte sich über die Zeit von einer Soll-Spezifikation zu einem Ist-Beschreibung gewandelt, der Soll-Anspruch in den Texten passte nicht mehr zum Code. Der neue Name macht das ehrlich.

Inhaltliche Änderungen gegenüber dem alten `requirements.md`:

- **Gestrichen**: Anforderung „Umschaltbarkeit der Zählebenen" (global-Toggle existiert nicht und ist nicht geplant; lokaler Donut-Toggle ist UI-Detail), Anforderung „Menschen-Events-Behandlung" (Toggle existiert nicht; Default-Variante ist in `decisions.md` festgeschrieben), Halbsatz „Persistente Identifier oder stabile URLs zu versionierten Datenständen" aus „Zitierfähigkeit" (DOIs gibt es nicht, versionierte Datenstände gibt es nicht).
- **Umformuliert**: alle Anforderungen, weg vom Was/Warum/Wie-Schema, hin zu kompakten flachen Listen pro User-Story (Variante 1).
- **Hinzugefügt**: Querschnitt „Barrierefreiheit" (heute durch die Accessibility-Patches eingelöst), Querschnitt „Verifizierbarkeit" (war vorher nur Nebensatz in Anforderung 1).

Neue Struktur: fünf User-Stories aus Historiker*innen-Perspektive plus Querschnitts-Eigenschaften. Die Stories sind:

1. Eine Person über ihre Quellen und Rollen verfolgen
2. Die Beziehungen einer Person erkunden
3. Rechtsgeschäfte nach Geschlecht und Rolle vergleichen
4. Organisationen und ihre Mitglieder analysieren
5. Quellen ausschnitthaft sammeln, teilen und exportieren

Querschnitts-Eigenschaften: Datenrobustheit/Provenienz, Verifizierbarkeit, Barrierefreiheit, zitierfähiger Datenstand, Informationsdichte.

### Verweis-Drift behoben

In `index.md`, `architecture.md`, `data.md`, `analyse.md`, `decisions.md`, `ui-design.md`, `scholar-user-stories.md` alle Wikilink-Verweise auf `[[requirements]]` und gestrichene Anchor-Targets (`Provenienz-Tip und Glossar-Tip`, `Verifikations-Test-Set`) auf die neuen Ziele umgebogen oder auf nächstliegende Ersatzanker (Glossar, decisions). Tote Anker innerhalb von `scholar-user-stories.md` und `journal.md` bleiben bestehen — beide Dokumente sollen ohnehin in einer eigenen Runde überarbeitet werden.

### `ui-design.md` aufgeräumt

Die drei Abschnitte „Zählebenen-Umschalter (Phase 2, nicht umgesetzt)", „Bestandsfilter (Phase 2, nicht umgesetzt)", „Menschen-Events-Toggle (Phase 2, nicht umgesetzt)" wurden zu einem einzigen Abschnitt „Bestandsfilter" zusammengezogen, der den realen Stand sachlich beschreibt. Provenienz-Tip-Beschreibung im Tip-System auf „Bestand und Zähloperation" reduziert (statt vorher zusätzlich „Menschen-Event-Status und aktive Filter", die es nie gab).

## 2. Konzeptionelle Entscheidungen dieser Session

- **Phase 2 als Konzept fällt weg.** Knowledge-Dokumente beschreiben den Ist-Stand, keine Wartesaal-Klauseln mehr.
- **Lesepublikum sind Historiker*innen**, die mit den Quellen arbeiten. Sprache und Tonlage entsprechend, kein Software-Spezifikations-Jargon.
- **Dokumente sollen umbenannt werden** in einer zukünftigen Runde: `ui-design.md` → `design.md`, `scholar-user-stories.md` → `user-stories.md`, `decisions.md` möglicherweise ganz entfernen.
- **User-Stories als Format** für das Anforderungsdokument, flache Markdown-Listen ohne Dashes und ohne Doppelpunkte.
- **Datenschutz, Mehrsprachigkeit, Druckbarkeit** sind keine relevanten Anforderungen für dieses Projekt und tauchen nicht im Anforderungskatalog auf.

## 3. Was offen ist nach dieser Session

### Sofort committen vor Schlafengehen

Diese Datei plus die Knowledge-Änderungen aus dem Knowledge-Refactor sind heute Abend uncommitted. Nutzer hat explizit darum gebeten, das temporär mit zu committen.

### Nächste Knowledge-Schritte

Liste aus den Befunden, die ich in der Session gegen `data.md` und `specification.md` erhoben habe. Sie sind besprochen, aber noch nicht umgesetzt.

**Für `data.md`** noch zu tun:
- Annotationsebenen von vier auf fünf erweitern (Dispositivformel/Trigger als eigene Ebene ergänzen, ist in der Renderer-Legende sichtbar als eigener Layer aber im Dokument nicht erwähnt)
- Korpus-Pfad-Struktur knapp erklären (`QGW/Vienna_1177-1414_ready` etc.)
- `RELEASED_PERIOD`-Erweiterung „bis 1414 für QGW II/1 und II/2" und Lücke 1418-1447 mit je einem Satz ehrlich machen
- Verweis auf `docs/data/SCHEMA.md` als technische kanonische Quelle ergänzen
- ID-Schema (`pe__`, `org__`, `pl__`, `f__`) kurz erwähnen
- „Erschließungsform" terminologisch klären — der Begriff steht editionstheoretisch (Regest/Volltext/Grundbücher) und TEI-strukturell (abstract/seal/entry/nota) für unterschiedliche Dinge
- Frontmatter `version: 0.1` → `0.2` bumpen

**Für `specification.md`** noch zu tun:
- Story 1 ergänzen mit Suchfunktion auf der Quellenliste (das Suchfeld durchsucht Signatur, Datum, Ort, Korpus-Label, Regest und fehlt heute in der Story)
- Story 3 auseinanderziehen (Auswertungs-Seite und Zeitstrom sind zwei eigenständige Werkzeuge mit unterschiedlichen Forschungs-Pfaden, heute zu eng zusammengefasst)
- Story 4 berichtigen: Organisationen sind im Personennetzwerk *nicht* klickbar (laut `journal.md` Zeile 107), nur eingefärbt. Heute suggeriert die Story einen Sprung, der nicht existiert
- Story 5 ehrlich machen: URL-Sync greift auf den Visualisierungs-Seiten, aber nicht auf der Quellenliste. Vorher verifizieren ob das wirklich so ist (Grep-Befund deutet darauf, nicht 100% gesichert)
- Faksimile-Volltext-Synopse als Element in Story 1 aufnehmen (Quellen-Detailseite hat Volltext und Faksimile parallel, das ist editorisches Kernfeature)
- Erschließungsform als Filter auf der Quellenliste in Story 5 erwähnen
- Querschnitt „Datenrobustheit und Provenienz" um den Drill-down-Mechanismus ergänzen — Tooltip-Text ist nur eine Hälfte, die andere ist der Klick-Drill-down auf jede Aggregat-Zelle
- Verweis auf `verification/findings.md` als bewusst nicht-UI-sichtbares Komplement
- Korpus-Filter wird in Story 1 und 4 nicht erwähnt, obwohl er auf den Registern verfügbar ist — Konsistenz mit Story 5

### Strukturelle Aufgaben (eigene Sessions)

- `scholar-user-stories.md` überarbeiten: das Dokument enthält noch viele Verweise auf gestrichene Anforderungen. Soll laut Nutzer in `user-stories.md` umbenannt werden. Inhaltliche Sichtung, welche Stories noch passen und welche raus.
- `decisions.md` möglicherweise auflösen oder kondensieren. Aktuell hat es 26 Entscheidungen, einige davon sind in `journal.md` redundant.
- `ui-design.md` → `design.md` umbenennen (Dateirename und alle Wikilinks anpassen).

## 4. Wo weitermachen

Wenn die nächste Session direkt an dieser anknüpft:

1. Committen was uncommitted ist (siehe Abschnitt 3.1).
2. `data.md` und `specification.md` mit der Befundliste aus Abschnitt 3.2 überarbeiten.
3. Verify-Lauf, dass nichts gebrochen ist.
4. Anschließend `scholar-user-stories.md` als nächstes Refactor-Ziel.

`MEMORY.md` Eintrag `tei_html_coverage_plan.md` ist nach wie vor gültig. Keine neuen Memory-Einträge in dieser Session, weil die Inhalte projekt-konzeptionell sind und in `knowledge/` gehören.

---

# Session 2026-05-11 (Tag) — Refactor-Session

Snapshot zum Wiedereinstieg in die nächste Session. Kompakt, sachlich, auf den aktuellen Stand bezogen.

## 1. Was die Session geschafft hat

Acht Commits auf `main`, durchgehend grün getestet.

| Commit | Milestone | Inhalt |
|---|---|---|
| `f7843a5162` | M1 | drill-down.js Production-Bug behoben (Migration auf VizCore.openDrillOverlay), 527-Zeilen-Datei chart-helpers.js gelöscht (tot), 19 `<button>` ohne type-Attribut korrigiert, 2 ungenutzte Macros raus |
| `9f6ba7165b` | M2 | Tote CSS-Selektoren raus (`.stats-*`, `.aggregat-corpus-disabled`, `.doc-details`-Reste, `.anno-toggle-popover`), 9 hardcodierte Hex-Farben durch Tokens ersetzt, falscher `--color-sex-m`-Fallback korrigiert |
| `205e4f0688` | M3 | `EdCore.sortKey` + `EdCore.compareValues` aus drei Implementierungen (`index.js`, `profile.js`, `register.js`) konsolidiert; `TableInfra.setupTableFilter` aus zwei Implementierungen konsolidiert; 21 neue JS-Tests |
| `24d5f4ad41` | B | **Mirror-Beziehungen** auf Personenprofilen: wenn `related_key` in `occ_relations_in_sources.csv` ein `pe__`-Key ist, erscheint die Beziehung auch auf dem Bezugs-Profil. Hochadel-Profile zeigen jetzt ihre Amtsträger |
| `bff4dd585c` | M6a | **HTML-Coverage-Stufe** aufgebaut: `verification/parse_html.py` als lxml.html-Reader, `verification/compare_html.py` mit ersten Pruefungen (Name, Geschlecht, Source-Count) |
| `18deee8b5a` | M6b | Quellen-Reader, Beziehungs-Counts-Cross-Check (occ und occ_inverse gegen CSV), Orphan-Check für `data-ref` |
| `e49ff9f47c` | M6c | Erweiterte Coverage (death_display, authority_urls, wiki_url, observance, parent_org), `verification/contract.py` mit must/may/filter-Regeln, Inventory- und README-Update |
| `ed6d0a4f5d` | docs | Journal-Eintrag in `knowledge/journal.md` |

## 2. Stand des Projekts

### Inhaltlich

- **Mirror-Beziehungen live**. Auf Personenprofilen erscheint eine Sektion „Personen mit Beruf / Amt in meinem Bezug", wenn jemand als Bezug in occ-Relationen auftaucht. Schließt die Asymmetrie, die Hochadel-Profile mangels Amtsträger-Sicht hatten.
- **Analyse-Seite drill-down funktioniert**. Der „Quellen anzeigen (N)"-Button hatte stumm nichts getan, jetzt öffnet er das Overlay.
- **Profile sind kompakt**: Header in einer Zeile mit Mikro-Rollen-Strip, horizontale Meta-Strip-Zeile, Quellen-Tabelle direkt unter dem Header, Toolbar nicht sticky.
- **Einheitliche Farblogik**: Link-Farbe nach Ziel-Typ (Person blau, Org lila).

### Technisch

- **JS-Duplikate weg**: Sort- und Filter-Logik je einmal zentral statt drei bzw. zwei Mal verteilt.
- **CSS schlanker um ~120 Zeilen**, Token-Verwendung konsistent.
- **Tote Dateien identifiziert und entfernt**: `chart-helpers.js`, `drill-down.js`-Referenz, plus mehrere CSS-Blöcke.

### Verifikation

`verification/` hat jetzt zwei Coverage-Stufen:

```
python -m verification.run         # TEI → JSON-Aggregate (existierte vorher)
python -m verification.run --html  # Pipeline-CSV → gerendertes HTML (NEU)
python -m verification.run --all   # beide
```

**Stufe 2 (HTML-Coverage)** prüft aktuell 18 Aspekte zwischen `pipeline/output/*.csv` und den HTMLs unter `docs/`. Lauf gegen den aktuellen Build: alle 18 Pruefungen grün, kein Mismatch über 8441 Personen-Profile, 607 Org-Profile, 2601 Quellen-Seiten in 130 Sekunden.

Geprüfte Felder pro Personenprofil:
- display_name (forename_reg + surname_reg + addname_reg)
- sex_label
- source_count gegen Tabellen-Zeilen
- death_display (dead_before ISO → DD.MM.YYYY)
- authority_urls (pipe-split)
- wiki_url (PAGEID_WienWiki)
- occ_count und occ_inverse_count gegen CSV

Geprüfte Felder pro Org-Profil:
- name (pre-pipe), source_count, observance, parent_org_id, authority_urls

Pro Quellen-Seite:
- Jedes `data-ref` (Person/Org) zeigt auf ein existierendes Profil

Reports: `verification/reports/YYYY-MM-DD-html.{md,json}`, versioniert.

### Tests

| | vorher | nachher |
|---|---:|---:|
| Python (pytest) | 350 | **357** (7 neue für `parse_html`) |
| JS (vitest) | 26 (eine Suite kaputt) | **47** (chart-helpers-Test entfernt, 21 neue für sortKey/compareValues/setupTableFilter) |

## 3. Architektur-Schlüsselstellen

Damit eine neue Session direkt produktiv wird, hier die wichtigsten Anker:

### Frontend (CSS/JS/Templates)

- **Tokens**: `frontend/static/css/tokens.css` ist Single-Source-of-Truth für Farben, Spacing, Z-Index. Hardcodes vermeiden, Token-Fallbacks `var(--token, #hex)` sind unnötig (Token wird sicher geladen).
- **Sort/Filter**: `frontend/static/js/core.js` exportiert `EdCore.sortKey` und `EdCore.compareValues` (numerische Detection inbegriffen). `frontend/static/js/table-infra.js` exportiert `TableInfra.setupTableFilter(input, table)` für DOM-Filter mit Umlaut-Toleranz und Wort-AND.
- **Drill-Down-Overlay**: `frontend/static/js/viz-core.js` mit `bindDrillOverlay(opts)` einmalig im init, `openDrillOverlay({overlayId, title, fileKeys, docsLookup})` pro Click.
- **Profile**: `frontend/templates/person.html` und `org.html` teilen sich `.person-*`-CSS aus `person.css`. Class-Names sind historisch, der Org-Reuse von `.person-profile` ist semantisch falsch (Rename in zurückgestelltem Refactor).
- **Aggregator**: `frontend/aggregator/person_profiles.py` baut die Profil-Dicts. `occ_inverse`/`title_ref_inverse` sind Mirror-Slots im rel-Dict (Commit `24d5f4ad41`).

### Verifikation

- **Pfade**: `verification/config.py` definiert `DOCS_DIR`, `HTML_REGISTER_PERSONS`, `HTML_REGISTER_ORGS`, `HTML_DOCUMENTS`.
- **Reader**: `verification/parse_html.py` mit `read_person_profile`, `read_org_profile`, `read_document`, plus `iter_*`-Funktionen. CSS-Selektoren spiegeln das Template-Markup.
- **Pruefungen**: `verification/compare_html.py` mit `check_person_profiles`, `check_org_profiles`, `check_person_extended_fields`, `check_org_extended_fields`, `check_person_relation_counts`, `check_document_refs`.
- **Vertrag**: `verification/contract.py` deklariert pro Feld required/conditional/filter und bekannte Lücken.
- **Inventory**: `verification/inventory.md` Ebene 4 listet alle HTML-Checks mit CSV-Quelle und HTML-Selector.

## 4. Was offen ist

### Hohe Priorität (für nächste Session)

**Coverage-Erweiterungen** (M6 weitergedacht):
- Quellen-HTML-Felder über `data-ref` hinaus: Regest-Volltext gegen TEI-`<note>`, Faksimile-Verfügbarkeit, Provenance-Strip.
- **Dritte Stufe**: TEI direkt gegen HTML (nicht über CSV). Würde sicherstellen, dass jeder `<rs type="person">`-Span im TEI-Body als annotiertes `<span class="anno-person" data-ref="...">` im gerenderten Volltext landet.
- Konsistenz-Checks zwischen Profil und Quellen-Seite: wenn Person X auf Quelle 100 in der Profil-Quellentabelle verweist, muss Quelle 100 `data-ref="pe__X"` im Body haben.

### Mittlere Priorität

**Test-Refactor** (3–4h, eigene Session):
- Historische `test_m1.py`, `test_m2.py`, `test_m3_scholarly.py` (33 Tests, teils redundant mit `test_aggregator.py`/`test_renderer.py`) konsolidieren.
- Langsamen Test beschleunigen: `test_html_has_doctype` (2,66s Setup wegen vollem Build).
- Breitere JS-Coverage: `VizCore.makeDecadeFilter`, `basket.js` (localStorage-Roundtrip), `TableInfra.initRangeSlider` (Range-Math).

### Niedrige Priorität (zurückgestellt, weil Polish ohne User-Wert)

**M4 — CSS-Komponenten** (~60 Min): `.chip`, `.search-box`, `.form-filter-chip`, `.sidebar-block` aus `index.css` (1078 Zeilen) nach `components.css`. Breakpoint-Duplikate (1200/768/480px in `responsive.css` + `exploration.css` + `startseite.css`) zentralisieren.

**M5 — exploration.css splitten** (~90 Min): 2009 Zeilen → `viz-base.css` + `viz-timeline.css` + `viz-network.css` + `viz-aggregat.css`. Templates anpassen. Bruchrisiko, weil falsch zugeordneter Selector silent das Layout zerlegt.

**Tooltip-Konsolidierung** (2–3h): `hint.js` + `tip.js` haben überlappende Mechanik (Viewport-Clamp, Show/Hide-Timing). Gemeinsame Base extrahieren, zwei dünne Modus-Layer drauf. Hohes Brüche-Risiko, weil Tooltips nuanciert sind (Pinning, Hover-Close-Delay).

**Person → Entity-Rename** (2–3h): `.person-profile`/`.person-toolbar`/`.person-header` werden auch auf Org-Profilen verwendet. ~150 Selektoren in `person.css`, zwei Templates, 9048 generierte Profile beim Build. Massen-Refactor, fehleranfällig.

## 5. Operatives

### Build und Tests

```
python -m frontend build                # Site neu bauen
python -m pytest frontend/tests/ verification/  # Python-Tests (357)
cd frontend && npm test                 # JS-Tests (47)
python -m verification.run --html       # HTML-Coverage (130s)
```

### Datenpipeline (Schwester-Repo)

Pipeline-Änderungen erfordern `cd ../db_for_medieval_legal_transactions && python -m pipeline transform`, dann zurück und `python -m frontend build`.

### Git-Konventionen (aus MEMORY.md)

- Alle Commits direkt auf `main`, keine Feature-Branches.
- Niemals `git push` oder `gh pr create` ohne expliziten Auftrag.
- Keine Emojis, keine Dashes (Gedankenstriche) in Ausgaben.
- Keine hardcodierten Quantitäten in Narrativ-Texten (Korpus-Zahlen, Jahre); SSoT ist `RELEASED_PERIOD`.

## 6. Erkenntnisse zur Arbeitsweise

Vier Insights, die in der Session entstanden sind und für die nächste relevant bleiben:

1. **Code-Analyse-Agenten produzieren breite Listen, keine priorisierten Schmerzen.** Vor M4/M5: erst klären, ob es echten User-Schmerz gibt, dann technische Sauberkeit. Nicht andersrum.

2. **Defensive Checks verstecken Bugs.** Der drill-down.js-Production-Bug war durch `if (typeof DrillDown === 'undefined') return` stumm geblieben. Beim nächsten Asset-Audit: alle `typeof X === 'undefined'`-Checks anschauen, was sie tarnen.

3. **TEI-HTML-Coverage ist der strategische Hebel.** Sie findet Daten-Asymmetrien wie das Mirror-Beziehungs-Problem systematisch. Bei zukünftigen Feature-Diskussionen ist die Frage: „würde die Coverage das fangen, wenn jemand es einbaut?"

4. **Cache-Effizienz ist real.** Lange Sessions werden teurer. Saubere Milestone-Trennung und Memory-Einträge (`tei_html_coverage_plan.md`) helfen, künftige Arbeit ohne Konversations-Replay zu starten.

## 7. Wo weitermachen

Wenn die nächste Session direkt produktiv sein soll, in dieser Reihenfolge:

1. `python -m verification.run --html` laufen lassen — Stand bestätigen, ggf. neue Drift.
2. **Coverage-Erweiterungen** (TEI direkt gegen HTML, Konsistenz Profil↔Quelle) — höchster Wert, baut auf jetzigem Stand.
3. Falls neue Mismatches durch (1) gefunden: erst die Daten- oder Renderer-Korrektur, dann Tests.
4. Wenn UI-Arbeit gewünscht: kein blindes M4/M5, sondern erst die Frage „was fehlt dem User?" beantworten.

`MEMORY.md` im Projektordner hat einen Eintrag `tei_html_coverage_plan.md`, der die Coverage-Mechanik in der nächsten Session automatisch in den Kontext bringt.
