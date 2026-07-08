# Übergabe: Glossar-Demo → Integration

**Für:** ChPollin (Frontend-Integration) · **Stand:** 2026-07-08 · **Branch:** `feat/glossar-demo`

Diese Demo ist ein **isoliertes Referenzmodell** für ein neues Glossar der Datenbank
„Stadt und Gemeinschaft Wien". Sie zeigt Optik, Struktur und die Änderungspipeline an
einem lauffähigen Beispiel. Die eigentliche Integration ins produktive Frontend liegt
bei dir; diese Demo nimmt dir die inhaltliche und gestalterische Vorarbeit ab.

## Wichtigste Eigenschaft: alles additiv

Die Demo berührt **keine** Produktionsdateien. Sie fügt nur neue Dateien hinzu und lässt
`frontend/content/project/glossar.md` und `docs/project/glossary.html` (deine Integration)
unangetastet. Der Branch lässt sich daher gefahrlos lesen, cherry-picken, mergen oder
weiterbauen — er kann deine spätere Arbeit nicht überschreiben.

## Deliverables (die relevanten Dateien)

| Datei | Rolle |
|---|---|
| `frontend/content/project/glossar-demo/glossar.md` | **Inhaltliches Glossar** — die redigierten Begriffstexte (A–G), Kern des Modells |
| `frontend/content/project/glossar-demo/technik.md` | **Technisches Glossar** — Platzhalter, trägt „In Arbeit"-Banner |
| `frontend/content/project/glossar-demo/tutorial.md` | Ruhende Quelle (Fallstudien) — **nicht gebaut**, für spätere Erweiterung |
| `frontend/static/css/glossar-demo.css` | Seiten-lokales Styling (entry-refs-Box, TOC, Tooltip-Demo) |
| `frontend/templates/glossar_demo.html` | Template-Chrome (setzt auf `about.html` auf) |
| `frontend/build/_pages.py` → `_build_glossar_demo()` | Build-Anbindung inkl. Slug-Normalisierung |
| `scripts/build_glossar_demo.py` | Eigenständiges Build-Skript der Demo |
| `frontend/tests/test_glossar_demo.py` | 45 Regressionstests |
| `docs/project/glossar-demo/{glossar,technik}.html` | Gerenderte Seiten (Build-Output) |

Textquelle der Begriffe: `specs/material/glossar-final.docx` (das finale `.docx` des Projektteams,
im Branch enthalten). Für die Integration nicht zwingend nötig — der Text steckt bereits gerendert
in `glossar.md` — aber beigelegt, falls du direkt mit der Datei arbeiten möchtest. Das `.docx`
enthält zusätzlich die Arbeitsabschnitte H (Datenmodell/roleNames) und I (drei Fallbeispiele mit
Links auf dein Frontend), die in der Demo bewusst noch nicht erscheinen.

## Bauen und Ansehen

```
python3 scripts/build_glossar_demo.py          # baut docs/project/glossar-demo/*.html
python3 -m pytest frontend/tests/test_glossar_demo.py -q   # 45 passed
```

Nicht `python -m frontend build` — die Demo hat keine Pipeline/CSV und baut eigenständig.

Lokale Ansicht: `python3 -m http.server 8000 --directory docs`, dann
`http://localhost:8000/project/glossar-demo/glossar.html`. Hinweis: Die produktive CSP
(`upgrade-insecure-requests`) bricht CSS über `http://localhost` in Safari; auf GitHub Pages
(HTTPS) kein Problem. Für lokale Safari-Ansicht die CSP-Meta aus den HTMLs strippen.

## Content-Modell (so werden neue Begriffe gepflegt)

- `## Abschnitt`, `### Begriff` (Überschrift = sauberer kanonischer Term, kein Code-Alias → Slug-Stabilität).
- Definition als Fließtext-Absatz.
- **Referenz-Zeilen** am Eintragsende: ein Absatz mit hartem Umbruch (zwei Leerzeichen am
  Zeilenende), Labels `**Verwandt:** / **Weiterführend:** / **Literatur:**`, `{: .entry-refs }`
  in der letzten Zeile. Rendert als abgesetzte Box.
- **Interne Sprünge:** `[[#Begriff]]` bzw. `[[#Begriff|Anzeigetext]]` → beim Build zu
  `[Text](#slug)` umgeschrieben. **Achtung ß/ss:** die Slug-Regel entfernt `ß` ganz statt
  `ß→ss`; Begriffe mit `ß` nicht als internes Sprungziel verwenden.
- **Gender-Doppelpunkt** (`Bürger:in`), nicht Gender-Stern.
- Inhaltsverzeichnis („Inhalt", A–G fett) wird automatisch aus den Überschriften erzeugt.

## Zwei Seiten + die Änderungspipeline testen

Aktiv sind **Glossar** und **Technik**. Die Technik-Seite ist bewusst als „In Arbeit"
markiert und eignet sich als **Testfläche für die Änderungspipeline**: Markdown-Quelle
bearbeiten → `build_glossar_demo.py` → gerenderte Seite prüfen — einmal durchspielen, bevor
das inhaltliche Glossar produktiv angebunden wird. Das Tutorial ist vorerst ausgesetzt
(`tutorial.md` ruht als Quelle; die Fallstudien kommen später als Tutorial zurück).

## Qualitätsstand

45/45 Tests grün; Inhalt gegen das Team-`.docx` und alle Stakeholder-Vorgaben unabhängig
(mehrstufig, grep-geerdet) verifiziert. Detaillierte Projekthistorie: `WEITER.md`.
