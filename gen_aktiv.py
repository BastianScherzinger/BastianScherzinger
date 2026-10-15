"""Erzeugt assets/aktiv.svg: Commits pro Tag 2026 ueber alle eigenen Repos.

Zaehlt auch private Repos, die GitHub im Beitragsdiagramm nicht zeigt.
Kopien und Arbeitsbaeume werden ueber den Wurzel-Commit zusammengefasst,
jeder Commit zaehlt einmal.
"""
import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

DESK = Path.home() / "Desktop"
OUT = Path(__file__).parent / "assets" / "aktiv.svg"
BG, BORDER = "#0D1117", "#30363D"
TEXT, MUTED, DIM = "#E6EDF3", "#8B949E", "#6E7681"
ACCENT = "#E8A33D"
LEVELS = ["#161B22", "#3B2A12", "#6B4A1A", "#A86F22", "#E8A33D"]
SANS = 'ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", "Cascadia Code", Consolas, "Liberation Mono", monospace'
START, END = date(2026, 1, 1), date.today()


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


repos = {}
for g in DESK.glob("**/.git"):
    r = g.parent
    rel = str(r.relative_to(DESK)).lower()
    if len(r.relative_to(DESK).parts) > 4 or "-wt-" in rel or "_github-backup" in rel or "claudegehirn" in rel or ".claude" in rel:
        continue
    root = git(r, "rev-list", "--max-parents=0", "HEAD").split()
    if root:
        repos.setdefault(root[-1], r)

seen, days = set(), Counter()
for r in repos.values():
    for line in git(r, "log", "--all", f"--since={START}", "--format=%H %ad", "--date=short").splitlines():
        h, d = line.split()
        if h not in seen:
            seen.add(h)
            days[d] += 1

active = sorted(d for d in days if days[d])
streak = best = 0
prev = None
for d in active:
    cur = date.fromisoformat(d)
    streak = streak + 1 if prev and (cur - prev).days == 1 else 1
    best, prev = max(best, streak), cur
top_day, top_n = days.most_common(1)[0]

GAP = 4
x0, y0 = 70, 150
first = START - timedelta(days=START.weekday())
weeks = (END - first).days // 7 + 1
W = 1200
CELL = int((W - x0 - 40) / weeks) - GAP
H = y0 + 7 * (CELL + GAP) + 76
p = []
p.append(f'<text class="m" x="40" y="40" font-size="12" fill="{DIM}" letter-spacing="1.4">AKTIVITÄT 2026 · ALLE EIGENEN REPOS, AUCH PRIVATE</text>')
stats = [(f"{len(seen):,}".replace(",", "."), "Commits 2026"), (str(len(active)), "aktive Tage"),
         (str(best), "Tage am Stück"), (str(top_n), f"Rekord am {date.fromisoformat(top_day):%d.%m.}")]
for i, (n, l) in enumerate(stats):
    x = 40 + i * 220
    p.append(f'<text class="s" x="{x}" y="82" font-size="30" font-weight="800" fill="{ACCENT if i == 0 else TEXT}">{n}</text>')
    p.append(f'<text class="m" x="{x}" y="100" font-size="12" fill="{MUTED}">{l}</text>')
for i, lab in ((0, "Mo"), (2, "Mi"), (4, "Fr"), (6, "So")):
    p.append(f'<text class="m" x="{x0 - 12}" y="{y0 + i * (CELL + GAP) + CELL * .7:.0f}" text-anchor="end" font-size="11" fill="{DIM}">{lab}</text>')
MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
d, last_m = first, -1
while d <= END:
    wk = (d - first).days // 7
    x = x0 + wk * (CELL + GAP)
    if d.weekday() == 0 and d.month != last_m and d.day <= 7:
        p.append(f'<text class="m" x="{x}" y="{y0 - 10}" font-size="11" fill="{DIM}">{MONTHS[d.month - 1]}</text>')
        last_m = d.month
    if START <= d <= END:
        n = days.get(d.isoformat(), 0)
        lv = 0 if n == 0 else 1 if n <= 5 else 2 if n <= 20 else 3 if n <= 80 else 4
        y = y0 + d.weekday() * (CELL + GAP)
        anim = f'<animate attributeName="opacity" values="1;.55;1" dur="3s" begin="{(wk % 9) * .25:.2f}s" repeatCount="indefinite"/>' if lv == 4 else ""
        p.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3.5" fill="{LEVELS[lv]}"><title>{d:%d.%m.}: {n} Commits</title>{anim}</rect>')
    d += timedelta(days=1)
ly = H - 30
p.append(f'<text class="m" x="{x0}" y="{ly + 12}" font-size="11" fill="{DIM}">weniger</text>')
for i, c in enumerate(LEVELS):
    p.append(f'<rect x="{x0 + 62 + i * 21}" y="{ly}" width="17" height="17" rx="3.5" fill="{c}"/>')
p.append(f'<text class="m" x="{x0 + 62 + 5 * 21 + 6}" y="{ly + 12}" font-size="11" fill="{DIM}">mehr · gemessen am {END:%d.%m.%Y} über {len(repos)} Repos</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Aktivität 2026: {len(seen)} Commits an {len(active)} Tagen, längste Serie {best} Tage">
  <title>Aktivität 2026</title>
  <style>.s{{font-family:{SANS}}} .m{{font-family:{MONO}}} @media (prefers-reduced-motion: reduce){{animate{{display:none}}}}</style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
  {chr(10).join(p)}
</svg>
"""
OUT.write_text(svg, encoding="utf-8")
print("aktiv.svg", len(seen), "Commits,", len(active), "Tage, Serie", best, "Rekord", top_day, top_n, "Repos", len(repos))
