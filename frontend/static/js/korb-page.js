// Wissenskorb-Seite: rendert die gesammelte Quellen-Liste; Remove-/Clear-/
// CSV-Export-Aktionen. Daten kommen aus dem Wissenskorb-Modul.
(function () {
    'use strict';

    function fmt(n) {
        return (n || 0).toLocaleString('de-AT').replace(/,/g, '.');
    }
    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function render() {
        const items = Wissenskorb.list();
        const tbody = document.getElementById('korb-tbody');
        const wrap = document.getElementById('korb-list-wrap');
        const empty = document.getElementById('korb-empty');
        const count = document.getElementById('korb-count');
        const table = document.getElementById('korb-table');
        if (count) count.textContent = `${fmt(items.length)} Eintr${items.length === 1 ? 'ag' : 'äge'}`;
        if (!items.length) {
            if (table) table.hidden = true;
            if (empty) empty.hidden = false;
            return;
        }
        if (table) table.hidden = false;
        if (empty) empty.hidden = true;

        const ROOT = (window.ROOT_PATH || '.');
        // Sortiert nach Datum (aufsteigend)
        const sorted = items.slice().sort((a, b) =>
            (a.date || '').localeCompare(b.date || ''));
        tbody.innerHTML = sorted.map(it => {
            const url = it.url ? `${ROOT}/${esc(it.url)}` : '#';
            return `<tr data-id="${esc(it.id)}" data-type="${esc(it.type || 'source')}">
                <td><a href="${url}">${esc(it.id)}</a></td>
                <td>${esc(it.date || '')}</td>
                <td>${esc(it.coll || '')}</td>
                <td class="cell-regest">${esc(it.regest || '')}</td>
                <td class="col-actions">
                    <button type="button" class="korb-row-remove" aria-label="Aus Wissenskorb entfernen">×</button>
                </td>
            </tr>`;
        }).join('');
    }

    function bind() {
        const tbody = document.getElementById('korb-tbody');
        if (tbody) {
            tbody.addEventListener('click', (e) => {
                const btn = e.target.closest('.korb-row-remove');
                if (!btn) return;
                const tr = btn.closest('tr[data-id]');
                if (!tr) return;
                Wissenskorb.remove(tr.dataset.type, tr.dataset.id);
                render();
            });
        }
        const clearBtn = document.getElementById('korb-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (Wissenskorb.count() === 0) return;
                if (!confirm('Den gesamten Wissenskorb leeren?')) return;
                Wissenskorb.clear();
                render();
            });
        }
        const exportBtn = document.getElementById('korb-export');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                const items = Wissenskorb.list();
                if (!items.length) return;
                const header = ['type', 'id', 'date', 'collection', 'regest', 'url', 'addedAt'];
                const csvRow = (vals) => vals.map(v => {
                    const s = String(v == null ? '' : v);
                    return /[",;\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
                }).join(';');
                const lines = [csvRow(header)];
                for (const it of items) {
                    lines.push(csvRow([
                        it.type || 'source', it.id,
                        it.date || '', it.coll || '',
                        it.regest || '', it.url || '',
                        it.addedAt || '',
                    ]));
                }
                const blob = new Blob(['﻿' + lines.join('\r\n')],
                    { type: 'text/csv;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'wissenskorb.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            });
        }
        // Cross-Tab + same-tab Updates
        window.addEventListener('wissenskorb-change', render);
        window.addEventListener('storage', (e) => {
            if (e.key === 'sugw-wissenskorb-v1') render();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        bind();
        render();
    });
})();
