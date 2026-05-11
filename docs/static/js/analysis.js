/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis page
   Driver

   Wires composer to hash and data loader. Live update on every state
   change — no submit button.
   ========================================================================== */

(function() {
    'use strict';

    let ROOT = window.ROOT_PATH || '.';

    let Store = {
        state: null,
        dataCache: {}
    };

    /* ----- Hash --------------------------------------------------------- */

    function parseHash() {
        let raw = window.location.hash.replace(/^#/, '');
        if (!raw) return null;
        let out = {};
        raw.split('&').forEach(function(part) {
            let i = part.indexOf('=');
            if (i > 0) out[decodeURIComponent(part.slice(0, i))] = decodeURIComponent(part.slice(i + 1));
        });
        return out;
    }

    function writeHash(state) {
        let hash = window.AnalysisComposer.toHash(state);
        if (window.location.hash !== hash) {
            history.replaceState(null, '',
                window.location.pathname + window.location.search + hash);
        }
    }

    /* ----- Data loader -------------------------------------------------- */

    function loadDataFiles(filenames, callback) {
        if (!filenames || filenames.length === 0) { callback({}); return; }
        let pending = filenames.length;
        let result = {};
        let failed = false;

        filenames.forEach(function(filename) {
            if (Store.dataCache[filename]) {
                result[filename] = Store.dataCache[filename];
                if (--pending === 0 && !failed) callback(result);
                return;
            }
            fetch(ROOT + '/data/' + filename)
                .then(function(r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.json();
                })
                .then(function(data) {
                    Store.dataCache[filename] = data;
                    result[filename] = data;
                    if (--pending === 0 && !failed) callback(result);
                })
                .catch(function() {
                    if (failed) return;
                    failed = true;
                    let panel = document.getElementById('result');
                    if (panel) panel.innerHTML = '<p class="result-empty">Konnte ' +
                        filename + ' nicht laden.</p>';
                });
        });
    }

    /* ----- Render ------------------------------------------------------- */

    // docsLookup wird lazy beim ersten Drill-Click geladen (analog zu
    // analysis-aggregat.js). VizCore.bindDrillOverlay verkabelt Close/ESC
    // einmalig, openDrillOverlay() rendert pro Click.
    let DOCS_LOOKUP = {};

    function setState(newState) {
        Store.state = newState;
        let files = window.AnalysisComposer.requiredFiles(newState);
        loadDataFiles(files, function(dataMap) {
            window.AnalysisComposer.render({
                state: newState,
                dataMap: dataMap,
                composerRoot: document.getElementById('composer'),
                resultPanel: document.getElementById('result'),
                openDrill: openDrill,
                onChange: setState
            });
            writeHash(newState);
        });
    }

    function openDrill(title, fileKeys) {
        if (!window.VizCore) return;
        if (!Object.keys(DOCS_LOOKUP).length) {
            window.VizCore.loadDocsLookup().then(function(lk) {
                DOCS_LOOKUP = lk;
                openDrill(title, fileKeys);
            });
            return;
        }
        window.VizCore.openDrillOverlay({
            overlayId: 'analysis-drilldown',
            title: title,
            fileKeys: fileKeys,
            docsLookup: DOCS_LOOKUP,
        });
    }

    /* ----- Init --------------------------------------------------------- */

    function init() {
        if (window.VizCore) {
            window.VizCore.bindDrillOverlay({ overlayId: 'analysis-drilldown' });
        }
        window.AnalysisComposer.loadVocab(function() {
            let parsed = parseHash();
            let state = (parsed && window.AnalysisComposer.fromHash(parsed))
                || window.AnalysisComposer.defaultState();
            setState(state);

            window.addEventListener('hashchange', function() {
                let p = parseHash();
                let s = (p && window.AnalysisComposer.fromHash(p))
                    || window.AnalysisComposer.defaultState();
                setState(s);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
