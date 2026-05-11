/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Facsimile viewer (synopsis mode)
   ========================================================================== */

(function() {
    'use strict';

    function initFacsimileViewer() {
        let urlScript = document.querySelector('.facs-urls');
        let facsUrls = [];
        if (urlScript) {
            try { facsUrls = JSON.parse(urlScript.textContent); } catch(e) { /* ignore */ }
        }
        if (!facsUrls.length) return;

        let currentPage = 0;
        let zoom = 1;
        let imgEl = document.getElementById('facs-image');
        let wrapEl = document.getElementById('facs-image-wrap');
        let currentEl = document.getElementById('facs-current');
        let prevBtn = document.querySelector('.facs-prev');
        let nextBtn = document.querySelector('.facs-next');
        let loaded = {};

        loadCurrentImage();

        function loadCurrentImage() {
            if (!imgEl || currentPage >= facsUrls.length) return;
            let url = facsUrls[currentPage];
            // Per-page alt text: append page number for multi-page sources
            // so screen readers can distinguish facsimile pages.
            let baseAlt = imgEl.getAttribute('data-alt-base');
            if (!baseAlt) {
                baseAlt = imgEl.getAttribute('alt') || '';
                imgEl.setAttribute('data-alt-base', baseAlt);
            }
            if (facsUrls.length > 1) {
                imgEl.alt = baseAlt + ', Seite ' + (currentPage + 1) + ' von ' + facsUrls.length;
            } else {
                imgEl.alt = baseAlt;
            }
            if (loaded[url]) { imgEl.src = url; return; }
            imgEl.classList.add('loading');
            imgEl.src = url;
            imgEl.onload = function() { imgEl.classList.remove('loading'); loaded[url] = true; };
            imgEl.onerror = function() { imgEl.classList.remove('loading'); imgEl.alt = 'Bild konnte nicht geladen werden'; };
        }

        if (prevBtn) prevBtn.addEventListener('click', function() {
            if (currentPage > 0) { currentPage--; updatePageControls(); loadCurrentImage(); }
        });
        if (nextBtn) nextBtn.addEventListener('click', function() {
            if (currentPage < facsUrls.length - 1) { currentPage++; updatePageControls(); loadCurrentImage(); }
        });

        function updatePageControls() {
            if (currentEl) currentEl.textContent = currentPage + 1;
            if (prevBtn) prevBtn.disabled = currentPage === 0;
            if (nextBtn) nextBtn.disabled = currentPage >= facsUrls.length - 1;
            resetZoom();
        }

        let zoomIn = document.querySelector('.facs-zoom-in');
        let zoomOut = document.querySelector('.facs-zoom-out');
        let zoomReset = document.querySelector('.facs-zoom-reset');

        if (zoomIn) zoomIn.addEventListener('click', function() { setZoom(zoom * 1.3); });
        if (zoomOut) zoomOut.addEventListener('click', function() { setZoom(zoom / 1.3); });
        if (zoomReset) zoomReset.addEventListener('click', resetZoom);

        function setZoom(z) {
            zoom = Math.max(0.5, Math.min(5, z));
            if (imgEl) imgEl.style.transform = 'scale(' + zoom + ')';
        }

        function resetZoom() {
            zoom = 1;
            if (imgEl) imgEl.style.transform = 'scale(1)';
        }

        if (wrapEl) {
            wrapEl.addEventListener('wheel', function(e) {
                e.preventDefault();
                let delta = e.deltaY > 0 ? 0.9 : 1.1;
                setZoom(zoom * delta);
            }, { passive: false });
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        initFacsimileViewer();
    });

})();
