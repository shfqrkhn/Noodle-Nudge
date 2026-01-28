from playwright.sync_api import sync_playwright, expect
import time
import statistics

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            # FORCE DEBUG MODE via URL parameter
            print("Navigating to Settings with ?debug...")
            page.goto("http://localhost:8000/docs/?debug")

            print("Navigating to Settings View...")
            page.click("a[data-nav='settings']")

            # Wait for Debug Panel Trigger to be visible
            print("Looking for debug trigger...")
            expect(page.locator("a[href='#debug-collapse']")).to_be_visible(timeout=5000)
            page.click("a[href='#debug-collapse']")

            # Measure time to fill random data
            print("Triggering massive scoring calculation (Random Data Fill)...")
            start_time = time.time()
            page.click("button[data-debug-action='fill-random']")

            # Wait for success toast
            expect(page.locator(".toast.text-bg-success")).to_be_visible(timeout=30000)
            end_time = time.time()

            duration = end_time - start_time
            print(f"✅ Scoring Engine Stress Test Completed in {duration:.4f} seconds.")

            # Verify results exist
            page.click("a[data-nav='assessments']")
            expect(page.locator("text=✅").first).to_be_visible()
            print("✅ Verified results are persisted.")

        except Exception as e:
            print(f"Error: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
