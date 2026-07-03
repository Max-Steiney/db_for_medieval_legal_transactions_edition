# WEITER.md — Übergabe & Fortsetzung (Glossar-Demo)

**Stand:** 2026-07-03 · **Branch:** `feat/glossar-demo` (22 Commits, alles LOKAL, NICHT gepusht)

## „weiter" — was tun, wenn ich das lese

Wenn der User „weiter" sagt:
1. Prüfe den Stand: `git branch --show-current` (soll `feat/glossar-demo` sein), `git log --oneline main..HEAD`.
2. Baue + teste einmal, um den Ist-Zustand zu bestätigen:
   `python3 scripts/build_glossar_demo.py` und
   `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q` (erwartet: 39 passed).
3. Frag den User, ob der **finale Glossar-`.docx`** jetzt vorliegt. Falls ja → „Nächster Schritt" unten. Falls nein → auf sein Signal warten.

## Was ist das Projekt

Wir bauen eine **visuelle Demo eines neuen Glossars** (drei Seiten: Glossar / Technik / Tutorial) als isoliertes Modell zur Übergabe an ChPollin. Zweck: die Optik/Funktion zeigen; die Texte kommen aus einem `.docx` des Projektteams. Die echte Integration ins Frontend macht ChPollin. Details: [knowledge/](knowledge/), CLAUDE.md, und die Spec-Dateien unten.

## Aktueller Stand (fertig)

- **3-Seiten-Demo** unter `frontend/content/project/glossar-demo/{glossar,technik,tutorial}.md` → gerendert nach `docs/project/glossar-demo/*.html` via `scripts/build_glossar_demo.py`.
- **Umgesetzt & reviewt (VERDIKT ready):** Grund-Demo; Plan A (produktions-konform: CSS-Asset `frontend/static/css/glossar-demo.css` + Template `frontend/templates/glossar_demo.html`, Slug-Normalisierung); Verweise/Referenzen + Tutorial-Didaktik; Refinements (Tooltip-Fix, Abschnitte D/E/F, gebeugte Verlinkung, Tutorial-Rundgang).
- **Tests:** `frontend/tests/test_glossar_demo.py` — **39 passing**.
- **Inhalt bisher aus dem ENTWURFS-`.docx`** (`specs/material/glossar-entwurf.txt`), von Hand eingearbeitet. **Es gibt keinen automatischen Importer.**

## Nächster Schritt (der „weiter"-Kern): finaler `.docx`

Der Import ist **im Wesentlichen einmalig**. Empfehlung: **manuell-aber-verifiziert** einarbeiten (wie bisher), kein aufwändiges Tool nötig (optionale Tooling-Spec: `specs/2026-07-01-glossar-import-system-design.md`, Teil B — NICHT gebaut).

Ablauf beim finalen `.docx`:
1. `.docx` nach `specs/material/` legen (Binärdatei bleibt ggf. ungetrackt).
2. Text + Kommentare extrahieren (einmaliges Python: `.docx` ist ein ZIP → `word/document.xml` + `word/comments.xml`; Überschriften = Begriffe, Absätze = Definitionen). Vorlage: die vorhandenen `specs/material/glossar-entwurf.txt` / `…-kommentare.txt` wurden so erzeugt.
3. Die finalen Texte in die `glossar-demo/*.md` übernehmen — **Struktur & Konventionen unten strikt beibehalten**; Referenzen (`Weiterführend`/`Literatur`) und interne `[[#Begriff]]`-Verweise mitziehen.
4. Bauen, Tests grün, sichten.
5. **Offener Prüfpunkt aus dem Review:** ß-Slug-Divergenz — die TOC-Slugify wirft `ß` weg, `_slug_anchor` faltet `ß→ss`. Begriffe mit `ß` NICHT als interne Link-Ziele nehmen bzw. Slugs angleichen.

## Konventionen (verbindlich, nicht brechen)

