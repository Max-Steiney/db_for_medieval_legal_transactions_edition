// Register page: sidebar filters, sort, sub-label disambiguation, faceted
// counts. Mirrors the sources page (index.js): same TableInfra components and
// tooltip/popover family.

(function() {
    'use strict';

    let esc = EdCore.esc;

    // Role pills mirror the form pills on the sources page: a uniform pill
    // in --anno-person blue, differentiated purely by SVG icon. currentColor
    // lets the icons inherit the pill colour.
    let ROLE_ICONS = {
        // issuer: box with arrow pointing out to the right ("issued")
        issuer:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<rect x="2" y="3.5" width="6" height="9" rx="0.5" ' +
            'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
            '<path d="M9 8h5m0 0l-2.3-2.3M14 8l-2.3 2.3" ' +
            'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
            '</svg>',
        // recipient: arrow from the left into a box (mirrored issuer)
        recipient:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<rect x="8" y="3.5" width="6" height="9" rx="0.5" ' +
            'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
            '<path d="M2 8h5m0 0L4.7 5.7M7 8L4.7 10.3" ' +
            'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
            '</svg>',
        // witness / sealer: signet — identical to the seal icon on the
        // sources page (FORM_ICONS.s). Consistent visual language: where a
        // seal hangs, there is also a sealer.
        witness:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.4" fill="none"/>' +
            '<circle cx="8" cy="8" r="2.2" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
            '<circle cx="8" cy="8" r="0.6" fill="currentColor"/>' +
            '</svg>',
        // other: three horizontal dots (neutral, not alarming)
        other:
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<circle cx="4" cy="8" r="1.2" fill="currentColor"/>' +
            '<circle cx="8" cy="8" r="1.2" fill="currentColor"/>' +
            '<circle cx="12" cy="8" r="1.2" fill="currentColor"/>' +
            '</svg>'
    };
    let ROLE_LABELS = {
        issuer:    'Aussteller*in',
        recipient: 'Empfänger*in',
        witness:   'Zeug*in / Siegler*in',
        other:     'Sonstige'
    };
    let ROLE_LABELS_PLURAL = {
        issuer:    'Aussteller*innen',
        recipient: 'Empfänger*innen',
        witness:   'Zeug*innen / Siegler*innen',
        other:     'Sonstige'
    };
    let ROLE_DESCRIPTIONS = {
        issuer:    'Person stellt mindestens eine Quelle aus.',
        recipient: 'Person ist Empfängerin oder Empfänger in mindestens einer Quelle.',
        witness:   'Person tritt als Zeuge oder Siegler in mindestens einer Quelle auf.',
        other:     'Person nimmt eine sonstige, nicht weiter klassifizierte Rolle ein.'
    };
    // Info "i" as an affordance on sidebar chips — visual cue that a
    // definition exists. Hovering the chip shows the edition tooltip with
    // ROLE_DESCRIPTIONS.
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
        let isPersons = regType === 'persons';
        let isOrgs = regType === 'orgs';
        // Basket actions only for persons and orgs. Places stay without the
        // "+" column because their detail pages are not part of the release.
        let basketCol = (isPersons || isOrgs) ? 1 : 0;
        let colCount = (isPersons ? 4 : 3) + basketCol;
        let entityLabel = (isPersons ? 'Personen'
                           : (regType === 'orgs' ? 'Organisationen' : 'Orte'));
        let entitySingular = (isPersons ? 'Person'
                           : (regType === 'orgs' ? 'Organisation' : 'Ort'));
        let filterSexEl = document.getElementById('filter-sex');
        let filterRolesEl = document.getElementById('filter-roles');
        let filterTypesEl = document.getElementById('filter-types');
        let filterCorporaEl = document.getElementById('filter-corpora');
        let resultCount = document.getElementById('result-count');
        let activeFiltersEl = document.getElementById('active-filters');

        // Forward declarations due to init order (initRangeSlider calls
        // applyFilters synchronously before we return here).
        let rangeSlider;
        let urlSyncEnabled = false;

        let allEntries = [];
        // Raw org-type code -> German label, filled from search data (e.tpl);
        // mirrored so table, basket and active-filter strip share the chip label.
        let typeLabels = {};
        let state = {
            query: '',
            letter: '',
            sex: [],          // m/f/u — empty = all (persons only)
            roles: [],        // issuer/recipient/witness/other — OR logic (persons only)
            types: [],        // orgs/places type facet — OR logic
            corpora: [],      // collection_path — OR logic
            yearMin: 0,
            yearMax: 9999,
            sortKey: 'n',
            sortDir: 1
        };

        let filteredEntries = [];

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
                td.colSpan = colCount;
                let head = '<div class="detail-content">'
                    + '<p class="detail-id-line">'
                    + '<span class="detail-id-label">ID</span> '
                    + '<code class="detail-id">' + esc(entry.id) + '</code></p>';
                if (docs.length === 0) {
                    td.innerHTML = head + '<p class="no-docs-note">Keine Quellen verknüpft.</p></div>';
                } else {
                    let html = head
                        + '<table class="detail-doc-table"><thead><tr>'
                        + '<th scope="col">Nr.</th><th scope="col">Datum</th><th scope="col">Quellenkorpus</th><th scope="col">Regest</th>'
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

        function renderActivity(entry) {
            // Sub-label beneath the name, e.g. 'belegt 1340 · QGW II/1 · Nr. 66'
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
                       ' data-hint="' + esc(body || label) + '"' +
                       (body ? ' data-hint-type="' + esc(label) + '"' : '') +
                       ' aria-label="' + esc(label) + '">' +
                       icon + '</span>';
            }).join('');
            return '<span class="form-pills">' + html + '</span>';
        }

        function renderDocsBadge(entry) {
            // The column header "Quellen" already gives the context — the
            // cell shows only the count with a dotted underline as tooltip
            // affordance. Hover reveals "X Quelle/n" plus per-corpus breakdown.
            let body = '';
            if (entry._coCount && entry._coCount.length) {
                body = entry._coCount.map(function(c) {
                    return c.label + ': ' + c.n;
                }).join(' | ');
            }
            let label = entry.dc === 1 ? '1 Quelle' : entry.dc + ' Quellen';
            return '<button class="badge badge-docs doc-count-link"' +
                   ' data-hint="' + esc(body || label) + '"' +
                   (body ? ' data-hint-type="' + esc(label) + '"' : '') +
                   '>' +
                       '<span class="badge-text">' + entry.dc + '</span>' +
                   '</button>';
        }

        let renderer = TableInfra.createTableRenderer({
            tbodyId: 'register-tbody',
            noResultsId: 'no-results',
            colCount: colCount,
            renderRow: function(entry, i, tr) {
                tr.dataset.entityId = entry.id;
                let sub = renderActivity(entry);
                // Every register row links its name to the profile page.
                // The linked-sources badge in the same row stays as the
                // inline-detail trigger so sources can be inspected without
                // leaving the list.
                let profileHref = (window.ROOT_PATH || '.') + '/register/'
                    + regType + '/' + encodeURIComponent(entry.id) + '.html';
                let profileUrl = 'register/' + regType + '/' + encodeURIComponent(entry.id) + '.html';
                let nameHtml =
                    '<a class="register-name register-name-linked" href="' + esc(profileHref) + '">' + esc(entry.n) + '</a>'
                    + (sub ? '<span class="register-name-sub">' + sub + '</span>' : '');
                let basketCell = '';
                if (isPersons && typeof DataBasket !== 'undefined') {
                    basketCell = '<td class="col-actions">' + DataBasket.buttonHTML({
                        type: 'person',
                        id: entry.id,
                        label: entry.n,
                        url: profileUrl,
                        sex: entry.sex || '',
                        active_min: entry.am || '',
                        active_max: entry.ax || ''
                    }) + '</td>';
                } else if (isOrgs && typeof DataBasket !== 'undefined') {
                    basketCell = '<td class="col-actions">' + DataBasket.buttonHTML({
                        type: 'org',
                        id: entry.id,
                        label: entry.n,
                        url: profileUrl,
                        type_label: entry.tpl || entry.tp || ''
                    }) + '</td>';
                }
                if (isPersons) {
                    let sexLabel = entry.sex === 'm' ? 'm' : entry.sex === 'f' ? 'w' : '–';
                    tr.innerHTML =
                        '<td class="col-name">' + nameHtml + '</td>' +
                        '<td class="col-sex">' + sexLabel + '</td>' +
                        '<td class="col-roles">' + renderRolePills(entry.rl) + '</td>' +
                        '<td class="col-docs">' + renderDocsBadge(entry) + '</td>' +
                        basketCell;
                } else {
                    let typeLabel = entry.tp ? esc(entry.tpl || entry.tp) : '<span class="cell-empty">&ndash;</span>';
                    tr.innerHTML =
                        '<td class="col-name">' + nameHtml + '</td>' +
                        '<td class="col-type">' + typeLabel + '</td>' +
                        '<td class="col-docs">' + renderDocsBadge(entry) + '</td>' +
                        basketCell;
                }
            }
        });

        // Name link navigates to the profile; the linked-sources badge stays
        // the inline-detail trigger.
        let tbody = document.getElementById('register-tbody');
        tbody.addEventListener('click', function(e) {
            // Never intercept anchor tags (<a href>) — browser navigation.
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

        let searchControl = TableInfra.setupSearch(state, applyFilters);
        TableInfra.setupSortHeaders('register-table', state, applyFilters);
        _applyInitialBarHeights();
        rangeSlider = TableInfra.initRangeSlider(state, applyFilters);

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

        // Inject role icons into the sidebar chips (single source of truth:
        // ROLE_ICONS from the JS, no duplicate in the template). Plus
        // data-tip-* for the edition tooltip with the definition and an "i"
        // affordance. Users immediately see which table icon belongs to
        // which role AND what the role means.
        if (filterRolesEl) {
            filterRolesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                let k = c.getAttribute('data-role');
                if (ROLE_ICONS[k]) {
                    let pill = document.createElement('span');
                    pill.className = 'form-filter-chip-pill';
                    pill.innerHTML = ROLE_ICONS[k];
                    c.insertBefore(pill, c.firstChild);
                }
                let label = ROLE_LABELS_PLURAL[k] || '';
                let desc = ROLE_DESCRIPTIONS[k] || '';
                if (desc) c.setAttribute('data-hint', desc);
                if (label) c.setAttribute('data-hint-type', label);
                // Drop the native title — data-hint takes over.
                c.removeAttribute('title');
                if (desc) {
                    let info = document.createElement('span');
                    info.className = 'form-filter-chip-info';
                    info.innerHTML = INFO_ICON;
                    c.appendChild(info);
                }
            });
        }

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
        bindMultiChips(filterTypesEl,   'types',   'data-type');
        bindMultiChips(filterCorporaEl, 'corpora', 'data-corpus');

        // URL parameter restore, before the first applyFilters.
        let urlParams = new URLSearchParams(window.location.search);
        let urlQuery = urlParams.get('q');
        if (urlQuery && searchControl) {
            searchControl.set(urlQuery);
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
        _restoreMulti('types',   'types',   filterTypesEl,   'data-type',   'is-active');
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
            if (skip !== 'types' && state.types.length) {
                // Empty type bucketed as "" — entries without a type land
                // there. Active selection of "" matches those rows.
                let tp = entry.tp || '';
                if (state.types.indexOf(tp) === -1) return false;
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
                // Match if the person's activity interval overlaps the slider
                // range — analogous to the sources histogram (decade overlap).
                if (ymax < state.yearMin || ymin > state.yearMax) return false;
            }
            if (skip !== 'query' && !EdCore.matchesQuery(entry._s, state.query)) return false;
            return true;
        }

        function updateChipCounts() {
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
            if (filterTypesEl) {
                let counts = {};
                allEntries.forEach(function(e) {
                    if (!matchesAllExcept(e, 'types')) return;
                    let tp = e.tp || '';
                    counts[tp] = (counts[tp] || 0) + 1;
                });
                let typeChips = Array.from(
                    filterTypesEl.querySelectorAll('.form-filter-chip'));
                typeChips.forEach(function(c) {
                    let v = c.getAttribute('data-type');
                    let n = counts[v] || 0;
                    let ce = c.querySelector('.form-filter-chip-count');
                    if (ce) ce.textContent = n;
                    let isActive = c.classList.contains('is-active');
                    c.hidden = (n === 0 && !isActive);
                });
                // Reorder by currently visible counts; catch-all buckets
                // (OTHER, empty) stay pinned to the end.
                typeChips.sort(function(a, b) {
                    let va = a.getAttribute('data-type');
                    let vb = b.getAttribute('data-type');
                    let ta = (va === 'OTHER' || va === '') ? 1 : 0;
                    let tb = (vb === 'OTHER' || vb === '') ? 1 : 0;
                    if (ta !== tb) return ta - tb;
                    return (counts[vb] || 0) - (counts[va] || 0);
                });
                typeChips.forEach(function(c) { filterTypesEl.appendChild(c); });
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
                // Update only data-hint, not native title: a title would show
                // a second tooltip with the stale build-time count.
                bar.setAttribute('data-hint',
                    dec + 'er: ' + c + ' ' + (c === 1 ? entitySingular : entityLabel));
            });
        }

        function _applyInitialBarHeights() {
            document.querySelectorAll('.range-bar').forEach(function(bar) {
                let h = parseInt(bar.getAttribute('data-height')) || 0;
                bar.style.setProperty('--bar-height', h + '%');
            });
        }

        function _compareEntries(a, b, key, dir) {
            return EdCore.compareValues(a[key], b[key], dir);
        }

        function syncUrlFromState() {
            if (!urlSyncEnabled) return;
            let p = new URLSearchParams();
            if (state.query)   p.set('q', state.query);
            if (state.letter)  p.set('letter', state.letter);
            if (state.sex.length)     p.set('sex', state.sex.join(','));
            if (state.roles.length)   p.set('roles', state.roles.join(','));
            if (state.types.length)   p.set('types', state.types.join(','));
            if (state.corpora.length) p.set('corpora', state.corpora.join(','));
            if (rangeSlider && rangeSlider.isFiltered && rangeSlider.isFiltered()) {
                p.set('yearMin', state.yearMin);
                p.set('yearMax', state.yearMax);
            }
            let qs = p.toString();
            let url = location.pathname + (qs ? '?' + qs : '') + location.hash;
            history.replaceState(null, '', url);
        }

        function updateActiveFilters() {
            if (!activeFiltersEl) return;
            activeFiltersEl.innerHTML = '';
            if (state.query) {
                TableInfra.addFilterChip(activeFiltersEl, 'Suche: ' + state.query, function() {
                    if (searchControl) searchControl.reset();
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
                    return ROLE_LABELS_PLURAL[r] || r;
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
            if (state.types.length) {
                let label = 'Typ: ' + state.types.map(function(t) { return typeLabels[t] || t || 'ohne Angabe'; }).join(', ');
                TableInfra.addFilterChip(activeFiltersEl, label, function() {
                    state.types = [];
                    if (filterTypesEl) filterTypesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                        c.classList.remove('is-active');
                        c.setAttribute('aria-pressed', 'false');
                    });
                    applyFilters();
                });
            }
            if (rangeSlider && rangeSlider.isFiltered()) {
                TableInfra.addFilterChip(activeFiltersEl, 'Zeitraum: ' + state.yearMin + '–' + state.yearMax,
                    function() { rangeSlider.reset(); });
            }
        }

        let resetBtn = document.getElementById('filter-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                state.letter = '';
                state.sex = [];
                state.roles = [];
                state.types = [];
                state.corpora = [];
                if (searchControl) searchControl.reset();
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
                if (filterTypesEl) filterTypesEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
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

        function applyFilters() {
            filteredEntries = allEntries.filter(function(e) {
                return matchesAllExcept(e, null);
            });
            filteredEntries.sort(function(a, b) {
                return _compareEntries(a, b, state.sortKey, state.sortDir);
            });
            renderer.render(filteredEntries);
            if (resultCount) resultCount.textContent = filteredEntries.length + ' ' + entityLabel;
            updateActiveFilters();
            updateChipCounts();
            updateHistogram();
            syncUrlFromState();
        }

        // Deep link via hash (#pe__id).
        function openFromHash() {
            let hash = window.location.hash;
            if (!hash || hash.length < 2) return;
            let targetId = decodeURIComponent(hash.substring(1));
            let entry = null;
            for (let i = 0; i < allEntries.length; i++) {
                if (allEntries[i].id === targetId) { entry = allEntries[i]; break; }
            }
            if (!entry) return;
            // Constrain via the search to the target id so the row is
            // guaranteed to land in the virtualised tbody.
            if (searchControl) searchControl.set(targetId);
            state.letter = '';
            state.sex = [];
            state.roles = [];
            state.types = [];
            state.corpora = [];
            applyFilters();
            let row = tbody.querySelector('tr[data-entity-id="' + CSS.escape(targetId) + '"]');
            if (!row) return;
            row.scrollIntoView({block: 'center'});
            renderDetailRow(entry, row);
        }

        let loadingTbody = document.getElementById('register-tbody');
        loadingTbody.innerHTML = '<tr><td colspan="' + colCount + '" class="cell-placeholder">Daten werden geladen…</td></tr>';

        fetch((window.ROOT_PATH || '.') + '/data/' + regType + '_search.json')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                allEntries = data;
                let norm = EdCore.normForSearch;
                // Per-corpus counts per person for the linked-sources cell tooltip.
                let corpusLabels = {};
                if (filterCorporaEl) {
                    filterCorporaEl.querySelectorAll('.chip').forEach(function(c) {
                        let key = c.getAttribute('data-corpus');
                        let lab = c.querySelector('.chip-label');
                        if (key && lab) corpusLabels[key] = lab.textContent;
                    });
                }
                allEntries.forEach(function(e) {
                    // Search index covers name/ID/first name/surname plus
                    // activity years and the sub-label (corpus + Nr.) — so
                    // '1340 Katharina' and 'Nr. 66' work as search terms.
                    // Add 'Nr. <i0>' explicitly so users can search the
                    // sub-label spelling directly.
                    let parts = [
                        e.n || '', e.id || '',
                        e.fn || '', e.sn || '',
                        e.am || '', e.ax || '',
                        e.cl0 || '', e.i0 || '',
                        e.i0 ? ('Nr. ' + e.i0) : ''
                    ];
                    e._s = norm(parts.join(' '));
                    e._fl = e.n.charAt(0).toUpperCase();
                    // Per-corpus breakdown per person for the linked-sources cell tooltip.
                    e._coCount = (e.co || []).map(function(k) {
                        return {label: corpusLabels[k] || k, n: 1};
                    });
                    if (e.tp) typeLabels[e.tp] = e.tpl || e.tp;
                });
                filteredEntries = allEntries.slice();
                urlSyncEnabled = true;
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
