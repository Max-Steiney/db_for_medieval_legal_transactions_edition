# UI Components and Interaction Patterns

Component inventory, templates, and JS modules for the digital edition.

## Information Seeking Mantra

**"Overview first, zoom and filter, then details-on-demand"**

### Index Page (overview + filter)

- **Corpus summary line**: document/person/org counts + date range
- **Dual-handle range slider**: histogram background (decade bars) + two overlaid `<input type="range">` for min/max year filtering. Labels track handle positions dynamically
- **Collection chips**: inline pills replacing large cards, click to toggle filter
- **Faceted filters**: place dropdown (top 15), facsimile (with/without), text search (multi-word AND)
- **Active filter chips**: removable pills showing current filters
- **Progressive table rendering**: IntersectionObserver loads 100 rows at a time (no hard cap)
- **Row preview (details-on-demand)**: click row to expand inline preview with full regest + facsimile thumbnail

### Document Page (Text-Bild-Synopse)

- **Synopsis layout**: text + facsimile side by side as default view (CSS grid `1fr 1fr`), no tab switching needed
- **Compact toolbar** (sticky below nav): breadcrumb, Nr. + date + place, inline prev/next
- **Facsimile panel**: always visible for documents with facsimile URLs (79%), sticky position, lazy-loaded images, page navigation, zoom/pan
- **Compact details section** (below content): metadata (Archiv, Originaldatierung, Quelle, Digitalisat link) + annotation legend in two-column grid
- **No-facsimile fallback** (21%): single column, text body centred at `max-width: 52rem`
- **Prev/next navigation**: inline in toolbar + bottom of page
- **Print metadata**: hidden `<div class="doc-print-meta">` block, shown only in `@media print`

### Register Pages

- **List pages** (`persons.html`, `organisations.html`, `places.html`): alphabet bar, search, type/docs filter, sortable table, progressive rendering. JSON data fetched asynchronously from `docs/data/` files (externalized for performance).
- **Inline detail expansion**: clicking an entity name (or doc count) lazy-loads a JSON file and expands a detail row showing all linked documents as clickable links. Entries with 0 documents are visually muted and not clickable.
- **Bidirectional linking**: document annotations (`<a class="anno-person">`) link to register pages with hash fragments (e.g. `persons.html#pe__xyz`), which auto-expand the entity's detail row on arrival.
- **3 JSON files** in `docs/register/`: `persons.json`, `organisations.json`, `places.json` — compact reverse-index data with keys `u` (url), `i` (idno), `d` (date_display), `c` (collection_label), `r` (regest).

## Edition Components

