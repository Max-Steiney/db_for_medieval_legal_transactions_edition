<nav class="demo-pagenav">
  <strong>Glossar</strong> ·
  <a href="tutorial.html">Tutorial</a> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

Das Glossar ist der Kern dieses Modells: eine Begriffsdefinitionssammlung des
Projekts, die zugleich die Tooltips im UI speist. Anwendungsbezogene
Erklärungen finden sich im [Tutorial](tutorial.html), die TEI-Auszeichnung und
das vollständige Rollenvokabular auf der Seite
[Technik / Datenmodell](technik.html).

Die Begriffe sind in sechs Abschnitte gegliedert: **A. Datenbank und
Datenmodell**, **B. Quellen und Überlieferung**, **C. Rollen in
Rechtsgeschäften**, **D. Historische Institutionen**, **E. Rechtsgeschäfte** und
**F. Projektrelevante Maße, Währungen und Besitzrecht**.

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
Gemeinschaft" handelt es sich derzeit um [[#Regest|Regesten]] aus den „Quellen
zur Geschichte der Stadt Wien" (Uhlirz). Künftig werden im Frontend weitere
Korpora hinzukommen, z.B. die „Wiener Stadtbücher" und Grundbücher.

Erfassungsstand: von Beginn der Überlieferung 1177 bis inklusive das Jahr 1414.

