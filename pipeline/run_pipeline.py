import subprocess
import sys
from pathlib import Path

# Project root = parent of /pipeline
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run(script_path: str):
    full_path = PROJECT_ROOT / script_path
    print(f"\n▶ Running: {script_path}")

    result = subprocess.run(
        [sys.executable, str(full_path)],
        cwd=str(PROJECT_ROOT)
    )

    if result.returncode != 0:
        print(f"\n❌ Failed at: {script_path}")
        sys.exit(1)

print("\n🚀 LINKEDIN AI LEAD PIPELINE STARTED")

# 1) Enrichment
run("enrich/batch_enricher.py")

# 2) AI message generation
run("ai/message_generator.py")

# 3) ICP scoring (⭐)
run("ai/icp_scorer.py")

# 4) Final merge
run("final_merge.py")

print("\n✅ PIPELINE FINISHED SUCCESSFULLY")
print("📄 Final output → data/final_outreach.csv")
