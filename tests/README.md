# Test-Set — Verifikation der Frontend-Aggregate gegen TEI-Quelldaten

## Zweck

Jede aggregierte Zahl, die das Frontend anzeigt (Gesamtanzahl Personen, Rollenverteilung, Transaktionstyp-Histogramm etc.), muss maschinell gegen die TEI-Quelldaten verifizierbar sein. Dieses Test-Set parst TEI-XML und Register-XML unabhängig von der Pipeline und vergleicht die eigenständig errechneten Aggregate mit den vom Build erzeugten JSON-Dateien unter `/data/`.

Zwei Anwendungsfälle:

1. **Datenrobustheit** — Pipeline-Fehler, falsche Aggregationen oder unvollständige Daten werden erkannt, bevor sie das Frontend erreichen.
2. **Provenienz-Grundlage** — das gleiche Parser- und Aggregator-Gerüst wird in Etappe 3 für die Quellen-Drill-Down-JSONs genutzt, die Frontend-Tooltips speisen.

## Ausführung

Vom Edition-Repo-Root:

```
python -m tests.run
```

Exit-Code `0` bei vollständigem Match, `1` bei mindestens einem Mismatch.

Reports werden in `tests/reports/YYYY-MM-DD.md` (menschenlesbar) und `tests/reports/YYYY-MM-DD.json` (maschinenlesbar) geschrieben. Die Reports sind Teil der Versionierung — Veränderungen im Verlauf sind per `git log tests/reports/` nachvollziehbar.

## Scope

Das Test-Set verifiziert end-to-end gegen **TEI-XML + Register-XML**, ohne die CSV-Zwischenstufen der Pipeline. Damit werden auch Fehler in der TEI-zu-CSV-Vorverarbeitung gefangen.

**Eingeschränkter Corpus:** TEI-Quellen liegen nur für `QGW` und `Stadtbuecher` vor. Andere Quellenkorpora (Copeybuch_Zeibig, GenanntenListe_Weinzettel, Genanntenliste_Stubenviertel, Gewerbuch_D, Satzbuch_CD, Widmerliste) erscheinen aktuell im Frontend als Regesten-Rendering, liegen aber nicht in `sources/` und werden von den Aggregaten in `data/*.json` derzeit nicht berücksichtigt. Sobald für diese Korpora TEI bereitgestellt wird, erweitert sich der Test-Set-Scope automatisch.

## Struktur

```
tests/
  README.md           dieser Text
  inventory.md        Aggregat-Katalog: was getestet wird, woher die Erwartung stammt
  config.py           Pfade (TEI-Quellen, Register, JSON-Output), Konstanten
  parse_tei.py        TEI-Parser (lxml): Nennungen, Rollen, Events, Beziehungen
  parse_indices.py    Register-Loader (personList, orgList, placeList)
  aggregate.py        unabhängige Aggregations-Funktionen (Counter, Kreuztabellen)
  parse_json.py       Lesen der vorhandenen JSON-Outputs aus /data/
  compare.py          Vergleich Test-Aggregate vs. JSON, Diff-Erzeugung
  report.py           Report-Generator (Markdown + JSON)
  run.py              Einstiegspunkt (python -m tests.run)
  reports/            historische Reports, committed
```

## Abhängigkeiten

- `lxml` — TEI-XML-Parsing.
- Python-Standardbibliothek für alles andere.

Installation, falls `lxml` fehlt:

```
pip install lxml
```

## Erweiterung

Neue Aggregate werden in zwei Schritten aufgenommen:

1. Eintrag in `tests/inventory.md` mit Name, erwarteter Quelle und Aggregations-Regel.
2. Entsprechende Funktion in `tests/aggregate.py`, Vergleichsfall in `tests/compare.py`.

Die Reihenfolge ist Breite-vor-Tiefe: erst Gesamtanzahlen abdecken, dann Kreuztabellen, dann Drill-Downs pro Zelle.
