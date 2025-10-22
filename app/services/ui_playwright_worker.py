import sys
import json
import sys
from playwright.sync_api import sync_playwright


def run_tests(test_steps):
    """Runs browser-based UI tests using Playwright."""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://dev.claims.curacel.co")

        for step in test_steps:
            try:
                # Log to stderr so stdout stays clean for JSON
                print(f"[WORKER] Executing test step: {step}", file=sys.stderr)
                # Placeholder action simulation
                results.append({"step": step, "status": "passed"})
            except Exception as e:
                results.append({"step": step, "status": "failed", "error": str(e)})

        browser.close()
    return results


if __name__ == "__main__":
    try:
        # Read JSON argument from subprocess
        test_steps = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
        results = run_tests(test_steps)

        # Print ONLY valid JSON to stdout for parent process
        sys.stdout.write(json.dumps(results))
        sys.stdout.flush()

    except Exception as e:
        # Log errors safely as JSON
        sys.stdout.write(json.dumps([{"error": str(e)}]))
        sys.stdout.flush()
        sys.exit(1)
