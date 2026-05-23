// Exploration / Zeitstrom: stacked bar chart of source density per decade.
// Stack axis selectable (corpus / form of treatment / sex / transaction type).
// Brush picks a decade range -> drill-down source list.
// Shared infrastructure comes from VizCore (viz-core.js).
(function () {
    'use strict';

    const V = VizCore;

    // ---------------------------------------------------------------------
    // Stack definitions
    // ---------------------------------------------------------------------
    const STACKS = {
        collection: {
            label: 'Quellenkorpus',
            categories: [
                { key: 'QGW',          label: 'QGW',         color: '#b85c2f' },
                { key: 'Stadtbuecher', label: 'Stadtbücher', color: '#2e7a88' },
            ],
            assign: (doc) => doc.c || 'OTHER',
        },
        form: {
            label: 'Erschließungsform',
            categories: [
                { key: 'R', label: 'Regest',  color: '#2e7a88' },
                { key: 'S', label: 'Siegel',  color: '#6b6040' },
                { key: 'E', label: 'Eintrag', color: '#b85c2f' },
                { key: 'N', label: 'Nota',    color: '#a08470' },
            ],
            // Multiple forms per source possible; we count the source
            // multiple times (once per present form).
            multi: true,
            assignAll: (doc) => {
                const out = [];
                if (doc.ecR > 0) out.push('R');
                if (doc.ecS > 0) out.push('S');
                if (doc.ecE > 0) out.push('E');
                if (doc.ecN > 0) out.push('N');
                return out;
            },
        },
        sex: {
            label: 'Geschlecht der Beteiligten',
            categories: [
                { key: 'mixed', label: 'gemischt',         color: '#7a6b8c' },
                { key: 'm',     label: 'nur ♂ männlich',   color: '#5d3a74' },
                { key: 'f',     label: 'nur ♀ weiblich',   color: '#2d6650' },
                { key: 'none',  label: 'ohne Personen',    color: '#9a9590' },
            ],
            assign: (doc) => {
                const m = doc.pcdm || 0;
                const f = doc.pcdf || 0;
                if (m === 0 && f === 0) return 'none';
                if (m > 0 && f === 0) return 'm';
                if (f > 0 && m === 0) return 'f';
                return 'mixed';
            },
        },
        // Transaction type needs its own data source (transactions.tx_timeline);
        // handled separately in the renderer and not derived from search.json.
        tx: {
            label: 'Transaktionstyp',
            categories: [],  // populated dynamically
            fromTransactions: true,
        },
    };

    const TX_TOP_N = 8;
    const TX_PALETTE = [
        '#b85c2f', '#2e7a88', '#6b6040', '#a08470',
        '#c4a035', '#5d3a74', '#2d6650', '#7a6b8c',
        '#9a9590',
    ];

    // ---------------------------------------------------------------------
    // Data loading
    // ---------------------------------------------------------------------
    const TRANSACTIONS = V.readJsonScript('exploration-data-transactions', { observations: {} });
    let DOCS = [];
    let DOCS_BY_DECADE = new Map();
    let DOCS_LOOKUP = {};   // file_key -> doc base record (lazy, for tx drill)

    // ---------------------------------------------------------------------
    // Filter state
    // ---------------------------------------------------------------------
    const STATE = {
        decadeMin: null,
        decadeMax: null,
        stack: 'collection',
        brushMin: null,
        brushMax: null,
        stackFocus: null,   // null = all categories, otherwise category key
        drillSort: 'date-asc',  // 'date-asc' | 'date-desc' | 'coll'
    };
    const decFilter = V.makeDecadeFilter(STATE);

    // ---------------------------------------------------------------------
    // Aggregation
    // ---------------------------------------------------------------------
    function aggregate() {
        const stackDef = effectiveStackDef();
        const categories = stackDef.categories;
        const values = {};
        const totals = {};

        // Collect decades in filter; initialise values/totals only for those —
        // out-of-range docs are filtered in the doc loop below via the
        // values[dec] lookup. We then expand the decade list to be
        // contiguous (1170, 1180, 1190, …) so empty decades show up as
        // zero-height columns rather than being silently dropped — the
        // time axis stays metrically meaningful.
        const decadesSet = new Set();
        for (const doc of DOCS) {
            const dec = doc._dec;
            if (dec === null) continue;
            if (!decFilter.contains(dec)) continue;
            decadesSet.add(dec);
        }
        if (STATE.stack === 'tx') {
            const tl = (TRANSACTIONS.observations || {}).tx_timeline || {};
            for (const byDec of Object.values(tl)) {
                for (const d of Object.keys(byDec)) {
                    const dec = parseInt(d, 10);
                    if (decFilter.contains(dec)) decadesSet.add(dec);
                }
            }
        }
        let decades = Array.from(decadesSet).sort((a, b) => a - b);
        if (decades.length >= 2) {
            const lo = decades[0], hi = decades[decades.length - 1];
            decades = [];
            for (let d = lo; d <= hi; d += 10) decades.push(d);
        }
        for (const d of decades) {
            values[d] = {};
            for (const c of categories) values[d][c.key] = 0;
            totals[d] = 0;
        }

        if (STATE.stack === 'tx') {
            // Special case: aggregate from transactions.tx_timeline. Decades that
            // appear there but not in DOCS are added on top (tx data is
            // independent of the doc set).
            const tl = (TRANSACTIONS.observations || {}).tx_timeline || {};
            for (const cat of categories) {
                const byDec = tl[cat.key] || {};
                for (const [d, c] of Object.entries(byDec)) {
                    const dec = parseInt(d, 10);
                    if (!decFilter.contains(dec)) continue;
                    if (!values[dec]) {
                        values[dec] = {};
                        for (const cc of categories) values[dec][cc.key] = 0;
                        totals[dec] = 0;
                        if (!decades.includes(dec)) {
                            decades.push(dec);
                            decades.sort((a, b) => a - b);
                        }
                    }
                    values[dec][cat.key] = (values[dec][cat.key] || 0) + c;
                    totals[dec] += c;
                }
            }
        } else {
            for (const doc of DOCS) {
                const dec = doc._dec;
                if (dec === null) continue;
                if (!values[dec]) continue;
                if (stackDef.multi) {
                    const keys = stackDef.assignAll(doc);
                    for (const k of keys) {
                        if (values[dec][k] !== undefined) {
                            values[dec][k]++;
                            totals[dec]++;
                        }
                    }
                } else {
                    const k = stackDef.assign(doc);
                    if (values[dec][k] !== undefined) {
                        values[dec][k]++;
                        totals[dec]++;
                    }
                }
            }
        }

        return { decades, categories, values, totals };
    }

    // Returns the effective stack definition (for 'tx' it builds the
    // top-N categories dynamically from transactions).
    function effectiveStackDef() {
        const def = STACKS[STATE.stack];
        if (STATE.stack !== 'tx') return def;

        const tl = (TRANSACTIONS.observations || {}).tx_timeline || {};
        const totals = {};
        for (const [type, byDec] of Object.entries(tl)) {
            if (type === '_not_normalised') continue;
            let s = 0;
            for (const c of Object.values(byDec)) s += c;
            if (s > 0) totals[type] = s;
        }
        const sorted = Object.entries(totals).sort((a, b) => b[1] - a[1]);
        const top = sorted.slice(0, TX_TOP_N);
        const cats = top.map(([k], i) => ({
            key: k, label: V.labelize(k), color: TX_PALETTE[i],
        }));
        return Object.assign({}, def, { categories: cats });
    }

    // ---------------------------------------------------------------------
    // Renderer
    // ---------------------------------------------------------------------
    function renderChart() {
        const chart = document.getElementById('stream-chart');
        const yax = document.getElementById('stream-yaxis');
        const heading = document.getElementById('stream-axis-heading');
        if (!chart) return;

        const agg = aggregate();
        const { decades, categories, values, totals } = agg;
        const maxTotal = decades.reduce((m, d) => Math.max(m, totals[d]), 1);

        const stackDef = effectiveStackDef();
        if (heading) {
            heading.textContent = (STATE.stack === 'tx')
                ? `Rechtsgeschäfte pro Jahrzehnt — Top ${categories.length} Transaktionstypen`
                : `Quellen pro Jahrzehnt — Stapel: ${stackDef.label}`;
        }

        if (yax) {
            const ticks = [0, Math.round(maxTotal * 0.5), maxTotal];
            yax.innerHTML = ticks.reverse().map(t =>
                `<span class="explore-stream-ytick">${V.fmt(t)}</span>`
            ).join('');
        }

        const inactive = STATE.brushMin !== null;
        const focus = STATE.stackFocus;
        const cols = decades.map(d => {
            const dimmed = inactive && (d < STATE.brushMin || d > STATE.brushMax);
            const segs = categories.map(c => {
                const v = values[d][c.key] || 0;
                if (v === 0) return '';
                // hpx kann sub-pixel werden (1 Doc in einem 700er-Maximum).
                // Wir geben dem Renderer trotzdem den proportionalen Wert
                // und lassen die CSS min-height 2px den Strich sichtbar
                // halten — sonst gehen die Anfangsjahre des Korpus
                // (jeweils 1 Quelle) optisch verloren.
                const hpx = Math.max(1, Math.round((v / maxTotal) * 220));
                const segDim = (focus !== null && c.key !== focus) ? ' is-dimmed' : '';
                return `<span class="explore-stream-seg${segDim}"
                              data-h="${hpx}"
                              data-bg="${c.color}"
                              data-hint="${c.label}: ${V.fmt(v)}"></span>`;
            }).join('');
            // X-tick: full year only at century starts and every 5th decade.
            // Other ticks show the last two digits to keep the axis compact
            // without making "70" indistinguishable from 1170/1270/1370.
            const isMajor = (d % 100 === 0) || (d % 50 === 0);
            const tickLabel = isMajor ? String(d) : String(d).slice(2);
            const tickCls = isMajor ? 'explore-stream-xtick explore-stream-xtick--major' : 'explore-stream-xtick';
            return `<button type="button"
                class="explore-stream-col${dimmed ? ' is-dimmed' : ''}"
                data-decade="${d}"
                aria-label="${d}er: ${V.fmt(totals[d])}"
                data-hint="${d}er: ${V.fmt(totals[d])}">
                <span class="explore-stream-stack">${segs}</span>
                <span class="${tickCls}">${tickLabel}</span>
            </button>`;
        }).join('');

        chart.innerHTML = cols;
        V.applyDataStyles(chart);

        renderLegend(categories, values, totals);
        bindBars();
    }

    function renderLegend(categories, values, totals) {
        const el = document.getElementById('stream-legend');
        if (!el) return;
        const grand = Object.values(totals).reduce((s, c) => s + c, 0);
        const focus = STATE.stackFocus;
        el.innerHTML = categories.map(c => {
            const sum = Object.values(values).reduce(
                (s, dv) => s + (dv[c.key] || 0), 0);
            const isFocused = (focus === c.key);
            const isDimmed = (focus !== null && !isFocused);
            const cls = 'legend-item legend-item--clickable'
                + (isFocused ? ' is-focused' : '')
                + (isDimmed  ? ' is-dimmed'  : '');
            const ariaPressed = isFocused ? 'true' : 'false';
            // Focused item shows a × to make "click again to clear" explicit.
            // The mark stays inside the same clickable region — same click
            // handler clears the focus (toggle).
            const clearMark = isFocused
                ? '<span class="legend-clear" aria-hidden="true">&times;</span>'
                : '';
            const title = isFocused
                ? 'Klick: Fokus auf ' + c.label + ' wieder aufheben'
                : 'Klick: nur ' + c.label + ' im Brush-Drill anzeigen';
            return `<li class="${cls}" data-cat="${c.key}"
                role="button" tabindex="0" aria-pressed="${ariaPressed}"
                data-hint="${title}">
                <span class="legend-swatch" data-bg="${c.color}"></span>
                <span class="legend-label">${c.label}</span>
                <span class="legend-count">${V.fmt(sum)}</span>
                <span class="legend-pct">${V.pct(sum, grand)}&nbsp;%</span>
                ${clearMark}
            </li>`;
        }).join('');
        V.applyDataStyles(el);
    }

    function bindLegendFocus() {
        const el = document.getElementById('stream-legend');
        if (!el) return;
        el.addEventListener('click', (e) => {
            const item = e.target.closest('[data-cat]');
            if (!item) return;
            const key = item.getAttribute('data-cat');
            // Toggle: same category again -> clear focus
            STATE.stackFocus = (STATE.stackFocus === key) ? null : key;
            renderChart();
            renderDrill();
            updateActiveFilters();
            writeUrl();
        });
        el.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            const item = e.target.closest('[data-cat]');
            if (!item) return;
            e.preventDefault();
            item.click();
        });
    }

    // ---------------------------------------------------------------------
    // Brush / bar click
    // ---------------------------------------------------------------------
    let brushAnchor = null;

    function bindBars() {
        const chart = document.getElementById('stream-chart');
        if (!chart) return;

        chart.querySelectorAll('.explore-stream-col').forEach(col => {
            col.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const dec = parseInt(col.dataset.decade, 10);
                brushAnchor = dec;
                STATE.brushMin = dec;
                STATE.brushMax = dec;
                renderChart();
                renderDrill();
            });
            col.addEventListener('mouseenter', () => {
                if (brushAnchor === null) return;
                const dec = parseInt(col.dataset.decade, 10);
                STATE.brushMin = Math.min(brushAnchor, dec);
                STATE.brushMax = Math.max(brushAnchor, dec);
                renderChart();
            });
            // Keyboard activation: Enter/Space brushes the single decade.
            // Shift+Arrow on a focused column extends the existing brush
            // by one decade so keyboard users can build a range.
            col.addEventListener('keydown', (e) => {
                const dec = parseInt(col.dataset.decade, 10);
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    STATE.brushMin = dec;
                    STATE.brushMax = dec;
                    renderChart();
                    renderDrill();
                    updateActiveFilters();
                    writeUrl();
                    return;
                }
                if (e.shiftKey && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
                    if (STATE.brushMin === null) return;
                    e.preventDefault();
                    if (e.key === 'ArrowLeft') {
                        STATE.brushMin = Math.min(STATE.brushMin, dec - 10);
                    } else {
                        STATE.brushMax = Math.max(STATE.brushMax, dec + 10);
                    }
                    renderChart();
                    renderDrill();
                    updateActiveFilters();
                    writeUrl();
                }
            });
        });
        // Mouse-up ends brushing globally so the selection persists even
        // when the user releases outside the chart.
        document.addEventListener('mouseup', () => {
            if (brushAnchor !== null) {
                brushAnchor = null;
                renderDrill();
                updateActiveFilters();
                writeUrl();
            }
        });
    }

    function clearBrush() {
        STATE.brushMin = null;
        STATE.brushMax = null;
        renderChart();
        renderDrill();
        updateActiveFilters();
        writeUrl();
    }

    // ---------------------------------------------------------------------
    // Drill-down: source list for the brushed decades
    // ---------------------------------------------------------------------
    function renderDrill() {
        const drill = document.getElementById('stream-drill');
        const list = document.getElementById('drill-list');
        const title = document.getElementById('drill-title');
        const meta = document.getElementById('drill-meta');
        if (!drill || !list) return;

        if (STATE.brushMin === null) {
            drill.hidden = true;
            list.innerHTML = '';
            return;
        }

        const lo = STATE.brushMin, hi = STATE.brushMax;
        const stackDef = effectiveStackDef();
        const focus = STATE.stackFocus;
        const focusedCat = focus
            ? stackDef.categories.find(c => c.key === focus)
            : null;

        // Pick data source:
        // - tx stack with focus -> file_keys from transactions.tx_type_decade,
        //   resolved to doc records via docs_lookup
        // - otherwise (incl. tx without focus, all stacks): from DOCS_BY_DECADE
        let docs;
        if (STATE.stack === 'tx' && focus) {
            docs = collectTxFocusedDocs(focus, lo, hi);
        } else {
            docs = collectStreamDocs(lo, hi, focus);
        }
        sortDrillDocs(docs);

        const rangeLabel = (lo === hi) ? `${lo}er` : `${lo}er–${hi}er`;
        const focusLabel = focusedCat ? ` · ${focusedCat.label}` : '';
        if (title) title.textContent = `Auswahl ${rangeLabel}${focusLabel}`;
        if (meta) meta.textContent = `${V.fmt(docs.length)} Quellen`;

        // Cross-nav: sources list page with the brush period (no sex filter
        // — the timeline doesn't have one). Tx/collection/form focus cannot
        // be mapped 1:1 onto the source filters (sources have no tx/stack
        // filters), so it's omitted. If a focus is active we make the loss
        // explicit in the link tooltip so the user knows the result list
        // will be broader than what the chart shows here.
        const crossNav = document.getElementById('drill-crossnav');
        if (crossNav) {
            crossNav.href = V.buildDocumentsURL({
                decadeMin: lo,
                decadeMax: hi,
            });
            const baseHint = 'Filter (Zeitraum) wird in die Quellen-Listenseite übernommen.';
            crossNav.title = focusedCat
                ? baseHint + ' Der Fokus "' + focusedCat.label + '" wird nicht weitergegeben.'
                : baseHint;
        }

        const ROOT = (window.ROOT_PATH || '..');
        const SHOW = 200;
        const hasBasket = (typeof DataBasket !== 'undefined');
        const shown = docs.slice(0, SHOW);
        list.innerHTML = shown.map(doc => {
            const basketBtn = hasBasket ? DataBasket.buttonHTML({
                id: doc.id, label: doc.id,
                url: doc.u, date: doc.date, coll: doc.coll, regest: '',
            }) : '';
            return `<li class="explore-stream-doc">
                <a href="${ROOT}/${doc.u}" class="doc-link">
                    <span class="doc-id">${doc.id}</span>
                    <span class="doc-date">${doc.date}</span>
                    <span class="doc-coll">${doc.coll}</span>
                    <span class="doc-place">${doc.place}</span>
                </a>
                ${basketBtn}
            </li>`;
        }).join('') + (docs.length > SHOW
            ? `<li class="explore-stream-doc-more">… und ${V.fmt(docs.length - SHOW)} weitere; bitte enger eingrenzen.</li>`
            : '');

        drill.hidden = false;
    }

    // Sorts in place using STATE.drillSort. Sort key '_sort' carries
    // the ISO-ish date; coll is the collection label for grouping.
    function sortDrillDocs(docs) {
        const mode = STATE.drillSort || 'date-asc';
        if (mode === 'date-desc') {
            docs.sort((a, b) => (b._sort || '').localeCompare(a._sort || ''));
        } else if (mode === 'coll') {
            docs.sort((a, b) => {
                const c = (a.coll || '').localeCompare(b.coll || '');
                if (c !== 0) return c;
                return (a._sort || '').localeCompare(b._sort || '');
            });
        } else {
            docs.sort((a, b) => (a._sort || '').localeCompare(b._sort || ''));
        }
    }

    function bindDrillSort() {
        const grp = document.getElementById('drill-sort');
        if (!grp) return;
        grp.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-sort]');
            if (!btn) return;
            STATE.drillSort = btn.getAttribute('data-sort');
            V.setActiveChip(grp, STATE.drillSort, 'data-sort', 'is-active');
            renderDrill();
            writeUrl();
        });
    }

    // Returns drill records from DOCS_BY_DECADE (search.json-based).
    // If focus is set, filters via stackDef.assign(All).
    function collectStreamDocs(lo, hi, focus) {
        const stackDef = effectiveStackDef();
        const docs = [];
        for (let d = lo; d <= hi; d += 10) {
            for (const doc of (DOCS_BY_DECADE.get(d) || [])) {
                if (focus !== null) {
                    if (stackDef.multi) {
                        if (!stackDef.assignAll(doc).includes(focus)) continue;
                    } else if (stackDef.assign && stackDef.assign(doc) !== focus) {
                        continue;
                    }
                }
                docs.push({
                    u: doc.u,
                    id: doc.id,
                    date: doc.dn || doc.di || '',
                    coll: doc.cl || doc.c || '',
                    place: doc.p || '',
                    _sort: doc.di || '',
                });
            }
        }
        return docs;
    }

    // Returns drill records for a tx focus from transactions.drill_down via
    // docs_lookup. Triggers a lazy load of docs_lookup.json if needed
    // (the result will surface on the next render).
    function collectTxFocusedDocs(txKey, lo, hi) {
        const dd = ((TRANSACTIONS.drill_down || {}).tx_type_decade || {})[txKey] || {};
        const seen = new Set();
        const docs = [];
        for (let d = lo; d <= hi; d += 10) {
            for (const fk of (dd[String(d)] || [])) {
                if (seen.has(fk)) continue;
                seen.add(fk);
                const lk = DOCS_LOOKUP[fk];
                if (!lk) continue;
                docs.push({
                    u: lk.u,
                    id: lk.i,
                    date: lk.d,
                    coll: lk.c,
                    place: '',
                    _sort: lk.d || '',
                });
            }
        }
        if (!Object.keys(DOCS_LOOKUP).length) {
            // Lazy load: docs_lookup not yet here. Fetch and re-run
            // the drill rendering.
            V.loadDocsLookup().then(lk => {
                DOCS_LOOKUP = lk;
                renderDrill();
            }).catch(() => {});
        }
        return docs;
    }

    // ---------------------------------------------------------------------
    // Sidebar controls
    // ---------------------------------------------------------------------
    function bindStackChips() {
        const group = document.getElementById('stream-stack-axis');
        if (!group) return;
        group.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-stack]');
            if (!btn) return;
            STATE.stack = btn.getAttribute('data-stack');
            // Reset stack focus — categories change with the axis,
            // so the old focus key no longer applies.
            STATE.stackFocus = null;
            V.setActiveChip(group, STATE.stack, 'data-stack', 'is-active');
            // Keep brush — the source selection is valid independently
            // of the axis.
            renderChart();
            renderDrill();
            updateActiveFilters();
            writeUrl();
        });
    }

    function bindReset() {
        const btn = document.getElementById('filter-reset');
        if (!btn) return;
        btn.addEventListener('click', () => {
            STATE.stack = 'collection';
            STATE.brushMin = null;
            STATE.brushMax = null;
            STATE.stackFocus = null;
            STATE.drillSort = 'date-asc';
            V.setActiveChip(document.getElementById('stream-stack-axis'),
                            'collection', 'data-stack', 'is-active');
            V.setActiveChip(document.getElementById('drill-sort'),
                            'date-asc', 'data-sort', 'is-active');
            // Slider reset fires the onChange hook via the input event and
            // therefore renderChart()+renderDrill(). If the slider is
            // missing, render once directly.
            if (!V.resetSliderInputs()) {
                STATE.decadeMin = null;
                STATE.decadeMax = null;
                renderChart();
                renderDrill();
                updateActiveFilters();
            }
        });
    }

    function bindDrillClear() {
        const btn = document.getElementById('drill-clear');
        if (btn) btn.addEventListener('click', clearBrush);
    }

    // ---------------------------------------------------------------------
    // Active filter strip
    // ---------------------------------------------------------------------
    function clearStackFocus() {
        STATE.stackFocus = null;
        renderChart();
        renderDrill();
        updateActiveFilters();
        writeUrl();
    }

    function updateActiveFilters() {
        const filters = [];
        if (decFilter.isActive()) {
            const minEl = document.getElementById('range-min');
            const maxEl = document.getElementById('range-max');
            const lo = minEl ? minEl.value : STATE.decadeMin;
            const hi = maxEl ? maxEl.value : STATE.decadeMax;
            filters.push({
                label: 'Zeitraum: ' + lo + '–' + hi,
                onClear: () => V.resetSliderInputs(),
            });
        }
        if (STATE.brushMin !== null) {
            const lo = STATE.brushMin, hi = STATE.brushMax;
            const range = (lo === hi) ? `${lo}er` : `${lo}er–${hi}er`;
            filters.push({ label: 'Auswahl: ' + range, onClear: clearBrush });
        }
        if (STATE.stackFocus !== null) {
            const cat = effectiveStackDef().categories.find(c => c.key === STATE.stackFocus);
            const label = cat ? cat.label : STATE.stackFocus;
            filters.push({ label: 'Kategorie: ' + label, onClear: clearStackFocus });
        }
        V.renderActiveFilters('active-filters', filters);
    }

    // ---------------------------------------------------------------------
    // Init
    // ---------------------------------------------------------------------
    function onSliderChange() {
        renderChart();
        renderDrill();
        updateActiveFilters();
        writeUrl();
    }

    // ---------------------------------------------------------------------
    // URL state sync
    // Format: ?dec=1300-1380&stack=tx&brush=1340-1370&focus=Kauf
    // ---------------------------------------------------------------------
    let urlSyncActive = false;

    function writeUrl() {
        if (!urlSyncActive) return;
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        const dec = decFilter.isActive() && minEl && maxEl
            ? `${minEl.value}-${maxEl.value}` : null;
        const brush = STATE.brushMin !== null
            ? (STATE.brushMin === STATE.brushMax
                ? String(STATE.brushMin)
                : `${STATE.brushMin}-${STATE.brushMax}`)
            : null;
        V.writeUrlState({
            dec:   dec,
            stack: STATE.stack !== 'collection' ? STATE.stack : null,
            brush: brush,
            focus: STATE.stackFocus,
            sort:  STATE.drillSort !== 'date-asc' ? STATE.drillSort : null,
        });
    }

    function applyUrlState() {
        const u = V.parseUrlState();
        if (u.stack && STACKS[u.stack]) STATE.stack = u.stack;
        if (u.dec) {
            const m = u.dec.match(/^(\d{4})-(\d{4})$/);
            if (m) {
                const lo = parseInt(m[1], 10);
                const hi = parseInt(m[2], 10);
                STATE.decadeMin = V.decadeOf(lo);
                STATE.decadeMax = V.decadeOf(hi);
                V.applySliderValues(lo, hi);
            }
        }
        if (u.brush) {
            const m = u.brush.match(/^(\d{4})(?:-(\d{4}))?$/);
            if (m) {
                STATE.brushMin = parseInt(m[1], 10);
                STATE.brushMax = m[2] ? parseInt(m[2], 10) : STATE.brushMin;
            }
        }
        if (u.focus) {
            // Validity is checked at the first render (effectiveStackDef).
            STATE.stackFocus = u.focus;
        }
        if (u.sort && ['date-asc', 'date-desc', 'coll'].includes(u.sort)) {
            STATE.drillSort = u.sort;
        }
        // UI sync for the stack chips and sort chips
        V.setActiveChip(document.getElementById('stream-stack-axis'),
                        STATE.stack, 'data-stack', 'is-active');
        V.setActiveChip(document.getElementById('drill-sort'),
                        STATE.drillSort, 'data-sort', 'is-active');
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindStackChips();
        V.bindRangeSlider({ state: STATE, onChange: onSliderChange });
        bindReset();
        bindDrillClear();
        bindDrillSort();
        bindLegendFocus();
        applyUrlState();

        V.loadSearchJson()
            .then(({ docs, byDecade }) => {
                DOCS = docs;
                DOCS_BY_DECADE = byDecade;
                renderChart();
                renderDrill();
                updateActiveFilters();
                urlSyncActive = true;
                writeUrl();
            })
            .catch(err => {
                console.warn('search.json nicht ladbar:', err);
                const chart = document.getElementById('stream-chart');
                if (chart) chart.innerHTML =
                    '<div class="aggregat-empty">Daten konnten nicht geladen werden.</div>';
            });
        // docs_lookup is only needed for the tx focus drill — eager-load
        // it in the background so the first click responds without delay.
        V.loadDocsLookup().then(lk => { DOCS_LOOKUP = lk; }).catch(() => {});
    });
})();
