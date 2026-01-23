from playwright.sync_api import sync_playwright
import time

print("SCRIPT STARTED")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    # ---------- LOGIN ----------
    login_page = context.new_page()
    login_page.goto("https://www.linkedin.com/login")

    input("Login manually, wait for FEED, then press ENTER")

    login_page.wait_for_url("**/feed/**", timeout=60000)
    print("FEED detected")

    # Allow background redirects to finish
    time.sleep(5)

    # ---------- PROFILE TAB ----------
    profile_page = context.new_page()
    profile_url = "https://www.linkedin.com/in/ranjita-singh-dealing-in-online-sap-training-86306362/"
    print("Opening profile...")

    profile_page.goto(profile_url, wait_until="domcontentloaded")
    time.sleep(6)

    # Force render
    profile_page.mouse.wheel(0, 2500)
    time.sleep(3)

    # NON-BLOCKING extraction
    name = ""
    try:
        elements = profile_page.locator("h1")
        if elements.count() > 0:
            name = elements.first.inner_text().strip()
    except:
        pass

    if name:
        print("NAME:", name)
    else:
        print("NAME NOT FOUND (this is acceptable)")

    input("Press ENTER to close")
    browser.close()

print("SCRIPT ENDED")
