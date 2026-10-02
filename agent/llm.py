"""
Deterministic LLM Client with disk caching, token tracking, and structured output.
Supports:
- Gemini (Google AI Studio REST)
- OpenAI
- Anthropic
- Groq (Ultra-fast, high limits: llama-3.3-70b-versatile, llama-3.1-8b-instant)
- Hugging Face (Inference API / Serverless Router)
- DeepSeek (deepseek-chat)
- OpenRouter (Unified router)
- Together AI
- xAI (Grok)
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

# OpenAI-compatible provider endpoints
OPENAI_COMPATIBLE_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "together": "https://api.together.xyz/v1/chat/completions",
    "xai": "https://api.x.ai/v1/chat/completions",
    "huggingface": "https://router.huggingface.co/hf-inference/v1/chat/completions",
}

class LLMClient:
    def __init__(self, cache_dir: str = "data/cache/llm"):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.fast_model = os.getenv("FAST_MODEL", "gemini-2.5-flash")
        self.strong_model = os.getenv("STRONG_MODEL", "gemini-2.5-pro")
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.hf_key = os.getenv("HUGGINGFACE_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.together_key = os.getenv("TOGETHER_API_KEY")
        self.xai_key = os.getenv("XAI_API_KEY")

        # Auto-detect provider if default is missing its key
        if self.provider == "gemini" and not self.gemini_key:
            if self.groq_key:
                self.provider = "groq"
                self.fast_model = "llama-3.3-70b-versatile"
            elif self.openai_key:
                self.provider = "openai"
                self.fast_model = "gpt-4o-mini"
            elif self.deepseek_key:
                self.provider = "deepseek"
                self.fast_model = "deepseek-chat"
            elif self.openrouter_key:
                self.provider = "openrouter"
                self.fast_model = "meta-llama/llama-3.3-70b-instruct"
            elif self.anthropic_key:
                self.provider = "anthropic"
                self.fast_model = "claude-3-5-haiku-20241022"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cumulative stats
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost_usd = 0.0

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        keys = {
            "gemini": self.gemini_key,
            "openai": self.openai_key,
            "anthropic": self.anthropic_key,
            "groq": self.groq_key,
            "huggingface": self.hf_key,
            "deepseek": self.deepseek_key,
            "openrouter": self.openrouter_key,
            "together": self.together_key,
            "xai": self.xai_key,
        }
        return keys.get(provider.lower())

    def has_valid_key(self) -> bool:
        return bool(self.get_api_key_for_provider(self.provider))

    def _get_cache_path(self, model: str, prompt: str) -> Path:
        key = f"{model}:{prompt}".encode("utf-8")
        h = hashlib.sha256(key).hexdigest()
        return self.cache_dir / f"{h}.json"

    def calculate_cost(self, model: str, prompt_toks: int, completion_toks: int) -> float:
        # Rates per million tokens
        m = model.lower()
        if "gemini" in m:
            rate_in, rate_out = 0.15 / 1_000_000, 0.60 / 1_000_000
        elif "groq" in m or "llama-3" in m:
            rate_in, rate_out = 0.05 / 1_000_000, 0.08 / 1_000_000
        elif "deepseek" in m:
            rate_in, rate_out = 0.14 / 1_000_000, 0.28 / 1_000_000
        elif "gpt-4o-mini" in m:
            rate_in, rate_out = 0.15 / 1_000_000, 0.60 / 1_000_000
        elif "claude-3-5-haiku" in m:
            rate_in, rate_out = 0.80 / 1_000_000, 4.00 / 1_000_000
        else:
            rate_in, rate_out = 0.20 / 1_000_000, 0.80 / 1_000_000
        return (prompt_toks * rate_in) + (completion_toks * rate_out)

    def generate_structured(self, prompt: str, system_prompt: str, json_schema: Dict[str, Any], model: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        chosen_model = model or self.fast_model
        cache_path = self._get_cache_path(chosen_model, f"{system_prompt}\n{prompt}")

        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                return cached["data"], cached["usage"]

        api_key = self.get_api_key_for_provider(self.provider)
        if not api_key:
            raise RuntimeError(f"Missing API key for provider '{self.provider}'. Set {self.provider.upper()}_API_KEY in .env.")

        start_time = time.time()
        raw_text = ""
        prompt_tokens = 0
        completion_tokens = 0

        if self.provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]}
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "responseMimeType": "application/json"
                }
            }
            for attempt in range(3):
                try:
                    with httpx.Client(timeout=45.0) as client:
                        resp = client.post(url, json=payload)
                        if resp.status_code == 200:
                            res_data = resp.json()
                            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                            usage = res_data.get("usageMetadata", {})
                            prompt_tokens = usage.get("promptTokenCount", len(prompt) // 4)
                            completion_tokens = usage.get("candidatesTokenCount", len(raw_text) // 4)
                            break
                        elif resp.status_code == 429:
                            time.sleep(2 * (attempt + 1))
                            if attempt == 2:
                                raise RuntimeError(f"Gemini API rate limit (429): {resp.text}")
                        else:
                            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
                except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError) as net_err:
                    if attempt == 2:
                        raise net_err
                    time.sleep(2 * (attempt + 1))

        elif self.provider in OPENAI_COMPATIBLE_ENDPOINTS:
            url = OPENAI_COMPATIBLE_ENDPOINTS[self.provider]
            headers = {"Authorization": f"Bearer {api_key}"}
            if self.provider == "openrouter":
                headers["HTTP-Referer"] = "https://composio.dev"
                headers["X-Title"] = "Composio Research Agent"

            payload = {
                "model": chosen_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            with httpx.Client(timeout=45.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise RuntimeError(f"{self.provider} API error ({resp.status_code}): {resp.text}")
                res_data = resp.json()
                raw_text = res_data["choices"][0]["message"]["content"]
                usage = res_data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", len(prompt) // 4)
                completion_tokens = usage.get("completion_tokens", len(raw_text) // 4)

        elif self.provider == "anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": chosen_model,
                "system": system_prompt + "\n\nCRITICAL: Output ONLY a valid JSON object matching the requested schema. No markdown fences, no conversational text.",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
                "temperature": 0.0
            }
            with httpx.Client(timeout=45.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise RuntimeError(f"Anthropic API error ({resp.status_code}): {resp.text}")
                res_data = resp.json()
                raw_text = res_data["content"][0]["text"]
                # Clean any markdown fences if present
                clean = raw_text.strip()
                if clean.startswith("```json"):
                    clean = clean[7:]
                if clean.startswith("```"):
                    clean = clean[3:]
                if clean.endswith("```"):
                    clean = clean[:-3]
                raw_text = clean.strip()
                usage = res_data.get("usage", {})
                prompt_tokens = usage.get("input_tokens", len(prompt) // 4)
                completion_tokens = usage.get("output_tokens", len(raw_text) // 4)

        duration = time.time() - start_time
        
        # Robust JSON extraction
        try:
            parsed_data = json.loads(raw_text)
        except Exception:
            start_idx = raw_text.find("{")
            end_idx = raw_text.rfind("}")
            if start_idx != -1 and end_idx != -1:
                parsed_data = json.loads(raw_text[start_idx:end_idx+1])
            else:
                raise RuntimeError(f"Failed to parse JSON response: {raw_text[:200]}")

        cost = self.calculate_cost(chosen_model, prompt_tokens, completion_tokens)

        usage_meta = {
            "model": chosen_model,
            "provider": self.provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost,
            "duration_sec": round(duration, 2)
        }

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"data": parsed_data, "usage": usage_meta}, f, indent=2)

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost_usd += cost

        return parsed_data, usage_meta
