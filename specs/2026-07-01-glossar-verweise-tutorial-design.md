# Design: Glossar-Verweise/Referenzen + Tutorial-Didaktik (Demo)

Stand: 2026-07-01
Status: Entwurf zur Durchsicht

## Anlass

Sichtungs-Feedback des Users an der Demo (nach Plan A):
1. Das Glossar „kennt sich selbst nicht" — Einträge sollten aufeinander verweisen.
2. Nur Tutorial/Technik sind verlinkt; der `.docx` enthält bereits viele Hyperlinks
   (ad fontes, Wien-Wiki, monasterium), die die Demo weglässt.
3. Keine einheitliche Lösung für weiterführende Links und Literaturangaben — soll
   über alle Glossar-Seiten gleich sein.
4. Das Tutorial ist nur eine Liste der Fallbeispiele und erklärt sich nicht selbst.

Ziel: die Muster **jetzt** festlegen (vor den Finaltexten), auf die Demo anwenden
und in die Import-Pipeline (Plan B) einbauen. Proportional gehalten — keine großen
Umbauten.

## A. Verweise & Referenzen (Punkte 1–3)

### Referenz-Zeilen-Konvention

Nach der Definition eines Eintrags folgen bei Bedarf einheitlich beschriftete
Zeilen, markdown-nativ über die (bereits aktivierte) `attr_list`-Extension mit der
Klasse `.entry-refs`, gestylt in `frontend/static/css/glossar-demo.css`:

```markdown
**Verwandt:** [[#Urkunde]] · [[#Quelle]]
**Weiterführend:** [ad fontes: „Regest"](https://www.adfontes.uzh.ch/…)
**Literatur:** Brauneder/Jaritz, FRA III/10 (1989)
{: .entry-refs }
```

Die Zeilen bilden EINEN Absatz (jeweils mit hartem Zeilenumbruch, also zwei
Leerzeichen am Zeilenende); das `{: .entry-refs }` in der letzten Zeile hängt die
Klasse an den gesamten Absatz. Nur vorhandene Zeilen schreiben.

- **Verwandt** — interne `[[#Begriff]]`-Sprünge (rendern via `_rewrite_wiki_links`
  zu `[Label](#slug)`; die Anker liegen auf der Glossar-Seite).
- **Weiterführend** — externe Links aus dem `.docx` (ad fontes, Wien-Wiki,
  monasterium.net).
- **Literatur** — Literaturangaben aus dem `.docx` (die „Siehe zu …"-Hinweise:
  Brauneder/Jaritz, Geyer, Ertl, Czeike, Perger, Uhlirz …).
- Nur die tatsächlich vorhandenen Zeilen erscheinen; **keine leeren Platzhalter**.

Technischer Hinweis: `attr_list` wird auf einen Markdown-Absatz angewandt (`{: .entry-refs }`
in der Folgezeile). Die `[[#…]]`-Links stehen im Markdown-Text (NICHT in einem rohen
HTML-Block), damit Python-Markdown sie zu Links rendert.

### Interne Selbst-Verlinkung (Punkt 1)

Zusätzlich zur `Verwandt`-Zeile wird die **erste Erwähnung** eines anderen
Glossarbegriffs im Definitionstext verlinkt (Beispiel: der Eintrag „Event" nennt
„Quelle" → `[[#Quelle]]`). Bewusst einfach: nur die Erstnennung, nicht jede.

### Einheitlichkeit (Punkt 3)

Dieselbe `.entry-refs`-Konvention gilt auf **allen** Glossar-Demo-Seiten, wo
Referenzen vorkommen (Glossar, Technik, Tutorial). Ein Muster, eine CSS-Klasse.

## B. Tutorial als geführte Lektion (Punkt 4)

Aus der reinen Fall-Liste wird eine kleine Lektion:

- **Einleitung**, die die Datenlogik erklärt: Was ist ein *Event*, eine *Rolle*,
  eine *Entität* — mit `[[#…]]`-Sprüngen ins Glossar.
- Jeder der drei Fälle (604/16/1869) bekommt eine kurze Rahmung
  **„Was dieser Fall zeigt"** (z. B. Fall 1: mehrere Rollen + „mit Handen";
  Fall 2: Ausstellerin + fremder Siegler; Fall 3: Verwandtschafts-/Status-Attribute)
  und Rückverweise ins Glossar/Technik.
- Ergebnis: Nach dem Tutorial versteht eine neue Person die Grundlogik, nicht nur
  drei Einzelbeispiele.

Die Rahmungstexte schreibe ich als **Demo-Text** (vom Team final verfeinerbar);
sie stehen unter der `.dev-only`-freien, sichtbaren Ebene (echter Tutorial-Inhalt).

## Herkunft der Inhalte & Import (Plan B)

- **Demo jetzt:** Referenzen/Links werden aus dem vorliegenden `.docx`-Extrakt
  (`specs/material/glossar-entwurf.txt`) befüllt; die Tutorial-Rahmung wird als
  Demo-Text geschrieben.
- **Plan B (Import):** Die Konventionen werden Teil der Pipeline:
  - Externe Links/Literatur aus dem `.docx` landen automatisch in
    `Weiterführend`/`Literatur`-Zeilen.
  - Ein einfacher „erste-Nennung-verlinken"-Durchgang bereitet die internen
    `Verwandt`-/Inline-Verweise vor (gegen die bekannte Begriffsliste), zur
    redaktionellen Kontrolle geflaggt.

## Scope / Guardrails

- Nur `frontend/content/project/glossar-demo/*.md` + `frontend/static/css/glossar-demo.css`
  + Tests. Produktive `glossar.md`/`glossary.html` unberührt.
- Nur Markdown-Content, nie `docs/` direkt; lokal bauen mit
  `python3 scripts/build_glossar_demo.py`; kein Push.
- Interne Anker bleiben produktions-konform (saubere Term-Slugs, siehe Plan A).

## Tests

- `.entry-refs`-Zeilen erscheinen auf der Glossar-Seite (mind. je ein Verwandt/
  Weiterführend/Literatur-Beispiel gerendert).
- Interne `[[#…]]`-Verweise lösen zu funktionierenden Ankern auf (z. B. der
  „Event"-Eintrag enthält einen Link auf `#quelle`).
- Externe Links aus dem `.docx` erscheinen als `href`-Links (mind. ein ad-fontes-
  und ein Wien-Wiki-Link).
- `.entry-refs` ist in `glossar-demo.css` gestylt.
- Tutorial hat eine Einleitung (Datenlogik) und je Fall eine „Was dieser Fall
  zeigt"-Rahmung.
- Produktions-Isolationstest bleibt grün.

## Nicht-Ziele (YAGNI)

- Keine Verlinkung jeder Begriffs-Erwähnung (nur Erstnennung).
- Kein interaktiver JS-Walkthrough im Tutorial.
- Kein gestylter Referenz-Karten-Block (nur schlichte beschriftete Zeilen).
- Keine Änderung an Produktion/Pipeline/Datenschicht.
