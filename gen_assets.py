"""Erzeugt die animierten SVG-Assets fuer das GitHub-Profil.

Alle Inhalte stammen aus gemessenen Daten (Git-Historie, Dateisystem, DNS,
Railway, GitHub-API) — es werden keine Werte geschaetzt oder erfunden.

Robustheitsregel: Jedes Element ist im Grundzustand vollstaendig sichtbar.
Animation kommt nur additiv dazu (wandernde Lichtpunkte, pulsierende Ringe).
So bleibt das Bild korrekt, wenn ein Renderer nur ein Standbild zeigt oder
der Betrachter `prefers-reduced-motion` gesetzt hat.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

# --- Design-Tokens -----------------------------------------------------------
BG, BORDER = "#0D1117", "#30363D"
TEXT, MUTED, DIM = "#E6EDF3", "#8B949E", "#6E7681"
ACCENT, ACCENT_DIM, HAIR = "#E8A33D", "#8A6524", "#21262D"

SANS = 'ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", "Cascadia Code", Consolas, "Liberation Mono", monospace'

BASE_CSS = f"""
    .s {{ font-family: {SANS}; }}
    .m {{ font-family: {MONO}; }}
    .ring {{ animation: pulse 3.6s ease-in-out infinite;
             transform-box: fill-box; transform-origin: center; }}
    @keyframes pulse {{ 0%,100% {{ transform: scale(1); opacity: .30 }}
                        50%     {{ transform: scale(1.35); opacity: .04 }} }}
    @media (prefers-reduced-motion: reduce) {{
      .ring, .comet {{ animation: none !important; }}
    }}
"""


def card(w, h, defs="", extra_css="", body="", title=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <defs>{defs}</defs>
  <style>{BASE_CSS}{extra_css}</style>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
{body}
</svg>
"""


# ============================================================ JOURNEY =========
# (Zeit, Titel, Beschreibung, Meilenstein?)
PHASES = [
    ("2016 – 2021   ·   FRÜHE JAHRE", [
        ("2016", "Scratch", "Mit 11 die ersten Blöcke zusammengesteckt", 0),
        ("2017", "Python", "Mit 12 der Einstieg — eingeführt vom Vater", 0),
        ("2018–19", "Programmier-AG", "Im Internat 10–15 Schülern Python beigebracht", 1),
        ("Jul 2019", "Tommy", "Erstes eigenes Script auf GitHub — steht bis heute dort", 0),
        ("2019–21", "Linux & Hardware", "Kali, 4-Node-Raspberry-Pi-Cluster, LED-Projekte", 0),
    ]),
    ("2025 – 2026   ·   NEUSTART", [
        ("Jul 2025", "Realschulabschluss", "TikTok @python_tutorials_de startet — Lehren als Lernmethode", 1),
        ("Dez 2025", "Wieder bei null", "hello world, turtle-Grafik, ursina — bewusst von vorn", 0),
        ("Jan–Feb 2026", "Grundlagen", "Scraper, Flask, REST-APIs, OpenCV", 0),
        ("Mär 2026", "VintedBot", "Erster bezahlter Auftrag — über einen TikTok-Kommentar", 1),
    ]),
    ("2026   ·   PROFESSIONELL", [
        ("Apr 2026", "Fünf Bot-Iterationen", "async, MongoDB, Proxy-Routing, Dashboard — in 23 Tagen", 0),
        ("Mai 2026", "Django", "Erste Kundenseiten gehen live", 0),
        ("Jun 2026", "JARVIS", "Eigene KI-Agenten-Plattform — 44.285 Zeilen, 258 Commits", 1),
        ("Jul 2026", "livingen", "47.785 Zeilen, 1.545 Tests, Docker, GitHub Actions", 1),
        ("Aug 2026", "LieferungDirekt", "FastAPI + native Kotlin-App, 214 Tests, übergabefertig", 1),
    ]),
]

SPINE_X, YEAR_X, TEXT_X = 92, 124, 236
ROW_H, HEAD_H, PAD_TOP = 56, 52, 40


