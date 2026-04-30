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

- `build.py`, `__main__.py` — orchestrator and command-line entry point.
- `renderer.py` — recursive TEI-to-HTML conversion via dispatch table.
- `register.py` — person, organisation, and place register lookup from the
  sibling repo's `indices/*.xml`.
- `aggregator.py` — derives data for the visualisation perspectives (roles,
  transactions, networks, places) from the sibling repo's `pipeline/output/`.
- `status.py` — quality-strip data per document.
- `config.py` — paths. `DOCS_DIR` lives in this repo (output); `SOURCES_DIR`,
  `KNOWLEDGE_DIR`, `VALIDATION_REPORT_PATH` resolve into the sibling.
- `templates/` — Jinja2 templates for document, register, statistics, and
  exploration pages.
- `static/` — CSS, JavaScript, fonts, images.
- `content/` — Markdown content rendered into the site (notably
  `edition_guidelines.md`).
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
- [../knowledge/ui.md](../knowledge/ui.md) — UI components, templates, JavaScript modules.
- [../knowledge/design.md](../knowledge/design.md) — design system (tokens, colours, typography).
- [../knowledge/visualization.md](../knowledge/visualization.md) — visualisation perspectives and open questions.
- [content/edition_guidelines.md](content/edition_guidelines.md) — annotation model and editorial conventions (rendered into the site).
