# zynx_agi/monitoring/api_endpoints.py
"""
API endpoints for Zynx AGI monitoring dashboard
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any, Optional
import json
from .zynx_monitor import zynx_monitor

def create_monitoring_router() -> APIRouter:
    """Create monitoring API router"""
    
    router = APIRouter()
    
    @router.get("/metrics/current")
    async def get_current_zynx_metrics():
        """Get current Zynx AGI metrics"""
        if zynx_monitor.metrics_buffer:
            latest = zynx_monitor.metrics_buffer[-1]
            data = {
                "timestamp": latest.timestamp.isoformat(),
                "performance": {
                    "inference_time_ms": latest.inference_time_ms,
                    "tokens_per_second": latest.tokens_per_second,
                    "concurrent_requests": latest.concurrent_requests,
                    "queue_depth": latest.queue_depth
                },
                "cultural_intelligence": {
                    "cultural_accuracy": latest.cultural_accuracy_score,
                    "emotional_intelligence": latest.emotional_intelligence_score,
                    "thai_proficiency": latest.thai_language_proficiency,
                    "formality_detection": latest.formality_detection_accuracy,
                    "avg_politeness": latest.politeness_level_avg
                },
                "ai_platforms": {
                    "openai_requests": latest.openai_requests,
                    "claude_requests": latest.claude_requests,
                    "errors": latest.ai_platform_errors
                },
                "system": {
                    "cpu_percent": latest.cpu_percent,
                    "memory_percent": latest.memory_percent,
                    "active_websockets": latest.active_websockets,
                    "success_rate": latest.success_rate,
                    "uptime_seconds": latest.uptime_seconds
                },
                "language_usage": {
                    "thai_ratio": latest.thai_messages_ratio,
                    "english_ratio": latest.english_messages_ratio,
                    "cultural_switches": latest.cultural_context_switches
                }
            }
            return data
        return {"error": "No metrics available"}
    
    @router.get("/summary")
    async def get_zynx_performance_summary(hours: int = 24):
        """Get Zynx AGI performance summary"""
        return zynx_monitor.get_zynx_performance_summary(hours)
    
    @router.get("/health")
    async def get_zynx_health():
        """Zynx AGI specific health check"""
        summary = zynx_monitor.get_zynx_performance_summary(hours=1)
        health_score = summary.get("zynx_health_score", 0)
        
        return {
            "status": "healthy" if health_score > 80 else ("degraded" if health_score > 60 else "critical"),
            "health_score": health_score,
            "cultural_intelligence": summary.get("cultural_intelligence", {}),
            "ai_platform_health": summary.get("ai_platform_usage", {}),
            "recommendations": summary.get("recommendations", []),
            "uptime_hours": summary.get("performance", {}).get("uptime_hours", 0)
        }
    
    @router.websocket("/ws/metrics")
    async def websocket_metrics_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time Zynx metrics"""
        await websocket.accept()
        zynx_monitor.websocket_clients.add(websocket)
        
        try:
            while True:
                await websocket.receive_text()  # Keep connection alive
        except WebSocketDisconnect:
            zynx_monitor.websocket_clients.discard(websocket)
        except Exception as e:
            zynx_monitor.websocket_clients.discard(websocket)
    
    @router.get("/cultural/stats")
    async def get_cultural_statistics():
        """Get cultural intelligence statistics"""
        summary = zynx_monitor.get_zynx_performance_summary(hours=24)
        return {
            "cultural_intelligence": summary.get("cultural_intelligence", {}),
            "language_distribution": summary.get("language_distribution", {}),
            "recent_cultural_switches": summary.get("cultural_intelligence", {}).get("cultural_context_switches", 0)
        }
    
    @router.get("/ai-platforms/usage")
    async def get_ai_platform_usage():
        """Get AI platform usage statistics"""
        summary = zynx_monitor.get_zynx_performance_summary(hours=24)
        return summary.get("ai_platform_usage", {})
    
    @router.post("/test/simulate-load")
    async def simulate_load(requests: int = 10):
        """Simulate load for testing monitoring system"""
        import asyncio
        import random
        
        async def simulate_request():
            # Simulate Thai or English message
            is_thai = random.choice([True, False])
            message = "สวัสดีครับ" if is_thai else "Hello"
            
            cultural_context = {
                "primaryCulture": "thai" if is_thai else "international",
                "formalityLevel": random.uniform(0.5, 1.0),
                "politenessLevel": random.uniform(0.6, 0.9)
            }
            
            zynx_monitor.track_chat_request(
                message=message,
                cultural_context=cultural_context,
                processing_time=random.uniform(300, 1200),
                ai_platform=random.choice(["openai", "claude"])
            )
        
        # Simulate concurrent requests
        tasks = [simulate_request() for _ in range(requests)]
        await asyncio.gather(*tasks)
        
        return {"message": f"Simulated {requests} requests", "status": "completed"}
    
    return router