def journey():
    rows, y = [], PAD_TOP + 26
    for phase, items in PHASES:
        rows.append(("head", phase, y))
        y += HEAD_H
        for it in items:
            rows.append(("item", it, y))
            y += ROW_H
        y += 10
    height = y + 16

    ys = [r[2] for r in rows if r[0] == "item"]
    first_y, last_y = ys[0], ys[-1]

    body = [
        f'  <text class="s" x="44" y="{PAD_TOP-4}" font-size="12" fill="{DIM}" letter-spacing="1.4">ENTWICKLUNGSWEG</text>',
        # Rueckgrat: immer vollstaendig gezeichnet
        f'  <line x1="{SPINE_X}" y1="{first_y}" x2="{SPINE_X}" y2="{last_y}" stroke="{HAIR}" stroke-width="2" stroke-linecap="round"/>',
        f'  <line x1="{SPINE_X}" y1="{first_y}" x2="{SPINE_X}" y2="{last_y}" stroke="{ACCENT_DIM}" stroke-width="2" stroke-linecap="round" opacity="0.55"/>',
        # wandernder Lichtpunkt entlang des Rueckgrats
        f'  <circle class="comet" cx="{SPINE_X}" cy="{first_y}" r="3.5" fill="#FFD9A0"/>',
    ]

    for kind, data, y in rows:
        if kind == "head":
            body.append(
                f'  <text class="s" x="44" y="{y-14}" font-size="11.5" font-weight="700" '
                f'fill="{DIM}" letter-spacing="1.6">{escape(data)}</text>'
            )
            continue
        when, title, desc, milestone = data
        if milestone:
            body.append(
                f'  <circle class="ring" cx="{SPINE_X}" cy="{y}" r="12" fill="none" stroke="{ACCENT}" stroke-width="1.2" opacity="0.30"/>'
            )
        r = 6.5 if milestone else 4.5
        fill = ACCENT if milestone else BG
        stroke = ACCENT if milestone else "#4A5560"
        body.append(f'  <circle cx="{SPINE_X}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        body.append(f'  <text class="m" x="{YEAR_X}" y="{y-3}" font-size="12" fill="{ACCENT if milestone else DIM}">{escape(when)}</text>')
        body.append(f'  <text class="s" x="{TEXT_X}" y="{y-3}" font-size="15.5" font-weight="700" fill="{TEXT}">{escape(title)}</text>')
        body.append(f'  <text class="s" x="{TEXT_X}" y="{y+17}" font-size="13" fill="{MUTED}">{escape(desc)}</text>')

    travel = last_y - first_y
    css = f"""
    .comet {{ animation: travel 7s cubic-bezier(.5,0,.5,1) infinite; }}
    @keyframes travel {{
      0%   {{ transform: translateY(0);            opacity: 0 }}
      6%   {{ opacity: 1 }}
      88%  {{ opacity: 1 }}
      100% {{ transform: translateY({travel}px);   opacity: 0 }}
    }}
"""
    return card(1200, height, "", css, "\n".join(body),
                "Entwicklungsweg von Bastian Scherzinger, 2016 bis 2026")


# ============================================================= SKILLS =========
# (Skill, Level 0-100, Einstufung, Beleg) — Level aus gemessener Nutzung abgeleitet
SKILLS = [
    ("Python",           92, "sicher",         "170.668 Zeilen über 15 Projekte · async, OOP, Packaging"),
    ("Web-Scraping",     82, "fortgeschritten", "Playwright, Selenium, Scrapling, curl_cffi, cloudscraper"),
    ("Django",           80, "fortgeschritten", "9 produktive Seiten · ORM, Templates, Middleware, eigenes i18n"),
    ("Deployment",       78, "fortgeschritten", "Railway, Gunicorn, Whitenoise, Docker · 8 Seiten live"),
    ("REST-APIs",        74, "solide",          "FastAPI-Backend · Anthropic-, Supabase-, Discord-Integration"),
    ("SEO / GEO",        72, "solide",          "Schema.org-@graph, llms.txt, Local-SEO · Google Ads betreut"),
    ("HTML / CSS",       68, "solide",          "Eigenes Token-System, responsive, Lighthouse-A11y 100"),
    ("Testing",          62, "im Aufbau",       "2.324 Testfunktionen — aber stark ungleich verteilt"),
    ("Datenbanken",      58, "im Aufbau",       "PostgreSQL, SQLite, Supabase inkl. RLS · wenig Query-Tuning"),
    ("Docker",           48, "Grundlagen",      "Dockerfiles in 5 Projekten · noch kein Compose-Stack"),
    ("Kotlin / Android", 42, "Grundlagen",      "13.174 Zeilen Jetpack Compose in einem Projekt"),
    ("JavaScript",       38, "Grundlagen",      "Vanilla-JS, Scroll-Animationen · kein Framework"),
    ("CI/CD",            30, "Grundlagen",      "GitHub Actions bisher nur in einem Projekt"),
]

LEVEL_COLORS = {
    "sicher": "#E8A33D", "fortgeschritten": "#D2933A",
    "solide": "#B07E36", "im Aufbau": "#7E6033", "Grundlagen": "#55492F",
}


def skills():
    pad, row_h, top = 44, 42, 112
    bar_x, bar_w = 236, 300
    height = top + len(SKILLS) * row_h + 30

    defs = f"""
    <linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="90" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
      <animateTransform attributeName="gradientTransform" type="translate"
                        values="{bar_x-110} 0; {bar_x+bar_w+40} 0; {bar_x+bar_w+40} 0"
                        dur="5s" repeatCount="indefinite"/>
    </linearGradient>"""

    body = [
        f'  <text class="s" x="{pad}" y="52" font-size="12" fill="{DIM}" letter-spacing="1.4">FÄHIGKEITEN</text>',
        f'  <text class="s" x="{pad}" y="80" font-size="13.5" fill="{MUTED}">Einstufung aus gemessener Nutzung abgeleitet — jede Zeile nennt ihren Beleg.</text>',
    ]

    for i, (name, lvl, grade, ev) in enumerate(SKILLS):
        y = top + i * row_h
        col = LEVEL_COLORS[grade]
        w = round(bar_w * lvl / 100)
        body.append(f'  <text class="s" x="{pad}" y="{y+5}" font-size="14" font-weight="600" fill="{TEXT}">{escape(name)}</text>')
        body.append(f'  <rect x="{bar_x}" y="{y-8}" width="{bar_w}" height="9" rx="4.5" fill="#1B2027"/>')
        body.append(f'  <rect x="{bar_x}" y="{y-8}" width="{w}" height="9" rx="4.5" fill="{col}"/>')
        # Lichtreflex nur innerhalb des gefuellten Balkens
        body.append(f'  <clipPath id="c{i}"><rect x="{bar_x}" y="{y-8}" width="{w}" height="9" rx="4.5"/></clipPath>')
        body.append(f'  <rect clip-path="url(#c{i})" x="{bar_x}" y="{y-8}" width="{bar_w}" height="9" fill="url(#sheen)"/>')
        body.append(f'  <text class="m" x="{bar_x+bar_w+18}" y="{y+4}" font-size="11.5" fill="{DIM}">{escape(grade)}</text>')
        body.append(f'  <text class="s" x="{bar_x+bar_w+134}" y="{y+4}" font-size="12.5" fill="{MUTED}">{escape(ev)}</text>')

    return card(1200, height, defs, "", "\n".join(body), "Fähigkeiten mit Belegen")


# ========================================================== REICHWEITE =======
# Zahlen vom Kanalinhaber angegeben (Stand August 2026).
STATS = [
    ("1.800+", "FOLLOWER", "von null aufgebaut"),
    ("11.269", "LIKES", "über alle Videos"),
    ("126.000", "AUFRUFE", "bestes Video"),
    ("100.000", "AUFRUFE", "zweitbestes Video"),
]


def reichweite():
    w, h = 1200, 250
    pad = 44
    defs = """
    <radialGradient id="rglow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#E8A33D" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="#E8A33D" stop-opacity="0"/>
    </radialGradient>"""
    css = """
    .puls { animation: p 4s ease-in-out infinite; transform-origin: 1030px 125px; }
    @keyframes p { 0%,100% { transform: scale(1); opacity:.85 } 50% { transform: scale(1.08); opacity:1 } }
    @media (prefers-reduced-motion: reduce) { .puls { animation: none } }
"""
    body = [
        f'  <clipPath id="rc"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14"/></clipPath>',
        f'  <g clip-path="url(#rc)"><circle class="puls" cx="1030" cy="125" r="200" fill="url(#rglow)"/></g>',
        f'  <text class="s" x="{pad}" y="46" font-size="12" fill="{DIM}" letter-spacing="1.4">REICHWEITE</text>',
        f'  <text class="m" x="{pad}" y="78" font-size="20" font-weight="600" fill="{ACCENT}">@python_tutorials_de</text>',
        f'  <text class="s" x="{pad}" y="104" font-size="13.5" fill="{MUTED}">Python-Tutorials und Projektbeispiele auf TikTok — mehrere Kunden kamen über diesen Kanal.</text>',
        f'  <line x1="{pad}" y1="128" x2="{w-pad}" y2="128" stroke="{HAIR}" stroke-width="1"/>',
    ]
    spalte = (w - 2 * pad) // len(STATS)
    for i, (zahl, label, note) in enumerate(STATS):
        x = pad + i * spalte
        body.append(f'  <text class="m" x="{x}" y="185" font-size="34" font-weight="700" fill="{TEXT}" letter-spacing="-1">{escape(zahl)}</text>')
        body.append(f'  <text class="s" x="{x}" y="207" font-size="11.5" fill="{ACCENT}" letter-spacing="0.9">{escape(label)}</text>')
        body.append(f'  <text class="s" x="{x}" y="227" font-size="12" fill="{DIM}">{escape(note)}</text>')
    return card(w, h, defs, css, "\n".join(body), "Reichweite auf TikTok")


if __name__ == "__main__":
    (OUT / "journey.svg").write_text(journey(), encoding="utf-8")
    (OUT / "skills.svg").write_text(skills(), encoding="utf-8")
    (OUT / "reichweite.svg").write_text(reichweite(), encoding="utf-8")
    for f in ("journey.svg", "skills.svg", "reichweite.svg"):
        print(f"{f}: {(OUT / f).stat().st_size} Bytes")
