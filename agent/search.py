"""
Pluggable search module for App Buildability Agent.
Supports:
1. Composio search action (if COMPOSIO_API_KEY configured)
2. Tavily API (if TAVILY_API_KEY configured)
3. SerpAPI (if SERPAPI_API_KEY configured)
4. Direct Hint/Domain Snippet fetcher (zero-credential fallback)
"""

import os
import re
import httpx
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class SearchProvider:
    def __init__(self):
        self.composio_key = os.getenv("COMPOSIO_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.timeout = 10.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def search_snippets(self, app_name: str, hint: str, query: str = None) -> List[Dict[str, str]]:
        """
        Returns top snippets: [{'title': ..., 'snippet': ..., 'url': ...}]
        """
        # 1. Try Composio Search if available
        if self.composio_key:
            try:
                from composio import Composio, Action
                client = Composio(api_key=self.composio_key)
                # Attempt search action execution
                res = client.actions.execute(action=Action.TAVILY_SEARCH, params={"query": query or f"{app_name} API documentation developer"})
                if res and isinstance(res, dict) and "data" in res:
                    snippets = []
                    for item in res["data"].get("results", [])[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("content", "")[:300],
                            "url": item.get("url", "")
                        })
                    if snippets:
                        return snippets
            except Exception:
                pass

        # 2. Try Tavily directly
        if self.tavily_key:
            try:
                resp = httpx.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.tavily_key, "query": query or f"{app_name} API developer docs auth", "max_results": 5},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return [
                        {
                            "title": item.get("title", ""),
                            "snippet": item.get("content", "")[:300],
                            "url": item.get("url", "")
                        }
                        for item in data.get("results", [])
                    ]
            except Exception:
                pass

        # 3. Direct domain fallback using the hint
        return self._fallback_hint_snippets(app_name, hint)

    def _fallback_hint_snippets(self, app_name: str, hint: str) -> List[Dict[str, str]]:
        """Zero-credential fallback: fetches public meta tags and headlines from hint domain."""
        snippets = []
        raw_url = hint.split()[0].strip() if hint else ""
        if not raw_url.startswith("http"):
            target_url = f"https://{raw_url}"
        else:
            target_url = raw_url

        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=self.headers) as client:
                resp = client.get(target_url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    title = soup.title.string.strip() if soup.title and soup.title.string else app_name
                    
                    meta_desc = ""
                    for m in soup.find_all("meta"):
                        if m.get("name", "").lower() in ["description", "og:description", "twitter:description"]:
                            meta_desc = m.get("content", "").strip()
                            if meta_desc:
                                break
                    
                    # Extract sample paragraph or heading
                    h_text = ""
                    headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "p"]) if len(h.get_text().strip()) > 30]
                    if headings:
                        h_text = " | ".join(headings[:2])
                        
                    content_snippet = (meta_desc + " " + h_text).strip()[:300]
                    snippets.append({
                        "title": title[:100],
                        "snippet": content_snippet or f"{app_name} developer resources and portal",
                        "url": str(resp.url)
                    })
        except Exception as e:
            snippets.append({
                "title": f"{app_name} Reference",
                "snippet": f"Official domain: {hint}",
                "url": target_url
            })

        return snippets
