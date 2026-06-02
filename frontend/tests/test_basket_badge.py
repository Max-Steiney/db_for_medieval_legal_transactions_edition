"""E1: der Nav-Badge zeigt die Korb-Eintraege pro Entitaetstyp getrennt
(je eine farbige Pille), nicht mehr eine addierte Gesamtzahl. Source-Guards."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
BASKET_JS = _ROOT / "static" / "js" / "basket.js"
BASE_HTML = _ROOT / "templates" / "base.html"
COMPONENTS_CSS = _ROOT / "static" / "css" / "components.css"


def test_badge_renders_per_type_pills():
    src = BASKET_JS.read_text(encoding="utf-8")
    assert "nav-basket-pill--" in src, (
        "updateBadge rendert keine Typ-Pillen mehr (E1)."
    )
    assert "['source', 'person', 'org']" in src, (
        "Die Pillen werden nicht pro Entitaetstyp gezaehlt (E1)."
    )


def test_badge_not_single_total():
    src = BASKET_JS.read_text(encoding="utf-8")
    assert "badge.textContent = c > 0" not in src, (
        "Der Badge faellt wieder auf eine addierte Gesamtzahl zurueck (E1)."
    )


def test_badge_markup_is_pill_container():
    html = BASE_HTML.read_text(encoding="utf-8")
    assert 'class="nav-basket-counts"' in html, (
        "Der Pillen-Container fehlt im Nav-Markup (E1)."
    )


def test_tooltip_names_gathered_and_derived_per_type():
    # Tooltip muss pro Typ benennen, was gesammelt und was abgeleitet ist,
    # damit die Badge-Totals (1/45/8) lesbar werden. Nicht nur eine Summe
    # "Davon N abgeleitet".
    src = BASKET_JS.read_text(encoding="utf-8")
    assert "countGathered(d[0])" in src and "countDerived(d[0])" in src, (
        "breakdownText schluesselt gesammelt/abgeleitet nicht pro Typ auf (E1)."
    )
    assert "gesammelt" in src and "abgeleitet" in src, (
        "Tooltip benennt gesammelt/abgeleitet nicht (E1)."
    )


def test_pill_colors_per_type():
    css = COMPONENTS_CSS.read_text(encoding="utf-8")
    for cls, token in (
        ("--source", "--anno-place"),
        ("--person", "--anno-person"),
        ("--org", "--anno-org"),
    ):
        assert ".nav-basket-pill" + cls in css, f"Pillen-Klasse {cls} fehlt."
        assert token in css, f"Farbtoken {token} fehlt fuer die Pillen."
