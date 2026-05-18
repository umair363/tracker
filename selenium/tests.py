"""
Roshan Safar Society Tracker — Selenium Test Suite
====================================================
Tests the live application end-to-end using headless Chrome.

Usage:
    python tests.py [APP_URL]
    python tests.py http://85.211.225.161

Requirements:
    pip install selenium==4.18.1 webdriver-manager==4.0.1
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ─── Configuration ─────────────────────────────────────────────────────────────
APP_URL      = (sys.argv[1] if len(sys.argv) > 1 else "http://85.211.225.161").rstrip("/")
ADMIN_USER   = "admin"
ADMIN_PASS   = "admin123"
WAIT_TIMEOUT = 15   # seconds to wait for elements

passed = 0
failed = 0

# ─── Reporting ─────────────────────────────────────────────────────────────────
def report(name, condition):
    global passed, failed
    symbol = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {symbol}: {name}")
    if condition:
        passed += 1
    else:
        failed += 1

def get_body_text(driver):
    """Return all visible page text in uppercase for CSS text-transform safe comparison."""
    return driver.find_element(By.TAG_NAME, "body").text.upper()

def wait_for_text(driver, text_upper, timeout=WAIT_TIMEOUT):
    """Wait until the given uppercase text appears anywhere on the page."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: text_upper in get_body_text(d)
        )
        return True
    except TimeoutException:
        return False

def wait_for_element(driver, by, value, timeout=WAIT_TIMEOUT):
    """Wait until an element is present and visible."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
    except TimeoutException:
        return None

# ─── Browser Setup ─────────────────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--force-device-scale-factor=1")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)

print(f"\n🧪 Running Selenium Tests — Target: {APP_URL}\n{'─' * 55}")

try:
    # ─────────────────────────────────────────────────────────────────────────
    # TEST 1: Homepage Loads
    # Verifies that the app is reachable and has the correct page title.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 1] Homepage Loads")
    driver.get(APP_URL)

    # Wait for the page to fully load (past the animated spinner)
    wait_for_text(driver, "WELCOME BACK")

    report("Page title is 'Roshan Safar'", "Roshan Safar" in driver.title)
    report("Page body has content",        len(driver.page_source) > 500)
    report("Login page is displayed",      "WELCOME BACK" in get_body_text(driver))

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Login Form Elements Visible
    # Verifies all input fields and the submit button are rendered.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 2] Login Form Elements Visible")
    username_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your username']")
    password_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your password']")
    sign_in_btn    = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Sign In')]")

    report("Username input is present",    username_input is not None)
    report("Password input is present",    password_input is not None)
    report("Sign In button is present",    sign_in_btn is not None)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 3: Invalid Login Rejected
    # Submitting wrong credentials must show an error — no dashboard access.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 3] Invalid Login Rejected")
    username_input.clear()
    username_input.send_keys("wronguser")
    password_input.clear()
    password_input.send_keys("wrongpassword")
    sign_in_btn.click()
    time.sleep(1)

    body = get_body_text(driver)
    report("Error message displayed",      "INVALID" in body)
    report("Dashboard NOT shown",          "DASHBOARD" not in body)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 4: Admin Login Succeeds — Dashboard Renders With Data
    # Verifies all four stat cards and the Fundraising Goal section appear.
    # Note: CSS `text-transform: uppercase` means innerText is UPPERCASE.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 4] Admin Login → Dashboard Renders With Data")
    username_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your username']")
    password_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your password']")
    sign_in_btn    = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Sign In')]")

    username_input.clear()
    username_input.send_keys(ADMIN_USER)
    password_input.clear()
    password_input.send_keys(ADMIN_PASS)
    sign_in_btn.click()

    # Wait explicitly for the dashboard header to appear
    dashboard_visible = wait_for_text(driver, "DASHBOARD")
    report("Dashboard page loads after login",  dashboard_visible)

    # Wait for data to arrive (API fetch → React render)
    # Stat card labels have textTransform:uppercase → Selenium innerText is UPPERCASE
    collected_visible = wait_for_text(driver, "COLLECTED", timeout=10)
    report("'Collected' stat card visible",     collected_visible)
    report("'Expenses' stat card visible",      "EXPENSES" in get_body_text(driver))
    report("'Balance' stat card visible",       "BALANCE"  in get_body_text(driver))

    # Fundraising Goal section
    fundraising_visible = wait_for_text(driver, "FUNDRAISING GOAL", timeout=10)
    report("'Fundraising Goal' section visible", fundraising_visible)
    report("Progress percentage shown",          "% REACHED" in get_body_text(driver))

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 5: Sidebar Navigation Works
    # Clicks each nav item and verifies the correct page content appears.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 5] Sidebar Navigation Works")

    # Navigate to Donations
    donations_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Donations')]")
    if donations_btn:
        donations_btn.click()
        donations_loaded = wait_for_text(driver, "METHOD")   # column header in donations table
        report("Donations page loads with table", donations_loaded)
    else:
        report("Donations nav button found", False)

    # Navigate to Expenses
    expenses_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Expenses')]")
    if expenses_btn:
        expenses_btn.click()
        expenses_loaded = wait_for_text(driver, "CATEGORY")  # column header in expenses table
        report("Expenses page loads with table", expenses_loaded)
    else:
        report("Expenses nav button found", False)

    # Navigate to Leaderboard
    leaderboard_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Leaderboard')]")
    if leaderboard_btn:
        leaderboard_btn.click()
        leaderboard_loaded = wait_for_text(driver, "PKR")    # formatted amounts visible
        report("Leaderboard page loads with data", leaderboard_loaded)
    else:
        report("Leaderboard nav button found", False)

    # Navigate back to Dashboard
    dashboard_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Dashboard')]")
    if dashboard_btn:
        dashboard_btn.click()
        back_to_dash = wait_for_text(driver, "FUNDRAISING GOAL")
        report("Can navigate back to Dashboard", back_to_dash)
    else:
        report("Dashboard nav button found", False)

finally:
    driver.quit()

# ─── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'─' * 55}")
total = passed + failed
print(f"📊 Results: {passed} passed, {failed} failed out of {total}")
if failed == 0:
    print("🎉 All tests passed!\n")
else:
    print(f"⚠️  {failed} test(s) failed.\n")

sys.exit(1 if failed > 0 else 0)
