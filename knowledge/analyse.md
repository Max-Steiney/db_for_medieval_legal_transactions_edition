---
title: Analyse
project:
  name: Stadt und Gemeinschaft Wien
  repository: https://github.com/chpollin/db_for_medieval_legal_transactions_edition
status: active
language: de
version: 0.2
created: 2026-02-19
updated: 2026-05-16
authors: [Christopher Pollin]
generated-with: Claude Code
method:
  name: Promptotyping
  url: https://lisa.gerda-henkel-stiftung.de/digitale_geschichte_pollin
topics: ["[[Information Visualisation]]", "[[Quantitative Analysis]]"]
related: [exploration, specification, ui-design, decisions, glossar]
---

# Analyse

Der Analysebereich versammelt die quantitativen Zugänge zur Datenbasis. Er steht als gleichberechtigter Zweig neben der [[exploration]]: das Interaktionsmuster ist strukturiert (vorgegebene Achsen, exakte Zahlen, Provenienz), die Exploration arbeitet visuell-interaktiv. Begründung der Trennung in [[specification#Exploration und Analyse als getrennte Bereiche]]. In der öffentlichen Sicht ist der Analysebereich derzeit ausgeblendet (Stakeholder-Protokoll 18.05.2026, Prio 1); seine Seiten entstehen nur im internen Build (`--audience intern`).

## Zwei Sub-Seiten

**Auswertungen** (`/analysis/auswertungen.html`) zeigt vorberechnete Verteilungen: Funktionsrollen, Beziehungstypen, Transaktionstypen, Bezeichnungen — jeweils als Donut, Bar-Chart oder Tabelle mit Mini-Bars. Filter sind Zeitraum und Geschlecht; eine Zähleinheit-Umschaltung in der Funktionsrollen-Sektion wechselt lokal zwischen Nennungen und Individuellen Personen. Die Seite ist filter-getrieben — Nutzerinnen ändern Achsen und sehen Verteilungen sich anpassen. Begründung der Verortung in [[specification#Auswertungen gehört in den Analyse-Bereich]].

Jede Aggregat-Zelle ist klickbar und öffnet das [[ui-design#Drill-down-Overlay]] mit den beitragenden Quellen — Donut-Arc und Legend-Item für Funktionsrollen und Beziehungstypen, Bar für Transaktionstypen, Tabellenzeile für Bezeichnungen. Im Footer steht der Cross-Page-Sprung in die Quellen-Liste mit übernommenem Zeitraum-und-Geschlecht-Filter ([[ui-design#Cross-Page-Sprung in die Quellen-Liste]]). Der Filter-Stand wird in die URL serialisiert, damit jeder Forschungsstand zitierbar ist ([[ui-design#URL-State-Sync]]).

**Abfragen** (`/analysis/index.html`) ist eine strukturierte Konstellations-Abfrage: Forscherinnen legen beliebig viele nummerierte Personen-Bedingungen an, je mit Rolle und optionalen Filtern (Geschlecht, Beruf/Tätigkeit/Amt), und sehen alle Rechtsgeschäfte, in denen diese Konstellation gemeinsam erfüllt ist. Globaler Filter: Korpus (Mehrfachauswahl) plus Reset. Der Verknüpfungs-Modus (Rechtsgeschäft eng vs. Quelle weit) ist im UI ausgeblendet. Live-Update, kein Submit. Architektur und Begründung in [[specification#Abfragen-Sub-Seite als Konstellations-Abfrage]].

Die beiden Sub-Seiten lesen unterschiedliche Aggregate und tragen unterschiedliche Filter. Auswertungen stützt sich auf `roles.json`, `relations.json` und `transactions.json` und filtert nach Zeitraum und Geschlecht; Abfragen liest allein `role_constellation.json` (plus `docs_lookup.json` für die Metadaten) und filtert nur nach Korpus. Eine Filteränderung auf der einen Seite überträgt sich nicht automatisch auf die andere; das ist eine offene Designfrage.

## Zielsetzung

Der Analysebereich soll Nutzerinnen erlauben, konkrete inhaltliche Fragen an den Datenbestand zu stellen, ohne SQL, SPARQL oder vergleichbare Query-Sprachen lernen zu müssen. Statt beliebiger Abfragen werden vorgefertigte Fragetypen angeboten, die über typisierte Slots angepasst werden. Das konzeptionelle Vorbild ist die komponierbare Logik von Scratch, übersetzt in ein domänenspezifisches Vokabular für Urkundenforschung.

Typische Beispielfragen:

- Wie viele geistliche Einrichtungen sind im Datenbestand belegt?
- Wie verteilen sich die Beteiligten an Rechtsgeschäften nach Geschlecht?
- Welche Rechtsgeschäftstypen treten in welchem Zeitraum auf?
- In welchen Rollen treten Frauen in Stadtbüchern auf?

Vier konkrete Forschungsfragen aus der editorischen Praxis prägen die Galerie ([[user-stories#2 Konkrete Forschungsfragen aus der editorischen Praxis]]):

- Welche Personen in Uhlirz-Berufskategorie IV sind untereinander verheiratet?
- Welche Personen in Uhlirz-Berufskategorie VI haben Hausbesitz an welchen Orten?
- Welche Personen sind durch eine Tätigkeit (`occ`) an St. Stephan gebunden, und wer sind ihre Verwandten?
- Welche Personen oder Organisationen stehen in einem Issuer-Recipient-Verhältnis zu St. Agnes auf der Himmelpforte?

Diese vier Fragen sind nicht Beispielsammlung, sondern Implementierungs-Achse für die Galerie und die Sektionen der Organisationsprofile; jede Frage etabliert einen wiederverwendbaren Aggregator-Baustein (Uhlirz-Kategorie-Join, Heirats-Begriffs-Match, Org-Hierarchie-Traversal, Cross-Role-Query), der danach für ähnliche Fragen verfügbar ist.

## Datenbestand

Pro Ebene liegt eine eigene JSON vor: Quellen in `search.json` und `docs_lookup.json`, Personen in `persons_search.json`, Organisationen in `orgs_search.json`, vorberechnete Aggregate in `roles.json`, `relations.json` und `transactions.json`. Detail-Profile pro Entität liegen unter `register/persons/` und `register/orgs/`.

Die Aggregat-JSONs enthalten vorberechnete Kreuztabellen mit Drill-Down-Listen auf Dokumentenebene und sind dreigeteilt: `meta` (Schema, Dimensionen, Quellen), `observations` (Kreuztabellen), `drill_down` (Listen von Dokument-IDs pro Zelle) und `coverage` (Gesamtsummen und Datenqualitäts-Indikatoren). Das ermöglicht das einheitliche UI-Muster *aggregierte Zahl anzeigen, bei Klick Quelldokumente auflisten, über `docs_lookup.json` zu Metadaten auflösen*.

Das Personenregister liegt als flaches Array mit kompakten Feldnamen vor (Kennung, Namensform, Vor- und Familienname, Geschlecht, Datierung, Quellen-Count, Qualitätsgewicht). Das Organisationsregister nutzt dasselbe Schema mit zusätzlichem Typ-Feld. Orts-Annotationen im Quellen-Volltext bleiben als Inline-Markup sichtbar, tragen aber kein Sprungziel und kein eigenes Register.

### Organisationstypen als Klassifikationsbasis

Das `tp`-Feld des Organisationsregisters führt eine geschlossene Typologie. Die Kategorie geistlich/weltlich liegt nicht als eigene Eigenschaft vor und muss über eine versionierte Zuordnungstabelle erzeugt werden. Im Interface ist die verwendete Zuordnung aufrufbar und zitierbar. Grenzfälle (Zeche/Bruderschaft, Spital/Siechenhaus) sind als solche ausweisbar.

### Datenqualität und Freigabestand

Die `coverage`-Blöcke der Aggregat-JSONs (etwa `role_constellation.json.coverage`) machen die Datenqualität sichtbar. Charakteristisch ist eine durchgängig niedrige Normalisierungsrate. Diese Verhältnisse sind keine nebensächliche Meta-Information: eine Zählung *Transaktionen vom Typ Kauf* bedeutet nicht, dass alle anderen Events keine Käufe sind, sondern dass nur ein Bruchteil überhaupt kategorisiert ist.

Single Source of Truth für die freigegebenen Korpora ist `RELEASED_CORPORA` im Schwester-Repo (`pipeline/config.py`); der Zeitraum lebt als `RELEASED_PERIOD` im Frontend-Repo (`frontend/config.py`). Hardcoded Werte in Templates sind ein Fehler.

## Technische Architektur

Zwei Laufzeit-Schichten tragen die Analyse-Seiten. Die **Aggregations-Schicht** liest vorberechnete Kreuztabellen aus den Aggregat-JSONs. Die **Filter-Schicht** kombiniert oder verfeinert dynamisch, indem sie die Register-Arrays zur Laufzeit filtert. Die **Drill-Down-Schicht** verknüpft jede Aggregat-Zelle mit einer Liste von Dokument-IDs, aufgelöst über `docs_lookup.json` — Klick-zu-Quellen ohne zusätzliches Nachladen.

Eine SPARQL-Engine im Browser (Comunica, Oxigraph WASM) wäre möglich, ist aber methodisch nicht gerechtfertigt: die Aggregationen liegen vorberechnet vor, der Engine-Overhead wäre Selbstzweck.

## Konstellations-Abfrage

Die Abfragen-Sub-Seite ist eine strukturierte Datenbank-Abfrage über Rollen-Konstellationen. Eine Forscherin stellt sie aus drei Schichten zusammen:

1. **Personen-Bedingungen.** Beliebig viele nummerierte Tabellenzeilen, je mit einer Rolle (Aussteller, Empfänger, Zeuge oder Siegler, sonstige Beteiligung) und optionalen Filtern für Geschlecht und Beruf/Tätigkeit/Amt. Die Zeile ist visuell selbsterklärend; sie braucht kein Etikett und wird im UI nur über ihre Nummer adressiert („Person 1", „Person 2"). Der Begriff „Personenblock" aus der frühen Iteration ist Entwickler-Sprache und wird im UI nicht verwendet.
2. **Verknüpfungs-Modus.** „Im selben Rechtsgeschäft" (eng, Default) oder „in derselben Quelle" (weit). Im weiten Modus werden alle Personen einer Urkunde oder eines Stadtbuch-Eintrags zusammen ausgewertet, im engen nur die eines einzelnen Geschäfts.
3. **Globale Filter.** Quellenkorpus (Mehrfachauswahl) und Reset. Der Verknüpfungs-Modus ist im UI ausgeblendet (Default Rechtsgeschäft eng), der Parser versteht `scope=source` weiterhin für alte Permalinks.

### Datenbasis und Matching

Datenquelle ist `docs/data/role_constellation.json`, ein Per-Event-Aggregat aus `frontend/aggregator/role_constellation.py`. Jedes Event trägt seine Participants mit `{p, n, r, s, t, o, u}` (Personen-ID, Name, Rolle, Geschlecht, Titel-Marker, Berufsliste, Uhlirz-Berufsklasse); optional kommt `nt` (Personen-Note) hinzu. Das Matching läuft clientseitig in `frontend/static/js/analysis-resolver.js`: pro Treffer ordnet ein Greedy-Pass jedem aktiven Block einen Participant zu, ohne eine Person doppelt zu belegen. Ergebnis ist eine Trefferliste, die nach Datum und Quelle stabil sortiert wird.

### Eingabeformen der Bedingungen

Geschlecht und Rolle nutzen kontrollierte Vokabulare und werden als Dropdown angeboten. Beruf, Tätigkeit oder Amt wird als Freitext-Feld mit Operator „enthält" und smarten Vorschlägen (eigenes Autocomplete-Popover statt des nativen `<datalist>`, das sich nicht stylen lässt) aus den Top-Originalvarianten samt Belegzahl angeboten. Eine Bedingung „Titel" gibt es nicht — die TEI-Edition trennt Honorifics nicht von Berufen, beide stehen gemeinsam in `<occupation>`. Eine eigene Titel-Achse wäre eine Pipeline-Erweiterung im Schwester-Repo, nicht eine UI-Frage.

### Anfangszustand und Empty-States

Beim Öffnen der Seite ist die Trefferliste leer und keine Personen-Zeile angelegt. Der Empty-State sagt deutlich, was zu tun ist, und bietet vier Beispiel-Konstellationen als Einstieg an. Sobald mindestens eine Zeile eine Rolle gesetzt hat, läuft die Abfrage automatisch und zeigt die Treffer-Counts in der Toolbar. Werden alle Bedingungen aufgelockert, kommt die Tabelle wieder in den Empty-State zurück.

### Permalink und Export

Der gesamte Abfrage-Stand wird als URL-Fragment serialisiert (`#p1=r=issuer,s=m,o=snyder&p2=r=recipient,s=f&c=QGW`) und beim Reload reproduziert. Ein `scope`-Parameter erscheint nur abweichend vom Default (`scope=source`); ein `y=`-Parameter wird nicht serialisiert. Der CSV-Export der angezeigten Tabelle nutzt die UI-Spalten: Datum, Quelle, Korpus, je Personen-Zeile eine Spalte mit dem Personennamen, Rechtsgeschäfts-Typ. Dateiname `abfrage_YYYY-MM-DD.csv`, UTF-8 mit BOM (Excel-kompatibel). Wer eine Trefferzeile in den Datenkorb legt, hält den Quellenbezug über Sitzungen hinweg.

## Provenienz und epistemische Transparenz

Die Provenienz lebt auf vier Ebenen:

- **Datensatz-Ebene.** Herkunft des Quellenkorpus: Datenbank, Projekt, Institutionen.
- **Korpus- und Erschließungsform-Ebene.** Jede Aggregation ist nach Korpus und Erschließungsform aufschlüsselbar. Volltext und Regest plus Faksimile stützen unterschiedliche Arten von Aussagen.
- **Entitäts-Ebene.** Jede Person, Organisation oder Quelle trägt eine eindeutige `id` und ist über `docs_lookup.json` mit den Originalquellen verknüpft.
- **Query-Ebene.** Unter jedem Ergebnis steht der verwendete Zählmodus, die herangezogenen Felder und Korpora sowie die zugrunde gelegten Zuordnungstabellen.

Drill-down-Mechanik und Provenienz-Indizierung in [[architecture#Provenienz-Indizes]], UI-Ausprägung in [[ui-design#Tip-System]] und [[ui-design#Drill-down-Overlay]]. Die Coverage-Blöcke machen Datenqualität sichtbar, ohne apologetisch zu werden — die Verhältnisse sind Eigenschaft der Datenbank, nicht Makel des Interfaces. Theoretischer Bezug: die Offenlegung der Übersetzungskette von der Urkunde bis zur angezeigten Zahl entspricht der Sichtbarmachung von Latours *circulating reference*.

## Offene Punkte

- Welche Zählmodi sind pro Entitätstyp semantisch zulässig? Nennungen gibt es nur für Register-Entitäten, nicht für Quellen.
- Wie gehen wir mit dem Anteil *unspecified* beim Geschlecht um? Das binäre `f`/`m`-Modell ist eine Vereinfachung der historischen Realität und sollte als Modellierungsentscheidung ausgewiesen werden.
- Welche Granularität an Aggregationen über Organisationen ist wissenschaftlich tragbar? Detail-Profile sind freigegeben; Aggregationen über Organisationstypen und Eigentumsbeziehungen lassen sich darauf aufbauend ergänzen.
- Volltextsuche auf `search.json` als alternativer Einstieg neben dem Frage-Interface.
- Export der Abfragespezifikation als JSON oder CSV zur Weitergabe und Zitation.

Menschen-Events sind ein Sonderfall des Datenmodells (Definition in [[technik#Menschen-Event]]). Personen-Annotationen in verschachtelten Events werden nicht doppelt gezählt, siehe [[specification#Nennungen zählen nur Personen-Annotationen außerhalb mentioned Events]]. Kartenvisualisierungen und Netzwerk-Visualisierungen liegen konzeptionell im Bereich [[exploration]].
