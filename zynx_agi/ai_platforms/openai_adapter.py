import asyncio
from typing import Dict, Any, Optional, List
from .base_adapter import LLMProviderAdapter, LLMRequest, LLMResponse, LLMError
from .openai_client import OpenAIClient
from ..config.settings import settings

class OpenAIAdapter(LLMProviderAdapter):
    """OpenAI provider adapter for LLM Gateway"""
    
    def __init__(self):
        super().__init__("openai")
        self.client = None
        self.models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        # Cost per 1K tokens (approximate, should be updated with current pricing)
        self.cost_per_1k_tokens = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03}
        }
    
    def _get_client(self):
        """Get or create OpenAI client"""
        if self.client is None:
            try:
                self.client = OpenAIClient()
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                raise e
        return self.client
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI client"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Get OpenAI client
            client = self._get_client()
            
            # Use existing OpenAI client
            response = await client.generate_response(
                message=request.message,
                cultural_context=request.cultural_context,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Check if response contains error
            if "error" in response:
                raise Exception(f"{response['error']}: {response.get('message', '')}")
            
            return LLMResponse(
                text=response["text"],
                model=response.get("model", request.model or "gpt-3.5-turbo"),
                provider="openai",
                usage=response.get("usage", {}),
                cultural_context=response.get("cultural_context"),
                metadata=request.metadata,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {str(e)}")
            raise e
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available"""
        try:
            if not settings.OPENAI_API_KEY:
                return False
            
            # Try to get/create client
            client = self._get_client()
            
            # Simple availability check - try to get token usage
            usage = client.get_token_usage()
            return True
            
        except Exception as e:
            self.logger.warning(f"OpenAI availability check failed: {str(e)}")
            return False
    
    async def get_supported_models(self) -> List[str]:
        """Get supported OpenAI models"""
        return self.models.copy()
    
    async def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for OpenAI request"""
        try:
            model = request.model or "gpt-3.5-turbo"
            
            if model not in self.cost_per_1k_tokens:
                model = "gpt-3.5-turbo"  # Fallback to default pricing
            
            # Estimate input tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_input_tokens = len(request.message) / 4
            
            # Estimate output tokens (rough approximation based on max_tokens or default)
            estimated_output_tokens = request.max_tokens or 150
            
            # Calculate cost
            pricing = self.cost_per_1k_tokens[model]
            input_cost = (estimated_input_tokens / 1000) * pricing["input"]
            output_cost = (estimated_output_tokens / 1000) * pricing["output"]
            
            return input_cost + output_cost
            
        except Exception as e:
            self.logger.warning(f"Cost estimation error: {str(e)}")
            return 0.01  # Default fallback cost
    
    async def close(self):
        """Close the OpenAI client"""
        if self.client:
            await self.client.close()