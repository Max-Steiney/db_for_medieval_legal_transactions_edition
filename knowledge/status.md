# **Frontend-Entwicklung — Projektstatus und Arbeitsstand**

**Prosopographische Datenbank mittelalterlicher Wiener Rechtsgeschäfte**
Christopher Pollin, Digital Humanities Craft OG

* v1. 11.05.2026 (**WORK IN PROGRESS**)
* AI-Unterstützung: Claude Opus 4.7, Claude Code
* Am 2026-06-17 vom Repo-Root nach `knowledge/status.md` verschoben und mit den Notizen des Frontend-Meetings dieses Tages zusammengeführt. Dies ist der lebende Projekt-Tracker und damit bewusst **nicht zeitlos** wie der übrige `knowledge/`-Bestand; umgesetzte Änderungen sind zeitlos im [[journal]] beschrieben.

## **Projektgegenstand**

Die prosopographische Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte aus den Quellen der Stadt Wien mit Schwerpunkt auf Personen, Funktionsrollen und Beziehungen. Sie ist als statische Site publiziert und erfüllt eine Doppelfunktion. Sie ist eigenständige Publikation der annotierten TEI-Quellen und gleichzeitig sichtbare Verifikationsschicht für die zugrundeliegenden Pipeline-Outputs.

- Live (GitHub Pages aus docs/): kanonische URL siehe Abschnitt Offene Fragen, Zitation und Permalink
- Frontend-Code: [github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition](https://github.com/chpollin/db_for_medieval_legal_transactions_edition)
- Datengrundlage: [github.com/chpollin/db\_for\_medieval\_legal\_transactions](https://github.com/chpollin/db_for_medieval_legal_transactions)

## **Technischer Stack**

Statische Site ohne Serverkomponente und ohne Laufzeit-Datenbank. Build-Output liegt in docs/ und wird über GitHub Pages ausgeliefert.

- Python-Toolkette: [Python 3](https://www.python.org/), [lxml](https://lxml.de/), [Jinja2](https://jinja.palletsprojects.com/), [Markdown](https://python-markdown.github.io/), [MarkupSafe](https://markupsafe.palletsprojects.com/), [pytest](https://docs.pytest.org/)
- Datenaustausch: CSV (Pipeline → Aggregator), JSON mit inline drill\_down (Aggregator → Frontend)
- Build-CLI: python \-m frontend build (optional \--single FILE)
- Frontend: Vanilla-[JavaScript](https://developer.mozilla.org/de/docs/Web/JavaScript) und Vanilla-[CSS](https://developer.mozilla.org/de/docs/Web/CSS) mit Design-Tokens; Visualisierungen als handgeschriebenes [SVG](https://developer.mozilla.org/de/docs/Web/SVG)
- Schriften: self-hosted woff2, [Crimson Pro](https://fonts.google.com/specimen/Crimson+Pro), [Inter](https://fonts.google.com/specimen/Inter), [JetBrains Mono](https://www.jetbrains.com/lp/mono/) unter [SIL OFL](https://openfontlicense.org/)
- [localStorage](https://developer.mozilla.org/de/docs/Web/API/Window/localStorage) (Datenkorbskorb), URL-Parameter (Filter-Stand)
- Sicherheit: [Content-Security-Policy](https://developer.mozilla.org/de/docs/Web/HTTP/CSP) — `script-src 'self'` strikt (kein `unsafe-inline`); `style-src 'self' 'unsafe-inline'` wegen der vendored OpenSeadragon-Lib, die ihre Stile dynamisch setzt (commit c0454a27df). Risiko-Modell: statische Site ohne User-Input, daher minimal.

## **Konventionen für dieses Dokument**

### Statusmarker

- `[ ]` offen, noch nicht angefasst
- `[?]` in Klärung mit Stakeholder oder im Team
- `[~]` umgesetzt, Verifikation oder Sign-off ausstehend
- `[x]` erledigt und verifiziert

### Pro-Punkt-Schema

Jeder Anforderungs-Punkt folgt diesem Schema. Felder, die nicht zutreffen, entfallen.

```
- [Status] Anforderung (Herkunft: ...)
   * Befund: aktueller Zustand mit Code-Stelle und Verifikations-Link
   * Umsetzung: was gemacht wurde, ggf. Commit-Hash und Verifikations-Link
   * Offen: konkrete Frage oder verbleibende Aufgabe
```

Herkunft-Schlüssel: `eigene Beobachtung`, `Stakeholder-Review 11.05.2026`, `Annotationsrichtlinien`, oder analog.

### Querschnittsregeln

Regeln, die für alle Punkte gelten und deshalb nicht in jedem einzeln wiederholt werden:

- **UI-Konsistenz**: Derselbe Begriff oder Feldname trägt im gesamten UI dasselbe Label. Liegt dieselbe Datenlogik in mehreren Ansichten (Profil-Header, Sidebar-Filter, Tooltip-Titel, Hilfe-Texte), muss das Label überall identisch sein. Verankert in [`CLAUDE.md`](../CLAUDE.md) (Agent-Regeln, Bullet „Keine UI-Inkonsistenzen"), [`knowledge/ui-design.md`](ui-design.md) (Abschnitt „Begriffs- und Label-Konsistenz") und Memory-Datei `feedback_ui_konsistenz.md`. Anlass: Belegt-Wording, das auf drei Stellen synchron gezogen werden musste.

## Frontend-Meeting 2026-06-17

Notizen und Beschlüsse des Frontend-Meetings, hierher integriert (das ehemalige Root-Dokument `MEETING-FRONTEND-2026-06-17.md` wurde danach entfernt). Die umgesetzten Änderungen sind zeitlos im [[journal]] (Einträge 2026-06-17) beschrieben.

Der gesamte zu diesem Zeitpunkt umgesetzte Stand ist vom Stakeholder abgenommen. Eine getrennte Acceptance-Verfolgung („behauptet erledigt" versus „abgenommen") entfällt damit; `[~]` bedeutet im Folgenden nur noch „technische Verifikation offen", nicht „Sign-off offen".

### Heute umgesetzt

- Stadtbücher Band 1 aus der öffentlichen Sicht genommen (aus `PUBLIC_CORPORA`); QGW II/1 wird zuerst veröffentlicht. Beim Umsetzen ein Altlast-Leck behoben: `query_vocabulary.json` wird nicht mehr im öffentlichen Build geschrieben. Sicht-Regressionstests angepasst.
- Sterbedatum aus Tooltip, Annotations-Hint und Tab-Titel entfernt (`build_tooltip_person`, `person.html`). Grund: die Register-Werte sind `notAfter`-Termini, wurden aber als exaktes „† Datum" gezeigt und waren missverständlich. Der Profil-Header behält das Datum als „Verstorben vor …", weil das den Terminus ante quem korrekt wiedergibt.
- occ-Bezeichnungen in den Org-Profilen auf die inhaltliche Normalform gezogen (`roleName_norm_matching.csv`), sodass z. B. „Bischof, pischolf" zu „Bischof" zusammenfällt; die Belege-Zahl bleibt.
- README ergänzt: „Daten hinzufügen" (Einzelquelle vs. Subkorpus, `done/`-Konvention), „Voraussetzungen", Verifikations- und Status-Befehle, beide Preview-Ports.

### Noch offen

- Öffentlich/intern-Trennung weiterführen: restliche experimentelle Sektionen sauber gaten, technische IDs auch aus den JSON-Indexen der öffentlichen Sicht entfernen, Datenkorb-Erklärblock finalisieren.
- Register-Konsistenz: Personen mit Profil, aber ohne Register-Eintrag (nur `corresp`-Verweis) — Regel einschließend oder streng? Hängt mit dem Strippen quellenloser Namen in Beziehungs-Zeilen und Org-Hierarchie zusammen.
- Erschließungsform-Filter: Werte „Regest" und „Eintrag" entfernen (korpus-redundant), braucht Sign-off. Satzbuch CD dafür noch nicht annotiert.
- Kin-Bezeichnungen werden in der Beziehungsspalte ohne Trenner aneinandergehängt (z. B. „Schwester Enkelkindtochter"); dabei geht auch die `<add>`-Markierung (editorische Ergänzung) verloren, die im Volltext als `[…]` erscheint.
- Gendergerechte Rollen-Labels: geteilte `sexLabel`-Funktion fehlt (sechs Stellen, drei Schreibweisen für „unbekannt").
- Org-Typ „Koenigreich" hat kein Mapping in `roles.json` (Build-Warnung in beiden Sichten).
- Sankey-Diagramm zu Transaktionsflüssen: konzipiert, nicht gebaut (Exploration, intern).

### Offene konzeptionelle Fragen

Leitsatz „wir sammeln, was wir haben" präzisieren? Zitierformat präzisieren? Org-Verweise im Fließtext klickbar machen?

### Bekannte Datenlücken aus der Verifikation (Schwester-Repo)

Mehrere TEI-Quellfehler sind dokumentiert (`verification/findings.md`): Klammer-Anomalien im Datums-Text der Stadtbücher Bd. 1, fehlende Sigillanten-Rollen in QGW_II_I_24, ein nicht annotierter Bischof Albrecht von Passau, ein unvollständiger ID-Renaming-Pass, untypisierte Heirats-Begriffe. Sie gehören ins Schwester-Repo. Frage: sollen bekannte Lücken im Frontend sichtbar gemacht werden?

### Pre-existing Test-Befunde (unabhängig von den heutigen Änderungen)

Zwei Frontend-Tests waren schon vor den heutigen Änderungen rot (gegengeprüft mit der alten Korpus-Menge): `test_qgw_ready_event_total_distribution` — die Norm „QGW-_ready-Quellen tragen fast immer genau ein Event" stimmt nicht mehr (Daten-/Pipeline-Drift). Und `test_datengrundlage_reference` — die Annotationsrichtlinien sollen eine Seite `datengrundlage.html` verlinken, die im Build nirgends erzeugt wird. Separat zu klären.

### Zusätzlicher Bereich: Annotationsänderungen durch Claude Code (kein Frontend-Punkt)

Auslöser: Stadtbücher. Personen, die ein Geschäft ins Stadtbuch einbringen, sind als `witness` annotiert, sind aber keine Zeugen; sinnvoll wäre eine eigene Rolle „Einbringer". Daraus die offene Frage, ob Claude Code solche Annotationsänderungen direkt in den TEI-Quellen vornehmen kann. Kein Frontend-Punkt, sondern Daten- und Bearbeitungs-Workflow im Schwester-Repo. Zu durchdenken: menschliche Verifikation einbauen; Workflow in `CLAUDE.md` beschreiben; Rolle „Einbringer" definieren (mit Beispiel); Python-Skript als Support-Werkzeug; teiCrafter einbeziehen; Diff über Git/GitHub als Verifikationsschritt; Konfidenz ggf. mit schriftlicher Erklärung als Prompting-Strategie; Änderungen im teiHeader `revisionDesc` dokumentieren; größeren Teil des Korpus ins Context-Window holen; dynamische Workflows/Subagents; Verifikation durch Mensch und Agent.

## **Anforderungen und Umsetzung**

### **Korpus-Sichtbarkeit (öffentlich versus intern)**

- [x] **Öffentlicher Build zeigt ausschließlich die freigegebenen Korpora (QGW II/1, StB Bd. 1), interner Build alle fünf.** (Herkunft: Stakeholder-Protokoll 18.05.2026, Prio 1 Punkt 1)
   * Befund: `RELEASED_CORPORA` (Pipeline, fünf Subkorpora) und `PUBLIC_CORPORA` (`frontend/config.py`, zwei) waren beide vorhanden, aber `is_public_corpus` wurde nur an zwei Profil-Stellen abgefragt. Startseite, Quellen-Liste, Register, Suche und Gesamtzahlen liefen gegen alle fünf; die Startseite zeigte Satzbuch CD bis 1460.
   * Umsetzung: Sicht-abhängige Auflösung `visible_corpora()` / `is_visible_corpus()` in `frontend/config.py`, gespeist aus der Audience (öffentlich → `PUBLIC_CORPORA`, intern → `RELEASED_CORPORA`), mit Override `--corpora` bzw. `FRONTEND_CORPORA`. Zentraler Datei-Filter `_is_visible_file` in der Build-Dokumentauswahl, dadurch durchgängig in allen Aggregaten; KPI-Berechnung der Startseite (`_kpi.py`) und TEI-Download-Kopie ziehen ebenfalls `visible_corpora()`. Öffentlich jetzt 2.601 Quellen und 8.406 Personen, intern unverändert 2.686 und 8.718. Verifikation: [Startseite](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/).
   * Umsetzung: Drei verdeckte Lecks behoben, die die Reduktion erst sichtbar machte. Verwaiste Alt-Profile, weil `register/persons` und `register/orgs` vor dem Neuschreiben nicht geleert wurden (Aufräum-Fix in `_pages.py`). Ungefilterte Beziehungs-Liste, weil das Org-Tätigkeitsnetzwerk `file_meta_by_key()` über alle fünf Korpora nutzte statt der sichtbaren Teilmenge (`org_profiles.py`). Per-Quelle-Aggregat `docs_aggregate.json`, weil `aggregate_docs` die Pipeline-CSV direkt über `_cached_csv` las (filtert nur auf `RELEASED_CORPORA`); enthielt öffentlich 85 versteckte Quellen mit Jahren bis 1458, jetzt mit `is_visible_corpus`-Filter 2.601 Quellen und Höchstjahr 1414 (`aggregator/docs.py`, commit `0d5438001b`).
   * Umsetzung: Regressionstests `frontend/tests/test_visible_corpora.py` (Logik, ohne Bau) und `frontend/tests/test_public_corpus_scope.py` (gegen den gebauten Stand: nur zwei Korpora, keine quellenlose Entität, kein Profil-Link in versteckte Quelle, symmetrisch Personen und Organisationen). Dazu ein breiter Klassen-Scan, der jede `data/*.json` auf versteckte Sammlungen prüft und damit jede künftige Aggregat-Datei abdeckt, die den Sicht-Filter vergisst. Doku in README und [`knowledge/specification.md`](specification.md).
   * Umsetzung 2026-05-27 (Commits 92fef424a2 Code, ede129c097 Rebuild): Das verbliebene Aggregat-Leck geschlossen. `_cached_csv` in `frontend/aggregator/_shared.py` filtert jetzt zentral über `is_visible_corpus` statt `is_released_corpus`; damit folgen auch `roles.json`, `relations.json`, `transactions.json`, `role_constellation.json` und `timeline.json` der Sicht. Vorher trugen diese fünf released-scoped Daten (Satzbuch CD, QGW II/2) in Drill-down-file_keys und Labels, obwohl keine öffentliche Seite sie lädt; über die direkte URL waren sie dennoch abrufbar. `query_vocabulary.json` beschränkt den Korpus-Filter öffentlich auf sichtbare Sammlungen (`_pages.py`). Der breite Klassen-Scan `test_public_corpus_scope.py` traf die geleckte file_key-Form (`f__Satzbuch_CD_`) und die Labels („Satzbuch CD", „QGW II/2") vorher nicht und wurde um diese Marker erweitert, plus ein gezielter Regressionstest. Die released-Helfer bleiben für `research_questions.py` erhalten. Verifiziert: öffentlich null Hidden-Marker über alle `data/*.json`, intern unverändert vollständig.
   * Offen: Drei Folgepunkte, getrennt zu behandeln.
       1. **35 Personen mit Profil, aber ohne Register- und Sucheintrag.** Tiefenanalyse abgeschlossen: alle 35 kommen ausschließlich als relationaler Verweis `<roleName corresp="pe__...">` vor, nie als eigenständige `<rs type="person">`-Nennung (Beispiel Elisabeth in Quelle 731, dort drei Mal als roleName corresp in einem Kinder-Kontext, null Mal als rs). Ursache im Code: `_build_person_profiles` erzeugt für jeden Reverse-Index-Eintrag ein Profil, `_build_register_json`/`_released_person_keys` zählen aber nur `rs type="person"`. Diese Personen sind nicht quellenlos, sie stehen real in einer öffentlichen Quelle. Entscheidung offen, gehört zu A.3.2: **einschließend** (relationalen Verweis als Beleg werten, die 35 ins Register und die Suche aufnehmen) versus **streng** (nur eigenständig genannte Personen sind klickbare Einheiten, kein eigenes Profil für die 35).
       2. **`data-released-max="1460"` im body.** Erledigt 2026-05-26: `data-released-min` und `data-released-max` aus `frontend/templates/base.html` entfernt; der korrespondierende `window.RELEASED_PERIOD`-Initialisierer in `frontend/static/js/core.js` ebenfalls. Hintergrund: Setter ohne Konsumenten; die Zeit-Schieberegler nehmen ihre Grenzen datengetrieben aus `min_year`/`max_year`. Regression `frontend/tests/test_released_period_dead_code.py` sichert, dass weder das DOM-Attribut noch der JS-Init wiederkommen.
       3. **Quellenlose Namen in Beziehungs-Zeilen und Org-Hierarchie.** Vom Stakeholder entschieden: strikt, es soll nur erscheinen, was real in den Daten ist, quellenlose Namen nie. Lokalisiert in `frontend/aggregator/person_profiles.py::_build_relation_index` (Beziehungs-Treffer ohne sichtbare Quelle haben leeres `file_lookup` und rendern als Klartext) sowie in der Org-Hierarchie. Wartet auf Punkt 1, weil dieser mitbestimmt, welche relationalen Ziele überhaupt übrig bleiben.

### **Suchleisten**

- [~] [**Quellen-Liste**](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html) (Sidebar)
   * Befund: Filtert die Liste live; geprüft werden Signatur, Datum (TEI- und Anzeigeform), Ort, Korpus-Label, Regest (Anriss \+ Volltext).
- [~] [**Personen-Register**](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html)
   * Befund: Filtert die Liste live; geprüft werden Name (auch Vor- und Familienname einzeln), ID, Aktivitätszeitraum, Sub-Label der Erstnennung.
- [~] [**Organisations-Register**](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html)
   * Befund: Filtert die Liste live; geprüft werden Name, ID, Aktivitätszeitraum, Sub-Label der Erstnennung.
- [~] [**Personennetzwerk**](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/exploration/personennetzwerk.html)
   * Befund: Sidebar, Live-Vorschlagsliste ab 2 Zeichen, max. 12 Treffer. Sucht eine Person und zentriert das Ego-Layout auf den Treffer; geprüft wird der Personenname.

### [**Quellen**](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html)

- [x] **Welche Korpora werden verwendet, auch ungeprüfte Korpora berücksichtigen?** (Herkunft: eigene Beobachtung)
   * Umsetzung: Die publizierte Datengrundlage umfasst zwei freigegebene Subkorpora: **QGW/Vienna\_1177-1414\_ready** und **Stadtbuecher/Band\_1\_1395-1400\_ready**. Ungeprüfte Korpora werden nicht berücksichtigt.
- [x] **Anzeige- und Zähllogik so umbauen, dass ausschließlich geprüfte Korpora (QGW, StB) in Zählungen, Nennungen und Gesamtsummen einfließen.** (Herkunft: eigene Beobachtung)
   * Umsetzung: Die Filterung ist durch eine zentrale Freigabeliste gesichert, die an allen Stationen der Datenverarbeitung (Quellen einlesen, Daten aufbereiten, Zahlen für die Startseite berechnen, Register erstellen, Detailseiten rendern) gleichermaßen greift, sodass nur geprüfte Korpora in Zählungen, Nennungen und Aggregate einfließen können.

- [?] **Erschließungsform-Symbol fehlt bei vielen Quellen.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Rechts in jeder Zeile der Quellen-Liste stehen kleine Symbole, die anzeigen, welche editorischen Strukturen die Quelle im TEI-Markup trägt. R steht für Regest (Inhaltszusammenfassung als `<abstract>`), S für Siegel-Beschreibung (`<seal>`), E für Eintrag im Stadtbuch-Format (`<entry>`), N für Nota (Marginal-Nachsatz, `<nota>`). Der Stakeholder hat beobachtet, dass das R-Symbol bei manchen Quellen fehlt, obwohl die Spalte „Regest" einen Text zeigt. Das ist kein Frontend-Fehler. Die Spalte „Regest" zieht ihren Textauszug aus dem Anfang des Quellen-Volltexts und steht immer dann, wenn überhaupt Text vorhanden ist. Das R-Symbol dagegen ist nur dann gesetzt, wenn die TEI-Quelle ein `<abstract>`-Element trägt. Beide Werte können auseinanderlaufen.
   * Datenlage: 214 von 2686 freigegebenen Quellen tragen gar keine Erschließungsform. Sie verteilen sich auf drei unterschiedliche Pools.

       | Korpus | mit Erschließungsform | ohne | Anteil ohne |
       |---|---|---|---|
       | QGW (drei Bände, 1177 bis 1457) | 2043 | 27 | 1 % |
       | Satzbuch CD (1448 bis 1460) | 0 | 38 | 100 % |
       | Stadtbücher Bd. 1 (1395 bis 1400) | 429 | 149 | 26 % |
       | **Gesamt** | **2472** | **214** | **8 %** |

     Die 27 QGW-Quellen sind fast ausnahmslos Privilegien-Quellen, im Quellentitel als `(= Privil. Nr. 1)` bis `(= Privil. Nr. 28)` markiert (25 Stück). Sie tragen alle ein Faksimile, sind also editorisch sichtbar geführt. Vermutung, dass sie bewusst ohne `<abstract>` ediert wurden, weil das eigentliche Regest im Privilegienband (QGW II/2) parallel ediert ist. Zwei Sonderfälle ohne Privilegien-Marker, Quelle 783.1 und Quelle 1630, fallen aus dem Muster und wirken eher wie Datenlücken.

     Die 38 Quellen im Satzbuch CD sind der gesamte freigegebene Bestand dieses Korpus. Keine einzige Quelle trägt eine Erschließungsform, was wie ein Annotations-Rückstand im jüngsten Korpus aussieht.

     Die 149 Stadtbuch-Quellen sind 26 % des Bandes; der Rest (429 Quellen) trägt `<entry>`. Wahrscheinlich noch nicht annotierter Teil-Bestand, der einzeln geprüft werden muss.
   * Offen, Entscheidung der Projektpartner. Drei Pools, drei Entscheidungen.
       1. Für die 25 QGW-Privilegien entweder `<abstract>` nachtragen oder eine eigene Erschließungsform „Privileg" als sechste Kategorie einführen, die die Doppel-Edition mit dem Privilegienband sichtbar macht. Die zwei Sonderfälle 783.1 und 1630 separat prüfen.
       2. Für das Satzbuch CD klären, ob die fehlende Annotation Rückstand ist (dann nacharbeiten) oder bewusste Entscheidung (dann im UI als „in Bearbeitung" kennzeichnen).
       3. Für die 149 Stadtbuch-Quellen klären, ob sie noch nicht annotiert sind oder als eigene Klasse zu führen sind.
   * Verifikation: [Quellen-Liste mit Filter „ohne Erschließungsform"](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html?forms=none) zeigt die 176 oeffentlich sichtbaren (27 QGW-Privilegien plus 149 Stadtbuecher; Satzbuch CD nur im internen Build, Released-Scope gesamt 214); [eingeengt auf QGW](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html?forms=none&collection=QGW/Vienna_1177-1414_ready) zeigt die 27 Privilegien-Quellen; [QGW Nr. 15 als Stichprobe](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/15.html).

- [x] **Filter „Erschließungsform" für Nicht-Fachleute schwer einordnenbar.** (Herkunft: Stakeholder-Review 11.05.2026; entschieden Stakeholder-Durchgang 02.06.2026)
   * Entscheidung 02.06.2026: Der Filter wird komplett entfernt (Punkt A2), nicht nur konsolidiert. Siehe Abschnitt „Stakeholder-Durchgang 02.06.2026". Die folgenden Befunde dokumentieren den Stand davor.
   * Befund: In der Sidebar der Quellen-Liste filtert ein Block namens „Erschließungsform" über fünf Werte (Regest, Siegel, Eintrag, Nota, ohne). Stakeholder berichten, dass sowohl die Überschrift als auch einzelne Werte ohne editorisches Vorwissen schwer einzuordnen sind. Zwei strukturelle Schwächen kommen hinzu. Die Werte „Regest" und „Eintrag" decken sich faktisch mit dem Korpus-Filter direkt darüber. „Regest" zeigt fast nur QGW-Quellen, „Eintrag" fast nur Stadtbuch-Quellen, beide bringen gegenüber dem Korpus-Filter keinen Mehrwert. Nur „Siegel" und „Nota" sind echte Sonderfälle innerhalb der Korpora und filtern wirklich. Der Wert „ohne" (oeffentlich 176, im Released-Scope 214 inklusive Satzbuch CD) wirft die drei Pools aus dem vorherigen Punkt unter einem Label zusammen und ist in dieser Form nicht interpretierbar.
   * Offen, UI-Pfade zur Wahl.
       1. **Minimal-Pfad**, ohne Daten- oder Logik-Eingriff. Überschrift verständlicher benennen (Vorschlag „Editorische Sonderfälle" oder „Strukturen in der Quelle"); Tooltip-Texte mit Beispielen und Korpus-Bezug anreichern; einzeiligen Hilfe-Satz unter der Überschrift einbauen, der den Filter als „TEI-Strukturen pro Quelle, mehrere möglich" verständlich macht.
       2. **Mittel-Pfad**, Filter-Werte konsolidieren. „Regest" und „Eintrag" entfernen, weil sie nichts hinzufügen. Es bleiben „Siegel", „Nota" und „ohne". Der „ohne"-Tooltip führt die drei Pools (27 QGW-Privilegien, 38 Satzbuch CD, 149 Stadtbücher) klar auseinander. Überschrift zu „Editorische Sonderfälle".
       3. **Großer Pfad**, Filter neu konzipieren. Binärer Filter „mit redaktioneller Erschließung" gegen „ohne", plus zwei Sonderfilter „Siegel" und „Nota". Benötigt eine neue Datenspalte im Backend, also größerer Eingriff.
   * Umsetzung Stand 2026-05-23 (Schicht 1, reine Texterhellung, ohne Sign-off): R/S/E/N-Symbol-Tooltips in der Quellen-Liste auf jargonarme Form ohne TEI-Vokabel umgeschrieben (R-Tooltip nennt zusätzlich den Symbol-Spalten-Unterschied); „ohne"-Chip-Tooltip in der Sidebar um die Pool-Aufschlüsselung (QGW-Privilegien, Satzbuch CD, Stadtbücher) erweitert; statt eines Subtitles unter der Filter-Überschrift sitzt jetzt ein `i`-Icon direkt am Label, das ein Popover mit Filter-Erklärung und Definitions-Liste der fünf Werte öffnet (konsistent mit dem `tip_help`-Muster des Suche-Blocks).
   * Offen (Schicht 2, braucht Sign-off): Filter-Werte „Regest" und „Eintrag" entfernen, weil korpus-redundant; Überschrift umbenennen zu „Besondere Merkmale" oder analog; oder der große Pfad mit neuem binärem Filter.
   * Verifikation: [Quellen-Liste, Sidebar-Block „Erschließungsform"](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html).

### **Register**

- [ ] **Anhand von Stichproben mit bekannter Nennungs-Anzahl ist davon auszugehen, dass derzeit im Schnitt 2/3 bis 3/4 aller Hits bei den Nennungen nicht angezeigt werden.** (Herkunft: Stakeholder-Review)
   * Befund: Frontend zeigt distinkte Quellen, nicht Gesamtnennungen.
   * Offen: Klären, was genau gemeint ist (Quellen-Anzahl vs. Gesamtnennungen), dann entscheiden, ob ein zweites Zahlenfeld nötig ist.
- [x] **Die angezeigten Daten dürfen nur aus den geprüften Korpora stammen (QGW, StB). Es dürfen nur die Personen aufscheinen, die in diesen Beständen genannt sind.** (Herkunft: eigene Beobachtung)
   * Umsetzung: Eine zentrale Freigabeliste `RELEASED_CORPORA` in `pipeline/config.py` wird beim Build an drei Stellen geprüft (beim Einlesen der TEI-Dateien, beim Sammeln der Personen-IDs, beim Schreiben der Index-JSONs) und durch das unabhängige `verification/`-Test-Set gegengeprüft.

- [x] **Personen-Profile zeigten Vor- oder Nachnamen nicht, wenn nur `<orig>` in personList.xml gefüllt ist.** (Herkunft: eigene Beobachtung)
   * Befund: Strikt-`_reg`-lesender Profilkopf ließ den Namen weg, obwohl Listing und Suche ihn zeigten. Stichproben: Schonhauer, Hagker, Payr. ~100 Profile betroffen.
   * Umsetzung: `_load_person_stammdaten` und `_orig_display` mit Fallback `_reg or _orig` pro Feld (commit 74b02d7c75). Bulk-Verifikation 98/98 IDs grün.

#### Organisations-Register

- [~] **Belegt-Kategorie präzisieren** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Header-Feld `Belegt` auf der Org-Profil-Seite, gerendert in `frontend/templates/org.html:94`. Wert ist min/max der ISO-Jahre aller Quellen, in denen die Org annotiert ist, berechnet in `frontend/aggregator/org_profiles.py:419-421,457-458`. Das Datum pro Quelle kommt aus dem teiHeader; die Pipeline arbeitet ein 8-Prioritäten-Lookup ab (`pipeline/utils/date_parser.py:103`). Im freigegebenen Korpus greifen davon nur drei Pfade: `date/@when` (Standardfall), `date/@from+@to` (Range, davon wird `from` genommen), `origin/@notAfter` (nur Subkorpus Satzbuch\_CD\_1448-60). `rs type="event"` trägt nie ein eigenes Datum, Events erben die Datierung der Quelle.
   * Problem: Das Label liest sich ontologisch als historische Existenz-Datierung der Institution. Tatsächlich ist es Editions-Datierung: in welchen Jahren existieren in dieser Edition Quellen, die die Org annotieren. Bei Orgs mit nur einer Quelle steht das nackte Jahr und wirkt wie ein Punkt-Datum. Knapp zwei Drittel aller Orgs haben nur eine Quelle.
   * Umsetzung: Label durch dynamisches `Datum der Quelle` (Singular bei einer Quelle) oder `Datum der Quellen` (Plural sonst) ersetzt. Spannen mit `bis` statt en-dash. Einheitlicher Tooltip ergänzt. Synchron umgesetzt auf Org-Profil (`frontend/templates/org.html`), Personen-Profil (`frontend/templates/person.html`) und Sidebar-Filter beider Register (`frontend/templates/register_list.html`, samt Korrektur des „je Person"-Bugs in Sub-Label und Histogramm-Hints des Org-Registers, plus „Aktivitätszeitraum" im Suche-Hilfe-Tooltip). 380 von 380 Tests grün.
   * Verifikation: [Burg Kufstein](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html) (eine Quelle, „Datum der Quelle 1397"), [Zwettl Zisterzienser](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__zwettl-zisterzienser.html) (zwei Quellen mit Lücke, „Datum der Quellen 1342 bis 1388"), [Wien St. Stephan](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__wien-st_stephan.html) (viele Quellen, breite Spanne), [Organisations-Register-Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html), [Personen-Register-Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html).
   * Offen: Sign-off Stakeholder. Bei Einzelquelle (knapp zwei Drittel der Orgs) wurde bewusst kein expliziter „(1 Quelle)"-Hinweis ergänzt, da der Singular im Label und das Nachbarfeld `Quellen: 1` die Aussage tragen; falls dem Stakeholder das zu schwach ist, ist die Klammer-Ergänzung ein kleiner Folge-Eingriff.

- [?] **Relationale Tags sichtbar machen, wenn Organisationen innerhalb anderer Tags annotiert sind.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Reverse-Index liest sowohl `<rs type="org" ref="#org__...">` als auch `<roleName corresp="#org__...">` (`frontend/build/_helpers.py:133-154`), die Org-Profil-Seite findet die Quelle daher korrekt. Im gerenderten Quellen-HTML aber sammelt `frontend/static/js/document.js:94,118` für die Annotationen-Tabelle ausschließlich `.anno-person, .anno-org, .anno-place` und ignoriert `data-corresp^="org__"` auf `anno-attr-occ`- und `anno-attr-title_ref`-Spans. Resultat: die Org-Verweise sind im Body als Tooltip da, aber kein klickbarer Link und kein Tabellen-Eintrag.
   * Verifikation: [Burg Kufstein, Quellen-Block](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html) zeigt Quelle 222 (StB I), [Stadtbuch-Eintrag 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html) zeigt Burg Kufstein nicht in der Annotationen-Tabelle, obwohl `#org__kufstein-burg` als `corresp` auf der `<roleName type="occ">phleger</roleName>` von Rudolf von Rosenhaim sitzt.
   * Offen: Soll der implizite Org-Verweis als klickbarer Link im Body gerendert werden, als zusätzlicher Zeilen-Typ in der Annotationen-Tabelle, oder beides. Selbe Frage für `title_ref`-Org-Bezüge.

- [x] **Person-IDs in der öffentlichen Ansicht ausblenden.** (Herkunft: Stakeholder-Review 11.05.2026, bestätigt Protokoll 18.05.2026 A.3.2)
   * Umsetzung Stand 2026-05-23 (commit 1eb99a692e): Technische IDs (`pe__`, `org__`, `ev__`) wurden an sechs Stellen aus dem sichtbaren Public-UI entfernt. ID-Pair im Meta-Strip von Personen- und Org-Profilen entfernt. „ID: ..."-Zeile aus Annotations-Tooltips auf der Quellen-Detailseite gestrichen (`entityTipBody` in `document.js`). Event-ID als alleiniger Titel im Event-Tooltip durch einen Fallback „Rechtsgeschäft" ersetzt, wenn weder Dispositiv-Verb noch Abschnitt vorhanden. „ID: ..."-Zeilen in den Drill-down-Pills des Abfrage-Interfaces entfernt (`analysis-resolver.js`). `[xml_id]`-Suffix in den Body-Annotations-Tooltips entfernt (`register.py::build_tooltip_*`, plus Test-Anpassung in `test_register.py`). Zitierbarkeit bleibt über den URL-Slug und `href`/`data-ref`-Attribute erhalten.
   * Verifikation: [Org-Profil Burg Kufstein](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html), [Personen-Profil Adelheid](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons/pe__adelheid_QGW_II_I_1111.html), [Stadtbuch-Eintrag 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html). Im privaten Build und mit `?dev=1` weiterhin sichtbar.
   * Offen: Build-then-grep-Regression-Test, dass `pe__`/`org__`/`ev__` in keinem Public-HTML außerhalb von `href`/`data-ref` auftaucht. Steht als eigener Task auf der Sofort-Liste.

- [?] **Formulierung „für" als Rollenbezeichnung ersetzen, sie ist irreführend.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Keine Stelle im Frontend-Code setzt explizit „für" als Label-String. Die Rollen-Vokabulare in Templates (`ROLE_LABEL` in `person.html:13`, `org.html:15`) und JS (`document.js`) verwenden „Aussteller\*in", „Empfänger\*in", „Zeug\*in / Siegler\*in", „Sonstige". Plausibler Kandidat ist die `anno-attr-rep`-Annotation (Stellvertretung), in der das TEI-Wort „für" als Rolle markiert wird, siehe Beispiel [QGW Vienna 1051](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1051.html) („für" als Span mit `data-hint-type="Stellvertretung"`).
   * Offen: Bestätigung durch Stakeholder, wo genau im UI „für" als Rolle erscheint. Idealerweise Screenshot. Wenn es der `anno-attr-rep`-Fall ist, müsste der Anzeige-Text zur Rolle in der Annotationen-Tabelle gehoben werden (statt das TEI-Wort), nicht das Wort im Quellentext geändert.

- [?] **Kategorie „im Quellen-Wortlaut" vereinheitlichen.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Identisches Label „Im Quellen-Wortlaut:" auf beiden Profil-Sub-Headern (`frontend/templates/org.html:66` und `frontend/templates/person.html:97`). Backing-Felder unterscheiden sich: Org rendert `profile.name_orig` (Roh-Wortlaut aus den Org-Stammdaten), Person rendert `profile.name_orig_display` (aufbereiteter Display-String, siehe `frontend/aggregator/person_profiles.py:459,133`). Die wahrscheinliche Uneinheitlichkeit liegt nicht im Label, sondern im dahinterliegenden Wert: bei Personen wird auf `_orig` zurückgefallen, wenn `_reg` leer ist (Fallback-Logik), sodass „im Quellen-Wortlaut" gelegentlich nur die Normalform wiederholt.
   * Offen: Klären, ob der Stakeholder die Wert-Aufbereitung meint oder das Label selbst. Wenn Wert: konsistente Behandlung Org vs Person (kein Fallback, oder Fallback auf beiden Seiten, oder Sub-Label-Hinweis).

### **Analyse**

#### [Auswertungen](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/auswertungen.html)

- [?] **Provenienz der aggregierten Kategorien sichtbar machen, damit Klassifikationen nachvollziehbar werden und Editor-Verantwortung erkennbar bleibt.** (Herkunft: Stakeholder-Feedback 26.05.2026 von Christina Lutter: „Transaktionstypen als existierende, aber noch nicht geprüfte Darstellungen unter „Analysen". Hier zeigt sich die Diskrepanz zwischen der Interpretation durch Claude und unserer manuellen Kategorisierung: Claude fasst pauschal zusammen, wir haben umständlich in einer Tabelle jeden Text-String einzeln beurteilt. Das darf hier nicht einfach zusammenfallen.")
   * Befund: Die Aggregate, die auf der Auswertungen-Seite erscheinen, setzen sich aus drei sehr unterschiedlich verantworteten Schichten zusammen, die im UI aktuell nicht voneinander unterschieden sind.
       * **Schicht 1, Rohdaten 1:1 aus den TEI-Annotationen.** Rollen-Verteilung, Geschlechts-Verteilung, Datierungen, Organisationstypen. Keine Bündelung, kein Mapping. Pass-through aus den Pipeline-CSVs `persons_in_events.csv`, `persons.csv`, `events_in_sources.csv`, `organisations.csv`.
       * **Schicht 2, Editor-Tabellen aus dem Daten-Repo.** Drei manuell gepflegte Normalisierungstabellen unter `../db_for_medieval_legal_transactions/normalisation_lists/`. Jede Zeile trägt eine `resp`/`Editor`-Spalte mit Editor-Initialen (kg = Korbinian Grünwald, cs = Carina Siegl, rs = Ronald Salzer, df, hk, lp, ks), Auflösung in `editors/Name_of_Editors.csv`.
            * Transaktionstypen aus [`label_norm_matching.csv`](../db_for_medieval_legal_transactions/normalisation_lists/label_norm_matching.csv), 2461 Zeilen, 54 Kategorien (Abgabe_unbestimt, Ablass, Bau, Bestandnahme, Kauf, Lehensvergabe, Leihkauf, Stiftung, Tausch, Testament, Vergleich, …), Editor durchgehend kg. Beispiel-Zuordnung: Roh-String „verleiht | einen Ablass von 40 Tagen" → Kategorie „Ablass".
            * Uhlirz-Berufskategorien aus [`roleName_norm_matching.csv`](../db_for_medieval_legal_transactions/normalisation_lists/roleName_norm_matching.csv), Spalte `Gewerbe_nach_Uhlirz_GstW`, 18 Kategorien (I bis XVIII), Editoren kg/rs/cs mit `note`-Spalte für strittige Fälle. Beispiel: Roh-String „wachsgiezzer" → Uhlirz IV.
            * Funktionen aus [`function_norm_matching.csv`](../db_for_medieval_legal_transactions/normalisation_lists/function_norm_matching.csv), 686 Zeilen, im Frontend aktuell nicht konsumiert (nur Pipeline-Transformation).
       * **Schicht 3, Frontend-eigene Bündelung ohne Editor-Tabelle.** Drei Stellen, an denen Frontend-Code Strings zusammenführt ohne Stakeholder-Sign-off.
            * Schreibvarianten-Normalisierung in [`frontend/aggregator/relations.py:55-144`](../frontend/aggregator/relations.py#L55-L144), `_LABEL_NORM`-Dict mit etwa 30 hartcodierten Gruppen. Beispiele: Display-Label „hausfrau" sammelt 13 Schreibvarianten (hausfraw, hausfraun, hawsfraw, hausvrowe, …); „witib" sammelt 7 Varianten; „geschäftsvollstrecker" sammelt 9 Varianten.
            * Heirats-Erkennung in [`frontend/aggregator/research_questions.py:35-48`](../frontend/aggregator/research_questions.py#L35-L48), `MARRIAGE_TERMS`-Set mit 12 Begriffen (gemahl, gemahlin, gatte, hausfrau, ehefrau, …), entscheidet die Treffermenge der Forschungsfrage Uhlirz IV. In [`verification/findings.md`](../verification/findings.md) als „provisorisch, Substring-basiert" markiert.
            * Sammelkategorien geistlich/weltlich/sonstige für die Organisationstypen in [`frontend/content/categories.json`](../frontend/content/categories.json), decided 2026-05-01, mit `meta.note`-Begründung, aber ohne Editor-Kürzel.
   * Verifikation der Schicht-2-Tabellen: [Beispielzeilen `label_norm_matching.csv`](../db_for_medieval_legal_transactions/normalisation_lists/label_norm_matching.csv), [Beispielzeilen `roleName_norm_matching.csv`](../db_for_medieval_legal_transactions/normalisation_lists/roleName_norm_matching.csv), [Editor-Auflösung](../db_for_medieval_legal_transactions/normalisation_lists/editors/Name_of_Editors.csv).
   * Vorschlag, Block A (Frontend, sofort, kein Datenrepo-Eingriff).
       1. **Header-Zeile pro Aggregat-Sektion** mit Quell-Tabelle und Editor-Initialen. Beispieltext Transaktionstypen: „54 Kategorien aus der editorischen Normalisierungstabelle `label_norm_matching.csv`, gepflegt von Korbinian Grünwald (kg)". Begründung: aktuell zeigt die UI nur Kategorie-Labels, die Stakeholderin sieht nicht, dass die Werte aus ihrer eigenen Tabelle stammen.
       2. **`_not_normalised`-Bucket als sichtbare graue Zeile** mit Drill-down. Aktuell `delete totals['_not_normalised']` in [`analysis-aggregat.js:349-350`](../frontend/static/js/analysis-aggregat.js#L349-L350); damit verschwindet der nicht-klassifizierte Anteil aus der Anzeige. Begründung: Ehrlichkeit gegenüber der Forscherin und gleichzeitig Werkzeug fürs Editor-Team (welche Strings müssten noch in die Tabelle).
       3. **Variants-Tooltip pro Zeile** in der Relations-Labels-Tabelle. Die `variants`-Liste ist im JSON schon mitgeführt, das UI nutzt sie nicht. Begründung: die Bündelung „hausfraw, hausfraun, hawsfraw → hausfrau" wird damit transparent statt versteckt.
       4. **Coverage-Anteil sichtbar als Footer-Text** neben den Balken. Die `~15% coverage`-Kennzahl steht in `meta`, das UI führt sie nicht aus. Begründung: verhindert die Fehlinterpretation einer Vollabdeckung.
   * Vorschlag, Block B (Daten-Repo, mittel, braucht Editor-Sign-off).
       5. **Neue `kin_norm_matching.csv` im Pipeline-Repo** anlegen, analog zu den bestehenden Norm-Tabellen, Spalten `spelling, norm, type, resp, note`. Verschiebt die etwa 30 Schreibvarianten-Gruppen aus `relations.py` in editor-verantworteten Code. Begründung: aktuell entscheidet Frontend-Code allein, ob `hawsfraw` mit `hausfraw` zusammenfällt. Saubere Stelle für diese Entscheidung ist die Editor-Tabelle.
       6. **Spalte `is_marriage` in dieser neuen Tabelle.** Löst das `MARRIAGE_TERMS`-Set aus `research_questions.py` ab. Begründung: die Treffermenge der Forschungsfrage Uhlirz IV hängt heute am Frontend-Code, nicht an der Editor-Klassifikation.
       7. **Sign-off oder Re-Decision für `categories.json`.** Die Sammelkategorien-Datei lebt im Frontend-Repo ohne Editor-Kürzel. Entweder explizite Stakeholder-Zustimmung mit Initialen ins `meta`-Feld, oder Verschiebung der Datei ins Pipeline-Repo zu den anderen Normalisierungstabellen. Begründung: Spitäler-zu-geistlich, Universität-zu-sonstige sind Modellierungsentscheidungen, keine Datentatsachen.
   * Vorschlag, Block C (Provenance-System, Folge-Iteration nach A und B).
       8. **`meta.resp` als Standardfeld in jeder Aggregat-JSON.** Liste der beteiligten Editor-Initialen aus den gelesenen Tabellen. Begründung: macht die Editorenverantwortung pro Aggregat maschinenlesbar.
       9. **Spalten-Tooltips pro Kategorie-Pille projektweit.** Top-Roh-Strings und ihre Frequenz im Hover. Begründung: UI-Ausprägung des Prinzips „nur die Daten sprechen lassen, nicht die Klassifikation".
   * Offen: Stakeholder-Bestätigung, ob Block A für die nächste Iteration als alleinige UI-Maßnahme ausreicht oder ob Block B im selben Schritt mitgezogen wird. Block B benötigt Editor-Team-Aufwand für die neue Tabelle.

#### [Abfragen](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html)

- [~] **Gib mir alle Personen, die in der Verwandtschaft Personen aus der Uhlirz-Handwerkerkategorie IV haben und miteinander verheiratet sind.** (Herkunft: Stakeholder-Anfrage)
   * Verifikation: [Abfrage-Interface, Uhlirz IV](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#p1=u=IV%20Erzeugung%20und%20Vertrieb%20von%20Leuchtstoffen%20Fetten%20und%20Oelen)
   * Befund: Angezeigt sind Events mit mindestens einer Person der Klasse IV, mit allen Beteiligten, Korpus und Datum, sortier- und exportierbar.
   * Offen: Die Bedingung „verwandt mit" und der spezifische kin-Typ Ehe (Gemahl, hausvrowe). Grund: die kin-Annotation aus `kin_relations_in_sources.csv` ist nicht im Konstellations-Aggregat enthalten, und die UI hat keinen Slot „verwandt mit Person Y". Zusätzlich passt die paar-zentrierte Ergebnisform nicht zur event-zentrierten Trefferliste.

- [~] **Gib mir alle Personen, die als Berufsbezeichnung eine Uhlirz-Kategorie VI aufweisen, und zeige deren Hausbesitzorte auf einer Karte an.** (Herkunft: Stakeholder-Anfrage)
   * Verifikation: [Abfrage-Interface, Uhlirz VI](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#p1=u=VI%20Lederindustrie)
   * Befund: Angezeigt sind Events mit mindestens einer Person der Klasse VI, mit allen Beteiligten.
   * Offen: Hausbesitz und Karte. Grund: bewusst aus dem Scope genommen, Ortsstammdaten sind nicht konsolidiert. `rs type="place"` bleibt nur als Tooltip im Quellenvolltext, ohne Sprungziel und ohne Geokoordinaten. Eine owner- oder topo-Relation auf Personen ist im Aggregat ebenfalls nicht abgebildet.

- [~] **Gib mir alle Personen, die mit St. Stephan über die Kategorie occ (Tätigkeit) verbunden sind, sowie deren Verwandte.** (Herkunft: Stakeholder-Anfrage)
   * Verifikation 1: [Abfrage-Interface, naive Annäherung über Ko-Vorkommen](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#g1=n=St.%20Stephan%20\(Pfarr-%20und%20Domkirche\))
      * Befund: Angezeigt sind Events, in denen St. Stephan überhaupt beteiligt ist.
      * Offen: Die semantische Aussage „tätig *bei* St. Stephan". Grund: das Interface filtert Ko-Vorkommen im Event, nicht die occ-Relation Person→Org. Bewusste Aufgabenteilung: Profilseite für Entitäts-Beziehungen, Abfrage-Interface für Mengen-Schnitte.
   * Verifikation 2: [Org-Profil St. Stephan, Block „Personen mit Tätigkeitsverbindung"](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__wien-st_stephan.html)
      * Befund: Angezeigt sind 113 Personen mit Tätigkeitsbezeichnungen bei St. Stephan, Anzahl der Belege und eine Spalte mit 1-Hop-Verwandtschafts-Beziehungen aus dem Quellenkorpus.
      * Offen: Die konkreten Namen der Verwandten hinter der kin-Zahl. Grund: das Aggregat führt die Anzahl, aber nicht die aufgelösten Personen mit. Sinnvoll wäre eine Tooltip- oder Popover-Auflösung; kleiner Eingriff im Aggregator plus Markup.

- [x] **Gib mir alle Personen/Organisationen, die durch ein Issuer-Recipient-Verhältnis mit St. Agnes auf der Himmelpforte verbunden sind.** (Herkunft: Stakeholder-Anfrage)
   * Verifikation 1: [Abfrage-Interface, Person Issuer plus Agnes Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#p1=r=issuer&g1=r=recipient,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien). Angezeigt sind Events, in denen eine beliebige Person als Ausstellerin und St. Agnes als Empfängerin auftritt.
   * Verifikation 2: [Abfrage-Interface, Gegenrichtung Agnes Issuer plus Person Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#g1=r=issuer,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien&p1=r=recipient). Angezeigt sind Events, in denen St. Agnes ausstellt und eine Person empfängt.
   * Verifikation 3: [Abfrage-Interface, Org-Org-Konstellation mit Agnes als Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#g1=r=issuer&g2=r=recipient,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien). Angezeigt sind Events, in denen eine andere Organisation ausstellt und St. Agnes empfängt.

### **Exploration**

- [~] **Zeitstrom** (Herkunft: eigene Beobachtung, Stakeholder-Protokoll A.5.2)
   * Befund A.5.2 Detailkorrektur: „Shift + Pfeiltaste" extendierte den Brush nur um eine Dekade, weil die Tastatur-Verschiebung den ursprünglich fokussierten Spalten-`dec` als Anker beibehielt und der Fokus auf dem ausgewählten Knopf hängen blieb. Folge: zweite und dritte Shift-Pfeil-Eingabe lieferten dasselbe Maximum, der Brush wuchs nicht weiter.
   * Umsetzung Stand 2026-05-26: `exploration-timeline.js` rechnet die Ziel-Dekade explizit (`targetDec = dec + step`) und setzt nach `renderChart()` den Fokus auf die Nachbar-Spalte `data-decade="<targetDec>"`. So wandert Brush und Tastatur-Fokus in eins über die Achse, beliebig oft hintereinander. Regression `frontend/tests/test_a52_personennetzwerk_quellen.py::TestZeitstromShiftArrow` sichert das Verhalten ab.
   * Umsetzung Stand 2026-05-26 (D.5.1 Stapel-Achsen-Audit): Page-Intro entfernt fuer Konsistenz zur Personennetzwerk-Seite. Tooltips der vier Stack-Chips geschaerft: jeder Chip erklaert jetzt die konkrete Berechnungs-Logik statt nur die Kategorien-Liste. Quellenkorpus weist Saulenhoehe als Zahl freigegebener Quellen aus. Erschliessungsform macht explizit, dass eine Quelle pro zutreffende Form (R/S/E/N) erneut gezahlt wird und die Saulenhoehe damit Erschliessungs-Belege misst, nicht Quellen. Transaktionstyp weist Coverage rund ein Viertel und Top-8-Filter aus. Geschlecht benennt vollstaendig fuenf Buckets inklusive `unspecified`. Geschlechts-Bucket-Logik korrigiert: Quellen mit Personen ohne sex-Annotation landen jetzt in eigenem Bucket "ohne Geschlechtsangabe" (sand-toniert #a08470) und nicht mehr in "ohne Personen"; getrennt via `pcd > 0` versus `pcd == 0`. Chart-Header dynamisch: TX-Modus zeigt die echte Coverage-Rate aus `transactions.json.coverage` (rund 25 % im Stand 2026-05-26), Form-Modus weist die Mehrfach-Zaehlung im Titel aus. Acht zusaetzliche Regressionen in `TestZeitstromPage` und `TestZeitstromAxisLogic`.
   * Offen: weitere A.5.1-Themen (Brush-Reset-Verhalten, Drill-Sortierung) noch nicht durchgegangen. Geschlechts-Achse bleibt eine binaere Heuristik mit der bekannten Schwaeche "ein einzelner annotierter Mann in einer Quelle stempelt sie als 'nur maennlich'", was die Mit-Anwesenheit unmarkierter Personen verbirgt; eine wirklich saubere Loesung waere eine separate Achse "Anteils-Darstellung" (Stacked-Area), bisher zurueckgestellt.
- [~] **Personennetzwerk** (Herkunft: eigene Beobachtung, Stakeholder-Protokoll A.5.2)
   * Befund A.5.2: „Nachvollziehbarkeit relationaler Aussagen muss verbessert werden — Quellen direkt verlinkt, Beziehungsbegriffe überprüfbar, relationale Aussagen leichter auf ihre Grundlage zurückführen." Die Detail-Tabelle zeigte je Verbindung nur einen Belege-Zähler (4); für eine Verifikation am Quelltext fehlte der Sprung in die zugehörigen Urkunden. Außerdem nutzte das Grouping nur die Wortlaut-Form `l` ("pruder"), nicht die normalisierte Form `ln` ("bruder"), und die Tabelle bot keine Möglichkeit, beide nebeneinander zu sehen.
   * Umsetzung Stand 2026-05-26 (Erste Iteration): Spalte „Belege" in „Quellen" umbenannt und mit klickbaren Chips (Signatur · Datum) gefüllt; Hover blendet den Regest-Anriss als Hint ein, Klick öffnet die jeweilige Quellen-Detailseite. `exploration-network.js` sammelt jetzt `r.ln` zusätzlich zu `r.l`; die Bezeichnungs-Zelle zeigt die Manuskript-Form und blendet die normalisierte Form kursiv in Klammern dazu, sobald sie sich unterscheidet. `docs_lookup.json` wird vor dem ersten Render abgewartet, damit Chips nicht zunächst als unresolved erscheinen. CSS in `exploration.css` (`.net-source-chips`, `.net-source-chip`, `.net-label-norm`).
   * Umsetzung Stand 2026-05-26 (Zweite Iteration, drei Phasen): **Layout** auf zweispaltig umgebaut, Filter inklusive Active-Filter-Strip als horizontale Leiste oberhalb (`.explore-filterbar`, `.explore-net-layout`); Graph links, Detail-Tabelle rechts mit internem Scrolling, stack auf eine Spalte ab Viewport < 1100 px; Such-Dropdown absolut positioniert, damit es das Layout beim Aufklappen nicht verschiebt. **Akteursnetzwerk**: Organisationen werden gleichwertige Mittelpunkte, Aggregator (`frontend/aggregator/relations.py`) liefert `orgs[]` mit Anzeigenamen aus `organisations.csv` (421 referenzierte Orgs), JS baut einen gemeinsamen ACTORS-Index und spiegelt Personen-Edges zu Org-Edges, sodass eine Org als Center alle mit ihr verbundenen Personen anordnet. **Tooltips und Legende**: SVG-`<title>` durch `data-hint` ersetzt (projektweit konsistent via `hint.js`); Edges zeigen Beziehungstyp, Bezeichnung (raw und normalisiert) und Quellen-Anzahl; Knoten zeigen Name, Personen-Geschlecht oder Org-Markierung und Gesamt-Verbindungen; Beziehungstyp-Chips bekommen farbige Swatches und sind zugleich Filter und Legende (`.net-type-swatch`). Audience-Banner entfernt, da redundant zur Nav-Badge „Intern". Regressionen in `frontend/tests/test_a52_personennetzwerk_quellen.py` (21 Tests).
   * Umsetzung Stand 2026-05-26 (Dritte Iteration, Visual-Polish-Pass nach erstem Sichttest): Detail-Tabelle bekommt feste Spalten-Breiten via `colgroup` (Akteur 26 %, Beziehung 17 %, Bezeichnung 21 %, Quellen 36 %) und `table-layout: fixed`, leere Aktionen-Spalte entfernt. Quellen-Chips kompakter: nur noch die Signatur als sichtbares Label, das Datum wandert in den Hover-Hint (zusammen mit dem Regest-Anriss); Chip-Padding und Font auf `text-2xs` reduziert. Center-Label bekommt einen Hintergrund-Halo (`stroke="var(--color-bg)" paint-order="stroke"`) und mehr Abstand zum Knoten, damit es auch ueber dunklen Geschlechts-Farben lesbar bleibt; Neighbor-Labels analog. Org-Knoten skalieren jetzt wie Personen-Knoten nach Verbindungsanzahl (`nodeRadius(getEdgeCount(...))`) statt fix `r=8`, damit die Akteurs-Gleichwertigkeit auch visuell sichtbar bleibt. Active-Filter-Strip in der Filterleiste verliert die dashed Border-Top zugunsten kompakter, harmonischerer Einbettung. Sieben zusaetzliche Regressionen in `TestNetworkLayoutPolishV3`.
   * Umsetzung Stand 2026-05-26 (Vierte Iteration, Hub-Skalierung): Der Ego-Layout-Ring bricht bei Hub-Akteuren wie `org__wien` mit 725 Beruf-/Stand-Verbindungen zur unleserlichen Knoten- und Linien-Wolke zusammen. Zwei Schwellwerte loesen das. `MAX_GRAPH_NODES = 48` kappt die im Graph sichtbaren Nachbarn, vorher absteigend nach Quellen-Anzahl sortiert, damit die belegstaerksten Verbindungen bleiben. `LABEL_THRESHOLD = 18` blendet statische Knoten-Labels ab mittlerer Dichte aus, die Hover-Tooltips uebernehmen die Identifikation. Wenn gekappt wird, weist der Block-Header die Nutzerin darauf hin, dass im Graph nur die N quellenstaerksten Verbindungen liegen; die Detail-Tabelle behaelt alle Eintraege und ist die kanonische Sicht. Wien als Mittelpunkt geht damit von tausend ueberlagernden Beschriftungen zu 48 lesbaren Knoten, deren Identitaeten ueber Hover und Tabelle nachvollziehbar bleiben. Sechs zusaetzliche Regressionen in `TestNetworkHubScalability`.
   * Offen: Personennetzwerk und Akteursnetzwerk-Substanz sind (per A.6) nur im internen Build sichtbar. Für die öffentliche Ausspielung muss die A.6-Diskussion zur Exploration-Sichtbarkeit fortgeführt werden, bevor die A.5.2-Verbesserungen ein öffentliches Publikum erreichen. Phase 4 (Sortier-Toggle, Profil-Sprung-Icon) zurückgestellt, bis konkrete Beobachtungen am internen Build vorliegen.
- [ ] **…**

### **Projekt**

**Aktuell sind hier nur Platzhalter.** Schickt mir bitte alle diese Texte. Sie liegen dann als .md-Dateien im Repository und können dort bearbeitet werden. Anschließend werden sie als HTML angezeigt.

- [~] **Projekt** (Herkunft: eigene Beobachtung, Stakeholder-Protokoll A.6)
   * Bearbeiten: [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition/edit/main/frontend/content/project/about.md](https://github.com/chpollin/db_for_medieval_legal_transactions_edition/edit/main/frontend/content/project/about.md)
   * Ansehen: \<PAGES\_BASE\>/project/about.html
   * Umsetzung Stand 2026-05-26: Sechs Sektionen (Projektbeschreibung, Forschungskontext, Forschungsfragen, Annotationsmodell, Technische Umsetzung, Qualitätssicherung) auf neutralen Platzhalter „Text in redaktioneller Überarbeitung." gesetzt (commit 2241aa10c7). Hintergrund: Stakeholder-Punkt A.6 fordert wissenschaftlich belastbare Referenztexte; bis zum Sign-off durch das Editorenteam bleibt der Inhalt ausgeblendet.
   * Offen: Inhalt liefern (Projektbeschreibung, Forschungskontext, Forschungsfragen, technische Umsetzung, …).
- [ ] **Annotationsrichtlinien** (Herkunft: eigene Beobachtung)
   * Bearbeiten (kanonische Quelle, Schwester-Repo): [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions/edit/main/edition\_guidelines.md](https://github.com/chpollin/db_for_medieval_legal_transactions/edit/main/edition_guidelines.md)
   * Ansehen: \<PAGES\_BASE\>/project/edition-guidelines.html
   * Hinweis: Dieselbe Quelle, die das Datenmodell mit RelaxNG definiert. Die Datei lebt im Daten-Repo. Der Build dieses Frontends synchronisiert sie automatisch, wenn sie sich geändert hat. Lokale Arbeitskopie im Frontend (nicht bearbeiten) liegt unter `frontend/content/project/edition-guidelines.md`.
- [~] **Glossar** (Herkunft: eigene Beobachtung, Stakeholder-Protokoll A.6)
   * Bearbeiten: [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition/edit/main/frontend/content/project/glossar.md](https://github.com/chpollin/db_for_medieval_legal_transactions_edition/edit/main/frontend/content/project/glossar.md)
   * Ansehen: \<PAGES\_BASE\>/project/glossary.html
   * Befund Stakeholder A.6: „Mehrere Texte im Glossar wirken derzeit stilistisch und terminologisch uneinheitlich. Insbesondere bei wissenschaftlichen Definitionen sollte stärker redaktionell überarbeitet, terminologisch vereinheitlicht und fachlich präzisiert werden. Die Definitionen sollten als wissenschaftlich belastbare Referenztexte funktionieren."
   * Umsetzung Stand 2026-05-26: Alle 17 Glossar-Einträge auf neutralen Platzhalter „Definition in redaktioneller Überarbeitung." gesetzt (commit 2241aa10c7). Anker bleiben erhalten, damit die Tooltip-Verlinkung weiter funktioniert. Parallel auf neun Inline-Tooltip-Bodies mit `slug=`-Verweis (Quellenkorpus, Quelle, Regest, Beteiligte, Rolle, Rechtsgeschäft, Funktionsrollen) und auf die drei Matrix-Spalten-Definitionen der Startseite (`_kpi.py`) erstreckt, damit das UI keine inkonsistente Mischung aus alter Definition und Platzhalter zeigt. Glossar-Eintrag aus dem Projekt-Dropdown der Nav entfernt (commit 0c43b0b2f2), da der Inhalt aktuell nur Platzhalter trägt; die Seite bleibt für die Tooltip-Anker erreichbar.
   * Offen: Editorenteam liefert wissenschaftlich belastbare Definitionen für die 17 Begriffe und die parallel laufenden Tooltip-Bodies.
   * Hinweis: Speist auch UI-Tooltips an mehreren Stellen.
- [ ] **Impressum** (Herkunft: eigene Beobachtung)
   * Bearbeiten: [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition/edit/main/frontend/content/impressum.md](https://github.com/chpollin/db_for_medieval_legal_transactions_edition/edit/main/frontend/content/impressum.md)
   * Ansehen: \<PAGES\_BASE\>/impressum.html
   * Offen: Inhalt liefern (Verantwortliche, Forschungsprojekte, technische Umsetzung, Lizenz CC BY 4.0, Datenquellen, Zitierweise, Kontakt, …)
- [?] **Welche Lizenzen, wie genau und kleinteilig (TEI, XML, Frontend etc.)?** (Herkunft: eigene Beobachtung)
   * Vorschlag: Alles CC-BY.
   * Offen: Sign-off der Projektpartner.
- [ ] **Lizenz für Code → LICENSE\-Datei im Repo** (Herkunft: eigene Beobachtung)
- [?] **Wie schauen Zitierempfehlungen aus?** (Herkunft: eigene Beobachtung)
- [?] **Zitations-Button funktioniert, in den Zitaten lässt sich aber keine gängige Zitierform erkennen.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Offen: Welche Zitierform wird gewünscht (Chicago Author-Date, MLA, fußnotenbasiert, etc.)?

### **Entitäten Views (Quellen, Personen, Organisationen)**

- [x] **Verlinkung Person | Organisation → Urkunden** (Herkunft: eigene Beobachtung)
   * Befund: Jede Profil-Seite (Personen und Orgs) trägt eine Quellen-Tabelle mit Signatur, Datum, Korpus, Bezeichnung, Rolle und Regest-Anriss. Verifikation: [Burg Kufstein](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html).
- [?] **Verlinkung Urkunden → Person | Organisation** (Herkunft: eigene Beobachtung)
   * Befund: Direkte Annotationen (`<rs type="person">`, `<rs type="org">`) werden im Quellen-HTML als klickbare Links gerendert und in der Annotationen-Tabelle aufgeführt. Restproblem sind implizite Org-Refs via `roleName corresp`, abgedeckt im konkreten Punkt „Relationale Tags sichtbar machen" im Org-Register.
- [ ] **Quellenansicht** (Herkunft: eigene Beobachtung)
   * Beispiel: [https://chpollin.github.io/db\_for\_medieval\_legal\_transactions\_edition/documents/QGW/Vienna\_1177-1414\_ready/105.html](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/105.html)
- [ ] **Person** (Herkunft: eigene Beobachtung)
   * Beispiel: [https://chpollin.github.io/db\_for\_medieval\_legal\_transactions\_edition/register/persons/pe\_\_adelheid\_QGW\_II\_I\_1111.html](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons/pe__adelheid_QGW_II_I_1111.html)
- [ ] **Organisation** (Herkunft: eigene Beobachtung)
   * Beispiel: [https://chpollin.github.io/db\_for\_medieval\_legal\_transactions\_edition/register/orgs/org\_\_klosterneuburg-augustiner\_chorherren.html](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__klosterneuburg-augustiner_chorherren.html)

#### Faksimile-Viewer und Quellen-Metadaten

- [x] **Zoom-Funktion der Digitalisate ist nicht navigierbar, vergrößerte Ausschnitte lassen sich nicht verschieben.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Umsetzung: Der Faksimile-Viewer wurde neu gebaut. Ausschnitte lassen sich jetzt mit dem Mausrad oder den Knöpfen vergrößern, mit gehaltener Maustaste verschieben und um 90 Grad drehen; ein Knopf stellt die ursprüngliche Ansicht wieder her.
   * Verifikation: [QGW Vienna Nr. 100](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/100.html)
- [x] **„Datenherkunft" ist unklar formuliert („Wiener Stadt- und Landesarchiv 9 Pers., 0 Org.").** (Herkunft: Stakeholder-Review 11.05.2026)
   * Umsetzung: Label „Datenherkunft" durch „Aufbewahrungsort" ersetzt, Inhalt reduziert auf Archivname (`tei:repository`) und Monasterium-Link. Personen- und Organisations-Counts wandern aus dem Footer in den Annotations-Summary mit Aufschlüsselung nach Typ (commit c0454a27df).
   * Verifikation: [QGW Vienna Nr. 1022](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html)
- [x] **„Originaldatierung" wird nicht ganz angezeigt und ist nicht notwendig, da sie ohnehin im Regest steht.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Umsetzung: Feld entfernt.
- [x] **Dispositivformeln werden nicht klar voneinander getrennt dargestellt.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Umsetzung: Jede Dispositivformel im Quellentext wird mit einer gestrichelten Unterstreichung in der Trigger-Farbe markiert (konsistent mit dem Legenden-Swatch), und jede trägt einen Hover-Tooltip „Dispositivformel — Verb, das das Rechtsgeschäft anzeigt" (commit c0454a27df).
   * Verifikation: [QGW Vienna Nr. 1022](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html), fünf benachbarte Dispositivformeln im Regest sind jetzt einzeln erkennbar.
- [~] **Mehrere Kategorien innerhalb der Annotationstabellen erscheinen unklar oder nicht notwendig. Tabellen auf wissenschaftlich nachvollziehbare und öffentlich verständliche Kategorien reduzieren.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Umsetzung Stand 2026-05-23 (Annotations-Politur, Tab-Konsolidierung, lokales Polish):
      * **Tab-Konsolidierung.** Die drei Sub-Tabellen (Entitäten, Dispositivformeln, Editorische Ergänzungen) leben in einer zentrierten Tab-Pillen-Leiste, nur eine Tabelle ist gleichzeitig sichtbar. Counts stehen in den Tab-Pillen selbst (z. B. „Entitäten 19"). Bei nur einer sichtbaren Tab wird der Tab-Strip ganz ausgeblendet, damit kein Either-Or-Schalter ohne Alternative steht. Dispositivformeln-Tab ist in der öffentlichen Sicht als `.dev-only` versteckt, in der privaten Sicht (`?dev=1`) sichtbar mit gelbem Rahmen plus „Entwicklung"-Label. Die analoge Event-Gruppierung der Dispositivformeln- und Editorische-Ergänzungen-Tabellen entfällt, weil sie durch die Tab-Trennung redundant würde.
      * **Block-Header schlanker.** Untertitel entfernt, Counter-Pille rechts oben entfernt, Trennlinie unter dem Header entfernt. Der Block-Titel „Annotationen" steht jetzt allein als Anker, die Zahlen leben in den Tab-Pillen und im Section-Header pro Event.
      * **Entitäten-Tabelle visuell aufgeräumt.** Typ-Spalte raus, dafür ein farbiger Punkt vor der Nennform als visueller Type-Marker (Annotations-Token-Farbe pro Person/Org/Ort), Tooltip nennt den Typ aus. Funktionsrolle als gefüllte Akzentblau-Pille (kontrolliertes Vokabular, eine Rolle pro Zelle). Attribute als umrandete Tags pro Wert (statt Komma-getrennter Text), Type-Information liegt im Hover-Tooltip. Geschlecht ausgeschrieben „weiblich"/„männlich"/Halbgeviertstrich, kein Glyph mehr.
      * **Section-Header pro Event.** Disp-Vorschau als kursive Erst-und-Letzte-Trigger-Spanne mit `…` in der Mitte (z. B. „stiftet … bestellt"), rechts „N Genannte". Die rohe `ev__`-ID ist nicht mehr sichtbar. Die Disp-Vorschau übernimmt die Mini-Titel-Funktion des Geschäfts.
      * **Bug-Fixes.** Sortier-Pfeile auf den Spaltenköpfen brechen nicht mehr unter das Spaltenlabel (`white-space: nowrap`). Sortier-Pfeile aus `person.css` in `components.css` gezogen, sodass alle `.sortable-table`-Tabellen projektweit dieselben Sort-Indikatoren tragen.
      * **Vorgängerstand (commit c0454a27df).** Redundante „Ereignisse"-Untertabelle entfernt, Entitäten nach Top-Level-Event gruppiert, nested events in die Eltern-Gruppe kollabiert, Spalten umbenannt (Entität → Genannt als, Rolle → Funktionsrolle), Spalte Abschnitt entfernt, neue Spalte Geschlecht, Spalten-Header-Tooltips, xml:id aus Zellen entfernt, gruppen-aware Sortierung.
   * Verifikation: [QGW Vienna Nr. 1022](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html) (Mehrfach-Disp-Worst-Case mit Datenfehler-Spur bei Stephans witib), [QGW Vienna Nr. 23](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/23.html) (Einfach-Event-Fall), [QGW Vienna Nr. 320](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/320.html) (Multi-Event mit gefülltem Editorische-Ergänzungen-Tab), [Stadtbuch I Nr. 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html) (Stadtbuch-Format), [QGW Nr. 1022 mit `?dev=1`](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html?dev=1) (private Sicht mit Dispositivformeln-Tab eingeblendet).
   * Offen (Backlog): kleine „erwähnt"-Pille auf Zeilen, die nur aus eingebetteten Ereignissen stammen. Architektur-Konsolidierung über ein geteiltes `table-core.js`-Modul (Cell-Renderer für Type-Marker, Funktionsrollen-Pille, Attribut-Tags, Geschlechts-Label, Sortier-Logik), das die jetzt page-lokale Logik in `document.js`/`register.js`/`profile.js`/`basket-page.js`/`analysis-resolver.js` konsolidiert.

### **Sonstiges und Daten**

- [ ] **Texte auf Startseite** (Herkunft: eigene Beobachtung)
- [x] **Hover-Tooltips für alle Annotations-Typen im Quellentext** (Herkunft: eigene Beobachtung)
   * Umsetzung: Vorher hatten nur `rs[@type='person|org|place']` einen `data-hint` mit Type-Label. Triggerstrings (Dispositivformeln und Funktionsrollen-Verben), `roleName`-Attribute (alle Subtypen wie Verwandtschaft, Titel, Beruf, Stellvertretung etc.) und `add` (editorische Ergänzungen) tragen jetzt ebenfalls einheitliches `data-hint` plus `data-hint-type`. Coverage in QGW Nr. 1022 stieg von 13/40 auf 32/40 Annotationen mit Tooltip (commit c0454a27df).
- [x] **Einheitlicher Tooltip-Look projektweit** (Herkunft: eigene Beobachtung)
   * Umsetzung: Native `title="..."`-Tooltips (Browser-Default) durchgehend auf das projekteigene `data-hint`-System mit `hint.js` migriert. Betrifft Facsimile-Buttons, Exploration-Chips, Korpus-Sidebar-Chips, Cite-Copy-Buttons, Sparkline-Bars und Decade-Säulen im Zeitstrom, Geschlechtsbars im Aggregat, Network-Recenter-Buttons (commit c0454a27df).
- [x] **Mechanik öffentliche vs. interne Sicht (dev-only)** (Herkunft: Editions-Workflow)
   * Umsetzung Stand 2026-05-23: Eine universelle CSS-Klasse `.dev-only` ist projektweit nutzbar. Default-Sicht blendet markierte Elemente aus, URL-Parameter `?dev=1` setzt `.dev-mode` auf `<html>` und macht sie sichtbar mit einem gelben gestrichelten Rahmen plus „Entwicklung"-Label am rechten oberen Rand. Ersetzt die wiederkehrende „öffentlicher Build versus interner Build"-Frage durch einen URL-Schalter im selben Build, der editorisch zwischen Sichten hin- und herschalten lässt, ohne separate Build-Stände wie Stufe 2 oder Stufe 4 zu produzieren. Erste Anwendung ist die Dispositivformeln-Sub-Tabelle in der Annotationsansicht der Quellen-Detailseite. Mechanik liegt in `frontend/static/css/document.css` (Selektor) und `frontend/static/js/document.js` (URL-Parameter-Schalter), kann projektweit in andere Module ausgerollt werden.
   * Ergänzung Stand 2026-05-23 (commit 0c735eeb17, Begriffsumbenennung 2026-05-26 zuerst public/private analog GitHub-Repos, am selben Tag auf oeffentlich/intern): Zweite Build-Schicht über das Audience-Modul (`frontend/audiences.py`). CLI-Flag `--audience oeffentlich|intern` greift orthogonal zur Stufenwahl. `--audience intern` hängt `-intern` an das Stage-Output-Verzeichnis (Stufe 1 plus intern landet in `docs-intern/`) und blendet ganze Sektionen und Datenpunkte vor dem Rendern in den Build ein. `?dev=1` und `--audience` lösen verschiedene Probleme: Audience entscheidet, *ob* etwas im Output enthalten ist; Dev-Mode entscheidet, *ob* enthaltene Elemente sichtbar geschaltet werden. Spec in [`knowledge/specification.md`](specification.md) unter „Öffentliche versus interne Sicht in zwei Schichten".
   * Verifikation: Beliebige Quellen-Detailseite mit und ohne `?dev=1` vergleichen, z. B. [QGW Vienna Nr. 23 öffentlich](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/23.html) versus [QGW Vienna Nr. 23 intern](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/23.html?dev=1).
- [x] **Build-Stand auf der Nav-Badge sichtbar machen** (Herkunft: eigene Beobachtung)
   * Umsetzung Stand 2026-05-26 (commit 0c43b0b2f2): Die Nav-Badge zeigt statt nur „Prototyp" jetzt „Prototyp · {Audience-Label} · {Build-Datum}", z. B. „Prototyp · Öffentlich · 26. Mai 2026" oder „Prototyp · Intern · 26. Mai 2026". Title-Tooltip trägt die ausführliche Form für Screenreader. Damit ist auf jeder Seite ohne Footer-Blick erkennbar, welche Sicht gerade gerendert ist und wann der Build entstand. Ergänzt das rote „Interne Version"-Banner, das im internen Build aktiv ist; im öffentlichen Build steht nur die Badge.
- [ ] **Glossar-Tooltips und Datenpunkt-Provenance** (Herkunft: eigene Beobachtung)
   * Offen: Glossar-Texte als `tip_glossary`-Popover an UI-Stellen einsetzen, an denen Fachbegriffe stehen (Quellenkorpus, Event, Rechtsgeschäft, Regest etc.). Eigene Tooltip-Form, neben dem Hover-Hint-System.
   * Offen: Datenpunkt-Provenance-Popover an Zahlen auf der Startseite und in Aggregat-Quadranten (zeigt, woher die Zahl kommt).
- [~] **Datenkorb-Erklärung ergänzen** (Herkunft: Stakeholder-Protokoll 18.05.2026 A.1.2: „Datenkorb als gute Idee aber Erklärung und Testung notwendig.")
   * Umsetzung Stand 2026-05-23 (commit 9af4ca93d9): Mehrteiliger Erklär-Block direkt unter dem Titel: Persistenz (lokal im Browser, kein Login, kein Server-Sync, geht beim Cache-Leeren verloren), Bedeutung der Status-Marker „gesammelt" und „abgeleitet" inkl. Beförderungs-Mechanik per „*"-Knopf, Export-Verhalten der drei Knöpfe. Export-Knöpfe paarweise beschriftet: „Nur gesammelte exportieren" und „Mit abgeleiteten exportieren". Quellen-Knopf einfach „Quellen exportieren" (Quellen werden nicht abgeleitet). Spalte „Aktiv" in der Personen-Tabelle umbenannt zu „Datum der Quellen" plus Tooltip, konsistent mit Personen- und Org-Profil. Tooltip am Korb-Button in der Topbar ergänzt.
   * Überholt 02.06.2026 (Punkt E1): Der Topbar-Counter summierte alle Einträge über alle Sektionen zu einer Zahl (1 Quelle plus 40 abgeleitete Personen = 41), was als unklar bemängelt wurde. Jetzt zeigt der Badge pro Entitätstyp eine eigene farbige Pille (Quelle grün, Person blau, Organisation violett); der Tooltip nennt dieselben Zahlen plus den abgeleiteten Anteil. Dazu ein globaler „Gesamten Datenkorb leeren"-Button. Siehe Abschnitt „Stakeholder-Durchgang 02.06.2026".
   * Verifikation: [Datenkorb-Seite](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/korb.html). Hover über Korb-Button in der Topbar zeigt die Aufschlüsselung.
   * Offen: Sign-off Stakeholder. Sortierung der Tabellen und Such-/Filter-Funktion im Korb für große Sammlungen wären ein nächster Ausbau-Schritt.

- [x] **Glossar-Links in der Korpora-Übersicht auf der Startseite funktionieren nicht.** (Herkunft: Stakeholder-Protokoll 18.05.2026 A.1.1)
   * Umsetzung Stand 2026-05-23 (commit 3d5bf5f7e3): Das Macro `tip_glossary` zog `root_path` aus dem Template-Kontext, wurde aber in allen neun Templates ohne `with context` importiert. Dadurch entstand ein absoluter Pfad `/project/glossary.html#...`, der auf GitHub Pages mit Subpfad auf die falsche Domain-Root zeigte. Fix: alle neun Templates importieren `tip_glossary` (und benachbarte Macros) jetzt mit `with context`. Pattern in [`knowledge/test-strategy.md`](test-strategy.md) und CLAUDE.md Agent-Regeln festgehalten.
   * Verifikation: [Startseite](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/), Klick auf „im Glossar"-Link in den Korpus-Spalten der Korpora-Übersicht öffnet die Glossar-Seite mit dem richtigen Anker.

- [~] **Disp-Vorschau im Annotations-Section-Header als Quellenzitat visuell markieren.** (Herkunft: Eigene Beobachtung, Diskussion 23.05.2026)
   * Umsetzung Stand 2026-05-23 (commit 8db6b7adb0): Counter „N Genannte" wandert in eine eigene schmale Header-Zeile rechts oben. Disp-Vorschau steht in eigener zentrierter Zeile darunter, in deutschen Anführungszeichen via `<q lang="de">`, kursiv und gedämpft grau, klar abgesetzt von der rotbraunen Inline-Trigger-Farbe im Volltext. Counter-Grammatik passt sich an (1 Genannter / N Genannte). Bei Rechtsgeschäften ohne Disp-Vorschau (häufig im Stadtbuch-Korpus) bleibt die zweite Zeile leer, statt der früheren rohen Event-ID erscheint nichts.
   * Verifikation: [QGW Nr. 1245](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1245.html) (Vidimierungs-Fall mit Auslassungspunkten), [QGW Nr. 1022](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html), [Stadtbuch 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html) (Fallback-Fall, nur Counter).
   * Offen: Stakeholder-Sign-off. Wenn bei Fallback-Fall ein sprechender Text gewünscht ist (z. B. „Rechtsgeschäft im Stadtbuch-Eintrag"), ist das ein zeilen-kleiner JS-Patch. UI-Konvention in [`knowledge/ui-design.md`](ui-design.md) unter „Section-Header in Tabellen mit Quellenzitat" festgehalten.
- [~] **Es muss möglich sein, anzeigen zu lassen, welche Personen in einem bestimmten Band der QGW vorkommen.** (Herkunft: Stakeholder-Anfrage)
   * Befund: Personen- und Organisations-Register tragen in der Sidebar einen Korpus-Filter (`frontend/templates/register_list.html:34`, `sidebar_corpus_chips`), Mehrfachauswahl möglich. Im freigegebenen Korpus existiert bisher nur ein QGW-Band (`QGW/Vienna_1177-1414_ready`), daher entspricht „in bestimmtem Band" aktuell genau dem QGW-Chip. Verifikation: [Personen-Register, Sidebar-Bestandsfilter](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html).
   * Offen: Sign-off Stakeholder, ob das Band-Konzept hinreichend abgedeckt ist. Bei künftiger Freigabe weiterer QGW-Bände wird der Filter automatisch um den jeweiligen Chip ergänzt.
- [x] **Belege-Zähler im Org-Profil-Block „Personen mit Tätigkeitsverbindung" zeigte 0 statt der tatsächlichen Anzahl.** (Herkunft: eigene Beobachtung 23.05.2026)
   * Befund: Beispiel Burg Kufstein hatte Rudolf von Rosenheim (phleger) mit Belege-Count 0, obwohl die Quelle 223a (Stadtbuch I) ihn ausweist. Bug-Quelle in `frontend/aggregator/org_profiles.py::_build_occ_network`: der Lookup `file_lookup.get(fk, {})` rief mit `fk` als `file_key` an, aber `file_lookup` ist nach `(collection_path, idno)` verschlüsselt — strukturell konnte der Treffer nie kommen, die Files-Liste blieb leer.
   * Umsetzung Stand 2026-05-23 (commit 045aa03bff): Neue Funktion `file_meta_by_key()` in `frontend/aggregator/_profile_enrichment.py`, die `filenames.csv` direkt nach `file_key` indiziert und idno, URL, Datum, collection_path zurückgibt. `_build_occ_network` nutzt jetzt diesen Lookup und liefert echte Belege.
   * Regression: `frontend/tests/test_occ_network_belege.py` prüft, dass die phleger-Zeile im Kufstein-Profil mindestens einen Beleg trägt.
   * Verifikation: [Burg Kufstein, Block „Personen mit Tätigkeitsverbindung"](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html) zeigt jetzt Belege 1 für Rudolf von Rosenheim mit Verlinkung auf [Stadtbuch I Nr. 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html).
- [~] **Verifikations-Drift-Sicherung: Forschungsfrage 3 (occ St. Stephan) vergleicht Frontend gegen Pipeline-Sollwert.** (Herkunft: eigene Verifikations-Arbeit 23.05.2026)
   * Umsetzung Stand 2026-05-23 (commit 583c641434): Stufe 4 der Verifikation (`verification/research_questions.py`) liest jetzt zusätzlich zum Pipeline-Sollwert auch das gerenderte Org-Profil und vergleicht drei Werte (section_count im Block-Header, row_count im tbody, kin_sum der rel-col-kin-Spalte). Klassifikation: `match` (gleich), `known_gap` (Frontend kleiner wegen Korpus-Freigabe-Filter, erwartbar), `mismatch` (Frontend größer als Sollwert, echter Aggregator-Drift), `no_frontend` (Profil nicht gerendert). Aktueller Stand St. Stephan: 113 Personen von 156 Sollwert (`known_gap`), 11 kin-Records von 20 (`known_gap`), section_count == row_count (`match`).
   * Regression: `verification/test_research_questions.py` mit acht Tests prüft die Klassifikation und blockiert künftigen Aggregator-Drift (`mismatch` fällt als Bug auf).
   * Verifikation: `python -m verification.run --research-questions` schreibt nach `verification/reports/research_questions-YYYY-MM-DD.{md,json}`.
- [x] **Verifikations-Ziel auf die interne Fassung umgestellt, Scope-Fehlalarme behoben.** (Herkunft: eigene Verifikations-Arbeit 27.05.2026)
   * Befund: Das Test-Set (`verification/`) re-aggregiert TEI im released-Scope (`is_released_corpus`, fünf Subkorpora), verglich aber fest gegen `docs/` (öffentlicher Build). Seit der Korpus-Trennung ist der öffentliche Build bewusst schmaler (nur die zwei freigegebenen Korpora). Dadurch meldete `verification.run` Scope-Differenzen als Mismatch, die keine echte Drift sind, etwa `docs.date_range.QGW` mit 1457 aus dem released-TEI gegen 1414 im öffentlichen Build sowie die beiden Occurrence-Zähler.
   * Umsetzung (Commits d016e6189d Code, 8f6103476f Reports): Default-Ziel jetzt `docs-intern/` (released-Scope, deckt sich mit dem TEI-Lesebereich des Test-Sets), per Umgebungsvariable `VERIFICATION_DOCS_DIR` überschreibbar (`VERIFICATION_DOCS_DIR=docs` für den öffentlichen Build). `run.py` bricht mit Bauanweisung ab, wenn das Ziel fehlt. Per-Korpus-Datumsspannen-Checks behandeln Korpora außerhalb von `COLLECTIONS_WITH_TEI` als `known_gap` statt Mismatch, damit das freigegebene, aber vom Parser noch nicht abgedeckte Satzbuch CD keinen Fehlalarm erzeugt. Ergebnis gegen frisch gebautes `docs-intern`: sechs Mismatches auf drei reduziert. Regression `frontend/tests/test_verification_target.py`. Verifikation: `python -m frontend build --audience intern`, dann `python -m verification.run --all`.
   * Offen (an Stakeholder und Projektpartner):
       1. **Satzbuch CD im Test-Set abdecken.** SB_CD ist freigegeben, liegt als TEI vor und ist Teil der internen Fassung, wird vom Verifikations-Parser aber noch nicht gelesen (Datumsangaben und Personennennungen in abweichender Annotationsstruktur). Aktuell `known_gap`. Volle Abdeckung wäre ein eigener Arbeitsschritt: `parse_tei` an die SB_CD-Struktur anpassen, `COLLECTIONS_WITH_TEI` erweitern, dann die dabei auftauchenden neuen Befunde abarbeiten.
       2. **`html.persons.display_name` (154 Fälle), methodische Differenz.** Das gerenderte Profil zeigt den zusammengesetzten Anzeigenamen (zum Beispiel „Albrecht Hergensperger der Zimmermann"), das Test-Set vergleicht gegen das CSV-Feld `name` („Albrecht der Zimmermann"). Kein Drift, sondern ein Vergleich gegen das falsche Feld. Entscheidung: den Vergleich auf das passende Feld ziehen oder als `known_gap` führen.
- [ ] **Technische Refactors, sicher aber zurückgestellt.** (Herkunft: eigene Beobachtung 27.05.2026, Milestone M7)
   * Umsetzung: CSS-Token-Konsolidierung (Commit 78ee2c0912), esc-Delegation in `exploration-network.js` (1ac8aaf097), `_format_death_german`-Entdopplung und Import-Reihenfolge (bf0f8553af). Alle mit Test bzw. verhaltensgleich.
   * Offen: (1) Das Rollen-Schlüssel-Tupel (issuer/recipient/witness/other) liegt vierfach (`person_profiles._ROLES`, `org_profiles._ROLES`, `role_constellation.VALID_ROLES`, `_pages.PERSON_ROLES`). Konsolidierung auf ein gemeinsames Konstanten-Modul ist sicher, weil es die Schlüssel betrifft, nicht die gendergerechten Labels (die hängen an der Gender-Entscheidung oben). (2) Die zwei Range-Slider-Implementierungen (`table-infra` gegen `viz-core`) zusammenführen. (3) Einen gemeinsamen CSV-Exporter mit einheitlichem Zeilenende. Punkte (2) und (3) sind interaktive UI und brauchen manuelle Browser-Prüfung. (4) `basket-page.js` hält ein eigenes `esc`, ohne `EdCore` zu referenzieren; vor einer Vereinheitlichung prüfen, ob `core.js` auf `korb.html` geladen ist. Hinweis: `EdCore.getParam` ist trotz Plan-Annahme nicht tot, `test_m2.py` fordert es ausdrücklich.
- [ ] **Konsistenz-Ziel erreichen. Alle Zahlen im Interface stimmen mit den überprüften Korpora im Git-Repository überein. DB-Datenqualität hat Vorrang, Frontend-Korrekturen folgen der DB.** (Herkunft: eigene Beobachtung)
- [ ] **Farben und Schriften** (Herkunft: eigene Beobachtung)
- [~] **Rollen-Label-Wording und projektweite Gender-Regel.** (Herkunft: eigene Beobachtung 27.05.2026; Stakeholder-Terminologie-Entscheidung)
   * Entschieden und umgesetzt 02.06.2026 (Commit a91df57): durchgängig Sternform, Numerus kontextabhängig (Singular pro Person, Plural als Kategorie); witness „Zeug*innen / Siegler*innen". Details im Abschnitt „Stakeholder-Durchgang 02.06.2026", Punkt C1. Die folgenden Befunde dokumentieren den Stand davor.
   * Befund: Das kontrollierte Funktionsrollen-Vokabular (issuer/recipient/witness/other) trägt im Code vier verschiedene Gender-Konventionen nebeneinander, ohne projektweite Regel. Stern-Form „Aussteller\*in" zentral in `frontend/role_labels.py` (ROLE_LABELS), konsumiert von `renderer.py` und den Profil-Templates (`person.html`, `org.html`), mit eigener Kopie in `document.js`; Doppelpunkt-Form „Aussteller:in" in `frontend/content/query_vocabulary.json`; Beidnennung „Aussteller / Ausstellerin" in `viz-core.js`; ungegendert „Aussteller" in `register.js` und `analysis-resolver.js`. Für witness zusätzlich abweichendes Wording: „Zeug\*in / Siegler\*in" (renderer, document, Profile), „Zeuge / Siegler" (register, resolver), „Siegler:in / Zeug:in" (viz-core). Die kanonische Quelle `edition_guidelines.md` glossiert die Rollen ungegendert als „Aussteller, Empfänger, Zeuge, sonstige Beteiligung" und hält fest, dass die Rolle witness „sealer or witness" abdeckt. Die TEI-Daten tragen nur den technischen Wert `role="witness"`, kein deutsches Label; die Beschriftung ist reine Anzeige-Schicht und nirgends zentral definiert. Das Frontend kann und soll das nicht von sich aus vereinheitlichen.
   * Offen (Stakeholder-Terminologie-Entscheidung): (1) Eine projektweite Gender-Regel festlegen (Stern `*in`, Doppelpunkt `:in` oder Beidnennung), gendergerecht und über das gesamte UI konsistent. (2) Das witness-Wording festlegen, nur „Zeuge" wie in den Richtlinien oder „Zeuge / Siegler", da die Rolle den Siegler mit abdeckt. Beides muss in der Projekt-Terminologie verankert sein. Erst danach Engineering-Schritt: ein gemeinsames Rollen-Vokabular als Single Source of Truth (heute vierfach kopiert) schaffen und alle Stellen daran ziehen; `knowledge/ui-design.md` nennt aktuell „Zeug\*in" als kanonisch und wäre entsprechend nachzuziehen.
   * Zwischenstand 2026-05-27 (Commit f18e92b064): Der davon unabhängige Anzeige-Bug ist behoben. Der aktive Rollen-Filter-Chip im Register zeigte den rohen englischen Schlüssel (issuer/recipient/...) statt eines deutschen Labels (`ROLE_LABELS[r].long` auf flacher Map ergab immer undefined). Direkter Zugriff `ROLE_LABELS[r] || r`; das Wording selbst bleibt bis zur Entscheidung unverändert.
- [x] **Kategorie „Tod" in „als verstorben genannt" umbenennen.** (Herkunft: Stakeholder-Review)
   * Verifikation: [pe\_\_christian\_von\_strass\_StB\_I\_624](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons/pe__christian_von_strass_StB_I_624.html)

### **Stakeholder-Durchgang 02.06.2026**

Arbeitsstand des Durchgangs, in den jeweiligen thematischen Punkten oben querverwiesen. Diese Sektion löst die frühere separate Datei `OFFENE-PUNKTE-MEETING.md` ab.

#### A) Quellen-Liste und Filter-Sidebar

- [x] **A1 Ausstellungsort aus der Volltextsuche entfernen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commit 8d90d9f, Rebuild 4b16f48): `doc.p` aus dem `_s`-Such-Haystack in `frontend/static/js/index.js` entfernt; Such-Hilfe und Platzhalter angepasst (kein „Ort" mehr). Der Ort bleibt über den eigenen Ort-Filter erreichbar, nicht über die Volltextsuche. Signatur bleibt bewusst durchsuchbar (Fundstelle aus der Fußnote auffindbar). Guard `frontend/tests/test_index_filters.py`.
   * Verifikation: [Quellen-Liste](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html).
- [x] **A2 Erschließungsform-Filter komplett entfernen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commit 8d90d9f, Rebuild 4b16f48): Der gesamte Sidebar-Block (Regest/Siegel/Nota/ohne) aus `frontend/templates/index.html` entfernt. Die JS-Referenzen waren bereits defensiv mit `if (filterFormsEl)` abgesichert, das Entfernen des Markup genügte. Keine Tabellenspalte betroffen, das R/S/E/N-Symbol in den Zeilen bleibt. Löst den früheren offenen Schicht-2-Punkt „Erschließungsform-Filter konsolidieren".
- [x] **A3 Faksimile-Filter komplett entfernen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commit 8d90d9f, Rebuild 4b16f48): Sidebar-Block `id="filter-facs"` aus `frontend/templates/index.html` entfernt, JS ebenfalls defensiv abgesichert. Guard in `test_index_filters.py`.
- [x] **A4 Filter „Geschlechter-Mix" umbenennen, Option „ohne Personen" entfernen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Entscheidung 02.06.2026: Filter behalten, aber klarer benennen und die sachfremde Option entfernen.
   * Umsetzung (Commit 6ab0714): „Geschlechter-Mix" heißt jetzt „Geschlecht der Beteiligten". Die Option „ohne Personen" (die 53 Quellen ganz ohne annotierte Person) ist entfernt, weil sie keine Geschlechts-Aussage trifft. Vier Optionen (alle, mit Frauenbeteiligung, nur Frauen, nur Männer). Template plus `index.js` (Match, Zähler, Aktiv-Filter-Label). Guard in `test_index_filters.py`.
   * Verifikation: [Quellen-Liste, Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html).
- [x] **A5 Zeitraum-Histogramm zeigt zwei Tooltips gleichzeitig.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: Jeder Histogramm-Balken trug ein natives `title`-Attribut neben dem eigenen `data-hint` (hint.js), beim Drüberfahren überlagerten sich zwei Tooltips mit verschiedenen Zahlen.
   * Umsetzung (Commit 0ea9797, Rebuild 0f60729): Statt `title` wird nur noch `data-hint` mit der live gefilterten Zahl gesetzt, in `index.js` und `register.js`. Guards in `test_index_filters.py` und `test_register_js.py` (`bar.title not in src`).
   * Verifikation: [Quellen-Liste](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents.html), Zeitraum-Histogramm.

#### B) Faksimile-Viewer

- [x] **B2 Faksimile sitzt bei langem Regest zu weit unten.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: Die Synopse stellte Text und Faksimile als gleich hohe Grid-Spalten (`align-items: stretch`); bei langem Regest wurde das Panel sehr hoch und OpenSeadragon zentrierte das Bild weit unter dem Fold.
   * Umsetzung (Commit 7093051, Rebuild 50e0989): `.doc-facs-panel` ist jetzt `position: sticky` mit bildschirmrelativer Höhe statt grid-stretch; der Viewer bleibt beim Scrollen auf gleicher Höhe sichtbar. Guard `frontend/tests/test_facs_panel_sticky.py`.
   * Verifikation: [QGW Nr. 105](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/105.html) (langes Regest), [QGW Nr. 2](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/2.html) (kurzes Regest).
- [x] **B1 Vollbildansicht für den Viewer.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commit 7093051, Rebuild 50e0989): Eigener Vollbild-Button links von Zoom +/-, native Fullscreen-API auf das gesamte `.facs-viewer`-Element, damit Seiten-Navigation und Zoom auch im Vollbild bedienbar bleiben. ESC und erneuter Klick schließen, Tooltip wechselt. `:fullscreen`-CSS füllt den Bildschirm randlos. Guard `frontend/tests/test_facs_fullscreen.py`.
   * Verifikation: [QGW Nr. 2](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/2.html).
- [x] **B3 doc 105: „ihr" mit aufgelöstem Namen aus der Verknüpfung.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: „ihr" ist ein `<rs type="person" ref="#pe__gertrud...">`, der aufgelöste Name steckt im Hover-Tooltip, war aber nicht in der Annotationstabelle sichtbar.
   * Entscheidung 02.06.2026: Auflösung in der Annotationstabelle (Variante C), nicht im Fließtext. ID nur intern.
   * Umsetzung (Commits 267e787, 026daa0): Die „Genannt als"-Zelle zeigt den aufgelösten Registernamen als Hauptnamen und den Quell-Wortlaut kursiv in Klammern dahinter, also „Gertrude (ihr)" (Name aus dem `data-hint` des Spans). Die technische ID (`pe__`/`org__`) erscheint zusätzlich nur im internen Build (`data-audience="intern"`) oder mit `?dev=1`, öffentlich nicht. Geschlechtsspalte als Kurzform m/w wie Register und Korb. Guards in `test_anno_resolve.py`.
   * Verifikation: [QGW Nr. 105, Annotationen](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/105.html), Zeile „ihr".

#### C) Rollen-Labels (siehe „Rollen-Label-Wording und projektweite Gender-Regel" oben)

- [~] **C1 Rollen-Labels gendergerecht und konsistent über Profile, Sidebar, Tooltips.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Entscheidung 02.06.2026: durchgängig Sternform, Numerus kontextabhängig (Variante 2). witness immer „Zeug*innen / Siegler*innen" in Kategorie-Kontexten.
   * Umsetzung (Commit a91df57): Per-Person-Kontexte (Annotationstabelle, Profil, Register-Tabellen-Pille, Abfrage-Teilnehmer) Singular „Aussteller*in / Empfänger*in / Zeug*in / Siegler*in / Sonstige"; Kategorie-, Filter- und Aggregat-Kontexte (Register-Sidebar-Chips, Aktiv-Filter, Abfrage-Dropdowns, Rollen-Verteilung) Plural „Aussteller*innen / Empfänger*innen / Zeug*innen / Siegler*innen". Zweiter SSoT-Satz `ROLE_LABELS_PLURAL` in `frontend/role_labels.py`, Build-Chips ziehen daraus. Ersetzt die vier bisherigen uneinheitlichen Konventionen. Guards in `test_role_labels.py`, `test_register_js.py`.
   * Verifikation: [Personen-Register-Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html) (Plural-Chips), [QGW Nr. 1022 Annotationstabelle](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html) (Singular pro Person).
   * Offen: Sign-off. Die tiefere Code-Konsolidierung der Inline-Kopien auf eine einzige JS-SSoT bleibt der Refactor-Punkt unten.
- [x] **C2 Caveat zur Datenlage bei Zeuginnen und Sieglerinnen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Notiz: In den Daten sind Zeugen fast ausschließlich männlich. Das gendergerechte Plural-Label „Zeug*innen / Siegler*innen" benennt die Rolle, behauptet aber keine Geschlechterverteilung; die tatsächliche Verteilung bleibt über die Geschlechts-Filter und Aggregate sichtbar. Keine weitere Maßnahme.

#### D) Zitation und Zotero (siehe „Zitations-Button" oben)

- [x] **D1 Zotero einbinden.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Entscheidung 02.06.2026: wird nicht umgesetzt. Verworfen.
- [?] **D2 Zitation präzisieren. TODO Kund_innen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Der Zitations-Button funktioniert, die gewünschte Zitierform (Chicago, MLA, fußnotenbasiert) liefern die Projektpartner*innen. Ebenso liefern sie die noch ausstehenden Projekt-Texte (About, Glossar-Definitionen, Impressum), siehe Abschnitt „Projekt". Kein Frontend-Schritt offen, bis die Vorgaben kommen.

#### E) Datenkorb

- [x] **E1 Topbar-Badge entitätsweise aufschlüsseln, globaler Leeren-Button.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: Der Badge summierte alle Einträge zu einer Zahl (Beispiel 41 = 1 gesammelte Quelle plus 40 abgeleitete Personen), unklar was im Korb liegt.
   * Umsetzung (Commit ed6600c, Rebuild bc37157): Badge zeigt pro Entitätstyp eine farbige Pille (Quelle grün `--anno-place`, Person blau `--anno-person`, Organisation violett `--anno-org`), leere Typen ausgeblendet. Der Korb-Tooltip nutzt dieselbe Logik (Gesamtzahl pro Typ plus „Davon N abgeleitet"), Badge und Tooltip stimmen überein. Neuer globaler „Gesamten Datenkorb leeren"-Button im Korb-Header mit Sicherheitsabfrage, ausgeblendet bei leerem Korb. Dabei behobener Nebenbug: `.explore-btn` setzt `display: inline-flex` und schlug die UA-Regel `[hidden]{display:none}`, sodass der Button im leeren Korb sichtbar blieb; expliziter `[hidden]`-Reset ergänzt. Guards `test_basket_badge.py`, `test_basket_clear_all.py`.
   * Verifikation: [Datenkorb-Seite](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/korb.html). Eintrag auf einer Quellenseite hinzufügen, dann Nav-Badge und Korb-Header prüfen.
- [ ] **Korb-Tabellen-Konsistenz mit den Listen-Seiten.** (Herkunft: eigene Beobachtung 02.06.2026)
   * Befund: Die Korb-Seite rendert ihre drei Tabellen mit `aggregat-table` (Tabellenstil aus dem Analyse-/Explorationsbereich), während Quellen-Liste und Register die Listen mit `index-table` rendern (`register_list.html:106`). Die beiden Stil-Familien unterscheiden sich in Kopf, Zebra und Dichte. Da der Korb dieselben Entitäten listet wie die Register, wäre `index-table` konsistenter.
   * Offen: Entscheidung, ob die Korb-Tabellen auf `index-table` umgestellt werden; betrifft `frontend/templates/korb.html` und `basket-page.js`.

#### G) Freigabe-Entscheidung

- [?] **G1 Stadtbücher Bd. 1 aus der öffentlichen Sicht nur in den internen Bereich.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: Umsetzung wäre eine Zeile (Korpus aus `PUBLIC_CORPORA` in `frontend/config` entfernen, bleibt in `RELEASED_CORPORA`), öffentlicher Build zeigte dann nur noch QGW bis 1414.
   * Offen, zurückgestellt: Vom Nutzer am 02.06.2026 vorerst zurückgestellt („brauchen wir vorerst nicht").
- [?] **G2 Leitsatz „wir sammeln nur alles was wir haben" präzisieren.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Offen: Bedeutung und Konsequenz für die Darstellung noch zu klären.

#### H) Org-Register, Typ-Filter

- [x] **H1 Typ-Filter zeigt Rohcodes statt Labels.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Befund: `_type_chip_data` in `frontend/build/_pages.py` setzte `label = key` (Kloster_f, Spital_Siechenhaus, …); das Mapping `label_org_type` lag nur in den Profilen.
   * Umsetzung (Commit 0d8cb35, Rebuild 4b16f48): Helfer `_org_type_label` labelt Filter-Chips, Tabellenspalte, Datenkorb und Aktiv-Filter-Chip einheitlich (`tpl`-Feld in `_org_search_data`, gespiegelt in `register.js`). Guards in `test_register_pages.py`, `test_register_js.py`.
   * Verifikation: [Organisations-Register](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html).
- [x] **H2 OTHER ans Ende, als „Sonstige" anzeigen.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commit 0d8cb35): `_org_type_label` mappt OTHER auf „Sonstige", Sortierschlüssel zieht OTHER und leeren Wert ans Ende.
   * Verifikation: [Org-Register, Filter OTHER](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html?types=OTHER).
- [x] **H-Folge Org-Typ einheitlich normalisiert und Chips dynamisch sortiert.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Umsetzung (Commits ccbbf55 Normalisierung, Rebuild 26c1cc7; de7a954 dynamische Sortierung, Rebuild d138233): Tabellenspalte, Datenkorb und Aktiv-Filter-Chip zeigen jetzt überall das normalisierte Label statt des Rohcodes. Unter aktivem Filter sortieren sich die Typ-Chips dynamisch nach der live sichtbaren Zahl (Sammelposten OTHER/leer ans Ende), damit nicht eine kleinere Zahl über einer größeren steht.
- [x] **H3 Klassen-Label „Kloster (Frauenorden)" / „Kloster (Männerorden)" einheitlich.** (Herkunft: Stakeholder-Durchgang 02.06.2026)
   * Entscheidung 02.06.2026: durchgängig „Kloster (Frauenorden)", analog „Kloster (Männerorden)" bei Bedarf; kein plurales „Frauenklöster".
   * Befund: bereits erfüllt. `label_org_type` mappt `Kloster_f` → „Kloster (Frauenorden)" und `Kloster_m` → „Kloster (Männerorden)"; seit H1 zieht auch Liste/Filter/Datenkorb dieses Label über `tpl`. Kein „Frauenklöster"-String im Code.
   * Verifikation: [Org-Register, Typ-Filter](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html).
