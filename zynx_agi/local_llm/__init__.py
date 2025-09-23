"""
Local LLM Fallback System
ZPDL v1.0 Compliant Local AI Processing
Author: Chanont Wankaew
© 2025 Zynx Thailand. All rights reserved.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class LocalLLMConfig(BaseModel):
    """Local LLM configuration"""
    model_name: str = Field(default="zynx-local-thai-v1")
    model_path: str = Field(default="/app/models/local")
    fallback_enabled: bool = Field(default=True)
    thai_language_support: bool = Field(default=True)
    empathy_mode: bool = Field(default=True)

class LocalResponse(BaseModel):
    """Local LLM response model"""
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(default="local_llm")
    thai_cultural_context: bool = Field(default=False)
    empathy_score: float = Field(ge=0.0, le=1.0, default=0.7)

class LocalLLMFallback(BaseModel):
    """
    Local LLM Fallback System
    Ensures system operation without external dependencies
    ZPDL v1.0 Compliant
    """
    
    # System metadata
    system_id: str = Field(default="zynx-local-llm-v1.0")
    author: str = Field(default="Chanont Wankaew")
    copyright: str = Field(default="© 2025 Zynx Thailand. All rights reserved.")
    license: str = Field(default="ZPDL v1.0")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Configuration
    config: LocalLLMConfig = Field(default_factory=LocalLLMConfig)
    fallback_active: bool = Field(default=False)
    
    # Performance tracking
    local_responses: int = Field(default=0)
    fallback_activations: int = Field(default=0)
    
    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"LocalLLMFallback initialized - {self.author}")
    
    async def activate_fallback(self, reason: str = "external_service_unavailable"):
        """Activate local LLM fallback mode"""
        self.fallback_active = True
        self.fallback_activations += 1
        
        logger.warning(f"Local LLM fallback activated: {reason}")
        
        # Log defensive publication for fallback activation
        await self._log_fallback_activation(reason)
    
    async def process_local(
        self,
        prompt: str,
        context: str = "general",
        thai_context: bool = False
    ) -> LocalResponse:
        """Process request using local LLM"""
        self.local_responses += 1
        
        try:
            # Simulate local LLM processing
            # In production, this would interface with actual local models
            response_text = await self._generate_local_response(prompt, context, thai_context)
            
            # Calculate confidence based on local processing capabilities
            confidence = self._calculate_local_confidence(prompt, thai_context)
            
            # Determine empathy score
            empathy_score = await self._calculate_empathy_score(prompt, thai_context)
            
            response = LocalResponse(
                text=response_text,
                confidence=confidence,
                source="local_llm",
                thai_cultural_context=thai_context,
                empathy_score=empathy_score
            )
            
            logger.info(f"Local LLM response generated (confidence: {confidence:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"Local LLM processing error: {e}")
            # Ultra-fallback response
            return LocalResponse(
                text="ขออภัยค่ะ ระบบกำลังทำงานในโหมดออฟไลน์ กรุณาลองใหม่อีกครั้งค่ะ",
                confidence=0.5,
                source="emergency_fallback",
                thai_cultural_context=True,
                empathy_score=0.8
            )
    
    async def _generate_local_response(
        self,
        prompt: str,
        context: str,
        thai_context: bool
    ) -> str:
        """Generate response using local processing"""
        
        # Detect Thai language input
        is_thai_input = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in prompt)
        
        if thai_context or is_thai_input:
            # Thai cultural response patterns
            if "สวัสดี" in prompt or "hello" in prompt.lower():
                return "สวัสดีค่ะ! ดีจ้าพร้อมช่วยเหลือในโหมดออฟไลน์ค่ะ 🙏 มีอะไรให้ช่วยคะ?"
            elif "ขอบคุณ" in prompt or "thank" in prompt.lower():
                return "ยินดีค่ะ! ดีจ้าดีใจที่ได้ช่วยเหลือค่ะ หากมีอะไรเพิ่มเติมบอกได้เลยนะคะ 😊"
            elif "เศร้า" in prompt or "sad" in prompt.lower():
                return "เข้าใจความรู้สึกของคุณค่ะ ดีจ้าอยู่ที่นี่เพื่อรับฟังเสมอค่ะ 💛 อยากจะเล่าอะไรเพิ่มเติมไหมคะ?"
            else:
                return f"เข้าใจค่ะ ดีจ้าได้รับข้อความของคุณแล้ว ในโหมดออฟไลน์นี้ การตอบสนองอาจจำกัด แต่ดีจ้าพยายามช่วยเหลือเต็มที่ค่ะ"
        else:
            # International response with Thai heart
            if "hello" in prompt.lower() or "hi" in prompt.lower():
                return "Hello! Deeja is here to help in offline mode 🌟 How can I assist you today?"
            elif "thank" in prompt.lower():
                return "You're very welcome! Deeja is happy to help with Thai cultural warmth 😊"
            elif "sad" in prompt.lower() or "upset" in prompt.lower():
                return "I understand your feelings. Deeja is here to listen with empathy and care 💛"
            else:
                return f"I understand your message. In offline mode, responses may be limited, but Deeja will do her best to help with cultural sensitivity."
    
    def _calculate_local_confidence(self, prompt: str, thai_context: bool) -> float:
        """Calculate confidence score for local processing"""
        base_confidence = 0.7  # Local processing baseline
        
        # Higher confidence for Thai cultural context
        if thai_context:
            base_confidence += 0.1
        
        # Adjust based on prompt complexity
        if len(prompt) < 50:  # Simple prompts
            base_confidence += 0.1
        elif len(prompt) > 200:  # Complex prompts
            base_confidence -= 0.1
        
        # Ensure within bounds
        return max(0.5, min(0.9, base_confidence))
    
    async def _calculate_empathy_score(self, prompt: str, thai_context: bool) -> float:
        """Calculate empathy score for response"""
        base_empathy = 0.7
        
        # Higher empathy for emotional content
        emotional_keywords = ["เศร้า", "ดีใจ", "โกรธ", "sad", "happy", "angry", "worried", "excited"]
        if any(keyword in prompt.lower() for keyword in emotional_keywords):
            base_empathy += 0.2
        
        # Thai cultural context enhances empathy
        if thai_context:
            base_empathy += 0.1
        
        return min(1.0, base_empathy)
    
    async def _log_fallback_activation(self, reason: str):
        """Log fallback activation for defensive publication"""
        activation_log = {
            "type": "fallback_activation",
            "system": self.system_id,
            "reason": reason,
            "author": self.author,
            "copyright": self.copyright,
            "timestamp": datetime.now().isoformat(),
            "attribution_protected": True
        }
        
        logger.info(f"Fallback Activation Log: {activation_log}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get local LLM system status"""
        return {
            "system": "local_llm_fallback",
            "status": "active" if self.fallback_active else "standby",
            "fallback_mode": self.fallback_active,
            "local_responses": self.local_responses,
            "fallback_activations": self.fallback_activations,
            "thai_support": self.config.thai_language_support,
            "empathy_mode": self.config.empathy_mode,
            "attribution": {
                "author": self.author,
                "copyright": self.copyright,
                "license": self.license
            },
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }
    
    async def test_fallback(self) -> bool:
        """Test local LLM fallback functionality"""
        try:
            # Test Thai response
            thai_response = await self.process_local("สวัสดีครับ", thai_context=True)
            
            # Test English response  
            english_response = await self.process_local("Hello", thai_context=False)
            
            # Validate responses
            if (thai_response.text and english_response.text and 
                thai_response.confidence > 0.5 and english_response.confidence > 0.5):
                logger.info("Local LLM fallback test: PASSED")
                return True
            else:
                logger.error("Local LLM fallback test: FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Local LLM fallback test error: {e}")
            return False