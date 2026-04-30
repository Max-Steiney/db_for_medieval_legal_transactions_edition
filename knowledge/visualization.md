# Information Visualisation and Exploration

The conceptual reference for the four interactive research visualisations (Epics A–D) in the digital edition. Records the principles, the data constraints that shape every panel, the per-Epic deviation from the original specification, and the open questions still under discussion. Implementation parameters live in the source.

Original specification: "Anforderungsspezifikation Informationsvisualisierung und User Interface" v6.0, March 2026 (LLM-assisted, derived from the repository data and the research programmes "Stadt und Gemeinschaft" and "Soziale Netzwerke im spätmittelalterlichen Wien"). Where this document differs from the spec, the deviation is noted in the corresponding Epic section.

For design tokens and the colour palette see [design.md](design.md); for UI components and JS modules see [ui.md](ui.md); for the build system see [architecture.md](architecture.md).

## Design principles

1. **Transparency.** Every visualisation declares its data coverage, normalisation rate, and uncertainties. Missing or uncertain values appear as their own category, never silently excluded.
2. **Traceability.** Every aggregated data point allows drill-down to the underlying source documents. Both direct references (`rs/@ref`) and indirect references (`@corresp`) lead to the document view; the reference type is shown.
3. **Reusability.** Aggregated and register data are exportable with metadata. Documents and register entries have stable references for citation.
4. **One Epic, one visualisation.** Each Epic is realised as a single interactive visualisation composed of linked panels that share a filter context. A change in one panel updates all panels of the same Epic.
5. **Static architecture.** All data is aggregated at build time and served as JSON. Client-side JavaScript renders the visualisations. No server, no API, no database at runtime. Iterative editing in the browser is incompatible with this model.

## Data constraints that shape every panel

**Two normalisation systems, not one.** Earlier versions of the spec spoke of "15 % normalisation" without distinguishing the two independent systems at work in the data:

| System | Source list | Affects |
|--------|-------------|---------|
| Transaction type | `label_norm_matching.csv` → catchwords | Epic C Panel 1, transaction-type filter in all Epics |
| Function | `function_norm_matching.csv` → triggerstrings | Epic C Panel 2, fine-grained participation analysis |

The transaction-type view operates on substantially better-covered data than the function view. The distinction is analytically important and must be communicated at every coverage label.

**Other structural constraints.** Each is surfaced as a visible category in the relevant visualisation, never silently dropped:

- Transmission gap **1419–1447** (29 years, single 1438 outlier). Hatched on every time axis.
- A small share of persons have no sex attribute. "Keine Angabe" is its own filter option.
- `@cert` coverage on person-event links is extremely low. The display is implemented but practically invisible.
- Place references split between `ref` (direct) and `corresp` (indirect) paths in roughly equal magnitudes.
- Only a quarter of place register entries have parseable coordinates; the map shows the geocoded subset, the table shows everything.
- Most places are `immo` (real-estate parcels); the map shows settlements, the table all types.
- Placeholder dates come in several patterns (year-range, partial sentinel, multi-span, undatable); each handled separately by the time slider so undatable documents stay visible.

Live coverage rates are in `pipeline/output/validation_report.md` and the statistics dashboard.

## Shared conventions

**Bar-chart scaling.** All bars in a panel share the same maximum. Absolute values determine length; percentages appear alongside. Bars under 1 % get a minimum width; if more than five categories fall under 1 %, they collapse into an expandable "Weitere" group.

**Filter logic.** Every filter change updates every panel of the Epic. Clickable elements have hover effect and cursor change. Navigation to a single document always lands in the document view.

**Initial state.** Full time range, no filters, no element pre-selected. Exception: Epic B opens with a search field instead of a pre-selected ego network — pre-selecting one would suggest an arbitrary editorial choice.

### Cross-Epic navigation

| From | To | Trigger | Result |
|------|-----|---------|--------|
| A (Panel 2/3) | B | "Im Netzwerk anzeigen" | Beziehungsexplorer opens with the selected person's relationships |
| B (detail) | A | "Institutionelles Profil" | Role Explorer shows the selected person's profile |
| C (Panel 3) | D | "Auf Karte anzeigen" | Place Explorer centres on the recipient's location |
| D (Marker) | C | "Transaktionen an diesem Ort" | Transaction Explorer with location filter |
| Register | Epics | Cross-reference list in entry | Epic occurrences with counts |

Cross-navigation appears only when data is available. Not yet implemented end-to-end.

## Epic A — Persons, roles, institutional affiliation

**Research question.** How do persons appear in legal transactions, which functional roles do they take, how do these distributions vary by sex, and in which institutional contexts do persons act?

**Visualisation.** Two top panels (role distribution, institutional affiliation) plus a full-width detail panel below, all sharing one header (time slider, sex filter, inline stats). Panel 1 is a grouped horizontal bar chart of functional roles × sex with a `%` toggle that switches between absolute counts and role-internal proportions. Panel 2 ranks org types by event count. Panel 3 is the drill-down area, activated by clicking bars in Panels 1 or 2.

