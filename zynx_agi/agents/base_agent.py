"""
Base Agent Framework for ZynxAGI
Provides the foundation for all AI agents in the ecosystem
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all ZynxAGI agents"""
    
    def __init__(self, agent_id: str, name: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.created_at = datetime.now()
        self.status = "ready"
        self.logger = logging.getLogger(f"agents.{agent_id}")
        
    @abstractmethod
    async def process_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a request and return a response"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    def get_manifest(self) -> Dict[str, Any]:
        """Return agent manifest information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "capabilities": self.get_capabilities(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "mcp_command": getattr(self, 'mcp_command', None)
        }
    
    def set_status(self, status: str):
        """Update agent status"""
        self.status = status
        self.logger.info(f"Agent {self.agent_id} status changed to: {status}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "healthy": self.status == "ready",
            "timestamp": datetime.now().isoformat()
        }