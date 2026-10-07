"""Render the GitHub contribution calendar as a themed SVG (black / orange / gray)."""
import datetime
import json
import os
import sys
import urllib.request

USER = os.environ.get("GH_USER", "strohergustavo")
QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""

LEVELS = {
    "NONE": "#151B23",
    "FIRST_QUARTILE": "#4A2A1F",
    "SECOND_QUARTILE": "#7D4330",
    "THIRD_QUARTILE": "#B25E42",
    "FOURTH_QUARTILE": "#D97757",
}
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal):
    cell, gap = 16, 4
    step = cell + gap
    left, top = 92, 108
    weeks = cal["weeks"]
    width = 1200
    height = top + 7 * step + 64

    out = []
    last_month = None
    for w, week in enumerate(weeks):
        x = left + w * step
        first = datetime.date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and first.day <= 7:
            if w < len(weeks) - 2:
                out.append(f'<text x="{x}" y="{top - 12}" class="mono" font-size="13" fill="#737373">{first:%b}</text>')
            last_month = first.month
        for day in week["contributionDays"]:
            d = datetime.date.fromisoformat(day["date"])
            y = top + ((d.weekday() + 1) % 7) * step
            color = LEVELS.get(day["contributionLevel"], LEVELS["NONE"])
            n = day["contributionCount"]
            label = f'{n} contribution{"s" if n != 1 else ""} on {d:%b %d, %Y}'
            out.append(
                f'<rect class="c" style="animation-delay:{w * 0.018:.3f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{color}"><title>{label}</title></rect>'
            )
    for i, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="48" y="{top + i * step + 12}" class="mono" font-size="13" fill="#737373">{name}</text>')

    lx = width - 48 - 5 * step - 44
    ly = height - 40
    legend = [f'<text x="{lx - 46}" y="{ly + 12}" class="mono" font-size="13" fill="#737373">Less</text>']
    for i, c in enumerate(LEVELS.values()):
        legend.append(f'<rect x="{lx + i * step}" y="{ly}" width="{cell}" height="{cell}" rx="4" fill="{c}"/>')
    legend.append(f'<text x="{lx + 5 * step + 6}" y="{ly + 12}" class="mono" font-size="13" fill="#737373">More</text>')

    total = cal["totalContributions"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year">
<style>
  .sans {{ font-family: {SANS}; }} .mono {{ font-family: {MONO}; }}
  .c {{ opacity: 0; animation: pop .5s ease-out forwards; }}
  @keyframes pop {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
</style>
<rect width="{width}" height="{height}" rx="18" fill="#010409"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="none" stroke="#1F242B"/>
<text x="48" y="54" class="sans" font-size="22" font-weight="600" fill="#F5F5F5"><tspan fill="#D97757">{total}</tspan> contributions in the last year</text>
{chr(10).join(out)}
{"".join(legend)}
</svg>
"""


if __name__ == "__main__":
    cal = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else fetch()
    sys.stdout.write(render(cal))
