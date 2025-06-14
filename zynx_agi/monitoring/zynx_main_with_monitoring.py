# zynx_agi/main.py (Modified with Monitoring Integration)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from .config.settings import settings

# ========== ZYNX MONITORING INTEGRATION ==========
from .monitoring.integration import setup_zynx_monitoring
from .monitoring.zynx_monitor import zynx_monitor
# =================================================

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ZynxAGI",
    description="Universal AI Orchestration Platform with Cultural-Emotional Intelligence + Real-time Monitoring",
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

# ========== SETUP ZYNX MONITORING ==========
# One-line integration - adds middleware, endpoints, and starts monitoring
setup_zynx_monitoring(app)
logger.info("🔥 Zynx AGI Monitoring System activated!")
# ==========================================

# --- SERVE REACT APP ---
# Mount the React frontend static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

@app.get("/")
async def root():
    """Root endpoint with monitoring metrics"""
    try:
        # Get real-time health from monitoring
        health_data = zynx_monitor.get_zynx_performance_summary(hours=1)
        health_score = health_data.get("zynx_health_score", 95)
        
        return {
            "message": "Welcome to ZynxAGI - Universal AI Orchestration Platform",
            "version": "1.0.0",
            "cultural_intelligence": "Thai-English Bridge Active",
            "status": "operational",
            "docs": "/docs",
            "monitoring": "/api/v1/monitoring/health",
            "health_score": f"{health_score:.1f}%",
            "emoji": "🚀🔥"
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Enhanced health check with monitoring data"""
    try:
        # Get monitoring data
        monitoring_summary = zynx_monitor.get_zynx_performance_summary(hours=1)
        
        return {
            "status": "healthy",
            "app": "ZynxAGI",
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                "cultural_intelligence": "ready",
                "universal_dispatcher": "ready",
                "monitoring_system": "active"
            },
            "message": "ZynxAGI is running successfully! 🌟",
            "thai_message": "ระบบ ZynxAGI ทำงานปกติค่ะ! 🇹🇭",
            "monitoring": {
                "health_score": monitoring_summary.get("zynx_health_score", 95),
                "cultural_accuracy": monitoring_summary.get("cultural_intelligence", {}).get("avg_cultural_accuracy", 0.95),
                "active_connections": monitoring_summary.get("performance", {}).get("active_websockets", 0),
                "uptime_hours": monitoring_summary.get("performance", {}).get("uptime_hours", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Chat endpoint for testing (enhanced with monitoring)
@app.post("/api/v1/chat/message")
async def chat_message(request: dict):
    """Chat endpoint with automatic monitoring tracking"""
    import time
    start_time = time.time()
    
    try:
        message = request.get("message", "")

        # Detect Thai or English
        is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in message)

        if "สวัสดี" in message or "hello" in message.lower() or "hi" in message.lower():
            if is_thai:
                response_text = "สวัสดีค่ะ! ยินดีต้อนรับสู่ ZynxAGI 🌟 ฉันคือ Deeja น้องดีจ้าที่จะช่วยคุณเชื่อมต่อกับ AI ที่เหมาะสมที่สุดพร้อมความเข้าใจทางวัฒนธรรม! ระบบกำลังพัฒนาอยู่แต่พร้อมช่วยเหลือคุณแล้วค่ะ ✨"
                cultural_context = {
                    "primaryCulture": "thai",
                    "formalityLevel": 0.9,
                    "politenessLevel": 0.9,
                    "culturalMarkers": ["ค่ะ", "kreng_jai"],
                    "communicationStyle": "warm_thai"
                }
            else:
                response_text = "Hello! Welcome to ZynxAGI 🌟 I'm Deeja, your cultural-intelligent AI assistant who will help you connect with the most suitable AI while understanding cultural nuances! The system is under development but ready to help you! ✨"
                cultural_context = {
                    "primaryCulture": "international",
                    "formalityLevel": 0.7,
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
                "formalityLevel": 0.8,
                "politenessLevel": 0.8 if is_thai else 0.7,
                "culturalMarkers": ["ค่ะ"] if is_thai else [],
                "communicationStyle": "helpful_thai" if is_thai else "helpful_international"
            }

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # ========== TRACK WITH MONITORING SYSTEM ==========
        zynx_monitor.track_chat_request(
            message=message,
            cultural_context=cultural_context,
            processing_time=processing_time,
            ai_platform="deeja"  # Internal Deeja system
        )
        # =================================================

        return {
            "message": response_text,
            "aiPlatform": "deeja",
            "culturalContext": cultural_context,
            "culturalAccuracyScore": 0.95,
            "emotionalIntelligenceScore": 0.88,
            "processingTime": processing_time / 1000,  # Convert to seconds
            "monitoring": {
                "tracked": True,
                "processing_time_ms": processing_time
            }
        }
    except Exception as e:
        # Track error with monitoring
        zynx_monitor.track_ai_platform_error("deeja", str(e))
        logger.error(f"Error in chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/cultural/analyze")
async def cultural_analyze(request: dict):
    """Cultural analysis endpoint with monitoring"""
    import time
    start_time = time.time()
    
    try:
        text = request.get("text", "")

        # Simple but effective cultural analysis
        is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in text)
        has_politeness = any(particle in text for particle in ["ครับ", "ค่ะ", "นะ", "จ้ะ"])

        result = {
            "primaryCulture": "thai" if is_thai else "international",
            "language": "th-TH" if is_thai else "en-US",
            "formalityLevel": 0.9 if has_politeness else 0.6,
            "politenessLevel": 0.9 if has_politeness else (0.7 if is_thai else 0.6),
            "culturalMarkers": ["ครับ", "ค่ะ"] if has_politeness else [],
            "communicationStyle": "thai_polite" if is_thai and has_politeness else ("thai_casual" if is_thai else "international")
        }
        
        # Track cultural analysis
        processing_time = (time.time() - start_time) * 1000
        zynx_monitor.cultural_analyses += 1
        
        return result
        
    except Exception as e:
        logger.error(f"Error in cultural analyze: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== NEW MONITORING ENDPOINTS ==========
@app.get("/api/v1/monitoring/dashboard")
async def get_monitoring_dashboard():
    """Get monitoring dashboard data"""
    try:
        current_metrics = {}
        if zynx_monitor.metrics_buffer:
            latest = zynx_monitor.metrics_buffer[-1]
            current_metrics = {
                "cultural_accuracy": latest.cultural_accuracy_score,
                "thai_proficiency": latest.thai_language_proficiency,
                "emotional_intelligence": latest.emotional_intelligence_score,
                "inference_time_ms": latest.inference_time_ms,
                "active_websockets": latest.active_websockets,
                "thai_message_ratio": latest.thai_messages_ratio
            }
        
        summary = zynx_monitor.get_zynx_performance_summary(hours=24)
        
        return {
            "current_metrics": current_metrics,
            "summary": summary,
            "status": "active",
            "dashboard_url": "/monitoring/dashboard.html"
        }
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving monitoring data")

@app.get("/api/v1/system/stats")
async def get_system_stats():
    """Get system statistics with Zynx-specific metrics"""
    try:
        return {
            "chat_requests": zynx_monitor.chat_requests,
            "thai_messages": zynx_monitor.thai_messages,
            "english_messages": zynx_monitor.english_messages,
            "cultural_analyses": zynx_monitor.cultural_analyses,
            "cultural_switches": zynx_monitor.cultural_context_switches,
            "ai_platform_usage": zynx_monitor.ai_platform_usage,
            "active_websockets": zynx_monitor.websocket_connections,
            "uptime_seconds": int((zynx_monitor.start_time).total_seconds()) if zynx_monitor.start_time else 0
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving system statistics")
# =============================================

def start():
    """Start the server with monitoring"""
    logger.info("🚀 Starting ZynxAGI with Advanced Monitoring System...")
    logger.info("📊 Monitoring Dashboard: http://localhost:8000/api/v1/monitoring/health")
    logger.info("📈 Real-time Metrics: http://localhost:8000/api/v1/monitoring/metrics/current")
    logger.info("🎯 Cultural Intelligence: http://localhost:8000/api/v1/monitoring/cultural/stats")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start()
