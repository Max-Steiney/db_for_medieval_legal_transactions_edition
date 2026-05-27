"""Guard: das Status-Dashboard meldet den realen Build-Stand.

status.py zeigte vor M5 auf das docs/ des Pipeline-Schwester-Repos statt
auf das Frontend-Repo, pruefte die alte Seite register/organisations.html
und erwartete Analyse- und Exploration-Seiten auch in der oeffentlichen
Sicht, wo sie gar nicht gebaut werden. Diese Tests halten die korrigierte
Pfad- und Sicht-Logik fest.
"""

import frontend.status as status
from frontend.config import FRONTEND_REPO_ROOT
from pipeline.config import REPO_ROOT as PIPELINE_REPO_ROOT


def test_docs_dir_rooted_in_frontend_repo():
    docs = status._docs_dir()
    assert docs.parent == FRONTEND_REPO_ROOT
    assert PIPELINE_REPO_ROOT not in docs.parents, (
        "Das Dashboard zeigt wieder auf das docs/ des Pipeline-Repos."
    )


def test_docs_dir_follows_audience(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "oeffentlich")
    assert status._docs_dir().name == "docs"
    monkeypatch.setenv("FRONTEND_AUDIENCE", "intern")
    assert status._docs_dir().name == "docs-intern"


def test_docs_dir_follows_stage(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "oeffentlich")
    monkeypatch.setenv("FRONTEND_STAGE", "2")
    assert status._docs_dir().name == "docs-with-mentioned"


def test_expected_pages_use_orgs_not_organisations(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "oeffentlich")
    pages = status._expected_pages()
    assert "register/orgs.html" in pages
    assert "register/organisations.html" not in pages


def test_public_view_excludes_experimental_pages(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "oeffentlich")
    pages = status._expected_pages()
    assert not any(p.startswith("analysis/") for p in pages), (
        "Analyse-Seiten werden oeffentlich nicht gebaut und duerfen nicht "
        "als erwartet gelten."
    )
    assert not any(p.startswith("exploration/") for p in pages)


def test_intern_view_includes_experimental_pages(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "intern")
    pages = status._expected_pages()
    assert "analysis/auswertungen.html" in pages
    assert "exploration/zeitstrom.html" in pages
    assert "exploration/personennetzwerk.html" in pages
