from playwright.sync_api import sync_playwright, expect
import sys
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure we test the fresh code
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            # Ensure server is running (handled by user/system, assuming port 8000)
            page.goto("http://localhost:8000/docs/")

            # 1. Verify Settings Navigation Item is Visible
            print("Checking Settings navigation...")
            settings_nav = page.locator('a[data-nav="settings"]')
            expect(settings_nav).to_be_visible()

            # Click it
            settings_nav.click()

            # 2. Verify View Header
            # We expect the header to be "Settings" (updated from "Debug Panel") and icon to be ⚙️
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

            # 5. Verify Functionality (Proves SettingsManager is wired)
            print("Verifying Export Functionality...")
            with page.expect_download() as download_info:
                export_btn.click()
            download = download_info.value
            print(f"Download started: {download.suggested_filename}")

            print("Verifying Reset Functionality...")
            # Handle confirmation dialog
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
            browser.close()

if __name__ == "__main__":
    run()
