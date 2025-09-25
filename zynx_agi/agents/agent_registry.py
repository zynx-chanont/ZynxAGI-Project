"""
Agent Registry - Discovery and management of available agents
Central registry for all agents in the Zynx ecosystem
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from .base_agent import ZynxAgent, AgentCapability
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry for discovering and managing available agents
    Provides agent lifecycle management and capability discovery
    """
    
    def __init__(self, storage_driver=None):
        self.storage = storage_driver
        self.agents: Dict[str, ZynxAgent] = {}
        self.capabilities_map: Dict[AgentCapability, List[str]] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the agent registry"""
        logger.info("Initializing Agent Registry...")
        
        # Build capabilities map
        await self._build_capabilities_map()
        
        # Log registry initialization
        if self.storage:
            await self.storage.store_log({
                "action": "agent_registry_initialized",
                "total_agents": len(self.agents),
                "total_capabilities": len(self.capabilities_map),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.initialized = True
        logger.info(f"Agent Registry initialized with {len(self.agents)} agents")
    
    async def register_agent(self, agent: ZynxAgent) -> bool:
        """Register a new agent in the registry"""
        try:
            # Initialize the agent first
            if not await agent.initialize():
                logger.error(f"Failed to initialize agent {agent.agent_id}")
                return False
            
            # Register the agent
            self.agents[agent.agent_id] = agent
            
            # Update capabilities map
            for capability in agent.capabilities:
                if capability not in self.capabilities_map:
                    self.capabilities_map[capability] = []
                self.capabilities_map[capability].append(agent.agent_id)
            
            # Store agent metadata
            self.agent_metadata[agent.agent_id] = {
                "registered_at": datetime.utcnow().isoformat(),
                "capabilities": [cap.value for cap in agent.capabilities],
                "active": agent.active,
                "config": agent.config
            }
            
            # Log registration
            if self.storage:
                await self.storage.store_log({
                    "action": "agent_registered",
                    "agent_id": agent.agent_id,
                    "capabilities": [cap.value for cap in agent.capabilities],
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"Successfully registered agent: {agent.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return False
        
        try:
            agent = self.agents[agent_id]
            
            # Shutdown the agent
            await agent.shutdown()
            
            # Remove from capabilities map
            for capability in agent.capabilities:
                if capability in self.capabilities_map:
                    if agent_id in self.capabilities_map[capability]:
                        self.capabilities_map[capability].remove(agent_id)
                    
                    # Remove empty capability entries
                    if not self.capabilities_map[capability]:
                        del self.capabilities_map[capability]
            
            # Remove agent
            del self.agents[agent_id]
            del self.agent_metadata[agent_id]
            
            # Log unregistration
            if self.storage:
                await self.storage.store_log({
                    "action": "agent_unregistered", 
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"Successfully unregistered agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[ZynxAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[ZynxAgent]:
        """Get all agents that support a specific capability"""
        agent_ids = self.capabilities_map.get(capability, [])
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with their metadata"""
        agents_list = []
        
        for agent_id, agent in self.agents.items():
            metadata = self.agent_metadata.get(agent_id, {})
            agents_list.append({
                "agent_id": agent_id,
                "active": agent.active,
                "capabilities": [cap.value for cap in agent.capabilities],
                "registered_at": metadata.get("registered_at"),
                "metrics": agent.get_metrics()
            })
        
        return agents_list
    
    def list_capabilities(self) -> Dict[str, List[str]]:
        """List all available capabilities and supporting agents"""
        return {
            cap.value: agent_ids 
            for cap, agent_ids in self.capabilities_map.items()
        }
    
    async def discover_agent_for_request(self, request: Dict[str, Any]) -> Optional[str]:
        """Discover the best agent for a specific request"""
        message = request.get("message", "").lower()
        
        # Simple discovery logic based on content analysis
        if any(word in message for word in ["thai", "cultural", "ครับ", "ค่ะ"]):
            # Cultural/Thai content - route to Deeja
            cultural_agents = self.get_agents_by_capability(AgentCapability.CULTURAL_ANALYSIS)
            if cultural_agents:
                return cultural_agents[0].agent_id
        
        if any(word in message for word in ["emotion", "feeling", "empathy", "เศร้า", "ดีใจ"]):
            # Emotional content - route to Deeja
            emotional_agents = self.get_agents_by_capability(AgentCapability.EMOTIONAL_INTELLIGENCE)
            if emotional_agents:
                return emotional_agents[0].agent_id
        
        if any(word in message for word in ["metadata", "compliance", "privacy", "license"]):
            # Metadata/compliance content - route to Zynx-Metadata
            metadata_agents = self.get_agents_by_capability(AgentCapability.METADATA_MANAGEMENT)
            if metadata_agents:
                return metadata_agents[0].agent_id
        
        # Default to main agent
        chat_agents = self.get_agents_by_capability(AgentCapability.CHAT)
        main_agents = [agent for agent in chat_agents if agent.agent_id == "zynx_main"]
        if main_agents:
            return main_agents[0].agent_id
        elif chat_agents:
            return chat_agents[0].agent_id
        
        return None
    
    async def health_check_all_agents(self) -> Dict[str, Any]:
        """Perform health check on all registered agents"""
        health_results = {
            "overall_healthy": True,
            "total_agents": len(self.agents),
            "healthy_agents": 0,
            "unhealthy_agents": 0,
            "agent_health": {},
            "check_timestamp": datetime.utcnow().isoformat()
        }
        
        for agent_id, agent in self.agents.items():
            try:
                health_check = await agent.health_check()
                health_results["agent_health"][agent_id] = health_check
                
                if health_check.get("active", False):
                    health_results["healthy_agents"] += 1
                else:
                    health_results["unhealthy_agents"] += 1
                    health_results["overall_healthy"] = False
                    
            except Exception as e:
                logger.error(f"Health check failed for agent {agent_id}: {e}")
                health_results["agent_health"][agent_id] = {
                    "agent_id": agent_id,
                    "active": False,
                    "error": str(e)
                }
                health_results["unhealthy_agents"] += 1
                health_results["overall_healthy"] = False
        
        return health_results
    
    async def get_agent_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for agents"""
        if agent_id:
            # Get metrics for specific agent
            agent = self.get_agent(agent_id)
            if agent:
                return {
                    "agent_id": agent_id,
                    "metrics": agent.get_metrics(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"error": f"Agent {agent_id} not found"}
        
        # Get metrics for all agents
        all_metrics = {
            "registry_metrics": {
                "total_agents": len(self.agents),
                "active_agents": len([a for a in self.agents.values() if a.active]),
                "total_capabilities": len(self.capabilities_map)
            },
            "agent_metrics": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for agent_id, agent in self.agents.items():
            all_metrics["agent_metrics"][agent_id] = agent.get_metrics()
        
        return all_metrics
    
    async def _build_capabilities_map(self):
        """Build the capabilities map from registered agents"""
        self.capabilities_map.clear()
        
        for agent_id, agent in self.agents.items():
            for capability in agent.capabilities:
                if capability not in self.capabilities_map:
                    self.capabilities_map[capability] = []
                self.capabilities_map[capability].append(agent_id)
    
    async def reload_agent(self, agent_id: str) -> bool:
        """Reload an agent (shutdown and reinitialize)"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found for reload")
            return False
        
        try:
            agent = self.agents[agent_id]
            
            # Shutdown current instance
            await agent.shutdown()
            
            # Reinitialize
            if await agent.initialize():
                # Update metadata
                self.agent_metadata[agent_id]["reloaded_at"] = datetime.utcnow().isoformat()
                
                # Log reload
                if self.storage:
                    await self.storage.store_log({
                        "action": "agent_reloaded",
                        "agent_id": agent_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                logger.info(f"Successfully reloaded agent: {agent_id}")
                return True
            else:
                logger.error(f"Failed to reinitialize agent {agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reload agent {agent_id}: {e}")
            return False
    
    async def shutdown_all_agents(self):
        """Shutdown all registered agents"""
        logger.info("Shutting down all agents...")
        
        shutdown_tasks = []
        for agent in self.agents.values():
            shutdown_tasks.append(agent.shutdown())
        
        # Wait for all agents to shutdown
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        # Clear registry
        self.agents.clear()
        self.capabilities_map.clear()
        self.agent_metadata.clear()
        
        logger.info("All agents shutdown complete")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status"""
        return {
            "initialized": self.initialized,
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.active]),
            "available_capabilities": list(self.capabilities_map.keys()),
            "agent_ids": list(self.agents.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
