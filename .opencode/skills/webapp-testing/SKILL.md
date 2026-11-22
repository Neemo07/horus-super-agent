---
name: webapp-testing
description: "Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs."
license: Apache-2.0
compatibility: opencode
metadata:
  source: https://github.com/anthropics/skills
---
# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available:**
- `scripts/with_server.py` — Manages server lifecycle (supports single or multiple concurrent servers, waits for ports to become ready, and tears down cleanly on exit).

Always run scripts with `--help` first to see usage. Invoke them directly as black-box helpers rather than ingesting their source into your context window unless customization is strictly necessary.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
├─ Yes → Read HTML file directly to identify selectors
│  ├─ Success → Write Playwright script using selectors (file:// URL)
│  └─ Fails/Incomplete → Treat as dynamic (below)
└─ No (dynamic webapp) → Is the server already running?
   ├─ No → Run: python .opencode/skills/webapp-testing/scripts/with_server.py --help
   │        Then use the helper + write simplified Playwright script
   └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using `with_server.py`

Single server:
```bash
python .opencode/skills/webapp-testing/scripts/with_server.py \
  --server "npm run dev" --port 5173 -- python your_automation.py
```

Multiple servers (e.g., backend + frontend):
```bash
python .opencode/skills/webapp-testing/scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

Automation script template (servers are already running and ready):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: console_errors.append(str(err)))

    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")  # CRITICAL: Wait for JS/data hydration
    page.screenshot(path="/tmp/inspect.png", full_page=True)

    # ... assertions and interactions ...
    assert not console_errors, f"Console errors: {console_errors}"
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM first:**
   ```python
   page.screenshot(path="/tmp/inspect.png", full_page=True)
   content = page.content()
   buttons = page.locator("button").all()
   ```
2. **Identify real selectors** from the rendered state (`role=`, `text=`, `data-testid`, CSS selectors, or IDs).
3. **Execute actions** and assert visible outcomes, network responses, and zero console/page errors.

## Common Pitfalls & Best Practices

- ❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps.
- ✅ **Do** wait for `page.wait_for_load_state("networkidle")` (or explicit `page.wait_for_selector(...)`).
- ✅ Use `sync_playwright()` for clean synchronous scripts and always close the browser.
- ✅ Capture both `console` errors and `pageerror` exceptions as part of verification evidence for `plan.py done <id> --run "..."`.
- ✅ Pair with `frontend-design` (visual screenshot critique) and `speed-engineer` (check Slow 4G skeletons, image payloads, and query count in Network events).
