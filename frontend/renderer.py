"""Recursive TEI element tree -> HTML string conversion.

Pure Python renderer. Templates only handle page layout;
this module handles the deep TEI nesting.
"""

from xml.sax.saxutils import escape

from pipeline.config import TEI_NS
from pipeline.utils.text_utils import strip_hash
from frontend.register import (
    build_tooltip_person,
    build_tooltip_org,
    build_tooltip_place,
)

TEI = f"{{{TEI_NS}}}"

# Entity type → (register tuple index, tooltip builder)
_ENTITY_MAP = {
    "person": (0, build_tooltip_person),
    "org":    (1, build_tooltip_org),
    "place":  (2, build_tooltip_place),
}

# rs/@type -> register detail directory (one HTML per entity inside).
# Names mirror the build output: docs/register/<dir>/<id>.html. Places
# have no register page; rs type="place" stays a span with the
# register-tooltip but no href.
_ENTITY_PAGE = {
    "person": "register/persons",
    "org": "register/orgs",
}

# rs/@type -> short label rendered as type vorspann in the hover-hint.
# Picked up by hint.js as data-hint-type attribute.
_HINT_TYPE = {
    "person": "Person",
    "org": "Organisation",
    "place": "Ort",
}


def render_document(body_element, registers, root_path="."):
    """Render a TEI <body> element to an HTML string.

    *registers* is a 3-tuple (persons, orgs, places).
    *root_path* is the relative path from the output file back to docs root
    (e.g. ``../../..``).  It is appended to the registers tuple so that
    entity handlers can build correct hrefs without changing every handler
    signature.
    """
    ctx = registers + (root_path,)
    return _render_children(body_element, ctx)


def _render_children(element, registers):
    """Render all children of an element, including text and tail."""
    parts = []
    if element.text:
        parts.append(escape(element.text))
    for child in element:
        parts.append(_render_element(child, registers))
        # Tail text (text after the closing tag, belonging to parent)
        if child.tail:
            parts.append(escape(child.tail))
    return "".join(parts)


def _render_element(element, registers):
    """Dispatch rendering based on element tag."""
    tag = element.tag

    # Skip comments and processing instructions (tag is not a string)
    if not isinstance(tag, str):
        return ""

    if tag.startswith(TEI):
        local = tag[len(TEI):]
    else:
        local = tag

    handler = ELEMENT_HANDLERS.get(local, _render_default)
    return handler(element, registers)


# --- Element handlers ---


_DIV_HEADINGS = {
    "abstract": "Regest",
    "seal": "Siegelbeschreibung",
    "nota": "Indorsat / Nota",
    "entry": "Eintrag",
}


def _render_div(element, registers):
    """Render <div type="...">.

    For each `div type` we inject a small micro-heading (see
    _DIV_HEADINGS) so that while scrolling it is visible where the
    regest ends and the seal description begins. Other div types stay
    without a heading; `header`/`lists` have special handling.
    """
    div_type = element.get("type", "")

    # Skip lists div (XInclude references)
    if div_type == "lists":
        return ""

    css_class = f"tei-{div_type}" if div_type else "tei-div"

    if div_type == "header":
        return f'<header class="{css_class}">{_render_children(element, registers)}</header>'

    heading_label = _DIV_HEADINGS.get(div_type)
    heading_html = (
        f'<h2 class="tei-section-head">{escape(heading_label)}</h2>'
        if heading_label else ""
    )
    return (
        f'<section class="{css_class}">'
        f'{heading_html}{_render_children(element, registers)}'
        f'</section>'
    )


def _render_p(element, registers):
    """Render <p>."""
    return f'<p>{_render_children(element, registers)}</p>'


