"""
Phase 2: Agent v1 (Naive Baseline)
- Search snippets only (no deep page fetching, no verifier loops)
- One structured LLM call per app
- Saves valid AppRecord JSON into data/runs/v1/
"""

import os
import sys
import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

from schema.app_record import AppRecord, ProvenanceSpec
from agent.search import SearchProvider
from agent.llm import LLMClient

PILOT_IDS = [1, 58, 91, 50, 83] # Salesforce, Sherlock, NotebookLM, fanbasis, Binance

SYSTEM_PROMPT = """You are an expert API researcher for Composio.
Your goal is to evaluate software products and determine their API buildability for AI agents.
You must output a single valid JSON object strictly adhering to the schema.
Do not invent information. If an API is unknown or not public, record it accurately using the enum values.
"""

def build_v1_prompt(app_row: dict, snippets: list, schema_json: dict) -> str:
    snippets_text = "\n".join([f"- [{s.get('title', '')}]: {s.get('snippet', '')} ({s.get('url', '')})" for s in snippets])
    return f"""App Details:
ID: {app_row['id']}
Name: {app_row['app']}
Category: {app_row['category']}
Reference Hint: {app_row['hint']}

Search Snippets:
{snippets_text if snippets_text else "No external search snippets available."}

Instructions:
Extract the app's buildability profile into a JSON object matching this schema definition:
{json.dumps(schema_json, indent=2)}

Important:
- Set provenance.run_id to "v1_naive"
- Set provenance.prompt_version to "v1.0"
- Return ONLY valid JSON.
"""

def run_app_v1(app_row: dict, search: SearchProvider, llm: LLMClient, schema_json: dict, output_dir: Path) -> dict:
    app_id = int(app_row["id"])
    app_name = app_row["app"]
    slug = app_name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    out_file = output_dir / f"app_{app_id:03d}_{slug}.json"

    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # 1. Search top snippets
    snippets = search.search_snippets(app_name, app_row["hint"])

    # 2. Formulate prompt & call LLM
    prompt = build_v1_prompt(app_row, snippets, schema_json)
    
    raw_data, usage = llm.generate_structured(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        json_schema=schema_json
    )

    # Inject id and app name if missed
    raw_data["id"] = app_id
    raw_data["app"] = app_name
    raw_data["category"] = app_row["category"]
    if "provenance" not in raw_data:
        raw_data["provenance"] = {}
    raw_data["provenance"]["run_id"] = "v1_naive"
    raw_data["provenance"]["model"] = usage.get("model", "unknown")
    raw_data["provenance"]["prompt_version"] = "v1.0"
    raw_data["provenance"]["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Normalize common enum typos from naive LLM
    if "auth_methods" in raw_data and isinstance(raw_data["auth_methods"], list):
        norm_auth = []
        for m in raw_data["auth_methods"]:
            m_str = str(m).lower()
            if m_str == "token":
                m_str = "bearer_token"
            norm_auth.append(m_str)
        raw_data["auth_methods"] = norm_auth

    # Validate against AppRecord
    record = AppRecord.model_validate(raw_data)
    record_dict = record.model_dump(mode="json")

    # Save to runs/v1
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record_dict, f, indent=2)

    return record_dict

def main():
    parser = argparse.ArgumentParser(description="Run Agent v1 Naive Baseline")
    parser.add_argument("--pilot", action="store_true", help="Run 5 pilot apps only")
    parser.add_argument("--all", action="store_true", help="Run all 100 apps")
    parser.add_argument("--app-id", type=int, help="Run single app by ID")
    args = parser.parse_args()

    input_csv = Path("data/input/apps.csv")
    output_dir = Path("data/runs/v1")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open("schema/app_record.schema.json", "r", encoding="utf-8") as f:
        schema_json = json.load(f)

    with open(input_csv, "r", encoding="utf-8") as f:
        apps = list(csv.DictReader(f))

    search = SearchProvider()
    llm = LLMClient()

    if not llm.has_valid_key():
        print(f"\n[STOP CONDITION TRIGGERED: MISSING API KEY]")
        print(f"Agent v1 requires an LLM API Key to run. Currently provider is '{llm.provider}' and key is missing.")
        print(f"Please provide GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env.")
        sys.exit(2)

    if args.pilot:
        target_apps = [a for a in apps if int(a["id"]) in PILOT_IDS]
        print(f"--- Running 5 Pilot Apps (Salesforce, Sherlock, NotebookLM, fanbasis, Binance) ---")
    elif args.app_id:
        target_apps = [a for a in apps if int(a["id"]) == args.app_id]
    else:
        target_apps = apps
        print(f"--- Running all {len(apps)} Apps ---")

    start_time = time.time()
    successful = 0
    failures = []

    for app in target_apps:
        print(f"[{app['id']}/100] Processing {app['app']} ({app['category']})...", end="", flush=True)
        try:
            rec = run_app_v1(app, search, llm, schema_json, output_dir)
            successful += 1
            print(f" DONE -> Verdict: {rec['verdict']}, Blocker: {rec['main_blocker']}")
        except Exception as e:
            failures.append((app["id"], app["app"], str(e)))
            print(f" FAILED: {e}")

    total_time = round(time.time() - start_time, 2)
    print("\n" + "=" * 60)
    print(f"V1 BASELINE BATCH RUN COMPLETED")
    print(f"Processed: {len(target_apps)} | Success: {successful} | Failures: {len(failures)}")
    print(f"Elapsed Time: {total_time}s")
    print(f"Total Prompt Tokens: {llm.total_prompt_tokens}")
    print(f"Total Completion Tokens: {llm.total_completion_tokens}")
    print(f"Total Estimated Spend: ${llm.total_cost_usd:.4f} USD")

    if args.pilot:
        projected_100_cost = (llm.total_cost_usd / len(target_apps)) * 100 if target_apps else 0.0
        print(f"Projected 100-App Cost: ${projected_100_cost:.4f} USD (Max Budget: $20.00 USD)")
        if projected_100_cost > 20.0:
            print("[STOP: Projected budget exceeds MAX_BUDGET_USD]")
            sys.exit(1)
        else:
            print("[BUDGET CHECK PASSED: Projected spend is well under $20.00 USD]")

    print("=" * 60)

if __name__ == "__main__":
    main()
