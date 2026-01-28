from playwright.sync_api import sync_playwright, expect
import os
import json

def run():
    # Create test files
    invalid_file = "invalid_backup.json"
    valid_file = "valid_backup.json"

    with open(invalid_file, "w") as f:
        json.dump({"foo": "bar"}, f)

    with open(valid_file, "w") as f:
        json.dump({
            "assessments": {},
            "dailyContent": {},
            "userAnswers": {},
            "userResults": {},
            "appConfig": {},
            "viewDate": "2026-01-01T00:00:00.000Z",
            "debugLog": []
        }, f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to Settings...")
            page.goto("http://localhost:8000/docs/")

            # Navigate to Settings
            page.click("a[data-nav='settings']")
            expect(page.locator("h2")).to_contain_text("Settings")

            # Test Invalid Import
            print("Testing Invalid Import...")
            with page.expect_file_chooser() as fc_info:
                page.click("button[onclick=\"document.getElementById('import-file').click()\"]")
            file_chooser = fc_info.value
            file_chooser.set_files(invalid_file)

            # Expect Error Toast
            # "Import failed: Invalid backup: Missing keys."
            error_toast = page.locator(".toast.text-bg-danger .toast-body")
            expect(error_toast).to_contain_text("Invalid backup: Missing keys")
            print("✅ Verified invalid import was rejected.")

            # Close toast (optional, but good hygiene)
            page.click(".btn-close")

            # Wait for toast to disappear
            expect(error_toast).to_be_hidden()

            # Test Valid Import
            print("Testing Valid Import...")
            with page.expect_file_chooser() as fc_info:
                page.click("button[onclick=\"document.getElementById('import-file').click()\"]")
            file_chooser = fc_info.value
            file_chooser.set_files(valid_file)

            # Expect Success Toast
            # "Data imported successfully!"
            success_toast = page.locator(".toast.text-bg-success .toast-body")
            expect(success_toast).to_contain_text("Data imported successfully")
            print("✅ Verified valid import was accepted.")

            # Take screenshot
            os.makedirs("scripts", exist_ok=True)
            page.screenshot(path="scripts/verification_import_validation.png")

        except Exception as e:
            print(f"Error: {e}")
            raise e
        finally:
            browser.close()
            if os.path.exists(invalid_file): os.remove(invalid_file)
            if os.path.exists(valid_file): os.remove(valid_file)

if __name__ == "__main__":
    run()
