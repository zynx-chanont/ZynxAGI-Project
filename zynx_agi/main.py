import asyncio
import logging
import time
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hmac
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator
import uvicorn

from .agents.zynx_metadata import observe_interaction
from .ai_platforms.provider import AIProviderGateway
from .config.settings import settings
from .core.engines import core_registry
from .cultural.thai_cultural_engine import ThaiCulturalEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared runtime instances
cultural_engine = ThaiCulturalEngine()
ai_gateway = AIProviderGateway(settings)


class ChatMessageRequest(BaseModel):
    """Validated payload for chat message endpoint."""

    model_config = ConfigDict(extra="allow")

    message: str = Field(..., min_length=1, max_length=4000)
    conversation_history: Optional[List[Dict[str, Any]]] = None
    cultural_context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    domain: Optional[str] = "general"

    @field_validator("message")
    @classmethod
    def validate_non_empty_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or whitespace")
        return stripped


class ChatMessageResponse(BaseModel):
    """Structured response for chat message endpoint."""

    message: str
    aiPlatform: str
    model: str
    mode: Literal["live", "mock", "fallback"]
    isMock: bool
    providerError: Optional[str] = None
    culturalContext: Dict[str, Any]
    processingTime: float
    coreEngines: Dict[str, str]
    usage: Optional[Dict[str, int]] = None


class CulturalAnalyzeRequest(BaseModel):
    """Validated payload for cultural analysis endpoint."""

    text: str = Field(..., min_length=1, max_length=4000)

    @field_validator("text")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Text cannot be empty or whitespace")
        return stripped


# Create FastAPI app
app = FastAPI(
    title="ZynxAGI",
    description="Universal AI Orchestration Platform with Cultural-Emotional Intelligence",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware: never combine wildcard '*' with allow_credentials=True
_has_wildcard = "*" in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not _has_wildcard,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)


def register_routers() -> None:
    """Register API routers for Core-Gateway adapter and optional services."""
    try:
        from .api.adapter import router as adapter_router
        app.include_router(adapter_router)
        logger.info("Gateway-to-Core Adapter router registered successfully")
    except Exception as exc:
        logger.error("Failed to register Adapter router: %s", exc)

    try:
        from .api.chat import router as chat_router
        from .api.cultural import router as cultural_router
        from .api.metadata import router as metadata_router

        app.include_router(chat_router)
        app.include_router(cultural_router)
        app.include_router(metadata_router)
        logger.info("Optional API routers registered successfully")
    except Exception as exc:
        logger.warning("Some optional API routers could not be registered: %s", exc)


register_routers()

# ─── Gate 4: Cryptographic Schema Lock & Database Boundary Freeze ─────────────
try:
    from .core.schema_lock import register_standard_schemas
    from .core.database_boundary import enforce_database_freeze, DatabaseBoundaryPolicy

    register_standard_schemas()
    enforce_database_freeze()
    logger.info("Gate 4: Schema locks and database boundary freeze initialized successfully")
except Exception as exc:
    logger.warning("Gate 4: Schema locks or database boundary could not be initialized: %s", exc)


async def _safe_observe_interaction(
    agent_name: str,
    user_input: str,
    agent_response: str,
    context: Dict[str, Any],
) -> None:
    try:
        await observe_interaction(
            agent_name=agent_name,
            user_input=user_input,
            agent_response=agent_response,
            context=context,
        )
    except Exception as exc:
        logger.warning("Metadata observer skipped: %s", exc)


def _analyze_message_culture(text: str) -> tuple[bool, Dict[str, Any]]:
    """Compute real rule-based cultural metadata from ThaiCulturalEngine."""
    is_thai = any(0x0E00 <= ord(char) <= 0x0E7F for char in text)
    particles, politeness_score = cultural_engine.analyze_polite_particles(text)
    formality_score = cultural_engine.analyze_formality(text)
    patterns = cultural_engine.detect_cultural_patterns(text)

    if formality_score >= 0.7:
        formality_label = "formal"
    elif formality_score >= 0.4 or particles:
        formality_label = "semi-formal"
    else:
        formality_label = "casual"

    if is_thai and particles:
        style = "polite_thai"
    elif is_thai:
        style = "helpful_thai"
    else:
        style = "helpful_international"

    return is_thai, {
        "primaryCulture": "thai" if is_thai else "international",
        "language": "th-TH" if is_thai else "en-US",
        "formalityLevel": formality_label,
        "formalityScore": round(formality_score, 3),
        "politenessLevel": round(politeness_score, 3),
        "culturalMarkers": particles or list(patterns.keys()),
        "culturalPatterns": list(patterns.keys()),
        "communicationStyle": style,
    }



