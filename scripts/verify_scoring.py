from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure we test the fresh code and avoid caching issues
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            page.goto("http://localhost:8000/docs/")

            # Wait for content to load
            expect(page.locator("text=Discover Your Core Profile")).to_be_visible(timeout=10000)

            # Go to Assessments
            print("Navigating to Assessments...")
            page.get_by_role("link", name="Assessments").click()
            expect(page.locator("h2 >> text=Assessments")).to_be_visible()

            # Start Assessment (Core Personality)
            print("Starting Core Personality assessment...")
            # We select the first 'Start Assessment' button which corresponds to the first assessment
            page.get_by_role("button", name="Start Assessment").first.click()

            # Title is "Your Core Profile"
            expect(page.locator("h2 >> text=Your Core Profile")).to_be_visible()

            # Fill answers
            print("Filling answers...")
            # Automatically click the first option for every question using JS
            page.evaluate("""() => {
                document.querySelectorAll('.likert-scale').forEach(group => {
                    const firstInput = group.querySelector('input');
                    if(firstInput) firstInput.click();
                });
            }""")

            # Submit
            print("Submitting answers...")
            page.get_by_role("button", name="Submit Answers").click()

            # Verify Toast
            print("Verifying success toast...")
            expect(page.locator(".toast-body >> text=Assessment completed!")).to_be_visible()

            # Verify Results Page
            print("Verifying results page...")
            expect(page.locator("text=Your Results for Your Core Profile")).to_be_visible()

            # Check for chart canvas (might take a moment to render)
            expect(page.locator("canvas")).to_be_visible()

            # Screenshot
            screenshot_path = "scripts/verification_results.png"
            page.screenshot(path=screenshot_path)
            print(f"Verification successful! Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="scripts/verification_error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
