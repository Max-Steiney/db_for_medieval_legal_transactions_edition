# Scholar User Stories

Nutzungsszenarien aus Forscherinnen-Perspektive. Pro Story ein Szenario im Muster *Als Forscherin, die …, will ich …, damit …*. Darunter eine knappe Ableitung, welche Anforderung, Komponente und Begriffe das Szenario adressiert.

Die Stories sind nach drei Gruppen sortiert: zentrale Forschungsoperationen, wissenschaftliche Absicherung, begriffliche Orientierung.

## Zentrale Forschungsoperationen

### Verteilung einer Kategorie überblicken

*Als Forscherin, die Häufigkeitsstrukturen in einer Kategorie untersucht, will ich jederzeit zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]] umschalten, damit ich Frequenz und Breite sauber voneinander trennen kann.*

Ableitung:
- Anforderung [[requirements#Umschaltbarkeit der Zählebenen]]
- Komponente [[ui-design#Zählebenen-Umschalter]]
- Begriffe [[glossar#Gesamtnennung]], [[glossar#Individuelle Person]]

### Rollenbasierte Akteursanalyse

*Als Forscherin, die Geschlechteranteile in einer bestimmten [[glossar#Rolle]] untersucht, will ich nach Rolle und Geschlecht gleichzeitig filtern, damit ich die Verteilung unmittelbar ablesen kann.*

Ableitung:
- Anforderung [[requirements#Bestandsfilterung als universelle Dimension]]
- Komponente [[analyse]]
- Begriff [[glossar#Rolle]]

### Bestandsvergleich

*Als Forscherin, die einen Teilbestand gegen den Gesamtbestand kontrastiert, will ich die gleiche Kategorie auf beide Bestände anwenden, damit ich Auffälligkeiten des Teilbestands erkenne.*

Ableitung:
- Anforderung [[requirements#Bestandsfilterung als universelle Dimension]]
- Komponente [[ui-design#Bestandsfilter]]
- Begriff [[glossar#Quellenkorpus]]

### Zeitverlauf einer Kategorie

*Als Forscherin, die Entwicklungen über die Zeit untersucht, will ich eine Kategorie im Zeitraster sehen, damit ich Kontinuitäten und Brüche erkenne.*

Ableitung:
- Komponente [[ui-design#Zeitfilter]], [[exploration]]

### Rollenkombination abfragen

*Als Forscherin, die gemeinsam handelnde Eheleute untersucht, will ich diese [[glossar#Rollenkombination]] direkt abrufen, damit ich nicht jede Abfrage manuell zusammenbaue.*

Ableitung:
- Komponente [[analyse]]
- Begriff [[glossar#Rollenkombination]]

## Wissenschaftliche Absicherung

### Provenienz einer Zahl prüfen

*Als Forscherin, die eine Zahl in einer Publikation verwenden will, will ich an Ort und Stelle sehen, welcher Bestand und welche Operation der Zahl zugrunde liegen, damit ich sie gegenüber Reviewerinnen vertreten kann.*

Ableitung:
- Anforderung [[requirements#Datenrobustheit und Provenienz]]
- Komponente [[ui-design#Provenienz-Tip und Glossar-Tip]]

### Peer-Review einer Abfrage

*Als Forscherin, die eine Auswertung einer Kollegin prüft, will ich dieselbe Filterkombination aufrufen können wie sie, damit wir auf derselben Datensicht diskutieren.*

Ableitung:
- Anforderung [[requirements#Zitierfähige Datenstände]]
- Komponente [[ui-design#Zitierbarkeit einzelner Ansichten]]

### Publikationsreife Zitation

*Als Forscherin, die Zahlen in einer Veröffentlichung zitiert, will ich einen eingefrorenen Datenstand zum Stichtag der Einreichung referenzieren, damit meine Aussagen langfristig überprüfbar bleiben.*

Ableitung:
- Anforderung [[requirements#Zitierfähige Datenstände]]

### Fehlerverdacht lokalisieren

*Als Forscherin, die eine unplausible Zahl sieht, will ich erkennen können, ob der Grund in den Quelldaten, in der Transformation oder in der Darstellung liegt, damit ich den Fehler präzise benennen kann.*

Ableitung:
- Anforderung [[requirements#Datenrobustheit und Provenienz]]
- Komponente [[ui-design#Provenienz-Tip und Glossar-Tip]]
- Fundament [[architecture]]

## Begriffliche Orientierung

### Unbekannten Begriff an Ort und Stelle verstehen

*Als Forscherin, die einem projektspezifischen Begriff wie [[glossar#Menschen-Event]] zum ersten Mal begegnet, will ich seine Bedeutung im UI nachschlagen, ohne den Kontext zu verlassen, damit ich die Konsequenz einer Filteraktion verstehe.*

Ableitung:
- Komponente [[ui-design#Glossar-Integration]]
- Begriff [[glossar#Menschen-Event]]

### Menschen-Events kontrolliert behandeln

*Als Forscherin, die exakte Statistiken zu Personen in einem Rechtsgeschäft aufstellt, will ich [[glossar#Menschen-Event|Menschen-Events]] aktiv ein- oder ausschließen, damit referenzierte Personen aus früheren Geschäften meine Zahlen nicht verzerren.*

Ableitung:
- Anforderung [[requirements#Menschen-Events-Behandlung]]
- Komponente [[ui-design#Menschen-Events-Toggle]]
- Begriff [[glossar#Menschen-Event]]

## Wiederkehrende Grundabfragen

*Als Forscherin, die wiederkehrende Fragen an die Datenbank stellt, will ich eine Liste vordefinierter Grundabfragen direkt aufrufen, damit ich nicht jedes Mal die Filterabfolge manuell durchklicke.*

Die Liste der konkreten Grundabfragen wird mit dem Fachteam festgelegt. Typische Kandidaten sind Abfragen nach Rollen und Geschlecht, nach [[glossar#Rollenkombination|Rollenkombinationen]] und nach Bestandsvergleichen.

Ableitung:
- Komponente [[analyse]]

## Siehe auch

- [[requirements]] systematische Anforderungsableitung
- [[ui-design]] konkrete Umsetzung
- [[glossar]] verwendete Fachbegriffe
