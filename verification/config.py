"""Pfade und Konstanten für das Test-Set.

Das Test-Set liegt im Edition-Repo, liest TEI und Register aus dem
Pipeline-Repo (relativ) und vergleicht gegen die JSONs im eigenen
`data/`-Ordner. Spätere URL-Varianten (z. B. Raw-GitHub) können hier
ergänzt werden, ohne andere Module anzufassen.
"""

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

# Test-Targets: JSONs im Edition-Repo. Der Build schreibt nach
# docs/data/, nicht nach data/. Frueher lag hier ein paralleler
# data/-Snapshot — das fuehrte zu Mismatches gegen alten Stand,
# nicht gegen echte Drift.
DATA_DIR = EDITION_ROOT / "docs" / "data"

# Report-Ausgabe
REPORTS_DIR = TESTS_DIR / "reports"

# TEI-Namespace
TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}

# Quellenkorpora mit verfügbarem TEI (nur diese werden gegen JSON verglichen)
COLLECTIONS_WITH_TEI = ("QGW", "Stadtbuecher")
