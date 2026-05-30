# Verification — Verifikation der Frontend-Aggregate gegen TEI-Quelldaten

## Zweck

Jede aggregierte Zahl, die das Frontend anzeigt (Gesamtanzahl Personen, Rollenverteilung, Transaktionstyp-Histogramm etc.), muss maschinell gegen die TEI-Quelldaten verifizierbar sein. Dieses Verifikations-Set parst TEI-XML und Register-XML unabhängig von der Pipeline und vergleicht die eigenständig errechneten Aggregate mit den vom Build erzeugten JSON-Dateien unter `/data/`.

Zwei Anwendungsfälle:

1. **Datenrobustheit** — Pipeline-Fehler, falsche Aggregationen oder unvollständige Daten werden erkannt, bevor sie das Frontend erreichen.
2. **Provenienz-Grundlage** — das gleiche Parser- und Aggregator-Gerüst wird in Etappe 3 für die Quellen-Drill-Down-JSONs genutzt, die Frontend-Tooltips speisen.

Der Ordner heißt bewusst `verification/`, nicht `tests/`, um Kollisionen mit pytest-Konventionen zu vermeiden. Was hier läuft, ist kein Unit-Test-Paket, sondern ein Verifikations-Runner.

## Ausführung

Vom Edition-Repo-Root:

```
python -m verification.run              # TEI → JSON-Aggregate
python -m verification.run --html       # Pipeline-CSV → gerendertes HTML
python -m verification.run --tei-html   # TEI direkt → gerendertes HTML
python -m verification.run --research-questions  # Stufe 4: Forschungsfragen-Verifikation
python -m verification.run --all        # alle drei Pfade
python -m verification.run --inventory  # TEI-Element-Inventar pro Subkorpus
```

Neben den drei Pfaden existiert Stufe 4 (Forschungsfragen-Verifikation, `--research-questions`).

Verglichen wird gegen die **interne Fassung** (`docs-intern/`). Das Test-Set liest TEI im released-Scope (`is_released_corpus`), und nur der interne Build rendert genau diesen Umfang; der öffentliche Build (`docs/`) ist seit der Korpus-Trennung bewusst schmaler und würde Scope-Differenzen als Mismatch melden, die keine Drift sind. Vor dem Lauf muss die interne Fassung gebaut sein:

```
python -m frontend build --audience intern
```

Mit `VERIFICATION_DOCS_DIR=<verzeichnis>` lässt sich ein anderer Build erzwingen, z. B. `VERIFICATION_DOCS_DIR=docs` für den öffentlichen Build (dann erscheinen die schmaleren Korpus-Grenzen als erwartete Scope-Differenzen). Fehlt das Ziel-Verzeichnis, bricht der Runner mit einer Bauanweisung ab.

Exit-Code `0` solange nur `match`, `known_gap` oder `info` auftreten. Exit-Code `1` erst bei mindestens einem echten `mismatch`. Der Inventar-Modus liefert keine Vergleichs-Resultate und gibt immer Exit-Code 0.

Reports werden in `verification/reports/YYYY-MM-DD.md` (menschenlesbar) und `verification/reports/YYYY-MM-DD.json` (maschinenlesbar) geschrieben. Stufen-Suffixe: `-html` für CSV→HTML, `-tei-html` für TEI→HTML, `-all` für alle drei, `inventory-` für das Inventar, `research_questions-` für die Forschungsfragen-Verifikation. Die Reports sind Teil der Versionierung — Veränderungen im Verlauf sind per `git log verification/reports/` nachvollziehbar.

### Inventar-Modus

`python -m verification.run --inventory` scannt das aktive `sources/`-Verzeichnis und erzeugt pro Subkorpus eine Liste aller verwendeten TEI-Elemente mit Datei-Anzahl, Attributen und distinct Attribut-Werten. Output: `inventory-YYYY-MM-DD.md` (lesbar mit Querschnitts-Tabelle und Detail-Tabellen pro Subkorpus) plus `inventory-YYYY-MM-DD.json` (maschinenlesbar als Grundlage fuer kuenftige Coverage-Checks).

Zweck: sichtbar machen, welche Annotation in welchem Subkorpus wirklich vorliegt, bevor Frontend-Features oder Freigabe-Entscheidungen darauf aufbauen. Headline-Zahlen pro Korpus: rs gesamt, rs/event, rs/person, rs/org, rs/place, ref-Quote.

Per Default scannt der Modus das im Pipeline-Repo konfigurierte `sources/`-Verzeichnis. Fuer einen Ad-hoc-Lauf gegen ein anderes Repo-Clone laesst sich der Pfad ueberschreiben:

```
VERIFY_SOURCES_DIR=/pfad/zu/alternativem/sources python -m verification.run --inventory
```

## Drei Coverage-Stufen

