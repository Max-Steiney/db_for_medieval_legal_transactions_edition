/* ==========================================================================
   Stadt und Gemeinschaft Wien — Datenbank
   Provenienz-Popover: Projekt-Standard für aggregierte Zahlen.

   Interaktions-Modell:
   - Hover / Focus  → öffnet transient (schließt beim Verlassen)
   - Klick          → fixiert persistent (bleibt offen, bis explizit zu)
   - Hover beim fixierten Popover → ignoriert (kein Wegflackern)
   - ESC / Klick außerhalb → schließt beides

   Ein Popover ist zu jeder Zeit aktiv. Beim Öffnen eines neuen wird
   das vorige geschlossen.
   ========================================================================== */

(function () {
    'use strict';

    let HOVER_CLOSE_DELAY = 180;  // ms, kleine Toleranz beim Wechsel Trigger↔Popover

    let currentOpen = null;       // aktuell offenes aside
    let pinned = false;           // wurde es per Klick fixiert?
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

    // --- Klick: fixieren / toggle / schließen ----------------------------

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
        // Klick außerhalb des offenen Popovers schließt es.
        if (currentOpen && !e.target.closest('.prov-popover')) {
            close(currentOpen);
        }
    });

    // --- Hover / Fokus: transient öffnen ---------------------------------

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
        // Nur schließen, wenn wir den Hover-Bereich ganz verlassen.
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

    // --- Tastatur: ESC schließt ------------------------------------------

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && currentOpen) {
            close(currentOpen);
            // Fokus zurück auf den Trigger, für Screenreader-Flow
            let t = findTrigger(currentOpen && currentOpen.id);
            if (t) t.focus();
        }
    });
})();
