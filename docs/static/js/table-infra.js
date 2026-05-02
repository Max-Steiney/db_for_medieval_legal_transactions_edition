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
        if (!searchInput) return;
        let searchTimer;
        // V3 Diakritika: Suchanfrage mit der gleichen Normalisierung
        // versehen wie die Pre-Compute-Strings (umlaut-tolerant).
        let norm = (window.EdCore && EdCore.normForSearch) ||
                   function(s) { return (s || '').toLowerCase(); };
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(function() {
                state.query = norm(searchInput.value.trim());
                searchClear.classList.toggle('hidden', !state.query);
                applyFilters();
            }, 200);
        });
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            state.query = '';
            searchClear.classList.add('hidden');
            applyFilters();
        });
    }


    /* ------------------------------------------------------------------
       Sortable column headers
       ------------------------------------------------------------------ */

    function setupSortHeaders(tableId, state, applyFilters) {
        let headers = document.querySelectorAll('#' + tableId + ' th[data-sort]');
        headers.forEach(function(th) {
            th.addEventListener('click', function() {
                let key = th.getAttribute('data-sort');
                if (state.sortKey === key) {
                    state.sortDir *= -1;
                } else {
                    state.sortKey = key;
                    state.sortDir = 1;
                }
                headers.forEach(function(h) { h.classList.remove('sorted-asc', 'sorted-desc'); });
                th.classList.add(state.sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
                applyFilters();
            });
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
        let chip = document.createElement('span');
        chip.className = 'filter-chip';
        chip.innerHTML = esc(label) + ' <button aria-label="Filter entfernen">\u00D7</button>';
        chip.querySelector('button').addEventListener('click', onRemove);
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