### Navigation Bar
- Fixed (sticky) at top, dark background (`#2c2825`), `z-index: var(--z-nav)`
- Brand: Serif font + Unicode sigil (&#10070;) + uppercase subtitle "DIGITAL EDITION"
- Height: 3.5rem
- **3 dropdowns**: Register (Personen, Organisationen, Orte), Exploration (Übersicht, Rollen, Transaktionen, Beziehungen, Orte), Projekt (Statistik, Editionsrichtlinien). CSS `.nav-dropdown` with absolute-positioned `.nav-dropdown-menu`. Escape-to-close, outside-click-to-close
- **Brand** links to Startseite (`index.html`), "Dokumente" links to `documents.html`

### Index Page — Corpus Overview

**Corpus summary line**: one-line stats ("3.041 Quellen, 16.084 Personen, 1.078 Organisationen — Wien, ca. 1177–1524")

**Dual-handle range slider**: Replaces the old SVG bar chart. Mini-histogram background (5rem height, `--anno-person` bars), two overlaid `<input type="range">` for min/max year selection. Features: crossing prevention, dynamic label positioning (labels track handles via JS percentage calc), track fill between handles, histogram bar opacity reflects selection (in-range 70%, out-of-range 12%, default 35%). Thumbs: 18px circles, `--anno-person` colour, hover halo. Year labels follow handle positions with `transform: translateX(-50%)`.

**Collection chips**: inline pill buttons replacing the old large cards. 1px border, 1rem border-radius. Active state: blue border + tint. Click toggles collection filter.

**Faceted filters**: place dropdown (top 15 places), facsimile dropdown (with/without), text search with icon. Active filters shown as removable chips below.

### Index Table
- Sortable columns (click headers, arrow indicators up/down)
- Hover highlight + alternate row shading (`nth-child(even)`)
- Truncated regest column (2-line clamp with `-webkit-line-clamp`)
- Progressive rendering via `IntersectionObserver` (100 rows per batch, no hard cap)
- **Row preview**: click row to expand inline detail (full regest, metadata, facsimile thumbnail). Keyboard accessible (`tabindex`, Enter/Space).
- Preview animation: 0.2s ease-out fade-in

### Document Toolbar (sticky)
- Sticky below nav bar (`top: 3.5rem`, `z-index: var(--z-nav) - 1`)
- Left: breadcrumb + "Nr. X / date / place" (serif, inline)
- Right action buttons (left to right): TEI download, quality badge, annotation toggle, factoid view, citation helper, inline prev/next
- Toolbar buttons: 2rem square, border, hover accent. Mobile (≤768px): min-height 2.75rem (WCAG 44px touch target)
- Mobile (< 768px): not sticky, wraps, inline paging hidden

### TEI-XML Download (M1)
- Download button in toolbar with `download` attribute for browser-native download
- Links to static copy at `docs/tei/{collection}/{file}.xml`
- Build step `_copy_tei_sources()` copies all done files during `python -m frontend build`

### Quality Strip (M1)
- Colour-coded badge button in toolbar (green/yellow/orange via `--color-quality-ok/notice/warning`)
- Click expands `.quality-panel` section with server-rendered findings table (severity, category, detail)
- Score 0: "Keine Auffälligkeiten" message. Score 1/2: findings table with severity badges
- Quality score also in doc-meta JSON for client-side access

### Annotation Layer Toggle (M1)
- Toggle button (&#x25CE;) in toolbar opens `.anno-toggle-popover` dropdown
- 4 checkboxes: entities (person/org/place), functions (roles), attributes (roleName), triggers (dispositive verbs)
- "Alle ein/aus" button toggles all layers simultaneously
- State persisted in `localStorage` key `wub-anno-layers`
- CSS: body-level classes `.hide-entities/.hide-functions/.hide-attributes/.hide-triggers` on `.doc-body`
- Popover: same open/close pattern as citation helper (click, click-outside, Escape)
- Mobile (≤768px): popover stretches full-width

### Synopsis Layout (Text-Bild-Synopse)
- Default view: text + facsimile side by side (CSS grid `1fr 1fr`, `max-width: 90rem`)
- No tab switching — facsimile always visible for documents with facsimile URLs (79%)
- No-facsimile fallback (21%): single column, text centred at `max-width: 52rem`
- Breakpoint: stacks at <= 1024px

### Facsimile Panel
- Always visible in synopsis, `position: sticky; top: 7rem`
- First image loads immediately on init (no tab activation needed)
- Page navigation (prev/next) for multi-page documents
- Zoom controls: +, -, 1:1 reset. Mouse wheel zoom on image wrap
- CSS transform zoom (no library), `transform-origin: center`

### Sidebar (off-canvas metadata)
- Off-canvas overlay from right, width `var(--sidebar-width)` (22rem)
- `z-index: var(--z-sidebar)` (200), semi-transparent overlay backdrop
- Sections: metadata (`<dl>`), annotation legend, provenance
- Triggered by toolbar [i] button (scrolls to metadata) or [?] button (scrolls to legend)
- Close: x button, overlay click, Escape key
- Mobile (< 768px): full-width sidebar

### Prev/Next Navigation
- Inline in toolbar (compact, small font) + bottom of page
- Styled as bordered links with hover transition

### Annotation Legend (in sidebar)
- CSS grid of colour swatches with labels
- Swatches mirror actual annotation styles (border patterns match rendering)
- No collapsible toggle — always visible inside sidebar

### Provenance Block (in sidebar)
- "Datenherkunft" section inside sidebar
- Definition list: source file, collection, registers, renderer

### Print Metadata
- Hidden `<div class="doc-print-meta">` — shown only in `@media print`
- Contains: Nr., date, place, archive, citation

### Document Body
- White card with generous padding (2.5rem horizontal)
- Justified text with CSS hyphens
- Annotation spans are inline — no layout disruption

### Tooltips (JS-enhanced)
- Dark background (`#2c2825`), sans-serif, `z-index: var(--z-tooltip)`
- Type badge (coloured pill: Person / Organisation / Ort)
- Name in regular weight, ID in monospace below
- Positioned near cursor, viewport-aware
- `var(--transition-fast)` fade-in transition

### Register List Pages (persons/organisations/places)
- Same layout pattern as index page (`.index-page.register-page`)
- **Alphabet bar**: 26 letter buttons + "Alle" toggle. `.alpha-btn` inline pills, active state with `--anno-person` colour
- **Search/filter bar**: shared `search_box` macro, type/sex dropdown, docs dropdown (with/without documents)
- **Sortable table**: name, sex/type, death/type, doc count, ID. Progressive rendering via shared `createTableRenderer()`
- **Entity type badges**: `.entity-type-badge` coloured pills (person blue, org purple, place green)
- **Doc count badge**: `.doc-count-badge` with zero-state variant (`.doc-count-zero` muted)

### Register Inline Detail Expansion (JSON + JS)
- **Clickable names**: entities with documents render as `<button class="register-name-linked">` (blue, bold); entities with 0 documents render as `<span class="register-name">` (muted)
- **Doc-count badge**: also clickable (`<button class="doc-count-link">`) for entities with documents
- **Detail row**: `<tr class="detail-row">` inserted below clicked row, colspan full table width. Contains document table (Nr. linked, date, collection, regest). Slide-in animation via `@keyframes detailSlide`
- **Lazy JSON loading**: 3 files in `docs/register/` (`persons.json`, `organisations.json`, `places.json`) loaded on first click via XHR, cached in memory
- **Deep-linking**: hash fragments (e.g. `persons.html#pe__xyz`) auto-expand the matching entity on page load

**Note on JSON data sources:** Register pages use `docs/register/{persons,organisations,places}.json` for entity-to-document reverse-index data (compact format with keys `u`, `i`, `d`, `c`, `r`). Exploration pages use a separate `docs/data/docs_lookup.json` (file_key → edition URL mapping) loaded by the `DrillDown` module for drill-down overlays. Both mechanisms lazy-load their JSON on first interaction.

## Exploration Components

### Exploration Hub (`exploration.html`)

Entry point for all four Epics. Card grid layout (`.explore-hub-card`) with one card per Epic:

- **Card structure**: Title, status badge ("Verfügbar" / "In Entwicklung"), short description, link to Epic subpage
- **Status badges**: green for available, grey for in-development
- **Layout**: CSS grid, 2 columns on desktop, stacks on mobile
- **Cards link to**: `exploration_roles.html` (Rollen), `exploration_transactions.html` (Transaktionen), `exploration_networks.html` (Beziehungen), `exploration_places.html` (Orte)

### Exploration Page Layout

Each Epic occupies one page (or tab section) with a consistent structure:

```
+-----------------------------------------------------+
|  Filter Header (time slider, sex filter, ...)       |
+-----------------------------------------------------+
|  Transparency Bar (data basis, coverage, caveats)   |
+--------------+--------------+-----------------------+
|  Panel 1     |  Panel 2     |  Panel 3              |
|  (chart)     |  (table/     |  (detail/             |
|              |   browser)   |   profile)            |
+--------------+--------------+-----------------------+
```

- Panels use the existing `.doc-body` card surface (white card, border, shadow)
- Panel headers use `--text-lg` sans-serif, with a subtle bottom border
- Empty/inactive panels show a centred hint text in `--color-text-muted`
- Panel-to-panel interaction: active selection highlighted with `--anno-person` accent

### Unified Header Pattern

All active exploration pages (Rollen, Transaktionen, Orte) use a unified compact header pattern (`.explore-header-unified`):

- **Row 1:** Title (h1) + inline stats + time slider (right-aligned)
- **Row 2:** Filter controls (search, dropdowns, toggles)

The time slider is a dual-handle range slider (1170-1520, step 10 decades) with a gap note that appears when the selected range touches the 1418-1447 transmission gap. It applies to all panels of the current Epic.

**Time semantics for Places (Epic D):** Places inherit time from events via the `places_in_events` -> `events_in_sources` join. Places without computable decades are always shown regardless of slider position. When the slider is narrowed, only places with at least one decade in range remain visible.

All active exploration pages use `.explore-header-unified` — a compact header replacing the previous three-block layout (`.explore-header--compact` + `.explore-filter-header` + `.explore-transparency`). Structure:

```
.explore-header-unified
  .explore-header-row          -> flex row: title+stats left, time slider right
    .explore-header-title
      h1                       -> page name (e.g. "Rollen", "Orte")
      .explore-header-stats    -> inline coverage metrics
    .explore-header-time
      .explore-range-wrap      -> dual-handle slider (min/max inputs)
      .explore-range-display   -> "1170-1520" label
      .explore-gap-note        -> "Luecke 1418-1447" (shown conditionally)
  .explore-header-controls     -> second row: filters, search, dropdowns
    .explore-filter-group
```

At <=768px: header row stacks vertically, time slider moves below title.

### Filter Header Component

Reusable across Epics A, B, C. Not used in Epic D (too few data points for meaningful filtering).

- Full-width card below page heading
- Contains: time range slider (reuse `initRangeSlider()` pattern), categorical filters as pill-shaped toggles (reuse `.chip` base)
- Transmission gap 1418-1447: hatched band on time axis with "Ueberlieferungsluecke" label in `--text-2xs`
- Normalisation rate indicator: persistent badge in `--color-not-norm` background with percentage, next to transaction type filter
- Gap warning: appears dynamically when selected range overlaps gap ("X Jahre ohne Ueberlieferung im gewaehlten Zeitraum")

### Drill-Down Pattern

Consistent across all Epics. Click aggregated element -> overlay with document table (progressive rendering, sortable columns: Nr., Date, Collection, Regest). Close via button/Escape. CSV export in footer. Shared module: `DrillDown` namespace in `drill-down.js`, `drill_down_overlay()` Jinja2 macro.

Consistent across all Epics. When clicking an aggregated element (bar segment, heatmap cell, map marker, table row) that leads to a document list:

1. Overlay/modal with document table (reuse index table pattern: progressive rendering, sortable columns)
2. Columns: Nr. (linked), Date, Collection, Regest (truncated)
3. Close button + Escape key
4. "Export" button in overlay footer (CSV download of listed documents)
5. CSS: `.drill-down-overlay` with `--z-sidebar` z-index, semi-transparent backdrop

### Chart Components

**Horizontal bar chart** (Epic A Panel 1, Epic A Panel 3, Epic C Panel 3 detail):
- Bars use `border-radius: 2px` on the value end
- Label left-aligned outside bar, value right-aligned inside bar (or outside if bar too short)
- Grouped bars: `gap: 2px` between segments, `gap: var(--space-sm)` between groups
- Hover state: bar brightens slightly, tooltip with absolute count + percentage

**Stacked bar chart** (Epic C Panel 1):
- Vertical orientation, decades on x-axis
- Legend as inline chips above chart (reuse `.chip` base)
- "Not normalised" segment uses `--color-not-norm` (dominant, ~85%)
- Transmission gap decades: hatched pattern, no data bars

**Horizontal bar chart — Institutional Recipients** (Epic C Panel 3, implemented):
- Bars per organisation type, sorted by frequency (484 institutions, ~20 types)
- Click bar -> institution detail overlay -> supporter table
- Design decision: horizontal bar chart instead of treemap (spec suggested treemap). Simpler, more readable, no d3-hierarchy dependency.

**Grouped bar chart** (Epic B Panel 1):
- Horizontal grouped bars: relationship types × sex
- Bars use `border-radius: 2px`, same pattern as Epic A Panel 1
- Colours per sex category (`--color-sex-*`), consistent with Epic A
- Hover: absolute count + percentage tooltip
- Click: drill-down to person list via DrillDown overlay

**Label heatmap** (Epic B Panel 2):
- Paginated grid: top 20 relationship labels by frequency, "Alle anzeigen" expands to full set
- 93 label variants merged via normalisation
- Columns: relationship type categories (kin, occ, rep, friend, etc.)
- Cell colour intensity encodes frequency (CSS opacity or colour scale)
- Conditional "Keine Angabe" column (shown only when data exists)
- Row highlight on person search match
- Click cell: drill-down to documents
- Sticky Panel 1 above heatmap for context

**Map** (Epic D Panel 1):
- Leaflet.js with OpenStreetMap tiles
- Marker colours: place type palette (reuse `--anno-place` green base, variants by type)
- Cluster circles: `--color-bg-warm` background with count label
- Coverage statistic: top-right overlay card, same style as corpus summary line

## Templates (Jinja2 Macros)

### Jinja2 Macros (`macros.html`)

| Macro | Parameters | Usage |
|-------|------------|-------|
| `doc_nav(meta, root_path, extra_class)` | prev/next links | Toolbar inline + bottom navigation |
| `external_icon()` | — | SVG icon for external links (details section) |
| `search_box(placeholder)` | Placeholder text | Search input + icon + clear button (index + register) |
| `result_count(count, label)` | Count + label text | Result counter display (index + register) |
| `active_filters()` | — | Active filters container (JS-managed) |
| `no_results(message)` | Message text | No-results fallback (index + register) |
| `json_data(script_id, data_json)` | Script ID + JSON | Embedded search data script tag |
| `drill_down_overlay(id_prefix, wide)` | Element ID prefix, wide flag | Reusable drill-down document overlay (table + CSV export) |

## JS Architecture

**No bundler.** Each JS file uses IIFE pattern, exposing a namespaced global. Files are loaded via `<script>` tags in the correct dependency order. The publication repository serves via GitHub Pages over HTTP/2, so multiple small requests are efficient.

**Namespace hierarchy:**

| Namespace | File | Depends on | Purpose |
|-----------|------|------------|---------|
| `EdCore` | `core.js` | — | Nav, `esc()` utility, base infrastructure |
| `TableInfra` | `table-infra.js` | `EdCore` | Shared table rendering, search, sort, filters |
| `ChartHelpers` | `chart-helpers.js` | — | SVG factory (`svgEl`), CSS token reader (`getToken`), tooltip system (`createTooltip`/`showTooltip`/`moveTooltip`/`hideTooltip`), number formatting (`fmt`), shared label/colour maps (`ROLE_LABELS`, `ROLE_ORDER`, `SEX_LABELS`, `sexColors()`), range slider (`updateRangeFill`), shared UI helpers (`loadJSON`, `bindTimeRange`, `bindChipFilter`, `bindToggle`, `bindSearch`, `bindSortHeaders`, `renderHorizontalBars`) |
| `DrillDown` | `drill-down.js` | `EdCore`, `ChartHelpers` | Document drill-down overlay, lazy docs_lookup.json, CSV export |

**Page-specific modules** (no global namespace, use `init*()` entry points):

| Function | File | Dependencies |
|----------|------|-------------|
| `initIndex()` | `index.js` | `EdCore`, `TableInfra` |
| `initRegister()` | `register.js` | `EdCore`, `TableInfra` |
| `initStatistics()` | `statistics.js` | `EdCore`, `ChartHelpers` |
| `initExploration()` | `exploration-roles.js` | `EdCore`, `ChartHelpers`, `DrillDown` |
| `initTransactionExplorer()` | `exploration-transactions.js` | `EdCore`, `ChartHelpers`, `DrillDown` |
| `initNetworkExplorer()` | `exploration-networks.js` | `EdCore`, `ChartHelpers`, `DrillDown` |
| `initPlaceExplorer()` | `exploration-places.js` | `EdCore`, `ChartHelpers`, `DrillDown` |
| `initFactoidView()` | `document.js` | `EdCore` |
| `initCitationHelper()` | `document.js` | `EdCore` |
| `initQualityPanel()` | `document.js` | `EdCore` |
| `initAnnotationToggle()` | `document.js` | `EdCore` |
| `initGuidelines()` | `content.js` | `EdCore` |

**CSS token hygiene:** JS chart code reads colours from CSS custom properties via `ChartHelpers.getToken('--token-name')` with hardcoded fallbacks, ensuring design system changes propagate to SVG charts.
