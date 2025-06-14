# zynx_monitoring_integration.py
# Easy integration of Zynx AGI Monitoring into your existing FastAPI project

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from typing import Optional, Dict, Any
import json
from datetime import datetime
import threading
from zynx_monitoring_core import ZynxAGIMonitor, AGIMetrics

class ZynxMonitoringMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to automatically track AI inference metrics
    Integrates seamlessly with your existing Zynx AGI endpoints
    """
    
    def __init__(self, app: FastAPI, monitor: ZynxAGIMonitor):
        super().__init__(app)
        self.monitor = monitor
        self.active_requests = {}
        
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        request_id = id(request)
        
        # Track active request
        self.monitor.active_requests[request_id] = {
            "start_time": start_time,
            "endpoint": request.url.path,
            "method": request.method
        }
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Remove from active requests
        if request_id in self.monitor.active_requests:
            del self.monitor.active_requests[request_id]
        
        # Track AI-specific endpoints
        if self._is_ai_endpoint(request.url.path):
            await self._track_ai_metrics(request, response, duration_ms)
            
        return response
        
    def _is_ai_endpoint(self, path: str) -> bool:
        """Check if endpoint is AI-related"""
        ai_paths = ['/chat', '/generate', '/inference', '/ai', '/zynx']
        return any(ai_path in path.lower() for ai_path in ai_paths)
        
    async def _track_ai_metrics(self, request: Request, response: Response, duration_ms: float):
        """Track specific AI metrics for Zynx endpoints"""
        # You can implement custom tracking logic here
        # This will be called for each AI request
        pass

class ZynxIntegration:
    """
    Main integration class for adding Zynx AGI monitoring to your FastAPI app
    """
    
    def __init__(self, app: FastAPI, db_path: str = "zynx_metrics.db"):
        self.app = app
        self.monitor = ZynxAGIMonitor(db_path)
        self.inference_tracker = ZynxInferenceTracker(self.monitor)
        
        # Add middleware
        app.add_middleware(ZynxMonitoringMiddleware, monitor=self.monitor)
        
        # Add monitoring routes
        self._add_monitoring_routes()
        
        # Start monitoring
        self.monitor.start_monitoring()
        
    def _add_monitoring_routes(self):
        """Add monitoring endpoints to your FastAPI app"""
        
        @self.app.get("/zynx/metrics/current")
        async def get_current_metrics():
            """Get current Zynx AGI metrics"""
            if self.monitor.metrics_buffer:
                latest = self.monitor.metrics_buffer[-1]
                return {
                    "timestamp": latest.timestamp.isoformat(),
                    "performance": {
                        "inference_time_ms": latest.inference_time_ms,
                        "tokens_per_second": latest.tokens_per_second,
                        "queue_depth": latest.queue_depth,
                        "gpu_utilization": latest.gpu_utilization
                    },
                    "quality": {
                        "response_quality": latest.response_quality_score,
                        "cultural_accuracy": latest.cultural_accuracy_score,
                        "emotional_intelligence": latest.emotional_intelligence_score,
                        "thai_proficiency": latest.thai_language_proficiency
                    },
                    "system": {
                        "cpu_percent": latest.cpu_percent,
                        "memory_percent": latest.memory_percent,
                        "success_rate": latest.success_rate,
                        "uptime_seconds": latest.uptime_seconds
                    }
                }
            return {"error": "No metrics available"}
            
        @self.app.get("/zynx/health")
        async def get_health_check():
            """Zynx AGI health check endpoint"""
            summary = self.monitor.get_performance_summary(hours=1)
            return {
                "status": "healthy" if summary.get("zynx_health_score", 0) > 70 else "degraded",
                "health_score": summary.get("zynx_health_score", 0),
                "bottlenecks": summary.get("bottlenecks", []),
                "recommendations": summary.get("recommendations", [])
            }
            
        @self.app.get("/zynx/dashboard")
        async def serve_dashboard():
            """Serve the monitoring dashboard (redirect to frontend)"""
            return {"message": "Access dashboard at /zynx/dashboard.html"}

class ZynxInferenceTracker:
    """
    Helper class to track AI inference metrics
    Use this in your AI endpoints to get detailed metrics
    """
    
    def __init__(self, monitor: ZynxAGIMonitor):
        self.monitor = monitor
        
    def track_inference(self, 
                       model_name: str,
                       input_tokens: int,
                       output_tokens: int,
                       inference_time_ms: float,
                       quality_scores: Optional[Dict[str, float]] = None):
        """
        Track a single AI inference
        Call this in your chat/generate endpoints
        """
        # Calculate tokens per second
        tokens_per_second = output_tokens / (inference_time_ms / 1000) if inference_time_ms > 0 else 0
        
        # Update baselines if needed
        if hasattr(self.monitor, 'inference_history'):
            self.monitor.inference_history.append({
                "timestamp": datetime.now(),
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "inference_time_ms": inference_time_ms,
                "tokens_per_second": tokens_per_second,
                "quality_scores": quality_scores or {}
            })
        
        # Log for analysis
        print(f"🧠 Zynx Inference: {model_name} | {inference_time_ms:.1f}ms | {tokens_per_second:.1f} tok/s")

# Easy setup function
def setup_zynx_monitoring(app: FastAPI, db_path: str = "zynx_metrics.db") -> ZynxIntegration:
    """
    One-line setup for Zynx AGI monitoring
    
    Usage:
        from zynx_monitoring_integration import setup_zynx_monitoring
        
        app = FastAPI()
        zynx = setup_zynx_monitoring(app)
        
        @app.post("/chat")
        async def chat_endpoint(request: ChatRequest):
            start_time = time.time()
            
            # Your AI logic here
            response = await your_ai_function(request.message)
            
            # Track the inference
            inference_time = (time.time() - start_time) * 1000
            zynx.inference_tracker.track_inference(
                model_name="zynx-deeja-v1",
                input_tokens=len(request.message.split()),
                output_tokens=len(response.split()),
                inference_time_ms=inference_time,
                quality_scores={
                    "cultural_accuracy": 0.95,
                    "emotional_intelligence": 0.88
                }
            )
            
            return {"response": response}
    """
    return ZynxIntegration(app, db_path)

# Context manager for tracking inference
class track_zynx_inference:
    """
    Context manager for easy inference tracking
    
    Usage:
        with track_zynx_inference(zynx.inference_tracker, "zynx-deeja-v1") as tracker:
            response = await ai_model.generate(prompt)
            tracker.set_tokens(input_tokens=100, output_tokens=200)
            tracker.set_quality(cultural_accuracy=0.95)
    """
    
    def __init__(self, tracker: ZynxInferenceTracker, model_name: str):
        self.tracker = tracker
        self.model_name = model_name
        self.start_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.quality_scores = {}
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            inference_time_ms = (time.time() - self.start_time) * 1000
            self.tracker.track_inference(
                model_name=self.model_name,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                inference_time_ms=inference_time_ms,
                quality_scores=self.quality_scores
            )
    
    def set_tokens(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        
    def set_quality(self, **quality_scores):
        self.quality_scores.update(quality_scores)

# Decorator for automatic tracking
def zynx_track(model_name: str = "zynx-model", tracker_var: str = "zynx_tracker"):
    """
    Decorator to automatically track AI function calls
    
    Usage:
        @zynx_track(model_name="zynx-deeja-v1")
        async def generate_response(prompt: str) -> str:
            # Your AI logic
            return response
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get tracker from globals or function args
            tracker = kwargs.pop(tracker_var, None)
            if not tracker:
                # Try to find tracker in global scope
                import inspect
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    tracker = frame.f_back.f_globals.get(tracker_var)
            
            if tracker:
                with track_zynx_inference(tracker, model_name) as t:
                    result = await func(*args, **kwargs)
                    # Auto-detect tokens if result is string
                    if isinstance(result, str):
                        t.set_tokens(
                            input_tokens=len(str(args[0]).split()) if args else 0,
                            output_tokens=len(result.split())
                        )
                    return result
            else:
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Configuration helper
class ZynxMonitoringConfig:
    """Configuration class for Zynx monitoring"""
    
    def __init__(self):
        self.db_path = "zynx_metrics.db"
        self.collection_interval = 5  # seconds
        self.history_retention_hours = 24
        self.alert_thresholds = {
            "inference_time_ms": 1000,
            "gpu_utilization": 95,
            "queue_depth": 10,
            "cultural_accuracy": 0.85
        }
        self.enable_websocket = True
        self.websocket_port = 8001
        
    def to_dict(self):
        return {
            "db_path": self.db_path,
            "collection_interval": self.collection_interval,
            "history_retention_hours": self.history_retention_hours,
            "alert_thresholds": self.alert_thresholds,
            "enable_websocket": self.enable_websocket,
            "websocket_port": self.websocket_port
        }

