# Glossar-Demo produktions-konform (Asset-Reuse + Slug-Normalisierung) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die bestehende Glossar-Demo an die Frontend-Asset-Muster angleichen (Styles in eine echte CSS-Datei + Demo-Template statt Inline-`<style>`) und die Begriffs-Slugs produktions-konform machen (kein Alias-Drift), damit ChPollins Übergang Demo → Frontend minimal wird.

**Architecture:** Die drei Demo-Seiten werden weiter über `_render_content_page` gerendert, aber mit einem neuen Mini-Template `glossar_demo.html`, das `about.html` erweitert und eine gemeinsame `frontend/static/css/glossar-demo.css` über den bestehenden `{% block head %}`-Slot einhängt (exakt wie `about.html` `content.css` einhängt). Die Inline-`<style>`-Blöcke wandern aus den `.md` in diese CSS-Datei; Rollen-Überschriften werden auf den sauberen kanonischen Term reduziert (Code-Alias in den Body).

**Tech Stack:** Python 3.12, Jinja2 (Template-Vererbung), Python-Markdown, pytest. Build-Deps sind per `pip --user` installiert.

## Global Constraints

- **Produktives Glossar unberührt:** `frontend/content/project/glossar.md` und `docs/project/glossary.html` werden NICHT verändert. Nur `glossar-demo/`, ein neues Demo-Template, eine neue CSS-Datei, der Runner und die Tests.
- **`docs/` ist Build-Output:** nur über Runner/Build erzeugen, nie direkt editieren.
- **Keine Pushes; keine Datenschicht-/Pipeline-Änderung.** Nur lokale Commits.
- **Build-Pfad:** Demo lokal bauen mit `python3 scripts/build_glossar_demo.py`; Voll-Build `python -m frontend build` läuft hier NICHT (kein pipeline/CSV). Tests mit `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest`.
- **Asset-Muster (verbindlich):** Quell-CSS liegt in `frontend/static/css/`; `_copy_static()` kopiert `frontend/static/` → `docs/static/`; Templates hängen CSS über `{% block head %}` mit `?v={{ asset_v }}` ein (`asset_v` ist Jinja-Global aus `frontend/build/_helpers.py:177`). `about.html` ist das Muster (`content.css` via block head).
- **Slug-Regel:** Anker kommen aus dem Überschriften-Text. Begriffs-Überschriften = sauberer kanonischer Term; Rollen-Code-Alias (`issuer` etc.) NICHT in die Überschrift (sonst Slug-Drift `ausstellerin-issuer` statt `ausstellerin`).
- **Rollen-Codewerte exakt:** `issuer`, `recipient`, `witness`, `other`.

---

## File Structure

- `frontend/static/css/glossar-demo.css` — neu: konsolidierte Demo-Styles (aus den drei Inline-`<style>`).
- `frontend/templates/glossar_demo.html` — neu: Mini-Template, erweitert `about.html`, hängt `glossar-demo.css` ein.
- `frontend/build/_pages.py` — `_build_glossar_demo` rendert mit `template_name="glossar_demo.html"`.
- `scripts/build_glossar_demo.py` — kopiert `glossar-demo.css` nach `docs/static/css/` (Runner ruft `_copy_static` nicht auf).
- `frontend/content/project/glossar-demo/{glossar,technik,tutorial}.md` — Inline-`<style>` entfernt; in `glossar.md` zusätzlich Rollen-Überschriften normalisiert.
- `frontend/tests/test_glossar_demo.py` — neue Tests (CSS-Link, keine Inline-Styles, saubere Rollen-Slugs).

---

## Task 1: Demo-Styles in Asset-Datei + Demo-Template (Asset-Reuse)

