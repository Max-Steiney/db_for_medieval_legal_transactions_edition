# Stadt und Gemeinschaft Wien, Datenbank zu mittelalterlichen Wiener Rechtsgeschäften

**Projektbericht für die Projektpartner**
Christopher Pollin, Digital Humanities Craft OG. Stand 21.06.2026.

Dieser Bericht beschreibt, was die Datenbank ist, was sie enthält, wie man mit ihr arbeitet, wie neue Daten hineinkommen und woran derzeit gearbeitet wird. Er ist in allgemeinverständlicher Sprache gehalten. Fachbegriffe sind am Ende im Glossar erklärt.

## Was die Datenbank ist

Die Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte aus den Quellen der Stadt Wien, mit Schwerpunkt auf Personen, ihren Funktionsrollen und ihren Beziehungen. Sie ist eine eigenständige wissenschaftliche Publikation der annotierten Quellen und macht zugleich die zugrunde liegende Datenaufbereitung nachvollziehbar.

Die Datenbank ist eine reine Website ohne Server und ohne Login. Sie ist über das Internet erreichbar und wird automatisch aus den aufbereiteten Quellen erzeugt.

- Live-Website: https://chpollin.github.io/db_for_medieval_legal_transactions_edition/

## Was die Datenbank enthält

Die Inhalte sind in Quellenbeständen organisiert, die sich in Zeitraum, Herkunft und Erschließungsform unterscheiden.

Öffentlich sichtbar ist derzeit ein Bestand, die Quellen zur Geschichte der Stadt Wien (QGW) für den Zeitraum 1177 bis 1414. In der internen Arbeitsversion sind zusätzlich die Stadtbücher Band 1 und das Satzbuch CD enthalten sowie die Auswertungen und die interaktiven Ansichten.

Aus diesen Beständen erschließt die Datenbank vier Ebenen, die aufeinander aufbauen: den Quellenbestand, die einzelne Quelle, das einzelne Rechtsgeschäft und die einzelne Nennung einer Person oder Organisation. Personen und Organisationen sind in zwei durchsuchbaren Registern zusammengeführt, jeweils mit einer eigenen Profilseite.

## Die Funktionen im Überblick

Zu jeder Funktion steht der aktuelle Stand in Klartext: fertig, in Arbeit, wartet auf eure Vorgabe oder mit euch zu klären.

### Startseite

Einstieg mit einer Übersicht der Bestände und den wichtigsten Kennzahlen.
Stand: fertig. Offen sind nur die einleitenden Texte, siehe Abschnitt „Was noch von euch kommt".

### Quellen-Liste mit Filtern

Eine durchsuchbare Liste aller Quellen. Die Suche greift auf Signatur, Datum, Ort und Regest zu. In der Seitenleiste lässt sich die Liste nach Bestand, Zeitraum und Geschlecht der Beteiligten einschränken.
Stand: fertig. Aus dem letzten Durchgang umgesetzt: der Ausstellungsort ist aus der freien Volltextsuche genommen und bleibt über den eigenen Ort-Filter erreichbar; die nicht aussagekräftigen Filter (Erschließungsform, Faksimile) sind entfernt; der Filter „Geschlecht der Beteiligten" ist klarer benannt; ein doppelter Tooltip im Zeitraum-Diagramm ist behoben.

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

## Wie Daten und Bestände ins System kommen

Die Datenbank wird nicht von Hand befüllt, sondern aus aufbereiteten Quelldaten automatisch erzeugt. Es gibt zwei getrennte Teile. Im Datenteil liegen die ausgezeichneten Quellen und die redaktionellen Listen. Aus ihm wird der sichtbare Teil, die Website, neu gebaut.

Ein einzelnes Dokument kommt so hinzu: Die ausgezeichnete Quelle wird in den passenden Bestand des Datenteils eingestellt, dann wird die Website neu gebaut. Das Dokument erscheint danach in der Liste, im Register und auf seiner eigenen Detailseite, mit allen Verknüpfungen zu Personen und Organisationen.

Ein neuer Bestand kommt so hinzu: Der Bestand wird als eigene Gruppe im Datenteil angelegt und als freigegeben gekennzeichnet. Erst dann fließt er in Zählungen, Register und Übersichten ein.

