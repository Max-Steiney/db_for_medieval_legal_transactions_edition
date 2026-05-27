"""Pfade und Konstanten für das Test-Set.

Das Test-Set liegt im Edition-Repo, liest TEI und Register aus dem
Pipeline-Repo (relativ) und vergleicht gegen die JSONs im eigenen
`data/`-Ordner. Spätere URL-Varianten (z. B. Raw-GitHub) können hier
ergänzt werden, ohne andere Module anzufassen.
"""

import os
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
EDITION_ROOT = TESTS_DIR.parent
PIPELINE_ROOT = (EDITION_ROOT.parent / "db_for_medieval_legal_transactions").resolve()

# Eingangsquellen im Pipeline-Repo
TEI_SOURCES_DIR = PIPELINE_ROOT / "sources"
INDICES_DIR = PIPELINE_ROOT / "indices"

PERSON_LIST = INDICES_DIR / "personList.xml"
ORG_LIST = INDICES_DIR / "orgList.xml"
PLACE_LIST = INDICES_DIR / "placeList.xml"

# Test-Target: der gerenderte Build, gegen den verglichen wird. Das
# Test-Set liest TEI im released-Scope (is_released_corpus, siehe
# parse_tei.iter_sources). Genau diesen Umfang rendert die interne
# Fassung docs-intern/; der oeffentliche Build docs/ ist seit der
# Korpus-Trennung bewusst schmaler (nur PUBLIC_CORPORA) und meldete
# dadurch Scope-Mismatches, die keine Drift sind (z. B. date_range.QGW
# bis 1457 im released-TEI gegen 1414 im oeffentlichen Build). Default-
# Ziel ist deshalb docs-intern. Ueber VERIFICATION_DOCS_DIR laesst sich
# ein anderes Verzeichnis erzwingen (Name relativ zum Edition-Root oder
# absoluter Pfad), z. B. VERIFICATION_DOCS_DIR=docs fuer den
# oeffentlichen Build.
_docs_override = os.environ.get("VERIFICATION_DOCS_DIR", "").strip()
if _docs_override:
    _docs_path = Path(_docs_override)
    DOCS_DIR = _docs_path if _docs_path.is_absolute() else (EDITION_ROOT / _docs_path)
else:
    DOCS_DIR = EDITION_ROOT / "docs-intern"

DATA_DIR = DOCS_DIR / "data"

# Gerenderte HTML-Outputs fuer die HTML-Coverage-Stufe. Profil-HTMLs
# liegen unter <build>/register/, Quellen unter <build>/documents/.
HTML_REGISTER_PERSONS = DOCS_DIR / "register" / "persons"
HTML_REGISTER_ORGS = DOCS_DIR / "register" / "orgs"
HTML_DOCUMENTS = DOCS_DIR / "documents"

# Report-Ausgabe
REPORTS_DIR = TESTS_DIR / "reports"

# TEI-Namespace
TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}

# Quellenkorpora, deren TEI das Test-Set unabhaengig re-aggregiert und
# gegen die JSON-Outputs vergleicht. Satzbuch_CD ist zwar seit 2026-05
# freigegeben und Teil der internen Fassung (Default-Ziel), wird hier aber
# bewusst noch NICHT gelesen: der Parser extrahiert SB_CD-Datumsangaben und
# Personennennungen noch nicht zuverlaessig (andere Annotationsstruktur).
# Solange SB_CD nicht im Scope ist, behandeln die per-Korpus-Checks es als
# known_gap statt als Mismatch (siehe compare.run_checks). Vollabdeckung
# von SB_CD ist ein eigener Folgepunkt.
COLLECTIONS_WITH_TEI = ("QGW", "Stadtbuecher")
