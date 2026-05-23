// Tests fuer frontend/static/js/document.js — Annotationen-Tabelle.
//
// document.js exportiert keine Bindings (reines IIFE-Script), daher
// laesst sich entityTipBody/eventTipBody nicht direkt aufrufen. Die
// Regression-Guards laufen daher als statische Quelltext-Inspektion:
// das frueher in den Tabellen-Tooltip injizierte Roh-TEI-Markup darf
// nicht mehr im Build-Output erscheinen. Die Strings `<rs ` und
// `<triggerstring` durfen nur noch als Klassenpraefix oder Selektor-
// Argument vorkommen, nicht als Tooltip-Body-Anteil.

const fs = require('fs');
const path = require('path');

const SOURCE = fs.readFileSync(
    path.resolve(__dirname, '../../static/js/document.js'), 'utf8'
);

describe('document.js Tooltip-Body', () => {
    test('entityTipBody enthaelt kein Roh-rs-Markup', () => {
        // Frueher: parts.push('<rs ' + rsAttrs.join(' ') + '>' + f.name + '</rs>');
        // Jetzt: parts = [f.name]; ...
        const match = SOURCE.match(/parts\.push\(\s*'<rs /);
        expect(match).toBeNull();
    });

    test('eventTipBody enthaelt kein Roh-rs-event-Markup', () => {
        const match = SOURCE.match(/parts\s*=\s*\[\s*'<rs type="event"/);
        expect(match).toBeNull();
    });

    test('triggerTipBody enthaelt kein Roh-triggerstring-Markup', () => {
        const match = SOURCE.match(/parts\s*=\s*\[\s*'<triggerstring/);
        expect(match).toBeNull();
    });

    test('addTipBody enthaelt kein Roh-add-Markup', () => {
        const match = SOURCE.match(/parts\s*=\s*\[\s*'<add>/);
        expect(match).toBeNull();
    });
});

describe('document.js Annotationen-Tabelle: Markup-Konvention', () => {
    test('Tabellen tragen sortable-table-Klasse', () => {
        // Drei Sub-Tabellen (Entitaeten, Dispositivformeln,
        // Editorische Ergaenzungen) tragen das CSS-Hook fuer
        // .sortable-table, damit Sort-Pfeile und Hover-Stil greifen.
        const matches = SOURCE.match(/annotations-table sortable-table/g);
        expect(matches).not.toBeNull();
        expect(matches.length).toBeGreaterThanOrEqual(3);
    });

    test('jede th hat data-sort', () => {
        // Heuristik: Anzahl <th-Tags muss die Anzahl data-sort-Attribute
        // matchen (im Tabellenbau).
        const thCount = (SOURCE.match(/<th scope="col"/g) || []).length;
        const dataSortCount = (SOURCE.match(/data-sort="/g) || []).length;
        expect(thCount).toBeGreaterThan(0);
        expect(dataSortCount).toBeGreaterThanOrEqual(thCount);
    });

    test('Type-Marker als anno-type-dot vor der Nennform', () => {
        // Loest die frueher separate "Typ"-Spalte ab. Annotations-Token-
        // Farbe traegt die Typ-Information ohne Spaltenbreite zu kosten.
        const match = SOURCE.match(/anno-type-dot anno-type-dot--/);
        expect(match).not.toBeNull();
    });

    test('alte annotation-type-Klasse wird nicht mehr injiziert', () => {
        const match = SOURCE.match(/annotation-type annotation-type-/);
        expect(match).toBeNull();
    });

    test('Tabs-Strip wird gerendert', () => {
        // Drei Sub-Tabellen wandern in einen Tab-Toggle, sobald mehr als
        // eine Tabelle Inhalt traegt.
        const match = SOURCE.match(/class="annotations-tab/);
        expect(match).not.toBeNull();
    });

    test('Sortierfunktion ist initialisiert', () => {
        const match = SOURCE.match(/_attachAnnotationSorting/);
        expect(match).not.toBeNull();
    });
});
