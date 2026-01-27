from pathlib import Path
import csv

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "enriched_leads.csv"
OUTPUT_CSV = DATA_DIR / "icp_scored_leads.csv"

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

def score_authority(text):
    if not text or text == "N/A":
        return 1, "Authority unknown"
    t = text.lower()
    if any(k in t for k in ["founder", "ceo", "owner", "director", "head"]):
        return 3, "Decision-maker role"
    if any(k in t for k in ["manager", "lead", "consultant"]):
        return 2, "Influencer role"
    return 1, "Individual contributor"

def score_relevance(text):
    if not text or text == "N/A":
        return 1, "Relevance unknown"
    t = text.lower()
    if any(k in t for k in ["marketing", "growth", "product", "sales", "startup"]):
        return 3, "Relevant domain"
    return 1, "Domain unclear"

def score_maturity(text):
    if not text or text == "N/A":
        return 1, "Profile maturity unknown"
    t = text.lower()
    if any(k in t for k in ["student", "intern", "fresher"]):
        return 0, "Early career"
    return 2, "Professional profile"

def score_signal(text):
    if not text or text == "N/A":
        return 1, "Low information signal"
    return 3, "Clear profile signal"

def to_stars(score):
    if score >= 10:
        return "⭐⭐⭐⭐⭐"
    if score >= 8:
        return "⭐⭐⭐⭐☆"
    if score >= 6:
        return "⭐⭐⭐☆☆"
    if score >= 4:
        return "⭐⭐☆☆☆"
    return "⭐☆☆☆☆"

# ================= START =================
print("ICP STAR RATING STARTED")

if not INPUT_CSV.exists():
    print("❌ enriched_leads.csv not found")
    exit(1)

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    enriched_rows = list(csv.DictReader(f))

existing_urls = load_existing_urls(OUTPUT_CSV)

new_rows = [
    row for row in enriched_rows
    if row["profile_url"] not in existing_urls
]

print(f"Total enriched leads: {len(enriched_rows)}")
print(f"Already scored: {len(existing_urls)}")
print(f"New leads to score today: {len(new_rows)}")

if not new_rows:
    print("Nothing new to score. Exiting.")
    exit(0)

results = []

for idx, row in enumerate(new_rows, start=1):
    headline = row["headline"]
    url = row["profile_url"]

    a, ar = score_authority(headline)
    r, rr = score_relevance(headline)
    m, mr = score_maturity(headline)
    s, sr = score_signal(headline)

    total = a + r + m + s
    stars = to_stars(total)

    reason = f"{ar} | {rr} | {mr} | {sr}"

    print(f"[{idx}] {stars} ({total}/12)")

    results.append({
        "profile_url": url,
        "icp_stars": stars,
        "confidence_score": total,
        "icp_reason": reason
    })

file_exists = OUTPUT_CSV.exists()

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "profile_url",
            "icp_stars",
            "confidence_score",
            "icp_reason"
        ]
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Added {len(results)} ICP scores → {OUTPUT_CSV}")
print("ICP STAR RATING FINISHED")
