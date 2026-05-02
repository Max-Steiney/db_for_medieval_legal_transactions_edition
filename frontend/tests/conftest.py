"""Shared test infrastructure for edition tests."""

from html.parser import HTMLParser

import pytest
from lxml import etree

import frontend.build

TEI = "http://www.tei-c.org/ns/1.0"
EMPTY_REGISTERS = ({}, {}, {})


def tei(xml_str):
    """Parse a TEI XML fragment."""
    wrapped = f'<body xmlns="{TEI}">{xml_str}</body>'
    return etree.fromstring(wrapped)


class TagFinder(HTMLParser):
    """Simple HTML parser to find elements by class or attribute."""

    def __init__(self):
        super().__init__()
        self.elements = []  # list of (tag, attrs_dict)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def find_by_class(self, css_class):
        """Return all elements containing the given CSS class."""
        return [
            (tag, attrs) for tag, attrs in self.elements
            if css_class in attrs.get("class", "").split()
        ]

    def find_by_attr(self, attr_name, attr_value=None):
        """Return elements with a specific attribute (optionally matching value)."""
        results = []
        for tag, attrs in self.elements:
            if attr_name in attrs:
                if attr_value is None or attrs[attr_name] == attr_value:
                    results.append((tag, attrs))
        return results


def parse_html(html_str):
    """Parse HTML and return a TagFinder for assertions."""
    finder = TagFinder()
    finder.feed(html_str)
    return finder


def patch_build_path(monkeypatch, name, value):
    """Patch a path constant across alle build-Submodule.

    Ersetzt das alte Idiom ``monkeypatch.setattr(frontend.build, "DATA_DIR", x)``,
    das nach dem Package-Split nicht mehr ausreicht: jedes Submodul (_helpers,
    _metadata, _pages, _quality) hat seine eigene Top-Level-Importbindung von
    DOCS_DIR/DATA_DIR. Wir setzen den Wert auf allen Stellen gleichzeitig.
    """
    import frontend.build as _b
    import frontend.build._helpers as _h
    import frontend.build._metadata as _m
    import frontend.build._pages as _p
    import frontend.build._quality as _q
    for mod in (_b, _h, _m, _p, _q):
        if hasattr(mod, name):
            monkeypatch.setattr(mod, name, value, raising=False)


@pytest.fixture(scope="module")
def docs_dir(tmp_path_factory):
    """Monkeypatch DOCS_DIR to a temp directory for the test module.

    Nach dem build-Package-Split (frontend.build/__init__.py + Submodule)
    haben die Submodule ihre eigenen DOCS_DIR-Bindings — der einfache
    Patch auf frontend.build.DOCS_DIR reicht nicht mehr. Wir patchen
    daher jedes Submodul, das DOCS_DIR liest oder darauf schreibt.
    """
    import frontend.build._helpers as _h
    import frontend.build._metadata as _m
    import frontend.build._pages as _p

    tmp_docs = tmp_path_factory.mktemp("docs")
    originals = {
        "build": frontend.build.DOCS_DIR,
        "helpers": _h.DOCS_DIR,
        "metadata": _m.DOCS_DIR,
        "pages": _p.DOCS_DIR,
    }
    frontend.build.DOCS_DIR = tmp_docs
    _h.DOCS_DIR = tmp_docs
    _m.DOCS_DIR = tmp_docs
    _p.DOCS_DIR = tmp_docs
    yield tmp_docs
    frontend.build.DOCS_DIR = originals["build"]
    _h.DOCS_DIR = originals["helpers"]
    _m.DOCS_DIR = originals["metadata"]
    _p.DOCS_DIR = originals["pages"]
