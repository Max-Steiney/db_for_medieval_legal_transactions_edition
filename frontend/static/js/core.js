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
       Active-Page-Markierung in der Top-Nav
       Markiert den passenden Top-Level-Eintrag anhand von
       location.pathname. Top-Level-Links direkt; Dropdown-Wrapper
       erhaelt `is-current`, wenn eine Sub-Seite die aktive ist.
       Rein clientseitig, damit der Build-Code unveraendert bleibt.
       ------------------------------------------------------------------ */

    function initNavActive() {
        let here = (window.location.pathname || '').replace(/\/+$/, '/index.html');
        if (here.endsWith('/')) here += 'index.html';

        let items = document.querySelectorAll('.nav-links .nav-item');
        items.forEach(function(item) {
            // Direkter Link
            if (item.tagName === 'A') {
                let href = item.getAttribute('href') || '';
                if (href && here.endsWith(normalizeNavHref(href))) {
                    item.setAttribute('aria-current', 'page');
                }
                return;
            }
            // Dropdown-Trigger: pruefe Sub-Links
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
        // Schneide Hash/Query, lasse Pfad enden auf .html / index.html
        let s = href.split('#')[0].split('?')[0];
        if (s.endsWith('/')) s += 'index.html';
        // root_path-Praefix (./, ../, ../../) abschneiden, sodass
        // endsWith() den Repo-relativen Pfad vergleicht.
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
       Search normalisation (V3 Diakritika)
       Transformiert Umlaute nach deutscher Konvention (ö <-> oe, ü <-> ue,
       ä <-> ae, ß <-> ss) und entfernt verbleibende kombinierende
       Diakritika via NFD. Dadurch findet eine Suche nach "Poetel" auch
       "Pötel", "Strauss" auch "Strauß", "Mueller" auch "Müller". Die
       Funktion wird sowohl beim Pre-Compute der Suchstrings als auch
       beim Tippen in der Suche verwendet — beide Seiten m&uuml;ssen
       identisch normalisiert sein, damit die Substring-Suche greift.
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

// CommonJS-Export fuer Vitest. Im Browser ist `module` undefiniert, der
// Block ist daher dort wirkungslos.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EdCore };
}
