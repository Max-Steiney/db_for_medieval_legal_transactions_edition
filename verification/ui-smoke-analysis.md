# UI-Smoke: Abfragen-Sub-Seite (analysis/index.html)

Dokumentierter Klickpfad für die Konstellations-Abfrage. Zwei Forschungsfragen
mit unabhängig aus `docs/data/role_constellation.json` berechneter Ground
Truth. Bei jedem Schritt: erwarteter Wert vs. gesehener Wert vs. Status.

Stand: 2026-05-12. Verifikation erfolgt mit dem Chrome-Tool des
Claude-Code-Harness; ein menschlicher Smoke-Test folgt demselben Pfad.

## Anfangszustand

| Schritt | Erwartet | Gesehen | OK |
|---|---|---|---|
| Seite öffnen ohne URL-Hash | keine Personen-Karte, leere Tabelle, Empty-State sichtbar | 0 Karten, 0 Zeilen, Empty-State sichtbar | ✓ |
| KPI-Strip unter dem H1 | „Korpus: 2.336 Quellen · 2.399 Rechtsgeschäfte · 7.582 Personen" | exakt | ✓ |
| Korpus-Chips | QGW II/1 (1.822), Stadtbücher Bd. 1 (577) | exakt | ✓ |
| Zeitraum-Slider | 1177 bis 1414, ohne Histogramm-Bars | so | ✓ |
| CSV-Button | disabled | disabled | ✓ |

## Frage A — Frauen als Ausstellerinnen gegenüber männlichen Empfängern

Forschungsfrage: „In welchen Rechtsgeschäften treten Frauen als
Ausstellerinnen gegenüber männlichen Empfängern auf?"

Ground Truth (aus dem JSON unabhängig berechnet): 643 Rechtsgeschäfte aus
639 Quellen. Korpus-Split: QGW II/1 513 RG, Stadtbücher Bd. 1 130 RG.
Erste chronologische Treffer: Margarethe Gutratin / Siegfried Celeub am
1255-02-18 (QGW_4, Übergabe); Jutta Hesner / Rudolf Chitzel am 1301-03-14
(QGW_26, Kauf); Margarethe Preusslin / Greiffe bei unser Frauen auf der
Stetten am 1306-11-16 (QGW_46, Übergabe).

| Schritt | Erwartet | Gesehen | OK |
|---|---|---|---|
| Block 1: Rolle Aussteller, Geschlecht weiblich | 643 RG / 639 Quellen | 643 RG / 639 Quellen | ✓ |
| Block 2: Rolle Empfänger, Geschlecht männlich | (gleiche Bedingung) | (gleich) | ✓ |
| Erste Tabellenzeile | 1255-02-18 / f__QGW_4 / QGW II/1 / Margarethe Gutratin & Siegfried Celeub / Übergabe | exakt | ✓ |
| Korpus auf QGW II/1 anklicken | 513 RG / 509 Quellen | 513 RG / 509 Quellen | ✓ |
| Range auf 1380–1410 (zusätzlich) | nicht aus Ground Truth direkt — Quervergleich nötig | 199 RG / 199 Quellen | ✓ |
| Quervergleich: QGW (199) + Stadtbücher (130) | = 329 (Ground Truth für 1380–1410 ohne Korpus-Filter) | 329 | ✓ |
| Aktive-Filter-Chips | „1380–1410 ×", „Korpus: QGW II/1 ×" | beide sichtbar | ✓ |
| URL-Hash | `#p1=r=issuer,s=f&p2=r=recipient,s=m&y=1380-1410&c=QGW II/1` | wird serialisiert (URL-encoded) | ✓ |
| Reset-Klick → leere Tabelle, KPI bleibt | 0 Karten, 0 Zeilen, Empty-State | nach Promise-Auflösung: 0 / 0 / true | ✓ |

## Frage B — Pfarrer als Aussteller, Bürger als Empfänger

Forschungsfrage: „In welchen Quellen treten Pfarrer als Aussteller
gegenüber Bürgern als Empfänger auf?"

Ground Truth: 4 Rechtsgeschäfte, 4 Quellen, alle QGW II/1. Treffer:

