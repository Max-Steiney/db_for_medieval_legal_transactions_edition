// Facsimile viewer (OpenSeadragon)

(function() {
    'use strict';

    function initFacsimileViewer() {
        let urlScript = document.querySelector('.facs-urls');
        let facsUrls = [];
        if (urlScript) {
            try { facsUrls = JSON.parse(urlScript.textContent); } catch(e) { /* ignore */ }
        }
        if (!facsUrls.length) return;
        if (typeof OpenSeadragon !== 'function') return;

        let host = document.getElementById('facs-osd');
        if (!host) return;

        let currentPage = 0;
        let currentEl = document.getElementById('facs-current');
        let prevBtn = document.querySelector('.facs-prev');
        let nextBtn = document.querySelector('.facs-next');
        let zoomIn = document.querySelector('.facs-zoom-in');
        let zoomOut = document.querySelector('.facs-zoom-out');
        let zoomReset = document.querySelector('.facs-zoom-reset');
        let rotateBtn = document.querySelector('.facs-rotate');
        let fullscreenBtn = document.querySelector('.facs-fullscreen');
        let viewerEl = document.querySelector('.facs-viewer');

        let viewer = OpenSeadragon({
            element: host,
            tileSources: { type: 'image', url: facsUrls[currentPage] },
            drawer: 'canvas',
            showNavigationControl: false,
            showNavigator: false,
            showRotationControl: false,
            showFullPageControl: false,
            showHomeControl: false,
            showZoomControl: false,
            animationTime: 0.4,
            blendTime: 0.1,
            minZoomImageRatio: 1,
            maxZoomPixelRatio: 6,
            visibilityRatio: 1,
            constrainDuringPan: true,
            homeFillsViewer: false,
            gestureSettingsMouse: { scrollToZoom: true,  clickToZoom: false, dblClickToZoom: true, dragToPan: true, pinchToZoom: false },
            gestureSettingsTouch: { scrollToZoom: false, clickToZoom: false, dblClickToZoom: true, dragToPan: true, pinchToZoom: true  },
            gestureSettingsPen:   { scrollToZoom: false, clickToZoom: false, dblClickToZoom: true, dragToPan: true, pinchToZoom: false }
        });

        function loadPage(idx) {
            if (idx < 0 || idx >= facsUrls.length) return;
            currentPage = idx;
            viewer.open({ type: 'image', url: facsUrls[currentPage] });
            updatePageControls();
        }

        function updatePageControls() {
            if (currentEl) currentEl.textContent = currentPage + 1;
            if (prevBtn) prevBtn.disabled = currentPage === 0;
            if (nextBtn) nextBtn.disabled = currentPage >= facsUrls.length - 1;
        }

        if (prevBtn) prevBtn.addEventListener('click', function() { loadPage(currentPage - 1); });
        if (nextBtn) nextBtn.addEventListener('click', function() { loadPage(currentPage + 1); });

        if (zoomIn) zoomIn.addEventListener('click', function() {
            viewer.viewport.zoomBy(1.3);
            viewer.viewport.applyConstraints();
        });
        if (zoomOut) zoomOut.addEventListener('click', function() {
            viewer.viewport.zoomBy(1 / 1.3);
            viewer.viewport.applyConstraints();
        });
        if (zoomReset) zoomReset.addEventListener('click', function() {
            viewer.viewport.setRotation(0);
            viewer.viewport.goHome();
        });
        if (rotateBtn) rotateBtn.addEventListener('click', function() {
            let next = (viewer.viewport.getRotation() + 90) % 360;
            viewer.viewport.setRotation(next);
        });

        // Native fullscreen on the whole viewer so page nav and zoom stay usable.
        if (fullscreenBtn && viewerEl && viewerEl.requestFullscreen) {
            fullscreenBtn.addEventListener('click', function() {
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    viewerEl.requestFullscreen();
                }
            });
            document.addEventListener('fullscreenchange', function() {
                let active = document.fullscreenElement === viewerEl;
                fullscreenBtn.setAttribute('data-hint', active ? 'Vollbild verlassen' : 'Vollbild');
                fullscreenBtn.setAttribute('aria-label', active ? 'Vollbild verlassen' : 'Vollbild');
            });
        } else if (fullscreenBtn) {
            fullscreenBtn.style.display = 'none';
        }

        // Reset rotation on page change so a new page does not start tilted.
        viewer.addHandler('open', function() {
            viewer.viewport.setRotation(0);
        });

        updatePageControls();
    }

    document.addEventListener('DOMContentLoaded', initFacsimileViewer);

})();
