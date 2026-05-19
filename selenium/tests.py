"""
Roshan Safar Society Tracker — Selenium Test Suite
====================================================
Tests the live application end-to-end using a VISIBLE Chrome browser.
Screenshots are saved to ./screenshots/ after each test.

Usage:
    python tests.py [APP_URL]
    python tests.py http://85.211.225.161

Requirements:
    pip install selenium==4.18.1 webdriver-manager==4.0.1
"""

import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ─── Configuration ─────────────────────────────────────────────────────────────
APP_URL      = (sys.argv[1] if len(sys.argv) > 1 else "http://85.211.225.161").rstrip("/")
ADMIN_USER   = "admin"
ADMIN_PASS   = "admin123"
WAIT_TIMEOUT = 15   # seconds to wait for elements

# ─── Screenshot Directory ───────────────────────────────────────────────────────
TIMESTAMP       = datetime.now().strftime("%Y%m%d_%H%M%S")
SCREENSHOT_DIR  = os.path.join(os.path.dirname(__file__), "screenshots", TIMESTAMP)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
print(f"📸 Screenshots will be saved to: {SCREENSHOT_DIR}")

passed = 0
failed = 0
_shot_idx = 0

# ─── Reporting ─────────────────────────────────────────────────────────────────
def screenshot(driver, label):
    """Save a screenshot with an auto-incrementing name."""
    global _shot_idx
    _shot_idx += 1
    safe_label = label.replace(" ", "_").replace("/", "-")[:60]
    filename   = f"{_shot_idx:02d}_{safe_label}.png"
    path       = os.path.join(SCREENSHOT_DIR, filename)
    try:
        driver.save_screenshot(path)
        print(f"    📷 Screenshot saved → {filename}")
    except Exception:
        print(f"    ⚠️  Could not capture screenshot: {filename} (window may be closed)")
    return path

def report(name, condition, driver=None):
    global passed, failed
    symbol = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {symbol}: {name}")
    if driver:
        screenshot(driver, f"{'PASS' if condition else 'FAIL'}_{name}")
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
    """Wait until an element is present in the DOM."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except (TimeoutException, Exception):
        return None

# ─── Browser Setup ─────────────────────────────────────────────────────────────
print("\n🔧 Setting up Chrome browser (webdriver-manager will auto-install ChromeDriver)...")

options = Options()
# ✅ VISIBLE browser — headless removed so you can watch the tests run
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--force-device-scale-factor=1")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# webdriver-manager 4.0.1 has a bug: .install() returns the NOTICES file
# instead of the actual chromedriver.exe — fix by resolving the exe manually.
_raw_path    = ChromeDriverManager().install()
_driver_dir  = os.path.dirname(_raw_path)
_chromedriver = os.path.join(_driver_dir, "chromedriver.exe")
if not os.path.isfile(_chromedriver):
    # Fallback: search subdirectories for chromedriver.exe
    for root, dirs, files in os.walk(os.path.dirname(_driver_dir)):
        for f in files:
            if f.lower() == "chromedriver.exe":
                _chromedriver = os.path.join(root, f)
                break
print(f"   ChromeDriver: {_chromedriver}")
service = Service(_chromedriver)
driver  = webdriver.Chrome(service=service, options=options)
driver.set_window_size(1440, 900)
driver.maximize_window()

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
    screenshot(driver, "Test1_homepage_loaded")

    report("Page title is 'Roshan Safar'", "Roshan Safar" in driver.title, driver)
    report("Page body has content",        len(driver.page_source) > 500,  driver)
    report("Login page is displayed",      "WELCOME BACK" in get_body_text(driver), driver)

    # ─────────────────────────────────────────────────────────────────────────
    # TEST 2: Login Form Elements Visible
    # Verifies all input fields and the submit button are rendered.
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 2] Login Form Elements Visible")
    username_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your username']")
    password_input = wait_for_element(driver, By.CSS_SELECTOR, "input[placeholder='Enter your password']")
    sign_in_btn    = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Sign In')]")

    screenshot(driver, "Test2_login_form")
    report("Username input is present",    username_input is not None, driver)
    report("Password input is present",    password_input is not None, driver)
    report("Sign In button is present",    sign_in_btn is not None,    driver)

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
    time.sleep(1.5)

    screenshot(driver, "Test3_invalid_login_attempt")
    body = get_body_text(driver)
    report("Error message displayed",      "INVALID" in body,      driver)
    report("Dashboard NOT shown",          "DASHBOARD" not in body, driver)

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

    screenshot(driver, "Test4_before_admin_login")
    sign_in_btn.click()

    # Wait explicitly for the dashboard header to appear
    dashboard_visible = wait_for_text(driver, "DASHBOARD")
    screenshot(driver, "Test4_dashboard_after_login")
    report("Dashboard page loads after login",  dashboard_visible, driver)

    # Wait for data to arrive (API fetch → React render)
    collected_visible = wait_for_text(driver, "COLLECTED", timeout=10)
    screenshot(driver, "Test4_stat_cards")
    report("'Collected' stat card visible",     collected_visible, driver)
    report("'Expenses' stat card visible",      "EXPENSES" in get_body_text(driver), driver)
    report("'Balance' stat card visible",       "BALANCE"  in get_body_text(driver), driver)

    # Fundraising Goal section
    fundraising_visible = wait_for_text(driver, "FUNDRAISING GOAL", timeout=10)
    screenshot(driver, "Test4_fundraising_goal")
    report("'Fundraising Goal' section visible", fundraising_visible, driver)
    report("Progress percentage shown",          "% REACHED" in get_body_text(driver), driver)

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
        screenshot(driver, "Test5_donations_page")
        report("Donations page loads with table", donations_loaded, driver)
    else:
        report("Donations nav button found", False, driver)

    # Navigate to Expenses
    expenses_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Expenses')]")
    if expenses_btn:
        expenses_btn.click()
        expenses_loaded = wait_for_text(driver, "CATEGORY")  # column header in expenses table
        screenshot(driver, "Test5_expenses_page")
        report("Expenses page loads with table", expenses_loaded, driver)
    else:
        report("Expenses nav button found", False, driver)

    # Navigate to Leaderboard
    leaderboard_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Leaderboard')]")
    if leaderboard_btn:
        leaderboard_btn.click()
        leaderboard_loaded = wait_for_text(driver, "PKR")    # formatted amounts visible
        screenshot(driver, "Test5_leaderboard_page")
        report("Leaderboard page loads with data", leaderboard_loaded, driver)
    else:
        report("Leaderboard nav button found", False, driver)

    # Navigate back to Dashboard
    dashboard_btn = wait_for_element(driver, By.XPATH, "//button[contains(text(),'Dashboard')]")
    if dashboard_btn:
        dashboard_btn.click()
        back_to_dash = wait_for_text(driver, "FUNDRAISING GOAL")
        screenshot(driver, "Test5_back_to_dashboard")
        report("Can navigate back to Dashboard", back_to_dash, driver)
    else:
        report("Dashboard nav button found", False, driver)

finally:
    screenshot(driver, "final_state")
    driver.quit()

# ─── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'─' * 55}")
total = passed + failed
print(f"📊 Results: {passed} passed, {failed} failed out of {total}")
print(f"📁 All screenshots saved in: {SCREENSHOT_DIR}")
if failed == 0:
    print("🎉 All tests passed!\n")
else:
    print(f"⚠️  {failed} test(s) failed.\n")

sys.exit(1 if failed > 0 else 0)
