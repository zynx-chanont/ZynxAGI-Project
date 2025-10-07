"""
LLM Proxy Service

Provides a unified interface for interacting with multiple LLM providers:
- OpenAI (GPT models)
- Anthropic (Claude models)  
- Ollama (Local models)
"""

import os
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProxy:
    """Unified LLM proxy for multiple providers."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
    async def generate(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from specified LLM provider.
        
        Args:
            provider: LLM provider ("openai", "anthropic", "ollama")
            model: Model name
            messages: List of message dictionaries with "role" and "content"
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        if provider == "openai":
            return await self._call_openai(model, messages, max_tokens, temperature, **kwargs)
        elif provider == "anthropic":
            return await self._call_anthropic(model, messages, max_tokens, temperature, **kwargs)
        elif provider == "ollama":
            return await self._call_ollama(model, messages, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _call_openai(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        max_tokens: int, 
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """Call OpenAI API."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                usage=data.get("usage"),
                metadata={"provider": "openai"}
            )
    
    async def _call_anthropic(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        max_tokens: int, 
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """Call Anthropic Claude API."""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
            
        # Convert messages format for Claude
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": claude_messages,
            **kwargs
        }
        
        if system_message:
            payload["system"] = system_message
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["content"][0]["text"],
                model=data["model"],
                usage=data.get("usage"),
                metadata={"provider": "anthropic"}
            )
    
    async def _call_ollama(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        max_tokens: int, 
        temperature: float,
        **kwargs
    ) -> LLMResponse:
        """Call Ollama local API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        **kwargs
                    },
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["message"]["content"],
                model=model,
                metadata={"provider": "ollama"}
            )


# Global instance
llm_proxy = LLMProxy()