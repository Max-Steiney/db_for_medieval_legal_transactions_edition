"""Logik-Tests fuer die sicht-abhaengige Korpus-Auswahl.

visible_corpora() ist die zentrale Stelle, an der die Sicht (public vs.
private) entscheidet, welche Quellen-Sammlungen ein Build beruecksichtigt.
Bricht sie, erscheinen entweder ungepruefte Sammlungen oeffentlich oder
die interne Sicht verliert Sammlungen. Diese Tests laufen ohne Bau.
Stakeholder decision: Protokoll 18.05.2026 ("QGW bis 1414, StB Bd. 1").
"""

from frontend import config


PUBLIC = ("QGW/Vienna_1177-1414_ready", "Stadtbuecher/Band_1_1395-1400_ready")
HIDDEN = ("QGW/Vienna_1415-1417", "QGW/Vienna_1448-57_ready",
          "Satzbuch_CD/SB_CD_1448-60_ready")


def test_public_audience_only_public_corpora(monkeypatch):
    monkeypatch.delenv("FRONTEND_CORPORA", raising=False)
    monkeypatch.setenv("FRONTEND_AUDIENCE", "public")
    assert set(config.visible_corpora()) == set(PUBLIC)
    for c in PUBLIC:
        assert config.is_visible_corpus(c)
    for c in HIDDEN:
        assert not config.is_visible_corpus(c), (
            f"{c} ist oeffentlich sichtbar, darf es aber nicht sein."
        )


def test_private_audience_includes_hidden_corpora(monkeypatch):
    monkeypatch.delenv("FRONTEND_CORPORA", raising=False)
    monkeypatch.delenv("FRONTEND_STAGE", raising=False)
    monkeypatch.setenv("FRONTEND_AUDIENCE", "private")
    vis = set(config.visible_corpora())
    assert set(PUBLIC) <= vis
    for c in HIDDEN:
        assert c in vis, f"{c} fehlt in der internen Sicht."


def test_public_corpora_is_strict_subset_of_released():
    assert set(config.PUBLIC_CORPORA) == set(PUBLIC)
    assert set(config.PUBLIC_CORPORA) < set(config.RELEASED_CORPORA)


def test_corpora_override_takes_precedence(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "public")
    monkeypatch.setenv("FRONTEND_CORPORA", "QGW/Vienna_1448-57_ready")
    assert config.visible_corpora() == ("QGW/Vienna_1448-57_ready",)
    assert config.is_visible_corpus("QGW/Vienna_1448-57_ready")
    assert not config.is_visible_corpus("QGW/Vienna_1177-1414_ready")
