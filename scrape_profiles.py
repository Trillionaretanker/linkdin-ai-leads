from playwright.sync_api import sync_playwright, TimeoutError
import csv
import time

PROFILE_URLS = [
    "https://www.linkedin.com/in/ranjita-singh-dealing-in-online-sap-training-86306362/",
    "https://www.linkedin.com/in/surajsingh0912/",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("https://www.linkedin.com/login")
    input("👉 Login manually and WAIT until feed loads, then press ENTER...")

    page.wait_for_url("**/feed/**", timeout=60000)
    print("✅ Feed detected")
    time.sleep(3)

    results = []

    for url in PROFILE_URLS:
        print(f"\n🔍 Opening profile: {url}")

        try:
            print("⏳ Loading profile page...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            print("⏳ Waiting for profile header...")
            page.wait_for_selector("h1", timeout=15000)

            print("✅ Profile loaded, extracting data...")
            time.sleep(2)
        except TimeoutError:
            print("⚠️ Profile took too long, skipping")
            continue

        # Force render
        page.mouse.wheel(0, 2000)
        time.sleep(2)

        # NAME
        try:
            name = page.locator("h1").first.inner_text().strip()
        except:
            name = ""

        # ROLE
        try:
            role = page.locator("div.text-body-medium.break-words").first.inner_text().strip()
        except:
            role = ""

        # COMPANY (best-effort)
        company = ""
        try:
            experience_section = page.locator("section#experience-section")
            if experience_section.count() > 0:
                company = experience_section.locator("span.t-14.t-normal").first.inner_text().strip()
        except:
            company = ""

        # Fallback
        if not name and not role:
            name = "Profile loaded"

        results.append([name, role, company, url])
        print(f"✅ Scraped: {name}")

        time.sleep(3)

    # Save CSV
    with open("detailed_leads.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "role", "company", "profile_url"])
        writer.writerows(results)

    print(f"\n💾 Saved {len(results)} profiles to detailed_leads.csv")
    input("Press ENTER to close browser")
    browser.close()
