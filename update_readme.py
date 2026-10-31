"""Builds README.md: ASCII portrait on the left, live GitHub stats on the right.
Run locally:  GH_USER=yourname GH_TOKEN=xxxx python update_readme.py
Runs automatically via .github/workflows/update.yml
"""
import os, json, urllib.request
from datetime import date

# ========= EDIT THESE =========
USER      = os.getenv("GH_USER", "your-username")
NAME      = "yourname"                     # shown as name@github
BIRTHDAY  = date(2004, 1, 1)               # used for the live "Uptime"
INFO = {
    "OS":               "Windows 11, Ubuntu, Android",
    "Host":             "Your College / Company",
    "Kernel":           "Your Major / Role",
    "IDE":              "VS Code, IntelliJ IDEA",
    "Languages.Programming": "Python, Java, JavaScript",
    "Languages.Computer":    "HTML, CSS, JSON, SQL",
    "Languages.Real":        "English, Tamil",
    "Hobbies.Software": "Open source, Web dev, AI tools",
    "Hobbies.Hardware": "PC building, Electronics",
    "Email.Personal":   "you@example.com",
    "LinkedIn":         "your-linkedin",
    "Discord":          "your-discord",
}
# ==============================

TOKEN = os.getenv("GH_TOKEN")

def gh(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN: req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def live_stats():
    try:
        u = gh(f"/users/{USER}")
        repos, page = [], 1
        while True:
            chunk = gh(f"/users/{USER}/repos?per_page=100&page={page}")
            repos += chunk
            if len(chunk) < 100: break
            page += 1
        stars = sum(r["stargazers_count"] for r in repos if not r["fork"])
        commits = gh(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
        return {"Repos": u["public_repos"], "Stars": stars,
                "Followers": u["followers"], "Commits": commits}
    except Exception as e:
        print("stats fallback:", e)
        return {"Repos": "--", "Stars": "--", "Followers": "--", "Commits": "--"}

def uptime():
    t = date.today(); y = t.year - BIRTHDAY.year
    m = t.month - BIRTHDAY.month; d = t.day - BIRTHDAY.day
    if d < 0: m -= 1; d += 30
    if m < 0: y -= 1; m += 12
    return f"{y} years, {m} months, {d} days"

def row(key, val, width=58):
    dots = "." * max(2, width - len(key) - len(str(val)) - 3)
    return f". {key}: {dots} {val}"

def header(title, width=58):
    return f"- {title} " + "-" * (width - len(title) - 3)

def build():
    s = live_stats()
    right = [f"{NAME}@{USER} " + "-" * 40,
             row("OS", INFO["OS"]),
             row("Uptime", uptime()),
             row("Host", INFO["Host"]),
             row("Kernel", INFO["Kernel"]),
             row("IDE", INFO["IDE"]), "",
             row("Languages.Programming", INFO["Languages.Programming"]),
             row("Languages.Computer", INFO["Languages.Computer"]),
             row("Languages.Real", INFO["Languages.Real"]), "",
             row("Hobbies.Software", INFO["Hobbies.Software"]),
             row("Hobbies.Hardware", INFO["Hobbies.Hardware"]), "",
             header("Contact"),
             row("Email.Personal", INFO["Email.Personal"]),
             row("LinkedIn", INFO["LinkedIn"]),
             row("Discord", INFO["Discord"]), "",
             header("GitHub Stats"),
             row("Repos", s["Repos"]),
             row("Stars", s["Stars"]),
             row("Followers", s["Followers"]),
             row("Commits", s["Commits"]),
             f"  (updated {date.today().isoformat()})"]
    left = open("ascii.txt").read().split("\n")
    n = max(len(left), len(right))
    left  += [""] * (n - len(left))
    right += [""] * (n - len(right))
    w = max(len(l) for l in left) + 3
    body = "\n".join(l.ljust(w) + r for l, r in zip(left, right))
    return body

README = """<h3 align="center">{user} / README.md</h3>

<pre>
{body}
</pre>

<p align="center">
  <img height="165" src="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true&theme=dark&hide_border=true" />
  <img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username={user}&layout=compact&theme=dark&hide_border=true" />
</p>
<p align="center">
  <img src="https://streak-stats.demolab.com?user={user}&theme=dark&hide_border=true" />
</p>
<p align="center">
  <img src="https://komarev.com/ghpvc/?username={user}&label=Profile%20views&color=0e75b6&style=flat" />
</p>
"""

if __name__ == "__main__":
    # escape for HTML <pre>
    body = build().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    open("README.md", "w").write(README.format(user=USER, body=body))
    print("README.md updated")