Für die Sichtbarkeit gilt eine klare Regel. Öffentlich erscheinen nur fertige Bestände. Die interne Arbeitsversion kann zusätzlich noch unfertige Bestände zeigen, damit an ihnen gearbeitet werden kann, bevor sie veröffentlicht werden.

## Öffentliche und interne Sicht

Es gibt eine öffentliche und eine interne Version derselben Website. Die öffentliche Version zeigt nur fertige, freigegebene Bestände und lässt die noch in Arbeit befindlichen Bereiche aus. Die interne Version zeigt zusätzlich die unfertigen Bestände sowie die Auswertungen und die Exploration. Auf jeder Seite ist oben erkennbar, welche Version gerade angezeigt wird und von wann der Stand ist.

Dieser Bericht markiert bei jedem Beispiel-Verweis, ob er öffentlich erreichbar ist oder nur in der internen Version.

## Lizenz

Alle Inhalte stehen unter der Lizenz CC BY 4.0, also die Quellentexte und Annotationen, die aufbereiteten Daten und der Programmcode. Sie dürfen frei weiterverwendet werden, sofern die Herkunft genannt wird.

## Zitierhinweis

Zitiert wird nach dem Muster Autor, Titel (Jahr), dauerhafte Adresse. Für die Datenbank als Ganzes:

Christopher Pollin, ‘Stadt und Gemeinschaft Wien. Datenbank zu mittelalterlichen Wiener Rechtsgeschäften’ (2026), https://chpollin.github.io/db_for_medieval_legal_transactions_edition/.

Für eine einzelne Quelle treten deren Signatur und ihre dauerhafte Adresse an die Stelle der Gesamtadresse. Noch zu bestätigen ist allein, wer im Autor-Feld genannt wird, du allein oder zusammen mit den Editor:innen der Edition.

## Was noch von euch kommt

An einer Stelle wartet die Datenbank noch auf Inhalte, die nur von eurer Seite kommen können. Bis dahin steht dort ein Platzhalter.

- **Projekt-Texte**: die Texte für „Über das Projekt", die Definitionen im Glossar und das Impressum. *In Vorbereitung, von den Projektpartnern zu liefern.*

## Mit euch zu klären

Diese Punkte betreffen die Darstellung und brauchen eine kurze Vorgabe, ändern aber nichts an der Funktion.

- An welcher Stelle im Interface das Wort „für" als Rollenbezeichnung stört. Ein Beispiel genügt.
- Ob bei der Angabe „im Quellen-Wortlaut" das Wort selbst oder der angezeigte Inhalt das Problem ist.
- Was der Leitsatz „wir sammeln nur alles, was wir haben" genau aussagen soll und ob das Folgen für die Darstellung hat.

## Glossar

