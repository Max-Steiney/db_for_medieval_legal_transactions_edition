// Exploration / person network: Ego-layout around a single person.
// Pick a person (search or suggestion click) -> that person sits in the
// center, their direct connections (filtered by relation type) are arranged
// radially around it. Clicking a neighbor person moves the center.
(function () {
    'use strict';

    const V = VizCore;

    const REL_LABELS = V.REL_LABELS;        // {kin, occ, rep, friend}
    const REL_COLORS = V.REL_COLORS;
    const REL_ORDER  = V.REL_ORDER;

    // Sex colors for person nodes (from tokens.css).
    const SEX_COLORS = {
        m: '#5d3a74',
        f: '#2d6650',
        unspecified: '#9a9590',
    };

    // ---------------------------------------------------------------------
    // Load data + build index
    // ---------------------------------------------------------------------
    const EPIC_B = V.readJsonScript('network-data-epic-b', { persons: [] });
    let DOCS_LOOKUP = {};

    // PERSONS: id -> {id, name, sex, rels[]}
    // ORGS:    id -> name (orgs appear as occ targets; they have no own record)
    const PERSONS = new Map();
    const ORGS = new Map();
    // Edge index: pid -> [{otherKey, otherIsOrg, type, label, sourceKeys: [fk]}]
    const EDGE_INDEX = new Map();

    function buildIndex() {
        for (const p of EPIC_B.persons || []) {
            PERSONS.set(p.id, p);
        }
        for (const p of EPIC_B.persons || []) {
            const edges = new Map();    // (other|type) -> {otherKey, type, labels[], sourceKeys[]}
            for (const r of p.rels || []) {
                const t = r.t;
                const other = r.r || '';
                if (!other) continue;
                const isOrg = other.startsWith('org__');
                const key = other + '|' + t;
                if (!edges.has(key)) {
                    edges.set(key, {
                        otherKey: other,
                        otherIsOrg: isOrg,
                        type: t,
                        labels: [],
                        sourceKeys: [],
                    });
                }
                const e = edges.get(key);
                if (r.l && !e.labels.includes(r.l)) e.labels.push(r.l);
                if (r.f && !e.sourceKeys.includes(r.f)) e.sourceKeys.push(r.f);
                // Remember org entry for display name.
                if (isOrg && !ORGS.has(other)) {
                    // Org key has form "org__alias" — use as readable label.
                    ORGS.set(other, prettifyOrg(other));
                }
            }
            EDGE_INDEX.set(p.id, Array.from(edges.values()));
        }
    }

    function prettifyOrg(orgKey) {
        return V.labelize(orgKey.replace(/^org__/, ''));
    }

    function getPerson(id)  { return PERSONS.get(id); }
    function getOrgName(id) { return ORGS.get(id) || prettifyOrg(id); }
    function getEdges(pid)  { return EDGE_INDEX.get(pid) || []; }
    function getEdgeCount(pid) { return getEdges(pid).length; }

    // ---------------------------------------------------------------------
    // Filter state
    // ---------------------------------------------------------------------
    const STATE = {
        center: null,            // pid or null (= suggestion mode)
        types: new Set(REL_ORDER),
    };

    function activeEdges(pid) {
        return getEdges(pid).filter(e => STATE.types.has(e.type));
    }

    // ---------------------------------------------------------------------
    // Suggestions: top-N persons with the most connections
    // ---------------------------------------------------------------------
    function topSuggestions(n) {
        const candidates = [];
        for (const p of PERSONS.values()) {
            const c = activeEdges(p.id).length;
            if (c > 0) candidates.push({ p, c });
        }
        candidates.sort((a, b) => b.c - a.c);
        return candidates.slice(0, n).map(x => x.p);
    }

    // ---------------------------------------------------------------------
    // SVG renderer (inline, no external lib)
    // ---------------------------------------------------------------------
    const W = 720, H = 520, CX = W / 2, CY = H / 2;
    const RADIUS_NEIGHBOR = 200;

    function nodeRadius(edgeCount) {
        // 8..22px, smoothly monotonic with number of relations.
        return Math.min(22, Math.max(8, 8 + Math.sqrt(edgeCount) * 2.5));
    }

    function nodeColor(person) {
        return SEX_COLORS[person.sex] || SEX_COLORS.unspecified;
    }

    function renderEgo(pid) {
        const canvas = document.getElementById('net-canvas');
        const heading = document.getElementById('net-graph-heading');
        const hint = document.getElementById('net-hint');
        const detail = document.getElementById('net-detail');
        if (!canvas) return;

        const center = getPerson(pid);
        if (!center) {
            renderSuggestions();
            return;
        }
        const edges = activeEdges(pid);
        if (heading) {
            heading.innerHTML = `<span class="net-heading-name">${escapeHtml(center.name)}</span>
                <span class="aggregat-quadrant-h2-meta">${V.fmt(edges.length)} Verbindungen
                ${STATE.types.size < REL_ORDER.length ? `· gefiltert auf ${STATE.types.size} Typ(en)` : ''}</span>`;
        }
        if (hint) hint.hidden = true;
        if (detail) detail.hidden = false;

        // Radial layout: distribute neighbors on a circle.
        const N = edges.length;
        const positioned = edges.map((e, i) => {
            const angle = (2 * Math.PI * i / Math.max(N, 1)) - Math.PI / 2;
            return {
                edge: e,
                x: CX + RADIUS_NEIGHBOR * Math.cos(angle),
                y: CY + RADIUS_NEIGHBOR * Math.sin(angle),
            };
        });

        const cR = nodeRadius(edges.length);
        const lines = positioned.map(pos => `<line
            class="net-edge net-edge--${pos.edge.type}"
            x1="${CX}" y1="${CY}" x2="${pos.x.toFixed(1)}" y2="${pos.y.toFixed(1)}"
            stroke="${REL_COLORS[pos.edge.type] || '#888'}"
            stroke-width="${1 + Math.min(pos.edge.sourceKeys.length, 4)}"
            stroke-opacity="0.55">
            <title>${escapeAttr(REL_LABELS[pos.edge.type] || pos.edge.type)}: ${pos.edge.labels.map(escapeAttr).join(', ') || '(ohne Bezeichnung)'} · ${pos.edge.sourceKeys.length} Beleg(e)</title>
        </line>`).join('');

        const neighborNodes = positioned.map(pos => {
            const e = pos.edge;
            const isOrg = e.otherIsOrg;
            const other = isOrg ? null : getPerson(e.otherKey);
            const name = isOrg ? getOrgName(e.otherKey) : (other ? other.name : e.otherKey);
            const r = isOrg ? 8 : nodeRadius(getEdgeCount(e.otherKey));
            const color = isOrg ? '#a08470' : nodeColor(other || { sex: 'unspecified' });
            const dataAttr = isOrg
                ? `data-org="${escapeAttr(e.otherKey)}"`
                : `data-pid="${escapeAttr(e.otherKey)}"`;
            return `<g class="net-node ${isOrg ? 'is-org' : 'is-person'}" ${dataAttr}>
                <circle cx="${pos.x.toFixed(1)}" cy="${pos.y.toFixed(1)}" r="${r}"
                        fill="${color}" stroke="white" stroke-width="2"/>
                <text x="${pos.x.toFixed(1)}" y="${(pos.y + r + 12).toFixed(1)}"
                      text-anchor="middle" class="net-node-label">${escapeHtml(truncate(name, 24))}</text>
                <title>${escapeAttr(name)}${isOrg ? ' (Organisation)' : ''}</title>
            </g>`;
        }).join('');

        const centerNode = `<g class="net-node net-node--center" data-pid="${escapeAttr(center.id)}">
            <circle cx="${CX}" cy="${CY}" r="${cR + 4}"
                    fill="${nodeColor(center)}" stroke="var(--color-text)" stroke-width="2.5"/>
            <text x="${CX}" y="${(CY + cR + 18).toFixed(1)}" text-anchor="middle"
                  class="net-node-label net-node-label--center">${escapeHtml(center.name)}</text>
            <title>${escapeAttr(center.name)} (Mittelpunkt)</title>
        </g>`;

        canvas.innerHTML = `<svg class="net-svg" viewBox="0 0 ${W} ${H}"
            role="img" aria-label="Personennetzwerk: Ego-Layout um ${escapeAttr(center.name)}">
            ${lines}
            ${neighborNodes}
            ${centerNode}
        </svg>`;

        renderDetailTable(center, edges);
    }

    function renderSuggestions() {
        const canvas = document.getElementById('net-canvas');
        const heading = document.getElementById('net-graph-heading');
        const hint = document.getElementById('net-hint');
        const detail = document.getElementById('net-detail');
        if (!canvas) return;

        if (heading) heading.textContent = 'Vorschläge: Personen mit vielen Verbindungen';
        if (hint) {
            hint.hidden = false;
            hint.textContent = 'Klicke auf eine Person, um ins Netz einzutreten — oder suche links nach einem Namen.';
        }
        if (detail) detail.hidden = true;

        const list = topSuggestions(12);
        const items = list.map(p => {
            const c = activeEdges(p.id).length;
            return `<button type="button" class="net-suggestion-card" data-pid="${escapeAttr(p.id)}">
                <span class="net-suggestion-dot" style="background:${nodeColor(p)}"></span>
                <span class="net-suggestion-name">${escapeHtml(p.name)}</span>
                <span class="net-suggestion-count">${V.fmt(c)} Verb.</span>
            </button>`;
        }).join('');
        canvas.innerHTML = `<div class="net-suggestions">${items}</div>`;
    }

    function renderDetailTable(center, edges) {
        const tbody = document.getElementById('net-detail-tbody');
        const meta = document.getElementById('net-detail-meta');
        const title = document.getElementById('net-detail-title');
        if (!tbody) return;

        if (title) title.textContent = `Verbindungen von ${center.name}`;
        if (meta)  meta.textContent  = `${V.fmt(edges.length)} Eintr${edges.length === 1 ? 'ag' : 'äge'}`;

        // Sort: evidence count descending, then by name.
        const sorted = edges.slice().sort((a, b) => {
            if (b.sourceKeys.length !== a.sourceKeys.length)
                return b.sourceKeys.length - a.sourceKeys.length;
            const an = a.otherIsOrg ? getOrgName(a.otherKey) : (getPerson(a.otherKey) || {}).name || '';
            const bn = b.otherIsOrg ? getOrgName(b.otherKey) : (getPerson(b.otherKey) || {}).name || '';
            return an.localeCompare(bn);
        });

        const rows = sorted.map(e => {
            const isOrg = e.otherIsOrg;
            const other = isOrg ? null : getPerson(e.otherKey);
            const name = isOrg ? getOrgName(e.otherKey) : (other ? other.name : e.otherKey);
            const labels = e.labels.length ? e.labels.map(escapeHtml).join(', ') : '<span class="text-muted-inline">—</span>';
            const nameCell = isOrg
                ? `<span class="net-detail-name net-detail-name--org">${escapeHtml(name)}</span>`
                : `<button type="button" class="net-detail-recenter" data-pid="${escapeAttr(e.otherKey)}"
                       title="Zum Mittelpunkt machen">${escapeHtml(name)}</button>`;
            // Knowledge basket button shows only for person profiles, not for orgs.
            let korbBtn = '';
            if (!isOrg && other && typeof Wissenskorb !== 'undefined') {
                const url = `register/persons/${other.id}.html`;
                korbBtn = Wissenskorb.buttonHTML({
                    type: 'person', id: other.id, label: other.name, url: url,
                    date: '', coll: 'Personenregister', regest: '',
                });
            }
            return `<tr>
                <td class="col-label">${nameCell}</td>
                <td>${escapeHtml(REL_LABELS[e.type] || e.type)}${isOrg ? ' (Org)' : ''}</td>
                <td>${labels}</td>
                <td class="num">${V.fmt(e.sourceKeys.length)}</td>
                <td class="col-actions">${korbBtn}</td>
            </tr>`;
        });
        tbody.innerHTML = rows.join('') ||
            '<tr><td colspan="5" class="aggregat-empty">Keine Verbindungen für die aktive Filterauswahl.</td></tr>';
    }

    // ---------------------------------------------------------------------
    // Search
    // ---------------------------------------------------------------------
    function bindSearch() {
        const input = document.getElementById('net-person-search');
        const results = document.getElementById('net-search-results');
        if (!input || !results) return;
        input.addEventListener('input', () => {
            const q = input.value.trim().toLowerCase();
            if (q.length < 2) { results.innerHTML = ''; results.hidden = true; return; }
            const matches = [];
            for (const p of PERSONS.values()) {
                if (p.name.toLowerCase().includes(q)) {
                    matches.push(p);
                    if (matches.length >= 12) break;
                }
            }
            if (!matches.length) {
                results.innerHTML = '<li class="net-search-empty">Keine Treffer.</li>';
                results.hidden = false;
                return;
            }
            results.innerHTML = matches.map(p => {
                const c = getEdgeCount(p.id);
                return `<li>
                    <button type="button" class="net-search-hit" data-pid="${escapeAttr(p.id)}">
                        <span class="net-search-hit-name">${escapeHtml(p.name)}</span>
                        <span class="net-search-hit-count">${V.fmt(c)} Verb.</span>
                    </button>
                </li>`;
            }).join('');
            results.hidden = false;
        });
        results.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-pid]');
            if (!btn) return;
            const pid = btn.dataset.pid;
            input.value = '';
            results.hidden = true;
            results.innerHTML = '';
            recenter(pid);
        });
    }

    function bindGraphInteraction() {
        const canvas = document.getElementById('net-canvas');
        if (!canvas) return;
        canvas.addEventListener('click', (e) => {
            const node = e.target.closest('[data-pid]');
            if (node) {
                recenter(node.dataset.pid);
                return;
            }
        });
        const detail = document.getElementById('net-detail');
        if (detail) {
            detail.addEventListener('click', (e) => {
                const btn = e.target.closest('.net-detail-recenter[data-pid]');
                if (!btn) return;
                recenter(btn.dataset.pid);
            });
        }
    }

    function bindTypeFilter() {
        const group = document.getElementById('net-type-filter');
        if (!group) return;
        group.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-net-type]');
            if (!btn) return;
            const t = btn.getAttribute('data-net-type');
            if (STATE.types.has(t)) {
                if (STATE.types.size > 1) STATE.types.delete(t);   // keep at least 1 type active
            } else {
                STATE.types.add(t);
            }
            for (const b of group.querySelectorAll('[data-net-type]')) {
                const isOn = STATE.types.has(b.getAttribute('data-net-type'));
                b.classList.toggle('is-active', isOn);
                b.setAttribute('aria-pressed', isOn ? 'true' : 'false');
            }
            renderActive();
            updateActiveFilters();
            writeUrl();
        });
    }

    function bindReset() {
        const btn = document.getElementById('filter-reset');
        if (!btn) return;
        btn.addEventListener('click', () => {
            STATE.center = null;
            STATE.types = new Set(REL_ORDER);
            // Sync type chips visually.
            const group = document.getElementById('net-type-filter');
            if (group) {
                for (const b of group.querySelectorAll('[data-net-type]')) {
                    b.classList.add('is-active');
                    b.setAttribute('aria-pressed', 'true');
                }
            }
            const input = document.getElementById('net-person-search');
            if (input) input.value = '';
            renderActive();
            updateActiveFilters();
            writeUrl();
        });
    }

    function recenter(pid) {
        if (!PERSONS.has(pid)) return;
        STATE.center = pid;
        renderEgo(pid);
        updateActiveFilters();
        writeUrl();
    }

    function renderActive() {
        if (STATE.center && PERSONS.has(STATE.center)) {
            renderEgo(STATE.center);
        } else {
            renderSuggestions();
        }
    }

    // ---------------------------------------------------------------------
    // Active filter strip
    // ---------------------------------------------------------------------
    function updateActiveFilters() {
        const filters = [];
        if (STATE.center && PERSONS.has(STATE.center)) {
            const p = PERSONS.get(STATE.center);
            filters.push({
                label: 'Mittelpunkt: ' + p.name,
                onClear: () => { STATE.center = null; renderActive(); updateActiveFilters(); writeUrl(); },
            });
        }
        if (STATE.types.size < REL_ORDER.length) {
            const labels = Array.from(STATE.types).map(t => REL_LABELS[t] || t).join(', ');
            filters.push({
                label: 'Beziehungstyp: ' + labels,
                onClear: () => {
                    STATE.types = new Set(REL_ORDER);
                    const group = document.getElementById('net-type-filter');
                    if (group) for (const b of group.querySelectorAll('[data-net-type]')) {
                        b.classList.add('is-active');
                        b.setAttribute('aria-pressed', 'true');
                    }
                    renderActive(); updateActiveFilters(); writeUrl();
                },
            });
        }
        V.renderActiveFilters('active-filters', filters);
    }

    // ---------------------------------------------------------------------
    // URL state sync
    // ?p=pe__xxx&types=kin,occ
    // ---------------------------------------------------------------------
    let urlSyncActive = false;

    function writeUrl() {
        if (!urlSyncActive) return;
        const allTypes = STATE.types.size === REL_ORDER.length;
        V.writeUrlState({
            p:     STATE.center,
            types: allTypes ? null : Array.from(STATE.types).join(','),
        });
    }

    function applyUrlState() {
        const u = V.parseUrlState();
        if (u.types) {
            const set = new Set(u.types.split(',').filter(t => REL_ORDER.includes(t)));
            if (set.size > 0) STATE.types = set;
        }
        if (u.p && PERSONS.has(u.p)) STATE.center = u.p;
        // Sync type chips visually.
        const group = document.getElementById('net-type-filter');
        if (group) {
            for (const b of group.querySelectorAll('[data-net-type]')) {
                const isOn = STATE.types.has(b.getAttribute('data-net-type'));
                b.classList.toggle('is-active', isOn);
                b.setAttribute('aria-pressed', isOn ? 'true' : 'false');
            }
        }
    }

    // ---------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------
    function escapeHtml(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function escapeAttr(s) {
        return escapeHtml(s).replace(/"/g, '&quot;');
    }
    function truncate(s, n) {
        return s && s.length > n ? s.slice(0, n - 1) + '…' : (s || '');
    }

    // ---------------------------------------------------------------------
    // Init
    // ---------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', () => {
        buildIndex();
        bindSearch();
        bindGraphInteraction();
        bindTypeFilter();
        bindReset();
        applyUrlState();
        renderActive();
        updateActiveFilters();
        urlSyncActive = true;
        writeUrl();
        V.loadDocsLookup().then(lk => { DOCS_LOOKUP = lk; }).catch(() => {});
    });
})();
