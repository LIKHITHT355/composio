"""
Stage 1: Entity & Official Domain Resolver
Disambiguates generic or homonymous app names (Front, Plain, Close, Grain, Consensus, Twenty).
Confirms canonical entity name, official domain, and one-liner.
"""

from typing import Dict, Any, Tuple
import re

# Known disambiguation mapping for homonymous apps
DISAMBIGUATION_MAP = {
    "front": {
        "official_domain": "front.com",
        "canonical_name": "Front",
        "one_liner": "Customer operations and collaborative email inbox platform.",
        "primary_docs": "https://dev.frontapp.com"
    },
    "plain": {
        "official_domain": "plain.com",
        "canonical_name": "Plain",
        "one_liner": "Modern B2B customer support platform built for engineering and product teams.",
        "primary_docs": "https://plain.com/docs"
    },
    "close": {
        "official_domain": "close.com",
        "canonical_name": "Close",
        "one_liner": "Inside sales CRM with integrated calling, SMS, and email automation.",
        "primary_docs": "https://developer.close.com"
    },
    "grain": {
        "official_domain": "grain.com",
        "canonical_name": "Grain",
        "one_liner": "AI meeting recorder and conversation intelligence platform.",
        "primary_docs": "https://grain.com"
    },
    "consensus": {
        "official_domain": "consensus.app",
        "canonical_name": "Consensus",
        "one_liner": "AI-powered academic search engine summarizing scientific research.",
        "primary_docs": "https://consensus.app"
    },
    "twenty": {
        "official_domain": "twenty.com",
        "canonical_name": "Twenty",
        "one_liner": "Modern open-source CRM alternative to Salesforce.",
        "primary_docs": "https://twenty.com/developers"
    },
    "sherlock": {
        "official_domain": "github.com/sherlock-project/sherlock",
        "canonical_name": "Sherlock",
        "one_liner": "Open-source command-line OSINT tool to hunt usernames across social platforms.",
        "primary_docs": "https://github.com/sherlock-project/sherlock"
    },
    "mermaid cli": {
        "official_domain": "github.com/mermaid-js/mermaid-cli",
        "canonical_name": "Mermaid CLI",
        "one_liner": "Command line interface for Mermaid diagram generation library.",
        "primary_docs": "https://github.com/mermaid-js/mermaid-cli"
    }
}

class EntityResolver:
    @staticmethod
    def resolve(app_name: str, category: str, hint: str) -> Dict[str, str]:
        app_key = app_name.strip().lower()
        if app_key in DISAMBIGUATION_MAP:
            mapping = DISAMBIGUATION_MAP[app_key]
            return {
                "app": mapping["canonical_name"],
                "official_domain": mapping["official_domain"],
                "one_liner": mapping["one_liner"],
                "primary_docs": mapping["primary_docs"],
                "resolved_source": "disambiguation_rule"
            }

        # Clean hint to extract domain
        raw_hint = hint.split()[0].strip()
        # Remove http/https
        clean_domain = re.sub(r"^https?://", "", raw_hint)
        # Take host part
        domain = clean_domain.split("/")[0]

        return {
            "app": app_name,
            "official_domain": domain,
            "one_liner": f"{app_name} software platform for {category.lower()}.",
            "primary_docs": f"https://{raw_hint}" if not raw_hint.startswith("http") else raw_hint,
            "resolved_source": "hint_extraction"
        }
