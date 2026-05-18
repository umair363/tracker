"""
Roshan Safar — Selenium Automated Tests
Run: pip install -r requirements.txt && python tests.py
"""
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ─── Config ────────────────────────────────────────────────────────────────────
APP_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

passed = 0
failed = 0

def report(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ PASS: {name}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {name}")
        failed += 1

# ─── Setup Chrome ──────────────────────────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    print(f"\n🧪 Running Selenium Tests against: {APP_URL}\n")

    # ─── Test 1: Homepage Loads ────────────────────────────────────────────────
    print("Test 1: Homepage Loads")
    driver.get(APP_URL)
    time.sleep(2)
    report("Page title contains 'Roshan Safar'", "Roshan Safar" in driver.title)
    report("Page has content", len(driver.page_source) > 100)

    # ─── Test 2: Login Form Visible ────────────────────────────────────────────
    print("\nTest 2: Login Form Visible")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    report("Username input exists", len(inputs) >= 1)
    report("Password input exists", len(inputs) >= 2)

    # Check for 'Welcome back' heading
    body_text = driver.find_element(By.TAG_NAME, "body").text
    report("'Welcome back' text visible", "Welcome back" in body_text)

    # ─── Test 3: Invalid Login Shows Error ─────────────────────────────────────
    print("\nTest 3: Invalid Login Shows Error")
    username_input = inputs[0]
    password_input = inputs[1]

    username_input.clear()
    username_input.send_keys("wronguser")
    password_input.clear()
    password_input.send_keys("wrongpass")

    # Find and click the Sign In button
    buttons = driver.find_elements(By.TAG_NAME, "button")
    sign_in_btn = [b for b in buttons if "Sign In" in b.text]
    if sign_in_btn:
        sign_in_btn[0].click()
        time.sleep(1)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    report("Error message shown for invalid login", "Invalid" in body_text)

    # ─── Test 4: Valid Admin Login Reaches Dashboard ───────────────────────────
    print("\nTest 4: Valid Admin Login Reaches Dashboard")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    username_input = inputs[0]
    password_input = inputs[1]

    username_input.clear()
    username_input.send_keys(ADMIN_USER)
    password_input.clear()
    password_input.send_keys(ADMIN_PASS)

    buttons = driver.find_elements(By.TAG_NAME, "button")
    sign_in_btn = [b for b in buttons if "Sign In" in b.text]
    if sign_in_btn:
        sign_in_btn[0].click()
        time.sleep(3)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    report("Dashboard text visible after login", "Dashboard" in body_text)
    report("Collected stat visible", "Collected" in body_text)
    report("Balance stat visible", "Balance" in body_text)
    report("Fundraising Goal visible", "Fundraising Goal" in body_text)

    # ─── Test 5: Navigation Works ─────────────────────────────────────────────
    print("\nTest 5: Navigation Works")
    # Click on Donations in sidebar
    buttons = driver.find_elements(By.TAG_NAME, "button")
    donations_btn = [b for b in buttons if "Donations" in b.text]
    if donations_btn:
        donations_btn[0].click()
        time.sleep(1)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    report("Donations page loads", "Donations" in body_text or "Method" in body_text)

    # Click on Leaderboard
    buttons = driver.find_elements(By.TAG_NAME, "button")
    lb_btn = [b for b in buttons if "Leaderboard" in b.text or "Ranks" in b.text]
    if lb_btn:
        lb_btn[0].click()
        time.sleep(1)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    report("Leaderboard page loads", "Leaderboard" in body_text or "collection" in body_text)

    # ─── Results ───────────────────────────────────────────────────────────────
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {passed + failed}\n")

finally:
    driver.quit()

sys.exit(1 if failed > 0 else 0)
