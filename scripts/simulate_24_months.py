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

        # Ensure NoodleNudge is available (good practice for optimization scripts)
        await page.wait_for_function("typeof window.NoodleNudge !== 'undefined'")

        try:
            # ⚡ OPTIMIZATION: Run the entire simulation loop in the browser context
            # This drastically reduces IPC overhead compared to calling evaluate() 730+ times.
            logs = await page.evaluate("""async ({ days, assessmentInterval, exportInterval, startDateStr }) => {
                const logs = [];
                const startDate = new Date(startDateStr);
                const currentDate = new Date(startDate);

                const waitForSelector = (selector, timeout = 2000) => {
                    return new Promise((resolve, reject) => {
                        if (document.querySelector(selector)) return resolve(true);
                        const observer = new MutationObserver(() => {
                            if (document.querySelector(selector)) {
                                observer.disconnect();
                                resolve(true);
                            }
                        });
                        observer.observe(document.body, { childList: true, subtree: true });
                        setTimeout(() => { observer.disconnect(); reject(new Error(`Timeout waiting for ${selector}`)); }, timeout);
                    });
                };

                for (let day = 0; day < days; day++) {
                    // 1. Day Change
                    const dateStr = currentDate.toISOString().split('T')[0];
                    NoodleNudge.State.set({ viewDate: dateStr });
                    NoodleNudge.App.navigate('dashboard');

                    // Verify Dashboard
                    const headers = Array.from(document.querySelectorAll('.card-header'));
                    const dashboardOk = headers.some(h => h.textContent.includes('Quote for Today'));
                    if (!dashboardOk) throw new Error(`Day ${day}: Dashboard failed to render (Date: ${dateStr})`);

                    // 2. Weekly Assessment
                    if (day % assessmentInterval === 0) {
                        NoodleNudge.SettingsManager.fillWithRandomData();
                        // Verify navigation (synchronous in App.navigate)
                        if (!document.querySelector(".assessment-list-header")) {
                            throw new Error(`Day ${day}: Failed to navigate to assessments after fill.`);
                        }
                    }

                    // 3. Monthly Export
                    if (day % exportInterval === 0) {
                         try {
                             const exportPromise = NoodleNudge.SettingsManager.exportData();
                             await waitForSelector(".toast-body", 2000);
                             const toast = document.querySelector(".toast-body");
                             if (!toast || !toast.textContent.includes('exported successfully')) {
                                 // Logging handled by toast presence mostly
                             }
                             // Wait for export logic to settle if needed, though toast implies done
                         } catch (e) {
                             throw new Error(`Day ${day}: Export failed - ${e.message}`);
                         }
                    }

                    // Logging
                    if (day % 100 === 0) {
                        const state = await NoodleNudge.DB.get('appState');
                        const results = state.userResults ? Object.keys(state.userResults).length : 0;
                        const answers = state.userAnswers ? Object.keys(state.userAnswers).length : 0;
                        let historyCount = 0;
                        if (state.userHistory) {
                             Object.values(state.userHistory).forEach(arr => historyCount += arr.length);
                        }
                        logs.push(`Day ${day}/${days} completed. (Date: ${dateStr})`);
                        logs.push(`  DB Entries (Results+Answers): ${results + answers}`);
                        logs.push(`  History Entries: ${historyCount}`);
                    }

                    // Increment day
                    currentDate.setDate(currentDate.getDate() + 1);
                }
                return logs;
            }""", {
                "days": SIMULATION_DAYS,
                "assessmentInterval": ASSESSMENT_INTERVAL,
                "exportInterval": EXPORT_INTERVAL,
                "startDateStr": START_DATE.isoformat()
            })

            # Print logs from browser
            for log in logs:
                print(log)

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
