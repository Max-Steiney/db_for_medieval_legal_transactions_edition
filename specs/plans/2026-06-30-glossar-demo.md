# Drei-Seiten-Glossar (Demo) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein durchklickbares, nativ aussehendes Demo-Modell des neuen Glossars aus drei verlinkten Seiten (Glossar / Technik / Tutorial), gebaut über das bestehende Frontend-Build-System, als Übergabe-Vorlage für ChPollin.

**Architecture:** Drei Markdown-Inhaltsquellen unter `frontend/content/project/glossar-demo/` werden von einer neuen Build-Funktion `_build_glossar_demo(env)` (in `frontend/build/_pages.py`) über das bestehende `_render_content_page`-Gerüst (Template `about.html`, `base.html`-Chrome) nach `docs/project/glossar-demo/*.html` gerendert. Lokal gebaut über ein Runner-Skript, das den `_MS_Test`-Pipeline-Fork auf `sys.path` legt. Keine neuen JS-Dateien (Aufklappbares via natives `<details>`), Styling über vorhandene CSS-Variablen plus minimaler Inline-`<style>`-Block.

**Tech Stack:** Python 3.12, Jinja2, Python-Markdown (Extensions: tables, fenced_code, codehilite, toc, attr_list), pytest. Build-Deps sind per `pip --user` installiert.

## Global Constraints

- **Produktives Glossar unberührt:** `frontend/content/project/glossar.md` und `docs/project/glossary.html` werden NICHT verändert. Die Demo lebt ausschließlich unter `glossar-demo/`.
- **`docs/` ist Build-Output:** Demo-Seiten nur über den Build / das Runner-Skript erzeugen, nie direkt editieren.
- **Keine Pushes; keine Datenschicht-/Pipeline-Änderung.** `_MS_Test` und KGruenwald-Ordner read-only.
- **Build-Pfad:** Lokaler Build über `scripts/build_glossar_demo.py`; Tests über `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest`. `frontend/__init__.py` bleibt unverändert.
- **Inhaltsquelle (Source of Truth):** `specs/material/glossar-entwurf.txt` (Glossar-/Fall-Texte) und `specs/material/glossar-entwurf-kommentare.txt` (Redaktions-Kommentare). Prosa von dort übernehmen, nicht neu erfinden.
- **Redaktionsvorgaben aus Kommentaren (verbindlich für die Darstellung):**
  - #22: In den Fallbeispielen NICHT generisch gendern — Rollen exakt wie im Original (z. B. „Ausstellerin" für Benedicta in Fall 2).
  - #13/#14: Zeug:in und Siegler:in GETRENNT beschreiben; der gemeinsame Code-Wert `witness` wird auf der Technik-Seite erklärt, nicht in der Prosa verschmolzen. Den Satz „Das Projekt hat sich dazu entschlossen Zeug*innen und Siegler*innen als Witness zusammenzuführen" NICHT übernehmen (Kommentar #14: Kardinalfehler).
  - #7: Beim Eintrag „Attribut" Verwandtschaft als Beispiel weglassen (gehört als `kin`-Relation auf die Technik-Seite); stattdessen z. B. Beruf/Titel/Geschlecht.
  - #6: „Event/Ereignis" auch als Entität benennen.
- **Begriff-/Label-Konsistenz:** Rollen-Codewerte sind genau `issuer`, `recipient`, `witness`, `other`. Nicht gesetzter Wert = leerer String, nicht `none`.
- **Keine technischen IDs im öffentlichen Sichttext** außer den TEI-Tags/Rollen-Codes, die hier bewusst Gegenstand der Technik-Seite sind (legitim, da in der herunterladbaren XML enthalten).
- **`.dev-only`-Redaktionsnotizen** an offenen Kommentar-Stellen sind erwünscht (Klasse `dev-only`, sichtbar nur unter `?dev=1`).

---

## File Structure

- `frontend/content/project/glossar-demo/glossar.md` — Glossar-Seite (Abschnitte A–F).
- `frontend/content/project/glossar-demo/technik.md` — Technik/Datenmodell-Seite (Abschnitt G).
- `frontend/content/project/glossar-demo/tutorial.md` — Tutorial mit drei Fallbeispielen (604/16/1869).
- `frontend/build/_pages.py` — neue Funktion `_build_glossar_demo(env)` (am Ende, nach `_build_glossary`).
- `frontend/build/__init__.py` — Import + Aufruf + `__all__`-Eintrag von `_build_glossar_demo`.
- `scripts/build_glossar_demo.py` — Runner: legt `_MS_Test` auf `sys.path`, baut nur die Demo.
- `frontend/tests/test_glossar_demo.py` — Regressionstests (nutzt `docs_dir`-Fixture + `_init_jinja`).

