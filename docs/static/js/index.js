/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Index page: search, filter, sort, preview
   ========================================================================== */

(function() {
    'use strict';

    let esc = EdCore.esc;

    // Mapping der Validierungs-Kategorien aus pipeline/validation_report.json
    // auf lesbare deutsche Labels. Unbekannte Codes fallen auf den Code zurueck.
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
        // Forward-Deklaration: rangeSlider, chips und urlSyncEnabled
        // werden in updateActiveFilters / updateCorpusCounts /
        // syncUrlFromState referenziert, BEVOR initRangeSlider
        // zurueckkehrt (Init-Callback ruft applyFilters synchron).
        // Mit let waeren sie in TDZ.
        let rangeSlider;
        let chips;
        let urlSyncEnabled = false;

        // State
        let allDocs = [];
        let state = {
            query: '',
            collection: '',
            place: '',         // Sonderwert '__none__' = "ohne Ortsangabe"
            facs: '',
            sex: '',           // '' | 'with-f' | 'only-f' | 'only-m' | 'none'
            forms: [],         // Array aus 'R','S','E','N','none' — leer = alle
            yearMin: 0,
            yearMax: 9999,
            sortKey: 'di',
            sortDir: 1,
            previewIdx: -1
        };

        // --- Form-Filter-Helfer: prueft, ob doc in den ausgewaehlten Formen
        // liegt. ODER-Verknuepfung innerhalb der Formen, AND zu allen anderen
        // Filtern. Leere Auswahl = alle Quellen erlaubt.
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

        // --- Content cell renderer (Inhalt-Spalte) ---
        // Persons-Badge mit Geschlechter-Aufschluesselung im title; danach
        // Form-Pills R/S/E/N (TEI-Annotations-Tiefe) plus Faksimile-Pill
        // F als kleine Strich-Icons; Multi-Event-Indikator, wenn die Quelle
        // mehrere Rechtsgeschaefte dokumentiert.
        //
        // Icons sind currentColor-Strich-SVGs, damit sie die Pillen-Farbe
        // (--anno-person) erben und Hover-States ohne Sonderlogik mitnehmen.
        let FORM_ICONS = {
            // Regest: drei zusammenfassende Linien (Standard-"Summary")
            r: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M3.5 5h9M3.5 8h9M3.5 11h6" ' +
               'stroke="currentColor" stroke-width="1.4" stroke-linecap="round" fill="none"/>' +
               '</svg>',
            // Siegel: Petschaft-Anmutung – runder Siegelring mit innerem
            // Kreis und kleinem Mittelpunkt. Kein Stern/Rad.
            s: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.4" fill="none"/>' +
               '<circle cx="8" cy="8" r="2.2" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
               '<circle cx="8" cy="8" r="0.6" fill="currentColor"/>' +
               '</svg>',
            // Eintrag: aufgeschlagenes Buch / zwei Seiten
            e: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M8 4.5v8M3 4.5c1.5 0 3.4.4 5 1.2c1.6-.8 3.5-1.2 5-1.2v7c-1.5 0-3.4.4-5 1.2c-1.6-.8-3.5-1.2-5-1.2v-7z" ' +
               'stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Nota: Lesezeichen / kleiner Notiz-Marker
            n: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<path d="M5 3h6v10l-3-2.2L5 13z" ' +
               'stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Faksimile: Bild-Rahmen mit Sonne-und-Berg-Andeutung
            f: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<rect x="2.4" y="3.4" width="11.2" height="9.2" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
               '<circle cx="6" cy="7" r="1.1" stroke="currentColor" stroke-width="1.1" fill="none"/>' +
               '<path d="M2.6 11.6l3-2.6l2.4 2l3-2.6l2.4 2.2" ' +
               'stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" fill="none"/>' +
               '</svg>',
            // Mehrere Rechtsgeschaefte: zwei leicht versetzte Rechtecke,
            // lesen sich als 'mehr als ein Vorgang in einer Quelle'.
            m: '<svg viewBox="0 0 16 16" aria-hidden="true">' +
               '<rect x="2.6" y="4.6" width="7.6" height="7.6" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="none"/>' +
               '<rect x="5.8" y="2.6" width="7.6" height="7.6" rx="1" ' +
               'stroke="currentColor" stroke-width="1.3" fill="var(--color-bg-card)"/>' +
               '</svg>'
        };

        function renderContent(doc) {
            let parts = [];

            if (doc.pcd > 0) {
                let label = doc.pcd === 1 ? '1 Person' : doc.pcd + ' Personen';
                let breakdown = [];
                if (doc.pcdf) breakdown.push(doc.pcdf + ' weiblich');
                if (doc.pcdm) breakdown.push(doc.pcdm + ' m\u00e4nnlich');
                if (doc.pcdu) breakdown.push(doc.pcdu + ' ohne Geschlechtsangabe');
                let title = breakdown.length
                    ? label + '\n' + breakdown.join(', ')
                    : label;
                parts.push(
                    '<span class="badge badge-persons" title="' + esc(title) + '">' +
                    esc(label) + '</span>'
                );
            }

            let pills = [];
            if (doc.ecR > 0) pills.push(['r', 'Regest', 'Regest-Annotation (TEI <div type="abstract">)']);
            if (doc.ecS > 0) pills.push(['s', 'Siegel', 'Siegelbeschreibung (TEI <div type="seal">)']);
            if (doc.ecE > 0) pills.push(['e', 'Eintrag', 'Stadtbuch-Eintrag (TEI <div type="entry">)']);
            if (doc.ecN > 0) pills.push(['n', 'Nota', 'Nachsatz/Notiz (TEI <div type="nota">)']);
            if (doc.f) pills.push(['f', 'Faksimile', 'Digitalisat des Originals verlinkt']);
            // Mehrere Rechtsgeschaefte als regulaere Pille \u2014 gestapelte
            // Rechtecke; die konkrete Anzahl steckt im Tooltip.
            if (doc.ec > 1) {
                pills.push(['m', 'Mehrere Rechtsgesch\u00e4fte',
                            doc.ec + ' Rechtsgesch\u00e4fte in einer Quelle']);
            }
            if (pills.length) {
                let html = pills.map(function(p) {
                    return '<span class="form-pill form-pill-' + p[0] +
                           '" title="' + esc(p[1] + ': ' + p[2]) +
                           '" aria-label="' + esc(p[1]) + '">' +
                           FORM_ICONS[p[0]] + '</span>';
                }).join('');
                parts.push('<span class="form-pills">' + html + '</span>');
            }

            return parts.join(' ');
        }

        // Datum-Cell mit Range-Hint: bei Mehrjahres-Range (z.B. "1198–1230")
        // erklaert ein title-Tooltip die Konvention "Datum unscharf,
        // gesicherter Zeitraum...". Bei sauberem Einzeldatum kein Tooltip.
        function renderDateCell(doc) {
            let dateText = doc.dn || doc.d;
            let attr = '';
            if (dateText && dateText.indexOf('–') !== -1) {
                attr = ' title="Datum unscharf — gesicherter Zeitraum laut TEI: ' +
                    esc(dateText.replace('–', ' bis ')) + '"';
            }
            return '<td class="col-date"' + attr + '>' + esc(dateText) + '</td>';
        }

        // SVG-Chevron als Ausklapp-Affordance. Wird per CSS rotiert,
        // sobald die Zeile expandiert ist (.doc-row.is-open).
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
                tr.innerHTML =
                    '<td class="col-idno"><a href="' + esc(doc.u) + '" class="doc-link">' + esc(doc.id) + '</a></td>' +
                    renderDateCell(doc) +
                    '<td class="col-place">' + esc(doc.p) + '</td>' +
                    '<td class="col-title"><span class="cell-title">' + esc(doc.t) + '</span></td>' +
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

        // --- URL parameter restore — fuer teilbare Links und Browser-Back ---
        // Unterstuetzt: collection, place, facs, quality, q (search),
        // yearMin/yearMax. Wird einmal beim Init gelesen; spaetere
        // Aenderungen schreibt syncUrlFromState() per replaceState().
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

        // Faceted-Search Standardmuster: pro Filter-Dimension werden die
        // Counts unter Beruecksichtigung ALLER ANDEREN Filter berechnet.
        // skip ist die zu ignorierende Dimension ('collection' | 'place' |
        // 'facs' | 'quality' | 'sex' | 'forms' | 'year' | 'query' | null).
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

        // Live-Histogramm: Bar-Hoehen aus den gefilterten Quellen pro
        // Dekade neu berechnen. Nur die Year-Range wird ignoriert,
        // damit die Bars die GESAMTVERTEILUNG bei sonst aktiven Filtern
        // zeigen — der Slider bleibt dadurch sinnvoll bedienbar.
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

        // Initial-Hoehen aus Template-data-height auf CSS-Variable mappen.
        // Liest die per Build berechneten Bar-Hoehen einmal beim Laden.
        function _applyInitialBarHeights() {
            document.querySelectorAll('.range-bar').forEach(function(bar) {
                let h = parseInt(bar.getAttribute('data-height')) || 0;
                bar.style.setProperty('--bar-height', h + '%');
            });
        }

        // Live-Counts auf Filter-Dropdowns. Pro Option wird die Treffer-
        // Zahl gegen die anderen aktiven Filter berechnet — das spart
        // dem User leere Selektionen ("Wien (0)" wenn schon ein Filter
        // alle Wiener ausschliesst).
        function _setOptionLabel(opt, baseLabel, count) {
            opt.textContent = count !== null
                ? baseLabel + ' (' + count + ')'
                : baseLabel;
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
                    } else {
                        _setOptionLabel(opt, opt.dataset.label, counts[val] || 0);
                    }
                });
            }
            // Faksimile
            if (filterFacs) {
                let withFacs = 0, withoutFacs = 0;
                allDocs.forEach(function(doc) {
                    if (!matchesAllExcept(doc, 'facs')) return;
                    if (doc.f) withFacs++;
                    else withoutFacs++;
                });
                filterFacs.querySelectorAll('option').forEach(function(opt) {
                    if (!opt.dataset.label) opt.dataset.label = opt.textContent.split(' (')[0];
                    if (opt.value === '1') _setOptionLabel(opt, opt.dataset.label, withFacs);
                    else if (opt.value === '0') _setOptionLabel(opt, opt.dataset.label, withoutFacs);
                    else _setOptionLabel(opt, opt.dataset.label, null);
                });
            }
            // Geschlechter-Mix
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
                    if (opt.value === '') _setOptionLabel(opt, opt.dataset.label, null);
                    else _setOptionLabel(opt, opt.dataset.label, counts[opt.value] || 0);
                });
            }
            // Erschliessungsform-Chips
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
                    let countEl = c.querySelector('.form-filter-chip-count');
                    if (countEl) countEl.textContent = counts[f] || 0;
                });
            }
            // Place: ohne-Ortsangabe-Option
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
                }
            }
        }

        // Filter-State -> URL. history.replaceState() schreibt ohne
        // History-Eintrag, damit Browser-Back NICHT durch Filterstaende
        // geht (Standard-SPA-Konvention bei Filter-UIs).
        // urlSyncEnabled-Guard: waehrend Init laufen mehrere
        // applyFilters-Calls bevor die URL-Parameter eingelesen sind —
        // sie wuerden die URL leeren. Flag oben forward-deklariert.
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

        // --- Core filter logic ---
        function applyFilters() {
            state.previewIdx = -1;

            filteredDocs = allDocs.filter(function(doc) {
                if (state.collection && doc.cp !== state.collection) return false;
                return matchesAllExcept(doc, 'collection');
            });

            filteredDocs.sort(function(a, b) {
                let va = a[state.sortKey] || '';
                let vb = b[state.sortKey] || '';
                if (va < vb) return -state.sortDir;
                if (va > vb) return state.sortDir;
                return 0;
            });

            renderer.render(filteredDocs);
            if (resultCount) resultCount.textContent = filteredDocs.length + ' Quellen';
            updateActiveFilters();
            updateCorpusCounts();
            updateHistogram();
            updateDropdownCounts();
            syncUrlFromState();
        }

        // --- Reset-Button: alle Filter zuruecksetzen ---
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

        // --- Filter-Event-Listener fuer die neuen Filter ---
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
            // Vorher offene Zeile als geschlossen markieren (Chevron dreht zurueck).
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

            // Qualitaets-Hinweise tauchen in der Vorschau bewusst NICHT auf:
            // die Findings sind redaktionell-technische Annotations-Hinweise
            // (Datierungs-Attribut, leere Referenz etc.) und gehoeren in die
            // Quellansicht selbst, wo sie kontextuell verankert werden koennen.
            // Das Dot-Signal in der Tabelle bleibt als 'da gibt's noch was'-Hinweis.
            let qualityHtml = '';

            previewTr.innerHTML =
                '<td colspan="5"><div class="doc-preview">' +
                '<div class="preview-text">' +
                '<p class="preview-regest">' + esc(doc.tf || doc.t) + '</p>' +
                qualityHtml +
                '<div class="preview-meta">' +
                '<span>' + esc(doc.d) + '</span>' +
                (doc.p ? '<span>' + esc(doc.p) + '</span>' : '') +
                '<span>' + esc(doc.cl) + '</span>' +
                (doc.pc ? '<span>' + doc.pc + ' Personen</span>' : '') +
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
                // Konsistenz: Suche ist filterwirksam und gehoert daher in
                // die aktive-Filter-Leiste, sonst sind die Trefferzahlen
                // unerklaerlich.
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
                // URL-Sync ab jetzt freigeben: alle URL-Parameter sind
                // bereits in state eingelesen, allDocs ist verfuegbar,
                // weitere applyFilters-Calls (User-Interaktionen) sollen
                // den Filterstand in die URL schreiben.
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
