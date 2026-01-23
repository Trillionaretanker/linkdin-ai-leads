from playwright.sync_api import sync_playwright
import csv
import time

INPUT_CSV = "../leads.csv"
OUTPUT_CSV = "enriched_leads.csv"

def safe_text(page, selector):
    try:
        el = page.locator(selector)
        if el.count() > 0:
            return el.first.inner_text().strip()
    except:
        pass
    return ""

print("BATCH ENRICHER STARTED")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    # -------- LOGIN --------
    login_page = context.new_page()
    login_page.goto("https://www.linkedin.com/login")
    input("Login manually, wait for FEED, then press ENTER")

    login_page.wait_for_url("**/feed/**", timeout=60000)
    print("FEED detected")
    time.sleep(5)

    # -------- READ INPUT --------
    profiles = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profiles.append(row["profile_url"])

    print(f"Loaded {len(profiles)} profiles")

    results = []

    # -------- PROCESS EACH PROFILE --------
    for idx, url in enumerate(profiles, start=1):
        print(f"\n[{idx}/{len(profiles)}] Opening profile")

        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(6)

            page.mouse.wheel(0, 2500)
            time.sleep(3)

            name = safe_text(page, "h1")
            headline = safe_text(page, "div.text-body-medium")

            if not name:
                name = "N/A"
            if not headline:
                headline = "N/A"

            results.append({
                "name": name,
                "headline": headline,
                "profile_url": url
            })

            print(f"✓ Done: {name}")

        except Exception as e:
            print("Skipped (error)")
            results.append({
                "name": "ERROR",
                "headline": "ERROR",
                "profile_url": url
            })

        finally:
            page.close()
            time.sleep(3)  # safety delay

    # -------- WRITE OUTPUT --------
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "headline", "profile_url"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} rows to {OUTPUT_CSV}")
    input("Press ENTER to close browser")
    browser.close()

print("BATCH ENRICHER FINISHED")
