# Journal

Arbeitstagebuch. Einziges chronologisches Dokument der Wissensbasis.

Format pro Eintrag: Überschrift mit Datum und Kurztitel, darunter eine knappe Notiz zum Fortschritt, zu Entscheidungspfaden, zu verworfenen Alternativen oder zu offenen Fragen. Verlinkt werden die Zieldokumente, nicht Personen oder Meetings.

Was hier rein darf: Fortschritt der Wissensbasis, Entscheidungspfade, die in [[decisions]] münden, verworfene Alternativen mit Begründung, offene Fragen, die beim Arbeiten auftauchen.

Was nicht rein darf: Personennamen, Meeting-Protokolle, Projektmanagement-Stand, Quantitäten des Korpus.

Einträge in umgekehrt chronologischer Reihenfolge, neueste oben.

---

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
