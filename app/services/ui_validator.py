import asyncio
import json
import sys
import subprocess
import traceback


async def run_ui_tests(test_steps):
    """
    Run automated UI tests using a separate Playwright subprocess.
    This approach isolates Playwright’s event loop (Windows-safe).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_playwright_worker, test_steps)


def _run_playwright_worker(test_steps):
    """Executes a separate Python subprocess to run Playwright safely."""
    try:
        # Ensure JSON serialization
        test_data = json.dumps(test_steps)

        result = subprocess.run(
            [sys.executable, "app/services/ui_playwright_worker.py", test_data],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print("[PLAYWRIGHT STDERR]", result.stderr)
            return [{"error": f"Playwright subprocess failed: {result.stderr.strip()}"}]

        # Parse results from subprocess stdout
        try:
            return json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            print("[PLAYWRIGHT OUTPUT PARSE ERROR]", result.stdout)
            return [{"error": "Failed to parse Playwright test results."}]

    except Exception as e:
        print("[PLAYWRIGHT CRITICAL ERROR]", e)
        traceback.print_exc()
        return [{"error": f"Playwright execution failed: {str(e)}"}]
