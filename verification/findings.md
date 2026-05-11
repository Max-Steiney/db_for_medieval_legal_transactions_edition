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

### Filenames-Filter: `status="in progress"`

64 TEI-Quellen (14 QGW, 50 Stadtbuecher) haben in
`pipeline/output/filenames.csv` den Status `in progress` und werden vom
Build nicht zu HTML gerendert. `compare_tei_html.check_pair_coverage`
meldet das als `known_gap`. Wenn der Status auf `done` wechselt, wird
automatisch das HTML erzeugt und die Verifikation in den Pair-Vergleich
aufgenommen.

## Gelöste Befunde

(noch keine)
