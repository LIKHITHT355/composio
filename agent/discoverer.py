"""
Stage 2: Targeted Multi-Field Discoverer
Executes targeted queries for:
- Authentication methods
- Credential gating & pricing
- API reference & OpenAPI
- MCP servers
- Composio toolkit catalog
"""

from typing import Dict, Any, List
from agent.search import SearchProvider

class FieldDiscoverer:
    def __init__(self, search_provider: SearchProvider):
        self.search = search_provider

    def discover(self, app_name: str, domain: str, hint: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs targeted queries for key fields and returns categorized snippets/URLs.
        """
        results = {}

        # 1. API Documentation & Style
        q_api = f"{app_name} site:{domain} API documentation developer reference"
        results["api"] = self.search.search_snippets(app_name, hint, query=q_api)

        # 2. Authentication methods
        q_auth = f"{app_name} API authentication OAuth2 API key Bearer token header"
        results["auth"] = self.search.search_snippets(app_name, hint, query=q_auth)

        # 3. Credential access & pricing gating
        q_gate = f"{app_name} API pricing developer access free trial paid plan required approval"
        results["gating"] = self.search.search_snippets(app_name, hint, query=q_gate)

        # 4. MCP Servers
        q_mcp = f"{app_name} model context protocol MCP server site:github.com"
        results["mcp"] = self.search.search_snippets(app_name, hint, query=q_mcp)

        # 5. Direct standard developer subdomains & paths
        subdomain_candidates = [
            f"https://developer.{domain}",
            f"https://docs.{domain}",
            f"https://{domain}/docs",
            f"https://{domain}/api",
            f"https://{domain}/developers"
        ]
        results["direct_candidates"] = [{"url": u, "title": f"{app_name} Developer Portal", "snippet": ""} for u in subdomain_candidates]

        return results
