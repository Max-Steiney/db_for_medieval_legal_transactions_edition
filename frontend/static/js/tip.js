/* ==========================================================================
   Tip popover: persistent tooltip for glossary terms and data provenance.

   Interaction model:
   - Hover / focus     -> transient open (closes on leave)
   - Click             -> pinned (stays open until explicitly closed)
   - Hover over pinned -> ignored (prevents flicker)
   - ESC / outside     -> closes both modes

   Single shared mechanic for both .tip-popover--glossary and
   .tip-popover--data. At most one popover is open at a time.

   Trigger contract: any element with [data-tip="popover-id"]. The popover
   element itself is .tip-popover with id="popover-id".
   ========================================================================== */

(function () {
    'use strict';

    let HOVER_CLOSE_DELAY = 180;  // ms tolerance for trigger<->popover transit

    let currentOpen = null;
    let pinned = false;
    let hoverCloseTimer = null;

    function findTrigger(popoverId) {
        return document.querySelector('[data-tip="' + popoverId + '"]');
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
        requestAnimationFrame(function () { clampToViewport(popover); });
    }

    // Horizontal viewport clamp. Uses documentElement.clientWidth (the
    // visible area excluding scrollbar) and compensates the arrow position
    // via the --tip-arrow-offset CSS custom property.
    function clampToViewport(popover) {
        popover.style.transform = '';
        popover.style.setProperty('--tip-arrow-offset', '0px');
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
            popover.style.setProperty('--tip-arrow-offset', (-shift) + 'px');
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
        let trigger = e.target.closest('[data-tip]');
        if (trigger) {
            e.preventDefault();
            e.stopPropagation();
            let id = trigger.getAttribute('data-tip');
            let p = document.getElementById(id);
            if (!p) return;
            if (currentOpen === p && pinned) {
                close(p);
            } else {
                open(p, true);
            }
            return;
        }
        let closeBtn = e.target.closest('.tip-close');
        if (closeBtn) {
            e.preventDefault();
            close(closeBtn.closest('.tip-popover'));
            return;
        }
        if (currentOpen && !e.target.closest('.tip-popover')) {
            close(currentOpen);
        }
    });

    // --- Hover / focus: transient open ---------------------------------

    document.addEventListener('mouseover', function (e) {
        let trigger = e.target.closest('[data-tip]');
        if (trigger) {
            cancelHoverClose();
            let id = trigger.getAttribute('data-tip');
            let p = document.getElementById(id);
            if (p && currentOpen !== p) open(p, false);
            return;
        }
        let pop = e.target.closest('.tip-popover');
        if (pop && currentOpen === pop) {
            cancelHoverClose();
        }
    });

    document.addEventListener('mouseout', function (e) {
        let trigger = e.target.closest('[data-tip]');
        let pop = e.target.closest('.tip-popover');
        if (!trigger && !pop) return;
        let relTarget = e.relatedTarget;
        let goingToTrigger = relTarget && relTarget.closest
            && relTarget.closest('[data-tip]') === findTrigger(currentOpen ? currentOpen.id : '');
        let goingToPop = relTarget && relTarget.closest
            && relTarget.closest('.tip-popover') === currentOpen;
        if (goingToTrigger || goingToPop) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    document.addEventListener('focusin', function (e) {
        let trigger = e.target.closest('[data-tip]');
        if (!trigger) return;
        cancelHoverClose();
        let id = trigger.getAttribute('data-tip');
        let p = document.getElementById(id);
        if (p && currentOpen !== p) open(p, false);
    });

    document.addEventListener('focusout', function (e) {
        let trigger = e.target.closest('[data-tip]');
        if (!trigger) return;
        if (currentOpen && !pinned) scheduleHoverClose(currentOpen);
    });

    // --- Keyboard: ESC closes ------------------------------------------

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && currentOpen) {
            close(currentOpen);
            let t = findTrigger(currentOpen && currentOpen.id);
            if (t) t.focus();
        }
    });
})();
