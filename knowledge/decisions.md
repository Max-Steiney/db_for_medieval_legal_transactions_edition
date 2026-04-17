# Entscheidungen

Getroffene Leitentscheidungen mit Begründung. Zeitlos formuliert. Pro Eintrag Entscheidung, Begründung und Konsequenz, optional eine Abgrenzung, was ausdrücklich nicht gemeint ist.

## Titel und Untertitel

**Entscheidung.** Der Haupttitel der Edition lautet „Stadt und Gemeinschaft Wien", der Untertitel „Datenbank zu mittelalterlichen Rechtsgeschäften".

**Begründung.** Der Haupttitel ist in den Projektpublikationen etabliert. Eine abweichende Neubenennung würde Kontinuität mit bereits gedruckten Texten brechen. Der Untertitel ist deutsch, damit das UI sprachlich durchgängig bleibt und nicht ohne Anlass zwischen Deutsch und Englisch wechselt.

**Konsequenz.** Der Titel ist in Navigationsleiste, Seitentitel und Fußzeile konsistent zu führen.

## Exploration und Analyse als getrennte Bereiche

**Entscheidung.** Das UI führt zwei Navigationsbereiche nebeneinander: Exploration und Analyse.

**Begründung.** Beide Bereiche bedienen unterschiedliche Forschungssituationen und verlangen entgegengesetzte Interaktionsmuster. Die Exploration arbeitet ergebnisoffen mit Überblicksdarstellungen. Die Analyse arbeitet gezielt mit vordefinierten Abfragekombinationen. Eine Zusammenlegung wäre für beide Seiten ein Verlust.

