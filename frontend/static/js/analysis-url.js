/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis/index.html
   URL-Serialisierung der Konstellations-Abfrage

   Pure-Logic-Modul: nimmt einen State-Snapshot entgegen und produziert
   einen Hash-String, bzw. parst einen Hash-String zurueck in einen
   State-Patch. Wird vom analysis-resolver.js verwendet (und in
   tests/js/analysis-url.test.js geprueft).

   State-Form:
     { persons: [{role, sex, occ, uhlirz}],
       orgs:    [{role, name, type}],
       scope:   'event'|'source',
       corpora: array<string> }

   URL-Form:
     pN=r=...,s=...,o=...,u=...   pro Personen-Bedingung
     gN=r=...,n=...,t=...         pro Org-Bedingung
     c=corpus1,corpus2            nur wenn != allCorpora
     scope=source                 nur wenn != 'event'
   ========================================================================== */

(function () {
    'use strict';

    function _personParts(p) {
        const parts = [];
        if (p.role)   parts.push('r=' + p.role);
        if (p.sex)    parts.push('s=' + p.sex);
        if (p.occ)    parts.push('o=' + encodeURIComponent(p.occ));
        if (p.uhlirz) parts.push('u=' + encodeURIComponent(p.uhlirz));
        return parts;
    }

    function _orgParts(o) {
        const parts = [];
        if (o.role) parts.push('r=' + o.role);
        if (o.name) parts.push('n=' + encodeURIComponent(o.name));
        if (o.type) parts.push('t=' + encodeURIComponent(o.type));
        return parts;
    }

    function _personActive(p) {
        return !!(p.role || p.sex || p.occ || p.uhlirz);
    }
    function _orgActive(o) {
        return !!(o.role || o.name || o.type);
    }

    /**
     * State -> Hash-String (ohne fuehrendes '#').
     * @param {object} state
     * @param {string[]} allCorpora full set of corpora — used as default,
     *   only deviations are serialized.
     */
    function serializeQueryState(state, allCorpora) {
        const params = [];
        (state.persons || []).forEach((p, idx) => {
            if (!_personActive(p)) return;
            params.push('p' + (idx + 1) + '=' + _personParts(p).join(','));
        });
        (state.orgs || []).forEach((o, idx) => {
            if (!_orgActive(o)) return;
            params.push('g' + (idx + 1) + '=' + _orgParts(o).join(','));
        });
        const corpora = state.corpora || [];
        const all = allCorpora || [];
        const corporaSet = new Set(corpora);
        const allSet = new Set(all);
        // Default ist "alle Korpora aktiv". Nur wenn die Auswahl davon
        // abweicht (kleiner oder anders), wird sie serialisiert.
        const isAllCorpora =
            corpora.length === all.length &&
            corpora.every(c => allSet.has(c));
        if (!isAllCorpora && corpora.length) {
            params.push('c=' + corpora.map(encodeURIComponent).join(','));
        }
        if (state.scope && state.scope !== 'event') {
            params.push('scope=' + state.scope);
        }
        return params.join('&');
    }

    /**
     * Hash-String (ohne fuehrendes '#') -> State-Patch.
     * Fehlende Slots werden NICHT vorbefuellt; der Aufrufer muss leere
     * Personen/Orgs-Cards selbst initialisieren (siehe defaultPerson/
     * defaultOrg).
     */
    function parseQueryHash(hash) {
        const state = {
            persons: [],
            orgs: [],
            scope: 'event',
            corpora: null,  // null = "nicht gesetzt, Default verwenden"
        };
        const raw = (hash || '').replace(/^#/, '');
        if (!raw) return state;
        const personRe = /^p(\d+)$/;
        const orgRe = /^g(\d+)$/;
        raw.split('&').forEach(seg => {
            const eq = seg.indexOf('=');
            if (eq < 0) return;
            const k = seg.slice(0, eq);
            const v = seg.slice(eq + 1);
            const m = personRe.exec(k);
            const mo = orgRe.exec(k);
            if (m) {
                const idx = parseInt(m[1], 10) - 1;
                if (idx < 0) return;
                while (state.persons.length <= idx) {
                    state.persons.push(defaultPerson());
                }
                v.split(',').forEach(pair => {
                    const e = pair.indexOf('=');
                    if (e < 0) return;
                    const pk = pair.slice(0, e);
                    const pv = decodeURIComponent(pair.slice(e + 1));
                    if (pk === 'r') state.persons[idx].role = pv;
                    else if (pk === 's') state.persons[idx].sex = pv;
                    else if (pk === 'o') state.persons[idx].occ = pv;
                    else if (pk === 'u') state.persons[idx].uhlirz = pv;
                });
            } else if (mo) {
                const idx = parseInt(mo[1], 10) - 1;
                if (idx < 0) return;
                while (state.orgs.length <= idx) {
                    state.orgs.push(defaultOrg());
                }
                v.split(',').forEach(pair => {
                    const e = pair.indexOf('=');
                    if (e < 0) return;
                    const pk = pair.slice(0, e);
                    const pv = decodeURIComponent(pair.slice(e + 1));
                    if (pk === 'r') state.orgs[idx].role = pv;
                    else if (pk === 'n') state.orgs[idx].name = pv;
                    else if (pk === 't') state.orgs[idx].type = pv;
                });
            } else if (k === 'c') {
                state.corpora = v.split(',').map(decodeURIComponent);
            } else if (k === 'scope') {
                state.scope = v === 'source' ? 'source' : 'event';
            }
        });
        return state;
    }

    function defaultPerson() {
        return { role: '', sex: '', occ: '', uhlirz: '' };
    }
    function defaultOrg() {
        return { role: '', name: '', type: '' };
    }

    const api = {
        serializeQueryState,
        parseQueryHash,
        defaultPerson,
        defaultOrg,
    };

    if (typeof window !== 'undefined') {
        window.AnalysisURL = api;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})();
