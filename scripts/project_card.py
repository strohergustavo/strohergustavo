"""Render a compact project card (GitHub "pinned" size) in the profile theme.

Usage:
  python3 scripts/project_card.py "Title" "Description line one" "Description line two" "Python" 100 > assets/card-name.svg
"""
import sys
from xml.sax.saxutils import escape

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
ORANGE = "#D9663E"

# Arcade invader, two frames (11 x 8 pixels).
INVADER = (
    [
        "..X.....X..",
        "...X...X...",
        "..XXXXXXX..",
        ".XX.XXX.XX.",
        "XXXXXXXXXXX",
        "X.XXXXXXX.X",
        "X.X.....X.X",
        "...XX.XX...",
    ],
    [
        "..X.....X..",
        "X..X...X..X",
        "X.XXXXXXX.X",
        "XXX.XXX.XXX",
        "XXXXXXXXXXX",
        ".XXXXXXXXX.",
        "..X.....X..",
        ".X.......X.",
    ],
)


def pixels(rows, size):
    return "".join(
        f'<rect x="{x * size}" y="{y * size}" width="{size}" height="{size}"/>'
        for y, row in enumerate(rows)
        for x, c in enumerate(row)
        if c == "X"
    )


def render(title, line1, line2, language, percent):
    w, h = 420, 132
    px = 2
    inv_x, inv_y = w - 20 - 11 * px, 22
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}: {escape(line1)} {escape(line2)} {escape(language)} {percent}%.">
<style>
  .sans {{ font-family: {SANS}; }}
  .in {{ opacity: 0; animation: fadeUp .7s cubic-bezier(.2,.7,.2,1) forwards; }}
  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(6px) }} to {{ opacity: 1; transform: none }} }}
  .walk {{ animation: walk 2.4s steps(1) infinite; }}
  @keyframes walk {{ 0% {{ transform: translateX(0) }} 25% {{ transform: translateX(-2px) }} 50% {{ transform: translateX(0) }} 75% {{ transform: translateX(2px) }} }}
  .fa {{ animation: fa 1.2s steps(1) infinite; }}
  .fb {{ animation: fb 1.2s steps(1) infinite; }}
  @keyframes fa {{ 0% {{ opacity: 1 }} 50% {{ opacity: 0 }} }}
  @keyframes fb {{ 0% {{ opacity: 0 }} 50% {{ opacity: 1 }} }}
</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="#010409" stroke="#262C36"/>
<g class="in">
  <text x="20" y="34" class="sans" font-size="15" font-weight="600" fill="{ORANGE}">{escape(title)}</text>
  <g transform="translate({inv_x} {inv_y})"><g class="walk" fill="{ORANGE}" shape-rendering="crispEdges">
    <g class="fa">{pixels(INVADER[0], px)}</g>
    <g class="fb">{pixels(INVADER[1], px)}</g>
  </g></g>
  <text x="20" y="62" class="sans" font-size="12.5" fill="#8B949E">{escape(line1)}</text>
  <text x="20" y="80" class="sans" font-size="12.5" fill="#8B949E">{escape(line2)}</text>
  <circle cx="26" cy="108" r="5" fill="{ORANGE}"/>
  <text x="37" y="112.5" class="sans" font-size="12.5"><tspan fill="#F0F6FC" font-weight="600">{escape(language)}</tspan><tspan fill="#8B949E"> {percent}%</tspan></text>
</g>
</svg>
"""


if __name__ == "__main__":
    title, line1, line2, language, percent = sys.argv[1:6]
    sys.stdout.write(render(title, line1, line2, language, percent))
