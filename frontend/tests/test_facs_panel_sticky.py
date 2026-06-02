"""B2: das Faksimile-Panel klebt beim Scrollen statt mit dem langen Regest
nach oben wegzulaufen. Source-Guard gegen die CSS-Regel."""

import re
from pathlib import Path

DOC_CSS = Path(__file__).resolve().parents[1] / "static" / "css" / "document.css"


def test_facs_panel_is_sticky():
    src = DOC_CSS.read_text(encoding="utf-8")
    block = re.search(r"\.doc-facs-panel\s*\{([^}]*)\}", src)
    assert block, ".doc-facs-panel-Regel fehlt."
    body = block.group(1)
    assert "position: sticky" in body, (
        "Das Faksimile-Panel ist nicht mehr sticky; bei langem Regest "
        "wandert das Bild wieder unter den Fold (B2)."
    )
    assert "height:" in body and "vh" in body, (
        "Dem Panel fehlt die bildschirmrelative Hoehe; es stretcht wieder "
        "auf die Regest-Hoehe."
    )
