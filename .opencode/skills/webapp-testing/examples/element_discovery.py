"""Discover buttons, links and inputs on a rendered page.
Run: python examples/element_discovery.py http://localhost:5173
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_load_state("networkidle")  # CRITICAL for dynamic apps

    for label, selector in (("buttons", "button"), ("links", "a[href]"), ("inputs", "input, textarea, select")):
        items = page.locator(selector).all()
        print(f"\n{label} ({len(items)}):")
        for el in items:
            text = (el.inner_text() or el.get_attribute("aria-label") or el.get_attribute("name") or "").strip()
            print(f"  - {text[:60]!r}  visible={el.is_visible()}")

    page.screenshot(path="/tmp/element_discovery.png", full_page=True)
    browser.close()
