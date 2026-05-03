// Auswertungen-Seite: vier Sektionen, Donut + Bar-Charts statt dichter Tabellen.
// Sidebar-Filter (Zeitraum, Geschlecht) wirken auf alle Sektionen.
(function () {
    'use strict';

    const ROLE_LABELS = {
        'issuer':    'Aussteller / Ausstellerin',
        'recipient': 'Empfänger / Empfängerin',
        'witness':   'Siegler:in / Zeug:in',
        'other':     'Sonstige',
        '':          'keine Rolle',
    };
    const ROLE_ORDER = ['issuer', 'recipient', 'witness', 'other', ''];
    // Distinkte Hue-Familien, kein Konflikt mit sex-m (Aubergine) / sex-f (Petrol).
    const ROLE_COLORS = {
        'issuer':    '#b85c2f',  // Terracotta
        'recipient': '#2e7a88',  // Aqua
        'witness':   '#6b6040',  // Olive
        'other':     '#a08470',  // Sand
        '':          '#9a9590',  // Grau (keine)
    };

    const REL_LABELS = {
        'kin': 'Verwandtschaft',
        'occ': 'Beruf / Stand',
        'rep': 'Vertretung',
        'friend': 'Freundschaft',
    };
    const REL_ORDER = ['kin', 'occ', 'rep', 'friend'];
    const REL_COLORS = {
        'kin':    '#b85c2f',  // Terracotta (Verwandtschaft = warm)
        'occ':    '#c4a035',  // Gold (Beruf/Stand)
        'rep':    '#6b6040',  // Olive (Vertretung)
        'friend': '#2e7a88',  // Aqua (Freundschaft)
    };

    const SEX_LABELS_DE = {
        'm':           '♂ männlich',
        'f':           '♀ weiblich',
        'unspecified': 'ohne Angabe',
    };

    // ---------------------------------------------------------------------
    // Daten laden
    // ---------------------------------------------------------------------
    function readJson(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        try { return JSON.parse(el.textContent); }
        catch (e) { console.error('Bad JSON in', id, e); return null; }
    }
    const EPIC_A = readJson('aggregat-data-epic-a') || { observations: {} };
    const EPIC_B = readJson('aggregat-data-epic-b') || { overview: {}, labels: [] };
    const EPIC_C = readJson('aggregat-data-epic-c') || { observations: {} };

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

    // ---------------------------------------------------------------------
    // Hilfsfunktionen
    // ---------------------------------------------------------------------
    function fmt(n) {
        return (n || 0).toLocaleString('de-AT').replace(/,/g, '.');
    }
    function pct(n, total) {
        if (!total) return '–';
        return ((n / total) * 100).toFixed(1).replace('.', ',');
    }
    function decadeOf(year) { return Math.floor(year / 10) * 10; }
    function noTimeFilter() {
        return STATE.decadeMin === null && STATE.decadeMax === null;
    }
    function inDecadeRange(decade) {
        const dec = parseInt(decade, 10);
        if (STATE.decadeMin !== null && dec < STATE.decadeMin) return false;
        if (STATE.decadeMax !== null && dec > STATE.decadeMax) return false;
        return true;
    }

    // Pipeline-Underscore-Keys ("ueber_gabe") wieder lesbar machen.
    // Umlaut-Recovery muss case-sensitive sein, sonst wird "Uebergabe" nicht
    // zu "Übergabe".
    function labelize(k) {
        return k.replace(/_/g, ' ')
            .replace(/Ae/g, 'Ä').replace(/Oe/g, 'Ö').replace(/Ue/g, 'Ü')
            .replace(/ae/g, 'ä').replace(/oe/g, 'ö').replace(/ue/g, 'ü');
    }

    // CSP "style-src 'self'" blockiert inline style="..."-Attribute. Wir
    // codieren Werte als data-Attribute und projizieren sie nach jedem
    // innerHTML auf die Element-style-Property (CSP-konform via JS-IDL).
    function applyDataStyles(root) {
        if (!root) return;
        root.querySelectorAll('[data-w]').forEach(el => {
            el.style.width = el.dataset.w + '%';
        });
        root.querySelectorAll('[data-bg]').forEach(el => {
            el.style.background = el.dataset.bg;
        });
    }

    // Markiert in einer Chip-Gruppe die zu activeKey passende Schaltflaeche
    // als aktiv (CSS-Klasse + aria-pressed); alle anderen werden zurueck-
    // gesetzt. Spart sich die immer gleiche forEach-Schleife an 6 Stellen.
    function setActiveChip(group, activeKey, attr, activeClass) {
        if (!group) return;
        activeClass = activeClass || 'active';
        group.querySelectorAll('[' + attr + ']').forEach(b => {
            const isActive = b.getAttribute(attr) === activeKey;
            b.classList.toggle(activeClass, isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
    }

    // M/W-Bar + Counts; gleiche Optik in Donut-Legenden und Bezeichnungs-
    // Tabelle. Liefert HTML-Snippet, der Aufrufer entscheidet ueber Wrapper.
    function sexBarHTML(m, f) {
        const tot = (m || 0) + (f || 0);
        const mPct = tot ? (m / tot * 100) : 0;
        const fPct = tot ? (f / tot * 100) : 0;
        return `
            <span class="legend-sex-bar"
                  title="männlich ${fmt(m)} · weiblich ${fmt(f)}">
                <span class="legend-sex-bar-m" data-w="${mPct.toFixed(2)}"></span>
                <span class="legend-sex-bar-f" data-w="${fPct.toFixed(2)}"></span>
            </span>
            <span class="legend-sex-counts">
                <span class="sex-m-num">${fmt(m || 0)}</span>
                <span class="sex-sep">/</span>
                <span class="sex-f-num">${fmt(f || 0)}</span>
            </span>`;
    }

    // ---------------------------------------------------------------------
    // Donut-Renderer (Inline-SVG, keine externe Lib)
    // segments: [{key, label, value, color}, ...]
    // Konzentrische Stroke-Arcs auf einem Kreis statt Path-Arc-Kommandos —
    // einfacher zu verstehen und sauber animierbar wenn nötig.
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
                <title>${seg.label}: ${fmt(v)} (${pct(v, total)} %)</title>
            </circle>`;
            offset += len;
            return arc;
        });

        const centerLabel = opts.centerLabel || '';
        const totalText = `<text x="${cx}" y="${cy - 1}" text-anchor="middle"
            class="donut-center-value">${fmt(total)}</text>`;
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
    // entries: [{key, label, value, color, m, f, hasSex}]
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
                <span class="legend-count">${fmt(e.value)}</span>
                <span class="legend-pct">${pct(e.value, total)}&nbsp;%</span>
                ${sex}
            </li>`;
        });
        container.innerHTML = items.join('');
        applyDataStyles(container);
    }

    // ---------------------------------------------------------------------
    // Sektion 1: Funktionsrollen
    // ---------------------------------------------------------------------
    function aggregateRoles() {
        const dec = EPIC_A.observations.role_by_sex_by_decade || {};
        const persDec = EPIC_A.observations.role_persons_by_decade || {};
        const noTime = noTimeFilter();

        const mentions = {};
        for (const role of ROLE_ORDER) {
            mentions[role] = { m: 0, f: 0 };
            const byDec = dec[role] || {};
            if (noTime) {
                const full = (EPIC_A.observations.role_by_sex || {})[role] || {};
                mentions[role].m = full.m || 0;
                mentions[role].f = full.f || 0;
            } else {
                for (const [d, sexCounts] of Object.entries(byDec)) {
                    if (!inDecadeRange(d)) continue;
                    mentions[role].m += sexCounts.m || 0;
                    mentions[role].f += sexCounts.f || 0;
                }
            }
        }

        const persons = {};
        for (const role of ROLE_ORDER) {
            persons[role] = { m: 0, f: 0 };
            const byDec = persDec[role] || {};
            const seenM = new Set();
            const seenF = new Set();
            for (const [d, sexKeys] of Object.entries(byDec)) {
                if (!inDecadeRange(d)) continue;
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

        // Donut-Segmente: Wert pro Rolle gemäß Geschlecht-Filter
        const segments = ROLE_ORDER.map(r => {
            const m = data[r].m || 0;
            const f = data[r].f || 0;
            let v = m + f;
            if (sex === 'm') v = m;
            else if (sex === 'f') v = f;
            return {
                key: r,
                label: ROLE_LABELS[r] || r || '(keine)',
                value: v,
                color: ROLE_COLORS[r] || '#888',
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
        const totalM = ROLE_ORDER.reduce((s, r) => s + (data[r].m || 0), 0);
        const totalF = ROLE_ORDER.reduce((s, r) => s + (data[r].f || 0), 0);
        const grandTotal = totalM + totalF;
        const rows = [];
        for (const role of ROLE_ORDER) {
            const m = data[role].m || 0;
            const f = data[role].f || 0;
            const total = m + f;
            if (total === 0) continue;
            rows.push(`<tr data-role="${role}">
                <td class="col-label">${ROLE_LABELS[role] || role || '(keine)'}</td>
                <td class="num">${fmt(total)}</td>
                <td class="num pct">${pct(total, grandTotal)}</td>
                <td class="num sex-m">${fmt(m)}</td>
                <td class="num pct sex-m">${pct(m, total)}</td>
                <td class="num pct sex-m">${pct(m, totalM)}</td>
                <td class="num sex-f">${fmt(f)}</td>
                <td class="num pct sex-f">${pct(f, total)}</td>
                <td class="num pct sex-f">${pct(f, totalF)}</td>
            </tr>`);
        }
        rows.push(`<tr class="aggregat-row-total">
            <td class="col-label">gesamt</td>
            <td class="num">${fmt(grandTotal)}</td>
            <td class="num pct">100,0</td>
            <td class="num sex-m">${fmt(totalM)}</td>
            <td class="num pct sex-m">${pct(totalM, grandTotal)}</td>
            <td class="num pct sex-m">100,0</td>
            <td class="num sex-f">${fmt(totalF)}</td>
            <td class="num pct sex-f">${pct(totalF, grandTotal)}</td>
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

        const perType = REL_ORDER.map(t => {
            const e = overview[t] || { m: 0, f: 0, unspecified: 0 };
            const m = e.m || 0;
            const f = e.f || 0;
            const u = e.unspecified || 0;
            const total = m + f + u;
            let v = total;
            if (sex === 'm') v = m;
            else if (sex === 'f') v = f;
            else if (sex === 'unspecified') v = u;
            return { key: t, label: REL_LABELS[t], color: REL_COLORS[t], value: v, m, f, total };
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
            <td class="num">${fmt(s.total)}</td>
            <td class="num pct">${pct(s.total, grandRels)}</td>
            <td class="num sex-m">${fmt(s.m)}</td>
            <td class="num pct sex-m">${pct(s.m, s.total)}</td>
            <td class="num sex-f">${fmt(s.f)}</td>
            <td class="num pct sex-f">${pct(s.f, s.total)}</td>
            <td class="num">–</td>
        </tr>`);
        rows.push(`<tr class="aggregat-row-total">
            <td class="col-label">gesamt</td>
            <td class="num">${fmt(grandRels)}</td>
            <td class="num pct">100,0</td>
            <td class="num sex-m">${fmt(totalM)}</td>
            <td class="num pct sex-m">${pct(totalM, grandRels)}</td>
            <td class="num sex-f">${fmt(totalF)}</td>
            <td class="num pct sex-f">${pct(totalF, grandRels)}</td>
            <td class="num">${fmt(personsTotal)}</td>
        </tr>`);
        tbody.innerHTML = rows.join('');
    }

    // ---------------------------------------------------------------------
    // Sektion 3: Transaktionstypen — horizontale Balken
    // ---------------------------------------------------------------------
    function aggregateTxTypes() {
        const tl = (EPIC_C.observations || {}).tx_timeline || {};
        const noTime = noTimeFilter();
        const totals = {};
        for (const [type, byDec] of Object.entries(tl)) {
            let s = 0;
            for (const [d, c] of Object.entries(byDec)) {
                if (noTime || inDecadeRange(d)) s += c;
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

        const barRow = (label, val, cssClass = '') => {
            const wRel = (val / maxVal * 100).toFixed(2);
            return `<div class="aggregat-bar-row ${cssClass}">
                <span class="aggregat-bar-label">${label}</span>
                <div class="aggregat-bar-track">
                    <div class="aggregat-bar-fill" data-w="${wRel}"></div>
                </div>
                <span class="aggregat-bar-count">${fmt(val)}</span>
                <span class="aggregat-bar-pct">${pct(val, grandTotal)}&nbsp;%</span>
            </div>`;
        };

        const rows = top.map(([k, c]) => barRow(labelize(k), c));

        if (rest.length) {
            // Aufklappbare Sonstige-Sammelzeile: Klick toggelt is-open auf
            // dem Wrapper, das CSS zeigt dann die versteckten rest-Bars.
            const restRows = rest.map(([k, c]) => barRow(labelize(k), c, 'is-rest-item'));
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
                    <span class="aggregat-bar-count">${fmt(restSum)}</span>
                    <span class="aggregat-bar-pct">${pct(restSum, grandTotal)}&nbsp;%</span>
                </button>
                <div class="aggregat-bar-rest-items">${restRows.join('')}</div>
            </div>`);
        }

        container.innerHTML = rows.join('') ||
            '<div class="aggregat-empty">keine Daten im Filter-Zeitraum</div>';
        applyDataStyles(container);

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
                parts.push(`${fmt(notNorm)} Rechtsgeschäfte ohne normalisiertes Verb sind ausgeblendet.`);
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
                ? `${fmt(all.length)} Bezeichnungen`
                : `${fmt(filtered.length)} von ${fmt(all.length)}`;
        }

        const rows = filtered.map(l => {
            const persons = l.persons || 0;
            const barWidth = (persons / maxPersons * 100).toFixed(2);
            const variants = (l.variants || []).slice(0, 6).join(', ');
            return `<tr data-label="${encodeURIComponent(l.label)}"
                title="${variants ? 'Varianten: ' + variants : ''}">
                <td class="col-label">${l.label}</td>
                <td>${REL_LABELS[l.type] || l.type}</td>
                <td class="num col-persons">
                    <div class="cell-mini-bar">
                        <span class="cell-mini-bar-fill" data-w="${barWidth}"></span>
                        <span class="cell-mini-bar-num">${fmt(persons)}</span>
                    </div>
                </td>
                <td class="col-sexbar">${sexBarHTML(l.m || 0, l.f || 0)}</td>
            </tr>`;
        });
        tbody.innerHTML = rows.join('') ||
            '<tr><td colspan="4" class="aggregat-empty">Keine Treffer.</td></tr>';
        applyDataStyles(tbody);
    }

    // ---------------------------------------------------------------------
    // Filter-Bedienung
    // ---------------------------------------------------------------------
    function bindSexFilter() {
        const group = document.getElementById('filter-sex');
        if (!group) return;

        // Initial-Setup: aktiver Chip optisch markieren, Chips ohne Treffer
        // (count=0) ausblenden, damit kein toter Klick angeboten wird.
        setActiveChip(group, STATE.sex, 'data-sex');
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
            setActiveChip(group, STATE.sex, 'data-sex');
            renderAll();
        });
    }

    function bindRangeSlider() {
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        if (!minEl || !maxEl) return;
        const labelMin = document.getElementById('range-label-min');
        const labelMax = document.getElementById('range-label-max');
        const sliderMin = parseInt(minEl.min, 10);
        const sliderMax = parseInt(maxEl.max, 10);

        function update() {
            let lo = parseInt(minEl.value, 10);
            let hi = parseInt(maxEl.value, 10);
            if (lo > hi) { [lo, hi] = [hi, lo]; }
            // Slider voll aufgespannt = kein Filter (sonst fallen Daten
            // ohne parsbare Dekade aus den Aggregaten).
            if (lo <= sliderMin && hi >= sliderMax) {
                STATE.decadeMin = null;
                STATE.decadeMax = null;
            } else {
                STATE.decadeMin = decadeOf(lo);
                STATE.decadeMax = decadeOf(hi);
            }
            if (labelMin) labelMin.textContent = lo;
            if (labelMax) labelMax.textContent = hi;
            updateRangeVisuals(lo, hi);
            renderAll();
        }
        minEl.addEventListener('input', update);
        maxEl.addEventListener('input', update);
    }

    function updateRangeVisuals(lo, hi) {
        const histo = document.getElementById('range-histogram');
        if (!histo) return;
        histo.querySelectorAll('.range-bar').forEach(bar => {
            const dec = parseInt(bar.dataset.decade, 10);
            const inRange = (dec >= decadeOf(lo) && dec <= decadeOf(hi));
            bar.classList.toggle('range-bar--out', !inRange);
            const h = bar.dataset.height || 0;
            bar.style.setProperty('--bar-height', h + '%');
            bar.style.height = h + '%';
        });
    }

    function bindRolesToggle() {
        const grp = document.querySelector('#q-roles .aggregat-toggle');
        if (!grp) return;
        grp.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-roles-mode]');
            if (!btn) return;
            STATE.rolesMode = btn.getAttribute('data-roles-mode');
            setActiveChip(grp, STATE.rolesMode, 'data-roles-mode', 'is-active');
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
                setActiveChip(chipGroup, STATE.labelType, 'data-rel');
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
            STATE.decadeMin = null;
            STATE.decadeMax = null;
            STATE.labelSearch = '';
            STATE.labelType = 'all';
            STATE.rolesMode = 'mentions';

            setActiveChip(document.getElementById('filter-sex'), 'all', 'data-sex');
            setActiveChip(document.querySelector('.aggregat-rel-type-chips'),
                          'all', 'data-rel');
            setActiveChip(document.querySelector('#q-roles .aggregat-toggle'),
                          'mentions', 'data-roles-mode', 'is-active');

            const minEl = document.getElementById('range-min');
            const maxEl = document.getElementById('range-max');
            if (minEl && maxEl) {
                minEl.value = minEl.min;
                maxEl.value = maxEl.max;
                minEl.dispatchEvent(new Event('input'));  // triggert renderAll
            } else {
                renderAll();
            }
            const search = document.getElementById('labels-search');
            if (search) search.value = '';
        });
    }

    // ---------------------------------------------------------------------
    // Active-Filter-Strip — pro aktivem Filter eine entfernbare Pille.
    // Klick auf die Pille loescht den jeweiligen Filter und re-rendert.
    // ---------------------------------------------------------------------
    function clearTimeFilter() {
        const minEl = document.getElementById('range-min');
        const maxEl = document.getElementById('range-max');
        if (!minEl || !maxEl) return;
        minEl.value = minEl.min;
        maxEl.value = maxEl.max;
        minEl.dispatchEvent(new Event('input', { bubbles: true }));
    }
    function clearSexFilter() {
        STATE.sex = 'all';
        setActiveChip(document.getElementById('filter-sex'), 'all', 'data-sex');
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
        setActiveChip(document.querySelector('.aggregat-rel-type-chips'),
                      'all', 'data-rel');
        renderLabels();
        updateActiveFilters();
    }

    function updateActiveFilters() {
        const el = document.getElementById('active-filters');
        if (!el) return;
        el.innerHTML = '';
        const ti = (typeof TableInfra !== 'undefined') ? TableInfra : null;
        if (!ti) return;

        if (STATE.decadeMin !== null || STATE.decadeMax !== null) {
            const minEl = document.getElementById('range-min');
            const maxEl = document.getElementById('range-max');
            const lo = minEl ? minEl.value : STATE.decadeMin;
            const hi = maxEl ? maxEl.value : STATE.decadeMax;
            ti.addFilterChip(el, 'Zeitraum: ' + lo + '–' + hi, clearTimeFilter);
        }
        if (STATE.sex && STATE.sex !== 'all') {
            ti.addFilterChip(el, 'Geschlecht: ' + (SEX_LABELS_DE[STATE.sex] || STATE.sex),
                             clearSexFilter);
        }
        if (STATE.labelType && STATE.labelType !== 'all') {
            ti.addFilterChip(el, 'Bezeichnungs-Typ: ' + (REL_LABELS[STATE.labelType] || STATE.labelType),
                             clearLabelType);
        }
        if (STATE.labelSearch && STATE.labelSearch.trim()) {
            ti.addFilterChip(el, 'Bezeichnung: ' + STATE.labelSearch.trim(),
                             clearLabelSearch);
        }
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
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindSexFilter();
        bindRangeSlider();
        bindRolesToggle();
        bindLabelsToolbar();
        bindReset();
        renderAll();
    });
})();
