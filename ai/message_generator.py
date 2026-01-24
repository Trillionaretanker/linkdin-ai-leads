from pathlib import Path
import csv
import os
import time
import random
import google.generativeai as genai

# =========================
# PATH CONFIG
# =========================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_CSV = DATA_DIR / "enriched_leads.csv"
OUTPUT_CSV = DATA_DIR / "ai_messages.csv"

# =========================
# API CONFIG
# =========================

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# VARIATION CONTROLS
# =========================

OPENING_STYLES = [
    "casual professional",
    "curious and thoughtful",
    "friendly and conversational",
    "straightforward and polite",
    "warm and respectful"
]

MESSAGE_PATTERNS = [
    "a short professional networking intro",
    "a simple hello and interest in connecting",
    "express curiosity about their background",
    "a polite reach-out without context",
    "a light and natural connection opener"
]

# =========================
# PROMPT BUILDER
# =========================

def build_prompt(name, headline, style, pattern):
    base_rules = (
        "Write a LinkedIn connection message. "
        "Do not sell anything. "
        "Do not mention sales, tools, automation, or AI. "
        "Sound like a real human. "
        "Maximum 2 sentences. "
        "Avoid generic phrases like "
        "'came across your profile' or 'would love to connect'."
    )

    identity = f"Address the person as {name}. " if name and name != "N/A" else ""
    role_ref = f"Lightly reference their work or role: {headline}. " if headline and headline != "N/A" else ""

    return (
        f"{base_rules} "
        f"{identity}"
        f"{role_ref}"
        f"Tone: {style}. "
        f"Pattern: {pattern}."
    )

# =========================
# MAIN
# =========================

print("AI MESSAGE GENERATOR STARTED")

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
    name = row.get("name", "N/A")
    headline = row.get("headline", "N/A")
    url = row.get("profile_url")

    print(f"[{idx}/{len(rows)}] Generating message")

    style = random.choice(OPENING_STYLES)
    pattern = random.choice(MESSAGE_PATTERNS)
    prompt = build_prompt(name, headline, style, pattern)

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.9,
                "top_p": 0.9
            }
        )
        message = response.text.strip()
    except Exception:
        message = "Hello, hope you're doing well. Happy to connect here."

    results.append({
        "profile_url": url,
        "personalized_message": message
    })

    time.sleep(1)  # rate safety

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["profile_url", "personalized_message"]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Saved {len(results)} messages → {OUTPUT_CSV}")
print("AI MESSAGE GENERATOR FINISHED")
