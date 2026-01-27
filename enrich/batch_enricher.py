from pathlib import Path
from playwright.sync_api import sync_playwright
import csv
import time

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

INPUT_CSV = PROJECT_ROOT / "leads.csv"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_CSV = DATA_DIR / "enriched_leads.csv"
SESSION_FILE = PROJECT_ROOT / "linkedin_session.json"

DATA_DIR.mkdir(exist_ok=True)

NAME_SELECTORS = [
    "h1",
    "header h1",
    "h1 span"
]

HEADLINE_SELECTORS = [
    "div.text-body-medium",
    "section div span",
    "div[data-generated-suggestion-target]"
]


def safe_text_multi(page, selectors):
    for selector in selectors:
        try:
            loc = page.locator(selector)
            if loc.count() > 0:
                text = loc.first.inner_text().strip()
                if text:
                    return text
        except:
            pass
    return "N/A"


print("BATCH ENRICHER STARTED")

if not INPUT_CSV.exists():
    print(f"❌ Input file not found: {INPUT_CSV}")
    exit(1)

profiles = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        profiles.append(row["profile_url"])

print(f"Loaded {len(profiles)} profiles")

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    if SESSION_FILE.exists():
        print("✅ Using saved LinkedIn session")
        context = browser.new_context(storage_state=str(SESSION_FILE))
    else:
        context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

    print("👉 Login manually. When FEED is visible, press ENTER.")
    input()

    context.storage_state(path=str(SESSION_FILE))
    print("💾 LinkedIn session saved")

    for idx, url in enumerate(profiles, start=1):
        print(f"\n[{idx}/{len(profiles)}] Opening profile")
        print(f"URL: {url}")

        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)

            page.mouse.wheel(0, 3000)
            time.sleep(2)

            name = safe_text_multi(page, NAME_SELECTORS)
            headline = safe_text_multi(page, HEADLINE_SELECTORS)

            results.append({
                "name": name,
                "headline": headline,
                "profile_url": url
            })

            print(f"✓ Done: {name}")

        except Exception as e:
            print(f"⚠️ Skipped: {e}")
            results.append({
                "name": "N/A",
                "headline": "N/A",
                "profile_url": url
            })

        finally:
            page.close()
            time.sleep(2)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "headline", "profile_url"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Saved {len(results)} rows → {OUTPUT_CSV}")
    input("Press ENTER to close browser")
    browser.close()

print("BATCH ENRICHER FINISHED")
