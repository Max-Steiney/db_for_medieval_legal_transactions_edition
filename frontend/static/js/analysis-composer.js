/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis page
   Composer + KPI dashboard

   Left panel: subject list + filter chips + "+ Filter" button.
   Live update on every state change.

   Right panel: subject overview (always visible). When filters are active,
   a result card with share and drill-down is shown on top.

   State shape:
     { subject: 'persons'|'sources'|'events'|'relationships',
       filters: { <filterId>: <value>, ... } }

   Hash:  #s=<subject>[&filter=<k:v,k:v>]

   Public API:
     AnalysisComposer.loadVocab(cb)
     AnalysisComposer.defaultState()
     AnalysisComposer.fromHash(parsed) -> state | null
     AnalysisComposer.toHash(state)    -> string
     AnalysisComposer.requiredFiles(state) -> [string]
     AnalysisComposer.render({state, dataMap, composerRoot, resultPanel,
                              openDrill, onChange})

   openDrill(title, fileKeys) is a callback supplied by analysis.js that
   wraps VizCore.openDrillOverlay. The composer just hands the file_keys
   to it on click; lazy lookup loading lives in the caller.
   ========================================================================== */

(function() {
    'use strict';

    /* -------- Helpers ----------------------------------------------------- */

    let ROOT = window.ROOT_PATH || '.';

    function fmt(n) {
        return typeof n === 'number' && !isNaN(n) ? n.toLocaleString('de-DE') : '0';
    }

    function pct(part, total) {
        if (!total) return '';
        return (part / total * 100).toFixed(1).replace('.', ',') + ' %';
    }

    function esc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function(c) {
            return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
        });
    }

    function el(tag, className, html) {
        let n = document.createElement(tag);
        if (className) n.className = className;
        if (html != null) n.innerHTML = html;
        return n;
    }

    /* -------- Vocabulary -------------------------------------------------- */

    let VOCAB = null;

    function loadVocab(callback) {
        if (VOCAB) { callback(VOCAB); return; }
        fetch(ROOT + '/data/query_vocabulary.json')
            .then(function(r) { return r.json(); })
            .then(function(v) { VOCAB = v; callback(v); })
            .catch(function() { callback(null); });
    }

    function valueLabel(filterId, value) {
        let f = VOCAB.filters[filterId];
        if (!f) return value;
        if (f.values) {
            for (let i = 0; i < f.values.length; i++) {
                if (f.values[i].value === value) return f.values[i].label;
            }
        }
        if (f.value_kind === 'range') return value + (f.value_suffix || '');
        if (f.value_kind === 'from_data') {
            let lbl = f.value_labels && f.value_labels[value];
            if (lbl) return lbl;
            if (f.value_labels_ref) {
                let ref = VOCAB.filters[f.value_labels_ref];
                if (ref && ref.value_labels && ref.value_labels[value]) {
                    return ref.value_labels[value];
                }
            }
        }
        return value;
    }

    function valuesForFilter(filterId, dataMap) {
        let f = VOCAB.filters[filterId];
        if (!f) return [];
        if (f.values) return f.values.slice();
        if (f.value_kind === 'range') {
            let out = [];
            for (let d = f.range[0]; d <= f.range[1]; d += (f.step || 10)) {
                out.push({ value: String(d), label: d + (f.value_suffix || '') });
            }
            return out;
        }
        if (f.value_kind === 'from_data') {
            let src = (f.values_source || '').split('.');
            let fileName = src[0] === 'roles' ? 'roles.json'
                         : src[0] === 'transactions' ? 'transactions.json' : null;
            let node = fileName ? dataMap[fileName] : null;
            for (let i = 1; node && i < src.length; i++) node = node[src[i]];
            if (!node) return [];
            return Object.keys(node)
                .sort(function(a, b) { return (node[b] || 0) - (node[a] || 0); })
                .map(function(k) { return { value: k, label: valueLabel(filterId, k) }; });
        }
        return [];
    }

    /* -------- State + Hash ----------------------------------------------- */

    function defaultState() {
        return { subject: 'persons', filters: {} };
    }

    function activeFilterIds(state) {
        return Object.keys(state.filters || {}).filter(function(k) {
            return state.filters[k] != null && state.filters[k] !== '';
        });
    }

    function fromHash(parsed) {
        if (!parsed || !parsed.s) return null;
        let st = { subject: parsed.s, filters: {} };
        if (parsed.filter) {
            parsed.filter.split(',').forEach(function(kv) {
                let i = kv.indexOf(':');
                if (i > 0) st.filters[kv.slice(0, i)] = kv.slice(i + 1);
            });
        }
        return st;
    }

    function toHash(state) {
        let parts = ['s=' + encodeURIComponent(state.subject)];
        let fkeys = activeFilterIds(state);
        if (fkeys.length) {
            parts.push('filter=' + fkeys.map(function(k) {
                return encodeURIComponent(k) + ':' + encodeURIComponent(state.filters[k]);
            }).join(','));
        }
        return '#' + parts.join('&');
    }

    let SUBJECT_FILES = {
        persons:       ['roles.json'],
        sources:       ['timeline.json'],
        events:        ['roles.json', 'transactions.json'],
        relationships: ['relations.json']
    };

    function requiredFiles(state) {
        let files = ['query_vocabulary.json'].concat(SUBJECT_FILES[state.subject] || []);
        // org_type picker for events reads from roles; already included above.
        if (state.filters.org_category) files.push('categories.json');
        let seen = {}, out = [];
        files.forEach(function(f) { if (!seen[f]) { seen[f] = true; out.push(f); } });
        return out;
    }

    /* -------- Resolve via capabilities ----------------------------------- */

    function resolve(state, dataMap) {
        let caps = window.AnalysisCapabilities;
        if (!caps) return null;
        let cap = caps.pick(state.subject, state.filters);
        if (!cap) return null;
        if (!cap.files.every(function(f) { return !!dataMap[f]; })) return null;
        try { return cap.resolve(state.filters, dataMap); }
        catch (e) { return null; }
    }

    function liveCount(subject, trialFilters, dataMap) {
        let caps = window.AnalysisCapabilities;
        if (!caps) return null;
        let cap = caps.pick(subject, trialFilters);
        if (!cap) return null;
        if (!cap.files.every(function(f) { return !!dataMap[f]; })) return null;
        try {
            let r = cap.resolve(trialFilters, dataMap);
            return r ? r.count : null;
        } catch (e) { return null; }
    }

    /* -------- Picker ----------------------------------------------------- */

    let openPop = null;

    function closePicker() {
        if (openPop && openPop.parentNode) openPop.parentNode.removeChild(openPop);
        openPop = null;
    }

    function showPicker(anchor, options, onPick, opts) {
        closePicker();
        opts = opts || {};
        let pop = el('div', 'composer-picker');
        pop.setAttribute('role', 'listbox');
        if (opts.title) pop.appendChild(el('div', 'composer-picker-title', esc(opts.title)));

        options.forEach(function(o) {
            let b = el('button', 'composer-picker-option' +
                (o.disabled ? ' is-disabled' : '') +
                (o.active ? ' is-active' : '') +
                (typeof o.count === 'number' && o.count === 0 ? ' is-zero' : ''));
            b.type = 'button';
            let inner = '<span class="composer-picker-option-label">' + esc(o.label) + '</span>';
            if (typeof o.count === 'number') {
                inner += '<span class="composer-picker-option-count">' + fmt(o.count) + '</span>';
            }
            b.innerHTML = inner;
            if (!o.disabled) {
                b.addEventListener('click', function(ev) {
                    ev.stopPropagation();
                    onPick(o.value);
                    closePicker();
                });
            }
            pop.appendChild(b);
        });

        document.body.appendChild(pop);
        let rect = anchor.getBoundingClientRect();
        pop.style.position = 'absolute';
        pop.style.top = (window.scrollY + rect.bottom + 4) + 'px';
        pop.style.left = (window.scrollX + rect.left) + 'px';
        pop.style.minWidth = Math.max(rect.width, 200) + 'px';
        openPop = pop;

        setTimeout(function() {
            document.addEventListener('click', outsideClose, true);
            document.addEventListener('keydown', escClose);
        }, 0);
    }

    function outsideClose(ev) {
        if (!openPop || openPop.contains(ev.target)) return;
        closePicker();
        document.removeEventListener('click', outsideClose, true);
        document.removeEventListener('keydown', escClose);
    }

    function escClose(ev) { if (ev.key === 'Escape') closePicker(); }

    /* -------- Composer (left panel) -------------------------------------- */

    function renderComposer(state, dataMap, root, onChange) {
        root.innerHTML = '';
        root.appendChild(buildSubjectGroup(state, onChange));
        root.appendChild(buildFilterGroup(state, dataMap, onChange));
    }

    function buildSubjectGroup(state, onChange) {
        let g = el('div', 'composer-group');
        g.appendChild(el('div', 'composer-group-label', 'Thema'));
        let list = el('div', 'composer-subjects');
        Object.keys(VOCAB.subjects).forEach(function(sid) {
            let s = VOCAB.subjects[sid];
            let b = el('button', 'composer-subject' + (state.subject === sid ? ' is-active' : ''));
            b.type = 'button';
            b.innerHTML = '<span class="composer-subject-marker"></span>' +
                '<span class="composer-subject-label">' + esc(s.label) + '</span>';
            b.addEventListener('click', function() {
                if (state.subject !== sid) onChange({ subject: sid, filters: {} });
            });
            list.appendChild(b);
        });
        g.appendChild(list);
        return g;
    }

    function buildFilterGroup(state, dataMap, onChange) {
        let g = el('div', 'composer-group');
        g.appendChild(el('div', 'composer-group-label', 'Filter'));
        let wrap = el('div', 'composer-chips');
        let active = activeFilterIds(state);
        if (active.length === 0) {
            let subjLabel = VOCAB.subjects[state.subject].label.toLowerCase();
            wrap.appendChild(el('span', 'composer-empty-hint',
                'noch keine Filter — alle ' + subjLabel + ' werden gezaehlt'));
        }
        active.forEach(function(fid) {
            wrap.appendChild(buildFilterChip(state, fid, dataMap, onChange));
        });
        wrap.appendChild(buildAddFilterButton(state, dataMap, onChange));
        g.appendChild(wrap);
        return g;
    }

    function buildFilterChip(state, fid, dataMap, onChange) {
        let def = VOCAB.filters[fid];
        let lblText = def.label || fid;
        let valText = valueLabel(fid, state.filters[fid]);

        let chip = el('span', 'composer-chip');
        let btn = el('button', 'composer-chip-body');
        btn.type = 'button';
        btn.innerHTML = '<span class="composer-chip-label">' + esc(lblText) + '</span>' +
            '<span class="composer-chip-value">' + esc(valText) + '</span>' +
            '<span class="composer-chip-caret">&#9662;</span>';
        btn.title = 'Wert aendern';
        btn.addEventListener('click', function() {
            let opts = valuesForFilter(fid, dataMap).map(function(o) {
                let trial = Object.assign({}, state.filters);
                trial[fid] = o.value;
                return Object.assign({}, o, {
                    active: state.filters[fid] === o.value,
                    count: liveCount(state.subject, trial, dataMap)
                });
            });
            showPicker(btn, opts, function(v) {
                let nf = Object.assign({}, state.filters);
                nf[fid] = v;
                onChange(Object.assign({}, state, { filters: nf }));
            }, { title: lblText });
        });
        chip.appendChild(btn);

        let x = el('button', 'composer-chip-remove', '×');
        x.type = 'button';
        x.title = 'Filter entfernen';
        x.setAttribute('aria-label', 'Filter ' + lblText + ' entfernen');
        x.addEventListener('click', function() {
            let nf = Object.assign({}, state.filters);
            delete nf[fid];
            onChange(Object.assign({}, state, { filters: nf }));
        });
        chip.appendChild(x);
        return chip;
    }

    function buildAddFilterButton(state, dataMap, onChange) {
        let subj = VOCAB.subjects[state.subject];
        let max = (VOCAB.constraints && VOCAB.constraints.max_active_filters) || 3;
        let active = activeFilterIds(state);
        let atMax = active.length >= max;

        let btn = el('button', 'composer-chip-add' + (atMax ? ' is-disabled' : ''));
        btn.type = 'button';
        btn.textContent = atMax ? 'max. ' + max + ' Filter' : '+ Filter';
        btn.disabled = atMax;
        if (atMax) return btn;

        btn.addEventListener('click', function() {
            let caps = window.AnalysisCapabilities;
            let opts = (subj.filters || []).map(function(fid) {
                let alreadyOn = active.indexOf(fid) !== -1;
                let combo = active.concat([fid]);
                let allowed = caps && caps.isFilterCombinationAllowed(state.subject, combo);
                return {
                    value: fid,
                    label: VOCAB.filters[fid].label,
                    disabled: alreadyOn || !allowed
                };
            });
            showPicker(btn, opts, function(fid) {
                /* default to first value with count > 0 */
                let values = valuesForFilter(fid, dataMap);
                let pick = values[0];
                for (let i = 0; i < values.length; i++) {
                    let trial = Object.assign({}, state.filters);
                    trial[fid] = values[i].value;
                    let c = liveCount(state.subject, trial, dataMap);
                    if (typeof c === 'number' && c > 0) { pick = values[i]; break; }
                }
                if (!pick) return;
                let nf = Object.assign({}, state.filters);
                nf[fid] = pick.value;
                onChange(Object.assign({}, state, { filters: nf }));
            }, { title: 'Filter hinzufuegen' });
        });
        return btn;
    }

    /* -------- Result (right panel) --------------------------------------- */

    function renderResult(state, dataMap, panel, openDrill) {
        panel.innerHTML = '';
        let subj = VOCAB.subjects[state.subject];
        let hasFilters = activeFilterIds(state).length > 0;

        if (hasFilters) {
            let r = resolve(state, dataMap);
            if (!r) {
                panel.appendChild(el('div', 'result-blocked',
                    'Diese Filter-Kombination ist nicht aufloesbar. Bitte einen Filter entfernen.'));
            } else {
                panel.appendChild(buildPrimaryBlock(state, r, dataMap, openDrill));
            }
        }

        panel.appendChild(el('div', 'result-section-title',
            (subj ? subj.label : '') + ' im Datenstand'));

        let kpis = overviewKpis(state.subject, dataMap);
        if (kpis.length) panel.appendChild(buildKpiGrid(kpis));

        let cov = (VOCAB.coverage && VOCAB.coverage[state.subject]) || '';
        if (cov) panel.appendChild(el('p', 'result-coverage', esc(cov)));
    }

    function buildPrimaryBlock(state, r, dataMap, openDrill) {
        let wrap = el('div', 'result-primary');
        wrap.appendChild(el('div', 'result-section-title', 'Aktuelle Auswahl'));

        let total = subjectTotal(state.subject, dataMap);
        let dd = r.drillDownIds || [];
        let unique = {}; dd.forEach(function(k) { unique[k] = true; });
        let sourceCount = Object.keys(unique).length;

        let primary = [{
            label: primaryLabel(state.subject),
            value: r.count,
            primary: true,
            suffix: total ? '   (' + pct(r.count, total) + ')' : ''
        }];
        if (sourceCount) {
            primary.push({ label: 'in unterschiedlichen Quellen', value: sourceCount });
        }
        wrap.appendChild(buildKpiGrid(primary));

        if (r.caveats && r.caveats.length) {
            r.caveats.forEach(function(c) {
                wrap.appendChild(el('p', 'result-caveat', esc(c)));
            });
        }

        wrap.appendChild(buildResultActions(r, state, openDrill));
        return wrap;
    }

    function buildKpiGrid(kpis) {
        let grid = el('div', 'result-kpis');
        kpis.forEach(function(k) {
            let card = el('div', 'result-kpi' + (k.primary ? ' is-primary' : ''));
            let html = '<div class="result-kpi-value">' + fmt(k.value);
            if (k.suffix) html += '<span class="result-kpi-suffix">' + esc(k.suffix) + '</span>';
            html += '</div>';
            html += '<div class="result-kpi-label">' + esc(k.label) + '</div>';
            if (k.hint) html += '<div class="result-kpi-hint">' + esc(k.hint) + '</div>';
            card.innerHTML = html;
            grid.appendChild(card);
        });
        return grid;
    }

    function buildResultActions(r, state, openDrill) {
        let row = el('div', 'result-actions');
        let dd = r.drillDownIds || [];
        let n = dd.length;

        let ddBtn = el('button', 'result-action-btn');
        ddBtn.type = 'button';
        ddBtn.disabled = n === 0;
        ddBtn.textContent = n > 0 ? 'Quellen anzeigen (' + fmt(n) + ')' : 'Keine Quellenliste';
        if (n > 0 && typeof openDrill === 'function') {
            ddBtn.addEventListener('click', function() {
                openDrill(r.drillDownLabel || 'Quellen', dd);
            });
        }
        row.appendChild(ddBtn);

        let p = el('button', 'result-action-btn result-action-btn-permalink');
        p.type = 'button';
        p.textContent = 'Permalink kopieren';
        p.addEventListener('click', function() { copyPermalink(p, toHash(state)); });
        row.appendChild(p);
        return row;
    }

    function copyPermalink(btn, hash) {
        let loc = window.location;
        let url = loc.protocol + '//' + loc.host + loc.pathname + hash;
        let done = function() {
            let prev = btn.textContent;
            btn.textContent = 'kopiert';
            btn.classList.add('is-ok');
            setTimeout(function() {
                btn.classList.remove('is-ok');
                btn.textContent = prev;
            }, 1200);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(done).catch(function() { fallbackCopy(url, done); });
        } else { fallbackCopy(url, done); }
    }

    function fallbackCopy(text, cb) {
        let ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch (e) { /* noop */ }
        document.body.removeChild(ta); cb();
    }

    /* -------- KPI data sources ------------------------------------------- */

    let OVERVIEW = {
        persons: function(d) {
            let c = (d['roles.json'] || {}).coverage || {};
            let sd = c.sex_distribution || {};
            return [
                { label: 'Personen gesamt',       value: c.person_count || 0 },
                { label: 'Frauen',                value: sd.f || 0 },
                { label: 'Männer',                value: sd.m || 0 },
                { label: 'mit Institutionsbezug', value: c.persons_with_org || 0 }
            ];
        },
        sources: function(d) {
            let t = d['timeline.json'] || {};
            let coll = t.collections || {};
            return [
                { label: 'Quellen gesamt', value: t.total || 0 },
                { label: 'QGW',            value: (coll.QGW || {}).count || 0 },
                { label: 'Stadtbuecher',   value: (coll.Stadtbuecher || {}).count || 0 }
            ];
        },
        events: function(d) {
            let c = (d['roles.json'] || {}).coverage || {};
            return [
                { label: 'Rechtsgeschaefte gesamt', value: c.total_events || 0 },
                { label: 'normalisiert',            value: c.normalisation_rate || 0,
                  hint: 'in kontrolliertes Vokabular ueberfuehrt' }
            ];
        },
        relationships: function(d) {
            let c = (d['relations.json'] || {}).coverage || {};
            let tc = c.type_counts || {};
            return [
                { label: 'Beziehungen gesamt', value: c.total_relations || 0 },
                { label: 'Verwandtschaft',     value: tc.kin || 0 },
                { label: 'Beruf',              value: tc.occ || 0 },
                { label: 'Vertretung',         value: tc.rep || 0 },
                { label: 'Freundschaft',       value: tc.friend || 0 }
            ];
        }
    };

    let TOTAL = {
        persons:       function(d) { return ((d['roles.json'] || {}).coverage || {}).person_count || 0; },
        sources:       function(d) { return (d['timeline.json'] || {}).total || 0; },
        events:        function(d) { return ((d['roles.json'] || {}).coverage || {}).total_events || 0; },
        relationships: function(d) { return ((d['relations.json'] || {}).coverage || {}).total_relations || 0; }
    };

    let PRIMARY_LABEL = {
        persons:       'Treffer (Personen)',
        sources:       'Treffer (Quellen)',
        events:        'Treffer (Rechtsgeschaefte)',
        relationships: 'Treffer (Beziehungen)'
    };

    function overviewKpis(subject, dataMap) {
        return (OVERVIEW[subject] || function() { return []; })(dataMap);
    }

    function subjectTotal(subject, dataMap) {
        return (TOTAL[subject] || function() { return 0; })(dataMap);
    }

    function primaryLabel(subject) {
        return PRIMARY_LABEL[subject] || 'Treffer';
    }

    /* -------- Public API ------------------------------------------------- */

    function render(opts) {
        if (!VOCAB) {
            opts.composerRoot.innerHTML = '<p class="composer-loading">Lade Vokabular...</p>';
            opts.resultPanel.innerHTML = '';
            return;
        }
        renderComposer(opts.state, opts.dataMap, opts.composerRoot, opts.onChange);
        renderResult(opts.state, opts.dataMap, opts.resultPanel, opts.openDrill);
    }

    window.AnalysisComposer = {
        loadVocab: loadVocab,
        defaultState: defaultState,
        fromHash: fromHash,
        toHash: toHash,
        requiredFiles: requiredFiles,
        render: render
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { AnalysisComposer: window.AnalysisComposer };
    }

})();
