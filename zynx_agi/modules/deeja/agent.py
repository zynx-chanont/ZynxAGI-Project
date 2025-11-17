"""
Deeja Module (ดีจ้า) - Main Agent Implementation
================================================

Self-contained module for emotional AI with Thai cultural intelligence.
"""

import re
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .config import DeejaConfig
from .models import (
    DeejaRequest,
    DeejaResponse,
    CulturalAnalysis,
    EmotionalAnalysis
)


logger = logging.getLogger(__name__)


class DeejaModule:
    """
    Deeja (ดีจ้า) - Emotional AI & Cultural Intelligence Module
    
    A self-contained, independently usable module for:
    - Cultural analysis (Thai specialization)
    - Emotional intelligence
    - Empathy scoring
    - Culturally appropriate responses
    - Ethical reasoning
    
    Example:
        >>> deeja = DeejaModule()
        >>> await deeja.initialize()
        >>> response = await deeja.process(DeejaRequest(message="สวัสดีครับ"))
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Deeja module
        
        Args:
            config: Optional configuration dictionary or DeejaConfig instance
        """
        if isinstance(config, DeejaConfig):
            self.config = config
        else:
            self.config = DeejaConfig(**(config or {}))
        
        self.module_id = self.config.module_id
        self.active = False
        self.cultural_contexts = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.module_id}")
        self.logger.setLevel(getattr(logging, self.config.log_level))
    
    async def initialize(self) -> None:
        """Initialize the Deeja module"""
        self.logger.info(f"Initializing Deeja module: {self.module_id}")
        
        # Initialize cultural models
        await self._initialize_cultural_models()
        
        # Setup empathy scoring
        await self._setup_empathy_scoring()
        
        # Initialize ethical reasoning
        await self._setup_ethical_reasoning()
        
        self.active = True
        self.logger.info("Deeja module initialization complete - Thai cultural intelligence active")
    
    async def _initialize_cultural_models(self) -> None:
        """Initialize Thai cultural analysis models"""
        self.cultural_contexts = {
            "formal_business": {
                "formality_level": 0.9,
                "required_markers": ["kreng_jai", "bun_khun"],
                "appropriate_responses": ["respectful", "hierarchical"]
            },
            "casual_social": {
                "formality_level": 0.4,
                "required_markers": ["sanuk", "mai_pen_rai"],
                "appropriate_responses": ["friendly", "relaxed"]
            },
            "family_intimate": {
                "formality_level": 0.2,
                "required_markers": ["family_terms", "warm_language"],
                "appropriate_responses": ["caring", "supportive"]
            }
        }
        self.logger.info("Cultural models initialized")
    
    async def _setup_empathy_scoring(self) -> None:
        """Setup empathy scoring system"""
        self.empathy_calibration = {
            "baseline_score": self.config.baseline_empathy_score,
            "cultural_bonus": self.config.cultural_bonus,
            "emotional_resonance_multiplier": self.config.emotional_resonance_multiplier,
            "thai_context_boost": self.config.thai_context_boost
        }
        self.logger.info("Empathy scoring system configured")
    
    async def _setup_ethical_reasoning(self) -> None:
        """Setup ethical reasoning framework"""
        self.ethical_framework = {
            "principles": self.config.ethical_principles,
            "thai_values": self.config.thai_values
        }
        self.logger.info("Ethical reasoning framework initialized")
    
    async def process(self, request: DeejaRequest) -> DeejaResponse:
        """
        Process a request through Deeja's emotional and cultural intelligence
        
        Args:
            request: DeejaRequest containing message and context
            
        Returns:
            DeejaResponse with analysis and culturally appropriate response
        """
        if not self.active:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            # Perform cultural analysis
            cultural_analysis = await self._analyze_cultural_context(request)
            
            # Perform emotional analysis
            emotional_analysis = await self._analyze_emotional_intelligence(request)
            
            # Calculate empathy score
            empathy_score = await self._calculate_empathy_score(
                request, cultural_analysis, emotional_analysis
            )
            
            # Apply ethical reasoning
            ethical_assessment = await self._apply_ethical_reasoning(request)
            
            # Generate culturally appropriate response
            response_message = await self._generate_response(
                request, cultural_analysis, emotional_analysis, empathy_score
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return DeejaResponse(
                success=True,
                message=response_message,
                cultural_analysis=cultural_analysis,
                emotional_analysis=emotional_analysis,
                empathy_score=empathy_score,
                response_language=cultural_analysis.language_detected,
                cultural_appropriateness=cultural_analysis.cultural_appropriateness,
                ethical_assessment=ethical_assessment,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return DeejaResponse(
                success=False,
                message="Processing failed",
                error=str(e)
            )
    
    async def _analyze_cultural_context(self, request: DeejaRequest) -> CulturalAnalysis:
        """Analyze cultural context with Thai specialization"""
        message = request.message
        
        analysis = CulturalAnalysis(
            language_detected="unknown",
            formality_level=0.5,
            cultural_context="neutral",
            thai_markers=[],
            detected_context="general",
            cultural_appropriateness=1.0
        )
        
        # Detect Thai language
        thai_characters = re.findall(r'[\u0E00-\u0E7F]', message)
        if thai_characters:
            analysis.language_detected = "thai"
            analysis.cultural_appropriateness += 0.3
        else:
            # Check for English or other languages
            analysis.language_detected = "english"
        
        # Check for Thai cultural markers
        for marker_type, markers in self.config.thai_cultural_markers.items():
            found_markers = [marker for marker in markers if marker in message]
            if found_markers:
                analysis.thai_markers.append({
                    "type": marker_type,
                    "markers": found_markers
                })
        
        # Determine formality level
        formal_count = sum(1 for p in self.config.thai_polite_particles if p in message)
        informal_count = sum(1 for p in self.config.thai_informal_pronouns if p in message)
        
        if formal_count > informal_count:
            analysis.formality_level = 0.8
            analysis.detected_context = "formal_business"
            analysis.politeness_indicators = [p for p in self.config.thai_polite_particles if p in message]
        elif informal_count > formal_count:
            analysis.formality_level = 0.3
            analysis.detected_context = "casual_social"
        
        return analysis
    
    async def _analyze_emotional_intelligence(self, request: DeejaRequest) -> EmotionalAnalysis:
        """Analyze emotional context"""
        message = request.message.lower()
        
        analysis = EmotionalAnalysis(
            sentiment="neutral",
            emotional_intensity=0.5,
            detected_emotions=[],
            empathy_required=False,
            emotional_support_needed=False
        )
        
        # Emotion detection patterns
        emotion_patterns = {
            "sad": ["เศร้า", "เสียใจ", "หดหู่", "ท้อแท้", "sad", "depressed"],
            "happy": ["ดีใจ", "มีความสุข", "สนุก", "เฮง", "happy", "joyful"],
            "angry": ["โกรธ", "ฉุนเฉียว", "หงุดหงิด", "angry", "frustrated"],
            "anxious": ["กังวล", "เครียด", "กลัว", "worried", "anxious"],
            "grateful": ["ขอบคุณ", "ขอบใจ", "grateful", "thankful"]
        }
        
        for emotion, patterns in emotion_patterns.items():
            if any(pattern in message for pattern in patterns):
                analysis.detected_emotions.append(emotion)
                
                if emotion in ["sad", "anxious", "angry"]:
                    analysis.empathy_required = True
                    analysis.emotional_support_needed = True
                    analysis.emotional_intensity = 0.8
        
        # Determine overall sentiment
        if any(emotion in ["happy", "grateful"] for emotion in analysis.detected_emotions):
            analysis.sentiment = "positive"
        elif any(emotion in ["sad", "angry", "anxious"] for emotion in analysis.detected_emotions):
            analysis.sentiment = "negative"
        
        return analysis
    
    async def _calculate_empathy_score(
        self,
        request: DeejaRequest,
        cultural_analysis: CulturalAnalysis,
        emotional_analysis: EmotionalAnalysis
    ) -> float:
        """Calculate empathy score with Thai cultural calibration"""
        
        base_score = self.empathy_calibration["baseline_score"]
        
        # Emotional awareness component
        emotional_component = (
            emotional_analysis.emotional_intensity *
            self.config.emotional_awareness_weight
        )
        
        # Cultural sensitivity component
        cultural_component = (
            cultural_analysis.cultural_appropriateness *
            self.config.cultural_sensitivity_weight
        )
        
        # Thai cultural bonus
        thai_bonus = 0
        if cultural_analysis.language_detected == "thai":
            thai_bonus = self.empathy_calibration["thai_context_boost"]
        
        # Calculate final score
        empathy_score = min(1.0, base_score + emotional_component + cultural_component + thai_bonus)
        
        # Apply empathy multiplier if emotional support needed
        if emotional_analysis.empathy_required:
            empathy_score *= self.empathy_calibration["emotional_resonance_multiplier"]
            empathy_score = min(1.0, empathy_score)
        
        return round(empathy_score, 3)
    
    async def _apply_ethical_reasoning(self, request: DeejaRequest) -> Dict[str, Any]:
        """Apply ethical reasoning"""
        return {
            "compliant": True,
            "ethical_concerns": [],
            "recommendations": [],
            "cultural_ethics_score": 1.0
        }
    
    async def _generate_response(
        self,
        request: DeejaRequest,
        cultural_analysis: CulturalAnalysis,
        emotional_analysis: EmotionalAnalysis,
        empathy_score: float
    ) -> str:
        """Generate culturally appropriate response"""
        
        if cultural_analysis.language_detected == "thai":
            return await self._generate_thai_response(emotional_analysis)
        else:
            return await self._generate_english_response(emotional_analysis)
    
    async def _generate_thai_response(self, emotional_analysis: EmotionalAnalysis) -> str:
        """Generate Thai culturally appropriate response"""
        if emotional_analysis.sentiment == "negative":
            return "เข้าใจความรู้สึกของคุณค่ะ ขอให้กำลังใจนะคะ 💙"
        elif emotional_analysis.sentiment == "positive":
            return "ดีใจด้วยนะคะ! ขอให้มีความสุขเสมอ 😊"
        else:
            return "สวัสดีค่ะ มีอะไรให้ช่วยเหลือไหมคะ 🙏"
    
    async def _generate_english_response(self, emotional_analysis: EmotionalAnalysis) -> str:
        """Generate English response with cultural awareness"""
        if emotional_analysis.sentiment == "negative":
            return "I understand how you're feeling. Please know that I'm here to support you. 💙"
        elif emotional_analysis.sentiment == "positive":
            return "I'm so happy to hear that! Wishing you continued joy and happiness. 😊"
        else:
            return "Hello! How can I assist you today with empathy and cultural understanding?"
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            "module_id": self.module_id,
            "active": self.active,
            "cultural_contexts": list(self.cultural_contexts.keys()),
            "empathy_calibration": self.empathy_calibration,
            "ethical_framework": self.ethical_framework,
            "config": self.config.model_dump()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the module"""
        self.logger.info("Shutting down Deeja module")
        self.active = False
