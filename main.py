from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state="linkedin_session.json"
    )
    page = context.new_page()

    page.goto("https://www.linkedin.com/login")

    print("👉 Please log in manually in the browser.")
    print("👉 After successful login, press ENTER here.")

    input()

    context.storage_state(path="linkedin_session.json")
    print("✅ Session saved successfully!")

    browser.close()
