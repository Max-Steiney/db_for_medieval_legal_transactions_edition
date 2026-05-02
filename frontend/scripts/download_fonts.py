"""Einmaliges Download-Skript fuer Self-Hosting der Schriften.

Holt woff2 + Subset-Range fuer Crimson Pro, Inter, JetBrains Mono ueber
die Google Fonts CSS2-API mit Chrome-User-Agent (sodass woff2 statt
woff/ttf zurueckkommt). Schreibt:

  frontend/static/fonts/<family>-<weight>[-italic].woff2  (latin + latin-ext)
  frontend/static/css/fonts.css                            (alle @font-face)

Die Skript ist nicht Teil des Builds — einmal manuell ausgefuehrt:
    python -m frontend.scripts.download_fonts

Subsets latin+latin-ext sind fuer eine deutschsprachige Edition mit
mhd. Quellen ausreichend; Cyrillic/Greek/Vietnamese werden bewusst
weggelassen (kleinere Bundle-Groesse).
"""

import re
import sys
import urllib.request
from pathlib import Path

CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Crimson+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700"
    ";1,300;1,400;1,500"
    "&family=Inter:wght@300;400;500;600"
    "&family=JetBrains+Mono:wght@400"
    "&display=swap"
)

# Chrome-UA -> Google liefert woff2 (mit anderen UAs koennen andere Formate kommen)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Subsets, die wir behalten. Alle anderen Bloecke werden uebersprungen.
KEEP_SUBSETS = {"latin", "latin-ext"}

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = ROOT / "frontend" / "static" / "fonts"
CSS_OUT = ROOT / "frontend" / "static" / "css" / "fonts.css"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def slug(family: str, weight: str, style: str) -> str:
    fam = family.lower().replace(" ", "-")
    italic = "-italic" if style == "italic" else ""
    return f"{fam}-{weight}{italic}"


def main() -> int:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    CSS_OUT.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {CSS_URL}")
    css = fetch(CSS_URL).decode("utf-8")

    # CSS-Bloecke trennen: "/* subset */ @font-face { ... }"
    # Pattern: comment with subset name, then a font-face block.
    pattern = re.compile(
        r"/\*\s*(?P<subset>[\w-]+)\s*\*/\s*"
        r"@font-face\s*\{(?P<body>[^}]+)\}",
        re.MULTILINE,
    )

    out_blocks: list[str] = []
    downloaded: dict[str, Path] = {}

    for m in pattern.finditer(css):
        subset = m.group("subset")
        if subset not in KEEP_SUBSETS:
            continue
        body = m.group("body")

        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        urange = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()

        local_name = f"{slug(family, weight, style)}-{subset}.woff2"
        local_path = FONTS_DIR / local_name

        if local_path not in downloaded.values():
            print(f"  -> {local_name}")
            data = fetch(url)
            local_path.write_bytes(data)
            downloaded[local_name] = local_path

        out_blocks.append(f"""/* {family} {weight} {style} ({subset}) */
@font-face {{
    font-family: '{family}';
    font-style: {style};
    font-weight: {weight};
    font-display: swap;
    src: url('../fonts/{local_name}') format('woff2');
    unicode-range: {urange};
}}""")

    if not out_blocks:
        print("Fehler: keine passenden Font-Faces in der CSS-Antwort gefunden.",
              file=sys.stderr)
        return 1

    header = (
        "/* === Self-hosted Schriften ===\n"
        " * Generiert von frontend/scripts/download_fonts.py\n"
        " * Quelle: Google Fonts CSS2-API. Lizenz: SIL OFL.\n"
        " * Subsets: latin, latin-ext.\n"
        " */\n\n"
    )
    CSS_OUT.write_text(header + "\n\n".join(out_blocks) + "\n",
                       encoding="utf-8")

    print(f"\n{len(downloaded)} woff2-Dateien nach {FONTS_DIR}")
    print(f"CSS geschrieben: {CSS_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
