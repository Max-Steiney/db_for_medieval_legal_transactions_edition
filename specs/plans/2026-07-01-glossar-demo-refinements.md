# Glossar-Demo Refinements (Sichtungs-Feedback 2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vier Sichtungs-Punkte umsetzen — Tooltip-Vorschau richtig positionieren, Glossar-Abschnitte D/E/F aus dem Entwurfs-.docx ergänzen, interne Verlinkung auch für gebeugte Formen, und das Tutorial zu einem geführten Rundgang ausbauen.

**Architecture:** Rein content-/CSS-getrieben, wie die bisherige Demo. Neue Begriffe folgen dem Content-Modell (`##` Abschnitt / `###` Begriff / Definition / `.entry-refs`-Zeilen); interne Links über `[[#Term|Label]]`; Tooltip-Fix in `glossar-demo.css`; Tutorial als Markdown mit Cross-Page-Links ins Glossar.

**Tech Stack:** Markdown (attr_list, toc), Jinja2, pytest. Build-Deps per `pip --user` installiert.

## Global Constraints

- **Produktion unberührt:** nur `frontend/content/project/glossar-demo/*.md`, `frontend/static/css/glossar-demo.css`, `frontend/tests/test_glossar_demo.py`. NICHT `glossar.md`/`glossary.html` der Produktion, nicht `technik.md` außer wo genannt.
- **`docs/` ist Build-Output:** nur via `python3 scripts/build_glossar_demo.py`. `python -m frontend build` läuft hier NICHT.
- **Tests:** `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`.
- **Keine Pushes; lokale Commits.**
- **Inhaltsquelle:** `specs/material/glossar-entwurf.txt`, Abschnitte D/E/F (Prosa wörtlich/eng übernehmen, nichts erfinden).
- **Gender-Doppelpunkt:** der `.docx` nutzt Gender-Stern (`Bürger*in`); im Frontend wird durchgängig Gender-Doppelpunkt geschrieben (`Bürger:in`, `Hofmeister:in`). Kein `*in` im Sichttext.
- **Referenz-Zeilen:** bestehende `.entry-refs`-Konvention (ein Absatz, Zeilen mit hartem Umbruch = zwei Leerzeichen, `{: .entry-refs }` in der letzten Zeile; steht VOR einer etwaigen `dev-only`-Notiz). Interne Links nur auf saubere Slugs.

---

## File Structure

- `frontend/static/css/glossar-demo.css` — Tooltip-Vorschau-Positionierung fixen.
- `frontend/content/project/glossar-demo/glossar.md` — Abschnitte D/E/F ergänzen; gebeugte interne Links setzen.
- `frontend/content/project/glossar-demo/tutorial.md` — geführter Rundgang.
- `frontend/tests/test_glossar_demo.py` — neue Tests.

Externe Referenzen für D/E/F (aus dem Extrakt), exakt:
- Wien-Wiki Schranne: `https://www.geschichtewiki.wien.gv.at/Schranne`
- Wien-Wiki Kaufkraftrechner: `https://www.geschichtewiki.wien.gv.at/Kaufkraftrechner`
- Literatur Währung/Maße: `Geyer, Münze und Geld (Wien 1938)` und `Ertl, Wien 1448 (Wien/Köln/Weimar 2020)`
- Literatur Burgrecht/Grundzins: `Czeike, Das „Burgrecht" in Wien im 15. Jahrhundert (JbVGStW 10, 1952/53)`
- Literatur Letztwillige Verfügung: `Brauneder/Jaritz (Hg.), Die Wiener Stadtbücher 1395–1430, Teil 1, FRA III/10 (Wien/Köln 1989), S. 17`

---

## Task 1: Tooltip-Vorschau richtig positionieren

Die echte `tip.css` setzt `.tip-popover { position:absolute; left:50%; transform:translateX(-50%); animation:tip-fade-in }`. Unser Demo-Override setzt nur `position:static`, resettet aber `transform`/`animation`/`top`/`left` nicht — dadurch wird das Popover um die halbe Breite nach links geschoben (linke Kante aus dem beigen Fenster).

