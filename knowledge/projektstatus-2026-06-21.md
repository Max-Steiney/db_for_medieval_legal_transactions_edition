# Stadt und Gemeinschaft Wien, Datenbank zu mittelalterlichen Wiener Rechtsgeschäften

**Projektbericht für die Projektpartner**
Christopher Pollin, Digital Humanities Craft OG. Stand 21.06.2026.

Dieser Bericht beschreibt die Datenbank als laufendes System. Er erklärt, was sie ist und enthält, was sie kann, wie sie aufgebaut ist, wie neue Daten und Texte hineinkommen, wie daraus die Website entsteht und wie sie veröffentlicht wird. Am Schluss steht, woran derzeit gearbeitet wird und was von eurer Seite noch gebraucht wird. Der Bericht ist allgemeinverständlich gehalten, Fachbegriffe sind am Ende im Glossar erklärt.

## Was die Datenbank ist

Die Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte aus den Quellen der Stadt Wien, mit Schwerpunkt auf Personen, ihren Funktionsrollen und ihren Beziehungen. Sie ist eine eigenständige wissenschaftliche Publikation der annotierten Quellen und macht zugleich die zugrunde liegende Datenaufbereitung nachvollziehbar.

Technisch ist sie eine reine Website ohne Server und ohne Login. Sie wird automatisch aus den aufbereiteten Quellen erzeugt und über GitHub Pages bereitgestellt.

- Live-Website: https://chpollin.github.io/db_for_medieval_legal_transactions_edition/

## Was die Datenbank enthält

Die Inhalte sind in Quellenbeständen organisiert, die sich in Zeitraum, Herkunft und Erschließungsform unterscheiden.

Öffentlich sichtbar ist derzeit ein Bestand, die Quellen zur Geschichte der Stadt Wien (QGW) für den Zeitraum 1177 bis 1414. In der internen Arbeitsversion sind zusätzlich die Stadtbücher Band 1 und das Satzbuch CD enthalten sowie die Auswertungen und die interaktiven Ansichten.

Aus diesen Beständen erschließt die Datenbank vier aufeinander aufbauende Ebenen, den Quellenbestand, die einzelne Quelle, das einzelne Rechtsgeschäft und die einzelne Nennung einer Person oder Organisation. Personen und Organisationen sind in zwei durchsuchbaren Registern zusammengeführt, jeweils mit einer eigenen Profilseite.

## Die Funktionen im Überblick

Zu jeder Funktion steht der aktuelle Stand in Klartext, also fertig, in Arbeit, wartet auf eure Vorgabe oder mit euch zu klären.

### Startseite

Einstieg mit einer Übersicht der Bestände und den wichtigsten Kennzahlen.
Stand: fertig. Offen sind nur die einleitenden Texte, siehe Abschnitt „Was noch von euch kommt".

### Quellen-Liste mit Filtern

Eine durchsuchbare Liste aller Quellen. Die Suche greift auf Signatur, Datum, Ort und Regest zu. In der Seitenleiste lässt sich die Liste nach Bestand, Zeitraum und Geschlecht der Beteiligten einschränken.
Stand: fertig. Aus dem letzten Durchgang umgesetzt, der Ausstellungsort ist aus der freien Volltextsuche genommen und bleibt über den eigenen Ort-Filter erreichbar, die nicht aussagekräftigen Filter (Erschließungsform, Faksimile) sind entfernt, der Filter „Geschlecht der Beteiligten" ist klarer benannt, ein doppelter Tooltip im Zeitraum-Diagramm ist behoben.

### Quellen-Detailseite

Zeigt eine Quelle mit Regest, Volltext (soweit vorhanden), Annotationen und dem Digitalisat. Das Digitalisat lässt sich vergrößern, verschieben, drehen und im Vollbild anzeigen, und es bleibt beim Scrollen sichtbar. Die Annotationen sind in einer aufgeräumten Tabelle zusammengefasst, in der erwähnte Personen mit ihrem aufgelösten Namen erscheinen.
Stand: fertig. Technische Kennungen sind aus der öffentlichen Anzeige entfernt und bleiben nur im Hintergrund für die Zitierbarkeit erhalten.

