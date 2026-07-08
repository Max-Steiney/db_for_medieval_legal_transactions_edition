# WEITER.md — Übergabe & Fortsetzung (Glossar-Demo)

**Stand:** 2026-07-08 · **Branch:** `feat/glossar-demo` (29 Commits, alles LOKAL, NICHT gepusht)

**Der finale `.docx` ist eingearbeitet** (zuletzt Fassung 2026-07-08 mit **G. Literaturverzeichnis**;
Extrakt `specs/material/glossar-final.txt`, adversarial verifiziert). Abschnitt F bildet die
`.docx`-Gliederung wortgetreu ab (Kategorie-Überschriften + Legende); A–E im Pro-Begriff-Format.

**Stakeholder-Durchgang „Demo-Ergänzungen" (2026-07-08), Stand:**
- **Bucket B** (Demo-eigene Erklär-/Brücken-Sätze) entfernt, bis auf den E-Intro-Satz (Seitenverweise). Commit `369f67a3c8`.
- **Bucket A / Struktur:** **Tutorial vorerst aus der Demo genommen** (Commit `d1cd048a9a`) — nicht mehr gebaut, `tutorial.md` bleibt als **ruhende Quelle** für die spätere Wiederaufnahme (Fallstudien). Die Demo ist jetzt **zweiseitig: Glossar + Technik**. Technik trägt ein „In Arbeit"-Banner; das Glossar-Intro verlinkt nur noch auf das „technische Glossar" und hat die Abschnitts-Aufzählung + Tooltip-Vorschau verloren. Referenzzeilen + interne Sprunglinks bleiben.
- **Offen: Bucket C** (Umformulierungen: saubere Überschriften „Event"/„Letztwillige Verfügung"/„Grundherr:in"/„Siegler:in"; „Grundzins / Grunddienst"; Kurzzitate + Literaturverzeichnis) — noch mit dem Stakeholder durchzugehen.
- **Tests:** `frontend/tests/test_glossar_demo.py` — **45/45 grün** (Fixture auf 2 Seiten; Tutorial-Tests entfernt).

## „weiter" — was tun, wenn ich das lese

Wenn der User „weiter" sagt:
1. Prüfe den Stand: `git branch --show-current` (soll `feat/glossar-demo` sein), `git log --oneline main..HEAD`.
2. Baue + teste einmal, um den Ist-Zustand zu bestätigen:
   `python3 scripts/build_glossar_demo.py` und
   `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q` (erwartet: 45 passed).
3. Falls eine **neuere `.docx`-Fassung** kommt: nach `specs/material/` legen, mit
   `scratchpad/extract_docx.py`-Muster extrahieren (DOCX=ZIP → `word/document.xml`+`word/comments.xml`),
   gegen `glossar-final.txt` diffen, Deltas konventionskonform übernehmen (siehe unten). Sonst → Branch-Abschluss unten.

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

## Abschluss-Optionen für den Branch (wenn gewünscht)

Branch bleibt aktuell liegen (Option „so lassen"). Alternativen später: lokal nach `main` mergen, oder — nur auf ausdrücklichen Auftrag — nach `origin` pushen. Nie nach `upstream`.
