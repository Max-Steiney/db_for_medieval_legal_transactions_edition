# WEITER.md — Übergabe & Fortsetzung (Glossar-Demo)

**Stand:** 2026-07-08 · **Branch:** `feat/glossar-demo` (auf `origin`; Historie am 2026-07-08 bereinigt)

**STATUS: ABGENOMMEN — Übergabe an ChPollin vorbereitet, PR macht der Stakeholder selbst.**
Der Stakeholder hat die Demo am 2026-07-08 abgenommen. Übergabeweg: Branch nach `origin`
(mein Fork) gepusht; Übergabe an ChPollin per Cross-Fork-PR gegen `upstream` (= `chpollin/…_edition`).
`upstream` wird dabei nie gepusht (ein PR schlägt vor). **Offener Schritt:** der Stakeholder öffnet den
PR selbst zusammen mit einer erklärenden E-Mail an Christopher (ChPollin) — PR-Materialien unten.
ChPollin-gerichtete Kurz-Doku: `HANDOVER-ChPollin.md`. **45/45 Tests grün.**

> **Hinweis Commit-Hashes:** Die Branch-Historie wurde am 2026-07-08 umgeschrieben (siehe
> „Material-Bereinigung"). Alle früheren Commit-Kurz-Hashes sind damit **ungültig**; den
> aktuellen Stand immer über `git log --oneline main..HEAD` prüfen.

**Material-Bereinigung (2026-07-08):** Die vier getrackten `.txt`-Arbeitsextrakte unter
`specs/material/` (`glossar-entwurf.txt`, `glossar-entwurf-kommentare.txt`, `glossar-final.txt`,
`glossar-final-kommentare.txt`) waren Working Documents — u. a. enthielt `…-entwurf-kommentare.txt`
interne Team-Kommentare (Klarnamen, E-Mail-Adresse, candide Anmerkungen). Sie wurden per
`git filter-branch` **komplett aus der Branch-Historie entfernt** und der Branch force-gepusht,
damit sie nicht im öffentlichen PR erscheinen. Im Repo bleiben nur die Design-Specs (`specs/*.md`)
und Pläne (`specs/plans/*.md`). Das `.docx` selbst ist ohnehin **gitignored** (nie im Repo);
`glossar-final.docx` liegt lokal weiter auf Platte als redaktionelle Quelle.

**Stakeholder-Durchgang (2026-07-08) — alle Punkte erledigt (Hashes s. o. nicht mehr gültig):**
- **Struktur:** Tutorial vorerst ausgesetzt (nicht gebaut; `tutorial.md` ruht für spätere Fallstudien). Demo **zweiseitig: Glossar + Technik**. Technik trägt „In Arbeit"-Banner.
- **Demo-eigene Zusätze (Bucket B):** entfernt bis auf den E-Intro-Satz (Seitenverweise).
- **Umformulierungen (Bucket C):** geprüft und bewusst behalten — saubere Überschriften „Event"/„Letztwillige Verfügung"/„Grundherr:in"/„Siegler:in", „Grundzins / Grunddienst", Kurzzitate + G. Literaturverzeichnis. Abschnitt F bildet die `.docx`-Gliederung wortgetreu ab (Kategorie-Überschriften + Legende); A–E im Pro-Begriff-Format.
- **Quellenkorpus:** drei Quellenangaben wie im `.docx` (2× Uhlirz QGW, 1× Brauneder/Jaritz) als eingerückte Liste; Links verkürzt als „Weiterführend:"-Zeilen.
- **Optik:** `.entry-refs` als abgesetzte Box (warmer Hintergrund); Inhalt-TOC: Abschnitte A–G fett (`.toc > ul > li > a`).
- **E-Intro:** Link „Rechtshistorisches Glossar" (statt URL); „gedruckten Bände" ergänzt.
- **Literaturverzeichnis:** alphabetisch (Brauneder, Czeike×2, Ertl, Geyer, Perger, Uhlirz×2); „Christian NESCHWARA" in Großbuchstaben.

**Finale Verifikation (2026-07-08):** 5-Lens-Workflow (Text-Treue vs. `.docx`, Struktur A–G,
Tutorial-Aussetzung, Stakeholder-Items, Link/Render), grep-geerdet und gegen eigene Greps
korroboriert — **0 Findings**.

## „weiter" — was tun, wenn ich das lese

Die Demo ist **abgenommen** und der Branch liegt auf `origin`. Offen ist nur die **PR-Übergabe** —
die macht der Stakeholder selbst mit erklärender E-Mail an Christopher.
1. Stand prüfen: `git branch --show-current` (= `feat/glossar-demo`), `git log --oneline main..HEAD`,
   `git status` (sauber), lokal == `origin` (`git log origin/feat/glossar-demo..HEAD` leer).
2. **PR-Materialien** liegen bereit (Compare-URL, Titel, Beschreibung) — Abschnitt „Abschluss / Übergabe".
   `gh` ist lokal nicht installiert; PR per Klick auf die Compare-URL. E-Mail-Entwurf lag im
   Session-Scratchpad (nicht committet, da an Christopher gerichtet).
3. Kommt **Abnahme-Feedback**: einarbeiten (bauen, Tests grün, sichten, lokal committen, pushen).
4. Kommt eine **neuere `.docx`-Fassung**: Diff-/Import-Ablauf im Abschnitt „Nächster Schritt".

## Was ist das Projekt

Wir bauen eine **visuelle Demo eines neuen Glossars** als isoliertes Modell zur Übergabe an ChPollin. Aktuell zweiseitig (Glossar + Technik); das Tutorial ist vorerst ausgesetzt (siehe Header), `tutorial.md` liegt als ruhende Quelle bereit. Zweck: die Optik/Funktion zeigen; die Texte kommen aus einem `.docx` des Projektteams. Die echte Integration ins Frontend macht ChPollin. Details: [knowledge/](knowledge/), CLAUDE.md, und die Spec-Dateien unten.

## Aktueller Stand (fertig)

- **Demo** unter `frontend/content/project/glossar-demo/{glossar,technik}.md` → gerendert nach `docs/project/glossar-demo/*.html` via `scripts/build_glossar_demo.py` (`tutorial.md` liegt bereit, wird aber nicht gebaut).
- **Umgesetzt & reviewt (VERDIKT ready):** Grund-Demo; Plan A (produktions-konform: CSS-Asset `frontend/static/css/glossar-demo.css` + Template `frontend/templates/glossar_demo.html`, Slug-Normalisierung); Verweise/Referenzen + Tutorial-Didaktik; Refinements (Tooltip-Fix, Abschnitte D/E/F, gebeugte Verlinkung).
- **Tests:** `frontend/tests/test_glossar_demo.py` — **45 passing** (2-Seiten-Fixture; Tutorial-Tests entfernt).
- **Inhalt aus dem FINALEN `.docx`** (liegt lokal/gitignored unter `specs/material/`), von Hand eingearbeitet + adversarial verifiziert. **Es gibt keinen automatischen Importer.**

## Nächster Schritt: nur bei einer NEUEREN `.docx`-Fassung

Der finale `.docx` ist eingearbeitet. Falls eine noch neuere Fassung kommt, gilt derselbe **manuell-aber-verifizierte** Ablauf (kein Tool nötig):
1. `.docx` nach `specs/material/` legen (Binärdatei bleibt ungetrackt; `.gitignore` ignoriert alle `specs/material/*.docx`).
2. Text + Kommentare extrahieren. Muster-Skript `extract_docx.py` (Session-Scratchpad): `.docx` ist ein ZIP → `word/document.xml` + `word/comments.xml`; Überschriften = Begriffe, Absätze = Definitionen, `<w:commentReference>` inline als `[Kommentar #N]`. **Extrakte in eine temporäre Datei (Scratchpad) schreiben, nicht ins Repo committen** (Working Documents).
3. Alten Stand zum Vergleich aus dem `.docx` bzw. per `git show` extrahieren und mit `git diff --no-index --word-diff …` gegen den neuen Extrakt diffen; nur die Deltas konventionskonform in `glossar-demo/*.md` übernehmen.
4. Bauen, Tests grün, sichten; für neue/umbenannte Begriffe Regressionstests nachziehen.
5. **Offener Prüfpunkt:** ß-Slug-Divergenz — TOC-Slugify wirft `ß` weg, `_slug_anchor` faltet `ß→ss`. Begriffe mit `ß` NICHT als interne Link-Ziele nehmen. (Aktuell kein Link-Ziel mit `ß`; die H2 „F. … Maße …" hat `ß`, ist aber kein Sprungziel.)

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
- **Safari-Ansicht (CSP-frei):** nach dem Bau CSP-Meta aus den **beiden** HTMLs strippen und nach `docs/project/glossar-demo-preview/` (gitignored) schreiben; Server: `python3 -m http.server 8000 --directory docs`; öffnen: `http://localhost:8000/project/glossar-demo-preview/glossar.html` (`?dev=1` für Redaktionsnotizen). Grund: die produktive CSP (`upgrade-insecure-requests`) bricht CSS über `http://localhost` in Safari; auf GitHub Pages (HTTPS) kein Problem.
- **Nach dem Bau:** die HTMLs bekommen einen neuen `?v=`-Cache-Bust-Stempel. Ist das die einzige Änderung, verwerfen (`git checkout -- docs/project/glossar-demo/*.html`); nur bei echter Inhalts-/CSS-Änderung committen.

## Guardrails / Sicherheit

- **Produktiv unberührt:** `frontend/content/project/glossar.md` und `docs/project/glossary.html` NICHT ändern (das ist ChPollins Integration). `docs/` ist Build-Output — nie direkt editieren.
- **Kein Push** ohne ausdrücklichen Auftrag. `origin` = mein Fork (Push nur auf Zuruf; der `feat/glossar-demo`-Push + Force-Push am 2026-07-08 war ausdrücklich freigegeben), `upstream` = Original mit gesperrtem Push (NIEMALS dorthin). Beide Repos sind **öffentlich**.
- **Nachbarordner:** `../db_for_medieval_legal_transactions_MS_Test` = mein Pipeline-Fork, READ-ONLY (liefert `pipeline.config` für Tests). `../db_for_medieval_legal_transactions` (ohne Suffix) = fremder Klon — NIEMALS anfassen.
- `frontend/__init__.py` verdrahtet den Pipeline-Pfad fest auf den fremden Ordner (ohne `pipeline`); deshalb Tests/Runner mit `PYTHONPATH=…_MS_Test`.

## Referenz-Dateien (auf diesem Branch)

- Specs: `specs/2026-06-30-glossar-demo-design.md`, `specs/2026-07-01-glossar-import-system-design.md`, `specs/2026-07-01-glossar-verweise-tutorial-design.md`
- Pläne: `specs/plans/*.md`
- Inhalts-Quelle: `specs/material/glossar-final.docx` (lokal, **gitignored**, nicht im Repo). Die früheren `.txt`-Arbeitsextrakte + Kommentar-Dateien wurden am 2026-07-08 als Working Documents aus der Historie entfernt.
- Ausführungs-Ledger (gitignored): `.superpowers/sdd/progress.md`

## Abschluss / Übergabe an ChPollin

Was ChPollin bekommt: die gerenderten Seiten `docs/project/glossar-demo/{glossar,technik}.html`
(Optik/Funktion) plus die Quellen (`frontend/content/project/glossar-demo/*.md`,
`frontend/static/css/glossar-demo.css`, `frontend/templates/glossar_demo.html`) und
`HANDOVER-ChPollin.md` als Einstieg. Die eigentliche Frontend-Integration macht ChPollin.
Das `.docx` braucht er dafür nicht (der Text steckt gerendert in `glossar.md`); bei Bedarf als
E-Mail-Anhang, nicht über den PR.

**PR-Materialien (Stakeholder öffnet den PR selbst):**
- Compare-URL:
  `https://github.com/chpollin/db_for_medieval_legal_transactions_edition/compare/main...Max-Steiney:db_for_medieval_legal_transactions_edition_MS_Testing:feat/glossar-demo?expand=1`
- Titel: `Glossar-Demo: isoliertes Referenzmodell (Glossar + Technik) zur Integration`
- Beschreibung: additives Referenzmodell, berührt keine Produktionsdateien; Einstieg `HANDOVER-ChPollin.md`;
  Build `python3 scripts/build_glossar_demo.py`, Tests `… -m pytest frontend/tests/test_glossar_demo.py -q` (45 passed).
- Fallback ohne Fork-PR: ChPollin fügt meinen Fork als Remote hinzu und fetcht `feat/glossar-demo`.

Branch-Optionen (Stakeholder entscheidet): PR öffnen (gewählter Weg); „so lassen"; lokal nach `main`
mergen. **Nie nach `upstream` pushen.**
