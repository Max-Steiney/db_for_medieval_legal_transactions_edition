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

# triggerstring/@n -> (type label, body) for the hover-hint. Mirrors the
# unified hint.js contract used by entity references, so Dispositivformeln
# and Funktionsrollen-Trigger pop out the same way in the body text.
_TRIGGER_HINT = {
    "disp": ("Dispositivformel", "Verb, das das Rechtsgeschäft anzeigt"),
    "fn":   ("Funktionsrollen-Trigger", "Verb, das eine Funktionsrolle markiert"),
}

# roleName/@type -> (type label, body) for the hover-hint. Without these,
# the user has no way to tell whether italic text like "statrichter" is a
# Beruf, ein Titel oder ein Verwandtschaftsbezug. Werte stammen aus den
# Edition-Guidelines, Abschnitt 2 Ebene 4.
_ROLENAME_HINT = {
    "kin":    ("Verwandtschaft",   "Verwandtschaftsbeziehung"),
    "title":  ("Titel",            "Titel oder Anrede"),
    "prof":   ("Beruf",            "Berufsbezeichnung"),
    "occ":    ("Amt",              "Amts- oder Berufsbezeichnung mit Organisations- oder Ortsbezug"),
    "dead":   ("Verstorben",       "In der Quelle als verstorben genannt"),
    "rep":    ("Stellvertretung",  "Vertretung einer anderen Person"),
    "friend": ("Freundschaft",     "Freundschafts- oder Bündnisbeziehung"),
    "topo":   ("Topographie",      "Topographische Lagebezeichnung"),
    "owner":  ("Besitz",           "Besitzverhältnis zu einer Person, Organisation oder einem Ort"),
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
    prev_child = None
    for child in element:
        # Defensive whitespace patch (TEI corpus): roleName/add tags are
        # frequently siblings without intervening whitespace. Without the
        # patch the rendered HTML reads "fraterepiscopus" or
        # "episcopusAdam". Two cases handled here:
        #   1) sibling element after roleName/add (text node missing
        #      between previous-element's closing and this element)
        #   2) tail text after roleName/add starting with a letter/digit
        # Punctuation and pre-existing whitespace are explicit opt-outs.
        if prev_child is not None and _needs_space_between_siblings(prev_child, child):
            parts.append(" ")
        parts.append(_render_element(child, registers))
        tail = child.tail or ""
        if tail and _needs_space_before_tail(child, tail):
            parts.append(" ")
        if tail:
            parts.append(escape(tail))
        prev_child = child
    return "".join(parts)


def _is_attribute_tag(child):
    """Tag-Filter fuer das Whitespace-Patch: roleName und add sind die
    Annotationen, die im UI als kompakte Pillen rendern und im Plain-Text
    direkt an Folge-Token kleben, wenn der TEI-Quelltext kein Whitespace
    setzt."""
    tag = child.tag
    if not isinstance(tag, str):
        return False
    local = tag[len(TEI):] if tag.startswith(TEI) else tag
    return local in ("roleName", "add")


def _needs_space_before_tail(child, tail):
    """True iff a single space should be injected between a roleName/add
    element and its tail text. Punctuation, brackets, dashes and any
    leading whitespace are explicit opt-outs."""
    if not _is_attribute_tag(child):
        return False
    first = tail[:1]
    if first.isspace():
        return False
    if first in (",", ".", ";", ":", "!", "?", ")", "]", "}", "/", "-",
                 "–", "—", "…"):
        return False
    return True


def _needs_space_between_siblings(prev_child, current_child):
    """True iff a single space should be injected between two adjacent
    child elements. Fires when the previous child is a roleName/add AND
    no tail text separated them AND no whitespace was already injected
    on the current child's leading text."""
    if not _is_attribute_tag(prev_child):
        return False
    if prev_child.tail:
        # If there is any tail text, _needs_space_before_tail already
        # decides whether a space is necessary; we must not double-space.
        return False
    # Current child has its own text? Only inject if it doesn't start
    # with whitespace/punctuation.
    leading = current_child.text or ""
    if leading:
        first = leading[:1]
        if first.isspace():
            return False
        if first in (",", ".", ";", ":", "!", "?", ")", "]", "}", "/", "-",
                     "–", "—", "…"):
            return False
    return True


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
        # Geschlecht (nur Person) als data-sex auf den Anker setzen,
        # damit die Annotations-Tabelle es ohne zusaetzlichen JSON-Fetch
        # in einer Spalte zeigen kann. Leere Strings werden nicht
        # emittiert -- "unbekannt" laesst die Tabelle als Dash rendern.
        sex_attr = ""
        if rs_type == "person" and ref in register:
            sex_val = (register[ref] or {}).get("sex", "")
            if sex_val:
                sex_attr = f' data-sex="{escape(sex_val)}"'

        # Place annotations stay as span when the place register has no
        # detail page for them.
        if ref and ref in register and rs_type in _ENTITY_PAGE:
            root_path = registers[3] if len(registers) > 3 else "."
            page = _ENTITY_PAGE[rs_type]
            href = f"{root_path}/{page}/{ref}.html"
            return (
                f'<a class="anno-{rs_type}" data-ref="{escape(ref)}"{sex_attr} '
                f'data-hint="{escape(tooltip)}" data-hint-type="{hint_type}" '
                f'href="{escape(href)}">'
                f"{children}</a>"
            )
        return (
            f'<span class="anno-{rs_type}" data-ref="{escape(ref)}"{sex_attr} '
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

    hint = _ROLENAME_HINT.get(rn_type)
    if hint:
        type_label, body = hint
        attrs += f' data-hint="{escape(body)}" data-hint-type="{escape(type_label)}"'

    return f'<span class="{css}"{attrs}>{_render_children(element, registers)}</span>'


def _render_triggerstring(element, registers):
    """Render <triggerstring n="...">."""
    n = element.get("n", "")
    css = f"anno-trigger anno-trigger-{n}" if n else "anno-trigger"
    hint = _TRIGGER_HINT.get(n)
    if hint:
        type_label, body = hint
        return (
            f'<span class="{css}" '
            f'data-hint="{escape(body)}" data-hint-type="{escape(type_label)}">'
            f'{_render_children(element, registers)}</span>'
        )
    return f'<span class="{css}">{_render_children(element, registers)}</span>'


def _make_span_wrapper(css_class):
    """Factory for handlers that wrap children in a <span> with a CSS class."""
    def handler(element, registers):
        return f'<span class="{css_class}">{_render_children(element, registers)}</span>'
    return handler


def _render_add(element, registers):
    """Render <add>: editorial addition, marked in the body via square
    brackets (CSS ::before/::after). Hover-hint erklaert die eckigen
    Klammern, damit die Lesehilfe ohne Konsultation der Richtlinien
    auskommt."""
    return (
        f'<span class="tei-add" '
        f'data-hint="Vom Editor sinngemäß ergänzt" '
        f'data-hint-type="Editorische Ergänzung">'
        f'{_render_children(element, registers)}</span>'
    )


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
    "add": _render_add,
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
