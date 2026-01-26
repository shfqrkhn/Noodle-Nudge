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

            # Wait for the app to initialize (look for a known element)
            page.wait_for_selector("#app-root")

            # Run the benchmark in the browser context
            # We will call NoodleNudge.State.get() 10,000 times
            result_ms = page.evaluate("""() => {
                // Ensure State is initialized
                if (!window.NoodleNudge || !window.NoodleNudge.State) {
                    return -1;
                }

                // Warmup
                for(let i=0; i<100; i++) {
                    NoodleNudge.State.get();
                }

                const start = performance.now();
                const iterations = 10000;
                for(let i=0; i<iterations; i++) {
                    const s = NoodleNudge.State.get();
                    // Access a property to ensure no dead code elimination (though unlikely with JIT this simple)
                    const temp = s.assessments;
                }
                const end = performance.now();
                return end - start;
            }""")

            if result_ms < 0:
                print("Error: NoodleNudge.State not found.")
                sys.exit(1)

            print(f"Benchmark Result: {result_ms:.4f} ms for 10,000 calls")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_benchmark()
