from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to avoid caching issues
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            page.goto("http://localhost:8000/docs/")

            # Wait for content to load using the robust locator from verify_scoring.py
            print("Waiting for initial content...")
            expect(page.locator("text=Discover Your Core Profile")).to_be_visible(timeout=10000)

            # Check footer for version
            version_locator = page.locator("footer small")
            print("Checking footer version...")
            expect(version_locator).to_contain_text("Noodle Nudge v1.1.8")

            # Screenshot
            screenshot_path = "scripts/verification_version.png"
            page.screenshot(path=screenshot_path)
            print(f"Verification successful! Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="scripts/verification_error_version.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