### Personen- und Organisations-Register

Zwei durchsuchbare Verzeichnisse. Jeder Eintrag führt zu einer Profilseite mit Stammdaten, Beziehungen und einer Tabelle der Quellen, in denen die Person oder Organisation vorkommt.
Stand: fertig. Die Funktionsrollen sind durchgängig geschlechtergerecht und einheitlich beschriftet (Aussteller:in, Empfänger:in, Zeug:in / Siegler:in, Sonstige).

### Datenkorb

Eine Sammelmappe, in die Nutzer Quellen, Personen und Organisationen ablegen und als Tabelle exportieren. Sie liegt lokal im Browser, ohne Login und ohne Server.
Stand: fertig. Die Anzeige oben rechts schlüsselt den Inhalt nach Typ auf, ein Knopf leert den ganzen Korb. Ein Erklärtext zur Funktionsweise ist ergänzt.

### Auswertungen

Quantitative Verteilungen, etwa nach Rolle, Geschlecht, Datierung und Organisationstyp, als Diagramme und Tabellen.
Stand: in Arbeit, derzeit nur in der internen Version. Mit euch zu klären ist, ob die Herkunft der ausgewerteten Kategorien sichtbar gemacht wird, also wer eine Klassifikation verantwortet und was noch nicht eingeordnet ist.

### Exploration

Zwei visuell-interaktive Ansichten. Der Zeitstrom zeigt die zeitliche Verteilung als gestapeltes Balkendiagramm. Das Personennetzwerk zeigt das Beziehungsgeflecht um eine ausgewählte Person oder Organisation.
Stand: in Arbeit, derzeit nur in der internen Version. Mit euch zu klären ist, ob diese Ansichten öffentlich werden.

### Abfragen

Ein Werkzeug, mit dem sich Konstellationen von Beteiligten suchen lassen, etwa alle Rechtsgeschäfte mit einer bestimmten Rolle und Organisation.
Stand: in Arbeit, derzeit nur in der internen Version.

## Wie die Datenbank aufgebaut ist

Die Datenbank besteht aus zwei getrennten Teilen, die in zwei getrennten GitHub-Repositorien liegen.

Im Datenteil liegen die ausgezeichneten Quellen im TEI-Format, dem internationalen Standard für historische Texte, dazu die redaktionellen Listen. Eine Aufbereitungsstrecke liest diese Quellen und erzeugt daraus geordnete Tabellen.

Im Website-Teil liegt der Baumechanismus, der aus den Tabellen und den redaktionellen Texten die fertige Website erzeugt, dazu die fertige Website selbst. Was im Internet steht, ist immer dieser gebaute Stand, nicht die Quelldateien.

Der Weg ist also immer derselbe, ausgezeichnete Quelle, Aufbereitung, Bau der Website, Veröffentlichung. Kein Schritt davon ist Handarbeit an der fertigen Seite. Das hält die Datenbank reproduzierbar, jede Seite lässt sich jederzeit aus den Quellen neu erzeugen.

## Wie neue Daten und Bestände hineinkommen

Die Auszeichnung der Quellen und die Register-Pflege passieren immer im Datenteil, dem Repository `db_for_medieval_legal_transactions`. Dieses Website-Repository rendert nur. Die Befehlsblöcke unten sind die technische Anleitung für die Person, die den Bau ausführt. Wer nur den Ablauf verstehen will, kann sie überspringen.

### Ein einzelnes Dokument in einen bestehenden Bestand aufnehmen

