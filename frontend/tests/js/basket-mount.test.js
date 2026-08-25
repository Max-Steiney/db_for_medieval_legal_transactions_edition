// Tests fuer frontend/static/js/basket-mount.js — Bulk-Knopf im Kopf der
// Quellen-Liste auf Personen- und Org-Profilen.
//
// basket-mount.js ist ein reines IIFE ohne Export und hydriert direkt beim
// Laden. Die Quelle wird daher via fs gelesen und pro Test neu im
// jsdom-Kontext evaluiert (Muster aus vitest.config.js), nachdem das
// Markup steht. DataBasket haengt als globales Binding am Scope, genau wie
// im Browser (basket.js wird vor basket-mount.js geladen).

const fs = require('fs');
const path = require('path');

require('./basket-env.js').installLocalStorage();
// Ohne Lookup-Tabelle: der Ableitungs-Durchgang laeuft leer durch.
window.fetch = () => Promise.resolve({ ok: false });

const { DataBasket } = require('../../static/js/basket.js');
globalThis.DataBasket = DataBasket;

const MOUNT_SRC = fs.readFileSync(
    path.resolve(__dirname, '../../static/js/basket-mount.js'), 'utf8'
);

function source(id) {
    return {
        id: id, label: id, url: 'documents/' + id + '.html',
        date: '1380-05-01', coll: 'QGW II/1', regest: 'Regest ' + id,
    };
}

// Jede Evaluierung von basket-mount.js haengt window-Listener an
// (basket-change, storage). Ohne Aufraeumen wuerden die Knoepfe frueherer
// Tests weiter mitzeichnen. Erfasst werden nur die Registrierungen aus dem
// Mount selbst, nicht die von basket.js.
const mountListeners = [];
function dropMountListeners() {
    while (mountListeners.length) {
        const reg = mountListeners.pop();
        window.removeEventListener(reg[0], reg[1], reg[2]);
    }
}

// Baut das Markup, das sources_bulk_mount rendert, und laesst das Skript
// darauf laufen. Rueckgabe ist der hydrierte Knopf.
function mount(payload) {
    document.body.innerHTML =
        '<section class="person-sources">' +
        '<h2 class="section-head">Quellen mit Nennung' +
        '<span class="basket-bulk-mount"></span>' +
        '<script type="application/json" class="basket-bulk-data">' +
        JSON.stringify(payload) + '</script>' +
        '</h2></section>';
    const nativeAdd = window.addEventListener;
    window.addEventListener = function (type, fn, opts) {
        mountListeners.push([type, fn, opts]);
        return nativeAdd.call(window, type, fn, opts);
    };
    try {
        (0, eval)(MOUNT_SRC);
    } finally {
        window.addEventListener = nativeAdd;
    }
    return document.querySelector('.basket-bulk-btn');
}

// Zaehlt die localStorage-Lesezugriffe waehrend fn().
function countReads(fn) {
    const orig = localStorage.getItem;
    let n = 0;
    localStorage.getItem = function (k) { n++; return orig.call(localStorage, k); };
    try { fn(); } finally { localStorage.getItem = orig; }
    return n;
}

beforeEach(() => {
    dropMountListeners();
    localStorage.clear();
});

