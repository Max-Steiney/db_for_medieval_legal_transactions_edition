# **Frontend-Entwicklung — Projektstatus und Arbeitsstand**

**Prosopographische Datenbank mittelalterlicher Wiener Rechtsgeschäfte**
Christopher Pollin, Digital Humanities Craft OG

* v1. 11.05.2026 (**WORK IN PROGRESS**)
* AI-Unterstützung: Claude Opus 4.7, Claude Code

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

- **UI-Konsistenz**: Derselbe Begriff oder Feldname trägt im gesamten UI dasselbe Label. Liegt dieselbe Datenlogik in mehreren Ansichten (Profil-Header, Sidebar-Filter, Tooltip-Titel, Hilfe-Texte), muss das Label überall identisch sein. Verankert in [`CLAUDE.md`](CLAUDE.md) (Agent-Regeln, Bullet „Keine UI-Inkonsistenzen"), [`knowledge/ui-design.md`](knowledge/ui-design.md) (Abschnitt „Begriffs- und Label-Konsistenz") und Memory-Datei `feedback_ui_konsistenz.md`. Anlass: Belegt-Wording, das auf drei Stellen synchron gezogen werden musste.

## **Anforderungen und Umsetzung**

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
   * Befund: Header-Feld `Belegt` auf der Org-Profil-Seite, gerendert in `frontend/templates/org.html:94`. Wert ist min/max der ISO-Jahre aller Quellen, in denen die Org annotiert ist, berechnet in `frontend/aggregator/org_profiles.py:415,452`. Das Datum pro Quelle kommt aus dem teiHeader; die Pipeline arbeitet ein 8-Prioritäten-Lookup ab (`pipeline/utils/date_parser.py:103`). Im freigegebenen Korpus greifen davon nur drei Pfade: `date/@when` (Standardfall), `date/@from+@to` (Range, davon wird `from` genommen), `origin/@notAfter` (nur Subkorpus Satzbuch\_CD\_1448-60). `rs type="event"` trägt nie ein eigenes Datum, Events erben die Datierung der Quelle.
   * Problem: Das Label liest sich ontologisch als historische Existenz-Datierung der Institution. Tatsächlich ist es Editions-Datierung: in welchen Jahren existieren in dieser Edition Quellen, die die Org annotieren. Bei Orgs mit nur einer Quelle steht das nackte Jahr und wirkt wie ein Punkt-Datum. Knapp zwei Drittel aller Orgs haben nur eine Quelle.
   * Umsetzung: Label durch dynamisches `Datum der Quelle` (Singular bei einer Quelle) oder `Datum der Quellen` (Plural sonst) ersetzt. Spannen mit `bis` statt en-dash. Einheitlicher Tooltip ergänzt. Synchron umgesetzt auf Org-Profil (`frontend/templates/org.html`), Personen-Profil (`frontend/templates/person.html`) und Sidebar-Filter beider Register (`frontend/templates/register_list.html`, samt Korrektur des „je Person"-Bugs in Sub-Label und Histogramm-Hints des Org-Registers, plus „Aktivitätszeitraum" im Suche-Hilfe-Tooltip). 380 von 380 Tests grün.
   * Verifikation: [Burg Kufstein](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html) (eine Quelle, „Datum der Quelle 1397"), [Zwettl Zisterzienser](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__zwettl-zisterzienser.html) (zwei Quellen mit Lücke, „Datum der Quellen 1342 bis 1388"), [Wien St. Stephan](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__wien-st_stephan.html) (viele Quellen, breite Spanne), [Organisations-Register-Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs.html), [Personen-Register-Sidebar](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html).
   * Offen: Sign-off Stakeholder. Bei Einzelquelle (knapp zwei Drittel der Orgs) wurde bewusst kein expliziter „(1 Quelle)"-Hinweis ergänzt, da der Singular im Label und das Nachbarfeld `Quellen: 1` die Aussage tragen; falls dem Stakeholder das zu schwach ist, ist die Klammer-Ergänzung ein kleiner Folge-Eingriff.