Konventionen:
- Output-Pfade: `DOCS_DIR / "project" / "glossar-demo" / "<name>.html"`.
- `root_path="../.."` (eine Ebene tiefer als die bestehende `glossary.html`).
- Fall-Links: `{{root_path}}/documents/QGW/Vienna_1177-1414_ready/<nr>.html`, in den Markdown-Quellen als `../../documents/QGW/Vienna_1177-1414_ready/<nr>.html`.
- Seiten-Cross-Links relativ innerhalb `glossar-demo/`: `glossar.html`, `technik.html`, `tutorial.html`.

---

## Task 1: Build-Plumbing + Runner (Smoke)

Erzeugt die drei Seiten aus (zunächst minimalen) Inhaltsquellen, verdrahtet die Build-Funktion und das Runner-Skript. Liefert die durchgängige, testbare Render-Kette.

**Files:**
- Create: `frontend/content/project/glossar-demo/glossar.md`
- Create: `frontend/content/project/glossar-demo/technik.md`
- Create: `frontend/content/project/glossar-demo/tutorial.md`
- Modify: `frontend/build/_pages.py` (neue Funktion am Dateiende)
- Modify: `frontend/build/__init__.py` (Import, Aufruf in `build()`, `__all__`)
- Create: `scripts/build_glossar_demo.py`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: `_render_content_page` (`frontend/build/_pages.py`), `_init_jinja` (`frontend/build/_helpers.py`, re-exportiert in `frontend.build`), `DOCS_DIR`, `CONTENT_DIR` (`frontend/config`).
- Produces: `_build_glossar_demo(env) -> None`, schreibt `DOCS_DIR/project/glossar-demo/{glossar,technik,tutorial}.html`.

- [ ] **Step 1: Minimale Inhaltsquellen anlegen**

`frontend/content/project/glossar-demo/glossar.md`:
```markdown
## Quelle

Eine einzelne historische Quelle, die in der Datenbank erfasst wurde.
```

`frontend/content/project/glossar-demo/technik.md`:
```markdown
## Rollen im Rechtsgeschäft

Kontrolliertes Vokabular: `issuer`, `recipient`, `witness`, `other`.
```

`frontend/content/project/glossar-demo/tutorial.md`:
```markdown
## Drei Fallbeispiele

Einstieg über drei konkrete Quellen.
```

- [ ] **Step 2: Failing test schreiben**

`frontend/tests/test_glossar_demo.py`:
```python
"""Tests for the three-page glossary demo build."""

import pytest

from frontend.build import _build_glossar_demo, _init_jinja


@pytest.fixture(scope="module")
def built_demo(docs_dir):
    env = _init_jinja()
    _build_glossar_demo(env)
    base = docs_dir / "project" / "glossar-demo"
    pages = {p: (base / f"{p}.html") for p in ("glossar", "technik", "tutorial")}
    contents = {}
    for name, path in pages.items():
        assert path.exists(), f"glossar-demo/{name}.html was not generated"
        contents[name] = path.read_text(encoding="utf-8")
    return contents


def test_all_three_pages_built(built_demo):
    assert set(built_demo) == {"glossar", "technik", "tutorial"}


def test_pages_have_native_chrome(built_demo):
    for name, content in built_demo.items():
        assert content.startswith("<!DOCTYPE html>"), name
        # base.html chrome marker: the project work name appears in header/footer
        assert "Stadt und Gemeinschaft Wien" in content, name
```

- [ ] **Step 3: Test ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: FAIL mit `ImportError: cannot import name '_build_glossar_demo'`.

- [ ] **Step 4: Build-Funktion implementieren**

