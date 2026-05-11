/* Entity-Profil-Interaktivitaet.
 *
 * Vier progressive-enhancement-Aufgaben:
 *
 *  1. Quellen-Titel-Chips: bei vielen Belegungen (vgl. org__wien mit 439
 *     Chips) wird nur das erste Kontingent gezeigt; ein Toggle blendet
 *     den Rest ein. Die Schwelle steht im data-collapsible-Attribut.
 *
 *  2. Tabellen-Truncation: rel-table und person-source-table tragen ein
 *     data-truncate-at-Attribut, wenn der Server mehr Zeilen als die
 *     Schwelle gerendert hat. Wir markieren ueberzaehlige tr mit
 *     .is-overflow und liefern einen Toggle-Button, der die Tabelle
 *     expandiert/zusammenfaltet.
 *
 *  3. Quick-Filter: ein .table-filter-input ueber einer Tabelle (rel
 *     oder src) filtert die Zeilen substringweise nach textContent. Bei
 *     aktivem Filter wird die Truncation aufgehoben, damit Matches
 *     jenseits der Schwelle nicht versteckt bleiben.
 *
 *  4. Spalten-Sortierung: Tabellen mit .sortable-table und th[data-sort]
 *     reagieren auf Klicks im Header. Sortier-Werte kommen aus
 *     data-sort-value am td (ISO-Datum fuer chronologisch, sonst
 *     textContent), Default-Reihenfolge ist die serverseitige (meist
 *     chronologisch). Mechanik analog zu setupSortHeaders in
 *     table-infra.js, aber DOM-basiert statt array-basiert.
 *
 * Kein Framework, kein Build-Step, kein State ausserhalb des DOM. Alle
 * Sektionen sind serverseitig vollstaendig gerendert; das JS verbessert
 * nur die Sicht.
 */

(function () {
    'use strict';

    function findNearestTable(input) {
        // sucht im aktuellen Section-Container die naechstgelegene Tabelle
        var target = input.getAttribute('data-target') || '';
        var scope = input.closest('section') || input.parentElement;
        if (!scope) return null;
        if (target === 'rel')  return scope.querySelector('.rel-table');
        if (target === 'src')  return scope.querySelector('.person-source-table');
        return scope.querySelector('table');
    }

    function applyTruncation(table) {
        var threshold = parseInt(table.getAttribute('data-truncate-at') || '0', 10);
        if (!threshold) return;
        var rows = table.querySelectorAll('tbody > tr');
        rows.forEach(function (row, i) {
            if (i >= threshold) row.classList.add('is-overflow');
        });
        // Toggle-Button anhaengen
        var hidden = rows.length - threshold;
        if (hidden <= 0) return;
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

    function applySourceTitlesCollapse() {
        document.querySelectorAll('.person-titles[data-collapsible]').forEach(function (el) {
            var threshold = parseInt(el.getAttribute('data-collapsible') || '0', 10);
            if (!threshold) return;
            var chips = el.querySelectorAll('.pt-chip');
            if (chips.length <= threshold) return;
            chips.forEach(function (chip, i) {
                if (i >= threshold) chip.classList.add('is-overflow');
            });
            var hidden = chips.length - threshold;
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'pt-toggle';
            btn.textContent = '+' + hidden + ' weitere anzeigen';
            btn.setAttribute('aria-expanded', 'false');
            btn.addEventListener('click', function () {
                var expanded = el.classList.toggle('is-expanded');
                btn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
                btn.textContent = expanded
                    ? 'Weniger anzeigen'
                    : '+' + hidden + ' weitere anzeigen';
            });
            el.appendChild(btn);
        });
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

    /* DOM-basiertes Sort-Click auf th[data-sort]. Liest data-sort-value
       von den td derselben Spalte, faellt auf textContent zurueck. Leere
       Werte landen am Ende (analog zum Index-Verhalten). */
    function applySortableTables() {
        document.querySelectorAll('table.sortable-table').forEach(function (table) {
            var headers = table.querySelectorAll('thead th[data-sort]');
            if (!headers.length) return;
            // Default-Reihenfolge merken, um die initiale Sortierung
            // (chronologisch aus dem Aggregator) wiederherstellbar zu machen.
            var tbody = table.querySelector('tbody');
            if (!tbody) return;
            var originalOrder = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
            var state = { key: null, dir: 1 };

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

            function applySort() {
                if (state.key === null) {
                    // Zurueck zur Default-Reihenfolge.
                    var frag = document.createDocumentFragment();
                    originalOrder.forEach(function (tr) { frag.appendChild(tr); });
                    tbody.appendChild(frag);
                    return;
                }
                var colIndex = -1;
                headers.forEach(function (h, i) {
                    if (h.getAttribute('data-sort') === state.key) {
                        // Tatsaechlicher Spalten-Index in der Header-Reihe,
                        // damit auch th vor dem data-sort-th gezaehlt werden.
                        var allHeaders = table.querySelectorAll('thead th');
                        for (var j = 0; j < allHeaders.length; j++) {
                            if (allHeaders[j] === h) { colIndex = j; break; }
                        }
                    }
                });
                if (colIndex < 0) return;

                var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
                rows.sort(function (a, b) {
                    var va = cellValue(a, colIndex);
                    var vb = cellValue(b, colIndex);
                    var aEmpty = (va === '' || va === '-');
                    var bEmpty = (vb === '' || vb === '-');
                    if (aEmpty && bEmpty) return 0;
                    if (aEmpty) return 1;
                    if (bEmpty) return -1;
                    // Numerisch vergleichen, wenn beide Werte reine Zahlen
                    // sind (Signatur-Nummern wie 49, 185, 1599).
                    var na = Number(va);
                    var nb = Number(vb);
                    if (!isNaN(na) && !isNaN(nb) && /^-?\d+(\.\d+)?$/.test(va) && /^-?\d+(\.\d+)?$/.test(vb)) {
                        return (na - nb) * state.dir;
                    }
                    return sortKey(va).localeCompare(sortKey(vb), 'de') * state.dir;
                });
                var frag2 = document.createDocumentFragment();
                rows.forEach(function (tr) { frag2.appendChild(tr); });
                tbody.appendChild(frag2);
            }

            headers.forEach(function (th) {
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
                    headers.forEach(function (h) {
                        h.classList.remove('sorted-asc', 'sorted-desc');
                    });
                    if (state.key !== null) {
                        th.classList.add(state.dir === 1 ? 'sorted-asc' : 'sorted-desc');
                    }
                    applySort();
                });
            });
        });
    }

    function init() {
        document.querySelectorAll('table[data-truncate-at]').forEach(applyTruncation);
        applySourceTitlesCollapse();
        applyQuickFilters();
        applySortableTables();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
