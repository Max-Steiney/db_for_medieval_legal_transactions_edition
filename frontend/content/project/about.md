## Projektbeschreibung

**Stadt und Gemeinschaft Wien** ist eine prosopographische Datenbank
mittelalterlicher Wiener Rechtsgesch&auml;fte. Sie dokumentiert soziale Strukturen,
Netzwerke und Strategien von Individuen und Gruppen im sp&auml;tmittelalterlichen Wien.

Die Datenbank erschlie&szlig;t TEI-XML-Quelltexte mit Personen, Organisationen und Orten
in einem vierstufigen Annotationsmodell und macht sie durch interaktive Visualisierungen
zug&auml;nglich. Den Freigabestand der Quellen zeigt die [Quellenliste](../documents.html);
Verantwortliche, Lizenz und Zitierweise stehen im [Impressum](../impressum.html).

## Forschungskontext

Methodisch folgt das Projekt dem Ansatz der digitalen Prosopographie.
Jede Quelle wird auf vier Ebenen annotiert: Ereignisse, Funktionen,
Entit&auml;ten und Attribute/Relationen.

## Forschungsfragen

Zwei &uuml;bergreifende Forschungsfragen strukturieren die digitale Erschlie&szlig;ung:

| | Forschungsfrage | Zugang |
|---|----------------|--------|
| 1 | Welche sozialen, &ouml;konomischen und institutionellen Beziehungsgeflechte lassen sich aus den Wiener Rechtsgesch&auml;ften prosopographisch rekonstruieren? Wie strukturieren Verwandtschaft, Amt, Besitz und Repr&auml;sentation die st&auml;dtische Gesellschaft? | [Auswertungen](../analysis/auswertungen.html), [Personennetzwerk](../exploration/personennetzwerk.html) |
| 2 | Wie ver&auml;ndern sich Transaktionspraktiken im sp&auml;tmittelalterlichen Wien &uuml;ber die Zeit, und welche institutionellen Empf&auml;ngerstrukturen lassen sich identifizieren? | [Zeitstrom](../exploration/zeitstrom.html) |

## Annotationsmodell

Jedes Quelldokument wird in vier hierarchischen Ebenen annotiert.

### Ebene 1: Ereignisse

Rechtsgesch&auml;fte (`<rs type="event">`) werden identifiziert und &uuml;ber dispositive
Verben (`<catchwords>`) kategorisiert. Die Kategorienbildung erfolgt post-hoc aus
den Verbformen, nicht a priori.

### Ebene 2: Funktionen

Innerhalb jedes Ereignisses werden Funktionsrollen zugewiesen:
Aussteller\*in (*issuer*), Empf&auml;nger\*in (*recipient*),
Zeug\*in (*witness*) und Sonstige (*other*).

### Ebene 3: Entit&auml;ten

Personen, Organisationen und Orte werden identifiziert und &uuml;ber
eindeutige Identifikatoren (`@ref`) mit den Registern verkn&uuml;pft.

### Ebene 4: Attribute und Relationen

Eigenschaften (Beruf, Titel, Tod) und Beziehungen (Verwandtschaft, Amt,
Repr&auml;sentation, Freundschaft, Topographie) werden &uuml;ber
`<roleName>` annotiert und mit Referenzen (`@corresp`) aufgel&ouml;st.

Die vollst&auml;ndigen Annotationskonventionen stehen in den
[Annotationsrichtlinien](edition-guidelines.html).

## Technische Umsetzung

Die Datenbank wird als **statische Website** auf GitHub Pages publiziert.
Die gesamte Verarbeitungskette ist transparent und reproduzierbar.

| Komponente | Technologie |
|------------|------------|
| Quelldaten | TEI-XML |
| Schema | RelaxNG (`toolbox.rng`) |
| Pipeline | Python/lxml |
| Webanwendung | Python/Jinja2, HTML/CSS/JS |
| Visualisierung | SVG-Diagramme (client-seitig) |
| Tests | pytest (Pipeline + Webanwendung) |
| Hosting | GitHub Pages (statisch) |

Der Quellcode liegt in zwei Repositories: Datengrundlage in
[db\_for\_medieval\_legal\_transactions](https://github.com/chpollin/db_for_medieval_legal_transactions),
Publikationsschicht in
[db\_for\_medieval\_legal\_transactions\_edition](https://github.com/chpollin/db_for_medieval_legal_transactions_edition).

## Qualit&auml;tssicherung

Die Datenbank erf&uuml;llt die Anforderungen einer externen Begutachtung
(Lehrstuhl f&uuml;r Digital Humanities, Universit&auml;t Graz, Dezember 2025):

- **Lizenz**: CC BY 4.0
- **Schema**: RelaxNG ersetzt DTD (ODD-Anforderung)
- **Validierung**: Fehlerfrei &uuml;ber alle Quelldateien
- **XPointer-Konformit&auml;t**: Alle Referenzen standardisiert
- **Annotationsrichtlinien**: Dokumentiert in den [Annotationsrichtlinien](edition-guidelines.html)
- **Kontrolliertes Vokabular**: Typisierung und Normalisierung aller Annotationsattribute