**Files:**
- Create: `frontend/static/css/glossar-demo.css`
- Create: `frontend/templates/glossar_demo.html`
- Modify: `frontend/build/_pages.py` (`_build_glossar_demo`, `template_name`)
- Modify: `scripts/build_glossar_demo.py` (CSS nach docs kopieren)
- Modify: `frontend/content/project/glossar-demo/glossar.md` (Inline-`<style>` entfernen)
- Modify: `frontend/content/project/glossar-demo/technik.md` (Inline-`<style>` entfernen)
- Modify: `frontend/content/project/glossar-demo/tutorial.md` (Inline-`<style>` entfernen)
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: `_render_content_page(..., template_name=...)`, `_build_glossar_demo(env)`, `_init_jinja`, `asset_v`-Global.
- Produces: gerenderte Seiten mit `<link ... static/css/glossar-demo.css?v=...>`, keine Inline-`<style>`.

- [ ] **Step 1: Failing tests ergänzen**

In `frontend/tests/test_glossar_demo.py` anfügen:
```python
def test_pages_link_demo_css(built_demo):
    for name, c in built_demo.items():
        assert "static/css/glossar-demo.css" in c, name


def test_md_sources_have_no_inline_style():
    from pathlib import Path
    base = Path(__file__).resolve().parents[1] / "content" / "project" / "glossar-demo"
    for name in ("glossar", "technik", "tutorial"):
        md = (base / f"{name}.md").read_text(encoding="utf-8")
        assert "<style>" not in md, name


def test_demo_css_asset_exists():
    from pathlib import Path
    css = Path(__file__).resolve().parents[1] / "static" / "css" / "glossar-demo.css"
    assert css.exists()
    body = css.read_text(encoding="utf-8")
    # Kern-Klassen der drei Seiten muessen abgedeckt sein
    for cls in (".demo-pagenav", ".demo-tip-demo", ".demo-case", ".demo-editnote",
                ".tech-codes", ".roleName-grid", ".dev-only"):
        assert cls in body, cls
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k "demo_css or inline_style or link_demo"`
Expected: FAIL (CSS-Datei/Link fehlen, Inline-Styles noch vorhanden).

- [ ] **Step 3: CSS-Asset anlegen**

`frontend/static/css/glossar-demo.css` (konsolidiert aus den drei Inline-Blöcken; nutzt vorhandene CSS-Variablen):
```css
/* Glossar-Demo — seiten-lokale Styles (Demo-Modell, isoliert).
   Wird ueber glossar_demo.html (block head) eingehaengt, analog content.css. */

.demo-pagenav {
    font-size: .9rem;
    margin: 0 0 1.5rem;
    padding: .6rem .8rem;
    background: var(--color-bg-warm, #f6f3ec);
    border: 1px solid var(--color-border, #d8d2c4);
    border-radius: 6px;
}
.demo-pagenav strong { color: var(--color-text-strong, #5a4a2f); }

/* Tooltip-Kopplungs-Demo (Glossar) */
.demo-tip-demo {
    border: 1px solid var(--color-border, #d8d2c4);
    border-radius: 8px;
    padding: 1rem;
    margin: 1.5rem 0;
    background: var(--color-bg-warm, #f6f3ec);
}
.demo-tip-demo .tip-popover {
    position: static; display: block; max-width: 340px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, .12);
    background: #fff; border: 1px solid #d8d2c4; border-radius: 6px; padding: 0;
}
.demo-tip-demo .tip-head {
    display: flex; justify-content: space-between; align-items: center;
    padding: .5rem .8rem; border-bottom: 1px solid #e7e2d6;
}
.demo-tip-demo .tip-title { margin: 0; font-size: 1rem; }
.demo-tip-demo .tip-body { padding: .6rem .8rem; font-size: .9rem; }
.demo-tip-demo .tip-link { display: inline-block; margin-top: .4rem; font-size: .85rem; }

/* Fallbeispiel-Karten (Tutorial) */
.demo-case {
    border: 1px solid var(--color-border, #d8d2c4);
    border-radius: 8px; padding: 1rem 1.2rem; margin: 1.5rem 0; background: #fff;
}
.demo-case h3 { margin-top: 0; }
.demo-case blockquote {
    font-style: italic; color: var(--color-text-muted, #5a5346);
    border-left: 3px solid var(--color-border, #d8d2c4);
    margin: .6rem 0; padding-left: .8rem;
}
.demo-case .roles { margin: .6rem 0 0; padding-left: 1.1rem; }
.demo-case .roles code { font-size: .92em; }
.demo-case .demo-xref { margin: .8rem 0 0; font-size: .95em; }

/* Technik-Seite */
.tech-codes { list-style: none; padding-left: 0; }
.tech-codes > li { margin: .4rem 0; }
.tech-codes code { background: #f0ede4; padding: .1rem .35rem; border-radius: 3px; }
.roleName-grid th, .roleName-grid td { vertical-align: top; }

/* Querverweis-Zeilen */
.demo-xref { font-size: .85rem; color: var(--color-text-muted, #6b6356); margin: 0 0 .5rem; }

/* Redaktionsnotizen: im oeffentlichen Build verborgen, per ?dev=1 sichtbar */
.demo-editnote { border-left: 3px solid #e0a800; background: #fff8e1; padding: .5rem .8rem; margin: .6rem 0; font-size: .85rem; }
.dev-only { display: none !important; }
.dev-mode .dev-only { display: block !important; border: 2px solid #e0b000; background: #fffbe6; padding: .5rem .75rem; margin: .75rem 0; border-radius: 4px; }
```