**Q3 workaround.** The spec asks for an ecclesiastical/secular split. Until the mapping table from the project partners arrives (Open Question 3), Panel 2 shows org types directly (Messe, Pfarre, Stadt, Kloster, …). The mapping can be added as a post-processing layer without changing the data structure.

| US | Summary | Status |
|----|---------|--------|
| A.1 | Role distribution by sex (structural asymmetries) | Done |
| A.2 | Time filtering with gap indication | Done |
| A.3 | Breakdown by transaction type with normalisation rate | Not started |
| A.4 | Institutional affiliation by org type | Done (Q3 workaround) |
| A.5 | Institutional profile of a selected person | Partial (drill-down to documents only) |
| A.6 | Multi-affiliation frequency by sex | Not started (requires Q3) |

## Epic B — Social networks and forms of belonging

**Research question.** What social networks emerge from person co-occurrence in source documents, and what do the annotated relationship types (kin, occ, rep, friend, …) reveal about forms of belonging?

**Co-occurrence definition.** Two persons co-occur when they appear in the same `event` element (same `rs[@type="event"]`), not merely in the same document. The frequency between two persons is the number of distinct shared events. Mentioned events (`_men_` in the event ID) are currently included without distinction.

**Implementation deviation: heatmap instead of force graph.** The original spec called for a d3-force ego network with Louvain communities. Prototype evaluation showed two problems: most co-occurrence edges have weight 1 (a structural artefact of the document model rather than meaningful tie strength), and force-directed layouts at this corpus size produce unreadable hairballs. The implementation is therefore a relationship heatmap with a grouped bar chart for type × sex distribution, plus a paginated label heatmap (relationship label × type category, cell intensity = frequency, conditional "Keine Angabe" column when data exists). This focuses on what is analytically valuable — the six annotated relationship types — rather than on raw co-occurrence.

| US | Summary | Status |
|----|---------|--------|
| B.1 | Relationship type distribution with person search | Done |
| B.2 | Filter by relationship type and time range | Done |
| B.3 | Label heatmap with normalisation and pagination | Done |
| B.4 | Drill-down to documents and CSV export | Done |

## Epic C — Transaction repertoire and institutional recipients

**Research question.** What types of legal transactions occur, how does the repertoire change over the study period, and which institutions appear as recipients?

**Visualisation.** Three panels under a shared header (time slider, optional institution-type filter that switches Panel 1 to recipient perspective). Panel 1 is a stacked bar chart of decades × normalised transaction types, with two distinct "not" categories: "catchword present, not normalised" and "no catchword". These must not be merged — they are analytically different. The transmission gap is hatched, not blank. Panel 2 is the verb form browser (searchable, sortable table). Panel 3 ranks institutional recipients.

**Implementation deviations.** Panel 1 is a stacked bar chart, not a streamgraph: a streamgraph's flowing form would suggest continuity that is misleading given the unassigned share and the 30-year gap. Panel 3 is a horizontal bar chart, not a treemap: simpler, no d3-hierarchy dependency, and a ranking is more direct than an area encoding. Panel 2's stem grouping is manual, not algorithmic — Levenshtein distance on Middle High German verb forms produces too many false positives.

| US | Summary | Status |
|----|---------|--------|
| C.1 | Transaction types over time, transparent "not normalised" share | Done |
| C.2 | Searchable verb form browser with frequency and normalisation status | Done |
| C.3 | Institutional recipients by type | Done (bars, was treemap in spec) |
| C.4 | Donation patterns over time (Panel 1 in institution-filtered mode) | Deferred (Q2) |
| C.5 | Supporter list of an institution with timeline | Done (table; no timeline) |

## Epic D — Topography of property

**Research question.** What is the spatial dimension of the legal transactions, as far as the data allows?

**Data situation.** Substantially better than originally assumed. The figure "44 directly referenced places" in early specs counted only `<rs type="place">` elements in source text; the actual pipeline output via `places_in_sources.csv` shows roughly an order of magnitude more references when both `ref` and `corresp` paths are counted. Only a quarter of place register entries have parseable coordinates, but the geocoded subset is sufficient for a meaningful settlement map.

**Implementation decision.** The spec envisioned a two-stage rollout (Stage 1: map without time filter; Stage 2: time filter after re-annotation). The implemented version is a settlements-only Leaflet map plus the full register table, with a time slider that uses optional semantics: places without computable decades stay visible regardless of filter. Combines elements of both spec stages while staying honest about the data.

**Bidirectional linking.** Click on a marker highlights and scrolls to the table row; click on a table row pans/zooms the map. Both popups and table rows open the standard drill-down overlay with the document list.

