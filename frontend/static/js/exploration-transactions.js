/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Exploration: Transaction Explorer (Epic C)
   Uses: ChartHelpers, DrillDown
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;
    let fmt = ChartHelpers.fmt;
    let TOOLTIP_CLASS = 'explore-tooltip';

    function initTransactionExplorer() {
        if (!document.getElementById('explore-panel-timeline')) return;

        ChartHelpers.createTooltip(TOOLTIP_CLASS);

        let epicC = null;

        // Colour palette for top transaction types
        let TX_PALETTE = [
            '#2e5a88', '#b85c2f', '#3a7a5c', '#7b4d8e', '#c45a5a',
            '#2e7a88', '#c4a035', '#6b6040', '#7a6b8c', '#5a7a3a'
        ];
        let NOT_NORM_COLOR = ChartHelpers.getToken('--color-not-norm') || '#d4cfc8';

        let TX_LABELS = {
            '_not_normalised': 'Nicht normalisiert',
            'Kauf': 'Kauf', 'Satz': 'Satz', 'Stiftung': 'Stiftung',
            'Uebergabe': '\u00dcbergabe', 'Erbe': 'Erbe', 'Transfer': 'Transfer',
            'Richtspruch': 'Richtspruch', 'Burgrecht': 'Burgrecht',
            'Teilung': 'Teilung', 'Zuschreibung': 'Zuschreibung',
            'Verzicht': 'Verzicht', 'Grundienst': 'Grunddienst',
            'Tausch': 'Tausch', 'Leihkauf': 'Leihkauf',
            'Morgengab_Heimsteuer': 'Morgengabe/Heimsteuer',
            'Testament': 'Testament', 'Schenkung': 'Schenkung',
            'Seelgeraet': 'Seelger\u00e4t'
        };
        function txLabel(key) { return TX_LABELS[key] || key.replace(/_/g, ' '); }

        let ORG_TYPE_LABELS = {
            'Kloster_m': 'Kloster (m.)', 'Kloster_f': 'Kloster (w.)',
            'Spital_Siechenhaus': 'Spital/Siechenhaus',
            'Kirche_Kapelle': 'Kirche/Kapelle', 'Kirche': 'Kirche',
            'Kapelle': 'Kapelle', 'Zeche_Bruderschaft': 'Zeche/Bruderschaft',
            'Dioezese_Erzdioezese': 'Di\u00f6zese/Erzdi\u00f6zese',
            'Universitaet': 'Universit\u00e4t', 'Koenigreich': 'K\u00f6nigreich'
        };
        function orgTypeLabel(key) { return ORG_TYPE_LABELS[key] || key.replace(/_/g, ' '); }

        // State
        let RP = window.RELEASED_PERIOD || {min: 1177, max: 1414};
        let state = {
            decadeMin: RP.min,
            decadeMax: RP.max,
            txTableView: false,
            recipTableView: false,
            verbSearch: '',
            verbNormFilter: 'all',
            verbSortKey: 'freq',
            verbSortAsc: false
        };

        let drillHandle = DrillDown.bind({});

        // -- Shared bindings --
        ChartHelpers.bindTimeRange('explore', state, function() {
            if (epicC) {
                renderTxChart();
                renderRecipChart();
            }
        });

        ChartHelpers.bindToggle('explore-tx-table-toggle', 'explore-tx-chart',
            'explore-tx-table', state, 'txTableView', renderTxTable);

        ChartHelpers.bindToggle('explore-recip-table-toggle', 'explore-recip-chart',
            'explore-recip-table', state, 'recipTableView', renderRecipTable);

        // -- Compute filtered timeline data --
        function getFilteredTimeline() {
            let txTimeline = epicC.observations.tx_timeline;
            let result = {};
            let grandTotal = 0;
            for (let txType in txTimeline) {
                let sum = 0;
                for (let dStr in txTimeline[txType]) {
                    let d = parseInt(dStr, 10);
                    if (d < state.decadeMin || d > state.decadeMax) continue;
                    sum += txTimeline[txType][dStr];
                }
                if (sum > 0) {
                    result[txType] = sum;
                    grandTotal += sum;
                }
            }
            return { types: result, total: grandTotal };
        }

        function getDecadesInRange() {
            let decades = [];
            for (let d = state.decadeMin; d <= state.decadeMax; d += 10) {
                decades.push(d);
            }
            return decades;
        }

        // -- Render stacked bar chart (Panel 1) --
        function renderTxChart() {
            let wrap = document.getElementById('explore-tx-chart');
            wrap.innerHTML = '';
            let txTimeline = epicC.observations.tx_timeline;

            let decades = getDecadesInRange();
            if (!decades.length) return;

            let txTypes = [];
            for (let txType in txTimeline) {
                let total = 0;
                for (let d in txTimeline[txType]) total += txTimeline[txType][d];
                txTypes.push({ key: txType, total: total });
            }
            txTypes.sort(function(a, b) { return b.total - a.total; });

            let TX_COLORS = {};
            let colIdx = 0;
            for (let ti = 0; ti < txTypes.length; ti++) {
                let k = txTypes[ti].key;
                if (k === '_not_normalised') {
                    TX_COLORS[k] = NOT_NORM_COLOR;
                } else {
                    TX_COLORS[k] = TX_PALETTE[colIdx % TX_PALETTE.length];
                    colIdx++;
                }
            }

            let activeTypes = [];
            for (let ati = 0; ati < txTypes.length; ati++) {
                let atk = txTypes[ati].key;
                let hasData = false;
                for (let di = 0; di < decades.length; di++) {
                    if ((txTimeline[atk] || {})[String(decades[di])] > 0) {
                        hasData = true;
                        break;
                    }
                }
                if (hasData) activeTypes.push(atk);
            }

            let decadeStacks = [];
            let maxStack = 0;
            for (let dsi = 0; dsi < decades.length; dsi++) {
                let dd = decades[dsi];
                let stack = [];
                let stackTotal = 0;
                for (let ai = 0; ai < activeTypes.length; ai++) {
                    let val = (txTimeline[activeTypes[ai]] || {})[String(dd)] || 0;
                    stack.push({ type: activeTypes[ai], value: val });
                    stackTotal += val;
                }
                decadeStacks.push({ decade: dd, segments: stack, total: stackTotal });
                if (stackTotal > maxStack) maxStack = stackTotal;
            }
            if (maxStack === 0) maxStack = 1;

            // Legend
            let legendDiv = document.createElement('div');
            legendDiv.className = 'explore-legend explore-legend--wrap';
            let legendTypes = activeTypes.slice(0, 11);
            if (activeTypes.length > 11) {
                let nnIdx = legendTypes.indexOf('_not_normalised');
                if (nnIdx === -1) legendTypes[10] = '_not_normalised';
            }
            for (let li = 0; li < legendTypes.length; li++) {
                let item = document.createElement('span');
                item.className = 'explore-legend-item';
                let swatch = document.createElement('span');
                swatch.className = 'explore-legend-swatch';
                swatch.style.setProperty('--swatch-color', TX_COLORS[legendTypes[li]]);
                item.appendChild(swatch);
                item.appendChild(document.createTextNode(txLabel(legendTypes[li])));
                legendDiv.appendChild(item);
            }
            if (activeTypes.length > legendTypes.length) {
                let moreItem = document.createElement('span');
                moreItem.className = 'explore-legend-item explore-legend-more';
                moreItem.textContent = '+ ' + (activeTypes.length - legendTypes.length) + ' weitere';
                legendDiv.appendChild(moreItem);
            }
            wrap.appendChild(legendDiv);

            // SVG chart
            let margin = { top: 10, right: 20, bottom: 40, left: 40 };
            let chartW = wrap.clientWidth - margin.left - margin.right;
            if (chartW < 300) chartW = 300;
            let chartH = 280;
            let barW = Math.max(8, Math.floor((chartW - decades.length * 2) / decades.length));
            let actualChartW = decades.length * (barW + 2);
            let svgW = margin.left + actualChartW + margin.right;
            let svgH = margin.top + chartH + margin.bottom;

            let svg = document.createElementNS(ChartHelpers.SVG_NS, 'svg');
            svg.setAttribute('width', svgW);
            svg.setAttribute('height', svgH);
            svg.setAttribute('role', 'img');
            svg.setAttribute('aria-label', 'Transaktionstypen im Zeitverlauf');
            svg.style.display = 'block';
            svg.style.margin = '0 auto';

            // Hatch pattern for transmission gap
            let defs = document.createElementNS(ChartHelpers.SVG_NS, 'defs');
            let pattern = document.createElementNS(ChartHelpers.SVG_NS, 'pattern');
            pattern.setAttribute('id', 'gap-hatch');
            pattern.setAttribute('patternUnits', 'userSpaceOnUse');
            pattern.setAttribute('width', '8');
            pattern.setAttribute('height', '8');
            pattern.setAttribute('patternTransform', 'rotate(45)');
            let hatchLine = document.createElementNS(ChartHelpers.SVG_NS, 'line');
            hatchLine.setAttribute('x1', '0'); hatchLine.setAttribute('y1', '0');
            hatchLine.setAttribute('x2', '0'); hatchLine.setAttribute('y2', '8');
            hatchLine.setAttribute('stroke', '#e0dbd4'); hatchLine.setAttribute('stroke-width', '2');
            pattern.appendChild(hatchLine);
            defs.appendChild(pattern);
            svg.appendChild(defs);

            // Y-axis labels
            let yTicks = 5;
            for (let yt = 0; yt <= yTicks; yt++) {
                let yVal = Math.round(maxStack / yTicks * yt);
                let yPos = margin.top + chartH - (yVal / maxStack * chartH);
                let yLabel = document.createElementNS(ChartHelpers.SVG_NS, 'text');
                yLabel.setAttribute('x', margin.left - 6);
                yLabel.setAttribute('y', yPos + 4);
                yLabel.setAttribute('text-anchor', 'end');
                yLabel.setAttribute('class', 'explore-axis-label');
                yLabel.textContent = yVal;
                svg.appendChild(yLabel);
                let gridLine = document.createElementNS(ChartHelpers.SVG_NS, 'line');
                gridLine.setAttribute('x1', margin.left);
                gridLine.setAttribute('y1', yPos);
                gridLine.setAttribute('x2', margin.left + actualChartW);
                gridLine.setAttribute('y2', yPos);
                gridLine.setAttribute('class', 'explore-grid-line');
                svg.appendChild(gridLine);
            }

            // Stacked bars per decade
            for (let dbi = 0; dbi < decadeStacks.length; dbi++) {
                let ds = decadeStacks[dbi];
                let x = margin.left + dbi * (barW + 2);
                let isGap = ds.decade >= 1420 && ds.decade <= 1440;

                if (isGap && ds.total === 0) {
                    let gapRect = document.createElementNS(ChartHelpers.SVG_NS, 'rect');
                    gapRect.setAttribute('x', x);
                    gapRect.setAttribute('y', margin.top);
                    gapRect.setAttribute('width', barW);
                    gapRect.setAttribute('height', chartH);
                    gapRect.setAttribute('class', 'explore-gap-bar');
                    svg.appendChild(gapRect);
                }

                let yBottom = margin.top + chartH;
                for (let si = ds.segments.length - 1; si >= 0; si--) {
                    let seg = ds.segments[si];
                    if (seg.value === 0) continue;
                    let segH = (seg.value / maxStack) * chartH;
                    let segY = yBottom - segH;

                    let rect = document.createElementNS(ChartHelpers.SVG_NS, 'rect');
                    rect.setAttribute('x', x);
                    rect.setAttribute('y', segY);
                    rect.setAttribute('width', barW);
                    rect.setAttribute('height', segH);
                    rect.setAttribute('fill', TX_COLORS[seg.type] || '#999');
                    rect.setAttribute('class', 'explore-bar');

                    (function(type, value, decade, total) {
                        rect.addEventListener('mouseenter', function(e) {
                            let pct = total > 0 ? Math.round(value / total * 100) : 0;
                            ChartHelpers.showTooltip(TOOLTIP_CLASS,
                                esc(txLabel(type)) + ': ' +
                                value.toLocaleString('de-DE') + ' (' + pct + ' %) \u00B7 ' +
                                decade + 'er', e.clientX, e.clientY);
                        });
                        rect.addEventListener('mousemove', function(e) {
                            ChartHelpers.moveTooltip(TOOLTIP_CLASS, e.clientX, e.clientY);
                        });
                        rect.addEventListener('mouseleave', function() {
                            ChartHelpers.hideTooltip(TOOLTIP_CLASS);
                        });
                        rect.addEventListener('click', function() {
                            openTxDrillDown(type, decade);
                        });
                    })(seg.type, seg.value, ds.decade, ds.total);

                    svg.appendChild(rect);
                    yBottom = segY;
                }

                // Decade label
                let dLabel = document.createElementNS(ChartHelpers.SVG_NS, 'text');
                dLabel.setAttribute('x', x + barW / 2);
                dLabel.setAttribute('y', margin.top + chartH + 16);
                dLabel.setAttribute('text-anchor', 'middle');
                dLabel.setAttribute('class', 'explore-axis-label');
                if (dbi % 2 === 0 || decades.length <= 20) {
                    dLabel.textContent = ds.decade;
                }
                svg.appendChild(dLabel);
            }

            wrap.appendChild(svg);

            // Footer
            let filtered = getFilteredTimeline();
            let footer = document.getElementById('explore-tx-footer');
            let normInRange = filtered.types['_not_normalised'] || 0;
            let normPct = filtered.total > 0 ? Math.round((filtered.total - normInRange) / filtered.total * 100) : 0;
            footer.textContent = 'Datenbasis: ' + filtered.total.toLocaleString('de-DE') +
                ' Rechtsgesch\u00e4fte \u00B7 Normalisiert: ' + normPct + ' % \u00B7 ' +
                state.decadeMin + '\u2013' + state.decadeMax;
        }

        // -- Transaction types table --
        function renderTxTable() {
            let filtered = getFilteredTimeline();
            let tbody = document.getElementById('explore-tx-tbody');
            tbody.innerHTML = '';
            let sortedTypes = [];
            for (let t in filtered.types) {
                sortedTypes.push({ key: t, count: filtered.types[t] });
            }
            sortedTypes.sort(function(a, b) { return b.count - a.count; });
            for (let i = 0; i < sortedTypes.length; i++) {
                let item = sortedTypes[i];
                let pct = filtered.total > 0 ? (item.count / filtered.total * 100).toFixed(1) : '0.0';
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + esc(txLabel(item.key)) + '</td>' +
                    '<td class="num">' + item.count.toLocaleString('de-DE') + '</td>' +
                    '<td class="num">' + pct + ' %</td>';
                tbody.appendChild(tr);
            }
        }

        // -- Verb form browser (Panel 2) --
        let verbNormFilter = document.getElementById('explore-verb-norm-filter');

        function getFilteredVerbs() {
            let allTriggerstrings = epicC.triggerstrings || [];
            let search = state.verbSearch;
            let normFilter = state.verbNormFilter;
            return allTriggerstrings.filter(function(ts) {
                if (search && ts.form.toLowerCase().indexOf(search) === -1) return false;
                if (normFilter === 'normalised' && !ts.norm) return false;
                if (normFilter === 'not_normalised' && ts.norm) return false;
                return true;
            });
        }

        function sortVerbs(verbs) {
            let key = state.verbSortKey;
            let asc = state.verbSortAsc;
            return verbs.slice().sort(function(a, b) {
                let va = a[key], vb = b[key];
                if (typeof va === 'string') va = va.toLowerCase();
                if (typeof vb === 'string') vb = vb.toLowerCase();
                if (va < vb) return asc ? -1 : 1;
                if (va > vb) return asc ? 1 : -1;
                return 0;
            });
        }

        function renderVerbTable() {
            let verbs = sortVerbs(getFilteredVerbs());
            let tbody = document.getElementById('explore-verb-tbody');
            tbody.innerHTML = '';

            let limit = Math.min(verbs.length, 200);
            for (let i = 0; i < limit; i++) {
                appendVerbRow(tbody, verbs[i]);
            }

            if (verbs.length > limit) {
                let sentinel = document.createElement('tr');
                sentinel.innerHTML = '<td colspan="4" class="explore-loading-more">Lade weitere ' +
                    (verbs.length - limit) + ' Eintr\u00e4ge\u2026</td>';
                tbody.appendChild(sentinel);
                let observer = new IntersectionObserver(function(entries) {
                    if (entries[0].isIntersecting) {
                        observer.disconnect();
                        sentinel.remove();
                        for (let j = limit; j < verbs.length; j++) {
                            appendVerbRow(tbody, verbs[j]);
                        }
                    }
                });
                observer.observe(sentinel);
            }

            let footer = document.getElementById('explore-verb-footer');
            let normCount = verbs.filter(function(v) { return !!v.norm; }).length;
            footer.textContent = verbs.length.toLocaleString('de-DE') + ' Verbformen angezeigt' +
                ' \u00B7 davon normalisiert: ' + normCount.toLocaleString('de-DE');
        }

        function appendVerbRow(tbody, v) {
            let tr = document.createElement('tr');
            tr.className = 'explore-verb-row';
            tr.innerHTML =
                '<td class="explore-verb-form">' + esc(v.form) + '</td>' +
                '<td class="num">' + v.freq.toLocaleString('de-DE') + '</td>' +
                '<td>' + (v.norm ? esc(txLabel(v.norm)) : '<span class="text-muted">\u2014</span>') + '</td>' +
                '<td class="num explore-verb-docs">' + v.doc_count.toLocaleString('de-DE') + '</td>';
            tr.addEventListener('click', function() { openVerbDrillDown(v); });
            tbody.appendChild(tr);
        }

        ChartHelpers.bindSearch('explore-verb-search', function(q) {
            state.verbSearch = q;
            renderVerbTable();
        });

        if (verbNormFilter) {
            verbNormFilter.addEventListener('change', function() {
                state.verbNormFilter = verbNormFilter.value;
                renderVerbTable();
            });
        }

        ChartHelpers.bindSortHeaders('#explore-verb-table th[data-sort]',
            state, 'verbSortKey', 'verbSortAsc', renderVerbTable, ['form']);

        // -- Recipient chart (Panel 3) --
        function renderRecipChart() {
            let wrap = document.getElementById('explore-recip-chart');
            let recipTypeTotals = epicC.observations.recipient_type_totals || {};

            let types = [];
            for (let t in recipTypeTotals) {
                types.push({ key: t, count: recipTypeTotals[t] });
            }
            types.sort(function(a, b) { return b.count - a.count; });
            if (!types.length) { wrap.innerHTML = ''; return; }

            let items = types.map(function(tp) {
                return {
                    label: orgTypeLabel(tp.key),
                    type: tp.key,
                    segments: [{ key: tp.key, value: tp.count, color: '#7b4d8e' }],
                    total: tp.count
                };
            });

            ChartHelpers.renderHorizontalBars(wrap, {
                items: items,
                labelWidth: 140,
                barHeight: 26,
                barGap: 4,
                groupGap: 0,
                ariaLabel: 'Empf\u00e4nger nach Organisationstyp',
                onTip: function(item) {
                    return esc(item.label) + ': ' +
                        item.total.toLocaleString('de-DE') + ' Zuwendungen';
                },
                onClick: function(item) {
                    openInstDetail(item.type);
                }
            });

            let totalRecip = 0;
            for (let ri = 0; ri < types.length; ri++) totalRecip += types[ri].count;
            let footer = document.getElementById('explore-recip-footer');
            footer.textContent = 'Datenbasis: ' + totalRecip.toLocaleString('de-DE') +
                ' Empf\u00e4nger-Zuweisungen \u00B7 ' + types.length + ' Organisationstypen';
        }

        function renderRecipTable() {
            let tbody = document.getElementById('explore-recip-tbody');
            tbody.innerHTML = '';
            let recipTypeTotals = epicC.observations.recipient_type_totals || {};
            let types = [];
            for (let t in recipTypeTotals) {
                types.push({ key: t, count: recipTypeTotals[t] });
            }
            types.sort(function(a, b) { return b.count - a.count; });
            for (let i = 0; i < types.length; i++) {
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + esc(orgTypeLabel(types[i].key)) + '</td>' +
                    '<td class="num">' + types[i].count.toLocaleString('de-DE') + '</td>';
                tbody.appendChild(tr);
            }
        }

        // -- Institution detail overlay --
        let instOverlay = document.getElementById('explore-inst-detail');
        let instClose = document.getElementById('explore-inst-detail-close');
        let instTitle = document.getElementById('explore-inst-detail-title');
        let instTbody = document.getElementById('explore-inst-detail-tbody');
        let instCount = document.getElementById('explore-inst-detail-count');

        function closeInstDetail() {
            if (instOverlay) { instOverlay.classList.add('hidden'); document.body.style.overflow = ''; }
        }
        if (instClose) instClose.addEventListener('click', closeInstDetail);
        if (instOverlay) {
            instOverlay.addEventListener('click', function(e) {
                if (e.target === instOverlay) closeInstDetail();
            });
        }

        function openInstDetail(orgType) {
            let allRecipients = epicC.recipients || [];
            let institutions = allRecipients.filter(function(r) { return r.type === orgType; });
            institutions.sort(function(a, b) { return b.count - a.count; });

            instTitle.textContent = orgTypeLabel(orgType) + ' \u2014 Einzelinstitutionen';
            instTbody.innerHTML = '';
            for (let i = 0; i < institutions.length; i++) {
                let inst = institutions[i];
                let tr = document.createElement('tr');
                tr.className = 'explore-verb-row';
                tr.innerHTML =
                    '<td>' + esc(inst.name || inst.id) + '</td>' +
                    '<td>' + esc(orgTypeLabel(inst.type)) + '</td>' +
                    '<td class="num">' + inst.count.toLocaleString('de-DE') + '</td>';
                (function(orgId, orgName) {
                    tr.addEventListener('click', function() {
                        closeInstDetail();
                        openSupporterDrillDown(orgId, orgName);
                    });
                })(inst.id, inst.name || inst.id);
                instTbody.appendChild(tr);
            }
            instCount.textContent = institutions.length + ' Institutionen';
            instOverlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (instOverlay && !instOverlay.classList.contains('hidden')) closeInstDetail();
            }
        });

        // -- Drill-down functions --
        function openTxDrillDown(txType, decade) {
            let dd = epicC.drill_down || {};
            let fkeys = ((dd.tx_type_decade || {})[txType] || {})[String(decade)] || [];
            DrillDown.open(drillHandle, txLabel(txType) + ' \u00B7 ' + decade + 'er', fkeys);
        }

        function openVerbDrillDown(verb) {
            let fkeys = verb.file_keys || [];
            DrillDown.open(drillHandle, '\u201E' + verb.form + '\u201C' +
                (verb.norm ? ' \u2192 ' + txLabel(verb.norm) : ''), fkeys);
        }

        function openSupporterDrillDown(orgId, orgName) {
            let supporters = epicC.org_supporters[orgId] || [];
            let fkeys = [];
            for (let i = 0; i < supporters.length; i++) {
                if (fkeys.indexOf(supporters[i].file_key) === -1) fkeys.push(supporters[i].file_key);
            }
            DrillDown.open(drillHandle, orgName + ' \u2014 Zuwendungen', fkeys);
        }

        // ── E4: Org Type × Transaction Type Matrix ──

        function renderOrgTxMatrix() {
            let otData = epicC && epicC.org_tx;
            let container = document.getElementById('explore-orgtx-matrix');
            let statsEl = document.getElementById('explore-orgtx-stats');
            if (!otData || !container) return;

            let cov = otData.coverage || {};
            if (statsEl) {
                statsEl.textContent = cov.matched_with_tx_type + ' zugeordnete Empfänger-Events von ' +
                    cov.total_recipient_events + ' (' + cov.match_rate + ' %)';
            }

            let cells = otData.cells || [];
            if (!cells.length) {
                container.innerHTML = '<p class="explore-hint">Keine Daten.</p>';
                return;
            }

            // Build unique org types and tx types
            let orgTypes = [];
            let txTypes = [];
            let orgSet = {};
            let txSet = {};
            let cellMap = {};
            let maxCount = 0;
            cells.forEach(function(c) {
                if (!orgSet[c.org_type]) { orgTypes.push(c.org_type); orgSet[c.org_type] = true; }
                if (!txSet[c.tx_type]) { txTypes.push(c.tx_type); txSet[c.tx_type] = true; }
                cellMap[c.org_type + '__' + c.tx_type] = c.count;
                if (c.count > maxCount) maxCount = c.count;
            });

            // Limit to top 12 tx types for readability
            txTypes = txTypes.slice(0, 12);

            // Render as HTML table (heatmap-style with opacity encoding)
            let html = '<div class="explore-heatmap-scroll"><table class="explore-data-table explore-heatmap-table">' +
                '<thead><tr><th>Org-Typ</th>';
            txTypes.forEach(function(tx) { html += '<th class="num explore-heatmap-th-vertical">' + esc(tx) + '</th>'; });
            html += '</tr></thead><tbody>';

            orgTypes.forEach(function(ot) {
                html += '<tr><td>' + esc(ot) + '</td>';
                txTypes.forEach(function(tx) {
                    let key = ot + '__' + tx;
                    let count = cellMap[key] || 0;
                    let opacity = count > 0 ? 0.15 + 0.85 * (count / maxCount) : 0;
                    let textCls = opacity > 0.5 ? ' explore-heatmap-cell--inverse' : '';
                    html += '<td class="num explore-heatmap-cell' + textCls +
                        '" data-heat-opacity="' + opacity.toFixed(2) + '"' +
                        (count > 0 ? ' data-ot="' + esc(ot) + '" data-tx="' + esc(tx) + '"' : '') + '>' +
                        (count > 0 ? count : '') + '</td>';
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            container.innerHTML = html;
            container.querySelectorAll('.explore-heatmap-cell').forEach(function(td) {
                let op = parseFloat(td.getAttribute('data-heat-opacity')) || 0;
                td.style.setProperty('--heat-opacity', op);
                if (op > 0) td.style.setProperty('--heat-cursor', 'pointer');
            });

            // Drill-down on cells
            container.querySelectorAll('[data-ot]').forEach(function(td) {
                td.addEventListener('click', function() {
                    let ot = td.getAttribute('data-ot');
                    let tx = td.getAttribute('data-tx');
                    let fkeys = (otData.drill_down || {})[ot + '__' + tx] || [];
                    if (fkeys.length) {
                        DrillDown.open(drillHandle, ot + ' × ' + tx, fkeys);
                    }
                });
            });
        }

        // -- Load data and render --
        ChartHelpers.loadJSON((window.ROOT_PATH || '.') + '/data/epic_c.json', 'explore-tx-chart', function(data) {
            epicC = data;
            renderTxChart();
            renderVerbTable();
            renderRecipChart();
            renderOrgTxMatrix();
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('exploration-page')) {
            initTransactionExplorer();
        }
    });

})();
