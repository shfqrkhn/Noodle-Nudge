from playwright.sync_api import sync_playwright
import time
import sys

def run_benchmark():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure we test the fresh code and avoid caching issues
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            # Navigate to the app
            page.goto("http://localhost:8000/docs/")

            # Wait for the app to initialize (wait for loader to disappear)
            page.wait_for_selector("#loader-overlay", state="hidden")

            # Inject large data
            page.evaluate("""() => {
                const largeData = {};
                for(let i=0; i<5000; i++) {
                    largeData[`item_${i}`] = {
                        id: i,
                        text: "x".repeat(200),
                        nested: { a: 1, b: [1,2,3] }
                    };
                }
                // We assume NoodleNudge.State exists
                if (window.NoodleNudge && window.NoodleNudge.State) {
                    window.NoodleNudge.State.set({ benchmarkData: largeData }, { silent: true });
                }
            }""")

            # Run the benchmark in the browser context
            # We will call NoodleNudge.State.get() 1,000 times (reduced from 10k as deep clone might be slow)
            result_ms = page.evaluate("""() => {
                // Ensure State is initialized
                if (!window.NoodleNudge || !window.NoodleNudge.State) {
                    return -1;
                }

                const start = performance.now();
                const iterations = 1000;
                for(let i=0; i<iterations; i++) {
                    const s = NoodleNudge.State.get();
                    // Access a property
                    const temp = s.benchmarkData;
                }
                const end = performance.now();
                return end - start;
            }""")

            if result_ms < 0:
                print("Error: NoodleNudge.State not found.")
                sys.exit(1)

            print(f"Benchmark Result: {result_ms:.4f} ms for 1,000 calls")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_benchmark()
