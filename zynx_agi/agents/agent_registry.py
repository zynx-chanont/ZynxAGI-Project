"""
Agent Registry for managing and discovering agents in ZynxAGI
Handles registration, discovery, and lifecycle management of AI agents
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentManifest(Dict[str, Any]):
    """
    Represents the manifest for an agent.
    Contains metadata about agent capabilities, version, dependencies, etc.
    """
    
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.validate()
    
    def validate(self):
        """Validate manifest structure"""
        required_fields = ["name", "version", "description", "capabilities"]
        for field in required_fields:
            if field not in self:
                raise ValueError(f"Manifest missing required field: {field}")

class AgentRegistry:
    """Registry for managing AI agents in the ZynxAGI ecosystem"""
    
    def __init__(self):
        self._registered_agents: Dict[str, AgentManifest] = {}
        self._agent_instances: Dict[str, Any] = {}  # Will store actual agent instances
        logger.info("AgentRegistry initialized")

    def register_agent(self, agent_id: str, manifest: AgentManifest, agent_instance: Any = None) -> bool:
        """
        Register an agent with the platform.
        
        Args:
            agent_id: Unique identifier for the agent
            manifest: Agent manifest containing metadata
            agent_instance: Optional actual agent instance
            
        Returns:
            bool: True if registration successful
        """
        try:
            if agent_id in self._registered_agents:
                logger.info(f"Agent {agent_id} already registered. Updating manifest.")
            
            self._registered_agents[agent_id] = manifest
            
            if agent_instance:
                self._agent_instances[agent_id] = agent_instance
            
            logger.info(f"Agent {agent_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the platform"""
        try:
            if agent_id in self._registered_agents:
                del self._registered_agents[agent_id]
                if agent_id in self._agent_instances:
                    del self._agent_instances[agent_id]
                logger.info(f"Agent {agent_id} unregistered")
                return True
            else:
                logger.warning(f"Agent {agent_id} not found for unregistration")
                return False
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {str(e)}")
            return False

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for a specific agent"""
        return self._registered_agents.get(agent_id)

    def get_agent_instance(self, agent_id: str) -> Optional[Any]:
        """Get actual agent instance"""
        return self._agent_instances.get(agent_id)

    def list_agents(self) -> Dict[str, AgentManifest]:
        """List all registered agents"""
        return self._registered_agents.copy()
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability"""
        matching_agents = []
        for agent_id, manifest in self._registered_agents.items():
            capabilities = manifest.get("capabilities", [])
            if capability in capabilities:
                matching_agents.append(agent_id)
        return matching_agents
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_agents": len(self._registered_agents),
            "active_instances": len(self._agent_instances),
            "agent_list": list(self._registered_agents.keys()),
            "timestamp": datetime.now().isoformat()
        }

# Global registry instance
registry = AgentRegistry()