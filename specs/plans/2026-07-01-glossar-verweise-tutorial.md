# Glossar-Verweise/Referenzen + Tutorial-Didaktik — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die Glossar-Demo verweisfähig machen — einheitliche Referenz-Zeilen (Verwandt/Weiterführend/Literatur), interne Begriffs-Verlinkung und ein Tutorial, das die Datenlogik erklärt statt nur Fälle aufzulisten.

**Architecture:** Rein content-/CSS-getrieben. Referenz-Zeilen sind Markdown-Absätze mit `attr_list`-Klasse `.entry-refs` (gestylt in `glossar-demo.css`); interne Verweise nutzen die `[[#Begriff]]`-Wiki-Mechanik (rendert zu `#slug`-Ankern); externe Links/Literatur kommen aus dem `.docx`-Extrakt. Das Tutorial bekommt eine erklärende Einleitung und pro Fall eine „Was dieser Fall zeigt"-Rahmung.

**Tech Stack:** Markdown (Extensions attr_list, toc), Jinja2, pytest. Build-Deps per `pip --user` installiert.

## Global Constraints

- **Produktion unberührt:** nur `frontend/content/project/glossar-demo/*.md`, `frontend/static/css/glossar-demo.css`, `frontend/tests/test_glossar_demo.py`. NICHT `frontend/content/project/glossar.md` / `docs/project/glossary.html`.
- **`docs/` ist Build-Output:** nur via `python3 scripts/build_glossar_demo.py`. `python -m frontend build` läuft hier NICHT.
- **Tests:** `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`.
- **Keine Pushes; lokale Commits.**
- **Slug-Stabilität:** interne Links NUR auf saubere Ein-Token-Slugs (Wiki-Rewriter `_slug_anchor` und TOC-Slugify müssen übereinstimmen). Überschriften mit `/` oder Klammern erzeugen Drift → vorher normalisieren.
- **Referenz-Mechanik:** `.entry-refs`-Absatz = mehrere Zeilen mit hartem Zeilenumbruch (zwei Leerzeichen am Zeilenende), `{: .entry-refs }` in der LETZTEN Zeile hängt die Klasse an den ganzen Absatz. `[[#…]]`-Links stehen im Markdown-Text (nicht in rohem HTML), damit sie rendern.
- **Keine leeren Referenz-Zeilen:** nur vorhandene Verweise schreiben.

---

## File Structure

- `frontend/static/css/glossar-demo.css` — `.entry-refs`-Styling ergänzen.
- `frontend/content/project/glossar-demo/glossar.md` — Referenz-Zeilen + interne Erst-Erwähnungs-Links + Event-Überschrift normalisieren.
- `frontend/content/project/glossar-demo/tutorial.md` — Einleitung (Datenlogik) + „Was dieser Fall zeigt" pro Fall + Rückverweise.
- `frontend/tests/test_glossar_demo.py` — neue Tests.

Externe Quellen (aus `specs/material/glossar-entwurf.txt`), exakte URLs:
- ad fontes Urkunde: `https://www.adfontes.uzh.ch/tutorium/quellen-auswerten/urkunden-und-diplomatik/definition-urkunde/`
- ad fontes Regest: `https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/regesten/`
- ad fontes Edition: `https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/kritische-edition/`
- ad fontes Transkription: `https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/transkription/`
- ad fontes Siegel: `https://www.adfontes.uzh.ch/tutorium/handschriften-beschreiben/siegel/`
- Wien-Wiki QGW: `https://www.geschichtewiki.wien.gv.at/Quellen_zur_Geschichte_der_Stadt_Wien`
- Literatur Stadtbücher: `Brauneder/Jaritz (Hg.), Die Wiener Stadtbücher 1395–1430, Teil 1, FRA III/10 (Wien/Köln 1989)`
- Literatur Register: `Perger, Die Wiener Ratsbürger 1396–1526`

---

## Task 1: Referenz-Zeilen, interne Verlinkung, Event-Slug

