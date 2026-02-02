import sys
import os
import time
import subprocess
import json
import socket
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone

def wait_for_server(port, timeout=10):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Server not ready on port {port}")
            time.sleep(0.1)

def run_verification():
    # Start the server
    server_process = subprocess.Popen([sys.executable, "-m", "http.server", "8000", "--directory", "docs"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Replaced fixed sleep with wait_for_server
    try:
        wait_for_server(8000)
    except TimeoutError:
        print("FAIL: Server failed to start.")
        return False

    try:
        with sync_playwright() as p:
            # Block service workers to prevent caching issues
            context = p.chromium.launch(headless=True).new_context(service_workers='block')
            page = context.new_page()

            print("1. Opening App...")
            page.goto("http://localhost:8000/")

            # Wait for loader to disappear
            page.wait_for_selector('#loader-overlay', state='hidden')
            page.wait_for_selector('.main-nav .nav-link.active')

            # Verify we are on Dashboard (Today)
            active_nav = page.eval_on_selector('.main-nav .nav-link.active', 'el => el.textContent')
            if "Today" not in active_nav:
                print("FAIL: Not on Today tab initially.")
                return False

            # Get viewDate from state
            view_date_state = page.evaluate("NoodleNudge.State.get().viewDate")
            print(f"Initial State viewDate: {view_date_state}")

            # Verify it matches system today
            app_date = datetime.fromisoformat(view_date_state.replace('Z', '+00:00')).date()
            sys_date = datetime.now(timezone.utc).date()

            if app_date != sys_date:
                print(f"FAIL: App date ({app_date}) does not match system date ({sys_date})")
                return False

            # Get the displayed quote
            quote_text = page.inner_text('.card-body blockquote')
            print(f"Displayed Quote: {quote_text}")

            # Calculate expected day of year
            day_of_year = app_date.timetuple().tm_yday
            print(f"Day of Year: {day_of_year}")

            # Load quotes JSON to verify
            with open('docs/JSON/Content_Quotes.json', 'r') as f:
                quotes_data = json.load(f)

            # Create O(1) lookup dictionary for efficient access
            quotes_by_day = {
                item['day']: item['quote']
                for items in quotes_data['quote_categories'].values()
                for item in items
            }

            # Find expected quote using O(1) lookup
            expected_quote = quotes_by_day.get(day_of_year)

            if not expected_quote:
                # Fallback logic in app: if not found, use modulo?
                # But for day 27 it should be found.
                print(f"WARNING: No quote found in JSON for day {day_of_year}")
            else:
                print(f"Expected Quote: {expected_quote}")
                if expected_quote not in quote_text:
                     # It might be sanitized or slightly different?
                     # NoodleNudge.Utils.sanitizeHTML puts it in textContent.
                     if quote_text.strip() != expected_quote.strip():
                         print("FAIL: Quote mismatch.")
                         return False

            # 2. Change the day
            print("2. Changing day to previous day...")
            page.click('button[data-action="prev-day"]')

            # Wait for viewDate to change instead of sleeping
            try:
                page.wait_for_function("initial => NoodleNudge.State.get().viewDate !== initial", arg=view_date_state, timeout=5000)
            except Exception:
                print("FAIL: Timeout waiting for viewDate change.")
                return False

            new_view_date = page.evaluate("NoodleNudge.State.get().viewDate")
            print(f"Modified State viewDate: {new_view_date}")

            if new_view_date == view_date_state:
                print("FAIL: Date did not change.")
                return False


            # 3. Reload the page
            print("3. Reloading page...")
            page.reload()
            page.wait_for_selector('#loader-overlay', state='hidden')

            # 4. Verify it reset to Today
            reloaded_view_date = page.evaluate("NoodleNudge.State.get().viewDate")
            print(f"Reloaded State viewDate: {reloaded_view_date}")

            reloaded_date = datetime.fromisoformat(reloaded_view_date.replace('Z', '+00:00')).date()
            if reloaded_date != sys_date:
                print(f"FAIL: App did not reset to Today. Held onto: {reloaded_view_date}")
                return False


            print("SUCCESS: App resets to Today and shows correct content.")
            return True

    finally:
        server_process.terminate()

if __name__ == "__main__":
    if run_verification():
        sys.exit(0)
    else:
        sys.exit(1)
