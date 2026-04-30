# Design System — Digital Edition

Visual design system for the Wiener Urkundenbuch digital edition. Scholarly, warm, transparent. For UI components see `ui.md`. For the scholarly edition concept see `../../db_for_medieval_legal_transactions/knowledge/data.md`.

## Design Principles

1. **Scholarly gravity**: Serif typography, warm palette, generous whitespace — the edition must feel like a serious research tool, not a web app
2. **Epistemic transparency**: The data pipeline is visible, not hidden. Technical identifiers coexist with human-readable labels (two-layer UI, see `../../db_for_medieval_legal_transactions/knowledge/data.md`)
3. **Annotation without distraction**: Colour-coded highlights must be visible but never compete with the source text
4. **Desktop-first, print-aware**: Scholars work on large screens. Print output must be clean and usable

## Colour Palette

### Base Colours (parchment-inspired)

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg` | `#faf8f4` | Page background |
| `--color-bg-warm` | `#f5f1ea` | Table headers, hover states |
| `--color-bg-card` | `#ffffff` | Cards, document body |
| `--color-bg-nav` | `#2c2825` | Navigation bar |
| `--color-bg-footer` | `#37332f` | Footer |
| `--color-text` | `#2c2825` | Primary text |
| `--color-text-muted` | `#595550` | Secondary text (WCAG AA ≥4.5:1 on --color-bg) |
| `--color-text-light` | `#706b65` | Labels, placeholders (WCAG AA ≥4.5:1 on --color-bg) |
| `--color-border` | `#e0dbd4` | Primary borders |
| `--color-border-light` | `#ece8e2` | Subtle dividers |

### Annotation Colours (muted academic tones)

Designed for layered readability: background tints + bottom borders on entities, left borders on function roles.

| Annotation | Primary | Background | Border |
|------------|---------|------------|--------|
| Person | `#2e5a88` (slate blue) | `#e8f0f8` | `#b8d0e8` |
| Organisation | `#7b4d8e` (muted purple) | `#f2eaf6` | `#d4bce0` |
| Place | `#3a7a5c` (sage green) | `#e6f3ed` | `#b4d8c6` |
| Fn: Issuer | `#b85c2f` (burnt orange) | `rgba(184,92,47,0.06)` | — |
| Fn: Recipient | `#2e7a88` (teal) | `rgba(46,122,136,0.06)` | — |
| Fn: Witness | `#6b6040` (olive) | `rgba(107,96,64,0.06)` | — |
| Fn: Other | `#7a6b8c` (lavender) | `rgba(122,107,140,0.06)` | — |
| Triggerstring | `#8c5a2e` (warm brown) | — | — |
| Editorial add | `#5a7a3a` (moss green) | — | — |
| Attribute | `#6b6560` (warm grey) | — | — |

### Visualisation Colour Palette

Extends the annotation palette with chart-specific colours.

| Purpose | Token (proposed) | Hex | Usage |
|---------|-----------------|-----|-------|
| Male | `--color-sex-m` | `#2e5a88` | Reuse person blue |
| Female | `--color-sex-f` | `#b85c2f` | Reuse issuer orange |
| No sex data | `--color-sex-none` | `#b0a99f` | Warm grey, muted but visible |
| Ecclesiastical | `--color-inst-eccl` | `#7b4d8e` | Reuse org purple |
| Secular | `--color-inst-sec` | `#2e7a88` | Reuse recipient teal |
| Ambiguous | `--color-inst-ambig` | `#8c8680` | Neutral warm grey |
| Not normalised | `--color-not-norm` | `#d4cfc8` | Light warm grey, visually dominant area |
| Transmission gap | (hatched pattern) | `--color-border-light` | 45° diagonal lines |
| Relationship: kin | `--color-rel-kin` | `#c45a5a` | Muted red |
| Relationship: occ | `--color-rel-occ` | `#2e5a88` | Slate blue |
| Relationship: rep | `--color-rel-rep` | `#3a7a5c` | Sage green |
| Relationship: friend | `--color-rel-friend` | `#c4a035` | Warm gold |
| Relationship: none | `--color-rel-none` | `#b0a99f` | Warm grey |

Design rationale: Reuse existing annotation colours where semantics align (person=blue for male, org=purple for ecclesiastical). New colours only where no semantic match exists.

### Colour Logic

- **Entities** (person/org/place): Subtle background + 2px bottom border. These are the most important annotations — always visible inline
- **Function roles** (issuer/recipient/witness): 3px left border + very faint background. These frame groups of entities
- **Triggerstrings**: Bold text colour only (no background), to highlight dispositive verbs without visual noise
- **Editorial additions** (`<add>`): Italic + CSS-generated brackets `[...]` in light grey
- **Unclear text**: Wavy underline — standard philological convention

### CSS Architecture (DRY consolidation)

