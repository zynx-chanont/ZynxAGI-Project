"""
Zynx Module - Configuration
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ZynxConfig(BaseModel):
    """Configuration for Zynx module"""
    
    # Module identification
    module_id: str = "zynx_main"
    module_name: str = "Zynx Universal Orchestrator"
    version: str = "1.0.0"
    
    # AI Platform Configuration
    ai_platforms: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "openai": {"status": "available", "priority": 1},
        "anthropic": {"status": "available", "priority": 2},
        "google": {"status": "available", "priority": 3},
        "local_llm": {"status": "fallback", "priority": 4}
    })
    
    # Orchestration Rules
    orchestration_rules: Dict[str, Any] = Field(default_factory=lambda: {
        "cultural_context_threshold": 0.7,
        "emotional_intelligence_required": True,
        "ip_guardrails_enabled": True,
        "compliance_monitoring": True
    })
    
    # Storage Configuration
    storage_enabled: bool = True
    storage_path: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_interactions: bool = True
    
    # Performance Configuration
    timeout_seconds: int = 30
    max_retries: int = 3
    
    class Config:
        extra = "allow"
