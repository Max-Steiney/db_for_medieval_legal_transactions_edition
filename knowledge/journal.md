---
title: Journal
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.3
created: 2026-02-19
updated: 2026-05-17
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
related: [decisions, specification, architecture]
---

# Journal

Arbeitstagebuch. Einziges chronologisches Dokument der Wissensbasis.

Format pro Eintrag: Datum, Kurztitel, ein bis drei Absätze. Was umgesetzt wurde, warum (oft mit verworfener Alternative), wo das Detail zeitlos abgelegt ist. Was nicht rein darf: Personennamen, Meeting-Protokolle, Projektmanagement-Stand, Quantitäten des Korpus, Test- und Build-Zahlen.

Einträge in umgekehrt chronologischer Reihenfolge, neueste oben.

## 2026-05-17 Stufenmodell datenseitig wirksam, neue Subkorpora freigegeben

Das tags zuvor als CLI-Gerüst eingeführte [[decisions#Stufenmodell für Korpus-Auswahl und Annotationsebenen|Stufenmodell]] wird datenseitig aktiv. Im Pipeline-Repo zwei neue `_ready`-Subkorpora aus QGW und Satzbuch CD und die Korpus-Konstanten neu geordnet: `RELEASED_CORPORA` (Stufe 1), `ALL_READY_CORPORA` (Stufe 3, derzeit deckungsgleich mit Stufe 1), `ALL_TEI_CORPORA` (Stufe 4) als monotone Hierarchie. `active_corpora()` liest `FRONTEND_STAGE`.

Auf editorische Empfehlung werden die beiden neuen Subkorpora Teil von Stufe 1. Argument: sie zeigen die volle Bandbreite des Erfassungsschemas, insbesondere die konsequent ausgezeichneten Ortsbeziehungen und Mentioned-Events, und gelten als verbindliche Datengrundlage für künftige Frontend-Arbeit.

Beobachtung zu zwei der Forschungsfragen (Wachsgießer-Heirat, Lederindustrie-Hausbesitz): selbst Stufe 4 zeigt nur eine Person pro Uhlirz-Kategorie. Das `roleName_norm_matching.csv` hat das Mapping, aber die TEI-Quellen tragen die entsprechenden Berufsbezeichnungen in den vorhandenen Subkorpora selten. Die Frage ist datenseitig durch die editorische Lage der `occupation`-Annotation begrenzt, nicht durch den Aggregator. Befund in [verification/findings.md](../verification/findings.md). Tests entsprechend gehärtet, Detail in [[architecture#Test-Strategie]].

## 2026-05-16 Konstellations-Abfrage mit Beispiel-Einstieg

Die Abfragen-Sub-Seite (`/analysis/index.html`) wird von der Galerie-Wireframe auf eine strukturierte Konstellations-Abfrage umgestellt. N nummerierte Personenblöcke mit Rolle und optional Geschlecht und Beruf-Substring; globale Filter Zeitraum, Korpus und Verknüpfungs-Modus „im selben Rechtsgeschäft" gegen „in derselben Quelle"; Permalink, CSV-Export, Datenkorb pro Trefferzeile. Aggregator `frontend/aggregator/role_constellation.py`, Resolver `frontend/static/js/analysis-resolver.js`. Detail in [[decisions#Abfragen-Sub-Seite als Konstellations-Abfrage]] und [[analyse#Konstellations-Abfrage]].

Onboarding ergänzt den leeren Anfangszustand mit Beispiel-Chips, die typische Konstellationen vorsetzen. Leitsatz: was im Frontend als Beispiel sichtbar ist, darf Substring-getrieben sein, weil die Forscherin den Mechanismus im Personenblock sieht und korrigieren kann; was im Aggregator versteckt eine Zahl produziert, darf das nicht. Daraus folgt ein findings-Eintrag: die Heirats-Substring-Liste in `research_questions.py` ist provisorisch und gehört als typisierende Spalte `is_marriage` in `kin_norm_matching.csv` ins Pipeline-Repo.

## 2026-05-16 Stufenmodell, Inventar, Mentioned-Toggle und Wissensbasis-Konsolidierung

Vier zusammenhängende Arbeitsblöcke aus derselben Welle, ausgelöst durch eine Editorinnen-Mail mit Forschungsfragen und neuen Subkorpora.

Das **Stufenmodell** in `frontend/stages.py` bündelt Korpus-Auswahl und Annotationsebenen als zitierbares Profil; vier benannte Stufen, CLI-Flag `--stage N`. Statt für jede Anforderung einen weiteren Boolean-Schalter einzuführen, ist jede Aussage des Frontends jetzt interpretierbar als Aussage unter einer bestimmten Stufe. Detail in [[decisions#Stufenmodell für Korpus-Auswahl und Annotationsebenen]].

Der **Mentioned-Event-Vergleichsstand** ist als Build-Flag realisiert, nicht als UI-Toggle. `--include-mentioned` ist Alias auf Stufe 2 und schreibt nach `docs-with-mentioned/`. Verworfen: UI-Toggle (zu viel Code für die Frequenz, in der der Vergleich gemacht wird) und nur-KPI-Toggle (inkonsistent, weil Auswertungen und Netzwerk unverändert blieben). Detail in [[decisions#Mentioned-Event-Vergleichsstand als Build-Flag]].

Das **TEI-Inventar** als vierter Verifikationsmodus (`verification/inventory.py`) scannt pro Subkorpus jedes Element samt Attributen und Top-Werten. Env-Var `VERIFY_SOURCES_DIR` erlaubt Scan gegen alternative Clones. Detail in [[architecture#Test-Strategie]].

Die **Wissensbasis-Konsolidierung** löst zwei Klassen von Befunden auf. Strukturell: alle Wiki-Links auf das frühere `requirements`-Dokument sind auf [[specification]] umgelegt. Inhaltlich: die Forschungsfragen aus der Mail leben als User-Stories in [[scholar-user-stories]] und als Implementierungs-Achse in [[decisions#Forschungsfragen als Implementierungs-Achse]]; die Karten-Idee in [[exploration]] umformuliert von „bewusst nicht vorgesehen" auf „in Stufe 4 angelegt, datenseitig deferred".

Im selben Zug: Stiftungsnetzwerk-Sektion auf den Org-Profilseiten, occ-Netzwerk-Aggregator (Template-Sektion noch offen), Galerie-Resolver für Uhlirz-Kategorien (UI-Anbindung steht aus). Verifikations-Säule 4 (`verification/research_questions.py`) leitet pro Forschungsfrage die erwartete Zahlen-Antwort aus TEI plus CSV ab; vergleicht zunächst nicht gegen das Frontend-Resultat, sondern liefert die Referenzzahlen.

## 2026-05-11 Verifikations-Säulen ausgebaut, Reader-Robustheit, Befunde-Register

Das Verifikations-Set hat jetzt drei Säulen plus Inventar: TEI zu JSON, Pipeline-CSV zu HTML, TEI direkt zu HTML. Die dritte Säule (`--tei-html`) liest TEI-Quellen direkt und vergleicht `<rs ref="…">` mit `data-ref="…"` im gerenderten HTML, sodass Pipeline-Drops und Renderer-Halluzinationen in beide Richtungen aufgedeckt werden. Wichtige Erkenntnis: das Profil listet eine Quelle auch dann, wenn die Person nur indirekt über `roleName/@corresp` referenziert wird; der Cross-Check addiert `data-corresp` zu `data-ref`. Detail in [[architecture#Test-Strategie]].

Die HTML-Reader fangen Lese-Fehler ab und liefern statt eines Crashs ein leeres Datenobjekt mit `read_failed=True`. Belastbare Mismatches landen namentlich in [verification/findings.md](../verification/findings.md).

Verworfen: pytest-Integration der Säulen 2 und 3. Vollständige Läufe dauern mehrere Minuten, das ist für normale Test-Runs zu lang. Separater Runner bleibt schlanker.

## 2026-05-11 Org-Detail-Profile, Datenkorb auf drei Typen, Ortsregister entfernt

Organisationen tragen jetzt eigene Detail-Profile parallel zu den Personen-Profilen (`frontend/aggregator/org_profiles.py`); `<rs type="org">` verlinkt direkt aufs Profil, die Sackgasse ist geschlossen. Mirror-Beziehungen auf Personenprofilen ergänzt: wenn jemand als `related_key` in `occ_relations_in_sources.csv` auftaucht, erscheint auf dem Bezugs-Profil eine Sektion „Personen mit Beruf in meinem Bezug". Schließt eine vorher systematisch einseitige Asymmetrie.

Der Datenkorb sammelt jetzt drei Item-Typen (Quellen, Personen, Organisationen) mit je eigener Tabelle, Remove- und CSV-Aktion. Kern-Mechanik: Ableitung als sichtbare Schicht. Legt jemand eine Quelle in den Korb, lädt `basket.js` lazy `docs_entities.json` und legt die zugehörigen Entitäten als abgeleitete Einträge ohne `gathered`-Flag nach; sie erscheinen kursiv und gedimmt, ein +-Klick stuft sie zur eigenständigen Sammlung hoch. Detail in [[decisions#Datenkorb als clientseitige Sammlung]].

Im selben Zug das Ortsregister entfernt. Es war nie freigegeben; Orts-Aussagen liegen außerhalb des Forschungsfokus, ein eigenes Register würde Bearbeitungstiefe vortäuschen. `<rs type="place">` bleibt als Inline-Span im Volltext mit Tooltip, ohne Sprungziel. Detail in [[decisions#Register-Freigabe]].

## 2026-05-11 Konsolidierungs-Welle

Mehrere durchgreifende Refactors im selben Zug. Tooltip-System in eine gemeinsame Mechanik mit vier Varianten zusammengeführt (Provenienz, Glossar, UI-Hilfe, Hover-Hint). Aggregator-Module umbenannt von `epic_a/b/c` zu `roles/relations/transactions`, fachliche Domänen statt Sprint-Codenamen. Top-Navigation einheitlich in `base.html` ohne Duplikate. Begriff „Factoid" aus dem Frontend entfernt, im DH-Kontext etabliert, hier redundant zur dichten Begriffsfamilie (Nennung, Gesamtnennung, Individuelle Person, Event).

## 2026-05-03 Exploration-Sub-Seiten Zeitstrom und Personennetzwerk

Zwei Sub-Seiten unter `/exploration/` plus geteilte Visualisierungs-Schicht. **Zeitstrom** als gestapelter Bar-Chart pro Jahrzehnt mit umschaltbarer Stapel-Achse (Korpus, Erschließungsform, Geschlecht, Top-Transaktionstypen) und Brush-zu-Drill-down. **Personennetzwerk** als Ego-Layout, Klick auf einen Nachbar verlagert das Zentrum. Detail in [[exploration]].

Bewusst gegen Force-Layout: die meisten Co-Occurrence-Kanten haben Gewicht eins, ein Strukturartefakt der Urkundenform. Ein globales Force-Layout würde als unleserliches Knäuel erscheinen. Das Ego-Layout schneidet stattdessen pro Schritt einen lesbaren Ausschnitt, analog zum klassischen Genealogie-Stammbaum.

Im selben Zug die geteilte Visualisierungs-Schicht in `viz-core.js` extrahiert: Domain-Konstanten, Range-Slider, Active-Filter-Strip, URL-Sync, Drill-Overlay, JSON-Loader, CSP-sichere Style-Projektion über `data-*`-Attribute. Eine neue Sub-Seite muss das Filter-Boilerplate nicht wiederholen. Detail in [[architecture#Geteilte Visualisierungs-Schicht]].

## 2026-05-03 URL-Sync, Cross-Page-Sprung, Drill-down

Drei verbundene Verbesserungen schließen die Workflow-Brüche zwischen den Seiten. **URL-Sync** serialisiert den Filter-Stand per `history.replaceState` in die URL und liest ihn beim Page-Load wieder ein; jeder Forschungsstand wird Permalink. `pushState` wäre falsch, weil Browser-Back nicht durch Filter-Mikrostände gehen soll. **Cross-Page-Sprung** als Footer-Link in den Drill-Containern öffnet die Quellen-Liste mit übernommenem Zeitraum-und-Geschlecht-Filter; Mapping ist asymmetrisch, weil das Quellen-Filter-Vokabular nicht symmetrisch zur Sex-Achse ist. **Drill-down** macht jede Donut-Arc, Bar und Bezeichnungs-Zeile klickbar; das gemeinsame Drill-Overlay zeigt die beitragenden Quellen. Detail in [[decisions#Forschungsstand zitierbar via URL-Parameter]] und [[decisions#Cross-Page-Sprung mit Filter-Übernahme]].

## 2026-05-03 Auswertungs-Seite Rework und Verschiebung in den Analyse-Bereich

Die Auswertungs-Seite hatte vier dichte Aggregat-Tabellen mit Zeilen- und Spalten-Prozenten. Stakeholder-Kritik: zu wenig visuell, zu viel statisch. Rework zu zwei Donuts (Funktionsrollen, Beziehungstypen), einem horizontalen Bar-Chart (Transaktionstypen mit aufklappbarer „Sonstige"-Sammelreihe) und einer scrollbaren Bezeichnungs-Tabelle mit Mini-Bars. Detail-Tabellen pro Donut bleiben als aufklappbares `<details>`.

**Strukturelle Verschiebung:** Die Seite lag bis dahin unter `/exploration/auswertungen.html`. Inhaltlich ist sie analytische Visualisierung (filter-getrieben, vorgegebene Achsen), keine offene Erkundung. Verschiebung nach `/analysis/auswertungen.html`. Nav: ein Dropdown „Analyse" mit „Auswertungen" und „Abfragen". Detail in [[decisions#Auswertungen gehört in den Analyse-Bereich]] und [[decisions#Exploration und Analyse als getrennte Bereiche]].

## 2026-05-02 Personen-Profilseiten und Tooltip-Trennung

Personennamen waren bisher Sackgassen (Hash-Anker auf das JS-gerenderte Register, wo der Anker nicht ankam). Jede individuelle Person bekommt jetzt eine eigene Profilseite unter `register/persons/<pe__id>.html`, gespeist aus `frontend/aggregator/person_profiles.py`. Joint Stammdaten, Quellenvorkommen, Rollen-Aggregation und fünf Beziehungs-CSVs. kin/friend/rep werden bidirektional aufgelöst; die Verwandtschafts-Lücke (eine Person sieht nur eine Seite einer kodierten Ehe) ist geschlossen.

Verworfen: einzelne `person_profiles.json` mit allen Profilen (zu groß für ein server-gerendertes Feature), Tab-Bar Lebenslauf/Beziehungen/Quellen (gegen das Maximaler-Informations-Output-Prinzip aus [[ui-design]]). Detail in [[decisions#Personen- und Organisationsprofile als Detailseiten]].

Die Tooltip-Komponente wird in zwei eigenständige Varianten zerlegt: **Glossar-Tip** an Begriffen (kompaktes `i`-Icon), **Provenienz-Tip** an Zahlen (gepunktet unterstrichen, öffnet XPath und Filter-Hinweis). Schema beim Ausrollen auf weitere Seiten konsistent: Glossar an Begriffen, Provenienz an Zahlen. Detail in [[ui-design#Tip-System]].

## 2026-05-01 Analyse-Seite Richtung A umgesetzt

Die Analyse-Seite war kurz als Slot-Workbench mit Familien-Tab-Bar als oberster UI-Ebene gebaut und auf eine kuratierte Frage-Galerie mit Result-Panel und Custom-Builder umgebaut. Frage als first-class concept, nicht an eine Familie gebunden. Permalinks doppelt: `#q=<id>` für die Galerie, `#f=<fid>&…` für den Custom-Builder.

## 2026-04-17 Terminologie-Konsolidierung, Erschließungsform, Provenienz-Ausrollung

UI-Terminologie durchgehend auf die kanonischen Begriffe aus [[glossar]] und [[decisions#Begriff Quellenkorpus]] gezogen. „Dokument(e)" zu „Quelle(n)", „Rechtsakt(e)" zu „Rechtsgeschäft(e)", verbliebene „Sammlung"-Spaltenkopfzeile zu „Quellenkorpus". Technische Labels auf HTML-Ebene (ARIA, CSS-IDs) bleiben unberührt. Die Erschließungsform eines Quellenkorpus ist an den Korpus-Chips sichtbar (QGW: „Regest + Faksimile", Stadtbücher: „Volltext"). Provenienz-Tooltip von den Startseiten-KPIs auf weitere Seiten ausgerollt.

## 2026-04-17 Startseiten-Layout, Datenstand-Korrektur

Startseite konzeptionell neu geordnet: zwei gleichberechtigte Säulen Exploration und Analyse nebeneinander, statt einer einzelnen Exploration-Sektion mit Trennstrich. Eyebrow-Labels in Sans-Caps markieren die Bereiche. Footer trennt Datenstand und Build-Datum. Bis zuletzt zeigte „Datenstand" das Build-Tagesdatum, was inhaltlich falsch ist. Datenstand ist jetzt das Datum des letzten Commits im Pipeline-Repo, ermittelt über `git log -1 --format=%cI`. Hilfsfunktion in `frontend.build._pipeline_repo_data_date()`.

Begleitend [[glossar#Gesamtnennung]] präzisiert: die Zählebene ist quellenbereinigt, Mehrfacherwähnungen einer Person in derselben Quelle werden zu einer Nennung zusammengefasst. Detail in [[decisions#Quellenbereinigte Zählung]].

## 2026-04-17 Verifikations-Test-Set entsteht

Im Edition-Repo entsteht ein eigenständiges Verifikations-Test-Set in Python mit lxml. Liest TEI-Quellen und Register-XMLs unabhängig ein, rechnet Aggregate nach und vergleicht mit den JSON-Ausgaben unter `/data/`. Detail in [[decisions#Verifikations-Test-Set als eigenständige Komponente]] und [[architecture#Test-Strategie]].

Befund im Erstlauf: der UI-Wert „Gesamtnennungen Personen" war tatsächlich die Anzahl individueller Personen; Label korrigiert.

## 2026-04-17 URL-Refactor und deutsche UI

Die flache Root-Struktur wird auf semantische Unterordner umgebaut: `register/`, `exploration/`, `analysis/`, `project/`. JavaScript adressiert die JSON-Indexe über `window.ROOT_PATH`, damit die Auslieferung auch aus Unterordner-Tiefe funktioniert. UI durchgängig auf Deutsch, Englisch bleibt in Pfaden und im Code. Quantitäten aus Templates entfernt, an die Pipeline-Repo-Konfiguration gebunden. Hardcoded Zahlen gelten ab jetzt als Fehler. Detail in [[decisions#Titel und Untertitel]].

## 2026-04-17 Entstehung der Wissensbasis

Anlass war die Einarbeitung von Feedback zum Frontend. Die Wissensbasis ist als Obsidian-kompatibler Markdown-Ordner angelegt. Pro Dokument gilt zeitlose Formulierung ohne Projektmanagement-Artefakte und ohne Quantitäten des Korpus. Verworfen: README und Unterordner-Gliederung, weil die flache Struktur den Vault in Obsidian unmittelbar nutzbar macht. Detail in [[decisions#Zeitlose Formulierung der Wissensbasis]] und [[decisions#Obsidian-kompatibles Knowledge-Format]].

Für das Glossar wurde ein Kriterium festgelegt: aufgenommen werden nur Begriffe, die im UI erscheinen und ohne Definition zu Missverständnissen führen. Selbsterklärende Alltagsbegriffe bleiben draußen. Aufgenommen bleibt „Rechtsgeschäft", weil seine Abgrenzung zu [[glossar#Event]] im UI-Kontext präzise sein muss.
