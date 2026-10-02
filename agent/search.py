"""
Pluggable search module for App Buildability Agent with local caching.
Supports:
1. Brave Search API (BRAVE_API_KEY - 2,000 free queries/mo)
2. Serper.dev (SERPER_API_KEY - 2,500 free Google search queries)
3. Exa.ai (EXA_API_KEY - 1,000 free neural search queries)
4. SerpAPI (SERPAPI_API_KEY)
5. Tavily API (TAVILY_API_KEY)
6. Composio search action (COMPOSIO_API_KEY)
7. Direct Hint/Domain Snippet fetcher (zero-credential fallback)
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class SearchProvider:
    def __init__(self, cache_dir: str = "data/cache/search"):
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.exa_key = os.getenv("EXA_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.composio_key = os.getenv("COMPOSIO_API_KEY")
        
        self.timeout = 15.0
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _get_cache_path(self, query: str) -> Path:
        h = hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()
        return self.cache_dir / f"{h}.json"

    def search_snippets(self, app_name: str, hint: str, query: str = None) -> List[Dict[str, str]]:
        search_query = query or f"{app_name} API developer documentation authentication"
        cache_path = self._get_cache_path(search_query)

        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        snippets = []

        # 1. Try Brave Search (2,000 free monthly queries)
        if self.brave_key:
            try:
                resp = httpx.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={"X-Subscription-Token": self.brave_key, "Accept": "application/json"},
                    params={"q": search_query, "count": 5},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    web_results = data.get("web", {}).get("results", [])
                    for item in web_results[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("description", "")[:300],
                            "url": item.get("url", "")
                        })
                    if snippets:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(snippets, f, indent=2)
                        return snippets
            except Exception:
                pass

        # 2. Try Serper.dev (2,500 free Google queries)
        if self.serper_key:
            try:
                resp = httpx.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": self.serper_key, "Content-Type": "application/json"},
                    json={"q": search_query, "num": 5},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("organic", [])[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", "")[:300],
                            "url": item.get("link", "")
                        })
                    if snippets:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(snippets, f, indent=2)
                        return snippets
            except Exception:
                pass

        # 3. Try Exa.ai (1,000 free queries)
        if self.exa_key:
            try:
                resp = httpx.post(
                    "https://api.exa.ai/search",
                    headers={"x-api-key": self.exa_key, "Content-Type": "application/json"},
                    json={"query": search_query, "numResults": 5, "useAutoprompt": True},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", [])[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": (item.get("text", "") or item.get("title", ""))[:300],
                            "url": item.get("url", "")
                        })
                    if snippets:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(snippets, f, indent=2)
                        return snippets
            except Exception:
                pass

        # 4. Try SerpAPI if available
        if self.serpapi_key:
            try:
                resp = httpx.get(
                    "https://serpapi.com/search.json",
                    params={
                        "q": search_query,
                        "api_key": self.serpapi_key,
                        "num": 5,
                        "engine": "google"
                    },
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    organic = data.get("organic_results", [])
                    for item in organic[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", "")[:300],
                            "url": item.get("link", "")
                        })
                    if snippets:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(snippets, f, indent=2)
                        return snippets
            except Exception:
                pass

        # 5. Try Tavily directly
        if self.tavily_key:
            try:
                resp = httpx.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.tavily_key, "query": search_query, "max_results": 5},
                    timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", [])[:5]:
                        snippets.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("content", "")[:300],
                            "url": item.get("url", "")
                        })
                    if snippets:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(snippets, f, indent=2)
                        return snippets
            except Exception:
                pass

        # 6. Direct domain fallback using the hint
        snippets = self._fallback_hint_snippets(app_name, hint)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2)
        return snippets

    def _fallback_hint_snippets(self, app_name: str, hint: str) -> List[Dict[str, str]]:
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
                    
                    headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "p"]) if len(h.get_text().strip()) > 30]
                    h_text = " | ".join(headings[:2]) if headings else ""
                        
                    content_snippet = (meta_desc + " " + h_text).strip()[:300]
                    snippets.append({
                        "title": title[:100],
                        "snippet": content_snippet or f"{app_name} developer resources and portal",
                        "url": str(resp.url)
                    })
        except Exception:
            snippets.append({
                "title": f"{app_name} Reference",
                "snippet": f"Official domain: {hint}",
                "url": target_url
            })

        return snippets