# ─── Service-to-Service Authentication Dependency (Gate 2/3) ──────────────────
from .security.auth import http_bearer, verify_service_token


@app.get("/")
@app.head("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    provider_cfg = ai_gateway.resolve_configuration()
    return {
        "message": "Welcome to ZynxAGI - Universal AI Orchestration Platform",
        "version": settings.APP_VERSION,
        "cultural_intelligence": "Thai-English Bridge Active",
        "status": "operational",
        "mode": "live" if provider_cfg.configured else "mock",
        "docs": "/docs",
    }


def _build_health_payload() -> Dict[str, Any]:
    provider_cfg = ai_gateway.resolve_configuration()
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "live" if provider_cfg.configured else "mock",
        "ai_provider": {
            "provider": provider_cfg.provider,
            "model": provider_cfg.model,
            "configured": provider_cfg.configured,
        },
        "components": {
            "api": "healthy",
            "cultural_intelligence": "ready",
            "universal_dispatcher": "ready",
            "ai_gateway": "live" if provider_cfg.configured else "mock_mode",
        },
        "core_engines": core_registry.status_summary(),
        "message": "ZynxAGI is running successfully!",
        "thai_message": "ระบบ ZynxAGI ทำงานปกติค่ะ!",
    }


@app.get("/health")
@app.head("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return _build_health_payload()


@app.get("/api/v1/health")
@app.head("/api/v1/health")
async def api_v1_health_check() -> Dict[str, Any]:
    """Versioned health check endpoint for frontend clients and cloud health monitors."""
    return _build_health_payload()


@app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    _token: str = Depends(verify_service_token),
) -> ChatMessageResponse:
    """Process a chat message through Cultural Engine and AIProviderGateway."""
    start_ts = time.perf_counter()

    try:
        is_thai, cultural_context = _analyze_message_culture(request.message)
        core_statuses = core_registry.status_summary()

        ai_result = await ai_gateway.generate(
            message=request.message,
            cultural_context=cultural_context,
            is_thai=is_thai,
            conversation_history=request.conversation_history,
            requested_model=request.model,
        )

        processing_time = round(time.perf_counter() - start_ts, 4)

        asyncio.create_task(
            _safe_observe_interaction(
                agent_name="deeja_gateway",
                user_input=request.message,
                agent_response=ai_result.message,
                context={
                    "endpoint": "/api/v1/chat/message",
                    "language": "thai" if is_thai else "english",
                    "mode": ai_result.mode,
                    "provider": ai_result.provider,
                    "cultural_context": cultural_context,
                },
            )
        )

        return ChatMessageResponse(
            message=ai_result.message,
            aiPlatform=ai_result.provider,
            model=ai_result.model,
            mode=ai_result.mode,  # type: ignore[arg-type]
            isMock=ai_result.is_mock,
            providerError=ai_result.error,
            culturalContext=cultural_context,
            processingTime=processing_time,
            coreEngines=core_statuses,
            usage=ai_result.usage,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error in chat message endpoint: %s", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/cultural/analyze")
async def cultural_analyze(
    request: CulturalAnalyzeRequest,
    _token: str = Depends(verify_service_token),
) -> Dict[str, Any]:
    """Cultural analysis endpoint."""
    try:
        is_thai, cultural_context = _analyze_message_culture(request.text)
        return {
            "primaryCulture": cultural_context["primaryCulture"],
            "language": cultural_context["language"],
            "formalityLevel": cultural_context["formalityLevel"],
            "formalityScore": cultural_context["formalityScore"],
            "politenessLevel": cultural_context["politenessLevel"],
            "culturalMarkers": cultural_context["culturalMarkers"],
            "culturalPatterns": cultural_context["culturalPatterns"],
            "communicationStyle": cultural_context["communicationStyle"],
            "isThai": is_thai,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error in cultural analyze endpoint: %s", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Internal server error")


def start() -> None:
    """Start the server (honours $PORT used by Render / Hugging Face Spaces)."""
    import os

    uvicorn.run(
        "zynx_agi.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    start()


@app.get("/api/v1/database/boundaries")
async def get_database_boundaries(
    _token: str = Depends(verify_service_token),
) -> Dict[str, Any]:
    """Return the Gate 4 frozen Supabase database boundary manifest."""
    return DatabaseBoundaryPolicy.get_boundary_manifest()
