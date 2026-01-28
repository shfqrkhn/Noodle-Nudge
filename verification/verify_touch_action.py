from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to avoid stale cache
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            page.goto("http://localhost:8000/docs/")

            # Wait for content
            expect(page.locator("text=Discover Your Core Profile")).to_be_visible(timeout=10000)

            # Check computed style on a link
            nav_link = page.locator("a[data-nav='assessments']")
            touch_action = nav_link.evaluate("element => window.getComputedStyle(element).touchAction")
            print(f"Computed touch-action for nav link: {touch_action}")
            assert touch_action == "manipulation", f"Expected 'manipulation', got '{touch_action}'"

            # Check computed style on a button
            btn = page.locator("button[data-nav='assessments']")
            touch_action_btn = btn.evaluate("element => window.getComputedStyle(element).touchAction")
            print(f"Computed touch-action for button: {touch_action_btn}")
            assert touch_action_btn == "manipulation", f"Expected 'manipulation', got '{touch_action_btn}'"

            # Screenshot
            screenshot_path = "verification/verification_touch.png"
            page.screenshot(path=screenshot_path)
            print(f"Verification successful! Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="verification/verification_error_touch.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
