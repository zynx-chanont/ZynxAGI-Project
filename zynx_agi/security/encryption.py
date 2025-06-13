from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import jwt
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio
from zynx_agi.agents import ZynxAgent, AgentCapability, AgentResponse
from zynx_agi.clients import ThaiCulturalMCPClient
from zynx_agi.memory import MemoryHierarchy, MemoryType
from zynx_agi.conflict_resolution import ConflictResolver, ConflictResolution
from zynx_agi.meta_cognition import MetaCognition
from zynx_agi.unified_reasoning import UnifiedReasoningEngine
import logging
import pytest
import json

load_dotenv()

# Encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Security(oauth2_scheme)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(username=username)
        return token_data
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def encrypt_data(data: str) -> bytes:
    """Encrypt data using Fernet"""
    return fernet.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt data using Fernet"""
    return fernet.decrypt(encrypted_data).decode()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

class ThaiCulturalMCPAgent(ZynxAgent):
    """Agent สำหรับจัดการกับ Thai Cultural MCP Server"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.COMMUNICATION
            ]
        )
        self.mcp_client = ThaiCulturalMCPClient()
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        # วิเคราะห์ cultural context
        cultural_analysis = await self.mcp_client.analyze_cultural_context(
            text=input_data.get("text", "")
        )
        
        # ปรับข้อความตาม cultural context
        adjusted_text = await self.mcp_client.adjust_text(
            text=input_data.get("text", ""),
            cultural_context=cultural_analysis
        )
        
        return AgentResponse(
            agent_id=self.agent_id,
            result={
                "original_text": input_data.get("text", ""),
                "adjusted_text": adjusted_text,
                "cultural_analysis": cultural_analysis
            },
            confidence=0.9,
            reasoning_path=["cultural_analysis", "text_adjustment"],
            resource_usage={"api_calls": 2},
            timestamp=asyncio.get_event_loop().time()
        ) 

class ThaiCulturalMemory(MemoryHierarchy):
    """Memory system สำหรับเก็บข้อมูลวัฒนธรรมไทย"""
    
    async def store_cultural_pattern(self, pattern: Dict[str, Any]):
        """เก็บรูปแบบการสื่อสารทางวัฒนธรรม"""
        await self.store(
            memory_type=MemoryType.SEMANTIC,
            data={"cultural_patterns": pattern}
        )
    
    async def retrieve_cultural_context(self, query: str) -> List[Dict[str, Any]]:
        """ค้นหาบริบททางวัฒนธรรมที่เกี่ยวข้อง"""
        return await self.retrieve(
            memory_type=MemoryType.SEMANTIC,
            query=query
        ) 

class ThaiCulturalConflictResolver(ConflictResolver):
    """Conflict resolver สำหรับความขัดแย้งทางวัฒนธรรม"""
    
    async def _cultural_consensus_building(
        self, 
        responses: List[AgentResponse], 
        context: Dict[str, Any]
    ) -> ConflictResolution:
        """สร้างฉันทามติโดยคำนึงถึงบริบททางวัฒนธรรม"""
        # วิเคราะห์ความเหมาะสมทางวัฒนธรรมของแต่ละ response
        cultural_scores = [
            self._evaluate_cultural_appropriateness(r, context)
            for r in responses
        ]
        
        # เลือก response ที่เหมาะสมที่สุดทางวัฒนธรรม
        best_response = responses[cultural_scores.index(max(cultural_scores))]
        
        return ConflictResolution(
            winning_response=best_response,
            resolution_method="cultural_consensus",
            consensus_score=max(cultural_scores),
            dissenting_agents=[
                r.agent_id for i, r in enumerate(responses)
                if cultural_scores[i] < max(cultural_scores)
            ]
        ) 

