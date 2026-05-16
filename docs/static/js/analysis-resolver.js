/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis/index.html
   Konstellations-Resolver

   Datenbank-Abfrage-UI ueber docs/data/role_constellation.json.

   - Anfangszustand: keine Personen-Box, leere Trefferliste.
   - Forscherin klickt "+ Person hinzufuegen": neue nummerierte Box mit
     Rollen-Dropdown und optionalen Bedingungen (Geschlecht, Beruf-enthaelt).
   - Mindestens eine Box mit gesetzter Rolle => Treffer werden gerechnet.
   - Live-Update bei jeder Aenderung, kein Submit.
   - URL-Hash serialisiert den Abfrage-Stand, Reload reproduziert ihn.
   - CSV-Export der aktuellen Tabelle.

   Datenshape (role_constellation.json::events[]):
     { e, f, c, d, tx,
       p: [ { p, n, r, s, t, o } ] }
       r ∈ {issuer, recipient, witness, other}
       s ∈ {m, f, ""}
       o[] = occupation strings (Originalform)
   ========================================================================== */

(function () {
    'use strict';

    /* ---------- DOM-Bezuege ---------------------------------------------- */
    const root = document.querySelector('.analysis-query');
    if (!root) return;

    const personsTable = root.querySelector('#qb-persons-table');
    const personsTbody = root.querySelector('#qb-persons-tbody');
    const addPersonBtn = root.querySelector('#qb-add-person');
    const resetBtn = root.querySelector('#filter-reset');
    const scopeChips = root.querySelectorAll('[data-filter="scope"] .form-filter-chip');
    const corpusChipsRoot = root.querySelector('#filter-corpora');
    const rangeMin = root.querySelector('#range-min');
    const rangeMax = root.querySelector('#range-max');
    const rangeLabelMin = root.querySelector('#range-label-min');
    const rangeLabelMax = root.querySelector('#range-label-max');
    const hitsSrc = root.querySelector('#hits-sources');
    const hitsEv  = root.querySelector('#hits-events');
    const tbody = root.querySelector('#hits-tbody');
    const emptyBox = root.querySelector('#hits-empty');
    const emptyMsg = root.querySelector('#hits-empty-msg');
    const csvBtn = root.querySelector('#csv-download');
    const activeStrip = root.querySelector('#active-filters');

    /* ---------- Daten ---------------------------------------------------- */
    let DATA = null;       // role_constellation.json
    let OCC_VOCAB = [];    // [{value, count}]
    let dataPromise = null;

    function getDataUrl() {
        const tag = document.getElementById('role-constellation-data');
        try {
            return JSON.parse(tag.textContent).url;
        } catch (_) {
            return '../data/role_constellation.json';
        }
    }

    function loadData() {
        if (DATA) return Promise.resolve(DATA);
        if (dataPromise) return dataPromise;
        dataPromise = fetch(getDataUrl())
            .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
            .then(json => { DATA = json; return DATA; })
            .catch(err => {
                emptyMsg.textContent =
                    'Daten konnten nicht geladen werden (' + err.message + '). ' +
                    'Bitte Seite neu laden.';
                throw err;
            });
        return dataPromise;
    }

    // Occupation-Vokabular ist im Personen-Tabellen-Container hinterlegt
    // (data-occupation-vocab attribute). Wir lesen es einmal.
    try {
        OCC_VOCAB = JSON.parse(personsTable.dataset.occupationVocab || '[]');
    } catch (_) { OCC_VOCAB = []; }

    /* ---------- Zustand -------------------------------------------------- */
    // State-Form:
    //   { persons: [ {role, sex, occ} ],
    //     scope: 'event'|'source',
    //     yearMin, yearMax,
    //     corpora: Set<string> }
    let state = {
        persons: [],
        scope: 'event',
        yearMin: rangeMin ? +rangeMin.min : 1177,
        yearMax: rangeMax ? +rangeMax.max : 1414,
        corpora: new Set()
    };
    const RELEASED_MIN = state.yearMin;
    const RELEASED_MAX = state.yearMax;

    const ROLE_LABELS = {
        issuer:    'Aussteller',
        recipient: 'Empfänger',
        witness:   'Zeuge / Siegler',
        other:     'sonstige Beteiligung'
    };
    const ROLE_LIST = ['issuer', 'recipient', 'witness', 'other'];
    const SEX_LABELS = { m: 'männlich', f: 'weiblich', u: 'ohne Angabe' };

    /* ---------- Renderer: Personen-Tabelle ------------------------------ */
    function renderPersonRow(idx, p) {
        const tr = document.createElement('tr');
        tr.className = 'qb-person-row';
        tr.dataset.personIdx = idx;

        // Spalte Nr.
        const numTd = document.createElement('td');
        numTd.className = 'qb-col-num';
        const numSpan = document.createElement('span');
        numSpan.className = 'qb-person-num';
        numSpan.textContent = idx + 1;
        numTd.appendChild(numSpan);
        tr.appendChild(numTd);

        // Spalte Rolle (Pflicht)
        const roleTd = document.createElement('td');
        roleTd.className = 'qb-col-role';
        const roleSel = document.createElement('select');
        roleSel.className = 'qb-person-role';
        roleSel.setAttribute('aria-label', 'Rolle Person ' + (idx + 1));
        const blank = document.createElement('option');
        blank.value = '';
        blank.textContent = '— Rolle wählen —';
        roleSel.appendChild(blank);
        ROLE_LIST.forEach(r => {
            const o = document.createElement('option');
            o.value = r;
            o.textContent = ROLE_LABELS[r];
            if (p.role === r) o.selected = true;
            roleSel.appendChild(o);
        });
        roleSel.addEventListener('change', () => {
            state.persons[idx].role = roleSel.value;
            sync();
        });
        roleTd.appendChild(roleSel);
        tr.appendChild(roleTd);

        // Spalte Geschlecht (optional)
        const sexTd = document.createElement('td');
        sexTd.className = 'qb-col-sex';
        const sexSel = document.createElement('select');
        sexSel.setAttribute('aria-label', 'Geschlecht Person ' + (idx + 1));
        ['', 'm', 'f', 'u'].forEach(v => {
            const o = document.createElement('option');
            o.value = v;
            o.textContent = v === '' ? '— alle —' : SEX_LABELS[v];
            if ((p.sex || '') === v) o.selected = true;
            sexSel.appendChild(o);
        });
        sexSel.addEventListener('change', () => {
            state.persons[idx].sex = sexSel.value;
            sync();
        });
        sexTd.appendChild(sexSel);
        tr.appendChild(sexTd);

        // Spalte Beruf, Tätigkeit oder Amt (optional, Substring, Vorschlagsliste)
        const occTd = document.createElement('td');
        occTd.className = 'qb-col-occ';
        const occInput = document.createElement('input');
        occInput.type = 'text';
        occInput.setAttribute('list', 'qb-occ-suggestions');
        occInput.setAttribute('aria-label',
            'Beruf, Tätigkeit oder Amt Person ' + (idx + 1) + ' (enthält)');
        occInput.placeholder = 'z. B. purger, Bürger, pharrer';
        occInput.value = p.occ || '';
        occInput.addEventListener('input', () => {
            state.persons[idx].occ = occInput.value.trim();
            sync();
        });
        occTd.appendChild(occInput);
        tr.appendChild(occTd);

        // Spalte Entfernen
        const rmTd = document.createElement('td');
        rmTd.className = 'qb-col-rm';
        const rm = document.createElement('button');
        rm.type = 'button';
        rm.className = 'qb-person-remove';
        rm.setAttribute('aria-label', 'Person ' + (idx + 1) + ' entfernen');
        rm.innerHTML = '&times;';
        rm.addEventListener('click', () => {
            state.persons.splice(idx, 1);
            renderPersonsTable();
            sync();
        });
        rmTd.appendChild(rm);
        tr.appendChild(rmTd);

        return tr;
    }

    function renderPersonsTable() {
        personsTbody.innerHTML = '';
        state.persons.forEach((p, idx) => {
            personsTbody.appendChild(renderPersonRow(idx, p));
        });
        // Datalist für Occ-Vorschläge einmalig anlegen — ausserhalb der
        // Tabelle, damit es nicht im tbody clearend mit entfernt wird.
        if (!document.getElementById('qb-occ-suggestions')) {
            const dl = document.createElement('datalist');
            dl.id = 'qb-occ-suggestions';
            OCC_VOCAB.forEach(v => {
                const o = document.createElement('option');
                o.value = v.value;
                o.label = v.value + ' (' + v.count + ')';
                dl.appendChild(o);
            });
            personsTable.parentNode.appendChild(dl);
        }
        // Tabelle ausblenden, wenn keine Zeilen vorhanden — der Header
        // alleine waere optisch leer.
        personsTable.classList.toggle('is-empty', state.persons.length === 0);
    }

    /* ---------- Globale Filter: Verkabelung ----------------------------- */
    addPersonBtn.addEventListener('click', () => {
        state.persons.push({ role: '', sex: '', occ: '' });
        renderPersonsTable();
        sync();
    });

    scopeChips.forEach(chip => {
        chip.addEventListener('click', () => {
            scopeChips.forEach(c => {
                c.classList.remove('is-active');
                c.setAttribute('aria-pressed', 'false');
            });
            chip.classList.add('is-active');
            chip.setAttribute('aria-pressed', 'true');
            state.scope = chip.dataset.scope;
            sync();
        });
    });

    if (corpusChipsRoot) {
        corpusChipsRoot.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const key = chip.dataset.corpus;
                if (state.corpora.has(key)) {
                    state.corpora.delete(key);
                    chip.classList.remove('is-active');
                    chip.setAttribute('aria-pressed', 'false');
                } else {
                    state.corpora.add(key);
                    chip.classList.add('is-active');
                    chip.setAttribute('aria-pressed', 'true');
                }
                sync();
            });
        });
    }

    function updateRangeLabels() {
        if (rangeLabelMin) rangeLabelMin.textContent = state.yearMin;
        if (rangeLabelMax) rangeLabelMax.textContent = state.yearMax;
    }
    if (rangeMin && rangeMax) {
        const onRangeInput = () => {
            let lo = +rangeMin.value, hi = +rangeMax.value;
            if (lo > hi) { [lo, hi] = [hi, lo]; }
            state.yearMin = lo;
            state.yearMax = hi;
            updateRangeLabels();
            sync();
        };
        rangeMin.addEventListener('input', onRangeInput);
        rangeMax.addEventListener('input', onRangeInput);
    }

    resetBtn.addEventListener('click', () => {
        state.persons = [];
        state.scope = 'event';
        state.yearMin = RELEASED_MIN;
        state.yearMax = RELEASED_MAX;
        state.corpora.clear();
        // UI-Reset
        if (rangeMin) rangeMin.value = RELEASED_MIN;
        if (rangeMax) rangeMax.value = RELEASED_MAX;
        updateRangeLabels();
        scopeChips.forEach(c => {
            const isDefault = c.dataset.scope === 'event';
            c.classList.toggle('is-active', isDefault);
            c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
        });
        if (corpusChipsRoot) {
            corpusChipsRoot.querySelectorAll('.chip').forEach(c => {
                c.classList.remove('is-active');
                c.setAttribute('aria-pressed', 'false');
            });
        }
        renderPersonsTable();
        sync();
    });

    /* ---------- Matching ------------------------------------------------ */
    function eventInDateRange(ev) {
        const y = parseInt((ev.d || '').slice(0, 4), 10);
        if (isNaN(y)) return true;  // unknown date: do not exclude
        return y >= state.yearMin && y <= state.yearMax;
    }

    function eventInCorpus(ev) {
        if (!state.corpora.size) return true;
        return state.corpora.has(ev.c);
    }

    function personMatchesCard(person, card) {
        if (card.role && person.r !== card.role) return false;
        if (card.sex) {
            const s = person.s || '';
            if (card.sex === 'u' ? (s !== '') : (s !== card.sex)) return false;
        }
        if (card.occ) {
            const needle = card.occ.toLowerCase();
            const hit = (person.o || []).some(o => (o || '').toLowerCase().includes(needle));
            if (!hit) return false;
        }
        return true;
    }

    // Pro Treffer-Event ordnen wir jedem aktiven Block einen Participant zu
    // (distinct, kein doppeltes Belegen einer Person). Liefert die Liste der
    // zugeordneten Participants in Block-Reihenfolge, oder null bei Misserfolg.
    function assignParticipants(ev, cards) {
        const used = new Set();
        const out = [];
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i];
            let found = null;
            for (let j = 0; j < ev.p.length; j++) {
                if (used.has(j)) continue;
                if (personMatchesCard(ev.p[j], card)) { found = j; break; }
            }
            if (found == null) return null;
            used.add(found);
            out.push(ev.p[found]);
        }
        return out;
    }

    function activeCards() {
        return state.persons.filter(p => p.role);
    }

    function compute() {
        const cards = activeCards();
        if (!DATA || !cards.length) {
            return { hits: [], cards: cards };
        }
        const events = DATA.events || [];

        if (state.scope === 'event') {
            // Eng: Konstellation muss innerhalb desselben Events erfuellt sein.
            const hits = [];
            for (const ev of events) {
                if (!eventInDateRange(ev) || !eventInCorpus(ev)) continue;
                const assigned = assignParticipants(ev, cards);
                if (assigned) hits.push({ ev: ev, persons: assigned });
            }
            return { hits: hits, cards: cards };
        }

        // Weit: alle Personen muessen in derselben Quelle (file_key)
        // vorkommen, nicht zwingend im selben Event. Wir suchen pro Quelle
        // eine Block-Zuordnung, deren Treffer aus den Quell-Events stammen.
        const byFile = new Map();
        for (const ev of events) {
            if (!eventInDateRange(ev) || !eventInCorpus(ev)) continue;
            if (!byFile.has(ev.f)) byFile.set(ev.f, []);
            byFile.get(ev.f).push(ev);
        }
        const hits = [];
        for (const [fk, evs] of byFile.entries()) {
            // sammele alle Personen der Quelle in einem Pseudo-Event
            const allP = [];
            for (const ev of evs) for (const p of ev.p) allP.push(p);
            const pseudo = {
                e: evs[0].e, f: fk, c: evs[0].c,
                d: evs[0].d, tx: evs[0].tx, p: allP
            };
            const assigned = assignParticipants(pseudo, cards);
            if (assigned) hits.push({ ev: pseudo, persons: assigned });
        }
        return { hits: hits, cards: cards };
    }

    /* ---------- Renderer: Treffer-Tabelle ------------------------------- */
    function renderHits(result) {
        const { hits, cards } = result;
        const onboarding = root.querySelector('#qb-onboarding');
        tbody.innerHTML = '';
        if (!cards.length) {
            emptyBox.classList.remove('hidden');
            emptyMsg.textContent =
                'Noch keine Abfrage zusammengestellt. Einen Personenblock mit ' +
                'Rolle anlegen oder ein Beispiel unten anklicken.';
            if (onboarding) onboarding.classList.remove('hidden');
            hitsSrc.textContent = '0 Quellen';
            hitsEv.textContent = '0 Rechtsgeschäfte';
            csvBtn.setAttribute('disabled', '');
            return;
        }
        if (!hits.length) {
            emptyBox.classList.remove('hidden');
            emptyMsg.textContent =
                'Keine Treffer. Eine Bedingung lockern, einen Personenblock ' +
                'entfernen oder den Zeitraum erweitern.';
            if (onboarding) onboarding.classList.add('hidden');
            hitsSrc.textContent = '0 Quellen';
            hitsEv.textContent = '0 Rechtsgeschäfte';
            csvBtn.setAttribute('disabled', '');
            return;
        }
        emptyBox.classList.add('hidden');
        if (onboarding) onboarding.classList.add('hidden');

        const sourceKeys = new Set();
        const eventKeys = new Set();
        for (const h of hits) {
            sourceKeys.add(h.ev.f);
            eventKeys.add(h.ev.e);
        }
        hitsSrc.textContent = fmt(sourceKeys.size) + ' Quellen';
        hitsEv.textContent  = fmt(eventKeys.size)  + ' Rechtsgeschäfte';
        csvBtn.removeAttribute('disabled');

        // Stabil: sortiere nach Datum, dann nach Quelle.
        // Leere Datümer (Stadtbuch-Einträge ohne Einzeldatierung) ans Ende.
        hits.sort((a, b) => {
            const da = (a.ev.d || '').trim(), db = (b.ev.d || '').trim();
            if (!da && !db) return a.ev.f.localeCompare(b.ev.f);
            if (!da) return 1;
            if (!db) return -1;
            return da < db ? -1 : da > db ? 1 : a.ev.f.localeCompare(b.ev.f);
        });

        const frag = document.createDocumentFragment();
        const limit = 500;
        for (let i = 0; i < Math.min(hits.length, limit); i++) {
            frag.appendChild(buildRow(hits[i], cards));
        }
        if (hits.length > limit) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 5 + 1;
            td.style.textAlign = 'center';
            td.style.color = 'var(--color-text-light)';
            td.style.fontStyle = 'italic';
            td.textContent =
                '… ' + fmt(hits.length - limit) + ' weitere Treffer ' +
                'werden nicht in der Tabelle dargestellt. CSV-Download enthält alle.';
            tr.appendChild(td);
            frag.appendChild(tr);
        }
        tbody.appendChild(frag);
    }

    function buildRow(hit, cards) {
        const tr = document.createElement('tr');
        const ev = hit.ev;

        td(tr, formatDate(ev.d), 'col-date');

        const sourceTd = document.createElement('td');
        sourceTd.className = 'col-idno';
        const srcA = document.createElement('a');
        srcA.href = '../documents/' + encodeURIComponent(ev.f) + '.html';
        srcA.textContent = ev.f;
        sourceTd.appendChild(srcA);
        tr.appendChild(sourceTd);

        td(tr, ev.c, 'col-corpus');

        // Beteiligte Personen als Pills, eine pro Block.
        const personsTd = document.createElement('td');
        personsTd.className = 'col-persons';
        hit.persons.forEach((p, idx) => {
            const pill = document.createElement('span');
            pill.className = 'person-pill';
            const num = document.createElement('span');
            num.className = 'person-pill-num';
            num.textContent = idx + 1;
            const a = document.createElement('a');
            a.href = '../register/persons/' + encodeURIComponent(p.p) + '.html';
            a.textContent = p.n || p.p;
            pill.appendChild(num);
            pill.appendChild(a);
            personsTd.appendChild(pill);
        });
        tr.appendChild(personsTd);

        td(tr, ev.tx || '', 'col-tx');

        // Datenkorb-Button
        const basketTd = document.createElement('td');
        basketTd.className = 'col-basket';
        if (window.DataBasket && DataBasket.buttonHTML) {
            basketTd.innerHTML = DataBasket.buttonHTML({
                type: 'source',
                id: ev.f,
                label: ev.f,
                url: '../documents/' + ev.f + '.html',
                date: ev.d,
                coll: ev.c,
                regest: ''
            });
        }
        tr.appendChild(basketTd);

        return tr;
    }

    function td(tr, text, cls) {
        const el = document.createElement('td');
        if (cls) el.className = cls;
        el.textContent = text;
        tr.appendChild(el);
        return el;
    }

    function formatDate(s) {
        // "1342-04-08" -> "1342-04-08". Stadtbuch-Eintraege ohne
        // Einzeldatierung haben einen leeren d-Wert; im UI markieren
        // wir das transparent als "—".
        const t = (s || '').trim();
        return t || '—';
    }

    function fmt(n) {
        return n.toLocaleString('de-DE');
    }

    /* ---------- Aktive-Filter-Chips ------------------------------------- */
    function renderActiveFilters() {
        if (!activeStrip) return;
        activeStrip.innerHTML = '';
        const pieces = [];
        if (state.yearMin !== RELEASED_MIN || state.yearMax !== RELEASED_MAX) {
            pieces.push({ kind: 'time',
                label: state.yearMin + '–' + state.yearMax,
                on: () => { state.yearMin = RELEASED_MIN; state.yearMax = RELEASED_MAX;
                            rangeMin.value = RELEASED_MIN; rangeMax.value = RELEASED_MAX;
                            updateRangeLabels(); }});
        }
        for (const c of state.corpora) {
            pieces.push({ kind: 'corpus',
                label: 'Korpus: ' + c,
                on: () => {
                    state.corpora.delete(c);
                    corpusChipsRoot.querySelector('[data-corpus="' + c + '"]')
                        ?.classList.remove('is-active');
                }});
        }
        if (state.scope !== 'event') {
            pieces.push({ kind: 'scope',
                label: 'gemeinsam in: ' + (state.scope === 'source' ? 'Quelle' : 'Rechtsgeschäft'),
                on: () => {
                    state.scope = 'event';
                    scopeChips.forEach(c => {
                        const isDefault = c.dataset.scope === 'event';
                        c.classList.toggle('is-active', isDefault);
                        c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
                    });
                }});
        }
        if (!pieces.length) return;
        pieces.forEach(p => {
            const b = document.createElement('button');
            b.type = 'button';
            b.className = 'active-filter-chip';
            b.innerHTML = p.label + ' <span aria-hidden="true">&times;</span>';
            b.setAttribute('aria-label', p.label + ' entfernen');
            b.addEventListener('click', () => { p.on(); sync(); });
            activeStrip.appendChild(b);
        });
    }

    /* ---------- URL-State ----------------------------------------------- */
    function writeUrl() {
        const params = [];
        state.persons.forEach((p, idx) => {
            if (!p.role && !p.sex && !p.occ) return;
            const parts = [];
            if (p.role) parts.push('r=' + p.role);
            if (p.sex)  parts.push('s=' + p.sex);
            if (p.occ)  parts.push('o=' + encodeURIComponent(p.occ));
            params.push('p' + (idx + 1) + '=' + parts.join(','));
        });
        if (state.yearMin !== RELEASED_MIN || state.yearMax !== RELEASED_MAX) {
            params.push('y=' + state.yearMin + '-' + state.yearMax);
        }
        if (state.corpora.size) {
            params.push('c=' + Array.from(state.corpora).map(encodeURIComponent).join(','));
        }
        if (state.scope !== 'event') {
            params.push('scope=' + state.scope);
        }
        const hash = params.length ? '#' + params.join('&') : '';
        if (window.location.hash !== hash) {
            history.replaceState(null, '',
                window.location.pathname + window.location.search + hash);
        }
    }

    function readUrl() {
        const raw = window.location.hash.replace(/^#/, '');
        if (!raw) return;
        const parts = raw.split('&');
        const personRe = /^p(\d+)$/;
        parts.forEach(seg => {
            const eq = seg.indexOf('=');
            if (eq < 0) return;
            const k = seg.slice(0, eq);
            const v = seg.slice(eq + 1);
            const m = personRe.exec(k);
            if (m) {
                const idx = parseInt(m[1], 10) - 1;
                if (idx < 0) return;
                while (state.persons.length <= idx) {
                    state.persons.push({ role: '', sex: '', occ: '' });
                }
                v.split(',').forEach(pair => {
                    const e = pair.indexOf('=');
                    if (e < 0) return;
                    const pk = pair.slice(0, e), pv = decodeURIComponent(pair.slice(e + 1));
                    if (pk === 'r') state.persons[idx].role = pv;
                    if (pk === 's') state.persons[idx].sex = pv;
                    if (pk === 'o') state.persons[idx].occ = pv;
                });
            } else if (k === 'y') {
                const yr = v.split('-');
                if (yr.length === 2) {
                    const lo = parseInt(yr[0], 10), hi = parseInt(yr[1], 10);
                    if (!isNaN(lo) && !isNaN(hi)) {
                        state.yearMin = lo; state.yearMax = hi;
                        if (rangeMin) rangeMin.value = lo;
                        if (rangeMax) rangeMax.value = hi;
                        updateRangeLabels();
                    }
                }
            } else if (k === 'c') {
                v.split(',').map(decodeURIComponent).forEach(c => state.corpora.add(c));
                state.corpora.forEach(c => {
                    corpusChipsRoot.querySelector('[data-corpus="' + c + '"]')
                        ?.classList.add('is-active');
                    corpusChipsRoot.querySelector('[data-corpus="' + c + '"]')
                        ?.setAttribute('aria-pressed', 'true');
                });
            } else if (k === 'scope') {
                state.scope = v === 'source' ? 'source' : 'event';
                scopeChips.forEach(c => {
                    const active = c.dataset.scope === state.scope;
                    c.classList.toggle('is-active', active);
                    c.setAttribute('aria-pressed', active ? 'true' : 'false');
                });
            }
        });
    }

    /* ---------- CSV-Export ---------------------------------------------- */
    function csvEscape(s) {
        const str = (s == null) ? '' : String(s);
        if (/[",;\n]/.test(str)) return '"' + str.replace(/"/g, '""') + '"';
        return str;
    }

    function downloadCsv() {
        const result = compute();
        if (!result.hits.length) return;
        // Identische Sortierung wie in der Tabelle: nach Datum, leere
        // Datümer ans Ende, Stichschluss nach Quelle. CSV soll exakt das
        // wiedergeben, was die Forscherin am Bildschirm sieht.
        result.hits.sort((a, b) => {
            const da = (a.ev.d || '').trim(), db = (b.ev.d || '').trim();
            if (!da && !db) return a.ev.f.localeCompare(b.ev.f);
            if (!da) return 1;
            if (!db) return -1;
            return da < db ? -1 : da > db ? 1 : a.ev.f.localeCompare(b.ev.f);
        });
        const headers = ['Datum', 'Quelle', 'Korpus'];
        for (let i = 1; i <= result.cards.length; i++) headers.push('Person ' + i);
        headers.push('Rechtsgeschäft');
        const lines = [headers.map(csvEscape).join(';')];
        for (const h of result.hits) {
            const row = [
                h.ev.d || '',
                h.ev.f || '',
                h.ev.c || '',
                ...h.persons.map(p => p.n || p.p || ''),
                h.ev.tx || ''
            ];
            lines.push(row.map(csvEscape).join(';'));
        }
        // BOM für Excel-Kompatibilitaet
        const blob = new Blob(['﻿' + lines.join('\n')],
            { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const today = new Date().toISOString().slice(0, 10);
        a.download = 'abfrage_' + today + '.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
    }

    csvBtn.addEventListener('click', () => {
        if (!csvBtn.hasAttribute('disabled')) downloadCsv();
    });

    /* ---------- Onboarding: Beispiel-Abfragen --------------------------- */
    const EXAMPLES = {
        'women-issuers': [
            { role: 'issuer', sex: 'f', occ: '' }
        ],
        'women-issuers-men-recipients': [
            { role: 'issuer',    sex: 'f', occ: '' },
            { role: 'recipient', sex: 'm', occ: '' }
        ],
        'burger-recipients': [
            { role: 'recipient', sex: '', occ: 'urger' }
        ],
        'clergy-pair': [
            { role: 'issuer',    sex: '', occ: 'pfarr' },
            { role: 'recipient', sex: '', occ: 'pfarr' }
        ]
    };

    function applyExample(key) {
        const tpl = EXAMPLES[key];
        if (!tpl) return;
        state.persons = tpl.map(p => ({ role: p.role, sex: p.sex, occ: p.occ }));
        renderPersonsTable();
        sync();
        // Scroll zur Personen-Tabelle, damit Forscherin sieht, was gesetzt wurde.
        personsTable.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    root.querySelectorAll('.qb-example').forEach(btn => {
        btn.addEventListener('click', () => applyExample(btn.dataset.example));
    });

    /* ---------- Sync-Loop ----------------------------------------------- */
    function sync() {
        writeUrl();
        renderActiveFilters();
        loadData().then(() => {
            renderHits(compute());
        }).catch(() => {/* loadData hat schon Fehlertext gesetzt */});
    }

    /* ---------- Boot ---------------------------------------------------- */
    readUrl();
    renderPersonsTable();
    updateRangeLabels();
    // Daten erst beim ersten Sync laden — Initial-Render zeigt leere Tabelle.
    if (state.persons.length || state.corpora.size ||
        state.yearMin !== RELEASED_MIN || state.yearMax !== RELEASED_MAX ||
        state.scope !== 'event') {
        sync();
    } else {
        // Kein State aus URL: nur den UI-State darstellen, keine Daten laden.
        renderActiveFilters();
        renderHits({ hits: [], cards: [] });
    }

})();
