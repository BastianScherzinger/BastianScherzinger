"""Erzeugt die Ablaufdiagramme als SVG (assets/flow-*.svg).

Ersetzt die Mermaid-Bloecke im README: GitHub zeigte bei einigen davon
„Unable to render rich display“. Eigene SVGs sehen ueberall gleich aus und
passen zum Stil von gen_assets.py. Jedes Element ist ohne Animation sichtbar;
die wandernden Punkte auf den Kanten kommen nur additiv dazu.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "assets"
BG, BORDER = "#0D1117", "#30363D"
TEXT, MUTED, DIM = "#E6EDF3", "#8B949E", "#6E7681"
ACCENT, ACCENT_DIM, HAIR, NODE = "#E8A33D", "#8A6524", "#21262D", "#161B22"
SANS = 'ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, "SF Mono", "Cascadia Code", Consolas, "Liberation Mono", monospace'

NW, NH = 176, 66  # Knotengroesse


def flow(name, title, cols, rows, nodes, edges, caption):
    """nodes: id -> (spalte, zeile, [zeilen], art); art: n | a (Akzent) | d (Datenspeicher) | q (Entscheidung)"""
    W = 1200
    pad_x, top = 40, 58
    nw = min(176, (W - 2 * pad_x - (cols - 1) * 48) / cols)
    col_w = (W - 2 * pad_x - nw) / max(cols - 1, 1)
    row_h = 104
    back_last = any(len(e) > 3 and nodes[e[0]][1] == rows - 1 for e in edges)
    H = top + rows * row_h + 52 + (44 if back_last else 0)
    pos = {k: (pad_x + c * col_w, top + r * row_h + 10) for k, (c, r, _, _) in nodes.items()}
    out = [f'<text class="m" x="{pad_x}" y="34" font-size="12" fill="{DIM}" letter-spacing="1.4">{escape(title.upper())}</text>']
    defs = [f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACCENT_DIM}"/></marker>']
    for i, e in enumerate(edges):
        a, b = e[0], e[1]
        label = e[2] if len(e) > 2 else ""
        back = len(e) > 3 and e[3] == "back"
        ax, ay = pos[a]; bx, by = pos[b]
        if back:  # Ruecksprung unter den Knoten entlang
            x1, y1 = ax + nw / 2, ay + NH
            x2, y2 = bx + nw / 2, by + NH
            d = f"M{x1:.1f},{y1:.1f} C{x1:.1f},{y1 + 60:.1f} {x2:.1f},{y2 + 60:.1f} {x2:.1f},{y2 + 4:.1f}"
            lx, ly = (x1 + x2) / 2, max(y1, y2) + 48
        elif abs(ax - bx) < 1:  # gleiche Spalte: senkrecht
            x1, y1, x2, y2 = ax + nw / 2, ay + NH, bx + nw / 2, by - 4
            if by < ay:
                y1, y2 = ay, by + NH + 4
            d = f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"
            lx, ly = x1 + 8, (y1 + y2) / 2 + 4
        else:
            x1, y1 = ax + nw, ay + NH / 2
            x2, y2 = bx - 4, by + NH / 2
            mx = (x1 + x2) / 2
            d = f"M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
            lx, ly = mx, (y1 + y2) / 2 - 7
        dash = ' stroke-dasharray="5 5"' if back else ""
        out.append(f'<path id="e{i}" d="{d}" fill="none" stroke="{ACCENT_DIM}" stroke-width="1.6"{dash} marker-end="url(#ah)"/>')
        out.append(f'<circle r="3" fill="{ACCENT}" class="dot"><animateMotion dur="{2.6 + (i % 3) * .5}s" begin="{(i * .37) % 2:.2f}s" repeatCount="indefinite"><mpath href="#e{i}"/></animateMotion></circle>')
        if label:
            anchor = "start" if (abs(ax - bx) < 1 and not back) else "middle"
            out.append(f'<text class="m" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="11" fill="{MUTED}" paint-order="stroke" stroke="{BG}" stroke-width="4">{escape(label)}</text>')
    for k, (c, r, lines, kind) in nodes.items():
        x, y = pos[k]
        stroke = ACCENT if kind in ("a", "q") else BORDER
        fill = "#1F1A10" if kind == "a" else NODE
        if kind == "d":
            out.append(f'<path d="M{x},{y + 10} a{nw / 2},10 0 0 1 {nw},0 v{NH - 20} a{nw / 2},10 0 0 1 {-nw},0 z" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
            out.append(f'<path d="M{x},{y + 10} a{nw / 2},10 0 0 0 {nw},0" fill="none" stroke="{stroke}" stroke-width="1.4"/>')
        elif kind == "q":
            out.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{NH}" rx="33" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{NH}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        n = len(lines)
        for j, ln in enumerate(lines):
            yy = y + NH / 2 + (j - (n - 1) / 2) * 17 + 5
            if j == 0:
                out.append(f'<text class="s" x="{x + nw / 2}" y="{yy:.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="{TEXT}">{escape(ln)}</text>')
            else:
                out.append(f'<text class="m" x="{x + nw / 2}" y="{yy:.1f}" text-anchor="middle" font-size="11" fill="{MUTED}">{escape(ln)}</text>')
    out.append(f'<text class="s" x="{pad_x}" y="{H - 20}" font-size="12.5" fill="{DIM}">{escape(caption)}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}: {escape(caption)}">
  <title>{escape(title)}</title>
  <defs>{''.join(defs)}</defs>
  <style>.s{{font-family:{SANS}}} .m{{font-family:{MONO}}} @media (prefers-reduced-motion: reduce){{.dot{{display:none}}}}</style>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
  {chr(10).join(out)}
</svg>
"""
    (OUT / f"flow-{name}.svg").write_text(svg, encoding="utf-8")
    print("flow", name, W, H)