**Weiterführend:** [Monasterium: Haus­urkunden (WStLA)](https://www.monasterium.net/mom/AT-WStLA/HAUrk/fond) · [Wien-Wiki: QGW, Band II.1](https://www.geschichtewiki.wien.gv.at/Quellen_zur_Geschichte_der_Stadt_Wien#Band_II.1:_Verzeichnis_der_Originalurkunden_des_Städtischen_Archives_1239_-_1411)  
**Literatur:** Karl Uhlirz (Hg.), Verzeichnis der Originalurkunden des Städtischen Archives 1239–1411 (Wien 1898). (Quellen zur Geschichte der Stadt Wien, Abt. 2: Regesten aus dem Archiv der Stadt Wien 1)
{: .entry-refs }

### Event

Die grundlegende Analyseeinheit der Datenbank. Ein Event (auch: Ereignis)
entspricht einem in einer [[#Quelle]] dokumentierten Vorgang – oft ein
Rechtsgeschäft, etwa ein Verkauf, eine Stiftung, eine letztwillige Verfügung oder
ein Gerichtsverfahren.

### Factoid

Eine einzelne strukturierte Information, die aus einer Quelle gewonnen wurde und
der Quelle zugeordnet bleibt; auch widersprüchliche Angaben bleiben enthalten.
Factoids ermöglichen es, Personen, Orte, Organisationen und ihre Beziehungen
systematisch auszuwerten.

### Annotation

Eine Markierung im Quellentext, mit der Informationen wie Personen,
Organisationen, Orte und ihre [[#Attribut|Attribute]] ausgezeichnet werden – im
Fall des Projekts „Stadt und Gemeinschaft" handelt es sich dabei um in digitale
Textdateien umgewandelte [[#Regest|Regesten]] und Stadtbucheinträge, die nach den
Standards der TEI annotiert/codiert wurden.

### Entität

Die zentralen Analyseeinheiten (Entitäten) sind Ereignisse, Personen,
Organisationen und Orte (künftig auch im Frontend), die in einer Quelle genannt
werden und als eigener Datensatz in der Datenbank erfasst sind.

### Rolle

Die Funktion, die eine Person oder Organisation innerhalb eines bestimmten
Ereignisses einnimmt. Dieselbe Person kann in einer oder mehreren Quellen
verschiedene Rollen einnehmen. Das kontrollierte Rollenvokabular und seine
Code-Werte werden auf der Seite [Technik / Datenmodell](technik.html#rollen)
erläutert.

### Attribut

Eine Eigenschaft einer [[#Entität]], beispielsweise eine Profession oder ein
Titel.

### Verknüpfung

Die technische Verknüpfung von Informationen innerhalb der Datenbank,
beispielsweise zwischen einer Person und den [[#Quelle|Quellen]], in denen sie erwähnt wird.

### Beziehung

Eine Verbindung zwischen zwei [[#Entität|Entitäten]], etwa eine Verwandtschaftsbeziehung oder
eine Amtszugehörigkeit.

### Register

Ein Verzeichnis von Personen, Organisationen oder Orten, die in den Quellen
vorkommen, in unserem Fall insbesondere die Register der Quellen zur Geschichte
der Stadt Wien (hrsg. von Karl Uhlirz), ergänzend auch Werke wie „Die Wiener
Ratsbürger 1396–1526" (hrsg. von Richard Perger).

**Literatur:** Perger, Die Wiener Ratsbürger 1396–1526
{: .entry-refs }

### Normierung

Die Vereinheitlichung zeitgenössisch variabler Schreibweisen oder Bezeichnungen,
um Informationen systematisch durchsuchen und auswerten zu können, beispielsweise
der Begriff Bürger/Bürgerin, der unter anderem auch in den Schreibweisen
purger/purgerin oder civis wiennensis vorkommt.

## B. Quellen und Überlieferung

### Urkunde

Ein schriftliches, beglaubigtes Dokument, das ein Rechtsgeschäft, einen
Rechtsanspruch oder eine rechtlich relevante Handlung festhält. Sie folgt einem
festen formalen Aufbau und trägt Beglaubigungsmittel wie Siegel,
Herrschermonogramm oder Zeugenreihe, die ihr Rechts- und Beweiskraft verleihen.
Im Spätmittelalter treten vermehrt Privaturkunden von Städten, Räten und Bürgern
hervor.

**Verwandt:** [[#Regest]] · [[#Siegel]]  
**Weiterführend:** [ad fontes: „Urkunde"](https://www.adfontes.uzh.ch/tutorium/quellen-auswerten/urkunden-und-diplomatik/definition-urkunde/)
{: .entry-refs }

### Regest

Eine knappe Inhaltsangabe einer historischen [[#Quelle]], die wichtige
Informationen zusammenfasst. Regesten erfassen vor allem Rechtsinhalt, Datierung und beteiligte
Personen und dienen seit dem Mittelalter der Ordnung und Erschließung von
Urkundenbeständen (etwa in den Regesta Imperii).

**Verwandt:** [[#Urkunde]] · [[#Quelle]]  
**Weiterführend:** [ad fontes: „Regest"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/regesten/) · [Regesta Imperii](https://www.regesta-imperii.de/unternehmen.html)
{: .entry-refs }

### Edition

Eine wissenschaftliche Veröffentlichung historischer Quellen, meist mit
Transkriptionen, Kommentaren und Erläuterungen. Anders als die bloße
[[#Transkription]] berücksichtigt die kritische Edition die gesamte Überlieferung
eines Textes und rekonstruiert ihn nach der philologisch-kritischen Methode aus
dem Vergleich aller Textzeugen. Varianten und Kommentar werden in einem
kritischen Apparat dokumentiert, häufig ergänzt durch Stellen- und Namenregister.

**Verwandt:** [[#Transkription]]  
**Weiterführend:** [ad fontes: „kritische Edition"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/kritische-edition/) · [Monumenta Germaniae Historica](https://www.mgh.de/de/die-mgh/ueber-die-mgh)
{: .entry-refs }

### Digitalisat

Eine digitale Aufnahme einer historischen Quelle. Es entsteht als Endprodukt der
Digitalisierung, bei der ein analoges Objekt (etwa eine Urkunde oder Handschrift)
für die elektronische Speicherung und Verbreitung aufbereitet wird. Ziel ist die
möglichst originalgetreue Wiedergabe der Vorlage nach wissenschaftlichen
Erfordernissen.

### Transkription

Die buchstabengetreue Übertragung eines historischen Textes in moderne Schrift.
Sie folgt festgelegten Transkriptionsregeln – etwa dem Auflösen eindeutiger
Kürzungen, moderner Interpunktion und dem Kennzeichnen unsicherer Lesungen oder
Lücken – und gibt die sprachliche und orthographische Form des Originals möglichst
genau wieder. Anders als die kritische [[#Edition]] bildet sie dabei einen
einzelnen Textzeugen ab, ohne die gesamte Überlieferung heranzuziehen.

**Weiterführend:** [ad fontes: „Transkription"](https://www.adfontes.uzh.ch/tutorium/quellen-erschliessen/transkription/)
{: .entry-refs }

### Siegel

Ein Beglaubigungsmittel, mit dem die Echtheit einer Urkunde und die beteiligten
Personen bestätigt wurden. Der Begriff bezeichnet sowohl den Abdruck als auch den
Stempel, mit dem er erzeugt wird, und steht als rechtserhebliches Zeichen des
Siegelführers für Echtheit, Unversehrtheit und Gültigkeit.

**Weiterführend:** [ad fontes: „Siegel"](https://www.adfontes.uzh.ch/tutorium/handschriften-beschreiben/siegel/)
{: .entry-refs }

### Vidimus / Vidimierung

Die rechtsgültige Bestätigung, dass eine Abschrift (z.B. einer Urkunde) dem
Original entspricht. Konkret handelt es sich um eine beglaubigte Abschrift, die
das Original rechtlich ersetzen kann. Davon zu unterscheiden ist das Transsumpt,
das den Inhalt einer Urkunde in eine neue Urkunde aufnimmt.

Für alle Einträge unter weiterführende Angabe vgl. auch das [Glossar von ad
fontes (UZH)](https://www.adfontes.uzh.ch/glossar).

## C. Rollen in Rechtsgeschäften

Die folgenden Funktionsrollen werden hier nur kurz eingeführt; ihre
Code-Werte und die TEI-Auszeichnung stehen auf der Seite
[Technik / Datenmodell](technik.html#rollen). Konkrete Quellen mit aufgelösten
Rollen zeigt das [Tutorial](tutorial.html).

### Aussteller:in

Die Person oder Organisation, die verfügt oder erklärt. Bei einem Verkauf ist
dies meist die verkaufende Person, bei einem Testament die testierende Person.
Code-Wert im Datenmodell: `issuer`.

### Empfänger:in

Die Person oder Organisation, die eine Leistung, ein Recht oder einen Gegenstand
erhält. Code-Wert im Datenmodell: `recipient`.

### Einbringer:in

Eine Person, die ein Rechtsgeschäft oder eine letztwillige Verfügung dem Rat
oder einer anderen Autorität vorlegt und dessen Anerkennung veranlasst.

### Zeug:in

Eine Person, die ein Rechtsgeschäft bezeugt und dadurch dessen Gültigkeit stärkt.
Code-Wert im Datenmodell: `witness`.

### Siegler:in

Eine Person oder Institution, deren Siegel zur Beglaubigung eines Dokuments
verwendet wurde. Code-Wert im Datenmodell: `witness`.

### Grundherr:in

Die Person oder Institution, die einem Rechtsgeschäft als betroffene
Grundherrschaft zustimmt. Wer ein Haus oder ein [[#Burgrecht]] veräußert, tut dies
„mit Handen" des Grundherrn bzw. der Grundherrin – neben individuellen Personen
ist das oft der Stadtrat oder eine geistliche Institution. Im Datenmodell gehört
diese Funktion zur Sammelrolle `other`.

### Erblasser:in

Die Person, deren Vermögen nach ihrem Tod nach ihrem Willen verteilt wird.

### Testamentsvollstrecker:in

Eine Person, die mit der Durchführung einer letztwilligen Verfügung beauftragt
ist.

## D. Historische Institutionen

### Stadtrat
Das zentrale politische Entscheidungsgremium einer mittelalterlichen Stadt.

**Weiterführend:** [Wien-Wiki: Stadtrat](https://www.geschichtewiki.wien.gv.at/Stadtrat)  
**Literatur:** Czeike, Historisches Lexikon Wien, Band 5, S. 301
{: .entry-refs }

### Bürgermeister
Der gewählte Vorsitzende/führende Vertreter des [[#Stadtrat|Stadtrats]].

**Weiterführend:** [Wien-Wiki: Bürgermeister](https://www.geschichtewiki.wien.gv.at/Bürgermeister)  
**Literatur:** Czeike, Historisches Lexikon Wien, Band 1, S. 507–510
{: .entry-refs }

### Richter
Vorsteher des Stadtgerichts. Sein Bestellungsmodus war im Untersuchungszeitraum
des Projektes immer wieder umstritten. Prinzipiell galt er aber als städtisches
Amt mit landesfürstlicher Bestellung.

**Weiterführend:** [Wien-Wiki: Stadtrichter](https://www.geschichtewiki.wien.gv.at/Stadtrichter)  
**Literatur:** Czeike, Historisches Lexikon Wien, Band 5, S. 302 (Stadtrichter)
{: .entry-refs }

### Bürger:in
Eine Person mit Bürgerrecht in einer Stadt.

**Weiterführend:** [Wien-Wiki: Bürgerrecht](https://www.geschichtewiki.wien.gv.at/Bürgerrecht)  
**Literatur:** Czeike, Historisches Lexikon Wien, Band 1, S. 511
{: .entry-refs }

### Bürgerschranne
Sitz des Stadtgerichts der Stadt Wien.

**Weiterführend:** [Wien-Wiki: Schranne](https://www.geschichtewiki.wien.gv.at/Schranne)  
**Literatur:** Czeike, Historisches Lexikon Wien, Band 5, S. 141 f.
{: .entry-refs }

## E. Rechtsgeschäfte

Die in diesem Abschnitt genannten Begriffe sind großteils auch im konsolidierten
*Rechtshistorischen Glossar der Wiener Stadtbücher* (hg. von Wilhelm Brauneder und
Christian Neschwara, Institut für Realienkunde, Universität Salzburg) online
zugänglich: [imareal.sbg.ac.at/rechtshistorisches-glossar](https://www.imareal.sbg.ac.at/rechtshistorisches-glossar/). Die
Seitenverweise („Teil 1", „Teil 2" usw.) beziehen sich auf die Bände dieser
Edition.

### Rechtsgeschäft
Eine Willenserklärung mit rechtlich relevanten Folgen zwischen Personen oder
Institutionen. Im Datenmodell ist ein Rechtsgeschäft der häufigste Typ eines
[[#Event|Events]]. Vgl. zur zeitgenössischen Unterscheidung von einseitigem und
gegenseitigem Rechtsgeschäft die Einträge *Geschäft* (Teil 1, S. 17 f.) und
*Gemächt* (Teil 2, S. 13).

Die Wirksamkeit eines Rechtsgeschäfts setzt Geschäftsfähigkeit voraus:
Rechtsgeschäfte Minderjähriger sind nach Wiener Recht nur schwebend wirksam und
werden erst mit Erreichen der Mündigkeit (Vogtbarkeit, in Wien im 15. Jahrhundert
grundsätzlich mit 18 Jahren) durch Bestätigung unwiderruflich; vgl.
*Volljährigkeitsweisung* (Teil 4, S. 11 f.).

### Verkauf
Die Übertragung eines Gutes gegen Bezahlung. Vgl. zum liegenschaftsrechtlichen
Rahmen der Veräußerung und Belastung den Eintrag [[#Burgrecht]] (Teil 1, S. 13 f.).

### Schenkung
Die unentgeltliche Übertragung eines Gutes. Vgl. zu unentgeltlichen Zuwendungen
von Todes wegen (Vermächtnis/Legat) den Eintrag *Geschäft* (Teil 1, S. 17 f.).

### Stiftung
Die dauerhafte Zuwendung von Besitz oder Einkünften für einen bestimmten Zweck,
häufig religiöser Art (Gebetsgedenken/memoria für das Seelenheil); für eine
ausführliche Begriffserklärung (dort unter dem Stichwort *Messstiftung*) vgl.
Teil 1, S. 18.

In Wien überwiegen Messstiftungen zur Feier von Seelenmessen: entweder als
*Klosterstiftung*, bei der das Kloster das Stiftungsvermögen erhält und selbst
verwaltet, oder als *Altarpfründe*, bei der sich der Stifter über die
„Lehenschaft" (Bestellung und Kontrolle des Messpriesters) weltlichen Einfluss
auf die Stiftung vorbehält.

### Letztwillige Verfügung
Eine Verfügung über den Nachlass für die Zeit nach dem Tod (zeitgenössisch
„Geschäft").

In der Wiener Rechtssprache bezeichnet „Geschäft" (zu „(ver)schaffen") die
einseitige, jederzeit widerrufliche Verfügung von Todes wegen, im Unterschied zu
den mit „(ver)machen" umschriebenen Verfügungen unter Lebenden und
sachenrechtlichen Abreden (*Gemächt*); mit der Vollziehung eines Geschäfts werden
ein oder mehrere Willensvollstrecker („Geschäftsherren") betraut. (Teil 1, S. 17)

### Verpfändung
Die Überlassung eines Gutes als Sicherheit für eine Forderung. Vgl. den Eintrag
[[#Burgrecht]] (Teil 1, S. 13 f.); zur Verpfändung von Erbgut in Notlagen *Echte
Not* (Teil 1, S. 14 f.), zur Haftung mit dem gesamten Vermögen *Geloben „zu allem
Gut"* (Teil 2, S. 12).

### Darlehen
Die zeitweise Überlassung von Geld oder Gütern gegen Rückgabe. Vgl. zur
zeitgenössischen Kreditgewährung durch Rentenkauf den Eintrag [[#Burgrecht]]
(dort Burgrechts-Rente; Teil 1, S. 14).

### Urteil
Die Entscheidung eines Gerichts oder einer anderen rechtsprechenden Instanz.

### Offener Brief
Eine [[#Urkunde]], die nicht verschlossen ausgestellt wurde und öffentlich
vorgelegt werden konnte.

### Grundzins / Grunddienst
Eine regelmäßig zu entrichtende Abgabe für die Nutzung eines Grundstücks = die
ursprüngliche Belastung des Grundstücks aus dem Bodenleihe-/Besitzverhältnis.
Vgl. den Eintrag [[#Burgrecht]], Burgrechts-Leihe (Teil 1, S. 13 f.).

### Burgrecht
Eine durch ein Geld-/Rentengeschäft (Kapitalanlage auf der Liegenschaft) neu
geschaffene Rente: Die Gläubiger:innen („Käufer:innen") überlassen den
Grundbesitzer:innen („Verkäufer:innen") Kapital und beziehen dafür einen
jährlichen Zins (meist 8–12,5 % des überlassenen Kapitals). Das Burgrecht tritt
als zweite Belastung neben den Grunddienst. Die Liegenschaft hat damit neben
Grundherr:innen auch „Burgherr:innen".

**Literatur:** Felix Czeike, Das „Burgrecht" in Wien im 15. Jahrhundert, in: Jahrbuch des Vereins für Geschichte der Stadt Wien 10 (1952/53), S. 115–137
{: .entry-refs }

## F. Projektrelevante Maße, Währungen und Besitzrecht

### Silber
- `d.` / `Wr. Pf.` = denarius / Wiener Pfennig

### Gold
- `fl. ung.` = florenus / Gulden, ungarisch
- `fl. rh.` = florenus / Gulden, rheinisch

### Recheneinheiten
- `lb.` = libra / Pfund = 240 denarii
- `ß.` / `s.` = solidus / Schilling, 1 solidus = 30 denarii

### Recheneinheiten vs. Umlaufsmünze
Grundlage war die Pfennigwährung; der Wiener Pfennig war die einzige tatsächlich
ausgemünzte Umlaufwährung und – neben Naturalien – Basis des Alltagsverkehrs.

Pfund und Schilling wurden nicht geprägt, sondern dienten als Recheneinheiten.
Das Pfund diente auch als Gewichtseinheit.

Der Pfennig blieb über das ganze 15. Jh. die maßgebliche Bezugsgröße.

### Weitere Silbermünzen (späteres 15. Jh.)
Kreuzer = 4 Pfennig; Groschen = zunächst 2 Kreuzer.

Sie verdrängten den Pfennig nach der „Schinderlingszeit" (1450er/60er Jahre)
zunehmend, lösten ihn als Recheneinheit aber nicht ab.

### Goldmünzen als „Oberwährung"
Maßgeblich waren der ungarische (`fl. ung.`) und der rheinische Gulden
(`fl. rh.`).

Wegen ihres konstanten Metallwerts dienten sie als Maßstab bei größeren
Zahlungen und als Referenzgröße zur Bewertung der Silbermünzen.

### Projektrelevante Grundstücks- und Flächenmaße
- **Joch:** Flächenmaß für ländlichen Boden; in Wien nutzungsabhängig: bei
  Weingärten 3.200 Quadratklafter (≈ 1,15 ha), bei Äckern 1.600 Quadratklafter
  (≈ 0,58 ha).
- **Tagwerk:** Flächenmaß nach Arbeitszeit bemessen; in Wien entspricht dies
  einem Joch.
- **Quadratklafter:** Grundeinheit der Flächenberechnung, ≈ 3,6 m²; die Klafter
  ist zugleich das zugrunde liegende Längenmaß für Grundstücksabmessungen.

### Relevante Gewichtsmaße
- **Wiener Pfund (Gewicht):** ca. 0,56 kg.
- **Zentner** = 100 Wiener Pfund, ca. 56 kg; für schwere Waren.

**Weiterführend:** [Wien-Wiki: Kaufkraftrechner](https://www.geschichtewiki.wien.gv.at/Kaufkraftrechner)  
**Literatur:** Rudolf Geyer, Münze und Geld. Maß und Gewicht in Nieder- und Oberösterreich (Wien 1938); Thomas Ertl, Wien 1448. Steuerwesen und Wohnverhältnisse in einer spätmittelalterlichen Stadt (Wien/Köln/Weimar 2020)
{: .entry-refs }

---

Querverweise: [Tutorial](tutorial.html) · [Technik / Datenmodell](technik.html)
