import time
from playwright.sync_api import Page, TimeoutError

class SelfHealingDriver:
    """
    A wrapper around Playwright that automatically attempts fallback locators 
    if the primary UI selector fails (e.g., due to UI changes).
    """
    def __init__(self, page: Page):
        self.page = page
        self.healing_logs = []  # Stores data about fixed locators to show on the Dashboard later

    def _find_working_selector(self, primary_selector: str, fallbacks: list[str]) -> str:
        """
        Attempts to find the element. If the primary fails, loops through fallbacks.
        """
        # Step 1: Try the primary selector with a short timeout (2 seconds)
        try:
            self.page.wait_for_selector(primary_selector, timeout=2000, state="attached")
            return primary_selector
        except TimeoutError:
            print(f"⚠️ [WARNING] Primary selector '{primary_selector}' failed. Triggering Self-Healing...")

        # Step 2: Fallback Heuristics (Semantic & DOM searching)
        for fallback in fallbacks:
            try:
                self.page.wait_for_selector(fallback, timeout=2000, state="attached")
                print(f"✅ [HEALED] Found element using fallback: '{fallback}'")
                
                # Log this healing event so we can track UI fragility later
                self.healing_logs.append({
                    "failed_selector": primary_selector,
                    "healed_selector": fallback,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                return fallback
            except TimeoutError:
                continue # Try the next fallback
        
        # Step 3: If everything fails, raise a critical error
        raise Exception(f"❌ [CRITICAL] Self-healing failed for '{primary_selector}'. Element truly missing.")

    def click(self, primary_selector: str, fallbacks: list[str] = None):
        """Self-healing click action"""
        if not fallbacks: fallbacks = []
        valid_selector = self._find_working_selector(primary_selector, fallbacks)
        self.page.locator(valid_selector).click()
        print(f"🖱️ Clicked on: {valid_selector}")

    def fill(self, primary_selector: str, text: str, fallbacks: list[str] = None):
        """Self-healing typing/fill action"""
        if not fallbacks: fallbacks = []
        valid_selector = self._find_working_selector(primary_selector, fallbacks)
        self.page.locator(valid_selector).fill(text)
        print(f"⌨️ Typed '{text}' into: {valid_selector}")


# Local Test Execution for Module 2
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    print("🚀 Starting Self-Healing Engine Test...")
    
    with sync_playwright() as p:
        # Launch browser in visible mode
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Go to a sample test website
        page.goto("https://practicetestautomation.com/practice-test-login/")
        
        # Initialize our AI Smart Driver
        driver = SelfHealingDriver(page)

        try:
            # 1. Fill Username
            driver.fill(primary_selector="input#username", text="student", fallbacks=["input[name='username']", "text='Username'"])
            
            # 2. Fill Password
            driver.fill(primary_selector="input#password", text="Password123", fallbacks=["input[name='password']"])
            
            # 3. Click Submit using a DELIBERATELY BROKEN primary selector to test healing!
            # The real ID is 'submit', but we will put 'submit-broken' to force a failure.
            print("\n--- Testing Healing Capability ---")
            driver.click(
                primary_selector="button#submit-broken", 
                fallbacks=["button#submit", "text='Submit'"]
            )
            
            # Wait a few seconds to see the result
            page.wait_for_timeout(3000)
            
            print("\n📊 Healing Logs Recorded:")
            print(driver.healing_logs)

        except Exception as e:
            print(str(e))
        finally:
            browser.close()

#I completed the module to test this run the "python modules/self_healing.py"
