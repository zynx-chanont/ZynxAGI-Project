from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from ..config.settings import settings
from ..security.pii_scrubber import pii_scrubber, PIIDetectionResult
from ..ai_platforms.base_adapter import LLMRequest, LLMResponse, LLMError
from ..ai_platforms.openai_adapter import OpenAIAdapter
from ..ai_platforms.zynx_local_adapter import ZynxLocalAdapter

# Initialize router
router = APIRouter(prefix="/api/v1/llm", tags=["LLM Gateway"])
logger = logging.getLogger(__name__)

# Request/Response models
class LLMGatewayRequest(BaseModel):
    message: str = Field(..., description="The message to send to the LLM")
    model: Optional[str] = Field(None, description="Specific model to use")
    provider: Optional[str] = Field(None, description="LLM provider: 'openai', 'zynx_local', 'claude'")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(150, ge=1, le=4000, description="Maximum tokens in response")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Cultural context for response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class LLMGatewayResponse(BaseModel):
    text: str
    model: str
    provider: str
    usage: Dict[str, int]
    cultural_context: Optional[Dict[str, Any]] = None
    processing_time_ms: float
    cost_estimate: float
    compliance: Dict[str, Any]
    pii_detected: bool
    timestamp: datetime

class LLMGatewayError(BaseModel):
    error: str
    message: str
    provider: str
    retryable: bool
    timestamp: datetime

# Provider management
class LLMProviderManager:
    """Manages LLM providers and routing"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIAdapter(),
            "zynx_local": ZynxLocalAdapter()
        }
        self.fallback_order = ["openai", "zynx_local"]
        
        # Usage tracking
        self.usage_stats = {
            "requests_total": 0,
            "requests_by_provider": {},
            "errors_by_provider": {},
            "total_tokens": 0,
            "total_cost": 0.0
        }
        
        # Data retention tracking
        self.request_log = []
    
    async def get_provider(self, provider_name: Optional[str] = None) -> str:
        """Get the best available provider"""
        # Use specified provider if available
        if provider_name:
            if provider_name in self.providers:
                if await self.providers[provider_name].is_available():
                    return provider_name
                else:
                    logger.warning(f"Requested provider {provider_name} is not available")
            else:
                logger.warning(f"Unknown provider: {provider_name}")
        
        # Use configured default provider
        default_provider = settings.ZYNX_LLM_PROVIDER
        if default_provider in self.providers:
            if await self.providers[default_provider].is_available():
                return default_provider
        
        # Try fallback providers
        for provider in self.fallback_order:
            if provider in self.providers:
                if await self.providers[provider].is_available():
                    logger.info(f"Using fallback provider: {provider}")
                    return provider
        
        raise HTTPException(status_code=503, detail="No LLM providers available")
    
    async def generate_response(self, request: LLMGatewayRequest) -> LLMGatewayResponse:
        """Generate response through the gateway"""
        start_time = asyncio.get_event_loop().time()
        
        # 1. Scrub PII from request
        request_dict = request.model_dump()
        scrubbed_request, pii_result = pii_scrubber.scrub_request(request_dict)
        
        # 2. Check cross-border compliance
        compliance_result = pii_scrubber.check_cross_border_compliance(request_dict)
        
        if not compliance_result["transfer_allowed"]:
            raise HTTPException(
                status_code=403, 
                detail=f"Cross-border data transfer not allowed: {compliance_result['requirements']}"
            )
        
        # 3. Get appropriate provider
        provider_name = await self.get_provider(request.provider)
        provider = self.providers[provider_name]
        
        # 4. Create LLM request
        llm_request = LLMRequest(
            message=scrubbed_request["message"],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            cultural_context=request.cultural_context,
            metadata=request.metadata
        )
        
        # 5. Estimate cost
        cost_estimate = await provider.estimate_cost(llm_request)
        
        try:
            # 6. Generate response
            llm_response = await provider.generate_response(llm_request)
            
            # 7. Scrub PII from response
            response_dict = {
                "text": llm_response.text,
                "cultural_context": llm_response.cultural_context
            }
            scrubbed_response, response_pii_result = pii_scrubber.scrub_response(response_dict)
            
            # 8. Update usage statistics
            self._update_usage_stats(provider_name, llm_response.usage, cost_estimate)
            
            # 9. Log for audit (anonymized)
            await self._log_request(
                scrubbed_request, scrubbed_response, pii_result, 
                provider_name, compliance_result
            )
            
            total_processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return LLMGatewayResponse(
                text=scrubbed_response["text"],
                model=llm_response.model,
                provider=llm_response.provider,
                usage=llm_response.usage,
                cultural_context=scrubbed_response.get("cultural_context"),
                processing_time_ms=total_processing_time,
                cost_estimate=cost_estimate,
                compliance=compliance_result,
                pii_detected=pii_result.has_pii or response_pii_result.has_pii,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            # Update error statistics
            if provider_name not in self.usage_stats["errors_by_provider"]:
                self.usage_stats["errors_by_provider"][provider_name] = 0
            self.usage_stats["errors_by_provider"][provider_name] += 1
            
            logger.error(f"LLM Gateway error with provider {provider_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    def _update_usage_stats(self, provider: str, usage: Dict[str, int], cost: float):
        """Update usage statistics"""
        self.usage_stats["requests_total"] += 1
        
        if provider not in self.usage_stats["requests_by_provider"]:
            self.usage_stats["requests_by_provider"][provider] = 0
        self.usage_stats["requests_by_provider"][provider] += 1
        
        self.usage_stats["total_tokens"] += usage.get("total_tokens", 0)
        self.usage_stats["total_cost"] += cost
    
    async def _log_request(self, request: Dict, response: Dict, pii_result: PIIDetectionResult, 
                          provider: str, compliance: Dict):
        """Log request for audit (anonymized)"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "provider": provider,
            "pii_detected": pii_result.has_pii,
            "pii_types": pii_result.detected_types,
            "compliance_required": compliance["checks_required"],
            "message_length": len(request["message"]),
            "response_length": len(response["text"]),
            # Don't log actual content for privacy
        }
        
        self.request_log.append(log_entry)
        
        # Implement data retention (remove old logs)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_PERIOD_DAYS)
        self.request_log = [
            entry for entry in self.request_log 
            if entry["timestamp"] > cutoff_date
        ]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats.copy()