**Files:**
- Modify: `frontend/static/css/glossar-demo.css` (`.demo-tip-demo .tip-popover`)
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: bestehendes `.demo-tip-demo .tip-popover`-Regelset.
- Produces: korrekt im Container sitzende Tooltip-Vorschau.

- [ ] **Step 1: Failing test ergänzen**

```python
def test_tooltip_preview_reset_positioning():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "css" / "glossar-demo.css").read_text(encoding="utf-8")
    # Der Demo-Override muss die absolute-Positionierung der echten tip.css neutralisieren
    block = css.split(".demo-tip-demo .tip-popover", 1)[-1].split("}", 1)[0]
    assert "transform: none" in block
    assert "animation: none" in block
    assert "left: auto" in block
```

- [ ] **Step 2: Test ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k tooltip_preview_reset`
Expected: FAIL.

- [ ] **Step 3: Override ergänzen**

In `frontend/static/css/glossar-demo.css` die Regel `.demo-tip-demo .tip-popover { … }` um die Reset-Deklarationen erweitern (innerhalb des bestehenden Blocks, zusätzlich zu `position: static; display: block;`):
```css
    position: static;
    top: auto;
    left: auto;
    transform: none;
    animation: none;
    min-width: 0;
```
Und den Pfeil der echten Popover-Optik in der Vorschau ausblenden — direkt nach dem Block ergänzen:
```css
.demo-tip-demo .tip-popover::before { display: none; }
```

- [ ] **Step 4: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Sichtprüfung**

`docs/project/glossar-demo/glossar.html` lokal ansehen: die Tooltip-Vorschau sitzt jetzt vollständig im beigen Kasten.

- [ ] **Step 6: Commit**

```bash
git add frontend/static/css/glossar-demo.css frontend/tests/test_glossar_demo.py docs/project/glossar-demo docs/static/css/glossar-demo.css
git commit -m "fix(glossar-demo): Tooltip-Vorschau korrekt im Container positionieren

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Glossar-Abschnitte D/E/F ergänzen

**Files:**
- Modify: `frontend/content/project/glossar-demo/glossar.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: Content-Modell + `.entry-refs`-Konvention aus dem Bestand.
- Produces: drei neue `##`-Abschnitte mit `###`-Begriffen und Referenz-Zeilen.

- [ ] **Step 1: Failing tests ergänzen**

```python
def test_glossar_has_sections_def(built_demo):
    c = built_demo["glossar"]
    for term in ("Stadtrat", "Bürgermeister", "Richter", "Bürgerschranne",
                 "Rechtsgeschäft", "Verkauf", "Schenkung", "Stiftung",
                 "Verpfändung", "Darlehen", "Urteil",
                 "Wiener Pfennig", "Gulden", "Joch", "Burgrecht"):
        assert term in c, term


def test_glossar_def_references(built_demo):
    c = built_demo["glossar"]
    assert "Czeike" in c
    assert ("Geyer" in c) or ("Ertl" in c)
    assert "geschichtewiki.wien.gv.at/Schranne" in c
    assert "geschichtewiki.wien.gv.at/Kaufkraftrechner" in c


def test_glossar_gender_doppelpunkt():
    from pathlib import Path
    md = (Path(__file__).resolve().parents[1] / "content" / "project" / "glossar-demo" / "glossar.md").read_text(encoding="utf-8")
    assert "*in" not in md  # kein Gender-Stern aus dem .docx
    assert "Bürger:in" in md
```

- [ ] **Step 2: Tests ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k "sections_def or def_references or gender_doppelpunkt"`
Expected: FAIL.

- [ ] **Step 3: Abschnitt D ergänzen**

Am Ende von `glossar.md` (nach dem bestehenden Inhalt, vor dem finalen `---`/Querverweise-Footer) anfügen. Prosa aus `specs/material/glossar-entwurf.txt` Abschnitt D. Gender-Doppelpunkt.
```markdown
## D. Historische Institutionen und Personengruppen

### Stadtrat
Das zentrale politische Entscheidungsgremium einer mittelalterlichen Stadt.

