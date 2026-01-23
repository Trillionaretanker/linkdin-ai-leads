from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.linkedin.com/login")

    print("👉 Login manually in the browser.")
    print("👉 Once LinkedIn feed loads, come back and press ENTER.")

    input()

    context.storage_state(path="linkedin_session.json")
    print("✅ Session saved as linkedin_session.json")

    browser.close()
