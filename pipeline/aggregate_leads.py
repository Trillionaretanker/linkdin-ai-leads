from pathlib import Path
import csv
from datetime import datetime

# ================= PATHS =================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

LEAD_SOURCES_DIR = PROJECT_ROOT / "lead_sources"
DATA_DIR = PROJECT_ROOT / "data"

MASTER_CSV = DATA_DIR / "leads_master.csv"

DATA_DIR.mkdir(exist_ok=True)
LEAD_SOURCES_DIR.mkdir(exist_ok=True)

# ================= HELPERS =================

def normalize_url(url: str) -> str:
    """
    Normalize LinkedIn profile URLs so duplicates can be detected.
    """
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    url = url.split("?")[0]
    if not url.endswith("/"):
        url += "/"
    return url


def load_existing_leads():
    """
    Load already-known leads from leads_master.csv
    """
    leads = {}
    if not MASTER_CSV.exists():
        return leads

    with open(MASTER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads[row["profile_url"]] = row
    return leads


# ================= START =================

print("LEAD AGGREGATOR STARTED")

existing_leads = load_existing_leads()
print(f"Existing leads: {len(existing_leads)}")

new_leads_count = 0
today = datetime.utcnow().strftime("%Y-%m-%d")

aggregated = dict(existing_leads)

# ================= READ ALL SOURCES =================

for source_file in LEAD_SOURCES_DIR.glob("*.csv"):
    source_name = source_file.stem
    print(f"Reading source: {source_file.name}")

    with open(source_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_url = row.get("profile_url", "").strip()
            if not raw_url:
                continue

            profile_url = normalize_url(raw_url)

            if profile_url in aggregated:
                continue

            aggregated[profile_url] = {
                "profile_url": profile_url,
                "source": source_name,
                "discovered_on": today,
                "status": "new"
            }

            new_leads_count += 1

# ================= WRITE MASTER FILE =================

with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "profile_url",
            "source",
            "discovered_on",
            "status"
        ]
    )
    writer.writeheader()
    writer.writerows(aggregated.values())

print(f"New leads added today: {new_leads_count}")
print(f"Total leads in master file: {len(aggregated)}")
print(f"Master file saved → {MASTER_CSV}")
print("LEAD AGGREGATOR FINISHED")
