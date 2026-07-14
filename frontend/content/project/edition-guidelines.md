## 1. Projektkontext

Die Datenbank `db_for_medieval_legal_transactions` ist eine TEI-XML-basierte prosopographische Datenbank mittelalterlicher Wiener Rechtsgeschaefte (ca. 1177 bis 1524). Das Datenmodell orientiert sich an [TEI P5](https://tei-c.org/release/doc/tei-p5-doc/en/html/) und an Konventionen der digitalen Prosopographie.

### Entstehungsgeschichte

- **Masterarbeit:** Immobilientransfers Wien 1360 bis 1373 (Excel-basiert)
- **Konzeptualisierung:** Uebergang zu einer XML-basierten Datenbank
- **Dissertation:** *Im Netz der Stadt*, Erstellung der vollstaendigen DTD
- **Forschungsprojekt:** *Stadt und Gemeinschaft* (Universitaet Wien), parallele Nutzung und Erweiterung
- **Publikation:** *Die digitale Erfassung von mittelalterlichen Rechtsgeschaeften*, DHd-Blog, 31. Okt. 2021

Eine Kompatibilitaet mit [CIDOC-CRM](https://www.cidoc-crm.org/) ist langfristig angedacht.

### Quellensammlungen

Die Edition umfasst aktuell folgende Quellensammlungen:

| Sammlung | Zeitraum |
|----------|----------|
| QGW/Vienna\_1177-1414\_ready | 1177 bis 1414 |
| QGW/Vienna\_1415-1417 | 1415 bis 1417 |
| QGW/Vienna\_1458-66 | 1458 bis 1466 |
| QGW/Vienna\_1493-1500 | 1493 bis 1500 |
| QGW/Vienna\_1524 | 1524 |
| Stadtbuecher/Band\_1\_1395-1400\_ready | 1395 bis 1400 |

Die im Rahmen der Dissertation *Im Netz der Stadt* erfassten Sammlungen (Gewerbuch_D, Satzbuch_CD, Copeybuch_Zeibig, Widmerliste, Genanntenlisten) sind aus dem oeffentlichen Bestand zurueckgezogen.

Die Schema-Validierung erfolgt gegen `sources/schema/toolbox.rng` (RelaxNG).


## 2. Annotationsmodell

Das Annotationsmodell wird im Folgenden in vier konzeptuellen Ebenen dargestellt. Die Ebenen sind hierarchisch aufgebaut: Jede ist Teil der jeweils hoeheren, und die Verschachtelung im XML spiegelt diese Hierarchie wider.

| Ebene | Gegenstand | TEI-Element | Klassifikation |
|-------|-----------|-------------|----------------|
| 1. Ereignisse | Rechtsgeschaefte | `<rs type="event">` | ueber `<triggerstring n="disp">` |
| 2. Funktionen | Rollen im Rechtsgeschaeft | `<rs type="fn">` | ueber `@role` |
| 3. Entitaeten | Personen, Orte, Organisationen | `<rs type="person\|org\|place">` | ID-Verknuepfung mit Registern |
| 4. Attribute/Relationen | Eigenschaften und Beziehungen | `<roleName>` | ueber `@type` und `@corresp` |

### Ebene 1: Ereignisse

Ein Ereignis umschliesst eine vollstaendige rechtliche Handlung. Es wird mit `<rs type="event" ref="ev__*">` annotiert. Der `@ref`-Wert verweist auf eine Ereignis-ID.

Innerhalb des Ereignisses markiert `<triggerstring n="disp">` den **dispositiven Triggerstring**, das Verb oder die Verbalphrase, die die Art des Rechtsgeschaefts bestimmt. Die Kategorisierung erfolgt nicht a priori, sondern durch Extraktion dispositiver Verben und nachtraegliche Kategorienbildung.

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

*Quelle: QGW II/1 Nr. 1 (1198 bis 1230)*

### Ebene 2: Funktionen

Funktionen beschreiben die Rolle einer Person oder Organisation innerhalb eines Ereignisses. Sie werden mit `<rs type="fn" role="...">` annotiert. Die im Bestand vorkommenden Rollen klassifizieren die Beteiligung an einem Rechtsgeschaeft (Aussteller, Empfaenger, Zeuge, sonstige Beteiligung) sowie das Transaktionsgut. Bei der Rolle `other` wird die spezifische Funktion durch einen zusaetzlichen Triggerstring naeher bestimmt:

```xml
<rs type="fn" role="other">
  <triggerstring n="fn">mit Zustimmung</triggerstring> seiner
  <rs type="person" ref="pe__diemut_QGW_II_I_10">
    <roleName type="kin" corresp="pe__berthold_QGW_II_I_10">
      Gemahlin</roleName> Dimu/od</rs>
  und seiner Kinder und Erben
</rs>
```

*Quelle: QGW II/1 Nr. 10 (1274)*

### Ebene 3: Entitaeten

Entitaeten sind Personen, Organisationen und Orte. Sie werden mit `<rs>` annotiert und ueber `@ref` mit den Registern verknuepft.

| Typ | Element | ID-Praefix | Register |
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
<rs type="place" ref="pl__wien-immo_hoher_markt_wentkremen_33">
  zway hewser gelegen ... ze Wienn</rs>
```

**Hinweis zu Ortsreferenzen:** Orte sind im Annotationsbestand systematisch unterrepraesentiert. Direkte `<rs type="place">`-Referenzen sind selten. Orte werden primaer ueber `@corresp`-Attribute in `<roleName>` referenziert (topographische und Besitzrelationen, s. Ebene 4).

### Ebene 4: Attribute und Relationen

Attribute und Relationen werden mit `<roleName type="..." corresp="...">` annotiert. Der `@type` bestimmt die Art der Aussage; `@corresp` verknuepft sie mit einem Eintrag in einem der Register.

Zwei Arten von `@type`-Werten sind zu unterscheiden:

- **Attribute** charakterisieren die Entitaet selbst und benoetigen kein `@corresp` (z.B. ein Titel oder die Markierung "verstorben").
- **Relationen** verknuepfen die Entitaet ueber `@corresp` mit einem zweiten Eintrag (z.B. eine Verwandtschaftsbeziehung zu einer Person, eine Amtsfunktion in einer Organisation, eine topographische Lage in einem Ort).

Die im Bestand belegten Relationstypen umfassen unter anderem Verwandtschaft, Berufs- und Amtszuordnung, Stellvertretung, Freundschaft, Topographie und Besitzverhaeltnisse. Die maßgebliche Liste der zulaessigen Werte wird im Schema gefuehrt; die Ausweisung im Bestand ist im Validierungsbericht (`pipeline/output/validation_report.md`) abgebildet.

**Verwandtschaft (kin):**

```xml
<rs type="person" ref="pe__elisabeth_QGW_II_I_100">Elsbet, sein
  <roleName type="kin" corresp="pe__konrad_chrannest_QGW_II_I_99">
    hausvrowe</roleName>
</rs>
```

*Quelle: QGW II/1 Nr. 100 (1327)*

**Amtstraeger (occ):**

```xml
<rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus,
  <roleName type="occ" corresp="org__oesterreich-herzogtum">
    camerarius</roleName>
</rs>
```

*Quelle: QGW II/1 Nr. 10 (1274)*

**Titel (title):**

```xml
<rs type="person" ref="pe__herbert_auf_der_saeule_QGW_II_I_184">
  <roleName type="title">Grundherren</roleName>,
  <roleName type="title">hern</roleName> Herbortes auf der Seul</rs>
```

*Quelle: QGW II/1 Nr. 100 (1327)*

**Freundschaft (friend):**

```xml
<roleName type="friend"
  corresp="pe__albrecht_chirichhaimer_QGW_II_I_996">
  <add>lieben Freund</add></roleName>
```

*Quelle: QGW II/1 Nr. 996*

**Topographie und Besitz (topo, owner):**

```xml
<rs type="place" ref="pl__wien-immo_hoher_markt_wentkremen_33">
  <roleName type="owner" corresp="pe__katharina_StB_I_8">irew</roleName>
  zway hewser gelegen
  <roleName type="topo" corresp="pl__wien-hoher_markt_wentkremen">
    under den</roleName>
  <rs type="place" ref="pl__wien-hoher_markt_wentkremen">
    Wentchremen ze Wienn</rs>
</rs>
```

*Quelle: Stadtbuecher Bd. 1, Nr. 8*

**Stellvertretung (rep):**

```xml
<rs type="person" ref="pe__johann_cherner_QGW_II_I_810">
  Janns Cherner
  <roleName type="rep" corresp="pe__thomas_cherner_QGW_II_I_999">
    <add>fuer</add></roleName>
</rs>
```

*Quelle: QGW II/1 Nr. 999*

### Zusaetzliche Attribute

- **`@cert`**: Sicherheitsangabe zu einer Annotation, vergeben in Stufen.
- **`@select`**: traegt im Projekt einen zweiten XPointer-Verweis und kontextualisiert die durch `@corresp` etablierte Relation, indem ein zweiter Registereintrag (typischerweise ein Ort oder eine Organisation) mitreferenziert wird. Beispiel:

  ```xml
  <roleName type="occ"
            corresp="#org__tulln-dominikanerinnen"
            select="#pl__doebling">amptman</roleName>
  ```

  ("Amtmann der Tullner Dominikanerinnen mit Zustaendigkeit in Doebling".)

  Diese Verwendung ist eine projektspezifische Konvention und weicht von der TEI-Definition ab, nach der `@select` der Aufloesung von Ambiguitaeten zwischen alternativen Lesarten dient ([att.global.linking](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.linking.html)).

### Zusammenspiel der Ebenen

Ein vollstaendiges Beispiel zeigt die Verschachtelung aller vier Ebenen:

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

*Quelle: QGW II/1 Nr. 10 (1274). Bertoldus, Kaemmerer des Herzogtums Oesterreich, gibt mit Zustimmung seiner Gemahlin Dimu/od eine Rente an das Nonnenkloster St. Nikolaus.*


## 3. Tagging-Workflow

Die folgende Reihenfolge beschreibt den typischen Ablauf, in dem Annotationen in einer Quelle angelegt werden.

### Schritt 1: Bearbeiter:innen-Kuerzel

Jede:r Bearbeiter:in traegt ein Kuerzel in das `@resp`-Attribut des `<div>`-Elements ein:

```xml
<div type="abstract" resp="kg">
```

Die Zuordnung der Kuerzel zu konkreten Personen wird projektintern gepflegt (siehe Abschnitt 7).

### Schritt 2: Ereignisse

Alle Rechtsgeschaefte werden als Ereignisse markiert:

```xml
<rs type="event" ref="ev__QGW_II_I_1">...</rs>
```

Erwaehnte Ereignisse (nicht das Hauptereignis der Urkunde) erhalten das Suffix `_men_`:

```xml
<rs type="event" ref="ev__QGW_II_II_00606_men_1">...</rs>
```

### Schritt 3: Dispositivformeln

Dispositive Verben und Verbalphrasen werden mit `<triggerstring n="disp">` markiert:

```xml
<triggerstring n="disp">verkaufen</triggerstring>
```

Fuer implizite Informationen wird `<add>` innerhalb des Triggerstrings verwendet:

```xml
<triggerstring n="disp">haben <add>gegeben</add></triggerstring>
```

### Schritt 4: Funktionen

Allen beteiligten Personen und Organisationen wird eine Funktionsrolle zugewiesen:

```xml
<rs type="fn" role="issuer">...</rs>
<rs type="fn" role="recipient">...</rs>
<rs type="fn" role="witness">...</rs>
<rs type="fn" role="other"><triggerstring n="fn">mit Handen</triggerstring> ...</rs>
```

### Schritt 5: Entitaeten

Entitaeten werden zuerst mit leerem `<rs/>` markiert, dann wird die ID (`@ref`) zugewiesen:

```xml
<!-- Schritt 5a: Markierung -->
<rs type="person">Chunrat der Chrannest</rs>

<!-- Schritt 5b: ID-Zuweisung -->
<rs type="person" ref="pe__konrad_chrannest_QGW_II_I_99">
  Chunrat der Chrannest</rs>
```

### Schritt 6: Attribute und Relationen

Attribute und Relationen werden innerhalb der Entitaet annotiert:

```xml
<rs type="person" ref="pe__berthold_QGW_II_I_10">Bertoldus,
  <roleName type="occ" corresp="org__oesterreich-herzogtum">
    camerarius</roleName>
</rs>
```

Wenn eine Relation neben dem `@corresp`-Verweis durch einen zweiten Registereintrag kontextualisiert werden soll, wird `@select` verwendet (zur Funktion siehe Abschnitt 2, Ebene 4):

```xml
<roleName type="occ"
          corresp="#org__tulln-dominikanerinnen"
          select="#pl__doebling">amptman</roleName>
```

### Schritt 7: Masseinheiten

Masseinheiten und Waehrungsangaben werden mit `<measure/>` markiert.

### Zusaetzliche Konventionen

- **`@cert`**: Wahrscheinlichkeitsangabe fuer unsichere Zuordnungen
- **`<unclear>`**: Unleserliche oder schwer lesbare Passagen
- **`<add>`**: Editorische Ergaenzungen und implizite Informationen


## 4. ID-Konstruktionsregeln

### Ereignisse (ev\_\_)

```
ev__ + Quellenabkuerzung + (_) Nummer
```

| Muster | Beispiel |
|--------|---------|
| Hauptereignis | `ev__QGW_II_I_1` |
| Hauptereignis (mit Nullen) | `ev__SB_CD_00642` |
| Erwaehnte Ereignisse | `ev__QGW_II_II_00606_men_1` |

Im Bestand treten zusaetzliche Sondervarianten auf, etwa fuer Privilegienurkunden. Ihre genaue Bildungsregel ist projektintern zu klaeren.

### Personen (pe\_\_)

```
pe__ + normalisierter_Vorname + (_) normalisierter_Nachname + (_) Quellenabkuerzung + (_) Nummer
```

| Muster | Beispiel |
|--------|---------|
| Standard | `pe__johann_maurperger_QGW_II_II_2870` |
| Homonyme (Suffixunterscheidung) | `pe__agnes_QGW_II_II_3250_a`, `pe__agnes_QGW_II_II_3250_b` |
| Ohne Nachname (Beruf stattdessen) | `pe__berthold_QGW_II_I_10` |

**Konventionen:**

- Keine Umlaute in IDs.
- Vornamen werden ueber eine externe Normalisierungstabelle vereinheitlicht (siehe Abschnitt 5).
- Nachnamen stammen aus dem Quellenregister; fehlt ein Register, wird die Originalschreibung verwendet.
- Bei fehlendem Nachnamen wird der Beruf verwendet.
- Bei Frauen und Kindern wird ein potenzieller Nachname in `<add>` ergaenzt.

Diese Konventionen beschreiben die im Bestand erkennbare Praxis; Detailausnahmen werden im konkreten Einzelfall editorisch entschieden.

### Individualisierungsverfahren

Die Disambiguierung von Homonymen erfolgt durch das Suffix `_a` / `_b` (usw.) an der Personen-ID. Dieses Verfahren greift, wenn derselbe Name in derselben Quelle mehrfach vorkommt und die Personen durch Kontextinformationen (Beruf, Verwandtschaft, Amt) unterschieden werden koennen.

**Register-Struktur (personList.xml):**

Jeder Personeneintrag enthaelt:

- `<persName>`: `<forename>`, `<surname>` (jeweils mit `<reg>` fuer normalisierte Form), `<addName>` (Beiname), `<genName>` (Generationsname)
- `<death notAfter="">`: Todesdatum
- `<idno>`: Verknuepfung mit externen Normdateien
- `@sex` (f/m), `@source`, `@resp`, `@cert`
- `@sameAs`: Queridentifikation mit einer anderen Person im Register

**Namenskonvention als Individualisierungsstrategie:**

Die Struktur der Personen-ID selbst, normalisierter Vorname plus Nachname plus Quelle plus Nummer, bildet bereits eine erste Individualisierungsschicht. Unterschiedliche Quellen erzeugen unterschiedliche IDs fuer potentiell identische Personen. Die Zusammenfuehrung erfolgt ueber `@sameAs` im Register; sie ist eine historisch-prosopographische Urteilsfrage und keine algorithmische Operation.

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

Die im Register vorkommenden Organisationstypen reichen von uebergeordneten Herrschaftsverbaenden (Reich, Koenigreich, Herzogtum) ueber kirchliche Einrichtungen (Dioezese, Pfarre, Kirche, Kapelle, Kloster, Altar, Messe, Bruderschaft) bis zu staedtischen und karitativen Einrichtungen (Stadtverwaltung, Spital).

### Orte (pl\_\_)

```
pl__ + Siedlung + (-) Name
```

| Muster | Beispiel |
|--------|---------|
| Siedlung | `pl__wien` |
| Strasse | `pl__wien-hoher_markt` |
| Immobilie | `pl__wien-immo_karntnerstrasse_1` |

Das Praefix `immo_` kennzeichnet Immobilien. Hierarchisierung (Haeuser in Strassen) ist moeglich.


## 5. Normalisierung

Die Normalisierung von Trigger-Formeln, Funktionen und Rollennamen erfolgt ueber projekteigene Normalisierungslisten, die in `normalisation_lists/` gepflegt werden. Die Normalisierung von Vornamen wird ueber einen externen Webservice (`medieval-legal-transactions.univie.ac.at/norm_names/`) verwaltet, der mit projekteigenen Zugangsdaten zugaenglich ist. Die normalisierten Formen fliessen in die Personen-IDs und Register-Eintraege ein.

Nicht alle Triggerstrings und roleName-Eintraege im Bestand sind durch die Normalisierungslisten abgedeckt.


## 6. Vokabular und Validierung

Dieser Abschnitt beschreibt die Funktion der wesentlichen Attribute. Die kanonischen Wertelisten werden hier nicht ausgezaehlt: Sie sind im RelaxNG-Schema (`sources/schema/toolbox.rng`) festgelegt und werden bei jedem Validierungslauf gegen den Bestand abgeglichen. Der Validierungsbericht (`pipeline/output/validation_report.md`) listet Abweichungen mit Datei und Zeile.

- **`rs/@type`** klassifiziert, was die Referenz bezeichnet (Person, Organisation, Ort, Ereignis, Funktionsrolle).
- **`rs/@role`** klassifiziert die Rolle einer Funktion innerhalb eines Ereignisses (Aussteller, Empfaenger, Zeuge, sonstige Beteiligung, Transaktionsgut).
- **`roleName/@type`** klassifiziert die Art des Attributs oder der Relation an einer Entitaet (Beruf, Verwandtschaft, Titel, Stellvertretung, Topographie, Besitz u.a., siehe Abschnitt 2, Ebene 4).
- **`triggerstring/@n`** klassifiziert die Funktion einer Triggerformel (Disposition, Funktionstext, Begruendung).
- **`@cert`** traegt einen Sicherheitsgrad zu einer Annotation, vergeben in mehreren Stufen.
- **`div/@resp`** sowie das `@resp`-Attribut an Registereintraegen tragen ein Bearbeiter:innen-Kuerzel; siehe Abschnitt 7.

Bekannte Schreibvarianten und Tippfehler in den Quelldaten werden bei der Tabellenerzeugung durch die Pipeline normalisiert; die XML-Quelldateien bleiben als geschuetzte Forschungsdaten unveraendert. Eine Korrektur an der Quelle ist Aufgabe der Bearbeiter:innen.


## 7. Bearbeiter:innen-Konvention

Das Attribut `@resp` an `<div>`-Elementen in den Quelldokumenten und an Eintraegen in den Registern traegt ein kurzes Bearbeiter:innen-Kuerzel. Mehrere Kuerzel koennen durch Bindestrich verbunden werden, um eine gemeinsame Verantwortung mehrerer Bearbeiter:innen auszuweisen (z.B. `df-hk-kg`).

Die Zuordnung der Kuerzel zu konkreten Personen wird projektintern gepflegt und ist nicht Bestandteil der oeffentlichen Edition. Pflegestelle ist die Datei `normalisation_lists/editors/Name_of_Editors.csv`.


## 8. Zitierhinweis

### Empfohlene Zitierweise

> *Stadt und Gemeinschaft Wien: Datenbank zu mittelalterlichen Wiener Rechtsgeschaeften.* Universitaet Wien, 2026. https://chpollin.github.io/db_for_medieval_legal_transactions/

### BibTeX

```
@misc{sugw_db,
  author       = {{Stadt und Gemeinschaft Wien}},
  title        = {Stadt und Gemeinschaft Wien: Datenbank zu mittelalterlichen Wiener Rechtsgeschaeften},
  year         = {2026},
  publisher    = {Universitaet Wien},
  url          = {https://chpollin.github.io/db_for_medieval_legal_transactions/}
}
```

Ein persistenter Identifikator (DOI) ist in Vorbereitung. Bei Einzelquellen-Zitaten empfiehlt sich die Angabe der Datei-ID (z.B. `QGW_1177-1414_0001`).


## 9. Lizenzierung

Die Lizenzierung wird auf drei Geltungsbereiche bezogen.

### Die digitale Edition als Werk

Die im Rahmen der Modernisierung erstellten Bestandteile (die generierten HTML-Seiten, das Layout, die vorliegenden Annotationsrichtlinien, der Pipeline-Code, das RelaxNG-Schema und die Visualisierungen) werden unter der [Creative Commons Attribution 4.0 International License (CC BY 4.0)](http://creativecommons.org/licenses/by/4.0/) veroeffentlicht. Der vollstaendige Lizenztext liegt im Repository unter `LICENSE`.

### Die TEI-Quelldaten und Register

Die Quelldokumente in `sources/` und die drei Register in `indices/` tragen ihre Urheber- und Bearbeitungsangaben in den eigenen `<publicationStmt>`- und `<sourceDesc>`-Elementen. Diese Angaben werden im Rahmen der Modernisierung nicht ueberschrieben. Eine einheitliche Lizenzangabe fuer die oeffentliche Veroeffentlichung dieser Daten ist zwischen den Projektpartner:innen und der Universitaet Wien zu vereinbaren; bis zu dieser Vereinbarung gelten die in den Quelldateien selbst dokumentierten Angaben.

### Die Normalisierungslisten

Die Normalisierungslisten in `normalisation_lists/` werden Gegenstand einer ausdruecklichen Lizenzvereinbarung sein. Eine Lizenzangabe pro Datei ist vorgesehen.


## 10. Versionsgeschichte

| Datum | Aenderung |
|-------|----------|
| 2026-02-20 | Ersterfassung des Korpus, Aufbau der Python-Pipeline und der automatisierten Tests |
| 2026-03-01 | RelaxNG-Schema, Integritaetspruefungen und Klassifikation der Annotationsbefunde |
| 2026-03-01 | Editionsrichtlinien v1: erstmalige Konsolidierung, Markdown-Build-Pipeline, Erfuellung der Gutachten-Anforderungen #5+#6 |
| 2026-03-12 | Kontrolliertes Vokabular und Normalisierung bekannter Tippfehler in der Pipeline |
| 2026-03-12 | Richtlinien-Ueberarbeitung: Restrukturierung, Zwei-Spalten-Layout, Hyperlinks, Zitierhinweis, Lizenz |
| 2026-03-20 | Korpus-Bereinigung: Rueckzug der dissertationsspezifischen Sammlungen aus dem oeffentlichen Bestand |
| 2026-04 | URI-Plausibilitaetspruefung, Worked-Examples im Validierungsreport |
| 2026-04-28 | Verifikation gegen den Bestand: `@select` als projektspezifische Konvention dokumentiert; Vokabular-Abschnitt auf Funktionsbeschreibung umgestellt; Bearbeiter:innen-Konvention von Personenliste entkoppelt; Lizenzierung auf drei Geltungsbereiche aufgeschluesselt |

Die detaillierte Aenderungshistorie ist in der Git-Historie des Repositoriums (`git log`) dokumentiert; den aktuellen Lieferstand fasst `knowledge/status.md` zusammen.
