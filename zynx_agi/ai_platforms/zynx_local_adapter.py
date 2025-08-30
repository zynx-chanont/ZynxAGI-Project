import asyncio
import httpx
from typing import Dict, Any, Optional, List
from .base_adapter import LLMProviderAdapter, LLMRequest, LLMResponse, LLMError
from ..config.settings import settings

class ZynxLocalAdapter(LLMProviderAdapter):
    """Zynx Local model adapter for LLM Gateway"""
    
    def __init__(self):
        super().__init__("zynx_local")
        self.api_url = settings.ZYNX_LOCAL_API_URL
        self.models = ["zynx-deeja-v1", "zynx-thai-v1"]
        self.timeout = 30
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Zynx Local model"""
        if not self.api_url:
            raise Exception("ZYNX_LOCAL_API_URL not configured")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Prepare request payload
            payload = {
                "message": request.message,
                "model": request.model or "zynx-deeja-v1",
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 150,
                "cultural_context": request.cultural_context
            }
            
            # Make request to Zynx Local API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return LLMResponse(
                text=result.get("text", result.get("message", "")),
                model=result.get("model", payload["model"]),
                provider="zynx_local",
                usage=result.get("usage", {
                    "prompt_tokens": len(request.message.split()),
                    "completion_tokens": len(result.get("text", "").split()),
                    "total_tokens": len(request.message.split()) + len(result.get("text", "").split())
                }),
                cultural_context=result.get("cultural_context", request.cultural_context),
                metadata=request.metadata,
                processing_time_ms=processing_time
            )
            
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Zynx Local HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Zynx Local API error: {e.response.status_code}")
        except httpx.TimeoutException:
            self.logger.error("Zynx Local request timeout")
            raise Exception("Zynx Local API timeout")
        except Exception as e:
            self.logger.error(f"Zynx Local generation error: {str(e)}")
            raise e
    
    async def is_available(self) -> bool:
        """Check if Zynx Local is available"""
        if not self.api_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Zynx Local availability check failed: {str(e)}")
            return False
    
    async def get_supported_models(self) -> List[str]:
        """Get supported Zynx Local models"""
        return self.models.copy()
    
    async def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for Zynx Local request (free for now)"""
        return 0.0  # Zynx Local is free for internal use