Am Ende von `frontend/build/_pages.py` anfügen:
```python
def _build_glossar_demo(env):
    """Build the three-page glossary demo (Glossar/Technik/Tutorial).

    Isoliertes Demo-Modell zur Übergabe; nutzt dasselbe about.html-Gerüst
    wie die produktive Glossar-Seite, schreibt aber nach project/glossar-demo/
    und lässt die produktive glossary.html unberührt.
    """
    demo_dir = CONTENT_DIR / "project" / "glossar-demo"
    out_dir = DOCS_DIR / "project" / "glossar-demo"
    pages = [
        ("glossar", "Glossar (Demo)",
         "Begriffsdefinitionen des Projekts – Kern des Modells, speist die Tooltips."),
        ("technik", "Technik / Datenmodell (Demo)",
         "TEI-Auszeichnung, Rollen und roleName-Typen der Datenbank."),
        ("tutorial", "Tutorial (Demo)",
         "Einstieg in die Datenbank anhand dreier konkreter Quellen."),
    ]
    for name, title, subtitle in pages:
        md_path = demo_dir / f"{name}.md"
        if not md_path.exists():
            print(f"  WARN: {md_path} nicht gefunden, skip.", file=sys.stderr)
            continue
        _render_content_page(
            env,
            md_source=md_path.read_text(encoding="utf-8"),
            page_title=title,
            page_subtitle=subtitle,
            out_path=out_dir / f"{name}.html",
            root_path="../..",
        )
    print("  Glossar-Demo: project/glossar-demo/{glossar,technik,tutorial}.html")
```

- [ ] **Step 5: In den Build verdrahten**

In `frontend/build/__init__.py` im Import-Block aus `frontend.build._pages` `_build_glossary` um `_build_glossar_demo` ergänzen:
```python
    _build_about,
    _build_glossary,
    _build_glossar_demo,
```
Direkt nach der Zeile `_build_glossary(env)` (≈ Z. 247) einfügen:
```python
    _build_glossar_demo(env)
```
Im `__all__` (≈ Z. 301) `"_build_glossary",` um `"_build_glossar_demo",` ergänzen.

- [ ] **Step 6: Runner-Skript anlegen**

`scripts/build_glossar_demo.py`:
```python
"""Lokaler Demo-Build ohne Pipeline-CSVs.

Legt den _MS_Test-Pipeline-Fork (read-only) auf sys.path, damit
`from pipeline.config import ...` aufloest, und baut nur die drei
Glossar-Demo-Seiten. frontend/__init__.py bleibt unveraendert.

Aufruf:  python3 scripts/build_glossar_demo.py
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MS_TEST = _REPO.parent / "db_for_medieval_legal_transactions_MS_Test"
if not (_MS_TEST / "pipeline").is_dir():
    raise SystemExit(f"pipeline-Fork nicht gefunden unter {_MS_TEST}")
sys.path.insert(0, str(_MS_TEST))

from frontend.build import _build_glossar_demo, _init_jinja  # noqa: E402

env = _init_jinja()
_build_glossar_demo(env)
print("OK: docs/project/glossar-demo/ gebaut")
```

- [ ] **Step 7: Tests ausführen, Erfolg bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS (3 Tests).

- [ ] **Step 8: Runner verifizieren**

Run: `python3 scripts/build_glossar_demo.py && ls docs/project/glossar-demo/`
Expected: `OK: docs/project/glossar-demo/ gebaut` und drei HTML-Dateien.

- [ ] **Step 9: Commit**

```bash
git add frontend/content/project/glossar-demo frontend/build/_pages.py frontend/build/__init__.py scripts/build_glossar_demo.py frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Build-Geruest fuer Drei-Seiten-Glossar-Demo"
```

---

## Task 2: Glossar-Seite (Inhalt + Tooltip-Kopplung)

Die Kern-Seite: Begriffsdefinitionen aus Abschnitten A–F, Tooltip-Kopplungs-Callout, Seiten-Navigation, Redaktionsvorgaben.

**Files:**
- Modify: `frontend/content/project/glossar-demo/glossar.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: `_build_glossar_demo` aus Task 1.
- Produces: keine neuen Symbole (nur Inhalt).

- [ ] **Step 1: Failing tests ergänzen**

In `frontend/tests/test_glossar_demo.py` anfügen:
```python
def test_glossar_has_core_terms(built_demo):
    c = built_demo["glossar"]
    for term in ("Quelle", "Quellenkorpus", "Event", "Entit", "Rolle",
                 "Annotation", "Regest", "Rechtsgesch"):
        assert term in c, term


def test_glossar_event_is_named_entity(built_demo):
    # Kommentar #6: Ereignis auch als Entitaet benennen
    c = built_demo["glossar"].lower()
    assert "ereignis" in c and "entit" in c