**Konsequenz.** Siehe [[ui-design#Navigation]] und [[ui-design#Zwei Modi nebeneinander]].

**Nicht gemeint ist**, dass Exploration und Analyse streng disjunkt wären. Eine Nutzerin kann in der Exploration eine Auffälligkeit entdecken und in der Analyse gezielt weiterverfolgen.

## Begriff Gesamtnennungen

**Entscheidung.** Die Zählebene aller Erwähnungen heißt im UI „Gesamtnennungen", nicht „Nennungen". Die Zählebene der konsolidierten Register-Einträge heißt „Individuelle Personen", „Individuelle Organisationen", „Individuelle Orte".

**Begründung.** Das Präfix schafft eine explizite Abgrenzung zur [[glossar#Individuelle Person]] und reduziert die Verwechslungsgefahr in publikationsrelevanten Zahlen. Die Kurzform „Nennungen" war zu nahe an der alltagssprachlichen Verwendung und lud zu Fehlinterpretationen ein.

**Konsequenz.** Alle UI-Labels, Filter- und Achsenbeschriftungen verwenden „Gesamtnennungen" oder „Individuelle Personen". Siehe [[glossar#Gesamtnennung]]. Welche der beiden Zählebenen einer konkreten Zahl zugrunde liegt, muss an jeder Zahl per [[ui-design#Provenienz-Tooltip]] erkennbar sein. Ein Label, das eine Zahl fälschlich der anderen Zählebene zuordnet, ist ein Fehler im Sinne von [[requirements#Datenrobustheit und Provenienz]] und wird von [[architecture#Verifikations-Test-Set]] sichtbar gemacht.

## Quellenbereinigte Zählung

**Entscheidung.** Gesamtnennungen werden quellenbereinigt gezählt: eine Person, Organisation oder ein Ort, die oder der in derselben Quelle mehrfach erwähnt wird, trägt für diese Quelle genau eine Gesamtnennung bei.

**Begründung.** Urteilslisten, Zeugenreihen und Formularwiederholungen führen dazu, dass ein und dieselbe Person innerhalb einer Urkunde zwanzigmal namentlich auftaucht. Eine Zählung pro Einzelerwähnung würde solche Formelpartien gegenüber substanziellen Einzelnennungen überproportional gewichten und Vergleiche zwischen Regesten (wenige Nennungen pro Quelle) und edierten Volltexten (viele Nennungen pro Quelle) systematisch verzerren. Die quellenbereinigte Zählung beantwortet die Forschungsfrage „in wie vielen Quellen ist Person X belegt" präzise und ist robust gegen das Erschließungsformat.

**Konsequenz.** Die Definition in [[glossar#Gesamtnennung]] ist entsprechend formuliert. Der [[ui-design#Provenienz-Tooltip]] benennt diese Zählebene an jeder betroffenen Zahl explizit. Eine Umschaltung auf ungereinigte Einzelerwähnungen ist nicht vorgesehen; sie wäre statistisch missverständlich und fachlich schwer interpretierbar.

**Nicht gemeint ist**, dass das Datenmodell die Information über Mehrfachnennungen verliert. Die TEI-Quellen markieren jede Erwähnung einzeln. Die Dedupizierung greift erst in der Aggregation.

## Begriff Quellenkorpus

**Entscheidung.** Die oberste Gruppierungsebene der Datenbasis heißt „Quellenkorpus", nicht „Sammlung".

**Begründung.** „Sammlung" suggeriert einen kuratorischen Akt, den der Bestand so nicht erfahren hat. „Quellenkorpus" ist der fachhistorisch präzisere Begriff und wird in den Projektpublikationen durchgehend verwendet.

**Konsequenz.** Labels, Filter und Seitentitel sprechen von Quellenkorpus. Siehe [[glossar#Quellenkorpus]].

## Freigegebener Zeitraum

**Entscheidung.** Das UI zeigt den Zeitraum 1177 bis 1412, mit einer Ausnahme bis 1414 für QGW II/1 und QGW II/2.

**Begründung.** Nur freigegebene Regesten werden im Frontend angezeigt. Andere Werte in anderen Ansichten (etwa 1524 oder 1520) waren fehlerhafte Ableitungen aus unbereinigten Quellen.

**Konsequenz.** Zeitregler und Anzeigen verwenden diesen Bereich. Abweichungen gelten als Fehler.

## Formulierung „noch nicht ausgewertet"

**Entscheidung.** Der Zeitraum 1418 bis 1447 wird als „noch nicht ausgewertet" bezeichnet, nicht als „Überlieferungslücke".

**Begründung.** Die Überlieferung existiert. Nur die redaktionelle Auswertung steht aus. Die frühere Formulierung war sachlich falsch und wäre in einer wissenschaftlich verwendbaren Edition nicht haltbar.

**Konsequenz.** Der Begriff ist an allen sichtbaren Stellen konsequent zu verwenden.

## Personenregister-Freigabe

**Entscheidung.** Aktuell ist nur das Personenregister öffentlich. Organisationen- und Ortsregister sind nicht freigegeben.

**Begründung.** Der Bearbeitungsstand der drei Register unterscheidet sich. Eine Freigabe unreifer Register widerspräche dem Anspruch an Datenrobustheit.

**Konsequenz.** Organisationen- und Ortsregister-Seiten zeigen Platzhalter oder sind deaktiviert, bis ihre Qualität eine Freigabe zulässt.

## Trennung Edition-Repo und Pipeline-Repo

**Entscheidung.** Build-Output liegt in einem eigenen Repository, getrennt vom Pipeline- und Template-Quellcode.

**Begründung.** Siehe [[architecture#Trennung Quelle und Build-Output]]. Die Trennung hält die Historie der Inhaltsänderungen übersichtlich und reduziert das Risiko, dass Output-Artefakte mit Quelländerungen verwechselt werden.

**Konsequenz.** HTMLs werden nicht direkt editiert. Änderungen gehen durch Rebuild.

## Obsidian-kompatibles Knowledge-Format

**Entscheidung.** Die konzeptionelle Wissensbasis liegt als flache Markdown-Dateien mit Wiki-Links vor, ohne Unterordner, ohne Nummernpräfixe und ohne README.

**Begründung.** Die flache Struktur macht den Vault in Obsidian unmittelbar nutzbar und senkt die Einstiegshürde für Mit-Autorinnen. Ein README wäre Redundanz, weil Einstieg und Übersicht aus der Dateiliste selbst hervorgehen.

**Konsequenz.** Dokumente im `knowledge/`-Ordner folgen dieser Struktur. Verlinkung geschieht über Wiki-Syntax, nicht über Markdown-Referenzen.

## Verifikations-Test-Set als eigenständige Komponente

**Entscheidung.** Neben der Pipeline existiert ein unabhängiges Verifikations-Test-Set, das die TEI-Quellen und Register-XMLs eigenständig einliest, die Aggregate nachrechnet und gegen die vom Build erzeugten JSON-Ausgaben legt.

**Begründung.** Eine Zahl, die aus derselben Pipeline stammt, die sie angeblich verifiziert, verifiziert sich selbst nicht. Die Frage, ob ein Label an einer Zahl semantisch korrekt ist, lässt sich nur beantworten, wenn eine zweite, unabhängige Rechnung sie bestätigt. Die Implementierung in Python mit `lxml` vermeidet CSV-Zwischenstufen und trifft auf die Quelle direkt.

**Konsequenz.** Das Test-Set läuft auf Abruf und schreibt versionierte Reports. Diskrepanzen führen zu Korrekturen in Templates, Aggregations-Logik oder Quell-Daten. Gleichzeitig dient dieselbe Aggregations-Logik als Fundament für die [[#Provenienz als inline Drill-down in den Aggregat-JSONs]], weil beide dieselben Zählungen auf derselben Quellebene nachvollziehen. Siehe [[architecture#Verifikations-Test-Set]].

## Provenienz als inline Drill-down in den Aggregat-JSONs

**Entscheidung.** Die Provenienz einer aggregierten Zahl — also die Liste der Quelldokumente, die sie stützen — lebt als `drill_down`-Unterstruktur **innerhalb** der jeweiligen Aggregat-JSON, nicht als separate Datei.

**Begründung.** Bei der Prüfung des Build-Outputs zeigte sich, dass vier der fünf aggregierten JSONs die Provenienz-Information bereits als inline Drill-down tragen (role × sex → file_keys, relation type × sex → file_keys, transaction type × decade → file_keys, place → file_keys). Eine separate Parallel-JSON-Struktur wäre Duplikation derselben Information. Die inline Form hält Aggregat und Provenienz zusammen, ohne dass ein Frontend-Reader zwei Dateien korrelieren muss.

**Konsequenz.** Jeder Aggregat-JSON enthält einen `drill_down`-Abschnitt mit dem gleichen Schlüsselmuster wie die Counter-Werte, aber mit sortierten Listen von `file_key`-Verweisen statt Zahlen. Das Frontend löst einen Tooltip durch Lookup im gleichen JSON auf, ohne zusätzliches Nachladen. Die Zielkonsumption für das `file_key` ist `data/docs_lookup.json`, das jeden Schlüssel auf URL, Regest und Metadaten abbildet. Siehe [[requirements#Datenrobustheit und Provenienz]] und [[ui-design#Provenienz-Tooltip]].

**Nicht gemeint ist**, dass Aggregat-JSONs gegenseitig referenzieren oder fachlich zirkulär werden. `drill_down` ist eine reine Quellenauflistung, keine Aggregation zweiter Ordnung.

## Zeitlose Formulierung der Wissensbasis

**Entscheidung.** Die Dokumente der Wissensbasis sind zeitlos formuliert, mit Ausnahme von [[journal]].

**Begründung.** Konzepte, Anforderungen und Entscheidungen bleiben länger gültig als operative Einzelheiten. Ein Dokument, das mit einem konkreten Stichtag verknüpft ist, veraltet schneller und lädt zur Überarbeitung in die falsche Richtung ein.

**Konsequenz.** Keine Personennamen, keine Meeting-Datumsangaben, keine Quantitäten des Korpus. Ausnahme bleibt das journal.md als chronologisches Arbeitstagebuch.

## Maximaler Informations-Output als Gestaltungsleitlinie

**Entscheidung.** Das UI priorisiert Nachvollziehbarkeit vor reduzierter Darstellung.

**Begründung.** Fachnutzerinnen brauchen Herkunftsanzeigen an jeder Zahl. Eine Reduktion, die Herkunft verschleiert, ist für die wissenschaftliche Verwendung dysfunktional.

**Konsequenz.** Tooltips, Filterstatus und Zählebenen-Anzeige sind dauerhaft sichtbar. Ausführung in [[ui-design#Leitprinzip Maximaler Informations-Output]].

**Nicht gemeint ist**, dass Dichte Unübersichtlichkeit bedeutet. Die Oberfläche strebt hohe Informationsdichte mit klarer hierarchischer Gliederung an, nicht visuelles Rauschen.

## Siehe auch

- [[requirements]] Anforderungen, aus denen die Entscheidungen folgen
- [[ui-design]] gestalterische Umsetzung
- [[journal]] chronologischer Pfad, auf dem Entscheidungen entstanden sind
