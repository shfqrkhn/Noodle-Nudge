from playwright.sync_api import sync_playwright, expect
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(service_workers='block')
        page = context.new_page()

        try:
            print("Navigating to http://localhost:8000/docs/ ...")
            page.goto("http://localhost:8000/docs/")

            # Wait for content
            expect(page.locator("h2").first).to_be_visible()

            # 1. Links (Nav)
            print("Checking Nav Links...")
            nav_link = page.locator(".nav-link.active").first
            style = nav_link.evaluate("el => window.getComputedStyle(el).touchAction")
            if style != "manipulation":
                raise Exception(f"Nav Link touch-action is '{style}', expected 'manipulation'")
            print("✅ Nav Link passed.")

            # 2. Buttons (CTA)
            print("Checking CTA Button...")
            cta_btn = page.locator("button[data-nav='assessments']")
            style = cta_btn.evaluate("el => window.getComputedStyle(el).touchAction")
            if style != "manipulation":
                raise Exception(f"CTA Button touch-action is '{style}', expected 'manipulation'")
            print("✅ CTA Button passed.")

            # Navigate to Assessments
            page.click("a[data-nav='assessments']")
            expect(page.locator("h2 >> text=Assessments")).to_be_visible()

            # 3. Card Sort Item (Core Values)
            print("Opening Core Values (Card Sort)...")
            page.click("button[data-assessment-id='core_values_v1.0.0']")
            expect(page.locator(".sortable-card").first).to_be_visible()

            print("Checking Sortable Cards...")
            card = page.locator(".sortable-card").first
            style = card.evaluate("el => window.getComputedStyle(el).touchAction")
            if style != "manipulation":
                raise Exception(f"Sortable Card touch-action is '{style}', expected 'manipulation'")
            print("✅ Sortable Card passed.")

            # Navigate back to Assessments for Likert check
            page.click("button[data-nav='assessments']")
            expect(page.locator("h2 >> text=Assessments")).to_be_visible()

            # 4. Inputs (Radio) - Core Profile
            print("Opening Core Profile (Likert)...")
            page.click("button[data-assessment-id='core_profile_v1.0.0']")
            expect(page.locator("form")).to_be_visible()

            print("Checking Radio Inputs...")
            radio = page.locator("input[type='radio']").first
            style = radio.evaluate("el => window.getComputedStyle(el).touchAction")
            if style != "manipulation":
                raise Exception(f"Radio Input touch-action is '{style}', expected 'manipulation'")
            print("✅ Radio Input passed.")

            # 5. Labels
            print("Checking Labels...")
            label = page.locator("label.btn").first
            style = label.evaluate("el => window.getComputedStyle(el).touchAction")
            if style != "manipulation":
                raise Exception(f"Label touch-action is '{style}', expected 'manipulation'")
            print("✅ Label passed.")

            print("ALL CHECKS PASSED: Mobile Physics (touch-action) is correctly applied.")

        except Exception as e:
            print(f"Verification Failed: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
