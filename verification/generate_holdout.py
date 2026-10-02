"""
Phase 5: Fresh 10-App Holdout Generator (Disjoint from the 30 Sample Apps)
Picks exactly 1 disjoint app per category (10 apps total).
Saves to verification/holdout_sample.json.
"""

import json
import csv
from pathlib import Path

def generate_holdout():
    # Load 30-app sample IDs
    with open("verification/sample.json", "r", encoding="utf-8") as f:
        sample_30 = json.load(f)
    sample_ids = {int(x["id"]) for x in sample_30}

    # Load all 100 apps
    with open("data/input/apps.csv", "r", encoding="utf-8") as f:
        all_apps = list(csv.DictReader(f))

    # Pre-select 1 disjoint app per category
    # Categories: CRM, Support, Comms, Marketing, Ecommerce, Data, Developer, Productivity, Finance, AI
    CANDIDATE_HOLDOUT_IDS = [
        2,   # HubSpot (CRM)
        11,  # Zendesk (Support)
        21,  # Slack (Comms)
        35,  # Mailchimp (Marketing)
        41,  # Shopify (Ecommerce)
        51,  # DataForSEO (Data)
        61,  # GitHub (Developer)
        73,  # Linear (Productivity)
        81,  # Stripe (Finance)
        96   # Devin (AI)
    ]

    holdout = []
    for app in all_apps:
        app_id = int(app["id"])
        if app_id in CANDIDATE_HOLDOUT_IDS:
            assert app_id not in sample_ids, f"Holdout app {app_id} is in 30-app sample!"
            holdout.append({
                "id": app_id,
                "app": app["app"],
                "category": app["category"],
                "hint": app["hint"]
            })

    assert len(holdout) == 10, f"Expected 10 holdout apps, got {len(holdout)}"
    out_path = Path("verification/holdout_sample.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(holdout, f, indent=2)

    print(f"Generated fresh disjoint 10-app holdout saved to {out_path}")
    return holdout

if __name__ == "__main__":
    generate_holdout()
