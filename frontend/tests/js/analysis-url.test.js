// Tests fuer analysis-url.js — Roundtrip der Konstellations-URL.
//
// Hintergrund: Forschungsfragen werden als Permalink geteilt (Mail-
// Fragen 3 und 4 stuetzen sich darauf, dass eine URL wie
// #p1=r=issuer&g1=r=recipient,n=St. Agnes... nach Reload denselben
// State erzeugt). Ein Round-Trip-Test schuetzt vor Serialisierungs-
// Drift.

const {
    serializeQueryState,
    parseQueryHash,
    defaultPerson,
    defaultOrg,
} = require('../../static/js/analysis-url.js');

const ALL_CORPORA = ['QGW_II_I', 'QGW_II_II', 'Stadtbuecher_I', 'Satzbuch_CD'];

function roundtrip(state) {
    const hash = serializeQueryState(state, ALL_CORPORA);
    const parsed = parseQueryHash('#' + hash);
    // corpora-Default: parser liefert null, wenn der Param weggelassen
    // wurde. Fuer den Vergleich normalisieren wir das in die "alle"-Liste.
    if (parsed.corpora === null) parsed.corpora = ALL_CORPORA.slice();
    return { hash, parsed };
}

describe('serializeQueryState / parseQueryHash — Roundtrip', () => {
    test('empty state serializes to empty string', () => {
        const state = {
            persons: [], orgs: [], scope: 'event', corpora: ALL_CORPORA.slice(),
        };
        expect(serializeQueryState(state, ALL_CORPORA)).toBe('');
    });

    test('inactive person and org slots are stripped', () => {
        const state = {
            persons: [defaultPerson(), defaultPerson()],
            orgs: [defaultOrg()],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        expect(serializeQueryState(state, ALL_CORPORA)).toBe('');
    });

    test('single person condition round-trips', () => {
        const state = {
            persons: [{ role: 'issuer', sex: 'f', occ: '', uhlirz: '' }],
            orgs: [],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash).toBe('p1=r=issuer,s=f');
        expect(parsed.persons[0]).toEqual({
            role: 'issuer', sex: 'f', occ: '', uhlirz: '',
        });
    });

    test('uhlirz-only condition round-trips with encoded value', () => {
        const cat = 'IV Erzeugung und Vertrieb von Leuchtstoffen Fetten und Oelen';
        const state = {
            persons: [{ role: '', sex: '', occ: '', uhlirz: cat }],
            orgs: [],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash.startsWith('p1=u=')).toBe(true);
        expect(parsed.persons[0].uhlirz).toBe(cat);
    });

    test('mail-frage 4: person issuer + org recipient Himmelpforte', () => {
        const state = {
            persons: [{ role: 'issuer', sex: '', occ: '', uhlirz: '' }],
            orgs: [{ role: 'recipient', name: 'St. Agnes (auf der Himmelpforte) Wien', type: '' }],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash).toMatch(/^p1=r=issuer&g1=r=recipient,n=/);
        expect(parsed.persons[0].role).toBe('issuer');
        expect(parsed.orgs[0].role).toBe('recipient');
        expect(parsed.orgs[0].name).toBe('St. Agnes (auf der Himmelpforte) Wien');
    });

    test('two person conditions in order round-trip', () => {
        const state = {
            persons: [
                { role: 'issuer',    sex: 'f', occ: '',      uhlirz: '' },
                { role: 'recipient', sex: 'm', occ: 'urger', uhlirz: '' },
            ],
            orgs: [],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash).toBe('p1=r=issuer,s=f&p2=r=recipient,s=m,o=urger');
        expect(parsed.persons[0].sex).toBe('f');
        expect(parsed.persons[1].occ).toBe('urger');
    });

    test('two org conditions in order round-trip', () => {
        const state = {
            persons: [],
            orgs: [
                { role: 'issuer', name: '', type: '' },
                { role: 'recipient', name: 'Himmelpforte', type: '' },
            ],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash).toBe('g1=r=issuer&g2=r=recipient,n=Himmelpforte');
        expect(parsed.orgs[1].name).toBe('Himmelpforte');
    });

    test('scope != event is serialized', () => {
        const state = {
            persons: [{ role: 'issuer', sex: '', occ: '', uhlirz: '' }],
            orgs: [],
            scope: 'source',
            corpora: ALL_CORPORA.slice(),
        };
        const { hash, parsed } = roundtrip(state);
        expect(hash).toContain('scope=source');
        expect(parsed.scope).toBe('source');
    });

    test('partial corpora selection is serialized; full set is omitted', () => {
        const full = {
            persons: [{ role: 'issuer', sex: '', occ: '', uhlirz: '' }],
            orgs: [],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        expect(serializeQueryState(full, ALL_CORPORA)).not.toContain('c=');

        const partial = {
            persons: [{ role: 'issuer', sex: '', occ: '', uhlirz: '' }],
            orgs: [],
            scope: 'event',
            corpora: ['QGW_II_I', 'Stadtbuecher_I'],
        };
        const { hash, parsed } = roundtrip(partial);
        expect(hash).toContain('c=QGW_II_I,Stadtbuecher_I');
        expect(parsed.corpora).toEqual(['QGW_II_I', 'Stadtbuecher_I']);
    });

    test('special chars in occ-field survive round-trip', () => {
        const state = {
            persons: [{ role: '', sex: '', occ: 'Bürger & Co.', uhlirz: '' }],
            orgs: [],
            scope: 'event',
            corpora: ALL_CORPORA.slice(),
        };
        const { parsed } = roundtrip(state);
        expect(parsed.persons[0].occ).toBe('Bürger & Co.');
    });
});

describe('parseQueryHash — edge cases', () => {
    test('empty string yields empty state', () => {
        const parsed = parseQueryHash('');
        expect(parsed.persons).toEqual([]);
        expect(parsed.orgs).toEqual([]);
        expect(parsed.scope).toBe('event');
        expect(parsed.corpora).toBeNull();
    });

    test('unknown key is silently ignored', () => {
        const parsed = parseQueryHash('#xyz=foo&p1=r=issuer');
        expect(parsed.persons[0].role).toBe('issuer');
    });

    test('non-sequential indices fill gaps with defaults', () => {
        const parsed = parseQueryHash('#p3=r=issuer');
        expect(parsed.persons.length).toBe(3);
        expect(parsed.persons[2].role).toBe('issuer');
        expect(parsed.persons[0]).toEqual(defaultPerson());
    });
});
