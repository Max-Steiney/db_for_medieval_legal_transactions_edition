# Analyse

Wissensdokument zum Analysebereich der Edition. Der Analysebereich ist der klassische Abfragemodus, der Nutzerinnen mit einer konkreten Forschungsfrage über vordefinierte Template-Familien direkten Zugriff auf wiederkehrende Kombinationen aus Rolle, Geschlecht, Bestand und Zeitraum gibt. Er steht als zweiter Zweig neben der [[exploration]], bedient aber ein entgegengesetztes Interaktionsmuster.

Deployment als statisches Frontend auf GitHub Pages, auf Basis der vorhandenen JSON-Datengrundlage.

**Stand der quantitativen Eckdaten:** Die Zahlen in diesem Dokument (Gesamtzahlen der Quellen, Personen, Events und Coverage-Werte) beziehen sich auf den Datenstand beim Schreiben der Blaupause. Sie dienen der Dimensionierung der Architektur, nicht als laufend aktualisierte Referenz. Der jeweils aktuelle Stand lebt im Footer der Edition sowie in den aggregierten JSONs unter `/data/`. Abweichung dieses Dokuments von den laufenden Zahlen ist beabsichtigt und kein Fehler.

## 1. Zielsetzung

Der Analysebereich soll Nutzern erlauben, konkrete inhaltliche Fragen an die Sammlung zu stellen, ohne SQL, SPARQL oder vergleichbare Query-Sprachen lernen zu müssen. Statt beliebiger Abfragen werden vorgefertigte Fragetypen angeboten, die der Nutzer über typisierte Slots anpasst. Das konzeptionelle Vorbild ist die komponierbare Logik von Scratch, übersetzt in ein domänenspezifisches Vokabular für Urkundenforschung.

Typische Beispielfragen, die das Interface beantworten soll:

- Wie viele geistliche Einrichtungen sind in der Sammlung belegt?
- Wie verteilen sich die Beteiligten an Rechtsgeschäften nach Geschlecht?
- Welche Rechtsgeschäftstypen treten in welchem Zeitraum auf?
- In welchen Rollen treten Frauen in Stadtbüchern auf?

## 2. Datenbestand als Ausgangspunkt

Der Datenbestand liegt in Form vorkonfektionierter JSON-Dateien vor, die bereits stark auf Analyse- und Visualisierungszwecke hin normalisiert sind. Die Ebenen und Dimensionen des Modells (vgl. `data.md`) finden sich darin konkret wieder.

### 2.1 Quantitative Eckdaten

| Ebene | Anzahl | Datei |
|---|---|---|
| Quellendokumente (gesamt) | 2.740 | `search.json`, `docs_lookup.json` |
| Quellendokumente QGW | 2.112 | |
| Quellendokumente Stadtbücher | 628 | |
| Events (Rechtsgeschäfte) | 5.002 | `epic_a.json`, `epic_c.json` |
| Personen (konsolidierte Identitäten) | 16.084 | `persons_search.json` |
| davon männlich / weiblich | 11.860 / 4.224 | |
| Organisationen | 1.078 | `organisations_search.json` |
| Orte | 2.537 | `places_search.json` |
| Annotierte Beziehungen | 12.178 | `epic_b.json` |

Zeitraum: freigegeben 1177 bis 1412 (Ausnahmen bis 1414), mit nicht ausgewertetem Bereich 1418 bis 1447. Die Dokumentdichte ist stark ungleichverteilt: 779 Dokumente allein in den 1390er Jahren (davon 514 Stadtbücher), wenige Dutzend Dokumente in den ersten zwei Jahrhunderten.

### 2.2 Register-Dateien

Die drei Register liegen als flache Arrays mit kompakten Feldnamen vor. Beispiel `persons_search.json`:

```json
{
  "id": "pe__abraham_QGW_II_I_1599",
  "n":  "Abraham der Jud",
  "fn": "Abraham",
  "sn": "",
  "sex": "m",
  "d": "",
  "dc": 1,
  "qw": 1
}
```

