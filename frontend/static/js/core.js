/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Core: navigation, hamburger menu, esc() utility, build-time globals.
   ========================================================================== */

(function() {
    'use strict';
    let body = document.body;
    if (body) {
        if (body.dataset.rootPath !== undefined && window.ROOT_PATH === undefined) {
            window.ROOT_PATH = body.dataset.rootPath;
        }
    }
})();

let EdCore = (function() {
    'use strict';

    /* ------------------------------------------------------------------
       HTML-escape utility (used by multiple modules)
       ------------------------------------------------------------------ */

    let esc = (function() {
        let d = document.createElement('div');
        return function(s) {
            if (s === undefined || s === null || s === '') return '';
            d.textContent = String(s);
            return d.innerHTML;
        };
    })();


    /* ------------------------------------------------------------------
       Navigation dropdown
       ------------------------------------------------------------------ */

    function closeAllDropdowns(dropdowns) {
        dropdowns.forEach(function(d) {
            d.classList.remove('open');
            let t = d.querySelector('.nav-dropdown-trigger');
            if (t) t.setAttribute('aria-expanded', 'false');
        });
    }

    function initNavDropdown() {
        let dropdowns = document.querySelectorAll('.nav-dropdown');
        dropdowns.forEach(function(dd) {
            let trigger = dd.querySelector('.nav-dropdown-trigger');
            if (!trigger) return;

            trigger.addEventListener('click', function(e) {
                e.stopPropagation();
                let isOpen = dd.classList.contains('open');
                closeAllDropdowns(dropdowns);
                if (!isOpen) {
                    dd.classList.add('open');
                    trigger.setAttribute('aria-expanded', 'true');
                }
            });
        });

        document.addEventListener('click', function() {
            closeAllDropdowns(dropdowns);
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAllDropdowns(dropdowns);
            }
        });
    }


    /* ------------------------------------------------------------------
       Hamburger menu (responsive nav)
       ------------------------------------------------------------------ */

    function initNavHamburger() {
        let btn = document.getElementById('nav-hamburger');
        let links = document.getElementById('nav-links');
        if (!btn || !links) return;

        btn.addEventListener('click', function() {
            let isOpen = links.classList.toggle('open');
            btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        document.addEventListener('click', function(e) {
            if (!btn.contains(e.target) && !links.contains(e.target)) {
                links.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
            }
        });

        // Escape closes the hamburger menu and returns focus to the trigger.
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && links.classList.contains('open')) {
                links.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
                btn.focus();
            }
        });
    }


    /* ------------------------------------------------------------------
       Active-page marker in the top nav. Pure client-side so the build
       output stays stateless. Top-level <a> gets aria-current="page";
       dropdown wrappers additionally get .is-current when one of their
       sub-links is active.
       ------------------------------------------------------------------ */

    function initNavActive() {
        let here = (window.location.pathname || '').replace(/\/+$/, '/index.html');
        if (here.endsWith('/')) here += 'index.html';

        let items = document.querySelectorAll('.nav-links .nav-item');
        items.forEach(function(item) {
            if (item.tagName === 'A') {
                let href = item.getAttribute('href') || '';
                if (href && here.endsWith(normalizeNavHref(href))) {
                    item.setAttribute('aria-current', 'page');
                }
                return;
            }
            let dd = item.closest('.nav-dropdown');
            if (!dd) return;
            let subs = dd.querySelectorAll('.nav-dropdown-menu a');
            for (let i = 0; i < subs.length; i++) {
                let h = subs[i].getAttribute('href') || '';
                if (h && here.endsWith(normalizeNavHref(h))) {
                    dd.classList.add('is-current');
                    subs[i].setAttribute('aria-current', 'page');
                    break;
                }
            }
        });
    }

    function normalizeNavHref(href) {
        // Strip hash/query, force trailing .html, and replace any
        // ./ or ../ prefix with /, so endsWith() compares repo-relative
        // paths regardless of the page's depth.
        let s = href.split('#')[0].split('?')[0];
        if (s.endsWith('/')) s += 'index.html';
        s = s.replace(/^(\.\.\/)+/, '/').replace(/^\.\//, '/');
        return s;
    }


    /* ------------------------------------------------------------------
       Initialise on every page
       ------------------------------------------------------------------ */

    document.addEventListener('DOMContentLoaded', function() {
        initNavDropdown();
        initNavHamburger();
        initNavActive();
    });


    /* ------------------------------------------------------------------
       URL parameter utility (E6 cross-epic navigation)
       ------------------------------------------------------------------ */

    function getParam(name) {
        try {
            return new URLSearchParams(window.location.search).get(name);
        } catch(e) {
            return null;
        }
    }


    /* ------------------------------------------------------------------
       Search normalisation: map German umlauts to their two-letter
       equivalents (ö <-> oe, ü <-> ue, ä <-> ae, ß <-> ss), then strip
       remaining combining diacritics via NFD. Used on both the pre-
       computed search strings and the live input; both sides MUST be
       normalised identically for substring matching to work, e.g.
       "Poetel" finds "Pötel", "Strauss" finds "Strauß".
       ------------------------------------------------------------------ */

    let COMBINING_MARKS_RE = new RegExp('[\\u0300-\\u036f]', 'g');

    function normForSearch(s) {
        if (s === undefined || s === null) return '';
        return String(s)
            .replace(/Ä/g, 'Ae').replace(/ä/g, 'ae')
            .replace(/Ö/g, 'Oe').replace(/ö/g, 'oe')
            .replace(/Ü/g, 'Ue').replace(/ü/g, 'ue')
            .replace(/ß/g, 'ss')
            .normalize('NFD')
            .replace(COMBINING_MARKS_RE, '')
            .toLowerCase();
    }


    /* ------------------------------------------------------------------
       Word-AND match against an already-normalised haystack.

       Both arguments must be pre-normalised via normForSearch() — this
       keeps the hot path (one call per row per keystroke) free of
       string allocations. Whitespace-split, empty query returns true.
       ------------------------------------------------------------------ */

    function matchesQuery(haystack, normQuery) {
        if (!normQuery) return true;
        if (!haystack) return false;
        let words = normQuery.split(/\s+/);
        for (let i = 0; i < words.length; i++) {
            if (words[i] && haystack.indexOf(words[i]) === -1) return false;
        }
        return true;
    }


    /* ------------------------------------------------------------------
       Sort utilities (shared by index.js, profile.js, register.js)

       sortKey() normalises a value for lexicographic comparison:
       - strips square brackets (editorial markup like "[Wien]" sorts
         under W, not under [)
       - trims leading/trailing punctuation (",", ";", ":", whitespace);
         "Wien," sorts with "Wien", "St. Poelten" is left alone because
         its dot is internal
       - lowercases (defensive; localeCompare 'de' would handle case but
         we want a deterministic comparable form)

       compareValues() is the generic cell-vs-cell comparator:
       - empty values (undefined/null/""/"-") sort to the end
       - both values numeric -> numeric compare
       - otherwise -> sortKey + localeCompare('de')
       - dir = +1 ascending, -1 descending
       ------------------------------------------------------------------ */

    let NUM_RE = /^-?\d+(\.\d+)?$/;

    function sortKey(v) {
        return String(v == null ? '' : v)
            .replace(/[\[\]]/g, '')
            .replace(/^[\s,;:]+|[\s,;:]+$/g, '')
            .toLowerCase();
    }

    function isEmptyForSort(v) {
        return v === undefined || v === null || v === '' || v === '-';
    }

    function compareValues(a, b, dir) {
        dir = dir || 1;
        let aE = isEmptyForSort(a);
        let bE = isEmptyForSort(b);
        if (aE && bE) return 0;
        if (aE) return 1;
        if (bE) return -1;
        // Pure numbers on both sides -> numeric compare. typeof handles
        // the case where the caller already parsed them; strings that
        // happen to be all digits (like signature numbers) are matched
        // via NUM_RE.
        if (typeof a === 'number' && typeof b === 'number') {
            return (a - b) * dir;
        }
        let sa = String(a), sb = String(b);
        if (NUM_RE.test(sa) && NUM_RE.test(sb)) {
            return (Number(sa) - Number(sb)) * dir;
        }
        return sortKey(sa).localeCompare(sortKey(sb), 'de') * dir;
    }


    /* ------------------------------------------------------------------
       Public API
       ------------------------------------------------------------------ */

    return {
        esc: esc,
        getParam: getParam,
        normForSearch: normForSearch,
        matchesQuery: matchesQuery,
        sortKey: sortKey,
        compareValues: compareValues
    };

})();

// CommonJS export for Vitest. `module` is undefined in the browser,
// so this block is a no-op there.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EdCore };
}
