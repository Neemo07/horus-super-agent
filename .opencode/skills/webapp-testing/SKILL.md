---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: MIT
compatibility: opencode
metadata:
  source: anthropics/skills (skills/webapp-testing)
  edition: condensed-offline
---
# Web Application Testing

> Provenance: offline edition re-authored from the upstream `anthropics/skills` `webapp-testing` skill; `scripts/with_server.py` and `examples/` are independent implementations with the same CLI contract. Run `python scripts/sync_upstream.py --only webapp-testing` from the project root to replace this folder with the verbatim upstream skill.

To test local web applications, write native Python Playwright scripts.

**Helper scripts**
- `scripts/with_server.py` - starts one or more servers, waits for their ports, runs your command, then stops the servers (Windows and POSIX).

Always run `python scripts/with_server.py --help` first. Treat helper scripts as black boxes: call them, do not read their source into context unless a customised solution is unavoidable.

## Decision tree
```
Task -> static HTML?
  yes -> read the HTML, pick selectors, write a Playwright script (file:// URL)
         fails/incomplete -> treat as dynamic
  no  -> server already running?
         no  -> python scripts/with_server.py --help, then wrap your script with it
         yes -> reconnaissance-then-action:
                1. navigate, wait for networkidle
                2. screenshot or inspect the DOM
                3. identify selectors from what is rendered
                4. act with those selectors
```

## Run with a managed server
```bash
# one server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py

# backend + frontend
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```
Your automation script contains only Playwright logic; servers are managed for you.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)   # always headless
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")      # CRITICAL on dynamic apps
    # ... automation logic
    browser.close()
```

## Reconnaissance-then-action
1. Inspect the rendered DOM: `page.screenshot(path="/tmp/inspect.png", full_page=True)`, `page.content()`, `page.locator("button").all()`.
2. Identify selectors from the inspection result.
3. Execute actions with those selectors.

**Pitfall:** never inspect the DOM of a dynamic app before `networkidle`. Wait first.

## Best practices
- Use `sync_playwright()` for synchronous scripts and always close the browser.
- Prefer descriptive selectors: `role=`, `text=`, `data-testid`, ids; avoid brittle CSS chains.
- Add explicit waits: `page.wait_for_selector(...)`; use `wait_for_timeout` only as a last resort.
- Capture `page.on("console", ...)` and `page.on("pageerror", ...)` during runs; a green flow with console errors is not green.
- Assert on visible outcomes (text, URL, element state), not on "no exception".

## Evidence (Horus)
Use the final command as the task's proof: `plan.py done <id> --run "python scripts/with_server.py --server \"npm run dev\" --port 5173 -- python e2e/check_login.py"`. The script must exit non-zero on any failed assertion.

## Setup (once)
```bash
pip install playwright
python -m playwright install chromium
```

## Reference files
- `examples/element_discovery.py` - list buttons, links and inputs on a page
- `examples/static_html_automation.py` - drive a local HTML file via `file://`
- `examples/console_logging.py` - capture console output and page errors during automation
