---
title: Spezifikation
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 1.0
created: 2026-02-19
updated: 2026-05-17
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Requirements Engineering]]"]
related: [user-stories, architecture, ui-design, analyse, exploration]
---

# Spezifikation

Anforderungs-Spezifikation der Anwendung. Was die Datenbank publiziert, welche Querschnitts-Erwartungen das UI einlöst, und welche Leitentscheidungen das Verhalten festlegen.

Pro Anforderung steht eine kurze Erläuterung, eine Begründung und eine Konsequenz (Implementierung oder Verweis). Manche Anforderungen tragen zusätzlich eine Abgrenzung „Nicht gemeint ist" zu Missverständnissen. Was Forscher*innen damit untersuchen wollen, beschreibt [[user-stories]]. Chronologische Notizen zur Umsetzung leben im [[journal]].

## Inhalt

1. Korpus, Freigabe und Build-Profil
2. Begriffe und Zählebenen
3. UI-Bereiche und Interaktion
4. Querschnitts-Anforderungen
5. Build, Repos und Wissensbasis

---

# 1 Korpus, Freigabe und Build-Profil

## Begriff Quellenkorpus

**Anforderung.** Die oberste Gruppierungsebene der Datenbasis heißt „Quellenkorpus", nicht „Sammlung".

**Begründung.** „Sammlung" suggeriert einen kuratorischen Akt, den der Bestand so nicht erfahren hat. „Quellenkorpus" ist der fachhistorisch präzisere Begriff und wird in den Projektpublikationen durchgehend verwendet.

