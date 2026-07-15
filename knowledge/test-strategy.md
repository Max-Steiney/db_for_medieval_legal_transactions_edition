---
title: Test-Strategie
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/Max-Steiney/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-05-23
updated: 2026-05-23
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Testing]]", "[[Regression]]"]
related: [architecture, ui-design, journal]
---

# Test-Strategie

Wie sichern wir, dass die Daten sauber und vollständig im Frontend ankommen und dort sauber gerendert werden.

## Vier Säulen

Die Qualitätssicherung steht auf vier komplementären Säulen. Jede deckt eine Fehlerklasse ab, die die anderen nicht sehen.

**Pytest** (`frontend/tests/`) testet den Build-Code: Aggregator-Funktionen, Renderer, Template-Rendering, Tooltip-Strings, Konfig-Loading. Läuft in elf Sekunden, gehört zu jedem Build. Fängt Regressionen in der Programmlogik.

**Verifikations-Test-Set** (`verification/`) prüft Daten-Konsistenz End-to-End in drei Coverage-Stufen (TEI zu JSON, CSV zu HTML, TEI zu HTML), plus TEI-Inventar. Eigene Codebasis ohne geteilte Aggregations-Funktionen, damit die Pipeline sich nicht selbst verifiziert. Findet Pipeline-Drift, Renderer-Halluzinationen, Orphan-Annotationen.

**JS-Tests** (`frontend/tests/js/`) testen die Browser-Logik: URL-Sync der Abfrage-Page, Core-Helpers, Document-spezifische Annotation-Builder. Decken den Teil ab, den statische HTML-Snapshots nicht erreichen.

**Manuelle Sichtprüfung** deckt Layout, Tooltip-Positionierung, Druckansicht, Lesefluss. Teil jeder größeren UI-Änderung, nicht der CI.

Detailbeschreibung in [[architecture#Test-Strategie]].

## Pattern Code plus Test im selben Commit

Jede UI- oder Daten-Änderung bekommt im selben Commit einen Regression-Test. Begründung: Tests-als-Nachgedanke verschiebt sie immer nach hinten und produziert Lücken. Wenn der Test im selben Commit landet, ist die Anforderung dauerhaft abgesichert und ein Sign-off von Behauptung („IDs sind weg") zu Messung („Test grün") gehoben.

Beispiele für den Pattern:

- ID-Entfernung in Tooltips. Code-Change in `register.py` plus Test-Anpassung in `test_register.py`, beides im selben Commit.
- Datenkorb-Label-Konsistenz. Wenn „Aktiv" zu „Datum der Quellen" wandert, prüft ein neuer Test, dass der Spaltenheader im gerenderten Korb-HTML so heißt.
- Audience-Filter. Wenn Analyse und Exploration aus der öffentlichen Nav verschwinden, prüft ein Test, dass die entsprechenden Pfade nicht in der gerenderten `docs/index.html` als sichtbarer Link auftauchen.

Ausnahme: rein visuelle Politur (Farbton, Padding, Hover-Zustand) braucht keinen Test, weil sie sich nicht binär entscheiden lässt. Im Commit-Message vermerken.

## Test-Typen

Vier wiederkehrende Test-Typen, die zu den vier Säulen passen.

**Unit-Tests für Hilfsfunktionen.** Eingabe-Output-Tabellen für Tooltip-Builder, Date-Parser, ID-Slug-Konstruktion. Klein, schnell, deckt Edge-Cases ab. Pattern in `test_register.py` (Tooltip-Builder), `test_data_schema.py` (Schema-Validierung).

**Aggregator-Tests.** Geben CSV-Fixtures rein, prüfen das Aggregat-JSON. Pattern in `test_aggregator.py`, `test_org_profile_sections.py`. Fängt Pipeline-zu-Aggregator-Drift.

**Render-Tests.** Bauen Templates mit Fixture-Daten, prüfen das HTML. Pattern in `test_renderer.py`, `test_register_pages.py`. Fängt Template-Drift.

**Build-then-grep-Tests.** Lassen den vollen Build laufen, dann greppen über `docs/`. „Diese Klasse darf nicht im sichtbaren Text auftauchen", „Dieser Pfad muss in jedem Profile-HTML linken". Robust, deckt das HTML-Output-Ende ab, ist aber langsam (braucht vollen Build). Beispiel: Regression-Test, dass `pe__`, `org__`, `ev__` in keiner Public-HTML im sichtbaren Text vorkommen.

## Lücken, die bewusst offen bleiben

Nicht alles ist automatisierbar oder lohnt sich.

**Browser-Visual-Regression.** Screenshot-Vergleich pro Seite mit Playwright o. Ä. wäre der nächste Ausbau-Schritt, ist aber separater Meilenstein. Lücke deckt aktuell die manuelle Sichtprüfung.

**JS-rendered DOM-Inhalte.** Die Annotations-Tabelle wird zur Laufzeit aus den TEI-Spans aufgebaut, statisches HTML zeigt nur Container. Build-then-grep-Tests greifen hier nicht direkt. Die `frontend/tests/js/`-Tests decken die Logik ab, nicht das gerenderte DOM.

## Datenfeld-Coverage als nächster Ausbauschritt

Pro relevantem Datenfeld eine Spec-Zeile: „Der Anzeigename `display` (keine eigene `persons.csv`-Spalte, sondern in `register.py` aus den Namensteilen `forename`/`surname`/`addName` zusammengesetzt) muss in Personen-Profil (header), Quellen-Tabelle (Spalte Name) und Drill-Down-Tooltip auftauchen, mit identischem Wert." Tests prüfen das gegen den Build. Sicherer Schutz gegen UI-Inkonsistenz, würde die Memory-Regel „UI-Konsistenz" automatisiert sichern statt nur als Soll-Bestimmung.

Skizzen-Datei wäre `frontend/tests/test_data_coverage.py` mit einer Liste von Spec-Tupeln `(csv_feld, [(html_pfad, selector, transformation)])`.

## Aktueller Stand

| Säule | Tests | Status |
|---|---|---|
| Pytest | 516 | grün |
| Verifikations-Test-Set Stufe 1 (TEI zu JSON) | 27 checks | grün |
| Verifikations-Test-Set Stufe 2 (CSV zu HTML) | 25 checks | grün |
| Verifikations-Test-Set Stufe 3 (TEI zu HTML) | aktiv | wechselnd |
| JS-Tests | 3 Files | grün |
| Build-then-grep für IDs | offen | Task auf der Sofort-Liste |
| Datenfeld-Coverage | offen | eigener Meilenstein |
| Browser-Visual-Regression | offen | nicht geplant |
