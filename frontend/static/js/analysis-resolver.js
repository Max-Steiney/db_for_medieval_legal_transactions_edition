// Constellation query UI for analysis/index.html, driven by
// role_constellation.json. Each "+ Person/Organisation" box is an optional
// filter condition; any non-empty box triggers live matching (no submit).
// State round-trips through the URL hash; the current table exports to CSV.
//
// Event shape (role_constellation.json::events[]):
//   { e, f, c, d, tx, p:[{p,n,r,s,t,o,u,nt?}], og:[{g,n,r,tp}]? }
//   r in {issuer, recipient, witness, other}; s in {m, f, ""}
//   o[] occupation strings (verbatim); u[] Uhlirz classes; og[].tp org type

(function () {
    'use strict';

    const root = document.querySelector('.analysis-query');
    if (!root) return;

    const personsTable = root.querySelector('#qb-persons-table');
    const personsTbody = root.querySelector('#qb-persons-tbody');
    const orgsTable = root.querySelector('#qb-orgs-table');
    const orgsTbody = root.querySelector('#qb-orgs-tbody');
    const addPersonBtn = root.querySelector('#qb-add-person');
    const addOrgBtn = root.querySelector('#qb-add-org');
    const resetBtn = root.querySelector('#filter-reset');
    // Empty for now (scope switch hidden in analysis.html); the scopeChips
    // handlers below are then no-ops but kept in case it returns.
    const scopeChips = root.querySelectorAll('[data-filter="scope"] .qb-pill');
    const corpusChecksRoot = root.querySelector('#filter-corpora');
    const hitsSrc = root.querySelector('#hits-sources');
    const hitsEv  = root.querySelector('#hits-events');
    const tbody = root.querySelector('#hits-tbody');
    const emptyBox = root.querySelector('#hits-empty');
    const emptyMsg = root.querySelector('#hits-empty-msg');
    const csvBtn = root.querySelector('#csv-download');
    const activeStrip = root.querySelector('#active-filters');
    const resultsToolbar = root.querySelector('#results-toolbar');
    const hitsTable = root.querySelector('#hits-table');

    let DATA = null;       // role_constellation.json
    let DOCS_LOOKUP = {};  // file_key -> {u, i, d, c, r} from docs_lookup.json
    let OCC_VOCAB = [];    // [{value, count}]
    let dataPromise = null;

    function getDataUrl() {
        const tag = document.getElementById('role-constellation-data');
        try {
            return JSON.parse(tag.textContent).url;
        } catch (_) {
            return '../data/role_constellation.json';
        }
    }

    function loadData() {
        if (DATA) return Promise.resolve(DATA);
        if (dataPromise) return dataPromise;
        // Load matching data and the lookup (source URLs + readable idnos) in parallel.
        const cstUrl = getDataUrl();
        const lookupUrl = (window.ROOT_PATH || '..') + '/data/docs_lookup.json';
        dataPromise = Promise.all([
            fetch(cstUrl).then(r => {
                if (!r.ok) throw new Error('HTTP ' + r.status); return r.json();
            }),
            fetch(lookupUrl).then(r => r.ok ? r.json() : {}).catch(() => ({})),
        ])
            .then(([json, lookup]) => { DATA = json; DOCS_LOOKUP = lookup || {}; return DATA; })
            .catch(err => {
                emptyMsg.textContent =
                    'Daten konnten nicht geladen werden (' + err.message + '). ' +
                    'Bitte Seite neu laden.';
                throw err;
            });
        return dataPromise;
    }

    // /analysis/ sits one level deep; docs_lookup holds root-relative URLs.
    function docUrl(fileKey) {
        const rec = DOCS_LOOKUP[fileKey];
        if (rec && rec.u) return '../' + rec.u;
        return '../documents/' + encodeURIComponent(fileKey) + '.html';
    }
    function docIdno(fileKey) {
        const rec = DOCS_LOOKUP[fileKey];
        return (rec && rec.i) || fileKey;
    }

    try {
        OCC_VOCAB = JSON.parse(personsTable.dataset.occupationVocab || '[]');
    } catch (_) { OCC_VOCAB = []; }
    // Full vocabulary (all attested occupations) feeds only the "also
    // recognized" block; the dropdown stays the top-50. Falls back silently
    // to the normal vocabulary when the build ships no full list.
    let OCC_FULL_VOCAB = [];
    try {
        OCC_FULL_VOCAB = JSON.parse(personsTable.dataset.occupationFullVocab || '[]');
    } catch (_) { OCC_FULL_VOCAB = []; }
    let UHLIRZ_VOCAB = [];
    try {
        UHLIRZ_VOCAB = JSON.parse(personsTable.dataset.uhlirzVocab || '[]');
    } catch (_) { UHLIRZ_VOCAB = []; }
    let ORG_VOCAB = [];
    try {
        ORG_VOCAB = orgsTable
            ? JSON.parse(orgsTable.dataset.organisationVocab || '[]')
            : [];
    } catch (_) { ORG_VOCAB = []; }
    let ORG_FULL_VOCAB = [];
    try {
        ORG_FULL_VOCAB = orgsTable
            ? JSON.parse(orgsTable.dataset.organisationFullVocab || '[]')
            : [];
    } catch (_) { ORG_FULL_VOCAB = []; }
    let ORG_TYPE_VOCAB = [];
    try {
        ORG_TYPE_VOCAB = orgsTable
            ? JSON.parse(orgsTable.dataset.orgTypeVocab || '[]')
            : [];
    } catch (_) { ORG_TYPE_VOCAB = []; }

    // Custom popover instead of native <datalist>, which cannot be styled
    // (Windows Chrome renders a dark panel with white text). One instance at
    // a time, anchored on body so table overflow does not clip it.
    let activePopover = null;
    function closePopover() {
        if (activePopover) {
            activePopover.panel.remove();
            document.removeEventListener('mousedown', activePopover.onDocMouseDown);
            window.removeEventListener('resize', activePopover.onWindowChange);
            window.removeEventListener('scroll', activePopover.onWindowChange, true);
            activePopover = null;
        }
    }

    function attachAutocomplete(input, opts) {
        const vocab = opts.vocab;
        if (!vocab || !vocab.length) return;
        const hint = opts.hint || 'Vorkommen';
        const getContext = opts.getContext;
        const extra = (opts.extraVocab && opts.extraVocab.length)
            ? opts.extraVocab : null;
        let selectedIdx = -1;

        function ctx() {
            try { return (getContext && getContext()) || null; }
            catch (_) { return null; }
        }
        // Effective count under the active filter. Sex filter picks the
        // per-sex count; type filter zeroes non-matching items so they grey
        // out and sink instead of disappearing.
        function effectiveCount(item, c) {
            if (!c) return item.count || 0;
            if (c.sex === 'm') return item.count_m || 0;
            if (c.sex === 'f') return item.count_f || 0;
            if (c.sex === 'u') return item.count_u || 0;
            if (c.orgType && (item.type || '') !== c.orgType) return 0;
            return item.count || 0;
        }

        function buildItems(query) {
            const q = (query || '').trim().toLowerCase();
            const matches = q
                ? vocab.filter(v => v.value.toLowerCase().includes(q))
                : vocab.slice();
            const c = ctx();
            // Zero counts to the end, else empty suggestions sit on top.
            if (c && (c.sex || c.orgType)) {
                const decorated = matches.map((m, i) => ({
                    m, i, eff: effectiveCount(m, c),
                }));
                decorated.sort((a, b) => {
                    const az = a.eff === 0;
                    const bz = b.eff === 0;
                    if (az !== bz) return az ? 1 : -1;
                    return a.i - b.i;
                });
                return decorated.slice(0, 30).map(d => d.m);
            }
            return matches.slice(0, 30);
        }

        // Build a suggestion row. Primary rows carry a keyboard index and
        // sex-aware counts; tail rows ('extra') are static and plain.
        function makeRow(it, variant, primaryIdx, c, hasSexCounts) {
            const isPrimary = variant === 'primary';
            const eff = isPrimary ? effectiveCount(it, c) : (it.count || 0);
            const isZero = isPrimary && !!(c && (c.sex || c.orgType) && eff === 0);
            const row = document.createElement('button');
            row.type = 'button';
            row.className = 'qb-ac-item'
                + (isPrimary && primaryIdx === selectedIdx ? ' is-active' : '')
                + (isZero ? ' is-empty' : '')
                + (!isPrimary ? ' qb-ac-item--extra' : '');
            if (isPrimary) row.dataset.idx = primaryIdx;

            const value = document.createElement('span');
            value.className = 'qb-ac-value';
            value.textContent = it.value;
            row.appendChild(value);

            const meta = document.createElement('span');
            meta.className = 'qb-ac-meta';
            if (isPrimary && hasSexCounts) {
                const sexKey = c && c.sex;
                // Show the u segment only when relevant.
                const showU = sexKey === 'u' || (it.count_u || 0) > 0;
                function seg(cls, n, isActive) {
                    const s = document.createElement('span');
                    s.className = 'qb-ac-count qb-ac-count--' + cls
                        + (isActive ? ' is-active' : '')
                        + (sexKey && !isActive ? ' is-dim' : '');
                    s.textContent = n;
                    return s;
                }
                meta.appendChild(seg('total', (it.count || 0), !sexKey));
                meta.appendChild(seg('m', (it.count_m || 0), sexKey === 'm'));
                meta.appendChild(seg('f', (it.count_f || 0), sexKey === 'f'));
                if (showU) meta.appendChild(seg('u', (it.count_u || 0), sexKey === 'u'));
                meta.title = 'Gesamt ' + (it.count || 0) + ' ' + hint
                    + ', davon ' + (it.count_m || 0) + ' ' + SEX_LABELS.m
                    + ', ' + (it.count_f || 0) + ' ' + SEX_LABELS.f
                    + (showU ? ', ' + (it.count_u || 0) + ' ' + SEX_LABELS.u : '');
            } else {
                meta.textContent = (it.count || 0) + ' ' + hint;
            }
            row.appendChild(meta);

            if (isPrimary) {
                row.addEventListener('mouseenter', () => {
                    selectedIdx = primaryIdx;
                    Array.from(row.parentNode.children).forEach((el, k) => {
                        el.classList.toggle('is-active', k === primaryIdx);
                    });
                });
            }
            // mousedown, not click: blur would tear down the popover first.
            row.addEventListener('mousedown', (e) => {
                e.preventDefault();
                input.value = it.value;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                closePopover();
            });
            return row;
        }

        function renderItems(panel, items) {
            panel.innerHTML = '';
            if (!items.length) {
                const empty = document.createElement('div');
                empty.className = 'qb-ac-empty';
                empty.textContent = 'Keine Vorschläge';
                panel.appendChild(empty);
                return;
            }
            const c = ctx();
            // Sex counts exist only in the occupation vocabulary; org/Uhlirz
            // entries carry a single count.
            const hasSexCounts = 'count_m' in items[0] || 'count_f' in items[0];
            items.forEach((it, i) => {
                panel.appendChild(makeRow(it, 'primary', i, c, hasSexCounts));
            });

            // The "also recognized" block triggers on a search string OR an
            // active type filter; the latter so rare types (e.g. the few
            // Gemeinden) surface without typing.
            const q = (input.value || '').trim().toLowerCase();
            const triggerByType = !!(c && c.orgType);
            if (!extra || (!q && !triggerByType)) return;

            const primarySet = new Set(items.map(it => it.value));
            const tail = extra
                .filter(v => !primarySet.has(v.value)
                    && (!q || v.value.toLowerCase().includes(q))
                    && (!triggerByType || (v.type || '') === c.orgType))
                .slice(0, 12);
            if (!tail.length) return;

            const head = document.createElement('div');
            head.className = 'qb-ac-section';
            head.textContent = 'Auch erkannt (nicht in der Liste)';
            panel.appendChild(head);
            tail.forEach(it => panel.appendChild(makeRow(it, 'extra', -1, c, false)));
        }

        function positionPanel(panel) {
            const rect = input.getBoundingClientRect();
            panel.style.left = (rect.left + window.scrollX) + 'px';
            panel.style.top = (rect.bottom + window.scrollY + 2) + 'px';
            panel.style.width = rect.width + 'px';
        }

        function openPopover() {
            closePopover();
            const panel = document.createElement('div');
            panel.className = 'qb-ac-panel';
            panel.setAttribute('role', 'listbox');
            document.body.appendChild(panel);
            const items = buildItems(input.value);
            selectedIdx = items.length ? 0 : -1;
            renderItems(panel, items);
            positionPanel(panel);

            const onDocMouseDown = (e) => {
                if (e.target === input) return;
                if (panel.contains(e.target)) return;
                closePopover();
            };
            const onWindowChange = () => positionPanel(panel);
            document.addEventListener('mousedown', onDocMouseDown);
            window.addEventListener('resize', onWindowChange);
            window.addEventListener('scroll', onWindowChange, true);

            activePopover = { panel, input, items, onDocMouseDown, onWindowChange };
        }

        function refreshPopover() {
            if (!activePopover || activePopover.input !== input) {
                openPopover();
                return;
            }
            const items = buildItems(input.value);
            selectedIdx = items.length ? 0 : -1;
            activePopover.items = items;
            renderItems(activePopover.panel, items);
        }

        input.setAttribute('autocomplete', 'off');
        input.addEventListener('focus', openPopover);
        input.addEventListener('input', refreshPopover);
        input.addEventListener('keydown', (e) => {
            if (!activePopover || activePopover.input !== input) return;
            const items = activePopover.items;
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIdx = Math.min(items.length - 1, selectedIdx + 1);
                renderItems(activePopover.panel, items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIdx = Math.max(0, selectedIdx - 1);
                renderItems(activePopover.panel, items);
            } else if (e.key === 'Enter') {
                if (selectedIdx >= 0 && items[selectedIdx]) {
                    e.preventDefault();
                    input.value = items[selectedIdx].value;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    closePopover();
                }
            } else if (e.key === 'Escape') {
                closePopover();
            }
        });
    }

    // State: { persons:[{role,sex,occ,uhlirz}], orgs:[{role,name,type}],
    //          scope:'event'|'source', corpora:Set<string> }
    // occ and orgs.name are case-insensitive substring matches; uhlirz and
    // orgs.type are exact. An empty corpora set means "all corpora".
    // Defaults come from the checkboxes (all active initially).
    const ALL_CORPORA = corpusChecksRoot
        ? Array.from(corpusChecksRoot.querySelectorAll('input[data-corpus]'))
            .map(cb => cb.dataset.corpus)
        : [];
    let state = {
        persons: [],
        orgs: [],
        scope: 'event',
        corpora: new Set(ALL_CORPORA),
        // Result sort: key in {date, source, corpus, tx}, dir 1 asc / -1 desc.
        // Default chronological, empty dates last.
        sortKey: 'date',
        sortDir: 1
    };

    const ROLE_LABELS = {
        issuer:    'Aussteller:in',
        recipient: 'Empfänger:in',
        witness:   'Zeug:in / Siegler:in',
        other:     'sonstige Beteiligung'
    };
    const ROLE_LABELS_PLURAL = {
        issuer:    'Aussteller:innen',
        recipient: 'Empfänger:innen',
        witness:   'Zeug:innen / Siegler:innen',
        other:     'sonstige Beteiligung'
    };
    const ROLE_LIST = ['issuer', 'recipient', 'witness', 'other'];
    const SEX_LABELS = { m: 'männlich', f: 'weiblich', u: 'ohne Angabe' };

    function renderPersonRow(idx, p) {
        const tr = document.createElement('tr');
        tr.className = 'qb-person-row';
        tr.dataset.personIdx = idx;

        const numTd = document.createElement('td');
        numTd.className = 'qb-col-num';
        const numSpan = document.createElement('span');
        numSpan.className = 'qb-person-num';
        numSpan.textContent = idx + 1;
        numTd.appendChild(numSpan);
        tr.appendChild(numTd);

        // Role (optional; blank = any role)
        const roleTd = document.createElement('td');
        roleTd.className = 'qb-col-role';
        const roleSel = document.createElement('select');
        roleSel.className = 'qb-person-role';
        roleSel.setAttribute('aria-label', 'Rolle Person ' + (idx + 1));
        const blank = document.createElement('option');
        blank.value = '';
        blank.textContent = '— beliebige Rolle —';
        roleSel.appendChild(blank);
        ROLE_LIST.forEach(r => {
            const o = document.createElement('option');
            o.value = r;
            o.textContent = ROLE_LABELS_PLURAL[r];
            if (p.role === r) o.selected = true;
            roleSel.appendChild(o);
        });
        roleSel.addEventListener('change', () => {
            state.persons[idx].role = roleSel.value;
            sync();
        });
        roleTd.appendChild(roleSel);
        tr.appendChild(roleTd);

        // Sex (optional)
        const sexTd = document.createElement('td');
        sexTd.className = 'qb-col-sex';
        const sexSel = document.createElement('select');
        sexSel.setAttribute('aria-label', 'Geschlecht Person ' + (idx + 1));
        // 'u' (unspecified) deliberately omitted: in the current corpus every
        // annotated person has a sex (m or f), so the option always yields 0
        // hits. Re-add 'u' once persons without a sex enter the corpus.
        ['', 'm', 'f'].forEach(v => {
            const o = document.createElement('option');
            o.value = v;
            o.textContent = v === '' ? '— alle —' : SEX_LABELS[v];
            if ((p.sex || '') === v) o.selected = true;
            sexSel.appendChild(o);
        });
        sexSel.addEventListener('change', () => {
            state.persons[idx].sex = sexSel.value;
            sync();
            // Re-render this slot's occupation autocomplete if open, so the
            // sex-specific counts (and greying of 0 entries) show at once.
            if (activePopover && activePopover.input === occInput) {
                activePopover.input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        sexTd.appendChild(sexSel);
        tr.appendChild(sexTd);

        // Occupation (optional; substring match, with suggestion list)
        const occTd = document.createElement('td');
        occTd.className = 'qb-col-occ';
        const occInput = document.createElement('input');
        occInput.type = 'text';
        occInput.setAttribute('aria-label',
            'Beruf, Tätigkeit oder Amt Person ' + (idx + 1) + ' (enthält)');
        occInput.placeholder = 'z. B. purger, Bürger, pharrer';
        occInput.value = p.occ || '';
        occInput.addEventListener('input', () => {
            state.persons[idx].occ = occInput.value.trim();
            sync();
        });
        // getContext reads the current sex from state so per-occupation
        // counts can be shown sex-aware.
        attachAutocomplete(occInput, {
            vocab: OCC_VOCAB,
            hint: 'Vorkommen im Korpus',
            getContext: () => ({ sex: (state.persons[idx] || {}).sex || '' }),
            extraVocab: OCC_FULL_VOCAB,
        });
        occTd.appendChild(occInput);
        tr.appendChild(occTd);

        // Uhlirz occupation class (optional; exact category match). Dropdown
        // fed from UHLIRZ_VOCAB; empty default means "any".
        const uhlirzTd = document.createElement('td');
        uhlirzTd.className = 'qb-col-uhlirz';
        const uhlirzSel = document.createElement('select');
        uhlirzSel.setAttribute('aria-label',
            'Uhlirz-Berufsklasse Person ' + (idx + 1));
        const uhlBlank = document.createElement('option');
        uhlBlank.value = '';
        uhlBlank.textContent = '— alle —';
        uhlirzSel.appendChild(uhlBlank);
        UHLIRZ_VOCAB.forEach(cat => {
            const o = document.createElement('option');
            o.value = cat;
            o.textContent = cat;
            if ((p.uhlirz || '') === cat) o.selected = true;
            uhlirzSel.appendChild(o);
        });
        uhlirzSel.addEventListener('change', () => {
            state.persons[idx].uhlirz = uhlirzSel.value;
            sync();
        });
        uhlirzTd.appendChild(uhlirzSel);
        tr.appendChild(uhlirzTd);

        const rmTd = document.createElement('td');
        rmTd.className = 'qb-col-rm';
        const rm = document.createElement('button');
        rm.type = 'button';
        rm.className = 'qb-person-remove';
        rm.setAttribute('aria-label', 'Person ' + (idx + 1) + ' entfernen');
        rm.innerHTML = '&times;';
        rm.addEventListener('click', () => {
            state.persons.splice(idx, 1);
            renderPersonsTable();
            sync();
        });
        rmTd.appendChild(rm);
        tr.appendChild(rmTd);

        return tr;
    }

    function renderPersonsTable() {
        personsTbody.innerHTML = '';
        state.persons.forEach((p, idx) => {
            personsTbody.appendChild(renderPersonRow(idx, p));
        });
        // Hide the table when it has no rows; the header alone looks empty.
        personsTable.classList.toggle('is-empty', state.persons.length === 0);
    }

    function renderOrgRow(idx, o) {
        const tr = document.createElement('tr');
        tr.className = 'qb-org-row';
        tr.dataset.orgIdx = idx;

        const numTd = document.createElement('td');
        numTd.className = 'qb-col-num';
        const numSpan = document.createElement('span');
        numSpan.className = 'qb-org-num';
        numSpan.textContent = idx + 1;
        numTd.appendChild(numSpan);
        tr.appendChild(numTd);

        const roleTd = document.createElement('td');
        roleTd.className = 'qb-col-role';
        const roleSel = document.createElement('select');
        roleSel.className = 'qb-org-role';
        roleSel.setAttribute('aria-label', 'Rolle Organisation ' + (idx + 1));
        const blank = document.createElement('option');
        blank.value = '';
        blank.textContent = '— beliebige Rolle —';
        roleSel.appendChild(blank);
        ROLE_LIST.forEach(r => {
            const op = document.createElement('option');
            op.value = r;
            op.textContent = ROLE_LABELS_PLURAL[r];
            if (o.role === r) op.selected = true;
            roleSel.appendChild(op);
        });
        roleSel.addEventListener('change', () => {
            state.orgs[idx].role = roleSel.value;
            sync();
        });
        roleTd.appendChild(roleSel);
        tr.appendChild(roleTd);

        // Name (substring) with autocomplete
        const nameTd = document.createElement('td');
        nameTd.className = 'qb-col-org-name';
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.setAttribute('aria-label',
            'Name Organisation ' + (idx + 1) + ' (enthält)');
        nameInput.placeholder = 'z. B. Himmelpforte, Stephan, Klosterneuburg';
        nameInput.value = o.name || '';
        nameInput.addEventListener('input', () => {
            state.orgs[idx].name = nameInput.value.trim();
            sync();
        });
        // ORG_FULL_VOCAB is essential here: for type filters like "Gemeinde"
        // all matches sit outside the top-50, so without extraVocab the list
        // would be fully greyed out.
        attachAutocomplete(nameInput, {
            vocab: ORG_VOCAB,
            hint: 'Vorkommen im Korpus',
            getContext: () => ({ orgType: (state.orgs[idx] || {}).type || '' }),
            extraVocab: ORG_FULL_VOCAB,
        });
        nameTd.appendChild(nameInput);
        tr.appendChild(nameTd);

        const typeTd = document.createElement('td');
        typeTd.className = 'qb-col-org-type';
        const typeSel = document.createElement('select');
        typeSel.setAttribute('aria-label',
            'Typ Organisation ' + (idx + 1));
        const tBlank = document.createElement('option');
        tBlank.value = '';
        tBlank.textContent = '— alle —';
        typeSel.appendChild(tBlank);
        ORG_TYPE_VOCAB.forEach(t => {
            const op = document.createElement('option');
            op.value = t;
            op.textContent = t;
            if ((o.type || '') === t) op.selected = true;
            typeSel.appendChild(op);
        });
        typeSel.addEventListener('change', () => {
            state.orgs[idx].type = typeSel.value;
            sync();
            // Re-render this slot's name autocomplete if open, so type-matching
            // names move to the top and non-matching ones grey out.
            if (activePopover && activePopover.input === nameInput) {
                activePopover.input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
        typeTd.appendChild(typeSel);
        tr.appendChild(typeTd);

        const rmTd = document.createElement('td');
        rmTd.className = 'qb-col-rm';
        const rm = document.createElement('button');
        rm.type = 'button';
        rm.className = 'qb-org-remove';
        rm.setAttribute('aria-label', 'Organisation ' + (idx + 1) + ' entfernen');
        rm.innerHTML = '&times;';
        rm.addEventListener('click', () => {
            state.orgs.splice(idx, 1);
            renderOrgsTable();
            sync();
        });
        rmTd.appendChild(rm);
        tr.appendChild(rmTd);

        return tr;
    }

    function renderOrgsTable() {
        if (!orgsTbody) return;
        orgsTbody.innerHTML = '';
        state.orgs.forEach((o, idx) => {
            orgsTbody.appendChild(renderOrgRow(idx, o));
        });
        if (orgsTable) {
            orgsTable.classList.toggle('is-empty', state.orgs.length === 0);
        }
    }

    addPersonBtn.addEventListener('click', () => {
        state.persons.push({ role: '', sex: '', occ: '', uhlirz: '' });
        renderPersonsTable();
        sync();
    });

    if (addOrgBtn) {
        addOrgBtn.addEventListener('click', () => {
            state.orgs.push({ role: '', name: '', type: '' });
            renderOrgsTable();
            sync();
        });
    }

    scopeChips.forEach(chip => {
        chip.addEventListener('click', () => {
            scopeChips.forEach(c => {
                c.classList.remove('is-active');
                c.setAttribute('aria-pressed', 'false');
            });
            chip.classList.add('is-active');
            chip.setAttribute('aria-pressed', 'true');
            state.scope = chip.dataset.scope;
            sync();
        });
    });

    if (corpusChecksRoot) {
        corpusChecksRoot.querySelectorAll('input[data-corpus]').forEach(cb => {
            cb.addEventListener('change', () => {
                const key = cb.dataset.corpus;
                if (cb.checked) state.corpora.add(key);
                else state.corpora.delete(key);
                const label = cb.closest('label');
                if (label) label.classList.toggle('is-active', cb.checked);
                sync();
            });
        });
    }

    resetBtn.addEventListener('click', () => {
        state.persons = [];
        state.orgs = [];
        state.scope = 'event';
        state.corpora = new Set(ALL_CORPORA);
        scopeChips.forEach(c => {
            const isDefault = c.dataset.scope === 'event';
            c.classList.toggle('is-active', isDefault);
            c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
        });
        if (corpusChecksRoot) {
            corpusChecksRoot.querySelectorAll('input[data-corpus]')
                .forEach(cb => {
                    cb.checked = true;
                    const label = cb.closest('label');
                    if (label) label.classList.add('is-active');
                });
        }
        renderPersonsTable();
        renderOrgsTable();
        sync();
    });

    function eventInCorpus(ev) {
        if (!state.corpora.size) return false;
        return state.corpora.has(ev.c);
    }

    function personMatchesCard(person, card) {
        if (card.role && person.r !== card.role) return false;
        if (card.sex) {
            const s = person.s || '';
            if (card.sex === 'u' ? (s !== '') : (s !== card.sex)) return false;
        }
        if (card.occ) {
            const needle = card.occ.toLowerCase();
            const hit = (person.o || []).some(o => (o || '').toLowerCase().includes(needle));
            if (!hit) return false;
        }
        if (card.uhlirz) {
            const cats = person.u || [];
            if (cats.indexOf(card.uhlirz) === -1) return false;
        }
        return true;
    }

    function orgMatchesCard(org, card) {
        if (card.role && org.r !== card.role) return false;
        if (card.name) {
            const needle = card.name.toLowerCase();
            if (!(org.n || '').toLowerCase().includes(needle)) return false;
        }
        if (card.type && (org.tp || '') !== card.type) return false;
        return true;
    }

    // Assign each active card a distinct participant within the event (no
    // person used twice). Returns the assigned participants in card order, or
    // null if assignment fails.
    function assignParticipants(ev, cards) {
        const used = new Set();
        const out = [];
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            let found = null;
            for (let j = 0; j < ev.p.length; j++) {
                if (used.has(j)) continue;
                if (personMatchesCard(ev.p[j], card)) { found = j; break; }
            }
            if (found == null) return null;
            used.add(found);
            out.push(ev.p[found]);
        }
        return out;
    }

    function assignOrgs(ev, cards) {
        const list = ev.og || [];
        const used = new Set();
        const out = [];
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            let found = null;
            for (let j = 0; j < list.length; j++) {
                if (used.has(j)) continue;
                if (orgMatchesCard(list[j], card)) { found = j; break; }
            }
            if (found == null) return null;
            used.add(found);
            out.push(list[found]);
        }
        return out;
    }

    // Every added card counts as an active condition, even with all slots
    // empty: clicking "+" asserts "I am searching for a person/org here". An
    // empty card matches any person/org, giving the trivial "all events with
    // at least N participants" case.
    function activeCards() {
        return state.persons.slice();
    }
    function activeOrgCards() {
        return state.orgs.slice();
    }

    function compute() {
        const cards = activeCards();
        const orgCards = activeOrgCards();
        if (!DATA || (!cards.length && !orgCards.length)) {
            return { hits: [], cards: cards, orgCards: orgCards };
        }
        const events = DATA.events || [];

        if (state.scope === 'event') {
            // Narrow: the constellation must hold within the same event.
            const hits = [];
            for (const ev of events) {
                if (!eventInCorpus(ev)) continue;
                const assignedP = cards.length ? assignParticipants(ev, cards) : [];
                if (cards.length && !assignedP) continue;
                const assignedO = orgCards.length ? assignOrgs(ev, orgCards) : [];
                if (orgCards.length && !assignedO) continue;
                hits.push({
                    ev: ev,
                    persons: assignedP || [],
                    orgs: assignedO || []
                });
            }
            return { hits: hits, cards: cards, orgCards: orgCards };
        }

        // Wide: all conditions must be jointly satisfiable within the same
        // source (file_key), not necessarily within the same event.
        const byFile = new Map();
        for (const ev of events) {
            if (!eventInCorpus(ev)) continue;
            if (!byFile.has(ev.f)) byFile.set(ev.f, []);
            byFile.get(ev.f).push(ev);
        }
        const hits = [];
        for (const [fk, evs] of byFile.entries()) {
            const allP = [];
            const allO = [];
            for (const ev of evs) {
                for (const p of ev.p) allP.push(p);
                for (const o of (ev.og || [])) allO.push(o);
            }
            const pseudo = {
                e: evs[0].e, f: fk, c: evs[0].c,
                d: evs[0].d, tx: evs[0].tx, p: allP, og: allO
            };
            const assignedP = cards.length ? assignParticipants(pseudo, cards) : [];
            if (cards.length && !assignedP) continue;
            const assignedO = orgCards.length ? assignOrgs(pseudo, orgCards) : [];
            if (orgCards.length && !assignedO) continue;
            hits.push({
                ev: pseudo,
                persons: assignedP || [],
                orgs: assignedO || []
            });
        }
        return { hits: hits, cards: cards, orgCards: orgCards };
    }

    function renderHits(result) {
        const { hits, cards, orgCards } = result;
        const totalCards = cards.length + (orgCards ? orgCards.length : 0);
        const onboarding = root.querySelector('#qb-onboarding');
        tbody.innerHTML = '';
        if (!totalCards) {
            emptyBox.classList.remove('hidden');
            emptyMsg.textContent = 'Person oder Organisation hinzufügen oder Beispiel wählen.';
            if (onboarding) onboarding.classList.remove('hidden');
            if (resultsToolbar) resultsToolbar.hidden = true;
            if (hitsTable) hitsTable.hidden = true;
            csvBtn.setAttribute('disabled', '');
            return;
        }
        if (!hits.length) {
            emptyBox.classList.remove('hidden');
            emptyMsg.textContent = 'Keine Treffer. Bedingung lockern oder Korpus erweitern.';
            if (onboarding) onboarding.classList.add('hidden');
            if (resultsToolbar) resultsToolbar.hidden = false;
            if (hitsTable) hitsTable.hidden = true;
            hitsSrc.textContent = '0';
            hitsEv.textContent = '0';
            csvBtn.setAttribute('disabled', '');
            return;
        }
        emptyBox.classList.add('hidden');
        if (onboarding) onboarding.classList.add('hidden');
        if (resultsToolbar) resultsToolbar.hidden = false;
        if (hitsTable) hitsTable.hidden = false;

        const sourceKeys = new Set();
        const eventKeys = new Set();
        for (const h of hits) {
            sourceKeys.add(h.ev.f);
            eventKeys.add(h.ev.e);
        }
        hitsSrc.textContent = fmt(sourceKeys.size);
        hitsEv.textContent  = fmt(eventKeys.size);
        csvBtn.removeAttribute('disabled');
        if (hits.length > 500) {
            csvBtn.setAttribute('title',
                'Tabelle zeigt 500 von ' + fmt(hits.length) + ' Treffern. ' +
                'CSV enthaelt alle.');
        } else {
            csvBtn.removeAttribute('title');
        }

        sortHits(hits);

        const frag = document.createDocumentFragment();
        const limit = 500;
        for (let i = 0; i < Math.min(hits.length, limit); i++) {
            frag.appendChild(buildRow(hits[i], cards, orgCards || []));
        }
        if (hits.length > limit) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 5 + 1;
            td.style.textAlign = 'center';
            td.style.color = 'var(--color-text-light)';
            td.style.fontStyle = 'italic';
            td.textContent =
                '… ' + fmt(hits.length - limit) + ' weitere Treffer ' +
                'werden nicht in der Tabelle dargestellt. CSV-Download enthält alle.';
            tr.appendChild(td);
            frag.appendChild(tr);
        }
        tbody.appendChild(frag);
    }

    function buildPersonPill(p, num) {
        // num=null -> context participant, no number pill and toned down;
        // num>=1 -> condition hit, highlighted.
        const pill = document.createElement('span');
        pill.className = 'person-pill' + (num == null ? ' is-context' : '');
        const tipParts = [p.n || p.p];
        if (p.nt) tipParts.push(p.nt);
        pill.title = tipParts.join('\n');
        if (num != null) {
            const numEl = document.createElement('span');
            numEl.className = 'person-pill-num';
            numEl.textContent = num;
            pill.appendChild(numEl);
        }
        const a = document.createElement('a');
        a.href = '../register/persons/' + encodeURIComponent(p.p) + '.html';
        a.textContent = p.n || p.p;
        pill.appendChild(a);
        const role = (p.r && ROLE_LABELS[p.r]) || '';
        if (role) {
            const r = document.createElement('span');
            r.className = 'person-pill-role';
            r.textContent = role;
            pill.appendChild(r);
        }
        if (p.s === 'm' || p.s === 'f') {
            const s = document.createElement('span');
            s.className = 'person-pill-sex person-pill-sex--' + p.s;
            s.textContent = p.s === 'f' ? 'weiblich' : 'maennlich';
            pill.appendChild(s);
        }
        return pill;
    }

    function buildOrgPill(o, num) {
        const pill = document.createElement('span');
        pill.className = 'org-pill' + (num == null ? ' is-context' : '');
        const tipParts = [o.n || o.g];
        if (o.tp) tipParts.push('Typ: ' + o.tp);
        pill.title = tipParts.join('\n');
        if (num != null) {
            const numEl = document.createElement('span');
            numEl.className = 'org-pill-num';
            numEl.textContent = num;
            pill.appendChild(numEl);
        }
        const a = document.createElement('a');
        a.href = '../register/orgs/' + encodeURIComponent(o.g) + '.html';
        a.textContent = o.n || o.g;
        pill.appendChild(a);
        const role = (o.r && ROLE_LABELS[o.r]) || '';
        if (role) {
            const r = document.createElement('span');
            r.className = 'org-pill-role';
            r.textContent = role;
            pill.appendChild(r);
        }
        return pill;
    }

    function buildRow(hit, cards, orgCards) {
        const tr = document.createElement('tr');
        const ev = hit.ev;

        td(tr, formatDate(ev.d), 'col-date');

        const sourceTd = document.createElement('td');
        sourceTd.className = 'col-idno';
        const srcA = document.createElement('a');
        srcA.href = docUrl(ev.f);
        srcA.textContent = docIdno(ev.f);
        sourceTd.appendChild(srcA);
        tr.appendChild(sourceTd);

        td(tr, ev.c, 'col-corpus');

        // Participants: issuers always shown (rarely many, almost always 1-4).
        // Recipients shown but capped: beyond RECIPIENT_LIMIT per entity type
        // the surplus moves into the "+N weitere" expander, where all
        // witnesses/sealers and other participants also land. Condition hits
        // (number pill) are ALWAYS visible, regardless of role or position.
        const personsTd = document.createElement('td');
        personsTd.className = 'col-persons';

        const RECIPIENT_LIMIT = 4;

        // Index: which person/org is a condition hit? Order follows the
        // condition rows 1..N.
        const personHitIdx = new Map();
        hit.persons.forEach((p, idx) => personHitIdx.set(p.p, idx + 1));
        const orgHitIdx = new Map();
        (hit.orgs || []).forEach((o, idx) => orgHitIdx.set(o.g, idx + 1));

        const allPersons = ev.p || [];
        const allOrgs = ev.og || [];

        // Split per entity type into condition hits, issuers, recipients and
        // rest. Condition hits are kept out of the other buckets so they do
        // not appear twice.
        function partition(items, getId, hitMap) {
            const hits = [], issuers = [], recipients = [], rest = [];
            for (const it of items) {
                if (hitMap.has(getId(it))) { hits.push(it); continue; }
                if (it.r === 'issuer') issuers.push(it);
                else if (it.r === 'recipient') recipients.push(it);
                else rest.push(it);
            }
            return { hits, issuers, recipients, rest };
        }
        const pp = partition(allPersons, p => p.p, personHitIdx);
        const oo = partition(allOrgs, o => o.g, orgHitIdx);

        // Visible: condition hits + all issuers + first RECIPIENT_LIMIT
        // recipients. Hidden: surplus recipients + everything in other roles.
        const visiblePersons = [
            ...pp.hits, ...pp.issuers,
            ...pp.recipients.slice(0, RECIPIENT_LIMIT)
        ];
        const hiddenPersons = [
            ...pp.recipients.slice(RECIPIENT_LIMIT), ...pp.rest
        ];
        const visibleOrgs = [
            ...oo.hits, ...oo.issuers,
            ...oo.recipients.slice(0, RECIPIENT_LIMIT)
        ];
        const hiddenOrgs = [
            ...oo.recipients.slice(RECIPIENT_LIMIT), ...oo.rest
        ];

        visiblePersons.forEach(p => personsTd.appendChild(
            buildPersonPill(p, personHitIdx.get(p.p) || null)));
        visibleOrgs.forEach(o => personsTd.appendChild(
            buildOrgPill(o, orgHitIdx.get(o.g) || null)));

        const hiddenCount = hiddenPersons.length + hiddenOrgs.length;
        if (hiddenCount > 0) {
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'col-persons-more';
            toggle.textContent = '+' + hiddenCount + ' weitere';
            toggle.setAttribute('aria-expanded', 'false');
            personsTd.appendChild(toggle);

            const more = document.createElement('span');
            more.className = 'col-persons-more-pills';
            more.hidden = true;
            hiddenPersons.forEach(p => more.appendChild(buildPersonPill(p, null)));
            hiddenOrgs.forEach(o => more.appendChild(buildOrgPill(o, null)));
            personsTd.appendChild(more);

            toggle.addEventListener('click', () => {
                const open = !more.hidden ? false : true;
                more.hidden = !open;
                toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
                toggle.textContent = open
                    ? 'weniger anzeigen'
                    : '+' + hiddenCount + ' weitere';
            });
        }

        tr.appendChild(personsTd);

        td(tr, ev.tx || '', 'col-tx');

        const basketTd = document.createElement('td');
        basketTd.className = 'col-basket';
        if (window.DataBasket && DataBasket.buttonHTML) {
            basketTd.innerHTML = DataBasket.buttonHTML({
                type: 'source',
                id: ev.f,
                label: docIdno(ev.f),
                url: docUrl(ev.f),
                date: ev.d,
                coll: ev.c,
                regest: ''
            });
        }
        tr.appendChild(basketTd);

        return tr;
    }

    function td(tr, text, cls) {
        const el = document.createElement('td');
        if (cls) el.className = cls;
        el.textContent = text;
        tr.appendChild(el);
        return el;
    }

    function formatDate(s) {
        // "1342-04-08" -> "8. Apr 1342". Entries without a single date have an
        // empty d-value, shown as "—"; year-only dates stay as the year.
        // Sorting happens separately over the ISO string, not this display form.
        const t = (s || '').trim();
        if (!t) return '—';
        const m = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$/.exec(t);
        if (!m) return t;
        const year = m[1];
        const mon = m[2] && parseInt(m[2], 10);
        const day = m[3] && parseInt(m[3], 10);
        const MONTHS_DE = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
        if (day && mon)  return day + '. ' + MONTHS_DE[mon - 1] + ' ' + year;
        if (mon)         return MONTHS_DE[mon - 1] + ' ' + year;
        return year;
    }

    // Stable sort key for hits. Returns a string whose lexicographic order
    // yields the desired result; empty values sort last (via '~' prefix).
    function hitSortKey(hit, key) {
        const ev = hit.ev;
        if (key === 'date') {
            const d = (ev.d || '').trim();
            return d ? d : '~';
        }
        if (key === 'source') return docIdno(ev.f).toString().toLowerCase();
        if (key === 'corpus') return (ev.c || '').toLowerCase();
        if (key === 'tx')     {
            const t = (ev.tx || '').trim();
            return t ? t.toLowerCase() : '~';
        }
        return '';
    }
    function sortHits(hits) {
        const k = state.sortKey;
        const dir = state.sortDir;
        hits.sort((a, b) => {
            const ka = hitSortKey(a, k), kb = hitSortKey(b, k);
            if (ka < kb) return -1 * dir;
            if (ka > kb) return 1 * dir;
            // Tiebreaker on source so the order stays stable.
            return a.ev.f.localeCompare(b.ev.f);
        });
    }

    function fmt(n) {
        return n.toLocaleString('de-DE');
    }

    // Corpus selection is deliberately not duplicated: the checkboxes above
    // are the single source of truth, an extra "Korpus: …" pill would be
    // redundant.
    function renderActiveFilters() {
        if (!activeStrip || !window.VizCore) return;
        const pieces = [];
        if (state.scope !== 'event') {
            pieces.push({
                label: 'gemeinsam in: ' + (state.scope === 'source' ? 'Quelle' : 'Rechtsgeschäft'),
                onClear: () => {
                    state.scope = 'event';
                    scopeChips.forEach(c => {
                        const isDefault = c.dataset.scope === 'event';
                        c.classList.toggle('is-active', isDefault);
                        c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
                    });
                    sync();
                },
            });
        }
        window.VizCore.renderActiveFilters(activeStrip.id, pieces);
    }

    // Pure serialization/parsing lives in analysis-url.js (window.AnalysisURL)
    // so round-trip tests can run without a DOM. Here only DOM sync.
    function writeUrl() {
        const snapshot = {
            persons: state.persons,
            orgs: state.orgs,
            scope: state.scope,
            corpora: Array.from(state.corpora),
        };
        const body = window.AnalysisURL.serializeQueryState(snapshot, ALL_CORPORA);
        const hash = body ? '#' + body : '';
        if (window.location.hash !== hash) {
            history.replaceState(null, '',
                window.location.pathname + window.location.search + hash);
        }
    }

    function readUrl() {
        const parsed = window.AnalysisURL.parseQueryHash(window.location.hash);
        if (!parsed.persons.length && !parsed.orgs.length
            && parsed.corpora === null && parsed.scope === 'event') {
            return;
        }
        if (parsed.persons.length) state.persons = parsed.persons;
        if (parsed.orgs.length) state.orgs = parsed.orgs;
        if (parsed.corpora) {
            // Explicit corpus selection from the URL overrides the all-default;
            // sync the checkboxes accordingly.
            state.corpora.clear();
            parsed.corpora.forEach(c => state.corpora.add(c));
            if (corpusChecksRoot) {
                corpusChecksRoot.querySelectorAll('input[data-corpus]')
                    .forEach(cb => {
                        const on = state.corpora.has(cb.dataset.corpus);
                        cb.checked = on;
                        const label = cb.closest('label');
                        if (label) label.classList.toggle('is-active', on);
                    });
            }
        }
        if (parsed.scope && parsed.scope !== state.scope) {
            state.scope = parsed.scope;
            scopeChips.forEach(c => {
                const active = c.dataset.scope === state.scope;
                c.classList.toggle('is-active', active);
                c.setAttribute('aria-pressed', active ? 'true' : 'false');
            });
        }
    }

    function csvEscape(s) {
        const str = (s == null) ? '' : String(s);
        if (/[",;\n]/.test(str)) return '"' + str.replace(/"/g, '""') + '"';
        return str;
    }

    function downloadCsv() {
        const result = compute();
        if (!result.hits.length) return;
        // Same sort as the table so the CSV mirrors what is on screen.
        sortHits(result.hits);
        const orgCards = result.orgCards || [];
        const headers = ['Datum', 'Quelle', 'Korpus'];
        for (let i = 1; i <= result.cards.length; i++) headers.push('Person ' + i);
        for (let i = 1; i <= orgCards.length; i++) headers.push('Organisation ' + i);
        headers.push('Rechtsgeschäft');
        const lines = [headers.map(csvEscape).join(';')];
        for (const h of result.hits) {
            const row = [
                h.ev.d || '',
                docIdno(h.ev.f),
                h.ev.c || '',
                ...h.persons.map(p => p.n || p.p || ''),
                ...(h.orgs || []).map(o => o.n || o.g || ''),
                h.ev.tx || ''
            ];
            lines.push(row.map(csvEscape).join(';'));
        }
        // BOM for Excel compatibility
        const blob = new Blob(['﻿' + lines.join('\n')],
            { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const today = new Date().toISOString().slice(0, 10);
        a.download = 'abfrage_' + today + '.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
    }

    csvBtn.addEventListener('click', () => {
        if (!csvBtn.hasAttribute('disabled')) downloadCsv();
    });

    // Entries may carry person and org conditions. Format:
    //   { persons: [ {role, sex, occ, uhlirz} ], orgs: [ {role, name, type} ] }
    // The old form (flat array) is kept for compatibility with persons-only
    // examples.
    const EXAMPLES = {
        'women-issuers': [
            { role: 'issuer', sex: 'f', occ: '' }
        ],
        'women-issuers-men-recipients': [
            { role: 'issuer',    sex: 'f', occ: '' },
            { role: 'recipient', sex: 'm', occ: '' }
        ],
        'burger-recipients': [
            { role: 'recipient', sex: '', occ: 'urger' }
        ],
        'clergy-pair': [
            { role: 'issuer',    sex: '', occ: 'pfarr' },
            { role: 'recipient', sex: '', occ: 'pfarr' }
        ],
        'verwaltung': [
            { role: 'issuer', sex: '', occ: '', uhlirz: 'XVIII Verwaltung' }
        ],
        'org-st-agnes': {
            persons: [],
            orgs: [
                { role: 'recipient', name: 'St. Agnes', type: '' }
            ]
        }
    };

    function applyExample(key) {
        const tpl = EXAMPLES[key];
        if (!tpl) return;
        // Persons list from tpl.persons (new form) or tpl itself (old form).
        const personsTpl = Array.isArray(tpl) ? tpl : (tpl.persons || []);
        const orgsTpl = Array.isArray(tpl) ? [] : (tpl.orgs || []);
        state.persons = personsTpl.map(p => ({
            role: p.role || '', sex: p.sex || '',
            occ: p.occ || '', uhlirz: p.uhlirz || ''
        }));
        state.orgs = orgsTpl.map(o => ({
            role: o.role || '', name: o.name || '', type: o.type || ''
        }));
        renderPersonsTable();
        renderOrgsTable();
        sync();
        // Scroll to the persons table so the user sees what was set.
        personsTable.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    root.querySelectorAll('.qb-example').forEach(btn => {
        btn.addEventListener('click', () => applyExample(btn.dataset.example));
    });

    function sync() {
        writeUrl();
        renderActiveFilters();
        loadData().then(() => {
            renderHits(compute());
        }).catch(() => {/* loadData already set the error text */});
    }

    // Reset the whole query state to default, then read the current URL hash.
    // Called on initial boot and on every hashchange, so permalinks always
    // produce a clean state instead of carrying over remnants of prior hashes.
    function resetStateFromUrl() {
        state.persons = [];
        state.orgs = [];
        state.scope = 'event';
        state.corpora = new Set(ALL_CORPORA);
        scopeChips.forEach(c => {
            const isDefault = c.dataset.scope === 'event';
            c.classList.toggle('is-active', isDefault);
            c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
        });
        if (corpusChecksRoot) {
            corpusChecksRoot.querySelectorAll('input[data-corpus]')
                .forEach(cb => {
                    cb.checked = true;
                    const label = cb.closest('label');
                    if (label) label.classList.add('is-active');
                });
        }
        readUrl();
        renderPersonsTable();
        renderOrgsTable();
    }

    // Has the user diverged from the default state?
    // Default = no persons/orgs, scope=event, all corpora active.
    function hasNonDefaultState() {
        return state.persons.length > 0 ||
               state.orgs.length > 0 ||
               state.scope !== 'event' ||
               state.corpora.size !== ALL_CORPORA.length;
    }

    window.addEventListener('hashchange', () => {
        resetStateFromUrl();
        if (hasNonDefaultState()) {
            sync();
        } else {
            renderActiveFilters();
            renderHits({ hits: [], cards: [], orgCards: [] });
        }
    });

    // Headers carry data-sort="date|source|corpus|tx". A click switches the
    // sort key; clicking the same column again flips the direction. Visual
    // feedback via aria-sort and sorted-asc/sorted-desc classes, already
    // styled by the global table CSS.
    if (hitsTable) {
        const sortHeaders = hitsTable.querySelectorAll('th[data-sort]');
        function refreshSortIndicators() {
            sortHeaders.forEach(h => {
                h.classList.remove('sorted-asc', 'sorted-desc');
                h.setAttribute('aria-sort', 'none');
                if (h.dataset.sort === state.sortKey) {
                    h.classList.add(state.sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
                    h.setAttribute('aria-sort',
                        state.sortDir === 1 ? 'ascending' : 'descending');
                }
            });
        }
        sortHeaders.forEach(th => {
            th.addEventListener('click', e => {
                // Ignore clicks on tip triggers; they open the glossary
                // popover, a separate interaction path.
                if (e.target.closest('.tip-trigger, .tip-popover')) return;
                const key = th.dataset.sort;
                if (state.sortKey === key) state.sortDir *= -1;
                else { state.sortKey = key; state.sortDir = 1; }
                refreshSortIndicators();
                if (DATA) renderHits(compute());
            });
        });
        refreshSortIndicators();
    }

    readUrl();
    renderPersonsTable();
    renderOrgsTable();
    // Load data only on the first sync; the initial render shows an empty table.
    if (hasNonDefaultState()) {
        sync();
    } else {
        // No state from URL: render only the UI state, load no data.
        renderActiveFilters();
        renderHits({ hits: [], cards: [], orgCards: [] });
    }

})();