def test_glossar_attribut_without_verwandtschaft(built_demo):
    # Kommentar #7: Verwandtschaft NICHT als Attribut-Beispiel
    c = built_demo["glossar"]
    block = c.split("Attribut", 1)[-1].split("</section>")[0] if "Attribut" in c else ""
    assert "Verwandtschaft" not in block[:600]


def test_glossar_has_tooltip_coupling_demo(built_demo):
    c = built_demo["glossar"]
    assert "tip-popover" in c  # Demonstration des echten Tooltip-Looks


def test_glossar_links_to_other_demo_pages(built_demo):
    c = built_demo["glossar"]
    assert "technik.html" in c and "tutorial.html" in c


def test_glossar_witness_and_sealer_separated(built_demo):
    # Kommentar #13/#14: Zeug:in und Siegler:in getrennt, nicht "zusammengefuehrt"
    c = built_demo["glossar"]
    assert "zusammenzuführen" not in c and "zusammenführen" not in c
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: FAIL (neue Tests, Terme/Marker fehlen noch).

- [ ] **Step 3: Glossar-Inhalt schreiben**

`frontend/content/project/glossar-demo/glossar.md` ersetzen. Prosa der Begriffe wörtlich aus `specs/material/glossar-entwurf.txt`, Abschnitte A (Datenbank/Datenmodell) und B (Quellen/Überlieferung) übernehmen; Redaktionsvorgaben #6/#7/#13/#14 beachten. Struktur:

```markdown
<nav class="demo-pagenav">
  <strong>Glossar</strong> ·
  <a href="tutorial.html">Tutorial</a> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

<style>
.demo-pagenav{font-size:.9rem;margin:0 0 1.5rem;padding:.6rem .8rem;background:var(--color-bg-warm,#f6f3ec);border-radius:6px}
.demo-tip-demo{border:1px solid var(--color-border,#d8d2c4);border-radius:8px;padding:1rem;margin:1.5rem 0;background:var(--color-bg-warm,#f6f3ec)}
.demo-tip-demo .tip-popover{position:static;display:block;max-width:340px;box-shadow:0 1px 4px rgba(0,0,0,.12)}
.demo-editnote{border-left:3px solid #e0a800;background:#fff8e1;padding:.5rem .8rem;margin:.6rem 0;font-size:.85rem}
.demo-xref{font-size:.85rem;color:var(--color-text-muted,#6b6356)}
</style>

Das Glossar ist der Kern dieses Modells: eine Begriffsdefinitionssammlung des
Projekts, die zugleich die Tooltips im UI speist. Anwendungsbezogene
Erklärungen finden sich im [Tutorial](tutorial.html) und auf der Seite
[Technik / Datenmodell](technik.html).

## Quelle

Eine einzelne historische Quelle, die in der Datenbank erfasst wurde. Im Projekt
„Stadt und Gemeinschaft" handelt es sich vor allem um Urkunden und
Stadtbucheinträge.

<div class="demo-tip-demo">
  <p class="demo-xref">So erscheint dieser Begriff als Tooltip im UI:</p>
  <aside class="tip-popover tip-popover--glossary" aria-hidden="false">
    <header class="tip-head"><h3 class="tip-title">Quelle</h3></header>
    <div class="tip-body">Eine einzelne historische Quelle, die in der Datenbank
    erfasst wurde.<a class="tip-link" href="glossar.html#quelle">im Glossar</a></div>
  </aside>
</div>

## Quellenkorpus

[... Text aus glossar-entwurf.txt, Abschnitt A ...]
```

