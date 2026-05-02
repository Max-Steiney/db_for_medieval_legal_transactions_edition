/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Exploration: Role Explorer (Epic A)
   Panel 1: Function roles by sex (bar chart)
   Panel 2: Institutional affiliation by org type (bar chart)
   Panel 3: Detail (context-dependent drill-down)
   Uses: ChartHelpers, DrillDown
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;
    let fmt = ChartHelpers.fmt;
    let TOOLTIP_CLASS = 'explore-tooltip';

    // Human-readable labels for org types
    let ORG_TYPE_LABELS = {
        'Messe': 'Messe/Stiftung',
        'Pfarre': 'Pfarre',
        'Stadt': 'Stadt',
        'Kirche_Kapelle': 'Kirche/Kapelle',
        'Altar': 'Altar',
        'Dioezese_Erzdioezese': 'Di\u00f6zese',
        'Kloster_m': 'Kloster (m.)',
        'Gemeinde': 'Gemeinde',
        'Zeche_Bruderschaft': 'Zeche/Bruderschaft',
        'OTHER': 'Sonstige',
        'Kloster_f': 'Kloster (w.)',
        'Spital_Siechenhaus': 'Spital/Siechenhaus',
        'Stadtviertel': 'Stadtviertel',
        'Herzogtum': 'Herzogtum',
        'Orden': 'Orden',
        'Burg': 'Burg',
        'Koenigreich': 'K\u00f6nigreich',
        'Universitaet': 'Universit\u00e4t',
        'Reich': 'Reich',
        'Markgrafschaft': 'Markgrafschaft',
        'Kloster': 'Kloster',
        'Kirche': 'Kirche',
        'Kapelle': 'Kapelle'
    };

    function initExploration() {
        if (!document.getElementById('explore-role-chart')) return;

        ChartHelpers.createTooltip(TOOLTIP_CLASS);

        let epicA = null;

        // Colour map
        let SEX_COLORS = {
            m: ChartHelpers.getToken('--color-sex-m') || '#2e5a88',
            f: ChartHelpers.getToken('--color-sex-f') || '#b85c2f',
            unspecified: ChartHelpers.getToken('--color-sex-none') || '#b0a99f'
        };
        let SEX_LABELS = ChartHelpers.SEX_LABELS;
        let ROLE_LABELS = ChartHelpers.ROLE_LABELS;
        let CANONICAL_ROLES = ChartHelpers.ROLE_ORDER;
        let SEX_KEYS = ['m', 'f', 'unspecified'];
        let ORG_COLOR = ChartHelpers.getToken('--color-rel-occ') || '#2e5a88';

        // State
        let RP = window.RELEASED_PERIOD || {min: 1177, max: 1414};
        let state = {
            decadeMin: RP.min,
            decadeMax: RP.max,
            sexFilter: 'all',
            tableView: false,
            instTableView: false,
            pctMode: false
        };

        let drillHandle = DrillDown.bind({});

        // -- Shared bindings --
        ChartHelpers.bindTimeRange('explore', state, function() {
            renderRoleChart();
            renderInstChart();
        });

        ChartHelpers.bindChipFilter('#explore-sex-filter .explore-chip', 'data-sex',
            state, 'sexFilter', function() {
                renderRoleChart();
                renderInstChart();
            });

        // Percentage toggle
        let pctBtn = document.getElementById('explore-pct-toggle');
        if (pctBtn) {
            pctBtn.addEventListener('click', function() {
                state.pctMode = !state.pctMode;
                pctBtn.classList.toggle('active', state.pctMode);
                pctBtn.setAttribute('aria-pressed', state.pctMode ? 'true' : 'false');
                renderRoleChart();
            });
        }

        ChartHelpers.bindToggle('explore-table-toggle', 'explore-role-chart',
            'explore-role-table', state, 'tableView', renderRoleTable);

        ChartHelpers.bindToggle('explore-inst-table-toggle', 'explore-inst-chart',
            'explore-inst-table', state, 'instTableView', renderInstTable);

        // ================================================================
        // Panel 1: Role chart
        // ================================================================

        function getFilteredData() {
            let obs = epicA.observations;
            let roleDecade = obs.role_by_sex_by_decade;

            let result = {};
            for (let ri = 0; ri < CANONICAL_ROLES.length; ri++) {
                let role = CANONICAL_ROLES[ri];
                result[role] = { m: 0, f: 0, unspecified: 0, total: 0 };

                let decadeData = roleDecade[role] || {};
                for (let dStr in decadeData) {
                    let d = parseInt(dStr, 10);
                    if (d < state.decadeMin || d > state.decadeMax) continue;
                    let sexCounts = decadeData[dStr];
                    for (let si = 0; si < SEX_KEYS.length; si++) {
                        let sex = SEX_KEYS[si];
                        result[role][sex] += sexCounts[sex] || 0;
                    }
                }
                result[role].total = result[role].m + result[role].f + result[role].unspecified;
            }
            // Merge empty-role data into "other"
            let emptyDecade = roleDecade[''] || {};
            for (let edStr in emptyDecade) {
                let ed = parseInt(edStr, 10);
                if (ed < state.decadeMin || ed > state.decadeMax) continue;
                let eSex = emptyDecade[edStr];
                for (let esi = 0; esi < SEX_KEYS.length; esi++) {
                    result.other[SEX_KEYS[esi]] += eSex[SEX_KEYS[esi]] || 0;
                }
            }
            result.other.total = result.other.m + result.other.f + result.other.unspecified;

            return result;
        }

        function renderRoleChart() {
            let data = getFilteredData();
            let wrap = document.getElementById('explore-role-chart');
            let sexes = state.sexFilter === 'all' ? SEX_KEYS : [state.sexFilter];

            // Build items for shared bar chart
            let items = [];
            for (let ri = 0; ri < CANONICAL_ROLES.length; ri++) {
                let role = CANONICAL_ROLES[ri];
                let segs = [];
                for (let si = 0; si < sexes.length; si++) {
                    let rawVal = data[role][sexes[si]] || 0;
                    let displayVal = state.pctMode && data[role].total > 0
                        ? Math.round(rawVal / data[role].total * 100)
                        : rawVal;
                    segs.push({
                        key: sexes[si],
                        value: displayVal,
                        rawValue: rawVal,
                        color: SEX_COLORS[sexes[si]]
                    });
                }
                items.push({ label: ROLE_LABELS[role] || role, role: role, segments: segs, total: data[role].total });
            }

            let legend = sexes.map(function(s) { return { label: SEX_LABELS[s], color: SEX_COLORS[s] }; });

            ChartHelpers.renderHorizontalBars(wrap, {
                items: items,
                labelWidth: 100,
                ariaLabel: 'Funktionsrollen nach Geschlecht' + (state.pctMode ? ' (prozentual)' : ''),
                tooltipClass: TOOLTIP_CLASS,
                legend: legend,
                onTip: function(item, seg) {
                    let raw = seg.rawValue !== undefined ? seg.rawValue : seg.value;
                    let pct = item.total > 0 ? Math.round(raw / item.total * 100) : 0;
                    return item.label + ' \u00B7 ' + SEX_LABELS[seg.key] + ': ' +
                        raw.toLocaleString('de-DE') + ' (' + pct + ' %)';
                },
                onClick: function(item, seg) {
                    openRoleDrillDown(item.role, seg.key);
                }
            });

            let grandTotal = 0;
            for (let ft = 0; ft < CANONICAL_ROLES.length; ft++) {
                grandTotal += data[CANONICAL_ROLES[ft]].total;
            }
            let footer = document.getElementById('explore-role-footer');
            footer.textContent = 'Datenbasis: ' + grandTotal.toLocaleString('de-DE') +
                ' Personen-Ereignis-Zuordnungen \u00B7 Zeitraum ' +
                state.decadeMin + '\u2013' + state.decadeMax;
        }

        function renderRoleTable() {
            let data = getFilteredData();
            let tbody = document.getElementById('explore-role-tbody');
            tbody.innerHTML = '';
            for (let ri = 0; ri < CANONICAL_ROLES.length; ri++) {
                let role = CANONICAL_ROLES[ri];
                let d = data[role];
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + (ROLE_LABELS[role] || role) + '</td>' +
                    '<td class="num">' + d.m.toLocaleString('de-DE') + '</td>' +
                    '<td class="num">' + d.f.toLocaleString('de-DE') + '</td>' +
                    '<td class="num">' + d.unspecified.toLocaleString('de-DE') + '</td>' +
                    '<td class="num"><strong>' + d.total.toLocaleString('de-DE') + '</strong></td>';
                tbody.appendChild(tr);
            }
        }

        function openRoleDrillDown(role, sex) {
            let drillDownData = epicA.drill_down || {};
            let roleFkeys = (drillDownData.role_sex || {})[role] || {};
            let fkeys = roleFkeys[sex] || [];
            if (role === 'other') {
                let emptyFkeys = ((drillDownData.role_sex || {})[''] || {})[sex] || [];
                fkeys = fkeys.concat(emptyFkeys);
                let seen = {};
                fkeys = fkeys.filter(function(fk) {
                    if (seen[fk]) return false;
                    seen[fk] = true;
                    return true;
                });
            }
            if (!fkeys.length) return;
            DrillDown.open(drillHandle, (ROLE_LABELS[role] || role) + ' \u00B7 ' + SEX_LABELS[sex], fkeys);
        }

        // ================================================================
        // Panel 2: Institutional affiliation (org-type bar chart)
        // ================================================================

        function getFilteredOrgData() {
            let obs = epicA.observations;
            let orgByDecade = obs.org_type_by_decade || {};
            let orgBySex = obs.org_type_by_sex || {};

            let allTypes = {};
            for (let ot in orgByDecade) { allTypes[ot] = true; }

            let result = [];
            for (let otype in allTypes) {
                let decades = orgByDecade[otype] || {};
                let total = 0;
                for (let dStr in decades) {
                    let d = parseInt(dStr, 10);
                    if (d < state.decadeMin || d > state.decadeMax) continue;
                    total += decades[dStr];
                }
                if (total === 0) continue;

                let sexData = orgBySex[otype] || {};
                let m = sexData.m || 0;
                let f = sexData.f || 0;
                let u = sexData.unspecified || 0;

                if (state.sexFilter !== 'all') {
                    if (state.sexFilter === 'm' && m === 0) continue;
                    if (state.sexFilter === 'f' && f === 0) continue;
                    if (state.sexFilter === 'unspecified' && u === 0) continue;
                }

                result.push({
                    type: otype,
                    label: ORG_TYPE_LABELS[otype] || otype,
                    total: total,
                    m: m, f: f, unspecified: u,
                    personTotal: m + f + u
                });
            }
            result.sort(function(a, b) { return b.total - a.total; });
            return result;
        }

        function renderInstChart() {
            if (!epicA) return;
            let data = getFilteredOrgData();
            let wrap = document.getElementById('explore-inst-chart');

            if (data.length === 0) {
                wrap.innerHTML = '<p class="cell-placeholder">Keine Daten f\u00fcr diesen Zeitraum.</p>';
                return;
            }

            let items = data.map(function(d) {
                return {
                    label: d.label,
                    type: d.type,
                    segments: [{ key: d.type, value: d.total, color: ORG_COLOR }],
                    total: d.total,
                    personTotal: d.personTotal,
                    m: d.m, f: d.f
                };
            });

            ChartHelpers.renderHorizontalBars(wrap, {
                items: items,
                labelWidth: 120,
                barHeight: 22,
                barGap: 6,
                groupGap: 0,
                labelFontSize: '12',
                ariaLabel: 'Organisationstypen nach Ereignish\u00e4ufigkeit',
                tooltipClass: TOOLTIP_CLASS,
                onTip: function(item) {
                    return item.label + ': ' + item.total.toLocaleString('de-DE') +
                        ' Ereignisse \u00B7 ' + item.personTotal.toLocaleString('de-DE') +
                        ' Personen (M ' + item.m + ' / W ' + item.f + ')';
                },
                onClick: function(item) {
                    openOrgDrillDown(item.type);
                }
            });

            let totalEvents = 0;
            for (let ti = 0; ti < data.length; ti++) totalEvents += data[ti].total;
            let footer = document.getElementById('explore-inst-footer');
            footer.textContent = data.length + ' Organisationstypen \u00B7 ' +
                totalEvents.toLocaleString('de-DE') + ' Ereignisse \u00B7 Zeitraum ' +
                state.decadeMin + '\u2013' + state.decadeMax;
        }

        function renderInstTable() {
            let data = getFilteredOrgData();
            let tbody = document.getElementById('explore-inst-tbody');
            tbody.innerHTML = '';
            for (let i = 0; i < data.length; i++) {
                let d = data[i];
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + esc(d.label) + '</td>' +
                    '<td class="num">' + d.m.toLocaleString('de-DE') + '</td>' +
                    '<td class="num">' + d.f.toLocaleString('de-DE') + '</td>' +
                    '<td class="num">' + d.unspecified.toLocaleString('de-DE') + '</td>' +
                    '<td class="num"><strong>' + d.personTotal.toLocaleString('de-DE') + '</strong></td>';
                tr.style.cursor = 'pointer';
                (function(item) {
                    tr.addEventListener('click', function() {
                        openOrgDrillDown(item.type);
                    });
                })(d);
                tbody.appendChild(tr);
            }
        }

        function openOrgDrillDown(orgType) {
            let fkeys = (epicA.drill_down.org_type || {})[orgType] || [];
            if (!fkeys.length) return;
            let label = ORG_TYPE_LABELS[orgType] || orgType;
            DrillDown.open(drillHandle, label + ' \u2014 Quellen', fkeys);
        }

        // ================================================================
        // Data loading
        // ================================================================

        ChartHelpers.loadJSON((window.ROOT_PATH || '.') + '/data/epic_a.json', 'explore-role-chart', function(data) {
            epicA = data;
            // E6: handle URL parameter for sex filter pre-selection
            let sexParam = EdCore.getParam('sex');
            if (sexParam && ['m', 'f', 'unspecified'].indexOf(sexParam) >= 0) {
                state.sexFilter = sexParam;
                let chips = document.querySelectorAll('#explore-sex-filter .explore-chip');
                chips.forEach(function(c) {
                    c.classList.toggle('active', c.getAttribute('data-sex') === sexParam);
                });
            }
            renderRoleChart();
            renderInstChart();
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('exploration-page')) {
            initExploration();
        }
    });

})();
