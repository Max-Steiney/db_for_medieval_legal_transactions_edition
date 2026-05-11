// Tests fuer analysis-composer.js — State, Hash-Serialisierung,
// Required-Files-Berechnung. Pure Logik, kein DOM-Zugriff.

const { AnalysisComposer } = require('../../static/js/analysis-composer.js');

describe('AnalysisComposer.defaultState', () => {
    test('subject = persons, no filters', () => {
        const st = AnalysisComposer.defaultState();
        expect(st.subject).toBe('persons');
        expect(st.filters).toEqual({});
    });

    test('returns fresh object each call (no shared mutation)', () => {
        const a = AnalysisComposer.defaultState();
        const b = AnalysisComposer.defaultState();
        a.filters.x = 1;
        expect(b.filters).toEqual({});
    });
});

describe('AnalysisComposer.fromHash / toHash — Round-trip', () => {
    test('subject-only state round-trips', () => {
        const st = { subject: 'events', filters: {} };
        const hash = AnalysisComposer.toHash(st);
        // Hash starts with #, parse only after #
        expect(hash.startsWith('#')).toBe(true);
        const parsed = parseQuery(hash);
        const restored = AnalysisComposer.fromHash(parsed);
        expect(restored.subject).toBe('events');
        expect(restored.filters).toEqual({});
    });

    test('state with one filter round-trips', () => {
        const st = { subject: 'persons', filters: { sex: 'f' } };
        const parsed = parseQuery(AnalysisComposer.toHash(st));
        const restored = AnalysisComposer.fromHash(parsed);
        expect(restored.subject).toBe('persons');
        expect(restored.filters).toEqual({ sex: 'f' });
    });

    test('state with multiple filters round-trips', () => {
        const st = {
            subject: 'relationships',
            filters: { rel_type: 'kin', sex: 'm' },
        };
        const parsed = parseQuery(AnalysisComposer.toHash(st));
        const restored = AnalysisComposer.fromHash(parsed);
        expect(restored.subject).toBe('relationships');
        expect(restored.filters).toEqual({ rel_type: 'kin', sex: 'm' });
    });

    test('empty filter values are dropped from hash', () => {
        const st = {
            subject: 'persons',
            filters: { sex: '', other: null, valid: 'x' },
        };
        const hash = AnalysisComposer.toHash(st);
        // empty/null filter values omitted; only 'valid' should appear
        expect(hash).toMatch(/valid:x/);
        expect(hash).not.toMatch(/sex:/);
        expect(hash).not.toMatch(/other:/);
    });

    test('fromHash returns null for invalid input', () => {
        expect(AnalysisComposer.fromHash(null)).toBe(null);
        expect(AnalysisComposer.fromHash({})).toBe(null);
        expect(AnalysisComposer.fromHash({ noSubject: 'x' })).toBe(null);
    });
});

describe('AnalysisComposer.requiredFiles', () => {
    test('always includes query_vocabulary.json', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'persons', filters: {},
        });
        expect(files).toContain('query_vocabulary.json');
    });

    test('persons subject pulls roles', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'persons', filters: {},
        });
        expect(files).toContain('roles.json');
        expect(files).not.toContain('relations.json');
        expect(files).not.toContain('transactions.json');
    });

    test('events subject pulls roles + transactions', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'events', filters: {},
        });
        expect(files).toContain('roles.json');
        expect(files).toContain('transactions.json');
    });

    test('relationships subject pulls relations', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'relationships', filters: {},
        });
        expect(files).toContain('relations.json');
    });

    test('sources subject pulls timeline.json', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'sources', filters: {},
        });
        expect(files).toContain('timeline.json');
    });

    test('org_category filter triggers categories.json load', () => {
        const without = AnalysisComposer.requiredFiles({
            subject: 'persons', filters: {},
        });
        const withCat = AnalysisComposer.requiredFiles({
            subject: 'persons', filters: { org_category: 'geistlich' },
        });
        expect(without).not.toContain('categories.json');
        expect(withCat).toContain('categories.json');
    });

    test('returns deduplicated files', () => {
        const files = AnalysisComposer.requiredFiles({
            subject: 'events', filters: {},
        });
        const seen = new Set();
        for (const f of files) {
            expect(seen.has(f)).toBe(false);
            seen.add(f);
        }
    });
});

// --- Helper: parse the hash that toHash() produced -------------------------
// fromHash erwartet {s, filter} aus query-string-style; toHash schreibt den
// Hash. Wir parsen ihn hier aequivalent zur produktiven URL-Logik.

function parseQuery(hash) {
    // "#s=persons&filter=sex:f"
    const trimmed = hash.startsWith('#') ? hash.slice(1) : hash;
    if (!trimmed) return {};
    const out = {};
    for (const part of trimmed.split('&')) {
        const eq = part.indexOf('=');
        if (eq < 0) continue;
        const key = decodeURIComponent(part.slice(0, eq));
        const value = decodeURIComponent(part.slice(eq + 1));
        // toHash uses 's=...' for subject; fromHash expects key 's' or 'filter'
        if (key === 's') out.s = value;
        else if (key === 'filter') out.filter = value;
    }
    return out;
}
