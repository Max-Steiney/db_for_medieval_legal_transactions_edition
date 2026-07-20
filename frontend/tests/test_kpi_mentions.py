"""Tests fuer die quellenbereinigte Gesamtnennungs-Zaehlung (Startseiten-KPI).

specification.md, Abschnitt "Quellenbereinigte Zaehlung": eine Person, die
in derselben Quelle mehrfach erwaehnt wird, traegt fuer diese Quelle genau
EINE Gesamtnennung bei. Glossar und beide Matrix-Tooltips sind entsprechend
formuliert; die Zaehlschleife in _kpi.py zaehlte bis 20.07.2026 dennoch pro
Annotations-Element (12.437 statt 10.482). Diese Tests koppeln Definition
und Zahl — genau die Pruefung, deren Fehlen den Widerspruch drei Monate
unbemerkt liess.

Fixpunkte aus den echten Quellen:
- Diemut (pe__diemut_QGW_II_I_105): 6x annotiert in Quelle 105
  (Bedingungskette "Schafferin Diemut ..."), zaehlt 1x.
- Berthold (pe__berthold_QGW_II_I_10): 2x annotiert in Quelle 10
  (Namensnennung + Formular-Rueckverweis "der Aussteller"), zaehlt 1x.
"""

from pathlib import Path

import pytest
from lxml import etree

from frontend.build._kpi import (
    _TEI_NS,
    _XP_PERSONS_EXCL_MENTIONED,
    _scan_released_tei,
)
from frontend.config import visible_corpora
from pipeline.config import SOURCES_DIR


def _person_refs(tree):
    """Alle pe__-Referenzen der KPI-XPath, in Dokumentreihenfolge."""
    refs = []
    for el in tree.xpath(_XP_PERSONS_EXCL_MENTIONED, namespaces=_TEI_NS):
        ref = (el.get("ref") or "").strip().lstrip("#")
        if ref.startswith("pe__"):
            refs.append(ref)
    return refs


def _doc(path_key, name):
    coll, sub = path_key.split("/", 1)
    return etree.parse(str(SOURCES_DIR / coll / sub / "done" / name))


@pytest.fixture(scope="module")
def kpis():
    totals, per_corpus = _scan_released_tei()
    return totals, per_corpus


class TestBekannteMehrfachFaelle:
    """Die dokumentierten Doppelzaehlungs-Faelle aus dem Audit 20.07.2026."""

    def test_diemut_sechsfach_annotiert(self):
        refs = _person_refs(_doc("QGW/Vienna_1177-1414_ready", "105.xml"))
        diemut = [r for r in refs if r == "pe__diemut_QGW_II_I_105"]
        # Datenlage: 6 Annotationen — zaehlt quellenbereinigt genau 1x.
        assert len(diemut) >= 2, "Mehrfach-Annotation im Testfall verschwunden"
        assert len(set(diemut)) == 1

    def test_berthold_formelverweis(self):
        refs = _person_refs(_doc("QGW/Vienna_1177-1414_ready", "10.xml"))
        berthold = [r for r in refs if r == "pe__berthold_QGW_II_I_10"]
        assert len(berthold) >= 2, "Formular-Rueckverweis im Testfall verschwunden"
        assert len(set(berthold)) == 1


class TestQuellenbereinigteTotals:
    """Die KPI-Summe muss der unabhaengig berechneten Paar-Zaehlung entsprechen."""

    def test_totals_gleich_distinkte_paare(self, kpis):
        totals, per_corpus = kpis
        pair_sum = 0
        raw_sum = 0
        for path_key in visible_corpora():
            coll, sub = path_key.split("/", 1)
            done = SOURCES_DIR / coll / sub / "done"
            if not done.exists():
                continue
            for f in sorted(done.rglob("*.xml")):
                try:
                    tree = etree.parse(str(f))
                except etree.XMLSyntaxError:
                    continue
                refs = _person_refs(tree)
                raw_sum += len(refs)
                pair_sum += len(set(refs))
        assert totals["person_mentions"] == pair_sum, (
            f"KPI {totals['person_mentions']} != quellenbereinigte "
            f"Paar-Zaehlung {pair_sum}"
        )
        # Rohe Element-Zaehlung darf nie wieder die KPI stellen, solange
        # Mehrfach-Annotationen im Korpus existieren.
        if raw_sum != pair_sum:
            assert totals["person_mentions"] < raw_sum

    def test_korpus_zeilen_summieren_zum_total(self, kpis):
        totals, per_corpus = kpis
        assert totals["person_mentions"] == sum(
            c["person_mentions"] for c in per_corpus
        )
