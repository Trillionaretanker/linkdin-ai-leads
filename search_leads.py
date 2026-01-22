from playwright.sync_api import sync_playwright
import time
import csv

JOB_TITLE = "Founder"
LOCATION = "India"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("https://www.linkedin.com/login")
    input("👉 Login manually and WAIT until feed loads, then press ENTER...")

    # Wait for feed
    page.wait_for_url("**/feed/**", timeout=60000)
    print("✅ Feed detected")
    time.sleep(3)

    # Search
    search_url = (
        f"https://www.linkedin.com/search/results/people/"
        f"?keywords={JOB_TITLE}%20{LOCATION}"
    )
    page.goto(search_url, wait_until="domcontentloaded")
    print("🔍 Search page opened")
    time.sleep(5)

    profiles = set()

    for _ in range(3):
        links = page.locator("a[href*='/in/']")
        count = links.count()

        for i in range(count):
            href = links.nth(i).get_attribute("href")
            if href:
                profiles.add(href.split("?")[0])

        page.mouse.wheel(0, 4000)
        time.sleep(3)

    # Save to CSV
    with open("leads.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["profile_url"])
        for profile in profiles:
            writer.writerow([profile])

    print(f"\n✅ Saved {len(profiles)} leads to leads.csv")

    input("\nPress ENTER to close browser")
    browser.close()
