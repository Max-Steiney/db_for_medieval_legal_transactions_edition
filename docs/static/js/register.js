/* ==========================================================================
   Stadt und Gemeinschaft Wien — Datenbank
   Register page: search, filter, sort
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;

    function initRegister() {
        let table = document.getElementById('register-table');
        if (!table) return;
        let regType = table.dataset.type;
        let filterType = document.getElementById('filter-type');
        let filterDocs = document.getElementById('filter-docs');
        let filterQuality = document.getElementById('filter-quality');
        let resultCount = document.getElementById('result-count');
        let activeFiltersEl = document.getElementById('active-filters');

        let allEntries = [];
        let state = {
            query: '',
            letter: '',
            typeFilter: '',
            docsFilter: '',
            qualityFilter: '',
            sortKey: 'n',
            sortDir: 1
        };

        let filteredEntries = [];
        let colCount = regType === 'persons' ? 6 : 5;

        // --- Detail JSON cache ---
        let detailCache = null;  // lazy-loaded JSON { entityId: [{u,i,d,c,r},...] }
        let jsonFile = (window.ROOT_PATH || '.') + '/register/' + regType + '.json';

        function loadDetailJSON(cb) {
            if (detailCache) { cb(detailCache); return; }
            fetch(jsonFile)
                .then(function(r) { return r.json(); })
                .then(function(data) { detailCache = data; cb(detailCache); })
                .catch(function() { detailCache = {}; cb(detailCache); });
        }

        function renderDetailRow(entry, parentTr) {
            let existing = parentTr.nextElementSibling;
            if (existing && existing.classList.contains('detail-row')) {
                existing.remove();
                parentTr.classList.remove('expanded');
                return;
            }
            loadDetailJSON(function(cache) {
                let docs = cache[entry.id] || [];
                let detailTr = document.createElement('tr');
                detailTr.className = 'detail-row';
                let td = document.createElement('td');
                td.colSpan = colCount;
                if (docs.length === 0) {
                    td.innerHTML = '<div class="detail-content"><p class="no-docs-note">Keine Quellen verkn\u00fcpft.</p></div>';
                } else {
                    let html = '<div class="detail-content"><table class="detail-doc-table"><thead><tr>'
                        + '<th>Nr.</th><th>Datum</th><th>Quellenkorpus</th><th>Regest</th></tr></thead><tbody>';
                    for (let i = 0; i < docs.length; i++) {
                        let d = docs[i];
                        html += '<tr><td><a href="' + esc(d.u) + '">' + esc(d.i) + '</a></td>'
                            + '<td>' + esc(d.d) + '</td>'
                            + '<td>' + esc(d.c) + '</td>'
                            + '<td>' + esc(d.r) + '</td></tr>';
                    }
                    html += '</tbody></table></div>';
                    td.innerHTML = html;
                }
                detailTr.appendChild(td);
                parentTr.classList.add('expanded');
                parentTr.parentNode.insertBefore(detailTr, parentTr.nextSibling);
            });
        }

        // --- Table renderer ---
        let renderer = TableInfra.createTableRenderer({
            tbodyId: 'register-tbody',
            noResultsId: 'no-results',
            colCount: colCount,
            renderRow: function(entry, i, tr) {
                tr.dataset.entityId = entry.id;
                let dcClass = entry.dc === 0 ? 'doc-count-badge doc-count-zero' : 'doc-count-badge';
                let nameBtn = entry.dc > 0
                    ? '<button class="register-name register-name-linked" data-idx="' + i + '">' + esc(entry.n) + '</button>'
                    : '<span class="register-name">' + esc(entry.n) + '</span>';
                let html = '<td class="col-name">' + nameBtn + '</td>';

                if (regType === 'persons') {
                    let sexLabel = entry.sex === 'm' ? 'm' : entry.sex === 'f' ? 'w' : '\u2013';
                    html += '<td class="col-sex">' + sexLabel + '</td>';
                    html += '<td class="col-death">' + esc(entry.d) + '</td>';
                } else {
                    html += '<td class="col-type">' + esc(entry.tp) + '</td>';
                }

                if (entry.dc > 0) {
                    html += '<td class="col-docs"><button class="doc-count-link"><span class="' + dcClass + '">' + entry.dc + '</span></button></td>';
                } else {
                    html += '<td class="col-docs"><span class="' + dcClass + '">' + entry.dc + '</span></td>';
                }

                // Quality indicator (worst score across linked documents)
                let qLabel = entry.qw === 2 ? '\u26a0' : entry.qw === 1 ? '\u2139' : entry.qw === 0 ? '\u2713' : '\u2013';
                let qClass = 'quality-dot quality-' + (entry.qw === 2 ? 'warning' : entry.qw === 1 ? 'notice' : entry.qw === 0 ? 'ok' : 'na');
                html += '<td class="col-quality"><span class="' + qClass + '" title="' + (entry.qw === 2 ? 'Warnungen' : entry.qw === 1 ? 'Hinweise' : entry.qw === 0 ? 'Fehlerfrei' : 'Keine Quellen') + '">' + qLabel + '</span></td>';

                html += '<td class="col-id"><span class="cell-id">' + esc(entry.id) + '</span></td>';

                tr.innerHTML = html;
            }
        });

        // --- Click handler for inline detail expansion ---
        let tbody = document.getElementById('register-tbody');
        tbody.addEventListener('click', function(e) {
            // Clickable: name button OR doc-count badge (when dc > 0)
            let trigger = e.target.closest('.register-name-linked, .doc-count-link');
            if (!trigger) return;
            let tr = trigger.closest('tr');
            let entityId = tr.dataset.entityId;
            let entry = null;
            for (let i = 0; i < allEntries.length; i++) {
                if (allEntries[i].id === entityId) { entry = allEntries[i]; break; }
            }
            if (entry && entry.dc > 0) renderDetailRow(entry, tr);
        });

        // --- Shared infrastructure ---
        TableInfra.setupSearch(state, applyFilters);
        TableInfra.setupSortHeaders('register-table', state, applyFilters);

        // --- Alphabet bar ---
        let alphaBtns = document.querySelectorAll('.alpha-btn');
        alphaBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                let letter = btn.dataset.letter;
                if (state.letter === letter) {
                    state.letter = '';
                } else {
                    state.letter = letter;
                }
                alphaBtns.forEach(function(b) { b.classList.remove('active'); });
                if (state.letter) {
                    btn.classList.add('active');
                } else {
                    document.querySelector('.alpha-btn-all').classList.add('active');
                }
                applyFilters();
            });
        });

        // --- Type filter ---
        if (filterType) {
            filterType.addEventListener('change', function() {
                state.typeFilter = filterType.value;
                applyFilters();
            });
        }

        // --- Docs filter ---
        if (filterDocs) {
            filterDocs.addEventListener('change', function() {
                state.docsFilter = filterDocs.value;
                applyFilters();
            });
        }

        // --- Quality filter ---
        if (filterQuality) {
            filterQuality.addEventListener('change', function() {
                state.qualityFilter = filterQuality.value;
                applyFilters();
            });
        }

        // --- Core filter ---
        function applyFilters() {
            filteredEntries = allEntries.filter(function(entry) {
                if (state.letter && entry._fl !== state.letter) return false;

                if (state.typeFilter) {
                    let field = regType === 'persons' ? entry.sex : entry.tp;
                    if (field !== state.typeFilter) return false;
                }

                if (state.docsFilter === '1' && entry.dc === 0) return false;
                if (state.docsFilter === '0' && entry.dc > 0) return false;

                if (state.qualityFilter !== '') {
                    let qVal = parseInt(state.qualityFilter);
                    if (entry.qw !== qVal) return false;
                }

                if (state.query) {
                    let words = state.query.split(/\s+/);
                    for (let i = 0; i < words.length; i++) {
                        if (entry._s.indexOf(words[i]) === -1) return false;
                    }
                }

                return true;
            });

            // Sort
            filteredEntries.sort(function(a, b) {
                let va, vb;
                if (state.sortKey === 'dc' || state.sortKey === 'qw') {
                    va = a[state.sortKey]; vb = b[state.sortKey];
                } else {
                    va = (a[state.sortKey] || '').toLowerCase();
                    vb = (b[state.sortKey] || '').toLowerCase();
                }
                if (va < vb) return -state.sortDir;
                if (va > vb) return state.sortDir;
                return 0;
            });

            renderer.render(filteredEntries);
            if (resultCount) resultCount.textContent = filteredEntries.length + ' Eintr\u00e4ge';
            updateActiveFilters();
        }

        function updateActiveFilters() {
            if (!activeFiltersEl) return;
            activeFiltersEl.innerHTML = '';

            if (state.letter) {
                TableInfra.addFilterChip(activeFiltersEl, 'Buchstabe: ' + state.letter, function() {
                    state.letter = '';
                    alphaBtns.forEach(function(b) { b.classList.remove('active'); });
                    document.querySelector('.alpha-btn-all').classList.add('active');
                    applyFilters();
                });
            }
            if (state.typeFilter) {
                TableInfra.addFilterChip(activeFiltersEl, (regType === 'persons' ? 'Geschlecht' : 'Typ') + ': ' + state.typeFilter, function() {
                    state.typeFilter = '';
                    if (filterType) filterType.value = '';
                    applyFilters();
                });
            }
            if (state.docsFilter) {
                TableInfra.addFilterChip(activeFiltersEl, state.docsFilter === '1' ? 'Mit Quellen' : 'Ohne Quellen', function() {
                    state.docsFilter = '';
                    if (filterDocs) filterDocs.value = '';
                    applyFilters();
                });
            }
        }

        // Deep-link: auto-expand entity from URL hash (e.g. register/persons.html#pe__123)
        function openFromHash() {
            let hash = window.location.hash;
            if (!hash || hash.length < 2) return;
            let targetId = decodeURIComponent(hash.substring(1));
            let entry = null;
            for (let i = 0; i < allEntries.length; i++) {
                if (allEntries[i].id === targetId) { entry = allEntries[i]; break; }
            }
            if (!entry) return;
            // Filter via Suche auf die Ziel-ID, damit das Target im tbody
            // landet (_s enthält die ID). Sonst blockiert die Paginierung.
            // state.query muss mit der gleichen Normalisierung (V3) erfolgen,
            // mit der auch _s vorberechnet wurde.
            state.query = EdCore.normForSearch(targetId);
            state.letter = '';
            state.typeFilter = '';
            state.docsFilter = '';
            state.qualityFilter = '';
            let si = document.getElementById('search-input');
            if (si) si.value = targetId;
            if (filterType) filterType.value = '';
            if (filterDocs) filterDocs.value = '';
            if (filterQuality) filterQuality.value = '';
            applyFilters();
            let row = tbody.querySelector('tr[data-entity-id="' + CSS.escape(targetId) + '"]');
            if (!row) return;
            row.scrollIntoView({ block: 'center' });
            renderDetailRow(entry, row);
        }

        // --- Load data from external JSON file ---
        let loadingTbody = document.getElementById('register-tbody');
        loadingTbody.innerHTML = '<tr><td colspan="' + colCount + '" class="cell-placeholder">Daten werden geladen\u2026</td></tr>';

        fetch((window.ROOT_PATH || '.') + '/data/' + regType + '_search.json')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                allEntries = data;
                // Pre-compute search strings (V3: Umlaut-tolerant via EdCore.normForSearch)
                let norm = EdCore.normForSearch;
                allEntries.forEach(function(entry) {
                    entry._s = norm(entry.n + ' ' + entry.id + ' ' + (entry.tp || '') + ' ' + (entry.fn || '') + ' ' + (entry.sn || ''));
                    entry._fl = entry.n.charAt(0).toUpperCase();
                });
                filteredEntries = allEntries.slice();
                applyFilters();
                openFromHash();
                window.addEventListener('hashchange', openFromHash);
            })
            .catch(function(err) {
                console.warn('Register-Daten konnten nicht geladen werden:', err);
                loadingTbody.innerHTML = '<tr><td colspan="' + colCount + '" class="cell-placeholder">Daten konnten nicht geladen werden.</td></tr>';
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('register-table')) {
            initRegister();
        }
    });

})();
