"""Generates dark_mode.svg + light_mode.svg: ASCII portrait + live GitHub stats.
Run locally:  GH_USER=AshwinKirbaa GH_TOKEN=xxxx python update_readme.py
Runs automatically through .github/workflows/update.yml
"""
import os, json, urllib.request
from datetime import date
from xml.sax.saxutils import escape

# ============ EDIT THESE ============
USER     = os.getenv("GH_USER", "AshwinKirbaa")
NAME     = "ashwin"
BIRTHDAY = date(2004, 1, 1)          # <- your real birthday, drives the live Uptime
INFO = [
    ("OS",                    "Windows 11, Ubuntu, Android"),
    ("Host",                  "Your College / Company"),
    ("Kernel",                "Your Major / Role"),
    ("IDE",                   "VS Code, IntelliJ IDEA"),
    None,
    ("Languages.Programming", "Python, Java, JavaScript"),
    ("Languages.Computer",    "HTML, CSS, JSON, SQL"),
    ("Languages.Real",        "English, Tamil"),
    None,
    ("Hobbies.Software",      "Open source, Web dev, AI tools"),
    ("Hobbies.Hardware",      "PC building, Electronics"),
]
CONTACT = [
    ("Email.Personal", "ashwinkirbaa17@gmail.com"),
    ("LinkedIn",       "ashwin-kirbaa17"),
    ("GitHub",         USER),
]
# ====================================

TOKEN = os.getenv("GH_TOKEN")
def gh(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN: req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)

def stats():
    try:
        u = gh(f"/users/{USER}")
        repos, page = [], 1
        while True:
            c = gh(f"/users/{USER}/repos?per_page=100&page={page}"); repos += c
            if len(c) < 100: break
            page += 1
        return [("Repos", u["public_repos"]),
                ("Stars", sum(r["stargazers_count"] for r in repos if not r["fork"])),
                ("Followers", u["followers"]),
                ("Following", u["following"]),
                ("Commits", gh(f"/search/commits?q=author:{USER}&per_page=1")["total_count"])]
    except Exception as e:
        print("stats fallback:", e)
        return [(k, "--") for k in ("Repos", "Stars", "Followers", "Following", "Commits")]

def uptime():
    t = date.today(); y = t.year - BIRTHDAY.year
    m = t.month - BIRTHDAY.month; d = t.day - BIRTHDAY.day
    if d < 0: m -= 1; d += 30
    if m < 0: y -= 1; m += 12
    return f"{y} years, {m} months, {d} days"

THEMES = {
  "dark":  dict(bg="#0d1117", ascii="#c9d1d9", key="#ffa657", val="#79c0ff", head="#e6edf3", dots="#484f58"),
  "light": dict(bg="#ffffff", ascii="#24292f", key="#bc4c00", val="#0550ae", head="#1f2328", dots="#afb8c1"),
}
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

def render(theme):
    c = THEMES[theme]
    art = open(f"ascii_{theme}.txt").read().split("\n")
    AFS, ALH = 8, 9                       # ascii font size / line height
    CW = AFS * 0.602                      # monospace cell width
    ART_W = int(max(len(l) for l in art) * CW) + 20
    X0 = ART_W + 20                       # info panel left
    PW = 470                              # info panel width
    W, FS, LH = X0 + PW + 20, 13, 21
    s = stats()
    rows = [("head", f"{NAME}@{USER}")]
    rows += [("kv", "OS", INFO[0][1]), ("kv", "Uptime", uptime())] + [("kv", *i) if i else ("gap",) for i in INFO[1:]]
    rows += [("gap",), ("head", "Contact")] + [("kv", *i) for i in CONTACT]
    rows += [("gap",), ("head", "GitHub Stats")] + [("kv", k, str(v)) for k, v in s]
    rows += [("gap",), ("note", f"updated {date.today().isoformat()}")]
    H = max(len(art) * ALH + 30, len(rows) * LH + 50)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="100%" height="100%" rx="10" fill="{c["bg"]}"/>',
         f'<g font-family="{MONO}" font-size="{AFS}" fill="{c["ascii"]}" xml:space="preserve">']
    for i, l in enumerate(art):
        body = l.strip(" ")
        if body:
            lead = len(l) - len(l.lstrip(" "))     # position by offset: SVG collapses leading spaces
            o.append(f'<text x="{14 + lead*CW:.1f}" y="{22 + i*ALH}" style="white-space:pre" textLength="{len(body)*CW:.1f}" lengthAdjust="spacing">{escape(body)}</text>')
    o.append('</g>')
    o.append(f'<g font-family="{MONO}" font-size="{FS}">')
    y = 34
    for r in rows:
        if r[0] == "head":
            o.append(f'<text x="{X0}" y="{y}" fill="{c["head"]}" font-weight="bold">{escape(r[1])}</text>')
            o.append(f'<line x1="{X0 + len(r[1])*FS*0.602 + 10:.0f}" x2="{X0+PW}" y1="{y-4}" y2="{y-4}" stroke="{c["dots"]}"/>')
        elif r[0] == "kv":
            k, v = r[1], r[2]
            o.append(f'<text x="{X0}" y="{y}" fill="{c["key"]}">{escape(k)}:</text>')
            kx = X0 + (len(k) + 2) * FS * 0.602
            vx = X0 + PW - len(v) * FS * 0.602 - 6
            o.append(f'<line x1="{kx:.0f}" x2="{vx:.0f}" y1="{y-2}" y2="{y-2}" stroke="{c["dots"]}" stroke-dasharray="1 4" stroke-linecap="round"/>')
            o.append(f'<text x="{X0+PW}" y="{y}" fill="{c["val"]}" text-anchor="end">{escape(v)}</text>')
        elif r[0] == "note":
            o.append(f'<text x="{X0}" y="{y}" fill="{c["dots"]}" font-size="11">{escape(r[1])}</text>')
        y += LH if r[0] != "gap" else LH // 2
    o.append('</g></svg>')
    open(f"{theme}_mode.svg", "w").write("\n".join(o))

if __name__ == "__main__":
    for t in THEMES: render(t)
    print("SVGs updated")
