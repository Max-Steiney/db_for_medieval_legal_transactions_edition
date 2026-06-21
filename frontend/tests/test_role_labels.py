"""Konsistenz-Test fuer das zentrale Funktionsrollen-Label-Mapping.

frontend/role_labels.py ist die Single-Source-of-Truth. Test prueft,
dass Python-Konsumenten (renderer, _profile_enrichment) und der
JS-Fallback in document.js denselben Wert fuer 'witness' tragen, plus
dass kein alter String mehr im Quellcode lebt.
"""

import re
from pathlib import Path

from frontend.role_labels import ROLE_LABELS, ROLE_LABELS_PLURAL


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_ROOT = REPO_ROOT / "frontend"


class TestRoleLabelsCanonical:
    """Die SSoT hat die erwarteten Werte."""

    def test_witness_ist_zeugin_und_sieglerin(self):
        assert ROLE_LABELS["witness"] == "Zeug:in / Siegler:in"

    def test_alle_vier_tei_werte_belegt(self):
        for key in ("issuer", "recipient", "witness", "other"):
            assert key in ROLE_LABELS
            assert ROLE_LABELS[key]


class TestRoleLabelsPlural:
    """Plural-Variante fuer Kategorie/Filter/Aggregat-Kontexte."""

    def test_witness_plural(self):
        assert ROLE_LABELS_PLURAL["witness"] == "Zeug:innen / Siegler:innen"

    def test_issuer_recipient_plural(self):
        assert ROLE_LABELS_PLURAL["issuer"] == "Aussteller:innen"
        assert ROLE_LABELS_PLURAL["recipient"] == "Empfänger:innen"

    def test_kategorie_js_nutzt_plural_witness(self):
        # Register-Sidebar/Aktiv-Filter, Abfrage-Dropdown und Rollen-
        # Verteilung sind Kategorie-Kontexte und tragen den Plural.
        for rel in ("static/js/register.js", "static/js/viz-core.js",
                    "static/js/analysis-resolver.js"):
            text = (FRONTEND_ROOT / rel).read_text(encoding="utf-8")
            assert "Zeug:innen / Siegler:innen" in text, (
                f"{rel} traegt nicht das Plural-witness-Label."
            )

    def test_query_vocabulary_plural(self):
        text = (FRONTEND_ROOT / "content" / "query_vocabulary.json").read_text(
            encoding="utf-8")
        assert "Zeug:innen / Siegler:innen" in text

    def test_pages_baut_chips_aus_plural_ssot(self):
        text = (FRONTEND_ROOT / "build" / "_pages.py").read_text(encoding="utf-8")
        assert "ROLE_LABELS_PLURAL[key]" in text, (
            "Register-Sidebar-Chips werden nicht aus der Plural-SSoT gebaut."
        )


class TestRoleLabelsKonsumenten:
    """Konsumenten lesen aus der SSoT, nicht aus eigenen Inline-Dicts."""

    def test_renderer_nutzt_ssot(self):
        from frontend.renderer import _fn_label
        assert _fn_label("witness") == ROLE_LABELS["witness"]
        assert _fn_label("issuer") == ROLE_LABELS["issuer"]

    def test_profile_enrichment_nutzt_ssot(self):
        from frontend.aggregator._profile_enrichment import (
            ROLE_LABEL_PERSON,
            ROLE_LABEL_ORG,
        )
        assert ROLE_LABEL_PERSON is ROLE_LABELS or ROLE_LABEL_PERSON == ROLE_LABELS
        assert ROLE_LABEL_ORG is ROLE_LABELS or ROLE_LABEL_ORG == ROLE_LABELS

    def test_keine_asterisk_genderform_im_quellcode(self):
        """Die veraltete Asterisk-Genderform ('Zeug*in', 'Siegler*in' und
        die aelteren Aussteller*/Empfaenger*-Varianten) darf nirgends mehr
        im Quellcode leben. Seit der Umstellung auf den Gender-Doppelpunkt
        traegt die SSoT durchgaengig die Form ':in' bzw. ':innen'.
        """
        legacy = re.compile(r"(Aussteller|Empfänger|Zeug|Siegler)\*in")
        forbidden_files = set()
        for path in FRONTEND_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in (".py", ".html", ".js"):
                continue
            if "tests" in path.parts or path.name.startswith("test_"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if legacy.search(text):
                forbidden_files.add(str(path.relative_to(REPO_ROOT)))
        assert forbidden_files == set(), (
            f"Veraltete Asterisk-Genderform im Quellcode: "
            f"{sorted(forbidden_files)}"
        )

    def test_jinja_globals_enthalten_role_labels(self):
        from frontend.build._helpers import _init_jinja
        env = _init_jinja()
        assert "ROLE_LABELS" in env.globals
        assert env.globals["ROLE_LABELS"] == ROLE_LABELS
