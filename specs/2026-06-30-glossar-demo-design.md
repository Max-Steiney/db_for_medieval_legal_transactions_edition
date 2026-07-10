# Design: Drei-Seiten-Glossar (Demo-Modell)

Stand: 2026-06-30
Status: Entwurf zur Durchsicht

## Ziel

Ein **visuelles Modell** des neuen Glossars als Demo, im Stil der bestehenden
ChPollin-Seite, durchklickbar. Es zeigt, wie die drei Nutzungswege als drei
eigenständige, untereinander verlinkte Seiten umgesetzt werden. Die **finale,
nahtlose Integration ins Frontend ist ChPollins Aufgabe** (Metapher: wir liefern
dem Bauherrn das visuelle Modell und so viel Vorplanung wie sinnvoll, gebaut wird
final dort).

Inhaltsgrundlage ist das Redaktions-`.docx` des Teams
(`specs/material/glossar-entwurf.docx`, „Version nach Besprechung 18.6."). Es
enthält nahezu fertige Texte für Glossar und die drei Fallbeispiele samt
Rollen-Auflösung. Die Demo verwendet diesen **echten Inhalt** (keine generischen
Platzhalter); offene Redaktionspunkte bleiben Sache des Teams.

## Drei Personas = drei Seiten

Statt drei Ebenen in einem Eintrag werden die drei Nutzungswege als drei klar
getrennte, untereinander verlinkte Seiten umgesetzt (Entscheidung User
2026-06-30, gestützt auf Team-Kommentare #10/#11/#20 im `.docx`):

1. **Tutorial** — neue Nutzer:innen. Einstieg über die drei Fallbeispiele;
   erklärt Begriffe, Annotation und Datenlogik im Kontext echter Quellen.
2. **Glossar** — eingearbeitete Nutzer:innen. Begriffsdefinitionen (Abschnitte
   A–F des `.docx`); speist die Tooltips; gezieltes Nachschlagen.
3. **Technik / Datenmodell** — Datenbank-Interessierte. Abschnitt G des `.docx`:
   TEI-Auszeichnung, Rollen, dispositive Verben, `roleName`-Typen. Legitim
   öffentlich, weil die TEI-Tags ohnehin in der herunterladbaren XML stehen.

Jede Seite steht für sich und ist allein nutzbar; alle drei verweisen
aufeinander und auf die drei Fallbeispiele.

### Verhältnis der Seiten (konzeptuelle Hierarchie)

Das **Glossar ist der Kern** der Übung: eine Begriffsdefinitionssammlung des
Projekts, deren Hauptzweck das Füttern der Tooltips ist. **Tutorial** und
**Technik/Datenmodell** sind daraus **abgeleitete, anwendungsbezogene
Erklärungen** — sie führen Nutzer:innen in Aufbau und Technik ein, gründen aber
auf den Glossar-Definitionen. Alle Seiten verfolgen dasselbe Ziel: Fragen
beantworten. Ein **FAQ** kann später als 4. Seite anschließen (derzeit
Nicht-Ziel, aber die Struktur wird dafür offen gehalten). Die Seiten erklären
sich zu einem Grad gegenseitig und sind entsprechend verlinkt.

## Die drei Fallbeispiele (gegeben im `.docx`)

Drei real existierende, lokal bereits gerenderte Quellen
(`docs/documents/QGW/Vienna_1177-1414_ready/`):

- **Fall 1 — Nr. 604:** Verkauf „mit Handen" der Stadt. Rollen: Aussteller:innen
  (Ehepaar, `issuer`), Empfänger (`recipient`), „mit Handen" (`other`),
  Zeuge/Siegler (`witness`); Ämter (`occ`).
- **Fall 2 — Nr. 16:** Schenkung für das Seelenheil an ein Kloster. Rollen:
  Ausstellerin (`issuer`), Empfängerin/Institution (`recipient`), Siegler =
  Ehemann (`witness`/sealer).
- **Fall 3 — Nr. 1869:** Witwe vergibt Erbe. Rollen: Ausstellerin (`issuer`),
  Empfänger/Verwandter (`recipient`), Verwandtschaft (`kin`), Todesvermerk
  (`dead`), Beruf (`prof`), zwei Siegler (`witness`).

Die Fälle sind das verbindende Rückgrat: das Tutorial spielt sie durch, Glossar
und Technik referenzieren sie zur Veranschaulichung.

## Architektur & Build-Einbindung

- Drei neue, **isolierte Demo-Seiten**, durch das bestehende Build-System
  erzeugt, z. B. unter `docs/project/glossar-demo/` (`tutorial.html`,
  `glossar.html`, `technik.html`) oder als `glossar-demo-*.html`. Genaue Pfade
  bei Implementierung.
- Produktive `frontend/content/project/glossar.md` und
  `docs/project/glossary.html` bleiben **unangetastet**.
- Additiv hinzu:
  - strukturierte Inhaltsquellen für die drei Seiten (Format bei Umsetzung
    festgelegt; Inhalt stammt aus dem `.docx`),
  - Build-Funktion(en) parallel zu `_build_glossary` in
    `frontend/build/_pages.py` (kein Eingriff in Bestehendes),
  - Template(s) im Stil von `about.html`/`base.html`,
  - kleines JS nur falls nötig (z. B. Tab-/Akkordeon-Interaktion einzelner
    Bausteine; bevorzugt bestehende Muster).
- **Keine** Verlinkung in der öffentlichen Navigation. Per URL erreichbar, zur
  Übergabe gedacht.

## Seite 1 — Tutorial

Geführter Einstieg „So ist die Datenbank aufgebaut", umgesetzt als Abfolge der
drei Fallbeispiele. Pro Fall:

- kurzer Quellentext-Auszug (aus dem `.docx`),
- Auflösung der Rollen **im Kontext** (wer ist `issuer`/`recipient`/… in genau
  diesem Fall),
- Links in das **Glossar** (Begriffsbedeutung) und in die **Technik**-Seite
  (wie die Rolle ausgezeichnet wird),
- Link auf die echte gerenderte Quelle (604/16/1869).

Vorgabe #22: In den Fallbeispielen **nicht generisch gendern**, sondern die
Rollen exakt wie im Original wiedergeben (z. B. „Ausstellerin" für Benedicta de
Arnstain in Fall 2; Plural nur wo tatsächlich mehrere/gemischt).

## Seite 2 — Glossar

Die Begriffe der Abschnitte A–F des `.docx` als Referenz. Pro Eintrag:

- **Titel** und **Kurzdefinition** (1–2 Sätze). Die Kurzdefinition ist zugleich
  der Tooltip-Text (Single Source, siehe unten).
- ggf. erläuternder Zusatz, Querverweise auf verwandte Begriffe,
- Links zur **Technik**-Seite (wo ein Begriff eine TEI-Entsprechung hat) und zu
  den **Fallbeispielen**.

Redaktionsvorgaben aus den Kommentaren, soweit darstellungsrelevant:
- #6: „Event/Ereignis" auch als Entität benennen.
- #7: bei „Attribut" Verwandtschaft als Beispiel entfernen (gehört als `kin`
  zur Technik-Seite); stattdessen z. B. Geschlecht/Beruf/Titel.
- #13/#14: Zeug:in und Siegler:in **getrennt** beschreiben, nicht „zusammen-
  führen"; der gemeinsame Code-Wert `witness` wird auf der Technik-Seite
  erklärt, nicht in der Prosa verschmolzen.

## Seite 3 — Technik / Datenmodell

Abschnitt G des `.docx`:

- **Rollen** `rs type="fn" role="…"`: `issuer`, `recipient`, `witness`,
  `other` — je mit Kurzdefinition und Bezug zu den Fallbeispielen.
- **Dispositive Verben** (`triggerstring n="disp"`): typisierende Aktionswörter.
- **`roleName`-Typen**: Attribute (`prof`, `title`, `dead`) vs. Relationen
  (`kin`, `rep`, `occ`, `title_ref`).
- XML-Schnipsel zur Veranschaulichung, Verweis auf den TEI-Download der Quellen.
- Erklärung der `witness`-Zusammenfassung (siehe #12/#13): siegelnde Zeugen und
  siegelnde Aussteller:innen werden als das Rechtsgeschäft beglaubigende
  Personen erfasst; die beiden Rollen werden dennoch getrennt beschrieben.

## Tooltip-Kopplung sichtbar machen

Ein Demonstrations-Callout (auf der Glossar-Seite) „So erscheint dieser Begriff
als Tooltip im UI" zeigt den echten `tip_glossary`-Popover mit der
Kurzdefinition. Umsetzungs-Empfehlung an ChPollin: Kurzdefinition künftig
**einmal** in der Glossar-Quelle pflegen und daraus den Tooltip speisen (heute
stehen die Tooltip-Texte inline in den Templates via `tip_glossary`/`caller()`).

## Offene Redaktionspunkte (Kommentare)

Inhaltlich offene Punkte (z. B. #5 Neschwara-Referenz, #8 Register-Abgrenzung,
#9 Abgleich mit Ad Fontes, #16/#17 Referenz-Sammlungen) bleiben **Sache des
Teams** und werden nicht selbst entschieden. Optional: solche Stellen im Modell
als dezente `.dev-only`-Redaktionsnotiz markieren (nur unter `?dev=1` sichtbar),
damit Team und ChPollin die offenen Punkte im Modell wiederfinden.

## Stil, JS, Tests

- Native Einbettung: `base.html`, bestehendes Seiten-CSS; vorhandene
  Interaktionsmuster (Tabs/Tooltips) wiederverwenden statt neu erfinden.
- **Regressionstest(s)** in `frontend/tests/` (Pflicht laut CLAUDE.md):
  - Die drei Demo-Seiten bauen ohne Fehler.
  - Querverlinkung vorhanden: Tutorial → Glossar/Technik; Glossar ↔ Technik;
    alle → Fallbeispiele.
  - Die drei Fall-Links zeigen auf existierende Dokument-Seiten (604/16/1869).
  - Single-Source-Invariante: Glossar-Kurzdefinition == Tooltip-Text.

## Guardrails / Scope

- **Keine** Änderungen an Datenschicht oder Pipeline (Schwester-Repos
  read-only / unangetastet).
- **Keine** Pushes; lokale Commits nur auf ausdrücklichen Auftrag.
- Produktives Glossar (`glossar.md`, `glossary.html`) unberührt.
- `docs/` nur über den Build erzeugen, nicht direkt editieren.
- Keine redaktionellen Endtexte erfinden; offene Kommentarpunkte dem Team
  überlassen.

## Build-Pfad (geklärt am 2026-06-30)

Der fest verdrahtete Pfad `../db_for_medieval_legal_transactions` (KGruenwald)
enthält **kein** `pipeline`-Paket; der Voll-Build (`python -m frontend build`)
läuft hier nicht (zudem fehlen die Pipeline-CSVs). Lösung für den content-/
template-getriebenen Demo-Build:

- `pipeline.config` aus dem `_MS_Test`-Fork (read-only) importieren, indem ein
  **Runner-Skript** (`scripts/build_glossar_demo.py`) `_MS_Test` auf `sys.path`
  legt. `frontend/__init__.py` bleibt unverändert.
- Build-Deps (`jinja2`, `markdown`, `pytest`, `pygments`) sind per `pip --user`
  installiert (User-Site, kein System-Eingriff).
- Verifiziert: Jinja-Env, `about.html`, Markdown-Render, voller Content-Page-
  Render und `pytest`-Discovery (562 Tests) laufen mit
  `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test`.
- Die Demo braucht **keine** Pipeline-CSVs (`pipeline/output`).

## Nicht-Ziele (YAGNI)

- Kein globaler Persona-Umschalter.
- Keine flächendeckende Umverdrahtung aller Tooltips der Seite.
- Keine redaktionellen Endtexte (liefert das Team).
- Keine Integration in die öffentliche Navigation.
