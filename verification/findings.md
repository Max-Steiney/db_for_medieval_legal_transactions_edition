# Befunde

Reale Drift-Befunde aus den Verifikationsläufen, die nicht im Edition-Repo
gefixt werden können (TEI-Quellfehler, Sonderkonventionen). Liste wird bei
jedem neuen Befund ergänzt; gelöste Befunde werden nicht gelöscht, sondern
mit Lösungs-Commit markiert.

## Aktive Befunde

### TEI-Quelldaten: Klammer-Anomalien im Datums-Text (Stadtbuecher Band 1)

Stand: 2026-05-11
Status: offen
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`

Drei Stadtbücher-Quellen haben im `<profileDesc/creation/date>`-Text-Inhalt
syntaktisch defekte Klammer-Patterns:

| file_key | TEI-Text | Anomalie |
|---|---|---|
| Stadtbuecher_Band_1_1395-1400_ready_190 | `1397 Oktober ISa)` | schließende Klammer ohne öffnende |
| Stadtbuecher_Band_1_1395-1400_ready_265 | `1398 Mai 7 a )` | schließende Klammer ohne öffnende, plus stray `a` |
| Stadtbuecher_Band_1_1395-1400_ready_32  | `1396 Januar 20"`  | doppelte Anführungsstriche im Datums-Text |

Aufdecker: `python -m verification.run --tei-html`, Check
`teihtml.date_display_vs_tei`.

Effekt: HTML rendert den korrigierten Wert (Renderer normalisiert die
Anzeige), aber der TEI-Text bleibt asymmetrisch. Cross-Verifikation
schlägt fehl. Fix gehört in die jeweiligen `<date>`-Elemente im
Schwester-Repo.

### TEI-Quelldaten: kaputter Edit-Marker im Datums-Text (Stadtbuch 333)

