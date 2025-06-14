# zynx_agi/monitoring/zynx_monitor.py
"""
Custom Monitoring Integration for Zynx AGI Engine
Seamlessly integrates with existing architecture
"""

import time
import psutil
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.base import BaseHTTPMiddleware
import sqlite3
import threading
from collections import deque
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class ZynxAGIMetrics:
    """Enhanced metrics for Zynx AGI performance tracking"""
    timestamp: datetime
    
    # Core Performance
    inference_time_ms: float
    tokens_per_second: float
    concurrent_requests: int
    queue_depth: int
    
    # Cultural Intelligence (Deeja)
    cultural_accuracy_score: float
    emotional_intelligence_score: float
    thai_language_proficiency: float
    formality_detection_accuracy: float
    politeness_level_avg: float
    
    # AI Platform Usage
    openai_requests: int
    claude_requests: int
    ai_platform_errors: int
    
    # System Health
    cpu_percent: float
    memory_percent: float
    active_websockets: int
    response_quality_score: float
    success_rate: float
    uptime_seconds: int
    
    # Chat Specific
    thai_messages_ratio: float
    english_messages_ratio: float
    cultural_context_switches: int

class ZynxAGIMonitor:
    """Enhanced monitoring system specifically for Zynx AGI Engine"""
    
    def __init__(self, db_path: str = "zynx_metrics.db"):
        self.db_path = db_path
        self.metrics_buffer = deque(maxlen=1000)
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.websocket_clients = set()
        
        # Zynx-specific counters
        self.chat_requests = 0
        self.cultural_analyses = 0
        self.thai_messages = 0
        self.english_messages = 0
        self.ai_platform_usage = {"openai": 0, "claude": 0, "errors": 0}
        self.websocket_connections = 0
        self.cultural_context_switches = 0
        
        self._init_database()
        
        # Zynx-specific baselines
        self.baselines = {
            "target_inference_time": 800.0,  # ms (more realistic for Zynx)
            "cultural_accuracy_threshold": 0.90,
            "emotional_intelligence_threshold": 0.85,
            "thai_proficiency_threshold": 0.92,
            "target_success_rate": 0.95
        }
        
    def _init_database(self):
        """Initialize SQLite database for Zynx metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zynx_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT,
                alert_level TEXT DEFAULT 'normal'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zynx_cultural_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                message_text TEXT,
                detected_culture TEXT,
                formality_level REAL,
                politeness_level REAL,
                cultural_adjustments TEXT,
                processing_time_ms REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zynx_ai_platform_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                platform TEXT,
                model TEXT,
                tokens_used INTEGER,
                processing_time_ms REAL,
                success BOOLEAN,
                cultural_context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def start_monitoring(self):
        """Start the Zynx monitoring loop"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🚀 Zynx AGI Monitoring System ACTIVATED!")
        
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_monitoring = False
        logger.info("⏹️ Zynx AGI Monitoring System DEACTIVATED")
        
    def _monitoring_loop(self):
        """Main monitoring loop optimized for Zynx AGI"""
        while self.is_monitoring:
            try:
                metrics = self._collect_zynx_metrics()
                self._store_metrics(metrics)
                self._analyze_zynx_performance(metrics)
                self._broadcast_to_websockets(metrics)
                
            except Exception as e:
                logger.error(f"❌ Zynx Monitoring error: {e}")
                
            time.sleep(3)  # Faster collection for real-time chat
            
    def _collect_zynx_metrics(self) -> ZynxAGIMetrics:
        """Collect Zynx AGI specific metrics"""
        now = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Zynx-specific calculations
        total_messages = self.thai_messages + self.english_messages
        thai_ratio = self.thai_messages / max(total_messages, 1)
        english_ratio = self.english_messages / max(total_messages, 1)
        
        # Mock enhanced metrics (replace with actual Zynx calculations)
        cultural_accuracy = np.random.uniform(0.88, 0.98)
        emotional_intelligence = np.random.uniform(0.82, 0.95)
        thai_proficiency = np.random.uniform(0.90, 0.99)
        formality_detection = np.random.uniform(0.85, 0.96)
        
        # Calculate inference time based on cultural complexity
        base_inference = np.random.normal(650, 100)  # Base time
        cultural_complexity_factor = 1.2 if thai_ratio > 0.5 else 1.0
        inference_time = base_inference * cultural_complexity_factor
        
        # Calculate tokens per second
        tokens_per_sec = np.random.normal(45, 8)
        
        # System health
        success_rate = 1.0 - (self.ai_platform_usage["errors"] / max(self.chat_requests, 1))
        uptime = int((now - self.start_time).total_seconds())
        
        return ZynxAGIMetrics(
            timestamp=now,
            inference_time_ms=max(0, inference_time),
            tokens_per_second=max(0, tokens_per_sec),
            concurrent_requests=self.websocket_connections,
            queue_depth=min(self.websocket_connections, 5),
            cultural_accuracy_score=cultural_accuracy,
            emotional_intelligence_score=emotional_intelligence,
            thai_language_proficiency=thai_proficiency,
            formality_detection_accuracy=formality_detection,
            politeness_level_avg=np.random.uniform(0.7, 0.9),
            openai_requests=self.ai_platform_usage["openai"],
            claude_requests=self.ai_platform_usage["claude"],
            ai_platform_errors=self.ai_platform_usage["errors"],
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            active_websockets=self.websocket_connections,
            response_quality_score=np.random.uniform(0.85, 0.97),
            success_rate=success_rate,
            uptime_seconds=uptime,
            thai_messages_ratio=thai_ratio,
            english_messages_ratio=english_ratio,
            cultural_context_switches=self.cultural_context_switches
        )
        
    def _analyze_zynx_performance(self, metrics: ZynxAGIMetrics):
        """Analyze Zynx-specific performance patterns"""
        alerts = []
        
        # Cultural Intelligence alerts
        if metrics.cultural_accuracy_score < self.baselines["cultural_accuracy_threshold"]:
            alerts.append({
                "metric": "cultural_accuracy",
                "severity": "warning",
                "message": f"Deeja cultural accuracy below threshold: {metrics.cultural_accuracy_score:.2f}"
            })
            
        if metrics.thai_language_proficiency < self.baselines["thai_proficiency_threshold"]:
            alerts.append({
                "metric": "thai_proficiency",
                "severity": "warning", 
                "message": f"Thai language processing degraded: {metrics.thai_language_proficiency:.2f}"
            })
            
        # Performance alerts
        if metrics.inference_time_ms > 1200:  # Adjusted for cultural processing
            alerts.append({
                "metric": "inference_time",
                "severity": "warning",
                "message": f"High inference time with cultural processing: {metrics.inference_time_ms:.1f}ms"
            })
            
        # AI Platform health
        total_ai_requests = metrics.openai_requests + metrics.claude_requests
        if total_ai_requests > 0:
            error_rate = metrics.ai_platform_errors / total_ai_requests
            if error_rate > 0.1:
                alerts.append({
                    "metric": "ai_platform_errors",
                    "severity": "critical",
                    "message": f"High AI platform error rate: {error_rate:.1%}"
                })
        
        if alerts:
            self._store_alerts(alerts)
            
    def _store_alerts(self, alerts: List[Dict]):
        """Store Zynx-specific alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for alert in alerts:
            cursor.execute('''
                INSERT INTO zynx_cultural_events 
                (timestamp, message_text, detected_culture, formality_level, politeness_level, cultural_adjustments, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert["message"],
                "alert",
                0.0,
                0.0,
                json.dumps(alert),
                0.0
            ))
            
        conn.commit()
        conn.close()
        
    def _store_metrics(self, metrics: ZynxAGIMetrics):
        """Store metrics to database"""
        self.metrics_buffer.append(metrics)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO zynx_metrics (timestamp, data)
            VALUES (?, ?)
        ''', (metrics.timestamp.isoformat(), json.dumps(asdict(metrics), default=str)))
        
        conn.commit()
        conn.close()
        
    def _broadcast_to_websockets(self, metrics: ZynxAGIMetrics):
        """Broadcast real-time metrics to dashboard"""
        if self.websocket_clients:
            data = asdict(metrics)
            data["timestamp"] = metrics.timestamp.isoformat()
            
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    asyncio.create_task(client.send_text(json.dumps(data)))
                except:
                    disconnected.add(client)
            
            self.websocket_clients -= disconnected
            
    # Zynx-specific tracking methods
    def track_chat_request(self, message: str, cultural_context: Dict[str, Any], 
                          processing_time: float, ai_platform: str):
        """Track a chat request with cultural context"""
        self.chat_requests += 1
        
        # Detect language
        is_thai = any(ord(char) >= 0x0E00 and ord(char) <= 0x0E7F for char in message)
        if is_thai:
            self.thai_messages += 1
        else:
            self.english_messages += 1
            
        # Track AI platform usage
        if ai_platform.lower() == "openai":
            self.ai_platform_usage["openai"] += 1
        elif ai_platform.lower() == "claude":
            self.ai_platform_usage["claude"] += 1
            
        # Store cultural event
        self._store_cultural_event(message, cultural_context, processing_time, ai_platform)
        
    def track_cultural_context_switch(self, from_culture: str, to_culture: str):
        """Track when cultural context changes"""
        self.cultural_context_switches += 1
        logger.info(f"Cultural context switch: {from_culture} → {to_culture}")
        
    def track_websocket_connection(self, connected: bool):
        """Track WebSocket connections"""
        if connected:
            self.websocket_connections += 1
        else:
            self.websocket_connections = max(0, self.websocket_connections - 1)
            
    def track_ai_platform_error(self, platform: str, error: str):
        """Track AI platform errors"""
        self.ai_platform_usage["errors"] += 1
        logger.error(f"AI Platform Error [{platform}]: {error}")
        
    def _store_cultural_event(self, message: str, cultural_context: Dict[str, Any], 
                             processing_time: float, ai_platform: str):
        """Store cultural processing event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO zynx_cultural_events 
            (timestamp, message_text, detected_culture, formality_level, politeness_level, cultural_adjustments, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            message[:100],  # Truncate for privacy
            cultural_context.get("primaryCulture", "unknown"),
            cultural_context.get("formalityLevel", 0.0),
            cultural_context.get("politenessLevel", 0.0),
            json.dumps({"platform": ai_platform, "context": cultural_context}),
            processing_time
        ))
        
        conn.commit()
        conn.close()
        
    def get_zynx_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get Zynx AGI specific performance summary"""
        since = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp >= since]
        
        if not recent_metrics:
            return {"error": "No metrics available"}
            
        # Zynx-specific analysis
        avg_cultural_accuracy = np.mean([m.cultural_accuracy_score for m in recent_metrics])
        avg_thai_proficiency = np.mean([m.thai_language_proficiency for m in recent_metrics])
        avg_emotional_intelligence = np.mean([m.emotional_intelligence_score for m in recent_metrics])
        avg_inference_time = np.mean([m.inference_time_ms for m in recent_metrics])
        
        # Cultural insights
        thai_usage = np.mean([m.thai_messages_ratio for m in recent_metrics])
        cultural_switches = sum([m.cultural_context_switches for m in recent_metrics])
        
        # AI platform distribution
        total_openai = sum([m.openai_requests for m in recent_metrics])
        total_claude = sum([m.claude_requests for m in recent_metrics])
        total_requests = total_openai + total_claude
        
        return {
            "period_hours": hours,
            "total_chat_requests": self.chat_requests,
            "cultural_intelligence": {
                "avg_cultural_accuracy": round(avg_cultural_accuracy, 3),
                "avg_thai_proficiency": round(avg_thai_proficiency, 3),
                "avg_emotional_intelligence": round(avg_emotional_intelligence, 3),
                "cultural_context_switches": cultural_switches
            },
            "language_distribution": {
                "thai_usage_ratio": round(thai_usage, 3),
                "english_usage_ratio": round(1 - thai_usage, 3),
                "total_thai_messages": self.thai_messages,
                "total_english_messages": self.english_messages
            },
            "ai_platform_usage": {
                "openai_requests": total_openai,
                "claude_requests": total_claude,
                "total_requests": total_requests,
                "error_count": self.ai_platform_usage["errors"],
                "success_rate": round(1 - (self.ai_platform_usage["errors"] / max(total_requests, 1)), 3)
            },
            "performance": {
                "avg_inference_time_ms": round(avg_inference_time, 2),
                "active_websockets": self.websocket_connections,
                "uptime_hours": round((datetime.now() - self.start_time).total_seconds() / 3600, 2)
            },
            "zynx_health_score": self._calculate_zynx_health_score(recent_metrics),
            "recommendations": self._generate_zynx_recommendations(recent_metrics)
        }
        
    def _calculate_zynx_health_score(self, metrics: List[ZynxAGIMetrics]) -> float:
        """Calculate Zynx AGI specific health score"""
        if not metrics:
            return 0.0
            
        # Weighted calculation for Zynx AGI
        cultural_score = np.mean([m.cultural_accuracy_score * 100 for m in metrics]) * 0.3
        performance_score = 100 - np.mean([max(0, m.inference_time_ms - 500) / 10 for m in metrics]) * 0.25
        thai_proficiency_score = np.mean([m.thai_language_proficiency * 100 for m in metrics]) * 0.25
        emotional_intelligence_score = np.mean([m.emotional_intelligence_score * 100 for m in metrics]) * 0.2
        
        health_score = cultural_score + performance_score + thai_proficiency_score + emotional_intelligence_score
        return max(0, min(100, health_score))
        
    def _generate_zynx_recommendations(self, metrics: List[ZynxAGIMetrics]) -> List[str]:
        """Generate Zynx AGI specific optimization recommendations"""
        if not metrics:
            return []
            
        recommendations = []
        
        avg_cultural_accuracy = np.mean([m.cultural_accuracy_score for m in metrics])
        if avg_cultural_accuracy < 0.9:
            recommendations.append("Consider expanding Thai cultural training data")
            
        avg_inference_time = np.mean([m.inference_time_ms for m in metrics])
        if avg_inference_time > 1000:
            recommendations.append("Optimize cultural context processing pipeline")
            
        thai_ratio = np.mean([m.thai_messages_ratio for m in metrics])
        if thai_ratio > 0.8:
            recommendations.append("Consider dedicated Thai language model optimization")
        elif thai_ratio < 0.2:
            recommendations.append("Focus on international communication patterns")
            
        avg_emotional_intelligence = np.mean([m.emotional_intelligence_score for m in metrics])
        if avg_emotional_intelligence < 0.85:
            recommendations.append("Enhance emotional context detection algorithms")
            
        websocket_usage = np.mean([m.active_websockets for m in metrics])
        if websocket_usage > 10:
            recommendations.append("Consider WebSocket connection pooling")
            
        return recommendations

# Global monitor instance
zynx_monitor = ZynxAGIMonitor()