Weiter mit: Quellenkorpus, Event/Ereignis (mit „… ist eine Entität …", #6), Factoid, Annotation, Entität, Rolle, Attribut (ohne Verwandtschaft, #7 — `<div class="demo-editnote dev-only">Redaktion offen (#7): Attribut-Beispiele final festlegen.</div>`), Verknüpfung, Beziehung, Register, Normierung; dann Abschnitt B: Urkunde, Regest, Edition, Digitalisat, Transkription, Siegel, Vidimus. Rollen (Aussteller:in, Empfänger:in, Zeug:in, Siegler:in …) hier nur kurz mit Querlink auf [Technik](technik.html#rollen); Zeug:in und Siegler:in als getrennte Einträge.

- [ ] **Step 4: Tests ausführen, Erfolg bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Sichtprüfung (Render)**

Run: `python3 scripts/build_glossar_demo.py`
Dann `docs/project/glossar-demo/glossar.html` im Browser öffnen und prüfen: native Chrome, Tooltip-Demo sichtbar, Querlinks vorhanden.

- [ ] **Step 6: Commit**

```bash
git add frontend/content/project/glossar-demo/glossar.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo/glossar.html
git commit -m "feat(glossar-demo): Glossar-Seite mit Begriffen und Tooltip-Kopplung"
```

---

## Task 3: Technik / Datenmodell-Seite

Abschnitt G aus dem `.docx`: Rollen-Codewerte, dispositive Verben, roleName-Typen, XML-Beispiele, witness-Zusammenfassung erklärt.

**Files:**
- Modify: `frontend/content/project/glossar-demo/technik.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: `_build_glossar_demo` aus Task 1.
- Produces: keine neuen Symbole.

- [ ] **Step 1: Failing tests ergänzen**

```python
def test_technik_has_role_codes(built_demo):
    c = built_demo["technik"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_technik_has_rolename_types(built_demo):
    c = built_demo["technik"]
    for t in ("prof", "title", "dead", "kin", "rep", "occ", "title_ref"):
        assert t in c, t


def test_technik_has_xml_snippet(built_demo):
    c = built_demo["technik"]
    assert "rs type=" in c and "role=" in c


def test_technik_explains_witness_grouping(built_demo):
    # #12/#13: witness fasst siegelnde Zeugen und Aussteller zusammen, Rollen aber getrennt beschrieben
    c = built_demo["technik"].lower()
    assert "witness" in c and "siegel" in c


def test_technik_links_back(built_demo):
    c = built_demo["technik"]
    assert "glossar.html" in c and "tutorial.html" in c
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k technik`
Expected: FAIL.

- [ ] **Step 3: Technik-Inhalt schreiben**

`frontend/content/project/glossar-demo/technik.md` aus `specs/material/glossar-entwurf.txt`, Abschnitt G. Struktur:

```markdown
<nav class="demo-pagenav">
  <a href="glossar.html">Glossar</a> ·
  <a href="tutorial.html">Tutorial</a> ·
  <strong>Technik / Datenmodell</strong>
</nav>

Diese Seite erklärt, wie die im [Glossar](glossar.html) definierten Begriffe in
den TEI-Quellen technisch ausgezeichnet sind. Die Tags erscheinen in der
herunterladbaren XML jeder Quelle. Beispiele aus den drei
[Fallbeispielen](tutorial.html).

## Rollen im Rechtsgeschäft {#rollen}

Auszeichnung als `<rs type="fn" role="…">`:

- **`issuer`** – Aussteller:in/Geber:in (verfügt oder erklärt).
- **`recipient`** – Empfänger:in/Adressat:in (erhält Recht, Gut, Geld).
- **`witness`** – Zeug:in und Siegler:in. *Hinweis:* Die beiden Funktionen
  werden inhaltlich getrennt beschrieben (siehe [Glossar](glossar.html)),
  im Auswertungsmodell aber gemeinsam als das Rechtsgeschäft beglaubigende
  Personen erfasst – siegelnde Aussteller:innen erscheinen dadurch in mehreren
  Rollen.
- **`other`** – weitere Beteiligte (z. B. Grundherr:in „mit Handen", Intervenient:in).

```xml
<rs type="fn" role="issuer">Hainreich der Santwerfer</rs>
```

## Dispositive Verben

`<triggerstring n="disp">` … [Liste aus Abschnitt G übernehmen]

## roleName-Typen

**Attribute** (`roleName` ohne Relation):
- `prof` – Beruf · `title` – Titel/Rang · `dead` – Todesfloskel/Status.

**Relationen** (`roleName` mit `corresp`):
- `kin` – Verwandtschaft · `rep` – rechtliche Vertretung · `occ` –
  Tätigkeitsbeziehung · `title_ref` – titulare Ortsbindung.
```

- [ ] **Step 4: Tests ausführen, Erfolg bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/content/project/glossar-demo/technik.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo/technik.html
git commit -m "feat(glossar-demo): Technik/Datenmodell-Seite (Abschnitt G)"
```

---

## Task 4: Tutorial-Seite (drei Fallbeispiele)

Geführter Einstieg über die drei konkreten Quellen 604/16/1869 mit Rollen-Auflösung im Kontext und Links in Glossar/Technik sowie auf die echten gerenderten Quellen.

**Files:**
- Modify: `frontend/content/project/glossar-demo/tutorial.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: `_build_glossar_demo` aus Task 1.
- Produces: keine neuen Symbole.

- [ ] **Step 1: Failing tests ergänzen**

```python
import re

CASE_DOCS = ("604", "16", "1869")


def test_tutorial_links_to_three_real_sources(built_demo, docs_dir):
    c = built_demo["tutorial"]
    base = "documents/QGW/Vienna_1177-1414_ready"
    for nr in CASE_DOCS:
        assert f"{base}/{nr}.html" in c, nr


def test_tutorial_case_sources_exist_in_repo():
    # Die drei Fall-Quellen muessen real gebaut vorliegen
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    for nr in CASE_DOCS:
        p = repo / "docs" / "documents" / "QGW" / "Vienna_1177-1414_ready" / f"{nr}.html"
        assert p.exists(), p


def test_tutorial_resolves_roles_in_context(built_demo):
    c = built_demo["tutorial"]
    for code in ("issuer", "recipient", "witness", "other"):
        assert code in c, code


def test_tutorial_links_into_glossar_and_technik(built_demo):
    c = built_demo["tutorial"]
    assert "glossar.html" in c and "technik.html" in c


def test_tutorial_case2_not_generically_gendered(built_demo):
    # Kommentar #22: in den Faellen exakte Rollen, kein generisches Gendern.
    # Fall 2 (Nr. 16) hat eine Ausstellerin (Singular feminin) -> "Ausstellerin".
    c = built_demo["tutorial"]
    seg = c.split("16.html", 1)[0][-1200:] + c.split("16.html", 1)[-1][:1200]
    assert "Ausstellerin" in seg
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k tutorial`
Expected: FAIL.

- [ ] **Step 3: Tutorial-Inhalt schreiben**

`frontend/content/project/glossar-demo/tutorial.md` aus `specs/material/glossar-entwurf.txt`, Abschnitt „Fallbeispiele" (Fall 1 Nr. 604, Fall 2 Nr. 16, Fall 3 Nr. 1869). Pro Fall eine Karte mit Quellentext-Auszug, Rollen-Auflösung im Kontext (mit Code in Klammern und Querlink auf [Technik](technik.html#rollen)) und Link auf die echte Quelle. #22: Rollen exakt wie im Original (Fall 2: „Ausstellerin", „Empfängerin"; Fall 1: „Aussteller:innen"/Ehepaar). Struktur:

```markdown
<nav class="demo-pagenav">
  <a href="glossar.html">Glossar</a> ·
  <strong>Tutorial</strong> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

<style>
.demo-case{border:1px solid var(--color-border,#d8d2c4);border-radius:8px;padding:1rem 1.2rem;margin:1.5rem 0;background:#fff}
.demo-case h3{margin-top:0}
.demo-case blockquote{font-style:italic;color:var(--color-text-muted,#5a5346);border-left:3px solid var(--color-border,#d8d2c4);margin:.6rem 0;padding-left:.8rem}
.demo-case .roles{margin:.6rem 0 0;padding-left:1.1rem}
</style>

So ist die Datenbank aufgebaut – erklärt an drei konkreten Quellen. Begriffe
sind im [Glossar](glossar.html) definiert, ihre technische Auszeichnung auf der
Seite [Technik / Datenmodell](technik.html).

<div class="demo-case">
  <h3>Fallbeispiel 1: Verkauf „mit Handen" der Stadt (Nr. 604)</h3>
  <blockquote>„Hainreich der Santwerfer und Elsbet, seine Hausfrau, verkaufen
  mit Handen … 1 lb dn. gelts purchrechts …"</blockquote>
  <ul class="roles">
    <li><strong>Aussteller:innen</strong> (<code>issuer</code>): das Ehepaar
    Hainreich der Santwerfer und seine Hausfrau Elsbet</li>
    <li><strong>Empfänger</strong> (<code>recipient</code>): Jans der Urbetsch</li>
    <li><strong>„mit Handen"</strong> (<code>other</code>): Bürgermeister Jans
    von Tirnach und der Rat der Stadt Wien</li>
    <li><strong>Zeuge/Siegler</strong> (<code>witness</code>): Ratsmitglied
    Leopold Polz</li>
  </ul>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/604.html">Quelle 604 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
</div>

[... Fall 2 (Nr. 16) und Fall 3 (Nr. 1869) analog aus glossar-entwurf.txt ...]
```

- [ ] **Step 4: Tests ausführen, Erfolg bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/content/project/glossar-demo/tutorial.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo/tutorial.html
git commit -m "feat(glossar-demo): Tutorial mit drei Fallbeispielen (604/16/1869)"
```

---

## Task 5: Quervernetzung & Abschluss-Integration

Gegenseitige Verlinkung absichern, Single-Source-Hinweis für die Tooltip-Kopplung verankern, vollständigen Testlauf.

**Files:**
- Modify: ggf. `frontend/content/project/glossar-demo/*.md` (fehlende Cross-Links ergänzen)
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: alle vorherigen Tasks.
- Produces: keine neuen Symbole.

- [ ] **Step 1: Integrations-Test ergänzen**

```python
def test_mutual_cross_links(built_demo):
    # jede Seite verlinkt die beiden anderen
    pairs = {
        "glossar": ("technik.html", "tutorial.html"),
        "technik": ("glossar.html", "tutorial.html"),
        "tutorial": ("glossar.html", "technik.html"),
    }
    for page, targets in pairs.items():
        for t in targets:
            assert t in built_demo[page], f"{page} -> {t}"


def test_glossary_demo_does_not_touch_production(docs_dir):
    # produktive glossary.html wird vom Demo-Build NICHT geschrieben
    assert not (docs_dir / "project" / "glossary.html").exists()
```

- [ ] **Step 2: Tests ausführen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: ggf. FAIL bei `test_mutual_cross_links`, falls ein Cross-Link fehlt.

- [ ] **Step 3: Fehlende Cross-Links ergänzen**

In der/den betroffenen `*.md` die fehlenden `demo-pagenav`-Links bzw. Inline-Verweise ergänzen, bis `test_mutual_cross_links` grün ist.

- [ ] **Step 4: Voller Demo-Testlauf + Build**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS (alle Tests).
Run: `python3 scripts/build_glossar_demo.py`
Expected: drei aktuelle HTML-Dateien.

- [ ] **Step 5: Regressions-Check Gesamt-Suite**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/ -q --tb=no --no-header`
Expected: keine NEUEN Fehlschläge gegenüber dem Stand vor Task 1 (vorbestehende, von fehlenden CSVs abhängige Fehlschläge ignorieren — vor Task 1 einmal als Baseline notieren).

- [ ] **Step 6: Commit**

```bash
git add frontend/content/project/glossar-demo frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Quervernetzung der drei Seiten + Integrationstests"
```

---

## Self-Review (ausgefüllt)

**Spec coverage:**
- Drei-Seiten-Modell (Glossar/Technik/Tutorial) → Tasks 1–4. ✓
- Glossar als Kern + Tooltip-Kopplung → Task 2 (Callout, Single-Source-Hinweis). ✓
- Drei Fallbeispiele 604/16/1869 → Task 4 (+ Existenz-Test). ✓
- Technik = Abschnitt G (Rollen, Verben, roleName) → Task 3. ✓
- Quervernetzung → Task 5. ✓
- Native Einbettung (base.html/CSS) → Task 1 (`_render_content_page`/about.html). ✓
- Tests im selben Commit (CLAUDE.md) → jede Task hat Test-Steps. ✓
- Build-Pfad gelöst (Runner + `_MS_Test`) → Task 1 Step 6. ✓
- Redaktionsvorgaben #6/#7/#13/#14/#22 → Tasks 2/3/4 mit gezielten Tests. ✓
- `.dev-only`-Redaktionsnotizen → Task 2 (demo-editnote dev-only). ✓
- FAQ als 4. Seite → Nicht-Ziel, bewusst nicht eingeplant. ✓

**Placeholder scan:** Build-Plumbing, Runner und alle Tests sind vollständiger Code. Die Prosa-Inhalte verweisen bewusst auf die als Datei vorliegende Source of Truth (`specs/material/glossar-entwurf.txt`) und geben Struktur + Pflicht-Elemente vor; das ist Transkription aus einer Datei, kein TBD.

**Type consistency:** Eine Funktion `_build_glossar_demo(env)`, durchgängig gleich benannt in `_pages.py`, `__init__.py`, Runner und Tests. Output-Pfade und `root_path="../.."` konsistent über alle Tasks.
