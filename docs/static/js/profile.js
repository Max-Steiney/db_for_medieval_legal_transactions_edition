/* Entity-Profil-Interaktivitaet.
 *
 * Drei progressive-enhancement-Aufgaben:
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

    function init() {
        document.querySelectorAll('table[data-truncate-at]').forEach(applyTruncation);
        applySourceTitlesCollapse();
        applyQuickFilters();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
