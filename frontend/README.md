# frontend/ — Static-site builder

A static-site generator that renders the TEI-XML sources from the sibling
pipeline repository into browsable, annotated HTML pages. Output is written
to `docs/` in this repository, from where GitHub Pages serves it.

## Cross-repo bootstrap

The TEI sources, registers, and CSV pipeline output live in the sibling
repository `db_for_medieval_legal_transactions`. Both repos must be cloned
side-by-side. `frontend/__init__.py` puts the sibling on `sys.path`, so
`from pipeline.config import …` resolves transparently — no install step,
no submodule.

```
parent/
  db_for_medieval_legal_transactions/         ← sources, registers, pipeline (CSVs)
  db_for_medieval_legal_transactions_edition/ ← this repo (frontend + docs/)
```

## Contents

- `build/` (package), `__main__.py` — orchestrator and command-line entry point.
- `renderer.py` — recursive TEI-to-HTML conversion via dispatch table.
- `register.py` — person, organisation, and place register lookup from the
  sibling repo's `indices/*.xml`.
- `aggregator/` (package) — derives the aggregate JSONs (roles, relations,
  transactions, role_constellation, timeline, per-source docs_aggregate) from
  the sibling repo's `pipeline/output/`.
- `status.py` — milestone + data-file overview for development context.
- `config.py` — paths. `DOCS_DIR` lives in this repo (output); `SOURCES_DIR`
  and `KNOWLEDGE_DIR` resolve into the sibling.
- `templates/` — Jinja2 templates for document, register, statistics, and
  exploration pages.
- `static/` — CSS, JavaScript, fonts, images.
- `content/` — Markdown content rendered into the site (about, impressum).
  The annotation guidelines themselves (`edition_guidelines.md`) live in
  the sibling pipeline repository's root, because they describe the
  source-data annotation model rather than publication content; the
  frontend renders them via `EDITION_GUIDELINES_PATH`.
- `tests/` — automated tests (renderer, build, register pages, statistics,
  exploration).

## Conventions

- **Output:** all generated HTML, CSS, and JS go to `docs/` in this repo.
  GitHub Pages serves them.
- **No server-side runtime:** pure static client application; no database,
  no backend.
- **Source of truth:** all visualisation data is derived from the sibling
  repo's `pipeline/output/`; the frontend does not duplicate the pipeline's
  extraction logic. CSVs must be regenerated there before rebuilding here.

## Usage

```bash
# Refresh CSVs in the sibling first, if TEI sources changed
cd ../db_for_medieval_legal_transactions
python -m pipeline transform

# Then build the site
cd ../db_for_medieval_legal_transactions_edition
python -m frontend build                                          # all pages → docs/
python -m frontend build --single ../db_for_medieval_legal_transactions/sources/QGW/.../X.xml  # one file
python -m pytest frontend/tests/                                  # frontend tests
```

## See also

- [../knowledge/architecture.md](../knowledge/architecture.md) — build system in the wider architecture.
- [../knowledge/ui-design.md](../knowledge/ui-design.md) — UI components, templates, JavaScript modules, design system (tokens, colours, typography).
- [../knowledge/data.md](../knowledge/data.md) — data model and aggregate JSONs.
- [../knowledge/analyse.md](../knowledge/analyse.md) and [../knowledge/exploration.md](../knowledge/exploration.md) — analysis and exploration perspectives.
- [../../db_for_medieval_legal_transactions/edition_guidelines.md](../../db_for_medieval_legal_transactions/edition_guidelines.md) — annotation model and editorial conventions (lives in the pipeline repo, rendered into the site by `_build_guidelines()`).
