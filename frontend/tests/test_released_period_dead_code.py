"""Korpus-Folgepunkt 2: data-released-min/max und window.RELEASED_PERIOD
sind toter Code (Setter ohne Konsumenten). Regressions-Test sichert ab,
dass weder das DOM-Attribut noch der JS-Init wiederkommen, ohne dass ein
echter Konsument dazukommt. Wenn ein Konsument entsteht, diesen Test
zusammen mit der Wiederherstellung anpassen.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_base_template_has_no_data_released_attributes():
    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    assert "data-released-min" not in base
    assert "data-released-max" not in base


def test_core_js_has_no_released_period_init():
    core = (ROOT / "static" / "js" / "core.js").read_text(encoding="utf-8")
    assert "RELEASED_PERIOD" not in core
    assert "releasedMin" not in core
    assert "releasedMax" not in core
