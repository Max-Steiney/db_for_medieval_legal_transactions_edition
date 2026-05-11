/* ==========================================================================
   Knowledge basket — persistent collection of sources across sessions.
   localStorage-based; a flat array of items keyed by type+id.
   Nav badge updates via custom event 'basket-change'.

   The UI label "Wissenskorb" stays German throughout — this is content of
   the edition. Code-side symbols use the English term "basket" so the
   source is consistent with the rest of the codebase.
   ========================================================================== */

let KnowledgeBasket = (function () {
    'use strict';

    const KEY = 'sugw-basket-v1';
    const LEGACY_KEY = 'sugw-wissenskorb-v1';

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

    function read() {
        try {
            const raw = localStorage.getItem(KEY);
            if (!raw) return [];
            const arr = JSON.parse(raw);
            return Array.isArray(arr) ? arr : [];
        } catch (_) { return []; }
    }
    function write(items) {
        try {
            localStorage.setItem(KEY, JSON.stringify(items));
            window.dispatchEvent(new CustomEvent('basket-change', { detail: { count: items.length } }));
        } catch (_) {}
    }

    function itemKey(item) { return (item.type || 'source') + ':' + item.id; }

    function add(item) {
        if (!item || !item.id) return false;
        const items = read();
        const k = itemKey(item);
        if (items.some(x => itemKey(x) === k)) return false;
        items.push({
            type:  item.type || 'source',
            id:    item.id,
            label: item.label || item.id,
            url:   item.url   || '',
            date:  item.date  || '',
            coll:  item.coll  || '',
            regest: item.regest || '',
            addedAt: new Date().toISOString(),
        });
        write(items);
        return true;
    }
    function remove(type, id) {
        const items = read();
        const k = (type || 'source') + ':' + id;
        const filtered = items.filter(x => itemKey(x) !== k);
        if (filtered.length === items.length) return false;
        write(filtered);
        return true;
    }
    function toggle(item) {
        return has(item.type, item.id) ? remove(item.type, item.id) : add(item);
    }
    function has(type, id) {
        const k = (type || 'source') + ':' + id;
        return read().some(x => itemKey(x) === k);
    }
    function list() { return read(); }
    function count() { return read().length; }
    function clear() { write([]); }

    // Update nav badge. Called eagerly by core.js on page load, then
    // reacts to changes within the session.
    function updateBadge() {
        const badge = document.getElementById('nav-basket-count');
        if (!badge) return;
        const c = count();
        badge.textContent = c > 0 ? String(c) : '';
        badge.hidden = (c === 0);
    }

    // Markup helper: small "+"/check button that triggers the toggle.
    // Caller inserts it into markup; clicks are handled via document-level
    // event delegation in bindGlobalClicks().
    function buttonHTML(item) {
        const inBasket = has(item.type, item.id);
        const label = inBasket
            ? 'Aus Wissenskorb entfernen'
            : 'In Wissenskorb legen';
        const icon = inBasket ? '✓' : '+';
        const cls  = 'basket-btn' + (inBasket ? ' is-in' : '');
        const data = encodeURIComponent(JSON.stringify(item));
        return `<button type="button" class="${cls}"
            data-basket-item="${data}"
            aria-label="${label}" title="${label}">${icon}</button>`;
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
                // Visual toggle: class + icon, without a re-render.
                const inBasket = has(item.type, item.id);
                btn.classList.toggle('is-in', inBasket);
                btn.textContent = inBasket ? '✓' : '+';
                const lab = inBasket ? 'Aus Wissenskorb entfernen' : 'In Wissenskorb legen';
                btn.setAttribute('aria-label', lab);
                btn.setAttribute('title', lab);
            } catch (_) {}
        });
        window.addEventListener('basket-change', updateBadge);
        // Cross-tab sync: listen for localStorage changes from other tabs
        // and refresh the badge.
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
        add, remove, toggle, has, list, count, clear,
        updateBadge, buttonHTML,
    };
})();
