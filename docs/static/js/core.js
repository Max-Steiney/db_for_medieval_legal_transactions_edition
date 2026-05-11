/* ==========================================================================
   Wiener Urkundenbuch — Digital Edition
   Core: navigation, hamburger menu, esc() utility, build-time globals.
   ========================================================================== */

(function() {
    'use strict';
    // Build-time values reach the client via <body data-*> attributes
    // (no inline <script> needed -- compatible with strict CSP).
    let body = document.body;
    if (body) {
        if (body.dataset.rootPath !== undefined && window.ROOT_PATH === undefined) {
            window.ROOT_PATH = body.dataset.rootPath;
        }
        if (body.dataset.releasedMin && body.dataset.releasedMax && window.RELEASED_PERIOD === undefined) {
            window.RELEASED_PERIOD = {
                min: parseInt(body.dataset.releasedMin, 10),
                max: parseInt(body.dataset.releasedMax, 10)
            };
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
       Public API
       ------------------------------------------------------------------ */

    return {
        esc: esc,
        getParam: getParam,
        normForSearch: normForSearch
    };

})();

// CommonJS export for Vitest. `module` is undefined in the browser,
// so this block is a no-op there.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EdCore };
}
