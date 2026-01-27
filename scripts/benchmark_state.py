from playwright.sync_api import sync_playwright
import time
import sys

def run_benchmark():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block service workers to ensure we test the fresh code
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            # Navigate to the app
            page.goto("http://localhost:8000/docs/")
            page.wait_for_selector("#loader-overlay", state="hidden")

            # Inject large data
            # 50,000 items * ~200 chars ~ 10MB
            page.evaluate("""() => {
                const largeData = {};
                for(let i=0; i<50000; i++) {
                    largeData[`item_${i}`] = {
                        id: i,
                        text: "x".repeat(200),
                        nested: { a: 1, b: [1,2,3] }
                    };
                }
                if (window.NoodleNudge && window.NoodleNudge.State) {
                    window.NoodleNudge.State.set({ benchmarkData: largeData }, { silent: true });
                }
            }""")

            # Verify data presence
            key_count = page.evaluate("""() => {
                const s = NoodleNudge.State.get();
                return s.benchmarkData ? Object.keys(s.benchmarkData).length : 0;
            }""")
            print(f"Injected items count: {key_count}")

            if key_count != 50000:
                print("Error: Data injection failed.")
                sys.exit(1)

            # Run the benchmark
            # 1,000,000 iterations of get()
            print("Running 1,000,000 iterations of State.get()...")
            result_ms = page.evaluate("""() => {
                const start = Date.now();
                const iterations = 1000000;
                let check = 0;
                for(let i=0; i<iterations; i++) {
                    const s = NoodleNudge.State.get();
                    if (s.benchmarkData) check++;
                }
                const end = Date.now();
                return end - start;
            }""")

            print(f"Benchmark Result: {result_ms} ms for 1,000,000 calls")
            print(f"Average time per call: {result_ms / 1000000:.6f} ms")

            # Threshold: Should be well under 1000ms if optimized (likely < 200ms)
            # If it was deep clone, 1 call takes ~30ms, so 1M calls would take 30,000s (8 hours)
            if result_ms < 5000:
                print("✅ Performance verification PASSED (Optimized)")
            else:
                print("❌ Performance verification FAILED (Too slow)")
                sys.exit(1)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_benchmark()