**Konsequenz.** Labels, Filter und Seitentitel sprechen von Quellenkorpus. Siehe [[glossar#Quellenkorpus]].

## Freigegebener Zeitraum

**Anforderung.** Das UI zeigt nur den Zeitraum, den `RELEASED_PERIOD` in `frontend/config.py` führt. Hardcoded Jahre in Templates sind ein Fehler.

**Begründung.** Nur freigegebene Regesten werden angezeigt. Frühere Anzeigen außerhalb des Freigabezeitraums waren fehlerhafte Ableitungen aus unbereinigten Quellen.

**Konsequenz.** Zeitregler und Anzeigen leiten ihre Grenzen aus der Konfiguration ab.

## Freigegebene Korpora und Aufnahme-Workflow

**Anforderung.** Die Menge der publizierten Subkorpora ist als Tupel `RELEASED_CORPORA` im Pipeline-Repo (`pipeline/config.py`) hinterlegt und gilt als Single Source of Truth für CSV-Erzeugung und Frontend-Build.

**Begründung.** Eine zentrale Liste verhindert, dass an mehreren Stellen unterschiedliche Mengen entstehen (Pipeline exportiert, Frontend filtert, Tests prüfen). Sie macht die Freigabeentscheidung explizit und rückführbar auf einen Commit. Ungeprüfte Korpora bleiben für die editorische Arbeit zugänglich, ohne in den publizierten Stand zu lecken.

**Konsequenz.** Ein neuer Subkorpus wird in vier Schritten aufgenommen: Quellen unter `sources/<Collection>/<Subcollection>_ready/` ablegen, das Tupel `RELEASED_CORPORA` ergänzen, im Pipeline-Repo `python -m pipeline transform` ausführen, im Frontend-Repo `python -m frontend build`. Liegt der neue Zeitraum außerhalb des aktuellen Freigabezeitraums, ist zusätzlich `RELEASED_PERIOD` in `frontend/config.py` anzupassen. Für interne Analysen steht der Override `PIPELINE_INCLUDE_UNRELEASED=1` zur Verfügung; im publizierten Build wird er nicht eingesetzt.

## Formulierung „noch nicht ausgewertet"

**Anforderung.** Eine nicht ausgewertete Periode innerhalb des Freigabezeitraums wird als „noch nicht ausgewertet" bezeichnet, nicht als „Überlieferungslücke".

**Begründung.** Die Überlieferung existiert; nur die redaktionelle Auswertung steht aus. Die frühere Formulierung war sachlich falsch und in einer wissenschaftlich verwendbaren Datenbank nicht haltbar.

**Konsequenz.** Der Begriff ist an allen sichtbaren Stellen konsequent zu verwenden. Konkrete Grenzen leben in `RELEASED_PERIOD.unprocessed_gaps`.

## Register-Freigabe

**Anforderung.** Die Datenbank publiziert zwei Register: Personen und Organisationen. Jede individuelle Entität mit mindestens einer Nennung in einer freigegebenen Quelle erhält eine eigene Detail-Profilseite. Orts-Daten leben ausschließlich als Inline-Annotation im Quellen-Volltext.

**Begründung.** Die Pipeline liefert für Personen- und Organisations-Daten konsistente Stammdaten, Quellenverweise und Beziehungen. Für Orte fehlt diese Konsolidierung im aktuellen Freigabestand: Orts-Annotationen sind in den freigegebenen Subkorpora zu wenige und zu ungleichmäßig verteilt, um ein eigenständiges Register zu tragen. Ein Ortsregister auf dieser Basis würde Bearbeitungstiefe vortäuschen, die die freigegebenen Daten nicht hergeben. Die Orts-Auszeichnung der TEI-Edition bleibt im Quellen-Volltext als Markup sichtbar, damit sie nicht unsichtbar wird; sie trägt aber kein Sprungziel und führt zu keiner eigenständigen Detail-Ansicht.

**Konsequenz.** Listen-Seiten liegen unter `register/persons.html` und `register/orgs.html`. Detail-Seiten unter `register/persons/<pe__id>.html` und `register/orgs/<org__id>.html`. `<rs type="person">` und `<rs type="org">` im Quellen-Volltext verlinken jeweils auf das zugehörige Profil; `<rs type="place">` wird als `<span>` mit Tooltip ohne Sprungziel gerendert. Orts-Bezüge in Org- und Personen-Profilen (Standort, Eigentum, Pacht) erscheinen als Klartext.

**Nicht gemeint ist**, dass das Ortsregister dauerhaft ausgeschlossen ist. Die Entscheidung ist datenabhängig. Sobald weitere Subkorpora freigegeben werden, in denen `<rs type="place">` mit `@ref` konsequent ausgezeichnet ist und die Orts-Stammdaten in `indices/placeList.xml` konsolidiert sind, ist sie neu zu treffen. Ein Inventar-Lauf via `python -m verification.run --inventory` macht die Annotationsdichte pro Subkorpus sichtbar und liefert die Datengrundlage für die Neubewertung.

## Stufenmodell für Korpus-Auswahl und Annotationsebenen

**Anforderung.** Der Build kennt vier benannte Stufen, die Korpus-Auswahl und Annotationsebenen als zitierbares Profil bündeln. Aktiviert über `python -m frontend build --stage N` (N in 1 bis 4); `--include-mentioned` bleibt als Alias auf Stufe 2 erhalten.

| Stufe | Subkorpora | Mentioned | Orts-Sichtbarkeit | Anzeige-Filter | Output |
|---|---|---|---|---|---|
| 1 Publikation | alle freigegebenen `_ready` | aus | Inline-Markup plus Orts-Annotation | fest auf freigegeben | `docs/` |
| 2 Vergleich | wie Stufe 1 | ein | wie Stufe 1 | wie Stufe 1 | `docs-with-mentioned/` |
| 3 Voller `_ready`-Bestand | heute deckungsgleich mit Stufe 1 | aus | wie Stufe 1 | Freigabe-Badge umschaltbar | `docs-full/` |
| 4 Maximalversion | alle mit TEI | ein | Register plus Karte | wie Stufe 3 | `docs-max/` |

**Begründung.** Zuvor steuerten zwei voneinander unabhängige Schalter den Build, `RELEASED_CORPORA` als Build-Zeit-Filter und `PIPELINE_INCLUDE_MENTIONED_EVENTS` als Env-Var. Mit den neu eingespielten Subkorpora und neuen Forschungsfragen werden mehr Achsen relevant: Orts-Annotation, Freigabe-Status pro Subkorpus, Mentioned-Events. Jeder neue Boolean-Schalter würde die Aufruflogik vergrößern, ohne die Stände interpretierbar zu machen. Das Stufenmodell macht jeden Build-Stand zu einer benannten, zitierbaren Konfiguration, die in Provenienz-Tooltips, Reports und Diskussionen referenziert werden kann.

**Konsequenz.** `frontend/stages.py` definiert die Stufen als Dict mit den Achsen `corpora_scope`, `include_mentioned`, `place_visibility`, `display_filter`, `output_dir`. `set_stage_env()` setzt `FRONTEND_STAGE` und davon abgeleitete Env-Vars. `frontend/config.py` und `pipeline/config.py` lesen `FRONTEND_STAGE` als zweite Aktivierungsquelle neben den direkten Env-Vars; Ad-hoc-Pipeline-Läufe (`PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform`) funktionieren unverändert. Stufe 1 und 3 sind heute deckungsgleich, weil alle `_ready`-Subkorpora freigegeben sind; sobald wieder ein `_ready`-Subkorpus die Freigabe nicht hat, divergieren sie. Stufe 4 nimmt zusätzlich die nicht-`_ready`-Subkorpora auf und ist Vorschau auf den Maximalbestand.

**Nicht gemeint ist**, dass eine Stufe öffentlich publiziert wird außer Stufe 1. Stufen 2 bis 4 sind editorische Werkzeuge; `.gitignore` hält `docs-with-mentioned/`, `docs-full/` und `docs-max/` aus dem Repo. GitHub Pages serviert weiterhin nur `docs/`.

## Mentioned-Event-Vergleichsstand als Build-Flag

**Anforderung.** Der Vergleichsstand „Rechtsgeschäfte inklusive mentioned Events" wird als Build-Flag realisiert, nicht als UI-Toggle. Aktiviert wird er über die Umgebungsvariable `PIPELINE_INCLUDE_MENTIONED_EVENTS=1` (Pipeline-Repo) bzw. das CLI-Flag `python -m frontend build --include-mentioned` oder `--stage 2` (Frontend-Repo). Der Default-Build bleibt unverändert und schreibt nach `docs/`; der Vergleichsbuild landet in `docs-with-mentioned/`.

**Begründung.** Die Anforderung kommt aus der editorischen Arbeit: ein Vergleichsstand soll zeigen, wie sich Häufigkeiten, Rollen und Beziehungstypen verändern, wenn verschachtelte rs-Events als vollwertige Events gezählt werden. Ein UI-Toggle wäre methodisch attraktiver (Live-Vergleich im Browser, beide Stände in einem Permalink), würde aber alle Aggregat-JSONs verdoppeln, jede Visualisierung umschalten und die URL-Logik quer durch den Frontend-Code verändern. Der Aufwand passt nicht zur Frequenz, mit der der Vergleich tatsächlich gemacht wird. Ein Build-Flag liefert denselben Erkenntnisgewinn als zwei statische Stände, die parallel servierbar sind.

**Konsequenz.** Pipeline-seitig schaltet `pipeline.config.include_mentioned_events()` die Filter in `pipeline/utils/event_helpers.py` zentral um; `event_mentions.csv` bleibt im Vergleichsbuild leer, damit verschachtelte Events nicht doppelt gezählt werden. Frontend-seitig setzt `frontend/__main__.py` die Env-Var vor dem Import von `frontend.config`; `DOCS_DIR` wählt dann das Output-Verzeichnis. `_kpi.py` schaltet die XPath-Selektoren um, sodass die Hero-KPIs der Startseite konsistent mit dem CSV-Stand laufen. Aufrufkette: `PIPELINE_INCLUDE_MENTIONED_EVENTS=1 python -m pipeline transform` im Pipeline-Repo, dann `python -m frontend build --include-mentioned` (oder `--stage 2`) im Frontend-Repo.

**Nicht gemeint ist**, dass `docs-with-mentioned/` öffentlich publiziert wird. Der Stand ist ein editorisches Vergleichswerkzeug. GitHub Pages serviert weiterhin nur `docs/`.

---

# 2 Begriffe und Zählebenen

## Begriff Gesamtnennungen

**Anforderung.** Die Zählebene aller Erwähnungen heißt im UI „Gesamtnennungen", nicht „Nennungen". Die Zählebene der konsolidierten Register-Einträge heißt „Individuelle Personen", „Individuelle Organisationen", „Individuelle Orte".

**Begründung.** Das Präfix schafft eine explizite Abgrenzung zur [[glossar#Individuelle Person]] und reduziert die Verwechslungsgefahr in publikationsrelevanten Zahlen. Die Kurzform „Nennungen" war zu nahe an der alltagssprachlichen Verwendung und lud zu Fehlinterpretationen ein.

**Konsequenz.** Alle UI-Labels, Filter- und Achsenbeschriftungen verwenden „Gesamtnennungen" oder „Individuelle Personen". Siehe [[glossar#Gesamtnennung]]. Welche der beiden Zählebenen einer konkreten Zahl zugrunde liegt, soll am Provenienz-Tooltip erkennbar sein, siehe [[ui-design#Tip-System]]. Ein Label, das eine Zahl fälschlich der anderen Zählebene zuordnet, ist ein Fehler im Sinne von [[#Datenrobustheit und Provenienz]] und wird vom Verifikations-Test-Set sichtbar gemacht, siehe [[architecture#Test-Strategie]].

## Quellenbereinigte Zählung

**Anforderung.** Gesamtnennungen werden quellenbereinigt gezählt: eine Person, Organisation oder ein Ort, die oder der in derselben Quelle mehrfach erwähnt wird, trägt für diese Quelle genau eine Gesamtnennung bei.

**Begründung.** Urteilslisten, Zeugenreihen und Formularwiederholungen führen dazu, dass ein und dieselbe Person innerhalb einer Urkunde namentlich vielfach auftaucht. Eine Zählung pro Einzelerwähnung würde solche Formelpartien gegenüber substanziellen Einzelnennungen überproportional gewichten und Vergleiche zwischen Regesten (wenige Nennungen pro Quelle) und edierten Volltexten (viele Nennungen pro Quelle) systematisch verzerren. Die quellenbereinigte Zählung beantwortet die Forschungsfrage „in wie vielen Quellen ist Person X belegt" präzise und ist robust gegen das Erschließungsformat.

**Konsequenz.** Die Definition in [[glossar#Gesamtnennung]] ist entsprechend formuliert. Der [[ui-design#Tip-System]] benennt diese Zählebene an jeder betroffenen Zahl explizit. Eine Umschaltung auf ungereinigte Einzelerwähnungen ist nicht vorgesehen; sie wäre statistisch missverständlich und fachlich schwer interpretierbar.

**Nicht gemeint ist**, dass das Datenmodell die Information über Mehrfachnennungen verliert. Die TEI-Quellen markieren jede Erwähnung einzeln. Die Dedupizierung greift erst in der Aggregation.

## Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events

**Anforderung.** Eine Personen-Nennung wird im Frontend nur dann gezählt, wenn die Person im TEI-Quellentext als `<rs type="person">` mit `@ref` auf einen `pe__`-Schlüssel annotiert ist und sich nicht innerhalb eines verschachtelten `<rs type="event">` (mentioned Event) befindet. Korrespondierende Hilfsverknüpfungen (`@corresp` ohne `@type="person"`) werden ebenfalls ausgeschlossen.

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

**Anforderung.** Die Distinct-Zählung der individuellen Personen schließt Personen-Annotationen innerhalb mentioned Events **ein**; die Zählung der Nennungen schließt sie **aus**.

**Begründung.** Beide Zählebenen beantworten verschiedene Fragen. „Wie viele unterscheidbare historische Personen umfasst das publizierte Korpus?" — diese Frage zielt auf das Personenregister; eine Person ist *bekannt*, sobald sie in einer freigegebenen Quelle in irgendeiner Annotation auftritt, auch als Querverweis in einem mentioned Event. „Wie häufig wird Person X in den freigegebenen Quellentexten erwähnt?" — diese Frage zielt auf die Belegdichte als Akteurin; nur direkte Quellentext-Erwähnungen aktueller Geschäfte zählen, mentioned Events sind für diese Frage Querverweise auf andere Quellen und gehören nicht in den Zähler.

Die Asymmetrie ist semantisch konsistent: Eine Person, die nur als Querverweis in einer einzigen Quelle erscheint, ist trotzdem im Register vermerkt (und damit zählbar als Individuum), aber sie hat keine *eigene* Quellenpräsenz, die in Nennungs-Statistiken aufscheinen sollte.

**Konsequenz.** `frontend/build.py::_scan_released_tei` führt zwei XPath-Pässe pro Datei: `_XP_PERSONS_ALL` für Distinct-Zählung und Sex-Splitt; `_XP_PERSONS_EXCL_MENTIONED` für die Nennungszählung. Die Asymmetrie ist im Glossar-Eintrag [[glossar#Individuelle Person]] und in den Provenienz-Tooltips auf der Startseite explizit benannt.

## KPIs werden direkt aus TEI via XPath gerechnet

**Anforderung.** Alle Release-KPIs der Startseite (Quellen, Quellen mit Personen, individuelle Personen, Nennungen, Rechtsgeschäfte, Korpus-Matrix) werden im Frontend-Build direkt aus den freigegebenen TEI-Quellen mit lxml und einem dokumentierten XPath gerechnet. CSV-Outputs der Pipeline werden für diese Zahlen nicht herangezogen.

**Begründung.** Eine Zahl ist nur dann wissenschaftlich verwendbar, wenn ihre Provenienz transparent, ihre Berechnungsoperation dokumentiert und ihr Ergebnis selbstständig reproduzierbar ist. Eine zweistufige Aggregation (TEI → Pipeline-CSV → Frontend) erzeugt eine Zwischenebene, an der Definitionen subtil abweichen können — die Pipeline-Spalte `kind_of_linking` etwa mappt auf TEI-Annotationen, ist aber nicht 1:1 identisch mit der semantischen Frage „erscheint Person X im Quellentext". Direkter XPath auf TEI ist die kürzeste, prüfbarste Operation und in den Tooltips wörtlich abgedruckt — eine Verifikation reicht aus, um eine Zahl zu reproduzieren.

**Konsequenz.** `frontend/build.py` definiert die XPath-Konstanten `_XP_TOP_EVENTS`, `_XP_PERSONS_ALL`, `_XP_PERSONS_EXCL_MENTIONED` und scannt einmal pro Build alle freigegebenen TEI-Quellen mit lxml. Die Funktion `_scan_released_tei` ist die alleinige Quelle der Wahrheit für `_compute_release_kpis`, `_compute_corpus_breakdown` und `_released_person_keys`. Der Scan ist kein Bottleneck.

**Nicht gemeint ist**, dass die Pipeline-CSVs überflüssig werden. Sie bleiben für die Detailansichten (Personenregister, Suche, Exploration), für Verifikations-Tests (`verification/`) und für externe SQL-Importe relevant. Nur für die Hero-KPIs der Startseite gilt: TEI direkt, kein Umweg.

## Rechtsgeschäfte zählen nur Top-Level-rs-Events

**Anforderung.** Die Anzahl der Rechtsgeschäfte (Events) zählt ausschließlich `<rs type="event">`-Elemente, die selbst keinen `<rs type="event">`-Vorfahren haben. Verschachtelte rs-Events innerhalb anderer rs-Events sind Querverweise auf andere Geschäfte und werden separat als `event_mentions` erfasst.

**Begründung.** Im TEI-Kodierungsmodell der Datenbank wird ein Rechtsgeschäft als oberstes `<rs type="event">` markiert. Innerhalb seines Prosatexts können weitere Geschäfte zitiert werden, etwa eine ältere Urkunde, auf die sich das aktuelle bezieht. Diese Zitate werden ebenfalls mit `<rs type="event">` ausgezeichnet, sind aber semantisch keine eigenständigen Geschäfte des aktuellen Dokuments. Wer alle rs-Events ungefiltert zählt, summiert Geschäfte und Zitate in einen Topf und überschätzt den Umfang systematisch.

**Konsequenz.** Der zentrale XPath in `pipeline/transformers/events.py` lautet:

```
//tei:body//tei:rs[@type='event'][not(ancestor::tei:rs[@type='event'])]
```

Verschachtelte rs-Events landen über `pipeline/utils/event_helpers.py::iter_top_level_events()` als `event_mentions`-Zeilen mit ihrem `outer_event_key` in `event_mentions.csv`, ohne in die Hauptzählung einzugehen. Hand-rolled `//tei:rs[@type='event']`-XPaths ohne den `not(ancestor)`-Filter sind ein Fehler.

**Nicht gemeint ist**, dass die Information über mentioned Events verloren geht. Sie bleibt in `event_mentions.csv` und kann zusätzlich angezeigt werden — etwa über einen Toggle „Rechtsgeschäfte inkl. mentioned Events". Dieser Toggle wäre eine Anzeige-Option, nicht der Standardwert (siehe [[#Mentioned-Event-Vergleichsstand als Build-Flag]]).

---

# 3 UI-Bereiche und Interaktion

## Titel und Untertitel

**Anforderung.** Der Haupttitel der Datenbank lautet „Stadt und Gemeinschaft Wien", der Untertitel „Datenbank zu mittelalterlichen Rechtsgeschäften".

**Begründung.** Der Haupttitel ist in den Projektpublikationen etabliert. Eine abweichende Neubenennung würde Kontinuität mit bereits gedruckten Texten brechen. Der Untertitel ist deutsch, damit das UI sprachlich durchgängig bleibt und nicht ohne Anlass zwischen Deutsch und Englisch wechselt.

**Konsequenz.** Der Titel ist in Navigationsleiste, Seitentitel und Fußzeile konsistent zu führen.

## Exploration und Analyse als getrennte Bereiche

**Anforderung.** Das UI führt zwei Navigationsbereiche nebeneinander: Analyse und Exploration. Die Trennung folgt dem Interaktionsmodus, nicht dem Inhalt.

- **Analyse** versammelt quantitative Auswertungen mit vorgegebener Achsensemantik: Verteilungen (Donut, Bar-Chart, Tabellen mit Prozentwerten) und Template-Abfragen mit typisierten Slots. Nutzerinnen kommen mit einer Frage und bekommen Zahlen plus Provenienz.
- **Exploration** ist visuell-interaktive Erkundung der Datenstruktur selbst: Personen-Netzwerke, Karten, Timeline-Bänder, Sankey-Diagramme. Nutzerinnen kommen ohne klare Frage und entdecken Pattern in der Visualisierung.

**Begründung.** Donut, Bar-Chart und Verteilungstabellen sind nach DH-Standard analytische Visualisierung — sie zeigen vorberechnete Statistik. Force-Layouts, Karten und Sankey-Diagramme sind Information-Visualisation für offene Erkundung. Die Erwartungshaltung der Nutzerinnen unterscheidet sich entsprechend: „Auswertung" suggeriert quantitative Antwort, „Exploration" visuelles Stöbern. Die Pfade folgen dieser Semantik.

**Konsequenz.** Unter `/analysis/` liegen `auswertungen.html` (Statistik-Verteilungen) und `index.html` (Abfragen). Unter `/exploration/` liegen `zeitstrom.html` (gestapelter Bar-Chart mit Brush-zu-Drill-down) und `personennetzwerk.html` (Ego-Layout mit Klick-Hopping); ein Sankey-Diagramm zu Transaktionsflüssen ist konzipiert, aber noch nicht umgesetzt. Die Navigation bündelt beide Bereiche in eigenen Dropdowns. Siehe [[ui-design#Navigation]] und [[ui-design#Zwei Modi nebeneinander]].

**Nicht gemeint ist**, dass Exploration und Analyse streng disjunkt wären. Eine Nutzerin kann eine Auffälligkeit in einem Donut-Diagramm entdecken (Analyse) und sie in einer Netzwerkvisualisierung qualitativ weiterverfolgen (Exploration), oder umgekehrt. Die Bereiche teilen sich dieselben Aggregate (`roles.json`/`relations.json`/`transactions.json`) und dieselben Filter-Bausteine (Sidebar, Active-Filter-Strip).

## Auswertungen gehört in den Analyse-Bereich

**Anforderung.** Die Auswertungen-Seite (vier Sektionen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen, jeweils als Donut, Bar-Chart oder Tabelle) liegt unter `/analysis/auswertungen.html` und nicht unter `/exploration/`.

**Begründung.** Die Seite zeigt vorberechnete statistische Verteilungen mit Prozentwerten und exakten Zahlen. Die Interaktion beschränkt sich auf zwei orthogonale Achsen (Zeitraum, Geschlecht) plus eine Zähleinheit-Umschaltung (Nennungen ↔ Individuelle Personen) — alles strukturierte Auswertungsachsen, keine offene Erkundung. Donut und Bar-Chart sind klassische Statistik-Displays, keine explorativen Visualisierungen. Wer auf den Eintrag „Auswertungen" klickt, erwartet quantitative Antworten; das ist Analyse-Domain.

**Konsequenz.** Build-Ziel: `docs/analysis/auswertungen.html`. Template: `frontend/templates/analysis_aggregat.html`. JavaScript: `frontend/static/js/analysis-aggregat.js`. Aggregator-Source: `frontend/aggregator/roles.py`, `relations.py`, `transactions.py`. Die Navigation führt sie als Dropdown-Eintrag unter „Analyse", neben „Abfragen" (`/analysis/index.html`).

**Nicht gemeint ist**, dass die Seite niemals interaktive Exploration enthielte. Filter ziehen, Pattern entdecken — das geht hier auch. Aber das primäre Interaktionsmuster ist Verteilungs-Display, nicht visuelle Strukturerkundung.

## Abfragen-Sub-Seite als Konstellations-Abfrage

**Anforderung.** Die Abfragen-Sub-Seite (`/analysis/index.html`) ist eine strukturierte Datenbank-Abfrage über Rollen-Konstellationen, kein Such-UI und keine Frage-Galerie. Eine Forscherin legt N nummerierte Personen-Bedingungen an. Alle vier Slots pro Person (Rolle, Geschlecht, Beruf/Tätigkeit/Amt als Substring-Match auf der Originalschreibung, Uhlirz-Berufsklasse als klassifizierte Achse) sind optional und gleichberechtigt. Eine Person zählt als aktive Filter-Bedingung, sobald mindestens ein Slot gesetzt ist. Alle aktiven Bedingungen müssen gemeinsam in demselben Rechtsgeschäft (eng, Default) oder in derselben Quelle (weit) erfüllt sein. Globaler Geltungsbereich: Quellenkorpus (Mehrfachauswahl). Anfangszustand: keine Personen-Bedingung, leere Trefferliste. Live-Update bei jeder Änderung.

Die Seite ist visuell in zwei semantisch unterschiedliche Bereiche getrennt: Der **Abfrage-Bereich** oben (Geltungsbereich plus Personen-Bedingungen) definiert, *was gesucht wird*. Die **Trefferzeile** im Tabellen-Header (KPI als „X Rechtsgeschäfte in Y Quellen", CSV-Download rechts) und die Trefferliste darunter zeigen *die Antwort*. Eine globale Reset-Aktion „Zurückstellen" rechts oben im Abfrage-Container leert die ganze Konstellation. Eine spätere Sidebar wird post-hoc-Filter (Zeitraum, optional weitere Achsen) aufnehmen, die die Treffermenge eingrenzen ohne die Abfrage selbst zu ändern.

**Begründung.** Forscherinnen kommen mit konkreten Konstellationsfragen („männliche Aussteller mit Tätigkeit X, weibliche Empfängerinnen mit Beruf Y") an die Datenbank, nicht mit abstrakten Slot-Subjects. Die strukturierte Abfrage über Bedingungen, die parallel erfüllt sein müssen, bildet das Forschungsinteresse direkter ab als eine Frage-Galerie mit vorgefertigten Resolvern. Sie ist auch näher am Sprachgefühl der Vorgänger-Datenbank, die als „Standardsuche" mit kombinierbaren Bedingungen funktioniert hat.

**Konsequenz.** Eine einzelne JS-Datei `analysis-resolver.js` lädt `docs/data/role_constellation.json` lazy, hält den Zustand im DOM und in der URL, matcht Konstellationen clientseitig gegen `events[]`. Die alten Module `analysis.js`, `analysis-composer.js`, `analysis-capabilities.js` (Frage-Galerie-Implementierung) sind entfernt. Permalinks serialisieren die ganze Abfrage: `#p1=r=issuer,s=m,o=snyder&p2=r=recipient,s=f&y=1340-1410&c=QGW`. CSV-Export gibt genau die Bildschirmspalten heraus.

**Nicht gemeint ist**, dass das UI alle früheren Frage-Galerie-Achsen abdeckt. Beziehungstypen, Transaktionstypen, Aggregat-Donuts liegen auf der Auswertungs-Sub-Seite, nicht hier.

**Datenpfad-Vorbehalte.** Geschlecht und Rolle funktionieren vollständig. Beruf/Tätigkeit/Amt liegt nur als Originalschreibung vor (`snyder`, `purger`, `Bürger` nebeneinander), das UI bietet ein Freitext-Feld mit Operator „enthält" und smarten Vorschlägen aus den Top-Schreibvarianten. Eine Bedingung „Titel = Herr / Bischof" wird nicht angeboten, weil das TEI-Modell Honorifics und Berufe in einer einzigen Annotation (`<occupation>`) zusammenführt; eine separate Titel-Achse erfordert eine Anpassung im Schwester-Repo (Pipeline-Spalte plus TEI-Annotation), nicht im Frontend.

Der Beruf- und der Uhlirz-Filter ziehen ihre Werte aus zwei Annotationsorten: `occ_relations_in_sources.csv` (typisierte `<occupation>`-Annotation, oft Status und Funktion: purger, clericus) und `persons_in_sources.csv::source_prof` (Apposition im Quellentext, oft das eigentliche Handwerk: wachsgiesser, ledrer). Beide Quellen werden pro Person und Event vereinigt und case-insensitiv dedupliziert; die Uhlirz-Klassifikation läuft über die Vereinigung. Begründung: das Forschungsinteresse „wer tritt als Wachsgießer auf" meint beide Annotationsformen, und die Trennung wäre Edition-Detailwissen, das der Filter nicht voraussetzen darf. Konsequenz: die UI-Treffermengen decken sich jetzt mit denen der Verifikations-Säule `verification/research_questions.py`, die `source_prof` schon länger liest. Die strukturelle Trennung zwischen Funktion und Beruf bleibt auf den Personenprofilen sichtbar, wo beide Annotationsorte separat aufgelistet sind. Eine separate Titel-Achse („Herr / Bischof") wird weiterhin nicht angeboten, weil das TEI-Modell Honorifics und Berufe in einer einzigen Annotation zusammenführt; das erfordert eine Anpassung im Schwester-Repo, nicht im Frontend.

## Personen- und Organisationsprofile als Detailseiten

**Anforderung.** Jede individuelle Person und jede individuelle Organisation mit Nennung in einer freigegebenen Quelle erhält eine eigene Detail-Profilseite. `<rs type="person">` und `<rs type="org">` im Quellen-Volltext verlinken direkt auf das Profil.

**Begründung.** Personennamen und Organisationsbezeichnungen waren ohne Profilseiten Sackgassen — klickbar, aber nur als Hash-Anker in die Register-Liste, wo der Anker im JS-gerenderten Index nicht ankam. Beziehungs-Daten (Verwandtschaft, Freundschaft, Vertretung, Beruf, Titelverweis) lagen vollständig in den Pipeline-CSVs vor, waren UI-seitig aber unsichtbar; ein im TEI kodiertes Ehepaar blieb für die Forscherin im Frontend nicht einsehbar. Die Profile schließen diese Lücke und machen die TEI-Annotation auf Entitäts-Ebene navigierbar.

**Konsequenz.** Aggregator-Module `person_profiles` und `org_profiles` rendern Profile direkt zu HTML. Layout und Bidirektionalität der Beziehungs-Auflösung sind in [[ui-design#Entitäts-Profilseite]] und [[data#Register]] beschrieben.

**Nicht gemeint ist**, dass jedes Profil eine vollständige Biografie liefert. Die Profile zeigen, was die TEI-Annotation hergibt.

## Datenkorb als clientseitige Sammlung

**Anforderung.** Forschende sammeln Quellen, Personen und Organisationen über Sitzungen hinweg in einem clientseitigen Datenkorb. Daten bleiben rein clientseitig, keine Server-Persistenz, keine Identitätspflicht.

**Begründung.** Forschungspfade springen häufig zwischen Übersicht, Aggregat, Quelle, Person, Organisation. Eine sammelnde Schicht über mehrere Seiten und Item-Typen erlaubt es, ein Forschungs-Korpus zusammenzustellen, ohne Browser-Tab-Wildwuchs oder manuelle Bookmark-Strategie. Eine Account-basierte Persistenz wäre ein anderer Stack mit Auth, DSGVO-Implikationen und laufenden Speicherkosten — ohne erkennbaren Mehrwert für die jetzt bedienten Forschungsszenarien.

**Konsequenz.** UI-Mechanik (Sammeln, Ableiten, Promotion, drei Tabellen, CSV-Export) in [[ui-design#Datenkorb]], technische Persistenz und Komponenten-Verteilung in [[architecture#Datenkorb als clientseitige Persistenz]]. Der Bridge-Pfad in externe Werkzeuge (Zotero, BibTeX-Konverter, Excel) läuft über CSV-Export.

## Forschungsstand zitierbar via URL-Parameter

**Anforderung.** Auf den Daten-Visualisierungs-Seiten wird der Filter-Stand in URL-Suchparameter serialisiert und bei Page-Load wieder eingelesen. Quellen- und Personen-Listenseiten haben das Pattern bereits.

**Begründung.** Eine Forscherin will einen Filter-Stand bookmarken, in eine Mail kopieren oder in einer Publikation zitieren. Ohne URL-Sync ist der Filter beim Reload weg.

**Konsequenz.** Mechanik (Schreib-Strategie, weggelassene Defaults, Init-Guard, Cross-Page-Sprung) in [[architecture#URL-State als Forschungsstand]].

## Cross-Page-Sprung mit Filter-Übernahme

**Anforderung.** Drill-down-Overlays (Auswertungen) und Brush-Drill (Zeitstrom) bieten einen „→ in Quellen-Liste öffnen"-Link. Der Link transferiert Zeitraum + Geschlechter-Filter (mappt auf das Quellen-Filter-Vokabular) in die Quellen-Listenseite. Page-spezifische Filter (Rolle, Beziehungstyp, Bezeichnung, Transaktionstyp, Stack-Fokus) werden nicht übertragen, weil die Quellen-Liste sie nicht kennt.

**Begründung.** Die Visualisierung weckt das Interesse, die strukturierte Quellen-Liste vertieft. Beide Seiten teilen sich Zeitraum und Geschlechter-Achse — die Übernahme ist verlustfrei für diese, ehrlich-lückenhaft für die anderen.

**Konsequenz.** `VizCore.buildDocumentsURL({decadeMin, decadeMax, sex})` baut die Cross-Nav-URL. Mapping ist asymmetrisch: `sex='f' → with-f`, `sex='m' → only-m` (Quellen kennt kein `with-m`).

## Forschungsfragen als Implementierungs-Achse

**Anforderung.** Konkrete Forschungsfragen aus der editorischen Praxis ([[user-stories#2 Konkrete Forschungsfragen aus der editorischen Praxis]]) sind die Achse, an der neue Aggregator-Bausteine und Galerie-Einträge gebaut werden. Implementiert wird primär durch Erweiterung bestehender Komponenten (Galerie-Frage in `/analysis/index.html`, Sektion auf der Organisations-Profilseite), nicht durch neue Views. Eine neue Sub-Seite oder Library wird nur eingeführt, wenn keine bestehende Komponente die Antwort tragen kann.

**Begründung.** Vier konkrete Fragen schlagen zehn abstrakte Slot-Kombinationen. Forscherinnen kommen mit Fragen, nicht mit Achsen; die Galerie braucht eine kritische Masse konkreter Einträge, damit Nutzerinnen das Muster erkennen und auf eigene Fragen übertragen. Jede Frage etabliert einen wiederverwendbaren Aggregator-Baustein (Uhlirz-Kategorie-Join, Heirats-Begriffs-Match, Org-Hierarchie-Traversal, Cross-Role-Query), der für viele weitere Fragen verfügbar ist; der Aufwand pro Frage zahlt vierfach ein. Frühere Architektur-Entscheidungen (Org-Profilseiten, Galerie-Composer, Drill-Down-Indizes) tragen die Antwort bereits, sodass massive neue Views Overengineering wären.

**Konsequenz.** Neue Aggregator-Funktionen in den bestehenden Modulen `org_profiles` und `aggregator/analysis` (für die Galerie). Neue normierte Listen (Uhlirz-Kategorien aus `roleName_norm_matching.csv`, Heirats-Begriffe als Konstante im Pipeline-Code) als kleine Code-Bausteine. Verifikation als vierte Säule in `verification/research_questions.py`, die pro Frage eine erwartete Zahlen-Antwort aus den TEI- oder CSV-Daten ableitet und gegen das Frontend-Resultat vergleicht.

**Nicht gemeint ist**, dass jede denkbare Frage einen Galerie-Eintrag bekommt. Die Galerie wächst mit der editorischen Praxis und mit den fachlich tragenden Forschungsfragen, nicht beliebig.

---

# 4 Querschnitts-Anforderungen

## Datenpfad-Ehrlichkeit

**Anforderung.** Filterbedingungen und Achsenwerte im UI werden nur angeboten, wenn sie in den Daten tatsächlich existieren und das TEI-Annotationsmodell sie trennscharf führt.

**Begründung.** Ein Filter „Titel ist Herr" wird beispielsweise auf der Abfragen-Sub-Seite nicht angeboten, weil die TEI-Edition Honorifics und Berufe in einer einzigen Annotation zusammenführt. Eine derartige Bedingung müsste zuerst im Schwester-Repo als eigene Spalte angelegt werden.

**Konsequenz.** Bedingungen mit nur einer Schreibweise im Datenbestand (Originalform) werden explizit als solche gekennzeichnet, damit Forscherinnen das Trefferbild korrekt einordnen.

## Datenrobustheit und Provenienz

**Anforderung.** Aggregierte Zahlen tragen auf Startseite, Auswertungen und Korpus-Zählern einen Provenienz-Tooltip, der den zugrunde liegenden Bestand und die Zähloperation benennt.

**Begründung.** Fachnutzerinnen brauchen Herkunftsanzeigen an jeder Zahl, um sie in eigenen Texten zitieren oder gegen eigene Auswertungen halten zu können. Eine Zahl ohne benannte Provenienz ist für wissenschaftliche Verwendung dysfunktional.

**Konsequenz.** Die Rückführung auf die Quelldokumente läuft über die in [[architecture#Provenienz-Indizes]] beschriebenen Indizes. Das Tip-System umfasst vier Klassen, Provenienz, Glossar-Definition, UI-Hilfe und schneller Hover-Hint, siehe [[ui-design#Tip-System]].

## Provenienz als inline Drill-down in den Aggregat-JSONs

**Anforderung.** Die Provenienz einer aggregierten Zahl — also die Liste der Quelldokumente, die sie stützen — lebt als `drill_down`-Unterstruktur **innerhalb** der jeweiligen Aggregat-JSON, nicht als separate Datei.

**Begründung.** Die meisten aggregierten JSONs tragen die Provenienz-Information bereits als inline Drill-down (role × sex → file_keys, relation type × sex → file_keys, transaction type × decade → file_keys, place → file_keys). Eine separate Parallel-JSON-Struktur wäre Duplikation derselben Information. Die inline Form hält Aggregat und Provenienz zusammen, ohne dass ein Frontend-Reader zwei Dateien korrelieren muss.

**Konsequenz.** Jeder Aggregat-JSON enthält einen `drill_down`-Abschnitt mit dem gleichen Schlüsselmuster wie die Counter-Werte, aber mit sortierten Listen von `file_key`-Verweisen statt Zahlen. Das Frontend löst einen Tooltip durch Lookup im gleichen JSON auf, ohne zusätzliches Nachladen. Die Zielkonsumption für das `file_key` ist `data/docs_lookup.json`, das jeden Schlüssel auf URL, Regest und Metadaten abbildet. Siehe [[ui-design#Tip-System]].

**Nicht gemeint ist**, dass Aggregat-JSONs gegenseitig referenzieren oder fachlich zirkulär werden. `drill_down` ist eine reine Quellenauflistung, keine Aggregation zweiter Ordnung.

## Verifizierbarkeit und Verifikations-Test-Set

**Anforderung.** Neben der Pipeline existiert ein unabhängiges Verifikations-Test-Set, das die TEI-Quellen und Register-XMLs eigenständig einliest, die Aggregate nachrechnet und gegen die vom Build erzeugten JSON-Ausgaben legt. Drei Verifikations-Stufen unter `verification/` plus ein TEI-Inventar.

**Begründung.** Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht. Die Frage, ob ein Label an einer Zahl semantisch korrekt ist, lässt sich nur beantworten, wenn eine zweite, unabhängige Rechnung sie bestätigt. Die Implementierung in Python mit `lxml` vermeidet CSV-Zwischenstufen und trifft auf die Quelle direkt.

**Konsequenz.** Das Test-Set läuft auf Abruf und schreibt versionierte Reports. Diskrepanzen führen zu Korrekturen in Templates, Aggregations-Logik oder Quell-Daten. Befunde, die in der Edition nicht behoben werden können, sind in `verification/findings.md` namentlich dokumentiert. Architektur in [[architecture#Test-Strategie]].

## Zitierfähiger Datenstand

**Anforderung.** Der aktuelle Datenstand ist in der Fußzeile jeder Seite als Datum des letzten Commits im Pipeline-Repo sichtbar, in lesbarer Langform. Er ist damit der Stand der Quellen, nicht der Zeitpunkt des Build-Laufs.

**Begründung.** Eine Forscherin zitiert die Datenbank mit einem Datenstand; dieser muss sich an der Quelländerung orientieren, nicht am operativen Build. Sonst veraltet das Zitat zum nächsten Rebuild.

**Konsequenz.** Umsetzung in [[architecture#Datenstand aus dem Pipeline-Repo]], UI-Ausprägung in [[ui-design#Datenstand und Build-Datum]].

## Barrierefreiheit

**Anforderung.** Das UI ist mit Tastatur und Screen-Reader bedienbar und erfüllt die zentralen WCAG-2.1-AA-Kriterien.

**Konsequenz.** Sprachauszeichnung, Skip-Link, sichtbarer Tastatur-Fokus, semantische Landmark-Struktur, Heading-Hierarchie, ARIA-Live-Regions für dynamische Trefferzahlen, `aria-sort` auf sortierbaren Tabellenspalten, Focus-Trap und Return-Focus im Drill-down-Overlay, Hover-Hints auch über Tastatur-Fokus erreichbar, Kontrast-Tokens auf AA-Niveau, `prefers-reduced-motion` reduziert Animationen.

## Maximaler Informations-Output als Gestaltungsleitlinie

**Anforderung.** Das UI priorisiert Nachvollziehbarkeit vor reduzierter Darstellung.

**Begründung.** Fachnutzerinnen brauchen Herkunftsanzeigen an jeder Zahl. Eine Reduktion, die Herkunft verschleiert, ist für die wissenschaftliche Verwendung dysfunktional.

**Konsequenz.** Tooltips, Filterstatus und Zählebenen-Anzeige sind dauerhaft sichtbar. Ausführung in [[ui-design#Gestaltungshaltung]].

**Nicht gemeint ist**, dass Dichte Unübersichtlichkeit bedeutet. Die Oberfläche strebt hohe Informationsdichte mit klarer hierarchischer Gliederung an, nicht visuelles Rauschen.

---

# 5 Build, Repos und Wissensbasis

## Trennung Frontend-Repo und Pipeline-Repo

**Anforderung.** Build-Output liegt in einem eigenen Repository, getrennt vom Pipeline- und Template-Quellcode.

**Begründung.** Siehe [[architecture#Statische HTML-Ausgabe und Prototyp-Charakter]]. Die Trennung hält die Historie der Inhaltsänderungen übersichtlich und reduziert das Risiko, dass Output-Artefakte mit Quelländerungen verwechselt werden.

**Konsequenz.** HTMLs werden nicht direkt editiert. Änderungen gehen durch Rebuild.

## Obsidian-kompatibles Knowledge-Format

**Anforderung.** Die Wissensbasis liegt als flache Markdown-Dateien mit Wiki-Links vor, ohne Unterordner. [[index]] dient als Lesepfad-Einstieg.

**Begründung.** Die flache Struktur macht den Vault in Obsidian unmittelbar nutzbar. Build-Anleitungen leben in `README.md` und `CLAUDE.md`, nicht in der Wissensbasis.

## Zeitlose Formulierung der Wissensbasis

**Anforderung.** Die Dokumente der Wissensbasis sind zeitlos formuliert, mit Ausnahme von [[journal]].

**Begründung.** Konzepte, Anforderungen und Entscheidungen bleiben länger gültig als operative Einzelheiten. Ein Dokument, das mit einem konkreten Stichtag verknüpft ist, veraltet schneller und lädt zur Überarbeitung in die falsche Richtung ein.

**Konsequenz.** Keine Personennamen, keine Meeting-Datumsangaben, keine Quantitäten des Korpus. Ausnahme bleibt das journal.md als chronologisches Arbeitstagebuch.

---

## Siehe auch

* [[user-stories]] Forschungsszenarien, deren Einlösung diese Anforderungen tragen
* [[ui-design]] wie die Anforderungen gestalterisch umgesetzt sind
* [[architecture]] technische Realisierung von Build, Aggregaten, Provenienz, Verifikation
* [[data]] Datenbasis, Erschließungsformen, Datenebenen, Annotationsebenen
* [[glossar]] verwendete Begriffe
* [[journal]] chronologische Notizen zu Umsetzung und Stand
