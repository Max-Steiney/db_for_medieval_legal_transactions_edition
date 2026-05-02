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
       Initialise on every page
       ------------------------------------------------------------------ */

    document.addEventListener('DOMContentLoaded', function() {
        initNavDropdown();
        initNavHamburger();
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