**Temporal dimension.** Places have no inherent time dimension; they inherit dates via `places_in_events` → `events_in_sources`. The aggregator computes a sorted list of decades per place. The slider treats places without decades as always-visible.

External dependencies: Leaflet and Leaflet.markercluster (CDN with integrity hash). Tile source: OpenStreetMap. Historical map material is a separate licensing project and not included.

| US | Summary | Status |
|----|---------|--------|
| D.1 | Settlement map with coverage statistic and time filter | Done |
| D.2 | Full place register with type/georef filters and bidirectional map linking | Done |

## Open questions

The live discussion items, kept here as the project's running context. Numbering follows the original spec.

### For domain experts

| # | Question | Affects | Status |
|---|---------|---------|--------|
| 1 | `@cert`: "not evaluated" as own category, or implicitly certain? | Epic B display | Resolved (conditional column) |
| 2 | `Kirche`/`Kapelle`/`Kirche_Kapelle`: merge or keep separate? | Epic C Panel 3 | Open |
| 3 | Ecclesiastical/secular mapping of org types | Epic A Panels 2+3 | Partially resolved (workaround in place) |
| 4 | Place annotation expansion as separate task? | Epic D expansion | Partially resolved (Stage 1 implemented) |
| 5 | Verb normalisation — pre-task or iterative? In-browser iterative is incompatible with the static architecture; recommendation: pre-task outside the edition. | Epic C enhancement | Open |
| 6 | Bar chart scaling — optional absolute/proportional toggle in Epic A Panel 1 | Epic A UI | Toggle implemented (E1); default-mode question still open |
| 7 | Reading view — diplomatic text + view with resolved abbreviations? Depends on `<expan>` in TEI. | Document view | Open |
| 9 | Network scope — should organisations and places be nodes too? Requires a separate co-occurrence definition. | Epic B scope | Open (not blocking the current heatmap) |

### For developer

| # | Question | Affects | Status |
|---|---------|---------|--------|
| 8 | JSON-LD export — requires RDF schema, classified as Tier 3. Recommendation: out of scope; CSV export sufficient. | Register export | Deferred |
| 10 | Mentioned-events toggle — two JSON variants at build time vs. client-side filtering | Epic B | Deferred |
| 11 | Stable URIs for visualisation states — filter parameters in URL? | All Epics | Open |
| 12 | CSV export metadata header — how extensive? Spec wants data basis, filters, timestamp, normalisation rate. | All Epics | Open |
| 13 | Source overview vs. statistics page — merge or keep separate? | Navigation | Open |

## Out of scope (current contract)

JSON-LD export, RDF/CIDOC-CRM modelling, GND/Wikidata linking, and a SPARQL endpoint are classified as Tier 3 in the Vogeler evaluation (see [../../db_for_medieval_legal_transactions/knowledge/status.md](../../db_for_medieval_legal_transactions/knowledge/status.md)) and require either an RDF schema, authority-data matching, or server infrastructure incompatible with the static architecture. Iterative verb normalisation in the browser would require a backend. NLP/AI-assisted annotation is research infrastructure. Each of these can be specified as its own work package.

## Derived research questions

Five thematic clusters guide visualisation priorities and identify gaps. Cluster letters are independent of Epic letters.

| Cluster | # | Question | Data | Addressed by |
|---------|---|----------|------|--------------|
| **Gender & legal agency** | A1 | Female participation asymmetry across roles over time | Complete | Epic A %-toggle |
| | A2 | Kinship framing of women (Hausfrau vs. Witib → legal agency) | Complete | Epic B + cross-epic link |
| | A3 | Occupation domains with higher female presence | Complete | Epic B heatmap |
| **Institutional landscape** | B1 | Recipient-type dominance shift over time | Complete | Epic C Panel 3 |
| | B2 | Organisations ranked by supporter network size | Complete | Epic C supporter tables |
| | B3 | Org type × transaction type correlation | Complete | New cross-tab |
| **Transaction practices** | C1 | Transaction-type repertoire evolution | Complete | Epic C Panel 1 |
| | C2 | Transaction type × social status of participants | Needs join | New aggregation |
| | C3 | Representation patterns (who represents whom; gendered?) | Complete | Directed rep view |
| **Social networks** | D1 | Most frequently appearing persons (urban-elite proxy) | Complete | Statistics top-persons |
| | D2 | Witness frequency vs. social connectivity | Needs join | New aggregation |
| | D3 | Friendship network structure | Complete | Epic B friend filter |
| **Topography** | E1 | Geographic clustering of transactions by type | Limited | Epic D + tx-type layer |

Not answerable with the current data: donation patterns over time (blocked by Q2), ecclesiastical/secular analysis (blocked by Q3), property transfer chains (transactiongoods table near-empty).

## Implementation status

Tracked in [../../db_for_medieval_legal_transactions/knowledge/status.md](../../db_for_medieval_legal_transactions/knowledge/status.md) (Digital Edition section). `python -m frontend status` prints a live milestone overview.
