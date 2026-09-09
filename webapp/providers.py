#!/usr/bin/env python3
"""STEMMA webapp provider abstraction.

Every Draft backend is a *provider*. A provider is the single seam through which
the webapp asks a model/agent to produce schema-shaped candidates; no provider
is allowed to write to content/, connections/, or sources/.

The design honours the entitlement boundary:

* ``antigravity``       — official Google Antigravity local agent. It uses the
                         Antigravity SDK (``google.antigravity``) when installed
                         and otherwise shells out to the official Antigravity
                         CLI (``agy``). Authentication is the *local* Google AI
                         Pro/Ultra/Antigravity session held by that SDK/CLI. No
                         Gemini API key and no third-party client credential is
                         invented; if the SDK/CLI is not authenticated, the
                         provider reports that instead of silently switching to
                         a paid API key.
* ``gemini_api``        — official Gemini Developer API (separate entitlement;
                         requires an AI Studio/GenAI ``AIza…`` key).
* ``vertex_ai``         — official Vertex AI (separate entitlement; GCP project
                         + location + ADC, or Vertex API key).
* ``openai_compatible`` — any OpenAI-compatible endpoint. This is *not* an
                         Antigravity entitlement path; include it only for a
                         community bridge/tunnel you run yourself.

The registry is deliberately small and deterministic so tests can assert the
contract without network or credentials.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

SYSTEM_DRAFT_NOTE = "You produce only valid JSON proposal payloads for STEMMA."

ALIASES = {
    "google": "gemini_api",
    "openai": "openai_compatible",
    "antigravity_harness": "openai_compatible",
}

# Canonical provider ids. ``aliases`` above are accepted by save_llm_config but
# are canonicalized before persistence so a future reader never has to guess.
PROVIDER_IDS = ("antigravity", "gemini_api", "vertex_ai", "openai_compatible")


class ProviderError(ValueError):
    """A provider was misconfigured or returned an unusable result."""


class ProviderNotConfigured(ProviderError):
    """No usable provider/credentials are available."""


@dataclass(frozen=True)
class ProviderSpec:
    id: str
    label: str
    needs_base_url: bool = False
    needs_api_key: bool = False
    needs_model: bool = True
    defaults: dict = None  # type: ignore[assignment]
    hint: str = ""

    def __post_init__(self) -> None:
        if self.defaults is None:
            object.__setattr__(self, "defaults", {})


SPECS: dict[str, ProviderSpec] = {
    "antigravity": ProviderSpec(
        id="antigravity",
        label="Antigravity (official local agent: SDK then CLI)",
        needs_base_url=False,
        needs_api_key=False,
        needs_model=False,
        defaults={"base_url": "", "model": "", "transport": "auto"},
        hint=(
            "Uses your locally signed-in Google AI Pro / Antigravity session. "
            "Tries the official Antigravity SDK, then the official agy CLI. "
            "No Gemini API key is used, and no third-party client credential is "
            "invented. Run `agy` once (or install google.antigravity) on the "
            "machine that hosts the webapp server, then press Load models."
        ),
    ),
    "gemini_api": ProviderSpec(
        id="gemini_api",
        label="Gemini API (separate key entitlement)",
        needs_base_url=True,
        needs_api_key=True,
        needs_model=True,
        defaults={"base_url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-3-pro-preview"},
        hint="Official Gemini Developer API. Keys start with AIza… from Google AI Studio / GenAI. Separate from Antigravity entitlements.",
    ),
    "vertex_ai": ProviderSpec(
        id="vertex_ai",
        label="Vertex AI (separate GCP entitlement)",
        needs_base_url=False,
        needs_api_key=False,
        needs_model=True,
        defaults={"model": "gemini-2.5-pro", "project": "", "location": "us-central1"},
        hint="Official Vertex AI. Configure project + location and use Application Default Credentials (or a Vertex key) in the environment that runs the webapp server.",
    ),
    "openai_compatible": ProviderSpec(
        id="openai_compatible",
        label="OpenAI-compatible (custom bridge/tunnel)",
        needs_base_url=True,
        needs_api_key=True,
        needs_model=True,
        defaults={"base_url": "http://127.0.0.1:6012/v1", "model": "gemini-3-pro"},
        hint="Community harness/bridge or any OpenAI-compatible endpoint. NOT an Antigravity/Google AI Pro entitlement path.",
    ),
}

# Keep the old ids working in config files + tests without ambiguity.
for _alias, _canonical in ALIASES.items():
    if _alias not in SPECS:
        SPECS[_alias] = SPECS[_canonical]


def canonical_provider(provider: str | None) -> str:
    p = (provider or "").strip().lower()
    return ALIASES.get(p, p if p in PROVIDER_IDS else "")


def spec(provider: str | None) -> ProviderSpec:
    cid = canonical_provider(provider)
    if not cid:
        raise ProviderError("unknown provider: " + str(provider))
    return SPECS[cid]


def _agy_which() -> str | None:
    return shutil.which("agy")


def _sdk_importable() -> bool:
    try:
        import google.antigravity  # noqa: F401
        return True
    except Exception:  # noqa: BLE001 - optional backend
        return False


def availability(provider: str | None, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Describe whether a provider can be used without making a network call."""
    cid = canonical_provider(provider)
    cfg = config or {}
    if cid == "antigravity":
        if _sdk_importable():
            return {"ok": True, "mechanism": "antigravity-sdk", "message": "Antigravity SDK installed."}
        if _agy_which():
            return {"ok": True, "mechanism": "antigravity-cli", "message": "Antigravity CLI (agy) found."}
        return {"ok": False, "mechanism": "",
                "message": "Antigravity local agent not available. Install the official Antigravity CLI "
                           "(`curl -fsSL https://antigravity.google/cli/install.sh | bash`) or the "
                           "Antigravity SDK (`pip install google-antigravity`) on the host running the webapp "}
    if cid == "gemini_api":
        if not (cfg.get("base_url") and cfg.get("model") and cfg.get("api_key")):
            return {"ok": False, "mechanism": "gemini-api",
                    "message": "Gemini API needs base_url, model, and an AIza… API key."}
        return {"ok": True, "mechanism": "gemini-api", "message": "Gemini API configuration present."}
    if cid == "vertex_ai":
        try:
            import google.genai  # noqa: F401
        except Exception:  # noqa: BLE001
            return {"ok": False, "mechanism": "vertex-ai",
                    "message": "Vertex AI needs the 'google-genai' SDK (`pip install google-genai`)."}
        if not (cfg.get("model") and (cfg.get("project") or cfg.get("api_key"))):
            return {"ok": False, "mechanism": "vertex-ai",
                    "message": "Vertex AI needs a model id and a GCP project (or a Vertex API key)."}
        return {"ok": True, "mechanism": "vertex-ai", "message": "Vertex AI SDK present and config complete."}
    if cid == "openai_compatible":
        if not (cfg.get("base_url") and cfg.get("model") and cfg.get("api_key")):
            return {"ok": False, "mechanism": "openai-compatible",
                    "message": "OpenAI-compatible provider needs base_url, model, and API key."}
        return {"ok": True, "mechanism": "openai-compatible", "message": "OpenAI-compatible configuration present."}
    return {"ok": False, "mechanism": "", "message": "unknown provider"}


