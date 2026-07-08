# WEITER.md — Übergabe & Fortsetzung (Glossar-Demo)

**Stand:** 2026-07-08 · **Branch:** `feat/glossar-demo` (40 Commits, alles LOKAL, NICHT gepusht)

**STATUS: bereit zur FINALEN ABNAHME durch den Stakeholder — danach Übergabe an ChPollin zur Implementierung.**
Die Demo ist inhaltlich und optisch durchgearbeitet; der Stakeholder-Durchgang ist abgeschlossen.
Der finale `.docx` (`specs/material/glossar-final.docx`, Fassung 2026-07-08) ist eingearbeitet und
adversarial verifiziert; Extrakt `specs/material/glossar-final.txt` ist synchron. **45/45 Tests grün.**

**Stakeholder-Durchgang (2026-07-08) — alle Punkte erledigt:**
- **Struktur:** **Tutorial vorerst ausgesetzt** (nicht gebaut; `tutorial.md` ruht für spätere Fallstudien). Demo **zweiseitig: Glossar + Technik**. Technik trägt „In Arbeit"-Banner. (`d1cd048a9a`)
- **Demo-eigene Zusätze (Bucket B):** entfernt bis auf den E-Intro-Satz (Seitenverweise). (`369f67a3c8`)
- **Umformulierungen (Bucket C):** geprüft und **bewusst behalten** — saubere Überschriften „Event"/„Letztwillige Verfügung"/„Grundherr:in"/„Siegler:in", „Grundzins / Grunddienst", Kurzzitate + G. Literaturverzeichnis. Abschnitt F bildet die `.docx`-Gliederung wortgetreu ab (Kategorie-Überschriften + Legende); A–E im Pro-Begriff-Format.
- **Quellenkorpus:** drei Quellenangaben wie im `.docx` (2× Uhlirz QGW, 1× Brauneder/Jaritz) als eingerückte Liste; Links verkürzt als „Weiterführend:"-Zeilen. (`94f5df09ee`, `e98e97769c`)
- **Optik:** `.entry-refs` als abgesetzte Box (warmer Hintergrund); Inhalt-TOC: Abschnitte A–G fett (`.toc > ul > li > a`). (`e2b5f8a620`, `9fc9946e32`)
- **E-Intro:** Link „Rechtshistorisches Glossar" (statt URL); „gedruckten Bände" ergänzt. (`8f450a06d5`, `ead90684f2`)
- **Literaturverzeichnis:** alphabetisch (Brauneder, Czeike×2, Ertl, Geyer, Perger, Uhlirz×2); „Christian NESCHWARA" in Großbuchstaben. (`a1c5164d03`, `9fc9946e32`)

**Hinweis zum `.docx`:** Die `.docx` auf Platte wurde von uns zweimal formaterhaltend editiert (Literaturverzeichnis alphabetisch sortiert; „Neschwara"→„NESCHWARA" nur im Brauneder-Vollzitat) — via lxml, nur Bibliografie-Absätze, Rest byte-gleich, Zip-Integrität geprüft. `glossar-final.txt` ist synchron. (Ephemere Backups lagen im Session-Scratchpad; die `.docx` auf Platte ist der maßgebliche Stand.)

## „weiter" — was tun, wenn ich das lese

Nächster Schritt ist die **finale Abnahme** durch den Stakeholder, danach die Übergabe an ChPollin.
1. Stand prüfen: `git branch --show-current` (= `feat/glossar-demo`), `git log --oneline main..HEAD`.
2. Ist-Zustand bestätigen und vorlegen: `python3 scripts/build_glossar_demo.py`, Tests
   (`PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`, erwartet: 45 passed),
   CSP-freie Vorschau erneuern (Abschnitt „Build/Test/Ansehen") und dem Stakeholder zur Abnahme zeigen.
3. **Abnahme-Feedback** einarbeiten, falls Punkte offen sind (jeweils: bauen, Tests grün, sichten, lokal committen).
4. **Nach Freigabe → Übergabe an ChPollin** (Abschnitt „Abschluss/Übergabe" unten; Branch liegt lokal, NICHT gepusht).
5. Falls doch eine **neuere `.docx`-Fassung** kommt: Diff-/Import-Ablauf im Abschnitt „Nächster Schritt" unten.

## Was ist das Projekt

Wir bauen eine **visuelle Demo eines neuen Glossars** als isoliertes Modell zur Übergabe an ChPollin. Aktuell zweiseitig (Glossar + Technik); das Tutorial ist vorerst ausgesetzt (siehe Header), `tutorial.md` liegt als ruhende Quelle bereit. Zweck: die Optik/Funktion zeigen; die Texte kommen aus einem `.docx` des Projektteams. Die echte Integration ins Frontend macht ChPollin. Details: [knowledge/](knowledge/), CLAUDE.md, und die Spec-Dateien unten.

## Aktueller Stand (fertig)

- **Demo** unter `frontend/content/project/glossar-demo/{glossar,technik}.md` → gerendert nach `docs/project/glossar-demo/*.html` via `scripts/build_glossar_demo.py` (`tutorial.md` liegt bereit, wird aber nicht gebaut).
- **Umgesetzt & reviewt (VERDIKT ready):** Grund-Demo; Plan A (produktions-konform: CSS-Asset `frontend/static/css/glossar-demo.css` + Template `frontend/templates/glossar_demo.html`, Slug-Normalisierung); Verweise/Referenzen + Tutorial-Didaktik; Refinements (Tooltip-Fix, Abschnitte D/E/F, gebeugte Verlinkung, Tutorial-Rundgang).
- **Tests:** `frontend/tests/test_glossar_demo.py` — **45 passing** (2-Seiten-Fixture; Tutorial-Tests entfernt).
- **Inhalt aus dem FINALEN `.docx`** (`specs/material/glossar-final.docx` → `…-final.txt`), von Hand eingearbeitet + adversarial verifiziert. **Es gibt keinen automatischen Importer.**

## Nächster Schritt: nur bei einer NEUEREN `.docx`-Fassung

Der finale `.docx` ist eingearbeitet. Falls eine noch neuere Fassung kommt, gilt derselbe **manuell-aber-verifizierte** Ablauf (kein Tool nötig):
1. `.docx` nach `specs/material/` legen (Binärdatei bleibt ungetrackt; `.gitignore` ignoriert alle `specs/material/*.docx`).
2. Text + Kommentare extrahieren. Fertiges Muster liegt im Session-Scratchpad (`extract_docx.py`): `.docx` ist ein ZIP → `word/document.xml` + `word/comments.xml`; Überschriften = Begriffe, Absätze = Definitionen, `<w:commentReference>` inline als `[Kommentar #N]`.
3. Gegen `specs/material/glossar-final.txt` diffen (`git diff --no-index --word-diff …`), nur die Deltas konventionskonform in `glossar-demo/*.md` übernehmen.
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

## Abschluss / Übergabe an ChPollin

Nach der finalen Abnahme geht die Demo an ChPollin. Was ChPollin bekommt: die gerenderten Seiten
`docs/project/glossar-demo/{glossar,technik}.html` (Optik/Funktion) plus die Quellen
(`frontend/content/project/glossar-demo/*.md`, `frontend/static/css/glossar-demo.css`,
`frontend/templates/glossar_demo.html`). Die eigentliche Frontend-Integration macht ChPollin.

Branch-Optionen (Stakeholder entscheidet): „so lassen" (liegt lokal); lokal nach `main` mergen;
oder — **nur auf ausdrücklichen Auftrag** — nach `origin` (mein Fork) pushen bzw. PR. **Nie nach `upstream`.**
