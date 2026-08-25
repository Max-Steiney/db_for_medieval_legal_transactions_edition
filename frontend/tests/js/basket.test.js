// Tests fuer frontend/static/js/basket.js — Bulk-Add (addMany).
//
// jsdom (siehe vitest.config.js) liefert window-Events und document;
// basket.js ruft beim Laden init() auf, das dort durchlaeuft.
// Die Ableitungs-Schicht (Phase 2) laedt docs_entities.json per fetch und
// cached das Ergebnis fuer die gesamte Modul-Lebensdauer -- der Stub steht
// deshalb VOR dem require und liefert die Lookup-Tabelle, die der
// Ableitungs-Test braucht. Quellen, die nicht in ENTITIES stehen, loesen
// keinen zweiten Write aus.

// localStorage-Ersatz muss vor dem require stehen, siehe basket-env.js.
require('./basket-env.js').installLocalStorage();

// Lookup-Tabelle im Format von docs_entities.json:
//   { "<idno>": { p: [...Personen], o: [...Organisationen] } }
const ENTITIES = {
    'QGW-A': {
        p: [{ id: 'pe__hans', n: 'Hans', sex: 'm', am: '1380', ax: '1390' }],
        o: [{ id: 'org__stephan', n: 'St. Stephan', tpl: 'Kirche' }],
    },
    'QGW-B': {
        p: [{ id: 'pe__hans', n: 'Hans' }, { id: 'pe__grete', n: 'Grete', sex: 'f' }],
        o: [],
    },
};

window.fetch = () => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(ENTITIES),
});

const { DataBasket } = require('../../static/js/basket.js');

const KEY = 'sugw-basket-v1';

const stored = () => JSON.parse(localStorage.getItem(KEY) || '[]');
const byId = (id) => stored().find(x => x.id === id);
// Wartet den asynchronen Ableitungs-Durchgang ab (fetch-Stub plus zwei
// Promise-Ketten); ein Makrotask-Tick deckt alle Microtasks ab.
const flush = () => new Promise(resolve => setTimeout(resolve, 0));

function src(id) {
    return {
        type:   'source',
        id:     id,
        label:  id,
        url:    'documents/' + id + '.html',
        date:   '1380-01-01',
        coll:   'QGW II/1',
        regest: 'Regest ' + id,
    };
}

// Zaehlt die basket-change-Events waehrend fn() (inkl. optionalem await).
async function countChanges(fn) {
    let n = 0;
    const onChange = () => { n++; };
    window.addEventListener('basket-change', onChange);
    await fn();
    window.removeEventListener('basket-change', onChange);
    return n;
}

beforeEach(() => {
    localStorage.clear();
});

describe('DataBasket.addMany', () => {
    test('nimmt alle Quellen auf und liefert die Zahl der Aenderungen', () => {
        const changed = DataBasket.addMany([src('X-1'), src('X-2'), src('X-3')]);
        expect(changed).toBe(3);
        const items = stored();
        expect(items.length).toBe(3);
        items.forEach(it => {
            expect(it.type).toBe('source');
            expect(it.gathered).toBe(true);
        });
        // Feldform wie beim Einzel-Add: Datum, Korpus, Regest bleiben erhalten.
        expect(byId('X-2').date).toBe('1380-01-01');
        expect(byId('X-2').coll).toBe('QGW II/1');
        expect(byId('X-2').regest).toBe('Regest X-2');
        expect(byId('X-2').url).toBe('documents/X-2.html');
    });

    test('feuert genau ein basket-change-Event fuer die ganze Liste', async () => {
        const n = await countChanges(() => {
            DataBasket.addMany([src('X-1'), src('X-2'), src('X-3')]);
        });
        expect(n).toBe(1);
    });

    test('promotet abgeleitete Eintraege und zaehlt sie als Aenderung', () => {
        localStorage.setItem(KEY, JSON.stringify([{
            type: 'person', id: 'pe__hans', label: 'Hans',
            url: 'register/persons/pe__hans.html',
            gathered: false, src: ['QGW-A'],
        }]));
        const changed = DataBasket.addMany([
            { type: 'person', id: 'pe__hans', label: 'Hans' },
            src('X-1'),
        ]);
        // Eine Promotion plus eine neue Quelle.
        expect(changed).toBe(2);
        const items = stored();
        expect(items.length).toBe(2);
        const hans = byId('pe__hans');
        expect(hans.gathered).toBe(true);
        // Die Herkunfts-Verknuepfung bleibt bei der Promotion bestehen.
        expect(hans.src).toEqual(['QGW-A']);
    });

    test('ist idempotent: zweiter Aufruf aendert und schreibt nichts', async () => {
        const items = [src('X-1'), src('X-2')];
        expect(DataBasket.addMany(items)).toBe(2);
        const before = localStorage.getItem(KEY);
        let changed = null;
        const n = await countChanges(() => {
            changed = DataBasket.addMany(items);
        });
        expect(changed).toBe(0);
        expect(n).toBe(0);
        expect(localStorage.getItem(KEY)).toBe(before);
    });

    test('zieht die abgeleiteten Eintraege aller Quellen gebuendelt nach', async () => {
        DataBasket.addMany([src('QGW-A'), src('QGW-B')]);
        await flush();
        const items = stored();
        expect(items.filter(x => x.type === 'source').length).toBe(2);

        const hans = byId('pe__hans');
        expect(hans.type).toBe('person');
        expect(hans.gathered).toBe(false);
        // In beiden Quellen annotiert -> beide idnos im src-Array.
        expect(hans.src).toEqual(['QGW-A', 'QGW-B']);
        expect(hans.url).toBe('register/persons/pe__hans.html');
        expect(hans.active_min).toBe('1380');
        expect(hans.active_max).toBe('1390');

        const grete = byId('pe__grete');
        expect(grete.src).toEqual(['QGW-B']);
        expect(grete.sex).toBe('f');

        const org = byId('org__stephan');
        expect(org.type).toBe('org');
        expect(org.gathered).toBe(false);
        expect(org.src).toEqual(['QGW-A']);
        expect(org.url).toBe('register/orgs/org__stephan.html');
        expect(org.type_label).toBe('Kirche');
    });

    test('der Ableitungs-Durchgang schreibt hoechstens einmal nach', async () => {
        const n = await countChanges(async () => {
            DataBasket.addMany([src('QGW-A'), src('QGW-B')]);
            await flush();
        });
        // Ein Write fuer die Quellen, einer fuer alle Ableitungen zusammen.
        expect(n).toBe(2);
    });

    test('leere oder ungueltige Eingabe bleibt folgenlos', async () => {
        const n = await countChanges(() => {
            expect(DataBasket.addMany([])).toBe(0);
            expect(DataBasket.addMany(null)).toBe(0);
            expect(DataBasket.addMany([{ label: 'ohne id' }])).toBe(0);
        });
        expect(n).toBe(0);
        expect(stored()).toEqual([]);
    });
});

describe('DataBasket.add bleibt unveraendert', () => {
    test('Einzel-Add zieht die Ableitung weiterhin nach', async () => {
        expect(DataBasket.add(src('QGW-A'))).toBe(true);
        await flush();
        expect(byId('QGW-A').gathered).toBe(true);
        expect(byId('pe__hans').src).toEqual(['QGW-A']);
        expect(byId('org__stephan').gathered).toBe(false);
    });
});
