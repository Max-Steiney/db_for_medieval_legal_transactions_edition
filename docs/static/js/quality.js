/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Quality Dashboard (M2): category chart, collection table, CSV export
   ========================================================================== */

(function() {
    'use strict';

    function initQuality() {
        var dataEl = document.getElementById('quality-data');
        if (!dataEl) return;
        var data;
        try { data = JSON.parse(dataEl.textContent); } catch(e) { return; }

        renderCategoryChart(data);
        renderCollectionTable(data);
        bindExport(data);
    }


    /* ---- Category Bar Chart ---- */

    function renderCategoryChart(data) {
        var container = document.getElementById('quality-category-chart');
        if (!container || !data.byCategory) return;

        var items = data.byCategory.map(function(c) {
            return {
                label: c.category.replace(/_/g, ' '),
                segments: [{ key: c.category, value: c.count, color: categoryColor(c.category) }],
                total: c.count
            };
        });

        ChartHelpers.renderHorizontalBars(container, {
            items: items,
            labelWidth: 140,
            barHeight: 22,
            barGap: 4,
            groupGap: 2,
            ariaLabel: 'Findings nach Kategorie'
        });
    }

    function categoryColor(cat) {
        if (cat.indexOf('ref_null') >= 0) return ChartHelpers.getToken('--color-quality-warning') || '#c45a5a';
        if (cat.indexOf('warning') >= 0) return ChartHelpers.getToken('--color-quality-warning') || '#c45a5a';
        return ChartHelpers.getToken('--color-quality-notice') || '#b08020';
    }


    /* ---- Collection Table ---- */

    function renderCollectionTable(data) {
        var container = document.getElementById('quality-collection-table');
        if (!container || !data.byCollection) return;

        var html = '<table class="explore-data-table"><thead><tr>' +
            '<th>Quellenkorpus</th><th class="num">Quellen</th>' +
            '<th class="num">Fehlerfrei</th><th class="num">Hinweise</th>' +
            '<th class="num">Warnungen</th><th class="num">Fehlerquote</th>' +
            '</tr></thead><tbody>';

        data.byCollection.forEach(function(c) {
            var errRate = c.total > 0 ? Math.round((c.warning / c.total) * 100) : 0;
            html += '<tr>' +
                '<td>' + EdCore.esc(c.label) + '</td>' +
                '<td class="num">' + c.total + '</td>' +
                '<td class="num">' + c.ok + '</td>' +
                '<td class="num">' + c.notice + '</td>' +
                '<td class="num">' + c.warning + '</td>' +
                '<td class="num">' + errRate + ' %</td>' +
                '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    }


    /* ---- CSV Export ---- */

    function bindExport(data) {
        var btn = document.getElementById('quality-export');
        if (!btn || !data.files) return;

        btn.addEventListener('click', function() {
            var lines = ['Datei;Idno;Sammlung;Score;Findings;Kategorien'];
            data.files.forEach(function(f) {
                lines.push([
                    f.file, f.idno, f.collection,
                    f.score, f.count,
                    (f.categories || '').replace(/;/g, ',')
                ].join(';'));
            });
            var blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' });
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'quality_export.csv';
            a.click();
            URL.revokeObjectURL(url);
        });
    }


    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('quality-page')) {
            initQuality();
        }
    });

})();
