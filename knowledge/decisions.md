---
title: Entscheidungen
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-02-19
updated: 2026-05-09
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Decision Records]]", "[[Architecture Decision Records]]"]
related: [requirements, architecture, ui-design, analyse, exploration]
---

# Entscheidungen

Getroffene Leitentscheidungen mit Begründung. Zeitlos formuliert. Pro Eintrag Entscheidung, Begründung und Konsequenz, optional eine Abgrenzung, was ausdrücklich nicht gemeint ist.

## Forschungsstand zitierbar via URL-Parameter

**Entscheidung.** Auf den Daten-Visualisierungs-Seiten (`/analysis/auswertungen.html`, `/exploration/zeitstrom.html`) wird der Filter-Stand in die URL-Suchparameter serialisiert und bei Page-Load von dort gelesen. Auswertungen führt `dec`, `sex`, `type`, `q`, `mode`; Zeitstrom führt `dec`, `stack`, `brush`, `focus`. Die Quellen- und Personen-Listenseiten haben das gleiche Pattern bereits.

**Begründung.** Eine Forscherin will einen Filter-Stand bookmarken, in eine Mail kopieren oder in einer Publikation zitieren. Ohne URL-Sync ist der eingestellte Filter beim Reload weg. Die Konsistenz mit Quellen + Personen schließt zusätzlich eine UX-Lücke.

**Konsequenz.** `history.replaceState` (kein History-Eintrag — Browser-Back soll nicht durch Filter-Mikrostände gehen). Empty-Default-Werte werden nicht in die URL geschrieben, damit Sharing-URLs minimal bleiben. URL-Sync ist während Page-Init deaktiviert (Guard `urlSyncActive`), sonst würden initiale Apply-Calls die URL leeren.

## Cross-Page-Sprung mit Filter-Übernahme

**Entscheidung.** Drill-down-Overlays (Auswertungen) und Brush-Drill (Zeitstrom) bieten einen „→ in Quellen-Liste öffnen"-Link. Der Link transferiert Zeitraum + Geschlechter-Filter (mappt auf das Quellen-Filter-Vokabular) in die Quellen-Listenseite. Page-spezifische Filter (Rolle, Beziehungstyp, Bezeichnung, Transaktionstyp, Stack-Fokus) werden nicht übertragen, weil die Quellen-Liste sie nicht kennt.

**Begründung.** Die Visualisierung weckt das Interesse, die strukturierte Quellen-Liste vertieft. Beide Seiten teilen sich Zeitraum und Geschlechter-Achse — die Übernahme ist verlustfrei für diese, ehrlich-lückenhaft für die anderen.

**Konsequenz.** `VizCore.buildDocumentsURL({decadeMin, decadeMax, sex})` baut die Cross-Nav-URL. Mapping ist asymmetrisch: `sex='f' → with-f`, `sex='m' → only-m` (Quellen kennt kein `with-m`).

## Wissenskorb als clientseitige Sammlung

**Entscheidung.** Forschende sammeln Quellen über Sitzungen hinweg in einem clientseitigen Wissenskorb (localStorage, Schlüssel `sugw-wissenskorb-v1`). „+"-Knöpfe stehen neben jedem Quellen-Eintrag in den Listen (Quellen-Tabelle, Auswertungs-Drill, Zeitstrom-Drill); ein Korb-Icon im Nav zeigt die Anzahl; eine eigene Korb-Seite (`/korb.html`) listet die Sammlung mit Remove- und CSV-Export-Aktion.

**Begründung.** Die identifizierten Forschungspfade (siehe [[exploration]] und [[analyse]]) springen häufig zwischen Übersicht und Detail. Eine sammelnde Schicht über mehreren Seiten erlaubt es, ein Forschungs-Korpus zusammenzustellen, ohne den Browser-Tab-Wildwuchs einer manuellen Bookmark-Strategie. Cross-Tab-Sync via `storage`-Event hält parallel offene Tabs konsistent.

**Konsequenz.** `wissenskorb.js` ist eine site-weite Komponente (in `base.html` geladen, Nav-Icon dort verankert). Schlüssel ist die zusammengesetzte ID `type:id` (aktuell nur `source` als Typ; Personen-Sammlung wäre eine spätere Erweiterung). Daten bleiben rein clientseitig — keine Server-Persistenz, keine Identitätspflicht; Export als CSV überträgt die Sammlung in Werkzeuge der Forschenden (Zotero, Excel, BibTeX-Konverter).

**Nicht gemeint ist** ein server-persistierter Account. Das wäre ein anderer Stack (Auth, DSGVO, Speicherkosten). Der clientseitige Korb ist bewusst der niedrigschwellige Einstieg.

## Titel und Untertitel

