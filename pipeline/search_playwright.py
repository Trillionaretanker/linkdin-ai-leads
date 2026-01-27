from pathlib import Path
from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

SOURCE_DIR = PROJECT_ROOT / "lead_sources"
SOURCE_DIR.mkdir(exist_ok=True)

OUTPUT_CSV = SOURCE_DIR / "playwright.csv"
SESSION_FILE = PROJECT_ROOT / "linkedin_session.json"

SEARCH_KEYWORDS = [
    "Founder",
    "Co-Founder",
    "CEO",
    "Startup Founder"
]

MAX_PROFILES_PER_KEYWORD = 15

print("🔍 PLAYWRIGHT LEAD SEARCH STARTED")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    if SESSION_FILE.exists():
        context = browser.new_context(storage_state=str(SESSION_FILE))
        print("✅ Using saved LinkedIn session")
    else:
        context = browser.new_context()
        print("⚠️ Manual login required")

    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

    print("👉 Ensure FEED is visible, then press ENTER")
    input()

    context.storage_state(path=str(SESSION_FILE))
    print("💾 Session saved")

    collected = set()
    leads = []
    today = datetime.now().strftime("%Y-%m-%d")

    for keyword in SEARCH_KEYWORDS:
        print(f"\n🔎 Searching: {keyword}")

        search_url = (
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={keyword.replace(' ', '%20')}"
        )

        page.goto(search_url, wait_until="domcontentloaded")
        time.sleep(5)

        # Scroll to load results
        for _ in range(3):
            page.mouse.wheel(0, 3000)
            time.sleep(2)

        links = page.locator("a[href*='/in/']")

        count = links.count()
        print(f"Found {count} profile links")

        for i in range(min(count, MAX_PROFILES_PER_KEYWORD)):
            href = links.nth(i).get_attribute("href")
            if not href:
                continue

            clean_url = href.split("?")[0]

            if clean_url not in collected:
                collected.add(clean_url)
                leads.append({
                    "profile_url": clean_url,
                    "source": "playwright",
                    "added_on": today
                })

        time.sleep(3)

    browser.close()

# Write output
file_exists = OUTPUT_CSV.exists()

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=["profile_url", "source", "added_on"]
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(leads)

print(f"\n✅ Collected {len(leads)} raw leads")
print(f"Saved → {OUTPUT_CSV}")
print("PLAYWRIGHT LEAD SEARCH FINISHED")
