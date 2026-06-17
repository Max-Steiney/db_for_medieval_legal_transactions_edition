"""Unit tests for the TEI-to-HTML renderer."""

import pytest

from frontend.renderer import render_document, _render_children
from frontend.tests.conftest import tei, parse_html, EMPTY_REGISTERS, TEI


# --- Structural tests ---


def test_plain_paragraph():
    body = tei('<p>Ein einfacher Text.</p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "<p>Ein einfacher Text.</p>" in html


def test_div_abstract():
    body = tei('<div type="abstract"><p>Regest</p></div>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    sections = finder.find_by_class("tei-abstract")
    assert len(sections) == 1
    assert sections[0][0] == "section"
    assert "<p>Regest</p>" in html


def test_div_entry():
    body = tei('<div type="entry"><p>Eintrag</p></div>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-entry")


def test_div_header():
    body = tei('<div type="header"><p>Titel</p></div>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    headers = finder.find_by_class("tei-header")
    assert len(headers) == 1
    assert headers[0][0] == "header"


def test_div_seal():
    body = tei('<div type="seal"><p>Siegel</p></div>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-seal")


def test_div_lists_skipped():
    body = tei('<div type="lists"><p>Should not appear</p></div>')
    html = render_document(body, EMPTY_REGISTERS)
    assert html == ""


# --- Entity annotation tests ---


def test_rs_person_with_register():
    persons = {"pe__hans_test": {
        "forename": "Hans", "surname": "Test", "addName": "",
        "death": "1350", "display": "Hans Test", "sex": "m",
    }}
    body = tei('<p><rs type="person" ref="pe__hans_test">Hans</rs></p>')
    html = render_document(body, (persons, {}, {}))
    finder = parse_html(html)
    spans = finder.find_by_class("anno-person")
    assert len(spans) == 1
    assert spans[0][1]["data-ref"] == "pe__hans_test"
    assert "Hans Test" in html
    # Sterbedatum erscheint seit Meeting 2026-06-17 nicht mehr im Annotations-
    # Hint (notAfter-Terminus, war als exaktes Datum missverstaendlich).
    assert "1350" not in html


def test_rs_person_orphaned_ref():
    body = tei('<p><rs type="person" ref="pe__unknown">Jemand</rs></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    spans = finder.find_by_attr("data-hint", "pe__unknown")
    assert len(spans) == 1


def test_rs_org():
    orgs = {"org__kloster": {"name": "Stift Klosterneuburg", "type": "Kloster"}}
    body = tei('<p><rs type="org" ref="org__kloster">das Stift</rs></p>')
    html = render_document(body, ({}, orgs, {}))
    finder = parse_html(html)
    assert finder.find_by_class("anno-org")
    assert "Stift Klosterneuburg" in html


def test_rs_place():
    places = {"pl__wien": {"name": "Wien", "type": "settlement", "lat": "48.2", "lng": "16.37"}}
    body = tei('<p><rs type="place" ref="pl__wien">Wien</rs></p>')
    html = render_document(body, ({}, {}, places))
    finder = parse_html(html)
    assert finder.find_by_class("anno-place")


def test_rs_event():
    body = tei('<p><rs type="event" ref="ev__100">Text</rs></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    spans = finder.find_by_class("anno-event")
    assert len(spans) == 1
    assert spans[0][1]["data-ref"] == "ev__100"


# --- Function role tests (parametrized) ---


@pytest.mark.parametrize("role,expected_class", [
    ("issuer", "anno-fn-issuer"),
    ("recipient", "anno-fn-recipient"),
    ("witness", "anno-fn-witness"),
    ("other", "anno-fn-other"),
])
def test_rs_fn_role(role, expected_class):
    body = tei(f'<p><rs type="fn" role="{role}">text</rs></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class(expected_class), f"Missing {expected_class}"


# --- roleName type tests (parametrized) ---


@pytest.mark.parametrize("rn_type", [
    "kin", "title", "occ", "prof", "dead", "rep", "friend", "topo", "owner",
])
def test_rolename_type(rn_type):
    corresp = ' corresp="pe__x"' if rn_type == "kin" else ""
    body = tei(f'<p><roleName type="{rn_type}"{corresp}>text</roleName></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    expected_class = f"anno-attr-{rn_type}"
    assert finder.find_by_class(expected_class), f"Missing {expected_class}"


def test_rolename_kin_corresp():
    """kin roleName preserves data-corresp attribute."""
    body = tei('<p><roleName type="kin" corresp="pe__x">hausvrowe</roleName></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    spans = finder.find_by_attr("data-corresp", "pe__x")
    assert len(spans) == 1


# --- Whitespace patch between roleName/add and following text ---


def test_rolename_glued_forename_gets_space():
    """Nr. 24 pattern: <roleName>...</roleName>Forename without TEI-side
    space. Renderer injects a single space so 'episcopusAdam' becomes
    'episcopus Adam'."""
    body = tei(
        '<p><rs type="person" ref="pe__x">'
        '<roleName type="occ"><add>episcopus</add></roleName>'
        'Adam Marturanensis</rs></p>'
    )
    html = render_document(body, EMPTY_REGISTERS)
    assert "</span> Adam" in html
    assert "episcopusAdam" not in html


def test_rolename_followed_by_comma_no_extra_space():
    """Punctuation legitimately follows without whitespace -- patch must
    not insert a space before commas/semicolons/dots."""
    body = tei(
        '<p><rs type="person" ref="pe__x">'
        '<roleName type="title">frater</roleName>, X</rs></p>'
    )
    html = render_document(body, EMPTY_REGISTERS)
    assert "</span>, X" in html
    assert "</span> , X" not in html


def test_rolename_preexisting_space_not_doubled():
    """Tail already starts with whitespace -- patch is a no-op."""
    body = tei(
        '<p><rs type="person" ref="pe__x">'
        '<roleName type="occ">archiepiscopus</roleName> Philippus</rs></p>'
    )
    html = render_document(body, EMPTY_REGISTERS)
    assert "</span> Philippus" in html
    assert "</span>  Philippus" not in html


def test_add_glued_to_following_text():
    """add tag with glued tail also gets the space-injection treatment."""
    body = tei('<p><rs type="person" ref="pe__x">Hans <add>der</add>Schneider</rs></p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "</span> Schneider" in html


def test_two_adjacent_rolenames_get_space():
    """Nr. 24 pattern: <roleName>frater</roleName><roleName><add>archiepiscopus
    </add></roleName> -- two sibling roleNames without tail text. Patch
    must inject space between them so the plain-text reads 'frater
    archiepiscopus' not 'fraterarchiepiscopus'."""
    body = tei(
        '<p><rs type="person" ref="pe__x">'
        '<roleName type="title">frater</roleName>'
        '<roleName type="occ"><add>archiepiscopus</add></roleName>'
        ' Johannes Turritanus</rs></p>'
    )
    html = render_document(body, EMPTY_REGISTERS)
    # Plain text content of the rendered anchor should contain
    # "frater archiepiscopus", not "fraterarchiepiscopus".
    import re
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    assert "frater archiepiscopus" in text
    assert "fraterarchiepiscopus" not in text


def test_sibling_with_comma_text_no_space():
    """Punctuation as leading text of the next sibling -- patch is a no-op."""
    body = tei(
        '<p><rs type="person" ref="pe__x">'
        '<roleName>frater</roleName>'
        '<add>, X</add></rs></p>'
    )
    html = render_document(body, EMPTY_REGISTERS)
    assert "</span><span" in html
    # No injected space before the comma-leading sibling
    assert "</span> <span class=\"tei-add\">, X" not in html


# --- Triggerstring tests ---


def test_triggerstring_disp():
    body = tei('<p><triggerstring n="disp">verkaufen</triggerstring></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("anno-trigger-disp")
    assert "verkaufen" in html


def test_triggerstring_fn():
    body = tei('<p><triggerstring n="fn">mit Handen</triggerstring></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("anno-trigger-fn")


# --- Inline element tests ---


def test_add():
    body = tei('<p><add>Grundherren</add></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-add")
    assert "Grundherren" in html


def test_unclear():
    body = tei('<p><unclear>unleserlich</unclear></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-unclear")


# --- Deep nesting test ---


def test_nested_annotation():
    """Test deeply nested annotation (event > fn > person > roleName)."""
    xml = (
        '<p><rs type="event" ref="ev__1">'
        '<rs type="fn" role="issuer">'
        '<rs type="person" ref="pe__x">Hans der '
        '<roleName type="prof">Schneider</roleName>'
        '</rs></rs></rs></p>'
    )
    body = tei(xml)
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)

    assert finder.find_by_class("anno-event")
    assert finder.find_by_class("anno-fn-issuer")
    assert finder.find_by_class("anno-person")
    assert finder.find_by_class("anno-attr-prof")
    assert "Schneider" in html

    # Verify data-ref attributes
    event_spans = finder.find_by_attr("data-ref", "ev__1")
    assert len(event_spans) >= 1
    person_spans = finder.find_by_attr("data-ref", "pe__x")
    assert len(person_spans) >= 1


# --- Additional element handler tests ---


def test_render_note():
    body = tei('<p><note>Anmerkung</note></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-note")
    assert "Anmerkung" in html


def test_render_lb():
    body = tei('<p>Text<lb/>Text</p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "<br/>" in html


def test_render_pb_with_n():
    body = tei('<p><pb n="3"/></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-pb")
    assert "[3]" in html


def test_render_pb_without_n():
    body = tei('<p><pb/></p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "[//]" in html


def test_render_gap():
    body = tei('<p><gap/></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-gap")
    assert "[...]" in html


def test_render_sic():
    body = tei('<p><sic>error</sic></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-sic")
    assert "error" in html


def test_render_bibl():
    body = tei('<p><bibl>Ref</bibl></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-bibl")
    assert "Ref" in html


def test_render_title():
    body = tei('<p><title>Book</title></p>')
    html = render_document(body, EMPTY_REGISTERS)
    finder = parse_html(html)
    assert finder.find_by_class("tei-title")
    assert "Book" in html


def test_render_skip_header():
    body = tei('<teiHeader><fileDesc><titleStmt><title>T</title></titleStmt></fileDesc></teiHeader><p>visible</p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "visible" in html
    assert "fileDesc" not in html


def test_render_default():
    body = tei('<p><persName>Hans</persName></p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "Hans" in html


def test_tail_text_preserved():
    body = tei('<p><rs type="person" ref="pe__x">Hans</rs> der Alte</p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "der Alte" in html


def test_html_escaping():
    body = tei('<p>A &amp; B &lt; C</p>')
    html = render_document(body, EMPTY_REGISTERS)
    assert "&amp;" in html


# --- Entity link tests ---


def test_rs_person_renders_as_link():
    """Known person ref renders as <a> tag, not <span>."""
    persons = {"pe__hans": {
        "forename": "Hans", "surname": "", "addName": "",
        "death": "", "display": "Hans", "sex": "m",
    }}
    body = tei('<p><rs type="person" ref="pe__hans">Hans</rs></p>')
    html = render_document(body, (persons, {}, {}), root_path="../..")
    assert "<a " in html
    assert 'class="anno-person"' in html


def test_rs_person_link_href():
    """Person link points to the per-entity profile page."""
    persons = {"pe__hans": {
        "forename": "Hans", "surname": "", "addName": "",
        "death": "", "display": "Hans", "sex": "m",
    }}
    body = tei('<p><rs type="person" ref="pe__hans">Hans</rs></p>')
    html = render_document(body, (persons, {}, {}), root_path="../..")
    assert 'href="../../register/persons/pe__hans.html"' in html


def test_rs_org_renders_as_link():
    """Known org ref renders as <a> pointing to the org detail page."""
    orgs = {"org__kloster": {"name": "Stift", "type": "Kloster"}}
    body = tei('<p><rs type="org" ref="org__kloster">das Stift</rs></p>')
    html = render_document(body, ({}, orgs, {}), root_path=".")
    assert "<a " in html
    assert 'href="./register/orgs/org__kloster.html"' in html


def test_rs_place_renders_as_span():
    """Known place ref renders as <span> (no register/detail page for
    places; annotation kept but not linked)."""
    places = {"pl__wien": {"name": "Wien", "type": "settlement", "lat": "", "lng": ""}}
    body = tei('<p><rs type="place" ref="pl__wien">Wien</rs></p>')
    html = render_document(body, ({}, {}, places), root_path=".")
    assert "<span " in html
    assert "<a " not in html
    assert 'register/places' not in html
    assert 'data-ref="pl__wien"' in html


def test_orphaned_ref_renders_as_span():
    """Orphaned ref (not in register) stays as <span>, not <a>."""
    body = tei('<p><rs type="person" ref="pe__unknown">Jemand</rs></p>')
    html = render_document(body, EMPTY_REGISTERS, root_path="../..")
    assert "<span " in html
    assert "<a " not in html