- **Entity annotations**: `.anno-person`, `.anno-org`, `.anno-place` share a grouped base selector (border-radius, padding, cursor, transition). Each only sets `background` + `border-bottom-color`
- **Function roles**: `.anno-fn` base class provides `border-left: 3px solid` + `padding-left`. Modifiers (`-issuer`, `-recipient`, `-witness`, `-other`) only set colour + background
- **Sidebar lists**: `.sidebar-dl` shared base for metadata and provenance definition lists (grid layout, typography)
- **Facsimile buttons**: shared selector for `.facs-controls button` and `.facs-zoom-controls button`
- **Section labels**: `.tei-seal::before` and `.tei-nota::before` share a grouped pseudo-element selector

## Typography

### Font Stack

| Role | Font | Fallback | Weight |
|------|------|----------|--------|
| Body text | Crimson Pro | Georgia, Times New Roman, serif | 400 (regular), 500 (medium), 600 (semibold) |
| UI elements | Inter | -apple-system, Segoe UI, sans-serif | 300–600 |
| Technical IDs | JetBrains Mono | Consolas, monospace | 400 |

### Scale

| Token | Size | Usage |
|-------|------|-------|
| `--text-2xs` | 0.6875rem (11px) | Meta labels, timeline labels, seal/nota pseudo-elements |
| `--text-xs` | 0.8125rem (13px) | Labels, technical IDs, breadcrumbs |
| `--text-sm` | 0.875rem (14px) | Table cells, secondary text |
| `--text-base` | 1.0625rem (17px) | Body text, metadata values |
| `--text-lg` | 1.25rem (20px) | Subtitles |
| `--text-xl` | 1.5rem (24px) | Page headings (mobile) |
| `--text-2xl` | 2rem (32px) | Page headings (desktop) |

### Line Heights

- Body text: `1.85` — generous for readability of dense medieval German
- Headings: `1.3` — tight for visual weight

### Typographic Conventions

- **Meta labels**: Sans-serif, uppercase, 0.6875rem, letter-spacing 0.06em — creates clear hierarchy without bold
- **Original dates**: Italic serif — signals historical language
- **Citations**: Smaller, muted colour — visually subordinate
- **Technical IDs / paths**: Monospace, smaller — distinct from content

## CSS Architecture: DRY Consolidation

### Card Surface (`components.css`, grouped selector)
`.doc-body`, `.facs-viewer`, `.index-table-wrap`, `.stats-chart-card`, `.stats-collection-card`, `.stats-kpi`, `.explore-panel`, `.explore-hub-card`, `.explore-header-unified`, `.explore-filter-header`, `.start-entry-card` share: `background: var(--color-bg-card)`, `border`, `border-radius: var(--radius-lg)`, `box-shadow: var(--shadow-sm)`. Each component only adds its own rules (padding, overflow).

### Tooltip Base (`components.css`, grouped selector)
`.edition-tooltip`, `.stats-tooltip`, `.explore-tooltip` share: `position: fixed`, `z-index: var(--z-tooltip)`, `background: var(--color-bg-nav)`, `color: var(--color-text-inverse)`, `pointer-events: none`, `opacity: 0`, `transition`. When visible (`.visible`): `pointer-events: auto` (WCAG 1.4.13 — tooltip is hoverable and persistent). Each tooltip class only adds type-specific rules (font-size, padding, max-width).

### Chip Base (grouped selector)
`.chip`, `.chip-active`, `.filter-chip` share: `display: inline-flex`, `align-items`, `gap`, `border`, `border-radius: 1rem`, `font-family: var(--font-sans)`. Variants only override padding, background, font-size, colour.

### Print Styles (single merged block)
All `@media print` rules consolidated into one block at end of file (document + guidelines).

## Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 0.25rem | Inline gaps |
| `--space-sm` | 0.5rem | Tight padding |
| `--space-md` | 1rem | Standard padding |
| `--space-lg` | 1.5rem | Section spacing |
| `--space-xl` | 2.5rem | Major sections |
| `--space-2xl` | 4rem | Page-level spacing |

## Transition & Z-Index Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--transition-fast` | 0.15s | Hover effects, tooltips, all interactive elements |
| `--transition-normal` | 0.2s | Preview animation |
| `--z-nav` | 100 | Sticky navigation bar |
| `--z-sidebar` | 200 | Off-canvas sidebar |
| `--z-tooltip` | 1000 | Entity hover tooltips |

## Layout Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--max-width` | 52rem | Text-only readable width |
| `--max-width-wide` | 90rem | Synopsis layout + index page |
| `--sidebar-width` | 22rem | Off-canvas sidebar |

## Responsive Breakpoints

| Width | Adjustments |
|-------|------------|
| > 1024px | Full synopsis layout (text + facsimile side by side) |
| ≤ 1024px | Synopsis stacks (text above facsimile), facs panel not sticky |
| ≤ 768px | Toolbar not sticky, inline paging hidden, sidebar full-width, table h-scroll, preview thumb hidden |
| ≤ 480px | Single-column legend, stacked collection chips |

