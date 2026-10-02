"""
Composio App Buildability Agent - Unified CLI Entrypoint
Usage:
  python -m agent research "<App Name>" --site <domain> [--category <cat>]
  python -m agent score
  python -m agent patterns
  python -m agent build-site
"""

import sys
import json
import argparse
from pathlib import Path

from agent.resolver import EntityResolver
from agent.discoverer import FieldDiscoverer
from agent.fetcher import PageFetcher
from agent.search import SearchProvider
from agent.v2_grounded import run_app_v2
from agent.v4_refined import refine_record
from agent.llm import LLMClient

def cmd_research(app_name: str, site: str = None, category: str = "General"):
    print(f"=== Researching App: {app_name} ===")
    
    # 1. Resolve
    print("1. Resolving canonical entity and domain...")
    resolved = EntityResolver.resolve(app_name, category, site or "")
    print(f"   -> Canonical: {resolved['app']} ({resolved['official_domain']})")

    # 2. Setup Pipeline Providers
    search_provider = SearchProvider()
    discoverer = FieldDiscoverer(search_provider)
    fetcher = PageFetcher()
    llm = LLMClient()
    resolver = EntityResolver()

    with open("schema/app_record.schema.json", "r", encoding="utf-8") as f:
        schema_json = json.load(f)

    scratch_dir = Path("data/scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)

    dummy_input = {
        "id": 999,
        "app": resolved["app"],
        "category": category,
        "hint": resolved["official_domain"]
    }

    # 3. Grounded Extraction
    print("2. Extracting evidence-grounded claims with in-source citations...")
    v2_record = run_app_v2(dummy_input, resolver, discoverer, fetcher, llm, schema_json, scratch_dir)
    
    # 4. Refine with Taxonomy Rules
    print("3. Applying verification rules and taxonomy reconciliation...")
    v4_record = refine_record(v2_record)

    print("\n" + "=" * 60)
    print("FINAL BUILDABILITY DOSSIER")
    print("=" * 60)
    print(f"App: {v4_record['app']} ({v4_record['official_domain']})")
    print(f"Category: {v4_record['category']}")
    print(f"Verdict: {v4_record['verdict'].upper()}")
    print(f"Main Blocker: {v4_record['main_blocker']}")
    print(f"Credential Access: {v4_record['credential_access']}")
    print(f"Auth Methods: {', '.join(v4_record.get('auth_methods', []))}")
    print(f"API Exists: {v4_record.get('api', {}).get('exists')} (Styles: {', '.join(v4_record.get('api', {}).get('styles', []))})")
    print(f"MCP Status: {v4_record.get('mcp', {}).get('status')}")
    print("\nEvidence Quotes:")
    for e in v4_record.get("evidence", []):
        print(f" - [{e['field']}] {e['url']}\n   \"{e['quote']}\"")
    print("=" * 60)

    # Save to scratch
    scratch_dir = Path("data/scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    out_file = scratch_dir / f"{v4_record['app'].lower().replace(' ', '_')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(v4_record, f, indent=2)
    print(f"Output saved to {out_file}")

def main():
    parser = argparse.ArgumentParser(description="Composio App Buildability Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    # research command
    res_parser = subparsers.add_parser("research", help="Research a single app")
    res_parser.add_argument("app", help="Name of the app (e.g. 'Salesforce')")
    res_parser.add_argument("--site", help="Official domain or hint URL", default=None)
    res_parser.add_argument("--category", help="Software category", default="General")

    # score command
    subparsers.add_parser("score", help="Run benchmark scoring across runs")

    # patterns command
    subparsers.add_parser("patterns", help="Compute patterns and strategic clusters")

    # build-site command
    subparsers.add_parser("build-site", help="Recompile the case study HTML")

    args = parser.parse_args()

    if args.command == "research":
        cmd_research(args.app, args.site, args.category)
    elif args.command == "score":
        import verification.score
        verification.score.main()
    elif args.command == "patterns":
        import analysis.patterns
        analysis.patterns.main()
    elif args.command == "build-site":
        import site.build_site
        site.build_site.main()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
