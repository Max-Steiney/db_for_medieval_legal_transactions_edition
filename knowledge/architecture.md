---
title: Architektur
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.2
created: 2026-02-19
updated: 2026-05-16
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Static Site Architecture]]", "[[TEI]]"]
related: [data, specification, decisions, ui-design, journal]
---

# Architektur

Bausteine der Datenbank und ihr Zusammenspiel. Konzeptionell, ohne Implementierungsdetails.

## Datenfluss

Der Datenfluss ist einsträngig. TEI-XML-Quellen werden durch eine Python-Pipeline in JSON- und CSV-Zwischenformate transformiert. Jinja2-Templates rendern daraus statische HTML-Dateien. Die fertigen Seiten werden über GitHub Pages ausgeliefert.

Jede Stufe ist für sich nachvollziehbar. Wer eine Aussage der Oberfläche anzweifelt, kann sie bis in die TEI-Quelle zurückverfolgen.

## TEI als Quelle

Die Quelldaten liegen in TEI-XML vor, dem etablierten Standard für die digitale Erschließung historischer Texte. Die Wahl ist nicht konjunkturell, sondern langfristig gedacht. TEI dokumentiert Text und Annotation in einem einzigen Dokument und bleibt auch nach dem Ende dieser Datenbank lesbar.