Die ausgezeichnete TEI-Datei wird im Datenteil unter `sources/<Bestand>/<Unterbestand>_ready/done/<Nummer>.xml` abgelegt. Nur Dateien im Ordner `done/` werden gerendert, alles andere bleibt absichtlich außen vor. Neue Personen, Organisationen oder Orte, auf die die Datei verweist, werden in die Register `indices/personList.xml`, `orgList.xml` und `placeList.xml` eingetragen (ID-Präfixe `pe__`, `org__`, `pl__`). Dann wird geprüft, die Daten werden neu erzeugt und die Website gebaut.

```
cd ../db_for_medieval_legal_transactions
python -m pipeline validate      # prueft, dass alle Verweise aufloesen
python -m pipeline transform     # Daten neu erzeugen
cd ../db_for_medieval_legal_transactions_edition
python -m frontend build         # Website neu bauen -> docs/
```

Liegt der Bestand in der öffentlichen Auswahl, erscheint die Quelle danach automatisch auch öffentlich, ohne weitere Einstellung.

### Einen neuen Bestand anlegen und freigeben

Die Quellen werden wie oben unter `sources/<Bestand>/<Unterbestand>_ready/done/` abgelegt. Damit der Bestand überhaupt in Zählungen, Register und Übersichten einfließt, wird sein Pfad in die Freigabeliste eingetragen. Soll er zusätzlich öffentlich erscheinen, kommt er auch in die öffentliche Auswahl.

- Freigeben (intern sichtbar): Pfad `"<Bestand>/<Unterbestand>_ready"` zu `RELEASED_CORPORA` in `../db_for_medieval_legal_transactions/pipeline/config.py` ergänzen.
- Öffentlich: denselben Pfad zusätzlich zu `PUBLIC_CORPORA` in `frontend/config.py` ergänzen.
- Liegt der Bestand außerhalb des bisher erfassten Zeitraums, `RELEASED_PERIOD` in `frontend/config.py` anpassen.

Danach derselbe Bau wie oben.

```
cd ../db_for_medieval_legal_transactions
python -m pipeline validate
python -m pipeline transform
cd ../db_for_medieval_legal_transactions_edition
python -m frontend build
```

Für die Sichtbarkeit gilt durchgängig eine klare Regel. Öffentlich erscheinen nur fertige, freigegebene Bestände. Die interne Arbeitsversion kann zusätzlich unfertige Bestände zeigen, damit an ihnen gearbeitet werden kann, bevor sie veröffentlicht werden.

## Wie ihr Texte und das Glossar pflegt

Drei Seiten der Website werden nicht aus den Quellen erzeugt, sondern aus einfachen Textdateien, die ihr selbst pflegt, nämlich „Über das Projekt", das Glossar und das Impressum. Jede dieser Dateien ist in Markdown gehalten, einem schlichten Textformat ohne Programmierung. Eine Überschrift beginnt einen Abschnitt, der Text darunter ist der Inhalt.

Im Glossar ist ein Begriff ein Abschnitt. Die Überschrift ist der Begriff, der Absatz darunter die Definition. So lässt sich jeder Eintrag einzeln ergänzen oder ändern, ohne die übrigen zu berühren, und ein Begriff kann auf einen anderen verweisen. Ein ausgefüllter Beispieleintrag liegt bereits vor, die übrigen Begriffe tragen einen Platzhalter und warten auf eure Definition.

Bearbeitet wird direkt im GitHub-Repository, im Browser, ohne eigene Software. Eine kurze Anleitung dazu liegt neben den Textdateien im Repository.

Die drei Dateien liegen im Website-Repository unter `frontend/content/project/about.md` (Über das Projekt), `frontend/content/project/glossar.md` (Glossar) und `frontend/content/impressum.md` (Impressum). Einen Glossareintrag ändert man, indem man in `glossar.md` den Absatz unter der Begriffs-Überschrift bearbeitet oder einen neuen Abschnitt `## Begriff` anlegt, und dann die Website neu baut.

```
# im Website-Repository, nach dem Bearbeiten von glossar.md
python -m frontend build         # zieht den geaenderten Text in die Glossar-Seite -> docs/
```

