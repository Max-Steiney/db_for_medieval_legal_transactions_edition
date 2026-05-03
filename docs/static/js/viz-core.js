/* ==========================================================================
   Wiener Urkundenbuch — Viz-Core
   Geteilte Infrastruktur fuer die Daten-Visualisierungs-Seiten unter
   /analysis/ und /exploration/. Liefert Daten-Lader, Dekaden-Helper,
   CSP-sichere Style-Projektion, Chip-Toggle, Sidebar-Bindings und das
   Active-Filter-Strip-Rendering. Domain-Konstanten (Rollen, Beziehungen,
   Geschlechter-Labels) leben hier zentral, damit alle Seiten sie konsistent
   nutzen.
   ========================================================================== */

let VizCore = (function () {
    'use strict';

    // ---------------------------------------------------------------------
    // Domain-Konstanten — projektweit konsistent
    // ---------------------------------------------------------------------
    const ROLE_LABELS = {
        'issuer':    'Aussteller / Ausstellerin',
        'recipient': 'Empfänger / Empfängerin',
        'witness':   'Siegler:in / Zeug:in',
        'other':     'Sonstige',
        '':          'keine Rolle',
    };
    const ROLE_ORDER = ['issuer', 'recipient', 'witness', 'other', ''];
    const ROLE_COLORS = {
        'issuer':    '#b85c2f',  // Terracotta
        'recipient': '#2e7a88',  // Aqua
        'witness':   '#6b6040',  // Olive
        'other':     '#a08470',  // Sand
        '':          '#9a9590',  // Grau (keine)
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

    // ---------------------------------------------------------------------
    // Number formatting
    // ---------------------------------------------------------------------
    function fmt(n) {
        return (n || 0).toLocaleString('de-AT').replace(/,/g, '.');
    }
    function pct(n, total) {
        if (!total) return '–';
        return ((n / total) * 100).toFixed(1).replace('.', ',');
    }

    // ---------------------------------------------------------------------
    // Decade helpers — Dekaden-Arithmetik und Range-Filter.
    // makeDecadeFilter(state) bindet sich an ein Page-State-Objekt, das
    // numerische Felder decadeMin/decadeMax fuehrt (null = kein Filter).
    // ---------------------------------------------------------------------
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

    // ---------------------------------------------------------------------
    // Pipeline-Underscore-Keys ("ueber_gabe") wieder lesbar machen.
    // Umlaut-Recovery muss case-sensitive sein, sonst wird "Uebergabe" nicht
    // zu "Übergabe".
    // ---------------------------------------------------------------------
    function labelize(k) {
        return k.replace(/_/g, ' ')
            .replace(/Ae/g, 'Ä').replace(/Oe/g, 'Ö').replace(/Ue/g, 'Ü')
            .replace(/ae/g, 'ä').replace(/oe/g, 'ö').replace(/ue/g, 'ü');
    }

    // ---------------------------------------------------------------------
    // CSP-sichere Style-Projektion
    // CSP "style-src 'self'" blockiert inline style="..."-Attribute. Wir
    // codieren Werte als data-Attribute und projizieren sie nach jedem
    // innerHTML auf die Element-style-Property (CSP-konform via JS-IDL).
    // Unterstuetzte data-Attribute:
    //   data-w        -> style.width = "<v>%"
    //   data-h        -> style.height = "<v>px"
    //   data-bg       -> style.background = "<v>"
    //   data-bottom   -> style.bottom = "<v>px"
    // ---------------------------------------------------------------------
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

    // ---------------------------------------------------------------------
    // JSON aus eingebettetem <script type="application/json">
    // ---------------------------------------------------------------------
    function readJsonScript(id, fallback) {
        const el = document.getElementById(id);
        if (!el) return fallback || null;
        try { return JSON.parse(el.textContent); }
        catch (e) {
            console.error('Bad JSON in', id, e);
            return fallback || null;
        }
    }

    // ---------------------------------------------------------------------
    // Document-Preprocessing fuer search.json
    // Annotiert jeden Doc mit _dec (parsbare Dekade aus di/d) und liefert
    // {docs, byDecade} fuer schnellen Lookup.
    // ---------------------------------------------------------------------
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

    // docs_lookup.json: file_key (z. B. "f__QGW_0a") -> Doc-Stammdaten
    // {u: url, i: idno, d: display-Datum, c: Korpus-Label, r: Regest}.
    // Fuer Drill-down-Listen, die nur file_keys speichern (drill_down in
    // epic_a/b/c).
    function loadDocsLookup(rootPath) {
        const root = rootPath || (window.ROOT_PATH || '..');
        return fetch(root + '/data/docs_lookup.json').then(r => r.json());
    }

    // ---------------------------------------------------------------------
    // Chip-Active-Toggle-Helper
    // Markiert in einer Chip-Gruppe die zu activeKey passende Schaltflaeche
    // als aktiv (CSS-Klasse + aria-pressed); alle anderen werden zurueck-
    // gesetzt. activeClass default 'active' (Sidebar-Standard); fuer Toggle-
    // Buttons in Quadrant-Headers wird 'is-active' uebergeben.
    // ---------------------------------------------------------------------
    function setActiveChip(group, activeKey, attr, activeClass) {
        if (!group) return;
        activeClass = activeClass || 'active';
        group.querySelectorAll('[' + attr + ']').forEach(b => {
            const isActive = b.getAttribute(attr) === activeKey;
            b.classList.toggle(activeClass, isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
    }

    // ---------------------------------------------------------------------
    // Range-Slider-Binding
    // bindRangeSlider({state, onChange}) bindet auf die per Macro
    // generierten Inputs (#range-min, #range-max). Mutiert
    // state.decadeMin/decadeMax (null wenn voll aufgespannt -> kein Filter).
    // Aktualisiert range-label-min/max + Histogramm-Highlights.
    // onChange wird nach jeder Veraenderung aufgerufen.
    // ---------------------------------------------------------------------
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
            // Slider voll aufgespannt = kein Filter (sonst fallen Daten
            // ohne parsbare Dekade aus den Aggregaten).
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
        // Triggert update() (das von bindRangeSlider angehaengt wurde),
        // welches state.decadeMin/Max auf null setzt + onChange ruft.
        minEl.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
    }

    // ---------------------------------------------------------------------
    // Drill-Down-Overlay
    // Verwendet das drill_down_overlay()-Macro aus macros.html (das bereits
    // CSS, Header, Tabelle, Footer-Count und Schliessen-Button mitbringt).
    // openDrillOverlay({ overlayId, title, fileKeys, docsLookup,
    //                    decadeFilter, note }) populiert die Overlay-Tabelle
    // und macht sie sichtbar. Der Aufrufer hat den Overlay-Schliess-Handler
    // einmal via bindDrillOverlay() initialisiert.
    // ---------------------------------------------------------------------
    function bindDrillOverlay(opts) {
        const id = opts.overlayId;
        const overlay = document.getElementById(id);
        const closeBtn = document.getElementById(id + '-close');
        if (!overlay || !closeBtn) return;
        function close() { overlay.classList.add('hidden'); overlay.setAttribute('aria-hidden', 'true'); }
        closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) close();   // Klick auf Backdrop
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !overlay.classList.contains('hidden')) close();
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

        // file_keys -> Doc-Records, optional nach Dekade filtern (Datum
        // aus dem d-Feld der Lookup-Eintraege; erste 4 Zeichen = Jahr).
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
        // Sortierung nach Datum (d ist YYYY...).
        docs.sort((a, b) => (a.d || '').localeCompare(b.d || ''));

        if (titleEl) titleEl.textContent = opts.title || 'Quellen';
        if (countEl) {
            const noteText = opts.note ? ' · ' + opts.note : '';
            countEl.textContent = fmt(docs.length) + ' Quellen' + noteText;
        }

        if (tbody) {
            const root = (window.ROOT_PATH || '..');
            const SHOW = 500;
            const rows = docs.slice(0, SHOW).map(d => `<tr>
                <td><a href="${root}/${d.u}">${d.i || ''}</a></td>
                <td>${d.d || ''}</td>
                <td>${d.c || ''}</td>
                <td class="cell-regest">${d.r || ''}</td>
            </tr>`);
            if (docs.length > SHOW) {
                rows.push(`<tr><td colspan="4" class="aggregat-empty">… und ${fmt(docs.length - SHOW)} weitere; bitte enger eingrenzen.</td></tr>`);
            }
            tbody.innerHTML = rows.join('') ||
                '<tr><td colspan="4" class="aggregat-empty">Keine Quellen gefunden.</td></tr>';
        }

        overlay.classList.remove('hidden');
        overlay.setAttribute('aria-hidden', 'false');
    }

    // ---------------------------------------------------------------------
    // Active-Filter-Strip
    // renderActiveFilters(containerId, filters) — filters ist eine Array
    // von Objekten {label, onClear}. Pro Eintrag wird eine entfernbare
    // Pille gerendert; Klick ruft onClear.
    // ---------------------------------------------------------------------
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

    // ---------------------------------------------------------------------
    // Public API
    // ---------------------------------------------------------------------
    return {
        // Konstanten
        ROLE_LABELS, ROLE_ORDER, ROLE_COLORS,
        REL_LABELS, REL_ORDER, REL_COLORS,
        SEX_LABELS_DE,
        // Format/Helper
        fmt, pct,
        decadeOf, makeDecadeFilter,
        labelize,
        applyDataStyles,
        setActiveChip,
        // Daten
        readJsonScript,
        preprocessDocs,
        loadSearchJson,
        loadDocsLookup,
        // Sidebar
        bindRangeSlider,
        resetSliderInputs,
        // Filter-Strip
        renderActiveFilters,
        // Drill-Down
        bindDrillOverlay,
        openDrillOverlay,
    };
})();
