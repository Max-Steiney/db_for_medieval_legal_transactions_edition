// Data basket page: renders three sections (sources, persons, orgs).
// Each section has its own export and clear actions. Derived rows are
// dimmed italic and carry a "aus Quelle" column linking back to the
// source idnos they were attached to.
(function () {
    'use strict';

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // Lazy lookup: source idno -> source basket item (for the "aus Quelle"
    // link). Adds a data-hint tooltip with the source date and a regest
    // preview so the link reveals what it points to without a click.
    function sourceLink(srcId, items, root) {
        const src = items.find(x => x.type === 'source' && x.id === srcId);
        if (src && src.url) {
            const bits = [];
            if (src.date) bits.push(src.date);
            if (src.coll) bits.push(src.coll);
            if (src.regest) bits.push(String(src.regest).slice(0, 120));
            const hint = bits.length
                ? ' data-hint="' + esc(bits.join(' · ')) + '"'
                : '';
            return '<a href="' + esc(root + '/' + src.url) + '"' + hint + '>Nr. ' + esc(srcId) + '</a>';
        }
        return 'Nr. ' + esc(srcId);
    }
    function sourcesCell(it, items, root) {
        if (!it.src || !it.src.length) return '';
        return it.src.map(s => sourceLink(s, items, root)).join(', ');
    }

    function buildSourceRow(it, root) {
        const url = it.url ? esc(root + '/' + it.url) : '#';
        const rowCls = it.gathered ? '' : ' basket-row-derived';
        return `<tr class="basket-row${rowCls}" data-id="${esc(it.id)}" data-type="source">
            <td><a href="${url}">${esc(it.id)}</a></td>
            <td>${esc(it.date || '')}</td>
            <td>${esc(it.coll || '')}</td>
            <td class="cell-regest">${esc(it.regest || '')}</td>
            <td class="col-actions">
                <button type="button" class="basket-row-remove" aria-label="Aus Datenkorb entfernen">x</button>
            </td>
        </tr>`;
    }
    function buildPersonRow(it, items, root) {
        const url = it.url ? esc(root + '/' + it.url) : '#';
        const rowCls = it.gathered ? '' : ' basket-row-derived';
        const sexLabel = it.sex === 'm' ? 'm' : it.sex === 'f' ? 'w' : '–';
        const active = (it.active_min || '') +
            (it.active_max && it.active_max !== it.active_min
                ? ' bis ' + it.active_max : '');
        return `<tr class="basket-row${rowCls}" data-id="${esc(it.id)}" data-type="person">
            <td><a href="${url}">${esc(it.label || it.id)}</a></td>
            <td>${esc(sexLabel)}</td>
            <td>${esc(active)}</td>
            <td class="col-source">${sourcesCell(it, items, root)}</td>
            <td class="col-actions">
                <button type="button" class="basket-row-remove" aria-label="Aus Datenkorb entfernen">x</button>
            </td>
        </tr>`;
    }
    function buildOrgRow(it, items, root) {
        const url = it.url ? esc(root + '/' + it.url) : '#';
        const rowCls = it.gathered ? '' : ' basket-row-derived';
        return `<tr class="basket-row${rowCls}" data-id="${esc(it.id)}" data-type="org">
            <td><a href="${url}">${esc(it.label || it.id)}</a></td>
            <td>${esc(it.type_label || '')}</td>
            <td class="col-source">${sourcesCell(it, items, root)}</td>
            <td class="col-actions">
                <button type="button" class="basket-row-remove" aria-label="Aus Datenkorb entfernen">x</button>
            </td>
        </tr>`;
    }

    // Per-section column sort, driven by clicks on the th[data-sort] headers.
    // key null = default order (gathered first, then date/label).
    const sortState = {
        source: { key: null, dir: 1 },
        person: { key: null, dir: 1 },
        org:    { key: null, dir: 1 },
    };

    function sortGetter(type, key) {
        if (type === 'source') {
            if (key === 'idno') return it => it.id || '';
            if (key === 'date') return it => it.date || '';
            if (key === 'coll') return it => it.coll || '';
        } else if (type === 'person') {
            if (key === 'name')   return it => it.label || it.id || '';
            if (key === 'sex')    return it => it.sex || '';
            if (key === 'active') return it => it.active_min || '';
        } else if (type === 'org') {
            if (key === 'name') return it => it.label || it.id || '';
            if (key === 'type') return it => it.type_label || '';
        }
        return () => '';
    }

    // Sort: with an active column, sort purely by it (like the registers).
    // Otherwise gathered first, then primary key (date for sources, label
    // otherwise) so each section has a stable, scannable order.
    function sortItems(items, type) {
        const st = sortState[type];
        if (st && st.key) {
            const get = sortGetter(type, st.key);
            return items.slice().sort((a, b) =>
                EdCore.compareValues(get(a), get(b), st.dir));
        }
        const dateKey = type === 'source';
        return items.slice().sort((a, b) => {
            if (a.gathered !== b.gathered) return a.gathered ? -1 : 1;
            const sa = dateKey ? (a.date || '') : (a.label || a.id);
            const sb = dateKey ? (b.date || '') : (b.label || b.id);
            return String(sa).localeCompare(String(sb), 'de');
        });
    }

    function renderSection(type) {
        const section = document.querySelector('[data-section="' + type + '"]');
        if (!section) return;
        const all = DataBasket.list();
        const items = all.filter(x => (x.type || 'source') === type);
        const tbody = section.querySelector('tbody');
        const empty = section.querySelector('.basket-section-empty');
        const table = section.querySelector('table');
        const gNum = section.querySelector('[data-stat="gathered"]');
        const dNum = section.querySelector('[data-stat="derived"]');
        const gC = items.filter(x => x.gathered).length;
        const dC = items.length - gC;
        if (gNum) gNum.textContent = String(gC);
        if (dNum) dNum.textContent = String(dC);

        if (!items.length) {
            if (table) table.hidden = true;
            if (empty) empty.hidden = false;
            return;
        }
        if (table) table.hidden = false;
        if (empty) empty.hidden = true;

        const root = (window.ROOT_PATH || '.');
        const sorted = sortItems(items, type);
        let html = '';
        if (type === 'source') {
            html = sorted.map(it => buildSourceRow(it, root)).join('');
        } else if (type === 'person') {
            html = sorted.map(it => buildPersonRow(it, all, root)).join('');
        } else if (type === 'org') {
            html = sorted.map(it => buildOrgRow(it, all, root)).join('');
        }
        tbody.innerHTML = html;
    }

    function renderAll() {
        renderSection('source');
        renderSection('person');
        renderSection('org');
        const empty = document.getElementById('basket-empty-all');
        if (empty) empty.hidden = (DataBasket.count() > 0);
        const clearAll = document.getElementById('basket-clear-all');
        if (clearAll) clearAll.hidden = (DataBasket.count() === 0);
    }

    function csvDownload(filename, header, rows) {
        const csvRow = (vals) => vals.map(v => {
            const s = String(v == null ? '' : v);
            return /[",;\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
        }).join(';');
        const lines = [csvRow(header), ...rows.map(csvRow)];
        const blob = new Blob(['﻿' + lines.join('\r\n')],
            { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function exportType(type, mode) {
        const all = DataBasket.list(type);
        const items = mode === 'gathered' ? all.filter(x => x.gathered) : all;
        if (!items.length) return;
        const suffix = mode === 'gathered' ? 'gesammelt' : 'alles';
        if (type === 'source') {
            csvDownload('datenkorb-quellen-' + suffix + '.csv',
                ['id', 'date', 'collection', 'regest', 'url'],
                items.map(it => [it.id, it.date || '', it.coll || '',
                                 it.regest || '', it.url || '']));
        } else if (type === 'person') {
            const header = ['id', 'label', 'sex', 'active_min', 'active_max', 'url'];
            if (mode === 'all') header.push('aus_quelle');
            csvDownload('datenkorb-personen-' + suffix + '.csv',
                header,
                items.map(it => {
                    const row = [it.id, it.label || '', it.sex || '',
                                 it.active_min || '', it.active_max || '',
                                 it.url || ''];
                    if (mode === 'all') row.push((it.src || []).join(','));
                    return row;
                }));
        } else if (type === 'org') {
            const header = ['id', 'label', 'type', 'url'];
            if (mode === 'all') header.push('aus_quelle');
            csvDownload('datenkorb-organisationen-' + suffix + '.csv',
                header,
                items.map(it => {
                    const row = [it.id, it.label || '',
                                 it.type_label || '', it.url || ''];
                    if (mode === 'all') row.push((it.src || []).join(','));
                    return row;
                }));
        }
    }

    function bind() {
        // Section action buttons via delegation.
        document.querySelectorAll('.basket-section').forEach(sec => {
            sec.addEventListener('click', (e) => {
                const btn = e.target.closest('button[data-action]');
                if (!btn) return;
                const type = btn.dataset.type;
                const act = btn.dataset.action;
                if (act === 'export-gathered') exportType(type, 'gathered');
                else if (act === 'export-all')  exportType(type, 'all');
                else if (act === 'clear') {
                    if (DataBasket.count(type) === 0) return;
                    const label = type === 'source' ? 'Quellen'
                                : type === 'person' ? 'Personen'
                                : 'Organisationen';
                    if (!confirm(label + ' aus dem Datenkorb leeren?')) return;
                    DataBasket.clear(type);
                    renderAll();
                }
            });
            // Row remove.
            sec.addEventListener('click', (e) => {
                const btn = e.target.closest('.basket-row-remove');
                if (!btn) return;
                const tr = btn.closest('tr[data-id]');
                if (!tr) return;
                DataBasket.remove(tr.dataset.type, tr.dataset.id);
                renderAll();
            });
            // Column sort: click cycles asc -> desc -> default.
            const type = sec.getAttribute('data-section');
            const heads = sec.querySelectorAll('thead th[data-sort]');
            heads.forEach(th => {
                th.addEventListener('click', () => {
                    const st = sortState[type];
                    const key = th.getAttribute('data-sort');
                    if (st.key === key) {
                        if (st.dir === 1) st.dir = -1;
                        else { st.key = null; st.dir = 1; }
                    } else { st.key = key; st.dir = 1; }
                    heads.forEach(h => {
                        h.classList.remove('sorted-asc', 'sorted-desc');
                        h.setAttribute('aria-sort', 'none');
                    });
                    if (st.key !== null) {
                        th.classList.add(st.dir === 1 ? 'sorted-asc' : 'sorted-desc');
                        th.setAttribute('aria-sort',
                            st.dir === 1 ? 'ascending' : 'descending');
                    }
                    renderSection(type);
                });
            });
        });
        // Global "clear everything" button lives in the header, outside the
        // section delegation above.
        const clearAll = document.getElementById('basket-clear-all');
        if (clearAll) {
            clearAll.addEventListener('click', () => {
                if (DataBasket.count() === 0) return;
                if (!confirm('Den gesamten Datenkorb leeren? Alle Quellen, ' +
                    'Personen und Organisationen werden entfernt.')) return;
                DataBasket.clear();
                renderAll();
            });
        }
        // Reactive updates.
        window.addEventListener('basket-change', renderAll);
        window.addEventListener('storage', (e) => {
            if (e.key === 'sugw-basket-v1') renderAll();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        bind();
        renderAll();
    });
})();
