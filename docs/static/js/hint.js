/* ==========================================================================
   Hover hint: lightweight transient tooltip following the cursor.

   Trigger contract: any element with [data-hint="text"]. Optionally a
   small uppercase type label via [data-hint-type="Person"] etc.

   Replaces native title-attributes for UI controls (Toolbar-Actions, Nav,
   Histogram-Bars) and entity annotations in the document text
   (.anno-person, .anno-org, .anno-place).

   A single .tip-hint element is appended to body and positioned at the
   cursor on mouseover. No click persistence, no ARIA dialog semantics --
   this is decorative UI orientation, not content.
   ========================================================================== */

(function () {
    'use strict';

    function initHint() {
        let hint = document.createElement('div');
        hint.className = 'tip-hint';
        hint.setAttribute('aria-hidden', 'true');
        hint.innerHTML =
            '<span class="tip-hint-type"></span>' +
            '<span class="tip-hint-body"></span>';
        document.body.appendChild(hint);

        let typeEl = hint.querySelector('.tip-hint-type');
        let bodyEl = hint.querySelector('.tip-hint-body');

        function show(target) {
            let body = target.getAttribute('data-hint') || '';
            let type = target.getAttribute('data-hint-type') || '';
            if (!body) return;
            if (type) {
                typeEl.textContent = type;
                typeEl.style.display = '';
            } else {
                typeEl.textContent = '';
                typeEl.style.display = 'none';
            }
            bodyEl.textContent = body;
            hint.classList.add('is-visible');
        }

        function hide() {
            hint.classList.remove('is-visible');
        }

        function position(e) {
            if (!hint.classList.contains('is-visible')) return;
            let x = e.clientX + 12;
            let y = e.clientY + 16;
            let w = hint.offsetWidth;
            let h = hint.offsetHeight;
            if (x + w > window.innerWidth - 8) x = e.clientX - w - 8;
            if (y + h > window.innerHeight - 8) y = e.clientY - h - 8;
            hint.style.left = x + 'px';
            hint.style.top = y + 'px';
        }

        document.addEventListener('mouseover', function (e) {
            let t = e.target.closest('[data-hint]');
            if (t) show(t);
        });

        document.addEventListener('mouseout', function (e) {
            let t = e.target.closest('[data-hint]');
            if (!t) return;
            // Ignore moves between child elements of the same trigger.
            let rel = e.relatedTarget;
            if (rel && rel.closest && rel.closest('[data-hint]') === t) return;
            hide();
        });

        document.addEventListener('mousemove', position);

        // Hide when scrolling: position becomes stale otherwise.
        document.addEventListener('scroll', hide, true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHint);
    } else {
        initHint();
    }
})();