Stand: 2026-05-11
Status: offen
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`

`Stadtbuecher_Band_1_1395-1400_ready_333` hat im `<date>`-Element den
Inhalt `(1398 Dezember 10 ?a»` — eine geöffnete, nie geschlossene Klammer
mit einem unklaren Edit-Marker `?a»` am Ende. Vermutlich wollte der
Bearbeiter einen redaktionellen Hinweis hinterlassen ("fraglich a") und
hat das Schließen der Klammer vergessen.

Pfad in der TEI: `sources/Stadtbuecher/Band_1_1395-1400_ready/done/333.xml`,
Element `<tei:profileDesc/tei:creation/tei:date>`.

Aufdecker: `python -m verification.run --tei-html`, Check
`teihtml.date_display_html_missing`. Der Reader kann die Datums-Anzeige
aus dem HTML-Titel nicht extrahieren, weil die schließende Klammer fehlt
und damit kein parenthetisches Datums-Pattern matched.

Fix: `<date when="1398-12-10">(1398 Dezember 10)</date>` (oder mit
explizitem Editions-Hinweis statt `?a»`). Gehört ins Schwester-Repo.

### TEI-Annotation: Sigillanten-Rolle fehlt bei Bischofssammelindulgenzen

Stand: 2026-05-11
Status: offen
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`,
inhaltliche Entscheidung der Editorinnen

Beispiel: QGW_II_I_24 (1298 II 20, Rom). Die `<physDesc/sealDesc>`
beschreibt zwölf an Seidenfäden anhängende Wachssiegel plus ein
eingeschaltetes Pergamentsiegel. Die vierzehn Bischöfe im Regest sind
ausschließlich als `<rs type="fn" role="issuer">` annotiert, nicht
zusätzlich als `sealer or witness`. Die Sigillanten-Eigenschaft (im
Original durch die Wachssiegel physisch belegt) wird damit nicht
auswertbar.

Das kontrollierte Rollenvokabular der Annotationsrichtlinien
(`issuer`, `recipient`, `sealer or witness`, `other`, `none`) erlaubt
Mehrfach-Rollen über separate `<rs type="fn">`-Wrapper. Eine
Nachannotation müsste das Pattern systematisch im Stand QGW II/1 und
II/2 prüfen — nicht nur Nr. 24.

Aufdecker: Sichtprüfung Nr. 24 im Rahmen der UI-Korrekturen
2026-05-11.

### TEI-Annotation: Bischof Albrecht von Passau ohne Person-Annotation

Stand: 2026-05-11
Status: offen
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`

In QGW_II_I_24 nennt die `<physDesc/sealDesc>`: "nach dem dritten Siegel
ist das des Bischofs Albrecht von Passau (an Pergamentstreifen
anhangend, ungefärbtes Wachs, Bruchstück) eingeschaltet." Diese
fünfzehnte Person ist mit eigener physischer Beleg-Spur am Stück
vorhanden, aber weder in `personList.xml` registriert noch im Regest
als `<rs type="person">` annotiert. Im UI steht "14 Pers., 1 Org."
statt der korrekten 15.

Fix: neuer Personen-Eintrag `pe__albrecht_von_passau_QGW_II_I_24` (oder
sprechender) in `personList.xml`, Annotation `<rs type="person" …>`
mit `role="sealer or witness"` an passender Stelle der
Siegelbeschreibung.

### Register-Konvention: ID-Renaming-Pass unvollständig

Stand: 2026-05-11
Status: offen, projektweit
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`

In `indices/personList.xml` tragen viele Einträge XML-Kommentare mit
einer "sprechenden" Ziel-ID, die tatsächliche `xml:id` folgt aber
weiter dem laufnummernbasierten Schema. Beispiel QGW_II_I_24:

| tatsächliche ID | gewünschte ID (Kommentar) |
|---|---|
| `pe__philipp_QGW_II_I_24` | `pe__philipp_von_salerno` |
| `pe__lambert_QGW_II_I_24` | `pe__lambert_von_aquino` |
| `pe__leonardo_patrasso_QGW_II_I_24` | `pe__leonhard_patrasso` |
| (mindestens 8 weitere bei Nr. 24) | |

Konsequenz: zwei Konventionen existieren parallel; sprechende IDs in
den Kommentaren sind als technische Schulden lesbar. Eine Mass-
Migration müsste alle Quellen-XMLs gleichzeitig aktualisieren
(Stadtbücher und QGW), inklusive `ref=`-Verweise. Das ist ein
projektweiter Auftrag, der bewusst aufgeschoben ist.

### TEI-Annotation: Datierungs-Personen (Päpste, Kaiser) unklare Konvention

Stand: 2026-05-11
Status: offen, konzeptionell
Verantwortlich: Schwester-Repo `db_for_medieval_legal_transactions`,
Klärung in den Annotationsrichtlinien

In QGW_II_I_24 steht im `<origDate>` der Wortlaut "pont. domini
Bonifatii pape anno quarto" — Bonifaz VIII. wird als Datierungs-Anker
genannt, aber nicht als `<rs type="person">` annotiert. Konsistente
Konvention ist unklar:

- In den meisten Quellen steht der Papst/Kaiser im `<origDate>`-Text-
  Inhalt, kein Annotationsziel.
- Falls eine Querverbindung gewünscht ist (Quellen, die unter Bonifaz
  VIII. ausgestellt wurden), bräuchte es eine projektweite Regel zur
  Datierungs-Person.

Vor einer technischen Lösung muss die Editionsrichtlinie diese
Konvention festlegen.

## Coverage-Lücken und Konventionen (kein Bug)

### TEI-Konvention: `<rs type="event" ref="NULL">`

119 Quellen verwenden `ref="NULL"` für Events ohne stabilen Identifier
(z. B. unbenannte Anschluss-Geschäfte). Der Frontend-Renderer filtert
diese Fälle korrekt. Die Verifikation zählt sie nicht als Drift —
`compare_tei_html.check_event_refs` filtert `NULL` explizit raus.

### Stadtbuecher-Konvention: Datum in Klammern

Stadtbuecher-TEI setzt Datumsangaben oft in runde oder eckige Klammern
(`(1397 Mai 22, Klosterneuburg)`), das Frontend rendert sie ohne. Die
Vergleichs-Normalisierung in `compare_tei_html._normalize_date` strippt
äußere Klammern. Konvention dokumentiert, kein Drift.

### Stadtbuecher-Konvention: Buchungs- vs. Ausstellungsdatum

Stadtbuecher-TEI hat Pattern `Eintragsdatum (Originaldatum)` —
das Frontend rendert nur das Originaldatum. Die Vergleichs-Funktion
`compare_tei_html._dates_equivalent` akzeptiert das.

### Heirat: Begriff nicht typisiert, Substring-Match provisorisch

Die freien Verwandtschaftsbezeichnungen in `kin_relations_in_sources.csv`
(Spalte `kin`) führen Heirats-Verhältnisse als deutsche Begriffe
(`gemahl`, `gemahlin`, `gatte`, `hausfrau`, `ehefrau` und Schreibvarianten),
ohne typisierende Spalte. `verification/research_questions.py` und
`frontend/aggregator/research_questions.py` markieren ein kin-Verhältnis
als Heirat per Substring-Match auf einer im Code stehenden Begriffs-Liste.

Die beiden Aggregat-Implementierungen kommen auf unterschiedliche Zahlen
für Uhlirz-IV-Heiratspaare (9 vs. 12), weil sie zwei unterschiedliche
Match-Verfahren nutzen (Token-Split gegen freies Substring). Beides ist
provisorisch.

Methodisch saubere Auflösung: eine Klassifikations-Spalte `is_marriage`
in `normalisation_lists/kin_norm_matching.csv` im Pipeline-Repo (analog
zu `Gewerbe_nach_Uhlirz_GstW` in `roleName_norm_matching.csv`). Bis
dahin zählt jeder im Frontend ausgewiesene Heirats-Befund als
„provisorisch, Substring-basiert".

### Wachsgießer-Heirats-Frage: Datengrundlage in allen Stufen knapp

Stand: 2026-05-17
Status: offen, langfristig

Auch in Stufe 4 (alle TEI-Subkorpora) trägt die Uhlirz-Kategorie IV
(Erzeugung und Vertrieb von Leuchtstoffen, Fetten und Ölen) im Aggregat
nur eine Person. Das `roleName_norm_matching.csv` hat das Mapping
(`kerzenmacher`, `cherczenmacher`, `öler` etc.), aber die TEI-Quellen
tragen diese Berufsbezeichnungen kaum in `<occupation>`-Elementen.
Konsequenz: Mail-Frage 1 (Heirats-Konstellationen unter Wachsgießern)
lässt sich nicht aus dem aktuell annotierten Bestand beantworten,
unabhängig vom Aggregator-Pfad. Die Beantwortung wartet auf weiteres
TEI-Material oder auf editorische Nachannotation in den bestehenden
Quellen.

### Filenames-Filter: `status="in progress"`

64 TEI-Quellen (14 QGW, 50 Stadtbuecher) haben in
`pipeline/output/filenames.csv` den Status `in progress` und werden vom
Build nicht zu HTML gerendert. `compare_tei_html.check_pair_coverage`
meldet das als `known_gap`. Wenn der Status auf `done` wechselt, wird
automatisch das HTML erzeugt und die Verifikation in den Pair-Vergleich
aufgenommen.

## Gelöste Befunde

### Renderer-Whitespace zwischen Attribut-Span und Forename

Gelöst: 2026-05-11
Aufdecker: Sichtprüfung Nr. 24 (Bischofssammelindulgenz, 14 Aussteller)

Im TEI-Quelltext stand das Forename direkt nach `</roleName>` (oder
nach zwei aufeinanderfolgenden `<roleName>`-Geschwistern) ohne
trennendes Leerzeichen. Der Renderer übernahm den Whitespace 1:1, was
zu Plain-Text-Output wie `episcopusAdam Marturanensis` und
`fraterepiscopus Johannes Turritanus` führte. Im Regest-HTML lasen sich
sieben Vorkommen aus Nr. 24 fehlerhaft.

Fix: defensiver Whitespace-Patch in
`frontend/renderer.py::_render_children`. Zwischen `<roleName>`/`<add>`
und einem unmittelbar folgenden Buchstaben/Ziffer (im Tail-Text oder im
Text des nächsten Geschwister-Elements) wird ein Leerzeichen injiziert.
Punktuation und vorhandenes Whitespace bleiben unangetastet.

Regression-Guard: `verification.compare_tei_html.check_glued_attributes`
(`teihtml.attr_name_glued`). Sucht das Pattern
`<span class="anno-attr…">…</span>[A-Z…]` und meldet Mismatch bei
Vorkommen. Lauf 2026-05-11: 0 Vorkommen über alle 2601 Quellen.

Tests: `frontend/tests/test_renderer.py`,
`test_rolename_glued_forename_gets_space`,
`test_rolename_followed_by_comma_no_extra_space`,
`test_rolename_preexisting_space_not_doubled`,
`test_add_glued_to_following_text`,
`test_two_adjacent_rolenames_get_space`,
`test_sibling_with_comma_text_no_space`.