## Print Stylesheet

- Hidden: navigation, footer, toolbar, sidebar, facsimile panel, paging, active filters
- Shown: `doc-print-meta` block (Nr., date, place, archive, citation)
- White background, 11pt body text
- Annotations: no backgrounds, 1px solid underlines
- Function roles: no left borders or backgrounds
- No shadows or rounded corners

## Exploration Responsive Behaviour

| Width | Layout |
|-------|--------|
| > 1200px | Panels side by side (CSS grid `1fr 1fr` or `1fr 1fr 1fr`) |
| ≤ 1200px | Panels stack vertically, full width |
| ≤ 768px | Filter header collapses to expandable accordion; panels stack vertically; heatmap scrollable horizontally |
| ≤ 480px | Chart legends stack vertically; table columns reduce to essentials (name, count) |

## Exploration Accessibility

Every complex visualisation has a tabular alternative accessible via a toggle ("Tabellenansicht / Diagrammansicht"):

| Visualisation | Alternative |
|--------------|-------------|
| Role bars (A) | Table: role × sex × count |
| Relationship heatmap (B) | Heatmap cells are keyboard-navigable; drill-down tables provide tabular alternative |
| Recipient bar chart (C) | Table: type × institution × recipient count, sortable |
| Map (D) | Panel 2 (place register table) already serves as alternative |

Screen reader: `aria-label` on all SVG charts (always set, fallback "Balkendiagramm"), `role="img"`. Sort headers have `aria-sort` (ascending/descending/none). Drill-down overlays have focus trap + focus restore.

## WCAG 2.1 AA Compliance (Session 41)

Accessibility fixes applied across the entire edition:

| Category | Implementation |
|----------|---------------|
| **Colour contrast** | `--color-text-muted` darkened to #595550, `--color-text-light` to #706b65 (both ≥4.5:1 on parchment bg) |
| **Focus visible** | Global `:focus-visible` rule (2px solid `--anno-person`), nav-specific override for dark bg |
| **Screen-reader utility** | `.sr-only` class in `base.css` (visually hidden, accessible to AT) |
| **Search labels** | `<label class="sr-only">` on all search inputs via `search_box` macro |
| **SVG charts** | `aria-label` always set on `<svg>` (was conditional). Decorative icons get `aria-hidden="true"` |
| **Sort headers** | `aria-sort` attribute updated dynamically in `bindSortHeaders()` |
| **Drill-down overlay** | Focus trap (Tab cycles within dialog), focus moved to close button on open, previous focus restored on close |
| **Tooltip persistence** | `pointer-events: auto` when `.visible` (WCAG 1.4.13 hoverable), hover-persistence via mouseenter/mouseleave, Escape-to-dismiss |
| **Touch targets** | `min-height: 2.75rem` (44px) on chips, alphabet buttons, toolbar buttons at ≤768px |
| **Table scroll** | Gradient scroll-shadow indicator on `.index-table-wrap` horizontal overflow |
| **Reduced motion** | `@media (prefers-reduced-motion)` disables all animations/transitions |

## CSS Architecture (Phase I additions)

**File split:** Monolithic `style.css` → 12 files in `frontend/static/css/`. Each page template loads `tokens.css` + `base.css` + `components.css` (via `base.html`) plus page-specific files via `{% block head %}`.

**New files (Session 39):**
- `components.css` — consolidated card-surface (11 selectors) and tooltip-base (3 selectors) patterns, loaded in `base.html` after `base.css`

**New CSS tokens (Session 39):** `--color-bg-hover`, `--color-bg-alt`, `--radius-sm`, `--color-accent`, `--color-primary`, `--color-sex-m-muted`, `--color-sex-f-muted`, `--color-quality-ok/notice/warning`, `--color-rel-kin/occ/rep/friend`

**JS architecture (Sessions 39–40):** `exploration.js` split into 4 files: `exploration-roles.js` (Epic A), `exploration-transactions.js` (Epic C), `exploration-places.js` (Epic D), `exploration-networks.js` (Epic B). Session 40 extended `chart-helpers.js` with 7 shared functions (`loadJSON`, `bindTimeRange`, `bindChipFilter`, `bindToggle`, `bindSearch`, `bindSortHeaders`, `renderHorizontalBars`), significantly reducing duplication across all 4 exploration files. Shared label/colour maps in `ChartHelpers` (`ROLE_LABELS`, `ROLE_ORDER`, `SEX_LABELS`, `sexColors()`, `updateRangeFill()`). All fetch() calls have `.catch()` error handling.

**Dual-handle range slider:** Two `<input type="range">` overlaid on a single track (`.explore-range-track`) with a coloured fill element (`.explore-range-fill`). `ChartHelpers.updateRangeFill(idPrefix)` positions the fill bar as a percentage. Used by all 4 exploration pages via `time_range_slider()` Jinja2 macro.

See `ui.md` § JS Architecture for full namespace hierarchy and dependency map.
