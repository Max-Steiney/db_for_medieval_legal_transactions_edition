/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Exploration: Relationship Explorer (Epic B)
   Uses: ChartHelpers, DrillDown
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;
    let fmt = ChartHelpers.fmt;
    let TOOLTIP_CLASS = 'explore-tooltip';

    function initNetworkExplorer() {
        if (!document.getElementById('explore-rel-chart')) return;

        ChartHelpers.createTooltip(TOOLTIP_CLASS);
        let drillHandle = DrillDown.bind({});

        let epicB = null;

        // Colours
        let REL_COLORS = {
            kin: ChartHelpers.getToken('--color-rel-kin') || '#c45a5a',
            occ: ChartHelpers.getToken('--color-rel-occ') || '#2e5a88',
            rep: ChartHelpers.getToken('--color-rel-rep') || '#3a7a5c',
            friend: ChartHelpers.getToken('--color-rel-friend') || '#c4a035'
        };
        let REL_LABELS = {
            kin: 'Verwandtschaft', occ: 'Beruf',
            rep: 'Vertretung', friend: 'Freundschaft'
        };
        let SEX_LABELS = ChartHelpers.SEX_LABELS;
        let SEX_COLORS = {
            m: ChartHelpers.getToken('--color-sex-m') || '#2e5a88',
            f: ChartHelpers.getToken('--color-sex-f') || '#b85c2f',
            unspecified: ChartHelpers.getToken('--color-sex-none') || '#b0a99f'
        };
        let REL_TYPES = ['kin', 'occ', 'rep', 'friend'];
        let SEX_KEYS = ['m', 'f', 'unspecified'];

        // State
        let RP = window.RELEASED_PERIOD || {min: 1177, max: 1414};
        let state = {
            decadeMin: RP.min,
            decadeMax: RP.max,
            typeFilter: 'all',
            sexFilter: 'all',
            labelSearch: '',
            labelTableView: false,
            overviewTableView: false,
            selectedLabel: null,
            labelSortKey: 'total',
            labelSortAsc: false
        };

        // -- Shared bindings --
        ChartHelpers.bindTimeRange('explore-rel', state, renderAll);

        ChartHelpers.bindChipFilter('#explore-rel-type-filter .explore-chip', 'data-rel',
            state, 'typeFilter', renderAll);

        ChartHelpers.bindChipFilter('#explore-rel-sex-filter .explore-chip', 'data-sex',
            state, 'sexFilter', renderAll);

        ChartHelpers.bindToggle('explore-overview-table-toggle', 'explore-rel-chart',
            'explore-rel-overview-table', state, 'overviewTableView', renderOverviewTable);

        ChartHelpers.bindToggle('explore-label-table-toggle', 'explore-label-heatmap',
            'explore-label-table', state, 'labelTableView', renderLabelTable);

        ChartHelpers.bindSearch('explore-label-search', function(q) {
            state.labelSearch = q;
            if (state.labelTableView) {
                renderLabelTable();
            } else {
                renderLabelHeatmap();
            }
        });

        // -- Person search --
        let personSearchInput = document.getElementById('explore-person-search');
        let personSearchTimer = null;
        personSearchInput.addEventListener('input', function() {
            clearTimeout(personSearchTimer);
            personSearchTimer = setTimeout(function() {
                let q = personSearchInput.value.toLowerCase().trim();
                if (q.length < 2) return;
                renderPersonSearchResults(q);
            }, 300);
        });

        // ── Compute filtered overview data ──
        function getFilteredOverview() {
            let obs = epicB.overview;
            let tbsd = obs.type_by_sex_by_decade;
            let types = state.typeFilter === 'all' ? REL_TYPES : [state.typeFilter];
            let result = {};
            for (let ti = 0; ti < types.length; ti++) {
                let t = types[ti];
                result[t] = { m: 0, f: 0, unspecified: 0, total: 0 };
                let decadeData = tbsd[t] || {};
                for (let dStr in decadeData) {
                    let d = parseInt(dStr, 10);
                    if (d < state.decadeMin || d > state.decadeMax) continue;
                    let sexCounts = decadeData[dStr];
                    for (let si = 0; si < SEX_KEYS.length; si++) {
                        result[t][SEX_KEYS[si]] += sexCounts[SEX_KEYS[si]] || 0;
                    }
                }
                result[t].total = result[t].m + result[t].f + result[t].unspecified;
            }
            return result;
        }

        // ── Render overview bar chart ──
        function renderOverviewChart() {
            let data = getFilteredOverview();
            let wrap = document.getElementById('explore-rel-chart');

            let types = state.typeFilter === 'all' ? REL_TYPES : [state.typeFilter];
            let sexes = state.sexFilter === 'all' ? SEX_KEYS : [state.sexFilter];

            let items = types.map(function(relType) {
                let segs = sexes.map(function(sex) {
                    return { key: sex, value: data[relType][sex] || 0, color: SEX_COLORS[sex] };
                });
                return { label: REL_LABELS[relType] || relType, relType: relType, segments: segs, total: data[relType].total };
            });

            let legend = sexes.map(function(s) { return { label: esc(SEX_LABELS[s]), color: SEX_COLORS[s] }; });

            ChartHelpers.renderHorizontalBars(wrap, {
                items: items,
                labelWidth: 120,
                ariaLabel: 'Beziehungstypen nach Geschlecht',
                legend: legend,
                onTip: function(item, seg) {
                    let pct = item.total > 0 ? Math.round(seg.value / item.total * 100) : 0;
                    return esc(item.label) + ' \u00B7 ' + esc(SEX_LABELS[seg.key]) +
                        ': ' + fmt(seg.value) + ' (' + pct + '\u00A0%)';
                },
                onClick: function(item, seg) {
                    openTypeSexDrillDown(item.relType, seg.key);
                }
            });

            // Footer
            let grandTotal = 0;
            for (let ft = 0; ft < types.length; ft++) {
                grandTotal += data[types[ft]].total;
            }
            let footer = document.getElementById('explore-overview-footer');
            footer.textContent = 'Datenbasis: ' + fmt(grandTotal) +
                ' annotierte Beziehungen \u00B7 Zeitraum ' +
                state.decadeMin + '\u2013' + state.decadeMax;
        }

        // ── Render overview table ──
        function renderOverviewTable() {
            let data = getFilteredOverview();
            let types = state.typeFilter === 'all' ? REL_TYPES : [state.typeFilter];
            let tbody = document.getElementById('explore-rel-overview-tbody');
            tbody.innerHTML = '';
            for (let ti = 0; ti < types.length; ti++) {
                let t = types[ti];
                let d = data[t];
                let tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + esc(REL_LABELS[t] || t) + '</td>' +
                    '<td class="num">' + fmt(d.m) + '</td>' +
                    '<td class="num">' + fmt(d.f) + '</td>' +
                    '<td class="num">' + fmt(d.unspecified) + '</td>' +
                    '<td class="num"><strong>' + fmt(d.total) + '</strong></td>';
                tbody.appendChild(tr);
            }
        }

        // ── Get filtered labels ──
        function getFilteredLabels() {
            let labels = epicB.labels;
            let filtered = [];
            for (let i = 0; i < labels.length; i++) {
                let lb = labels[i];
                if (state.typeFilter !== 'all' && lb.type !== state.typeFilter) continue;
                if (state.labelSearch && lb.label.toLowerCase().indexOf(state.labelSearch) < 0) continue;
                filtered.push(lb);
            }
            return filtered;
        }

        // ── Heatmap pagination ──
        let heatmapLimit = 20;
        let HEATMAP_STEPS = [20, 60, Infinity];

        // ── Render label heatmap ──
        function renderLabelHeatmap() {
            let wrap = document.getElementById('explore-label-heatmap');
            wrap.innerHTML = '';

            let filtered = getFilteredLabels();
            let labels = filtered.slice(0, heatmapLimit);
            if (labels.length === 0) {
                wrap.innerHTML = '<p class="explore-hint">Keine Bezeichnungen gefunden.</p>';
                return;
            }

            let sexes = state.sexFilter === 'all' ? SEX_KEYS : [state.sexFilter];

            // Hide 'unspecified' column if all visible labels have 0
            if (sexes.length > 1) {
                let hasUnspecified = false;
                for (let ui = 0; ui < labels.length; ui++) {
                    if ((labels[ui].unspecified || 0) > 0) { hasUnspecified = true; break; }
                }
                if (!hasUnspecified) {
                    sexes = sexes.filter(function(s) { return s !== 'unspecified'; });
                }
            }

            let maxCount = 1;
            for (let mi = 0; mi < labels.length; mi++) {
                for (let si = 0; si < sexes.length; si++) {
                    let c = labels[mi][sexes[si]] || 0;
                    if (c > maxCount) maxCount = c;
                }
            }

            let labelW = 140;
            let cellW = 80;
            let cellH = 22;
            let cellGap = 2;
            let headerH = 28;
            let typeColW = 20;
            let totalW = labelW + typeColW + sexes.length * (cellW + cellGap) + 10;
            let totalH = headerH + labels.length * (cellH + cellGap);

            let svg = document.createElementNS(ChartHelpers.SVG_NS, 'svg');
            svg.setAttribute('width', totalW);
            svg.setAttribute('height', totalH);
            svg.setAttribute('role', 'img');
            svg.setAttribute('aria-label', 'Heatmap der Beziehungsbezeichnungen');
            svg.style.display = 'block';

            // Column headers
            for (let hi = 0; hi < sexes.length; hi++) {
                let headerText = document.createElementNS(ChartHelpers.SVG_NS, 'text');
                headerText.setAttribute('x', labelW + typeColW + hi * (cellW + cellGap) + cellW / 2);
                headerText.setAttribute('y', headerH - 8);
                headerText.setAttribute('text-anchor', 'middle');
                headerText.setAttribute('class', 'explore-heatmap-header');
                headerText.textContent = SEX_LABELS[sexes[hi]];
                svg.appendChild(headerText);
            }

            // Rows
            for (let ri = 0; ri < labels.length; ri++) {
                let lb = labels[ri];
                let rowY = headerH + ri * (cellH + cellGap);

                let labelText = document.createElementNS(ChartHelpers.SVG_NS, 'text');
                labelText.setAttribute('x', labelW - 4);
                labelText.setAttribute('y', rowY + cellH / 2 + 4);
                labelText.setAttribute('text-anchor', 'end');
                labelText.setAttribute('class', 'explore-heatmap-label');
                let displayLabel = lb.label.length > 18 ? lb.label.substring(0, 16) + '\u2026' : lb.label;
                labelText.textContent = displayLabel;
                svg.appendChild(labelText);

                let typeRect = document.createElementNS(ChartHelpers.SVG_NS, 'rect');
                typeRect.setAttribute('x', labelW + 2);
                typeRect.setAttribute('y', rowY + 2);
                typeRect.setAttribute('width', typeColW - 6);
                typeRect.setAttribute('height', cellH - 4);
                typeRect.setAttribute('rx', 3);
                typeRect.setAttribute('fill', REL_COLORS[lb.type] || '#999');
                svg.appendChild(typeRect);

                for (let ci = 0; ci < sexes.length; ci++) {
                    let sex = sexes[ci];
                    let count = lb[sex] || 0;
                    let cx = labelW + typeColW + ci * (cellW + cellGap);
                    let opacity = count > 0 ? 0.15 + 0.85 * (count / maxCount) : 0.05;

                    let cell = document.createElementNS(ChartHelpers.SVG_NS, 'rect');
                    cell.setAttribute('x', cx);
                    cell.setAttribute('y', rowY);
                    cell.setAttribute('width', cellW);
                    cell.setAttribute('height', cellH);
                    cell.setAttribute('rx', 3);
                    cell.setAttribute('fill', REL_COLORS[lb.type] || '#999');
                    cell.setAttribute('opacity', opacity);
                    cell.setAttribute('class', 'explore-heatmap-cell');

                    (function(label, type, s, cnt, total, variants) {
                        cell.addEventListener('mouseenter', function(e) {
                            let pct = total > 0 ? Math.round(cnt / total * 100) : 0;
                            let tip = esc(label) + ' \u00B7 ' + esc(SEX_LABELS[s]) +
                                ': ' + fmt(cnt) + ' (' + pct + '\u00A0%)';
                            if (variants && variants.length) {
                                tip += '<br><small>auch: ' + esc(variants.join(', ')) + '</small>';
                            }
                            ChartHelpers.showTooltip(TOOLTIP_CLASS, tip, e.clientX, e.clientY);
                        });
                        cell.addEventListener('mouseleave', function() { ChartHelpers.hideTooltip(TOOLTIP_CLASS); });
                        cell.addEventListener('click', function() {
                            showLabelDetail(label, type, s);
                        });
                    })(lb.label, lb.type, sex, count, lb.total, lb.variants || []);

                    svg.appendChild(cell);

                    if (count > 0) {
                        let countText = document.createElementNS(ChartHelpers.SVG_NS, 'text');
                        countText.setAttribute('x', cx + cellW / 2);
                        countText.setAttribute('y', rowY + cellH / 2 + 4);
                        countText.setAttribute('text-anchor', 'middle');
                        countText.setAttribute('class', 'explore-heatmap-count');
                        countText.setAttribute('pointer-events', 'none');
                        countText.textContent = fmt(count);
                        svg.appendChild(countText);
                    }
                }
            }

            wrap.appendChild(svg);

            // Legend
            let legendDiv = document.createElement('div');
            legendDiv.className = 'explore-legend';
            let typesToShow = state.typeFilter === 'all' ? REL_TYPES : [state.typeFilter];
            for (let tl = 0; tl < typesToShow.length; tl++) {
                let tItem = document.createElement('span');
                tItem.className = 'explore-legend-item';
                let swatch = document.createElement('span');
                swatch.className = 'explore-legend-swatch';
                swatch.style.setProperty('--swatch-color', REL_COLORS[typesToShow[tl]]);
                tItem.appendChild(swatch);
                tItem.appendChild(document.createTextNode(REL_LABELS[typesToShow[tl]]));
                legendDiv.appendChild(tItem);
            }
            wrap.appendChild(legendDiv);

            // "Show more" button
            if (labels.length < filtered.length) {
                let moreBtn = document.createElement('button');
                moreBtn.className = 'explore-btn explore-btn--secondary';
                let nextStep = Infinity;
                for (let nsi = 0; nsi < HEATMAP_STEPS.length; nsi++) {
                    if (HEATMAP_STEPS[nsi] > heatmapLimit) { nextStep = HEATMAP_STEPS[nsi]; break; }
                }
                let nextCount = nextStep === Infinity ? filtered.length : Math.min(nextStep, filtered.length);
                moreBtn.textContent = 'Mehr anzeigen (' + nextCount + ' von ' + fmt(filtered.length) + ')';
                moreBtn.addEventListener('click', function() {
                    heatmapLimit = nextStep;
                    renderLabelHeatmap();
                });
                wrap.appendChild(moreBtn);
            }

            let footer = document.getElementById('explore-label-footer');
            let shown = labels.length;
            let total = filtered.length;
            footer.textContent = shown < total ?
                'Zeige ' + shown + ' von ' + fmt(total) + ' Bezeichnungen' :
                fmt(total) + ' Bezeichnungen';
        }

        // ── Render label table ──
        function renderLabelTable() {
            let filtered = getFilteredLabels();
            filtered.sort(function(a, b) {
                let key = state.labelSortKey;
                let va = key === 'label' ? a.label.toLowerCase() : (key === 'type' ? a.type : (a[key] || 0));
                let vb = key === 'label' ? b.label.toLowerCase() : (key === 'type' ? b.type : (b[key] || 0));
                if (va < vb) return state.labelSortAsc ? -1 : 1;
                if (va > vb) return state.labelSortAsc ? 1 : -1;
                return 0;
            });

            let tbody = document.getElementById('explore-label-tbody');
            tbody.innerHTML = '';
            let maxRows = 200;
            let count = Math.min(filtered.length, maxRows);
            for (let i = 0; i < count; i++) {
                let lb = filtered[i];
                let tr = document.createElement('tr');
                tr.className = 'explore-label-row';
                let typeMod = REL_TYPES.indexOf(lb.type) >= 0 ? lb.type : 'none';
                tr.innerHTML =
                    '<td>' + esc(lb.label) +
                    ' <span class="explore-rel-badge explore-rel-badge--' + typeMod + '">' +
                    esc(REL_LABELS[lb.type] || lb.type) + '</span></td>' +
                    '<td>' + esc(REL_LABELS[lb.type] || lb.type) + '</td>' +
                    '<td class="num">' + fmt(lb.m) + '</td>' +
                    '<td class="num">' + fmt(lb.f) + '</td>' +
                    '<td class="num"><strong>' + fmt(lb.total) + '</strong></td>';
                (function(label, type) {
                    tr.addEventListener('click', function() {
                        showLabelDetail(label, type, null);
                    });
                })(lb.label, lb.type);
                tbody.appendChild(tr);
            }

            ChartHelpers.bindSortHeaders('#explore-label-table .sortable',
                state, 'labelSortKey', 'labelSortAsc', renderLabelTable, ['label', 'type']);

            let footer = document.getElementById('explore-label-footer');
            footer.textContent = count < filtered.length ?
                'Zeige ' + count + ' von ' + fmt(filtered.length) + ' Bezeichnungen' :
                fmt(filtered.length) + ' Bezeichnungen';
        }

        // ── Show label detail in Panel 3 ──
        function showLabelDetail(label, type, sex) {
            state.selectedLabel = { label: label, type: type, sex: sex };
            let body = document.getElementById('explore-detail-body');
            let title = document.getElementById('explore-detail-title');
            body.innerHTML = '';

            let heading = esc(label) + ' (' + esc(REL_LABELS[type] || type) + ')';
            if (sex) heading += ' \u00B7 ' + esc(SEX_LABELS[sex]);
            title.innerHTML = heading;

            let labelLowerForLookup = label.toLowerCase();
            for (let vi = 0; vi < epicB.labels.length; vi++) {
                if (epicB.labels[vi].label.toLowerCase() === labelLowerForLookup &&
                    epicB.labels[vi].type === type) {
                    let vars = epicB.labels[vi].variants;
                    if (vars && vars.length) {
                        title.innerHTML += ' <small class="text-muted-inline">(auch: ' +
                            esc(vars.join(', ')) + ')</small>';
                    }
                    break;
                }
            }

            let persons = epicB.persons;
            let matches = [];
            let labelLower = label.toLowerCase();
            for (let i = 0; i < persons.length; i++) {
                let p = persons[i];
                if (sex && p.sex !== sex) continue;
                let rels = p.rels;
                let matchingFkeys = [];
                for (let j = 0; j < rels.length; j++) {
                    let relLabel = (rels[j].ln || rels[j].l || '').toLowerCase();
                    if (rels[j].t === type && relLabel === labelLower) {
                        if (rels[j].f) matchingFkeys.push(rels[j].f);
                    }
                }
                if (matchingFkeys.length > 0) {
                    matches.push({ id: p.id, name: p.name, sex: p.sex, file_keys: matchingFkeys });
                }
            }

            if (matches.length === 0) {
                body.innerHTML = '<p class="explore-hint">Keine Personen gefunden.</p>';
                return;
            }

            let table = document.createElement('table');
            table.className = 'explore-data-table';
            table.innerHTML = '<thead><tr><th>Person</th><th>Geschlecht</th><th>Belege</th></tr></thead>';
            let tbody = document.createElement('tbody');

            for (let mi = 0; mi < matches.length; mi++) {
                let m = matches[mi];
                let tr = document.createElement('tr');
                tr.className = 'explore-label-row';
                tr.innerHTML =
                    '<td>' + esc(m.name) + '</td>' +
                    '<td>' + esc(SEX_LABELS[m.sex] || m.sex) + '</td>' +
                    '<td class="num">' + m.file_keys.length + '</td>';
                (function(name, fkeys) {
                    tr.addEventListener('click', function() {
                        DrillDown.open(drillHandle, name, fkeys);
                    });
                })(m.name, m.file_keys);
                tbody.appendChild(tr);
            }
            table.appendChild(tbody);
            body.appendChild(table);

            let detailFooter = document.getElementById('explore-detail-footer');
            detailFooter.textContent = fmt(matches.length) + ' Personen mit dieser Bezeichnung';

            let detailPanel = document.getElementById('explore-panel-detail');
            detailPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            detailPanel.classList.add('explore-panel--highlight');
            setTimeout(function() {
                detailPanel.classList.remove('explore-panel--highlight');
            }, 1200);
        }

        // ── Person search results ──
        function renderPersonSearchResults(query) {
            let body = document.getElementById('explore-detail-body');
            let title = document.getElementById('explore-detail-title');
            body.innerHTML = '';
            title.textContent = 'Personensuche: ' + esc(query);

            let persons = epicB.persons;
            let matches = [];
            for (let i = 0; i < persons.length && matches.length < 50; i++) {
                if (persons[i].name.toLowerCase().indexOf(query) >= 0) {
                    matches.push(persons[i]);
                }
            }

            if (matches.length === 0) {
                body.innerHTML = '<p class="explore-hint">Keine Personen gefunden.</p>';
                return;
            }

            let table = document.createElement('table');
            table.className = 'explore-data-table';
            table.innerHTML = '<thead><tr><th>Person</th><th>Geschlecht</th><th>Beziehungen</th></tr></thead>';
            let tbody = document.createElement('tbody');

            for (let mi = 0; mi < matches.length; mi++) {
                let p = matches[mi];
                let tr = document.createElement('tr');
                tr.className = 'explore-label-row';

                let relSummary = {};
                let allFkeys = [];
                for (let ri = 0; ri < p.rels.length; ri++) {
                    let rel = p.rels[ri];
                    relSummary[rel.t] = (relSummary[rel.t] || 0) + 1;
                    if (rel.f) allFkeys.push(rel.f);
                }
                let badges = '';
                for (let t = 0; t < REL_TYPES.length; t++) {
                    let rt = REL_TYPES[t];
                    if (relSummary[rt]) {
                        badges += '<span class="explore-rel-badge explore-rel-badge--' + rt + '">' +
                            relSummary[rt] + ' ' + esc(REL_LABELS[rt]) + '</span> ';
                    }
                }

                tr.innerHTML =
                    '<td>' + esc(p.name) + '</td>' +
                    '<td>' + esc(SEX_LABELS[p.sex] || p.sex) + '</td>' +
                    '<td>' + badges + '</td>';
                (function(name, fkeys) {
                    tr.addEventListener('click', function() {
                        if (fkeys.length) DrillDown.open(drillHandle, name, fkeys);
                    });
                })(p.name, allFkeys);
                tbody.appendChild(tr);
            }
            table.appendChild(tbody);
            body.appendChild(table);

            let detailFooter = document.getElementById('explore-detail-footer');
            detailFooter.textContent = matches.length >= 50 ?
                'Erste 50 Treffer angezeigt' : fmt(matches.length) + ' Treffer';
        }

        // ── Drill-down for type × sex bar click ──
        function openTypeSexDrillDown(type, sex) {
            let dd = epicB.drill_down || {};
            let ts = dd.type_sex || {};
            let key = type + '_' + sex;
            let fkeys = ts[key] || [];
            if (!fkeys.length) return;
            DrillDown.open(drillHandle, esc(REL_LABELS[type]) + ' \u00B7 ' + esc(SEX_LABELS[sex]), fkeys);
        }

        // ── Render all panels ──
        function renderAll() {
            if (!epicB) return;
            renderOverviewChart();
            if (state.overviewTableView) renderOverviewTable();
            if (state.labelTableView) {
                renderLabelTable();
            } else {
                renderLabelHeatmap();
            }
        }

        // ── E5: Representation Direction Panel ──

        function renderRepDirection() {
            let repData = epicB && epicB.rep_direction;
            let repPanels = document.getElementById('explore-rep-panels');
            if (!repData || !repPanels) return;

            let matrix = repData.matrix || {};
            let total = repData.total || 0;
            let statsEl = document.getElementById('explore-rep-stats');
            if (statsEl) statsEl.textContent = total + ' Vertretungsbeziehungen';

            // Render 2x2 matrix as simple HTML table
            let matrixEl = document.getElementById('explore-rep-matrix');
            if (matrixEl) {
                let sexLabels = ChartHelpers.SEX_LABELS;
                let sexKeys = ['m', 'f', 'unspecified'];
                let html = '<table class="explore-data-table explore-rep-matrix-table">' +
                    '<thead><tr><th>Vertreter \\ Vertretene</th>';
                sexKeys.forEach(function(s) { html += '<th class="num">' + esc(sexLabels[s]) + '</th>'; });
                html += '</tr></thead><tbody>';
                sexKeys.forEach(function(repSex) {
                    html += '<tr><td><strong>' + esc(sexLabels[repSex]) + '</strong></td>';
                    sexKeys.forEach(function(prinSex) {
                        let key = repSex + '>' + prinSex;
                        let count = matrix[key] || 0;
                        let opacity = count > 0 ? Math.min(0.15 + count / total * 3, 0.8) : 0;
                        html += '<td class="num explore-heatmap-cell" data-heat-opacity="' +
                            opacity.toFixed(3) + '" data-dir="' + key + '">' + count + '</td>';
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                matrixEl.innerHTML = html;
                // Apply per-cell custom properties from data-heat-opacity attribute.
                matrixEl.querySelectorAll('.explore-heatmap-cell').forEach(function(td) {
                    let op = parseFloat(td.getAttribute('data-heat-opacity')) || 0;
                    td.style.setProperty('--heat-opacity', op);
                    if (op > 0) td.style.setProperty('--heat-cursor', 'pointer');
                });

                // Drill-down on matrix cells
                matrixEl.querySelectorAll('[data-dir]').forEach(function(td) {
                    td.addEventListener('click', function() {
                        let dirKey = td.getAttribute('data-dir');
                        let fkeys = (repData.drill_down || {})[dirKey] || [];
                        if (fkeys.length) {
                            let parts = dirKey.split('>');
                            DrillDown.open(drillHandle,
                                'Vertretung: ' + sexLabels[parts[0]] + ' → ' + sexLabels[parts[1]],
                                fkeys);
                        }
                    });
                });
            }

            // Top representatives and principals as simple lists
            _renderTopList('explore-rep-top-reps', repData.top_representatives || []);
            _renderTopList('explore-rep-top-principals', repData.top_principals || []);
        }

        function _renderTopList(containerId, items) {
            let container = document.getElementById(containerId);
            if (!container) return;
            if (!items.length) { container.innerHTML = '<p class="explore-hint">Keine Daten.</p>'; return; }
            let html = '<ol class="stats-ranking">';
            let max = items[0].count;
            items.forEach(function(item) {
                let pct = max > 0 ? (item.count / max * 100) : 0;
                let sexCls = item.sex === 'f' ? 'stats-rank-bar-fill--f' : 'stats-rank-bar-fill--m';
                html += '<li>' +
                    '<div class="stats-rank-bar-track"><div class="stats-rank-bar-fill ' +
                    sexCls + '" data-rank-pct="' + pct.toFixed(1) + '"></div></div>' +
                    '<span class="stats-rank-name">' + esc(item.name) + '</span>' +
                    '<span class="stats-rank-count">' + item.count + '</span>' +
                    '</li>';
            });
            html += '</ol>';
            container.innerHTML = html;
            // Bar widths from data-rank-pct attribute (avoids inline style strings).
            container.querySelectorAll('.stats-rank-bar-fill').forEach(function(el) {
                el.style.setProperty('--rank-pct', el.getAttribute('data-rank-pct') + '%');
            });
        }

        // ── D3: Friendship Table ──

        function renderFriendshipTable() {
            let friendData = epicB && epicB.friendship;
            let friendPanels = document.getElementById('explore-friend-panels');
            if (!friendData || !friendPanels) return;

            let statsEl = document.getElementById('explore-friend-stats');
            if (statsEl) statsEl.textContent = friendData.total_edges + ' Beziehungen, ' + friendData.unique_persons + ' Personen';

            let container = document.getElementById('explore-friend-table');
            if (!container) return;

            let edges = friendData.edges || [];
            if (!edges.length) { container.innerHTML = '<p class="explore-hint">Keine Freundschaftsbeziehungen gefunden.</p>'; return; }

            let sexLabels = ChartHelpers.SEX_LABELS;
            let html = '<table class="explore-data-table"><thead><tr>' +
                '<th>Person A</th><th>Geschlecht</th><th>Person B</th><th>Geschlecht</th><th>Quelle</th>' +
                '</tr></thead><tbody>';
            edges.forEach(function(e) {
                html += '<tr>' +
                    '<td>' + esc(e.source_name) + '</td>' +
                    '<td>' + esc(sexLabels[e.source_sex] || e.source_sex) + '</td>' +
                    '<td>' + esc(e.target_name) + '</td>' +
                    '<td>' + esc(sexLabels[e.target_sex] || e.target_sex) + '</td>' +
                    '<td><a href="' + (window.ROOT_PATH || '.') + '/documents/' + esc(e.file_key).replace('f__', '').replace(/_/g, '/') + '.html">' + esc(e.file_key) + '</a></td>' +
                    '</tr>';
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        // ── Load data and initial render ──
        personSearchInput.classList.remove('hidden');

        // ── E6: Handle URL parameters for cross-epic navigation ──
        function handleUrlParams() {
            let personParam = EdCore.getParam('person');
            if (personParam && personSearchInput) {
                personSearchInput.value = personParam.replace(/^pe__/, '').replace(/_/g, ' ');
                personSearchInput.dispatchEvent(new Event('input'));
            }
        }

        ChartHelpers.loadJSON((window.ROOT_PATH || '.') + '/data/epic_b.json', 'explore-rel-chart', function(data) {
            epicB = data;
            renderAll();
            renderRepDirection();
            renderFriendshipTable();
            handleUrlParams();
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('exploration-page')) {
            initNetworkExplorer();
        }
    });

})();