**Entscheidung.** Der Haupttitel der Datenbank lautet „Stadt und Gemeinschaft Wien", der Untertitel „Datenbank zu mittelalterlichen Rechtsgeschäften".

**Begründung.** Der Haupttitel ist in den Projektpublikationen etabliert. Eine abweichende Neubenennung würde Kontinuität mit bereits gedruckten Texten brechen. Der Untertitel ist deutsch, damit das UI sprachlich durchgängig bleibt und nicht ohne Anlass zwischen Deutsch und Englisch wechselt.

**Konsequenz.** Der Titel ist in Navigationsleiste, Seitentitel und Fußzeile konsistent zu führen.

## Exploration und Analyse als getrennte Bereiche

**Entscheidung.** Das UI führt zwei Navigationsbereiche nebeneinander: Analyse und Exploration. Die Trennung folgt dem Interaktionsmodus, nicht dem Inhalt.

- **Analyse** versammelt quantitative Auswertungen mit vorgegebener Achsensemantik: Verteilungen (Donut, Bar-Chart, Tabellen mit Prozentwerten) und Template-Abfragen mit typisierten Slots. Nutzerinnen kommen mit einer Frage und bekommen Zahlen plus Provenienz.
- **Exploration** ist visuell-interaktive Erkundung der Datenstruktur selbst: Personen-Netzwerke, Karten, Timeline-Bänder, Sankey-Diagramme. Nutzerinnen kommen ohne klare Frage und entdecken Pattern in der Visualisierung.

**Begründung.** Donut, Bar-Chart und Verteilungstabellen sind nach DH-Standard analytische Visualisierung — sie zeigen vorberechnete Statistik. Force-Layouts, Karten und Sankey-Diagramme sind Information-Visualisation für offene Erkundung. Die Erwartungshaltung der Nutzerinnen unterscheidet sich entsprechend: „Auswertung" suggeriert quantitative Antwort, „Exploration" visuelles Stöbern. Die Pfade folgen dieser Semantik.

**Konsequenz.** Unter `/analysis/` liegen `auswertungen.html` (Statistik-Verteilungen) und `index.html` (Abfragen). `/exploration/` ist für künftige visuelle Views reserviert (Personen-Netzwerk, Karten, Timeline) und enthält aktuell keine Inhalte. Die Navigation bündelt beide Analyse-Seiten in einem Dropdown „Analyse"; Exploration erscheint dort, sobald die ersten visuellen Views fertig sind. Siehe [[ui-design#Navigation]] und [[ui-design#Zwei Modi nebeneinander]].

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

