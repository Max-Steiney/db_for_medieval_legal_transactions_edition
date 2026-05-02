/* ==========================================================================
   Stadt und Gemeinschaft Wien — Datenbank
   Personenregister: Sidebar-Filter, Sort, Sub-Label-Disambiguierung,
   Faceted-Search-Counts. Architektur parallel zur Quellenseite (index.js):
   gleiche Komponenten aus TableInfra (Range-Slider, Search, Sort, Renderer),
   gleiche Tooltip-/Popover-Familie (data-tip-* + provenance.js).
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;

    // Rollen-Pillen analog zu den Erschliessungsform-Pillen der Quellenseite:
    // einheitliche Form-Pille in --anno-person-Blau, Differenzierung rein
    // ueber das SVG-Icon. currentColor laesst die Icons die Pillen-Farbe erben.
    let ROLE_ICONS = {
        // Aussteller: Box mit Pfeil nach rechts heraus ("ausgegeben")
        issuer:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<rect x="2" y="3.5" width="6" height="9" rx="0.5" ' +
            'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
            '<path d="M9 8h5m0 0l-2.3-2.3M14 8l-2.3 2.3" ' +
            'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
            '</svg>',
        // Empfaenger: Pfeil von links in eine Box (gespiegelter issuer)
        recipient:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<rect x="8" y="3.5" width="6" height="9" rx="0.5" ' +
            'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
            '<path d="M2 8h5m0 0L4.7 5.7M7 8L4.7 10.3" ' +
            'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
            '</svg>',
        // Zeuge / Siegler: Petschaft — identisch zum Siegel-Icon der
        // Quellenseite (FORM_ICONS.s). Konsistente visuelle Sprache: wo
        // ein Siegel klebt, ist auch ein Siegler.
        witness:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.4" fill="none"/>' +
            '<circle cx="8" cy="8" r="2.2" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
            '<circle cx="8" cy="8" r="0.6" fill="currentColor"/>' +
            '</svg>',
        // Sonstige: drei horizontale Punkte (neutral, nicht alarmierend)
        other:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<circle cx="4" cy="8" r="1.2" fill="currentColor"/>' +
            '<circle cx="8" cy="8" r="1.2" fill="currentColor"/>' +
            '<circle cx="12" cy="8" r="1.2" fill="currentColor"/>' +
            '</svg>'
    };
    let ROLE_LABELS = {
        issuer:    'Aussteller',
        recipient: 'Empfänger',
        witness:   'Zeuge / Siegler',
        other:     'Sonstige'
    };
    let ROLE_DESCRIPTIONS = {
        issuer:    'Person stellt mindestens eine Quelle aus.',
        recipient: 'Person ist Empfängerin oder Empfänger in mindestens einer Quelle.',
        witness:   'Person tritt als Zeuge oder Siegler in mindestens einer Quelle auf.',
        other:     'Person nimmt eine sonstige, nicht weiter klassifizierte Rolle ein.'
    };
    // Info-"i" als Affordance an Sidebar-Chips — visuelles Signal, dass es
    // eine Definition gibt. Hover ueber den ganzen Chip zeigt den Edition-
    // Tooltip mit ROLE_DESCRIPTIONS.
    let INFO_ICON =
        '<svg viewBox="0 0 16 16" aria-hidden="true">' +
        '<circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3" fill="none"/>' +
        '<text x="8" y="11.5" text-anchor="middle" font-size="9" font-weight="700" ' +
        'fill="currentColor" font-family="Georgia, serif">i</text>' +
        '</svg>';

    let SEX_LABELS = {m: 'männlich', f: 'weiblich', u: 'ohne Angabe'};

    function initRegister() {
        let table = document.getElementById('register-table');
        if (!table) return;
        let regType = table.dataset.type;
        let filterSexEl = document.getElementById('filter-sex');
        let filterRolesEl = document.getElementById('filter-roles');
        let filterCorporaEl = document.getElementById('filter-corpora');
        let resultCount = document.getElementById('result-count');
        let activeFiltersEl = document.getElementById('active-filters');

        // Forward-Deklarationen wegen Init-Reihenfolge (initRangeSlider
        // ruft applyFilters synchron, bevor wir hier zurueckkommen).
        let rangeSlider;
        let urlSyncEnabled = false;

        let allEntries = [];
        let state = {
            query: '',
            letter: '',
            sex: [],          // Array m/f/u — leer = alle
            roles: [],        // Array issuer/recipient/witness/other — ODER-Logik
            corpora: [],      // Array collection_path — ODER-Logik
            yearMin: 0,
            yearMax: 9999,
            sortKey: 'n',
            sortDir: 1
        };

        let filteredEntries = [];

        // --- Detail JSON cache (Inline-Detailzeile pro Person) ---
        let detailCache = null;
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
                td.colSpan = 4;
                let head = '<div class="detail-content">'
                    + '<p class="detail-id-line">'
                    + '<span class="detail-id-label">ID</span> '
                    + '<code class="detail-id">' + esc(entry.id) + '</code></p>';
                if (docs.length === 0) {
                    td.innerHTML = head + '<p class="no-docs-note">Keine Quellen verknüpft.</p></div>';
                } else {
                    let html = head
                        + '<table class="detail-doc-table"><thead><tr>'
                        + '<th>Nr.</th><th>Datum</th><th>Quellenkorpus</th><th>Regest</th>'
                        + '</tr></thead><tbody>';
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

        // --- Renderer: Name-Cell mit Sub-Label, Geschl., Rollen-Pillen, Quellen ---
        function renderActivity(entry) {
            // Sub-Label unter dem Namen: 'belegt 1340 · QGW II/1 · Nr. 66'
            let bits = [];
            if (entry.am) {
                let span = (entry.ax && entry.ax !== entry.am)
                    ? entry.am + '–' + entry.ax
                    : entry.am;
                bits.push('belegt ' + span);
            }
            if (entry.cl0) bits.push(esc(entry.cl0));
            if (entry.i0)  bits.push('Nr. ' + esc(entry.i0));
            return bits.length ? bits.join(' · ') : '';
        }

        function renderRolePills(roles) {
            if (!roles || !roles.length) return '';
            let html = roles.map(function(r) {
                let label = ROLE_LABELS[r];
                let icon = ROLE_ICONS[r];
                let body = ROLE_DESCRIPTIONS[r] || '';
                if (!label || !icon) return '';
                return '<span class="form-pill role-pill-' + r + '"' +
                       ' data-tip-title="' + esc(label) + '"' +
                       (body ? ' data-tip-body="' + esc(body) + '"' : '') +
                       ' aria-label="' + esc(label) + '">' +
                       icon + '</span>';
            }).join('');
            return '<span class="form-pills">' + html + '</span>';
        }

        function renderDocsBadge(entry) {
            // Spalten-Header "Quellen" gibt schon den Kontext — die Zelle
            // zeigt nur die Anzahl mit dotted underline als Tooltip-
            // Affordance. Hover zeigt "X Quelle/n" + Korpus-Aufschluesselung.
            let body = '';
            if (entry._coCount && entry._coCount.length) {
                body = entry._coCount.map(function(c) {
                    return c.label + ': ' + c.n;
                }).join(' | ');
            }
            let label = entry.dc === 1 ? '1 Quelle' : entry.dc + ' Quellen';
            return '<button class="badge badge-docs doc-count-link"' +
                   ' data-tip-title="' + esc(label) + '"' +
                   (body ? ' data-tip-body="' + esc(body) + '"' : '') +
                   '>' +
                       '<span class="badge-text">' + entry.dc + '</span>' +
                   '</button>';
        }

        let renderer = TableInfra.createTableRenderer({
            tbodyId: 'register-tbody',
            noResultsId: 'no-results',
            colCount: 4,
            renderRow: function(entry, i, tr) {
                tr.dataset.entityId = entry.id;
                let sub = renderActivity(entry);
                // Personen-Namen: Link auf Profilseite. Klick auf den
                // Quellen-Badge in derselben Zeile bleibt der Inline-
                // Detail-Trigger, damit man Quellen einsehen kann ohne
                // die Seite zu verlassen.
                let profileHref = (window.ROOT_PATH || '.') + '/register/persons/'
                    + encodeURIComponent(entry.id) + '.html';
                let nameHtml = (regType === 'persons')
                    ? '<a class="register-name register-name-linked" href="' + esc(profileHref) + '">' + esc(entry.n) + '</a>'
                      + (sub ? '<span class="register-name-sub">' + sub + '</span>' : '')
                    : '<button class="register-name register-name-linked"'
                      + ' data-idx="' + i + '">' + esc(entry.n) + '</button>'
                      + (sub ? '<span class="register-name-sub">' + sub + '</span>' : '');
                let sexLabel = entry.sex === 'm' ? 'm' : entry.sex === 'f' ? 'w' : '–';
                tr.innerHTML =
                    '<td class="col-name">' + nameHtml + '</td>' +
                    '<td class="col-sex">' + sexLabel + '</td>' +
                    '<td class="col-roles">' + renderRolePills(entry.rl) + '</td>' +
                    '<td class="col-docs">' + renderDocsBadge(entry) + '</td>';
            }
        });

        // --- Click-Handler fuer Name + Quellen-Badge ---
        // Im Personenregister fuehrt der Name-Link direkt aufs Profil
        // (kein Inline-Detail). Der Quellen-Badge bleibt der
        // Inline-Trigger; Org/Ort behalten den Button-Toggle.
        let tbody = document.getElementById('register-tbody');
        tbody.addEventListener('click', function(e) {
            // Anker-Tags (<a href>) niemals abfangen — Browser-Navigation.
            if (e.target.closest('a')) return;
            let trigger = e.target.closest('.register-name-linked, .doc-count-link');
            if (!trigger) return;
            let tr = trigger.closest('tr');
            if (!tr) return;
            let entityId = tr.dataset.entityId;
            let entry = null;
            for (let i = 0; i < allEntries.length; i++) {
                if (allEntries[i].id === entityId) { entry = allEntries[i]; break; }
            }
            if (entry) renderDetailRow(entry, tr);
        });

        // --- Shared Infrastructure: Suche + Sort-Header + Range-Slider ---
        TableInfra.setupSearch(state, applyFilters);
        TableInfra.setupSortHeaders('register-table', state, applyFilters);
        _applyInitialBarHeights();
        rangeSlider = TableInfra.initRangeSlider(state, applyFilters);

        // --- Alphabet-Bar ---
        let alphaBtns = document.querySelectorAll('.alpha-btn');
        alphaBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                let letter = btn.dataset.letter;
                state.letter = (state.letter === letter) ? '' : letter;
                alphaBtns.forEach(function(b) { b.classList.remove('active'); });
                if (state.letter) {
                    btn.classList.add('active');
                } else {
                    document.querySelector('.alpha-btn-all').classList.add('active');
                }
                applyFilters();
            });
        });

        // --- Rollen-Icons in die Sidebar-Chips injizieren (Single-Source-
        // of-Truth: ROLE_ICONS aus dem JS, kein Duplikat im Template).
        // Plus: data-tip-* fuer Edition-Tooltip mit Definition + "i"-
        // Affordance. So sieht man im Filter sofort, welches Tabellen-Icon
        // zu welcher Rolle gehoert UND was die Rolle bedeutet.
        if (filterRolesEl) {
            filterRolesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                let k = c.getAttribute('data-role');
                if (ROLE_ICONS[k]) {
                    let pill = document.createElement('span');
                    pill.className = 'form-filter-chip-pill';
                    pill.innerHTML = ROLE_ICONS[k];
                    c.insertBefore(pill, c.firstChild);
                }
                let label = ROLE_LABELS[k] || '';
                let desc = ROLE_DESCRIPTIONS[k] || '';
                if (label) c.setAttribute('data-tip-title', label);
                if (desc)  c.setAttribute('data-tip-body', desc);
                // Native title entfernen — Edition-Tooltip uebernimmt
                c.removeAttribute('title');
                if (desc) {
                    let info = document.createElement('span');
                    info.className = 'form-filter-chip-info';
                    info.innerHTML = INFO_ICON;
                    c.appendChild(info);
                }
            });
        }

        // --- Multi-Select-Chip-Helper (Sex / Roles / Corpora) ---
        function bindMultiChips(container, key, attr) {
            if (!container) return;
            container.querySelectorAll('.form-filter-chip, .chip').forEach(function(chip) {
                chip.addEventListener('click', function() {
                    let v = chip.getAttribute(attr);
                    let arr = state[key];
                    let idx = arr.indexOf(v);
                    if (idx === -1) {
                        arr.push(v);
                        chip.classList.add('is-active');
                        chip.classList.add('active');
                        chip.setAttribute('aria-pressed', 'true');
                    } else {
                        arr.splice(idx, 1);
                        chip.classList.remove('is-active');
                        chip.classList.remove('active');
                        chip.setAttribute('aria-pressed', 'false');
                    }
                    applyFilters();
                });
            });
        }
        bindMultiChips(filterSexEl,     'sex',     'data-sex');
        bindMultiChips(filterRolesEl,   'roles',   'data-role');
        bindMultiChips(filterCorporaEl, 'corpora', 'data-corpus');

        // --- URL-Parameter-Restore (vor erstem applyFilters wirksam) ---
        let urlParams = new URLSearchParams(window.location.search);
        let urlQuery = urlParams.get('q');
        if (urlQuery) {
            state.query = EdCore.normForSearch(urlQuery);
            let si = document.getElementById('search-input');
            if (si) si.value = urlQuery;
        }
        let urlLetter = urlParams.get('letter');
        if (urlLetter) {
            state.letter = urlLetter;
            alphaBtns.forEach(function(b) { b.classList.remove('active'); });
            let target = document.querySelector('.alpha-btn[data-letter="' + urlLetter + '"]');
            if (target) target.classList.add('active');
        }
        function _restoreMulti(key, urlKey, container, attr, activeClass) {
            let raw = urlParams.get(urlKey);
            if (!raw || !container) return;
            state[key] = raw.split(',').filter(Boolean);
            state[key].forEach(function(v) {
                let chip = container.querySelector('[' + attr + '="' + v + '"]');
                if (chip) {
                    chip.classList.add(activeClass);
                    chip.setAttribute('aria-pressed', 'true');
                }
            });
        }
        _restoreMulti('sex',     'sex',     filterSexEl,     'data-sex',    'is-active');
        _restoreMulti('roles',   'roles',   filterRolesEl,   'data-role',   'is-active');
        _restoreMulti('corpora', 'corpora', filterCorporaEl, 'data-corpus', 'active');
        let urlYearMin = urlParams.get('yearMin');
        let urlYearMax = urlParams.get('yearMax');
        if (urlYearMin && urlYearMax) {
            let rmin = document.getElementById('range-min');
            let rmax = document.getElementById('range-max');
            if (rmin && rmax) {
                rmin.value = urlYearMin;
                rmax.value = urlYearMax;
                rmin.dispatchEvent(new Event('input'));
            }
        }

        // --- Faceted-Search: matchesAllExcept(entry, skip) ---
        function entryYears(entry) {
            let am = parseInt(entry.am);
            let ax = parseInt(entry.ax);
            return [isNaN(am) ? null : am, isNaN(ax) ? null : ax];
        }
        function matchesAllExcept(entry, skip) {
            if (skip !== 'letter' && state.letter) {
                if (entry._fl !== state.letter) return false;
            }
            if (skip !== 'sex' && state.sex.length) {
                let s = entry.sex || 'u';
                if (state.sex.indexOf(s) === -1) return false;
            }
            if (skip !== 'roles' && state.roles.length) {
                let any = false;
                for (let i = 0; i < state.roles.length; i++) {
                    if (entry.rl && entry.rl.indexOf(state.roles[i]) !== -1) {
                        any = true; break;
                    }
                }
                if (!any) return false;
            }
            if (skip !== 'corpora' && state.corpora.length) {
                let any = false;
                for (let i = 0; i < state.corpora.length; i++) {
                    if (entry.co && entry.co.indexOf(state.corpora[i]) !== -1) {
                        any = true; break;
                    }
                }
                if (!any) return false;
            }
            if (skip !== 'year' && rangeSlider && rangeSlider.isFiltered()) {
                let yrs = entryYears(entry);
                if (yrs[0] === null) return false;
                let ymin = yrs[0], ymax = yrs[1] !== null ? yrs[1] : yrs[0];
                // Person matcht, wenn ihr Aktivitaetsintervall den Slider-Bereich
                // ueberlappt — analog zum Quellen-Histogramm (decade-overlap).
                if (ymax < state.yearMin || ymin > state.yearMax) return false;
            }
            if (skip !== 'query' && state.query) {
                let words = state.query.split(/\s+/);
                for (let i = 0; i < words.length; i++) {
                    if (entry._s.indexOf(words[i]) === -1) return false;
                }
            }
            return true;
        }

        // --- Live-Counts an Sidebar-Chips ---
        function updateChipCounts() {
            // Geschlecht
            if (filterSexEl) {
                let counts = {};
                allEntries.forEach(function(e) {
                    if (!matchesAllExcept(e, 'sex')) return;
                    let s = e.sex || 'u';
                    counts[s] = (counts[s] || 0) + 1;
                });
                filterSexEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                    let v = c.getAttribute('data-sex');
                    let n = counts[v] || 0;
                    let ce = c.querySelector('.form-filter-chip-count');
                    if (ce) ce.textContent = n;
                    let isActive = c.classList.contains('is-active');
                    c.hidden = (n === 0 && !isActive);
                });
            }
            // Rollen
            if (filterRolesEl) {
                let counts = {};
                allEntries.forEach(function(e) {
                    if (!matchesAllExcept(e, 'roles')) return;
                    if (!e.rl) return;
                    e.rl.forEach(function(r) { counts[r] = (counts[r] || 0) + 1; });
                });
                filterRolesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                    let v = c.getAttribute('data-role');
                    let n = counts[v] || 0;
                    let ce = c.querySelector('.form-filter-chip-count');
                    if (ce) ce.textContent = n;
                    let isActive = c.classList.contains('is-active');
                    c.hidden = (n === 0 && !isActive);
                });
            }
            // Korpora
            if (filterCorporaEl) {
                let counts = {};
                allEntries.forEach(function(e) {
                    if (!matchesAllExcept(e, 'corpora')) return;
                    if (!e.co) return;
                    e.co.forEach(function(c) { counts[c] = (counts[c] || 0) + 1; });
                });
                filterCorporaEl.querySelectorAll('.chip').forEach(function(c) {
                    let v = c.getAttribute('data-corpus');
                    let n = counts[v] || 0;
                    let ce = c.querySelector('.chip-count');
                    if (ce) ce.textContent = n;
                    let isActive = c.classList.contains('active');
                    c.hidden = (n === 0 && !isActive);
                });
            }
        }

        function updateHistogram() {
            let bars = document.querySelectorAll('.range-bar');
            if (!bars.length) return;
            let counts = {};
            allEntries.forEach(function(e) {
                if (!matchesAllExcept(e, 'year')) return;
                let yrs = entryYears(e);
                if (yrs[0] === null) return;
                let ymin = yrs[0], ymax = yrs[1] !== null ? yrs[1] : yrs[0];
                let dmin = Math.floor(ymin / 10) * 10;
                let dmax = Math.floor(ymax / 10) * 10;
                for (let d = dmin; d <= dmax; d += 10) {
                    counts[d] = (counts[d] || 0) + 1;
                }
            });
            let maxCount = 0;
            for (let k in counts) if (counts[k] > maxCount) maxCount = counts[k];
            if (maxCount === 0) maxCount = 1;
            bars.forEach(function(bar) {
                let dec = parseInt(bar.getAttribute('data-decade'));
                let c = counts[dec] || 0;
                let pct = c > 0 ? Math.max(4, Math.round(c / maxCount * 100)) : 0;
                bar.style.setProperty('--bar-height', pct + '%');
                bar.setAttribute('data-count', c);
                bar.title = dec + 'er: ' + c + ' Personen';
            });
        }

        function _applyInitialBarHeights() {
            document.querySelectorAll('.range-bar').forEach(function(bar) {
                let h = parseInt(bar.getAttribute('data-height')) || 0;
                bar.style.setProperty('--bar-height', h + '%');
            });
        }

        // --- Sortier-Helfer (analog Quellenseite, Klammer-Strip + locale) ---
        function _sortKey(v) {
            return String(v)
                .replace(/[\[\]]/g, '')
                .replace(/^[\s,;:]+|[\s,;:]+$/g, '');
        }
        function _compareEntries(a, b, key, dir) {
            let va = a[key];
            let vb = b[key];
            let aEmpty = (va === '' || va === null || va === undefined);
            let bEmpty = (vb === '' || vb === null || vb === undefined);
            if (aEmpty && bEmpty) return 0;
            if (aEmpty) return 1;
            if (bEmpty) return -1;
            if (typeof va === 'number' && typeof vb === 'number') {
                return (va - vb) * dir;
            }
            return _sortKey(va).localeCompare(_sortKey(vb), 'de') * dir;
        }

        // --- URL aus State syncen ---
        function syncUrlFromState() {
            if (!urlSyncEnabled) return;
            let p = new URLSearchParams();
            if (state.query)   p.set('q', state.query);
            if (state.letter)  p.set('letter', state.letter);
            if (state.sex.length)     p.set('sex', state.sex.join(','));
            if (state.roles.length)   p.set('roles', state.roles.join(','));
            if (state.corpora.length) p.set('corpora', state.corpora.join(','));
            if (rangeSlider && rangeSlider.isFiltered && rangeSlider.isFiltered()) {
                p.set('yearMin', state.yearMin);
                p.set('yearMax', state.yearMax);
            }
            let qs = p.toString();
            let url = location.pathname + (qs ? '?' + qs : '') + location.hash;
            history.replaceState(null, '', url);
        }

        // --- Active-Filter-Pillen ---
        function updateActiveFilters() {
            if (!activeFiltersEl) return;
            activeFiltersEl.innerHTML = '';
            if (state.query) {
                TableInfra.addFilterChip(activeFiltersEl, 'Suche: ' + state.query, function() {
                    state.query = '';
                    let si = document.getElementById('search-input');
                    if (si) si.value = '';
                    let sc = document.getElementById('search-clear');
                    if (sc) sc.classList.add('hidden');
                    applyFilters();
                });
            }
            if (state.letter) {
                TableInfra.addFilterChip(activeFiltersEl, 'Buchstabe: ' + state.letter, function() {
                    state.letter = '';
                    alphaBtns.forEach(function(b) { b.classList.remove('active'); });
                    document.querySelector('.alpha-btn-all').classList.add('active');
                    applyFilters();
                });
            }
            if (state.sex.length) {
                let label = 'Geschlecht: ' + state.sex.map(function(s) {
                    return SEX_LABELS[s] || s;
                }).join(', ');
                TableInfra.addFilterChip(activeFiltersEl, label, function() {
                    state.sex = [];
                    if (filterSexEl) filterSexEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                        c.classList.remove('is-active');
                        c.setAttribute('aria-pressed', 'false');
                    });
                    applyFilters();
                });
            }
            if (state.roles.length) {
                let label = 'Rolle: ' + state.roles.map(function(r) {
                    return (ROLE_LABELS[r] && ROLE_LABELS[r].long) || r;
                }).join(', ');
                TableInfra.addFilterChip(activeFiltersEl, label, function() {
                    state.roles = [];
                    if (filterRolesEl) filterRolesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                        c.classList.remove('is-active');
                        c.setAttribute('aria-pressed', 'false');
                    });
                    applyFilters();
                });
            }
            if (state.corpora.length) {
                let names = state.corpora.map(function(c) {
                    let chip = filterCorporaEl
                        && filterCorporaEl.querySelector('[data-corpus="' + c + '"] .chip-label');
                    return chip ? chip.textContent : c;
                });
                let label = state.corpora.length === 1
                    ? 'Quellenkorpus: ' + names[0]
                    : 'Quellenkorpus: ' + state.corpora.length + ' ausgewählt';
                TableInfra.addFilterChip(activeFiltersEl, label, function() {
                    state.corpora = [];
                    if (filterCorporaEl) filterCorporaEl.querySelectorAll('.chip').forEach(function(c) {
                        c.classList.remove('active');
                    });
                    applyFilters();
                });
            }
            if (rangeSlider && rangeSlider.isFiltered()) {
                TableInfra.addFilterChip(activeFiltersEl, 'Zeitraum: ' + state.yearMin + '–' + state.yearMax,
                    function() { rangeSlider.reset(); });
            }
        }

        // --- Reset ---
        let resetBtn = document.getElementById('filter-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                state.query = '';
                state.letter = '';
                state.sex = [];
                state.roles = [];
                state.corpora = [];
                let si = document.getElementById('search-input');
                if (si) si.value = '';
                let sc = document.getElementById('search-clear');
                if (sc) sc.classList.add('hidden');
                alphaBtns.forEach(function(b) { b.classList.remove('active'); });
                document.querySelector('.alpha-btn-all').classList.add('active');
                if (filterSexEl) filterSexEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                    c.classList.remove('is-active');
                    c.setAttribute('aria-pressed', 'false');
                });
                if (filterRolesEl) filterRolesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                    c.classList.remove('is-active');
                    c.setAttribute('aria-pressed', 'false');
                });
                if (filterCorporaEl) filterCorporaEl.querySelectorAll('.chip').forEach(function(c) {
                    c.classList.remove('active');
                });
                if (rangeSlider && rangeSlider.reset) rangeSlider.reset();
                applyFilters();
            });
        }

        // --- Core: applyFilters ---
        function applyFilters() {
            filteredEntries = allEntries.filter(function(e) {
                return matchesAllExcept(e, null);
            });
            filteredEntries.sort(function(a, b) {
                return _compareEntries(a, b, state.sortKey, state.sortDir);
            });
            renderer.render(filteredEntries);
            if (resultCount) resultCount.textContent = filteredEntries.length + ' Personen';
            updateActiveFilters();
            updateChipCounts();
            updateHistogram();
            syncUrlFromState();
        }

        // --- Deep-Link via Hash (#pe__id) ---
        function openFromHash() {
            let hash = window.location.hash;
            if (!hash || hash.length < 2) return;
            let targetId = decodeURIComponent(hash.substring(1));
            let entry = null;
            for (let i = 0; i < allEntries.length; i++) {
                if (allEntries[i].id === targetId) { entry = allEntries[i]; break; }
            }
            if (!entry) return;
            // Per Suche auf die Ziel-ID einschraenken, damit die Zeile sicher
            // im virtualisierten tbody landet.
            state.query = EdCore.normForSearch(targetId);
            state.letter = '';
            state.sex = [];
            state.roles = [];
            state.corpora = [];
            let si = document.getElementById('search-input');
            if (si) si.value = targetId;
            applyFilters();
            let row = tbody.querySelector('tr[data-entity-id="' + CSS.escape(targetId) + '"]');
            if (!row) return;
            row.scrollIntoView({block: 'center'});
            renderDetailRow(entry, row);
        }

        // --- Daten laden ---
        let loadingTbody = document.getElementById('register-tbody');
        loadingTbody.innerHTML = '<tr><td colspan="4" class="cell-placeholder">Daten werden geladen…</td></tr>';

        fetch((window.ROOT_PATH || '.') + '/data/' + regType + '_search.json')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                allEntries = data;
                let norm = EdCore.normForSearch;
                // Korpus-Counts pro Person fuer den Quellen-Cell-Tooltip
                let corpusLabels = {};
                if (filterCorporaEl) {
                    filterCorporaEl.querySelectorAll('.chip').forEach(function(c) {
                        let key = c.getAttribute('data-corpus');
                        let lab = c.querySelector('.chip-label');
                        if (key && lab) corpusLabels[key] = lab.textContent;
                    });
                }
                allEntries.forEach(function(e) {
                    // Suchindex umfasst Name/ID/Vorname/Nachname plus Aktivitaets-
                    // Jahre und das Sub-Label (Korpus + Nr.) — damit funktioniert
                    // '1340 Katharina' und 'Nr. 66' als Suchterms.
                    // 'Nr. <i0>' explizit aufnehmen, damit User die Sub-Label-
                    // Schreibweise direkt suchen koennen.
                    let parts = [
                        e.n || '', e.id || '',
                        e.fn || '', e.sn || '',
                        e.am || '', e.ax || '',
                        e.cl0 || '', e.i0 || '',
                        e.i0 ? ('Nr. ' + e.i0) : ''
                    ];
                    e._s = norm(parts.join(' '));
                    e._fl = e.n.charAt(0).toUpperCase();
                    // Korpus-Aufschluesselung pro Person fuer Quellen-Cell-Tooltip
                    e._coCount = (e.co || []).map(function(k) {
                        return {label: corpusLabels[k] || k, n: 1};
                    });
                });
                filteredEntries = allEntries.slice();
                urlSyncEnabled = true;
                applyFilters();
                openFromHash();
                window.addEventListener('hashchange', openFromHash);
            })
            .catch(function(err) {
                console.warn('Register-Daten konnten nicht geladen werden:', err);
                loadingTbody.innerHTML = '<tr><td colspan="4" class="cell-placeholder">Daten konnten nicht geladen werden.</td></tr>';
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('register-table')) {
            initRegister();
        }
    });

})();