- **Prosopographie**: die Erfassung von Personen einer historischen Gruppe nach ihren Merkmalen, Rollen und Beziehungen, um aus vielen Einzelfällen ein soziales Bild zu gewinnen.
- **Rechtsgeschäft**: die rechtliche Transaktion selbst (Kauf, Stiftung, Verleihung, Testament und Ähnliches), die in einer Quelle festgehalten ist.
- **Quellenkorpus (Bestand)**: die oberste Gruppierung von Quellen, die sich in Zeitraum, Herkunft und Erschließungsform ähneln.
- **Quelle**: ein einzelnes überliefertes Schriftstück, also eine Urkunde oder ein Stadtbuch-Eintrag, das ein oder mehrere Rechtsgeschäfte dokumentiert.
- **Event**: ein einzelnes Rechtsgeschäft als strukturierte Einheit innerhalb einer Quelle. In der Praxis trägt fast jede Quelle genau ein Event.
- **Nennung (Gesamtnennung)**: das Vorkommen einer Person in einer Quelle. Mehrfacherwähnungen in derselben Quelle zählen als eine Nennung.
- **Individuelle Person**: die einzelne, über alle Quellen hinweg zusammengeführte Person als Identität, unabhängig davon, in wie vielen Quellen sie genannt ist.
- **Menschen-Event**: ein Sonderfall, bei dem ein Event vor allem Personen zusammenhält. Diese Personen werden in der Zählung nicht doppelt erfasst.
- **Rollenkombination**: die Zusammensetzung der Beteiligten eines Rechtsgeschäfts nach ihren Rollen, also wer ausstellt, wer empfängt und wer bezeugt.
- **Erschließungsform**: die Art, wie eine Quelle editorisch aufbereitet ist. Sie bestimmt, welche Art von Aussage eine Quelle stützt. Vier Formen kommen vor (Regest, Siegel, Eintrag, Nota).
- **Regest**: eine redaktionelle Zusammenfassung des Quelleninhalts. Der volle Wortlaut ist nicht ausgeschrieben, aber im Digitalisat einsehbar.
- **Volltext**: der vollständig ausgeschriebene Wortlaut einer Quelle, der textgenaue Belege erlaubt.
- **Faksimile (Digitalisat)**: die fotografische Abbildung des Originals, im Viewer zoom-, verschieb- und drehbar.
- **Siegel**: die Beschreibung der Besiegelung einer Urkunde, als eigene Erschließungsform ausgewiesen.
- **Eintrag**: die Erschließungsform für laufende Eintragungen in Stadtbüchern, im Unterschied zur Einzelurkunde.
- **Nota**: ein kurzer Nachtrag am Rand einer Quelle.
- **Signatur**: die eindeutige Fundstelle einer Quelle, über die sie zitierbar und auffindbar ist.
- **Aufbewahrungsort**: das Archiv, das das Original verwahrt (früher als „Datenherkunft" bezeichnet).
- **Dispositivformel**: das Verb oder die Wendung im Quellentext, die das Rechtsgeschäft anzeigt (etwa „verleiht", „stiftet").
- **Annotation**: die inhaltliche Auszeichnung im Quellentext, mit der Personen, Organisationen, Orte, Rollen und editorische Ergänzungen markiert sind.
- **Register**: das durchsuchbare Verzeichnis aller Personen beziehungsweise Organisationen. Jeder Eintrag ist eine zusammengeführte Identität mit eigener Profilseite.
- **Profil**: die Detailseite einer Person oder Organisation mit Stammdaten, Beziehungen und einer Tabelle der Quellen, in denen sie vorkommt.
- **Rolle (Funktionsrolle)**: die Eigenschaft, in der jemand an einem Rechtsgeschäft beteiligt ist. Es gibt vier Werte (Aussteller:in, Empfänger:in, Zeug:in / Siegler:in, Sonstige).
- **Tätigkeit (occ)**: die berufliche oder institutionelle Funktion einer Person, oft in Bezug auf eine Organisation (zum Beispiel „Pfleger" einer Burg).
- **Beziehung**: eine dokumentierte Verbindung zwischen Entitäten, nämlich Verwandtschaft, Freundschaft, Vertretung, Tätigkeit oder Titelverweis.
- **Normalisierung (Normalform)**: die Zusammenführung verschiedener Schreibweisen desselben Begriffs auf eine einheitliche Form.
- **Uhlirz-Kategorie**: eine Einteilung der Berufe in Gruppen (römische Ziffern I bis XVIII) nach der Systematik von Karl Uhlirz.
- **Als verstorben genannt**: die Kennzeichnung, dass eine Person in der Quelle bereits als verstorben erwähnt wird. Das ergibt keinen exakten Sterbetag, sondern einen Zeitpunkt, vor dem sie gestorben ist.
- **Provenienz (Datenherkunft)**: die Angabe, woher eine Aussage oder Klassifikation stammt, aus welcher Quelle und von welcher redaktionellen Hand.
- **Datenkorb**: eine Sammelmappe, in die Nutzer Quellen, Personen und Organisationen ablegen und exportieren. Sie liegt lokal im Browser, ohne Login.
- **Öffentliche Sicht**: die Live-Website, die nur fertige, freigegebene Bestände zeigt.
- **Interne Sicht**: die Arbeitsversion, die zusätzlich unfertige Bestände sowie Auswertungen und Exploration zeigt.
- **TEI**: der internationale Standard zur strukturierten Auszeichnung historischer Texte, in dem die Quellen kodiert sind.
