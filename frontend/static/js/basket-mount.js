// Hydrates static "+" basket placeholders on detail pages.
// The server renders a <span class="toolbar-basket-mount" data-basket-...>
// per detail page (sources, persons, orgs). On load we read the dataset,
// build the proper basket button via DataBasket.buttonHTML, and replace
// the placeholder. Click handling stays in basket.js via event delegation.
//
// Second path: the bulk mount on person / org profiles
// (<span class="basket-bulk-mount"> plus a JSON payload block, rendered by
// the sources_bulk_mount macro). It becomes a labelled button that adds
// every listed source at once via DataBasket.addMany.
(function () {
    'use strict';

    const BASKET_KEY = 'sugw-basket-v1';

    function fieldsFor(type, ds) {
        const base = {
            type: type,
            id:    ds.basketId    || '',
            label: ds.basketLabel || ds.basketId || '',
            url:   ds.basketUrl   || '',
        };
        if (type === 'source') {
            base.date   = ds.basketDate   || '';
            base.coll   = ds.basketColl   || '';
            base.regest = ds.basketRegest || '';
        } else if (type === 'person') {
            base.sex        = ds.basketSex        || '';
            base.active_min = ds.basketActiveMin  || '';
            base.active_max = ds.basketActiveMax  || '';
        } else if (type === 'org') {
            base.type_label = ds.basketTypeLabel  || '';
        }
        return base;
    }
    function hydrate() {
        if (typeof DataBasket === 'undefined') return;
        document.querySelectorAll('.toolbar-basket-mount').forEach(function (el) {
            const type = el.dataset.basketType || 'source';
            if (!el.dataset.basketId) return;
            const item = fieldsFor(type, el.dataset);
            const wrap = document.createElement('span');
            wrap.className = 'toolbar-basket';
            wrap.innerHTML = DataBasket.buttonHTML(item);
            el.replaceWith(wrap);
        });
    }
    // --- Bulk-Mount ----------------------------------------------------
    // Nur der Fertig-Zustand traegt eine Glyphe (Haekchen im Stil von
    // basket.js: 16x16-Canvas, currentColor). Im Normalzustand steht der
    // Knopf allein auf seinem Text-Label -- ein zusaetzliches Plus davor
    // wirkte neben dem ausgeschriebenen "in den Datenkorb" doppelt.
    const SVG_CHECK =
        '<svg class="basket-btn-icon" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path d="M3.5 8.2l3 3l6-6" stroke="currentColor" stroke-width="1.6" ' +
        'stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>';
    const HINT_OPEN = 'Alle gelisteten Quellen in den Datenkorb aufnehmen. ' +
        'Annotierte Personen und Organisationen werden als abgeleitete ' +
        'Eintraege mit uebernommen.';
    const HINT_DONE = 'Alle Quellen dieser Liste sind im Datenkorb.';

    // Payload liegt im Nachbar-Script des Mounts. Fehlerhaftes JSON laesst
    // den Knopf einfach ausfallen, die Seite bleibt bedienbar.
    function bulkPayload(el) {
        let node = el.nextElementSibling;
        if (!node || !node.classList.contains('basket-bulk-data')) {
            node = el.parentElement
                ? el.parentElement.querySelector('script.basket-bulk-data')
                : null;
        }
        if (!node) return null;
        try {
            const data = JSON.parse(node.textContent || '[]');
            if (!Array.isArray(data)) return null;
            return data.filter(function (d) { return d && d.id; })
                .map(function (d) {
                    return Object.assign({ type: 'source' }, d);
                });
        } catch (_) { return null; }
    }

    function bulkLabel(n, done) {
        const subject = n === 1 ? 'Quelle' : 'Alle ' + n + ' Quellen';
        return subject + (done ? ' im Datenkorb' : ' in den Datenkorb');
    }

    // Zustand haengt allein am Korb-Inhalt, nicht am Rueckgabewert von
    // addMany: Entfernen im Korb oder in einem anderen Tab muss den Knopf
    // wieder aktivieren.
    //
    // Genau EIN Korb-Read pro Repaint: isGathered() liest und parst bei
    // jedem Aufruf den kompletten localStorage-Eintrag, ein Aufruf pro
    // gelisteter Quelle waere also O(Quellen x Korbgroesse). Auf Profilen
    // mit vielen Quellen (org__wien: 1.330) blockiert das den Main-Thread,
    // und zwar genau im Fertig-Zustand, den der Knopf selbst herstellt.
    function paintBulk(btn, payload) {
        const gathered = new Set();
        DataBasket.list('source').forEach(function (x) {
            if (x.gathered === true) gathered.add(x.id);
        });
        const done = payload.every(function (d) {
            return gathered.has(d.id);
        });
        const label = bulkLabel(payload.length, done);
        btn.className = 'basket-bulk-btn' + (done ? ' is-in' : '');
        btn.disabled = done;
        btn.innerHTML = (done ? SVG_CHECK : '') +
            '<span class="basket-bulk-label"></span>';
        btn.querySelector('.basket-bulk-label').textContent = label;
        btn.setAttribute('data-hint', done ? HINT_DONE : HINT_OPEN);
    }

    function hydrateBulk() {
        if (typeof DataBasket === 'undefined') return;
        document.querySelectorAll('.basket-bulk-mount').forEach(function (el) {
            const payload = bulkPayload(el);
            if (!payload || !payload.length) return;
            const btn = document.createElement('button');
            btn.type = 'button';
            paintBulk(btn, payload);
            btn.addEventListener('click', function () {
                DataBasket.addMany(payload);
                paintBulk(btn, payload);
            });
            const repaint = function () { paintBulk(btn, payload); };
            window.addEventListener('basket-change', repaint);
            window.addEventListener('storage', function (e) {
                if (e.key === BASKET_KEY) repaint();
            });
            el.replaceWith(btn);
        });
    }

    function mountAll() {
        hydrate();
        hydrateBulk();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mountAll);
    } else {
        mountAll();
    }
})();
