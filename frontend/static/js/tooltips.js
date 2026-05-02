/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Tooltips — einheitlicher Hover-Tooltip ueber alle Seiten:

   - Entity-Tooltip (Person/Org/Ort): triggers via .anno-person/.anno-org/
     .anno-place, zeigt Typ-Badge + Name + ID. Wird von annotierten
     Begriffen im Dokumenttext genutzt.
   - Daten-Tooltip (Badges, Pillen, Hinweise): triggers via [data-tip-title],
     zeigt Titel + optionalen Body. Wird von Tabellen-Badges, Form-Pillen,
     Datums-Hinweisen und vergleichbaren UI-Elementen genutzt — als Ersatz
     fuer native title-Attribute, damit Stil und Verhalten konsistent sind.

   Beide Varianten teilen sich Cursor-Tracking, .visible-State und das
   Outline-Styling (.edition-tooltip in components.css/document.css).
   ========================================================================== */

(function() {
    'use strict';

    function initTooltips() {
        let tooltip = document.createElement('div');
        tooltip.className = 'edition-tooltip';
        tooltip.innerHTML =
            '<span class="tooltip-type"></span>' +
            '<span class="tooltip-name"></span>' +
            '<span class="tooltip-id"></span>' +
            '<span class="tooltip-body"></span>';
        document.body.appendChild(tooltip);

        let typeEl = tooltip.querySelector('.tooltip-type');
        let nameEl = tooltip.querySelector('.tooltip-name');
        let idEl = tooltip.querySelector('.tooltip-id');
        let bodyEl = tooltip.querySelector('.tooltip-body');

        let typeLabels = {
            'anno-person': ['Person', 'tooltip-type-person'],
            'anno-org': ['Organisation', 'tooltip-type-org'],
            'anno-place': ['Ort', 'tooltip-type-place']
        };

        function showEntity(target) {
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
            bodyEl.textContent = '';
            tooltip.classList.add('visible');
            tooltip.classList.remove('edition-tooltip--data');

            if (title) {
                target.setAttribute('data-title', title);
                target.removeAttribute('title');
            }
        }

        function showData(target) {
            let title = target.getAttribute('data-tip-title') || '';
            let body = target.getAttribute('data-tip-body') || '';

            typeEl.className = 'tooltip-type';
            typeEl.textContent = '';
            nameEl.textContent = title;
            idEl.textContent = '';
            bodyEl.textContent = body;
            tooltip.classList.add('visible', 'edition-tooltip--data');
        }

        document.addEventListener('mouseover', function(e) {
            let entity = e.target.closest('.anno-person, .anno-org, .anno-place');
            if (entity) { showEntity(entity); return; }
            let data = e.target.closest('[data-tip-title]');
            if (data) { showData(data); return; }
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
            let entity = e.target.closest('.anno-person, .anno-org, .anno-place');
            let data = e.target.closest('[data-tip-title]');
            if (!entity && !data) return;
            tooltip.classList.remove('visible');
            if (entity) {
                let saved = entity.getAttribute('data-title');
                if (saved) {
                    entity.setAttribute('title', saved);
                    entity.removeAttribute('data-title');
                }
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        initTooltips();
    });

})();
