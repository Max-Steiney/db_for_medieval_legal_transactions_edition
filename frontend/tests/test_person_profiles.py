"""Tests for the Person-Profile feature: aggregator, build step, linking."""

import pytest

from frontend.aggregator import build_person_profiles
from frontend.aggregator import _shared as agg_shared


# Realistic reverse_index fragment for two persons that share a kin
# relation (Diemut "Gemahlin" Berthold, ev__QGW_II_I_10, file f__QGW_10).
# Verified against pipeline/output/kin_relations_in_sources.csv first line.

PE_DIEMUT  = "pe__diemut_QGW_II_I_10"
PE_BERTHOLD = "pe__berthold_QGW_II_I_10"

DOC_10 = {
    "url":              "documents/QGW/Vienna_1177-1414_ready/10.html",
    "idno":             "10",
    "date_display":     "1274",
    "date_iso":         "12740101",
    "collection_label": "QGW II/1 (1177–1414)",
    "collection_path":  "QGW/Vienna_1177-1414_ready",
    "regest":           "Test-Regest fuer 10",
}

REVERSE_INDEX_PAAR = {
    PE_DIEMUT:   [DOC_10],
    PE_BERTHOLD: [DOC_10],
}


@pytest.fixture(autouse=True)
def _reset_csv_cache():
    """Clear the CSV cache between tests — the module-level cache would
    otherwise drag filter results from earlier tests into later ones."""
    agg_shared._csv_cache.clear()
    agg_shared._released_file_keys_cache = None
    yield
    agg_shared._csv_cache.clear()
    agg_shared._released_file_keys_cache = None


class TestPersonProfileAggregator:
    """build_person_profiles produces the expected profile dict."""

    def test_returns_only_person_ids(self):
        rev = {**REVERSE_INDEX_PAAR, "org__irgendwas": [DOC_10],
               "pl__wien": [DOC_10]}
        out = build_person_profiles(rev)
        assert all(pid.startswith("pe__") for pid in out.keys())

    def test_skips_persons_without_sources(self):
        rev = {PE_DIEMUT: []}
        out = build_person_profiles(rev)
        assert PE_DIEMUT not in out

    def test_known_person_has_stammdaten(self):
        out = build_person_profiles(REVERSE_INDEX_PAAR)
        diemut = out[PE_DIEMUT]
        assert diemut["forename"]
        assert diemut["sex"] == "f"
        assert diemut["display"]
        assert diemut["id"] == PE_DIEMUT

    def test_sources_passed_through(self):
        out = build_person_profiles(REVERSE_INDEX_PAAR)
        diemut = out[PE_DIEMUT]
        assert diemut["source_count"] == 1
        assert diemut["sources"][0]["idno"] == "10"
        assert diemut["active_min"] == "1274"

    def test_kin_relation_resolved_bidirectionally(self):
        out = build_person_profiles(REVERSE_INDEX_PAAR)
        # Diemut sees Berthold as counterpart.
        diemut_kin = out[PE_DIEMUT]["relations"]["kin"]
        diemut_others = {e["other_id"] for e in diemut_kin}
        assert PE_BERTHOLD in diemut_others, (
            "Diemut should have Berthold listed in kin relations"
        )
        # Berthold sees Diemut as counterpart.
        bert_kin = out[PE_BERTHOLD]["relations"]["kin"]
        bert_others = {e["other_id"] for e in bert_kin}
        assert PE_DIEMUT in bert_others, (
            "Berthold should have Diemut listed in kin relations"
        )

    def test_relation_carries_source_link(self):
        out = build_person_profiles(REVERSE_INDEX_PAAR)
        diemut_kin = out[PE_DIEMUT]["relations"]["kin"]
        for e in diemut_kin:
            if e["other_id"] == PE_BERTHOLD:
                assert e["idno"] == "10"
                assert "documents/QGW" in e["url"]
                assert e["label"], "label should be non-empty"
                return
        pytest.fail("Berthold relation not found")

    def test_role_perspective_is_set(self):
        out = build_person_profiles(REVERSE_INDEX_PAAR)
        # In kin_relations.csv: person_key=Diemut, related_key=Berthold.
        # Diemut sees herself as 'subject' (bearer of the "Gemahlin" label),
        # Berthold sees Diemut as 'counterpart'.
        diemut_to_berthold = next(
            e for e in out[PE_DIEMUT]["relations"]["kin"]
            if e["other_id"] == PE_BERTHOLD
        )
        berthold_from_diemut = next(
            e for e in out[PE_BERTHOLD]["relations"]["kin"]
            if e["other_id"] == PE_DIEMUT
        )
        assert diemut_to_berthold["role"] == "subject"
        assert berthold_from_diemut["role"] == "counterpart"


