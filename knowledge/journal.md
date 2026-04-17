# Journal

Arbeitstagebuch. Einziges chronologisches Dokument der Wissensbasis.

Format pro Eintrag: Überschrift mit Datum und Kurztitel, darunter eine knappe Notiz zum Fortschritt, zu Entscheidungspfaden, zu verworfenen Alternativen oder zu offenen Fragen. Verlinkt werden die Zieldokumente, nicht Personen oder Meetings.

Was hier rein darf: Fortschritt der Wissensbasis, Entscheidungspfade, die in [[decisions]] münden, verworfene Alternativen mit Begründung, offene Fragen, die beim Arbeiten auftauchen.

Was nicht rein darf: Personennamen, Meeting-Protokolle, Projektmanagement-Stand, Quantitäten des Korpus.

Einträge in umgekehrt chronologischer Reihenfolge, neueste oben.

---

## 2026-04-17 Terminologie-Konsolidierung, Erschlie\u00dfungsform, Provenienz-Ausrollung

Die UI-Terminologie wird durchgehend auf die kanonischen Begriffe aus [[glossar]] und [[decisions#Begriff Quellenkorpus]] gezogen. Alle benutzerseitig sichtbaren Vorkommen von „Dokument(e)" werden zu „Quelle(n)", „Rechtsakt(e)" zu „Rechtsgesch\u00e4ft(e)", eine verbliebene „Sammlung"-Spaltenkopfzeile zu „Quellenkorpus". Technische Labels auf HTML-Ebene (ARIA-Attribute, CSS-IDs) bleiben unber\u00fchrt, weil sie sich auf das HTML-Dokument als Tr\u00e4gerformat beziehen, nicht auf die Quelle der Edition.

Die [[data#Erschlie\u00dfungsformen|Erschlie\u00dfungsform]] eines Quellenkorpus ist im UI an den Quellenkorpus-Chips der Dokumenten-\u00dcbersicht sichtbar. QGW-Best\u00e4nde tragen das Label „Regest + Faksimile", Stadtb\u00fccher tragen „Volltext". Die Zuordnung liegt als Build-Konstante `_transmission_form` vor und fliesst in die `collections`-Datenstruktur mit ein.

Die Provenienz-Tooltip-Komponente wird von den Startseiten-KPIs auf weitere Seiten ausgerollt: Exploration-Hub (Personen, Rechtsgesch\u00e4fte, Quellen), Personenregister (Gesamt-Eintr\u00e4ge mit Hinweis auf quellenbereinigte Z\u00e4hlung pro Eintrag), Datenqualit\u00e4t (Quellen gesamt). Das Muster ist dasselbe wie auf der Startseite; die Popover-Inhalte verweisen jeweils auf die relevanten Glossar-Eintr\u00e4ge und Dateipfade.

Offen f\u00fcr eigene Sessions:

- **Z\u00e4hlebenen-Umschalter [[requirements#Umschaltbarkeit der Z\u00e4hlebenen]].** Implementierungspfad: globaler Schalter in der Navbar oder Filter-Leiste, persistierter Zustand im `localStorage`, propagiert via `window.COUNT_MODE` an die Exploration-Skripte. Jeder Counter muss pro Zahl wissen, welche der beiden Ebenen er anzeigen kann; f\u00fcr die Mehrzahl der Exploration-Seiten bedeutet das eine parallele JSON-Struktur (oder zus\u00e4tzliche Felder in den bestehenden `epic_*`-Dateien), die beide Ebenen vorhalten. Der Provenienz-Tooltip zeigt in jedem Popover den gew\u00e4hlten Modus.

- **Menschen-Events-Toggle [[ui-design#Menschen-Events-Toggle]].** Implementierungspfad analog: `window.INCLUDE_HUMAN_EVENTS`, persistiert, propagiert. Datenmodell-Seite: die Aggregatoren m\u00fcssen Nennungen trennen, je nachdem ob sie aus einem prim\u00e4ren Event stammen oder als Verweis auf ein fr\u00fcheres Event vorliegen. Voraussetzung ist eine belastbare Markierung im TEI-Datenstrom. Bei fehlender Markierung zeigt das UI den aktuellen stillschweigenden Zustand (Einschluss) offen, statt ihn zu verschleiern.

- **Bestandsfilter universell [[ui-design#Bestandsfilter]].** Derzeit wirkt der Filter nur auf der Quellen-\u00dcbersicht. Implementierungspfad: eine gemeinsame Filter-Komponente mit `window.CORPUS_FILTER` als Zustand, die alle Seiten beim Laden konsultieren. Die Seiten selbst m\u00fcssen ihre Aggregate so aufbauen, dass sie auf beliebige Teilmengen der Korpora herunter-rechenbar sind. F\u00fcr die Exploration-Skripte heisst das, dass die `epic_*`-JSONs zus\u00e4tzlich eine korpusbasierte Unterschl\u00fcsselung tragen.

- **Analyse-Seite mit Template-Familien.** Blaupause in [[quer ui]]. Umsetzung erfordert Fachteam-Entscheidung \u00fcber die initiale Familienmenge. Technischer Pfad: clientseitige Template-Engine mit Slot-Parametern, Live-Counts aus den `epic_*`-Aggregaten, Drill-down \u00fcber das bestehende `docs_lookup.json`.

Kleinere UX-Punkte, die ohne Phase-2-Abh\u00e4ngigkeit umgesetzt werden k\u00f6nnen:

- Multi-Select-Chips f\u00fcr den Quellenkorpus-Filter (mehrere Korpora gleichzeitig).
- Tag-Farbdifferenzierung f\u00fcr Rollen in der Einzelquellen-Ansicht.
- Mouse-over-Legenden in den Exploration-Visualisierungen, mit kurzen Erkl\u00e4rungen der Achsen und Kodierungen.
- F-Faktoid-Legende (Markierung weiblicher Faktoid-Gruppen in den Rollen-Ansichten).
- Archivinfos auf der Einzelquellen-Ansicht (Signatur, Bestand, Faszikel, sofern aus TEI-Header extrahierbar).

## 2026-04-17 Startseiten-Layout, Datenstand und offene Phase-2-Punkte

Die Startseite wird konzeptionell neu geordnet. Statt einer einzelnen Exploration-Sektion mit Trennstrich stehen zwei gleichberechtigte Säulen nebeneinander: Exploration (vier visuelle Zugänge) und Analyse (Einstieg zur Grundabfragen-Seite im Template-Familien-Stil von [[quer ui]]). Eyebrow-Labels in Sans-Caps markieren die Bereiche ohne optischen Schwergewichte wie border-bottom. Die Entry-Cards (Quellen, Personenregister, Über das Projekt) tragen Icons in der Akzentfarbe. Die Farblogik stabilisiert sich: blau für Akzente (Icons, Labels, interaktive Elemente), schwarz für Inhaltstitel, gedämpftes Grau für Beschreibungstexte.

Der Footer trennt Datenstand und Build-Datum. Bis zuletzt zeigte „Datenstand" das Tagesdatum des Builds, was inhaltlich falsch ist. Der Datenstand ist nun das Datum des letzten Commits im Pipeline-Repo, ermittelt über `git log -1 --format=%cI` und in deutscher Langform ausgegeben. Die Hilfsfunktionen `_format_german_date` und `_pipeline_repo_data_date` liegen in `edition/build.py`. Die Dissertations-Zeile im Footer entfällt; sie war Projekthistorie, nicht Editionskontext.

[[glossar#Gesamtnennung]] wird präzisiert: die Zählebene ist quellenbereinigt, Mehrfacherwähnungen einer Person in derselben Quelle werden zu einer Nennung zusammengefasst. Die entsprechende Leitentscheidung liegt als [[decisions#Quellenbereinigte Zählung]] vor. Der Provenienz-Tooltip zur individuellen Person nimmt diese Schärfung auf.

Offen bleibt aus der Phase-2-Liste des CS-Feedbacks:

- **Zählebenen-Umschalter** zwischen Gesamtnennungen und Individuellen Personen in allen betroffenen Visualisierungen ([[requirements#Umschaltbarkeit der Zählebenen]]). Ohne diese Umschaltung zeigen Rollen- und Beziehungs-Ansichten nur eine Zählebene.
- **Menschen-Events-Toggle** ([[glossar#Menschen-Event]]): aktiv ein- und ausschließbar, konsistent durch alle abhängigen Darstellungen. Ohne Toggle ist der aktuelle Zustand stillschweigend ein Ausschluss, was Vergleiche über Visualisierungen erschwert.
- **Bestandsfilter universell** in allen Visualisierungen, nicht nur in den Quellen-Suchseiten. Sinnvoll, sobald Organisationen und Orte freigegeben sind.
- **Persistente Referenzierbarkeit / PID**: beschlossen, aber technische Ausprägung (w3id, ARK, Handle) braucht Stakeholder-Entscheidung. Siehe [[requirements#Persistente Referenzierbarkeit]].
- **Provenienz-Tooltip-Ausrollung** auf Register- und Exploration-Seiten. Die Komponente ist etabliert, der Einsatzort bisher auf Startseiten-KPIs beschränkt.

Außerhalb der Phase 2 stehen vereinzelte Daten-Anomalien im TEI-Bestand: Pseudo-Rollen außerhalb des kontrollierten Vokabulars, Sonderzeichen-URLs in docs_lookup.json, eine Witness-Anomalie in ausgewählten Quellen. Die Bereinigung läuft auf Seite der TEI-Annotation. Das Verifikations-Test-Set macht sie als `known_gap` sichtbar.

## 2026-04-17 Test-Set, Label-Korrektur und offengelegte Datenlücken

Im Edition-Repo entsteht ein eigenständiges Verifikations-Test-Set (Python, `lxml`). Es liest die TEI-Quellen und Register-XMLs des Pipeline-Repos unabhängig ein, rechnet Aggregate nach und vergleicht sie mit den JSON-Ausgaben unter `/data/`. Die Entscheidung dazu steht in [[decisions#Verifikations-Test-Set als eigenständige Komponente]].

Der Erstlauf liefert drei belastbare Befunde.

Erstens: Register-Totals und Datum-Ranges stimmen exakt. Der Test bestätigt die Identität individueller Personen aus dem Register mit dem Count der Personen-Such-JSON.

Zweitens: Der Zahlenwert, der im UI als „Gesamtnennungen Personen" beschriftet war, ist tatsächlich die Anzahl individueller Personen, nicht die der Nennungen. Das Label war falsch und wurde korrigiert zu „individuelle Personen". Siehe [[decisions#Begriff Gesamtnennungen]] und [[glossar#Individuelle Person]].

Drittens: Ein Quellenkorpus-Teilbestand erscheint in den Aggregaten des Frontends, hat aber keine TEI-Quelle im Pipeline-Repo. Die Zahlen im Frontend beruhen für diesen Teilbestand nur auf einer CSV-Zwischenstufe. Die Offenlegung ist eine Konsequenz aus [[requirements#Datenrobustheit und Provenienz]]. Die Entscheidung, wie mit dieser Lücke umgegangen wird (Datenergänzung, Sichtbarmachung als eingeschränkte Provenienz oder Ausblendung), steht aus.

Parallel werden im TEI Pseudo-Rollen sichtbar, die weder im kontrollierten Rollenvokabular vorgesehen sind noch interpretativ Bedeutung haben. Sie entstehen aus Annotationsfehlern und werden im Test-Report als solche markiert. Die Bereinigung läuft auf Seite der TEI-Annotation, nicht in der Pipeline.

## 2026-04-17 URL-Refactor und deutsche UI

Die flache Root-Struktur des Edition-Repos wird auf semantische Unterordner umgebaut: `register/`, `exploration/`, `analysis/`, `project/`. Die Umstellung betrifft Navigation, Build-Output und JavaScript-Lader, die die JSON-Indexe künftig über ein zentral gesetztes `window.ROOT_PATH` adressieren. Damit funktioniert die Edition auch aus Unterordner-Tiefe heraus, ohne dass Pfade zu absoluten Web-Pfaden mutieren.

Die UI-Oberfläche wird durchgängig auf Deutsch gezogen. Englisch bleibt in Pfaden und im Code. Der Untertitel lautet jetzt „Datenbank zu mittelalterlichen Rechtsgeschäften". Siehe [[decisions#Titel und Untertitel]].

Quantitätsbezogene Angaben (Zeiträume, unausgewertete Perioden, Korpus-Zählwerte) werden aus Templates entfernt und an eine zentrale Konfigurationsdatei im Pipeline-Repo gebunden. Hardcoded Zahlen in Templates gelten ab jetzt als Fehler.

## 2026-04-17 Entstehung der Wissensbasis

Anlass war die Einarbeitung von Feedback zum Frontend. In der ersten Iteration wurde die Wissensbasis als Obsidian-kompatibler Markdown-Ordner angelegt. Pro Dokument gilt zeitlose Formulierung ohne Projektmanagement-Artefakte und ohne Quantitäten des Korpus. Siehe [[decisions#Zeitlose Formulierung der Wissensbasis]].

Verworfen wurde ein README und eine Unterordner-Gliederung. Grund ist, dass die flache Struktur den Vault in Obsidian unmittelbar nutzbar macht und die Einstiegshürde senkt.

Für das Glossar wurde ein Kriterium festgelegt. Aufgenommen werden nur Begriffe, die im UI erscheinen und ohne Definition zu Missverständnissen führen. Selbsterklärende Alltagsbegriffe wie „Ehepaar" oder „Witwe" bleiben draußen. Aufgenommen bleibt „Rechtsgeschäft", weil es der Gegenstand der Datenbank ist und seine Abgrenzung zu [[glossar#Event]] im UI-Kontext präzise sein muss.

Offen: die konkrete Liste der Grundabfragen im Bereich Analyse. Sie wird mit dem Fachteam festgelegt und lebt vermutlich als eigener Bereich unter [[ui-design#Analyse]] weiter.
