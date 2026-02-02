import asyncio
import datetime
import random
import time
from playwright.async_api import async_playwright

# Configuration
SIMULATION_DAYS = 730  # 24 months
ASSESSMENT_INTERVAL = 7  # Take an assessment every 7 days
EXPORT_INTERVAL = 30  # Export data every 30 days
START_DATE = datetime.date(2024, 1, 1)

async def run_simulation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Block SW to ensure we test app logic directly
        context = await browser.new_context(service_workers="block")
        page = await context.new_page()

        print(f"Starting 24-month simulation from {START_DATE}...")

        # Initial Load
        await page.goto("http://localhost:8000/docs/index.html")
        await page.wait_for_selector("#loader-overlay", state="hidden")

        current_date = START_DATE

        try:
            for day in range(SIMULATION_DAYS):
                # 1. Simulate Day Change (Set system time logic in app)
                # The app uses `new Date()` in `NoodleNudge.State.get().viewDate` (default)
                # or `viewDate` in state.
                # We need to update `viewDate` in state to simulate "Today".
                date_str = current_date.isoformat()

                # Mock the Date object? Or just set state.viewDate?
                # The app's `DashboardView` uses `new Date()` to determine "isToday" for the Next button.
                # But it uses `viewDate` from state to render content.
                # To simulate "Time Passing", we should update the `viewDate`.

                success = await page.evaluate("""(date) => {
                    NoodleNudge.State.set({ viewDate: date });
                    NoodleNudge.App.navigate('dashboard');
                    const headers = Array.from(document.querySelectorAll('.card-header'));
                    return headers.some(h => h.textContent.includes('Quote for Today'));
                }""", date_str)

                # Check for errors (Dashboard should load)
                if not success:
                    print(f"FAILURE Day {day}: Dashboard failed to render.")
                    return False

                # 2. Weekly Assessment
                if day % ASSESSMENT_INTERVAL == 0:
                    # Use the debug tool to fill random data (fastest way to simulate usage)
                    # "fill-random" fills ALL assessments. That's heavy but good for stress test.
                    await page.evaluate("NoodleNudge.SettingsManager.fillWithRandomData()")
                    # Verify we ended up on Assessments page
                    if not await page.is_visible(".assessment-list-header"):
                        print(f"FAILURE Day {day}: Failed to navigate to assessments after fill.")
                        return False

                # 3. Monthly Export (Check for crashes during JSON generation)
                if day % EXPORT_INTERVAL == 0:
                    # We can't easily click the download button in headless without handling the download event
                    # But we can call the function and catch errors
                    try:
                        await page.evaluate("NoodleNudge.SettingsManager.exportData()")
                        # Wait for toast
                        await page.wait_for_selector(".toast-body:has-text('exported successfully')", timeout=2000)
                    except Exception as e:
                        print(f"FAILURE Day {day}: Export failed - {e}")
                        return False

                if day % 100 == 0:
                    print(f"Day {day}/{SIMULATION_DAYS} completed. (Date: {current_date})")
                    # Check memory usage or DB size?
                    # DB size check
                    db_count = await page.evaluate("""async () => {
                        const state = await NoodleNudge.DB.get('appState');
                        const results = state.userResults ? Object.keys(state.userResults).length : 0;
                        const answers = state.userAnswers ? Object.keys(state.userAnswers).length : 0;
                        return results + answers;
                    }""")
                    print(f"  DB Entries (Results+Answers): {db_count}")

                current_date += datetime.timedelta(days=1)

            print("Simulation Complete!")
            return True

        except Exception as e:
            print(f"CRITICAL FAILURE: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(run_simulation())
    if not success:
        exit(1)