**Files:**
- Modify: `frontend/static/css/glossar-demo.css` (`.entry-refs`)
- Modify: `frontend/content/project/glossar-demo/glossar.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: bestehende `_build_glossar_demo`-Pipeline, `attr_list`/Wiki-Link-Rendering.
- Produces: gerenderte Glossar-Seite mit `.entry-refs`-Absätzen, internen `#slug`-Links, externen `href`-Links.

- [ ] **Step 1: Failing tests ergänzen**

In `frontend/tests/test_glossar_demo.py` anfügen:
```python
def test_glossar_has_reference_lines(built_demo):
    c = built_demo["glossar"]
    assert 'class="entry-refs"' in c
    # Beschriftungen der Referenz-Zeilen
    assert "Weiterführend" in c
    assert "Literatur" in c
    assert "Verwandt" in c


def test_glossar_has_external_links(built_demo):
    c = built_demo["glossar"]
    assert "adfontes.uzh.ch" in c
    assert "geschichtewiki.wien.gv.at" in c


def test_glossar_internal_first_mention_links(built_demo):
    # Der Event-Eintrag verlinkt intern auf #quelle (Selbst-Verlinkung).
    c = built_demo["glossar"]
    assert 'href="#quelle"' in c


def test_glossar_event_heading_clean_slug(built_demo):
    # '### Event' -> id="event"; kein Slug-Drift durch '/ Ereignis'
    c = built_demo["glossar"]
    assert 'id="event"' in c
    assert 'id="event--ereignis"' not in c


def test_entry_refs_styled_in_css():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "css" / "glossar-demo.css").read_text(encoding="utf-8")
    assert ".entry-refs" in css
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k "reference or external_links or first_mention or event_heading or entry_refs"`
Expected: FAIL.

- [ ] **Step 3: `.entry-refs`-Styling in `glossar-demo.css` ergänzen**

Am Ende von `frontend/static/css/glossar-demo.css` anfügen:
```css
/* Referenz-Zeilen am Eintrags-Ende (Verwandt / Weiterführend / Literatur) */
.entry-refs {
    font-size: .85rem;
    line-height: 1.5;
    color: var(--color-text-muted, #6b6356);
    margin: .5rem 0 1.25rem;
    padding-left: .75rem;
    border-left: 2px solid var(--color-border, #d8d2c4);
}
.entry-refs strong { color: var(--color-text-strong, #5a4a2f); font-weight: 600; }
```

- [ ] **Step 4: Event-Überschrift normalisieren**

