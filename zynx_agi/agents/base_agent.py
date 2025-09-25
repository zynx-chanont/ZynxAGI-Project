"""
Base Agent Implementation for Zynx AGI System
Provides core functionality and interfaces for all agents
"""

import asyncio
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Simple BaseModel replacement for when pydantic is not available
try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class AgentCapability(str, Enum):
    """Enumeration of agent capabilities"""
    CHAT = "chat"
    CULTURAL_ANALYSIS = "cultural_analysis"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    METADATA_MANAGEMENT = "metadata_management"
    SESSION_MANAGEMENT = "session_management"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    TRANSLATION = "translation"
    EMPATHY_SCORING = "empathy_scoring"


class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    success: bool
    agent_id: str
    response_data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    timestamp: str
    processing_time_ms: Optional[float] = None
    compliance_info: Dict[str, bool] = {"zpdl_compliant": True, "pdpa_compliant": True}


class ZynxAgent(ABC):
    """Abstract base class for all Zynx agents"""
    
    def __init__(
        self, 
        agent_id: str, 
        capabilities: List[AgentCapability],
        storage_driver=None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.storage = storage_driver
        self.config = config or {}
        self.active = False
        self.session_data: Dict[str, Any] = {}
        self.metrics = {
            "requests_processed": 0,
            "total_processing_time": 0.0,
            "errors": 0,
            "started_at": datetime.utcnow().isoformat()
        }
    
    async def initialize(self) -> bool:
        """Initialize the agent and its resources"""
        try:
            await self._setup_agent()
            self.active = True
            logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            return False
    
    @abstractmethod
    async def _setup_agent(self):
        """Agent-specific setup logic"""
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """Process an incoming request"""
        pass
    
    async def execute_capability(
        self, 
        capability: AgentCapability, 
        data: Dict[str, Any]
    ) -> AgentResponse:
        """Execute a specific capability"""
        if capability not in self.capabilities:
            return AgentResponse(
                success=False,
                agent_id=self.agent_id,
                response_data={"error": f"Capability {capability} not supported"},
                timestamp=datetime.utcnow().isoformat()
            )
        
        start_time = datetime.utcnow()
        
        try:
            result = await self._execute_capability_impl(capability, data)
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.metrics["requests_processed"] += 1
            self.metrics["total_processing_time"] += processing_time
            
            return AgentResponse(
                success=True,
                agent_id=self.agent_id,
                response_data=result,
                timestamp=start_time.isoformat(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error executing capability {capability} on {self.agent_id}: {e}")
            
            return AgentResponse(
                success=False,
                agent_id=self.agent_id,
                response_data={"error": str(e)},
                timestamp=start_time.isoformat()
            )
    
    @abstractmethod
    async def _execute_capability_impl(
        self, 
        capability: AgentCapability, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Implementation of capability execution"""
        pass
    
    async def update_session_data(self, session_id: str, data: Dict[str, Any]):
        """Update session-specific data"""
        if session_id not in self.session_data:
            self.session_data[session_id] = {}
        self.session_data[session_id].update(data)
        
        # Log session update for compliance
        if self.storage:
            await self.storage.store_log({
                "action": "session_update",
                "agent_id": self.agent_id,
                "session_id": session_id,
                "data_hash": hashlib.sha256(str(data).encode()).hexdigest()[:16],
                "compliance": "ZPDL_v1.0"
            })
    
    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session-specific data"""
        return self.session_data.get(session_id, {})
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_processing_time = (
            self.metrics["total_processing_time"] / self.metrics["requests_processed"]
            if self.metrics["requests_processed"] > 0 else 0
        )
        
        return {
            **self.metrics,
            "average_processing_time_ms": avg_processing_time,
            "error_rate": (
                self.metrics["errors"] / self.metrics["requests_processed"]
                if self.metrics["requests_processed"] > 0 else 0
            ),
            "active": self.active
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the agent"""
        return {
            "agent_id": self.agent_id,
            "active": self.active,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": self.get_metrics(),
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        try:
            await self._cleanup_agent()
            self.active = False
            logger.info(f"Agent {self.agent_id} shutdown successfully")
        except Exception as e:
            logger.error(f"Error during agent {self.agent_id} shutdown: {e}")
    
    async def _cleanup_agent(self):
        """Agent-specific cleanup logic"""
        pass