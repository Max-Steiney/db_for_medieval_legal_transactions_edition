/* ==========================================================================
   Stadt und Gemeinschaft Wien — analysis page
   Capability manifest

   Declarative description of which (subject, filter-set) tuples can be
   resolved via which pre-computed aggregation or which register filter.

   A capability is an entry with:
     filters:  array of filter IDs that must be set EXACTLY in state.filters
     files:    array of required data file names (relative to /data/)
     resolve:  function(filters, dataMap) -> {
                 count:          number,
                 drillDownIds?:  [file_keys],
                 drillDownLabel?: string,
                 caveats?:       [strings]
               }

   Capabilities are ordered per subject from SPECIFIC to GENERIC.
   pick() returns the first match.

   Public API:
     AnalysisCapabilities.pick(subject, filters)
     AnalysisCapabilities.isFilterCombinationAllowed(subject, filterIds)
     AnalysisCapabilities.listSubjects()
   ========================================================================== */

(function() {
    'use strict';

    /* -------- Helpers ---------------------------------------------------- */

    function setEqual(a, b) {
        if (a.length !== b.length) return false;
        let as = a.slice().sort(), bs = b.slice().sort();
        for (let i = 0; i < as.length; i++) if (as[i] !== bs[i]) return false;
        return true;
    }

    function activeKeys(filters) {
        return Object.keys(filters || {}).filter(function(k) {
            return filters[k] != null && filters[k] !== '';
        });
    }

    function categoryTypes(orgCategory, dataMap) {
        let cat = dataMap['categories.json'];
        if (!cat) return [];
        return (cat.categories && cat.categories[orgCategory]) || [];
    }

    function unionUnique(arrays) {
        let seen = {}, out = [];
        arrays.forEach(function(a) {
            (a || []).forEach(function(k) {
                if (!seen[k]) { seen[k] = true; out.push(k); }
            });
        });
        return out;
    }

    /* -------- Capabilities ---------------------------------------------- */

    let CAPS = {

        /* ============ PERSONS (mentions, not individuals) ============ */
        persons: [

            /* sex + role -> role_by_sex */
            {
                filters: ['sex', 'role'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    let role = f.role, sex = f.sex;
                    let pair = (ea.observations.role_by_sex || {})[role] || {};
                    let dd = (((ea.drill_down || {}).role_sex || {})[role] || {})[sex] || [];
                    return {
                        count: pair[sex] || 0,
                        drillDownIds: dd,
                        drillDownLabel: 'Nennungen ' + sex + ' in der Rolle ' + role
                    };
                }
            },

            /* sex + org_type -> org_type_by_sex */
            {
                filters: ['sex', 'org_type'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    let pair = (ea.observations.org_type_by_sex || {})[f.org_type] || {};
                    let dd = ((ea.drill_down || {}).org_type || {})[f.org_type] || [];
                    return {
                        count: pair[f.sex] || 0,
                        drillDownIds: dd,
                        drillDownLabel: 'Personen-Nennungen mit Orgs vom Typ ' + f.org_type,
                        caveats: ['Drill-Down faengt alle Quellen mit dieser Org-Typ-Beteiligung; Geschlecht-Filter wirkt nur auf die Zaehlung.']
                    };
                }
            },

            /* sex + qw -> register */
            {
                filters: ['sex', 'qw'],
                files: ['persons_search.json'],
                resolve: function(f, d) {
                    let arr = d['persons_search.json'] || [];
                    let qw = parseInt(f.qw, 10), c = 0;
                    for (let i = 0; i < arr.length; i++) {
                        if (arr[i].qw === qw && arr[i].sex === f.sex) c++;
                    }
                    return { count: c };
                }
            },

            /* role -> sum over sex */
            {
                filters: ['role'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    let pair = (ea.observations.role_by_sex || {})[f.role] || {};
                    let dds = ((ea.drill_down || {}).role_sex || {})[f.role] || {};
                    return {
                        count: (pair.m || 0) + (pair.f || 0),
                        drillDownIds: (dds.m || []).concat(dds.f || []),
                        drillDownLabel: 'Nennungen in der Rolle ' + f.role
                    };
                }
            },

            /* org_type -> org_type_totals */
            {
                filters: ['org_type'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    return {
                        count: (ea.observations.org_type_totals || {})[f.org_type] || 0,
                        drillDownIds: ((ea.drill_down || {}).org_type || {})[f.org_type] || [],
                        drillDownLabel: 'Quellen mit Orgs vom Typ ' + f.org_type
                    };
                }
            },

            /* org_category -> sum over associated org_types */
            {
                filters: ['org_category'],
                files: ['roles.json', 'categories.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    let types = categoryTypes(f.org_category, d);
                    let totals = ea.observations.org_type_totals || {};
                    let dds = (ea.drill_down || {}).org_type || {};
                    let sum = 0, ddArrays = [];
                    types.forEach(function(t) {
                        sum += totals[t] || 0;
                        ddArrays.push(dds[t] || []);
                    });
                    return {
                        count: sum,
                        drillDownIds: unionUnique(ddArrays),
                        drillDownLabel: 'Quellen mit ' + f.org_category + 'en Einrichtungen'
                    };
                }
            },

            /* sex -> coverage (individual persons) */
            {
                filters: ['sex'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    let ea = d['roles.json'];
                    return {
                        count: (ea.coverage.sex_distribution || {})[f.sex] || 0,
                        caveats: ['Hier zaehlen wir individuelle Personen, nicht Nennungen — auf der Subjekt-Ebene Personen entspricht das der Coverage-Zahl aus dem Personen-Register.']
                    };
                }
            },

            /* qw -> register */
            {
                filters: ['qw'],
                files: ['persons_search.json'],
                resolve: function(f, d) {
                    let arr = d['persons_search.json'] || [];
                    let qw = parseInt(f.qw, 10), c = 0;
                    for (let i = 0; i < arr.length; i++) if (arr[i].qw === qw) c++;
                    return { count: c };
                }
            },

            /* empty -> person_count */
            {
                filters: [],
                files: ['roles.json'],
                resolve: function(f, d) {
                    return { count: d['roles.json'].coverage.person_count || 0 };
                }
            }
        ],

        /* ============ SOURCES ============ */
        sources: [

            /* korpus + decade */
            {
                filters: ['korpus', 'decade'],
                files: ['timeline.json'],
                resolve: function(f, d) {
                    let cell = ((d['timeline.json'].decades || {})[f.decade]) || {};
                    return { count: cell[f.korpus] || 0 };
                }
            },

            /* korpus */
            {
                filters: ['korpus'],
                files: ['timeline.json'],
                resolve: function(f, d) {
                    return {
                        count: ((d['timeline.json'].collections || {})[f.korpus] || {}).count || 0
                    };
                }
            },

            /* decade */
            {
                filters: ['decade'],
                files: ['timeline.json'],
                resolve: function(f, d) {
                    let cell = ((d['timeline.json'].decades || {})[f.decade]) || {};
                    return { count: cell.total || 0 };
                }
            },

            /* empty */
            {
                filters: [],
                files: ['timeline.json'],
                resolve: function(f, d) {
                    return { count: d['timeline.json'].total || 0 };
                }
            }
        ],

        /* ============ EVENTS (legal transactions) ============ */
        events: [

            /* tx_type */
            {
                filters: ['tx_type'],
                files: ['roles.json'],
                resolve: function(f, d) {
                    return {
                        count: (d['roles.json'].observations.transaction_types || {})[f.tx_type] || 0
                    };
                }
            },

            /* recipient_type */
            {
                filters: ['recipient_type'],
                files: ['transactions.json'],
                resolve: function(f, d) {
                    return {
                        count: (d['transactions.json'].observations.recipient_type_totals || {})[f.recipient_type] || 0,
                        caveats: ['Pipeline fuehrt keinen pro-recipient_type-Drill-Down — Quellen-Liste waere breiter (Org-Typ in beliebiger Rolle).']
                    };
                }
            },

            /* empty */
            {
                filters: [],
                files: ['roles.json'],
                resolve: function(f, d) {
                    return { count: d['roles.json'].coverage.total_events || 0 };
                }
            }
        ],

        /* ============ RELATIONSHIPS ============ */
        relationships: [

            /* rel_type + sex */
            {
                filters: ['rel_type', 'sex'],
                files: ['relations.json'],
                resolve: function(f, d) {
                    let eb = d['relations.json'];
                    let pair = ((eb.overview || {}).type_by_sex || {})[f.rel_type] || {};
                    let dd = (((eb.drill_down || {}).type_sex || {})[f.rel_type] || {})[f.sex] || [];
                    return {
                        count: pair[f.sex] || 0,
                        drillDownIds: dd,
                        drillDownLabel: 'Beziehungen ' + f.sex + ' vom Typ ' + f.rel_type
                    };
                }
            },

            /* rel_type */
            {
                filters: ['rel_type'],
                files: ['relations.json'],
                resolve: function(f, d) {
                    let c = ((d['relations.json'].coverage || {}).type_counts || {})[f.rel_type] || 0;
                    return { count: c };
                }
            },

            /* empty */
            {
                filters: [],
                files: ['relations.json'],
                resolve: function(f, d) {
                    return { count: (d['relations.json'].coverage || {}).total_relations || 0 };
                }
            }
        ]
    };

    /* -------- Public API ------------------------------------------------- */

    function pick(subject, filters) {
        let list = CAPS[subject] || [];
        let active = activeKeys(filters);
        for (let i = 0; i < list.length; i++) {
            if (setEqual(active, list[i].filters)) return list[i];
        }
        return null;
    }

    function isFilterCombinationAllowed(subject, filterIds) {
        let list = CAPS[subject] || [];
        for (let i = 0; i < list.length; i++) {
            if (setEqual(filterIds, list[i].filters)) return true;
        }
        return false;
    }

    function listSubjects() { return Object.keys(CAPS); }

    window.AnalysisCapabilities = {
        pick: pick,
        isFilterCombinationAllowed: isFilterCombinationAllowed,
        listSubjects: listSubjects,
        _CAPS: CAPS
    };

})();
