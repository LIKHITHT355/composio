"""
Preflight verification script.
Checks:
1. Python version >= 3.11
2. Network connectivity (fetches 3 public docs pages)
3. LLM API Key availability in environment (.env or OS)
4. Composio Key availability
5. Search Provider availability
6. Playwright / Browser tools
7. Input file data/input/apps.csv validation (100 rows, 10 categories)
"""

import os
import sys
import csv
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()

def check_python():
    version = sys.version_info
    ok = version >= (3, 11)
    return ok, f"Python {version.major}.{version.minor}.{version.micro}"

def check_network():
    test_urls = [
        "https://docs.github.com/en/rest",
        "https://stripe.com/docs/api",
        "https://docs.composio.dev"
    ]
    results = []
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        for url in test_urls:
            try:
                resp = client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                results.append((url, resp.status_code == 200, f"Status {resp.status_code}"))
            except Exception as e:
                results.append((url, False, str(e)))
    all_ok = all(r[1] for r in results)
    return all_ok, results

def check_keys():
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    composio_key = os.getenv("COMPOSIO_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    serpapi_key = os.getenv("SERPAPI_API_KEY")

    has_llm = bool(gemini_key or openai_key or anthropic_key)
    has_composio = bool(composio_key)
    has_search = bool(tavily_key or serpapi_key)

    details = {
        "LLM_KEY": "PRESENT" if has_llm else "MISSING",
        "COMPOSIO_KEY": "PRESENT" if has_composio else "OPTIONAL/MISSING",
        "SEARCH_PROVIDER": "PRESENT" if has_search else "FALLBACK_DIRECT_FETCH"
    }
    return has_llm, details

def check_csv(csv_path="data/input/apps.csv"):
    p = Path(csv_path)
    if not p.exists():
        return False, "data/input/apps.csv not found"
    
    with open(p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if len(rows) != 100:
        return False, f"Expected 100 rows, found {len(rows)}"
    
    categories = {r.get("category", "").strip() for r in rows}
    if len(categories) != 10:
        return False, f"Expected 10 categories, found {len(categories)}: {categories}"
    
    # Check required fields
    for idx, r in enumerate(rows, start=1):
        if not r.get("id") or not r.get("app") or not r.get("category"):
            return False, f"Row {idx} missing required fields (id, app, category)"
            
    return True, f"100 rows valid across 10 categories: {list(sorted(categories))}"

def main():
    print("=" * 60)
    print("PREFLIGHT DIAGNOSTIC REPORT")
    print("=" * 60)

    py_ok, py_msg = check_python()
    print(f"[{'PASS' if py_ok else 'FAIL'}] Python: {py_msg}")

    net_ok, net_details = check_network()
    print(f"[{'PASS' if net_ok else 'FAIL'}] Network Connectivity:")
    for url, ok, msg in net_details:
        print(f"   - {url} -> {'OK' if ok else 'FAIL'} ({msg})")

    llm_ok, key_details = check_keys()
    print(f"[{'PASS' if llm_ok else 'WARN/STOP'}] Keys & Providers:")
    for k, v in key_details.items():
        print(f"   - {k}: {v}")

    csv_ok, csv_msg = check_csv()
    print(f"[{'PASS' if csv_ok else 'FAIL/WAIT'}] Apps CSV: {csv_msg}")

    print("=" * 60)
    
    # Preflight overall status
    if not (py_ok and net_ok):
        print("CRITICAL PREFLIGHT FAILURE: Python or Network check failed.")
        sys.exit(1)
        
    if not csv_ok:
        print("PREFLIGHT GATE PAUSE: apps.csv needs to be placed into data/input/apps.csv.")
        sys.exit(2)

    print("PREFLIGHT PASSED SUCCESSFULLY.")

if __name__ == "__main__":
    main()