# Example usage file
EXAMPLE_USAGE = '''
# example_app.py - How to integrate Zynx monitoring

from fastapi import FastAPI
from zynx_monitoring_integration import setup_zynx_monitoring, track_zynx_inference
import time

app = FastAPI(title="Zynx AGI API")

# One-line setup
zynx = setup_zynx_monitoring(app)

@app.post("/chat")
async def chat_with_deeja(message: str):
    """Chat endpoint with automatic monitoring"""
    
    # Method 1: Context manager
    with track_zynx_inference(zynx.inference_tracker, "zynx-deeja-v1") as tracker:
        # Your AI logic here
        response = await your_ai_model.generate(message)
        
        # Set metrics
        tracker.set_tokens(
            input_tokens=len(message.split()),
            output_tokens=len(response.split())
        )
        tracker.set_quality(
            cultural_accuracy=0.95,
            emotional_intelligence=0.88,
            thai_proficiency=0.92
        )
    
    return {"response": response}

@app.post("/generate")
async def generate_content(prompt: str):
    """Alternative method: Manual tracking"""
    start_time = time.time()
    
    # Your AI generation logic
    content = await your_ai_model.generate(prompt)
    
    # Manual tracking
    inference_time = (time.time() - start_time) * 1000
    zynx.inference_tracker.track_inference(
        model_name="zynx-content-generator",
        input_tokens=len(prompt.split()),
        output_tokens=len(content.split()),
        inference_time_ms=inference_time,
        quality_scores={
            "creativity": 0.89,
            "coherence": 0.93
        }
    )
    
    return {"content": content}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Zynx AGI API with monitoring")
    print("📊 Dashboard: http://localhost:8000/zynx/dashboard")
    print("📈 Metrics: http://localhost:8000/zynx/metrics/current")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

if __name__ == "__main__":
    print("🔧 Zynx AGI Monitoring Integration Ready!")
    print("\n" + "="*50)
    print("INTEGRATION GUIDE:")
    print("="*50)
    print(EXAMPLE_USAGE)
