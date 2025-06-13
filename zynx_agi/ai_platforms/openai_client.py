from typing import Dict, Any, List, Optional, Union
import openai
from openai import AsyncOpenAI
import asyncio
import logging
from datetime import datetime
import json
import tiktoken
from ..config.settings import settings
from ..cultural.thai_cultural_engine import ThaiCulturalEngine

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI client with cultural context integration and optimization"""
    
    def __init__(self):
        self.settings = settings.ai
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.cultural_engine = ThaiCulturalEngine()
        self.model = self.settings.OPENAI_MODEL
        self.max_tokens = self.settings.OPENAI_MAX_TOKENS
        self.temperature = self.settings.OPENAI_TEMPERATURE
        self.encoding = tiktoken.encoding_for_model(self.model)
        self._token_usage_stats = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "last_reset": datetime.now()
        }
        
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def _optimize_prompt(self, prompt: str, max_tokens: int) -> str:
        """Optimize prompt to fit within token limit"""
        tokens = self._count_tokens(prompt)
        if tokens <= max_tokens:
            return prompt
            
        # Truncate prompt while preserving meaning
        words = prompt.split()
        while self._count_tokens(" ".join(words)) > max_tokens and words:
            words.pop()
        return " ".join(words)
    
    def _create_cultural_prompt(self, 
                              message: str, 
                              cultural_context: Optional[Dict[str, Any]] = None,
                              max_tokens: Optional[int] = None) -> str:
        """Create a culturally aware prompt with token optimization"""
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
        
        if max_tokens:
            base_prompt = self._optimize_prompt(base_prompt, max_tokens)
            
        return base_prompt
    
    def _update_token_usage(self, usage: Dict[str, int]):
        """Update token usage statistics"""
        self._token_usage_stats["total_tokens"] += usage.get("total_tokens", 0)
        self._token_usage_stats["prompt_tokens"] += usage.get("prompt_tokens", 0)
        self._token_usage_stats["completion_tokens"] += usage.get("completion_tokens", 0)
        
        # Reset stats if more than 24 hours have passed
        if (datetime.now() - self._token_usage_stats["last_reset"]).days >= 1:
            self._token_usage_stats = {
                "total_tokens": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "last_reset": datetime.now()
            }
    
    async def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle different types of errors"""
        error_type = type(error).__name__
        error_message = str(error)
        
        if isinstance(error, openai.APIError):
            return {
                "error": "API Error",
                "message": error_message,
                "retryable": True
            }
        elif isinstance(error, openai.RateLimitError):
            return {
                "error": "Rate Limit Error",
                "message": error_message,
                "retryable": True
            }
        elif isinstance(error, openai.APITimeoutError):
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
        """Process OpenAI's response with cultural awareness"""
        try:
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Process with cultural engine if context provided
            if cultural_context:
                processed = await self.cultural_engine.process_message({
                    "text": response_text,
                    "context_type": "formal" if cultural_context.get('formality_level', 0.7) > 0.7 else "informal"
                })
                response_text = processed["adjusted_text"]
            
            # Update token usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            self._update_token_usage(usage)
            
            return {
                "text": response_text,
                "model": self.model,
                "usage": usage,
                "cultural_context": cultural_context
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return await self._handle_error(e)
    
    async def generate_response(self, 
                              message: str, 
                              cultural_context: Optional[Dict[str, Any]] = None,
                              temperature: Optional[float] = None,
                              max_tokens: Optional[int] = None,
                              max_retries: int = 3) -> Dict[str, Any]:
        """Generate a culturally aware response from OpenAI"""
        retry_count = 0
        last_error = None
        
        # Use provided parameters or defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        while retry_count < max_retries:
            try:
                # Create culturally aware prompt
                prompt = self._create_cultural_prompt(message, cultural_context, tokens)
                
                # Generate response
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=tokens,
                    temperature=temp,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a culturally aware AI assistant. Respond appropriately while considering cultural context."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
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
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage statistics"""
        return {
            "stats": self._token_usage_stats,
            "time_since_reset": str(datetime.now() - self._token_usage_stats["last_reset"])
        }
    
    async def close(self):
        """Close the client connection"""
        await self.client.close() 