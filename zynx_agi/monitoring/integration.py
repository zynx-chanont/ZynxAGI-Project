# zynx_agi/monitoring/integration.py
"""
Easy integration functions for existing Zynx AGI codebase
"""

import time
from fastapi import FastAPI, WebSocket
from .middleware import ZynxMonitoringMiddleware
from .zynx_monitor import zynx_monitor
from .api_endpoints import create_monitoring_router
import logging

logger = logging.getLogger(__name__)

def setup_zynx_monitoring(app: FastAPI) -> None:
    """
    One-line setup for Zynx AGI monitoring
    
    Usage:
        from zynx_agi.monitoring.integration import setup_zynx_monitoring
        
        app = FastAPI()
        setup_zynx_monitoring(app)
    """
    
    # Add monitoring middleware
    app.add_middleware(ZynxMonitoringMiddleware)
    
    # Add monitoring API endpoints
    monitoring_router = create_monitoring_router()
    app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])
    
    # Start monitoring
    zynx_monitor.start_monitoring()
    
    logger.info("🚀 Zynx AGI Monitoring System integrated successfully!")
    
    return zynx_monitor

# Context managers and decorators for manual tracking
class track_chat_inference:
    """
    Context manager for tracking chat inference in existing code
    
    Usage:
        # In your existing chat.py
        with track_chat_inference(message, cultural_context, "openai") as tracker:
            response = await process_message_with_cultural_context(message, client)
            tracker.set_success(True)
    """
    
    def __init__(self, message: str, cultural_context: dict, ai_platform: str):
        self.message = message
        self.cultural_context = cultural_context
        self.ai_platform = ai_platform
        self.start_time = None
        self.success = False
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            processing_time = (time.time() - self.start_time) * 1000
            
            if exc_type is not None:
                # Error occurred
                zynx_monitor.track_ai_platform_error(self.ai_platform, str(exc_val))
            else:
                # Success
                zynx_monitor.track_chat_request(
                    message=self.message,
                    cultural_context=self.cultural_context,
                    processing_time=processing_time,
                    ai_platform=self.ai_platform
                )
                
    def set_success(self, success: bool):
        self.success = success

def track_websocket_connection(websocket: WebSocket, connected: bool):
    """Helper function to track WebSocket connections"""
    zynx_monitor.track_websocket_connection(connected)

def track_cultural_switch(from_culture: str, to_culture: str):
    """Helper function to track cultural context switches"""
    zynx_monitor.track_cultural_context_switch(from_culture, to_culture)