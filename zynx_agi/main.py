from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from .config.settings import settings
from .modules import ZynxCore, DeejaAgent, ZynxMetadata
from .storage import ZynxStorage
from .local_llm import LocalLLMFallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZynxAGI",
    description="Universal AI Orchestration Platform with Cultural-Emotional Intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize ZPDL v1.0 compliant modules
zynx_core = ZynxCore()
deeja_agent = DeejaAgent()
zynx_metadata = ZynxMetadata()
zynx_storage = ZynxStorage()
local_llm_fallback = LocalLLMFallback()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SERVE REACT APP ---
# Mount the React frontend static files
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static") # Temporarily commented out for testing

@app.get("/")
async def root():
    """Root endpoint"""
    try:
        return {
            "message": "Welcome to ZynxAGI - Universal AI Orchestration Platform",
            "version": "1.0.0",
            "cultural_intelligence": "Thai-English Bridge Active",
            "status": "operational",
            "docs": "/docs",
            "emoji": "🚀"
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint with ZPDL v1.0 attribution"""
    try:
        # Initialize modules if needed
        await zynx_core.initialize()
        
        return {
            "status": "healthy",
            "app": "ZynxAGI",
            "version": "1.0.0",
            "attribution": zynx_core.get_attribution(),
            "components": {
                "api": "healthy",
                "cultural_intelligence": "ready",
                "universal_dispatcher": "ready",
                "zynx_core": zynx_core.get_status(),
                "deeja_agent": deeja_agent.get_status(),
                "metadata_system": zynx_metadata.get_status(),
                "storage_system": zynx_storage.get_storage_stats(),
                "local_llm_fallback": local_llm_fallback.get_status()
            },
            "message": "ZynxAGI is running successfully! 🌟",
            "thai_message": "ระบบ ZynxAGI ทำงานปกติค่ะ! 🇹🇭",
            "zpdl_compliance": "v1.0"
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Chat endpoint with Deeja integration
@app.post("/api/v1/chat/message")
async def chat_message(request: dict):
    """Chat endpoint with Deeja agent integration and fallback support"""
    try:
        message = request.get("message", "")
        context = request.get("context", "casual")
        
        # Try Deeja agent first
        try:
            deeja_response = await deeja_agent.process_message(message, context)
            
            # Create metadata entry for the interaction
            metadata_uuid = zynx_metadata.create_metadata(
                metadata_type="interaction",
                title=f"Deeja Chat Interaction",
                content=f"Input: {message}\nResponse: {deeja_response.text}",
                tags=["deeja", "chat", "cultural_ai"]
            )
            
            return {
                "message": deeja_response.text,
                "aiPlatform": "deeja",
                "culturalContext": {
                    "primaryCulture": "thai" if deeja_response.cultural_context.startswith("thai") else "international",
                    "emotion_score": deeja_response.emotion_score,
                    "politeness_level": deeja_response.politeness_level,
                    "thai_elements": deeja_response.thai_elements
                },
                "metadata_uuid": metadata_uuid,
                "attribution": deeja_agent.get_attribution(),
                "source": "deeja_agent",
                "culturalAccuracyScore": 0.95,
                "emotionalIntelligenceScore": deeja_response.emotion_score,
                "processingTime": 0.3
            }
            
        except Exception as deeja_error:
            logger.warning(f"Deeja agent error, falling back to local LLM: {deeja_error}")
            
            # Activate local LLM fallback
            await local_llm_fallback.activate_fallback("deeja_agent_error")
            
            # Detect Thai context
            is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in message)
            
            local_response = await local_llm_fallback.process_local(
                message, context, thai_context=is_thai
            )
            
            return {
                "message": local_response.text,
                "aiPlatform": "local_fallback",
                "culturalContext": {
                    "primaryCulture": "thai" if is_thai else "international",
                    "confidence": local_response.confidence,
                    "empathy_score": local_response.empathy_score
                },
                "source": local_response.source,
                "fallback_mode": True,
                "attribution": local_llm_fallback.get_status()["attribution"],
                "culturalAccuracyScore": local_response.confidence,
                "emotionalIntelligenceScore": local_response.empathy_score,
                "processingTime": 0.8
            }
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/api/v1/cultural/analyze")
async def cultural_analyze(request: dict):
    """Cultural analysis endpoint"""
    try:
        text = request.get("text", "")
        
        # Simple but effective cultural analysis
        is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in text)
        has_politeness = any(particle in text for particle in ["ครับ", "ค่ะ", "นะ", "จ้ะ"])
        
        return {
            "primaryCulture": "thai" if is_thai else "international",
            "language": "th-TH" if is_thai else "en-US",
            "formalityLevel": "formal" if has_politeness else "casual",
            "politenessLevel": 0.9 if has_politeness else (0.7 if is_thai else 0.6),
            "culturalMarkers": ["ครับ", "ค่ะ"] if has_politeness else [],
            "communicationStyle": "thai_polite" if is_thai and has_politeness else ("thai_casual" if is_thai else "international")
        }
    except Exception as e:
        logger.error(f"Error in cultural analyze: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def start():
    """Start the server"""
    uvicorn.run(
        app,
        host="0.0.0.0",  # Changed from 127.0.0.1 to 0.0.0.0 for production
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start() 