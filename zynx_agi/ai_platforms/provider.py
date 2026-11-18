"""
Modular AI Provider Gateway for ZynxAGI.

Resolves backend-only provider credentials from environment/settings,
calls live AI APIs when configured, and provides an explicit, honest
mock/fallback mode when credentials are absent or upstream calls fail.
"""

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from ..config.settings import Settings, settings as default_settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_KEYS = {
    "",
    "your_ai_provider_api_key_here",
    "your_openai_api_key_here",
    "your_anthropic_api_key_here",
    "your_google_api_key_here",
    "changeme",
}

_SUPPORTED_PROVIDERS = {"openai", "anthropic", "google", "mock", "auto"}

_GOOGLE_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _is_valid_secret(value: Optional[str]) -> bool:
    if not value:
        return False
    normalized = value.strip()
    return bool(normalized) and normalized.lower() not in _PLACEHOLDER_KEYS


def _infer_provider_from_key_or_model(
    api_key: str, model: Optional[str]
) -> str:
    if model:
        lowered = model.lower()
        if "claude" in lowered:
            return "anthropic"
        if "gemini" in lowered:
            return "google"
        if "gpt" in lowered or lowered.startswith("o1") or lowered.startswith("o3"):
            return "openai"
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if api_key.startswith("AIza"):
        return "google"
    return "openai"


@dataclass(frozen=True)
class ProviderConfiguration:
    """Resolved non-secret description of active AI provider configuration."""

    provider: str
    model: str
    configured: bool
    api_key: Optional[str] = field(default=None, repr=False)


