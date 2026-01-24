from pathlib import Path
from playwright.sync_api import sync_playwright
import csv
import time

# =========================
# PATH CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

INPUT_CSV = PROJECT_ROOT / "leads.csv"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_CSV = DATA_DIR / "enriched_leads.csv"
SESSION_FILE = PROJECT_ROOT / "linkedin_session.json"

DATA_DIR.mkdir(exist_ok=True)

# =========================
# HELPERS
# =========================
def safe_text(page, selector):
    try:
        loc = page.locator(selector)
        if loc.count() > 0:
            return loc.first.inner_text().strip()
    except:
        pass
    return "N/A"


def wait_for_manual_login(page):
    print("👉 Login manually. When LinkedIn FEED is visible, press ENTER here.")
    input()


# =========================
# MAIN
# =========================
print("BATCH ENRICHER STARTED")

if not INPUT_CSV.exists():
    print(f"❌ Input file not found: {INPUT_CSV}")
    print("Run lead search first.")
    exit(1)

# -------- Load profiles --------
profiles = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        profiles.append(row["profile_url"])

print(f"Loaded {len(profiles)} profiles")

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    # -------- Session handling --------
    if SESSION_FILE.exists():
        print("✅ Using saved LinkedIn session")
        context = browser.new_context(storage_state=str(SESSION_FILE))
    else:
        print("⚠️ No session found — manual login required")
        context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

    wait_for_manual_login(page)

    # Save session after successful login
    context.storage_state(path=str(SESSION_FILE))
    print("💾 LinkedIn session saved")

    # -------- Process profiles --------
    for idx, url in enumerate(profiles, start=1):
        print(f"\n[{idx}/{len(profiles)}] Opening profile")

        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)

            # Gentle scroll to trigger lazy content
            page.mouse.wheel(0, 2500)
            time.sleep(2)

            name = safe_text(page, "h1")
            headline = safe_text(page, "div.text-body-medium")

            results.append({
                "name": name,
                "headline": headline,
                "profile_url": url
            })

            print(f"✓ Done: {name}")

        except Exception as e:
            print("⚠️ Skipped due to error")
            results.append({
                "name": "N/A",
                "headline": "N/A",
                "profile_url": url
            })

        finally:
            page.close()
            time.sleep(2)  # safety delay

    # -------- Write output --------
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
