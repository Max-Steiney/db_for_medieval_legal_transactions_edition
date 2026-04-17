# Architektur

Bausteine der Edition: wie aus den TEI-Quellen die statische Website entsteht. Konzeptionell, ohne Implementierungsdetails.

## Datenfluss

<!-- TEI-XML-Quellen → Python/lxml-Pipeline → JSON/CSV-Zwischenformate → Jinja2-Templates → statische HTML-Dateien → Auslieferung über GitHub Pages. -->

## TEI als Quelle

<!-- Warum TEI: wissenschaftlicher Standard, Annotation und Text in einem Dokument, langfristig tragfähig. Siehe [[data#Annotationsebenen]]. -->

## Pipeline

<!-- Was die Pipeline leistet: Validierung, Transformation, Aggregation. Warum Python/lxml: Werkzeugkette ohne Java-Abhängigkeit, einfache Erweiterbarkeit, Regressionstests möglich. -->

## Templates

<!-- Jinja2-Templates als gemeinsamer Rahmen für alle Seiten. Ein base.html hält Navigation und Fußzeile zentral. Änderungen am Rahmen greifen in allen Seiten. -->

## Statische HTML-Ausgabe

<!-- Warum statisch: einfache Hosting-Infrastruktur, hohe Ladegeschwindigkeit, Zitierbarkeit einzelner Seiten, keine laufenden Serverkosten. Konsequenz: dynamische Filter werden clientseitig über JSON-Indexe realisiert. -->

## Trennung Quelle und Build-Output

<!-- Zwei Repositories: Pipeline-Repo (Quelle, Templates, Build-Code) und Edition-Repo (reiner Build-Output für GitHub Pages). Änderungen am UI gehören in die Quelle, werden gebaut, dann synchronisiert. -->

### Warum zwei Repos

<!-- Build-Output ist groß (tausende Regesten-HTMLs), lenkt in der Versionskontrolle der Quelle vom Wesentlichen ab. Getrenntes Output-Repo hält die Historie der Inhaltsänderungen übersichtlich. -->

### Konsequenz für Arbeitsweise

<!-- Inhaltliche Änderung → Pipeline-Repo → Build → Sync. Im Edition-Repo werden keine HTMLs direkt editiert, außer Meta-Dateien (CLAUDE.md, knowledge/). -->

## Clientseitige Suche und Filter

<!-- Suche und Filter laufen im Browser gegen vorgebaute JSON-Indexe. Warum: keine Serverlogik, Zitierbarkeit der Anfrage-URL möglich, Performance. Grenze: sehr große Datenmengen erfordern clientseitige Indexierungsstrategien. -->

## Auslieferung über statisches Hosting

<!-- GitHub Pages als Auslieferungskanal. Warum: kostenlos, zuverlässig, Versionierung über Git. Konsequenz: Unterordner-Struktur ist frei wählbar, case-sensitive, keine serverseitige URL-Umschreibung. -->

## Grenzen der Architektur

<!-- Was die statische Architektur nicht leistet: Echtzeit-Daten, persistierte Nutzereingaben, Auth. Warum das hier akzeptabel ist: Edition ist Publikationsform, nicht kollaboratives Werkzeug. -->

## Siehe auch

- [[data]] — was verarbeitet wird
- [[requirements]] — welche funktionalen Anforderungen gelten
- [[ui-design]] — wie die Bausteine zu einer Oberfläche werden
