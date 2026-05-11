// Tests fuer frontend/static/js/core.js — die Pure-Logic-Helfer.
// Jsdom-Umgebung (siehe vitest.config.js) liefert document.

// vitest-globals (describe/test/expect) sind via vitest.config.js aktiviert,
// daher kein expliziter Import noetig.
const { EdCore } = require('../../static/js/core.js');

describe('EdCore.esc', () => {
    test('escapes HTML special chars', () => {
        expect(EdCore.esc('<b>x</b>')).toBe('&lt;b&gt;x&lt;/b&gt;');
        expect(EdCore.esc('a & b')).toBe('a &amp; b');
        expect(EdCore.esc('"quoted"')).toBe('"quoted"');
    });

    test('returns empty string for null/undefined/empty', () => {
        expect(EdCore.esc(null)).toBe('');
        expect(EdCore.esc(undefined)).toBe('');
        expect(EdCore.esc('')).toBe('');
    });

    test('coerces numbers to strings', () => {
        expect(EdCore.esc(0)).toBe('0');
        expect(EdCore.esc(42)).toBe('42');
    });
});

describe('EdCore.normForSearch', () => {
    test('lowercases', () => {
        expect(EdCore.normForSearch('ABC')).toBe('abc');
    });

    test('replaces German umlauts with digraphs', () => {
        expect(EdCore.normForSearch('Mueller')).toBe('mueller');
        expect(EdCore.normForSearch('Müller')).toBe('mueller');
        expect(EdCore.normForSearch('Pötel')).toBe('poetel');
        expect(EdCore.normForSearch('Käse')).toBe('kaese');
    });

    test('replaces sharp s', () => {
        expect(EdCore.normForSearch('Strauß')).toBe('strauss');
        expect(EdCore.normForSearch('weiß')).toBe('weiss');
    });

    test('strips combining diacritics', () => {
        // 'café' uses combining acute on e; result must be 'cafe'
        expect(EdCore.normForSearch('café')).toBe('cafe');
    });

    test('matches umlaut-tolerant: a query in either form finds the other', () => {
        // The function is used both for indexing and for the user query;
        // both sides must produce the same normalised form.
        expect(EdCore.normForSearch('Müller')).toBe(EdCore.normForSearch('Mueller'));
        expect(EdCore.normForSearch('Strauß')).toBe(EdCore.normForSearch('Strauss'));
    });

    test('handles null/undefined', () => {
        expect(EdCore.normForSearch(null)).toBe('');
        expect(EdCore.normForSearch(undefined)).toBe('');
    });

    test('preserves non-letter content', () => {
        expect(EdCore.normForSearch('Wien 1380')).toBe('wien 1380');
    });
});

describe('EdCore.getParam', () => {
    test('returns null when query is empty', () => {
        // jsdom default URL is about:blank with no query.
        expect(EdCore.getParam('foo')).toBe(null);
    });

    test('reads query parameters when set', () => {
        // Re-write history to add a query string for this test.
        window.history.replaceState({}, '', '/?id=pe__hans&kind=person');
        expect(EdCore.getParam('id')).toBe('pe__hans');
        expect(EdCore.getParam('kind')).toBe('person');
        expect(EdCore.getParam('missing')).toBe(null);
        // Clean up so other tests start with no query.
        window.history.replaceState({}, '', '/');
    });
});

describe('EdCore.sortKey', () => {
    test('strips square brackets globally', () => {
        // Editorial markup like "[Wien]" must sort under W, not under [.
        expect(EdCore.sortKey('[Wien]')).toBe('wien');
        expect(EdCore.sortKey('[Wien')).toBe('wien');
        expect(EdCore.sortKey('Wien]')).toBe('wien');
    });

    test('trims leading/trailing punctuation but keeps internal dots', () => {
        // "Wien," sorts with "Wien"; "St. Poelten" is left alone because
        // its dot is internal.
        expect(EdCore.sortKey('Wien,')).toBe('wien');
        expect(EdCore.sortKey(',Wien')).toBe('wien');
        expect(EdCore.sortKey('  Wien  ')).toBe('wien');
        expect(EdCore.sortKey('St. Poelten')).toBe('st. poelten');
    });

    test('lowercases', () => {
        expect(EdCore.sortKey('ABC')).toBe('abc');
        expect(EdCore.sortKey('Wien')).toBe('wien');
    });

    test('handles null/undefined/empty', () => {
        expect(EdCore.sortKey(null)).toBe('');
        expect(EdCore.sortKey(undefined)).toBe('');
        expect(EdCore.sortKey('')).toBe('');
    });

    test('coerces numbers to strings', () => {
        expect(EdCore.sortKey(42)).toBe('42');
        expect(EdCore.sortKey(0)).toBe('0');
    });
});

describe('EdCore.compareValues', () => {
    test('empty values sort to the end (ascending)', () => {
        expect(EdCore.compareValues('Wien', '', 1)).toBe(-1);
        expect(EdCore.compareValues('', 'Wien', 1)).toBe(1);
        expect(EdCore.compareValues('', '', 1)).toBe(0);
    });

    test('null/undefined/dash count as empty', () => {
        expect(EdCore.compareValues(null, 'X', 1)).toBe(1);
        expect(EdCore.compareValues(undefined, 'X', 1)).toBe(1);
        expect(EdCore.compareValues('-', 'X', 1)).toBe(1);
    });

    test('numeric strings compare numerically, not lexicographically', () => {
        // Without numeric detection, "1599" would sort before "49".
        expect(EdCore.compareValues('49', '1599', 1)).toBeLessThan(0);
        expect(EdCore.compareValues('1599', '49', 1)).toBeGreaterThan(0);
        expect(EdCore.compareValues('100', '100', 1)).toBe(0);
    });

    test('genuine numbers compare numerically', () => {
        expect(EdCore.compareValues(5, 10, 1)).toBeLessThan(0);
        expect(EdCore.compareValues(10, 5, 1)).toBeGreaterThan(0);
    });

    test('text falls back to locale-aware compare with sortKey', () => {
        // Bracket-stripped, punctuation-trimmed, then localeCompare('de').
        expect(EdCore.compareValues('Wien', '[Wien]', 1)).toBe(0);
        expect(EdCore.compareValues('Wien,', 'Wien', 1)).toBe(0);
        expect(EdCore.compareValues('Aachen', 'Wien', 1)).toBeLessThan(0);
    });

    test('umlauts sort with their base letter in de-locale', () => {
        // localeCompare('de'): "Pötel" sorts near "Poe…" / "Pot…"
        const aFirst = EdCore.compareValues('Pötel', 'Quedlinburg', 1);
        const oFirst = EdCore.compareValues('Pötel', 'Aachen', 1);
        expect(aFirst).toBeLessThan(0);
        expect(oFirst).toBeGreaterThan(0);
    });

    test('descending direction flips the result', () => {
        expect(EdCore.compareValues('A', 'B', -1)).toBeGreaterThan(0);
        expect(EdCore.compareValues('B', 'A', -1)).toBeLessThan(0);
    });

    test('default direction is ascending', () => {
        expect(EdCore.compareValues('A', 'B')).toBeLessThan(0);
    });
});
