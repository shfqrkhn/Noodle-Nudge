import sys
import asyncio
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

PORT = 8081

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

async def wait_for_server(port, timeout=10):
    """Waits for the server to be ready by attempting to connect to the port."""
    start_time = time.time()
    while True:
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', port)
            writer.close()
            await writer.wait_closed()
            return
        except (ConnectionRefusedError, OSError):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Server failed to start on port {port} within {timeout} seconds.")
            await asyncio.sleep(0.05)

async def main():
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    await wait_for_server(PORT)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        # Create context with blocked service workers (per memory instructions to avoid caching issues)
        context = await browser.new_context(service_workers="block")
        page = await context.new_page()

        try:
            print(f"Navigating to http://localhost:{PORT}/docs/index.html")
            await page.goto(f"http://localhost:{PORT}/docs/index.html")

            # Wait for loader to disappear (App initialized)
            try:
                await page.wait_for_selector("#loader-overlay", state="hidden", timeout=10000)
            except Exception:
                print("Timeout waiting for loader to hide.")

            # Wait for content to load in memory
            # The app calls loadAllContent -> State.set -> subscriber updates UI (and logs)
            print("Waiting for content to populate in State...")
            await page.wait_for_function("() => NoodleNudge.State.get().assessments && Object.keys(NoodleNudge.State.get().assessments).length > 0", timeout=10000)

            # Check Memory
            assessments_in_memory = await page.evaluate("Object.keys(NoodleNudge.State.get().assessments || {}).length")
            print(f"Assessments in Memory: {assessments_in_memory}")

            # Check IDB
            # Since we are in a fresh context, IDB started empty.
            # The app should have attempted to persist the state when content loaded.
            print("Checking IndexedDB state...")
            assessments_in_db = await page.evaluate("""async () => {
                const state = await NoodleNudge.DB.get('appState');
                if (!state) return -1; // No state at all?
                return state.assessments ? Object.keys(state.assessments).length : 0;
            }""")
            print(f"Assessments in DB: {assessments_in_db}")

            # Validation
            if assessments_in_memory > 0:
                if assessments_in_db == 0:
                    print("SUCCESS: Optimization verified! Static content is in memory but NOT in IDB.")
                    sys.exit(0)
                elif assessments_in_db == -1:
                     print("FAILURE: IDB is empty. Persistence failed entirely?")
                     sys.exit(1)
                else:
                    print(f"FAILURE: Assessments found in DB ({assessments_in_db}). Optimization NOT applied.")
                    sys.exit(1)
            else:
                print("FAILURE: Assessments never loaded in memory.")
                sys.exit(1)

        except Exception as e:
            print(f"Error executing verification: {e}")
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
