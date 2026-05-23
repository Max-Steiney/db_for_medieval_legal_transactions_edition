# Forschungsfragen-Verifikation

Stand: 2026-05-23

- Pipeline-Output: `C:\Users\Chrisi\Documents\GitHub\DHCraft\sugw\db_for_medieval_legal_transactions\pipeline\output`
- Indices: `C:\Users\Chrisi\Documents\GitHub\DHCraft\sugw\db_for_medieval_legal_transactions\indices`
- Norm-Listen: `C:\Users\Chrisi\Documents\GitHub\DHCraft\sugw\db_for_medieval_legal_transactions\normalisation_lists`

Diese Stufe rechnet vier Forschungsfragen direkt aus TEI/Indices/Pipeline-CSV neu. Vergleich gegen das Frontend-Output folgt in einer spaeteren Iteration.

## Ergebnisse

### uhlirz_iv_marriages

- category: `IV Erzeugung und Vertrieb von Leuchtstoffen Fetten und Oelen`
- persons_in_category: `21`
- marriage_pairs_in_category: `13`
- source_files_involved: `14`

### uhlirz_vi_ownership

- category: `VI Lederindustrie`
- persons_in_category: `105`
- persons_with_ownership: `2`
- ownership_places: `2`
- places_with_coordinates: `0`

### occ_st_stephan

- target_org: `org__wien-st_stephan`
- occ_records_main_only: `199`
- occ_records_including_suborgs: `274`
- distinct_persons: `156`
- persons_with_kin_relations: `28`
- kin_records_sum: `20`
- frontend_section_count: `113`
- frontend_row_count: `113`
- frontend_kin_sum: `11`
- status_persons: `known_gap`
- status_kin: `known_gap`
- status_section_vs_rows: `match`

### funding_st_agnes

- target_org: `org__wien-st_agnes_auf_der_himmelpforte`
- events_as_issuer: `10`
- events_as_recipient: `10`
- issuer_persons_for_recipient_events: `13`
- issuer_orgs_for_recipient_events: `1`
- recipient_persons_for_issuer_events: `14`
- recipient_orgs_for_issuer_events: `0`