Felder: `id` eindeutige Kennung, `n` Namensform, `fn`/`sn` Vor- und Familienname, `sex` Geschlecht, `d` Datierung, `dc` Anzahl der Quellen mit Nennung (*document count*), `qw` Qualitäts- bzw. Normalisierungsgewicht (`-1` unbekannt, `0` niedrig, `1` und `2` höhere Konfidenz).

`organisations_search.json` hat das gleiche Schema plus Feld `tp` für den Organisationstyp. `places_search.json` enthält zusätzlich `lat`, `lng`. Alle drei Register sind zur Laufzeit direkt filter- und indizierbar, ohne weitere Aufbereitung.

### 2.3 Vorkompilierte Aggregationen: die `epic_*`-Dateien

Die `epic_*.json` enthalten bereits vorberechnete Kreuztabellen mit Drill-Down-Listen auf Dokumentenebene. Sie entsprechen exakt dem in früheren Iterationen theoretisch angenommenen Konzept der *vorberechneten Aggregationen*.

- `epic_a.json` Rollen × Geschlecht × Dekade × Organisationstyp (Event-Partizipationen)
- `epic_b.json` Beziehungen (Verwandtschaft, Beruf, Vertretung, Freundschaft), 12.178 insgesamt
- `epic_c.json` Transaktionstypen × Dekade × Organisationstyp
- `epic_d.json` Ortsregister mit Referenzierungs- und Georeferenzierungsstatus

Die Struktur jeder Datei ist dreigeteilt:

```
meta          Schema, Dimensionen, Maße, Quellen
observations  Kreuztabellen als verschachtelte Objekte
drill_down    Listen von Dokument-IDs pro Zelle
coverage      Gesamtsummen und Datenqualitäts-Indikatoren
```

Das ermöglicht ein einheitliches UI-Muster: aggregierte Zahl anzeigen, bei Klick direkt die Liste der Quelldokumente aufschlüsseln, über `docs_lookup.json` zu Metadaten jedes Dokuments auflösen.

### 2.4 Organisationstypen als Klassifikationsbasis

Das Feld `tp` im Organisationsregister enthält eine geschlossene Typologie, auf der die Kategorie *geistlich vs. weltlich* aufsetzen muss, da sie im Datenmodell nicht als eigene Eigenschaft vorliegt, sondern über eine Zuordnungstabelle erzeugt werden muss:

| Kategorie | Typen | Summe der Entitäten |
|---|---|---|
| geistlich | Messe, Pfarre, Kirche_Kapelle, Altar, Dioezese_Erzdioezese, Kloster_m, Kloster_f, Zeche_Bruderschaft, Spital_Siechenhaus, Orden, Kirche, Kapelle | ~870 |
| weltlich | Stadt, Gemeinde, Stadtviertel, Herzogtum, Burg, Koenigreich, Reich, Markgrafschaft | ~183 |
| sonstige / kontextabhängig | Universitaet, OTHER | ~26 |

Diese Zuordnung ist eine inhaltliche Modellierungsentscheidung, die im Interface dokumentiert werden muss. Zeche_Bruderschaft und Spital_Siechenhaus sind Grenzfälle und sollten als solche ausweisbar sein.

### 2.5 Datenqualität und Freigabestand

Der Validierungsreport (`quality.json`) und Coverage-Angaben der `epic_*` zeigen ein differenziertes Bild:

- Normalisierte Transaktionen: 1.057 von 5.002 Events (~21 Prozent). 938 Events haben ein dispositives Verb, das noch nicht in das kontrollierte Vokabular normalisiert wurde.
- Personen mit Organisationszuordnung: 3.865 von 16.084 (~24 Prozent).
- Referenzierte Orte: 37 von 2.537. Mit Koordinaten: 717.
- Einzigartige Verbformen: 1.082 (Normalisierungsreserve für Transaktionstypen).
- Validierungsbefunde: 2.103 insgesamt (1.918 *info*, 185 *warning*), konzentriert auf `QGW/Vienna_1177-1414_ready`.
- Nicht freigegebene Korpora: `QGW/Vienna_1415-1417`, `QGW/Vienna_1458-66`, `QGW/Vienna_1493-1500` erscheinen in der Validierung, sind aber im UI nicht sichtbar zu machen.

