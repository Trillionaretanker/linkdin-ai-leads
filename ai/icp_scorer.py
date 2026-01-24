from pathlib import Path
import csv

# =========================
# PATH CONFIG
# =========================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "enriched_leads.csv"
OUTPUT_CSV = DATA_DIR / "icp_scored_leads.csv"

# =========================
# GENERALIZED ICP SCORING
# =========================

def score_authority(text):
    if not text or text == "N/A":
        return 1, "Authority unknown"

    text = text.lower()
    if any(k in text for k in ["founder", "ceo", "owner", "director", "head"]):
        return 3, "Decision-maker role"
    if any(k in text for k in ["manager", "lead", "consultant"]):
        return 2, "Influencer role"
    return 1, "Individual contributor"


def score_relevance(text):
    if not text or text == "N/A":
        return 1, "Relevance unknown"

    text = text.lower()
    if any(k in text for k in ["marketing", "growth", "product", "sales", "startup"]):
        return 3, "Relevant domain"
    return 1, "Domain unclear"


def score_maturity(text):
    if not text or text == "N/A":
        return 1, "Profile maturity unknown"

    text = text.lower()
    if any(k in text for k in ["student", "intern", "fresher"]):
        return 0, "Early career"
    return 2, "Professional profile"


def score_signal_strength(text):
    if not text or text == "N/A":
        return 1, "Low information signal"
    return 3, "Clear profile signal"


def score_to_stars(score):
    if score >= 10:
        return "⭐⭐⭐⭐⭐"
    if score >= 8:
        return "⭐⭐⭐⭐☆"
    if score >= 6:
        return "⭐⭐⭐☆☆"
    if score >= 4:
        return "⭐⭐☆☆☆"
    return "⭐☆☆☆☆"

# =========================
# MAIN
# =========================

print("ICP STAR RATING STARTED")

if not INPUT_CSV.exists():
    print(f"❌ Input file not found: {INPUT_CSV}")
    exit(1)

rows = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} leads")

results = []

for idx, row in enumerate(rows, start=1):
    headline = row.get("headline", "N/A")
    url = row.get("profile_url")

    a, ar = score_authority(headline)
    r, rr = score_relevance(headline)
    m, mr = score_maturity(headline)
    s, sr = score_signal_strength(headline)

    total_score = a + r + m + s
    stars = score_to_stars(total_score)

    reason = f"{ar} | {rr} | {mr} | {sr}"

    print(f"[{idx}] {stars} ({total_score}/12)")

    results.append({
        "profile_url": url,
        "icp_stars": stars,
        "confidence_score": total_score,
        "icp_reason": reason
    })

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["profile_url", "icp_stars", "confidence_score", "icp_reason"]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ ICP scores saved → {OUTPUT_CSV}")
print("ICP STAR RATING FINISHED")
