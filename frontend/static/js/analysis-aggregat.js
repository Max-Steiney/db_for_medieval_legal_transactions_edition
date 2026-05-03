// Analyse / Auswertungen: vier Sektionen mit Donut, Bar-Chart und Tabelle.
// Sidebar-Filter (Zeitraum, Geschlecht) wirken auf alle Sektionen.
// Geteilte Infrastruktur kommt aus VizCore (viz-core.js).
(function () {
    'use strict';

    const V = VizCore;

    // ---------------------------------------------------------------------
    // Daten laden
    // ---------------------------------------------------------------------
    const EPIC_A = V.readJsonScript('aggregat-data-epic-a', { observations: {} });
    const EPIC_B = V.readJsonScript('aggregat-data-epic-b', { overview: {}, labels: [] });
    const EPIC_C = V.readJsonScript('aggregat-data-epic-c', { observations: {} });
    let DOCS_LOOKUP = {};   // file_key -> doc-Stammdaten, async geladen

    // ---------------------------------------------------------------------
    // Filter-State
    // ---------------------------------------------------------------------
    const STATE = {
        sex: 'all',                  // 'all' | 'm' | 'f' | 'unspecified'
        decadeMin: null,             // numeric decade or null
        decadeMax: null,
        labelSearch: '',
        labelType: 'all',
        rolesMode: 'mentions',       // 'mentions' | 'persons'
    };
    const decFilter = V.makeDecadeFilter(STATE);

    // ---------------------------------------------------------------------
    // M/W-Bar + Counts; gleiche Optik in Donut-Legenden und Bezeichnungs-
    // Tabelle. Liefert HTML-Snippet, der Aufrufer entscheidet ueber Wrapper.
    // ---------------------------------------------------------------------
    function sexBarHTML(m, f) {
        const tot = (m || 0) + (f || 0);
        const mPct = tot ? (m / tot * 100) : 0;
        const fPct = tot ? (f / tot * 100) : 0;
        return `
            <span class="legend-sex-bar"
                  title="männlich ${V.fmt(m)} · weiblich ${V.fmt(f)}">
                <span class="legend-sex-bar-m" data-w="${mPct.toFixed(2)}"></span>
                <span class="legend-sex-bar-f" data-w="${fPct.toFixed(2)}"></span>
            </span>
            <span class="legend-sex-counts">
                <span class="sex-m-num">${V.fmt(m || 0)}</span>
                <span class="sex-sep">/</span>
                <span class="sex-f-num">${V.fmt(f || 0)}</span>
            </span>`;
    }

    // ---------------------------------------------------------------------
    // Donut-Renderer (Inline-SVG, keine externe Lib).
    // segments: [{key, label, value, color}, ...]
    // ---------------------------------------------------------------------
    function renderDonut(container, segments, opts) {
        if (!container) return;
        opts = opts || {};
        const total = segments.reduce((s, x) => s + (x.value || 0), 0);
        const cx = 50, cy = 50, r = 38, sw = 14;
        const C = 2 * Math.PI * r;

        if (total === 0) {
            container.innerHTML = '<div class="aggregat-donut-empty">keine Daten</div>';
            return;
        }

        let offset = 0;
        const arcs = segments.map(seg => {
            const v = seg.value || 0;
            if (v === 0) return '';
            const len = (v / total) * C;
            const arc = `<circle class="donut-arc" data-key="${seg.key}"
                cx="${cx}" cy="${cy}" r="${r}" fill="none"
                stroke="${seg.color}" stroke-width="${sw}"
                stroke-dasharray="${len.toFixed(3)} ${(C - len).toFixed(3)}"
                stroke-dashoffset="${(-offset).toFixed(3)}"
                transform="rotate(-90 ${cx} ${cy})">
                <title>${seg.label}: ${V.fmt(v)} (${V.pct(v, total)} %)</title>
            </circle>`;
            offset += len;
            return arc;
        });

        const centerLabel = opts.centerLabel || '';
        const totalText = `<text x="${cx}" y="${cy - 1}" text-anchor="middle"
            class="donut-center-value">${V.fmt(total)}</text>`;
        const subText = centerLabel ? `<text x="${cx}" y="${cy + 9}" text-anchor="middle"
            class="donut-center-label">${centerLabel}</text>` : '';

        container.innerHTML = `<svg class="donut-svg" viewBox="0 0 100 100"
            role="img" aria-label="${opts.ariaLabel || 'Donut-Diagramm'}">
            ${arcs.join('')}
            ${totalText}${subText}
        </svg>`;
    }

    // ---------------------------------------------------------------------
    // Legende: pro Segment ein Eintrag mit Farbe, Label, Count, %, M/W-Bar
    // ---------------------------------------------------------------------
    function renderLegend(container, entries, total) {
        if (!container) return;
        const items = entries.map(e => {
            const sex = e.hasSex
                ? `<span class="legend-sex">${sexBarHTML(e.m, e.f)}</span>`
                : '';
            return `<li class="legend-item" data-key="${e.key}">
                <span class="legend-swatch" data-bg="${e.color}"></span>
                <span class="legend-label">${e.label}</span>
                <span class="legend-count">${V.fmt(e.value)}</span>
                <span class="legend-pct">${V.pct(e.value, total)}&nbsp;%</span>
                ${sex}
            </li>`;
        });
        container.innerHTML = items.join('');
        V.applyDataStyles(container);
    }

    // ---------------------------------------------------------------------
    // Sektion 1: Funktionsrollen
    // ---------------------------------------------------------------------
    function aggregateRoles() {
        const dec = EPIC_A.observations.role_by_sex_by_decade || {};
        const persDec = EPIC_A.observations.role_persons_by_decade || {};
        const noTime = decFilter.noFilter();

        const mentions = {};
        for (const role of V.ROLE_ORDER) {
            mentions[role] = { m: 0, f: 0 };
            const byDec = dec[role] || {};
            if (noTime) {
                const full = (EPIC_A.observations.role_by_sex || {})[role] || {};
                mentions[role].m = full.m || 0;
                mentions[role].f = full.f || 0;
            } else {
                for (const [d, sexCounts] of Object.entries(byDec)) {
                    if (!decFilter.contains(d)) continue;
                    mentions[role].m += sexCounts.m || 0;
                    mentions[role].f += sexCounts.f || 0;
                }
            }
        }

        const persons = {};
        for (const role of V.ROLE_ORDER) {
            persons[role] = { m: 0, f: 0 };
            const byDec = persDec[role] || {};
            const seenM = new Set();
            const seenF = new Set();
            for (const [d, sexKeys] of Object.entries(byDec)) {
                if (!decFilter.contains(d)) continue;
                (sexKeys.m || []).forEach(k => seenM.add(k));
                (sexKeys.f || []).forEach(k => seenF.add(k));
            }
            persons[role].m = seenM.size;
            persons[role].f = seenF.size;
        }
        return { mentions, persons };
    }

    function renderRoles() {
        const agg = aggregateRoles();
        const data = STATE.rolesMode === 'persons' ? agg.persons : agg.mentions;
        const sex = STATE.sex;

        const segments = V.ROLE_ORDER.map(r => {
            const m = data[r].m || 0;
            const f = data[r].f || 0;
            let v = m + f;
            if (sex === 'm') v = m;
            else if (sex === 'f') v = f;
            return {
                key: r,
                label: V.ROLE_LABELS[r] || r || '(keine)',
                value: v,
                color: V.ROLE_COLORS[r] || '#888',
            };
        }).filter(s => s.value > 0);

        const total = segments.reduce((s, x) => s + x.value, 0);
        const unitLabel = STATE.rolesMode === 'persons' ? 'Personen' : 'Nennungen';

        renderDonut(document.getElementById('roles-donut'), segments, {
            centerLabel: unitLabel,
            ariaLabel: 'Funktionsrollen-Verteilung',
        });

        // M/W-Aufschluesselung in der Legende ist immer sichtbar — der
        // Sex-Filter veraendert nur die Donut-Werte, nicht das, was wir an
        // Zusatz-Information ueber das Geschlechterverhaeltnis zeigen.
        const legendEntries = segments.map(s => ({
            key: s.key,
            label: s.label,
            value: s.value,
            color: s.color,
            m: data[s.key].m || 0,
            f: data[s.key].f || 0,
            hasSex: true,
        }));
        renderLegend(document.getElementById('roles-legend'), legendEntries, total);

        renderRolesDetailTable(data);
    }

    function renderRolesDetailTable(data) {
        const tbody = document.querySelector('#roles-table tbody');
        if (!tbody) return;
        const totalM = V.ROLE_ORDER.reduce((s, r) => s + (data[r].m || 0), 0);
        const totalF = V.ROLE_ORDER.reduce((s, r) => s + (data[r].f || 0), 0);
        const grandTotal = totalM + totalF;
        const rows = [];
        for (const role of V.ROLE_ORDER) {
            const m = data[role].m || 0;
            const f = data[role].f || 0;
            const total = m + f;
            if (total === 0) continue;
            rows.push(`<tr data-role="${role}">
                <td class="col-label">${V.ROLE_LABELS[role] || role || '(keine)'}</td>
                <td class="num">${V.fmt(total)}</td>
                <td class="num pct">${V.pct(total, grandTotal)}</td>
                <td class="num sex-m">${V.fmt(m)}</td>
                <td class="num pct sex-m">${V.pct(m, total)}</td>
                <td class="num pct sex-m">${V.pct(m, totalM)}</td>
                <td class="num sex-f">${V.fmt(f)}</td>
                <td class="num pct sex-f">${V.pct(f, total)}</td>
                <td class="num pct sex-f">${V.pct(f, totalF)}</td>
            </tr>`);
        }
        rows.push(`<tr class="aggregat-row-total">
            <td class="col-label">gesamt</td>
            <td class="num">${V.fmt(grandTotal)}</td>
            <td class="num pct">100,0</td>
            <td class="num sex-m">${V.fmt(totalM)}</td>
            <td class="num pct sex-m">${V.pct(totalM, grandTotal)}</td>
            <td class="num pct sex-m">100,0</td>
            <td class="num sex-f">${V.fmt(totalF)}</td>
            <td class="num pct sex-f">${V.pct(totalF, grandTotal)}</td>
            <td class="num pct sex-f">100,0</td>
        </tr>`);
        tbody.innerHTML = rows.join('');
    }

    // ---------------------------------------------------------------------
    // Sektion 2: Beziehungstypen
    // ---------------------------------------------------------------------
    function renderRelations() {
        const overview = (EPIC_B.overview || {}).type_by_sex || {};
        const cov = (EPIC_B.coverage || {});
        const personsTotal = cov.persons_with_relations || cov.node_count || 0;
        const sex = STATE.sex;

        const perType = V.REL_ORDER.map(t => {
            const e = overview[t] || { m: 0, f: 0, unspecified: 0 };
            const m = e.m || 0;
            const f = e.f || 0;
            const u = e.unspecified || 0;
            const total = m + f + u;
            let v = total;
            if (sex === 'm') v = m;
            else if (sex === 'f') v = f;
            else if (sex === 'unspecified') v = u;
            return {
                key: t, label: V.REL_LABELS[t], color: V.REL_COLORS[t],
                value: v, m, f, total
            };
        });

        const segments = perType.filter(s => s.value > 0).map(s => ({
            key: s.key, label: s.label, value: s.value, color: s.color
        }));
        const grand = segments.reduce((s, x) => s + x.value, 0);

        renderDonut(document.getElementById('relations-donut'), segments, {
            centerLabel: 'Beziehungen',
            ariaLabel: 'Beziehungstypen-Verteilung',
        });

        const legendEntries = perType.filter(s => s.value > 0).map(s => ({
            key: s.key, label: s.label, value: s.value, color: s.color,
            m: s.m, f: s.f,
            hasSex: true,
        }));
        renderLegend(document.getElementById('relations-legend'), legendEntries, grand);

        renderRelationsDetailTable(perType, personsTotal);
    }

    function renderRelationsDetailTable(perType, personsTotal) {
        const tbody = document.querySelector('#relations-table tbody');
        if (!tbody) return;
        const grandRels = perType.reduce((s, x) => s + x.total, 0);
        const totalM = perType.reduce((s, x) => s + x.m, 0);
        const totalF = perType.reduce((s, x) => s + x.f, 0);
        const rows = perType.map(s => `<tr data-rel="${s.key}">
            <td class="col-label">${s.label}</td>
            <td class="num">${V.fmt(s.total)}</td>
            <td class="num pct">${V.pct(s.total, grandRels)}</td>
            <td class="num sex-m">${V.fmt(s.m)}</td>
            <td class="num pct sex-m">${V.pct(s.m, s.total)}</td>
            <td class="num sex-f">${V.fmt(s.f)}</td>
            <td class="num pct sex-f">${V.pct(s.f, s.total)}</td>
            <td class="num">–</td>
        </tr>`);
        rows.push(`<tr class="aggregat-row-total">
            <td class="col-label">gesamt</td>
            <td class="num">${V.fmt(grandRels)}</td>
            <td class="num pct">100,0</td>
            <td class="num sex-m">${V.fmt(totalM)}</td>
            <td class="num pct sex-m">${V.pct(totalM, grandRels)}</td>
            <td class="num sex-f">${V.fmt(totalF)}</td>
            <td class="num pct sex-f">${V.pct(totalF, grandRels)}</td>
            <td class="num">${V.fmt(personsTotal)}</td>
        </tr>`);
        tbody.innerHTML = rows.join('');
    }

    // ---------------------------------------------------------------------
    // Sektion 3: Transaktionstypen — horizontale Balken
    // ---------------------------------------------------------------------
    function aggregateTxTypes() {
        const tl = (EPIC_C.observations || {}).tx_timeline || {};
        const noTime = decFilter.noFilter();
        const totals = {};
        for (const [type, byDec] of Object.entries(tl)) {
            let s = 0;
            for (const [d, c] of Object.entries(byDec)) {
                if (noTime || decFilter.contains(d)) s += c;
            }
            if (s > 0) totals[type] = s;
        }
        return totals;
    }

    function renderTx() {
        const container = document.getElementById('tx-bars');
        const foot = document.getElementById('tx-foot');
        if (!container) return;

        const totals = aggregateTxTypes();
        const notNorm = totals['_not_normalised'] || 0;
        delete totals['_not_normalised'];

        const sorted = Object.entries(totals).sort((a, b) => b[1] - a[1]);
        const top = sorted.slice(0, 10);
        const rest = sorted.slice(10);
        const restSum = rest.reduce((s, [, c]) => s + c, 0);
        const grandTotal = sorted.reduce((s, [, c]) => s + c, 0);
        const maxVal = top.length ? top[0][1] : 1;

        // txKey wird ans Markup gehaengt, damit der Drill-Click-Handler
        // den Pipeline-Schluessel zur Aufloesung kennt (data-tx).
        const barRow = (label, val, txKey, cssClass = '') => {
            const wRel = (val / maxVal * 100).toFixed(2);
            const txAttr = txKey ? ` data-tx="${txKey}"` : '';
            return `<div class="aggregat-bar-row ${cssClass}"${txAttr}>
                <span class="aggregat-bar-label">${label}</span>
                <div class="aggregat-bar-track">
                    <div class="aggregat-bar-fill" data-w="${wRel}"></div>
                </div>
                <span class="aggregat-bar-count">${V.fmt(val)}</span>
                <span class="aggregat-bar-pct">${V.pct(val, grandTotal)}&nbsp;%</span>
            </div>`;
        };

        const rows = top.map(([k, c]) => barRow(V.labelize(k), c, k));

        if (rest.length) {
            // Aufklappbare Sonstige-Sammelzeile: Klick toggelt is-open auf
            // dem Wrapper, das CSS zeigt dann die versteckten rest-Bars.
            const restRows = rest.map(([k, c]) => barRow(V.labelize(k), c, k, 'is-rest-item'));
            rows.push(`<div class="aggregat-bar-rest" data-rest-toggle>
                <button type="button" class="aggregat-bar-row aggregat-bar-row--rest"
                        aria-expanded="false">
                    <span class="aggregat-bar-label">
                        <span class="rest-arrow" aria-hidden="true">▸</span>
                        Sonstige (${rest.length} Typen)
                    </span>
                    <div class="aggregat-bar-track">
                        <div class="aggregat-bar-fill is-rest-fill"
                             data-w="${(restSum / maxVal * 100).toFixed(2)}"></div>
                    </div>
                    <span class="aggregat-bar-count">${V.fmt(restSum)}</span>
                    <span class="aggregat-bar-pct">${V.pct(restSum, grandTotal)}&nbsp;%</span>
                </button>
                <div class="aggregat-bar-rest-items">${restRows.join('')}</div>
            </div>`);
        }

        container.innerHTML = rows.join('') ||
            '<div class="aggregat-empty">keine Daten im Filter-Zeitraum</div>';
        V.applyDataStyles(container);

        const wrap = container.querySelector('[data-rest-toggle]');
        if (wrap) {
            const btn = wrap.querySelector('button');
            btn.addEventListener('click', () => {
                const open = wrap.classList.toggle('is-open');
                btn.setAttribute('aria-expanded', open ? 'true' : 'false');
                const arrow = btn.querySelector('.rest-arrow');
                if (arrow) arrow.textContent = open ? '▾' : '▸';
            });
        }

        if (foot) {
            const parts = [];
            if (STATE.sex && STATE.sex !== 'all') {
                parts.push('Geschlechter-Filter wird auf Rechtsgeschäfte nicht angewendet (Events sind keiner Person zugeordnet).');
            }
            if (notNorm > 0) {
                parts.push(`${V.fmt(notNorm)} Rechtsgeschäfte ohne normalisiertes Verb sind ausgeblendet.`);
            }
            foot.innerHTML = parts.length
                ? parts.map(p => `<span class="aggregat-foot-line">${p}</span>`).join('')
                : '';
        }
    }

    // ---------------------------------------------------------------------
    // Sektion 4: Bezeichnungen — Tabelle mit Mini-Bars
    // ---------------------------------------------------------------------
    function renderLabels() {
        const tbody = document.querySelector('#labels-table tbody');
        const meta = document.getElementById('labels-count-meta');
        if (!tbody) return;

        const all = EPIC_B.labels || [];
        const search = STATE.labelSearch.trim().toLowerCase();
        const sexFilter = STATE.sex;
        const typeFilter = STATE.labelType;

        const filtered = all.filter(l => {
            if (typeFilter !== 'all' && l.type !== typeFilter) return false;
            if (sexFilter === 'm' && (l.m || 0) === 0) return false;
            if (sexFilter === 'f' && (l.f || 0) === 0) return false;
            if (search) {
                const hay = (l.label + ' ' + (l.variants || []).join(' ')).toLowerCase();
                if (!hay.includes(search)) return false;
            }
            return true;
        });
        filtered.sort((a, b) => (b.persons || 0) - (a.persons || 0));
        const maxPersons = filtered.reduce((m, l) => Math.max(m, l.persons || 0), 1);

        if (meta) {
            meta.textContent = (filtered.length === all.length)
                ? `${V.fmt(all.length)} Bezeichnungen`
                : `${V.fmt(filtered.length)} von ${V.fmt(all.length)}`;
        }

        const rows = filtered.map(l => {
            const persons = l.persons || 0;
            const barWidth = (persons / maxPersons * 100).toFixed(2);
            const variants = (l.variants || []).slice(0, 6).join(', ');
            return `<tr data-label="${encodeURIComponent(l.label)}"
                title="${variants ? 'Varianten: ' + variants : ''}">
                <td class="col-label">${l.label}</td>
                <td>${V.REL_LABELS[l.type] || l.type}</td>
                <td class="num col-persons">
                    <div class="cell-mini-bar">
                        <span class="cell-mini-bar-fill" data-w="${barWidth}"></span>
                        <span class="cell-mini-bar-num">${V.fmt(persons)}</span>
                    </div>
                </td>
                <td class="col-sexbar">${sexBarHTML(l.m || 0, l.f || 0)}</td>
            </tr>`;
        });
        tbody.innerHTML = rows.join('') ||
            '<tr><td colspan="4" class="aggregat-empty">Keine Treffer.</td></tr>';
        V.applyDataStyles(tbody);
    }

    // ---------------------------------------------------------------------
    // Filter-Bedienung
    // ---------------------------------------------------------------------
    function bindSexFilter() {
        const group = document.getElementById('filter-sex');
        if (!group) return;

        // Initial-Setup: aktiver Chip optisch markieren, Chips ohne Treffer
        // (count=0) ausblenden, damit kein toter Klick angeboten wird.
        V.setActiveChip(group, STATE.sex, 'data-sex');
        group.querySelectorAll('[data-sex]').forEach(b => {
            const cnt = b.querySelector('.form-filter-chip-count');
            if (cnt && cnt.textContent.trim() === '0' && b.getAttribute('data-sex') !== 'all') {
                b.hidden = true;
            }
        });

        group.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-sex]');
            if (!btn) return;
            STATE.sex = btn.getAttribute('data-sex');
            V.setActiveChip(group, STATE.sex, 'data-sex');
            renderAll();
        });
    }

    function bindRolesToggle() {
        const grp = document.querySelector('#q-roles .aggregat-toggle');
        if (!grp) return;
        grp.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-roles-mode]');
            if (!btn) return;
            STATE.rolesMode = btn.getAttribute('data-roles-mode');
            V.setActiveChip(grp, STATE.rolesMode, 'data-roles-mode', 'is-active');
            renderRoles();
        });
    }

    function bindLabelsToolbar() {
        const search = document.getElementById('labels-search');
        if (search) {
            search.addEventListener('input', (e) => {
                STATE.labelSearch = e.target.value;
                renderLabels();
                updateActiveFilters();
            });
        }
        const chipGroup = document.querySelector('.aggregat-rel-type-chips');
        if (chipGroup) {
            chipGroup.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-rel]');
                if (!btn) return;
                STATE.labelType = btn.getAttribute('data-rel');
                V.setActiveChip(chipGroup, STATE.labelType, 'data-rel');
                renderLabels();
                updateActiveFilters();
            });
        }
    }

    function bindReset() {
        const btn = document.getElementById('filter-reset');
        if (!btn) return;
        btn.addEventListener('click', () => {
            STATE.sex = 'all';
            STATE.labelSearch = '';
            STATE.labelType = 'all';
            STATE.rolesMode = 'mentions';

            V.setActiveChip(document.getElementById('filter-sex'), 'all', 'data-sex');
            V.setActiveChip(document.querySelector('.aggregat-rel-type-chips'),
                            'all', 'data-rel');
            V.setActiveChip(document.querySelector('#q-roles .aggregat-toggle'),
                            'mentions', 'data-roles-mode', 'is-active');

            const search = document.getElementById('labels-search');
            if (search) search.value = '';
            // Slider-Reset triggert via input-Event den onChange-Hook und
            // damit renderAll(). Falls der Slider fehlt, einmal direkt rendern.
            if (!V.resetSliderInputs()) {
                STATE.decadeMin = null;
                STATE.decadeMax = null;
                renderAll();
            }
        });
    }

    // ---------------------------------------------------------------------
    // Active-Filter-Strip — Filter-Beschreibungen + Clear-Callbacks
    // ---------------------------------------------------------------------
    function clearSexFilter() {
        STATE.sex = 'all';
        V.setActiveChip(document.getElementById('filter-sex'), 'all', 'data-sex');
        renderAll();
    }
    function clearLabelSearch() {
        STATE.labelSearch = '';
        const s = document.getElementById('labels-search');
        if (s) s.value = '';
        renderLabels();
        updateActiveFilters();
    }
    function clearLabelType() {
        STATE.labelType = 'all';
        V.setActiveChip(document.querySelector('.aggregat-rel-type-chips'),
                        'all', 'data-rel');
        renderLabels();
        updateActiveFilters();
    }

    function updateActiveFilters() {
        const filters = [];
        if (decFilter.isActive()) {
            const minEl = document.getElementById('range-min');
            const maxEl = document.getElementById('range-max');
            const lo = minEl ? minEl.value : STATE.decadeMin;
            const hi = maxEl ? maxEl.value : STATE.decadeMax;
            filters.push({
                label: 'Zeitraum: ' + lo + '–' + hi,
                onClear: () => V.resetSliderInputs(),
            });
        }
        if (STATE.sex && STATE.sex !== 'all') {
            filters.push({
                label: 'Geschlecht: ' + (V.SEX_LABELS_DE[STATE.sex] || STATE.sex),
                onClear: clearSexFilter,
            });
        }
        if (STATE.labelType && STATE.labelType !== 'all') {
            filters.push({
                label: 'Bezeichnungs-Typ: ' + (V.REL_LABELS[STATE.labelType] || STATE.labelType),
                onClear: clearLabelType,
            });
        }
        if (STATE.labelSearch && STATE.labelSearch.trim()) {
            filters.push({
                label: 'Bezeichnung: ' + STATE.labelSearch.trim(),
                onClear: clearLabelSearch,
            });
        }
        V.renderActiveFilters('active-filters', filters);
    }

    // ---------------------------------------------------------------------
    // Drill-Down: Klick auf Donut-Arc / Bar / Bezeichnung -> Quellen-Liste.
    // Sammelt file_keys aus den drill_down-Indices der epic_*-Aggregate
    // und ruft V.openDrillOverlay zum Anzeigen.
    // ---------------------------------------------------------------------
    function drillRoleSex(roleKey) {
        const dd = ((EPIC_A.drill_down || {}).role_sex || {})[roleKey] || {};
        const sex = STATE.sex;
        const keys = [];
        if (sex === 'all' || sex === 'm') (dd.m || []).forEach(k => keys.push(k));
        if (sex === 'all' || sex === 'f') (dd.f || []).forEach(k => keys.push(k));
        if (sex === 'all' || sex === 'unspecified') (dd.unspecified || []).forEach(k => keys.push(k));
        const label = V.ROLE_LABELS[roleKey] || roleKey || 'keine Rolle';
        const sexNote = (sex !== 'all') ? ' · ' + (V.SEX_LABELS_DE[sex] || sex) : '';
        openDrill('Funktionsrolle: ' + label + sexNote, keys);
    }
    function drillRelationSex(relKey) {
        const dd = (EPIC_B.drill_down || {}).type_sex || {};
        const sex = STATE.sex;
        const keys = [];
        // type_sex Keys sind composite: "kin_m", "kin_f", "occ_m", ...
        if (sex === 'all' || sex === 'm') (dd[relKey + '_m'] || []).forEach(k => keys.push(k));
        if (sex === 'all' || sex === 'f') (dd[relKey + '_f'] || []).forEach(k => keys.push(k));
        const label = V.REL_LABELS[relKey] || relKey;
        const sexNote = (sex !== 'all') ? ' · ' + (V.SEX_LABELS_DE[sex] || sex) : '';
        openDrill('Beziehungstyp: ' + label + sexNote, keys);
    }
    function drillTxType(txKey) {
        // tx_type_decade.{type}.{decade} -> [file_keys]
        const dd = ((EPIC_C.drill_down || {}).tx_type_decade || {})[txKey] || {};
        const keys = [];
        for (const [d, fks] of Object.entries(dd)) {
            if (!decFilter.contains(d)) continue;
            fks.forEach(k => keys.push(k));
        }
        openDrill('Transaktionstyp: ' + V.labelize(txKey), keys);
    }
    function drillLabel(label) {
        // label_sex Keys sind composite: "{lowercased_label}__{m|f}"
        const dd = (EPIC_B.drill_down || {}).label_sex || {};
        const sex = STATE.sex;
        const lc = label.toLowerCase();
        const keys = [];
        if (sex === 'all' || sex === 'm') (dd[lc + '__m'] || []).forEach(k => keys.push(k));
        if (sex === 'all' || sex === 'f') (dd[lc + '__f'] || []).forEach(k => keys.push(k));
        const sexNote = (sex !== 'all') ? ' · ' + (V.SEX_LABELS_DE[sex] || sex) : '';
        openDrill('Bezeichnung: ' + label + sexNote, keys);
    }

    function openDrill(title, fileKeys) {
        if (!Object.keys(DOCS_LOOKUP).length) {
            // Lookup ist async; der erste Klick faengt das ab und laedt nach.
            V.loadDocsLookup().then(lk => {
                DOCS_LOOKUP = lk;
                openDrill(title, fileKeys);
            });
            return;
        }
        const crossNavUrl = V.buildDocumentsURL({
            decadeMin: STATE.decadeMin,
            decadeMax: STATE.decadeMax,
            sex: STATE.sex !== 'all' ? STATE.sex : null,
        });
        V.openDrillOverlay({
            overlayId: 'aggregat-drilldown',
            title: title,
            fileKeys: fileKeys,
            docsLookup: DOCS_LOOKUP,
            decadeFilter: decFilter.isActive() ? decFilter : null,
            crossNavUrl: crossNavUrl,
        });
    }

    function bindDrillClicks() {
        // Donut-Arcs: per Event-Delegation auf den jeweiligen Donut-Container
        const rolesDonut = document.getElementById('roles-donut');
        if (rolesDonut) {
            rolesDonut.addEventListener('click', (e) => {
                const arc = e.target.closest('.donut-arc');
                if (!arc) return;
                drillRoleSex(arc.dataset.key || '');
            });
        }
        const relsDonut = document.getElementById('relations-donut');
        if (relsDonut) {
            relsDonut.addEventListener('click', (e) => {
                const arc = e.target.closest('.donut-arc');
                if (!arc) return;
                drillRelationSex(arc.dataset.key || '');
            });
        }
        // Legend-Items oeffnen denselben Drill (besser klickbar als die
        // schmalen SVG-Arcs)
        const rolesLegend = document.getElementById('roles-legend');
        if (rolesLegend) {
            rolesLegend.addEventListener('click', (e) => {
                const item = e.target.closest('.legend-item');
                if (!item) return;
                drillRoleSex(item.dataset.key || '');
            });
        }
        const relsLegend = document.getElementById('relations-legend');
        if (relsLegend) {
            relsLegend.addEventListener('click', (e) => {
                const item = e.target.closest('.legend-item');
                if (!item) return;
                drillRelationSex(item.dataset.key || '');
            });
        }
        // Tx-Bars: Click auf normale Bar-Reihen, nicht auf die Sonstige-
        // Toggle-Reihe und nicht auf die Sub-Items (deren Tx-Key haben wir
        // im Renderer aktuell noch nicht ans data-Attribut gehaengt; die
        // werden in einer naechsten Iteration klickbar).
        const txBars = document.getElementById('tx-bars');
        if (txBars) {
            txBars.addEventListener('click', (e) => {
                const row = e.target.closest('.aggregat-bar-row');
                if (!row) return;
                if (row.classList.contains('aggregat-bar-row--rest')) return;  // Toggle, kein Drill
                const txKey = row.dataset.tx;
                if (txKey) drillTxType(txKey);
            });
        }
        // Bezeichnungs-Tabelle
        const labelsTable = document.getElementById('labels-table');
        if (labelsTable) {
            labelsTable.addEventListener('click', (e) => {
                const tr = e.target.closest('tr[data-label]');
                if (!tr) return;
                const label = decodeURIComponent(tr.dataset.label);
                drillLabel(label);
            });
        }
    }

    // ---------------------------------------------------------------------
    // URL-State-Sync — Filter-Stand wird in die Suchparameter serialisiert,
    // damit der Forschungsstand zitierbar / bookmark-fähig ist.
    // Format: ?dec=1300-1380&sex=f&type=kin&q=hausfrau&mode=persons
    // ---------------------------------------------------------------------
    let urlSyncActive = false;   // Switch, damit Apply-from-URL keine
                                  // Re-Writes triggert.

    function writeUrl() {
        if (!urlSyncActive) return;
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        const dec = decFilter.isActive() && minEl && maxEl
            ? `${minEl.value}-${maxEl.value}` : null;
        V.writeUrlState({
            dec: dec,
            sex:  STATE.sex !== 'all' ? STATE.sex : null,
            type: STATE.labelType !== 'all' ? STATE.labelType : null,
            q:    STATE.labelSearch.trim() || null,
            mode: STATE.rolesMode !== 'mentions' ? STATE.rolesMode : null,
        });
    }

    function applyUrlState() {
        const u = V.parseUrlState();
        if (u.sex && ['m', 'f', 'unspecified'].includes(u.sex)) STATE.sex = u.sex;
        if (u.mode === 'persons') STATE.rolesMode = 'persons';
        if (u.type && ['kin', 'occ', 'rep', 'friend'].includes(u.type)) STATE.labelType = u.type;
        if (u.q) STATE.labelSearch = u.q;
        if (u.dec) {
            const m = u.dec.match(/^(\d{4})-(\d{4})$/);
            if (m) {
                const lo = parseInt(m[1], 10);
                const hi = parseInt(m[2], 10);
                STATE.decadeMin = V.decadeOf(lo);
                STATE.decadeMax = V.decadeOf(hi);
                V.applySliderValues(lo, hi);
            }
        }
        // UI-Sync: Chips, Toggle, Search-Input
        V.setActiveChip(document.getElementById('filter-sex'), STATE.sex, 'data-sex');
        V.setActiveChip(document.querySelector('.aggregat-rel-type-chips'),
                        STATE.labelType, 'data-rel');
        V.setActiveChip(document.querySelector('#q-roles .aggregat-toggle'),
                        STATE.rolesMode, 'data-roles-mode', 'is-active');
        const searchEl = document.getElementById('labels-search');
        if (searchEl && STATE.labelSearch) searchEl.value = STATE.labelSearch;
    }

    // ---------------------------------------------------------------------
    // Master-Render
    // ---------------------------------------------------------------------
    function renderAll() {
        renderRoles();
        renderRelations();
        renderTx();
        renderLabels();
        updateActiveFilters();
        writeUrl();
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindSexFilter();
        V.bindRangeSlider({ state: STATE, onChange: renderAll });
        bindRolesToggle();
        bindLabelsToolbar();
        bindReset();
        V.bindDrillOverlay({ overlayId: 'aggregat-drilldown' });
        bindDrillClicks();
        // URL-State zuerst lesen + auf STATE/UI mappen, dann ein einziges
        // renderAll(); danach URL-Sync aktiv schalten.
        applyUrlState();
        renderAll();
        urlSyncActive = true;
        writeUrl();
        // docs_lookup eager im Hintergrund vorladen, damit der erste
        // Drill-Klick keine Verzoegerung hat. Der Klick-Pfad faellt sauber
        // auf "lade nach" zurueck, falls der Fetch noch nicht fertig ist.
        V.loadDocsLookup().then(lk => { DOCS_LOOKUP = lk; }).catch(() => {});
    });
})();