- [?] **Relationale Tags sichtbar machen, wenn Organisationen innerhalb anderer Tags annotiert sind.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Reverse-Index liest sowohl `<rs type="org" ref="#org__...">` als auch `<roleName corresp="#org__...">` (`frontend/build/_helpers.py:132-153`), die Org-Profil-Seite findet die Quelle daher korrekt. Im gerenderten Quellen-HTML aber sammelt `frontend/static/js/document.js:100` für die Annotationen-Tabelle ausschließlich `.anno-person, .anno-org, .anno-place` und ignoriert `data-corresp^="org__"` auf `anno-attr-occ`- und `anno-attr-title_ref`-Spans. Resultat: die Org-Verweise sind im Body als Tooltip da, aber kein klickbarer Link und kein Tabellen-Eintrag.
   * Verifikation: [Burg Kufstein, Quellen-Block](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__kufstein-burg.html) zeigt Quelle 222 (StB I), [Stadtbuch-Eintrag 223a](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/Stadtbuecher/Band_1_1395-1400_ready/223a.html) zeigt Burg Kufstein nicht in der Annotationen-Tabelle, obwohl `#org__kufstein-burg` als `corresp` auf der `<roleName type="occ">phleger</roleName>` von Rudolf von Rosenhaim sitzt.
   * Offen: Soll der implizite Org-Verweis als klickbarer Link im Body gerendert werden, als zusätzlicher Zeilen-Typ in der Annotationen-Tabelle, oder beides. Selbe Frage für `title_ref`-Org-Bezüge.

- [?] **Person-IDs in der öffentlichen Ansicht ausblenden.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Technische IDs wie `org__kufstein-burg`, `pe__...` stehen prominent als `<code class="person-id">` in der Meta-Strip (`frontend/templates/org.html:107`, analog im Personen-Profil) und in jedem Annotations-Tooltip im Quellen-Body (`data-hint="Burg Kufstein [org__kufstein-burg]"`).
   * Offen: Komplett ausblenden, hinter Aufklapper/Detail verstecken oder nur in Tooltips entfernen. Bezug zur Zitierbarkeit ist zu klären.

- [?] **Formulierung „für" als Rollenbezeichnung ersetzen, sie ist irreführend.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Keine Stelle im Frontend-Code setzt explizit „für" als Label-String. Die Rollen-Vokabulare in Templates (`ROLE_LABEL` in `person.html:13`, `org.html:15`) und JS (`document.js`) verwenden „Aussteller\*in", „Empfänger\*in", „Zeuge / Siegler\*in", „Sonstige". Plausibler Kandidat ist die `anno-attr-rep`-Annotation (Stellvertretung), in der das TEI-Wort „für" als Rolle markiert wird, siehe Beispiel [QGW Vienna 1051](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1051.html) („für" als Span mit `data-hint-type="Stellvertretung"`).
   * Offen: Bestätigung durch Stakeholder, wo genau im UI „für" als Rolle erscheint. Idealerweise Screenshot. Wenn es der `anno-attr-rep`-Fall ist, müsste der Anzeige-Text zur Rolle in der Annotationen-Tabelle gehoben werden (statt das TEI-Wort), nicht das Wort im Quellentext geändert.

- [?] **Kategorie „im Quellen-Wortlaut" vereinheitlichen.** (Herkunft: Stakeholder-Review 11.05.2026)
   * Befund: Identisches Label „Im Quellen-Wortlaut:" auf beiden Profil-Sub-Headern (`frontend/templates/org.html:66` und `frontend/templates/person.html:97`). Backing-Felder unterscheiden sich: Org rendert `profile.name_orig` (Roh-Wortlaut aus den Org-Stammdaten), Person rendert `profile.name_orig_display` (aufbereiteter Display-String, siehe `frontend/aggregator/person_profiles.py:53,128`). Die wahrscheinliche Uneinheitlichkeit liegt nicht im Label, sondern im dahinterliegenden Wert: bei Personen wird auf `_orig` zurückgefallen, wenn `_reg` leer ist (Fallback-Logik), sodass „im Quellen-Wortlaut" gelegentlich nur die Normalform wiederholt.
   * Offen: Klären, ob der Stakeholder die Wert-Aufbereitung meint oder das Label selbst. Wenn Wert: konsistente Behandlung Org vs Person (kein Fallback, oder Fallback auf beiden Seiten, oder Sub-Label-Hinweis).

