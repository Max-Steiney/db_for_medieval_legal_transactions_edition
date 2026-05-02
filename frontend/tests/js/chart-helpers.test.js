// Tests fuer chart-helpers.js Pure-Logic-Helfer.

const { ChartHelpers } = require('../../static/js/chart-helpers.js');

describe('ChartHelpers.fmt — German thousands separator', () => {
    test('formats numbers below 1000 unchanged', () => {
        expect(ChartHelpers.fmt(0)).toBe('0');
        expect(ChartHelpers.fmt(42)).toBe('42');
        expect(ChartHelpers.fmt(999)).toBe('999');
    });

    test('formats thousands with .', () => {
        expect(ChartHelpers.fmt(1000)).toBe('1.000');
        expect(ChartHelpers.fmt(2601)).toBe('2.601');
        expect(ChartHelpers.fmt(16084)).toBe('16.084');
    });

    test('formats millions correctly', () => {
        expect(ChartHelpers.fmt(1000000)).toBe('1.000.000');
        expect(ChartHelpers.fmt(2601834)).toBe('2.601.834');
    });

    test('handles strings via String() coercion', () => {
        expect(ChartHelpers.fmt('1234')).toBe('1.234');
    });
});

describe('ChartHelpers.svgEl — SVG element factory', () => {
    test('creates SVG element with correct namespace', () => {
        const el = ChartHelpers.svgEl('rect');
        expect(el.namespaceURI).toBe('http://www.w3.org/2000/svg');
        expect(el.tagName.toLowerCase()).toBe('rect');
    });

    test('applies attribute map', () => {
        const el = ChartHelpers.svgEl('circle', { cx: '5', cy: '10', r: '3' });
        expect(el.getAttribute('cx')).toBe('5');
        expect(el.getAttribute('cy')).toBe('10');
        expect(el.getAttribute('r')).toBe('3');
    });

    test('omitted attrs leaves element with no extra attrs', () => {
        const el = ChartHelpers.svgEl('g');
        expect(el.attributes.length).toBe(0);
    });
});

describe('ChartHelpers role/sex constants', () => {
    test('ROLE_ORDER contains canonical roles', () => {
        expect(ChartHelpers.ROLE_ORDER).toEqual(['issuer', 'recipient', 'witness', 'other']);
    });

    test('ROLE_LABELS covers ROLE_ORDER', () => {
        for (const r of ChartHelpers.ROLE_ORDER) {
            expect(typeof ChartHelpers.ROLE_LABELS[r]).toBe('string');
            expect(ChartHelpers.ROLE_LABELS[r].length).toBeGreaterThan(0);
        }
    });

    test('SEX_LABELS has m/f/unspecified', () => {
        expect(Object.keys(ChartHelpers.SEX_LABELS).sort()).toEqual(['f', 'm', 'unspecified']);
    });
});
