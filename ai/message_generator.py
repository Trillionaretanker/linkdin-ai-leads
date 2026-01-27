from pathlib import Path
import csv
import os
import time
import random
import google.generativeai as genai

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "enriched_leads.csv"
OUTPUT_CSV = DATA_DIR / "ai_messages.csv"

# ================= API =================
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= VARIATION =================
OPENING_STYLES = [
    "casual professional",
    "friendly and conversational",
    "curious and thoughtful",
    "straightforward and polite",
    "warm and respectful"
]

MESSAGE_PATTERNS = [
    "light professional intro",
    "short networking hello",
    "curiosity-driven opener",
    "simple connection request",
    "natural relationship opener"
]

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

def build_prompt(name, headline, style, pattern):
    base = (
        "Write a LinkedIn connection message. "
        "No selling. No tools. No automation. "
        "Sound human. Max 2 sentences. "
        "Avoid phrases like 'came across your profile'. "
    )

    n = f"Address them as {name}. " if name != "N/A" else ""
    h = f"Lightly reference their role: {headline}. " if headline != "N/A" else ""

    return f"{base}{n}{h}Tone: {style}. Pattern: {pattern}."

# ================= START =================
print("AI MESSAGE GENERATOR STARTED")

if not INPUT_CSV.exists():
    print("❌ enriched_leads.csv not found")
    exit(1)

# Load enriched leads
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    enriched_rows = list(csv.DictReader(f))

print(f"Total enriched leads: {len(enriched_rows)}")

# Load already messaged profiles
processed_urls = load_existing_urls(OUTPUT_CSV)
print(f"Messages already generated: {len(processed_urls)}")

# Filter only new leads
new_leads = [
    row for row in enriched_rows
    if row["profile_url"] not in processed_urls
]

print(f"New messages to generate today: {len(new_leads)}")

if not new_leads:
    print("Nothing new to process. Exiting.")
    exit(0)

results = []

# ================= GENERATE =================
for idx, row in enumerate(new_leads, start=1):
    name = row["name"]
    headline = row["headline"]
    url = row["profile_url"]

    print(f"[{idx}/{len(new_leads)}] Generating message")

    prompt = build_prompt(
        name,
        headline,
        random.choice(OPENING_STYLES),
        random.choice(MESSAGE_PATTERNS)
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.9, "top_p": 0.9}
        )
        message = response.text.strip()
    except:
        message = "Hello, hope you're doing well. Happy to connect here."

    results.append({
        "profile_url": url,
        "personalized_message": message
    })

    time.sleep(1)

# ================= APPEND =================
file_exists = OUTPUT_CSV.exists()

with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["profile_url", "personalized_message"]
    )
    if not file_exists:
        writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Added {len(results)} new messages → {OUTPUT_CSV}")
print("AI MESSAGE GENERATOR FINISHED")