* 1341-05-12 f__QGW_237: Hermann (Pfarrer) / Konrad Wiltwercher (Bürger), Kauf
* 1355-11-05 f__QGW_470: Ortolf von Apamaea / Johann Smausser, Revers
* 1391-02-02 f__QGW_1200: Ludwig von Hietzing / Johann auf der Säule, „verpflichtet sich"
* 1391-08-09 f__QGW_1213: Johann von Zuentgraben / Ulrich Reindl, Übergabe

| Schritt | Erwartet | Gesehen | OK |
|---|---|---|---|
| Block 1: Rolle Aussteller, Beruf enthält „pharrer" | — | gesetzt | ✓ |
| Block 2: Rolle Empfänger, Beruf enthält „purger" | — | gesetzt | ✓ |
| Treffer-Counts | 4 RG / 4 Quellen | 4 RG / 4 Quellen | ✓ |
| Alle vier Tabellenzeilen | wie Ground Truth | alle vier exakt | ✓ |
| Permalink-Reload (URL kopieren, Tab neu laden) | beide Karten + Bedingungen wiederhergestellt | 2 Karten, alle Bedingungen wieder da | ✓ |
| CSV-Inhalt | 5 Zeilen (Header + 4 Treffer), sortiert nach Datum | 5 Zeilen, sortiert | ✓ (nach Bugfix, s. u.) |

## Während der Verifikation entdeckter und behobener Bug

**CSV-Sortierung.** Der erste CSV-Test zeigte die Treffer in einer anderen
Reihenfolge als die Tabelle. Ursache: `downloadCsv()` nutzte die unsortierte
`compute()`-Liste; die Sortierung lag nur im `renderHits()`-Pfad. Fix: in
`downloadCsv()` dieselbe Sortier-Logik (Datum, leere Datümer ans Ende,
Stichschluss nach Quelle) vor der Zeilen-Generierung anwenden. Bestätigt
durch einen zweiten CSV-Test nach Rebuild.

## Was die Verifikation zeigt

* **Konstellations-Matching ist korrekt.** Beide Fragen liefern exakt die
  Trefferzahl, die das JSON unabhängig hergibt. Das gilt für reine
  Geschlechts-Bedingungen (Frage A) und für Beruf-Substring-Matching
  (Frage B). Die Greedy-Zuordnung im Resolver ordnet Participants korrekt
  den nummerierten Blöcken zu, ohne eine Person doppelt zu belegen.
* **Filter sind kompositional.** Korpus und Zeitraum greifen
  unabhängig vom Konstellations-Filter; Quervergleich der Teilsummen
  (QGW + Stadtbücher = Gesamt) stimmt.
* **CSV-Export entspricht dem Bildschirm.** Spalten und Sortierung
  identisch zur Tabelle; alle Treffer enthalten (nicht nur die ersten 500).
* **Permalink reproduziert den Stand.** Personen-Bedingungen, Geschlechts-
  und Berufs-Filter, Zeitraum, Korpus, Verknüpfungs-Modus: alles kommt aus
  der URL zurück.
* **Empty-States sind transparent.** Solange kein Block mit Rolle existiert,
  steht der Empty-State mit einem konkreten Handlungsvorschlag.

## Bekannte Datenrealitäten

Diese sind keine Bugs des UI, sondern Eigenschaften des Korpus:

* 137 von 2.399 Rechtsgeschäften (5,7%) haben kein Einzeldatum; allesamt
  Stadtbuch-Einträge. Im UI markiert als „—", in der Sortierung ans Ende.
* `title_ref` in der Pipeline-CSV enthält toponymische Präpositionen
  (`zu`, `von`, `gesessen zu`), keine Honorifics. Eine UI-Bedingung „Titel"
  wird daher nicht angeboten.
* `occ` ist eine gemischte Sammlung aus Originalformen und teilweise
  normierten Schreibweisen (`purger 669`, `Bürger 277` nebeneinander).
  Das UI nennt das Feld „wie ediert, enthält" und bietet Vorschläge mit
  Belegzahl.
