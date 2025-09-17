"""
LLM API Router

Provides endpoints for interacting with the LLM proxy service.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.llm_proxy import llm_proxy, LLMResponse

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


class MessageModel(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class GenerateRequest(BaseModel):
    provider: str  # "openai", "anthropic", "ollama"
    model: str
    messages: List[MessageModel]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    additional_params: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/ping")
async def ping():
    """Health check endpoint for LLM service."""
    return {
        "status": "ok",
        "service": "llm_proxy",
        "providers": ["openai", "anthropic", "ollama"]
    }


@router.post("/generate", response_model=GenerateResponse)
async def generate_completion(request: GenerateRequest):
    """
    Generate completion from specified LLM provider.
    
    Supports OpenAI, Anthropic, and Ollama providers with unified interface.
    """
    try:
        # Convert Pydantic models to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        additional_params = request.additional_params or {}
        
        # Call LLM proxy
        response = await llm_proxy.generate(
            provider=request.provider,
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            **additional_params
        )
        
        return GenerateResponse(
            content=response.content,
            model=response.model,
            provider=response.metadata.get("provider", request.provider),
            usage=response.usage,
            metadata=response.metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")


@router.get("/models")
async def list_available_models():
    """List available models for each provider."""
    return {
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "ollama": [
            "llama2",
            "codellama",
            "mistral"
        ]
    }