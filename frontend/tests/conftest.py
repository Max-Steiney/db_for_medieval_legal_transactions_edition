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


@pytest.fixture(scope="module")
def docs_dir(tmp_path_factory):
    """Monkeypatch DOCS_DIR to a temp directory for the test module."""
    tmp_docs = tmp_path_factory.mktemp("docs")
    original = frontend.build.DOCS_DIR
    frontend.build.DOCS_DIR = tmp_docs
    yield tmp_docs
    frontend.build.DOCS_DIR = original
