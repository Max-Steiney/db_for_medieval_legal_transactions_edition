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

Konsequenz für den Build: jede Aggregations-Funktion füllt `drill_down` parallel zu den Counter-Werten. Begründung in [[decisions#Provenienz als inline Drill-down in den Aggregat-JSONs]], Umsetzung in [[ui-design#Provenienz-Tooltip]].

## Siehe auch

- [[data]] was verarbeitet wird
- [[requirements]] welche Anforderungen die Architektur zu erfüllen hat
- [[ui-design]] wie die Bausteine zur Oberfläche werden
