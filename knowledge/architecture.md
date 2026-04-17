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

## Siehe auch

- [[data]] was verarbeitet wird
- [[requirements]] welche Anforderungen die Architektur zu erfüllen hat
- [[ui-design]] wie die Bausteine zur Oberfläche werden
