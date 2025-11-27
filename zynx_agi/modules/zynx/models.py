"""
Zynx Module - Data Models
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ZynxRequest(BaseModel):
    """Request model for Zynx module"""
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ZynxResponse(BaseModel):
    """Response model from Zynx module"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    platform_used: Optional[str] = None
    routing_decision: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    compliance_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PlatformStatus(BaseModel):
    """Status of an AI platform"""
    name: str
    status: str  # "available", "error", "fallback"
    priority: int
    initialized: bool = False
    last_check: Optional[str] = None
    error: Optional[str] = None


class OrchestrationRules(BaseModel):
    """Rules for AI orchestration"""
    cultural_context_threshold: float = 0.7
    emotional_intelligence_required: bool = True
    ip_guardrails_enabled: bool = True
    compliance_monitoring: bool = True
