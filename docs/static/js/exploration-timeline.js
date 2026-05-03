// Exploration / Zeitstrom: gestapelter Bar-Chart der Quellendichte pro
// Dekade, Stapel-Achse waehlbar (Korpus / Erschliessungsform / Geschlecht /
// Transaktionstyp). Brush waehlt Dekaden-Bereich -> Drill-down-Quellenliste.
// Geteilte Infrastruktur kommt aus VizCore (viz-core.js).
(function () {
    'use strict';

    const V = VizCore;

    // ---------------------------------------------------------------------
    // Stapel-Definitionen
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
            // Mehrere Formen pro Quelle moeglich; wir zaehlen die Quelle
            // dann mehrfach (eine pro vorhandener Form).
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
        // Transaktionstyp braucht eigene Datenquelle (epic_c.tx_timeline);
        // wird im Renderer gesondert behandelt und nicht aus search.json
        // abgeleitet.
        tx: {
            label: 'Transaktionstyp',
            categories: [],  // wird dynamisch befuellt
            fromEpicC: true,
        },
    };

    const TX_TOP_N = 8;
    const TX_PALETTE = [
        '#b85c2f', '#2e7a88', '#6b6040', '#a08470',
        '#c4a035', '#5d3a74', '#2d6650', '#7a6b8c',
        '#9a9590',
    ];

    // ---------------------------------------------------------------------
    // Daten laden
    // ---------------------------------------------------------------------
    const EPIC_C = V.readJsonScript('exploration-data-epic-c', { observations: {} });
    let DOCS = [];
    let DOCS_BY_DECADE = new Map();
    let DOCS_LOOKUP = {};   // file_key -> Doc-Stammdaten (lazy fuer tx-Drill)

    // ---------------------------------------------------------------------
    // Filter-State
    // ---------------------------------------------------------------------
    const STATE = {
        decadeMin: null,
        decadeMax: null,
        stack: 'collection',
        brushMin: null,
        brushMax: null,
        stackFocus: null,   // null = alle Kategorien, sonst category-key
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

        // Dekaden im Filter sammeln; values/totals nur fuer diese
        // initialisieren — out-of-range Docs werden in der Doc-Schleife
        // unten ueber den values[dec]-Lookup gefiltert.
        const decadesSet = new Set();
        for (const doc of DOCS) {
            const dec = doc._dec;
            if (dec === null) continue;
            if (!decFilter.contains(dec)) continue;
            decadesSet.add(dec);
        }
        const decades = Array.from(decadesSet).sort((a, b) => a - b);
        for (const d of decades) {
            values[d] = {};
            for (const c of categories) values[d][c.key] = 0;
            totals[d] = 0;
        }

        if (STATE.stack === 'tx') {
            // Spezialfall: aus epic_c.tx_timeline aggregieren. Dekaden, die
            // dort vorkommen aber nicht in DOCS, werden zusaetzlich
            // nachgetragen (Tx-Daten sind unabhaengig vom Doc-Set).
            const tl = (EPIC_C.observations || {}).tx_timeline || {};
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

    // Liefert die effektive Stack-Definition (fuer 'tx' baut sie die
    // Top-N Kategorien dynamisch aus epic_c).
    function effectiveStackDef() {
        const def = STACKS[STATE.stack];
        if (STATE.stack !== 'tx') return def;

        const tl = (EPIC_C.observations || {}).tx_timeline || {};
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
                const hpx = Math.round((v / maxTotal) * 220);
                if (hpx < 1) return '';
                const segDim = (focus !== null && c.key !== focus) ? ' is-dimmed' : '';
                return `<span class="explore-stream-seg${segDim}"
                              data-h="${hpx}"
                              data-bg="${c.color}"
                              title="${c.label}: ${V.fmt(v)}"></span>`;
            }).join('');
            return `<button type="button"
                class="explore-stream-col${dimmed ? ' is-dimmed' : ''}"
                data-decade="${d}"
                aria-label="${d}er: ${V.fmt(totals[d])}"
                title="${d}er: ${V.fmt(totals[d])}">
                <span class="explore-stream-stack">${segs}</span>
                <span class="explore-stream-xtick">${String(d).slice(2)}</span>
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
            return `<li class="${cls}" data-cat="${c.key}"
                role="button" tabindex="0" aria-pressed="${ariaPressed}"
                title="Klick: nur ${c.label} im Brush-Drill anzeigen">
                <span class="legend-swatch" data-bg="${c.color}"></span>
                <span class="legend-label">${c.label}</span>
                <span class="legend-count">${V.fmt(sum)}</span>
                <span class="legend-pct">${V.pct(sum, grand)}&nbsp;%</span>
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
            // Toggle: gleiche Kategorie nochmal -> Fokus aufheben
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
    // Brush / Bar-Klick
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
        });
        // Maus-Up beendet Brushing global, damit Auswahl auch bestehen
        // bleibt, wenn der User ausserhalb des Charts loslaesst.
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
    // Drill-down: Quellen-Liste der gebrushten Dekaden
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

        // Datenquelle waehlen:
        // - tx-Stack mit Fokus  -> file_keys aus epic_c.tx_type_decade,
        //   ueber docs_lookup zu Doc-Records aufgeloest
        // - sonst (auch tx ohne Fokus, alle Stacks): aus DOCS_BY_DECADE
        let docs;
        if (STATE.stack === 'tx' && focus) {
            docs = collectTxFocusedDocs(focus, lo, hi);
        } else {
            docs = collectStreamDocs(lo, hi, focus);
        }
        docs.sort((a, b) => (a._sort || '').localeCompare(b._sort || ''));

        const rangeLabel = (lo === hi) ? `${lo}er` : `${lo}er–${hi}er`;
        const focusLabel = focusedCat ? ` · ${focusedCat.label}` : '';
        if (title) title.textContent = `Auswahl ${rangeLabel}${focusLabel}`;
        if (meta) meta.textContent = `${V.fmt(docs.length)} Quellen`;

        // Cross-Nav: Quellen-Listenseite mit dem Brush-Zeitraum (kein
        // Geschlechter-Filter — der Zeitstrom hat keinen). Tx-/collection-
        // /form-Fokus laesst sich nicht 1:1 auf die Quellen-Filter mappen
        // (Quellen kennt keine Tx-/Stack-Filter), wird daher weggelassen.
        const crossNav = document.getElementById('drill-crossnav');
        if (crossNav) {
            crossNav.href = V.buildDocumentsURL({
                decadeMin: lo,
                decadeMax: hi,
            });
        }

        const ROOT = (window.ROOT_PATH || '..');
        const SHOW = 200;
        const hasKorb = (typeof Wissenskorb !== 'undefined');
        const shown = docs.slice(0, SHOW);
        list.innerHTML = shown.map(doc => {
            const korbBtn = hasKorb ? Wissenskorb.buttonHTML({
                type: 'source', id: doc.id, label: doc.id,
                url: doc.u, date: doc.date, coll: doc.coll, regest: '',
            }) : '';
            return `<li class="explore-stream-doc">
                <a href="${ROOT}/${doc.u}" class="doc-link">
                    <span class="doc-id">${doc.id}</span>
                    <span class="doc-date">${doc.date}</span>
                    <span class="doc-coll">${doc.coll}</span>
                    <span class="doc-place">${doc.place}</span>
                </a>
                ${korbBtn}
            </li>`;
        }).join('') + (docs.length > SHOW
            ? `<li class="explore-stream-doc-more">… und ${V.fmt(docs.length - SHOW)} weitere; bitte enger eingrenzen.</li>`
            : '');

        drill.hidden = false;
    }

    // Liefert Drill-Records aus DOCS_BY_DECADE (search.json-basiert).
    // Wenn focus gesetzt ist, wird per stackDef.assign(All) gefiltert.
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

    // Liefert Drill-Records fuer einen Tx-Fokus aus epic_c.drill_down ueber
    // docs_lookup. Triggert ggf. das Nachladen von docs_lookup.json (laeuft
    // dann beim naechsten Render).
    function collectTxFocusedDocs(txKey, lo, hi) {
        const dd = ((EPIC_C.drill_down || {}).tx_type_decade || {})[txKey] || {};
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
            // Lazy-Load: docs_lookup ist noch nicht da. Nachladen und
            // das Drill-Rendering wiederholen.
            V.loadDocsLookup().then(lk => {
                DOCS_LOOKUP = lk;
                renderDrill();
            }).catch(() => {});
        }
        return docs;
    }

    // ---------------------------------------------------------------------
    // Sidebar-Bedienung
    // ---------------------------------------------------------------------
    function bindStackChips() {
        const group = document.getElementById('stream-stack-axis');
        if (!group) return;
        group.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-stack]');
            if (!btn) return;
            STATE.stack = btn.getAttribute('data-stack');
            // Stack-Fokus zuruecksetzen — die Kategorien aendern sich
            // mit der Achse, der alte Fokus-Key passt nicht mehr.
            STATE.stackFocus = null;
            V.setActiveChip(group, STATE.stack, 'data-stack', 'is-active');
            // Brush bleibt bestehen — die Quellen-Auswahl ist
            // achsen-unabhaengig gueltig.
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
            V.setActiveChip(document.getElementById('stream-stack-axis'),
                            'collection', 'data-stack', 'is-active');
            // Slider-Reset triggert via input-Event den onChange-Hook und
            // damit renderChart()+renderDrill(). Falls Slider fehlt,
            // einmal direkt rendern.
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
    // Active-Filter-Strip
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
    // URL-State-Sync
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
            // Validitaet wird beim ersten Render geprueft (effectiveStackDef).
            STATE.stackFocus = u.focus;
        }
        // UI-Sync der Stack-Chips
        V.setActiveChip(document.getElementById('stream-stack-axis'),
                        STATE.stack, 'data-stack', 'is-active');
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindStackChips();
        V.bindRangeSlider({ state: STATE, onChange: onSliderChange });
        bindReset();
        bindDrillClear();
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
        // docs_lookup nur fuer den Tx-Fokus-Drill noetig — eager im
        // Hintergrund vorladen, damit der erste Klick ohne Verzoegerung lebt.
        V.loadDocsLookup().then(lk => { DOCS_LOOKUP = lk; }).catch(() => {});
    });
})();