def configured(config: dict[str, Any] | None) -> bool:
    av = availability((config or {}).get("provider") or "", config)
    return bool(av.get("ok"))


# --------------------------------------------------------------------------- #
# Shared HTTP + JSON helpers
# --------------------------------------------------------------------------- #

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def json_from_content(content: Any, *, label: str = "provider response") -> dict[str, Any]:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise ProviderError(f"{label} returned a non-JSON object: {type(content).__name__}")
    text = _strip_fences(content)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"{label} returned non-JSON: {text[:300]}") from exc
    if not isinstance(parsed, dict):
        raise ProviderError(f"{label} returned JSON that is not an object: {text[:200]}")
    return parsed


def _extract_chat_text(obj: Any) -> str:
    """Extract a plain-text response from common provider response shapes."""
    if isinstance(obj, str):
        return obj
    if not isinstance(obj, dict):
        return json.dumps(obj)
    for key in ("response", "text", "output", "content"):
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val
        if isinstance(val, dict) and val.get("text"):
            return str(val["text"])
    # OpenAI-compatible payloads.
    try:
        return obj["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    # Gemini REST payloads.
    try:
        parts = obj["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    except (KeyError, IndexError, TypeError, AttributeError):
        pass
    return json.dumps(obj)


def _openai_chat(config: dict[str, Any], prompt: str) -> dict[str, Any]:
    import urllib.error
    import urllib.request
    url = f"{str(config['base_url']).rstrip('/')}/chat/completions"
    body_payload: dict[str, Any] = {
        "model": config.get("model") or "",
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_DRAFT_NOTE},
            {"role": "user", "content": prompt},
        ],
    }
    # Only official OpenAI guarantees json_object; local bridges commonly reject it.
    if canonical_provider(config.get("provider")) == "openai_compatible" and "api.openai.com" in str(config.get("base_url")):
        body_payload["response_format"] = {"type": "json_object"}
    url = url
    request = urllib.request.Request(url, data=json.dumps(body_payload).encode("utf-8"), method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {config.get('api_key', '')}")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"OpenAI-compatible provider returned HTTP {exc.code}: {exc.read().decode('utf-8')[:300]}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"OpenAI-compatible provider request failed: {exc}") from exc
    payload = json.loads(raw)
    return json_from_content(_extract_chat_text(payload), label="OpenAI-compatible provider")


