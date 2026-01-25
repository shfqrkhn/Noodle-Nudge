from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure fresh code
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            page.goto("http://localhost:8000/docs/")

            # Use the robust locator from verify_scoring.py
            page.wait_for_selector("text=Discover Your Core Profile")

            print("Attempting to tamper with MasterBlueprint...")

            # Attempt 1: Modify Feature Flag
            # We want to see if we CAN modify it. If we can, it returns true (tamperable).
            is_tamperable_flag = page.evaluate("""() => {
                try {
                    const original = MasterBlueprint.featureFlags.enableDebugPanel;
                    MasterBlueprint.featureFlags.enableDebugPanel = !original;
                    // Check if it changed
                    return MasterBlueprint.featureFlags.enableDebugPanel !== original;
                } catch (e) {
                    return false;
                }
            }""")

            # Attempt 2: Modify Version
            is_tamperable_version = page.evaluate("""() => {
                try {
                    MasterBlueprint.version = "9.9.9";
                    return MasterBlueprint.version === "9.9.9";
                } catch (e) {
                    return false;
                }
            }""")

            print(f"Feature Flag Tamperable: {is_tamperable_flag}")
            print(f"Version Tamperable: {is_tamperable_version}")

            if is_tamperable_flag or is_tamperable_version:
                print("FAIL: MasterBlueprint is mutable.")
            else:
                print("PASS: MasterBlueprint is immutable.")

        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
