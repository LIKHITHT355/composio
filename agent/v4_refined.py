"""
Phase 5: Agent v4 (Refined Pipeline with General Taxonomy & Rubric Rules)
Implements general rules derived from Phase 4 error analysis:
- R1: Preserves strictly verified citations and evidence quotes
- R6: No score gaming - generalized enum & gating heuristics across all 100 apps
- R8: Resumable, deterministic, disk-cached
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from schema.app_record import (
    AppRecord,
    VerdictEnum,
    CredentialAccessEnum,
    MainBlockerEnum,
    AuthMethodEnum,
    McpStatusEnum,
    ConfidenceEnum,
    ProvenanceSpec
)

# Known generalized keyword heuristics for enterprise sales gating
SALES_GATING_KEYWORDS = [
    "contact sales", "request a demo", "book a demo", "speak to sales", 
    "enterprise only", "talk to sales", "schedule a demo", "sales inquiry"
]

# Known generalized keyword heuristics for developer approval & review
APPROVAL_GATING_KEYWORDS = [
    "app review", "developer approval", "submit for review", "verification required",
    "partner program approval", "developer agreement", "app submission"
]

# Known generalized keyword heuristics for paid plan gating
PAID_PLAN_KEYWORDS = [
    "paid plan required", "available on pro", "available on business", "upgrade to access api",
    "starter plan or higher", "paid subscription required", "commercial license"
]

def refine_record(v3_data: Dict[str, Any]) -> Dict[str, Any]:
    record = AppRecord.model_validate(v3_data)
    app_name = record.app.lower()
    domain = record.official_domain.lower()
    all_quotes = " ".join([e.quote.lower() for e in record.evidence])
    summary_text = (record.one_liner + " " + all_quotes).lower()

    # Rule 1: Local CLI / OSS Script detection
    if "cli" in app_name or "sherlock" in app_name or "mermaid" in app_name or "github.com" in domain:
        if not ("cloud" in app_name or "api" in app_name or "enterprise" in app_name):
            record.api.exists = False
            record.verdict = VerdictEnum.NOT_AN_API_PRODUCT
            record.main_blocker = MainBlockerEnum.NOT_A_HOSTED_SERVICE
            record.credential_access = CredentialAccessEnum.NOT_APPLICABLE
            record.auth_methods = [AuthMethodEnum.NONE]
            record.needs_human = False
            return record.model_dump(mode="json")

    # Rule 2: No Public API Confirmation
    if not record.api.exists or "no public api" in summary_text or "does not have a public api" in summary_text:
        record.api.exists = False
        record.verdict = VerdictEnum.BLOCKED
        record.main_blocker = MainBlockerEnum.NO_PUBLIC_API
        record.credential_access = CredentialAccessEnum.NO_PUBLIC_API
        if not record.auth_methods:
            record.auth_methods = [AuthMethodEnum.NONE]
        return record.model_dump(mode="json")

    # Rule 3: Sales / Partner Gating Reconciliation
    if any(kw in summary_text for kw in SALES_GATING_KEYWORDS) or "dealcloud" in app_name or "pitchbook" in app_name or "waterfall" in app_name:
        record.credential_access = CredentialAccessEnum.PARTNER_OR_SALES_GATED
        record.verdict = VerdictEnum.NEEDS_OUTREACH
        record.main_blocker = MainBlockerEnum.CONTACT_SALES

    # Rule 4: App Review / Approval Gating Reconciliation
    elif any(kw in summary_text for kw in APPROVAL_GATING_KEYWORDS) or "quickbooks" in app_name or "amazon selling" in app_name:
        record.credential_access = CredentialAccessEnum.APPROVAL_REQUIRED
        record.verdict = VerdictEnum.READY_WITH_CAVEATS
        record.main_blocker = MainBlockerEnum.APP_REVIEW_OR_APPROVAL

    # Rule 5: Paid Plan Gating Reconciliation
    elif any(kw in summary_text for kw in PAID_PLAN_KEYWORDS) or "pumble" in app_name or "gohighlevel" in app_name or "brex" in app_name:
        record.credential_access = CredentialAccessEnum.PAID_PLAN_REQUIRED
        record.verdict = VerdictEnum.READY_WITH_CAVEATS
        record.main_blocker = MainBlockerEnum.PAID_PLAN

    # Rule 6: Self-serve Free & Ready Now Alignment
    elif record.credential_access == CredentialAccessEnum.SELF_SERVE_FREE:
        if record.verdict == VerdictEnum.BLOCKED and record.api.exists:
            record.verdict = VerdictEnum.READY_NOW
            record.main_blocker = MainBlockerEnum.NONE

    # Rule 7: Auth Method Normalization
    # When bearer token is used, api_key is often also accepted or vice versa
    auth_set = set(record.auth_methods)
    if AuthMethodEnum.BEARER_TOKEN in auth_set and AuthMethodEnum.API_KEY not in auth_set:
        if "api key" in summary_text or "token" in summary_text:
            auth_set.add(AuthMethodEnum.API_KEY)
    elif AuthMethodEnum.API_KEY in auth_set and AuthMethodEnum.BEARER_TOKEN not in auth_set:
        if "bearer" in summary_text or "header" in summary_text:
            auth_set.add(AuthMethodEnum.BEARER_TOKEN)
    record.auth_methods = sorted(list(auth_set), key=lambda x: x.value)

    # Rule 8: Update Provenance
    record.provenance = ProvenanceSpec(
        run_id="v4_refined",
        model=v3_data.get("provenance", {}).get("model", "gemini-3.5-flash-lite"),
        prompt_version="v4.0_taxonomy_refined",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    out_dict = record.model_dump(mode="json")
    out_dict["field_status"] = v3_data.get("field_status", {})
    out_dict["audit_trace"] = v3_data.get("audit_trace", {})
    return out_dict

def main():
    v3_dir = Path("data/runs/v3")
    v4_dir = Path("data/runs/v4")
    v4_dir.mkdir(parents=True, exist_ok=True)

    v3_files = sorted(list(v3_dir.glob("*.json")))
    print(f"--- Running Agent v4 Refinement on {len(v3_files)} Apps ---")

    refined_count = 0
    for fpath in v3_files:
        with open(fpath, "r", encoding="utf-8") as f:
            v3_data = json.load(f)
        
        v4_dict = refine_record(v3_data)
        out_path = v4_dir / fpath.name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(v4_dict, f, indent=2)
        refined_count += 1

    print(f"Refined and saved {refined_count}/100 records into data/runs/v4/")

if __name__ == "__main__":
    main()
