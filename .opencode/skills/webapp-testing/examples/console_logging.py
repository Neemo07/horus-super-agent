"""Capture console output and uncaught page errors while a flow runs.
Exit code 1 if any console error or page error was seen.
Run: python examples/console_logging.py http://localhost:5173
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
problems = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda m: (print(f"[console.{m.type}] {m.text}"),
                                  problems.append(m.text) if m.type == "error" else None))
    page.on("pageerror", lambda e: (print(f"[pageerror] {e}"), problems.append(str(e))))
    page.goto(url)
    page.wait_for_load_state("networkidle")
    # ... drive the flow under test here
    browser.close()

sys.exit(1 if problems else 0)