class ThaiCulturalMetaCognition(MetaCognition):
    """MetaCognition system สำหรับการเรียนรู้วัฒนธรรมไทย"""
    
    async def evaluate_cultural_understanding(
        self,
        response: Dict[str, Any],
        cultural_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """ประเมินความเข้าใจทางวัฒนธรรม"""
        metrics = {
            "cultural_accuracy": self._calculate_cultural_accuracy(
                response, cultural_context
            ),
            "cultural_sensitivity": self._calculate_cultural_sensitivity(
                response, cultural_context
            ),
            "adaptation_rate": self._calculate_adaptation_rate()
        }
        
        self.performance_history.append(metrics)
        return metrics 

class ThaiCulturalReasoningEngine(UnifiedReasoningEngine):
    """Reasoning engine สำหรับจัดการกับวัฒนธรรมไทย"""
    
    def __init__(self):
        super().__init__()
        self.cultural_memory = ThaiCulturalMemory()
        self.cultural_meta_cognition = ThaiCulturalMetaCognition()
        
        # ลงทะเบียน agents
        self.register_agent(ThaiCulturalMCPAgent("thai_cultural_agent"))
        self.register_agent(ThaiCulturalAnalysisAgent("thai_analysis_agent"))
    
    async def process_cultural_request(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ประมวลผลคำขอที่เกี่ยวข้องกับวัฒนธรรม"""
        request = {
            "text": text,
            "context": context,
            "type": "cultural_analysis"
        }
        
        return await self.process_request(request) 

class ThaiCulturalErrorHandler:
    """จัดการข้อผิดพลาดที่เกี่ยวข้องกับวัฒนธรรม"""
    
    @staticmethod
    async def handle_cultural_error(
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """จัดการข้อผิดพลาดและให้คำแนะนำ"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # บันทึก error
        logging.error(f"Cultural error: {error_type} - {error_message}")
        
        # ส่งคืนข้อความที่เหมาะสม
        return {
            "error": error_type,
            "message": "ขออภัย เกิดข้อผิดพลาดในการวิเคราะห์วัฒนธรรม",
            "suggestion": "กรุณาลองใหม่อีกครั้ง",
            "context": context
        } 

class ThaiCulturalConfig:
    """จัดการการตั้งค่าสำหรับระบบวัฒนธรรมไทย"""
    
    def __init__(self):
        self.config = {
            "cultural_sensitivity_threshold": 0.8,
            "max_retry_attempts": 3,
            "cache_ttl": 3600,
            "supported_cultural_patterns": [
                "formal",
                "informal",
                "business",
                "social"
            ]
        }
    
    def get_config(self, key: str) -> Any:
        """ดึงค่าการตั้งค่า"""
        return self.config.get(key) 

class TestThaiCulturalIntegration:
    """ทดสอบการทำงานร่วมกันของระบบวัฒนธรรมไทย"""
    
    @pytest.mark.asyncio
    async def test_cultural_analysis_flow(self):
        """ทดสอบการวิเคราะห์วัฒนธรรม"""
        engine = ThaiCulturalReasoningEngine()
        
        result = await engine.process_cultural_request(
            text="สวัสดีครับ ผมชื่อสมชาย",
            context={"formality": "formal"}
        )
        
        assert "cultural_analysis" in result
        assert "adjusted_text" in result
        assert result["confidence"] > 0.8 

class ZynxAGIDemo:
    """Demo system for Zynx AGI"""
    
    def __init__(self):
        self.reasoning_engine = ThaiCulturalReasoningEngine()
        self.demo_scenarios = {
            "basic_chat": {
                "title": "Basic Cultural Chat",
                "description": "ทดสอบการสนทนาพื้นฐานกับระบบ",
                "examples": [
                    "สวัสดีครับ ผมชื่อสมชาย",
                    "ขอแนะนำตัวหน่อยครับ",
                    "ช่วยอธิบายวัฒนธรรมไทยให้หน่อย"
                ]
            },
            "business_communication": {
                "title": "Business Communication",
                "description": "ทดสอบการสื่อสารในบริบทธุรกิจ",
                "examples": [
                    "ขอเสนอโครงการใหม่ครับ",
                    "ขอประชุมกับทีมงาน",
                    "ขอรายงานความคืบหน้า"
                ]
            },
            "cultural_analysis": {
                "title": "Cultural Analysis",
                "description": "ทดสอบการวิเคราะห์วัฒนธรรม",
                "examples": [
                    "วิเคราะห์ความเหมาะสมของข้อความนี้",
                    "ปรับข้อความให้สุภาพขึ้น",
                    "ตรวจสอบความถูกต้องทางวัฒนธรรม"
                ]
            }
        }
    
    async def run_demo(self, scenario: str, input_text: str) -> Dict[str, Any]:
        """Run a demo scenario"""
        try:
            # 1. Process the input
            result = await self.reasoning_engine.process_cultural_request(
                text=input_text,
                context={"scenario": scenario}
            )
            
            # 2. Format the response
            demo_response = {
                "input": input_text,
                "scenario": self.demo_scenarios[scenario]["title"],
                "cultural_analysis": result.get("cultural_analysis", {}),
                "adjusted_text": result.get("adjusted_text", ""),
                "confidence": result.get("confidence", 0.0),
                "reasoning": result.get("reasoning", []),
                "performance_metrics": result.get("performance_metrics", {})
            }
            
            return demo_response
            
        except Exception as e:
            return {
                "error": str(e),
                "input": input_text,
                "scenario": scenario
            }
    
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of available demo scenarios"""
        return [
            {
                "id": scenario_id,
                "title": data["title"],
                "description": data["description"],
                "examples": data["examples"]
            }
            for scenario_id, data in self.demo_scenarios.items()
        ]

# Example usage
async def main():
    demo = ZynxAGIDemo()
    
    # Run a basic chat scenario
    result = await demo.run_demo(
        scenario="basic_chat",
        input_text="สวัสดีครับ ผมชื่อสมชาย"
    )
    
    print("Demo Result:", json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main()) 

class CulturalContextManager:
    """จัดการบริบททางวัฒนธรรม"""
    
    def __init__(self):
        self.context_patterns = {
            "formal": {
                "particles": ["ครับ", "ค่ะ", "ขอ", "กรุณา"],
                "tone": "polite",
                "structure": "hierarchical"
            },
            "informal": {
                "particles": ["นะ", "สิ", "ดิ", "จ้ะ"],
                "tone": "casual",
                "structure": "equal"
            },
            "business": {
                "particles": ["ขอ", "กรุณา", "โปรด"],
                "tone": "professional",
                "structure": "formal"
            }
        }
    
    async def analyze_context(self, text: str) -> Dict[str, Any]:
        """วิเคราะห์บริบททางวัฒนธรรมจากข้อความ"""
        context = {
            "formality_level": self._detect_formality(text),
            "tone": self._detect_tone(text),
            "structure": self._detect_structure(text),
            "cultural_elements": self._extract_cultural_elements(text)
        }
        return context
    
    def _detect_formality(self, text: str) -> str:
        """ตรวจจับระดับความเป็นทางการ"""
        # Implementation
        return "formal"
    
    def _detect_tone(self, text: str) -> str:
        """ตรวจจับน้ำเสียง"""
        # Implementation
        return "polite"
    
    def _detect_structure(self, text: str) -> str:
        """ตรวจจับโครงสร้างประโยค"""
        # Implementation
        return "hierarchical"
    
    def _extract_cultural_elements(self, text: str) -> List[str]:
        """สกัดองค์ประกอบทางวัฒนธรรม"""
        # Implementation
        return ["respect", "hierarchy"] 

class CulturalResponseGenerator:
    """สร้างการตอบสนองที่เหมาะสมทางวัฒนธรรม"""
    
    def __init__(self, context_manager: CulturalContextManager):
        self.context_manager = context_manager
        self.response_templates = {
            "formal": {
                "greeting": "สวัสดี{particle}",
                "introduction": "ขอแนะนำตัว{particle}",
                "request": "ขอ{action}{particle}"
            },
            "informal": {
                "greeting": "สวัสดี{particle}",
                "introduction": "แนะนำตัว{particle}",
                "request": "{action}{particle}"
            }
        }
    
    async def generate_response(
        self,
        input_text: str,
        context: Dict[str, Any]
    ) -> str:
        """สร้างการตอบสนองที่เหมาะสม"""
        formality = context.get("formality_level", "formal")
        template = self.response_templates[formality]
        
        # Generate appropriate response
        response = self._apply_template(template, input_text, context)
        return response
    
    def _apply_template(
        self,
        template: Dict[str, str],
        input_text: str,
        context: Dict[str, Any]
    ) -> str:
        """ประยุกต์ใช้ template"""
        # Implementation
        return "สวัสดีครับ" 

class CulturalLearningSystem:
    """ระบบการเรียนรู้วัฒนธรรม"""
    
    def __init__(self):
        self.learning_data = {
            "patterns": {},
            "exceptions": {},
            "feedback": []
        }
    
    async def learn_from_interaction(
        self,
        input_text: str,
        response: str,
        feedback: Dict[str, Any]
    ):
        """เรียนรู้จากการโต้ตอบ"""
        # Update patterns
        self._update_patterns(input_text, response)
        
        # Update exceptions
        if feedback.get("is_exception"):
            self._update_exceptions(input_text, response)
        
        # Store feedback
        self.learning_data["feedback"].append({
            "input": input_text,
            "response": response,
            "feedback": feedback,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def _update_patterns(self, input_text: str, response: str):
        """อัปเดตรูปแบบการสื่อสาร"""
        # Implementation
        pass
    
    def _update_exceptions(self, input_text: str, response: str):
        """อัปเดตข้อยกเว้น"""
        # Implementation
        pass 

class CulturalValidationSystem:
    """ระบบตรวจสอบความเหมาะสมทางวัฒนธรรม"""
    
    def __init__(self):
        self.validation_rules = {
            "formality": self._validate_formality,
            "politeness": self._validate_politeness,
            "context": self._validate_context
        }
    
    async def validate_response(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ตรวจสอบความเหมาะสมของการตอบสนอง"""
        validation_results = {}
        
        for rule_name, rule_func in self.validation_rules.items():
            validation_results[rule_name] = await rule_func(response, context)
        
        return validation_results
    
    async def _validate_formality(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> bool:
        """ตรวจสอบความเหมาะสมของระดับความเป็นทางการ"""
        # Implementation
        return True
    
    async def _validate_politeness(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> bool:
        """ตรวจสอบความสุภาพ"""
        # Implementation
        return True
    
    async def _validate_context(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> bool:
        """ตรวจสอบความเหมาะสมของบริบท"""
        # Implementation
        return True 

class CulturalFeedbackSystem:
    """ระบบรับ feedback ทางวัฒนธรรม"""
    
    def __init__(self):
        self.feedback_history = []
    
    async def collect_feedback(
        self,
        interaction: Dict[str, Any],
        user_feedback: Dict[str, Any]
    ):
        """เก็บ feedback จากผู้ใช้"""
        feedback_entry = {
            "interaction": interaction,
            "user_feedback": user_feedback,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.feedback_history.append(feedback_entry)
        
        # Analyze feedback
        analysis = await self._analyze_feedback(feedback_entry)
        
        return analysis
    
    async def _analyze_feedback(
        self,
        feedback_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """วิเคราะห์ feedback"""
        # Implementation
        return {
            "sentiment": "positive",
            "improvement_areas": [],
            "suggestions": []
        } 