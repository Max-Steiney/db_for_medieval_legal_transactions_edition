# Inhaltsdateien pflegen

Dieser Ordner enthält die redaktionell pflegbaren Texte der Website. Der Build
liest sie und setzt sie in die jeweilige Seite ein. Die Inhalte liegen bei den
Projektpartnern, Struktur und Build bei Digital Humanities Craft.

## Welche Datei wird zu welcher Seite

| Datei | Seite im Frontend |
|---|---|
| `project/about.md` | Über das Projekt |
| `project/glossar.md` | Glossar |
| `project/edition-guidelines.md` | Editionsrichtlinien |
| `impressum.md` | Impressum und Lizenzhinweise |

Jede dieser Dateien ist reines Markdown. Eine Überschrift mit zwei Rauten
(`## Titel`) beginnt einen Abschnitt, der Text darunter ist der Inhalt. Die
Abschnittsüberschriften werden zugleich zum Inhaltsverzeichnis der Seite.

## Glossar pflegen

Im Glossar ist ein Begriff ein Abschnitt. Die Überschrift ist der Begriff, der
Absatz darunter die Definition. Die Begriffe stehen alphabetisch.

```markdown
## Quellenkorpus

Ein Quellenkorpus ist die oberste Ordnungsebene der Datenbank. Er fasst
überlieferungsgeschichtlich oder inhaltlich zusammengehörige Quellen zu einem
benannten Bestand zusammen ...
```

Ein Begriff lässt sich auf einen anderen Glossarbegriff verlinken. `[[#Quelle]]`
verweist auf den Eintrag „Quelle", `[[#Quelle|Quellen]]` zeigt stattdessen das
Wort „Quellen" an und verlinkt auf denselben Eintrag. Der Eintrag
„Quellenkorpus" ist als ausgefülltes Beispiel hinterlegt, die übrigen Begriffe
tragen einen Platzhalter und warten auf die redaktionelle Definition.

## Build

Eine Änderung an diesen Dateien wird sichtbar, sobald die Seite neu gebaut wird:

```
python -m frontend build
```

Der Build schreibt die öffentliche Fassung nach `docs/`, von wo GitHub Pages sie
ausliefert. Öffentlich erscheinen nur fertige Bestände; die interne Fassung
(`python -m frontend build --audience intern`, Ausgabe nach `docs-intern/`) kann
auch unfertige Bestände zeigen.
