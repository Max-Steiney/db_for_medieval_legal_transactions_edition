Kanonische Definitionen aller Fachbegriffe der Datenbank. Quelle für Tooltips im UI und für die Glossar-Seite. Alphabetisch sortiert, pro Eintrag eine Definition, gegebenenfalls Abgrenzung und Hinweis zu häufigen Verwechslungen.

## Als verstorben genannt

Eine Person wird in einer Quelle bereits als verstorben bezeichnet, etwa durch Beiworte wie „selig", „weiland" oder „tot" neben dem Namen. Im TEI-Datenmodell wird das mit `<roleName type="dead">` ausgezeichnet. Im UI erscheint die Markierung als Dolch (†) neben dem Personennamen im Quellenvolltext und als Header-Feld im Personenprofil.

Die Markierung ist eine Quellenaussage, kein gesichertes Sterbedatum. Sie sagt nur, dass die Person zum Zeitpunkt der Quelle bereits verstorben war. Ein genaues Sterbedatum wird, sofern aus mehreren Quellen rekonstruierbar, separat im Personenregister als `<death notAfter="...">` geführt und im Profil als „Verstorben vor" angezeigt.

> **Abgrenzung:** „Als verstorben genannt" ist eine Quellen-Markierung pro Nennung. „Verstorben vor" ist eine konsolidierte Datierung im Personenregister.

## Eintrag

Ein in einem Verwaltungsbuch (Stadtbuch, Grundbuch, Gewerbuch) verzeichnetes Rechtsgeschäft. Anders als eine Urkunde steht ein Eintrag nicht für sich, sondern ist Teil einer fortlaufenden Aufzeichnung, die ein Amt oder eine Institution geführt hat. Im TEI-Datenmodell wird er als `<entry>` ausgezeichnet.

