from playwright.sync_api import sync_playwright, expect
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to Assessment...")
            page.goto("http://localhost:8000/docs/")

            # Navigate to an assessment
            page.get_by_role("link", name="Assessments").click()
            page.get_by_role("button", name="Start Assessment").first.click()

            expect(page.locator("h2")).to_be_visible()
            print("Assessment loaded.")

            # Verify Buttons
            back_btn = page.get_by_role("button", name="Back to Assessments")
            # Note: The text is "Back to Assessments" (from L10N 'backToList').
            # The emoji ⬅️ is inside a span.
            # Locator 'name' usually matches text content.
            # L10N 'backToList' is "Back to Assessments" (checked in memory/code).

            expect(back_btn).to_be_visible()
            print("Back button visible.")

            submit_btn = page.get_by_role("button", name="Submit Answers")
            expect(submit_btn).to_be_visible()
            print("Submit button visible.")

            # Test Back Button Functionality
            back_btn.click()
            expect(page.locator("h2 >> text=Assessments")).to_be_visible()
            print("Back button navigation verified.")

            screenshot_path = "scripts/verification_buttons_success.png"
            page.screenshot(path=screenshot_path)
            print(f"Verification Successful! Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Verification Failed: {e}")
            page.screenshot(path="scripts/verification_buttons_failure.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