FLOWS = [
    ("arbeitsweise", "So arbeite ich mit KI-Agenten", 6, 2, {
        "a": (0, 0, ["Auftrag", "per Sprache"], "n"),
        "b": (1, 0, ["Plan", "Opus · Fable"], "n"),
        "c": (2, 0, ["Agententeam", "Sonnet · parallel", "in Git-Worktrees"], "n"),
        "d": (3, 0, ["Prüfung", "Tests · Prüfcockpit"], "n"),
        "e": (4, 0, ["Abnahme", "durch mich"], "q"),
        "f": (5, 0, ["Merge + Deploy", "Railway"], "a"),
        "g": (5, 1, ["Doku", "für die nächste", "Sitzung"], "n"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f", "passt"), ("e", "c", "nachbessern", "back"), ("f", "g")],
     "Entscheidungen und Abnahme bleiben bei mir, die Agenten bauen. 10.09.–15.10.2026: 984 Agenten, über 160.000 Werkzeugaufrufe."),
    ("ruempelwerk", "Vom Suchenden zum Auftrag", 5, 3, {
        "a": (0, 1, ["Suche bei Google", "Halle · Leipzig"], "n"),
        "b": (1, 1, ["Orts- und", "Leistungsseite"], "n"),
        "c": (2, 1, ["Wie anfragen?"], "q"),
        "d": (3, 0, ["Formular", "in 2 Minuten"], "n"),
        "e": (3, 1, ["WhatsApp-Video", "Festpreis vor Ort"], "n"),
        "f": (3, 2, ["Besichtigung", "online buchen"], "n"),
        "g": (4, 1, ["Telegram + Mail", "in Echtzeit"], "a"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("c", "e"), ("c", "f"), ("d", "g"), ("e", "g"), ("f", "g")],
     "Drei Wege zur Anfrage, eine Benachrichtigung. Jede Anfrage kommt sofort an, der Kunde bekommt ein Festpreis-Angebot."),
    ("lieferungdirekt", "LieferungDirekt", 4, 3, {
        "a": (0, 1, ["Android-App", "Kotlin · Compose"], "n"),
        "f": (0, 0, ["Wirt", "pflegt Inhalte selbst"], "n"),
        "b": (1, 1, ["FastAPI", "Service-Schicht"], "a"),
        "c": (2, 0, ["PostgreSQL"], "d"),
        "d": (2, 1, ["Redis", "Rate-Limit · Cache"], "d"),
        "e": (2, 2, ["Küchen-Alarm", "Long-Polling"], "n"),
    }, [("a", "b", "REST + JWT"), ("f", "b"), ("b", "c"), ("b", "d"), ("b", "e")],
     "Bestellungen lösen im Laden einen Alarm aus, ohne Firebase. Nach der Übergabe gehört das System dem Wirt."),
    ("livingen", "livingen", 5, 1, {
        "a": (0, 0, ["Kleinanzeigen", "u. a. Quellen"], "n"),
        "b": (1, 0, ["Scraper", "Normalisierung · Dedup"], "n"),
        "c": (2, 0, ["Datenhaltung"], "d"),
        "d": (3, 0, ["Dashboard", "Flask · Live-Fortschritt"], "n"),
        "e": (4, 0, ["Discord-Bot", "je Bundesland"], "a"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("d", "b", "Suchen anlegen", "back")],
     "Mein am saubersten getestetes Projekt: 1.478 Testfunktionen, Docker und GitHub Actions."),
    ("jarvis", "JARVIS", 6, 2, {
        "a": (0, 0, ["Quellen", "Verzeichnisse · Maps"], "n"),
        "b": (1, 0, ["Scraper", "Playwright"], "n"),
        "c": (2, 0, ["Anreicherung", "Kontakt · Webseite?"], "n"),
        "d": (3, 0, ["Bewertung", "lohnt der Kontakt?"], "q"),
        "e": (4, 0, ["Angebots-Mail"], "n"),
        "f": (4, 1, ["Website-Bau", "Vorlage + Inhalte"], "n"),
        "g": (5, 1, ["Repo + Railway", "+ Domain"], "a"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("d", "f"), ("f", "g")],
     "Von der Lead-Recherche bis zur deployten Kundenseite, gesteuert über ein Flask-Dashboard mit Sprachsteuerung."),
    ("mediapipe", "MEDIAPIPE WVM", 6, 1, {
        "a": (0, 0, ["Briefing", "Ziel · Zielgruppe"], "n"),
        "b": (1, 0, ["Drehbuch", "Szene für Szene"], "n"),
        "c": (2, 0, ["Szenen", "KI-Video je Szene"], "n"),
        "d": (3, 0, ["Warteschlange", "lange Renderjobs"], "n"),
        "e": (4, 0, ["Montage", "ffmpeg · Ton"], "n"),
        "f": (5, 0, ["Ausgabe", "9:16 · 1:1 · 16:9"], "a"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "f")],
     "Ein Durchlauf statt vieler Einzelwerkzeuge. Daraus ist meine Leistung Werbevideo entstanden."),
    ("luviq", "Luviq Onlineshop", 5, 2, {
        "a": (0, 0, ["Besucher"], "n"),
        "b": (1, 0, ["Katalog", "Detailseiten"], "n"),
        "c": (2, 0, ["Warenkorb", "Session"], "n"),
        "d": (3, 0, ["Checkout", "PayPal"], "a"),
        "e": (4, 0, ["Bestätigung", "Brevo-Mail"], "n"),
        "k": (2, 1, ["Konto", "Registrierung"], "n"),
        "f": (1, 1, ["Cloudinary", "Produktbilder"], "d"),
    }, [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("k", "c"), ("f", "b")],
     "Django 5 · PostgreSQL · PayPal · Cloudinary · django-axes · Docker"),
    ("vintedbot", "VintedBot", 5, 2, {
        "a": (0, 0, ["Suchen", "je Discord-Kanal"], "n"),
        "b": (1, 0, ["Warteschlange", "asyncio"], "n"),
        "p": (1, 1, ["Proxy-Rotation"], "n"),
        "c": (2, 0, ["Abruf", "requests statt Browser"], "n"),
        "d": (3, 0, ["Schon gesehen?"], "q"),
        "g": (3, 1, ["MongoDB Atlas"], "d"),
        "e": (4, 0, ["Discord-Meldung"], "a"),
    }, [("a", "b"), ("b", "c"), ("p", "c"), ("c", "d"), ("d", "g"), ("d", "e", "neu")],
     "Vom Browser zum direkten HTML-Abruf: Speicherbedarf von 1,5 GB auf unter 200 MB."),
]

if __name__ == "__main__":
    for f in FLOWS:
        flow(*f)