class TestPersonProfileBuildStep:
    """_build_person_profiles renders one HTML per profile."""

    def test_writes_html_per_profile(self, tmp_path, monkeypatch):
        from frontend.tests.conftest import patch_build_path
        from frontend.build._helpers import _init_jinja
        from frontend.build._pages import _build_person_profiles

        patch_build_path(monkeypatch, "DOCS_DIR", tmp_path)
        env = _init_jinja()
        _build_person_profiles(REVERSE_INDEX_PAAR, env)

        out_dir = tmp_path / "register" / "persons"
        assert out_dir.is_dir()
        diemut_file = out_dir / f"{PE_DIEMUT}.html"
        bert_file   = out_dir / f"{PE_BERTHOLD}.html"
        assert diemut_file.exists()
        assert bert_file.exists()

    def test_html_contains_relation_to_partner(self, tmp_path, monkeypatch):
        from frontend.tests.conftest import patch_build_path
        from frontend.build._helpers import _init_jinja
        from frontend.build._pages import _build_person_profiles

        patch_build_path(monkeypatch, "DOCS_DIR", tmp_path)
        env = _init_jinja()
        _build_person_profiles(REVERSE_INDEX_PAAR, env)

        diemut_html = (tmp_path / "register" / "persons" /
                       f"{PE_DIEMUT}.html").read_text(encoding="utf-8")
        # Berthold profile link must be present.
        assert f"{PE_BERTHOLD}.html" in diemut_html
        # Source table must contain source 10.
        assert ">10<" in diemut_html or "Nr. 10" in diemut_html or "10.html" in diemut_html
        # Relations block exists.
        assert "Verwandtschaft" in diemut_html

    def test_html_skips_relation_link_when_partner_missing(
        self, tmp_path, monkeypatch
    ):
        """If the relation partner has no own profile (e.g. only present in
        non-released sources), the name may be displayed but MUST NOT
        render as a dead link."""
        from frontend.tests.conftest import patch_build_path
        from frontend.build._helpers import _init_jinja
        from frontend.build._pages import _build_person_profiles

        patch_build_path(monkeypatch, "DOCS_DIR", tmp_path)
        env = _init_jinja()
        _build_person_profiles({PE_DIEMUT: [DOC_10]}, env)

        diemut_html = (tmp_path / "register" / "persons" /
                       f"{PE_DIEMUT}.html").read_text(encoding="utf-8")
        # Berthold profile must NOT be linked because not in linked_persons.
        assert f'href="{PE_BERTHOLD}.html"' not in diemut_html
        assert f'href="../../register/persons/{PE_BERTHOLD}.html"' not in diemut_html


class TestDedupAddname:
    """_dedup_addname ist die SSoT fuer die Dedup-Bedingung.

    Beide Konsumenten (_display_name und der Profile-Dict-Aufbau)
    rufen diese Helper-Funktion auf. Hier zentral getestet.
    """

    @pytest.mark.parametrize("surname,addname,expected", [
        # Identisch -> addname ausgenullt
        ("von Cremona", "von Cremona", ""),
        # Case-Unterschied -> ausgenullt
        ("der chramer", "der Chramer", ""),
        # Trailing-Whitespace -> ausgenullt
        ("von Schönberg", " von Schönberg ", ""),
        # Distinkt -> addname bleibt
        ("Gorser", "zu Schönberg", "zu Schönberg"),
        # Leerer surname -> addname bleibt (kann nicht doppeln)
        ("", "von X", "von X"),
        # Leerer addname -> bleibt leer
        ("Hacking", "", ""),
    ])
    def test_dedup_bedingung(self, surname, addname, expected):
        from frontend.aggregator.person_profiles import _dedup_addname
        assert _dedup_addname(surname, addname) == expected


class TestDisplayNameDedup:
    """End-to-End-Outcome: _display_name und profile.addName ziehen
    beide den Dedup ueber denselben Helper. Geht eine der beiden
    Stellen kaputt (oder vergisst den Helper-Aufruf), schlaegt der
    Integrations-Test an.

    Reale Faelle aus persons.csv: TEI-Annotation traegt bei
    Adelsfamilien den Toponym-Bestandteil identisch in <surname> und
    <addName>. Ohne Dedup erscheinen 'Albert von Cremona von Cremona'
    und 156 weitere.
    """

    def test_display_name_konsument(self):
        """_display_name nutzt den Helper und liefert den Namen ohne
        Doppel-Suffix."""
        from frontend.aggregator.person_profiles import _display_name
        assert _display_name({
            "forename": "Albert",
            "surname": "von Cremona",
            "addName": "von Cremona",
        }) == "Albert von Cremona"

    def test_profile_dict_konsument(self):
        """Profile-Output: profile.addName ist ausgenullt, profile.display
        zeigt 'Vorname Surname' ohne Doppel. Echter Integrations-Test
        gegen build_person_profiles mit dem realen pe__rapoto-Stamm
        (surname='von Schönberg', addname_reg='von Schönberg').
        """
        from frontend.aggregator import build_person_profiles
        rapoto_id = "pe__rapoto_von_schoenberg_QGW_II_I_1"
        rev = {rapoto_id: [DOC_10]}
        profiles = build_person_profiles(rev)
        assert rapoto_id in profiles, (
            "Stamm-Lookup fehlgeschlagen; persons.csv-Eintrag fehlt?"
        )
        rapoto = profiles[rapoto_id]
        assert rapoto["addName"] == "", (
            f"addName muss ausgenullt sein, ist: {rapoto['addName']!r}"
        )
        assert rapoto["display"] == "Rapoto von Schönberg", (
            f"display soll ohne Doppel sein, ist: {rapoto['display']!r}"
        )

    def test_distinct_addname_bleibt_im_profile(self):
        """Gegenprobe: wenn surname und addName verschieden sind,
        bleiben beide im Profile erhalten. Schutz gegen einen
        ueber-aggressiven Dedup."""
        from frontend.aggregator import build_person_profiles
        # pe__thomas_gorser_SB_CD_00787_a hat surname='Gorser',
        # addname_reg='zu Schönberg' -- distinkt, Dedup darf nicht
        # greifen.
        thomas_id = "pe__thomas_gorser_SB_CD_00787_a"
        rev = {thomas_id: [DOC_10]}
        profiles = build_person_profiles(rev)
        if thomas_id not in profiles:
            pytest.skip(f"{thomas_id} nicht im Stamm; CSV evtl. geaendert")
        thomas = profiles[thomas_id]
        assert thomas["addName"] == "zu Schönberg"
        assert "zu Schönberg" in thomas["display"]