Diese Zahlen sind keine nebensächliche Meta-Information, sondern konstitutiver Teil dessen, was das Interface ausweisen muss. Eine Zählung von *Transaktionen vom Typ Kauf* bedeutet nicht, dass alle anderen Events keine Käufe sind, sondern dass nur 21 Prozent überhaupt kategorisiert wurden.

### 2.6 Volumen und Performance

Rohgrößen der Dateien: `search.json` 2,5 MB, `persons_search.json` 2,3 MB, `epic_b.json` 1,6 MB, `epic_c.json` 1,7 MB, `docs_lookup.json` 722 KB. Gzip-komprimiert (GitHub Pages liefert standardmäßig komprimiert aus) reduziert sich das erfahrungsgemäß auf 20 bis 30 Prozent. Progressives Laden (Register beim Start, `epic_*` on-demand beim Öffnen der zugehörigen Template-Familie) hält den initialen Transfer im Bereich weniger hundert KB.

## 3. Technische Architektur

### 3.1 Verzicht auf SPARQL im Browser

Comunica oder Oxigraph WASM funktionieren grundsätzlich, bringen aber deutlichen Overhead (Bundle mehrere MB, Cold Start, kleine Entwicklerbasis). Da die Aggregationen im Datenbestand bereits vorberechnet vorliegen, ist die Ausdrucksstärke einer SPARQL-Engine nicht nötig und methodisch nicht gerechtfertigt.

### 3.2 Zweischichtige Laufzeitarchitektur

**Aggregations-Schicht (read-only, vorkompiliert).** Für Fragen, die sich auf die vorberechneten Kreuztabellen der `epic_*` abbilden lassen, werden die Zählungen direkt aus der passenden Datei gelesen. Antwortzeit: Einzelabfrage, O(1)-Lookup in verschachtelten Objekten.

**Filter-Schicht (dynamisch, auf Register-Arrays).** Für Fragen, die die vorberechneten Dimensionen kombinieren oder feinere Filter setzen, werden die Register-Arrays zur Laufzeit gefiltert. Bei 16.000 Einträgen und einfachen Prädikaten liegt das im Millisekundenbereich.

**Drill-Down-Schicht.** Jede Aggregation ist über `drill_down[key]` mit einer Liste von Dokument-IDs verknüpft, die über `docs_lookup.json` in Metadaten aufgelöst werden. Das erlaubt das Klick-zu-Quellen-Muster ohne zusätzliche Datenladung.

### 3.3 Indizierung beim Start

Beim ersten Öffnen des Analysebereichs werden folgende Indizes im Speicher aufgebaut:

```
personsById         Map<id, Person>
personsBySex        Map<"m"|"f", Person[]>
personsByQw         Map<number, Person[]>
orgsById            Map<id, Organisation>
orgsByType          Map<typeName, Organisation[]>
orgsByCategory      Map<"geistlich"|"weltlich"|"sonstige", Organisation[]>
placesById          Map<id, Place>
docsById            Map<id, Document>
docsByCorpus        Map<corpusName, Document[]>
docsByDecade        Map<decade, Document[]>
```

Diese Indizes stehen allen Query-Templates zur Verfügung und sind nach Build einmal initialisiert.

### 3.4 Kategorien-Mapping als separates Artefakt

Die Zuordnung `tp → category` (geistlich/weltlich/sonstige) liegt nicht in den Daten, sondern muss explizit modelliert werden. Sie gehört als eigene Konfigurationsdatei `categories.json` ins Repository, versioniert und dokumentiert. Im Interface muss die verwendete Zuordnung aufrufbar und zitierbar sein.

### 3.5 Freigabe-Filter

Nicht alle Korpora in der Validierung sind im UI sichtbar. Eine Konfiguration `release.json` entscheidet, welche Korpora und welche Register-Dimensionen angezeigt werden. Die Filterung erfolgt beim Build (um die ausgelieferten JSON-Dateien klein zu halten) und zusätzlich zur Laufzeit als Sicherheitsnetz.

### 3.6 Build-Pipeline

GitHub Action beim Deploy:

