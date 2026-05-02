# Journal

Arbeitstagebuch. Einziges chronologisches Dokument der Wissensbasis.

Format pro Eintrag: Überschrift mit Datum und Kurztitel, darunter eine knappe Notiz zum Fortschritt, zu Entscheidungspfaden, zu verworfenen Alternativen oder zu offenen Fragen. Verlinkt werden die Zieldokumente, nicht Personen oder Meetings.

Was hier rein darf: Fortschritt der Wissensbasis, Entscheidungspfade, die in [[decisions]] münden, verworfene Alternativen mit Begründung, offene Fragen, die beim Arbeiten auftauchen.

Was nicht rein darf: Personennamen, Meeting-Protokolle, Projektmanagement-Stand, Quantitäten des Korpus.

Einträge in umgekehrt chronologischer Reihenfolge, neueste oben.

---

## 2026-05-02 Tooltip-Komponenten getrennt, Toggle entfernt

Die Startseiten-Card „Quellen durchsuchen" wird konzeptionell aufgeräumt. Der Toggle „Erwähnte Geschäfte einbeziehen" über der Korpus-Matrix entfällt. Begründung: Die Matrix-Werte werden nicht mehr zwischen zwei Zählebenen umgeschaltet, sondern zeigen einheitlich die quellenbereinigte Default-Variante (Personen in verschachtelten rs-Events ausgeschlossen, vgl. [[glossar#Gesamtnennung]]). Die parallele Aggregator-Schicht für die inklusive Variante (`person_mentions_with_mentioned`, `distinct_events_with_mentioned`, der zweite XPath-Loop über alle rs-Events) ist damit ohne Konsumenten und wird aus `frontend/build.py` entfernt. Für eine zukünftige Wiedereinführung als globaler Zählebenen-Umschalter (vgl. [[requirements#Umschaltbarkeit der Zählebenen]]) gibt es einen sauberen Rebuild-Pfad — der Aggregator hat keinen verkrusteten Toggle-Zustand mehr.

Der Begriff **Event** bleibt im UI bewusst stehen, gegen den ersten Impuls, ihn durch „Rechtsgeschäft" zu ersetzen. Die `events_in_sources.csv` zeigt, dass die `<rs type="event">`-Annotation heterogen ist: 2.025 `abstract` (das eigentliche Regest), 1.565 `seal` (Siegelvermerke), 439 `entry` (Kanzleivermerke), 47 `nota`, plus 138 ohne Kategorie. Nur `abstract` deckt sich mit der Glossar-Definition von [[glossar#Rechtsgeschäft]]. „Rechtsgeschäft" als Spaltenlabel wäre für die Begleitelemente zu eng; „Event" ist der ehrlichere Sammelbegriff und respektiert das technische Vokabular der TEI-Annotation. Eine separate Aufschlüsselung pro `event_in`-Kategorie bleibt eine offene Designfrage für eine spätere Session.

Die Tooltip-Komponente wird in zwei eigenständige Varianten zerlegt, weil sie zuvor zwei verschiedene Aufgaben in einem Popover gemischt hat. **Glossar-Tip** (Macro `glossary_tip`): kompaktes `i`-Icon neben einem Begriff, öffnet die Begriffsdefinition mit Link zum Glossar. **Provenienz-Tip** (Macros `prov_stat` + `prov_popover`): an einer Zahl, gepunktet unterstrichen, öffnet den Verifikations-XPath und einen kurzen Hinweis zur Filterung. Beide Komponenten teilen die JS-Logik aus `provenance.js` (gleiche `data-prov-trigger`-Mechanik), unterscheiden sich aber in Trigger-Form und Inhalt. Auf der Startseite folgt die Korpus-Matrix dem Schema: jeder Spalten-Header trägt einen Glossar-Tip, die Gesamt-Zahlen in der `tfoot`-Zeile tragen einen Provenienz-Tip. Die Zellen pro Korpus bleiben einfache Zahlen, weil ihre Provenienz mit der Spalten-Summe übereinstimmt. Beim Ausrollen auf weitere Seiten (Exploration-Subpages, Datenqualität, Statistik — vgl. [[journal]]-Eintrag 2026-04-17) sollte das Schema konsistent gehalten werden: Glossar an Begriffen, Provenienz an Zahlen.

Begleitend wird der Provenienz-Popover-Container auf horizontale Edge-Detection erweitert. Beim Öffnen prüft `clampToViewport` in `provenance.js`, ob das Popover über `documentElement.clientWidth - margin` hinausragt, und kompensiert über `transform: translateX(...)`. Der Pfeil bleibt am ursprünglichen Trigger ausgerichtet via CSS-Variable `--prov-arrow-offset`. Ohne diesen Mechanismus war die Personenregister-Card am rechten Rand der Startseite betroffen.

Drei kleinere Refactors: (1) `var` → `let` projektweit über alle JS-Files in `frontend/static/js/`. Ein TDZ-Bug in `index.js` (`rangeSlider` wurde im Init-Callback gelesen, bevor `initRangeSlider()` zurückkehrte) wurde durch eine Forward-Deklaration `let rangeSlider;` am Funktionsanfang behoben. (2) Die Korpus-Matrix in `frontend/templates/startseite.html` zieht ihre Spalten-Configs (Label, Glossar-Definition, Verifikations-XPath, Provenienz-Note) aus einer Liste `_compute_matrix_columns()` in `build.py`. Eine zusätzliche Spalte braucht jetzt nur einen weiteren Eintrag in dieser Liste, kein dupliziertes Template-Markup. (3) Spalten-Header `Quellenkorpus` ergänzt, damit die erste Spalte der Matrix nicht mehr unbeschriftet ist.

---

## 2026-05-01 Analyse-Seite Richtung A umgesetzt und refactored

Die [[analyse|Analyse-Seite]] ist von der Slot-Workbench (Phase 1, Familien-Tab-Bar als oberste UI-Ebene) zu **Richtung A** umgebaut: kuratierte Frage-Galerie als Einstieg, einziges Result-Panel als zentrale Antwort-Bühne, Custom-Builder darunter im `<details>` für freie Slot-Kombinationen. Der Tab-Bar-Ansatz wurde verworfen, weil er Familien als oberste Mental-Model-Ebene aufzwang — die Galerie bietet stattdessen direkten Zugriff über die Forschungsfrage selbst.

Architektur-Entscheidung **Frage als first-class concept**: Eine Frage ist autonom (`{ id, group, text, dataFiles, viz, answer, resolveViz, resolveComparison, resolveDrillDown, coverage }`), nicht an eine Familie gebunden. Familien bleiben für den Custom-Builder relevant. Das entkoppelt die kuratierte Schicht von der Slot-Architektur.

Architektur-Entscheidung **drei Mini-Viz-Stufen**: Karten zeigen subtile 6 px Stacked-Bars, 28 px Sparklines, Top-3-Mini-Bars oder 2×2-Heatmaps; das Result-Panel zeigt vollwertige SVG-Renderings. Beide Stufen teilen sich die Renderer-Logik.

Architektur-Entscheidung **Permalinks doppelt**: `#q=<id>` für Galerie, `#f=<fid>&...` für Custom-Builder. Beide bidirektional serialisiert; Custom-Permalink öffnet das `<details>` automatisch. Permalink-Copy-Button mit Clipboard-API ersetzt den vorherigen reinen Anzeige-Hint.

Refactor-Pass danach: COVERAGE-Map konsolidiert vier nahezu identische Coverage-Funktionen, generischer `topN(source, n, opts)` ersetzt drei `topX`-Helfer, Label-Maps zentralisiert (Roles/Orgs/Tx), Driver in neun nummerierte Sub-Sections gegliedert, CSS auf Token-Aliases umgestellt, Mobile-Layout < 600 px ergänzt, `:focus-visible`-Outlines durchgängig. Stub-Familien 2–5 aus `analysis-families.js` entfernt (waren tot und irreführend).

Bekannte Folge-Lücken: Familien 2–5 sind als Galerie-Resolver implementiert, aber noch nicht als Custom-Builder-Slots. Korpus-Filter ist weiter aufgeschoben, weil die Galerie-Antworten Korpus-übergreifend formuliert sind. `RELEASED_PERIOD` aus Event-Datum dynamisch ableiten (CS-Feedback-Punkt 1.2) wartet weiter auf eine konflikt-freie Session mit dem Pipeline-Repo. Tests: 23 grün, davon 12 Aggregat-Konsistenz-Tests pro Frage, die Pipeline-Drift erkennen, bevor Nutzer:innen falsche Zahlen sehen.

---

## 2026-04-17 Terminologie-Konsolidierung, Erschließungsform, Provenienz-Ausrollung

Die UI-Terminologie wird durchgehend auf die kanonischen Begriffe aus [[glossar]] und [[decisions#Begriff Quellenkorpus]] gezogen. Alle benutzerseitig sichtbaren Vorkommen von „Dokument(e)" werden zu „Quelle(n)", „Rechtsakt(e)" zu „Rechtsgeschäft(e)", eine verbliebene „Sammlung"-Spaltenkopfzeile zu „Quellenkorpus". Technische Labels auf HTML-Ebene (ARIA-Attribute, CSS-IDs) bleiben unberührt, weil sie sich auf das HTML-Dokument als Trägerformat beziehen, nicht auf die Quelle der Edition.

Die [[data#Erschließungsformen|Erschließungsform]] eines Quellenkorpus ist im UI an den Quellenkorpus-Chips der Dokumenten-Übersicht sichtbar. QGW-Bestände tragen das Label „Regest + Faksimile", Stadtbücher tragen „Volltext". Die Zuordnung liegt als Build-Konstante `_transmission_form` vor und fliesst in die `collections`-Datenstruktur mit ein.

Die Provenienz-Tooltip-Komponente wird von den Startseiten-KPIs auf weitere Seiten ausgerollt: Exploration-Hub (Personen, Rechtsgeschäfte, Quellen), Personenregister (Gesamt-Einträge mit Hinweis auf quellenbereinigte Zählung pro Eintrag), Datenqualität (Quellen gesamt). Das Muster ist dasselbe wie auf der Startseite; die Popover-Inhalte verweisen jeweils auf die relevanten Glossar-Einträge und Dateipfade.

Offen für eigene Sessions:

- **Zählebenen-Umschalter [[requirements#Umschaltbarkeit der Zählebenen]].** Implementierungspfad: globaler Schalter in der Navbar oder Filter-Leiste, persistierter Zustand im `localStorage`, propagiert via `window.COUNT_MODE` an die Exploration-Skripte. Jeder Counter muss pro Zahl wissen, welche der beiden Ebenen er anzeigen kann; für die Mehrzahl der Exploration-Seiten bedeutet das eine parallele JSON-Struktur (oder zusätzliche Felder in den bestehenden `epic_*`-Dateien), die beide Ebenen vorhalten. Der Provenienz-Tooltip zeigt in jedem Popover den gewählten Modus.

- **Menschen-Events-Toggle [[ui-design#Menschen-Events-Toggle]].** Implementierungspfad analog: `window.INCLUDE_HUMAN_EVENTS`, persistiert, propagiert. Datenmodell-Seite: die Aggregatoren müssen Nennungen trennen, je nachdem ob sie aus einem primären Event stammen oder als Verweis auf ein früheres Event vorliegen. Voraussetzung ist eine belastbare Markierung im TEI-Datenstrom. Bei fehlender Markierung zeigt das UI den aktuellen stillschweigenden Zustand (Einschluss) offen, statt ihn zu verschleiern.

- **Bestandsfilter universell [[ui-design#Bestandsfilter]].** Derzeit wirkt der Filter nur auf der Quellen-Übersicht. Implementierungspfad: eine gemeinsame Filter-Komponente mit `window.CORPUS_FILTER` als Zustand, die alle Seiten beim Laden konsultieren. Die Seiten selbst müssen ihre Aggregate so aufbauen, dass sie auf beliebige Teilmengen der Korpora herunter-rechenbar sind. Für die Exploration-Skripte heisst das, dass die `epic_*`-JSONs zusätzlich eine korpusbasierte Unterschlüsselung tragen.

- **Analyse-Seite mit Template-Familien.** Blaupause in [[analyse]]. Umsetzung erfordert Fachteam-Entscheidung über die initiale Familienmenge. Technischer Pfad: clientseitige Template-Engine mit Slot-Parametern, Live-Counts aus den `epic_*`-Aggregaten, Drill-down über das bestehende `docs_lookup.json`.

Kleinere UX-Punkte, die ohne Phase-2-Abhängigkeit umgesetzt werden können:

- Multi-Select-Chips für den Quellenkorpus-Filter (mehrere Korpora gleichzeitig).
- Tag-Farbdifferenzierung für Rollen in der Einzelquellen-Ansicht.
- Mouse-over-Legenden in den Exploration-Visualisierungen, mit kurzen Erklärungen der Achsen und Kodierungen.
- F-Faktoid-Legende (Markierung weiblicher Faktoid-Gruppen in den Rollen-Ansichten).
- Archivinfos auf der Einzelquellen-Ansicht (Signatur, Bestand, Faszikel, sofern aus TEI-Header extrahierbar).

## 2026-04-17 Startseiten-Layout, Datenstand und offene Phase-2-Punkte

Die Startseite wird konzeptionell neu geordnet. Statt einer einzelnen Exploration-Sektion mit Trennstrich stehen zwei gleichberechtigte Säulen nebeneinander: Exploration (vier visuelle Zugänge) und Analyse (Einstieg zur Grundabfragen-Seite im Template-Familien-Stil von [[analyse]]). Eyebrow-Labels in Sans-Caps markieren die Bereiche ohne optischen Schwergewichte wie border-bottom. Die Entry-Cards (Quellen, Personenregister, Über das Projekt) tragen Icons in der Akzentfarbe. Die Farblogik stabilisiert sich: blau für Akzente (Icons, Labels, interaktive Elemente), schwarz für Inhaltstitel, gedämpftes Grau für Beschreibungstexte.

Der Footer trennt Datenstand und Build-Datum. Bis zuletzt zeigte „Datenstand" das Tagesdatum des Builds, was inhaltlich falsch ist. Der Datenstand ist nun das Datum des letzten Commits im Pipeline-Repo, ermittelt über `git log -1 --format=%cI` und in deutscher Langform ausgegeben. Die Hilfsfunktionen `_format_german_date` und `_pipeline_repo_data_date` liegen in `edition/build.py`. Die Dissertations-Zeile im Footer entfällt; sie war Projekthistorie, nicht Editionskontext.

[[glossar#Gesamtnennung]] wird präzisiert: die Zählebene ist quellenbereinigt, Mehrfacherwähnungen einer Person in derselben Quelle werden zu einer Nennung zusammengefasst. Die entsprechende Leitentscheidung liegt als [[decisions#Quellenbereinigte Zählung]] vor. Der Provenienz-Tooltip zur individuellen Person nimmt diese Schärfung auf.

Offen bleibt aus der Phase-2-Liste des CS-Feedbacks:

- **Zählebenen-Umschalter** zwischen Gesamtnennungen und Individuellen Personen in allen betroffenen Visualisierungen ([[requirements#Umschaltbarkeit der Zählebenen]]). Ohne diese Umschaltung zeigen Rollen- und Beziehungs-Ansichten nur eine Zählebene.
- **Menschen-Events-Toggle** ([[glossar#Menschen-Event]]): aktiv ein- und ausschließbar, konsistent durch alle abhängigen Darstellungen. Ohne Toggle ist der aktuelle Zustand stillschweigend ein Ausschluss, was Vergleiche über Visualisierungen erschwert.
- **Bestandsfilter universell** in allen Visualisierungen, nicht nur in den Quellen-Suchseiten. Sinnvoll, sobald Organisationen und Orte freigegeben sind.
- **Persistente Referenzierbarkeit / PID**: beschlossen, aber technische Ausprägung (w3id, ARK, Handle) braucht Stakeholder-Entscheidung. Siehe [[requirements#Zitierfähige Datenstände]].
- **Provenienz-Tooltip-Ausrollung** auf Register- und Exploration-Seiten. Die Komponente ist etabliert, der Einsatzort bisher auf Startseiten-KPIs beschränkt.

Außerhalb der Phase 2 stehen vereinzelte Daten-Anomalien im TEI-Bestand: Pseudo-Rollen außerhalb des kontrollierten Vokabulars, Sonderzeichen-URLs in docs_lookup.json, eine Witness-Anomalie in ausgewählten Quellen. Die Bereinigung läuft auf Seite der TEI-Annotation. Das Verifikations-Test-Set macht sie als `known_gap` sichtbar.

## 2026-04-17 Test-Set, Label-Korrektur und offengelegte Datenlücken

Im Edition-Repo entsteht ein eigenständiges Verifikations-Test-Set (Python, `lxml`). Es liest die TEI-Quellen und Register-XMLs des Pipeline-Repos unabhängig ein, rechnet Aggregate nach und vergleicht sie mit den JSON-Ausgaben unter `/data/`. Die Entscheidung dazu steht in [[decisions#Verifikations-Test-Set als eigenständige Komponente]].

Der Erstlauf liefert drei belastbare Befunde.

Erstens: Register-Totals und Datum-Ranges stimmen exakt. Der Test bestätigt die Identität individueller Personen aus dem Register mit dem Count der Personen-Such-JSON.

Zweitens: Der Zahlenwert, der im UI als „Gesamtnennungen Personen" beschriftet war, ist tatsächlich die Anzahl individueller Personen, nicht die der Nennungen. Das Label war falsch und wurde korrigiert zu „individuelle Personen". Siehe [[decisions#Begriff Gesamtnennungen]] und [[glossar#Individuelle Person]].

Drittens: Ein Quellenkorpus-Teilbestand erscheint in den Aggregaten des Frontends, hat aber keine TEI-Quelle im Pipeline-Repo. Die Zahlen im Frontend beruhen für diesen Teilbestand nur auf einer CSV-Zwischenstufe. Die Offenlegung ist eine Konsequenz aus [[requirements#Datenrobustheit und Provenienz]]. Die Entscheidung, wie mit dieser Lücke umgegangen wird (Datenergänzung, Sichtbarmachung als eingeschränkte Provenienz oder Ausblendung), steht aus.

Parallel werden im TEI Pseudo-Rollen sichtbar, die weder im kontrollierten Rollenvokabular vorgesehen sind noch interpretativ Bedeutung haben. Sie entstehen aus Annotationsfehlern und werden im Test-Report als solche markiert. Die Bereinigung läuft auf Seite der TEI-Annotation, nicht in der Pipeline.

## 2026-04-17 URL-Refactor und deutsche UI

Die flache Root-Struktur des Edition-Repos wird auf semantische Unterordner umgebaut: `register/`, `exploration/`, `analysis/`, `project/`. Die Umstellung betrifft Navigation, Build-Output und JavaScript-Lader, die die JSON-Indexe künftig über ein zentral gesetztes `window.ROOT_PATH` adressieren. Damit funktioniert die Edition auch aus Unterordner-Tiefe heraus, ohne dass Pfade zu absoluten Web-Pfaden mutieren.

Die UI-Oberfläche wird durchgängig auf Deutsch gezogen. Englisch bleibt in Pfaden und im Code. Der Untertitel lautet jetzt „Datenbank zu mittelalterlichen Rechtsgeschäften". Siehe [[decisions#Titel und Untertitel]].

Quantitätsbezogene Angaben (Zeiträume, unausgewertete Perioden, Korpus-Zählwerte) werden aus Templates entfernt und an eine zentrale Konfigurationsdatei im Pipeline-Repo gebunden. Hardcoded Zahlen in Templates gelten ab jetzt als Fehler.

## 2026-04-17 Entstehung der Wissensbasis

Anlass war die Einarbeitung von Feedback zum Frontend. In der ersten Iteration wurde die Wissensbasis als Obsidian-kompatibler Markdown-Ordner angelegt. Pro Dokument gilt zeitlose Formulierung ohne Projektmanagement-Artefakte und ohne Quantitäten des Korpus. Siehe [[decisions#Zeitlose Formulierung der Wissensbasis]].

Verworfen wurde ein README und eine Unterordner-Gliederung. Grund ist, dass die flache Struktur den Vault in Obsidian unmittelbar nutzbar macht und die Einstiegshürde senkt.

Für das Glossar wurde ein Kriterium festgelegt. Aufgenommen werden nur Begriffe, die im UI erscheinen und ohne Definition zu Missverständnissen führen. Selbsterklärende Alltagsbegriffe wie „Ehepaar" oder „Witwe" bleiben draußen. Aufgenommen bleibt „Rechtsgeschäft", weil es der Gegenstand der Datenbank ist und seine Abgrenzung zu [[glossar#Event]] im UI-Kontext präzise sein muss.

Offen: die konkrete Liste der Grundabfragen im Bereich Analyse. Sie wird mit dem Fachteam festgelegt und lebt vermutlich als eigener Bereich unter [[analyse]] weiter.
