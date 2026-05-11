/* Entity-Profil-Interaktivitaet.
 *
 * Drei progressive-enhancement-Aufgaben:
 *
 *  1. Tabellen-Truncation: rel-table und person-source-table tragen ein
 *     data-truncate-at-Attribut, wenn der Server mehr Zeilen als die
 *     Schwelle gerendert hat. Ueberzaehlige tr bekommen .is-overflow,
 *     ein Toggle-Button expandiert/zusammenfaltet die Tabelle.
 *
 *  2. Quick-Filter: ein .table-filter-input ueber einer Tabelle (rel
 *     oder src) filtert die Zeilen substringweise nach textContent. Bei
 *     aktivem Filter wird die Truncation aufgehoben, damit Matches
 *     jenseits der Schwelle nicht versteckt bleiben.
 *
 *  3. Spalten-Sortierung: Tabellen mit .sortable-table und th[data-sort]
 *     reagieren auf Klicks im Header. Sortier-Werte kommen aus
 *     data-sort-value am td (ISO-Datum fuer chronologisch, sonst
 *     textContent), Default-Reihenfolge ist die serverseitige (meist
 *     chronologisch). Mechanik analog zu setupSortHeaders in
 *     table-infra.js, aber DOM-basiert statt array-basiert. Nach Sort
 *     wird die Truncate-Markierung neu vergeben, damit "erste N Zeilen"
 *     immer die ersten N nach aktueller Sortierung sind.
 *
 * Kein Framework, kein Build-Step, kein State ausserhalb des DOM. Alle
 * Sektionen sind serverseitig vollstaendig gerendert; das JS verbessert
 * nur die Sicht.
 *
 * Genannt-als-Bezeichnungen sind im aktuellen Markup ein <details>-
 * Element, das ohne JS kollabiert/aufklappt. Frueher gab es hier eine
 * separate Toggle-Logik (applySourceTitlesCollapse); die ist mit dem
 * Header-Refactor entfallen.
 */

(function () {
    'use strict';

    /* ----------------------------------------------------------------
       Truncate
       ---------------------------------------------------------------- */

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

    /* ----------------------------------------------------------------
       Quick-Filter
       ---------------------------------------------------------------- */

    function findNearestTable(input) {
        // Jede Filter-Section enthaelt genau eine Tabelle (rel-table oder
        // person-source-table). querySelector('table') reicht.
        var scope = input.closest('section') || input.parentElement;
        return scope ? scope.querySelector('table') : null;
    }

    function applyQuickFilters() {
        document.querySelectorAll('.table-filter-input').forEach(function (input) {
            var table = findNearestTable(input);
            if (!table) return;
            var status = input.parentElement.querySelector('.table-filter-status');
            var rows = Array.prototype.slice.call(table.querySelectorAll('tbody > tr'));
            var total = rows.length;

            function update() {
                var q = (input.value || '').trim().toLowerCase();
                var matched = 0;
                if (q.length === 0) {
                    rows.forEach(function (r) { r.classList.remove('row-hidden'); });
                    table.classList.remove('is-filtering');
                    matched = total;
                } else {
                    table.classList.add('is-filtering');
                    rows.forEach(function (r) {
                        var hay = (r.textContent || '').toLowerCase();
                        if (hay.indexOf(q) === -1) {
                            r.classList.add('row-hidden');
                        } else {
                            r.classList.remove('row-hidden');
                            matched += 1;
                        }
                    });
                }
                if (status) {
                    status.textContent = q
                        ? matched + ' von ' + total + ' Zeilen'
                        : '';
                }
            }
            input.addEventListener('input', update);
        });
    }

    /* ----------------------------------------------------------------
       Spalten-Sortierung
       ---------------------------------------------------------------- */

    function sortKey(s) {
        return String(s || '')
            .replace(/[\[\]]/g, '')
            .replace(/^[\s,;:]+|[\s,;:]+$/g, '')
            .toLowerCase();
    }

    function cellValue(tr, colIndex) {
        var td = tr.children[colIndex];
        if (!td) return '';
        var v = td.getAttribute('data-sort-value');
        return v !== null ? v : td.textContent.trim();
    }

    var NUM_RE = /^-?\d+(\.\d+)?$/;

    function compareCells(va, vb, dir) {
        var aEmpty = (va === '' || va === '-');
        var bEmpty = (vb === '' || vb === '-');
        if (aEmpty && bEmpty) return 0;
        if (aEmpty) return 1;
        if (bEmpty) return -1;
        // Numerisch vergleichen, wenn beide Werte reine Zahlen sind
        // (Signatur-Nummern wie 49, 185, 1599).
        if (NUM_RE.test(va) && NUM_RE.test(vb)) {
            return (Number(va) - Number(vb)) * dir;
        }
        return sortKey(va).localeCompare(sortKey(vb), 'de') * dir;
    }

    function setupSortableTable(table) {
        var allHeaders = Array.prototype.slice.call(table.querySelectorAll('thead th'));
        var sortHeaders = allHeaders.filter(function (h) { return h.hasAttribute('data-sort'); });
        if (!sortHeaders.length) return;
        var tbody = table.querySelector('tbody');
        if (!tbody) return;

        // Spalten-Index pro data-sort-Key einmal cachen (O(n) statt O(n^2)
        // pro Sort-Klick).
        var indexByKey = {};
        sortHeaders.forEach(function (h) {
            indexByKey[h.getAttribute('data-sort')] = allHeaders.indexOf(h);
        });

        // Default-Reihenfolge (serverseitig, meist chronologisch) merken.
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
                    return compareCells(cellValue(a, colIndex), cellValue(b, colIndex), state.dir);
                });
            }
            var frag = document.createDocumentFragment();
            rows.forEach(function (tr) { frag.appendChild(tr); });
            tbody.appendChild(frag);
            // Truncate-Markierung an neuer Position vergeben, damit "erste
            // 50 Zeilen" zur aktuellen Sortierung passt.
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
                        // Dritter Klick: Sortierung zuruecknehmen.
                        state.key = null;
                        state.dir = 1;
                    }
                } else {
                    state.key = key;
                    state.dir = 1;
                }
                sortHeaders.forEach(function (h) {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                });
                if (state.key !== null) {
                    th.classList.add(state.dir === 1 ? 'sorted-asc' : 'sorted-desc');
                }
                applySort();
            });
        });
    }

    function applySortableTables() {
        document.querySelectorAll('table.sortable-table').forEach(setupSortableTable);
    }

    /* ----------------------------------------------------------------
       Init
       ---------------------------------------------------------------- */

    function init() {
        document.querySelectorAll('table[data-truncate-at]').forEach(applyTruncation);
        applyQuickFilters();
        applySortableTables();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
