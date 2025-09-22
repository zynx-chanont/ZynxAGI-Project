from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
from .config.settings import settings
from .agents.agent_registry import registry, AgentManifest
from .agents.coded_agent import CodeDAgent

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

# --- SERVE REACT APP ---
# Mount the React frontend static files (only if directory exists)
frontend_dist = "frontend/dist"
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

# --- INITIALIZE AGENTS ---
# Initialize and register agents
def initialize_agents():
    """Initialize and register all agents"""
    try:
        # Initialize CodeD Agent
        coded_agent = CodeDAgent()
        coded_manifest = AgentManifest({
            "name": "CodeD",
            "version": "1.0.0", 
            "description": "Specialized coding assistant for generating, analyzing, and debugging code",
            "capabilities": coded_agent.get_capabilities(),
            "mcp_command": "/coded",
            "status": "live"
        })
        
        # Register the agent
        registry.register_agent("coded", coded_manifest, coded_agent)
        logger.info("CodeD agent registered successfully")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        return False

# Initialize agents on startup
initialize_agents()

# --- MCP COMMAND PROCESSING ---
async def process_mcp_command(message: str, context: dict = None) -> dict:
    """Process MCP (Model Context Protocol) commands"""
    try:
        # Check if message starts with MCP command
        if not message.strip().startswith('/'):
            return None
        
        # Parse command
        parts = message.strip().split(' ', 1)
        command = parts[0].lower()
        command_text = parts[1] if len(parts) > 1 else ""
        
        # Route to appropriate agent
        if command == "/coded":
            agent = registry.get_agent_instance("coded")
            if agent:
                return await agent.process_request(command_text, context)
            else:
                return {
                    "success": False,
                    "error": "CodeD agent not available",
                    "message": "The coding assistant is currently unavailable. Please try again later."
                }
        
        # Unknown command
        return {
            "success": False,
            "error": "Unknown MCP command",
            "message": f"Unknown command: {command}. Available commands: /coded",
            "available_commands": ["/coded"]
        }
        
    except Exception as e:
        logger.error(f"Error processing MCP command: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error processing command. Please try again."
        }

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
    """Chat endpoint with MCP command support and cultural intelligence"""
    try:
        message = request.get("message", "")
        
        # Check for MCP commands first
        mcp_response = await process_mcp_command(message)
        if mcp_response:
            # Format MCP response for chat interface
            if mcp_response.get("success"):
                return {
                    "message": mcp_response.get("message", str(mcp_response)),
                    "aiPlatform": mcp_response.get("agent", "unknown"),
                    "culturalContext": {
                        "primaryCulture": "technical",
                        "formalityLevel": "professional",
                        "politenessLevel": 0.8,
                        "culturalMarkers": [],
                        "communicationStyle": "technical_assistance"
                    },
                    "culturalAccuracyScore": 0.9,
                    "emotionalIntelligenceScore": 0.8,
                    "processingTime": 0.3,
                    "mcp_data": mcp_response  # Include full MCP response
                }
            else:
                return {
                    "message": mcp_response.get("message", "Command failed"),
                    "aiPlatform": "mcp_error",
                    "culturalContext": {
                        "primaryCulture": "error",
                        "formalityLevel": "helpful",
                        "politenessLevel": 0.8,
                        "culturalMarkers": [],
                        "communicationStyle": "error_assistance"
                    },
                    "culturalAccuracyScore": 0.7,
                    "emotionalIntelligenceScore": 0.7,
                    "processingTime": 0.1,
                    "error": mcp_response.get("error")
                }
        
        # Detect Thai or English for regular messages
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

# Agents endpoints
@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents"""
    try:
        agents_list = registry.list_agents()
        return {
            "agents": agents_list,
            "stats": registry.get_stats(),
            "available_commands": ["/coded"]
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    """Get information about a specific agent"""
    try:
        manifest = registry.get_agent_manifest(agent_id)
        if not manifest:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent_instance = registry.get_agent_instance(agent_id)
        health = await agent_instance.health_check() if agent_instance else {"status": "unknown"}
        
        return {
            "agent_id": agent_id,
            "manifest": manifest,
            "health": health
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/agents/{agent_id}/process")
async def process_agent_request(agent_id: str, request: dict):
    """Process a request through a specific agent"""
    try:
        agent_instance = registry.get_agent_instance(agent_id)
        if not agent_instance:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        message = request.get("message", "")
        context = request.get("context", {})
        
        response = await agent_instance.process_request(message, context)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}")
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