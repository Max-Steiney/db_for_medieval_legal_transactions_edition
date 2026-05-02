## Projektbeschreibung

**Stadt und Gemeinschaft Wien** ist eine digitale Edition der prosopographischen Datenbank
mittelalterlicher Wiener Rechtsgesch&auml;fte (ca. 1177&ndash;1524). Die Datenbank
dokumentiert soziale Strukturen, Netzwerke und Strategien von Individuen und Gruppen
im sp&auml;tmittelalterlichen Wien.

Die Edition erschlie&szlig;t TEI-XML-Quelltexte mit Personen,
Organisationen und Orten in einem vierstufigen Annotationsmodell
und macht sie durch interaktive Visualisierungen zug&auml;nglich.

## Forschungskontext

Die Datenbank entstand im Kontext zweier Forschungsprojekte:

- **&raquo;Im Netz der Stadt&laquo;** &mdash; Dissertation
  zur prosopographischen Rekonstruktion sozialer Verflechtungen in Wien auf Basis
  mittelalterlicher Rechtsgesch&auml;fte. Die Datenbank wurde f&uuml;r diese Arbeit
  konzipiert und der XML-Standard entwickelt.

- **&raquo;Stadt und Gemeinschaft&laquo;** (Universit&auml;t Wien) &mdash;
  Parallelprojekt, das die Datenbank im Kontext st&auml;dtischer Gemeinschaftsbildung
  und Zugeh&ouml;rigkeit nutzt.

Methodisch folgt das Projekt dem **Factoid-Ansatz** der digitalen Prosopographie
(King&rsquo;s College London). Jede Quelle wird auf vier Ebenen annotiert: Ereignisse,
Funktionen, Entit&auml;ten und Attribute/Relationen.

## Forschungsfragen

Zwei &uuml;bergreifende Forschungsfragen strukturieren die digitale Erschlie&szlig;ung:

| | Forschungsfrage | Exploration |
|---|----------------|-------------|
| 1 | Welche sozialen, &ouml;konomischen und institutionellen Beziehungsgeflechte lassen sich aus den Wiener Rechtsgesch&auml;ften prosopographisch rekonstruieren? Wie strukturieren Verwandtschaft, Amt, Besitz und Repr&auml;sentation die st&auml;dtische Gesellschaft? | [Rollen](exploration_roles.html), [Beziehungen](exploration_networks.html) |
| 2 | Wie ver&auml;ndern sich Transaktionspraktiken im sp&auml;tmittelalterlichen Wien &uuml;ber die Zeit, und welche institutionellen Empf&auml;ngerstrukturen lassen sich identifizieren? | [Transaktionen](exploration_transactions.html) |

## Quellenbestand

Die Edition verarbeitet Quellen aus neun Sammlungen mit einem Zeitraum von 1177 bis 1524.
Zwischen 1418 und 1447 besteht eine &Uuml;berlieferungsl&uuml;cke (keine Quellen).

| Sammlung | Zeitraum |
|----------|----------|
| QGW II/1 | 1177&ndash;1414 |
| Stadtb&uuml;cher Bd. 1 | 1395&ndash;1400 |
| QGW II/2 (1448&ndash;1457) | 1448&ndash;1457 |
| QGW II/3 | 1458&ndash;1466 |
| Gewerbuch D | 1448&ndash;1460 |
| Satzbuch CD | 1448&ndash;1460 |
| QGW II/4 | 1493&ndash;1500 |
| QGW II/2 (1415&ndash;1417) | 1415&ndash;1417 |
| QGW II/5 | 1524 |
| Weitere | diverse |

## Annotationsmodell

Jedes Quelldokument wird in vier hierarchischen Ebenen annotiert:

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

## Technische Umsetzung

Die digitale Edition wird als **statische Website** auf GitHub Pages publiziert.
Die gesamte Verarbeitungskette ist transparent und reproduzierbar:

| Komponente | Technologie |
|------------|------------|
| Quelldaten | TEI-XML |
| Schema | RelaxNG (`toolbox.rng`) |
| Pipeline | Python/lxml |
| Edition | Python/Jinja2 &rarr; HTML/CSS/JS |
| Visualisierung | SVG-Diagramme (client-seitig), Leaflet.js (Karten) |
| Tests | pytest (Pipeline + Edition) |
| Hosting | GitHub Pages (statisch) |

Der Quellcode ist verf&uuml;gbar unter:
[github.com/chpollin/db\_for\_medieval\_legal\_transactions](https://github.com/chpollin/db_for_medieval_legal_transactions)

## Qualit&auml;tssicherung

Die Edition erf&uuml;llt alle kurzfristigen Anforderungen einer externen Begutachtung
(Lehrstuhl f&uuml;r Digital Humanities, Universit&auml;t Graz, Dezember 2025):

- **Lizenz**: CC BY 4.0
- **Schema**: RelaxNG ersetzt DTD (ODD-Anforderung)
- **Validierung**: Fehlerfrei &uuml;ber alle Quelldateien
- **XPointer-Konformit&auml;t**: Alle Referenzen standardisiert
- **Annotationsrichtlinien**: Dokumentiert in den [Editionsrichtlinien](edition_guidelines.html)
- **Kontrolliertes Vokabular**: Typisierung und Normalisierung aller Annotationsattribute

## Zitierweise

> *Stadt und Gemeinschaft Wien &mdash; Datenbank zu mittelalterlichen Wiener Rechtsgesch&auml;ften.*
> Universit&auml;t Wien, 2026.
> Digitale Aufbereitung: Digital Humanities Craft OG.
> Online: [github.com/chpollin/db\_for\_medieval\_legal\_transactions](https://github.com/chpollin/db_for_medieval_legal_transactions).
> Lizenz: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Kontakt

- **Forschungsprojekt**: Universit&auml;t Wien
- **Digitale Aufbereitung**: [Digital Humanities Craft OG](https://dhcraft.org)
