// Hydrates static "+" basket placeholders on detail pages.
// The server renders a <span class="toolbar-basket-mount" data-basket-...>
// per detail page (sources, persons, orgs). On load we read the dataset,
// build the proper basket button via DataBasket.buttonHTML, and replace
// the placeholder. Click handling stays in basket.js via event delegation.
(function () {
    'use strict';
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
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hydrate);
    } else {
        hydrate();
    }
})();
