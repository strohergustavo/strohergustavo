"""Render a compact project card (GitHub "pinned" size) in the profile theme.

Usage:
  python3 scripts/project_card.py "Title" "Description line one" "Description line two" "Python" 100 > assets/project-name.svg
"""
import sys
from xml.sax.saxutils import escape

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"


def render(title, line1, line2, language, percent):
    w, h = 420, 132
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}: {escape(line1)} {escape(line2)} {escape(language)} {percent}%.">
<style>
  .sans {{ font-family: {SANS}; }}
  .in {{ opacity: 0; animation: fadeUp .7s cubic-bezier(.2,.7,.2,1) forwards; }}
  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(6px) }} to {{ opacity: 1; transform: none }} }}
</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="#010409" stroke="#262C36"/>
<g class="in">
  <text x="20" y="34" class="sans" font-size="15" font-weight="600" fill="#D9663E">{escape(title)}</text>
  <text x="{w - 20}" y="34" text-anchor="end" class="sans" font-size="15" fill="#8B949E">↗</text>
  <text x="20" y="62" class="sans" font-size="12.5" fill="#8B949E">{escape(line1)}</text>
  <text x="20" y="80" class="sans" font-size="12.5" fill="#8B949E">{escape(line2)}</text>
  <circle cx="26" cy="108" r="5" fill="#D9663E"/>
  <text x="37" y="112.5" class="sans" font-size="12.5"><tspan fill="#F0F6FC" font-weight="600">{escape(language)}</tspan><tspan fill="#8B949E"> {percent}%</tspan></text>
</g>
</svg>
"""


if __name__ == "__main__":
    title, line1, line2, language, percent = sys.argv[1:6]
    sys.stdout.write(render(title, line1, line2, language, percent))