def _gemini_chat(config: dict[str, Any], prompt: str) -> dict[str, Any]:
    import urllib.error
    import urllib.request
    url = f"{str(config['base_url']).rstrip('/')}/models/{config.get('model')}:generateContent"
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": f"{SYSTEM_DRAFT_NOTE} Return only a JSON object; no markdown fences."}]},
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("x-goog-api-key", config.get("api_key", ""))
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"Gemini API returned HTTP {exc.code}: {exc.read().decode('utf-8')[:300]}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"Gemini API request failed: {exc}") from exc
    payload = json.loads(raw)
    return json_from_content(_extract_chat_text(payload), label="Gemini API")


def _vertex_chat(config: dict[str, Any], prompt: str) -> dict[str, Any]:
    try:
        from google import genai
    except Exception as exc:  # noqa: BLE001
        raise ProviderNotConfigured("Vertex AI provider requires the 'google-genai' package.") from exc
    try:
        client_kwargs: dict[str, Any] = {"vertex": True}
        if config.get("project"):
            client_kwargs["project"] = config["project"]
        if config.get("location"):
            client_kwargs["location"] = config["location"]
        client = genai.Client(**client_kwargs)
        response = client.models.generate_content(
            model=config.get("model") or "",
            contents=f"{SYSTEM_DRAFT_NOTE}\n\n{prompt}",
        )
        return json_from_content(_extract_chat_text(getattr(response, "text", None) or response),
                                 label="Vertex AI")
    except ProviderError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"Vertex AI request failed: {exc}") from exc


# --------------------------------------------------------------------------- #
# Antigravity SDK + CLI adapters
# --------------------------------------------------------------------------- #

def _antigravity_sdk_chat(config: dict[str, Any], prompt: str) -> str:
    try:
        from google.antigravity import Agent, LocalAgentConfig
    except Exception as exc:  # noqa: BLE001
        raise ProviderNotConfigured("Antigravity SDK not installed.") from exc
    try:
        kwargs: dict[str, Any] = {"system_instructions": SYSTEM_DRAFT_NOTE}
        # Optional Vertex/enterprise mode; otherwise the SDK uses the local
        # Google AI Pro / Antigravity session (no Gemini API key).
        if config.get("project"):
            kwargs["project"] = config["project"]
        if config.get("location"):
            kwargs["location"] = config["location"]
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        agent_config = LocalAgentConfig(**kwargs)
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"Antigravity SDK config failed: {exc}") from exc
    try:
        async def run() -> str:
            async with Agent(agent_config) as agent:
                response = await agent.chat(prompt)
                return await response.text()
        return _run_async(run())
    except ProviderError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"Antigravity SDK chat failed: {exc}") from exc


