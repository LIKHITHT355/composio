"""
Deterministic LLM Client with disk caching, token tracking, and structured output.
Supports Gemini (Google AI Studio REST), OpenAI, and Anthropic.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, cache_dir: str = "data/cache/llm"):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.fast_model = os.getenv("FAST_MODEL", "gemini-2.5-flash")
        self.strong_model = os.getenv("STRONG_MODEL", "gemini-2.5-pro")
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        # Auto-detect provider if default is missing its key
        if self.provider == "gemini" and not self.gemini_key:
            if self.openai_key:
                self.provider = "openai"
                self.fast_model = "gpt-4o-mini"
            elif self.anthropic_key:
                self.provider = "anthropic"
                self.fast_model = "claude-3-5-haiku-20241022"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cumulative stats
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0

    def has_valid_key(self) -> bool:
        if self.provider == "gemini":
            return bool(self.gemini_key)
        elif self.provider == "openai":
            return bool(self.openai_key)
        elif self.provider == "anthropic":
            return bool(self.anthropic_key)
        return False

    def _get_cache_path(self, model: str, prompt: str) -> Path:
        key = f"{model}:{prompt}".encode("utf-8")
        h = hashlib.sha256(key).hexdigest()
        return self.cache_dir / f"{h}.json"

    def calculate_cost(self, model: str, prompt_toks: int, completion_toks: int) -> float:
        # Standard pricing per million tokens
        if "gemini" in model.lower():
            rate_in = 0.15 / 1_000_000
            rate_out = 0.60 / 1_000_000
        elif "gpt-4o-mini" in model.lower():
            rate_in = 0.15 / 1_000_000
            rate_out = 0.60 / 1_000_000
        elif "claude-3-5-haiku" in model.lower():
            rate_in = 0.80 / 1_000_000
            rate_out = 4.00 / 1_000_000
        else:
            rate_in = 0.50 / 1_000_000
            rate_out = 1.50 / 1_000_000
        return (prompt_toks * rate_in) + (completion_toks * rate_out)

    def generate_structured(self, prompt: str, system_prompt: str, json_schema: Dict[str, Any], model: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Executes structured JSON completion with disk caching and token tracking.
        Returns: (parsed_json_dict, usage_metadata)
        """
        chosen_model = model or self.fast_model
        cache_path = self._get_cache_path(chosen_model, f"{system_prompt}\n{prompt}")

        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                return cached["data"], cached["usage"]

        if not self.has_valid_key():
            raise RuntimeError(f"Missing API key for provider '{self.provider}'. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env.")

        start_time = time.time()
        raw_text = ""
        prompt_tokens = 0
        completion_tokens = 0

        if self.provider == "gemini":
            # Gemini v1beta REST API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]}
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "responseMimeType": "application/json"
                }
            }
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code != 200:
                    raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
                res_data = resp.json()
                raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                usage = res_data.get("usageMetadata", {})
                prompt_tokens = usage.get("promptTokenCount", len(prompt) // 4)
                completion_tokens = usage.get("candidatesTokenCount", len(raw_text) // 4)

        elif self.provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}"}
            payload = {
                "model": chosen_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise RuntimeError(f"OpenAI API error ({resp.status_code}): {resp.text}")
                res_data = resp.json()
                raw_text = res_data["choices"][0]["message"]["content"]
                usage = res_data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", len(prompt) // 4)
                completion_tokens = usage.get("completion_tokens", len(raw_text) // 4)

        duration = time.time() - start_time
        parsed_data = json.loads(raw_text)
        cost = self.calculate_cost(chosen_model, prompt_tokens, completion_tokens)

        usage_meta = {
            "model": chosen_model,
            "provider": self.provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost,
            "duration_sec": round(duration, 2)
        }

        # Save to disk cache
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"data": parsed_data, "usage": usage_meta}, f, indent=2)

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost_usd += cost

        return parsed_data, usage_meta