@dataclass
class AIProviderResult:
    """Structured response returned by AIProviderGateway."""

    message: str
    provider: str
    model: str
    mode: str  # "live" | "mock" | "fallback"
    is_mock: bool
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class AIProviderGateway:
    """Clean, provider-agnostic AI gateway reading secrets exclusively from backend config."""

    def __init__(self, app_settings: Optional[Settings] = None) -> None:
        self.settings = app_settings or default_settings
        # Set when the configured Gemini model 404s and a replacement is discovered.
        self._google_model_override: Optional[str] = None

    @staticmethod
    async def _discover_google_model(
        client: httpx.AsyncClient, api_key: str, exclude: str
    ) -> Optional[str]:
        """Pick a generateContent-capable Gemini model available to this key.

        Preference: stable (non-preview/exp) "flash" models, newest version first,
        excluding "lite"/"live"/"image"/"tts" variants where possible.
        """
        try:
            response = await client.get(
                f"{_GOOGLE_API_BASE}/models",
                headers={"x-goog-api-key": api_key},
                params={"pageSize": 1000},
            )
            response.raise_for_status()
            models = response.json().get("models") or []
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Gemini model discovery failed: %s", type(exc).__name__)
            return None

        candidates: List[str] = []
        for item in models:
            if not isinstance(item, dict):
                continue
            methods = item.get("supportedGenerationMethods") or []
            name = str(item.get("name", "")).removeprefix("models/")
            if "generateContent" in methods and name and name != exclude and "gemini" in name:
                candidates.append(name)
        if not candidates:
            return None

        def _rank(name: str):
            lowered = name.lower()
            unstable = any(tag in lowered for tag in ("preview", "exp", "latest"))
            special = any(tag in lowered for tag in ("lite", "live", "image", "tts", "audio", "embedding", "thinking"))
            is_flash = "flash" in lowered
            version = [int(n) for n in re.findall(r"\d+", lowered)[:2]]
            return (not is_flash, special, unstable, [-v for v in version], lowered)

        return sorted(candidates, key=_rank)[0]

    def resolve_configuration(
        self, requested_model: Optional[str] = None
    ) -> ProviderConfiguration:
        """Resolve which AI provider and model should handle requests."""
        raw_provider = (self.settings.AI_PROVIDER or "auto").strip().lower()
        if raw_provider not in _SUPPORTED_PROVIDERS:
            logger.warning(
                "Unsupported AI_PROVIDER '%s'; falling back to auto detection",
                raw_provider,
            )
            raw_provider = "auto"

        if raw_provider == "mock":
            return ProviderConfiguration(
                provider="mock",
                model="deeja-mock-v1",
                configured=False,
                api_key=None,
            )

        override_model = (
            requested_model.strip()
            if requested_model and requested_model.strip() not in {"auto", "deeja-v1"}
            else None
        )
        configured_model = (
            override_model
            or (self.settings.AI_MODEL.strip() if self.settings.AI_MODEL else None)
        )

        # Explicit provider selection
        if raw_provider in {"openai", "anthropic", "google"}:
            api_key = self._key_for_provider(raw_provider)
            if not api_key:
                return ProviderConfiguration(
                    provider="mock",
                    model="deeja-mock-v1",
                    configured=False,
                    api_key=None,
                )
            return ProviderConfiguration(
                provider=raw_provider,
                model=configured_model or self._default_model_for(raw_provider),
                configured=True,
                api_key=api_key,
            )

        # Auto selection: check unified AI_API_KEY first, then provider-specific keys
        if _is_valid_secret(self.settings.AI_API_KEY):
            unified_key = self.settings.AI_API_KEY.strip()  # type: ignore[union-attr]
            provider = _infer_provider_from_key_or_model(unified_key, configured_model)
            return ProviderConfiguration(
                provider=provider,
                model=configured_model or self._default_model_for(provider),
                configured=True,
                api_key=unified_key,
            )

        for candidate in ("openai", "anthropic", "google"):
            api_key = self._key_for_provider(candidate)
            if api_key:
                return ProviderConfiguration(
                    provider=candidate,
                    model=configured_model or self._default_model_for(candidate),
                    configured=True,
                    api_key=api_key,
                )

        return ProviderConfiguration(
            provider="mock",
            model="deeja-mock-v1",
            configured=False,
            api_key=None,
        )

    def _key_for_provider(self, provider: str) -> Optional[str]:
        if provider == "openai":
            candidate = self.settings.AI_API_KEY if _is_valid_secret(self.settings.AI_API_KEY) else self.settings.OPENAI_API_KEY
            return candidate.strip() if _is_valid_secret(candidate) else None
        if provider == "anthropic":
            candidate = self.settings.AI_API_KEY if _is_valid_secret(self.settings.AI_API_KEY) else self.settings.ANTHROPIC_API_KEY
            return candidate.strip() if _is_valid_secret(candidate) else None
        if provider == "google":
            candidate = self.settings.AI_API_KEY if _is_valid_secret(self.settings.AI_API_KEY) else self.settings.GOOGLE_API_KEY
            return candidate.strip() if _is_valid_secret(candidate) else None
        return None

    def _default_model_for(self, provider: str) -> str:
        if provider == "openai":
            return self.settings.OPENAI_MODEL
        if provider == "anthropic":
            return self.settings.ANTHROPIC_MODEL
        if provider == "google":
            return self.settings.GOOGLE_MODEL
        return "deeja-mock-v1"

    def _build_system_prompt(self, cultural_context: Dict[str, Any]) -> str:
        primary = cultural_context.get("primaryCulture", "international")
        formality = cultural_context.get("formalityLevel", "casual")
        style = cultural_context.get("communicationStyle", "helpful")
        return (
            "You are Deeja (ดีจ้า), the cultural-aware AI assistant of ZYNX AGI. "
            "Respond helpfully, accurately, and concisely in the user's language (Thai or English). "
            f"Detected cultural context: primaryCulture={primary}, formality={formality}, style={style}."
        )

    def _normalize_history(
        self, history: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, str]]:
        normalized: List[Dict[str, str]] = []
        if not history:
            return normalized
        for item in history[-10:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
                normalized.append({"role": role, "content": content.strip()[:4000]})
        return normalized

    def _mock_response(
        self,
        message: str,
        is_thai: bool,
        mode: str = "mock",
        provider: str = "mock",
        model: str = "deeja-mock-v1",
        error: Optional[str] = None,
    ) -> AIProviderResult:
        lower = message.lower()
        is_greeting = "สวัสดี" in message or any(
            greet in lower.split() for greet in ("hello", "hi", "hey")
        )

        if mode == "fallback":
            prefix_th = "[โหมดสำรอง — ผู้ให้บริการ AI หลักไม่พร้อมใช้งานชั่วคราว] "
            prefix_en = "[Fallback Mode — upstream AI provider temporarily unavailable] "
        else:
            prefix_th = "[Mock Mode — ยังไม่ได้ตั้งค่า AI API Key บน Backend] "
            prefix_en = "[Mock Mode — no live AI provider API key configured on backend] "

        if is_thai:
            if is_greeting:
                body = (
                    "สวัสดีค่ะ! ฉันคือ Deeja บนระบบ ZynxAGI 🌟 "
                    "ขณะนี้ระบบกำลังตอบกลับจากโหมดจำลอง (Mock/Fallback) โดยวิเคราะห์บริบทภาษาไทยและระดับความสุภาพให้เรียบร้อยแล้วค่ะ"
                )
            else:
                body = (
                    f"ได้รับข้อความของคุณแล้วค่ะ: \"{message}\" "
                    "เมื่อตั้งค่า AI_API_KEY (หรือ OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY) ใน Backend แล้ว ข้อความนี้จะถูกประมวลผลด้วยโมเดล AI จริงค่ะ"
                )
            full_message = f"{prefix_th}{body}"
        else:
            if is_greeting:
                body = (
                    "Hello! I'm Deeja on ZynxAGI 🌟 "
                    "The backend is responding in local mock/fallback mode with cultural context analysis active."
                )
            else:
                body = (
                    f"Received your message: \"{message}\". "
                    "Configure AI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY) on the backend to enable live AI generation."
                )
            full_message = f"{prefix_en}{body}"

        return AIProviderResult(
            message=full_message,
            provider=provider,
            model=model,
            mode=mode,
            is_mock=True,
            usage=None,
            error=error,
        )

    async def _call_openai(
        self,
        client: httpx.AsyncClient,
        config: ProviderConfiguration,
        system_prompt: str,
        history: List[Dict[str, str]],
        message: str,
    ) -> AIProviderResult:
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message},
        ]
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.model,
                "messages": messages,
                "max_tokens": self.settings.OPENAI_MAX_TOKENS,
                "temperature": self.settings.OPENAI_TEMPERATURE,
            },
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Empty response content from OpenAI")
        raw_usage = payload.get("usage") or {}
        usage = {
            "prompt_tokens": int(raw_usage.get("prompt_tokens", 0)),
            "completion_tokens": int(raw_usage.get("completion_tokens", 0)),
            "total_tokens": int(raw_usage.get("total_tokens", 0)),
        }
        return AIProviderResult(
            message=text.strip(),
            provider="openai",
            model=config.model,
            mode="live",
            is_mock=False,
            usage=usage,
        )

    async def _call_anthropic(
        self,
        client: httpx.AsyncClient,
        config: ProviderConfiguration,
        system_prompt: str,
        history: List[Dict[str, str]],
        message: str,
    ) -> AIProviderResult:
        messages = [*history, {"role": "user", "content": message}]
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": config.api_key or "",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": config.model,
                "max_tokens": self.settings.ANTHROPIC_MAX_TOKENS,
                "temperature": self.settings.ANTHROPIC_TEMPERATURE,
                "system": system_prompt,
                "messages": messages,
            },
        )
        response.raise_for_status()
        payload = response.json()
        blocks = payload.get("content") or []
        text_parts = [
            block.get("text", "")
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        text = "\n".join(part for part in text_parts if part).strip()
        if not text:
            raise ValueError("Empty response content from Anthropic")
        raw_usage = payload.get("usage") or {}
        input_tokens = int(raw_usage.get("input_tokens", 0))
        output_tokens = int(raw_usage.get("output_tokens", 0))
        return AIProviderResult(
            message=text,
            provider="anthropic",
            model=config.model,
            mode="live",
            is_mock=False,
            usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        )

    async def _call_google(
        self,
        client: httpx.AsyncClient,
        config: ProviderConfiguration,
        system_prompt: str,
        history: List[Dict[str, str]],
        message: str,
    ) -> AIProviderResult:
        contents = [
            {
                "role": "model" if item["role"] == "assistant" else "user",
                "parts": [{"text": item["content"]}],
            }
            for item in history
        ]
        contents.append({"role": "user", "parts": [{"text": message}]})
        headers = {
            "x-goog-api-key": config.api_key or "",
            "Content-Type": "application/json",
        }
        body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
        }

        model = self._google_model_override or config.model
        response = await client.post(
            f"{_GOOGLE_API_BASE}/models/{model}:generateContent",
            headers=headers,
            json=body,
        )
        if response.status_code == 404:
            # Configured model was retired or is unavailable for this key:
            # discover a supported model once, cache it, and retry.
            discovered = await self._discover_google_model(client, config.api_key or "", exclude=model)
            if discovered:
                logger.warning(
                    "Gemini model '%s' not found; switching to discovered model '%s'",
                    model,
                    discovered,
                )
                self._google_model_override = discovered
                model = discovered
                response = await client.post(
                    f"{_GOOGLE_API_BASE}/models/{model}:generateContent",
                    headers=headers,
                    json=body,
                )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates") or []
        parts = (candidates[0].get("content") or {}).get("parts", []) if candidates else []
        text = "".join(
            part.get("text", "") for part in parts if isinstance(part, dict)
        ).strip()
        if not text:
            raise ValueError("Empty response content from Google Gemini")
        meta = payload.get("usageMetadata") or {}
        prompt_tokens = int(meta.get("promptTokenCount", 0))
        completion_tokens = int(meta.get("candidatesTokenCount", 0))
        return AIProviderResult(
            message=text,
            provider="google",
            model=model,
            mode="live",
            is_mock=False,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": int(
                    meta.get("totalTokenCount", prompt_tokens + completion_tokens)
                ),
            },
        )

    async def generate(
        self,
        message: str,
        cultural_context: Dict[str, Any],
        is_thai: bool,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        requested_model: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> AIProviderResult:
        """Generate an AI response if configured; otherwise return an honest mock/fallback."""
        config = self.resolve_configuration(requested_model=requested_model)
        if not config.configured or not config.api_key:
            return self._mock_response(message=message, is_thai=is_thai, mode="mock")

        system_prompt = self._build_system_prompt(cultural_context)
        history = self._normalize_history(conversation_history)

        async def _dispatch(client: httpx.AsyncClient) -> AIProviderResult:
            if config.provider == "openai":
                return await self._call_openai(
                    client, config, system_prompt, history, message
                )
            if config.provider == "anthropic":
                return await self._call_anthropic(
                    client, config, system_prompt, history, message
                )
            if config.provider == "google":
                return await self._call_google(
                    client, config, system_prompt, history, message
                )
            return self._mock_response(message=message, is_thai=is_thai, mode="mock")

        try:
            if http_client is not None:
                return await _dispatch(http_client)
            async with httpx.AsyncClient(
                timeout=self.settings.AI_REQUEST_TIMEOUT
            ) as client:
                return await _dispatch(client)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.warning(
                "Upstream AI provider '%s' returned HTTP %s; using safe fallback",
                config.provider,
                status_code,
            )
            return self._mock_response(
                message=message,
                is_thai=is_thai,
                mode="fallback",
                provider=config.provider,
                model=config.model,
                error=f"Upstream AI provider returned status {status_code}",
            )
        except (httpx.RequestError, ValueError, KeyError, IndexError) as exc:
            logger.warning(
                "Upstream AI provider '%s' call failed (%s); using safe fallback",
                config.provider,
                type(exc).__name__,
            )
            return self._mock_response(
                message=message,
                is_thai=is_thai,
                mode="fallback",
                provider=config.provider,
                model=config.model,
                error=f"Upstream AI provider unavailable ({type(exc).__name__})",
            )
