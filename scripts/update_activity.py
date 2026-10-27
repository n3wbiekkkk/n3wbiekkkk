"""Render public GitHub contribution data into the profile's activity panel."""
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERY = '''query { user(login: "n3wbiekkkk") { contributionsCollection {
contributionCalendar { totalContributions weeks { contributionDays {
contributionCount date weekday
} } } } } }'''


def render(calendar):
    days = [d for w in calendar['weeks'] for d in w['contributionDays']]
    today = date.fromisoformat(days[-1]['date'])
    recent = [d for d in days if date.fromisoformat(d['date']) > today - timedelta(days=30)]
    counts = [d['contributionCount'] for d in recent]
    streak = 0
    # An unfinished day without contributions does not break yesterday's streak.
    completed = days[:-1] if not days[-1]['contributionCount'] else days
    for day in reversed(completed):
        if not day['contributionCount']:
            break
        streak += 1
    maximum = max(counts, default=1) or 1
    bars = []
    for i, count in enumerate(counts):
        height = max(3, count / maximum * 103)
        x = 53 + i * 36.4
        bars.append(f'<rect x="{x:.1f}" y="{337-height:.1f}" width="22" height="{height:.1f}" rx="3" fill="{"#f5f5f5" if count else "#262626"}"><title>{recent[i]["date"]}: {count} contributions</title></rect>')
    metrics = ''.join(f'<text x="{x}" y="133" class="value">{value}</text><text x="{x}" y="160" class="label">{label}</text>' for x, value, label in [(48, f'{calendar["totalContributions"]:,}', 'CONTRIBUTIONS / YEAR'), (448, f'{sum(counts):,}', 'CONTRIBUTIONS / 30 DAYS'), (848, f'{streak:02}', 'CURRENT STREAK / DAYS')])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="395" viewBox="0 0 1200 395" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity for n3wbiekkkk</title>
<desc id="desc">{calendar['totalContributions']} contributions in the past year, {sum(counts)} in the last 30 days, and a {streak}-day current streak. Updated {today.isoformat()}.</desc>
<style>text{{font-family:Arial,Helvetica,sans-serif}}.value{{font-size:62px;font-weight:700;letter-spacing:-3px;fill:#f5f5f5}}.label{{font-family:monospace;font-size:12px;letter-spacing:1px;fill:#999999}}</style>
<rect x=".5" y=".5" width="1199" height="394" rx="16" fill="#0b0b0b" stroke="#2a2a2a"/>
<text x="48" y="40" class="label" fill="#f5f5f5">GITHUB / ACTIVITY</text><text x="1152" y="40" text-anchor="end" class="label">{today.strftime('%d %b %Y').upper()}</text>
{metrics}<path d="M400 80V164M800 80V164M48 194H1152" stroke="#2a2a2a"/>
<text x="48" y="221" class="label">LAST 30 DAYS</text><text x="1152" y="221" text-anchor="end" class="label">CONTRIBUTIONS / DAY</text>
{''.join(bars)}<path d="M48 343H1152" stroke="#2a2a2a"/>
<text x="48" y="373" class="label">{recent[0]['date']}</text><text x="1152" y="373" text-anchor="end" class="label">{recent[-1]['date']}</text></svg>'''


if __name__ == '__main__':
    raw = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={QUERY}'], text=True)
    response = json.loads(raw)
    calendar = response['data']['user']['contributionsCollection']['contributionCalendar']
    (ROOT / 'assets/activity.svg').write_text(render(calendar))
    print('Updated assets/activity.svg')
