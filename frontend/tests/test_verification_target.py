"""Guard: das Verifikations-Set vergleicht gegen den richtigen Build.

Das Test-Set liest TEI im released-Scope. Diesen Umfang rendert nur die
interne Fassung (docs-intern/); der oeffentliche Build (docs/) ist seit
der Korpus-Trennung schmaler und wuerde Scope-Mismatches melden, die
keine Drift sind. Default-Ziel ist deshalb docs-intern, per
VERIFICATION_DOCS_DIR ueberschreibbar. Diese Tests halten beides fest.
"""

import importlib

import verification.config as vcfg


def test_default_target_is_docs_intern(monkeypatch):
    monkeypatch.delenv("VERIFICATION_DOCS_DIR", raising=False)
    try:
        m = importlib.reload(vcfg)
        assert m.DOCS_DIR.name == "docs-intern"
        assert m.DATA_DIR == m.DOCS_DIR / "data"
        assert m.HTML_DOCUMENTS == m.DOCS_DIR / "documents"
        assert m.HTML_REGISTER_PERSONS == m.DOCS_DIR / "register" / "persons"
    finally:
        importlib.reload(vcfg)


def test_override_env_honoured(monkeypatch):
    monkeypatch.setenv("VERIFICATION_DOCS_DIR", "docs")
    try:
        m = importlib.reload(vcfg)
        assert m.DOCS_DIR.name == "docs"
        assert m.DATA_DIR == m.DOCS_DIR / "data"
    finally:
        monkeypatch.delenv("VERIFICATION_DOCS_DIR", raising=False)
        importlib.reload(vcfg)