### Bürgermeister
Der gewählte Vorsitzende/führende Vertreter des [[#Stadtrat|Stadtrats]].

### Richter
Vorsteher des Stadtgerichts. Sein Bestellungsmodus war im Untersuchungszeitraum
des Projekts immer wieder umstritten; prinzipiell galt er als städtisches Amt mit
landesfürstlicher Bestellung.

### Bürger:in
Eine Person mit Bürgerrecht in einer Stadt.

### Hofmeister:in
Ein:e Verwalter:in eines größeren Haushalts oder Besitzkomplexes.

### Bürgerschranne
Sitz des Stadtgerichts der Stadt Wien.

**Weiterführend:** [Wien-Wiki: Schranne](https://www.geschichtewiki.wien.gv.at/Schranne)
{: .entry-refs }
```

- [ ] **Step 4: Abschnitt E ergänzen**

```markdown
## E. Rechtsgeschäfte

### Rechtsgeschäft
Eine Willenserklärung mit rechtlich relevanten Folgen zwischen Personen oder
Institutionen. Im Datenmodell ist ein Rechtsgeschäft der häufigste Typ eines
[Events](glossar.html#event).

### Verkauf
Die Übertragung eines Gutes gegen Bezahlung.

### Schenkung
Die unentgeltliche Übertragung eines Gutes.

### Stiftung
Die dauerhafte Zuwendung von Besitz oder Einkünften für einen bestimmten Zweck,
häufig religiöser Art (Gebetsgedenken/memoria für das Seelenheil).

### Letztwillige Verfügung
Eine Verfügung über den Nachlass für die Zeit nach dem Tod (zeitgenössisch
„Geschäft").

**Literatur:** Brauneder/Jaritz (Hg.), Die Wiener Stadtbücher 1395–1430, Teil 1, FRA III/10 (Wien/Köln 1989), S. 17
{: .entry-refs }

### Verpfändung
Die Überlassung eines Gutes als Sicherheit für eine Forderung.

### Darlehen
Die zeitweise Überlassung von Geld oder Gütern gegen Rückgabe.

### Urteil
Die Entscheidung eines Gerichts oder einer anderen rechtsprechenden Instanz.

### Offener Brief
Eine [[#Urkunde]], die nicht verschlossen ausgestellt wurde und öffentlich
vorgelegt werden konnte.
```

- [ ] **Step 5: Abschnitt F ergänzen**

Prosa aus Extrakt Abschnitt F; Beträge/Umrechnungen übernehmen. Struktur:
```markdown
## F. Maße, Währungen und Besitzrecht

### Wiener Pfennig
Der denarius (`d.` / `Wr. Pf.`) war die einzige tatsächlich ausgemünzte
Umlaufwährung und – neben Naturalien – Basis des Alltagsverkehrs; über das ganze
15. Jahrhundert die maßgebliche Bezugsgröße.

**Weiterführend:** [Wien-Wiki: Kaufkraftrechner](https://www.geschichtewiki.wien.gv.at/Kaufkraftrechner)
**Literatur:** Geyer, Münze und Geld (Wien 1938); Ertl, Wien 1448 (Wien/Köln/Weimar 2020)
{: .entry-refs }

### Pfund und Schilling
Recheneinheiten (nicht geprägt): 1 Pfund (`lb.`, libra) = 240 denarii;
1 Schilling (`ß.`/`s.`, solidus) = 30 denarii. Das Pfund diente auch als
Gewichtseinheit.

### Gulden
Goldmünze (florenus) als „Oberwährung": der ungarische (`fl. ung.`) und der
rheinische Gulden (`fl. rh.`) dienten wegen ihres konstanten Metallwerts als
Maßstab bei größeren Zahlungen.

### Kreuzer und Groschen
Spätere Silbermünzen (späteres 15. Jh.): Kreuzer = 4 Pfennig; Groschen =
zunächst 2 Kreuzer. Sie verdrängten den Pfennig nach der „Schinderlingszeit"
zunehmend, lösten ihn als Recheneinheit aber nicht ab.

### Joch
Flächenmaß für ländlichen Boden; in Wien nutzungsabhängig: bei Weingärten 3.200
Quadratklafter (≈ 1,15 ha), bei Äckern 1.600 Quadratklafter (≈ 0,58 ha).

### Tagwerk
Flächenmaß nach Arbeitszeit bemessen; in Wien entspricht dies einem [[#Joch]].

### Quadratklafter
Grundeinheit der Flächenberechnung, ≈ 3,6 m²; die Klafter ist zugleich das
zugrunde liegende Längenmaß.

### Wiener Pfund (Gewicht) und Zentner
Ein Wiener Pfund sind ca. 0,56 kg; ein Zentner (100 Wiener Pfund) ca. 56 kg
(für schwere Waren).

### Grundzins / Grunddienst
Eine regelmäßig zu entrichtende Abgabe für die Nutzung eines Grundstücks — die
ursprüngliche Belastung aus dem Bodenleihe-/Besitzverhältnis.

### Burgrecht
Eine durch ein Geld-/Rentengeschäft neu geschaffene Rente: Gläubiger:innen
(„Käufer:innen") überlassen den Grundbesitzer:innen („Verkäufer:innen") Kapital
und beziehen dafür einen jährlichen Zins (meist 8–12,5 %). Das Burgrecht tritt
als zweite Belastung neben den Grunddienst.

**Literatur:** Czeike, Das „Burgrecht" in Wien im 15. Jahrhundert (JbVGStW 10, 1952/53)
{: .entry-refs }
```

- [ ] **Step 6: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add frontend/content/project/glossar-demo/glossar.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Abschnitte D/E/F aus dem Entwurf ergaenzt

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Interne Verlinkung gebeugter Formen

Auch nicht-1:1-Nennungen anderer Glossarbegriffe verlinken (Label-Form `[[#Term|Wort]]`). Konkretes Beispiel des Users: im Eintrag „Beziehung" soll „Entitäten" auf den Eintrag „Entität" verweisen.

**Files:**
- Modify: `frontend/content/project/glossar-demo/glossar.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: Task 2 (neue Begriffe existieren als Linkziele).
- Produces: gebeugte interne Links über die Label-Form.

- [ ] **Step 1: Failing test ergänzen**

```python
def test_beziehung_links_to_entitat(built_demo):
    c = built_demo["glossar"]
    idx = c.find(">Beziehung<")
    assert idx != -1, "Beziehung-Heading fehlt"
    seg = c[idx:idx + 500]
    assert 'href="#entitat"' in seg, "Beziehung verlinkt nicht auf Entität"
```

- [ ] **Step 2: Test ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k beziehung_links`
Expected: FAIL.

- [ ] **Step 3: Gebeugte Links setzen**

Im Eintrag „Beziehung" die Nennung „zwei Entitäten" als `[[#Entität|Entitäten]]` verlinken:
```markdown
Eine Verbindung zwischen zwei [[#Entität|Entitäten]], etwa eine
Verwandtschaftsbeziehung oder eine Amtszugehörigkeit.
```
Zusätzlich, wo es sich im Lesefluss anbietet (Erstnennung, gebeugte Form erlaubt), weitere klare Fälle setzen — z. B.:
- Verknüpfung: „… zwischen einer Person und den [[#Quelle|Quellen]] …"
- Attribut: „Eine Eigenschaft einer [[#Entität]] …"
Nur eindeutige Fälle, nicht jede Nennung.

- [ ] **Step 4: Bauen + Tests ausführen**

Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/content/project/glossar-demo/glossar.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): interne Verlinkung auch fuer gebeugte Formen

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Tutorial als geführter Rundgang

**Files:**
- Modify: `frontend/content/project/glossar-demo/tutorial.md`
- Test: `frontend/tests/test_glossar_demo.py`

**Interfaces:**
- Consumes: bestehende Tutorial-Struktur (Intro „So funktioniert die Datenbank" + drei `demo-case`-Karten). Cross-Page-Links `glossar.html#slug`.
- Produces: erweiterte, führende Erklär-Struktur.

- [ ] **Step 1: Failing test ergänzen**

```python
def test_tutorial_guided_tour(built_demo):
    c = built_demo["tutorial"]
    for marker in ("Was ist diese Datenbank",
                   "Wie lese ich eine annotierte Quelle",
                   "Wie geht es weiter"):
        assert marker in c, marker
    # die drei Fall-Rahmungen bleiben erhalten
    assert c.count("Was dieser Fall zeigt") == 3
```

- [ ] **Step 2: Test ausführen, Fehlschlag bestätigen**

Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q -k guided_tour`
Expected: FAIL.

- [ ] **Step 3: Tutorial ausbauen**

In `frontend/content/project/glossar-demo/tutorial.md` den Rundgang ergänzen. Bestehende Einleitung „## So funktioniert die Datenbank" und die drei Fall-Karten (mit „Was dieser Fall zeigt") bleiben; davor/dazwischen führende Abschnitte einfügen. Neue `##`-Abschnitte (erklärender Demo-Text, für neue Nutzer:innen; Cross-Page-Links ins Glossar):

- `## Was ist diese Datenbank?` — kurz: Sammlung mittelalterlicher Wiener Rechtsgeschäfte, aus Regesten und Stadtbucheinträgen erschlossen; Ziel: Personen, Organisationen und ihre Rechtsgeschäfte systematisch durchsuch- und auswertbar machen. Verlinke [Quelle](glossar.html#quelle), [Regest](glossar.html#regest).
- (bestehend) `## So funktioniert die Datenbank` — Datenlogik (Event/Rolle/Entität).
- `## Wie lese ich eine annotierte Quelle?` — erklären, dass im Quellentext Personen/Organisationen/Orte ausgezeichnet („annotiert") sind, dass jede Person eine [Rolle](glossar.html#rolle) im Geschäft hat, und dass die technische Auszeichnung auf der [Technik-Seite](technik.html) steht. Hinweis auf die herunterladbare TEI-XML jeder Quelle.
- (bestehend) die drei Fallbeispiel-Karten als Lektionen.
- `## Wie geht es weiter?` — Verweise: Begriffe im [Glossar](glossar.html) nachschlagen, technischer Aufbau auf der [Technik-Seite](technik.html); Einladung, selbst eine Quelle zu öffnen.

Der Text soll neue Nutzer:innen wirklich durchführen (nicht nur auflisten); ganze Sätze, freundlicher, erklärender Ton.

- [ ] **Step 4: Anker prüfen, bauen, testen**

Nach dem Bau prüfen, dass die verwendeten Glossar-Anker existieren:
`grep -oE 'id="(quelle|regest|rolle|event|entitat)"' docs/project/glossar-demo/glossar.html`
Run: `python3 scripts/build_glossar_demo.py`
Run: `PYTHONPATH=../db_for_medieval_legal_transactions_MS_Test python3 -m pytest frontend/tests/test_glossar_demo.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/content/project/glossar-demo/tutorial.md frontend/tests/test_glossar_demo.py docs/project/glossar-demo
git commit -m "feat(glossar-demo): Tutorial als gefuehrter Rundgang ausgebaut

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review (ausgefüllt)

**Spec/Feedback coverage:**
- Punkt 1 (Tooltip schief) → Task 1 (CSS-Reset transform/animation/left) + Test. ✓
- Punkt 2 (D/E/F fehlen) → Task 2 (drei Abschnitte aus dem Entwurf, Referenzen, Gender-Doppelpunkt) + Tests. ✓
- Punkt 3 (gebeugte Verlinkung, Beziehung→Entität) → Task 3 (Label-Form-Links) + Test. ✓
- Punkt 4 (Tutorial ausbauen) → Task 4 (geführter Rundgang) + Test. ✓
- Produktions-Isolation bleibt (nur Demo-Dateien) — `test_glossary_demo_does_not_touch_production` grün. ✓

**Placeholder scan:** Tests + CSS sind vollständiger Code; D/E/F-Inhalte sind konkret vorgegeben (Prosa aus dem benannten Extrakt-Abschnitt, exakte URLs/Literatur). Tutorial-Abschnitte mit klarer Vorgabe je Abschnitt.

**Type/Slug consistency:** interne Links nur auf saubere Slugs (`#entitat`, `#quelle`, `#joch`, `#stadtrat`); Cross-Page-Links im Tutorial auf verifizierte Glossar-Anker; `.entry-refs`-Muster identisch zum Bestand; Gender-Doppelpunkt durchgängig.