def agy_command(config: dict[str, Any], prompt: str, *, output_format: str = "json",
                timeout: str = "10m") -> list[str]:
    cmd = ["agy", "-p", prompt, "--output-format", output_format, "--print-timeout", timeout]
    model = config.get("model") or ""
    if model:
        cmd += ["--model", model]
    effort = config.get("effort") or ""
    if effort:
        cmd += ["--effort", effort]
    agent = config.get("agent") or ""
    if agent:
        cmd += ["--agent", agent]
    return cmd


def _antigravity_cli_chat(config: dict[str, Any], prompt: str) -> str:
    exe = _agy_which()
    if not exe:
        raise ProviderNotConfigured("Antigravity CLI (agy) not found in PATH.")
    cmd = agy_command(config, prompt)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired as exc:
        raise ProviderError("Antigravity CLI timed out (increase --print-timeout).") from exc
    except OSError as exc:
        raise ProviderError(f"Antigravity CLI failed to start: {exc}") from exc
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip()[-400:]
        raise ProviderError(f"Antigravity CLI returned {result.returncode}: {tail}")
    out = (result.stdout or "").strip()
    if not out:
        raise ProviderError("Antigravity CLI returned no response.")
    try:
        parsed = json.loads(out)
        return _extract_chat_text(parsed)
    except json.JSONDecodeError:
        return out


def _antigravity_cli_models(config: dict[str, Any]) -> list[str]:
    exe = _agy_which()
    if not exe:
        raise ProviderNotConfigured("Antigravity CLI (agy) not found in PATH.")
    try:
        result = subprocess.run([exe, "models"], capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"agy models failed: {exc}") from exc
    if result.returncode != 0:
        raise ProviderError(f"agy models returned {result.returncode}: {(result.stderr or '')[:200]}")
    ids: list[str] = []
    for raw in (result.stdout or "").splitlines():
        line = raw.strip()
        if not line or line.startswith(("Name", "Model", "──", "Usage", "Featured")):
            continue
        # Likely "display name | slug | notes"; keep a numeric slug if present.
        columns = [c.strip() for c in line.split("|")]
        ids.extend(columns)
    return sorted({x for x in ids if x and " " not in x})


def _antigravity_unknown_models() -> list[str]:
    # Listed only as a hint if `agy models` cannot run; official IDs change over time.
    return sorted({
        "gemini-3-pro", "gemini-3-pro-high", "gemini-3-pro-low",
        "gemini-3-flash", "gemini-3.1-pro-high", "gemini-3.1-pro-low",
        "claude-opus-4-6-thinking", "claude-sonnet-4-6",
    })


def _antigravity_transport(config: dict[str, Any]) -> str:
    transport = (config.get("transport") or "").lower()
    if transport == "sdk" and _sdk_importable():
        return "sdk"
    if transport == "cli" and _agy_which():
        return "cli"
    if _sdk_importable():
        return "sdk"
    if _agy_which():
        return "cli"
    raise ProviderNotConfigured(
        "Antigravity local agent unavailable. Install the official Antigravity SDK "
        "or CLI on the host running this webapp server."
    )


def _run_async(coro):
    import asyncio
    try:
        return asyncio.run(coro)
    except RuntimeError:  # already inside an event loop (rare in this server)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)


def _antigravity_chat(config: dict[str, Any], prompt: str) -> dict[str, Any]:
    transport = _antigravity_transport(config)
    try:
        if transport == "sdk":
            text = _antigravity_sdk_chat(config, prompt)
        else:
            text = _antigravity_cli_chat(config, prompt)
    except ProviderError:
        raise
    return json_from_content(_extract_chat_text(text) if isinstance(text, str) else text,
                             label="Antigravity agent")


def _antigravity_probe(config: dict[str, Any]) -> dict[str, Any]:
    av = availability("antigravity", config)
    if not av.get("ok"):
        return {"ok": False, "provider": "antigravity", "message": av["message"]}
    transport = _antigravity_transport(config)
    return {"ok": True, "provider": "antigravity", "mechanism": transport,
            "message": f"Antigravity local agent available via {'SDK' if transport == 'sdk' else 'CLI'}."
                       " Press Load models to select an Antigravity model, then Draft."}


