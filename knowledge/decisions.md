# Entscheidungen

Getroffene Entscheidungen mit Begründung. Zeitlos formuliert. Format: *Entscheidung — Begründung — Konsequenz fürs UI*.

## Titel und Untertitel

<!-- Entscheidung: Haupttitel „Stadt und Gemeinschaft Wien", Untertitel „Database for Medieval Legal Transactions". -->
<!-- Begründung: bereits etablierter Titel in der alten Datenbank; terminologische Kontinuität. -->
<!-- Konsequenz: Titel konsistent in Navigationsleiste, Seitentitel, Fußzeile. -->

## Exploration und Analyse als getrennte Bereiche

<!-- Entscheidung: zwei Navigationsbereiche nebeneinander, nicht einer statt des anderen. -->
<!-- Begründung: unterschiedliche Zugangsformen (ergebnisoffen explorativ vs. gezielt abfragend). Eine Zusammenlegung verwässert beide. -->
<!-- Konsequenz: siehe [[ui-design#Navigation]]. -->

## Begriff „Gesamtnennungen"

<!-- Entscheidung: [[glossar#Gesamtnennung]] statt „Nennungen". -->
<!-- Begründung: das Präfix schafft explizite Abgrenzung zur [[glossar#Individuelle Person]] — reduziert Missverständnisse in publikationsrelevanten Zahlen. -->
<!-- Konsequenz: Begriff überall im UI einheitlich verwenden. -->

## Begriff „Quellenkorpus"

<!-- Entscheidung: [[glossar#Quellenkorpus]] statt „Sammlung". -->
<!-- Begründung: in der alten Datenbank etablierter Begriff; fachlich präziser. -->
<!-- Konsequenz: Labels, Filter, Seitentitel sprechen von Quellenkorpus. -->

## Freigegebener Zeitraum

<!-- Entscheidung: Anzeige 1177–1412, Ausnahme 1414 für QGW II/1 und II/2. -->
<!-- Begründung: nur freigegebene Regesten im Frontend; andere Werte sind fehlerhafte Ableitungen. -->
<!-- Konsequenz: Zeitregler und Anzeigen verwenden diesen Bereich; Abweichungen gelten als Fehler. -->

## Formulierung „noch nicht ausgewertet"

<!-- Entscheidung: Lücke 1418–1447 wird als „noch nicht ausgewertet" bezeichnet, nicht als „Überlieferungslücke". -->
<!-- Begründung: die Überlieferung existiert; nur die Auswertung steht noch aus. Die alte Formulierung war sachlich falsch. -->

## Personenregister-Freigabe

<!-- Entscheidung: aktuell nur Personenregister öffentlich; Organisationen und Orte nicht freigegeben. -->
<!-- Begründung: unterschiedlicher Bearbeitungsstand. Freigabe folgt, sobald die jeweilige Qualität das zulässt. -->
<!-- Konsequenz: Orte- und Organisationen-Seiten zeigen Platzhalter oder sind deaktiviert. -->

## Trennung Edition-Repo und Pipeline-Repo

<!-- Entscheidung: Build-Output in eigenem Repository, getrennt vom Pipeline- und Template-Quellcode. -->
<!-- Begründung: siehe [[architecture#Warum zwei Repos]]. -->
<!-- Konsequenz: HTMLs werden nicht direkt editiert; Änderungen gehen durch Rebuild. -->

## Obsidian-kompatibles Knowledge-Format

<!-- Entscheidung: konzeptionelle Wissensbasis als flache Markdown-Dateien mit Wiki-Links, keine Unterordner, kein README. -->
<!-- Begründung: niedrige Einstiegshürde, in Obsidian nutzbar (Graph-View, Backlinks), leicht in andere Formate überführbar. -->
<!-- Konsequenz: Dokumente in [[knowledge/]] folgen dieser Struktur. -->

## Zeitlose Formulierung der Wissensbasis

<!-- Entscheidung: keine Personennamen, keine Meeting-Datumsangaben, keine Quantitäten des Korpus in der Wissensbasis. -->
<!-- Begründung: Konzepte sollen unabhängig von operativen Einzelheiten langfristig gültig bleiben. -->
<!-- Konsequenz: [[journal]] ist das einzige chronologische Dokument; alle anderen sind zeitlos. -->

## Maximaler Informations-Output als Gestaltungsleitlinie

<!-- Entscheidung: [[ui-design#Leitprinzip: Maximaler Informations-Output]] gilt vor reduzierter Ästhetik. -->
<!-- Begründung: Fachnutzerinnen brauchen Provenienz; Reduktion, die Provenienz verschleiert, ist dysfunktional. -->
<!-- Konsequenz: Tooltips, Filterstatus, Zählebenen-Anzeige dauerhaft sichtbar. -->

## Siehe auch

- [[requirements]] — Anforderungen, aus denen Entscheidungen folgen
- [[ui-design]] — gestalterische Umsetzung
- [[journal]] — chronologische Herleitung einzelner Entscheidungen
