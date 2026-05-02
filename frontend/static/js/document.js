/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Document page: annotations view + citation helper + layer toggles
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;


    /* ------------------------------------------------------------------
       Annotationen — alle annotierten Layer aus dem TEI als strukturierte
       Tabellen unter Editionstext + Digitalisat. Permanenter Bereich,
       kein Toggle. Vier Sub-Tabellen:
         1. Personen / Organisationen / Orte (mit Rolle, Attribute, Event,
            Abschnitt)
         2. Ereignisse (Event-Refs + Section-Typ + Dispositiv-Verb)
         3. Dispositivformeln (Trigger-Strings)
         4. Editorische Ergaenzungen (.anno-add)
       ------------------------------------------------------------------ */

    function initAssertionsView() {
        let container = document.getElementById('factoid-view');
        if (!container) return;
        buildAnnotationsTables(container);
    }

    function _entityType(el) {
        return el.classList.contains('anno-person') ? 'Person' :
               el.classList.contains('anno-org') ? 'Organisation' :
               el.classList.contains('anno-place') ? 'Ort' : '';
    }

    function _entityName(el) {
        let title = el.getAttribute('title') || el.getAttribute('data-title') || '';
        if (title) {
            let stripped = title.replace(/\s*\[.*\]\s*$/, '').trim();
            if (stripped) return stripped;
        }
        return el.textContent.trim();
    }

    function _sectionTypeFor(el) {
        let sec = el.closest('section.tei-abstract, section.tei-seal, section.tei-nota, section.tei-entry');
        if (!sec) return '';
        if (sec.classList.contains('tei-abstract')) return 'Regest';
        if (sec.classList.contains('tei-seal')) return 'Siegelbeschreibung';
        if (sec.classList.contains('tei-nota')) return 'Indorsat / Nota';
        if (sec.classList.contains('tei-entry')) return 'Eintrag';
        return '';
    }

    function buildAnnotationsTables(container) {
        let body = document.querySelector('.doc-body');
        let bodyEl = container.querySelector('.annotations-body');
        let summaryEl = container.querySelector('.annotations-summary');
        if (!body || !bodyEl) return;

        let DASH = '–';
        let ROLE_LABELS = {
            'issuer': 'Aussteller*in',
            'recipient': 'Empfänger*in',
            'witness': 'Zeug*in',
            'other': 'Sonstige'
        };

        // ---- 1. Entitaeten: zuerst innerhalb von Funktionsrollen-Spans
        //         (mit Rolle), dann standalone (ohne Rolle).
        let entities = [];
        let seen = new Set();
        let fnSpans = body.querySelectorAll('.anno-fn');
        for (let i = 0; i < fnSpans.length; i++) {
            let fnSpan = fnSpans[i];
            let role = fnSpan.getAttribute('data-role') || '';
            let roleLabel = ROLE_LABELS[role] || role || DASH;
            let nested = fnSpan.querySelectorAll('.anno-person, .anno-org, .anno-place');
            for (let j = 0; j < nested.length; j++) {
                let entity = nested[j];
                let type = _entityType(entity);
                if (!type) continue;
                let attrs = [];
                let attrSpans = entity.querySelectorAll('.anno-attr');
                for (let k = 0; k < attrSpans.length; k++) {
                    attrs.push(attrSpans[k].textContent.trim());
                }
                let eventSpan = entity.closest('.anno-event');
                entities.push({
                    name: _entityName(entity),
                    type: type,
                    role: roleLabel,
                    attributes: attrs.join(', '),
                    event: eventSpan ? (eventSpan.getAttribute('data-ref') || '') : '',
                    ref: entity.getAttribute('data-ref') || '',
                    section: _sectionTypeFor(entity)
                });
                seen.add(entity);
            }
        }
        let standalone = body.querySelectorAll('.anno-person, .anno-org, .anno-place');
        for (let m = 0; m < standalone.length; m++) {
            let el = standalone[m];
            if (seen.has(el)) continue;
            let elType = _entityType(el);
            if (!elType) continue;
            let elAttrs = [];
            let elAttrSpans = el.querySelectorAll('.anno-attr');
            for (let n = 0; n < elAttrSpans.length; n++) {
                elAttrs.push(elAttrSpans[n].textContent.trim());
            }
            let elEvent = el.closest('.anno-event');
            entities.push({
                name: _entityName(el),
                type: elType,
                role: DASH,
                attributes: elAttrs.join(', '),
                event: elEvent ? (elEvent.getAttribute('data-ref') || '') : '',
                ref: el.getAttribute('data-ref') || '',
                section: _sectionTypeFor(el)
            });
        }

        // ---- 2. Ereignisse: pro Event-Span eine Zeile (deduped per ref).
        let events = [];
        let eventSeen = new Set();
        let eventSpans = body.querySelectorAll('.anno-event');
        for (let e = 0; e < eventSpans.length; e++) {
            let ev = eventSpans[e];
            let ref = ev.getAttribute('data-ref') || '';
            if (eventSeen.has(ref)) continue;
            eventSeen.add(ref);
            let trigger = ev.querySelector('.anno-trigger-disp, .anno-trigger');
            events.push({
                ref: ref,
                section: _sectionTypeFor(ev),
                trigger: trigger ? trigger.textContent.trim() : ''
            });
        }

        // ---- 3. Dispositivformeln / Trigger-Strings.
        let triggers = [];
        let triggerSpans = body.querySelectorAll('.anno-trigger');
        for (let t = 0; t < triggerSpans.length; t++) {
            let tr = triggerSpans[t];
            let kind = tr.classList.contains('anno-trigger-disp') ? 'Dispositiv' :
                       tr.classList.contains('anno-trigger-fn') ? 'Funktionsrolle' :
                       'Trigger';
            let evSpan = tr.closest('.anno-event');
            triggers.push({
                text: tr.textContent.trim(),
                kind: kind,
                event: evSpan ? (evSpan.getAttribute('data-ref') || '') : '',
                section: _sectionTypeFor(tr)
            });
        }

        // ---- 4. Editorische Ergaenzungen (.anno-add).
        let adds = [];
        let addSpans = body.querySelectorAll('.anno-add');
        for (let a = 0; a < addSpans.length; a++) {
            let ad = addSpans[a];
            adds.push({
                text: ad.textContent.trim(),
                section: _sectionTypeFor(ad)
            });
        }

        // ---- Summary in der Header-Pille.
        let summaryParts = [];
        if (entities.length) {
            summaryParts.push(entities.length + ' Entität' + (entities.length !== 1 ? 'en' : ''));
        }
        if (events.length) {
            summaryParts.push(events.length + ' Ereignis' + (events.length !== 1 ? 'se' : ''));
        }
        if (triggers.length) {
            summaryParts.push(triggers.length + ' Dispositivformel' + (triggers.length !== 1 ? 'n' : ''));
        }
        if (adds.length) {
            summaryParts.push(adds.length + ' Ergänzung' + (adds.length !== 1 ? 'en' : ''));
        }
        if (summaryEl) summaryEl.textContent = summaryParts.join('  ·  ');

        if (!entities.length && !events.length && !triggers.length && !adds.length) {
            bodyEl.innerHTML = '<p class="annotations-empty">Keine Annotationen in dieser Quelle.</p>';
            return;
        }

        let html = '';

        // Provenance-Tooltip pro Zeile: jede Annotation erhaelt
        // data-tip-title + data-tip-body, sodass tooltips.js den
        // einheitlichen Daten-Tooltip zeigt. Body enthaelt das TEI-
        // Markup als Schnipsel + Abschnitts-Kontext, damit klar wird,
        // welches Quell-Element die Zeile abbildet.
        function entityTipBody(f) {
            let parts = [];
            let rsAttrs = ['type="' + f.type.toLowerCase() + '"'];
            if (f.ref) rsAttrs.push('ref="#' + f.ref + '"');
            parts.push('<rs ' + rsAttrs.join(' ') + '>' + f.name + '</rs>');
            if (f.role && f.role !== DASH) parts.push('Rolle: ' + f.role);
            if (f.attributes) parts.push('Attribute: ' + f.attributes);
            if (f.event) parts.push('in Event: ' + f.event);
            if (f.section) parts.push('Abschnitt: ' + f.section);
            return parts.join(' · ');
        }

        function eventTipBody(ev) {
            let parts = ['<rs type="event" xml:id="' + ev.ref + '">'];
            if (ev.trigger) parts.push('Dispositiv-Verb: ' + ev.trigger);
            if (ev.section) parts.push('Abschnitt: ' + ev.section);
            return parts.join(' · ');
        }

        function triggerTipBody(tr) {
            let parts = ['<triggerstring n="' + tr.kind.toLowerCase() + '">' + tr.text + '</triggerstring>'];
            if (tr.event) parts.push('in Event: ' + tr.event);
            if (tr.section) parts.push('Abschnitt: ' + tr.section);
            return parts.join(' · ');
        }

        function addTipBody(ad) {
            let parts = ['<add>' + ad.text + '</add>'];
            if (ad.section) parts.push('Abschnitt: ' + ad.section);
            return parts.join(' · ');
        }

        function escAttr(s) {
            // EdCore.esc liefert &lt;/&gt;/&amp;, escapt aber nicht das
            // doppelte Anfuehrungszeichen — fuer Attribut-Werte muessen
            // " ebenfalls escapt sein, sonst beendet das erste " im
            // Body das Attribut vorzeitig.
            return esc(s).replace(/"/g, '&quot;');
        }
        function tipAttrs(title, body) {
            return ' data-tip-title="' + escAttr(title) + '" data-tip-body="' + escAttr(body) + '"';
        }

        if (entities.length) {
            // Profil-Verlinkung: Personen-Refs (pe__) bekommen einen Link
            // auf register/persons/<id>.html. Orgs/Orte haben (noch) keine
            // Profilseiten, deshalb hier nur der Klartext-Name.
            let rootPath = (document.body && document.body.dataset.rootPath) || '..';
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Personen, Organisationen, Orte</h3>'
                + '<table class="annotations-table"><thead><tr>'
                + '<th>Entität</th><th>Typ</th><th>Rolle</th><th>Attribute</th><th>Abschnitt</th><th>Event</th><th>ID</th>'
                + '</tr></thead><tbody>';
            for (let p = 0; p < entities.length; p++) {
                let f = entities[p];
                let nameCell;
                if (f.type === 'Person' && f.ref && f.ref.indexOf('pe__') === 0) {
                    nameCell = '<a class="anno-table-link" href="'
                        + esc(rootPath) + '/register/persons/' + esc(f.ref) + '.html">'
                        + esc(f.name) + '</a>';
                } else {
                    nameCell = esc(f.name);
                }
                html += '<tr' + tipAttrs(f.type + '-Annotation', entityTipBody(f)) + '>'
                    + '<td>' + nameCell + '</td>'
                    + '<td><span class="annotation-type annotation-type-' + f.type.toLowerCase() + '">' + esc(f.type) + '</span></td>'
                    + '<td>' + esc(f.role) + '</td>'
                    + '<td>' + esc(f.attributes || DASH) + '</td>'
                    + '<td>' + esc(f.section || DASH) + '</td>'
                    + '<td><span class="cell-id">' + esc(f.event || DASH) + '</span></td>'
                    + '<td><span class="cell-id">' + esc(f.ref) + '</span></td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        if (events.length) {
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Ereignisse</h3>'
                + '<table class="annotations-table"><thead><tr>'
                + '<th>Abschnitt</th><th>Dispositiv-Verb</th><th>ID</th>'
                + '</tr></thead><tbody>';
            for (let e2 = 0; e2 < events.length; e2++) {
                let ev = events[e2];
                html += '<tr' + tipAttrs('Ereignis-Annotation', eventTipBody(ev)) + '>'
                    + '<td>' + esc(ev.section || DASH) + '</td>'
                    + '<td>' + esc(ev.trigger || DASH) + '</td>'
                    + '<td><span class="cell-id">' + esc(ev.ref) + '</span></td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        if (triggers.length) {
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Dispositivformeln</h3>'
                + '<table class="annotations-table"><thead><tr>'
                + '<th>Text</th><th>Art</th><th>Abschnitt</th><th>Event</th>'
                + '</tr></thead><tbody>';
            for (let t2 = 0; t2 < triggers.length; t2++) {
                let tr2 = triggers[t2];
                html += '<tr' + tipAttrs('Dispositivformel', triggerTipBody(tr2)) + '>'
                    + '<td>' + esc(tr2.text) + '</td>'
                    + '<td>' + esc(tr2.kind) + '</td>'
                    + '<td>' + esc(tr2.section || DASH) + '</td>'
                    + '<td><span class="cell-id">' + esc(tr2.event || DASH) + '</span></td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        if (adds.length) {
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Editorische Ergänzungen</h3>'
                + '<table class="annotations-table"><thead><tr>'
                + '<th>Text</th><th>Abschnitt</th>'
                + '</tr></thead><tbody>';
            for (let a2 = 0; a2 < adds.length; a2++) {
                let ad2 = adds[a2];
                html += '<tr' + tipAttrs('Editorische Ergänzung', addTipBody(ad2)) + '>'
                    + '<td>' + esc(ad2.text) + '</td>'
                    + '<td>' + esc(ad2.section || DASH) + '</td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        bodyEl.innerHTML = html;
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
                    e.target.textContent = '✓';
                    setTimeout(function() { e.target.textContent = '⎘'; }, 1500);
                });
            });
        }
    }


    /* ------------------------------------------------------------------
       Annotation Toggle — Detail-Legende ist die Steuerung. Klick auf
       eine Gruppe (Entitaeten/Funktionsrollen/Attribute/Dispositivformel)
       schaltet ihre Layer-Klasse auf `.doc-body` um. Status persistiert
       per localStorage; Klassen folgen dem alten classMap-Schema, damit
       die existenten CSS-Selektoren (.doc-body.hide-entities .anno-...)
       weiter greifen.
       ------------------------------------------------------------------ */

    function initAnnotationToggle() {
        let body = document.querySelector('.doc-body');
        let toggles = document.querySelectorAll('.legend-toggle[data-layer]');
        if (!body || !toggles.length) return;

        let STORAGE_KEY = 'wub-anno-layers';
        let classMap = {
            entities: 'hide-entities',
            functions: 'hide-functions',
            attributes: 'hide-attributes',
            triggers: 'hide-triggers'
        };

        let saved = null;
        try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch(e) { /* ignore */ }
        if (saved && typeof saved === 'object') {
            toggles.forEach(function(t) {
                let layer = t.dataset.layer;
                let cls = classMap[layer];
                if (!cls) return;
                if (saved[layer] === false) {
                    t.setAttribute('aria-pressed', 'false');
                    body.classList.add(cls);
                }
            });
        }

        toggles.forEach(function(t) {
            t.addEventListener('click', function() {
                let layer = t.dataset.layer;
                let cls = classMap[layer];
                if (!cls) return;
                let isOn = t.getAttribute('aria-pressed') !== 'false';
                let newOn = !isOn;
                t.setAttribute('aria-pressed', newOn ? 'true' : 'false');
                if (newOn) {
                    body.classList.remove(cls);
                } else {
                    body.classList.add(cls);
                }
                saveState();
            });
        });

        function saveState() {
            let state = {};
            toggles.forEach(function(t) {
                state[t.dataset.layer] = t.getAttribute('aria-pressed') !== 'false';
            });
            try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) { /* ignore */ }
        }
    }


    /* ------------------------------------------------------------------
       Initialise on document pages
       ------------------------------------------------------------------ */

    document.addEventListener('DOMContentLoaded', function() {
        if (document.querySelector('.doc-body')) {
            initAssertionsView();
            initCitationHelper();
            initAnnotationToggle();
        }
    });

})();
