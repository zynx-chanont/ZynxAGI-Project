"""
Deeja Module - Data Models
"""

from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DeejaRequest(BaseModel):
    """Request model for Deeja module"""
    message: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    language: Optional[str] = None  # Auto-detect if not provided
    formality_hint: Optional[str] = None  # "formal", "casual", "friendly"


class CulturalAnalysis(BaseModel):
    """Cultural analysis result"""
    language_detected: str = "unknown"
    formality_level: float = 0.5  # 0.0 (very casual) to 1.0 (very formal)
    cultural_context: str = "neutral"
    thai_markers: List[Dict[str, Any]] = Field(default_factory=list)
    detected_context: str = "general"
    cultural_appropriateness: float = 1.0
    politeness_indicators: List[str] = Field(default_factory=list)


class EmotionalAnalysis(BaseModel):
    """Emotional analysis result"""
    sentiment: str = "neutral"  # "positive", "negative", "neutral"
    emotional_intensity: float = 0.5  # 0.0 to 1.0
    detected_emotions: List[str] = Field(default_factory=list)
    empathy_required: bool = False
    emotional_support_needed: bool = False


class DeejaResponse(BaseModel):
    """Response model from Deeja module"""
    success: bool
    message: str
    cultural_analysis: Optional[CulturalAnalysis] = None
    emotional_analysis: Optional[EmotionalAnalysis] = None
    empathy_score: Optional[float] = None
    response_language: Optional[str] = None
    cultural_appropriateness: Optional[float] = None
    ethical_assessment: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None


class ThaiCulturalMarker(BaseModel):
    """Thai cultural marker definition"""
    type: str  # "kreng_jai", "sanuk", "mai_pen_rai", etc.
    markers: List[str]
    weight: float = 1.0


class EmpathyCalibration(BaseModel):
    """Empathy scoring calibration parameters"""
    baseline_score: float = 0.5
    cultural_bonus: float = 0.2
    emotional_resonance_multiplier: float = 1.5
    thai_context_boost: float = 0.3
