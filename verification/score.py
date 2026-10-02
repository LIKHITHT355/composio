"""
Phase 4: Benchmark Scoring & Statistical Evaluation
Scores Agent v1, v2, and v3 against gold_labels.json on the 30-app sample.
Computes:
- Per-field accuracy (auth_methods exact & overlap)
- App-level "all KF correct"
- 95% Wilson Score Confidence Intervals
- Confusion matrices (credential_access, verdict)
- Error taxonomy categorization
- Outputs verification/results.json and verification/misses.md
"""

import json
import math
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple

KEY_FIELDS = [
    "auth_methods",
    "credential_access",
    "api.exists",
    "mcp.status",
    "verdict",
    "main_blocker"
]

def wilson_score_interval(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + (z ** 2) / total
    center = (p + (z ** 2) / (2 * total)) / denom
    margin = (z * math.sqrt((p * (1 - p) / total) + ((z ** 2) / (4 * (total ** 2))))) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return (round(lower, 4), round(upper, 4))

def check_auth_methods_match(agent_auth: List[str], gold_auth: List[str]) -> Tuple[bool, bool]:
    norm_agent = set(m.lower().strip() for m in agent_auth)
    norm_gold = set(m.lower().strip() for m in gold_auth)
    exact = norm_agent == norm_gold
    overlap = len(norm_agent.intersection(norm_gold)) > 0 if norm_gold else (norm_agent == {"none"})
    return exact, overlap

def classify_error(field: str, agent_val: Any, gold_val: Any, app_name: str) -> str:
    agent_str = str(agent_val).lower()
    gold_str = str(gold_val).lower()

    if field == "api.exists" and agent_str == "true" and gold_str == "false":
        return "hallucinated"
    if field == "verdict" and agent_str == "ready_now" and gold_str in ["ready_with_caveats", "needs_outreach"]:
        return "over_generous_verdict"
    if field == "credential_access" and "free" in agent_str and "paid" in gold_str:
        return "missed_gating_nuance"
    if field == "credential_access" and "free" in agent_str and "approval" in gold_str:
        return "missed_gating_nuance"
    if "cli" in app_name.lower() or "sherlock" in app_name.lower() or "mermaid" in app_name.lower():
        if field == "verdict" and agent_str != "not_an_api_product":
            return "wrong_entity"
    return "missed_gating_nuance"

def score_version(version_dir: Path, gold_labels: List[Dict[str, Any]]) -> Dict[str, Any]:
    field_stats = {
        "auth_methods_exact": {"correct": 0, "total": 0, "unsure": 0},
        "auth_methods_overlap": {"correct": 0, "total": 0, "unsure": 0},
        "credential_access": {"correct": 0, "total": 0, "unsure": 0},
        "api.exists": {"correct": 0, "total": 0, "unsure": 0},
        "mcp.status": {"correct": 0, "total": 0, "unsure": 0},
        "verdict": {"correct": 0, "total": 0, "unsure": 0},
        "main_blocker": {"correct": 0, "total": 0, "unsure": 0}
    }

    confusion_matrices = {
        "verdict": {},
        "credential_access": {}
    }

    error_taxonomy = {
        "hallucinated": 0,
        "wrong_entity": 0,
        "stale_docs": 0,
        "missed_gating_nuance": 0,
        "over_generous_verdict": 0,
        "bad_evidence": 0
    }

    all_kf_correct_count = 0
    total_apps_evaluated = 0
    misses_list = []

    # Map gold labels by ID
    gold_by_id = {int(g["id"]): g for g in gold_labels}

    for app_id, gold in gold_by_id.items():
        # Find matching run record in version_dir
        matches = list(version_dir.glob(f"app_{app_id:03d}_*.json"))
        if not matches:
            continue

        with open(matches[0], "r", encoding="utf-8") as f:
            rec = json.load(f)

        app_name = gold.get("app", rec.get("app", f"App {app_id}"))
        total_apps_evaluated += 1
        app_all_correct = True

        # 1. auth_methods
        gold_auth = gold.get("auth_methods", [])
        if "unsure" in gold_auth:
            field_stats["auth_methods_exact"]["unsure"] += 1
            field_stats["auth_methods_overlap"]["unsure"] += 1
        else:
            field_stats["auth_methods_exact"]["total"] += 1
            field_stats["auth_methods_overlap"]["total"] += 1
            exact, overlap = check_auth_methods_match(rec.get("auth_methods", []), gold_auth)
            if exact:
                field_stats["auth_methods_exact"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("auth_methods", rec.get("auth_methods"), gold_auth, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "auth_methods",
                    "agent": rec.get("auth_methods"),
                    "truth": gold_auth,
                    "cause": err_type
                })
            if overlap:
                field_stats["auth_methods_overlap"]["correct"] += 1

        # 2. credential_access
        gold_cred = gold.get("credential_access")
        agent_cred = rec.get("credential_access")
        if gold_cred == "unsure":
            field_stats["credential_access"]["unsure"] += 1
        else:
            field_stats["credential_access"]["total"] += 1
            cm = confusion_matrices["credential_access"].setdefault(str(gold_cred), {})
            cm[str(agent_cred)] = cm.get(str(agent_cred), 0) + 1
            if agent_cred == gold_cred:
                field_stats["credential_access"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("credential_access", agent_cred, gold_cred, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "credential_access",
                    "agent": agent_cred,
                    "truth": gold_cred,
                    "cause": err_type
                })

        # 3. api.exists
        gold_api_exists = gold.get("api_exists")
        agent_api_exists = rec.get("api", {}).get("exists")
        if gold_api_exists == "unsure":
            field_stats["api.exists"]["unsure"] += 1
        else:
            field_stats["api.exists"]["total"] += 1
            if agent_api_exists == gold_api_exists:
                field_stats["api.exists"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("api.exists", agent_api_exists, gold_api_exists, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "api.exists",
                    "agent": agent_api_exists,
                    "truth": gold_api_exists,
                    "cause": err_type
                })

        # 4. mcp.status
        gold_mcp = gold.get("mcp_status")
        agent_mcp = rec.get("mcp", {}).get("status")
        if gold_mcp == "unsure":
            field_stats["mcp.status"]["unsure"] += 1
        else:
            field_stats["mcp.status"]["total"] += 1
            if agent_mcp == gold_mcp:
                field_stats["mcp.status"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("mcp.status", agent_mcp, gold_mcp, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "mcp.status",
                    "agent": agent_mcp,
                    "truth": gold_mcp,
                    "cause": err_type
                })

        # 5. verdict
        gold_verdict = gold.get("verdict")
        agent_verdict = rec.get("verdict")
        if gold_verdict == "unsure":
            field_stats["verdict"]["unsure"] += 1
        else:
            field_stats["verdict"]["total"] += 1
            cm = confusion_matrices["verdict"].setdefault(str(gold_verdict), {})
            cm[str(agent_verdict)] = cm.get(str(agent_verdict), 0) + 1
            if agent_verdict == gold_verdict:
                field_stats["verdict"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("verdict", agent_verdict, gold_verdict, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "verdict",
                    "agent": agent_verdict,
                    "truth": gold_verdict,
                    "cause": err_type
                })

        # 6. main_blocker
        gold_blocker = gold.get("main_blocker")
        agent_blocker = rec.get("main_blocker")
        if gold_blocker == "unsure":
            field_stats["main_blocker"]["unsure"] += 1
        else:
            field_stats["main_blocker"]["total"] += 1
            if agent_blocker == gold_blocker:
                field_stats["main_blocker"]["correct"] += 1
            else:
                app_all_correct = False
                err_type = classify_error("main_blocker", agent_blocker, gold_blocker, app_name)
                error_taxonomy[err_type] += 1
                misses_list.append({
                    "app": app_name,
                    "field": "main_blocker",
                    "agent": agent_blocker,
                    "truth": gold_blocker,
                    "cause": err_type
                })

        if app_all_correct:
            all_kf_correct_count += 1

    # Format results with CIs
    formatted_fields = {}
    for f_name, stats in field_stats.items():
        corr = stats["correct"]
        tot = stats["total"]
        acc = (corr / tot) if tot > 0 else 0.0
        ci = wilson_score_interval(corr, tot)
        formatted_fields[f_name] = {
            "correct": corr,
            "total": tot,
            "unsure": stats["unsure"],
            "accuracy": round(acc, 4),
            "ci_95": ci
        }

    app_level_acc = (all_kf_correct_count / total_apps_evaluated) if total_apps_evaluated > 0 else 0.0
    app_ci = wilson_score_interval(all_kf_correct_count, total_apps_evaluated)

    return {
        "total_apps_evaluated": total_apps_evaluated,
        "all_kf_correct": {
            "count": all_kf_correct_count,
            "total": total_apps_evaluated,
            "accuracy": round(app_level_acc, 4),
            "ci_95": app_ci
        },
        "fields": formatted_fields,
        "confusion_matrices": confusion_matrices,
        "error_taxonomy": error_taxonomy,
        "misses": misses_list
    }

def main():
    gold_path = Path("verification/gold_labels.json")
    if not gold_path.exists():
        print(f"Error: {gold_path} does not exist. Awaiting human gold labels.")
        return

    with open(gold_path, "r", encoding="utf-8") as f:
        gold_labels = json.load(f)

    results = {
        "v1": score_version(Path("data/runs/v1"), gold_labels),
        "v2": score_version(Path("data/runs/v2"), gold_labels),
        "v3": score_version(Path("data/runs/v3"), gold_labels),
        "v4": score_version(Path("data/runs/v4"), gold_labels)
    }

    # Score holdout sample if available
    holdout_path = Path("verification/holdout_labels.json")
    if holdout_path.exists():
        with open(holdout_path, "r", encoding="utf-8") as f:
            holdout_labels = json.load(f)
        results["holdout_v4"] = score_version(Path("data/runs/v4"), holdout_labels)

    out_file = Path("verification/results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Generate verification/misses.md
    misses_md = Path("verification/misses.md")
    with open(misses_md, "w", encoding="utf-8") as f:
        f.write("# Verification Misses Log & Detailed Error Taxonomy\n\n")
        for ver in ["v1", "v2", "v3", "v4"]:
            if ver in results:
                f.write(f"## Version {ver.upper()} Misses ({len(results[ver]['misses'])} total discrepancies)\n\n")
                f.write("| App | Field | Agent Said | Ground Truth | Error Taxonomy Cause |\n")
                f.write("|---|---|---|---|---|\n")
                for m in results[ver]["misses"]:
                    f.write(f"| **{m['app']}** | `{m['field']}` | `{m['agent']}` | `{m['truth']}` | {m['cause']} |\n")
                f.write("\n")

    print(f"Benchmark results saved to {out_file} and {misses_md}")

if __name__ == "__main__":
    main()
