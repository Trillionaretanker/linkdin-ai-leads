from playwright.sync_api import sync_playwright

print("Script started")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.linkedin.com/login")
    print("👉 Please log in manually in the browser.")

    input("👉 After logging in and reaching the FEED, press ENTER here...")

    # Now you're logged in — automation can start
    page.goto("https://www.linkedin.com/feed/")
    print("✅ Logged in successfully. Ready for next steps.")

    input("Press ENTER to close browser")
    browser.close()

print("Script finished")
