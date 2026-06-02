// Shared visualisation layer for the data visualisation pages under
// /analysis/ and /exploration/. Provides data loaders, decade helpers,
// CSP-safe style projection, chip toggling, sidebar bindings and the
// Active-Filter-Strip rendering. Domain constants (roles, relations,
// sex labels) live here centrally so all pages stay consistent.

let VizCore = (function () {
    'use strict';

    // Domain constants — kept consistent project-wide
    const ROLE_LABELS = {
        'issuer':    'Aussteller*innen',
        'recipient': 'Empfänger*innen',
        'witness':   'Zeug*innen / Siegler*innen',
        'other':     'Sonstige',
        '':          'keine Rolle',
    };
    const ROLE_ORDER = ['issuer', 'recipient', 'witness', 'other', ''];
    const ROLE_COLORS = {
        'issuer':    '#b85c2f',  // Terracotta
        'recipient': '#2e7a88',  // Aqua
        'witness':   '#6b6040',  // Olive
        'other':     '#a08470',  // Sand
        '':          '#9a9590',  // grey (none)
    };

    const REL_LABELS = {
        'kin':    'Verwandtschaft',
        'occ':    'Beruf / Stand',
        'rep':    'Vertretung',
        'friend': 'Freundschaft',
    };
    const REL_ORDER = ['kin', 'occ', 'rep', 'friend'];
    const REL_COLORS = {
        'kin':    '#b85c2f',  // Terracotta
        'occ':    '#c4a035',  // Gold
        'rep':    '#6b6040',  // Olive
        'friend': '#2e7a88',  // Aqua
    };

    const SEX_LABELS_DE = {
        'm':           '♂ männlich',
        'f':           '♀ weiblich',
        'unspecified': 'ohne Angabe',
    };

    function fmt(n) {
        return (n || 0).toLocaleString('de-AT').replace(/,/g, '.');
    }
    function pct(n, total) {
        if (!total) return '–';
        return ((n / total) * 100).toFixed(1).replace('.', ',');
    }

    // Decade helpers — decade arithmetic and range filtering.
    // makeDecadeFilter(state) binds to a page state object holding numeric
    // fields decadeMin/decadeMax (null = no filter).
    function decadeOf(year) { return Math.floor(year / 10) * 10; }

    function makeDecadeFilter(state) {
        return {
            isActive() {
                return state.decadeMin !== null || state.decadeMax !== null;
            },
            noFilter() {
                return state.decadeMin === null && state.decadeMax === null;
            },
            contains(decade) {
                const dec = parseInt(decade, 10);
                if (state.decadeMin !== null && dec < state.decadeMin) return false;
                if (state.decadeMax !== null && dec > state.decadeMax) return false;
                return true;
            },
        };
    }

    // Turn pipeline underscore keys ("ueber_gabe") back into display form.
    // Umlaut recovery must be case-sensitive — otherwise "Uebergabe" would
    // not round-trip to "Übergabe".
    function labelize(k) {
        return k.replace(/_/g, ' ')
            .replace(/Ae/g, 'Ä').replace(/Oe/g, 'Ö').replace(/Ue/g, 'Ü')
            .replace(/ae/g, 'ä').replace(/oe/g, 'ö').replace(/ue/g, 'ü');
    }

    // CSP-safe style projection
    // CSP "style-src 'self'" blocks inline style="..." attributes. We
    // encode values as data attributes and project them after each
    // innerHTML onto the element's style property (CSP-compliant via JS IDL).
    // Supported data attributes:
    //   data-w        -> style.width = "<v>%"
    //   data-h        -> style.height = "<v>px"
    //   data-bg       -> style.background = "<v>"
    //   data-bottom   -> style.bottom = "<v>px"
    function applyDataStyles(root) {
        if (!root) return;
        root.querySelectorAll('[data-w]').forEach(el => {
            el.style.width = el.dataset.w + '%';
        });
        root.querySelectorAll('[data-h]').forEach(el => {
            el.style.height = el.dataset.h + 'px';
        });
        root.querySelectorAll('[data-bg]').forEach(el => {
            el.style.background = el.dataset.bg;
        });
        root.querySelectorAll('[data-bottom]').forEach(el => {
            el.style.bottom = el.dataset.bottom + 'px';
        });
    }

    // Read JSON from an embedded <script type="application/json">
    function readJsonScript(id, fallback) {
        const el = document.getElementById(id);
        if (!el) return fallback || null;
        try { return JSON.parse(el.textContent); }
        catch (e) {
            console.error('Bad JSON in', id, e);
            return fallback || null;
        }
    }

    // Document preprocessing for search.json
    // Annotates each doc with _dec (parsable decade from di/d) and returns
    // {docs, byDecade} for fast lookup.
    function preprocessDocs(raw) {
        const docs = [];
        const byDecade = new Map();
        for (const d of raw) {
            const yearStr = (d.di || d.d || '').slice(0, 4);
            const year = /^\d{4}$/.test(yearStr) ? parseInt(yearStr, 10) : null;
            const dec = (year !== null) ? decadeOf(year) : null;
            d._dec = dec;
            docs.push(d);
            if (dec !== null) {
                if (!byDecade.has(dec)) byDecade.set(dec, []);
                byDecade.get(dec).push(d);
            }
        }
        return { docs, byDecade };
    }

    function loadSearchJson(rootPath) {
        const root = rootPath || (window.ROOT_PATH || '..');
        return fetch(root + '/data/search.json')
            .then(r => r.json())
            .then(preprocessDocs);
    }

    // docs_lookup.json: file_key (e.g. "f__QGW_0a") -> doc base record
    // {u: url, i: idno, d: display date, c: corpus label, r: regest}.
    // Used by Drill-down lists that only store file_keys (drill_down in
    // roles/relations/transactions).
    function loadDocsLookup(rootPath) {
        const root = rootPath || (window.ROOT_PATH || '..');
        return fetch(root + '/data/docs_lookup.json').then(r => r.json());
    }

    // Chip active-toggle helper
    // Marks the button matching activeKey in a chip group as active (CSS
    // class + aria-pressed); all others are cleared. activeClass defaults
    // to 'active' (sidebar standard); quadrant-header toggle buttons pass
    // 'is-active' instead.
    function setActiveChip(group, activeKey, attr, activeClass) {
        if (!group) return;
        activeClass = activeClass || 'active';
        group.querySelectorAll('[' + attr + ']').forEach(b => {
            const isActive = b.getAttribute(attr) === activeKey;
            b.classList.toggle(activeClass, isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
    }

    // Range-Slider binding
    // bindRangeSlider({state, onChange}) binds to the inputs generated by
    // the macro (#range-min, #range-max). Mutates state.decadeMin/decadeMax
    // (null when fully expanded -> no filter). Updates range-label-min/max
    // and histogram highlights. onChange fires after every change.
    function bindRangeSlider(opts) {
        const state = opts.state;
        const onChange = opts.onChange || function () {};
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        if (!minEl || !maxEl) return;
        const labelMin = document.getElementById('range-label-min');
        const labelMax = document.getElementById('range-label-max');
        const sliderMin = parseInt(minEl.min, 10);
        const sliderMax = parseInt(maxEl.max, 10);

        function update() {
            let lo = parseInt(minEl.value, 10);
            let hi = parseInt(maxEl.value, 10);
            if (lo > hi) { [lo, hi] = [hi, lo]; }
            // Fully expanded slider = no filter (otherwise documents
            // without a parsable decade would drop out of the aggregates).
            if (lo <= sliderMin && hi >= sliderMax) {
                state.decadeMin = null;
                state.decadeMax = null;
            } else {
                state.decadeMin = decadeOf(lo);
                state.decadeMax = decadeOf(hi);
            }
            if (labelMin) labelMin.textContent = lo;
            if (labelMax) labelMax.textContent = hi;
            updateRangeHistogram(lo, hi);
            onChange(lo, hi);
        }
        minEl.addEventListener('input', update);
        maxEl.addEventListener('input', update);
        // Initial paint: data-height is set per bar in the template but only
        // projected onto style.height by updateRangeHistogram. Without this
        // first call the histogram stays flat until the user moves the slider.
        updateRangeHistogram(parseInt(minEl.value, 10), parseInt(maxEl.value, 10));
    }

    function updateRangeHistogram(lo, hi) {
        const histo = document.getElementById('range-histogram');
        if (!histo) return;
        histo.querySelectorAll('.range-bar').forEach(bar => {
            const dec = parseInt(bar.dataset.decade, 10);
            const inRange = (dec >= decadeOf(lo) && dec <= decadeOf(hi));
            bar.classList.toggle('range-bar--out', !inRange);
            const h = bar.dataset.height || 0;
            bar.style.setProperty('--bar-height', h + '%');
            bar.style.height = h + '%';
        });
    }

    function resetSliderInputs() {
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        if (!minEl || !maxEl) return false;
        minEl.value = minEl.min;
        maxEl.value = maxEl.max;
        // Triggers update() (attached by bindRangeSlider), which clears
        // state.decadeMin/Max to null and calls onChange.
        minEl.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
    }

    // Set slider DOM to values and refresh visuals (histogram highlights,
    // Range-Slider labels). Does NOT dispatch an input event — the caller
    // already set state itself and will call renderAll() afterwards.
    function applySliderValues(lo, hi) {
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        if (!minEl || !maxEl) return;
        if (lo != null) minEl.value = lo;
        if (hi != null) maxEl.value = hi;
        const labelMin = document.getElementById('range-label-min');
        const labelMax = document.getElementById('range-label-max');
        if (labelMin) labelMin.textContent = minEl.value;
        if (labelMax) labelMax.textContent = maxEl.value;
        updateRangeHistogram(parseInt(minEl.value, 10), parseInt(maxEl.value, 10));
    }

    // URL state sync
    // parseUrlState() reads URL search parameters as a flat object.
    // writeUrlState({...}) writes via history.replaceState — no history
    // entries, no page loads. Empty/null values are dropped.
    function parseUrlState() {
        const out = {};
        const p = new URLSearchParams(location.search);
        for (const [k, v] of p) out[k] = v;
        return out;
    }

    function writeUrlState(params) {
        const p = new URLSearchParams();
        for (const [k, v] of Object.entries(params || {})) {
            if (v === null || v === undefined || v === '') continue;
            p.set(k, String(v));
        }
        const qs = p.toString();
        const url = location.pathname + (qs ? '?' + qs : '');
        history.replaceState(null, '', url);
    }

    // Cross-page jump: build a source list URL carrying the transferable
    // filters (time range + sex mapping). The source list page has no
    // role/relation/designation/tx filter — those are deliberately not
    // forwarded. The sex mapping is asymmetric:
    //   sex='f' -> 'with-f'  (sources containing at least one woman)
    //   sex='m' -> 'only-m'  ('with-m' does not exist on the source page)
    function buildDocumentsURL(opts) {
        const root = opts.root || (window.ROOT_PATH || '..');
        const p = new URLSearchParams();
        if (opts.decadeMin != null) p.set('yearMin', opts.decadeMin);
        if (opts.decadeMax != null) p.set('yearMax', opts.decadeMax + 9);
        if (opts.sex === 'f')      p.set('sex', 'with-f');
        else if (opts.sex === 'm') p.set('sex', 'only-m');
        const qs = p.toString();
        return root + '/documents.html' + (qs ? '?' + qs : '');
    }

    // Drill-down overlay
    // Uses the drill_down_overlay() macro from macros.html (which already
    // ships CSS, header, table, footer count and close button).
    // openDrillOverlay({ overlayId, title, fileKeys, docsLookup,
    //                    decadeFilter, note }) populates the overlay table
    // and shows it. The caller has wired up the close handler once via
    // bindDrillOverlay().
    // Element to return focus to after the drill-down overlay closes.
    let _drillReturnFocus = null;

    function bindDrillOverlay(opts) {
        const id = opts.overlayId;
        const overlay = document.getElementById(id);
        const closeBtn = document.getElementById(id + '-close');
        if (!overlay || !closeBtn) return;

        function close() {
            overlay.classList.add('hidden');
            overlay.setAttribute('aria-hidden', 'true');
            if (_drillReturnFocus && typeof _drillReturnFocus.focus === 'function') {
                try { _drillReturnFocus.focus(); } catch (_) {}
            }
            _drillReturnFocus = null;
        }

        closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) close();   // click on backdrop
        });

        // Modal keyboard handling: Escape closes, Tab/Shift+Tab traps focus
        // inside the overlay (required by aria-modal="true", WCAG 2.4.3 / 2.1.2).
        document.addEventListener('keydown', (e) => {
            if (overlay.classList.contains('hidden')) return;
            if (e.key === 'Escape') { close(); return; }
            if (e.key !== 'Tab') return;

            const focusables = overlay.querySelectorAll(
                'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"]), ' +
                'input:not([disabled]), select:not([disabled]), textarea:not([disabled])'
            );
            if (!focusables.length) return;
            const first = focusables[0];
            const last = focusables[focusables.length - 1];
            const active = document.activeElement;
            if (e.shiftKey && active === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && active === last) {
                e.preventDefault();
                first.focus();
            }
        });
    }

    function openDrillOverlay(opts) {
        const id = opts.overlayId;
        const overlay = document.getElementById(id);
        if (!overlay) return;
        const titleEl = document.getElementById(id + '-title');
        const tbody = document.getElementById(id + '-tbody');
        const countEl = document.getElementById(id + '-count');
        const lookup = opts.docsLookup || {};
        const decadeFilter = opts.decadeFilter || null;

        // file_keys -> doc records, optionally filtered by decade (date
        // taken from the lookup entries' d field; first 4 chars = year).
        const seen = new Set();
        const docs = [];
        for (const fk of (opts.fileKeys || [])) {
            if (seen.has(fk)) continue;
            seen.add(fk);
            const e = lookup[fk];
            if (!e) continue;
            if (decadeFilter) {
                const yearStr = (e.d || '').slice(0, 4);
                if (/^\d{4}$/.test(yearStr)) {
                    const dec = decadeOf(parseInt(yearStr, 10));
                    if (!decadeFilter.contains(dec)) continue;
                }
            }
            docs.push({ key: fk, ...e });
        }
        // Sort by date (d starts with YYYY).
        docs.sort((a, b) => (a.d || '').localeCompare(b.d || ''));

        if (titleEl) titleEl.textContent = opts.title || 'Quellen';
        if (countEl) {
            const noteText = opts.note ? ' · ' + opts.note : '';
            countEl.textContent = fmt(docs.length) + ' Quellen' + noteText;
        }

        // Optional cross-nav link in the footer ("-> open in source list").
        // Injected into the footer container and replaced on each open so
        // the URL stays current.
        const footer = overlay.querySelector('.explore-drilldown-footer');
        if (footer) {
            const existing = footer.querySelector('.explore-drilldown-crossnav');
            if (existing) existing.remove();
            if (opts.crossNavUrl) {
                const link = document.createElement('a');
                link.className = 'explore-drilldown-crossnav explore-btn';
                link.href = opts.crossNavUrl;
                link.textContent = '→ in Quellen-Liste öffnen';
                link.title = 'Filter (Zeitraum, Geschlecht) werden in die Quellen-Listenseite uebernommen.';
                footer.appendChild(link);
            }
        }

        if (tbody) {
            const root = (window.ROOT_PATH || '..');
            const SHOW = 500;
            const hasBasket = (typeof DataBasket !== 'undefined');
            const rows = docs.slice(0, SHOW).map(d => {
                const basketBtn = hasBasket ? DataBasket.buttonHTML({
                    id: d.i, label: d.i,
                    url: d.u, date: d.d, coll: d.c, regest: d.r,
                }) : '';
                return `<tr>
                    <td><a href="${root}/${d.u}">${d.i || ''}</a></td>
                    <td>${d.d || ''}</td>
                    <td>${d.c || ''}</td>
                    <td class="cell-regest">${d.r || ''}</td>
                    <td class="col-actions">${basketBtn}</td>
                </tr>`;
            });
            if (docs.length > SHOW) {
                rows.push(`<tr><td colspan="5" class="aggregat-empty">… und ${fmt(docs.length - SHOW)} weitere; bitte enger eingrenzen.</td></tr>`);
            }
            tbody.innerHTML = rows.join('') ||
                '<tr><td colspan="5" class="aggregat-empty">Keine Quellen gefunden.</td></tr>';
        }

        // Remember the previously focused element (return target on close),
        // then move focus to the close button once the overlay is visible.
        if (overlay.classList.contains('hidden')) {
            _drillReturnFocus = document.activeElement;
        }
        overlay.classList.remove('hidden');
        overlay.setAttribute('aria-hidden', 'false');
        const closeBtn = document.getElementById(id + '-close');
        if (closeBtn && typeof closeBtn.focus === 'function') {
            requestAnimationFrame(function () {
                try { closeBtn.focus(); } catch (_) {}
            });
        }
    }

    // Active-Filter-Strip
    // renderActiveFilters(containerId, filters) — filters is an array of
    // {label, onClear} objects. Each entry renders a removable pill;
    // clicking it calls onClear.
    function renderActiveFilters(containerId, filters) {
        const el = document.getElementById(containerId);
        if (!el) return;
        el.innerHTML = '';
        const ti = (typeof TableInfra !== 'undefined') ? TableInfra : null;
        if (!ti) return;
        for (const f of filters) {
            ti.addFilterChip(el, f.label, f.onClear);
        }
    }

    return {
        // Constants
        ROLE_LABELS, ROLE_ORDER, ROLE_COLORS,
        REL_LABELS, REL_ORDER, REL_COLORS,
        SEX_LABELS_DE,
        // Format/helpers
        fmt, pct,
        decadeOf, makeDecadeFilter,
        labelize,
        applyDataStyles,
        setActiveChip,
        // Data
        readJsonScript,
        preprocessDocs,
        loadSearchJson,
        loadDocsLookup,
        // Sidebar
        bindRangeSlider,
        resetSliderInputs,
        applySliderValues,
        // URL state
        parseUrlState,
        writeUrlState,
        buildDocumentsURL,
        // Filter strip
        renderActiveFilters,
        // Drill-down
        bindDrillOverlay,
        openDrillOverlay,
    };
})();
