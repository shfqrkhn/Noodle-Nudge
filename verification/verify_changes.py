from playwright.sync_api import sync_playwright
import time

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure fresh content
        context = browser.new_context(service_workers="block")
        page = context.new_page()

        # Navigate to the app
        page.goto("http://localhost:8125/docs/index.html")

        # 1. Verify Version in Footer
        footer = page.wait_for_selector("footer small")
        version_text = footer.inner_text()
        print(f"Footer Version Text: {version_text}")

        if "v1.2.22" not in version_text:
            print("FAILURE: Version v1.2.22 not found in footer.")
        else:
            print("SUCCESS: Version v1.2.22 found.")

        # 2. Verify Loader Color
        # Force show loader
        page.evaluate("NoodleNudge.UI.showLoader()")
        time.sleep(0.5) # Wait for render

        # Screenshot the loader
        page.screenshot(path="verification/loader_and_version.png")
        print("Screenshot saved to verification/loader_and_version.png")

        # Get computed style of the loader top border
        loader_color = page.evaluate("""() => {
            const loader = document.querySelector('.loader');
            return window.getComputedStyle(loader).borderTopColor;
        }""")

        print(f"Loader Border Top Color: {loader_color}")

        # #2563EB in RGB is rgb(37, 99, 235)
        if loader_color == "rgb(37, 99, 235)":
            print("SUCCESS: Loader color matches #2563EB.")
        else:
            print(f"FAILURE: Loader color mismatch. Expected rgb(37, 99, 235), got {loader_color}")

        browser.close()

if __name__ == "__main__":
    verify_changes()