- **Content-Modell:** `## Abschnitt`, `### Begriff` (Überschrift = sauberer kanonischer Term, KEIN Code-Alias in der Überschrift → sonst Slug-Drift). Definition als Absatz. Interne Verweise `[[#Begriff]]` bzw. `[[#Begriff|Wort]]` (Label-Form für gebeugte Formen, z. B. `[[#Entität|Entitäten]]`).
- **Referenz-Zeilen:** ein Absatz mit hartem Umbruch (zwei Leerzeichen am Zeilenende), Labels `**Verwandt:** / **Weiterführend:** / **Literatur:**`, `{: .entry-refs }` in der LETZTEN Zeile; steht VOR einer etwaigen `.dev-only`-Notiz. Nur vorhandene Zeilen (keine leeren).
- **Gender-Doppelpunkt** (`Bürger:in`), NICHT Gender-Stern.
- **Rollen-Codes** exakt: `issuer`, `recipient`, `witness`, `other`.
- **Tutorial** verlinkt Glossar-Begriffe als Cross-Page-Links `[Wort](glossar.html#slug)` (NICHT `[[#…]]`, da anderes Dokument).
- **`.dev-only`** für offene/interne Notizen (versteckt; sichtbar mit `?dev=1`).

## Build / Test / Ansehen

- **Bauen:** `python3 scripts/build_glossar_demo.py` — **NICHT** `python -m frontend build` (hier kein Pipeline/CSV; schlägt fehl).
- **Tests:** `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`.
- **Build-Deps** sind per `pip --user` installiert (jinja2, markdown, pytest, pygments).
- **Safari-Ansicht (CSP-frei):** nach dem Bau CSP-Meta aus den drei HTMLs strippen und nach `docs/project/glossar-demo-preview/` (gitignored) schreiben; Server: `python3 -m http.server 8000 --directory docs`; öffnen: `http://localhost:8000/project/glossar-demo-preview/glossar.html` (`?dev=1` für Redaktionsnotizen). Grund: die produktive CSP (`upgrade-insecure-requests`) bricht CSS über `http://localhost` in Safari; auf GitHub Pages (HTTPS) kein Problem. (Der lokale Server aus dieser Sitzung läuft evtl. noch; sonst neu starten.)

## Guardrails / Sicherheit

- **Produktiv unberührt:** `frontend/content/project/glossar.md` und `docs/project/glossary.html` NICHT ändern (das ist ChPollins Integration). `docs/` ist Build-Output — nie direkt editieren.
- **Kein Push** ohne ausdrücklichen Auftrag. `origin` = mein Fork (Push nur auf Zuruf), `upstream` = Original mit gesperrtem Push (NIEMALS dorthin).
- **Nachbarordner:** `../db_for_medieval_legal_transactions_MS_Test` = mein Pipeline-Fork, READ-ONLY (liefert `pipeline.config` für Tests). `../db_for_medieval_legal_transactions` (ohne Suffix) = fremder Klon — NIEMALS anfassen.
- `frontend/__init__.py` verdrahtet den Pipeline-Pfad fest auf den fremden Ordner (ohne `pipeline`); deshalb Tests/Runner mit `PYTHONPATH=…_MS_Test`.

## Referenz-Dateien (auf diesem Branch)

- Specs: `specs/2026-06-30-glossar-demo-design.md`, `specs/2026-07-01-glossar-import-system-design.md`, `specs/2026-07-01-glossar-verweise-tutorial-design.md`
- Pläne: `specs/plans/*.md`
- Inhalts-Extrakt (Entwurf): `specs/material/glossar-entwurf.{docx,txt}`, `…-kommentare.txt`
- Ausführungs-Ledger (gitignored): `.superpowers/sdd/progress.md`

## Abschluss-Optionen für den Branch (wenn gewünscht)

Branch bleibt aktuell liegen (Option „so lassen"). Alternativen später: lokal nach `main` mergen, oder — nur auf ausdrücklichen Auftrag — nach `origin` pushen. Nie nach `upstream`.
