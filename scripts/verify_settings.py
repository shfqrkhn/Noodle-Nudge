from playwright.sync_api import sync_playwright, expect
import sys
import time
import os
import subprocess
import socket
import json

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

def create_corrupt_import_file():
    corrupt_data = {
        "assessments": {},
        "dailyContent": {},
        "userAnswers": "THIS_SHOULD_BE_AN_OBJECT",
        "userResults": {},
        "appConfig": { "version": "1.2.12" },
        "userHistory": {}
    }
    file_path = os.path.abspath("scripts/corrupt_import.json")
    with open(file_path, 'w') as f:
        json.dump(corrupt_data, f)
    return file_path

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

                # 1. Verify Settings Navigation Item is Visible
                print("Checking Settings navigation...")
                settings_nav = page.locator('a[data-nav="settings"]')
                expect(settings_nav).to_be_visible()

                # Click it
                settings_nav.click()

                # 2. Verify View Header
                print("Verifying Settings View Header...")
                header = page.locator("h2")
                expect(header).to_contain_text("Settings")
                expect(header).to_contain_text("⚙️")

                # 3. Verify Data Management Panel
                print("Verifying Data Management Panel...")
                panel_header = page.locator(".card-header >> text=Data Management")
                expect(panel_header).to_be_visible()

                # 4. Verify Buttons exist
                print("Verifying Buttons...")
                export_btn = page.get_by_role("button", name="Export My Data")
                expect(export_btn).to_be_visible()

                import_btn = page.get_by_role("button", name="Import My Data")
                expect(import_btn).to_be_visible()

                reset_btn = page.get_by_role("button", name="Reset All Data")
                expect(reset_btn).to_be_visible()

                # 5. Verify Export Functionality (Proves SettingsManager is wired)
                print("Verifying Export Functionality...")
                with page.expect_download() as download_info:
                    export_btn.click()
                download = download_info.value
                print(f"Download started: {download.suggested_filename}")

                # 6. Verify Corruption Resistance (Sentinel Test)
                print("Verifying Import Validation (Corruption Test)...")
                corrupt_file_path = create_corrupt_import_file()

                # Upload directly to hidden input
                page.set_input_files("#import-file", corrupt_file_path)

                # Wait a moment for processing
                time.sleep(2)

                # Check for error toast or verify state is unchanged
                # We expect either an error toast or at least NOT a reload that persists corruption
                # If reload happens, we check state after reload.

                # Check userAnswers type in state
                user_answers_type = page.evaluate("typeof NoodleNudge.State.get().userAnswers")
                user_answers_value = page.evaluate("NoodleNudge.State.get().userAnswers")

                print(f"Post-import userAnswers type: {user_answers_type}")

                if user_answers_type != 'object' or user_answers_value == "THIS_SHOULD_BE_AN_OBJECT":
                    print("FAILURE: State was corrupted by import!")
                    raise Exception("State Corruption Detected")
                else:
                    print("SUCCESS: State resisted corruption.")

                # 7. Verify Reset Functionality
                print("Verifying Reset Functionality...")
                page.on("dialog", lambda dialog: dialog.accept())
                reset_btn.click()

                # Check for success toast
                expect(page.get_by_text("All data has been reset")).to_be_visible()
                print("Reset toast appeared.")

                screenshot_path = "scripts/verification_settings_success.png"
                page.screenshot(path=screenshot_path)
                print(f"Verification Successful! Screenshot saved to {screenshot_path}")

            except Exception as e:
                print(f"Verification Failed: {e}")
                page.screenshot(path="scripts/verification_settings_failure.png")
                sys.exit(1)
            finally:
                if os.path.exists("scripts/corrupt_import.json"):
                    os.remove("scripts/corrupt_import.json")
                browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run()
