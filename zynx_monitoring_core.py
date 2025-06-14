# Zynx AGI Engine - Advanced Monitoring System
# "The Arc Reactor Neural Network Monitor"

import time
import psutil
import GPUtil
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import threading
from collections import deque
import numpy as np

@dataclass
class AGIMetrics:
    """Core metrics for Zynx AGI performance tracking"""
    timestamp: datetime
    # Compute Metrics
    cpu_percent: float
    memory_percent: float
    gpu_utilization: float
    gpu_memory_used: float
    gpu_temperature: float
    
    # AI Inference Metrics
    inference_time_ms: float
    tokens_per_second: float
    model_latency_p95: float
    queue_depth: int
    concurrent_requests: int
    
    # Quality Metrics
    response_quality_score: float
    hallucination_risk_score: float
    context_coherence_score: float
    
    # Cultural Intelligence (Deeja) Metrics
    cultural_accuracy_score: float
    emotional_intelligence_score: float
    thai_language_proficiency: float
    
    # System Health
    error_rate: float
    success_rate: float
    uptime_seconds: int

class ZynxAGIMonitor:
    """
    Advanced monitoring system for Zynx AGI Engine
    Tracks compute performance, AI quality, and cultural intelligence
    """
    
    def __init__(self, db_path: str = "zynx_metrics.db"):
        self.db_path = db_path
        self.metrics_buffer = deque(maxlen=1000)  # Keep last 1000 metrics
        self.active_requests = {}
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.websocket_clients = set()
        
        # Initialize database
        self._init_database()
        
        # Performance baselines (will be calibrated)
        self.baselines = {
            "target_inference_time": 500.0,  # ms
            "target_tokens_per_second": 50.0,
            "max_queue_depth": 10,
            "target_gpu_utilization": 80.0,
        }
        
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agi_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT,
                alert_level TEXT DEFAULT 'normal'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                actual_value REAL,
                threshold_value REAL,
                severity TEXT,
                message TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def start_monitoring(self):
        """Start the monitoring loop"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("🚀 Zynx AGI Monitoring System ACTIVATED!")
        
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_monitoring = False
        print("⏹️ Zynx AGI Monitoring System DEACTIVATED")
        
    def _monitoring_loop(self):
        """Main monitoring loop - runs every 5 seconds"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self._store_metrics(metrics)
                self._analyze_performance(metrics)
                self._broadcast_to_websockets(metrics)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                
            time.sleep(5)  # Collect metrics every 5 seconds
            
    def _collect_metrics(self) -> AGIMetrics:
        """Collect all system and AI metrics"""
        now = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU metrics (if available)
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                gpu_util = gpu.load * 100
                gpu_memory = gpu.memoryUtil * 100
                gpu_temp = gpu.temperature
            else:
                gpu_util = gpu_memory = gpu_temp = 0.0
        except:
            gpu_util = gpu_memory = gpu_temp = 0.0
            
        # Mock AI metrics (replace with actual AGI metrics)
        inference_time = np.random.normal(450, 50)  # ms
        tokens_per_sec = np.random.normal(55, 10)
        queue_depth = len(self.active_requests)
        
        # Mock quality scores (replace with actual Zynx evaluations)
        response_quality = np.random.uniform(0.85, 0.98)
        hallucination_risk = np.random.uniform(0.02, 0.15)
        context_coherence = np.random.uniform(0.88, 0.96)
        
        # Mock Deeja cultural intelligence scores
        cultural_accuracy = np.random.uniform(0.90, 0.98)
        emotional_intelligence = np.random.uniform(0.87, 0.95)
        thai_proficiency = np.random.uniform(0.92, 0.99)
        
        # System health
        error_rate = np.random.uniform(0.01, 0.05)
        success_rate = 1.0 - error_rate
        uptime = int((now - self.start_time).total_seconds())
        
        return AGIMetrics(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            gpu_utilization=gpu_util,
            gpu_memory_used=gpu_memory,
            gpu_temperature=gpu_temp,
            inference_time_ms=max(0, inference_time),
            tokens_per_second=max(0, tokens_per_sec),
            model_latency_p95=inference_time * 1.2,  # Rough P95
            queue_depth=queue_depth,
            concurrent_requests=len(self.active_requests),
            response_quality_score=response_quality,
            hallucination_risk_score=hallucination_risk,
            context_coherence_score=context_coherence,
            cultural_accuracy_score=cultural_accuracy,
            emotional_intelligence_score=emotional_intelligence,
            thai_language_proficiency=thai_proficiency,
            error_rate=error_rate,
            success_rate=success_rate,
            uptime_seconds=uptime
        )
        
    def _store_metrics(self, metrics: AGIMetrics):
        """Store metrics to database and memory buffer"""
        self.metrics_buffer.append(metrics)
        
        # Store to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agi_metrics (timestamp, data)
            VALUES (?, ?)
        ''', (metrics.timestamp.isoformat(), json.dumps(asdict(metrics), default=str)))
        
        conn.commit()
        conn.close()
        
    def _analyze_performance(self, metrics: AGIMetrics):
        """Analyze performance and generate alerts"""
        alerts = []
        
        # Check inference time
        if metrics.inference_time_ms > self.baselines["target_inference_time"] * 1.5:
            alerts.append({
                "metric": "inference_time",
                "severity": "warning",
                "message": f"Inference time high: {metrics.inference_time_ms:.1f}ms (target: {self.baselines['target_inference_time']}ms)"
            })
            
        # Check GPU utilization
        if metrics.gpu_utilization > 95:
            alerts.append({
                "metric": "gpu_utilization",
                "severity": "critical",
                "message": f"GPU utilization critical: {metrics.gpu_utilization:.1f}%"
            })
            
        # Check queue depth
        if metrics.queue_depth > self.baselines["max_queue_depth"]:
            alerts.append({
                "metric": "queue_depth",
                "severity": "warning",
                "message": f"Request queue backing up: {metrics.queue_depth} requests"
            })
            
        # Check Deeja cultural performance
        if metrics.cultural_accuracy_score < 0.85:
            alerts.append({
                "metric": "cultural_accuracy",
                "severity": "warning",
                "message": f"Cultural accuracy declining: {metrics.cultural_accuracy_score:.2f}"
            })
            
        # Store alerts
        if alerts:
            self._store_alerts(alerts)
            
    def _store_alerts(self, alerts: List[Dict]):
        """Store performance alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for alert in alerts:
            cursor.execute('''
                INSERT INTO performance_alerts 
                (timestamp, metric_name, severity, message)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert["metric"],
                alert["severity"],
                alert["message"]
            ))
            
        conn.commit()
        conn.close()
        
    def _broadcast_to_websockets(self, metrics: AGIMetrics):
        """Broadcast real-time metrics to connected WebSocket clients"""
        if self.websocket_clients:
            data = asdict(metrics)
            data["timestamp"] = metrics.timestamp.isoformat()
            
            # Remove disconnected clients
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    asyncio.create_task(client.send_text(json.dumps(data)))
                except:
                    disconnected.add(client)
            
            self.websocket_clients -= disconnected
            
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        since = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp >= since]
        
        if not recent_metrics:
            return {"error": "No metrics available"}
            
        # Calculate averages
        avg_inference = np.mean([m.inference_time_ms for m in recent_metrics])
        avg_tokens_per_sec = np.mean([m.tokens_per_second for m in recent_metrics])
        avg_gpu_util = np.mean([m.gpu_utilization for m in recent_metrics])
        avg_cultural_accuracy = np.mean([m.cultural_accuracy_score for m in recent_metrics])
        
        # Find bottlenecks
        bottlenecks = []
        if avg_inference > self.baselines["target_inference_time"] * 1.2:
            bottlenecks.append("compute_latency")
        if avg_gpu_util > 90:
            bottlenecks.append("gpu_capacity")
        if np.mean([m.queue_depth for m in recent_metrics]) > 5:
            bottlenecks.append("request_throughput")
            
        return {
            "period_hours": hours,
            "total_requests": len(recent_metrics),
            "performance": {
                "avg_inference_time_ms": round(avg_inference, 2),
                "avg_tokens_per_second": round(avg_tokens_per_sec, 2),
                "avg_gpu_utilization": round(avg_gpu_util, 2),
                "avg_cultural_accuracy": round(avg_cultural_accuracy, 4)
            },
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_optimization_recommendations(bottlenecks),
            "zynx_health_score": self._calculate_zynx_health_score(recent_metrics)
        }
        
    def _generate_optimization_recommendations(self, bottlenecks: List[str]) -> List[str]:
        """Generate actionable optimization recommendations"""
        recommendations = []
        
        if "compute_latency" in bottlenecks:
            recommendations.extend([
                "Consider model quantization (8-bit/4-bit)",
                "Implement request batching",
                "Add GPU instances for inference scaling"
            ])
            
        if "gpu_capacity" in bottlenecks:
            recommendations.extend([
                "Scale horizontal GPU infrastructure",
                "Implement model serving load balancer",
                "Consider distributed inference pipeline"
            ])
            
        if "request_throughput" in bottlenecks:
            recommendations.extend([
                "Implement async request queuing",
                "Add cache layer for common responses",
                "Optimize database queries"
            ])
            
        return recommendations
        
    def _calculate_zynx_health_score(self, metrics: List[AGIMetrics]) -> float:
        """Calculate overall Zynx AGI Engine health score (0-100)"""
        if not metrics:
            return 0.0
            
        # Weighted health calculation
        performance_score = 100 - np.mean([max(0, m.inference_time_ms - 300) / 10 for m in metrics])
        quality_score = np.mean([m.response_quality_score * 100 for m in metrics])
        cultural_score = np.mean([m.cultural_accuracy_score * 100 for m in metrics])
        reliability_score = np.mean([m.success_rate * 100 for m in metrics])
        
        # Weighted average
        health_score = (
            performance_score * 0.25 +
            quality_score * 0.30 +
            cultural_score * 0.25 +
            reliability_score * 0.20
        )
        
        return max(0, min(100, health_score))

# FastAPI integration for real-time dashboard
app = FastAPI(title="Zynx AGI Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitor instance
monitor = ZynxAGIMonitor()

@app.on_event("startup")
async def startup_event():
    """Start monitoring when API starts"""
    monitor.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring when API shuts down"""
    monitor.stop_monitoring()

@app.get("/metrics/current")
async def get_current_metrics():
    """Get current AGI metrics"""
    if monitor.metrics_buffer:
        latest = monitor.metrics_buffer[-1]
        return asdict(latest)
    return {"error": "No metrics available"}

@app.get("/metrics/summary")
async def get_performance_summary(hours: int = 24):
    """Get performance summary"""
    return monitor.get_performance_summary(hours)

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    monitor.websocket_clients.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        monitor.websocket_clients.discard(websocket)

if __name__ == "__main__":
    import uvicorn
    
    # Start the monitor
    monitor.start_monitoring()
    
    print("🔥 Zynx AGI Engine Monitoring System")
    print("📊 Real-time metrics collection activated")
    print("🎯 Ready to track Arc Reactor performance!")
    
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8001)