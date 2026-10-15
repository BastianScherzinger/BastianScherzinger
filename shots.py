"""Nimmt frische Screenshots der Live-Seiten auf (1440x900, verkleinert auf 800x500)."""
from pathlib import Path
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "assets" / "sites"
SITES = {
    "ruempelwerk": "https://www.ruempelwerk-mitteldeutschland.de",
    "hg-fluegel": "https://www.hg-fluegel.de",
    "rtc-service": "https://www.rtc-service.com",
    "wvm-it": "https://www.wvm-it.tech",
    "1a-entruempelung": "https://www.1a-entruemplung.com",
    "webagentur": "https://webagentur-scherzinger.com",
    "rhein-neckar": "https://rhein-neckar-production.up.railway.app",
    "luviq": "https://www.luviq-alsfeld.com",
}

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1, locale="de-DE")
    for name, url in SITES.items():
        page = ctx.new_page()
        try:
            r = page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(2500)
            # Cookie-Hinweise wegklicken, falls vorhanden
            for sel in ["text=Alle akzeptieren", "text=Akzeptieren", "text=Nur notwendige", "text=Verstanden"]:
                try:
                    page.locator(sel).first.click(timeout=800)
                    page.wait_for_timeout(600)
                    break
                except Exception:
                    pass
            png = page.screenshot()
            Image.open(BytesIO(png)).convert("RGB").resize((800, 500), Image.LANCZOS).save(OUT / f"{name}.jpg", quality=82, optimize=True)
            print(name, r.status if r else "-", "ok")
        except Exception as e:
            print(name, "FEHLER", str(e)[:120])
        page.close()
    b.close()
