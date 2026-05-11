/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Shared table infrastructure (range slider, search, sort, renderer, chips)
   ========================================================================== */

let TableInfra = (function() {
    'use strict';

    let esc = EdCore.esc;


    /* ------------------------------------------------------------------
       Range slider with histogram
       ------------------------------------------------------------------ */

    function initRangeSlider(state, applyFilters) {
        let slider = document.getElementById('range-slider');
        if (!slider) return null;

        let rangeMin = document.getElementById('range-min');
        let rangeMax = document.getElementById('range-max');
        let labelMin = document.getElementById('range-label-min');
        let labelMax = document.getElementById('range-label-max');
        let histogram = document.getElementById('range-histogram');
        let bars = histogram ? histogram.querySelectorAll('.range-bar') : [];

        let dataMin = parseInt(slider.dataset.min);
        let dataMax = parseInt(slider.dataset.max);

        state.yearMin = dataMin;
        state.yearMax = dataMax;

        // Track fill element
        let trackFill = document.createElement('div');
        trackFill.className = 'range-track-fill';
        slider.querySelector('.range-inputs').appendChild(trackFill);

        function updateSlider() {
            let minVal = parseInt(rangeMin.value);
            let maxVal = parseInt(rangeMax.value);

            // Prevent crossing
            if (minVal > maxVal) {
                if (this === rangeMin) {
                    rangeMin.value = maxVal;
                    minVal = maxVal;
                } else {
                    rangeMax.value = minVal;
                    maxVal = minVal;
                }
            }

            state.yearMin = minVal;
            state.yearMax = maxVal;

            // Percentages for positioning
            let range = dataMax - dataMin;
            let pctMin = range > 0 ? (minVal - dataMin) / range * 100 : 0;
            let pctMax = range > 0 ? (maxVal - dataMin) / range * 100 : 100;

            // Update labels — position them at handle locations
            labelMin.textContent = minVal;
            labelMax.textContent = maxVal;
            labelMin.style.left = pctMin + '%';
            labelMax.style.left = pctMax + '%';

            // Track fill position
            trackFill.style.left = pctMin + '%';
            trackFill.style.width = (pctMax - pctMin) + '%';

            // Histogram bar opacity
            bars.forEach(function(bar) {
                let decade = parseInt(bar.dataset.decade);
                let decadeEnd = decade + 9;
                if (decade >= minVal && decadeEnd <= maxVal) {
                    bar.className = 'range-bar in-range';
                } else if (decadeEnd < minVal || decade > maxVal) {
                    bar.className = 'range-bar out-of-range';
                } else {
                    bar.className = 'range-bar in-range';
                }
            });

            applyFilters();
        }

        rangeMin.addEventListener('input', updateSlider);
        rangeMax.addEventListener('input', updateSlider);

        // Initial track fill
        updateSlider.call(rangeMin);

        return {
            reset: function() {
                rangeMin.value = dataMin;
                rangeMax.value = dataMax;
                updateSlider.call(rangeMin);
            },
            isFiltered: function() {
                return state.yearMin > dataMin || state.yearMax < dataMax;
            }
        };
    }


    /* ------------------------------------------------------------------
       Debounced search input + clear button
       ------------------------------------------------------------------ */

    function setupSearch(state, applyFilters) {
        let searchInput = document.getElementById('search-input');
        let searchClear = document.getElementById('search-clear');
        if (!searchInput) return null;
        let searchTimer;
        // V3 diacritics: apply the same normalization to the search query
        // as to the pre-computed strings (umlaut-tolerant).
        let norm = (window.EdCore && EdCore.normForSearch) ||
                   function(s) { return (s || '').toLowerCase(); };
        function setClearVisible(visible) {
            if (searchClear) searchClear.classList.toggle('hidden', !visible);
        }
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(function() {
                state.query = norm(searchInput.value.trim());
                setClearVisible(!!state.query);
                applyFilters();
            }, 200);
        });
        if (searchClear) {
            searchClear.addEventListener('click', function() {
                searchInput.value = '';
                state.query = '';
                setClearVisible(false);
                applyFilters();
            });
        }
        // Returns a handle analogous to initRangeSlider so callers can
        // reset the input from elsewhere (global reset button) without
        // duplicating the DOM lookups and visibility toggle.
        return {
            reset: function() {
                clearTimeout(searchTimer);
                searchInput.value = '';
                state.query = '';
                setClearVisible(false);
            },
            // Programmatic set: used when another control (e.g. the
            // hash-jump on register pages) wants to constrain the table
            // via the search field. Displays the unnormalised text in
            // the input, but writes the normalised form into state.
            set: function(rawValue) {
                clearTimeout(searchTimer);
                let raw = rawValue == null ? '' : String(rawValue);
                searchInput.value = raw;
                state.query = norm(raw.trim());
                setClearVisible(!!state.query);
            }
        };
    }


    /* ------------------------------------------------------------------
       Sortable column headers
       ------------------------------------------------------------------ */

    function setupSortHeaders(tableId, state, applyFilters) {
        let headers = document.querySelectorAll('#' + tableId + ' th[data-sort]');
        headers.forEach(function(th) {
            th.addEventListener('click', function(e) {
                // Clicks on the provenance trigger (i icon) or its popover
                // must NOT trigger sorting — they open the source citation
                // and are a different interaction path than column sort.
                if (e.target.closest('.tip-trigger, .tip-popover')) return;
                let key = th.getAttribute('data-sort');
                if (state.sortKey === key) {
                    state.sortDir *= -1;
                } else {
                    state.sortKey = key;
                    state.sortDir = 1;
                }
                headers.forEach(function(h) {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                    h.setAttribute('aria-sort', 'none');
                });
                th.classList.add(state.sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
                th.setAttribute('aria-sort', state.sortDir === 1 ? 'ascending' : 'descending');
                applyFilters();
            });
            th.setAttribute('aria-sort', 'none');
        });
    }


    /* ------------------------------------------------------------------
       Progressive-rendering table engine
       config: {tbodyId, noResultsId, colCount, renderRow(item, index, tr)}
       Returns {render(items)}
       ------------------------------------------------------------------ */

    function createTableRenderer(config) {
        let tbody = document.getElementById(config.tbodyId);
        let noResults = document.getElementById(config.noResultsId);
        let batchSize = config.batchSize || 100;
        let renderedCount = 0;
        let observer = null;
        let items = [];

        function renderTable() {
            tbody.innerHTML = '';
            renderedCount = 0;
            if (items.length === 0) { noResults.classList.remove('hidden'); return; }
            noResults.classList.add('hidden');
            renderBatch();
            setupScrollObserver();
        }

        function renderBatch() {
            let end = Math.min(renderedCount + batchSize, items.length);
            let fragment = document.createDocumentFragment();
            for (let i = renderedCount; i < end; i++) {
                let tr = document.createElement('tr');
                config.renderRow(items[i], i, tr);
                fragment.appendChild(tr);
            }
            tbody.appendChild(fragment);
            renderedCount = end;
        }

        function setupScrollObserver() {
            if (observer) observer.disconnect();
            if (renderedCount >= items.length) return;
            let sentinel = document.createElement('tr');
            sentinel.className = 'scroll-sentinel';
            sentinel.innerHTML = '<td colspan="' + config.colCount + '" class="table-sentinel"></td>';
            tbody.appendChild(sentinel);
            observer = new IntersectionObserver(function(entries) {
                if (entries[0].isIntersecting && renderedCount < items.length) {
                    sentinel.remove();
                    renderBatch();
                    setupScrollObserver();
                }
            }, { rootMargin: '200px' });
            observer.observe(sentinel);
        }

        return {
            render: function(filteredItems) {
                items = filteredItems;
                renderTable();
            }
        };
    }


    /* ------------------------------------------------------------------
       Filter chip
       ------------------------------------------------------------------ */

    function addFilterChip(container, label, onRemove) {
        // Click anywhere on the pill removes the filter \u2014 looks like a
        // removable tag and acts like one. A dedicated \u2715 button stays
        // for screen readers and as a visual affordance signal.
        let chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'filter-chip';
        chip.setAttribute('aria-label', label + ' entfernen');
        chip.innerHTML =
            '<span class="filter-chip-label">' + esc(label) + '</span>' +
            '<span class="filter-chip-x" aria-hidden="true">\u00D7</span>';
        chip.addEventListener('click', onRemove);
        container.appendChild(chip);
    }


    /* ------------------------------------------------------------------
       Public API
       ------------------------------------------------------------------ */

    return {
        initRangeSlider: initRangeSlider,
        setupSearch: setupSearch,
        setupSortHeaders: setupSortHeaders,
        createTableRenderer: createTableRenderer,
        addFilterChip: addFilterChip
    };

})();

// CommonJS export for Vitest.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TableInfra };
}
