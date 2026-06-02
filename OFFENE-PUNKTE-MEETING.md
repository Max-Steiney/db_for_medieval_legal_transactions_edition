# Offene Punkte (Meeting-Mitschrift)

Arbeitsstand des Stakeholder-Durchgangs am 02.06.2026.
Status je Punkt: [klar] sofort umsetzbar, [fix] Bug zu beheben,
[klären] braucht Entscheidung oder Detail, [editorisch] Schwester-Repo / Daten,
[erledigt] umgesetzt und committet.

Erledigt am 02.06.2026 (Block 1): A1, A2, A3, H1, H2 plus zwei Folgeschritte
beim Org-Typ (einheitliche Normalisierung ueber Tabelle/Datenkorb/Aktiv-Filter,
dynamische Chip-Sortierung nach Live-Zahl). Commits 8d90d9f, 0d8cb35, 4b16f48,
ccbbf55, 26c1cc7, de7a954, d138233. Offen bei H bleibt nur H3 (Wortwahl
Frauenkloester gegen Kloster (Frauenorden)).

## A) Quellen-Liste, Filter-Sidebar (documents.html)

- A1 [klar] Ort aus der Volltextsuche entfernen. Durchsucht bleiben
  Signatur, Datum, Regest. Signatur bleibt bewusst drin (Fundstelle aus
  Fußnote auffindbar).
- A2 [klar] Erschließungsform-Filter komplett entfernen
  (Regest/Siegel/Nota/ohne). Nur Sidebar, keine Tabellenspalte betroffen.
- A3 [klar] Faksimile-Filter komplett entfernen. Nur Sidebar.
- A4 [klären] Geschlechter-Mix. Notiz: "eher entfernen, verzerrend" plus
  "nur Personen (53) entfernen". Offen: ganzer Filter raus oder nur
  einzelne Optionen?
- A5 [fix] Zeitraum zeigt zwei Tooltips gleichzeitig. Ursache: jeder
  Histogramm-Balken trägt einen eigenen Hover-Hint, beim Drüberfahren
  überlagern sich zwei.

## B) Quellen-Detailseite und Faksimile-Viewer

- B1 [klären/feature] Vollbildansicht für den Viewer (Beispiel doc 2).
- B2 [fix] doc 105: Faksimile sitzt zu weit unten, Layout-Bug.
- B3 [klären] doc 105: "ihr" soll mit echtem Namen aus der Verknüpfung
  angezeigt werden; interne Version zusätzlich ID und Name. Offen, was
  genau annotiert ist.

## C) Register, Profile, Rollen-Labels

- C1 [editorisch/klar] Rollen-Labels gendergerecht formulieren, konsistent
  über Profile, Sidebar, Tooltips. Aktuell: Aussteller / Empfänger /
  Zeuge / Siegler / Sonstige.
- C2 [editorisch] Zeuginnen und Sieglerinnen: in den Daten sind Zeugen
  fast ausschließlich Männer und nur in wenigen Beständen vorhanden.
  Gendergerechtes Label darf nicht über die Datenlage hinwegtäuschen.

## H) Org-Register, Typ-Filter (orgs.html)

- H1 [klar] Typ-Filter zeigt Rohcodes statt Labels (Kloster_f,
  Spital_Siechenhaus, OTHER ...). Mapping label_org_type existiert in
  aggregator/_profile_labels.py, wird aber nur in den Profilen genutzt,
  nicht in der Liste (_type_chip_data in build/_pages.py setzt label = key).
  Fix: Mapping auch auf die Filter-Chips anwenden.
- H2 [klar] OTHER immer ans Ende sortieren und als "Sonstige" anzeigen,
  nicht nach Häufigkeit einsortiert.
- H3 [klären] Kloster_f als "Frauenklöster" gewünscht. Profil nutzt
  derzeit "Kloster (Frauenorden)". Offen: im Listen/Filter-Kontext ein
  plurales Klassen-Label (Frauenklöster, Spitäler) gegen das singularische
  Profil-Label.

## D) Zitation und Zotero

- D1 [klären/feature] Zotero einbinden über ein Tool. Offen: eingebettete
  Metadaten (COinS/unAPI für den Zotero-Connector) oder Export-Button.
- D2 [klären] Zitation: Detail kommt noch.

## E) Datenkorb

- E1 [klären] Datenkorb-Nummer: Notiz unvollständig, Detail kommt noch.

## F) Annotation und Datenkategorisierung (Schwester-Repo)

- F1 [editorisch] Stadtbuch 502: die Frau ist nicht als witness
  annotiert. Beispiel-Beleg im XML.
- F2 [editorisch] Kategorisierung in den Stadtbüchern muss nochmal
  geprüft werden (Rollen, Erschließung).

## G) Freigabe-Entscheidung

- G1 [klären/Entscheidung] Stadtbücher Bd. 1 (1395 bis 1400) aus der
  öffentlichen Sicht herausnehmen und nur in den internen Bereich geben,
  weil es noch Probleme in den Daten gibt. Umsetzung: Korpus aus
  PUBLIC_CORPORA entfernen (frontend/config), bleibt in RELEASED_CORPORA.
  Effekt: öffentlicher Build zeigt nur noch QGW bis 1414.
- G2 [klären] Leitsatz "wir sammeln nur alles was wir haben": Bedeutung
  und Konsequenz noch zu präzisieren.

## Offene Detail-Eingaben

A4, B1, B3, D1, D2, E1, G1, G2.
