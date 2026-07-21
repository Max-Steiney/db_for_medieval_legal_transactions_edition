## 1. Projektkontext

Die Datenbank `db_for_medieval_legal_transactions` ist eine TEI-XML-basierte Datenbank mittelalterlicher Wiener Rechtsgeschäfte (aktuell 1177 bis 1414). Das Datenmodell orientiert sich an [TEI P5](https://tei-c.org/release/doc/tei-p5-doc/en/html/) und an Konventionen der digitalen Prosopographie. Infolge wird Aufbau und Funktionsweise der Datenbank überblicksartig skizziert.

Eine detaillierte Beschreibung inklusive Entity-Relationship-Modell (ER-Model) finden Sie in folgendem Artikel:

Korbinian Grünwald, [Die digitale Erfassung von mittelalterlichen Rechtsgeschäften – Beschreibung der semistrukturierten XML-Datenbank db_for_medieval_legal_transactions](https://dhd-blog.org/?p=16737), in: DHdBlog: Digital Humanities im deutschsprachigen Raum (2021).

Eine Kompatibilität mit [CIDOC-CRM](https://www.cidoc-crm.org/) ist langfristig angedacht.

### Quellensammlungen

Die Edition umfasst aktuell folgende Quellensammlungen:

| Korpora |
|---------|
| **QGW/Vienna\_1177-1414** |
| Stadtbuecher/Band\_1\_1395-1400 \* |

\* Im Frontend wird aktuell nur der Bestand QGW/Vienna\_1177-1414 angezeigt; die Freischaltung der übrigen Bestände folgt.

## 2. Annotationsmodell

Das Annotationsmodell wird im Folgenden in vier konzeptuellen Ebenen dargestellt. Die Ebenen sind hierarchisch aufgebaut: Jede ist Teil der jeweils höheren, und die Verschachtelung im XML spiegelt diese Hierarchie wider.
Die Schema-Validierung erfolgt gegen `sources/schema/toolbox.rng` (RelaxNG).

| Ebene | Gegenstand | TEI-Element | Klassifikation |
|-------|-----------|-------------|----------------|
| 1. Ereignisse | Rechtsgeschäfte | `<rs type="event">` | über `<triggerstring n="disp">` |
| 2. Funktionen | Rollen im Rechtsgeschäft | `<rs type="fn">` | über `@role` |
| 3. Entitäten | Personen, Orte, Organisationen | `<rs type="person\|org\|place">` | über `@type` und `@ref` |
| 4. Attribute/Relationen | Eigenschaften und Beziehungen | `<roleName>` | über `@type` und `@corresp` |

### Ebene 1: Ereignisse

Ein Ereignis umschließt eine vollständige rechtliche Handlung. Es wird mit `<rs type="event" ref="ev__*">` annotiert. Der `@ref`-Wert verweist auf eine Ereignis-ID.

Innerhalb des Ereignisses markiert `<triggerstring n="disp">` den **dispositiven Triggerstring**, das Verb oder die Verbalphrase, die die Art des Rechtsgeschäfts bestimmt. Die Kategorisierung erfolgt nicht a priori, sondern durch Extraktion dispositiver Verben und nachträgliche Kategorienbildung.

```xml
<rs type="event" ref="ev__QGW_II_I_1">
  <rs type="fn" role="issuer">
    <rs type="person" ref="pe__hadmar_von_schoenberg_QGW_II_I_1">
      H(admar) de Schonenberg</rs>, ...
  </rs>
  <triggerstring n="disp">haben <add>gegeben</add></triggerstring>
  <rs type="fn" role="recipient">
    <rs type="org" ref="org__wien-st_niklas_vor_dem_stubentor_zisterzienserinnen">
      dem Nonnenkloster St. Nikolaus</rs>
  </rs>
  quattuor iugera lignorum ...
</rs>
```

*Quelle: [QGW II/1 Nr. 1 (1198 bis 1230)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1.html)*

### Ebene 2: Funktionen

Funktionen beschreiben die Rolle einer Person oder Organisation innerhalb eines Ereignisses. Sie werden mit `<rs type="fn" role="...">` annotiert. Die im Bestand vorkommenden Rollen klassifizieren die Beteiligung an einem Rechtsgeschäft: Aussteller, Empfänger, Zeuge, sonstige Beteiligung. Sonstige Beteiligungen werden unter der Rolle `other` über einen zusätzlichen Triggerstring näher bestimmt:

```xml
<rs type="fn" role="other">
  <triggerstring n="fn">mit Zustimmung</triggerstring> seiner
  <rs type="person" ref="pe__diemut_QGW_II_I_10">
    <roleName type="kin" corresp="pe__berthold_QGW_II_I_10">
      Gemahlin</roleName> Dimu/od</rs>
  und seiner Kinder und Erben
</rs>
```

*Quelle: [QGW II/1 Nr. 10 (1274)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/10.html)*

### Ebene 3: Entitäten

Entitäten sind Personen, Organisationen und Orte. Sie werden mit `<rs>` annotiert und über `@ref` mit den Indices verknüpft.

| Typ | Element | ID-Präfix | Index |
|-----|---------|-----------|----------|
| Person | `<rs type="person" ref="pe__*">` | `pe__` | personList.xml |
| Organisation | `<rs type="org" ref="org__*">` | `org__` | orgList.xml |
| Ort | `<rs type="place" ref="pl__*">` | `pl__` | placeList.xml |

**Person:**

```xml
<rs type="person" ref="pe__konrad_chrannest_QGW_II_I_99">
  Chunrat der Chrannest</rs>
```

**Organisation:**

```xml
<rs type="org" ref="org__wien-st_niklas_vor_dem_stubentor_zisterzienserinnen">
  dem Nonnenkloster St. Nikolaus</rs>
```

**Ort:**

```xml
<rs type="place" ref="pl__wien-kohlmarkt">Kolmarkcht</rs>
```

### Ebene 4: Attribute und Relationen

Attribute und Relationen werden mit `<roleName type="...">` annotiert; damit werden Personen und Organisationen mit weiteren Informationen versehen. Der `@type` bestimmt die Art der Aussage.

Zwei Arten von `@type`-Werten sind zu unterscheiden:

- **Attribute** charakterisieren die Entität selbst (z.B. ein Titel oder die Markierung "verstorben").
- **Relationen** verknüpfen die Entität über `@corresp` mit einem zweiten Eintrag (z.B. eine Verwandtschaftsbeziehung zu einer Person, eine Amtsfunktion in einer Organisation, eine topographische Lage in einem Ort).

**Attribute:**

**Beruf (prof):**

```xml
<rs type="person" ref="pe__prokop_chreier_QGW_II_I_1227">Proko, des Chreier
  <roleName type="prof">wirt</roleName> in seinem haus ze Prag</rs>
```

*Quelle: [QGW II/1 Nr. 1227 (1392)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1227.html)*

**Titel (title):**

```xml
<rs type="person" ref="pe__herbert_auf_der_saeule_QGW_II_I_184">
  <roleName type="title">Grundherren</roleName>,
  <roleName type="title">hern</roleName> Herbortes auf der Seul</rs>
```

*Quelle: [QGW II/1 Nr. 100 (1327)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/100.html)*

**Verstorben (dead):**

```xml
<rs type="person" ref="pe__dietrich_QGW_II_I_566">
  <roleName type="dead">Tode</roleName> des ...</rs>
```

*Quelle: [QGW II/1 Nr. 566 (1360)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/566.html)*

**Relationen:**

**Amtsträger (occ):**

```xml
<rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus,
  <roleName type="occ" corresp="org__oesterreich-herzogtum">
    camerarius</roleName>
</rs>
```

*Quelle: [QGW II/1 Nr. 10 (1274)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/10.html)*

**Verwandtschaft (kin):**

```xml
<rs type="person" ref="pe__elisabeth_QGW_II_I_100">Elsbet, sein
  <roleName type="kin" corresp="pe__konrad_chrannest_QGW_II_I_99">
    hausvrowe</roleName>
</rs>
```

*Quelle: [QGW II/1 Nr. 100 (1327)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/100.html)*

**Stellvertretung (rep):**

```xml
<rs type="person" ref="pe__johann_cherner_QGW_II_I_810">
  Janns Cherner
  <roleName type="rep" corresp="pe__thomas_cherner_QGW_II_I_999">
    <add>fuer</add></roleName>
</rs>
```

*Quelle: [QGW II/1 Nr. 999](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/999.html)*

### Zusammenspiel der Ebenen

Ein vollständiges Beispiel zeigt die Verschachtelung aller vier Ebenen:

```xml
<!-- Ebene 1: Ereignis -->
<rs type="event" ref="ev__QGW_II_I_10">
  <!-- Ebene 2: Funktion (Aussteller) -->
  <rs type="fn" role="issuer">
    <!-- Ebene 3: Entitaet (Person) -->
    <rs type="person" ref="pe__berthold_QGW_II_I_10">
      Bertoldus,
      <!-- Ebene 4: Attribut (Amtstraeger) -->
      <roleName type="occ" corresp="org__oesterreich-herzogtum">
        camerarius</roleName>
    </rs>
  </rs>,
  <triggerstring n="disp">gibt</triggerstring>
  <!-- Ebene 2: Funktion (Sonstige) -->
  <rs type="fn" role="other">
    <triggerstring n="fn">mit Zustimmung</triggerstring> seiner
    <!-- Ebene 3: Entitaet (Person) -->
    <rs type="person" ref="pe__diemut_QGW_II_I_10">
      <!-- Ebene 4: Relation (Verwandtschaft) -->
      <roleName type="kin" corresp="pe__berthold_QGW_II_I_10">
        Gemahlin</roleName> Dimu/od
    </rs>
    und seiner Kinder und Erben
  </rs>
  eine Rente von 12 sh. dn. ...
  <!-- Ebene 2: Funktion (Empfaenger) -->
  <rs type="fn" role="recipient">
    <!-- Ebene 3: Entitaet (Organisation) -->
    <rs type="org"
      ref="org__wien-st_niklas_vor_dem_stubentor_zisterzienserinnen">
      das Nonnenkloster bei S. Nikolaus</rs>
  </rs>
  ...
</rs>
```

*Quelle: [QGW II/1 Nr. 10 (1274)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/10.html). Bertoldus, Kämmerer des Herzogtums Österreich, gibt mit Zustimmung seiner Gemahlin Dimu/od eine Rente an das Nonnenkloster St. Nikolaus.*

### Zusätzliche Attribute

**`@cert`**: Sicherheitsangabe zu einer Annotation, vergeben in Stufen.

```xml
<rs type="person" ref="pe__georg_QGW_II_I_144">Georg, des hubmaisters
  <roleName type="occ" corresp="pe__konrad_hubmeister_QGW_II_I_207" cert="low">schreiber</roleName></rs>
```

*Quelle: [QGW II/1 Nr. 165 (1335)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/165.html)*

## 3. Tagging-Workflow

Die folgende Reihenfolge beschreibt den typischen Ablauf, in dem Annotationen in einer Quelle angelegt werden. Der Workflow wird durchgehend an einer Quelle gezeigt: [QGW II/1 Nr. 10 (1274)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/10.html). Die vollständig annotierte Quelle:

```xml
<div type="abstract" resp="ks">
  <p>
    <rs type="event" ref="ev__QGW_II_I_10">*
      <rs type="fn" role="issuer">
        <rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus,
          <roleName type="occ" corresp="org__oesterreich-herzogtum">camerarius</roleName></rs>
      </rs>,
      <triggerstring n="disp">gibt</triggerstring>
      <rs type="fn" role="other">
        <triggerstring n="fn">mit Zustimmung</triggerstring> seiner
        <rs type="person" ref="pe__diemut_QGW_II_I_10">
          <roleName type="kin" corresp="pe__berthold_QGW_II_I_10">Gemahlin</roleName> Dimu/od</rs>
        und seiner Kinder und Erben
      </rs>
      eine Rente von 12 sh. dn. innerhalb der Mauern Wiens auf dem
      gemeinhin Langmaur genannten Orte an
      <rs type="fn" role="recipient">
        <rs type="org" ref="org__wien-st_niklas_vor_dem_stubentor_zisterzienserinnen">das Nonnenkloster bei S. Nikolaus</rs>
      </rs>
      mit der Bestimmung, dass 6 sh. zur Kammer, 6 sh. zum Krankenhause
      der Nonnen gereicht werden sollen.
    </rs>
  </p>
</div>
<div type="seal">
  <p>
    <rs type="event" ref="ev__QGW_II_I_10">
      <rs type="fn" role="witness">Siegler: der
        <rs type="person" ref="pe__berthold_QGW_II_I_10">Aussteller</rs>.</rs>
    </rs>
  </p>
</div>
```

### Schritt 1: Bearbeiter:innen-Kürzel

Jede:r Bearbeiter:in trägt ein Kürzel in das `@resp`-Attribut des `<div>`-Elements und an Einträgen in den Indices ein. Im Beispiel trägt der Abstract-Div das Kürzel `ks`:

```xml
<div type="abstract" resp="ks">
```

Mehrere Kürzel können durch Bindestrich verbunden werden, um eine gemeinsame Verantwortung mehrerer Bearbeiter:innen auszuweisen (z.B. `df-hk-kg`). Die Zuordnung der Kürzel zu konkreten Personen wird projektintern gepflegt und ist nicht Bestandteil der öffentlichen Edition; Pflegestelle ist die Datei `normalisation_lists/editors/Name_of_Editors.csv`.

### Schritt 2: Ereignisse

Alle Rechtsgeschäfte werden als Ereignisse markiert. Im Beispiel umschließt ein Ereignis die gesamte Schenkung:

```xml
<rs type="event" ref="ev__QGW_II_I_10">...</rs>
```

### Schritt 3: Dispositivformeln

Dispositive Verben und Verbalphrasen werden mit `<triggerstring n="disp">` markiert. Im Beispiel ist das die Schenkungsformel:

```xml
<triggerstring n="disp">gibt</triggerstring>
```

### Schritt 4: Funktionen

Allen beteiligten Personen und Organisationen wird eine Funktionsrolle zugewiesen. Im Beispiel sind alle vier Rollen belegt:

```xml
<rs type="fn" role="issuer">Bertoldus, ...</rs>
<rs type="fn" role="other"><triggerstring n="fn">mit Zustimmung</triggerstring> seiner Gemahlin ...</rs>
<rs type="fn" role="recipient">das Nonnenkloster bei S. Nikolaus</rs>
<rs type="fn" role="witness">Siegler: der Aussteller.</rs>
```

### Schritt 5: Entitäten

Entitäten werden zuerst mit leerem `<rs/>` markiert, dann wird die ID (`@ref`) zugewiesen:

```xml
<!-- Schritt 5a: Markierung -->
<rs type="person">Bertoldus</rs>

<!-- Schritt 5b: ID-Zuweisung -->
<rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus, ...</rs>
```

### Schritt 6: Attribute und Relationen

Attribute und Relationen werden innerhalb der Entität annotiert. Im Beispiel trägt Bertoldus das Amt (`occ`), seine Gemahlin Diemut die Verwandtschaftsrelation (`kin`):

```xml
<rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus,
  <roleName type="occ" corresp="org__oesterreich-herzogtum">camerarius</roleName></rs>
```

### Zusätzliche Konventionen

Über den gezeigten Ablauf hinaus treten weitere Fälle auf:

**Erwähnte Ereignisse** (nicht das Hauptereignis der Urkunde, sondern ein darin nur erwähntes Rechtsgeschäft) erhalten das Suffix `_men_`:

```xml
<rs type="event" ref="ev__QGW_II_I_823_men_1">dass das Haus vor offenem
  Gerichte in der Bürgerschranne der Kapelle zugesprochen wurde</rs>
```

*Quelle: [QGW II/1 Nr. 823 (1372)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/823.html)*

**Implizite Informationen** werden mit `<add>` in den Tag geholt — etwas, das im Text erst später oder nur implizit erscheint. Im Triggerstring:

```xml
<triggerstring n="disp">haben <add>gegeben</add></triggerstring>
```

`<add>` kann auch an anderer Stelle stehen, etwa innerhalb eines `<rs type="person">`, um einen erst später genannten Namensteil zu ergänzen:

```xml
<rs type="person" ref="pe__heinrich_chamrer_QGW_II_I_1516">
  <add>Heinrich</add> des Chamrer</rs>
```

*Quelle: [QGW II/1 Nr. 1347 (1396)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1347.html)*

**`<unclear>`** markiert unleserliche oder schwer lesbare Passagen:

```xml
<rs type="person" ref="pe__leonhard_QGW_II_I_1553">Lienharts des Mu/echsen,
  <roleName type="occ" corresp="org__mauerbach-kartaeuser">pergmaister
    <unclear>zu Eczkestorf</unclear></roleName></rs>
```

*Quelle: [QGW II/1 Nr. 1553 (1403)](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/documents/QGW/Vienna_1177-1414_ready/1553.html)*


## 4. ID-Konstruktionsregeln

### Ereignisse (ev\_\_)

```
ev__ + Quellenabkuerzung + (_) Nummer
```

| Muster | Beispiel |
|--------|---------|
| Hauptereignis | `ev__QGW_II_I_1` |
| Erwähnte Ereignisse | `ev__QGW_II_I_823_men_1` |

### Personen (pe\_\_)

```
pe__ + normalisierter_Vorname + (_) normalisierter_Nachname + (_) Quellenabkuerzung + (_) Nummer
```

| Muster | Beispiel |
|--------|---------|
| Standard | `pe__heinrich_straiher_QGW_II_I_331` |
| Homonyme (Suffixunterscheidung) | `pe__elisabeth_QGW_II_I_301_a`, `pe__elisabeth_QGW_II_I_301_b` |

**Konventionen:**

- Keine Umlaute in IDs.
- Vornamen werden über eine externe Normalisierungstabelle vereinheitlicht (siehe Abschnitt 5).
- Nachnamen stammen aus dem Quellenregister; fehlt ein Register, wird die Originalschreibung verwendet.
- Bei fehlendem Nachnamen wird der Beruf verwendet.
- Bei Frauen und Kindern wird ein potenzieller Nachname in `<add>` ergänzt.

Diese Konventionen beschreiben die im Bestand erkennbare Praxis; Detailausnahmen werden im konkreten Einzelfall editorisch entschieden.

### Individualisierungsverfahren

Die Disambiguierung von Homonymen erfolgt durch das Suffix `_a` / `_b` (usw.) an der Personen-ID. Dieses Verfahren greift, wenn derselbe Name in derselben Quelle mehrfach vorkommt und die Personen durch Kontextinformationen (Beruf, Verwandtschaft, Amt) unterschieden werden können.

**Index-Struktur (personList.xml):**

Jeder Personeneintrag kann folgende Informationen enthalten:

- `<persName>`: `<forename>`, `<surname>` (jeweils mit `<reg>` für normalisierte Form), `<addName>` (Beiname), `<genName>` (Generationsname)
- `<death notAfter="">`: Todesdatum
- `<idno>`: Verknüpfung mit externen Normdateien
- `@sex` (f/m), `@source`, `@resp`, `@cert`
- `@sameAs`: Queridentifikation mit einer anderen Person im Index

Ein gut gefüllter Eintrag, hier der Wiener Bürgermeister [Heinrich Straiher](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/register/persons/pe__heinrich_straiher_QGW_II_I_331.html):

```xml
<person sex="m" source="QGW_II_I_register_pg_579" resp="ks" xml:id="pe__heinrich_straiher_QGW_II_I_331">
  <persName type="wienwiki">Heinrich Straicher</persName>
  <persName>
    <forename><reg>Heinrich</reg></forename> <surname><reg>Straiher</reg></surname>
  </persName>
  <note>Hofmeister zu Dornbach, Judenrichter, Bgm., Gem. Klara</note>
  <death notAfter="1363-08-22">1363-08-22</death>
  <idno type="URI">https://www.geschichtewiki.wien.gv.at/Special:URIResolver/?curid=18785</idno>
</person>
```


### Organisationen (org\_\_)

```
org__ + Siedlung + (-) Patron/Eigenname + (_) Institutionstyp + (-) Unterorganisation
```

| Muster | Beispiel |
|--------|---------|
| Siedlung | `org__wien` |
| Kirche | `org__wien-st_stephan` |
| Altar einer Kirche | `org__wien-st_stephan-altar_st_dorothea` |

**Prinzip:** Vom Allgemeinen zum Spezifischen. Hierarchische Verschachtelung in orgList.xml.

Beispiel ([org__wien](https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/register/orgs/org__wien.html) mit hierarchisch verschachtelten Unterorganisationen):

```xml
<org type="Stadt" xml:id="org__wien" resp="kg">
  <orgName><reg>Wien</reg></orgName>
  <note>Bürgermeister, Rat (und Gemein)</note>
  <location><address><addrLine corresp="#pl__wien"/></address></location>
  <org type="Stadtviertel" xml:id="org__wien-stubarum">
    <orgName><reg xml:lang="LAT">Stubarum</reg> <reg xml:lang="GER">Stubenviertel</reg></orgName>
    ...
  </org>
</org>
```

### Orte (pl\_\_)

```
pl__ + Siedlung + (-) Name
```

| Muster | Beispiel |
|--------|---------|
| Siedlung | `pl__wien` |

Beispiel (`pl__wien`):

```xml
<place xml:id="pl__wien" type="settlement" resp="kg">
  <placeName><reg>Wien</reg></placeName>
  <location><geo decls="LatLng">48.20849 16.37208</geo></location>
  <idno type="URL">https://www.geonames.org/2761369/vienna.html</idno>
</place>
```


## 5. Normalisierung

Die Normalisierung von Trigger-Formeln, Funktionen und Rollennamen erfolgt über projekteigene Normalisierungslisten, die in `normalisation_lists/` gepflegt werden. Die Normalisierung von Vornamen wird über einen externen Webservice (`medieval-legal-transactions.univie.ac.at/norm_names/`) verwaltet, der mit projekteigenen Zugangsdaten zugänglich ist. 


## 6. Validierung

Dieser Abschnitt beschreibt die Funktion der wesentlichen Attribute. Die kanonischen Wertelisten werden hier nicht ausgezählt: Sie sind im RelaxNG-Schema (`sources/schema/toolbox.rng`) festgelegt und werden bei jedem Validierungslauf gegen den Bestand abgeglichen. Der Validierungsbericht (`pipeline/output/validation_report.md`) listet Abweichungen mit Datei und Zeile.

- **`rs/@type`** klassifiziert, was die Referenz bezeichnet (Person, Organisation, Ort, Ereignis, Funktionsrolle).
- **`rs/@role`** klassifiziert die Rolle einer Funktion innerhalb eines Ereignisses (Aussteller, Empfänger, Zeuge, sonstige Beteiligung).
- **`roleName/@type`** klassifiziert die Art des Attributs oder der Relation an einer Entität (Beruf, Verwandtschaft, Titel, Stellvertretung, Topographie, Besitz u.a., siehe Abschnitt 2, Ebene 4).
- **`triggerstring/@n`** klassifiziert die Funktion einer Triggerformel (Disposition, Funktionstext, Begründung).
- **`@cert`** trägt einen Sicherheitsgrad zu einer Annotation, vergeben in mehreren Stufen.
- **`div/@resp`** sowie das `@resp`-Attribut an Indexeinträgen tragen ein Bearbeiter:innen-Kürzel; siehe Abschnitt 3, Schritt 1.

Bekannte Schreibvarianten in den Quelldaten werden bei der Tabellenerzeugung durch die Pipeline normalisiert; die XML-Quelldateien bleiben als geschützte Forschungsdaten unverändert. Eine Korrektur an der Quelle ist Aufgabe der Bearbeiter:innen.


## 7. Zitierhinweis

### Empfohlene Zitierweise

> *Stadt und Gemeinschaft Wien: Datenbank zu mittelalterlichen Wiener Rechtsgeschäften.* Universität Wien, 2026. https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/

### BibTeX

```
@misc{sugw_db,
  author       = {{Stadt und Gemeinschaft Wien}},
  title        = {Stadt und Gemeinschaft Wien: Datenbank zu mittelalterlichen Wiener Rechtsgeschaeften},
  year         = {2026},
  publisher    = {Universitaet Wien},
  url          = {https://max-steiney.github.io/db_for_medieval_legal_transactions_edition/}
}
```

Ein persistenter Identifikator (DOI) ist in Vorbereitung. Bei Einzelquellen-Zitaten empfiehlt sich die Angabe der Datei-ID (z.B. `QGW_1177-1414_0001`).


## 8. Lizenzierung

Alle Inhalte der Datenbank — die TEI-annotierten Quellentexte, die Register (Personen, Organisationen, Orte), die Normalisierungslisten sowie deren Darstellung im Frontend — stehen unter der Lizenz [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.de). Sie dürfen für nicht-kommerzielle Zwecke frei genutzt, geteilt und bearbeitet werden, sofern die Quelle genannt wird und Bearbeitungen unter derselben Lizenz veröffentlicht werden. Für die Namensnennung wird die Zitierweise aus Abschnitt 7 empfohlen.
