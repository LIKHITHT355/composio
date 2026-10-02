"""
Phase 3: Agent v2 (Evidence-Grounded Extraction + Verifier A)
- Entity resolution + targeted field discovery
- Deep page fetch & cache
- LLM extracts schema strictly from cached evidence with URL + quote (<=300 chars)
- Verifier A: Deterministic in-source quote verification, domain check, and consistency rules
"""

import os
import sys
import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from schema.app_record import (
    AppRecord,
    EvidenceItem,
    ConfidenceEnum,
    VerdictEnum,
    CredentialAccessEnum,
    MainBlockerEnum,
    ProvenanceSpec
)
from agent.resolver import EntityResolver
from agent.discoverer import FieldDiscoverer
from agent.fetcher import PageFetcher
from agent.search import SearchProvider
from agent.llm import LLMClient

SYSTEM_PROMPT_V2 = """You are a rigorous, evidence-grounded API research agent for Composio.
Your directive is zero fabrication (Rule R1): every claim must be grounded in the provided cached text passages.
Every key finding must include an EvidenceItem with:
- "field": the schema field name (e.g. auth_methods, credential_access, api.exists, mcp.status, verdict)
- "url": exact source URL from the provided text
- "quote": verbatim quotation (<=300 characters) copied directly from the text proving the claim.

If the evidence does not clearly prove an API or authentication method exists, output "unknown" or "none".
Never assume or extrapolate beyond the provided text.
Output MUST be a single valid JSON object matching the AppRecord schema.
"""

def build_v2_prompt(app_row: dict, resolved: dict, evidence_passages: List[Dict[str, str]], schema_json: dict) -> str:
    passages_text = ""
    for idx, p in enumerate(evidence_passages, 1):
        passages_text += f"\n--- SOURCE {idx}: {p['url']} ---\n{p['text']}\n"

    return f"""Target Application:
ID: {app_row['id']}
Name: {resolved['app']}
Category: {app_row['category']}
Official Domain: {resolved['official_domain']}
Hint: {app_row['hint']}

GROUNDED EVIDENCE PASSAGES:
{passages_text if passages_text.strip() else "No fetched web passages available."}

SCHEMA CONTRACT:
{json.dumps(schema_json, indent=2)}

TASK:
Produce an AppRecord adhering strictly to the schema.
Every non-unknown Key Field (auth_methods, credential_access, api.exists, mcp.status, verdict, main_blocker) MUST cite an evidence quote verbatim from the text above.
Set provenance.run_id to "v2_grounded".
Set provenance.prompt_version to "v2.0".
"""

def run_verifier_a(record: AppRecord, fetcher: PageFetcher, resolved_domain: str) -> Tuple[AppRecord, Dict[str, Any]]:
    """
    Verifier A (Deterministic):
    1. Verifies quote literally exists in cached page.
    2. Verifies URL domain consistency.
    3. Enforces strict consistency rules.
    """
    total_quotes = len(record.evidence)
    verified_quotes = 0
    flags = []

    # 1. Quote in-source verification
    for item in record.evidence:
        is_verified = fetcher.verify_quote(item.url, item.quote)
        item.quote_verified = is_verified
        if is_verified:
            verified_quotes += 1
        else:
            flags.append(f"Unverified quote for {item.field}: '{item.quote[:50]}...'")

    # 2. Domain check
    for item in record.evidence:
        if resolved_domain not in item.url and "github.com" not in item.url:
            flags.append(f"Third-party evidence domain used: {item.url}")
            if item.field in record.confidence:
                record.confidence[item.field] = ConfidenceEnum.LOW

    # 3. Consistency rules
    if not record.api.exists and record.verdict == VerdictEnum.READY_NOW:
        flags.append("Inconsistency: api.exists is False but verdict is ready_now. Downgrading.")
        record.verdict = VerdictEnum.BLOCKED
        record.main_blocker = MainBlockerEnum.NO_PUBLIC_API
        record.needs_human = True

    if record.credential_access in [CredentialAccessEnum.APPROVAL_REQUIRED, CredentialAccessEnum.PARTNER_OR_SALES_GATED] and record.verdict == VerdictEnum.READY_NOW:
        flags.append(f"Inconsistency: Gated access ({record.credential_access}) cannot be ready_now.")
        record.verdict = VerdictEnum.NEEDS_OUTREACH
        record.needs_human = True

    if record.credential_access == CredentialAccessEnum.PAID_PLAN_REQUIRED and record.verdict == VerdictEnum.READY_NOW:
        record.verdict = VerdictEnum.READY_WITH_CAVEATS
        record.main_blocker = MainBlockerEnum.PAID_PLAN

    # Confidence calculation
    quote_acc = (verified_quotes / total_quotes) if total_quotes > 0 else 0.0
    for kf in ["auth_methods", "credential_access", "api.exists", "verdict", "main_blocker"]:
        # If any quote for this field is unverified, lower confidence
        field_quotes = [e for e in record.evidence if e.field == kf or kf.startswith(e.field)]
        if field_quotes and any(not e.quote_verified for e in field_quotes):
            record.confidence[kf] = ConfidenceEnum.LOW
            record.needs_human = True
        elif not field_quotes:
            record.confidence[kf] = ConfidenceEnum.LOW
        else:
            record.confidence[kf] = ConfidenceEnum.HIGH

    meta = {
        "total_quotes": total_quotes,
        "verified_quotes": verified_quotes,
        "quote_accuracy": quote_acc,
        "flags": flags
    }
    return record, meta

