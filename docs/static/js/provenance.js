/* ==========================================================================
   Stadt und Gemeinschaft Wien — Datenbank
   Provenance popover: project-wide convention for aggregate numbers.

   Interaction model:
   - Hover / focus  -> transient open (closes on leave)
   - Click          -> pinned (stays open until explicitly closed)
   - Hover over a pinned popover -> ignored (prevents flicker)
   - ESC / outside click -> closes both modes

   At most one popover is open at a time; opening a new one closes the
   previous.
   ========================================================================== */

(function () {
    'use strict';

    let HOVER_CLOSE_DELAY = 180;  // ms; tolerance for trigger<->popover transit

    let currentOpen = null;
    let pinned = false;
    let hoverCloseTimer = null;

    function findTrigger(popoverId) {
        return document.querySelector('[data-prov-trigger="' + popoverId + '"]');
    }

    function close(popover) {
        if (!popover) return;
        popover.setAttribute('aria-hidden', 'true');
        let trigger = findTrigger(popover.id);
        if (trigger) trigger.setAttribute('aria-expanded', 'false');
        if (currentOpen === popover) {
            currentOpen = null;
            pinned = false;
        }
    }

    function open(popover, makePinned) {
        if (!popover) return;
        if (currentOpen && currentOpen !== popover) close(currentOpen);
        popover.setAttribute('aria-hidden', 'false');
        let trigger = findTrigger(popover.id);
        if (trigger) trigger.setAttribute('aria-expanded', 'true');
        currentOpen = popover;
        if (makePinned) pinned = true;
        // Viewport-Constraint: nach Render messen und ggf. seitlich klemmen
        requestAnimationFrame(function () { clampToViewport(popover); });
    }

    // Verschiebt das Popover horizontal so, dass es im Viewport bleibt,
    // und kompensiert die Pfeil-Position via CSS-Variable, damit der
    // Pfeil weiter auf den Trigger zeigt.
    // Nutzt documentElement.clientWidth (= sichtbarer Bereich ohne Scrollbar)
    // statt window.innerWidth (das die Scrollbar mitzaehlt).
    function clampToViewport(popover) {
        popover.style.transform = '';
        popover.style.setProperty('--prov-arrow-offset', '0px');
        let rect = popover.getBoundingClientRect();
        let margin = 12;
        let vw = document.documentElement.clientWidth;
        let shift = 0;
        if (rect.right > vw - margin) {
            shift = (vw - margin) - rect.right;
        } else if (rect.left < margin) {
            shift = margin - rect.left;
        }
        if (shift !== 0) {
            popover.style.transform = 'translateX(calc(-50% + ' + shift + 'px))';
            popover.style.setProperty('--prov-arrow-offset', (-shift) + 'px');
        }
    }

    function cancelHoverClose() {
        if (hoverCloseTimer) {
            clearTimeout(hoverCloseTimer);
            hoverCloseTimer = null;
        }
    }

    function scheduleHoverClose(popover) {
        cancelHoverClose();
        hoverCloseTimer = setTimeout(function () {
            if (!pinned && currentOpen === popover) close(popover);
        }, HOVER_CLOSE_DELAY);
    }

    // --- Click: pin / toggle / close -----------------------------------

    document.addEventListener('click', function (e) {
        let trigger = e.target.closest('[data-prov-trigger]');
        if (trigger) {
            e.preventDefault();
            e.stopPropagation();
            let id = trigger.getAttribute('data-prov-trigger');
            let p = document.getElementById(id);
            if (!p) return;
            if (currentOpen === p && pinned) {
                close(p);
            } else {
                open(p, true);  // Klick = pinnen
            }
            return;
        }
        let closeBtn = e.target.closest('.prov-popover-close');
        if (closeBtn) {
            e.preventDefault();
            close(closeBtn.closest('.prov-popover'));
            return;
        }
        if (currentOpen && !e.target.closest('.prov-popover')) {
            close(currentOpen);
        }
    });

    // --- Hover / focus: transient open ---------------------------------

    document.addEventListener('mouseover', function (e) {
        let trigger = e.target.closest('[data-prov-trigger]');
        if (trigger) {
            cancelHoverClose();
            let id = trigger.getAttribute('data-prov-trigger');
            let p = document.getElementById(id);
            if (p && currentOpen !== p) open(p, false);
            return;
        }
        let pop = e.target.closest('.prov-popover');
        if (pop && currentOpen === pop) {
            cancelHoverClose();
        }
    });

    document.addEventListener('mouseout', function (e) {
        let trigger = e.target.closest('[data-prov-trigger]');
        let pop = e.target.closest('.prov-popover');
        if (!trigger && !pop) return;
        // Only close when leaving the trigger/popover hover region entirely.
        let relTarget = e.relatedTarget;
        let goingToTrigger = relTarget && relTarget.closest && relTarget.closest('[data-prov-trigger]') === findTrigger(currentOpen ? currentOpen.id : '');
        let goingToPop = relTarget && relTarget.closest && relTarget.closest('.prov-popover') === currentOpen;
        if (goingToTrigger || goingToPop) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    document.addEventListener('focusin', function (e) {
        let trigger = e.target.closest('[data-prov-trigger]');
        if (!trigger) return;
        cancelHoverClose();
        let id = trigger.getAttribute('data-prov-trigger');
        let p = document.getElementById(id);
        if (p && currentOpen !== p) open(p, false);
    });

    document.addEventListener('focusout', function (e) {
        let trigger = e.target.closest('[data-prov-trigger]');
        if (!trigger) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    // --- Keyboard: ESC closes ------------------------------------------

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && currentOpen) {
            close(currentOpen);
            // Restore focus to trigger for screen-reader flow
            let t = findTrigger(currentOpen && currentOpen.id);
            if (t) t.focus();
        }
    });
})();
