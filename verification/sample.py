"""
Phase 4: Stratified Sample Generator (Fixed Seed)
Generates verification/sample.json (30 apps, 3 per category)
Guarantees coverage of CLI/OSS, obscure, ambiguous, enterprise, and review-gated apps.
"""

import json
import csv
import random
from pathlib import Path

MANDATORY_INCLUSIONS = [
    5,   # Twenty (OSS CRM)
    10,  # DealCloud (Enterprise / contact-sales)
    14,  # Front (Ambiguous name)
    17,  # Plain (Ambiguous name)
    28,  # WhatsApp Business (App review / gated)
    31,  # Google Ads (Developer review / approval)
    37,  # systeme.io (Obscure / funnel builder)
    49,  # Amazon Selling Partner (SigV4, strict approval)
    50,  # fanbasis (Obscure creator platform)
    58,  # Sherlock (OSS CLI tool)
    90,  # PitchBook (Institutional contact-sales)
    91,  # NotebookLM (Ambiguous consumer product)
    98,  # Mermaid CLI (OSS CLI tool)
    100  # Grain (Ambiguous AI recorder)
]

def generate_sample(seed: int = 42) -> list:
    random.seed(seed)
    with open("data/input/apps.csv", "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Group by category
    by_cat = {}
    for r in rows:
        cat = r["category"]
        by_cat.setdefault(cat, []).append(r)

    sampled = []
    # For each category, select 3 apps (including mandatory if present)
    for cat, items in sorted(by_cat.items()):
        mandatory_in_cat = [r for r in items if int(r["id"]) in MANDATORY_INCLUSIONS]
        remaining = [r for r in items if int(r["id"]) not in MANDATORY_INCLUSIONS]
        
        # Shuffle remaining deterministically
        random.shuffle(remaining)
        needed = 3 - len(mandatory_in_cat)
        cat_sample = mandatory_in_cat + remaining[:needed]
        sampled.extend(cat_sample)

    sampled.sort(key=lambda x: int(x["id"]))
    return sampled

def main():
    out_file = Path("verification/sample.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    sample = generate_sample(seed=42)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2)

    print(f"Generated stratified sample of {len(sample)} apps saved to {out_file}")
    cats = {}
    for s in sample:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    print(f"Category distribution: {cats}")

if __name__ == "__main__":
    main()
