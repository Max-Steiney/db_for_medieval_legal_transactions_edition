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

    var HOVER_CLOSE_DELAY = 180;  // ms, kleine Toleranz beim Wechsel Trigger↔Popover

    var currentOpen = null;       // aktuell offenes aside
    var pinned = false;           // wurde es per Klick fixiert?
    var hoverCloseTimer = null;

    function findTrigger(popoverId) {
        return document.querySelector('[data-prov-trigger="' + popoverId + '"]');
    }

    function close(popover) {
        if (!popover) return;
        popover.setAttribute('aria-hidden', 'true');
        var trigger = findTrigger(popover.id);
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
        var trigger = findTrigger(popover.id);
        if (trigger) trigger.setAttribute('aria-expanded', 'true');
        currentOpen = popover;
        if (makePinned) pinned = true;
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
        var trigger = e.target.closest('[data-prov-trigger]');
        if (trigger) {
            e.preventDefault();
            e.stopPropagation();
            var id = trigger.getAttribute('data-prov-trigger');
            var p = document.getElementById(id);
            if (!p) return;
            if (currentOpen === p && pinned) {
                close(p);
            } else {
                open(p, true);  // Klick = pinnen
            }
            return;
        }
        var closeBtn = e.target.closest('.prov-popover-close');
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
        var trigger = e.target.closest('[data-prov-trigger]');
        if (trigger) {
            cancelHoverClose();
            var id = trigger.getAttribute('data-prov-trigger');
            var p = document.getElementById(id);
            if (p && currentOpen !== p) open(p, false);
            return;
        }
        var pop = e.target.closest('.prov-popover');
        if (pop && currentOpen === pop) {
            cancelHoverClose();
        }
    });

    document.addEventListener('mouseout', function (e) {
        var trigger = e.target.closest('[data-prov-trigger]');
        var pop = e.target.closest('.prov-popover');
        if (!trigger && !pop) return;
        // Nur schließen, wenn wir den Hover-Bereich ganz verlassen.
        var relTarget = e.relatedTarget;
        var goingToTrigger = relTarget && relTarget.closest && relTarget.closest('[data-prov-trigger]') === findTrigger(currentOpen ? currentOpen.id : '');
        var goingToPop = relTarget && relTarget.closest && relTarget.closest('.prov-popover') === currentOpen;
        if (goingToTrigger || goingToPop) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    document.addEventListener('focusin', function (e) {
        var trigger = e.target.closest('[data-prov-trigger]');
        if (!trigger) return;
        cancelHoverClose();
        var id = trigger.getAttribute('data-prov-trigger');
        var p = document.getElementById(id);
        if (p && currentOpen !== p) open(p, false);
    });

    document.addEventListener('focusout', function (e) {
        var trigger = e.target.closest('[data-prov-trigger]');
        if (!trigger) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    // --- Tastatur: ESC schließt ------------------------------------------

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && currentOpen) {
            close(currentOpen);
            // Fokus zurück auf den Trigger, für Screenreader-Flow
            var t = findTrigger(currentOpen && currentOpen.id);
            if (t) t.focus();
        }
    });
})();
