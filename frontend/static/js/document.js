/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Document page: annotations view + citation helper + layer toggles
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;


    /* ------------------------------------------------------------------
       Annotations — all annotated layers from the TEI as structured
       tables below edition text + facsimile. Permanent area, no toggle.
       Four sub-tables:
         1. Persons / organisations / places (with role, attributes,
            event, section)
         2. Events (event refs + section type + dispositive verb)
         3. Dispositive formulas (trigger strings)
         4. Editorial additions (.anno-add)
       ------------------------------------------------------------------ */

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
        let summaryEl = container.querySelector('.annotations-summary');
        if (!body || !bodyEl) return;

        let DASH = '–';
        let ROLE_LABELS = {
            'issuer': 'Aussteller*in',
            'recipient': 'Empfänger*in',
            'witness': 'Zeug*in',
            'other': 'Sonstige'
        };

        // ---- 1. Entities: first inside function-role spans (with role),
        //         then standalone (without role).
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
                section: _sectionTypeFor(el),
                sex: el.getAttribute('data-sex') || ''
            });
        }

        // ---- 2. Events: one row per event span (deduped by ref).
        // Nested-Events (Events innerhalb von Events; "erwaehnte
        // Ereignisse" aus der Narrative) werden in der Tabelle nicht
        // als eigene Gruppe gefuehrt; ihre Entitaeten wandern in die
        // Gruppe ihres Eltern-Events. Der Gruppen-Header zeigt
        // ausschliesslich, was in der Quelle steht: das erste
        // Disp-Verb des Events plus die rohe ev__-ID als Anker.
        let events = [];
        let eventSeen = new Set();
        let eventSpans = body.querySelectorAll('.anno-event');

        // Map jede ref auf das outermost-anno-event in der Hierarchie.
        // Wird beim Entitaeten-Gruppieren genutzt, um nested-Events in
        // ihre Eltern-Gruppe zu kollabieren.
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
            if (isNested) continue; // nested events erscheinen nicht als eigene Gruppe
            let trigger = ev.querySelector('.anno-trigger-disp, .anno-trigger');
            events.push({
                ref: ref,
                section: _sectionTypeFor(ev),
                trigger: trigger ? trigger.textContent.trim() : ''
            });
        }

        // ---- 3. Dispositive formulas / trigger strings.
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

        // ---- 4. Editorial additions (.anno-add).
        let adds = [];
        let addSpans = body.querySelectorAll('.anno-add');
        for (let a = 0; a < addSpans.length; a++) {
            let ad = addSpans[a];
            adds.push({
                text: ad.textContent.trim(),
                section: _sectionTypeFor(ad)
            });
        }

        // ---- Summary in the header pill.
        // Entitaeten werden in Personen/Organisationen/Orte aufgeschluesselt,
        // damit der Quellen-Footer den Hinweis "X Pers., Y Org." nicht
        // mehr tragen muss (Kunden-Feedback 2026-05).
        let summaryParts = [];
        if (entities.length) {
            let personCount = 0, orgCount = 0, placeCount = 0;
            for (let i = 0; i < entities.length; i++) {
                if (entities[i].type === 'Person') personCount++;
                else if (entities[i].type === 'Organisation') orgCount++;
                else if (entities[i].type === 'Ort') placeCount++;
            }
            if (personCount) summaryParts.push(personCount + ' Person' + (personCount !== 1 ? 'en' : ''));
            if (orgCount) summaryParts.push(orgCount + ' Organisation' + (orgCount !== 1 ? 'en' : ''));
            if (placeCount) summaryParts.push(placeCount + ' Ort' + (placeCount !== 1 ? 'e' : ''));
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

        // Per-row hover hint: each annotation gets data-hint (body) plus
        // data-hint-type (small caps label). Picked up by hint.js. Body
        // is plain structured text -- no raw TEI markup leaking into
        // the UI tooltip layer (see Block 3 of the 2026-05 plan).
        function entityTipBody(f) {
            let parts = [f.name];
            if (f.role && f.role !== DASH) parts.push('Rolle: ' + f.role);
            if (f.attributes) parts.push('Attribute: ' + f.attributes);
            if (f.event) parts.push('Event: ' + f.event);
            if (f.section) parts.push('Abschnitt: ' + f.section);
            if (f.ref) parts.push('ID: ' + f.ref);
            return parts.join(' · ');
        }

        function eventTipBody(ev) {
            let parts = [ev.ref];
            if (ev.trigger) parts.push('Dispositiv-Verb: ' + ev.trigger);
            if (ev.section) parts.push('Abschnitt: ' + ev.section);
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
            // EdCore.esc emits &lt;/&gt;/&amp; but does not escape the
            // double quote — for attribute values " must also be
            // escaped, otherwise the first " in the body would
            // prematurely close the attribute.
            return esc(s).replace(/"/g, '&quot;');
        }
        function tipAttrs(type, body) {
            return ' data-hint="' + escAttr(body) + '" data-hint-type="' + escAttr(type) + '"';
        }

        // data-sort-value on each <td> drives the column sorter, which
        // re-uses the .sortable-table convention from profile.js.
        // For cells where the visible content is a link or a badge,
        // the plain text equivalent goes into data-sort-value so that
        // alphabetical sorting compares names, not href markup.
        function sortAttr(value) {
            return ' data-sort-value="' + escAttr(value) + '"';
        }

        // Type-Badge: einheitliche Pillen-Komponente, systemweit als
        // .entity-badge verwendet (auch Register-Profile, Quellenliste).
        // Klasse --person/--organisation/--ort uebersetzt aus dem
        // type-Label.
        function typeBadge(type) {
            let mod = type === 'Person' ? 'person'
                    : type === 'Organisation' ? 'organisation'
                    : type === 'Ort' ? 'place' : 'other';
            return '<span class="entity-badge entity-badge--' + mod
                + '">' + esc(type) + '</span>';
        }

        if (entities.length) {
            // Entitaeten nach Event gruppieren, damit auf einen Blick
            // erkennbar ist, welche Personen/Orgs/Orte zum selben
            // Rechtsgeschaeft gehoeren. Sortierung wirkt gruppen-aware:
            // Klick auf Spaltenkopf sortiert die Zeilen jeder Gruppe,
            // die Gruppen-Reihenfolge bleibt fix (Dokument-Reihenfolge
            // der Events). Diese Logik lebt in _attachAnnotationSorting.
            let rootPath = (document.body && document.body.dataset.rootPath) || '..';

            let entityGroups = {};
            let entityOrder = [];
            for (let p = 0; p < entities.length; p++) {
                let rawKey = entities[p].event || '';
                // Entitaeten in nested events landen in der Gruppe ihres
                // outermost-Eltern-Events. Damit verschwindet die
                // Sub-Gruppierung "Erwaehntes Ereignis N" aus der UI.
                let key = rawKey && topLevelByRef[rawKey] ? topLevelByRef[rawKey] : rawKey;
                if (!entityGroups[key]) { entityGroups[key] = []; entityOrder.push(key); }
                entityGroups[key].push(entities[p]);
            }
            // Event-Meta nach Ref fuer schnellen Lookup beim Rendern.
            let eventByRef = {};
            for (let i = 0; i < events.length; i++) eventByRef[events[i].ref] = events[i];

            // Gruppen-Reihenfolge: erst Events in der Reihenfolge ihres
            // Auftretens im Body, dann nicht-gemappte Gruppen (selten),
            // zuletzt ohne-Event-Gruppe.
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

            function entityRow(f) {
                let nameMain;
                if (f.type === 'Person' && f.ref && f.ref.indexOf('pe__') === 0) {
                    nameMain = '<a class="anno-table-link" href="'
                        + esc(rootPath) + '/register/persons/' + esc(f.ref) + '.html">'
                        + esc(f.name) + '</a>';
                } else if (f.type === 'Organisation' && f.ref && f.ref.indexOf('org__') === 0) {
                    nameMain = '<a class="anno-table-link" href="'
                        + esc(rootPath) + '/register/orgs/' + esc(f.ref) + '.html">'
                        + esc(f.name) + '</a>';
                } else {
                    nameMain = esc(f.name);
                }
                // ID lebt nur noch im Row-Tooltip (entityTipBody),
                // damit jede Zeile einzeilig bleibt und mehrere Entitaeten
                // untereinander nicht zur Tapete werden. Abschnitt
                // (Regest/Siegelbeschreibung/...) ebenfalls nur im
                // Tooltip -- meist Regest, geringer analytischer Wert
                // als eigene Spalte.
                // Geschlecht-Glyph nur bei Person, sonst leere Zelle.
                let sexCell = '';
                let sexSort = '';
                if (f.type === 'Person') {
                    if (f.sex === 'm') { sexCell = '<span class="anno-sex">m</span>'; sexSort = 'm'; }
                    else if (f.sex === 'f') { sexCell = '<span class="anno-sex">w</span>'; sexSort = 'w'; }
                    else { sexCell = '<span class="anno-sex anno-sex--unknown">' + DASH + '</span>'; sexSort = 'z'; }
                }
                return '<tr' + tipAttrs(f.type + '-Annotation', entityTipBody(f)) + '>'
                    + '<td' + sortAttr(f.name) + '>' + nameMain + '</td>'
                    + '<td' + sortAttr(f.type) + '>' + typeBadge(f.type) + '</td>'
                    + '<td' + sortAttr(f.role) + '>' + esc(f.role) + '</td>'
                    + '<td' + sortAttr(f.attributes) + '>' + esc(f.attributes || DASH) + '</td>'
                    + '<td' + sortAttr(sexSort) + '>' + sexCell + '</td>'
                    + '</tr>';
            }

            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Entitäten</h3>'
                + '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="name" data-hint="Wortlaut, mit dem die Person, Organisation oder der Ort in der Quelle erscheint.">Genannt als</th>'
                + '<th scope="col" data-sort="type" data-hint="Annotations-Kategorie: Person, Organisation oder Ort.">Typ</th>'
                + '<th scope="col" data-sort="role" data-hint="Funktion im Rechtsgeschäft: Aussteller*in, Empfänger*in, Zeug*in oder Sonstige.">Funktionsrolle</th>'
                + '<th scope="col" data-sort="attributes" data-hint="Zusatzangaben zur Entität: Beruf, Titel, Verwandtschaftsbezug, als verstorben genannt etc.">Attribute</th>'
                + '<th scope="col" data-sort="sex" data-hint="Geschlecht laut Personenregister (m oder w). Nur bei Personen belegt.">Geschlecht</th>'
                + '</tr></thead><tbody>';
            for (let g = 0; g < orderedKeys.length; g++) {
                let key = orderedKeys[g];
                let label;
                if (!key) {
                    label = '<span class="annotations-group-label">Ohne Event</span>';
                } else {
                    let ev = eventByRef[key];
                    // Quellentext (Disp-Verb) als kursiv und in
                    // Trigger-Farbe markieren -- wiedererkennbar mit
                    // den Disp-Verben im Body. Kein UI-Vorspann mehr.
                    let trig = ev && ev.trigger ? ev.trigger : '';
                    if (trig) {
                        label = '<span class="annotations-group-source">' + esc(trig) + '</span>'
                              + '<span class="annotations-group-id">' + esc(key) + '</span>';
                    } else {
                        label = '<span class="annotations-group-id">' + esc(key) + '</span>';
                    }
                }
                html += '<tr class="annotations-group-row"><th colspan="5" scope="rowgroup">'
                    + label + '</th></tr>';
                let rows = entityGroups[key];
                for (let r2 = 0; r2 < rows.length; r2++) {
                    html += entityRow(rows[r2]);
                }
            }
            html += '</tbody></table></section>';
        }

        if (triggers.length) {
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Dispositivformeln</h3>'
                + '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="text">Text</th>'
                + '<th scope="col" data-sort="kind">Art</th>'
                + '<th scope="col" data-sort="section">Abschnitt</th>'
                + '<th scope="col" data-sort="event">Event</th>'
                + '</tr></thead><tbody>';
            for (let t2 = 0; t2 < triggers.length; t2++) {
                let tr2 = triggers[t2];
                html += '<tr' + tipAttrs('Dispositivformel', triggerTipBody(tr2)) + '>'
                    + '<td' + sortAttr(tr2.text) + '>' + esc(tr2.text) + '</td>'
                    + '<td' + sortAttr(tr2.kind) + '>' + esc(tr2.kind) + '</td>'
                    + '<td' + sortAttr(tr2.section) + '>' + esc(tr2.section || DASH) + '</td>'
                    + '<td' + sortAttr(tr2.event) + '><span class="cell-id">' + esc(tr2.event || DASH) + '</span></td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        if (adds.length) {
            html += '<section class="annotation-group">'
                + '<h3 class="annotation-group-title">Editorische Ergänzungen</h3>'
                + '<table class="annotations-table sortable-table"><thead><tr>'
                + '<th scope="col" data-sort="text">Text</th>'
                + '<th scope="col" data-sort="section">Abschnitt</th>'
                + '</tr></thead><tbody>';
            for (let a2 = 0; a2 < adds.length; a2++) {
                let ad2 = adds[a2];
                html += '<tr' + tipAttrs('Editorische Ergänzung', addTipBody(ad2)) + '>'
                    + '<td' + sortAttr(ad2.text) + '>' + esc(ad2.text) + '</td>'
                    + '<td' + sortAttr(ad2.section) + '>' + esc(ad2.section || DASH) + '</td>'
                    + '</tr>';
            }
            html += '</tbody></table></section>';
        }

        bodyEl.innerHTML = html;

        // Attach column sorting to every freshly built table. Mechanik
        // analog zu profile.js: data-sort-value pro td, EdCore.compareValues
        // als Vergleichs-Primitive, dritter Klick setzt zurueck.
        let sortTables = bodyEl.querySelectorAll('table.sortable-table');
        for (let s = 0; s < sortTables.length; s++) {
            _attachAnnotationSorting(sortTables[s]);
        }
    }

    /* ------------------------------------------------------------------
       Sortierung der Annotationen-Untertabellen.
       Nachgebaut nach profile.js -> setupSortableTable. profile.js wird
       auf Document-Pages nicht geladen, ausserdem laeuft seine init zu
       frueh (DOMContentLoaded), bevor buildAnnotationsTables die
       Tabellen erzeugt hat. Daher eigene, schlanke Variante hier.
       ------------------------------------------------------------------ */
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

            // Gruppen-aware Sortierung: tbody wird an den
            // .annotations-group-row-Grenzen segmentiert; jede Gruppe
            // wird in sich sortiert, die Gruppen-Reihenfolge bleibt
            // fix. Tabellen ohne Gruppen-Header fallen auf eine
            // implizite Einzel-Gruppe zurueck (= globale Sortierung).
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


    /* ------------------------------------------------------------------
       Annotation toggle — detail legend is the control. Clicking a
       group (entities / function roles / attributes / dispositive
       formula) toggles its layer class on `.doc-body`. State persists
       via localStorage; classes follow the existing classMap scheme so
       current CSS selectors (.doc-body.hide-entities .anno-...) keep
       working.
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
