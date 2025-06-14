# zynx_agi/monitoring/middleware.py
"""
Zynx AGI Monitoring Middleware
Seamlessly integrates with existing FastAPI app
"""

import time
import json
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
from .zynx_monitor import zynx_monitor

logger = logging.getLogger(__name__)

class ZynxMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track Zynx AGI requests"""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.monitor = zynx_monitor
        
    async def dispatch(self, request: Request, call_next: Callable):
        # Start timing
        start_time = time.time()
        request_id = id(request)
        
        # Track active request
        self.monitor.websocket_connections += 1
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000  # ms
            
            # Track specific endpoints
            if self._is_chat_endpoint(request.url.path):
                await self._track_chat_request(request, response, processing_time)
            elif self._is_cultural_endpoint(request.url.path):
                await self._track_cultural_request(request, response, processing_time)
                
            return response
            
        except Exception as e:
            # Track errors
            self.monitor.track_ai_platform_error("system", str(e))
            raise
        finally:
            # Remove from active requests
            self.monitor.websocket_connections = max(0, self.monitor.websocket_connections - 1)
            
    def _is_chat_endpoint(self, path: str) -> bool:
        """Check if endpoint is chat-related"""
        chat_paths = ['/chat', '/api/v1/chat', '/message']
        return any(chat_path in path.lower() for chat_path in chat_paths)
        
    def _is_cultural_endpoint(self, path: str) -> bool:
        """Check if endpoint is cultural analysis related"""
        cultural_paths = ['/cultural', '/analyze']
        return any(cultural_path in path.lower() for cultural_path in cultural_paths)
        
    async def _track_chat_request(self, request: Request, response: Response, processing_time: float):
        """Track chat-specific metrics"""
        try:
            if hasattr(request, '_body'):
                body = await request.body()
                if body:
                    data = json.loads(body)
                    message = data.get('text', data.get('message', ''))
                    
                    # Mock cultural context (you can enhance this)
                    cultural_context = {
                        "primaryCulture": "thai" if any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in message) else "international",
                        "formalityLevel": 0.7,
                        "politenessLevel": 0.8
                    }
                    
                    self.monitor.track_chat_request(
                        message=message,
                        cultural_context=cultural_context,
                        processing_time=processing_time,
                        ai_platform="openai"  # Default, you can detect from request
                    )
        except Exception as e:
            logger.warning(f"Could not track chat request: {e}")
            
    async def _track_cultural_request(self, request: Request, response: Response, processing_time: float):
        """Track cultural analysis requests"""
        try:
            # Track cultural analysis
            self.monitor.cultural_analyses += 1
        except Exception as e:
            logger.warning(f"Could not track cultural request: {e}")