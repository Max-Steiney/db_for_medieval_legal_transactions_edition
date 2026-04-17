# Datenbasis

Was die Edition als Gegenstand dokumentiert und wie die Daten strukturiert sind. Fachbegriffe werden verwendet, nicht definiert. Definitionen in [[glossar]].

## Gegenstand

Die Edition erschließt mittelalterliche Wiener Rechtsgeschäfte in schriftlicher Überlieferung. Der Fokus liegt auf Urkunden und urkundlich verfassten Einträgen in Stadtbüchern, die rechtliche Transaktionen dokumentieren.

Der freigegebene Zeitraum beginnt 1177 und endet 1412, mit einer Ausnahme bis 1414 für die Quellenkorpora QGW II/1 und QGW II/2. Außerhalb dieses Rahmens liegende Zeitabschnitte werden nicht angezeigt.

## Quellenkorpora

Die Daten sind in Quellenkorpora organisiert, die sich in Zeitraum, Provenienz und Erschließungsform unterscheiden.

Das QGW-Corpus bündelt die „Quellen zur Geschichte Wiens" in mehreren Bänden. Die Stadtbücher bilden eine eigenständige Quellengruppe mit abweichender Überlieferungsform. Weitere Korpora wie Gewerbücher und Grundbücher werden im Build-Prozess vorgehalten, sind aber zum aktuellen Zeitpunkt nicht freigegeben.

Welche Korpora im UI tatsächlich sichtbar sind, entscheidet sich am Freigabestand, nicht an der technischen Verfügbarkeit.

## Nicht oder nur teilweise ausgewertet

Der Zeitraum 1418 bis 1447 ist im UI als „noch nicht ausgewertet" gekennzeichnet. Die Überlieferung existiert, die redaktionelle Auswertung steht aus. Der frühere Begriff „Überlieferungslücke" war sachlich falsch und wird nicht mehr verwendet.

Organisationen und Orte sind als Register-Dimensionen angelegt, aber zum aktuellen Zeitpunkt nicht freigegeben. Nur das Personenregister ist öffentlich.

## Erschließungsformen

Die Quellenkorpora unterscheiden sich in der Form ihrer Erschließung. Die Unterscheidung ist an der Oberfläche sichtbar zu machen, weil sie bestimmt, welche Art von Aussage eine Quelle stützt.

Monasterium-Quellen liegen als digitalisierte Faksimiles mit zugeordneten Regesten vor. Ein Regest ist eine redaktionelle Zusammenfassung; der zugrunde liegende Text ist nicht vollständig ediert, aber im Digitalisat einsehbar.

Die Stadtbücher sind als edierter Volltext erschlossen. Textgenaue Belege sind hier möglich, weil die Edition die Wortlaute wiedergibt.

Grundbücher und verwandte Bestände befinden sich auf unterschiedlichen Stufen der Erschließung. Der Status wird pro Bestand ausgewiesen.

## Hierarchie der Daten

Die Daten sind in vier Ebenen organisiert. [[glossar#Quellenkorpus]] ist die oberste Gruppierung, darunter einzelne [[glossar#Quelle|Quellen]], darunter einzelne [[glossar#Event|Events]], darunter einzelne Nennungen.

Jede Ebene hat ihre eigene Zählung. Wer nach Urkunden zählt, bleibt auf Quellenebene. Wer nach Rechtsgeschäften zählt, steigt auf Event-Ebene ab. Wer nach Personen zählt, wählt zwischen [[glossar#Gesamtnennung]] und [[glossar#Individuelle Person]].

## Register

Die Edition führt drei parallele Register: Personen, Organisationen, Orte. Jeder Eintrag ist eine konsolidierte Identität mit eindeutiger ID und verknüpft die Vorkommen in den Quellen.

Die Register sind nicht redundant zu den Quellen, sondern deren Bezugspunkt. Ohne Register gäbe es nur Namensketten ohne Zuordnung zu individuellen Entitäten.

## Annotationsebenen

Die TEI-Auszeichnung arbeitet auf vier Ebenen.

Events bilden die oberste Auszeichnungsebene. Sie halten ein konkretes Rechtsgeschäft als strukturierte Einheit zusammen.

Funktionen und Rollen spezifizieren, in welcher Eigenschaft eine Person oder Organisation an einem Event beteiligt ist. Das kontrollierte Vokabular ist in [[glossar#Rolle]] festgelegt.

Entitäten referenzieren die Register-Einträge für Personen, Organisationen und Orte.

Attribute halten zusätzliche Merkmale fest, etwa Verwandtschaftsbeziehungen, Berufe oder topographische Zuordnungen.

## Sonderfall Menschen-Events

Im Datenbestand vorkommend. Definition in [[glossar#Menschen-Event]], UI-Behandlung in [[requirements#Menschen-Events-Behandlung]].

## Siehe auch

- [[glossar]] Definitionen der verwendeten Begriffe
- [[architecture]] wie die Daten technisch verarbeitet werden
- [[requirements]] welche Anforderungen sich aus der Datenstruktur ableiten
