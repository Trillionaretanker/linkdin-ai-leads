from pathlib import Path
import csv

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

AI_MESSAGES_CSV = DATA_DIR / "ai_messages.csv"
ICP_CSV = DATA_DIR / "icp_scored_leads.csv"
OUTPUT_CSV = DATA_DIR / "final_outreach.csv"

# ================= HELPERS =================
def load_existing_urls(path):
    if not path.exists():
        return set()
    urls = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.add(row["profile_url"])
    return urls

def tone_from_stars(stars):
    return {
        "⭐⭐⭐⭐⭐": "Direct & confident",
        "⭐⭐⭐⭐☆": "Curious & value-driven",
        "⭐⭐⭐☆☆": "Exploratory",
        "⭐⭐☆☆☆": "Soft networking",
        "⭐☆☆☆☆": "Passive / optional"
    }.get(stars, "Neutral")

# ================= START =================
print("FINAL MERGE STARTED")

if not AI_MESSAGES_CSV.exists() or not ICP_CSV.exists():
    print("❌ Required input files missing")
    exit(1)

# Load AI messages
ai_messages = {}
with open(AI_MESSAGES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ai_messages[row["profile_url"]] = row["personalized_message"]

# Load ICP data
icp_data = {}
with open(ICP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        icp_data[row["profile_url"]] = {
            "icp_stars": row["icp_stars"],
            "confidence_score": row["confidence_score"],
            "icp_reason": row["icp_reason"]
        }

existing_urls = load_existing_urls(OUTPUT_CSV)

new_urls = [
    url for url in ai_messages
    if url in icp_data and url not in existing_urls
]

print(f"Existing outreach rows: {len(existing_urls)}")
print(f"New rows to merge today: {len(new_urls)}")

if not new_urls:
    print("Nothing new to merge. Exiting.")
    exit(0)

results = []

for url in new_urls:
    icp = icp_data[url]
    stars = icp["icp_stars"]

    results.append({
        "profile_url": url,
        "icp_stars": stars,
        "confidence_score": icp["confidence_score"],
        "message_tone": tone_from_stars(stars),
        "personalized_message": ai_messages[url]
    })

file_exists = OUTPUT_CSV.exists()

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "profile_url",
            "icp_stars",
            "confidence_score",
            "message_tone",
            "personalized_message"
        ]
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(results)

print(f"✅ Added {len(results)} rows → {OUTPUT_CSV}")
print("FINAL MERGE FINISHED")
