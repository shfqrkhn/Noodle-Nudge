from playwright.sync_api import sync_playwright, expect
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to avoid caching issues during test
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            # 1. Test WITHOUT debug mode
            print("1. Testing WITHOUT debug mode...")
            page.goto("http://localhost:8000/docs/")
            page.wait_for_selector("text=Discover Your Core Profile")

            # Execute fillWithRandomData
            print("   Invoking fillWithRandomData()...")
            page.evaluate("NoodleNudge.SettingsManager.fillWithRandomData()")

            # Check userResults
            user_results = page.evaluate("NoodleNudge.State.get().userResults")
            if user_results and len(user_results) > 0:
                raise Exception("FAIL: userResults populated when debug mode is OFF!")
            print("   PASS: userResults remains empty.")

            # 2. Test WITH debug mode
            print("2. Testing WITH debug mode...")
            page.goto("http://localhost:8000/docs/?debug")
            page.wait_for_selector("text=Discover Your Core Profile")

            # Execute fillWithRandomData
            print("   Invoking fillWithRandomData()...")
            page.evaluate("NoodleNudge.SettingsManager.fillWithRandomData()")

            # Check userResults
            user_results_debug = page.evaluate("NoodleNudge.State.get().userResults")
            if not user_results_debug or len(user_results_debug) == 0:
                raise Exception("FAIL: userResults NOT populated when debug mode is ON!")
            print(f"   PASS: userResults populated with {len(user_results_debug)} items.")

            print("✅ SUCCESS: Sentinel Guard verification passed.")

        except Exception as e:
            print(f"❌ FAIL: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
