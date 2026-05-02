/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   DrillDown: shared document drill-down overlay + CSV export
   ========================================================================== */

let DrillDown = (function() {
    'use strict';

    let esc = EdCore.esc;

    // Shared state
    let docsLookup = null;
    let docsLookupLoading = false;
    let currentData = [];
    let boundOverlays = {};
    let previousFocus = null; // WCAG: restore focus on close

    /* ------------------------------------------------------------------
       Lazy-load docs_lookup.json (shared across all explorers)
       ------------------------------------------------------------------ */

    function loadDocsLookup(callback) {
        if (docsLookup) { callback(docsLookup); return; }
        if (docsLookupLoading) {
            // Queue: wait and retry
            let check = setInterval(function() {
                if (docsLookup) { clearInterval(check); callback(docsLookup); }
                if (!docsLookupLoading && !docsLookup) { clearInterval(check); }
            }, 100);
            return;
        }
        docsLookupLoading = true;
        fetch((window.ROOT_PATH || '.') + '/data/docs_lookup.json')
            .then(function(res) { return res.json(); })
            .then(function(data) {
                docsLookup = data;
                docsLookupLoading = false;
                callback(docsLookup);
            })
            .catch(function() {
                docsLookupLoading = false;
            });
    }


    /* ------------------------------------------------------------------
       Bind an overlay by element IDs. Call once per overlay.
       Returns a handle for open/close.
       ------------------------------------------------------------------ */

    function bind(config) {
        let overlayId = config.overlayId || 'explore-drilldown';
        let overlay = document.getElementById(overlayId);
        if (!overlay) return null;

        let titleEl = document.getElementById(config.titleId || 'explore-drilldown-title');
        let tbodyEl = document.getElementById(config.tbodyId || 'explore-drilldown-tbody');
        let countEl = document.getElementById(config.countId || 'explore-drilldown-count');
        let closeBtn = document.getElementById(config.closeId || 'explore-drilldown-close');
        let exportBtn = document.getElementById(config.exportId || 'explore-drilldown-export');

        let handle = {
            overlay: overlay,
            titleEl: titleEl,
            tbodyEl: tbodyEl,
            countEl: countEl
        };

        function close() {
            overlay.classList.add('hidden');
            document.body.style.overflow = '';
            // WCAG: restore focus to trigger element
            if (previousFocus) {
                previousFocus.focus();
                previousFocus = null;
            }
        }

        if (closeBtn) closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) close();
        });

        // Escape key — only close this overlay if it's visible
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !overlay.classList.contains('hidden')) {
                close();
            }
        });

        // WCAG: focus trap — keep Tab cycling within the overlay
        // Queries focusable elements dynamically (content is populated after open)
        overlay.addEventListener('keydown', function(e) {
            if (e.key !== 'Tab' || overlay.classList.contains('hidden')) return;
            let focusable = overlay.querySelectorAll('a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])');
            if (!focusable.length) return;
            let first = focusable[0];
            let last = focusable[focusable.length - 1];
            if (e.shiftKey) {
                if (document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        });

        // CSV export
        if (exportBtn) {
            exportBtn.addEventListener('click', function() {
                if (!currentData.length) return;
                let lines = ['Nr.;Datum;Sammlung;Regest'];
                for (let i = 0; i < currentData.length; i++) {
                    let d = currentData[i];
                    lines.push([d.i, d.d, d.c, (d.r || '').replace(/;/g, ',')].join(';'));
                }
                let blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' });
                let url = URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = 'exploration_' + (titleEl ? titleEl.textContent : 'export').replace(/[^a-zA-Z0-9]/g, '_') + '.csv';
                a.click();
                URL.revokeObjectURL(url);
            });
        }

        handle.close = close;
        boundOverlays[overlayId] = handle;
        return handle;
    }


    /* ------------------------------------------------------------------
       Open drill-down: show overlay, lazy-load docs, populate table
       ------------------------------------------------------------------ */

    function open(handle, title, fileKeys) {
        if (!handle || !fileKeys.length) return;
        // WCAG: store trigger element for focus restoration
        previousFocus = document.activeElement;
        handle.titleEl.textContent = title;
        handle.tbodyEl.innerHTML = '<tr><td colspan="4" class="cell-placeholder">Lade Quellendaten\u2026</td></tr>';
        handle.countEl.textContent = fileKeys.length + ' Quellen';
        handle.overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        // WCAG: move focus to close button
        let closeBtn = handle.overlay.querySelector('.explore-drilldown-close');
        if (closeBtn) closeBtn.focus();

        loadDocsLookup(function(lookup) {
            currentData = [];
            handle.tbodyEl.innerHTML = '';
            for (let i = 0; i < fileKeys.length; i++) {
                let doc = lookup[fileKeys[i]];
                if (!doc) continue;
                currentData.push(doc);
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td><a href="./' + doc.u + '">' + esc(doc.i) + '</a></td>' +
                    '<td>' + esc(doc.d) + '</td>' +
                    '<td>' + esc(doc.c) + '</td>' +
                    '<td>' + esc(doc.r) + '</td>';
                handle.tbodyEl.appendChild(tr);
            }
            handle.countEl.textContent = currentData.length + ' Quellen';
        });
    }


    /* ------------------------------------------------------------------
       Public API
       ------------------------------------------------------------------ */

    return {
        loadDocsLookup: loadDocsLookup,
        bind: bind,
        open: open
    };

})();
