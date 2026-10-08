"""Render the GitHub contribution calendar as a themed SVG (black / orange / gray)."""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

USER = os.environ.get("GH_USER", "strohergustavo")
TZ = ZoneInfo(os.environ.get("GH_TZ", "America/Sao_Paulo"))
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
VIEWER_QUERY = """query {
  viewer {
    login
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
    "FIRST_QUARTILE": "#4F271A",
    "SECOND_QUARTILE": "#7F3B25",
    "THIRD_QUARTILE": "#AE5032",
    "FOURTH_QUARTILE": "#D9663E",
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def graphql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(body["errors"])
    return body["data"]


def rest(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def paged(path):
    sep = "&" if "?" in path else "?"
    page = 1
    while True:
        items = rest(f"{path}{sep}per_page=100&page={page}")
        yield from items
        if len(items) < 100:
            return
        page += 1


def level(n, peak):
    if n == 0:
        return "NONE"
    return ("FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE")[min(3, (4 * n - 1) // peak)]


def from_commits():
    """Rebuild the calendar from the owner's own commits.

    A private profile makes the GraphQL calendar come back empty, even for the
    owner's token, so count commits authored by the user in every repository
    the token can see instead.
    """
    today = datetime.datetime.now(TZ).date()
    start = today - datetime.timedelta(days=364 + (today.weekday() + 1) % 7)
    since = datetime.datetime.combine(start, datetime.time(), TZ).isoformat()
    counts = {}
    try:
        repos = list(paged("/user/repos?affiliation=owner,collaborator"))
    except urllib.error.HTTPError:
        repos = list(paged(f"/users/{USER}/repos"))
    for repo in repos:
        try:
            commits = list(paged(f"/repos/{repo['full_name']}/commits?author={USER}&since={since}"))
        except urllib.error.HTTPError:
            continue  # empty or inaccessible repository
        for c in commits:
            stamp = datetime.datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00"))
            day = stamp.astimezone(TZ).date()
            counts[day] = counts.get(day, 0) + 1
    print(f"Counted commits in {len(repos)} repositories", file=sys.stderr)
    peak = max(counts.values(), default=1)
    weeks, day = [], start
    while day <= today:
        week = []
        for _ in range(7):
            if day <= today:
                n = counts.get(day, 0)
                week.append({"date": day.isoformat(), "contributionCount": n, "contributionLevel": level(n, peak)})
            day += datetime.timedelta(days=1)
        weeks.append({"contributionDays": week})
    return {"totalContributions": sum(counts.values()), "weeks": weeks}


def fetch():
    # A private profile hides the calendar from everyone else, so when the token
    # belongs to the profile owner, read it as the viewer instead.
    data = graphql(VIEWER_QUERY)
    if data["viewer"]["login"].lower() == USER.lower():
        cal = data["viewer"]["contributionsCollection"]["contributionCalendar"]
        if cal["totalContributions"] == 0:
            print("Calendar is empty (private profile); counting commits instead", file=sys.stderr)
            cal = from_commits()
        return cal
    return graphql(QUERY, {"login": USER})["user"]["contributionsCollection"]["contributionCalendar"]


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
            anim = "" if n == 0 else f' class="f" style="animation-delay:{0.4 + w * 0.03:.2f}s"'
            out.append(
                f'<rect{anim} x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{color}"><title>{label}</title></rect>'
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
  .f {{ animation: grow .6s ease-out both; }}
  @keyframes grow {{ from {{ fill: #151B23 }} }}
</style>
<rect width="{width}" height="{height}" rx="18" fill="#010409"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="none" stroke="#1F242B"/>
<text x="48" y="54" class="sans" font-size="22" font-weight="600" fill="#F5F5F5"><tspan fill="#D9663E">{total}</tspan> contributions in the last year</text>
{chr(10).join(out)}
{"".join(legend)}
</svg>
"""


if __name__ == "__main__":
    cal = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else fetch()
    if cal["totalContributions"] == 0:
        raise SystemExit("Got 0 contributions; keeping the previous graph.")
    sys.stdout.write(render(cal))
