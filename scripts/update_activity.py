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


def activity_data(calendar):
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
    return today, recent, counts, streak


def render(calendar):
    today, recent, counts, streak = activity_data(calendar)
    maximum = max(counts, default=1) or 1
    step = 1104 / len(counts)
    bars = []
    for i, count in enumerate(counts):
        height = max(3, count / maximum * 76)
        x = 48 + i * step
        fill = '#f4f3ef' if count else '#353539'
        bars.append(
            f'<rect x="{x:.1f}" y="{350-height:.1f}" '
            f'width="{max(2, step-11):.1f}" height="{height:.1f}" fill="{fill}">'
            f'<title>{recent[i]["date"]}: {count} contributions</title></rect>'
        )
    metrics = ''.join(
        f'<text x="{x}" y="166" class="value">{value}</text>'
        f'<text x="{x}" y="199" class="label">{label}</text>'
        for x, value, label in [
            (48, f'{calendar["totalContributions"]:,}', 'CONTRIBUTIONS / YEAR'),
            (448, f'{sum(counts):,}', 'CONTRIBUTIONS / 30 DAYS'),
            (848, f'{streak:02}', 'CURRENT STREAK / DAYS'),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity for n3wbiekkkk</title>
<desc id="desc">{calendar['totalContributions']} contributions in the past year, {sum(counts)} in the last 30 days, and a {streak}-day current streak. Updated {today.isoformat()}.</desc>
<style>
text{{font-family:Arial,Helvetica,sans-serif}}
.value{{font-size:86px;font-weight:700;letter-spacing:-4px;fill:#f4f3ef}}
.label{{font-family:'Courier New',monospace;font-size:13px;letter-spacing:1px;fill:#99999d}}
.section{{font-family:'Courier New',monospace;font-size:14px;letter-spacing:1.5px;fill:#f4f3ef}}
</style>
<rect width="1200" height="420" fill="#0a0a0b"/>
<rect x=".5" y=".5" width="1199" height="419" fill="none" stroke="#2b2b2e"/>
<path d="M48 0H164" stroke="#f4f3ef" stroke-width="4"/>
<text x="48" y="43" class="section">02 / GITHUB ACTIVITY</text>
<text x="1152" y="43" text-anchor="end" class="label">UPDATED / {today.isoformat()}</text>
<path d="M48 68H1152M400 99V205M800 99V205M48 230H1152" fill="none" stroke="#2b2b2e"/>
{metrics}
<text x="48" y="257" class="label">THE LAST 30 DAYS</text>
<text x="1152" y="257" text-anchor="end" class="label">DAILY FREQUENCY</text>
<path d="M48 275H1152M48 312H1152" stroke="#1b1b1e"/>
{''.join(bars)}
<path d="M48 351H1152" stroke="#45454a"/>
<text x="48" y="376" class="label">{recent[0]['date']}</text>
<text x="1152" y="376" text-anchor="end" class="label">{recent[-1]['date']}</text>
<text x="48" y="405" class="label" font-size="10">SOURCE / GITHUB CONTRIBUTION CALENDAR</text>
<path d="M1120 399H1152M1144 391L1152 399L1144 407" fill="none" stroke="#99999d"/>
</svg>'''


def render_mobile(calendar):
    today, recent, counts, streak = activity_data(calendar)
    maximum = max(counts, default=1) or 1
    step = 536 / len(counts)
    bars = []
    for i, count in enumerate(counts):
        height = max(3, count / maximum * 76)
        x = 32 + i * step
        fill = '#f4f3ef' if count else '#353539'
        bars.append(
            f'<rect x="{x:.1f}" y="{530-height:.1f}" '
            f'width="{max(2, step-6):.1f}" height="{height:.1f}" fill="{fill}">'
            f'<title>{recent[i]["date"]}: {count} contributions</title></rect>'
        )
    metrics = ''.join(
        f'<text x="32" y="{y-29}" class="label">{label}</text>'
        f'<text x="32" y="{y-5}" class="label">{period}</text>'
        f'<text x="568" y="{y}" text-anchor="end" class="value">{value}</text>'
        for y, value, label, period in [
            (163, f'{calendar["totalContributions"]:,}', 'CONTRIBUTIONS', 'PAST YEAR'),
            (263, f'{sum(counts):,}', 'CONTRIBUTIONS', 'LAST 30 DAYS'),
            (363, f'{streak:02}', 'CURRENT STREAK', 'DAYS'),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="620" viewBox="0 0 600 620" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity for n3wbiekkkk</title>
<desc id="desc">{calendar['totalContributions']} contributions in the past year, {sum(counts)} in the last 30 days, and a {streak}-day current streak. Updated {today.isoformat()}.</desc>
<style>
text{{font-family:Arial,Helvetica,sans-serif}}
.value{{font-size:76px;font-weight:700;letter-spacing:-4px;fill:#f4f3ef}}
.label{{font-family:'Courier New',monospace;font-size:18px;letter-spacing:1px;fill:#99999d}}
.section{{font-family:'Courier New',monospace;font-size:18px;letter-spacing:1px;fill:#f4f3ef}}
</style>
<rect width="600" height="620" fill="#0a0a0b"/>
<rect x=".5" y=".5" width="599" height="619" fill="none" stroke="#2b2b2e"/>
<path d="M32 0H148" stroke="#f4f3ef" stroke-width="4"/>
<text x="32" y="40" class="section">02 / GITHUB ACTIVITY</text>
<text x="32" y="70" class="label">UPDATED / {today.isoformat()}</text>
<path d="M32 90H568M32 190H568M32 290H568M32 390H568" fill="none" stroke="#2b2b2e"/>
{metrics}
<text x="32" y="425" class="label">THE LAST 30 DAYS</text>
<path d="M32 454H568M32 492H568" stroke="#1b1b1e"/>
{''.join(bars)}
<path d="M32 531H568" stroke="#45454a"/>
<text x="32" y="558" class="label">{recent[0]['date']}</text>
<text x="568" y="558" text-anchor="end" class="label">{recent[-1]['date']}</text>
<text x="32" y="596" class="label">SOURCE / GITHUB</text>
<path d="M536 590H568M560 582L568 590L560 598" fill="none" stroke="#99999d"/>
</svg>'''


if __name__ == '__main__':
    raw = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else subprocess.check_output(['gh', 'api', 'graphql', '-f', f'query={QUERY}'], text=True)
    response = json.loads(raw)
    calendar = response['data']['user']['contributionsCollection']['contributionCalendar']
    (ROOT / 'assets/activity-mono.svg').write_text(render(calendar))
    (ROOT / 'assets/activity-mobile.svg').write_text(render_mobile(calendar))
    print('Updated assets/activity-mono.svg and assets/activity-mobile.svg')
