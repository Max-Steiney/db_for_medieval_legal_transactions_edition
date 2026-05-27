// Exploration / Personennetzwerk.
// Akteure sind Personen UND Organisationen. Ego-Layout um einen Akteur;
// Klick auf einen Nachbar-Knoten verlagert das Zentrum, beim Wechsel von
// Person zu Org (oder umgekehrt) wird die Visualisierung passend gespiegelt:
// fuer eine Org rechnen wir aus den Personen-Relationen die Nachbar-
// Personen (occ-, rep-Targets), fuer eine Person die direkten rels.
(function () {
    'use strict';

    const V = VizCore;

    const REL_LABELS = V.REL_LABELS;
    const REL_COLORS = V.REL_COLORS;
    const REL_ORDER  = V.REL_ORDER;

    const SEX_COLORS = {
        m: '#5d3a74',
        f: '#2d6650',
        unspecified: '#9a9590',
    };
    const ORG_COLOR = '#a08470';

    const RELATIONS = V.readJsonScript('network-data-relations', { persons: [] });
    let DOCS_LOOKUP = {};

    // Single actor index: key (pe__... or org__...) -> actor record.
    // kind === 'person' fuer Personen mit sex und rels[]; kind === 'org'
    // fuer Organisationen mit Anzeigenamen aus relations.json::orgs.
    const ACTORS = new Map();
    // Edges pro Akteur: actor_key -> [{otherKey, otherKind, type,
    // labels[], labelsNorm[], sourceKeys[]}]. Fuer Personen direkt aus rels,
    // fuer Orgs als invertierte Spiegel der Personen-Edges.
    const EDGE_INDEX = new Map();

    function buildIndex() {
        for (const p of RELATIONS.persons || []) {
            p._s = EdCore.normForSearch(p.name || '');
            ACTORS.set(p.id, {
                id: p.id, name: p.name, kind: 'person',
                sex: p.sex, _s: p._s,
            });
        }
        for (const o of RELATIONS.orgs || []) {
            ACTORS.set(o.id, {
                id: o.id, name: o.name, kind: 'org',
                _s: EdCore.normForSearch(o.name || ''),
            });
        }
        for (const p of RELATIONS.persons || []) {
            const edges = new Map();
            for (const r of p.rels || []) {
                const t = r.t;
                const other = r.r || '';
                if (!other) continue;
                const otherKind = other.startsWith('org__') ? 'org' : 'person';
                const key = other + '|' + t;
                if (!edges.has(key)) {
                    edges.set(key, {
                        otherKey: other, otherKind, type: t,
                        labels: [], labelsNorm: [], sourceKeys: [],
                    });
                }
                const e = edges.get(key);
                if (r.l && !e.labels.includes(r.l)) e.labels.push(r.l);
                if (r.ln && !e.labelsNorm.includes(r.ln)) e.labelsNorm.push(r.ln);
                if (r.f && !e.sourceKeys.includes(r.f)) e.sourceKeys.push(r.f);
                if (otherKind === 'org' && !ACTORS.has(other)) {
                    const fallback = prettifyOrg(other);
                    ACTORS.set(other, {
                        id: other, name: fallback, kind: 'org',
                        _s: EdCore.normForSearch(fallback),
                    });
                }
            }
            EDGE_INDEX.set(p.id, Array.from(edges.values()));
        }
        // Inverse Edges fuer Orgs: pro Person-Edge, das auf eine Org zeigt,
        // ein Spiegel-Edge mit Person als otherKey unter der Org anlegen.
        const personIds = [];
        for (const a of ACTORS.values()) {
            if (a.kind === 'person') personIds.push(a.id);
        }
        for (const pid of personIds) {
            const edges = EDGE_INDEX.get(pid) || [];
            for (const e of edges) {
                if (e.otherKind !== 'org') continue;
                let orgEdges = EDGE_INDEX.get(e.otherKey);
                if (!orgEdges) {
                    orgEdges = [];
                    EDGE_INDEX.set(e.otherKey, orgEdges);
                }
                orgEdges.push({
                    otherKey: pid, otherKind: 'person', type: e.type,
                    labels: e.labels, labelsNorm: e.labelsNorm,
                    sourceKeys: e.sourceKeys,
                });
            }
        }
    }

    function prettifyOrg(orgKey) {
        return V.labelize(orgKey.replace(/^org__/, ''));
    }

    function getActor(key) { return ACTORS.get(key); }
    function getEdges(key) { return EDGE_INDEX.get(key) || []; }
    function getEdgeCount(key) { return getEdges(key).length; }

    const STATE = {
        center: null,
        types: new Set(REL_ORDER),
    };

    function activeEdges(key) {
        return getEdges(key).filter(e => STATE.types.has(e.type));
    }

    function topSuggestions(n) {
        const candidates = [];
        for (const a of ACTORS.values()) {
            const c = activeEdges(a.id).length;
            if (c > 0) candidates.push({ a, c });
        }
        candidates.sort((x, y) => y.c - x.c);
        return candidates.slice(0, n).map(x => x.a);
    }

    const W = 720, H = 520, CX = W / 2, CY = H / 2;
    const RADIUS_NEIGHBOR = 200;
    // Hub-Akteure (z.B. org__wien mit 725 Verbindungen) wuerden den Ring
    // zu einer unleserlichen Wolke aufblasen. Der Graph ist die Lesart,
    // die Detail-Tabelle die vollstaendige Quelle. Labels werden ab
    // mittlerer Dichte ausgeblendet, sichtbare Knoten ab hoher Dichte
    // gekappt (sortiert nach Quellen-Anzahl, also visuelle Prominenz
    // folgt Beleg-Staerke).
    const MAX_GRAPH_NODES = 48;
    const LABEL_THRESHOLD = 18;

    function nodeRadius(edgeCount) {
        return Math.min(22, Math.max(8, 8 + Math.sqrt(edgeCount) * 2.5));
    }

    function nodeColor(actor) {
        if (!actor) return SEX_COLORS.unspecified;
        if (actor.kind === 'org') return ORG_COLOR;
        return SEX_COLORS[actor.sex] || SEX_COLORS.unspecified;
    }

    function actorDataAttr(actor) {
        return actor.kind === 'org'
            ? `data-org="${escapeAttr(actor.id)}"`
            : `data-pid="${escapeAttr(actor.id)}"`;
    }

    function renderEgo(key) {
        const canvas = document.getElementById('net-canvas');
        const heading = document.getElementById('net-graph-heading');
        const hint = document.getElementById('net-hint');
        if (!canvas) return;

        const center = getActor(key);
        if (!center) {
            renderSuggestions();
            return;
        }
        const edges = activeEdges(key);
        const sortedEdges = edges.slice().sort((a, b) => {
            if (b.sourceKeys.length !== a.sourceKeys.length)
                return b.sourceKeys.length - a.sourceKeys.length;
            const an = (getActor(a.otherKey) || {}).name || a.otherKey;
            const bn = (getActor(b.otherKey) || {}).name || b.otherKey;
            return an.localeCompare(bn);
        });
        const visibleEdges = sortedEdges.slice(0, MAX_GRAPH_NODES);
        const showLabels = visibleEdges.length <= LABEL_THRESHOLD;
        const capped = sortedEdges.length > visibleEdges.length;

        if (heading) {
            const kindBadge = center.kind === 'org' ? ' <span class="net-heading-kind">(Organisation)</span>' : '';
            const capNote = capped
                ? ` · im Graph die ${visibleEdges.length} quellenstärksten`
                : '';
            const filterNote = STATE.types.size < REL_ORDER.length
                ? ` · gefiltert auf ${STATE.types.size} Typ(en)`
                : '';
            heading.innerHTML = `<span class="net-heading-name">${escapeHtml(center.name)}</span>${kindBadge}
                <span class="aggregat-quadrant-h2-meta">${V.fmt(edges.length)} Verbindungen${capNote}${filterNote}</span>`;
        }
        if (hint) hint.hidden = true;

        const N = visibleEdges.length;
        const positioned = visibleEdges.map((e, i) => {
            const angle = (2 * Math.PI * i / Math.max(N, 1)) - Math.PI / 2;
            return {
                edge: e,
                x: CX + RADIUS_NEIGHBOR * Math.cos(angle),
                y: CY + RADIUS_NEIGHBOR * Math.sin(angle),
            };
        });

        const cR = nodeRadius(edges.length);
        const lines = positioned.map(pos => {
            const edgeHint = `${REL_LABELS[pos.edge.type] || pos.edge.type}: ${edgeLabelText(pos.edge)} | ${pos.edge.sourceKeys.length} Quelle(n)`;
            return `<line
                class="net-edge net-edge--${pos.edge.type}"
                x1="${CX}" y1="${CY}" x2="${pos.x.toFixed(1)}" y2="${pos.y.toFixed(1)}"
                stroke="${REL_COLORS[pos.edge.type] || '#888'}"
                stroke-width="${1 + Math.min(pos.edge.sourceKeys.length, 4)}"
                stroke-opacity="0.55"
                data-hint="${escapeAttr(edgeHint)}"
                data-hint-type="Beziehung"></line>`;
        }).join('');

        const neighborNodes = positioned.map(pos => {
            const e = pos.edge;
            const other = getActor(e.otherKey);
            const isOrgNeighbor = e.otherKind === 'org';
            const name = other ? other.name : (isOrgNeighbor ? prettifyOrg(e.otherKey) : e.otherKey);
            const r = nodeRadius(getEdgeCount(e.otherKey));
            const color = nodeColor(other || { kind: e.otherKind, sex: 'unspecified' });
            const dataAttr = isOrgNeighbor
                ? `data-org="${escapeAttr(e.otherKey)}"`
                : `data-pid="${escapeAttr(e.otherKey)}"`;
            const hint = nodeHintText(other, e.otherKey, isOrgNeighbor);
            const hintType = isOrgNeighbor ? 'Organisation' : 'Person';
            const labelMarkup = showLabels
                ? `<text x="${pos.x.toFixed(1)}" y="${(pos.y + r + 14).toFixed(1)}"
                          text-anchor="middle" class="net-node-label"
                          stroke="var(--color-bg)" stroke-width="3" paint-order="stroke">${escapeHtml(truncate(name, 24))}</text>`
                : '';
            return `<g class="net-node ${isOrgNeighbor ? 'is-org' : 'is-person'}" ${dataAttr}
                       data-hint="${escapeAttr(hint)}" data-hint-type="${hintType}">
                <circle cx="${pos.x.toFixed(1)}" cy="${pos.y.toFixed(1)}" r="${r}"
                        fill="${color}" stroke="white" stroke-width="2"/>
                ${labelMarkup}
            </g>`;
        }).join('');

        const centerKindClass = center.kind === 'org' ? ' is-org' : ' is-person';
        const centerHint = nodeHintText(center, center.id, center.kind === 'org') + ' | Mittelpunkt';
        const centerHintType = center.kind === 'org' ? 'Organisation' : 'Person';
        const centerOuterR = cR + 4;
        const centerNode = `<g class="net-node net-node--center${centerKindClass}" ${actorDataAttr(center)}
                                data-hint="${escapeAttr(centerHint)}" data-hint-type="${centerHintType}">
            <circle cx="${CX}" cy="${CY}" r="${centerOuterR}"
                    fill="${nodeColor(center)}" stroke="var(--color-text)" stroke-width="2.5"/>
            <text x="${CX}" y="${(CY + centerOuterR + 18).toFixed(1)}" text-anchor="middle"
                  class="net-node-label net-node-label--center"
                  stroke="var(--color-bg)" stroke-width="4" paint-order="stroke">${escapeHtml(center.name)}</text>
        </g>`;

        canvas.innerHTML = `<svg class="net-svg" viewBox="0 0 ${W} ${H}"
            role="img" aria-label="Personennetzwerk: Ego-Layout um ${escapeAttr(center.name)}">
            ${lines}
            ${neighborNodes}
            ${centerNode}
        </svg>`;

        renderDetailTable(center, sortedEdges);
    }

    function renderSuggestions() {
        const canvas = document.getElementById('net-canvas');
        const heading = document.getElementById('net-graph-heading');
        const hint = document.getElementById('net-hint');
        if (!canvas) return;

        if (heading) heading.textContent = 'Vorschläge: Akteure mit vielen Verbindungen';
        if (hint) hint.hidden = false;
        renderDetailPlaceholder();

        const list = topSuggestions(12);
        const items = list.map(a => {
            const c = activeEdges(a.id).length;
            const kindLabel = a.kind === 'org' ? ' Org' : '';
            return `<button type="button" class="net-suggestion-card" ${actorDataAttr(a)}>
                <span class="net-suggestion-dot" style="background:${nodeColor(a)}"></span>
                <span class="net-suggestion-name">${escapeHtml(a.name)}${kindLabel ? ` <span class="net-suggestion-kind">${kindLabel}</span>` : ''}</span>
                <span class="net-suggestion-count">${V.fmt(c)} Verb.</span>
            </button>`;
        }).join('');
        canvas.innerHTML = `<div class="net-suggestions">${items}</div>`;
    }

    const SEX_LABEL = { m: 'männlich', f: 'weiblich', unspecified: 'ohne Angabe' };

    function nodeHintText(actor, fallbackKey, isOrg) {
        if (isOrg) {
            const name = actor ? actor.name : prettifyOrg(fallbackKey);
            const c = getEdgeCount(fallbackKey);
            return `${name} | Organisation | ${V.fmt(c)} Verbindung${c === 1 ? '' : 'en'} im Korpus`;
        }
        if (!actor) return fallbackKey;
        const sex = SEX_LABEL[actor.sex] || SEX_LABEL.unspecified;
        const c = getEdgeCount(actor.id);
        return `${actor.name} | ${sex} | ${V.fmt(c)} Verbindung${c === 1 ? '' : 'en'} im Korpus`;
    }

    function edgeLabelText(e) {
        if (!e.labels.length && !e.labelsNorm.length) return '(ohne Bezeichnung)';
        const raw = e.labels.map(escapeAttr).join(', ');
        const norm = e.labelsNorm.map(escapeAttr).join(', ');
        if (!raw) return norm;
        if (!norm || raw === norm) return raw;
        return raw + ' (normalisiert: ' + norm + ')';
    }

    function renderLabelCell(e) {
        if (!e.labels.length && !e.labelsNorm.length) {
            return '<span class="text-muted-inline">&mdash;</span>';
        }
        const raw = e.labels.map(escapeHtml).join(', ');
        const norm = e.labelsNorm.map(escapeHtml).join(', ');
        if (!raw) return `<span class="net-label-norm">${norm}</span>`;
        if (!norm || raw === norm) return raw;
        return `${raw}<span class="net-label-norm" data-hint="Normalisierte Form fuer Auswertungen"> (${norm})</span>`;
    }

    function renderSourceCell(e) {
        const keys = e.sourceKeys;
        if (!keys.length) return '<span class="text-muted-inline">&mdash;</span>';
        const chips = keys.map(fk => {
            const meta = DOCS_LOOKUP[fk];
            if (!meta) {
                return `<span class="net-source-chip net-source-chip--unresolved"
                              data-hint="Quelle ${escapeAttr(fk)} nicht im Lookup; ggf. ausserhalb des freigegebenen Korpus">${escapeHtml(fk.replace(/^f__/, ''))}</span>`;
            }
            const url = '../' + meta.u;
            const label = meta.i || fk;
            const dateBit = meta.d ? meta.d + ' · ' : '';
            const regestBit = meta.r ? meta.r.slice(0, 240) : '';
            const hint = (dateBit + regestBit).trim();
            return `<a class="net-source-chip" href="${escapeAttr(url)}"
                       data-hint="${escapeAttr(hint)}">${escapeHtml(label)}</a>`;
        }).join('');
        return `<div class="net-source-chips">${chips}</div>`;
    }

    function renderDetailPlaceholder() {
        const tbody = document.getElementById('net-detail-tbody');
        const meta = document.getElementById('net-detail-meta');
        const title = document.getElementById('net-detail-title');
        if (!tbody) return;
        if (title) title.textContent = 'Verbindungen';
        if (meta)  meta.textContent  = '';
        tbody.innerHTML =
            '<tr><td colspan="4" class="net-detail-empty">' +
            'Akteur auswählen, um die Verbindungs-Tabelle anzuzeigen. ' +
            'Suche oben in der Filterleiste oder Klick auf einen Vorschlag im Graph links.' +
            '</td></tr>';
    }

    function renderDetailTable(center, edges) {
        const tbody = document.getElementById('net-detail-tbody');
        const meta = document.getElementById('net-detail-meta');
        const title = document.getElementById('net-detail-title');
        if (!tbody) return;

        if (title) title.textContent = `Verbindungen von ${center.name}`;
        if (meta)  meta.textContent  = `${V.fmt(edges.length)} Eintr${edges.length === 1 ? 'ag' : 'äge'}`;

        const rows = edges.map(e => {
            const other = getActor(e.otherKey);
            const isOrgTarget = e.otherKind === 'org';
            const name = other ? other.name : (isOrgTarget ? prettifyOrg(e.otherKey) : e.otherKey);
            const cls = isOrgTarget ? 'net-detail-recenter net-detail-recenter--org' : 'net-detail-recenter';
            const hint = isOrgTarget
                ? 'Organisation zum Mittelpunkt machen'
                : 'Person zum Mittelpunkt machen';
            const nameCell = `<button type="button" class="${cls}"
                       ${isOrgTarget ? `data-org="${escapeAttr(e.otherKey)}"` : `data-pid="${escapeAttr(e.otherKey)}"`}
                       data-hint="${escapeAttr(hint)}">${escapeHtml(name)}</button>`;
            const relSuffix = (isOrgTarget && center.kind === 'person') ? ' (Org)' : '';
            return `<tr>
                <td class="col-net-person">${nameCell}</td>
                <td class="col-net-type">${escapeHtml(REL_LABELS[e.type] || e.type)}${relSuffix}</td>
                <td class="col-net-label">${renderLabelCell(e)}</td>
                <td class="col-net-sources">${renderSourceCell(e)}</td>
            </tr>`;
        });
        tbody.innerHTML = rows.join('') ||
            '<tr><td colspan="4" class="aggregat-empty">Keine Verbindungen für die aktive Filterauswahl.</td></tr>';
    }

    function bindSearch() {
        const input = document.getElementById('net-person-search');
        const results = document.getElementById('net-search-results');
        if (!input || !results) return;
        input.addEventListener('input', () => {
            const q = EdCore.normForSearch(input.value.trim());
            if (q.length < 2) { results.innerHTML = ''; results.hidden = true; return; }
            const matches = [];
            for (const a of ACTORS.values()) {
                if (EdCore.matchesQuery(a._s, q)) {
                    matches.push(a);
                    if (matches.length >= 12) break;
                }
            }
            if (!matches.length) {
                results.innerHTML = '<li class="net-search-empty">Keine Treffer.</li>';
                results.hidden = false;
                return;
            }
            results.innerHTML = matches.map(a => {
                const c = getEdgeCount(a.id);
                const kindLabel = a.kind === 'org' ? ' <span class="net-search-hit-kind">Org</span>' : '';
                return `<li>
                    <button type="button" class="net-search-hit" ${actorDataAttr(a)}>
                        <span class="net-search-hit-name">${escapeHtml(a.name)}${kindLabel}</span>
                        <span class="net-search-hit-count">${V.fmt(c)} Verb.</span>
                    </button>
                </li>`;
            }).join('');
            results.hidden = false;
        });
        results.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-pid], [data-org]');
            if (!btn) return;
            input.value = '';
            results.hidden = true;
            results.innerHTML = '';
            recenter(btn.dataset.pid || btn.dataset.org);
        });
    }

    function bindGraphInteraction() {
        const canvas = document.getElementById('net-canvas');
        if (canvas) {
            canvas.addEventListener('click', (e) => {
                const node = e.target.closest('[data-pid], [data-org]');
                if (!node) return;
                recenter(node.dataset.pid || node.dataset.org);
            });
        }
        const detail = document.getElementById('net-detail');
        if (detail) {
            detail.addEventListener('click', (e) => {
                const btn = e.target.closest('.net-detail-recenter');
                if (!btn) return;
                recenter(btn.dataset.pid || btn.dataset.org);
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
                if (STATE.types.size > 1) STATE.types.delete(t);
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

    function recenter(key) {
        if (!key || !ACTORS.has(key)) return;
        STATE.center = key;
        renderEgo(key);
        updateActiveFilters();
        writeUrl();
    }

    function renderActive() {
        if (STATE.center && ACTORS.has(STATE.center)) {
            renderEgo(STATE.center);
        } else {
            renderSuggestions();
        }
    }

    function updateActiveFilters() {
        const filters = [];
        if (STATE.center && ACTORS.has(STATE.center)) {
            const a = ACTORS.get(STATE.center);
            const label = a.kind === 'org'
                ? 'Mittelpunkt (Org): ' + a.name
                : 'Mittelpunkt: ' + a.name;
            filters.push({
                label,
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
        if (u.p && ACTORS.has(u.p)) STATE.center = u.p;
        const group = document.getElementById('net-type-filter');
        if (group) {
            for (const b of group.querySelectorAll('[data-net-type]')) {
                const isOn = STATE.types.has(b.getAttribute('data-net-type'));
                b.classList.toggle('is-active', isOn);
                b.setAttribute('aria-pressed', isOn ? 'true' : 'false');
            }
        }
    }

    // Text-Escaping kommt aus EdCore (textContent-Verfahren, hier geladen);
    // escapeAttr ergaenzt nur das Anfuehrungszeichen fuer Attribut-Kontexte.
    function escapeHtml(s) {
        return EdCore.esc(s);
    }
    function escapeAttr(s) {
        return escapeHtml(s).replace(/"/g, '&quot;');
    }
    function truncate(s, n) {
        return s && s.length > n ? s.slice(0, n - 1) + '…' : (s || '');
    }

    document.addEventListener('DOMContentLoaded', () => {
        buildIndex();
        bindSearch();
        bindGraphInteraction();
        bindTypeFilter();
        bindReset();
        applyUrlState();
        updateActiveFilters();
        V.loadDocsLookup()
            .then(lk => { DOCS_LOOKUP = lk; })
            .catch(() => {})
            .finally(() => {
                renderActive();
                urlSyncActive = true;
                writeUrl();
            });
    });
})();
