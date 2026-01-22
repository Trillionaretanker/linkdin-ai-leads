from playwright.sync_api import sync_playwright

print("SCRIPT STARTED")

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://google.com")
    print("Google opened")
    input("Press ENTER to close browser")
    browser.close()

print("SCRIPT ENDED")
