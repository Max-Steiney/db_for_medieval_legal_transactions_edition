/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Index page: search, filter, sort, preview
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;

    // Maps validation category codes from pipeline/validation_report.json to
    // user-facing German labels. Unknown codes fall back to the raw code.
    let QUALITY_CATEGORY_LABELS = {
        'instant_attribute':    'Datierungs-Attribut',
        'ref_null':             'leere Referenz',
        'uri_with_whitespace':  'URI mit Whitespace',
        'uri_invalid_netloc':   'URI ungueltig',
        'rs_no_type':           'rs ohne @type',
        'rs_type_noncanonical': 'rs @type unkanonisch',
        'rs_type_empty':        'rs @type leer',
        'triggerstring_no_n':   'triggerstring ohne @n'
    };

    function initIndex() {
        let filterPlace = document.getElementById('filter-place');
        let filterFacs = document.getElementById('filter-facs');
        let filterSex = document.getElementById('filter-sex');
        let filterFormsEl = document.getElementById('filter-forms');
        let resultCount = document.getElementById('result-count');
        let activeFiltersEl = document.getElementById('active-filters');
        // Forward declarations: rangeSlider, chips and urlSyncEnabled are
        // referenced from updateActiveFilters / updateCorpusCounts /
        // syncUrlFromState BEFORE initRangeSlider returns (its init callback
        // calls applyFilters synchronously). With `let` they would be in TDZ.
        let rangeSlider;
        let chips;
        let urlSyncEnabled = false;

        let allDocs = [];
        let state = {
            query: '',
            collection: '',
            place: '',         // sentinel '__none__' = "without place"
            facs: '',
            sex: '',           // '' | 'with-f' | 'only-f' | 'only-m' | 'none'
            forms: [],         // subset of 'R','S','E','N','none' — empty = all
            yearMin: 0,
            yearMax: 9999,
            sortKey: 'di',
            sortDir: 1,
            previewIdx: -1
        };

        // Form filter: OR within the selected forms, AND against the other
        // filters. Empty selection = all sources pass.
        function docMatchesForms(doc, forms) {
            if (!forms || forms.length === 0) return true;
            for (let i = 0; i < forms.length; i++) {
                let f = forms[i];
                if (f === 'R' && doc.ecR > 0) return true;
                if (f === 'S' && doc.ecS > 0) return true;
                if (f === 'E' && doc.ecE > 0) return true;
                if (f === 'N' && doc.ecN > 0) return true;
                if (f === 'none' && !doc.ecR && !doc.ecS && !doc.ecE && !doc.ecN) return true;
            }
            return false;
        }

        function docMatchesSex(doc, sex) {
            if (!sex) return true;
            if (sex === 'with-f') return doc.pcdf > 0;
            if (sex === 'only-f') return doc.pcdf > 0 && doc.pcdm === 0;
            if (sex === 'only-m') return doc.pcdm > 0 && doc.pcdf === 0;
            if (sex === 'none') return doc.pcd === 0;
            return true;
        }

        function docMatchesPlace(doc, place) {
            if (!place) return true;
            if (place === '__none__') return !doc.p;
            return doc.p === place;
        }

        let collectionLabels = {};
        let filteredDocs = [];

        // --- Content cell renderer ---
        // Persons badge with sex breakdown in title; then form pills R/S/E/N
        // (TEI annotation depth) plus facsimile pill F as small stroke icons;
        // multi-event indicator when the source documents several legal
        // transactions.
        //
        // Icons are currentColor stroke SVGs so they inherit the pill color
        // (--anno-person) and pick up hover states without special handling.
        let FORM_ICONS = {
            // Regest: three summary lines (standard "summary" glyph)
            r: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M3.5 5h9M3.5 8h9M3.5 11h6" ' +
               'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" fill="none"/>' +
               '</svg>',
            // Siegel: signet impression — outer seal ring with inner circle
            // and small centerpoint. No star/wheel.
            s: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.4" fill="none"/>' +
               '<circle cx="8" cy="8" r="2.2" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
               '<circle cx="8" cy="8" r="0.6" fill="currentColor"/>' +
               '</svg>',
            // Eintrag: open book / two pages
            e: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M8 4.5v8M3 4.5c1.5 0 3.4.4 5 1.2c1.6-.8 3.5-1.2 5-1.2v7c-1.5 0-3.4.4-5 1.2c-1.6-.8-3.5-1.2-5-1.2v-7z" ' +
               'stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Nota: bookmark / small note marker
            n: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M5 3h6v10l-3-2.2L5 13z" ' +
               'stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Faksimile: picture frame with hint of sun and mountain
            f: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<rect x="2.4" y="3.4" width="11.2" height="9.2" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
               '<circle cx="6" cy="7" r="1.1" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
               '<path d="M2.6 11.6l3-2.6l2.4 2l3-2.6l2.4 2.2" ' +
               'stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Multiple legal transactions: two slightly offset rectangles,
            // read as 'more than one transaction in one source'.
            m: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<rect x="2.6" y="4.6" width="7.6" height="7.6" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
               '<rect x="5.8" y="2.6" width="7.6" height="7.6" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="var(--color-bg-card)"/>' +
               '</svg>'
        };

        function renderContent(doc) {
            let parts = [];

            // Hover-hints use the project-wide [data-hint] convention,
            // rendered by hint.js. data-hint-type sets the small caps
            // label, data-hint the body text. No native title attributes.
            if (doc.pcd > 0) {
                let label = doc.pcd === 1 ? '1 Person' : doc.pcd + ' Personen';
                let breakdown = [];
                if (doc.pcdf) breakdown.push(doc.pcdf + ' weiblich');
                if (doc.pcdm) breakdown.push(doc.pcdm + ' m\u00e4nnlich');
                if (doc.pcdu) breakdown.push(doc.pcdu + ' ohne Geschlechtsangabe');
                let body = breakdown.length ? breakdown.join(', ') : label;
                let typeLabel = breakdown.length ? label : '';
                parts.push(
                    '<span class="badge badge-persons"' +
                    ' data-hint="' + esc(body) + '"' +
                    (typeLabel ? ' data-hint-type="' + esc(typeLabel) + '"' : '') +
                    '>' +
                        '<span class="badge-text">' + doc.pcd + '</span>' +
                    '</span>'
                );
            }

            let pills = [];
            if (doc.ecR > 0) pills.push(['r', 'Regest', 'Regest-Annotation in der TEI-Quelle']);
            if (doc.ecS > 0) pills.push(['s', 'Siegel', 'Siegelbeschreibung in der TEI-Quelle']);
            if (doc.ecE > 0) pills.push(['e', 'Eintrag', 'Stadtbuch-Eintrag in der TEI-Quelle']);
            if (doc.ecN > 0) pills.push(['n', 'Nota', 'Nachsatz/Notiz in der TEI-Quelle']);
            if (doc.f) pills.push(['f', 'Faksimile', 'Digitalisat des Originals verlinkt']);
            // Multi-transaction marker as a regular pill \u2014 stacked rectangles;
            // the actual count lives in the tooltip body.
            if (doc.ec > 1) {
                pills.push(['m', 'Mehrere Rechtsgesch\u00e4fte',
                            doc.ec + ' Rechtsgesch\u00e4fte in einer Quelle']);
            }
            if (pills.length) {
                let html = pills.map(function(p) {
                    return '<span class="form-pill form-pill-' + p[0] + '"' +
                           ' data-hint="' + esc(p[2]) + '"' +
                           ' data-hint-type="' + esc(p[1]) + '"' +
                           ' aria-label="' + esc(p[1]) + '">' +
                           FORM_ICONS[p[0]] + '</span>';
                }).join('');
                parts.push('<span class="form-pills">' + html + '</span>');
            }

            return parts.join(' ');
        }

        // Date cell with range hint: for multi-year ranges (e.g. "1198–1230")
        // a tooltip explains the convention "date imprecise, secured
        // timespan...". For clean single dates no tooltip is rendered.
        function renderDateCell(doc) {
            let dateText = doc.dn || doc.d;
            let attr = '';
            if (dateText && dateText.indexOf('–') !== -1) {
                let body = 'Gesicherter Zeitraum laut TEI: ' +
                           dateText.replace('–', ' bis ');
                attr = ' data-hint="' + esc(body) + '"' +
                       ' data-hint-type="Datum unscharf"';
            }
            return '<td class="col-date"' + attr + '>' + esc(dateText) + '</td>';
        }

        // SVG chevron as expand affordance. Rotated via CSS once the row is
        // expanded (.doc-row.is-open).
        let CHEVRON_SVG =
            '<svg class="row-chevron" viewBox="0 0 16 16" aria-hidden="true">' +
            '<path d="M6 4l4 4l-4 4" stroke="currentColor" stroke-width="1.6" ' +
            'stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
            '</svg>';

        // --- Table renderer ---
        let renderer = TableInfra.createTableRenderer({
            tbodyId: 'doc-tbody',
            noResultsId: 'no-results',
            colCount: 5,
            renderRow: function(doc, i, tr) {
                tr.classList.add('doc-row');
                tr.setAttribute('data-idx', i);
                let korbBtn = '';
                if (typeof DataBasket !== 'undefined') {
                    korbBtn = DataBasket.buttonHTML({
                        id: doc.id, label: doc.id,
                        url: doc.u, date: doc.dn || doc.d || '',
                        coll: doc.cl || doc.c || '', regest: doc.t || '',
                    });
                }
                tr.innerHTML =
                    '<td class="col-idno"><a href="' + esc(doc.u) + '" class="doc-link">' + esc(doc.id) + '</a>' + korbBtn + '</td>' +
                    renderDateCell(doc) +
                    '<td class="col-place">' + esc(doc.p) + '</td>' +
                    '<td class="col-title"><a href="' + esc(doc.u) + '" class="doc-link doc-link--title cell-title">' + esc(doc.t) + '</a></td>' +
                    '<td class="col-content"><div class="col-content-inner">' +
                        '<div class="col-content-pills">' + renderContent(doc) + '</div>' +
                        CHEVRON_SVG +
                    '</div></td>';
                tr.tabIndex = 0;
                tr.setAttribute('role', 'button');
                tr.setAttribute('aria-expanded', 'false');
                tr.setAttribute('aria-label', 'Vorschau f\u00fcr Nr. ' + doc.id);
                (function(idx) {
                    tr.addEventListener('click', function(e) {
                        if (e.target.closest('a')) return;
                        if (e.target.closest('.korb-btn')) return;
                        togglePreview(idx);
                    });
                    tr.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); togglePreview(idx); }
                    });
                })(i);
            }
        });

        // --- Shared infrastructure ---
        TableInfra.setupSearch(state, applyFilters);
        TableInfra.setupSortHeaders('doc-table', state, applyFilters);

        // --- Inject form-of-treatment icons + definition tooltips into the
        // sidebar chips. Same SVGs as the table pills (FORM_ICONS), plus
        // data-tip-* and "i" affordance for the definition. The 'none' chip
        // ('ohne') has no table counterpart — icon omitted, definition stays.
        let FORM_LABELS = {R: 'Regest', S: 'Siegel', E: 'Eintrag', N: 'Nota', none: 'Ohne Erschließungsform'};
        let FORM_DESCRIPTIONS = {
            R: 'Inhaltszusammenfassung der Quelle, vom Editor verfasst (TEI-Element <abstract>).',
            S: 'Beschreibung des oder der Siegel an der Urkunde (TEI-Element <seal>).',
            E: 'Eintrag in einem Verwaltungsbuch (Stadtbuch, Grundbuch). TEI-Element <entry>.',
            N: 'Nachsatz oder Marginalie zur Hauptquelle (TEI-Element <nota>).',
            none: 'Quelle ohne erkannte Erschließungsform — keines der TEI-Elemente abstract/seal/entry/nota vorhanden.'
        };
        let INFO_ICON =
            '<svg viewBox="0 0 16 16" aria-hidden="true">' +
            '<circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3" fill="none"/>' +
            '<text x="8" y="11.5" text-anchor="middle" font-size="9" font-weight="700" ' +
            'fill="currentColor" font-family="Georgia, serif">i</text>' +
            '</svg>';
        if (filterFormsEl) {
            let iconKeyMap = {R: 'r', S: 's', E: 'e', N: 'n'};
            filterFormsEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                let key = c.getAttribute('data-form');
                let iconKey = iconKeyMap[key];
                if (iconKey && FORM_ICONS[iconKey]) {
                    let pill = document.createElement('span');
                    pill.className = 'form-filter-chip-pill';
                    pill.innerHTML = FORM_ICONS[iconKey];
                    c.insertBefore(pill, c.firstChild);
                }
                let label = FORM_LABELS[key] || '';
                let desc = FORM_DESCRIPTIONS[key] || '';
                if (desc) c.setAttribute('data-hint', desc);
                if (label) c.setAttribute('data-hint-type', label);
                c.removeAttribute('title');
                if (desc) {
                    let info = document.createElement('span');
                    info.className = 'form-filter-chip-info';
                    info.innerHTML = INFO_ICON;
                    c.appendChild(info);
                }
            });
        }

        // --- Range slider ---
        _applyInitialBarHeights();
        rangeSlider = TableInfra.initRangeSlider(state, applyFilters);

        // --- Collection chips ---
        chips = document.querySelectorAll('.collection-chips .chip');
        chips.forEach(function(chip) {
            chip.addEventListener('click', function() {
                let val = chip.getAttribute('data-collection');
                if (state.collection === val) {
                    state.collection = '';
                    chip.classList.remove('active');
                } else {
                    chips.forEach(function(c) { c.classList.remove('active'); });
                    state.collection = val;
                    chip.classList.add('active');
                }
                applyFilters();
            });
        });

        // --- Place filter ---
        if (filterPlace) {
            filterPlace.addEventListener('change', function() {
                state.place = filterPlace.value;
                applyFilters();
            });
        }

        // --- Facsimile filter ---
        if (filterFacs) {
            filterFacs.addEventListener('change', function() {
                state.facs = filterFacs.value;
                applyFilters();
            });
        }

        // --- URL parameter restore — for shareable links and browser back ---
        // Supports: collection, place, facs, q (search), yearMin/yearMax.
        // Read once at init; later changes are written by syncUrlFromState()
        // via replaceState().
        let urlParams = new URLSearchParams(window.location.search);
        let urlQuery = urlParams.get('q');
        if (urlQuery) {
            state.query = urlQuery;
            let si = document.getElementById('search-input');
            if (si) si.value = urlQuery;
        }
        let urlPlace = urlParams.get('place');
        if (urlPlace && filterPlace) {
            state.place = urlPlace;
            filterPlace.value = urlPlace;
        }
        let urlFacs = urlParams.get('facs');
        if (urlFacs !== null && filterFacs) {
            state.facs = urlFacs;
            filterFacs.value = urlFacs;
        }
        let urlSex = urlParams.get('sex');
        if (urlSex && filterSex) {
            state.sex = urlSex;
            filterSex.value = urlSex;
        }
        let urlForms = urlParams.get('forms');
        if (urlForms && filterFormsEl) {
            state.forms = urlForms.split(',').filter(Boolean);
            state.forms.forEach(function(f) {
                let chip = filterFormsEl.querySelector('.form-filter-chip[data-form="' + f + '"]');
                if (chip) {
                    chip.classList.add('is-active');
                    chip.setAttribute('aria-pressed', 'true');
                }
            });
        }
        let urlCollection = urlParams.get('collection');
        if (urlCollection) {
            state.collection = urlCollection;
            chips.forEach(function(c) {
                if (c.getAttribute('data-collection') === urlCollection) {
                    c.classList.add('active');
                } else {
                    c.classList.remove('active');
                }
            });
        }
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

        // Standard faceted-search pattern: per filter dimension the counts
        // are computed taking ALL OTHER filters into account. skip is the
        // dimension to ignore ('collection' | 'place' | 'facs' | 'sex' |
        // 'forms' | 'year' | 'query' | null).
        function matchesAllExcept(doc, skip) {
            if (skip !== 'collection' && state.collection && doc.cp !== state.collection) return false;
            if (skip !== 'place' && !docMatchesPlace(doc, state.place)) return false;
            if (skip !== 'facs') {
                if (state.facs === '1' && !doc.f) return false;
                if (state.facs === '0' && doc.f) return false;
            }
            if (skip !== 'sex' && !docMatchesSex(doc, state.sex)) return false;
            if (skip !== 'forms' && !docMatchesForms(doc, state.forms)) return false;
            if (skip !== 'year' && state.yearMin > 0 && state.yearMax < 9999) {
                let year = parseInt(doc.di);
                if (isNaN(year) || year < state.yearMin || year > state.yearMax) return false;
            }
            if (skip !== 'query' && state.query) {
                let words = state.query.split(/\s+/);
                for (let i = 0; i < words.length; i++) {
                    if (doc._s.indexOf(words[i]) === -1) return false;
                }
            }
            return true;
        }

        function updateCorpusCounts() {
            if (!chips) return;
            let counts = {};
            allDocs.forEach(function(doc) {
                if (!matchesAllExcept(doc, 'collection')) return;
                counts[doc.cp] = (counts[doc.cp] || 0) + 1;
            });
            chips.forEach(function(chip) {
                let key = chip.getAttribute('data-collection');
                let countEl = chip.querySelector('.chip-count');
                if (countEl) countEl.textContent = counts[key] || 0;
            });
        }

        // Live histogram: recompute bar heights from the filtered sources
        // per decade. Only the year range is ignored, so that bars show
        // the FULL distribution under the other active filters — this
        // keeps the slider usable.
        function updateHistogram() {
            let bars = document.querySelectorAll('.range-bar');
            if (!bars.length) return;
            let counts = {};
            allDocs.forEach(function(doc) {
                if (!matchesAllExcept(doc, 'year')) return;
                let year = parseInt(doc.di);
                if (isNaN(year)) return;
                let decade = Math.floor(year / 10) * 10;
                counts[decade] = (counts[decade] || 0) + 1;
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
                bar.title = dec + 'er: ' + c + ' Quellen';
            });
        }

        // Map initial heights from template data-height onto the CSS variable.
        // Reads the build-time bar heights once on load.
        function _applyInitialBarHeights() {
            document.querySelectorAll('.range-bar').forEach(function(bar) {
                let h = parseInt(bar.getAttribute('data-height')) || 0;
                bar.style.setProperty('--bar-height', h + '%');
            });
        }

        // Live counts on filter dropdowns. For each option the hit count
        // is computed against the other active filters — this saves the
        // user empty selections ("Wien (0)" when another filter already
        // excludes all Vienna entries).
        function _setOptionLabel(opt, baseLabel, count) {
            opt.textContent = count !== null
                ? baseLabel + ' (' + count + ')'
                : baseLabel;
        }

        // Zero-hit options are hidden so users do not run into dead-end
        // clicks ('Wien (0)' under a Stadtbuecher filter). The currently
        // selected option is NOT hidden — otherwise there is no way to
        // clear the filter via the dropdown (the active-filter chip with
        // X still works, but the consistency expectation is that the
        // chosen value is visible in the dropdown).
        function _setOptionHidden(opt, count, isCurrent) {
            opt.hidden = (count === 0 && !isCurrent);
        }

        function _setChipHidden(chip, count) {
            // Chips stay usable (to clear the selection) while active —
            // otherwise removed as soon as the count drops to 0.
            let isActive = chip.classList.contains('is-active') ||
                           chip.classList.contains('active');
            chip.hidden = (count === 0 && !isActive);
        }

        function updateDropdownCounts() {
            // Place
            if (filterPlace) {
                let counts = {};
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'place')) return;
                    if (doc.p) counts[doc.p] = (counts[doc.p] || 0) + 1;
                });
                filterPlace.querySelectorAll('option').forEach(function(opt) {
                    if (!opt.dataset.label) opt.dataset.label = opt.textContent.split(' (')[0];
                    let val = opt.value;
                    if (val === '') {
                        _setOptionLabel(opt, opt.dataset.label, null);
                    } else if (val === '__none__') {
                        // handled separately below
                    } else {
                        let c = counts[val] || 0;
                        _setOptionLabel(opt, opt.dataset.label, c);
                        _setOptionHidden(opt, c, state.place === val);
                    }
                });
            }
            // Facsimile
            if (filterFacs) {
                let withFacs = 0, withoutFacs = 0;
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'facs')) return;
                    if (doc.f) withFacs++;
                    else withoutFacs++;
                });
                filterFacs.querySelectorAll('option').forEach(function(opt) {
                    if (!opt.dataset.label) opt.dataset.label = opt.textContent.split(' (')[0];
                    if (opt.value === '1') {
                        _setOptionLabel(opt, opt.dataset.label, withFacs);
                        _setOptionHidden(opt, withFacs, state.facs === '1');
                    } else if (opt.value === '0') {
                        _setOptionLabel(opt, opt.dataset.label, withoutFacs);
                        _setOptionHidden(opt, withoutFacs, state.facs === '0');
                    } else {
                        _setOptionLabel(opt, opt.dataset.label, null);
                    }
                });
            }
            // Sex mix
            if (filterSex) {
                let counts = {'with-f': 0, 'only-f': 0, 'only-m': 0, 'none': 0};
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'sex')) return;
                    if (doc.pcdf > 0) counts['with-f']++;
                    if (doc.pcdf > 0 && doc.pcdm === 0) counts['only-f']++;
                    if (doc.pcdm > 0 && doc.pcdf === 0) counts['only-m']++;
                    if (doc.pcd === 0) counts['none']++;
                });
                filterSex.querySelectorAll('option').forEach(function(opt) {
                    if (!opt.dataset.label) opt.dataset.label = opt.textContent.split(' (')[0];
                    if (opt.value === '') {
                        _setOptionLabel(opt, opt.dataset.label, null);
                    } else {
                        let c = counts[opt.value] || 0;
                        _setOptionLabel(opt, opt.dataset.label, c);
                        _setOptionHidden(opt, c, state.sex === opt.value);
                    }
                });
            }
            // Form-of-treatment chips
            if (filterFormsEl) {
                let counts = {R:0, S:0, E:0, N:0, none:0};
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'forms')) return;
                    if (doc.ecR) counts.R++;
                    if (doc.ecS) counts.S++;
                    if (doc.ecE) counts.E++;
                    if (doc.ecN) counts.N++;
                    if (!doc.ecR && !doc.ecS && !doc.ecE && !doc.ecN) counts.none++;
                });
                filterFormsEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                    let f = c.getAttribute('data-form');
                    let n = counts[f] || 0;
                    let countEl = c.querySelector('.form-filter-chip-count');
                    if (countEl) countEl.textContent = n;
                    _setChipHidden(c, n);
                });
            }
            // Place: "no place given" option
            if (filterPlace) {
                let noPlaceCount = 0;
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'place')) return;
                    if (!doc.p) noPlaceCount++;
                });
                let opt = filterPlace.querySelector('option[value="__none__"]');
                if (opt) {
                    if (!opt.dataset.label) opt.dataset.label = '(ohne Ortsangabe)';
                    _setOptionLabel(opt, opt.dataset.label, noPlaceCount);
                    _setOptionHidden(opt, noPlaceCount, state.place === '__none__');
                }
            }
        }

        // Filter state -> URL. history.replaceState() writes without adding
        // a history entry, so browser-back does NOT step through filter
        // states (standard SPA convention for filter UIs).
        // urlSyncEnabled guard: during init multiple applyFilters calls run
        // before URL params are read in — they would clear the URL. Flag
        // forward-declared above.
        function syncUrlFromState() {
            if (!urlSyncEnabled) return;
            let p = new URLSearchParams();
            if (state.collection) p.set('collection', state.collection);
            if (state.place) p.set('place', state.place);
            if (state.facs) p.set('facs', state.facs);
            if (state.sex) p.set('sex', state.sex);
            if (state.forms && state.forms.length) p.set('forms', state.forms.join(','));
            if (state.query) p.set('q', state.query);
            if (rangeSlider && rangeSlider.isFiltered && rangeSlider.isFiltered()) {
                p.set('yearMin', state.yearMin);
                p.set('yearMax', state.yearMax);
            }
            let qs = p.toString();
            let url = location.pathname + (qs ? '?' + qs : '') + location.hash;
            history.replaceState(null, '', url);
        }

        // Sort comparator. Empty values always go to the bottom, regardless
        // of sort direction (standard data-table behaviour). Date values are
        // either clean ISO ('1177-05-10') or range form
        // ('1198-01-01 | 1230-12-31') — comparing the first 10 chars gives a
        // lexicographically consistent key. Strings are compared locale-aware
        // ('de') so umlauts sort correctly.
        //
        // Editorial notation: '[Wien]' (square brackets = editorially
        // reconstructed place name) must sort under W, not under '['.
        // Likewise 'Wien,' (a trailing comma from the source) must sort with
        // Wien. _sortKey strips square brackets globally and trims leading/
        // trailing punctuation that is only notation — 'St. Pölten' is left
        // alone because its dot is internal.
        function _sortKey(v) {
            return String(v)
                .replace(/[\[\]]/g, '')
                .replace(/^[\s,;:]+|[\s,;:]+$/g, '');
        }
        function _compareDocs(a, b, key, dir) {
            let va = a[key];
            let vb = b[key];
            if (key === 'di') {
                va = (typeof va === 'string') ? va.slice(0, 10) : '';
                vb = (typeof vb === 'string') ? vb.slice(0, 10) : '';
            }
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

        // --- Core filter logic ---
        function applyFilters() {
            state.previewIdx = -1;

            filteredDocs = allDocs.filter(function(doc) {
                if (state.collection && doc.cp !== state.collection) return false;
                return matchesAllExcept(doc, 'collection');
            });

            filteredDocs.sort(function(a, b) {
                return _compareDocs(a, b, state.sortKey, state.sortDir);
            });

            renderer.render(filteredDocs);
            if (resultCount) resultCount.textContent = filteredDocs.length + ' Quellen';
            updateActiveFilters();
            updateCorpusCounts();
            updateHistogram();
            updateDropdownCounts();
            syncUrlFromState();
        }

        // --- Reset button: clear all filters ---
        let resetBtn = document.getElementById('filter-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                state.collection = '';
                state.place = '';
                state.facs = '';
                state.sex = '';
                state.forms = [];
                state.query = '';
                chips.forEach(function(c) { c.classList.remove('active'); });
                if (filterPlace) filterPlace.value = '';
                if (filterFacs) filterFacs.value = '';
                if (filterSex) filterSex.value = '';
                if (filterFormsEl) {
                    filterFormsEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                        c.classList.remove('is-active');
                        c.setAttribute('aria-pressed', 'false');
                    });
                }
                let si = document.getElementById('search-input');
                if (si) si.value = '';
                if (rangeSlider && rangeSlider.reset) rangeSlider.reset();
                applyFilters();
            });
        }

        // --- Event listeners for the additional filters ---
        if (filterSex) {
            filterSex.addEventListener('change', function() {
                state.sex = filterSex.value;
                applyFilters();
            });
        }
        if (filterFormsEl) {
            filterFormsEl.querySelectorAll('.form-filter-chip').forEach(function(chip) {
                chip.addEventListener('click', function() {
                    let f = chip.getAttribute('data-form');
                    let idx = state.forms.indexOf(f);
                    if (idx === -1) {
                        state.forms.push(f);
                        chip.classList.add('is-active');
                        chip.setAttribute('aria-pressed', 'true');
                    } else {
                        state.forms.splice(idx, 1);
                        chip.classList.remove('is-active');
                        chip.setAttribute('aria-pressed', 'false');
                    }
                    applyFilters();
                });
            });
        }

        // --- Preview row ---
        function togglePreview(idx) {
            let tbody = document.getElementById('doc-tbody');
            let existing = tbody.querySelector('.preview-row');
            // Mark any previously open row as closed (chevron rotates back).
            tbody.querySelectorAll('.doc-row.is-open').forEach(function(r) {
                r.classList.remove('is-open');
                r.setAttribute('aria-expanded', 'false');
            });
            if (existing) existing.remove();

            if (state.previewIdx === idx) { state.previewIdx = -1; return; }

            state.previewIdx = idx;
            let doc = filteredDocs[idx];
            let tr = tbody.querySelector('tr[data-idx="' + idx + '"]');
            if (!tr) return;
            tr.classList.add('is-open');
            tr.setAttribute('aria-expanded', 'true');

            let previewTr = document.createElement('tr');
            previewTr.className = 'preview-row';

            let thumbHtml = '';
            if (doc.fu) {
                thumbHtml = '<div class="preview-thumb"><img src="' + esc(doc.fu) + '" loading="lazy" alt="Faksimile"></div>';
            }

            previewTr.innerHTML =
                '<td colspan="5"><div class="doc-preview">' +
                '<div class="preview-text">' +
                '<p class="preview-regest">' + esc(doc.tf || doc.t) + '</p>' +
                '<div class="preview-meta">' +
                '<span>' + esc(doc.d) + '</span>' +
                (doc.p ? '<span>' + esc(doc.p) + '</span>' : '') +
                '<span>' + esc(doc.cl) + '</span>' +
                (doc.pcd ? '<span>' + doc.pcd + ' Personen</span>' : '') +
                '</div>' +
                '<a href="' + esc(doc.u) + '" class="preview-link">Quelle anzeigen \u2192</a>' +
                '</div>' +
                thumbHtml +
                '</div></td>';

            tr.after(previewTr);
        }

        // --- Filter helpers ---
        function clearFilter(key, uiReset) {
            return function() {
                state[key] = '';
                if (uiReset) uiReset();
                applyFilters();
            };
        }

        function updateActiveFilters() {
            if (!activeFiltersEl) return;
            activeFiltersEl.innerHTML = '';

            if (state.collection) {
                TableInfra.addFilterChip(activeFiltersEl, 'Quellenkorpus: ' + (collectionLabels[state.collection] || state.collection),
                    clearFilter('collection', function() { chips.forEach(function(c) { c.classList.remove('active'); }); }));
            }
            if (state.query) {
                // Consistency: search acts as a filter, so it belongs in the
                // active-filter strip — otherwise the hit counts look
                // unexplainable.
                TableInfra.addFilterChip(activeFiltersEl, 'Suche: ' + state.query,
                    clearFilter('query', function() {
                        let si = document.getElementById('search-input');
                        if (si) si.value = '';
                        let sc = document.getElementById('search-clear');
                        if (sc) sc.classList.add('hidden');
                    }));
            }
            if (state.place) {
                let placeLabel = state.place === '__none__' ? 'Ort: (ohne Ortsangabe)' : 'Ort: ' + state.place;
                TableInfra.addFilterChip(activeFiltersEl, placeLabel,
                    clearFilter('place', function() { if (filterPlace) filterPlace.value = ''; }));
            }
            if (state.sex) {
                let sexLabels = {
                    'with-f': 'Mit Frauenbeteiligung',
                    'only-f': 'Nur Frauen',
                    'only-m': 'Nur Männer',
                    'none':   'Ohne Personen'
                };
                TableInfra.addFilterChip(activeFiltersEl, 'Geschlecht: ' + (sexLabels[state.sex] || state.sex),
                    clearFilter('sex', function() { if (filterSex) filterSex.value = ''; }));
            }
            if (state.forms && state.forms.length) {
                let formLabels = {R: 'Regest', S: 'Siegel', E: 'Eintrag', N: 'Nota', none: 'ohne Form'};
                let formsLabel = 'Form: ' + state.forms.map(function(f) { return formLabels[f] || f; }).join(', ');
                TableInfra.addFilterChip(activeFiltersEl, formsLabel, function() {
                    state.forms = [];
                    if (filterFormsEl) {
                        filterFormsEl.querySelectorAll('.form-filter-chip').forEach(function(c) {
                            c.classList.remove('is-active');
                            c.setAttribute('aria-pressed', 'false');
                        });
                    }
                    applyFilters();
                });
            }
            if (state.facs) {
                TableInfra.addFilterChip(activeFiltersEl, state.facs === '1' ? 'Mit Faksimile' : 'Ohne Faksimile',
                    clearFilter('facs', function() { if (filterFacs) filterFacs.value = ''; }));
            }
            if (rangeSlider && rangeSlider.isFiltered()) {
                TableInfra.addFilterChip(activeFiltersEl, 'Zeitraum: ' + state.yearMin + '–' + state.yearMax,
                    function() { rangeSlider.reset(); });
            }
        }

        // --- Load data from external JSON file ---
        let tbody = document.getElementById('doc-tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="cell-placeholder">Daten werden geladen\u2026</td></tr>';

        fetch((window.ROOT_PATH || '.') + '/data/search.json')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                allDocs = data;
                // Pre-compute search strings (V3: Umlaut-tolerant via EdCore.normForSearch)
                let norm = EdCore.normForSearch;
                allDocs.forEach(function(doc) {
                    doc._s = norm(doc.t + ' ' + doc.d + ' ' + doc.p + ' ' + doc.id + ' ' + doc.cl);
                    if (doc.cp && !collectionLabels[doc.cp]) collectionLabels[doc.cp] = doc.cl;
                });
                filteredDocs = allDocs.slice();
                // Release URL sync from here on: all URL params are already
                // read into state, allDocs is available, and further
                // applyFilters calls (user interactions) should write the
                // filter state back to the URL.
                urlSyncEnabled = true;
                applyFilters();
            })
            .catch(function(err) {
                console.warn('Suchdaten konnten nicht geladen werden:', err);
                tbody.innerHTML = '<tr><td colspan="5" class="cell-placeholder">Daten konnten nicht geladen werden.</td></tr>';
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('doc-table')) {
            initIndex();
        }
    });

})();
