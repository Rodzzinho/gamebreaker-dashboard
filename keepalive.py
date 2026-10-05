"""Visits the dashboard so Streamlit does not put it to sleep, and wakes it if it already has.
Run by .github/workflows/keepalive.yml every few hours."""
import sys
from playwright.sync_api import sync_playwright

URL = "https://gamebreaker-dashboard-6kjgpfcvmitztptdw8y4pc.streamlit.app/"


def page_text(pg):
    txt = ""
    for f in pg.frames:
        try:
            txt += f.inner_text("body")
        except Exception:
            pass
    return txt


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(8000)
    if "gone to sleep" in page_text(pg):
        for f in pg.frames:
            try:
                f.get_by_role("button", name="Yes, get this app back up!").click(timeout=4000)
                print("woke the app")
                break
            except Exception:
                continue
    up = False
    for _ in range(30):
        pg.wait_for_timeout(5000)
        if "We were already there" in page_text(pg):
            up = True
            break
    print("dashboard up:", up)
    b.close()
sys.exit(0 if up else 1)
