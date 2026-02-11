import asyncio
from playwright.async_api import async_playwright
import http.server
import socketserver
import threading
import os
import sys

PORT = 8010

def run_server():
    os.chdir('.')
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"serving at port {PORT}")
        httpd.serve_forever()

async def main():
    # Start server
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Wait for server
    await asyncio.sleep(2)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Go to app with debug enabled so logs are recorded
        await page.goto(f"http://localhost:{PORT}/docs/index.html?debug")
        await page.wait_for_selector("h2") # Wait for load

        # Inject malicious assessment logic via console
        # We try to access 'this' (which is window) using unicode escape \u0074his
        # To bypass regex, we need the string in JS memory to contain the literal backslash.
        # So we inject "\\u0074his"

        # Using 4 backslashes in python string to ensure 2 appear in JS source,
        # which means 1 literal backslash in JS string value.
        malicious_expression = r"\\u0074his.hacked = true; 100"

        print(f"Testing expression: {malicious_expression}")

        result = await page.evaluate(f"""
            () => {{
                try {{
                    const assessment = {{
                        id: 'evil',
                        sections: [],
                        scoringRubric: {{ primaryScores: [], derivativeInsights: [] }}
                    }};
                    const answers = {{}};
                    const scores = new Map();

                    // We need to inject a rule with the malicious calculation.
                    assessment.scoringRubric.primaryScores.push({{
                        id: 'evil_score',
                        title: 'Evil',
                        calculation: "{malicious_expression}"
                    }});

                    const res = NoodleNudge.Scoring.calculateResults(assessment, answers);
                    return res;
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            }}
        """)

        # Check if window.hacked is true
        is_hacked = await page.evaluate("() => window.hacked")
        print(f"Is hacked: {is_hacked}")

        # Check debug log for "Security Violation"
        debug_log = await page.evaluate("NoodleNudge.State.get().debugLog || []")
        has_security_violation = False
        for log in debug_log:
            print(f"Log: {log.get('message', '')}")
            if "Security Violation" in log.get('message', ''):
                has_security_violation = True
                break

        print(f"Has Security Violation in log: {has_security_violation}")

        await browser.close()

        if is_hacked:
            print("FAILURE: Vulnerability exploited!")
            sys.exit(1)
        elif has_security_violation:
            print("SUCCESS: Security Violation caught by new regex.")
            sys.exit(0)
        else:
            print("WARNING: Vulnerability prevented, but NOT by new regex (likely ReferenceError). Fix verification failed.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