Die Annotationsebenen sind in [[data#Annotationsebenen]] beschrieben.

## Pipeline

Die Python-Pipeline leistet Validierung, Transformation und Aggregation. Sie prüft die Quellen gegen ein RelaxNG-Schema, normalisiert Attribute, parst Datumsangaben und erzeugt die Zwischenformate für das Rendering.

Die Wahl von Python mit lxml folgt aus zwei Gründen. Die Werkzeugkette kommt ohne Java-Abhängigkeiten aus. Und Regressionstests sind in Python leichter zu schreiben und zu pflegen als in klassischen XSLT-Pipelines.

## Datenschichten und Aggregator

Zwischen TEI-Quellen und Frontend-Views liegen drei aufeinander aufbauende Schichten. Die unterste Schicht sind die Pipeline-CSVs (Schwester-Repo), die die TEI-Auszeichnung in tabellarische Form bringen. Darüber schreibt der Aggregator im Edition-Repo (Paket `frontend/aggregator/`) konsolidierte JSON-Dateien nach `docs/data/` und rendert serverseitig die Profilseiten unter `docs/register/persons/` und `docs/register/orgs/`. Die oberste Schicht sind die View-spezifischen JSONs, die das Frontend zur Renderzeit zusammenstellt.

Der Aggregator ist die Stelle, an der Frontend-spezifische Schnitte entstehen, die nicht in die Pipeline gehören. Submodule mit klarer fachlicher Verantwortung: `docs` für den Pro-Quelle-Record und den Forward-Index `docs_entities.json`; `roles`, `relations`, `transactions` für die thematischen Aggregat-JSONs; `timeline` für das Quellen-Zeitraster; `person_profiles` und `org_profiles` für die Entitäts-Profilseiten.

Der Vorteil dieser Trennung ist Wiederverwendbarkeit. Mehrere Frontend-Views (Tabelle, Detail, Profile, Auswertungen, Exploration) lesen denselben Aggregat-Datensatz, statt jede ihre eigene TEI-Logik mitzuführen. Begründung und Reihenfolge der Joins sind in [[data#Aggregat-Schicht]] festgehalten.

Eine TEI-Änderung wirkt erst, wenn alle drei Schichten neu laufen: erst Pipeline (`python -m pipeline transform` im Schwester-Repo), dann Aggregator + Build (`python -m frontend build` hier).

## Stufenmodell als Build-Profil

Der Frontend-Build kennt vier benannte Stufen, die Korpus-Auswahl und Annotationsebenen als zitierbares Profil bündeln (`frontend/stages.py`). CLI-Auslöser ist `--stage N` (1 bis 4); `--include-mentioned` bleibt als Alias auf Stufe 2 erhalten. Jede Stufe schreibt in ein eigenes Output-Verzeichnis (`docs/`, `docs-with-mentioned/`, `docs-full/`, `docs-max/`) und setzt davon abgeleitete Env-Vars für die Pipeline-Transformer. Konzept und vollständige Tabelle in [[specification#Stufenmodell für Korpus-Auswahl und Annotationsebenen]]; Mapping auf den Datenbestand in [[data#Stufenmodell für Korpus-Auswahl]].

## Test-Strategie

Die Qualitätssicherung steht auf drei Säulen, die unterschiedliche Fehlerklassen abdecken und sich nicht ersetzen.

**Pytest** (`frontend/tests/`) testet den Build-Code selbst: Aggregator-Funktionen, Renderer, Template-Rendering, JS-Infrastruktur. Die Suite läuft schnell (rund elf Sekunden) und gehört zu jedem Build (`python -m pytest frontend/tests/`). Sie fängt Regressionen in der Programmlogik, nicht in den Daten.

**Verifikations-Test-Set** (`verification/`) prüft die Daten-Konsistenz End-to-End: TEI-Quellen und Register-XMLs werden ohne Umweg über die Pipeline-Zwischenformate eingelesen, Aggregate eigenständig nachgerechnet und mit den vom Build erzeugten JSON-Dateien und gerenderten HTMLs verglichen. Drei Coverage-Stufen:

1. **TEI zu JSON** (`python -m verification.run`): unabhängige TEI-Aggregation vs. Pipeline-Output unter `docs/data/*.json`. Findet Pipeline-Fehler in der Aggregations-Logik.
2. **CSV zu HTML** (`python -m verification.run --html`): Pipeline-CSVs vs. gerenderte Profil- und Quellen-HTMLs. Findet Renderer-Drift, fehlende Felder im Template, Orphan-Annotationen.
3. **TEI zu HTML** (`python -m verification.run --tei-html`): TEI-Quelldateien direkt vs. gerenderte Quellen-HTMLs. Überspringt die CSV-Pipeline-Zwischenstufe und prüft, ob jede `<rs ref="...">`-Annotation als `data-ref="..."` im HTML erscheint und umgekehrt. Findet sowohl Pipeline-Drops (TEI-Annotation, die der Aggregator entfernt hat) als auch Renderer-Halluzinationen (HTML-Refs ohne TEI-Quelle).
4. **TEI-Inventar** (`python -m verification.run --inventory`): pro Subkorpus eine Liste aller verwendeten TEI-Elemente mit Datei-Anzahl, Attributen und distinct Attribut-Werten. Kein Vergleich, sondern Sichtbarkeit der Annotations-Realität — Grundlage für Freigabe-Entscheidungen und Forschungsfragen, die auf bestimmte Annotation angewiesen sind.

Das Test-Set nutzt dieselbe Technologie wie die Pipeline (Python, lxml), ist aber bewusst ein separater Codepfad ohne geteilte Aggregations-Funktionen. Die Trennung ist die Verifikationsgarantie: Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht. Reports sind versioniert in `verification/reports/` (Markdown + JSON). Statuswerte und Befund-Register: `verification/README.md` und `verification/findings.md`. Begründung in [[specification#Verifizierbarkeit und Verifikations-Test-Set]].

**Manuelle Sichtprüfung** deckt ab, was sich nicht automatisieren lässt: Layout, Tooltip-Positionierung, Druckansicht, Lesefluss. Sie ist Teil jeder größeren UI-Änderung, nicht der CI.

Die Säulen sind komplementär. Pytest fängt Code-Regressionen, Verifikation fängt Daten- und Rendering-Drift, Sichtprüfung fängt visuelle Brüche. Eine Änderung an Daten oder Templates wird typischerweise von zwei der drei Säulen gesehen.

## Templates

Die Oberfläche ist durch Jinja2-Templates definiert. Ein Basis-Template hält Navigation und Fußzeile zentral. Detail-Templates erweitern es um den jeweiligen Inhalt. Eine Änderung am Rahmen greift in allen Seiten, eine Änderung an einer Detailseite bleibt lokal.

## Statische HTML-Ausgabe und Prototyp-Charakter

Die Datenbank ist als statische Website ausgeliefert; GitHub Pages serviert vorberechnete HTML-Dateien ohne Server-Logik. Dynamische Funktionen (Filter, Suche, Umschalter) laufen im Browser gegen JSON-Indexe. Der Vorteil ist doppelt: die Infrastruktur ist einfach, und einzelne Seiten sind zitierbar, weil ihre URLs stabil bleiben. Sehr große oder stark wechselnde Daten verlangen besondere Indexierungsstrategien auf Client-Seite.

Templates und Build-Code liegen getrennt vom erzeugten Output. Inhaltliche Änderungen gehören in die Quelle, der Output wird durch einen Build-Lauf erneuert. HTML-Dateien werden nicht direkt editiert, ausgenommen Meta-Dateien wie `CLAUDE.md` und die Wissensbasis im `knowledge/`-Ordner.

Die Architektur ist ein Prototyp, kein produktionsreifes System. Entscheidungen wie „keine Datenbank, keine Auth, keine serverseitige Logik" sind bewusst getroffen — sie tauschen Echtzeit-Daten, persistierte Nutzereingaben und Authentifizierung gegen Einfachheit und Zitierbarkeit. Das ist akzeptabel, weil die Datenbank Publikationsform ist, kein kollaboratives Werkzeug.

## Provenienz-Indizes

Jede aggregierte Kennzahl ist auf die zugrundeliegenden Quelldokumente rückführbar: ein `drill_down`-Abschnitt innerhalb jeder Aggregat-JSON führt zu jedem Kreuztabellen-Feld die sortierte Liste der beitragenden `file_key`-Verweise. Metadaten zum Einzeldokument kommen aus `data/docs_lookup.json`. Begründung in [[specification#Provenienz als inline Drill-down in den Aggregat-JSONs]], UI-Ausprägung in [[ui-design#Tip-System]].

`docs_lookup.json` ist die einzige Stelle, an der ein `file_key` (`f__QGW_1551`) in die tatsächliche Quellen-URL, das anzuzeigende Idno, das normalisierte Datum, das Korpus-Label und den Kurzregest aufgelöst wird. Die Pfad-Struktur unter `documents/` (`<korpus>/<subkorpus>/<idno>.html`) ist nicht aus dem `file_key` ableitbar — sie hängt am Korpus-Pfad in `filenames.csv`. Jedes Frontend-Modul, das einen Quellen-Link, einen Datenkorb-Eintrag oder eine CSV-Spalte „Quelle" baut, geht über `docs_lookup`. Eine naive Konstruktion `documents/<file_key>.html` produziert deterministisch 404 für jede QGW- und Stadtbücher-Quelle und ist als Bug zu behandeln. Der gemeinsame Helper in `viz-core.js` lädt den Lookup einmal pro Seite; page-spezifische Resolver (etwa `analysis-resolver.js`) hängen sich daran an.

## Quellenbereinigte Aggregation als Invariante

Das Zählen von Entitäten pro Quelle erfolgt mengenbasiert: die Extraktionsfunktion im Build liefert pro Quelldokument eine Menge referenzierter Entity-IDs, nicht eine Liste mit möglichen Duplikaten. Eine Person, Organisation oder ein Ort wird pro Quelle höchstens einmal gezählt. Begründung in [[specification#Quellenbereinigte Zählung]], begriffliche Konsequenz in [[glossar#Gesamtnennung]].

## Datenstand aus dem Pipeline-Repo

Die Fußzeile führt einen **Datenstand**, der auf den letzten Commit des Pipeline-Repos verweist. Technisch ermittelt der Build das Commit-Datum per `git log -1 --format=%cI` im Pipeline-Repo-Root und formatiert es in lesbarer deutscher Langform. Der Datenstand ist damit nicht das Tagesdatum des Build-Laufs, sondern der Stand der Quellen, auf denen der Build beruht.

Getrennt davon bleibt das **Build-Datum** als Zeitstempel pro gerenderter Seite. Es markiert, wann die Einzelseite zuletzt neu gebaut wurde. Beide Angaben werden lesbar, nicht als ISO-Zeichenkette ausgegeben. Siehe [[ui-design#Datenstand und Build-Datum]].

## Geteilte Visualisierungs-Schicht

Die Daten-Visualisierungs-Seiten unter `/analysis/` und `/exploration/` teilen eine gemeinsame Infrastruktur, statt jede ihre eigene. Diese Schicht (`viz-core`) bündelt drei Klassen von Bausteinen: erstens die geteilten Domain-Konstanten (Rollen-, Beziehungs-, Geschlechter-Labels und ihre Farben), zweitens die geteilten Helfer (Zahlen-Formatierung, Dekaden-Filter als Closure über einen Page-State, CSP-sichere Style-Projektion über `data-*`-Attribute, Chip-Toggle), drittens die geteilten Sidebar-Bindings (Range-Slider, Reset, Active-Filter-Strip, URL-State-Sync, Drill-down-Overlay, JSON-Loader inklusive `docs_lookup` für Provenienz-Auflösung).

Eine Seite wird damit zu einem dünnen Orchestrator: sie definiert ihren eigenen State, schreibt ihre page-spezifischen Aggregations- und Renderer-Funktionen, und ruft in `DOMContentLoaded` die `viz-core`-Bindings. Eine neue visuelle Sub-Seite (Personen-Netzwerk, Karten, Sankey) muss das Filter-Boilerplate nicht wiederholen.

Begründung dieser Trennung ist dieselbe wie die zwischen Pipeline und Aggregator: Wiederverwendbarkeit und ein einziger Ort für jede Konvention. Eine Änderung am Active-Filter-Strip oder an der CSP-Style-Projektion greift in allen Visualisierungen gleichzeitig.

## URL-State als Forschungsstand

Auf den Daten-Visualisierungs-Seiten wird der Filter-Stand in die URL-Suchparameter serialisiert und beim Page-Load von dort gelesen. Damit wird ein Forschungsstand bookmark-fähig, teilbar und zitierbar (vgl. [[user-stories#Quellen, Personen und Organisationen sammeln, teilen und exportieren]]).

Die Schreib-Strategie nutzt `history.replaceState`, nicht `pushState` — Filter-Mikrostände sollen nicht den Browser-Back-Stack füllen. Default-Werte werden weggelassen, damit Sharing-URLs minimal bleiben. Während des Page-Inits ist die URL-Sync deaktiviert (Guard `urlSyncActive`), damit ein initiales Apply nicht den eingehenden Filter überschreibt.

Cross-Page-Sprünge transferieren das gemeinsame Subset der Filter (Zeitraum, Geschlecht) in andere Listenseiten. Das Mapping ist asymmetrisch, weil die Filter-Vokabulare nicht symmetrisch sind; Konvention und konkretes Mapping in [[specification#Cross-Page-Sprung mit Filter-Übernahme]]. Page-spezifische Filter werden nicht übertragen, die Lückenführung ist im Tooltip am Cross-Nav-Link sichtbar.

## Datenkorb als clientseitige Persistenz

Der Datenkorb persistiert in `localStorage` mit versioniertem Schlüssel, Cross-Tab-Sync läuft über das `storage`-Event und ein internes Custom-Event für In-Tab-Updates. Einträge tragen einen zusammengesetzten Schlüssel `type:id` mit den Typen `source`, `person`, `org`, ein `gathered`-Flag und eine `src`-Liste der Quellen-IDs, aus denen ein Eintrag abgeleitet wurde. Die Ableitung lädt beim ersten Bedarf den Forward-Index `docs_entities.json` (Quelle → annotierte Entity-IDs) aus `docs/data/`.

Komponenten-Verteilung: `basket.js` liefert die State-API und den Ableitungs-Mechanismus, in `base.html` global geladen. `basket-mount.js` hydratisiert eingebettete +-Knopf-Platzhalter auf Detail- und Profilseiten aus ihren `data-basket-*`-Attributen. `basket-page.js` rendert die Korb-Seite.

UI-seitige Mechanik und Sichtbarkeit in [[ui-design#Datenkorb]], Begründung in [[specification#Datenkorb als clientseitige Sammlung]].

## Siehe auch

- [[data]] was verarbeitet wird
- [[specification]] welche User-Stories die Architektur einlöst
- [[ui-design]] wie die Bausteine zur Oberfläche werden
