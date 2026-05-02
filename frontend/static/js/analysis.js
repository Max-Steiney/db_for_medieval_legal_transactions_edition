/* ==========================================================================
   Stadt und Gemeinschaft Wien - Analyse-Seite
   Driver

   Verbindet Composer mit Hash und Daten-Loader. Live-Update bei jeder
   State-Aenderung — kein Submit-Button mehr.
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

    /* ----- Daten-Loader ------------------------------------------------- */

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

    let drillHandle = null;

    function bindDrillDown() {
        if (typeof DrillDown === 'undefined') return;
        drillHandle = DrillDown.bind({
            overlayId: 'analysis-drilldown',
            titleId:   'analysis-drilldown-title',
            tbodyId:   'analysis-drilldown-tbody',
            countId:   'analysis-drilldown-count',
            closeId:   'analysis-drilldown-close',
            exportId:  'analysis-drilldown-export'
        });
    }

    function setState(newState) {
        Store.state = newState;
        let files = window.AnalysisComposer.requiredFiles(newState);
        loadDataFiles(files, function(dataMap) {
            window.AnalysisComposer.render({
                state: newState,
                dataMap: dataMap,
                composerRoot: document.getElementById('composer'),
                resultPanel: document.getElementById('result'),
                drillHandle: drillHandle,
                onChange: setState
            });
            writeHash(newState);
        });
    }

    /* ----- Init --------------------------------------------------------- */

    function init() {
        bindDrillDown();
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
