from pathlib import Path
import csv
import os
import time
import random
import google.generativeai as genai

# ================= CONFIG =================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

INPUT_CSV = PROJECT_ROOT / "enrich" / "enriched_leads.csv"
OUTPUT_CSV = BASE_DIR / "ai_messages.csv"

# Debug check (safe to remove later)
print("INPUT_CSV:", INPUT_CSV)
print("EXISTS:", INPUT_CSV.exists())

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= VARIATION CONTROLS =================

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

# ================= PROMPT BUILDER =================

def build_prompt(name, headline, style, pattern):
    base_rules = (
        "Write a LinkedIn connection message. "
        "Do not sell anything. "
        "Do not mention sales, tools, automation, or AI. "
        "Sound like a real human. "
        "Maximum 2 sentences. "
        "Do NOT use common phrases like "
        "'came across your profile' or 'would love to connect'."
    )

    identity = f"Address the person as {name}. " if name != "N/A" else ""
    role_ref = f"Lightly reference their work or role: {headline}. " if headline != "N/A" else ""

    return (
        f"{base_rules} "
        f"{identity}"
        f"{role_ref}"
        f"Tone: {style}. "
        f"Pattern: {pattern}."
    )

# ================= MAIN =================

print("AI MESSAGE GENERATOR STARTED")

rows = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} leads")

results = []

for idx, row in enumerate(rows, start=1):
    name = row["name"]
    headline = row["headline"]
    url = row["profile_url"]

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

print(f"\nSaved {len(results)} messages to {OUTPUT_CSV}")
print("AI MESSAGE GENERATOR FINISHED")