## Wie die Website veröffentlicht wird

Damit eine Änderung sichtbar wird, muss die Website neu gebaut werden, weil im Internet der gebaute Stand liegt und nicht die bearbeitete Textdatei. Das Bearbeiten allein genügt also nicht, der Bau gehört dazu.

Der Bau selbst ist ein einzelner Befehl. Ohne Zusatz entsteht die öffentliche Fassung in `docs/`, die GitHub Pages ausliefert. Mit dem Zusatz `--audience intern` entsteht zusätzlich die interne Fassung in `docs-intern/`.

```
python -m frontend build                       # oeffentliche Fassung -> docs/
python -m frontend build --audience intern     # interne Fassung -> docs-intern/
```

Derzeit läuft dieser Bau bei Digital Humanities Craft und wird anschließend veröffentlicht. Geplant ist, den Bau direkt an das Speichern im Repository zu koppeln. Sobald ihr dann eine Textdatei bearbeitet und sichert, baut das System die Seite selbst und stellt sie nach kurzer Zeit online. In diesem Ausbau genügt das Bearbeiten im Browser, der gesonderte Bau-Schritt entfällt.

## Öffentliche und interne Sicht

Es gibt eine öffentliche und eine interne Version derselben Website. Die öffentliche Version zeigt nur fertige, freigegebene Bestände und lässt die noch in Arbeit befindlichen Bereiche aus. Die interne Version zeigt zusätzlich die unfertigen Bestände sowie die Auswertungen und die Exploration. Auf jeder Seite ist oben erkennbar, welche Version gerade angezeigt wird und von wann der Stand ist.

## Lizenz

Alle Inhalte stehen unter der Lizenz CC BY 4.0, also die Quellentexte und Annotationen, die aufbereiteten Daten und der Programmcode. Sie dürfen frei weiterverwendet werden, sofern die Herkunft genannt wird.

## Zitierhinweis

Zitiert wird nach dem Muster Autor, Titel (Jahr), dauerhafte Adresse. Für die Datenbank als Ganzes lautet die Angabe:

Christopher Pollin, ‘Stadt und Gemeinschaft Wien. Datenbank zu mittelalterlichen Wiener Rechtsgeschäften’ (2026), https://chpollin.github.io/db_for_medieval_legal_transactions_edition/.

Für eine einzelne Quelle treten deren Signatur und ihre dauerhafte Adresse an die Stelle der Gesamtadresse. Noch zu bestätigen ist, wer im Autor-Feld genannt wird, du allein oder zusammen mit den Editor:innen der Edition. Dieselbe Angabe steht im Impressum und muss dort denselben Autor tragen.

## Was noch von euch kommt

An einer Stelle wartet die Datenbank noch auf Inhalte, die nur von eurer Seite kommen können. Bis dahin steht dort ein Platzhalter.

- **Projekt-Texte**: die Texte für „Über das Projekt", die Definitionen im Glossar und das Impressum. *In Vorbereitung, von den Projektpartnern zu liefern.*

## Mit euch zu klären

Diese Punkte brauchen eine kurze Vorgabe, ändern aber nichts an der Funktion.

- Wer im Autor-Feld der Zitation genannt wird, siehe Zitierhinweis.
- An welcher Stelle im Interface das Wort „für" als Rollenbezeichnung stört. Ein Beispiel genügt.
- Ob bei der Angabe „im Quellen-Wortlaut" das Wort selbst oder der angezeigte Inhalt das Problem ist.
- Was der Leitsatz „wir sammeln nur alles, was wir haben" genau aussagen soll und ob das Folgen für die Darstellung hat.

## Glossar

