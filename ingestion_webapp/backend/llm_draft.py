"""
STEMMA Ingestion Webapp - Multi-Provider LLM Seam
Supports Google Antigravity/Gemini, OpenRouter, NVIDIA NIM, and OpenCode.
Fetch live free-tier models and generate structured STEMMA proposal artifacts.
"""
from __future__ import annotations

import json
import os
import re
from typing import Dict, Any, List, Optional
import requests

# Default API Keys loaded from workspace environment if available
ENV_KEYS = {}
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
if os.path.exists(ENV_FILE):
    try:
        with open(ENV_FILE, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    ENV_KEYS[k] = v
    except Exception:
        pass

def fetch_provider_models(provider: str, api_key: Optional[str] = None, free_only: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch available models for a given provider, filtering for FREE models when requested.
    """
    provider = (provider or "google").lower()
    
    if provider in ["google", "antigravity"]:
        return [
            {"id": "antigravity-gemini-3.7-flash", "name": "antigravity-gemini-3.7-flash (Free / Antigravity)", "free": True, "provider": "google"},
            {"id": "gemini-2.5-flash", "name": "gemini-2.5-flash (Google AI Free Tier)", "free": True, "provider": "google"},
            {"id": "gemini-1.5-flash", "name": "gemini-1.5-flash (Google AI Free Tier)", "free": True, "provider": "google"},
            {"id": "gemini-2.5-pro", "name": "gemini-2.5-pro (Google AI Free Tier)", "free": True, "provider": "google"},
        ]

    elif provider == "openrouter":
        effective_key = api_key or ENV_KEYS.get("OPENROUTER_API_KEY")
        headers = {}
        if effective_key:
            headers["Authorization"] = f"Bearer {effective_key}"
        try:
            r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=5)
            if r.status_code == 200:
                raw_models = r.json().get("data", [])
                models = []
                for m in raw_models:
                    m_id = m.get("id", "")
                    pricing = m.get("pricing", {})
                    is_free = ":free" in m_id or (float(pricing.get("prompt", 1)) == 0 and float(pricing.get("completion", 1)) == 0)
                    if free_only and not is_free:
                        continue
                    models.append({
                        "id": m_id,
                        "name": f"{m.get('name', m_id)} {'(Free)' if is_free else ''}".strip(),
                        "free": is_free,
                        "provider": "openrouter"
                    })
                if models:
                    return models
        except Exception as e:
            print(f"Error fetching OpenRouter models: {e}")

        # Fallback free OpenRouter models
        return [
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B Instruct (Free)", "free": True, "provider": "openrouter"},
            {"id": "deepseek/deepseek-r1:free", "name": "DeepSeek R1 (Free)", "free": True, "provider": "openrouter"},
            {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash Exp (Free)", "free": True, "provider": "openrouter"},
            {"id": "nvidia/nemotron-3.5-lightning:free", "name": "NVIDIA Nemotron 3.5 Lightning (Free)", "free": True, "provider": "openrouter"},
            {"id": "qwen/qwen-2.5-72b-instruct:free", "name": "Qwen 2.5 72B Instruct (Free)", "free": True, "provider": "openrouter"},
        ]

    elif provider == "nvidia":
        effective_key = api_key or ENV_KEYS.get("NVIDIA_NIM_API_KEY")
        headers = {}
        if effective_key:
            headers["Authorization"] = f"Bearer {effective_key}"
        try:
            r = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers, timeout=5)
            if r.status_code == 200:
                raw_models = r.json().get("data", [])
                models = []
                for m in raw_models:
                    m_id = m.get("id", "")
                    models.append({
                        "id": m_id,
                        "name": f"{m_id} (NVIDIA NIM)",
                        "free": True,
                        "provider": "nvidia"
                    })
                if models:
                    return models
        except Exception as e:
            print(f"Error fetching NVIDIA models: {e}")

        return [
            {"id": "meta/llama-3.3-70b-instruct", "name": "Meta Llama 3.3 70B Instruct (NVIDIA NIM)", "free": True, "provider": "nvidia"},
            {"id": "deepseek-ai/deepseek-r1", "name": "DeepSeek R1 (NVIDIA NIM)", "free": True, "provider": "nvidia"},
            {"id": "nvidia/llama-3.1-nemotron-70b-instruct", "name": "NVIDIA Nemotron 70B (NVIDIA NIM)", "free": True, "provider": "nvidia"},
        ]

    elif provider == "opencode":
        return [
            {"id": "opencode-zen", "name": "OpenCode Zen (Free)", "free": True, "provider": "opencode"},
            {"id": "opencode/free-coder", "name": "OpenCode Free Coder (Free)", "free": True, "provider": "opencode"},
        ]

    return []


def generate_llm_draft(
    blueprint: Any,
    data: Dict[str, Any],
    api_key: Optional[str] = None,
    model_name: str = "antigravity-gemini-3.7-flash",
    provider: str = "google",
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate structured STEMMA proposal draft using specified Provider & Model.
    """
    text = (data.get("_extracted_text") or data.get("text") or "").strip()
    if not text:
        text = "<No document text extracted>"

    provider = (provider or "google").lower()

    # Determine effective API Key
    effective_key = api_key
    if not effective_key:
        if provider in ["google", "antigravity"]:
            effective_key = ENV_KEYS.get("GEMINI_API_KEY") or ENV_KEYS.get("GOOGLE_API_KEY") or ENV_KEYS.get("ANTIGRAVITY_API_KEY")
        elif provider == "openrouter":
            effective_key = ENV_KEYS.get("OPENROUTER_API_KEY")
        elif provider == "nvidia":
            effective_key = ENV_KEYS.get("NVIDIA_NIM_API_KEY")
        elif provider == "opencode":
            effective_key = ENV_KEYS.get("OPENCODE_API_KEY")

    if not effective_key:
        return _deterministic_fallback(blueprint, text, data)

    prompt = f"""You are a STEMMA Canonical Knowledge Curator.
Analyze the scientific text below and extract a canonical STEM entity or assertion.

Text to Analyze:
\"\"\"
{text[:4000]}
\"\"\"

Output Format Requirement:
Return ONLY a valid JSON object matching the STEMMA Schema:
{{
  "id": "lhs:<domain>.<slug>",  // e.g. lhs:phys.doppler-effect, lhs:chem.catalysis, lhs:math.derivative
  "type": "concept", // concept, law, phenomenon, quantity, principle, theorem, structure
  "name": "Canonical Entity Name",
  "domain": "physics", // math, physics, chemistry, biology, earth-space, engineering, scientific-practice
  "status": "draft",
  "definition": "Rigorous 2-3 sentence scientific definition.",
  "provenance": {{
    "ai_drafted": true,
    "source": "{getattr(blueprint, 'source_ref', 'lhs:src.unknown')}",
    "reviewer": null,
    "reviewed_at": null
  }},
  "relationships": []
}}
"""

    try:
        # Provider 1: Google Antigravity / Gemini
        if provider in ["google", "antigravity"]:
            from google import genai
            from google.genai import types

            target_model = model_name
            if "3.7-flash" in model_name or "antigravity" in model_name:
                target_model = "gemini-2.5-flash"

            client = genai.Client(api_key=effective_key)
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            parsed = _extract_json(response.text or "")
            if parsed and isinstance(parsed, dict) and "id" in parsed:
                return parsed

        # Provider 2: OpenRouter
        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {effective_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name or "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                res_data = res.json()
                content = res_data["choices"][0]["message"]["content"]
                parsed = _extract_json(content)
                if parsed and isinstance(parsed, dict) and "id" in parsed:
                    return parsed

        # Provider 3: NVIDIA NIM
        elif provider == "nvidia":
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {effective_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name or "meta/llama-3.3-70b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                res_data = res.json()
                content = res_data["choices"][0]["message"]["content"]
                parsed = _extract_json(content)
                if parsed and isinstance(parsed, dict) and "id" in parsed:
                    return parsed

        # Provider 4: OpenCode
        elif provider == "opencode":
            url = "https://opencode.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {effective_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name or "opencode-zen",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                res_data = res.json()
                content = res_data["choices"][0]["message"]["content"]
                parsed = _extract_json(content)
                if parsed and isinstance(parsed, dict) and "id" in parsed:
                    return parsed

    except Exception as e:
        print(f"Provider '{provider}' generation error: {e}. Using fallback.")

    return _deterministic_fallback(blueprint, text, data)

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        match = re.search(r'(\{.*?\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None

def _deterministic_fallback(blueprint: Any, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
    bp = blueprint
    source_ref = getattr(bp, 'source_ref', 'lhs:src.unknown')
    raw_title = data.get('title') or 'concept'
    slug_name = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')

    return {
        "id": f"lhs:phys.{slug_name or 'concept'}",
        "type": "concept",
        "name": raw_title.title(),
        "domain": "physics",
        "status": "draft",
        "definition": text[:350] or "Extracted scientific concept text pending review.",
        "provenance": {
            "ai_drafted": False,
            "source": source_ref,
            "reviewer": None,
            "reviewed_at": None
        },
        "relationships": []
    }