# --------------------------------------------------------------------------- #
# Public registry API
# --------------------------------------------------------------------------- #

def probe(config: dict[str, Any]) -> dict[str, Any]:
    cid = canonical_provider(config.get("provider") or "")
    if cid == "antigravity":
        return _antigravity_probe(config)
    av = availability(cid, config)
    if not av.get("ok"):
        return {"ok": False, "provider": cid, "message": av["message"]}
    # Reuse chat with a very small probe so real credential errors surface.
    try:
        chat(config, 'Return ONLY this JSON object: {"candidates": []}')
    except ProviderError as exc:
        return {"ok": False, "provider": cid, "message": str(exc)}
    return {"ok": True, "provider": cid, "message": av["message"]}


def chat(config: dict[str, Any], prompt: str) -> dict[str, Any]:
    cid = canonical_provider(config.get("provider") or "")
    if cid == "antigravity":
        return _antigravity_chat(config, prompt)
    if cid == "gemini_api":
        return _gemini_chat(config, prompt)
    if cid == "vertex_ai":
        return _vertex_chat(config, prompt)
    if cid == "openai_compatible":
        return _openai_chat(config, prompt)
    raise ProviderNotConfigured(f"unknown provider: {config.get('provider')}")


def list_models(config: dict[str, Any]) -> dict[str, Any]:
    cid = canonical_provider(config.get("provider") or "")
    if cid == "antigravity":
        if _agy_which():
            try:
                models = _antigravity_cli_models(config)
                if models:
                    return {"ok": True, "provider": cid, "count": len(models), "models": models,
                            "mechanism": "antigravity-cli", "message": "Loaded from `agy models`."}
            except ProviderError as exc:
                return {"ok": True, "provider": cid, "count": len(_antigravity_unknown_models()),
                        "models": _antigravity_unknown_models(),
                        "mechanism": "sdk-unknown", "message": f"`agy models` unavailable ({exc}); showing common ids."}
        return {"ok": True, "provider": cid, "count": len(_antigravity_unknown_models()),
                "models": _antigravity_unknown_models(),
                "mechanism": "sdk-unknown",
                "message": "Antigravity SDK/CLI model listing unavailable; showing common ids. "
                           "Install/authenticate the SDK or CLI on the webapp host for exact ids."}
    if cid == "gemini_api":
        models = _http_models(config, "gemini_api", headers={"x-goog-api-key": config.get("api_key", "")})
        return {"ok": True, "provider": cid, "count": len(models), "models": models}
    if cid == "vertex_ai":
        try:
            from google import genai  # noqa: F401
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Vertex AI model listing needs google-genai: {exc}") from exc
        return {"ok": True, "provider": cid, "count": 0, "models": [],
                "message": "Vertex AI model ids vary by project; enter the model id manually."}
    if cid == "openai_compatible":
        models = _http_models(config, "openai_compatible",
                              headers={"Authorization": f"Bearer {config.get('api_key', '')}"})
        return {"ok": True, "provider": cid, "count": len(models), "models": models}
    raise ProviderNotConfigured(f"unknown provider: {config.get('provider')}")


#: Curated known-free models per provider, used as a deterministic fallback catalog
#: when a live /models listing is unavailable or the provider has no listing
#: endpoint. Read-only; never fetched from a network by this module.
FREE_MODEL_CATALOG: dict[str, list[str]] = {
    "openai_compatible": [
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "google/gemini-2.0-flash-exp:free",
        "nvidia/nemotron-3.5-lightning:free",
        "qwen/qwen-2.5-72b-instruct:free",
    ],
    "gemini_api": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ],
    "vertex_ai": [],
    "antigravity": _antigravity_unknown_models(),
}


def free_models(provider: str | None) -> list[str]:
    """Return the curated known-free model catalog for a provider (deterministic).

    No network access — this is a fallback for a UI quick-pick list, not a live
    entitlement check. Providers without a meaningful free catalog return [].
    """
    cid = canonical_provider(provider)
    return list(FREE_MODEL_CATALOG.get(cid, []))


