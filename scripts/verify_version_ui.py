from playwright.sync_api import sync_playwright, expect
import sys
import time
import os
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
            # Block service workers to ensure we test the fresh code
            context = browser.new_context(service_workers='block')
            page = context.new_page()

            try:
                print("Navigating to http://localhost:8000/ ...")
                page.goto("http://localhost:8000/")
                page.wait_for_selector("#app-root")

                # Wait for content to load using the robust locator
                print("Waiting for initial content...")
                expect(page.locator("text=Discover Your Core Profile")).to_be_visible(timeout=10000)

                # Check footer for version
                version_locator = page.locator("footer small")
                print("Checking footer version...")
                expect(version_locator).to_contain_text("Noodle Nudge v1.2.19")

                # Screenshot
                screenshot_path = "scripts/verification_version.png"
                page.screenshot(path=screenshot_path)
                print(f"Verification successful! Screenshot saved to {screenshot_path}")

            except Exception as e:
                print(f"Error during verification: {e}")
                page.screenshot(path="scripts/verification_error_version.png")
                sys.exit(1)
            finally:
                browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run()
