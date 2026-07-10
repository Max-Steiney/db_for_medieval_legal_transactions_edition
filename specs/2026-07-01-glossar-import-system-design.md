# Design: Glossar-Import-System (finaler .docx → Demo, produktions-konform)

Stand: 2026-07-01
Status: Entwurf zur Durchsicht

## Ziel

Eine **wiederholbare, verifizierte Einmal-Import-Prozedur**, die den finalen,
sauberen (kommentar-freien) Glossar-`.docx` des Teams in die Markdown-Quellen des
Demo-Modells überführt — und den Inhalt dabei **produktions-konform formt**, sodass
ChPollins finale Übernahme in die echte `frontend/content/project/glossar.md`
nahezu mechanisch wird.

Entscheidungen des Users (2026-06-30/07-01):
- Import ist **im Wesentlichen einmalig**; danach ist Markdown die führende Quelle.
- Finaler `.docx` kommt **sauber** (Kommentare eingearbeitet).
- Ansatz **A**: geführter, halb-automatischer Import mit **Verifikations-Gate**.
- Ziel: **Demo, aber produktions-konform geformt** — Produktion bleibt unberührt.

## Zweck & Leitprinzip (Rahmung des Projektteams)

ChPollin hat das Frontend entworfen und nach Team-Feedback überarbeitet. Das
Projektteam schreibt gerade die Glossar-Texte. Zusätzlich zu den Texten soll
ChPollin eine **Demo des Glossars** (echte Texte + Tutorial + Technik) erhalten,
damit visuell sichtbar wird, wie sich das Team das Glossar und seine Aufgaben
vorstellt.

Zweck der Demo: **so nah wie möglich in das Frontend integrierbar, ohne tatsächlich
Teil davon zu sein.** Die echte Einarbeitung/Verbindung von Glossar und Frontend
ist ChPollins Aufgabe. Deshalb greift die Demo schon jetzt auf **so viele bestehende
Frontend-Ressourcen wie möglich** zurück (Templates, Render-Pipeline, Macros,
CSS-Klassen, Konventionen), damit der Übergang Demo → echtes Frontend so reibungslos
wie möglich wird.

Arbeitsfolge des Teams: das Frontend-System verstehen → die Demo darauf aufbauen →
wenn die Texte final sind, in dieses Muster importieren → als „fertige" Demo
**visuelle Demo + Texte** an ChPollin zur Einarbeitung schicken. Dieses Dokument
spezifiziert den Import-/Formungs-Schritt dieser Folge.

## Grundlage: knowledge/-Muster (belegt)

Ein Understand-Durchgang über `knowledge/` hat die tragenden Frontend-Muster
bestätigt. Die für den Import bindenden Erkenntnisse:

1. **Content-Pipeline `_render_content_page`** (`frontend/build/_pages.py`
   Z.1171-1197): eine Markdown-Quelle je Seite → `about.html`/`base.html`-Gerüst.
   Transform-Kette: Frontmatter-Strip → führendes-H1-Strip → Wiki-Link-Rewrite →
   Markdown-Render → Template. **Import schreibt nur Markdown, nie nach `docs/`.**
2. **Slug/Anker deterministisch aus dem Überschriften-TEXT** (`_slug_anchor`
   Z.1117-1127): lowercase, Umlaut-Faltung, Nicht-Alnum → Bindestrich. Unabhängig
   vom Heading-Level. `[[#Term]]` wird via `_rewrite_wiki_links` (Z.1144-1168)
   aufgelöst.
3. **`tip_glossary`-Macro** (`frontend/templates/macros.html` Z.254-280) speist die
   UI-Tooltips und verlinkt hart auf `project/glossary.html#slug` (**produktiv**,
   nicht Demo). Kurz- und Langdefinition sollten aus einer Single-Source je Begriff
   kommen. Macro immer `with context` importieren (root_path im Link).
4. **Zwei Glossar-Fassungen divergieren:** produktive `glossar.md` (17 Begriffe,
   flach, `##` = Begriff, fast alles Platzhalter) vs. Demo (`glossar-demo/glossar.md`,
   ~28 Begriffe, `##` = Abschnitt / `###` = Begriff, plus eingebettetes Chrome).
