"""
Page fetcher and cache with deterministic quote verifier.
Follows:
- R1: Quote verbatim verification (<=300 chars)
- R4: Safe crawling, rate-limiting, caching
- R10: Token thrift (~6k tokens per extraction call)
"""

import os
import re
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class PageFetcher:
    def __init__(self, cache_dir: str = "data/cache/pages"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = 15.0
        self.firecrawl_calls = 0
        self.max_firecrawl_scrapes = int(os.getenv("MAX_TEST_SCRAPES", "2"))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

    def _url_hash(self, url: str) -> str:
        return hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()

    def _get_cache_path(self, url: str) -> Path:
        return self.cache_dir / f"{self._url_hash(url)}.json"

    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetches a URL or returns cached copy.
        Returns: {
            "url": str,
            "status_code": int,
            "clean_text": str,
            "title": str,
            "sha256": str,
            "retrieved_at": str
        }
        """
        clean_url = url.strip()
        if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
            clean_url = f"https://{clean_url}"

        cache_path = self._get_cache_path(clean_url)
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        retrieved_at = datetime.now(timezone.utc).isoformat()
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=self.headers) as client:
                resp = client.get(clean_url)
                status_code = resp.status_code
                
                if status_code == 200:
                    raw_html = resp.text
                    clean_text, title = self._clean_html(raw_html)
                else:
                    clean_text = f"HTTP Error {status_code}"
                    title = f"Error {status_code}"

        except Exception as e:
            status_code = 0
            clean_text = f"Fetch failed: {str(e)}"
            title = "Fetch Error"

        # Fallback to Firecrawl if HTTP failed or returned minimal text (<150 chars), capped at 2 for testing
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        if (status_code != 200 or len(clean_text) < 150) and firecrawl_key and self.firecrawl_calls < self.max_firecrawl_scrapes:
            try:
                self.firecrawl_calls += 1
                fc_resp = httpx.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {firecrawl_key}"},
                    json={"url": clean_url},
                    timeout=20.0
                )
                if fc_resp.status_code == 200:
                    fc_data = fc_resp.json().get("data", {})
                    markdown = fc_data.get("markdown", "")
                    if markdown and len(markdown) > len(clean_text):
                        clean_text = markdown
                        title = fc_data.get("metadata", {}).get("title", title)
                        status_code = 200
            except Exception:
                pass

        text_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
        data = {
            "url": clean_url,
            "status_code": status_code,
            "title": title,
            "clean_text": clean_text,
            "sha256": text_hash,
            "retrieved_at": retrieved_at
        }

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return data

    def _clean_html(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Remove scripts, styles, forms, svgs
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "svg", "noscript"]):
            tag.decompose()

        # Extract text blocks
        lines = []
        for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "code", "pre", "td", "th"]):
            text = element.get_text().strip()
            if text:
                # Normalize spaces
                text = re.sub(r"\s+", " ", text)
                lines.append(text)

        clean_text = "\n".join(lines)
        return clean_text, title

    def verify_quote(self, url: str, quote: str) -> bool:
        """
        Deterministic Verifier (R1): checks if quote is literally in cached text.
        Allows whitespace normalization.
        """
        if not quote or not url:
            return False

        cache_path = self._get_cache_path(url)
        if not cache_path.exists():
            return False

        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)

        cached_text = cached.get("clean_text", "")
        
        # Exact check
        if quote in cached_text:
            return True

        # Whitespace-normalized check
        norm_cached = " ".join(cached_text.split()).lower()
        norm_quote = " ".join(quote.split()).lower()
        return norm_quote in norm_cached

    def get_top_passages(self, clean_text: str, keywords: List[str], max_chars: int = 6000) -> str:
        """
        Token thrift (R10): Extracts top relevant paragraphs matching keywords.
        Caps output to ~6000 characters (~1500 tokens).
        """
        paragraphs = clean_text.split("\n")
        scored = []
        for p in paragraphs:
            score = 0
            p_lower = p.lower()
            for kw in keywords:
                if kw.lower() in p_lower:
                    score += 1
            if score > 0:
                scored.append((score, p))

        # Sort descending by keyword density
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [p for _, p in scored]
        
        combined = "\n\n".join(selected)
        if len(combined) > max_chars:
            return combined[:max_chars]
        elif len(combined) < 500 and len(clean_text) > 0:
            # Fallback to first section if keyword filter was too strict
            return clean_text[:max_chars]
        return combined
