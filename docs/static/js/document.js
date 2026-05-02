/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Document page: factoid view + citation helper
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;


    /* ------------------------------------------------------------------
       Factoid View — extract atomic assertions from annotation spans
       ------------------------------------------------------------------ */

    function initFactoidView() {
        let toggleBtn = document.getElementById('factoid-toggle');
        let container = document.getElementById('factoid-view');
        if (!toggleBtn || !container) return;

        let built = false;

        toggleBtn.addEventListener('click', function() {
            let isVisible = !container.classList.contains('hidden');
            if (isVisible) {
                container.classList.add('hidden');
                toggleBtn.setAttribute('aria-expanded', 'false');
                return;
            }
            if (!built) {
                buildFactoidTable(container);
                built = true;
            }
            container.classList.remove('hidden');
            toggleBtn.setAttribute('aria-expanded', 'true');
        });
    }

    function buildFactoidTable(container) {
        let body = document.querySelector('.doc-body');
        if (!body) return;

        let factoids = [];

        // Walk all function role spans — each is a factoid context
        let fnSpans = body.querySelectorAll('.anno-fn');
        for (let i = 0; i < fnSpans.length; i++) {
            let fnSpan = fnSpans[i];
            let role = fnSpan.getAttribute('data-role') || '';
            let roleLabel = {
                'issuer': 'Aussteller*in',
                'recipient': 'Empf\u00e4nger*in',
                'witness': 'Zeug*in',
                'other': 'Sonstige'
            }[role] || role;

            // Find entities within this function span
            let entities = fnSpan.querySelectorAll('.anno-person, .anno-org, .anno-place');
            for (let j = 0; j < entities.length; j++) {
                let entity = entities[j];
                let type = entity.classList.contains('anno-person') ? 'Person' :
                           entity.classList.contains('anno-org') ? 'Organisation' : 'Ort';
                let ref = entity.getAttribute('data-ref') || '';
                let name = entity.textContent.trim();
                let title = entity.getAttribute('title') || entity.getAttribute('data-title') || '';
                if (title) name = title.replace(/\s*\[.*\]\s*$/, '') || name;

                // Collect attributes (roleName) within or near this entity
                let attrs = [];
                let attrSpans = entity.querySelectorAll('.anno-attr');
                for (let k = 0; k < attrSpans.length; k++) {
                    attrs.push(attrSpans[k].textContent.trim());
                }

                // Find event context (closest parent anno-event)
                let eventSpan = entity.closest('.anno-event');
                let eventRef = eventSpan ? (eventSpan.getAttribute('data-ref') || '') : '';

                factoids.push({
                    entity: name,
                    type: type,
                    ref: ref,
                    role: roleLabel,
                    attributes: attrs.join(', '),
                    event: eventRef
                });
            }
        }

        // Also find entities NOT inside any function span (standalone annotations)
        let allEntities = body.querySelectorAll('.anno-person, .anno-org, .anno-place');
        for (let m = 0; m < allEntities.length; m++) {
            let el = allEntities[m];
            if (el.closest('.anno-fn')) continue; // already captured above
            let elType = el.classList.contains('anno-person') ? 'Person' :
                         el.classList.contains('anno-org') ? 'Organisation' : 'Ort';
            let elRef = el.getAttribute('data-ref') || '';
            let elName = el.textContent.trim();
            let elTitle = el.getAttribute('title') || el.getAttribute('data-title') || '';
            if (elTitle) elName = elTitle.replace(/\s*\[.*\]\s*$/, '') || elName;

            let elAttrs = [];
            let elAttrSpans = el.querySelectorAll('.anno-attr');
            for (let n = 0; n < elAttrSpans.length; n++) {
                elAttrs.push(elAttrSpans[n].textContent.trim());
            }

            let elEvent = el.closest('.anno-event');
            let elEventRef = elEvent ? (elEvent.getAttribute('data-ref') || '') : '';

            factoids.push({
                entity: elName,
                type: elType,
                ref: elRef,
                role: '\u2013',
                attributes: elAttrs.join(', '),
                event: elEventRef
            });
        }

        if (factoids.length === 0) {
            container.innerHTML = '<p class="factoid-empty">Keine annotierten Entit\u00e4ten in diesem Dokument.</p>';
            return;
        }

        let html = '<table class="factoid-table"><thead><tr>'
            + '<th>Entit\u00e4t</th><th>Typ</th><th>Rolle</th><th>Attribute</th><th>Event</th><th>ID</th>'
            + '</tr></thead><tbody>';
        for (let p = 0; p < factoids.length; p++) {
            let f = factoids[p];
            html += '<tr>'
                + '<td>' + esc(f.entity) + '</td>'
                + '<td><span class="factoid-type factoid-type-' + f.type.toLowerCase() + '">' + esc(f.type) + '</span></td>'
                + '<td>' + esc(f.role) + '</td>'
                + '<td>' + esc(f.attributes || '\u2013') + '</td>'
                + '<td><span class="cell-id">' + esc(f.event || '\u2013') + '</span></td>'
                + '<td><span class="cell-id">' + esc(f.ref) + '</span></td>'
                + '</tr>';
        }
        html += '</tbody></table>';

        container.innerHTML = '<div class="factoid-header">'
            + '<span class="factoid-count">' + factoids.length + ' Faktoid' + (factoids.length !== 1 ? 'e' : '') + '</span>'
            + '</div>' + html;
    }


    /* ------------------------------------------------------------------
       Citation Helper — formatted citation with copy-to-clipboard
       ------------------------------------------------------------------ */

    function initCitationHelper() {
        let btn = document.getElementById('cite-toggle');
        let popover = document.getElementById('cite-popover');
        if (!btn || !popover) return;

        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            let isVisible = !popover.classList.contains('hidden');
            if (isVisible) {
                popover.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            } else {
                buildCitations(popover);
                popover.classList.remove('hidden');
                btn.setAttribute('aria-expanded', 'true');
            }
        });

        document.addEventListener('click', function(e) {
            if (!popover.contains(e.target) && e.target !== btn) {
                popover.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                popover.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    function buildCitations(popover) {
        // Read metadata from the page DOM
        let metaScript = document.getElementById('doc-meta');
        if (!metaScript) return;
        let meta;
        try { meta = JSON.parse(metaScript.textContent); } catch(e) { return; }

        let idno = meta.idno || '';
        let dateDisplay = meta.date_display || '';
        let citation = meta.citation || '';
        let collection = meta.collection_label || '';
        let url = window.location.href;
        let today = new Date().toISOString().slice(0, 10);

        // Chicago style
        let chicago = '';
        if (citation) {
            chicago = citation + '.';
        } else {
            chicago = 'Nr. ' + idno;
            if (dateDisplay) chicago += ' (' + dateDisplay + ')';
            chicago += '.';
        }
        chicago += ' In: Wiener Urkundenbuch Digital. Universität Wien.';
        chicago += ' ' + url + ' (Zugriff: ' + today + ').';

        // BibTeX
        let bibKey = 'WUB_' + idno.replace(/[^a-zA-Z0-9_]/g, '_');
        let bibtex = '@misc{' + bibKey + ',\n'
            + '  title     = {Nr. ' + idno + (dateDisplay ? ' (' + dateDisplay + ')' : '') + '},\n'
            + '  author    = {{Wiener Urkundenbuch Digital}},\n'
            + '  publisher = {Universität Wien},\n'
            + '  year      = {' + (dateDisplay.match(/\d{4}/) || ['s.d.'])[0] + '},\n'
            + '  howpublished = {\\url{' + url + '}},\n'
            + '  note      = {' + collection + '. Zugriff: ' + today + '}\n'
            + '}';

        popover.innerHTML = '<div class="cite-section">'
            + '<div class="cite-label">Chicago</div>'
            + '<div class="cite-text" id="cite-chicago">' + esc(chicago) + '</div>'
            + '<button class="cite-copy-btn" data-target="cite-chicago" title="Kopieren">&#x2398;</button>'
            + '</div>'
            + '<div class="cite-section">'
            + '<div class="cite-label">BibTeX</div>'
            + '<pre class="cite-text cite-bibtex" id="cite-bibtex">' + esc(bibtex) + '</pre>'
            + '<button class="cite-copy-btn" data-target="cite-bibtex" title="Kopieren">&#x2398;</button>'
            + '</div>';

        // Wire up copy buttons
        let copyBtns = popover.querySelectorAll('.cite-copy-btn');
        for (let i = 0; i < copyBtns.length; i++) {
            copyBtns[i].addEventListener('click', function(e) {
                e.stopPropagation();
                let targetId = this.getAttribute('data-target');
                let textEl = document.getElementById(targetId);
                if (!textEl) return;
                let text = textEl.textContent;
                navigator.clipboard.writeText(text).then(function() {
                    e.target.textContent = '\u2713';
                    setTimeout(function() { e.target.textContent = '\u2398'; }, 1500);
                });
            });
        }
    }


    /* ------------------------------------------------------------------
       Quality Panel — toggle findings display
       ------------------------------------------------------------------ */

    function initQualityPanel() {
        let btn = document.getElementById('quality-toggle');
        let panel = document.getElementById('quality-panel');
        if (!btn || !panel) return;

        btn.addEventListener('click', function() {
            let isVisible = !panel.classList.contains('hidden');
            if (isVisible) {
                panel.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            } else {
                panel.classList.remove('hidden');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    }


    /* ------------------------------------------------------------------
       Annotation Toggle — show/hide annotation layers with persistence
       ------------------------------------------------------------------ */

    function initAnnotationToggle() {
        let btn = document.getElementById('anno-toggle');
        let popover = document.getElementById('anno-toggle-popover');
        let body = document.querySelector('.doc-body');
        if (!btn || !popover || !body) return;

        let STORAGE_KEY = 'wub-anno-layers';
        let classMap = {
            entities: 'hide-entities',
            functions: 'hide-functions',
            attributes: 'hide-attributes',
            triggers: 'hide-triggers'
        };

        // Restore state from localStorage
        let saved = null;
        try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch(e) { /* ignore */ }
        if (saved && typeof saved === 'object') {
            Object.keys(classMap).forEach(function(layer) {
                let checkbox = popover.querySelector('[data-layer="' + layer + '"]');
                if (checkbox && saved[layer] === false) {
                    checkbox.checked = false;
                    body.classList.add(classMap[layer]);
                }
            });
        }

        // Checkbox change handler
        popover.addEventListener('change', function(e) {
            let checkbox = e.target;
            if (!checkbox.dataset || !checkbox.dataset.layer) return;
            let cls = classMap[checkbox.dataset.layer];
            if (!cls) return;
            if (checkbox.checked) {
                body.classList.remove(cls);
            } else {
                body.classList.add(cls);
            }
            saveState();
        });

        // Toggle all button
        let toggleAllBtn = document.getElementById('anno-toggle-all');
        if (toggleAllBtn) {
            toggleAllBtn.addEventListener('click', function() {
                let checkboxes = popover.querySelectorAll('[data-layer]');
                let allChecked = true;
                for (let i = 0; i < checkboxes.length; i++) {
                    if (!checkboxes[i].checked) { allChecked = false; break; }
                }
                let newState = !allChecked;
                for (let j = 0; j < checkboxes.length; j++) {
                    checkboxes[j].checked = newState;
                    let cls = classMap[checkboxes[j].dataset.layer];
                    if (cls) {
                        if (newState) {
                            body.classList.remove(cls);
                        } else {
                            body.classList.add(cls);
                        }
                    }
                }
                saveState();
            });
        }

        // Popover open/close (same pattern as cite popover)
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            let isVisible = !popover.classList.contains('hidden');
            popover.classList.toggle('hidden');
            btn.setAttribute('aria-expanded', isVisible ? 'false' : 'true');
        });

        document.addEventListener('click', function(e) {
            if (!popover.contains(e.target) && e.target !== btn) {
                popover.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                popover.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            }
        });

        function saveState() {
            let state = {};
            Object.keys(classMap).forEach(function(layer) {
                let cb = popover.querySelector('[data-layer="' + layer + '"]');
                state[layer] = cb ? cb.checked : true;
            });
            try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) { /* ignore */ }
        }
    }


    /* ------------------------------------------------------------------
       Initialise on document pages
       ------------------------------------------------------------------ */

    document.addEventListener('DOMContentLoaded', function() {
        if (document.querySelector('.doc-body')) {
            initFactoidView();
            initCitationHelper();
            initQualityPanel();
            initAnnotationToggle();
        }
    });

})();
