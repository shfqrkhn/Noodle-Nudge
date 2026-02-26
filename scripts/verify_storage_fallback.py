from playwright.sync_api import sync_playwright, expect
import sys
import time
import subprocess
import socket

def wait_for_server(port, timeout=10):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Server not ready on port {port}")
            time.sleep(0.1)

def run():
    # Start server
    server_process = subprocess.Popen([sys.executable, "-m", "http.server", "8000", "--directory", "docs"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        try:
            wait_for_server(8000)
        except TimeoutError:
            print("FAIL: Server failed to start.")
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Simulate missing IndexedDB
            page.add_init_script("delete window.indexedDB;")

            try:
                print("Navigating to http://localhost:8000/ ...")
                page.goto("http://localhost:8000/")

                # Wait for app to load (checking for main content)
                print("Waiting for dashboard content...")
                # If app crashes, this will timeout
                expect(page.locator("text=Discover Your Core Profile")).to_be_visible(timeout=5000)

                # Check for warning toast
                print("Checking for warning toast...")
                toast = page.locator(".toast:has-text('Storage unavailable')")
                expect(toast).to_be_visible(timeout=5000)

                # Take success screenshot
                page.screenshot(path="scripts/verification_success_fallback.png")
                print("SUCCESS: App loaded despite missing DB. Screenshot saved to scripts/verification_success_fallback.png")

            except Exception as e:
                print(f"FAIL: Verification failed: {e}")
                page.screenshot(path="scripts/verification_failure_fallback.png")
                sys.exit(1)
            finally:
                browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run()
