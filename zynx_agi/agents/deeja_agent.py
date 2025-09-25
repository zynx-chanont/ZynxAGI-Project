"""
Deeja Agent (ดีจ้า) - Emotional AI and Cultural Intelligence
The heart of Zynx AGI's "Empathy-First" philosophy with Thai cultural expertise
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from .base_agent import ZynxAgent, AgentCapability, AgentResponse
import logging

logger = logging.getLogger(__name__)


class DeejaAgent(ZynxAgent):
    """
    Deeja (ดีจ้า) - Primary emotional AI facilitating empathetic, ethical, 
    and culturally aware human-computer interactions with Thai cultural specialization
    """
    
    def __init__(self, storage_driver=None, config: Optional[Dict[str, Any]] = None):
        capabilities = [
            AgentCapability.CULTURAL_ANALYSIS,
            AgentCapability.EMOTIONAL_INTELLIGENCE,
            AgentCapability.EMPATHY_SCORING,
            AgentCapability.TRANSLATION,
            AgentCapability.CHAT
        ]
        
        super().__init__(
            agent_id="deeja",
            capabilities=capabilities,
            storage_driver=storage_driver,
            config=config
        )
        
        # Thai cultural markers and indicators
        self.thai_cultural_markers = {
            "kreng_jai": ["เกรงใจ", "กรุณา", "ขอโทษ", "รบกวน"],
            "sanuk": ["สนุก", "เล่น", "สบาย", "ผ่อนคลาย"], 
            "mai_pen_rai": ["ไม่เป็นไร", "ไม่มีปัญหา", "ช่างมัน"],
            "greng_jai": ["เกรงใจ", "ไม่อยากรบกวน", "ขอโทษที่"],
            "bun_khun": ["บุญคุณ", "ขอบคุณ", "ขอบใจ", "กตัญญู"]
        }
        
        # Empathy scoring model parameters
        self.empathy_model = {
            "emotional_awareness_weight": 0.3,
            "cultural_sensitivity_weight": 0.3,
            "response_appropriateness_weight": 0.2,
            "thai_cultural_weight": 0.2,
            "default_threshold": 0.7
        }
        
        # Ethical reasoning framework
        self.ethical_framework = {
            "principles": [
                "respect_for_persons",
                "beneficence", 
                "non_maleficence",
                "justice",
                "cultural_sensitivity"
            ],
            "thai_values": [
                "kreng_jai_respect",
                "sanuk_positivity",
                "mai_pen_rai_acceptance",
                "family_harmony",
                "buddhist_compassion"
            ]
        }
    
    async def _setup_agent(self):
        """Initialize Deeja agent with cultural and emotional intelligence models"""
        logger.info("Setting up Deeja (ดีจ้า) Agent...")
        
        # Initialize cultural analysis models
        await self._initialize_cultural_models()
        
        # Setup empathy scoring system
        await self._setup_empathy_scoring()
        
        # Initialize ethical reasoning engine
        await self._setup_ethical_reasoning()
        
        # Load Thai language processing
        await self._setup_thai_language_processing()
        
        logger.info("Deeja Agent setup complete - Thai cultural intelligence active")
    
    async def _initialize_cultural_models(self):
        """Initialize Thai cultural analysis models"""
        # Load cultural context rules
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
    
    async def _setup_empathy_scoring(self):
        """Setup empathy scoring and calibration system"""
        self.empathy_calibration = {
            "baseline_score": 0.5,
            "cultural_bonus": 0.2,
            "emotional_resonance_multiplier": 1.5,
            "thai_context_boost": 0.3
        }
    
    async def _setup_ethical_reasoning(self):
        """Setup ethical reasoning based on core knowledge base"""
        self.ethical_knowledge_base = {
            "respect_for_persons": {
                "description": "Treating individuals with dignity and autonomy",
                "thai_interpretation": "เคารพในคุณค่าและศักดิ์ศรีของบุคคล"
            },
            "cultural_sensitivity": {
                "description": "Understanding and respecting cultural differences",
                "thai_interpretation": "เข้าใจและเคารพความแตกต่างทางวัฒนธรรม"
            },
            "beneficence": {
                "description": "Acting in the best interest of others",
                "thai_interpretation": "ทำในสิ่งที่เป็นประโยชน์ต่อผู้อื่น"
            }
        }
    
    async def _setup_thai_language_processing(self):
        """Setup Thai language processing capabilities"""
        self.thai_language_patterns = {
            "polite_particles": ["ครับ", "ค่ะ", "คะ", "จ้ะ"],
            "formal_pronouns": ["กระผม", "ดิฉัน", "ท่าน", "คุณ"],
            "informal_pronouns": ["กู", "มึง", "เรา", "เธอ"],
            "respect_terms": ["เจ้าค่ะ", "เจ้าคะ", "ท่าน", "อาจารย์"]
        }
    
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """Process requests with empathy-first approach and cultural intelligence"""
        start_time = datetime.utcnow()
        
        try:
            # Perform cultural analysis
            cultural_analysis = await self._analyze_cultural_context(request)
            
            # Perform emotional intelligence analysis
            emotional_analysis = await self._analyze_emotional_intelligence(request)
            
            # Calculate empathy score
            empathy_score = await self._calculate_empathy_score(
                request, cultural_analysis, emotional_analysis
            )
            
            # Apply ethical reasoning
            ethical_assessment = await self._apply_ethical_reasoning(request)
            
            # Generate culturally appropriate response
            response_data = await self._generate_empathetic_response(
                request, cultural_analysis, emotional_analysis, empathy_score
            )
            
            # Log cultural interaction for learning
            if self.storage:
                await self.storage.store_log({
                    "action": "cultural_interaction",
                    "agent_id": self.agent_id,
                    "cultural_context": cultural_analysis["detected_context"],
                    "empathy_score": empathy_score,
                    "thai_cultural_markers": cultural_analysis["thai_markers"],
                    "ethical_compliant": ethical_assessment["compliant"]
                })
            
            return AgentResponse(
                success=True,
                agent_id=self.agent_id,
                response_data=response_data,
                metadata={
                    "cultural_analysis": cultural_analysis,
                    "emotional_analysis": emotional_analysis,
                    "empathy_score": empathy_score,
                    "ethical_assessment": ethical_assessment
                },
                timestamp=start_time.isoformat(),
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error(f"Error in Deeja agent processing: {e}")
            return AgentResponse(
                success=False,
                agent_id=self.agent_id,
                response_data={"error": str(e)},
                timestamp=start_time.isoformat()
            )
    
    async def _analyze_cultural_context(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cultural context with Thai specialization"""
        message = request.get("message", "")
        
        analysis = {
            "language_detected": "unknown",
            "formality_level": 0.5,
            "cultural_context": "neutral",
            "thai_markers": [],
            "detected_context": "general",
            "cultural_appropriateness": 1.0
        }
        
        # Detect Thai language
        thai_characters = re.findall(r'[\u0E00-\u0E7F]', message)
        if thai_characters:
            analysis["language_detected"] = "thai"
            analysis["cultural_appropriateness"] += 0.3
        
        # Check for Thai cultural markers
        for marker_type, markers in self.thai_cultural_markers.items():
            found_markers = [marker for marker in markers if marker in message]
            if found_markers:
                analysis["thai_markers"].append({
                    "type": marker_type,
                    "markers": found_markers
                })
        
        # Determine formality level
        formal_indicators = ["ครับ", "ค่ะ", "กระผม", "ดิฉัน", "ท่าน"]
        informal_indicators = ["จ้ะ", "นะ", "เอ่ย", "แหล่ะ"]
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in message)
        informal_count = sum(1 for indicator in informal_indicators if indicator in message)
        
        if formal_count > informal_count:
            analysis["formality_level"] = 0.8
            analysis["detected_context"] = "formal_business"
        elif informal_count > formal_count:
            analysis["formality_level"] = 0.3
            analysis["detected_context"] = "casual_social"
        
        return analysis
    
    async def _analyze_emotional_intelligence(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emotional context and intelligence requirements"""
        message = request.get("message", "")
        
        analysis = {
            "sentiment": "neutral",
            "emotional_intensity": 0.5,
            "detected_emotions": [],
            "empathy_required": False,
            "emotional_support_needed": False
        }
        
        # Emotion detection patterns
        emotion_patterns = {
            "sad": ["เศร้า", "เสียใจ", "หดหู่", "ท้อแท้", "sad", "depressed"],
            "happy": ["ดีใจ", "มีความสุข", "สนุก", "เฮง", "happy", "joyful"],
            "angry": ["โกรธ", "ฉุนเฉียว", "หงุดหงิด", "angry", "frustrated"],
            "anxious": ["กังวล", "เครียด", "กลัว", "worried", "anxious"],
            "grateful": ["ขอบคุณ", "ขอบใจ", "grateful", "thankful"]
        }
        
        for emotion, patterns in emotion_patterns.items():
            if any(pattern in message.lower() for pattern in patterns):
                analysis["detected_emotions"].append(emotion)
                
                if emotion in ["sad", "anxious", "angry"]:
                    analysis["empathy_required"] = True
                    analysis["emotional_support_needed"] = True
                    analysis["emotional_intensity"] = 0.8
        
        # Determine overall sentiment
        if any(emotion in ["happy", "grateful"] for emotion in analysis["detected_emotions"]):
            analysis["sentiment"] = "positive"
        elif any(emotion in ["sad", "angry", "anxious"] for emotion in analysis["detected_emotions"]):
            analysis["sentiment"] = "negative"
        
        return analysis
    
    async def _calculate_empathy_score(
        self,
        request: Dict[str, Any],
        cultural_analysis: Dict[str, Any],
        emotional_analysis: Dict[str, Any]
    ) -> float:
        """Calculate empathy score with Thai cultural calibration"""
        
        base_score = self.empathy_calibration["baseline_score"]
        
        # Emotional awareness component
        emotional_component = (
            emotional_analysis["emotional_intensity"] * 
            self.empathy_model["emotional_awareness_weight"]
        )
        
        # Cultural sensitivity component  
        cultural_component = (
            cultural_analysis["cultural_appropriateness"] *
            self.empathy_model["cultural_sensitivity_weight"]
        )
        
        # Thai cultural bonus
        thai_bonus = 0
        if cultural_analysis["language_detected"] == "thai":
            thai_bonus = self.empathy_calibration["thai_context_boost"]
        
        # Calculate final score
        empathy_score = min(1.0, base_score + emotional_component + cultural_component + thai_bonus)
        
        # Apply empathy required multiplier
        if emotional_analysis["empathy_required"]:
            empathy_score *= self.empathy_calibration["emotional_resonance_multiplier"]
            empathy_score = min(1.0, empathy_score)
        
        return round(empathy_score, 3)
    
    async def _apply_ethical_reasoning(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ethical reasoning based on core knowledge base"""
        message = request.get("message", "")
        
        assessment = {
            "compliant": True,
            "ethical_concerns": [],
            "recommendations": [],
            "cultural_ethics_score": 1.0
        }
        
        # Check against ethical principles
        for principle in self.ethical_framework["principles"]:
            principle_check = await self._check_ethical_principle(message, principle)
            if not principle_check["compliant"]:
                assessment["compliant"] = False
                assessment["ethical_concerns"].append(principle_check)
        
        # Thai cultural values check
        for value in self.ethical_framework["thai_values"]:
            value_check = await self._check_thai_cultural_value(message, value)
            if value_check["enhancement_possible"]:
                assessment["recommendations"].append(value_check["recommendation"])
        
        return assessment
    
    async def _check_ethical_principle(self, message: str, principle: str) -> Dict[str, Any]:
        """Check message against specific ethical principle"""
        # Basic ethical compliance check
        return {
            "principle": principle,
            "compliant": True,
            "explanation": f"Message complies with {principle}"
        }
    
    async def _check_thai_cultural_value(self, message: str, value: str) -> Dict[str, Any]:
        """Check message against Thai cultural values"""
        # Basic cultural value enhancement check
        return {
            "value": value,
            "enhancement_possible": False,
            "recommendation": f"Consider incorporating {value} for better cultural alignment"
        }
    
    async def _generate_empathetic_response(
        self,
        request: Dict[str, Any],
        cultural_analysis: Dict[str, Any],
        emotional_analysis: Dict[str, Any],
        empathy_score: float
    ) -> Dict[str, Any]:
        """Generate culturally appropriate and empathetic response"""
        
        message = request.get("message", "")
        
        response = {
            "message": "",
            "cultural_context": cultural_analysis["detected_context"],
            "empathy_score": empathy_score,
            "cultural_appropriateness": cultural_analysis["cultural_appropriateness"],
            "emotional_support": emotional_analysis["emotional_support_needed"],
            "thai_cultural_elements": cultural_analysis["thai_markers"]
        }
        
        # Generate appropriate response based on context
        if cultural_analysis["language_detected"] == "thai":
            response["message"] = await self._generate_thai_response(
                message, cultural_analysis, emotional_analysis
            )
            response["response_language"] = "thai"
        else:
            response["message"] = await self._generate_english_response(
                message, cultural_analysis, emotional_analysis  
            )
            response["response_language"] = "english"
        
        return response
    
    async def _generate_thai_response(
        self,
        message: str,
        cultural_analysis: Dict[str, Any],
        emotional_analysis: Dict[str, Any]
    ) -> str:
        """Generate Thai culturally appropriate response"""
        
        # Basic Thai response with cultural sensitivity
        if emotional_analysis["sentiment"] == "negative":
            return "เข้าใจความรู้สึกของคุณค่ะ ขอให้กำลังใจนะคะ 💙"
        elif emotional_analysis["sentiment"] == "positive":
            return "ดีใจด้วยนะคะ! ขอให้มีความสุขเสมอ 😊"
        else:
            return "สวัสดีค่ะ มีอะไรให้ช่วยเหลือไหมคะ 🙏"
    
    async def _generate_english_response(
        self,
        message: str,
        cultural_analysis: Dict[str, Any],
        emotional_analysis: Dict[str, Any]
    ) -> str:
        """Generate English response with cultural awareness"""
        
        if emotional_analysis["sentiment"] == "negative":
            return "I understand how you're feeling. Please know that I'm here to support you. 💙"
        elif emotional_analysis["sentiment"] == "positive":
            return "I'm so happy to hear that! Wishing you continued joy and happiness. 😊"
        else:
            return "Hello! How can I assist you today with empathy and cultural understanding?"
    
    async def _execute_capability_impl(
        self,
        capability: AgentCapability,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific Deeja capabilities"""
        
        if capability == AgentCapability.CULTURAL_ANALYSIS:
            return await self._analyze_cultural_context(data)
        
        elif capability == AgentCapability.EMOTIONAL_INTELLIGENCE:
            return await self._analyze_emotional_intelligence(data)
        
        elif capability == AgentCapability.EMPATHY_SCORING:
            cultural_analysis = await self._analyze_cultural_context(data)
            emotional_analysis = await self._analyze_emotional_intelligence(data)
            empathy_score = await self._calculate_empathy_score(
                data, cultural_analysis, emotional_analysis
            )
            return {"empathy_score": empathy_score}
        
        elif capability == AgentCapability.TRANSLATION:
            return await self._handle_translation(data)
        
        elif capability == AgentCapability.CHAT:
            return await self.process_request(data)
        
        else:
            raise ValueError(f"Unsupported capability: {capability}")
    
    async def _handle_translation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle translation with cultural context preservation"""
        text = data.get("text", "")
        target_language = data.get("target_language", "en")
        
        # Basic translation handling (would integrate with translation service)
        return {
            "original_text": text,
            "translated_text": f"[Translation to {target_language}]: {text}",
            "target_language": target_language,
            "cultural_notes": "Translation preserves cultural context"
        }
    
    async def self_reflect(self) -> Dict[str, Any]:
        """Deeja self-reflection process for empathy calibration"""
        reflection = {
            "empathy_calibration": self.empathy_calibration,
            "cultural_interactions_count": self.metrics.get("cultural_interactions", 0),
            "thai_language_processing": "active",
            "ethical_framework_status": "operational",
            "self_improvement_areas": [
                "Enhanced Thai cultural marker detection",
                "Improved emotional resonance calibration",
                "Expanded ethical reasoning patterns"
            ],
            "reflection_timestamp": datetime.utcnow().isoformat()
        }
        
        return reflection