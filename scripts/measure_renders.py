import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to the dashboard
        await page.goto("http://localhost:8000/docs/")

        # Wait for the loader to disappear
        await page.wait_for_selector("#loader-overlay", state="hidden")

        # Inject MutationObserver to count clears of #app-root
        await page.evaluate("""
            window.renderCount = 0;
            const appRoot = document.getElementById('app-root');
            const observer = new MutationObserver((mutations) => {
                console.log('Mutation Callback with', mutations.length, 'mutations');
                let removalCount = 0;
                for (const m of mutations) {
                    if (m.removedNodes.length > 0) {
                        removalCount++;
                        console.log('Removal detected:', m.removedNodes.length, 'nodes');
                    }
                }
                window.renderCount += removalCount;
            });
            observer.observe(appRoot, { childList: true });
        """)

        print("Observer attached. Clicking Prev Day...")

        # Click "Prev Day"
        await page.click('button[data-action="prev-day"]')

        # Wait a bit for renders to happen
        await page.wait_for_timeout(1000)

        # Get the count
        count = await page.evaluate("window.renderCount")
        print(f"Render Count: {count}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
