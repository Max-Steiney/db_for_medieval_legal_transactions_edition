"""Guard: keine CSS-Custom-Properties, die nirgends definiert sind.

7b hat sechs Fehlverweise auf nicht existente Tokens auf die kanonischen
Tokens in tokens.css gezogen (--color-surface -> --color-bg-card,
--color-text-primary -> --color-text, --text-md -> --text-base usw.). Ein
undefiniertes `var(--x)` ohne Fallback rendert mit dem Initialwert, also
faellt die beabsichtigte Gestaltung still aus. Dieser Test faengt sowohl die
Rueckkehr der alten Fehlverweise als auch jedes neue undefinierte Token.

Erlaubt bleibt eine kleine Allowlist: Tokens, die zur Laufzeit per JS gesetzt
werden (--bar-height, --tip-arrow-offset) oder ausschliesslich mit Fallback
genutzt werden (--heat-*, --rank-pct, --swatch-color, --color-on-accent).
"""

import re
from pathlib import Path

CSS_DIR = Path(__file__).resolve().parents[1] / "static" / "css"

# Tokens ohne Definition in tokens.css, die das absichtlich sind: per JS zur
# Laufzeit gesetzt oder nur mit Fallback genutzt. Siehe Modul-Docstring.
RUNTIME_OR_FALLBACK = {
    "--bar-height",         # index/viz-core/register: style.setProperty pro Balken
    "--tip-arrow-offset",   # tip.js: style.setProperty pro Tooltip
    "--heat-opacity",       # exploration: var(--heat-opacity, 0), pro Zelle
    "--heat-cursor",        # exploration: var(--heat-cursor, default), pro Zelle
    "--rank-pct",           # exploration: var(--rank-pct, 0%), pro Balken
    "--swatch-color",       # exploration: var(--swatch-color, var(--color-text-muted))
    "--color-on-accent",    # document: var(--color-on-accent, #fff)
}

_DEF = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
_USE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")


def _scan():
    defined, used = set(), set()
    for f in CSS_DIR.glob("*.css"):
        text = f.read_text(encoding="utf-8")
        defined.update(_DEF.findall(text))
        used.update(_USE.findall(text))
    return defined, used


def test_no_undefined_css_tokens():
    defined, used = _scan()
    undefined = used - defined - RUNTIME_OR_FALLBACK
    assert not undefined, (
        f"CSS nutzt nicht definierte Tokens ohne Fallback: {sorted(undefined)}. "
        f"In tokens.css definieren oder auf ein bestehendes Token ziehen."
    )