def _http_models(config: dict[str, Any], provider: str, *, headers: dict[str, str]) -> list[str]:
    import urllib.error
    import urllib.request
    endpoint = str(config.get("base_url") or "").rstrip("/")
    if not endpoint:
        raise ProviderError(f"{provider} needs a base_url to list models.")
    request = urllib.request.Request(f"{endpoint}/models", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"listing models failed: HTTP {exc.code}: {exc.read().decode('utf-8')[:300]}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"listing models failed: {exc}") from exc
    raw_ids: list[str] = []
    if isinstance(data, list):
        raw_ids = [str(x) for x in data]
    elif isinstance(data.get("data"), list):
        raw_ids = [str(m.get("id") or m.get("name") or "") for m in data["data"] if isinstance(m, dict)]
    elif isinstance(data.get("models"), list):
        for m in data["models"]:
            name = m.get("name") if isinstance(m, dict) else str(m)
            raw_ids.append(str(name).rsplit("/", 1)[-1])
    return sorted({x for x in raw_ids if x})


def login(config: dict[str, Any]) -> dict[str, Any]:
    cid = canonical_provider(config.get("provider") or "")
    if cid == "antigravity":
        if _sdk_importable() or _agy_which():
            return {"ok": False, "provider": cid,
                    "message": "Antigravity signs in locally with your Google account. "
                               "On the machine hosting this webapp run `agy` once and complete "
                               "Google Sign-In in your browser, or let the Antigravity SDK use "
                               "its existing local session. STEMMA does not collect Google credentials."}
        return {"ok": False, "provider": cid,
                "message": "Install the Antigravity CLI (`curl -fsSL https://antigravity.google/cli/install.sh | bash`) "
                           "or Antigravity SDK, then run it once to sign in with Google AI Pro."}
    if cid == "gemini_api":
        return {"ok": False, "provider": cid,
                "message": "Gemini API uses an API key, not an account login. Create/restrict the key at AI Studio."}
    if cid == "vertex_ai":
        return {"ok": False, "provider": cid,
                "message": "Vertex AI uses Application Default Credentials / a service-account scoped to your GCP project, not a consumer Google sign-in."}
    if cid == "openai_compatible":
        return _harness_login(config)
    return {"ok": False, "provider": cid, "message": "unknown provider"}


def _harness_login(config: dict[str, Any]) -> dict[str, Any]:
    import urllib.error
    import urllib.request
    endpoint = str(config.get("base_url") or "").rstrip("/")
    if not endpoint:
        return {"ok": False, "provider": canonical_provider(config.get("provider")),
                "message": "A base_url is required to use a local harness login."}
    errors: list[str] = []
    for path in ("/api/login", "/login"):
        url = f"{endpoint}{path}"
        method = "POST" if path == "/api/login" else "GET"
        headers = {"Content-Type": "application/json"}
        request = urllib.request.Request(url, data=b"{}" if method == "POST" else None,
                                         headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read()
            text = raw.decode("utf-8", "replace").strip()
            try:
                data = json.loads(text)
                result = data.get("url") or data.get("authorization_url") or data.get("login_url") or data.get("auth_url")
                if isinstance(result, str) and result.startswith("http"):
                    return {"ok": True, "provider": canonical_provider(config.get("provider")),
                            "url": result, "message": str(data.get("message") or "Open the login URL in your browser.")}
            except json.JSONDecodeError:
                pass
            if text.startswith("http"):
                return {"ok": True, "provider": canonical_provider(config.get("provider")),
                        "url": text, "message": "Open the login URL in your browser."}
        except urllib.error.HTTPError as exc:
            errors.append(f"{path}: HTTP {exc.code}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {exc}")
    return {"ok": False, "provider": canonical_provider(config.get("provider")),
            "message": "No login endpoint was found on this harness. Open its dashboard/CLI directly "
                       "or run its login command first. Paths tried: " + ", ".join(errors)}


def label(provider: str | None) -> str:
    return spec(provider).label
