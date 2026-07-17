<!-- ARCHIVIERT / PASSIV (Stand 2026-07-17): Diese Seite wird derzeit NICHT im
     Frontend gerendert und ist ueber keinen Live-Link erreichbar. Der Inhalt
     bleibt fuer eine moegliche spaetere Ueberarbeitung/Wiederaufnahme erhalten.
     Interne Verweise auf technik.html/glossar.html sind hier nur historisch. -->

<nav class="demo-pagenav">
  <a href="glossar.html">Glossar</a> ·
  <strong>Tutorial</strong> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

## Was ist diese Datenbank?

Diese Datenbank erschließt mittelalterliche Wiener Rechtsgeschäfte — Verkäufe, Schenkungen, Stiftungen, Verpfändungen und weitere Rechtsakte — aus handschriftlichen Überlieferungen des 12. bis 15. Jahrhunderts. Die Quellen stammen aus Regesten und Stadtbucheinträgen, die im Laufe der historischen Forschung transkribiert und ediert wurden.

Ziel der Datenbank ist es, die beteiligten Personen, Organisationen und ihre Rechtsgeschäfte systematisch durchsuch- und auswertbar zu machen. Jede [Quelle](glossar.html#quelle) — ob [Regest](glossar.html#regest) oder vollständig transkribierter Stadtbucheintrag — ist nach einem einheitlichen Modell erschlossen: Wer war beteiligt? In welcher Funktion? Welches Rechtsgeschäft lag vor?

Das folgende Tutorial führt durch die Grundbegriffe und zeigt an drei realen Quellen, wie das Modell in der Praxis aussieht.

## So funktioniert die Datenbank

Jede Quelle dokumentiert ein oder mehrere **Ereignisse**. Ein
[Event](glossar.html#event) (Ereignis) ist die grundlegende Analyseeinheit —
oft ein Rechtsgeschäft wie ein Verkauf oder eine Schenkung. An jedem Event sind
mehrere Beteiligte über eine [Rolle](glossar.html#rolle) gebunden; das
kontrollierte Vokabular kennt vier Code-Werte (`issuer`, `recipient`,
`witness`, `other`). Personen und Organisationen werden als
[Entität](glossar.html#entitat) einmalig erfasst und über ihre Rollen mit den
Events verknüpft.

Die folgenden drei Quellen spielen diese Logik durch — jeder Fall zeigt einen
anderen Aspekt.

## Wie lese ich eine annotierte Quelle?

Im Quellentext sind Personen, Organisationen und Orte ausgezeichnet — man sagt: **annotiert**. Das bedeutet, dass hinter jedem Namen in der Transkription eine maschinenlesbare Verknüpfung steht: die Person ist mit ihrem Registereintrag verbunden, die Organisation mit ihrer eigenen Entität in der Datenbank.

Jede Person, die an einem Rechtsgeschäft beteiligt ist, trägt eine [Rolle](glossar.html#rolle): Sie kann Ausstellerin oder Aussteller sein, Empfängerin oder Empfänger, Zeugin oder Zeuge — oder eine andere beteiligte Partei. Diese Rollen machen es möglich, über alle Quellen hinweg zu fragen: In welchen Rechtsgeschäften tritt eine bestimmte Person als Ausstellerin auf?

Die technische Seite dieser Auszeichnung — wie die TEI-XML-Elemente aufgebaut sind, welche Attributwerte möglich sind — beschreibt die [Technik-Seite](technik.html). Jede Quelle in der Datenbank kann außerdem als TEI-XML heruntergeladen werden; der Download-Link steht auf der jeweiligen Quellendetailseite.

### Fallbeispiel 1: Verkauf „mit Handen" der Stadt (Nr. 604) {#fallbeispiel-1}

<div class="demo-case">
  <blockquote>„Hainreich der Santwerfer und Elsbet, seine Hausfrau, verkaufen
  mit Handen hern Jansen von Tirnach, purgermaister und munsmaister, und des
  rates gemain der stat ze Wienne 1 lb dn. gelts purchrechts (ablösbar) auf
  ihrem Hause in der Chêrnerstrasse ze Wienne … um 8 lb dn. hern Jansen dem
  Urbêtschen."</blockquote>
  <blockquote>„Besiegelt mit dem städtischen Grundsiegel und dem Siegel hern
  Leupolts des Polczs, des rates der stat ze Wienne."</blockquote>
  <ul class="roles">
    <li><strong>Aussteller:innen</strong> (<code>issuer</code>): das Ehepaar
    Hainreich der Santwerfer und seine Hausfrau Elsbet</li>
    <li><strong>Empfänger</strong> (<code>recipient</code>): Jans der
    Urbetsch</li>
    <li><strong>„mit Handen"</strong> (<code>other</code>): Bürgermeister Jans
    von Tirnach (zugleich Münzmeister) und der Rat der Stadt Wien</li>
    <li><strong>Zeugen / Siegler</strong> (<code>witness</code>): Stadtrat und
    Ratsmitglied Leopold Polz</li>
  </ul>
  <p><strong>Was dieser Fall zeigt:</strong> ein Event mit gleich vier Rollen — ein ausstellendes Ehepaar, ein Empfänger, die zustimmende Grundherrschaft „mit Handen" und ein siegelnder Zeuge. Rechtsgeschäft: ein Verkauf um 8 Pfund Pfennig (ein ablösbares Burgrecht auf dem Haus). Einzelne Beteiligte sind zudem über Ämter an die Stadt Wien gebunden (Bürgermeister, Münzmeister, Ratsmitglied) — solche Tätigkeitsbeziehungen (<code>occ</code>) beschreibt die <a href="technik.html#rolename">Technik-Seite</a>.</p>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/604.html">Quelle 604 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
</div>

### Fallbeispiel 2: Schenkung für das Seelenheil an ein Kloster (Nr. 16) {#fallbeispiel-2}

<div class="demo-case">
  <blockquote>„Benedicta de Arnstain schenkt für das Seelenheil ihres Bruders
  und den Nachlass ihrer Sünden der Aebtissin und dem Collegium der Nonnen bei
  S. Nikolaus zu Wien die curia Ebonis und einen Weingarten, beides ausserhalb
  der Mauern der Stadt Krems gelegen."</blockquote>
  <blockquote>„Siegler: der Gemahl der Ausstellerin"</blockquote>
  <ul class="roles">
    <li><strong>Ausstellerin</strong> (<code>issuer</code>): Person, Benedicta
    de Arnstain</li>
    <li><strong>Empfängerin</strong> (<code>recipient</code>): Institution, der
    Nonnenkonvent St. Niklas</li>
    <li><strong>Siegler</strong> (<code>witness</code>): ihr Ehemann siegelt für
    sie</li>
  </ul>
  <p><strong>Was dieser Fall zeigt:</strong> eine einzelne Ausstellerin und eine Institution als Empfängerin — und dass für eine Frau ihr Ehemann siegelt (der Siegler ist nicht die Ausstellerin). Rechtsgeschäft: eine Schenkung für das Seelenheil ihres Bruders.</p>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/16.html">Quelle 16 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
</div>

### Fallbeispiel 3: eine Witwe vergibt Erbe (Urkunde 1869) {#fallbeispiel-3}

<div class="demo-case">
  <blockquote>„Margret, Niclass, des fleischakcher, witib ze Wienn, gibt ihrem
  Vetter Hannsen von Künigsprunn alles das gut und hab, so ihr von ihrer
  Schwester fraun Margreten seligen, etwenn wirtin in des graven von Czily haus
  in Wienn, anerstorben und angeerbt ist."</blockquote>
  <blockquote>„Besiegelt mit den Siegeln Jorgen des Grünpekchen und Marxen des
  Gödinger"</blockquote>
  <ul class="roles">
    <li><strong>Ausstellerin</strong> (<code>issuer</code>): Margret, Witwe des
    Fleischhackers Niklas</li>
    <li><strong>Empfänger</strong> (<code>recipient</code>): ein Verwandter, ihr
    Vetter Hanns von Künigsprunn</li>
    <li><strong>Siegler</strong> (<code>witness</code> / sealer): zwei Siegler</li>
  </ul>
  <p><strong>Was dieser Fall zeigt:</strong> wie Attribute und Relationen erfasst werden — Verwandtschaft (Witwe, Vetter, Schwester), ein Todesvermerk und ein Beruf hängen an den beteiligten Personen. Und einen Grenzfall der Klassifikation: Ist die Vergabe an den Vetter eine Schenkung oder ein Erbe? Solche offenen Zuordnungen bleiben in der Erschließung sichtbar.</p>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/1869.html">Quelle 1869 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
</div>

## Wie geht es weiter?

Die drei Fallbeispiele zeigen denselben Grundmechanismus: Ein [Event](glossar.html#event) — etwa ein Verkauf oder eine Schenkung — bündelt mehrere Beteiligte, von denen jede:r über eine [Rolle](glossar.html#rolle) mit dem Ereignis verknüpft ist.

Wenn Sie tiefer einsteigen möchten, bieten sich drei Wege an:

- **Begriffe nachschlagen:** Das [Glossar](glossar.html) erklärt alle zentralen Fachbegriffe der Datenbank — von [Quelle](glossar.html#quelle) und [Regest](glossar.html#regest) über [Event](glossar.html#event) bis hin zu Rechtsgeschäft und Entität.
- **Technik verstehen:** Die [Technik-Seite](technik.html) beschreibt den technischen Aufbau der Auszeichnung: wie TEI-XML-Elemente aufgebaut sind, welche Rollentypen und Personen-Attribute das Datenmodell kennt, und wie die maschinenlesbare Verknüpfung zwischen Text und Register hergestellt wird.
- **Eine Quelle selbst öffnen:** Klicken Sie auf einen der Quellen-Links in den Fallbeispielen oben, um eine reale annotierte Quelle in der Datenbank zu sehen. Im Volltext sind Personen und Organisationen hervorgehoben und mit ihren Registerprofilen verlinkt.

Die Datenbank wächst fortlaufend — neue Quellen werden erschlossen, bestehende Erschließungen werden verfeinert. Willkommen im Korpus.
