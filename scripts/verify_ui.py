
from playwright.sync_api import sync_playwright
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:8080/")

            # Wait for content
            page.wait_for_selector("#loader-overlay", state="hidden", timeout=15000)
            page.wait_for_selector("blockquote", state="visible")

            # Check for specific failure elements
            # The fallback is <p class="text-muted">No quote available for this day.</p>
            # We want to ensure this is NOT visible.

            fallback = page.locator("p.text-muted", has_text="No quote available for this day.")
            if fallback.is_visible():
                print("FAILURE: Fallback text is visible.")
                sys.exit(1)

            print("SUCCESS: Quote rendered.")
            page.screenshot(path="verification.png")

        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
