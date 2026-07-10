<nav class="demo-pagenav">
  <a href="glossar.html">Glossar</a> ·
  <strong>Technik / Datenmodell</strong>
</nav>

> **In Arbeit.** Das technische Glossar (TEI-Auszeichnung, Datenmodell) wird
> derzeit erarbeitet; Inhalte und Struktur sind vorläufig.

Diese Seite erklärt, wie die im [Glossar](glossar.html) definierten Begriffe in
den TEI-Quellen technisch ausgezeichnet sind. Die Tags erscheinen in der
herunterladbaren XML jeder Quelle. Die Beispiele unten stammen aus drei
konkreten Quellen.

## Rollen im Rechtsgeschäft {#rollen}

Die Funktion, die eine Person oder Organisation innerhalb eines Rechtsgeschäfts
einnimmt, wird als `<rs type="fn" role="…">` ausgezeichnet. Das kontrollierte
Vokabular kennt genau vier Code-Werte; ein nicht gesetzter Wert ist der leere
String, **nicht** `none`.

<ul class="tech-codes">
  <li><code>issuer</code> — Aussteller/Geber (Person/Organisation, die verfügt oder erklärt).</li>
  <li><code>recipient</code> — Empfänger/Adressat (erhält Recht, Gut, Geld).</li>
  <li><code>witness</code> — Zeuge/Siegler (bekräftigt, siegelt, „bei/sigillavit").</li>
  <li><code>other</code> — weitere Beteiligte/Funktionen (z. B. Grundherrin/-herr „mit Handen", Ratgeber, Intervenient). Spezifikation der Funktion via <code>&lt;triggerstring n="fn"&gt;</code>.</li>
</ul>

```xml
<rs type="fn" role="issuer">Hainreich der Santwerfer</rs>
```

### Warum Zeug:in und Siegler:in denselben Code-Wert tragen {#witness}

Im [Glossar](glossar.html) werden **Zeug:in** und **Siegler:in** getrennt
beschrieben, weil es zwei verschiedene Funktionen sind: Eine Zeug:in bezeugt ein
Rechtsgeschäft und stärkt dadurch dessen Gültigkeit; eine Siegler:in beglaubigt
ein Dokument durch ihr Siegel. Die Funktionen sind vergleichbar, aber nicht
dieselben.

Im **Auswertungsmodell** fallen beide unter den gemeinsamen Code-Wert
`witness`: siegelnde Zeug:innen und siegelnde Aussteller:innen werden gemeinsam
als die das Rechtsgeschäft beglaubigenden Personen erfasst. Eine
Aussteller:in, die zugleich ihr Siegel anbringt, erscheint dadurch in mehreren
Rollen — einmal als `issuer` und einmal als `witness`.

## Dispositive Verben {#disp}

Zentrale Aktionswörter, die das Event typisieren, werden als
`<triggerstring n="disp">` ausgezeichnet (Beispiele inkl. typischer
Formulierungen):

- **Kauf/Verkauf:** verkaufen, erkaufen, verhandeln; *habent verkaufft*; *gelts purkrechts* (Burgrechtskauf).
- **Schenkung/Stiftung/Widmung:** schenken, stiften, widmen.
- **Übergabe/Übertragung:** übergeben, übertragen, einantworten, auflassen.
- **Verpfändung/Sicherung:** verpfänden, versetzen, verpflichten.
- **Darlehen/Kredit/Zins:** leihen, aufnehmen, verzinsen, quittieren.
- **Bestätigung/Beglaubigung:** bestätigen, beurkunden, vidimieren.
- **Gericht/Verfahren:** klagen, antworten, vergleichen, sprechen/zusprechen, verurteilen.
- **Bestellung/Einsetzung:** setzen, bestellen, einsetzen (Amt/Vertretung).
- **Nutzung/Miete/Pacht:** mieten, pachten, verleihen (Nutzungsrechte).
- **Lösen/Ablösen:** lösen, ablösen, auslösen.

```xml
<triggerstring n="disp">verkaufen</triggerstring>
```

## roleName-Typen: Attribute und Relationen {#rolename}

Eigenschaften und Bindungen einer Entität werden als `<roleName type="…">`
ausgezeichnet. Zu unterscheiden sind **Attribute** (ohne Relation) und
**Relationen** (mit `corresp`, das auf die verbundene Entität verweist).

### Attribute (`roleName` ohne `corresp`)

Eine Eigenschaft, die einer Entität für sich zukommt, etwa ein Beruf, ein Titel
oder ein Status (Todesfloskel: „selig", „weilent").

<table class="roleName-grid">
  <thead><tr><th>type</th><th>Bedeutung</th><th>Beispiele</th></tr></thead>
  <tbody>
    <tr><td><code>prof</code></td><td>Beruf (Ausbildung)</td><td>„maurer", „schneider"</td></tr>
    <tr><td><code>title</code></td><td>Titel/Rang</td><td>„her", „magister"</td></tr>
    <tr><td><code>dead</code></td><td>Todesfloskel/Status</td><td>„selig", „weilent"</td></tr>
  </tbody>
</table>

### Relationen (`roleName` mit `corresp`)

Eine Verbindung zwischen zwei Entitäten, die über `corresp` auf die verbundene
Entität verweist.

<table class="roleName-grid">
  <thead><tr><th>type</th><th>Bedeutung</th><th>Beispiele</th></tr></thead>
  <tbody>
    <tr><td><code>kin</code></td><td>Verwandtschaft</td><td>„witib", „sohn", „swager"</td></tr>
    <tr><td><code>rep</code></td><td>Rechtliche Vertretung/Prokuration</td><td>„Gerhaben"</td></tr>
    <tr><td><code>occ</code></td><td>Tätigkeitsbeziehung (Amtsträger zu Amt/Institution; Dienstverhältnis)</td><td>Bürgermeister, Ratsmitglied</td></tr>
    <tr><td><code>title_ref</code></td><td>Titulare Bindung an einen Ort</td><td>„von"</td></tr>
  </tbody>
</table>

## Wie die Tags in den Fallbeispielen zusammenwirken {#faelle}

Die drei folgenden Fallbeispiele zeigen die Auszeichnung an konkreten Quellen.
Aus technischer Sicht:

### Fallbeispiel 1: Verkauf „mit Handen" der Stadt (Nr. 604)

- **Aussteller:innen** (`issuer`): das Ehepaar Hainreich der Santwerfer und seine Hausfrau Elsbet
- **Empfänger** (`recipient`): Jans der Urbetsch
- **„mit Handen"** (`other`): Bürgermeister Jans von Tirnach (zugleich Münzmeister) und der Rat der Stadt Wien
- **Zeugen/Siegler** (`witness` / sealer): Stadtrat und Ratsmitglied Leopold Polz
- **Ämter** (`occ`): Bürgermeister, Münzmeister, Ratsmitglied — an die Stadt Wien gebunden

### Fallbeispiel 2: Schenkung für das Seelenheil an ein Kloster (Nr. 16)

- **Ausstellerin** (`issuer`): Person, Benedicta de Arnstain
- **Empfängerin** (`recipient`): Institution, der Nonnenkonvent St. Niklas
- **Siegler** (`witness` / sealer): ihr Ehemann siegelt für sie

### Fallbeispiel 3: eine Witwe vergibt Erbe (Urkunde 1869)

- **Ausstellerin** (`issuer`): Margret, Witwe des Fleischhackers Niklas
- **Empfänger** (`recipient`): ein Verwandter, ihr Vetter Hanns von Künigsprunn
- **Siegler** (`witness` / sealer): zwei Siegler
- **Verwandtschaft** (`kin`): „witib" (Witwe), „Vetter", „Schwester"
- **Todesvermerk** (`dead`): die „selige" (verstorbene) Schwester
- **Beruf** (`prof`): die Schwester war „wirtin" im Haus des Grafen von Cilli

---

Zurück zum [Glossar](glossar.html).
