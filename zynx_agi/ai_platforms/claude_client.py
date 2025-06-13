from typing import Dict, Any, List, Optional, Union
import anthropic
from anthropic import AsyncAnthropic
import asyncio
import logging
from datetime import datetime
import json
from ..config.settings import settings
from ..cultural.thai_cultural_engine import ThaiCulturalEngine

logger = logging.getLogger(__name__)

class ClaudeClient:
    """Anthropic Claude client with cultural context awareness"""
    
    def __init__(self):
        self.settings = settings.ai
        self.client = AsyncAnthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        self.cultural_engine = ThaiCulturalEngine()
        self.model = self.settings.ANTHROPIC_MODEL
        self.max_tokens = self.settings.ANTHROPIC_MAX_TOKENS
        self.temperature = self.settings.ANTHROPIC_TEMPERATURE
        self._capabilities = None
        self._last_capability_check = None
        
    async def _check_capabilities(self) -> Dict[str, Any]:
        """Check Claude's capabilities and cache the results"""
        if (self._capabilities and self._last_capability_check and 
            (datetime.now() - self._last_capability_check).seconds < 3600):
            return self._capabilities
            
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system="You are a capability reporting assistant. Report your capabilities in JSON format.",
                messages=[{
                    "role": "user",
                    "content": "What are your capabilities? Report in JSON format with fields: model_name, max_tokens, supported_features, cultural_awareness, language_support."
                }]
            )
            
            capabilities = json.loads(response.content[0].text)
            self._capabilities = capabilities
            self._last_capability_check = datetime.now()
            return capabilities
            
        except Exception as e:
            logger.error(f"Error checking Claude capabilities: {str(e)}")
            return {
                "model_name": self.model,
                "max_tokens": self.max_tokens,
                "supported_features": ["text_generation", "cultural_awareness"],
                "cultural_awareness": True,
                "language_support": ["en", "th"]
            }
    
    def _create_cultural_prompt(self, 
                              message: str, 
                              cultural_context: Optional[Dict[str, Any]] = None) -> str:
        """Create a culturally aware prompt"""
        base_prompt = f"""You are a culturally aware AI assistant. 
        Respond appropriately to the following message while considering cultural context.
        
        Message: {message}
        """
        
        if cultural_context:
            cultural_guidance = f"""
            Cultural Context:
            - Formality Level: {cultural_context.get('formality_level', 0.7)}
            - Politeness Level: {cultural_context.get('politeness_level', 0.8)}
            - Cultural Elements: {', '.join(cultural_context.get('cultural_patterns', []))}
            
            Please adjust your response to match these cultural parameters.
            """
            base_prompt += cultural_guidance
            
        return base_prompt
    
    async def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle different types of errors"""
        error_type = type(error).__name__
        error_message = str(error)
        
        if isinstance(error, anthropic.APIError):
            return {
                "error": "API Error",
                "message": error_message,
                "retryable": True
            }
        elif isinstance(error, anthropic.RateLimitError):
            return {
                "error": "Rate Limit Error",
                "message": error_message,
                "retryable": True
            }
        elif isinstance(error, anthropic.APITimeoutError):
            return {
                "error": "Timeout Error",
                "message": error_message,
                "retryable": True
            }
        else:
            return {
                "error": "Unknown Error",
                "message": error_message,
                "retryable": False
            }
    
    async def _process_response(self, 
                              response: Any, 
                              cultural_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process Claude's response with cultural awareness"""
        try:
            # Extract the response text
            response_text = response.content[0].text
            
            # Process with cultural engine if context provided
            if cultural_context:
                processed = await self.cultural_engine.process_message({
                    "text": response_text,
                    "context_type": "formal" if cultural_context.get('formality_level', 0.7) > 0.7 else "informal"
                })
                response_text = processed["adjusted_text"]
            
            return {
                "text": response_text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "cultural_context": cultural_context
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return await self._handle_error(e)
    
    async def generate_response(self, 
                              message: str, 
                              cultural_context: Optional[Dict[str, Any]] = None,
                              max_retries: int = 3) -> Dict[str, Any]:
        """Generate a culturally aware response from Claude"""
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Create culturally aware prompt
                prompt = self._create_cultural_prompt(message, cultural_context)
                
                # Generate response
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system="You are a culturally aware AI assistant. Respond appropriately while considering cultural context.",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                # Process and return response
                return await self._process_response(response, cultural_context)
                
            except Exception as e:
                last_error = e
                error_info = await self._handle_error(e)
                
                if not error_info["retryable"]:
                    return error_info
                
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                continue
        
        # If all retries failed
        return await self._handle_error(last_error)
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get Claude's capabilities"""
        return await self._check_capabilities()
    
    async def close(self):
        """Close the client connection"""
        await self.client.close() 