In `frontend/content/project/glossar-demo/glossar.md` die Überschrift `### Event / Ereignis` zu `### Event` ändern und „Ereignis" im Absatz führen (z. B. Absatzbeginn: „Ein Event (auch: Ereignis) ist die grundlegende Analyseeinheit …"). Der Test `test_glossar_event_is_named_entity` (prüft „ereignis" im Text) muss weiter grün bleiben — „Ereignis" also im Body behalten.

- [ ] **Step 5: Interne Erst-Erwähnungs-Links setzen**

In `glossar.md` die erste Erwähnung eines anderen Glossarbegriffs im jeweiligen Definitions-Absatz als `[[#Begriff]]` verlinken (nur saubere Ein-Token-Slugs):
- Event-Eintrag: „… einem in einer [[#Quelle]] dokumentierten Vorgang …"
- Quellenkorpus-Eintrag: „… um [[#Regest|Regesten]] aus den QGW …"
- Annotation-Eintrag: erste Nennung „[[#Regest|Regesten]]"
- Regest-Eintrag: „Inhaltsangabe einer [[#Quelle]]"
Nur die Erstnennung, nicht jede.

- [ ] **Step 6: Referenz-Zeilen an die Einträge anhängen**

Jeweils direkt nach dem Definitions-Absatz (vor der nächsten `###`-Überschrift bzw. vor einer `dev-only`-Notiz) einen `.entry-refs`-Block einfügen. Nur die vorhandenen Zeilen; Format (harter Umbruch = zwei Leerzeichen am Zeilenende, `{: .entry-refs }` in der Schlusszeile):

Quellenkorpus:
```markdown
**Verwandt:** [[#Quelle]]
**Weiterführend:** [Wien-Wiki: Quellen zur Geschichte der Stadt Wien](https://www.geschichtewiki.wien.gv.at/Quellen_zur_Geschichte_der_Stadt_Wien)
**Literatur:** Brauneder/Jaritz (Hg.), Die Wiener Stadtbücher 1395–1430, Teil 1, FRA III/10 (Wien/Köln 1989)
{: .entry-refs }
```

Urkunde:
```markdown
**Verwandt:** [[#Regest]] · [[#Siegel]]
**Weiterführend:** [ad fontes: „Urkunde"](https://www.adfontes.uzh.ch/tutorium/quellen-auswerten/urkunden-und-diplomatik/definition-urkunde/)
{: .entry-refs }
```

Regest:
```markdown
**Verwandt:** [[#Urkunde]] · [[#Quelle]]
**Weiterführend:** [ad fontes: „Regest"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/regesten/)
{: .entry-refs }
```

Edition:
```markdown
**Verwandt:** [[#Transkription]]
**Weiterführend:** [ad fontes: „kritische Edition"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/kritische-edition/)
{: .entry-refs }
```

Transkription:
```markdown
**Weiterführend:** [ad fontes: „Transkription"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/transkription/)
{: .entry-refs }
```

Siegel:
```markdown
**Weiterführend:** [ad fontes: „Siegel"](https://www.adfontes.uzh.ch/tutorium/handschriften-beschreiben/siegel/)
{: .entry-refs }
```

Register:
```markdown
**Literatur:** Perger, Die Wiener Ratsbürger 1396–1526
{: .entry-refs }
```

- [ ] **Step 7: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS (alle bisherigen + neuen Tests).

- [ ] **Step 8: Commit**

```bash
git add frontend/static/css/glossar-demo.css frontend/content/project/glossar-demo/glossar.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Referenz-Zeilen + interne Verlinkung (Verweise/Literatur)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Tutorial als geführte Lektion

**Files:**
- Modify: `frontend/content/project/glossar-demo/tutorial.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: Task 1 (gebaute Demo, Tests grün). Nutzt Cross-Page-Links `glossar.html#slug` (nicht `[[#…]]`, da Ziel auf anderer Seite).
- Produces: Tutorial mit erklärender Einleitung + „Was dieser Fall zeigt"-Rahmung je Fall.

- [ ] **Step 1: Failing tests ergänzen**

In `frontend/tests/test_glossar_demo.py` anfügen:
```python
def test_tutorial_has_datenlogik_intro(built_demo):
    c = built_demo["tutorial"]
    # Einleitung erklaert die Grundbegriffe der Datenlogik und verlinkt ins Glossar
    for term in ("Event", "Rolle", "Entität"):
        assert term in c, term
    assert "glossar.html#" in c


def test_tutorial_has_case_framing(built_demo):
    c = built_demo["tutorial"]
    # Jeder der drei Faelle bekommt eine "Was dieser Fall zeigt"-Rahmung
    assert c.count("Was dieser Fall zeigt") == 3
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k "datenlogik or case_framing"`
Expected: FAIL.

- [ ] **Step 3: Einleitung (Datenlogik) einfügen**

In `frontend/content/project/glossar-demo/tutorial.md` nach der `demo-pagenav` und dem bestehenden Einleitungs-Absatz eine erklärende Passage ergänzen, die die Grundlogik erklärt und ins Glossar verlinkt (Cross-Page-Anker):
```markdown
## So funktioniert die Datenbank

Jede Quelle dokumentiert ein oder mehrere **Ereignisse**. Ein
[Event](glossar.html#event) (Ereignis) ist die grundlegende Analyseeinheit —
oft ein Rechtsgeschäft wie ein Verkauf oder eine Schenkung. An jedem Event sind
mehrere Beteiligte über eine [Rolle](glossar.html#rolle) gebunden; das
kontrollierte Vokabular kennt vier Code-Werte (`issuer`, `recipient`,
`witness`, `other`). Personen und Organisationen werden als
[Entität](glossar.html#entitat) einmalig erfasst und über ihre Rollen mit den
Events verknüpft.

Die folgenden drei Quellen spielen diese Logik durch — jeder Fall zeigt einen
anderen Aspekt.
```
Hinweis: Der Entität-Anker ist `#entitat` (Umlaut-Faltung ä→a im Slug). Vor dem Commit im gebauten `glossar.html` prüfen, dass die drei Anker (`#event`, `#rolle`, `#entitat`) als Heading-`id` existieren, und die Links ggf. daran anpassen.

- [ ] **Step 4: „Was dieser Fall zeigt" je Fall ergänzen**

In jeder der drei `demo-case`-Karten (Fall 1/2/3) nach der Rollen-Liste (`</ul>`) und vor der `demo-xref`-Zeile eine Rahmung einfügen, z. B.:
- Fall 1 (604): `<p><strong>Was dieser Fall zeigt:</strong> ein Event mit gleich vier Rollen — ein ausstellendes Ehepaar, ein Empfänger, die zustimmende Grundherrschaft „mit Handen" und ein siegelnder Zeuge.</p>`
- Fall 2 (16): `<p><strong>Was dieser Fall zeigt:</strong> eine einzelne Ausstellerin und eine Institution als Empfängerin — und dass für eine Frau ihr Ehemann siegelt (der Siegler ist nicht die Ausstellerin).</p>`
- Fall 3 (1869): `<p><strong>Was dieser Fall zeigt:</strong> wie Attribute und Relationen erfasst werden — Verwandtschaft (Witwe, Vetter, Schwester), ein Todesvermerk und ein Beruf hängen an den beteiligten Personen.</p>`

- [ ] **Step 5: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 6: Sichtprüfung**

Run: `python3 scripts/build_glossar_demo.py` und die Tutorial-Seite ansehen: Einleitung erklärt die Logik, jeder Fall trägt eine „Was dieser Fall zeigt"-Zeile, die Glossar-Links springen korrekt.

- [ ] **Step 7: Commit**

```bash
git add frontend/content/project/glossar-demo/tutorial.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Tutorial als gefuehrte Lektion (Datenlogik + Fall-Rahmung)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review (ausgefüllt)

**Spec coverage:**
- A: `.entry-refs`-Zeilen (Verwandt/Weiterführend/Literatur) → Task 1 Step 6 + Tests. ✓
- A: interne Erst-Erwähnungs-Links (Event→Quelle etc.) → Task 1 Step 5 + `test_glossar_internal_first_mention_links`. ✓
- A: externe Links aus dem `.docx` → Task 1 Step 6 + `test_glossar_has_external_links`. ✓
- A: Einheitlichkeit (`.entry-refs`, CSS) → Task 1 Step 3 + `test_entry_refs_styled_in_css`. ✓
- Slug-Stabilität (Event-Heading) → Task 1 Step 4 + `test_glossar_event_heading_clean_slug`. ✓
- B: Tutorial-Einleitung Datenlogik → Task 2 Step 3 + `test_tutorial_has_datenlogik_intro`. ✓
- B: „Was dieser Fall zeigt" je Fall → Task 2 Step 4 + `test_tutorial_has_case_framing`. ✓
- Produktions-Isolation → unverändert, `test_glossary_demo_does_not_touch_production` bleibt grün. ✓

**Placeholder scan:** Tests + CSS sind vollständiger Code; die `.md`-Edits sind exakte Ersetzungen mit konkreten URLs/Texten. Der Entität-Anker-Hinweis (Step 3) ist eine Verifikations-Anweisung, kein Platzhalter.

**Type consistency:** `.entry-refs` konsistent in CSS, Content und Tests; interne Links nur auf verifizierte Ein-Token-Slugs; Cross-Page-Links (`glossar.html#…`) im Tutorial statt `[[#…]]`.
