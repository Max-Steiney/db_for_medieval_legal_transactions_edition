---
title: Journal
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.1
created: 2026-02-19
updated: 2026-05-11
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
related: [decisions, requirements, architecture]
---

# Journal

Arbeitstagebuch. Einziges chronologisches Dokument der Wissensbasis.

Format pro Eintrag: Überschrift mit Datum und Kurztitel, darunter eine knappe Notiz zum Fortschritt, zu Entscheidungspfaden, zu verworfenen Alternativen oder zu offenen Fragen. Verlinkt werden die Zieldokumente, nicht Personen oder Meetings.

Was hier rein darf: Fortschritt der Wissensbasis, Entscheidungspfade, die in [[decisions]] münden, verworfene Alternativen mit Begründung, offene Fragen, die beim Arbeiten auftauchen.

Was nicht rein darf: Personennamen, Meeting-Protokolle, Projektmanagement-Stand, Quantitäten des Korpus.

Einträge in umgekehrt chronologischer Reihenfolge, neueste oben.

---

## 2026-05-11 Datenkorb auf drei Typen erweitert mit Ableitungs-Mechanik

Der Datenkorb sammelt jetzt nicht nur Quellen, sondern auch Personen und Organisationen. Drei Item-Typen mit kompaktem Schlüssel `type:id`, je eigener Tabelle auf der Korb-Seite, je eigener Remove- und Clear-Aktion, je eigenem CSV-Export.

Kern-Entscheidung **Ableitung als sichtbare Schicht**: legt eine Forscherin eine Quelle in den Korb, lädt `basket.js` lazy den Forward-Index `docs_entities.json` (Quelle → annotierte Entity-IDs, von `frontend/aggregator/docs` geschrieben) und legt die zugehörigen Entitäten als abgeleitete Einträge ohne `gathered`-Flag nach. Auf der Korb-Seite erscheinen sie kursiv und gedimmt mit „aus Quelle"-Rückverweis. Ein +-Klick stuft einen abgeleiteten Eintrag zur eigenständigen Sammlung hoch und macht ihn unabhängig von der Ursprungsquelle.

Verworfen: ein einzelner Sammler-Typ mit Mischtabelle. Die drei Typen brauchen unterschiedliche Spalten, und Forscherinnen wollen Personen aus dem Korb für Prosopografie separat exportieren, ohne Quellen-Zeilen mit zu schleppen.

## 2026-05-11 Detail-Profile für Organisationen, Ortsregister entfernt

Phase 1.5 / Phase 2 der Profilseiten-Idee aus 2026-05-02 abgeschlossen. Organisationen tragen jetzt eigene Detail-Profile, gerendert vom Aggregator-Modul `org_profiles`, parallel zu den Personen-Profilen. `<rs type="org">` im Quellen-Volltext verlinkt direkt aufs Org-Profil; die Sackgasse für Organisationen ist analog zur Personen-Lösung aus 2026-05-02 geschlossen.

