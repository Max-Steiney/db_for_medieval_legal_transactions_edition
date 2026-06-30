<nav class="demo-pagenav">
  <strong>Glossar</strong> ·
  <a href="tutorial.html">Tutorial</a> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

<style>
.demo-pagenav{font-size:.9rem;margin:0 0 1.5rem;padding:.6rem .8rem;background:var(--color-bg-warm,#f6f3ec);border-radius:6px}
.demo-tip-demo{border:1px solid var(--color-border,#d8d2c4);border-radius:8px;padding:1rem;margin:1.5rem 0;background:var(--color-bg-warm,#f6f3ec)}
.demo-tip-demo .tip-popover{position:static;display:block;max-width:340px;box-shadow:0 1px 4px rgba(0,0,0,.12);background:#fff;border:1px solid #d8d2c4;border-radius:6px;padding:0}
.demo-tip-demo .tip-head{display:flex;justify-content:space-between;align-items:center;padding:.5rem .8rem;border-bottom:1px solid #e7e2d6}
.demo-tip-demo .tip-title{margin:0;font-size:1rem}
.demo-tip-demo .tip-body{padding:.6rem .8rem;font-size:.9rem}
.demo-tip-demo .tip-link{display:inline-block;margin-top:.4rem;font-size:.85rem}
.demo-editnote{border-left:3px solid #e0a800;background:#fff8e1;padding:.5rem .8rem;margin:.6rem 0;font-size:.85rem}
.demo-xref{font-size:.85rem;color:var(--color-text-muted,#6b6356);margin:0 0 .5rem}
.dev-only{display:none !important}
.dev-mode .dev-only{display:block !important;border:2px solid #e0b000;background:#fffbe6;padding:.5rem .75rem;margin:.75rem 0;border-radius:4px}
</style>

Das Glossar ist der Kern dieses Modells: eine Begriffsdefinitionssammlung des
Projekts, die zugleich die Tooltips im UI speist. Anwendungsbezogene
Erklärungen finden sich im [Tutorial](tutorial.html), die TEI-Auszeichnung und
das vollständige Rollenvokabular auf der Seite
[Technik / Datenmodell](technik.html).

Die Begriffe sind in zwei Abschnitte gegliedert: **A. Datenbank und Datenmodell**
und **B. Quellen und Überlieferung**.

## A. Datenbank und Datenmodell

### Quelle

Eine einzelne historische Quelle, die in der Datenbank erfasst wurde. Im Projekt
„Stadt und Gemeinschaft" handelt es sich vor allem um Urkunden und
Stadtbucheinträge.

So erscheint ein Glossar-Begriff als Tooltip im UI – dieselbe Definition, gekoppelt
an das i-Symbol im Fließtext:

<div class="demo-tip-demo">
  <p class="demo-xref">Tooltip-Vorschau (echtes Popover-Markup):</p>
  <aside class="tip-popover tip-popover--glossary" role="dialog" aria-hidden="false" aria-label="Definition: Quelle">
    <header class="tip-head"><h3 class="tip-title">Quelle</h3></header>
    <div class="tip-body">Eine einzelne historische Quelle, die in der Datenbank erfasst wurde. Im Projekt „Stadt und Gemeinschaft" handelt es sich vor allem um Urkunden und Stadtbucheinträge.<a class="tip-link" href="glossar.html#quelle">im Glossar</a></div>
  </aside>
</div>

### Quellenkorpus

Eine Sammlung zusammengehöriger Quellen, im Fall des Projekts „Stadt und
Gemeinschaft" handelt es sich derzeit um Regesten aus den „Quellen zur Geschichte
der Stadt Wien" (Uhlirz) und Einträge aus dem ersten Band der Wiener Stadtbücher
1395–1400 (hrsg. von Jaritz/Brauneder). Künftig werden weitere Korpora
hinzukommen, z.B. Grundbücher.

Öffentlich zugänglich sind die erfassten Daten aus den Regesten im Band II.1 und
II.2 der QGW von 1177 bis 1414. Es handelt sich dabei um Regesten von Urkunden im
Wiener Stadt- und Landesarchiv. Auf monasterium.net sind sowohl die Regesten als
auch Digitalisate der Urkunden zugänglich.

Die Wiener Stadtbücher sind ein von der Stadtverwaltung geführtes Register, in dem
Rechtsgeschäfte, letztwillige Verfügungen und andere Vorgänge eingetragen wurden.
Ein Stadtbucheintrag ist ein einzelner Eintrag innerhalb der Wiener Stadtbücher.

<div class="demo-editnote dev-only">Redaktion offen (#0–#5): QGW- und Stadtbuch-Unterpunkte ausführen oder nur ins Wien-Wiki verlinken; Neschwara-Referenz und Jaritz/Brauneder-Definition aus Band 1 noch einarbeiten.</div>

### Event / Ereignis

Die grundlegende Analyseeinheit der Datenbank. Ein Event entspricht einem in
einer Quelle dokumentierten Vorgang – oft ein Rechtsgeschäft, etwa ein Verkauf,
eine Stiftung, eine letztwillige Verfügung oder ein Gerichtsverfahren.

<div class="demo-editnote dev-only">Redaktion (#6): Ereignis/Event als Entität des Datenmodells benennen (Kommentar #6, Lutter et al. 2021, insb. Abb. 2). Achtung: Die Entität-Definition im nächsten Abschnitt umfasst laut Extrakt Zeile 20 nur Personen/Organisationen (künftig Orte); eine stillschweigende Erweiterung um Ereignisse dort würde der Definition widersprechen. Inhaltliche Klärung steht noch aus.</div>

### Factoid

Eine einzelne strukturierte Information, die aus einer Quelle gewonnen wurde und
der Quelle zugeordnet bleibt; auch widersprüchliche Angaben bleiben enthalten.
Factoids ermöglichen es, Personen, Orte, Organisationen und ihre Beziehungen
systematisch auszuwerten.

### Annotation

Eine Markierung im Quellentext, mit der Informationen wie Personen,
Organisationen, Orte und ihre Eigenschaften ausgezeichnet werden – im Fall des
Projekts „Stadt und Gemeinschaft" handelt es sich dabei um in digitale
Textdateien umgewandelte Regesten und Stadtbucheinträge, die nach den Standards
der TEI annotiert/codiert wurden.

### Entität

Personen oder Organisationen (künftig auch Orte), die in einer Quelle genannt
werden und als eigener Datensatz in der Datenbank erfasst sind.

### Rolle

Die Funktion, die eine Person oder Organisation innerhalb eines bestimmten
Ereignisses einnimmt. Dieselbe Person kann in einer oder mehreren Quellen
verschiedene Rollen einnehmen. Das kontrollierte Rollenvokabular und seine
Code-Werte werden auf der Seite [Technik / Datenmodell](technik.html#rollen)
erläutert.

### Beziehung

Eine Verbindung zwischen zwei Entitäten, etwa eine Verwandtschaftsbeziehung oder
eine Amtszugehörigkeit.

### Attribut

Eine Eigenschaft einer Entität, beispielsweise ein Beruf, ein Titel oder ein
Status.

<div class="demo-editnote dev-only">Redaktion (#7): „Verwandtschaftsbeziehung" gestrichen – kin ist eine Relation und gehört in die saubere Trennung Attribute (prof/title/dead) vs. Relationen (kin/rep/occ/title_ref) auf der <a href="technik.html#rollen">Technik-Seite</a>. Als Attribut-Beispiele: Beruf (prof), Titel (title), Status (dead: Todesfloskel „selig", „weilent") — alle drei im Extrakt Zeilen 154–156 belegt.</div>

### Verknüpfung

Die technische Verknüpfung von Informationen innerhalb der Datenbank,
beispielsweise zwischen einer Person und den Quellen, in denen sie erwähnt wird.

### Register

Ein Verzeichnis von Personen, Organisationen oder Orten, die in den Quellen
vorkommen, in unserem Fall insbesondere die Register der Quellen zur Geschichte
der Stadt Wien (hrsg. von Karl Uhlirz), ergänzend auch Werke wie „Die Wiener
Ratsbürger 1396–1526" (hrsg. von Richard Perger).

<div class="demo-editnote dev-only">Redaktion offen (#8): Zusatz, dass im Prozess dieses Projekts selbst Register (persons / organisations / places / events) erstellt werden, gegen die Begriffsverwendung auf der Projektwebsite abgleichen.</div>

### Normierung

Die Vereinheitlichung zeitgenössisch variabler Schreibweisen oder Bezeichnungen,
um Informationen systematisch durchsuchen und auswerten zu können, beispielsweise
der Begriff Bürger/Bürgerin, der unter anderem auch in den Schreibweisen
purger/purgerin oder civis wiennensis vorkommt.

## B. Quellen und Überlieferung

<div class="demo-editnote dev-only">Redaktion offen (#9): Abschnitt B überarbeiten und mit Ad Fontes abgleichen; die ad-fontes-Links pro Begriff ergänzen.</div>

### Urkunde

Ein schriftliches, beglaubigtes Dokument, das ein Rechtsgeschäft, einen
Rechtsanspruch oder eine rechtlich relevante Handlung festhält.

### Regest

Eine knappe Inhaltsangabe einer historischen Quelle, die wichtige Informationen
zusammenfasst.

### Edition

Eine wissenschaftliche Veröffentlichung historischer Quellen, meist mit
Transkriptionen, Kommentaren und Erläuterungen.

### Digitalisat

Eine digitale Aufnahme einer historischen Quelle.

### Transkription

Die buchstabengetreue Übertragung eines historischen Textes in moderne Schrift.

### Siegel

Ein Beglaubigungsmittel, mit dem die Echtheit einer Urkunde und die beteiligten
Personen bestätigt wurden.

### Vidimus / Vidimierung

Die rechtsgültige Bestätigung, dass eine Abschrift dem Original entspricht.

## Rollen in Rechtsgeschäften

Die folgenden Funktionsrollen werden hier nur kurz eingeführt; ihre
Code-Werte und die TEI-Auszeichnung stehen auf der Seite
[Technik / Datenmodell](technik.html#rollen). Konkrete Quellen mit aufgelösten
Rollen zeigt das [Tutorial](tutorial.html).

### Aussteller:in (issuer)

Die Person oder Organisation, die verfügt oder erklärt. Bei einem Verkauf ist
dies meist die verkaufende Person, bei einem Testament die testierende Person.

### Empfänger:in (recipient)

Die Person oder Organisation, die eine Leistung, ein Recht oder einen Gegenstand
erhält.

### Zeug:in (witness)

Eine Person, die ein Rechtsgeschäft bezeugt und dadurch dessen Gültigkeit stärkt.

### Siegler:in (witness)

Eine Person oder Institution, deren Siegel zur Beglaubigung eines Dokuments
verwendet wurde.

<div class="demo-editnote dev-only">Redaktion (#13/#14): Zeug:in und Siegler:in werden getrennt beschrieben – die Funktionen sind vergleichbar, aber nicht dieselben. Der gemeinsame Code-Wert <code>witness</code> und der Auswertungsmodus (siegelnde Zeugen und siegelnde Aussteller:innen als beglaubigende Personen) werden auf der <a href="technik.html#rollen">Technik-Seite</a> erklärt.</div>

### Einbringer:in

Eine Person, die ein Rechtsgeschäft oder eine letztwillige Verfügung dem Rat
oder einer anderen Autorität vorlegt und dessen Anerkennung veranlasst.

### Erblasser:in

Die Person, deren Vermögen nach ihrem Tod nach ihrem Willen verteilt wird.

### Testamentsvollstrecker:in

Eine Person, die mit der Durchführung einer letztwilligen Verfügung beauftragt
ist.

### Grundherr:in („mit Handen", other)

Die Person oder Institution, die einem Rechtsgeschäft als betroffene
Grundherrschaft zustimmt. Wer ein Haus oder ein Burgrecht veräußert, tut dies
„mit Handen" des Grundherrn bzw. der Grundherrin – neben individuellen Personen
ist das oft der Stadtrat oder eine geistliche Institution. Im Datenmodell gehört
diese Funktion zur Sammelrolle other.

---

Querverweise: [Tutorial](tutorial.html) · [Technik / Datenmodell](technik.html)
