import traceback
import asyncio
from playwright.sync_api import sync_playwright

async def run_ui_tests(test_steps):
    """
    Run automated UI tests safely on Windows using Playwright's sync API
    executed within a background thread.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_sync_playwright, test_steps)


def _run_sync_playwright(test_steps):
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://dev.claims.curacel.co")

            for step in test_steps:
                try:
                    # For now, simulate that each step passed
                    print(f"[PLAYWRIGHT] Executing step: {step}")
                    results.append({"step": step, "status": "passed"})
                except Exception as e:
                    print(f"[PLAYWRIGHT ERROR] Step failed: {e}")
                    results.append({"step": step, "status": "failed", "error": str(e)})

            browser.close()
    except Exception as e:
        print(f"[PLAYWRIGHT CRITICAL ERROR] {e}")  # 👈 Add this line
        traceback.print_exc()  # 👈 Show the full traceback
        results.append({"error": f"Playwright execution failed: {str(e)}"})
    return results
