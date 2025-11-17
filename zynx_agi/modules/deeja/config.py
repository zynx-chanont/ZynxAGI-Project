"""
Deeja Module - Configuration
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeejaConfig(BaseModel):
    """Configuration for Deeja module"""
    
    # Module identification
    module_id: str = "deeja"
    module_name: str = "Deeja (ดีจ้า) - Emotional AI"
    version: str = "1.0.0"
    
    # Thai Cultural Markers
    thai_cultural_markers: Dict[str, List[str]] = Field(default_factory=lambda: {
        "kreng_jai": ["เกรงใจ", "กรุณา", "ขอโทษ", "รบกวน"],
        "sanuk": ["สนุก", "เล่น", "สบาย", "ผ่อนคลาย"],
        "mai_pen_rai": ["ไม่เป็นไร", "ไม่มีปัญหา", "ช่างมัน"],
        "bun_khun": ["บุญคุณ", "ขอบคุณ", "ขอบใจ", "กตัญญู"]
    })
    
    # Empathy Model Parameters
    emotional_awareness_weight: float = 0.3
    cultural_sensitivity_weight: float = 0.3
    response_appropriateness_weight: float = 0.2
    thai_cultural_weight: float = 0.2
    default_empathy_threshold: float = 0.7
    
    # Empathy Calibration
    baseline_empathy_score: float = 0.5
    cultural_bonus: float = 0.2
    emotional_resonance_multiplier: float = 1.5
    thai_context_boost: float = 0.3
    
    # Ethical Framework
    ethical_principles: List[str] = Field(default_factory=lambda: [
        "respect_for_persons",
        "beneficence",
        "non_maleficence",
        "justice",
        "cultural_sensitivity"
    ])
    
    thai_values: List[str] = Field(default_factory=lambda: [
        "kreng_jai_respect",
        "sanuk_positivity",
        "mai_pen_rai_acceptance",
        "family_harmony",
        "buddhist_compassion"
    ])
    
    # Language Processing
    thai_polite_particles: List[str] = Field(default_factory=lambda: [
        "ครับ", "ค่ะ", "คะ", "จ้ะ"
    ])
    
    thai_formal_pronouns: List[str] = Field(default_factory=lambda: [
        "กระผม", "ดิฉัน", "ท่าน", "คุณ"
    ])
    
    thai_informal_pronouns: List[str] = Field(default_factory=lambda: [
        "กู", "มึง", "เรา", "เธอ"
    ])
    
    # Storage Configuration
    storage_enabled: bool = True
    storage_path: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_interactions: bool = True
    
    class Config:
        extra = "allow"
