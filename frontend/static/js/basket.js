/* ==========================================================================
   Data basket, persistent collection of sources, persons, and organisations
   across sessions. localStorage-based; a flat array of items keyed by the
   compound key "<type>:<id>". Nav badge updates via custom event
   'basket-change'.

   Allowed types: 'source' | 'person' | 'org'.
   Entries lacking a type field are treated as 'source' (backwards-compat
   with the single-type basket that shipped first).

   Derived entries (Phase 2): adding a source pulls in its annotated
   persons / orgs as 'derived' entries via a per-source lookup
   (data/docs_entities.json). Derived entries carry the source idnos
   in their `src` array. A separate flag `gathered: true|false` keeps
   the user-collected entries distinct from purely derived ones.

       gathered === true   : explicitly added by the user via '+'
       gathered === false  : purely derived (src is non-empty)

   A manual '+' on a derived entry sets gathered=true (promotion). The
   entry then survives when its source(s) get removed.

   UI label is German ("Datenkorb"); code-side symbols use the English
   "basket" so the source stays consistent with the rest of the codebase.
   ========================================================================== */

let DataBasket = (function () {
    'use strict';

    const KEY = 'sugw-basket-v1';
    const LEGACY_KEY = 'sugw-wissenskorb-v1';
    const ALLOWED_TYPES = ['source', 'person', 'org'];
    // Path to docs_entities.json relative to ROOT_PATH. Loaded lazily on
    // the first source-add and cached on the window for the session.
    const ENTITIES_URL = 'data/docs_entities.json';

    // One-shot migration from the original key name. Reads any existing
    // value under the legacy key, copies it to the new key (if the new key
    // is still empty), and removes the legacy entry. Idempotent.
    function migrateLegacyKey() {
        try {
            const legacy = localStorage.getItem(LEGACY_KEY);
            if (legacy === null) return;
            if (localStorage.getItem(KEY) === null) {
                localStorage.setItem(KEY, legacy);
            }
            localStorage.removeItem(LEGACY_KEY);
        } catch (_) {}
    }

    function normType(t) {
        return ALLOWED_TYPES.indexOf(t) >= 0 ? t : 'source';
    }
    function key(type, id) {
        return normType(type) + ':' + id;
    }
    function sameItem(a, b) {
        return key(a.type, a.id) === key(b.type, b.id);
    }

    function read() {
        try {
            const raw = localStorage.getItem(KEY);
            if (!raw) return [];
            const arr = JSON.parse(raw);
            if (!Array.isArray(arr)) return [];
            // Migrate legacy items: assume source and gathered.
            return arr.map(x => Object.assign(
                { type: 'source', gathered: true, src: [] }, x
            ));
        } catch (_) { return []; }
    }
    function write(items) {
        try {
            localStorage.setItem(KEY, JSON.stringify(items));
            window.dispatchEvent(new CustomEvent('basket-change',
                { detail: { count: items.length } }));
        } catch (_) {}
    }

    // Build a normalised entry for storage. Unknown fields are dropped
    // per type so the CSV columns stay predictable.
    function normalise(item) {
        const type = normType(item.type);
        const base = {
            type:     type,
            id:       item.id,
            label:    item.label || item.id,
            url:      item.url   || '',
            gathered: item.gathered !== false,
            src:      Array.isArray(item.src) ? item.src.slice() : [],
        };
        if (type === 'source') {
            base.date   = item.date   || '';
            base.coll   = item.coll   || '';
            base.regest = item.regest || '';
        } else if (type === 'person') {
            base.sex        = item.sex        || '';
            base.active_min = item.active_min || '';
            base.active_max = item.active_max || '';
        } else if (type === 'org') {
            base.type_label = item.type_label || '';
        }
        return base;
    }

    function find(items, type, id) {
        const k = key(type, id);
        for (let i = 0; i < items.length; i++) {
            if (key(items[i].type, items[i].id) === k) return i;
        }
        return -1;
    }

    // Public add. For sources, also pulls in their annotated entities
    // as derived entries (async; uses cached lookup).
    function add(item) {
        if (!item || !item.id) return false;
        const items = read();
        const idx = find(items, item.type, item.id);
        if (idx >= 0) {
            // Promotion path: user explicitly added an entry that was
            // present (likely as derived). Mark as gathered.
            const cur = items[idx];
            if (!cur.gathered) {
                cur.gathered = true;
                write(items);
            }
            // If the user re-clicks '+' on an already-gathered source,
            // refresh derived links anyway (idempotent).
            if (normType(item.type) === 'source') attachDerived(item);
            return false;
        }
        const entry = normalise(item);
        entry.gathered = true; // direct add is always gathered
        items.push(entry);
        write(items);
        if (entry.type === 'source') attachDerived(entry);
        return true;
    }

    // Public remove. For sources, also detaches their derived entries.
    function remove(type, id) {
        const items = read();
        const idx = find(items, type, id);
        if (idx < 0) return false;
        items.splice(idx, 1);
        write(items);
        if (normType(type) === 'source') detachDerived(id);
        return true;
    }

    function toggle(item) {
        // Toggle uses gathered semantics: a derived-only entry must be
        // promotable via '+', not removable. So toggle 'removes' only if
        // the entry is gathered; otherwise it promotes.
        const items = read();
        const idx = find(items, item.type, item.id);
        if (idx >= 0 && items[idx].gathered) return remove(item.type, item.id);
        return add(item);
    }

    function has(type, id) {
        const items = read();
        return find(items, type, id) >= 0;
    }
    // isGathered: entry exists and is gathered (vs. purely derived).
    function isGathered(type, id) {
        const items = read();
        const idx = find(items, type, id);
        return idx >= 0 && items[idx].gathered === true;
    }
    function list(type) {
        const items = read();
        if (!type) return items;
        const t = normType(type);
        return items.filter(x => normType(x.type) === t);
    }
    function count(type) {
        return list(type).length;
    }
    // Gathered count per (optional) type.
    function countGathered(type) {
        return list(type).filter(x => x.gathered).length;
    }
    // Derived-only count per (optional) type.
    function countDerived(type) {
        return list(type).filter(x => !x.gathered).length;
    }
    function clear(type) {
        if (!type) { write([]); return; }
        const t = normType(type);
        write(read().filter(x => normType(x.type) !== t));
    }

    // -------------- Derived attach / detach --------------
    // The lookup is keyed by source idno: { "<idno>": { p: [...], o: [...] } }.
    let entitiesCache = null;
    let entitiesPromise = null;
    function loadEntities() {
        if (entitiesCache) return Promise.resolve(entitiesCache);
        if (entitiesPromise) return entitiesPromise;
        const root = (window.ROOT_PATH || '.');
        entitiesPromise = fetch(root + '/' + ENTITIES_URL)
            .then(r => r.ok ? r.json() : {})
            .then(d => { entitiesCache = d || {}; return entitiesCache; })
            .catch(() => { entitiesCache = {}; return entitiesCache; });
        return entitiesPromise;
    }

    // For a freshly-added source, fetch the lookup and add its annotated
    // persons / orgs as derived basket entries (gathered=false). If an
    // entry already exists (gathered or derived), only add the source id
    // to its `src` array.
    function attachDerived(sourceItem) {
        if (!sourceItem || normType(sourceItem.type) !== 'source') return;
        const srcId = sourceItem.id;
        loadEntities().then(map => {
            const bucket = map[srcId];
            if (!bucket) return;
            const items = read();
            let changed = false;
            (bucket.p || []).forEach(p => {
                changed = upsertDerived(items, 'person', {
                    id:         p.id,
                    label:      p.n || p.id,
                    url:        'register/persons/' + encodeURIComponent(p.id) + '.html',
                    sex:        p.sex || '',
                    active_min: p.am  || '',
                    active_max: p.ax  || '',
                }, srcId) || changed;
            });
            (bucket.o || []).forEach(o => {
                changed = upsertDerived(items, 'org', {
                    id:         o.id,
                    label:      o.n || o.id,
                    url:        'register/orgs/' + encodeURIComponent(o.id) + '.html',
                    type_label: o.tp || '',
                }, srcId) || changed;
            });
            if (changed) write(items);
        });
    }

    // Add a derived entry or register the source on an existing entry.
    // Returns true if items was mutated.
    function upsertDerived(items, type, base, srcId) {
        const idx = find(items, type, base.id);
        if (idx >= 0) {
            const cur = items[idx];
            if (cur.src.indexOf(srcId) === -1) {
                cur.src.push(srcId);
                return true;
            }
            return false;
        }
        const entry = normalise(Object.assign({}, base, {
            type:     type,
            gathered: false,
            src:      [srcId],
        }));
        items.push(entry);
        return true;
    }

    // When a source is removed, strip its id from every entry's src and
    // drop entries that have neither gathered nor any remaining source.
    function detachDerived(srcId) {
        const items = read();
        let changed = false;
        for (let i = items.length - 1; i >= 0; i--) {
            const it = items[i];
            if (!it.src || it.src.length === 0) continue;
            const pos = it.src.indexOf(srcId);
            if (pos === -1) continue;
            it.src.splice(pos, 1);
            changed = true;
            if (!it.gathered && it.src.length === 0) {
                items.splice(i, 1);
            }
        }
        if (changed) write(items);
    }

    // Update nav badge and the per-type breakdown tooltip on the nav-basket
    // anchor. Called eagerly by core.js on page load, then reacts to changes
    // within the session. The tooltip uses the shared [data-hint] hover
    // machinery from hint.js -- one short line, no popover.
    function updateBadge() {
        const badge = document.getElementById('nav-basket-count');
        const anchor = badge ? badge.closest('.nav-basket') : null;
        if (badge) {
            let html = '';
            ['source', 'person', 'org'].forEach(function (t) {
                const n = count(t);
                if (n > 0) {
                    html += '<span class="nav-basket-pill nav-basket-pill--' +
                        t + '">' + n + '</span>';
                }
            });
            badge.innerHTML = html;
            badge.hidden = (html === '');
        }
        if (anchor) {
            anchor.setAttribute('data-hint', breakdownText());
        }
    }

    // Build a compact, comma-separated breakdown whose per-type numbers match
    // the badge pills (totals per type), with the derived share as a suffix:
    //   "Datenkorb: 1 Quelle, 35 Personen, 7 Organisationen. Davon 41 abgeleitet."
    function breakdownText() {
        const tS = count('source');
        const tP = count('person');
        const tO = count('org');
        const dAll = countDerived();
        if (tS + tP + tO === 0) return 'Datenkorb ist leer';
        const parts = [];
        if (tS) parts.push(tS === 1 ? '1 Quelle'       : tS + ' Quellen');
        if (tP) parts.push(tP === 1 ? '1 Person'       : tP + ' Personen');
        if (tO) parts.push(tO === 1 ? '1 Organisation' : tO + ' Organisationen');
        let text = 'Datenkorb: ' + parts.join(', ');
        if (dAll) text += '. Davon ' + dAll + ' abgeleitet';
        return text;
    }

    // SVG glyphs. Same canvas (16x16), same stroke weight, so the three
    // states swap glyph cleanly without visual jump. Stroke uses
    // currentColor, so CSS can recolor per state (border + glyph in sync).
    const SVG_PLUS =
        '<svg class="basket-btn-icon" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path d="M8 4v8M4 8h8" stroke="currentColor" stroke-width="1.5" ' +
        'stroke-linecap="round" fill="none"/></svg>';
    const SVG_CHECK =
        '<svg class="basket-btn-icon" viewBox="0 0 16 16" aria-hidden="true">' +
        // "Check"-Pfad: ruhend sichtbar, beim Hover ueber CSS ausgeblendet.
        '<path class="glyph-check" d="M3.5 8.2l3 3l6-6" ' +
        'stroke="currentColor" stroke-width="1.6" ' +
        'stroke-linecap="round" stroke-linejoin="round" fill="none"/>' +
        // "Minus"-Pfad: ruhend versteckt, beim Hover ueber CSS sichtbar
        // (Vorschau auf "Klick entfernt").
        '<path class="glyph-minus" d="M4 8h8" stroke="currentColor" ' +
        'stroke-width="1.6" stroke-linecap="round" fill="none"/></svg>';
    const SVG_MINUS =
        '<svg class="basket-btn-icon" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path d="M4 8h8" stroke="currentColor" stroke-width="1.6" ' +
        'stroke-linecap="round" fill="none"/></svg>';
    const SVG_DASHED_PLUS =
        '<svg class="basket-btn-icon" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path d="M8 4v8M4 8h8" stroke="currentColor" stroke-width="1.5" ' +
        'stroke-linecap="round" stroke-dasharray="1.5 1.5" fill="none"/></svg>';

    // Visual state contract for the basket button. Three states share the
    // same outline circle, only the glyph (and the border color via CSS)
    // changes. The hover preview for is-in is handled in CSS via a
    // sibling glyph swapped through ::before on hover, so we do not need
    // to mutate the DOM on pointer move.
    function btnVisualState(present, gathered) {
        if (gathered) {
            return {
                cls:  'basket-btn is-in',
                icon: SVG_CHECK,
                lab:  'Aus Datenkorb entfernen',
                hint: 'Im Datenkorb. Klick entfernt den Eintrag.'
            };
        }
        if (present) {
            return {
                cls:  'basket-btn is-derived',
                icon: SVG_DASHED_PLUS,
                lab:  'In den Datenkorb uebernehmen',
                hint: 'Abgeleitet aus einer gesammelten Quelle. Klick uebernimmt den Eintrag als eigenstaendig gesammelt.'
            };
        }
        return {
            cls:  'basket-btn',
            icon: SVG_PLUS,
            lab:  'Zum Datenkorb hinzufuegen',
            hint: 'Eintrag in den Datenkorb aufnehmen.'
        };
    }

    // Markup helper. Returns the full <button>...</button> string ready to
    // drop into row templates.
    function buttonHTML(item) {
        const type = normType(item.type);
        const items = read();
        const idx = find(items, type, item.id);
        const present = idx >= 0;
        const gathered = present && items[idx].gathered;
        const v = btnVisualState(present, gathered);
        const payload = Object.assign({}, item, { type: type });
        const data = encodeURIComponent(JSON.stringify(payload));
        return `<button type="button" class="${v.cls}"
            data-basket-item="${data}"
            data-hint="${v.hint}"
            aria-label="${v.lab}">${v.icon}</button>`;
    }

    function bindGlobalClicks() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.basket-btn');
            if (!btn) return;
            e.preventDefault();
            e.stopPropagation();
            try {
                const item = JSON.parse(decodeURIComponent(btn.dataset.basketItem));
                toggle(item);
                // Refresh button visual state.
                const items = read();
                const idx = find(items, item.type, item.id);
                const present = idx >= 0;
                const gathered = present && items[idx].gathered;
                const v = btnVisualState(present, gathered);
                btn.className = v.cls;
                btn.innerHTML = v.icon;
                btn.setAttribute('aria-label', v.lab);
                btn.setAttribute('data-hint', v.hint);
                btn.removeAttribute('title');
            } catch (_) {}
        });
        window.addEventListener('basket-change', updateBadge);
        // Cross-tab sync.
        window.addEventListener('storage', (e) => {
            if (e.key === KEY) updateBadge();
        });
    }

    function init() {
        migrateLegacyKey();
        bindGlobalClicks();
        updateBadge();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    return {
        add, remove, toggle, has, isGathered,
        list, count, countGathered, countDerived,
        clear, updateBadge, buttonHTML,
    };
})();
