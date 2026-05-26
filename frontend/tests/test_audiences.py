"""Unit tests for the audience module.

Audience steuert orthogonal zur Stage, was die Templates an
Sektionen und IDs zeigen. Wenn das Modul wegfaellt, brechen
frontend.config (Import von active_audience) und base.html
(Globals audience_id) hart. Diese Tests sind die Sicherung
gegen einen erneuten verschwindenden Stand.
"""

import os

import pytest

from frontend import audiences


def test_default_audience_is_oeffentlich():
    assert audiences.DEFAULT_AUDIENCE_ID == "oeffentlich"


def test_active_audience_defaults_to_oeffentlich(monkeypatch):
    monkeypatch.delenv("FRONTEND_AUDIENCE", raising=False)
    assert audiences.active_audience_id() == "oeffentlich"
    a = audiences.active_audience()
    assert a["id"] == "oeffentlich"
    assert a["show_entity_ids"] is False


def test_active_audience_intern(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "intern")
    assert audiences.active_audience_id() == "intern"
    a = audiences.active_audience()
    assert a["show_entity_ids"] is True
    assert a["show_analysis_section"] is True


def test_invalid_audience_falls_back_to_oeffentlich(monkeypatch):
    monkeypatch.setenv("FRONTEND_AUDIENCE", "foobar")
    assert audiences.active_audience_id() == "oeffentlich"


def test_output_dir_suffix():
    assert audiences.output_dir_suffix("oeffentlich") == ""
    assert audiences.output_dir_suffix("intern") == "-intern"


def test_set_audience_env_rejects_unknown():
    with pytest.raises(ValueError):
        audiences.set_audience_env("nonsense")


def test_set_audience_env_writes_env(monkeypatch):
    monkeypatch.delenv("FRONTEND_AUDIENCE", raising=False)
    audiences.set_audience_env("intern")
    assert os.environ.get("FRONTEND_AUDIENCE") == "intern"
