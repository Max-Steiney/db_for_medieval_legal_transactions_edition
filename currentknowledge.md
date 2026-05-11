# Current Knowledge — Refactor-Session 2026-05-11

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
