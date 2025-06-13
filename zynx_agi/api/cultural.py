from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
from ..config.settings import settings
from ..cultural.thai_cultural_engine import ThaiCulturalEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cultural", tags=["cultural"])
cultural_engine = ThaiCulturalEngine()

# Request/Response Models
class CulturalAnalysisRequest(BaseModel):
    """Request model for cultural analysis"""
    text: str = Field(..., min_length=1, max_length=4000)
    language: str = Field("th", description="Language code (th, en)")
    context_type: Optional[str] = Field("formal", description="Context type (formal, informal)")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace')
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ["th", "en"]:
            raise ValueError('Language must be either "th" or "en"')
        return v
    
    @validator('context_type')
    def validate_context_type(cls, v):
        if v not in ["formal", "informal"]:
            raise ValueError('Context type must be either "formal" or "informal"')
        return v

class PolitenessAnalysis(BaseModel):
    """Politeness analysis results"""
    level: float = Field(..., ge=0.0, le=1.0)
    detected_particles: List[str]
    suggestions: List[str]
    score_breakdown: Dict[str, float]

class FormalityAnalysis(BaseModel):
    """Formality analysis results"""
    level: float = Field(..., ge=0.0, le=1.0)
    formal_elements: List[str]
    informal_elements: List[str]
    suggestions: List[str]
    score_breakdown: Dict[str, float]

class CulturalPattern(BaseModel):
    """Cultural pattern detection results"""
    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    examples: List[str]
    description: str

class CulturalAdaptation(BaseModel):
    """Cultural adaptation suggestions"""
    original_text: str
    adapted_text: str
    changes_made: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)

class CulturalAnalysisResponse(BaseModel):
    """Response model for cultural analysis"""
    text: str
    language: str
    context_type: str
    politeness: PolitenessAnalysis
    formality: FormalityAnalysis
    cultural_patterns: List[CulturalPattern]
    adaptations: List[CulturalAdaptation]
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)

# Helper Functions
def analyze_politeness(text: str, language: str) -> PolitenessAnalysis:
    """Analyze politeness level and patterns"""
    # This would be implemented using the ThaiCulturalEngine
    # For now, returning mock data
    return PolitenessAnalysis(
        level=0.8,
        detected_particles=["ครับ", "ค่ะ"],
        suggestions=["Consider adding more polite particles"],
        score_breakdown={
            "particles": 0.8,
            "tone": 0.7,
            "structure": 0.9
        }
    )

def analyze_formality(text: str, language: str) -> FormalityAnalysis:
    """Analyze formality level and patterns"""
    # This would be implemented using the ThaiCulturalEngine
    # For now, returning mock data
    return FormalityAnalysis(
        level=0.7,
        formal_elements=["กราบเรียน", "ขอประทาน"],
        informal_elements=["บอก", "พูด"],
        suggestions=["Consider using more formal pronouns"],
        score_breakdown={
            "pronouns": 0.7,
            "verbs": 0.8,
            "structure": 0.6
        }
    )

def detect_cultural_patterns(text: str, language: str) -> List[CulturalPattern]:
    """Detect cultural patterns in text"""
    # This would be implemented using the ThaiCulturalEngine
    # For now, returning mock data
    return [
        CulturalPattern(
            name="kreng_jai",
            confidence=0.9,
            examples=["ไม่เป็นไร", "ไม่ต้องกังวล"],
            description="Showing consideration and avoiding imposition"
        ),
        CulturalPattern(
            name="jai_yen",
            confidence=0.8,
            examples=["ใจเย็น", "ใจเย็นๆ"],
            description="Maintaining calm and composure"
        )
    ]

def suggest_adaptations(
    text: str,
    language: str,
    context_type: str
) -> List[CulturalAdaptation]:
    """Suggest cultural adaptations for the text"""
    # This would be implemented using the ThaiCulturalEngine
    # For now, returning mock data
    return [
        CulturalAdaptation(
            original_text=text,
            adapted_text=text + " ครับ/ค่ะ",
            changes_made=["Added polite particle"],
            confidence=0.9
        )
    ]

# Endpoints
@router.post("/analyze", response_model=CulturalAnalysisResponse)
async def analyze_cultural_context(request: CulturalAnalysisRequest):
    """Analyze cultural context of text"""
    start_time = datetime.now()
    
    try:
        # Process with cultural engine
        processed = await cultural_engine.process_message({
            "text": request.text,
            "context_type": request.context_type
        })
        
        # Analyze politeness
        politeness = analyze_politeness(processed["adjusted_text"], request.language)
        
        # Analyze formality
        formality = analyze_formality(processed["adjusted_text"], request.language)
        
        # Detect cultural patterns
        patterns = detect_cultural_patterns(processed["adjusted_text"], request.language)
        
        # Suggest adaptations
        adaptations = suggest_adaptations(
            processed["adjusted_text"],
            request.language,
            request.context_type
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return CulturalAnalysisResponse(
            text=request.text,
            language=request.language,
            context_type=request.context_type,
            politeness=politeness,
            formality=formality,
            cultural_patterns=patterns,
            adaptations=adaptations,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing cultural context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing cultural context: {str(e)}"
        )

@router.get("/patterns")
async def list_cultural_patterns():
    """List available cultural patterns"""
    try:
        # This would be implemented using the ThaiCulturalEngine
        # For now, returning mock data
        return {
            "patterns": [
                {
                    "name": "kreng_jai",
                    "description": "Showing consideration and avoiding imposition",
                    "examples": ["ไม่เป็นไร", "ไม่ต้องกังวล"],
                    "weight": 0.8
                },
                {
                    "name": "jai_yen",
                    "description": "Maintaining calm and composure",
                    "examples": ["ใจเย็น", "ใจเย็นๆ"],
                    "weight": 0.7
                },
                {
                    "name": "sanuk",
                    "description": "Making things fun and enjoyable",
                    "examples": ["สนุก", "เฮฮา"],
                    "weight": 0.6
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error listing cultural patterns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing cultural patterns: {str(e)}"
        )

@router.get("/languages")
async def list_supported_languages():
    """List supported languages for cultural analysis"""
    return {
        "languages": [
            {
                "code": "th",
                "name": "Thai",
                "supported_patterns": ["kreng_jai", "jai_yen", "sanuk"]
            },
            {
                "code": "en",
                "name": "English",
                "supported_patterns": ["politeness", "formality"]
            }
        ]
    } 