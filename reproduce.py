"""
Composio Research: Master End-to-End Reproduction Script
Enables a blind reviewer to reproduce and verify the entire project with a single command:
  python reproduce.py
"""

import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_step(step_name: str, cmd: list):
    print(f"\n[{step_name}] Running: {' '.join(cmd)}...")
    res = subprocess.run([sys.executable] + cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        print(f"[FAIL] [{step_name}]:\n{res.stderr}\n{res.stdout}")
        sys.exit(1)
    else:
        print(f"[PASS] [{step_name}]")
        for line in res.stdout.strip().split("\n")[-3:]:
            if line:
                print(f"   {line}")

def main():
    print("=" * 70)
    print("COMPOSIO APP BUILDABILITY RESEARCH: FULL REPRODUCTION RUNNER")
    print("=" * 70)

    # 1. Run Unit Tests (Schema & Pipeline Validation)
    run_step("1/5: Unit Tests", ["-m", "pytest", "tests/", "-v"])

    # 2. Build Final Datasets (apps.json & apps.csv)
    run_step("2/5: Build Final Datasets", ["-m", "analysis.build_final"])

    # 3. Run Benchmark Scoring (v1, v2, v3, v4 & Holdout with Wilson CIs)
    run_step("3/5: Statistical Benchmark", ["verification/score.py"])

    # 4. Synthesize Patterns & Action Clusters
    run_step("4/5: Synthesize Patterns", ["-m", "analysis.patterns"])

    # 5. Recompile Standalone Interactive HTML Case Study
    run_step("5/5: Compile HTML Case Study", ["site/build_site.py"])

    print("\n" + "=" * 70)
    print("*** REPRODUCTION COMPLETE: ALL GATES & DELIVERABLES VERIFIED! ***")
    print("=" * 70)
    print("Artifacts Ready:")
    print(" - Interactive Case Study: site/index.html")
    print(" - Clean Dataset:          data/final/apps.json (100 apps)")
    print(" - Tabular CSV:            data/final/apps.csv")
    print(" - Benchmark Results:      verification/results.json")
    print(" - Pattern Analytics:      data/final/patterns.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