5. **Kontrolliertes Rollenvokabular als SSoT:** `issuer/recipient/witness/other`;
   Gender-Doppelpunkt-Labels aus `frontend/role_labels.py::ROLE_LABELS_PLURAL`.
6. **Sichtbarkeit:** `.dev-only` (verbergen, `?dev=1`) für offene/interne Notizen;
   Audience-Achse für strukturelle Entfernung. Keine technischen IDs im öffentlichen
   Sichttext (Beschluss 18.05.2026 A.3.2).
7. **Nav ist SSoT in `base.html`**; der Glossar-Eintrag wurde bei Platzhalter-Stand
   aus dem Projekt-Dropdown **entfernt** und muss nach Import wiederhergestellt werden.
8. **Keine hardcodierten Zahlen/Zeiträume** (SSoT `frontend/config.RELEASED_PERIOD`);
   Datenstand kommt über den geerbten Footer.
9. **Test-Pair-Pattern**; Vorlage `frontend/tests/test_glossar_demo.py`.
   `verification/` ist NICHT der Ort (nur TEI-Daten-Konsistenz).

## Content-Modell (kanonisch, für den Import verbindlich)

- `##` = **thematischer Abschnitt** (A Datenbank/Datenmodell, B Quellen/Überlieferung,
  C Rollen, D Institutionen, E Rechtsgeschäfte, F Maße/Währungen).
- `###` = **einzelner Begriff**; die Überschrift ist der **saubere kanonische Term**
  (kein Code-Alias in Klammern). Slug wird daraus via `_slug_anchor` abgeleitet.
- Absatz darunter = Definition. Rollen-Code-Alias (`issuer` etc.) steht **im Body**,
  nicht in der Überschrift (verhindert Slug-Drift wie `aussteller-in-issuer`).
- Querverweise als `[[#Term]]` / `[[#Term|Label]]`.
- Routing: **A–F → Glossar**, **G → Technik** (darf Extra-Begriffe führen, die nicht
  im Glossar stehen), **Fallbeispiele → Tutorial**.

## Pipeline (fünf Stufen)

1. **Extrahieren** — `.docx` → treuer, strukturierter Text-/Kommentar-Abzug
   (vorhandener Extraktor, als `scripts/glossar_docx_extract.py` formalisiert):
   Überschriften = Begriffe, Abschnittszuordnung A–G/Fallbeispiele.
2. **Routen & Einsetzen** — jeder Abschnitt an seine Zielseite; Prosa wird in das
   **bestehende Seiten-Gerüst** eingesetzt (Nav, Styles, Tooltip-Demo, Fall-Karten
   bleiben). Begriffs-Überschriften sauber (kanonischer Term), Aliasse in den Body.
3. **Bauen** — `python3 scripts/build_glossar_demo.py`.
4. **Verifizieren (das Gate)** — siehe unten.
5. **Sichten & Committen** — Diff prüfen, lokal committen (kein Push).

## Verifikations-Gate

- **Coverage-Manifest (deterministisch, als Skript + Test):**
  `scripts/glossar_import_coverage.py` liest den `.docx`-Extrakt und prüft, dass jeder
  Begriff/jede Überschrift als H3 auf seiner Zielseite (gemäß Routing-Config)
  erscheint. Report: **abgedeckt / fehlend / unerwartet**. Gerichtet: alle A–F müssen
  im Glossar sein; G-Extras auf Technik sind erlaubt (kein Fehler).
- **Slug-Stabilitäts-Check:** jeder Begriffs-Slug wird aus der sauberen Überschrift
  reproduziert; Klammer-Alias-Drift wird geflaggt. (Optional Abgleich gegen die
  `slug=`-Werte bestehender `tip_glossary`-Aufrufe.)
