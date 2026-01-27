import asyncio
from playwright.async_api import async_playwright
import sys

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Block Service Workers to ensure we aren't hitting a stale cache
        context = await browser.new_context(service_workers="block")
        page = await context.new_page()

        try:
            # Navigate to the app (served locally on 8000)
            await page.goto("http://localhost:8000/docs/index.html")
            await page.wait_for_selector("#loader-overlay", state="hidden")

            # Inject Malicious State
            # We add a fake assessment "xss_test" with a malicious instruction
            await page.evaluate("""() => {
                const maliciousAssessment = {
                    id: "xss_test",
                    title: "XSS Test Assessment",
                    instructions: "General Instructions",
                    interactionType: "cardSort",
                    sections: [
                        {
                            id: "sec1",
                            title: "Malicious Section",
                            instructions: '<img src=x onerror="window.xss_triggered=true">',
                            items: [],
                            categories: []
                        }
                    ]
                };

                const currentState = NoodleNudge.State.get();
                const newAssessments = { ...currentState.assessments, xss_test: maliciousAssessment };
                NoodleNudge.State.set({ assessments: newAssessments });
            }""")

            print("Injected malicious assessment.")

            # Navigate to the malicious assessment
            # We trigger the navigation manually via App.navigate
            await page.evaluate("NoodleNudge.App.navigate('assessment', { id: 'xss_test' })")
            print("Navigated to assessment.")

            # Wait a moment for rendering and potential XSS execution
            await page.wait_for_timeout(1000)

            # Check if XSS triggered
            is_triggered = await page.evaluate("window.xss_triggered === true")

            if is_triggered:
                print("FAILURE: XSS Triggered! The instruction was interpreted as HTML.")
                sys.exit(1)
            else:
                # Double check that the text is actually there (escaped)
                content = await page.content()
                if '&lt;img src=x' in content or '&lt;img src="x"' in content:
                    print("SUCCESS: XSS Prevented. Payload rendered as escaped text.")
                    sys.exit(0)
                elif '<img src=x' in content:
                     # This case shouldn't happen if is_triggered is False unless the image failed to load but script didn't run?
                     # Or maybe the onerror hasn't fired yet.
                     # But for this test, if we see raw HTML tags, it's a fail.
                     print("FAILURE: Raw HTML tag found in source (even if script didn't trigger yet).")
                     sys.exit(1)
                else:
                    # Maybe the view didn't render correctly?
                    print("WARNING: Payload not found in DOM at all. Did the view render?")
                    sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
