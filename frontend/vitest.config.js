// Vitest-Konfiguration fuer das Edition-Frontend.
//
// Tests laufen unter jsdom, damit die geprueften JS-Module mit DOM-Hilfen
// (document.createElement, addEventListener) wie im Browser funktionieren.
// Die produktiven Skripte sind keine ES-Module; sie haengen ihre API an
// globale `let X = (function(){ ... })()`-Bindings. Daher liest jeder Test
// die Quelldatei via fs.readFileSync und evaluiert sie im jsdom-Kontext.
import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        environment: 'jsdom',
        include: ['tests/js/**/*.test.js'],
        globals: true,
    },
});
