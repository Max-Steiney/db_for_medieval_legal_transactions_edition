(function() {
    'use strict';

    let esc = EdCore.esc;

    // ?dev=1 sets .dev-mode on <html>, revealing all .dev-only elements.
    if (window.location && window.location.search.indexOf('dev=1') >= 0) {
        document.documentElement.classList.add('dev-mode');
    }


    // Renders all annotated TEI layers as structured tables: entities,
    // events, dispositive formulas, and editorial additions.
    function initAssertionsView() {
        let container = document.getElementById('annotations-view');
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
        let tabsEl = container.querySelector('.annotations-tabs');
        if (!body || !bodyEl) return;

        let DASH = '–';
        // Role labels are embedded by the build into <script id="role-labels">;
        // the fallback covers cases where that element is absent (e.g. in tests).
        let ROLE_LABELS = (function() {
            try {
                let el = document.getElementById('role-labels');
                if (el) return JSON.parse(el.textContent);
            } catch (e) {}
            return {
                'issuer': 'Aussteller:in',
                'recipient': 'Empfänger:in',
                'witness': 'Zeug:in / Siegler:in',
                'other': 'Sonstige'
            };
        })();

        // Entities: first those inside function-role spans (with role),
        // then standalone ones (without role).
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
                    resolved: (entity.getAttribute('data-hint') || '').trim(),
                    section: _sectionTypeFor(entity),
                    sex: entity.getAttribute('data-sex') || ''
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
                resolved: (el.getAttribute('data-hint') || '').trim(),
                section: _sectionTypeFor(el),
                sex: el.getAttribute('data-sex') || ''
            });
        }

        // Events: one row per event span (deduped by ref). Nested events
        // do not form their own group; their entities collapse into the
        // parent event's group.
        let events = [];
        let eventSeen = new Set();
        let eventSpans = body.querySelectorAll('.anno-event');

        // Maps each ref to the outermost anno-event in the hierarchy, so
        // entity grouping can collapse nested events into their parent group.
        let topLevelByRef = {};
        for (let e = 0; e < eventSpans.length; e++) {
            let span = eventSpans[e];
            let ref = span.getAttribute('data-ref') || '';
            if (!ref || topLevelByRef[ref]) continue;
            let topRef = ref;
            let walker = span.parentElement;
            while (walker && walker !== body) {
                if (walker.classList && walker.classList.contains('anno-event')) {
                    let pref = walker.getAttribute('data-ref') || '';
                    if (pref) topRef = pref;
                }
                walker = walker.parentElement;
            }
            topLevelByRef[ref] = topRef;
        }

        for (let e = 0; e < eventSpans.length; e++) {
            let ev = eventSpans[e];
            let ref = ev.getAttribute('data-ref') || '';
            if (eventSeen.has(ref)) continue;
            eventSeen.add(ref);
            let isNested = topLevelByRef[ref] !== ref;
            if (isNested) continue; // nested events do not form their own group
            let trigger = ev.querySelector('.anno-trigger-disp, .anno-trigger');
            events.push({
                ref: ref,
                section: _sectionTypeFor(ev),
                trigger: trigger ? trigger.textContent.trim() : ''
            });
        }

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

        let adds = [];
        let addSpans = body.querySelectorAll('.anno-add');
        for (let a = 0; a < addSpans.length; a++) {
            let ad = addSpans[a];
            adds.push({
                text: ad.textContent.trim(),
                section: _sectionTypeFor(ad)
            });
        }

        if (!entities.length && !events.length && !triggers.length && !adds.length) {
            bodyEl.innerHTML = '<p class="annotations-empty">Keine Annotationen in dieser Quelle.</p>';
            return;
        }

        // Per-row hover hint picked up by hint.js. Body is plain structured
        // text so no raw TEI markup leaks into the tooltip layer.
        function entityTipBody(f) {
            let parts = [f.name];
            if (f.role && f.role !== DASH) parts.push('Rolle: ' + f.role);
            if (f.attributes) parts.push('Attribute: ' + f.attributes);
            if (f.section) parts.push('Abschnitt: ' + f.section);
            return parts.join(' · ');
        }

        function eventTipBody(ev) {
            let parts = [];
            if (ev.trigger) parts.push('Dispositiv-Verb: ' + ev.trigger);
            if (ev.section) parts.push('Abschnitt: ' + ev.section);
            if (!parts.length) parts.push('Rechtsgeschäft');
            return parts.join(' · ');
        }

        function triggerTipBody(tr) {
            let parts = [tr.text, 'Art: ' + tr.kind];
            if (tr.event) parts.push('Event: ' + tr.event);
            if (tr.section) parts.push('Abschnitt: ' + tr.section);
            return parts.join(' · ');
        }

        function addTipBody(ad) {
            let parts = [ad.text];
            if (ad.section) parts.push('Abschnitt: ' + ad.section);
            return parts.join(' · ');
        }

        function escAttr(s) {
            // EdCore.esc does not escape the double quote, which must also
            // be escaped in attribute values to avoid closing the attribute.
            return esc(s).replace(/"/g, '&quot;');
        }
        function tipAttrs(type, body) {
            return ' data-hint="' + escAttr(body) + '" data-hint-type="' + escAttr(type) + '"';
        }

        // data-sort-value drives the column sorter. For link or badge cells
        // it holds the plain text so sorting compares names, not markup.
        function sortAttr(value) {
            return ' data-sort-value="' + escAttr(value) + '"';
        }

        function rolePill(role) {
            if (!role || role === DASH) {
                return '<span class="role-pill role-pill--none">' + DASH + '</span>';
            }
            let mod = '';
            if (role === 'Aussteller:in') mod = ' role-pill--issuer';
            else if (role === 'Empfänger:in') mod = ' role-pill--recipient';
            else if (role === 'Zeug:in') mod = ' role-pill--witness';
            else if (role === 'Sonstige') mod = ' role-pill--other';
            return '<span class="role-pill' + mod + '">' + esc(role) + '</span>';
        }

        function attrTags(arr) {
            if (!arr || !arr.length) return '<span class="attr-empty">' + DASH + '</span>';
            let out = '';
            for (let i = 0; i < arr.length; i++) {
                out += '<span class="attr-tag">' + esc(arr[i]) + '</span>';
            }
            return out;
        }

        // Dispositive preview for the event group header: first and last
        // formula with an ellipsis between, or fewer when there are one or two.
        let dispTriggersByEvent = {};
        for (let t = 0; t < triggers.length; t++) {
            if (triggers[t].kind !== 'Dispositiv') continue;
            let evRef = triggers[t].event || '';
            if (!evRef) continue;
            let topRef = topLevelByRef[evRef] || evRef;
            if (!dispTriggersByEvent[topRef]) dispTriggersByEvent[topRef] = [];
            dispTriggersByEvent[topRef].push(triggers[t].text);
        }
        function dispPreview(evRef) {
            let arr = dispTriggersByEvent[evRef] || [];
            if (arr.length === 0) return '';
            if (arr.length === 1) return arr[0];
            if (arr.length === 2) return arr[0] + ' … ' + arr[1];
            return arr[0] + ' … ' + arr[arr.length - 1];
        }

        let panels = [];
        // Default active panel is the first non-devOnly one, so a hidden
        // panel is never marked active without the dev switch. Set below.
        let defaultActiveKey = '';

        if (entities.length) {
            // Group entities by event so it is clear which belong to the
            // same legal transaction. Sorting is group-aware (see
            // _attachAnnotationSorting): rows sort within each group, group
            // order stays fixed in document order.
            let rootPath = (document.body && document.body.dataset.rootPath) || '..';
            let showIds = (document.body && document.body.getAttribute('data-audience') === 'intern')
                || document.documentElement.classList.contains('dev-mode');

            let entityGroups = {};
            let entityOrder = [];
            for (let p = 0; p < entities.length; p++) {
                let rawKey = entities[p].event || '';
                let key = rawKey && topLevelByRef[rawKey] ? topLevelByRef[rawKey] : rawKey;
                if (!entityGroups[key]) { entityGroups[key] = []; entityOrder.push(key); }
                entityGroups[key].push(entities[p]);
            }
            let eventByRef = {};
            for (let i = 0; i < events.length; i++) eventByRef[events[i].ref] = events[i];

            let renderedGroups = {};
            let orderedKeys = [];
            for (let e2 = 0; e2 < events.length; e2++) {
                let r = events[e2].ref;
                if (entityGroups[r] && !renderedGroups[r]) {
                    orderedKeys.push(r); renderedGroups[r] = true;
                }
            }
            for (let k = 0; k < entityOrder.length; k++) {
                let key = entityOrder[k];
                if (!renderedGroups[key]) { orderedKeys.push(key); renderedGroups[key] = true; }
            }

            function entityTypeMarker(type) {
                let mod = type === 'Person' ? 'person'
                        : type === 'Organisation' ? 'organisation'
                        : type === 'Ort' ? 'place' : 'other';
                let label = type;
                return '<span class="anno-type-dot anno-type-dot--' + mod
                    + '" aria-label="' + esc(label) + '" data-hint="' + esc(label) + '"></span>';
            }

            function entityRow(f) {
                // Display name: resolved identity first, source wording in
                // parentheses after it when the two differ.
                let hasResolved = f.resolved && f.resolved !== f.name;
                let primary = hasResolved ? f.resolved : f.name;
                let primaryHtml;
                if (f.type === 'Person' && f.ref && f.ref.indexOf('pe__') === 0) {
                    primaryHtml = '<a class="anno-table-link" href="'
                        + esc(rootPath) + '/register/persons/' + esc(f.ref) + '.html">'
                        + esc(primary) + '</a>';
                } else if (f.type === 'Organisation' && f.ref && f.ref.indexOf('org__') === 0) {
                    primaryHtml = '<a class="anno-table-link" href="'
                        + esc(rootPath) + '/register/orgs/' + esc(f.ref) + '.html">'
                        + esc(primary) + '</a>';
                } else {
                    primaryHtml = esc(primary);
                }
                let nameCell = entityTypeMarker(f.type) + primaryHtml;
                if (hasResolved) {
                    nameCell += ' <span class="anno-wording">(' + esc(f.name) + ')</span>';
                }
                if (showIds && f.ref) {
                    nameCell += '<span class="anno-ref">' + esc(f.ref) + '</span>';
                }

                // Sex as the short m/w form used in register and basket; empty for non-persons.
                let sexCell = '';
                let sexSort = '';
                if (f.type === 'Person') {
                    if (f.sex === 'm') { sexCell = '<span class="anno-sex">m</span>'; sexSort = 'm'; }
                    else if (f.sex === 'f') { sexCell = '<span class="anno-sex">w</span>'; sexSort = 'w'; }
                    else { sexCell = '<span class="anno-sex anno-sex--unknown">' + DASH + '</span>'; sexSort = 'z'; }
                }
                let attrArr = f.attributes ? f.attributes.split(/, /).filter(Boolean) : [];
                return '<tr' + tipAttrs(f.type + '-Annotation', entityTipBody(f)) + '>'
                    + '<td' + sortAttr(primary) + '>' + nameCell + '</td>'
                    + '<td' + sortAttr(f.role) + '>' + rolePill(f.role) + '</td>'
                    + '<td' + sortAttr(f.attributes) + '>' + attrTags(attrArr) + '</td>'
                    + '<td' + sortAttr(sexSort) + '>' + sexCell + '</td>'
                    + '</tr>';
            }

            let entHtml = '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="name" data-hint="Wortlaut, mit dem die Person, Organisation oder der Ort in der Quelle erscheint.">Genannt als</th>'
                + '<th scope="col" data-sort="role" data-hint="Funktion im Rechtsgeschäft: Aussteller:in, Empfänger:in, Zeug:in oder Sonstige.">Funktionsrolle</th>'
                + '<th scope="col" data-sort="attributes" data-hint="Zusatzangaben zur Entität: Beruf, Titel, Verwandtschaftsbezug, als verstorben genannt etc.">Attribute</th>'
                + '<th scope="col" data-sort="sex" data-hint="Geschlecht laut Personenregister (weiblich oder männlich). Nur bei Personen belegt.">Geschlecht</th>'
                + '</tr></thead><tbody>';
            for (let g = 0; g < orderedKeys.length; g++) {
                let key = orderedKeys[g];
                let rows = entityGroups[key];
                let label;
                if (!key) {
                    label = '<span class="annotations-group-label">Ohne Rechtsgeschäft</span>';
                } else {
                    let preview = dispPreview(key);
                    if (!preview) {
                        let ev = eventByRef[key];
                        preview = ev && ev.trigger ? ev.trigger : '';
                    }
                    let count = rows.length;
                    let countLabel = count + ' Genannte' + (count !== 1 ? '' : 'r');
                    label = '<div class="annotations-group-head">'
                        + '<span class="annotations-group-count">' + esc(countLabel) + '</span>'
                        + '</div>';
                    if (preview) {
                        label += '<div class="annotations-group-quote"><q class="annotations-group-source">' + esc(preview) + '</q></div>';
                    }
                }
                entHtml += '<tr class="annotations-group-row"><th colspan="4" scope="rowgroup">'
                    + label + '</th></tr>';
                for (let r2 = 0; r2 < rows.length; r2++) {
                    entHtml += entityRow(rows[r2]);
                }
            }
            entHtml += '</tbody></table>';
            panels.push({
                key: 'entities',
                label: 'Entitäten',
                count: entities.length,
                hint: 'Personen, Organisationen und Orte aus der TEI-Auszeichnung, gruppiert nach Rechtsgeschäft.',
                html: entHtml
            });
        }

        if (triggers.length) {
            let trHtml = '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="text" data-hint="Verb-Wortlaut aus der Quelle, der das Rechtsgeschäft oder eine Funktionsrolle markiert.">Text</th>'
                + '<th scope="col" data-sort="kind" data-hint="Dispositiv (markiert das Rechtsgeschäft) oder Funktionsrolle (markiert eine Rolle).">Art</th>'
                + '<th scope="col" data-sort="section" data-hint="Strukturteil der Quelle, in dem die Formel steht.">Abschnitt</th>'
                + '<th scope="col" data-sort="event" data-hint="Rechtsgeschäft, zu dem die Formel gehört.">Rechtsgeschäft</th>'
                + '</tr></thead><tbody>';
            for (let t2 = 0; t2 < triggers.length; t2++) {
                let tr2 = triggers[t2];
                let evRef = tr2.event || '';
                let evCell;
                if (evRef) {
                    let topRef = topLevelByRef[evRef] || evRef;
                    let preview = dispPreview(topRef);
                    let display = preview || topRef;
                    evCell = '<span class="annotations-group-source">' + esc(display) + '</span>';
                } else {
                    evCell = '<span class="cell-id">' + DASH + '</span>';
                }
                trHtml += '<tr' + tipAttrs('Dispositivformel', triggerTipBody(tr2)) + '>'
                    + '<td' + sortAttr(tr2.text) + '>' + esc(tr2.text) + '</td>'
                    + '<td' + sortAttr(tr2.kind) + '>' + esc(tr2.kind) + '</td>'
                    + '<td' + sortAttr(tr2.section) + '>' + esc(tr2.section || DASH) + '</td>'
                    + '<td' + sortAttr(evRef) + '>' + evCell + '</td>'
                    + '</tr>';
            }
            trHtml += '</tbody></table>';
            panels.push({
                key: 'triggers',
                label: 'Dispositivformeln',
                count: triggers.length,
                hint: 'Verb-Spannen, die im TEI das Rechtsgeschäft oder eine Funktionsrolle anzeigen.',
                html: trHtml,
                devOnly: true
            });
        }

        if (adds.length) {
            let adHtml = '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="text" data-hint="Sinngemäße Ergänzung der Editorin im Quellentext.">Text</th>'
                + '<th scope="col" data-sort="section" data-hint="Strukturteil der Quelle, in dem die Ergänzung steht.">Abschnitt</th>'
                + '</tr></thead><tbody>';
            for (let a2 = 0; a2 < adds.length; a2++) {
                let ad2 = adds[a2];
                adHtml += '<tr' + tipAttrs('Editorische Ergänzung', addTipBody(ad2)) + '>'
                    + '<td' + sortAttr(ad2.text) + '>' + esc(ad2.text) + '</td>'
                    + '<td' + sortAttr(ad2.section) + '>' + esc(ad2.section || DASH) + '</td>'
                    + '</tr>';
            }
            adHtml += '</tbody></table>';
            panels.push({
                key: 'adds',
                label: 'Editorische Ergänzungen',
                count: adds.length,
                hint: 'Vom Editor sinngemäß in den Quellentext eingefügte Wörter.',
                html: adHtml
            });
        }

        for (let i = 0; i < panels.length; i++) {
            if (!panels[i].devOnly) { defaultActiveKey = panels[i].key; break; }
        }
        if (!defaultActiveKey && panels.length) defaultActiveKey = panels[0].key;

        // Only render the tab strip with more than one visible panel.
        // Dev-only panels count only when .dev-mode is active.
        let isDevMode = document.documentElement.classList.contains('dev-mode');
        let visiblePanelCount = panels.filter(function(p) {
            return !p.devOnly || isDevMode;
        }).length;

        let tabsHtml = '';
        if (tabsEl && visiblePanelCount > 1) {
            for (let i = 0; i < panels.length; i++) {
                let p = panels[i];
                let active = p.key === defaultActiveKey;
                let cls = 'annotations-tab' + (active ? ' is-active' : '') + (p.devOnly ? ' dev-only' : '');
                tabsHtml += '<button type="button" class="' + cls + '"'
                    + ' role="tab"'
                    + ' aria-selected="' + (active ? 'true' : 'false') + '"'
                    + ' aria-controls="annotations-panel-' + esc(p.key) + '"'
                    + ' data-tab-target="' + esc(p.key) + '"'
                    + ' data-hint="' + escAttr(p.hint) + '">'
                    + '<span class="annotations-tab-label">' + esc(p.label) + '</span>'
                    + '<span class="annotations-tab-count">' + p.count + '</span>'
                    + '</button>';
            }
        }
        if (tabsEl) tabsEl.innerHTML = tabsHtml;

        let html = '';
        for (let i = 0; i < panels.length; i++) {
            let p = panels[i];
            let hidden = p.key === defaultActiveKey ? '' : ' hidden';
            let cls = 'annotation-group' + (p.devOnly ? ' dev-only' : '');
            html += '<section class="' + cls + '" id="annotations-panel-' + esc(p.key) + '"'
                + ' data-tab-panel="' + esc(p.key) + '"'
                + ' role="tabpanel"' + hidden + '>'
                + p.html
                + '</section>';
        }
        bodyEl.innerHTML = html;

        // Tab switch: only one panel visible, the others hidden; active tab
        // highlighted and aria-selected kept consistent.
        if (tabsEl && visiblePanelCount > 1) {
            let tabButtons = tabsEl.querySelectorAll('.annotations-tab');
            tabButtons.forEach(function(btn) {
                btn.addEventListener('click', function() {
                    let target = btn.getAttribute('data-tab-target');
                    tabButtons.forEach(function(b) {
                        let isActive = b.getAttribute('data-tab-target') === target;
                        b.classList.toggle('is-active', isActive);
                        b.setAttribute('aria-selected', isActive ? 'true' : 'false');
                    });
                    let allPanels = bodyEl.querySelectorAll('[data-tab-panel]');
                    allPanels.forEach(function(panel) {
                        if (panel.getAttribute('data-tab-panel') === target) {
                            panel.removeAttribute('hidden');
                        } else {
                            panel.setAttribute('hidden', '');
                        }
                    });
                });
            });
        }


        // Attach column sorting to every freshly built table.
        let sortTables = bodyEl.querySelectorAll('table.sortable-table');
        for (let s = 0; s < sortTables.length; s++) {
            _attachAnnotationSorting(sortTables[s]);
        }
    }

    // Sorting for the annotation sub-tables. A slim local variant of
    // profile.js setupSortableTable, which is not loaded on document pages
    // and whose init runs before these tables are built.
    function _attachAnnotationSorting(table) {
        let allHeaders = Array.prototype.slice.call(table.querySelectorAll('thead th'));
        let sortHeaders = allHeaders.filter(function (h) { return h.hasAttribute('data-sort'); });
        if (!sortHeaders.length) return;
        let tbody = table.querySelector('tbody');
        if (!tbody) return;

        let indexByKey = {};
        sortHeaders.forEach(function (h) {
            indexByKey[h.getAttribute('data-sort')] = allHeaders.indexOf(h);
        });

        let originalOrder = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
        let state = { key: null, dir: 1 };

        function cellValue(tr, colIndex) {
            let td = tr.children[colIndex];
            if (!td) return '';
            let v = td.getAttribute('data-sort-value');
            return v !== null ? v : td.textContent.trim();
        }

        function applySort() {
            let frag = document.createDocumentFragment();
            if (state.key === null) {
                originalOrder.forEach(function (tr) { frag.appendChild(tr); });
                tbody.appendChild(frag);
                return;
            }
            let colIndex = indexByKey[state.key];
            if (colIndex === undefined || colIndex < 0) return;

            // Group-aware sort: tbody is segmented at the
            // .annotations-group-row boundaries; each group sorts within
            // itself, group order stays fixed. Tables without group headers
            // fall back to a single implicit group (global sort).
            let allRows = Array.prototype.slice.call(tbody.children);
            let segments = [];
            let current = { header: null, dataRows: [] };
            segments.push(current);
            for (let i = 0; i < allRows.length; i++) {
                let row = allRows[i];
                if (row.classList && row.classList.contains('annotations-group-row')) {
                    current = { header: row, dataRows: [] };
                    segments.push(current);
                } else {
                    current.dataRows.push(row);
                }
            }
            segments.forEach(function (seg) {
                seg.dataRows.sort(function (a, b) {
                    return EdCore.compareValues(
                        cellValue(a, colIndex), cellValue(b, colIndex), state.dir);
                });
            });
            segments.forEach(function (seg) {
                if (seg.header) frag.appendChild(seg.header);
                seg.dataRows.forEach(function (tr) { frag.appendChild(tr); });
            });
            tbody.appendChild(frag);
        }

        sortHeaders.forEach(function (th) {
            th.addEventListener('click', function () {
                let key = th.getAttribute('data-sort');
                if (state.key === key) {
                    if (state.dir === 1) {
                        state.dir = -1;
                    } else {
                        state.key = null;
                        state.dir = 1;
                    }
                } else {
                    state.key = key;
                    state.dir = 1;
                }
                sortHeaders.forEach(function (h) {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                    h.setAttribute('aria-sort', 'none');
                });
                if (state.key !== null) {
                    th.classList.add(state.dir === 1 ? 'sorted-asc' : 'sorted-desc');
                    th.setAttribute('aria-sort', state.dir === 1 ? 'ascending' : 'descending');
                }
                applySort();
            });
            th.setAttribute('aria-sort', 'none');
        });
    }


    // Citation helper: formatted citation with copy-to-clipboard.
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
        chicago += ' In: Stadt und Gemeinschaft Wien: Datenbank zu mittelalterlichen Wiener Rechtsgeschäften, hg. von Korbinian Grünwald. Universität Wien.';
        chicago += ' ' + url + ' (Zugriff: ' + today + ').';

        // BibTeX
        let bibKey = 'SuGW_' + idno.replace(/[^a-zA-Z0-9_]/g, '_');
        let bibtex = '@misc{' + bibKey + ',\n'
            + '  title     = {Nr. ' + idno + (dateDisplay ? ' (' + dateDisplay + ')' : '') + '},\n'
            + '  author    = {{Stadt und Gemeinschaft Wien}},\n'
            + '  editor    = {Grünwald, Korbinian},\n'
            + '  publisher = {Universität Wien},\n'
            + '  year      = {' + (dateDisplay.match(/\d{4}/) || ['s.d.'])[0] + '},\n'
            + '  howpublished = {\\url{' + url + '}},\n'
            + '  note      = {' + collection + '. Zugriff: ' + today + '}\n'
            + '}';

        popover.innerHTML = '<div class="cite-section">'
            + '<div class="cite-label">Chicago</div>'
            + '<div class="cite-text" id="cite-chicago">' + esc(chicago) + '</div>'
            + '<button class="cite-copy-btn" data-target="cite-chicago" data-hint="Kopieren">&#x2398;</button>'
            + '</div>'
            + '<div class="cite-section">'
            + '<div class="cite-label">BibTeX</div>'
            + '<pre class="cite-text cite-bibtex" id="cite-bibtex">' + esc(bibtex) + '</pre>'
            + '<button class="cite-copy-btn" data-target="cite-bibtex" data-hint="Kopieren">&#x2398;</button>'
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


    // Annotation toggle: clicking a legend group toggles its layer class on
    // .doc-body (classMap scheme). State persists via localStorage.
    function initAnnotationToggle() {
        let body = document.querySelector('.doc-body');
        let toggles = document.querySelectorAll('.legend-toggle[data-layer]');
        if (!body || !toggles.length) return;

        let STORAGE_KEY = 'sugw-anno-layers';
        // One-time migration of the old 'wub-' localStorage key from the
        // former project name: carry over the preference, then drop it.
        try {
            let legacy = localStorage.getItem('wub-anno-layers');
            if (legacy !== null && localStorage.getItem(STORAGE_KEY) === null) {
                localStorage.setItem(STORAGE_KEY, legacy);
                localStorage.removeItem('wub-anno-layers');
            }
        } catch(e) { /* ignore */ }
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


    document.addEventListener('DOMContentLoaded', function() {
        if (document.querySelector('.doc-body')) {
            initAssertionsView();
            initCitationHelper();
            initAnnotationToggle();
        }
    });

})();
