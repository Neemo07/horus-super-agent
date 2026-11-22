"""Drive a local static HTML file through a file:// URL.
Run: python examples/static_html_automation.py path/to/index.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

html = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html").resolve()
if not html.exists():
    sys.exit(f"not found: {html}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(html.as_uri())
    page.wait_for_load_state("domcontentloaded")
    print("title:", page.title())
    page.screenshot(path="/tmp/static_page.png", full_page=True)
    browser.close()
