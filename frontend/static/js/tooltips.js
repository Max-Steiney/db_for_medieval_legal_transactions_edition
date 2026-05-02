/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Tooltips (entity hover)
   ========================================================================== */

(function() {
    'use strict';

    function initTooltips() {
        let tooltip = document.createElement('div');
        tooltip.className = 'edition-tooltip';
        tooltip.innerHTML = '<span class="tooltip-type"></span><span class="tooltip-name"></span><span class="tooltip-id"></span>';
        document.body.appendChild(tooltip);

        let typeEl = tooltip.querySelector('.tooltip-type');
        let nameEl = tooltip.querySelector('.tooltip-name');
        let idEl = tooltip.querySelector('.tooltip-id');

        let typeLabels = {
            'anno-person': ['Person', 'tooltip-type-person'],
            'anno-org': ['Organisation', 'tooltip-type-org'],
            'anno-place': ['Ort', 'tooltip-type-place']
        };

        document.addEventListener('mouseover', function(e) {
            let target = e.target.closest('.anno-person, .anno-org, .anno-place');
            if (!target) return;

            let cls = target.classList.contains('anno-person') ? 'anno-person' :
                      target.classList.contains('anno-org') ? 'anno-org' : 'anno-place';
            let info = typeLabels[cls];
            let title = target.getAttribute('title') || '';
            let ref = target.getAttribute('data-ref') || '';

            let name = title.replace(/\s*\[.*\]\s*$/, '');

            typeEl.className = 'tooltip-type ' + info[1];
            typeEl.textContent = info[0];
            nameEl.textContent = name;
            idEl.textContent = ref;

            if (title) {
                target.setAttribute('data-title', title);
                target.removeAttribute('title');
            }

            tooltip.classList.add('visible');
        });

        document.addEventListener('mousemove', function(e) {
            if (!tooltip.classList.contains('visible')) return;
            let x = e.clientX + 12;
            let y = e.clientY + 16;
            let w = tooltip.offsetWidth;
            let h = tooltip.offsetHeight;
            if (x + w > window.innerWidth - 8) x = e.clientX - w - 8;
            if (y + h > window.innerHeight - 8) y = e.clientY - h - 8;
            tooltip.style.left = x + 'px';
            tooltip.style.top = y + 'px';
        });

        document.addEventListener('mouseout', function(e) {
            let target = e.target.closest('.anno-person, .anno-org, .anno-place');
            if (!target) return;
            tooltip.classList.remove('visible');
            let saved = target.getAttribute('data-title');
            if (saved) {
                target.setAttribute('title', saved);
                target.removeAttribute('data-title');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        initTooltips();
    });

})();
