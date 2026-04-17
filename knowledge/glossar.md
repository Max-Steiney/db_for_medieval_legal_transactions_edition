# Glossar

Kanonische Definitionen aller Fachbegriffe der Edition. Quelle für Tooltips und die Glossar-Seite im UI. Alphabetisch sortiert. Pro Eintrag Definition, Abgrenzung und, wo nötig, eine Notiz zu häufigen Verwechslungen.

## Event

Ein konkretes Rechtsgeschäft, das in einer Quelle verzeichnet ist. Events sind die kleinste Einheit, auf die sich Rollen, Beteiligte und Transaktionsangaben beziehen.

Eine Quelle kann mehrere Events dokumentieren. Events wiederum können aufeinander verweisen, etwa wenn ein späteres Rechtsgeschäft auf ein früheres zurückbezieht.

Achtung: Nicht verwechseln mit einer Quelle als Ganzes. Die Unterscheidung trägt alle Zähl- und Filteroperationen. Verwendet in [[data#Hierarchie der Daten]], [[requirements]].

## Gesamtnennung

Eine Beziehung zwischen einer Person, Organisation oder einem Ort und einer Quelle, in der sie genannt wird. Wer in drei Quellen vorkommt, trägt drei Gesamtnennungen bei. Eine Person, die in derselben Quelle mehrfach erwähnt wird (typisch für Zeugenreihen oder Urteilslisten), trägt für diese Quelle nur eine Gesamtnennung bei (quellenbereinigte Zählung).

Gesamtnennungen sind die Zählebene für Häufigkeit gesellschaftlicher Präsenz. Sie machen Aussagen über Dichte und Funktionsträgerschaft möglich, ohne durch Mehrfachnennungen in einzelnen Urteilsformeln verzerrt zu werden.

Achtung: Nicht zu verwechseln mit [[#Individuelle Person]]. Beide Zählebenen sind gleichzeitig gültig, beantworten aber verschiedene Fragen. Verwendet in [[requirements#Umschaltbarkeit der Zählebenen]] und [[decisions#Quellenbereinigte Zählung]].

## Individuelle Person

Eine konsolidierte Identität im Personenregister, unabhängig von der Anzahl ihrer Nennungen. Dieselbe historische Person ist genau eine individuelle Person, auch wenn sie in fünfzig Quellen erscheint.

Die Zählebene für gesellschaftliche Struktur. Sie beantwortet, wie viele unterscheidbare Akteurinnen und Akteure das Korpus enthält. Analog gelten individuelle Organisationen und individuelle Orte.

Verwendet in [[requirements#Umschaltbarkeit der Zählebenen]], [[scholar-user-stories]].

## Menschen-Event

Eine Person, die in einem Rechtsgeschäft namentlich erwähnt wird, weil sie in einem früheren, referenzierten Geschäft bereits vorkam. Sie ist mit einem Personennamen belegt, gehört aber nicht zum unmittelbaren Ereignis der aktuellen Quelle.

Der Begriff ist spezifisch für das Datenmodell der Edition und außerhalb nicht selbsterklärend. Das UI macht den Ein- oder Ausschlussstatus an jeder Abfrage sichtbar und lässt die Nutzerin aktiv entscheiden.

Achtung: Eine stillschweigende Einbeziehung oder ein stillschweigender Ausschluss verändert Statistiken. Die asymmetrische Behandlung in verschiedenen Anzeigen macht Vergleiche ungültig. Verwendet in [[requirements#Menschen-Events-Behandlung]], [[ui-design#Menschen-Events-Toggle]].

## Quelle

Eine einzelne Urkunde oder ein einzelnes Regest als Datensatz-Einheit. Die Quelle ist der Träger eines oder mehrerer Events.

Im UI konsequent „Quelle" statt „Dokument". Die alternative Bezeichnung war in früheren Oberflächen unklar, weil sie mit Dateiformaten und Digitalisaten verwechselt werden konnte.

Achtung: Eine Quelle ist nicht dasselbe wie ein [[#Event]]. Wer nach Rechtsgeschäften zählt, zählt Events. Wer nach Urkunden zählt, zählt Quellen. Verwendet in [[data#Hierarchie der Daten]].

## Quellenkorpus

Eine thematisch und editorisch zusammengehörige Gruppe von Quellen (beispielsweise die QGW-Bände oder die Stadtbücher). Der Quellenkorpus ist die oberste Gliederungsebene der Datenbasis.

Der Begriff ersetzt die frühere Bezeichnung „Sammlung". „Sammlung" ist editionsphilologisch ungenau, weil sie einen kuratorischen Akt nahelegt, den der Bestand so nicht erfahren hat.

Verwendet in [[data#Quellenkorpora]], [[ui-design#Bestandsfilter]], [[decisions#Begriff Quellenkorpus]].

## Rechtsgeschäft

Eine Transaktion mit rechtlich bindender Wirkung zwischen Akteurinnen und Akteuren, niedergelegt in einer Quelle. Typische Rechtsgeschäfte sind Kauf, Verkauf, Schenkung, Verleihung, Verpfändung und Zeugenschaft.

Rechtsgeschäfte sind der historische Gegenstand der Datenbank. Ihre Auszeichnung im Datenmodell geschieht über [[#Event]]. Rechtsgeschäft ist der fachliche Begriff, Event die technische Kategorie.

Achtung: Im Sprachgebrauch werden „Event" und „Rechtsgeschäft" oft synonym verwendet. Im Glossar und im UI sind sie trennscharf zu halten. Verwendet in [[data#Gegenstand]].

## Rolle

Die Funktion einer Person oder Organisation in einem Event. Das kontrollierte Vokabular der Rollen ist kurz und festgelegt: `issuer` (ausstellend), `recipient` (empfangend), `sealer or witness` (siegelnd oder bezeugend), `other`, `none`.

Nur diese Werte sind gültig. Ein offenes Rollenvokabular wäre statistisch unbrauchbar, weil es die Aggregation über das Korpus verhinderte.

Verwendet in [[requirements]], [[scholar-user-stories#Rollenbasierte Akteursanalyse]], [[ui-design#Analyse]].

## Rollenkombination

Eine aus mehreren Rollen abgeleitete Kategorie, die das UI als Abfrage zugänglich macht. Beispiele sind gemeinsam handelnde Eheleute oder Witwen in einer bestimmten Rolle.

Rollenkombinationen sind keine eigene Annotationsebene im Datenmodell, sondern eine Auswertungsperspektive. Sie entstehen durch Kombination von Rollenattributen und anderen Merkmalen wie Geschlecht oder Beziehungstyp.

Verwendet in [[scholar-user-stories]], [[ui-design#Analyse]].

## Siehe auch

- [[data]] setzt diese Begriffe systemisch in Verbindung
- [[requirements]] leitet aus Zählebenen und Vokabular funktionale Anforderungen ab
- [[ui-design]] setzt die Umschaltbarkeit und das Rollenvokabular als Komponenten um
