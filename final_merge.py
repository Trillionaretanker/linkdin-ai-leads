from pathlib import Path
import csv

# =========================
# PATH CONFIG
# =========================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

ENRICHED_CSV = DATA_DIR / "enriched_leads.csv"
AI_MESSAGES_CSV = DATA_DIR / "ai_messages.csv"
ICP_CSV = DATA_DIR / "icp_scored_leads.csv"

OUTPUT_CSV = DATA_DIR / "final_outreach.csv"

# =========================
# LOAD DATA
# =========================

print("FINAL MERGE STARTED")

for file in [ENRICHED_CSV, AI_MESSAGES_CSV, ICP_CSV]:
    if not file.exists():
        print(f"❌ Missing required file: {file}")
        exit(1)

# ---- Load enriched leads ----
enriched = {}
with open(ENRICHED_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        enriched[row["profile_url"]] = row

# ---- Load AI messages ----
ai_messages = {}
with open(AI_MESSAGES_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ai_messages[row["profile_url"]] = row["personalized_message"]

# ---- Load ICP scores ----
icp_data = {}
with open(ICP_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        icp_data[row["profile_url"]] = row

# =========================
# TONE MAPPING
# =========================

def tone_from_stars(stars):
    if stars == "⭐⭐⭐⭐⭐":
        return "Direct & confident"
    if stars == "⭐⭐⭐⭐☆":
        return "Curious & value-driven"
    if stars == "⭐⭐⭐☆☆":
        return "Exploratory"
    if stars == "⭐⭐☆☆☆":
        return "Soft networking"
    return "Passive / optional"

# =========================
# MERGE
# =========================

results = []

for url, base in enriched.items():
    message = ai_messages.get(url, "N/A")
    icp = icp_data.get(url, {})

    stars = icp.get("icp_stars", "N/A")
    confidence = icp.get("confidence_score", "N/A")
    tone = tone_from_stars(stars)

    results.append({
        "profile_url": url,
        "name": base.get("name", "N/A"),
        "headline": base.get("headline", "N/A"),
        "icp_stars": stars,
        "confidence_score": confidence,
        "message_tone": tone,
        "personalized_message": message
    })

# =========================
# WRITE OUTPUT
# =========================

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "profile_url",
            "name",
            "headline",
            "icp_stars",
            "confidence_score",
            "message_tone",
            "personalized_message"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ FINAL FILE CREATED → {OUTPUT_CSV}")
print("FINAL MERGE FINISHED")
