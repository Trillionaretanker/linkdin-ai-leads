from pathlib import Path
import csv
import os
import json
import time
import google.generativeai as genai

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "enriched_leads.csv"
OUTPUT_CSV = DATA_DIR / "ai_classified_leads.csv"

# ================= AI CONFIG =================
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

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

def build_prompt(name, headline):
    return f"""
You are an AI system analyzing a LinkedIn profile.

Name: {name}
Headline: {headline}

Classify the person and return ONLY valid JSON with these fields:

- role_type: Decision Maker | Influencer | Individual Contributor
- seniority: Junior | Mid | Senior | Executive
- function: Tech | Business | Sales | Marketing | Operations | Other
- icp_stars: 1 to 5 (integer)
- confidence_score: 1 to 10 (integer)
- outreach_tone: Direct | Curious | Soft Networking | Passive
- reasoning: short explanation (1 sentence)

Rules:
- Use reasoning, not keyword matching
- If information is weak, lower confidence
- Be conservative, realistic, professional
- Output ONLY JSON, no extra text
"""

# ================= START =================
print("🧠 AI PROFILE CLASSIFIER STARTED")

if not INPUT_CSV.exists():
    print("❌ enriched_leads.csv not found")
    exit(1)

with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

existing_urls = load_existing_urls(OUTPUT_CSV)

new_rows = [
    row for row in rows
    if row["profile_url"] not in existing_urls
]

print(f"Total enriched profiles: {len(rows)}")
print(f"Already classified: {len(existing_urls)}")
print(f"New profiles today: {len(new_rows)}")

if not new_rows:
    print("Nothing new to classify. Exiting.")
    exit(0)

results = []

for idx, row in enumerate(new_rows, start=1):
    name = row["name"]
    headline = row["headline"]
    url = row["profile_url"]

    print(f"[{idx}/{len(new_rows)}] Classifying profile")

    prompt = build_prompt(name, headline)

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "top_p": 0.9
            }
        )

        data = json.loads(response.text)

        results.append({
            "profile_url": url,
            "role_type": data.get("role_type"),
            "seniority": data.get("seniority"),
            "function": data.get("function"),
            "icp_stars": data.get("icp_stars"),
            "confidence_score": data.get("confidence_score"),
            "outreach_tone": data.get("outreach_tone"),
            "reasoning": data.get("reasoning")
        })

    except Exception as e:
        print("⚠️ AI failed, fallback applied")

        results.append({
            "profile_url": url,
            "role_type": "Unknown",
            "seniority": "Unknown",
            "function": "Other",
            "icp_stars": 2,
            "confidence_score": 3,
            "outreach_tone": "Passive",
            "reasoning": "Insufficient profile information"
        })

    time.sleep(1.2)  # rate safety

file_exists = OUTPUT_CSV.exists()

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "profile_url",
            "role_type",
            "seniority",
            "function",
            "icp_stars",
            "confidence_score",
            "outreach_tone",
            "reasoning"
        ]
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Classified {len(results)} profiles → {OUTPUT_CSV}")
print("AI PROFILE CLASSIFIER FINISHED")
