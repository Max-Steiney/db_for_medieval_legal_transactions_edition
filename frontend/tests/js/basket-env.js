// Testumgebung fuer die Datenkorb-Skripte (kein Test, wird von
// vitest.config.js include-Muster nicht eingesammelt).
//
// jsdom liefert unter der hier verwendeten Node-Version kein
// localStorage (Node blendet ein eigenes, deaktiviertes globales
// localStorage ein). Der Korb liest und schreibt ausschliesslich ueber
// diese API, daher haengen wir vor dem Laden von basket.js einen
// In-Memory-Ersatz mit derselben Signatur an den globalen Scope.

function installLocalStorage() {
    const store = new Map();
    Object.defineProperty(globalThis, 'localStorage', {
        configurable: true,
        writable: true,
        value: {
            getItem(k) {
                return store.has(String(k)) ? store.get(String(k)) : null;
            },
            setItem(k, v) { store.set(String(k), String(v)); },
            removeItem(k) { store.delete(String(k)); },
            clear() { store.clear(); },
            key(i) { return Array.from(store.keys())[i] ?? null; },
            get length() { return store.size; },
        },
    });
}

module.exports = { installLocalStorage };
