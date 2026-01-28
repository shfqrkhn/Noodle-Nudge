from playwright.sync_api import sync_playwright
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

            # Run the benchmark
            # 1,000,000 iterations of sanitizeHTML()
            print("Running 1,000,000 iterations of sanitizeHTML()...")
            result_ms = page.evaluate("""() => {
                const start = Date.now();
                const iterations = 1000000;
                const input = "<div>Test string & <script>alert(1)</script> 'quote' \\"double quote\\"</div>";
                for(let i=0; i<iterations; i++) {
                    NoodleNudge.Utils.sanitizeHTML(input);
                }
                const end = Date.now();
                return end - start;
            }""")

            print(f"Benchmark Result: {result_ms} ms for 1,000,000 calls")
            print(f"Average time per call: {result_ms / 1000000:.6f} ms")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_benchmark()
