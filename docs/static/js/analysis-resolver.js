/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis/index.html
   Konstellations-Resolver

   Datenbank-Abfrage-UI ueber docs/data/role_constellation.json.

   - Anfangszustand: keine Personen-Box, leere Trefferliste.
   - Forscherin klickt "+ Person hinzufuegen": neue nummerierte Box mit
     Bedingungs-Slots (Rolle, Geschlecht, Beruf, Uhlirz-Klasse). Alle
     Slots sind optional, die leere Rolle bedeutet "beliebige Rolle".
   - Eine Box zaehlt als aktive Filter-Bedingung, sobald irgendein Slot
     gesetzt ist; mindestens eine aktive Box => Treffer werden gerechnet.
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
    const scopeChips = root.querySelectorAll('[data-filter="scope"] .qb-pill');
    const corpusChecksRoot = root.querySelector('#filter-corpora');
    const hitsSrc = root.querySelector('#hits-sources');
    const hitsEv  = root.querySelector('#hits-events');
    const tbody = root.querySelector('#hits-tbody');
    const emptyBox = root.querySelector('#hits-empty');
    const emptyMsg = root.querySelector('#hits-empty-msg');
    const csvBtn = root.querySelector('#csv-download');
    const activeStrip = root.querySelector('#active-filters');
    const resultsToolbar = root.querySelector('#results-toolbar');
    const hitsTable = root.querySelector('#hits-table');

    /* ---------- Daten ---------------------------------------------------- */
    let DATA = null;       // role_constellation.json
    let DOCS_LOOKUP = {};  // file_key -> {u, i, d, c, r} aus docs_lookup.json
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
        // role_constellation.json fuer die Trefferlogik, docs_lookup.json
        // fuer korrekte Quellen-URLs und sprechende Idnos. Beide parallel.
        const cstUrl = getDataUrl();
        const lookupUrl = (window.ROOT_PATH || '..') + '/data/docs_lookup.json';
        dataPromise = Promise.all([
            fetch(cstUrl).then(r => {
                if (!r.ok) throw new Error('HTTP ' + r.status); return r.json();
            }),
            fetch(lookupUrl).then(r => r.ok ? r.json() : {}).catch(() => ({})),
        ])
            .then(([json, lookup]) => { DATA = json; DOCS_LOOKUP = lookup || {}; return DATA; })
            .catch(err => {
                emptyMsg.textContent =
                    'Daten konnten nicht geladen werden (' + err.message + '). ' +
                    'Bitte Seite neu laden.';
                throw err;
            });
        return dataPromise;
    }

    // /analysis/ liegt eine Ebene tief; docs_lookup haelt root-relative URLs.
    function docUrl(fileKey) {
        const rec = DOCS_LOOKUP[fileKey];
        if (rec && rec.u) return '../' + rec.u;
        return '../documents/' + encodeURIComponent(fileKey) + '.html';
    }
    function docIdno(fileKey) {
        const rec = DOCS_LOOKUP[fileKey];
        return (rec && rec.i) || fileKey;
    }

    try {
        OCC_VOCAB = JSON.parse(personsTable.dataset.occupationVocab || '[]');
    } catch (_) { OCC_VOCAB = []; }
    let UHLIRZ_VOCAB = [];
    try {
        UHLIRZ_VOCAB = JSON.parse(personsTable.dataset.uhlirzVocab || '[]');
    } catch (_) { UHLIRZ_VOCAB = []; }

    /* ---------- Zustand -------------------------------------------------- */
    // State-Form:
    //   { persons: [ {role, sex, occ, uhlirz} ],
    //     scope: 'event'|'source',
    //     corpora: Set<string> }
    // uhlirz ist Default '' (= "alle"); ein gesetzter Wert filtert auf
    // genau diese Uhlirz-Kategorie, gematcht gegen die u-Liste der
    // Participants in role_constellation.json.
    // corpora: leeres Set bedeutet "alle Korpora" (kein Filter); ein
    // explizit befuelltes Set filtert auf die gewaehlten Korpora.
    // Defaults werden aus den Checkboxen gelesen (alle initial aktiv).
    const ALL_CORPORA = corpusChecksRoot
        ? Array.from(corpusChecksRoot.querySelectorAll('input[data-corpus]'))
            .map(cb => cb.dataset.corpus)
        : [];
    let state = {
        persons: [],
        scope: 'event',
        corpora: new Set(ALL_CORPORA)
    };

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

        // Spalte Rolle (optional; leer = beliebige Rolle)
        const roleTd = document.createElement('td');
        roleTd.className = 'qb-col-role';
        const roleSel = document.createElement('select');
        roleSel.className = 'qb-person-role';
        roleSel.setAttribute('aria-label', 'Rolle Person ' + (idx + 1));
        const blank = document.createElement('option');
        blank.value = '';
        blank.textContent = '— beliebige Rolle —';
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

        // Spalte Uhlirz-Berufsklasse (optional, exakter Match auf
        // Kategorie). Dropdown wird aus UHLIRZ_VOCAB gespeist; leerer
        // Default-Wert bedeutet "alle".
        const uhlirzTd = document.createElement('td');
        uhlirzTd.className = 'qb-col-uhlirz';
        const uhlirzSel = document.createElement('select');
        uhlirzSel.setAttribute('aria-label',
            'Uhlirz-Berufsklasse Person ' + (idx + 1));
        const uhlBlank = document.createElement('option');
        uhlBlank.value = '';
        uhlBlank.textContent = '— alle —';
        uhlirzSel.appendChild(uhlBlank);
        UHLIRZ_VOCAB.forEach(cat => {
            const o = document.createElement('option');
            o.value = cat;
            o.textContent = cat;
            if ((p.uhlirz || '') === cat) o.selected = true;
            uhlirzSel.appendChild(o);
        });
        uhlirzSel.addEventListener('change', () => {
            state.persons[idx].uhlirz = uhlirzSel.value;
            sync();
        });
        uhlirzTd.appendChild(uhlirzSel);
        tr.appendChild(uhlirzTd);

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
        state.persons.push({ role: '', sex: '', occ: '', uhlirz: '' });
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

    if (corpusChecksRoot) {
        corpusChecksRoot.querySelectorAll('input[data-corpus]').forEach(cb => {
            cb.addEventListener('change', () => {
                const key = cb.dataset.corpus;
                if (cb.checked) state.corpora.add(key);
                else state.corpora.delete(key);
                const label = cb.closest('label');
                if (label) label.classList.toggle('is-active', cb.checked);
                sync();
            });
        });
    }

    resetBtn.addEventListener('click', () => {
        state.persons = [];
        state.scope = 'event';
        state.corpora = new Set(ALL_CORPORA);
        scopeChips.forEach(c => {
            const isDefault = c.dataset.scope === 'event';
            c.classList.toggle('is-active', isDefault);
            c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
        });
        if (corpusChecksRoot) {
            corpusChecksRoot.querySelectorAll('input[data-corpus]')
                .forEach(cb => {
                    cb.checked = true;
                    const label = cb.closest('label');
                    if (label) label.classList.add('is-active');
                });
        }
        renderPersonsTable();
        sync();
    });

    /* ---------- Matching ------------------------------------------------ */
    function eventInCorpus(ev) {
        if (!state.corpora.size) return false;
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
        if (card.uhlirz) {
            const cats = person.u || [];
            if (cats.indexOf(card.uhlirz) === -1) return false;
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
        return state.persons.filter(p => p.role || p.sex || p.occ || p.uhlirz);
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
                if (!eventInCorpus(ev)) continue;
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
            if (!eventInCorpus(ev)) continue;
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
            emptyMsg.textContent = 'Person hinzufügen oder Beispiel wählen.';
            if (onboarding) onboarding.classList.remove('hidden');
            if (resultsToolbar) resultsToolbar.hidden = true;
            if (hitsTable) hitsTable.hidden = true;
            csvBtn.setAttribute('disabled', '');
            return;
        }
        if (!hits.length) {
            emptyBox.classList.remove('hidden');
            emptyMsg.textContent = 'Keine Treffer. Bedingung lockern oder Korpus erweitern.';
            if (onboarding) onboarding.classList.add('hidden');
            if (resultsToolbar) resultsToolbar.hidden = false;
            if (hitsTable) hitsTable.hidden = true;
            hitsSrc.textContent = '0';
            hitsEv.textContent = '0';
            csvBtn.setAttribute('disabled', '');
            return;
        }
        emptyBox.classList.add('hidden');
        if (onboarding) onboarding.classList.add('hidden');
        if (resultsToolbar) resultsToolbar.hidden = false;
        if (hitsTable) hitsTable.hidden = false;

        const sourceKeys = new Set();
        const eventKeys = new Set();
        for (const h of hits) {
            sourceKeys.add(h.ev.f);
            eventKeys.add(h.ev.e);
        }
        hitsSrc.textContent = fmt(sourceKeys.size);
        hitsEv.textContent  = fmt(eventKeys.size);
        csvBtn.removeAttribute('disabled');
        if (hits.length > 500) {
            csvBtn.setAttribute('title',
                'Tabelle zeigt 500 von ' + fmt(hits.length) + ' Treffern. ' +
                'CSV enthaelt alle.');
        } else {
            csvBtn.removeAttribute('title');
        }

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
        srcA.href = docUrl(ev.f);
        srcA.textContent = docIdno(ev.f);
        sourceTd.appendChild(srcA);
        tr.appendChild(sourceTd);

        td(tr, ev.c, 'col-corpus');

        // Beteiligte Personen als Pills, eine pro Bedingungs-Zeile. Pille
        // zeigt Nummer + Name + Rolle + Geschlecht, damit das Trefferbild
        // ohne Profil-Klick lesbar ist.
        const personsTd = document.createElement('td');
        personsTd.className = 'col-persons';
        hit.persons.forEach((p, idx) => {
            const pill = document.createElement('span');
            pill.className = 'person-pill';
            // Tooltip mit voller Stammdaten-Info: voller Name, ID, Note.
            // Hilft die Person zu identifizieren, wenn der angezeigte
            // Kurzname mehrdeutig waere (mehrere "Johann" in der Liste).
            const tipParts = [p.n || p.p];
            if (p.nt) tipParts.push(p.nt);
            tipParts.push('ID: ' + p.p);
            pill.title = tipParts.join('\n');
            const num = document.createElement('span');
            num.className = 'person-pill-num';
            num.textContent = idx + 1;
            const a = document.createElement('a');
            a.href = '../register/persons/' + encodeURIComponent(p.p) + '.html';
            a.textContent = p.n || p.p;
            pill.appendChild(num);
            pill.appendChild(a);
            // Rolle als kurze Pille hinter dem Namen (issuer -> Aussteller).
            const role = (p.r && ROLE_LABELS[p.r]) || '';
            if (role) {
                const r = document.createElement('span');
                r.className = 'person-pill-role';
                r.textContent = role;
                pill.appendChild(r);
            }
            // Geschlecht als kleines Suffix (m/f). 'u' und '' werden
            // weggelassen, damit nur tatsaechlich belegte Werte sichtbar
            // sind.
            if (p.s === 'm' || p.s === 'f') {
                const s = document.createElement('span');
                s.className = 'person-pill-sex person-pill-sex--' + p.s;
                s.textContent = p.s === 'f' ? 'weiblich' : 'maennlich';
                pill.appendChild(s);
            }
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
                label: docIdno(ev.f),
                url: docUrl(ev.f),
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
    // Korpus-Auswahl wird bewusst nicht dupliziert: die Checkboxen oben
    // sind die einzige Quelle der Wahrheit, ein zusaetzlicher "Korpus: …"-
    // Pill waere Redundanz.
    function renderActiveFilters() {
        if (!activeStrip || !window.VizCore) return;
        const pieces = [];
        if (state.scope !== 'event') {
            pieces.push({
                label: 'gemeinsam in: ' + (state.scope === 'source' ? 'Quelle' : 'Rechtsgeschäft'),
                onClear: () => {
                    state.scope = 'event';
                    scopeChips.forEach(c => {
                        const isDefault = c.dataset.scope === 'event';
                        c.classList.toggle('is-active', isDefault);
                        c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
                    });
                    sync();
                },
            });
        }
        window.VizCore.renderActiveFilters(activeStrip.id, pieces);
    }

    /* ---------- URL-State ----------------------------------------------- */
    function writeUrl() {
        const params = [];
        state.persons.forEach((p, idx) => {
            if (!p.role && !p.sex && !p.occ && !p.uhlirz) return;
            const parts = [];
            if (p.role)   parts.push('r=' + p.role);
            if (p.sex)    parts.push('s=' + p.sex);
            if (p.occ)    parts.push('o=' + encodeURIComponent(p.occ));
            if (p.uhlirz) parts.push('u=' + encodeURIComponent(p.uhlirz));
            params.push('p' + (idx + 1) + '=' + parts.join(','));
        });
        // Korpus-Auswahl nur dann serialisieren, wenn sie vom Default
        // (alle Korpora aktiv) abweicht. Default = leerer Parameter.
        if (state.corpora.size !== ALL_CORPORA.length) {
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
                    state.persons.push({ role: '', sex: '', occ: '', uhlirz: '' });
                }
                v.split(',').forEach(pair => {
                    const e = pair.indexOf('=');
                    if (e < 0) return;
                    const pk = pair.slice(0, e), pv = decodeURIComponent(pair.slice(e + 1));
                    if (pk === 'r') state.persons[idx].role = pv;
                    if (pk === 's') state.persons[idx].sex = pv;
                    if (pk === 'o') state.persons[idx].occ = pv;
                    if (pk === 'u') state.persons[idx].uhlirz = pv;
                });
            } else if (k === 'c') {
                // Explizite Korpus-Auswahl aus URL ueberschreibt den
                // All-Default. Checkboxen entsprechend synchronisieren.
                state.corpora.clear();
                v.split(',').map(decodeURIComponent).forEach(c => state.corpora.add(c));
                if (corpusChecksRoot) {
                    corpusChecksRoot.querySelectorAll('input[data-corpus]')
                        .forEach(cb => {
                            const on = state.corpora.has(cb.dataset.corpus);
                            cb.checked = on;
                            const label = cb.closest('label');
                            if (label) label.classList.toggle('is-active', on);
                        });
                }
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
                docIdno(h.ev.f),
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
        ],
        'verwaltung': [
            { role: 'issuer', sex: '', occ: '', uhlirz: 'XVIII Verwaltung' }
        ]
    };

    function applyExample(key) {
        const tpl = EXAMPLES[key];
        if (!tpl) return;
        state.persons = tpl.map(p => ({
            role: p.role, sex: p.sex, occ: p.occ, uhlirz: p.uhlirz || ''
        }));
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

    /* ---------- State-Reset auf URL-Hash --------------------------------- */
    // Setzt den gesamten Abfrage-Stand auf den Default zurueck und liest
    // dann den aktuellen URL-Hash ein. Wird beim initialen Boot und bei
    // jeder hashchange-Aenderung gerufen, damit Permalinks immer einen
    // sauberen Zustand erzeugen, statt Reste aus vorigen Hash-Zustaenden
    // mitzuschleppen.
    function resetStateFromUrl() {
        state.persons = [];
        state.scope = 'event';
        state.corpora = new Set(ALL_CORPORA);
        scopeChips.forEach(c => {
            const isDefault = c.dataset.scope === 'event';
            c.classList.toggle('is-active', isDefault);
            c.setAttribute('aria-pressed', isDefault ? 'true' : 'false');
        });
        if (corpusChecksRoot) {
            corpusChecksRoot.querySelectorAll('input[data-corpus]')
                .forEach(cb => {
                    cb.checked = true;
                    const label = cb.closest('label');
                    if (label) label.classList.add('is-active');
                });
        }
        readUrl();
        renderPersonsTable();
    }

    // Hat der Nutzer eine Abweichung vom Default-Zustand vorgenommen?
    // Default = keine Personen, scope=event, alle Korpora aktiv.
    function hasNonDefaultState() {
        return state.persons.length > 0 ||
               state.scope !== 'event' ||
               state.corpora.size !== ALL_CORPORA.length;
    }

    window.addEventListener('hashchange', () => {
        resetStateFromUrl();
        if (hasNonDefaultState()) {
            sync();
        } else {
            renderActiveFilters();
            renderHits({ hits: [], cards: [] });
        }
    });

    /* ---------- Boot ---------------------------------------------------- */
    readUrl();
    renderPersonsTable();
    // Daten erst beim ersten Sync laden — Initial-Render zeigt leere Tabelle.
    if (hasNonDefaultState()) {
        sync();
    } else {
        // Kein State aus URL: nur den UI-State darstellen, keine Daten laden.
        renderActiveFilters();
        renderHits({ hits: [], cards: [] });
    }

})();