Im selben Zug das **Ortsregister entfernt**. Es war ohnehin nie freigegeben; ein Code-Pfad für Ort-Detail-Seiten hatte sich aus einer früheren Iteration angesammelt. Begründung der Streichung: Orts-Aussagen liegen außerhalb des Forschungsfokus, ein eigenes Register würde Bearbeitungstiefe vortäuschen, die die Daten nicht hergeben. `<rs type="place">` bleibt als Inline-Span im Volltext mit Tooltip, ohne Sprungziel. Eintrag in [[decisions#Register-Freigabe]] umgeschrieben, Wiederaufnahme-Klausel gestrichen.

## 2026-05-11 Konsolidierungs-Welle

Mehrere kleinere, aber durchgreifende Refactors im selben Zug.

- **Tooltip-System** in eine gemeinsame Mechanik (`tip.js`, `tip.css`) mit vier Varianten zusammengeführt: `tip-popover--data` für Provenienz, `tip-popover--glossary` für Begriffsdefinitionen, `tip-popover--help` für UI- und Funktions-Hilfen und `data-hint`-Hover für leichte Selbsterklärungen. Gemeinsamer Open/Close-Pfad und Edge-Detection. Eine Aufteilung in separate JS-Komponenten wurde verworfen, weil die Mechanik substanziell gleich ist.
- **Aggregator-Module umbenannt** von `epic_a/b/c` zu `roles/relations/transactions`. Fachliche Domänen statt Sprint-Codenamen.
- **Top-Navigation** lebt einheitlich in `base.html` ohne Duplikate auf Sub-Seiten; Footer und Startseite kosmetisch entrümpelt.
- **Code-Kommentare** durchgängig auf Englisch (`frontend/` Python und JS). Inhaltliche Doku bleibt deutsch.
- **Begriff Factoid** aus dem Frontend entfernt. Im DH-Kontext etabliert, im hiesigen UI aber redundant zur bereits dichten Begriffsfamilie (Nennung, Gesamtnennung, Individuelle Person, Event). Interne Datenmodell-Namen bleiben unangetastet.

---

## 2026-05-03 Personennetzwerk als zweite Exploration-Sub-Seite, Karten-Idee verworfen

Zweite visuelle Sub-Seite unter `/exploration/`: ein **Personennetzwerk** als Ego-Layout. Eine Person sitzt im Mittelpunkt, ihre direkten annotierten Beziehungen liegen radial drumherum; Klick auf einen Nachbar verlagert das Zentrum, so wandert man durchs Netz. Personen-Suche, Beziehungstyp-Chips (Verwandtschaft / Beruf-Stand / Vertretung / Freundschaft) und URL-Sync sind die Bedien-Achsen. Detail-Tabelle unter dem Graphen listet alle Verbindungen mit Beziehungstyp, Bezeichnung, Beleg-Anzahl und „+"-Knopf für den Datenkorb (Personen-Sammlung).

Bewusst gegen Force-Layout: die meisten Co-Occurrence-Kanten haben Gewicht 1 — ein Strukturartefakt der Urkundenform, kein analytisch belastbares Beziehungsmaß. Ein Force-Layout über das Gesamt-Beziehungsnetz würde als unleserliches „Knäuel" erscheinen, in dem nichts erkennbar ist. Das Ego-Layout schneidet stattdessen pro Schritt einen lesbaren lokalen Ausschnitt — analog zum klassischen Genealogie-Stammbaum, nur mit Klick-Hopping als Navigation. Globale Topologie lässt sich daraus durch sequenzielles Erkunden rekonstruieren.

Datenpfad: relations-Aggregator wurde erweitert um das Feld `r` (related_key) in jeder rels-Eintrag, damit die Person-zu-Person-Kanten clientseitig rekonstruierbar sind. Vorher waren nur die Selbstreferenzen ohne Gegenüber im JSON. Aufwand: ein zusätzliches Feld pro rels-Eintrag, kein Schema-Bruch.

`occ`-Beziehungen (Beruf / Stand) zeigen Person → Organisation; sie werden als Knoten anderer Farbe (Sand) dargestellt, sind aber nicht weiter klickbar — Org-Profile gibt es noch nicht. Die anderen drei Typen (kin/rep/friend) tragen das Klick-Hopping.

**Karten-Idee verworfen.** Eine geographische Visualisierung war als dritte geplante Sub-Seite skizziert (siehe ältere Iterationen von `exploration.md`). Verworfen aus zwei Gründen: erstens fehlt die für eine sinnvolle Karte erforderliche flächendeckende Georeferenzierung des Ortsregisters (nur ein Bruchteil der Orts-Einträge hat Koordinaten), zweitens liegen Orts-Aussagen ohnehin außerhalb des Forschungsfokus der Datenbank. Knowledge-Dokumente sweepen-bereinigt von der Karten-Erwähnung; geplant bleibt nur noch das Sankey-Diagramm zu Transaktionsflüssen.

## 2026-05-03 URL-Sync, Cross-Page-Sprung, Datenkorb

Drei verbundene Verbesserungen, die die identifizierten Workflow-Brüche zwischen den Seiten schließen.

**URL-Sync** auf den Visualisierungs-Seiten: Filter-Stand (`dec`, `sex`, `type`, `q`, `mode` für Auswertungen; `dec`, `stack`, `brush`, `focus` für Zeitstrom) wird per `history.replaceState` in die URL serialisiert und beim Page-Load wieder eingelesen. Damit ist jeder Filter-Stand bookmark-fähig, teilbar, in einer Publikation zitierbar — ein Forschungsstand wird Permalink. `pushState` wäre falsch gewesen, weil Browser-Back nicht durch Filter-Mikrostände gehen soll. Default-Werte werden weggelassen, damit Sharing-URLs minimal bleiben. Eintrag in [[decisions#Forschungsstand zitierbar via URL-Parameter]].

**Cross-Page-Sprung** als Footer-Link in beiden Drill-Containern (Auswertungs-Drill-Overlay, Zeitstrom-Brush-Drill): „→ in Quellen-Liste öffnen" mit übernommenem Zeitraum-und-Geschlecht-Filter. Mapping ist asymmetrisch, weil das Quellen-Filter-Vokabular nicht symmetrisch zur Sex-Achse der Visualisierungen ist (`with-f` für ♀, `only-m` für ♂; `with-m` existiert nicht). Page-spezifische Filter (Rolle, Beziehungstyp, Bezeichnung, Tx-Kategorie, Stack-Fokus) werden bewusst nicht übertragen — die Quellen-Liste kennt sie nicht. Tooltip am Link macht die Lückenführung transparent. Eintrag in [[decisions#Cross-Page-Sprung mit Filter-Übernahme]].

**Datenkorb** als clientseitige Sammler-Schicht über allen Quellen-Listen. `localStorage` mit versioniertem Schlüssel `sugw-basket-v1`, Cross-Tab-Sync via `storage`-Event, In-Tab-Updates via Custom-Event. „+"-Knopf in den Listen-Renderern (Quellen-Tabelle, Drill-Overlay, Brush-Drill); Korb-Icon mit Live-Badge im Nav (in `base.html` verankert, also auf jeder Seite); eigene Korb-Seite (`/korb.html`) mit Liste, Remove, Clear und CSV-Export (UTF-8 mit BOM, Excel-kompatibel). Eintrag in [[decisions#Datenkorb als clientseitige Sammlung]].

Verworfen: Server-persistierter Korb mit Account. Anderer Stack (Auth, DSGVO, Speicherkosten) ohne erkennbaren Mehrwert für die jetzt bedienten Forschungsszenarien — der CSV-Export ist die Bridge in externe Werkzeuge (Zotero, BibTeX-Konverter, Excel). Verworfen auch ein Personen-Sammler in dieser Iteration: Personen tauchen aktuell nicht in den Visualisierungen auf, der Mehrwert läge erst nach den geplanten Personen-Profil-Drill-Pfaden vor.

## 2026-05-03 Drill-down auf der Auswertungs-Seite, Stack-Kategorie isolierbar im Zeitstrom

Die Auswertungs-Seite war bis dahin eine Drill-Sackgasse: „Hausfrau · 1.153 Personen" war sichtbar, aber kein einziger dieser Personen erreichbar. Donut-Arc, Bar und Bezeichnungs-Zeile waren tooltip-only.

Jetzt klickt jedes dieser Elemente das gemeinsame Drill-down-Overlay auf — Donut-Arc und Legend-Item für Funktionsrollen ([[architecture#Provenienz-Indizes|`roles.drill_down.role_sex`]]), dito für Beziehungstypen (`relations.drill_down.type_sex`), Bar für Transaktionstypen (`transactions.drill_down.tx_type_decade`), Tabellenzeile für Bezeichnungen (`relations.drill_down.label_sex`). Der Geschlechter-Filter wird über sex-Suffixe im Lookup-Schlüssel mitgenommen (`kin_f`, `hausfrau__f`); der Zeitraum-Filter nativ bei decade-partitionierten Drills (Tx) und bei den anderen über Datums-Parsing aus `docs_lookup.json`. Auflösung der `file_keys` lazy beim ersten Klick, eager im Hintergrund vorgeladen. Eintrag in [[decisions#Auswertungen gehört in den Analyse-Bereich]] erweitert um die Drill-Pfade.

Im Zeitstrom war der Brush bisher unscharf: „1390er" lieferte 730 Quellen aller Tx-Typen gemischt, einzelne Stapel-Kategorien waren nicht isolierbar. Jetzt fokussiert ein Klick auf ein Legend-Item eine Kategorie — die anderen Bar-Segmente dimmen, der Drill filtert auf die fokussierte Kategorie. Bei Stack=Tx läuft der gefilterte Drill über `transactions.drill_down.tx_type_decade` und löst die `file_keys` über `docs_lookup` auf; bei den anderen Stacks (collection/form/sex) filtert der Renderer das `DOCS_BY_DECADE`-Set in-memory mit der `assign`/`assignAll`-Funktion der Stack-Definition.

Verifiziert über drei Forschungsfragen: „Welche Personen heißen 'wittib'?" (Bezeichnungs-Drill, vorher Sackgasse), „Welche Schuldbrief/Pfand-Geschäfte 1390er?" (Stack-Fokus + Brush, vorher unscharf), „Welche Quellen 1390er nur weiblich?" (Cross-Nav in Quellen-Liste mit übernommenen Filtern). Pattern für die nächsten Sub-Seiten (Personen-Netzwerk, Karten): die viz-core-Drill-Funktionen sind generisch genug, dass die neuen Sub-Seiten sie wiederverwenden können.

## 2026-05-03 Zeitstrom als erste Exploration-Sub-Seite, viz-core-Refactor

Erste Sub-Seite unter `/exploration/`: ein gestapelter Bar-Chart der Quellendichte pro Jahrzehnt mit umschaltbarer Stapel-Achse (Quellenkorpus, Erschließungsform, Geschlecht-der-Beteiligten, Top-8-Transaktionstypen) und Brush-zu-Drill-down. Datenquellen: `data/search.json` für die ersten drei Stapel-Achsen clientseitig aggregiert, `transactions.tx_timeline` für die Tx-Stapelung. Drill-Liste verlinkt direkt in die Quellen-Detailseiten.

Vier Variationen waren skizziert (Timeline-Strom, Personen-Netzwerk Force-Layout, Ego-Netzwerk radial, Quellen-Galaxie als Scatter); Timeline gewählt, weil die Daten 100 % verfügbar sind, das Drill-down-Pattern aus den Auswertungen wiederverwendbar ist und die Sub-Seite ohne externe Lib auskommt. Personen-Netzwerk wurde für später aufgespart, weil das Knäuel-Risiko bei 8.406 Personen mit überwiegend Gewicht-1-Kanten harte Filter-Defaults zwingen würde — riskanter als erstes Stück.

Im selben Zug ein zweiter Refactor-Pass nach dem ersten innerhalb der Auswertungs-Seite: die geteilte Infrastruktur wandert in `viz-core.js` (Domain-Konstanten, Number-Formatting, Dekaden-Filter, CSP-sichere Style-Projektion über `data-*`-Attribute, Chip-Toggle, Range-Slider-Binding, Active-Filter-Strip, JSON-Loader, später Drill-Overlay + URL-State + Cross-Nav-Builder). Beide Visualisierungs-Seiten nutzen das Modul; eine neue Sub-Seite muss das Filter-Boilerplate nicht wiederholen. Zeilen-Bilanz: `analysis-aggregat.js` von 832 auf ~520, `exploration-timeline.js` von ~580 auf ~376. Eintrag in [[architecture#Geteilte Visualisierungs-Schicht]].

CSP-Falle unterwegs: `style-src 'self'` blockiert inline `style="…"`-Attribute, was die Bar-Fills und M/W-Mini-Bars auf 0px clampte. Lösung: Werte werden als `data-w` / `data-bg` / `data-h` codiert und nach jedem `innerHTML` über `applyDataStyles()` per JS-IDL auf die `style`-Property projiziert — CSP-konform.

## 2026-05-03 Auswertungen-Seite Rework und Verschiebung in den Analyse-Bereich

Die Auswertungs-Seite hatte vier dichte Aggregat-Tabellen mit `% Zeile / % Spalte` und KPI-Header. Stakeholder-Kritik: zu wenig visuell, zu viel statisch, dichte Tabellen ohne erkennbares Pattern. Rework in mehreren Iterationen.

**Visualisierung:** zwei Donuts (Funktionsrollen, Beziehungstypen) mit Legende-pro-Eintrag-mit-M/W-Mini-Bar, ein horizontales Bar-Chart (Transaktionstypen mit aufklappbarer „Sonstige"-Sammelreihe), eine scrollbare Tabelle (alle 1.244 Bezeichnungen, vorher Top-15) mit Mini-Bar-Personen-Spalte und gestapelter M/W-Bar. Detail-Tabellen pro Donut bleiben als aufklappbares `<details>` für Forschende, die die ursprünglichen `% Zeile / % Spalte`-Werte brauchen.

**Sprache und Farbe:** Rollen-Labels gegendert („Aussteller / Ausstellerin", „Empfänger / Empfängerin", „Siegler:in / Zeug:in", „keine Rolle"); Geschlechter-Visualisierung in Aubergine/Petrol statt Blau/Orange — bewusst klischee-frei, ohne Konflikt mit den Donut-Paletten (siehe [[ui-design#Farbkodierung und Typografie]]); „Beziehungen" statt „Kanten"; Pluralisierung im Slider-Tooltip („1 Quelle" / „N Quellen") über neuen Macro-Parameter `unit_singular`. M/W-Bar in der Legende immer sichtbar — auch wenn Geschlechter-Filter aktiv ist.

**Strukturelle Verschiebung:** Die Seite lag bis dahin unter `/exploration/auswertungen.html`. Inhaltlich ist sie aber analytische Visualisierung (Donut + Bar + Verteilungstabellen, filter-getrieben), keine offene Erkundung — Donut und Bar sind nach DH-Standard analytische Display-Klasse, nicht explorative Information-Visualisation. Verschiebung nach `/analysis/auswertungen.html`; Template `analysis_aggregat.html`, JS `analysis-aggregat.js`. Nav: ein Dropdown „Analyse" mit „Auswertungen" + „Abfragen", separat von einem späteren „Exploration"-Dropdown. Begründung in [[decisions#Auswertungen gehört in den Analyse-Bereich]] und [[decisions#Exploration und Analyse als getrennte Bereiche]] (letztere neu gefasst: Trennung folgt Interaktionsmodus, nicht Inhalt).

Erster Refactor-Pass am Ende: Helper extrahiert (Chip-Active-Toggle 6× dupliziert → `setActiveChip`, M/W-Bar-Markup 2× → `sexBarHTML`), toter Code raus (`bindCorpusFilter` gegen einen entfernten Block, unbenutztes `ROOT_PATH`), `bindReset` über die Helfer vereinfacht. Reduktion von 834 auf 523 Zeilen ohne Verhaltensänderung — die Vorbereitung für den `viz-core`-Refactor zwei Iterationen später.

---

## 2026-05-02 Person-View Phase 1: Profilseiten pro Entität

Bisher waren Personennamen in der Datenbank Sackgassen: in der Annotations-Tabelle der Quellen-Detailseite und im Volltext klickbar, aber nur als Hash-Anker auf das Listen-Register `register/persons.html#pe__id`, wo der Anker im JS-gerenderten Index nicht ankam. Beziehungs-Daten lagen im Pipeline-Output (`kin_relations_in_sources.csv`, `friend_/rep_/occ_/title-ref_relations_in_sources.csv`), waren aber nirgends UI-seitig sichtbar. Beispiel: Simon Pötel und Anna Pötlin sind im TEI als Ehepaar codiert, im Frontend war diese Verwandtschaft nicht einsehbar.

Phase 1 macht jede [[glossar#Individuelle Person]] zu einer eigenen Profilseite unter `register/persons/<pe__id>.html`. Quelle der Daten ist der neue Aggregator `frontend/aggregator/person_profiles.py`: er joint Stammdaten aus `persons.csv` (Name, Geschlecht, Tod, Notiz, Wien-Wiki-Link), Quellenvorkommen aus dem bestehenden `reverse_index`, Rollen-Aggregation aus `persons_in_events.csv` und Beziehungen aus den fünf Relations-CSVs. Die Brücke zwischen `file_key` (z. B. `f__QGW_10`) und konkreter Quellen-URL läuft über `filenames.csv`, weil die Pipeline-CSVs file_key-zentriert sind und `reverse_index` idno-zentriert.

Beziehungs-Modell: kin/friend/rep werden bidirektional aufgelöst (eine CSV-Zeile erscheint im Profil beider Seiten), occ und title-ref nur in der Subjekt-Sicht (das Gegenüber ist eine Organisation, die noch keine Profilseite hat). Pro Beziehungseintrag wird die Quelle als Nachweis verlinkt. Damit ist die Verwandtschafts-Lücke geschlossen: Diemut → Berthold (Gemahlin) und Berthold → Diemut (Counterpart) erscheinen jeweils im Profil der anderen Person, mit Klick-Pfad zur Quelle.

Verlinkungs-Pfade: `frontend/renderer.py` zeigt `<rs type="person" ref>` jetzt auf das Profil statt auf das Listen-Register; die Annotations-Tabelle in `document.js` setzt Personennamen als Profil-Links; das Personenregister `register/persons.html` linkt die Namens-Spalte aufs Profil, der Quellen-Badge bleibt Inline-Detail-Trigger (Quellen einsehen ohne Seitenwechsel). Org/Ort-Refs sind unverändert — Phase 2 öffnet sie analog.

Verworfene Alternativen: (a) ein einzelnes `person_profiles.json` mit allen Profilen — gewonnen wäre Client-Lazy-Loading-Möglichkeit, verloren wären zwei MB JSON für ein Feature, das aktuell rein server-gerendert ist; daher in-memory-Pipeline ohne JSON-Zwischenstufe. (b) Tab-Bar Lebenslauf/Beziehungen/Quellen — gegen das „maximaler Informations-Output"-Prinzip aus [[ui-design]], permanente Sichtbarkeit aller Sub-Bereiche schlägt schmaleres Tab-Switching. (c) `<rs>`-Spans im Volltext zusätzlich mit Cursor-Pointer markieren — verworfen, weil sie ohnehin schon `<a>`-Tags sind und Browser-Default-Hover ausreicht.

Korpus-Lücke beim Smoke-Test: das Pötel-Paar selbst ist nur in `Vienna_1458-66` belegt, das nicht im freigegebenen Korpus liegt. Profile für beide existieren also nicht — funktional korrekt, weil das Released-Set die Profil-Menge bestimmt. Sobald QGW II/2 freigegeben wird, taucht das Paar automatisch auf. Verifiziert wurde das Feature stattdessen am Paar Diemut/Berthold (Nr. 10, 1274) und an Alexander III. (Beruf-Beziehung zur Vatikan-Org).

Build-Zahlen: 8.441 Profile, Build-Zeit von ~18 s auf ~19 s. Tests: 333 grün, 32 skipped. Die Profilseite selbst ist absichtlich schlank gehalten (Toolbar mit Breadcrumb + Meta-Strip, Header mit Name + Notiz + Quellen-Titel-Chips, Beziehungs-Block, Quellen-Tabelle) und auf Vereinheitlichung mit der Quellen-Detailseite ausgelegt. Stat-Karten (Quellen-Count, Rollen-Aufschlüsselung, Beziehungs-Count) wurden nach erstem Wurf wieder entfernt — sie brachen die Konsistenz zur restlichen UI.

Offen für eine eigene Session — Phase 1.5 / Phase 2:

- **Profilseite reicher.** Vier Achsen, in absteigender Schmerz-Reihenfolge: (1) Header als richtige Visitenkarte (Name groß, Lebensspanne als Pille, Sex-Symbol, Wien-Wiki-Link prominent statt im Footer); (2) Beziehungs-Tabellen als Listen-/Karten-Form, weil Tabellen bei 1–3 Einträgen klobig wirken; (3) Quellen-Tabelle um Rolle-pro-Quelle, Erschließungsform-Icon und Faksimile-Indikator ergänzen, damit pro Zeile sichtbar ist, *was* die Person dort tat; (4) Mention-Kontext-Snippet, also der Satz aus dem TEI rund um den jeweiligen `<rs>`-Span — am wertvollsten, weil „wie wird die Person beschrieben" ohne Quellen-Öffnen sichtbar wäre, und am aufwendigsten.

- **Org-Profile / Ort-Profile (Phase 2).** Datenmodell-seitig schon vorhanden (`organisations.csv`, `places.csv`, `orgs_in_sources.csv`, `places_in_sources.csv`, `topo_relations_in_sources.csv` für Topographie). Verworfen für Phase 1, weil die Beziehungs-Substanz bei Personen am dichtesten ist und das Pötel-Beispiel dort liegt. Bei Org-Profilen wird die occ-Beziehung dann von beiden Seiten sichtbar (Person mit Amt → Org mit ihren Amtsträger:innen).

---

## 2026-05-02 Tooltip-Komponenten getrennt, Toggle entfernt

Die Startseiten-Card „Quellen durchsuchen" wird konzeptionell aufgeräumt. Der Toggle „Erwähnte Geschäfte einbeziehen" über der Korpus-Matrix entfällt. Begründung: Die Matrix-Werte werden nicht mehr zwischen zwei Zählebenen umgeschaltet, sondern zeigen einheitlich die quellenbereinigte Default-Variante (Personen in verschachtelten rs-Events ausgeschlossen, vgl. [[glossar#Gesamtnennung]]). Die parallele Aggregator-Schicht für die inklusive Variante (`person_mentions_with_mentioned`, `distinct_events_with_mentioned`, der zweite XPath-Loop über alle rs-Events) ist damit ohne Konsumenten und wird aus `frontend/build.py` entfernt. Für eine zukünftige Wiedereinführung als globaler Zählebenen-Umschalter (vgl. [[requirements#Umschaltbarkeit der Zählebenen]]) gibt es einen sauberen Rebuild-Pfad — der Aggregator hat keinen verkrusteten Toggle-Zustand mehr.

Der Begriff **Event** bleibt im UI bewusst stehen, gegen den ersten Impuls, ihn durch „Rechtsgeschäft" zu ersetzen. Die `events_in_sources.csv` zeigt, dass die `<rs type="event">`-Annotation heterogen ist: 2.025 `abstract` (das eigentliche Regest), 1.565 `seal` (Siegelvermerke), 439 `entry` (Kanzleivermerke), 47 `nota`, plus 138 ohne Kategorie. Nur `abstract` deckt sich mit der Glossar-Definition von [[glossar#Rechtsgeschäft]]. „Rechtsgeschäft" als Spaltenlabel wäre für die Begleitelemente zu eng; „Event" ist der ehrlichere Sammelbegriff und respektiert das technische Vokabular der TEI-Annotation. Eine separate Aufschlüsselung pro `event_in`-Kategorie bleibt eine offene Designfrage für eine spätere Session.

Die Tooltip-Komponente wird in zwei eigenständige Varianten zerlegt, weil sie zuvor zwei verschiedene Aufgaben in einem Popover gemischt hat. **Glossar-Tip** (Macro `glossary_tip`): kompaktes `i`-Icon neben einem Begriff, öffnet die Begriffsdefinition mit Link zum Glossar. **Provenienz-Tip** (Macros `prov_stat` + `prov_popover`): an einer Zahl, gepunktet unterstrichen, öffnet den Verifikations-XPath und einen kurzen Hinweis zur Filterung. Beide Komponenten teilen die JS-Logik aus `provenance.js` (gleiche `data-prov-trigger`-Mechanik), unterscheiden sich aber in Trigger-Form und Inhalt. Auf der Startseite folgt die Korpus-Matrix dem Schema: jeder Spalten-Header trägt einen Glossar-Tip, die Gesamt-Zahlen in der `tfoot`-Zeile tragen einen Provenienz-Tip. Die Zellen pro Korpus bleiben einfache Zahlen, weil ihre Provenienz mit der Spalten-Summe übereinstimmt. Beim Ausrollen auf weitere Seiten (Exploration-Subpages, Datenqualität, Statistik — vgl. [[journal]]-Eintrag 2026-04-17) sollte das Schema konsistent gehalten werden: Glossar an Begriffen, Provenienz an Zahlen.

Begleitend wird der Provenienz-Popover-Container auf horizontale Edge-Detection erweitert. Beim Öffnen prüft `clampToViewport` in `provenance.js`, ob das Popover über `documentElement.clientWidth - margin` hinausragt, und kompensiert über `transform: translateX(...)`. Der Pfeil bleibt am ursprünglichen Trigger ausgerichtet via CSS-Variable `--prov-arrow-offset`. Ohne diesen Mechanismus war die Personenregister-Card am rechten Rand der Startseite betroffen.

Drei kleinere Refactors: (1) `var` → `let` projektweit über alle JS-Files in `frontend/static/js/`. Ein TDZ-Bug in `index.js` (`rangeSlider` wurde im Init-Callback gelesen, bevor `initRangeSlider()` zurückkehrte) wurde durch eine Forward-Deklaration `let rangeSlider;` am Funktionsanfang behoben. (2) Die Korpus-Matrix in `frontend/templates/startseite.html` zieht ihre Spalten-Configs (Label, Glossar-Definition, Verifikations-XPath, Provenienz-Note) aus einer Liste `_compute_matrix_columns()` in `build.py`. Eine zusätzliche Spalte braucht jetzt nur einen weiteren Eintrag in dieser Liste, kein dupliziertes Template-Markup. (3) Spalten-Header `Quellenkorpus` ergänzt, damit die erste Spalte der Matrix nicht mehr unbeschriftet ist.

---

## 2026-05-01 Analyse-Seite Richtung A umgesetzt und refactored

Die [[analyse|Analyse-Seite]] ist von der Slot-Workbench (Phase 1, Familien-Tab-Bar als oberste UI-Ebene) zu **Richtung A** umgebaut: kuratierte Frage-Galerie als Einstieg, einziges Result-Panel als zentrale Antwort-Bühne, Custom-Builder darunter im `<details>` für freie Slot-Kombinationen. Der Tab-Bar-Ansatz wurde verworfen, weil er Familien als oberste Mental-Model-Ebene aufzwang — die Galerie bietet stattdessen direkten Zugriff über die Forschungsfrage selbst.

Architektur-Entscheidung **Frage als first-class concept**: Eine Frage ist autonom (`{ id, group, text, dataFiles, viz, answer, resolveViz, resolveComparison, resolveDrillDown, coverage }`), nicht an eine Familie gebunden. Familien bleiben für den Custom-Builder relevant. Das entkoppelt die kuratierte Schicht von der Slot-Architektur.

Architektur-Entscheidung **drei Mini-Viz-Stufen**: Karten zeigen subtile 6 px Stacked-Bars, 28 px Sparklines, Top-3-Mini-Bars oder 2×2-Heatmaps; das Result-Panel zeigt vollwertige SVG-Renderings. Beide Stufen teilen sich die Renderer-Logik.

Architektur-Entscheidung **Permalinks doppelt**: `#q=<id>` für Galerie, `#f=<fid>&...` für Custom-Builder. Beide bidirektional serialisiert; Custom-Permalink öffnet das `<details>` automatisch. Permalink-Copy-Button mit Clipboard-API ersetzt den vorherigen reinen Anzeige-Hint.

Refactor-Pass danach: COVERAGE-Map konsolidiert vier nahezu identische Coverage-Funktionen, generischer `topN(source, n, opts)` ersetzt drei `topX`-Helfer, Label-Maps zentralisiert (Roles/Orgs/Tx), Driver in neun nummerierte Sub-Sections gegliedert, CSS auf Token-Aliases umgestellt, Mobile-Layout < 600 px ergänzt, `:focus-visible`-Outlines durchgängig. Stub-Familien 2–5 aus `analysis-families.js` entfernt (waren tot und irreführend).

Bekannte Folge-Lücken: Familien 2–5 sind als Galerie-Resolver implementiert, aber noch nicht als Custom-Builder-Slots. Korpus-Filter ist weiter aufgeschoben, weil die Galerie-Antworten Korpus-übergreifend formuliert sind. `RELEASED_PERIOD` aus Event-Datum dynamisch ableiten (CS-Feedback-Punkt 1.2) wartet weiter auf eine konflikt-freie Session mit dem Pipeline-Repo. Tests: 23 grün, davon 12 Aggregat-Konsistenz-Tests pro Frage, die Pipeline-Drift erkennen, bevor Nutzer:innen falsche Zahlen sehen.

---

## 2026-04-17 Terminologie-Konsolidierung, Erschließungsform, Provenienz-Ausrollung

Die UI-Terminologie wird durchgehend auf die kanonischen Begriffe aus [[glossar]] und [[decisions#Begriff Quellenkorpus]] gezogen. Alle benutzerseitig sichtbaren Vorkommen von „Dokument(e)" werden zu „Quelle(n)", „Rechtsakt(e)" zu „Rechtsgeschäft(e)", eine verbliebene „Sammlung"-Spaltenkopfzeile zu „Quellenkorpus". Technische Labels auf HTML-Ebene (ARIA-Attribute, CSS-IDs) bleiben unberührt, weil sie sich auf das HTML-Dokument als Trägerformat beziehen, nicht auf die Quelle der Datenbank.

Die [[data#Erschließungsformen|Erschließungsform]] eines Quellenkorpus ist im UI an den Quellenkorpus-Chips der Dokumenten-Übersicht sichtbar. QGW-Bestände tragen das Label „Regest + Faksimile", Stadtbücher tragen „Volltext". Die Zuordnung liegt als Build-Konstante `_transmission_form` vor und fliesst in die `collections`-Datenstruktur mit ein.

Die Provenienz-Tooltip-Komponente wird von den Startseiten-KPIs auf weitere Seiten ausgerollt: Exploration-Hub (Personen, Rechtsgeschäfte, Quellen), Personenregister (Gesamt-Einträge mit Hinweis auf quellenbereinigte Zählung pro Eintrag), Datenqualität (Quellen gesamt). Das Muster ist dasselbe wie auf der Startseite; die Popover-Inhalte verweisen jeweils auf die relevanten Glossar-Einträge und Dateipfade.

Offen für eigene Sessions:

- **Zählebenen-Umschalter [[requirements#Umschaltbarkeit der Zählebenen]].** Implementierungspfad: globaler Schalter in der Navbar oder Filter-Leiste, persistierter Zustand im `localStorage`, propagiert via `window.COUNT_MODE` an die Exploration-Skripte. Jeder Counter muss pro Zahl wissen, welche der beiden Ebenen er anzeigen kann; für die Mehrzahl der Exploration-Seiten bedeutet das eine parallele JSON-Struktur (oder zusätzliche Felder in den bestehenden Aggregat-JSONs), die beide Ebenen vorhalten. Der Provenienz-Tooltip zeigt in jedem Popover den gewählten Modus.

- **Menschen-Events-Toggle [[ui-design#Menschen-Events-Toggle]].** Implementierungspfad analog: `window.INCLUDE_HUMAN_EVENTS`, persistiert, propagiert. Datenmodell-Seite: die Aggregatoren müssen Nennungen trennen, je nachdem ob sie aus einem primären Event stammen oder als Verweis auf ein früheres Event vorliegen. Voraussetzung ist eine belastbare Markierung im TEI-Datenstrom. Bei fehlender Markierung zeigt das UI den aktuellen stillschweigenden Zustand (Einschluss) offen, statt ihn zu verschleiern.

- **Bestandsfilter universell [[ui-design#Bestandsfilter]].** Derzeit wirkt der Filter nur auf der Quellen-Übersicht. Implementierungspfad: eine gemeinsame Filter-Komponente mit `window.CORPUS_FILTER` als Zustand, die alle Seiten beim Laden konsultieren. Die Seiten selbst müssen ihre Aggregate so aufbauen, dass sie auf beliebige Teilmengen der Korpora herunter-rechenbar sind. Für die Exploration-Skripte heisst das, dass die Aggregat-JSONs zusätzlich eine korpusbasierte Unterschlüsselung tragen.

- **Analyse-Seite mit Template-Familien.** Blaupause in [[analyse]]. Umsetzung erfordert Fachteam-Entscheidung über die initiale Familienmenge. Technischer Pfad: clientseitige Template-Engine mit Slot-Parametern, Live-Counts aus den Aggregat-JSONs, Drill-down über das bestehende `docs_lookup.json`.

Kleinere UX-Punkte, die ohne Phase-2-Abhängigkeit umgesetzt werden können:

- Multi-Select-Chips für den Quellenkorpus-Filter (mehrere Korpora gleichzeitig).
- Tag-Farbdifferenzierung für Rollen in der Einzelquellen-Ansicht.
- Mouse-over-Legenden in den Exploration-Visualisierungen, mit kurzen Erklärungen der Achsen und Kodierungen.
- F-Faktoid-Legende (Markierung weiblicher Faktoid-Gruppen in den Rollen-Ansichten).
- Archivinfos auf der Einzelquellen-Ansicht (Signatur, Bestand, Faszikel, sofern aus TEI-Header extrahierbar).

## 2026-04-17 Startseiten-Layout, Datenstand und offene Phase-2-Punkte

Die Startseite wird konzeptionell neu geordnet. Statt einer einzelnen Exploration-Sektion mit Trennstrich stehen zwei gleichberechtigte Säulen nebeneinander: Exploration (vier visuelle Zugänge) und Analyse (Einstieg zur Grundabfragen-Seite im Template-Familien-Stil von [[analyse]]). Eyebrow-Labels in Sans-Caps markieren die Bereiche ohne optischen Schwergewichte wie border-bottom. Die Entry-Cards (Quellen, Personenregister, Über das Projekt) tragen Icons in der Akzentfarbe. Die Farblogik stabilisiert sich: blau für Akzente (Icons, Labels, interaktive Elemente), schwarz für Inhaltstitel, gedämpftes Grau für Beschreibungstexte.

Der Footer trennt Datenstand und Build-Datum. Bis zuletzt zeigte „Datenstand" das Tagesdatum des Builds, was inhaltlich falsch ist. Der Datenstand ist nun das Datum des letzten Commits im Pipeline-Repo, ermittelt über `git log -1 --format=%cI` und in deutscher Langform ausgegeben. Die Hilfsfunktionen `_format_german_date` und `_pipeline_repo_data_date` liegen in `edition/build.py`. Die Dissertations-Zeile im Footer entfällt; sie war Projekthistorie, nicht Datenbank-Kontext.

[[glossar#Gesamtnennung]] wird präzisiert: die Zählebene ist quellenbereinigt, Mehrfacherwähnungen einer Person in derselben Quelle werden zu einer Nennung zusammengefasst. Die entsprechende Leitentscheidung liegt als [[decisions#Quellenbereinigte Zählung]] vor. Der Provenienz-Tooltip zur individuellen Person nimmt diese Schärfung auf.

Offen bleibt aus der Phase-2-Liste des CS-Feedbacks:

- **Zählebenen-Umschalter** zwischen Gesamtnennungen und Individuellen Personen in allen betroffenen Visualisierungen ([[requirements#Umschaltbarkeit der Zählebenen]]). Ohne diese Umschaltung zeigen Rollen- und Beziehungs-Ansichten nur eine Zählebene.
- **Menschen-Events-Toggle** ([[glossar#Menschen-Event]]): aktiv ein- und ausschließbar, konsistent durch alle abhängigen Darstellungen. Ohne Toggle ist der aktuelle Zustand stillschweigend ein Ausschluss, was Vergleiche über Visualisierungen erschwert.
- **Bestandsfilter universell** in allen Visualisierungen, nicht nur in den Quellen-Suchseiten. Sinnvoll, sobald Organisationen und Orte freigegeben sind.
- **Persistente Referenzierbarkeit / PID**: beschlossen, aber technische Ausprägung (w3id, ARK, Handle) braucht Stakeholder-Entscheidung. Siehe [[requirements#Zitierfähige Datenstände]].
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

Die flache Root-Struktur des Frontend-Repos wird auf semantische Unterordner umgebaut: `register/`, `exploration/`, `analysis/`, `project/`. Die Umstellung betrifft Navigation, Build-Output und JavaScript-Lader, die die JSON-Indexe künftig über ein zentral gesetztes `window.ROOT_PATH` adressieren. Damit funktioniert die Auslieferung auch aus Unterordner-Tiefe heraus, ohne dass Pfade zu absoluten Web-Pfaden mutieren.

Die UI-Oberfläche wird durchgängig auf Deutsch gezogen. Englisch bleibt in Pfaden und im Code. Der Untertitel lautet jetzt „Datenbank zu mittelalterlichen Rechtsgeschäften". Siehe [[decisions#Titel und Untertitel]].

Quantitätsbezogene Angaben (Zeiträume, unausgewertete Perioden, Korpus-Zählwerte) werden aus Templates entfernt und an eine zentrale Konfigurationsdatei im Pipeline-Repo gebunden. Hardcoded Zahlen in Templates gelten ab jetzt als Fehler.

## 2026-04-17 Entstehung der Wissensbasis

Anlass war die Einarbeitung von Feedback zum Frontend. In der ersten Iteration wurde die Wissensbasis als Obsidian-kompatibler Markdown-Ordner angelegt. Pro Dokument gilt zeitlose Formulierung ohne Projektmanagement-Artefakte und ohne Quantitäten des Korpus. Siehe [[decisions#Zeitlose Formulierung der Wissensbasis]].

Verworfen wurde ein README und eine Unterordner-Gliederung. Grund ist, dass die flache Struktur den Vault in Obsidian unmittelbar nutzbar macht und die Einstiegshürde senkt.

Für das Glossar wurde ein Kriterium festgelegt. Aufgenommen werden nur Begriffe, die im UI erscheinen und ohne Definition zu Missverständnissen führen. Selbsterklärende Alltagsbegriffe wie „Ehepaar" oder „Witwe" bleiben draußen. Aufgenommen bleibt „Rechtsgeschäft", weil es der Gegenstand der Datenbank ist und seine Abgrenzung zu [[glossar#Event]] im UI-Kontext präzise sein muss.

Offen: die konkrete Liste der Grundabfragen im Bereich Analyse. Sie wird mit dem Fachteam festgelegt und lebt vermutlich als eigener Bereich unter [[analyse]] weiter.
