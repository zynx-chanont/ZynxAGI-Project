from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union, Literal
import json
import logging
import asyncio
from datetime import datetime
from ..config.settings import settings
from ..cultural.thai_cultural_engine import ThaiCulturalEngine
from ..ai_platforms.openai_client import OpenAIClient
from ..ai_platforms.claude_client import ClaudeClient
from ..ai_platforms.thai_cultural_mcp import get_current_user, TokenData
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
cultural_engine = ThaiCulturalEngine()

# Request/Response Models
class CulturalContext(BaseModel):
    """Cultural context model"""
    formality_level: float
    politeness_level: float
    cultural_elements: Dict[str, float]
    detected_particles: List[str]
    cultural_patterns: List[str]

class ChatMessage(BaseModel):
    """Chat message model"""
    text: str = Field(..., min_length=1, max_length=4000)
    context: Optional[CulturalContext] = None
    model: str = Field("deeja-v1", description="AI model to use")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(1000, gt=0)

class ChatResponse(BaseModel):
    """Chat response model"""
    text: str
    model: str
    usage: Dict[str, int]
    processing_time: float
    cultural_context: CulturalContext
    suggestions: List[str]

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: Literal["message", "typing", "error", "system"] = Field(..., description="Message type")
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.user_sessions[client_id] = {
            "connected_at": datetime.now(),
            "message_count": 0,
            "last_message": None
        }
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.user_sessions:
            del self.user_sessions[client_id]
            
    async def send_message(self, client_id: str, message: WebSocketMessage):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message.dict())
            if client_id in self.user_sessions:
                self.user_sessions[client_id]["message_count"] += 1
                self.user_sessions[client_id]["last_message"] = datetime.now()
            
    async def broadcast(self, message: WebSocketMessage, exclude: Optional[str] = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_json(message.dict())
                
    def get_session_stats(self, client_id: str) -> Optional[Dict[str, Any]]:
        return self.user_sessions.get(client_id)

manager = ConnectionManager()

# AI Client Factory
def get_ai_client(model: Optional[str] = None) -> Union[OpenAIClient, ClaudeClient]:
    """Get appropriate AI client based on model selection"""
    if model == "claude":
        return ClaudeClient()
    return OpenAIClient()  # Default to OpenAI

async def process_message_with_cultural_context(
    message: ChatMessage,
    client: Union[OpenAIClient, ClaudeClient]
) -> Dict[str, Any]:
    """Process message with cultural context and generate response"""
    # Process with cultural context
    if message.context:
        processed_context = await cultural_engine.process_message({
            "text": message.text,
            "context_type": "formal" if message.context["formality_level"] > 0.7 else "informal"
        })
        message.text = processed_context["adjusted_text"]
        message.context = CulturalContext(**processed_context["cultural_context"])
    
    # Generate response
    return await client.generate_response(
        message=message.text,
        cultural_context=message.context.dict() if message.context else None,
        temperature=message.temperature,
        max_tokens=message.max_tokens
    )

# MCP Client
class ThaiCulturalMCPClient:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.token = None
    
    async def login(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/token",
                data={"username": "admin", "password": "password"}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
            else:
                raise HTTPException(status_code=401, detail="Failed to authenticate with MCP server")
    
    async def analyze_cultural_context(self, text: str) -> Dict[str, Any]:
        if not self.token:
            await self.login()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/cultural/analyze",
                json={"text": text},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=500, detail="Failed to analyze cultural context")
    
    async def adjust_cultural_context(self, text: str) -> str:
        if not self.token:
            await self.login()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/cultural/adjust",
                json={"text": text},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()["adjusted_text"]
            else:
                raise HTTPException(status_code=500, detail="Failed to adjust cultural context")

# Initialize MCP client
mcp_client = ThaiCulturalMCPClient()

# REST Endpoints
@router.post("/message", response_model=ChatResponse)
async def chat_message(
    message: ChatMessage,
    background_tasks: BackgroundTasks
):
    """Process a chat message with cultural context"""
    start_time = datetime.now()
    
    try:
        # Get AI client
        client = get_ai_client(message.model)
        
        # Process message and generate response
        response = await process_message_with_cultural_context(message, client)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Log usage in background
        background_tasks.add_task(
            log_chat_usage,
            message=message,
            response=response,
            processing_time=processing_time
        )
        
        return ChatResponse(
            text=response["text"],
            model=response["model"],
            usage=response["usage"],
            cultural_context=message.context,
            processing_time=processing_time,
            suggestions=response["suggestions"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )
    finally:
        if 'client' in locals():
            await client.close()

async def log_chat_usage(message: ChatMessage, response: Dict[str, Any], processing_time: float):
    """Log chat usage statistics"""
    try:
        logger.info(
            f"Chat Usage - Model: {response['model']}, "
            f"Tokens: {response['usage']['total_tokens']}, "
            f"Time: {processing_time:.2f}s"
        )
    except Exception as e:
        logger.error(f"Error logging chat usage: {str(e)}")

# WebSocket Endpoints
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create chat message
            chat_message = ChatMessage(**message_data)
            
            # Send typing indicator
            await manager.send_message(
                client_id,
                WebSocketMessage(
                    type="typing",
                    content={"status": "processing"}
                )
            )
            
            try:
                # Get AI client
                client = get_ai_client(chat_message.model)
                
                # Process message and generate response
                response = await process_message_with_cultural_context(chat_message, client)
                
                # Send response
                await manager.send_message(
                    client_id,
                    WebSocketMessage(
                        type="message",
                        content={
                            "text": response["text"],
                            "model": response["model"],
                            "usage": response["usage"],
                            "cultural_context": response["cultural_context"]
                        }
                    )
                )
                
            except Exception as e:
                logger.error(f"Error in WebSocket chat: {str(e)}")
                await manager.send_message(
                    client_id,
                    WebSocketMessage(
                        type="error",
                        content={"error": str(e)}
                    )
                )
            finally:
                if 'client' in locals():
                    await client.close()
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(
            WebSocketMessage(
                type="system",
                content={"message": f"Client {client_id} disconnected"}
            )
        )
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)

@router.get("/ws/stats/{client_id}")
async def get_websocket_stats(client_id: str):
    """Get WebSocket session statistics"""
    stats = manager.get_session_stats(client_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Client session not found")
    return stats

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: TokenData = Depends(get_current_user)
):
    """Chat endpoint with cultural intelligence"""
    try:
        # Analyze cultural context
        cultural_analysis = await mcp_client.analyze_cultural_context(message.text)
        
        # Adjust response based on cultural context
        adjusted_response = await mcp_client.adjust_cultural_context(message.text)
        
        # Create cultural context
        cultural_context = CulturalContext(
            formality_level=cultural_analysis["formality_level"],
            politeness_level=cultural_analysis["politeness_level"],
            cultural_elements=cultural_analysis["cultural_elements"],
            detected_particles=cultural_analysis["detected_particles"],
            cultural_patterns=cultural_analysis["cultural_patterns"]
        )
        
        return ChatResponse(
            text=adjusted_response,
            model=message.model,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            processing_time=0.0,
            cultural_context=cultural_context,
            suggestions=cultural_analysis["suggestions"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cultural/prompts")
async def get_prompts(
    current_user: TokenData = Depends(get_current_user)
):
    """Get available cultural prompts"""
    if not mcp_client.token:
        await mcp_client.login()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{mcp_client.base_url}/api/v1/cultural/prompts",
            headers={"Authorization": f"Bearer {mcp_client.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to get cultural prompts")

@router.get("/cultural/resources")
async def get_resources(
    current_user: TokenData = Depends(get_current_user)
):
    """Get available cultural resources"""
    if not mcp_client.token:
        await mcp_client.login()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{mcp_client.base_url}/api/v1/cultural/resources",
            headers={"Authorization": f"Bearer {mcp_client.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to get cultural resources") 