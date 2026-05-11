// Tests fuer TableInfra.setupTableFilter (DOM-Tabellen-Filter).
// Braucht EdCore global, weil table-infra.js esc = EdCore.esc verwendet.

const { EdCore } = require('../../static/js/core.js');
global.EdCore = EdCore;

const { TableInfra } = require('../../static/js/table-infra.js');

describe('TableInfra.setupTableFilter', () => {
    function mkTable(rows) {
        document.body.innerHTML = `
            <section>
                <div class="table-filter">
                    <input type="search" class="table-filter-input">
                    <span class="table-filter-status"></span>
                </div>
                <table>
                    <thead><tr><th>Person</th><th>Datum</th></tr></thead>
                    <tbody>
                        ${rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')}
                    </tbody>
                </table>
            </section>`;
        return {
            input: document.querySelector('.table-filter-input'),
            table: document.querySelector('table'),
            status: document.querySelector('.table-filter-status'),
            rows: Array.from(document.querySelectorAll('tbody tr')),
        };
    }

    function fireInput(input, value) {
        input.value = value;
        input.dispatchEvent(new Event('input'));
    }

    test('does nothing for null input/table', () => {
        expect(() => TableInfra.setupTableFilter(null, null)).not.toThrow();
        expect(() => TableInfra.setupTableFilter(null, document.createElement('table'))).not.toThrow();
    });

    test('shows all rows and empty status when query is empty', () => {
        const { input, table, status, rows } = mkTable([
            ['Wien', '1380'],
            ['Aachen', '1395'],
        ]);
        TableInfra.setupTableFilter(input, table);
        fireInput(input, '');
        expect(rows.every(r => !r.classList.contains('row-hidden'))).toBe(true);
        expect(table.classList.contains('is-filtering')).toBe(false);
        expect(status.textContent).toBe('');
    });

    test('hides non-matching rows and reports count', () => {
        const { input, table, status, rows } = mkTable([
            ['Wien', '1380'],
            ['Aachen', '1395'],
            ['Wien-Neustadt', '1410'],
        ]);
        TableInfra.setupTableFilter(input, table);
        fireInput(input, 'Wien');
        expect(rows[0].classList.contains('row-hidden')).toBe(false);
        expect(rows[1].classList.contains('row-hidden')).toBe(true);
        expect(rows[2].classList.contains('row-hidden')).toBe(false);
        expect(table.classList.contains('is-filtering')).toBe(true);
        expect(status.textContent).toBe('2 von 3 Zeilen');
    });

    test('is umlaut-tolerant: "Poetel" finds "Pötel"', () => {
        const { input, table, rows } = mkTable([
            ['Pötel', '1380'],
            ['Wien', '1395'],
        ]);
        TableInfra.setupTableFilter(input, table);
        fireInput(input, 'Poetel');
        expect(rows[0].classList.contains('row-hidden')).toBe(false);
        expect(rows[1].classList.contains('row-hidden')).toBe(true);
    });

    test('whitespace-split word-AND: "Wien 1410" matches only the row with both', () => {
        const { input, table, rows } = mkTable([
            ['Wien', '1380'],
            ['Wien-Neustadt', '1410'],
            ['Aachen', '1410'],
        ]);
        TableInfra.setupTableFilter(input, table);
        fireInput(input, 'Wien 1410');
        expect(rows[0].classList.contains('row-hidden')).toBe(true);
        expect(rows[1].classList.contains('row-hidden')).toBe(false);
        expect(rows[2].classList.contains('row-hidden')).toBe(true);
    });

    test('clearing the filter restores all rows', () => {
        const { input, table, status, rows } = mkTable([
            ['Wien', '1380'],
            ['Aachen', '1395'],
        ]);
        TableInfra.setupTableFilter(input, table);
        fireInput(input, 'Wien');
        expect(rows[1].classList.contains('row-hidden')).toBe(true);
        fireInput(input, '');
        expect(rows.every(r => !r.classList.contains('row-hidden'))).toBe(true);
        expect(table.classList.contains('is-filtering')).toBe(false);
        expect(status.textContent).toBe('');
    });

    test('caches normalised haystack per row (does not re-normalise on every keystroke)', () => {
        // Indirect check: __filterHay is populated as a side-effect on
        // each row and contains the umlaut-normalised text. textContent
        // of a <tr> joins all <td> texts without inter-cell whitespace.
        const { input, table, rows } = mkTable([['Pötel', '1380']]);
        TableInfra.setupTableFilter(input, table);
        expect(rows[0].__filterHay).toBe('poetel1380');
    });

    test('returns a handle with update() for programmatic re-filtering', () => {
        const { input, table } = mkTable([['Wien', '1380']]);
        const handle = TableInfra.setupTableFilter(input, table);
        expect(typeof handle.update).toBe('function');
        expect(Array.isArray(handle.rows)).toBe(true);
        expect(handle.rows.length).toBe(1);
    });
});