Das Test-Set deckt drei Pfade ab, die zusammen die End-to-End-Verifikation ergeben:

1. **TEI → JSON** (`run` ohne Argument): unabhängige TEI-Aggregation vs. Pipeline-Output unter `docs-intern/data/*.json`. Findet Pipeline-Fehler in der Aggregations-Logik.
2. **CSV → HTML** (`run --html`): Pipeline-CSVs (Aggregator-Input) vs. gerenderte Profil- und Quellen-HTMLs unter `docs-intern/`. Findet Renderer-Drift, fehlende Felder im Template, Orphan-Annotationen.
3. **TEI → HTML** (`run --tei-html`): TEI-Quelldateien direkt vs. gerenderte Quellen-HTMLs. Ueberspringt die CSV-Pipeline und prueft End-to-End, ob jede `<rs ref="...">`-Annotation als `data-ref="..."` im HTML erscheint und umgekehrt. Findet sowohl Pipeline-Drops (TEI-Annotation, die der Aggregator entfernt hat) als auch Renderer-Halluzinationen (HTML-Refs ohne TEI-Quelle).

Die drei Stufen laufen unabhängig; einzelne Felder können in einer Stufe match sein und in der anderen mismatch.

## Statuswerte

| Status | Bedeutung |
|---|---|
| `match` | TEI und JSON stimmen überein. |
| `mismatch` | Echte Abweichung zwischen TEI-Re-Aggregation und JSON. Hinweis auf Pipeline-Fehler, falsches Label oder Datenproblem. |
| `known_gap` | Erklärter struktureller Unterschied, kein Fehler (z. B. Dokumente ohne TEI-Quelle, Typ-Normalisierung in der Pipeline). |
| `info` | Kontext-Kennzahl ohne direktes Pendant im JSON. |

## Scope

Das Verifikations-Set prüft end-to-end gegen **TEI-XML + Register-XML**, ohne die CSV-Zwischenstufen der Pipeline. Damit werden auch Fehler in der TEI-zu-CSV-Vorverarbeitung gefangen.

**Eingeschränkter Corpus:** Das Test-Set re-aggregiert TEI nur aus `QGW` und `Stadtbuecher` (`COLLECTIONS_WITH_TEI` in `config.py`). `Satzbuch_CD` ist seit 2026-05 freigegeben, liegt als TEI in `sources/` vor und ist Teil der internen Fassung, wird hier aber noch nicht gelesen: der Parser extrahiert SB_CD-Datumsangaben und Personennennungen noch nicht zuverlässig (abweichende Annotationsstruktur). Per-Korpus-Checks behandeln SB_CD deshalb als `known_gap` statt als Mismatch; die volle SB_CD-Abdeckung ist ein offener Folgepunkt. Weitere Korpora (Copeybuch_Zeibig, GenanntenListe_Weinzettel, Genanntenliste_Stubenviertel, Gewerbuch_D, Widmerliste) liegen nicht als released-TEI vor und erscheinen im Frontend nur als Regesten-Rendering.

## Struktur

```
verification/
  README.md           dieser Text
  inventory.md        Aggregat-Katalog: was getestet wird, woher die Erwartung stammt
  contract.py         Feld-Vertraege fuer die HTML-Coverage
  config.py           Pfade (TEI-Quellen, Register, JSON-Output), Konstanten
  inventory.py        Stufe Inventar: TEI-Element-Inventar pro Subkorpus
  research_questions.py  Stufe 4: Forschungsfragen-Verifikation
  provenance.py       Provenienz-Konsistenz-Checks innerhalb der JSON-Ausgaben
  parse_tei.py        TEI-Parser (lxml): Nennungen, Rollen, Events, Beziehungen
  parse_indices.py    Register-Loader (personList, orgList, placeList)
  parse_html.py       HTML-Reader (lxml.html): Profile, Quellen, data-ref
  aggregate.py        unabhängige Aggregations-Funktionen (Counter, Kreuztabellen)
  parse_json.py       Lesen der vorhandenen JSON-Outputs aus /data/
  compare.py          Stufe 1: TEI-Aggregat vs. JSON
  compare_html.py     Stufe 2: Pipeline-CSV vs. gerendertes HTML
  compare_tei_html.py Stufe 3: TEI direkt vs. gerendertes HTML
  report.py           Report-Generator (Markdown + JSON)
  run.py              Einstiegspunkt (python -m verification.run)
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

1. Eintrag in `verification/inventory.md` mit Name, erwarteter Quelle und Aggregations-Regel.
2. Entsprechende Funktion in `verification/aggregate.py`, Vergleichsfall in `verification/compare.py`.

Die Reihenfolge ist Breite-vor-Tiefe: erst Gesamtanzahlen abdecken, dann Kreuztabellen, dann Drill-Downs pro Zelle.