def run_app_v2(app_row: dict, resolver: EntityResolver, discoverer: FieldDiscoverer, fetcher: PageFetcher, llm: LLMClient, schema_json: dict, output_dir: Path) -> dict:
    app_id = int(app_row["id"])
    app_name = app_row["app"]
    slug = app_name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    out_file = output_dir / f"app_{app_id:03d}_{slug}.json"

    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # 1. Resolve
    resolved = resolver.resolve(app_name, app_row["category"], app_row["hint"])

    # 2. Discover targeted endpoints & URLs
    discovered = discoverer.discover(resolved["app"], resolved["official_domain"], app_row["hint"])
    candidate_urls = []
    
    # Priority: primary docs from resolver
    if resolved.get("primary_docs"):
        candidate_urls.append(resolved["primary_docs"])

    for field_cat, items in discovered.items():
        for item in items[:2]:
            u = item.get("url")
            if u and u not in candidate_urls:
                candidate_urls.append(u)

    # 3. Fetch & extract top passages (~6k tokens cap)
    evidence_passages = []
    keywords = ["api", "oauth", "token", "key", "developer", "pricing", "free", "tier", "mcp", "rest", "graphql", "sign"]
    
    for url in candidate_urls[:4]: # Limit to top 4 relevant pages for token thrift
        page_data = fetcher.fetch(url)
        if page_data["status_code"] == 200:
            top_text = fetcher.get_top_passages(page_data["clean_text"], keywords, max_chars=3500)
            if top_text.strip():
                evidence_passages.append({
                    "url": page_data["url"],
                    "text": top_text
                })

    # 4. Extract
    prompt = build_v2_prompt(app_row, resolved, evidence_passages, schema_json)
    raw_data, usage = llm.generate_structured(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT_V2,
        json_schema=schema_json
    )

    raw_data["id"] = app_id
    raw_data["app"] = resolved["app"]
    raw_data["category"] = app_row["category"]
    raw_data["official_domain"] = resolved["official_domain"]
    
    if "provenance" not in raw_data:
        raw_data["provenance"] = {}
    raw_data["provenance"]["run_id"] = "v2_grounded"
    raw_data["provenance"]["model"] = usage.get("model", "gemini-3.5-flash-lite")
    raw_data["provenance"]["prompt_version"] = "v2.0"
    raw_data["provenance"]["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Model validation
    record = AppRecord.model_validate(raw_data)

    # 5. Verifier A (Deterministic)
    verified_record, verifier_meta = run_verifier_a(record, fetcher, resolved["official_domain"])
    record_dict = verified_record.model_dump(mode="json")
    record_dict["_verifier_a"] = verifier_meta

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record_dict, f, indent=2)

    return record_dict

def main():
    parser = argparse.ArgumentParser(description="Run Agent v2 Evidence-Grounded Pipeline")
    parser.add_argument("--pilot", action="store_true", help="Run 5 pilot apps only")
    parser.add_argument("--all", action="store_true", help="Run all 100 apps")
    parser.add_argument("--app-id", type=int, help="Run single app by ID")
    args = parser.parse_args()

    input_csv = Path("data/input/apps.csv")
    output_dir = Path("data/runs/v2")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open("schema/app_record.schema.json", "r", encoding="utf-8") as f:
        schema_json = json.load(f)

    with open(input_csv, "r", encoding="utf-8") as f:
        apps = list(csv.DictReader(f))

    search = SearchProvider()
    resolver = EntityResolver()
    discoverer = FieldDiscoverer(search)
    fetcher = PageFetcher()
    llm = LLMClient()

    if not llm.has_valid_key():
        print("Missing LLM API key.")
        sys.exit(1)

    PILOT_IDS = [1, 58, 91, 50, 83]
    if args.pilot:
        target_apps = [a for a in apps if int(a["id"]) in PILOT_IDS]
    elif args.app_id:
        target_apps = [a for a in apps if int(a["id"]) == args.app_id]
    else:
        target_apps = apps

    total_quotes = 0
    verified_quotes = 0
    start_time = time.time()

    for app in target_apps:
        print(f"[{app['id']}/100] V2 Grounding {app['app']}...", end="", flush=True)
        try:
            rec = run_app_v2(app, resolver, discoverer, fetcher, llm, schema_json, output_dir)
            va = rec.get("_verifier_a", {})
            total_quotes += va.get("total_quotes", 0)
            verified_quotes += va.get("verified_quotes", 0)
            q_pct = (va.get("verified_quotes", 0) / va.get("total_quotes", 1)) * 100 if va.get("total_quotes") else 100
            print(f" DONE -> Verdict: {rec['verdict']} | Quotes Verified: {q_pct:.0f}%")
        except Exception as e:
            print(f" FAILED: {e}")

    duration = round(time.time() - start_time, 2)
    overall_quote_acc = (verified_quotes / total_quotes * 100) if total_quotes > 0 else 100.0
    print("\n" + "=" * 60)
    print("AGENT V2 RUN SUMMARY")
    print(f"Processed: {len(target_apps)} apps in {duration}s")
    print(f"Total Quotes Extracted: {total_quotes}")
    print(f"In-Source Verified Quotes: {verified_quotes} ({overall_quote_acc:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    main()