- [ ] **Step 4: Demo-Template anlegen**

`frontend/templates/glossar_demo.html`:
```html
{% extends "about.html" %}

{% block head %}
{{ super() }}
<link rel="stylesheet" href="{{ root_path }}/static/css/glossar-demo.css?v={{ asset_v }}">
{% endblock %}
```

- [ ] **Step 5: `_build_glossar_demo` auf das Template umstellen**

In `frontend/build/_pages.py` in `_build_glossar_demo` den `_render_content_page`-Aufruf um `template_name` ergänzen:
```python
        _render_content_page(
            env,
            md_source=md_path.read_text(encoding="utf-8"),
            page_title=title,
            page_subtitle=subtitle,
            out_path=out_dir / f"{name}.html",
            root_path="../..",
            template_name="glossar_demo.html",
        )
```

- [ ] **Step 6: Runner kopiert die Demo-CSS nach docs/**

In `scripts/build_glossar_demo.py` vor der Erfolgsmeldung ergänzen (der Runner ruft `_copy_static` nicht auf, daher gezielte Kopie):
```python
import shutil  # noqa: E402  (oben zu den Imports ziehen)

_css_src = _REPO / "frontend" / "static" / "css" / "glossar-demo.css"
_css_dst = _REPO / "docs" / "static" / "css" / "glossar-demo.css"
_css_dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(str(_css_src), str(_css_dst))
```

- [ ] **Step 7: Inline-`<style>` aus den drei `.md` entfernen**

In `frontend/content/project/glossar-demo/glossar.md`, `technik.md`, `tutorial.md` jeweils den kompletten Block von der Zeile `<style>` bis einschließlich `</style>` (direkt nach der `demo-pagenav`-`<nav>`) entfernen. Die `<nav class="demo-pagenav">` bleibt; nur der `<style>…</style>`-Block verschwindet.

- [ ] **Step 8: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS (alle bisherigen + neuen Tests).

- [ ] **Step 9: Sichtprüfung (optional, lokal)**

Run: `python3 scripts/build_glossar_demo.py && ls docs/static/css/glossar-demo.css`
Danach die drei Seiten über den lokalen Server ansehen (Formatierung muss unverändert wirken; Styles kommen jetzt aus der CSS-Datei).

- [ ] **Step 10: Commit**

```bash
git add frontend/static/css/glossar-demo.css frontend/templates/glossar_demo.html frontend/build/_pages.py scripts/build_glossar_demo.py frontend/content/project/glossar-demo frontend/tests/test_glossar_demo.py docs/project/glossar-demo docs/static/css/glossar-demo.css
git commit -m "refactor(glossar-demo): Styles in Asset-Datei + Demo-Template (Frontend-Muster)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Rollen-Überschriften slug-konform normalisieren

**Files:**
- Modify: `frontend/content/project/glossar-demo/glossar.md` (Rollen-Überschriften + Body)
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: Task 1 (gebaute Seiten, Tests grün).
- Produces: Rollen-Überschriften ohne Code-Alias; Codes im Body.

- [ ] **Step 1: Failing tests ergänzen**

In `frontend/tests/test_glossar_demo.py` anfügen:
```python
def test_glossar_role_headings_are_clean():
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project"
          / "glossar-demo" / "glossar.md").read_text(encoding="utf-8")
    for line in md.splitlines():
        if line.startswith("### "):
            for alias in ("(issuer)", "(recipient)", "(witness)", "(other)"):
                assert alias not in line, line


def test_glossar_role_codes_present_in_body(built_demo):
    c = built_demo["glossar"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_glossar_role_anchor_not_drifted(built_demo):
    # Der Anker der Aussteller:in-Ueberschrift darf den Code nicht enthalten
    c = built_demo["glossar"]
    assert 'id="ausstellerin-issuer"' not in c
    assert 'id="aussteller-in-issuer"' not in c
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k "role_headings or role_anchor"`
Expected: FAIL (Überschriften tragen aktuell `(issuer)` etc.).

- [ ] **Step 3: Rollen-Überschriften bereinigen, Alias in den Body**

In `frontend/content/project/glossar-demo/glossar.md` die fünf Rollen-Überschriften auf den sauberen Term reduzieren und den Code-Wert in den jeweiligen Absatz aufnehmen:

`### Aussteller:in (issuer)` → `### Aussteller:in` ; am Ende des Absatzes anfügen: ` Code-Wert im Datenmodell: \`issuer\`.`

`### Empfänger:in (recipient)` → `### Empfänger:in` ; anfügen: ` Code-Wert im Datenmodell: \`recipient\`.`

`### Zeug:in (witness)` → `### Zeug:in` ; anfügen: ` Code-Wert im Datenmodell: \`witness\`.`

`### Siegler:in (witness)` → `### Siegler:in` ; anfügen: ` Code-Wert im Datenmodell: \`witness\`.`

`### Grundherr:in („mit Handen", other)` → `### Grundherr:in` ; der Absatz nennt bereits „mit Handen" und die „Sammelrolle other" — sicherstellen, dass beides erhalten bleibt.

Die Einträge ohne Code-Alias (`### Einbringer:in`, `### Erblasser:in`, `### Testamentsvollstrecker:in`) bleiben unverändert.

- [ ] **Step 4: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS (alle Tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/content/project/glossar-demo/glossar.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "refactor(glossar-demo): Rollen-Ueberschriften slug-konform (Alias in den Body)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review (ausgefüllt)

**Spec coverage (Teil A der Spec):**
- „Chrome aus dem Content lösen" (Styles) → Task 1 (CSS-Asset + Template, Inline-`<style>` entfernt). ✓
- „auf so viele Frontend-Ressourcen wie möglich zurückgreifen" → Task 1 nutzt exakt das `about.html`/`block head`/`asset_v`/`_copy_static`-Muster. ✓
- „Slug-Stabilität / kein Alias-Drift" → Task 2 (saubere Rollen-Überschriften, Code im Body). ✓
- „Rollen-Codewerte exakt issuer/recipient/witness/other" → Task 2 Body + Tests. ✓
- „Produktion unberührt" → nur `glossar-demo/` + neue Demo-Dateien; Isolationstest `test_glossary_demo_does_not_touch_production` bleibt grün. ✓
- „Code+Test im selben Commit" → jede Task hat Test-Steps. ✓

**Placeholder scan:** CSS, Template, Build-/Runner-Edits und Tests sind vollständiger Code; die `.md`-Edits sind exakte, benannte Ersetzungen (kein TBD).

**Type consistency:** `template_name="glossar_demo.html"` konsistent zwischen `_pages.py` und der neuen Template-Datei; `glossar-demo.css`-Pfad konsistent in CSS-Datei, Template-`<link>`, Runner-Kopie und Tests.

**Hinweis (nicht Teil dieses Plans):** Teil B der Spec — das `.docx`-Import-Tooling (Extraktor, Coverage-/Slug-/Terminologie-Check, Routing-Config, Runbook) — bekommt einen eigenen Plan, erst relevant beim finalen `.docx`.
