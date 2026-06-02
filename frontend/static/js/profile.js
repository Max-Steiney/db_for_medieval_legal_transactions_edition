/* Entity profile progressive enhancement: table truncation (rows beyond
 * data-truncate-at get .is-overflow plus a toggle button) and click-to-sort
 * columns (DOM-based, sort values from td[data-sort-value]). All sections are
 * fully server-rendered; the JS only improves the view.
 */

(function () {
    'use strict';

    function reapplyTruncationMarks(table) {
        var threshold = parseInt(table.getAttribute('data-truncate-at') || '0', 10);
        if (!threshold) return;
        var rows = table.querySelectorAll('tbody > tr');
        rows.forEach(function (row, i) {
            row.classList.toggle('is-overflow', i >= threshold);
        });
    }

    function applyTruncation(table) {
        var threshold = parseInt(table.getAttribute('data-truncate-at') || '0', 10);
        if (!threshold) return;
        var rows = table.querySelectorAll('tbody > tr');
        if (rows.length <= threshold) return;
        rows.forEach(function (row, i) {
            if (i >= threshold) row.classList.add('is-overflow');
        });
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'table-toggle';
        btn.textContent = 'Alle ' + rows.length + ' Zeilen anzeigen';
        btn.setAttribute('aria-expanded', 'false');
        btn.addEventListener('click', function () {
            var expanded = table.classList.toggle('is-expanded');
            btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
            btn.textContent = expanded
                ? 'Weniger anzeigen'
                : 'Alle ' + rows.length + ' Zeilen anzeigen';
        });
        table.insertAdjacentElement('afterend', btn);
    }

    // Comparison primitives live in EdCore; this is only the DOM part:
    // read data-sort-value per td, sort the tr, re-mark truncation.
    function cellValue(tr, colIndex) {
        var td = tr.children[colIndex];
        if (!td) return '';
        var v = td.getAttribute('data-sort-value');
        return v !== null ? v : td.textContent.trim();
    }

    function setupSortableTable(table) {
        var allHeaders = Array.prototype.slice.call(table.querySelectorAll('thead th'));
        var sortHeaders = allHeaders.filter(function (h) { return h.hasAttribute('data-sort'); });
        if (!sortHeaders.length) return;
        var tbody = table.querySelector('tbody');
        if (!tbody) return;

        // Cache column index per data-sort key once (O(n) instead of O(n^2)
        // per sort click).
        var indexByKey = {};
        sortHeaders.forEach(function (h) {
            indexByKey[h.getAttribute('data-sort')] = allHeaders.indexOf(h);
        });

        // Remember the default (server-side, usually chronological) order.
        var originalOrder = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
        var state = { key: null, dir: 1 };

        function applySort() {
            var rows;
            if (state.key === null) {
                rows = originalOrder.slice();
            } else {
                var colIndex = indexByKey[state.key];
                if (colIndex < 0 || colIndex === undefined) return;
                rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
                rows.sort(function (a, b) {
                    return EdCore.compareValues(cellValue(a, colIndex), cellValue(b, colIndex), state.dir);
                });
            }
            var frag = document.createDocumentFragment();
            rows.forEach(function (tr) { frag.appendChild(tr); });
            tbody.appendChild(frag);
            // Re-mark truncation at the new positions so "first N rows"
            // matches the current sort order.
            reapplyTruncationMarks(table);
        }

        sortHeaders.forEach(function (th) {
            th.addEventListener('click', function (e) {
                if (e.target.closest('.tip-trigger, .tip-popover')) return;
                var key = th.getAttribute('data-sort');
                if (state.key === key) {
                    if (state.dir === 1) {
                        state.dir = -1;
                    } else {
                        // Third click: clear the sort.
                        state.key = null;
                        state.dir = 1;
                    }
                } else {
                    state.key = key;
                    state.dir = 1;
                }
                sortHeaders.forEach(function (h) {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                    h.setAttribute('aria-sort', 'none');
                });
                if (state.key !== null) {
                    th.classList.add(state.dir === 1 ? 'sorted-asc' : 'sorted-desc');
                    th.setAttribute('aria-sort', state.dir === 1 ? 'ascending' : 'descending');
                }
                applySort();
            });
            th.setAttribute('aria-sort', 'none');
        });
    }

    function applySortableTables() {
        document.querySelectorAll('table.sortable-table').forEach(setupSortableTable);
    }

    function init() {
        document.querySelectorAll('table[data-truncate-at]').forEach(applyTruncation);
        applySortableTables();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
