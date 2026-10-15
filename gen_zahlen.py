"""Erzeugt assets/zahlen.svg: Kennzahlen 2026 mit Commits je Monat.

Quelle: Git-Historie von 38 eigenen Repos (Kopien und Arbeitsbaeume entfernt),
gemessen am 15.10.2026. Stil wie gen_assets.py; jedes Element ist ohne
Animation vollstaendig sichtbar.
"""
from pathlib import Path

OUT = Path(__file__).parent / "assets" / "zahlen.svg"
BG, BORDER = "#0D1117", "#30363D"
TEXT, MUTED, DIM = "#E6EDF3", "#8B949E", "#6E7681"
ACCENT, ACCENT_DIM, HAIR = "#E8A33D", "#8A6524", "#21262D"
SANS = 'ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", "Cascadia Code", Consolas, "Liberation Mono", monospace'

KPIS = [("6.273", "Commits seit Mai"), ("38", "eigene Repos"), ("11.871", "Testfunktionen"), ("7", "Seiten live betreut")]
MONTHS = [("Mai", 462), ("Jun", 362), ("Jul", 315), ("Aug", 213), ("Sep", 3882), ("Okt*", 1039)]

W, H = 900, 330
parts = []
for i, (num, label) in enumerate(KPIS):
    x = 40 + i * 120
    parts.append(f'<text x="40" y="{62 + i * 62}" class="s" font-size="34" font-weight="800" fill="{ACCENT if i % 2 == 0 else TEXT}">{num}</text>')
    parts.append(f'<text x="40" y="{82 + i * 62}" class="m" font-size="12" fill="{MUTED}">{label}</text>')
cx, cy, cw, ch = 330, 40, 530, 230
mx = max(v for _, v in MONTHS)
bw = cw / len(MONTHS)
for v in (1000, 2000, 3000, 4000):
    y = cy + ch - ch * v / 4000
    parts.append(f'<line x1="{cx}" x2="{cx + cw}" y1="{y:.1f}" y2="{y:.1f}" stroke="{HAIR}"/>')
    parts.append(f'<text x="{cx - 8}" y="{y + 4:.1f}" text-anchor="end" class="m" font-size="11" fill="{DIM}">{v:,}</text>'.replace(",", "."))
for i, (m, v) in enumerate(MONTHS):
    h = ch * v / 4000
    x = cx + i * bw + bw * .18
    col = ACCENT if v == mx else ACCENT_DIM
    parts.append(f'<rect x="{x:.1f}" y="{cy + ch - h:.1f}" width="{bw * .64:.1f}" height="{h:.1f}" rx="4" fill="{col}"><animate attributeName="opacity" values="1;.75;1" dur="4s" begin="{i * .3}s" repeatCount="indefinite"/></rect>')
    parts.append(f'<text x="{x + bw * .32:.1f}" y="{cy + ch - h - 8:.1f}" text-anchor="middle" class="m" font-size="12" fill="{TEXT}">{v:,}</text>'.replace(",", "."))
    parts.append(f'<text x="{x + bw * .32:.1f}" y="{cy + ch + 20:.1f}" text-anchor="middle" class="m" font-size="12" fill="{MUTED}">{m}</text>')
parts.append(f'<text x="{cx}" y="{H - 18}" class="m" font-size="11" fill="{DIM}">Commits je Monat 2026 · Sep = Gründung + KI-Agententeams · *Okt bis 15.10.</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Kennzahlen 2026: 6.273 Commits seit Mai, 38 Repos, 11.871 Tests, 7 betreute Seiten; Commits je Monat mit Spitze im September">
  <title>Kennzahlen 2026</title>
  <style>.s{{font-family:{SANS}}} .m{{font-family:{MONO}}} @media (prefers-reduced-motion: reduce){{animate{{display:none}}}}</style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
  <line x1="290" x2="290" y1="30" y2="{H - 30}" stroke="{HAIR}"/>
  {chr(10).join(parts)}
</svg>
"""
OUT.write_text(svg, encoding="utf-8")
print("geschrieben", OUT)
