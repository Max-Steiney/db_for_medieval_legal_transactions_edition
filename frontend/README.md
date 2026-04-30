# frontend/ — Digital edition builder

A static-site generator that renders the TEI-XML sources into browsable, annotated HTML
pages and writes them to `docs/`. The output is mirrored to a separate publication
repository, from which GitHub Pages serves the public edition.

## Contents

- `build.py`, `__main__.py` — orchestrator and command-line entry point.
- `renderer.py` — recursive TEI-to-HTML conversion via dispatch table.
- `register.py` — person, organisation, and place register lookup from `indices/*.xml`.
- `aggregator.py` — derives data for the visualisation perspectives (roles,
  transactions, networks, places) from the pipeline output.
- `status.py` — quality-strip data per document.
- `config.py` — paths (imports from `pipeline.config`).
- `templates/` — Jinja2 templates for document, register, statistics, and exploration pages.
- `static/` — CSS, JavaScript, fonts, images.
- `content/` — Markdown content rendered into the edition (notably `edition_guidelines.md`).
- `tests/` — automated tests (renderer, build, register pages, statistics, exploration).

## Conventions

- **Output:** all generated HTML, CSS, and JS go to `docs/`. The publication repository
  consumes that folder unchanged.
- **No server-side runtime:** the edition runs as a pure static client application; no
  database, no backend.
- **Source of truth:** all visualisation data is derived from `pipeline/output/`; the
  edition does not duplicate the pipeline's extraction logic.

## Usage

```bash
python -m frontend build                                 # build all pages into docs/
python -m frontend build --single sources/QGW/.../X.xml  # build a single source file
python -m pytest frontend/tests/                         # run edition tests
```

## See also

- [knowledge/architecture.md](../knowledge/architecture.md) — build system in the wider pipeline architecture.
- [knowledge/ui.md](../knowledge/ui.md) — UI components, templates, JavaScript modules.
- [knowledge/design.md](../knowledge/design.md) — design system (tokens, colours, typography).
- [knowledge/visualization.md](../knowledge/visualization.md) — visualisation perspectives and open questions.
- [frontend/content/edition_guidelines.md](content/edition_guidelines.md) — annotation model and editorial conventions (rendered into the edition).
