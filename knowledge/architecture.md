# Architektur

Bausteine der Edition und ihr Zusammenspiel. Konzeptionell, ohne Implementierungsdetails.

## Datenfluss

Der Datenfluss ist einsträngig. TEI-XML-Quellen werden durch eine Python-Pipeline in JSON- und CSV-Zwischenformate transformiert. Jinja2-Templates rendern daraus statische HTML-Dateien. Die fertigen Seiten werden über GitHub Pages ausgeliefert.

Jede Stufe ist für sich nachvollziehbar. Wer eine Aussage der Oberfläche anzweifelt, kann sie bis in die TEI-Quelle zurückverfolgen.

## TEI als Quelle

Die Quelldaten liegen in TEI-XML vor, dem etablierten Standard für die digitale Edition historischer Texte. Die Wahl ist nicht konjunkturell, sondern langfristig gedacht. TEI dokumentiert Text und Annotation in einem einzigen Dokument und bleibt auch nach dem Ende dieser Edition lesbar.

Die Annotationsebenen der Edition sind in [[data#Annotationsebenen]] beschrieben.

## Pipeline

Die Python-Pipeline leistet Validierung, Transformation und Aggregation. Sie prüft die Quellen gegen ein RelaxNG-Schema, normalisiert Attribute, parst Datumsangaben und erzeugt die Zwischenformate für das Rendering.

Die Wahl von Python mit lxml folgt aus zwei Gründen. Die Werkzeugkette kommt ohne Java-Abhängigkeiten aus. Und Regressionstests sind in Python leichter zu schreiben und zu pflegen als in klassischen XSLT-Pipelines.

## Datenschichten und Aggregator

Zwischen TEI-Quellen und Frontend-Views liegen drei aufeinander aufbauende Schichten. Die unterste Schicht sind die Pipeline-CSVs (Schwester-Repo), die die TEI-Auszeichnung in tabellarische Form bringen. Darüber schreibt der Aggregator im Edition-Repo (`frontend/aggregator.py`) konsolidierte JSON-Dateien nach `docs/data/`. Die oberste Schicht sind die View-spezifischen JSONs, die das Frontend zur Renderzeit zusammenstellt.

Der Aggregator ist die Stelle, an der Frontend-spezifische Schnitte entstehen, die nicht in die Pipeline gehören. Er joined Pipeline-CSVs (filenames, persons, persons_in_sources, events_in_sources) zu einem pro-Quelle-Record mit Counts, Geschlechter-Aufschlüsselung, Datumsnormalisierung und Annotations-Tiefe (`docs_aggregate.json`). Aus diesem Aggregat baut der Build den client-seitigen Suchindex `search.json`.

Der Vorteil dieser Trennung ist Wiederverwendbarkeit. Mehrere Frontend-Views (Tabelle, Detail, Exploration) lesen denselben Aggregat-Datensatz, statt jede ihre eigene TEI-Logik mitzuführen. Begründung und Reihenfolge der Joins sind in [[data#Aggregat-Schicht]] festgehalten.

Eine TEI-Änderung wirkt erst, wenn alle drei Schichten neu laufen: erst Pipeline (`python -m pipeline transform` im Schwester-Repo), dann Aggregator + Build (`python -m frontend build` hier).

## Verifikations-Test-Set

Parallel zur Pipeline existiert ein unabhängiges Test-Set im Edition-Repo. Es liest die TEI-Quellen und Register-XMLs ohne Umweg über die Pipeline-Zwischenformate ein, rechnet Aggregate eigenständig nach und vergleicht sie mit den JSON-Ausgaben, die das Frontend konsumiert. Abweichungen zwischen Test-Aggregat und JSON-Aggregat sind ein Signal, das entweder auf einen Pipeline-Fehler, eine Fehl-Beschriftung in Templates oder auf eine Datenlücke hinweist.

Das Test-Set nutzt dieselbe Technologie wie die Pipeline (Python, lxml), ist aber bewusst ein separater Codepfad ohne geteilte Aggregations-Funktionen. Die Trennung ist die Verifikationsgarantie: Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht.

Reports sind versioniert und menschen- wie maschinenlesbar. Begründung in [[decisions#Verifikations-Test-Set als eigenständige Komponente]].

## Templates

Die Oberfläche ist durch Jinja2-Templates definiert. Ein Basis-Template hält Navigation und Fußzeile zentral. Detail-Templates erweitern es um den jeweiligen Inhalt. Eine Änderung am Rahmen greift in allen Seiten, eine Änderung an einer Detailseite bleibt lokal.

## Statische HTML-Ausgabe

Die Edition wird als statische Website ausgeliefert. Jede Seite ist eine fertige HTML-Datei, die GitHub Pages ohne Server-Logik ausliefert. Dynamische Funktionen (Filter, Suche, Umschalter) laufen im Browser gegen vorgebaute JSON-Indexe.

Der Vorteil ist doppelt. Die Infrastruktur ist einfach und die einzelnen Seiten sind zitierbar, weil ihre URL langfristig stabil bleibt. Die Grenze liegt darin, dass sehr große oder stark wechselnde Daten besondere Indexierungsstrategien auf Client-Seite verlangen.

## Prototyp-Charakter

Die Edition ist ein Prototyp, kein produktionsreifes System. Architekturentscheidungen sind auf Iterationsgeschwindigkeit und Nachvollziehbarkeit optimiert, nicht auf Dauerbetrieb mit vielen Nutzerinnen.

Das heißt nicht, dass der Prototyp instabil wäre. Es heißt, dass Entscheidungen wie „keine Datenbank, keine Auth, keine serverseitige Logik" bewusst getroffen sind, weil sie in dieser Phase mehr Nutzen als Kosten bringen.

## Trennung Quelle und Build-Output

Templates und Build-Code liegen getrennt vom erzeugten Build-Output. Inhaltliche Änderungen gehören in die Quelle und werden durch einen Build-Lauf wirksam. Im Output-Ordner werden HTML-Dateien nicht direkt editiert, außer Meta-Dateien wie CLAUDE.md und der Wissensbasis im `knowledge/`-Ordner.

## Clientseitige Suche und Filter

Suche und Filter laufen im Browser gegen vorgebaute JSON-Indexe. Der Vorteil ist, dass keine Serverlogik betrieben werden muss und dass die Anfrage-URL zitierbar bleibt. Die Grenze liegt im Volumen. Sehr große Indexe belasten das Laden einer Seite und erfordern Teilindexe oder progressive Ladeverfahren.

## Auslieferung über statisches Hosting

GitHub Pages ist der Auslieferungskanal. Die Wahl ist kostenfrei, zuverlässig und versioniert. Die Unterordner-Struktur ist frei wählbar, case-sensitive und unterliegt keiner serverseitigen URL-Umschreibung.

## Grenzen der Architektur

Die statische Architektur leistet keine Echtzeit-Daten, keine persistierten Nutzereingaben und keine Authentifizierung. Das ist akzeptabel, weil die Edition Publikationsform ist, nicht kollaboratives Werkzeug. Wer an den Quelldaten arbeitet, tut das auf einer anderen Ebene als der, die die Edition bedient.

## Provenienz-Indizes

Jede aggregierte Kennzahl im Frontend ist auf die Menge der zugrundeliegenden Quelldokumente rückführbar. Die Rückführung geschieht als `drill_down`-Abschnitt innerhalb der Aggregat-JSONs, der zu jedem Kreuztabellen-Feld die sortierte Liste der beitragenden `file_key`-Verweise führt. Das Frontend löst die Provenienz durch Lookup im selben JSON auf, der die Zahlen liefert; zusätzliche Metadaten zum Einzeldokument kommen aus `data/docs_lookup.json`.

Konsequenz für den Build: jede Aggregations-Funktion füllt `drill_down` parallel zu den Counter-Werten. Begründung in [[decisions#Provenienz als inline Drill-down in den Aggregat-JSONs]], Umsetzung in [[ui-design#Provenienz-Tip und Glossar-Tip]].

## Quellenbereinigte Aggregation als Invariante

Das Zählen von Entitäten pro Quelle erfolgt mengenbasiert: die Extraktionsfunktion im Build liefert pro Quelldokument eine Menge referenzierter Entity-IDs, nicht eine Liste mit möglichen Duplikaten. Eine Person, Organisation oder ein Ort wird pro Quelle höchstens einmal gezählt, auch wenn die TEI-Auszeichnung sie im Text mehrfach markiert. Siehe [[decisions#Quellenbereinigte Zählung]] für die Begründung und [[glossar#Gesamtnennung]] für die begriffliche Konsequenz im UI.

Damit ist die Aggregation robust gegen Urteilslisten, Zeugenreihen und Formelwiederholungen, die eine ungereinigte Zählung verzerren würden.

## Datenstand aus dem Pipeline-Repo

Die Fußzeile der Edition führt einen **Datenstand**, der auf den letzten Commit des Pipeline-Repos verweist. Technisch ermittelt der Build das Commit-Datum per `git log -1 --format=%cI` im Pipeline-Repo-Root und formatiert es in lesbarer deutscher Langform. Der Datenstand ist damit nicht das Tagesdatum des Build-Laufs, sondern der Stand der Quellen, auf denen der Build beruht.

Getrennt davon bleibt das **Build-Datum** als Zeitstempel pro gerenderter Seite. Es markiert, wann die Einzelseite zuletzt neu gebaut wurde. Beide Angaben werden lesbar, nicht als ISO-Zeichenkette ausgegeben. Siehe [[ui-design#Datenstand und Build-Datum]].

## Siehe auch

- [[data]] was verarbeitet wird
- [[requirements]] welche Anforderungen die Architektur zu erfüllen hat
- [[ui-design]] wie die Bausteine zur Oberfläche werden
