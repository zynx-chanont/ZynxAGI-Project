from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import asyncio
from .config.settings import settings
from .agents.zynx_metadata import observe_interaction

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers after app creation
def register_routers():
    """Register API routers"""
    try:
        from .api.chat import router as chat_router
        from .api.cultural import router as cultural_router
        from .api.metadata import router as metadata_router
        from .api.export import router as export_router
        
        app.include_router(chat_router)
        app.include_router(cultural_router)
        app.include_router(metadata_router)
        app.include_router(export_router)
        logger.info("API routers registered successfully")
    except Exception as e:
        logger.warning(f"Some API routers could not be registered: {e}")

# Register routers
register_routers()

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
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "app": "ZynxAGI",
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                "cultural_intelligence": "ready",
                "universal_dispatcher": "ready"
            },
            "message": "ZynxAGI is running successfully! 🌟",
            "thai_message": "ระบบ ZynxAGI ทำงานปกติค่ะ! 🇹🇭"
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Chat endpoint for testing
@app.post("/api/v1/chat/message")
async def chat_message(request: dict):
    """Chat endpoint for testing Frontend integration"""
    try:
        message = request.get("message", "")
        
        # Detect Thai or English
        is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in message)
        
        if "สวัสดี" in message or "hello" in message.lower() or "hi" in message.lower():
            if is_thai:
                response_text = "สวัสดีค่ะ! ยินดีต้อนรับสู่ ZynxAGI 🌟 ฉันคือ Deeja น้องดีจ้าที่จะช่วยคุณเชื่อมต่อกับ AI ที่เหมาะสมที่สุดพร้อมความเข้าใจทางวัฒนธรรม! ระบบกำลังพัฒนาอยู่แต่พร้อมช่วยเหลือคุณแล้วค่ะ ✨"
                cultural_context = {
                    "primaryCulture": "thai",
                    "formalityLevel": "casual",
                    "politenessLevel": 0.9,
                    "culturalMarkers": ["ค่ะ", "kreng_jai"],
                    "communicationStyle": "warm_thai"
                }
            else:
                response_text = "Hello! Welcome to ZynxAGI 🌟 I'm Deeja, your cultural-intelligent AI assistant who will help you connect with the most suitable AI while understanding cultural nuances! The system is under development but ready to help you! ✨"
                cultural_context = {
                    "primaryCulture": "international",
                    "formalityLevel": "friendly",
                    "politenessLevel": 0.7,
                    "culturalMarkers": [],
                    "communicationStyle": "warm_international"
                }
        else:
            if is_thai:
                response_text = f"ขอบคุณสำหรับข้อความ: '{message}' ค่ะ 🙏 ZynxAGI กำลังพัฒนาระบบความฉลาดทางวัฒนธรรมเพื่อเข้าใจการสื่อสารแบบไทยและสากลค่ะ ฉันพร้อมช่วยเหลือคุณ! 🤖💫"
            else:
                response_text = f"Thank you for your message: '{message}' 🙏 ZynxAGI is developing cultural intelligence to understand both Thai and international communication styles. I'm here to help! 🤖💫"
            
            cultural_context = {
                "primaryCulture": "thai" if is_thai else "international",
                "formalityLevel": "casual",
                "politenessLevel": 0.8 if is_thai else 0.7,
                "culturalMarkers": ["ค่ะ"] if is_thai else [],
                "communicationStyle": "helpful_thai" if is_thai else "helpful_international"
            }
        
        # Observer: Track chat interaction
        asyncio.create_task(
            observe_interaction(
                agent_name="deeja_basic",
                user_input=message,
                agent_response=response_text,
                context={
                    "endpoint": "/api/v1/chat/message",
                    "language": "thai" if is_thai else "english",
                    "cultural_context": cultural_context
                }
            )
        )
        
        return {
            "message": response_text,
            "aiPlatform": "deeja",
            "culturalContext": cultural_context,
            "culturalAccuracyScore": 0.95,
            "emotionalIntelligenceScore": 0.88,
            "processingTime": 0.5
        }
    except Exception as e:
        logger.error(f"Error in chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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