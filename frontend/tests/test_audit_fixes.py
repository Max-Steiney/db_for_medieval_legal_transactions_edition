"""Regressionstests zu den Befunden des inhaltlichen Audits vom 20.07.2026.

Jeder Test sichert einen behobenen Audit-Befund gegen Rueckfall:
- F1: sichtbare technische IDs in Personen-Profilen (Notiz + rep-Relation)
- F2: Korpus-Scope-Texte (Stadtbuecher sind noch nicht freigeschaltet,
      Frontend-Meeting 17.06.2026)
- F3: Gender-Doppelpunkt statt Gender-Stern in allen Content-Quellen
- F6: Projekt-Mail im Impressum
(F5, canonical-Link: test_build.py::test_canonical_is_absolute)
"""

import re
from pathlib import Path

import pytest

from frontend.aggregator import build_person_profiles
from frontend.aggregator import _shared as agg_shared
from frontend.aggregator.person_profiles import (
    _humanize_entity_id,
    _resolve_ids_in_text,
)

BASE = Path(__file__).resolve().parents[1]

DOC_STUB = {
    "url":              "documents/QGW/Vienna_1177-1414_ready/61.html",
    "idno":             "61",
    "date_display":     "1288",
    "date_iso":         "12880101",
    "collection_label": "QGW II/1 (1177–1414)",
    "collection_path":  "QGW/Vienna_1177-1414_ready",
    "regest":           "Test-Regest",
}


@pytest.fixture(autouse=True)
def _reset_csv_cache():
    agg_shared._csv_cache.clear()
    agg_shared._released_file_keys_cache = None
    yield
    agg_shared._csv_cache.clear()
    agg_shared._released_file_keys_cache = None


# --- F1: ID-Aufloesung (Unit) ---

class TestIdResolutionUnit:

    def test_registername_ersetzt_id(self):
        out = _resolve_ids_in_text(
            "Schwester v. pe__gertrud_QGW_II_I_105",
            {"pe__gertrud_QGW_II_I_105": "Gertrud Poll"}, {})
        assert out == "Schwester v. Gertrud Poll"

    def test_dedup_bei_vorangestelltem_namen(self):
        out = _resolve_ids_in_text(
            "Gem. v. Konrad Futrer pe__konrad_futrer_QGW_II_I_251",
            {"pe__konrad_futrer_QGW_II_I_251": "Konrad Futrer"}, {})
        assert out == "Gem. v. Konrad Futrer"

    def test_unaufloesbare_id_wird_humanisiert(self):
        out = _resolve_ids_in_text("Gem. pe__niklas_lebansorg", {}, {})
        assert out == "Gem. Niklas Lebansorg"

    def test_leerer_registername_faellt_nicht_auf_rohe_id(self):
        # _load_org_names faellt bei leerem name_reg auf die ID zurueck --
        # die Aufloesung darf das nie durchreichen.
        out = _resolve_ids_in_text(
            "Vertritt org__oesterreich",
            {}, {"org__oesterreich": "org__oesterreich"})
        assert "org__" not in out
        assert "Oesterreich" in out

    def test_humanize_verwirft_korpus_segmente(self):
        assert _humanize_entity_id("pe__konrad_futrer_QGW_II_I_251") == "Konrad Futrer"


# --- F1: ID-Aufloesung (Integration ueber echte Pipeline-CSVs) ---

class TestIdResolutionProfiles:

    PE_KATHARINA = "pe__katharina_QGW_II_I_1537_a"   # Notiz "Gem. pe__niklas_lebansorg"
    PE_OREL = "pe__siegfried_orel_QGW_II_I_61"       # rep-Relation zu org__wien

    def test_note_ohne_rohe_ids(self):
        out = build_person_profiles({self.PE_KATHARINA: [DOC_STUB]})
        note = out[self.PE_KATHARINA]["note"]
        assert "pe__" not in note and "org__" not in note
        assert "Niklas Lebansorg" in note

    def test_rep_partner_org_aufgeloest(self):
        out = build_person_profiles({self.PE_OREL: [DOC_STUB]})
        reps = out[self.PE_OREL]["relations"]["rep"]
        assert reps, "rep-Relation von Siegfried Orel fehlt"
        wien = [e for e in reps if e["other_id"] == "org__wien"]
        assert wien, "org__wien-Relation fehlt"
        assert wien[0]["other_name"] == "Wien"
        assert wien[0]["other_kind"] == "org"


# --- F2: Korpus-Scope-Texte ---

def test_startseite_tooltip_ohne_stadtbuecher_als_bestand():
    src = (BASE / "templates" / "startseite.html").read_text(encoding="utf-8")
    assert "und die Wiener Stadtb" not in src
    assert "weitere Korpora" in src


def test_quellenliste_beispiele_ohne_stadtbuecher():
    # Beispiel-Korpuslabels in Such-/Signatur-Tooltips duerfen nur
    # tatsaechlich geladene Korpora nennen.
    src = (BASE / "templates" / "index.html").read_text(encoding="utf-8")
    assert "Stadtb&uuml;cher Bd. 1" not in src


def test_glossar_stadtbuecher_als_vorbereitung():
    md = (BASE / "content" / "project" / "glossar.md").read_text(encoding="utf-8")
    assert "In Vorbereitung (im Frontend noch nicht freigeschaltet)" in md


# --- F3: Gender-Doppelpunkt in allen Content-Quellen ---

def test_kein_gender_stern_in_content():
    star = re.compile(r"\w\*in(nen)?\b")
    for f in sorted((BASE / "content").rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = star.search(text)
        assert not m, f"Gender-Stern in {f.name}: ...{text[max(0, m.start()-30):m.end()+10]!r}"


# --- F6: Projekt-Mail im Impressum ---

def test_impressum_hat_projektmail():
    md = (BASE / "content" / "impressum.md").read_text(encoding="utf-8")
    assert "stadtgemeinschaftwien.ioeg@univie.ac.at" in md


# --- Audit-Punkt 9: Browser-Tab-Titel + Werktitel-Trennzeichen ---

def test_title_tag_traegt_projektname():
    # Tab-Titel war "<Seite>, Datenbank" ohne Projektname; jetzt
    # "<Seite> – Stadt und Gemeinschaft Wien".
    src = (BASE / "templates" / "base.html").read_text(encoding="utf-8")
    assert "&ndash; Stadt und Gemeinschaft Wien</title>" in src
    assert ", Datenbank</title>" not in src


def test_werktitel_mit_doppelpunkt():
    # Kanonische Zitierform (Annotationsrichtlinien §7): "Stadt und
    # Gemeinschaft Wien: Datenbank zu ..." — die Komma-Variante darf in
    # Impressum und Zitier-Helfer nicht zurueckkehren.
    for rel in ("content/impressum.md", "static/js/document.js"):
        text = (BASE / rel).read_text(encoding="utf-8")
        assert "Stadt und Gemeinschaft Wien, Datenbank zu" not in text, rel
    impressum = (BASE / "content" / "impressum.md").read_text(encoding="utf-8")
    assert "Stadt und Gemeinschaft Wien: Datenbank zu" in impressum
