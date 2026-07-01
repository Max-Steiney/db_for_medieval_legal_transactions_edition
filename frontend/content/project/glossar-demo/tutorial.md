<nav class="demo-pagenav">
  <a href="glossar.html">Glossar</a> ·
  <strong>Tutorial</strong> ·
  <a href="technik.html">Technik / Datenmodell</a>
</nav>

So ist die Datenbank aufgebaut – erklärt an drei konkreten Quellen. Die
Fachbegriffe sind im [Glossar](glossar.html) definiert, ihre technische
Auszeichnung beschreibt die Seite [Technik / Datenmodell](technik.html). Jede
Person oder Organisation nimmt innerhalb eines Ereignisses eine **Rolle** ein;
das kontrollierte Vokabular kennt vier Code-Werte – `issuer`, `recipient`,
`witness` und `other` (ein nicht gesetzter Wert ist der leere String, nicht
`none`). Die folgenden drei Fälle lösen diese Rollen jeweils im Kontext der
Quelle auf und verlinken auf das gerenderte Regest.

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
    <li><strong>Empfänger</strong> (<code>recipient</code>): eine Einzelperson,
    Jans der Urbetsch</li>
    <li><strong>„mit Handen"</strong> (<code>other</code>): Bürgermeister Jans
    von Tirnach (zugleich Münzmeister) und der Rat der Stadt Wien</li>
    <li><strong>Zeugen / Siegler</strong> (<code>witness</code>): Stadtrat und
    Ratsmitglied Leopold Polz</li>
  </ul>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/604.html">Quelle 604 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
  <p class="dev-only">Redaktionsnotiz (#22): Rollen exakt aus dem Entwurf
  übernommen, hier kein generisches Gendern. Das Ehepaar bleibt
  „Aussteller:innen". Rechtsgeschäft: Verkauf; Geld/Besitz: 8 Pfund Pfennig,
  ablösbares Burgrecht auf dem Haus. Ämter (occ): Bürgermeister, Münzmeister,
  Ratsmitglied — an die Stadt Wien gebunden; gehören auf die Technik-Seite.</p>
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
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/16.html">Quelle 16 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
  <p class="dev-only">Redaktionsnotiz (#22): Hier feminin Singular wie im
  Original – „Ausstellerin", „Empfängerin". Rechtsgeschäft: Schenkung für das
  Seelenheil ihres Bruders. Der Siegler (Ehemann) trägt im Datenmodell den
  Code-Wert <code>witness</code> – warum siegelnde und bezeugende Funktion
  diesen gemeinsamen Wert teilen, steht auf der Technik-Seite, nicht hier.</p>
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
    <li><strong>Ausstellerin</strong> (<code>issuer</code>): Person, Margret,
    Witwe des Fleischhackers Niklas</li>
    <li><strong>Empfänger</strong> (<code>recipient</code>): ein Verwandter, ihr
    Vetter Hanns von Künigsprunn</li>
    <li><strong>Siegler</strong> (<code>witness</code>): zwei Siegler</li>
  </ul>
  <p class="demo-xref"><a href="../../documents/QGW/Vienna_1177-1414_ready/1869.html">Quelle 1869 ansehen</a>
  · <a href="technik.html#rollen">Rollen technisch</a></p>
  <p class="dev-only">Redaktionsnotiz (#7): Verwandtschaft (kin: „witib"/Witwe,
  „Vetter", „Schwester"), Todesvermerk (dead: die „selige" Schwester) und Beruf
  (die Schwester war „wirtin" im Haus des Grafen von Cilli) sind hier nur
  inhaltlich angedeutet; ihre technische Auszeichnung als Attribut bzw. Relation
  gehört auf die <a href="technik.html">Technik-Seite</a>.</p>
</div>

Diese drei Quellen zeigen denselben Mechanismus: Ein **Ereignis** (etwa ein
Verkauf oder eine Schenkung) bündelt mehrere Beteiligte, von denen jede:r über
die Rolle mit einem der vier Code-Werte (`issuer`, `recipient`, `witness`,
`other`) an das Ereignis gebunden ist. Die Begriffe dazu stehen im
[Glossar](glossar.html), die TEI-Auszeichnung und die roleName-Typen auf der
Seite [Technik / Datenmodell](technik.html).