describe('Bulk-Mount auf Profilseiten', () => {
    test('hydriert den Platzhalter zum Knopf mit Anzahl im Label', () => {
        const btn = mount([source('A-1'), source('A-2'), source('A-3')]);
        expect(btn).toBeTruthy();
        expect(btn.textContent).toBe('Alle 3 Quellen in den Datenkorb');
        expect(btn.disabled).toBe(false);
        expect(btn.getAttribute('data-hint')).toContain('abgeleitete');
        // Normalzustand traegt keine Glyphe: nur das Text-Label.
        expect(btn.querySelector('svg')).toBe(null);
        // Der Platzhalter ist ersetzt, der Payload-Block bleibt stehen.
        expect(document.querySelector('.basket-bulk-mount')).toBe(null);
        expect(document.querySelector('script.basket-bulk-data')).toBeTruthy();
    });

    test('traegt nicht die delegierte Klasse basket-btn', () => {
        // basket.js delegiert Klicks auf .basket-btn; der Bulk-Knopf wuerde
        // sonst als Einzel-Knopf mit fehlendem data-basket-item behandelt.
        const btn = mount([source('A-1')]);
        expect(btn.classList.contains('basket-btn')).toBe(false);
    });

    test('Singular-Label bei genau einer Quelle', () => {
        const btn = mount([source('A-1')]);
        expect(btn.textContent).toBe('Quelle in den Datenkorb');
    });

    test('Klick nimmt alle gelisteten Quellen auf und schaltet den Knopf um', () => {
        const btn = mount([source('A-1'), source('A-2')]);
        btn.click();
        const items = DataBasket.list('source');
        expect(items.length).toBe(2);
        items.forEach(it => expect(it.gathered).toBe(true));
        expect(items[0].coll).toBe('QGW II/1');
        expect(items[0].regest).toBe('Regest A-1');
        // Fertig-Zustand.
        expect(btn.textContent).toBe('Alle 2 Quellen im Datenkorb');
        expect(btn.disabled).toBe(true);
        expect(btn.classList.contains('is-in')).toBe(true);
        expect(btn.getAttribute('data-hint')).toBe(
            'Alle Quellen dieser Liste sind im Datenkorb.'
        );
        // Nur der Fertig-Zustand traegt eine Glyphe (Haekchen).
        expect(btn.querySelectorAll('svg').length).toBe(1);
    });

    test('startet im Fertig-Zustand, wenn schon alles im Korb liegt', () => {
        DataBasket.addMany([
            Object.assign({ type: 'source' }, source('A-1')),
            Object.assign({ type: 'source' }, source('A-2')),
        ]);
        const btn = mount([source('A-1'), source('A-2')]);
        expect(btn.disabled).toBe(true);
        expect(btn.textContent).toBe('Alle 2 Quellen im Datenkorb');
    });

    test('Teilzustand zaehlt als offen', () => {
        DataBasket.add(Object.assign({ type: 'source' }, source('A-1')));
        const btn = mount([source('A-1'), source('A-2')]);
        expect(btn.disabled).toBe(false);
        expect(btn.textContent).toBe('Alle 2 Quellen in den Datenkorb');
    });

    test('Entfernen im Korb aktiviert den Knopf wieder', () => {
        const btn = mount([source('A-1'), source('A-2')]);
        btn.click();
        expect(btn.disabled).toBe(true);
        // Entfernen geschieht auf der Korb-Seite; das basket-change-Event
        // muss den Knopf neu zeichnen.
        DataBasket.remove('source', 'A-2');
        expect(btn.disabled).toBe(false);
        expect(btn.textContent).toBe('Alle 2 Quellen in den Datenkorb');
    });

    test('ein Repaint liest den Korb einmal, nicht einmal pro Quelle', () => {
        // Regression: paintBulk rief isGathered pro gelisteter Quelle auf,
        // und jedes isGathered parst den kompletten Korb. Die Zahl der
        // Lesezugriffe eines Repaints darf nicht mit der Laenge der Liste
        // wachsen -- gerade im Fertig-Zustand, in dem every() nicht mehr
        // abkuerzt und den der Knopf selbst herstellt.
        const readsFor = function (n, prefix) {
            dropMountListeners();
            localStorage.clear();
            const payload = Array.from({ length: n }, (_, i) => source(prefix + i));
            DataBasket.addMany(payload.map(
                d => Object.assign({ type: 'source' }, d)
            ));
            const btn = mount(payload);
            expect(btn.disabled).toBe(true);
            return countReads(function () {
                window.dispatchEvent(new CustomEvent('basket-change', {
                    detail: {},
                }));
            });
        };
        const small = readsFor(5, 'S-');
        const large = readsFor(60, 'L-');
        // Gleiche Kosten bei 5 und bei 60 Quellen; der Sockel stammt aus
        // dem Badge-Update in basket.js.
        expect(large).toBe(small);
        expect(large).toBeLessThan(60);
    });

    test('kaputter Payload laesst den Knopf einfach aus', () => {
        document.body.innerHTML =
            '<h2 class="section-head">Quellen' +
            '<span class="basket-bulk-mount"></span>' +
            '<script type="application/json" class="basket-bulk-data">' +
            '{kein json' + '</script></h2>';
        (0, eval)(MOUNT_SRC);
        expect(document.querySelector('.basket-bulk-btn')).toBe(null);
    });
});