- **Quellenbestand (Quellenkorpus)**: die oberste Gruppierung von Quellen, die sich in Zeitraum, Herkunft und Erschließungsform ähneln.
- **Quelle**: ein einzelnes überliefertes Schriftstück, also eine Urkunde oder ein Stadtbuch-Eintrag, das ein oder mehrere Rechtsgeschäfte dokumentiert.
- **Rechtsgeschäft**: die rechtliche Transaktion selbst, etwa Kauf, Stiftung, Verleihung oder Testament, die in einer Quelle festgehalten ist. Verbindliche Abgrenzung von den Editor:innen.
- **Event**: ein einzelnes Rechtsgeschäft als strukturierte Einheit innerhalb einer Quelle. In der Praxis trägt fast jede Quelle genau ein Event.
- **Nennung (Gesamtnennung)**: das Vorkommen einer Person in einer Quelle. Mehrfacherwähnungen in derselben Quelle zählen als eine Nennung.
- **Individuelle Person**: die einzelne, über alle Quellen hinweg zusammengeführte Person als Identität, unabhängig davon, in wie vielen Quellen sie genannt ist.
- **Rolle (Funktionsrolle)**: die Eigenschaft, in der jemand an einem Rechtsgeschäft beteiligt ist. Es gibt vier Werte (Aussteller:in, Empfänger:in, Zeug:in / Siegler:in, Sonstige).
- **Register**: das durchsuchbare Verzeichnis aller Personen beziehungsweise Organisationen. Jeder Eintrag ist eine zusammengeführte Identität mit eigener Profilseite.
- **Profil**: die Detailseite einer Person oder Organisation mit Stammdaten, Beziehungen und einer Tabelle der Quellen, in denen sie vorkommt.
- **Beziehung**: eine dokumentierte Verbindung zwischen Entitäten, nämlich Verwandtschaft, Freundschaft, Vertretung, Tätigkeit oder Titelverweis.
- **Erschließungsform**: die Art, wie eine Quelle editorisch aufbereitet ist. Sie bestimmt, welche Art von Aussage eine Quelle stützt. Vier Formen kommen vor (Regest, Siegel, Eintrag, Nota).
- **Regest**: eine redaktionelle Zusammenfassung des Quelleninhalts. Der volle Wortlaut ist nicht ausgeschrieben, aber im Digitalisat einsehbar.
- **Volltext**: der vollständig ausgeschriebene Wortlaut einer Quelle, der textgenaue Belege erlaubt.
- **Faksimile (Digitalisat)**: die fotografische Abbildung des Originals, im Viewer zoom-, verschieb- und drehbar.
- **Annotation**: die inhaltliche Auszeichnung im Quellentext, mit der Personen, Organisationen, Orte, Rollen und editorische Ergänzungen markiert sind.
- **Signatur**: die eindeutige Fundstelle einer Quelle, über die sie zitierbar und auffindbar ist.
- **Als verstorben genannt**: die Kennzeichnung, dass eine Person in der Quelle bereits als verstorben erwähnt wird. Das ergibt keinen exakten Sterbetag, sondern einen Zeitpunkt, vor dem sie gestorben ist.
- **Öffentliche Sicht**: die Live-Website, die nur fertige, freigegebene Bestände zeigt.
- **Interne Sicht**: die Arbeitsversion, die zusätzlich unfertige Bestände sowie Auswertungen und Exploration zeigt.
- **TEI**: der internationale Standard zur strukturierten Auszeichnung historischer Texte, in dem die Quellen kodiert sind.
- **Markdown**: ein schlichtes Textformat, in dem die redaktionellen Seiten (Glossar, „Über das Projekt", Impressum) ohne Programmierung gepflegt werden.
- **Aufbereitung (Pipeline)**: die automatische Strecke, die die TEI-Quellen einliest und in geordnete Tabellen überführt.
- **Bau (Build)**: der Schritt, der aus den aufbereiteten Tabellen und den redaktionellen Texten die fertige Website erzeugt.
- **Repository**: der versionierte Ablageort eines Projektteils auf GitHub. Datenteil und Website-Teil liegen in je einem eigenen Repository.
- **GitHub Pages**: der Dienst, der den gebauten Stand der Website im Internet bereitstellt.
