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

            page.wait_for_selector("text=Discover Your Core Profile")

            print("Checking MasterBlueprint availability...")

            result = page.evaluate("""() => {
                try {
                    return {
                        exists: typeof MasterBlueprint !== 'undefined',
                        value: typeof MasterBlueprint !== 'undefined' ? MasterBlueprint : null
                    };
                } catch (e) {
                    return { error: e.toString() };
                }
            }""")

            print(f"Result: {result}")

        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
