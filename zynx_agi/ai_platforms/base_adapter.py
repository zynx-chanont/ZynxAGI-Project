from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """Standardized LLM request structure"""
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    cultural_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMResponse:
    """Standardized LLM response structure"""
    text: str
    model: str
    provider: str
    usage: Dict[str, int]
    cultural_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time_ms: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass 
class LLMError:
    """Standardized LLM error structure"""
    error_type: str
    message: str
    retryable: bool
    provider: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class LLMProviderAdapter(ABC):
    """Abstract base class for LLM provider adapters"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"{__name__}.{provider_name}")
    
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from the LLM provider"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available"""
        pass
    
    @abstractmethod
    async def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        pass
    
    @abstractmethod
    async def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for the request"""
        pass
    
    def _handle_error(self, error: Exception, context: str = "") -> LLMError:
        """Handle and standardize errors"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Determine if error is retryable
        retryable = error_type in [
            "APITimeoutError", "RateLimitError", "ServiceUnavailableError",
            "ConnectionError", "HTTPException"
        ]
        
        self.logger.error(f"{context} - {error_type}: {error_message}")
        
        return LLMError(
            error_type=error_type,
            message=error_message,
            retryable=retryable,
            provider=self.provider_name
        )