# Initialize provider manager
provider_manager = LLMProviderManager()

# API Endpoints
@router.post("/chat", response_model=LLMGatewayResponse)
async def llm_chat(
    request: LLMGatewayRequest,
    background_tasks: BackgroundTasks
):
    """
    Main LLM Gateway endpoint for chat completions
    
    This endpoint:
    1. Scrubs PII from requests and responses
    2. Routes to appropriate LLM provider
    3. Ensures compliance with data protection policies
    4. Tracks usage and costs
    5. Implements fallback logic
    """
    try:
        response = await provider_manager.generate_response(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in LLM Gateway: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/providers")
async def list_providers():
    """List available LLM providers and their status"""
    providers_status = {}
    
    for name, provider in provider_manager.providers.items():
        try:
            is_available = await provider.is_available()
            supported_models = await provider.get_supported_models()
            
            providers_status[name] = {
                "available": is_available,
                "models": supported_models
            }
        except Exception as e:
            providers_status[name] = {
                "available": False,
                "error": str(e),
                "models": []
            }
    
    return {
        "providers": providers_status,
        "default_provider": settings.ZYNX_LLM_PROVIDER,
        "fallback_order": provider_manager.fallback_order
    }

@router.get("/usage")
async def get_usage_stats():
    """Get usage statistics and metrics"""
    return {
        "usage_stats": provider_manager.get_usage_stats(),
        "retention_period_days": settings.RETENTION_PERIOD_DAYS,
        "cross_border_compliance": settings.CROSS_BORDER_COMPLIANCE
    }

@router.get("/health")
async def health_check():
    """Health check for LLM Gateway"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "providers": {}
    }
    
    all_healthy = True
    
    for name, provider in provider_manager.providers.items():
        try:
            is_available = await provider.is_available()
            health_status["providers"][name] = {
                "available": is_available,
                "status": "healthy" if is_available else "unavailable"
            }
            if not is_available:
                all_healthy = False
        except Exception as e:
            health_status["providers"][name] = {
                "available": False,
                "status": "error",
                "error": str(e)
            }
            all_healthy = False
    
    health_status["overall_status"] = "healthy" if all_healthy else "degraded"
    return health_status