1. Eingangsdaten (JSON-LD oder TEI-abgeleitet) werden normalisiert.
2. Register werden mit kompakten Feldnamen geschrieben.
3. Aggregationen (`epic_*`) werden neu gerechnet, inklusive `drill_down` und `coverage`.
4. `categories.json` und `release.json` werden angewendet.
5. Dateien werden gzipkomprimiert ausgeliefert.

## 4. Interface-Konzept: Query-Templates mit Slots

### 4.1 Grundstruktur

Ein Template ist ein Satz mit typisierten Lücken. Das generische Template lautet:

> Zeige [Zählmodus] von [Entitätstyp] mit [Eigenschaft] gleich [Wert], gruppiert nach [Dimension].

Der Nutzer füllt die Slots der Reihe nach; jede Auswahl schränkt die möglichen Folgewerte ein. Bei jeder Wahl wird live die resultierende Ergebniszahl angezeigt.

### 4.2 Slot-Typen

**Zählmodus-Slot.** Bestimmt die Zählebene: individuelle Identitäten, Gesamtnennungen, Events, Quellendokumente. Die Unterscheidung ist nicht kosmetisch: *Anzahl Personen mit Rolle Zeuge* (individuell) und *Anzahl Zeugen-Nennungen* (Gesamt) sind verschiedene Zahlen.

**Entitätstyp-Slot.** Geschlossene Liste der im Freigabestand sichtbaren Entitäten: Personen, Organisationen, Orte, Quellen, Events. Welche tatsächlich wählbar sind, hängt am Freigabe-Filter und an der Verfügbarkeit von Aggregationen.

**Eigenschafts-Slot.** Dynamisch abhängig vom Entitätstyp. Für Personen: Geschlecht, Rolle im Event, Beruf, Verwandtschaftsbeziehung, Qualitätsgewicht. Für Organisationen: Typ, Kategorie (geistlich/weltlich). Für Quellen: Korpus, Jahrzehnt, Erschließungsform. Für Events: Transaktionstyp, beteiligter Organisationstyp.

**Wert-Slot.** Tatsächlich vorkommende Werte aus den Daten, mit Count hinter jeder Option.

**Gruppierungs-Slot.** Optional. Bestimmt die Pivot-Dimension: nach Dekade, nach Korpus, nach Organisationstyp, nach Geschlecht. Gibt das Ergebnis nicht als einzelne Zahl, sondern als Tabelle oder Diagramm aus.

**Join-Slot.** Weil Verknüpfungen zwischen Personen und Organisationen über Events laufen, braucht es für Fragen wie *Personen in geistlichen Einrichtungen* einen Slot, der die Verknüpfungsebene explizit macht: *Personen, die an Events mit Organisationen vom Typ [Wert] beteiligt sind, in der Rolle [Wert]*.

### 4.3 Template-Familien (konkrete Startmenge)

Aus den vorhandenen Aggregationen lassen sich unmittelbar fünf Template-Familien ableiten, die ohne zusätzliche Berechnung funktionieren:

**Familie 1: Personenrollen nach Geschlecht.** Basis: `epic_a.observations.role_by_sex`. Slot-Template: *Anzahl [Nennungen|Personen] in der Rolle [Rolle] mit Geschlecht [Geschlecht]*, optional gruppiert nach Dekade.

**Familie 2: Beteiligung an Organisationstypen.** Basis: `epic_a.observations.org_type_by_sex` und `org_type_totals`. Slot-Template: *Anzahl [Nennungen|Personen] in Events mit Organisationen vom Typ [Typ] oder Kategorie [geistlich/weltlich], mit Geschlecht [Geschlecht]*, optional gruppiert nach Dekade.

**Familie 3: Rechtsgeschäftstypen.** Basis: `epic_a.observations.transaction_types` und `epic_c.observations.tx_timeline`. Slot-Template: *Anzahl Events vom Typ [Transaktionstyp]*, optional gruppiert nach Dekade oder Empfänger-Organisationstyp.

**Familie 4: Beziehungsstrukturen.** Basis: `epic_b`. Slot-Template: *Anzahl Beziehungen vom Typ [Verwandtschaft|Beruf|Vertretung|Freundschaft] mit Label [Wert]*, optional gefiltert nach Geschlecht der beteiligten Personen.

