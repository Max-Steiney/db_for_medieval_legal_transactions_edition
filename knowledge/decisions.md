---
title: Entscheidungen
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
topics: ["[[Decision Records]]", "[[Architecture Decision Records]]"]
related: [specification, architecture, ui-design, analyse, exploration]
---

# Entscheidungen

Getroffene Leitentscheidungen mit Begründung. Zeitlos formuliert. Pro Eintrag Entscheidung, Begründung und Konsequenz, optional eine Abgrenzung, was ausdrücklich nicht gemeint ist.

## Forschungsstand zitierbar via URL-Parameter

**Entscheidung.** Auf den Daten-Visualisierungs-Seiten wird der Filter-Stand in URL-Suchparameter serialisiert und bei Page-Load wieder eingelesen. Quellen- und Personen-Listenseiten haben das Pattern bereits.

**Begründung.** Eine Forscherin will einen Filter-Stand bookmarken, in eine Mail kopieren oder in einer Publikation zitieren. Ohne URL-Sync ist der Filter beim Reload weg.

**Konsequenz.** Mechanik (Schreib-Strategie, weggelassene Defaults, Init-Guard, Cross-Page-Sprung) in [[architecture#URL-State als Forschungsstand]].

## Cross-Page-Sprung mit Filter-Übernahme

**Entscheidung.** Drill-down-Overlays (Auswertungen) und Brush-Drill (Zeitstrom) bieten einen „→ in Quellen-Liste öffnen"-Link. Der Link transferiert Zeitraum + Geschlechter-Filter (mappt auf das Quellen-Filter-Vokabular) in die Quellen-Listenseite. Page-spezifische Filter (Rolle, Beziehungstyp, Bezeichnung, Transaktionstyp, Stack-Fokus) werden nicht übertragen, weil die Quellen-Liste sie nicht kennt.

**Begründung.** Die Visualisierung weckt das Interesse, die strukturierte Quellen-Liste vertieft. Beide Seiten teilen sich Zeitraum und Geschlechter-Achse — die Übernahme ist verlustfrei für diese, ehrlich-lückenhaft für die anderen.

**Konsequenz.** `VizCore.buildDocumentsURL({decadeMin, decadeMax, sex})` baut die Cross-Nav-URL. Mapping ist asymmetrisch: `sex='f' → with-f`, `sex='m' → only-m` (Quellen kennt kein `with-m`).

## Datenkorb als clientseitige Sammlung

**Entscheidung.** Forschende sammeln Quellen, Personen und Organisationen über Sitzungen hinweg in einem clientseitigen Datenkorb. Daten bleiben rein clientseitig, keine Server-Persistenz, keine Identitätspflicht.

**Begründung.** Forschungspfade springen häufig zwischen Übersicht, Aggregat, Quelle, Person, Organisation. Eine sammelnde Schicht über mehrere Seiten und Item-Typen erlaubt es, ein Forschungs-Korpus zusammenzustellen, ohne Browser-Tab-Wildwuchs oder manuelle Bookmark-Strategie. Eine Account-basierte Persistenz wäre ein anderer Stack mit Auth, DSGVO-Implikationen und laufenden Speicherkosten — ohne erkennbaren Mehrwert für die jetzt bedienten Forschungsszenarien.

**Konsequenz.** UI-Mechanik (Sammeln, Ableiten, Promotion, drei Tabellen, CSV-Export) in [[ui-design#Datenkorb]], technische Persistenz und Komponenten-Verteilung in [[architecture#Datenkorb als clientseitige Persistenz]]. Der Bridge-Pfad in externe Werkzeuge (Zotero, BibTeX-Konverter, Excel) läuft über CSV-Export.

## Personen- und Organisationsprofile als Detailseiten

**Entscheidung.** Jede individuelle Person und jede individuelle Organisation mit Nennung in einer freigegebenen Quelle erhält eine eigene Detail-Profilseite. `<rs type="person">` und `<rs type="org">` im Quellen-Volltext verlinken direkt auf das Profil.

**Begründung.** Personennamen und Organisationsbezeichnungen waren ohne Profilseiten Sackgassen — klickbar, aber nur als Hash-Anker in die Register-Liste, wo der Anker im JS-gerenderten Index nicht ankam. Beziehungs-Daten (Verwandtschaft, Freundschaft, Vertretung, Beruf, Titelverweis) lagen vollständig in den Pipeline-CSVs vor, waren UI-seitig aber unsichtbar; ein im TEI kodiertes Ehepaar blieb für die Forscherin im Frontend nicht einsehbar. Die Profile schließen diese Lücke und machen die TEI-Annotation auf Entitäts-Ebene navigierbar.

**Konsequenz.** Aggregator-Module `person_profiles` und `org_profiles` rendern Profile direkt zu HTML. Layout und Bidirektionalität der Beziehungs-Auflösung sind in [[ui-design#Entitäts-Profilseite]] und [[data#Register]] beschrieben.

**Nicht gemeint ist**, dass jedes Profil eine vollständige Biografie liefert. Die Profile zeigen, was die TEI-Annotation hergibt.

## Analyse-Seite mit Frage-Galerie und Custom-Builder

**Entscheidung.** Die Abfragen-Sub-Seite (`/analysis/index.html`) bedient zwei Einstiegsmodi nebeneinander: eine kuratierte Galerie konkreter Forschungsfragen als oberste Ebene, ein freier Custom-Builder darunter im aufklappbaren `<details>`. Die Frage ist first-class concept und autonom (`{id, group, text, dataFiles, viz, answer, resolveViz, resolveComparison, resolveDrillDown, coverage}`), nicht an eine Familie gebunden.

**Begründung.** Die frühere Slot-Workbench mit Template-Familien als oberster Mental-Model-Ebene zwang Nutzerinnen, sich erst durch eine Familien-Tab-Bar zu navigieren, bevor sie ihre Frage formulieren konnten. Forscherinnen kommen aber mit der Frage selbst, nicht mit einer Familien-Kategorie. Die Galerie bietet direkten Zugriff über den Frage-Text; der Custom-Builder bleibt für die freie Kombination von Slots verfügbar, ist aber nicht der Default-Einstieg.

**Konsequenz.** Galerie-Karten tragen subtile Mini-Visualisierungen; das Result-Panel zeigt vollwertige SVG-Renderings. Beide Stufen teilen sich die Renderer-Logik. Permalinks doppelt: `#q=<id>` für die Galerie, `#f=<fid>&...` für den Custom-Builder. JS-seitig getrennt in `analysis-composer.js` (UI), `analysis-capabilities.js` (Capability-Manifest) und `analysis.js` (Driver).

**Nicht gemeint ist**, dass die Galerie statisch fest steht. Frage-Resolver lassen sich ergänzen, ohne die Architektur zu ändern; einige Resolver sind als Galerie-Antwort fertig, aber noch nicht als Slot-Kombination im Custom-Builder ausgebaut.

## Titel und Untertitel

**Entscheidung.** Der Haupttitel der Datenbank lautet „Stadt und Gemeinschaft Wien", der Untertitel „Datenbank zu mittelalterlichen Rechtsgeschäften".

**Begründung.** Der Haupttitel ist in den Projektpublikationen etabliert. Eine abweichende Neubenennung würde Kontinuität mit bereits gedruckten Texten brechen. Der Untertitel ist deutsch, damit das UI sprachlich durchgängig bleibt und nicht ohne Anlass zwischen Deutsch und Englisch wechselt.

**Konsequenz.** Der Titel ist in Navigationsleiste, Seitentitel und Fußzeile konsistent zu führen.

## Exploration und Analyse als getrennte Bereiche

**Entscheidung.** Das UI führt zwei Navigationsbereiche nebeneinander: Analyse und Exploration. Die Trennung folgt dem Interaktionsmodus, nicht dem Inhalt.

- **Analyse** versammelt quantitative Auswertungen mit vorgegebener Achsensemantik: Verteilungen (Donut, Bar-Chart, Tabellen mit Prozentwerten) und Template-Abfragen mit typisierten Slots. Nutzerinnen kommen mit einer Frage und bekommen Zahlen plus Provenienz.
- **Exploration** ist visuell-interaktive Erkundung der Datenstruktur selbst: Personen-Netzwerke, Karten, Timeline-Bänder, Sankey-Diagramme. Nutzerinnen kommen ohne klare Frage und entdecken Pattern in der Visualisierung.

**Begründung.** Donut, Bar-Chart und Verteilungstabellen sind nach DH-Standard analytische Visualisierung — sie zeigen vorberechnete Statistik. Force-Layouts, Karten und Sankey-Diagramme sind Information-Visualisation für offene Erkundung. Die Erwartungshaltung der Nutzerinnen unterscheidet sich entsprechend: „Auswertung" suggeriert quantitative Antwort, „Exploration" visuelles Stöbern. Die Pfade folgen dieser Semantik.

**Konsequenz.** Unter `/analysis/` liegen `auswertungen.html` (Statistik-Verteilungen) und `index.html` (Abfragen). Unter `/exploration/` liegen `zeitstrom.html` (gestapelter Bar-Chart mit Brush-zu-Drill-down) und `personennetzwerk.html` (Ego-Layout mit Klick-Hopping); ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert, aber noch nicht umgesetzt. Die Navigation bündelt beide Bereiche in eigenen Dropdowns. Siehe [[ui-design#Navigation]] und [[ui-design#Zwei Modi nebeneinander]].

**Nicht gemeint ist**, dass Exploration und Analyse streng disjunkt wären. Eine Nutzerin kann eine Auffälligkeit in einem Donut-Diagramm entdecken (Analyse) und sie in einer Netzwerkvisualisierung qualitativ weiterverfolgen (Exploration), oder umgekehrt. Die Bereiche teilen sich dieselben Aggregate (`roles.json`/`relations.json`/`transactions.json`) und dieselben Filter-Bausteine (Sidebar, Active-Filter-Strip).

## Auswertungen gehört in den Analyse-Bereich

**Entscheidung.** Die Auswertungen-Seite (vier Sektionen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen, jeweils als Donut, Bar-Chart oder Tabelle) liegt unter `/analysis/auswertungen.html` und nicht unter `/exploration/`.

**Begründung.** Die Seite zeigt vorberechnete statistische Verteilungen mit Prozentwerten und exakten Zahlen. Die Interaktion beschränkt sich auf zwei orthogonale Achsen (Zeitraum, Geschlecht) plus eine Zähleinheit-Umschaltung (Nennungen ↔ Individuelle Personen) — alles strukturierte Auswertungsachsen, keine offene Erkundung. Donut und Bar-Chart sind klassische Statistik-Displays, keine explorativen Visualisierungen. Wer auf den Eintrag „Auswertungen" klickt, erwartet quantitative Antworten; das ist Analyse-Domain.

**Konsequenz.** Build-Ziel: `docs/analysis/auswertungen.html`. Template: `frontend/templates/analysis_aggregat.html`. JavaScript: `frontend/static/js/analysis-aggregat.js`. Aggregator-Source: `frontend/aggregator/roles.py`, `relations.py`, `transactions.py`. Die Navigation führt sie als Dropdown-Eintrag unter „Analyse", neben „Abfragen" (`/analysis/index.html`).

**Vorgeschichte.** Frühere Iterationen hatten vier separate Sub-Seiten unter `/exploration/` (Rollen, Beziehungen, Transaktionen, Orte), wurden zu einer zusammengelegten `exploration/auswertungen.html`-Seite gebündelt und schließlich nach `/analysis/` verschoben, sobald klar war, dass die Inhalte analytischer als explorativer Natur sind. Die Verschiebung dokumentiert sich in [[journal]].

**Nicht gemeint ist**, dass die Seite niemals interaktive Exploration enthielte. Filter ziehen, Pattern entdecken — das geht hier auch. Aber das primäre Interaktionsmuster ist Verteilungs-Display, nicht visuelle Strukturerkundung.

## Begriff Gesamtnennungen

**Entscheidung.** Die Zählebene aller Erwähnungen heißt im UI „Gesamtnennungen", nicht „Nennungen". Die Zählebene der konsolidierten Register-Einträge heißt „Individuelle Personen", „Individuelle Organisationen", „Individuelle Orte".

**Begründung.** Das Präfix schafft eine explizite Abgrenzung zur [[glossar#Individuelle Person]] und reduziert die Verwechslungsgefahr in publikationsrelevanten Zahlen. Die Kurzform „Nennungen" war zu nahe an der alltagssprachlichen Verwendung und lud zu Fehlinterpretationen ein.

**Konsequenz.** Alle UI-Labels, Filter- und Achsenbeschriftungen verwenden „Gesamtnennungen" oder „Individuelle Personen". Siehe [[glossar#Gesamtnennung]]. Welche der beiden Zählebenen einer konkreten Zahl zugrunde liegt, soll am Provenienz-Tooltip erkennbar sein, siehe [[ui-design#Tip-System]]. Ein Label, das eine Zahl fälschlich der anderen Zählebene zuordnet, ist ein Fehler im Sinne von [[specification#Datenrobustheit und Provenienz]] und wird vom Verifikations-Test-Set sichtbar gemacht, siehe [[architecture#Test-Strategie]].

## Quellenbereinigte Zählung

**Entscheidung.** Gesamtnennungen werden quellenbereinigt gezählt: eine Person, Organisation oder ein Ort, die oder der in derselben Quelle mehrfach erwähnt wird, trägt für diese Quelle genau eine Gesamtnennung bei.

**Begründung.** Urteilslisten, Zeugenreihen und Formularwiederholungen führen dazu, dass ein und dieselbe Person innerhalb einer Urkunde zwanzigmal namentlich auftaucht. Eine Zählung pro Einzelerwähnung würde solche Formelpartien gegenüber substanziellen Einzelnennungen überproportional gewichten und Vergleiche zwischen Regesten (wenige Nennungen pro Quelle) und edierten Volltexten (viele Nennungen pro Quelle) systematisch verzerren. Die quellenbereinigte Zählung beantwortet die Forschungsfrage „in wie vielen Quellen ist Person X belegt" präzise und ist robust gegen das Erschließungsformat.

**Konsequenz.** Die Definition in [[glossar#Gesamtnennung]] ist entsprechend formuliert. Der [[ui-design#Provenienz-Tip und Glossar-Tip]] benennt diese Zählebene an jeder betroffenen Zahl explizit. Eine Umschaltung auf ungereinigte Einzelerwähnungen ist nicht vorgesehen; sie wäre statistisch missverständlich und fachlich schwer interpretierbar.

**Nicht gemeint ist**, dass das Datenmodell die Information über Mehrfachnennungen verliert. Die TEI-Quellen markieren jede Erwähnung einzeln. Die Dedupizierung greift erst in der Aggregation.

## Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events

**Entscheidung.** Eine Personen-Nennung wird im Frontend nur dann gezählt, wenn die Person im TEI-Quellentext als `<rs type="person">` mit `@ref` auf einen `pe__`-Schlüssel annotiert ist und sich nicht innerhalb eines verschachtelten `<rs type="event">` (mentioned Event) befindet. Korrespondierende Hilfsverknüpfungen (`@corresp` ohne `@type="person"`) werden ebenfalls ausgeschlossen.

**Begründung.** Das TEI-Datenmodell verwendet zwei Mechanismen, die nicht zu Nennungen zählen sollten:

1. `@corresp` ist eine administrative Verknüpfung, die typischerweise eine Beziehung kodiert (etwa eine Verwandtschaftsangabe in einer Hilfsmarkierung), ohne dass der Personenname an der Stelle im Text steht.
2. Personen-Annotationen innerhalb eines verschachtelten `<rs type="event">` referenzieren ein älteres, anderwärts erfasstes Geschäft. Sie sind Querverweise, keine Akteurinnen oder Akteure des aktuellen Quellenereignisses.

Wer Nennungen für Häufigkeitsstatistiken oder Belegdichten zählt, will explizit Quellentext-Erwähnungen aktueller Geschäfte — nicht Hilfsverknüpfungen oder Querverweise. Eine inklusive Zählung erzeugt Diskrepanzen zu publizierten Statistiken und verzerrt die Häufigkeitsbilder einzelner Personen.

**Konsequenz.** Der maßgebliche XPath ist:

```
//tei:body//tei:*[@type='person']
  [not(ancestor::tei:rs[@type='event']
       [ancestor::tei:rs[@type='event']])]
```

`frontend/build.py::_scan_released_tei` wertet diesen XPath direkt gegen die freigegebenen TEI-Quellen aus. CSV-Outputs der Pipeline werden für KPIs nicht mehr verwendet, sodass keine zwischenzeitliche Datentransformation die Definition ändern kann.

**Nicht gemeint ist**, dass `@corresp`-Verknüpfungen oder mentioned Events aus dem Datenmodell entfernt werden. Sie bleiben in den TEI-Quellen und in den CSV-Outputs der Pipeline für Beziehungsanalysen und Querverweise verfügbar. Die Filterung greift ausschließlich bei der Frontend-Anzeige.

## Asymmetrische Zählung: individuelle Personen vs. Nennungen

**Entscheidung.** Die Distinct-Zählung der individuellen Personen schließt Personen-Annotationen innerhalb mentioned Events **ein**; die Zählung der Nennungen schließt sie **aus**.

**Begründung.** Beide Zählebenen beantworten verschiedene Fragen. „Wie viele unterscheidbare historische Personen umfasst das publizierte Korpus?" — diese Frage zielt auf das Personenregister; eine Person ist *bekannt*, sobald sie in einer freigegebenen Quelle in irgendeiner Annotation auftritt, auch als Querverweis in einem mentioned Event. „Wie häufig wird Person X in den freigegebenen Quellentexten erwähnt?" — diese Frage zielt auf die Belegdichte als Akteurin; nur direkte Quellentext-Erwähnungen aktueller Geschäfte zählen, mentioned Events sind für diese Frage Querverweise auf andere Quellen und gehören nicht in den Zähler.

Die Asymmetrie ist semantisch konsistent: Eine Person, die nur als Querverweis in einer einzigen Quelle erscheint, ist trotzdem im Register vermerkt (und damit zählbar als Individuum), aber sie hat keine *eigene* Quellenpräsenz, die in Nennungs-Statistiken aufscheinen sollte.

**Konsequenz.** `frontend/build.py::_scan_released_tei` führt zwei XPath-Pässe pro Datei: `_XP_PERSONS_ALL` für Distinct-Zählung und Sex-Splitt; `_XP_PERSONS_EXCL_MENTIONED` für die Nennungszählung. Die Asymmetrie ist im Glossar-Eintrag [[glossar#Individuelle Person]] und in den Provenienz-Tooltips auf der Startseite explizit benannt.

## KPIs werden direkt aus TEI via XPath gerechnet

**Entscheidung.** Alle Release-KPIs der Startseite (Quellen, Quellen mit Personen, individuelle Personen, Nennungen, Rechtsgeschäfte, Korpus-Matrix) werden im Frontend-Build direkt aus den freigegebenen TEI-Quellen mit lxml und einem dokumentierten XPath gerechnet. CSV-Outputs der Pipeline werden für diese Zahlen nicht herangezogen.

**Begründung.** Eine Zahl ist nur dann wissenschaftlich verwendbar, wenn ihre Provenienz transparent, ihre Berechnungsoperation dokumentiert und ihr Ergebnis selbstständig reproduzierbar ist. Eine zweistufige Aggregation (TEI → Pipeline-CSV → Frontend) erzeugt eine Zwischenebene, an der Definitionen subtil abweichen können — die Pipeline-Spalte `kind_of_linking` etwa mappt auf TEI-Annotationen, ist aber nicht 1:1 identisch mit der semantischen Frage „erscheint Person X im Quellentext". Direkter XPath auf TEI ist die kürzeste, prüfbarste Operation und in den Tooltips wörtlich abgedruckt — eine Verifikation reicht aus, um eine Zahl zu reproduzieren.

**Konsequenz.** `frontend/build.py` definiert die XPath-Konstanten `_XP_TOP_EVENTS`, `_XP_PERSONS_ALL`, `_XP_PERSONS_EXCL_MENTIONED` und scannt einmal pro Build alle freigegebenen TEI-Quellen mit lxml. Die Funktion `_scan_released_tei` ist die alleinige Quelle der Wahrheit für `_compute_release_kpis`, `_compute_corpus_breakdown` und `_released_person_keys`. Der Scan ist kein Bottleneck.

**Nicht gemeint ist**, dass die Pipeline-CSVs überflüssig werden. Sie bleiben für die Detailansichten (Personenregister, Suche, Exploration), für Verifikations-Tests (`verification/`) und für externe SQL-Importe relevant. Nur für die Hero-KPIs der Startseite gilt: TEI direkt, kein Umweg.

## Rechtsgeschäfte zählen nur Top-Level-rs-Events

**Entscheidung.** Die Anzahl der Rechtsgeschäfte (Events) zählt ausschließlich `<rs type="event">`-Elemente, die selbst keinen `<rs type="event">`-Vorfahren haben. Verschachtelte rs-Events innerhalb anderer rs-Events sind Querverweise auf andere Geschäfte und werden separat als `event_mentions` erfasst.

**Begründung.** Im TEI-Kodierungsmodell der Datenbank wird ein Rechtsgeschäft als oberstes `<rs type="event">` markiert. Innerhalb seines Prosatexts können weitere Geschäfte zitiert werden, etwa eine ältere Urkunde, auf die sich das aktuelle bezieht. Diese Zitate werden ebenfalls mit `<rs type="event">` ausgezeichnet, sind aber semantisch keine eigenständigen Geschäfte des aktuellen Dokuments. Wer alle rs-Events ungefiltert zählt, summiert Geschäfte und Zitate in einen Topf und überschätzt den Umfang systematisch.

**Konsequenz.** Der zentrale XPath in `pipeline/transformers/events.py` lautet:

```
//tei:body//tei:rs[@type='event'][not(ancestor::tei:rs[@type='event'])]
```

Verschachtelte rs-Events landen über `pipeline/utils/event_helpers.py::iter_top_level_events()` als `event_mentions`-Zeilen mit ihrem `outer_event_key` in `event_mentions.csv`, ohne in die Hauptzählung einzugehen. Hand-rolled `//tei:rs[@type='event']`-XPaths ohne den `not(ancestor)`-Filter sind ein Fehler.

**Nicht gemeint ist**, dass die Information über mentioned Events verloren geht. Sie bleibt in `event_mentions.csv` und kann zusätzlich angezeigt werden — etwa über einen Toggle „Rechtsgeschäfte inkl. mentioned Events". Dieser Toggle wäre eine Anzeige-Option, nicht der Standardwert.

## Mentioned-Event-Vergleichsstand als Build-Flag

**Entscheidung.** Der Vergleichsstand „Rechtsgeschäfte inklusive mentioned Events" wird als Build-Flag realisiert, nicht als UI-Toggle. Aktiviert wird er über die Umgebungsvariable `PIPELINE_INCLUDE_MENTIONED_EVENTS=1` (Pipeline-Repo) bzw. das CLI-Flag `python -m frontend build --include-mentioned` (Frontend-Repo). Der Default-Build bleibt unverändert und schreibt nach `docs/`; der Vergleichsbuild landet in `docs-with-mentioned/`.

**Begründung.** Die Anforderung kommt aus der editorischen Arbeit: ein Vergleichsstand soll zeigen, wie sich Häufigkeiten, Rollen und Beziehungstypen verändern, wenn verschachtelte rs-Events als vollwertige Events gezählt werden. Ein UI-Toggle wäre methodisch attraktiver (Live-Vergleich im Browser, beide Stände in einem Permalink), würde aber alle Aggregat-JSONs verdoppeln, jede Visualisierung umschalten und die URL-Logik quer durch den Frontend-Code verändern. Der Aufwand passt nicht zur Frequenz, mit der der Vergleich tatsächlich gemacht wird. Ein Build-Flag liefert denselben Erkenntnisgewinn als zwei statische Stände, die parallel servierbar sind.

**Konsequenz.** Pipeline-seitig schaltet `pipeline.config.include_mentioned_events()` die Filter in `pipeline/utils/event_helpers.py` zentral um; `event_mentions.csv` bleibt im Vergleichsbuild leer, damit verschachtelte Events nicht doppelt gezählt werden. Frontend-seitig setzt `frontend/__main__.py` die Env-Var vor dem Import von `frontend.config`; `DOCS_DIR` wählt dann das Output-Verzeichnis. `_kpi.py` schaltet die XPath-Selektoren um, sodass die Hero-KPIs der Startseite konsistent mit dem CSV-Stand laufen. Aufrufkette: `PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform` im Pipeline-Repo, dann `python -m frontend build --include-mentioned` im Frontend-Repo.

**Beobachtung am Stand 2026-05-16.** Die Differenz wird vollständig vom QGW-Korpus getragen (+727 Events), Stadtbücher trägt zwei. Roles-Coverage: 4214 → 4943 Events (+17 %), Transactions identisch, Person-Count unverändert (Distinct-Personen sind ohnehin asymmetrisch gezählt), Persons-with-Org +47.

**Nicht gemeint ist**, dass `docs-with-mentioned/` öffentlich publiziert wird. Der Stand ist ein editorisches Vergleichswerkzeug. GitHub Pages serviert weiterhin nur `docs/`.

## Stufenmodell für Korpus-Auswahl und Annotationsebenen

**Entscheidung.** Der Build kennt vier benannte Stufen, die Korpus-Auswahl und Annotationsebenen als zitierbares Profil bündeln. Aktiviert über `python -m frontend build --stage N` (N in 1 bis 4); `--include-mentioned` bleibt als Alias auf Stufe 2 erhalten.

| Stufe | Subkorpora | Mentioned | Orts-Sichtbarkeit | Anzeige-Filter | Output |
|---|---|---|---|---|---|
| 1 Publikation | nur freigegebene `_ready` | aus | nur Inline-Markup | fest auf freigegeben | `docs/` |
| 2 Vergleich | wie Stufe 1 | ein | wie Stufe 1 | wie Stufe 1 | `docs-with-mentioned/` |
| 3 Voller `_ready`-Bestand | alle `_ready` | aus | Ortsregister | Freigabe-Badge umschaltbar | `docs-full/` |
| 4 Maximalversion | alle mit TEI | ein | Register plus Karte | wie Stufe 3 | `docs-max/` |

**Begründung.** Zuvor steuerten zwei voneinander unabhängige Schalter den Build, `RELEASED_CORPORA` als Build-Zeit-Filter und `PIPELINE_INCLUDE_MENTIONED_EVENTS` als Env-Var. Mit den von Korbinian neu eingespielten Subkorpora (QGW 1448–57, Satzbuch CD 1448–60) und den vier Forschungsfragen aus der Mail vom 16. Mai werden mehr Achsen relevant: Orts-Annotation, Freigabe-Status pro Subkorpus, Mentioned-Events. Jeder neue Boolean-Schalter würde die Aufruflogik vergrößern, ohne die Stände interpretierbar zu machen. Das Stufenmodell macht jeden Build-Stand zu einer benannten, zitierbaren Konfiguration, die in Provenienz-Tooltips, Reports und Diskussionen referenziert werden kann.

**Konsequenz.** `frontend/stages.py` definiert die Stufen als Dict mit den Achsen `corpora_scope`, `include_mentioned`, `place_visibility`, `display_filter`, `output_dir`. `set_stage_env()` setzt `FRONTEND_STAGE` und davon abgeleitete Env-Vars. `frontend/config.py` und `pipeline/config.py` lesen `FRONTEND_STAGE` als zweite Aktivierungsquelle neben den direkten Env-Vars; Ad-hoc-Pipeline-Läufe (`PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform`) funktionieren unverändert. Stufen 1 und 2 sind heute funktional aktiv und byte-identisch zum vorigen Zwei-Schalter-Stand; Stufen 3 und 4 bauen, liefern aber zunächst denselben Daten-Output, bis die zugehörigen Subkorpora und Features (Ortsregister, Karte, Freigabe-Filter) datenseitig aktiviert sind.

**Nicht gemeint ist**, dass eine Stufe öffentlich publiziert wird außer Stufe 1. Stufen 2 bis 4 sind editorische Werkzeuge; `.gitignore` hält `docs-with-mentioned/`, `docs-full/` und `docs-max/` aus dem Repo. GitHub Pages serviert weiterhin nur `docs/`.

## Forschungsfragen als Implementierungs-Achse

**Entscheidung.** Konkrete Forschungsfragen aus der editorischen Praxis ([[scholar-user-stories#Konkrete Forschungsfragen aus der editorischen Praxis]]) sind die Achse, an der neue Aggregator-Bausteine und Galerie-Einträge gebaut werden. Implementiert wird primär durch Erweiterung bestehender Komponenten (Galerie-Frage in `/analysis/index.html`, Sektion auf der Organisations-Profilseite), nicht durch neue Views. Eine neue Sub-Seite oder Library wird nur eingeführt, wenn keine bestehende Komponente die Antwort tragen kann.

**Begründung.** Vier konkrete Fragen schlagen zehn abstrakte Slot-Kombinationen. Forscherinnen kommen mit Fragen, nicht mit Achsen; die Galerie braucht eine kritische Masse konkreter Einträge, damit Nutzerinnen das Muster erkennen und auf eigene Fragen übertragen. Jede Frage etabliert einen wiederverwendbaren Aggregator-Baustein (Uhlirz-Kategorie-Join, Heirats-Begriffs-Match, Org-Hierarchie-Traversal, Cross-Role-Query), der für viele weitere Fragen verfügbar ist; der Aufwand pro Frage zahlt vierfach ein. Frühere Architektur-Entscheidungen (Org-Profilseiten, Galerie-Composer, Drill-Down-Indizes) tragen die Antwort bereits, sodass massive neue Views Overengineering wären.

**Konsequenz.** Neue Aggregator-Funktionen in den bestehenden Modulen `org_profiles` und `aggregator/analysis` (für die Galerie). Neue normierte Listen (Uhlirz-Kategorien aus `roleName_norm_matching.csv`, Heirats-Begriffe als Konstante im Pipeline-Code) als kleine Code-Bausteine. Verifikation als vierte Säule in `verification/research_questions.py`, die pro Frage eine erwartete Zahlen-Antwort aus den TEI- oder CSV-Daten ableitet und gegen das Frontend-Resultat vergleicht.

**Nicht gemeint ist**, dass jede denkbare Frage einen Galerie-Eintrag bekommt. Die Galerie wächst mit der editorischen Praxis und mit den fachlich tragenden Forschungsfragen, nicht beliebig.

## Begriff Quellenkorpus

**Entscheidung.** Die oberste Gruppierungsebene der Datenbasis heißt „Quellenkorpus", nicht „Sammlung".

**Begründung.** „Sammlung" suggeriert einen kuratorischen Akt, den der Bestand so nicht erfahren hat. „Quellenkorpus" ist der fachhistorisch präzisere Begriff und wird in den Projektpublikationen durchgehend verwendet.

**Konsequenz.** Labels, Filter und Seitentitel sprechen von Quellenkorpus. Siehe [[glossar#Quellenkorpus]].

## Freigegebener Zeitraum

**Entscheidung.** Das UI zeigt nur den Zeitraum, den `RELEASED_PERIOD` in `frontend/config.py` führt. Hardcoded Jahre in Templates sind ein Fehler.

**Begründung.** Nur freigegebene Regesten werden angezeigt. Frühere Anzeigen außerhalb des Freigabezeitraums waren fehlerhafte Ableitungen aus unbereinigten Quellen.

**Konsequenz.** Zeitregler und Anzeigen leiten ihre Grenzen aus der Konfiguration ab.

## Freigegebene Korpora und Aufnahme-Workflow

**Entscheidung.** Die Menge der publizierten Subkorpora ist als Tupel `RELEASED_CORPORA` im Pipeline-Repo (`pipeline/config.py`) hinterlegt und gilt als Single Source of Truth für CSV-Erzeugung und Frontend-Build.

**Begründung.** Eine zentrale Liste verhindert, dass an mehreren Stellen unterschiedliche Mengen entstehen (Pipeline exportiert, Frontend filtert, Tests prüfen). Sie macht die Freigabeentscheidung explizit und rückführbar auf einen Commit. Ungeprüfte Korpora bleiben für die editorische Arbeit zugänglich, ohne in den publizierten Stand zu lecken.

**Konsequenz.** Ein neuer Subkorpus wird in vier Schritten aufgenommen: Quellen unter `sources/<Collection>/<Subcollection>_ready/` ablegen, das Tupel `RELEASED_CORPORA` ergänzen, im Pipeline-Repo `python -m pipeline transform` ausführen, im Frontend-Repo `python -m frontend build`. Liegt der neue Zeitraum außerhalb des aktuellen Freigabezeitraums, ist zusätzlich `RELEASED_PERIOD` in `frontend/config.py` anzupassen. Für interne Analysen steht der Override `PIPELINE_INCLUDE_UNRELEASED=1` zur Verfügung; im publizierten Build wird er nicht eingesetzt.

## Formulierung „noch nicht ausgewertet"

**Entscheidung.** Eine nicht ausgewertete Periode innerhalb des Freigabezeitraums wird als „noch nicht ausgewertet" bezeichnet, nicht als „Überlieferungslücke".

**Begründung.** Die Überlieferung existiert; nur die redaktionelle Auswertung steht aus. Die frühere Formulierung war sachlich falsch und in einer wissenschaftlich verwendbaren Datenbank nicht haltbar.

**Konsequenz.** Der Begriff ist an allen sichtbaren Stellen konsequent zu verwenden. Konkrete Grenzen leben in `RELEASED_PERIOD.unprocessed_gaps`.

## Register-Freigabe

**Entscheidung.** Die Datenbank publiziert zwei Register: Personen und Organisationen. Jede individuelle Entität mit mindestens einer Nennung in einer freigegebenen Quelle erhält eine eigene Detail-Profilseite. Orts-Daten leben ausschließlich als Inline-Annotation im Quellen-Volltext.

**Begründung.** Die Pipeline liefert für Personen- und Organisations-Daten konsistente Stammdaten, Quellenverweise und Beziehungen. Für Orte fehlt diese Konsolidierung im aktuellen Freigabestand: die beiden freigegebenen Subkorpora QGW Vienna 1177-1414 und Stadtbücher Band 1 tragen zusammen 37 Orts-Annotationen, verteilt auf 11 von 2601 Dateien. Ein Ortsregister auf dieser Basis würde Bearbeitungstiefe vortäuschen, die die freigegebenen Daten nicht hergeben. Die Orts-Auszeichnung der TEI-Edition bleibt im Quellen-Volltext als Markup sichtbar, damit sie nicht unsichtbar wird; sie trägt aber kein Sprungziel und führt zu keiner eigenständigen Detail-Ansicht.

**Konsequenz.** Listen-Seiten liegen unter `register/persons.html` und `register/orgs.html`. Detail-Seiten unter `register/persons/<pe__id>.html` und `register/orgs/<org__id>.html`. `<rs type="person">` und `<rs type="org">` im Quellen-Volltext verlinken jeweils auf das zugehörige Profil; `<rs type="place">` wird als `<span>` mit Tooltip ohne Sprungziel gerendert. Orts-Bezüge in Org- und Personen-Profilen (Standort, Eigentum, Pacht) erscheinen als Klartext.

**Nicht gemeint ist**, dass das Ortsregister dauerhaft ausgeschlossen ist. Die Entscheidung ist datenabhängig. Sobald weitere Subkorpora freigegeben werden, in denen `<rs type="place">` mit `@ref` konsequent ausgezeichnet ist und die Orts-Stammdaten in `indices/placeList.xml` konsolidiert sind, ist sie neu zu treffen. Ein Inventar-Lauf via `python -m verification.run --inventory` macht die Annotationsdichte pro Subkorpus sichtbar und liefert die Datengrundlage für die Neubewertung.

## Trennung Frontend-Repo und Pipeline-Repo

**Entscheidung.** Build-Output liegt in einem eigenen Repository, getrennt vom Pipeline- und Template-Quellcode.

**Begründung.** Siehe [[architecture#Trennung Quelle und Build-Output]]. Die Trennung hält die Historie der Inhaltsänderungen übersichtlich und reduziert das Risiko, dass Output-Artefakte mit Quelländerungen verwechselt werden.

**Konsequenz.** HTMLs werden nicht direkt editiert. Änderungen gehen durch Rebuild.

## Obsidian-kompatibles Knowledge-Format

**Entscheidung.** Die Wissensbasis liegt als flache Markdown-Dateien mit Wiki-Links vor, ohne Unterordner. [[index]] dient als Lesepfad-Einstieg.

**Begründung.** Die flache Struktur macht den Vault in Obsidian unmittelbar nutzbar. Build-Anleitungen leben in `README.md` und `CLAUDE.md`, nicht in der Wissensbasis.

## Verifikations-Test-Set als eigenständige Komponente

**Entscheidung.** Neben der Pipeline existiert ein unabhängiges Verifikations-Test-Set, das die TEI-Quellen und Register-XMLs eigenständig einliest, die Aggregate nachrechnet und gegen die vom Build erzeugten JSON-Ausgaben legt.

**Begründung.** Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht. Die Frage, ob ein Label an einer Zahl semantisch korrekt ist, lässt sich nur beantworten, wenn eine zweite, unabhängige Rechnung sie bestätigt. Die Implementierung in Python mit `lxml` vermeidet CSV-Zwischenstufen und trifft auf die Quelle direkt.

**Konsequenz.** Das Test-Set läuft auf Abruf und schreibt versionierte Reports. Diskrepanzen führen zu Korrekturen in Templates, Aggregations-Logik oder Quell-Daten. Gleichzeitig dient dieselbe Aggregations-Logik als Fundament für die [[#Provenienz als inline Drill-down in den Aggregat-JSONs]], weil beide dieselben Zählungen auf derselben Quellebene nachvollziehen. Siehe [[architecture#Verifikations-Test-Set]].

## Provenienz als inline Drill-down in den Aggregat-JSONs

**Entscheidung.** Die Provenienz einer aggregierten Zahl — also die Liste der Quelldokumente, die sie stützen — lebt als `drill_down`-Unterstruktur **innerhalb** der jeweiligen Aggregat-JSON, nicht als separate Datei.

**Begründung.** Die meisten aggregierten JSONs tragen die Provenienz-Information bereits als inline Drill-down (role × sex → file_keys, relation type × sex → file_keys, transaction type × decade → file_keys, place → file_keys). Eine separate Parallel-JSON-Struktur wäre Duplikation derselben Information. Die inline Form hält Aggregat und Provenienz zusammen, ohne dass ein Frontend-Reader zwei Dateien korrelieren muss.

**Konsequenz.** Jeder Aggregat-JSON enthält einen `drill_down`-Abschnitt mit dem gleichen Schlüsselmuster wie die Counter-Werte, aber mit sortierten Listen von `file_key`-Verweisen statt Zahlen. Das Frontend löst einen Tooltip durch Lookup im gleichen JSON auf, ohne zusätzliches Nachladen. Die Zielkonsumption für das `file_key` ist `data/docs_lookup.json`, das jeden Schlüssel auf URL, Regest und Metadaten abbildet. Siehe [[specification#Datenrobustheit und Provenienz]] und [[ui-design#Tip-System]].

**Nicht gemeint ist**, dass Aggregat-JSONs gegenseitig referenzieren oder fachlich zirkulär werden. `drill_down` ist eine reine Quellenauflistung, keine Aggregation zweiter Ordnung.

## Zeitlose Formulierung der Wissensbasis

**Entscheidung.** Die Dokumente der Wissensbasis sind zeitlos formuliert, mit Ausnahme von [[journal]].

**Begründung.** Konzepte, Anforderungen und Entscheidungen bleiben länger gültig als operative Einzelheiten. Ein Dokument, das mit einem konkreten Stichtag verknüpft ist, veraltet schneller und lädt zur Überarbeitung in die falsche Richtung ein.

**Konsequenz.** Keine Personennamen, keine Meeting-Datumsangaben, keine Quantitäten des Korpus. Ausnahme bleibt das journal.md als chronologisches Arbeitstagebuch.

## Maximaler Informations-Output als Gestaltungsleitlinie

**Entscheidung.** Das UI priorisiert Nachvollziehbarkeit vor reduzierter Darstellung.

**Begründung.** Fachnutzerinnen brauchen Herkunftsanzeigen an jeder Zahl. Eine Reduktion, die Herkunft verschleiert, ist für die wissenschaftliche Verwendung dysfunktional.

**Konsequenz.** Tooltips, Filterstatus und Zählebenen-Anzeige sind dauerhaft sichtbar. Ausführung in [[ui-design#Leitprinzip Maximaler Informations-Output]].

**Nicht gemeint ist**, dass Dichte Unübersichtlichkeit bedeutet. Die Oberfläche strebt hohe Informationsdichte mit klarer hierarchischer Gliederung an, nicht visuelles Rauschen.

## Siehe auch

- [[specification]] User-Stories, deren Einlösung diese Entscheidungen prägen
- [[ui-design]] gestalterische Umsetzung
- [[journal]] chronologischer Pfad, auf dem Entscheidungen entstanden sind
