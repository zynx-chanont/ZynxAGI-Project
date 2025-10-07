"""
Deeja Agent Module (น้องดีจ้า)
ZPDL v1.0 Compliant Emotional AI Agent
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from ..cultural.thai_cultural_engine import ThaiCulturalEngine

logger = logging.getLogger(__name__)

class EmpatheticResponse(BaseModel):
    """Empathetic response model"""
    text: str
    emotion_score: float = Field(ge=0.0, le=1.0)
    cultural_context: str
    politeness_level: float = Field(ge=0.0, le=1.0)
    thai_elements: List[str] = Field(default_factory=list)

class DeejaAgent(BaseModel):
    """
    Deeja Agent - Thai Emotional AI with Cultural Intelligence
    น้องดีจ้า - AI ที่เข้าใจอารมณ์และวัฒนธรรมไทย
    ZPDL v1.0 Compliant with IP Attribution
    """
    
    # ZPDL v1.0 Metadata
    agent_id: str = Field(default="deeja-v1.0")
    agent_name: str = Field(default="น้องดีจ้า (Deeja)")
    author: str = Field(default="Chanont Wankaew")
    copyright: str = Field(default="© 2025 Zynx Thailand. All rights reserved.")
    license: str = Field(default="ZPDL v1.0")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Agent Configuration
    empathy_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    cultural_weight: float = Field(default=0.9, ge=0.0, le=1.0)
    thai_context_priority: bool = Field(default=True)
    
    # Internal state
    cultural_engine: Optional[ThaiCulturalEngine] = None
    interaction_count: int = Field(default=0)
    
    class Config:
        """Pydantic configuration"""
        extra = "forbid"
        validate_assignment = True
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self.cultural_engine = ThaiCulturalEngine()
        logger.info(f"Deeja Agent initialized - {self.author}")
    
    def generate_metadata_hash(self) -> str:
        """Generate SHA-256 hash for metadata integrity"""
        metadata = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "author": self.author,
            "copyright": self.copyright,
            "license": self.license,
            "created_at": self.created_at.isoformat()
        }
        metadata_str = json.dumps(metadata, sort_keys=True)
        return hashlib.sha256(metadata_str.encode()).hexdigest()
    
    def get_attribution(self) -> Dict[str, Any]:
        """Get ZPDL v1.0 compliant attribution"""
        return {
            "agent": self.agent_name,
            "author": self.author,
            "copyright": self.copyright,
            "license": self.license,
            "agent_id": self.agent_id,
            "metadata_hash": self.generate_metadata_hash(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_message(self, text: str, context: str = "casual") -> EmpatheticResponse:
        """Process message with Thai cultural empathy"""
        self.interaction_count += 1
        
        try:
            # Analyze cultural context
            is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in text)
            
            # Extract emotional elements
            emotion_score = await self._analyze_emotion(text, is_thai)
            
            # Generate culturally appropriate response
            cultural_response = await self._generate_cultural_response(
                text, context, is_thai, emotion_score
            )
            
            # Log interaction for defensive publication
            await self._log_interaction(text, cultural_response)
            
            return cultural_response
            
        except Exception as e:
            logger.error(f"Error processing message in Deeja: {e}")
            # Fallback empathetic response
            return EmpatheticResponse(
                text="ขออภัยค่ะ มีปัญหาเล็กน้อย แต่ดีจ้ายังอยู่ที่นี่เพื่อช่วยเหลือค่ะ 🙏",
                emotion_score=0.7,
                cultural_context="thai_formal",
                politeness_level=0.9,
                thai_elements=["ค่ะ", "ขออภัย", "🙏"]
            )
    
    async def _analyze_emotion(self, text: str, is_thai: bool) -> float:
        """Analyze emotional content of text"""
        # Simple emotion analysis - in production this would use ML models
        positive_words = ["ดี", "สุข", "ยินดี", "รัก", "happy", "good", "love", "joy"]
        negative_words = ["เศร้า", "โกรธ", "เสียใจ", "หงุดหงิด", "sad", "angry", "upset"]
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        if positive_count > negative_count:
            return min(0.8 + positive_count * 0.1, 1.0)
        elif negative_count > positive_count:
            return max(0.3 - negative_count * 0.1, 0.0)
        else:
            return 0.6  # Neutral
    
    async def _generate_cultural_response(
        self, 
        text: str, 
        context: str, 
        is_thai: bool, 
        emotion_score: float
    ) -> EmpatheticResponse:
        """Generate culturally appropriate empathetic response"""
        
        if is_thai:
            # Thai cultural response
            if context == "formal":
                response_text = "เข้าใจในความรู้สึกของคุณค่ะ ดีจ้าอยู่ที่นี่เพื่อช่วยเหลือเสมอค่ะ 🙏"
                politeness = 0.9
                thai_elements = ["ค่ะ", "🙏"]
            else:
                response_text = "เข้าใจนะคะ ดีจ้าพร้อมช่วยเหลือเสมอเลยค่ะ 😊"
                politeness = 0.8
                thai_elements = ["นะคะ", "ค่ะ", "😊"]
                
            cultural_context = "thai_empathetic"
        else:
            # International response with Thai heart
            response_text = "I understand your feelings. Deeja is here to help with Thai cultural warmth 🌟"
            politeness = 0.7
            thai_elements = ["Thai cultural warmth"]
            cultural_context = "international_thai_influenced"
        
        return EmpatheticResponse(
            text=response_text,
            emotion_score=emotion_score,
            cultural_context=cultural_context,
            politeness_level=politeness,
            thai_elements=thai_elements
        )
    
    async def _log_interaction(self, input_text: str, response: EmpatheticResponse):
        """Log interaction for defensive publication"""
        interaction_log = {
            "type": "deeja_interaction",
            "agent": self.agent_name,
            "interaction_id": f"deeja-{self.interaction_count}",
            "attribution": self.get_attribution(),
            "timestamp": datetime.now().isoformat(),
            "metadata_hash": hashlib.sha256(f"{input_text}{response.text}".encode()).hexdigest()
        }
        
        logger.info(f"Deeja Interaction Log: {interaction_log}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent": self.agent_name,
            "status": "active",
            "interactions": self.interaction_count,
            "empathy_threshold": self.empathy_threshold,
            "cultural_weight": self.cultural_weight,
            "attribution": self.get_attribution(),
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }
    
    async def self_reflect(self) -> Dict[str, Any]:
        """Deeja's self-reflection process for empathy calibration"""
        reflection = {
            "current_empathy": self.empathy_threshold,
            "interactions_today": self.interaction_count,
            "cultural_alignment": "Thai-centric with global awareness",
            "emotional_state": "Compassionate and ready to help",
            "attribution": self.get_attribution(),
            "reflection_time": datetime.now().isoformat()
        }
        
        logger.info(f"Deeja Self-Reflection: {reflection}")
        return reflection