**Familie 5: Dokumentenverteilung.** Basis: `timeline.json` und `search.json`. Slot-Template: *Anzahl Quellen im Korpus [Korpus] in der Dekade [Dekade]*.

Die erste konkrete Beispielabfrage aus dem Entwurfsgespräch (*Personen in geistlichen Einrichtungen nach Geschlecht*) realisiert sich als Familie 2 mit Kategorie-Filter *geistlich* und Gruppierung *Geschlecht*. Die resultierenden Zahlen lassen sich direkt aus `epic_a.observations.org_type_by_sex` ablesen, nach Summierung über die geistlichen Typen gemäß `categories.json`.

### 4.4 Darstellung

Für den ersten Prototyp sind Dropdowns oder Chip-Gruppen pragmatisch. Chips haben den Vorteil, alle Optionen gleichzeitig sichtbar zu machen, was das Datenmodell transparenter erscheinen lässt. Scratch-artige Drag-and-Drop-Blöcke bleiben als spätere Ausbaustufe möglich.

### 4.5 Live-Counts

Neben jeder Slot-Option steht der zugehörige Count, kontextabhängig aktualisiert bei jeder Auswahl. Das verhindert Null-Result-Queries, macht das Datenmodell transparent und gibt Exploration eine haptische Qualität. Quelle der Counts: die jeweils passende Ebene der `epic_*`-Struktur.

### 4.6 Globale Filter

Oberhalb der Templates: Korpus (multi-select), Zeitraum (Range innerhalb der freigegebenen Grenzen), Qualitätsgewicht (Schwellenwert für `qw` bei Personen). Diese Filter wirken auf alle Templates parallel.

## 5. Provenienz und epistemische Transparenz

### 5.1 Vier Ebenen

**Datensatz-Ebene.** Herkunft der Sammlung: Edition, Projekt, beteiligte Institutionen. Zentral verlinkbar.

**Korpus- und Erschließungsform-Ebene.** Jede Aggregation ist nach Korpus und Erschließungsform aufschlüsselbar. Stadtbücher (edierter Volltext) und QGW (Regesten plus Faksimile) stützen unterschiedliche Arten von Aussagen.

**Entitäts-Ebene.** Jede Person, Organisation, Ort oder Quelle trägt über die `id` eine eindeutige Identität und ist über `docs_lookup.json` mit den Originalquellen verknüpft (Monasterium-URL, Editionsstelle).

**Query-Ebene.** Unter jedem Ergebnis steht ein kompakter Auszug: verwendete Felder, Zählmodus, zugrunde gelegte Zuordnungstabellen (etwa `categories.json`), herangezogene Korpora.

### 5.2 Ausweisung der Datenqualität

Zahlen aus `quality.json` und aus den `coverage`-Blöcken der `epic_*` werden neben relevanten Counts als Kontext angezeigt. Beispiele:

- *Diese Zählung von Transaktionstypen bezieht sich auf 1.057 normalisierte Events. 3.945 Events sind bisher nicht in das kontrollierte Vokabular überführt.*
- *Diese Zuordnung Person zu Organisation basiert auf 3.865 von 16.084 Personen mit expliziter Organisationsanbindung.*

Der Interface-Ton bleibt dabei beschreibend, nicht apologetisch. Die Zahlen sind Eigenschaft der Edition, nicht Makel des Interfaces.

### 5.3 Drill-Down-Mechanik

Jede Aggregation ist interaktiv. Klick auf *192 Zeugen-Nennungen männlich* öffnet die Liste der Quelldokumente aus `drill_down.role_sex.witness.m`, aufgelöst über `docs_lookup.json` zu einer Liste mit Datum, Kurzregest und Link zur Edition. Dieser Pfad macht die aggregierte Zahl auf Einzelbelegebene nachprüfbar.

Theoretischer Bezug: Die Offenlegung dieser Übersetzungskette von der Urkunde über Katalogisierung, Annotation, Aggregation und Freigabe bis zur angezeigten Zahl entspricht der Sichtbarmachung von Latours *circulating reference*. Das Interface dokumentiert seine eigene epistemische Infrastruktur.

### 5.4 UI-Komponenten