**Konsequenz.** Alle UI-Labels, Filter- und Achsenbeschriftungen verwenden „Gesamtnennungen" oder „Individuelle Personen". Siehe [[glossar#Gesamtnennung]]. Welche der beiden Zählebenen einer konkreten Zahl zugrunde liegt, muss an jeder Zahl per [[ui-design#Provenienz-Tip und Glossar-Tip]] erkennbar sein. Ein Label, das eine Zahl fälschlich der anderen Zählebene zuordnet, ist ein Fehler im Sinne von [[requirements#Datenrobustheit und Provenienz]] und wird von [[architecture#Verifikations-Test-Set]] sichtbar gemacht.

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

Wer Nennungen für Häufigkeitsstatistiken oder Belegdichten zählt, will explizit Quellentext-Erwähnungen aktueller Geschäfte — nicht Hilfsverknüpfungen oder Querverweise. Das Altsystem (PHP/MariaDB-Frontend) zählt aus genau diesem Grund mit beiden Filtern. Eine inklusive Zählung erzeugt Diskrepanzen zu publizierten Statistiken und verzerrt die Häufigkeitsbilder einzelner Personen.

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

Diese Asymmetrie ist im Altsystem etabliert und semantisch konsistent: Eine Person, die nur als Querverweis in einer einzigen Quelle erscheint, ist trotzdem im Register vermerkt (und damit zählbar als Individuum), aber sie hat keine *eigene* Quellenpräsenz, die in Nennungs-Statistiken aufscheinen sollte.

**Konsequenz.** `frontend/build.py::_scan_released_tei` führt zwei XPath-Pässe pro Datei: `_XP_PERSONS_ALL` für Distinct-Zählung und Sex-Splitt; `_XP_PERSONS_EXCL_MENTIONED` für die Nennungszählung. Die Asymmetrie ist im Glossar-Eintrag [[glossar#Individuelle Person]] und in den Provenienz-Tooltips auf der Startseite explizit benannt.

## KPIs werden direkt aus TEI via XPath gerechnet

**Entscheidung.** Alle Release-KPIs der Startseite (Quellen, Quellen mit Personen, individuelle Personen, Nennungen, Rechtsgeschäfte, Korpus-Matrix) werden im Frontend-Build direkt aus den freigegebenen TEI-Quellen mit lxml und einem dokumentierten XPath gerechnet. CSV-Outputs der Pipeline werden für diese Zahlen nicht herangezogen.

**Begründung.** Das Stakeholder-Leitprinzip aus Meeting 17.04. fordert: *Jede dargestellte Zahl ist nur dann wissenschaftlich verwendbar, wenn ihre Provenienz transparent, ihre Berechnungsoperation dokumentiert und ihr Ergebnis durch das Fachteam selbstständig reproduzierbar ist.* Eine zweistufige Aggregation (TEI → Pipeline-CSV → Frontend) erzeugt eine Zwischenebene, an der Definitionen subtil abweichen können (Beispiel: die Pipeline-Spalte `kind_of_linking` mappt auf TEI-Annotationen, ist aber nicht 1:1 identisch mit der semantischen Frage „erscheint Person X im Quellentext"). Direkter XPath auf TEI ist die kürzeste, prüfbarste Operation und in den Tooltips wörtlich abgedruckt — eine Verifikation reicht aus, um eine Zahl zu reproduzieren.

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

**Nicht gemeint ist**, dass die Information über mentioned Events verloren geht. Sie bleibt in `event_mentions.csv` und kann zusätzlich angezeigt werden — etwa über einen Toggle „Rechtsgeschäfte inkl. mentioned Events", wie ihn das Altsystem kennt. Dieser Toggle ist eine Anzeige-Option, nicht der Standardwert.

## Begriff Quellenkorpus

**Entscheidung.** Die oberste Gruppierungsebene der Datenbasis heißt „Quellenkorpus", nicht „Sammlung".

**Begründung.** „Sammlung" suggeriert einen kuratorischen Akt, den der Bestand so nicht erfahren hat. „Quellenkorpus" ist der fachhistorisch präzisere Begriff und wird in den Projektpublikationen durchgehend verwendet.

**Konsequenz.** Labels, Filter und Seitentitel sprechen von Quellenkorpus. Siehe [[glossar#Quellenkorpus]].

## Freigegebener Zeitraum

**Entscheidung.** Das UI zeigt den Zeitraum 1177 bis 1412, mit einer Ausnahme bis 1414 für QGW II/1 und QGW II/2.

**Begründung.** Nur freigegebene Regesten werden im Frontend angezeigt. Andere Werte in anderen Ansichten (etwa 1524 oder 1520) waren fehlerhafte Ableitungen aus unbereinigten Quellen.

**Konsequenz.** Zeitregler und Anzeigen verwenden diesen Bereich. Abweichungen gelten als Fehler.

## Formulierung „noch nicht ausgewertet"

**Entscheidung.** Der Zeitraum 1418 bis 1447 wird als „noch nicht ausgewertet" bezeichnet, nicht als „Überlieferungslücke".

**Begründung.** Die Überlieferung existiert. Nur die redaktionelle Auswertung steht aus. Die frühere Formulierung war sachlich falsch und wäre in einer wissenschaftlich verwendbaren Datenbank nicht haltbar.

**Konsequenz.** Der Begriff ist an allen sichtbaren Stellen konsequent zu verwenden.

## Register-Freigabe

**Entscheidung.** Alle drei Register (Personen, Organisationen, Orte) sind öffentlich. Jede Entität mit mindestens einer Nennung in einer freigegebenen Quelle erhält eine eigene Detail-Seite.

**Begründung.** Die Pipeline liefert für alle drei Entitätstypen konsistente Daten (Stammdaten, Quellenverweise, Beziehungen). Eine Detail-Seite pro Entität macht die Annotations-Substanz prüfbar und gibt Cross-Links zwischen Quelle, Person, Organisation und Ort eine sichtbare Heimat. Eine spätere Qualitätsverbesserung der Org- und Ortsdaten bleibt möglich und betrifft nur die Datengrundlage, nicht die Publikationsschicht.

**Konsequenz.** Listen-Seiten liegen unter `register/persons.html`, `register/orgs.html`, `register/places.html`. Detail-Seiten unter `register/persons/<pe__id>.html`, `register/orgs/<org__id>.html`, `register/places/<pl__id>.html`. Inline-Annotationen (`<rs type="org">`, `<rs type="place">`) im Quellen-Volltext verlinken auf die jeweilige Detail-Seite.

**Geo-Information.** Orte erhalten textuelle Geo-Felder (Adresse, Parzelle, Koordinaten als Rohzahl, GeoNames-Link). Es wird kein Karten-Widget gerendert: Orts-Aussagen liegen außerhalb des Forschungsfokus, eine Karte würde eine analytische Tiefe suggerieren, die das Register nicht trägt. Der GeoNames-Link bleibt das einzige Sprungziel zur räumlichen Verortung.

## Trennung Frontend-Repo und Pipeline-Repo

**Entscheidung.** Build-Output liegt in einem eigenen Repository, getrennt vom Pipeline- und Template-Quellcode.

**Begründung.** Siehe [[architecture#Trennung Quelle und Build-Output]]. Die Trennung hält die Historie der Inhaltsänderungen übersichtlich und reduziert das Risiko, dass Output-Artefakte mit Quelländerungen verwechselt werden.

**Konsequenz.** HTMLs werden nicht direkt editiert. Änderungen gehen durch Rebuild.

## Obsidian-kompatibles Knowledge-Format

**Entscheidung.** Die konzeptionelle Wissensbasis liegt als flache Markdown-Dateien mit Wiki-Links vor, ohne Unterordner und ohne Nummernpräfixe. Eine einzige Strukturdatei ([[index]]) dient als Lesepfad-Einstieg und Wegweiser; sie trägt keine inhaltliche Substanz.

**Begründung.** Die flache Struktur macht den Vault in Obsidian unmittelbar nutzbar und senkt die Einstiegshürde für Mit-Autorinnen. Ein klassisches README mit Build-Anleitungen oder Repo-Setup gehört nicht in die Wissensbasis — solche Inhalte leben in `README.md` und `CLAUDE.md` im Repo-Root. Eine Lesepfad-Datei ist demgegenüber selbst Wissensdokument: sie sagt, in welcher Reihenfolge die Konzepte aufeinander aufbauen und wo welcher Begriff kanonisch definiert ist.

**Konsequenz.** Dokumente im `knowledge/`-Ordner folgen dieser Struktur. Verlinkung geschieht über Wiki-Syntax, nicht über Markdown-Referenzen.

## Verifikations-Test-Set als eigenständige Komponente

**Entscheidung.** Neben der Pipeline existiert ein unabhängiges Verifikations-Test-Set, das die TEI-Quellen und Register-XMLs eigenständig einliest, die Aggregate nachrechnet und gegen die vom Build erzeugten JSON-Ausgaben legt.

**Begründung.** Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht. Die Frage, ob ein Label an einer Zahl semantisch korrekt ist, lässt sich nur beantworten, wenn eine zweite, unabhängige Rechnung sie bestätigt. Die Implementierung in Python mit `lxml` vermeidet CSV-Zwischenstufen und trifft auf die Quelle direkt.

**Konsequenz.** Das Test-Set läuft auf Abruf und schreibt versionierte Reports. Diskrepanzen führen zu Korrekturen in Templates, Aggregations-Logik oder Quell-Daten. Gleichzeitig dient dieselbe Aggregations-Logik als Fundament für die [[#Provenienz als inline Drill-down in den Aggregat-JSONs]], weil beide dieselben Zählungen auf derselben Quellebene nachvollziehen. Siehe [[architecture#Verifikations-Test-Set]].

## Provenienz als inline Drill-down in den Aggregat-JSONs

**Entscheidung.** Die Provenienz einer aggregierten Zahl — also die Liste der Quelldokumente, die sie stützen — lebt als `drill_down`-Unterstruktur **innerhalb** der jeweiligen Aggregat-JSON, nicht als separate Datei.

**Begründung.** Die meisten aggregierten JSONs tragen die Provenienz-Information bereits als inline Drill-down (role × sex → file_keys, relation type × sex → file_keys, transaction type × decade → file_keys, place → file_keys). Eine separate Parallel-JSON-Struktur wäre Duplikation derselben Information. Die inline Form hält Aggregat und Provenienz zusammen, ohne dass ein Frontend-Reader zwei Dateien korrelieren muss.

**Konsequenz.** Jeder Aggregat-JSON enthält einen `drill_down`-Abschnitt mit dem gleichen Schlüsselmuster wie die Counter-Werte, aber mit sortierten Listen von `file_key`-Verweisen statt Zahlen. Das Frontend löst einen Tooltip durch Lookup im gleichen JSON auf, ohne zusätzliches Nachladen. Die Zielkonsumption für das `file_key` ist `data/docs_lookup.json`, das jeden Schlüssel auf URL, Regest und Metadaten abbildet. Siehe [[requirements#Datenrobustheit und Provenienz]] und [[ui-design#Provenienz-Tip und Glossar-Tip]].

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

- [[requirements]] Anforderungen, aus denen die Entscheidungen folgen
- [[ui-design]] gestalterische Umsetzung
- [[journal]] chronologischer Pfad, auf dem Entscheidungen entstanden sind