### **Analyse**

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
   * Verifikation 2: [Org-Profil St. Stephan, Block „Personen mit Tätigkeitsverbindung"](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__wien-st_stephan.html#tatigkeit)
      * Befund: Angezeigt sind 113 Personen mit Tätigkeitsbezeichnungen bei St. Stephan, Anzahl der Belege und eine Spalte mit 1-Hop-Verwandtschafts-Beziehungen aus dem Quellenkorpus.
      * Offen: Die konkreten Namen der Verwandten hinter der kin-Zahl. Grund: das Aggregat führt die Anzahl, aber nicht die aufgelösten Personen mit. Sinnvoll wäre eine Tooltip- oder Popover-Auflösung; kleiner Eingriff im Aggregator plus Markup.

- [x] **Gib mir alle Personen/Organisationen, die durch ein Issuer-Recipient-Verhältnis mit St. Agnes auf der Himmelpforte verbunden sind.** (Herkunft: Stakeholder-Anfrage)
   * Verifikation 1: [Abfrage-Interface, Person Issuer plus Agnes Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#p1=r=issuer&g1=r=recipient,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien). Angezeigt sind Events, in denen eine beliebige Person als Ausstellerin und St. Agnes als Empfängerin auftritt.
   * Verifikation 2: [Abfrage-Interface, Gegenrichtung Agnes Issuer plus Person Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#g1=r=issuer,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien&p1=r=recipient). Angezeigt sind Events, in denen St. Agnes ausstellt und eine Person empfängt.
   * Verifikation 3: [Abfrage-Interface, Org-Org-Konstellation mit Agnes als Recipient](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/analysis/index.html#g1=r=issuer&g2=r=recipient,n=St.%20Agnes%20\(auf%20der%20Himmelpforte\)%20Wien). Angezeigt sind Events, in denen eine andere Organisation ausstellt und St. Agnes empfängt.

### **Exploration**

- [ ] **Zeitstrom** (Herkunft: eigene Beobachtung)
- [ ] **Personennetzwerk** (Herkunft: eigene Beobachtung)
- [ ] **…**

### **Projekt**

**Aktuell sind hier nur Platzhalter.** Schickt mir bitte alle diese Texte. Sie liegen dann als .md-Dateien im Repository und können dort bearbeitet werden. Anschließend werden sie als HTML angezeigt.

- [ ] **Projekt** (Herkunft: eigene Beobachtung)
   * Bearbeiten: [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition/edit/main/frontend/content/project/about.md](https://github.com/chpollin/db_for_medieval_legal_transactions_edition/edit/main/frontend/content/project/about.md)
   * Ansehen: \<PAGES\_BASE\>/project/about.html
   * Offen: Inhalt liefern (Projektbeschreibung, Forschungskontext, Forschungsfragen, technische Umsetzung, …)
- [ ] **Annotationsrichtlinien** (Herkunft: eigene Beobachtung)
   * Bearbeiten (kanonische Quelle, Schwester-Repo): [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions/edit/main/edition\_guidelines.md](https://github.com/chpollin/db_for_medieval_legal_transactions/edit/main/edition_guidelines.md)
   * Ansehen: \<PAGES\_BASE\>/project/edition-guidelines.html
   * Hinweis: Dieselbe Quelle, die das Datenmodell mit RelaxNG definiert. Die Datei lebt im Daten-Repo. Der Build dieses Frontends synchronisiert sie automatisch, wenn sie sich geändert hat. Lokale Arbeitskopie im Frontend (nicht bearbeiten) liegt unter `frontend/content/project/edition-guidelines.md`.
- [ ] **Glossar** (Herkunft: eigene Beobachtung)
   * Bearbeiten: [https://github.com/chpollin/db\_for\_medieval\_legal\_transactions\_edition/edit/main/frontend/content/project/glossar.md](https://github.com/chpollin/db_for_medieval_legal_transactions_edition/edit/main/frontend/content/project/glossar.md)
   * Ansehen: \<PAGES\_BASE\>/project/glossary.html
   * Offen: Inhalt liefern (Begriffe der Datenbank: Quellenkorpus, Quelle, Event, Rechtsgeschäft, etc.).
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
   * Umsetzung (commit c0454a27df):
      * Redundante „Ereignisse"-Untertabelle entfernt; Entitäten nach Top-Level-Event gruppiert; Gruppen-Header zeigt den Dispositiv-Verb-Wortlaut der Quelle (kursiv, Trigger-Farbe) plus rohe `ev__`-ID als Anker. Nested events (Erwähnungen in der Narrative) sind ausgeblendet, ihre Entitäten wandern in die Eltern-Gruppe.
      * Spalten umbenannt: „Entität" → „Genannt als", „Rolle" → „Funktionsrolle". Spalte „Abschnitt" entfernt (Info bleibt im Row-Tooltip). Neue Spalte „Geschlecht" mit m/w/—-Glyph (Daten über `data-sex` auf `rs[@type=person]`).
      * Spalten-Header-Tooltips mit Ein-Satz-Definition pro Kategorie.
      * xml:id aus den Zellen entfernt (lebt nur im Row-Tooltip), Padding angehoben, gruppen-aware Sortierung.
   * Verifikation: [QGW Vienna Nr. 1022](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1022.html) (Mehrfach-Event-Worst-Case), [QGW Vienna Nr. 23](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/23.html) (Einfach-Event-Fall).
   * Offen (geparkt): Disp-Verb-/Event-ID-Politur — die rohen `ev__…`-IDs als sprechende Namen, eine spätere Evaluierungs-Runde.
   * Offen (Backlog): Type-Pillen pro Wert in der „Attribute"-Spalte; kleine „erwähnt"-Pille auf Zeilen, die nur aus eingebetteten Ereignissen stammen; analoge Event-Gruppierung der Tabellen „Dispositivformeln" und „Editorische Ergänzungen".

### **Sonstiges und Daten**

- [ ] **Texte auf Startseite** (Herkunft: eigene Beobachtung)
- [x] **Hover-Tooltips für alle Annotations-Typen im Quellentext** (Herkunft: eigene Beobachtung)
   * Umsetzung: Vorher hatten nur `rs[@type='person|org|place']` einen `data-hint` mit Type-Label. Triggerstrings (Dispositivformeln und Funktionsrollen-Verben), `roleName`-Attribute (alle Subtypen wie Verwandtschaft, Titel, Beruf, Stellvertretung etc.) und `add` (editorische Ergänzungen) tragen jetzt ebenfalls einheitliches `data-hint` plus `data-hint-type`. Coverage in QGW Nr. 1022 stieg von 13/40 auf 32/40 Annotationen mit Tooltip (commit c0454a27df).
- [x] **Einheitlicher Tooltip-Look projektweit** (Herkunft: eigene Beobachtung)
   * Umsetzung: Native `title="..."`-Tooltips (Browser-Default) durchgehend auf das projekteigene `data-hint`-System mit `hint.js` migriert. Betrifft Facsimile-Buttons, Exploration-Chips, Korpus-Sidebar-Chips, Cite-Copy-Buttons, Sparkline-Bars und Decade-Säulen im Zeitstrom, Geschlechtsbars im Aggregat, Network-Recenter-Buttons (commit c0454a27df).
- [ ] **Glossar-Tooltips und Datenpunkt-Provenance** (Herkunft: eigene Beobachtung)
   * Offen: Glossar-Texte als `tip_glossary`-Popover an UI-Stellen einsetzen, an denen Fachbegriffe stehen (Quellenkorpus, Event, Rechtsgeschäft, Regest etc.). Eigene Tooltip-Form, neben dem Hover-Hint-System.
   * Offen: Datenpunkt-Provenance-Popover an Zahlen auf der Startseite und in Aggregat-Quadranten (zeigt, woher die Zahl kommt).
- [ ] **Datenkorb** (Herkunft: eigene Beobachtung)
- [~] **Es muss möglich sein, anzeigen zu lassen, welche Personen in einem bestimmten Band der QGW vorkommen.** (Herkunft: Stakeholder-Anfrage)
   * Befund: Personen- und Organisations-Register tragen in der Sidebar einen Korpus-Filter (`frontend/templates/register_list.html:30`, `sidebar_corpus_chips`), Mehrfachauswahl möglich. Im freigegebenen Korpus existiert bisher nur ein QGW-Band (`QGW/Vienna_1177-1414_ready`), daher entspricht „in bestimmtem Band" aktuell genau dem QGW-Chip. Verifikation: [Personen-Register, Sidebar-Bestandsfilter](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons.html).
   * Offen: Sign-off Stakeholder, ob das Band-Konzept hinreichend abgedeckt ist. Bei künftiger Freigabe weiterer QGW-Bände wird der Filter automatisch um den jeweiligen Chip ergänzt.
- [ ] **Konsistenz-Ziel erreichen. Alle Zahlen im Interface stimmen mit den überprüften Korpora im Git-Repository überein. DB-Datenqualität hat Vorrang, Frontend-Korrekturen folgen der DB.** (Herkunft: eigene Beobachtung)
- [ ] **Farben und Schriften** (Herkunft: eigene Beobachtung)
- [x] **Kategorie „Tod" in „als verstorben genannt" umbenennen.** (Herkunft: Stakeholder-Review)
   * Verifikation: [pe\_\_christian\_von\_strass\_StB\_I\_624](https://chpollin.github.io/db_for_medieval_legal_transactions_edition/register/persons/pe__christian_von_strass_StB_I_624.html)