- Info-Icon neben jeder Aggregation mit Popover (Query-Definition, Zählmodus, herangezogene Felder, Korpora, Coverage-Zahlen, verwendete Zuordnungstabellen).
- Quellenliste bei Drill-Down: Chips mit Kürzel, Datum, Erschließungsform-Markierung, verlinkt.
- Erschließungsform-Breakdown unter jedem Count (zum Beispiel *20 (Regest 15, Volltext 5)*).
- Export als JSON oder CSV: Query-Spezifikation, Ergebniszahlen, beteiligte Dokument-IDs, Zeitstempel, Versionskennung der Daten.

## 6. Sonderfälle und offene Punkte

### 6.1 Sonderfälle aus dem Datenmodell

`data.md` verweist auf Menschen-Events, deren UI-Behandlung in separaten Dokumenten festgelegt ist. Das Template-System muss konfigurierbar bleiben, damit solche Sonderfälle als eigene Template-Familien ergänzt werden können.

### 6.2 Zu klärende Punkte vor Implementierung

- Welche Zählmodi sind pro Entitätstyp semantisch zulässig? Nennungen gibt es nur für Register-Entitäten, nicht für Quellen.
- Wie gehen wir mit dem Anteil *unspecified* beim Geschlecht um? Im Datenmodell ist *f*/*m* binär, was die historische Realität vereinfacht und als Modellierungsentscheidung ausgewiesen werden sollte.
- Wie behandeln wir Organisationen-Templates, solange das Organisationsregister nicht öffentlich freigegeben ist? Vorschlag: Aggregationen über Organisationstypen sind möglich, Einzelentitäten bleiben ausgeblendet, bis die Freigabe erfolgt.
- Wie soll mit der Qualität der Normalisierung umgegangen werden? Vorschlag: Default-Schwellenwert `qw >= 0` (Unbekannt ausgeschlossen), mit Toggle zum Einschluss.
- Wie positionieren wir das Interface zwischen *Exploration* (spielerisch, niedrigschwellig) und *Analyse* (nachvollziehbar, zitierfähig)? Beides ist möglich, sollte aber nicht verwechselt werden.

### 6.3 Erweiterungspotenzial

- Volltextsuche auf `search.json` als alternativer Einstieg neben dem Template-Interface.
- Export der Abfragespezifikation als JSON oder CSV zur Weitergabe und Zitation.

Kartenvisualisierung und Netzwerkvisualisierung liegen konzeptionell im Bereich [[exploration]] und werden dort ausgearbeitet.

---

## Zusammenfassung

Der Analysebereich lässt sich auf Basis der vorhandenen JSON-Datenbestände als statisches Frontend ohne Backend umsetzen. Die `epic_*`-Dateien liefern bereits vorberechnete Aggregationen mit Drill-Down-Listen auf Dokumentenebene, sodass das zentrale UI-Muster (Zahl anzeigen, Herkunft aufschlüsseln, Quellen einsehen) direkt implementierbar ist. Die Register-Dateien erlauben dynamische Filter in Millisekunden. Die Kategorisierung *geistlich/weltlich* ist als eigene Zuordnungstabelle zu modellieren, da sie im Datenmodell nicht als Eigenschaft vorliegt. Das Interface nutzt Query-Templates mit sechs Slot-Typen (Zählmodus, Entitätstyp, Eigenschaft, Wert, Gruppierung, Join), Live-Counts aus den vorberechneten Aggregationen und Provenienzanzeige auf vier Ebenen inklusive Coverage-Kontext.

Eine konkrete Startmenge von fünf Template-Familien lässt sich ohne zusätzliche Berechnung aus den vorhandenen Aggregationen realisieren: Personenrollen, Organisationsbeteiligungen, Rechtsgeschäftstypen, Beziehungsstrukturen, Dokumentenverteilung.

Mögliche nächste Schritte:

- Die Zuordnungstabelle `categories.json` für Organisationstypen schreiben und im Team abstimmen, weil sie als Modellierungsentscheidung die späteren Zählungen prägt.
- Einen minimalen Prototyp einer Template-Familie (Vorschlag: Familie 2, Organisationsbeteiligungen nach Geschlecht) als Proof of Concept implementieren, um Interaktionsfluss, Live-Counts und Drill-Down an realen Daten zu erproben.