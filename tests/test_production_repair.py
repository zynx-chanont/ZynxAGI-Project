"""
Tests for ZYNX AGI production repair:
- FastAPI startup & health endpoints
- CORS configuration & preflight behavior
- Valid & invalid request validation
- AIProviderGateway live, mock, and fallback modes
- ZYNX Core modular engine interfaces
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from zynx_agi.ai_platforms.provider import AIProviderGateway
from zynx_agi.config.settings import Settings
from zynx_agi.core.engines import (
    ChanontTheoryEngine,
    EvolutionEngine,
    IntelligenceEngine,
    ReasoningEngine,
    StrategyEngine,
    ZynxCoreRegistry,
)
from zynx_agi.cultural.thai_cultural_engine import ThaiCulturalEngine
from zynx_agi.main import app


client = TestClient(app)


class TestHealthAndStartup:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["mode"] in {"mock", "live"}

    def test_health_and_v1_health_endpoints(self):
        for path in ("/health", "/api/v1/health"):
            response = client.get(path)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "ai_provider" in data
            assert "core_engines" in data
            assert data["core_engines"]["chanont_theory"] == "specification_in_development"


class TestCorsConfiguration:
    def test_settings_parses_comma_separated_origins(self):
        cfg = Settings(
            DEBUG=False,
            ALLOWED_ORIGINS="https://zynx-agi.netlify.app, https://custom.zynx.dev/",
        )
        assert cfg.ALLOWED_ORIGINS == [
            "https://zynx-agi.netlify.app",
            "https://custom.zynx.dev",
        ]

    def test_settings_rejects_wildcard_in_production(self):
        with pytest.raises(ValueError, match="Wildcard '\\*' is not permitted"):
            Settings(DEBUG=False, ALLOWED_ORIGINS="*")

    def test_cors_allows_netlify_production_origin(self):
        response = client.options(
            "/api/v1/chat/message",
            headers={
                "Origin": "https://zynx-agi.netlify.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            == "https://zynx-agi.netlify.app"
        )

    def test_cors_allows_localhost_dev_origin(self):
        response = client.options(
            "/api/v1/chat/message",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_blocks_unlisted_origin(self):
        response = client.options(
            "/api/v1/chat/message",
            headers={
                "Origin": "https://untrusted.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert "access-control-allow-origin" not in response.headers


class TestChatAndValidation:
    def test_chat_message_mock_mode_thai(self):
        response = client.post(
            "/api/v1/chat/message",
            json={"message": "สวัสดีค่ะ ช่วยแนะนำระบบหน่อย"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "mock"
        assert data["isMock"] is True
        assert data["aiPlatform"] == "mock"
        assert "Mock Mode" in data["message"]
        assert data["culturalContext"]["primaryCulture"] == "thai"
        assert "ค่ะ" in data["culturalContext"]["culturalMarkers"]
        assert "culturalAccuracyScore" not in data
        assert "emotionalIntelligenceScore" not in data

    def test_chat_message_mock_mode_english(self):
        response = client.post(
            "/api/v1/chat/message",
            json={"message": "Hello ZynxAGI!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "mock"
        assert data["isMock"] is True
        assert "Mock Mode" in data["message"]
        assert data["culturalContext"]["primaryCulture"] == "international"

    def test_chat_message_rejects_empty_and_whitespace(self):
        for payload in ({}, {"message": ""}, {"message": "   "}):
            response = client.post("/api/v1/chat/message", json=payload)
            assert response.status_code == 422

    def test_cultural_analyze_validation_and_analysis(self):
        bad_resp = client.post("/api/v1/cultural/analyze", json={"text": "   "})
        assert bad_resp.status_code == 422

        ok_resp = client.post(
            "/api/v1/cultural/analyze",
            json={"text": "สวัสดีครับ ขอบคุณมากครับ"},
        )
        assert ok_resp.status_code == 200
        data = ok_resp.json()
        assert data["primaryCulture"] == "thai"
        assert data["isThai"] is True
        assert "ครับ" in data["culturalMarkers"]


class TestAIProviderGateway:
    def test_placeholder_keys_resolve_to_mock(self):
        cfg = Settings(
            AI_PROVIDER="auto",
            AI_API_KEY="your_ai_provider_api_key_here",
            OPENAI_API_KEY="your_openai_api_key_here",
        )
        gateway = AIProviderGateway(cfg)
        resolved = gateway.resolve_configuration()
        assert resolved.configured is False
        assert resolved.provider == "mock"
        assert resolved.api_key is None

    @pytest.mark.asyncio
    async def test_openai_live_mode_with_mock_transport(self):
        secret_key = "sk-test-secret-openai-key"
        cfg = Settings(AI_PROVIDER="openai", AI_API_KEY=secret_key)
        gateway = AIProviderGateway(cfg)

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["Authorization"] == f"Bearer {secret_key}"
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "สวัสดีจาก Live OpenAI ค่ะ"}}],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 8,
                        "total_tokens": 20,
                    },
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="สวัสดีค่ะ",
                cultural_context={"primaryCulture": "thai"},
                is_thai=True,
                http_client=http_client,
            )

        assert result.mode == "live"
        assert result.is_mock is False
        assert result.provider == "openai"
        assert result.message == "สวัสดีจาก Live OpenAI ค่ะ"
        assert result.usage == {
            "prompt_tokens": 12,
            "completion_tokens": 8,
            "total_tokens": 20,
        }

    @pytest.mark.asyncio
    async def test_anthropic_live_mode_with_mock_transport(self):
        secret_key = "sk-ant-test-secret-key"
        cfg = Settings(AI_PROVIDER="anthropic", AI_API_KEY=secret_key)
        gateway = AIProviderGateway(cfg)

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["x-api-key"] == secret_key
            return httpx.Response(
                200,
                json={
                    "content": [{"type": "text", "text": "Hello from Anthropic"}],
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="Hello",
                cultural_context={"primaryCulture": "international"},
                is_thai=False,
                http_client=http_client,
            )

        assert result.mode == "live"
        assert result.is_mock is False
        assert result.provider == "anthropic"
        assert result.message == "Hello from Anthropic"
        assert result.usage == {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }

    @pytest.mark.asyncio
    async def test_google_live_mode_with_mock_transport(self):
        secret_key = "AIzaTestGoogleSecretKey"
        cfg = Settings(AI_PROVIDER="google", AI_API_KEY=secret_key)
        gateway = AIProviderGateway(cfg)

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["x-goog-api-key"] == secret_key
            assert secret_key not in str(request.url)
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {"content": {"parts": [{"text": "Hello from Gemini"}]}}
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 7,
                        "candidatesTokenCount": 4,
                        "totalTokenCount": 11,
                    },
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="Hello",
                cultural_context={"primaryCulture": "international"},
                is_thai=False,
                http_client=http_client,
            )

        assert result.mode == "live"
        assert result.is_mock is False
        assert result.provider == "google"
        assert result.message == "Hello from Gemini"

    @pytest.mark.asyncio
    async def test_google_retired_model_404_discovers_replacement(self):
        secret_key = "AIzaTestGoogleSecretKey"
        cfg = Settings(AI_PROVIDER="google", AI_API_KEY=secret_key, GOOGLE_MODEL="gemini-old-flash")
        gateway = AIProviderGateway(cfg)
        calls = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            assert secret_key not in str(request.url)
            if request.method == "GET" and request.url.path.endswith("/models"):
                return httpx.Response(200, json={"models": [
                    {"name": "models/text-embedding-004", "supportedGenerationMethods": ["embedContent"]},
                    {"name": "models/gemini-9.0-flash-lite", "supportedGenerationMethods": ["generateContent"]},
                    {"name": "models/gemini-9.0-flash-preview", "supportedGenerationMethods": ["generateContent"]},
                    {"name": "models/gemini-8.5-flash", "supportedGenerationMethods": ["generateContent"]},
                    {"name": "models/gemini-9.0-pro", "supportedGenerationMethods": ["generateContent"]},
                ]})
            if "gemini-old-flash" in request.url.path:
                return httpx.Response(404, json={"error": {"code": 404}})
            assert "gemini-8.5-flash:generateContent" in request.url.path
            return httpx.Response(200, json={
                "candidates": [{"content": {"parts": [{"text": "Hi from new model"}]}}],
            })

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="Hello", cultural_context={}, is_thai=False, http_client=http_client,
            )
            assert result.mode == "live" and result.is_mock is False
            assert result.model == "gemini-8.5-flash"
            assert result.message == "Hi from new model"

            # Second call uses the cached replacement directly (no 404, no discovery).
            calls.clear()
            again = await gateway.generate(
                message="Hello", cultural_context={}, is_thai=False, http_client=http_client,
            )
            assert again.mode == "live"
            assert calls == [("POST", "/v1beta/models/gemini-8.5-flash:generateContent")]

    @pytest.mark.asyncio
    async def test_google_404_without_replacement_falls_back(self):
        cfg = Settings(AI_PROVIDER="google", AI_API_KEY="AIzaTestKey")
        gateway = AIProviderGateway(cfg)

        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "GET":
                return httpx.Response(200, json={"models": []})
            return httpx.Response(404, json={})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="Hello", cultural_context={}, is_thai=False, http_client=http_client,
            )
        assert result.mode == "fallback" and result.is_mock is True
        assert "404" in (result.error or "")

    @pytest.mark.asyncio
    async def test_upstream_failure_triggers_safe_fallback_without_key_leak(self):
        secret_key = "sk-do-not-leak-me"
        cfg = Settings(AI_PROVIDER="openai", AI_API_KEY=secret_key)
        gateway = AIProviderGateway(cfg)

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, json={"error": "Service unavailable"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            result = await gateway.generate(
                message="สวัสดีค่ะ",
                cultural_context={"primaryCulture": "thai"},
                is_thai=True,
                http_client=http_client,
            )

        assert result.mode == "fallback"
        assert result.is_mock is True
        assert result.error is not None
        assert "503" in result.error
        assert secret_key not in result.message
        assert secret_key not in result.error


class TestZynxCoreModularEngines:
    def test_all_five_engines_registered(self):
        registry = ZynxCoreRegistry()
        descriptors = registry.list_engines()
        engine_ids = [item["engine_id"] for item in descriptors]
        assert engine_ids == [
            "intelligence",
            "reasoning",
            "strategy",
            "evolution",
            "chanont_theory",
        ]

    def test_chanont_theory_engine_marked_in_development(self):
        engine = ChanontTheoryEngine()
        assert engine.status == "specification_in_development"
        context = engine.inspect_context({"message": "test"})
        assert context["specification_ready"] is False

    def test_individual_engines_inspect_context(self):
        assert IntelligenceEngine().inspect_context({"message": "สวัสดี"})["detected_script"] == "thai"
        assert ReasoningEngine().inspect_context({"conversation_history": [{"role": "user", "content": "hi"}]})["history_turns"] == 1
        assert StrategyEngine().inspect_context({"model": "gpt-4o-mini"})["requested_model"] == "gpt-4o-mini"
        assert EvolutionEngine().inspect_context({})["status"] == "ready"

    @pytest.mark.asyncio
    async def test_thai_cultural_engine_process_message_alias(self):
        engine = ThaiCulturalEngine()
        result = await engine.process_message({"text": "สวัสดีครับ", "adjust_response": False})
        assert result["original_text"] == "สวัสดีครับ"
        assert "ครับ" in result["cultural_context"]["detected_particles"]