- **Terminologie-Guard:** kanonische Begriffe (Quellenkorpus, Gesamtnennung,
  Individuelle Person, „noch nicht ausgewertet") und Rollen-Codes/Labels
  (`issuer/recipient/witness/other` + `ROLE_LABELS_PLURAL`) müssen exakt geführt
  werden; Abweichungen als **Warnung**, nicht stillschweigend übernommen.
- **Keine-Hardcoded-Zahlen-Check:** Heuristik flaggt Jahres-/Mengen-Literale im
  importierten Text.
- **Fidelity-Prüfung (adversarial, wie im Demo-Workflow):** Agent vergleicht
  gerenderte Seite gegen den Extrakt (erfunden/verfälscht/paraphrasiert/ausgelassen).
- **Isolationstest:** produktive `glossary.html` bleibt unberührt (Vorlage
  `test_glossary_demo_does_not_touch_production`).

## Produktions-Konformität (bakes in)

Der Import formt so, dass ChPollins Übernahme mechanisch wird:
- Begriffs-Überschriften = kanonische Terme → **Slugs identisch** zu dem, was
  `tip_glossary(slug=…)` und `[[glossar#…]]`-Wiki-Anker der `knowledge/`-Basis
  erwarten (Slug kommt aus Text, nicht Level — H3=Begriff ist slug-kompatibel zu
  produktivem H2=Begriff).
- Terminologie/Rollen-Labels deckungsgleich mit den SSoT.
- Keine hardcodierten Zahlen/Jahre.

## Dokumentierte ChPollin-Schritte (nicht Teil unseres Imports)

Als **Runbook** übergeben, nicht selbst ausgeführt (Produktion unberührt):
- Demo-Inhalte in produktive `frontend/content/project/glossar.md` überführen.
- Glossar-**Nav-Eintrag** im Projekt-Dropdown von `base.html` wiederherstellen.
- **Chrome aus dem Content lösen:** die im Demo eingebettete `<nav class="demo-pagenav">`
  und die Inline-`<style>`-Blöcke ins Template/CSS ziehen, damit der Content rein
  redaktionell bleibt.
- `tip_glossary`-`slug=`-Werte gegen die finalen Slugs prüfen.

## Zu bauendes Tooling (jetzt, validiert am Entwurfs-.docx)

- `scripts/glossar_docx_extract.py` — `.docx` → Text/Kommentare (formalisiert).
- `scripts/glossar_import_coverage.py` — Coverage-/Slug-/Terminologie-Report,
  auch als pytest verankert.
- Routing-Config (Abschnitt → Seite), klein und explizit.
- **Import-Runbook** (Schritt-für-Schritt + die ChPollin-Schritte oben).
- **Content-Modell-Normalisierung** der bestehenden Demo: Rollen-Überschriften auf
  saubere Terme umstellen (Alias in den Body), damit Slugs produktions-konform sind.

## Deliverable

Beim finalen `.docx`: aktualisierte `.md` + **Import-Bericht** (Coverage,
Terminologie-Abgleich, Abweichungen) + Runbook. Alles lokal, kein Push.

## Guardrails / Scope

- Keine Datenschicht-/Pipeline-Änderung; produktive `glossar.md`/`glossary.html`
  unberührt.
- Nur Markdown-Content schreiben, nie `docs/` direkt.
- Keine Pushes; lokale Commits nur auf Auftrag; `.docx`-Binärdatei ungetrackt.
- Tooling unter `scripts/`; validiert gegen den vorliegenden Entwurfs-`.docx`.

## Nicht-Ziele (YAGNI)

- Kein Dauer-Sync / keine Automatisierung für viele Import-Runden.
- Keine parallele `glossar.json`-Datenstruktur.
- Keine automatische Migration in die produktive `glossar.md` (ChPollin-Schritt).
- Kein automatisches Umschreiben von `base.html`-Nav/Templates (ChPollin-Schritt).

## Offene Punkte (für Team/ChPollin, im Runbook zu vermerken)

- Aufnahmekriterium: der finale `.docx` kann mehr Begriffe liefern als heute; nimmt
  der Import alle auf oder filtert er gegen „erscheint im UI"? Default: alle
  aufnehmen, nicht-UI-Begriffe als `.dev-only` markieren.
- Sichtbarkeit der Technik-Seite (ganz intern via Audience vs. `.dev-only`-Passagen).
- Ob Klammer-Aliasse im Heading grundsätzlich verboten werden (Empfehlung: ja).
