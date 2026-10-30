"""Collect public GitHub metrics and render the profile's SVG dashboard.

Python standard library only. Run with --render-only to use data/metrics.json.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from html import escape
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER = "Duong31102005"
TZ = timezone(timedelta(hours=7))
PROJECTS = [
    ("Duong31102005/AI_Robot", "owned", "Vision + voice robotics"),
    ("namp12/robot_main", "team", "ROS 2 navigation + delivery"),
    ("namp12/Robot_web", "team", "Robot control + telemetry"),
    ("namp12/Robot_Tu_Hanh", "team", "Autonomous mobile robot"),
    ("namp12/cang_tin_truong_hoc", "team", "Canteen operations platform"),
    ("Duong31102005/btl_Nhom11", "owned", "Web application"),
    ("Duong31102005/Quan-li-khoa-hoc", "owned", "Course management"),
]
CYAN, MINT, PURPLE = "#4ddaf0", "#70e5bd", "#b3a0ff"
TEXT, MUTED, GRID = "#e4eef8", "#91a4b9", "#233345"
PALETTE = [CYAN, PURPLE, MINT, "#f6bd72", "#ed8fb2", "#739efa", "#65758d"]


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def dt(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include its timezone")
    return parsed


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Duong-profile-analytics",
               "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = Request("https://api.github.com" + path, headers=headers)
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def collect():
    now = datetime.now(timezone.utc)
    local_now = now.astimezone(TZ)
    first = local_now.year * 12 + local_now.month - 1 - 5
    since = datetime(first // 12, first % 12 + 1, 1, tzinfo=TZ).astimezone(timezone.utc)

    def one(project):
        name, relationship, _ = project
        base = "/repos/" + name
        meta = api(base)
        if meta.get("private") is not False:
            raise RuntimeError("Only public repositories may be included: " + name)
        languages = api(base + "/languages")
        commits = {}
        page = 1
        while True:
            query = urlencode({"author": USER, "since": iso(since), "until": iso(now),
                               "sha": meta["default_branch"], "per_page": 100, "page": page})
            batch = api(base + "/commits?" + query)
            if not isinstance(batch, list):
                raise RuntimeError("Unexpected commit response for " + name)
            for commit in batch:
                date = commit["commit"]["author"]["date"]
                if since <= dt(date) <= now:
                    commits[commit["sha"]] = {"sha": commit["sha"], "date": date}
            if len(batch) < 100:
                break
            page += 1
        return {"full_name": name, "relationship": relationship, "private": False,
                "fork": meta["fork"], "stars": meta["stargazers_count"],
                "forks": meta["forks_count"], "pushed_at": meta["pushed_at"],
                "primary_language": meta["language"], "language_bytes": languages,
                "commits": sorted(commits.values(), key=lambda c: (c["date"], c["sha"]))}

    with ThreadPoolExecutor(max_workers=4) as pool:
        repos = list(pool.map(one, PROJECTS))
    return {"user": USER, "generated_at": iso(now), "since": iso(since), "repos": repos}


def validate(data):
    """Reject incomplete snapshots rather than publishing missing data as zero."""
    if data.get("user") != USER:
        raise ValueError("Unexpected profile owner")
    since, now = dt(data["since"]), dt(data["generated_at"])
    if since > now:
        raise ValueError("Snapshot end precedes the activity window")
    expected = {name: relation for name, relation, _ in PROJECTS}
    repos = data.get("repos")
    if not isinstance(repos, list) or len(repos) != len(expected):
        raise ValueError("All selected repositories must be present")
    seen = set()
    for repo in repos:
        name = repo["full_name"]
        if name not in expected or name in seen or repo["relationship"] != expected[name]:
            raise ValueError("Unexpected, duplicate, or misclassified repository: " + name)
        seen.add(name)
        if repo.get("private") is not False or not isinstance(repo.get("fork"), bool):
            raise ValueError("Incomplete or non-public repository metadata: " + name)
        languages = repo.get("language_bytes")
        if not isinstance(languages, dict) or any(
            not isinstance(k, str) or type(v) is not int or v < 0 for k, v in languages.items()
        ):
            raise ValueError("Missing or invalid language byte data: " + name)
        if not isinstance(repo.get("commits"), list):
            raise ValueError("Missing commit data: " + name)
        dt(repo["pushed_at"])
        commits = {}
        for commit in repo["commits"]:
            sha, date = commit["sha"], commit["date"]
            if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
                raise ValueError("Invalid commit SHA: " + name)
            if since <= dt(date) <= now:
                commits[sha] = {"sha": sha, "date": date}
        repo["commits"] = sorted(commits.values(), key=lambda c: (c["date"], c["sha"]))
    data["repos"] = sorted(repos, key=lambda repo: list(expected).index(repo["full_name"]))


def text(x, y, value, size=14, color=TEXT, weight=400, anchor="start", mono=False):
    font = "Consolas,monospace" if mono else "Segoe UI,Arial,sans-serif"
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>')


def rect(x, y, w, h, fill, radius=0, stroke="none"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def svg(title, body, width=480, height=280):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>'
            + rect(1, 1, width-2, height-2, "#101925", 16, GRID) + body + "</svg>\n")


def panel(title, subtitle, content, note):
    return svg(title, rect(23, 25, 3, 18, CYAN, 1) + text(36, 40, title, 18, TEXT, 600)
               + text(24, 63, subtitle, 12, MUTED) + content + text(24, 259, note, 11, MUTED))


def donut(title, subtitle, values, note):
    values = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    if len(values) > 6:
        values = values[:5] + [("Other", sum(value for _, value in values[5:]))]
    total = sum(value for _, value in values)
    body = ""
    if total:
        start = -90
        circumference = 2*math.pi*61
        for index, (name, value) in enumerate(values):
            angle = 360*value/total
            body += (f'<circle cx="117" cy="157" r="61" fill="none" stroke="{PALETTE[index]}" '
                     f'stroke-width="19" stroke-dasharray="{angle/360*circumference:.5f} {circumference:.5f}" '
                     f'transform="rotate({start} 117 157)"/>')
            y = 99 + index*25
            body += rect(225, y-9, 8, 8, PALETTE[index], 2)
            body += text(244, y, name, 13) + text(453, y, f"{value/total:.1%}", 13, MUTED, anchor="end")
            start += angle
        body += text(117, 157, f"{total/1_000_000:.2f} MB", 18, TEXT, 600, "middle")
        body += text(117, 177, "CODE BYTES", 10, MUTED, anchor="middle", mono=True)
    else:
        body += text(240, 157, "No language data available", 16, MUTED, anchor="middle")
    return panel(title, subtitle, body, note)


def bars(title, subtitle, labels, values, note, color=CYAN, ticks=None):
    left, top, bottom, width = 42, 100, 220, 411
    ceiling = max(1, math.ceil(max(values, default=0)/5)*5)
    body = ""
    for fraction in [0, .5, 1]:
        y = bottom-fraction*(bottom-top)
        body += f'<path d="M{left} {y}H455" stroke="{GRID}" stroke-width="1"/>'
        body += text(31, y+4, f"{ceiling*fraction:g}", 10, MUTED, anchor="end")
    step = width/len(values)
    bw = max(3, step*.58)
    for i, (label, value) in enumerate(zip(labels, values)):
        x = left+step*i+(step-bw)/2
        height = (bottom-top)*value/ceiling
        if value:
            body += rect(round(x, 2), round(bottom-height, 2), round(bw, 2), round(height, 2), color, 3)
        if len(values) <= 7:
            body += text(x+bw/2, bottom-height-7, value, 12, TEXT, anchor="middle")
        if ticks is None or i in ticks:
            body += text(x+bw/2, 240, label, 11, MUTED, anchor="middle")
    return panel(title, subtitle, body, note)


def repo_bars(repos, note):
    rows = sorted(repos, key=lambda r: (-len(r["commits"]), r["full_name"]))
    maximum = max((len(r["commits"]) for r in rows), default=1) or 1
    body = ""
    for i, repo in enumerate(rows):
        y = 94+i*22
        name = repo["full_name"].split("/")[1]
        short = {"cang_tin_truong_hoc": "Smart Canteen", "Quan-li-khoa-hoc": "Course Management"}.get(name, name)
        count = len(repo["commits"])
        body += text(24, y+7, short, 12)
        body += rect(186, y-3, 224, 10, "#1c2c3b", 4)
        if count:
            body += rect(186, y-3, count/maximum*224, 10, CYAN if repo["relationship"]=="owned" else PURPLE, 4)
        body += text(452, y+7, count, 12, TEXT, 600, "end")
    return panel("Commits by project", "Your authored commits on default branches", body, note)


def header():
    body = '<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#4ddaf0" stroke-opacity=".055"/></pattern></defs>'
    body += rect(2, 2, 956, 194, "url(#grid)", 16)
    body += text(34, 37, "DUONG31102005  /  ENGINEERING PROFILE", 11, MUTED, mono=True)
    body += text(32, 101, "ROBOTICS + AI", 48, TEXT, 700)
    body += text(35, 136, "Building systems that sense, decide, and move.", 17, MUTED)
    body += text(35, 171, "ROS 2   /   COMPUTER VISION   /   EMBEDDED   /   SOFTWARE", 11, CYAN, mono=True)
    body += '<g fill="none" stroke="#4ddaf0" stroke-width="2" stroke-linecap="round"><circle cx="817" cy="96" r="66" stroke-opacity=".2"/><circle cx="817" cy="96" r="80" stroke-opacity=".3" stroke-dasharray="2 9"/><rect x="778" y="67" width="78" height="65" rx="15"/><path d="M799 89v12m36-12v12m-31 16h26m-13-50V52m-42 40h-16m100 0h16"/><circle cx="817" cy="47" r="4" fill="#70e5bd"/></g>'
    return svg("Duong — Robotics, AI and software", body, 960, 198)


def render(data):
    validate(data)
    repos = data["repos"]
    since, now = dt(data["since"]), dt(data["generated_at"])
    unique = {}
    for repo in repos:
        for commit in repo["commits"]:
            unique[commit["sha"]] = dt(commit["date"]).astimezone(TZ)
    times = list(unique.values())
    date = now.astimezone(TZ).strftime("%Y-%m-%d")
    window = f"{since.astimezone(TZ):%b %Y} – {now.astimezone(TZ):%b %Y}"
    note = f"Public snapshot · {date}"
    outputs = {"header.svg": header()}
    active = len({d.date() for d in times})
    overview = ""
    summary = [(len(repos), "PUBLIC PROJECTS"), (sum(r["relationship"]=="team" for r in repos), "TEAM REPOSITORIES"),
               (len(unique), "AUTHORED COMMITS"), (active, "ACTIVE DAYS")]
    for i, (value, label) in enumerate(summary):
        x = 30+i*239
        if i:
            overview += f'<path d="M{x-14} 25V78" stroke="{GRID}"/>'
        overview += text(x, 55, value, 31, CYAN if i%2==0 else PURPLE, 700)
        overview += text(x, 78, label, 10, MUTED, mono=True)
    overview += text(30, 106, f"{window} · Selected public projects · UTC+07:00 · Updated {date}", 11, MUTED)
    outputs["overview.svg"] = svg("Repository and activity overview", overview, 960, 122)
    for relationship, title in [("owned", "Owned repository languages"), ("team", "Team repository languages")]:
        languages = Counter()
        for repo in repos:
            if repo["relationship"] == relationship and not repo["fork"]:
                languages.update(repo["language_bytes"])
        count = sum(r["relationship"]==relationship and not r["fork"] for r in repos)
        outputs[f"languages-{relationship}.svg"] = donut(title, f"Code composition by bytes · {count} public repositories", languages, note)
    months = []
    index = since.astimezone(TZ).year*12+since.astimezone(TZ).month-1
    end = now.astimezone(TZ)
    while index <= end.year*12+end.month-1:
        months.append((index//12, index%12+1))
        index += 1
    monthly = Counter((d.year, d.month) for d in times)
    outputs["monthly.svg"] = bars("Commit timeline", window+" · Your authored commits",
        [datetime(y, m, 1).strftime("%b") for y, m in months], [monthly[m] for m in months], note)
    hours = Counter(d.hour for d in times)
    outputs["hours.svg"] = bars("Commit hours", "Author timestamps · UTC+07:00", list(map(str, range(24))),
        [hours[h] for h in range(24)], note, PURPLE, [0, 6, 12, 18, 23])
    weekdays = Counter(d.weekday() for d in times)
    outputs["weekdays.svg"] = bars("Weekly rhythm", window+" · Commits by weekday",
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [weekdays[d] for d in range(7)], note, MINT)
    outputs["repositories.svg"] = repo_bars(repos, note)
    byname = {r["full_name"]: r for r in repos}
    rows = ["| Project | Focus | Relationship | Commits¹ |", "|:---|:---|:---|---:|"]
    for full_name, relationship, focus in PROJECTS:
        repo = byname[full_name]
        label = full_name.split("/")[1]
        relation = "Owned repo" if relationship=="owned" else "Team project"
        rows.append(f"| [{label}](https://github.com/{full_name}) | {focus} | {relation} | {len(repo['commits'])} |")
    table = "\n".join(rows)+f"\n\n<sub>¹ Your authored commits · {window} · Default branches · Snapshot {date}</sub>"
    readme = ROOT/"README.md"
    old = readme.read_text(encoding="utf-8")
    new, count = re.subn(r"(?s)(<!-- PROJECT_TABLE:START -->).*?(<!-- PROJECT_TABLE:END -->)",
                         lambda m: m[1]+"\n"+table+"\n"+m[2], old)
    if count != 1:
        raise RuntimeError("Expected exactly one project table marker in README")
    methodology = f'''# Analytics methodology

Snapshot: **{data['generated_at']}**. Window: **{data['since']}** through the snapshot timestamp.

- Scope: the seven explicitly selected public project repositories linked in the profile. The profile repository and private repositories are excluded.
- Owned repository means hosted under `{USER}`; it does not claim sole authorship. Team repositories belong to `namp12` and are projects the profile owner participates in.
- Commits come from GitHub REST `/repos/OWNER/REPO/commits`, filtered with `author={USER}` on each default branch. All pages are read. Only author timestamps within the window are counted.
- Overall charts deduplicate commit SHA across repositories. Per-project counts are specific to that repository. This is a scoped activity view, not GitHub's full contribution-calendar total.
- Hours, weekdays, and active days use author timestamps converted to UTC+07:00. These timestamps do not measure working hours or productivity.
- Language charts sum GitHub `/languages` byte counts separately for owned and team repositories, excluding forks. They describe repository contents, including code from teammates and any detectable vendored/generated files; they do not represent individual contribution shares or skill ratings. Empty language responses are retained as empty, not estimated.
- The window covers six calendar months including the current partial month. Failed API reads stop the update and preserve the previous published snapshot.

[Source data](data/metrics.json) · [Refresh script](scripts/update_profile.py)

## Repository activity

| Repository | Your commits | Repository last pushed (UTC) | Code bytes |
|:---|---:|:---|---:|
'''
    for repo in repos:
        methodology += f"| [{repo['full_name']}](https://github.com/{repo['full_name']}) | {len(repo['commits'])} | {repo['pushed_at']} | {sum(repo['language_bytes'].values()):,} |\n"
    assets = ROOT/"assets"
    assets.mkdir(exist_ok=True)
    for name, contents in outputs.items():
        (assets/name).write_text(contents, encoding="utf-8")
    readme.write_text(new, encoding="utf-8")
    (ROOT/"ANALYTICS.md").write_text(methodology, encoding="utf-8")
    print(json.dumps({"projects": len(repos), "unique_commits": len(unique), "active_days": active,
                      "assets": len(outputs), "snapshot": date}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-only", action="store_true", help="Render the existing public snapshot without network requests")
    args = parser.parse_args()
    path = ROOT/"data"/"metrics.json"
    data = json.loads(path.read_text(encoding="utf-8")) if args.render_only else collect()
    render(data)
    if not args.render_only:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
