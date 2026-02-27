from playwright.sync_api import sync_playwright
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8124

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, QuietHandler)
    httpd.serve_forever()

def run():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print(f"Navigating to http://localhost:{PORT}/docs/index.html")
            page.goto(f"http://localhost:{PORT}/docs/index.html")

            # Wait for content to confirm app is running
            page.wait_for_selector(".navbar-brand", timeout=10000)

            # Wait explicitly for the version span to be populated
            # The app populates #app-version in init()
            print("Waiting for #app-version...")
            version_span = page.wait_for_selector("#app-version", timeout=10000)

            # Use evaluate to get text content directly to avoid visibility issues or DOM lag
            version_text = page.evaluate("document.getElementById('app-version').textContent")
            print(f"Found version: {version_text}")

            if "1.2.22" in version_text:
                print("SUCCESS: Version v1.2.22 found in UI.")
                sys.exit(0)
            else:
                print(f"FAILURE: Version mismatch. Found: {version_text}")
                sys.exit(1)

        except Exception as e:
            print(f"Error during verification: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
