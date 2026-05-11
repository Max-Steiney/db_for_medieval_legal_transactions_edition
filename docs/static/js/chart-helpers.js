/* ==========================================================================
   Stadt und Gemeinschaft Wien — Digital Edition
   ChartHelpers: shared SVG chart utilities for statistics + exploration
   ========================================================================== */

let ChartHelpers = (function() {
    'use strict';

    let SVG_NS = 'http://www.w3.org/2000/svg';

    /* ------------------------------------------------------------------
       SVG element factory
       ------------------------------------------------------------------ */

    function svgEl(tag, attrs) {
        let el = document.createElementNS(SVG_NS, tag);
        if (attrs) {
            for (let k in attrs) {
                if (attrs.hasOwnProperty(k)) el.setAttribute(k, attrs[k]);
            }
        }
        return el;
    }


    /* ------------------------------------------------------------------
       CSS custom property reader (returns trimmed string)
       ------------------------------------------------------------------ */

    function getToken(name) {
        return getComputedStyle(document.documentElement)
            .getPropertyValue(name).trim();
    }


    /* ------------------------------------------------------------------
       German number formatting (thousands separator: ".")
       ------------------------------------------------------------------ */

    function fmt(n) {
        return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }


    /* ------------------------------------------------------------------
       Tooltip system — one tooltip per context (class name)
       ------------------------------------------------------------------ */

    let tooltips = {};

    /**
     * Create (or retrieve) a tooltip element for a given CSS class.
     * Appends to document.body on first call; reuses on subsequent calls.
     */
    function createTooltip(className) {
        if (tooltips[className]) return tooltips[className];
        let el = document.createElement('div');
        el.className = className;
        document.body.appendChild(el);
        tooltips[className] = { el: el, timer: null, hovered: false };

        // WCAG 1.4.13: keep tooltip visible while pointer is over it
        el.addEventListener('mouseenter', function() {
            tooltips[className].hovered = true;
            if (tooltips[className].timer) {
                clearTimeout(tooltips[className].timer);
                tooltips[className].timer = null;
            }
        });
        el.addEventListener('mouseleave', function() {
            tooltips[className].hovered = false;
            hideTooltip(className);
        });

        // Dismiss on touch outside
        document.addEventListener('touchstart', function(e) {
            if (!el.contains(e.target) && !e.target.closest('[data-tip]')) {
                hideTooltip(className);
            }
        });

        // WCAG 1.4.13: dismiss on Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') hideTooltip(className);
        });

        return tooltips[className];
    }

    /**
     * Show tooltip with HTML content at (x, y) client coords.
     * Repositions to avoid overflow.
     */
    function showTooltip(className, html, x, y) {
        let t = tooltips[className];
        if (!t) return;
        let el = t.el;
        el.innerHTML = html;
        el.classList.add('visible');

        let w = el.offsetWidth;
        let h = el.offsetHeight;
        let tx = x + 14;
        let ty = y + 18;
        if (tx + w > window.innerWidth - 8) tx = x - w - 8;
        if (ty + h > window.innerHeight - 8) ty = y - h - 8;
        el.style.left = tx + 'px';
        el.style.top = ty + 'px';
    }

    /**
     * Reposition an already-visible tooltip (mousemove handler).
     * Does NOT change innerHTML — just moves the element.
     */
    function moveTooltip(className, x, y) {
        let t = tooltips[className];
        if (!t) return;
        let el = t.el;
        let w = el.offsetWidth;
        let h = el.offsetHeight;
        let tx = x + 14;
        let ty = y + 18;
        if (tx + w > window.innerWidth - 8) tx = x - w - 8;
        if (ty + h > window.innerHeight - 8) ty = y - h - 8;
        el.style.left = tx + 'px';
        el.style.top = ty + 'px';
    }

    /**
     * Hide tooltip and clear any auto-dismiss timer.
     */
    function hideTooltip(className, force) {
        let t = tooltips[className];
        if (!t) return;
        // Don't hide while user is hovering the tooltip (unless forced)
        if (t.hovered && !force) return;
        t.el.classList.remove('visible');
        if (t.timer) { clearTimeout(t.timer); t.timer = null; }
    }

    /**
     * Show tooltip briefly on touch (auto-dismiss after ms).
     */
    function touchTooltip(className, html, x, y, ms) {
        showTooltip(className, html, x, y);
        let t = tooltips[className];
        if (t) t.timer = setTimeout(function() { hideTooltip(className); }, ms || 3000);
    }


    /* ------------------------------------------------------------------
       Shared label & colour maps (canonical across statistics + exploration)
       ------------------------------------------------------------------ */

    let ROLE_LABELS = {
        issuer: 'Aussteller:innen', recipient: 'Empf\u00e4nger:innen',
        witness: 'Zeug:innen', other: 'Sonstige'
    };
    let ROLE_ORDER = ['issuer', 'recipient', 'witness', 'other'];

    let SEX_LABELS = { m: 'M\u00e4nnlich', f: 'Weiblich', unspecified: 'Keine Angabe' };

    let _sexColors = null;
    function sexColors() {
        if (_sexColors) return _sexColors;
        _sexColors = {
            m: getToken('--color-sex-m-muted') || '#5a7fa0',
            f: getToken('--color-sex-f-muted') || '#b8696e',
            unspecified: getToken('--color-text-light') || '#b0a99f'
        };
        return _sexColors;
    }


    /* ------------------------------------------------------------------
       Dual-handle range slider fill
       ------------------------------------------------------------------ */

    function updateRangeFill(idPrefix) {
        let minInput = document.getElementById(idPrefix + '-range-min');
        let maxInput = document.getElementById(idPrefix + '-range-max');
        let fill = document.getElementById(idPrefix + '-range-fill');
        if (!minInput || !maxInput || !fill) return;
        let lo = parseFloat(minInput.value);
        let hi = parseFloat(maxInput.value);
        let min = parseFloat(minInput.min);
        let max = parseFloat(minInput.max);
        let range = max - min;
        if (range <= 0) return;
        if (lo > hi) { let t = lo; lo = hi; hi = t; }
        let left = ((lo - min) / range) * 100;
        let right = ((hi - min) / range) * 100;
        fill.style.left = left + '%';
        fill.style.width = (right - left) + '%';
    }


    /* ------------------------------------------------------------------
       Shared exploration helpers — extracted from per-Epic JS files
       ------------------------------------------------------------------ */

    /**
     * Load a JSON file with loading/error indicator in a container.
     * @param {string} url - fetch URL (e.g. './data/roles.json')
     * @param {string|HTMLElement} container - element or ID to show loading/error
     * @param {function} callback - called with parsed data on success
     */
    function loadJSON(url, container, callback) {
        let el = typeof container === 'string' ? document.getElementById(container) : container;
        if (el) el.innerHTML = '<p class="cell-placeholder">Daten werden geladen\u2026</p>';
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) { callback(data); })
            .catch(function(err) {
                console.warn('Daten konnten nicht geladen werden (' + url + '):', err);
                if (el) el.innerHTML = '<p class="cell-placeholder">Daten konnten nicht geladen werden.</p>';
            });
    }

    /**
     * Bind a dual-handle time range slider with gap note logic.
     * @param {string} idPrefix - element ID prefix (e.g. 'explore' or 'explore-rel')
     * @param {object} state - state object with decadeMin/decadeMax properties
     * @param {function} onChange - called after state update
     * @returns {object|null} - {rangeMin, rangeMax} elements or null
     */
    function bindTimeRange(idPrefix, state, onChange) {
        let rangeMin = document.getElementById(idPrefix + '-range-min');
        let rangeMax = document.getElementById(idPrefix + '-range-max');
        let rangeDisplay = document.getElementById(idPrefix + '-range-display');
        let gapNote = document.getElementById(idPrefix + '-gap-note');
        if (!rangeMin || !rangeMax) return null;

        function update() {
            let lo = parseInt(rangeMin.value, 10);
            let hi = parseInt(rangeMax.value, 10);
            if (lo > hi) { let tmp = lo; lo = hi; hi = tmp; }
            state.decadeMin = lo;
            state.decadeMax = hi;
            if (rangeDisplay) rangeDisplay.textContent = lo + '\u2013' + hi;
            updateRangeFill(idPrefix);
            if (gapNote) {
                if (lo <= 1440 && hi >= 1410) {
                    gapNote.classList.remove('hidden');
                } else {
                    gapNote.classList.add('hidden');
                }
            }
            if (onChange) onChange();
        }
        rangeMin.addEventListener('input', update);
        rangeMax.addEventListener('input', update);
        updateRangeFill(idPrefix);
        return { rangeMin: rangeMin, rangeMax: rangeMax };
    }

    /**
     * Bind filter chip buttons (toggle active class, update state, call callback).
     * @param {string} selector - CSS selector for chip container (e.g. '#explore-sex-filter .explore-chip')
     * @param {string} dataAttr - data attribute name (e.g. 'data-sex')
     * @param {object} state - state object
     * @param {string} stateKey - key in state to update (e.g. 'sexFilter')
     * @param {function} onChange - called after state update
     */
    function bindChipFilter(selector, dataAttr, state, stateKey, onChange) {
        let chips = document.querySelectorAll(selector);
        for (let i = 0; i < chips.length; i++) {
            chips[i].addEventListener('click', function() {
                for (let j = 0; j < chips.length; j++) chips[j].classList.remove('active');
                this.classList.add('active');
                state[stateKey] = this.getAttribute(dataAttr);
                if (onChange) onChange();
            });
        }
    }

    /**
     * Bind a chart/table toggle button.
     * @param {string} toggleId - button element ID
     * @param {string} chartId - chart container ID
     * @param {string} tableId - table container ID
     * @param {object} state - state object
     * @param {string} stateKey - boolean key in state (e.g. 'tableView')
     * @param {function} renderTable - called when switching to table view
     */
    function bindToggle(toggleId, chartId, tableId, state, stateKey, renderTable) {
        let toggle = document.getElementById(toggleId);
        let chartWrap = document.getElementById(chartId);
        let tableWrap = document.getElementById(tableId);
        if (!toggle || !chartWrap || !tableWrap) return;
        toggle.addEventListener('click', function() {
            state[stateKey] = !state[stateKey];
            chartWrap.classList.toggle('hidden', state[stateKey]);
            tableWrap.classList.toggle('hidden', !state[stateKey]);
            if (state[stateKey] && renderTable) renderTable();
        });
    }

    /**
     * Bind a search input with debounce.
     * @param {string} inputId - input element ID
     * @param {function} callback - called with trimmed value
     * @param {number} [delay=200] - debounce delay in ms
     */
    function bindSearch(inputId, callback, delay) {
        let input = document.getElementById(inputId);
        if (!input) return;
        let timer = null;
        input.addEventListener('input', function() {
            clearTimeout(timer);
            timer = setTimeout(function() {
                callback(input.value.toLowerCase().trim());
            }, delay || 200);
        });
    }

    /**
     * Bind sortable table headers (click toggles sort direction).
     * @param {string} tableSelector - CSS selector for sortable th elements
     * @param {object} state - state with sortKey and sortAsc properties
     * @param {string} sortKeyProp - state property name for sort key
     * @param {string} sortAscProp - state property name for sort direction
     * @param {function} renderFn - called after sort change
     * @param {Array} [textDefaults] - sort keys that default to ascending
     */
    function bindSortHeaders(tableSelector, state, sortKeyProp, sortAscProp, renderFn, textDefaults) {
        let headers = document.querySelectorAll(tableSelector);
        let textKeys = textDefaults || [];
        for (let i = 0; i < headers.length; i++) {
            headers[i].style.cursor = 'pointer';
            (function(header) {
                header.addEventListener('click', function() {
                    let key = header.getAttribute('data-sort');
                    if (state[sortKeyProp] === key) {
                        state[sortAscProp] = !state[sortAscProp];
                    } else {
                        state[sortKeyProp] = key;
                        state[sortAscProp] = textKeys.indexOf(key) >= 0;
                    }
                    // Update sort arrows + aria-sort
                    for (let j = 0; j < headers.length; j++) {
                        let arrow = headers[j].querySelector('.sort-arrow');
                        if (headers[j] === header) {
                            if (arrow) arrow.textContent = state[sortAscProp] ? ' \u2191' : ' \u2193';
                            headers[j].setAttribute('aria-sort', state[sortAscProp] ? 'ascending' : 'descending');
                        } else {
                            if (arrow) arrow.textContent = '';
                            headers[j].setAttribute('aria-sort', 'none');
                        }
                    }
                    renderFn();
                });
            })(headers[i]);
        }
    }

    /**
     * Render a horizontal bar chart (single-colour or grouped by segment).
     * @param {HTMLElement} container - target element (will be cleared)
     * @param {object} config
     * @param {Array} config.items - [{label, segments: [{key, value, color}], total}]
     *   For single-colour bars: segments has 1 entry.
     * @param {number} [config.labelWidth=120] - label column width
     * @param {number} [config.barHeight=24] - bar height
     * @param {number} [config.barGap=2] - gap between bars within a group
     * @param {number} [config.groupGap=16] - gap between groups
     * @param {string} [config.ariaLabel] - SVG aria-label
     * @param {string} [config.tooltipClass] - CSS class for tooltip (e.g. 'explore-tooltip')
     * @param {function} [config.onTip] - (item, segment, e) -> tooltip HTML string
     * @param {function} [config.onClick] - (item, segment) -> void
     * @param {Array} [config.legend] - [{label, color}] for legend
     */
    function renderHorizontalBars(container, config) {
        container.innerHTML = '';
        let items = config.items || [];
        if (!items.length) return;

        let labelW = config.labelWidth || 120;
        let barH = config.barHeight || 24;
        let barGap = config.barGap || 2;
        let groupGap = config.groupGap || 16;
        let chartW = container.clientWidth - labelW - 80;
        if (chartW < 150) chartW = 150;

        // Find max value for scaling
        let maxVal = 0;
        for (let mi = 0; mi < items.length; mi++) {
            let segs = items[mi].segments;
            for (let si = 0; si < segs.length; si++) {
                if (segs[si].value > maxVal) maxVal = segs[si].value;
            }
        }
        if (maxVal === 0) maxVal = 1;

        // Legend
        if (config.legend) {
            let legendDiv = document.createElement('div');
            legendDiv.className = 'explore-legend';
            for (let li = 0; li < config.legend.length; li++) {
                let lItem = document.createElement('span');
                lItem.className = 'explore-legend-item';
                let swatch = document.createElement('span');
                swatch.className = 'explore-legend-swatch';
                swatch.style.setProperty('--swatch-color', config.legend[li].color);
                lItem.appendChild(swatch);
                lItem.appendChild(document.createTextNode(config.legend[li].label));
                legendDiv.appendChild(lItem);
            }
            container.appendChild(legendDiv);
        }

        // Compute total height
        let totalH = 0;
        for (let hi = 0; hi < items.length; hi++) {
            totalH += items[hi].segments.length * (barH + barGap) + groupGap;
        }

        // Responsive label width: shrink on narrow containers
        if (container.clientWidth < 400) labelW = Math.max(80, Math.floor(container.clientWidth * 0.25));

        let svg = document.createElementNS(SVG_NS, 'svg');
        svg.setAttribute('width', labelW + chartW + 80);
        svg.setAttribute('height', totalH);
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', config.ariaLabel || 'Balkendiagramm');
        svg.style.display = 'block';

        let y = 0;
        for (let gi = 0; gi < items.length; gi++) {
            let item = items[gi];
            let segs = item.segments;

            // Group label
            let label = document.createElementNS(SVG_NS, 'text');
            label.setAttribute('x', labelW - 8);
            label.setAttribute('y', y + segs.length * (barH + barGap) / 2 + 5);
            label.setAttribute('text-anchor', 'end');
            label.setAttribute('class', 'explore-bar-label');
            if (config.labelFontSize) label.setAttribute('font-size', config.labelFontSize);
            label.textContent = item.label;
            svg.appendChild(label);

            for (let bi = 0; bi < segs.length; bi++) {
                let seg = segs[bi];
                let barW = Math.max(2, (seg.value / maxVal) * chartW);

                let rect = document.createElementNS(SVG_NS, 'rect');
                rect.setAttribute('x', labelW);
                rect.setAttribute('y', y);
                rect.setAttribute('width', barW);
                rect.setAttribute('height', barH);
                rect.setAttribute('rx', 2);
                rect.setAttribute('fill', seg.color);
                rect.setAttribute('class', 'explore-bar');

                // Tooltip + click via closure
                (function(itm, sg, bw) {
                    let tipCls = config.tooltipClass || 'explore-tooltip';
                    if (config.onTip) {
                        rect.addEventListener('mouseenter', function(e) {
                            showTooltip(tipCls, config.onTip(itm, sg, e), e.clientX, e.clientY);
                        });
                        rect.addEventListener('mousemove', function(e) {
                            moveTooltip(tipCls, e.clientX, e.clientY);
                        });
                        rect.addEventListener('mouseleave', function() {
                            hideTooltip(tipCls);
                        });
                    }
                    if (config.onClick) {
                        rect.addEventListener('click', function() {
                            config.onClick(itm, sg);
                        });
                    }
                })(item, seg, barW);

                svg.appendChild(rect);

                // Value label
                let valLabel = document.createElementNS(SVG_NS, 'text');
                valLabel.setAttribute('x', labelW + barW + 6);
                valLabel.setAttribute('y', y + barH / 2 + 4);
                valLabel.setAttribute('class', 'explore-bar-value');
                valLabel.textContent = seg.value.toLocaleString('de-DE');
                svg.appendChild(valLabel);

                y += barH + barGap;
            }
            y += groupGap;
        }
        container.appendChild(svg);
    }


    /* ------------------------------------------------------------------
       Public API
       ------------------------------------------------------------------ */

    return {
        SVG_NS: SVG_NS,
        svgEl: svgEl,
        getToken: getToken,
        fmt: fmt,
        ROLE_LABELS: ROLE_LABELS,
        ROLE_ORDER: ROLE_ORDER,
        SEX_LABELS: SEX_LABELS,
        sexColors: sexColors,
        createTooltip: createTooltip,
        showTooltip: showTooltip,
        moveTooltip: moveTooltip,
        hideTooltip: hideTooltip,
        touchTooltip: touchTooltip,
        updateRangeFill: updateRangeFill,
        loadJSON: loadJSON,
        bindTimeRange: bindTimeRange,
        bindChipFilter: bindChipFilter,
        bindToggle: bindToggle,
        bindSearch: bindSearch,
        bindSortHeaders: bindSortHeaders,
        renderHorizontalBars: renderHorizontalBars
    };

})();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartHelpers };
}