def _render_rs(element, registers):
    """Render <rs type="..." ref="..." role="...">."""
    rs_type = element.get("type", "")
    ref = strip_hash(element.get("ref", ""))
    role = element.get("role", "")

    if rs_type == "event":
        return (
            f'<span class="anno-event" data-ref="{escape(ref)}">'
            f"{_render_children(element, registers)}</span>"
        )

    if rs_type == "fn":
        role_class = f"anno-fn-{role}" if role else "anno-fn"
        label = _fn_label(role)
        return (
            f'<span class="anno-fn {role_class}" data-role="{escape(role)}">'
            f'<span class="fn-label">{label}</span>'
            f"{_render_children(element, registers)}</span>"
        )

    if rs_type in _ENTITY_MAP:
        reg_index, tooltip_fn = _ENTITY_MAP[rs_type]
        register = registers[reg_index]
        tooltip = tooltip_fn(register[ref], ref) if ref in register else ref
        children = _render_children(element, registers)
        # Hover-hint type label, shown as small caps above the tooltip body.
        hint_type = _HINT_TYPE.get(rs_type, "")
        # Person and org annotations link to register/<dir>/<id>.html.
        # Place annotations stay as span when the place register has no
        # detail page for them.
        if ref and ref in register and rs_type in _ENTITY_PAGE:
            root_path = registers[3] if len(registers) > 3 else "."
            page = _ENTITY_PAGE[rs_type]
            href = f"{root_path}/{page}/{ref}.html"
            return (
                f'<a class="anno-{rs_type}" data-ref="{escape(ref)}" '
                f'data-hint="{escape(tooltip)}" data-hint-type="{hint_type}" '
                f'href="{escape(href)}">'
                f"{children}</a>"
            )
        return (
            f'<span class="anno-{rs_type}" data-ref="{escape(ref)}" '
            f'data-hint="{escape(tooltip)}" data-hint-type="{hint_type}">'
            f"{children}</span>"
        )

    # Unknown rs type -- render generically
    return f'<span class="anno-{escape(rs_type)}">{_render_children(element, registers)}</span>'


def _fn_label(role):
    """Human-readable label for function roles."""
    labels = {
        "issuer": "Aussteller*in",
        "recipient": "Empfänger*in",
        "witness": "Zeug*in",
        "other": "Sonstige",
    }
    return labels.get(role, role)


def _render_rolename(element, registers):
    """Render <roleName type="..." corresp="...">."""
    rn_type = element.get("type", "")
    corresp = strip_hash(element.get("corresp", ""))

    css = f"anno-attr anno-attr-{rn_type}" if rn_type else "anno-attr"
    attrs = f' data-corresp="{escape(corresp)}"' if corresp else ""
    # Native tooltip on the dagger glyph (CSS ::after) for type="dead",
    # so readers see "als verstorben genannt" without consulting the
    # annotation guidelines.
    if rn_type == "dead":
        attrs += ' title="Als verstorben genannt"'

    return f'<span class="{css}"{attrs}>{_render_children(element, registers)}</span>'


def _render_triggerstring(element, registers):
    """Render <triggerstring n="...">."""
    n = element.get("n", "")
    css = f"anno-trigger anno-trigger-{n}" if n else "anno-trigger"
    return f'<span class="{css}">{_render_children(element, registers)}</span>'


def _make_span_wrapper(css_class):
    """Factory for handlers that wrap children in a <span> with a CSS class."""
    def handler(element, registers):
        return f'<span class="{css_class}">{_render_children(element, registers)}</span>'
    return handler


def _render_lb(element, registers):
    """Render <lb/> (line break)."""
    return "<br/>"


def _render_pb(element, registers):
    """Render <pb/> (page break)."""
    n = element.get("n", "")
    if n:
        return f'<span class="tei-pb" data-n="{escape(n)}">[{escape(n)}]</span>'
    return '<span class="tei-pb">[//]</span>'


def _render_gap(element, registers):
    """Render <gap> (lacuna)."""
    return '<span class="tei-gap">[...]</span>'


def _render_default(element, registers):
    """Fallback: render children without wrapping element."""
    return _render_children(element, registers)


def _render_skip(element, registers):
    """Skip element and all its content."""
    return ""


# --- Handler dispatch table ---

# Tags that pass through without wrapping
_PASSTHROUGH_TAGS = [
    "persName", "forename", "surname", "addName", "orgName",
    "placeName", "reg", "body", "text", "hi", "ref", "date", "origDate",
]

ELEMENT_HANDLERS = {
    "div": _render_div,
    "p": _render_p,
    "rs": _render_rs,
    "roleName": _render_rolename,
    "triggerstring": _render_triggerstring,
    # Simple span wrappers
    "add": _make_span_wrapper("tei-add"),
    "unclear": _make_span_wrapper("tei-unclear"),
    "note": _make_span_wrapper("tei-note"),
    "bibl": _make_span_wrapper("tei-bibl"),
    "title": _make_span_wrapper("tei-title"),
    "sic": _make_span_wrapper("tei-sic"),
    # Self-closing / special
    "lb": _render_lb,
    "pb": _render_pb,
    "gap": _render_gap,
    # Skip elements
    "teiHeader": _render_skip,
    "facsimile": _render_skip,
    # Inline pass-through
    **{tag: _render_default for tag in _PASSTHROUGH_TAGS},
}