Im Datenbestand sind die Stadtbücher als Volltext-Einträge erschlossen, mit textgenauer Wiedergabe der Wortlaute. Ein Eintrag ist eine der vier Erschließungsformen neben [[#Regest]], [[#Siegel]] und [[#Nota]].

## Erschließungsform

Die Form, in der eine Quelle in der Datenbank zugänglich gemacht wird: als [[#Regest]] mit [[#Faksimile]], als ausgeschriebener [[#Volltext]], als [[#Eintrag]] in einem Verwaltungsbuch, als [[#Siegel|Siegelbeschreibung]] oder als [[#Nota]]. Die Erschließungsform bestimmt, welche Art von Aussage eine Quelle stützt. Aus einem Volltext lassen sich textgenaue Belege ziehen, ein Regest stützt nur die zusammengefasste Aussage, das Faksimile dient der Verifikation am Bild.

## Event

Ein konkretes Rechtsgeschäft, das in einer Quelle verzeichnet ist. Events sind die kleinste Einheit, auf die sich Rollen, Beteiligte und Transaktionsangaben beziehen.

Eine Quelle kann mehrere Events dokumentieren. Events wiederum können aufeinander verweisen, etwa wenn ein späteres Rechtsgeschäft auf ein früheres zurückbezieht.

> **Abgrenzung:** Nicht zu verwechseln mit einer Quelle als Ganzes. Die Unterscheidung trägt alle Zähl- und Filteroperationen.

## Faksimile

Die digitale Reproduktion einer Quelle als Bild. Ein Faksimile zeigt die Quelle, wie sie überliefert ist, ohne sie zu transkribieren. Es macht die paläografische Lesart der Quelle einsehbar und erlaubt die Verifikation einer Lesung gegen das Original.

In der Datenbank liegen Faksimiles für QGW-Bestände vor, eingebunden über die Monasterium-Plattform. Stadtbücher haben (noch) keine Faksimiles.

## Gesamtnennung

Eine Beziehung zwischen einer Person, Organisation oder einem Ort und einer Quelle, in der sie genannt wird. Wer in drei Quellen vorkommt, trägt drei Gesamtnennungen bei. Eine Person, die in derselben Quelle mehrfach erwähnt wird (typisch für Zeugenreihen oder Urteilslisten), trägt für diese Quelle nur eine Gesamtnennung bei (quellenbereinigte Zählung).

Gesamtnennungen sind die Zählebene für Häufigkeit gesellschaftlicher Präsenz. Sie machen Aussagen über Dichte und Funktionsträgerschaft möglich, ohne durch Mehrfachnennungen in einzelnen Urteilsformeln verzerrt zu werden.

Zählregel: Eine Gesamtnennung entsteht ausschließlich aus einer direkten Personen-Annotation im Quellentext (`<rs type="person">` mit `@ref` auf einen Personeneintrag). Korrespondierende Hilfsverknüpfungen (`@corresp` ohne `@type="person"`) zählen nicht, da sie administrative Verknüpfungen für Beziehungen sind, keine Quellentext-Erwähnungen. Ebenso ausgeschlossen sind Personen-Annotationen innerhalb verschachtelter `<rs type="event">`-Elemente (mentioned Events), da diese auf andere, früher referenzierte Geschäfte verweisen und keine Akteure des aktuellen Quellenereignisses sind. Die Filterung folgt dem Altsystem (PHP/MariaDB-Frontend) und der etablierten quellenkundlichen Konvention.

> **Abgrenzung:** Nicht zu verwechseln mit [[#Individuelle Person]]. Beide Zählebenen sind gleichzeitig gültig, beantworten aber verschiedene Fragen.

## Individuelle Person

Eine konsolidierte Identität im Personenregister, unabhängig von der Anzahl ihrer Nennungen. Dieselbe historische Person ist genau eine individuelle Person, auch wenn sie in fünfzig Quellen erscheint.

Die Zählebene für gesellschaftliche Struktur. Sie beantwortet, wie viele unterscheidbare Akteurinnen und Akteure das Korpus enthält. Analog gelten individuelle Organisationen und individuelle Orte.

Zählregel: Eine Person zählt, sobald sie in mindestens einer freigegebenen Quelle als `<rs type="person">` annotiert ist, gleich ob direkt im Top-Level-Event oder innerhalb eines verschachtelten (mentioned) rs-Events. Personen, die ausschließlich über `@corresp`-Hilfsverknüpfungen oder nur in nicht freigegebenen Korpora referenziert werden, sind im Personenregister nicht enthalten. Die Gesamtgröße des Personenregisters in `indices/personList.xml` ist daher größer als die ausgewiesene Anzahl individueller Personen.

> **Asymmetrie zur Gesamtnennung:** Eine Person erscheint im Distinct-Count, sobald sie irgendwo annotiert ist. Ihre Nennungen werden aber nur außerhalb mentioned Events gezählt. Das ist gewollt: Eine Person, die nur als Querverweis in einem mentioned Event auftritt, ist bekannt (gehört in das Register), aber nicht Akteur der aktuellen Quelle (zählt also nicht zu den Nennungen).

## Menschen-Event

Eine Person, die in einem Rechtsgeschäft namentlich erwähnt wird, weil sie in einem früheren, referenzierten Geschäft bereits vorkam. Sie ist mit einem Personennamen belegt, gehört aber nicht zum unmittelbaren Ereignis der aktuellen Quelle.

Der Begriff ist spezifisch für das Datenmodell dieser Datenbank und außerhalb nicht selbsterklärend. Das UI macht den Ein- oder Ausschlussstatus an jeder Abfrage sichtbar und lässt die Nutzerin aktiv entscheiden.

> **Achtung:** Eine stillschweigende Einbeziehung oder ein stillschweigender Ausschluss verändert Statistiken. Die asymmetrische Behandlung in verschiedenen Anzeigen macht Vergleiche ungültig.

## Nota

Ein Nachsatz oder eine Marginalie zur Hauptquelle, der nachträglich angefügt wurde, etwa um eine spätere Ergänzung, eine Korrektur oder einen Hinweis auf den weiteren Verlauf des Geschäfts festzuhalten. Im TEI-Datenmodell als `<nota>` ausgezeichnet.

Notae sind kein eigenständiges Rechtsgeschäft, sondern Beiwerk zur Quelle, das die [[#Erschließungsform]] mitbestimmt. Wer nach den Akteuren eines Rechtsgeschäfts fragt, blickt zuerst in [[#Regest]], [[#Eintrag]] oder Volltext, nicht in die Nota.

## Quelle

Eine einzelne Urkunde oder ein einzelnes Regest als Datensatz-Einheit. Die Quelle ist der Träger eines oder mehrerer Events.

Im UI konsequent „Quelle" statt „Dokument". Die alternative Bezeichnung war in früheren Oberflächen unklar, weil sie mit Dateiformaten und Digitalisaten verwechselt werden konnte.

> **Abgrenzung:** Eine Quelle ist nicht dasselbe wie ein [[#Event]]. Wer nach Rechtsgeschäften zählt, zählt Events. Wer nach Urkunden zählt, zählt Quellen.

## Quellenkorpus

Eine thematisch und editorisch zusammengehörige Gruppe von Quellen (beispielsweise die QGW-Bände oder die Stadtbücher). Der Quellenkorpus ist die oberste Gliederungsebene der Datenbasis.

Der Begriff ersetzt die frühere Bezeichnung „Sammlung". „Sammlung" ist quellenkundlich ungenau, weil sie einen kuratorischen Akt nahelegt, den der Bestand so nicht erfahren hat.

## Rechtsgeschäft

Eine Transaktion mit rechtlich bindender Wirkung zwischen Akteurinnen und Akteuren, niedergelegt in einer Quelle. Typische Rechtsgeschäfte sind Kauf, Verkauf, Schenkung, Verleihung, Verpfändung und Zeugenschaft.

Rechtsgeschäfte sind der historische Gegenstand der Datenbank. Ihre Auszeichnung im Datenmodell geschieht über [[#Event]]. Rechtsgeschäft ist der fachliche Begriff, Event die technische Kategorie.

> **Achtung:** Im Sprachgebrauch werden „Event" und „Rechtsgeschäft" oft synonym verwendet. Im Glossar und im UI sind sie trennscharf zu halten.

## Regest

Eine redaktionelle Zusammenfassung des wesentlichen Inhalts einer Quelle. Das Regest fasst Gegenstand, Beteiligte, Datum und Ort eines [[#Rechtsgeschäft|Rechtsgeschäfts]] zusammen, ohne den Quellentext im Wortlaut wiederzugeben.

Im Datenbestand der QGW-Bände ist das Regest die primäre Erschließungsform, der Quellentext wird nicht ausgeschrieben, ist aber im [[#Faksimile]] einsehbar. Aussagen, die textgenaue Wortlaute brauchen, lassen sich aus einem Regest nicht ableiten, sie verlangen den [[#Volltext]] oder einen Blick ins Faksimile.

## Rolle

Die Funktion einer Person oder Organisation in einem Event. Das kontrollierte Vokabular der Rollen ist kurz und festgelegt: `issuer` (ausstellend), `recipient` (empfangend), `sealer or witness` (siegelnd oder bezeugend), `other`, `none`.

Nur diese Werte sind gültig. Ein offenes Rollenvokabular wäre statistisch unbrauchbar, weil es die Aggregation über das Korpus verhinderte.

## Rollenkombination

Eine aus mehreren Rollen abgeleitete Kategorie, die das UI als Abfrage zugänglich macht. Beispiele sind gemeinsam handelnde Eheleute oder Witwen in einer bestimmten Rolle.

Rollenkombinationen sind keine eigene Annotationsebene im Datenmodell, sondern eine Auswertungsperspektive. Sie entstehen durch Kombination von Rollenattributen und anderen Merkmalen wie Geschlecht oder Beziehungstyp.

## Siegel

Die Beschreibung des oder der an einer Urkunde angebrachten Siegel. Das Siegel beglaubigte die Urkunde und identifizierte ihre Aussteller; seine Beschreibung in der Edition hält Form, Material, Erhaltungszustand und gegebenenfalls die siegelnde Person fest. Im TEI-Datenmodell als `<seal>` ausgezeichnet.

Eine Siegelbeschreibung ist eine eigene [[#Erschließungsform]] neben [[#Regest]] und [[#Eintrag]]. Sie liefert Aussagen über Authentizität, Beglaubigungspraxis und Trägerschaft eines Rechtsgeschäfts, nicht über seinen Inhalt.

## Volltext

Der ausgeschriebene Wortlaut einer Quelle, transkribiert und annotiert. Im Volltext sind Personen, Organisationen, Orte und Rechtsgeschäfte unmittelbar im Quellentext markiert. Textgenaue Belege sind möglich.

In der Datenbank sind die Stadtbücher als Volltext erschlossen. QGW-Bestände sind über [[#Regest]] und [[#Faksimile]] erschlossen, ohne ausgeschriebenen Volltext.
